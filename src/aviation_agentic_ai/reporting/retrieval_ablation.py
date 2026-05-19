from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from aviation_agentic_ai.evaluation.cost_latency import cost_latency_block
from aviation_agentic_ai.evaluation.gold import (
    GoldLabel,
    gold_labels_for_questions,
    load_boundary_questions,
    load_gold_labels,
)
from aviation_agentic_ai.evaluation.metrics import (
    aggregate_kg_evidence_metrics,
    aggregate_retrieval_metrics,
    kg_evidence_metrics,
    retrieval_metrics,
)
from aviation_agentic_ai.evaluation.protocol import build_run_manifest, embedding_metadata
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.retrieval.hybrid import run_retrieval
from aviation_agentic_ai.retrieval.indexing import DEFAULT_COLLECTION_NAME


RetrievalRunner = Callable[..., dict[str, Any]]
Scenario = tuple[str, int, int, int]


DEFAULT_SCENARIOS: tuple[Scenario, ...] = (
    ("vector", 2, 5, 8),
    ("hybrid_graph_disabled", 2, 5, 8),
    ("graph", 1, 5, 8),
    ("graph", 2, 5, 8),
    ("graph", 3, 5, 8),
    ("hybrid", 1, 5, 8),
    ("hybrid", 2, 5, 8),
    ("hybrid", 3, 5, 8),
    ("hybrid", 2, 3, 8),
    ("hybrid", 2, 8, 8),
    ("hybrid", 2, 5, 5),
    ("hybrid", 2, 5, 10),
)


def _scenario_name(mode: str, graph_hops: int, vector_top_k: int, hybrid_top_k: int) -> str:
    return f"{mode}_hops{graph_hops}_v{vector_top_k}_h{hybrid_top_k}"


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "retrieval": aggregate_retrieval_metrics(
            [record["metrics"]["retrieval"] for record in records]
        ),
        "kg_evidence": aggregate_kg_evidence_metrics(
            [record["metrics"]["kg_evidence"] for record in records]
        ),
    }


def _hit_summary(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "chunk_id": str(hit.get("chunk_id", "")),
            "page": hit.get("page"),
            "rank": hit.get("rank"),
            "source": hit.get("source"),
        }
        for hit in hits
    ]


def _triple_summary(triples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "triple_id": str(triple.get("triple_id", "")),
            "chunk_id": str(triple.get("chunk_id", "")),
            "page": triple.get("page"),
            "rank": triple.get("rank"),
            "subject": triple.get("subject"),
            "predicate": triple.get("predicate"),
            "object": triple.get("object"),
        }
        for triple in triples
    ]


def _questions_and_labels(
    boundary_cq_path: str | Path,
    gold_labels_path: str | Path | None,
) -> tuple[list[dict[str, Any]], dict[str, GoldLabel]]:
    if gold_labels_path is not None:
        labels = load_gold_labels(gold_labels_path)
        if labels and all(label.question for label in labels.values()):
            questions = [
                {
                    "id": label.cq_id,
                    "competency_question": label.question,
                    "source_document": label.source_document,
                    "source_page": label.source_page,
                    "key_entities": list(label.key_entities),
                }
                for label in labels.values()
            ]
            return questions, labels
    questions = load_boundary_questions(boundary_cq_path)
    return questions, gold_labels_for_questions(questions, gold_labels_path)


def _explain_scenario(mode: str, aggregate: dict[str, Any]) -> str:
    retrieval = aggregate["retrieval"]
    kg = aggregate["kg_evidence"]
    if mode == "vector":
        return (
            "Vector retrieval measures whether semantic text search alone recovers the gold "
            "chunk/span/page evidence."
        )
    if mode == "hybrid_graph_disabled":
        return (
            "This is the hybrid ablation with graph evidence disabled; it should match "
            "vector retrieval behavior while preserving the hybrid experiment label."
        )
    if mode == "graph":
        return (
            "Graph retrieval is valuable when KG triples cover key entities, even if coarse "
            f"Recall@5 is {retrieval['recall_at_5']} and evidence coverage is "
            f"{kg['evidence_coverage']}."
        )
    return (
        "Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can "
        f"help evidence coverage ({kg['evidence_coverage']}) while not always improving "
        f"page-level Recall@5 ({retrieval['recall_at_5']})."
    )


def build_retrieval_ablation(
    boundary_cq_path: str | Path,
    chunks_path: str | Path,
    kg_path: str | Path,
    index_dir: str | Path,
    *,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    gold_labels_path: str | Path | None = None,
    scenarios: tuple[Scenario, ...] = DEFAULT_SCENARIOS,
    query_runner: RetrievalRunner = run_retrieval,
    command: str = "aviation-ai report retrieval-ablation",
) -> dict[str, Any]:
    started = perf_counter()
    questions, gold_labels = _questions_and_labels(boundary_cq_path, gold_labels_path)
    scenario_results: dict[str, Any] = {}

    for mode, graph_hops, vector_top_k, hybrid_top_k in scenarios:
        records: list[dict[str, Any]] = []
        for cq in questions:
            gold = gold_labels[str(cq["id"])]
            runner_mode = "vector" if mode == "hybrid_graph_disabled" else mode
            result = query_runner(
                cq["competency_question"],
                runner_mode,
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
                    gold,
                    top_k=vector_top_k,
                ),
                "kg_evidence": kg_evidence_metrics(
                    result.get("graph_triples", []),
                    gold.key_entities,
                ),
            }
            records.append(
                {
                    "cq_id": cq["id"],
                    "question": cq["competency_question"],
                    "gold": gold.to_dict(),
                    "mode": mode,
                    "settings": {
                        "graph_hops": graph_hops,
                        "vector_top_k": vector_top_k,
                        "hybrid_top_k": hybrid_top_k,
                    },
                    "metrics": metrics,
                    "hits": _hit_summary(result.get("fused_chunks", [])),
                    "graph_triples": _triple_summary(result.get("graph_triples", [])),
                }
            )
        aggregate = _aggregate(records)
        scenario_results[_scenario_name(mode, graph_hops, vector_top_k, hybrid_top_k)] = {
            "mode": mode,
            "settings": {
                "graph_hops": graph_hops,
                "vector_top_k": vector_top_k,
                "hybrid_top_k": hybrid_top_k,
            },
            "aggregate": aggregate,
            "explanation": _explain_scenario(mode, aggregate),
            "records": records,
        }

    run_manifest = build_run_manifest(
        "retrieval_ablation",
        parameters={
            "scenarios": [
                {
                    "mode": mode,
                    "graph_hops": hops,
                    "vector_top_k": vector_top_k,
                    "hybrid_top_k": hybrid_top_k,
                }
                for mode, hops, vector_top_k, hybrid_top_k in scenarios
            ],
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
        rebuild_policy={"chunks": False, "indexes": False, "kg": False},
        collection_name=collection_name,
        chunking_strategy="structure_aware",
        command=command,
        llm={"provider": "none", "model": "not_used"},
        embedding=embedding_metadata(index_dir, collection_name),
    )
    elapsed = perf_counter() - started
    return {
        "metadata": {
            "run_manifest": run_manifest,
            "boundary_cq_path": project_relative_path(boundary_cq_path),
            "gold_labels_path": project_relative_path(gold_labels_path)
            if gold_labels_path is not None
            else None,
            "chunks_path": project_relative_path(chunks_path),
            "kg_path": project_relative_path(kg_path),
            "index_dir": project_relative_path(index_dir),
            "collection_name": collection_name,
            "questions_total": len(questions),
            "scenarios_total": len(scenarios),
            "scoring_policy": "layered_metrics_no_mixed_overall_score",
            "cost_latency": cost_latency_block(
                elapsed_seconds=elapsed,
                questions_total=len(questions),
                chunks_path=chunks_path,
                kg_path=kg_path,
                index_dir=index_dir,
            ),
        },
        "scenarios": scenario_results,
    }


def write_retrieval_ablation_json(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_retrieval_ablation_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Retrieval Ablation",
        "",
        f"- Run ID: `{result['metadata']['run_manifest']['run_id']}`",
        f"- Questions: {result['metadata']['questions_total']}",
        f"- Scenarios: {result['metadata']['scenarios_total']}",
        "- Scoring: layered retrieval and KG evidence metrics; no mixed overall score.",
        "",
        "| Scenario | Mode | Recall@5 | MRR@5 | Context Precision@5 | KG coverage | Avg triples |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, scenario in result["scenarios"].items():
        retrieval = scenario["aggregate"]["retrieval"]
        kg = scenario["aggregate"]["kg_evidence"]
        lines.append(
            f"| {name} | {scenario['mode']} | {retrieval['recall_at_5']} | "
            f"{retrieval['mrr_at_5']} | {retrieval['context_precision_at_5']} | "
            f"{kg['evidence_coverage']} | {kg['avg_related_triple_count']} |"
        )
    lines.extend(["", "## Interpretation", ""])
    for name, scenario in result["scenarios"].items():
        lines.extend([f"### {name}", "", scenario["explanation"], ""])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_retrieval_ablation(
    boundary_cq_path: str | Path,
    chunks_path: str | Path,
    kg_path: str | Path,
    index_dir: str | Path,
    output_dir: str | Path,
    *,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    gold_labels_path: str | Path | None = None,
    scenarios: tuple[Scenario, ...] = DEFAULT_SCENARIOS,
    query_runner: RetrievalRunner = run_retrieval,
    report_name: str = "retrieval_ablation",
    command: str = "aviation-ai report retrieval-ablation",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_retrieval_ablation(
        boundary_cq_path,
        chunks_path,
        kg_path,
        index_dir,
        collection_name=collection_name,
        gold_labels_path=gold_labels_path,
        scenarios=scenarios,
        query_runner=query_runner,
        command=command,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "retrieval_ablation"
    json_path = write_retrieval_ablation_json(result, output / f"{stem}.json")
    md_path = write_retrieval_ablation_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
