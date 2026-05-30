from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from aviation_agentic_ai.advisory import ADVISORY_BOUNDARY
from aviation_agentic_ai.chunking.chunks import CHUNKING_STRATEGIES, read_chunks_jsonl
from aviation_agentic_ai.evaluation.gold import load_questions_and_gold_labels
from aviation_agentic_ai.evaluation.metrics import (
    aggregate_answer_metrics,
    aggregate_kg_evidence_metrics,
    aggregate_retrieval_metrics,
    answer_metrics,
    kg_evidence_metrics,
    retrieval_metrics,
)
from aviation_agentic_ai.evaluation.protocol import (
    build_run_manifest,
    embedding_metadata,
)
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.evidence_cards import (
    build_evidence_cards,
    evidence_cards_markdown_lines,
)
from aviation_agentic_ai.reporting.io import write_json_report
from aviation_agentic_ai.retrieval.hybrid import run_query
from aviation_agentic_ai.retrieval.indexing import DEFAULT_COLLECTION_NAME


QueryRunner = Callable[..., dict[str, Any]]


def _infer_chunking_strategy(chunks_path: str | Path) -> str:
    path = Path(chunks_path)
    if path.exists():
        chunks = read_chunks_jsonl(path)
        if chunks:
            return chunks[0].strategy
    name = path.name
    for strategy in CHUNKING_STRATEGIES:
        if strategy in name:
            return strategy
    return "unknown"


def _aggregate_mode_metrics(mode_metrics: list[dict[str, dict[str, Any]]]) -> dict[str, Any]:
    aggregate = {
        "retrieval": aggregate_retrieval_metrics(
            [item["retrieval"] for item in mode_metrics]
        ),
        "kg_evidence": aggregate_kg_evidence_metrics(
            [item["kg_evidence"] for item in mode_metrics]
        ),
        "llm_answer": aggregate_answer_metrics(
            [item["llm_answer"] for item in mode_metrics]
        ),
    }
    aggregate["recall_at_5"] = aggregate["retrieval"]["recall_at_5"]
    aggregate["evidence_coverage"] = aggregate["kg_evidence"]["evidence_coverage"]
    aggregate["citation_completeness"] = aggregate["llm_answer"]["citation_completeness"]
    return aggregate


def build_hybrid_rag_experiment(
    boundary_cq_path: str | Path,
    chunks_path: str | Path,
    kg_path: str | Path,
    index_dir: str | Path,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    graph_hops: int = 2,
    vector_top_k: int = 5,
    hybrid_top_k: int = 8,
    max_questions: int | None = None,
    gold_labels_path: str | Path | None = None,
    rebuild_chunks: bool = False,
    rebuild_indexes: bool = False,
    rebuild_kg: bool = False,
    chunking_strategy: str | None = None,
    command: str = "aviation-ai report hybrid-rag",
    query_runner: QueryRunner = run_query,
) -> dict[str, Any]:
    questions, gold_labels = load_questions_and_gold_labels(boundary_cq_path, gold_labels_path)
    if max_questions is not None:
        questions = questions[:max_questions]
    records: list[dict[str, Any]] = []
    mode_metric_items: dict[str, list[dict[str, dict[str, Any]]]] = {
        mode: [] for mode in ("vector", "graph", "hybrid")
    }

    for cq in questions:
        mode_results: dict[str, Any] = {}
        gold_label = gold_labels[str(cq["id"])]
        for mode in ("vector", "graph", "hybrid"):
            result = query_runner(
                cq["competency_question"],
                mode,
                chunks_path,
                kg_path,
                index_dir,
                collection_name=collection_name,
                graph_hops=graph_hops,
                vector_top_k=vector_top_k,
                hybrid_top_k=hybrid_top_k,
            )
            metrics = {
                "retrieval": retrieval_metrics(
                    result.get("fused_chunks", []),
                    gold_label,
                    top_k=vector_top_k,
                ),
                "kg_evidence": kg_evidence_metrics(
                    result.get("graph_triples", []),
                    [str(item) for item in cq.get("key_entities", [])],
                ),
                "llm_answer": answer_metrics(result),
            }
            mode_metric_items[mode].append(metrics)
            mode_results[mode] = {**result, "metrics": metrics}
        records.append(
            {
                "cq_id": cq["id"],
                "question": cq["competency_question"],
                "source_page": cq["source_page"],
                "key_entities": cq.get("key_entities", []),
                "gold": gold_label.to_dict(),
                "results": mode_results,
            }
        )

    aggregate = {
        mode: _aggregate_mode_metrics(values)
        for mode, values in mode_metric_items.items()
    }
    aggregate["hybrid_lift"] = {
        "vs_vector_recall_at_5": round(
            aggregate["hybrid"]["retrieval"]["recall_at_5"]
            - aggregate["vector"]["retrieval"]["recall_at_5"],
            4,
        ),
        "vs_graph_recall_at_5": round(
            aggregate["hybrid"]["retrieval"]["recall_at_5"]
            - aggregate["graph"]["retrieval"]["recall_at_5"],
            4,
        ),
    }
    effective_chunking_strategy = chunking_strategy or _infer_chunking_strategy(chunks_path)
    run_manifest = build_run_manifest(
        "hybrid_rag",
        parameters={
            "graph_hops": graph_hops,
            "vector_top_k": vector_top_k,
            "hybrid_top_k": hybrid_top_k,
            "max_questions": max_questions,
            "gold_labels_path": project_relative_path(gold_labels_path)
            if gold_labels_path is not None
            else None,
        },
        artifacts={
            "boundary_cq_path": boundary_cq_path,
            "chunks_path": chunks_path,
            "kg_path": kg_path,
            "index_dir": index_dir,
        },
        rebuild_policy={"chunks": rebuild_chunks, "indexes": rebuild_indexes, "kg": rebuild_kg},
        collection_name=collection_name,
        chunking_strategy=effective_chunking_strategy,
        command=command,
        embedding=embedding_metadata(index_dir, collection_name),
    )
    result = {
        "metadata": {
            "run_manifest": run_manifest,
            "advisory_boundary": ADVISORY_BOUNDARY,
            "boundary_cq_path": project_relative_path(boundary_cq_path),
            "gold_labels_path": project_relative_path(gold_labels_path)
            if gold_labels_path is not None
            else None,
            "chunks_path": project_relative_path(chunks_path),
            "kg_path": project_relative_path(kg_path),
            "index_dir": project_relative_path(index_dir),
            "collection_name": collection_name,
            "chunking_strategy": effective_chunking_strategy,
            "rebuild_chunks": rebuild_chunks,
            "rebuild_indexes": rebuild_indexes,
            "rebuild_kg": rebuild_kg,
            "graph_hops": graph_hops,
            "vector_top_k": vector_top_k,
            "hybrid_top_k": hybrid_top_k,
            "questions_total": len(questions),
        },
        "aggregate": aggregate,
        "records": records,
    }
    result["evidence_cards"] = build_evidence_cards(result, top_k=vector_top_k)
    return result


def write_hybrid_rag_experiment_json(result: dict[str, Any], output_path: str | Path) -> Path:
    return write_json_report(result, output_path)


def write_hybrid_rag_experiment_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    aggregate = result["aggregate"]
    lines = [
        "# Hybrid RAG Experiment",
        "",
        f"- Run ID: `{result['metadata']['run_manifest']['run_id']}`",
        f"- Questions: {result['metadata']['questions_total']}",
        f"- Chunks: `{result['metadata']['chunks_path']}`",
        f"- KG: `{result['metadata']['kg_path']}`",
        f"- Chroma collection: `{result['metadata']['collection_name']}`",
        f"- Chunking strategy: `{result['metadata']['chunking_strategy']}`",
        f"- Rebuild chunks/index/KG: {result['metadata']['rebuild_chunks']} / "
        f"{result['metadata']['rebuild_indexes']} / {result['metadata']['rebuild_kg']}",
        "",
        "## Agent Boundary",
        "",
        result["metadata"]["advisory_boundary"],
        "",
        "## Aggregate Metrics",
        "",
        "### Retrieval",
        "",
        "| Mode | Recall@5 | MRR@5 | Context Precision@5 |",
        "| --- | ---: | ---: | ---: |",
    ]
    for mode in ("vector", "graph", "hybrid"):
        retrieval = aggregate[mode]["retrieval"]
        lines.append(
            f"| {mode} | {retrieval['recall_at_5']} | {retrieval['mrr_at_5']} | "
            f"{retrieval['context_precision_at_5']} |"
        )
    lines.extend(
        [
            "",
            "### KG Evidence",
            "",
            "| Mode | Evidence coverage | Avg triples | Provenance complete | Avg invalid triples |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for mode in ("vector", "graph", "hybrid"):
        kg_metrics = aggregate[mode]["kg_evidence"]
        lines.append(
            f"| {mode} | {kg_metrics['evidence_coverage']} | "
            f"{kg_metrics['avg_related_triple_count']} | "
            f"{kg_metrics['provenance_complete_rate']} | "
            f"{kg_metrics['avg_invalid_triple_count']} |"
        )
    lines.extend(
        [
            "",
            "### LLM Answer",
            "",
            "| Mode | Citation completeness | Insufficient-evidence abstention | Answer present |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for mode in ("vector", "graph", "hybrid"):
        answer = aggregate[mode]["llm_answer"]
        lines.append(
            f"| {mode} | {answer['citation_completeness']} | "
            f"{answer['insufficient_evidence_abstention']} | {answer['answer_present']} |"
        )
    lines.extend(
        [
            "",
            "## Hybrid Lift",
            "",
            f"- vs vector Recall@5: {aggregate['hybrid_lift']['vs_vector_recall_at_5']}",
            f"- vs graph Recall@5: {aggregate['hybrid_lift']['vs_graph_recall_at_5']}",
            "",
            "## Question Results",
            "",
        ]
    )
    for record in result["records"]:
        hybrid = record["results"]["hybrid"]
        retrieval = hybrid["metrics"]["retrieval"]
        kg_metrics = hybrid["metrics"]["kg_evidence"]
        answer = hybrid["metrics"]["llm_answer"]
        lines.extend(
            [
                f"### {record['cq_id']}",
                "",
                f"- Question: {record['question']}",
                f"- Source page: {record['source_page']}",
                f"- Gold level: {record['gold']['gold_level']}",
                f"- Retrieval Recall@5: {retrieval['recall_at_5']}",
                f"- KG evidence coverage: {kg_metrics['evidence_coverage']}",
                f"- Citation complete: {answer['citation_completeness']}",
                f"- Hybrid answer: {hybrid.get('answer', '')}",
                "",
            ]
        )
    evidence_cards = result.get("evidence_cards")
    if isinstance(evidence_cards, dict):
        lines.extend(evidence_cards_markdown_lines(evidence_cards))
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_hybrid_rag_experiment(
    boundary_cq_path: str | Path,
    chunks_path: str | Path,
    kg_path: str | Path,
    index_dir: str | Path,
    output_dir: str | Path,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    graph_hops: int = 2,
    vector_top_k: int = 5,
    hybrid_top_k: int = 8,
    max_questions: int | None = None,
    gold_labels_path: str | Path | None = None,
    rebuild_chunks: bool = False,
    rebuild_indexes: bool = False,
    rebuild_kg: bool = False,
    chunking_strategy: str | None = None,
    report_name: str = "hybrid_rag_experiment",
    command: str = "aviation-ai report hybrid-rag",
    query_runner: QueryRunner = run_query,
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_hybrid_rag_experiment(
        boundary_cq_path,
        chunks_path,
        kg_path,
        index_dir,
        collection_name=collection_name,
        graph_hops=graph_hops,
        vector_top_k=vector_top_k,
        hybrid_top_k=hybrid_top_k,
        max_questions=max_questions,
        gold_labels_path=gold_labels_path,
        rebuild_chunks=rebuild_chunks,
        rebuild_indexes=rebuild_indexes,
        rebuild_kg=rebuild_kg,
        chunking_strategy=chunking_strategy,
        command=command,
        query_runner=query_runner,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "hybrid_rag_experiment"
    json_path = write_hybrid_rag_experiment_json(result, output / f"{stem}.json")
    md_path = write_hybrid_rag_experiment_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
