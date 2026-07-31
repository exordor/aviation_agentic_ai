"""Tests for bounded event-evidence tools, preflight validation, and agent loop."""

from __future__ import annotations

from datetime import UTC, datetime
import json
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
from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
    EventEvidenceIntegrationToolError,
    EventEvidenceIntegrationToolGateway,
    build_event_evidence_integration_tools,
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


def test_event_evidence_integration_gateway_get_event_requirements() -> None:
    task = _assembly_task()
    gateway = EventEvidenceIntegrationToolGateway(task=task)
    result = gateway.get_event_requirements()

    assert result.status == "ok"
    assert result.event_id == "urn:aviation-agentic-ai:event:test:1"
    assert result.required_event_slots == ["controlled_facility", "event_type"]
    assert result.optional_event_slots == ["impacting_condition"]
    assert result.schema_profile_id == "profile-1"
    assert result.available_evidence_layer_ids == ["layer:advisory", "layer:weather"]
    assert result.remaining_tool_budget == 6


def test_event_evidence_integration_gateway_gets_compact_candidate_bundle() -> None:
    task = _assembly_task()
    gateway = EventEvidenceIntegrationToolGateway(task=task)

    first = gateway.get_candidate_bundle()
    second = gateway.get_candidate_bundle()

    assert first.status == "ok"
    assert first.candidate_bundle_id == second.candidate_bundle_id
    assert first.candidate_bundle_id == stable_contract_id(
        "event-evidence-integration-candidate-bundle",
        task.task_id,
        task.payload_checksum,
    )
    assert [row.proposal_item_id for row in first.candidate_facts] == [
        "proposal-fact-1"
    ]
    assert first.candidate_facts[0].predicate_iri == "rdf:type"
    assert first.candidate_facts[0].object_value == "atm:GroundStopTMI"
    assert [row.proposal_item_id for row in first.candidate_profile_gaps] == [
        "proposal-gap-1"
    ]
    assert [row.evidence_id for row in first.evidence_records] == [
        "evidence:event:type",
        "evidence:event:weather",
    ]
    assert [row.resolution_proposal_id for row in first.resolution_records] == [
        "res-prop-1"
    ]
    assert first.context_association_count == 1
    assert first.public_observation_count == 1
    assert first.context_associations == []
    assert first.public_observations == []
    assert first.association_ids == []
    assert first.observation_ids == []
    assert {
        binding.source_id for binding in first.source_snapshot_bindings
    } == {"source:event"}


def test_event_evidence_integration_gateway_get_schema_context() -> None:
    task = _assembly_task()
    gateway = EventEvidenceIntegrationToolGateway(task=task)
    result = gateway.get_schema_context()

    assert result.status == "ok"
    assert result.schema_profile_id == "profile-1"
    assert result.schema_context_id == "context-1"
    assert result.schema_snapshot_sha256 == SHA_A


def test_event_evidence_integration_gateway_get_source_evidence() -> None:
    task = _assembly_task()
    gateway = EventEvidenceIntegrationToolGateway(task=task)
    result = gateway.get_source_evidence(evidence_ids=["evidence:event:type"])

    assert result.status == "ok"
    assert result.requested_evidence_ids == ["evidence:event:type"]
    assert [row.evidence_id for row in result.evidence_records] == [
        "evidence:event:type"
    ]
    assert result.evidence_records[0].source_id == "source:event"
    assert result.evidence_records[0].evidence_text == "GROUND STOP"

    # Foreign evidence ID must fail closed
    with pytest.raises(EventEvidenceIntegrationToolError):
        gateway.get_source_evidence(evidence_ids=["foreign-evidence"])


def test_event_evidence_integration_gateway_get_resolution_result() -> None:
    task = _assembly_task()
    gateway = EventEvidenceIntegrationToolGateway(task=task)
    result = gateway.get_resolution_result(resolution_proposal_ids=["res-prop-1"])

    assert result.status == "ok"
    assert result.resolution_proposal_ids == ["res-prop-1"]
    assert [row.resolution_proposal_id for row in result.resolution_records] == [
        "res-prop-1"
    ]
    assert result.resolution_records[0].authority_source_ids == ("source:event",)

    with pytest.raises(EventEvidenceIntegrationToolError):
        gateway.get_resolution_result(resolution_proposal_ids=["unknown-proposal"])


def test_event_evidence_integration_gateway_get_context_associations() -> None:
    task = _assembly_task()
    gateway = EventEvidenceIntegrationToolGateway(task=task)
    result = gateway.get_context_associations(association_ids=["assoc-weather-1"])

    assert result.status == "ok"
    assert result.association_ids == ["assoc-weather-1"]
    assert [row.association_id for row in result.context_associations] == [
        "assoc-weather-1"
    ]
    association = result.context_associations[0]
    assert association.event_id == EVENT_ID
    assert association.report_id == "weather-report-1"
    assert association.facility_id == "facility-1"
    assert association.relation_type == "observation_during_operation"
    assert association.source_id == "source:weather"
    assert association.source_snapshot_sha256 == SHA_A
    assert association.causal_claim is False

    with pytest.raises(EventEvidenceIntegrationToolError):
        gateway.get_context_associations(association_ids=["unknown-assoc"])


def test_event_evidence_integration_gateway_get_public_observations() -> None:
    task = _assembly_task()
    gateway = EventEvidenceIntegrationToolGateway(task=task)
    result = gateway.get_public_observations(observation_ids=["obs-bts-1"])

    assert result.status == "ok"
    assert result.observation_ids == ["obs-bts-1"]
    assert [row.observation_id for row in result.public_observations] == [
        "obs-bts-1"
    ]
    observation = result.public_observations[0]
    assert observation.phase == "active"
    assert observation.metric_key == "cancelled_count"
    assert observation.value == 2
    assert observation.derivation_id == "derivation-bts-1"
    assert observation.validation_profile_id == "profile-public-1"
    assert observation.source_id == "source:bts"
    assert observation.source_snapshot_sha256 == SHA_B

    with pytest.raises(EventEvidenceIntegrationToolError):
        gateway.get_public_observations(observation_ids=["unknown-obs"])


def test_build_event_evidence_integration_tools_exposes_only_compact_candidate_bundle() -> None:
    task = _assembly_task()
    gateway = EventEvidenceIntegrationToolGateway(task=task)
    tools = build_event_evidence_integration_tools(gateway)

    assert [tool.name for tool in tools] == ["get_candidate_bundle"]

    bundle = json.loads(tools[0].invoke({}))
    assert bundle["candidate_bundle_id"]
    assert bundle["context_association_count"] == 1
    assert bundle["public_observation_count"] == 1
    assert "context_associations" not in bundle
    assert "public_observations" not in bundle


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


class _ScriptedAssemblyModel:
    def __init__(self, turns: list) -> None:
        self.turns = list(turns)

    def invoke(self, messages: list, *, phase: str):
        return self.turns.pop(0)


def _assembly_tool_turn():
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord, ModelToolCall
    from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
    from langchain_core.messages import AIMessage

    calls = [
        {
            "id": "call:candidate-bundle",
            "name": "get_candidate_bundle",
            "args": {},
            "type": "tool_call",
        }
    ]
    return ToolModelTurn(
        message=AIMessage(content="", tool_calls=calls),
        record=ModelCallRecord(
            agent="event_evidence_integration",
            raw_response="",
            prompt_version="event-evidence-integration-v1",
            tool_calls=[
                ModelToolCall(
                    call_id="call:candidate-bundle",
                    name="get_candidate_bundle",
                    arguments={},
                )
            ],
        ),
    )


def _valid_proposal_text(task: EventEvidenceIntegrationTask | None = None) -> str:
    task = task or _assembly_task()
    return json.dumps(
        {
            "decision": "accepted",
            "candidate_bundle_id": stable_contract_id(
                "event-evidence-integration-candidate-bundle",
                task.task_id,
                task.payload_checksum,
            ),
            "selected_fact_ids": list(task.core_event_fact_ids),
            "selected_profile_gap_ids": [
                gap.proposal_item_id for gap in task.profile_gaps
            ],
            "limitation": None,
        },
        sort_keys=True,
    )


def test_event_evidence_integration_tool_observation_preserves_compact_serialization() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration import (
        _model_tool_observation,
    )
    from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
        EventEvidenceIntegrationToolResult,
    )

    payload = json.loads(
        _model_tool_observation(
            EventEvidenceIntegrationToolResult(
                tool="get_candidate_bundle",
                candidate_bundle_id="bundle:1",
            )
        )
    )

    assert payload == {
        "tool": "get_candidate_bundle",
        "candidate_bundle_id": "bundle:1",
    }


def test_event_evidence_integration_reports_provider_truncation_before_tool_call_error() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration import (
        run_event_evidence_integration_agent,
    )
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
    from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn

    scripted_model = _ScriptedAssemblyModel(
        [
            ToolModelTurn(
                message=None,
                record=ModelCallRecord(
                    agent="event_evidence_integration",
                    raw_response="",
                    prompt_version="event-evidence-integration-v1",
                    output_tokens=512,
                    finish_reason="length",
                    error="provider returned an invalid native tool call",
                ),
            )
        ]
    )

    result = run_event_evidence_integration_agent(
        task=_assembly_task(),
        binding=_binding(),
        tool_model_factory=lambda tools: scripted_model,
    )

    assert result.failure_reason == (
        "Event Evidence Integration Agent provider output was truncated"
    )


def test_event_evidence_integration_agent_evidence_schema_choice_success() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration import run_event_evidence_integration_agent
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
    from aviation_agentic_ai.agent_system.construction_contracts import (
        EventEvidenceIntegrationStatus,
        EvidenceLayerResult,
        EvidenceLayerStatus,
    )
    from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
    from langchain_core.messages import AIMessage

    task = _assembly_task()
    evidence_layer_results = (
        EvidenceLayerResult(
            layer_id="core",
            status=EvidenceLayerStatus.OK,
            required_for_task=True,
            artifact_ids=("proposal-fact-1",),
        ),
        EvidenceLayerResult(
            layer_id="weather",
            status=EvidenceLayerStatus.BLOCKED,
            required_for_task=False,
            blocking_error_id="weather:source-unavailable",
        ),
        EvidenceLayerResult(
            layer_id="bts",
            status=EvidenceLayerStatus.INSUFFICIENT,
            required_for_task=False,
            missing_reason_code="no_matching_public_observation",
        ),
    )
    limitations = (
        "BTS observation layer is insufficient",
        "Weather context layer is blocked",
    )
    turn_1 = _assembly_tool_turn()
    turn_2 = ToolModelTurn(
        message=AIMessage(content=_valid_proposal_text()),
        record=ModelCallRecord(
            agent="event_evidence_integration",
            raw_response=_valid_proposal_text(),
            prompt_version="event-evidence-integration-v1",
        ),
    )
    scripted_model = _ScriptedAssemblyModel([turn_1, turn_2])

    result = run_event_evidence_integration_agent(
        task=task,
        binding=_binding(),
        tool_model_factory=lambda tools: scripted_model,
        integration_status=EventEvidenceIntegrationStatus.PARTIAL,
        evidence_layer_results=evidence_layer_results,
        limitations=limitations,
    )

    assert result.proposal.integration_status is EventEvidenceIntegrationStatus.PARTIAL
    assert result.proposal.evidence_layer_results == evidence_layer_results
    assert result.proposal.limitations == limitations
    assert len(result.model_calls) == 2
    assert len(result.tool_traces) == 1
    assert result.tool_traces[0].result_refs == [
        stable_contract_id(
            "event-evidence-integration-candidate-bundle",
            task.task_id,
            task.payload_checksum,
        ),
        "evidence:event:type",
        "evidence:event:weather",
        "res-prop-1",
    ]
    assert result.tool_traces[0].source_ids == ["source:event"]
    assert result.feedback is None
    assert result.failure_reason is None


def test_event_evidence_integration_agent_abstention_is_honest_insufficient() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration import run_event_evidence_integration_agent
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
    from aviation_agentic_ai.agent_system.construction_contracts import (
        EventEvidenceIntegrationStatus,
        EvidenceLayerResult,
        EvidenceLayerStatus,
    )
    from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
    from langchain_core.messages import AIMessage

    task = _assembly_task()
    selection_text = json.dumps(
        {
            "decision": "abstained",
            "candidate_bundle_id": stable_contract_id(
                "event-evidence-integration-candidate-bundle",
                task.task_id,
                task.payload_checksum,
            ),
            "selected_fact_ids": [],
            "selected_profile_gap_ids": [],
            "limitation": "The sealed evidence remains ambiguous.",
        },
        sort_keys=True,
    )
    evidence_layer_results = (
        EvidenceLayerResult(
            layer_id="core",
            status=EvidenceLayerStatus.OK,
            required_for_task=True,
            artifact_ids=("proposal-fact-1",),
        ),
    )
    scripted_model = _ScriptedAssemblyModel(
        [
            _assembly_tool_turn(),
            ToolModelTurn(
                message=AIMessage(content=selection_text),
                record=ModelCallRecord(
                    agent="event_evidence_integration",
                    raw_response=selection_text,
                    prompt_version="event-evidence-integration-v1",
                ),
            ),
        ]
    )

    result = run_event_evidence_integration_agent(
        task=task,
        binding=_binding(),
        tool_model_factory=lambda tools: scripted_model,
        evidence_layer_results=evidence_layer_results,
    )

    assert result.proposal.integration_status is EventEvidenceIntegrationStatus.INSUFFICIENT
    assert result.proposal.proposed_facts == ()
    assert result.proposal.evidence_layer_results[-1].layer_id == (
        "event_evidence_integration"
    )
    assert result.proposal.evidence_layer_results[-1].status is (
        EvidenceLayerStatus.INSUFFICIENT
    )
    assert result.failure_reason == "The sealed evidence remains ambiguous."
    assert len(result.model_calls) == 2
    assert len(result.tool_traces) == 1


@pytest.mark.parametrize("mutation", ("wrong_bundle", "extra_fact"))
def test_event_evidence_integration_agent_rejects_selection_outside_sealed_bundle(
    mutation: str,
) -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration import run_event_evidence_integration_agent
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
    from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
    from langchain_core.messages import AIMessage

    task = _assembly_task()
    bundle_id = stable_contract_id(
        "event-evidence-integration-candidate-bundle",
        task.task_id,
        task.payload_checksum,
    )
    selected_fact_ids = list(task.core_event_fact_ids)
    if mutation == "wrong_bundle":
        bundle_id = "bundle:outside-task"
    else:
        selected_fact_ids.append("proposal-fact-outside-task")
    selection_text = json.dumps(
        {
            "decision": "accepted",
            "candidate_bundle_id": bundle_id,
            "selected_fact_ids": selected_fact_ids,
            "selected_profile_gap_ids": [
                gap.proposal_item_id for gap in task.profile_gaps
            ],
            "limitation": None,
        },
        sort_keys=True,
    )
    scripted_model = _ScriptedAssemblyModel(
        [
            _assembly_tool_turn(),
            ToolModelTurn(
                message=AIMessage(content=selection_text),
                record=ModelCallRecord(
                    agent="event_evidence_integration",
                    raw_response=selection_text,
                    prompt_version="event-evidence-integration-v1",
                ),
            ),
        ]
    )

    result = run_event_evidence_integration_agent(
        task=task,
        binding=_binding(),
        tool_model_factory=lambda tools: scripted_model,
    )

    assert result.proposal.integration_status.value == "blocked"
    assert result.failure_reason is not None
    assert "candidate bundle" in result.failure_reason
    assert len(result.model_calls) == 2


def test_event_evidence_integration_initial_prompt_keeps_record_details_in_tool_bundle() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration import _base_messages

    task = _assembly_task()
    prompt = str(_base_messages(task, catalog_path="configs/prompts/tmi_event_agents_v1.yaml")[-1].content)

    assert "evidence:event:type" not in prompt
    assert "evidence:event:weather" not in prompt
    assert "res-prop-1" not in prompt
    assert "assoc-weather-1" not in prompt
    assert "obs-bts-1" not in prompt
    assert "REQUIREMENTS:controlled_facility" in prompt
    assert "PROFILE:profile-1" in prompt
    assert "GROUND STOP" not in prompt
    assert "cancelled_count" not in prompt


def test_event_evidence_integration_agent_malformed_output_blocks_without_repair() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration import run_event_evidence_integration_agent
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
    from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
    from langchain_core.messages import AIMessage

    task = _assembly_task()
    turn_1 = _assembly_tool_turn()
    turn_2 = ToolModelTurn(
        message=AIMessage(content="{not-json"),
        record=ModelCallRecord(
            agent="event_evidence_integration",
            raw_response="{not-json",
            prompt_version="event-evidence-integration-v1",
        ),
    )

    scripted_model = _ScriptedAssemblyModel([turn_1, turn_2])

    result = run_event_evidence_integration_agent(
        task=task,
        binding=_binding(),
        tool_model_factory=lambda tools: scripted_model,
    )

    assert result.proposal.integration_status.value == "blocked"
    assert result.proposal.proposed_facts == ()
    assert result.proposal.profile_gaps == ()
    assert result.proposal.evidence_bindings == ()
    assert result.proposal.resolution_proposal_ids == ()
    assert result.proposal.context_association_ids == ()
    assert result.proposal.source_snapshot_bindings == ()
    assert len(result.model_calls) == 2


def test_event_evidence_integration_agent_replay_stability() -> None:
    from aviation_agentic_ai.agent_system.event_evidence_integration import run_event_evidence_integration_agent
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
    from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
    from langchain_core.messages import AIMessage

    task = _assembly_task()

    def _make_model():
        turn_1 = _assembly_tool_turn()
        turn_2 = ToolModelTurn(
            message=AIMessage(content=_valid_proposal_text()),
            record=ModelCallRecord(
                agent="event_evidence_integration",
                raw_response=_valid_proposal_text(),
                prompt_version="event-evidence-integration-v1",
            ),
        )
        return _ScriptedAssemblyModel([turn_1, turn_2])

    res1 = run_event_evidence_integration_agent(task=task, binding=_binding(), tool_model_factory=lambda tools: _make_model())
    res2 = run_event_evidence_integration_agent(task=task, binding=_binding(), tool_model_factory=lambda tools: _make_model())

    assert res1.proposal.event_evidence_integration_proposal_id == res2.proposal.event_evidence_integration_proposal_id
    assert res1.proposal.payload_checksum == res2.proposal.payload_checksum


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
