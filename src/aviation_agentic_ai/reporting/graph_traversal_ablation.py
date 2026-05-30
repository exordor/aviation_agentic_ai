from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from aviation_agentic_ai.evaluation.bootstrap_ci import bootstrap_metric_ci
from aviation_agentic_ai.evaluation.cost_latency import cost_latency_block
from aviation_agentic_ai.evaluation.gold import GoldLabel, load_questions_and_gold_labels
from aviation_agentic_ai.evaluation.metrics import (
    aggregate_kg_evidence_metrics,
    aggregate_retrieval_metrics,
    kg_evidence_metrics,
    retrieval_metrics,
)
from aviation_agentic_ai.evaluation.protocol import build_run_manifest, embedding_metadata
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.io import write_json_report
from aviation_agentic_ai.reporting.retrieval_summaries import hit_summary, triple_summary
from aviation_agentic_ai.retrieval.graph_traversal import (
    RELATION_KEYWORDS,
    normalize_entity_label,
)
from aviation_agentic_ai.retrieval.hybrid import run_retrieval
from aviation_agentic_ai.retrieval.indexing import DEFAULT_COLLECTION_NAME


RetrievalRunner = Callable[..., dict[str, Any]]

DEFAULT_GRAPH_TRAVERSAL_SCENARIOS: tuple[dict[str, Any], ...] = (
    {
        "name": "vector_only",
        "label": "vector-only",
        "mode": "vector",
        "graph_method": "lexical",
        "graph_hops": 2,
    },
    {
        "name": "lexical_graph_search",
        "label": "lexical graph search",
        "mode": "graph",
        "graph_method": "lexical",
        "graph_hops": 2,
    },
    {
        "name": "traversal_graph_1_hop",
        "label": "traversal graph search with 1 hop",
        "mode": "graph",
        "graph_method": "traversal",
        "graph_hops": 1,
    },
    {
        "name": "traversal_graph_2_hop",
        "label": "traversal graph search with 2 hops",
        "mode": "graph",
        "graph_method": "traversal",
        "graph_hops": 2,
    },
    {
        "name": "traversal_graph_3_hop",
        "label": "traversal graph search with 3 hops",
        "mode": "graph",
        "graph_method": "traversal",
        "graph_hops": 3,
    },
    {
        "name": "hybrid_vector_lexical_graph",
        "label": "hybrid vector + lexical graph",
        "mode": "hybrid",
        "graph_method": "lexical",
        "graph_hops": 2,
    },
    {
        "name": "hybrid_vector_traversal_graph",
        "label": "hybrid vector + traversal graph",
        "mode": "hybrid",
        "graph_method": "traversal",
        "graph_hops": 2,
        "graph_fusion_policy": "rrf",
    },
    {
        "name": "hybrid_vector_traversal_guarded",
        "label": "hybrid vector + traversal graph, vector-first guarded",
        "mode": "hybrid",
        "graph_method": "traversal",
        "graph_hops": 2,
        "graph_fusion_policy": "vector_first_guarded",
    },
)


def _record_path_metrics(
    question: str,
    result: dict[str, Any],
    gold: GoldLabel,
) -> dict[str, Any]:
    paths = result.get("graph_paths", [])
    triples = result.get("graph_triples", [])
    path_hops = [int(path.get("hops", 0)) for path in paths]
    haystack = normalize_entity_label(
        " ".join(
            [
                json.dumps(paths, sort_keys=True),
                json.dumps(triples, sort_keys=True),
            ]
        )
    )
    key_entities = [
        normalize_entity_label(entity)
        for entity in gold.key_entities
        if normalize_entity_label(entity)
    ]
    covered_entities = [
        entity for entity in key_entities if entity and entity in haystack
    ]

    normalized_question = normalize_entity_label(question)
    expected_relations = {
        predicate
        for predicate, keywords in RELATION_KEYWORDS.items()
        if any(normalize_entity_label(keyword) in normalized_question for keyword in keywords)
    }
    returned_relations = {
        str(edge.get("predicate", ""))
        for path in paths
        for edge in path.get("edges", [])
    } | {str(triple.get("predicate", "")) for triple in triples}
    relation_matches = expected_relations & returned_relations
    expected_chunk_ids = {str(chunk_id) for chunk_id in gold.expected_chunk_ids}

    def path_supports_question(path: dict[str, Any]) -> bool:
        path_text = normalize_entity_label(json.dumps(path, sort_keys=True))
        path_chunk_ids = {str(chunk_id) for chunk_id in path.get("chunk_ids", [])}
        path_pages = {int(page) for page in path.get("pages", []) if page is not None}
        entity_match = any(entity and entity in path_text for entity in key_entities)
        relation_match = any(
            str(edge.get("predicate", "")) in expected_relations
            for edge in path.get("edges", [])
        )
        chunk_match = bool(expected_chunk_ids & path_chunk_ids)
        page_match = gold.source_page >= 0 and int(gold.source_page) in path_pages
        return entity_match or relation_match or chunk_match or page_match

    path_relevance = [path_supports_question(path) for path in paths]
    top_k = 5
    top_relevance = path_relevance[:top_k]
    supporting_paths = sum(int(relevant) for relevant in path_relevance)
    top_supporting_paths = sum(int(relevant) for relevant in top_relevance)

    return {
        "path_coverage": bool(paths),
        "path_count": len(paths),
        "path_hops": path_hops,
        "avg_path_length": round(sum(path_hops) / max(len(path_hops), 1), 4),
        "key_entity_coverage": round(
            len(set(covered_entities)) / max(len(set(key_entities)), 1),
            4,
        )
        if key_entities
        else (1.0 if paths or triples else 0.0),
        "key_entities_covered": sorted(set(covered_entities)),
        "relation_coverage": bool(relation_matches) if expected_relations else None,
        "relation_coverage_applicable": bool(expected_relations),
        "expected_relations": sorted(expected_relations),
        "matched_relations": sorted(relation_matches),
        "path_recall_at_5": 1.0 if top_supporting_paths else 0.0,
        "path_precision_at_5": round(top_supporting_paths / max(len(top_relevance), 1), 4),
        "supporting_path_rate": round(supporting_paths / max(len(paths), 1), 4),
        "irrelevant_path_rate": round(
            (len(paths) - supporting_paths) / max(len(paths), 1),
            4,
        ),
        "supporting_path_count": supporting_paths,
        "irrelevant_path_count": len(paths) - supporting_paths,
        "path_relevance_method": "heuristic_key_entity_relation_or_gold_chunk_overlap",
        "requires_model_review": True,
        "human_review": False,
    }


def _path_summary(paths: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "path_id": str(path.get("path_id", "")),
            "hops": path.get("hops"),
            "score": path.get("score"),
            "seed_nodes": path.get("seed_nodes", []),
            "seed_node_sources": path.get("seed_node_sources", {}),
            "chunk_ids": path.get("chunk_ids", []),
            "pages": path.get("pages", []),
            "nodes": [
                {
                    "node_id": str(node.get("node_id", "")),
                    "label": node.get("label"),
                    "class": node.get("class"),
                    "class_name": node.get("class_name"),
                }
                for node in path.get("nodes", [])
            ],
            "edges": [
                {
                    "triple_id": str(edge.get("triple_id", "")),
                    "predicate": edge.get("predicate"),
                    "chunk_id": edge.get("chunk_id"),
                    "page": edge.get("page"),
                    "source": edge.get("source"),
                    "target": edge.get("target"),
                }
                for edge in path.get("edges", [])
            ],
        }
        for path in paths
    ]


def _aggregate_path_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    denominator = len(records) or 1
    metrics = [record["metrics"]["graph_paths"] for record in records]
    all_hops = [hop for metric in metrics for hop in metric["path_hops"]]
    applicable_relations = [
        metric for metric in metrics if metric["relation_coverage_applicable"]
    ]
    relation_denominator = len(applicable_relations) or 1
    relation_coverage = (
        round(
            sum(int(metric["relation_coverage"]) for metric in applicable_relations)
            / relation_denominator,
            4,
        )
        if applicable_relations
        else None
    )
    return {
        "path_coverage": round(
            sum(int(metric["path_coverage"]) for metric in metrics) / denominator,
            4,
        ),
        "path_recall_at_5": round(
            sum(float(metric["path_recall_at_5"]) for metric in metrics) / denominator,
            4,
        ),
        "path_precision_at_5": round(
            sum(float(metric["path_precision_at_5"]) for metric in metrics) / denominator,
            4,
        ),
        "supporting_path_rate": round(
            sum(float(metric["supporting_path_rate"]) for metric in metrics) / denominator,
            4,
        ),
        "irrelevant_path_rate": round(
            sum(float(metric["irrelevant_path_rate"]) for metric in metrics) / denominator,
            4,
        ),
        "avg_path_length": round(sum(all_hops) / max(len(all_hops), 1), 4),
        "avg_returned_paths": round(
            sum(int(metric["path_count"]) for metric in metrics) / denominator,
            4,
        ),
        "key_entity_coverage": round(
            sum(float(metric["key_entity_coverage"]) for metric in metrics)
            / denominator,
            4,
        ),
        "relation_coverage": relation_coverage,
        "relation_questions_total": len(applicable_relations),
        "requires_model_review": True,
        "human_review": False,
        "path_relevance_method": "heuristic_key_entity_relation_or_gold_chunk_overlap",
    }


def _aggregate(records: list[dict[str, Any]]) -> dict[str, Any]:
    retrieval_records = [record["metrics"]["retrieval"] for record in records]
    path_records = [record["metrics"]["graph_paths"] for record in records]
    return {
        "retrieval": aggregate_retrieval_metrics(retrieval_records),
        "retrieval_confidence_intervals": {
            "recall_at_5": bootstrap_metric_ci(
                retrieval_records,
                lambda metric: bool(metric.get("recall_at_5", False)),
            ),
            "recall_at_10": bootstrap_metric_ci(
                retrieval_records,
                lambda metric: bool(metric.get("recall_at_10", False)),
            ),
            "mrr_at_5": bootstrap_metric_ci(
                retrieval_records,
                lambda metric: float(metric.get("mrr_at_5", 0.0)),
            ),
            "ndcg_at_10": bootstrap_metric_ci(
                retrieval_records,
                lambda metric: float(metric.get("ndcg_at_10", 0.0)),
            ),
        },
        "kg_evidence": aggregate_kg_evidence_metrics(
            [record["metrics"]["kg_evidence"] for record in records]
        ),
        "graph_paths": _aggregate_path_metrics(records),
        "graph_path_confidence_intervals": {
            "path_coverage": bootstrap_metric_ci(
                path_records,
                lambda metric: bool(metric.get("path_coverage", False)),
            ),
            "path_recall_at_5": bootstrap_metric_ci(
                path_records,
                lambda metric: float(metric.get("path_recall_at_5", 0.0)),
            ),
            "path_precision_at_5": bootstrap_metric_ci(
                path_records,
                lambda metric: float(metric.get("path_precision_at_5", 0.0)),
            ),
            "supporting_path_rate": bootstrap_metric_ci(
                path_records,
                lambda metric: float(metric.get("supporting_path_rate", 0.0)),
            ),
        },
    }


def _failure_categories(record: dict[str, Any]) -> list[str]:
    categories: list[str] = []
    retrieval_hit = bool(record["metrics"]["retrieval"]["recall_at_5"])
    path_metrics = record["metrics"]["graph_paths"]
    kg_metrics = record["metrics"]["kg_evidence"]
    graph_method = record["settings"]["graph_method"]
    mode = record["mode"]
    paths = record.get("graph_paths", [])
    seed_sources = {
        source
        for path in paths
        for source in path.get("seed_node_sources", {}).values()
    }
    predicates = {
        str(edge.get("predicate", ""))
        for path in paths
        for edge in path.get("edges", [])
    }
    low_value_predicates = {"appliesTo", "partOf", "hasCondition"}

    if graph_method == "traversal" and not path_metrics["path_coverage"]:
        categories.append("seed_linking_error")
    if "fallback" in seed_sources:
        categories.append("generic_seed_node")
    if path_metrics["path_coverage"] and not retrieval_hit:
        categories.append("path_found_but_wrong_chunk")
    if (predicates and predicates <= low_value_predicates) or (
        path_metrics["relation_coverage_applicable"]
        and not path_metrics["relation_coverage"]
    ):
        categories.append("low_value_predicate")
    if mode == "hybrid" and path_metrics["path_coverage"] and not retrieval_hit:
        categories.append("graph_fusion_dilution")
    if not kg_metrics["evidence_coverage"]:
        categories.append("kg_sparse_for_question")
    return categories


def _failure_cases(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for record in records:
        reasons: list[str] = []
        if not record["metrics"]["retrieval"]["recall_at_5"]:
            reasons.append("missed_gold_evidence_at_5")
        if (
            record["settings"]["graph_method"] == "traversal"
            and not record["metrics"]["graph_paths"]["path_coverage"]
        ):
            reasons.append("no_traversal_path_returned")
        if not record["metrics"]["kg_evidence"]["evidence_coverage"]:
            reasons.append("missing_kg_key_entity_evidence")
        categories = _failure_categories(record)
        if reasons or categories:
            failures.append(
                {
                    "cq_id": record["cq_id"],
                    "question": record["question"],
                    "reasons": reasons,
                    "failure_categories": categories,
                    "retrieved_chunks": record["metrics"]["retrieval"][
                        "retrieved_chunk_ids"
                    ],
                    "key_entities_covered": record["metrics"]["graph_paths"][
                        "key_entities_covered"
                    ],
                }
            )
    return failures


def build_graph_traversal_ablation(
    boundary_cq_path: str | Path,
    chunks_path: str | Path,
    kg_path: str | Path,
    index_dir: str | Path,
    *,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    gold_labels_path: str | Path | None = None,
    vector_top_k: int = 5,
    hybrid_top_k: int = 8,
    scenarios: tuple[dict[str, Any], ...] = DEFAULT_GRAPH_TRAVERSAL_SCENARIOS,
    query_runner: RetrievalRunner = run_retrieval,
    command: str = "aviation-ai report graph-traversal-ablation",
) -> dict[str, Any]:
    started = perf_counter()
    questions, gold_labels = load_questions_and_gold_labels(boundary_cq_path, gold_labels_path)
    scenario_results: dict[str, Any] = {}

    for scenario in scenarios:
        records: list[dict[str, Any]] = []
        for cq in questions:
            gold = gold_labels[str(cq["id"])]
            result = query_runner(
                cq["competency_question"],
                scenario["mode"],
                chunks_path,
                kg_path,
                index_dir,
                collection_name=collection_name,
                graph_hops=int(scenario["graph_hops"]),
                graph_method=scenario["graph_method"],
                graph_fusion_policy=scenario.get("graph_fusion_policy", "rrf"),
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
                "graph_paths": _record_path_metrics(
                    cq["competency_question"],
                    result,
                    gold,
                ),
            }
            records.append(
                {
                    "cq_id": cq["id"],
                    "question": cq["competency_question"],
                    "gold": gold.to_dict(),
                    "mode": scenario["mode"],
                    "settings": {
                        "graph_method": scenario["graph_method"],
                        "graph_hops": scenario["graph_hops"],
                        "graph_fusion_policy": scenario.get("graph_fusion_policy", "rrf"),
                        "vector_top_k": vector_top_k,
                        "hybrid_top_k": hybrid_top_k,
                    },
                    "metrics": metrics,
                    "hits": hit_summary(result.get("fused_chunks", [])),
                    "graph_triples": triple_summary(result.get("graph_triples", [])),
                    "graph_paths": _path_summary(result.get("graph_paths", [])[:10]),
                }
            )
        aggregate = _aggregate(records)
        scenario_results[scenario["name"]] = {
            "label": scenario["label"],
            "mode": scenario["mode"],
            "settings": {
                "graph_method": scenario["graph_method"],
                "graph_hops": scenario["graph_hops"],
                "graph_fusion_policy": scenario.get("graph_fusion_policy", "rrf"),
                "vector_top_k": vector_top_k,
                "hybrid_top_k": hybrid_top_k,
            },
            "aggregate": aggregate,
            "failure_cases": _failure_cases(records),
            "records": records,
        }

    run_manifest = build_run_manifest(
        "graph_traversal_ablation",
        parameters={
            "scenarios": [
                {
                    "name": scenario["name"],
                    "mode": scenario["mode"],
                    "graph_method": scenario["graph_method"],
                    "graph_hops": scenario["graph_hops"],
                    "graph_fusion_policy": scenario.get("graph_fusion_policy", "rrf"),
                }
                for scenario in scenarios
            ],
            "vector_top_k": vector_top_k,
            "hybrid_top_k": hybrid_top_k,
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
            "scoring_policy": "layered_retrieval_kg_path_metrics_no_mixed_overall_score",
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


def write_graph_traversal_ablation_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    return write_json_report(result, output_path)


def write_graph_traversal_ablation_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Graph Traversal Ablation",
        "",
        f"- Run ID: `{result['metadata']['run_manifest']['run_id']}`",
        f"- Questions: {result['metadata']['questions_total']}",
        f"- Scenarios: {result['metadata']['scenarios_total']}",
        "- Scoring: retrieval, KG evidence, and graph path metrics are kept separate.",
        "",
        "| Scenario | Recall@5 | Recall@10 | MRR@5 | NDCG@10 | Context Precision@5 | "
        "KG coverage | Path coverage | Path Recall@5 | Path Precision@5 | "
        "Supporting path rate | Irrelevant path rate | Key entity coverage | "
        "Relation coverage | Failures |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for scenario in result["scenarios"].values():
        retrieval = scenario["aggregate"]["retrieval"]
        kg = scenario["aggregate"]["kg_evidence"]
        paths = scenario["aggregate"]["graph_paths"]
        relation = paths["relation_coverage"]
        relation_text = "n/a" if relation is None else str(relation)
        lines.append(
            f"| {scenario['label']} | {retrieval['recall_at_5']} | "
            f"{retrieval['recall_at_10']} | {retrieval['mrr_at_5']} | "
            f"{retrieval['ndcg_at_10']} | {retrieval['context_precision_at_5']} | "
            f"{kg['evidence_coverage']} | {paths['path_coverage']} | "
            f"{paths['path_recall_at_5']} | {paths['path_precision_at_5']} | "
            f"{paths['supporting_path_rate']} | {paths['irrelevant_path_rate']} | "
            f"{paths['key_entity_coverage']} | {relation_text} | "
            f"{len(scenario['failure_cases'])} |"
        )

    lines.extend(
        [
            "",
            "## Confidence Intervals",
            "",
            "| Scenario | Metric | Mean | 95% CI | n |",
            "| --- | --- | ---: | --- | ---: |",
        ]
    )
    for scenario_name, scenario in result["scenarios"].items():
        ci_groups = {
            "retrieval": scenario["aggregate"].get("retrieval_confidence_intervals", {}),
            "heuristic_path": scenario["aggregate"].get("graph_path_confidence_intervals", {}),
        }
        for group_name, ci in ci_groups.items():
            for metric, values in ci.items():
                lines.append(
                    f"| {scenario_name} | {group_name}.{metric} | {values.get('mean')} | "
                    f"{values.get('lower')} - {values.get('upper')} | {values.get('n')} |"
                )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "Lexical graph search remains the baseline. Traversal metrics describe whether "
            "bounded KG paths were returned and whether they cover named entities or relation "
            "intent; they do not imply better retrieval unless Recall@5/MRR@5 support that.",
            "",
            "Traversal is interpreted as diagnostic path evidence and explainability support, "
            "not as current proof of retrieval superiority over lexical or vector retrieval.",
            "",
            "High path coverage with low standalone Recall@5 usually means traversal can find "
            "connected KG paths, but the chunks attached to those paths are not necessarily "
            "the gold evidence chunks. This can happen through seed linking errors, generic "
            "seed nodes, low-value predicates, sparse KG coverage for the question, or graph "
            "fusion dilution when graph chunks displace stronger vector hits.",
            "",
            "Path Recall@5, Path Precision@5, Supporting Path Rate, and Irrelevant Path Rate "
            "are deterministic heuristics based on key-entity, relation-intent, source-page, "
            "and gold-chunk overlap. They require manual path relevance review before being "
            "treated as semantic path-correctness evidence.",
            "",
            "## Failure Cases",
            "",
        ]
    )
    for scenario_name, scenario in result["scenarios"].items():
        lines.extend([f"### {scenario_name}", ""])
        failures = scenario["failure_cases"][:10]
        if not failures:
            lines.extend(["No failure cases under the recorded checks.", ""])
            continue
        for failure in failures:
            categories = ", ".join(failure.get("failure_categories", []))
            reasons = ", ".join(failure["reasons"])
            detail = "; ".join(part for part in [reasons, categories] if part)
            lines.append(f"- `{failure['cq_id']}`: {reasons}")
            if categories:
                lines[-1] = f"- `{failure['cq_id']}`: {detail}"
        lines.append("")

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_graph_traversal_ablation(
    boundary_cq_path: str | Path,
    chunks_path: str | Path,
    kg_path: str | Path,
    index_dir: str | Path,
    output_dir: str | Path,
    *,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    gold_labels_path: str | Path | None = None,
    vector_top_k: int = 5,
    hybrid_top_k: int = 8,
    scenarios: tuple[dict[str, Any], ...] = DEFAULT_GRAPH_TRAVERSAL_SCENARIOS,
    query_runner: RetrievalRunner = run_retrieval,
    report_name: str = "graph_traversal_ablation",
    command: str = "aviation-ai report graph-traversal-ablation",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_graph_traversal_ablation(
        boundary_cq_path,
        chunks_path,
        kg_path,
        index_dir,
        collection_name=collection_name,
        gold_labels_path=gold_labels_path,
        vector_top_k=vector_top_k,
        hybrid_top_k=hybrid_top_k,
        scenarios=scenarios,
        query_runner=query_runner,
        command=command,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "graph_traversal_ablation"
    json_path = write_graph_traversal_ablation_json(result, output / f"{stem}.json")
    md_path = write_graph_traversal_ablation_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
