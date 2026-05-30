from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.reporting.io import read_json_object_or_none, write_json_report


STAGE_INPUTS = {
    "source_scope": "source_scope.json",
    "cq_gap_review": "cq_gap_review.json",
    "ontology_evaluation": "ontology_evaluation.json",
    "generated_ontology_evaluation": "generated_ontology_evaluation.json",
    "generated_boundary_ontology_evaluation": "generated_boundary_ontology_evaluation.json",
    "review_progress": "review_progress.json",
    "generation_run_summary": "generation_run_summary.json",
}


def _read_json_if_exists(path: Path) -> dict[str, Any] | None:
    return read_json_object_or_none(path, wrap_non_object=True)


def _summarize_evaluation(report_name: str, data: dict[str, Any]) -> dict[str, Any]:
    judgment = data.get("judgment", {})
    quality_gates = data.get("quality_gates", [])
    cq_coverage = data.get("cq_coverage", {})
    return {
        "report_name": report_name,
        "rdf_valid_tbox_extraction_prototype": judgment.get(
            "rdf_valid_tbox_extraction_prototype", False
        ),
        "valid_tbox_prototype": judgment.get("valid_tbox_prototype", False),
        "publication_ready_ontology": judgment.get("publication_ready_ontology", False),
        "failed_quality_gates": [gate for gate in quality_gates if not gate.get("passed", False)],
        "semantic_smells": data.get("semantic_smells", []),
        "entity_mention_coverage_ratio": cq_coverage.get("entity_mention_coverage_ratio", 0.0),
        "unique_entity_coverage_ratio": cq_coverage.get("unique_entity_coverage_ratio", 0.0),
        "answerability_support_score": cq_coverage.get("answerability_metrics", {}).get(
            "support_score", 0.0
        ),
    }


def _load_live_evaluations(stage_path: Path, pattern: str) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for path in sorted(
        stage_path.glob(pattern),
        key=lambda item: (item.stat().st_mtime, item.name),
    ):
        data = _read_json_if_exists(path)
        if data is None:
            continue
        reports.append(_summarize_evaluation(path.stem, data))
    return reports


def build_overnight_summary(stage_dir: str | Path) -> dict[str, Any]:
    stage_path = Path(stage_dir)
    inputs = {
        key: _read_json_if_exists(stage_path / filename)
        for key, filename in STAGE_INPUTS.items()
    }
    evaluation = inputs["ontology_evaluation"] or {}
    generated_evaluation = inputs["generated_ontology_evaluation"] or {}
    generated_boundary_evaluation = inputs["generated_boundary_ontology_evaluation"] or {}
    judgment = evaluation.get("judgment", {})
    generated_judgment = generated_evaluation.get("judgment", {})
    generated_boundary_judgment = generated_boundary_evaluation.get("judgment", {})
    quality_gates = evaluation.get("quality_gates", [])
    generated_quality_gates = generated_evaluation.get("quality_gates", [])
    generated_boundary_quality_gates = generated_boundary_evaluation.get("quality_gates", [])
    semantic_smells = evaluation.get("semantic_smells", [])
    generated_smells = generated_evaluation.get("semantic_smells", [])
    generated_boundary_smells = generated_boundary_evaluation.get("semantic_smells", [])
    cq_coverage = evaluation.get("cq_coverage", {})
    generated_coverage = generated_evaluation.get("cq_coverage", {})
    generated_boundary_coverage = generated_boundary_evaluation.get("cq_coverage", {})
    review_progress = inputs["review_progress"] or {}
    source_scope = inputs["source_scope"] or {}
    cq_gap = inputs["cq_gap_review"] or {}
    generation = inputs["generation_run_summary"] or {}
    live_evaluations = _load_live_evaluations(stage_path, "live_*_ontology_evaluation.json")
    live_boundary_evaluations = _load_live_evaluations(stage_path, "live_*_boundary_evaluation.json")
    source_themes = [
        str(item.get("title", ""))
        for item in source_scope.get("core_themes", [])
        if isinstance(item, dict) and item.get("title")
    ]

    return {
        "inputs_present": {key: value is not None for key, value in inputs.items()},
        "source_scope": {
            "themes": source_themes,
            "ontology_questions": source_scope.get("in_scope_ontology_questions", []),
            "boundary_cqs": cq_gap.get("boundary_cq_count", 0),
        },
        "cq_gap_review": {
            "existing_cqs": cq_gap.get("existing_cq_count", 0),
            "boundary_cqs": cq_gap.get("boundary_cq_count", 0),
            "weak_boundary_questions": cq_gap.get("missing_or_weak", []),
            "summary": cq_gap.get("summary", {}),
        },
        "ontology_evaluation": {
            "rdf_valid_tbox_extraction_prototype": judgment.get(
                "rdf_valid_tbox_extraction_prototype", False
            ),
            "valid_tbox_prototype": judgment.get("valid_tbox_prototype", False),
            "publication_ready_ontology": judgment.get("publication_ready_ontology", False),
            "failed_quality_gates": [
                gate for gate in quality_gates if not gate.get("passed", False)
            ],
            "semantic_smells": semantic_smells,
            "entity_mention_coverage_ratio": cq_coverage.get(
                "entity_mention_coverage_ratio", 0.0
            ),
            "unique_entity_coverage_ratio": cq_coverage.get("unique_entity_coverage_ratio", 0.0),
        },
        "generated_ontology_evaluation": {
            "rdf_valid_tbox_extraction_prototype": generated_judgment.get(
                "rdf_valid_tbox_extraction_prototype", False
            ),
            "valid_tbox_prototype": generated_judgment.get("valid_tbox_prototype", False),
            "publication_ready_ontology": generated_judgment.get(
                "publication_ready_ontology", False
            ),
            "failed_quality_gates": [
                gate for gate in generated_quality_gates if not gate.get("passed", False)
            ],
            "semantic_smells": generated_smells,
            "entity_mention_coverage_ratio": generated_coverage.get(
                "entity_mention_coverage_ratio", 0.0
            ),
            "answerability_support_score": generated_coverage.get(
                "answerability_metrics", {}
            ).get("support_score", 0.0),
        },
        "generated_boundary_ontology_evaluation": {
            "rdf_valid_tbox_extraction_prototype": generated_boundary_judgment.get(
                "rdf_valid_tbox_extraction_prototype", False
            ),
            "valid_tbox_prototype": generated_boundary_judgment.get(
                "valid_tbox_prototype", False
            ),
            "publication_ready_ontology": generated_boundary_judgment.get(
                "publication_ready_ontology", False
            ),
            "failed_quality_gates": [
                gate
                for gate in generated_boundary_quality_gates
                if not gate.get("passed", False)
            ],
            "semantic_smells": generated_boundary_smells,
            "entity_mention_coverage_ratio": generated_boundary_coverage.get(
                "entity_mention_coverage_ratio", 0.0
            ),
            "answerability_support_score": generated_boundary_coverage.get(
                "answerability_metrics", {}
            ).get("support_score", 0.0),
        },
        "live_ontology_evaluations": live_evaluations,
        "latest_live_ontology_evaluation": live_evaluations[-1] if live_evaluations else {},
        "live_boundary_evaluations": live_boundary_evaluations,
        "latest_live_boundary_evaluation": (
            live_boundary_evaluations[-1] if live_boundary_evaluations else {}
        ),
        "generation": generation,
        "review_progress": {
            "finding_status_counts": review_progress.get("finding_status_counts", {}),
            "action_status_counts": review_progress.get("action_status_counts", {}),
            "open_findings": review_progress.get("open_findings", []),
            "open_actions": review_progress.get("open_actions", []),
        },
    }


def write_overnight_summary_json(summary: dict[str, Any], output_path: str | Path) -> Path:
    return write_json_report(summary, output_path, sort_keys=False)


def write_overnight_summary_markdown(summary: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    evaluation = summary["ontology_evaluation"]
    generated = summary["generated_ontology_evaluation"]
    generated_boundary = summary["generated_boundary_ontology_evaluation"]
    latest_live = summary["latest_live_ontology_evaluation"]
    latest_live_boundary = summary["latest_live_boundary_evaluation"]
    source_scope = summary["source_scope"]
    cq_gap = summary["cq_gap_review"]
    generation = summary["generation"]
    review_progress = summary["review_progress"]
    failed_gates = evaluation["failed_quality_gates"]
    smells = evaluation["semantic_smells"]

    lines = [
        "# Overnight Ontology Optimization Report",
        "",
        "## Source Boundary",
        "",
        f"- Boundary CQs: {source_scope['boundary_cqs']}",
        f"- Core themes: {', '.join(source_scope['themes']) or 'Not generated'}",
        "",
        "## CQ Gap Review",
        "",
        f"- Existing CQs: {cq_gap['existing_cqs']}",
        f"- Boundary CQs: {cq_gap['boundary_cqs']}",
        f"- Weak boundary questions: {len(cq_gap['weak_boundary_questions'])}",
        "",
        "## Ontology Evaluation",
        "",
        f"- RDF-valid TBox extraction prototype: "
        f"{'yes' if evaluation['rdf_valid_tbox_extraction_prototype'] else 'no'}",
        f"- Valid TBox prototype: {'yes' if evaluation['valid_tbox_prototype'] else 'no'}",
        f"- Publication-ready ontology: "
        f"{'yes' if evaluation['publication_ready_ontology'] else 'no'}",
        f"- Failed quality gates: {len(failed_gates)}",
        f"- Semantic smells: {len(smells)}",
        f"- Entity mention coverage: {evaluation['entity_mention_coverage_ratio']}",
        f"- Unique entity coverage: {evaluation['unique_entity_coverage_ratio']}",
        "",
        "## Generated Seed Evaluation",
        "",
        f"- Valid TBox prototype: {'yes' if generated['valid_tbox_prototype'] else 'no'}",
        f"- Failed quality gates: {len(generated['failed_quality_gates'])}",
        f"- Semantic smells: {len(generated['semantic_smells'])}",
        f"- Entity mention coverage: {generated['entity_mention_coverage_ratio']}",
        f"- Silver answerability support score: {generated['answerability_support_score']}",
        "",
        "## Generated Boundary-CQ Evaluation",
        "",
        f"- Valid TBox prototype: {'yes' if generated_boundary['valid_tbox_prototype'] else 'no'}",
        f"- Failed quality gates: {len(generated_boundary['failed_quality_gates'])}",
        f"- Semantic smells: {len(generated_boundary['semantic_smells'])}",
        f"- Entity mention coverage: {generated_boundary['entity_mention_coverage_ratio']}",
        f"- Silver answerability support score: "
        f"{generated_boundary['answerability_support_score']}",
        "",
        "## Latest Live Generation Evaluation",
        "",
    ]
    if latest_live:
        lines.extend(
            [
                f"- Report: {latest_live['report_name']}",
                f"- Valid TBox prototype: "
                f"{'yes' if latest_live['valid_tbox_prototype'] else 'no'}",
                f"- Failed quality gates: {len(latest_live['failed_quality_gates'])}",
                f"- Semantic smells: {len(latest_live['semantic_smells'])}",
                f"- Entity mention coverage: {latest_live['entity_mention_coverage_ratio']}",
                f"- Silver answerability support score: "
                f"{latest_live['answerability_support_score']}",
                "",
            ]
        )
    else:
        lines.extend(["- No live generation evaluation recorded.", ""])
    if latest_live_boundary:
        lines.extend(
            [
                "## Latest Live Boundary-CQ Evaluation",
                "",
                f"- Report: {latest_live_boundary['report_name']}",
                f"- Valid TBox prototype: "
                f"{'yes' if latest_live_boundary['valid_tbox_prototype'] else 'no'}",
                f"- Failed quality gates: "
                f"{len(latest_live_boundary['failed_quality_gates'])}",
                f"- Semantic smells: {len(latest_live_boundary['semantic_smells'])}",
                f"- Entity mention coverage: "
                f"{latest_live_boundary['entity_mention_coverage_ratio']}",
                f"- Silver answerability support score: "
                f"{latest_live_boundary['answerability_support_score']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Generation Runs",
            "",
            f"- Runs: {generation.get('runs_total', 0)}",
            f"- Accepted pages: {generation.get('accepted_pages_total', 0)}",
            f"- Failed pages: {generation.get('failed_pages_total', 0)}",
            f"- Latest run: {generation.get('latest_run', {}).get('run_id', '') or 'None'}",
            "",
            "## Review Progress",
            "",
            f"- Finding statuses: {review_progress['finding_status_counts']}",
            f"- Action statuses: {review_progress['action_status_counts']}",
            f"- Open findings: {len(review_progress['open_findings'])}",
            f"- Open actions: {len(review_progress['open_actions'])}",
            "",
            "## Remaining Risks",
            "",
        ]
    )
    if failed_gates:
        lines.extend(f"- Failed gate: {gate['id']}" for gate in failed_gates[:10])
    if smells:
        lines.extend(f"- Semantic smell: {item['id']}" for item in smells[:10])
    if not failed_gates and not smells:
        lines.append("- No failed quality gates or semantic smells recorded.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_overnight_summary(stage_dir: str | Path) -> tuple[Path, Path, dict[str, Any]]:
    stage_path = Path(stage_dir)
    summary = build_overnight_summary(stage_path)
    json_path = write_overnight_summary_json(summary, stage_path / "overnight_optimization_report.json")
    md_path = write_overnight_summary_markdown(
        summary, stage_path / "overnight_optimization_report.md"
    )
    return json_path, md_path, summary
