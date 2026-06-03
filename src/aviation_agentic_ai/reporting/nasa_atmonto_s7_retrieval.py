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
    routed_underlying_mode,
    source_items_for_label,
)
from aviation_agentic_ai.reporting.nasa_atmonto_cq_queries import DEFAULT_GOLD_PATH
from aviation_agentic_ai.reporting.nasa_atmonto_graph_retrieval import (
    build_materialized_atcscc_fact_graph,
    traverse_materialized_graph_for_label,
)
from aviation_agentic_ai.reporting.nasa_atmonto_live_retrieval import (
    DEFAULT_DENSE_MODEL_NAME,
    DenseEncoder,
    build_dense_source_index,
    build_live_tfidf_source_index,
    query_dense_source_index,
    query_live_tfidf_source_index,
)

DEFAULT_S4_PREDICTION_PATH = Path(
    "data/experiments/nasa_atmonto/formal/s4_hybrid_backbone_enrichment_predictions.jsonl"
)
DEFAULT_QUERY_MANIFEST_PATH = Path("data/evaluation/nasa_atmonto/atcscc_cq_query_templates.json")
DEFAULT_SOURCE_RECORD_PATH = Path("data/experiments/nasa_atmonto/formal/input_records.jsonl")

RETRIEVAL_MODES: tuple[str, ...] = (
    "source_oracle",
    "vector_rag_proxy",
    "token_matched_vector_proxy",
    "live_tfidf_vector",
    "token_matched_live_tfidf_vector",
    "dense_embedding_vector",
    "token_matched_dense_embedding_vector",
    "graph_only",
    "hybrid_graphrag",
    "routed_graphrag",
    "routed_live_tfidf_graphrag",
    "routed_token_matched_live_tfidf_graphrag",
    "routed_dense_graphrag",
    "routed_token_matched_dense_graphrag",
)


def build_nasa_atmonto_s7_retrieval(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    gold_path: str | Path = DEFAULT_GOLD_PATH,
    s4_prediction_path: str | Path = DEFAULT_S4_PREDICTION_PATH,
    source_record_path: str | Path = DEFAULT_SOURCE_RECORD_PATH,
    query_manifest_path: str | Path | None = DEFAULT_QUERY_MANIFEST_PATH,
    max_cases_per_template: int = 1000,
    live_top_k: int = 5,
    dense_model_name: str = DEFAULT_DENSE_MODEL_NAME,
    dense_local_files_only: bool = True,
    dense_encoder: DenseEncoder | None = None,
) -> dict[str, Any]:
    started = perf_counter()
    root = Path(repo_root)
    gold_file = resolve_path(root, gold_path)
    s4_file = resolve_path(root, s4_prediction_path)
    source_file = resolve_path(root, source_record_path)
    query_manifest = load_query_manifest(root, query_manifest_path, DEFAULT_QUERY_MANIFEST_PATH)
    gold_records = read_jsonl_objects(gold_file)
    s4_records = read_jsonl_objects(s4_file)
    source_records = read_jsonl_objects(source_file)
    benchmark = build_answer_eval_benchmark(
        gold_records=gold_records,
        query_manifest=query_manifest,
        max_cases_per_template=max_cases_per_template,
    )
    gated_facts_by_source, critic_gate = gate_s4_facts(facts_by_source(s4_records))
    live_source_index = build_live_tfidf_source_index(source_records)
    dense_source_index = build_dense_source_index(
        source_records,
        model_name=dense_model_name,
        local_files_only=dense_local_files_only,
        encoder=dense_encoder,
    )
    materialized_graph = build_materialized_atcscc_fact_graph(gated_facts_by_source)
    answer_items_by_template_source = answer_items_index(benchmark["labels"])
    records = [
        retrieval_record_for_label(
            label,
            materialized_graph,
            live_source_index=live_source_index,
            dense_source_index=dense_source_index,
            answer_items_by_template_source=answer_items_by_template_source,
            live_top_k=live_top_k,
        )
        for label in benchmark["labels"]
    ]
    aggregate_by_mode = {
        mode: aggregate_retrieval_mode([record["modes"][mode] for record in records])
        for mode in RETRIEVAL_MODES
    }
    elapsed_seconds = perf_counter() - started
    return {
        "source_family": "nasa_atmonto_s7_retrieval",
        "status": "s7_retrieval_gate_evaluated",
        "metadata": {
            "gold_path": project_relative_path(gold_file, root),
            "s4_prediction_path": project_relative_path(s4_file, root),
            "source_record_path": project_relative_path(source_file, root),
            "query_manifest_path": project_relative_path(
                query_manifest_path or DEFAULT_QUERY_MANIFEST_PATH
            ),
            "template_count": query_manifest.get("metadata", {}).get("template_count")
            or len(query_manifest.get("templates", [])),
            "retrieval_case_count": len(records),
            "modes": list(RETRIEVAL_MODES),
            "max_cases_per_template": max_cases_per_template,
            "live_top_k": live_top_k,
            "live_source_document_count": live_source_index["document_count"],
            "dense_model_name": dense_source_index["model_name"],
            "dense_local_files_only": dense_source_index["local_files_only"],
            "dense_source_document_count": dense_source_index["document_count"],
            "graph_source_node_count": materialized_graph["source_node_count"],
            "graph_fact_node_count": materialized_graph["fact_node_count"],
            "graph_edge_count": materialized_graph["edge_count"],
            "elapsed_seconds": round(elapsed_seconds, 4),
            "boundary": (
                "Retrieval-only evaluation over source-bounded ATCSCC labels. "
                "Live retrieval modes include deterministic lexical TF-IDF and "
                "dense embedding source indexes over frozen ATCSCC records."
            ),
        },
        "critic_gate": critic_gate,
        "aggregate_by_mode": aggregate_by_mode,
        "route_summary": route_summary(records),
        "records": records,
        "claim_boundary": (
            "This report evaluates retrieval-context availability, graph path support, "
            "answer-set recovery, live lexical-vector retrieval, dense-vector retrieval, "
            "and token-budget controls. It does not prove operational GraphRAG performance."
        ),
    }


def retrieval_record_for_label(
    label: dict[str, Any],
    materialized_graph: dict[str, Any],
    *,
    live_source_index: dict[str, Any],
    dense_source_index: dict[str, Any],
    answer_items_by_template_source: dict[tuple[str, str], list[dict[str, Any]]],
    live_top_k: int,
) -> dict[str, Any]:
    source_items = source_items_for_label(label)
    graph_items = traverse_materialized_graph_for_label(materialized_graph, label)
    modes = {
        mode: retrieval_mode_result(
            label,
            mode,
            source_items,
            graph_items,
            live_source_index=live_source_index,
            dense_source_index=dense_source_index,
            answer_items_by_template_source=answer_items_by_template_source,
            live_top_k=live_top_k,
        )
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
    *,
    live_source_index: dict[str, Any],
    dense_source_index: dict[str, Any],
    answer_items_by_template_source: dict[tuple[str, str], list[dict[str, Any]]],
    live_top_k: int,
) -> dict[str, Any]:
    started = perf_counter()
    route_mode = routed_underlying_mode(label)
    if mode == "routed_graphrag":
        underlying_mode = route_mode
    elif mode == "routed_live_tfidf_graphrag":
        underlying_mode = "hybrid_graphrag" if route_mode == "hybrid_graphrag" else "live_tfidf_vector"
    elif mode == "routed_token_matched_live_tfidf_graphrag":
        underlying_mode = "hybrid_graphrag" if route_mode == "hybrid_graphrag" else "live_tfidf_vector"
    elif mode == "routed_dense_graphrag":
        underlying_mode = (
            "hybrid_graphrag" if route_mode == "hybrid_graphrag" else "dense_embedding_vector"
        )
    elif mode == "routed_token_matched_dense_graphrag":
        underlying_mode = (
            "hybrid_graphrag" if route_mode == "hybrid_graphrag" else "dense_embedding_vector"
        )
    else:
        underlying_mode = mode
    if mode == "token_matched_vector_proxy":
        underlying_mode = "vector_rag_proxy"
    if mode == "token_matched_live_tfidf_vector":
        underlying_mode = "live_tfidf_vector"
    if mode == "token_matched_dense_embedding_vector":
        underlying_mode = "dense_embedding_vector"
    if underlying_mode == "live_tfidf_vector":
        contexts, answer_items = live_contexts_for_label(
            label,
            live_source_index,
            answer_items_by_template_source,
            top_k=live_top_k,
        )
        if mode in {
            "token_matched_live_tfidf_vector",
            "routed_token_matched_live_tfidf_graphrag",
        }:
            target_contexts, _ = contexts_for_mode(label, "hybrid_graphrag", source_items, graph_items)
            contexts = trim_contexts_to_evidence_budget(
                contexts,
                label,
                estimate_context_tokens(target_contexts),
            )
    elif underlying_mode == "dense_embedding_vector":
        contexts, answer_items = dense_contexts_for_label(
            label,
            dense_source_index,
            answer_items_by_template_source,
            top_k=live_top_k,
        )
        if mode in {
            "token_matched_dense_embedding_vector",
            "routed_token_matched_dense_graphrag",
        }:
            target_contexts, _ = contexts_for_mode(label, "hybrid_graphrag", source_items, graph_items)
            contexts = trim_contexts_to_evidence_budget(
                contexts,
                label,
                estimate_context_tokens(target_contexts),
            )
    else:
        contexts, answer_items = contexts_for_mode(label, underlying_mode, source_items, graph_items)
    retrieval_latency_ms = (perf_counter() - started) * 1000
    retrieval = retrieval_metrics(contexts, label)
    target_source_retrieved = any(context.get("source_id") == label["source_id"] for context in contexts)
    answer_set = answer_set_metrics(
        label,
        answer_items,
        abstention_source_supported=not uses_live_source_retrieval(underlying_mode)
        or target_source_retrieved,
    )
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
        "runtime": {"retrieval_latency_ms": round(retrieval_latency_ms, 4)},
        "target_source_retrieved": target_source_retrieved,
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


def answer_items_index(labels: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    return {
        (str(label["template_id"]), str(label["source_id"])): source_items_for_label(label)
        for label in labels
        if not label.get("expected_abstention")
    }


def live_contexts_for_label(
    label: dict[str, Any],
    live_source_index: dict[str, Any],
    answer_items_by_template_source: dict[tuple[str, str], list[dict[str, Any]]],
    *,
    top_k: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    contexts = query_live_tfidf_source_index(
        live_source_index,
        live_query_for_label(label),
        top_k=top_k,
    )
    if label.get("expected_abstention"):
        return contexts, []
    answer_items: list[dict[str, Any]] = []
    template_id = str(label["template_id"])
    for context in contexts:
        source_id = str(context.get("source_id") or "")
        answer_items.extend(answer_items_by_template_source.get((template_id, source_id), []))
    return contexts, dedupe_items(answer_items)


def dense_contexts_for_label(
    label: dict[str, Any],
    dense_source_index: dict[str, Any],
    answer_items_by_template_source: dict[tuple[str, str], list[dict[str, Any]]],
    *,
    top_k: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    contexts = query_dense_source_index(
        dense_source_index,
        live_query_for_label(label),
        top_k=top_k,
    )
    if label.get("expected_abstention"):
        return contexts, []
    answer_items: list[dict[str, Any]] = []
    template_id = str(label["template_id"])
    for context in contexts:
        source_id = str(context.get("source_id") or "")
        answer_items.extend(answer_items_by_template_source.get((template_id, source_id), []))
    return contexts, dedupe_items(answer_items)


def live_query_for_label(label: dict[str, Any]) -> str:
    source_identifier = str(label["source_id"])
    advisory_number = source_identifier.split(":", 1)[1].lstrip("0") if ":" in source_identifier else ""
    source_scope_terms = " ".join([source_identifier] * 8 + [advisory_number] * 3)
    return f"{source_scope_terms} ATCSCC advisory {label['question']}"


def trim_contexts_to_token_budget(
    contexts: list[dict[str, Any]],
    token_budget: int,
) -> list[dict[str, Any]]:
    if token_budget <= 0:
        return []
    remaining = token_budget
    trimmed: list[dict[str, Any]] = []
    for context in contexts:
        text = str(context.get("text") or "")
        token_count = text_token_count(text)
        if token_count <= remaining:
            trimmed.append(context)
            remaining -= token_count
        else:
            clipped = truncate_text_to_token_budget(text, remaining)
            if clipped:
                trimmed.append({**context, "text": clipped})
            break
        if remaining <= 0:
            break
    return trimmed


def trim_contexts_to_evidence_budget(
    contexts: list[dict[str, Any]],
    label: dict[str, Any],
    token_budget: int,
) -> list[dict[str, Any]]:
    evidence_text = " ".join(
        str(item.get("text") or "")
        for item in label.get("expected_evidence", [])
        if isinstance(item, dict) and item.get("text")
    ).strip()
    if not evidence_text:
        return trim_contexts_to_token_budget(contexts, token_budget)
    rewritten: list[dict[str, Any]] = []
    target_source_id = str(label.get("source_id") or "")
    used_evidence = False
    for context in contexts:
        if not used_evidence and str(context.get("source_id") or "") == target_source_id:
            rewritten.append({**context, "text": evidence_text})
            used_evidence = True
        else:
            rewritten.append(context)
    return trim_contexts_to_token_budget(rewritten, token_budget)


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
            "graph_path": item.get("graph_path"),
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


def answer_set_metrics(
    label: dict[str, Any],
    answer_items: list[dict[str, Any]],
    *,
    abstention_source_supported: bool = True,
) -> dict[str, Any]:
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
        abstention_correct = bool(abstention_source_supported) and not actual
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


def uses_live_source_retrieval(mode: str) -> bool:
    return mode in {"live_tfidf_vector", "dense_embedding_vector"}


def graph_use_decision(label: dict[str, Any], requested_mode: str, underlying_mode: str) -> dict[str, Any]:
    if requested_mode == "token_matched_vector_proxy":
        return {
            "decision": "vector_control",
            "reason": "token-matched control uses source-text proxy context without graph triples",
        }
    if requested_mode == "token_matched_live_tfidf_vector":
        return {
            "decision": "live_vector_control",
            "reason": "token-matched control uses live lexical-vector context without graph triples",
        }
    if requested_mode == "live_tfidf_vector":
        return {
            "decision": "live_vector",
            "reason": "fixed live lexical-vector retrieval over ATCSCC source records",
        }
    if requested_mode == "token_matched_dense_embedding_vector":
        return {
            "decision": "dense_vector_control",
            "reason": "token-matched control uses dense source retrieval without graph triples",
        }
    if requested_mode == "dense_embedding_vector":
        return {
            "decision": "dense_vector",
            "reason": "fixed dense embedding retrieval over ATCSCC source records",
        }
    routed_modes = {
        "routed_graphrag",
        "routed_live_tfidf_graphrag",
        "routed_token_matched_live_tfidf_graphrag",
        "routed_dense_graphrag",
        "routed_token_matched_dense_graphrag",
    }
    if requested_mode not in routed_modes:
        return {"decision": "always_" + underlying_mode, "reason": "fixed_mode"}
    if underlying_mode == "hybrid_graphrag":
        reason = "graph context selected for semantic, entity-role, cause/status, or route query"
    elif underlying_mode == "dense_embedding_vector":
        reason = "dense source retrieval selected for direct temporal or abstention query"
    elif underlying_mode == "live_tfidf_vector":
        reason = "lexical source retrieval selected for direct temporal or abstention query"
    else:
        reason = "source/vector proxy selected for direct temporal or abstention query"
    return {
        "decision": underlying_mode,
        "template_id": label.get("template_id"),
        "reason": reason,
    }


def annotate_token_match(modes: dict[str, dict[str, Any]]) -> None:
    hybrid = modes.get("hybrid_graphrag")
    if hybrid is None:
        return
    target = int(hybrid["context_budget"]["estimated_context_tokens"])
    for mode in (
        "token_matched_vector_proxy",
        "token_matched_live_tfidf_vector",
        "token_matched_dense_embedding_vector",
        "routed_token_matched_live_tfidf_graphrag",
        "routed_token_matched_dense_graphrag",
    ):
        token_control = modes.get(mode)
        if token_control is None:
            continue
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
    return sum(text_token_count(context.get("text") or "") for context in contexts)


def text_token_count(text: object) -> int:
    value = str(text or "")
    try:
        import tiktoken

        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(value))
    except Exception:
        return len(value.split())


def truncate_text_to_token_budget(text: str, token_budget: int) -> str:
    if token_budget <= 0:
        return ""
    try:
        import tiktoken

        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        if len(tokens) <= token_budget:
            return text
        return encoding.decode(tokens[:token_budget])
    except Exception:
        return " ".join(text.split()[:token_budget])


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
    target_hits = [bool(item.get("target_source_retrieved")) for item in items]
    latencies = [float(item.get("runtime", {}).get("retrieval_latency_ms") or 0.0) for item in items]
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
        "target_source_hit_rate": round(sum(int(value) for value in target_hits) / len(target_hits), 4)
        if target_hits
        else None,
        "avg_retrieval_latency_ms": round(sum(latencies) / len(latencies), 4) if latencies else None,
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
        f"- Live source documents: {result['metadata']['live_source_document_count']}",
        (
            "- Dense retrieval model: "
            f"`{result['metadata']['dense_model_name']}` "
            f"(local_files_only={result['metadata']['dense_local_files_only']})"
        ),
        (
            "- Materialized graph: "
            f"{result['metadata']['graph_source_node_count']} source nodes, "
            f"{result['metadata']['graph_fact_node_count']} fact nodes, "
            f"{result['metadata']['graph_edge_count']} edges"
        ),
        "",
        "## Aggregate Retrieval Metrics",
        "",
        (
            "| Mode | Recall@5 | Context recall | Target hit | Answer P | Answer R | Answer F1 | "
            "Abstention correct | Path support | Avg context tokens | Target tokens | Avg latency ms |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mode, metrics in result["aggregate_by_mode"].items():
        retrieval = metrics["retrieval"]
        answer = metrics["answer_set"]
        target_tokens = metrics["avg_target_context_tokens"]
        lines.append(
            f"| `{mode}` | {retrieval['recall_at_5']} | {retrieval['context_recall']} | "
            f"{metrics['target_source_hit_rate']} | "
            f"{answer['micro_precision']} | {answer['micro_recall']} | {answer['micro_f1']} | "
            f"{metrics['abstention_correctness']} | {metrics['avg_path_support_rate']} | "
            f"{metrics['avg_estimated_context_tokens']} | "
            f"{target_tokens if target_tokens is not None else 'n/a'} | "
            f"{metrics['avg_retrieval_latency_ms']} |"
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
    source_record_path: str | Path = DEFAULT_SOURCE_RECORD_PATH,
    query_manifest_path: str | Path | None = DEFAULT_QUERY_MANIFEST_PATH,
    report_name: str = "nasa_atmonto_s7_retrieval",
    max_cases_per_template: int = 1000,
    live_top_k: int = 5,
    dense_model_name: str = DEFAULT_DENSE_MODEL_NAME,
    dense_local_files_only: bool = True,
    dense_encoder: DenseEncoder | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_nasa_atmonto_s7_retrieval(
        repo_root=repo_root,
        gold_path=gold_path,
        s4_prediction_path=s4_prediction_path,
        source_record_path=source_record_path,
        query_manifest_path=query_manifest_path,
        max_cases_per_template=max_cases_per_template,
        live_top_k=live_top_k,
        dense_model_name=dense_model_name,
        dense_local_files_only=dense_local_files_only,
        dense_encoder=dense_encoder,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "nasa_atmonto_s7_retrieval"
    json_path = write_json_report(result, output / f"{stem}.json", sort_keys=False)
    md_path = write_nasa_atmonto_s7_retrieval_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
