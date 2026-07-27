"""Bounded model -> tool batch -> strict-final loop for semantic resolution."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel, ConfigDict

from aviation_agentic_ai.agent_system.audit import sanitize_json_value, sanitize_text
from aviation_agentic_ai.agent_system.contracts import ModelCallRecord, ToolTraceEntry
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    ContractExecutionBinding,
    ResolutionDecision,
    ResolutionProposal,
    ResolutionProposalFields,
    ResolutionTask,
    seal_resolution_proposal,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.prompts import DEFAULT_PROMPT_CATALOG, assemble_prompt
from aviation_agentic_ai.agent_system.resolution_tools import (
    AuthorityRecordObservation,
    ResolutionToolGateway,
    ResolutionToolResult,
    build_resolution_tools,
)
from aviation_agentic_ai.agent_system.tool_model import ToolCallingModel

MAX_PROVIDER_TURNS = 2
MAX_TOOL_CALLS = 3
MAX_RENDERED_INPUT_TOKENS = 4096
MAX_OUTPUT_TOKENS = 256


@dataclass(frozen=True)
class SemanticResolutionResult:
    proposal: ResolutionProposal
    model_calls: tuple[ModelCallRecord, ...]
    tool_traces: tuple[ToolTraceEntry, ...]
    failure_reason: str | None = None


class _FinalDecision(BaseModel):
    """The entire provider-facing final-decision contract."""

    model_config = ConfigDict(extra="forbid", strict=True)

    decision: Literal["accepted", "abstained"]
    selected_candidate_id: str | None
    rejected_candidate_ids: list[str]
    limitation: str | None


def _base_messages(task: ResolutionTask, *, catalog_path: str) -> list[BaseMessage]:
    assembled = assemble_prompt(
        "semantic_resolution",
        {
            "task_id": task.task_id,
            "mention": task.mention,
            "structural_slot": task.structural_slot,
            "expected_entity_type": task.expected_entity_type,
            "eligible_candidate_ids": "\n".join(
                candidate.candidate_id for candidate in task.candidates if candidate.eligible
            )
            or "(none)",
            "authority_source_ids": "\n".join(task.authority_source_ids) or "(none)",
            "schema_slice_id": task.schema_slice_id,
        },
        catalog_path=catalog_path,
    )
    messages: list[BaseMessage] = []
    for role, content in assembled.messages:
        if role == "system":
            messages.append(SystemMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        else:
            messages.append(HumanMessage(content=content))
    return messages


def _final_messages(
    messages: list[BaseMessage],
    tool_selection: AIMessage,
    tool_messages: list[ToolMessage],
) -> list[BaseMessage]:
    """Keep only the final provider-visible instruction, task, and observations."""

    return [messages[0], messages[-1], tool_selection, *tool_messages]


def _tool_definition(tool: BaseTool) -> dict[str, Any]:
    """Project one bound tool into the provider-facing JSON-schema shape."""

    schema = tool.args_schema
    if hasattr(schema, "model_json_schema"):
        parameters = schema.model_json_schema()
    elif isinstance(schema, dict):
        parameters = schema
    else:
        parameters = {}
    return {
        "name": tool.name,
        "description": tool.description,
        "parameters": parameters,
    }


def _message_payload(message: BaseMessage) -> dict[str, Any]:
    """Preserve every provider-visible message field used by this loop."""

    payload: dict[str, Any] = {
        "type": message.type,
        "content": sanitize_json_value(message.content),
    }
    if isinstance(message, AIMessage):
        payload["tool_calls"] = sanitize_json_value(message.tool_calls)
    if isinstance(message, ToolMessage):
        payload["tool_call_id"] = message.tool_call_id
    return payload


def _estimated_input_tokens(
    messages: list[BaseMessage],
    *,
    bound_tools: list[BaseTool] | None = None,
) -> int:
    """Use UTF-8 payload bytes as a conservative local token upper bound."""

    payload = {
        "messages": [_message_payload(message) for message in messages],
        "tools": [_tool_definition(tool) for tool in bound_tools or []],
    }
    rendered = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )
    return len(rendered.encode("utf-8"))


def _observed_distinguishing_authority_content(
    *,
    task: ResolutionTask,
    candidate_id: str,
    observed_content: list[str],
) -> bool:
    """Require a selected candidate's own observed authority text to distinguish it."""

    candidate = next(row for row in task.candidates if row.candidate_id == candidate_id)
    markers = {
        candidate.surface_form.strip().casefold(),
        candidate.preferred_label.strip().casefold(),
        candidate.candidate_id.rsplit(":", maxsplit=1)[-1].strip().casefold(),
    }
    other_markers = {
        marker
        for row in task.candidates
        if row.candidate_id != candidate_id and row.eligible
        for marker in {
            row.surface_form.strip().casefold(),
            row.preferred_label.strip().casefold(),
            row.candidate_id.rsplit(":", maxsplit=1)[-1].strip().casefold(),
        }
    }
    distinctive = {marker for marker in markers if marker and marker not in other_markers}
    content = "\n".join(observed_content).casefold()
    return any(marker in content for marker in distinctive)


def _model_tool_observation(result: ResolutionToolResult) -> str:
    """Project a tool result to fields needed for the final bounded decision."""

    item_fields = (
        "candidate_id",
        "candidate_kind",
        "candidate_type",
        "ontology_class_prefixed",
        "ontology_class_iri",
        "authority_record_text",
        "check_kind",
        "status",
    )
    payload = {
        "tool": result.tool,
        "status": result.status,
        "items": [
            {key: value for key, value in item.model_dump().items() if key in item_fields}
            for item in result.items
        ],
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _message_text(message: AIMessage) -> str:
    if isinstance(message.content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in message.content
        )
    return str(message.content or "")


def _call_signature(call: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(call.get("id") or call.get("call_id") or ""),
        str(call.get("name") or ""),
        json.dumps(
            sanitize_json_value(call.get("args", call.get("arguments", {}))),
            sort_keys=True,
            separators=(",", ":"),
        ),
    )


def _record_call_signatures(record: ModelCallRecord) -> list[tuple[str, str, str]]:
    return [
        _call_signature(
            {
                "call_id": call.call_id,
                "name": call.name,
                "arguments": call.arguments,
            }
        )
        for call in record.tool_calls
    ]


def _safe_parameters(arguments: dict[str, Any]) -> dict[str, str]:
    sanitized = sanitize_json_value(arguments)
    if not isinstance(sanitized, dict):
        return {}
    return {
        str(key): json.dumps(value, sort_keys=True, default=str) for key, value in sanitized.items()
    }


def _proposal(
    *,
    task: ResolutionTask,
    binding: ContractExecutionBinding,
    decision: ResolutionDecision,
    selected_candidate_id: str | None,
    supporting_evidence_ids: tuple[str, ...],
    source_ids: tuple[str, ...],
    traces: tuple[ToolTraceEntry, ...],
    limitation: str | None,
) -> ResolutionProposal:
    rejected = tuple(
        sorted(
            audit.candidate_id
            for audit in task.candidate_audits
            if audit.candidate_id != selected_candidate_id
        )
    )
    proposal_id = stable_contract_id(
        "resolution-proposal",
        task.task_id,
        decision.value,
        selected_candidate_id or "NONE",
        json.dumps(rejected, separators=(",", ":"), ensure_ascii=False),
        json.dumps(supporting_evidence_ids, separators=(",", ":"), ensure_ascii=False),
    )
    return seal_resolution_proposal(
        task=task,
        binding=binding,
        fields=ResolutionProposalFields(
            resolution_proposal_id=proposal_id,
            run_id=task.run_id,
            task_id=task.task_id,
            task_payload_checksum=task.payload_checksum,
            event_id=task.event_id,
            mention=task.mention,
            structural_slot=task.structural_slot,
            expected_entity_type=task.expected_entity_type,
            selected_candidate_id=selected_candidate_id,
            rejected_candidate_ids=rejected,
            decision=decision,
            supporting_evidence_claim_ids=supporting_evidence_ids,
            authority_source_ids=source_ids,
            tool_trace_ids=tuple(trace.tool_call_id for trace in traces if trace.tool_call_id),
            limitation=limitation,
        ),
    )


def _blocked(
    *,
    task: ResolutionTask,
    binding: ContractExecutionBinding,
    model_calls: list[ModelCallRecord],
    traces: list[ToolTraceEntry],
    reason: str,
) -> SemanticResolutionResult:
    proposal = _proposal(
        task=task,
        binding=binding,
        decision=ResolutionDecision.BLOCKED,
        selected_candidate_id=None,
        supporting_evidence_ids=(),
        source_ids=(),
        traces=tuple(traces),
        limitation=reason,
    )
    return SemanticResolutionResult(
        proposal=proposal,
        model_calls=tuple(model_calls),
        tool_traces=tuple(traces),
        failure_reason=reason,
    )


def _parse_final_decision(raw: str) -> _FinalDecision:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("final response is not strict JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("final response is not a JSON object")
    expected = {
        "decision",
        "selected_candidate_id",
        "rejected_candidate_ids",
        "limitation",
    }
    if set(payload) != expected:
        raise ValueError("final response does not contain exactly the required keys")
    try:
        return _FinalDecision.model_validate(payload)
    except Exception as exc:
        raise ValueError("final response violates the strict JSON decision contract") from exc


def run_semantic_resolution_agent(
    *,
    task: ResolutionTask,
    binding: ContractExecutionBinding,
    tool_model_factory: Callable[[list[BaseTool]], ToolCallingModel] | None,
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
) -> SemanticResolutionResult:
    """Run the frozen two-turn resolution loop without repair retries."""

    model_calls: list[ModelCallRecord] = []
    traces: list[ToolTraceEntry] = []
    messages = _base_messages(task, catalog_path=catalog_path)
    if tool_model_factory is None:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Semantic Resolution Agent model factory is unavailable",
        )

    tools = build_resolution_tools(ResolutionToolGateway(task=task))
    if _estimated_input_tokens(messages, bound_tools=tools) > MAX_RENDERED_INPUT_TOKENS:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Semantic Resolution Agent rendered input budget exceeded",
        )
    registry = {tool.name: tool for tool in tools}
    try:
        model = tool_model_factory(tools)
    except Exception as exc:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=sanitize_text(
                f"Semantic Resolution Agent model construction failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        )
    try:
        first = model.invoke(messages, phase="select_tool")
    except Exception as exc:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=sanitize_text(
                f"Semantic Resolution Agent provider failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        )
    model_calls.append(first.record)
    if first.record.error:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=first.record.error,
        )
    if first.record.output_tokens > MAX_OUTPUT_TOKENS:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Semantic Resolution Agent output-token cap exceeded",
        )
    if first.message is None:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="provider returned no AI message",
        )
    if [
        _call_signature(dict(call)) for call in first.message.tool_calls
    ] != _record_call_signatures(first.record):
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="native tool calls do not match the persisted model audit",
        )

    calls = [dict(call) for call in first.message.tool_calls]
    allowed_tool_count = min(MAX_TOOL_CALLS, task.remaining_tool_budget)
    if not calls:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Semantic Resolution Agent did not select a resolution tool",
        )
    if len(calls) > allowed_tool_count:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Semantic Resolution Agent tool-call budget exceeded",
        )

    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    observed_evidence_by_candidate: dict[str, set[str]] = {}
    observed_sources_by_evidence: dict[str, str] = {}
    observed_authority_content_by_candidate: dict[str, list[str]] = {}
    tool_messages: list[ToolMessage] = []
    for call in calls:
        call_id = str(call.get("id") or "").strip()
        name = str(call.get("name") or "").strip()
        arguments = call.get("args")
        if not call_id or call_id in seen_ids:
            return _blocked(
                task=task,
                binding=binding,
                model_calls=model_calls,
                traces=traces,
                reason="missing or duplicate native tool-call ID",
            )
        if name not in registry:
            return _blocked(
                task=task,
                binding=binding,
                model_calls=model_calls,
                traces=traces,
                reason=f"unknown Semantic Resolution Agent tool: {name}",
            )
        if name in seen_names:
            return _blocked(
                task=task,
                binding=binding,
                model_calls=model_calls,
                traces=traces,
                reason=f"per-tool budget exceeded: {name}",
            )
        if not isinstance(arguments, dict):
            return _blocked(
                task=task,
                binding=binding,
                model_calls=model_calls,
                traces=traces,
                reason=f"invalid arguments for resolution tool: {name}",
            )
        seen_ids.add(call_id)
        seen_names.add(name)
        started = time.perf_counter()
        try:
            content = registry[name].invoke(arguments)
            result = ResolutionToolResult.model_validate_json(str(content))
            if result.tool != name:
                raise ValueError(f"tool result name mismatch: expected {name}, got {result.tool}")
        except Exception as exc:
            trace = ToolTraceEntry(
                tool_call_id=call_id,
                tool=name,
                parameters=_safe_parameters(arguments),
                status="blocked",
                duration_ms=(time.perf_counter() - started) * 1000.0,
                error=sanitize_text(f"{type(exc).__name__}: {exc}"),
            )
            traces.append(trace)
            return _blocked(
                task=task,
                binding=binding,
                model_calls=model_calls,
                traces=traces,
                reason=trace.error or "resolution tool failed",
            )
        duration = (time.perf_counter() - started) * 1000.0
        traces.append(
            ToolTraceEntry(
                tool_call_id=call_id,
                tool=name,
                parameters=_safe_parameters(arguments),
                result_refs=result.result_ids,
                source_ids=result.authority_source_ids,
                status="ok",
                duration_ms=duration,
            )
        )
        for evidence_id in result.authority_evidence_ids:
            candidate_id = next(
                (
                    claim.candidate_id
                    for claim in task.authority_evidence
                    if claim.evidence_id == evidence_id
                ),
                None,
            )
            if candidate_id:
                observed_evidence_by_candidate.setdefault(candidate_id, set()).add(evidence_id)
                source = next(
                    claim.source_id
                    for claim in task.authority_evidence
                    if claim.evidence_id == evidence_id
                )
                observed_sources_by_evidence[evidence_id] = source
        for item in result.items:
            if isinstance(item, AuthorityRecordObservation):
                observed_authority_content_by_candidate.setdefault(item.candidate_id, []).append(
                    item.authority_record_text
                )
        tool_messages.append(
            ToolMessage(
                content=_model_tool_observation(result),
                tool_call_id=call_id,
            )
        )

    final_messages = _final_messages(messages, first.message, tool_messages)
    if _estimated_input_tokens(final_messages) > MAX_RENDERED_INPUT_TOKENS:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Semantic Resolution Agent rendered input budget exceeded",
        )
    try:
        second = model.invoke(final_messages, phase="final_answer")
    except Exception as exc:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=sanitize_text(
                f"Semantic Resolution Agent provider failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        )
    model_calls.append(second.record)
    if second.record.error:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=second.record.error,
        )
    if second.record.output_tokens > MAX_OUTPUT_TOKENS:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Semantic Resolution Agent output-token cap exceeded",
        )
    if second.message is None:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="provider returned no AI message",
        )
    if [
        _call_signature(dict(call)) for call in second.message.tool_calls
    ] != _record_call_signatures(second.record):
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="native tool calls do not match the persisted model audit",
        )
    if second.message.tool_calls:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Semantic Resolution Agent requested another tool after the one-round tool budget",
        )
    try:
        final = _parse_final_decision(_message_text(second.message).strip())
    except ValueError as exc:
        return _blocked(
            task=task, binding=binding, model_calls=model_calls, traces=traces, reason=str(exc)
        )

    eligible_ids = {candidate.candidate_id for candidate in task.candidates if candidate.eligible}
    expected_rejected = {audit.candidate_id for audit in task.candidate_audits}
    if final.decision == "accepted":
        if final.selected_candidate_id not in eligible_ids:
            return _blocked(
                task=task,
                binding=binding,
                model_calls=model_calls,
                traces=traces,
                reason="selected candidate is not an eligible task candidate",
            )
        support = tuple(
            sorted(observed_evidence_by_candidate.get(final.selected_candidate_id, set()))
        )
        if not support:
            return _blocked(
                task=task,
                binding=binding,
                model_calls=model_calls,
                traces=traces,
                reason="selected candidate did not observe authority support",
            )
        if not _observed_distinguishing_authority_content(
            task=task,
            candidate_id=final.selected_candidate_id,
            observed_content=observed_authority_content_by_candidate.get(
                final.selected_candidate_id, []
            ),
        ):
            return _blocked(
                task=task,
                binding=binding,
                model_calls=model_calls,
                traces=traces,
                reason="selected candidate did not observe distinguishing authority content",
            )
        if set(final.rejected_candidate_ids) != expected_rejected - {final.selected_candidate_id}:
            return _blocked(
                task=task,
                binding=binding,
                model_calls=model_calls,
                traces=traces,
                reason="final response rejected candidates do not match the sealed task",
            )
        source_ids = tuple(
            sorted({observed_sources_by_evidence[evidence_id] for evidence_id in support})
        )
        proposal = _proposal(
            task=task,
            binding=binding,
            decision=ResolutionDecision.ACCEPTED,
            selected_candidate_id=final.selected_candidate_id,
            supporting_evidence_ids=support,
            source_ids=source_ids,
            traces=tuple(traces),
            limitation=final.limitation,
        )
    else:
        if final.selected_candidate_id is not None:
            return _blocked(
                task=task,
                binding=binding,
                model_calls=model_calls,
                traces=traces,
                reason="abstained final response selected a candidate",
            )
        if set(final.rejected_candidate_ids) != expected_rejected:
            return _blocked(
                task=task,
                binding=binding,
                model_calls=model_calls,
                traces=traces,
                reason="final response rejected candidates do not match the sealed task",
            )
        proposal = _proposal(
            task=task,
            binding=binding,
            decision=ResolutionDecision.ABSTAINED,
            selected_candidate_id=None,
            supporting_evidence_ids=(),
            source_ids=(),
            traces=tuple(traces),
            limitation=final.limitation,
        )
    return SemanticResolutionResult(
        proposal=proposal, model_calls=tuple(model_calls), tool_traces=tuple(traces)
    )


__all__ = [
    "MAX_OUTPUT_TOKENS",
    "MAX_PROVIDER_TURNS",
    "MAX_RENDERED_INPUT_TOKENS",
    "MAX_TOOL_CALLS",
    "SemanticResolutionResult",
    "run_semantic_resolution_agent",
]
