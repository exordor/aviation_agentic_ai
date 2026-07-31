"""Strict dormant contracts for the three-Agent decision-case migration."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.construction_contracts import (
    CONSTRUCTION_CONTRACT_VERSION,
    EventEvidenceIntegrationStatus,
    AuthorityDefinitionEvidenceClaim,
    AuthorityRecordEvidenceClaim,
    CandidateBuildStatus,
    EventEvidenceIntegrationProposalFields,
    EventEvidenceIntegrationSelection,
    EventEvidenceIntegrationTaskFields,
    EventEvidenceFactProposal,
    EventEvidenceProfileGapProposal,
    EvidenceLayerResult,
    EvidenceLayerStatus,
    ConstraintCheck,
    ConstraintCheckStatus,
    ContractExecutionBinding,
    FactAssessment,
    FactDisposition,
    QueryStatus,
    RawResolutionCandidateRef,
    ResolutionCandidate,
    ResolutionCandidateAudit,
    ResolutionDecision,
    ResolutionProposalFields,
    ResolutionTaskFields,
    SourceSnapshotBinding,
    EventEvidenceIntegrationFeedbackFields,
    canonical_id_tuple_token,
    canonical_payload_bytes,
    canonicalize_contract_value,
    seal_event_evidence_integration_proposal,
    seal_event_evidence_integration_task,
    seal_resolution_proposal,
    seal_resolution_task,
    seal_event_evidence_integration_feedback,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.graph_patch import parse_event_evidence_integration_output


SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
STARTED = datetime(2026, 5, 19, 20, 15, tzinfo=UTC)


def _framed_id(namespace: str, *values: str) -> str:
    framed = bytearray()
    for value in (namespace, *values):
        encoded = value.encode()
        framed.extend(len(encoded).to_bytes(8, "big"))
        framed.extend(encoded)
    return f"{namespace}:{hashlib.sha256(framed).hexdigest()}"


def _binding(run_id: str = "run-1") -> ContractExecutionBinding:
    return ContractExecutionBinding(
        run_id=run_id,
        created_at=STARTED,
        tool_version="deterministic-resolution-v1",
    )


def _authority_claim(candidate_id: str = "facility:KJFK") -> AuthorityRecordEvidenceClaim:
    source_id = stable_contract_id(
        "authority-source",
        "facility",
        candidate_id,
        "NASR:APT:KJFK",
        SHA_B,
    )
    evidence_id = stable_contract_id(
        "authority-evidence",
        candidate_id,
        source_id,
        SHA_B,
        SHA_C,
    )
    return AuthorityRecordEvidenceClaim(
        evidence_id=evidence_id,
        candidate_id=candidate_id,
        evidence_kind="facility_record",
        authority_record_text="KJFK JOHN F KENNEDY INTL",
        authority_record_locator="APT.txt:KJFK",
        authority_record_sha256=SHA_A,
        authority_source_ref="NASR:APT:KJFK",
        source_id=source_id,
        source_snapshot_sha256=SHA_B,
        authority_artifact_key="nasr_zip",
        authority_artifact_sha256=SHA_C,
        manifest_artifact_key="nasr_manifest",
        manifest_artifact_sha256=SHA_A,
    )


def _authority_definition_claim(
    candidate_id: str = "term:GS",
) -> AuthorityDefinitionEvidenceClaim:
    source_id = stable_contract_id(
        "authority-source",
        "term",
        candidate_id,
        "PCG:GROUND_STOP",
        SHA_B,
    )
    evidence_id = stable_contract_id(
        "authority-evidence",
        candidate_id,
        source_id,
        SHA_B,
        SHA_C,
    )
    return AuthorityDefinitionEvidenceClaim(
        evidence_id=evidence_id,
        candidate_id=candidate_id,
        evidence_kind="term_definition",
        definition_text="The GS is a process that requires aircraft to remain.",
        definition_locator="PCG_G-3:GROUND_STOP",
        authority_source_ref="PCG:GROUND_STOP",
        source_id=source_id,
        source_snapshot_sha256=SHA_B,
        authority_artifact_key="pilot_controller_glossary",
        authority_artifact_sha256=SHA_C,
        definition_registry_artifact_key="authority_definition_seed",
        definition_registry_artifact_sha256=SHA_A,
        term_registry_artifact_key="term_seed",
        term_registry_artifact_sha256=SHA_C,
    )


def _check(
    candidate_id: str,
    kind: str,
    *,
    status: ConstraintCheckStatus = ConstraintCheckStatus.PASS,
    evidence_ids: tuple[str, ...] = (),
) -> ConstraintCheck:
    constraint_id = stable_contract_id(
        "resolution-constraint",
        candidate_id,
        kind,
        "controlled_facility",
        "airport",
        SHA_A,
    )
    return ConstraintCheck(
        constraint_id=constraint_id,
        candidate_id=candidate_id,
        check_kind=kind,
        status=status,
        reason_code=f"{kind}:{status.value}",
        evidence_ids=evidence_ids,
        schema_snapshot_sha256=SHA_A if kind == "schema_compatibility" else None,
    )


def _candidate(
    candidate_id: str = "facility:KJFK",
    *,
    schema_status: ConstraintCheckStatus = ConstraintCheckStatus.PASS,
) -> ResolutionCandidate:
    claim = _authority_claim(candidate_id)
    return ResolutionCandidate(
        candidate_id=candidate_id,
        candidate_kind="facility",
        preferred_label="JOHN F KENNEDY INTL",
        surface_form="JFK",
        candidate_type="airport",
        ontology_class_prefixed="atm:Airport",
        ontology_class_iri="https://example.test/atm#Airport",
        authority_evidence_ids=(claim.evidence_id,),
        constraint_checks=(
            _check(candidate_id, "structural_slot"),
            _check(candidate_id, "expected_entity_type"),
            _check(
                candidate_id,
                "schema_compatibility",
                status=schema_status,
                evidence_ids=(claim.evidence_id,),
            ),
        ),
    )


def _candidate_checksum(candidate: ResolutionCandidate) -> str:
    payload = canonicalize_contract_value(
        candidate.model_dump(mode="python", exclude_computed_fields=True)
    )
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode()
    return hashlib.sha256(encoded).hexdigest()


def _audit(candidate: ResolutionCandidate) -> ResolutionCandidateAudit:
    claim = _authority_claim(candidate.candidate_id)
    checksum = _candidate_checksum(candidate)
    audit_id = stable_contract_id(
        "resolution-candidate-audit",
        candidate.candidate_id,
        candidate.candidate_kind,
        "ok",
        checksum,
        claim.evidence_id,
        claim.source_id,
        "NONE",
        "NONE",
    )
    return ResolutionCandidateAudit(
        candidate_audit_id=audit_id,
        candidate_id=candidate.candidate_id,
        candidate_kind=candidate.candidate_kind,
        build_status=CandidateBuildStatus.OK,
        candidate_payload_checksum=checksum,
        evidence_id=claim.evidence_id,
        source_id=claim.source_id,
    )


def _resolution_fields() -> ResolutionTaskFields:
    candidate = _candidate()
    audit = _audit(candidate)
    claim = _authority_claim()
    task_id = stable_contract_id(
        "resolution-task",
        "run-1",
        "event-1",
        "JFK",
        "controlled_facility",
        "airport",
        canonical_id_tuple_token((audit.candidate_audit_id,), sort_values=True),
        "schema-slice-1",
        SHA_A,
    )
    return ResolutionTaskFields(
        task_id=task_id,
        run_id="run-1",
        event_id="event-1",
        mention="JFK",
        structural_slot="controlled_facility",
        expected_entity_type="airport",
        authority_domain_status=CandidateBuildStatus.OK,
        raw_candidate_refs=(
            RawResolutionCandidateRef(
                candidate_id=candidate.candidate_id,
                candidate_kind="facility",
            ),
        ),
        candidates=(candidate,),
        candidate_audits=(audit,),
        authority_evidence=(claim,),
        authority_source_ids=(claim.source_id,),
        ontology_constraints=("atm:Airport",),
        schema_slice_id="schema-slice-1",
        schema_snapshot_sha256=SHA_A,
        remaining_tool_budget=3,
    )


def _proposal_fields(task_id: str, task_checksum: str) -> ResolutionProposalFields:
    candidate = _candidate()
    claim = _authority_claim()
    proposal_id = stable_contract_id(
        "resolution-proposal",
        task_id,
        ResolutionDecision.ACCEPTED.value,
        candidate.candidate_id,
        canonical_id_tuple_token((), sort_values=True),
        canonical_id_tuple_token((claim.evidence_id,), sort_values=True),
    )
    return ResolutionProposalFields(
        resolution_proposal_id=proposal_id,
        run_id="run-1",
        task_id=task_id,
        task_payload_checksum=task_checksum,
        event_id="event-1",
        mention="JFK",
        structural_slot="controlled_facility",
        expected_entity_type="airport",
        selected_candidate_id=candidate.candidate_id,
        rejected_candidate_ids=(),
        decision=ResolutionDecision.ACCEPTED,
        supporting_evidence_claim_ids=(claim.evidence_id,),
        authority_source_ids=(claim.source_id,),
        tool_trace_ids=("trace-2", "trace-1"),
        limitation=None,
    )


def _assembly_task_fields(resolution_proposal_id: str) -> EventEvidenceIntegrationTaskFields:
    authority_claim = _authority_claim()
    event_id = "urn:aviation-agentic-ai:event:test:1"
    fact = EventEvidenceFactProposal(
        proposal_item_id="proposal-fact-1",
        subject_id=event_id,
        predicate_iri="rdf:type",
        object_kind="iri",
        object_value="atm:GroundStopTMI",
        evidence_claim_ids=("evidence:event:type",),
        validation_profile_id="profile-1",
    )
    gap = EventEvidenceProfileGapProposal(
        proposal_item_id="proposal-gap-1",
        event_id=event_id,
        field="impacting_condition",
        normalized_value="weather",
        evidence_claim_ids=("evidence:event:weather",),
        schema_mapping_reason_code="not_in_profile",
        validation_profile_id="profile-1",
    )
    selected = ("evidence:event:type", "evidence:event:weather")
    task_id = stable_contract_id(
        "event-evidence-integration-task",
        "run-1",
        event_id,
        canonical_id_tuple_token(("proposal-fact-1",), sort_values=True),
        canonical_id_tuple_token((resolution_proposal_id,), sort_values=True),
        canonical_id_tuple_token(selected, sort_values=True),
        "profile-1",
        "context-1",
        SHA_A,
    )
    return EventEvidenceIntegrationTaskFields(
        task_id=task_id,
        run_id="run-1",
        event_id=event_id,
        core_event_fact_ids=("proposal-fact-1",),
        resolution_proposal_ids=(resolution_proposal_id,),
        available_evidence_layer_ids=("layer:advisory",),
        required_event_slots=("event_type",),
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
                "selected_candidate_id": "facility:KJFK",
                "supporting_evidence_claim_ids": (authority_claim.evidence_id,),
                "authority_source_ids": (authority_claim.source_id,),
            },
        ),
        proposed_facts=(fact,),
        profile_gaps=(gap,),
        context_association_ids=("association:weather",),
        context_associations=(
            {
                "association_id": "association:weather",
                "run_id": "run-1",
                "event_id": event_id,
                "report_id": "weather-report-1",
                "facility_id": "facility:KJFK",
                "relation_type": "observation_during_operation",
                "selection_method": "latest eligible report",
                "relevant_times": {"observed_at": "2026-05-19T21:30:00Z"},
                "source_id": "source:weather",
                "source_snapshot_sha256": SHA_A,
                "causal_claim": False,
            },
        ),
        public_observation_ids=("observation:bts",),
        public_observations=(
            {
                "observation_id": "observation:bts",
                "run_id": "run-1",
                "event_id": event_id,
                "phase": "active",
                "metric_key": "cancelled_count",
                "value": 2,
                "derivation_id": "derivation:bts",
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
                source_id=authority_claim.source_id,
                source_family=SourceFamily.NASR_FACILITY,
                source_snapshot_sha256=SHA_B,
            ),
            SourceSnapshotBinding(
                source_id="source:bts",
                source_family=SourceFamily.BTS_ON_TIME,
                source_snapshot_sha256=SHA_B,
            ),
            SourceSnapshotBinding(
                source_id="source:event",
                source_family=SourceFamily.ATCSCC_ADVISORY,
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


@pytest.mark.parametrize(
    ("id_field", "record_field", "error_match"),
    (
        (
            "selected_evidence_claim_ids",
            "evidence_records",
            "evidence records must exactly match",
        ),
        (
            "resolution_proposal_ids",
            "resolution_records",
            "resolution records must exactly match",
        ),
        (
            "context_association_ids",
            "context_associations",
            "context associations must exactly match",
        ),
        (
            "public_observation_ids",
            "public_observations",
            "public observations must exactly match",
        ),
    ),
)
def test_event_evidence_integration_task_rejects_advertised_ids_without_typed_records(
    id_field: str,
    record_field: str,
    error_match: str,
) -> None:
    fields = _assembly_task_fields("resolution:accepted")
    assert getattr(fields, id_field)
    missing_records = fields.model_copy(update={record_field: ()})

    with pytest.raises(ValueError, match=error_match):
        seal_event_evidence_integration_task(fields=missing_records, binding=_binding())


@pytest.mark.parametrize(
    ("id_field", "record_field", "error_match"),
    (
        (
            "selected_evidence_claim_ids",
            "evidence_records",
            "evidence records must exactly match",
        ),
        (
            "resolution_proposal_ids",
            "resolution_records",
            "resolution records must exactly match",
        ),
        (
            "context_association_ids",
            "context_associations",
            "context associations must exactly match",
        ),
        (
            "public_observation_ids",
            "public_observations",
            "public observations must exactly match",
        ),
    ),
)
def test_event_evidence_integration_task_rejects_typed_records_without_advertised_ids(
    id_field: str,
    record_field: str,
    error_match: str,
) -> None:
    fields = _assembly_task_fields("resolution:accepted")
    assert getattr(fields, record_field)
    missing_ids = fields.model_copy(update={id_field: ()})

    with pytest.raises(ValueError, match=error_match):
        seal_event_evidence_integration_task(fields=missing_ids, binding=_binding())


def test_event_evidence_integration_task_rejects_unbound_authority_and_unrelated_sources() -> None:
    fields = _assembly_task_fields("resolution:accepted")
    authority_source_id = fields.resolution_records[0].authority_source_ids[0]
    without_authority = fields.model_copy(
        update={
            "source_snapshot_bindings": tuple(
                row
                for row in fields.source_snapshot_bindings
                if row.source_id != authority_source_id
            )
        }
    )
    with pytest.raises(ValueError, match="resolution authority source"):
        seal_event_evidence_integration_task(fields=without_authority, binding=_binding())

    unrelated = SourceSnapshotBinding(
        source_id="source:unrelated",
        source_family=SourceFamily.METAR,
        source_snapshot_sha256=SHA_C,
    )
    with_unrelated = fields.model_copy(
        update={
            "source_snapshot_bindings": tuple(
                sorted(
                    (*fields.source_snapshot_bindings, unrelated),
                    key=lambda row: row.source_id,
                )
            )
        }
    )
    with pytest.raises(ValueError, match="exactly match referenced record sources"):
        seal_event_evidence_integration_task(fields=with_unrelated, binding=_binding())


def _assembly_proposal_fields(
    task_id: str,
    task_checksum: str,
    resolution_proposal_id: str,
) -> EventEvidenceIntegrationProposalFields:
    task_fields = _assembly_task_fields(resolution_proposal_id)
    proposal_id = stable_contract_id(
        "event-evidence-integration-proposal",
        task_id,
        task_checksum,
        EventEvidenceIntegrationStatus.OK.value,
        canonical_id_tuple_token(
            tuple(item.proposal_item_id for item in task_fields.proposed_facts),
            sort_values=True,
        ),
        canonical_id_tuple_token(
            tuple(item.proposal_item_id for item in task_fields.profile_gaps),
            sort_values=True,
        ),
        canonical_id_tuple_token((resolution_proposal_id,), sort_values=True),
    )
    return EventEvidenceIntegrationProposalFields(
        event_evidence_integration_proposal_id=proposal_id,
        run_id="run-1",
        task_id=task_id,
        task_payload_checksum=task_checksum,
        event_id="urn:aviation-agentic-ai:event:test:1",
        integration_status=EventEvidenceIntegrationStatus.OK,
        evidence_layer_results=(
            EvidenceLayerResult(
                layer_id="core",
                status=EvidenceLayerStatus.OK,
                required_for_task=True,
                artifact_ids=("proposal-fact-1",),
            ),
        ),
        proposed_facts=task_fields.proposed_facts,
        evidence_bindings=task_fields.selected_evidence_claim_ids,
        resolution_proposal_ids=(resolution_proposal_id,),
        context_association_ids=(),
        profile_gaps=task_fields.profile_gaps,
        omitted_slots=(),
        limitations=(),
        tool_trace_ids=("assembly-trace-2", "assembly-trace-1"),
        source_snapshot_bindings=task_fields.source_snapshot_bindings,
        revision_count=0,
    )


def test_enum_values_and_strict_frozen_surface() -> None:
    assert CONSTRUCTION_CONTRACT_VERSION == "tmi-event-construction-contracts-v1"
    assert {item.value for item in ResolutionDecision} == {
        "accepted",
        "abstained",
        "insufficient",
        "blocked",
    }
    assert {item.value for item in EventEvidenceIntegrationStatus} == {
        "ok",
        "partial",
        "insufficient",
        "blocked",
    }
    assert {item.value for item in QueryStatus} == {
        "ok",
        "insufficient",
        "blocked",
        "unsupported",
    }
    binding = _binding()
    with pytest.raises(ValidationError):
        ContractExecutionBinding(
            run_id="run-1",
            created_at=STARTED,
            tool_version="v1",
            unexpected=True,
        )
    with pytest.raises(ValidationError):
        binding.run_id = "other"


def test_stable_ids_are_length_framed_and_tuple_tokens_are_unambiguous() -> None:
    assert stable_contract_id("ns", "a|b", "c") == _framed_id("ns", "a|b", "c")
    assert stable_contract_id("ns", "a", "b|c") != stable_contract_id(
        "ns", "a|b", "c"
    )
    assert canonical_id_tuple_token(("β", "a"), sort_values=True) == '["a","β"]'
    assert canonical_id_tuple_token(("β", "a"), sort_values=False) == '["β","a"]'
    with pytest.raises(ValueError, match="duplicate"):
        canonical_id_tuple_token(("a", "a"), sort_values=True)
    with pytest.raises(TypeError):
        stable_contract_id("ns", 3)  # type: ignore[arg-type]


def test_authority_source_ids_bind_candidate_kind_and_canonical_source_content() -> None:
    facility_claim = _authority_claim()
    term_claim = _authority_definition_claim()
    assert facility_claim.source_id == stable_contract_id(
        "authority-source",
        "facility",
        facility_claim.candidate_id,
        facility_claim.authority_source_ref,
        facility_claim.source_snapshot_sha256,
    )
    assert term_claim.source_id == stable_contract_id(
        "authority-source",
        "term",
        term_claim.candidate_id,
        term_claim.authority_source_ref,
        term_claim.source_snapshot_sha256,
    )
    changed_raw_record = AuthorityRecordEvidenceClaim.model_validate(
        {
            **facility_claim.model_dump(mode="python"),
            "authority_record_sha256": SHA_C,
        }
    )
    assert changed_raw_record.source_id == facility_claim.source_id


def test_canonicalization_normalizes_aware_datetime_and_rejects_unsafe_values() -> None:
    plus_two = timezone(timedelta(hours=2))
    assert canonicalize_contract_value(
        datetime(2026, 5, 19, 22, 15, tzinfo=plus_two)
    ) == "2026-05-19T20:15:00.000000Z"
    for value in (
        datetime(2026, 5, 19, 20, 15),
        float("nan"),
        float("inf"),
        b"bytes",
        {"not-a-json-set"},
        object(),
    ):
        with pytest.raises((TypeError, ValueError)):
            canonicalize_contract_value(value)


def test_binding_normalizes_to_utc_and_requires_prompt_or_tool_version() -> None:
    plus_two = timezone(timedelta(hours=2))
    binding = ContractExecutionBinding(
        run_id="run-1",
        created_at=datetime(2026, 5, 19, 22, 15, tzinfo=plus_two),
        prompt_version="prompt-v1",
    )
    assert binding.created_at == STARTED
    assert binding.created_at.tzinfo is UTC
    with pytest.raises(ValidationError):
        ContractExecutionBinding(run_id="run-1", created_at=STARTED)
    with pytest.raises(ValidationError):
        ContractExecutionBinding(
            run_id="run-1",
            created_at=datetime(2026, 5, 19, 20, 15),
            tool_version="v1",
        )


def test_resolution_sealing_binds_checksum_and_preserves_ordered_trace() -> None:
    task = seal_resolution_task(fields=_resolution_fields(), binding=_binding())
    proposal = seal_resolution_proposal(
        task=task,
        fields=_proposal_fields(task.task_id, task.payload_checksum),
        binding=_binding(),
    )
    assert task.created_at == STARTED
    assert task.contract_version == CONSTRUCTION_CONTRACT_VERSION
    assert proposal.task_payload_checksum == task.payload_checksum
    assert proposal.tool_trace_ids == ("trace-2", "trace-1")
    assert hashlib.sha256(
        canonical_payload_bytes(type(task), _resolution_fields(), _binding())
    ).hexdigest() == task.payload_checksum
    with pytest.raises(ValidationError):
        type(task).model_validate(
            {
                **task.model_dump(
                    mode="python",
                    exclude_computed_fields=True,
                ),
                "payload_checksum": SHA_B,
            }
        )


def test_resolution_candidate_eligibility_is_computed_and_cannot_be_injected() -> None:
    failed = _candidate(schema_status=ConstraintCheckStatus.FAIL)
    assert failed.eligible is False
    with pytest.raises(ValidationError):
        ResolutionCandidate.model_validate(
            {
                **failed.model_dump(mode="python", exclude_computed_fields=True),
                "eligible": True,
            }
        )
    duplicate_check = failed.model_dump(mode="python", exclude_computed_fields=True)
    duplicate_check["constraint_checks"] = (
        failed.constraint_checks[0],
        failed.constraint_checks[0],
        failed.constraint_checks[2],
    )
    with pytest.raises(ValidationError):
        ResolutionCandidate.model_validate(duplicate_check)


def test_resolution_task_rejects_omitted_raw_audit_and_foreign_evidence() -> None:
    fields = _resolution_fields()
    with pytest.raises(ValidationError):
        ResolutionTaskFields.model_validate(
            {**fields.model_dump(mode="python"), "candidate_audits": ()}
        )
    claim = _authority_claim("facility:KLGA")
    with pytest.raises(ValidationError):
        ResolutionTaskFields.model_validate(
            {
                **fields.model_dump(mode="python"),
                "authority_evidence": (claim,),
                "authority_source_ids": (claim.source_id,),
            }
        )


def test_resolution_task_rejects_stale_candidate_checksum_and_schema_checksum() -> None:
    fields = _resolution_fields()
    stale = fields.candidate_audits[0].model_copy(
        update={"candidate_payload_checksum": SHA_C}
    )
    with pytest.raises(ValidationError):
        ResolutionTaskFields.model_validate(
            {**fields.model_dump(mode="python"), "candidate_audits": (stale,)}
        )
    candidate = fields.candidates[0]
    checks = list(candidate.constraint_checks)
    checks[-1] = checks[-1].model_copy(update={"schema_snapshot_sha256": SHA_B})
    bad_candidate = candidate.model_copy(update={"constraint_checks": tuple(checks)})
    with pytest.raises(ValidationError):
        ResolutionTaskFields.model_validate(
            {**fields.model_dump(mode="python"), "candidates": (bad_candidate,)}
        )


def test_resolution_builder_rejects_task_state_substitution_and_foreign_support() -> None:
    task = seal_resolution_task(fields=_resolution_fields(), binding=_binding())
    stale = _proposal_fields(task.task_id, SHA_C)
    with pytest.raises(ValueError, match="task payload checksum"):
        seal_resolution_proposal(task=task, fields=stale, binding=_binding())
    proposal = _proposal_fields(task.task_id, task.payload_checksum)
    foreign = proposal.model_copy(
        update={"supporting_evidence_claim_ids": ("foreign-evidence",)}
    )
    with pytest.raises(ValueError, match="supporting evidence"):
        seal_resolution_proposal(task=task, fields=foreign, binding=_binding())


def test_pre_enumeration_blocked_domain_is_distinct_from_empty_catalog() -> None:
    blocked_fields = _resolution_fields().model_copy(
        update={
            "authority_domain_status": CandidateBuildStatus.BLOCKED,
            "authority_domain_reason_code": "authority_unreadable",
            "authority_domain_error_id": "error:stable",
            "raw_candidate_refs": (),
            "candidates": (),
            "candidate_audits": (),
            "authority_evidence": (),
            "authority_source_ids": (),
        }
    )
    blocked_fields = blocked_fields.model_copy(
        update={
            "task_id": stable_contract_id(
                "resolution-task",
                "run-1",
                "event-1",
                "JFK",
                "controlled_facility",
                "airport",
                canonical_id_tuple_token((), sort_values=True),
                "schema-slice-1",
                SHA_A,
            )
        }
    )
    blocked = seal_resolution_task(fields=blocked_fields, binding=_binding())
    empty_fields = blocked_fields.model_copy(
        update={
            "authority_domain_status": CandidateBuildStatus.INSUFFICIENT,
            "authority_domain_reason_code": "empty_catalog",
            "authority_domain_error_id": None,
        }
    )
    empty = seal_resolution_task(fields=empty_fields, binding=_binding())
    assert blocked.task_id == empty.task_id
    assert blocked.payload_checksum != empty.payload_checksum


def test_assembly_sealing_enforces_support_profile_and_status_rollup() -> None:
    resolution_task = seal_resolution_task(fields=_resolution_fields(), binding=_binding())
    resolution = seal_resolution_proposal(
        task=resolution_task,
        fields=_proposal_fields(
            resolution_task.task_id,
            resolution_task.payload_checksum,
        ),
        binding=_binding(),
    )
    task = seal_event_evidence_integration_task(
        fields=_assembly_task_fields(resolution.resolution_proposal_id),
        binding=_binding(),
    )
    proposal = seal_event_evidence_integration_proposal(
        task=task,
        fields=_assembly_proposal_fields(
            task.task_id,
            task.payload_checksum,
            resolution.resolution_proposal_id,
        ),
        binding=_binding(),
    )
    assert proposal.tool_trace_ids == ("assembly-trace-2", "assembly-trace-1")
    required_missing = proposal.evidence_layer_results[0].model_copy(
        update={
            "status": EvidenceLayerStatus.INSUFFICIENT,
            "artifact_ids": (),
            "missing_reason_code": "missing",
        }
    )
    bad = _assembly_proposal_fields(
        task.task_id,
        task.payload_checksum,
        resolution.resolution_proposal_id,
    ).model_copy(update={"evidence_layer_results": (required_missing,)})
    with pytest.raises(ValueError, match="required"):
        seal_event_evidence_integration_proposal(task=task, fields=bad, binding=_binding())


def test_assembly_task_core_ids_must_match_proposed_fact_ids() -> None:
    fields = _assembly_task_fields("resolution-proposal-1")
    mismatched_core_ids = ("fact:foreign",)
    mismatched = fields.model_copy(
        update={
            "core_event_fact_ids": mismatched_core_ids,
            "task_id": stable_contract_id(
                "event-evidence-integration-task",
                fields.run_id,
                fields.event_id,
                canonical_id_tuple_token(
                    mismatched_core_ids,
                    sort_values=True,
                ),
                canonical_id_tuple_token(
                    fields.resolution_proposal_ids,
                    sort_values=True,
                ),
                canonical_id_tuple_token(
                    fields.selected_evidence_claim_ids,
                    sort_values=True,
                ),
                fields.schema_profile_id,
                fields.schema_context_id,
                fields.schema_snapshot_sha256,
            ),
        }
    )

    with pytest.raises(ValueError, match="core event fact IDs"):
        seal_event_evidence_integration_task(fields=mismatched, binding=_binding())


def test_event_evidence_integration_task_id_must_name_its_formal_event() -> None:
    fields = _assembly_task_fields("resolution-proposal-1")
    foreign_event_id = "urn:aviation-agentic-ai:event:foreign"
    mismatched = fields.model_copy(
        update={
            "event_id": foreign_event_id,
            "task_id": stable_contract_id(
                "event-evidence-integration-task",
                fields.run_id,
                foreign_event_id,
                canonical_id_tuple_token(
                    fields.core_event_fact_ids,
                    sort_values=True,
                ),
                canonical_id_tuple_token(
                    fields.resolution_proposal_ids,
                    sort_values=True,
                ),
                canonical_id_tuple_token(
                    fields.selected_evidence_claim_ids,
                    sort_values=True,
                ),
                fields.schema_profile_id,
                fields.schema_context_id,
                fields.schema_snapshot_sha256,
            ),
        }
    )

    with pytest.raises(ValueError, match="formal event"):
        seal_event_evidence_integration_task(fields=mismatched, binding=_binding())


def test_assembly_task_binds_context_associations_to_one_task_event() -> None:
    fields = _assembly_task_fields("resolution-proposal-1")
    association = fields.context_associations[0]
    gap = fields.profile_gaps[0]
    invalid_fields = (
        fields.model_copy(
            update={
                "context_associations": (
                    association.model_copy(update={"run_id": "run-foreign"}),
                ),
            }
        ),
        fields.model_copy(
            update={
                "context_associations": (
                    association.model_copy(update={"event_id": "event-foreign"}),
                ),
            }
        ),
        fields.model_copy(
            update={
                "profile_gaps": (
                    gap.model_copy(update={"event_id": "event-foreign"}),
                ),
            }
        ),
    )

    for invalid in invalid_fields:
        with pytest.raises(ValueError, match="task event ownership"):
            seal_event_evidence_integration_task(fields=invalid, binding=_binding())

    compact_event_id = "evt:canonical-event"
    absolute_event_id = "urn:aviation-agentic-ai:event:canonical-event"
    canonicalized = fields.model_copy(
        update={
            "event_id": absolute_event_id,
            "task_id": stable_contract_id(
                "event-evidence-integration-task",
                fields.run_id,
                absolute_event_id,
                canonical_id_tuple_token(
                    fields.core_event_fact_ids,
                    sort_values=True,
                ),
                canonical_id_tuple_token(
                    fields.resolution_proposal_ids,
                    sort_values=True,
                ),
                canonical_id_tuple_token(
                    fields.selected_evidence_claim_ids,
                    sort_values=True,
                ),
                fields.schema_profile_id,
                fields.schema_context_id,
                fields.schema_snapshot_sha256,
            ),
            "proposed_facts": tuple(
                fact.model_copy(update={"subject_id": compact_event_id})
                for fact in fields.proposed_facts
            ),
            "profile_gaps": tuple(
                row.model_copy(update={"event_id": compact_event_id})
                for row in fields.profile_gaps
            ),
            "context_associations": (
                association.model_copy(update={"event_id": absolute_event_id}),
            ),
            "public_observations": tuple(
                row.model_copy(update={"event_id": absolute_event_id})
                for row in fields.public_observations
            ),
        }
    )

    sealed = seal_event_evidence_integration_task(fields=canonicalized, binding=_binding())

    assert sealed.context_associations[0].event_id == absolute_event_id


def test_assembly_task_binds_public_observations_to_one_task_event() -> None:
    fields = _assembly_task_fields("resolution-proposal-1")
    observation = fields.public_observations[0]

    invalid_fields = (
        fields.model_copy(
            update={
                "public_observations": (
                    observation.model_copy(update={"run_id": "run-foreign"}),
                ),
            }
        ),
        fields.model_copy(
            update={
                "public_observations": (
                    observation.model_copy(update={"event_id": "event-foreign"}),
                ),
            }
        ),
    )

    for invalid in invalid_fields:
        with pytest.raises(ValueError, match="public observation task event ownership"):
            seal_event_evidence_integration_task(fields=invalid, binding=_binding())


def test_fact_support_profile_gap_support_and_disposition_are_strict() -> None:
    with pytest.raises(ValidationError):
        EventEvidenceFactProposal(
            proposal_item_id="fact",
            subject_id="event",
            predicate_iri="rdf:type",
            object_kind="iri",
            object_value="atm:TMI",
            validation_profile_id="profile",
        )
    with pytest.raises(ValidationError):
        EventEvidenceProfileGapProposal(
            proposal_item_id="gap",
            event_id="event",
            field="reason",
            normalized_value="weather",
            evidence_claim_ids=(),
            schema_mapping_reason_code="missing_mapping",
            validation_profile_id="profile",
        )
    with pytest.raises(ValidationError):
        FactAssessment(
            assessment_id="assessment",
            proposal_item_id="fact",
            disposition=FactDisposition.FORMAL_FACT,
            published_fact_id="published",
            profile_gap_id="gap",
        )


def test_validation_feedback_binds_exact_proposal_and_affected_item() -> None:
    resolution_task = seal_resolution_task(fields=_resolution_fields(), binding=_binding())
    resolution = seal_resolution_proposal(
        task=resolution_task,
        fields=_proposal_fields(
            resolution_task.task_id,
            resolution_task.payload_checksum,
        ),
        binding=_binding(),
    )
    task = seal_event_evidence_integration_task(
        fields=_assembly_task_fields(resolution.resolution_proposal_id),
        binding=_binding(),
    )
    proposal = seal_event_evidence_integration_proposal(
        task=task,
        fields=_assembly_proposal_fields(
            task.task_id,
            task.payload_checksum,
            resolution.resolution_proposal_id,
        ),
        binding=_binding(),
    )
    corrections = ("replace-object", "omit-item")
    feedback_id = stable_contract_id(
        "validation-feedback",
        task.task_id,
        proposal.payload_checksum,
        "proposal-fact-1",
        "invalid_object",
        "constraint-1",
        canonical_id_tuple_token(corrections, sort_values=False),
        canonical_id_tuple_token(("evidence:event:type",), sort_values=True),
    )
    fields = EventEvidenceIntegrationFeedbackFields(
        feedback_id=feedback_id,
        run_id="run-1",
        task_id=task.task_id,
        event_id=task.event_id,
        proposal_payload_checksum=proposal.payload_checksum,
        violation_code="invalid_object",
        constraint_id="constraint-1",
        affected_proposal_item_id="proposal-fact-1",
        repairable=True,
        allowed_corrections=corrections,
        evidence_ids=("evidence:event:type",),
    )
    feedback = seal_event_evidence_integration_feedback(
        task=task,
        proposal=proposal,
        fields=fields,
        binding=_binding(),
    )
    assert feedback.allowed_corrections == corrections
    with pytest.raises(ValueError, match="affected proposal item"):
        seal_event_evidence_integration_feedback(
            task=task,
            proposal=proposal,
            fields=fields.model_copy(
                update={"affected_proposal_item_id": "foreign-item"}
            ),
            binding=_binding(),
        )


def test_event_evidence_integration_parser_accepts_only_json_rows_and_none_marker() -> None:
    raw = (
        "GRAPH_PATCH\n"
        '{"proposal_item_id":"f1","subject_id":"event-1",'
        '"predicate_iri":"rdf:type","object_kind":"iri",'
        '"object_value":"atm:GroundStopTMI",'
        '"evidence_claim_ids":["e1"],"derivation_ids":[],'
        '"validation_profile_id":"profile-1"}\n'
        "PROFILE_GAPS\n"
        '{"proposal_item_id":"g1","event_id":"event-1","field":"reason",'
        '"normalized_value":"weather","evidence_claim_ids":["e2"],'
        '"schema_mapping_reason_code":"not_in_profile",'
        '"validation_profile_id":"profile-1"}'
    )
    parsed = parse_event_evidence_integration_output(
        raw,
        allowed_validation_profile_ids=frozenset({"profile-1"}),
    )
    assert [item.proposal_item_id for item in parsed.proposed_facts] == ["f1"]
    assert [item.proposal_item_id for item in parsed.profile_gaps] == ["g1"]
    empty = parse_event_evidence_integration_output(
        "GRAPH_PATCH\nNONE\nPROFILE_GAPS\nNONE",
        allowed_validation_profile_ids=frozenset({"profile-1"}),
    )
    assert empty.proposed_facts == ()
    assert empty.profile_gaps == ()


def test_event_evidence_integration_selection_accepts_compact_selected_ids() -> None:
    selection = EventEvidenceIntegrationSelection(
        decision="accepted",
        candidate_bundle_id="candidate-bundle:1",
        selected_fact_ids=("fact:1", "fact:2"),
        selected_profile_gap_ids=("gap:1",),
    )

    assert selection.decision == "accepted"
    assert selection.selected_fact_ids == ("fact:1", "fact:2")
    assert selection.selected_profile_gap_ids == ("gap:1",)
    assert selection.limitation is None


def test_event_evidence_integration_selection_requires_consistent_terminal_shape() -> None:
    accepted_failures = (
        {
            "decision": "accepted",
            "candidate_bundle_id": "candidate-bundle:1",
        },
        {
            "decision": "accepted",
            "candidate_bundle_id": "candidate-bundle:1",
            "selected_fact_ids": ("fact:1",),
            "limitation": "Unexpected limitation.",
        },
        {
            "decision": "accepted",
            "candidate_bundle_id": "candidate-bundle:1",
            "selected_fact_ids": ("fact:1", "fact:1"),
        },
    )
    for payload in accepted_failures:
        with pytest.raises(ValidationError):
            EventEvidenceIntegrationSelection.model_validate(payload)

    abstained = EventEvidenceIntegrationSelection(
        decision="abstained",
        candidate_bundle_id="candidate-bundle:1",
        limitation="The source evidence does not support the sealed candidate.",
    )
    assert abstained.selected_fact_ids == ()
    assert abstained.selected_profile_gap_ids == ()

    with pytest.raises(ValidationError):
        EventEvidenceIntegrationSelection(
            decision="abstained",
            candidate_bundle_id="candidate-bundle:1",
        )
    with pytest.raises(ValidationError):
        EventEvidenceIntegrationSelection(
            decision="abstained",
            candidate_bundle_id="candidate-bundle:1",
            selected_fact_ids=("fact:1",),
            limitation="Cannot accept.",
        )


@pytest.mark.parametrize(
    "raw",
    [
        "GRAPH_PATCH\nevent | rdf:type | atm:TMI | e1\nPROFILE_GAPS\nNONE",
        "prose before sections\nGRAPH_PATCH\nNONE\nPROFILE_GAPS\nNONE",
        "GRAPH_PATCH\nPROFILE_GAPS\nNONE",
        (
            "GRAPH_PATCH\n"
            '{"proposal_item_id":"f1","subject_id":"event","predicate_iri":"p",'
            '"object_kind":"wrong","object_value":"v","evidence_claim_ids":["e1"],'
            '"validation_profile_id":"profile-1"}\nPROFILE_GAPS\nNONE'
        ),
        (
            "GRAPH_PATCH\n"
            '{"proposal_item_id":"f1","subject_id":"event","predicate_iri":"p",'
            '"object_kind":"iri","object_value":"v","evidence_claim_ids":[],'
            '"validation_profile_id":"profile-1"}\nPROFILE_GAPS\nNONE'
        ),
        (
            "GRAPH_PATCH\n"
            '{"proposal_item_id":"f1","subject_id":"event","predicate_iri":"p",'
            '"object_kind":"iri","object_value":"v","evidence_claim_ids":["e1"],'
            '"validation_profile_id":"foreign"}\nPROFILE_GAPS\nNONE'
        ),
        (
            "GRAPH_PATCH\n"
            '{"proposal_item_id":"same","subject_id":"event","predicate_iri":"p",'
            '"object_kind":"iri","object_value":"v","evidence_claim_ids":["e1"],'
            '"validation_profile_id":"profile-1"}\nPROFILE_GAPS\n'
            '{"proposal_item_id":"same","event_id":"event","field":"reason",'
            '"normalized_value":"weather","evidence_claim_ids":["e2"],'
            '"schema_mapping_reason_code":"gap",'
            '"validation_profile_id":"profile-1"}'
        ),
    ],
)
def test_event_evidence_integration_parser_fails_closed(raw: str) -> None:
    with pytest.raises(ValueError):
        parse_event_evidence_integration_output(
            raw,
            allowed_validation_profile_ids=frozenset({"profile-1"}),
        )


def test_event_evidence_integration_parser_requires_nonempty_profile_allowlist() -> None:
    with pytest.raises(ValueError, match="allowed_validation_profile_ids"):
        parse_event_evidence_integration_output(
            "GRAPH_PATCH\nNONE\nPROFILE_GAPS\nNONE",
            allowed_validation_profile_ids=frozenset(),
        )
