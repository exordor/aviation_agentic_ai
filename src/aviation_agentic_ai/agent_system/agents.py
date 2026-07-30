"""Deterministic advisory evidence and bounded active Agent helpers.

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
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    AgentTask,
    EvidenceCard,
    EvidenceClaim,
    SourceRecord,
    ToolTraceEntry,
)
from aviation_agentic_ai.agent_system.prompts import assemble_prompt
from aviation_agentic_ai.agent_system.tmi_profiles import (
    classify_tmi_family,
    get_tmi_profile,
)


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
    constrained_area: str | None = None
    operational_term: str | None = None
    effective_start: str | None = None
    effective_end: str | None = None
    issued_time: str | None = None
    status: str | None = None
    advisory_number: str | None = None
    extension_probability: str | None = None
    impacting_condition: str | None = None
    implementation_status: str | None = None
    re_route_type: str | None = None
    re_route_reason: str | None = None
    re_route_time_type: str | None = None
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
_CONSTRAINED_AREA_RE = re.compile(
    r"CONSTRAINED\s+AREA\s*:\s*([A-Z][A-Z0-9]{2,4})",
    re.IGNORECASE,
)
_ELEMENT_TYPE_RE = re.compile(r"ELEMENT\s*TYPE\s*:\s*([A-Z][A-Z0-9_-]*)", re.IGNORECASE)
_EVENT_SPAN_PATTERNS: dict[str, re.Pattern[str]] = {
    "GDP": re.compile(r"\b(?:GDP|GROUND\s*DELAY\s*PROGRAM)\b", re.IGNORECASE),
    "GS": re.compile(r"\b(?:GS|GROUND\s*STOP)\b", re.IGNORECASE),
    "REROUTE": re.compile(r"\bROUTE\s+(?:FYI|PLN|RMD|RQD)\b", re.IGNORECASE),
}
_PERIOD_RE = re.compile(
    r"(?:GROUND\s*STOP\s*PERIOD|PERIOD|GDP\s*CNX\s*PERIOD)\s*:\s*"
    r"(\d{2}/\d{2,4}\w*\s*-\s*\d{2}/\d{2,4}\w*)",
    re.IGNORECASE,
)
_COMPACT_EFFECTIVE_RE = re.compile(
    r"EFFECTIVE\s+TIME\s*:\s*(\d{6})\s*-\s*(\d{6})",
    re.IGNORECASE,
)
_SIGNATURE_RE = re.compile(
    r"SIGNATURE\s*:\s*(\d{2})/(\d{2})/(\d{2})\s+(\d{2}):(\d{2})",
    re.IGNORECASE,
)
_ADVZY_RE = re.compile(r"ADVZY\s*(\d{3})", re.IGNORECASE)
_CNX_RE = re.compile(r"\bCNX\b", re.IGNORECASE)
_EXT_PROB_RE = re.compile(r"PROBABILITY\s+OF\s+EXTENSION\s*:\s*([A-Z]+)", re.IGNORECASE)
_REROUTE_STATUS_RE = re.compile(r"\bROUTE\s+(FYI|PLN|RMD|RQD)\b", re.IGNORECASE)
_REROUTE_REASON_RE = re.compile(
    r"\bREASON\s*:\s*([A-Z][A-Z0-9_-]*)",
    re.IGNORECASE,
)
_REROUTE_TIME_TYPE_RE = re.compile(
    r"\bVALID\s*:\s*(ETA|ETD|FCA\s+FLIGHT\s+LIST)\b",
    re.IGNORECASE,
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
_HEADER_DATE_RE = re.compile(r"ADVZY\s*\d{3}\s+\S+\s+(\d{2})/(\d{2})/(\d{4})", re.IGNORECASE)
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


def _anchor_compact_effective_value(
    token: str,
    year: int,
    month: int,
    header_day: int,
    *,
    allow_next_day: bool = False,
) -> str | None:
    """Anchor a compact ATCSCC ``DDHHMM`` effective-time token."""

    if not re.fullmatch(r"\d{6}", token):
        return None
    return _anchor_period_value(
        f"{token[:2]}/{token[2:]}",
        year,
        month,
        header_day,
        allow_next_day=allow_next_day,
    )


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
    event_family = classify_tmi_family(advisory_text)
    ctl = _CTL_ELEMENT_RE.search(advisory_text)
    if ctl:
        mentions.controlled_facility = ctl.group(1).upper()
        mentions.evidence_spans["controlled_facility"] = ctl.group(0)
    elif event_family == "REROUTE":
        constrained_area = _CONSTRAINED_AREA_RE.search(advisory_text)
        if constrained_area:
            mentions.controlled_facility = constrained_area.group(1).upper()
            mentions.constrained_area = constrained_area.group(1).upper()
            mentions.evidence_spans["controlled_facility"] = constrained_area.group(0)
            mentions.evidence_spans["constrained_area"] = constrained_area.group(0)
            mentions.element_type_code = "ARTCC"

    event = (
        _EVENT_SPAN_PATTERNS[event_family].search(advisory_text)
        if event_family in _EVENT_SPAN_PATTERNS
        else None
    )
    if event:
        mentions.event_type = event_family
        mentions.operational_term = (
            "RR" if event_family == "REROUTE" else event_family
        )
        mentions.evidence_spans["event_type"] = event.group(0)
        mentions.evidence_spans["operational_term"] = event.group(0)
    element_type = _ELEMENT_TYPE_RE.search(advisory_text)
    if element_type:
        mentions.element_type_code = element_type.group(1).upper()
    if mentions.event_type in {"GDP", "GS", "REROUTE"}:
        if mentions.controlled_facility:
            mentions.facility_structural_slot = FACILITY_SLOT
            if mentions.element_type_code:
                mentions.facility_expected_entity_type = ELEMENT_TYPE_TO_ENTITY_TYPE.get(
                    mentions.element_type_code
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
    elif header_date:
        compact_period = _COMPACT_EFFECTIVE_RE.search(advisory_text)
        if compact_period:
            year = int(header_date.group(3))
            month = int(header_date.group(1))
            header_day = int(header_date.group(2))
            start_token, end_token = compact_period.group(1), compact_period.group(2)
            start_val = _anchor_compact_effective_value(
                start_token,
                year,
                month,
                header_day,
            )
            end_val = _anchor_compact_effective_value(
                end_token,
                year,
                month,
                header_day,
                allow_next_day=True,
            )
            if start_val is not None:
                mentions.effective_start = start_val
                mentions.evidence_spans["effective_start"] = start_token
            if end_val is not None:
                mentions.effective_end = end_val
                mentions.evidence_spans["effective_end"] = end_token
    signature = _SIGNATURE_RE.search(advisory_text)
    if signature:
        try:
            issued = datetime(
                2000 + int(signature.group(1)),
                int(signature.group(2)),
                int(signature.group(3)),
                int(signature.group(4)),
                int(signature.group(5)),
                tzinfo=UTC,
            )
        except ValueError:
            pass
        else:
            mentions.issued_time = issued.strftime("%Y-%m-%dT%H:%M:%SZ")
            mentions.evidence_spans["issued_time"] = signature.group(0)
    advzy = _ADVZY_RE.search(advisory_text)
    if advzy:
        mentions.advisory_number = advzy.group(1)
        mentions.evidence_spans["advisory_number"] = advzy.group(0)
    if _CNX_RE.search(advisory_text):
        mentions.status = "CNX"
        mentions.evidence_spans["status"] = _CNX_RE.search(advisory_text).group(0)
    ext_prob = _EXT_PROB_RE.search(advisory_text)
    if ext_prob:
        extension_value = ext_prob.group(1).upper()
        mentions.extension_probability = (
            "MEDIUM" if extension_value == "MODERATE" else extension_value
        )
        mentions.evidence_spans["extension_probability"] = ext_prob.group(0)
    impacting = _IMPACTING_RE.search(advisory_text)
    if impacting:
        # Normalize to the leading single-word cause (e.g. "WEATHER") while
        # keeping the full exact span as evidence.
        raw = impacting.group(1).strip()
        first_token = re.split(r"\s*/\s*|\s+", raw, maxsplit=1)[0].lower()
        mentions.impacting_condition = first_token
        mentions.evidence_spans["impacting_condition"] = impacting.group(0)
    if mentions.event_type == "REROUTE":
        reroute_status = _REROUTE_STATUS_RE.search(advisory_text)
        if reroute_status:
            mentions.implementation_status = reroute_status.group(1).upper()
            mentions.re_route_type = "ROUTE"
            mentions.evidence_spans["implementation_status"] = reroute_status.group(0)
            mentions.evidence_spans["re_route_type"] = reroute_status.group(0)
        reroute_reason = _REROUTE_REASON_RE.search(advisory_text)
        if reroute_reason:
            mentions.re_route_reason = reroute_reason.group(1).upper()
            mentions.evidence_spans["re_route_reason"] = reroute_reason.group(0)
        reroute_time_type = _REROUTE_TIME_TYPE_RE.search(advisory_text)
        if reroute_time_type:
            mentions.re_route_time_type = " ".join(
                reroute_time_type.group(1).upper().split()
            )
            mentions.evidence_spans["re_route_time_type"] = (
                reroute_time_type.group(0)
            )
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
# Deterministic advisory evidence builder
# ---------------------------------------------------------------------------


def build_advisory_evidence(
    *,
    task: AgentTask,
    advisory: SourceRecord,
    event_classes: list[str],
    mentions: AdvisoryMentions,
) -> EvidenceCard:
    """Convert a raw advisory into a source-bounded evidence card.

    Makes no facility/term canonicalization. Uses the deterministic parse.

    This is a zero-call parser/service, not an Agent role. It makes no
    facility or terminology canonicalization decision.
    """

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
        ("constrained_area", mentions.constrained_area),
        ("operational_term", mentions.operational_term),
        ("effective_start", mentions.effective_start),
        ("effective_end", mentions.effective_end),
        ("issued_time", mentions.issued_time),
        ("status", mentions.status),
        ("advisory_number", mentions.advisory_number),
        ("extension_probability", mentions.extension_probability),
        ("impacting_condition", mentions.impacting_condition),
        ("implementation_status", mentions.implementation_status),
        ("re_route_type", mentions.re_route_type),
        ("re_route_reason", mentions.re_route_reason),
        ("re_route_time_type", mentions.re_route_time_type),
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
        profile = get_tmi_profile(mentions.event_type or "", publishable_only=True)
        ontology_target = (
            profile.prefixed_ontology_class
            if profile is not None
            and field_name in {"event_type", "operational_term"}
            else None
        )
        claims.append(
            EvidenceClaim(
                field_name=field_name,
                value=value,
                evidence_text=span,
                source_id=source_id,
                ontology_target=ontology_target,
            )
        )

    status = AgentStatus.RESOLVED if claims else AgentStatus.ABSTAIN
    return EvidenceCard(
        agent_role="advisory",
        status=status,
        claims=claims,
        source_ids=[source_id],
        tool_trace=tool_trace,
        decision_basis="deterministic structured-field parse of the advisory",
    )

# Re-export the prompt assembler for callers that build messages directly.
__all__ = [
    "AdvisoryMentions",
    "ToolNotAllowedError",
    "assemble_prompt",
    "parse_structured_fields",
    "build_advisory_evidence",
]
