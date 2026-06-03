from __future__ import annotations

from collections import Counter
from pathlib import Path
from time import perf_counter
from typing import Any

from aviation_agentic_ai.evaluation.metrics import (
    aggregate_retrieval_metrics,
    retrieval_metrics,
)
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import normalize_report_text, write_json_report
from aviation_agentic_ai.reporting.nasa_atmonto_answer_benchmark import (
    build_answer_eval_benchmark,
    dedupe_items,
    load_query_manifest,
    read_jsonl_objects,
    resolve_path,
)
from aviation_agentic_ai.reporting.nasa_atmonto_answer_scoring import (
    facts_by_source,
    gate_s4_facts,
    graph_items_for_label,
    routed_underlying_mode,
    source_items_for_label,
)
from aviation_agentic_ai.reporting.nasa_atmonto_cq_queries import DEFAULT_GOLD_PATH

DEFAULT_S4_PREDICTION_PATH = Path(
    "data/experiments/nasa_atmonto/formal/s4_hybrid_backbone_enrichment_predictions.jsonl"
)
DEFAULT_QUERY_MANIFEST_PATH = Path("data/evaluation/nasa_atmonto/atcscc_cq_query_templates.json")

RETRIEVAL_MODES: tuple[str, ...] = (
    "source_oracle",
    "vector_rag_proxy",
    "token_matched_vector_proxy",
    "graph_only",
    "hybrid_graphrag",
    "routed_graphrag",
)


def build_nasa_atmonto_s7_retrieval(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    gold_path: str | Path = DEFAULT_GOLD_PATH,
    s4_prediction_path: str | Path = DEFAULT_S4_PREDICTION_PATH,
    query_manifest_path: str | Path | None = DEFAULT_QUERY_MANIFEST_PATH,
    max_cases_per_template: int = 1000,
) -> dict[str, Any]:
    started = perf_counter()
    root = Path(repo_root)
    gold_file = resolve_path(root, gold_path)
    s4_file = resolve_path(root, s4_prediction_path)
    query_manifest = load_query_manifest(root, query_manifest_path, DEFAULT_QUERY_MANIFEST_PATH)
    gold_records = read_jsonl_objects(gold_file)
    s4_records = read_jsonl_objects(s4_file)
    benchmark = build_answer_eval_benchmark(
        gold_records=gold_records,
        query_manifest=query_manifest,
        max_cases_per_template=max_cases_per_template,
    )
    gated_facts_by_source, critic_gate = gate_s4_facts(facts_by_source(s4_records))
    records = [
        retrieval_record_for_label(label, gated_facts_by_source)
        for label in benchmark["labels"]
    ]
    aggregate_by_mode = {
        mode: aggregate_retrieval_mode([record["modes"][mode] for record in records])
        for mode in RETRIEVAL_MODES
    }
    elapsed_seconds = perf_counter() - started
    return {
        "source_family": "nasa_atmonto_s7_retrieval",
        "status": "s7_retrieval_proxy_evaluated",
        "metadata": {
            "gold_path": project_relative_path(gold_file, root),
            "s4_prediction_path": project_relative_path(s4_file, root),
            "query_manifest_path": project_relative_path(
                query_manifest_path or DEFAULT_QUERY_MANIFEST_PATH
            ),
            "template_count": query_manifest.get("metadata", {}).get("template_count")
            or len(query_manifest.get("templates", [])),
            "retrieval_case_count": len(records),
            "modes": list(RETRIEVAL_MODES),
            "max_cases_per_template": max_cases_per_template,
            "elapsed_seconds": round(elapsed_seconds, 4),
            "boundary": (
                "Retrieval-only deterministic proxy over source-bounded ATCSCC labels. "
                "Vector modes use source-text proxy context, not a live vector index."
            ),
        },
        "critic_gate": critic_gate,
        "aggregate_by_mode": aggregate_by_mode,
        "route_summary": route_summary(records),
        "records": records,
        "claim_boundary": (
            "This report evaluates retrieval-context availability, graph path support, "
            "answer-set recovery, and token-budget proxies. It does not prove live "
            "GraphRAG or vector-index performance."
        ),
    }


def retrieval_record_for_label(
    label: dict[str, Any],
    gated_facts_by_source: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    source_items = source_items_for_label(label)
    graph_items = graph_items_for_label(label, gated_facts_by_source)
    modes = {
        mode: retrieval_mode_result(label, mode, source_items, graph_items)
        for mode in RETRIEVAL_MODES
    }
    annotate_token_match(modes)
    return {
        "cq_id": label["cq_id"],
        "template_id": label["template_id"],
        "source_id": label["source_id"],
        "question": label["question"],
        "expected_abstention": label["expected_abstention"],
        "expected_answer_count": len(label.get("expected_values", [])),
        "route": label.get("route", ""),
        "modes": modes,
    }


def retrieval_mode_result(
    label: dict[str, Any],
    mode: str,
    source_items: list[dict[str, Any]],
    graph_items: list[dict[str, Any]],
) -> dict[str, Any]:
    underlying_mode = routed_underlying_mode(label) if mode == "routed_graphrag" else mode
    if mode == "token_matched_vector_proxy":
        underlying_mode = "vector_rag_proxy"
    contexts, answer_items = contexts_for_mode(label, underlying_mode, source_items, graph_items)
    retrieval = retrieval_metrics(contexts, label)
    answer_set = answer_set_metrics(label, answer_items)
    path_support = graph_path_support(label, answer_items) if uses_graph(underlying_mode) else None
    return {
        "requested_mode": mode,
        "underlying_mode": underlying_mode,
        "retrieval": retrieval,
        "answer_set": answer_set,
        "path_support": path_support,
        "context_budget": {
            "estimated_context_tokens": estimate_context_tokens(contexts),
            "context_count": len(contexts),
            "graph_context_count": sum(1 for context in contexts if context.get("kind") == "graph_triple"),
            "source_context_count": sum(1 for context in contexts if context.get("kind") == "source_chunk"),
        },
        "graph_use_decision": graph_use_decision(label, mode, underlying_mode),
    }


def contexts_for_mode(
    label: dict[str, Any],
    mode: str,
    source_items: list[dict[str, Any]],
    graph_items: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_context = source_context_for_label(label, source_items)
    graph_context = graph_contexts_for_items(label, graph_items)
    if label.get("expected_abstention"):
        if mode == "graph_only":
            return graph_context, graph_items
        if mode == "hybrid_graphrag":
            return dedupe_contexts(graph_context + source_context), graph_items
        return source_context, []
    if mode == "graph_only":
        return graph_context, graph_items
    if mode == "hybrid_graphrag":
        return dedupe_contexts(graph_context + source_context), dedupe_items(graph_items + source_items)
    return source_context, source_items


def source_context_for_label(
    label: dict[str, Any],
    source_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if label.get("expected_abstention") and not source_items:
        text = str(label.get("source_text", ""))[:500]
    else:
        text = " ".join(
            item.get("evidence_text", "") for item in source_items if item.get("evidence_text")
        ) or str(label.get("source_text", ""))[:500]
    return [
        {
            "kind": "source_chunk",
            "chunk_id": label["chunk_id"],
            "page": 1,
            "text": text,
            "source_id": label["source_id"],
        }
    ] if text else []


def graph_contexts_for_items(label: dict[str, Any], graph_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "kind": "graph_triple",
            "chunk_id": label["chunk_id"],
            "page": 1,
            "text": item.get("evidence_text", ""),
            "source_id": item.get("source_id") or label["source_id"],
            "predicate": item.get("predicate"),
            "value": item.get("value"),
            "fact_id": item.get("fact_id"),
        }
        for item in graph_items
        if item.get("evidence_text") or item.get("value")
    ]


def dedupe_contexts(contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for context in contexts:
        key = (
            str(context.get("kind") or ""),
            str(context.get("chunk_id") or ""),
            normalize_report_text(context.get("text") or context.get("value") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(context)
    return deduped


def answer_set_metrics(label: dict[str, Any], answer_items: list[dict[str, Any]]) -> dict[str, Any]:
    expected = {
        normalize_report_text(f"{item['predicate']}={item['value']}")
        for item in label.get("expected_values", [])
        if isinstance(item, dict)
    }
    actual = {
        normalize_report_text(f"{item['predicate']}={item['value']}")
        for item in answer_items
        if isinstance(item, dict)
    }
    abstention_correct = None
    if label.get("expected_abstention"):
        expected = {normalize_report_text(item) for item in label.get("answer_set", [])}
        abstention_correct = not actual
        if abstention_correct:
            actual = set(expected)
    true_positive = len(expected & actual)
    false_positive = len(actual - expected)
    false_negative = len(expected - actual)
    precision = true_positive / len(actual) if actual else None
    recall = true_positive / len(expected) if expected else None
    f1 = None
    if precision is not None and recall is not None and precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    return {
        "expected_count": len(expected),
        "retrieved_count": len(actual),
        "true_positive_count": true_positive,
        "false_positive_count": false_positive,
        "false_negative_count": false_negative,
        "precision": round(precision, 4) if precision is not None else None,
        "recall": round(recall, 4) if recall is not None else None,
        "f1": round(f1, 4) if f1 is not None else None,
        "expected_abstention": bool(label.get("expected_abstention")),
        "abstention_correct": abstention_correct,
    }


def graph_path_support(label: dict[str, Any], graph_items: list[dict[str, Any]]) -> dict[str, Any]:
    expected = {
        normalize_report_text(f"{item['predicate']}={item['value']}")
        for item in label.get("expected_values", [])
        if isinstance(item, dict)
    }
    graph = {
        normalize_report_text(f"{item['predicate']}={item['value']}")
        for item in graph_items
        if isinstance(item, dict)
    }
    supported = expected & graph
    return {
        "expected_graph_answer_count": len(expected),
        "supported_graph_answer_count": len(supported),
        "path_support_rate": round(len(supported) / len(expected), 4) if expected else None,
    }


def uses_graph(mode: str) -> bool:
    return mode in {"graph_only", "hybrid_graphrag"}


def graph_use_decision(label: dict[str, Any], requested_mode: str, underlying_mode: str) -> dict[str, Any]:
    if requested_mode == "token_matched_vector_proxy":
        return {
            "decision": "vector_control",
            "reason": "token-matched control uses source-text proxy context without graph triples",
        }
    if requested_mode != "routed_graphrag":
        return {"decision": "always_" + underlying_mode, "reason": "fixed_mode"}
    if underlying_mode == "hybrid_graphrag":
        reason = "graph context selected for semantic, entity-role, cause/status, or route query"
    else:
        reason = "source/vector proxy selected for direct temporal or abstention query"
    return {
        "decision": underlying_mode,
        "template_id": label.get("template_id"),
        "reason": reason,
    }


def annotate_token_match(modes: dict[str, dict[str, Any]]) -> None:
    token_control = modes.get("token_matched_vector_proxy")
    hybrid = modes.get("hybrid_graphrag")
    if token_control is None or hybrid is None:
        return
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


def estimate_context_tokens(contexts: list[dict[str, Any]]) -> int:
    return sum(len(str(context.get("text") or "").split()) for context in contexts)


def aggregate_retrieval_mode(items: list[dict[str, Any]]) -> dict[str, Any]:
    retrieval = aggregate_retrieval_metrics([item["retrieval"] for item in items])
    answer = aggregate_answer_set_metrics([item["answer_set"] for item in items])
    path_support_values = [
        float(item["path_support"]["path_support_rate"])
        for item in items
        if item.get("path_support")
        and item["path_support"].get("path_support_rate") is not None
    ]
    tokens = [int(item["context_budget"]["estimated_context_tokens"]) for item in items]
    target_tokens = [
        int(item["context_budget"]["target_estimated_context_tokens"])
        for item in items
        if item["context_budget"].get("target_estimated_context_tokens") is not None
    ]
    return {
        "retrieval": retrieval,
        "answer_set": answer,
        "abstention_correctness": aggregate_abstention_correctness(
            [item["answer_set"] for item in items]
        ),
        "avg_path_support_rate": round(sum(path_support_values) / len(path_support_values), 4)
        if path_support_values
        else None,
        "avg_estimated_context_tokens": round(sum(tokens) / len(tokens), 2) if tokens else 0.0,
        "avg_target_context_tokens": round(sum(target_tokens) / len(target_tokens), 2)
        if target_tokens
        else None,
    }


def aggregate_answer_set_metrics(items: list[dict[str, Any]]) -> dict[str, Any]:
    totals = Counter()
    f1_values: list[float] = []
    for item in items:
        for key in (
            "expected_count",
            "retrieved_count",
            "true_positive_count",
            "false_positive_count",
            "false_negative_count",
        ):
            totals[key] += int(item.get(key) or 0)
        if item.get("f1") is not None:
            f1_values.append(float(item["f1"]))
    precision = totals["true_positive_count"] / totals["retrieved_count"] if totals["retrieved_count"] else None
    recall = totals["true_positive_count"] / totals["expected_count"] if totals["expected_count"] else None
    f1 = None
    if precision is not None and recall is not None and precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    return {
        **dict(totals),
        "micro_precision": round(precision, 4) if precision is not None else None,
        "micro_recall": round(recall, 4) if recall is not None else None,
        "micro_f1": round(f1, 4) if f1 is not None else None,
        "macro_f1": round(sum(f1_values) / len(items), 4) if items else None,
    }


def aggregate_abstention_correctness(items: list[dict[str, Any]]) -> float | None:
    abstention_items = [
        item for item in items if item.get("expected_abstention") and item.get("abstention_correct") is not None
    ]
    if not abstention_items:
        return None
    return round(
        sum(int(bool(item["abstention_correct"])) for item in abstention_items)
        / len(abstention_items),
        4,
    )


def route_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    decisions = Counter()
    by_template: dict[str, dict[str, Any]] = {}
    for record in records:
        routed = record["modes"]["routed_graphrag"]
        template_id = str(record["template_id"])
        underlying_mode = str(routed["underlying_mode"])
        decisions[underlying_mode] += 1
        by_template.setdefault(
            template_id,
            {
                "underlying_mode": underlying_mode,
                "cases": 0,
                "decision": routed["graph_use_decision"],
            },
        )
        by_template[template_id]["cases"] += 1
    return {
        "decision_counts": dict(sorted(decisions.items())),
        "by_template": by_template,
    }


def write_nasa_atmonto_s7_retrieval_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO S7 Retrieval-Only Graph-Use Gate",
        "",
        "## Scope",
        "",
        f"- Status: `{result['status']}`",
        f"- Retrieval cases: {result['metadata']['retrieval_case_count']}",
        f"- Modes: {', '.join(f'`{mode}`' for mode in result['metadata']['modes'])}",
        f"- Boundary: {result['metadata']['boundary']}",
        "",
        "## Aggregate Retrieval Metrics",
        "",
        (
            "| Mode | Recall@5 | Context recall | Answer P | Answer R | Answer F1 | "
            "Abstention correct | Path support | Avg tokens | Target tokens |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mode, metrics in result["aggregate_by_mode"].items():
        retrieval = metrics["retrieval"]
        answer = metrics["answer_set"]
        target_tokens = metrics["avg_target_context_tokens"]
        lines.append(
            f"| `{mode}` | {retrieval['recall_at_5']} | {retrieval['context_recall']} | "
            f"{answer['micro_precision']} | {answer['micro_recall']} | {answer['micro_f1']} | "
            f"{metrics['abstention_correctness']} | {metrics['avg_path_support_rate']} | "
            f"{metrics['avg_estimated_context_tokens']} | "
            f"{target_tokens if target_tokens is not None else 'n/a'} |"
        )
    lines.extend(
        [
            "",
            "Method note: Answer-set F1 treats a correct expected abstention as recovering "
            "the no-answer label. `Abstention correct` is computed only over expected "
            "abstention cases and should be read separately from non-abstention answer recovery.",
            "",
            "## Graph-Use Route Summary",
            "",
            f"- Decision counts: {result['route_summary']['decision_counts']}",
            "",
            "| Template | Underlying mode | Cases | Reason |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for template_id, item in result["route_summary"]["by_template"].items():
        decision = item.get("decision", {})
        lines.append(
            f"| `{template_id}` | `{item['underlying_mode']}` | {item['cases']} | "
            f"{decision.get('reason', '')} |"
        )
    lines.extend(
        [
            "",
            "## Critic Gate",
            "",
            f"- Policy: {result['critic_gate']['policy']}",
            f"- Rejected facts: {result['critic_gate']['rejected_fact_count']}",
            f"- Rejected values: {', '.join(result['critic_gate']['rejected_values']) or 'none'}",
            "",
            "## Claim Boundary",
            "",
            result["claim_boundary"],
        ]
    )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_nasa_atmonto_s7_retrieval(
    *,
    output_dir: str | Path,
    repo_root: str | Path = PROJECT_ROOT,
    gold_path: str | Path = DEFAULT_GOLD_PATH,
    s4_prediction_path: str | Path = DEFAULT_S4_PREDICTION_PATH,
    query_manifest_path: str | Path | None = DEFAULT_QUERY_MANIFEST_PATH,
    report_name: str = "nasa_atmonto_s7_retrieval",
    max_cases_per_template: int = 1000,
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_nasa_atmonto_s7_retrieval(
        repo_root=repo_root,
        gold_path=gold_path,
        s4_prediction_path=s4_prediction_path,
        query_manifest_path=query_manifest_path,
        max_cases_per_template=max_cases_per_template,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "nasa_atmonto_s7_retrieval"
    json_path = write_json_report(result, output / f"{stem}.json", sort_keys=False)
    md_path = write_nasa_atmonto_s7_retrieval_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
