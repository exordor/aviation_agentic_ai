from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable

from aviation_agentic_ai.cross_source.identifiers import normalize_code


@dataclass(frozen=True)
class CohortSelection:
    records: list[dict[str, Any]]
    matched_codes_by_source: dict[str, list[str]]

    @property
    def source_ids(self) -> list[str]:
        return [str(record["source_id"]) for record in self.records]


def _code_pattern(code: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![A-Z0-9]){re.escape(code)}(?![A-Z0-9])", re.IGNORECASE)


def select_cross_source_cohort(
    records: Iterable[dict[str, Any]],
    *,
    airport_codes: Iterable[object],
    expected_count: int | None = None,
) -> CohortSelection:
    codes = sorted({normalize_code(code) for code in airport_codes if normalize_code(code)})
    patterns = {code: _code_pattern(code) for code in codes}
    selected: list[dict[str, Any]] = []
    matched: dict[str, list[str]] = {}

    for record in records:
        text = str(record.get("text") or "")
        source_id = str(record.get("source_id") or "")
        if not source_id:
            raise ValueError("Every cohort record must have source_id")
        hits = [code for code, pattern in patterns.items() if pattern.search(text)]
        if not hits:
            continue
        selected.append(record)
        matched[source_id] = hits

    if expected_count is not None and len(selected) != expected_count:
        raise ValueError(
            f"Cross-source cohort drift: expected {expected_count} records, found {len(selected)}"
        )
    return CohortSelection(records=selected, matched_codes_by_source=matched)
