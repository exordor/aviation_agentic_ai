"""Authority-domain facility and terminology resolution services.

Facility and terminology lookup are bounded authority services, not public
Agent roles.  The only model-mediated step is genuine multi-candidate semantic
selection through the shared Semantic Resolution Agent.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from aviation_agentic_ai.agent_system.authority_evidence import (
    AuthorityBuildStatus,
    AuthorityCandidateBuildResult,
    AuthoritySourceContentFields,
    canonical_authority_source_content,
)
from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    AgentTask,
    EvidenceCard,
    EvidenceClaim,
    ModelCallRecord,
    SourceFamily,
    SourceRecord,
    ToolTraceEntry,
)
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    CandidateBuildStatus,
    ContractExecutionBinding,
    RawResolutionCandidateRef,
    ResolutionCandidateAudit,
    ResolutionDecision,
    ResolutionDomainOutcome,
    ResolutionProposal,
    ResolutionProposalFields,
    ResolutionTask,
    ResolutionTaskFields,
    canonical_id_tuple_token,
    canonicalize_contract_value,
    seal_resolution_proposal,
    seal_resolution_task,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.semantic_resolution import (
    run_semantic_resolution_agent,
)

ToolModelFactory = Callable[[list[Any]], Any]
AUTHORITY_RESOLUTION_TOOL_VERSION = "authority-resolution-v1"


@dataclass
class _AuthorityResolutionInput:
    mention: str
    candidates: list[Any] = field(default_factory=list)
    source_id: str = ""
    structural_slot: str = ""
    expected_entity_type: str = ""
    advisory_evidence: str = ""
    resolution_event_id: str = ""
    resolution_event_mention: str = ""
    run_started_at: datetime | None = None
    schema_slice_id: str = ""
    schema_snapshot_sha256: str = ""
    resolution_tool_version: str = ""
    authority_domain_status: AuthorityBuildStatus | None = None
    authority_domain_reason_code: str = ""
    authority_domain_error_id: str = ""
    authority_candidate_results: tuple[AuthorityCandidateBuildResult, ...] = ()


@dataclass
class FacilityAuthorityResolutionInput(_AuthorityResolutionInput):
    """Candidate and binding inputs for NASR facility authority resolution."""


@dataclass
class TerminologyAuthorityResolutionInput(_AuthorityResolutionInput):
    """Candidate and binding inputs for FAA terminology authority resolution."""


@dataclass(frozen=True)
class AuthorityResolutionResult:
    """Source-bound authority resolution outcome without an Agent envelope."""

    evidence_card: EvidenceCard
    domain_outcome: ResolutionDomainOutcome
    authority_source_records: tuple[SourceRecord, ...]
    resolution_task: ResolutionTask
    resolution_proposal: ResolutionProposal
    resolution_tool_traces: tuple[ToolTraceEntry, ...] = ()
    model_calls: tuple[ModelCallRecord, ...] = ()


def _check_tool(task: AgentTask, tool: str) -> None:
    if tool not in task.allowed_tools:
        raise ValueError(f"tool {tool!r} is not permitted for authority resolution")


def _candidate_payload_checksum(candidate: Any) -> str:
    payload = candidate.model_dump(mode="python", exclude_computed_fields=True)
    canonical = canonicalize_contract_value(payload)
    return hashlib.sha256(
        json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode("utf-8")
    ).hexdigest()


def _candidate_key(candidate: Any, domain: str) -> tuple[str, str]:
    return (
        "facility" if domain == "facility" else "term",
        candidate.entity_id if domain == "facility" else candidate.term_id,
    )


def _binding(task: AgentTask, request: _AuthorityResolutionInput) -> ContractExecutionBinding:
    started_at = request.run_started_at
    if started_at is None or started_at.tzinfo is None or started_at.utcoffset() is None:
        started_at = datetime(1970, 1, 1, tzinfo=UTC)
    return ContractExecutionBinding(
        run_id=task.run_id,
        created_at=started_at.astimezone(UTC),
        tool_version=request.resolution_tool_version or AUTHORITY_RESOLUTION_TOOL_VERSION,
    )


def _terminal_result(
    *,
    task: AgentTask,
    request: _AuthorityResolutionInput,
    domain: str,
    reason_code: str,
    decision: ResolutionDecision,
) -> AuthorityResolutionResult:
    if decision not in {ResolutionDecision.BLOCKED, ResolutionDecision.INSUFFICIENT}:
        raise ValueError("terminal authority decision is unsupported")
    blocked = decision is ResolutionDecision.BLOCKED
    status = CandidateBuildStatus.BLOCKED if blocked else CandidateBuildStatus.INSUFFICIENT
    binding = _binding(task, request)
    event_id = request.resolution_event_id or "INVALID_RESOLUTION_EVENT"
    mention = request.mention or "MISSING_EVENT_MENTION"
    slot = request.structural_slot or "INVALID_STRUCTURAL_SLOT"
    entity_type = request.expected_entity_type or "INVALID_EXPECTED_ENTITY_TYPE"
    schema_slice = request.schema_slice_id or "INVALID_SCHEMA_SLICE"
    checksum = (
        request.schema_snapshot_sha256
        if re.fullmatch(r"[0-9a-f]{64}", request.schema_snapshot_sha256 or "")
        else "0" * 64
    )
    error_id = (
        stable_contract_id("resolution-error", task.run_id, domain, reason_code)
        if blocked
        else None
    )
    task_id = stable_contract_id(
        "resolution-task",
        task.run_id,
        event_id,
        mention,
        slot,
        entity_type,
        canonical_id_tuple_token((), sort_values=True),
        schema_slice,
        checksum,
    )
    resolution_task = seal_resolution_task(
        fields=ResolutionTaskFields(
            task_id=task_id,
            run_id=task.run_id,
            event_id=event_id,
            mention=mention,
            structural_slot=slot,
            expected_entity_type=entity_type,
            authority_domain_status=status,
            authority_domain_reason_code=reason_code,
            authority_domain_error_id=error_id,
            raw_candidate_refs=(),
            candidates=(),
            candidate_audits=(),
            authority_evidence=(),
            authority_source_ids=(),
            ontology_constraints=(),
            schema_slice_id=schema_slice,
            schema_snapshot_sha256=checksum,
            rejected_candidate_ids=(),
            remaining_tool_budget=0,
            decision=decision,
        ),
        binding=binding,
    )
    proposal = seal_resolution_proposal(
        task=resolution_task,
        fields=ResolutionProposalFields(
            resolution_proposal_id=stable_contract_id(
                "resolution-proposal",
                task_id,
                decision.value,
                "NONE",
                canonical_id_tuple_token((), sort_values=True),
                canonical_id_tuple_token((), sort_values=True),
            ),
            run_id=task.run_id,
            task_id=task_id,
            task_payload_checksum=resolution_task.payload_checksum,
            event_id=event_id,
            mention=mention,
            structural_slot=slot,
            expected_entity_type=entity_type,
            selected_candidate_id=None,
            rejected_candidate_ids=(),
            decision=decision,
            supporting_evidence_claim_ids=(),
            authority_source_ids=(),
            tool_trace_ids=(),
            limitation=reason_code,
        ),
        binding=binding,
    )
    card = EvidenceCard(
        agent_role=domain,
        status=AgentStatus.BLOCKED if blocked else AgentStatus.ABSTAIN,
        source_ids=[request.source_id] if request.source_id else [],
        uncertainties=[] if blocked else [reason_code],
        decision_basis=f"{decision.value}: {reason_code}; resolution_task_id={task_id}; tool_version={binding.tool_version}",
    )
    return AuthorityResolutionResult(
        evidence_card=card,
        domain_outcome=ResolutionDomainOutcome(
            domain=domain,
            required_for_case=True,
            decision=decision,
            task_id=task_id,
            task_payload_checksum=resolution_task.payload_checksum,
            resolution_proposal_id=proposal.resolution_proposal_id,
            limitation_code=reason_code,
            error_id=error_id,
        ),
        authority_source_records=(),
        resolution_task=resolution_task,
        resolution_proposal=proposal,
    )


def _blocked(
    *, task: AgentTask, request: _AuthorityResolutionInput, domain: str, reason_code: str
) -> AuthorityResolutionResult:
    return _terminal_result(
        task=task,
        request=request,
        domain=domain,
        reason_code=reason_code,
        decision=ResolutionDecision.BLOCKED,
    )


def _insufficient(
    *, task: AgentTask, request: _AuthorityResolutionInput, domain: str, reason_code: str
) -> AuthorityResolutionResult:
    return _terminal_result(
        task=task,
        request=request,
        domain=domain,
        reason_code=reason_code,
        decision=ResolutionDecision.INSUFFICIENT,
    )


def _validate_source_record(row: AuthorityCandidateBuildResult, *, domain: str) -> SourceRecord:
    if row.evidence_claim is None or row.source_record is None:
        raise ValueError("authority source record requires bound evidence")
    evidence = type(row.evidence_claim).model_validate(row.evidence_claim.model_dump(mode="python"))
    source = SourceRecord.model_validate(row.source_record.model_dump(mode="python"))
    expected_family = SourceFamily.NASR_FACILITY if domain == "facility" else SourceFamily.FAA_TERM
    expected_kind = "facility" if domain == "facility" else "term"
    if (
        source.family is not expected_family
        or row.candidate_kind != expected_kind
        or evidence.candidate_id != row.candidate_id
    ):
        raise ValueError("authority source record is outside the domain")
    if (
        source.source_id != evidence.source_id
        or hashlib.sha256(source.content.encode("utf-8")).hexdigest()
        != evidence.source_snapshot_sha256
    ):
        raise ValueError("authority source record differs from evidence")
    fields = AuthoritySourceContentFields.model_validate_json(source.content)
    if (
        fields.candidate_id != row.candidate_id
        or fields.candidate_kind != expected_kind
        or fields.authority_source_ref != evidence.authority_source_ref
        or canonical_authority_source_content(fields) != source.content
    ):
        raise ValueError("authority source record is not canonically bound")
    return source


def _resolve(
    *,
    task: AgentTask,
    request: _AuthorityResolutionInput,
    domain: str,
    semantic_resolution_tool_model_factory: ToolModelFactory | None = None,
) -> AuthorityResolutionResult:
    allowed = (
        ("lookup_nasr_facility", "lookup_artcc", "resolve_facility_alias")
        if domain == "facility"
        else (
            "lookup_faa_glossary",
            "lookup_pcg_term",
            "resolve_term_registry",
            "resolve_schema_event_class",
        )
    )
    for tool in allowed:
        _check_tool(task, tool)
    required = (
        request.mention,
        request.source_id,
        request.resolution_event_id,
        request.resolution_event_mention,
        request.run_started_at,
        request.structural_slot,
        request.expected_entity_type,
        request.schema_slice_id,
        request.schema_snapshot_sha256,
        request.resolution_tool_version,
        request.authority_domain_status,
    )
    if (
        not all(required)
        or request.resolution_tool_version != AUTHORITY_RESOLUTION_TOOL_VERSION
        or not re.fullmatch(r"[0-9a-f]{64}", request.schema_snapshot_sha256 or "")
    ):
        return _blocked(
            task=task,
            request=request,
            domain=domain,
            reason_code="RESOLUTION_EXECUTION_BINDING_INVALID",
        )
    if (
        request.run_started_at is None
        or request.run_started_at.tzinfo is None
        or request.run_started_at.utcoffset() is None
    ):
        return _blocked(
            task=task,
            request=request,
            domain=domain,
            reason_code="RESOLUTION_RUN_TIMESTAMP_INVALID",
        )
    expected_event_id = stable_contract_id(
        "resolution-event",
        task.run_id,
        task.source_id,
        request.resolution_event_mention.strip().upper() or "MISSING_EVENT_MENTION",
    )
    if request.resolution_event_id != expected_event_id:
        return _blocked(
            task=task,
            request=request,
            domain=domain,
            reason_code="RESOLUTION_EVENT_BINDING_MISMATCH",
        )
    if request.authority_domain_status is AuthorityBuildStatus.BLOCKED:
        return _blocked(
            task=task,
            request=request,
            domain=domain,
            reason_code=request.authority_domain_reason_code
            or f"{domain.upper()}_AUTHORITY_BLOCKED",
        )
    if request.authority_domain_status is AuthorityBuildStatus.INSUFFICIENT:
        return _insufficient(
            task=task,
            request=request,
            domain=domain,
            reason_code=request.authority_domain_reason_code
            or f"{domain.upper()}_AUTHORITY_INSUFFICIENT",
        )

    raw_keys = [_candidate_key(row, domain) for row in request.candidates]
    result_keys = [
        (row.candidate_kind, row.candidate_id) for row in request.authority_candidate_results
    ]
    if (
        len(raw_keys) != len(set(raw_keys))
        or len(result_keys) != len(set(result_keys))
        or set(raw_keys) != set(result_keys)
    ):
        return _blocked(
            task=task,
            request=request,
            domain=domain,
            reason_code="AUTHORITY_CANDIDATE_SET_MISMATCH",
        )
    result_by_key = {
        (row.candidate_kind, row.candidate_id): row for row in request.authority_candidate_results
    }
    rows = tuple(result_by_key[key] for key in sorted(raw_keys))
    if any(row.status is AuthorityBuildStatus.BLOCKED for row in rows):
        return _blocked(
            task=task,
            request=request,
            domain=domain,
            reason_code=next(
                (row.reason_code for row in rows if row.status is AuthorityBuildStatus.BLOCKED),
                "AUTHORITY_CANDIDATE_BLOCKED",
            ),
        )
    effective = (
        AuthorityBuildStatus.INSUFFICIENT
        if any(row.status is AuthorityBuildStatus.INSUFFICIENT for row in rows)
        else AuthorityBuildStatus.OK
    )
    if (
        request.authority_domain_status is AuthorityBuildStatus.OK
        and effective is AuthorityBuildStatus.INSUFFICIENT
    ):
        return _blocked(
            task=task,
            request=request,
            domain=domain,
            reason_code="AUTHORITY_DOMAIN_STATUS_MISMATCH",
        )

    candidates: list[Any] = []
    audits: list[ResolutionCandidateAudit] = []
    evidence = []
    records = []
    for row in rows:
        assert row.candidate is not None
        candidates.append(row.candidate)
        checksum = _candidate_payload_checksum(row.candidate)
        evidence_id = row.evidence_claim.evidence_id if row.evidence_claim else None
        source_id = row.source_record.source_id if row.source_record else None
        audits.append(
            ResolutionCandidateAudit(
                candidate_audit_id=stable_contract_id(
                    "resolution-candidate-audit",
                    row.candidate_id,
                    row.candidate_kind,
                    row.status.value,
                    checksum,
                    evidence_id or "NONE",
                    source_id or "NONE",
                    row.reason_code or "NONE",
                    row.error_id or "NONE",
                ),
                candidate_id=row.candidate_id,
                candidate_kind=row.candidate_kind,
                build_status=CandidateBuildStatus(row.status.value),
                candidate_payload_checksum=checksum,
                evidence_id=evidence_id,
                source_id=source_id,
                reason_code=row.reason_code,
                error_id=row.error_id,
            )
        )
        if row.evidence_claim:
            evidence.append(row.evidence_claim)
        if row.source_record:
            records.append(_validate_source_record(row, domain=domain))
    domain_status = CandidateBuildStatus(effective.value)
    domain_reason = request.authority_domain_reason_code or None
    if domain_status is CandidateBuildStatus.INSUFFICIENT and not domain_reason:
        domain_reason = next(
            (row.reason_code for row in rows if row.status is AuthorityBuildStatus.INSUFFICIENT),
            "AUTHORITY_EVIDENCE_INSUFFICIENT",
        )
    limitation = domain_reason
    if not request.advisory_evidence.strip():
        domain_status = CandidateBuildStatus.INSUFFICIENT
        domain_reason = limitation = "ADVISORY_EVIDENCE_MISSING"
    eligible = [candidate for candidate in candidates if candidate.eligible]
    model_mediated = domain_status is CandidateBuildStatus.OK and len(eligible) > 1
    if domain_status is CandidateBuildStatus.INSUFFICIENT:
        decision, selected = ResolutionDecision.INSUFFICIENT, None
    elif len(eligible) == 1:
        decision, selected, limitation = ResolutionDecision.ACCEPTED, eligible[0], None
    elif model_mediated:
        decision, selected = None, None
    else:
        decision, selected, limitation = (
            ResolutionDecision.INSUFFICIENT,
            None,
            "NO_ELIGIBLE_AUTHORITY_CANDIDATE",
        )
    ordered_candidates = tuple(sorted(candidates, key=lambda candidate: candidate.candidate_id))
    ordered_audits = tuple(sorted(audits, key=lambda audit: audit.candidate_audit_id))
    ordered_evidence = tuple(sorted(evidence, key=lambda claim: claim.evidence_id))
    rejected = tuple(
        sorted(
            candidate.candidate_id
            for candidate in ordered_candidates
            if (
                not candidate.eligible
                if model_mediated
                else selected is None or candidate.candidate_id != selected.candidate_id
            )
        )
    )
    task_id = stable_contract_id(
        "resolution-task",
        task.run_id,
        request.resolution_event_id,
        request.mention,
        request.structural_slot,
        request.expected_entity_type,
        canonical_id_tuple_token(
            [audit.candidate_audit_id for audit in ordered_audits], sort_values=True
        ),
        request.schema_slice_id,
        request.schema_snapshot_sha256,
    )
    binding = _binding(task, request)
    resolution_task = seal_resolution_task(
        fields=ResolutionTaskFields(
            task_id=task_id,
            run_id=task.run_id,
            event_id=request.resolution_event_id,
            mention=request.mention,
            structural_slot=request.structural_slot,
            expected_entity_type=request.expected_entity_type,
            authority_domain_status=domain_status,
            authority_domain_reason_code=domain_reason,
            authority_domain_error_id=None,
            raw_candidate_refs=tuple(
                RawResolutionCandidateRef(candidate_kind=kind, candidate_id=candidate_id)
                for kind, candidate_id in sorted(raw_keys)
            ),
            candidates=ordered_candidates,
            candidate_audits=ordered_audits,
            authority_evidence=ordered_evidence,
            authority_source_ids=tuple(sorted({claim.source_id for claim in ordered_evidence})),
            ontology_constraints=tuple(
                sorted({f"slot:{request.structural_slot}", f"type:{request.expected_entity_type}"})
            ),
            schema_slice_id=request.schema_slice_id,
            schema_snapshot_sha256=request.schema_snapshot_sha256,
            rejected_candidate_ids=rejected,
            remaining_tool_budget=3 if model_mediated else 0,
            decision=decision,
        ),
        binding=binding,
    )
    model_calls: tuple[ModelCallRecord, ...] = ()
    traces: tuple[ToolTraceEntry, ...] = ()
    if model_mediated:
        semantic = run_semantic_resolution_agent(
            task=resolution_task,
            binding=binding,
            tool_model_factory=semantic_resolution_tool_model_factory,
        )
        proposal, decision, limitation = (
            semantic.proposal,
            semantic.proposal.decision,
            semantic.proposal.limitation,
        )
        selected = next(
            (
                candidate
                for candidate in eligible
                if candidate.candidate_id == proposal.selected_candidate_id
            ),
            None,
        )
        model_calls, traces = semantic.model_calls, semantic.tool_traces
    else:
        assert decision is not None
        support_ids = tuple(sorted(selected.authority_evidence_ids)) if selected else ()
        support_sources = tuple(
            sorted(
                {claim.source_id for claim in ordered_evidence if claim.evidence_id in support_ids}
            )
        )
        proposal = seal_resolution_proposal(
            task=resolution_task,
            fields=ResolutionProposalFields(
                resolution_proposal_id=stable_contract_id(
                    "resolution-proposal",
                    task_id,
                    decision.value,
                    selected.candidate_id if selected else "NONE",
                    canonical_id_tuple_token(rejected, sort_values=True),
                    canonical_id_tuple_token(support_ids, sort_values=True),
                ),
                run_id=task.run_id,
                task_id=task_id,
                task_payload_checksum=resolution_task.payload_checksum,
                event_id=request.resolution_event_id,
                mention=request.mention,
                structural_slot=request.structural_slot,
                expected_entity_type=request.expected_entity_type,
                selected_candidate_id=selected.candidate_id if selected else None,
                rejected_candidate_ids=rejected,
                decision=decision,
                supporting_evidence_claim_ids=support_ids,
                authority_source_ids=support_sources,
                tool_trace_ids=(),
                limitation=limitation,
            ),
            binding=binding,
        )
    if decision is ResolutionDecision.ACCEPTED and selected is None:
        raise ValueError("accepted semantic resolution did not retain its candidate")
    status = (
        AgentStatus.RESOLVED
        if decision is ResolutionDecision.ACCEPTED
        else AgentStatus.BLOCKED
        if decision is ResolutionDecision.BLOCKED
        else AgentStatus.ABSTAIN
    )
    claim = (
        EvidenceClaim(
            field_name="controlled_facility" if domain == "facility" else "operational_term",
            value=selected.candidate_id,
            ontology_target=selected.ontology_class_prefixed,
            evidence_text=request.advisory_evidence.strip(),
            source_id=request.source_id,
            canonical_ref=selected.candidate_id,
        )
        if selected is not None
        else None
    )
    trace = ToolTraceEntry(
        tool="lookup_nasr_facility" if domain == "facility" else "resolve_term_registry",
        parameters={"mention": request.mention},
        result_refs=[task_id, *([selected.candidate_id] if selected is not None else [])],
    )
    return AuthorityResolutionResult(
        evidence_card=EvidenceCard(
            agent_role=domain,
            status=status,
            claims=[claim] if claim else [],
            canonical_refs=[selected.candidate_id] if selected else [],
            source_ids=[request.source_id] if request.source_id else [],
            uncertainties=[limitation] if limitation else [],
            tool_trace=[trace],
            decision_basis=f"{decision.value}: {limitation or 'unique eligible authority candidate'}; resolution_task_id={task_id}; tool_version={request.resolution_tool_version}",
        ),
        domain_outcome=ResolutionDomainOutcome(
            domain=domain,
            required_for_case=True,
            decision=decision,
            task_id=task_id,
            task_payload_checksum=resolution_task.payload_checksum,
            resolution_proposal_id=proposal.resolution_proposal_id,
            limitation_code=limitation,
            error_id=stable_contract_id(
                "resolution-error", task.run_id, domain, limitation or "SEMANTIC_RESOLUTION_BLOCKED"
            )
            if decision is ResolutionDecision.BLOCKED
            else None,
        ),
        authority_source_records=tuple(sorted(records, key=lambda record: record.source_id)),
        resolution_task=resolution_task,
        resolution_proposal=proposal,
        resolution_tool_traces=traces,
        model_calls=tuple(model_calls),
    )


def _resolve_or_block(**kwargs: Any) -> AuthorityResolutionResult:
    try:
        return _resolve(**kwargs)
    except (AssertionError, TypeError, ValueError):
        return _blocked(
            task=kwargs["task"],
            request=kwargs["request"],
            domain=kwargs["domain"],
            reason_code="RESOLUTION_CONTRACT_VALIDATION_FAILED",
        )


def resolve_facility_authority(
    *,
    task: AgentTask,
    request: FacilityAuthorityResolutionInput,
    semantic_resolution_tool_model_factory: ToolModelFactory | None = None,
) -> AuthorityResolutionResult:
    return _resolve_or_block(
        task=task,
        request=request,
        domain="facility",
        semantic_resolution_tool_model_factory=semantic_resolution_tool_model_factory,
    )


def resolve_terminology_authority(
    *,
    task: AgentTask,
    request: TerminologyAuthorityResolutionInput,
    semantic_resolution_tool_model_factory: ToolModelFactory | None = None,
) -> AuthorityResolutionResult:
    return _resolve_or_block(
        task=task,
        request=request,
        domain="terminology",
        semantic_resolution_tool_model_factory=semantic_resolution_tool_model_factory,
    )


__all__ = [
    "AUTHORITY_RESOLUTION_TOOL_VERSION",
    "AuthorityResolutionResult",
    "FacilityAuthorityResolutionInput",
    "TerminologyAuthorityResolutionInput",
    "resolve_facility_authority",
    "resolve_terminology_authority",
]
