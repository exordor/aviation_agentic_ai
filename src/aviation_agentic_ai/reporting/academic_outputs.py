from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.project_report import build_project_evidence_pack
from aviation_agentic_ai.reporting.thesis_claims import REVISED_THESIS_CLAIM


ACADEMIC_SKILLS = [
    "ml-paper-writing",
    "academic-paper-reviewer",
    "academic-pptx",
    "Presentations",
    "local-deterministic-svg-assets",
    "gpt-image-2-optional-relay-assets",
]

VISUAL_ASSETS = [
    {
        "path": "reports/final/assets/project_cover_ai.png",
        "fallback_path": "reports/final/assets/project_cover.svg",
        "purpose": "Apple-style title-slide cover visual for the defense deck.",
        "prompt_role": "AI aviation GraphRAG research cover; no embedded text.",
    },
    {
        "path": "reports/final/assets/pipeline_hero_ai.png",
        "fallback_path": "reports/final/assets/pipeline_overview.svg",
        "purpose": "Large pipeline hero visual for PDF -> chunks -> KG -> Hybrid RAG.",
        "prompt_role": "AI aviation GraphRAG pipeline hero; no embedded text.",
    },
    {
        "path": "reports/final/assets/kg_evidence_ai.png",
        "fallback_path": "reports/final/assets/ontology_kg_graphrag_concept.svg",
        "purpose": "Reusable KG evidence visual for ontology and GraphRAG slides.",
        "prompt_role": "AI aviation KG evidence component; no embedded text.",
    },
    {
        "path": "reports/final/assets/web_demo_ai.png",
        "fallback_path": None,
        "purpose": "Apple-inspired web demo mockup for the interface explanation slide.",
        "prompt_role": "AI web demo mockup; abstract placeholder text only.",
    },
]


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _artifact_data(evidence: dict[str, Any], key: str) -> dict[str, Any]:
    data = evidence.get("current_artifacts", {}).get(f"{key}_json", {}).get("data", {})
    if not data:
        data = evidence.get("thesis_ready_artifacts", {}).get(f"{key}_json", {}).get("data", {})
    return data if isinstance(data, dict) else {}


def _metric(data: dict[str, Any], *keys: str, default: Any = "TBD") -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


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
    ranking = chunking.get("ranking", []) if isinstance(chunking.get("ranking"), list) else []
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
                    "reports/final/project_report_sources.json",
                ],
            },
            {
                "claim": "The curated ontology is the explainable active schema for KG extraction.",
                "evidence_sources": [
                    "docs/ontology_design.md",
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
        "visual_assets": VISUAL_ASSETS,
        "source_policy": evidence.get("source_policy", {}),
    }


def build_academic_report_markdown(summary: dict[str, Any]) -> str:
    metrics = summary["metrics"]
    artifacts = summary.get("artifacts", {})
    lines = [
        "# Aviation Agentic AI: Ontology-Constrained GraphRAG for Aviation Learning",
        "",
        "## Abstract",
        "",
        "This project builds a reproducible aviation-domain GraphRAG prototype over FAA "
        "PHAK Chapter 4. The system converts a PDF into chunks, constrains KG extraction "
        "with an explainable curated ontology, builds vector and graph retrieval indexes, "
        "and reports grounded answers with citations. The current evidence shows that "
        "GraphRAG should be defended primarily as structured evidence support rather than "
        "as a single page-level Recall@5 improvement. Sources: `reports/stages/index.json`, "
        "`reports/stages/graphrag_review.json`.",
        "",
        "Revised thesis claim: " + REVISED_THESIS_CLAIM,
        "",
        "## 1. Introduction",
        "",
        "The course objective is to explain a full AI pipeline that can answer what the "
        "system does, why each design choice exists, and what evidence supports the "
        "claims. This implementation focuses on aviation learning and decision support, "
        "not operational flight authority. Sources: `GOALS.md`, "
        "`src/aviation_agentic_ai/advisory.py`.",
        "",
        "## 2. Background and Research Gap",
        "",
        "A vector-only RAG baseline can retrieve relevant pages, but it does not expose "
        "typed relations such as causes, affects, hasCondition, or supportedByEvidence. "
        "The project therefore uses an ontology-constrained KG to add interpretable "
        "evidence structure. Sources: `docs/ontology_design.md`, "
        "`configs/extraction_profile.yaml`.",
        "",
        "## 3. Methodology",
        "",
        "The implemented pipeline is PDF -> chunks -> curated ontology -> KG/ABox -> "
        "Chroma vector index -> graph/vector/hybrid retrieval -> grounded LLM answer -> "
        "layered evaluation report. The pipeline is CLI-first so that every major "
        "artifact can be regenerated and inspected. Sources: `README.md`, "
        "`configs/default.yaml`, `reports/stages/thesis_experiment_dashboard.json`.",
        "",
        "## 4. Explainable Ontology Design",
        "",
        f"The active ontology is `{artifacts.get('active_ontology', 'TBD')}` and its "
        f"design rationale is `{artifacts.get('ontology_design', 'TBD')}`. The curated "
        "ontology replaces the baseline as the main explainable schema because it is "
        "small enough to present, validates KG extraction, and supports GraphRAG "
        "relations.",
        "",
        f"Ontology metrics: classes={metrics['ontology']['classes']}, object properties="
        f"{metrics['ontology']['object_properties']}, TBox-only="
        f"{metrics['ontology']['tbox_only']}, class label coverage="
        f"{metrics['ontology']['label_coverage']}. Source: "
        "`reports/stages/curated_ontology_evaluation.json`.",
        "",
        "## 5. KG Construction and Validation",
        "",
        "KG extraction is constrained by the curated ontology and extraction profile; "
        "triples require evidence and provenance. Fixed-window and structure-aware KG "
        "artifacts are kept separate to avoid mixing chunk-id schemas.",
        "",
        f"Fixed-window KG: triples={metrics['kg']['fixed_window_triples']}, validation "
        f"errors={metrics['kg']['fixed_window_errors']}. Structure-aware KG: triples="
        f"{metrics['kg']['structure_aware_triples']}, validation errors="
        f"{metrics['kg']['structure_aware_errors']}. Sources: "
        "`reports/stages/kg_validation.json`, "
        "`reports/stages/structure_aware_kg_validation.json`.",
        "",
        "## 6. Chunking Comparison",
        "",
        f"The chunking comparison ranks `{metrics['chunking']['best_strategy']}` first "
        f"with Recall@5={metrics['chunking']['best_recall_at_5']}, MRR@5="
        f"{metrics['chunking']['best_mrr_at_5']}, and Context Precision@5="
        f"{metrics['chunking']['best_context_precision_at_5']}. It uses "
        f"{metrics['chunking']['structure_aware_chunks']} chunks versus "
        f"{metrics['chunking']['fixed_window_chunks']} fixed-window chunks. Source: "
        "`reports/stages/chunking_comparison.json`.",
        "",
        "The result is consistent with the document type: aviation handbooks have page, "
        "section, and list structure, so preserving structure improves retrieval "
        "granularity even when it increases index size.",
        "",
        "## 7. Hybrid RAG and GraphRAG Evaluation",
        "",
        "This section reports retrieval quality, KG evidence quality, answer citation "
        "quality, and safety-aware abstention separately. It does not use a single "
        "mixed overall score.",
        "",
        f"Fixed-window vector Recall@5={metrics['hybrid_rag']['fixed_vector_recall_at_5']} "
        f"and fixed-window hybrid Recall@5="
        f"{metrics['hybrid_rag']['fixed_hybrid_recall_at_5']}; fixed-window hybrid KG "
        f"evidence coverage={metrics['hybrid_rag']['fixed_hybrid_kg_coverage']}. "
        f"Structure-aware vector Recall@5="
        f"{metrics['hybrid_rag']['structure_vector_recall_at_5']} and structure-aware "
        f"hybrid Recall@5={metrics['hybrid_rag']['structure_hybrid_recall_at_5']}; "
        f"structure-aware hybrid KG evidence coverage="
        f"{metrics['hybrid_rag']['structure_hybrid_kg_coverage']}. Sources: "
        "`reports/stages/hybrid_rag_experiment.json`, "
        "`reports/stages/hybrid_rag_structure_aware.json`.",
        "",
        f"Evidence-level scoring is more useful for defending GraphRAG: structure-aware "
        f"hybrid supports {metrics['hybrid_rag']['structure_supported_answers']} answers "
        f"versus {metrics['hybrid_rag']['fixed_supported_answers']} for fixed-window "
        "hybrid. Source: `reports/stages/evidence_level_evaluation.json`.",
        "",
        "## 8. Benchmark V2, Traversal, and Sufficiency Evidence",
        "",
        "The thesis benchmark v2 layer is reported separately from the earlier course "
        "gold set. It is machine-seeded and span-validated against repository chunks, "
        "but it is not external aviation-expert certification.",
        "",
        f"Benchmark v2 contains {metrics['benchmark_v2']['labels_total']} labels: "
        f"{metrics['benchmark_v2']['supported_total']} supported labels and "
        f"{metrics['benchmark_v2']['no_answer_total']} insufficient-evidence labels. "
        f"Validation passed={metrics['benchmark_v2']['validation_valid']}; review "
        f"status=`{metrics['benchmark_v2']['review_status']}`. The manual-review pack "
        f"covers {metrics['benchmark_v2']['review_pack_labels_total']} labels and uses "
        "automatic findings only as prompts for human review. Sources: "
        "`reports/stages/benchmark_v2_summary.json`, "
        "`reports/stages/benchmark_review_pack.json`.",
        "",
        f"On benchmark v2, vector Recall@5="
        f"{metrics['benchmark_v2']['vector_recall_at_5']} and default hybrid Recall@5="
        f"{metrics['benchmark_v2']['hybrid_recall_at_5']}; hybrid KG evidence "
        f"coverage={metrics['benchmark_v2']['hybrid_kg_coverage']}. These retrieval "
        "metrics are kept separate from KG evidence coverage. Source: "
        "`reports/stages/retrieval_ablation_benchmark_v2.json`.",
        "",
        f"Graph traversal shows the expected split between graph reachability and "
        f"page-level retrieval quality: 2-hop traversal path coverage="
        f"{metrics['benchmark_v2']['traversal_path_coverage']} while standalone "
        f"Recall@5={metrics['benchmark_v2']['traversal_recall_at_5']}. The guarded "
        f"hybrid traversal policy records Recall@5="
        f"{metrics['benchmark_v2']['traversal_guarded_recall_at_5']} and is reported "
        "as a comparison point, not as a guaranteed improvement. Source: "
        "`reports/stages/graph_traversal_ablation_benchmark_v2.json`.",
        "",
        f"The evidence sufficiency layer reports supported decision accuracy="
        f"{metrics['benchmark_v2']['sufficiency_supported_decision_accuracy']}, "
        f"insufficient-evidence abstention accuracy="
        f"{metrics['benchmark_v2']['sufficiency_abstention_accuracy']}, false answer "
        f"rate on no-answer questions="
        f"{metrics['benchmark_v2']['sufficiency_false_answer_rate']}, false "
        f"abstention rate on supported questions="
        f"{metrics['benchmark_v2']['sufficiency_false_abstention_rate']}, risk-category "
        f"accuracy={metrics['benchmark_v2']['sufficiency_risk_category_accuracy']}, "
        f"and boundary violations="
        f"{metrics['benchmark_v2']['sufficiency_boundary_violation_count']}. Source: "
        "`reports/stages/sufficiency_evaluation.json`.",
        "",
        f"The triple semantic review sample contains "
        f"{metrics['benchmark_v2']['triple_review_sample_size']} triples with review "
        "fields initialized to `needs_review`; no semantic correctness claim is made "
        "until those annotations are completed. Source: "
        "`reports/stages/triple_semantic_review_sample.json`.",
        "",
        "## 9. Research-Question Synthesis From Thesis Dashboard",
        "",
        "The thesis experiment dashboard is the main synthesis artifact for the final "
        "report. It maps research questions to datasets, metrics, reports, current "
        "claim strength, and remaining gaps. Sources: "
        "`reports/stages/thesis_experiment_dashboard.json`, "
        "`docs/experiment_workflow.md`.",
        "",
        f"Dashboard consistency checks passed="
        f"{metrics['thesis_dashboard']['consistency_passed']}. The dashboard reports "
        f"vector Recall@5={metrics['thesis_dashboard']['vector_recall_at_5']}, lexical "
        f"hybrid Context Recall={metrics['thesis_dashboard']['hybrid_context_recall']}, "
        f"traversal Path Recall@5="
        f"{metrics['thesis_dashboard']['traversal_path_recall_at_5']}, and sufficiency "
        f"False Abstention Rate={metrics['thesis_dashboard']['false_abstention_rate']}.",
        "",
        *[
            (
                f"- {row.get('rq')}: claim strength={row.get('claim_strength')}; "
                f"reports={', '.join(row.get('evidence_reports', []))}; "
                f"gap={row.get('remaining_gaps')}"
            )
            for row in summary.get("rq_to_evidence_matrix", [])
            if isinstance(row, dict)
        ],
        "",
        "## 10. Discussion",
        "",
        "The main interpretation is that vector-only retrieval can remain competitive on "
        "coarse page-level gold labels, while GraphRAG contributes relation-level evidence "
        "coverage and provenance. This distinction prevents the evaluation from collapsing "
        "retrieval, KG evidence, answer quality, and abstention into one misleading score. "
        "Source: "
        "`reports/stages/graphrag_review.json`.",
        "",
        "## 11. Limitations and Threats to Validity",
        "",
        "The gold labels are reviewed for source alignment, but they remain course-project "
        "labels rather than external aviation examiner certification. The dataset is "
        "limited to PHAK Chapter 4. KG extraction depends on LLM structured output and "
        "therefore requires deterministic validation. Visual assets are explanatory "
        "presentation artifacts and must not be treated as experiment evidence.",
        "",
        "## 12. Web Demonstrator",
        "",
        f"The web demo readiness report marks ready={metrics['web_demo']['ready']}, "
        f"default strategy={metrics['web_demo']['default_strategy']}, and explanation "
        f"ready={metrics['web_demo']['explanation_ready']}. The final smoke report marks "
        f"ready={metrics['web_demo']['smoke_ready']}. The demo presents answer evidence, "
        "KG triples, relationship graph, mode comparison, pipeline explanation, and "
        "advisory boundary. Sources: `reports/stages/web_demo_readiness.json`, "
        "`reports/stages/web_demo_final_smoke.json`.",
        "",
        "## 12.1 Final Evaluation Decision",
        "",
        f"The final evaluation selects `{metrics['final_evaluation']['default_strategy']}` "
        "as the default demo and next-phase GraphRAG strategy while keeping "
        f"`{metrics['final_evaluation']['baseline_strategy']}` as the baseline. Gold "
        f"label review status is `{metrics['final_evaluation']['gold_review_status']}` "
        f"with review_required={metrics['final_evaluation']['gold_review_required']}. "
        "Source: `reports/stages/final_evaluation_review.json`.",
        "",
        "## 13. Advisory Boundary",
        "",
        summary["advisory_boundary"],
        "",
        "## 14. Conclusion",
        "",
        "The project is ready to be presented as a reproducible, evidence-layered "
        "GraphRAG prototype. The strongest defensible claim is not that graph retrieval "
        "universally beats vector retrieval, but that ontology-constrained KG evidence "
        "makes retrieved answers more explainable and auditable in the aviation handbook "
        "setting.",
        "",
        "## Reproducibility Appendix",
        "",
        "- `uv run aviation-ai report chunking-comparison`",
        "- `uv run aviation-ai report hybrid-rag`",
        "- `uv run aviation-ai report hybrid-rag --chunks data/chunks/06_phak_ch4_0.structure_aware.jsonl --kg-file data/kg/06_phak_ch4_0.structure_aware.kg.jsonl --collection-name phak_ch4_chunks_structure_aware --chunking-strategy structure_aware --report-name hybrid_rag_structure_aware`",
        "- `uv run aviation-ai report graphrag-review`",
        "- `uv run aviation-ai report evidence-eval`",
        "- `uv run aviation-ai report final-evaluation`",
        "- `uv run aviation-ai report web-demo-readiness`",
        "- `uv run aviation-ai report web-demo-smoke`",
        "- `uv run aviation-ai report thesis-claims`",
        "- `uv run aviation-ai cqs validate-benchmark`",
        "- `uv run aviation-ai report benchmark-v2`",
        "- `uv run aviation-ai report benchmark-review-pack`",
        "- `uv run aviation-ai report retrieval-ablation --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json --report-name retrieval_ablation_benchmark_v2`",
        "- `uv run aviation-ai report graph-traversal-ablation --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json --report-name graph_traversal_ablation_benchmark_v2`",
        "- `uv run aviation-ai report sufficiency-eval --gold-labels data/cqs/06_phak_ch4_0.benchmark_v2.gold.json`",
        "- `uv run aviation-ai report triple-semantic-review --sample-size 100`",
        "- `uv run aviation-ai report thesis-experiment-dashboard`",
        "- `uv run aviation-ai report academic-paper --no-ai`",
        "- `uv run aviation-ai report defense-notes`",
        "- `uv run aviation-ai report defense-deck-outline`",
        "",
        "## Source Paths",
        "",
        *[f"- `{path}`" for path in summary["source_paths"]],
        "",
    ]
    return "\n".join(lines)


def build_defense_notes(summary: dict[str, Any]) -> dict[str, Any]:
    metrics = summary["metrics"]
    return {
        "generated_at": _now(),
        "skills_used": ACADEMIC_SKILLS,
        "source_policy": summary["source_policy"],
        "elevator_pitch": (
            "This project turns one aviation handbook chapter into a reproducible "
            "GraphRAG pipeline: curated ontology, validated KG, chunking comparison, "
            "vector/graph/hybrid retrieval, grounded answers, and a web demo that makes "
            "the evidence inspectable. The thesis claim is evidence traceability and "
            "structured KG support, not universal Recall@k improvement."
        ),
        "demo_script": [
            "Open the web demo and state the advisory boundary first.",
            "Select a boundary CQ and show vector, graph, and hybrid evidence panels.",
            "Use the KG Relationship Graph to explain what GraphRAG adds beyond retrieved text.",
            "Use Why This Result to explain recall, KG coverage, and citation completeness.",
            "Close by showing reports/final/project_academic_report.md and the reproducibility commands.",
        ],
        "core_claims": summary["key_claims"],
        "metrics_talking_points": [
            (
                "Chunking: structure-aware is currently best by retrieval ranking "
                f"(Recall@5={metrics['chunking']['best_recall_at_5']}, "
                f"MRR@5={metrics['chunking']['best_mrr_at_5']})."
            ),
            (
                "Fixed-window Hybrid RAG should be described as KG-aligned baseline, "
                f"with hybrid KG evidence coverage="
                f"{metrics['hybrid_rag']['fixed_hybrid_kg_coverage']}."
            ),
            (
                "Structure-aware Hybrid RAG is the current default candidate: hybrid "
                f"Recall@5={metrics['hybrid_rag']['structure_hybrid_recall_at_5']} "
                "with separate KG evidence coverage and supported answers="
                f"{metrics['hybrid_rag']['structure_supported_answers']}."
            ),
        ],
        "qa_pairs": [
            {
                "question": "What is the ontology for?",
                "answer": (
                    "It defines a compact, explainable schema for aviation-domain concepts "
                    "and relations, so KG extraction can be validated and GraphRAG evidence "
                    "can be explained."
                ),
                "evidence_sources": [
                    "docs/ontology_design.md",
                    "reports/stages/curated_ontology_evaluation.json",
                ],
            },
            {
                "question": "Why not use the generated baseline ontology as the main one?",
                "answer": (
                    "The baseline is useful historical evidence, but it is too complex to "
                    "defend clearly. The curated ontology is smaller, modular, and aligned "
                    "with KG extraction properties."
                ),
                "evidence_sources": ["docs/ontology_design.md"],
            },
            {
                "question": "What does GraphRAG add if vector retrieval already has high Recall@5?",
                "answer": (
                    "The value is structured KG evidence coverage and provenance. Current "
                    "page-level Recall@5 is coarse, so vector retrieval can score well by "
                    "retrieving any chunk from the right page."
                ),
                "evidence_sources": [
                    "reports/stages/graphrag_review.json",
                    "reports/stages/evidence_level_evaluation.json",
                ],
            },
            {
                "question": "Why is structure-aware chunking recommended?",
                "answer": (
                    "It preserves handbook structure and currently ranks first on retrieval "
                    "quality; it also improves evidence-level answer support in the "
                    "structure-aware Hybrid RAG run."
                ),
                "evidence_sources": [
                    "reports/stages/chunking_comparison.json",
                    "reports/stages/evidence_level_evaluation.json",
                ],
            },
            {
                "question": "What is still weak?",
                "answer": (
                    "Gold labels are reviewed for source alignment but are not external "
                    "aviation examiner certification; the corpus is still only PHAK "
                    "Chapter 4, and LLM extraction must remain validator-gated."
                ),
                "evidence_sources": [
                    "data/cqs/06_phak_ch4_0.gold.json",
                    "reports/stages/final_evaluation_review.json",
                    "reports/stages/evidence_level_evaluation.json",
                ],
            },
            {
                "question": "Can this replace POH, checklist, ATC, instructor, or pilot judgment?",
                "answer": summary["advisory_boundary"],
                "evidence_sources": ["src/aviation_agentic_ai/advisory.py"],
            },
        ],
        "failure_cases": [
            {
                "case": "Coarse page-level gold can understate GraphRAG value.",
                "explanation": (
                    "Graph evidence may be relevant but off the gold source page, so page "
                    "Recall@5 can penalize useful structured evidence."
                ),
                "evidence_sources": ["reports/stages/graphrag_review.json"],
            },
            {
                "case": "KG evidence can fail even when retrieval succeeds.",
                "explanation": (
                    "Some CQs retrieve relevant text but lack extracted triples covering the "
                    "key entity; this is a KG extraction and schema coverage issue."
                ),
                "evidence_sources": ["reports/stages/evidence_level_evaluation.json"],
            },
        ],
        "source_paths": summary["source_paths"],
    }


def build_defense_notes_markdown(notes: dict[str, Any]) -> str:
    lines = [
        "# Project Defense Notes",
        "",
        "## 30-Second Summary",
        "",
        notes["elevator_pitch"],
        "",
        "## Demo Script",
        "",
        *[f"{index}. {step}" for index, step in enumerate(notes["demo_script"], start=1)],
        "",
        "## Metrics Talking Points",
        "",
        *[f"- {point}" for point in notes["metrics_talking_points"]],
        "",
        "## Likely Questions",
        "",
    ]
    for pair in notes["qa_pairs"]:
        lines.extend(
            [
                f"### {pair['question']}",
                "",
                pair["answer"],
                "",
                "Sources: "
                + ", ".join(f"`{source}`" for source in pair["evidence_sources"]),
                "",
            ]
        )
    lines.extend(["## Failure Cases", ""])
    for case in notes["failure_cases"]:
        lines.extend(
            [
                f"- **{case['case']}** {case['explanation']} Sources: "
                + ", ".join(f"`{source}`" for source in case["evidence_sources"]),
            ]
        )
    lines.extend(
        [
            "",
            "## Source Paths",
            "",
            *[f"- `{path}`" for path in notes["source_paths"]],
            "",
        ]
    )
    return "\n".join(lines)


def build_defense_deck_outline(summary: dict[str, Any]) -> dict[str, Any]:
    metrics = summary["metrics"]
    common_sources = [
        "reports/stages/index.json",
        "reports/final/project_academic_report.md",
    ]
    slides = [
        {
            "slide_number": 1,
            "title": "Ontology-constrained GraphRAG makes aviation handbook answers auditable",
            "role": "title",
            "claim": "The project turns PHAK Chapter 4 into an evidence-grounded GraphRAG demo.",
            "visual": "reports/final/assets/project_cover_ai.png",
            "evidence_sources": common_sources,
            "speaker_note": "Open with the problem, the source document, and the advisory boundary.",
        },
        {
            "slide_number": 2,
            "title": "The course goal is answered by a full evidence pipeline, not a single model call",
            "role": "motivation",
            "claim": "The project can explain what it does, why each component exists, and how results are evaluated.",
            "visual": "course objective and deliverable map",
            "evidence_sources": ["GOALS.md", "TASKS.md"],
            "speaker_note": "Frame the work as a reproducible research prototype.",
        },
        {
            "slide_number": 3,
            "title": "The pipeline preserves traceability from PDF text to grounded answers",
            "role": "method",
            "claim": "Each answer can be traced through chunks, KG triples, retrieval mode, and citations.",
            "visual": "reports/final/assets/pipeline_hero_ai.png",
            "evidence_sources": ["README.md", "configs/default.yaml"],
            "speaker_note": "Walk left-to-right through the pipeline.",
        },
        {
            "slide_number": 4,
            "title": "A curated ontology keeps the KG explainable enough to defend",
            "role": "method",
            "claim": (
                f"The active ontology has {metrics['ontology']['classes']} classes and "
                f"{metrics['ontology']['object_properties']} object properties."
            ),
            "visual": "ontology module diagram",
            "evidence_sources": [
                "docs/ontology_design.md",
                "reports/stages/curated_ontology_evaluation.json",
            ],
            "speaker_note": "Explain why the baseline ontology is not the main narrative object.",
        },
        {
            "slide_number": 5,
            "title": "KG extraction is useful only because every triple is validator-gated",
            "role": "method",
            "claim": (
                f"Fixed-window KG has {metrics['kg']['fixed_window_triples']} triples; "
                f"structure-aware KG has {metrics['kg']['structure_aware_triples']} triples."
            ),
            "visual": "reports/final/assets/kg_evidence_ai.png",
            "evidence_sources": [
                "reports/stages/kg_validation.json",
                "reports/stages/structure_aware_kg_validation.json",
            ],
            "speaker_note": "Stress evidence/provenance validation rather than raw triple count.",
        },
        {
            "slide_number": 6,
            "title": "Structure-aware chunking is the best current retrieval candidate",
            "role": "result",
            "claim": (
                f"Best strategy: {metrics['chunking']['best_strategy']} with Recall@5="
                f"{metrics['chunking']['best_recall_at_5']} and MRR@5="
                f"{metrics['chunking']['best_mrr_at_5']}."
            ),
            "visual": "chunking comparison bar chart",
            "evidence_sources": ["reports/stages/chunking_comparison.json"],
            "speaker_note": "Explain handbook structure, not just the metric ranking.",
        },
        {
            "slide_number": 7,
            "title": "GraphRAG should be judged as structured evidence, not just page Recall",
            "role": "result",
            "claim": (
                f"Structure-aware hybrid Recall@5="
                f"{metrics['hybrid_rag']['structure_hybrid_recall_at_5']} and KG coverage="
                f"{metrics['hybrid_rag']['structure_hybrid_kg_coverage']}."
            ),
            "visual": "layered retrieval metric comparison",
            "evidence_sources": [
                "reports/stages/hybrid_rag_structure_aware.json",
                "reports/stages/graphrag_review.json",
            ],
            "speaker_note": "Defend why a graph layer matters even when vector Recall is high.",
        },
        {
            "slide_number": 8,
            "title": "Evidence-level scoring favors the structure-aware hybrid run",
            "role": "result",
            "claim": (
                f"Structure-aware hybrid supports "
                f"{metrics['hybrid_rag']['structure_supported_answers']} answers versus "
                f"{metrics['hybrid_rag']['fixed_supported_answers']} for fixed-window hybrid."
            ),
            "visual": "supported answer distribution",
            "evidence_sources": ["reports/stages/evidence_level_evaluation.json"],
            "speaker_note": "Use this as the strongest experiment-level defense claim.",
        },
        {
            "slide_number": 9,
            "title": "The web demo turns raw evidence into an inspectable explanation surface",
            "role": "demo",
            "claim": (
                f"Readiness={metrics['web_demo']['ready']}; default strategy="
                f"{metrics['web_demo']['default_strategy']}; smoke="
                f"{metrics['web_demo']['smoke_ready']}."
            ),
            "visual": "reports/final/assets/web_demo_ai.png",
            "evidence_sources": [
                "reports/stages/web_demo_readiness.json",
                "reports/stages/web_demo_final_smoke.json",
            ],
            "speaker_note": "Show answer, chunks, KG triples, KG graph, and Why This Result.",
        },
        {
            "slide_number": 10,
            "title": "Current limitations define the next evaluation work",
            "role": "discussion",
            "claim": (
                "Gold labels are reviewed for source alignment; the next hardening step "
                "is external review, CI, and broader document coverage."
            ),
            "visual": "limitation to next-work ladder",
            "evidence_sources": [
                "data/cqs/06_phak_ch4_0.gold.json",
                "reports/stages/final_evaluation_review.json",
                "TASKS.md",
            ],
            "speaker_note": "Be explicit about what the project does not prove yet.",
        },
        {
            "slide_number": 11,
            "title": "The assistant is for aviation learning support, not operational authority",
            "role": "boundary",
            "claim": (
                "Learning and decision-support only; not a POH, checklist, ATC, "
                "instructor, or pilot-judgment substitute."
            ),
            "visual": "boundary statement",
            "evidence_sources": ["src/aviation_agentic_ai/advisory.py"],
            "speaker_note": (
                "Say the full advisory boundary before and after the demo if asked about "
                "real flight use."
            ),
        },
        {
            "slide_number": 12,
            "title": "The final contribution is an auditable prototype and a reproducible experiment protocol",
            "role": "conclusion",
            "claim": "The work is defensible because its claims are linked to artifacts, metrics, and reproducibility commands.",
            "visual": "takeaway checklist",
            "evidence_sources": common_sources + ["reports/final/project_defense_notes.md"],
            "speaker_note": "End on this slide for Q&A.",
        },
        {
            "slide_number": 13,
            "title": "The artifact index makes the experiment reproducible after the talk",
            "role": "appendix",
            "claim": "All deck claims map back to local source files, reports, and generated evidence artifacts.",
            "visual": "artifact index grid",
            "evidence_sources": [
                "reports/stages/index.json",
                "reports/final/aviation_graphrag_defense_deck_sources.json",
                "reports/final/project_report_sources.json",
            ],
            "speaker_note": "Use this appendix slide only when asked where a metric or artifact came from.",
        },
    ]
    return {
        "generated_at": _now(),
        "skills_used": ACADEMIC_SKILLS,
        "presentation_type": "structured_argument",
        "deck_profile": "engineering-platform",
        "design_system": {
            "background": "white",
            "primary": "dark navy",
            "accent": "mid blue",
            "font": "single sans-serif",
            "rule": "one action title and one evidence object per slide",
        },
        "metrics_snapshot": metrics,
        "visual_assets": summary["visual_assets"],
        "slides": slides,
        "qa_checklist": [
            "Every content slide has an action title.",
            "Reading action titles alone tells the argument.",
            "Every metric-bearing claim cites a local evidence source.",
            "Generated images are decorative/explanatory only and contain no fake metrics.",
            "A references/artifact-index appendix exists after the conclusion slide.",
            "The final non-appendix slide is a conclusion, not a thank-you slide.",
        ],
        "source_paths": summary["source_paths"],
    }


def build_defense_deck_outline_markdown(outline: dict[str, Any]) -> str:
    lines = [
        "# Aviation GraphRAG Defense Deck Outline",
        "",
        f"- Presentation type: `{outline['presentation_type']}`",
        f"- Deck profile: `{outline['deck_profile']}`",
        "- Design: white academic technical deck, dark navy primary, sparse blue accents.",
        "",
        "## Slide Spine",
        "",
    ]
    for slide in outline["slides"]:
        lines.extend(
            [
                f"### {slide['slide_number']}. {slide['title']}",
                "",
                f"- Role: `{slide['role']}`",
                f"- Claim: {slide['claim']}",
                f"- Visual: {slide['visual']}",
                "- Sources: "
                + ", ".join(f"`{source}`" for source in slide["evidence_sources"]),
                f"- Speaker note: {slide['speaker_note']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Academic QA Checklist",
            "",
            *[f"- {item}" for item in outline["qa_checklist"]],
            "",
            "## Source Paths",
            "",
            *[f"- `{path}`" for path in outline["source_paths"]],
            "",
        ]
    )
    return "\n".join(lines)


def _write_json(data: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def _write_markdown(markdown: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown.rstrip() + "\n", encoding="utf-8")
    return output_path


def build_visual_asset_svgs() -> dict[str, str]:
    return {
        "project_cover.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="1536" height="1024" viewBox="0 0 1536 1024" role="img" aria-label="Aviation GraphRAG academic cover diagram">
  <rect width="1536" height="1024" fill="#f8fafc"/>
  <rect x="96" y="112" width="1344" height="800" rx="48" fill="#ffffff" stroke="#d8e2ee" stroke-width="3"/>
  <path d="M230 650 C470 555 718 565 1120 394" fill="none" stroke="#1f4e79" stroke-width="10" stroke-linecap="round" opacity="0.12"/>
  <path d="M260 674 C515 585 766 594 1194 426" fill="none" stroke="#2e75b6" stroke-width="5" stroke-linecap="round" opacity="0.22"/>
  <g fill="#ffffff" stroke="#8fb3d8" stroke-width="3">
    <rect x="212" y="216" width="240" height="300" rx="20"/>
    <rect x="242" y="246" width="240" height="300" rx="20" opacity="0.9"/>
    <rect x="272" y="276" width="240" height="300" rx="20" opacity="0.85"/>
  </g>
  <g stroke="#b8c8da" stroke-width="8" stroke-linecap="round">
    <line x1="310" y1="344" x2="468" y2="344"/>
    <line x1="310" y1="404" x2="472" y2="404"/>
    <line x1="310" y1="464" x2="430" y2="464"/>
  </g>
  <g stroke="#1f4e79" stroke-width="5" opacity="0.82">
    <line x1="710" y1="326" x2="836" y2="262"/>
    <line x1="710" y1="326" x2="890" y2="392"/>
    <line x1="836" y1="262" x2="1012" y2="322"/>
    <line x1="890" y1="392" x2="1012" y2="322"/>
    <line x1="890" y1="392" x2="1038" y2="506"/>
    <line x1="1012" y1="322" x2="1156" y2="438"/>
  </g>
  <g fill="#ffffff" stroke="#2e75b6" stroke-width="5">
    <circle cx="710" cy="326" r="36"/>
    <circle cx="836" cy="262" r="30"/>
    <circle cx="890" cy="392" r="34"/>
    <circle cx="1012" cy="322" r="38"/>
    <circle cx="1038" cy="506" r="30"/>
    <circle cx="1156" cy="438" r="36"/>
  </g>
  <g fill="#eaf3fb" stroke="#2e75b6" stroke-width="3" opacity="0.95">
    <rect x="660" y="628" width="428" height="44" rx="22"/>
    <rect x="718" y="696" width="428" height="44" rx="22"/>
    <rect x="776" y="764" width="428" height="44" rx="22"/>
  </g>
  <circle cx="1214" cy="224" r="78" fill="#1f4e79" opacity="0.08"/>
  <circle cx="1250" cy="224" r="42" fill="#2e75b6" opacity="0.18"/>
</svg>
""",
        "pipeline_overview.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="1536" height="1024" viewBox="0 0 1536 1024" role="img" aria-label="PDF to Hybrid RAG pipeline diagram">
  <rect width="1536" height="1024" fill="#ffffff"/>
  <defs>
    <marker id="arrow" markerWidth="16" markerHeight="16" refX="14" refY="8" orient="auto">
      <path d="M0,0 L16,8 L0,16 z" fill="#1f4e79"/>
    </marker>
  </defs>
  <g fill="#f8fafc" stroke="#9fb6ce" stroke-width="3">
    <rect x="80" y="368" width="170" height="220" rx="20"/>
    <rect x="280" y="330" width="170" height="78" rx="20"/>
    <rect x="280" y="430" width="170" height="78" rx="20"/>
    <rect x="280" y="530" width="170" height="78" rx="20"/>
    <rect x="530" y="292" width="210" height="128" rx="24"/>
    <rect x="530" y="500" width="210" height="128" rx="24"/>
    <rect x="820" y="292" width="220" height="128" rx="24"/>
    <rect x="820" y="500" width="220" height="128" rx="24"/>
    <rect x="1128" y="386" width="250" height="160" rx="28"/>
  </g>
  <g stroke="#1f4e79" stroke-width="5" fill="none" marker-end="url(#arrow)">
    <path d="M250 478 H278"/>
    <path d="M450 370 H524"/>
    <path d="M450 470 C490 470 490 356 524 356"/>
    <path d="M450 570 C490 570 490 564 524 564"/>
    <path d="M740 356 H814"/>
    <path d="M740 564 H814"/>
    <path d="M1040 356 C1090 356 1088 440 1122 440"/>
    <path d="M1040 564 C1090 564 1088 492 1122 492"/>
  </g>
  <g stroke="#2e75b6" stroke-width="5" fill="#ffffff">
    <circle cx="595" cy="346" r="18"/>
    <circle cx="638" cy="376" r="18"/>
    <circle cx="684" cy="344" r="18"/>
    <line x1="595" y1="346" x2="638" y2="376"/>
    <line x1="638" y1="376" x2="684" y2="344"/>
    <circle cx="892" cy="548" r="18"/>
    <circle cx="942" cy="528" r="18"/>
    <circle cx="980" cy="574" r="18"/>
    <line x1="892" y1="548" x2="942" y2="528"/>
    <line x1="942" y1="528" x2="980" y2="574"/>
  </g>
  <g fill="#1f4e79" opacity="0.18">
    <rect x="118" y="424" width="96" height="12" rx="6"/>
    <rect x="118" y="464" width="96" height="12" rx="6"/>
    <rect x="118" y="504" width="70" height="12" rx="6"/>
    <circle cx="1242" cy="466" r="54"/>
    <rect x="1196" y="458" width="118" height="16" rx="8" fill="#2e75b6"/>
  </g>
</svg>
""",
        "ontology_kg_graphrag_concept.svg": """<svg xmlns="http://www.w3.org/2000/svg" width="1536" height="1024" viewBox="0 0 1536 1024" role="img" aria-label="Ontology constrained KG evidence for GraphRAG">
  <rect width="1536" height="1024" fill="#ffffff"/>
  <path d="M104 720 C378 604 638 618 1008 420 C1164 336 1288 282 1410 248" fill="none" stroke="#1f4e79" stroke-width="12" opacity="0.08"/>
  <g fill="#f8fafc" stroke="#9fb6ce" stroke-width="3">
    <rect x="116" y="196" width="270" height="90" rx="20"/>
    <rect x="116" y="322" width="270" height="90" rx="20"/>
    <rect x="116" y="448" width="270" height="90" rx="20"/>
    <rect x="116" y="574" width="270" height="90" rx="20"/>
    <rect x="116" y="700" width="270" height="90" rx="20"/>
  </g>
  <g stroke="#b8c8da" stroke-width="8" stroke-linecap="round">
    <line x1="158" y1="242" x2="314" y2="242"/>
    <line x1="158" y1="368" x2="306" y2="368"/>
    <line x1="158" y1="494" x2="330" y2="494"/>
    <line x1="158" y1="620" x2="286" y2="620"/>
    <line x1="158" y1="746" x2="318" y2="746"/>
  </g>
  <g stroke="#1f4e79" stroke-width="5" fill="none">
    <path d="M386 242 C488 242 488 346 588 346"/>
    <path d="M386 368 C492 368 488 440 588 440"/>
    <path d="M386 494 C488 494 492 534 588 534"/>
    <path d="M386 620 C492 620 488 628 588 628"/>
    <path d="M386 746 C492 746 488 722 588 722"/>
  </g>
  <g stroke="#2e75b6" stroke-width="5" fill="#ffffff">
    <circle cx="628" cy="346" r="32"/>
    <circle cx="754" cy="292" r="32"/>
    <circle cx="850" cy="384" r="32"/>
    <circle cx="724" cy="506" r="32"/>
    <circle cx="894" cy="572" r="32"/>
    <circle cx="768" cy="706" r="32"/>
    <line x1="628" y1="346" x2="754" y2="292"/>
    <line x1="754" y1="292" x2="850" y2="384"/>
    <line x1="628" y1="346" x2="724" y2="506"/>
    <line x1="724" y1="506" x2="894" y2="572"/>
    <line x1="724" y1="506" x2="768" y2="706"/>
    <line x1="850" y1="384" x2="894" y2="572"/>
  </g>
  <g fill="#f8fafc" stroke="#9fb6ce" stroke-width="3">
    <rect x="1056" y="250" width="324" height="108" rx="24"/>
    <rect x="1056" y="414" width="324" height="108" rx="24"/>
    <rect x="1056" y="578" width="324" height="160" rx="28"/>
  </g>
  <g stroke="#1f4e79" stroke-width="5" fill="none" marker-end="url(#arrow2)">
    <path d="M926 572 C990 572 990 632 1050 632"/>
    <path d="M926 384 C990 384 990 304 1050 304"/>
  </g>
  <defs>
    <marker id="arrow2" markerWidth="16" markerHeight="16" refX="14" refY="8" orient="auto">
      <path d="M0,0 L16,8 L0,16 z" fill="#1f4e79"/>
    </marker>
  </defs>
  <g fill="#2e75b6" opacity="0.2">
    <rect x="1100" y="302" width="180" height="14" rx="7"/>
    <rect x="1100" y="466" width="210" height="14" rx="7"/>
    <rect x="1100" y="640" width="222" height="14" rx="7"/>
    <rect x="1100" y="686" width="150" height="14" rx="7"/>
  </g>
</svg>
""",
    }


def write_visual_assets(output_dir: str | Path) -> tuple[list[Path], dict[str, Any]]:
    output = Path(output_dir)
    asset_dir = output / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for filename, svg in build_visual_asset_svgs().items():
        path = asset_dir / filename
        path.write_text(svg, encoding="utf-8")
        written.append(path)
    manifest_assets: list[dict[str, Any]] = []
    ai_asset_present = False
    for asset in VISUAL_ASSETS:
        asset_path = asset_dir / Path(asset["path"]).name
        fallback = asset.get("fallback_path")
        fallback_path = asset_dir / Path(fallback).name if fallback else None
        exists = asset_path.exists()
        if exists and asset_path.suffix.lower() == ".png":
            ai_asset_present = True
        manifest_assets.append(
            {
                **asset,
                "exists": exists,
                "fallback_exists": fallback_path.exists() if fallback_path else False,
            }
        )
    manifest = {
        "generated_at": _now(),
        "generation_method": (
            "ai_png_assets_with_local_svg_fallbacks"
            if ai_asset_present
            else "local_deterministic_svg_fallbacks"
        ),
        "uses_gateway_or_api": ai_asset_present,
        "api_metadata_policy": "No API key, token, or base URL is recorded in this manifest.",
        "assets": manifest_assets,
        "local_fallback_assets": [
            {
                "path": f"reports/final/assets/{filename}",
                "exists": (asset_dir / filename).exists(),
                "purpose": "Deterministic SVG fallback for reproducible report builds.",
            }
            for filename in sorted(build_visual_asset_svgs())
        ],
    }
    manifest_path = asset_dir / "visual_assets_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    written.append(manifest_path)
    return written, manifest


def write_academic_report(
    output_dir: str | Path,
    *,
    project_root: str | Path = PROJECT_ROOT,
    stage_index_path: str | Path | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    evidence = build_project_evidence_pack(
        project_root=project_root,
        stage_index_path=stage_index_path,
    )
    summary = build_academic_summary(evidence)
    markdown = build_academic_report_markdown(summary)
    output = Path(output_dir)
    md_path = _write_markdown(markdown, output / "project_academic_report.md")
    sources_path = _write_json(summary, output / "project_academic_report_sources.json")
    return md_path, sources_path, {
        "markdown": project_relative_path(md_path, base=project_root),
        "sources": project_relative_path(sources_path, base=project_root),
        "summary": summary,
    }


def write_defense_notes(
    output_dir: str | Path,
    *,
    project_root: str | Path = PROJECT_ROOT,
    stage_index_path: str | Path | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    evidence = build_project_evidence_pack(
        project_root=project_root,
        stage_index_path=stage_index_path,
    )
    summary = build_academic_summary(evidence)
    notes = build_defense_notes(summary)
    markdown = build_defense_notes_markdown(notes)
    output = Path(output_dir)
    md_path = _write_markdown(markdown, output / "project_defense_notes.md")
    json_path = _write_json(notes, output / "project_defense_notes.json")
    return md_path, json_path, notes


def write_defense_deck_outline(
    output_dir: str | Path,
    *,
    project_root: str | Path = PROJECT_ROOT,
    stage_index_path: str | Path | None = None,
) -> tuple[Path, Path, dict[str, Any]]:
    evidence = build_project_evidence_pack(
        project_root=project_root,
        stage_index_path=stage_index_path,
    )
    summary = build_academic_summary(evidence)
    outline = build_defense_deck_outline(summary)
    markdown = build_defense_deck_outline_markdown(outline)
    output = Path(output_dir)
    md_path = _write_markdown(markdown, output / "defense_deck_outline.md")
    json_path = _write_json(outline, output / "aviation_graphrag_defense_deck_sources.json")
    return md_path, json_path, outline
