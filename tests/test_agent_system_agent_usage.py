"""Research-only usage sidecar for selectively activated bounded Agents."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from aviation_agentic_ai.agent_system.agent_usage import (
    AgentUsageRecord,
    build_agent_usage_records,
    write_agent_usage_sidecar,
)
from aviation_agentic_ai.agent_system.contracts import (
    ModelCallRecord,
    ModelToolCall,
    ToolTraceEntry,
)
from aviation_agentic_ai.agent_system.construction_contracts import (
    ResolutionDecision,
)


def _semantic_result(
    *,
    task_id: str,
    event_id: str,
    decision: ResolutionDecision,
    model_calls: tuple[ModelCallRecord, ...] = (),
    tool_traces: tuple[ToolTraceEntry, ...] = (),
) -> SimpleNamespace:
    return SimpleNamespace(
        resolution_task=SimpleNamespace(task_id=task_id, event_id=event_id),
        domain_outcome=SimpleNamespace(decision=decision),
        model_calls=model_calls,
        resolution_tool_traces=tool_traces,
    )


def test_usage_records_distinguish_activation_bypass_and_not_reached() -> None:
    facility_call = ModelCallRecord(
        agent="semantic_resolution",
        raw_response='{"decision":"accepted","private":"not retained"}',
        input_tokens=120,
        output_tokens=18,
        latency_ms=31.5,
        tool_calls=[
            ModelToolCall(
                call_id="call:1",
                name="inspect_candidate",
                arguments={"candidate_id": "facility:KJFK"},
            )
        ],
    )
    facility_trace = ToolTraceEntry(
        tool_call_id="call:1",
        tool="inspect_candidate",
        parameters={"candidate_id": "facility:KJFK"},
        result_refs=["authority:facility:KJFK"],
        duration_ms=4.25,
    )
    state = {
        "resolution_event_id": "event:123",
        "facility_authority_result": _semantic_result(
            task_id="task:facility",
            event_id="event:123",
            decision=ResolutionDecision.ACCEPTED,
            model_calls=(facility_call,),
            tool_traces=(facility_trace,),
        ),
        "terminology_authority_result": _semantic_result(
            task_id="task:terminology",
            event_id="event:123",
            decision=ResolutionDecision.INSUFFICIENT,
        ),
    }

    records = build_agent_usage_records(source_id="2026-05-19:123", state=state)

    assert len(records) == 2
    facility, terminology = records
    assert facility.model_dump() == {
        "source_id": "2026-05-19:123",
        "event_id": "event:123",
        "task_id": "task:facility",
        "role": "semantic_resolution",
        "task_scope": "facility",
        "execution_mode": "activated",
        "outcome": "accepted",
        "detail_status": "accepted",
        "activation_reason": "multiple_eligible_authority_candidates",
        "provider_call_count": 1,
        "tool_call_count": 1,
        "input_tokens": 120,
        "output_tokens": 18,
        "provider_latency_ms": 31.5,
        "tool_latency_ms": 4.25,
    }
    assert terminology.execution_mode == "deterministic_bypass"
    assert terminology.outcome == "abstained"
    assert terminology.provider_call_count == 0
    assert terminology.tool_call_count == 0


def test_final_corpus_event_id_applies_to_both_resolution_usage_records() -> None:
    state = {
        "event_uri": "event:final-corpus-id",
        "resolution_event_id": "event:resolution-only",
        "facility_authority_result": _semantic_result(
            task_id="task:facility",
            event_id="event:resolution-only",
            decision=ResolutionDecision.ACCEPTED,
        ),
        "terminology_authority_result": _semantic_result(
            task_id="task:terminology",
            event_id="event:resolution-only",
            decision=ResolutionDecision.ACCEPTED,
        ),
    }

    records = build_agent_usage_records(source_id="source:final", state=state)

    assert {row.event_id for row in records} == {"event:final-corpus-id"}
    assert [row.task_id for row in records] == [
        "task:facility",
        "task:terminology",
    ]


def test_sidecar_is_corpus_bound_but_excludes_raw_model_and_tool_payloads(
    tmp_path: Path,
) -> None:
    record = AgentUsageRecord(
        source_id="source:1",
        event_id="event:1",
        task_id="task:1",
        role="semantic_resolution",
        task_scope="facility",
        execution_mode="activated",
        outcome="accepted",
        detail_status="accepted",
        activation_reason="multiple_eligible_authority_candidates",
        provider_call_count=1,
        tool_call_count=1,
        input_tokens=10,
        output_tokens=2,
        provider_latency_ms=7.5,
        tool_latency_ms=1.5,
    )

    manifest = write_agent_usage_sidecar(
        tmp_path,
        corpus_id="corpus:stable",
        records=(record,),
    )

    sidecar = tmp_path / "agent_usage"
    payload = (sidecar / "agent_usage.jsonl").read_text(encoding="utf-8")
    persisted = json.loads(payload)
    assert manifest.corpus_id == "corpus:stable"
    assert manifest.record_count == 1
    assert manifest.totals.activated_count == 1
    assert manifest.totals.provider_call_count == 1
    assert manifest.totals.tool_call_count == 1
    for forbidden in (
        "raw_response",
        "prompt",
        "arguments",
        "parameters",
        "result_refs",
        "reasoning",
    ):
        assert forbidden not in persisted


def test_latency_changes_only_the_sidecar_checksum(tmp_path: Path) -> None:
    base = {
        "source_id": "source:1",
        "event_id": "event:1",
        "task_id": "task:1",
        "role": "semantic_resolution",
        "task_scope": "facility",
        "execution_mode": "activated",
        "outcome": "accepted",
        "detail_status": "accepted",
        "activation_reason": "multiple_eligible_authority_candidates",
        "provider_call_count": 1,
        "tool_call_count": 0,
        "input_tokens": 10,
        "output_tokens": 2,
        "tool_latency_ms": 0.0,
    }
    first = write_agent_usage_sidecar(
        tmp_path,
        corpus_id="corpus:unchanged",
        records=(AgentUsageRecord(**base, provider_latency_ms=5.0),),
    )
    second = write_agent_usage_sidecar(
        tmp_path,
        corpus_id="corpus:unchanged",
        records=(AgentUsageRecord(**base, provider_latency_ms=8.0),),
    )

    assert first.corpus_id == second.corpus_id == "corpus:unchanged"
    assert first.artifact_sha256 != second.artifact_sha256
