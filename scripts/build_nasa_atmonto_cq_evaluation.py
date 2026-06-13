from __future__ import annotations

import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.atmonto.core.cq import write_nasa_atmonto_cq_evaluation


def main() -> int:
    config = load_default_config()
    report_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_nasa_atmonto_cq_evaluation(output_dir=report_dir)
    print(json.dumps({"json_path": str(json_path), "markdown_path": str(md_path)}, indent=2))
    print(
        f"Mapped {result['metadata']['cq_count']} CQs against "
        f"{result['gold_summary']['reviewed_records']} reviewed ATCSCC gold records."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
