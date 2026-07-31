"""Payload-free research metrics for selectively activated bounded Agents.

Records are stored with the ingestion run. They contain aggregate execution
metadata and never store prompts, model responses, tool arguments, tool results,
or reasoning text.
"""

from __future__ import annotations

from typing import Any, Literal, Sequence

from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.utils.identifiers import stable_id


AgentRole = Literal["semantic_resolution"]
AgentTaskScope = Literal["facility", "terminology"]
AgentExecutionMode = Literal[
    "activated",
    "deterministic_bypass",
    "not_reached",
]
AgentUsageOutcome = Literal[
    "accepted",
    "abstained",
    "blocked",
    "not_applicable",
]

class AgentUsageRecord(StrictModel):
    """One aggregate, payload-free execution record for one bounded role."""

    source_id: str = Field(min_length=1)
    event_id: str | None = None
    task_id: str = Field(min_length=1)
    role: AgentRole
    task_scope: AgentTaskScope
    execution_mode: AgentExecutionMode
    outcome: AgentUsageOutcome
    detail_status: str = ""
    activation_reason: str = Field(min_length=1)
    provider_call_count: int = Field(default=0, ge=0)
    tool_call_count: int = Field(default=0, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    provider_latency_ms: float = Field(default=0.0, ge=0.0)
    tool_latency_ms: float = Field(default=0.0, ge=0.0)


def build_agent_usage_records(
    *,
    source_id: str,
    state: dict[str, Any],
) -> tuple[AgentUsageRecord, AgentUsageRecord]:
    """Build the fixed facility and terminology resolution usage rows."""

    facility = _semantic_usage_record(
        source_id=source_id,
        event_id=_event_id(state),
        task_scope="facility",
        result=state.get("facility_authority_result"),
    )
    terminology = _semantic_usage_record(
        source_id=source_id,
        event_id=_event_id(state),
        task_scope="terminology",
        result=state.get("terminology_authority_result"),
    )
    return facility, terminology


def build_blocked_agent_usage_records(
    *,
    source_id: str,
    activation_reason: str = "workflow_exception_before_usage_capture",
) -> tuple[AgentUsageRecord, AgentUsageRecord]:
    """Represent a workflow exception when no finer usage trace was returned."""

    return tuple(
        AgentUsageRecord(
            source_id=source_id,
            event_id=None,
            task_id=stable_id("agent-usage-task", source_id, role, task_scope),
            role=role,
            task_scope=task_scope,
            execution_mode="not_reached",
            outcome="blocked",
            detail_status="workflow_exception",
            activation_reason=activation_reason,
        )
        for role, task_scope in (
            ("semantic_resolution", "facility"),
            ("semantic_resolution", "terminology"),
        )
    )  # type: ignore[return-value]


def _semantic_usage_record(
    *,
    source_id: str,
    event_id: str | None,
    task_scope: Literal["facility", "terminology"],
    result: Any | None,
) -> AgentUsageRecord:
    if result is None:
        return _not_reached_record(
            source_id=source_id,
            event_id=event_id,
            role="semantic_resolution",
            task_scope=task_scope,
            activation_reason="authority_resolution_not_reached",
        )
    model_calls = tuple(getattr(result, "model_calls", ()) or ())
    tool_traces = tuple(getattr(result, "resolution_tool_traces", ()) or ())
    decision = _enum_value(
        getattr(getattr(result, "domain_outcome", None), "decision", "blocked")
    )
    outcome: AgentUsageOutcome
    if decision == "accepted":
        outcome = "accepted"
    elif decision in {"abstained", "insufficient"}:
        outcome = "abstained"
    else:
        outcome = "blocked"
    task = getattr(result, "resolution_task", None)
    task_id = getattr(task, "task_id", None) or stable_id(
        "agent-usage-task",
        source_id,
        "semantic_resolution",
        task_scope,
    )
    return _usage_record(
        source_id=source_id,
        event_id=event_id,
        task_id=task_id,
        role="semantic_resolution",
        task_scope=task_scope,
        execution_mode=("activated" if model_calls else "deterministic_bypass"),
        outcome=outcome,
        detail_status=decision,
        activation_reason=(
            "multiple_eligible_authority_candidates"
            if model_calls
            else (
                "unique_eligible_authority_candidate"
                if outcome == "accepted"
                else "authority_path_terminal_without_model"
            )
        ),
        model_calls=model_calls,
        tool_traces=tool_traces,
    )


def _usage_record(
    *,
    source_id: str,
    event_id: str | None,
    task_id: str,
    role: AgentRole,
    task_scope: AgentTaskScope,
    execution_mode: AgentExecutionMode,
    outcome: AgentUsageOutcome,
    detail_status: str,
    activation_reason: str,
    model_calls: Sequence[Any],
    tool_traces: Sequence[Any],
) -> AgentUsageRecord:
    return AgentUsageRecord(
        source_id=source_id,
        event_id=event_id or None,
        task_id=task_id,
        role=role,
        task_scope=task_scope,
        execution_mode=execution_mode,
        outcome=outcome,
        detail_status=detail_status,
        activation_reason=activation_reason,
        provider_call_count=len(model_calls),
        tool_call_count=len(tool_traces),
        input_tokens=sum(int(getattr(call, "input_tokens", 0)) for call in model_calls),
        output_tokens=sum(int(getattr(call, "output_tokens", 0)) for call in model_calls),
        provider_latency_ms=sum(
            float(getattr(call, "latency_ms", 0.0)) for call in model_calls
        ),
        tool_latency_ms=sum(
            float(getattr(trace, "duration_ms", 0.0)) for trace in tool_traces
        ),
    )


def _not_reached_record(
    *,
    source_id: str,
    event_id: str | None,
    role: AgentRole,
    task_scope: AgentTaskScope,
    activation_reason: str,
    task_id: str | None = None,
) -> AgentUsageRecord:
    return AgentUsageRecord(
        source_id=source_id,
        event_id=event_id,
        task_id=task_id
        or stable_id("agent-usage-task", source_id, role, task_scope),
        role=role,
        task_scope=task_scope,
        execution_mode="not_reached",
        outcome="not_applicable",
        detail_status="not_reached",
        activation_reason=activation_reason,
    )


def _event_id(state: dict[str, Any]) -> str | None:
    return (
        str(state.get("event_uri") or state.get("resolution_event_id") or "")
        or None
    )


def _enum_value(value: Any) -> str:
    return str(getattr(value, "value", value)).lower()
