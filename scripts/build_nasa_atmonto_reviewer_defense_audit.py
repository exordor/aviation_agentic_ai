from __future__ import annotations

import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.atmonto.audit.reviewer_defense_audit import (
    write_nasa_atmonto_reviewer_defense_audit,
)


def main() -> int:
    config = load_default_config()
    output_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_nasa_atmonto_reviewer_defense_audit(
        output_dir=output_dir,
    )
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "status": result["status"],
                "completion_claim": result["metadata"]["completion_claim"],
                "completion_scope": result["metadata"]["completion_scope"],
                "human_answer_review_completed": result["metadata"][
                    "human_answer_review_completed"
                ],
                "reviewer_finding_count": len(result["reviewer_findings"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
