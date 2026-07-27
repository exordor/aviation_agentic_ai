"""Candidate-bounded read-only tools for semantic resolution."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

import pytest

from aviation_agentic_ai.agent_system.decision_case_contracts import (
    AuthorityRecordEvidenceClaim,
    CandidateBuildStatus,
    ConstraintCheck,
    ConstraintCheckStatus,
    ContractExecutionBinding,
    RawResolutionCandidateRef,
    ResolutionCandidate,
    ResolutionCandidateAudit,
    ResolutionTaskFields,
    canonical_id_tuple_token,
    canonicalize_contract_value,
    seal_resolution_task,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.resolution_tools import (
    ResolutionToolError,
    ResolutionToolGateway,
    build_resolution_tools,
)


SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
NOW = datetime(2026, 7, 27, 12, 0, tzinfo=UTC)


def _authority_claim(candidate_id: str) -> AuthorityRecordEvidenceClaim:
    source_id = stable_contract_id(
        "authority-source",
        "facility",
        candidate_id,
        f"NASR:APT:{candidate_id.rsplit(':', maxsplit=1)[-1]}",
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
        authority_record_text=f"{candidate_id} authority record",
        authority_record_locator=f"APT.txt:{candidate_id}",
        authority_record_sha256=SHA_A,
        authority_source_ref=f"NASR:APT:{candidate_id.rsplit(':', maxsplit=1)[-1]}",
        source_id=source_id,
        source_snapshot_sha256=SHA_B,
        authority_artifact_key="nasr_zip",
        authority_artifact_sha256=SHA_C,
        manifest_artifact_key="nasr_manifest",
        manifest_artifact_sha256=SHA_A,
    )


def _check(
    candidate_id: str,
    check_kind: str,
    *,
    status: ConstraintCheckStatus = ConstraintCheckStatus.PASS,
    evidence_ids: tuple[str, ...] = (),
) -> ConstraintCheck:
    return ConstraintCheck(
        constraint_id=stable_contract_id(
            "resolution-constraint",
            candidate_id,
            check_kind,
            "controlled_facility",
            "airport",
            SHA_A,
        ),
        candidate_id=candidate_id,
        check_kind=check_kind,
        status=status,
        reason_code=f"{check_kind}:{status.value}",
        evidence_ids=evidence_ids,
        schema_snapshot_sha256=SHA_A
        if check_kind == "schema_compatibility"
        else None,
    )


def _candidate(
    candidate_id: str,
    *,
    eligible: bool = True,
) -> ResolutionCandidate:
    claim = _authority_claim(candidate_id)
    schema_status = (
        ConstraintCheckStatus.PASS if eligible else ConstraintCheckStatus.FAIL
    )
    return ResolutionCandidate(
        candidate_id=candidate_id,
        candidate_kind="facility",
        preferred_label=f"{candidate_id} AIRPORT",
        surface_form=candidate_id.rsplit(":", maxsplit=1)[-1],
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
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode()
    ).hexdigest()


def _audit(candidate: ResolutionCandidate) -> ResolutionCandidateAudit:
    claim = _authority_claim(candidate.candidate_id)
    checksum = _candidate_checksum(candidate)
    return ResolutionCandidateAudit(
        candidate_audit_id=stable_contract_id(
            "resolution-candidate-audit",
            candidate.candidate_id,
            candidate.candidate_kind,
            "ok",
            checksum,
            claim.evidence_id,
            claim.source_id,
            "NONE",
            "NONE",
        ),
        candidate_id=candidate.candidate_id,
        candidate_kind=candidate.candidate_kind,
        build_status=CandidateBuildStatus.OK,
        candidate_payload_checksum=checksum,
        evidence_id=claim.evidence_id,
        source_id=claim.source_id,
    )


def _task(*, candidate_ids: tuple[str, ...] = ("facility:KJFK", "facility:KBOS")):
    candidates = tuple(
        _candidate(candidate_id, eligible=candidate_id != "facility:KBOS")
        for candidate_id in sorted(candidate_ids)
    )
    audits = tuple(sorted((_audit(candidate) for candidate in candidates), key=lambda row: row.candidate_audit_id))
    claims = tuple(sorted((_authority_claim(candidate.candidate_id) for candidate in candidates), key=lambda row: row.evidence_id))
    task_id = stable_contract_id(
        "resolution-task",
        "run-1",
        "event-1",
        "JFK",
        "controlled_facility",
        "airport",
        canonical_id_tuple_token(
            tuple(sorted(audit.candidate_audit_id for audit in audits)),
            sort_values=True,
        ),
        "schema-slice-1",
        SHA_A,
    )
    return seal_resolution_task(
        fields=ResolutionTaskFields(
            task_id=task_id,
            run_id="run-1",
            event_id="event-1",
            mention="JFK",
            structural_slot="controlled_facility",
            expected_entity_type="airport",
            authority_domain_status=CandidateBuildStatus.OK,
            raw_candidate_refs=tuple(
                RawResolutionCandidateRef(
                    candidate_id=candidate.candidate_id,
                    candidate_kind=candidate.candidate_kind,
                )
                for candidate in candidates
            ),
            candidates=candidates,
            candidate_audits=audits,
            authority_evidence=claims,
            authority_source_ids=tuple(sorted(claim.source_id for claim in claims)),
            ontology_constraints=("atm:Airport",),
            schema_slice_id="schema-slice-1",
            schema_snapshot_sha256=SHA_A,
            remaining_tool_budget=3,
        ),
        binding=ContractExecutionBinding(
            run_id="run-1",
            created_at=NOW,
            tool_version="semantic-resolution-tools-v1",
        ),
    )


def test_resolution_tools_expose_only_the_five_registered_names():
    tools = build_resolution_tools(ResolutionToolGateway(task=_task()))

    assert [tool.name for tool in tools] == [
        "get_resolution_candidates",
        "get_authority_record",
        "get_ontology_context",
        "check_candidate_constraints",
        "compare_candidate_evidence",
    ]


def test_resolution_candidates_return_only_eligible_task_owned_candidates():
    result = ResolutionToolGateway(task=_task()).get_resolution_candidates()

    assert result.candidate_ids == ["facility:KJFK"]
    assert [item.model_dump() for item in result.items] == [
        {
            "candidate_id": "facility:KJFK",
            "candidate_kind": "facility",
            "candidate_type": "airport",
            "ontology_class_iri": "https://example.test/atm#Airport",
            "ontology_class_prefixed": "atm:Airport",
        }
    ]


def test_authority_record_projects_exact_task_owned_evidence_and_source():
    task = _task()
    claim = next(
        claim
        for claim in task.authority_evidence
        if claim.candidate_id == "facility:KJFK"
    )

    result = ResolutionToolGateway(task=task).get_authority_record(
        candidate_id="facility:KJFK"
    )

    assert result.authority_evidence_ids == [claim.evidence_id]
    assert result.authority_source_ids == [claim.source_id]
    assert [item.model_dump() for item in result.items] == [
        {
            "authority_record_locator": "APT.txt:facility:KJFK",
            "authority_record_text": "facility:KJFK authority record",
            "candidate_id": "facility:KJFK",
            "evidence_id": claim.evidence_id,
            "evidence_kind": "facility_record",
            "source_id": claim.source_id,
        }
    ]


@pytest.mark.parametrize(
    ("candidate_ids", "message"),
    [
        (["facility:KXXX"], "outside the sealed task"),
        (["facility:KJFK", "facility:KJFK"], "duplicate candidate IDs"),
        (["facility:KBOS"], "ineligible candidate IDs"),
    ],
)
def test_candidate_requests_fail_closed_outside_the_eligible_task_scope(
    candidate_ids, message
):
    gateway = ResolutionToolGateway(task=_task())

    with pytest.raises(ResolutionToolError, match=message):
        gateway.get_ontology_context(candidate_ids=candidate_ids)


def test_cross_task_candidate_request_fails_closed():
    other_task = _task(candidate_ids=("facility:KORD",))
    gateway = ResolutionToolGateway(task=_task())

    with pytest.raises(ResolutionToolError, match="outside the sealed task"):
        gateway.get_authority_record(
            candidate_id=other_task.candidates[0].candidate_id
        )


def test_source_mismatched_task_is_refused_before_candidate_reads():
    task = _task()
    source_mismatched = task.model_copy(update={"authority_source_ids": ()})

    with pytest.raises(ResolutionToolError, match="source is not task-owned"):
        ResolutionToolGateway(task=source_mismatched)


def test_constraints_and_schema_context_are_typed_task_observations():
    task = _task()
    candidate = next(
        candidate
        for candidate in task.candidates
        if candidate.candidate_id == "facility:KJFK"
    )
    gateway = ResolutionToolGateway(task=task)

    constraint_result = gateway.check_candidate_constraints(
        candidate_ids=[candidate.candidate_id]
    )
    ontology_result = gateway.get_ontology_context(
        candidate_ids=[candidate.candidate_id]
    )

    assert constraint_result.constraint_ids == sorted(
        check.constraint_id for check in candidate.constraint_checks
    )
    assert constraint_result.items[0].status is ConstraintCheckStatus.PASS
    assert ontology_result.schema_slice_ids == [task.schema_slice_id]
    assert ontology_result.schema_snapshot_sha256 == task.schema_snapshot_sha256
    assert [item.model_dump() for item in ontology_result.items] == [
        {
            "candidate_id": candidate.candidate_id,
            "ontology_class_iri": candidate.ontology_class_iri,
            "ontology_class_prefixed": candidate.ontology_class_prefixed,
            "schema_slice_id": task.schema_slice_id,
            "schema_snapshot_sha256": task.schema_snapshot_sha256,
        }
    ]


def test_result_serialization_is_stable_and_evidence_comparison_is_source_bound():
    task = _task()
    gateway = ResolutionToolGateway(task=task)
    claim = next(
        claim
        for claim in task.authority_evidence
        if claim.candidate_id == "facility:KJFK"
    )

    result = gateway.compare_candidate_evidence(candidate_ids=["facility:KJFK"])

    assert result.authority_evidence_ids == [claim.evidence_id]
    assert result.authority_source_ids == [claim.source_id]
    assert result.model_dump_json() == result.model_dump_json()
    assert result.model_dump_json() == (
        '{"tool":"compare_candidate_evidence","status":"ok",'
        '"candidate_ids":["facility:KJFK"],'
        f'"authority_evidence_ids":["{claim.evidence_id}"],'
        f'"authority_source_ids":["{claim.source_id}"],'
        '"constraint_ids":[],"schema_slice_ids":[],'
        '"schema_snapshot_sha256":null,"result_ids":[],"items":[],'
        '"failure_reason":""}'
    )
