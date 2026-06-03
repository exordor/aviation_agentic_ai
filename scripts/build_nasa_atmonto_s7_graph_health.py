from __future__ import annotations

import argparse
import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.nasa_atmonto_s7_graph_health import (
    write_nasa_atmonto_s7_graph_health,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build graph-health diagnostics by CQ group from the S7 retrieval report."
    )
    parser.add_argument(
        "--s7-retrieval-report",
        default="reports/stages/nasa_atmonto_s7_retrieval.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_default_config()
    report_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_nasa_atmonto_s7_graph_health(
        output_dir=report_dir,
        s7_retrieval_report_path=args.s7_retrieval_report,
    )
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "status": result["status"],
                "retrieval_cases": result["metadata"]["retrieval_case_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
