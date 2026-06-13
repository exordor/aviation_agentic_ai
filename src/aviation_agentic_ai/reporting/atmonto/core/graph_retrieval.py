from __future__ import annotations

from collections import defaultdict
from typing import Any

from aviation_agentic_ai.reporting.atmonto.core.answer_benchmark import (
    answer_value,
    dedupe_items,
    predicate_name,
)


def build_materialized_atcscc_fact_graph(
    gated_facts_by_source: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    facts_by_source: dict[str, list[dict[str, Any]]] = defaultdict(list)
    facts_by_source_predicate: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    predicate_counts: dict[str, int] = defaultdict(int)
    fact_count = 0
    for source_id, facts in gated_facts_by_source.items():
        for fact in facts:
            predicate = predicate_name(fact.get("predicate"))
            value = answer_value(fact)
            if not predicate or not value:
                continue
            item = {
                "source_id": str(fact.get("source_id") or source_id),
                "predicate": predicate,
                "value": value,
                "evidence_text": str(fact.get("evidence_text") or ""),
                "fact_id": fact.get("fact_id"),
                "graph_path": [
                    str(fact.get("source_id") or source_id),
                    predicate,
                    value,
                ],
            }
            facts_by_source[str(source_id)].append(item)
            facts_by_source_predicate[(str(source_id), predicate)].append(item)
            predicate_counts[predicate] += 1
            fact_count += 1
    return {
        "facts_by_source": dict(facts_by_source),
        "facts_by_source_predicate": dict(facts_by_source_predicate),
        "source_node_count": len(facts_by_source),
        "fact_node_count": fact_count,
        "edge_count": fact_count * 2,
        "predicate_counts": dict(sorted(predicate_counts.items())),
    }


def traverse_materialized_graph_for_label(
    graph: dict[str, Any],
    label: dict[str, Any],
) -> list[dict[str, Any]]:
    source_id = str(label.get("source_id") or "")
    predicates = [str(predicate) for predicate in label.get("predicates", [])]
    facts_by_source_predicate = graph.get("facts_by_source_predicate", {})
    items: list[dict[str, Any]] = []
    for predicate in predicates:
        items.extend(facts_by_source_predicate.get((source_id, predicate), []))
    return dedupe_items(items)
