from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from statistics import mean
from time import perf_counter
from typing import Any, Callable

from aviation_agentic_ai.chunking.chunks import (
    BENCHMARK_V2_CHUNKING_STRATEGIES,
    CHUNKING_STRATEGIES,
    DEFAULT_SEMANTIC_EMBEDDING_MODEL,
    PILOT_CHUNKING_STRATEGIES,
    SourceChunk,
    build_chunk_file,
    chunking_profile,
    chunking_profiles,
    chunk_output_path_for_strategy,
    collection_name_for_strategy,
    read_chunks_jsonl,
)
from aviation_agentic_ai.evaluation.bootstrap_ci import bootstrap_metric_ci
from aviation_agentic_ai.evaluation.cost_latency import artifact_size_bytes
from aviation_agentic_ai.evaluation.document_metadata import document_metadata_from_pdf
from aviation_agentic_ai.evaluation.gold import (
    GoldLabel,
    gold_labels_for_questions,
    load_boundary_questions,
    load_gold_labels,
)
from aviation_agentic_ai.evaluation.metrics import (
    aggregate_retrieval_metrics,
    retrieval_metrics as _retrieval_metrics,
)
from aviation_agentic_ai.evaluation.protocol import (
    build_run_manifest,
    embedding_metadata,
)
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.retrieval.indexing import (
    DEFAULT_COLLECTION_NAME,
    build_chroma_index,
    query_chroma_index,
)


Retriever = Callable[[str, str | Path, str, int], list[dict[str, Any]]]
IndexBuilder = Callable[..., dict[str, Any]]

FAILURE_TYPES = (
    "missed_gold_evidence_at_5",
    "chunk_too_small_lost_context",
    "chunk_too_large_low_precision",
    "section_boundary_split",
    "semantic_boundary_error",
    "cross_page_evidence_split",
    "no_answer_retrieved_misleading_context",
    "proposition_context_loss",
    "parent_child_not_used",
)

TOPK_SENSITIVITY_VALUES = (3, 5, 10, 20)
DEFAULT_CONTEXT_BUDGET_CHARS = 4000


def retrieval_metrics(
    hits: list[dict[str, Any]],
    gold: Any | None = None,
    top_k: int = 5,
    source_page: int | None = None,
) -> dict[str, Any]:
    """Backward-compatible wrapper for page/chunk/span retrieval metrics."""
    return _retrieval_metrics(hits, gold if gold is not None else int(source_page or 0), top_k)


def _percentile(values: list[int], percentile: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((len(ordered) - 1) * percentile)))
    return ordered[index]


def _preserves_boundary(chunk: SourceChunk) -> bool:
    stripped = chunk.text.rstrip()
    return bool(stripped.endswith((".", "!", "?", ";", ":")) or chunk.section)


def _overlap_redundancy(chunks: list[SourceChunk]) -> float:
    total_chars = sum(max(0, chunk.char_end - chunk.char_start) for chunk in chunks)
    if not total_chars:
        return 0.0
    overlap_chars = 0
    by_page: dict[tuple[str, int], list[SourceChunk]] = {}
    for chunk in chunks:
        by_page.setdefault((chunk.source_document, chunk.page), []).append(chunk)
    for page_chunks in by_page.values():
        ordered = sorted(page_chunks, key=lambda item: (item.char_start, item.char_end))
        for left, right in zip(ordered, ordered[1:]):
            overlap_chars += max(0, min(left.char_end, right.char_end) - max(left.char_start, right.char_start))
    return round(overlap_chars / total_chars, 4)


def chunk_stats(chunks: list[SourceChunk]) -> dict[str, Any]:
    lengths = [len(chunk.text) for chunk in chunks]
    token_lengths = [chunk.token_count or len(chunk.text.split()) for chunk in chunks]
    return {
        "chunk_count": len(chunks),
        "chunks_total": len(chunks),
        "avg_chars": round(mean(lengths), 2) if lengths else 0.0,
        "p95_chars": _percentile(lengths, 0.95),
        "avg_tokens": round(mean(token_lengths), 2) if token_lengths else 0.0,
        "overlap_redundancy": _overlap_redundancy(chunks),
        "boundary_preservation_rate": round(
            sum(1 for chunk in chunks if _preserves_boundary(chunk)) / len(chunks), 4
        )
        if chunks
        else 0.0,
    }


def _aggregate(records: list[dict[str, Any]], chunks: list[SourceChunk]) -> dict[str, Any]:
    return {
        "chunking": chunk_stats(chunks),
        "retrieval": aggregate_retrieval_metrics(
            [record["metrics"]["retrieval"] for record in records]
        ),
    }


def _strategy_tradeoff(strategy: str) -> str:
    return {
        "fixed_window": "Controllable baseline, but it can cut through semantic boundaries.",
        "sentence_recursive": "Reduces mid-sentence cuts while keeping chunk sizes predictable.",
        "structure_aware": "Better preserves handbook section and list boundaries.",
        "semantic_meta_like": (
            "Approximates semantic boundary detection; more context-aware but less deterministic "
            "than rule-only strategies."
        ),
    }.get(strategy, "")


def _strategy_recommendation(strategy: str) -> str:
    return {
        "fixed_window": "Use as a stable baseline and regression check.",
        "sentence_recursive": "Use when sentence integrity matters more than strict size regularity.",
        "structure_aware": "Prefer for handbook chapters with headings, lists, and page-local sections.",
        "semantic_meta_like": (
            "Use for exploratory retrieval runs where semantic boundary quality is worth extra "
            "complexity."
        ),
    }.get(strategy, "")


def _strategy_explanation(
    strategy: str,
    aggregate: dict[str, Any],
    best_recall: float,
    best_mrr: float,
) -> str:
    retrieval = aggregate["retrieval"]
    chunking = aggregate["chunking"]
    parts = [_strategy_tradeoff(strategy)]
    if retrieval["recall_at_5"] >= best_recall:
        parts.append("It ties for the best source-page Recall@5 in this run.")
    elif best_recall - retrieval["recall_at_5"] >= 0.2:
        parts.append("Its lower Recall@5 suggests relevant pages are often missed.")
    if retrieval["mrr_at_5"] >= best_mrr:
        parts.append("It places relevant evidence near the top of the result list.")
    if retrieval["context_precision_at_5"] < 0.3 and retrieval["recall_at_5"] > 0:
        parts.append("It retrieves some relevant evidence but with noisy top-k context.")
    if chunking["boundary_preservation_rate"] >= 0.8:
        parts.append("High boundary preservation indicates fewer semantic or structural cuts.")
    if chunking["p95_chars"] > 1800:
        parts.append("Large p95 chunk size may increase context cost and dilute retrieval signals.")
    return " ".join(parts)


def build_chunking_comparison(
    pdf_path: str | Path,
    boundary_cq_path: str | Path,
    base_chunks_path: str | Path,
    index_dir: str | Path,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    strategies: tuple[str, ...] = PILOT_CHUNKING_STRATEGIES,
    max_chars: int = 1200,
    overlap_chars: int = 150,
    vector_top_k: int = 5,
    max_questions: int | None = None,
    rebuild_chunks: bool = True,
    rebuild_indexes: bool = True,
    gold_labels_path: str | Path | None = None,
    command: str = "aviation-ai report chunking-comparison",
    index_builder: IndexBuilder = build_chroma_index,
    retriever: Retriever = query_chroma_index,
) -> dict[str, Any]:
    questions = load_boundary_questions(boundary_cq_path)
    if max_questions is not None:
        questions = questions[:max_questions]
    gold_labels = gold_labels_for_questions(questions, gold_labels_path)

    strategy_results: dict[str, Any] = {}
    strategy_collections: list[str] = []
    for strategy in strategies:
        chunks_path = chunk_output_path_for_strategy(base_chunks_path, strategy)
        if rebuild_chunks or not chunks_path.exists():
            _, chunks = build_chunk_file(
                pdf_path,
                chunks_path,
                max_chars=max_chars,
                overlap_chars=overlap_chars,
                strategy=strategy,
            )
        else:
            chunks = read_chunks_jsonl(chunks_path)

        strategy_collection = collection_name_for_strategy(collection_name, strategy)
        strategy_collections.append(strategy_collection)
        if rebuild_indexes:
            index_builder(
                chunks_path,
                index_dir,
                collection_name=strategy_collection,
                reset=True,
            )

        records: list[dict[str, Any]] = []
        for cq in questions:
            hits = retriever(
                cq["competency_question"],
                index_dir,
                strategy_collection,
                vector_top_k,
            )
            gold_label = gold_labels[str(cq["id"])]
            metrics = retrieval_metrics(hits, gold_label, top_k=vector_top_k)
            records.append(
                {
                    "cq_id": cq["id"],
                    "question": cq["competency_question"],
                    "source_page": cq["source_page"],
                    "gold": gold_label.to_dict(),
                    "hits": hits,
                    "metrics": {"retrieval": metrics},
                }
            )

        strategy_results[strategy] = {
            "chunks_path": project_relative_path(chunks_path),
            "collection_name": strategy_collection,
            "aggregate": _aggregate(records, chunks),
            "tradeoff": _strategy_tradeoff(strategy),
            "recommendation": _strategy_recommendation(strategy),
            "records": records,
        }

    best_recall = max(
        (result["aggregate"]["retrieval"]["recall_at_5"] for result in strategy_results.values()),
        default=0.0,
    )
    best_mrr = max(
        (result["aggregate"]["retrieval"]["mrr_at_5"] for result in strategy_results.values()),
        default=0.0,
    )
    for strategy, strategy_result in strategy_results.items():
        strategy_result["explanation"] = _strategy_explanation(
            strategy,
            strategy_result["aggregate"],
            best_recall,
            best_mrr,
        )

    ranking = sorted(
        (
            {
                "strategy": strategy,
                "recall_at_5": result["aggregate"]["retrieval"]["recall_at_5"],
                "mrr_at_5": result["aggregate"]["retrieval"]["mrr_at_5"],
                "context_precision_at_5": result["aggregate"]["retrieval"][
                    "context_precision_at_5"
                ],
            }
            for strategy, result in strategy_results.items()
        ),
        key=lambda item: (
            -item["recall_at_5"],
            -item["mrr_at_5"],
            -item["context_precision_at_5"],
            item["strategy"],
        ),
    )
    run_manifest = build_run_manifest(
        "chunking_comparison",
        parameters={
            "strategies": list(strategies),
            "max_chars": max_chars,
            "overlap_chars": overlap_chars,
            "vector_top_k": vector_top_k,
            "max_questions": max_questions,
            "gold_labels_path": project_relative_path(gold_labels_path)
            if gold_labels_path is not None
            else None,
        },
        artifacts={
            "pdf_path": pdf_path,
            "boundary_cq_path": boundary_cq_path,
            "base_chunks_path": base_chunks_path,
            "index_dir": index_dir,
        },
        rebuild_policy={"chunks": rebuild_chunks, "indexes": rebuild_indexes, "kg": False},
        collection_name=collection_name,
        chunking_strategy="multiple",
        command=command,
        document=document_metadata_from_pdf(pdf_path).to_dict(),
        llm={"provider": "none", "model": "not_used"},
        embedding=embedding_metadata(
            index_dir,
            collection_name,
            collections=strategy_collections,
        ),
    )
    return {
        "metadata": {
            "run_manifest": run_manifest,
            "pdf_path": project_relative_path(pdf_path),
            "boundary_cq_path": project_relative_path(boundary_cq_path),
            "gold_labels_path": project_relative_path(gold_labels_path)
            if gold_labels_path is not None
            else None,
            "index_dir": project_relative_path(index_dir),
            "collection_name": collection_name,
            "strategy_collections": strategy_collections,
            "rebuild_chunks": rebuild_chunks,
            "rebuild_indexes": rebuild_indexes,
            "vector_top_k": vector_top_k,
            "max_chars": max_chars,
            "overlap_chars": overlap_chars,
            "questions_total": len(questions),
        },
        "ranking": ranking,
        "strategies": strategy_results,
    }


def write_chunking_comparison_json(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_chunking_comparison_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Chunking Comparison",
        "",
        f"- Run ID: `{result['metadata']['run_manifest']['run_id']}`",
        f"- Questions: {result['metadata']['questions_total']}",
        f"- Vector top k: {result['metadata']['vector_top_k']}",
        f"- Target chars: {result['metadata']['max_chars']}",
        f"- Overlap chars: {result['metadata']['overlap_chars']}",
        f"- Rebuild chunks: {result['metadata']['rebuild_chunks']}",
        f"- Rebuild indexes: {result['metadata']['rebuild_indexes']}",
        "",
        "## Ranking",
        "",
        "| Rank | Strategy | Recall@5 | MRR@5 | Context Precision@5 |",
        "| ---: | --- | ---: | ---: | ---: |",
    ]
    for rank, item in enumerate(result["ranking"], start=1):
        lines.append(
            f"| {rank} | {item['strategy']} | {item['recall_at_5']} | "
            f"{item['mrr_at_5']} | {item['context_precision_at_5']} |"
        )

    lines.extend(
        [
            "",
            "## Strategy Details",
            "",
            "| Strategy | Chunks | Avg chars | P95 chars | Boundary preservation | Tradeoff | Recommendation |",
            "| --- | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for strategy, strategy_result in result["strategies"].items():
        aggregate = strategy_result["aggregate"]["chunking"]
        lines.append(
            f"| {strategy} | {aggregate['chunk_count']} | {aggregate['avg_chars']} | "
            f"{aggregate['p95_chars']} | {aggregate['boundary_preservation_rate']} | "
            f"{strategy_result['tradeoff']} | {strategy_result['recommendation']} |"
        )
    lines.extend(["", "## Strategy Explanations", ""])
    for strategy, strategy_result in result["strategies"].items():
        retrieval = strategy_result["aggregate"]["retrieval"]
        lines.extend(
            [
                f"### {strategy}",
                "",
                strategy_result["explanation"],
                "",
                (
                    f"- Retrieval: Recall@5={retrieval['recall_at_5']}, "
                    f"MRR@5={retrieval['mrr_at_5']}, "
                    f"Context Precision@5={retrieval['context_precision_at_5']}"
                ),
                f"- Recommendation: {strategy_result['recommendation']}",
                "",
            ]
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_chunking_comparison(
    pdf_path: str | Path,
    boundary_cq_path: str | Path,
    base_chunks_path: str | Path,
    index_dir: str | Path,
    output_dir: str | Path,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    strategies: tuple[str, ...] = PILOT_CHUNKING_STRATEGIES,
    max_chars: int = 1200,
    overlap_chars: int = 150,
    vector_top_k: int = 5,
    max_questions: int | None = None,
    rebuild_chunks: bool = True,
    rebuild_indexes: bool = True,
    gold_labels_path: str | Path | None = None,
    command: str = "aviation-ai report chunking-comparison",
    index_builder: IndexBuilder = build_chroma_index,
    retriever: Retriever = query_chroma_index,
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_chunking_comparison(
        pdf_path,
        boundary_cq_path,
        base_chunks_path,
        index_dir,
        collection_name=collection_name,
        strategies=strategies,
        max_chars=max_chars,
        overlap_chars=overlap_chars,
        vector_top_k=vector_top_k,
        max_questions=max_questions,
        rebuild_chunks=rebuild_chunks,
        rebuild_indexes=rebuild_indexes,
        gold_labels_path=gold_labels_path,
        command=command,
        index_builder=index_builder,
        retriever=retriever,
    )
    output = Path(output_dir)
    json_path = write_chunking_comparison_json(result, output / "chunking_comparison.json")
    md_path = write_chunking_comparison_markdown(result, output / "chunking_comparison.md")
    return json_path, md_path, result


def _percentile_float(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((len(ordered) - 1) * percentile)))
    return round(ordered[index], 4)


def _safe_mean(values: list[float]) -> float:
    return round(mean(values), 4) if values else 0.0


def _label_breakdown(labels: list[GoldLabel]) -> dict[str, Any]:
    no_answer_total = sum(int(label.expected_abstention) for label in labels)
    return {
        "labels_total": len(labels),
        "supported_total": len(labels) - no_answer_total,
        "no_answer_total": no_answer_total,
        "question_type_counts": dict(
            sorted(Counter(label.question_type or "<missing>" for label in labels).items())
        ),
    }


def _retrieval_confidence_intervals(metric_items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "recall_at_5": bootstrap_metric_ci(
            metric_items,
            lambda metric: bool(metric.get("recall_at_5", False)),
        ),
        "recall_at_10": bootstrap_metric_ci(
            metric_items,
            lambda metric: bool(metric.get("recall_at_10", False)),
        ),
        "mrr_at_5": bootstrap_metric_ci(
            metric_items,
            lambda metric: float(metric.get("mrr_at_5", 0.0)),
        ),
        "ndcg_at_10": bootstrap_metric_ci(
            metric_items,
            lambda metric: float(metric.get("ndcg_at_10", 0.0)),
        ),
        "context_recall": bootstrap_metric_ci(
            metric_items,
            lambda metric: float(metric.get("context_recall", 0.0)),
        ),
    }


def _aggregate_retrieval_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    return aggregate_retrieval_metrics([record["metrics"]["retrieval"] for record in records])


def _supported_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        record
        for record in records
        if not bool(record.get("gold", {}).get("expected_abstention", False))
    ]


def _no_answer_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        record
        for record in records
        if bool(record.get("gold", {}).get("expected_abstention", False))
    ]


def _normalize_for_match(text: str) -> str:
    return " ".join(text.lower().split())


def _key_entity_overlap(
    hits: list[dict[str, Any]],
    key_entities: tuple[str, ...],
    *,
    top_k: int = 5,
) -> tuple[bool, list[str]]:
    haystack = _normalize_for_match(" ".join(str(hit.get("text", "")) for hit in hits[:top_k]))
    matched = [
        entity
        for entity in key_entities
        if entity and _normalize_for_match(entity) in haystack
    ]
    return bool(matched), matched


def _no_answer_diagnostics(records: list[dict[str, Any]]) -> dict[str, Any]:
    no_answer = _no_answer_records(records)
    denominator = len(no_answer) or 1
    return {
        "records_total": len(no_answer),
        "retrieved_context_rate_at_5": round(
            sum(int(bool(record.get("hits"))) for record in no_answer) / denominator,
            4,
        ),
        "key_entity_overlap_rate_at_5": round(
            sum(int(record.get("no_answer_diagnostics", {}).get("key_entity_overlap", False))
                for record in no_answer)
            / denominator,
            4,
        ),
        "interpretation": (
            "Insufficient-evidence labels have no gold retrieval target; overlap means retrieved "
            "context may look misleading and is not counted as recall."
        ),
    }


def _category_breakdown(records: list[dict[str, Any]]) -> dict[str, Any]:
    categories = (
        "supported_factual",
        "concept_definition",
        "relation_causal",
        "cross_page",
        "paraphrase",
        "terminology_variation",
        "insufficient_evidence",
    )
    grouped: dict[str, list[dict[str, Any]]] = {category: [] for category in categories}
    for record in records:
        question_type = str(record.get("gold", {}).get("question_type") or "<missing>")
        grouped.setdefault(question_type, []).append(record)
    return {
        category: {
            "labels": len(items),
            "retrieval": _aggregate_retrieval_records(items),
        }
        for category, items in grouped.items()
        if items or category in categories
    }


def _strategy_metadata(chunks: list[SourceChunk]) -> dict[str, Any]:
    metadata_values: dict[str, set[str]] = {}
    for chunk in chunks:
        for key, value in chunk.metadata.items():
            if value in ("", None):
                continue
            metadata_values.setdefault(key, set()).add(str(value))
    return {key: sorted(values) for key, values in sorted(metadata_values.items())}


def _strategy_cost_notes(strategy: str, chunks: list[SourceChunk]) -> str:
    stats = chunk_stats(chunks)
    if strategy == "hierarchical_parent_child":
        return (
            "Child chunks are indexed with parent metadata; full parent-return retrieval is "
            "not claimed in this report."
        )
    if strategy == "proposition_like":
        return "Heuristic proposition-like segmentation may increase chunk count and review cost."
    if strategy == "contextual_prefix":
        return "Deterministic prefixes add metadata tokens to every indexed chunk."
    if strategy.endswith("_small") or stats["avg_chars"] < 600:
        return "Small chunks may improve localization while increasing index size and KG extraction units."
    if strategy.endswith("_large") or stats["p95_chars"] > 1500:
        return "Large chunks may preserve broad context while diluting top-k precision."
    return "Cost impact is interpreted from chunk count, chunk size, index size, and latency."


def _profile_with_observed_metadata(
    strategy: str,
    chunks: list[SourceChunk],
    *,
    max_chars: int = 1200,
    overlap_chars: int = 150,
) -> dict[str, Any]:
    profile = chunking_profile(
        strategy,
        max_chars=max_chars,
        overlap_chars=overlap_chars,
    ).to_dict()
    observed = _strategy_metadata(chunks)
    semantic_backends = observed.get("semantic_backend", [])
    if strategy == "embedding_semantic":
        if semantic_backends == ["fallback_lexical"]:
            profile["real_embeddings"] = False
            profile["semantic_backend"] = "fallback_lexical"
            profile["name_accuracy"] = "fallback_not_true_semantic_for_this_run"
        elif semantic_backends:
            profile["semantic_backend"] = ", ".join(semantic_backends)
            profile["real_embeddings"] = "sentence_transformers" in semantic_backends
    return {
        **profile,
        "observed_metadata": observed,
        "chunks_total": len(chunks),
        "chunk_stats": chunk_stats(chunks),
    }


def build_chunking_implementation_audit(
    pdf_path: str | Path,
    chunks_dir: str | Path,
    *,
    strategies: tuple[str, ...] = CHUNKING_STRATEGIES,
    max_chars: int = 1200,
    overlap_chars: int = 150,
    max_pages: int | None = None,
    rebuild_chunks: bool = True,
    embedding_model: str = DEFAULT_SEMANTIC_EMBEDDING_MODEL,
    semantic_download: bool = True,
    command: str = "aviation-ai report chunking-implementation-audit",
) -> dict[str, Any]:
    chunks_root = Path(chunks_dir)
    rows: list[dict[str, Any]] = []
    for strategy in strategies:
        chunks_path = _chunk_path_for_v2(chunks_root, pdf_path, strategy)
        if rebuild_chunks or not chunks_path.exists():
            _, chunks = build_chunk_file(
                pdf_path,
                chunks_path,
                max_chars=max_chars,
                overlap_chars=overlap_chars,
                max_pages=max_pages,
                strategy=strategy,
                embedding_model=embedding_model,
                semantic_download=semantic_download,
            )
        else:
            chunks = read_chunks_jsonl(chunks_path)
        profile = _profile_with_observed_metadata(
            strategy,
            chunks,
            max_chars=max_chars,
            overlap_chars=overlap_chars,
        )
        rows.append(
            {
                "strategy": strategy,
                "chunks_path": project_relative_path(chunks_path),
                "family": profile["family"],
                "retrieval_unit": profile["retrieval_unit"],
                "returned_context_unit": profile["returned_context_unit"],
                "real_embeddings": profile["real_embeddings"],
                "semantic_backend": profile["semantic_backend"],
                "lexical_fallback": profile["lexical_fallback"],
                "parent_child_retrieval": profile["parent_child_retrieval"],
                "chunk_config": {
                    "max_chars": profile["max_chars"],
                    "overlap_chars": profile["overlap_chars"],
                    "max_tokens_approx": profile["max_tokens"],
                    "overlap_tokens_approx": profile["overlap_tokens"],
                },
                "context_prefix_enabled": profile["context_prefix_enabled"],
                "implementation_status": profile["implementation_status"],
                "limitations": profile["limitations"],
                "name_accuracy": profile["name_accuracy"],
                "observed_metadata": profile["observed_metadata"],
                "chunk_stats": profile["chunk_stats"],
            }
        )
    return {
        "metadata": {
            "run_manifest": build_run_manifest(
                "chunking_implementation_audit",
                parameters={
                    "strategies": list(strategies),
                    "max_chars": max_chars,
                    "overlap_chars": overlap_chars,
                    "max_pages": max_pages,
                    "embedding_model": embedding_model,
                    "semantic_download": semantic_download,
                },
                artifacts={"pdf_path": pdf_path, "chunks_dir": chunks_root},
                rebuild_policy={"chunks": rebuild_chunks, "indexes": False, "kg": False},
                collection_name="not_used",
                chunking_strategy="multiple",
                command=command,
                document=document_metadata_from_pdf(pdf_path).to_dict(),
                llm={"provider": "none", "model": "not_used"},
                embedding={"provider": "not_used_for_retrieval_index"},
            ),
            "pdf_path": project_relative_path(pdf_path),
            "chunks_dir": project_relative_path(chunks_root),
            "strategies_total": len(rows),
            "claim_policy": (
                "Audit describes implemented behavior. Partial methods are not treated "
                "as full semantic, parent-child, or LLM proposition extraction."
            ),
        },
        "strategies": rows,
        "profiles": {
            name: profile.to_dict()
            for name, profile in chunking_profiles(
                strategies,
                max_chars=max_chars,
                overlap_chars=overlap_chars,
            ).items()
        },
    }


def write_chunking_implementation_audit_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_chunking_implementation_audit_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Chunking Implementation Audit",
        "",
        "- This audit records implemented behavior, not aspirational method labels.",
        "- Partial methods remain explicitly marked partial until retrieval returns the claimed context unit.",
        "",
        "| Strategy | Family | Retrieval unit | Returned context | Backend | Parent-child | Status | Name accuracy | Chunks | Avg chars | Limitations |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in result["strategies"]:
        lines.append(
            f"| {row['strategy']} | {row['family']} | {row['retrieval_unit']} | "
            f"{row['returned_context_unit']} | {row['semantic_backend']} | "
            f"{row['parent_child_retrieval']} | {row['implementation_status']} | "
            f"{row['name_accuracy']} | {row['chunk_stats']['chunks_total']} | "
            f"{row['chunk_stats']['avg_chars']} | {'; '.join(row['limitations'])} |"
        )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_chunking_implementation_audit(
    pdf_path: str | Path,
    chunks_dir: str | Path,
    output_dir: str | Path,
    *,
    strategies: tuple[str, ...] = CHUNKING_STRATEGIES,
    max_chars: int = 1200,
    overlap_chars: int = 150,
    max_pages: int | None = None,
    rebuild_chunks: bool = True,
    embedding_model: str = DEFAULT_SEMANTIC_EMBEDDING_MODEL,
    semantic_download: bool = True,
    command: str = "aviation-ai report chunking-implementation-audit",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_chunking_implementation_audit(
        pdf_path,
        chunks_dir,
        strategies=strategies,
        max_chars=max_chars,
        overlap_chars=overlap_chars,
        max_pages=max_pages,
        rebuild_chunks=rebuild_chunks,
        embedding_model=embedding_model,
        semantic_download=semantic_download,
        command=command,
    )
    output = Path(output_dir)
    json_path = write_chunking_implementation_audit_json(
        result,
        output / "chunking_implementation_audit.json",
    )
    md_path = write_chunking_implementation_audit_markdown(
        result,
        output / "chunking_implementation_audit.md",
    )
    return json_path, md_path, result


def _hit_summary_v2(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "chunk_id": str(hit.get("chunk_id", "")),
            "page": hit.get("page"),
            "rank": hit.get("rank"),
            "score": hit.get("score"),
            "source": hit.get("source"),
            "text_excerpt": str(hit.get("text", ""))[:240],
            "metadata": hit.get("metadata", {}),
        }
        for hit in hits
    ]


def _trim_hits_to_context_budget(
    hits: list[dict[str, Any]],
    *,
    context_budget_chars: int,
) -> list[dict[str, Any]]:
    if context_budget_chars <= 0:
        raise ValueError("context_budget_chars must be positive")
    selected: list[dict[str, Any]] = []
    used = 0
    for hit in hits:
        text = str(hit.get("text", ""))
        hit_chars = len(text)
        if selected and used + hit_chars > context_budget_chars:
            break
        if not selected and hit_chars > context_budget_chars:
            clipped = {**hit, "text": text[:context_budget_chars]}
            clipped["metadata"] = {
                **dict(hit.get("metadata", {})),
                "context_budget_truncated": True,
            }
            selected.append(clipped)
            break
        selected.append(hit)
        used += hit_chars
    return selected


def _context_char_count(hits: list[dict[str, Any]]) -> int:
    return sum(len(str(hit.get("text", ""))) for hit in hits)


def _metric_at_k_from_hits(
    hits: list[dict[str, Any]],
    gold: dict[str, Any] | GoldLabel,
    k: int,
) -> dict[str, Any]:
    scoped_hits = hits[:k]
    base = retrieval_metrics(scoped_hits, gold, top_k=k)
    first_rank = base.get("first_relevant_rank")
    matched = base.get("matched_chunk_ids", [])
    return {
        "recall": bool(first_rank and int(first_rank) <= k),
        "precision": round(len(matched) / max(k, 1), 4),
        "mrr": round(1.0 / int(first_rank), 4) if first_rank and int(first_rank) <= k else 0.0,
        "context_recall": base.get("context_recall", 0.0),
        "hits_returned": len(scoped_hits),
        "context_chars": _context_char_count(scoped_hits),
    }


def _metric_at_k_from_record(record: dict[str, Any], k: int) -> dict[str, Any]:
    stored = record.get("top_k_metrics", {}).get(str(k))
    if isinstance(stored, dict):
        return stored
    return _metric_at_k_from_hits(record.get("hits", []), record.get("gold", {}), k)


def _aggregate_metric_at_k(records: list[dict[str, Any]], k: int) -> dict[str, Any]:
    items = [_metric_at_k_from_record(record, k) for record in records]
    denominator = len(items) or 1
    return {
        "n": len(items),
        "recall": round(sum(int(item["recall"]) for item in items) / denominator, 4),
        "precision": round(sum(float(item["precision"]) for item in items) / denominator, 4),
        "mrr": round(sum(float(item["mrr"]) for item in items) / denominator, 4),
        "context_recall": round(
            sum(float(item["context_recall"]) for item in items) / denominator,
            4,
        ),
        "mean_hits_returned": round(
            sum(int(item["hits_returned"]) for item in items) / denominator,
            4,
        ),
        "mean_context_chars": round(
            sum(int(item["context_chars"]) for item in items) / denominator,
            2,
        ),
    }


def _chunk_path_for_v2(chunks_dir: str | Path, pdf_path: str | Path, strategy: str) -> Path:
    return Path(chunks_dir) / f"{Path(pdf_path).stem}.{strategy}.benchmark_v2.jsonl"


def _aggregate_strategy_v2(
    records: list[dict[str, Any]],
    chunks: list[SourceChunk],
    *,
    index_build_seconds: float,
    query_latencies: list[float],
    index_size_bytes: int | None,
) -> dict[str, Any]:
    supported = _supported_records(records)
    supported_metrics = [record["metrics"]["retrieval"] for record in supported]
    return {
        "label_counts": {
            "labels_total": len(records),
            "supported_total": len(supported),
            "no_answer_total": len(records) - len(supported),
        },
        "chunking": chunk_stats(chunks),
        "retrieval_supported_only": _aggregate_retrieval_records(supported),
        "retrieval_all_labels_diagnostic": _aggregate_retrieval_records(records),
        "retrieval_confidence_intervals_supported_only": _retrieval_confidence_intervals(
            supported_metrics
        ),
        "no_answer_diagnostics": _no_answer_diagnostics(records),
        "category_breakdown": _category_breakdown(records),
        "cost_latency": {
            "index_build_seconds": round(index_build_seconds, 4),
            "query_latency_mean_seconds": _safe_mean(query_latencies),
            "query_latency_p95_seconds": _percentile_float(query_latencies, 0.95),
            "index_size_bytes": index_size_bytes,
        },
    }


def build_chunk_size_sensitivity(strategy_results: dict[str, Any]) -> dict[str, Any]:
    families = {
        "fixed": ("fixed_small", "fixed_medium", "fixed_large"),
        "recursive": ("recursive_small", "recursive_medium", "recursive_large"),
    }
    sensitivity: dict[str, Any] = {}
    for family, strategies in families.items():
        rows = []
        for strategy in strategies:
            result = strategy_results.get(strategy)
            if not result:
                continue
            aggregate = result["aggregate"]
            rows.append(
                {
                    "strategy": strategy,
                    "chunks_total": aggregate["chunking"]["chunks_total"],
                    "avg_chars": aggregate["chunking"]["avg_chars"],
                    "p95_chars": aggregate["chunking"]["p95_chars"],
                    "recall_at_5_supported": aggregate["retrieval_supported_only"]["recall_at_5"],
                    "mrr_at_5_supported": aggregate["retrieval_supported_only"]["mrr_at_5"],
                    "context_recall_supported": aggregate["retrieval_supported_only"][
                        "context_recall"
                    ],
                }
            )
        sensitivity[family] = {
            "rows": rows,
            "interpretation": (
                "Small chunks can improve entity/fact localization; large chunks can preserve "
                "broader context but may reduce precision. Definition, causal, and cross-page "
                "questions may prefer different chunk sizes."
            ),
        }
    return sensitivity


def build_chunking_comparison_v2(
    pdf_path: str | Path,
    gold_labels_path: str | Path,
    chunks_dir: str | Path,
    index_dir: str | Path,
    *,
    output_dir: str | Path | None = None,
    collection_prefix: str = "phak_ch4_chunking_v2",
    strategies: tuple[str, ...] = BENCHMARK_V2_CHUNKING_STRATEGIES,
    max_labels: int | None = None,
    rebuild_chunks: bool = True,
    rebuild_indexes: bool = True,
    embedding_model: str = DEFAULT_SEMANTIC_EMBEDDING_MODEL,
    semantic_download: bool = True,
    vector_top_k: int = 10,
    evaluation_mode: str = "top_k",
    context_budget_chars: int = DEFAULT_CONTEXT_BUDGET_CHARS,
    command: str = "aviation-ai report chunking-comparison-v2",
    index_builder: IndexBuilder = build_chroma_index,
    retriever: Retriever = query_chroma_index,
) -> dict[str, Any]:
    if evaluation_mode not in {"top_k", "fixed_context_budget"}:
        raise ValueError(f"Unsupported chunking evaluation mode: {evaluation_mode}")
    started = perf_counter()
    labels = list(load_gold_labels(gold_labels_path).values())
    if max_labels is not None:
        labels = labels[:max_labels]
    label_breakdown = _label_breakdown(labels)
    chunks_root = Path(chunks_dir)
    index_root = Path(index_dir)
    strategy_results: dict[str, Any] = {}
    strategy_collections: list[str] = []

    for strategy in strategies:
        chunks_path = _chunk_path_for_v2(chunks_root, pdf_path, strategy)
        if rebuild_chunks or not chunks_path.exists():
            _, chunks = build_chunk_file(
                pdf_path,
                chunks_path,
                strategy=strategy,
                embedding_model=embedding_model,
                semantic_download=semantic_download,
            )
        else:
            chunks = read_chunks_jsonl(chunks_path)

        strategy_index_dir = index_root / strategy
        collection_name = collection_name_for_strategy(collection_prefix, strategy)
        strategy_collections.append(collection_name)
        index_build_started = perf_counter()
        if rebuild_indexes:
            index_builder(
                chunks_path,
                strategy_index_dir,
                collection_name=collection_name,
                reset=True,
            )
        index_build_seconds = perf_counter() - index_build_started

        records: list[dict[str, Any]] = []
        query_latencies: list[float] = []
        for label in labels:
            query_started = perf_counter()
            retriever_top_k = (
                max(vector_top_k, TOPK_SENSITIVITY_VALUES[-1])
                if evaluation_mode == "fixed_context_budget"
                else vector_top_k
            )
            hits = retriever(
                label.question,
                strategy_index_dir,
                collection_name,
                retriever_top_k,
            )
            query_latencies.append(perf_counter() - query_started)
            scored_hits = (
                _trim_hits_to_context_budget(hits, context_budget_chars=context_budget_chars)
                if evaluation_mode == "fixed_context_budget"
                else hits
            )
            metrics = retrieval_metrics(scored_hits, label, top_k=vector_top_k)
            key_overlap, overlap_entities = _key_entity_overlap(
                scored_hits,
                label.key_entities,
                top_k=5,
            )
            records.append(
                {
                    "cq_id": label.cq_id,
                    "question": label.question,
                    "gold": label.to_dict(),
                    "metrics": {"retrieval": metrics},
                    "top_k_metrics": {
                        str(k): _metric_at_k_from_hits(scored_hits, label, k)
                        for k in TOPK_SENSITIVITY_VALUES
                        if k <= retriever_top_k
                    },
                    "hits": _hit_summary_v2(scored_hits[:vector_top_k]),
                    "context_budget": {
                        "evaluation_mode": evaluation_mode,
                        "context_budget_chars": context_budget_chars
                        if evaluation_mode == "fixed_context_budget"
                        else None,
                        "candidate_hits": len(hits[:retriever_top_k]),
                        "scored_hits": len(scored_hits),
                        "scored_context_chars": _context_char_count(scored_hits),
                    },
                    "no_answer_diagnostics": {
                        "retrieved_context_at_5": bool(scored_hits[:5]),
                        "key_entity_overlap": key_overlap,
                        "overlap_entities": overlap_entities,
                    }
                    if label.expected_abstention
                    else {},
                }
            )

        aggregate = _aggregate_strategy_v2(
            records,
            chunks,
            index_build_seconds=index_build_seconds,
            query_latencies=query_latencies,
            index_size_bytes=artifact_size_bytes(strategy_index_dir),
        )
        strategy_results[strategy] = {
            "chunks_path": project_relative_path(chunks_path),
            "index_dir": project_relative_path(strategy_index_dir),
            "collection_name": collection_name,
            "implementation_metadata": _strategy_metadata(chunks),
            "cost_notes": _strategy_cost_notes(strategy, chunks),
            "aggregate": aggregate,
            "records": records,
        }

    ranking = sorted(
        (
            {
                "strategy": strategy,
                "recall_at_5_supported": result["aggregate"]["retrieval_supported_only"][
                    "recall_at_5"
                ],
                "mrr_at_5_supported": result["aggregate"]["retrieval_supported_only"][
                    "mrr_at_5"
                ],
                "context_precision_at_5_supported": result["aggregate"][
                    "retrieval_supported_only"
                ]["context_precision_at_5"],
                "context_recall_supported": result["aggregate"]["retrieval_supported_only"][
                    "context_recall"
                ],
            }
            for strategy, result in strategy_results.items()
        ),
        key=lambda item: (
            -item["recall_at_5_supported"],
            -item["mrr_at_5_supported"],
            -item["context_recall_supported"],
            item["strategy"],
        ),
    )
    run_manifest = build_run_manifest(
        "chunking_comparison_benchmark_v2",
        parameters={
            "strategies": list(strategies),
            "max_labels": max_labels,
            "vector_top_k": vector_top_k,
            "gold_labels_path": project_relative_path(gold_labels_path),
            "embedding_model": embedding_model,
            "semantic_download": semantic_download,
            "evaluation_mode": evaluation_mode,
            "context_budget_chars": context_budget_chars
            if evaluation_mode == "fixed_context_budget"
            else None,
        },
        artifacts={
            "pdf_path": pdf_path,
            "chunks_dir": chunks_root,
            "index_dir": index_root,
            "output_dir": output_dir,
        },
        rebuild_policy={"chunks": rebuild_chunks, "indexes": rebuild_indexes, "kg": False},
        collection_name=collection_prefix,
        chunking_strategy="benchmark_v2_multiple",
        command=command,
        document=document_metadata_from_pdf(pdf_path).to_dict(),
        llm={"provider": "none", "model": "not_used"},
        embedding=embedding_metadata(index_root, collection_prefix, collections=strategy_collections),
    )
    return {
        "metadata": {
            "run_manifest": run_manifest,
            "pdf_path": project_relative_path(pdf_path),
            "gold_labels_path": project_relative_path(gold_labels_path),
            "chunks_dir": project_relative_path(chunks_root),
            "index_dir": project_relative_path(index_root),
            "collection_prefix": collection_prefix,
            "strategy_collections": strategy_collections,
            "strategies": list(strategies),
            "label_breakdown": label_breakdown,
            "scoring_policy": "layered_metrics_no_mixed_overall_score",
            "primary_retrieval_metrics": "supported_only",
            "all_label_metrics_policy": "diagnostic_only_no_answer_labels_have_no_gold_evidence",
            "evaluation_mode": evaluation_mode,
            "context_budget_chars": context_budget_chars
            if evaluation_mode == "fixed_context_budget"
            else None,
            "claim_limitations": [
                "Do not claim one chunker is universally best.",
                "Insufficient-evidence labels are analyzed separately from supported retrieval.",
                "Proposition-like and hierarchical methods are deterministic scaffolds, not LLM extraction.",
                "Top-k comparisons expose different context budgets when chunk sizes differ.",
            ],
            "elapsed_seconds": round(perf_counter() - started, 4),
        },
        "ranking": ranking,
        "chunk_size_sensitivity": build_chunk_size_sensitivity(strategy_results),
        "strategies": strategy_results,
    }


def _sample_failure_record(
    records: list[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
) -> list[dict[str, Any]]:
    for record in records:
        if predicate(record):
            return [
                {
                    "cq_id": record["cq_id"],
                    "question_type": record.get("gold", {}).get("question_type", ""),
                    "question": record["question"],
                    "expected_abstention": record.get("gold", {}).get("expected_abstention", False),
                    "metrics": record["metrics"]["retrieval"],
                    "top_hits": record["hits"][:3],
                    "no_answer_diagnostics": record.get("no_answer_diagnostics", {}),
                }
            ]
    return []


def _failure_samples_for_strategy(strategy: str, strategy_result: dict[str, Any]) -> dict[str, Any]:
    records = strategy_result["records"]
    chunking = strategy_result["aggregate"]["chunking"]

    def supported(record: dict[str, Any]) -> bool:
        return not bool(record.get("gold", {}).get("expected_abstention", False))

    def missed_at_5(record: dict[str, Any]) -> bool:
        return supported(record) and not bool(record["metrics"]["retrieval"].get("recall_at_5"))

    def low_context(record: dict[str, Any]) -> bool:
        return supported(record) and float(record["metrics"]["retrieval"].get("context_recall", 0.0)) < 1.0

    cards = {
        "missed_gold_evidence_at_5": _sample_failure_record(records, missed_at_5),
        "chunk_too_small_lost_context": _sample_failure_record(
            records,
            lambda record: chunking["avg_chars"] < 650 and low_context(record),
        ),
        "chunk_too_large_low_precision": _sample_failure_record(
            records,
            lambda record: chunking["p95_chars"] > 1200
            and supported(record)
            and float(record["metrics"]["retrieval"].get("precision_at_5", 0.0)) <= 0.2,
        ),
        "section_boundary_split": _sample_failure_record(
            records,
            lambda record: missed_at_5(record)
            and strategy
            in {
                "fixed_small",
                "fixed_medium",
                "fixed_large",
                "recursive_small",
                "recursive_medium",
                "recursive_large",
            },
        ),
        "semantic_boundary_error": _sample_failure_record(
            records,
            lambda record: strategy in {"semantic_meta_like", "embedding_semantic"}
            and missed_at_5(record),
        ),
        "cross_page_evidence_split": _sample_failure_record(
            records,
            lambda record: record.get("gold", {}).get("question_type") == "cross_page"
            and low_context(record),
        ),
        "no_answer_retrieved_misleading_context": _sample_failure_record(
            records,
            lambda record: bool(record.get("gold", {}).get("expected_abstention", False))
            and bool(record.get("no_answer_diagnostics", {}).get("key_entity_overlap", False)),
        ),
        "proposition_context_loss": _sample_failure_record(
            records,
            lambda record: strategy == "proposition_like" and low_context(record),
        ),
        "parent_child_not_used": _sample_failure_record(
            records,
            lambda record: strategy == "hierarchical_parent_child" and low_context(record),
        ),
    }
    return {
        failure_type: {
            "samples_total": len(samples),
            "samples": samples,
        }
        for failure_type, samples in cards.items()
    }


def build_chunking_failure_cards_v2(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "metadata": {
            "source_report": "reports/stages/chunking_comparison_benchmark_v2.json",
            "failure_types": list(FAILURE_TYPES),
            "selection_policy": "first deterministic matching sample per strategy and failure type",
            "claim_policy": "qualitative diagnostics only; not a manual error taxonomy",
        },
        "strategies": {
            strategy: _failure_samples_for_strategy(strategy, strategy_result)
            for strategy, strategy_result in result["strategies"].items()
        },
    }


def write_chunking_comparison_v2_json(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_chunking_failure_cards_v2_json(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_chunking_comparison_v2_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = result["metadata"]
    lines = [
        "# Chunking Comparison Benchmark V2",
        "",
        f"- Run ID: `{metadata['run_manifest']['run_id']}`",
        f"- Labels: {metadata['label_breakdown']['labels_total']}",
        f"- Supported labels: {metadata['label_breakdown']['supported_total']}",
        f"- Insufficient-evidence labels: {metadata['label_breakdown']['no_answer_total']}",
        f"- Evaluation mode: `{metadata.get('evaluation_mode', 'top_k')}`",
        f"- Context budget chars: {metadata.get('context_budget_chars')}",
        "- Scoring: layered metrics only; no single mixed overall score.",
        "- Claim boundary: rankings are benchmark-specific and do not identify a universal best chunker.",
        "- Supported-only retrieval metrics are primary; all-label metrics are diagnostic.",
        "- Top-k rankings can privilege larger chunks by exposing more context; fixed-budget results are the fairer comparison when available.",
        "",
        "## Supported-Only Ranking",
        "",
        "| Rank | Strategy | Recall@5 | Recall@10 | Precision@5 | MRR@5 | MRR@10 | NDCG@10 | Context Precision@5 | Context Recall |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, item in enumerate(result["ranking"], start=1):
        retrieval = result["strategies"][item["strategy"]]["aggregate"]["retrieval_supported_only"]
        lines.append(
            f"| {rank} | {item['strategy']} | {retrieval['recall_at_5']} | "
            f"{retrieval['recall_at_10']} | {retrieval['precision_at_5']} | "
            f"{retrieval['mrr_at_5']} | {retrieval['mrr_at_10']} | "
            f"{retrieval['ndcg_at_10']} | {retrieval['context_precision_at_5']} | "
            f"{retrieval['context_recall']} |"
        )

    lines.extend(
        [
            "",
            "## Strategy Cost And Chunking Diagnostics",
            "",
            "| Strategy | Chunks | Avg chars | P95 chars | Avg tokens | Boundary preservation | Overlap redundancy | Index build s | Mean query s | P95 query s | Index bytes | Cost notes |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for strategy, strategy_result in result["strategies"].items():
        aggregate = strategy_result["aggregate"]
        chunking = aggregate["chunking"]
        latency = aggregate["cost_latency"]
        lines.append(
            f"| {strategy} | {chunking['chunks_total']} | {chunking['avg_chars']} | "
            f"{chunking['p95_chars']} | {chunking['avg_tokens']} | "
            f"{chunking['boundary_preservation_rate']} | {chunking['overlap_redundancy']} | "
            f"{latency['index_build_seconds']} | {latency['query_latency_mean_seconds']} | "
            f"{latency['query_latency_p95_seconds']} | {latency['index_size_bytes']} | "
            f"{strategy_result['cost_notes']} |"
        )

    lines.extend(["", "## Confidence Intervals", ""])
    lines.append("| Strategy | Metric | Mean | 95% CI | n |")
    lines.append("| --- | --- | ---: | --- | ---: |")
    for strategy, strategy_result in result["strategies"].items():
        ci = strategy_result["aggregate"]["retrieval_confidence_intervals_supported_only"]
        for metric in ("recall_at_5", "recall_at_10", "mrr_at_5", "ndcg_at_10", "context_recall"):
            values = ci[metric]
            lines.append(
                f"| {strategy} | {metric} | {values['mean']} | "
                f"{values['lower']} - {values['upper']} | {values['n']} |"
            )

    lines.extend(["", "## Supported Vs No-Answer Diagnostics", ""])
    lines.append("| Strategy | Supported Recall@5 | All-label Recall@5 diagnostic | No-answer context rate@5 | No-answer key-entity overlap@5 |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for strategy, strategy_result in result["strategies"].items():
        aggregate = strategy_result["aggregate"]
        lines.append(
            f"| {strategy} | {aggregate['retrieval_supported_only']['recall_at_5']} | "
            f"{aggregate['retrieval_all_labels_diagnostic']['recall_at_5']} | "
            f"{aggregate['no_answer_diagnostics']['retrieved_context_rate_at_5']} | "
            f"{aggregate['no_answer_diagnostics']['key_entity_overlap_rate_at_5']} |"
        )

    lines.extend(["", "## Chunk Size Sensitivity", ""])
    for family, family_result in result["chunk_size_sensitivity"].items():
        lines.extend([f"### {family}", "", family_result["interpretation"], ""])
        lines.append("| Strategy | Chunks | Avg chars | P95 chars | Recall@5 | MRR@5 | Context Recall |")
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for row in family_result["rows"]:
            lines.append(
                f"| {row['strategy']} | {row['chunks_total']} | {row['avg_chars']} | "
                f"{row['p95_chars']} | {row['recall_at_5_supported']} | "
                f"{row['mrr_at_5_supported']} | {row['context_recall_supported']} |"
            )
        lines.append("")

    lines.extend(["", "## Category-Level Analysis", ""])
    lines.append("| Strategy | Question type | Labels | Recall@5 | Recall@10 | MRR@5 | Context Recall |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: |")
    for strategy, strategy_result in result["strategies"].items():
        for category, category_result in strategy_result["aggregate"]["category_breakdown"].items():
            retrieval = category_result["retrieval"]
            lines.append(
                f"| {strategy} | {category} | {category_result['labels']} | "
                f"{retrieval['recall_at_5']} | {retrieval['recall_at_10']} | "
                f"{retrieval['mrr_at_5']} | {retrieval['context_recall']} |"
            )
    lines.extend(["", "## Implementation Metadata", ""])
    for strategy, strategy_result in result["strategies"].items():
        metadata_values = strategy_result.get("implementation_metadata", {})
        lines.append(f"- `{strategy}`: `{json.dumps(metadata_values, sort_keys=True)}`")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_chunking_failure_cards_v2_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Chunking Failure Cards Benchmark V2",
        "",
        "- These cards are deterministic qualitative diagnostics, not manual review results.",
        "- Each card stores the first matching sample per strategy and failure type when one exists.",
        "",
        "| Strategy | Failure type | Samples | Example CQ | Notes |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for strategy, failures in result["strategies"].items():
        for failure_type, failure in failures.items():
            samples = failure["samples"]
            example = samples[0]["cq_id"] if samples else ""
            notes = "sample found" if samples else "no matching sample in this run"
            lines.append(
                f"| {strategy} | {failure_type} | {failure['samples_total']} | {example} | {notes} |"
            )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def build_chunking_topk_sensitivity_v2_from_result(
    result: dict[str, Any],
    *,
    top_k_values: tuple[int, ...] = TOPK_SENSITIVITY_VALUES,
) -> dict[str, Any]:
    strategies: dict[str, Any] = {}
    for strategy, strategy_result in result["strategies"].items():
        supported = _supported_records(strategy_result["records"])
        topk = {
            str(k): _aggregate_metric_at_k(supported, k)
            for k in top_k_values
        }
        strategies[strategy] = {
            "top_k": topk,
            "chunking": strategy_result["aggregate"]["chunking"],
            "implementation_metadata": strategy_result.get("implementation_metadata", {}),
        }
    rankings = {
        str(k): sorted(
            (
                {
                    "strategy": strategy,
                    "recall": values["top_k"][str(k)]["recall"],
                    "mrr": values["top_k"][str(k)]["mrr"],
                    "context_recall": values["top_k"][str(k)]["context_recall"],
                    "mean_context_chars": values["top_k"][str(k)]["mean_context_chars"],
                }
                for strategy, values in strategies.items()
            ),
            key=lambda item: (
                -float(item["recall"]),
                -float(item["mrr"]),
                -float(item["context_recall"]),
                item["strategy"],
            ),
        )
        for k in top_k_values
    }
    return {
        "metadata": {
            "source_report": "reports/stages/chunking_comparison_benchmark_v2.json",
            "top_k_values": list(top_k_values),
            "labels": result["metadata"]["label_breakdown"],
            "scoring_policy": "supported_labels_only_for_retrieval; no mixed overall score",
            "claim_policy": (
                "Top-k sensitivity is diagnostic. Larger k also changes context volume, "
                "so it is not a universal chunker ranking."
            ),
        },
        "rankings": rankings,
        "strategies": strategies,
    }


def write_chunking_topk_sensitivity_v2_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_chunking_topk_sensitivity_v2_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Chunking Top-K Sensitivity Benchmark V2",
        "",
        "- Supported-label retrieval only; insufficient-evidence labels are not recall targets.",
        "- Top-k comparisons also change context volume and must not be read as a universal chunking ranking.",
        "",
    ]
    for k, ranking in result["rankings"].items():
        lines.extend(
            [
                f"## Top-{k}",
                "",
                "| Rank | Strategy | Recall | MRR | Context Recall | Mean Context Chars |",
                "| ---: | --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for rank, item in enumerate(ranking, start=1):
            lines.append(
                f"| {rank} | {item['strategy']} | {item['recall']} | "
                f"{item['mrr']} | {item['context_recall']} | "
                f"{item['mean_context_chars']} |"
            )
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def build_chunking_category_analysis_v2_from_result(result: dict[str, Any]) -> dict[str, Any]:
    categories = (
        "supported_factual",
        "concept_definition",
        "relation_causal",
        "cross_page",
        "paraphrase",
        "terminology_variation",
        "insufficient_evidence",
    )
    category_rows: dict[str, list[dict[str, Any]]] = {category: [] for category in categories}
    for strategy, strategy_result in result["strategies"].items():
        breakdown = strategy_result["aggregate"].get("category_breakdown", {})
        records = strategy_result["records"]
        for category in categories:
            category_result = breakdown.get(category, {"labels": 0, "retrieval": {}})
            row = {
                "strategy": strategy,
                "labels": category_result.get("labels", 0),
                "retrieval": category_result.get("retrieval", {}),
                "diagnostic_only": category == "insufficient_evidence",
            }
            if category == "insufficient_evidence":
                no_answer_records = [
                    record
                    for record in records
                    if record.get("gold", {}).get("question_type") == category
                ]
                denominator = len(no_answer_records) or 1
                row["no_answer_diagnostics"] = {
                    "key_entity_overlap_rate_at_5": round(
                        sum(
                            int(
                                record.get("no_answer_diagnostics", {}).get(
                                    "key_entity_overlap",
                                    False,
                                )
                            )
                            for record in no_answer_records
                        )
                        / denominator,
                        4,
                    ),
                    "interpretation": "Possible misleading context; not recall.",
                }
            category_rows[category].append(row)
    best_by_category: dict[str, dict[str, Any]] = {}
    for category, rows in category_rows.items():
        if category == "insufficient_evidence":
            best_by_category[category] = {
                "strategy": "diagnostic_only",
                "interpretation": "No-answer labels have no gold evidence target.",
            }
            continue
        ranked = sorted(
            rows,
            key=lambda item: (
                -float(item.get("retrieval", {}).get("recall_at_5", 0.0)),
                -float(item.get("retrieval", {}).get("mrr_at_5", 0.0)),
                -float(item.get("retrieval", {}).get("context_recall", 0.0)),
                item["strategy"],
            ),
        )
        best_by_category[category] = ranked[0] if ranked else {}
    return {
        "metadata": {
            "source_report": "reports/stages/chunking_comparison_benchmark_v2.json",
            "categories": list(categories),
            "scoring_policy": "supported categories use retrieval metrics; insufficient-evidence is diagnostic only",
            "claim_policy": "Category winners are benchmark-specific and do not establish a universal best chunker.",
        },
        "best_by_category": best_by_category,
        "categories": category_rows,
    }


def write_chunking_category_analysis_v2_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_chunking_category_analysis_v2_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Chunking Category Analysis Benchmark V2",
        "",
        "- Supported question categories use retrieval metrics.",
        "- Insufficient-evidence labels are diagnostic only and are not recall failures.",
        "",
        "## Best By Category",
        "",
        "| Category | Strategy | Recall@5 | MRR@5 | Context Recall | Interpretation |",
        "| --- | --- | ---: | ---: | ---: | --- |",
    ]
    for category, best in result["best_by_category"].items():
        retrieval = best.get("retrieval", {}) if isinstance(best, dict) else {}
        lines.append(
            f"| {category} | {best.get('strategy', 'TBD')} | "
            f"{retrieval.get('recall_at_5', 'n/a')} | "
            f"{retrieval.get('mrr_at_5', 'n/a')} | "
            f"{retrieval.get('context_recall', 'n/a')} | "
            f"{best.get('interpretation', 'benchmark-specific')} |"
        )
    lines.extend(
        [
            "",
            "## Full Category Table",
            "",
            "| Category | Strategy | Labels | Recall@5 | Recall@10 | MRR@5 | Context Recall | Diagnostic only |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for category, rows in result["categories"].items():
        for row in rows:
            retrieval = row.get("retrieval", {})
            lines.append(
                f"| {category} | {row['strategy']} | {row['labels']} | "
                f"{retrieval.get('recall_at_5', 'n/a')} | "
                f"{retrieval.get('recall_at_10', 'n/a')} | "
                f"{retrieval.get('mrr_at_5', 'n/a')} | "
                f"{retrieval.get('context_recall', 'n/a')} | "
                f"{row['diagnostic_only']} |"
            )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_chunking_topk_sensitivity_v2(
    pdf_path: str | Path,
    gold_labels_path: str | Path,
    chunks_dir: str | Path,
    index_dir: str | Path,
    output_dir: str | Path,
    *,
    collection_prefix: str = "phak_ch4_chunking_v2",
    strategies: tuple[str, ...] = BENCHMARK_V2_CHUNKING_STRATEGIES,
    max_labels: int | None = None,
    rebuild_chunks: bool = True,
    rebuild_indexes: bool = True,
    embedding_model: str = DEFAULT_SEMANTIC_EMBEDDING_MODEL,
    semantic_download: bool = True,
    top_k_values: tuple[int, ...] = TOPK_SENSITIVITY_VALUES,
    command: str = "aviation-ai report chunking-topk-sensitivity-v2",
    index_builder: IndexBuilder = build_chroma_index,
    retriever: Retriever = query_chroma_index,
) -> tuple[Path, Path, dict[str, Any]]:
    comparison = build_chunking_comparison_v2(
        pdf_path,
        gold_labels_path,
        chunks_dir,
        index_dir,
        output_dir=output_dir,
        collection_prefix=collection_prefix,
        strategies=strategies,
        max_labels=max_labels,
        rebuild_chunks=rebuild_chunks,
        rebuild_indexes=rebuild_indexes,
        embedding_model=embedding_model,
        semantic_download=semantic_download,
        vector_top_k=max(top_k_values),
        command=command,
        index_builder=index_builder,
        retriever=retriever,
    )
    result = build_chunking_topk_sensitivity_v2_from_result(
        comparison,
        top_k_values=top_k_values,
    )
    output = Path(output_dir)
    json_path = write_chunking_topk_sensitivity_v2_json(
        result,
        output / "chunking_topk_sensitivity_benchmark_v2.json",
    )
    md_path = write_chunking_topk_sensitivity_v2_markdown(
        result,
        output / "chunking_topk_sensitivity_benchmark_v2.md",
    )
    return json_path, md_path, result


def write_chunking_category_analysis_v2(
    pdf_path: str | Path,
    gold_labels_path: str | Path,
    chunks_dir: str | Path,
    index_dir: str | Path,
    output_dir: str | Path,
    *,
    collection_prefix: str = "phak_ch4_chunking_v2",
    strategies: tuple[str, ...] = BENCHMARK_V2_CHUNKING_STRATEGIES,
    max_labels: int | None = None,
    rebuild_chunks: bool = True,
    rebuild_indexes: bool = True,
    embedding_model: str = DEFAULT_SEMANTIC_EMBEDDING_MODEL,
    semantic_download: bool = True,
    command: str = "aviation-ai report chunking-category-analysis-v2",
    index_builder: IndexBuilder = build_chroma_index,
    retriever: Retriever = query_chroma_index,
) -> tuple[Path, Path, dict[str, Any]]:
    comparison = build_chunking_comparison_v2(
        pdf_path,
        gold_labels_path,
        chunks_dir,
        index_dir,
        output_dir=output_dir,
        collection_prefix=collection_prefix,
        strategies=strategies,
        max_labels=max_labels,
        rebuild_chunks=rebuild_chunks,
        rebuild_indexes=rebuild_indexes,
        embedding_model=embedding_model,
        semantic_download=semantic_download,
        command=command,
        index_builder=index_builder,
        retriever=retriever,
    )
    result = build_chunking_category_analysis_v2_from_result(comparison)
    output = Path(output_dir)
    json_path = write_chunking_category_analysis_v2_json(
        result,
        output / "chunking_category_analysis_benchmark_v2.json",
    )
    md_path = write_chunking_category_analysis_v2_markdown(
        result,
        output / "chunking_category_analysis_benchmark_v2.md",
    )
    return json_path, md_path, result


def write_chunking_comparison_v2(
    pdf_path: str | Path,
    gold_labels_path: str | Path,
    chunks_dir: str | Path,
    index_dir: str | Path,
    output_dir: str | Path,
    *,
    collection_prefix: str = "phak_ch4_chunking_v2",
    strategies: tuple[str, ...] = BENCHMARK_V2_CHUNKING_STRATEGIES,
    max_labels: int | None = None,
    rebuild_chunks: bool = True,
    rebuild_indexes: bool = True,
    embedding_model: str = DEFAULT_SEMANTIC_EMBEDDING_MODEL,
    semantic_download: bool = True,
    evaluation_mode: str = "top_k",
    context_budget_chars: int = DEFAULT_CONTEXT_BUDGET_CHARS,
    command: str = "aviation-ai report chunking-comparison-v2",
    index_builder: IndexBuilder = build_chroma_index,
    retriever: Retriever = query_chroma_index,
) -> tuple[Path, Path, Path, Path, dict[str, Any], dict[str, Any]]:
    output = Path(output_dir)
    result = build_chunking_comparison_v2(
        pdf_path,
        gold_labels_path,
        chunks_dir,
        index_dir,
        output_dir=output,
        collection_prefix=collection_prefix,
        strategies=strategies,
        max_labels=max_labels,
        rebuild_chunks=rebuild_chunks,
        rebuild_indexes=rebuild_indexes,
        embedding_model=embedding_model,
        semantic_download=semantic_download,
        evaluation_mode=evaluation_mode,
        context_budget_chars=context_budget_chars,
        command=command,
        index_builder=index_builder,
        retriever=retriever,
    )
    failure_cards = build_chunking_failure_cards_v2(result)
    comparison_stem = (
        "chunking_comparison_benchmark_v2_budget"
        if evaluation_mode == "fixed_context_budget"
        else "chunking_comparison_benchmark_v2"
    )
    json_path = write_chunking_comparison_v2_json(
        result,
        output / f"{comparison_stem}.json",
    )
    md_path = write_chunking_comparison_v2_markdown(
        result,
        output / f"{comparison_stem}.md",
    )
    failure_json_path = write_chunking_failure_cards_v2_json(
        failure_cards,
        output / "chunking_failure_cards_benchmark_v2.json",
    )
    failure_md_path = write_chunking_failure_cards_v2_markdown(
        failure_cards,
        output / "chunking_failure_cards_benchmark_v2.md",
    )
    return json_path, md_path, failure_json_path, failure_md_path, result, failure_cards
