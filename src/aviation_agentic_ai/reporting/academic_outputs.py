from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from aviation_agentic_ai.reporting.accessors import nested_value as _metric


ACADEMIC_SKILLS = [
    "ml-paper-writing",
    "academic-paper-reviewer",
    "academic-pptx",
    "Presentations",
]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _artifact_data(evidence: dict[str, Any], key: str) -> dict[str, Any]:
    data = evidence.get("current_artifacts", {}).get(f"{key}_json", {}).get("data", {})
    if not data:
        data = evidence.get("thesis_ready_artifacts", {}).get(f"{key}_json", {}).get("data", {})
    return data if isinstance(data, dict) else {}


def _source_paths(evidence: dict[str, Any]) -> list[str]:
    sources: set[str] = {
        evidence.get("stage_index", {}).get("path", "reports/stages/index.json"),
        evidence.get("readme", {}).get("path", "README.md"),
        evidence.get("goals", {}).get("path", "GOALS.md"),
        evidence.get("tasks", {}).get("path", "TASKS.md"),
        evidence.get("course_goal", {}).get("path", "tmp/goal.md"),
        "configs/default.yaml",
        "configs/ontology_generation.yaml",
        "configs/extraction_profile.yaml",
        "docs/thesis_positioning.md",
        "reports/stages/thesis_claims_review.json",
    }
    for source in evidence.get("current_artifacts", {}).values():
        if isinstance(source, dict) and source.get("present") and source.get("path"):
            sources.add(str(source["path"]))
    for source in evidence.get("thesis_ready_artifacts", {}).values():
        if isinstance(source, dict) and source.get("present") and source.get("path"):
            sources.add(str(source["path"]))
    return sorted(path for path in sources if path)


def _active_artifacts(evidence: dict[str, Any]) -> dict[str, str]:
    artifacts = (
        evidence.get("stage_index", {})
        .get("data", {})
        .get("current_active_artifacts", {})
    )
    return artifacts if isinstance(artifacts, dict) else {}


def build_academic_summary(evidence: dict[str, Any]) -> dict[str, Any]:
    chunking = _artifact_data(evidence, "chunking_comparison")
    fixed_hybrid = _artifact_data(evidence, "hybrid_rag_experiment")
    structure_hybrid = _artifact_data(evidence, "hybrid_rag_structure_aware")
    evidence_eval = _artifact_data(evidence, "evidence_level_evaluation")
    graphrag_review = _artifact_data(evidence, "graphrag_review")
    curated_eval = _artifact_data(evidence, "curated_ontology_evaluation")
    kg_validation = _artifact_data(evidence, "kg_validation")
    structure_kg_validation = _artifact_data(evidence, "structure_aware_kg_validation")
    web_demo = _artifact_data(evidence, "web_demo_readiness")
    web_smoke = _artifact_data(evidence, "web_demo_final_smoke")
    final_evaluation = _artifact_data(evidence, "final_evaluation_review")
    benchmark_v2 = _artifact_data(evidence, "benchmark_v2_summary")
    benchmark_review = _artifact_data(evidence, "benchmark_review_pack")
    retrieval_v2 = _artifact_data(evidence, "retrieval_ablation_benchmark_v2")
    traversal_v2 = _artifact_data(evidence, "graph_traversal_ablation_benchmark_v2")
    sufficiency = _artifact_data(evidence, "sufficiency_evaluation")
    triple_review = _artifact_data(evidence, "triple_semantic_review")
    dashboard = _artifact_data(evidence, "thesis_experiment_dashboard")
    ranking = chunking.get("ranking", []) if isinstance(chunking, dict) and isinstance(chunking.get("ranking"), list) else []
    best_chunking = ranking[0] if ranking else {}
    fixed_hybrid_agg = fixed_hybrid.get("aggregate", {})
    structure_hybrid_agg = structure_hybrid.get("aggregate", {})
    evidence_experiments = evidence_eval.get("experiments", {})
    fixed_evidence = _metric(evidence_experiments, "fixed_window", "aggregate", "hybrid", default={})
    structure_evidence = _metric(
        evidence_experiments,
        "structure_aware",
        "aggregate",
        "hybrid",
        default={},
    )
    return {
        "generated_at": _now(),
        "skills_used": ACADEMIC_SKILLS,
        "source_paths": _source_paths(evidence),
        "artifacts": _active_artifacts(evidence),
        "key_claims": [
            {
                "claim": "The project implements a reproducible aviation-domain GraphRAG pipeline.",
                "evidence_sources": [
                    "README.md",
                    "reports/stages/index.json",
                ],
            },
            {
                "claim": "The curated ontology is the explainable active schema for KG extraction.",
                "evidence_sources": [
                    "docs/archive/phak_era/ontology_design.md",
                    "reports/stages/curated_ontology_evaluation.json",
                    "configs/extraction_profile.yaml",
                ],
            },
            {
                "claim": "Structure-aware chunking is the best current retrieval strategy by the chunking comparison ranking.",
                "evidence_sources": ["reports/stages/chunking_comparison.json"],
            },
            {
                "claim": "GraphRAG value should be defended as structured KG evidence coverage rather than only page-level Recall lift.",
                "evidence_sources": [
                    "docs/thesis_positioning.md",
                    "reports/stages/thesis_claims_review.json",
                    "reports/stages/graphrag_review.json",
                    "reports/stages/evidence_level_evaluation.json",
                ],
            },
            {
                "claim": "The web demo is a learning/decision-support explanation surface, not an operational flight authority.",
                "evidence_sources": [
                    "reports/stages/web_demo_readiness.json",
                    "reports/stages/web_demo_final_smoke.json",
                    "src/aviation_agentic_ai/advisory.py",
                ],
            },
            {
                "claim": "The final evaluation selects structure-aware as the default demo and next-phase GraphRAG strategy.",
                "evidence_sources": ["reports/stages/final_evaluation_review.json"],
            },
        ],
        "metrics": {
            "ontology": {
                "classes": _metric(curated_eval, "structural_metrics", "classes"),
                "object_properties": _metric(
                    curated_eval,
                    "structural_metrics",
                    "object_properties",
                ),
                "tbox_only": _metric(curated_eval, "structural_metrics", "tbox_only"),
                "label_coverage": _metric(
                    curated_eval,
                    "structural_metrics",
                    "class_label_coverage",
                ),
            },
            "kg": {
                "fixed_window_triples": kg_validation.get("triples_total", "TBD"),
                "fixed_window_errors": kg_validation.get("errors_total", "TBD"),
                "structure_aware_triples": structure_kg_validation.get(
                    "triples_total",
                    "TBD",
                ),
                "structure_aware_errors": structure_kg_validation.get(
                    "errors_total",
                    "TBD",
                ),
            },
            "chunking": {
                "best_strategy": best_chunking.get("strategy", "TBD"),
                "best_recall_at_5": best_chunking.get("recall_at_5", "TBD"),
                "best_mrr_at_5": best_chunking.get("mrr_at_5", "TBD"),
                "best_context_precision_at_5": best_chunking.get(
                    "context_precision_at_5",
                    "TBD",
                ),
                "structure_aware_chunks": _metric(
                    chunking,
                    "strategies",
                    "structure_aware",
                    "aggregate",
                    "chunking",
                    "chunk_count",
                ),
                "fixed_window_chunks": _metric(
                    chunking,
                    "strategies",
                    "fixed_window",
                    "aggregate",
                    "chunking",
                    "chunk_count",
                ),
            },
            "hybrid_rag": {
                "fixed_vector_recall_at_5": _metric(
                    fixed_hybrid_agg,
                    "vector",
                    "retrieval",
                    "recall_at_5",
                ),
                "fixed_hybrid_recall_at_5": _metric(
                    fixed_hybrid_agg,
                    "hybrid",
                    "retrieval",
                    "recall_at_5",
                ),
                "fixed_hybrid_kg_coverage": _metric(
                    fixed_hybrid_agg,
                    "hybrid",
                    "kg_evidence",
                    "evidence_coverage",
                ),
                "structure_vector_recall_at_5": _metric(
                    structure_hybrid_agg,
                    "vector",
                    "retrieval",
                    "recall_at_5",
                ),
                "structure_hybrid_recall_at_5": _metric(
                    structure_hybrid_agg,
                    "hybrid",
                    "retrieval",
                    "recall_at_5",
                ),
                "structure_hybrid_kg_coverage": _metric(
                    structure_hybrid_agg,
                    "hybrid",
                    "kg_evidence",
                    "evidence_coverage",
                ),
                "fixed_supported_answers": _metric(
                    fixed_evidence,
                    "answer_support_distribution",
                    "supported",
                ),
                "structure_supported_answers": _metric(
                    structure_evidence,
                    "answer_support_distribution",
                    "supported",
                ),
            },
            "web_demo": {
                "ready": web_demo.get("ready", "TBD"),
                "default_strategy": web_demo.get("selected_default_strategy", "TBD"),
                "explanation_ready": _metric(web_demo, "explanation", "ready"),
                "smoke_ready": web_smoke.get("ready", "TBD"),
            },
            "final_evaluation": {
                "default_strategy": _metric(
                    final_evaluation,
                    "default_strategy_decision",
                    "recommended_default",
                ),
                "baseline_strategy": _metric(
                    final_evaluation,
                    "default_strategy_decision",
                    "baseline",
                ),
                "gold_review_status": _metric(
                    final_evaluation,
                    "gold_label_review",
                    "review_status",
                ),
                "gold_review_required": _metric(
                    final_evaluation,
                    "gold_label_review",
                    "review_required",
                ),
            },
            "benchmark_v2": {
                "labels_total": _metric(benchmark_v2, "metadata", "labels_total"),
                "supported_total": _metric(benchmark_v2, "metadata", "supported_total"),
                "no_answer_total": _metric(benchmark_v2, "metadata", "no_answer_total"),
                "validation_valid": _metric(benchmark_v2, "validation", "valid"),
                "review_status": _metric(benchmark_v2, "metadata", "review_status"),
                "review_pack_labels_total": _metric(
                    benchmark_review,
                    "metadata",
                    "labels_total",
                ),
                "review_pack_finding_counts": _metric(
                    benchmark_review,
                    "finding_counts",
                    default={},
                ),
                "vector_recall_at_5": _metric(
                    retrieval_v2,
                    "scenarios",
                    "vector_hops2_v5_h8",
                    "aggregate",
                    "retrieval",
                    "recall_at_5",
                ),
                "hybrid_recall_at_5": _metric(
                    retrieval_v2,
                    "scenarios",
                    "hybrid_hops2_v5_h8",
                    "aggregate",
                    "retrieval",
                    "recall_at_5",
                ),
                "hybrid_kg_coverage": _metric(
                    retrieval_v2,
                    "scenarios",
                    "hybrid_hops2_v5_h8",
                    "aggregate",
                    "kg_evidence",
                    "evidence_coverage",
                ),
                "traversal_path_coverage": _metric(
                    traversal_v2,
                    "scenarios",
                    "traversal_graph_2_hop",
                    "aggregate",
                    "graph_paths",
                    "path_coverage",
                ),
                "traversal_recall_at_5": _metric(
                    traversal_v2,
                    "scenarios",
                    "traversal_graph_2_hop",
                    "aggregate",
                    "retrieval",
                    "recall_at_5",
                ),
                "traversal_guarded_recall_at_5": _metric(
                    traversal_v2,
                    "scenarios",
                    "hybrid_vector_traversal_guarded",
                    "aggregate",
                    "retrieval",
                    "recall_at_5",
                ),
                "sufficiency_supported_decision_accuracy": _metric(
                    sufficiency,
                    "metrics",
                    "supported_answer_decision_accuracy",
                ),
                "sufficiency_abstention_accuracy": _metric(
                    sufficiency,
                    "metrics",
                    "insufficient_evidence_abstention_accuracy",
                ),
                "sufficiency_false_answer_rate": _metric(
                    sufficiency,
                    "metrics",
                    "false_answer_rate_on_no_answer_questions",
                ),
                "sufficiency_false_abstention_rate": _metric(
                    sufficiency,
                    "metrics",
                    "false_abstention_rate_on_supported_questions",
                ),
                "sufficiency_risk_category_accuracy": _metric(
                    sufficiency,
                    "metrics",
                    "risk_category_accuracy",
                ),
                "sufficiency_boundary_violation_count": _metric(
                    sufficiency,
                    "metrics",
                    "boundary_violation_count",
                ),
                "triple_review_sample_size": _metric(
                    triple_review,
                    "metadata",
                    "sample_size",
                ),
            },
            "thesis_dashboard": {
                "consistency_passed": _metric(
                    dashboard,
                    "consistency_checks",
                    "all_passed",
                ),
                "vector_recall_at_5": _metric(
                    dashboard,
                    "primary_results",
                    "vector_only",
                    "recall_at_5",
                ),
                "hybrid_context_recall": _metric(
                    dashboard,
                    "primary_results",
                    "best_lexical_hybrid",
                    "context_recall",
                ),
                "traversal_path_recall_at_5": _metric(
                    dashboard,
                    "primary_results",
                    "traversal_hybrid",
                    "path_recall_at_5",
                ),
                "false_abstention_rate": _metric(
                    dashboard,
                    "primary_results",
                    "sufficiency",
                    "false_abstention_rate",
                ),
            },
        },
        "rq_to_evidence_matrix": dashboard.get("rq_to_evidence_matrix", [])
        if isinstance(dashboard, dict)
        else [],
        "graphrag_interpretations": graphrag_review.get("interpretations", []),
        "advisory_boundary": evidence.get("advisory_boundary", ""),
        "source_policy": evidence.get("source_policy", {}),
    }


