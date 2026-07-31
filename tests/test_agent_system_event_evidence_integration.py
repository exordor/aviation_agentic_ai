"""Tests for bounded event-evidence tools, preflight validation, and agent loop."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import pytest

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.construction_contracts import (
    EventEvidenceIntegrationTask,
    EventEvidenceIntegrationTaskFields,
    EventEvidenceFactProposal,
    EventEvidenceProfileGapProposal,
    ContractExecutionBinding,
    ResolutionDecision,
    SourceSnapshotBinding,
    canonical_id_tuple_token,
    seal_event_evidence_integration_task,
    stable_contract_id,
)
SHA_A = "a" * 64
SHA_B = "b" * 64
STARTED = datetime(2026, 5, 19, 20, 15, tzinfo=UTC)
EVENT_ID = "urn:aviation-agentic-ai:event:test:1"


def _binding(run_id: str = "run-1") -> ContractExecutionBinding:
    return ContractExecutionBinding(
        run_id=run_id,
        created_at=STARTED,
        tool_version="deterministic-event-evidence-integration-v1",
    )


def _assembly_task(
    *,
    event_id: str = EVENT_ID,
    resolution_proposal_id: str = "res-prop-1",
    proposed_facts: tuple[EventEvidenceFactProposal, ...] | None = None,
    profile_gaps: tuple[EventEvidenceProfileGapProposal, ...] | None = None,
    event_source_family: SourceFamily = SourceFamily.ATCSCC_ADVISORY,
) -> EventEvidenceIntegrationTask:
    facts = (
        (
            EventEvidenceFactProposal(
                proposal_item_id="proposal-fact-1",
                subject_id=event_id,
                predicate_iri="rdf:type",
                object_kind="iri",
                object_value="atm:GroundStopTMI",
                evidence_claim_ids=("evidence:event:type",),
                validation_profile_id="profile-1",
            ),
        )
        if proposed_facts is None
        else proposed_facts
    )
    gaps = (
        (
            EventEvidenceProfileGapProposal(
                proposal_item_id="proposal-gap-1",
                event_id=event_id,
                field="impacting_condition",
                normalized_value="weather",
                evidence_claim_ids=("evidence:event:weather",),
                schema_mapping_reason_code="not_in_profile",
                validation_profile_id="profile-1",
            ),
        )
        if profile_gaps is None
        else profile_gaps
    )
    selected = ("evidence:event:type", "evidence:event:weather")
    core_event_fact_ids = tuple(
        sorted(fact.proposal_item_id for fact in facts)
    )
    task_id = stable_contract_id(
        "event-evidence-integration-task",
        "run-1",
        event_id,
        canonical_id_tuple_token(core_event_fact_ids, sort_values=True),
        canonical_id_tuple_token((resolution_proposal_id,), sort_values=True),
        canonical_id_tuple_token(selected, sort_values=True),
        "profile-1",
        "context-1",
        SHA_A,
    )
    fields = EventEvidenceIntegrationTaskFields(
        task_id=task_id,
        run_id="run-1",
        event_id=event_id,
        core_event_fact_ids=core_event_fact_ids,
        resolution_proposal_ids=(resolution_proposal_id,),
        available_evidence_layer_ids=("layer:advisory", "layer:weather"),
        required_event_slots=("controlled_facility", "event_type"),
        optional_event_slots=("impacting_condition",),
        missing_slots=(),
        schema_profile_id="profile-1",
        schema_context_id="context-1",
        schema_snapshot_sha256=SHA_A,
        selected_evidence_claim_ids=selected,
        evidence_records=(
            {
                "evidence_id": "evidence:event:type",
                "field_name": "event_type",
                "value": "GS",
                "evidence_text": "GROUND STOP",
                "source_id": "source:event",
            },
            {
                "evidence_id": "evidence:event:weather",
                "field_name": "impacting_condition",
                "value": "weather",
                "evidence_text": "IMPACTING CONDITION: WEATHER",
                "source_id": "source:event",
            },
        ),
        resolution_records=(
            {
                "resolution_proposal_id": resolution_proposal_id,
                "decision": ResolutionDecision.ACCEPTED,
                "selected_candidate_id": "candidate:ground-stop",
                "supporting_evidence_claim_ids": ("evidence:event:type",),
                "authority_source_ids": ("source:event",),
            },
        ),
        proposed_facts=facts,
        profile_gaps=gaps,
        context_association_ids=("assoc-weather-1",),
        context_associations=(
            {
                "association_id": "assoc-weather-1",
                "run_id": "run-1",
                "event_id": event_id,
                "report_id": "weather-report-1",
                "facility_id": "facility-1",
                "relation_type": "observation_during_operation",
                "selection_method": "latest eligible report",
                "relevant_times": {"observed_at": "2026-05-19T21:30:00Z"},
                "source_id": "source:weather",
                "source_snapshot_sha256": SHA_A,
                "causal_claim": False,
            },
        ),
        public_observation_ids=("obs-bts-1",),
        public_observations=(
            {
                "observation_id": "obs-bts-1",
                "run_id": "run-1",
                "event_id": event_id,
                "phase": "active",
                "metric_key": "cancelled_count",
                "value": 2,
                "derivation_id": "derivation-bts-1",
                "validation_profile_id": "profile-public-1",
                "validation_profile_checksum": SHA_B,
                "source_id": "source:bts",
                "source_snapshot_sha256": SHA_B,
            },
        ),
        omitted_slots=(),
        validation_feedback=(),
        source_snapshot_bindings=(
            SourceSnapshotBinding(
                source_id="source:bts",
                source_family=SourceFamily.BTS_ON_TIME,
                source_snapshot_sha256=SHA_B,
            ),
            SourceSnapshotBinding(
                source_id="source:event",
                source_family=event_source_family,
                source_snapshot_sha256=SHA_B,
            ),
            SourceSnapshotBinding(
                source_id="source:weather",
                source_family=SourceFamily.METAR,
                source_snapshot_sha256=SHA_A,
            ),
        ),
        remaining_tool_budget=6,
    )
    return seal_event_evidence_integration_task(fields=fields, binding=_binding())


def test_deterministic_compiler_compiles_fixed_proposal() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
    )

    task = _assembly_task()
    proposal = compile_event_evidence_integration_proposal(
        task=task,
        binding=_binding(),
    )

    assert proposal.event_id == "urn:aviation-agentic-ai:event:test:1"
    assert proposal.integration_status.value == "ok"
    assert proposal.task_payload_checksum == task.payload_checksum
    assert len(proposal.proposed_facts) == 1
    assert len(proposal.profile_gaps) == 1


def test_preflight_validator_repairable_formatting_defect() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )

    task_fact = EventEvidenceFactProposal(
        proposal_item_id="proposal-fact-1",
        subject_id=EVENT_ID,
        predicate_iri="atm:controlledFacility",
        object_kind="iri",
        object_value="KJFK",
        evidence_claim_ids=("evidence:event:type",),
        validation_profile_id="profile-1",
    )
    task = _assembly_task(proposed_facts=(task_fact,), profile_gaps=())
    repairable_fact = EventEvidenceFactProposal(
        proposal_item_id="proposal-fact-1",
        subject_id=EVENT_ID,
        predicate_iri="atm:controlledFacility",
        object_kind="iri",
        object_value="kjfk",
        evidence_claim_ids=("evidence:event:type",),
        validation_profile_id="profile-1",
    )
    proposal = compile_event_evidence_integration_proposal(
        task=task,
        proposed_facts=(repairable_fact,),
        binding=_binding(),
    )
    feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=proposal,
        binding=_binding(),
    )

    assert feedback is not None
    assert feedback.repairable is True
    assert "KJFK" in feedback.allowed_corrections or "https://example.test/facility/KJFK" in feedback.allowed_corrections or len(feedback.allowed_corrections) > 0


def test_preflight_rejects_unlisted_non_type_object_value() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )

    task_fact = EventEvidenceFactProposal(
        proposal_item_id="proposal-fact-1",
        subject_id=EVENT_ID,
        predicate_iri="atm:controlledFacility",
        object_kind="iri",
        object_value="KJFK",
        evidence_claim_ids=("evidence:event:type",),
        validation_profile_id="profile-1",
    )
    task = _assembly_task(proposed_facts=(task_fact,), profile_gaps=())
    unlisted = task_fact.model_copy(update={"object_value": "KXYZ"})
    proposal = compile_event_evidence_integration_proposal(
        task=task,
        proposed_facts=(unlisted,),
        profile_gaps=(),
        binding=_binding(),
    )

    feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=proposal,
        binding=_binding(),
    )
    assert feedback is not None
    assert feedback.violation_code == "OUT_OF_TASK_OBJECT_VALUE"
    assert feedback.repairable is False


def test_preflight_validator_hard_causal_violation() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )

    task = _assembly_task()
    # Fact attempting forbidden causal assertion
    forbidden_fact = EventEvidenceFactProposal(
        proposal_item_id="proposal-fact-1",
        subject_id=EVENT_ID,
        predicate_iri="atm:causedByWeather",
        object_kind="iri",
        object_value="atm:Thunderstorm",
        evidence_claim_ids=("evidence:event:type",),
        validation_profile_id="profile-1",
    )
    proposal = compile_event_evidence_integration_proposal(
        task=task,
        proposed_facts=(forbidden_fact,),
        binding=_binding(),
    )
    feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=proposal,
        binding=_binding(),
    )

    assert feedback is not None
    assert feedback.repairable is False
    assert feedback.allowed_corrections == ()


def test_preflight_rejects_empty_and_missing_core_fact_proposals() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )

    second_fact = EventEvidenceFactProposal(
        proposal_item_id="proposal-fact-2",
        subject_id=EVENT_ID,
        predicate_iri="atm:advisoryNumber",
        object_kind="literal",
        object_value="123",
        evidence_claim_ids=("evidence:event:type",),
        validation_profile_id="profile-1",
    )
    task = _assembly_task(
        proposed_facts=(*_assembly_task().proposed_facts, second_fact),
        profile_gaps=(),
    )

    empty = compile_event_evidence_integration_proposal(
        task=task,
        proposed_facts=(),
        profile_gaps=(),
        binding=_binding(),
    )
    assert empty.integration_status.value == "insufficient"
    assert empty.proposed_facts == ()
    assert empty.profile_gaps == ()

    missing = compile_event_evidence_integration_proposal(
        task=task,
        proposed_facts=(task.proposed_facts[0],),
        profile_gaps=(),
        binding=_binding(),
    )
    missing_feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=missing,
        binding=_binding(),
    )
    assert missing_feedback is not None
    assert missing_feedback.violation_code == "MISSING_REQUIRED_FORMAL_SLOT"


def test_gap_only_task_compiles_to_empty_insufficient_proposal() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
    )

    gap = _assembly_task().profile_gaps[0]
    task = _assembly_task(proposed_facts=(), profile_gaps=(gap,))
    proposal = compile_event_evidence_integration_proposal(
        task=task,
        proposed_facts=(),
        profile_gaps=(gap,),
        binding=_binding(),
    )

    assert proposal.integration_status.value == "insufficient"
    assert proposal.proposed_facts == ()
    assert proposal.profile_gaps == ()
    assert proposal.evidence_bindings == ()
    assert proposal.resolution_proposal_ids == ()
    assert proposal.context_association_ids == ()
    assert proposal.source_snapshot_bindings == ()


def test_preflight_returns_feedback_for_foreign_task_binding() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )

    task = _assembly_task(profile_gaps=())
    foreign_task = _assembly_task(event_id="urn:aviation-agentic-ai:event:test:foreign", profile_gaps=())
    foreign_proposal = compile_event_evidence_integration_proposal(
        task=foreign_task,
        binding=_binding(),
    )

    feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=foreign_proposal,
        binding=_binding(),
    )

    assert feedback is not None
    assert feedback.violation_code == "TASK_BINDING_MISMATCH"
    assert feedback.affected_proposal_item_id == task.task_id
    assert feedback.evidence_ids == ()


def test_preflight_rejects_extra_formal_fact() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )

    task = _assembly_task(profile_gaps=())
    extra = EventEvidenceFactProposal(
        proposal_item_id="proposal-fact-extra",
        subject_id=EVENT_ID,
        predicate_iri="atm:advisoryNumber",
        object_kind="literal",
        object_value="123",
        evidence_claim_ids=("evidence:event:type",),
        validation_profile_id="profile-1",
    )
    proposal = compile_event_evidence_integration_proposal(
        task=task,
        proposed_facts=(*task.proposed_facts, extra),
        profile_gaps=(),
        binding=_binding(),
    )

    feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=proposal,
        binding=_binding(),
    )
    assert feedback is not None
    assert feedback.violation_code == "OUT_OF_TASK_FORMAL_FACT"
    assert feedback.affected_proposal_item_id == "proposal-fact-extra"


@pytest.mark.parametrize(
    ("field_name", "replacement", "expected_code"),
    (
        ("subject_id", "event-foreign", "OUT_OF_TASK_EVENT"),
        ("predicate_iri", "atm:foreignPredicate", "OUT_OF_SCHEMA_ASSERTION"),
        ("object_value", "atm:GroundDelayProgramTMI", "OUT_OF_SCHEMA_ASSERTION"),
        ("object_kind", "literal", "OUT_OF_SCHEMA_ASSERTION"),
        ("validation_profile_id", "profile-foreign", "OUT_OF_PROFILE_ASSERTION"),
        (
            "evidence_claim_ids",
            ("evidence:event:weather",),
            "OUT_OF_TASK_EVIDENCE",
        ),
        ("derivation_ids", ("derivation-bts-1",), "OUT_OF_TASK_DERIVATION"),
    ),
)
def test_preflight_rejects_formal_fact_signature_mutation(
    field_name: str,
    replacement: object,
    expected_code: str,
) -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )

    task = _assembly_task(profile_gaps=())
    proposal = compile_event_evidence_integration_proposal(
        task=task,
        profile_gaps=(),
        binding=_binding(),
    )
    mutated_fact = proposal.proposed_facts[0].model_copy(
        update={field_name: replacement}
    )
    mutated = proposal.model_copy(update={"proposed_facts": (mutated_fact,)})

    feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=mutated,
        binding=_binding(),
    )
    assert feedback is not None
    assert feedback.violation_code == expected_code


@pytest.mark.parametrize(
    ("field_name", "replacement", "expected_code"),
    (
        ("event_id", "event-foreign", "OUT_OF_TASK_EVENT"),
        ("field", "other_field", "OUT_OF_TASK_PROFILE_GAP"),
        ("normalized_value", "volume", "OUT_OF_TASK_PROFILE_GAP"),
        (
            "evidence_claim_ids",
            ("evidence:event:type",),
            "OUT_OF_TASK_EVIDENCE",
        ),
        ("schema_mapping_reason_code", "other_reason", "OUT_OF_TASK_PROFILE_GAP"),
        ("validation_profile_id", "profile-foreign", "OUT_OF_PROFILE_ASSERTION"),
    ),
)
def test_preflight_rejects_profile_gap_signature_mutation(
    field_name: str,
    replacement: object,
    expected_code: str,
) -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )

    task = _assembly_task()
    proposal = compile_event_evidence_integration_proposal(task=task, binding=_binding())
    mutated_gap = proposal.profile_gaps[0].model_copy(
        update={field_name: replacement}
    )
    mutated = proposal.model_copy(update={"profile_gaps": (mutated_gap,)})

    feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=mutated,
        binding=_binding(),
    )
    assert feedback is not None
    assert feedback.violation_code == expected_code


@pytest.mark.parametrize(
    ("profile_gaps", "expected_code"),
    (
        ((), "MISSING_REQUIRED_PROFILE_GAP"),
        (
            (
                _assembly_task().profile_gaps[0],
                EventEvidenceProfileGapProposal(
                    proposal_item_id="proposal-gap-foreign",
                    event_id=EVENT_ID,
                    field="impacting_condition",
                    normalized_value="weather",
                    evidence_claim_ids=("evidence:event:weather",),
                    schema_mapping_reason_code="not_in_profile",
                    validation_profile_id="profile-1",
                ),
            ),
            "OUT_OF_TASK_PROFILE_GAP",
        ),
    ),
)
def test_preflight_requires_exact_profile_gap_item_ids(
    profile_gaps: tuple[EventEvidenceProfileGapProposal, ...],
    expected_code: str,
) -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )

    task = _assembly_task()
    proposal = compile_event_evidence_integration_proposal(
        task=task,
        profile_gaps=profile_gaps,
        binding=_binding(),
    )
    feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=proposal,
        binding=_binding(),
    )
    assert feedback is not None
    assert feedback.violation_code == expected_code


@pytest.mark.parametrize(
    ("field_name", "replacement", "expected_code"),
    (
        (
            "evidence_bindings",
            ("evidence:foreign",),
            "TASK_EVIDENCE_SET_MISMATCH",
        ),
        (
            "resolution_proposal_ids",
            ("resolution-foreign",),
            "TASK_RESOLUTION_SET_MISMATCH",
        ),
        (
            "context_association_ids",
            ("association-foreign",),
            "TASK_CONTEXT_SET_MISMATCH",
        ),
    ),
)
def test_preflight_requires_exact_top_level_task_sets(
    field_name: str,
    replacement: tuple[str, ...],
    expected_code: str,
) -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )

    task = _assembly_task()
    proposal = compile_event_evidence_integration_proposal(task=task, binding=_binding())
    mutated = proposal.model_copy(update={field_name: replacement})

    feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=mutated,
        binding=_binding(),
    )
    assert feedback is not None
    assert feedback.violation_code == expected_code


def test_preflight_requires_exact_source_bindings() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )

    task = _assembly_task()
    proposal = compile_event_evidence_integration_proposal(task=task, binding=_binding())
    foreign_binding = SourceSnapshotBinding(
        source_id="source:foreign",
        source_family=SourceFamily.METAR,
        source_snapshot_sha256=SHA_A,
    )
    mutated = proposal.model_copy(
        update={"source_snapshot_bindings": (foreign_binding,)}
    )

    feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=mutated,
        binding=_binding(),
    )
    assert feedback is not None
    assert feedback.violation_code == "TASK_SOURCE_BINDING_SET_MISMATCH"


@pytest.mark.parametrize(
    ("layer_id", "artifact_id", "expected_code"),
    (
        ("core", "proposal-fact-foreign", "OUT_OF_TASK_FORMAL_FACT"),
        ("weather", "association-foreign", "OUT_OF_TASK_CONTEXT_ASSOCIATION"),
        ("bts", "observation-foreign", "OUT_OF_TASK_PUBLIC_OBSERVATION"),
    ),
)
def test_preflight_rejects_foreign_component_artifacts(
    layer_id: str,
    artifact_id: str,
    expected_code: str,
) -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )
    from aviation_agentic_ai.agent_system.construction_contracts import (
        EvidenceLayerResult,
        EvidenceLayerStatus,
    )

    task = _assembly_task()
    proposal = compile_event_evidence_integration_proposal(task=task, binding=_binding())
    foreign_layer = EvidenceLayerResult(
        layer_id=layer_id,
        status=EvidenceLayerStatus.OK,
        required_for_task=layer_id == "core",
        artifact_ids=(artifact_id,),
    )
    mutated = proposal.model_copy(
        update={"evidence_layer_results": (foreign_layer,)}
    )

    feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=mutated,
        binding=_binding(),
    )
    assert feedback is not None
    assert feedback.violation_code == expected_code


def test_preflight_accepts_advisory_backed_reason_and_ground_stop_gap() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )

    reason_fact = EventEvidenceFactProposal(
        proposal_item_id="proposal-fact-1",
        subject_id=EVENT_ID,
        predicate_iri="atm:impactingCondition",
        object_kind="literal",
        object_value="weather",
        evidence_claim_ids=("evidence:event:weather",),
        validation_profile_id="profile-1",
    )
    gdp_task = _assembly_task(
        proposed_facts=(reason_fact,),
        profile_gaps=(),
    )
    gdp_proposal = compile_event_evidence_integration_proposal(
        task=gdp_task,
        profile_gaps=(),
        binding=_binding(),
    )
    assert (
        preflight_validate_event_evidence_proposal(
            task=gdp_task,
            proposal=gdp_proposal,
            binding=_binding(),
        )
        is None
    )

    ground_stop_task = _assembly_task()
    ground_stop_proposal = compile_event_evidence_integration_proposal(
        task=ground_stop_task,
        binding=_binding(),
    )
    assert (
        preflight_validate_event_evidence_proposal(
            task=ground_stop_task,
            proposal=ground_stop_proposal,
            binding=_binding(),
        )
        is None
    )


@pytest.mark.parametrize("as_gap", (False, True))
def test_preflight_rejects_weather_backed_declared_reason(as_gap: bool) -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )

    reason_fact = EventEvidenceFactProposal(
        proposal_item_id="proposal-fact-1",
        subject_id=EVENT_ID,
        predicate_iri="atm:impactingCondition",
        object_kind="literal",
        object_value="weather",
        evidence_claim_ids=("evidence:event:weather",),
        validation_profile_id="profile-1",
    )
    reason_gap = EventEvidenceProfileGapProposal(
        proposal_item_id="proposal-gap-1",
        event_id=EVENT_ID,
        field="impacting_condition",
        normalized_value="weather",
        evidence_claim_ids=("evidence:event:weather",),
        schema_mapping_reason_code="not_in_profile",
        validation_profile_id="profile-1",
    )
    task = _assembly_task(
        proposed_facts=(
            _assembly_task().proposed_facts[0] if as_gap else reason_fact,
        ),
        profile_gaps=(reason_gap,) if as_gap else (),
        event_source_family=SourceFamily.METAR,
    )
    proposal = compile_event_evidence_integration_proposal(task=task, binding=_binding())

    feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=proposal,
        binding=_binding(),
    )
    assert feedback is not None
    assert feedback.violation_code == "INVALID_DECLARED_REASON_SUPPORT"


def test_preflight_rejects_bts_derived_declared_reason() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
        preflight_validate_event_evidence_proposal,
    )

    reason_fact = EventEvidenceFactProposal(
        proposal_item_id="proposal-fact-1",
        subject_id=EVENT_ID,
        predicate_iri="atm:impactingCondition",
        object_kind="literal",
        object_value="weather",
        evidence_claim_ids=("evidence:event:weather",),
        derivation_ids=("derivation-bts-1",),
        validation_profile_id="profile-1",
    )
    task = _assembly_task(proposed_facts=(reason_fact,), profile_gaps=())
    proposal = compile_event_evidence_integration_proposal(task=task, binding=_binding())

    feedback = preflight_validate_event_evidence_proposal(
        task=task,
        proposal=proposal,
        binding=_binding(),
    )
    assert feedback is not None
    assert feedback.violation_code == "INVALID_DECLARED_REASON_SUPPORT"


def test_mutated_bindings_fail_closed() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
    )

    task = _assembly_task()
    wrong_binding_source = SourceSnapshotBinding(
        source_id="source:event:mutated",
        source_family=SourceFamily.ATCSCC_ADVISORY,
        source_snapshot_sha256=SHA_B,
    )

    with pytest.raises(ValueError, match="source binding differs"):
        compile_event_evidence_integration_proposal(
            task=task,
            source_snapshot_bindings=(wrong_binding_source,),
            binding=_binding(),
        )


def test_repeated_compilation_produces_identical_ids() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        compile_event_evidence_integration_proposal,
    )

    task = _assembly_task()
    p1 = compile_event_evidence_integration_proposal(task=task, binding=_binding())
    p2 = compile_event_evidence_integration_proposal(task=task, binding=_binding())

    assert p1.event_evidence_integration_proposal_id == p2.event_evidence_integration_proposal_id
    assert p1.payload_checksum == p2.payload_checksum


def test_workflow_three_cases_event_evidence_integration_regression(tmp_path: Path) -> None:
    from aviation_agentic_ai.agent_system.sources import load_advisory_source
    from aviation_agentic_ai.agent_system.workflow import IngestContext, run_ingest
    from aviation_agentic_ai.cross_source.contracts import CanonicalEntity, CodeValue, EntityType
    from test_agent_system_authority_evidence import _catalog, _test_inputs

    config, _ = _test_inputs(tmp_path)
    catalog = _catalog(tmp_path)
    facilities = {
        "KJFK": CanonicalEntity(
            entity_id="urn:aviation-agentic-ai:facility:airport:KJFK",
            entity_type=EntityType.AIRPORT,
            preferred_label="John F Kennedy International Airport",
            codes=[CodeValue(scheme="IATA", value="JFK"), CodeValue(scheme="ICAO", value="KJFK")],
        ),
        "KEWR": CanonicalEntity(
            entity_id="urn:aviation-agentic-ai:facility:airport:KEWR",
            entity_type=EntityType.AIRPORT,
            preferred_label="Newark Liberty International Airport",
            codes=[CodeValue(scheme="IATA", value="EWR"), CodeValue(scheme="ICAO", value="KEWR")],
        ),
    }

    test_cases = [
        ("2026-05-19:123", "KJFK", "GroundStopTMI", "partial"),
        ("2026-05-19:138", "KJFK", "GroundDelayProgramTMI", "partial"),
        ("2026-05-20:020", "KEWR", "GroundDelayProgramTMI", "partial"),
    ]

    now = datetime.now(UTC)
    for source_id, fac_code, expected_class, expected_status in test_cases:
        advisory = load_advisory_source(config, source_id)
        out_dir = tmp_path / source_id.replace(":", "_")
        ctx = IngestContext(
            advisory=advisory,
            facility_candidates=[facilities[fac_code]],
            authority_catalog=catalog,
            run_id=f"run:{source_id}",
            run_started_at=now,
            output_dir=str(out_dir),
        )

        state = run_ingest(ctx)

        # 1. Zero Assembly model calls
        assert len(state["model_calls"]) == 0

        # 2. EventEvidenceIntegrationTask & Proposal state present
        task = state.get("event_evidence_integration_task")
        proposal = state.get("event_evidence_integration_proposal")
        assert task is not None
        assert proposal is not None
        assert proposal.integration_status.value == expected_status
        assert state["integration_graph_patch"] is not None
        assert state["validation"].publishable
        assert state["materialization"] is not None

        # 3. Canonical facility verification
        fac_facts = [f for f in proposal.proposed_facts if f.predicate_iri == "atm:controlledNASelement"]
        assert len(fac_facts) == 1
        assert fac_facts[0].object_value == facilities[fac_code].entity_id

        # 4. Reason / Profile Gap verification
        if source_id == "2026-05-19:123":
            # Ground Stop has impacting_condition as profile gap
            assert len(proposal.profile_gaps) == 1
            assert proposal.profile_gaps[0].field == "impacting_condition"
            assert proposal.profile_gaps[0].normalized_value == "weather"
            reason_facts = [f for f in proposal.proposed_facts if f.predicate_iri == "atm:impactingCondition"]
            assert len(reason_facts) == 0
            extension_facts = [
                f
                for f in proposal.proposed_facts
                if f.predicate_iri == "atm:extensionProbability"
            ]
            assert len(extension_facts) == 1
            assert extension_facts[0].object_value == "MEDIUM"
            gaps = state["validation"].profile_gaps
            assert len(gaps) == 1
            assert gaps[0].evidence == "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
        elif source_id == "2026-05-19:138":
            # GDP has impacting_condition as formal fact
            reason_facts = [f for f in proposal.proposed_facts if f.predicate_iri == "atm:impactingCondition"]
            assert len(reason_facts) == 1
            assert reason_facts[0].object_value == "weather"
            assert len(proposal.profile_gaps) == 0
            end_facts = [
                f
                for f in proposal.proposed_facts
                if f.predicate_iri == "atm:effectiveEndTime"
            ]
            assert [f.object_value for f in end_facts] == ["2026-05-20T02:59:00Z"]
        elif source_id == "2026-05-20:020":
            # GDP cancellation has missing impacting_condition
            reason_facts = [f for f in proposal.proposed_facts if f.predicate_iri == "atm:impactingCondition"]
            assert len(reason_facts) == 0
            assert "impacting_condition" in task.missing_slots


def test_workflow_canonical_node_identity_and_idempotency(tmp_path: Path) -> None:
    from aviation_agentic_ai.agent_system.sources import load_advisory_source
    from aviation_agentic_ai.agent_system.workflow import IngestContext, run_ingest
    from aviation_agentic_ai.cross_source.contracts import CanonicalEntity, CodeValue, EntityType
    from test_agent_system_authority_evidence import _catalog, _test_inputs

    config, _ = _test_inputs(tmp_path)
    catalog = _catalog(tmp_path)
    fac_jfk = CanonicalEntity(
        entity_id="urn:aviation-agentic-ai:facility:airport:KJFK",
        entity_type=EntityType.AIRPORT,
        preferred_label="John F Kennedy International Airport",
        codes=[CodeValue(scheme="IATA", value="JFK"), CodeValue(scheme="ICAO", value="KJFK")],
    )

    adv123 = load_advisory_source(config, "2026-05-19:123")
    adv138 = load_advisory_source(config, "2026-05-19:138")

    now = datetime.now(UTC)
    ctx1 = IngestContext(advisory=adv123, facility_candidates=[fac_jfk], authority_catalog=catalog, run_id="run:123", run_started_at=now, output_dir=str(tmp_path / "run123"))
    ctx2 = IngestContext(advisory=adv138, facility_candidates=[fac_jfk], authority_catalog=catalog, run_id="run:138", run_started_at=now, output_dir=str(tmp_path / "run138"))

    state1 = run_ingest(ctx1)
    state2 = run_ingest(ctx2)

    prop1 = state1["event_evidence_integration_proposal"]
    prop2 = state2["event_evidence_integration_proposal"]

    # Both KJFK records use the exact same canonical facility node ID
    fac1 = [f for f in prop1.proposed_facts if f.predicate_iri == "atm:controlledNASelement"][0]
    fac2 = [f for f in prop2.proposed_facts if f.predicate_iri == "atm:controlledNASelement"][0]
    assert fac1.object_value == fac2.object_value == "urn:aviation-agentic-ai:facility:airport:KJFK"

    # Idempotency check: run state1 again with identical inputs
    state1_repeat = run_ingest(ctx1)
    prop1_repeat = state1_repeat["event_evidence_integration_proposal"]
    assert prop1.event_evidence_integration_proposal_id == prop1_repeat.event_evidence_integration_proposal_id
    assert prop1.payload_checksum == prop1_repeat.payload_checksum
