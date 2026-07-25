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

import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from aviation_agentic_ai.agent_system.contracts import (
    AgentResult,
    AgentStatus,
    AgentTask,
    EvidenceCard,
    EvidenceClaim,
    ModelCallRecord,
    SourceRecord,
    ToolTraceEntry,
)
from aviation_agentic_ai.agent_system.graph_patch import parse_graph_patch_block
from aviation_agentic_ai.agent_system.prompts import assemble_prompt
from aviation_agentic_ai.agent_system.schema_guide import SchemaGuide

# A model invoker takes (agent_role, template_variables) and returns a
# ModelCallRecord. The invoker is responsible for assembling the frozen
# 6-message prompt from the catalog (design §16) and recording the call
# ledger (agent, prompt_set_id, prompt_version, attempt).
ModelInvoker = Callable[[str, dict[str, Any]], ModelCallRecord]


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
    evidence_spans: dict[str, str] = field(default_factory=dict)


_CTL_ELEMENT_RE = re.compile(r"CTL\s*ELEMENT\s*:\s*([A-Z]{2,5})", re.IGNORECASE)
_ELEMENT_TYPE_RE = re.compile(r"ELEMENT\s*TYPE\s*:\s*([A-Z]{2,5})", re.IGNORECASE)
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
    r"IMPACTING\s+CONDITION\s*:\s*([A-Z][A-Z\s/]*)", re.IGNORECASE
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


def _anchor_period_value(token: str, year: int, month: int, header_day: int) -> str | None:
    """Anchor a ``DD/HHMMZ`` period token to a full UTC timestamp (plan §12).

    Returns ``YYYY-MM-DDTHH:MM:SSZ`` when the token's day agrees with the
    header day (deterministic confirmation), otherwise ``None``. The raw source
    substring is preserved separately as ``evidence_text``; this function only
    produces the canonical claim value. It never guesses a calendar context.
    """

    m = _PERIOD_TOKEN_RE.match(token.strip())
    if not m:
        return None
    day, hh, mm = int(m.group(1)), m.group(2), m.group(3)
    if day != header_day:
        # The period day disagrees with the header date -> not uniquely
        # anchorable; abstain on this time fact rather than guess.
        return None
    return f"{year:04d}-{month:02d}-{day:02d}T{hh}:{mm}:00Z"


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
            end_val = _anchor_period_value(end_token, year, month, header_day)
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
        first_token = re.split(r"\s*/\s*|\s+", raw, maxsplit=1)[0].upper()
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
    advisory_evidence: str = ""


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
    # Multiple candidates: model may disambiguate among authority candidates
    # only; never invents a facility id.
    model_calls: list[ModelCallRecord] = []
    chosen = None
    if model_invoker is not None:
        cand_rows = [_facility_candidate_row(e) for e in candidates.candidates]
        rec = model_invoker(
            "facility",
            {
                "source_id": candidates.source_id,
                "facility_mention": candidates.mention,
                "structural_slot": candidates.structural_slot or "UNCLASSIFIED TEXT",
                "advisory_evidence": advisory_evidence,
                "authority_candidates": "\n".join(cand_rows),
            },
        )
        model_calls.append(rec)
        chosen = _pick_candidate_from_response(rec.raw_response, candidates.candidates)
    if chosen is None:
        card = EvidenceCard(
            agent_role="facility", status=AgentStatus.ABSTAIN,
            source_ids=[candidates.source_id] if candidates.source_id else [],
            uncertainties=[f"{len(candidates.candidates)} unresolved candidates"],
            tool_trace=tool_trace, decision_basis="unresolved multiple candidates",
        )
        return AgentResult(status=AgentStatus.ABSTAIN, evidence_card=card, model_calls=model_calls)
    ontology_type = _facility_ontology_type(chosen)
    claim = EvidenceClaim(
        field_name="controlled_facility", value=chosen.entity_id,
        ontology_target=ontology_type,
        evidence_text=advisory_evidence,
        source_id=candidates.source_id or chosen.entity_id,
        canonical_ref=chosen.entity_id,
    )
    card = EvidenceCard(
        agent_role="facility", status=AgentStatus.RESOLVED,
        claims=[claim], canonical_refs=[chosen.entity_id],
        source_ids=[claim.source_id], tool_trace=tool_trace,
        decision_basis="disambiguated among authority candidates",
    )
    return AgentResult(status=AgentStatus.RESOLVED, evidence_card=card, model_calls=model_calls)


def _facility_ontology_type(entity: Any) -> str:
    """Map a NASR entity type to its ontology class (nas:Airport / nas:ARTCC)."""

    etype = getattr(getattr(entity, "entity_type", None), "value", "")
    if etype == "artcc":
        return "nas:ARTCC"
    if etype == "airport":
        return "nas:Airport"
    return "nas:NASfacility"


def _facility_candidate_row(entity: Any) -> str:
    """Render one authority facility candidate row for the Facility prompt."""

    return (
        f"{entity.entity_id} | {getattr(entity, 'preferred_label', '')} | "
        f"{_facility_ontology_type(entity)} | airport facility record | "
        f"{getattr(entity, 'entity_id', '')}"
    )


def _pick_candidate_from_response(raw: str, candidates: list[Any]) -> Any | None:
    """Pick an authority candidate whose id appears in the model response."""

    by_id = {e.entity_id: e for e in candidates}
    for eid in by_id:
        if eid in raw:
            return by_id[eid]
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
    advisory_evidence: str = ""


def run_terminology_agent(
    *,
    task: AgentTask,
    candidates: TermCandidates,
    model_invoker: ModelInvoker | None = None,
) -> AgentResult:
    """Normalize a term mention, resolve its canonical term, map to event class."""

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

    # Filter to TMI-category candidates for event mapping.
    tmi_candidates = [
        t for t in candidates.candidates
        if getattr(getattr(t, "term_category", None), "value", "") == "traffic_management_initiative"
    ]
    pool = tmi_candidates or candidates.candidates

    if len(pool) == 1:
        return _resolve_term(pool[0], candidates, tool_trace, [])
    # Multiple: model may disambiguate among authority candidates only.
    model_calls: list[ModelCallRecord] = []
    chosen = None
    if model_invoker is not None:
        cand_rows = [_term_candidate_row(t, candidates.guide) for t in pool]
        rec = model_invoker(
            "terminology",
            {
                "source_id": candidates.source_id,
                "term_mention": candidates.mention,
                "advisory_evidence": candidates.advisory_evidence or candidates.mention,
                "authority_candidates": "\n".join(cand_rows),
            },
        )
        model_calls.append(rec)
        chosen = _pick_term_from_response(rec.raw_response, pool)
    if chosen is None:
        card = EvidenceCard(
            agent_role="terminology", status=AgentStatus.ABSTAIN,
            source_ids=[candidates.source_id] if candidates.source_id else [],
            uncertainties=[f"{len(pool)} unresolved term candidates"],
            tool_trace=tool_trace, decision_basis="unresolved multiple candidates",
        )
        return AgentResult(status=AgentStatus.ABSTAIN, evidence_card=card, model_calls=model_calls)
    return _resolve_term(chosen, candidates, tool_trace, model_calls)


def _term_candidate_row(term: Any, guide: SchemaGuide | None) -> str:
    """Render one authority term candidate row for the Terminology prompt."""

    abbrev = getattr(term, "abbreviation", "")
    ontology_class = "NONE"
    if guide is not None:
        event_class = guide.event_class_for_term(abbrev)
        if event_class:
            ontology_class = event_class
    return (
        f"{term.term_id} | {getattr(term, 'preferred_label', '')} | {ontology_class} | "
        f"an authority term definition | {term.term_id}"
    )


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


def _pick_term_from_response(raw: str, pool: list[Any]) -> Any | None:
    by_id = {t.term_id: t for t in pool}
    for tid in by_id:
        if tid in raw:
            return by_id[tid]
    return None


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
    model_invoker: ModelInvoker,
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
            agent_role="terminology", status=AgentStatus.ABSTAIN,
            source_ids=[inputs.advisory.source_id],
            decision_basis="missing resolved event type; no graph constructed",
        )
        return AgentResult(status=AgentStatus.ABSTAIN, evidence_card=card)

    compact = inputs.guide.compact_context_for_event(inputs.event_class)
    allowed = sorted(inputs.allowed_source_ids or {inputs.advisory.source_id})
    known = _known_canonical_entities(inputs.facility_card, inputs.guide)
    rec = model_invoker(
        "knowledge_graph_construction",
        {
            "event_uri": inputs.event_uri,
            "allowed_source_ids": "; ".join(allowed),
            "known_canonical_entities": _known_canonical_entities_text(known),
            "schema_context": compact,
            "advisory_evidence_card": _card_summary(inputs.advisory_card),
            "facility_evidence_card": _card_summary(inputs.facility_card),
            "terminology_evidence_card": _card_summary(inputs.terminology_card),
        },
    )
    block = parse_graph_patch_block(rec.raw_response)

    # Fail-closed model-output gate (plan §5.3). The raw response and any
    # provider error remain in the run trace; no KG artifacts are produced for
    # a BLOCKED or ABSTAINED patch.
    if rec.error:
        card = EvidenceCard(
            agent_role="terminology", status=AgentStatus.BLOCKED,
            source_ids=[inputs.advisory.source_id],
            decision_basis=f"provider error: {rec.error}",
        )
        return AgentResult(
            status=AgentStatus.BLOCKED, evidence_card=card,
            model_calls=[rec], failure_reason=f"provider error: {rec.error}",
        )
    from aviation_agentic_ai.agent_system.graph_patch import (
        PATCH_OK,
        PATCH_PARSED_EMPTY,
        classify_graph_patch_response,
    )
    outcome, reason = classify_graph_patch_response(rec.raw_response, block)
    if outcome == PATCH_PARSED_EMPTY:
        card = EvidenceCard(
            agent_role="terminology", status=AgentStatus.ABSTAIN,
            source_ids=[inputs.advisory.source_id],
            decision_basis="GRAPH_PATCH parsed with zero formal facts",
        )
        return AgentResult(
            status=AgentStatus.ABSTAIN, evidence_card=card, model_calls=[rec],
            failure_reason=reason or "",
        )
    if outcome != PATCH_OK:
        card = EvidenceCard(
            agent_role="terminology", status=AgentStatus.BLOCKED,
            source_ids=[inputs.advisory.source_id],
            decision_basis=f"fail-closed: {reason}",
        )
        return AgentResult(
            status=AgentStatus.BLOCKED, evidence_card=card, model_calls=[rec],
            failure_reason=reason or "",
        )
    card = EvidenceCard(
        agent_role="terminology", status=AgentStatus.RESOLVED,
        source_ids=[inputs.advisory.source_id],
        decision_basis=f"generated {len(block.patch_lines)} patch lines",
    )
    return AgentResult(
        status=AgentStatus.RESOLVED,
        artifact_ref="graph_patch",
        evidence_card=card,
        model_calls=[rec],
        graph_patch=block,
    )


def _known_canonical_entities(facility_card: EvidenceCard, guide: SchemaGuide) -> dict[str, str]:
    """Map resolved canonical facility ids -> ontology class for the patch."""

    entities: dict[str, str] = {}
    for claim in facility_card.claims:
        if claim.canonical_ref and claim.ontology_target:
            entities[claim.canonical_ref] = claim.ontology_target
    return entities


def _known_canonical_entities_text(entities: dict[str, str]) -> str:
    if not entities:
        return "NONE"
    return "\n".join(f"{eid} -> {cls}" for eid, cls in sorted(entities.items()))


def _card_summary(card: EvidenceCard) -> str:
    """Render one evidence card as a compact delimited block for the KG prompt."""

    parts = [f"status={card.status.value}"]
    for claim in card.claims:
        bits = [f"{claim.field_name}={claim.value}"]
        if claim.ontology_target:
            bits.append(f"ontology={claim.ontology_target}")
        if claim.canonical_ref:
            bits.append(f"canonical_ref={claim.canonical_ref}")
        bits.append(f"source={claim.source_id}")
        bits.append(f"evidence='{claim.evidence_text}'")
        parts.append(" ".join(bits))
    if card.canonical_refs:
        parts.append("canonical_refs=" + ",".join(card.canonical_refs))
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Query Agent (design §12)
# ---------------------------------------------------------------------------


@dataclass
class QueryGraphEvidence:
    """Graph-tool results supplied to the Query Agent (design §12.4)."""

    facts: list[dict[str, Any]] = field(default_factory=list)
    source_ids: list[str] = field(default_factory=list)


def run_query_agent(
    *,
    task: AgentTask,
    question: str,
    evidence: QueryGraphEvidence,
    ontology_labels: dict[str, str],
    model_invoker: ModelInvoker,
) -> tuple[str, list[str], ModelCallRecord]:
    """Answer a question using only the materialized graph + provenance.

    Returns (answer_text, source_ids, model_call). If no graph evidence, the
    answer is exactly ``图中证据不足`` and no model call is made.
    """

    for tool in ("graph_search", "graph_neighbors", "get_provenance"):
        _check_tool(task, tool)
    if not evidence.facts:
        return ("图中证据不足", [], _no_call_record("query"))
    rec = model_invoker(
        "query",
        {
            "user_question": question,
            "ontology_labels": _ontology_labels_text(ontology_labels),
            "graph_evidence": _graph_evidence_text(evidence.facts),
        },
    )
    answer, sources = _parse_query_answer(rec.raw_response, evidence.source_ids)
    return answer, sources, rec


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


def _parse_query_answer(raw: str, available: list[str]) -> tuple[str, list[str]]:
    """Extract the answer text and the cited source ids (must be known)."""

    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    sources: list[str] = []
    answer_lines: list[str] = []
    avail = set(available)
    in_sources = False
    for ln in lines:
        low = ln.lower()
        if low == "sources" or low.startswith("sources:"):
            in_sources = True
            if low.startswith("sources:"):
                tail = ln.split(":", 1)[1]
                for tok in re.split(r"[,\s]+", tail):
                    tok = tok.strip()
                    if tok and tok in avail:
                        sources.append(tok)
            continue
        if in_sources:
            for tok in re.split(r"[,\s]+", ln):
                tok = tok.strip().lstrip("-")
                if tok and tok in avail and tok not in sources:
                    sources.append(tok)
            continue
        answer_lines.append(ln)
    answer = " ".join(answer_lines).strip() or "图中证据不足"
    return answer, sources


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
    "run_advisory_agent",
    "run_facility_agent",
    "run_kg_construction_agent",
    "run_query_agent",
    "run_terminology_agent",
]
