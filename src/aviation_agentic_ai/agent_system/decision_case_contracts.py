"""Dormant strict contracts for the three-Agent decision-case migration.

These models define an auditable interchange surface.  They are deliberately
not registered with the active workflow or any model prompt in Batch A.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from enum import Enum
from typing import Annotated, Any, Literal, Self, cast

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    computed_field,
    field_validator,
    model_validator,
)

from aviation_agentic_ai.agent_system.contracts import (
    SourceFamily,
    WeatherContextAssociation,
)


DECISION_CASE_CONTRACT_VERSION = "decision-case-agent-contracts-v1"
Sha256Hex = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
_EVENT_IRI_PREFIX = "urn:aviation-agentic-ai:event:"


def _canonical_case_event_id(event_id: str) -> str:
    if event_id.startswith("evt:"):
        return f"{_EVENT_IRI_PREFIX}{event_id.removeprefix('evt:')}"
    return event_id


def _duplicates(values: Sequence[str]) -> set[str]:
    seen: set[str] = set()
    return {value for value in values if value in seen or seen.add(value)}


def _require_unique(values: Sequence[str], field_name: str) -> None:
    duplicates = _duplicates(values)
    if duplicates:
        raise ValueError(f"{field_name} contains duplicate IDs: {sorted(duplicates)!r}")


def _require_sorted_unique(values: Sequence[str], field_name: str) -> None:
    _require_unique(values, field_name)
    if tuple(values) != tuple(sorted(values)):
        raise ValueError(f"{field_name} must be sorted")


def _require_nonempty_strings(values: Sequence[str], field_name: str) -> None:
    if any(not value for value in values):
        raise ValueError(f"{field_name} contains an empty ID")


def _validate_ordered_ids(values: Sequence[str], field_name: str) -> None:
    _require_nonempty_strings(values, field_name)
    _require_unique(values, field_name)


def _validate_set_ids(values: Sequence[str], field_name: str) -> None:
    _require_nonempty_strings(values, field_name)
    _require_sorted_unique(values, field_name)


def canonicalize_contract_value(value: Any) -> Any:
    """Convert one strict contract value into a canonical JSON primitive."""

    if isinstance(value, BaseModel):
        value = value.model_dump(
            mode="python",
            exclude={"payload_checksum"},
            exclude_computed_fields=False,
        )
    if isinstance(value, Enum):
        return canonicalize_contract_value(value.value)
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("naive datetimes are not canonical contract values")
        return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("NaN and Infinity are not canonical contract values")
        return value
    if isinstance(value, bytes):
        raise TypeError("bytes are not canonical contract values")
    if isinstance(value, set | frozenset):
        raise TypeError("sets are not canonical contract values")
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise TypeError("canonical contract mapping keys must be strings")
        return {
            key: canonicalize_contract_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (tuple, list)):
        return [canonicalize_contract_value(item) for item in value]
    raise TypeError(f"unsupported canonical contract value: {type(value).__name__}")


def _canonical_json_bytes(value: Any) -> bytes:
    canonicalized_payload = canonicalize_contract_value(value)
    return json.dumps(
        canonicalized_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def stable_contract_id(namespace: str, *canonical_inputs: str) -> str:
    """Build one length-prefixed, delimiter-safe stable ID."""

    if not isinstance(namespace, str) or not namespace:
        raise TypeError("namespace must be a nonempty string")
    framed = bytearray()
    for value in (namespace, *canonical_inputs):
        if not isinstance(value, str):
            raise TypeError("stable contract ID inputs must be strings")
        encoded = value.encode("utf-8")
        framed.extend(len(encoded).to_bytes(8, "big", signed=False))
        framed.extend(encoded)
    return f"{namespace}:{hashlib.sha256(framed).hexdigest()}"


def canonical_id_tuple_token(
    values: Sequence[str],
    *,
    sort_values: bool,
) -> str:
    """Encode one duplicate-free ID sequence as a compact JSON array."""

    if isinstance(values, (str, bytes)):
        raise TypeError("ID sequence must not be a string")
    if any(not isinstance(value, str) for value in values):
        raise TypeError("ID sequence values must be strings")
    _require_unique(values, "values")
    encoded_values = sorted(values) if sort_values else list(values)
    return json.dumps(
        encoded_values,
        separators=(",", ":"),
        ensure_ascii=False,
    )


class FrozenContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class ContractExecutionBinding(FrozenContractModel):
    run_id: str
    created_at: AwareDatetime
    prompt_version: str | None = None
    tool_version: str | None = None

    @field_validator("created_at")
    @classmethod
    def normalize_created_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        return value.astimezone(UTC)

    @model_validator(mode="after")
    def require_execution_version(self) -> Self:
        if not self.run_id:
            raise ValueError("run_id must be nonempty")
        if not self.prompt_version and not self.tool_version:
            raise ValueError("prompt_version or tool_version is required")
        return self


class ChecksummedContract(FrozenContractModel):
    contract_version: Literal[
        "decision-case-agent-contracts-v1"
    ] = DECISION_CASE_CONTRACT_VERSION
    payload_checksum: Sha256Hex
    created_at: AwareDatetime
    prompt_version: str | None = None
    tool_version: str | None = None

    @model_validator(mode="after")
    def validate_integrity(self, info: ValidationInfo) -> Self:
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        if self.created_at.utcoffset().total_seconds() != 0:
            raise ValueError("sealed contract created_at must be UTC")
        if not self.prompt_version and not self.tool_version:
            raise ValueError("prompt_version or tool_version is required")
        if info.context and info.context.get("skip_payload_checksum"):
            return self
        payload = self.model_dump(
            mode="python",
            exclude={"payload_checksum"},
            exclude_computed_fields=False,
        )
        expected = hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()
        if self.payload_checksum != expected:
            raise ValueError("payload_checksum does not match the validated payload")
        return self


def canonical_payload_bytes(
    model_type: type[BaseModel],
    fields: BaseModel,
    binding: ContractExecutionBinding,
) -> bytes:
    """Validate and encode checksum-covered fields except payload_checksum."""

    payload = fields.model_dump(mode="python", exclude_computed_fields=True)
    payload.update(
        {
            "contract_version": DECISION_CASE_CONTRACT_VERSION,
            "created_at": binding.created_at,
            "prompt_version": binding.prompt_version,
            "tool_version": binding.tool_version,
        }
    )
    expected_fields = set(model_type.model_fields) - {"payload_checksum"}
    if set(payload) != expected_fields:
        missing = sorted(expected_fields - set(payload))
        extra = sorted(set(payload) - expected_fields)
        raise ValueError(
            f"field bundle does not match {model_type.__name__}: "
            f"missing={missing!r}, extra={extra!r}"
        )
    provisional = model_type.model_validate(
        {**payload, "payload_checksum": "0" * 64},
        context={"skip_payload_checksum": True},
    )
    return _canonical_json_bytes(
        provisional.model_dump(
            mode="python",
            exclude={"payload_checksum"},
            exclude_computed_fields=False,
        )
    )


def _seal_contract(
    model_type: type[ChecksummedContract],
    fields: BaseModel,
    binding: ContractExecutionBinding,
) -> ChecksummedContract:
    fields_run_id = getattr(fields, "run_id", None)
    if fields_run_id != binding.run_id:
        raise ValueError("binding run_id must match field bundle run_id")
    payload_bytes = canonical_payload_bytes(model_type, fields, binding)
    payload = fields.model_dump(mode="python", exclude_computed_fields=True)
    payload.update(
        {
            "contract_version": DECISION_CASE_CONTRACT_VERSION,
            "payload_checksum": hashlib.sha256(payload_bytes).hexdigest(),
            "created_at": binding.created_at,
            "prompt_version": binding.prompt_version,
            "tool_version": binding.tool_version,
        }
    )
    sealed = model_type.model_validate(payload)
    reproduced = _canonical_json_bytes(
        sealed.model_dump(
            mode="python",
            exclude={"payload_checksum"},
            exclude_computed_fields=False,
        )
    )
    if reproduced != payload_bytes:
        raise ValueError("sealed contract did not reproduce canonical payload bytes")
    return sealed


class ResolutionDecision(str, Enum):
    ACCEPTED = "accepted"
    ABSTAINED = "abstained"
    INSUFFICIENT = "insufficient"
    BLOCKED = "blocked"


class ConstraintCheckStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


class CandidateBuildStatus(str, Enum):
    OK = "ok"
    INSUFFICIENT = "insufficient"
    BLOCKED = "blocked"


class AuthorityEvidenceKind(str, Enum):
    FACILITY_RECORD = "facility_record"
    TERM_DEFINITION = "term_definition"


class AuthorityRecordEvidenceClaim(FrozenContractModel):
    evidence_id: str
    candidate_id: str
    evidence_kind: Literal["facility_record"]
    authority_record_text: str
    authority_record_locator: str
    authority_record_sha256: Sha256Hex
    authority_source_ref: str
    source_id: str
    source_snapshot_sha256: Sha256Hex
    authority_artifact_key: Literal["nasr_zip"]
    authority_artifact_sha256: Sha256Hex
    manifest_artifact_key: Literal["nasr_manifest"]
    manifest_artifact_sha256: Sha256Hex

    @model_validator(mode="after")
    def validate_stable_ids(self) -> Self:
        expected_source_id = stable_contract_id(
            "authority-source",
            "facility",
            self.candidate_id,
            self.authority_source_ref,
            self.source_snapshot_sha256,
        )
        if self.source_id != expected_source_id:
            raise ValueError("authority record source_id is not stable")
        expected_evidence_id = stable_contract_id(
            "authority-evidence",
            self.candidate_id,
            self.source_id,
            self.source_snapshot_sha256,
            self.authority_artifact_sha256,
        )
        if self.evidence_id != expected_evidence_id:
            raise ValueError("authority record evidence_id is not stable")
        return self


class AuthorityDefinitionEvidenceClaim(FrozenContractModel):
    evidence_id: str
    candidate_id: str
    evidence_kind: Literal["term_definition"]
    definition_text: str
    definition_locator: str
    authority_source_ref: str
    source_id: str
    source_snapshot_sha256: Sha256Hex
    authority_artifact_key: Literal["pilot_controller_glossary"]
    authority_artifact_sha256: Sha256Hex
    definition_registry_artifact_key: Literal["authority_definition_seed"]
    definition_registry_artifact_sha256: Sha256Hex
    term_registry_artifact_key: Literal["term_seed"]
    term_registry_artifact_sha256: Sha256Hex

    @model_validator(mode="after")
    def validate_stable_ids(self) -> Self:
        expected_source_id = stable_contract_id(
            "authority-source",
            "term",
            self.candidate_id,
            self.authority_source_ref,
            self.source_snapshot_sha256,
        )
        if self.source_id != expected_source_id:
            raise ValueError("authority definition source_id is not stable")
        expected_evidence_id = stable_contract_id(
            "authority-evidence",
            self.candidate_id,
            self.source_id,
            self.source_snapshot_sha256,
            self.authority_artifact_sha256,
        )
        if self.evidence_id != expected_evidence_id:
            raise ValueError("authority definition evidence_id is not stable")
        return self


AuthorityEvidenceClaim = (
    AuthorityRecordEvidenceClaim | AuthorityDefinitionEvidenceClaim
)


class SourceSnapshotBinding(FrozenContractModel):
    source_id: str
    source_family: SourceFamily
    source_snapshot_sha256: Sha256Hex


class ConstraintCheck(FrozenContractModel):
    constraint_id: str
    candidate_id: str
    check_kind: Literal[
        "structural_slot",
        "expected_entity_type",
        "schema_compatibility",
    ]
    status: ConstraintCheckStatus
    reason_code: str
    evidence_ids: tuple[str, ...] = ()
    schema_snapshot_sha256: Sha256Hex | None = None

    @model_validator(mode="after")
    def validate_shape(self) -> Self:
        _validate_set_ids(self.evidence_ids, "evidence_ids")
        if self.check_kind == "schema_compatibility":
            if self.schema_snapshot_sha256 is None:
                raise ValueError("schema compatibility check requires schema checksum")
        elif self.schema_snapshot_sha256 is not None:
            raise ValueError("only schema compatibility checks bind schema checksum")
        return self


class ResolutionCandidate(FrozenContractModel):
    candidate_id: str
    candidate_kind: Literal["facility", "term"]
    preferred_label: str
    surface_form: str
    candidate_type: str
    ontology_class_prefixed: str | None
    ontology_class_iri: str | None
    authority_evidence_ids: tuple[str, ...]
    constraint_checks: tuple[ConstraintCheck, ...]

    @model_validator(mode="after")
    def validate_candidate(self) -> Self:
        if bool(self.ontology_class_prefixed) != bool(self.ontology_class_iri):
            raise ValueError("ontology mapping fields must be both present or absent")
        _validate_set_ids(self.authority_evidence_ids, "authority_evidence_ids")
        kinds = [check.check_kind for check in self.constraint_checks]
        for required_kind in (
            "structural_slot",
            "expected_entity_type",
            "schema_compatibility",
        ):
            if kinds.count(required_kind) != 1:
                raise ValueError(f"candidate requires exactly one {required_kind} check")
        if any(check.candidate_id != self.candidate_id for check in self.constraint_checks):
            raise ValueError("constraint check candidate ownership mismatch")
        for check in self.constraint_checks:
            if not set(check.evidence_ids).issubset(self.authority_evidence_ids):
                raise ValueError("constraint check cites unknown candidate evidence")
        return self

    @computed_field
    @property
    def eligible(self) -> bool:
        return (
            self.ontology_class_prefixed is not None
            and self.ontology_class_iri is not None
            and bool(self.authority_evidence_ids)
            and all(
                check.status is ConstraintCheckStatus.PASS
                for check in self.constraint_checks
            )
            and all(
                check.schema_snapshot_sha256 is not None
                for check in self.constraint_checks
                if check.check_kind == "schema_compatibility"
            )
        )


class RawResolutionCandidateRef(FrozenContractModel):
    candidate_id: str
    candidate_kind: Literal["facility", "term"]


class ResolutionCandidateAudit(FrozenContractModel):
    candidate_audit_id: str
    candidate_id: str
    candidate_kind: Literal["facility", "term"]
    build_status: CandidateBuildStatus
    candidate_payload_checksum: Sha256Hex | None = None
    evidence_id: str | None = None
    source_id: str | None = None
    reason_code: str | None = None
    error_id: str | None = None

    @model_validator(mode="after")
    def validate_terminal_shape_and_id(self) -> Self:
        if self.build_status is CandidateBuildStatus.OK:
            if not (
                self.candidate_payload_checksum
                and self.evidence_id
                and self.source_id
            ):
                raise ValueError("ok audit requires candidate checksum, evidence, and source")
            if self.reason_code or self.error_id:
                raise ValueError("ok audit forbids reason and error")
        elif self.build_status is CandidateBuildStatus.INSUFFICIENT:
            if not self.candidate_payload_checksum or not self.reason_code:
                raise ValueError("insufficient audit requires checksum and reason")
            if self.evidence_id or self.source_id or self.error_id:
                raise ValueError("insufficient audit forbids evidence, source, and error")
        else:
            if not self.reason_code or not self.error_id:
                raise ValueError("blocked audit requires reason and stable error ID")
            if self.candidate_payload_checksum or self.evidence_id or self.source_id:
                raise ValueError("blocked audit forbids unvalidated candidate content")
        expected = stable_contract_id(
            "resolution-candidate-audit",
            self.candidate_id,
            self.candidate_kind,
            self.build_status.value,
            self.candidate_payload_checksum or "NONE",
            self.evidence_id or "NONE",
            self.source_id or "NONE",
            self.reason_code or "NONE",
            self.error_id or "NONE",
        )
        if self.candidate_audit_id != expected:
            raise ValueError("candidate_audit_id is not stable")
        return self


def _candidate_payload_checksum(candidate: ResolutionCandidate) -> str:
    payload = candidate.model_dump(
        mode="python",
        exclude_computed_fields=True,
    )
    return hashlib.sha256(_canonical_json_bytes(payload)).hexdigest()


class ResolutionTaskFields(FrozenContractModel):
    task_id: str
    run_id: str
    event_id: str
    mention: str
    structural_slot: str
    expected_entity_type: str
    authority_domain_status: CandidateBuildStatus
    authority_domain_reason_code: str | None = None
    authority_domain_error_id: str | None = None
    raw_candidate_refs: tuple[RawResolutionCandidateRef, ...]
    candidates: tuple[ResolutionCandidate, ...]
    candidate_audits: tuple[ResolutionCandidateAudit, ...]
    authority_evidence: tuple[AuthorityEvidenceClaim, ...]
    authority_source_ids: tuple[str, ...]
    ontology_constraints: tuple[str, ...]
    schema_slice_id: str
    schema_snapshot_sha256: Sha256Hex
    rejected_candidate_ids: tuple[str, ...] = ()
    remaining_tool_budget: int = Field(ge=0, le=3)
    decision: ResolutionDecision | None = None

    @model_validator(mode="after")
    def validate_resolution_task(self) -> Self:
        if not all(
            (
                self.run_id,
                self.event_id,
                self.mention,
                self.structural_slot,
                self.expected_entity_type,
                self.schema_slice_id,
            )
        ):
            raise ValueError("resolution task identity fields must be nonempty")
        if self.authority_domain_status is CandidateBuildStatus.OK:
            if self.authority_domain_reason_code or self.authority_domain_error_id:
                raise ValueError("ok authority domain forbids reason and error")
        elif self.authority_domain_status is CandidateBuildStatus.INSUFFICIENT:
            if (
                not self.authority_domain_reason_code
                or self.authority_domain_error_id
            ):
                raise ValueError("insufficient authority domain requires reason only")
        else:
            if (
                not self.authority_domain_reason_code
                or not self.authority_domain_error_id
            ):
                raise ValueError("blocked authority domain requires reason and error")
            if any(
                (
                    self.raw_candidate_refs,
                    self.candidates,
                    self.candidate_audits,
                    self.authority_evidence,
                    self.authority_source_ids,
                )
            ):
                raise ValueError("pre-enumeration blocked domain must contain no candidates")

        raw_keys = [
            (row.candidate_kind, row.candidate_id)
            for row in self.raw_candidate_refs
        ]
        if raw_keys != sorted(raw_keys) or len(raw_keys) != len(set(raw_keys)):
            raise ValueError("raw_candidate_refs must be sorted and unique")
        candidate_ids = [row.candidate_id for row in self.candidates]
        _validate_set_ids(candidate_ids, "candidates")
        audit_ids = [row.candidate_audit_id for row in self.candidate_audits]
        _validate_set_ids(audit_ids, "candidate_audits")
        evidence_ids = [row.evidence_id for row in self.authority_evidence]
        _validate_set_ids(evidence_ids, "authority_evidence")
        _validate_set_ids(self.authority_source_ids, "authority_source_ids")
        _validate_set_ids(self.ontology_constraints, "ontology_constraints")
        _validate_set_ids(self.rejected_candidate_ids, "rejected_candidate_ids")

        audit_by_key = {
            (row.candidate_kind, row.candidate_id): row
            for row in self.candidate_audits
        }
        if set(audit_by_key) != set(raw_keys):
            raise ValueError("candidate audits must exactly cover raw candidate refs")
        candidate_by_id = {row.candidate_id: row for row in self.candidates}
        expected_candidate_ids = {
            row.candidate_id
            for row in self.candidate_audits
            if row.build_status
            in {CandidateBuildStatus.OK, CandidateBuildStatus.INSUFFICIENT}
        }
        if set(candidate_by_id) != expected_candidate_ids:
            raise ValueError("candidates must match ok and insufficient audit rows")

        evidence_by_id = {
            row.evidence_id: row for row in self.authority_evidence
        }
        referenced_evidence: set[str] = set()
        for candidate in self.candidates:
            audit = audit_by_key[(candidate.candidate_kind, candidate.candidate_id)]
            if audit.candidate_payload_checksum != _candidate_payload_checksum(candidate):
                raise ValueError("candidate audit carries stale candidate checksum")
            for check in candidate.constraint_checks:
                expected_constraint_id = stable_contract_id(
                    "resolution-constraint",
                    candidate.candidate_id,
                    check.check_kind,
                    self.structural_slot,
                    self.expected_entity_type,
                    self.schema_snapshot_sha256,
                )
                if check.constraint_id != expected_constraint_id:
                    raise ValueError("constraint_id is not stable for the bound task")
                if (
                    check.check_kind == "schema_compatibility"
                    and check.schema_snapshot_sha256
                    != self.schema_snapshot_sha256
                ):
                    raise ValueError("schema check checksum differs from task schema")
            for evidence_id in candidate.authority_evidence_ids:
                evidence = evidence_by_id.get(evidence_id)
                if evidence is None or evidence.candidate_id != candidate.candidate_id:
                    raise ValueError("candidate cites foreign or missing authority evidence")
                referenced_evidence.add(evidence_id)
            if audit.build_status is CandidateBuildStatus.OK:
                if audit.evidence_id not in candidate.authority_evidence_ids:
                    raise ValueError("ok audit evidence is not owned by candidate")
                evidence = evidence_by_id[audit.evidence_id]
                if audit.source_id != evidence.source_id:
                    raise ValueError("audit source differs from authority evidence source")
        if set(evidence_by_id) != referenced_evidence:
            raise ValueError("authority evidence registry contains unrelated rows")
        source_projection = tuple(
            sorted({row.source_id for row in self.authority_evidence})
        )
        if self.authority_source_ids != source_projection:
            raise ValueError("authority_source_ids must equal exact evidence projection")

        expected_task_id = stable_contract_id(
            "resolution-task",
            self.run_id,
            self.event_id,
            self.mention,
            self.structural_slot,
            self.expected_entity_type,
            canonical_id_tuple_token(audit_ids, sort_values=True),
            self.schema_slice_id,
            self.schema_snapshot_sha256,
        )
        if self.task_id != expected_task_id:
            raise ValueError("resolution task_id is not stable")
        return self


class ResolutionTask(ChecksummedContract, ResolutionTaskFields):
    pass


class ResolutionProposalFields(FrozenContractModel):
    resolution_proposal_id: str
    run_id: str
    task_id: str
    task_payload_checksum: Sha256Hex
    event_id: str
    mention: str
    structural_slot: str
    expected_entity_type: str
    selected_candidate_id: str | None
    rejected_candidate_ids: tuple[str, ...]
    decision: ResolutionDecision
    supporting_evidence_claim_ids: tuple[str, ...]
    authority_source_ids: tuple[str, ...]
    tool_trace_ids: tuple[str, ...]
    limitation: str | None

    @model_validator(mode="after")
    def validate_resolution_proposal_shape(self) -> Self:
        _validate_set_ids(self.rejected_candidate_ids, "rejected_candidate_ids")
        _validate_set_ids(
            self.supporting_evidence_claim_ids,
            "supporting_evidence_claim_ids",
        )
        _validate_set_ids(self.authority_source_ids, "authority_source_ids")
        _validate_ordered_ids(self.tool_trace_ids, "tool_trace_ids")
        if self.decision is ResolutionDecision.ACCEPTED:
            if not self.selected_candidate_id or not self.supporting_evidence_claim_ids:
                raise ValueError("accepted proposal requires selection and authority support")
        elif self.selected_candidate_id is not None:
            raise ValueError("only accepted proposal may select a candidate")
        if self.decision is ResolutionDecision.BLOCKED and not self.limitation:
            raise ValueError("blocked proposal requires corruption limitation")
        expected = stable_contract_id(
            "resolution-proposal",
            self.task_id,
            self.decision.value,
            self.selected_candidate_id or "NONE",
            canonical_id_tuple_token(
                self.rejected_candidate_ids,
                sort_values=True,
            ),
            canonical_id_tuple_token(
                self.supporting_evidence_claim_ids,
                sort_values=True,
            ),
        )
        if self.resolution_proposal_id != expected:
            raise ValueError("resolution_proposal_id is not stable")
        return self


class ResolutionProposal(ChecksummedContract, ResolutionProposalFields):
    pass


class ResolutionDomainOutcome(FrozenContractModel):
    domain: Literal["facility", "terminology"]
    required_for_case: bool
    decision: ResolutionDecision
    task_id: str
    task_payload_checksum: Sha256Hex
    resolution_proposal_id: str
    limitation_code: str | None = None
    error_id: str | None = None


def seal_resolution_task(
    *,
    fields: ResolutionTaskFields,
    binding: ContractExecutionBinding,
) -> ResolutionTask:
    return cast(ResolutionTask, _seal_contract(ResolutionTask, fields, binding))


def seal_resolution_proposal(
    *,
    task: ResolutionTask,
    fields: ResolutionProposalFields,
    binding: ContractExecutionBinding,
) -> ResolutionProposal:
    if not (
        binding.run_id
        == task.run_id
        == fields.run_id
    ):
        raise ValueError("binding, task, and proposal run IDs must match")
    if fields.task_id != task.task_id:
        raise ValueError("proposal task_id does not match bound task")
    if fields.task_payload_checksum != task.payload_checksum:
        raise ValueError("proposal task payload checksum does not match bound task")
    for name in ("event_id", "mention", "structural_slot", "expected_entity_type"):
        if getattr(fields, name) != getattr(task, name):
            raise ValueError(f"proposal {name} does not match bound task")

    candidate_by_id = {
        candidate.candidate_id: candidate for candidate in task.candidates
    }
    eligible_ids = {
        candidate.candidate_id
        for candidate in task.candidates
        if candidate.eligible
    }
    if fields.decision is ResolutionDecision.ACCEPTED:
        if fields.selected_candidate_id not in eligible_ids:
            raise ValueError("selected candidate is not eligible in bound task")
    elif fields.decision is ResolutionDecision.ABSTAINED:
        if len(eligible_ids) < 2:
            raise ValueError("abstained proposal requires at least two eligible candidates")
    elif (
        fields.decision is ResolutionDecision.INSUFFICIENT
        and eligible_ids
        and task.authority_domain_status is not CandidateBuildStatus.INSUFFICIENT
    ):
        raise ValueError(
            "insufficient proposal cannot ignore an eligible candidate unless "
            "the bound authority domain is incomplete"
        )

    expected_rejected = {
        audit.candidate_id for audit in task.candidate_audits
    } - ({fields.selected_candidate_id} if fields.selected_candidate_id else set())
    if set(fields.rejected_candidate_ids) != expected_rejected:
        raise ValueError("proposal must reject every non-selected audit row")

    task_evidence = {
        evidence.evidence_id: evidence for evidence in task.authority_evidence
    }
    if not set(fields.supporting_evidence_claim_ids).issubset(task_evidence):
        raise ValueError("proposal cites supporting evidence outside bound task")
    if fields.selected_candidate_id:
        selected = candidate_by_id[fields.selected_candidate_id]
        if not set(fields.supporting_evidence_claim_ids).issubset(
            selected.authority_evidence_ids
        ):
            raise ValueError("accepted support is not owned by selected candidate")
    source_projection = tuple(
        sorted(
            {
                task_evidence[evidence_id].source_id
                for evidence_id in fields.supporting_evidence_claim_ids
            }
        )
    )
    if fields.authority_source_ids != source_projection:
        raise ValueError("proposal authority sources differ from support projection")
    return cast(
        ResolutionProposal,
        _seal_contract(ResolutionProposal, fields, binding),
    )


class AssemblyStatus(str, Enum):
    OK = "ok"
    PARTIAL = "partial"
    INSUFFICIENT = "insufficient"
    BLOCKED = "blocked"


class ComponentLayerStatus(str, Enum):
    OK = "ok"
    INSUFFICIENT = "insufficient"
    BLOCKED = "blocked"


class FactDisposition(str, Enum):
    FORMAL_FACT = "formal_fact"
    PROFILE_GAP = "profile_gap"
    REJECTED = "rejected"


class ComponentLayerResult(FrozenContractModel):
    layer_id: str
    status: ComponentLayerStatus
    required_for_task: bool
    artifact_ids: tuple[str, ...] = ()
    missing_reason_code: str | None = None
    blocking_error_id: str | None = None

    @model_validator(mode="after")
    def validate_component_status(self) -> Self:
        _validate_set_ids(self.artifact_ids, "artifact_ids")
        if self.status is ComponentLayerStatus.OK:
            if (
                not self.artifact_ids
                or self.missing_reason_code
                or self.blocking_error_id
            ):
                raise ValueError("ok component requires artifacts and no failure metadata")
        elif self.status is ComponentLayerStatus.INSUFFICIENT:
            if (
                self.artifact_ids
                or not self.missing_reason_code
                or self.blocking_error_id
            ):
                raise ValueError("insufficient component requires missing reason only")
        elif not self.blocking_error_id:
            raise ValueError("blocked component requires blocking error ID")
        return self


class CaseFactProposal(FrozenContractModel):
    proposal_item_id: str
    subject_id: str
    predicate_iri: str
    object_kind: Literal["iri", "literal"]
    object_value: str
    evidence_claim_ids: tuple[str, ...] = ()
    derivation_ids: tuple[str, ...] = ()
    validation_profile_id: Annotated[str, Field(min_length=1)]

    @model_validator(mode="after")
    def require_support(self) -> Self:
        _validate_set_ids(self.evidence_claim_ids, "evidence_claim_ids")
        _validate_set_ids(self.derivation_ids, "derivation_ids")
        if not self.evidence_claim_ids and not self.derivation_ids:
            raise ValueError("fact proposal requires evidence or derivation support")
        return self


class CaseProfileGapProposal(FrozenContractModel):
    proposal_item_id: str
    event_id: str
    field: str
    normalized_value: str
    evidence_claim_ids: Annotated[tuple[str, ...], Field(min_length=1)]
    schema_mapping_reason_code: str
    validation_profile_id: Annotated[str, Field(min_length=1)]

    @model_validator(mode="after")
    def validate_gap_support(self) -> Self:
        _validate_set_ids(self.evidence_claim_ids, "evidence_claim_ids")
        return self


class FactAssessment(FrozenContractModel):
    assessment_id: str
    proposal_item_id: str
    disposition: FactDisposition
    published_fact_id: str | None = None
    profile_gap_id: str | None = None
    rejection_id: str | None = None
    support_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_disposition_output(self) -> Self:
        _validate_set_ids(self.support_ids, "support_ids")
        outputs = {
            FactDisposition.FORMAL_FACT: self.published_fact_id,
            FactDisposition.PROFILE_GAP: self.profile_gap_id,
            FactDisposition.REJECTED: self.rejection_id,
        }
        if not outputs[self.disposition]:
            raise ValueError("assessment disposition requires its output ID")
        if sum(value is not None for value in outputs.values()) != 1:
            raise ValueError("assessment must contain exactly one disposition output")
        return self


class ValidationFeedbackFields(FrozenContractModel):
    feedback_id: str
    run_id: str
    task_id: str
    case_id: str
    proposal_payload_checksum: Sha256Hex
    violation_code: str
    constraint_id: str
    affected_proposal_item_id: str
    repairable: bool
    allowed_corrections: tuple[str, ...]
    evidence_ids: tuple[str, ...]

    @model_validator(mode="after")
    def validate_feedback_id(self) -> Self:
        _validate_ordered_ids(self.allowed_corrections, "allowed_corrections")
        _validate_set_ids(self.evidence_ids, "evidence_ids")
        expected = stable_contract_id(
            "validation-feedback",
            self.task_id,
            self.proposal_payload_checksum,
            self.affected_proposal_item_id,
            self.violation_code,
            self.constraint_id,
            canonical_id_tuple_token(
                self.allowed_corrections,
                sort_values=False,
            ),
            canonical_id_tuple_token(self.evidence_ids, sort_values=True),
        )
        if self.feedback_id != expected:
            raise ValueError("feedback_id is not stable")
        return self


class ValidationFeedback(ChecksummedContract, ValidationFeedbackFields):
    pass


def _validate_source_bindings(
    bindings: Sequence[SourceSnapshotBinding],
) -> None:
    source_ids = [binding.source_id for binding in bindings]
    _validate_set_ids(source_ids, "source_snapshot_bindings")


class CaseAssemblyEvidenceRecord(FrozenContractModel):
    """One source-bound evidence record exposed through the Assembly gateway."""

    evidence_id: str
    field_name: str
    value: str
    evidence_text: str
    source_id: str
    canonical_ref: str | None = None


class CaseAssemblyResolutionRecord(FrozenContractModel):
    """Typed projection of one accepted or abstained resolution proposal."""

    resolution_proposal_id: str
    decision: ResolutionDecision
    selected_candidate_id: str | None = None
    supporting_evidence_claim_ids: tuple[str, ...] = ()
    authority_source_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_resolution_record(self) -> Self:
        _validate_set_ids(
            self.supporting_evidence_claim_ids,
            "supporting_evidence_claim_ids",
        )
        _validate_set_ids(self.authority_source_ids, "authority_source_ids")
        if self.decision is ResolutionDecision.ACCEPTED:
            if self.selected_candidate_id is None:
                raise ValueError("accepted resolution record requires a candidate")
        elif self.selected_candidate_id is not None:
            raise ValueError("only accepted resolution records select a candidate")
        return self


class CaseAssemblyPublicObservation(FrozenContractModel):
    """Profile-validated public observation available to Assembly."""

    observation_id: str
    run_id: str
    event_id: str
    phase: Literal["baseline", "active", "recovery"]
    metric_key: str
    value: int | float
    derivation_id: str
    validation_profile_id: str
    validation_profile_checksum: Sha256Hex
    source_id: str
    source_snapshot_sha256: Sha256Hex


class CaseAssemblyTaskFields(FrozenContractModel):
    task_id: str
    run_id: str
    case_id: str
    core_event_fact_ids: tuple[str, ...]
    resolution_proposal_ids: tuple[str, ...]
    available_evidence_layer_ids: tuple[str, ...]
    required_case_slots: tuple[str, ...]
    optional_case_slots: tuple[str, ...]
    missing_slots: tuple[str, ...]
    schema_profile_id: str
    schema_context_id: str
    schema_snapshot_sha256: Sha256Hex
    selected_evidence_claim_ids: tuple[str, ...]
    evidence_records: tuple[CaseAssemblyEvidenceRecord, ...] = ()
    resolution_records: tuple[CaseAssemblyResolutionRecord, ...] = ()
    proposed_facts: tuple[CaseFactProposal, ...]
    profile_gaps: tuple[CaseProfileGapProposal, ...]
    context_association_ids: tuple[str, ...]
    context_associations: tuple[WeatherContextAssociation, ...] = ()
    public_observation_ids: tuple[str, ...]
    public_observations: tuple[CaseAssemblyPublicObservation, ...] = ()
    omitted_slots: tuple[str, ...]
    validation_feedback: tuple[ValidationFeedback, ...]
    source_snapshot_bindings: tuple[SourceSnapshotBinding, ...]
    remaining_tool_budget: int = Field(ge=0, le=6)

    @model_validator(mode="after")
    def validate_assembly_task(self) -> Self:
        for field_name in (
            "core_event_fact_ids",
            "resolution_proposal_ids",
            "available_evidence_layer_ids",
            "required_case_slots",
            "optional_case_slots",
            "missing_slots",
            "selected_evidence_claim_ids",
            "context_association_ids",
            "public_observation_ids",
            "omitted_slots",
        ):
            _validate_set_ids(getattr(self, field_name), field_name)
        fact_item_ids = [row.proposal_item_id for row in self.proposed_facts]
        gap_item_ids = [row.proposal_item_id for row in self.profile_gaps]
        _validate_set_ids(fact_item_ids, "proposed_facts")
        _validate_set_ids(gap_item_ids, "profile_gaps")
        if tuple(fact_item_ids) != self.core_event_fact_ids:
            raise ValueError(
                "core event fact IDs must exactly match proposed fact IDs"
            )
        if set(fact_item_ids) & set(gap_item_ids):
            raise ValueError("proposal item IDs must be unique across facts and gaps")
        task_event_ids = {
            *(
                _canonical_case_event_id(row.subject_id)
                for row in self.proposed_facts
            ),
            *(
                _canonical_case_event_id(row.event_id)
                for row in self.profile_gaps
            ),
        }
        if len(task_event_ids) != 1:
            raise ValueError(
                "task event ownership must resolve to exactly one event"
            )
        task_event_id = next(iter(task_event_ids))
        feedback_ids = [row.feedback_id for row in self.validation_feedback]
        _validate_ordered_ids(feedback_ids, "validation_feedback")
        _validate_source_bindings(self.source_snapshot_bindings)
        evidence_record_ids = tuple(row.evidence_id for row in self.evidence_records)
        resolution_record_ids = tuple(
            row.resolution_proposal_id for row in self.resolution_records
        )
        association_record_ids = tuple(
            row.association_id for row in self.context_associations
        )
        observation_record_ids = tuple(
            row.observation_id for row in self.public_observations
        )
        for values, field_name in (
            (evidence_record_ids, "evidence_records"),
            (resolution_record_ids, "resolution_records"),
            (association_record_ids, "context_associations"),
            (observation_record_ids, "public_observations"),
        ):
            _validate_set_ids(values, field_name)
        if evidence_record_ids != self.selected_evidence_claim_ids:
            raise ValueError("evidence records must exactly match selected evidence IDs")
        if resolution_record_ids != self.resolution_proposal_ids:
            raise ValueError("resolution records must exactly match proposal IDs")
        if association_record_ids != self.context_association_ids:
            raise ValueError("context associations must exactly match association IDs")
        if observation_record_ids != self.public_observation_ids:
            raise ValueError("public observations must exactly match observation IDs")
        binding_by_source = {
            row.source_id: row for row in self.source_snapshot_bindings
        }
        for row in self.evidence_records:
            if row.source_id not in binding_by_source:
                raise ValueError("evidence record source is not snapshot-bound")
        for row in self.resolution_records:
            if not set(row.authority_source_ids).issubset(binding_by_source):
                raise ValueError("resolution authority source is not snapshot-bound")
        for row in self.context_associations:
            if (
                row.run_id != self.run_id
                or _canonical_case_event_id(row.event_id) != task_event_id
            ):
                raise ValueError("context association task event ownership mismatch")
            binding = binding_by_source.get(row.source_id)
            if (
                binding is None
                or binding.source_snapshot_sha256
                != row.source_snapshot_sha256
            ):
                raise ValueError("context association source binding mismatch")
        for row in self.public_observations:
            if (
                row.run_id != self.run_id
                or _canonical_case_event_id(row.event_id) != task_event_id
            ):
                raise ValueError(
                    "public observation task event ownership mismatch"
                )
            binding = binding_by_source.get(row.source_id)
            if (
                binding is None
                or binding.source_snapshot_sha256
                != row.source_snapshot_sha256
            ):
                raise ValueError("public observation source binding mismatch")
        expected_source_ids = {
            *(row.source_id for row in self.evidence_records),
            *(
                source_id
                for row in self.resolution_records
                for source_id in row.authority_source_ids
            ),
            *(row.source_id for row in self.context_associations),
            *(row.source_id for row in self.public_observations),
        }
        if set(binding_by_source) != expected_source_ids:
            raise ValueError(
                "source snapshot bindings must exactly match referenced record sources"
            )
        selected = set(self.selected_evidence_claim_ids)
        for item in (*self.proposed_facts, *self.profile_gaps):
            if item.validation_profile_id != self.schema_profile_id:
                raise ValueError("proposal validation profile differs from task profile")
            if not set(item.evidence_claim_ids).issubset(selected):
                raise ValueError("proposal cites evidence outside selected task evidence")
        for feedback in self.validation_feedback:
            if (
                feedback.run_id != self.run_id
                or feedback.task_id != self.task_id
                or feedback.case_id != self.case_id
            ):
                raise ValueError("validation feedback ownership differs from task")
        expected = stable_contract_id(
            "case-assembly-task",
            self.run_id,
            self.case_id,
            canonical_id_tuple_token(self.core_event_fact_ids, sort_values=True),
            canonical_id_tuple_token(
                self.resolution_proposal_ids,
                sort_values=True,
            ),
            canonical_id_tuple_token(
                self.selected_evidence_claim_ids,
                sort_values=True,
            ),
            self.schema_profile_id,
            self.schema_context_id,
            self.schema_snapshot_sha256,
        )
        if self.task_id != expected:
            raise ValueError("case assembly task_id is not stable")
        return self


class CaseAssemblyTask(ChecksummedContract, CaseAssemblyTaskFields):
    pass


class CaseAssemblyProposalFields(FrozenContractModel):
    case_assembly_proposal_id: str
    run_id: str
    task_id: str
    task_payload_checksum: Sha256Hex
    case_id: str
    assembly_status: AssemblyStatus
    component_layer_results: tuple[ComponentLayerResult, ...]
    proposed_facts: tuple[CaseFactProposal, ...]
    evidence_bindings: tuple[str, ...]
    resolution_proposal_ids: tuple[str, ...]
    context_association_ids: tuple[str, ...]
    profile_gaps: tuple[CaseProfileGapProposal, ...]
    omitted_slots: tuple[str, ...]
    limitations: tuple[str, ...]
    tool_trace_ids: tuple[str, ...]
    source_snapshot_bindings: tuple[SourceSnapshotBinding, ...]
    revision_count: int = Field(ge=0, le=1)

    @model_validator(mode="after")
    def validate_assembly_proposal(self) -> Self:
        component_ids = [row.layer_id for row in self.component_layer_results]
        _validate_ordered_ids(component_ids, "component_layer_results")
        fact_item_ids = [row.proposal_item_id for row in self.proposed_facts]
        gap_item_ids = [row.proposal_item_id for row in self.profile_gaps]
        _validate_set_ids(fact_item_ids, "proposed_facts")
        _validate_set_ids(gap_item_ids, "profile_gaps")
        if set(fact_item_ids) & set(gap_item_ids):
            raise ValueError("proposal item IDs must be unique across facts and gaps")
        for field_name in (
            "evidence_bindings",
            "resolution_proposal_ids",
            "context_association_ids",
            "omitted_slots",
            "limitations",
        ):
            _validate_set_ids(getattr(self, field_name), field_name)
        _validate_ordered_ids(self.tool_trace_ids, "tool_trace_ids")
        _validate_source_bindings(self.source_snapshot_bindings)
        required_blocked = any(
            row.required_for_task
            and row.status is ComponentLayerStatus.BLOCKED
            for row in self.component_layer_results
        )
        required_missing = any(
            row.required_for_task
            and row.status is ComponentLayerStatus.INSUFFICIENT
            for row in self.component_layer_results
        )
        optional_blocked = any(
            not row.required_for_task
            and row.status is ComponentLayerStatus.BLOCKED
            for row in self.component_layer_results
        )
        publishable_status = self.assembly_status in {
            AssemblyStatus.OK,
            AssemblyStatus.PARTIAL,
        }
        if publishable_status and not self.proposed_facts:
            raise ValueError("publishable assembly requires formal facts")
        if not publishable_status and (
            self.proposed_facts
            or self.profile_gaps
            or self.evidence_bindings
            or self.resolution_proposal_ids
            or self.context_association_ids
            or self.source_snapshot_bindings
        ):
            raise ValueError(
                "non-publishable assembly cannot carry selected case content"
            )
        if required_blocked:
            if self.assembly_status is not AssemblyStatus.BLOCKED:
                raise ValueError("blocked required component requires blocked assembly")
        elif required_missing:
            if self.assembly_status is not AssemblyStatus.INSUFFICIENT:
                raise ValueError("missing required component requires insufficient assembly")
        elif optional_blocked and self.assembly_status is not AssemblyStatus.PARTIAL:
            raise ValueError("blocked optional component requires partial assembly")
        expected = stable_contract_id(
            "case-assembly-proposal",
            self.task_id,
            self.task_payload_checksum,
            self.assembly_status.value,
            canonical_id_tuple_token(fact_item_ids, sort_values=True),
            canonical_id_tuple_token(gap_item_ids, sort_values=True),
            canonical_id_tuple_token(
                self.resolution_proposal_ids,
                sort_values=True,
            ),
        )
        if self.case_assembly_proposal_id != expected:
            raise ValueError("case assembly proposal ID is not stable")
        return self


class CaseAssemblyProposal(ChecksummedContract, CaseAssemblyProposalFields):
    pass


def seal_case_assembly_task(
    *,
    fields: CaseAssemblyTaskFields,
    binding: ContractExecutionBinding,
) -> CaseAssemblyTask:
    return cast(
        CaseAssemblyTask,
        _seal_contract(CaseAssemblyTask, fields, binding),
    )


def seal_case_assembly_proposal(
    *,
    task: CaseAssemblyTask,
    fields: CaseAssemblyProposalFields,
    binding: ContractExecutionBinding,
) -> CaseAssemblyProposal:
    if not (binding.run_id == task.run_id == fields.run_id):
        raise ValueError("binding, task, and proposal run IDs must match")
    if fields.task_id != task.task_id:
        raise ValueError("assembly proposal task_id does not match bound task")
    if fields.task_payload_checksum != task.payload_checksum:
        raise ValueError("assembly proposal task checksum does not match bound task")
    if fields.case_id != task.case_id:
        raise ValueError("assembly proposal case_id does not match bound task")
    if not set(fields.resolution_proposal_ids).issubset(task.resolution_proposal_ids):
        raise ValueError("assembly proposal cites resolution outside bound task")
    if not set(fields.evidence_bindings).issubset(task.selected_evidence_claim_ids):
        raise ValueError("assembly proposal cites evidence outside bound task")
    if not set(fields.context_association_ids).issubset(task.context_association_ids):
        raise ValueError("assembly proposal cites context outside bound task")
    for item in (*fields.proposed_facts, *fields.profile_gaps):
        if item.validation_profile_id != task.schema_profile_id:
            raise ValueError("proposal validation profile differs from bound task")
        if not set(item.evidence_claim_ids).issubset(
            task.selected_evidence_claim_ids
        ):
            raise ValueError("proposal item cites evidence outside bound task")
    task_bindings = {
        binding_row.source_id: binding_row
        for binding_row in task.source_snapshot_bindings
    }
    for binding_row in fields.source_snapshot_bindings:
        if task_bindings.get(binding_row.source_id) != binding_row:
            raise ValueError("proposal source binding differs from bound task")
    return cast(
        CaseAssemblyProposal,
        _seal_contract(CaseAssemblyProposal, fields, binding),
    )


def seal_validation_feedback(
    *,
    task: CaseAssemblyTask,
    proposal: CaseAssemblyProposal,
    fields: ValidationFeedbackFields,
    binding: ContractExecutionBinding,
) -> ValidationFeedback:
    task_binding_mismatch = (
        fields.violation_code == "TASK_BINDING_MISMATCH"
        and fields.affected_proposal_item_id == task.task_id
    )
    if task_binding_mismatch:
        if not (binding.run_id == task.run_id == fields.run_id):
            raise ValueError("feedback binding, task, and fields run IDs must match")
        if (
            fields.task_id != task.task_id
            or fields.case_id != task.case_id
            or fields.evidence_ids
        ):
            raise ValueError("binding-mismatch feedback must be task-owned")
    else:
        if not (
            binding.run_id == task.run_id == proposal.run_id == fields.run_id
        ):
            raise ValueError(
                "feedback binding, task, proposal, and fields run IDs must match"
            )
        if not (
            fields.task_id == task.task_id == proposal.task_id
            and fields.case_id == task.case_id == proposal.case_id
        ):
            raise ValueError("feedback task/case ownership mismatch")
    if fields.proposal_payload_checksum != proposal.payload_checksum:
        raise ValueError("feedback proposal payload checksum mismatch")
    proposal_item_ids = {
        item.proposal_item_id
        for item in (*proposal.proposed_facts, *proposal.profile_gaps)
    }
    task_owned_anchor = (
        fields.violation_code
        in {"MISSING_REQUIRED_FORMAL_SLOT", "TASK_BINDING_MISMATCH"}
        and fields.affected_proposal_item_id == task.task_id
    )
    if (
        fields.affected_proposal_item_id not in proposal_item_ids
        and not task_owned_anchor
    ):
        raise ValueError("affected proposal item is not owned by bound proposal")
    available_evidence = set(proposal.evidence_bindings)
    available_evidence.update(
        evidence_id
        for item in (*proposal.proposed_facts, *proposal.profile_gaps)
        for evidence_id in item.evidence_claim_ids
    )
    if not set(fields.evidence_ids).issubset(available_evidence):
        raise ValueError("feedback cites evidence outside bound proposal")
    return cast(
        ValidationFeedback,
        _seal_contract(ValidationFeedback, fields, binding),
    )


class QueryStatus(str, Enum):
    OK = "ok"
    INSUFFICIENT = "insufficient"
    BLOCKED = "blocked"
    UNSUPPORTED = "unsupported"


class AnswerStatementKind(str, Enum):
    SOURCE_FACT = "source_fact"
    DETERMINISTIC_DERIVATION = "deterministic_derivation"
    AGENT_SYNTHESIS = "agent_synthesis"
    LIMITATION = "limitation"


class AnswerStatement(FrozenContractModel):
    statement_id: str
    statement_kind: AnswerStatementKind
    text: str
    support_fact_ids: tuple[str, ...] = ()
    support_derivation_ids: tuple[str, ...] = ()
    support_profile_gap_ids: tuple[str, ...] = ()
    support_source_ids: tuple[str, ...] = ()
    support_statement_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_statement_support(self) -> Self:
        for field_name in (
            "support_fact_ids",
            "support_derivation_ids",
            "support_profile_gap_ids",
            "support_source_ids",
        ):
            _validate_set_ids(getattr(self, field_name), field_name)
        _validate_ordered_ids(self.support_statement_ids, "support_statement_ids")
        if self.statement_kind is AnswerStatementKind.SOURCE_FACT:
            if not (self.support_fact_ids and self.support_source_ids):
                raise ValueError("source fact statement requires fact and source")
        elif self.statement_kind is AnswerStatementKind.DETERMINISTIC_DERIVATION:
            if not (
                self.support_derivation_ids
                and (self.support_fact_ids or self.support_source_ids)
            ):
                raise ValueError("derivation statement requires derivation and support")
        elif self.statement_kind is AnswerStatementKind.AGENT_SYNTHESIS:
            if not self.support_statement_ids:
                raise ValueError("agent synthesis requires prior statement support")
        return self


def _validate_component_rollup(
    component_results: Sequence[ComponentLayerResult],
    status: QueryStatus | None,
) -> None:
    if status is None:
        return
    required_blocked = any(
        row.required_for_task and row.status is ComponentLayerStatus.BLOCKED
        for row in component_results
    )
    required_missing = any(
        row.required_for_task
        and row.status is ComponentLayerStatus.INSUFFICIENT
        for row in component_results
    )
    if required_blocked:
        if status is not QueryStatus.BLOCKED:
            raise ValueError("blocked required component requires blocked query")
    elif required_missing and status is not QueryStatus.INSUFFICIENT:
        raise ValueError("missing required component requires insufficient query")


class CaseAnalysisTaskFields(FrozenContractModel):
    task_id: str
    run_id: str
    question: str
    intent_family: Literal[
        "episode",
        "operational_situation",
        "applicability_and_impact",
    ]
    event_or_case_scope: tuple[str, ...]
    query_plan_id: str
    available_bound_step_ids: tuple[str, ...]
    executed_bound_step_ids: tuple[str, ...]
    requested_evidence_layers: tuple[str, ...]
    retrieved_fact_ids: tuple[str, ...]
    retrieved_derivation_ids: tuple[str, ...]
    retrieved_profile_gap_ids: tuple[str, ...]
    retrieved_assessment_ids: tuple[str, ...]
    retrieved_source_ids: tuple[str, ...]
    component_layer_results: tuple[ComponentLayerResult, ...]
    missing_evidence: tuple[str, ...]
    source_snapshot_bindings: tuple[SourceSnapshotBinding, ...]
    remaining_step_budget: int = Field(ge=0, le=3)
    answer_status: QueryStatus | None
    answer_contract_id: str

    @model_validator(mode="after")
    def validate_analysis_task(self) -> Self:
        _validate_ordered_ids(self.event_or_case_scope, "event_or_case_scope")
        _validate_set_ids(
            self.available_bound_step_ids,
            "available_bound_step_ids",
        )
        _validate_ordered_ids(
            self.executed_bound_step_ids,
            "executed_bound_step_ids",
        )
        if not set(self.executed_bound_step_ids).issubset(
            self.available_bound_step_ids
        ):
            raise ValueError("executed steps must be available bound steps")
        for field_name in (
            "requested_evidence_layers",
            "retrieved_fact_ids",
            "retrieved_derivation_ids",
            "retrieved_profile_gap_ids",
            "retrieved_assessment_ids",
            "retrieved_source_ids",
            "missing_evidence",
        ):
            _validate_set_ids(getattr(self, field_name), field_name)
        component_ids = [row.layer_id for row in self.component_layer_results]
        _validate_ordered_ids(component_ids, "component_layer_results")
        _validate_source_bindings(self.source_snapshot_bindings)
        _validate_component_rollup(self.component_layer_results, self.answer_status)
        if self.answer_status is QueryStatus.UNSUPPORTED and any(
            (
                self.retrieved_fact_ids,
                self.retrieved_derivation_ids,
                self.retrieved_profile_gap_ids,
                self.retrieved_assessment_ids,
                self.retrieved_source_ids,
            )
        ):
            raise ValueError("unsupported task cannot carry retrieved evidence")
        expected = stable_contract_id(
            "case-analysis-task",
            self.run_id,
            self.query_plan_id,
            canonical_id_tuple_token(
                self.event_or_case_scope,
                sort_values=False,
            ),
            canonical_id_tuple_token(
                self.requested_evidence_layers,
                sort_values=True,
            ),
            self.answer_contract_id,
        )
        if self.task_id != expected:
            raise ValueError("case analysis task_id is not stable")
        return self


class CaseAnalysisTask(ChecksummedContract, CaseAnalysisTaskFields):
    pass


class QueryToolTrace(FrozenContractModel):
    """Sanitized trace of one validated, plan-bound read observation."""

    trace_id: str
    query_plan_id: str
    step_id: str
    operation: Literal[
        "read_episode_timeline",
        "read_operational_situation",
        "read_applicability",
        "read_observed_flight_outcome",
    ]
    observation_status: Literal["ok", "partial", "insufficient", "blocked"]
    fact_ids: tuple[str, ...] = ()
    derivation_ids: tuple[str, ...] = ()
    profile_gap_ids: tuple[str, ...] = ()
    assessment_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_sanitized_trace(self) -> Self:
        for field_name in (
            "fact_ids",
            "derivation_ids",
            "profile_gap_ids",
            "assessment_ids",
            "source_ids",
        ):
            _validate_set_ids(getattr(self, field_name), field_name)
        expected = stable_contract_id(
            "query-tool-trace",
            self.query_plan_id,
            self.step_id,
            self.operation,
            self.observation_status,
            canonical_id_tuple_token(self.fact_ids, sort_values=True),
            canonical_id_tuple_token(self.derivation_ids, sort_values=True),
            canonical_id_tuple_token(self.profile_gap_ids, sort_values=True),
            canonical_id_tuple_token(self.assessment_ids, sort_values=True),
            canonical_id_tuple_token(self.source_ids, sort_values=True),
        )
        if self.trace_id != expected:
            raise ValueError("query tool trace_id is not stable")
        return self


class QueryEvidenceBundleFields(FrozenContractModel):
    query_id: str
    run_id: str
    task_id: str
    task_payload_checksum: Sha256Hex
    answer_status: QueryStatus
    answer_contract_id: str
    component_statuses: tuple[ComponentLayerStatus, ...]
    component_layer_results: tuple[ComponentLayerResult, ...]
    executed_step_ids: tuple[str, ...]
    unexecuted_required_step_ids: tuple[str, ...]
    retrieved_fact_ids: tuple[str, ...]
    retrieved_derivation_ids: tuple[str, ...]
    retrieved_profile_gap_ids: tuple[str, ...]
    retrieved_assessment_ids: tuple[str, ...]
    retrieved_source_ids: tuple[str, ...]
    source_snapshot_bindings: tuple[SourceSnapshotBinding, ...]
    tool_trace_ids: tuple[str, ...]
    answer_statements: tuple[AnswerStatement, ...]
    limitations: tuple[str, ...]

    @model_validator(mode="after")
    def validate_evidence_bundle(self) -> Self:
        component_ids = [row.layer_id for row in self.component_layer_results]
        _validate_ordered_ids(component_ids, "component_layer_results")
        if self.component_statuses != tuple(
            row.status for row in self.component_layer_results
        ):
            raise ValueError("component_statuses must equal ordered projection")
        _validate_component_rollup(self.component_layer_results, self.answer_status)
        _validate_ordered_ids(self.executed_step_ids, "executed_step_ids")
        _validate_set_ids(
            self.unexecuted_required_step_ids,
            "unexecuted_required_step_ids",
        )
        for field_name in (
            "retrieved_fact_ids",
            "retrieved_derivation_ids",
            "retrieved_profile_gap_ids",
            "retrieved_assessment_ids",
            "retrieved_source_ids",
            "limitations",
        ):
            _validate_set_ids(getattr(self, field_name), field_name)
        _validate_source_bindings(self.source_snapshot_bindings)
        _validate_ordered_ids(self.tool_trace_ids, "tool_trace_ids")
        statement_ids = [row.statement_id for row in self.answer_statements]
        _validate_ordered_ids(statement_ids, "answer_statements")
        if self.answer_status is QueryStatus.UNSUPPORTED and any(
            (
                self.retrieved_fact_ids,
                self.retrieved_derivation_ids,
                self.retrieved_profile_gap_ids,
                self.retrieved_assessment_ids,
                self.retrieved_source_ids,
                self.answer_statements,
            )
        ):
            raise ValueError("unsupported bundle cannot carry evidence or statements")

        previous_statements: set[str] = set()
        supported_statements: set[str] = set()
        has_non_ok_component = any(
            row.status is not ComponentLayerStatus.OK
            for row in self.component_layer_results
        )
        for statement in self.answer_statements:
            if not set(statement.support_fact_ids).issubset(self.retrieved_fact_ids):
                raise ValueError("statement cites fact outside bundle")
            if not set(statement.support_derivation_ids).issubset(
                self.retrieved_derivation_ids
            ):
                raise ValueError("statement cites derivation outside bundle")
            if not set(statement.support_profile_gap_ids).issubset(
                self.retrieved_profile_gap_ids
            ):
                raise ValueError("statement cites profile gap outside bundle")
            if not set(statement.support_source_ids).issubset(
                self.retrieved_source_ids
            ):
                raise ValueError("statement cites source outside bundle")
            if not set(statement.support_statement_ids).issubset(previous_statements):
                raise ValueError("statement cites non-prior statement")
            if (
                statement.statement_kind is AnswerStatementKind.AGENT_SYNTHESIS
                and not set(statement.support_statement_ids).issubset(
                    supported_statements
                )
            ):
                raise ValueError("agent synthesis requires prior supported statements")
            direct_support = any(
                (
                    statement.support_fact_ids,
                    statement.support_derivation_ids,
                    statement.support_profile_gap_ids,
                    statement.support_source_ids,
                )
            )
            if (
                statement.statement_kind is AnswerStatementKind.LIMITATION
                and not direct_support
                and not has_non_ok_component
            ):
                raise ValueError(
                    "unsupported limitation requires a non-ok component layer"
                )
            previous_statements.add(statement.statement_id)
            if direct_support or (
                statement.support_statement_ids
                and set(statement.support_statement_ids).issubset(
                    supported_statements
                )
            ):
                supported_statements.add(statement.statement_id)

        expected = stable_contract_id(
            "query-evidence-bundle",
            self.task_id,
            self.task_payload_checksum,
            self.answer_status.value,
            canonical_id_tuple_token(
                self.executed_step_ids,
                sort_values=False,
            ),
            canonical_id_tuple_token(self.retrieved_fact_ids, sort_values=True),
            canonical_id_tuple_token(
                self.retrieved_derivation_ids,
                sort_values=True,
            ),
            canonical_id_tuple_token(
                self.retrieved_profile_gap_ids,
                sort_values=True,
            ),
            canonical_id_tuple_token(
                self.retrieved_source_ids,
                sort_values=True,
            ),
            self.answer_contract_id,
        )
        if self.query_id != expected:
            raise ValueError("query evidence bundle ID is not stable")
        return self


class QueryEvidenceBundle(ChecksummedContract, QueryEvidenceBundleFields):
    pass


def seal_case_analysis_task(
    *,
    fields: CaseAnalysisTaskFields,
    binding: ContractExecutionBinding,
) -> CaseAnalysisTask:
    return cast(
        CaseAnalysisTask,
        _seal_contract(CaseAnalysisTask, fields, binding),
    )


def seal_query_evidence_bundle(
    *,
    task: CaseAnalysisTask,
    fields: QueryEvidenceBundleFields,
    binding: ContractExecutionBinding,
) -> QueryEvidenceBundle:
    if not (binding.run_id == task.run_id == fields.run_id):
        raise ValueError("binding, task, and bundle run IDs must match")
    if fields.task_id != task.task_id:
        raise ValueError("bundle task_id does not match bound task")
    if fields.task_payload_checksum != task.payload_checksum:
        raise ValueError("bundle task checksum does not match bound task")
    if fields.answer_contract_id != task.answer_contract_id:
        raise ValueError("bundle answer contract differs from bound task")
    if not set(fields.executed_step_ids).issubset(task.available_bound_step_ids):
        raise ValueError("bundle executed step is not bound by task")
    if not set(fields.unexecuted_required_step_ids).issubset(
        task.available_bound_step_ids
    ):
        raise ValueError("bundle unexecuted step is not bound by task")
    for field_name in (
        "retrieved_fact_ids",
        "retrieved_derivation_ids",
        "retrieved_profile_gap_ids",
        "retrieved_assessment_ids",
        "retrieved_source_ids",
    ):
        if not set(getattr(fields, field_name)).issubset(getattr(task, field_name)):
            raise ValueError(f"bundle {field_name} exceeds bound task retrieval")
    task_bindings = {
        binding_row.source_id: binding_row
        for binding_row in task.source_snapshot_bindings
    }
    for binding_row in fields.source_snapshot_bindings:
        if task_bindings.get(binding_row.source_id) != binding_row:
            raise ValueError("bundle source binding differs from bound task")
    return cast(
        QueryEvidenceBundle,
        _seal_contract(QueryEvidenceBundle, fields, binding),
    )


class ParsedCaseAssemblySections(FrozenContractModel):
    proposed_facts: tuple[CaseFactProposal, ...]
    profile_gaps: tuple[CaseProfileGapProposal, ...]
