from __future__ import annotations

import argparse
import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.nasa_atmonto_s7_answer_review_decisions import (
    DEFAULT_PACKET_PATH,
    DEFAULT_REPORT_NAME,
    DEFAULT_REVIEW_CSV_PATH,
    write_nasa_atmonto_s7_answer_review_decisions,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and summarize NASA ATMONTO S7 answer review decisions.",
    )
    parser.add_argument(
        "--packet",
        default=str(DEFAULT_PACKET_PATH),
        help="Path to the S7 broad answer review packet JSON.",
    )
    parser.add_argument(
        "--review-csv",
        default=str(DEFAULT_REVIEW_CSV_PATH),
        help="Path to the reviewer-filled CSV to validate.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for the JSON and Markdown decision report.",
    )
    parser.add_argument(
        "--report-name",
        default=DEFAULT_REPORT_NAME,
        help="Report basename without extension.",
    )
    args = parser.parse_args()
    config = load_default_config()
    output_dir = (
        resolve_project_path(args.output_dir)
        if args.output_dir
        else resolve_project_path(config["paths"]["stage_report_dir"])
    )
    json_path, md_path, result = write_nasa_atmonto_s7_answer_review_decisions(
        output_dir=output_dir,
        packet_path=args.packet,
        review_csv_path=args.review_csv,
        report_name=args.report_name,
    )
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "status": result["status"],
                "expected_case_count": result["metadata"]["expected_case_count"],
                "completed_case_count": result["metadata"]["completed_case_count"],
                "pending_case_count": result["metadata"]["pending_case_count"],
                "human_review_completed": result["metadata"]["human_review_completed"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
