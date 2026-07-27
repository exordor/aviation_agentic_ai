"""Tolerant Graph Patch + PROFILE_GAPS parser (design §11.5).

The KG Construction Agent emits two sections:

    GRAPH_PATCH
    subject | predicate | object | source_ids

    PROFILE_GAPS
    field | value | evidence | reason

The parser is deliberately tolerant: it ignores blank lines, Markdown code
fences (```), and ``#`` comment lines. It locates the ``GRAPH_PATCH`` and
``PROFILE_GAPS`` section headers and parses the pipe-table rows beneath each.
It does NOT accept JSON, JSON Schema, RDF, Turtle, or Cypher. Malformed rows
are skipped (not fatal); the caller reports the parse rate.
"""

from __future__ import annotations

import json
import re

from aviation_agentic_ai.agent_system.contracts import GraphPatchBlock, GraphPatchLine, ProfileGap
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    CaseFactProposal,
    CaseProfileGapProposal,
    ParsedCaseAssemblySections,
)

_FENCE_RE = re.compile(r"^\s*```")
_GRAPH_PATCH_HEADER = "GRAPH_PATCH"
_PROFILE_GAPS_HEADER = "PROFILE_GAPS"


def _is_ignored(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if stripped.startswith("#"):
        return True
    if _FENCE_RE.match(line):
        return True
    return False


def _parse_patch_line(line: str) -> GraphPatchLine | None:
    columns = line.split("|")
    if len(columns) != 4:
        return None
    subject = columns[0].strip()
    predicate = columns[1].strip()
    obj = _normalize_object_literal(columns[2].strip())
    source_ids_raw = columns[3].strip()
    if not subject or not predicate or not obj or not source_ids_raw:
        return None
    source_ids = [s.strip() for s in source_ids_raw.split(",") if s.strip()]
    if not source_ids:
        return None
    return GraphPatchLine(
        subject=subject,
        predicate=predicate,
        object=obj,
        source_ids=source_ids,
    )


_TYPED_LITERAL_RE = re.compile(r'^"(.*)"\^\^[a-zA-Z][a-zA-Z0-9:-]*$', re.DOTALL)
_QUOTED_LITERAL_RE = re.compile(r'^"(.*)"$', re.DOTALL)


def _normalize_object_literal(value: str) -> str:
    """Normalize a Graph Patch object literal to its bare value.

    The Graph Patch contract emits bare literals (see the frozen catalog's
    few-shot examples). When a model occasionally wraps a literal in RDF
    Turtle typed-literal syntax (``"value"^^xsd:type``) or in straight quotes,
    this tolerant normalization (design §11.5) strips the casing to recover
    the bare literal the schema validator expects. IRIs and class refs are
    returned unchanged.
    """

    if not value:
        return value
    typed = _TYPED_LITERAL_RE.match(value)
    if typed:
        return typed.group(1)
    quoted = _QUOTED_LITERAL_RE.match(value)
    if quoted:
        return quoted.group(1)
    return value


def _parse_gap_line(line: str) -> ProfileGap | None:
    stripped = line.strip()
    # The catalog authoritatively encodes "no gaps" as a literal NONE row.
    if stripped.upper() == "NONE":
        return None
    columns = line.split("|")
    if len(columns) != 4:
        return None
    field_ = columns[0].strip()
    value = columns[1].strip()
    evidence = columns[2].strip()
    reason = columns[3].strip()
    if not field_ or not value or not evidence or not reason:
        return None
    # A repeated header row (field | value | evidence | reason) is not a gap.
    header_tokens = {"field", "value", "evidence", "reason"}
    if {field_.lower(), value.lower(), evidence.lower(), reason.lower()} == header_tokens:
        return None
    return ProfileGap(field=field_, value=value, evidence=evidence, reason=reason)


def parse_graph_patch(raw: str) -> list[GraphPatchLine]:
    """Parse only the GRAPH_PATCH section into patch lines."""

    return parse_graph_patch_block(raw).patch_lines


def parse_graph_patch_block(raw: str) -> GraphPatchBlock:
    """Parse a KG Construction Agent output into a :class:`GraphPatchBlock`."""

    section: str | None = None
    patch_lines: list[GraphPatchLine] = []
    profile_gaps: list[ProfileGap] = []
    for raw_line in raw.splitlines():
        if _is_ignored(raw_line):
            continue
        stripped = raw_line.strip()
        if stripped == _GRAPH_PATCH_HEADER:
            section = _GRAPH_PATCH_HEADER
            continue
        if stripped == _PROFILE_GAPS_HEADER:
            section = _PROFILE_GAPS_HEADER
            continue
        if section == _GRAPH_PATCH_HEADER:
            parsed = _parse_patch_line(raw_line)
            if parsed is not None:
                patch_lines.append(parsed)
        elif section == _PROFILE_GAPS_HEADER:
            parsed = _parse_gap_line(raw_line)
            if parsed is not None:
                profile_gaps.append(parsed)
        # Lines outside any section header are ignored.
    return GraphPatchBlock(
        patch_lines=patch_lines,
        profile_gaps=profile_gaps,
        raw=raw,
    )


def parse_case_assembly_output(
    raw: str,
    *,
    allowed_validation_profile_ids: frozenset[str],
) -> ParsedCaseAssemblySections:
    """Parse strict JSON-object rows under GRAPH_PATCH and PROFILE_GAPS.

    This parser is additive.  The active compatibility runtime continues to use
    :func:`parse_graph_patch` and its tolerant pipe-delimited behavior.
    """

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
    proposed_facts: list[CaseFactProposal] = []
    profile_gaps: list[CaseProfileGapProposal] = []
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
                item = CaseFactProposal.model_validate_json(stripped)
                proposed_facts.append(item)
            else:
                item = CaseProfileGapProposal.model_validate_json(stripped)
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
    return ParsedCaseAssemblySections(
        proposed_facts=tuple(proposed_facts),
        profile_gaps=tuple(profile_gaps),
    )


def parse_rate(raw: str, parsed: list[GraphPatchLine]) -> float:
    """Fraction of GRAPH_PATCH rows that parsed into patch lines."""

    block = parse_graph_patch_block(raw)
    considered = [
        ln
        for ln in raw.splitlines()
        if not _is_ignored(ln)
        and ln.strip() not in (_GRAPH_PATCH_HEADER, _PROFILE_GAPS_HEADER)
    ]
    in_patch_section = block.patch_lines or block.profile_gaps
    if not in_patch_section:
        # No section headers: fall back to whole-block parse rate.
        if not considered:
            return 0.0
        return len(parsed) / len(considered)
    patch_rows = [
        ln
        for ln in considered
        if ln  # placeholder; the block already parsed only valid ones
    ]
    _ = patch_rows
    # Count rows under the GRAPH_PATCH header (lines between GRAPH_PATCH and
    # PROFILE_GAPS / EOF).
    section: str | None = None
    patch_section_rows = 0
    for raw_line in raw.splitlines():
        if _is_ignored(raw_line):
            continue
        stripped = raw_line.strip()
        if stripped == _GRAPH_PATCH_HEADER:
            section = _GRAPH_PATCH_HEADER
            continue
        if stripped == _PROFILE_GAPS_HEADER:
            section = _PROFILE_GAPS_HEADER
            continue
        if section == _GRAPH_PATCH_HEADER:
            patch_section_rows += 1
    if patch_section_rows == 0:
        return 0.0
    return len(parsed) / patch_section_rows


# ---------------------------------------------------------------------------
# Fail-closed classification (plan §5.3)
# ---------------------------------------------------------------------------

# Outcome labels for the KG Construction Agent's model response. The workflow
# maps these to AgentStatus: BLOCKED for provider/parse failures, ABSTAIN for a
# correctly parsed response with no formal facts, RESOLVED only for a
# parse-complete patch that may reach the Formal Graph Kernel.
PATCH_EMPTY = "empty"
PATCH_MISSING_SECTION = "missing_section"
PATCH_MALFORMED_ROW = "malformed_row"
PATCH_PARSED_EMPTY = "parsed_empty"
PATCH_OK = "ok"


def classify_graph_patch_response(raw: str, block: GraphPatchBlock) -> tuple[str, str | None]:
    """Classify a KG Construction Agent response for fail-closed handling.

    Returns ``(outcome, reason)``:

    - ``empty``: blank/whitespace-only response -> BLOCKED.
    - ``missing_section``: no GRAPH_PATCH header present -> BLOCKED.
    - ``malformed_row``: a row under GRAPH_PATCH did not parse into 4 columns
      (the model emitted a structurally invalid patch) -> BLOCKED.
    - ``parsed_empty``: GRAPH_PATCH section present and well-formed but produced
      zero patch lines (a legitimately empty patch) -> ABSTAIN.
    - ``ok``: at least one patch line parsed; the patch may reach the Formal
      Graph Kernel.
    """

    if not raw or not raw.strip():
        return PATCH_EMPTY, "empty model response"
    if _GRAPH_PATCH_HEADER not in raw:
        return PATCH_MISSING_SECTION, "GRAPH_PATCH section missing"
    malformed = _count_malformed_patch_rows(raw)
    if malformed:
        return PATCH_MALFORMED_ROW, f"{malformed} malformed GRAPH_PATCH row(s)"
    if not block.patch_lines:
        return PATCH_PARSED_EMPTY, "GRAPH_PATCH parsed with zero patch lines"
    return PATCH_OK, None


def _count_malformed_patch_rows(raw: str) -> int:
    """Count rows under GRAPH_PATCH that were considered but did not parse."""

    section: str | None = None
    malformed = 0
    for line in raw.splitlines():
        if _is_ignored(line):
            continue
        stripped = line.strip()
        if stripped == _GRAPH_PATCH_HEADER:
            section = _GRAPH_PATCH_HEADER
            continue
        if stripped == _PROFILE_GAPS_HEADER:
            section = _PROFILE_GAPS_HEADER
            continue
        if section == _GRAPH_PATCH_HEADER:
            if _parse_patch_line(line) is None:
                malformed += 1
    return malformed
