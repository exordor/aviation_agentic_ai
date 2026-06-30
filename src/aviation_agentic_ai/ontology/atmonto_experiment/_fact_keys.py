"""AUTO-SPLIT from ontology/atmonto_experiment.py. See git history."""
from __future__ import annotations

from typing import Any

from ._io import (
    compact_text,
    term_name,
)

FactKey = tuple[str, str, str, str, str, str, str]

def fact_with_source_id(fact: dict[str, Any], source_id: object) -> dict[str, Any]:
    if fact.get("source_id") not in (None, "") or source_id in (None, ""):
        return fact
    return {**fact, "source_id": source_id}

def canonical_fact_key(fact: dict[str, Any]) -> FactKey:
    value = fact.get("object") if fact.get("fact_type") == "object_property" else fact.get("value")
    return (
        compact_text(fact.get("source_id")),
        term_name(fact.get("subject_class")),
        term_name(fact.get("predicate")),
        compact_text(value).lower(),
        term_name(fact.get("object_class")),
        term_name(fact.get("datatype")),
        compact_text(fact.get("evidence_text")).lower(),
    )

def evidence_tolerant_fact_key(fact: dict[str, Any]) -> tuple[str, ...]:
    """Fact identity ignoring the evidence_text span.

    Matches :func:`canonical_fact_key` on source id, subject class, predicate,
    value, object class, and datatype, so two facts that differ only in how
    their evidence is quoted count as the same fact. This separates extraction
    quality from evidence-citation formatting, which is useful when comparing an
    LLM extractor against a rule baseline that cites concatenated header spans.
    """
    return canonical_fact_key(fact)[:6]

def fact_key_predicate(key: FactKey) -> str:
    return key[2]
