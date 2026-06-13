from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT
from aviation_agentic_ai.reporting.atmonto.s7.answer_review_decisions import (
    ALLOWED_CITATION_SUFFICIENCY,
    ALLOWED_EVIDENCE_SUPPORT,
    ALLOWED_PROFILE_BOUNDARY,
    ALLOWED_REVIEW_DECISIONS,
    ALLOWED_REVIEWER_ROLES,
)

DEFAULT_REPORT_NAME = "nasa_atmonto_s7_answer_review_protocol"


def build_nasa_atmonto_s7_answer_review_protocol() -> dict[str, Any]:
    return {
        "source_family": "nasa_atmonto_s7_answer_review_protocol",
        "status": "answer_review_protocol_created",
        "artifacts": {
            "worksheet": "reports/stages/nasa_atmonto_s7_answer_review_worksheet.html",
            "packet_json": "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json",
            "packet_csv": "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv",
            "import_report": "reports/stages/nasa_atmonto_s7_answer_review_import.md",
            "decision_report": "reports/stages/nasa_atmonto_s7_answer_review_decisions.md",
        },
        "review_scope": {
            "case_count": 60,
            "failure_priority_cases": 3,
            "coverage_success_cases": 57,
            "unit_of_review": (
                "One S7 answer-generation case: question, answer values, source chunks, "
                "graph triples, automatic metrics, and reviewer fields."
            ),
        },
        "allowed_values": {
            "review_decision": sorted(ALLOWED_REVIEW_DECISIONS),
            "evidence_support": sorted(ALLOWED_EVIDENCE_SUPPORT),
            "citation_sufficiency": sorted(ALLOWED_CITATION_SUFFICIENCY),
            "profile_boundary": sorted(ALLOWED_PROFILE_BOUNDARY),
            "reviewer_role": sorted(ALLOWED_REVIEWER_ROLES),
        },
        "commands": {
            "build_packet": "uv run python scripts/build_nasa_atmonto_s7_broad_answer_review_packet.py",
            "build_worksheet": "uv run python scripts/build_nasa_atmonto_s7_answer_review_worksheet.py",
            "validate_default_csv": "uv run python scripts/build_nasa_atmonto_s7_answer_review_decisions.py",
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
            "refresh_dashboard": "uv run aviation-ai report thesis-experiment-dashboard",
        },
        "claim_boundary": (
            "The protocol is a review procedure, not review evidence. S7 answer-layer "
            "human review is complete only after all 60 cases have complete, valid "
            "reviewer fields and the decision report reports human_review_completed=True."
        ),
    }


def write_nasa_atmonto_s7_answer_review_protocol_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO S7 Answer Review Protocol",
        "",
        "## Purpose",
        "",
        (
            "This protocol defines how the S7 answer-generation layer is reviewed after "
            "automatic source-bounded metrics. It is intended for human or external "
            "expert review of answer correctness, evidence support, citation sufficiency, "
            "and profile-boundary cases."
        ),
        "",
        "## Scope",
        "",
        f"- Cases: {result['review_scope']['case_count']}",
        f"- Failure-priority cases: {result['review_scope']['failure_priority_cases']}",
        f"- Coverage-success cases: {result['review_scope']['coverage_success_cases']}",
        f"- Unit of review: {result['review_scope']['unit_of_review']}",
        "",
        "## Artifacts",
        "",
    ]
    for label, rel_path in result["artifacts"].items():
        lines.append(f"- {label}: `{rel_path}`")
    lines.extend(
        [
            "",
            "## Reviewer Procedure",
            "",
            "1. Open the worksheet HTML in a browser.",
            "2. Filter to `failure` priority cases first, then review coverage-success cases.",
            "3. For each case, compare every answer value against the source chunks and graph triples.",
            "4. Fill every required reviewer field; keep automatic metric columns unchanged.",
            "5. Download the reviewed CSV from the worksheet.",
            "6. Validate the reviewed CSV with the decision-status script.",
            "7. Import the reviewed CSV only after validation succeeds.",
            "8. Regenerate the SOTA audit and thesis dashboard after valid decisions are available.",
            "",
            "## Decision Fields",
            "",
            "| Field | Allowed values |",
            "| --- | --- |",
        ]
    )
    for field, values in result["allowed_values"].items():
        lines.append(f"| `{field}` | {' / '.join(values)} |")
    lines.extend(
        [
            "",
            "Required free-text or identity fields:",
            "",
            "- `reviewer_notes`: optional explanatory note, recommended for non-correct decisions.",
            "- `reviewer_id_or_initials`: pseudonym or initials.",
            "- `reviewed_at`: date or ISO timestamp.",
            "",
            "## Validation Commands",
            "",
        ]
    )
    for label, command in result["commands"].items():
        lines.append(f"- {label}: `{command}`")
    lines.extend(
        [
            "",
            "## Completion Gate",
            "",
            (
                "The gate is complete only when "
                "`reports/stages/nasa_atmonto_s7_answer_review_decisions.json` reports "
                "`human_review_completed=true`, `completed_case_count=60`, "
                "`pending_case_count=0`, and `invalid_case_count=0`."
            ),
            "",
            "## Claim Boundary",
            "",
            result["claim_boundary"],
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_nasa_atmonto_s7_answer_review_protocol(
    *,
    output_dir: str | Path,
    repo_root: str | Path = PROJECT_ROOT,
    report_name: str = DEFAULT_REPORT_NAME,
) -> tuple[Path, dict[str, Any]]:
    result = build_nasa_atmonto_s7_answer_review_protocol()
    output = Path(repo_root) / output_dir if not Path(output_dir).is_absolute() else Path(output_dir)
    md_path = write_nasa_atmonto_s7_answer_review_protocol_markdown(
        result,
        output / f"{report_name}.md",
    )
    return md_path, result
