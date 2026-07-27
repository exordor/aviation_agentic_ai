"""Bounded model -> tool batch -> preflight validation -> revision loop for case assembly."""

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
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    AssemblyStatus,
    CaseAssemblyProposal,
    CaseAssemblyTask,
    ComponentLayerResult,
    ComponentLayerStatus,
    ContractExecutionBinding,
    ValidationFeedback,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.case_assembly_tools import (
    CaseAssemblyToolGateway,
    CaseAssemblyToolResult,
    build_case_assembly_tools,
    compile_case_assembly_proposal,
    preflight_validate_case_assembly_proposal,
)
from aviation_agentic_ai.agent_system.graph_patch import parse_case_assembly_output
from aviation_agentic_ai.agent_system.prompts import DEFAULT_PROMPT_CATALOG, assemble_prompt
from aviation_agentic_ai.agent_system.tool_model import ToolCallingModel

MAX_ASSEMBLY_PROVIDER_TURNS = 3
MAX_ASSEMBLY_TOOL_CALLS = 6
MAX_RENDERED_INPUT_TOKENS = 4096
MAX_OUTPUT_TOKENS = 512


@dataclass(frozen=True)
class CaseAssemblyResult:
    """Result of running the Decision Case Assembly Agent."""

    proposal: CaseAssemblyProposal
    model_calls: tuple[ModelCallRecord, ...]
    tool_traces: tuple[ToolTraceEntry, ...]
    feedback: ValidationFeedback | None = None
    failure_reason: str | None = None


def _base_messages(task: CaseAssemblyTask, *, catalog_path: str) -> list[BaseMessage]:
    assembled = assemble_prompt(
        "decision_case_assembly",
        {
            "case_id": task.case_id,
            "required_case_slots": "\n".join(task.required_case_slots) or "(none)",
            "optional_case_slots": "\n".join(task.optional_case_slots) or "(none)",
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


def _case_assembly_trace_id(
    *,
    task: CaseAssemblyTask,
    ordinal: int,
    tool: str,
    parameters: dict[str, str],
    result_refs: list[str],
    source_ids: list[str],
    status: Literal["ok", "blocked"],
    error: str | None,
) -> str:
    return stable_contract_id(
        "case-assembly-tool-trace",
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


def _build_case_assembly_trace(
    *,
    task: CaseAssemblyTask,
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
    trace_id = _case_assembly_trace_id(
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


def _model_tool_observation(result: CaseAssemblyToolResult) -> str:
    return result.model_dump_json()


def _tool_result_bindings(
    result: CaseAssemblyToolResult,
) -> tuple[list[str], list[str]]:
    """Project exact returned record and source IDs into the audit trace."""

    result_refs = sorted(
        {
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


def _message_text(message: AIMessage) -> str:
    if isinstance(message.content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in message.content
        )
    return str(message.content or "")


def _compile_blocked_result(
    *,
    task: CaseAssemblyTask,
    binding: ContractExecutionBinding,
    model_calls: list[ModelCallRecord],
    traces: list[ToolTraceEntry],
    reason: str,
    feedback: ValidationFeedback | None = None,
    component_layer_results: Sequence[ComponentLayerResult] = (),
    limitations: Sequence[str] = (),
) -> CaseAssemblyResult:
    blocked_layers = tuple(component_layer_results)
    if blocked_layers:
        blocked_layers = (
            *blocked_layers,
            ComponentLayerResult(
                layer_id="decision_case_assembly",
                status=ComponentLayerStatus.BLOCKED,
                required_for_task=True,
                blocking_error_id=stable_contract_id(
                    "case-assembly-agent-error",
                    task.task_id,
                    task.payload_checksum,
                    reason,
                ),
            ),
        )
    proposal = compile_case_assembly_proposal(
        task=task,
        assembly_status=AssemblyStatus.BLOCKED,
        component_layer_results=blocked_layers,
        limitations=(*limitations, reason),
        tool_trace_ids=[trace.tool_call_id for trace in traces if trace.tool_call_id],
        binding=binding,
    )
    return CaseAssemblyResult(
        proposal=proposal,
        model_calls=tuple(model_calls),
        tool_traces=tuple(traces),
        feedback=feedback,
        failure_reason=reason,
    )


def run_case_assembly_agent(
    *,
    task: CaseAssemblyTask,
    binding: ContractExecutionBinding,
    tool_model_factory: Callable[[list[BaseTool]], ToolCallingModel] | None,
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
    assembly_status: AssemblyStatus | None = None,
    component_layer_results: Sequence[ComponentLayerResult] = (),
    limitations: Sequence[str] = (),
) -> CaseAssemblyResult:
    """Run the bounded Case Assembly Agent loop."""

    model_calls: list[ModelCallRecord] = []
    traces: list[ToolTraceEntry] = []
    messages = _base_messages(task, catalog_path=catalog_path)
    _blocked = partial(
        _compile_blocked_result,
        component_layer_results=tuple(component_layer_results),
        limitations=tuple(limitations),
    )

    if tool_model_factory is None:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Decision Case Assembly Agent model factory is unavailable",
        )

    tools = build_case_assembly_tools(CaseAssemblyToolGateway(task=task))
    if _estimated_input_tokens(messages, bound_tools=tools) > MAX_RENDERED_INPUT_TOKENS:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Decision Case Assembly Agent rendered input budget exceeded",
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
                f"Decision Case Assembly Agent model construction failed: {type(exc).__name__}: {exc}"
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
                agent="decision_case_assembly",
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
            reason=sanitize_text(f"Decision Case Assembly Agent provider failed: {provider_error}"),
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
            reason="Decision Case Assembly Agent output-token cap exceeded",
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
    allowed_tool_count = min(MAX_ASSEMBLY_TOOL_CALLS, task.remaining_tool_budget)
    if not calls:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Decision Case Assembly Agent did not select a tool",
        )
    if len(calls) > allowed_tool_count:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Decision Case Assembly Agent tool-call budget exceeded",
        )

    seen_ids: set[str] = set()
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
                reason=f"unknown Decision Case Assembly Agent tool: {name}",
            )
        if not isinstance(arguments, dict):
            return _blocked(
                task=task,
                binding=binding,
                model_calls=model_calls,
                traces=traces,
                reason=f"invalid arguments for assembly tool: {name}",
            )

        seen_ids.add(call_id)
        started = time.perf_counter()
        safe_parameters = _safe_parameters(arguments)
        try:
            content = registry[name].invoke(arguments)
            result = CaseAssemblyToolResult.model_validate_json(str(content))
        except Exception as exc:
            error = sanitize_text(f"{type(exc).__name__}: {exc}")
            trace = _build_case_assembly_trace(
                task=task,
                ordinal=len(traces),
                tool=name,
                parameters=safe_parameters,
                status="blocked",
                duration_ms=(time.perf_counter() - started) * 1000.0,
                error=error,
            )
            traces.append(trace)
            return _blocked(
                task=task,
                binding=binding,
                model_calls=model_calls,
                traces=traces,
                reason=trace.error or "assembly tool failed",
            )

        duration = (time.perf_counter() - started) * 1000.0
        result_refs, source_ids = _tool_result_bindings(result)
        traces.append(
            _build_case_assembly_trace(
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

    # Provider turn 2: Emit proposal
    turn_2_messages = [messages[0], messages[-1], first.message, *tool_messages]
    if _estimated_input_tokens(turn_2_messages) > MAX_RENDERED_INPUT_TOKENS:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Decision Case Assembly Agent rendered input budget exceeded",
        )

    provider_started = time.perf_counter()
    try:
        second = model.invoke(turn_2_messages, phase="emit_proposal")
    except Exception as exc:
        provider_error = sanitize_text(f"{type(exc).__name__}: {exc}")
        model_calls.append(
            ModelCallRecord(
                agent="decision_case_assembly",
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
            reason=sanitize_text(f"Decision Case Assembly Agent provider failed: {provider_error}"),
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
            reason="Decision Case Assembly Agent output-token cap exceeded",
        )
    if second.message is None:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="provider returned no AI message",
        )

    proposal_text = _message_text(second.message).strip()
    try:
        parsed_sections = parse_case_assembly_output(
            proposal_text,
            allowed_validation_profile_ids=frozenset({task.schema_profile_id}),
        )
    except Exception as exc:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=sanitize_text(f"malformed case assembly proposal output: {exc}"),
        )

    try:
        proposal = compile_case_assembly_proposal(
            task=task,
            assembly_status=assembly_status,
            component_layer_results=component_layer_results,
            proposed_facts=parsed_sections.proposed_facts,
            profile_gaps=parsed_sections.profile_gaps,
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
            reason=sanitize_text(f"case assembly proposal compilation error: {exc}"),
        )

    # Preflight Validation
    feedback = preflight_validate_case_assembly_proposal(
        task=task,
        proposal=proposal,
        binding=binding,
    )

    if feedback is None:
        # Valid on first try!
        return CaseAssemblyResult(
            proposal=proposal,
            model_calls=tuple(model_calls),
            tool_traces=tuple(traces),
            feedback=None,
        )

    if not feedback.repairable:
        # Hard violation -> block immediately without revision
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=f"hard validation violation: {feedback.violation_code}",
            feedback=feedback,
        )

    # Repairable defect -> Provider turn 3 (validation-guided revision)
    revision_user_msg = (
        f"REVISION_FEEDBACK\n"
        f"VIOLATION_CODE: {feedback.violation_code}\n"
        f"AFFECTED_ITEM: {feedback.affected_proposal_item_id}\n"
        f"ALLOWED_CORRECTIONS: {', '.join(feedback.allowed_corrections)}\n\n"
        f"Please emit a revised proposal with GRAPH_PATCH and PROFILE_GAPS correcting only this item using an allowed correction."
    )
    turn_3_messages = [
        *turn_2_messages,
        second.message,
        HumanMessage(content=revision_user_msg),
    ]

    if _estimated_input_tokens(turn_3_messages) > MAX_RENDERED_INPUT_TOKENS:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Decision Case Assembly Agent rendered input budget exceeded on revision turn",
            feedback=feedback,
        )

    provider_started = time.perf_counter()
    try:
        third = model.invoke(turn_3_messages, phase="revision")
    except Exception as exc:
        provider_error = sanitize_text(f"{type(exc).__name__}: {exc}")
        model_calls.append(
            ModelCallRecord(
                agent="decision_case_assembly",
                raw_response="",
                latency_ms=(time.perf_counter() - provider_started) * 1000.0,
                attempt=3,
                error=provider_error,
            )
        )
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=sanitize_text(f"Decision Case Assembly Agent provider revision failed: {provider_error}"),
            feedback=feedback,
        )

    model_calls.append(third.record)
    if third.record.error:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=third.record.error,
            feedback=feedback,
        )
    if third.record.output_tokens > MAX_OUTPUT_TOKENS:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="Decision Case Assembly Agent output-token cap exceeded on revision turn",
            feedback=feedback,
        )
    if third.message is None:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason="provider returned no AI message on revision turn",
            feedback=feedback,
        )

    revised_text = _message_text(third.message).strip()
    try:
        revised_sections = parse_case_assembly_output(
            revised_text,
            allowed_validation_profile_ids=frozenset({task.schema_profile_id}),
        )
    except Exception as exc:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=sanitize_text(f"malformed revised case assembly proposal: {exc}"),
            feedback=feedback,
        )

    try:
        revised_proposal = compile_case_assembly_proposal(
            task=task,
            assembly_status=assembly_status,
            component_layer_results=component_layer_results,
            proposed_facts=revised_sections.proposed_facts,
            profile_gaps=revised_sections.profile_gaps,
            limitations=limitations,
            tool_trace_ids=[trace.tool_call_id for trace in traces if trace.tool_call_id],
            revision_count=1,
            binding=binding,
        )
    except Exception as exc:
        return _blocked(
            task=task,
            binding=binding,
            model_calls=model_calls,
            traces=traces,
            reason=sanitize_text(f"revised case assembly proposal compilation error: {exc}"),
            feedback=feedback,
        )

    revised_feedback = preflight_validate_case_assembly_proposal(
        task=task,
        proposal=revised_proposal,
        binding=binding,
    )

    if revised_feedback is None:
        return CaseAssemblyResult(
            proposal=revised_proposal,
            model_calls=tuple(model_calls),
            tool_traces=tuple(traces),
            feedback=None,
        )

    return _blocked(
        task=task,
        binding=binding,
        model_calls=model_calls,
        traces=traces,
        reason=f"validation feedback not resolved after revision: {revised_feedback.violation_code}",
        feedback=revised_feedback,
    )
