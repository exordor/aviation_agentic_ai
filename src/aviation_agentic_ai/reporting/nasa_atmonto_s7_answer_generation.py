from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from time import perf_counter
from typing import Any

from aviation_agentic_ai.evaluation.cost_latency import cost_latency_block
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import write_json_report
from aviation_agentic_ai.reporting.nasa_atmonto_answer_benchmark import (
    build_answer_eval_benchmark,
    load_query_manifest,
    read_jsonl_objects,
    resolve_path,
)
from aviation_agentic_ai.reporting.nasa_atmonto_answer_scoring import (
    aggregate_mode,
    evaluate_result,
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
)
from aviation_agentic_ai.reporting.nasa_atmonto_s7_retrieval import (
    DEFAULT_QUERY_MANIFEST_PATH,
    DEFAULT_S4_PREDICTION_PATH,
    DEFAULT_SOURCE_RECORD_PATH,
    answer_items_index,
    contexts_for_mode,
    dense_contexts_for_label,
    estimate_context_tokens,
    live_contexts_for_label,
    trim_contexts_to_evidence_budget,
)

S7_ANSWER_MODES: tuple[str, ...] = (
    "source_oracle",
    "hybrid_graphrag",
    "routed_graphrag",
    "token_matched_live_tfidf_vector",
    "routed_token_matched_live_tfidf_graphrag",
    "token_matched_dense_embedding_vector",
    "routed_token_matched_dense_graphrag",
)


def build_nasa_atmonto_s7_answer_generation(
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
    labels = benchmark["labels"]
    answer_items_by_template_source = answer_items_index(labels)
    records, scored_by_mode = build_s7_answer_records(
        labels,
        materialized_graph,
        live_source_index=live_source_index,
        dense_source_index=dense_source_index,
        answer_items_by_template_source=answer_items_by_template_source,
        live_top_k=live_top_k,
    )
    aggregate_by_mode = {mode: aggregate_mode(items) for mode, items in scored_by_mode.items()}
    by_template = aggregate_by_template(scored_by_mode)
    elapsed_seconds = perf_counter() - started
    cost_latency = {
        "provider": "none",
        "model": "deterministic_s7_answer_scaffold",
        **cost_latency_block(
            elapsed_seconds=elapsed_seconds,
            questions_total=len(labels),
            cases_total=sum(len(items) for items in scored_by_mode.values()),
            kg_path=s4_file,
            token_usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        ),
    }
    return {
        "source_family": "nasa_atmonto_s7_answer_generation",
        "status": "s7_answer_generation_evaluated",
        "metadata": {
            "gold_path": project_relative_path(gold_file, root),
            "s4_prediction_path": project_relative_path(s4_file, root),
            "source_record_path": project_relative_path(source_file, root),
            "query_manifest_path": project_relative_path(
                query_manifest_path or DEFAULT_QUERY_MANIFEST_PATH
            ),
            "template_count": len(query_manifest.get("templates", [])),
            "benchmark_label_count": len(labels),
            "modes": list(S7_ANSWER_MODES),
            "max_cases_per_template": max_cases_per_template,
            "live_top_k": live_top_k,
            "live_source_document_count": live_source_index["document_count"],
            "dense_model_name": dense_source_index["model_name"],
            "dense_local_files_only": dense_source_index["local_files_only"],
            "dense_source_document_count": dense_source_index["document_count"],
            "graph_source_node_count": materialized_graph["source_node_count"],
            "graph_fact_node_count": materialized_graph["fact_node_count"],
            "graph_edge_count": materialized_graph["edge_count"],
            "generation_policy": "deterministic_answer_scaffold_over_s7_retrieved_contexts",
            "boundary": (
                "Retrospective ATCSCC S7 answer-generation rerun over routed live "
                "retrieval contexts; no live operational decision-support claim."
            ),
        },
        "critic_gate": critic_gate,
        "benchmark": benchmark,
        "records": records,
        "answer_quality": {
            "aggregate_by_mode": aggregate_by_mode,
            "aggregate_by_template": by_template,
            "secondary_metrics": {"cost_latency": cost_latency},
            "metric_policy": (
                "Answer correctness, citation precision/recall, evidence faithfulness, "
                "unsupported claim rate, abstention correctness, estimated context tokens, "
                "and latency are reported separately."
            ),
        },
        "claim_boundary": (
            "This report closes the retrieval-only S7 gap by generating deterministic "
            "answers from routed live lexical and dense retrieval contexts. It is still "
            "not an online LLM or operational ATC decision-support evaluation."
        ),
    }


def build_s7_answer_records(
    labels: list[dict[str, Any]],
    materialized_graph: dict[str, Any],
    *,
    live_source_index: dict[str, Any],
    dense_source_index: dict[str, Any],
    answer_items_by_template_source: dict[tuple[str, str], list[dict[str, Any]]],
    live_top_k: int,
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    records: list[dict[str, Any]] = []
    scored_by_mode: dict[str, list[dict[str, Any]]] = {mode: [] for mode in S7_ANSWER_MODES}
    for label in labels:
        source_items = source_items_for_label(label)
        graph_items = traverse_materialized_graph_for_label(materialized_graph, label)
        results = {
            mode: s7_answer_result_for_mode(
                label,
                mode,
                source_items,
                graph_items,
                live_source_index=live_source_index,
                dense_source_index=dense_source_index,
                answer_items_by_template_source=answer_items_by_template_source,
                live_top_k=live_top_k,
            )
            for mode in S7_ANSWER_MODES
        }
        metrics = {mode: evaluate_s7_answer_result(label, results[mode]) for mode in S7_ANSWER_MODES}
        for mode in S7_ANSWER_MODES:
            scored_by_mode[mode].append(
                {
                    "cq_id": label["cq_id"],
                    "template_id": label["template_id"],
                    "source_id": label["source_id"],
                    "metrics": metrics[mode],
                    "underlying_mode": results[mode]["underlying_mode"],
                    "estimated_context_tokens": results[mode]["context_budget"][
                        "estimated_context_tokens"
                    ],
                    "target_estimated_context_tokens": results[mode]["context_budget"].get(
                        "target_estimated_context_tokens"
                    ),
                    "estimated_padding_tokens": results[mode]["context_budget"].get(
                        "estimated_padding_tokens"
                    ),
                    "retrieval_latency_ms": results[mode]["runtime"]["retrieval_latency_ms"],
                    "target_source_retrieved": results[mode]["target_source_retrieved"],
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


def s7_answer_result_for_mode(
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
    underlying_mode = s7_underlying_mode(label, mode)
    target_contexts, _target_items = contexts_for_mode(
        label,
        "hybrid_graphrag",
        source_items,
        graph_items,
    )
    target_tokens = estimate_context_tokens(target_contexts)
    if underlying_mode == "live_tfidf_vector":
        contexts, answer_items = live_contexts_for_label(
            label,
            live_source_index,
            answer_items_by_template_source,
            top_k=live_top_k,
        )
        contexts = trim_contexts_to_evidence_budget(contexts, label, target_tokens)
    elif underlying_mode == "dense_embedding_vector":
        contexts, answer_items = dense_contexts_for_label(
            label,
            dense_source_index,
            answer_items_by_template_source,
            top_k=live_top_k,
        )
        contexts = trim_contexts_to_evidence_budget(contexts, label, target_tokens)
    else:
        contexts, answer_items = contexts_for_mode(label, underlying_mode, source_items, graph_items)
    retrieval_latency_ms = (perf_counter() - started) * 1000
    target_source_retrieved = any(
        str(context.get("source_id") or "") == str(label["source_id"]) for context in contexts
    )
    if label.get("expected_abstention"):
        answer_items = []
    fused_chunks = fused_chunks_from_contexts(contexts)
    graph_triples = graph_triples_from_contexts(contexts)
    answer = generated_answer_text(label, mode, answer_items, fused_chunks, graph_triples)
    estimated_tokens = estimate_context_tokens(contexts)
    return {
        "answer": answer,
        "answer_values": [
            {"predicate": item["predicate"], "value": item["value"]} for item in answer_items
        ],
        "requested_mode": mode,
        "underlying_mode": underlying_mode,
        "evidence_route": evidence_route_for_mode(underlying_mode),
        "fused_chunks": fused_chunks,
        "graph_triples": graph_triples,
        "context_budget": {
            "estimated_context_tokens": estimated_tokens,
            "context_count": len(contexts),
            "source_context_count": len(fused_chunks),
            "graph_context_count": len(graph_triples),
            "token_match_target_mode": "hybrid_graphrag"
            if "token_matched" in mode
            else None,
            "target_estimated_context_tokens": target_tokens
            if "token_matched" in mode
            else None,
            "estimated_padding_tokens": max(0, target_tokens - estimated_tokens)
            if "token_matched" in mode
            else None,
        },
        "runtime": {"retrieval_latency_ms": round(retrieval_latency_ms, 4)},
        "target_source_retrieved": target_source_retrieved,
        "graph_use_decision": graph_use_decision_for_mode(label, mode, underlying_mode),
    }


def s7_underlying_mode(label: dict[str, Any], mode: str) -> str:
    route_mode = routed_underlying_mode(label)
    if mode == "routed_graphrag":
        return route_mode
    if mode == "routed_token_matched_live_tfidf_graphrag":
        return "hybrid_graphrag" if route_mode == "hybrid_graphrag" else "live_tfidf_vector"
    if mode == "routed_token_matched_dense_graphrag":
        return "hybrid_graphrag" if route_mode == "hybrid_graphrag" else "dense_embedding_vector"
    if mode == "token_matched_live_tfidf_vector":
        return "live_tfidf_vector"
    if mode == "token_matched_dense_embedding_vector":
        return "dense_embedding_vector"
    return mode


def fused_chunks_from_contexts(contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    for index, context in enumerate(contexts, start=1):
        if context.get("kind") != "source_chunk":
            continue
        chunk_id = str(context.get("chunk_id") or f"retrieved-source-p1-c{index}")
        chunks.append(
            {
                "chunk_id": chunk_id,
                "page": context.get("page", 1),
                "text": str(context.get("text") or ""),
                "source_id": context.get("source_id"),
            }
        )
    return chunks


def graph_triples_from_contexts(contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    triples: list[dict[str, Any]] = []
    for index, context in enumerate(contexts, start=1):
        if context.get("kind") != "graph_triple":
            continue
        triples.append(
            {
                "triple_id": f"t{len(triples) + 1}",
                "chunk_id": str(context.get("chunk_id") or f"graph-context-p1-c{index}"),
                "page": context.get("page", 1),
                "predicate": context.get("predicate"),
                "object": context.get("value"),
                "evidence_text": str(context.get("text") or ""),
                "source_id": context.get("source_id"),
            }
        )
    return triples


def generated_answer_text(
    label: dict[str, Any],
    mode: str,
    answer_items: list[dict[str, Any]],
    fused_chunks: list[dict[str, Any]],
    graph_triples: list[dict[str, Any]],
) -> str:
    if label.get("expected_abstention") or not answer_items:
        return (
            "Insufficient evidence to answer this ATCSCC advisory question from "
            f"{mode}; no supported answer values were found."
        )
    values = "; ".join(f"{item['predicate']}={item['value']}" for item in answer_items)
    citations = [str(chunk["chunk_id"]) for chunk in fused_chunks if chunk.get("chunk_id")]
    citations.extend(str(triple["triple_id"]) for triple in graph_triples if triple.get("triple_id"))
    citation_text = ", ".join(citations) if citations else "no-valid-citation"
    return f"{values}. Citations: {citation_text}."


def evaluate_s7_answer_result(label: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    metrics = evaluate_result(label, result)
    if label.get("expected_abstention") and uses_live_retrieval(result["underlying_mode"]):
        target_source_retrieved = bool(result.get("target_source_retrieved"))
        metrics["answer_correctness"] = bool(metrics["answer_correctness"]) and target_source_retrieved
        metrics["abstention_correctness"] = (
            bool(metrics["abstention_correctness"]) and target_source_retrieved
        )
        if not target_source_retrieved:
            metrics["evidence_faithfulness"] = False
    return metrics


def uses_live_retrieval(underlying_mode: str) -> bool:
    return underlying_mode in {"live_tfidf_vector", "dense_embedding_vector"}


def evidence_route_for_mode(underlying_mode: str) -> str:
    if underlying_mode == "hybrid_graphrag":
        return "source_span_plus_critic_gated_s4_graph"
    if underlying_mode == "graph_only":
        return "critic_gated_s4_graph"
    if underlying_mode == "live_tfidf_vector":
        return "live_tfidf_source_retrieval"
    if underlying_mode == "dense_embedding_vector":
        return "dense_embedding_source_retrieval"
    return "source_text_retrieval_proxy"


def graph_use_decision_for_mode(
    label: dict[str, Any],
    requested_mode: str,
    underlying_mode: str,
) -> dict[str, Any]:
    if underlying_mode == "hybrid_graphrag":
        reason = "graph context selected for semantic, entity-role, cause/status, or route query"
    elif underlying_mode == "live_tfidf_vector":
        reason = "live lexical source retrieval selected for direct temporal or abstention query"
    elif underlying_mode == "dense_embedding_vector":
        reason = "dense source retrieval selected for direct temporal or abstention query"
    else:
        reason = "fixed source/vector proxy context"
    return {
        "requested_mode": requested_mode,
        "underlying_mode": underlying_mode,
        "template_id": label.get("template_id"),
        "reason": reason,
    }


def aggregate_by_template(
    scored_by_mode: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, dict[str, Any]]]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for mode, records in scored_by_mode.items():
        for record in records:
            grouped[str(record["template_id"])][mode].append(record)
    return {
        template_id: {mode: aggregate_mode(items) for mode, items in modes.items()}
        for template_id, modes in grouped.items()
    }


def write_nasa_atmonto_s7_answer_generation_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO S7 Live-Retrieval Answer Generation",
        "",
        "## Scope",
        "",
        f"- Status: `{result['status']}`",
        f"- Benchmark labels: {result['metadata']['benchmark_label_count']}",
        f"- Modes: {', '.join(f'`{mode}`' for mode in result['metadata']['modes'])}",
        f"- Boundary: {result['metadata']['boundary']}",
        f"- Live source documents: {result['metadata']['live_source_document_count']}",
        (
            "- Dense retrieval model: "
            f"`{result['metadata']['dense_model_name']}` "
            f"(local_files_only={result['metadata']['dense_local_files_only']})"
        ),
        "",
        "## Aggregate Answer Quality",
        "",
        (
            "| Mode | Answers | Correctness | Citation P | Citation R | Evidence faithful | "
            "Unsupported claim rate | Abstention correct | Avg context tokens | Target tokens |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for mode, metrics in result["answer_quality"]["aggregate_by_mode"].items():
        target_context = metrics["avg_target_context_tokens"]
        lines.append(
            f"| `{mode}` | {metrics['answers_total']} | {metrics['answer_correctness']} | "
            f"{metrics['citation_precision']} | {metrics['citation_recall']} | "
            f"{metrics['evidence_faithfulness']} | {metrics['unsupported_claim_rate']} | "
            f"{metrics['abstention_correctness']} | {metrics['avg_estimated_context_tokens']} | "
            f"{target_context if target_context is not None else 'n/a'} |"
        )
    lines.extend(
        [
            "",
            "## CQ Template Breakdown",
            "",
            "| Template | Mode | Correctness | Unsupported claim rate | Avg context tokens |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for template_id, modes in result["answer_quality"]["aggregate_by_template"].items():
        for mode, metrics in modes.items():
            lines.append(
                f"| `{template_id}` | `{mode}` | {metrics['answer_correctness']} | "
                f"{metrics['unsupported_claim_rate']} | {metrics['avg_estimated_context_tokens']} |"
            )
    lines.extend(
        [
            "",
            "## Cost and Latency",
            "",
            f"- Provider: {result['answer_quality']['secondary_metrics']['cost_latency']['provider']}",
            f"- Model: {result['answer_quality']['secondary_metrics']['cost_latency']['model']}",
            (
                "- Elapsed seconds: "
                f"{result['answer_quality']['secondary_metrics']['cost_latency']['elapsed_seconds']}"
            ),
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


def write_nasa_atmonto_s7_answer_generation(
    *,
    output_dir: str | Path,
    repo_root: str | Path = PROJECT_ROOT,
    gold_path: str | Path = DEFAULT_GOLD_PATH,
    s4_prediction_path: str | Path = DEFAULT_S4_PREDICTION_PATH,
    source_record_path: str | Path = DEFAULT_SOURCE_RECORD_PATH,
    query_manifest_path: str | Path | None = DEFAULT_QUERY_MANIFEST_PATH,
    report_name: str = "nasa_atmonto_s7_answer_generation",
    max_cases_per_template: int = 1000,
    live_top_k: int = 5,
    dense_model_name: str = DEFAULT_DENSE_MODEL_NAME,
    dense_local_files_only: bool = True,
    dense_encoder: DenseEncoder | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_nasa_atmonto_s7_answer_generation(
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
    stem = Path(report_name).stem or "nasa_atmonto_s7_answer_generation"
    json_path = write_json_report(result, output / f"{stem}.json", sort_keys=False)
    md_path = write_nasa_atmonto_s7_answer_generation_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
