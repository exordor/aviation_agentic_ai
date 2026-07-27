"""Typed, candidate-bounded read-only tools for semantic resolution."""

from __future__ import annotations

from typing import Literal

from langchain_core.tools import BaseTool, tool
from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    AuthorityDefinitionEvidenceClaim,
    AuthorityRecordEvidenceClaim,
    ConstraintCheck,
    ConstraintCheckStatus,
    ResolutionCandidate,
    ResolutionTask,
)


class ResolutionToolError(RuntimeError):
    """Raised when a resolution tool request escapes its sealed task."""


class GetAuthorityRecordInput(StrictModel):
    """One eligible candidate from the current sealed resolution task."""

    candidate_id: str = Field(min_length=1)


class CandidateIdsInput(StrictModel):
    """Eligible candidates from the current sealed resolution task."""

    candidate_ids: list[str] = Field(min_length=1, max_length=3)


class ResolutionCandidateObservation(StrictModel):
    candidate_id: str
    candidate_kind: Literal["facility", "term"]
    candidate_type: str
    ontology_class_prefixed: str
    ontology_class_iri: str


class AuthorityRecordObservation(StrictModel):
    candidate_id: str
    evidence_id: str
    evidence_kind: Literal["facility_record", "term_definition"]
    source_id: str
    authority_record_text: str
    authority_record_locator: str


class ConstraintObservation(StrictModel):
    constraint_id: str
    candidate_id: str
    check_kind: Literal[
        "structural_slot",
        "expected_entity_type",
        "schema_compatibility",
    ]
    status: ConstraintCheckStatus
    reason_code: str
    evidence_ids: list[str]
    schema_snapshot_sha256: str | None


class OntologyContextObservation(StrictModel):
    candidate_id: str
    ontology_class_prefixed: str
    ontology_class_iri: str
    schema_slice_id: str
    schema_snapshot_sha256: str


ResolutionToolObservation = (
    ResolutionCandidateObservation
    | AuthorityRecordObservation
    | ConstraintObservation
    | OntologyContextObservation
)


class ResolutionToolResult(StrictModel):
    """One deterministic, JSON-serializable resolution-tool observation."""

    tool: Literal[
        "get_resolution_candidates",
        "get_authority_record",
        "get_ontology_context",
        "check_candidate_constraints",
        "compare_candidate_evidence",
    ]
    status: Literal["ok", "insufficient", "blocked"] = "ok"
    candidate_ids: list[str] = Field(default_factory=list)
    authority_evidence_ids: list[str] = Field(default_factory=list)
    authority_source_ids: list[str] = Field(default_factory=list)
    constraint_ids: list[str] = Field(default_factory=list)
    schema_slice_ids: list[str] = Field(default_factory=list)
    schema_snapshot_sha256: str | None = None
    result_ids: list[str] = Field(default_factory=list)
    items: list[ResolutionToolObservation] = Field(default_factory=list)
    failure_reason: str = ""


class ResolutionToolGateway:
    """Read-only view of authority material scoped to one ``ResolutionTask``."""

    def __init__(self, *, task: ResolutionTask) -> None:
        self.task = task
        self._candidate_by_id = {
            candidate.candidate_id: candidate for candidate in task.candidates
        }
        self._evidence_by_id = {
            evidence.evidence_id: evidence for evidence in task.authority_evidence
        }
        self._eligible_candidate_ids = {
            candidate.candidate_id
            for candidate in task.candidates
            if candidate.eligible
        }
        self._validate_task_scope()

    def _validate_task_scope(self) -> None:
        """Defend the tool boundary even if a task bypassed contract construction."""

        task_source_ids = set(self.task.authority_source_ids)
        for candidate in self.task.candidates:
            for evidence_id in candidate.authority_evidence_ids:
                evidence = self._evidence_by_id.get(evidence_id)
                if evidence is None or evidence.candidate_id != candidate.candidate_id:
                    raise ResolutionToolError(
                        "candidate authority evidence is not task-owned"
                    )
                if evidence.source_id not in task_source_ids:
                    raise ResolutionToolError(
                        "candidate authority evidence source is not task-owned"
                    )

    def _eligible_candidates(
        self,
        candidate_ids: list[str],
    ) -> list[ResolutionCandidate]:
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ResolutionToolError("duplicate candidate IDs are not allowed")
        unknown = sorted(set(candidate_ids) - set(self._candidate_by_id))
        if unknown:
            raise ResolutionToolError(
                f"candidate IDs are outside the sealed task: {unknown}"
            )
        ineligible = sorted(set(candidate_ids) - self._eligible_candidate_ids)
        if ineligible:
            raise ResolutionToolError(f"ineligible candidate IDs: {ineligible}")
        return [self._candidate_by_id[candidate_id] for candidate_id in sorted(candidate_ids)]

    def _evidence_for(
        self,
        candidates: list[ResolutionCandidate],
    ) -> list[AuthorityRecordEvidenceClaim | AuthorityDefinitionEvidenceClaim]:
        evidence_ids = sorted(
            {
                evidence_id
                for candidate in candidates
                for evidence_id in candidate.authority_evidence_ids
            }
        )
        evidence = [self._evidence_by_id[evidence_id] for evidence_id in evidence_ids]
        for claim in evidence:
            if claim.source_id not in self.task.authority_source_ids:
                raise ResolutionToolError(
                    "authority evidence source is not task-owned"
                )
        return evidence

    @staticmethod
    def _authority_observation(
        claim: AuthorityRecordEvidenceClaim | AuthorityDefinitionEvidenceClaim,
    ) -> AuthorityRecordObservation:
        if isinstance(claim, AuthorityRecordEvidenceClaim):
            return AuthorityRecordObservation(
                candidate_id=claim.candidate_id,
                evidence_id=claim.evidence_id,
                evidence_kind=claim.evidence_kind,
                source_id=claim.source_id,
                authority_record_text=claim.authority_record_text,
                authority_record_locator=claim.authority_record_locator,
            )
        return AuthorityRecordObservation(
            candidate_id=claim.candidate_id,
            evidence_id=claim.evidence_id,
            evidence_kind=claim.evidence_kind,
            source_id=claim.source_id,
            authority_record_text=claim.definition_text,
            authority_record_locator=claim.definition_locator,
        )

    def get_resolution_candidates(self) -> ResolutionToolResult:
        """Read eligible candidate IDs and their task-owned ontology classes."""

        candidates = [
            self._candidate_by_id[candidate_id]
            for candidate_id in sorted(self._eligible_candidate_ids)
        ]
        return ResolutionToolResult(
            tool="get_resolution_candidates",
            candidate_ids=[candidate.candidate_id for candidate in candidates],
            items=[
                ResolutionCandidateObservation(
                    candidate_id=candidate.candidate_id,
                    candidate_kind=candidate.candidate_kind,
                    candidate_type=candidate.candidate_type,
                    ontology_class_prefixed=candidate.ontology_class_prefixed or "",
                    ontology_class_iri=candidate.ontology_class_iri or "",
                )
                for candidate in candidates
            ],
        )

    def get_authority_record(self, *, candidate_id: str) -> ResolutionToolResult:
        """Read the authority record or definition for one eligible candidate."""

        candidates = self._eligible_candidates([candidate_id])
        evidence = self._evidence_for(candidates)
        return ResolutionToolResult(
            tool="get_authority_record",
            candidate_ids=[candidate_id],
            authority_evidence_ids=[claim.evidence_id for claim in evidence],
            authority_source_ids=sorted({claim.source_id for claim in evidence}),
            items=[self._authority_observation(claim) for claim in evidence],
        )

    def get_ontology_context(self, *, candidate_ids: list[str]) -> ResolutionToolResult:
        """Read task-bound ontology classes and the schema slice for candidates."""

        candidates = self._eligible_candidates(candidate_ids)
        return ResolutionToolResult(
            tool="get_ontology_context",
            candidate_ids=[candidate.candidate_id for candidate in candidates],
            schema_slice_ids=[self.task.schema_slice_id],
            schema_snapshot_sha256=self.task.schema_snapshot_sha256,
            items=[
                OntologyContextObservation(
                    candidate_id=candidate.candidate_id,
                    ontology_class_prefixed=candidate.ontology_class_prefixed or "",
                    ontology_class_iri=candidate.ontology_class_iri or "",
                    schema_slice_id=self.task.schema_slice_id,
                    schema_snapshot_sha256=self.task.schema_snapshot_sha256,
                )
                for candidate in candidates
            ],
        )

    @staticmethod
    def _constraint_observation(check: ConstraintCheck) -> ConstraintObservation:
        return ConstraintObservation(
            constraint_id=check.constraint_id,
            candidate_id=check.candidate_id,
            check_kind=check.check_kind,
            status=check.status,
            reason_code=check.reason_code,
            evidence_ids=list(check.evidence_ids),
            schema_snapshot_sha256=check.schema_snapshot_sha256,
        )

    def check_candidate_constraints(
        self,
        *,
        candidate_ids: list[str],
    ) -> ResolutionToolResult:
        """Read structural, type, and schema checks for eligible candidates."""

        candidates = self._eligible_candidates(candidate_ids)
        checks = sorted(
            (check for candidate in candidates for check in candidate.constraint_checks),
            key=lambda check: check.constraint_id,
        )
        return ResolutionToolResult(
            tool="check_candidate_constraints",
            candidate_ids=[candidate.candidate_id for candidate in candidates],
            constraint_ids=[check.constraint_id for check in checks],
            schema_slice_ids=[self.task.schema_slice_id],
            schema_snapshot_sha256=self.task.schema_snapshot_sha256,
            items=[self._constraint_observation(check) for check in checks],
        )

    def compare_candidate_evidence(
        self,
        *,
        candidate_ids: list[str],
    ) -> ResolutionToolResult:
        """Read only task-owned evidence and source IDs for eligible candidates."""

        candidates = self._eligible_candidates(candidate_ids)
        evidence = self._evidence_for(candidates)
        return ResolutionToolResult(
            tool="compare_candidate_evidence",
            candidate_ids=[candidate.candidate_id for candidate in candidates],
            authority_evidence_ids=[claim.evidence_id for claim in evidence],
            authority_source_ids=sorted({claim.source_id for claim in evidence}),
        )


def build_resolution_tools(gateway: ResolutionToolGateway) -> list[BaseTool]:
    """Build the five model-visible read-only tools for one resolution task."""

    @tool("get_resolution_candidates")
    def get_resolution_candidates() -> str:
        """Read eligible candidates from the sealed resolution task."""

        return gateway.get_resolution_candidates().model_dump_json()

    @tool("get_authority_record", args_schema=GetAuthorityRecordInput)
    def get_authority_record(candidate_id: str) -> str:
        """Read the task-owned authority record for one eligible candidate."""

        return gateway.get_authority_record(candidate_id=candidate_id).model_dump_json()

    @tool("get_ontology_context", args_schema=CandidateIdsInput)
    def get_ontology_context(candidate_ids: list[str]) -> str:
        """Read task-bound ontology context for eligible candidates."""

        return gateway.get_ontology_context(candidate_ids=candidate_ids).model_dump_json()

    @tool("check_candidate_constraints", args_schema=CandidateIdsInput)
    def check_candidate_constraints(candidate_ids: list[str]) -> str:
        """Read task-bound constraints for eligible candidates."""

        return gateway.check_candidate_constraints(candidate_ids=candidate_ids).model_dump_json()

    @tool("compare_candidate_evidence", args_schema=CandidateIdsInput)
    def compare_candidate_evidence(candidate_ids: list[str]) -> str:
        """Read evidence and authority source IDs for eligible candidates."""

        return gateway.compare_candidate_evidence(
            candidate_ids=candidate_ids
        ).model_dump_json()

    return [
        get_resolution_candidates,
        get_authority_record,
        get_ontology_context,
        check_candidate_constraints,
        compare_candidate_evidence,
    ]
