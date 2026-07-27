"""Behavior coverage for the current authority-service architecture."""

from __future__ import annotations

from aviation_agentic_ai.agent_system.authority_resolution import (
    AuthorityResolutionResult,
    resolve_facility_authority,
    resolve_terminology_authority,
)
from aviation_agentic_ai.agent_system.contracts import AgentStatus, SourceFamily, SourceRecord
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.workflow import IngestContext, run_ingest
from test_agent_system_runtime_binding import (
    STARTED,
    _catalog,
    _facility_envelope,
    _gs_envelope,
    _task,
)


class FailingFactory:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, tools):
        del tools
        self.calls += 1
        raise AssertionError("unique authority resolution constructed a semantic model")


def test_unique_authority_candidates_resolve_without_semantic_model(tmp_path) -> None:
    """Catches model construction on deterministic, source-bound candidates."""

    factory = FailingFactory()
    facility = resolve_facility_authority(
        task=_task("facility"),
        request=_facility_envelope(tmp_path),
        semantic_resolution_tool_model_factory=factory,
    )
    terminology = resolve_terminology_authority(
        task=_task("terminology"),
        request=_gs_envelope(tmp_path),
        semantic_resolution_tool_model_factory=factory,
    )

    assert facility.evidence_card.status is AgentStatus.RESOLVED
    assert terminology.evidence_card.status is AgentStatus.RESOLVED
    assert facility.authority_source_records
    assert terminology.authority_source_records
    assert facility.model_calls == terminology.model_calls == ()
    assert factory.calls == 0


def test_ingest_returns_direct_authority_results_without_split_bridge(tmp_path) -> None:
    """Catches workflow state that reconstructs the removed result envelope."""

    catalog = _catalog(tmp_path)
    advisory = SourceRecord(
        source_id="2026-05-19:123",
        family=SourceFamily.ATCSCC_ADVISORY,
        content=(
            "ADVZY 123 JFK 05/19/2026\nCTL ELEMENT: JFK\nELEMENT TYPE: APT\n"
            "GROUND STOP\nGROUND STOP PERIOD: 19/2100Z - 19/2245Z\n"
            "SIGNATURE:\n26/05/19 20:30\n"
        ),
    )
    state = run_ingest(
        IngestContext(
            advisory=advisory,
            authority_catalog=catalog,
            guide=load_schema_guide(),
            run_id="run:test",
            run_started_at=STARTED,
            output_dir=str(tmp_path / "run"),
        )
    )

    assert isinstance(state["facility_authority_result"], AuthorityResolutionResult)
    assert isinstance(state["terminology_authority_result"], AuthorityResolutionResult)
    assert (
        not {
            "facility_result",
            "terminology_result",
            "facility_resolution_outcome",
            "terminology_resolution_outcome",
            "facility_resolution_task",
            "terminology_resolution_task",
            "facility_resolution_proposal",
            "terminology_resolution_proposal",
        }
        & state.keys()
    )
