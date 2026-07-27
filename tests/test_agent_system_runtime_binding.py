"""Load-bearing Batch A tests for frozen runtime and resolution bindings."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import aviation_agentic_ai.agent_system.agents as agents_module
from langchain_core.messages import AIMessage
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
    GraphPatchBlock,
    GraphPatchLine,
    GraphValidationResult,
    ModelCallRecord,
    ModelToolCall,
    SourceFamily,
    SourceRecord,
)
from aviation_agentic_ai.agent_system.decision_case_contracts import (
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


def _ambiguous_facility_envelope(tmp_path: Path) -> FacilityCandidates:
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


def _ambiguous_term_envelope(tmp_path: Path) -> TermCandidates:
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
                "decision": (
                    "accepted"
                    if self.selected_candidate_id is not None
                    else "abstained"
                ),
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
    factory_calls = []

    def forbidden_factory(tools):
        factory_calls.append(tools)
        raise AssertionError("unique resolution constructed semantic model")

    facility = _resolve_facility_compatibility(
        task=_task("facility"),
        candidates=_facility_envelope(tmp_path),
        semantic_resolution_tool_model_factory=forbidden_factory,
    )
    terminology = _resolve_terminology_compatibility(
        task=_task("terminology"),
        candidates=_gs_envelope(tmp_path),
        semantic_resolution_tool_model_factory=forbidden_factory,
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
    assert {
        json.loads(record.content)["preferred_label"]
        for record in terminology.authority_source_records
    } == {"Ground Stop", "Glide Slope"}
    assert factory_calls == []


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
    factory_calls = []
    envelope = _facility_envelope(tmp_path)
    blocked = _resolve_facility_compatibility(
        task=_task("facility"),
        candidates=replace(envelope, authority_candidate_results=()),
        semantic_resolution_tool_model_factory=lambda tools: factory_calls.append(
            tools
        ),
    )

    assert blocked.agent_result.status is AgentStatus.BLOCKED
    assert blocked.domain_outcome.decision is ResolutionDecision.BLOCKED
    assert factory_calls == []


def test_explicit_insufficient_authority_is_terminal_before_candidate_audit(
    tmp_path,
):
    factory_calls = []
    result = _resolve_facility_compatibility(
        task=_task("facility"),
        candidates=replace(
            _facility_envelope(tmp_path),
            authority_domain_status=AuthorityBuildStatus.INSUFFICIENT,
            authority_domain_reason_code="FACILITY_AUTHORITY_INCOMPLETE",
            authority_candidate_results=(),
        ),
        semantic_resolution_tool_model_factory=lambda tools: factory_calls.append(
            tools
        ),
    )

    assert result.agent_result.status is AgentStatus.ABSTAIN
    assert result.domain_outcome.decision is ResolutionDecision.INSUFFICIENT
    assert (
        result.domain_outcome.limitation_code
        == "FACILITY_AUTHORITY_INCOMPLETE"
    )
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

    result = _resolve_facility_compatibility(
        task=_task("facility"),
        candidates=replace(
            envelope,
            authority_candidate_results=(replace(built, candidate=ineligible),),
        ),
        semantic_resolution_tool_model_factory=lambda tools: factory_calls.append(
            tools
        ),
    )

    assert result.agent_result.status is AgentStatus.ABSTAIN
    assert result.domain_outcome.decision is ResolutionDecision.INSUFFICIENT
    assert (
        result.domain_outcome.limitation_code
        == "NO_ELIGIBLE_AUTHORITY_CANDIDATE"
    )
    assert factory_calls == []


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
    result = _resolve_facility_compatibility(
        task=_task("facility"),
        candidates=envelope,
        semantic_resolution_tool_model_factory=lambda tools: model,
    )

    assert result.agent_result.status is AgentStatus.RESOLVED
    assert result.domain_outcome.decision is ResolutionDecision.ACCEPTED
    assert result.agent_result.evidence_card.canonical_refs == [
        selected_candidate_id
    ]
    assert len(result.agent_result.model_calls) == 2
    assert model.invocations == ["select_tool", "final_answer"]
    assert result.resolution_task.remaining_tool_budget == 3
    assert result.resolution_task.decision is None
    assert not set(candidate_ids) & set(
        result.resolution_task.rejected_candidate_ids
    )
    assert result.resolution_proposal.selected_candidate_id == selected_candidate_id
    assert result.resolution_tool_traces
    assert all(
        claim.source_id == envelope.source_id
        for claim in result.agent_result.evidence_card.claims
    )


def test_multiple_term_candidates_can_abstain_through_the_same_runtime(tmp_path):
    envelope = _ambiguous_term_envelope(tmp_path)
    candidate_ids = [row.candidate_id for row in envelope.authority_candidate_results]
    model = _ScriptedResolutionModel(
        candidate_ids=candidate_ids,
        selected_candidate_id=None,
    )

    result = _resolve_terminology_compatibility(
        task=_task("terminology"),
        candidates=envelope,
        semantic_resolution_tool_model_factory=lambda tools: model,
    )

    assert result.agent_result.status is AgentStatus.ABSTAIN
    assert result.domain_outcome.decision is ResolutionDecision.ABSTAINED
    assert result.resolution_proposal.selected_candidate_id is None
    assert len(result.agent_result.model_calls) == 2
    assert model.invocations == ["select_tool", "final_answer"]


def test_semantic_resolution_factory_failure_is_a_sealed_blocked_result(tmp_path):
    envelope = _ambiguous_facility_envelope(tmp_path)
    calls = []

    def failing_factory(tools):
        calls.append(tools)
        raise RuntimeError("scripted setup failure")

    result = _resolve_facility_compatibility(
        task=_task("facility"),
        candidates=envelope,
        semantic_resolution_tool_model_factory=failing_factory,
    )

    assert len(calls) == 1
    assert result.agent_result.status is AgentStatus.BLOCKED
    assert result.domain_outcome.decision is ResolutionDecision.BLOCKED
    assert result.domain_outcome.error_id
    assert result.resolution_task.candidates
    assert result.resolution_proposal.task_id == result.resolution_task.task_id


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
            semantic_resolution_tool_model_factory=lambda tools: (
                calls.append("semantic-resolution") or None
            ),
            kg_tool_model_factory=lambda tools: calls.append("kg") or None,
        )
    )

    assert calls == []
    assert state["resolution_preflight_status"] == "blocked"
    assert state["kg_result"].status is AgentStatus.BLOCKED
    assert state["formal_layers"]["decision"]["status"] == "blocked"


def test_case_assembly_complexity_gate_uses_only_dedicated_factory() -> None:
    """Legacy KG factories never activate Assembly; fixed cases never need it."""

    from types import SimpleNamespace

    def legacy_factory(tools):
        del tools
        return object()

    def dedicated_factory(tools):
        del tools
        return object()
    complete = SimpleNamespace(
        missing_slots=(),
        available_evidence_layer_ids=(
            "layer:advisory",
            "layer:bts",
            "layer:weather",
        ),
    )
    unresolved = SimpleNamespace(
        missing_slots=("impacting_condition",),
        available_evidence_layer_ids=("layer:advisory",),
    )

    for source_id in (
        "2026-05-19:123",
        "2026-05-19:138",
        "2026-05-20:020",
    ):
        assert not workflow_module._should_activate_case_assembly_agent(
            source_id=source_id,
            task=unresolved,
            case_assembly_model_factory=dedicated_factory,
        )
    assert not workflow_module._should_activate_case_assembly_agent(
        source_id="fixture:unresolved",
        task=unresolved,
        case_assembly_model_factory=None,
    )
    assert not workflow_module._should_activate_case_assembly_agent(
        source_id="fixture:unresolved",
        task=complete,
        case_assembly_model_factory=dedicated_factory,
    )
    assert workflow_module._should_activate_case_assembly_agent(
        source_id="fixture:unresolved",
        task=unresolved,
        case_assembly_model_factory=dedicated_factory,
    )
    # A legacy KG factory cannot change the Assembly activation result.
    assert legacy_factory is not dedicated_factory


def test_blocked_assembly_stops_before_kernel_and_materialization(tmp_path, monkeypatch):
    """A sealed blocked Assembly result cannot enter the publication path."""

    from aviation_agentic_ai.agent_system.case_assembly import CaseAssemblyResult
    from aviation_agentic_ai.agent_system.decision_case_contracts import AssemblyStatus
    from aviation_agentic_ai.agent_system.sources import load_advisory_source

    config, _ = _test_inputs(tmp_path)
    catalog = _catalog(tmp_path)
    canonical = load_advisory_source(config, "2026-05-19:123")
    advisory = canonical.model_copy(
        update={
            "source_id": "fixture:blocked-assembly",
            "content": "\n".join(
                line
                for line in canonical.content.splitlines()
                if not line.startswith("IMPACTING CONDITION:")
            ),
        }
    )

    def blocked_assembly(*, task, binding, tool_model_factory):
        del tool_model_factory
        proposal = workflow_module.compile_case_assembly_proposal(
            task=task,
            assembly_status=AssemblyStatus.BLOCKED,
            limitations=("scripted hard semantic violation",),
            binding=binding,
        )
        return CaseAssemblyResult(
            proposal=proposal,
            model_calls=(),
            tool_traces=(),
            failure_reason="scripted hard semantic violation",
        )

    monkeypatch.setattr(workflow_module, "run_case_assembly_agent", blocked_assembly)

    state = run_ingest(
        IngestContext(
            advisory=advisory,
            facility_candidates=list(catalog.facility.entities),
            term_candidates=list(catalog.terminology.registry_terms),
            authority_catalog=catalog,
            guide=load_schema_guide(str(SCHEMA_PATH)),
            run_id="run:blocked-assembly",
            run_started_at=STARTED,
            output_dir=str(tmp_path / "blocked-assembly"),
            case_assembly_model_factory=lambda tools: object(),
        )
    )

    assert state["case_assembly_proposal"].assembly_status is AssemblyStatus.BLOCKED
    assert state["kg_result"].graph_patch is None
    assert state["validation"] is None
    assert state["materialization"] is None
    assert state["formal_layers"]["decision"]["status"] == "blocked"


def test_missing_ground_stop_extension_is_insufficient_and_unpublished(tmp_path):
    """A Ground Stop without its required extension field cannot publish."""

    from aviation_agentic_ai.agent_system.decision_case_contracts import AssemblyStatus
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
            output_dir=str(tmp_path / "missing-ground-stop-extension"),
        )
    )

    assert "extension_probability" in state["case_assembly_task"].missing_slots
    assert (
        state["case_assembly_proposal"].assembly_status
        is AssemblyStatus.INSUFFICIENT
    )
    assert state["kg_result"].graph_patch is None
    assert state["validation"] is None
    assert state["materialization"] is None


def test_explicit_ok_cannot_override_missing_required_slot(tmp_path, monkeypatch):
    """A caller cannot force publication by explicitly selecting Assembly OK."""

    from aviation_agentic_ai.agent_system.case_assembly import CaseAssemblyResult
    from aviation_agentic_ai.agent_system.decision_case_contracts import AssemblyStatus
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

    def explicit_ok_assembly(*, task, binding, tool_model_factory):
        del tool_model_factory
        proposal = workflow_module.compile_case_assembly_proposal(
            task=task,
            assembly_status=AssemblyStatus.OK,
            binding=binding,
        )
        return CaseAssemblyResult(
            proposal=proposal,
            model_calls=(),
            tool_traces=(),
        )

    monkeypatch.setattr(workflow_module, "run_case_assembly_agent", explicit_ok_assembly)

    state = run_ingest(
        IngestContext(
            advisory=advisory,
            facility_candidates=list(catalog.facility.entities),
            term_candidates=list(catalog.terminology.registry_terms),
            authority_catalog=catalog,
            guide=load_schema_guide(str(SCHEMA_PATH)),
            run_id="run:explicit-ok-missing-required",
            run_started_at=STARTED,
            output_dir=str(tmp_path / "explicit-ok-missing-required"),
            case_assembly_model_factory=lambda tools: object(),
        )
    )

    assert (
        state["case_assembly_proposal"].assembly_status
        is AssemblyStatus.INSUFFICIENT
    )
    assert state["kg_result"].graph_patch is None
    assert state["validation"] is None
    assert state["materialization"] is None


def test_hard_preflight_feedback_blocks_publication(tmp_path, monkeypatch):
    """A hard preflight violation blocks before the Formal Graph Kernel."""

    from aviation_agentic_ai.agent_system.case_assembly import CaseAssemblyResult
    from aviation_agentic_ai.agent_system.decision_case_contracts import AssemblyStatus
    from aviation_agentic_ai.agent_system.sources import load_advisory_source

    config, _ = _test_inputs(tmp_path)
    catalog = _catalog(tmp_path)
    canonical = load_advisory_source(config, "2026-05-19:123")
    advisory = canonical.model_copy(
        update={
            "source_id": "fixture:hard-preflight-violation",
            "content": "\n".join(
                line
                for line in canonical.content.splitlines()
                if not line.startswith("IMPACTING CONDITION:")
            ),
        }
    )

    def hard_violation_assembly(*, task, binding, tool_model_factory):
        del tool_model_factory
        forbidden_fact = task.proposed_facts[0].model_copy(
            update={
                "proposal_item_id": "proposal-fact:forbidden-causal",
                "predicate_iri": "atm:causedByWeather",
                "object_value": "atm:Thunderstorm",
            }
        )
        proposal = workflow_module.compile_case_assembly_proposal(
            task=task,
            assembly_status=AssemblyStatus.OK,
            proposed_facts=(*task.proposed_facts, forbidden_fact),
            binding=binding,
        )
        return CaseAssemblyResult(
            proposal=proposal,
            model_calls=(),
            tool_traces=(),
        )

    monkeypatch.setattr(workflow_module, "run_case_assembly_agent", hard_violation_assembly)

    state = run_ingest(
        IngestContext(
            advisory=advisory,
            facility_candidates=list(catalog.facility.entities),
            term_candidates=list(catalog.terminology.registry_terms),
            authority_catalog=catalog,
            guide=load_schema_guide(str(SCHEMA_PATH)),
            run_id="run:hard-preflight-violation",
            run_started_at=STARTED,
            output_dir=str(tmp_path / "hard-preflight-violation"),
            case_assembly_model_factory=lambda tools: object(),
        )
    )

    assert state["case_assembly_feedback"] is not None
    assert state["case_assembly_feedback"].repairable is False
    assert state["case_assembly_proposal"].assembly_status is AssemblyStatus.BLOCKED
    assert state["kg_result"].graph_patch is None
    assert state["validation"] is None
    assert state["materialization"] is None


def test_hard_preflight_block_preserves_component_layer_audit_rows(
    tmp_path,
    monkeypatch,
):
    """Preflight blocking retains the Assembly component-layer audit record."""

    from aviation_agentic_ai.agent_system.case_assembly import CaseAssemblyResult
    from aviation_agentic_ai.agent_system.decision_case_contracts import (
        AssemblyStatus,
        ComponentLayerResult,
        ComponentLayerStatus,
    )
    from aviation_agentic_ai.agent_system.sources import load_advisory_source

    config, _ = _test_inputs(tmp_path)
    catalog = _catalog(tmp_path)
    canonical = load_advisory_source(config, "2026-05-19:123")
    advisory = canonical.model_copy(
        update={
            "source_id": "fixture:hard-preflight-preserve-layers",
            "content": "\n".join(
                line
                for line in canonical.content.splitlines()
                if not line.startswith("IMPACTING CONDITION:")
            ),
        }
    )

    def hard_violation_assembly(*, task, binding, tool_model_factory):
        del tool_model_factory
        component_layers = (
            ComponentLayerResult(
                layer_id="core",
                status=ComponentLayerStatus.OK,
                required_for_task=True,
                artifact_ids=task.core_event_fact_ids,
            ),
            ComponentLayerResult(
                layer_id="optional-context",
                status=ComponentLayerStatus.INSUFFICIENT,
                required_for_task=False,
                missing_reason_code="optional_context_unavailable",
            ),
        )
        forbidden_fact = task.proposed_facts[0].model_copy(
            update={
                "proposal_item_id": "proposal-fact:preserve-layers",
                "predicate_iri": "atm:causedByWeather",
                "object_value": "atm:Thunderstorm",
            }
        )
        proposal = workflow_module.compile_case_assembly_proposal(
            task=task,
            assembly_status=AssemblyStatus.OK,
            component_layer_results=component_layers,
            proposed_facts=(*task.proposed_facts, forbidden_fact),
            binding=binding,
        )
        return CaseAssemblyResult(
            proposal=proposal,
            model_calls=(),
            tool_traces=(),
        )

    monkeypatch.setattr(workflow_module, "run_case_assembly_agent", hard_violation_assembly)

    state = run_ingest(
        IngestContext(
            advisory=advisory,
            facility_candidates=list(catalog.facility.entities),
            term_candidates=list(catalog.terminology.registry_terms),
            authority_catalog=catalog,
            guide=load_schema_guide(str(SCHEMA_PATH)),
            run_id="run:hard-preflight-preserve-layers",
            run_started_at=STARTED,
            output_dir=str(tmp_path / "hard-preflight-preserve-layers"),
            case_assembly_model_factory=lambda tools: object(),
        )
    )

    assert state["case_assembly_proposal"].assembly_status is AssemblyStatus.BLOCKED
    assert tuple(state["case_assembly_proposal"].component_layer_results) == (
        ComponentLayerResult(
            layer_id="core",
            status=ComponentLayerStatus.OK,
            required_for_task=True,
            artifact_ids=state["case_assembly_task"].core_event_fact_ids,
        ),
        ComponentLayerResult(
            layer_id="optional-context",
            status=ComponentLayerStatus.INSUFFICIENT,
            required_for_task=False,
            missing_reason_code="optional_context_unavailable",
        ),
    )
    assert state["kg_result"].graph_patch is None
    assert state["validation"] is None
    assert state["materialization"] is None


def test_blocked_authority_registry_is_absorbing_at_the_join(tmp_path):
    """A cross-branch audit conflict blocks preflight without partial recovery."""

    facility = _resolve_facility_compatibility(
        task=_task("facility"),
        candidates=_facility_envelope(tmp_path),
    )
    terminology = _resolve_terminology_compatibility(
        task=_task("terminology"),
        candidates=_gs_envelope(tmp_path),
    )
    authority_registry = workflow_module.merge_authority_source_records(
        workflow_module.AuthoritySourceRecordRegistry(
            records=facility.authority_source_records
        ),
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
            "facility_resolution_outcome": facility.domain_outcome,
            "terminology_resolution_outcome": terminology.domain_outcome,
            "authority_source_records": authority_registry,
        }
    )

    assert joined["resolution_preflight_status"] == "blocked"
    assert authority_registry.records == ()


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
            semantic_resolution_tool_model_factory=lambda tools: (
                calls.append("semantic-resolution") or None
            ),
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
            output_dir=str(tmp_path),
            case_assembly_model_factory=lambda tools: object(),
        ),
    )

    def capture_inputs(*, task, binding, tool_model_factory):
        del binding, tool_model_factory
        captured["allowed_source_ids"] = {b.source_id for b in task.source_snapshot_bindings}
        proposal = workflow_module.compile_case_assembly_proposal(
            task=task,
            binding=workflow_module.ContractExecutionBinding(
                run_id="run:test",
                created_at=datetime.now(UTC),
                tool_version="deterministic-assembly-v1",
            ),
        )
        return workflow_module.CaseAssemblyResult(
            proposal=proposal,
            model_calls=(),
            tool_traces=(),
            feedback=None,
        )

    monkeypatch.setattr(
        workflow_module,
        "run_case_assembly_agent",
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

    workflow_module._kg_construction_node(
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
            output_dir=str(tmp_path),
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
    monkeypatch.setattr(workflow_module, "write_fact_trace", lambda **kwargs: None)
    monkeypatch.setattr(workflow_module, "write_profile_gaps", lambda **kwargs: None)

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

    workflow_module._materialize_node(
        {
            "kg_result": AgentResult(
                status=AgentStatus.RESOLVED,
                graph_patch=GraphPatchBlock(
                    patch_lines=[
                        GraphPatchLine(
                            subject=event_uri,
                            predicate="rdf:type",
                            object="atm:GroundDelayProgramTMI",
                            source_ids=[advisory.source_id],
                        )
                    ]
                ),
            ),
            "event_uri": event_uri,
            "event_class": "atm:GroundDelayProgramTMI",
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
        }
    )

    assert captured["canonical_entities"] == {accepted_ref: "nas:Airport"}
