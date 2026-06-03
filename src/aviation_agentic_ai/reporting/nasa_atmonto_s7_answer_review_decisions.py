from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report

DEFAULT_REPORT_NAME = "nasa_atmonto_s7_answer_review_decisions"
DEFAULT_PACKET_PATH = Path("reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json")
DEFAULT_REVIEW_CSV_PATH = Path("reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv")

ALLOWED_REVIEW_DECISIONS = {
    "correct",
    "partially_correct",
    "incorrect",
    "abstention_correct",
    "profile_boundary",
    "unsure",
}
ALLOWED_EVIDENCE_SUPPORT = {
    "fully_supported",
    "partially_supported",
    "unsupported",
    "not_applicable",
}
ALLOWED_CITATION_SUFFICIENCY = {
    "sufficient",
    "partial",
    "insufficient",
    "not_applicable",
}
ALLOWED_PROFILE_BOUNDARY = {"yes", "no", "unsure"}
ALLOWED_REVIEWER_ROLES = {"external_expert", "human_reviewer", "supervisor"}
REQUIRED_REVIEW_FIELDS = (
    "review_decision",
    "evidence_support",
    "citation_sufficiency",
    "profile_boundary",
    "reviewer_id_or_initials",
    "reviewer_role",
    "reviewed_at",
)


def build_nasa_atmonto_s7_answer_review_decisions(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    packet_path: str | Path = DEFAULT_PACKET_PATH,
    review_csv_path: str | Path = DEFAULT_REVIEW_CSV_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    packet_source = _resolve(root, packet_path)
    csv_source = _resolve(root, review_csv_path)
    packet = read_json_object_or_empty(packet_source)
    expected_ids = _expected_review_ids(packet)
    rows = _read_csv_rows(csv_source)
    row_results = [_validate_row(row) for row in rows]
    ids = [str(row.get("review_id") or "") for row in rows]
    id_counts = Counter(ids)
    duplicate_ids = sorted(review_id for review_id, count in id_counts.items() if review_id and count > 1)
    row_id_set = {review_id for review_id in ids if review_id}
    missing_ids = sorted(expected_ids - row_id_set)
    extra_ids = sorted(row_id_set - expected_ids)
    status_counts = Counter(item["row_status"] for item in row_results)
    decision_counts = Counter(
        item["review_decision"]
        for item in row_results
        if item["row_status"] == "complete" and item["review_decision"]
    )
    reviewer_roles = Counter(
        item["reviewer_role"]
        for item in row_results
        if item["row_status"] == "complete" and item["reviewer_role"]
    )
    has_identity_errors = bool(missing_ids or extra_ids or duplicate_ids)
    completed = (
        bool(expected_ids)
        and status_counts.get("complete", 0) == len(expected_ids)
        and status_counts.get("invalid", 0) == 0
        and status_counts.get("pending", 0) == 0
        and not has_identity_errors
    )
    status = _decision_status(completed, status_counts)
    return {
        "source_family": "nasa_atmonto_s7_answer_review_decisions",
        "status": status,
        "metadata": {
            "packet_path": project_relative_path(packet_source, root),
            "review_csv_path": project_relative_path(csv_source, root),
            "expected_case_count": len(expected_ids),
            "csv_row_count": len(rows),
            "completed_case_count": status_counts.get("complete", 0),
            "pending_case_count": status_counts.get("pending", 0),
            "invalid_case_count": status_counts.get("invalid", 0),
            "human_review": completed,
            "human_review_completed": completed,
            "external_expert_certified": (
                completed and set(reviewer_roles) == {"external_expert"}
            ),
            "reviewer_roles": dict(sorted(reviewer_roles.items())),
        },
        "aggregate": {
            "row_status_counts": dict(sorted(status_counts.items())),
            "review_decision_counts": dict(sorted(decision_counts.items())),
            "missing_review_ids": missing_ids,
            "extra_review_ids": extra_ids,
            "duplicate_review_ids": duplicate_ids,
        },
        "row_results": row_results,
        "claim_boundary": (
            "This report validates and summarizes recorded human/expert review decisions. "
            "It does not create review decisions and does not certify expert review unless "
            "every case has complete reviewer fields with an accepted reviewer role."
        ),
    }


def write_nasa_atmonto_s7_answer_review_decisions_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    return write_json_report(result, output_path, sort_keys=False)


def write_nasa_atmonto_s7_answer_review_decisions_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO S7 Answer Review Decisions",
        "",
        "## Boundary",
        "",
        result["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- Status: `{result['status']}`",
        f"- Expected cases: {result['metadata']['expected_case_count']}",
        f"- CSV rows: {result['metadata']['csv_row_count']}",
        f"- Completed cases: {result['metadata']['completed_case_count']}",
        f"- Pending cases: {result['metadata']['pending_case_count']}",
        f"- Invalid cases: {result['metadata']['invalid_case_count']}",
        f"- Human review completed: `{result['metadata']['human_review_completed']}`",
        f"- External expert certified: `{result['metadata']['external_expert_certified']}`",
        "",
        "## Aggregate",
        "",
        f"- Row status counts: `{result['aggregate']['row_status_counts']}`",
        f"- Review decision counts: `{result['aggregate']['review_decision_counts']}`",
        f"- Reviewer roles: `{result['metadata']['reviewer_roles']}`",
        f"- Missing review IDs: `{result['aggregate']['missing_review_ids']}`",
        f"- Extra review IDs: `{result['aggregate']['extra_review_ids']}`",
        f"- Duplicate review IDs: `{result['aggregate']['duplicate_review_ids']}`",
        "",
        "## Invalid Or Pending Rows",
        "",
        "| Review ID | Status | Errors |",
        "| --- | --- | --- |",
    ]
    for item in result["row_results"]:
        if item["row_status"] == "complete":
            continue
        errors = "; ".join(item["errors"]) if item["errors"] else "not filled"
        lines.append(f"| `{item['review_id']}` | `{item['row_status']}` | {errors} |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_nasa_atmonto_s7_answer_review_decisions(
    *,
    output_dir: str | Path,
    repo_root: str | Path = PROJECT_ROOT,
    report_name: str = DEFAULT_REPORT_NAME,
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_nasa_atmonto_s7_answer_review_decisions(repo_root=repo_root)
    output = Path(output_dir)
    json_path = write_nasa_atmonto_s7_answer_review_decisions_json(
        result,
        output / f"{report_name}.json",
    )
    md_path = write_nasa_atmonto_s7_answer_review_decisions_markdown(
        result,
        output / f"{report_name}.md",
    )
    return json_path, md_path, result


def _resolve(root: Path, path: str | Path) -> Path:
    source = Path(path)
    return source if source.is_absolute() else root / source


def _expected_review_ids(packet: dict[str, Any]) -> set[str]:
    cases = packet.get("cases", []) if isinstance(packet.get("cases"), list) else []
    return {str(case.get("review_id") or "") for case in cases if isinstance(case, dict)}


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _validate_row(row: dict[str, str]) -> dict[str, Any]:
    normalized = {key: str(value or "").strip() for key, value in row.items()}
    review_values = [normalized.get(field, "") for field in REQUIRED_REVIEW_FIELDS]
    errors: list[str] = []
    if not any(review_values):
        return _row_result(normalized, "pending", errors)
    for field in REQUIRED_REVIEW_FIELDS:
        if not normalized.get(field):
            errors.append(f"missing {field}")
    _validate_allowed(normalized, "review_decision", ALLOWED_REVIEW_DECISIONS, errors)
    _validate_allowed(normalized, "evidence_support", ALLOWED_EVIDENCE_SUPPORT, errors)
    _validate_allowed(normalized, "citation_sufficiency", ALLOWED_CITATION_SUFFICIENCY, errors)
    _validate_allowed(normalized, "profile_boundary", ALLOWED_PROFILE_BOUNDARY, errors)
    _validate_allowed(normalized, "reviewer_role", ALLOWED_REVIEWER_ROLES, errors)
    return _row_result(normalized, "invalid" if errors else "complete", errors)


def _validate_allowed(
    row: dict[str, str],
    field: str,
    allowed_values: set[str],
    errors: list[str],
) -> None:
    value = row.get(field, "")
    if value and value not in allowed_values:
        errors.append(f"invalid {field}: {value}")


def _row_result(row: dict[str, str], status: str, errors: list[str]) -> dict[str, Any]:
    return {
        "review_id": row.get("review_id", ""),
        "row_status": status,
        "review_decision": row.get("review_decision", ""),
        "evidence_support": row.get("evidence_support", ""),
        "citation_sufficiency": row.get("citation_sufficiency", ""),
        "profile_boundary": row.get("profile_boundary", ""),
        "reviewer_role": row.get("reviewer_role", ""),
        "errors": errors,
    }


def _decision_status(completed: bool, status_counts: Counter[str]) -> str:
    if completed:
        return "s7_answer_review_decisions_completed"
    if status_counts.get("complete", 0) or status_counts.get("invalid", 0):
        return "s7_answer_review_decisions_partial_or_invalid"
    return "s7_answer_review_decisions_pending"
