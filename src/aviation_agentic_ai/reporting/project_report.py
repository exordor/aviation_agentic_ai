from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from aviation_agentic_ai.advisory import ADVISORY_BOUNDARY
from aviation_agentic_ai.config import load_yaml
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.hygiene import build_hygiene_plan
from aviation_agentic_ai.reporting.thesis_claims import REVISED_THESIS_CLAIM


PROJECT_REPORT_SECTIONS = (
    "Project motivation and course objective alignment",
    "Thesis claim positioning",
    "Architecture overview",
    "Ontology/TBox generation and evaluation",
    "KG/ABox extraction and validation",
    "Chunking comparison design",
    "Hybrid RAG protocol and layered metrics",
    "Current results and limitations",
    "Advisory assistant boundary",
    "Next work plan",
    "Reproducibility appendix",
)

LLMRunner = Callable[[str, float, int], str]


def _read_text_source(
    path: Path,
    *,
    base: str | Path = PROJECT_ROOT,
    max_chars: int = 4000,
) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": project_relative_path(path, base=base),
            "present": False,
            "excerpt": "",
        }
    text = path.read_text(encoding="utf-8")
    return {
        "path": project_relative_path(path, base=base),
        "present": True,
        "excerpt": text[:max_chars],
        "truncated": len(text) > max_chars,
    }


def _read_binary_source(path: Path, *, base: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": project_relative_path(path, base=base),
            "present": False,
            "binary": True,
            "size_bytes": 0,
        }
    return {
        "path": project_relative_path(path, base=base),
        "present": True,
        "binary": True,
        "format": path.suffix.removeprefix(".") or "binary",
        "size_bytes": path.stat().st_size,
        "excerpt": "",
    }


def _read_yaml_source(path: Path, *, base: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": project_relative_path(path, base=base),
            "present": False,
            "data": {},
        }
    return {
        "path": project_relative_path(path, base=base),
        "present": True,
        "data": load_yaml(path),
    }


def _compact_chunking_report(data: dict[str, Any]) -> dict[str, Any]:
    strategies: dict[str, Any] = {}
    for name, strategy in data.get("strategies", {}).items():
        if not isinstance(strategy, dict):
            continue
        records = strategy.get("records", [])
        strategies[name] = {
            "aggregate": strategy.get("aggregate", {}),
            "chunks_path": strategy.get("chunks_path"),
            "collection_name": strategy.get("collection_name"),
            "explanation": strategy.get("explanation"),
            "recommendation": strategy.get("recommendation"),
            "records_total": len(records) if isinstance(records, list) else "unknown",
            "tradeoff": strategy.get("tradeoff"),
        }
    return {
        "metadata": data.get("metadata", {}),
        "ranking": data.get("ranking", []),
        "strategies": strategies,
        "source_compaction": "strategy records and retrieved chunk texts omitted",
    }


def _compact_hybrid_record(record: dict[str, Any]) -> dict[str, Any]:
    compact_results: dict[str, Any] = {}
    for mode, result in record.get("results", {}).items():
        if not isinstance(result, dict):
            continue
        metrics = result.get("metrics", {})
        retrieval = metrics.get("retrieval", {}) if isinstance(metrics, dict) else {}
        compact_results[mode] = {
            "metrics": metrics,
            "matched_chunk_ids": retrieval.get("matched_chunk_ids", []),
            "matched_source_pages": retrieval.get("matched_source_pages", []),
            "retrieved_chunk_ids": retrieval.get("retrieved_chunk_ids", []),
            "retrieved_source_pages": retrieval.get("retrieved_source_pages", []),
        }
    gold = record.get("gold", {})
    return {
        "cq_id": record.get("cq_id"),
        "gold_level": gold.get("gold_level") if isinstance(gold, dict) else None,
        "key_entities": record.get("key_entities", []),
        "question": record.get("question"),
        "results": compact_results,
        "source_page": record.get("source_page"),
    }


def _compact_hybrid_report(data: dict[str, Any]) -> dict[str, Any]:
    records = data.get("records", [])
    return {
        "aggregate": data.get("aggregate", {}),
        "metadata": data.get("metadata", {}),
        "records": [
            _compact_hybrid_record(record)
            for record in records
            if isinstance(record, dict)
        ],
        "records_total": len(records) if isinstance(records, list) else "unknown",
        "source_compaction": "prompts, answers, triples, and full retrieved chunk texts omitted",
    }


def _compact_retrieval_ablation_report(data: dict[str, Any]) -> dict[str, Any]:
    scenarios: dict[str, Any] = {}
    for name, scenario in data.get("scenarios", {}).items():
        if not isinstance(scenario, dict):
            continue
        records = scenario.get("records", [])
        scenarios[name] = {
            "mode": scenario.get("mode"),
            "settings": scenario.get("settings", {}),
            "aggregate": scenario.get("aggregate", {}),
            "explanation": scenario.get("explanation", ""),
            "records_total": len(records) if isinstance(records, list) else "unknown",
        }
    return {
        "metadata": data.get("metadata", {}),
        "scenarios": scenarios,
        "source_compaction": "per-question hits and graph triples omitted",
    }


def _compact_graph_traversal_ablation_report(data: dict[str, Any]) -> dict[str, Any]:
    scenarios: dict[str, Any] = {}
    for name, scenario in data.get("scenarios", {}).items():
        if not isinstance(scenario, dict):
            continue
        records = scenario.get("records", [])
        failure_cases = scenario.get("failure_cases", [])
        scenarios[name] = {
            "mode": scenario.get("mode"),
            "settings": scenario.get("settings", {}),
            "aggregate": scenario.get("aggregate", {}),
            "failure_cases_total": (
                len(failure_cases) if isinstance(failure_cases, list) else "unknown"
            ),
            "records_total": len(records) if isinstance(records, list) else "unknown",
        }
    return {
        "metadata": data.get("metadata", {}),
        "scenarios": scenarios,
        "source_compaction": "per-question paths, hits, and failure-case details omitted",
    }


def _compact_answer_evaluation_report(data: dict[str, Any]) -> dict[str, Any]:
    records = data.get("records", {})
    return {
        "metadata": data.get("metadata", {}),
        "aggregate": data.get("aggregate", {}),
        "records_total_by_mode": {
            mode: len(items) if isinstance(items, list) else "unknown"
            for mode, items in records.items()
        }
        if isinstance(records, dict)
        else {},
        "source_compaction": "answer text and per-question details omitted",
    }


def _compact_robustness_report(data: dict[str, Any]) -> dict[str, Any]:
    records = data.get("records", [])
    return {
        "metadata": data.get("metadata", {}),
        "aggregate": data.get("aggregate", {}),
        "case_summaries": [
            {
                "case_id": record.get("case_id"),
                "base_cq_id": record.get("base_cq_id"),
                "case_type": record.get("case_type"),
                "expected_abstention": record.get("expected_abstention"),
                "metrics": record.get("metrics", {}),
            }
            for record in records
            if isinstance(record, dict)
        ],
        "records_total": len(records) if isinstance(records, list) else "unknown",
        "source_compaction": "retrieved chunks, triples, and generated answers omitted",
    }


def _compact_json_data(path: Path, data: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if path.name == "chunking_comparison.json":
        return _compact_chunking_report(data), True
    if path.name.startswith("hybrid_rag") and path.suffix == ".json":
        return _compact_hybrid_report(data), True
    if path.name.startswith("retrieval_ablation") and path.suffix == ".json":
        return _compact_retrieval_ablation_report(data), True
    if path.name.startswith("graph_traversal_ablation") and path.suffix == ".json":
        return _compact_graph_traversal_ablation_report(data), True
    if path.name == "answer_evaluation.json":
        return _compact_answer_evaluation_report(data), True
    if path.name == "robustness_evaluation.json":
        return _compact_robustness_report(data), True
    return data, False


def _read_json_source(path: Path, *, base: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": project_relative_path(path, base=base),
            "present": False,
            "data": {},
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    data = data if isinstance(data, dict) else {"value": data}
    compacted_data, compacted = _compact_json_data(path, data)
    return {
        "path": project_relative_path(path, base=base),
        "present": True,
        "data": compacted_data,
        "compacted": compacted,
    }


def _read_artifact_source(path: Path, *, base: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    if path.suffix == ".json":
        return _read_json_source(path, base=base)
    if path.suffix in {".yaml", ".yml"}:
        return _read_yaml_source(path, base=base)
    if path.suffix.lower() in {".pptx", ".pdf", ".png", ".jpg", ".jpeg", ".webp"}:
        return _read_binary_source(path, base=base)
    return _read_text_source(path, base=base, max_chars=8000)


def _read_course_goal_source(root: Path) -> dict[str, Any]:
    goals = root / "GOALS.md"
    if goals.exists():
        return _read_text_source(goals, base=root)
    return _read_text_source(root / "tmp" / "goal.md", base=root)


def _read_current_artifacts(
    root: Path,
    current_artifacts: dict[str, Any],
) -> dict[str, Any]:
    sources: dict[str, Any] = {}
    for key, rel_path in current_artifacts.items():
        if not isinstance(rel_path, str):
            continue
        path = root / rel_path
        sources[key] = _read_artifact_source(path, base=root)
        if path.suffix == ".md":
            json_path = path.with_suffix(".json")
            if json_path.exists():
                sources[f"{key}_json"] = _read_json_source(json_path, base=root)
    return sources


def _read_thesis_ready_artifacts(root: Path) -> dict[str, Any]:
    paths = {
        "benchmark_v2_summary": root / "reports" / "stages" / "benchmark_v2_summary.md",
        "benchmark_v2_summary_json": root / "reports" / "stages" / "benchmark_v2_summary.json",
        "benchmark_review_pack": root / "reports" / "stages" / "benchmark_review_pack.md",
        "benchmark_review_pack_json": root / "reports" / "stages" / "benchmark_review_pack.json",
        "retrieval_ablation_benchmark_v2": root
        / "reports"
        / "stages"
        / "retrieval_ablation_benchmark_v2.md",
        "retrieval_ablation_benchmark_v2_json": root
        / "reports"
        / "stages"
        / "retrieval_ablation_benchmark_v2.json",
        "graph_traversal_ablation_benchmark_v2": root
        / "reports"
        / "stages"
        / "graph_traversal_ablation_benchmark_v2.md",
        "graph_traversal_ablation_benchmark_v2_json": root
        / "reports"
        / "stages"
        / "graph_traversal_ablation_benchmark_v2.json",
        "sufficiency_evaluation": root / "reports" / "stages" / "sufficiency_evaluation.md",
        "sufficiency_evaluation_json": root
        / "reports"
        / "stages"
        / "sufficiency_evaluation.json",
        "benchmark_reviewed_subset_summary": root
        / "reports"
        / "stages"
        / "benchmark_reviewed_subset_summary.md",
        "benchmark_reviewed_subset_summary_json": root
        / "reports"
        / "stages"
        / "benchmark_reviewed_subset_summary.json",
        "answer_evaluation_benchmark_subset": root
        / "reports"
        / "stages"
        / "answer_evaluation_benchmark_subset.md",
        "answer_evaluation_benchmark_subset_json": root
        / "reports"
        / "stages"
        / "answer_evaluation_benchmark_subset.json",
        "triple_semantic_review": root / "reports" / "stages" / "triple_semantic_review.md",
        "triple_semantic_review_json": root
        / "reports"
        / "stages"
        / "triple_semantic_review_sample.json",
        "evaluation_protocol_review": root
        / "reports"
        / "stages"
        / "evaluation_protocol_review.md",
        "evaluation_protocol_review_json": root
        / "reports"
        / "stages"
        / "evaluation_protocol_review.json",
        "thesis_experiment_dashboard": root
        / "reports"
        / "stages"
        / "thesis_experiment_dashboard.md",
        "thesis_experiment_dashboard_json": root
        / "reports"
        / "stages"
        / "thesis_experiment_dashboard.json",
    }
    return {key: _read_artifact_source(path, base=root) for key, path in paths.items()}


def build_project_evidence_pack(
    *,
    project_root: str | Path = PROJECT_ROOT,
    stage_index_path: str | Path | None = None,
    stage_dir: str | Path | None = None,
    reviews_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(project_root)
    stages = Path(stage_dir) if stage_dir is not None else root / "reports" / "stages"
    reviews = Path(reviews_dir) if reviews_dir is not None else root / "reports" / "reviews"
    index_path = Path(stage_index_path) if stage_index_path is not None else stages / "index.json"
    if index_path.exists():
        stage_index = _read_json_source(index_path, base=root)
    else:
        stage_index = {
            "path": project_relative_path(index_path, base=root),
            "present": False,
            "data": build_hygiene_plan(
                stages,
                root / "reports" / "archive",
                reviews,
                base=root,
            ),
        }
    current_artifacts = stage_index.get("data", {}).get("current_active_artifacts", {})
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "report_sections": list(PROJECT_REPORT_SECTIONS),
        "advisory_boundary": ADVISORY_BOUNDARY,
        "stage_index": stage_index,
        "current_artifacts": _read_current_artifacts(root, current_artifacts)
        if isinstance(current_artifacts, dict)
        else {},
        "thesis_ready_artifacts": _read_thesis_ready_artifacts(root),
        "readme": _read_text_source(root / "README.md", base=root),
        "goals": _read_text_source(root / "GOALS.md", base=root),
        "tasks": _read_text_source(root / "TASKS.md", base=root),
        "thesis_positioning": _read_text_source(
            root / "docs" / "thesis_positioning.md",
            base=root,
        ),
        "thesis_claims_review": _read_artifact_source(
            root / "reports" / "stages" / "thesis_claims_review.md",
            base=root,
        ),
        "course_goal": _read_course_goal_source(root),
        "configs": {
            "default": _read_yaml_source(root / "configs" / "default.yaml", base=root),
            "ontology_generation": _read_yaml_source(
                root / "configs" / "ontology_generation.yaml",
                base=root,
            ),
            "extraction_profile": _read_yaml_source(
                root / "configs" / "extraction_profile.yaml",
                base=root,
            ),
        },
        "source_policy": {
            "env_files_read": False,
            "secrets_allowed": False,
            "missing_results_policy": "Use TBD / Not yet run; do not invent results.",
        },
    }


def _present_marker(source: dict[str, Any]) -> str:
    return "present" if source.get("present") else "missing"


def _metric_value(data: dict[str, Any], *keys: str, default: str = "TBD") -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _chunking_summary_lines(
    artifact_sources: dict[str, Any],
    categories: dict[str, Any],
) -> list[str]:
    report = artifact_sources.get("chunking_comparison")
    data = artifact_sources.get("chunking_comparison_json", {}).get("data", {})
    if not isinstance(data, dict) or not data:
        return [
            f"RAG experiment artifacts listed: {len(categories.get('rag_experiments', []))}. "
            "Chunking comparison should discuss retrieval tradeoffs rather than collapse "
            "them into a single score.",
        ]

    ranking = data.get("ranking", [])
    strategies = data.get("strategies", {})
    metadata = data.get("metadata", {})
    best = ranking[0] if ranking and isinstance(ranking[0], dict) else {}
    best_name = best.get("strategy", "TBD")
    fixed = strategies.get("fixed_window", {}) if isinstance(strategies, dict) else {}
    fixed_retrieval = _metric_value(fixed, "aggregate", "retrieval", default={})
    fixed_chunking = _metric_value(fixed, "aggregate", "chunking", default={})
    best_strategy = strategies.get(best_name, {}) if isinstance(strategies, dict) else {}
    best_chunking = _metric_value(best_strategy, "aggregate", "chunking", default={})
    report_path = report.get("path", "reports/stages/chunking_comparison.md") if report else "TBD"
    return [
        f"Chunking comparison evidence: `{report_path}`. It evaluated "
        f"{metadata.get('questions_total', 'TBD')} boundary CQs across "
        f"{len(strategies) if isinstance(strategies, dict) else 'TBD'} strategies.",
        f"Best chunking strategy: {best_name} with Recall@5="
        f"{best.get('recall_at_5', 'TBD')}, MRR@5={best.get('mrr_at_5', 'TBD')}, "
        f"and Context Precision@5={best.get('context_precision_at_5', 'TBD')}.",
        "Fixed-window remains the KG-aligned strategy for the current Hybrid RAG run: "
        f"Recall@5={fixed_retrieval.get('recall_at_5', 'TBD')}, "
        f"MRR@5={fixed_retrieval.get('mrr_at_5', 'TBD')}, Context Precision@5="
        f"{fixed_retrieval.get('context_precision_at_5', 'TBD')}, chunks="
        f"{fixed_chunking.get('chunk_count', 'TBD')}.",
        f"Interpretation: {best_name} improves ranking quality and context precision by "
        "preserving handbook structure, but its finer granularity increases chunk count "
        f"to {best_chunking.get('chunk_count', 'TBD')}. It is a candidate for future "
        "KG re-extraction rather than being mixed with the current fixed-window KG.",
    ]


def _hybrid_summary_lines(
    artifact_sources: dict[str, Any],
    retrieval_config: dict[str, Any],
) -> list[str]:
    report = artifact_sources.get("hybrid_rag_experiment")
    data = artifact_sources.get("hybrid_rag_experiment_json", {}).get("data", {})
    if not isinstance(data, dict) or not data:
        return [
            "Hybrid RAG uses separate retrieval, KG evidence, and LLM answer metrics. "
            f"Configured retrieval defaults include vector_top_k="
            f"{retrieval_config.get('vector_top_k', 'TBD')}, graph_hops="
            f"{retrieval_config.get('graph_hops', 'TBD')}, and hybrid_top_k="
            f"{retrieval_config.get('hybrid_top_k', 'TBD')}.",
        ]

    metadata = data.get("metadata", {})
    aggregate = data.get("aggregate", {})
    vector = aggregate.get("vector", {})
    graph = aggregate.get("graph", {})
    hybrid = aggregate.get("hybrid", {})
    lift = aggregate.get("hybrid_lift", {})
    manifest = metadata.get("run_manifest", {})
    llm = manifest.get("llm", {}) if isinstance(manifest, dict) else {}
    report_path = report.get("path", "reports/stages/hybrid_rag_experiment.md") if report else "TBD"
    lines = [
        f"Hybrid RAG evidence: `{report_path}`. It evaluated "
        f"{metadata.get('questions_total', 'TBD')} boundary CQs using "
        f"`{metadata.get('chunking_strategy', 'TBD')}` chunks, collection "
        f"`{metadata.get('collection_name', 'TBD')}`, and LLM "
        f"{llm.get('provider', 'TBD')}/{llm.get('model', 'TBD')}.",
        "Retrieval metrics: vector Recall@5="
        f"{_metric_value(vector, 'retrieval', 'recall_at_5')}, graph Recall@5="
        f"{_metric_value(graph, 'retrieval', 'recall_at_5')}, hybrid Recall@5="
        f"{_metric_value(hybrid, 'retrieval', 'recall_at_5')}; vector MRR@5="
        f"{_metric_value(vector, 'retrieval', 'mrr_at_5')}, graph MRR@5="
        f"{_metric_value(graph, 'retrieval', 'mrr_at_5')}, hybrid MRR@5="
        f"{_metric_value(hybrid, 'retrieval', 'mrr_at_5')}.",
        "KG evidence metrics: graph coverage="
        f"{_metric_value(graph, 'kg_evidence', 'evidence_coverage')}, hybrid coverage="
        f"{_metric_value(hybrid, 'kg_evidence', 'evidence_coverage')}, hybrid provenance "
        f"complete={_metric_value(hybrid, 'kg_evidence', 'provenance_complete_rate')}, "
        f"hybrid invalid triples={_metric_value(hybrid, 'kg_evidence', 'avg_invalid_triple_count')}.",
        "LLM answer metrics: vector citation completeness="
        f"{_metric_value(vector, 'llm_answer', 'citation_completeness')}, graph="
        f"{_metric_value(graph, 'llm_answer', 'citation_completeness')}, hybrid="
        f"{_metric_value(hybrid, 'llm_answer', 'citation_completeness')}; hybrid "
        "insufficient-evidence abstention="
        f"{_metric_value(hybrid, 'llm_answer', 'insufficient_evidence_abstention')}.",
        "Hybrid lift is reported as layered evidence, not a mixed total score: "
        f"vs vector Recall@5={lift.get('vs_vector_recall_at_5', 'TBD')}, "
        f"vs graph Recall@5={lift.get('vs_graph_recall_at_5', 'TBD')}.",
    ]
    structure_report = artifact_sources.get("hybrid_rag_structure_aware")
    structure_data = artifact_sources.get("hybrid_rag_structure_aware_json", {}).get("data", {})
    if isinstance(structure_data, dict) and structure_data:
        structure_metadata = structure_data.get("metadata", {})
        structure_aggregate = structure_data.get("aggregate", {})
        structure_hybrid = structure_aggregate.get("hybrid", {})
        structure_lift = structure_aggregate.get("hybrid_lift", {})
        structure_path = structure_report.get("path", "reports/stages/hybrid_rag_structure_aware.md")
        lines.append(
            f"Structure-aware Hybrid RAG evidence: `{structure_path}`. It evaluated "
            f"{structure_metadata.get('questions_total', 'TBD')} boundary CQs with hybrid "
            f"Recall@5={_metric_value(structure_hybrid, 'retrieval', 'recall_at_5')}, "
            "KG evidence coverage="
            f"{_metric_value(structure_hybrid, 'kg_evidence', 'evidence_coverage')}, "
            "and lift vs vector Recall@5="
            f"{structure_lift.get('vs_vector_recall_at_5', 'TBD')}."
        )
    review = artifact_sources.get("graphrag_review")
    if review and review.get("present"):
        lines.append(
            f"GraphRAG interpretation evidence: `{review.get('path')}` explains "
            "retrieval, KG evidence, and LLM answer behavior separately."
        )
    evidence_report = artifact_sources.get("evidence_level_evaluation")
    evidence_data = artifact_sources.get("evidence_level_evaluation_json", {}).get("data", {})
    if isinstance(evidence_data, dict) and evidence_data:
        fixed_hybrid = _metric_value(
            evidence_data,
            "experiments",
            "fixed_window",
            "aggregate",
            "hybrid",
            default={},
        )
        structure_hybrid = _metric_value(
            evidence_data,
            "experiments",
            "structure_aware",
            "aggregate",
            "hybrid",
            default={},
        )
        structure_support = structure_hybrid.get("answer_support_distribution", {})
        fixed_support = fixed_hybrid.get("answer_support_distribution", {})
        lines.append(
            "Evidence-level evaluation: "
            f"`{evidence_report.get('path', 'reports/stages/evidence_level_evaluation.md')}` "
            f"shows structure-aware hybrid span hit rate="
            f"{structure_hybrid.get('span_hit_rate', 'TBD')} and supported answers="
            f"{structure_support.get('supported', 'TBD')}; fixed-window hybrid span hit rate="
            f"{fixed_hybrid.get('span_hit_rate', 'TBD')} and supported answers="
            f"{fixed_support.get('supported', 'TBD')}."
        )
    return lines


def _experimental_expansion_lines(artifact_sources: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    expanded_source = artifact_sources.get("expanded_gold_labels_json") or artifact_sources.get(
        "expanded_gold_labels",
        {},
    )
    expanded = expanded_source.get("data", {}) if isinstance(expanded_source, dict) else {}
    if isinstance(expanded, dict) and expanded:
        labels = expanded.get("labels", [])
        no_answer = [
            item
            for item in labels
            if isinstance(item, dict) and item.get("expected_abstention")
        ]
        lines.append(
            "Expanded evaluation labels: "
            f"{len(labels) if isinstance(labels, list) else 'TBD'} questions, including "
            f"{len(no_answer)} insufficient-evidence/no-answer cases."
        )
    retrieval = artifact_sources.get("retrieval_ablation_json", {}).get("data", {})
    if isinstance(retrieval, dict) and retrieval:
        scenarios = retrieval.get("scenarios", {})
        vector = _metric_value(
            scenarios,
            "vector_hops2_v5_h8",
            "aggregate",
            "retrieval",
            default={},
        )
        graph_disabled = _metric_value(
            scenarios,
            "hybrid_graph_disabled_hops2_v5_h8",
            "aggregate",
            "retrieval",
            default={},
        )
        hybrid = _metric_value(
            scenarios,
            "hybrid_hops2_v5_h8",
            "aggregate",
            "retrieval",
            default={},
        )
        lines.append(
            "Retrieval ablation: "
            f"{retrieval.get('metadata', {}).get('scenarios_total', 'TBD')} scenarios over "
            f"{retrieval.get('metadata', {}).get('questions_total', 'TBD')} questions; "
            f"vector Recall@5={vector.get('recall_at_5', 'TBD')}, graph-disabled hybrid "
            f"Recall@5={graph_disabled.get('recall_at_5', 'TBD')}, and default hybrid "
            f"Recall@5={hybrid.get('recall_at_5', 'TBD')}."
        )
    kg = artifact_sources.get("kg_extraction_comparison_json", {}).get("data", {})
    if isinstance(kg, dict) and kg:
        fixed = kg.get("experiments", {}).get("fixed_window", {})
        structure = kg.get("experiments", {}).get("structure_aware", {})
        lines.append(
            "KG extraction comparison: fixed-window valid triples="
            f"{fixed.get('valid_triples', 'TBD')} with key-entity coverage="
            f"{fixed.get('key_entity_coverage', 'TBD')}; structure-aware valid triples="
            f"{structure.get('valid_triples', 'TBD')} with key-entity coverage="
            f"{structure.get('key_entity_coverage', 'TBD')}."
        )
    answer = artifact_sources.get("answer_evaluation_json", {}).get("data", {})
    if isinstance(answer, dict) and answer:
        hybrid = answer.get("aggregate", {}).get("hybrid", {})
        lines.append(
            "Answer evaluation: hybrid citation completeness="
            f"{hybrid.get('citation_completeness', 'TBD')}, citation correctness="
            f"{hybrid.get('citation_correctness', 'TBD')}, answer faithfulness="
            f"{hybrid.get('answer_faithfulness', 'TBD')}, advisory-boundary violations="
            f"{hybrid.get('advisory_boundary_violation_count', 'TBD')}."
        )
    robustness = artifact_sources.get("robustness_evaluation_json", {}).get("data", {})
    if isinstance(robustness, dict) and robustness:
        aggregate = robustness.get("aggregate", {})
        lines.append(
            "Robustness evaluation: retrieval stability="
            f"{aggregate.get('retrieval_stability', 'TBD')}, citation stability="
            f"{aggregate.get('citation_stability', 'TBD')}, abstention correctness="
            f"{aggregate.get('abstention_correctness', 'TBD')}."
        )
    return lines


def _dashboard_project_report(evidence: dict[str, Any], dashboard: dict[str, Any]) -> str:
    primary = dashboard.get("primary_results", {})
    rq_rows = dashboard.get("rq_to_evidence_matrix", [])
    dataset_rows = dashboard.get("dataset_usage_matrix", [])
    checks = dashboard.get("consistency_checks", {})
    failure = dashboard.get("failure_mode_summary", {})
    vector = primary.get("vector_only", {})
    hybrid = primary.get("best_lexical_hybrid", {})
    traversal = primary.get("traversal_hybrid", {})
    sufficiency = primary.get("sufficiency", {})
    robustness = primary.get("robustness", {})
    reviewed_subset = primary.get("benchmark_reviewed_subset", {})
    answer_subset = primary.get("answer_evaluation_benchmark_subset", {})
    kg = primary.get("kg", {})
    triple = primary.get("triple_semantic_review", {})
    lines = [
        "# Aviation Agentic AI Project Report",
        "",
        "## Research claim and scope",
        "",
        REVISED_THESIS_CLAIM,
        "",
        "This deterministic report is organized by research questions and uses "
        "`reports/stages/thesis_experiment_dashboard.json` as the main evidence "
        "source. The dashboard aggregates existing reports without recomputing "
        "experiments. It keeps retrieval, graph evidence, answer quality, ontology/KG "
        "quality, and safety-abstention metrics separate; no mixed overall score is "
        "created.",
        "",
        "Scope boundary: " + evidence["advisory_boundary"],
        "",
        "## Dataset and benchmark",
        "",
    ]
    for row in dataset_rows:
        lines.append(
            f"- **{row.get('dataset')}**: {row.get('purpose')}; evidence role="
            f"`{row.get('evidence_role')}`; thesis main claim support="
            f"{row.get('can_support_thesis_main_claim')}; limitations: "
            f"{row.get('limitations')}."
        )
    lines.extend(
        [
            "",
            "Benchmark v2 is the main thesis retrieval and safety benchmark. The 10-CQ "
            "and 35-question sets remain pilot/demo evidence and must not be presented "
            "as the main thesis benchmark.",
            "",
            "## Evaluation protocol",
            "",
            "The evaluation protocol is defined in `docs/evaluation_protocol.md` and "
            "audited by `reports/stages/evaluation_protocol_review.json`. Primary "
            "metrics include Recall@5/@10, MRR@5/@10, NDCG@10, Precision@5, Context "
            "Precision@5, Context Recall, graph path metrics, citation metrics, KG "
            "validation metrics, and safety-abstention metrics.",
            "",
            "## RQ1: ontology-constrained KG extraction",
            "",
            f"Current KG evidence: structure-aware valid triples={kg.get('valid_triples')}, "
            f"provenance completeness={kg.get('provenance_completeness')}, "
            f"evidence-in-source rate={kg.get('evidence_in_source_rate')}, unsupported "
            f"triple count={kg.get('unsupported_triple_count')}. Triple semantic review "
            f"sample size={triple.get('sample_size')}, reviewed={triple.get('reviewed')}, "
            f"needs_review={triple.get('needs_review')}; no semantic correctness claim is "
            "made until manual annotations are completed.",
            "",
            "## RQ2: evidence traceability",
            "",
            "Evidence traceability is supported by KG provenance, citation metrics, and "
            "the dashboard inventory. Answer-level scores are deterministic heuristics "
            "unless an LLM-judge or manual review score is explicitly recorded.",
            "",
            "## RQ3: vector vs graph vs hybrid retrieval (Hybrid RAG protocol and layered metrics)",
            "",
            f"Benchmark v2 vector-only: Recall@5={vector.get('recall_at_5')}, "
            f"Recall@10={vector.get('recall_at_10')}, MRR@5={vector.get('mrr_at_5')}, "
            f"NDCG@10={vector.get('ndcg_at_10')}. Lexical hybrid: Recall@5="
            f"{hybrid.get('recall_at_5')}, Recall@10={hybrid.get('recall_at_10')}, "
            f"MRR@5={hybrid.get('mrr_at_5')}, NDCG@10={hybrid.get('ndcg_at_10')}, "
            f"Context Recall={hybrid.get('context_recall')}, KG evidence coverage="
            f"{hybrid.get('kg_evidence_coverage')}.",
            "",
            f"Traversal hybrid: Recall@5={traversal.get('recall_at_5')}, Path Recall@5="
            f"{traversal.get('path_recall_at_5')}, Path Precision@5="
            f"{traversal.get('path_precision_at_5')}. Path metrics are heuristic and "
            "require manual review. High path coverage is not treated as evidence of "
            "high retrieval quality unless Recall/MRR/NDCG also support that claim.",
            "",
            "## RQ4: safety-aware abstention",
            "",
            f"Benchmark v2 safety metrics: Abstention Accuracy="
            f"{sufficiency.get('abstention_accuracy')}, False Answer Rate="
            f"{sufficiency.get('false_answer_rate')}, False Abstention Rate="
            f"{sufficiency.get('false_abstention_rate')}, Risk Category Accuracy="
            f"{sufficiency.get('risk_category_accuracy')}. Sufficiency diagnostics show "
            "strong abstention on benchmark v2 no-answer labels, while "
            "robustness must also remain visible: false answer rate="
            f"{robustness.get('false_answer_rate')}, boundary violations="
            f"{robustness.get('advisory_boundary_violation_count')}.",
            "",
            "## Review-dependent evidence status",
            "",
            "Benchmark reviewed subset: labels="
            f"{reviewed_subset.get('labels_total')}, status="
            f"{reviewed_subset.get('review_status')}, external aviation expert review "
            f"completed={reviewed_subset.get('external_aviation_expert_certified')}. "
            "Answer-evaluation benchmark subset: answers="
            f"{answer_subset.get('answers_total')}, status="
            f"{answer_subset.get('evaluation_status')}, unmatched gold labels="
            f"{answer_subset.get('unmatched_gold_labels')}, hybrid faithfulness="
            f"{answer_subset.get('hybrid_faithfulness')}, score method="
            f"{answer_subset.get('score_method')}. These are not manual review results.",
            "",
            "## Failure analysis",
            "",
            f"Graph failure categories: {failure.get('graph_failure_categories', {})}.",
            f"False abstentions on supported questions: "
            f"{failure.get('false_abstention_on_supported_question', 'TBD')}.",
            f"Machine-seeded benchmark wording findings: "
            f"{failure.get('machine_seeded_benchmark_wording', 'TBD')}.",
            f"Missing manual triple review items: "
            f"{failure.get('missing_manual_triple_review', 'TBD')}.",
            "",
            "## Limitations",
            "",
            "Benchmark v2 is thesis/course-project evidence, not external aviation expert "
            "certification. Path relevance and triple semantic correctness remain "
            "manual-review dependent. The system is not operational flight software and "
            "does not replace official sources or pilot judgment.",
            "",
            "## Reproducibility appendix",
            "",
            "- `make validate`",
            "- `make reports-core`",
            "- `make reports-main-experiments`",
            "- `make reports-review`",
            "- `make thesis-dashboard`",
            "- `uv run aviation-ai report project --no-ai`",
            "- `uv run aviation-ai report academic-paper --no-ai`",
            "",
            "## Dashboard consistency checks",
            "",
        ]
    )
    for key, value in checks.items():
        if key != "unsafe_hits":
            lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## RQ evidence matrix",
            "",
        ]
    )
    for row in rq_rows:
        lines.append(
            f"- **{row.get('rq')}**: reports={row.get('evidence_reports')}; metrics="
            f"{row.get('primary_metrics')}; claim strength={row.get('claim_strength')}; "
            f"gaps={row.get('remaining_gaps')}."
        )
    lines.append("")
    return "\n".join(lines)


def build_project_report_draft(evidence: dict[str, Any]) -> str:
    stage_index = evidence.get("stage_index", {}).get("data", {})
    categories = stage_index.get("categories", {})
    current_artifacts = stage_index.get("current_active_artifacts", {})
    artifact_sources = evidence.get("current_artifacts", {})
    thesis_sources = evidence.get("thesis_ready_artifacts", {})
    dashboard = thesis_sources.get("thesis_experiment_dashboard_json", {}).get("data", {})
    if isinstance(dashboard, dict) and dashboard:
        return _dashboard_project_report(evidence, dashboard)
    curated_eval = artifact_sources.get("curated_ontology_evaluation_json", {}).get("data", {})
    kg_validation = artifact_sources.get("kg_validation_json", {}).get("data", {})
    structure_kg_validation = artifact_sources.get(
        "structure_aware_kg_validation_json", {}
    ).get("data", {})
    structural = curated_eval.get("structural_metrics", {}) if isinstance(curated_eval, dict) else {}
    judgment = curated_eval.get("judgment", {}) if isinstance(curated_eval, dict) else {}
    config_default = evidence.get("configs", {}).get("default", {}).get("data", {})
    retrieval_config = config_default.get("retrieval", {}) if isinstance(config_default, dict) else {}
    ontology_path = current_artifacts.get("active_ontology", "TBD")
    ontology_design = current_artifacts.get("ontology_design", "TBD")
    kg_path = kg_validation.get("kg_path", current_artifacts.get("validated_kg", "TBD"))
    kg_triples = kg_validation.get("triples_total", "TBD")
    kg_errors = kg_validation.get("errors_total", "TBD")
    structure_kg_path = structure_kg_validation.get(
        "kg_path",
        current_artifacts.get("structure_aware_kg", "TBD"),
    )
    structure_kg_triples = structure_kg_validation.get("triples_total", "TBD")
    structure_kg_errors = structure_kg_validation.get("errors_total", "TBD")
    web_readiness = artifact_sources.get("web_demo_readiness_json", {}).get("data", {})
    web_smoke = artifact_sources.get("web_demo_final_smoke_json", {}).get("data", {})
    final_evaluation = artifact_sources.get("final_evaluation_review_json", {}).get(
        "data",
        {},
    )
    web_explanation = (
        web_readiness.get("explanation", {}) if isinstance(web_readiness, dict) else {}
    )
    default_decision = (
        final_evaluation.get("default_strategy_decision", {})
        if isinstance(final_evaluation, dict)
        else {}
    )
    gold_review = (
        final_evaluation.get("gold_label_review", {})
        if isinstance(final_evaluation, dict)
        else {}
    )
    chunking_lines = _chunking_summary_lines(artifact_sources, categories)
    hybrid_lines = _hybrid_summary_lines(artifact_sources, retrieval_config)
    expansion_lines = _experimental_expansion_lines(artifact_sources)
    benchmark_v2 = thesis_sources.get("benchmark_v2_summary_json", {}).get("data", {})
    benchmark_review = thesis_sources.get("benchmark_review_pack_json", {}).get("data", {})
    retrieval_v2 = thesis_sources.get("retrieval_ablation_benchmark_v2_json", {}).get(
        "data",
        {},
    )
    traversal_v2 = thesis_sources.get(
        "graph_traversal_ablation_benchmark_v2_json",
        {},
    ).get("data", {})
    sufficiency = thesis_sources.get("sufficiency_evaluation_json", {}).get("data", {})
    triple_review = thesis_sources.get("triple_semantic_review_json", {}).get("data", {})
    benchmark_v2_lines: list[str] = []
    if isinstance(benchmark_v2, dict) and benchmark_v2:
        metadata = benchmark_v2.get("metadata", {})
        validation = benchmark_v2.get("validation", {})
        benchmark_v2_lines.append(
            "Benchmark v2 summary: "
            f"{metadata.get('labels_total', 'TBD')} labels, supported="
            f"{metadata.get('supported_total', 'TBD')}, insufficient-evidence="
            f"{metadata.get('no_answer_total', 'TBD')}, validation passed="
            f"{validation.get('valid', 'TBD')}, review status="
            f"`{metadata.get('review_status', 'TBD')}`."
        )
    if isinstance(benchmark_review, dict) and benchmark_review:
        finding_counts = benchmark_review.get("finding_counts", {})
        benchmark_v2_lines.append(
            "Benchmark manual-review pack: "
            f"{benchmark_review.get('metadata', {}).get('labels_total', 'TBD')} labels "
            "grouped by question type; automatic findings include "
            f"{finding_counts}. These are review prompts, not completed expert certification."
        )
    if isinstance(retrieval_v2, dict) and retrieval_v2:
        scenarios = retrieval_v2.get("scenarios", {})
        vector = _metric_value(
            scenarios,
            "vector_hops2_v5_h8",
            "aggregate",
            "retrieval",
            default={},
        )
        hybrid = _metric_value(
            scenarios,
            "hybrid_hops2_v5_h8",
            "aggregate",
            "retrieval",
            default={},
        )
        hybrid_kg = _metric_value(
            scenarios,
            "hybrid_hops2_v5_h8",
            "aggregate",
            "kg_evidence",
            default={},
        )
        benchmark_v2_lines.append(
            "Benchmark v2 retrieval ablation: vector Recall@5="
            f"{vector.get('recall_at_5', 'TBD')}, default hybrid Recall@5="
            f"{hybrid.get('recall_at_5', 'TBD')}, and hybrid KG evidence coverage="
            f"{hybrid_kg.get('evidence_coverage', 'TBD')}."
        )
    if isinstance(traversal_v2, dict) and traversal_v2:
        scenarios = traversal_v2.get("scenarios", {})
        traversal = _metric_value(
            scenarios,
            "traversal_graph_2_hop",
            "aggregate",
            default={},
        )
        guarded = _metric_value(
            scenarios,
            "hybrid_vector_traversal_guarded",
            "aggregate",
            default={},
        )
        benchmark_v2_lines.append(
            "Benchmark v2 graph traversal: 2-hop traversal path coverage="
            f"{_metric_value(traversal, 'graph_paths', 'path_coverage')}, standalone "
            f"Recall@5={_metric_value(traversal, 'retrieval', 'recall_at_5')}; guarded "
            "hybrid traversal Recall@5="
            f"{_metric_value(guarded, 'retrieval', 'recall_at_5')}."
        )
    if isinstance(sufficiency, dict) and sufficiency:
        metrics = sufficiency.get("metrics", {})
        benchmark_v2_lines.append(
            "Sufficiency evaluation: insufficient-evidence abstention accuracy="
            f"{metrics.get('insufficient_evidence_abstention_accuracy', 'TBD')}, "
            "false answer rate on no-answer questions="
            f"{metrics.get('false_answer_rate_on_no_answer_questions', 'TBD')}, "
            "false abstention rate on supported questions="
            f"{metrics.get('false_abstention_rate_on_supported_questions', 'TBD')}, "
            f"boundary violations={metrics.get('boundary_violation_count', 'TBD')}."
        )
    if isinstance(triple_review, dict) and triple_review:
        benchmark_v2_lines.append(
            "Triple semantic review sample: "
            f"{triple_review.get('metadata', {}).get('sample_size', 'TBD')} triples are "
            "prepared with all semantic annotation fields marked `needs_review`; no "
            "semantic-correctness claim is made."
        )
    has_chunking = bool(
        artifact_sources.get("chunking_comparison_json", {}).get("data", {})
    )
    has_hybrid = bool(
        artifact_sources.get("hybrid_rag_experiment_json", {}).get("data", {})
    )
    has_structure_hybrid = bool(
        artifact_sources.get("hybrid_rag_structure_aware_json", {}).get("data", {})
    )
    has_evidence_eval = bool(
        artifact_sources.get("evidence_level_evaluation_json", {}).get("data", {})
    )
    has_web_readiness = isinstance(web_readiness, dict) and bool(web_readiness)
    has_web_smoke = isinstance(web_smoke, dict) and bool(web_smoke)
    has_final_evaluation = isinstance(final_evaluation, dict) and bool(final_evaluation)
    if has_chunking and has_hybrid:
        if has_structure_hybrid:
            if has_final_evaluation and has_web_smoke:
                next_work_lines = [
                    "1. Run final quality gates and keep the repository ready for submission.",
                    "2. Add GitLab CI for `ruff` and `pytest` if automated checks are required.",
                    "3. Optionally mirror the remaining P3 tasks into GitLab issues.",
                    "4. Expand beyond PHAK Chapter 4 only after document metadata and section schema are enforced.",
                ]
            else:
                first_next_work = (
                    "1. Review the chunk/span gold labels and fix weak spans."
                    if has_evidence_eval
                    else "1. Refine gold labels from source-page to chunk/span evidence."
                )
                next_work_lines = [
                    first_next_work,
                    "2. Smoke-test the FastAPI web demo and capture final review notes.",
                    "3. Write project-defense conclusions from fixed-window and structure-aware runs.",
                    "4. Generate the AI-polished final report after review.",
                    "5. Prepare final submission checks.",
                ]
        else:
            next_work_lines = [
                "1. Review the chunking and Hybrid RAG reports for project-defense claims.",
                "2. Decide whether to re-extract the KG with `structure_aware` chunks.",
                "3. Refine gold labels from source-page to chunk/span evidence.",
                "4. Generate the AI-polished final report after review.",
                "5. Implement the minimal web interface demonstrator.",
            ]
    else:
        next_work_lines = [
            "1. Run report hygiene to maintain a readable stage dashboard.",
            "2. Run chunking comparison and Hybrid RAG experiments with recorded run manifests.",
            "3. Refine gold labels from source-page to chunk/span evidence.",
            "4. Use the AI report command to polish this deterministic draft.",
        ]
    reproducibility_lines = [
        "- `uv run aviation-ai report chunking-comparison`",
        "- `uv run aviation-ai index build`",
        "- `uv run aviation-ai report hybrid-rag`",
    ]
    if has_structure_hybrid:
        reproducibility_lines.extend(
            [
                "- `uv run aviation-ai kg extract --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --output data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --ttl-output data/kg/06_phak_ch4_0.structure_aware.kg.ttl`",
                "- `uv run aviation-ai kg validate --kg-file data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --output-dir reports/stages --report-name structure_aware_kg_validation`",
                "- `uv run aviation-ai index build --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --collection-name phak_ch4_chunks_structure_aware`",
                "- `uv run aviation-ai report hybrid-rag --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --kg-file data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --collection-name phak_ch4_chunks_structure_aware --chunking-strategy structure_aware --report-name hybrid_rag_structure_aware`",
                "- `uv run aviation-ai report graphrag-review`",
            ]
        )
    if has_evidence_eval:
        reproducibility_lines.extend(
            [
                "- `uv run aviation-ai cqs gold-draft`",
                "- `uv run aviation-ai report evidence-eval`",
            ]
        )
    if has_web_readiness:
        reproducibility_lines.extend(
            [
                "- `uv run aviation-ai report web-demo-readiness`",
                "- `uv run aviation-ai web serve`",
            ]
        )
    if has_web_smoke:
        reproducibility_lines.append("- `uv run aviation-ai report web-demo-smoke`")
    if has_final_evaluation:
        reproducibility_lines.append("- `uv run aviation-ai report final-evaluation`")
    reproducibility_lines.append("- `uv run aviation-ai report thesis-claims`")
    reproducibility_lines.extend(
        [
            "- `uv run aviation-ai report benchmark-v2`",
            "- `uv run aviation-ai report benchmark-review-pack`",
            "- `uv run aviation-ai report retrieval-ablation --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json --report-name retrieval_ablation_benchmark_v2`",
            "- `uv run aviation-ai report graph-traversal-ablation --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json --report-name graph_traversal_ablation_benchmark_v2`",
            "- `uv run aviation-ai report sufficiency-eval --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json`",
            "- `uv run aviation-ai report triple-semantic-review --sample-size 100`",
        ]
    )
    reproducibility_lines.extend(
        [
            "- `uv run aviation-ai report hygiene --apply`",
            "- `uv run aviation-ai report project --no-ai`",
            "- `uv run aviation-ai report project --ai`",
        ]
    )
    lines = [
        "# Aviation Agentic AI Project Report",
        "",
        "## Project motivation and course objective alignment",
        "",
        "This project investigates a reproducible aviation-domain RAG pipeline that turns "
        "FAA training text into ontology, KG, retrieval, and grounded-answer artifacts. "
        f"Course goal evidence: `{evidence['course_goal']['path']}` "
        f"({_present_marker(evidence['course_goal'])}).",
        "",
        "## Thesis claim positioning",
        "",
        REVISED_THESIS_CLAIM,
        "",
        "Thesis positioning evidence: "
        f"`{evidence['thesis_positioning']['path']}` "
        f"({_present_marker(evidence['thesis_positioning'])}); claim review evidence: "
        f"`{evidence['thesis_claims_review']['path']}` "
        f"({_present_marker(evidence['thesis_claims_review'])}).",
        "",
        "## Architecture overview",
        "",
        "The implementation is CLI-first and separates ontology, KG extraction, chunking, "
        "retrieval, evaluation, and reporting modules. Primary configuration evidence is "
        "`configs/default.yaml`, `configs/ontology_generation.yaml`, and "
        "`configs/extraction_profile.yaml`.",
        "",
        "## Ontology/TBox generation and evaluation",
        "",
        f"The active ontology is `{ontology_path}`, with design rationale in "
        f"`{ontology_design}`. It replaces the historical baseline as the explainable "
        "schema used for KG extraction.",
        f"Curated ontology metrics: triples={structural.get('triples', 'TBD')}, "
        f"classes={structural.get('classes', 'TBD')}, object_properties="
        f"{structural.get('object_properties', 'TBD')}, TBox-only="
        f"{structural.get('tbox_only', 'TBD')}, label coverage="
        f"{structural.get('class_label_coverage', 'TBD')}.",
        f"Ontology judgment: valid TBox prototype="
        f"{judgment.get('valid_tbox_prototype', 'TBD')}, publication-ready="
        f"{judgment.get('publication_ready_ontology', 'TBD')}.",
        f"Historical ontology evaluation artifacts indexed: "
        f"{len(categories.get('ontology_evaluation', []))}.",
        "",
        "## KG/ABox extraction and validation",
        "",
        "The KG stage is designed around focused triples with provenance and deterministic "
        "validation against the extraction profile.",
        f"Validated KG artifact: `{kg_path}`. Triples={kg_triples}; validation errors="
        f"{kg_errors}; ontology constraint=`{kg_validation.get('ontology_path', ontology_path)}`.",
        f"Structure-aware KG artifact: `{structure_kg_path}`. Triples="
        f"{structure_kg_triples}; validation errors={structure_kg_errors}. It is kept "
        "separate from the fixed-window KG to avoid mixing chunk-id schemas.",
        "",
        "## Chunking comparison design",
        "",
        *chunking_lines,
        "",
        "## Hybrid RAG protocol and layered metrics",
        "",
        *hybrid_lines,
        "",
        "## Current results and limitations",
        "",
        "Current evidence now covers the explainable curated ontology, fixed-window KG, "
        "structure-aware KG, chunking comparison, fixed-window Hybrid RAG, "
        "structure-aware Hybrid RAG, and GraphRAG review when their reports are present "
        "in the stage index.",
        "Web demo readiness: "
        f"ready={web_readiness.get('ready', 'TBD') if isinstance(web_readiness, dict) else 'TBD'}, "
        "default strategy="
        f"{web_readiness.get('selected_default_strategy', 'TBD') if isinstance(web_readiness, dict) else 'TBD'}.",
        "The web demo is an offline-first FastAPI interface with a macOS-style "
        "sidebar, toolbar controls, answer workspace, chunk evidence, KG triple "
        "evidence, KG relationship graph, pipeline explanation, mode comparison, "
        "Why This Result panel, and advisory boundary display.",
        "Web explanation readiness: "
        f"ready={web_explanation.get('ready', 'TBD') if isinstance(web_explanation, dict) else 'TBD'}, "
        "default path="
        f"{web_explanation.get('default_path', 'TBD') if isinstance(web_explanation, dict) else 'TBD'}, "
        "recommended strategy="
        f"{web_explanation.get('recommended_strategy', 'TBD') if isinstance(web_explanation, dict) else 'TBD'}.",
        "Final evaluation review: "
        f"default strategy={default_decision.get('recommended_default', 'TBD')}, "
        f"baseline={default_decision.get('baseline', 'TBD')}, gold review status="
        f"{gold_review.get('review_status', 'TBD')}, review required="
        f"{gold_review.get('review_required', 'TBD')}.",
        "Web demo smoke: "
        f"ready={web_smoke.get('ready', 'TBD') if isinstance(web_smoke, dict) else 'TBD'} "
        "for static/API checks.",
        *expansion_lines,
        *benchmark_v2_lines,
        "Limitations: chunk/span gold labels are reviewed for source alignment but "
        "are not external aviation examiner certification, structure-aware KG "
        "extraction is more expensive because it uses many smaller chunks, and "
        "GraphRAG should be defended as structured evidence support rather than a "
        "single-score Recall improvement.",
        "",
        "## Advisory assistant boundary",
        "",
        evidence["advisory_boundary"],
        "",
        "## Next work plan",
        "",
        *next_work_lines,
        "",
        "## Reproducibility appendix",
        "",
        *reproducibility_lines,
        "",
        "## Evidence Sources",
        "",
        f"- Stage index: `{evidence['stage_index']['path']}` "
        f"({_present_marker(evidence['stage_index'])})",
        f"- README: `{evidence['readme']['path']}` ({_present_marker(evidence['readme'])})",
        f"- Goal: `{evidence['course_goal']['path']}` "
        f"({_present_marker(evidence['course_goal'])})",
        f"- Thesis positioning: `{evidence['thesis_positioning']['path']}` "
        f"({_present_marker(evidence['thesis_positioning'])})",
        "- Thesis-ready stage evidence: `reports/stages/benchmark_v2_summary.md`, "
        "`reports/stages/retrieval_ablation_benchmark_v2.md`, "
        "`reports/stages/graph_traversal_ablation_benchmark_v2.md`, "
        "`reports/stages/sufficiency_evaluation.md`, "
        "`reports/stages/triple_semantic_review.md`",
        "- Configs: `configs/default.yaml`, `configs/ontology_generation.yaml`, "
        "`configs/extraction_profile.yaml`",
        "",
    ]
    return "\n".join(lines)


def build_project_report_prompt(evidence: dict[str, Any], draft: str) -> str:
    evidence_json = json.dumps(evidence, indent=2, sort_keys=True)
    return (
        "Write a complete Markdown project report for the Aviation Agentic AI project.\n\n"
        "Rules:\n"
        "- Use only the evidence pack and deterministic draft below.\n"
        "- Cite source file paths inline when making factual claims.\n"
        "- Do not invent completed experiments, metrics, models, or results.\n"
        "- If evidence is missing, write TBD or Not yet run.\n"
        "- Do not include API keys, tokens, secrets, or environment variable values.\n"
        "- Preserve the revised thesis claim and layered evaluation framing.\n"
        "- Preserve the advisory boundary and do not claim the assistant replaces POH, "
        "checklists, ATC, instructor guidance, or pilot judgment.\n"
        "- Keep all required sections from the deterministic draft.\n\n"
        f"Deterministic draft:\n---\n{draft}\n---\n\n"
        f"Evidence pack JSON:\n---\n{evidence_json[:20000]}\n---\n"
    )


def _invoke_llm_project_report(prompt: str, temperature: float, max_tokens: int) -> str:
    try:
        from langchain_core.messages import HumanMessage
    except ImportError as exc:
        raise RuntimeError(
            "AI project report generation requires optional ontology-generation dependencies. "
            "Install with: uv sync --extra ontology-generation"
        ) from exc

    from aviation_agentic_ai.llm.providers import get_llm

    response = get_llm(temperature=temperature, max_tokens=max_tokens).invoke(
        [HumanMessage(content=prompt)]
    )
    return str(getattr(response, "content", response)).strip()


def write_project_report_sources(evidence: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_project_report_markdown(markdown: str, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    return path


def write_project_report(
    output_dir: str | Path,
    *,
    project_root: str | Path = PROJECT_ROOT,
    stage_index_path: str | Path | None = None,
    use_ai: bool = False,
    llm_runner: LLMRunner | None = None,
    temperature: float = 0.0,
    max_tokens: int = 4096,
) -> tuple[Path, Path, dict[str, Any]]:
    evidence = build_project_evidence_pack(
        project_root=project_root,
        stage_index_path=stage_index_path,
    )
    draft = build_project_report_draft(evidence)
    prompt = build_project_report_prompt(evidence, draft)
    if use_ai:
        runner = llm_runner or _invoke_llm_project_report
        markdown = runner(prompt, temperature, max_tokens)
    else:
        markdown = draft
    output = Path(output_dir)
    md_path = write_project_report_markdown(markdown, output / "project_report.md")
    sources_path = write_project_report_sources(evidence, output / "project_report_sources.json")
    return md_path, sources_path, {
        "used_ai": use_ai,
        "prompt": prompt,
        "markdown": markdown,
        "sources": evidence,
        "output_paths": {
            "markdown": project_relative_path(md_path),
            "sources": project_relative_path(sources_path),
        },
    }
