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
    "pdf_extraction_comparison": "reports/stages/pdf_extraction_comparison.json",
    "pdf_hybrid_repair_report": "reports/stages/pdf_hybrid_repair_report.json",
    "pdf_backend_chunking_comparison": "reports/stages/pdf_backend_chunking_comparison.json",
    "nasa_source_discovery": "reports/stages/nasa_source_discovery.json",
    "nasa_source_ingestion": "reports/stages/nasa_source_ingestion.json",
    "nasa_source_validation": "reports/stages/nasa_source_validation.json",
    "nasa_chunking_summary": "reports/stages/nasa_chunking_summary.json",
    "ontology_boundary_nasa": "reports/stages/ontology_boundary_nasa.json",
    "nasa_kg_validation": "reports/stages/nasa_kg_validation.json",
    "nasa_benchmark_summary": "reports/stages/nasa_benchmark_summary.json",
    "cross_source_ontology_validation": "reports/stages/cross_source_ontology_validation.json",
    "multisource_retrieval_smoke": "reports/stages/multisource_retrieval_smoke.json",
    "nasa_bga_domain_transfer_pilot": (
        "reports/stages/nasa_bga_domain_transfer_pilot.json"
    ),
    "deepseek_v4pro_implementation_remediation": (
        "reports/reviews/deepseek_v4pro_implementation_remediation.json"
    ),
    "kg_extraction_comparison": "reports/stages/kg_extraction_comparison.json",
    "curated_ontology_evaluation": "reports/stages/curated_ontology_evaluation.json",
    "triple_semantic_review_sample": "reports/stages/triple_semantic_review_sample.json",
    "answer_evaluation": "reports/stages/answer_evaluation.json",
    "robustness_evaluation": "reports/stages/robustness_evaluation.json",
    "benchmark_review_pack": "reports/stages/benchmark_review_pack.json",
    "nasa_atmonto_formal_experiment_scoring": (
        "reports/stages/nasa_atmonto_formal_experiment_scoring.json"
    ),
    "nasa_atmonto_prediction_output_validation": (
        "reports/stages/nasa_atmonto_prediction_output_validation.json"
    ),
    "nasa_atmonto_cq_evaluation": "reports/stages/nasa_atmonto_cq_evaluation.json",
    "nasa_atmonto_s5_s6_agentic_loop": (
        "reports/stages/nasa_atmonto_s5_s6_agentic_loop.json"
    ),
    "nasa_atmonto_s5_s6_independent_agentic_run": (
        "reports/stages/nasa_atmonto_s5_s6_independent_agentic_run.json"
    ),
    "nasa_atmonto_s5_s6_live_agentic_pilot": (
        "reports/stages/nasa_atmonto_s5_s6_live_agentic_pilot.json"
    ),
    "nasa_atmonto_s5_s6_live_agentic_full_run": (
        "reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.json"
    ),
    "nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic": (
        "reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.json"
    ),
    "nasa_atmonto_sota_goal_audit": (
        "reports/stages/nasa_atmonto_sota_goal_audit.json"
    ),
    "nasa_atmonto_reviewer_defense_audit": (
        "reports/stages/nasa_atmonto_reviewer_defense_audit.json"
    ),
    "nasa_atmonto_s7_retrieval": "reports/stages/nasa_atmonto_s7_retrieval.json",
    "nasa_atmonto_s7_graph_health": (
        "reports/stages/nasa_atmonto_s7_graph_health.json"
    ),
    "nasa_atmonto_s7_llm_answer_generation": (
        "reports/stages/nasa_atmonto_s7_llm_answer_generation.json"
    ),
    "nasa_atmonto_s7_vector_only_llm_answer_generation": (
        "reports/stages/nasa_atmonto_s7_vector_only_llm_answer_generation.json"
    ),
    "nasa_atmonto_s7_human_review_candidates": (
        "reports/stages/nasa_atmonto_s7_human_review_candidates.json"
    ),
    "nasa_atmonto_s7_broad_answer_review_packet": (
        "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json"
    ),
    "nasa_atmonto_s7_answer_review_decisions": (
        "reports/stages/nasa_atmonto_s7_answer_review_decisions.json"
    ),
    "nasa_atmonto_s7_answer_review_import": (
        "reports/stages/nasa_atmonto_s7_answer_review_import.json"
    ),
    "nasa_atmonto_s7_candidate_adjudication": (
        "reports/stages/nasa_atmonto_s7_candidate_adjudication.json"
    ),
    "nasa_atmonto_s7_profile_decision": (
        "reports/stages/nasa_atmonto_s7_profile_decision.json"
    ),
}

UNSAFE_PATTERNS = (
    "graphrag always improves recall",
    "graphrag universally improves recall",
    "externally aviation-expert certified",
    "external aviation-expert certification",
    "certified aviation QA system",
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
        "pdf_extraction_comparison": ("pdf_extraction", "claim_safety"),
        "pdf_hybrid_repair_report": ("pdf_extraction", "text_fidelity"),
        "pdf_backend_chunking_comparison": ("pdf_extraction", "retrieval"),
        "nasa_source_discovery": ("source_expansion", "claim_safety"),
        "nasa_source_ingestion": ("source_expansion",),
        "nasa_source_validation": ("source_expansion", "claim_safety"),
        "nasa_chunking_summary": ("source_expansion", "retrieval"),
        "ontology_boundary_nasa": ("source_expansion", "ontology_kg"),
        "nasa_kg_validation": ("source_expansion", "ontology_kg"),
        "nasa_benchmark_summary": ("source_expansion", "benchmark_validation"),
        "cross_source_ontology_validation": ("source_expansion", "ontology_kg"),
        "multisource_retrieval_smoke": ("source_expansion", "retrieval"),
        "nasa_bga_domain_transfer_pilot": (
            "source_expansion",
            "ontology_kg",
            "evaluation_protocol",
            "transfer_pilot",
            "claim_safety",
        ),
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
        "nasa_atmonto_formal_experiment_scoring": (
            "ontology_kg",
            "evaluation_protocol",
        ),
        "nasa_atmonto_prediction_output_validation": (
            "ontology_kg",
            "evaluation_protocol",
            "claim_safety",
        ),
        "nasa_atmonto_cq_evaluation": (
            "ontology_kg",
            "answer_generation",
            "evaluation_protocol",
        ),
        "nasa_atmonto_s5_s6_live_agentic_pilot": (
            "ontology_kg",
            "llm_agents",
            "evaluation_protocol",
        ),
        "nasa_atmonto_s5_s6_live_agentic_full_run": (
            "ontology_kg",
            "llm_agents",
            "evaluation_protocol",
        ),
        "nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic": (
            "ontology_kg",
            "llm_agents",
            "failure_analysis",
            "claim_safety",
        ),
        "nasa_atmonto_sota_goal_audit": (
            "claim_safety",
            "evaluation_protocol",
            "failure_analysis",
        ),
        "nasa_atmonto_reviewer_defense_audit": (
            "claim_safety",
            "failure_analysis",
            "evaluation_protocol",
        ),
        "nasa_atmonto_s7_retrieval": (
            "retrieval",
            "graph_paths",
            "evaluation_protocol",
        ),
        "nasa_atmonto_s7_graph_health": (
            "retrieval",
            "graph_paths",
            "claim_safety",
        ),
        "nasa_atmonto_s7_llm_answer_generation": (
            "answer_generation",
            "graph_paths",
            "safety_abstention",
        ),
        "nasa_atmonto_s7_vector_only_llm_answer_generation": (
            "answer_generation",
            "retrieval",
        ),
        "nasa_atmonto_s7_human_review_candidates": (
            "answer_generation",
            "llm_review_scaffold",
            "failure_analysis",
        ),
        "nasa_atmonto_s7_broad_answer_review_packet": (
            "answer_generation",
            "llm_review_scaffold",
            "failure_analysis",
        ),
        "nasa_atmonto_s7_answer_review_decisions": (
            "answer_generation",
            "human_review_scaffold",
            "claim_safety",
            "failure_analysis",
        ),
        "nasa_atmonto_s7_answer_review_import": (
            "answer_generation",
            "human_review_scaffold",
            "claim_safety",
        ),
        "nasa_atmonto_s7_candidate_adjudication": (
            "answer_generation",
            "failure_analysis",
            "claim_safety",
        ),
        "nasa_atmonto_s7_profile_decision": (
            "answer_generation",
            "failure_analysis",
            "claim_safety",
            "evaluation_protocol",
        ),
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
        "pdf_extraction_comparison": "phak_ch4_pdf_first_pages_heading_sample",
        "pdf_hybrid_repair_report": "phak_ch4_pdf_docling_items",
        "pdf_backend_chunking_comparison": "benchmark_v2_120",
        "nasa_source_discovery": "nasa_bga_aerodynamics_full_landing_page_manifest",
        "nasa_source_ingestion": "nasa_bga_aerodynamics_full_corpus",
        "nasa_source_validation": "nasa_bga_aerodynamics_full_corpus",
        "nasa_chunking_summary": "nasa_bga_lessons_in_aerodynamics_subset",
        "ontology_boundary_nasa": "nasa_bga_lessons_in_aerodynamics_subset",
        "nasa_kg_validation": "nasa_bga_lessons_in_aerodynamics_subset",
        "nasa_benchmark_summary": "nasa_bga_lessons_seed_50",
        "cross_source_ontology_validation": "faa_phak_nasa_cross_source_seed_30",
        "multisource_retrieval_smoke": "faa_phak_nasa_smoke_35",
        "nasa_bga_domain_transfer_pilot": "nasa_bga_aerodynamics_reference_transfer",
        "deepseek_v4pro_implementation_remediation": "not_dataset_specific",
        "answer_evaluation": "10_cq_answer_subset",
        "robustness_evaluation": "robustness_10_cases",
        "kg_extraction_comparison": "35_question_expanded",
        "triple_semantic_review_sample": "triple_semantic_review_sample",
        "nasa_atmonto_formal_experiment_scoring": "atcscc_gold_100",
        "nasa_atmonto_prediction_output_validation": "atcscc_prediction_outputs",
        "nasa_atmonto_cq_evaluation": "atcscc_cq_answer_sets",
        "nasa_atmonto_s5_s6_live_agentic_pilot": "atcscc_s5_s6_live_agentic_pilot_3",
        "nasa_atmonto_s5_s6_live_agentic_full_run": "atcscc_s5_s6_live_agentic_full_run_100",
        "nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic": "atcscc_s5_s6_live_agentic_full_run_100",
        "nasa_atmonto_sota_goal_audit": "atcscc_thesis_claim_gate",
        "nasa_atmonto_reviewer_defense_audit": "atcscc_thesis_claim_gate",
        "nasa_atmonto_s7_retrieval": "atcscc_s7_source_bounded_317",
        "nasa_atmonto_s7_graph_health": "atcscc_s7_source_bounded_317",
        "nasa_atmonto_s7_llm_answer_generation": "atcscc_s7_source_bounded_60",
        "nasa_atmonto_s7_vector_only_llm_answer_generation": (
            "atcscc_s7_source_bounded_60"
        ),
        "nasa_atmonto_s7_human_review_candidates": "atcscc_s7_review_candidate_queue_9",
        "nasa_atmonto_s7_broad_answer_review_packet": "atcscc_s7_source_bounded_60",
        "nasa_atmonto_s7_answer_review_decisions": "atcscc_s7_source_bounded_60",
        "nasa_atmonto_s7_answer_review_import": "atcscc_s7_source_bounded_60",
        "nasa_atmonto_s7_candidate_adjudication": "atcscc_s7_review_candidate_queue_9",
        "nasa_atmonto_s7_profile_decision": "atcscc_s7_profile_decision_what_if_3",
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


def _best_s7_answer_mode(aggregate_by_mode: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    valid_modes = {
        mode: metrics
        for mode, metrics in aggregate_by_mode.items()
        if isinstance(metrics, dict)
    }
    if not valid_modes:
        return None, {}
    best_mode = max(
        valid_modes,
        key=lambda mode: (
            valid_modes[mode].get("answer_correctness") or 0.0,
            valid_modes[mode].get("evidence_faithfulness") or 0.0,
            -(valid_modes[mode].get("unsupported_claim_rate") or 1.0),
        ),
    )
    return best_mode, valid_modes[best_mode]


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
    pdf_extraction = reports.get("pdf_extraction_comparison", {})
    pdf_repair = reports.get("pdf_hybrid_repair_report", {})
    pdf_backend_chunking = reports.get("pdf_backend_chunking_comparison", {})
    kg = reports["kg_extraction_comparison"]
    triple = reports["triple_semantic_review_sample"]
    benchmark_llm = reports.get("benchmark_llm_review", {})
    triple_llm = reports.get("triple_semantic_llm_review", {})
    graph_path_llm = reports.get("graph_path_llm_review", {})
    answer_generation = reports.get("answer_generation_benchmark_subset", {})
    answer_llm = reports.get("answer_llm_judge", {})
    llm_consistency = reports.get("llm_review_consistency", {})
    nasa_ingestion = reports.get("nasa_source_ingestion", {})
    nasa_discovery = reports.get("nasa_source_discovery", {})
    nasa_validation = reports.get("nasa_source_validation", {})
    nasa_chunking = reports.get("nasa_chunking_summary", {})
    nasa_boundary = reports.get("ontology_boundary_nasa", {})
    nasa_kg = reports.get("nasa_kg_validation", {})
    nasa_benchmark = reports.get("nasa_benchmark_summary", {})
    cross_source = reports.get("cross_source_ontology_validation", {})
    multisource = reports.get("multisource_retrieval_smoke", {})
    implementation_remediation = reports.get("deepseek_v4pro_implementation_remediation", {})
    s7_llm_answers = reports.get("nasa_atmonto_s7_llm_answer_generation", {})
    s7_vector_only_answers = reports.get(
        "nasa_atmonto_s7_vector_only_llm_answer_generation",
        {},
    )
    s7_review_candidates = reports.get("nasa_atmonto_s7_human_review_candidates", {})
    s7_candidate_adjudication = reports.get("nasa_atmonto_s7_candidate_adjudication", {})
    s7_profile_decision = reports.get("nasa_atmonto_s7_profile_decision", {})

    vector = _scenario_metrics(retrieval, "vector_hops2_v5_h8")
    hybrid = _scenario_metrics(retrieval, "hybrid_hops2_v5_h8")
    guarded = _scenario_metrics(traversal, "hybrid_vector_traversal_guarded")
    traversal_graph = _scenario_metrics(traversal, "traversal_graph_2_hop")
    structure_kg = _metric(kg, "experiments", "structure_aware", default={})
    suff_metrics = sufficiency.get("metrics", {})
    s7_answer_modes = _metric(
        s7_llm_answers,
        "answer_quality",
        "aggregate_by_mode",
        default={},
    )
    if not isinstance(s7_answer_modes, dict):
        s7_answer_modes = {}
    s7_vector_answer_modes = _metric(
        s7_vector_only_answers,
        "answer_quality",
        "aggregate_by_mode",
        default={},
    )
    if not isinstance(s7_vector_answer_modes, dict):
        s7_vector_answer_modes = {}
    vector_only_metrics = s7_vector_answer_modes.get("token_matched_live_tfidf_vector", {})
    if not isinstance(vector_only_metrics, dict):
        vector_only_metrics = {}
    best_s7_mode, best_s7_metrics = _best_s7_answer_mode(s7_answer_modes)
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
        "s7_llm_answer_generation": {
            "status": s7_llm_answers.get("status", "not_present"),
            "prompt_version": _metric(s7_llm_answers, "metadata", "prompt_version"),
            "reviewer_model": _metric(s7_llm_answers, "metadata", "reviewer_model"),
            "selected_case_count": _metric(
                s7_llm_answers,
                "metadata",
                "selected_case_count",
                default=0,
            ),
            "max_cases_per_template": _metric(
                s7_llm_answers,
                "metadata",
                "max_cases_per_template",
            ),
            "modes": list(s7_answer_modes),
            "best_mode": best_s7_mode,
            "best_mode_metrics": best_s7_metrics,
            "aggregate_by_mode": s7_answer_modes,
            "vector_only_metrics": vector_only_metrics,
            "vector_only_selected_case_count": _metric(
                s7_vector_only_answers,
                "metadata",
                "selected_case_count",
                default=0,
            ),
            "human_review_candidate_count": _metric(
                s7_review_candidates,
                "metadata",
                "candidate_count",
                default=0,
            ),
            "failure_candidate_count": _metric(
                s7_review_candidates,
                "metadata",
                "failure_candidate_count",
                default=0,
            ),
            "adjudication_status": s7_candidate_adjudication.get("status", "not_present"),
            "adjudication_decision_counts": _metric(
                s7_candidate_adjudication,
                "summary",
                "decision_counts",
                default={},
            ),
            "profile_or_gold_boundary_failures": _metric(
                s7_candidate_adjudication,
                "summary",
                "profile_or_gold_boundary_failures",
                default=0,
            ),
            "strict_main_metrics_changed_by_adjudication": _metric(
                s7_candidate_adjudication,
                "metadata",
                "strict_main_metrics_changed",
                default=False,
            ),
            "profile_decision_status": s7_profile_decision.get("status", "not_present"),
            "profile_decision_corrected_record_count": _metric(
                s7_profile_decision,
                "metadata",
                "corrected_record_count",
                default=0,
            ),
            "profile_decision_strict_main_metrics_changed": _metric(
                s7_profile_decision,
                "metadata",
                "strict_main_metrics_changed",
                default=False,
            ),
            "profile_decision_gold_or_profile_changed": _metric(
                s7_profile_decision,
                "metadata",
                "gold_or_profile_changed",
                default=False,
            ),
            "profile_decision_what_if_metrics_replace_main": _metric(
                s7_profile_decision,
                "metadata",
                "what_if_metrics_replace_main",
                default=False,
            ),
            "profile_decision_corrected_record_count_by_mode": _metric(
                s7_profile_decision,
                "summary",
                "corrected_record_count_by_mode",
                default={},
            ),
            "profile_decision_what_if_aggregate_by_mode": _metric(
                s7_profile_decision,
                "summary",
                "what_if_aggregate_by_mode",
                default={},
            ),
            "profile_decision_recommended_policy": _metric(
                s7_profile_decision,
                "summary",
                "recommended_policy",
            ),
            "coverage_candidate_count": _metric(
                s7_review_candidates,
                "metadata",
                "coverage_candidate_count",
                default=0,
            ),
            "claim_boundary": (
                "S7 LLM answers are source-bounded diagnostics over frozen retrieved "
                "contexts; the candidate package is a review queue, not human-reviewed "
                "evidence."
            ),
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
            and isinstance(
                _metric(chunking_topk, "ranking", default=[None])[0], dict
            )
            else "TBD",
            "topk_recall_at_5_supported": _metric(
                chunking_topk,
                "ranking",
                default=[{"recall_at_5_supported": "TBD"}],
            )[0].get("recall_at_5_supported", "TBD")
            if isinstance(_metric(chunking_topk, "ranking", default=[]), list)
            and _metric(chunking_topk, "ranking", default=[])
            and isinstance(
                _metric(chunking_topk, "ranking", default=[None])[0], dict
            )
            else "TBD",
            "budget_best_strategy": _metric(
                chunking_budget,
                "ranking",
                default=[{"strategy": "TBD"}],
            )[0].get("strategy", "TBD")
            if isinstance(_metric(chunking_budget, "ranking", default=[]), list)
            and _metric(chunking_budget, "ranking", default=[])
            and isinstance(
                _metric(chunking_budget, "ranking", default=[None])[0], dict
            )
            else "TBD",
            "budget_recall_at_5_supported": _metric(
                chunking_budget,
                "ranking",
                default=[{"recall_at_5_supported": "TBD"}],
            )[0].get("recall_at_5_supported", "TBD")
            if isinstance(_metric(chunking_budget, "ranking", default=[]), list)
            and _metric(chunking_budget, "ranking", default=[])
            and isinstance(
                _metric(chunking_budget, "ranking", default=[None])[0], dict
            )
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
        "pdf_extraction_backend": {
            "recommended_backend": _metric(
                pdf_backend_chunking,
                "metadata",
                "recommended_default_backend",
                default="hybrid_docling_pymupdf",
            ),
            "recommended_status": _metric(
                pdf_backend_chunking,
                "metadata",
                "recommended_default_status",
                default="candidate_default_not_final",
            ),
            "legacy_false_heading_count": _metric(
                pdf_extraction,
                "backends",
                "pymupdf_text_legacy",
                "false_heading_count",
            ),
            "legacy_heading_precision": _metric(
                pdf_extraction,
                "backends",
                "pymupdf_text_legacy",
                "heading_precision",
            ),
            "docling_heading_recall": _metric(
                pdf_extraction,
                "backends",
                "docling_structure",
                "heading_recall",
            ),
            "docling_section_header_hits": _metric(
                pdf_extraction,
                "backends",
                "docling_structure",
                "gt_headings_labeled_as_section_header",
            ),
            "hybrid_repair_count": _metric(
                pdf_backend_chunking,
                "metadata",
                "hybrid_repair_count",
                default=_metric(pdf_repair, "metadata", "repaired_items"),
            ),
            "hybrid_retrieval_recall_at_5": _metric(
                pdf_backend_chunking,
                "strategies",
                "hybrid_docling_pymupdf_structure_aware_large",
                "retrieval",
                "recall_at_5",
            ),
            "claim_warning": (
                "PDF structure reliability is now tied to Docling labels; PyMuPDF "
                "heuristic headings are legacy baseline evidence only."
            ),
        },
        "kg": {
            "provenance_completeness": structure_kg.get("provenance_complete_rate"),
            "evidence_in_source_rate": structure_kg.get("evidence_in_chunk_rate"),
            "valid_triples": structure_kg.get("valid_triples"),
            "unsupported_triple_count": structure_kg.get("unsupported_triple_count"),
        },
        "nasa_source_expansion": {
            "status": (
                "full_corpus_collected_aerodynamics_subset_experiment_ready"
                if _metric(nasa_validation, "experiment_valid", default=False)
                and _metric(nasa_discovery, "metadata", "missing_unique_urls_total", default=1) == 0
                and _metric(nasa_chunking, "metadata", "experiment_pages_total", default=0) > 0
                else "source_expansion_in_progress"
            ),
            "landing_page_discovery": {
                "discovered_unique_urls": _metric(
                    nasa_discovery,
                    "metadata",
                    "discovered_unique_urls_total",
                ),
                "covered_unique_urls": _metric(
                    nasa_discovery,
                    "metadata",
                    "covered_unique_urls_total",
                ),
                "missing_unique_urls": _metric(
                    nasa_discovery,
                    "metadata",
                    "missing_unique_urls_total",
                ),
                "coverage_rate": _metric(nasa_discovery, "metadata", "coverage_rate"),
                "selection_status": _metric(
                    nasa_discovery,
                    "metadata",
                    "selection_status",
                ),
                "experiment_subset_section": _metric(
                    nasa_discovery,
                    "metadata",
                    "experiment_subset_section",
                ),
            },
            "ingested_pages": _metric(nasa_ingestion, "metadata", "pages_total"),
            "valid_pages": _metric(nasa_validation, "metadata", "valid_pages"),
            "invalid_pages": _metric(nasa_validation, "metadata", "invalid_pages"),
            "experiment_pages": _metric(nasa_validation, "metadata", "experiment_pages_total"),
            "experiment_valid_pages": _metric(
                nasa_validation,
                "metadata",
                "experiment_valid_pages",
            ),
            "experiment_invalid_pages": _metric(
                nasa_validation,
                "metadata",
                "experiment_invalid_pages",
            ),
            "source_type": _metric(nasa_validation, "metadata", "source_type"),
            "chunked_corpus_pages": _metric(nasa_chunking, "metadata", "corpus_pages_total"),
            "chunked_experiment_pages": _metric(
                nasa_chunking,
                "metadata",
                "experiment_pages_total",
            ),
            "experiment_subset": _metric(nasa_chunking, "metadata", "experiment_subset"),
            "chunking_strategies": _metric(nasa_chunking, "metadata", "strategies", default=[]),
            "chunking_distribution": nasa_chunking.get("chunk_strategy_distribution", {}),
            "ontology_boundary": {
                "existing_coverage": len(nasa_boundary.get("existing_ontology_coverage", [])),
                "alias_candidates": len(nasa_boundary.get("alias_candidates", [])),
                "class_candidates": len(nasa_boundary.get("recommended_class_additions", [])),
                "property_candidates": len(nasa_boundary.get("recommended_property_additions", [])),
                "high_risk_operational_detections": len(
                    nasa_boundary.get("high_risk_operational_concepts_detected", [])
                ),
            },
            "kg_dry_run": {
                "triples_total": _metric(nasa_kg, "triples_total"),
                "valid_triples": _metric(nasa_kg, "valid_triples"),
                "provenance_completeness": _metric(
                    nasa_kg,
                    "metrics",
                    "provenance_complete_rate",
                    default=_metric(nasa_kg, "provenance_completeness"),
                ),
                "evidence_in_source_rate": _metric(
                    nasa_kg,
                    "metrics",
                    "evidence_in_chunk_rate",
                    default=_metric(nasa_kg, "evidence_in_source_rate"),
                ),
            },
            "benchmark_seed": {
                "labels_total": _metric(nasa_benchmark, "metadata", "labels_total"),
                "review_status": _metric(nasa_benchmark, "metadata", "review_status"),
                "external_aviation_expert_certified": _metric(
                    nasa_benchmark,
                    "metadata",
                    "external_aviation_expert_certified",
                ),
            },
            "cross_source": {
                "labels_total": _metric(cross_source, "metadata", "labels_total"),
                "document_routing_targets": cross_source.get("document_routing_targets", []),
            },
            "multisource_smoke": {
                "status": _metric(multisource, "metadata", "status"),
                "labels_total": _metric(multisource, "metadata", "labels_total"),
                "faa_plus_nasa_recall_at_5": _metric(
                    multisource,
                    "scenarios",
                    "faa_plus_nasa",
                    "recall_at_5",
                ),
                "faa_plus_nasa_source_routing_accuracy": _metric(
                    multisource,
                    "scenarios",
                    "faa_plus_nasa",
                    "source_routing_accuracy",
                ),
            },
            "claim_policy": (
                "NASA source integration supports internal source-diversity evaluation, "
                "not external aviation certification or operational readiness."
            ),
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
                "pdf_backend_chunking_comparison",
            ],
            "limitations": (
                "implementation-maturity labels required; top-k context volume differs by chunk size"
            ),
            "can_support_thesis_main_claim": "partial_benchmark_specific",
            "evidence_role": "retrieval_design_diagnostic",
        },
        {
            "dataset": "PHAK PDF extraction backend comparison",
            "purpose": "compare PDF structure extraction and hybrid text repair",
            "used_in_reports": [
                "pdf_extraction_comparison",
                "pdf_hybrid_repair_report",
                "pdf_backend_chunking_comparison",
            ],
            "limitations": "Docling structure is document-specific and text repairs are conservative",
            "can_support_thesis_main_claim": "partial_backend_evidence",
            "evidence_role": "pdf_extraction_diagnostic",
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
            "dataset": "NASA BGA full landing-page corpus",
            "purpose": "second authoritative educational source collection from NASA Glenn BGA",
            "used_in_reports": [
                "nasa_source_discovery",
                "nasa_source_ingestion",
                "nasa_source_validation",
            ],
            "limitations": (
                "collected as educational web evidence; interactive pages may expose limited text"
            ),
            "can_support_thesis_main_claim": "source_collection_only",
            "evidence_role": "source_collection",
        },
        {
            "dataset": "NASA Lessons in Aerodynamics subset",
            "purpose": "source-expansion experiment for ontology boundary, chunking, KG, and seed QA",
            "used_in_reports": [
                "nasa_chunking_summary",
                "ontology_boundary_nasa",
                "nasa_kg_validation",
                "nasa_benchmark_summary",
                "cross_source_ontology_validation",
                "multisource_retrieval_smoke",
                "nasa_bga_domain_transfer_pilot",
            ],
            "limitations": (
                "bounded concept-centric educational-source transfer pilot; no external "
                "aviation certification, no human review, no operational readiness, and "
                "no full S7-style answer-generation ablation"
            ),
            "can_support_thesis_main_claim": "bounded_second_source_family_transfer",
            "evidence_role": "domain_transfer_pilot",
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
            "dataset": "ATCSCC S7 source-bounded answer set",
            "purpose": (
                "SOTA-comparable GraphRAG answer-generation diagnostic over frozen "
                "retrieved ATCSCC contexts"
            ),
            "used_in_reports": [
                "nasa_atmonto_s7_answer_generation",
                "nasa_atmonto_s7_llm_answer_generation",
                "nasa_atmonto_s7_human_review_candidates",
                "nasa_atmonto_s7_broad_answer_review_packet",
                "nasa_atmonto_s7_answer_review_decisions",
                "nasa_atmonto_s7_answer_review_import",
                "nasa_atmonto_s7_candidate_adjudication",
                "nasa_atmonto_s7_profile_decision",
            ],
            "limitations": (
                "bounded retrospective LLM run; broad 60-case reviewer packet, "
                "reviewed-CSV import gate, and decision-status report exist but "
                "external review decisions remain incomplete; profile-decision "
                "what-if does not replace strict main metrics or completed human review"
            ),
            "can_support_thesis_main_claim": "source_bounded_diagnostic",
            "evidence_role": "s7_graphrag_answer_generation",
        },
        {
            "dataset": "ATCSCC S5/S6 live agentic pilot 3",
            "purpose": (
                "bounded live extractor/validator/critic/refiner pilot over reviewed "
                "ATCSCC advisory samples"
            ),
            "used_in_reports": ["nasa_atmonto_s5_s6_live_agentic_pilot"],
            "limitations": (
                "3-sample live LLM pilot; useful for method evidence but not a full "
                "autonomous-agent benchmark"
            ),
            "can_support_thesis_main_claim": "bounded_method_pilot",
            "evidence_role": "s5_s6_live_agentic_pilot",
        },
        {
            "dataset": "ATCSCC S5/S6 live agentic full run 100",
            "purpose": (
                "full reviewed-set live extractor/validator/critic/refiner run over "
                "ATCSCC advisory samples"
            ),
            "used_in_reports": ["nasa_atmonto_s5_s6_live_agentic_full_run"],
            "limitations": (
                "full extraction-layer run; still not human-reviewed answer quality, "
                "operational decision support, or cross-domain validation"
            ),
            "can_support_thesis_main_claim": "full_extraction_layer_method_evidence",
            "evidence_role": "s5_s6_live_agentic_full_run",
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
            "rq": "RQ1 schema-constrained event extraction",
            "evidence_reports": [
                "nasa_atmonto_formal_experiment_scoring",
                "nasa_atmonto_prediction_output_validation",
                "nasa_atmonto_cq_evaluation",
                "atcscc_ontology_profile_overview",
            ],
            "primary_metrics": [
                "schema validity",
                "structural acceptance rate",
                "triple precision/recall/F1",
                "evidence-span containment",
                "provenance completeness",
            ],
            "current_result_summary": (
                "The ATCSCC application schema constrains accepted advisory-event "
                "fields and keeps structure, evidence support, and semantic scoring "
                "separate. Current KG provenance completeness="
                f"{primary['kg']['provenance_completeness']}."
            ),
            "claim_strength": "strong",
            "remaining_gaps": (
                "Semantic correctness remains reviewed-subset/profile-relative, not "
                "full ontology correctness."
            ),
        },
        {
            "rq": "RQ2 agentic validation-refinement",
            "evidence_reports": [
                "nasa_atmonto_s5_s6_agentic_loop",
                "nasa_atmonto_s5_s6_independent_agentic_run",
                "nasa_atmonto_s5_s6_live_agentic_pilot",
                "nasa_atmonto_s5_s6_live_agentic_full_run",
                "nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic",
            ],
            "primary_metrics": [
                "schema violation rate",
                "repair count",
                "quarantine/rejection count",
                "unsupported relation rate",
                "post-loop extraction F1",
            ],
            "current_result_summary": (
                "S5/S6 artifacts make extractor, validator, refiner, and critic outcomes "
                "inspectable. The live full-run diagnostic is extraction-layer evidence "
                "and should be interpreted before answer-generation claims."
            ),
            "claim_strength": "moderate",
            "remaining_gaps": (
                "The agent loop is not autonomous ontology construction; it is a "
                "bounded diagnostic and repair loop for advisory-event extraction."
            ),
        },
        {
            "rq": "RQ3 KG-RAG grounding vs vector-only RAG",
            "evidence_reports": [
                "nasa_atmonto_s7_retrieval",
                "nasa_atmonto_s7_graph_health",
                "nasa_atmonto_s7_llm_answer_generation",
                "nasa_atmonto_s7_vector_only_llm_answer_generation",
            ],
            "primary_metrics": [
                "answer-set F1",
                "target-source hit rate",
                "citation precision",
                "citation recall",
                "evidence faithfulness",
                "unsupported claim rate",
                "matched vector-only vs KG-RAG correctness",
            ],
            "current_result_summary": (
                "S7 reports vector, graph, and routed modes separately. Matched "
                "head-to-head diagnostic: KG-RAG correctness="
                f"{primary['s7_llm_answer_generation']['best_mode_metrics'].get('answer_correctness')} "
                "vs vector-only correctness="
                f"{primary['s7_llm_answer_generation']['vector_only_metrics'].get('answer_correctness')}; "
                "KG-RAG unsupported claim rate="
                f"{primary['s7_llm_answer_generation']['best_mode_metrics'].get('unsupported_claim_rate')} "
                "vs vector-only unsupported claim rate="
                f"{primary['s7_llm_answer_generation']['vector_only_metrics'].get('unsupported_claim_rate')}."
            ),
            "claim_strength": "moderate-strong",
            "remaining_gaps": (
                "This is source-bounded ATCSCC evidence, not a universal claim that "
                "GraphRAG beats vector-only retrieval."
            ),
        },
        {
            "rq": "RQ4 failure modes and human-review boundary",
            "evidence_reports": [
                "nasa_atmonto_s7_llm_answer_generation",
                "nasa_atmonto_s7_human_review_candidates",
                "nasa_atmonto_s7_answer_review_import",
                "nasa_atmonto_s7_answer_review_decisions",
                "nasa_atmonto_s7_candidate_adjudication",
                "nasa_atmonto_s7_profile_decision",
                "nasa_atmonto_reviewer_defense_audit",
            ],
            "primary_metrics": [
                "failure candidate count",
                "profile/gold-boundary failures",
                "Unsupported Claim Rate",
                "Abstention Correctness",
                "human_review_completed",
                "expert_certification_completed",
            ],
            "current_result_summary": (
                "S7 best-mode unsupported claim rate="
                f"{primary['s7_llm_answer_generation']['best_mode_metrics'].get('unsupported_claim_rate')} "
                "with "
                f"{primary['s7_llm_answer_generation']['failure_candidate_count']} "
                "failure candidates queued for review; "
                f"{primary['s7_llm_answer_generation']['profile_or_gold_boundary_failures']} "
                "are deterministically adjudicated as profile/gold-boundary cases. "
                "A profile-decision sensitivity report corrects "
                f"{primary['s7_llm_answer_generation']['profile_decision_corrected_record_count']} "
                "records under a predicate-whitelist what-if while leaving strict main "
                "metrics unchanged."
            ),
            "claim_strength": "moderate",
            "remaining_gaps": (
                "Human/expert review remains separate from automated diagnostics; "
                "operational ATC use remains out of scope."
            ),
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
        root / "docs" / "experiment_protocol.md",
        root / "reports" / "stages" / "thesis_experiment_dashboard.md",
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
    s7_llm_selected = _metric(
        reports.get("nasa_atmonto_s7_llm_answer_generation", {}),
        "metadata",
        "selected_case_count",
        default=0,
    )
    s7_review_candidates = _metric(
        reports.get("nasa_atmonto_s7_human_review_candidates", {}),
        "metadata",
        "candidate_count",
        default=0,
    )
    s7_adjudication_failures = _metric(
        reports.get("nasa_atmonto_s7_candidate_adjudication", {}),
        "summary",
        "profile_or_gold_boundary_failures",
        default=0,
    )
    s7_profile_decision = reports.get("nasa_atmonto_s7_profile_decision", {})
    s7_profile_decision_corrected = _metric(
        s7_profile_decision,
        "metadata",
        "corrected_record_count",
        default=0,
    )
    s7_profile_decision_replaces_main = _metric(
        s7_profile_decision,
        "metadata",
        "what_if_metrics_replace_main",
        default=True,
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
        "s7_llm_answer_generation_available": s7_llm_selected > 0,
        "s7_human_review_candidates_available": s7_review_candidates > 0,
        "s7_candidate_adjudication_available": s7_adjudication_failures > 0,
        "s7_profile_decision_what_if_available": (
            s7_profile_decision_corrected > 0 and not s7_profile_decision_replaces_main
        ),
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


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    if value is None:
        return "n/a"
    return str(value)


def _concise_dashboard_markdown_lines(result: dict[str, Any]) -> list[str]:
    primary = result["primary_results"]
    s7 = primary["s7_llm_answer_generation"]
    kg_metrics = s7["best_mode_metrics"]
    vector_metrics = s7["vector_only_metrics"]
    checks = result["consistency_checks"]
    return [
        "# Master Project Dashboard",
        "",
        "## Outcome",
        "",
        "Evidence-grounded, schema-constrained Agentic KG-RAG over retrospective "
        "FAA ATCSCC advisories.",
        "",
        "This dashboard is the human-readable project display surface. The full "
        "machine-readable evidence inventory remains in "
        "`reports/stages/thesis_experiment_dashboard.json`.",
        "",
        "## Demo Path",
        "",
        "```bash",
        "uv run aviation-ai demo",
        "uv run aviation-ai report thesis-experiment-dashboard",
        "uv run aviation-ai report web-demo-smoke",
        "```",
        "",
        "Primary live-presentation path: `aviation-ai demo`. It runs offline over "
        "precomputed ATCSCC artifacts and traces one advisory through source text, "
        "S0 deterministic extraction, S4 evidence-linked graph facts, and S7 "
        "KG-RAG versus vector-only answers.",
        "",
        "## Pipeline",
        "",
        "```text",
        "ATCSCC advisory",
        "  -> lightweight schema/profile",
        "  -> S0/S1/S2/S3/S4 extraction systems",
        "  -> validator/refiner/critic diagnostics",
        "  -> evidence-linked advisory event graph",
        "  -> vector / graph / routed KG-RAG",
        "  -> source-bounded answers and failure review",
        "```",
        "",
        "## Research Questions",
        "",
        "| RQ | Claim strength | Evidence reports | Remaining boundary |",
        "| --- | --- | --- | --- |",
        *[
            (
                f"| {row['rq']} | {row['claim_strength']} | "
                f"{', '.join(row['evidence_reports'])} | {row['remaining_gaps']} |"
            )
            for row in result["rq_to_evidence_matrix"]
        ],
        "",
        "## Key Results",
        "",
        "| Layer | Result | Interpretation |",
        "| --- | --- | --- |",
        (
            "| Extraction / KG | "
            f"Provenance completeness={_format_metric(primary['kg']['provenance_completeness'])}; "
            f"evidence-in-source rate={_format_metric(primary['kg']['evidence_in_source_rate'])}; "
            f"valid triples={_format_metric(primary['kg']['valid_triples'])} | "
            "Accepted facts are source-bounded artifacts, not universal semantic truth. |"
        ),
        (
            "| Agentic loop | "
            "S5/S6 live full-run diagnostics are present | "
            "The loop is an auditable repair/rejection mechanism, not autonomous ontology construction. |"
        ),
        (
            "| KG-RAG answer generation | "
            f"Best mode={s7['best_mode']}; correctness="
            f"{_format_metric(kg_metrics.get('answer_correctness'))}; "
            f"citation precision={_format_metric(kg_metrics.get('citation_precision'))}; "
            f"citation recall={_format_metric(kg_metrics.get('citation_recall'))}; "
            f"unsupported claim rate={_format_metric(kg_metrics.get('unsupported_claim_rate'))} | "
            "Supports a source-bounded grounding claim. |"
        ),
        (
            "| Matched vector-only comparison | "
            f"vector-only correctness={_format_metric(vector_metrics.get('answer_correctness'))}; "
            f"vector-only unsupported claim rate="
            f"{_format_metric(vector_metrics.get('unsupported_claim_rate'))} | "
            "Useful RQ3 contrast, but not a universal GraphRAG superiority claim. |"
        ),
        (
            "| Review boundary | "
            f"human-review candidates={s7['human_review_candidate_count']}; "
            f"profile/gold-boundary failures={s7['profile_or_gold_boundary_failures']}; "
            "human review=false | "
            "Automated diagnostics remain separate from human or expert review. |"
        ),
        "",
        "## Demonstration Script",
        "",
        "1. State the boundary: retrospective ATCSCC advisories, not live ATC support.",
        "2. Run `uv run aviation-ai demo` and show the single-advisory trace.",
        "3. Point to the S0 deterministic facts and S4 evidence-linked graph facts.",
        "4. Compare the KG-RAG and vector-only answer arms for the same advisory.",
        "5. Open this dashboard and use the RQ table to connect demo behavior to thesis claims.",
        "6. End with failure boundaries: profile gaps, unsupported facts, and human review remain explicit.",
        "",
        "## Claim Boundary",
        "",
        "- The project is a bounded schema-constrained Agentic KG-RAG prototype.",
        "- The schema/profile is an engineering constraint, not a complete aviation ontology.",
        "- The event graph is source-bounded and evidence-linked.",
        "- KG-RAG is evaluated as a grounding and citation diagnostic, not as universal superiority.",
        "- Automated review does not replace human or external expert review.",
        "- The system is not live operational ATC decision support.",
        "",
        "## Current Checks",
        "",
        f"- Every RQ has evidence report: {checks['every_rq_has_evidence_report']}",
        f"- Primary metrics have report evidence: {checks['primary_thesis_metrics_have_report_evidence']}",
        f"- Unsafe claim patterns found: {not checks['no_unsafe_claim_patterns']}",
        f"- Automated consistency passed: {checks['automated_consistency_passed']}",
        f"- Claim readiness passed: {checks['claim_readiness_passed']}",
        "",
        "## Next Writing Step",
        "",
        "Write the thesis spine from this dashboard: title, abstract, method figure, "
        "experiment table, RQ-by-RQ results, and limitations. Do not add new "
        "workstreams unless they directly patch one of these rows.",
    ]


def write_thesis_experiment_dashboard_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    concise_lines = _concise_dashboard_markdown_lines(result)
    path.write_text("\n".join(concise_lines).rstrip() + "\n", encoding="utf-8")
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
