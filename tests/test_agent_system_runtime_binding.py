"""Load-bearing Batch A tests for frozen runtime and resolution bindings."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import aviation_agentic_ai.agent_system.authority_resolution as authority_module
from langchain_core.messages import AIMessage
from aviation_agentic_ai.agent_system.authority_resolution import (
    FacilityAuthorityResolutionInput,
    TerminologyAuthorityResolutionInput,
    resolve_facility_authority,
    resolve_terminology_authority,
)
from aviation_agentic_ai.agent_system.authority_evidence import (
    AuthorityBuildStatus,
    build_facility_resolution_candidate,
    build_term_resolution_candidate,
)
from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    AgentTask,
    EvidenceCard,
    EvidenceClaim,
    GraphPatchBlock,
    GraphPatchLine,
    GraphValidationResult,
    ModelCallRecord,
    ModelToolCall,
    SourceFamily,
    SourceRecord,
)
from aviation_agentic_ai.agent_system.construction_contracts import (
    ConstraintCheckStatus,
    ResolutionDecision,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.runtime import (
    create_run_binding,
    write_run_manifest,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
from aviation_agentic_ai.agent_system.workflow import IngestContext, run_ingest
import aviation_agentic_ai.agent_system.workflow as workflow_module
from test_agent_system_authority_evidence import (
    SCHEMA_PATH,
    _catalog,
    _facility,
    _term,
    _test_inputs,
)


STARTED = datetime(2026, 5, 19, 20, 30, 45, 123000, tzinfo=UTC)
TOOL_VERSION = "authority-resolution-v1"
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


def _facility_envelope(tmp_path: Path) -> FacilityAuthorityResolutionInput:
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
    return FacilityAuthorityResolutionInput(
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


def _gs_envelope(tmp_path: Path) -> TerminologyAuthorityResolutionInput:
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
    return TerminologyAuthorityResolutionInput(
        mention="GS",
        candidates=terms,
        source_id="2026-05-19:123",
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


def _ambiguous_facility_envelope(tmp_path: Path) -> FacilityAuthorityResolutionInput:
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
    return replace(
        _facility_envelope(tmp_path),
        candidates=entities,
        authority_candidate_results=built,
    )


def _ambiguous_term_envelope(tmp_path: Path) -> TerminologyAuthorityResolutionInput:
    envelope = _gs_envelope(tmp_path)
    mapped = next(
        row.candidate
        for row in envelope.authority_candidate_results
        if row.candidate is not None and row.candidate.ontology_class_iri
    )
    built = []
    for row in envelope.authority_candidate_results:
        assert row.candidate is not None
        checks = tuple(
            check.model_copy(update={"status": ConstraintCheckStatus.PASS})
            for check in row.candidate.constraint_checks
        )
        built.append(
            replace(
                row,
                candidate=row.candidate.model_copy(
                    update={
                        "constraint_checks": checks,
                        "ontology_class_prefixed": mapped.ontology_class_prefixed,
                        "ontology_class_iri": mapped.ontology_class_iri,
                    }
                ),
            )
        )
    return replace(envelope, authority_candidate_results=tuple(built))


class _ScriptedResolutionModel:
    def __init__(
        self,
        *,
        candidate_ids: list[str],
        selected_candidate_id: str | None,
    ) -> None:
        self.candidate_ids = sorted(candidate_ids)
        self.selected_candidate_id = selected_candidate_id
        self.invocations: list[str] = []

    def invoke(self, messages, *, phase):
        del messages
        self.invocations.append(phase)
        if phase == "select_tool":
            name = (
                "get_authority_record"
                if self.selected_candidate_id is not None
                else "get_resolution_candidates"
            )
            arguments = (
                {"candidate_id": self.selected_candidate_id}
                if self.selected_candidate_id is not None
                else {}
            )
            call = {
                "id": "call:resolution",
                "name": name,
                "args": arguments,
            }
            return ToolModelTurn(
                message=AIMessage(content="", tool_calls=[call]),
                record=ModelCallRecord(
                    agent="semantic_resolution",
                    raw_response="",
                    attempt=1,
                    tool_calls=[
                        ModelToolCall(
                            call_id=call["id"],
                            name=name,
                            arguments=arguments,
                        )
                    ],
                ),
            )
        rejected = [
            candidate_id
            for candidate_id in self.candidate_ids
            if candidate_id != self.selected_candidate_id
        ]
        payload = json.dumps(
            {
                "decision": ("accepted" if self.selected_candidate_id is not None else "abstained"),
                "selected_candidate_id": self.selected_candidate_id,
                "rejected_candidate_ids": rejected,
                "limitation": (
                    None
                    if self.selected_candidate_id is not None
                    else "Authority evidence remains ambiguous."
                ),
            },
            separators=(",", ":"),
        )
        return ToolModelTurn(
            message=AIMessage(content=payload),
            record=ModelCallRecord(
                agent="semantic_resolution",
                raw_response=payload,
                attempt=2,
            ),
        )


def test_run_binding_samples_one_utc_timestamp(tmp_path):
    local = STARTED.astimezone(UTC) + timedelta(0)
    binding = create_run_binding(tmp_path, "2026-05-19:123", started_at=local)

    assert binding.run_started_at == STARTED
    assert binding.run_id == binding.run_dir.name
    assert "20260519T203045123Z" in binding.run_id


def test_manifest_created_at_uses_frozen_run_started_at(tmp_path):
    failed_call = ModelCallRecord(
        agent="query",
        raw_response="",
        attempt=1,
        error="provider unavailable",
    )
    path = write_run_manifest(
        run_dir=tmp_path,
        source_id="2026-05-19:123",
        model_calls=[failed_call],
        materialization=None,
        schema_slice_id="slice:test",
        schema_checksum="a" * 64,
        evidence_cards=[],
        graph_patch_raw=None,
        prompt_set_id="prompt:test",
        profile_gap_count=0,
        created_at=STARTED,
    )

    payload = json.loads(path.read_text())
    assert payload["created_at"] == STARTED.isoformat()
    assert payload["manifest_version"] == "tmi-event-run-v1"
    assert payload["provider_attempts"] == 1
    assert payload["provider_successes"] == 0


def test_internal_helpers_return_typed_unique_resolution_without_authority_leak(
    tmp_path,
):
    factory_calls = []

    def forbidden_factory(tools):
        factory_calls.append(tools)
        raise AssertionError("unique resolution constructed semantic model")

    facility = resolve_facility_authority(
        task=_task("facility"),
        request=_facility_envelope(tmp_path),
        semantic_resolution_tool_model_factory=forbidden_factory,
    )
    terminology = resolve_terminology_authority(
        task=_task("terminology"),
        request=_gs_envelope(tmp_path),
        semantic_resolution_tool_model_factory=forbidden_factory,
    )

    for result in (facility, terminology):
        assert result.domain_outcome.decision is ResolutionDecision.ACCEPTED
        assert result.authority_source_records
        assert all(claim.source_id == "2026-05-19:123" for claim in result.evidence_card.claims)
        decision_basis = result.evidence_card.decision_basis
        assert "resolution_task_id=" in decision_basis
        assert "authority-source" not in decision_basis
        assert all(
            "authority-source" not in ref
            for trace in result.evidence_card.tool_trace
            for ref in trace.result_refs
        )

    assert terminology.evidence_card.canonical_refs == [
        _term(_catalog(tmp_path), "Ground Stop").term_id
    ]
    assert {
        json.loads(record.content)["preferred_label"]
        for record in terminology.authority_source_records
    } == {"Ground Stop", "Glide Slope"}
    assert factory_calls == []


def test_resolution_contracts_share_frozen_run_started_at(tmp_path, monkeypatch):
    sealed = []
    real_task_sealer = authority_module.seal_resolution_task
    real_proposal_sealer = authority_module.seal_resolution_proposal

    def capture_task(**kwargs):
        result = real_task_sealer(**kwargs)
        sealed.append(result)
        return result

    def capture_proposal(**kwargs):
        result = real_proposal_sealer(**kwargs)
        sealed.append(result)
        return result

    monkeypatch.setattr(authority_module, "seal_resolution_task", capture_task)
    monkeypatch.setattr(authority_module, "seal_resolution_proposal", capture_proposal)

    resolve_facility_authority(
        task=_task("facility"),
        request=_facility_envelope(tmp_path),
    )

    assert [contract.created_at for contract in sealed] == [STARTED, STARTED]


def test_exact_candidate_set_mismatch_is_blocked(tmp_path):
    factory_calls = []
    envelope = _facility_envelope(tmp_path)
    blocked = resolve_facility_authority(
        task=_task("facility"),
        request=replace(envelope, authority_candidate_results=()),
        semantic_resolution_tool_model_factory=lambda tools: factory_calls.append(tools),
    )

    assert blocked.evidence_card.status is AgentStatus.BLOCKED
    assert blocked.domain_outcome.decision is ResolutionDecision.BLOCKED
    assert factory_calls == []


def test_explicit_insufficient_authority_is_terminal_before_candidate_audit(
    tmp_path,
):
    factory_calls = []
    result = resolve_facility_authority(
        task=_task("facility"),
        request=replace(
            _facility_envelope(tmp_path),
            authority_domain_status=AuthorityBuildStatus.INSUFFICIENT,
            authority_domain_reason_code="FACILITY_AUTHORITY_INCOMPLETE",
            authority_candidate_results=(),
        ),
        semantic_resolution_tool_model_factory=lambda tools: factory_calls.append(tools),
    )

    assert result.evidence_card.status is AgentStatus.ABSTAIN
    assert result.domain_outcome.decision is ResolutionDecision.INSUFFICIENT
    assert result.domain_outcome.limitation_code == "FACILITY_AUTHORITY_INCOMPLETE"
    assert result.authority_source_records == ()
    assert factory_calls == []


def test_zero_eligible_candidates_are_insufficient_without_model_construction(
    tmp_path,
):
    envelope = _facility_envelope(tmp_path)
    built = envelope.authority_candidate_results[0]
    assert built.candidate is not None
    ineligible = built.candidate.model_copy(
        update={
            "constraint_checks": tuple(
                check.model_copy(update={"status": ConstraintCheckStatus.FAIL})
                for check in built.candidate.constraint_checks
            )
        }
    )
    factory_calls = []

    result = resolve_facility_authority(
        task=_task("facility"),
        request=replace(
            envelope,
            authority_candidate_results=(replace(built, candidate=ineligible),),
        ),
        semantic_resolution_tool_model_factory=lambda tools: factory_calls.append(tools),
    )

    assert result.evidence_card.status is AgentStatus.ABSTAIN
    assert result.domain_outcome.decision is ResolutionDecision.INSUFFICIENT
    assert result.domain_outcome.limitation_code == "NO_ELIGIBLE_AUTHORITY_CANDIDATE"
    assert factory_calls == []


def test_resolution_event_binding_is_recomputed_before_sealing(tmp_path):
    result = resolve_facility_authority(
        task=_task("facility"),
        request=replace(
            _facility_envelope(tmp_path),
            resolution_event_id=stable_contract_id(
                "resolution-event",
                "run:test",
                "2026-05-19:123",
                "GDP",
            ),
        ),
    )

    assert result.evidence_card.status is AgentStatus.BLOCKED
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
        result = resolve_facility_authority(
            task=_task("facility"),
            request=replace(
                envelope,
                authority_candidate_results=(replace(built, source_record=corrupt_record),),
            ),
        )

        assert result.evidence_card.status is AgentStatus.BLOCKED
        assert result.domain_outcome.decision is ResolutionDecision.BLOCKED
        assert result.authority_source_records == ()


def test_corrupt_schema_binding_fails_closed_as_blocked(tmp_path):
    result = resolve_facility_authority(
        task=_task("facility"),
        request=replace(
            _facility_envelope(tmp_path),
            schema_snapshot_sha256="b" * 64,
        ),
    )

    assert result.evidence_card.status is AgentStatus.BLOCKED
    assert result.domain_outcome.decision is ResolutionDecision.BLOCKED


def test_multiple_facility_candidates_use_the_shared_semantic_runtime(tmp_path):
    envelope = _ambiguous_facility_envelope(tmp_path)
    candidate_ids = [row.candidate_id for row in envelope.authority_candidate_results]
    selected_candidate_id = next(
        candidate_id for candidate_id in candidate_ids if candidate_id.endswith(":KJFK")
    )
    model = _ScriptedResolutionModel(
        candidate_ids=candidate_ids,
        selected_candidate_id=selected_candidate_id,
    )
    result = resolve_facility_authority(
        task=_task("facility"),
        request=envelope,
        semantic_resolution_tool_model_factory=lambda tools: model,
    )

    assert result.evidence_card.status is AgentStatus.RESOLVED
    assert result.domain_outcome.decision is ResolutionDecision.ACCEPTED
    assert result.evidence_card.canonical_refs == [selected_candidate_id]
    assert len(result.model_calls) == 2
    assert model.invocations == ["select_tool", "final_answer"]
    assert result.resolution_task.remaining_tool_budget == 3
    assert result.resolution_task.decision is None
    assert not set(candidate_ids) & set(result.resolution_task.rejected_candidate_ids)
    assert result.resolution_proposal.selected_candidate_id == selected_candidate_id
    assert result.resolution_tool_traces
    assert all(claim.source_id == envelope.source_id for claim in result.evidence_card.claims)


def test_multiple_term_candidates_can_abstain_through_the_same_runtime(tmp_path):
    envelope = _ambiguous_term_envelope(tmp_path)
    candidate_ids = [row.candidate_id for row in envelope.authority_candidate_results]
    model = _ScriptedResolutionModel(
        candidate_ids=candidate_ids,
        selected_candidate_id=None,
    )

    result = resolve_terminology_authority(
        task=_task("terminology"),
        request=envelope,
        semantic_resolution_tool_model_factory=lambda tools: model,
    )

    assert result.evidence_card.status is AgentStatus.ABSTAIN
    assert result.domain_outcome.decision is ResolutionDecision.ABSTAINED
    assert result.resolution_proposal.selected_candidate_id is None
    assert len(result.model_calls) == 2
    assert model.invocations == ["select_tool", "final_answer"]


def test_semantic_resolution_factory_failure_is_a_sealed_blocked_result(tmp_path):
    envelope = _ambiguous_facility_envelope(tmp_path)
    calls = []

    def failing_factory(tools):
        calls.append(tools)
        raise RuntimeError("scripted setup failure")

    result = resolve_facility_authority(
        task=_task("facility"),
        request=envelope,
        semantic_resolution_tool_model_factory=failing_factory,
    )

    assert len(calls) == 1
    assert result.evidence_card.status is AgentStatus.BLOCKED
    assert result.domain_outcome.decision is ResolutionDecision.BLOCKED
    assert result.domain_outcome.error_id
    assert result.resolution_task.candidates
    assert result.resolution_proposal.task_id == result.resolution_task.task_id


def test_required_blocked_domain_stops_assembly_and_preserves_blocked_status(
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
            semantic_resolution_tool_model_factory=lambda tools: (
                calls.append("semantic-resolution") or None
            ),
        )
    )

    assert calls == []
    assert state["resolution_preflight_status"] == "blocked"
    assert state["integration_graph_patch"] is None
    assert state["formal_layers"]["decision"]["status"] == "blocked"


def test_ingest_context_has_no_event_evidence_integration_model_factory() -> None:
    """Event evidence integration is a deterministic service, not a model role."""

    assert "event_evidence_integration_model_factory" not in IngestContext.__dataclass_fields__


def test_missing_ground_stop_extension_is_insufficient_and_unpublished(tmp_path):
    """A Ground Stop without its required extension field cannot publish."""

    from aviation_agentic_ai.agent_system.construction_contracts import EventEvidenceIntegrationStatus
    from aviation_agentic_ai.agent_system.sources import load_advisory_source

    config, _ = _test_inputs(tmp_path)
    catalog = _catalog(tmp_path)
    source = load_advisory_source(config, "2026-05-19:123")
    advisory = source.model_copy(
        update={
            "content": source.content.replace(
                "PROBABILITY OF EXTENSION: MEDIUM ",
                "",
            )
        }
    )

    state = run_ingest(
        IngestContext(
            advisory=advisory,
            facility_candidates=list(catalog.facility.entities),
            term_candidates=list(catalog.terminology.registry_terms),
            authority_catalog=catalog,
            guide=load_schema_guide(str(SCHEMA_PATH)),
            run_id="run:missing-ground-stop-extension",
            run_started_at=STARTED,
        )
    )

    assert "extension_probability" in state["event_evidence_integration_task"].missing_slots
    assert state["event_evidence_integration_proposal"].integration_status is EventEvidenceIntegrationStatus.INSUFFICIENT
    assert state["integration_graph_patch"] is None
    assert state["validation"] is None
    assert state["formal_publication"] is None
    assert state["ingestion_package"] is None
    assert state["formal_layers"]["decision"]["status"] == "insufficient"


def test_blocked_authority_registry_is_absorbing_at_the_join(tmp_path):
    """A cross-branch audit conflict blocks preflight without partial recovery."""

    facility = resolve_facility_authority(
        task=_task("facility"),
        request=_facility_envelope(tmp_path),
    )
    terminology = resolve_terminology_authority(
        task=_task("terminology"),
        request=_gs_envelope(tmp_path),
    )
    authority_registry = workflow_module.merge_authority_source_records(
        workflow_module.AuthoritySourceRecordRegistry(records=facility.authority_source_records),
        workflow_module.AuthoritySourceRecordRegistry(
            records=(
                facility.authority_source_records[0].model_copy(
                    update={"content": "conflicting canonical content"}
                ),
            )
        ),
    )

    joined = workflow_module._join_node(
        {
            "facility_authority_result": facility,
            "terminology_authority_result": terminology,
            "authority_source_records": authority_registry,
        }
    )

    assert joined["resolution_preflight_status"] == "blocked"
    assert authority_registry.records == ()


def test_exact_tmi_profile_does_not_depend_on_optional_term_definition(tmp_path):
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
            semantic_resolution_tool_model_factory=lambda tools: (
                calls.append("semantic-resolution") or None
            ),
        )
    )

    assert calls == []
    assert state["resolution_preflight_status"] == "resolved"
    assert "extension_probability" in state["event_evidence_integration_task"].missing_slots
    assert state["integration_graph_patch"] is None
    assert state["formal_layers"]["decision"]["status"] == "insufficient"


def test_event_class_hint_mismatch_blocks_before_assembly_factory(tmp_path, monkeypatch):
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

    result = workflow_module._integrate_event_evidence_node(
        {
            "resolution_preflight_status": "resolved",
            "advisory_evidence": advisory_card,
            "facility_authority_result": replace(
                resolve_facility_authority(
                    task=_task("facility"), request=_facility_envelope(tmp_path)
                ),
                evidence_card=facility_card,
            ),
            "terminology_authority_result": replace(
                resolve_terminology_authority(
                    task=_task("terminology"), request=_gs_envelope(tmp_path)
                ),
                evidence_card=terminology_card,
            ),
            "event_class_hint": "atm:GroundStopTMI",
            "formal_event_uri_hint": "",
        }
    )

    assert result["integration_graph_patch"] is None
    assert calls == []

    context_result = workflow_module._publish_event_node(
        {
            "resolution_preflight_status": "resolved",
            **result,
        }
    )

    assert context_result["formal_layers"]["decision"]["status"] == "blocked"


def test_workflow_kg_allowlist_uses_event_claims_not_card_source_ids(
    tmp_path,
    monkeypatch,
):
    """Authority metadata on a card cannot widen the core KG source allowlist."""

    captured = {}
    guide = load_schema_guide(str(SCHEMA_PATH))
    advisory = SourceRecord(
        source_id="fixture:assembly-allowlist",
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
        ),
    )

    original_builder = workflow_module._build_event_evidence_integration_task_from_state

    def capture_inputs(ctx, state, *, event_uri, event_class):
        task = original_builder(
            ctx,
            state,
            event_uri=event_uri,
            event_class=event_class,
        )
        captured["allowed_source_ids"] = {b.source_id for b in task.source_snapshot_bindings}
        return task

    monkeypatch.setattr(
        workflow_module,
        "_build_event_evidence_integration_task_from_state",
        capture_inputs,
    )
    authority_source = "authority:pcg:gdp"
    advisory_card = EvidenceCard(
        agent_role="advisory",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="event_type",
                value="GDP",
                evidence_text="GROUND DELAY PROGRAM",
                source_id=advisory.source_id,
            )
        ],
        source_ids=[advisory.source_id],
    )
    facility_card = EvidenceCard(
        agent_role="facility",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="controlled_facility",
                value="JFK",
                ontology_target="nas:Airport",
                evidence_text="CTL ELEMENT: JFK",
                source_id=advisory.source_id,
                canonical_ref="urn:aviation-agentic-ai:facility:airport:KJFK",
            )
        ],
        source_ids=[advisory.source_id, "authority:nasr:KJFK"],
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
            ),
            EvidenceClaim(
                field_name="authority_definition",
                value="GDP definition",
                evidence_text="authority definition text",
                source_id=authority_source,
            ),
        ],
        source_ids=[advisory.source_id, authority_source],
    )

    workflow_module._integrate_event_evidence_node(
        {
            "resolution_preflight_status": "resolved",
            "advisory_evidence": advisory_card,
            "facility_authority_result": replace(
                resolve_facility_authority(
                    task=_task("facility"), request=_facility_envelope(tmp_path)
                ),
                evidence_card=facility_card,
                resolution_proposal=resolve_facility_authority(
                    task=_task("facility"), request=_facility_envelope(tmp_path)
                ).resolution_proposal.model_copy(update={"authority_source_ids": ()}),
            ),
            "terminology_authority_result": replace(
                resolve_terminology_authority(
                    task=_task("terminology"), request=_gs_envelope(tmp_path)
                ),
                evidence_card=terminology_card,
                resolution_proposal=resolve_terminology_authority(
                    task=_task("terminology"), request=_gs_envelope(tmp_path)
                ).resolution_proposal.model_copy(update={"authority_source_ids": ()}),
            ),
            "event_class_hint": "atm:GroundDelayProgramTMI",
            "formal_event_uri_hint": "",
        }
    )

    assert captured["allowed_source_ids"] == {advisory.source_id}


def test_materialization_excludes_authority_only_canonical_entities(
    tmp_path,
    monkeypatch,
):
    """Formal Graph canonical entities come only from accepted event claims."""

    captured = {}
    guide = load_schema_guide(str(SCHEMA_PATH))
    advisory = SourceRecord(
        source_id="2026-05-19:138",
        family=SourceFamily.ATCSCC_ADVISORY,
        content="GROUND DELAY PROGRAM CTL ELEMENT: JFK",
    )
    accepted_ref = "urn:aviation-agentic-ai:facility:airport:KJFK"
    authority_ref = "urn:authority:facility:airport:KJFK"
    authority_source = "authority:nasr:KJFK"
    monkeypatch.setattr(
        workflow_module,
        "_CTX_HOLDER",
        IngestContext(
            advisory=advisory,
            guide=guide,
            run_id="run:test",
        ),
    )

    def capture_validation(**kwargs):
        captured["canonical_entities"] = kwargs["canonical_entities"]
        return GraphValidationResult(publishable=False)

    monkeypatch.setattr(
        workflow_module,
        "validate_graph_patch",
        capture_validation,
    )
    monkeypatch.setattr(
        workflow_module,
        "build_fact_trace_rows",
        lambda **kwargs: (),
    )
    monkeypatch.setattr(
        workflow_module,
        "build_profile_gap_rows",
        lambda **kwargs: (),
    )

    facility_card = EvidenceCard(
        agent_role="facility",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="controlled_facility",
                value="JFK",
                ontology_target="nas:Airport",
                evidence_text="CTL ELEMENT: JFK",
                source_id=advisory.source_id,
                canonical_ref=accepted_ref,
            ),
            EvidenceClaim(
                field_name="authority_facility_record",
                value="KJFK",
                ontology_target="nas:Airport",
                evidence_text="PRIVATE AUTHORITY FACILITY RECORD",
                source_id=authority_source,
                canonical_ref=authority_ref,
            ),
        ],
        canonical_refs=[accepted_ref, authority_ref],
        source_ids=[advisory.source_id, authority_source],
    )
    advisory_card = EvidenceCard(
        agent_role="advisory",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="event_type",
                value="GDP",
                evidence_text="GROUND DELAY PROGRAM",
                source_id=advisory.source_id,
            )
        ],
    )
    terminology_card = EvidenceCard(
        agent_role="terminology",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="operational_term",
                value="GDP",
                ontology_target="atm:GroundDelayProgramTMI",
                evidence_text="GROUND DELAY PROGRAM",
                source_id=advisory.source_id,
            )
        ],
    )
    event_uri = "urn:aviation-agentic-ai:event:test"

    workflow_module._validate_event_patch_node(
        {
            "integration_graph_patch": GraphPatchBlock(
                patch_lines=[
                    GraphPatchLine(
                        subject=event_uri,
                        predicate="rdf:type",
                        object="atm:GroundDelayProgramTMI",
                        source_ids=[advisory.source_id],
                    )
                ]
            ),
            "event_uri": event_uri,
            "event_class": "atm:GroundDelayProgramTMI",
            "advisory_evidence": advisory_card,
            "facility_authority_result": replace(
                resolve_facility_authority(
                    task=_task("facility"), request=_facility_envelope(tmp_path)
                ),
                evidence_card=facility_card,
            ),
            "terminology_authority_result": replace(
                resolve_terminology_authority(
                    task=_task("terminology"), request=_gs_envelope(tmp_path)
                ),
                evidence_card=terminology_card,
            ),
        }
    )

    assert captured["canonical_entities"] == {accepted_ref: "nas:Airport"}
