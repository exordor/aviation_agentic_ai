from __future__ import annotations

import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.nasa_atmonto_s7_automated_adversarial_review import (
    write_nasa_atmonto_s7_automated_adversarial_review,
)


def main() -> int:
    config = load_default_config()
    output_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_nasa_atmonto_s7_automated_adversarial_review(
        output_dir=output_dir,
    )
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "status": result["status"],
                "reviewed_case_count": result["metadata"]["reviewed_case_count"],
                "accepted_case_count": result["metadata"]["accepted_case_count"],
                "flagged_case_count": result["metadata"]["flagged_case_count"],
                "rejected_case_count": result["metadata"]["rejected_case_count"],
                "automated_review_completed": result["metadata"][
                    "automated_review_completed"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
