"""Corpus-bound research metrics for selectively activated bounded Agents.

The usage sidecar is derived after a TMI event workflow finishes. It records only
aggregate execution metadata and never stores prompts, model responses, tool
arguments, tool results, or reasoning text.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal, Sequence

from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.cross_source.identifiers import stable_id


AgentRole = Literal["semantic_resolution", "event_evidence_integration"]
AgentTaskScope = Literal["facility", "terminology", "tmi_event_evidence"]
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

AGENT_USAGE_DIRECTORY = "agent_usage"
AGENT_USAGE_ROWS = "agent_usage.jsonl"
AGENT_USAGE_MANIFEST = "agent_usage_manifest.json"
STAGING_AGENT_USAGE_ROWS = "agent_usage.jsonl"


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


class AgentUsageTotals(StrictModel):
    """Compact aggregate shown after a corpus build."""

    activated_count: int = Field(default=0, ge=0)
    deterministic_bypass_count: int = Field(default=0, ge=0)
    not_reached_count: int = Field(default=0, ge=0)
    accepted_count: int = Field(default=0, ge=0)
    abstained_count: int = Field(default=0, ge=0)
    blocked_count: int = Field(default=0, ge=0)
    not_applicable_count: int = Field(default=0, ge=0)
    provider_call_count: int = Field(default=0, ge=0)
    tool_call_count: int = Field(default=0, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    provider_latency_ms: float = Field(default=0.0, ge=0.0)
    tool_latency_ms: float = Field(default=0.0, ge=0.0)


class AgentUsageManifest(StrictModel):
    """Binding from the non-authoritative usage sidecar to one corpus."""

    manifest_version: Literal["tmi-event-agent-usage-v1"] = (
        "tmi-event-agent-usage-v1"
    )
    corpus_id: str = Field(min_length=1)
    artifact_path: Literal["agent_usage.jsonl"] = AGENT_USAGE_ROWS
    artifact_sha256: str = Field(min_length=64, max_length=64)
    record_count: int = Field(ge=0)
    totals: AgentUsageTotals


def agent_usage_key(
    record: AgentUsageRecord,
) -> tuple[str, AgentRole, AgentTaskScope]:
    """Stable overwrite key for staging and resume."""

    return record.source_id, record.role, record.task_scope


def build_agent_usage_records(
    *,
    source_id: str,
    state: dict[str, Any],
) -> tuple[AgentUsageRecord, AgentUsageRecord, AgentUsageRecord]:
    """Build the fixed facility, terminology, and integration usage rows."""

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
    integration = _event_evidence_integration_usage_record(
        source_id=source_id,
        event_id=_event_id(state),
        state=state,
    )
    return facility, terminology, integration


def build_blocked_agent_usage_records(
    *,
    source_id: str,
    activation_reason: str = "workflow_exception_before_usage_capture",
) -> tuple[AgentUsageRecord, AgentUsageRecord, AgentUsageRecord]:
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
            ("event_evidence_integration", "tmi_event_evidence"),
        )
    )  # type: ignore[return-value]


def summarize_agent_usage(records: Sequence[AgentUsageRecord]) -> AgentUsageTotals:
    """Aggregate the small set of metrics exposed by the sidecar."""

    return AgentUsageTotals(
        activated_count=sum(row.execution_mode == "activated" for row in records),
        deterministic_bypass_count=sum(
            row.execution_mode == "deterministic_bypass" for row in records
        ),
        not_reached_count=sum(row.execution_mode == "not_reached" for row in records),
        accepted_count=sum(row.outcome == "accepted" for row in records),
        abstained_count=sum(row.outcome == "abstained" for row in records),
        blocked_count=sum(row.outcome == "blocked" for row in records),
        not_applicable_count=sum(row.outcome == "not_applicable" for row in records),
        provider_call_count=sum(row.provider_call_count for row in records),
        tool_call_count=sum(row.tool_call_count for row in records),
        input_tokens=sum(row.input_tokens for row in records),
        output_tokens=sum(row.output_tokens for row in records),
        provider_latency_ms=sum(row.provider_latency_ms for row in records),
        tool_latency_ms=sum(row.tool_latency_ms for row in records),
    )


def write_agent_usage_records(
    path: str | Path,
    records: Sequence[AgentUsageRecord],
) -> str:
    """Write stable JSONL and return its SHA-256 checksum."""

    ordered = sorted(records, key=agent_usage_key)
    data = "".join(
        _canonical_json(row.model_dump(mode="json")) + "\n" for row in ordered
    ).encode("utf-8")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def read_agent_usage_records(path: str | Path) -> tuple[AgentUsageRecord, ...]:
    """Read a staging or published usage JSONL file."""

    target = Path(path)
    if not target.is_file():
        return ()
    return tuple(
        AgentUsageRecord.model_validate_json(line)
        for line in target.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def write_agent_usage_sidecar(
    corpus_dir: str | Path,
    *,
    corpus_id: str,
    records: Sequence[AgentUsageRecord],
) -> AgentUsageManifest:
    """Publish a rebuildable usage sidecar outside the canonical manifest."""

    root = Path(corpus_dir) / AGENT_USAGE_DIRECTORY
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / AGENT_USAGE_MANIFEST
    manifest_path.unlink(missing_ok=True)
    ordered = tuple(sorted(records, key=agent_usage_key))
    checksum = write_agent_usage_records(root / AGENT_USAGE_ROWS, ordered)
    manifest = AgentUsageManifest(
        corpus_id=corpus_id,
        artifact_sha256=checksum,
        record_count=len(ordered),
        totals=summarize_agent_usage(ordered),
    )
    manifest_path.write_text(
        manifest.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def read_agent_usage_manifest(
    corpus_dir: str | Path,
) -> AgentUsageManifest | None:
    """Read a published sidecar manifest when present and valid."""

    try:
        return AgentUsageManifest.model_validate_json(
            (
                Path(corpus_dir)
                / AGENT_USAGE_DIRECTORY
                / AGENT_USAGE_MANIFEST
            ).read_text(encoding="utf-8")
        )
    except (OSError, ValueError):
        return None


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


def _event_evidence_integration_usage_record(
    *,
    source_id: str,
    event_id: str | None,
    state: dict[str, Any],
) -> AgentUsageRecord:
    result = state.get("event_evidence_integration_result")
    task = state.get("event_evidence_integration_task")
    if result is None:
        return _not_reached_record(
            source_id=source_id,
            event_id=event_id,
            role="event_evidence_integration",
            task_scope="tmi_event_evidence",
            activation_reason=(
                "required_resolution_unavailable"
                if state.get("resolution_preflight_status") not in {None, "resolved"}
                else "event_evidence_integration_not_reached"
            ),
            task_id=getattr(task, "task_id", None),
        )
    status = _enum_value(
        getattr(getattr(result, "proposal", None), "integration_status", "blocked")
    )
    outcome: AgentUsageOutcome
    if status in {"ok", "partial"}:
        outcome = "accepted"
    elif status == "insufficient":
        outcome = "abstained"
    else:
        outcome = "blocked"
    model_calls = tuple(getattr(result, "model_calls", ()) or ())
    tool_traces = tuple(getattr(result, "tool_traces", ()) or ())
    return _usage_record(
        source_id=source_id,
        event_id=event_id,
        task_id=getattr(task, "task_id", None)
        or stable_id(
            "agent-usage-task",
            source_id,
            "event_evidence_integration",
            "tmi_event_evidence",
        ),
        role="event_evidence_integration",
        task_scope="tmi_event_evidence",
        execution_mode=("activated" if model_calls else "deterministic_bypass"),
        outcome=outcome,
        detail_status=status,
        activation_reason=(
            "noncanonical_evidence_or_schema_choice"
            if model_calls
            else "deterministic_event_evidence_compiler"
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


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
