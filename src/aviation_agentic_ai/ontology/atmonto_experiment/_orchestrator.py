"""AUTO-SPLIT from ontology/atmonto_experiment.py. See git history."""
from __future__ import annotations

from typing import Any
from pathlib import Path
import argparse
import json

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path

from ._io import (
    write_json,
    write_jsonl,
)
from ._system_defs import (
    GOLD_CANDIDATE_REVIEW_JSONL,
    GOLD_CANDIDATE_REVIEW_MD,
    GOLD_FREEZE_REPORT_JSON,
    GOLD_FREEZE_REPORT_MD,
    GOLD_REVIEW_BATCH_DIR,
    GOLD_REVIEW_BATCH_INDEX_MD,
    GOLD_REVIEW_DECISION_DIR,
    GOLD_REVIEW_DECISION_INDEX_MD,
    GOLD_REVIEW_DECISION_PROGRESS_JSON,
    GOLD_REVIEW_DECISION_PROGRESS_MD,
    GOLD_REVIEW_PRIORITY_PACKET_DIR,
    GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD,
    GOLD_REVIEW_PRIORITY_PACKET_JSON,
    GOLD_REVIEW_PROGRESS_JSON,
    GOLD_REVIEW_PROGRESS_MD,
    GOLD_REVIEW_SESSION_PLAN_JSON,
    GOLD_REVIEW_SESSION_PLAN_MD,
    GOLD_REVIEW_WORKLIST_JSON,
    GOLD_REVIEW_WORKLIST_MD,
    GOLD_REVIEW_WORKLOAD_PLAN_JSON,
    GOLD_REVIEW_WORKLOAD_PLAN_MD,
    GOLD_SEMANTIC_GROUPS_JSON,
    GOLD_SEMANTIC_GROUPS_MD,
    GOLD_VALIDATION_REPORT_JSON,
    GOLD_VALIDATION_REPORT_MD,
    PREDICTION_OUTPUT_VALIDATION_REPORT_JSON,
    PREDICTION_OUTPUT_VALIDATION_REPORT_MD,
    READINESS_REPORT_JSON,
    READINESS_REPORT_MD,
    REJECTION_ADJUDICATION_JSON,
    REJECTION_ADJUDICATION_MD,
    SCORING_REPORT_JSON,
    SCORING_REPORT_MD,
)
from ._gold_validation import (
    build_gold_annotation_validation_report,
    build_gold_freeze_status,
    gold_freeze_status_markdown,
    gold_validation_markdown,
)
from ._rejection_adjudication import (
    build_rejection_adjudication_report,
    rejection_adjudication_markdown,
)
from ._gold_review import (
    build_gold_review_batches,
    build_gold_review_decision_progress,
    build_gold_review_decision_templates,
    build_gold_review_priority_packets,
    build_gold_review_progress,
    build_gold_review_session_plan,
    build_gold_review_worklist,
    build_gold_review_workload_plan,
    build_gold_semantic_groups,
    build_system_candidate_review_package,
    gold_review_batch_index_markdown,
    gold_review_batch_markdown,
    gold_review_decision_has_manual_edits,
    gold_review_decision_index_markdown,
    gold_review_decision_progress_markdown,
    gold_review_priority_packet_index_markdown,
    gold_review_priority_packet_markdown,
    gold_review_priority_packet_summary,
    gold_review_progress_markdown,
    gold_review_session_plan_markdown,
    gold_review_worklist_markdown,
    gold_review_workload_plan_markdown,
    gold_semantic_groups_markdown,
    read_gold_review_decisions,
    system_candidate_review_markdown,
)
from ._extraction import (
    prepare_formal_experiment_inputs,
)
from ._prediction_validation import (
    build_prediction_output_validation_report,
    prediction_output_validation_markdown,
)
from ._audit_reports import (
    build_formal_experiment_readiness,
    build_formal_experiment_score_report,
    markdown_report,
    score_report_markdown,
)

def run_formal_experiment_readiness(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    prepare_inputs: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    prepared = prepare_formal_experiment_inputs(repo_root) if prepare_inputs else None
    gold_worklist = build_gold_review_worklist(repo_root)
    gold_validation = build_gold_annotation_validation_report(repo_root)
    gold_freeze_status = build_gold_freeze_status(repo_root)
    prediction_validation = build_prediction_output_validation_report(repo_root)
    candidate_review = build_system_candidate_review_package(repo_root)
    batch_report = build_gold_review_batches(repo_root, candidate_review=candidate_review)
    workload_plan = build_gold_review_workload_plan(repo_root)
    semantic_groups = build_gold_semantic_groups(repo_root, workload_plan=workload_plan)
    priority_packets = build_gold_review_priority_packets(repo_root)
    existing_decision_root = repo_root / GOLD_REVIEW_DECISION_DIR
    existing_decisions = (
        read_gold_review_decisions(existing_decision_root)
        if existing_decision_root.exists()
        else []
    )
    preserve_existing_decisions = any(
        gold_review_decision_has_manual_edits(decision)
        for decision in existing_decisions
    )
    decision_report = build_gold_review_decision_templates(
        repo_root,
        batch_report=batch_report,
    )
    progress_report = build_gold_review_progress(repo_root, batch_report=batch_report)
    rejection_adjudication = build_rejection_adjudication_report(repo_root)
    write_json(repo_root / GOLD_REVIEW_WORKLIST_JSON, gold_worklist)
    write_json(repo_root / GOLD_VALIDATION_REPORT_JSON, gold_validation)
    write_json(repo_root / GOLD_FREEZE_REPORT_JSON, gold_freeze_status)
    write_json(repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_JSON, prediction_validation)
    write_json(repo_root / REJECTION_ADJUDICATION_JSON, rejection_adjudication)
    write_json(repo_root / GOLD_REVIEW_PROGRESS_JSON, progress_report)
    write_json(repo_root / GOLD_REVIEW_WORKLOAD_PLAN_JSON, workload_plan)
    write_json(repo_root / GOLD_SEMANTIC_GROUPS_JSON, semantic_groups)
    write_json(
        repo_root / GOLD_REVIEW_PRIORITY_PACKET_JSON,
        gold_review_priority_packet_summary(priority_packets),
    )
    write_jsonl(repo_root / GOLD_CANDIDATE_REVIEW_JSONL, candidate_review["records"])
    (repo_root / GOLD_REVIEW_WORKLIST_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_REVIEW_WORKLIST_MD).write_text(
        gold_review_worklist_markdown(gold_worklist),
        encoding="utf-8",
    )
    (repo_root / GOLD_VALIDATION_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_VALIDATION_REPORT_MD).write_text(
        gold_validation_markdown(gold_validation),
        encoding="utf-8",
    )
    (repo_root / GOLD_FREEZE_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_FREEZE_REPORT_MD).write_text(
        gold_freeze_status_markdown(gold_freeze_status),
        encoding="utf-8",
    )
    (repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD).write_text(
        prediction_output_validation_markdown(prediction_validation),
        encoding="utf-8",
    )
    (repo_root / GOLD_CANDIDATE_REVIEW_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_CANDIDATE_REVIEW_MD).write_text(
        system_candidate_review_markdown(candidate_review),
        encoding="utf-8",
    )
    (repo_root / GOLD_REVIEW_BATCH_DIR).mkdir(parents=True, exist_ok=True)
    for batch in batch_report["batches"]:
        (repo_root / batch["path"]).write_text(
            gold_review_batch_markdown(batch),
            encoding="utf-8",
        )
    (repo_root / GOLD_REVIEW_BATCH_INDEX_MD).write_text(
        gold_review_batch_index_markdown(batch_report),
        encoding="utf-8",
    )
    (repo_root / GOLD_REVIEW_DECISION_DIR).mkdir(parents=True, exist_ok=True)
    if not preserve_existing_decisions:
        for batch in decision_report["batches"]:
            write_jsonl(repo_root / batch["path"], batch["records"])
        (repo_root / GOLD_REVIEW_DECISION_INDEX_MD).write_text(
            gold_review_decision_index_markdown(decision_report),
            encoding="utf-8",
        )
    decision_progress = build_gold_review_decision_progress(
        repo_root,
        batch_report=batch_report,
    )
    session_plan = build_gold_review_session_plan(
        repo_root,
        workload_plan=workload_plan,
        decision_progress=decision_progress,
    )
    report = build_formal_experiment_readiness(
        repo_root,
        session_plan=session_plan,
        decision_progress=decision_progress,
        review_progress=progress_report,
    )
    score_report = build_formal_experiment_score_report(repo_root)
    write_json(repo_root / GOLD_REVIEW_SESSION_PLAN_JSON, session_plan)
    write_json(repo_root / READINESS_REPORT_JSON, report)
    write_json(repo_root / SCORING_REPORT_JSON, score_report)
    (repo_root / GOLD_REVIEW_SESSION_PLAN_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_REVIEW_SESSION_PLAN_MD).write_text(
        gold_review_session_plan_markdown(session_plan),
        encoding="utf-8",
    )
    write_json(repo_root / GOLD_REVIEW_DECISION_PROGRESS_JSON, decision_progress)
    (repo_root / GOLD_REVIEW_DECISION_PROGRESS_MD).write_text(
        gold_review_decision_progress_markdown(decision_progress),
        encoding="utf-8",
    )
    (repo_root / GOLD_REVIEW_PROGRESS_MD).write_text(
        gold_review_progress_markdown(progress_report),
        encoding="utf-8",
    )
    (repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD).write_text(
        gold_review_workload_plan_markdown(workload_plan),
        encoding="utf-8",
    )
    (repo_root / GOLD_SEMANTIC_GROUPS_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_SEMANTIC_GROUPS_MD).write_text(
        gold_semantic_groups_markdown(semantic_groups),
        encoding="utf-8",
    )
    (repo_root / GOLD_REVIEW_PRIORITY_PACKET_DIR).mkdir(parents=True, exist_ok=True)
    for lane in priority_packets["lanes"]:
        (repo_root / lane["path"]).write_text(
            gold_review_priority_packet_markdown(lane),
            encoding="utf-8",
        )
    (repo_root / GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD).write_text(
        gold_review_priority_packet_index_markdown(priority_packets),
        encoding="utf-8",
    )
    (repo_root / REJECTION_ADJUDICATION_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / REJECTION_ADJUDICATION_MD).write_text(
        rejection_adjudication_markdown(rejection_adjudication),
        encoding="utf-8",
    )
    (repo_root / READINESS_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / READINESS_REPORT_MD).write_text(markdown_report(report), encoding="utf-8")
    (repo_root / SCORING_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / SCORING_REPORT_MD).write_text(
        score_report_markdown(score_report),
        encoding="utf-8",
    )
    return {
        "prepared_inputs": prepared,
        "gold_review_worklist_json": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLIST_JSON,
            repo_root,
        ),
        "gold_review_worklist_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLIST_MD,
            repo_root,
        ),
        "gold_validation_report_json": project_relative_path(
            repo_root / GOLD_VALIDATION_REPORT_JSON,
            repo_root,
        ),
        "gold_validation_report_markdown": project_relative_path(
            repo_root / GOLD_VALIDATION_REPORT_MD,
            repo_root,
        ),
        "gold_freeze_status_json": project_relative_path(
            repo_root / GOLD_FREEZE_REPORT_JSON,
            repo_root,
        ),
        "gold_freeze_status_markdown": project_relative_path(
            repo_root / GOLD_FREEZE_REPORT_MD,
            repo_root,
        ),
        "prediction_output_validation_report_json": project_relative_path(
            repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_JSON,
            repo_root,
        ),
        "prediction_output_validation_report_markdown": project_relative_path(
            repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD,
            repo_root,
        ),
        "candidate_review_jsonl": project_relative_path(
            repo_root / GOLD_CANDIDATE_REVIEW_JSONL,
            repo_root,
        ),
        "candidate_review_markdown": project_relative_path(
            repo_root / GOLD_CANDIDATE_REVIEW_MD,
            repo_root,
        ),
        "gold_review_batch_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_BATCH_INDEX_MD,
            repo_root,
        ),
        "gold_review_decision_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_INDEX_MD,
            repo_root,
        ),
        "gold_review_decision_progress_json": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_PROGRESS_JSON,
            repo_root,
        ),
        "gold_review_decision_progress_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_DECISION_PROGRESS_MD,
            repo_root,
        ),
        "gold_review_decision_templates_written": not preserve_existing_decisions,
        "gold_review_progress_json": project_relative_path(
            repo_root / GOLD_REVIEW_PROGRESS_JSON,
            repo_root,
        ),
        "gold_review_progress_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_PROGRESS_MD,
            repo_root,
        ),
        "gold_review_workload_plan_json": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLOAD_PLAN_JSON,
            repo_root,
        ),
        "gold_review_workload_plan_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD,
            repo_root,
        ),
        "gold_semantic_groups_json": project_relative_path(
            repo_root / GOLD_SEMANTIC_GROUPS_JSON,
            repo_root,
        ),
        "gold_semantic_groups_markdown": project_relative_path(
            repo_root / GOLD_SEMANTIC_GROUPS_MD,
            repo_root,
        ),
        "gold_review_session_plan_json": project_relative_path(
            repo_root / GOLD_REVIEW_SESSION_PLAN_JSON,
            repo_root,
        ),
        "gold_review_session_plan_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_SESSION_PLAN_MD,
            repo_root,
        ),
        "gold_review_priority_packet_json": project_relative_path(
            repo_root / GOLD_REVIEW_PRIORITY_PACKET_JSON,
            repo_root,
        ),
        "gold_review_priority_packet_index_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD,
            repo_root,
        ),
        "rejection_adjudication_json": project_relative_path(
            repo_root / REJECTION_ADJUDICATION_JSON,
            repo_root,
        ),
        "rejection_adjudication_markdown": project_relative_path(
            repo_root / REJECTION_ADJUDICATION_MD,
            repo_root,
        ),
        "report_json": project_relative_path(repo_root / READINESS_REPORT_JSON, repo_root),
        "report_markdown": project_relative_path(repo_root / READINESS_REPORT_MD, repo_root),
        "scoring_report_json": project_relative_path(repo_root / SCORING_REPORT_JSON, repo_root),
        "scoring_report_markdown": project_relative_path(repo_root / SCORING_REPORT_MD, repo_root),
        "gold_validation_status": gold_validation["status"],
        "prediction_output_validation_status": prediction_validation["status"],
        "status": report["status"],
        "scoring_status": score_report["status"],
        "missing_required_inputs": report["missing_required_inputs"],
    }

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare NASA ATMONTO formal experiment inputs and readiness report."
    )
    parser.add_argument("--repo-root", default=PROJECT_ROOT, type=Path)
    parser.add_argument(
        "--skip-prepare-inputs",
        action="store_true",
        help="Only rebuild the readiness report; do not regenerate input and prompt batches.",
    )
    return parser.parse_args(argv)

def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_formal_experiment_readiness(
        args.repo_root,
        prepare_inputs=not args.skip_prepare_inputs,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
