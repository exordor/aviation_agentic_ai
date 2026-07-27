"""Load-bearing Batch A tests for frozen runtime and resolution bindings."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import aviation_agentic_ai.agent_system.agents as agents_module
from aviation_agentic_ai.agent_system.agents import (
    FacilityCandidates,
    TermCandidates,
    _resolve_facility_compatibility,
    _resolve_terminology_compatibility,
    run_facility_agent,
)
from aviation_agentic_ai.agent_system.authority_evidence import (
    AuthorityBuildStatus,
    build_facility_resolution_candidate,
    build_term_resolution_candidate,
)
from aviation_agentic_ai.agent_system.contracts import (
    AgentResult,
    AgentStatus,
    AgentTask,
    EvidenceCard,
    EvidenceClaim,
    ModelCallRecord,
    SourceFamily,
    SourceRecord,
)
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    ResolutionDecision,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.runtime import (
    create_run_binding,
    write_run_manifest,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.workflow import IngestContext, run_ingest
import aviation_agentic_ai.agent_system.workflow as workflow_module
from test_agent_system_authority_evidence import (
    SCHEMA_PATH,
    _catalog,
    _facility,
    _term,
)


STARTED = datetime(2026, 5, 19, 20, 30, 45, 123000, tzinfo=UTC)
TOOL_VERSION = "resolution-compatibility-v1"
EVENT_MENTION = "GS"


def _task(domain: str, *, run_id: str = "run:test") -> AgentTask:
    tools = (
        ["lookup_nasr_facility", "lookup_artcc", "resolve_facility_alias"]
        if domain == "facility"
        else [
            "lookup_faa_glossary",
            "lookup_pcg_term",
            "resolve_term_registry",
            "resolve_schema_event_class",
        ]
    )
    return AgentTask(
        run_id=run_id,
        source_id="2026-05-19:123",
        objective=f"resolve {domain}",
        allowed_tools=tools,
    )


def _facility_envelope(tmp_path: Path) -> FacilityCandidates:
    catalog = _catalog(tmp_path)
    guide = load_schema_guide(str(SCHEMA_PATH))
    entity = _facility(catalog, "KJFK")
    built = build_facility_resolution_candidate(
        entity,
        structural_slot="controlled_nas_element",
        expected_entity_type="airport",
        catalog=catalog.facility,
        authority_snapshots=catalog.snapshots,
        guide=guide,
    )
    return FacilityCandidates(
        mention="JFK",
        candidates=[entity],
        source_id="2026-05-19:123",
        structural_slot="controlled_nas_element",
        expected_entity_type="airport",
        advisory_evidence="CTL ELEMENT: JFK",
        resolution_event_id=stable_contract_id(
            "resolution-event",
            "run:test",
            "2026-05-19:123",
            EVENT_MENTION,
        ),
        resolution_event_mention=EVENT_MENTION,
        run_started_at=STARTED,
        schema_slice_id=guide.schema_slice_id,
        schema_snapshot_sha256=guide.checksum,
        resolution_tool_version=TOOL_VERSION,
        authority_domain_status=AuthorityBuildStatus.OK,
        authority_candidate_results=(built,),
    )


def _gs_envelope(tmp_path: Path) -> TermCandidates:
    catalog = _catalog(tmp_path)
    guide = load_schema_guide(str(SCHEMA_PATH))
    terms = [_term(catalog, "Ground Stop"), _term(catalog, "Glide Slope")]
    built = tuple(
        build_term_resolution_candidate(
            term,
            structural_slot="traffic_management_initiative_type",
            expected_entity_type="traffic_management_initiative",
            catalog=catalog.terminology,
            authority_snapshots=catalog.snapshots,
            guide=guide,
        )
        for term in terms
    )
    return TermCandidates(
        mention="GS",
        candidates=terms,
        source_id="2026-05-19:123",
        guide=guide,
        structural_slot="traffic_management_initiative_type",
        expected_entity_type="traffic_management_initiative",
        advisory_evidence="GROUND STOP",
        resolution_event_id=stable_contract_id(
            "resolution-event",
            "run:test",
            "2026-05-19:123",
            EVENT_MENTION,
        ),
        resolution_event_mention=EVENT_MENTION,
        run_started_at=STARTED,
        schema_slice_id=guide.schema_slice_id,
        schema_snapshot_sha256=guide.checksum,
        resolution_tool_version=TOOL_VERSION,
        authority_domain_status=AuthorityBuildStatus.OK,
        authority_candidate_results=built,
    )


def test_run_binding_samples_one_utc_timestamp(tmp_path):
    local = STARTED.astimezone(UTC) + timedelta(0)
    binding = create_run_binding(tmp_path, "2026-05-19:123", started_at=local)

    assert binding.run_started_at == STARTED
    assert binding.run_id == binding.run_dir.name
    assert "20260519T203045123Z" in binding.run_id


def test_manifest_created_at_uses_frozen_run_started_at(tmp_path):
    path = write_run_manifest(
        run_dir=tmp_path,
        source_id="2026-05-19:123",
        model_calls=[],
        materialization=None,
        schema_slice_id="slice:test",
        schema_checksum="a" * 64,
        evidence_cards=[],
        graph_patch_raw=None,
        prompt_set_id="prompt:test",
        profile_gap_count=0,
        created_at=STARTED,
    )

    assert json.loads(path.read_text())["created_at"] == STARTED.isoformat()


def test_internal_helpers_return_typed_unique_resolution_without_authority_leak(
    tmp_path,
):
    facility = _resolve_facility_compatibility(
        task=_task("facility"),
        candidates=_facility_envelope(tmp_path),
    )
    terminology = _resolve_terminology_compatibility(
        task=_task("terminology"),
        candidates=_gs_envelope(tmp_path),
    )

    for result in (facility, terminology):
        assert isinstance(result.agent_result, AgentResult)
        assert result.agent_result.status is AgentStatus.RESOLVED
        assert result.domain_outcome.decision is ResolutionDecision.ACCEPTED
        assert result.authority_source_records
        assert all(
            claim.source_id == "2026-05-19:123"
            for claim in result.agent_result.evidence_card.claims
        )
        decision_basis = result.agent_result.evidence_card.decision_basis
        assert "resolution_task_id=" in decision_basis
        assert "authority-source" not in decision_basis
        assert all(
            "authority-source" not in ref
            for trace in result.agent_result.evidence_card.tool_trace
            for ref in trace.result_refs
        )

    assert terminology.agent_result.evidence_card.canonical_refs == [
        _term(_catalog(tmp_path), "Ground Stop").term_id
    ]


def test_resolution_contracts_share_frozen_run_started_at(tmp_path, monkeypatch):
    sealed = []
    real_task_sealer = agents_module.seal_resolution_task
    real_proposal_sealer = agents_module.seal_resolution_proposal

    def capture_task(**kwargs):
        result = real_task_sealer(**kwargs)
        sealed.append(result)
        return result

    def capture_proposal(**kwargs):
        result = real_proposal_sealer(**kwargs)
        sealed.append(result)
        return result

    monkeypatch.setattr(agents_module, "seal_resolution_task", capture_task)
    monkeypatch.setattr(agents_module, "seal_resolution_proposal", capture_proposal)

    _resolve_facility_compatibility(
        task=_task("facility"),
        candidates=_facility_envelope(tmp_path),
    )

    assert [contract.created_at for contract in sealed] == [STARTED, STARTED]


def test_exact_candidate_set_mismatch_is_blocked(tmp_path):
    envelope = _facility_envelope(tmp_path)
    blocked = _resolve_facility_compatibility(
        task=_task("facility"),
        candidates=replace(envelope, authority_candidate_results=()),
    )

    assert blocked.agent_result.status is AgentStatus.BLOCKED
    assert blocked.domain_outcome.decision is ResolutionDecision.BLOCKED


def test_explicit_insufficient_authority_is_terminal_before_candidate_audit(
    tmp_path,
):
    result = _resolve_facility_compatibility(
        task=_task("facility"),
        candidates=replace(
            _facility_envelope(tmp_path),
            authority_domain_status=AuthorityBuildStatus.INSUFFICIENT,
            authority_domain_reason_code="FACILITY_AUTHORITY_INCOMPLETE",
            authority_candidate_results=(),
        ),
    )

    assert result.agent_result.status is AgentStatus.ABSTAIN
    assert result.domain_outcome.decision is ResolutionDecision.INSUFFICIENT
    assert (
        result.domain_outcome.limitation_code
        == "FACILITY_AUTHORITY_INCOMPLETE"
    )
    assert result.authority_source_records == ()


def test_resolution_event_binding_is_recomputed_before_sealing(tmp_path):
    result = _resolve_facility_compatibility(
        task=_task("facility"),
        candidates=replace(
            _facility_envelope(tmp_path),
            resolution_event_id=stable_contract_id(
                "resolution-event",
                "run:test",
                "2026-05-19:123",
                "GDP",
            ),
        ),
    )

    assert result.agent_result.status is AgentStatus.BLOCKED
    assert result.domain_outcome.decision is ResolutionDecision.BLOCKED


def test_authority_source_records_are_checksum_and_family_bound(tmp_path):
    envelope = _facility_envelope(tmp_path)
    built = envelope.authority_candidate_results[0]
    record = built.source_record
    assert record is not None
    corrupt_records = (
        record.model_copy(update={"family": SourceFamily.FAA_TERM}),
        record.model_copy(update={"source_id": "authority-source:wrong"}),
        record.model_copy(update={"content": f"{record.content}\ncorrupt"}),
    )

    for corrupt_record in corrupt_records:
        result = _resolve_facility_compatibility(
            task=_task("facility"),
            candidates=replace(
                envelope,
                authority_candidate_results=(
                    replace(built, source_record=corrupt_record),
                ),
            ),
        )

        assert result.agent_result.status is AgentStatus.BLOCKED
        assert result.domain_outcome.decision is ResolutionDecision.BLOCKED
        assert result.authority_source_records == ()


def test_corrupt_schema_binding_fails_closed_as_blocked(tmp_path):
    result = _resolve_facility_compatibility(
        task=_task("facility"),
        candidates=replace(
            _facility_envelope(tmp_path),
            schema_snapshot_sha256="b" * 64,
        ),
    )

    assert result.agent_result.status is AgentStatus.BLOCKED
    assert result.domain_outcome.decision is ResolutionDecision.BLOCKED


def test_multiple_eligible_candidates_defer_without_resolution_provider(tmp_path):
    catalog = _catalog(tmp_path)
    guide = load_schema_guide(str(SCHEMA_PATH))
    entities = [_facility(catalog, "KJFK"), _facility(catalog, "KEWR")]
    built = tuple(
        build_facility_resolution_candidate(
            entity,
            structural_slot="controlled_nas_element",
            expected_entity_type="airport",
            catalog=catalog.facility,
            authority_snapshots=catalog.snapshots,
            guide=guide,
        )
        for entity in entities
    )
    envelope = replace(
        _facility_envelope(tmp_path),
        candidates=entities,
        authority_candidate_results=built,
    )

    result = _resolve_facility_compatibility(
        task=_task("facility"),
        candidates=envelope,
    )

    assert result.agent_result.status is AgentStatus.ABSTAIN
    assert result.domain_outcome.decision is ResolutionDecision.ABSTAINED
    assert (
        result.domain_outcome.limitation_code
        == "MODEL_MEDIATED_RESOLUTION_DEFERRED_BATCH_B"
    )


def test_legacy_ambiguous_facility_never_invokes_resolution_provider():
    @dataclass
    class Entity:
        entity_id: str
        preferred_label: str

    provider_calls = []
    result = run_facility_agent(
        task=_task("facility"),
        candidates=FacilityCandidates(
            mention="JFK",
            candidates=[Entity("facility:a", "A"), Entity("facility:b", "B")],
            source_id="2026-05-19:123",
            structural_slot="controlled_nas_element",
            expected_entity_type="airport",
            advisory_evidence="CTL ELEMENT: JFK",
        ),
        model_invoker=lambda *args: (
            provider_calls.append(args)
            or ModelCallRecord(agent="facility", raw_response="facility:a")
        ),
    )

    assert result.status is AgentStatus.ABSTAIN
    assert provider_calls == []


def test_required_blocked_domain_stops_kg_factory_and_preserves_blocked_status(
    tmp_path,
):
    catalog = _catalog(tmp_path)
    blocked_facility = replace(
        catalog.facility,
        status=AuthorityBuildStatus.BLOCKED,
        entities=(),
        records=(),
        reason_code="FACILITY_AUTHORITY_BLOCKED",
        error_id="error:facility-authority",
    )
    authority_catalog = replace(catalog, facility=blocked_facility)
    calls: list[str] = []
    advisory = SourceRecord(
        source_id="2026-05-19:123",
        family=SourceFamily.ATCSCC_ADVISORY,
        content=(
            "ADVZY 123 JFK 05/19/2026\n"
            "CTL ELEMENT: JFK\n"
            "ELEMENT TYPE: APT\n"
            "GROUND STOP\n"
            "GROUND STOP PERIOD: 19/2100Z - 19/2245Z\n"
            "SIGNATURE:\n26/05/19 20:30\n"
        ),
    )

    state = run_ingest(
        IngestContext(
            advisory=advisory,
            facility_candidates=list(catalog.facility.entities),
            term_candidates=list(catalog.terminology.registry_terms),
            authority_catalog=authority_catalog,
            guide=load_schema_guide(str(SCHEMA_PATH)),
            run_id="run:test",
            run_started_at=STARTED,
            output_dir=str(tmp_path / "run"),
            model_invoker_factory=lambda: calls.append("resolution") or None,
            kg_tool_model_factory=lambda tools: calls.append("kg") or None,
        )
    )

    assert calls == []
    assert state["resolution_preflight_status"] == "blocked"
    assert state["kg_result"].status is AgentStatus.BLOCKED
    assert state["formal_layers"]["decision"]["status"] == "blocked"


def test_required_insufficient_domain_stops_kg_and_resolution_factories(tmp_path):
    catalog = _catalog(tmp_path)
    incomplete_terms = replace(catalog.terminology, definitions=())
    authority_catalog = replace(catalog, terminology=incomplete_terms)
    calls: list[str] = []
    advisory = SourceRecord(
        source_id="2026-05-19:123",
        family=SourceFamily.ATCSCC_ADVISORY,
        content=(
            "ADVZY 123 JFK 05/19/2026\n"
            "CTL ELEMENT: JFK\n"
            "ELEMENT TYPE: APT\n"
            "GROUND STOP\n"
            "GROUND STOP PERIOD: 19/2100Z - 19/2245Z\n"
        ),
    )

    state = run_ingest(
        IngestContext(
            advisory=advisory,
            authority_catalog=authority_catalog,
            guide=load_schema_guide(str(SCHEMA_PATH)),
            run_id="run:test",
            run_started_at=STARTED,
            output_dir=str(tmp_path / "insufficient"),
            model_invoker_factory=lambda: calls.append("resolution") or None,
            kg_tool_model_factory=lambda tools: calls.append("kg") or None,
        )
    )

    assert calls == []
    assert state["resolution_preflight_status"] == "insufficient"
    assert state["kg_result"].status is AgentStatus.ABSTAIN
    assert state["formal_layers"]["decision"]["status"] == "insufficient"


def test_event_class_hint_mismatch_blocks_before_kg_factory(tmp_path, monkeypatch):
    calls = []
    guide = load_schema_guide(str(SCHEMA_PATH))
    advisory = SourceRecord(
        source_id="2026-05-19:138",
        family=SourceFamily.ATCSCC_ADVISORY,
        content="GROUND DELAY PROGRAM",
    )
    monkeypatch.setattr(
        workflow_module,
        "_CTX_HOLDER",
        IngestContext(
            advisory=advisory,
            guide=guide,
            run_id="run:test",
            output_dir=str(tmp_path),
            kg_tool_model_factory=lambda tools: calls.append("kg") or None,
        ),
    )
    advisory_card = EvidenceCard(
        agent_role="advisory",
        status=AgentStatus.RESOLVED,
    )
    facility_card = EvidenceCard(
        agent_role="facility",
        status=AgentStatus.RESOLVED,
    )
    terminology_card = EvidenceCard(
        agent_role="terminology",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="operational_term",
                value="term:gdp",
                ontology_target="atm:GroundDelayProgramTMI",
                evidence_text="GROUND DELAY PROGRAM",
                source_id=advisory.source_id,
            )
        ],
    )

    result = workflow_module._kg_construction_node(
        {
            "resolution_preflight_status": "resolved",
            "advisory_result": AgentResult(
                status=AgentStatus.RESOLVED,
                evidence_card=advisory_card,
            ),
            "facility_result": AgentResult(
                status=AgentStatus.RESOLVED,
                evidence_card=facility_card,
            ),
            "terminology_result": AgentResult(
                status=AgentStatus.RESOLVED,
                evidence_card=terminology_card,
            ),
            "event_class_hint": "atm:GroundStopTMI",
            "formal_event_uri_hint": "",
        }
    )

    assert result["kg_result"].status is AgentStatus.BLOCKED
    assert calls == []

    context_result = workflow_module._decision_context_node(
        {
            "resolution_preflight_status": "resolved",
            **result,
        }
    )

    assert context_result["formal_layers"]["decision"]["status"] == "blocked"
