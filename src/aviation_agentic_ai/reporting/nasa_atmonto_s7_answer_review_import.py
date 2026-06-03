from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import write_json_report
from aviation_agentic_ai.reporting.nasa_atmonto_s7_answer_review_decisions import (
    DEFAULT_PACKET_PATH,
    DEFAULT_REVIEW_CSV_PATH,
    build_nasa_atmonto_s7_answer_review_decisions,
)

DEFAULT_REPORT_NAME = "nasa_atmonto_s7_answer_review_import"
DEFAULT_REVIEWED_CSV_PATH = Path(
    "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.reviewed.csv"
)


def build_nasa_atmonto_s7_answer_review_import(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    reviewed_csv_path: str | Path = DEFAULT_REVIEWED_CSV_PATH,
    packet_path: str | Path = DEFAULT_PACKET_PATH,
    canonical_review_csv_path: str | Path = DEFAULT_REVIEW_CSV_PATH,
    require_complete: bool = True,
) -> dict[str, Any]:
    root = Path(repo_root)
    reviewed_csv = _resolve(root, reviewed_csv_path)
    canonical_csv = _resolve(root, canonical_review_csv_path)
    packet = _resolve(root, packet_path)
    decision_report = build_nasa_atmonto_s7_answer_review_decisions(
        repo_root=root,
        packet_path=packet,
        review_csv_path=reviewed_csv,
    )
    failure_reasons = _failure_reasons(
        reviewed_csv=reviewed_csv,
        decision_report=decision_report,
        require_complete=require_complete,
    )
    can_import = not failure_reasons
    return {
        "source_family": "nasa_atmonto_s7_answer_review_import",
        "status": "review_import_ready" if can_import else "review_import_rejected",
        "metadata": {
            "reviewed_csv_path": project_relative_path(reviewed_csv, root),
            "canonical_review_csv_path": project_relative_path(canonical_csv, root),
            "packet_path": project_relative_path(packet, root),
            "require_complete": require_complete,
            "reviewed_csv_exists": reviewed_csv.exists(),
            "canonical_review_csv_exists": canonical_csv.exists(),
            "can_import": can_import,
            "imported": False,
            "decision_status": decision_report["status"],
            "expected_case_count": decision_report["metadata"]["expected_case_count"],
            "completed_case_count": decision_report["metadata"]["completed_case_count"],
            "pending_case_count": decision_report["metadata"]["pending_case_count"],
            "invalid_case_count": decision_report["metadata"]["invalid_case_count"],
            "human_review_completed": decision_report["metadata"]["human_review_completed"],
        },
        "failure_reasons": failure_reasons,
        "decision_aggregate": decision_report["aggregate"],
        "claim_boundary": (
            "This import report validates whether a reviewer-filled CSV is safe to "
            "promote to the canonical S7 answer-review CSV. It does not create or "
            "modify reviewer decisions."
        ),
    }


def write_nasa_atmonto_s7_answer_review_import_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    return write_json_report(result, output_path, sort_keys=False)


def write_nasa_atmonto_s7_answer_review_import_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO S7 Answer Review Import",
        "",
        "## Boundary",
        "",
        result["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- Status: `{result['status']}`",
        f"- Reviewed CSV: `{result['metadata']['reviewed_csv_path']}`",
        f"- Canonical CSV: `{result['metadata']['canonical_review_csv_path']}`",
        f"- Require complete: `{result['metadata']['require_complete']}`",
        f"- Can import: `{result['metadata']['can_import']}`",
        f"- Imported: `{result['metadata']['imported']}`",
        f"- Decision status: `{result['metadata']['decision_status']}`",
        f"- Expected cases: {result['metadata']['expected_case_count']}",
        f"- Completed cases: {result['metadata']['completed_case_count']}",
        f"- Pending cases: {result['metadata']['pending_case_count']}",
        f"- Invalid cases: {result['metadata']['invalid_case_count']}",
        f"- Human review completed: `{result['metadata']['human_review_completed']}`",
        "",
        "## Failure Reasons",
        "",
    ]
    if result["failure_reasons"]:
        lines.extend(f"- {reason}" for reason in result["failure_reasons"])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Decision Aggregate",
            "",
            f"- Row status counts: `{result['decision_aggregate']['row_status_counts']}`",
            f"- Review decision counts: `{result['decision_aggregate']['review_decision_counts']}`",
            f"- Missing review IDs: `{result['decision_aggregate']['missing_review_ids']}`",
            f"- Extra review IDs: `{result['decision_aggregate']['extra_review_ids']}`",
            f"- Duplicate review IDs: `{result['decision_aggregate']['duplicate_review_ids']}`",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_nasa_atmonto_s7_answer_review_import(
    *,
    output_dir: str | Path,
    repo_root: str | Path = PROJECT_ROOT,
    reviewed_csv_path: str | Path = DEFAULT_REVIEWED_CSV_PATH,
    packet_path: str | Path = DEFAULT_PACKET_PATH,
    canonical_review_csv_path: str | Path = DEFAULT_REVIEW_CSV_PATH,
    report_name: str = DEFAULT_REPORT_NAME,
    import_if_valid: bool = False,
    require_complete: bool = True,
) -> tuple[Path, Path, dict[str, Any]]:
    root = Path(repo_root)
    output = Path(output_dir)
    result = build_nasa_atmonto_s7_answer_review_import(
        repo_root=root,
        reviewed_csv_path=reviewed_csv_path,
        packet_path=packet_path,
        canonical_review_csv_path=canonical_review_csv_path,
        require_complete=require_complete,
    )
    if import_if_valid and result["metadata"]["can_import"]:
        reviewed_csv = _resolve(root, reviewed_csv_path)
        canonical_csv = _resolve(root, canonical_review_csv_path)
        backup_path = _backup_path(canonical_csv)
        if canonical_csv.exists():
            _atomic_copy(canonical_csv, backup_path)
        _atomic_copy(reviewed_csv, canonical_csv)
        result["status"] = "review_import_imported"
        result["metadata"]["imported"] = True
        result["metadata"]["backup_csv_path"] = project_relative_path(backup_path, root)
    json_path = write_nasa_atmonto_s7_answer_review_import_json(
        result,
        output / f"{report_name}.json",
    )
    md_path = write_nasa_atmonto_s7_answer_review_import_markdown(
        result,
        output / f"{report_name}.md",
    )
    return json_path, md_path, result


def _failure_reasons(
    *,
    reviewed_csv: Path,
    decision_report: dict[str, Any],
    require_complete: bool,
) -> list[str]:
    reasons = []
    if not reviewed_csv.exists():
        reasons.append("reviewed CSV does not exist")
    if decision_report["aggregate"]["missing_review_ids"]:
        reasons.append("reviewed CSV is missing expected review IDs")
    if decision_report["aggregate"]["extra_review_ids"]:
        reasons.append("reviewed CSV contains extra review IDs")
    if decision_report["aggregate"]["duplicate_review_ids"]:
        reasons.append("reviewed CSV contains duplicate review IDs")
    if decision_report["metadata"]["invalid_case_count"]:
        reasons.append("reviewed CSV contains invalid reviewer rows")
    if require_complete and decision_report["metadata"]["human_review_completed"] is not True:
        reasons.append("reviewed CSV is not a complete 60-case human review")
    return reasons


def _resolve(root: Path, path: str | Path) -> Path:
    source = Path(path)
    return source if source.is_absolute() else root / source


def _backup_path(path: Path) -> Path:
    return path.with_name(f"{path.stem}.pre_review_import{path.suffix}")


def _atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = destination.with_suffix(destination.suffix + ".tmp")
    with source.open("rb") as input_handle, tmp_path.open("wb") as output_handle:
        shutil.copyfileobj(input_handle, output_handle)
    tmp_path.replace(destination)
