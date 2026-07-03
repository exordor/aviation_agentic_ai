from __future__ import annotations

import argparse
import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.atmonto.s7.answer_review_import import (
    DEFAULT_PACKET_PATH,
    DEFAULT_REPORT_NAME,
    DEFAULT_REVIEW_CSV_PATH,
    DEFAULT_REVIEWED_CSV_PATH,
    write_nasa_atmonto_s7_answer_review_import,
)
from aviation_agentic_ai.reporting.atmonto.s7.answer_review_decisions import (
    write_nasa_atmonto_s7_answer_review_decisions,
)
from aviation_agentic_ai.reporting.atmonto.audit.sota_goal_audit import (
    write_nasa_atmonto_sota_goal_audit,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and optionally import a reviewer-filled S7 answer review CSV.",
    )
    parser.add_argument(
        "reviewed_csv",
        nargs="?",
        default=str(DEFAULT_REVIEWED_CSV_PATH),
        help="Reviewer-filled CSV exported from the S7 answer review worksheet.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for the import JSON and Markdown report.",
    )
    parser.add_argument(
        "--packet",
        default=str(DEFAULT_PACKET_PATH),
        help="Path to the S7 broad answer review packet JSON.",
    )
    parser.add_argument(
        "--canonical-review-csv",
        default=str(DEFAULT_REVIEW_CSV_PATH),
        help="Canonical S7 review CSV path to replace after successful validation.",
    )
    parser.add_argument(
        "--report-name",
        default=DEFAULT_REPORT_NAME,
        help="Report basename without extension.",
    )
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Allow importing partial valid review rows. Not recommended for final SOTA gate.",
    )
    parser.add_argument(
        "--import-if-valid",
        action="store_true",
        help="Replace the canonical S7 review CSV only if validation passes.",
    )
    parser.add_argument(
        "--no-refresh",
        action="store_true",
        help="Do not regenerate decision, SOTA audit, and dashboard reports after import.",
    )
    args = parser.parse_args()
    config = load_default_config()
    output_dir = (
        resolve_project_path(args.output_dir)
        if args.output_dir
        else resolve_project_path(config["paths"]["stage_report_dir"])
    )
    json_path, md_path, result = write_nasa_atmonto_s7_answer_review_import(
        output_dir=output_dir,
        reviewed_csv_path=args.reviewed_csv,
        packet_path=args.packet,
        canonical_review_csv_path=args.canonical_review_csv,
        report_name=args.report_name,
        import_if_valid=args.import_if_valid,
        require_complete=not args.allow_partial,
    )
    refreshed: dict[str, str] = {}
    if result["metadata"]["imported"] and not args.no_refresh:
        decisions_json, decisions_md, _decisions = write_nasa_atmonto_s7_answer_review_decisions(
            output_dir=output_dir,
        )
        sota_json, sota_md, _sota = write_nasa_atmonto_sota_goal_audit(
            output_dir=output_dir,
        )
        refreshed = {
            "decisions_json": str(decisions_json),
            "decisions_markdown": str(decisions_md),
            "sota_json": str(sota_json),
            "sota_markdown": str(sota_md),
        }
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "status": result["status"],
                "can_import": result["metadata"]["can_import"],
                "imported": result["metadata"]["imported"],
                "failure_reasons": result["failure_reasons"],
                "decision_status": result["metadata"]["decision_status"],
                "completed_case_count": result["metadata"]["completed_case_count"],
                "pending_case_count": result["metadata"]["pending_case_count"],
                "invalid_case_count": result["metadata"]["invalid_case_count"],
                "refreshed": refreshed,
            },
            indent=2,
        )
    )
    return 0 if result["metadata"]["can_import"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
