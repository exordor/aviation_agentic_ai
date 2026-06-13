from __future__ import annotations

import argparse
import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.atmonto.s7.candidate_adjudication import (
    write_nasa_atmonto_s7_candidate_adjudication,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Adjudicate S7 human-review candidates without changing main metrics."
    )
    return parser.parse_args()


def main() -> int:
    parse_args()
    config = load_default_config()
    report_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_nasa_atmonto_s7_candidate_adjudication(
        output_dir=report_dir,
    )
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "status": result["status"],
                "failure_candidate_count": result["metadata"]["failure_candidate_count"],
                "decision_counts": result["summary"]["decision_counts"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
