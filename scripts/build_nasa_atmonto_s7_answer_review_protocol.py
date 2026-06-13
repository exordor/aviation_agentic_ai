from __future__ import annotations

import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.atmonto.s7.answer_review_protocol import (
    write_nasa_atmonto_s7_answer_review_protocol,
)


def main() -> int:
    config = load_default_config()
    output_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    md_path, result = write_nasa_atmonto_s7_answer_review_protocol(
        output_dir=output_dir,
    )
    print(
        json.dumps(
            {
                "markdown_path": str(md_path),
                "status": result["status"],
                "case_count": result["review_scope"]["case_count"],
                "failure_priority_cases": result["review_scope"]["failure_priority_cases"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
