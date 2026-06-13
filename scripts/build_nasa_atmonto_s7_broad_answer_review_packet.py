from __future__ import annotations

import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.atmonto.s7.broad_answer_review_packet import (
    write_nasa_atmonto_s7_broad_answer_review_packet,
)


def main() -> int:
    config = load_default_config()
    output_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, csv_path, result = write_nasa_atmonto_s7_broad_answer_review_packet(
        output_dir=output_dir,
    )
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "csv_path": str(csv_path),
                "status": result["status"],
                "case_count": result["metadata"]["case_count"],
                "failure_case_count": result["metadata"]["failure_case_count"],
                "human_review_completed": result["metadata"]["human_review_completed"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
