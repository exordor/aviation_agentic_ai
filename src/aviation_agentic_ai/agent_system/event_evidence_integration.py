"""Bounded model -> compact candidate selection -> deterministic event evidence integration."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import partial
import json
import time
from typing import Any, Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool

from aviation_agentic_ai.agent_system.audit import sanitize_json_value, sanitize_text
from aviation_agentic_ai.agent_system.contracts import ModelCallRecord, ToolTraceEntry
from aviation_agentic_ai.agent_system.construction_contracts import (
    EventEvidenceIntegrationStatus,
    EventEvidenceIntegrationProposal,
    EventEvidenceIntegrationSelection,
    EventEvidenceIntegrationTask,
    EvidenceLayerResult,
    EvidenceLayerStatus,
    ContractExecutionBinding,
    EventEvidenceIntegrationFeedback,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
    EventEvidenceIntegrationToolGateway,
    EventEvidenceIntegrationToolResult,
    build_event_evidence_integration_tools,
    compile_event_evidence_integration_proposal,
    preflight_validate_event_evidence_proposal,
)
from aviation_agentic_ai.agent_system.prompts import DEFAULT_PROMPT_CATALOG, assemble_prompt
from aviation_agentic_ai.agent_system.tool_model import ToolCallingModel

MAX_INTEGRATION_TOOL_CALLS = 1
MAX_INTEGRATION_PROVIDER_TURNS = 2
MAX_INTEGRATION_RENDERED_INPUT_TOKENS = 4096
MAX_INTEGRATION_OUTPUT_TOKENS = 10_000


@dataclass(frozen=True)
class EventEvidenceIntegrationResult:
    """Result of running the Event Evidence Integration Agent."""

    proposal: EventEvidenceIntegrationProposal
    model_calls: tuple[ModelCallRecord, ...]
    tool_traces: tuple[ToolTraceEntry, ...]
    feedback: EventEvidenceIntegrationFeedback | None = None
    failure_reason: str | None = None


def _base_messages(task: EventEvidenceIntegrationTask, *, catalog_path: str) -> list[BaseMessage]:
    assembled = assemble_prompt(
        "event_evidence_integration",
        {
            "event_id": task.event_id,
            "required_event_slots": "\n".join(task.required_event_slots) or "(none)",
            "optional_event_slots": "\n".join(task.optional_event_slots) or "(none)",
            "missing_slots": "\n".join(task.missing_slots) or "(none)",
            "schema_profile_id": task.schema_profile_id,
            "available_evidence_layer_ids": "\n".join(task.available_evidence_layer_ids) or "(none)",
            "selected_evidence_claim_ids": "\n".join(
                task.selected_evidence_claim_ids
            )
            or "(none)",
            "resolution_proposal_ids": "\n".join(task.resolution_proposal_ids)
            or "(none)",
            "context_association_ids": "\n".join(task.context_association_ids)
            or "(none)",
            "public_observation_ids": "\n".join(task.public_observation_ids)
            or "(none)",
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


def _tool_definition(tool: BaseTool) -> dict[str, Any]:
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
    return (len(rendered.encode("utf-8")) + 3) // 4


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


def _canonical_trace_value(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _event_evidence_integration_trace_id(
    *,
    task: EventEvidenceIntegrationTask,
    ordinal: int,
    tool: str,
    parameters: dict[str, str],
    result_refs: list[str],
    source_ids: list[str],
    status: Literal["ok", "blocked"],
    error: str | None,
) -> str:
    return stable_contract_id(
        "event-evidence-integration-tool-trace",
        task.task_id,
        task.payload_checksum,
        str(ordinal),
        tool,
        _canonical_trace_value(parameters),
        _canonical_trace_value(result_refs),
        _canonical_trace_value(source_ids),
        status,
        _canonical_trace_value(error),
    )


def _build_event_evidence_integration_trace(
    *,
    task: EventEvidenceIntegrationTask,
    ordinal: int,
    tool: str,
    parameters: dict[str, str],
    result_refs: list[str] | None = None,
    source_ids: list[str] | None = None,
    status: Literal["ok", "blocked"] = "ok",
    duration_ms: float = 0.0,
    error: str | None = None,
) -> ToolTraceEntry:
    bound_result_refs = list(result_refs or [])
    bound_source_ids = list(source_ids or [])
    trace_id = _event_evidence_integration_trace_id(
        task=task,
        ordinal=ordinal,
        tool=tool,
        parameters=parameters,
        result_refs=bound_result_refs,
        source_ids=bound_source_ids,
        status=status,
        error=error,
    )
    return ToolTraceEntry(
        tool_call_id=trace_id,
        tool=tool,
        parameters=parameters,
        result_refs=bound_result_refs,
        source_ids=bound_source_ids,
        status=status,
        duration_ms=duration_ms,
        error=error,
    )


def _model_tool_observation(result: EventEvidenceIntegrationToolResult) -> str:
    return result.model_dump_json(exclude_defaults=True)


def _tool_result_bindings(
    result: EventEvidenceIntegrationToolResult,
) -> tuple[list[str], list[str]]:
    """Project exact returned record and source IDs into the audit trace."""

    result_refs = sorted(
        {
            *([result.candidate_bundle_id] if result.candidate_bundle_id else []),
            *(row.evidence_id for row in result.evidence_records),
            *(
                row.resolution_proposal_id
                for row in result.resolution_records
            ),
            *(row.association_id for row in result.context_associations),
            *(row.observation_id for row in result.public_observations),
        }
    )
    source_ids = sorted(
        {
            *(row.source_id for row in result.evidence_records),
            *(
                source_id
                for row in result.resolution_records
                for source_id in row.authority_source_ids
            ),
            *(row.source_id for row in result.context_associations),
            *(row.source_id for row in result.public_observations),
        }
    )
    return result_refs, source_ids


def _execute_tool_batch(
    *,
    task: EventEvidenceIntegrationTask,
    calls: list[dict[str, Any]],
    registry: dict[str, BaseTool],
    traces: list[ToolTraceEntry],
    seen_ids: set[str],
    allowed_tool_count: int,
) -> tuple[list[ToolMessage], str | None]:
    """Execute one native tool batch within the cumulative sealed-task budget."""

    if len(traces) + len(calls) > allowed_tool_count:
        return [], "Event Evidence Integration Agent tool-call budget exceeded"

    tool_messages: list[ToolMessage] = []
    for call in calls:
        call_id = str(call.get("id") or "").strip()
        name = str(call.get("name") or "").strip()
        arguments = call.get("args")
        if not call_id or call_id in seen_ids:
            return [], "missing or duplicate native tool-call ID"
        if name not in registry:
            return [], f"unknown Event Evidence Integration Agent tool: {name}"
        if not isinstance(arguments, dict):
            return [], f"invalid arguments for integration tool: {name}"

        seen_ids.add(call_id)
        started = time.perf_counter()
        safe_parameters = _safe_parameters(arguments)
        try:
            content = registry[name].invoke(arguments)
            result = EventEvidenceIntegrationToolResult.model_validate_json(str(content))
        except Exception as exc:
            error = sanitize_text(f"{type(exc).__name__}: {exc}")
            trace = _build_event_evidence_integration_trace(
                task=task,
                ordinal=len(traces),
                tool=name,
                parameters=safe_parameters,
                status="blocked",
                duration_ms=(time.perf_counter() - started) * 1000.0,
                error=error,
            )
            traces.append(trace)
            return [], trace.error or "integration tool failed"

        duration = (time.perf_counter() - started) * 1000.0
        result_refs, source_ids = _tool_result_bindings(result)
        traces.append(
            _build_event_evidence_integration_trace(
                task=task,
                ordinal=len(traces),
                tool=name,
                parameters=safe_parameters,
                result_refs=result_refs,
                source_ids=source_ids,
                status="ok",
                duration_ms=duration,
            )
        )
        tool_messages.append(
            ToolMessage(
                content=_model_tool_observation(result),
                tool_call_id=call_id,
            )
        )
    return tool_messages, None


def _message_text(message: AIMessage) -> str:
    if isinstance(message.content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in message.content
        )
    return str(message.content or "")


def _output_budget_failure(record: ModelCallRecord) -> str | None:
    """Distinguish provider truncation from a local observed-budget breach."""

    if record.finish_reason == "length":
        return "Event Evidence Integration Agent provider output was truncated"
    if record.output_tokens > MAX_INTEGRATION_OUTPUT_TOKENS:
        return "Event Evidence Integration Agent output budget exceeded"
    return None


def _compile_blocked_result(
    *,
    task: EventEvidenceIntegrationTask,
    binding: ContractExecutionBinding,
    model_calls: list[ModelCallRecord],
    traces: list[ToolTraceEntry],
    reason: str,
    feedback: EventEvidenceIntegrationFeedback | None = None,
    evidence_layer_results: Sequence[EvidenceLayerResult] = (),
    limitations: Sequence[str] = (),
) -> EventEvidenceIntegrationResult:
    blocked_layers = tuple(evidence_layer_results)
    if blocked_layers:
        blocked_layers = (
            *blocked_layers,
            EvidenceLayerResult(
                layer_id="event_evidence_integration",
                status=EvidenceLayerStatus.BLOCKED,
                required_for_task=True,
                blocking_error_id=stable_contract_id(
                    "event-evidence-integration-agent-error",
                    task.task_id,
                    task.payload_checksum,
                    reason,
                ),
            ),
        )
    proposal = compile_event_evidence_integration_proposal(
        task=task,
        integration_status=EventEvidenceIntegrationStatus.BLOCKED,
        evidence_layer_results=blocked_layers,
        proposed_facts=(),
        evidence_bindings=(),
        resolution_proposal_ids=(),
        context_association_ids=(),
        profile_gaps=(),
        source_snapshot_bindings=(),
        limitations=(*limitations, reason),
        tool_trace_ids=[trace.tool_call_id for trace in traces if trace.tool_call_id],
        binding=binding,
    )
    return EventEvidenceIntegrationResult(
        proposal=proposal,
        model_calls=tuple(model_calls),
        tool_traces=tuple(traces),
        feedback=feedback,
        failure_reason=reason,
    )


def _compile_insufficient_result(
    *,
    task: EventEvidenceIntegrationTask,
    binding: ContractExecutionBinding,
    model_calls: list[ModelCallRecord],
    traces: list[ToolTraceEntry],
    reason: str,
    evidence_layer_results: Sequence[EvidenceLayerResult] = (),
    limitations: Sequence[str] = (),
) -> EventEvidenceIntegrationResult:
    """Compile an honest non-publishable result after model abstention."""

    agent_layer = EvidenceLayerResult(
        layer_id="event_evidence_integration",
        status=EvidenceLayerStatus.INSUFFICIENT,
        required_for_task=True,
        missing_reason_code="agent_abstained",
    )
    proposal = compile_event_evidence_integration_proposal(
        task=task,
        integration_status=EventEvidenceIntegrationStatus.INSUFFICIENT,
        evidence_layer_results=(*evidence_layer_results, agent_layer),
        limitations=(*limitations, reason),
        tool_trace_ids=[
            trace.tool_call_id for trace in traces if trace.tool_call_id
        ],
        binding=binding,
    )
    return EventEvidenceIntegrationResult(
        proposal=proposal,
        model_calls=tuple(model_calls),
        tool_traces=tuple(traces),
        failure_reason=reason,
    )


def run_event_evidence_integration_agent(
    *,
    task: EventEvidenceIntegrationTask,
    binding: ContractExecutionBinding,
    tool_model_factory: Callable[[list[BaseTool]], ToolCallingModel] | None,
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
    integration_status: EventEvidenceIntegrationStatus | None = None,
    evidence_layer_results: Sequence[EvidenceLayerResult] = (),
    limitations: Sequence[str] = (),
) -> EventEvidenceIntegrationResult:
    """Run the bounded Event Evidence Integration Agent loop."""

    model_calls: list[ModelCallRecord] = []
    traces: list[ToolTraceEntry] = []
    messages = _base_messages(task, catalog_path=catalog_path)
    _blocked = partial(
        _compile_blocked_result,
        evidence_layer_results=tuple(evidence_layer_results),
        limitations=tuple(limitations),
    )

    if tool_model_factory is None:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Event Evidence Integration Agent model factory is unavailable",
        )

    tools = build_event_evidence_integration_tools(EventEvidenceIntegrationToolGateway(task=task))
    if _estimated_input_tokens(messages, bound_tools=tools) > MAX_INTEGRATION_RENDERED_INPUT_TOKENS:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Event Evidence Integration Agent rendered input budget exceeded",
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
                f"Event Evidence Integration Agent model construction failed: {type(exc).__name__}: {exc}"
            ),
        )

    # Provider turn 1: Tool Selection
    provider_started = time.perf_counter()
    try:
        first = model.invoke(messages, phase="select_tool")
    except Exception as exc:
        provider_error = sanitize_text(f"{type(exc).__name__}: {exc}")
        model_calls.append(
            ModelCallRecord(
                agent="event_evidence_integration",
                raw_response="",
                latency_ms=(time.perf_counter() - provider_started) * 1000.0,
                attempt=1,
                error=provider_error,
            )
        )
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=sanitize_text(f"Event Evidence Integration Agent provider failed: {provider_error}"),
        )

    model_calls.append(first.record)
    if output_failure := _output_budget_failure(first.record):
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=output_failure,
        )
    if first.record.error:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=first.record.error,
        )
    if first.message is None:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="provider returned no AI message",
        )

    calls = [dict(call) for call in first.message.tool_calls]
    allowed_tool_count = min(MAX_INTEGRATION_TOOL_CALLS, task.remaining_tool_budget)
    if not calls:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Event Evidence Integration Agent did not select a tool",
        )
    if len(calls) > allowed_tool_count:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Event Evidence Integration Agent tool-call budget exceeded",
        )

    seen_ids: set[str] = set()
    tool_messages, tool_error = _execute_tool_batch(
        task=task,
        calls=calls,
        registry=registry,
        traces=traces,
        seen_ids=seen_ids,
        allowed_tool_count=allowed_tool_count,
    )
    if tool_error is not None:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=tool_error,
        )

    if len(calls) != 1 or calls[0].get("name") != "get_candidate_bundle":
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=(
                "Event Evidence Integration Agent must inspect exactly one "
                "candidate bundle"
            ),
        )

    # Provider turn 2: emit one compact accept/abstain decision. The full
    # facts remain in the sealed task and are never regenerated by the model.
    turn_2_messages = [messages[0], messages[-1], first.message, *tool_messages]
    if _estimated_input_tokens(turn_2_messages) > MAX_INTEGRATION_RENDERED_INPUT_TOKENS:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Event Evidence Integration Agent rendered input budget exceeded",
        )

    provider_started = time.perf_counter()
    try:
        second = model.invoke(turn_2_messages, phase="emit_proposal")
    except Exception as exc:
        provider_error = sanitize_text(f"{type(exc).__name__}: {exc}")
        model_calls.append(
            ModelCallRecord(
                agent="event_evidence_integration",
                raw_response="",
                latency_ms=(time.perf_counter() - provider_started) * 1000.0,
                attempt=2,
                error=provider_error,
            )
        )
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=sanitize_text(f"Event Evidence Integration Agent provider failed: {provider_error}"),
        )

    model_calls.append(second.record)
    if output_failure := _output_budget_failure(second.record):
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=output_failure,
        )
    if second.record.error:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=second.record.error,
        )
    if second.message is None:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="provider returned no AI message",
        )

    selection_text = _message_text(second.message).strip()
    try:
        selection = EventEvidenceIntegrationSelection.model_validate_json(selection_text)
    except Exception as exc:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=sanitize_text(
                f"malformed event evidence integration selection output: {exc}"
            ),
        )

    expected_bundle_id = stable_contract_id(
        "event-evidence-integration-candidate-bundle",
        task.task_id,
        task.payload_checksum,
    )
    if selection.candidate_bundle_id != expected_bundle_id:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Event Evidence Integration Agent selected the wrong candidate bundle",
        )
    if selection.decision == "abstained":
        return _compile_insufficient_result(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=selection.limitation or "Event Evidence Integration Agent abstained",
            evidence_layer_results=evidence_layer_results,
            limitations=limitations,
        )

    expected_fact_ids = set(task.core_event_fact_ids)
    expected_gap_ids = {
        row.proposal_item_id for row in task.profile_gaps
    }
    if (
        set(selection.selected_fact_ids) != expected_fact_ids
        or set(selection.selected_profile_gap_ids) != expected_gap_ids
    ):
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=(
                "Event Evidence Integration Agent selection differs from the "
                "sealed candidate bundle"
            ),
        )

    try:
        proposal = compile_event_evidence_integration_proposal(
            task=task,
            integration_status=integration_status,
            evidence_layer_results=evidence_layer_results,
            limitations=limitations,
            tool_trace_ids=[trace.tool_call_id for trace in traces if trace.tool_call_id],
            binding=binding,
        )
    except Exception as exc:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=sanitize_text(f"event evidence integration proposal compilation error: {exc}"),
        )

    feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=proposal,
        binding=binding,
    )

    if feedback is None:
        return EventEvidenceIntegrationResult(
            proposal=proposal,
            model_calls=tuple(model_calls),
            tool_traces=tuple(traces),
            feedback=None,
        )

    return _blocked(
        task=task,
        binding=binding,
        model_calls=model_calls,
        traces=traces,
        reason=f"sealed candidate validation failed: {feedback.violation_code}",
        feedback=feedback,
    )
