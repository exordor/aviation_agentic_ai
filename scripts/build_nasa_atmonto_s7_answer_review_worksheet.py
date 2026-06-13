from __future__ import annotations

import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.atmonto.s7.answer_review_worksheet import (
    write_nasa_atmonto_s7_answer_review_worksheet,
)


def main() -> int:
    config = load_default_config()
    output_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    html_path, result = write_nasa_atmonto_s7_answer_review_worksheet(
        output_dir=output_dir,
    )
    print(
        json.dumps(
            {
                "html_path": str(html_path),
                "status": result["status"],
                "case_count": result["metadata"]["case_count"],
                "failure_case_count": result["metadata"]["failure_case_count"],
                "coverage_success_case_count": result["metadata"][
                    "coverage_success_case_count"
                ],
                "human_review_completed": result["metadata"]["human_review_completed"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
