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

import re

from aviation_agentic_ai.agent_system.contracts import GraphPatchBlock, GraphPatchLine, ProfileGap

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
