from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report

DEFAULT_REPORT_NAME = "nasa_atmonto_s7_review_handoff"


ARTIFACTS: tuple[tuple[str, str, str], ...] = (
    (
        "worksheet_html",
        "reports/stages/nasa_atmonto_s7_answer_review_worksheet.html",
        "Interactive review worksheet for inspecting all selected S7 answer cases.",
    ),
    (
        "review_packet_markdown",
        "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.md",
        "Broad answer-review packet summary.",
    ),
    (
        "review_packet_json",
        "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json",
        "Machine-readable 60-case review packet.",
    ),
    (
        "review_packet_csv",
        "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv",
        "Canonical review CSV with blank reviewer fields until human review is recorded.",
    ),
    (
        "candidate_context",
        "reports/stages/nasa_atmonto_s7_human_review_candidates.md",
        "Failure-priority and candidate context used to seed review attention.",
    ),
    (
        "candidate_adjudication",
        "reports/stages/nasa_atmonto_s7_candidate_adjudication.md",
        "Candidate-level adjudication context and boundary notes.",
    ),
    (
        "review_protocol",
        "reports/stages/nasa_atmonto_s7_answer_review_protocol.md",
        "Reviewer procedure, fields, allowed values, and completion gate.",
    ),
    (
        "automated_adversarial_review",
        "reports/stages/nasa_atmonto_s7_automated_adversarial_review.md",
        "Automated multi-role answer-layer evidence, citation, CQ, and profile audit.",
    ),
    (
        "import_gate",
        "reports/stages/nasa_atmonto_s7_answer_review_import.md",
        "Safe reviewed-CSV import status.",
    ),
    (
        "decision_status",
        "reports/stages/nasa_atmonto_s7_answer_review_decisions.md",
        "Current human-review decision completeness status.",
    ),
    (
        "sota_completion_audit",
        "reports/stages/nasa_atmonto_sota_goal_audit.md",
        "Overall SOTA goal completion audit and failed criteria.",
    ),
)


def build_nasa_atmonto_s7_review_handoff(
    *,
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    root = Path(repo_root)
    packet = read_json_object_or_empty(
        root / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json"
    )
    import_report = read_json_object_or_empty(
        root / "reports/stages/nasa_atmonto_s7_answer_review_import.json"
    )
    decisions = read_json_object_or_empty(
        root / "reports/stages/nasa_atmonto_s7_answer_review_decisions.json"
    )
    automated_review = read_json_object_or_empty(
        root / "reports/stages/nasa_atmonto_s7_automated_adversarial_review.json"
    )
    sota_audit = read_json_object_or_empty(
        root / "reports/stages/nasa_atmonto_sota_goal_audit.json"
    )
    artifacts = [_artifact_entry(root, label, path, purpose) for label, path, purpose in ARTIFACTS]
    completion_gate = sota_audit.get("completion_gate", {}) if isinstance(sota_audit, dict) else {}
    return {
        "source_family": "nasa_atmonto_s7_review_handoff",
        "status": "s7_review_handoff_created",
        "metadata": {
            "packet_status": packet.get("status"),
            "case_count": packet.get("metadata", {}).get("case_count"),
            "failure_case_count": packet.get("metadata", {}).get("failure_case_count"),
            "coverage_success_case_count": packet.get("metadata", {}).get(
                "coverage_success_case_count"
            ),
            "import_status": import_report.get("status"),
            "import_can_import": import_report.get("metadata", {}).get("can_import"),
            "reviewed_csv_exists": import_report.get("metadata", {}).get("reviewed_csv_exists"),
            "decision_status": decisions.get("status"),
            "completed_case_count": decisions.get("metadata", {}).get("completed_case_count"),
            "pending_case_count": decisions.get("metadata", {}).get("pending_case_count"),
            "invalid_case_count": decisions.get("metadata", {}).get("invalid_case_count"),
            "human_review_completed": decisions.get("metadata", {}).get(
                "human_review_completed"
            ),
            "automated_review_status": automated_review.get("status"),
            "automated_review_case_count": automated_review.get("metadata", {}).get(
                "reviewed_case_count"
            ),
            "automated_review_completed": automated_review.get("metadata", {}).get(
                "automated_review_completed"
            ),
            "automated_review_accepted_case_count": automated_review.get(
                "metadata", {}
            ).get("accepted_case_count"),
            "automated_review_rejected_case_count": automated_review.get(
                "metadata", {}
            ).get("rejected_case_count"),
            "completion_gate_passed": completion_gate.get("passed"),
            "failed_completion_criteria": completion_gate.get("failed_criteria", []),
            "review_completion_mode": sota_audit.get("metadata", {}).get(
                "s7_review_completion_mode"
            ),
            "present_artifact_count": sum(1 for artifact in artifacts if artifact["present"]),
            "artifact_count": len(artifacts),
        },
        "artifacts": artifacts,
        "handoff_steps": [
            {
                "step": 1,
                "action": "Open the worksheet HTML and keep the protocol report visible.",
                "artifact": "reports/stages/nasa_atmonto_s7_answer_review_worksheet.html",
            },
            {
                "step": 2,
                "action": (
                    "Review failure-priority cases first, then all coverage-success cases. "
                    "Do not edit automatic metric columns."
                ),
                "artifact": "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv",
            },
            {
                "step": 3,
                "action": (
                    "Export the reviewer-filled CSV as "
                    "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.reviewed.csv."
                ),
                "artifact": "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.reviewed.csv",
            },
            {
                "step": 4,
                "action": (
                    "Either validate and import the human/expert reviewed CSV, or run "
                    "the automated adversarial review report for all 60 cases."
                ),
                "artifact": "reports/stages/nasa_atmonto_s7_answer_review_import.md",
            },
            {
                "step": 5,
                "action": "Regenerate the SOTA audit and require the completion gate to pass.",
                "artifact": "reports/stages/nasa_atmonto_sota_goal_audit.md",
            },
        ],
        "commands": {
            "open_worksheet": "open reports/stages/nasa_atmonto_s7_answer_review_worksheet.html",
            "validate_reviewed_csv": (
                "uv run python scripts/build_nasa_atmonto_s7_answer_review_decisions.py "
                "--review-csv reports/stages/nasa_atmonto_s7_broad_answer_review_packet.reviewed.csv"
            ),
            "import_reviewed_csv": (
                "uv run python scripts/import_nasa_atmonto_s7_reviewed_csv.py "
                "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.reviewed.csv "
                "--import-if-valid"
            ),
            "refresh_sota_audit": "uv run python scripts/build_nasa_atmonto_sota_goal_audit.py",
            "run_automated_adversarial_review": (
                "uv run python scripts/build_nasa_atmonto_s7_automated_adversarial_review.py"
            ),
            "require_sota_complete": (
                "uv run python scripts/build_nasa_atmonto_sota_goal_audit.py --require-complete"
            ),
        },
        "claim_boundary": (
            "This handoff is a reviewer-facing work aid. It does not certify answer "
            "correctness, expert review, operational readiness, or SOTA completion. "
            "Human/expert claims remain blocked unless the reviewed CSV is validly "
            "imported. Automated adversarial completion must be labelled separately."
        ),
    }


def write_nasa_atmonto_s7_review_handoff_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    return write_json_report(result, output_path, sort_keys=False)


def write_nasa_atmonto_s7_review_handoff_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = result["metadata"]
    lines = [
        "# NASA ATMONTO S7 Review Handoff",
        "",
        "## Boundary",
        "",
        result["claim_boundary"],
        "",
        "## Current State",
        "",
        f"- Packet status: `{metadata['packet_status']}`",
        f"- Review cases: {metadata['case_count']}",
        f"- Failure-priority cases: {metadata['failure_case_count']}",
        f"- Coverage-success cases: {metadata['coverage_success_case_count']}",
        f"- Import status: `{metadata['import_status']}`",
        f"- Import can proceed: `{metadata['import_can_import']}`",
        f"- Reviewed CSV exists: `{metadata['reviewed_csv_exists']}`",
        f"- Decision status: `{metadata['decision_status']}`",
        f"- Completed cases: {metadata['completed_case_count']}",
        f"- Pending cases: {metadata['pending_case_count']}",
        f"- Invalid cases: {metadata['invalid_case_count']}",
        f"- Human review completed: `{metadata['human_review_completed']}`",
        f"- Automated review status: `{metadata['automated_review_status']}`",
        f"- Automated review cases: {metadata['automated_review_case_count']}",
        f"- Automated review completed: `{metadata['automated_review_completed']}`",
        (
            "- Automated review accepted/rejected cases: "
            f"{metadata['automated_review_accepted_case_count']}/"
            f"{metadata['automated_review_rejected_case_count']}"
        ),
        f"- SOTA completion gate passed: `{metadata['completion_gate_passed']}`",
        f"- Failed completion criteria: `{metadata['failed_completion_criteria']}`",
        f"- S7 review completion mode: `{metadata['review_completion_mode']}`",
        "",
        "## Artifact Checklist",
        "",
        "| Artifact | Present | Path | Purpose |",
        "| --- | --- | --- | --- |",
    ]
    for artifact in result["artifacts"]:
        lines.append(
            f"| `{artifact['label']}` | `{artifact['present']}` | "
            f"`{artifact['path']}` | {artifact['purpose']} |"
        )
    lines.extend(["", "## Reviewer Handoff Steps", ""])
    for item in result["handoff_steps"]:
        lines.append(f"{item['step']}. {item['action']}")
        lines.append(f"   Artifact: `{item['artifact']}`")
    lines.extend(["", "## Commands", ""])
    for label, command in result["commands"].items():
        lines.append(f"- {label}: `{command}`")
    lines.extend(["", "## Completion Rule", ""])
    lines.append(
        "S7 answer-layer review can complete through either a 60-case human/expert "
        "CSV path or a 60-case automated adversarial path. The SOTA audit "
        "`--require-complete` command must exit 0, and the completion mode must "
        "remain visible in the report."
    )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_nasa_atmonto_s7_review_handoff(
    *,
    output_dir: str | Path,
    repo_root: str | Path = PROJECT_ROOT,
    report_name: str = DEFAULT_REPORT_NAME,
) -> tuple[Path, Path, dict[str, Any]]:
    output = Path(output_dir)
    result = build_nasa_atmonto_s7_review_handoff(repo_root=repo_root)
    json_path = write_nasa_atmonto_s7_review_handoff_json(
        result,
        output / f"{report_name}.json",
    )
    md_path = write_nasa_atmonto_s7_review_handoff_markdown(
        result,
        output / f"{report_name}.md",
    )
    return json_path, md_path, result


def _artifact_entry(root: Path, label: str, rel_path: str, purpose: str) -> dict[str, Any]:
    path = root / rel_path
    return {
        "label": label,
        "path": project_relative_path(path, root),
        "present": path.exists(),
        "purpose": purpose,
    }
