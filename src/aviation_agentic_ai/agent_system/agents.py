"""The five Agent roles of the multi-Agent KG system (design §§8–12).

Each Agent follows the bounded lifecycle of design §7: receive task, inspect
permitted context, choose an allowed tool when needed, collect authority-backed
evidence, decide resolved/abstain/profile_gap/blocked, emit an EvidenceCard,
Graph Patch, or answer.

Tool boundary enforcement: an Agent may only call the tools named in its
``allowed_tools``. Unique authority paths make NO model call; a model call is
used only for a genuine multi-candidate disambiguation, and even then the
Agent may only select from authority-supplied candidates. Every accepted
EvidenceClaim carries ``source_id`` and ``evidence_text``.

Prompt policy (design §16): every model call assembles the fixed 6-message
sequence from the frozen catalog via :mod:`aviation_agentic_ai.agent_system.prompts`.
Runtime code never rewrites, extends, or replaces the prompt text.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from aviation_agentic_ai.agent_system.contracts import (
    AgentResult,
    AgentStatus,
    AgentTask,
    EvidenceCard,
    EvidenceClaim,
    ModelCallRecord,
    SourceFamily,
    SourceRecord,
    ToolTraceEntry,
)
from aviation_agentic_ai.agent_system.authority_evidence import (
    AuthoritySourceContentFields,
    AuthorityBuildStatus,
    AuthorityCandidateBuildResult,
    canonical_authority_source_content,
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
from aviation_agentic_ai.agent_system.prompts import assemble_prompt
from aviation_agentic_ai.agent_system.schema_guide import SchemaGuide
from aviation_agentic_ai.agent_system.semantic_resolution import (
    run_semantic_resolution_agent,
)

# A model invoker takes (agent_role, template_variables) and returns a
# ModelCallRecord. The invoker is responsible for assembling the frozen
# 6-message prompt from the catalog (design §16) and recording the call
# ledger (agent, prompt_set_id, prompt_version, attempt).
ModelInvoker = Callable[[str, dict[str, Any]], ModelCallRecord]
ToolModelFactory = Callable[[list[Any]], Any]

# Shared English insufficient-evidence fallback for the active Query interface
# (plan §13 T4: English-only active interface). Defined here so both the Query
# Agent (agents.py) and the query runtime (query.py) reference one constant
# without a circular import.
INSUFFICIENT_EVIDENCE_ANSWER = "Insufficient graph evidence."


@dataclass
class AdvisoryMentions:
    """Deterministic structured-field parse of an advisory (design §8.2).

    Each normalized value is paired with an exact source span in
    ``evidence_spans`` (keyed by the same field name used in EvidenceClaim).
    The Formal Graph Kernel requires ``claim.evidence_text in source.content``
    (plan §5.2), so every span is copied verbatim from the advisory text.
    """

    event_type: str | None = None
    controlled_facility: str | None = None
    operational_term: str | None = None
    effective_start: str | None = None
    effective_end: str | None = None
    status: str | None = None
    advisory_number: str | None = None
    extension_probability: str | None = None
    impacting_condition: str | None = None
    element_type_code: str | None = None
    facility_structural_slot: str | None = None
    facility_expected_entity_type: str | None = None
    term_structural_slot: str | None = None
    term_expected_entity_type: str | None = None
    evidence_spans: dict[str, str] = field(default_factory=dict)


FACILITY_SLOT = "controlled_nas_element"
TERM_SLOT = "traffic_management_initiative_type"
ELEMENT_TYPE_TO_ENTITY_TYPE = {
    "APT": "airport",
    "ARTCC": "artcc",
}


_CTL_ELEMENT_RE = re.compile(r"CTL\s*ELEMENT\s*:\s*([A-Z]{2,5})", re.IGNORECASE)
_ELEMENT_TYPE_RE = re.compile(r"ELEMENT\s*TYPE\s*:\s*([A-Z][A-Z0-9_-]*)", re.IGNORECASE)
_EVENT_RE = re.compile(
    r"\b(GDP|GS|GROUND\s*DELAY\s*PROGRAM|GROUND\s*STOP)\b", re.IGNORECASE
)
_PERIOD_RE = re.compile(
    r"(?:GROUND\s*STOP\s*PERIOD|PERIOD|GDP\s*CNX\s*PERIOD)\s*:\s*"
    r"(\d{2}/\d{2,4}\w*\s*-\s*\d{2}/\d{2,4}\w*)",
    re.IGNORECASE,
)
_ADVZY_RE = re.compile(r"ADVZY\s*(\d{3})", re.IGNORECASE)
_CNX_RE = re.compile(r"\bCNX\b", re.IGNORECASE)
_EXT_PROB_RE = re.compile(
    r"PROBABILITY\s+OF\s+EXTENSION\s*:\s*([A-Z]+)", re.IGNORECASE
)
_IMPACTING_RE = re.compile(
    r"IMPACTING\s+CONDITION\s*:\s*([A-Z][A-Z /]*?)"
    r"(?=\s+(?:COMMENTS?|PROBABILITY|EFFECTIVE|CTL|GROUND|GDP|CUMULATIVE)"
    r"\s*:|[\r\n]|$)",
    re.IGNORECASE,
)
# Advisory header date: ``ADVZY <num> <facility> <MM>/<DD>/<YYYY>``. This is the
# deterministic calendar anchor for the period tokens (plan §12). The header
# date and the period day must agree; otherwise the period is not uniquely
# anchored and the time claim is omitted (no guessing).
_HEADER_DATE_RE = re.compile(
    r"ADVZY\s*\d{3}\s+\S+\s+(\d{2})/(\d{2})/(\d{4})", re.IGNORECASE
)
# A period token ``DD/HHMM[Z]``.
_PERIOD_TOKEN_RE = re.compile(r"^(\d{1,2})/(\d{2})(\d{2})Z?$")


def _anchor_period_value(
    token: str,
    year: int,
    month: int,
    header_day: int,
    *,
    allow_next_day: bool = False,
) -> str | None:
    """Anchor a ``DD/HHMMZ`` period token to a full UTC timestamp (plan §12).

    Returns ``YYYY-MM-DDTHH:MM:SSZ`` when the token's day agrees with the
    header day. An end token may also name the immediately following calendar
    day when ``allow_next_day`` is true. Other mismatches return ``None``. The
    raw source substring is preserved separately as ``evidence_text``.
    """

    m = _PERIOD_TOKEN_RE.match(token.strip())
    if not m:
        return None
    day, hour, minute = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        header_date = datetime(year, month, header_day, tzinfo=UTC)
    except ValueError:
        return None
    target_date = header_date
    if day != header_day:
        next_date = header_date + timedelta(days=1)
        if not allow_next_day or day != next_date.day:
            return None
        target_date = next_date
    try:
        anchored = target_date.replace(hour=hour, minute=minute)
    except ValueError:
        return None
    return anchored.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_structured_fields(advisory_text: str) -> AdvisoryMentions:
    """Deterministic structured-field parser (design §13; not an Agent).

    Captures the exact source span for each field so downstream EvidenceClaims
    can satisfy ``claim.evidence_text in source.content`` (plan §5.2).

    Plan §12: effective-period tokens are anchored to the full UTC date carried
    by the advisory header before they become EvidenceClaim values. The raw
    source substring (``DD/HHMMZ``) is preserved separately as evidence_text.
    If a period cannot be anchored to one full date deterministically, the time
    claim is omitted (no guessing).
    """

    mentions = AdvisoryMentions()
    ctl = _CTL_ELEMENT_RE.search(advisory_text)
    if ctl:
        mentions.controlled_facility = ctl.group(1).upper()
        mentions.evidence_spans["controlled_facility"] = ctl.group(0)
    event = _EVENT_RE.search(advisory_text)
    if event:
        raw = event.group(1).upper().replace(" ", "")
        if "GROUNDDELAYPROGRAM" in raw:
            mentions.event_type = "GDP"
        elif "GROUNDSTOP" in raw:
            mentions.event_type = "GS"
        else:
            mentions.event_type = raw
        mentions.operational_term = mentions.event_type
        mentions.evidence_spans["event_type"] = event.group(0)
        mentions.evidence_spans["operational_term"] = event.group(0)
    element_type = _ELEMENT_TYPE_RE.search(advisory_text)
    if element_type:
        mentions.element_type_code = element_type.group(1).upper()
    if mentions.event_type in {"GDP", "GS"}:
        if mentions.controlled_facility:
            mentions.facility_structural_slot = FACILITY_SLOT
            if mentions.element_type_code:
                mentions.facility_expected_entity_type = (
                    ELEMENT_TYPE_TO_ENTITY_TYPE.get(mentions.element_type_code)
                )
        mentions.term_structural_slot = TERM_SLOT
        mentions.term_expected_entity_type = "traffic_management_initiative"
    # Deterministic calendar anchor from the advisory header (plan §12).
    header_date = _HEADER_DATE_RE.search(advisory_text)
    period = _PERIOD_RE.search(advisory_text)
    if period and header_date:
        span = period.group(1)
        parts = re.split(r"\s*-\s*", span)
        if len(parts) == 2:
            year = int(header_date.group(3))
            month = int(header_date.group(1))
            header_day = int(header_date.group(2))
            start_token = parts[0].strip()
            end_token = parts[1].strip()
            start_val = _anchor_period_value(start_token, year, month, header_day)
            end_val = _anchor_period_value(
                end_token,
                year,
                month,
                header_day,
                allow_next_day=True,
            )
            # Only emit a time claim when the period is uniquely anchored to the
            # header date. Preserve the raw substring as evidence_text.
            if start_val is not None:
                mentions.effective_start = start_val
                mentions.evidence_spans["effective_start"] = start_token
            if end_val is not None:
                mentions.effective_end = end_val
                mentions.evidence_spans["effective_end"] = end_token
    advzy = _ADVZY_RE.search(advisory_text)
    if advzy:
        mentions.advisory_number = advzy.group(1)
        mentions.evidence_spans["advisory_number"] = advzy.group(0)
    if _CNX_RE.search(advisory_text):
        mentions.status = "CNX"
        mentions.evidence_spans["status"] = _CNX_RE.search(advisory_text).group(0)
    ext_prob = _EXT_PROB_RE.search(advisory_text)
    if ext_prob:
        mentions.extension_probability = ext_prob.group(1).upper()
        mentions.evidence_spans["extension_probability"] = ext_prob.group(0)
    impacting = _IMPACTING_RE.search(advisory_text)
    if impacting:
        # Normalize to the leading single-word cause (e.g. "WEATHER") while
        # keeping the full exact span as evidence.
        raw = impacting.group(1).strip()
        first_token = re.split(r"\s*/\s*|\s+", raw, maxsplit=1)[0].lower()
        mentions.impacting_condition = first_token
        mentions.evidence_spans["impacting_condition"] = impacting.group(0)
    return mentions


# ---------------------------------------------------------------------------
# Tool boundary enforcement
# ---------------------------------------------------------------------------


class ToolNotAllowedError(RuntimeError):
    """Raised when an Agent attempts a tool not in its allowed_tools."""


def _check_tool(task: AgentTask, tool: str) -> None:
    if tool not in task.allowed_tools:
        raise ToolNotAllowedError(
            f"tool {tool!r} not permitted for task (allowed: {task.allowed_tools})"
        )


def _trace(tool: str, **params: Any) -> ToolTraceEntry:
    safe = {k: str(v) for k, v in params.items() if v is not None}
    return ToolTraceEntry(tool=tool, parameters=safe)


# ---------------------------------------------------------------------------
# Advisory Agent (design §8)
# ---------------------------------------------------------------------------


def run_advisory_agent(
    *,
    task: AgentTask,
    advisory: SourceRecord,
    event_classes: list[str],
    mentions: AdvisoryMentions,
    model_invoker: ModelInvoker | None = None,
) -> AgentResult:
    """Convert a raw advisory into a source-bounded evidence card.

    Makes no facility/term canonicalization. Uses the deterministic parse.

    Plan §12 Advisory-call policy: the Advisory Agent must NOT make a model call
    whose response is not consumed by a bounded output parser and cannot change
    the EvidenceCard. For this vertical slice the deterministic parse is the sole
    producer of advisory claims; a complete parse therefore makes zero Advisory
    model calls, and an incomplete/ambiguous parse abstains without a model call
    (a model-assisted fallback is deferred until its output contract and consumer
    are explicitly designed). ``model_invoker`` is accepted for API symmetry but
    is never invoked here.
    """

    del model_invoker  # §12: the Advisory Agent makes no model call.
    for tool in ("get_advisory", "parse_structured_fields", "get_schema_event_classes"):
        _check_tool(task, tool)
    source_id = advisory.source_id
    tool_trace = [
        _trace("get_advisory", source_id=source_id),
        _trace("parse_structured_fields"),
        _trace("get_schema_event_classes", count=len(event_classes)),
    ]
    # Every EvidenceClaim must carry an exact source span (plan §5.2): the
    # evidence_text must appear verbatim in the advisory content. Synthetic
    # phrases such as "event mention GS" are rejected by the Formal Graph
    # Kernel. We assert source containment here so a regression is caught early.
    claims: list[EvidenceClaim] = []
    for field_name, value in (
        ("event_type", mentions.event_type),
        ("controlled_facility", mentions.controlled_facility),
        ("operational_term", mentions.operational_term),
        ("effective_start", mentions.effective_start),
        ("effective_end", mentions.effective_end),
        ("status", mentions.status),
        ("advisory_number", mentions.advisory_number),
        ("extension_probability", mentions.extension_probability),
        ("impacting_condition", mentions.impacting_condition),
    ):
        if not value:
            continue
        span = mentions.evidence_spans.get(field_name)
        if span is None:
            # No exact span captured for this field; do not emit a claim whose
            # evidence the Formal Graph Kernel would reject.
            continue
        # Plan §5.2 hard assertion: the evidence text must be source-contained.
        assert span in advisory.content, (
            f"advisory evidence span for {field_name!r} is not source-contained"
        )
        claims.append(EvidenceClaim(
            field_name=field_name, value=value,
            evidence_text=span, source_id=source_id,
        ))

    status = AgentStatus.RESOLVED if claims else AgentStatus.ABSTAIN
    # §12: zero Advisory model calls. The deterministic parse is the sole
    # producer; an incomplete parse abstains without a model call.
    model_calls: list[ModelCallRecord] = []

    card = EvidenceCard(
        agent_role="advisory",
        status=status,
        claims=claims,
        source_ids=[source_id],
        tool_trace=tool_trace,
        decision_basis="deterministic structured-field parse of the advisory",
    )
    return AgentResult(status=status, evidence_card=card, model_calls=model_calls)


# ---------------------------------------------------------------------------
# Facility Agent (design §9)
# ---------------------------------------------------------------------------


@dataclass
class FacilityCandidates:
    """Authority facility candidates for a mention (design §9.4)."""

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


@dataclass(frozen=True)
class CompatibilityResolutionResult:
    """Strict resolution result plus the unchanged legacy Agent envelope."""

    agent_result: AgentResult
    domain_outcome: ResolutionDomainOutcome
    authority_source_records: tuple[SourceRecord, ...]
    resolution_task: ResolutionTask
    resolution_proposal: ResolutionProposal
    resolution_tool_traces: tuple[ToolTraceEntry, ...] = ()


def _compatibility_requested(candidates: FacilityCandidates | TermCandidates) -> bool:
    """Return true once any Task 5 execution binding is supplied."""

    return any(
        (
            candidates.resolution_event_id,
            candidates.resolution_event_mention,
            candidates.run_started_at,
            candidates.schema_slice_id,
            candidates.schema_snapshot_sha256,
            candidates.resolution_tool_version,
            candidates.authority_domain_status,
            candidates.authority_domain_reason_code,
            candidates.authority_domain_error_id,
            candidates.authority_candidate_results,
        )
    )


def _candidate_payload_checksum(candidate: Any) -> str:
    payload = candidate.model_dump(
        mode="python",
        exclude_computed_fields=True,
    )
    canonical = canonicalize_contract_value(payload)
    encoded = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _candidate_key(candidate: Any, domain: str) -> tuple[str, str]:
    return (
        "facility" if domain == "facility" else "term",
        candidate.entity_id if domain == "facility" else candidate.term_id,
    )


def _safe_binding(
    task: AgentTask,
    candidates: FacilityCandidates | TermCandidates,
) -> ContractExecutionBinding:
    started_at = candidates.run_started_at
    if (
        started_at is None
        or started_at.tzinfo is None
        or started_at.utcoffset() is None
    ):
        started_at = datetime(1970, 1, 1, tzinfo=UTC)
    return ContractExecutionBinding(
        run_id=task.run_id,
        created_at=started_at.astimezone(UTC),
        tool_version=(
            candidates.resolution_tool_version or "resolution-compatibility-v1"
        ),
    )


def _terminal_compatibility_result(
    *,
    task: AgentTask,
    candidates: FacilityCandidates | TermCandidates,
    domain: str,
    reason_code: str,
    decision: ResolutionDecision,
) -> CompatibilityResolutionResult:
    """Return a sealed terminal result without inspecting candidate rows."""

    if decision not in {
        ResolutionDecision.BLOCKED,
        ResolutionDecision.INSUFFICIENT,
    }:
        raise ValueError("terminal compatibility decision is unsupported")
    blocked = decision is ResolutionDecision.BLOCKED
    domain_status = (
        CandidateBuildStatus.BLOCKED
        if blocked
        else CandidateBuildStatus.INSUFFICIENT
    )
    agent_status = AgentStatus.BLOCKED if blocked else AgentStatus.ABSTAIN
    binding = _safe_binding(task, candidates)
    event_id = candidates.resolution_event_id or "INVALID_RESOLUTION_EVENT"
    mention = candidates.mention or "MISSING_EVENT_MENTION"
    structural_slot = candidates.structural_slot or "INVALID_STRUCTURAL_SLOT"
    expected_entity_type = (
        candidates.expected_entity_type or "INVALID_EXPECTED_ENTITY_TYPE"
    )
    schema_slice_id = candidates.schema_slice_id or "INVALID_SCHEMA_SLICE"
    schema_checksum = (
        candidates.schema_snapshot_sha256
        if re.fullmatch(r"[0-9a-f]{64}", candidates.schema_snapshot_sha256 or "")
        else "0" * 64
    )
    error_id = (
        stable_contract_id(
            "resolution-error",
            task.run_id,
            domain,
            reason_code,
        )
        if blocked
        else None
    )
    task_id = stable_contract_id(
        "resolution-task",
        task.run_id,
        event_id,
        mention,
        structural_slot,
        expected_entity_type,
        canonical_id_tuple_token((), sort_values=True),
        schema_slice_id,
        schema_checksum,
    )
    sealed_task = seal_resolution_task(
        fields=ResolutionTaskFields(
            task_id=task_id,
            run_id=task.run_id,
            event_id=event_id,
            mention=mention,
            structural_slot=structural_slot,
            expected_entity_type=expected_entity_type,
            authority_domain_status=domain_status,
            authority_domain_reason_code=reason_code,
            authority_domain_error_id=error_id,
            raw_candidate_refs=(),
            candidates=(),
            candidate_audits=(),
            authority_evidence=(),
            authority_source_ids=(),
            ontology_constraints=(),
            schema_slice_id=schema_slice_id,
            schema_snapshot_sha256=schema_checksum,
            rejected_candidate_ids=(),
            remaining_tool_budget=0,
            decision=decision,
        ),
        binding=binding,
    )
    proposal_id = stable_contract_id(
        "resolution-proposal",
        task_id,
        decision.value,
        "NONE",
        canonical_id_tuple_token((), sort_values=True),
        canonical_id_tuple_token((), sort_values=True),
    )
    proposal = seal_resolution_proposal(
        task=sealed_task,
        fields=ResolutionProposalFields(
            resolution_proposal_id=proposal_id,
            run_id=task.run_id,
            task_id=task_id,
            task_payload_checksum=sealed_task.payload_checksum,
            event_id=event_id,
            mention=mention,
            structural_slot=structural_slot,
            expected_entity_type=expected_entity_type,
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
        status=agent_status,
        source_ids=[candidates.source_id] if candidates.source_id else [],
        uncertainties=[reason_code] if not blocked else [],
        decision_basis=(
            f"{decision.value}: {reason_code}; resolution_task_id={task_id}; "
            f"tool_version={binding.tool_version}"
        ),
    )
    return CompatibilityResolutionResult(
        agent_result=AgentResult(
            status=agent_status,
            evidence_card=card,
            failure_reason=reason_code if blocked else None,
        ),
        domain_outcome=ResolutionDomainOutcome(
            domain=domain,
            required_for_case=True,
            decision=decision,
            task_id=task_id,
            task_payload_checksum=sealed_task.payload_checksum,
            resolution_proposal_id=proposal.resolution_proposal_id,
            limitation_code=reason_code,
            error_id=error_id,
        ),
        authority_source_records=(),
        resolution_task=sealed_task,
        resolution_proposal=proposal,
    )


def _blocked_compatibility_result(
    *,
    task: AgentTask,
    candidates: FacilityCandidates | TermCandidates,
    domain: str,
    reason_code: str,
) -> CompatibilityResolutionResult:
    """Return a sealed fail-closed result without trusting malformed rows."""

    return _terminal_compatibility_result(
        task=task,
        candidates=candidates,
        domain=domain,
        reason_code=reason_code,
        decision=ResolutionDecision.BLOCKED,
    )


def _insufficient_compatibility_result(
    *,
    task: AgentTask,
    candidates: FacilityCandidates | TermCandidates,
    domain: str,
    reason_code: str,
) -> CompatibilityResolutionResult:
    """Return an explicit authority insufficiency before candidate inspection."""

    return _terminal_compatibility_result(
        task=task,
        candidates=candidates,
        domain=domain,
        reason_code=reason_code,
        decision=ResolutionDecision.INSUFFICIENT,
    )


def _normalized_resolution_event_mention(value: str) -> str:
    normalized = value.strip().upper()
    return normalized or "MISSING_EVENT_MENTION"


def _validate_authority_source_record(
    row: AuthorityCandidateBuildResult,
    *,
    domain: str,
) -> SourceRecord:
    """Revalidate one source record against its checksum-bound evidence."""

    if row.evidence_claim is None or row.source_record is None:
        raise ValueError("authority source record requires bound evidence")
    evidence = type(row.evidence_claim).model_validate(
        row.evidence_claim.model_dump(mode="python")
    )
    source_record = SourceRecord.model_validate(
        row.source_record.model_dump(mode="python")
    )
    expected_family = (
        SourceFamily.NASR_FACILITY
        if domain == "facility"
        else SourceFamily.FAA_TERM
    )
    if source_record.family is not expected_family:
        raise ValueError("authority source record family is outside the domain")
    expected_kind = "facility" if domain == "facility" else "term"
    if (
        row.candidate_kind != expected_kind
        or evidence.candidate_id != row.candidate_id
    ):
        raise ValueError("authority source record candidate binding is invalid")
    if source_record.source_id != evidence.source_id:
        raise ValueError("authority source record differs from evidence source")
    snapshot_sha256 = hashlib.sha256(
        source_record.content.encode("utf-8")
    ).hexdigest()
    if snapshot_sha256 != evidence.source_snapshot_sha256:
        raise ValueError("authority source record checksum differs from evidence")
    fields = AuthoritySourceContentFields.model_validate_json(
        source_record.content
    )
    if (
        fields.candidate_id != row.candidate_id
        or fields.candidate_kind != expected_kind
        or fields.authority_source_ref != evidence.authority_source_ref
        or canonical_authority_source_content(fields) != source_record.content
    ):
        raise ValueError("authority source record is not canonically bound")
    return source_record


def _resolve_compatibility_validated(
    *,
    task: AgentTask,
    candidates: FacilityCandidates | TermCandidates,
    domain: str,
    semantic_resolution_tool_model_factory: ToolModelFactory | None = None,
) -> CompatibilityResolutionResult:
    """Audit authority candidates and deterministically map one bounded result."""

    for tool in (
        ("lookup_nasr_facility", "lookup_artcc", "resolve_facility_alias")
        if domain == "facility"
        else (
            "lookup_faa_glossary",
            "lookup_pcg_term",
            "resolve_term_registry",
            "resolve_schema_event_class",
        )
    ):
        _check_tool(task, tool)

    required_bindings = (
        candidates.mention,
        candidates.source_id,
        candidates.resolution_event_id,
        candidates.resolution_event_mention,
        candidates.run_started_at,
        candidates.structural_slot,
        candidates.expected_entity_type,
        candidates.schema_slice_id,
        candidates.schema_snapshot_sha256,
        candidates.resolution_tool_version,
        candidates.authority_domain_status,
    )
    if (
        not all(required_bindings)
        or candidates.resolution_tool_version != "resolution-compatibility-v1"
        or not re.fullmatch(
            r"[0-9a-f]{64}",
            candidates.schema_snapshot_sha256 or "",
        )
    ):
        return _blocked_compatibility_result(
            task=task,
            candidates=candidates,
            domain=domain,
            reason_code="RESOLUTION_EXECUTION_BINDING_INVALID",
        )
    if (
        candidates.run_started_at is None
        or candidates.run_started_at.tzinfo is None
        or candidates.run_started_at.utcoffset() is None
    ):
        return _blocked_compatibility_result(
            task=task,
            candidates=candidates,
            domain=domain,
            reason_code="RESOLUTION_RUN_TIMESTAMP_INVALID",
        )
    expected_resolution_event_id = stable_contract_id(
        "resolution-event",
        task.run_id,
        task.source_id,
        _normalized_resolution_event_mention(
            candidates.resolution_event_mention
        ),
    )
    if candidates.resolution_event_id != expected_resolution_event_id:
        return _blocked_compatibility_result(
            task=task,
            candidates=candidates,
            domain=domain,
            reason_code="RESOLUTION_EVENT_BINDING_MISMATCH",
        )
    if candidates.authority_domain_status is AuthorityBuildStatus.BLOCKED:
        return _blocked_compatibility_result(
            task=task,
            candidates=candidates,
            domain=domain,
            reason_code=(
                candidates.authority_domain_reason_code
                or f"{domain.upper()}_AUTHORITY_BLOCKED"
            ),
        )
    if candidates.authority_domain_status is AuthorityBuildStatus.INSUFFICIENT:
        return _insufficient_compatibility_result(
            task=task,
            candidates=candidates,
            domain=domain,
            reason_code=(
                candidates.authority_domain_reason_code
                or f"{domain.upper()}_AUTHORITY_INSUFFICIENT"
            ),
        )

    raw_keys = [_candidate_key(row, domain) for row in candidates.candidates]
    result_keys = [
        (row.candidate_kind, row.candidate_id)
        for row in candidates.authority_candidate_results
    ]
    if (
        len(raw_keys) != len(set(raw_keys))
        or len(result_keys) != len(set(result_keys))
        or set(raw_keys) != set(result_keys)
    ):
        return _blocked_compatibility_result(
            task=task,
            candidates=candidates,
            domain=domain,
            reason_code="AUTHORITY_CANDIDATE_SET_MISMATCH",
        )

    result_by_key = {
        (row.candidate_kind, row.candidate_id): row
        for row in candidates.authority_candidate_results
    }
    ordered_results = tuple(result_by_key[key] for key in sorted(raw_keys))
    if any(row.status is AuthorityBuildStatus.BLOCKED for row in ordered_results):
        effective_status = AuthorityBuildStatus.BLOCKED
    elif any(
        row.status is AuthorityBuildStatus.INSUFFICIENT for row in ordered_results
    ):
        effective_status = AuthorityBuildStatus.INSUFFICIENT
    else:
        effective_status = AuthorityBuildStatus.OK
    if effective_status is AuthorityBuildStatus.BLOCKED:
        return _blocked_compatibility_result(
            task=task,
            candidates=candidates,
            domain=domain,
            reason_code=next(
                (
                    row.reason_code
                    for row in ordered_results
                    if row.status is AuthorityBuildStatus.BLOCKED
                ),
                "AUTHORITY_CANDIDATE_BLOCKED",
            ),
        )
    if (
        candidates.authority_domain_status is AuthorityBuildStatus.OK
        and effective_status is AuthorityBuildStatus.INSUFFICIENT
    ):
        return _blocked_compatibility_result(
            task=task,
            candidates=candidates,
            domain=domain,
            reason_code="AUTHORITY_DOMAIN_STATUS_MISMATCH",
        )

    audits: list[ResolutionCandidateAudit] = []
    validated_candidates = []
    authority_evidence = []
    authority_records = []
    for row in ordered_results:
        assert row.candidate is not None
        validated_candidates.append(row.candidate)
        checksum = _candidate_payload_checksum(row.candidate)
        build_status = CandidateBuildStatus(row.status.value)
        evidence_id = row.evidence_claim.evidence_id if row.evidence_claim else None
        source_id = row.source_record.source_id if row.source_record else None
        audit_id = stable_contract_id(
            "resolution-candidate-audit",
            row.candidate_id,
            row.candidate_kind,
            build_status.value,
            checksum,
            evidence_id or "NONE",
            source_id or "NONE",
            row.reason_code or "NONE",
            row.error_id or "NONE",
        )
        audits.append(
            ResolutionCandidateAudit(
                candidate_audit_id=audit_id,
                candidate_id=row.candidate_id,
                candidate_kind=row.candidate_kind,
                build_status=build_status,
                candidate_payload_checksum=checksum,
                evidence_id=evidence_id,
                source_id=source_id,
                reason_code=row.reason_code,
                error_id=row.error_id,
            )
        )
        if row.evidence_claim:
            authority_evidence.append(row.evidence_claim)
        if row.source_record:
            authority_records.append(
                _validate_authority_source_record(row, domain=domain)
            )

    domain_status = CandidateBuildStatus(effective_status.value)
    domain_reason = candidates.authority_domain_reason_code or None
    if domain_status is CandidateBuildStatus.INSUFFICIENT and not domain_reason:
        domain_reason = next(
            (
                row.reason_code
                for row in ordered_results
                if row.status is AuthorityBuildStatus.INSUFFICIENT
            ),
            "AUTHORITY_EVIDENCE_INSUFFICIENT",
        )
    if not candidates.advisory_evidence.strip():
        domain_status = CandidateBuildStatus.INSUFFICIENT
        domain_reason = "ADVISORY_EVIDENCE_MISSING"

    eligible = [candidate for candidate in validated_candidates if candidate.eligible]
    model_mediated = False
    if domain_status is CandidateBuildStatus.INSUFFICIENT:
        decision = ResolutionDecision.INSUFFICIENT
        selected = None
        limitation = domain_reason
    elif len(eligible) == 1:
        decision = ResolutionDecision.ACCEPTED
        selected = eligible[0]
        limitation = None
    elif len(eligible) > 1:
        decision = None
        selected = None
        limitation = None
        model_mediated = True
    else:
        decision = ResolutionDecision.INSUFFICIENT
        selected = None
        limitation = "NO_ELIGIBLE_AUTHORITY_CANDIDATE"

    raw_refs = tuple(
        RawResolutionCandidateRef(candidate_kind=kind, candidate_id=candidate_id)
        for kind, candidate_id in sorted(raw_keys)
    )
    ordered_candidates = tuple(
        sorted(validated_candidates, key=lambda row: row.candidate_id)
    )
    ordered_audits = tuple(
        sorted(audits, key=lambda row: row.candidate_audit_id)
    )
    evidence = tuple(
        sorted(authority_evidence, key=lambda row: row.evidence_id)
    )
    authority_source_ids = tuple(sorted({row.source_id for row in evidence}))
    rejected_ids = tuple(
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
        candidates.resolution_event_id,
        candidates.mention,
        candidates.structural_slot,
        candidates.expected_entity_type,
        canonical_id_tuple_token(
            [row.candidate_audit_id for row in ordered_audits],
            sort_values=True,
        ),
        candidates.schema_slice_id,
        candidates.schema_snapshot_sha256,
    )
    binding = _safe_binding(task, candidates)
    sealed_task = seal_resolution_task(
        fields=ResolutionTaskFields(
            task_id=task_id,
            run_id=task.run_id,
            event_id=candidates.resolution_event_id,
            mention=candidates.mention,
            structural_slot=candidates.structural_slot,
            expected_entity_type=candidates.expected_entity_type,
            authority_domain_status=domain_status,
            authority_domain_reason_code=domain_reason,
            authority_domain_error_id=None,
            raw_candidate_refs=raw_refs,
            candidates=ordered_candidates,
            candidate_audits=ordered_audits,
            authority_evidence=evidence,
            authority_source_ids=authority_source_ids,
            ontology_constraints=tuple(
                sorted(
                    {
                        f"slot:{candidates.structural_slot}",
                        f"type:{candidates.expected_entity_type}",
                    }
                )
            ),
            schema_slice_id=candidates.schema_slice_id,
            schema_snapshot_sha256=candidates.schema_snapshot_sha256,
            rejected_candidate_ids=rejected_ids,
            remaining_tool_budget=3 if model_mediated else 0,
            decision=decision,
        ),
        binding=binding,
    )
    model_calls: tuple[ModelCallRecord, ...] = ()
    resolution_tool_traces: tuple[ToolTraceEntry, ...] = ()
    failure_reason: str | None = None
    if model_mediated:
        semantic_result = run_semantic_resolution_agent(
            task=sealed_task,
            binding=binding,
            tool_model_factory=semantic_resolution_tool_model_factory,
        )
        proposal = semantic_result.proposal
        decision = proposal.decision
        limitation = proposal.limitation
        selected = next(
            (
                row
                for row in eligible
                if row.candidate_id == proposal.selected_candidate_id
            ),
            None,
        )
        model_calls = semantic_result.model_calls
        resolution_tool_traces = semantic_result.tool_traces
        failure_reason = semantic_result.failure_reason
    else:
        assert decision is not None
        support_ids = (
            tuple(sorted(selected.authority_evidence_ids)) if selected else ()
        )
        support_sources = tuple(
            sorted(
                {
                    row.source_id
                    for row in evidence
                    if row.evidence_id in support_ids
                }
            )
        )
        proposal_id = stable_contract_id(
            "resolution-proposal",
            task_id,
            decision.value,
            selected.candidate_id if selected else "NONE",
            canonical_id_tuple_token(rejected_ids, sort_values=True),
            canonical_id_tuple_token(support_ids, sort_values=True),
        )
        proposal = seal_resolution_proposal(
            task=sealed_task,
            fields=ResolutionProposalFields(
                resolution_proposal_id=proposal_id,
                run_id=task.run_id,
                task_id=task_id,
                task_payload_checksum=sealed_task.payload_checksum,
                event_id=candidates.resolution_event_id,
                mention=candidates.mention,
                structural_slot=candidates.structural_slot,
                expected_entity_type=candidates.expected_entity_type,
                selected_candidate_id=selected.candidate_id if selected else None,
                rejected_candidate_ids=rejected_ids,
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

    legacy_status = (
        AgentStatus.RESOLVED
        if decision is ResolutionDecision.ACCEPTED
        else AgentStatus.BLOCKED
        if decision is ResolutionDecision.BLOCKED
        else AgentStatus.ABSTAIN
    )
    claim = None
    if selected is not None:
        claim = EvidenceClaim(
            field_name=(
                "controlled_facility"
                if domain == "facility"
                else "operational_term"
            ),
            value=selected.candidate_id,
            ontology_target=selected.ontology_class_prefixed,
            evidence_text=candidates.advisory_evidence.strip(),
            source_id=candidates.source_id,
            canonical_ref=selected.candidate_id,
        )
    trace = ToolTraceEntry(
        tool=(
            "lookup_nasr_facility"
            if domain == "facility"
            else "resolve_term_registry"
        ),
        parameters={"mention": candidates.mention},
        result_refs=[
            task_id,
            *([selected.candidate_id] if selected is not None else []),
        ],
    )
    card = EvidenceCard(
        agent_role=domain,
        status=legacy_status,
        claims=[claim] if claim else [],
        canonical_refs=[selected.candidate_id] if selected else [],
        source_ids=[candidates.source_id] if candidates.source_id else [],
        uncertainties=[limitation] if limitation else [],
        tool_trace=[trace],
        decision_basis=(
            f"{decision.value}: {limitation or 'unique eligible authority candidate'}; "
            f"resolution_task_id={task_id}; "
            f"tool_version={candidates.resolution_tool_version}"
        ),
    )
    return CompatibilityResolutionResult(
        agent_result=AgentResult(
            status=legacy_status,
            evidence_card=card,
            model_calls=list(model_calls),
            failure_reason=(
                failure_reason or limitation
                if decision is ResolutionDecision.BLOCKED
                else None
            ),
        ),
        domain_outcome=ResolutionDomainOutcome(
            domain=domain,
            required_for_case=True,
            decision=decision,
            task_id=task_id,
            task_payload_checksum=sealed_task.payload_checksum,
            resolution_proposal_id=proposal.resolution_proposal_id,
            limitation_code=limitation,
            error_id=(
                stable_contract_id(
                    "resolution-error",
                    task.run_id,
                    domain,
                    limitation or "SEMANTIC_RESOLUTION_BLOCKED",
                )
                if decision is ResolutionDecision.BLOCKED
                else None
            ),
        ),
        authority_source_records=tuple(
            sorted(authority_records, key=lambda row: row.source_id)
        ),
        resolution_task=sealed_task,
        resolution_proposal=proposal,
        resolution_tool_traces=resolution_tool_traces,
    )


def _resolve_compatibility(
    *,
    task: AgentTask,
    candidates: FacilityCandidates | TermCandidates,
    domain: str,
    semantic_resolution_tool_model_factory: ToolModelFactory | None = None,
) -> CompatibilityResolutionResult:
    try:
        return _resolve_compatibility_validated(
            task=task,
            candidates=candidates,
            domain=domain,
            semantic_resolution_tool_model_factory=(
                semantic_resolution_tool_model_factory
            ),
        )
    except (AssertionError, TypeError, ValueError):
        return _blocked_compatibility_result(
            task=task,
            candidates=candidates,
            domain=domain,
            reason_code="RESOLUTION_CONTRACT_VALIDATION_FAILED",
        )


def _resolve_facility_compatibility(
    *,
    task: AgentTask,
    candidates: FacilityCandidates,
    semantic_resolution_tool_model_factory: ToolModelFactory | None = None,
) -> CompatibilityResolutionResult:
    return _resolve_compatibility(
        task=task,
        candidates=candidates,
        domain="facility",
        semantic_resolution_tool_model_factory=semantic_resolution_tool_model_factory,
    )


def run_facility_agent(
    *,
    task: AgentTask,
    candidates: FacilityCandidates,
    model_invoker: ModelInvoker | None = None,
) -> AgentResult:
    """Resolve a facility mention to one authoritative canonical entity.

    No model call for a unique authority candidate; abstain on unresolved
    multiples; no model-created facility ids.
    """

    if _compatibility_requested(candidates):
        del model_invoker
        return _resolve_facility_compatibility(
            task=task,
            candidates=candidates,
        ).agent_result

    for tool in ("lookup_nasr_facility", "lookup_artcc", "resolve_facility_alias"):
        _check_tool(task, tool)
    tool_trace = [_trace("lookup_nasr_facility", mention=candidates.mention)]
    # §11.4: the Facility Agent must use the exact advisory evidence span
    # passed to it. Synthetic strings are not evidence; if no exact span is
    # available the Agent abstains.
    advisory_evidence = (candidates.advisory_evidence or "").strip()
    if not advisory_evidence:
        card = EvidenceCard(
            agent_role="facility", status=AgentStatus.ABSTAIN,
            source_ids=[candidates.source_id] if candidates.source_id else [],
            tool_trace=tool_trace,
            decision_basis="no exact advisory evidence span supplied; abstain",
        )
        return AgentResult(status=AgentStatus.ABSTAIN, evidence_card=card)
    if not candidates.candidates:
        card = EvidenceCard(
            agent_role="facility", status=AgentStatus.ABSTAIN,
            source_ids=[candidates.source_id] if candidates.source_id else [],
            tool_trace=tool_trace, decision_basis="zero authority candidates",
        )
        return AgentResult(status=AgentStatus.ABSTAIN, evidence_card=card)
    if len(candidates.candidates) == 1:
        entity = candidates.candidates[0]
        ontology_type = _facility_ontology_type(entity)
        if ontology_type is None:
            card = EvidenceCard(
                agent_role="facility",
                status=AgentStatus.ABSTAIN,
                source_ids=[candidates.source_id] if candidates.source_id else [],
                tool_trace=tool_trace,
                decision_basis="candidate facility type is not mapped by the active profile",
            )
            return AgentResult(status=AgentStatus.ABSTAIN, evidence_card=card)
        claim = EvidenceClaim(
            field_name="controlled_facility", value=entity.entity_id,
            ontology_target=ontology_type,
            evidence_text=advisory_evidence,
            source_id=candidates.source_id or entity.entity_id,
            canonical_ref=entity.entity_id,
        )
        card = EvidenceCard(
            agent_role="facility", status=AgentStatus.RESOLVED,
            claims=[claim], canonical_refs=[entity.entity_id],
            source_ids=[claim.source_id], tool_trace=tool_trace,
            decision_basis="unique authority candidate",
        )
        return AgentResult(status=AgentStatus.RESOLVED, evidence_card=card)
    # Batch A does not ask a provider to resolve ambiguous candidates. Strict
    # compatibility metadata handles deterministic candidate-level filtering;
    # metadata-free legacy calls retain an honest abstention.
    del model_invoker
    if not candidates.structural_slot or not candidates.expected_entity_type:
        card = EvidenceCard(
            agent_role="facility",
            status=AgentStatus.ABSTAIN,
            source_ids=[candidates.source_id] if candidates.source_id else [],
            uncertainties=["ambiguous candidates lack known structural context"],
            tool_trace=tool_trace,
            decision_basis="missing structural slot or expected entity type",
        )
        return AgentResult(status=AgentStatus.ABSTAIN, evidence_card=card)
    card = EvidenceCard(
        agent_role="facility",
        status=AgentStatus.ABSTAIN,
        source_ids=[candidates.source_id] if candidates.source_id else [],
        uncertainties=[f"{len(candidates.candidates)} unresolved candidates"],
        tool_trace=tool_trace,
        decision_basis="multiple candidates require compatibility audit",
    )
    return AgentResult(status=AgentStatus.ABSTAIN, evidence_card=card)


def _facility_ontology_type(entity: Any) -> str | None:
    """Map a NASR entity type to its ontology class (nas:Airport / nas:ARTCC)."""

    etype = getattr(getattr(entity, "entity_type", None), "value", "")
    if etype == "artcc":
        return "nas:ARTCC"
    if etype == "airport":
        return "nas:Airport"
    return None


# ---------------------------------------------------------------------------
# Terminology Agent (design §10)
# ---------------------------------------------------------------------------


@dataclass
class TermCandidates:
    """Authority term candidates for a mention (design §10.4)."""

    mention: str
    candidates: list[Any] = field(default_factory=list)
    source_id: str = ""
    guide: SchemaGuide | None = None
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


def _resolve_terminology_compatibility(
    *,
    task: AgentTask,
    candidates: TermCandidates,
    semantic_resolution_tool_model_factory: ToolModelFactory | None = None,
) -> CompatibilityResolutionResult:
    return _resolve_compatibility(
        task=task,
        candidates=candidates,
        domain="terminology",
        semantic_resolution_tool_model_factory=semantic_resolution_tool_model_factory,
    )


def run_terminology_agent(
    *,
    task: AgentTask,
    candidates: TermCandidates,
    model_invoker: ModelInvoker | None = None,
) -> AgentResult:
    """Normalize a term mention, resolve its canonical term, map to event class."""

    if _compatibility_requested(candidates):
        del model_invoker
        return _resolve_terminology_compatibility(
            task=task,
            candidates=candidates,
        ).agent_result

    for tool in ("lookup_faa_glossary", "lookup_pcg_term", "resolve_term_registry", "resolve_schema_event_class"):
        _check_tool(task, tool)
    tool_trace = [
        _trace("resolve_term_registry", mention=candidates.mention),
        _trace("resolve_schema_event_class"),
    ]
    if not candidates.candidates:
        card = EvidenceCard(
            agent_role="terminology", status=AgentStatus.ABSTAIN,
            source_ids=[candidates.source_id] if candidates.source_id else [],
            tool_trace=tool_trace, decision_basis="zero authority candidates",
        )
        return AgentResult(status=AgentStatus.ABSTAIN, evidence_card=card)

    # Keep every abbreviation match until candidate-level compatibility is
    # audited. In particular, ``GS`` must retain Ground Stop and Glide Slope.
    pool = sorted(candidates.candidates, key=lambda term: term.term_id)

    if len(pool) == 1:
        return _resolve_term(pool[0], candidates, tool_trace, [])
    # Candidate-level type/schema audit is not active until the deterministic
    # compatibility wrappers land. Fail closed rather than asking the legacy
    # provider to choose between meanings such as Ground Stop and Glide Slope.
    del model_invoker
    card = EvidenceCard(
        agent_role="terminology",
        status=AgentStatus.ABSTAIN,
        source_ids=[candidates.source_id] if candidates.source_id else [],
        uncertainties=[f"{len(pool)} unresolved term candidates"],
        tool_trace=tool_trace,
        decision_basis="multiple candidates require candidate-level compatibility audit",
    )
    return AgentResult(status=AgentStatus.ABSTAIN, evidence_card=card)


def _resolve_term(term: Any, candidates: TermCandidates, tool_trace, model_calls) -> AgentResult:
    """Emit a resolved term card + event-class mapping (no new ontology class).

    §11.4: the claim's evidence text is the exact advisory span passed to the
    Agent (the term mention in context). Synthetic strings such as
    ``canonical term ... -> ...`` are not evidence. If no exact span is
    available the resolved mapping is recorded but cannot support a formal
    rdf:type fact (the Formal Graph Kernel's fact-to-claim binding will reject
    it for lack of source-contained evidence).
    """

    abbrev = getattr(term, "abbreviation", "")
    advisory_evidence = (candidates.advisory_evidence or "").strip()
    event_class = candidates.guide.event_class_for_term(abbrev) if candidates.guide else None
    if event_class is None:
        # Canonical term exists but no schema mapping -> profile_gap. The
        # advisory span (when available) is the evidence; otherwise no claim.
        if not advisory_evidence:
            card = EvidenceCard(
                agent_role="terminology", status=AgentStatus.PROFILE_GAP,
                canonical_refs=[term.term_id],
                source_ids=[candidates.source_id] if candidates.source_id else [],
                uncertainties=["canonical term has no ATMONTO event-class mapping",
                               "no exact advisory evidence span supplied"],
                tool_trace=tool_trace, decision_basis="no schema mapping; no exact evidence",
            )
            return AgentResult(status=AgentStatus.PROFILE_GAP, evidence_card=card, model_calls=model_calls)
        claim = EvidenceClaim(
            field_name="operational_term", value=term.term_id,
            evidence_text=advisory_evidence,
            source_id=candidates.source_id or term.term_id, canonical_ref=term.term_id,
        )
        card = EvidenceCard(
            agent_role="terminology", status=AgentStatus.PROFILE_GAP,
            claims=[claim], canonical_refs=[term.term_id], source_ids=[claim.source_id],
            uncertainties=["canonical term has no ATMONTO event-class mapping"],
            tool_trace=tool_trace, decision_basis="no schema mapping for this term",
        )
        return AgentResult(status=AgentStatus.PROFILE_GAP, evidence_card=card, model_calls=model_calls)
    if not advisory_evidence:
        # Resolved mapping but no exact advisory span -> cannot support a formal
        # fact; record the mapping without a source-contained claim.
        card = EvidenceCard(
            agent_role="terminology", status=AgentStatus.RESOLVED,
            canonical_refs=[term.term_id],
            source_ids=[candidates.source_id] if candidates.source_id else [],
            uncertainties=["no exact advisory evidence span supplied"],
            tool_trace=tool_trace,
            decision_basis=f"unique authority mapping -> {event_class}; no exact evidence",
        )
        return AgentResult(status=AgentStatus.RESOLVED, evidence_card=card, model_calls=model_calls)
    claim = EvidenceClaim(
        field_name="operational_term", value=term.term_id, ontology_target=event_class,
        evidence_text=advisory_evidence,
        source_id=candidates.source_id or term.term_id, canonical_ref=term.term_id,
    )
    card = EvidenceCard(
        agent_role="terminology", status=AgentStatus.RESOLVED,
        claims=[claim], canonical_refs=[term.term_id], source_ids=[claim.source_id],
        tool_trace=tool_trace, decision_basis=f"unique authority mapping -> {event_class}",
    )
    return AgentResult(status=AgentStatus.RESOLVED, evidence_card=card, model_calls=model_calls)


# ---------------------------------------------------------------------------
# Knowledge Graph Construction Agent (design §11)
# ---------------------------------------------------------------------------


@dataclass
class KGConstructionInput:
    """Inputs to the KG Construction Agent (design §11.2)."""

    advisory: SourceRecord
    advisory_card: EvidenceCard
    facility_card: EvidenceCard
    terminology_card: EvidenceCard
    event_uri: str
    event_class: str
    guide: SchemaGuide
    allowed_source_ids: set[str] = field(default_factory=set)


def run_kg_construction_agent(
    *,
    task: AgentTask,
    inputs: KGConstructionInput,
    tool_model_factory: ToolModelFactory | None = None,
) -> AgentResult:
    """Generate an ontology-constrained Graph Patch from the evidence cards.

    Uses the program-supplied event URI and resolved canonical ids only. No
    direct RDF/Turtle/Cypher/JSON-Schema output; no new ontology vocabulary.
    If no event class was resolved the Agent abstains and emits no patch.
    """

    for tool in ("get_schema_context", "resolve_canonical_ref", "get_source_evidence"):
        _check_tool(task, tool)
    # Missing resolved event type -> abstain, no formal patch (design §11.6).
    if not inputs.event_class:
        card = EvidenceCard(
            agent_role="knowledge_graph_construction",
            status=AgentStatus.ABSTAIN,
            source_ids=[inputs.advisory.source_id],
            decision_basis="missing resolved event type; no graph constructed",
        )
        return AgentResult(status=AgentStatus.ABSTAIN, evidence_card=card)

    allowed = sorted(inputs.allowed_source_ids)
    if not allowed:
        card = EvidenceCard(
            agent_role="knowledge_graph_construction",
            status=AgentStatus.BLOCKED,
            decision_basis="no accepted event evidence sources are available",
        )
        return AgentResult(
            status=AgentStatus.BLOCKED,
            evidence_card=card,
            failure_reason="no accepted event evidence sources are available",
        )
    known = _known_canonical_entities(
        inputs.facility_card,
        inputs.guide,
        allowed_source_ids=set(allowed),
    )
    if tool_model_factory is None:
        card = EvidenceCard(
            agent_role="knowledge_graph_construction",
            status=AgentStatus.BLOCKED,
            source_ids=[inputs.advisory.source_id],
            decision_basis="no native tool-calling model adapter is available",
        )
        return AgentResult(
            status=AgentStatus.BLOCKED,
            evidence_card=card,
            failure_reason="no native tool-calling model adapter is available",
        )

    from aviation_agentic_ai.agent_system.kg_tool_graph import (
        run_kg_tool_agent,
    )
    from aviation_agentic_ai.agent_system.kg_tools import (
        KGConstructionToolGateway,
        build_kg_construction_tools,
    )

    evidence_cards = {
        "advisory": inputs.advisory_card,
        "facility": inputs.facility_card,
        "terminology": inputs.terminology_card,
    }
    gateway = KGConstructionToolGateway(
        guide=inputs.guide,
        event_class=inputs.event_class,
        evidence_cards=evidence_cards,
        canonical_entities=known,
        allowed_source_ids=set(allowed),
    )
    tools = build_kg_construction_tools(gateway)
    return run_kg_tool_agent(
        model=tool_model_factory(tools),
        tools=tools,
        event_uri=inputs.event_uri,
        event_class=inputs.event_class,
        schema_slice_id=inputs.guide.schema_slice_id,
        allowed_source_ids=set(allowed),
        canonical_entities=known,
        evidence_cards=evidence_cards,
    )


def _known_canonical_entities(
    facility_card: EvidenceCard,
    guide: SchemaGuide,
    *,
    allowed_source_ids: set[str],
) -> dict[str, str]:
    """Map resolved canonical facility ids -> ontology class for the patch."""

    entities: dict[str, str] = {}
    for claim in facility_card.claims:
        if (
            claim.source_id in allowed_source_ids
            and claim.canonical_ref
            and claim.ontology_target
        ):
            entities[claim.canonical_ref] = claim.ontology_target
    return entities


# ---------------------------------------------------------------------------
# Query Agent (design §12)
# ---------------------------------------------------------------------------


@dataclass
class QueryGraphEvidence:
    """Graph-tool results supplied to the Query Agent (design §12.4)."""

    facts: list[dict[str, Any]] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)


@dataclass
class QueryResult:
    """The Query Agent's bounded outcome (plan §13 T3).

    ``status`` distinguishes a successful answer (``ok``), a deterministic
    insufficient-evidence decision (``insufficient``), and a provider failure
    (``blocked``). Only ``blocked`` carries a failure reason; provider failure
    must not be reported as insufficient evidence (plan §6.3, §13).
    """

    status: str  # ok | insufficient | blocked
    answer: str
    source_ids: list[str] = field(default_factory=list)
    model_call: ModelCallRecord | None = None
    failure_reason: str = ""


def run_query_agent(
    *,
    task: AgentTask,
    question: str,
    evidence: QueryGraphEvidence,
    ontology_labels: dict[str, str],
    model_invoker: ModelInvoker,
    insufficient_answer: str = "Insufficient graph evidence.",
) -> QueryResult:
    """Answer a question using only the materialized graph + provenance.

    Plan §6.3 / §13 T3/T4: a non-empty model-call error or an empty provider
    response raises a narrow ``blocked`` result BEFORE answer parsing.
    ``Insufficient graph evidence.`` is reserved for a successful deterministic
    retrieval decision with no relevant graph evidence — never for provider
    failure.
    """

    for tool in ("graph_search", "graph_neighbors", "get_provenance"):
        _check_tool(task, tool)
    if not evidence.facts:
        return QueryResult(
            status="insufficient", answer=insufficient_answer,
            model_call=_no_call_record("query"),
            failure_reason="no matching graph evidence",
        )
    rec = model_invoker(
        "query",
        {
            "user_question": question,
            "ontology_labels": _ontology_labels_text(ontology_labels),
            "graph_evidence": _graph_evidence_text(evidence.facts),
        },
    )
    # §13 T3: provider failure -> BLOCKED before answer parsing.
    if rec.error:
        return QueryResult(
            status="blocked", answer="", model_call=rec, failure_reason=rec.error,
        )
    if not rec.raw_response.strip():
        return QueryResult(
            status="blocked", answer="", model_call=rec,
            failure_reason="empty provider response",
        )
    answer, sources = parse_query_answer(rec.raw_response, evidence.source_ids)
    if not answer:
        return QueryResult(
            status="blocked", answer="", model_call=rec,
            failure_reason="query response contained no answer",
        )
    if not sources:
        return QueryResult(
            status="blocked", answer="", model_call=rec,
            failure_reason="query response cited no retrieved source",
        )
    return QueryResult(status="ok", answer=answer, source_ids=sources, model_call=rec)


def _ontology_labels_text(labels: dict[str, str]) -> str:
    """Render ontology labels as ``prefixed_name=label`` rows (design §12.2)."""

    if not labels:
        return "(none)"
    return "\n".join(f"{name}={label}" for name, label in sorted(labels.items()))


def _graph_evidence_text(facts: list[dict[str, Any]]) -> str:
    """Render graph facts as ``s p o [src1; src2]`` rows (design §12.2)."""

    rows: list[str] = []
    for fact in facts:
        subj = fact.get("subject", "")
        pred = fact.get("predicate", "")
        obj = fact.get("object", "")
        src = fact.get("source_document", "")
        rows.append(f"{subj} {pred} {obj} [{src}]")
    return "\n".join(rows)


def parse_query_answer_claims(raw: str) -> tuple[str, list[str]]:
    """Extract answer text and every source ID claimed by the response.

    Plan §6.3: the internal ``ANSWER`` and ``SOURCES`` headers emitted by the
    frozen query catalog are parsed but NOT displayed. ``ANSWER`` on its own
    line (or as an ``ANSWER:`` prefix) marks the start of the answer text and
    is stripped; ``SOURCES`` / ``sources:`` mark the source list.
    """

    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    sources: list[str] = []
    answer_lines: list[str] = []
    in_sources = False
    in_answer = False

    def add_source_tokens(text: str) -> None:
        for token in re.split(r"[,\s]+", text):
            token = token.strip().lstrip("-").rstrip(".;")
            if token and token.lower() not in {"and", "+"} and token not in sources:
                sources.append(token)

    for ln in lines:
        low = ln.lower()
        # ANSWER header: start of the displayed answer; the header itself is
        # stripped (plan §6.3).
        if low == "answer" or low.startswith("answer:"):
            in_answer = True
            if low.startswith("answer:"):
                tail = ln.split(":", 1)[1].strip()
                if tail:
                    answer_lines.append(tail)
            continue
        if low == "sources" or low.startswith("sources:"):
            in_sources = True
            in_answer = False
            if low.startswith("sources:"):
                add_source_tokens(ln.split(":", 1)[1])
            continue
        if in_sources:
            add_source_tokens(ln)
            continue
        answer_lines.append(ln)
    _ = in_answer  # parsed header presence; the answer text follows regardless
    # A non-empty provider response can still omit the answer body. Keep that
    # distinct from deterministic insufficient evidence so the caller can mark
    # the malformed model result BLOCKED.
    answer = " ".join(answer_lines).strip()
    return answer, sources


def parse_query_answer(raw: str, available: list[str]) -> tuple[str, list[str]]:
    """Extract the answer and retain only citations present in ``available``."""

    answer, claimed = parse_query_answer_claims(raw)
    allowed = set(available)
    return answer, [source for source in claimed if source in allowed]


def _no_call_record(agent: str) -> ModelCallRecord:
    """A zero-attempt record for the fail-closed path (no provider call)."""

    return ModelCallRecord(agent=agent, raw_response="", error="no graph evidence")


def _now_ms() -> float:
    return time.perf_counter()


# Re-export the prompt assembler for callers that build messages directly.
__all__ = [
    "AdvisoryMentions",
    "FacilityCandidates",
    "KGConstructionInput",
    "ModelInvoker",
    "QueryGraphEvidence",
    "ToolNotAllowedError",
    "assemble_prompt",
    "parse_structured_fields",
    "parse_query_answer",
    "parse_query_answer_claims",
    "run_advisory_agent",
    "run_facility_agent",
    "run_kg_construction_agent",
    "run_query_agent",
    "run_terminology_agent",
]
