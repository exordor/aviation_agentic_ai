"""Load the tracked FAA terminology seed without historical config coupling."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from aviation_agentic_ai.authority.contracts import (
    TermCategory,
    TermConcept,
    TermDefinition,
)
from aviation_agentic_ai.authority.identifiers import (
    canonical_term_id,
    normalize_code,
)
from aviation_agentic_ai.config import load_yaml


def _unique_strings(values: Iterable[object]) -> list[str]:
    return sorted({str(value).strip() for value in values if str(value).strip()})


def load_term_registry(seed_path: str | Path) -> list[TermConcept]:
    """Load and stably order authority terms from one explicit seed file."""

    payload = load_yaml(str(seed_path))
    terms: list[TermConcept] = []
    for item in payload.get("terms", []):
        category = TermCategory(str(item["category"]))
        abbreviation = normalize_code(item["abbreviation"])
        terms.append(
            TermConcept(
                term_id=canonical_term_id(category, abbreviation),
                abbreviation=abbreviation,
                preferred_label=str(item["preferred_label"]),
                term_category=category,
                aliases=_unique_strings(item.get("aliases", [])),
                definitions=[
                    TermDefinition(
                        text=str(definition["text"]),
                        source_ref=str(definition["source_ref"]),
                    )
                    for definition in item.get("definitions", [])
                ],
                denotes_schema_term=item.get("denotes_schema_term"),
                source_refs=_unique_strings(item.get("source_refs", [])),
            )
        )
    return sorted(terms, key=lambda item: (item.abbreviation, item.term_id))
