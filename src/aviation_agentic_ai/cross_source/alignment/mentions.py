from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Iterable

from aviation_agentic_ai.cross_source.contracts import (
    CanonicalEntity,
    Mention,
    MentionType,
    TermConcept,
)
from aviation_agentic_ai.cross_source.identifiers import normalize_code, stable_id


MENTION_DETECTOR_VERSION = "cross_source_mentions_v1"


def _record_text(record: dict[str, Any]) -> str:
    return str(record.get("text") or record.get("source_text") or "")


def _record_time(record: dict[str, Any]) -> datetime | None:
    alignment = dict(record.get("temporal_alignment") or {})
    value = alignment.get("source_period_start") or record.get("advisory_date")
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _evidence_window(text: str, start: int, end: int) -> str:
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end == -1:
        line_end = len(text)
    line = " ".join(text[line_start:line_end].split())
    if line:
        return line
    return " ".join(text[max(0, start - 80) : min(len(text), end + 80)].split())


def _tokens_for_facilities(entities: Iterable[CanonicalEntity]) -> set[str]:
    return {
        normalize_code(code.value)
        for entity in entities
        for code in entity.codes
        if normalize_code(code.value)
    }


def _tokens_for_terms(terms: Iterable[TermConcept]) -> set[str]:
    return {normalize_code(term.abbreviation) for term in terms if normalize_code(term.abbreviation)}


def _matches(text: str, tokens: set[str]) -> Iterable[re.Match[str]]:
    if not tokens:
        return ()
    alternatives = "|".join(re.escape(token) for token in sorted(tokens, key=lambda x: (-len(x), x)))
    return re.finditer(rf"(?<![A-Z0-9])(?:{alternatives})(?![A-Z0-9])", text.upper())


def extract_mentions(
    record: dict[str, Any],
    *,
    facilities: Iterable[CanonicalEntity],
    terms: Iterable[TermConcept],
) -> list[Mention]:
    text = _record_text(record)
    source_id = str(record.get("source_id") or record.get("sample_id") or "")
    if not source_id or not text:
        return []
    source_family = str(record.get("source_family") or "atcscc_advisories")
    record_time = _record_time(record)
    facility_tokens = _tokens_for_facilities(facilities)
    term_tokens = _tokens_for_terms(terms)
    mentions: list[Mention] = []

    for mention_type, tokens in (
        (MentionType.FACILITY_CODE, facility_tokens),
        (MentionType.OPERATIONAL_TERM, term_tokens),
    ):
        for match in _matches(text, tokens):
            surface = text[match.start() : match.end()]
            normalized = normalize_code(surface)
            mentions.append(
                Mention(
                    mention_id=stable_id(
                        "mention", source_id, mention_type.value, match.start(), normalized
                    ),
                    source_id=source_id,
                    source_family=source_family,
                    surface_form=surface,
                    normalized_form=normalized,
                    mention_type=mention_type,
                    evidence_text=_evidence_window(text, match.start(), match.end()),
                    span_start=match.start(),
                    span_end=match.end(),
                    record_time=record_time,
                    detected_by=MENTION_DETECTOR_VERSION,
                )
            )
    return sorted(mentions, key=lambda item: (item.span_start, item.mention_type.value))
