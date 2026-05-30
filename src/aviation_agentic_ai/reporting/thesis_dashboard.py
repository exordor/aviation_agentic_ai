from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.evaluation_protocol import PRIMARY_THESIS_METRICS


REPORT_SOURCES: dict[str, str] = {
    "thesis_claims_review": "reports/stages/thesis_claims_review.json",
    "evaluation_protocol_review": "reports/stages/evaluation_protocol_review.json",
    "benchmark_v2_summary": "reports/stages/benchmark_v2_summary.json",
    "retrieval_ablation_benchmark_v2": "reports/stages/retrieval_ablation_benchmark_v2.json",
    "graph_traversal_ablation_benchmark_v2": "reports/stages/graph_traversal_ablation_benchmark_v2.json",
    "sufficiency_evaluation": "reports/stages/sufficiency_evaluation.json",
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
    "not operational",
    "should not",
)

SAFE_UNSUPPORTED_CONTEXT_SECTIONS = (
    "claim safety matrix",
    "what the thesis must not claim",
    "consistency checks",
)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"value": data}


def _metric(data: dict[str, Any], *keys: str, default: Any = "TBD") -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _report_inventory(reports: dict[str, dict[str, Any]], root: Path) -> list[dict[str, Any]]:
    layer_map = {
        "thesis_claims_review": ("claim_safety",),
        "evaluation_protocol_review": ("evaluation_protocol",),
        "benchmark_v2_summary": ("benchmark_validation",),
        "retrieval_ablation_benchmark_v2": ("retrieval", "kg_evidence"),
        "graph_traversal_ablation_benchmark_v2": ("retrieval", "graph_paths"),
        "sufficiency_evaluation": ("safety_abstention",),
        "kg_extraction_comparison": ("ontology_kg",),
        "curated_ontology_evaluation": ("ontology_kg",),
        "triple_semantic_review_sample": ("ontology_kg", "manual_review"),
        "answer_evaluation": ("answer_generation", "safety_abstention"),
        "robustness_evaluation": ("safety_abstention", "robustness"),
        "benchmark_review_pack": ("benchmark_manual_review",),
    }
    dataset_map = {
        "benchmark_v2_summary": "benchmark_v2_120",
        "retrieval_ablation_benchmark_v2": "benchmark_v2_120",
        "graph_traversal_ablation_benchmark_v2": "benchmark_v2_120",
        "sufficiency_evaluation": "benchmark_v2_120",
        "answer_evaluation": "10_cq_answer_subset",
        "robustness_evaluation": "robustness_10_cases",
        "kg_extraction_comparison": "35_question_expanded",
        "triple_semantic_review_sample": "triple_semantic_review_sample",
    }
    manual_review = {
        "benchmark_v2_summary",
        "benchmark_review_pack",
        "graph_traversal_ablation_benchmark_v2",
        "triple_semantic_review_sample",
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
                "manual_review_required": name in manual_review,
            }
        )
    return inventory


def _scenario_metrics(report: dict[str, Any], scenario: str) -> dict[str, Any]:
    return _metric(report, "scenarios", scenario, "aggregate", default={})


def _primary_results(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    retrieval = reports["retrieval_ablation_benchmark_v2"]
    traversal = reports["graph_traversal_ablation_benchmark_v2"]
    sufficiency = reports["sufficiency_evaluation"]
    kg = reports["kg_extraction_comparison"]
    triple = reports["triple_semantic_review_sample"]

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
            "path_metrics_require_manual_review": _metric(
                guarded,
                "graph_paths",
                "requires_manual_review",
            ),
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
    return {
        "graph_failure_categories": dict(sorted(categories.items())),
        "false_abstention_on_supported_question": len(sufficiency_errors),
        "machine_seeded_benchmark_wording": benchmark_findings.get(
            "unnatural_machine_generated_wording",
            0,
        ),
        "missing_manual_triple_review": _metric(triple, "summary", "needs_review", default=0),
        "notes": [
            "High path coverage is interpreted separately from Recall@k.",
            "Manual-review-dependent metrics remain pending.",
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
            ],
            "limitations": "machine-seeded and requires manual naturalness review",
            "can_support_thesis_main_claim": "yes",
            "evidence_role": "main_thesis_benchmark",
        },
        {
            "dataset": "answer-eval subset",
            "purpose": "answer citation and faithfulness heuristics",
            "used_in_reports": ["answer_evaluation"],
            "limitations": "small subset; deterministic heuristic scores",
            "can_support_thesis_main_claim": "partial",
            "evidence_role": "pilot",
        },
        {
            "dataset": "triple semantic review sample",
            "purpose": "manual KG semantic correctness review template",
            "used_in_reports": ["triple_semantic_review_sample"],
            "limitations": "review fields pending; no correctness results claimed",
            "can_support_thesis_main_claim": "partial",
            "evidence_role": "manual_review_pending",
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
            "remaining_gaps": "Triple semantic correctness still requires manual review.",
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
                "deterministic heuristics unless manually reviewed."
            ),
            "claim_strength": "moderate",
            "remaining_gaps": "Answer-level manual or LLM-judge evaluation is optional and not run.",
        },
        {
            "rq": "RQ3 graph evidence vs vector sufficiency",
            "evidence_reports": [
                "retrieval_ablation_benchmark_v2",
                "graph_traversal_ablation_benchmark_v2",
            ],
            "primary_metrics": [
                "Recall@5",
                "Recall@10",
                "MRR@5",
                "NDCG@10",
                "Path Recall@5",
                "Path Precision@5",
            ],
            "current_result_summary": (
                "Vector and hybrid retrieval are reported separately. Graph traversal "
                "can improve path evidence without guaranteeing Recall improvement."
            ),
            "claim_strength": "moderate",
            "remaining_gaps": "Path relevance metrics are heuristic until manually reviewed.",
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
    triple = reports["triple_semantic_review_sample"]
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
        "manual_review_dependent_metrics_not_completed": (
            _metric(triple, "summary", "reviewed", default=0) == 0
            and _metric(triple, "metadata", "semantic_correctness_claimed", default=True)
            is False
        ),
        "no_unsafe_claim_patterns": not unsafe_hits,
        "unsafe_hits": unsafe_hits,
    }
    checks["all_passed"] = all(
        value
        for key, value in checks.items()
        if key not in {"primary_thesis_metric_gaps", "unsafe_hits"}
    )
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
            "manual_review_policy": "do_not_fabricate_manual_review_results",
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
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


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
        "| Report | Present | Dataset | Questions | Layers | Manual review required |",
        "| --- | ---: | --- | ---: | --- | ---: |",
    ]
    for item in result["experiment_inventory"]:
        lines.append(
            f"| `{item['report_name']}` | {item['present']} | {item['dataset_used']} | "
            f"{item['questions_count']} | {', '.join(item['metric_layers_covered'])} | "
            f"{item['manual_review_required']} |"
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
                "(heuristic, requires manual review) |"
            ),
            (
                "| sufficiency | "
                f"Abstention Accuracy={primary['sufficiency']['abstention_accuracy']}, "
                f"False Answer Rate={primary['sufficiency']['false_answer_rate']}, "
                f"False Abstention Rate={primary['sufficiency']['false_abstention_rate']} |"
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
        ]
    )

    failure = result["failure_mode_summary"]
    lines.extend(["", "## Failure-Mode Summary", ""])
    lines.append(f"- Graph failure categories: {failure['graph_failure_categories']}")
    lines.append(
        "- False abstention on supported questions: "
        f"{failure['false_abstention_on_supported_question']}"
    )
    lines.append(
        "- Machine-seeded benchmark wording findings: "
        f"{failure['machine_seeded_benchmark_wording']}"
    )
    lines.append(
        "- Missing manual triple review items: "
        f"{failure['missing_manual_triple_review']}"
    )

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
