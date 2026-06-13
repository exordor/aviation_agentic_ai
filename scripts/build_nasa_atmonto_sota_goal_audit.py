from __future__ import annotations

import argparse
import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.atmonto.audit.sota_goal_audit import (
    write_nasa_atmonto_sota_goal_audit,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the NASA ATMONTO SOTA goal completion audit."
    )
    parser.add_argument(
        "--require-complete",
        action="store_true",
        help="Exit with status 1 unless the internal diagnostic completion gate passes.",
    )
    parser.add_argument(
        "--require-human-review",
        action="store_true",
        help="Exit with status 1 unless the S7 human answer-review gate is complete.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_default_config()
    report_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_nasa_atmonto_sota_goal_audit(output_dir=report_dir)
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "status": result["status"],
                "completion_claim": result["completion_claim"],
                "completion_scope": result["metadata"]["s7_completion_scope"],
                "completion_gate_passed": result["completion_gate"]["passed"],
                "human_answer_review_completed": result["metadata"][
                    "s7_human_answer_review_completed"
                ],
                "expert_certification_completed": result["metadata"][
                    "s7_expert_certification_completed"
                ],
                "failed_criteria": result["completion_gate"]["failed_criteria"],
                "remaining_blockers": result["remaining_blockers"],
                "status_counts": result["metadata"]["status_counts"],
            },
            indent=2,
        )
    )
    if args.require_complete and not result["completion_gate"]["passed"]:
        return 1
    if args.require_human_review and not result["metadata"]["s7_human_answer_review_completed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
