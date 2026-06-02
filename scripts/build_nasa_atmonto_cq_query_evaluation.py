from __future__ import annotations

import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.nasa_atmonto_cq_queries import (
    write_nasa_atmonto_cq_query_evaluation,
)


def main() -> int:
    config = load_default_config()
    report_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, manifest_path, manifest_md_path, result = (
        write_nasa_atmonto_cq_query_evaluation(output_dir=report_dir)
    )
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "manifest_path": str(manifest_path),
                "manifest_markdown_path": str(manifest_md_path),
            },
            indent=2,
        )
    )
    print(
        f"Evaluated {result['metadata']['template_count']} CQ query templates "
        f"against {result['metadata']['system_count']} systems."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
