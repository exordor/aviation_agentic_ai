from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path


PRIMARY_THESIS_METRICS: tuple[dict[str, Any], ...] = (
    {
        "layer": "retrieval",
        "metrics": (
            "Recall@5",
            "Recall@10",
            "MRR@5",
            "MRR@10",
            "NDCG@10",
            "Precision@5",
            "Context Precision@5",
            "Context Recall",
        ),
        "classification": "mainstream",
        "reports": (
            "reports/stages/retrieval_ablation.json",
            "reports/stages/retrieval_ablation_benchmark_v2.json",
            "reports/stages/chunking_comparison.json",
        ),
    },
    {
        "layer": "graph_evidence",
        "metrics": (
            "Key Entity Coverage",
            "Relation Coverage",
            "Path Recall@5",
            "Path Precision@5",
            "Supporting Path Rate",
            "Average Path Length",
            "Irrelevant Path Rate",
        ),
        "classification": "mainstream_plus_heuristic_path_review",
        "reports": (
            "reports/stages/graph_traversal_ablation.json",
            "reports/stages/graph_traversal_ablation_benchmark_v2.json",
        ),
    },
    {
        "layer": "answer_generation",
        "metrics": (
            "Faithfulness",
            "Answer Correctness",
            "Answer Relevance",
            "Citation Completeness",
            "Citation Precision",
            "Citation Recall",
        ),
        "classification": "mainstream_heuristic_until_llm_or_manual_review",
        "reports": ("reports/stages/answer_evaluation.json",),
    },
    {
        "layer": "ontology_kg",
        "metrics": (
            "RDF/OWL parse validity",
            "label/comment coverage",
            "domain/range completeness",
            "unsupported class/property count",
            "provenance completeness",
            "evidence-in-source rate",
            "triple semantic correctness from manual sample review",
        ),
        "classification": "mainstream_plus_manual_review",
        "reports": (
            "reports/stages/curated_ontology_evaluation.json",
            "reports/stages/kg_validation.json",
            "reports/stages/kg_extraction_comparison.json",
            "reports/stages/triple_semantic_review_sample.json",
        ),
    },
    {
        "layer": "safety_abstention",
        "metrics": (
            "Abstention Accuracy",
            "False Answer Rate",
            "False Abstention Rate",
            "Advisory Boundary Violation Count",
            "Risk Category Accuracy",
        ),
        "classification": "safety_sensitive_project_primary",
        "reports": (
            "reports/stages/sufficiency_evaluation.json",
            "reports/stages/robustness_evaluation.json",
            "reports/stages/answer_evaluation.json",
        ),
    },
)

METRIC_IMPLEMENTATION_STATUS: tuple[dict[str, Any], ...] = (
    {
        "metric": "Recall@5",
        "status": "implemented",
        "kind": "mainstream_ir",
        "field": "recall_at_5",
        "reports": ("retrieval_ablation", "graph_traversal_ablation"),
    },
    {
        "metric": "Recall@10",
        "status": "implemented",
        "kind": "mainstream_ir",
        "field": "recall_at_10",
        "reports": ("retrieval_ablation", "graph_traversal_ablation"),
    },
    {
        "metric": "Precision@5",
        "status": "implemented",
        "kind": "mainstream_ir",
        "field": "precision_at_5",
        "reports": ("retrieval_ablation", "graph_traversal_ablation"),
    },
    {
        "metric": "MRR@5",
        "status": "implemented",
        "kind": "mainstream_ir",
        "field": "mrr_at_5",
        "reports": ("retrieval_ablation", "graph_traversal_ablation"),
    },
    {
        "metric": "MRR@10",
        "status": "implemented",
        "kind": "mainstream_ir",
        "field": "mrr_at_10",
        "reports": ("retrieval_ablation", "graph_traversal_ablation"),
    },
    {
        "metric": "NDCG@10",
        "status": "implemented",
        "kind": "mainstream_ir",
        "field": "ndcg_at_10",
        "reports": ("retrieval_ablation", "graph_traversal_ablation"),
    },
    {
        "metric": "Context Precision@5",
        "status": "implemented",
        "kind": "ragas_style",
        "field": "context_precision_at_5",
        "reports": ("retrieval_ablation", "graph_traversal_ablation"),
    },
    {
        "metric": "Context Recall",
        "status": "implemented",
        "kind": "ragas_style",
        "field": "context_recall",
        "reports": ("retrieval_ablation", "graph_traversal_ablation"),
    },
    {
        "metric": "Path Recall@5",
        "status": "heuristic_available_requires_manual_review",
        "kind": "graphrag_path",
        "field": "path_recall_at_5",
        "reports": ("graph_traversal_ablation",),
    },
    {
        "metric": "Path Precision@5",
        "status": "heuristic_available_requires_manual_review",
        "kind": "graphrag_path",
        "field": "path_precision_at_5",
        "reports": ("graph_traversal_ablation",),
    },
    {
        "metric": "Supporting Path Rate",
        "status": "heuristic_available_requires_manual_review",
        "kind": "graphrag_path",
        "field": "supporting_path_rate",
        "reports": ("graph_traversal_ablation",),
    },
    {
        "metric": "Irrelevant Path Rate",
        "status": "heuristic_available_requires_manual_review",
        "kind": "graphrag_path",
        "field": "irrelevant_path_rate",
        "reports": ("graph_traversal_ablation",),
    },
    {
        "metric": "Citation Precision",
        "status": "implemented",
        "kind": "deterministic_answer_heuristic",
        "field": "citation_precision",
        "reports": ("answer_evaluation",),
    },
    {
        "metric": "Citation Recall",
        "status": "implemented",
        "kind": "deterministic_answer_heuristic",
        "field": "citation_recall",
        "reports": ("answer_evaluation",),
    },
    {
        "metric": "Faithfulness",
        "status": "implemented_heuristic_llm_judge_optional_not_run",
        "kind": "ragas_ares_style",
        "field": "faithfulness",
        "reports": ("answer_evaluation",),
    },
    {
        "metric": "Answer Correctness",
        "status": "implemented_heuristic_llm_judge_optional_not_run",
        "kind": "ragas_style",
        "field": "answer_correctness",
        "reports": ("answer_evaluation",),
    },
    {
        "metric": "Answer Relevance",
        "status": "implemented_heuristic_llm_judge_optional_not_run",
        "kind": "ragas_ares_style",
        "field": "answer_relevance",
        "reports": ("answer_evaluation",),
    },
    {
        "metric": "Triple Semantic Correctness",
        "status": "manual_review_template_available_results_missing",
        "kind": "manual_kg_review",
        "field": "annotation.status",
        "reports": ("triple_semantic_review",),
    },
    {
        "metric": "RDF/OWL Parse Validity",
        "status": "implemented",
        "kind": "ontology_structural",
        "field": "structural_metrics.rdf_valid",
        "reports": ("curated_ontology_evaluation",),
    },
    {
        "metric": "Label/Comment Coverage",
        "status": "implemented",
        "kind": "ontology_usability_annotation",
        "field": "structural_metrics.*_coverage",
        "reports": ("curated_ontology_evaluation",),
    },
    {
        "metric": "Domain/Range Completeness",
        "status": "implemented",
        "kind": "ontology_functional",
        "field": "structural_metrics.properties_with_domain/range",
        "reports": ("curated_ontology_evaluation",),
    },
    {
        "metric": "Unsupported Class/Property Count",
        "status": "implemented",
        "kind": "kg_validation",
        "field": "errors_total and unsupported_triple_count",
        "reports": ("kg_validation", "kg_extraction_comparison"),
    },
    {
        "metric": "Provenance Completeness",
        "status": "implemented",
        "kind": "kg_validation",
        "field": "provenance_complete_rate",
        "reports": ("kg_extraction_comparison", "retrieval_ablation"),
    },
    {
        "metric": "Evidence-In-Source Rate",
        "status": "implemented",
        "kind": "kg_validation",
        "field": "evidence_in_chunk_rate",
        "reports": ("kg_extraction_comparison",),
    },
    {
        "metric": "Abstention Accuracy",
        "status": "implemented",
        "kind": "safety_sensitive",
        "field": "abstention_accuracy",
        "reports": ("sufficiency_evaluation", "robustness_evaluation"),
    },
    {
        "metric": "False Answer Rate",
        "status": "implemented",
        "kind": "safety_sensitive",
        "field": "false_answer_rate",
        "reports": ("sufficiency_evaluation", "robustness_evaluation"),
    },
    {
        "metric": "False Abstention Rate",
        "status": "implemented",
        "kind": "safety_sensitive",
        "field": "false_abstention_rate",
        "reports": ("sufficiency_evaluation", "robustness_evaluation"),
    },
    {
        "metric": "Advisory Boundary Violation Count",
        "status": "implemented",
        "kind": "safety_sensitive",
        "field": "advisory_boundary_violation_count",
        "reports": ("sufficiency_evaluation", "robustness_evaluation", "answer_evaluation"),
    },
    {
        "metric": "Risk Category Accuracy",
        "status": "implemented",
        "kind": "safety_sensitive",
        "field": "risk_category_accuracy",
        "reports": ("sufficiency_evaluation", "robustness_evaluation"),
    },
)

EVIDENCE_GAPS = (
    "Path Recall@k and Path Precision@k are heuristic until manually reviewed path relevance labels exist.",
    "Triple semantic correctness has a review sample but no completed manual correctness results.",
    "Faithfulness, answer correctness, and answer relevance are deterministic heuristics unless an explicit LLM-as-judge or manual review run is added.",
    "Benchmark labels are thesis/course-project evidence, not external aviation-expert certification.",
)


def _report_presence(root: Path) -> dict[str, dict[str, Any]]:
    paths = sorted(
        {
            path
            for group in PRIMARY_THESIS_METRICS
            for path in group["reports"]
        }
    )
    return {
        path: {
            "present": (root / path).exists(),
            "path": path,
        }
        for path in paths
    }


def build_evaluation_protocol_review(
    *,
    project_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    root = Path(project_root)
    implemented = [
        metric
        for metric in METRIC_IMPLEMENTATION_STATUS
        if str(metric["status"]).startswith(("implemented", "heuristic_available"))
    ]
    missing = [
        metric
        for metric in METRIC_IMPLEMENTATION_STATUS
        if "missing" in str(metric["status"]) or "not_run" in str(metric["status"])
    ]
    return {
        "metadata": {
            "protocol_doc": "docs/evaluation_protocol.md",
            "scoring_policy": "layered_metrics_no_mixed_overall_score",
            "project_root": project_relative_path(root, base=root),
        },
        "primary_thesis_metrics": list(PRIMARY_THESIS_METRICS),
        "implemented_metrics": implemented,
        "missing_or_pending_metrics": missing,
        "metric_catalog": list(METRIC_IMPLEMENTATION_STATUS),
        "report_presence": _report_presence(root),
        "evidence_gaps_before_thesis_submission": list(EVIDENCE_GAPS),
    }


def write_evaluation_protocol_review_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_evaluation_protocol_review_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Evaluation Protocol Review",
        "",
        f"- Protocol doc: `{result['metadata']['protocol_doc']}`",
        "- Scoring policy: layered metrics; no single mixed overall score.",
        "",
        "## Primary Thesis Metrics",
        "",
        "| Layer | Classification | Metrics | Reports |",
        "| --- | --- | --- | --- |",
    ]
    for group in result["primary_thesis_metrics"]:
        lines.append(
            f"| {group['layer']} | {group['classification']} | "
            f"{', '.join(group['metrics'])} | "
            f"{', '.join(f'`{report}`' for report in group['reports'])} |"
        )

    lines.extend(
        [
            "",
            "## Metric Implementation Status",
            "",
            "| Metric | Status | Kind | Field | Reports |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for metric in result["metric_catalog"]:
        lines.append(
            f"| {metric['metric']} | {metric['status']} | {metric['kind']} | "
            f"`{metric['field']}` | {', '.join(metric['reports'])} |"
        )

    lines.extend(["", "## Report Presence", "", "| Report | Present |", "| --- | ---: |"])
    for report in result["report_presence"].values():
        lines.append(f"| `{report['path']}` | {report['present']} |")

    lines.extend(["", "## Evidence Gaps Before Thesis Submission", ""])
    lines.extend(f"- {gap}" for gap in result["evidence_gaps_before_thesis_submission"])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_evaluation_protocol_review(
    output_dir: str | Path,
    *,
    project_root: str | Path = PROJECT_ROOT,
    report_name: str = "evaluation_protocol_review",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_evaluation_protocol_review(project_root=project_root)
    output = Path(output_dir)
    stem = Path(report_name).stem or "evaluation_protocol_review"
    json_path = write_evaluation_protocol_review_json(result, output / f"{stem}.json")
    md_path = write_evaluation_protocol_review_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
