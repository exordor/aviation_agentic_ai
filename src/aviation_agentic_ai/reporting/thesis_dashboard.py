from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.accessors import nested_value as _metric
from aviation_agentic_ai.reporting.evaluation_protocol import PRIMARY_THESIS_METRICS
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report


REPORT_SOURCES: dict[str, str] = {
    "thesis_claims_review": "reports/stages/thesis_claims_review.json",
    "evaluation_protocol_review": "reports/stages/evaluation_protocol_review.json",
    "benchmark_v2_summary": "reports/stages/benchmark_v2_summary.json",
    "retrieval_ablation_benchmark_v2": "reports/stages/retrieval_ablation_benchmark_v2.json",
    "graph_traversal_ablation_benchmark_v2": "reports/stages/graph_traversal_ablation_benchmark_v2.json",
    "sufficiency_evaluation": "reports/stages/sufficiency_evaluation.json",
    "benchmark_reviewed_subset_summary": "reports/stages/benchmark_reviewed_subset_summary.json",
    "benchmark_llm_review": "reports/stages/benchmark_llm_review.json",
    "benchmark_llm_rewrite_proposals": "reports/stages/benchmark_llm_rewrite_proposals.json",
    "answer_evaluation_benchmark_subset": "reports/stages/answer_evaluation_benchmark_subset.json",
    "answer_generation_benchmark_subset": "reports/stages/answer_generation_benchmark_subset.json",
    "answer_llm_judge": "reports/stages/answer_llm_judge.json",
    "triple_semantic_llm_review": "reports/stages/triple_semantic_llm_review.json",
    "graph_path_llm_review": "reports/stages/graph_path_llm_review.json",
    "llm_review_consistency": "reports/stages/llm_review_consistency.json",
    "chunking_implementation_audit": "reports/stages/chunking_implementation_audit.json",
    "chunking_comparison_benchmark_v2": "reports/stages/chunking_comparison_benchmark_v2.json",
    "chunking_comparison_benchmark_v2_budget": "reports/stages/chunking_comparison_benchmark_v2_budget.json",
    "chunking_topk_sensitivity_benchmark_v2": "reports/stages/chunking_topk_sensitivity_benchmark_v2.json",
    "chunking_category_analysis_benchmark_v2": "reports/stages/chunking_category_analysis_benchmark_v2.json",
    "chunking_failure_cards_benchmark_v2": "reports/stages/chunking_failure_cards_benchmark_v2.json",
    "deepseek_v4pro_implementation_remediation": (
        "reports/reviews/deepseek_v4pro_implementation_remediation.json"
    ),
    "kg_extraction_comparison": "reports/stages/kg_extraction_comparison.json",
    "curated_ontology_evaluation": "reports/stages/curated_ontology_evaluation.json",
    "triple_semantic_review_sample": "reports/stages/triple_semantic_review_sample.json",
    "answer_evaluation": "reports/stages/answer_evaluation.json",
    "robustness_evaluation": "reports/stages/robustness_evaluation.json",
    "benchmark_review_pack": "reports/stages/benchmark_review_pack.json",
}

UNSAFE_PATTERNS = (
    "graphrag always improves recall",
    "graphrag universally improves recall",
    "externally aviation-expert certified",
    "external aviation-expert certification",
    "certified aviation assistant",
    "operational flight readiness",
    "operationally safe for flight decisions",
    "support operational flight decisions",
    "replace poh",
    "replace the aircraft poh",
    "replace approved checklists",
    "replace atc",
    "human reviewed",
    "manual reviewed",
    "manual-review dependent",
    "expert reviewed",
    "expert gold",
    "aviation expert validated",
    "semantically correct triples",
    "proven safe",
    "operationally safe",
    "flight-ready",
)

SAFE_UNSUPPORTED_CONTEXT_MARKERS = (
    "avoid",
    "unsafe wording",
    "must not claim",
    "does not",
    "do not",
    "not assume",
    "not supported",
    "not external",
    "no human",
    "human review is absent",
    "not human",
    "not certified",
    "not operational",
    "should not",
)

SAFE_UNSUPPORTED_CONTEXT_SECTIONS = (
    "claim safety matrix",
    "what the thesis must not claim",
    "consistency checks",
)


def _load_json(path: Path) -> dict[str, Any]:
    return read_json_object_or_empty(path, wrap_non_object=True)


def _report_inventory(reports: dict[str, dict[str, Any]], root: Path) -> list[dict[str, Any]]:
    layer_map = {
        "thesis_claims_review": ("claim_safety",),
        "evaluation_protocol_review": ("evaluation_protocol",),
        "benchmark_v2_summary": ("benchmark_validation",),
        "retrieval_ablation_benchmark_v2": ("retrieval", "kg_evidence"),
        "graph_traversal_ablation_benchmark_v2": ("retrieval", "graph_paths"),
        "sufficiency_evaluation": ("safety_abstention",),
        "benchmark_reviewed_subset_summary": ("benchmark_llm_review_scaffold",),
        "benchmark_llm_review": ("benchmark_llm_review", "llm_judge"),
        "benchmark_llm_rewrite_proposals": ("benchmark_llm_review",),
        "answer_evaluation_benchmark_subset": ("answer_generation", "safety_abstention"),
        "answer_generation_benchmark_subset": ("answer_generation",),
        "answer_llm_judge": ("answer_generation", "llm_judge"),
        "triple_semantic_llm_review": ("ontology_kg", "llm_judge"),
        "graph_path_llm_review": ("graph_paths", "llm_judge"),
        "llm_review_consistency": ("llm_judge", "claim_safety"),
        "chunking_implementation_audit": ("retrieval", "evaluation_protocol"),
        "chunking_comparison_benchmark_v2": ("retrieval",),
        "chunking_comparison_benchmark_v2_budget": ("retrieval",),
        "chunking_topk_sensitivity_benchmark_v2": ("retrieval",),
        "chunking_category_analysis_benchmark_v2": ("retrieval",),
        "chunking_failure_cards_benchmark_v2": ("retrieval", "failure_analysis"),
        "deepseek_v4pro_implementation_remediation": (
            "implementation_review",
            "claim_safety",
        ),
        "kg_extraction_comparison": ("ontology_kg",),
        "curated_ontology_evaluation": ("ontology_kg",),
        "triple_semantic_review_sample": ("ontology_kg", "llm_review_scaffold"),
        "answer_evaluation": ("answer_generation", "safety_abstention"),
        "robustness_evaluation": ("safety_abstention", "robustness"),
        "benchmark_review_pack": ("benchmark_llm_review_scaffold",),
    }
    dataset_map = {
        "benchmark_v2_summary": "benchmark_v2_120",
        "retrieval_ablation_benchmark_v2": "benchmark_v2_120",
        "graph_traversal_ablation_benchmark_v2": "benchmark_v2_120",
        "sufficiency_evaluation": "benchmark_v2_120",
        "benchmark_reviewed_subset_summary": "benchmark_v2_reviewed_subset_60",
        "benchmark_llm_review": "benchmark_v2_reviewed_subset_or_v2",
        "benchmark_llm_rewrite_proposals": "benchmark_v2_reviewed_subset_or_v2",
        "answer_evaluation_benchmark_subset": "answer_eval_subset",
        "answer_generation_benchmark_subset": "answer_eval_subset",
        "answer_llm_judge": "answer_eval_subset",
        "triple_semantic_llm_review": "triple_semantic_review_sample",
        "graph_path_llm_review": "benchmark_v2_120",
        "llm_review_consistency": "llm_review_artifacts",
        "chunking_implementation_audit": "benchmark_v2_120",
        "chunking_comparison_benchmark_v2": "benchmark_v2_120",
        "chunking_comparison_benchmark_v2_budget": "benchmark_v2_120",
        "chunking_topk_sensitivity_benchmark_v2": "benchmark_v2_120",
        "chunking_category_analysis_benchmark_v2": "benchmark_v2_120",
        "chunking_failure_cards_benchmark_v2": "benchmark_v2_120",
        "deepseek_v4pro_implementation_remediation": "not_dataset_specific",
        "answer_evaluation": "10_cq_answer_subset",
        "robustness_evaluation": "robustness_10_cases",
        "kg_extraction_comparison": "35_question_expanded",
        "triple_semantic_review_sample": "triple_semantic_review_sample",
    }
    inventory = []
    for name, rel_path in REPORT_SOURCES.items():
        path = root / rel_path
        data = reports.get(name, {})
        inventory.append(
            {
                "report_name": name,
                "path": rel_path,
                "present": path.exists(),
                "dataset_used": dataset_map.get(name, "not_dataset_specific"),
                "questions_count": _metric(
                    data,
                    "metadata",
                    "questions_total",
                    default=_metric(data, "metadata", "labels_total", default="n/a"),
                ),
                "metric_layers_covered": list(layer_map.get(name, ())),
                "human_review_present": False,
                "llm_review_available": "llm" in name,
            }
        )
    return inventory


def _scenario_metrics(report: dict[str, Any], scenario: str) -> dict[str, Any]:
    return _metric(report, "scenarios", scenario, "aggregate", default={})


def _primary_results(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    retrieval = reports["retrieval_ablation_benchmark_v2"]
    traversal = reports["graph_traversal_ablation_benchmark_v2"]
    sufficiency = reports["sufficiency_evaluation"]
    robustness = reports["robustness_evaluation"]
    reviewed_subset = reports.get("benchmark_reviewed_subset_summary", {})
    answer_subset = reports.get("answer_evaluation_benchmark_subset", {})
    chunking_audit = reports.get("chunking_implementation_audit", {})
    chunking_topk = reports.get("chunking_comparison_benchmark_v2", {})
    chunking_budget = reports.get("chunking_comparison_benchmark_v2_budget", {})
    chunking_sensitivity = reports.get("chunking_topk_sensitivity_benchmark_v2", {})
    chunking_category = reports.get("chunking_category_analysis_benchmark_v2", {})
    kg = reports["kg_extraction_comparison"]
    triple = reports["triple_semantic_review_sample"]
    benchmark_llm = reports.get("benchmark_llm_review", {})
    triple_llm = reports.get("triple_semantic_llm_review", {})
    graph_path_llm = reports.get("graph_path_llm_review", {})
    answer_generation = reports.get("answer_generation_benchmark_subset", {})
    answer_llm = reports.get("answer_llm_judge", {})
    llm_consistency = reports.get("llm_review_consistency", {})
    implementation_remediation = reports.get("deepseek_v4pro_implementation_remediation", {})

    vector = _scenario_metrics(retrieval, "vector_hops2_v5_h8")
    hybrid = _scenario_metrics(retrieval, "hybrid_hops2_v5_h8")
    guarded = _scenario_metrics(traversal, "hybrid_vector_traversal_guarded")
    traversal_graph = _scenario_metrics(traversal, "traversal_graph_2_hop")
    structure_kg = _metric(kg, "experiments", "structure_aware", default={})
    suff_metrics = sufficiency.get("metrics", {})
    return {
        "vector_only": {
            "recall_at_5": _metric(vector, "retrieval", "recall_at_5"),
            "recall_at_10": _metric(vector, "retrieval", "recall_at_10"),
            "mrr_at_5": _metric(vector, "retrieval", "mrr_at_5"),
            "ndcg_at_10": _metric(vector, "retrieval", "ndcg_at_10"),
            "confidence_intervals": vector.get("retrieval_confidence_intervals", {}),
        },
        "best_lexical_hybrid": {
            "scenario": "hybrid_hops2_v5_h8",
            "recall_at_5": _metric(hybrid, "retrieval", "recall_at_5"),
            "recall_at_10": _metric(hybrid, "retrieval", "recall_at_10"),
            "mrr_at_5": _metric(hybrid, "retrieval", "mrr_at_5"),
            "ndcg_at_10": _metric(hybrid, "retrieval", "ndcg_at_10"),
            "context_recall": _metric(hybrid, "retrieval", "context_recall"),
            "kg_evidence_coverage": _metric(hybrid, "kg_evidence", "evidence_coverage"),
            "confidence_intervals": hybrid.get("retrieval_confidence_intervals", {}),
        },
        "traversal_hybrid": {
            "scenario": "hybrid_vector_traversal_guarded",
            "recall_at_5": _metric(guarded, "retrieval", "recall_at_5"),
            "path_recall_at_5": _metric(guarded, "graph_paths", "path_recall_at_5"),
            "path_precision_at_5": _metric(guarded, "graph_paths", "path_precision_at_5"),
            "path_metrics_require_model_review": _metric(
                guarded,
                "graph_paths",
                "requires_model_review",
            ),
            "human_review": False,
        },
        "standalone_traversal": {
            "path_coverage": _metric(traversal_graph, "graph_paths", "path_coverage"),
            "recall_at_5": _metric(traversal_graph, "retrieval", "recall_at_5"),
        },
        "sufficiency": {
            "abstention_accuracy": suff_metrics.get("abstention_accuracy"),
            "false_answer_rate": suff_metrics.get("false_answer_rate"),
            "false_abstention_rate": suff_metrics.get("false_abstention_rate"),
            "risk_category_accuracy": suff_metrics.get("risk_category_accuracy"),
            "confidence_intervals": sufficiency.get("confidence_intervals", {}),
        },
        "robustness": {
            "abstention_correctness": _metric(
                robustness,
                "aggregate",
                "abstention_correctness",
            ),
            "false_answer_rate": _metric(robustness, "aggregate", "false_answer_rate"),
            "advisory_boundary_violation_count": _metric(
                robustness,
                "aggregate",
                "advisory_boundary_violation_count",
            ),
        },
        "benchmark_reviewed_subset": {
            "labels_total": _metric(reviewed_subset, "metadata", "labels_total"),
            "review_status": _metric(reviewed_subset, "metadata", "review_status"),
            "external_aviation_expert_certified": _metric(
                reviewed_subset,
                "metadata",
                "external_aviation_expert_certified",
            ),
            "human_review_completed": _metric(
                reviewed_subset,
                "metadata",
                "human_review_completed",
            ),
            "llm_review_completed": _metric(
                reviewed_subset,
                "metadata",
                "llm_review_completed",
            ),
        },
        "answer_evaluation_benchmark_subset": {
            "answers_total": _metric(answer_subset, "metadata", "answers_total"),
            "evaluation_status": _metric(answer_subset, "metadata", "evaluation_status"),
            "unmatched_gold_labels": _metric(
                answer_subset,
                "metadata",
                "unmatched_gold_labels",
            ),
            "hybrid_faithfulness": _metric(
                answer_subset,
                "aggregate",
                "hybrid",
                "faithfulness",
            ),
            "score_method": "deterministic_heuristic",
        },
        "chunking_benchmark_v2": {
            "audit_status": _metric(
                chunking_audit,
                "metadata",
                "claim_policy",
            ),
            "topk_best_strategy": _metric(
                chunking_topk,
                "ranking",
                default=[{"strategy": "TBD"}],
            )[0].get("strategy", "TBD")
            if isinstance(_metric(chunking_topk, "ranking", default=[]), list)
            and _metric(chunking_topk, "ranking", default=[])
            else "TBD",
            "topk_recall_at_5_supported": _metric(
                chunking_topk,
                "ranking",
                default=[{"recall_at_5_supported": "TBD"}],
            )[0].get("recall_at_5_supported", "TBD")
            if isinstance(_metric(chunking_topk, "ranking", default=[]), list)
            and _metric(chunking_topk, "ranking", default=[])
            else "TBD",
            "budget_best_strategy": _metric(
                chunking_budget,
                "ranking",
                default=[{"strategy": "TBD"}],
            )[0].get("strategy", "TBD")
            if isinstance(_metric(chunking_budget, "ranking", default=[]), list)
            and _metric(chunking_budget, "ranking", default=[])
            else "TBD",
            "budget_recall_at_5_supported": _metric(
                chunking_budget,
                "ranking",
                default=[{"recall_at_5_supported": "TBD"}],
            )[0].get("recall_at_5_supported", "TBD")
            if isinstance(_metric(chunking_budget, "ranking", default=[]), list)
            and _metric(chunking_budget, "ranking", default=[])
            else "TBD",
            "topk_sensitivity_best_by_k": {
                key: rows[0].get("strategy", "TBD")
                for key, rows in chunking_sensitivity.get("rankings", {}).items()
                if isinstance(rows, list) and rows
            },
            "category_best": {
                key: value.get("strategy", "TBD")
                for key, value in chunking_category.get("best_by_category", {}).items()
                if isinstance(value, dict)
            },
            "partial_methods": [
                row.get("strategy")
                for row in chunking_audit.get("strategies", [])
                if isinstance(row, dict)
                and str(row.get("implementation_status", "")).startswith("partial")
            ],
            "semantic_backend": _metric(
                chunking_topk,
                "strategies",
                "embedding_semantic",
                "implementation_metadata",
                "semantic_backend",
                default="TBD",
            ),
            "claim_warning": (
                "Top-k chunking rankings expose unequal context budgets; fixed-budget "
                "and category diagnostics are stronger evidence but still benchmark-specific."
            ),
        },
        "kg": {
            "provenance_completeness": structure_kg.get("provenance_complete_rate"),
            "evidence_in_source_rate": structure_kg.get("evidence_in_chunk_rate"),
            "valid_triples": structure_kg.get("valid_triples"),
            "unsupported_triple_count": structure_kg.get("unsupported_triple_count"),
        },
        "triple_semantic_review": {
            "sample_size": _metric(triple, "metadata", "sample_size"),
            "reviewed": _metric(triple, "summary", "reviewed"),
            "needs_review": _metric(triple, "summary", "needs_review"),
            "semantic_correctness_claimed": _metric(
                triple,
                "metadata",
                "semantic_correctness_claimed",
            ),
        },
        "llm_review_status": {
            "benchmark": {
                "records": _metric(benchmark_llm, "summary", "items_total"),
                "llm_reviewed": _metric(benchmark_llm, "summary", "llm_reviewed_total"),
                "status": _metric(benchmark_llm, "summary", "review_status"),
            },
            "triple_semantic": {
                "records": _metric(triple_llm, "summary", "items_total"),
                "llm_reviewed": _metric(triple_llm, "summary", "llm_reviewed_total"),
                "evidence_support_rate": _metric(
                    triple_llm,
                    "summary",
                    "llm_evidence_support_rate",
                ),
            },
            "graph_paths": {
                "records": _metric(graph_path_llm, "summary", "items_total"),
                "llm_reviewed": _metric(graph_path_llm, "summary", "llm_reviewed_total"),
                "path_relevance_rate": _metric(
                    graph_path_llm,
                    "summary",
                    "llm_path_relevance_rate",
                ),
            },
            "answer_generation": {
                "answers_total": _metric(answer_generation, "metadata", "answers_total"),
                "status": _metric(answer_generation, "metadata", "evaluation_status"),
            },
            "answer_judge": {
                "records": _metric(answer_llm, "summary", "items_total"),
                "llm_reviewed": _metric(answer_llm, "summary", "llm_reviewed_total"),
                "correctness_rate": _metric(
                    answer_llm,
                    "summary",
                    "llm_answer_correctness_rate",
                ),
            },
            "consistency": {
                "agreement_rate": _metric(llm_consistency, "summary", "agreement_rate"),
                "consistency_not_measured": _metric(
                    llm_consistency,
                    "summary",
                    "consistency_not_measured",
                ),
            },
            "metric_source_policy": {
                "deterministic": "retrieval, validation, sufficiency, provenance",
                "heuristic": "path overlap and answer heuristic metrics",
                "llm_judge": "model-based review artifacts only",
                "human_review": "absent_false",
            },
            "human_review": False,
            "external_expert_certified": False,
            "aviation_expert_certified": False,
        },
        "implementation_review_remediation": {
            "status": implementation_remediation.get("status", "not_present"),
            "implemented_items": sum(
                1
                for item in implementation_remediation.get("items", [])
                if isinstance(item, dict) and item.get("remediation_status") == "implemented"
            ),
            "verified_already_fixed_items": sum(
                1
                for item in implementation_remediation.get("items", [])
                if isinstance(item, dict)
                and item.get("remediation_status") == "verified_already_fixed"
            ),
            "deferred_items": implementation_remediation.get("deferred_items", []),
            "scientific_metrics_changed": _metric(
                implementation_remediation,
                "policy",
                "scientific_metrics_changed",
                default=False,
            ),
            "human_review_claimed": _metric(
                implementation_remediation,
                "policy",
                "human_review_claimed",
                default=False,
            ),
            "external_aviation_expert_certified": _metric(
                implementation_remediation,
                "policy",
                "external_aviation_expert_certified",
                default=False,
            ),
        },
    }


def _failure_summary(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    traversal = reports["graph_traversal_ablation_benchmark_v2"]
    categories: Counter[str] = Counter()
    for scenario in traversal.get("scenarios", {}).values():
        if not isinstance(scenario, dict):
            continue
        for failure in scenario.get("failure_cases", []):
            categories.update(failure.get("failure_categories", []))
    sufficiency_errors = [
        record
        for record in reports["sufficiency_evaluation"].get("records", [])
        if record.get("expected_decision") == "answer"
        and record.get("decision", {}).get("decision") == "abstain"
    ]
    benchmark_findings = reports.get("benchmark_review_pack", {}).get("finding_counts", {})
    triple = reports["triple_semantic_review_sample"]
    chunking_failure_cards = reports.get("chunking_failure_cards_benchmark_v2", {})
    chunking_failures: Counter[str] = Counter()
    for failures in chunking_failure_cards.get("strategies", {}).values():
        if not isinstance(failures, dict):
            continue
        for failure_type, failure in failures.items():
            if isinstance(failure, dict):
                chunking_failures[failure_type] += int(failure.get("samples_total", 0))
    return {
        "graph_failure_categories": dict(sorted(categories.items())),
        "chunking_failure_card_samples": dict(sorted(chunking_failures.items())),
        "false_abstention_on_supported_question": len(sufficiency_errors),
        "machine_seeded_benchmark_wording": benchmark_findings.get(
            "unnatural_machine_generated_wording",
            0,
        ),
        "missing_llm_triple_review": _metric(triple, "summary", "needs_review", default=0),
        "notes": [
            "High path coverage is interpreted separately from Recall@k.",
            "Human review is absent; model-based review artifacts must be cited separately.",
        ],
    }


def _dataset_usage_matrix() -> list[dict[str, Any]]:
    return [
        {
            "dataset": "10-CQ pilot",
            "purpose": "demo and qualitative answer inspection",
            "used_in_reports": ["hybrid_rag_experiment", "answer_evaluation"],
            "limitations": "too small for main thesis retrieval claims",
            "can_support_thesis_main_claim": "partial",
            "evidence_role": "pilot",
        },
        {
            "dataset": "35-question expanded",
            "purpose": "pilot ablation and KG extraction comparison",
            "used_in_reports": ["retrieval_ablation", "kg_extraction_comparison"],
            "limitations": "pilot-sized and not the main benchmark",
            "can_support_thesis_main_claim": "partial",
            "evidence_role": "pilot",
        },
        {
            "dataset": "benchmark v2 120",
            "purpose": "main thesis retrieval and safety benchmark",
            "used_in_reports": [
                "benchmark_v2_summary",
                "retrieval_ablation_benchmark_v2",
                "graph_traversal_ablation_benchmark_v2",
                "sufficiency_evaluation",
                "chunking_comparison_benchmark_v2",
                "chunking_comparison_benchmark_v2_budget",
                "chunking_topk_sensitivity_benchmark_v2",
                "chunking_category_analysis_benchmark_v2",
            ],
            "limitations": "machine-seeded and requires model-based naturalness review",
            "can_support_thesis_main_claim": "provisional_internal_pending_llm_review",
            "evidence_role": "main_thesis_benchmark",
        },
        {
            "dataset": "benchmark v2 chunking experiment",
            "purpose": "chunking strategy comparison under top-k, fixed-budget, and category views",
            "used_in_reports": [
                "chunking_implementation_audit",
                "chunking_comparison_benchmark_v2",
                "chunking_comparison_benchmark_v2_budget",
                "chunking_topk_sensitivity_benchmark_v2",
                "chunking_category_analysis_benchmark_v2",
            ],
            "limitations": (
                "implementation-maturity labels required; top-k context volume differs by chunk size"
            ),
            "can_support_thesis_main_claim": "partial_benchmark_specific",
            "evidence_role": "retrieval_design_diagnostic",
        },
        {
            "dataset": "benchmark reviewed subset 60",
            "purpose": "model-based review scaffold for high-value labels",
            "used_in_reports": ["benchmark_reviewed_subset_summary"],
            "limitations": "review scaffold only; no human review or external aviation expert certification",
            "can_support_thesis_main_claim": "pending_llm_review",
            "evidence_role": "llm_review_scaffold",
        },
        {
            "dataset": "LLM review artifacts",
            "purpose": "model-based benchmark, triple, graph-path, answer, and consistency review",
            "used_in_reports": [
                "benchmark_llm_review",
                "triple_semantic_llm_review",
                "graph_path_llm_review",
                "answer_llm_judge",
                "llm_review_consistency",
            ],
            "limitations": "model-based internal review; no human or external expert certification",
            "can_support_thesis_main_claim": "internal_llm_review_only",
            "evidence_role": "llm_judge",
        },
        {
            "dataset": "answer-eval subset",
            "purpose": "answer citation and faithfulness heuristics",
            "used_in_reports": ["answer_evaluation", "answer_evaluation_benchmark_subset"],
            "limitations": "stratified subset; deterministic heuristic scores unless annotated",
            "can_support_thesis_main_claim": "partial",
            "evidence_role": "pilot",
        },
        {
            "dataset": "triple semantic review sample",
            "purpose": "KG semantic correctness review template",
            "used_in_reports": ["triple_semantic_review_sample"],
            "limitations": "review fields pending until model-based review is run; no expert correctness claimed",
            "can_support_thesis_main_claim": "partial",
            "evidence_role": "llm_review_pending",
        },
    ]


def _rq_evidence_matrix(primary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "rq": "RQ1 ontology constraint",
            "evidence_reports": [
                "curated_ontology_evaluation",
                "kg_extraction_comparison",
                "kg_validation",
            ],
            "primary_metrics": [
                "RDF/OWL parse validity",
                "label/comment coverage",
                "unsupported class/property count",
                "provenance completeness",
            ],
            "current_result_summary": (
                "Curated ontology validates as a task ontology; structure-aware KG "
                f"has provenance completeness={primary['kg']['provenance_completeness']}."
            ),
            "claim_strength": "strong",
            "remaining_gaps": "Triple semantic correctness is absent or LLM-estimated only.",
        },
        {
            "rq": "RQ2 evidence traceability",
            "evidence_reports": [
                "retrieval_ablation_benchmark_v2",
                "graph_traversal_ablation_benchmark_v2",
                "answer_evaluation",
            ],
            "primary_metrics": [
                "KG evidence coverage",
                "citation completeness",
                "citation precision",
                "citation recall",
            ],
            "current_result_summary": (
                "Hybrid reports expose KG evidence and citations; answer scores are "
                "deterministic heuristics unless LLM-judge scores are explicitly recorded."
            ),
            "claim_strength": "moderate",
            "remaining_gaps": "Answer-level LLM-judge evaluation must remain separate from deterministic metrics.",
        },
        {
            "rq": "RQ3 graph evidence vs vector sufficiency",
            "evidence_reports": [
                "retrieval_ablation_benchmark_v2",
                "graph_traversal_ablation_benchmark_v2",
                "chunking_comparison_benchmark_v2",
                "chunking_comparison_benchmark_v2_budget",
                "chunking_topk_sensitivity_benchmark_v2",
                "chunking_category_analysis_benchmark_v2",
            ],
            "primary_metrics": [
                "Recall@5",
                "Recall@10",
                "MRR@5",
                "NDCG@10",
                "Path Recall@5",
                "Path Precision@5",
                "Fixed-budget chunking Recall@5",
            ],
            "current_result_summary": (
                "Vector and hybrid retrieval are reported separately. Graph traversal "
                "can improve path evidence without guaranteeing Recall improvement. "
                "Chunking-v2 is reported with top-k, fixed-budget, and category views."
            ),
            "claim_strength": "moderate",
            "remaining_gaps": "Path relevance is heuristic or model-reviewed, not human-validated.",
        },
        {
            "rq": "RQ4 safety-aware abstention",
            "evidence_reports": ["sufficiency_evaluation", "robustness_evaluation"],
            "primary_metrics": [
                "Abstention Accuracy",
                "False Answer Rate",
                "False Abstention Rate",
                "Risk Category Accuracy",
            ],
            "current_result_summary": (
                f"Benchmark v2 abstention accuracy={primary['sufficiency']['abstention_accuracy']} "
                f"and false answer rate={primary['sufficiency']['false_answer_rate']}; "
                "false abstentions remain visible."
            ),
            "claim_strength": "moderate",
            "remaining_gaps": "Sufficiency can create false abstentions on supported questions.",
        },
    ]


def _claim_summary(reports: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    claims = reports["thesis_claims_review"].get("claim_safety_matrix", [])
    summary: list[dict[str, Any]] = []
    for claim in claims:
        if not isinstance(claim, dict):
            continue
        summary.append(
            {
                "claim": claim.get("claim"),
                "safe_wording": claim.get("safe_wording"),
                "evidence": claim.get("evidence_files", []),
                "limitations": claim.get("current_evidence"),
                "supported_strength": claim.get("supported_strength"),
                "unsafe_wording_to_avoid": claim.get("unsafe_wording_to_avoid"),
            }
        )
    return summary


def _primary_metric_report_gaps(root: Path) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for group in PRIMARY_THESIS_METRICS:
        expected_reports = [
            str(report_path)
            for report_path in group.get("reports", ())
            if isinstance(report_path, str)
        ]
        present_reports = [
            report_path
            for report_path in expected_reports
            if (root / report_path).exists()
        ]
        if present_reports:
            continue
        for metric in group.get("metrics", ()):
            gaps.append(
                {
                    "layer": group.get("layer", "unknown"),
                    "metric": metric,
                    "expected_reports": expected_reports,
                }
            )
    return gaps


def _line_is_unsafe_claim_context(line: str, heading: str) -> bool:
    return any(marker in line for marker in SAFE_UNSUPPORTED_CONTEXT_MARKERS) or any(
        section in heading for section in SAFE_UNSUPPORTED_CONTEXT_SECTIONS
    )


def _unsafe_claim_hits(path: Path) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    heading = ""
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip().lower()
        if line.startswith("#"):
            heading = line
        if not line or _line_is_unsafe_claim_context(line, heading):
            continue
        for pattern in UNSAFE_PATTERNS:
            if pattern in line:
                hits.append(
                    {
                        "path": project_relative_path(path),
                        "line": str(line_number),
                        "pattern": pattern,
                    }
                )
    return hits


def _consistency_checks(
    reports: dict[str, dict[str, Any]],
    root: Path,
    rq_matrix: list[dict[str, Any]],
    dataset_matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    benchmark_path = "data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"
    retrieval_gold = _metric(
        reports["retrieval_ablation_benchmark_v2"],
        "metadata",
        "gold_labels_path",
    )
    suff_gold = _metric(reports["sufficiency_evaluation"], "metadata", "gold_labels_path")
    sufficiency_boundary = _metric(
        reports["sufficiency_evaluation"],
        "metrics",
        "advisory_boundary_violation_count",
        default=0,
    )
    robustness_boundary = _metric(
        reports["robustness_evaluation"],
        "aggregate",
        "advisory_boundary_violation_count",
        default=0,
    )
    robustness_false_answer = _metric(
        reports["robustness_evaluation"],
        "aggregate",
        "false_answer_rate",
        default=0,
    )
    reviewed_subset = reports.get("benchmark_reviewed_subset_summary", {})
    reviewed_subset_pending = _metric(
        reviewed_subset,
        "metadata",
        "llm_review_completed",
        default=False,
    ) is not True
    scanned_paths = [
        root / "docs" / "thesis_positioning.md",
        root / "docs" / "experiment_workflow.md",
        root / "reports" / "stages" / "thesis_experiment_dashboard.md",
        root / "reports" / "final" / "project_report.md",
        root / "reports" / "final" / "project_academic_report.md",
    ]
    unsafe_hits: list[dict[str, str]] = []
    for path in scanned_paths:
        if not path.exists():
            continue
        unsafe_hits.extend(_unsafe_claim_hits(path))
    primary_metric_gaps = _primary_metric_report_gaps(root)
    triple_llm_reviewed = _metric(
        reports.get("triple_semantic_llm_review", {}),
        "summary",
        "llm_reviewed_total",
        default=0,
    )
    answer_llm_reviewed = _metric(
        reports.get("answer_llm_judge", {}),
        "summary",
        "llm_reviewed_total",
        default=0,
    )
    benchmark_llm_reviewed = _metric(
        reports.get("benchmark_llm_review", {}),
        "summary",
        "llm_reviewed_total",
        default=0,
    )
    checks = {
        "every_rq_has_evidence_report": all(row["evidence_reports"] for row in rq_matrix),
        "primary_thesis_metrics_have_report_evidence": not primary_metric_gaps,
        "primary_thesis_metric_gaps": primary_metric_gaps,
        "benchmark_v2_used_in_main_retrieval": retrieval_gold == benchmark_path,
        "benchmark_v2_used_in_safety": suff_gold == benchmark_path,
        "pilot_reports_not_marked_main": all(
            row["evidence_role"] != "main_thesis_benchmark"
            for row in dataset_matrix
            if row["dataset"] in {"10-CQ pilot", "35-question expanded", "answer-eval subset"}
        ),
        "human_review_absent": True,
        "external_expert_certified": False,
        "aviation_expert_certified": False,
        "benchmark_llm_review_available": benchmark_llm_reviewed > 0,
        "triple_semantic_llm_review_available": triple_llm_reviewed > 0,
        "answer_llm_judge_available": answer_llm_reviewed > 0,
        "reviewed_subset_llm_review_pending": reviewed_subset_pending,
        "safety_reports_have_no_boundary_violations": (
            sufficiency_boundary == 0 and robustness_boundary == 0
        ),
        "robustness_false_answer_rate_zero": robustness_false_answer == 0,
        "no_unsafe_claim_patterns": not unsafe_hits,
        "unsafe_hits": unsafe_hits,
    }
    checks["automated_consistency_passed"] = all(
        value
        for key, value in checks.items()
        if key not in {"primary_thesis_metric_gaps", "unsafe_hits"}
        and key
        not in {
            "reviewed_subset_llm_review_pending",
            "external_expert_certified",
            "aviation_expert_certified",
        }
    )
    checks["claim_readiness_passed"] = (
        checks["automated_consistency_passed"]
        and checks["benchmark_llm_review_available"]
        and checks["answer_llm_judge_available"]
    )
    checks["all_passed"] = checks["claim_readiness_passed"]
    return checks


def build_thesis_experiment_dashboard(
    *,
    project_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    root = Path(project_root)
    reports = {
        name: _load_json(root / rel_path)
        for name, rel_path in REPORT_SOURCES.items()
    }
    primary = _primary_results(reports)
    rq_matrix = _rq_evidence_matrix(primary)
    dataset_matrix = _dataset_usage_matrix()
    return {
        "metadata": {
            "scoring_policy": "layered_metrics_no_mixed_overall_score",
            "source_policy": "aggregate_existing_reports_no_recompute",
            "review_policy": "human_review_absent_use_model_based_review_only",
            "human_review": False,
            "external_expert_certified": False,
            "aviation_expert_certified": False,
            "advisory_boundary": (
                "Aviation learning and decision support only; does not replace POH/AFM, "
                "approved checklists, ATC instructions, instructor guidance, regulations, "
                "or pilot judgment."
            ),
        },
        "experiment_inventory": _report_inventory(reports, root),
        "rq_to_evidence_matrix": rq_matrix,
        "dataset_usage_matrix": dataset_matrix,
        "primary_results": primary,
        "failure_mode_summary": _failure_summary(reports),
        "thesis_ready_claim_summary": _claim_summary(reports),
        "consistency_checks": _consistency_checks(
            reports,
            root,
            rq_matrix,
            dataset_matrix,
        ),
    }


def write_thesis_experiment_dashboard_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    return write_json_report(result, output_path)


def write_thesis_experiment_dashboard_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Thesis Experiment Dashboard",
        "",
        "- Source policy: aggregate existing reports; do not recompute experiments unnecessarily.",
        "- Scoring policy: layered metrics; no mixed overall score.",
        f"- Advisory boundary: {result['metadata']['advisory_boundary']}",
        "",
        "## Experiment Inventory",
        "",
        "| Report | Present | Dataset | Questions | Layers | Human review present | LLM review available |",
        "| --- | ---: | --- | ---: | --- | ---: | ---: |",
    ]
    for item in result["experiment_inventory"]:
        lines.append(
            f"| `{item['report_name']}` | {item['present']} | {item['dataset_used']} | "
            f"{item['questions_count']} | {', '.join(item['metric_layers_covered'])} | "
            f"{item['human_review_present']} | {item['llm_review_available']} |"
        )

    lines.extend(
        [
            "",
            "## RQ-To-Evidence Matrix",
            "",
            "| RQ | Evidence reports | Primary metrics | Claim strength | Remaining gaps |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in result["rq_to_evidence_matrix"]:
        lines.append(
            f"| {row['rq']} | {', '.join(row['evidence_reports'])} | "
            f"{', '.join(row['primary_metrics'])} | {row['claim_strength']} | "
            f"{row['remaining_gaps']} |"
        )

    lines.extend(
        [
            "",
            "## Dataset Usage Matrix",
            "",
            "| Dataset | Purpose | Evidence role | Main claim support | Limitations |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in result["dataset_usage_matrix"]:
        lines.append(
            f"| {row['dataset']} | {row['purpose']} | {row['evidence_role']} | "
            f"{row['can_support_thesis_main_claim']} | {row['limitations']} |"
        )

    primary = result["primary_results"]
    lines.extend(
        [
            "",
            "## Primary Results",
            "",
            "| Metric group | Key numbers |",
            "| --- | --- |",
            (
                "| vector-only benchmark v2 | "
                f"Recall@5={primary['vector_only']['recall_at_5']}, "
                f"Recall@10={primary['vector_only']['recall_at_10']}, "
                f"MRR@5={primary['vector_only']['mrr_at_5']}, "
                f"NDCG@10={primary['vector_only']['ndcg_at_10']} |"
            ),
            (
                "| lexical hybrid benchmark v2 | "
                f"Recall@5={primary['best_lexical_hybrid']['recall_at_5']}, "
                f"Recall@10={primary['best_lexical_hybrid']['recall_at_10']}, "
                f"MRR@5={primary['best_lexical_hybrid']['mrr_at_5']}, "
                f"NDCG@10={primary['best_lexical_hybrid']['ndcg_at_10']}, "
                f"Context Recall={primary['best_lexical_hybrid']['context_recall']} |"
            ),
            (
                "| traversal hybrid | "
                f"Recall@5={primary['traversal_hybrid']['recall_at_5']}, "
                f"Path Recall@5={primary['traversal_hybrid']['path_recall_at_5']}, "
                f"Path Precision@5={primary['traversal_hybrid']['path_precision_at_5']} "
                "(heuristic or model-reviewed; no human review) |"
            ),
            (
                "| sufficiency | "
                f"Abstention Accuracy={primary['sufficiency']['abstention_accuracy']}, "
                f"False Answer Rate={primary['sufficiency']['false_answer_rate']}, "
                f"False Abstention Rate={primary['sufficiency']['false_abstention_rate']} |"
            ),
            (
                "| robustness | "
                f"Abstention Correctness={primary['robustness']['abstention_correctness']}, "
                f"False Answer Rate={primary['robustness']['false_answer_rate']}, "
                "Boundary Violations="
                f"{primary['robustness']['advisory_boundary_violation_count']} |"
            ),
            (
                "| benchmark reviewed subset | "
                f"Labels={primary['benchmark_reviewed_subset']['labels_total']}, "
                f"Review Status={primary['benchmark_reviewed_subset']['review_status']}, "
                "External Expert Certified="
                f"{primary['benchmark_reviewed_subset']['external_aviation_expert_certified']} |"
            ),
            (
                "| answer-eval benchmark subset | "
                f"Answers={primary['answer_evaluation_benchmark_subset']['answers_total']}, "
                f"Status={primary['answer_evaluation_benchmark_subset']['evaluation_status']}, "
                "Unmatched Gold Labels="
                f"{primary['answer_evaluation_benchmark_subset']['unmatched_gold_labels']}, "
                "Hybrid Faithfulness="
                f"{primary['answer_evaluation_benchmark_subset']['hybrid_faithfulness']}, "
                "Score Method=deterministic_heuristic |"
            ),
            (
                "| chunking benchmark v2 | "
                f"Top-k best={primary['chunking_benchmark_v2']['topk_best_strategy']} "
                f"(Recall@5={primary['chunking_benchmark_v2']['topk_recall_at_5_supported']}), "
                f"Fixed-budget best={primary['chunking_benchmark_v2']['budget_best_strategy']} "
                f"(Recall@5={primary['chunking_benchmark_v2']['budget_recall_at_5_supported']}), "
                f"Partial methods={primary['chunking_benchmark_v2']['partial_methods']} |"
            ),
            (
                "| KG | "
                f"Provenance Completeness={primary['kg']['provenance_completeness']}, "
                f"Evidence-in-source Rate={primary['kg']['evidence_in_source_rate']}, "
                f"Valid Triples={primary['kg']['valid_triples']} |"
            ),
            (
                "| triple semantic review | "
                f"Sample={primary['triple_semantic_review']['sample_size']}, "
                f"reviewed={primary['triple_semantic_review']['reviewed']}, "
                f"needs_review={primary['triple_semantic_review']['needs_review']} |"
            ),
            (
                "| LLM review status | "
                f"Benchmark reviewed={primary['llm_review_status']['benchmark']['llm_reviewed']}, "
                "triple evidence support="
                f"{primary['llm_review_status']['triple_semantic']['evidence_support_rate']}, "
                "graph path relevance="
                f"{primary['llm_review_status']['graph_paths']['path_relevance_rate']}, "
                "answer judge correctness="
                f"{primary['llm_review_status']['answer_judge']['correctness_rate']}, "
                "human review=false |"
            ),
            (
                "| implementation review remediation | "
                f"Status={primary['implementation_review_remediation']['status']}, "
                f"implemented={primary['implementation_review_remediation']['implemented_items']}, "
                f"verified already fixed="
                f"{primary['implementation_review_remediation']['verified_already_fixed_items']}, "
                f"deferred={primary['implementation_review_remediation']['deferred_items']}, "
                "metrics changed="
                f"{primary['implementation_review_remediation']['scientific_metrics_changed']} |"
            ),
        ]
    )

    ci = primary["sufficiency"].get("confidence_intervals", {})
    if ci:
        lines.extend(["", "## Safety Confidence Intervals", ""])
        lines.append("| Metric | Mean | 95% CI | n |")
        lines.append("| --- | ---: | --- | ---: |")
        for metric, values in ci.items():
            if metric == "ci_policy" or not isinstance(values, dict):
                continue
            lines.append(
                f"| {metric} | {values.get('mean')} | "
                f"{values.get('lower')} - {values.get('upper')} | {values.get('n')} |"
            )

    failure = result["failure_mode_summary"]
    lines.extend(["", "## Failure-Mode Summary", ""])
    lines.append(f"- Graph failure categories: {failure['graph_failure_categories']}")
    lines.append(
        "- Chunking failure-card samples: "
        f"{failure.get('chunking_failure_card_samples', {})}"
    )
    lines.append(
        "- False abstention on supported questions: "
        f"{failure['false_abstention_on_supported_question']}"
    )
    lines.append(
        "- Machine-seeded benchmark wording findings: "
        f"{failure['machine_seeded_benchmark_wording']}"
    )
    lines.append(
        "- Missing LLM triple review items: "
        f"{failure['missing_llm_triple_review']}"
    )

    lines.extend(["", "## LLM Review Status", ""])
    lines.append(
        "`deterministic`, `heuristic`, `llm_judge`, and `human_review` metrics are "
        "reported separately. Human review is absent and external expert certification is false."
    )
    lines.append(f"- Benchmark LLM review: {primary['llm_review_status']['benchmark']}")
    lines.append(f"- Triple semantic LLM review: {primary['llm_review_status']['triple_semantic']}")
    lines.append(f"- Graph path LLM review: {primary['llm_review_status']['graph_paths']}")
    lines.append(f"- Answer generation subset: {primary['llm_review_status']['answer_generation']}")
    lines.append(f"- Answer LLM judge: {primary['llm_review_status']['answer_judge']}")
    lines.append(f"- LLM review consistency: {primary['llm_review_status']['consistency']}")

    lines.extend(["", "## Thesis-Ready Claim Summary", ""])
    for claim in result["thesis_ready_claim_summary"]:
        lines.append(
            f"- **{claim['claim']}** Safe wording: {claim['safe_wording']} "
            f"Limitations: {claim['limitations']} Avoid: {claim['unsafe_wording_to_avoid']}"
        )

    checks = result["consistency_checks"]
    lines.extend(["", "## Consistency Checks", ""])
    for key, value in checks.items():
        if key != "unsafe_hits":
            lines.append(f"- `{key}`: {value}")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_thesis_experiment_dashboard(
    output_dir: str | Path,
    *,
    project_root: str | Path = PROJECT_ROOT,
    report_name: str = "thesis_experiment_dashboard",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_thesis_experiment_dashboard(project_root=project_root)
    output = Path(output_dir)
    stem = Path(report_name).stem or "thesis_experiment_dashboard"
    json_path = write_thesis_experiment_dashboard_json(result, output / f"{stem}.json")
    md_path = write_thesis_experiment_dashboard_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
