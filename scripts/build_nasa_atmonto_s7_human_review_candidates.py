from __future__ import annotations

import argparse
import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.nasa_atmonto_s7_human_review_candidates import (
    write_nasa_atmonto_s7_human_review_candidates,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a candidate package for human review of S7 LLM answer cases."
    )
    parser.add_argument("--max-success-per-template", type=int, default=1)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_default_config()
    report_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_nasa_atmonto_s7_human_review_candidates(
        output_dir=report_dir,
        max_success_per_template=args.max_success_per_template,
    )
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "status": result["status"],
                "candidate_count": result["metadata"]["candidate_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
