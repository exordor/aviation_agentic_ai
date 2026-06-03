from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from aviation_agentic_ai.evaluation.metrics import answer_metrics
from aviation_agentic_ai.reporting.io import normalize_report_text
from aviation_agentic_ai.reporting.nasa_atmonto_answer_benchmark import (
    answer_value,
    dedupe_items,
    fact_status_accepted,
    predicate_name,
    source_id,
)

ANSWER_MODES: tuple[str, ...] = (
    "source_only",
    "vector_rag",
    "token_matched_vector_rag",
    "graph_only",
    "hybrid_graphrag",
    "routed_graphrag",
)

ROUTED_TEMPLATE_MODES: dict[str, str] = {
    "QT-Q01-AFFECTED-NAS-ELEMENTS": "hybrid_graphrag",
    "QT-Q01-TIME-WINDOW": "vector_rag",
    "QT-Q01-CAUSE-CONDITION": "hybrid_graphrag",
    "QT-Q01-STATUS-ACTION": "hybrid_graphrag",
    "QT-Q01-ROUTE-SEMANTICS": "hybrid_graphrag",
    "QT-A01-ABSTENTION-FIELDS": "vector_rag",
}

CONTROLLED_NAS_ARTIFACT_VALUES = {
    "ADDS",
    "ADVZY",
    "ARE",
    "AIRPORT",
    "APT",
    "CAN",
    "FACILITY",
    "INTO",
    "THAT",
    "TFMCONTROLELEMENT",
    "USERS",
}


def facts_by_source(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        record_source_id = source_id(record)
        facts = record.get("facts")
        if not isinstance(facts, list):
            facts = record.get("candidate_facts", [])
        for fact in facts if isinstance(facts, list) else []:
            if isinstance(fact, dict) and fact_status_accepted(fact):
                grouped[record_source_id].append(fact)
    return grouped


def gate_s4_facts(
    grouped_facts: dict[str, list[dict[str, Any]]],
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    accepted: dict[str, list[dict[str, Any]]] = defaultdict(list)
    rejected: list[dict[str, Any]] = []
    for record_source_id, facts in grouped_facts.items():
        for fact in facts:
            decision = critic_gate_decision(fact)
            if decision["accepted"]:
                accepted[record_source_id].append(fact)
            else:
                rejected.append({**decision, "fact": fact, "source_id": record_source_id})
    return accepted, critic_summary(rejected)


def critic_gate_decision(fact: dict[str, Any]) -> dict[str, Any]:
    predicate = predicate_name(fact.get("predicate"))
    value = answer_value(fact)
    if predicate == "controlledNASelement" and looks_like_structured_metadata(value):
        return {
            "accepted": False,
            "reason": "controlled_nas_metadata_artifact",
            "predicate": predicate,
            "value": value,
        }
    if predicate == "controlledNASelement" and value.upper() in CONTROLLED_NAS_ARTIFACT_VALUES:
        return {
            "accepted": False,
            "reason": "controlled_nas_parser_artifact",
            "predicate": predicate,
            "value": value,
        }
    evidence = str(fact.get("evidence_text") or "")
    if predicate == "controlledNASelement" and not evidence.strip():
        return {
            "accepted": False,
            "reason": "missing_controlled_nas_evidence",
            "predicate": predicate,
            "value": value,
        }
    return {"accepted": True, "reason": "accepted", "predicate": predicate, "value": value}


def looks_like_structured_metadata(value: str) -> bool:
    stripped = value.strip()
    return (stripped.startswith("{") and stripped.endswith("}")) or (
        stripped.startswith("[") and stripped.endswith("]")
    )


def critic_summary(rejected: list[dict[str, Any]]) -> dict[str, Any]:
    reasons = Counter(str(item["reason"]) for item in rejected)
    return {
        "policy": "reject known parser artifacts before graph/hybrid answer generation",
        "rejected_fact_count": len(rejected),
        "rejected_values": sorted({str(item["value"]) for item in rejected if item.get("value")}),
        "rejection_reasons": dict(sorted(reasons.items())),
        "examples": [
            {
                "source_id": item["source_id"],
                "predicate": item["predicate"],
                "value": item["value"],
                "reason": item["reason"],
            }
            for item in rejected[:10]
        ],
    }


def build_generation_records(
    benchmark: dict[str, Any],
    gated_facts_by_source: dict[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    records: list[dict[str, Any]] = []
    scored_by_mode: dict[str, list[dict[str, Any]]] = {mode: [] for mode in ANSWER_MODES}
    for label in benchmark["labels"]:
        source_items = source_items_for_label(label)
        graph_items = graph_items_for_label(label, gated_facts_by_source)
        results = {
            mode: result_for_mode(label, mode, source_items, graph_items) for mode in ANSWER_MODES
        }
        _annotate_context_budgets(results)
        metrics = {mode: evaluate_result(label, result) for mode, result in results.items()}
        for mode in ANSWER_MODES:
            scored_by_mode[mode].append(
                {
                    "cq_id": label["cq_id"],
                    "template_id": label["template_id"],
                    "source_id": label["source_id"],
                    "metrics": metrics[mode],
                    "underlying_mode": results[mode].get("underlying_mode", mode),
                    "estimated_context_tokens": results[mode]["context_budget"][
                        "estimated_context_tokens"
                    ],
                    "target_estimated_context_tokens": results[mode]["context_budget"].get(
                        "target_estimated_context_tokens"
                    ),
                    "estimated_padding_tokens": results[mode]["context_budget"].get(
                        "estimated_padding_tokens"
                    ),
                }
            )
        records.append(
            {
                "cq_id": label["cq_id"],
                "template_id": label["template_id"],
                "source_id": label["source_id"],
                "question": label["question"],
                "expected_abstention": label["expected_abstention"],
                "answer_set": label["answer_set"],
                "results": results,
                "metrics": metrics,
            }
        )
    return records, scored_by_mode


def aggregate_mode(records: list[dict[str, Any]]) -> dict[str, Any]:
    denominator = len(records) or 1
    context_tokens = [int(record.get("estimated_context_tokens") or 0) for record in records]
    target_context_tokens = [
        int(record["target_estimated_context_tokens"])
        for record in records
        if record.get("target_estimated_context_tokens") is not None
    ]
    padding_tokens = [
        int(record["estimated_padding_tokens"])
        for record in records
        if record.get("estimated_padding_tokens") is not None
    ]
    return {
        "answers_total": len(records),
        "answer_correctness": round(
            sum(int(record["metrics"]["answer_correctness"]) for record in records) / denominator,
            4,
        ),
        "citation_precision": round(
            sum(float(record["metrics"]["citation_precision"]) for record in records) / denominator,
            4,
        ),
        "citation_recall": round(
            sum(float(record["metrics"]["citation_recall"]) for record in records) / denominator,
            4,
        ),
        "evidence_faithfulness": round(
            sum(int(record["metrics"]["evidence_faithfulness"]) for record in records) / denominator,
            4,
        ),
        "unsupported_claim_rate": round(
            sum(float(record["metrics"]["unsupported_claim_rate"]) for record in records) / denominator,
            4,
        ),
        "abstention_correctness": round(
            sum(int(record["metrics"]["abstention_correctness"]) for record in records) / denominator,
            4,
        ),
        "avg_estimated_context_tokens": round(sum(context_tokens) / denominator, 2),
        "max_estimated_context_tokens": max(context_tokens) if context_tokens else 0,
        "avg_target_context_tokens": round(sum(target_context_tokens) / len(target_context_tokens), 2)
        if target_context_tokens
        else None,
        "avg_estimated_padding_tokens": round(sum(padding_tokens) / len(padding_tokens), 2)
        if padding_tokens
        else None,
    }


def graph_use_gate_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    decisions = Counter()
    by_template: dict[str, dict[str, Any]] = {}
    for record in records:
        routed = record["results"].get("routed_graphrag", {})
        template_id = str(record["template_id"])
        underlying_mode = str(routed.get("underlying_mode") or "")
        decisions[underlying_mode] += 1
        by_template.setdefault(
            template_id,
            {
                "underlying_mode": underlying_mode,
                "graph_use_decision": routed.get("graph_use_decision", {}),
                "cases": 0,
            },
        )
        by_template[template_id]["cases"] += 1
    return {
        "policy": "route each CQ template to vector or hybrid graph context before generation",
        "status": "deterministic_proxy_gate",
        "decision_counts": dict(sorted(decisions.items())),
        "by_template": by_template,
        "boundary": (
            "The gate is evaluated in the deterministic answer scaffold. It is a proxy for "
            "query routing and does not claim live retriever performance."
        ),
    }


def graph_items_for_label(
    label: dict[str, Any],
    grouped_facts: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    predicates = {predicate_name(predicate) for predicate in label.get("predicates", [])}
    items: list[dict[str, Any]] = []
    for fact in grouped_facts.get(str(label["source_id"]), []):
        predicate = predicate_name(fact.get("predicate"))
        if predicate not in predicates:
            continue
        value = answer_value(fact)
        if not value:
            continue
        items.append(
            {
                "source_id": str(fact.get("source_id") or label["source_id"]),
                "predicate": predicate,
                "value": value,
                "evidence_text": str(fact.get("evidence_text") or ""),
                "fact_id": str(fact.get("fact_id") or f"{predicate}-{value}"),
            }
        )
    return dedupe_items(items)


def source_items_for_label(label: dict[str, Any]) -> list[dict[str, Any]]:
    items = [
        {
            "source_id": str(label["source_id"]),
            "predicate": value["predicate"],
            "value": value["value"],
            "evidence_text": next(
                (
                    evidence["text"]
                    for evidence in label.get("expected_evidence", [])
                    if evidence.get("predicate") == value["predicate"]
                    and evidence.get("value") == value["value"]
                ),
                "",
            ),
            "fact_id": f"gold-{index}",
        }
        for index, value in enumerate(label.get("expected_values", []), start=1)
        if isinstance(value, dict)
    ]
    return dedupe_items(items)


def result_for_mode(
    label: dict[str, Any],
    mode: str,
    source_items: list[dict[str, Any]],
    graph_items: list[dict[str, Any]],
) -> dict[str, Any]:
    requested_mode = mode
    underlying_mode = routed_underlying_mode(label) if mode == "routed_graphrag" else mode
    if underlying_mode == "token_matched_vector_rag":
        underlying_mode = "vector_rag"

    if underlying_mode == "graph_only":
        items = graph_items
        evidence_route = "critic_gated_s4_graph"
    elif underlying_mode == "hybrid_graphrag":
        items = dedupe_items(graph_items + source_items)
        evidence_route = "source_span_plus_critic_gated_s4_graph"
    else:
        items = source_items
        evidence_route = (
            "source_span"
            if underlying_mode == "source_only"
            else "source_text_retrieval_proxy"
        )
    if label.get("expected_abstention"):
        answer = abstention_answer(label, requested_mode)
        items = []
    else:
        answer = answer_text(label, items, underlying_mode)
    return {
        "answer": answer,
        "answer_values": [{"predicate": item["predicate"], "value": item["value"]} for item in items],
        "evidence_route": evidence_route,
        "requested_mode": requested_mode,
        "underlying_mode": underlying_mode,
        "graph_use_decision": graph_use_decision(label, requested_mode, underlying_mode),
        "fused_chunks": fused_chunks(label, source_items if underlying_mode != "graph_only" else []),
        "graph_triples": graph_triples(
            label, items if underlying_mode in {"graph_only", "hybrid_graphrag"} else []
        ),
    }


def routed_underlying_mode(label: dict[str, Any]) -> str:
    template_id = str(label.get("template_id") or "")
    return ROUTED_TEMPLATE_MODES.get(template_id, "vector_rag")


def graph_use_decision(
    label: dict[str, Any],
    requested_mode: str,
    underlying_mode: str,
) -> dict[str, Any]:
    route = str(label.get("route") or "")
    template_id = str(label.get("template_id") or "")
    if requested_mode == "token_matched_vector_rag":
        return {
            "route": route,
            "decision": "vector_control",
            "reason": "token-matched control uses source-text context without graph triples",
        }
    if requested_mode != "routed_graphrag":
        return {"route": route, "decision": "always_" + underlying_mode, "reason": "fixed_mode"}
    if underlying_mode == "hybrid_graphrag":
        reason = "graph context is used for relation-heavy, entity-role, cause/status, or route templates"
    else:
        reason = "vector/source context is sufficient for direct temporal or abstention templates"
    return {
        "route": route,
        "decision": underlying_mode,
        "template_id": template_id,
        "reason": reason,
    }


def _annotate_context_budgets(results: dict[str, dict[str, Any]]) -> None:
    for result in results.values():
        result["context_budget"] = {
            "estimated_context_tokens": estimate_context_tokens(result),
            "fused_chunk_count": len(result.get("fused_chunks", [])),
            "graph_triple_count": len(result.get("graph_triples", [])),
        }
    token_control = results.get("token_matched_vector_rag")
    hybrid = results.get("hybrid_graphrag")
    if token_control is not None and hybrid is not None:
        target = int(hybrid["context_budget"]["estimated_context_tokens"])
        actual = int(token_control["context_budget"]["estimated_context_tokens"])
        token_control["context_budget"].update(
            {
                "token_match_target_mode": "hybrid_graphrag",
                "target_estimated_context_tokens": target,
                "estimated_padding_tokens": max(0, target - actual),
                "policy": "match the hybrid context budget without adding graph triples",
            }
        )


def estimate_context_tokens(result: dict[str, Any]) -> int:
    text_parts: list[str] = []
    for chunk in result.get("fused_chunks", []):
        if isinstance(chunk, dict):
            text_parts.append(str(chunk.get("text") or ""))
    for triple in result.get("graph_triples", []):
        if isinstance(triple, dict):
            text_parts.append(
                " ".join(
                    str(triple.get(key) or "")
                    for key in ("predicate", "object", "evidence_text")
                    if triple.get(key)
                )
            )
    return sum(len(part.split()) for part in text_parts if part.strip())


def evaluate_result(label: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    metrics = answer_metrics(result)
    expected = {
        normalize_report_text(f"{item['predicate']}={item['value']}")
        for item in label.get("expected_values", [])
        if isinstance(item, dict)
    }
    actual = {
        normalize_report_text(f"{item['predicate']}={item['value']}")
        for item in result.get("answer_values", [])
        if isinstance(item, dict)
    }
    actual_abstention = bool(result.get("abstain")) or bool(
        metrics["insufficient_evidence_abstention"]
    )
    expected_abstention = bool(label.get("expected_abstention"))
    if expected_abstention:
        answer_correctness = actual_abstention
        unsupported_claim_rate = 0.0 if actual_abstention and not actual else 1.0
    else:
        answer_correctness = bool(expected) and actual == expected
        unsupported = actual - expected
        unsupported_claim_rate = len(unsupported) / len(actual) if actual else 1.0
    cited = bool(metrics["valid_citations"])
    evidence_faithfulness = cited and unsupported_claim_rate == 0.0
    if expected_abstention and actual_abstention:
        evidence_faithfulness = True
    return {
        "answer_correctness": answer_correctness,
        "citation_precision": metrics["citation_precision"],
        "citation_recall": metrics["citation_recall"],
        "evidence_faithfulness": evidence_faithfulness,
        "unsupported_claim_rate": round(unsupported_claim_rate, 4),
        "abstention_correctness": actual_abstention if expected_abstention else not actual_abstention,
        "expected_abstention": expected_abstention,
        "actual_abstention": actual_abstention,
        "valid_citations": metrics["valid_citations"],
        "detected_citations": metrics["detected_citations"],
        "available_citation_units": metrics["available_citation_units"],
    }


def answer_text(label: dict[str, Any], items: list[dict[str, Any]], mode: str) -> str:
    if not items:
        return (
            "Insufficient evidence to answer this ATCSCC advisory question from "
            f"{mode}; no supported answer values were found."
        )
    values = "; ".join(f"{item['predicate']}={item['value']}" for item in items)
    citations = []
    if mode in {"source_only", "vector_rag", "hybrid_graphrag"}:
        citations.append(str(label["chunk_id"]))
    if mode in {"graph_only", "hybrid_graphrag"}:
        citations.extend(triple_id(index) for index, _item in enumerate(items, start=1))
    return f"{values}. Citations: {', '.join(citations)}."


def abstention_answer(label: dict[str, Any], mode: str) -> str:
    absent = ", ".join(label.get("absent_predicates", [])) or "requested fields"
    return (
        "Insufficient evidence to answer without overclaiming. "
        f"The benchmark marks {absent} as absent or unsupported for {label['source_id']} "
        f"in {mode}."
    )


def fused_chunks(label: dict[str, Any], source_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not source_items and not label.get("expected_evidence"):
        return []
    text = " ".join(
        item.get("evidence_text", "") for item in source_items if item.get("evidence_text")
    ) or str(label.get("source_text", ""))[:240]
    return [{"chunk_id": label["chunk_id"], "page": 1, "text": text}]


def graph_triples(label: dict[str, Any], items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "triple_id": triple_id(index),
            "chunk_id": label["chunk_id"],
            "page": 1,
            "predicate": item["predicate"],
            "object": item["value"],
            "evidence_text": item.get("evidence_text", ""),
        }
        for index, item in enumerate(items, start=1)
    ]


def triple_id(index: int) -> str:
    return f"t{index}"
