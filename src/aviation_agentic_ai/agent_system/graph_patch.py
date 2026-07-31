"""Strict Event Evidence Integration output parser."""

from __future__ import annotations

import json

from aviation_agentic_ai.agent_system.construction_contracts import (
    EventEvidenceFactProposal,
    EventEvidenceProfileGapProposal,
    ParsedEventEvidenceIntegrationSections,
)

_GRAPH_PATCH_HEADER = "GRAPH_PATCH"
_PROFILE_GAPS_HEADER = "PROFILE_GAPS"


def parse_event_evidence_integration_output(
    raw: str,
    *,
    allowed_validation_profile_ids: frozenset[str],
) -> ParsedEventEvidenceIntegrationSections:
    """Parse strict JSON-object rows under GRAPH_PATCH and PROFILE_GAPS."""

    if not isinstance(allowed_validation_profile_ids, frozenset) or not (
        allowed_validation_profile_ids
    ):
        raise ValueError("allowed_validation_profile_ids must be a nonempty frozenset")
    if any(
        not isinstance(profile_id, str) or not profile_id
        for profile_id in allowed_validation_profile_ids
    ):
        raise ValueError("allowed_validation_profile_ids must contain nonempty strings")

    section: str | None = None
    seen_headers: list[str] = []
    saw_none: dict[str, bool] = {
        _GRAPH_PATCH_HEADER: False,
        _PROFILE_GAPS_HEADER: False,
    }
    proposed_facts: list[EventEvidenceFactProposal] = []
    profile_gaps: list[EventEvidenceProfileGapProposal] = []
    proposal_item_ids: set[str] = set()

    for line_number, raw_line in enumerate(raw.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped in {_GRAPH_PATCH_HEADER, _PROFILE_GAPS_HEADER}:
            if stripped in seen_headers:
                raise ValueError(f"duplicate {stripped} header on line {line_number}")
            if stripped == _PROFILE_GAPS_HEADER and seen_headers != [
                _GRAPH_PATCH_HEADER
            ]:
                raise ValueError("PROFILE_GAPS must follow GRAPH_PATCH")
            if stripped == _GRAPH_PATCH_HEADER and seen_headers:
                raise ValueError("GRAPH_PATCH must be the first section")
            seen_headers.append(stripped)
            section = stripped
            continue
        if section is None:
            raise ValueError(f"content outside a section on line {line_number}")
        if stripped == "NONE":
            rows = proposed_facts if section == _GRAPH_PATCH_HEADER else profile_gaps
            if rows or saw_none[section]:
                raise ValueError(f"NONE must be the only row in {section}")
            saw_none[section] = True
            continue
        if saw_none[section]:
            raise ValueError(f"NONE must be the only row in {section}")
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON object on line {line_number}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"row on line {line_number} must be a JSON object")
        try:
            if section == _GRAPH_PATCH_HEADER:
                item = EventEvidenceFactProposal.model_validate_json(stripped)
                proposed_facts.append(item)
            else:
                item = EventEvidenceProfileGapProposal.model_validate_json(stripped)
                profile_gaps.append(item)
        except ValueError as exc:
            raise ValueError(f"invalid {section} row on line {line_number}") from exc
        if item.validation_profile_id not in allowed_validation_profile_ids:
            raise ValueError(
                f"validation profile is not allowed on line {line_number}"
            )
        if item.proposal_item_id in proposal_item_ids:
            raise ValueError(f"duplicate proposal item ID on line {line_number}")
        proposal_item_ids.add(item.proposal_item_id)

    if seen_headers != [_GRAPH_PATCH_HEADER, _PROFILE_GAPS_HEADER]:
        raise ValueError("GRAPH_PATCH and PROFILE_GAPS sections are both required")
    if not proposed_facts and not saw_none[_GRAPH_PATCH_HEADER]:
        raise ValueError("empty GRAPH_PATCH section must contain NONE")
    if not profile_gaps and not saw_none[_PROFILE_GAPS_HEADER]:
        raise ValueError("empty PROFILE_GAPS section must contain NONE")
    return ParsedEventEvidenceIntegrationSections(
        proposed_facts=tuple(proposed_facts),
        profile_gaps=tuple(profile_gaps),
    )
