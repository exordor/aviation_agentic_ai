from __future__ import annotations

import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.atmonto.s7.review_handoff import (
    write_nasa_atmonto_s7_review_handoff,
)


def main() -> int:
    config = load_default_config()
    output_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_nasa_atmonto_s7_review_handoff(
        output_dir=output_dir,
    )
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "status": result["status"],
                "case_count": result["metadata"]["case_count"],
                "decision_status": result["metadata"]["decision_status"],
                "completion_gate_passed": result["metadata"]["completion_gate_passed"],
                "failed_completion_criteria": result["metadata"][
                    "failed_completion_criteria"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
