from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any, Callable

from aviation_agentic_ai.chunking.chunks import (
    CHUNKING_STRATEGIES,
    SourceChunk,
    build_chunk_file,
    chunk_output_path_for_strategy,
    collection_name_for_strategy,
    read_chunks_jsonl,
)
from aviation_agentic_ai.evaluation.document_metadata import document_metadata_from_pdf
from aviation_agentic_ai.evaluation.gold import gold_labels_for_questions, load_boundary_questions
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


def chunk_stats(chunks: list[SourceChunk]) -> dict[str, Any]:
    lengths = [len(chunk.text) for chunk in chunks]
    return {
        "chunk_count": len(chunks),
        "avg_chars": round(mean(lengths), 2) if lengths else 0.0,
        "p95_chars": _percentile(lengths, 0.95),
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
    strategies: tuple[str, ...] = CHUNKING_STRATEGIES,
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
    strategies: tuple[str, ...] = CHUNKING_STRATEGIES,
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
