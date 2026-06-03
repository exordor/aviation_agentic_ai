from __future__ import annotations

import argparse
import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.nasa_atmonto_s5_s6_live_agentic_pilot import (
    write_nasa_atmonto_s5_s6_live_agentic_pilot,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the bounded live S5/S6 multi-agent ATCSCC extraction pilot."
    )
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1400)
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_default_config()
    report_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_nasa_atmonto_s5_s6_live_agentic_pilot(
        output_dir=report_dir,
        limit=args.limit,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        progress=not args.quiet,
    )
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "status": result["status"],
                "live_llm_run": result["metadata"]["live_llm_run"],
                "record_count": result["metadata"]["record_count"],
                "s5_fact_count": result["metadata"]["s5_fact_count"],
                "s6_fact_count": result["metadata"]["s6_fact_count"],
                "quarantined_fact_count": result["metadata"]["quarantined_fact_count"],
                "s6_f1": result["metrics"]["s6_live_refined_semantic_metrics"]["f1"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
