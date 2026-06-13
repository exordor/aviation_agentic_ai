from __future__ import annotations

import argparse
import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.atmonto.agentic_loop.live_pilot import (
    DEFAULT_PREDICTION_OUTPUT_PATH,
    DEFAULT_REPORT_NAME,
    DEFAULT_RUN_METADATA_PATH,
    FULL_RUN_METADATA_PATH,
    FULL_RUN_PREDICTION_OUTPUT_PATH,
    FULL_RUN_REPORT_NAME,
    write_nasa_atmonto_s5_s6_live_agentic_pilot,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the bounded live S5/S6 multi-agent ATCSCC extraction pilot."
    )
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=1400)
    parser.add_argument(
        "--run-scope",
        choices=["pilot", "full_run"],
        default="pilot",
        help="Use full_run to write separate full-set artifacts instead of pilot artifacts.",
    )
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_default_config()
    report_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    report_name = FULL_RUN_REPORT_NAME if args.run_scope == "full_run" else DEFAULT_REPORT_NAME
    prediction_output_path = (
        FULL_RUN_PREDICTION_OUTPUT_PATH
        if args.run_scope == "full_run"
        else DEFAULT_PREDICTION_OUTPUT_PATH
    )
    run_metadata_output_path = (
        FULL_RUN_METADATA_PATH if args.run_scope == "full_run" else DEFAULT_RUN_METADATA_PATH
    )
    json_path, md_path, result = write_nasa_atmonto_s5_s6_live_agentic_pilot(
        output_dir=report_dir,
        report_name=report_name,
        prediction_output_path=prediction_output_path,
        run_metadata_output_path=run_metadata_output_path,
        limit=args.limit,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        run_scope=args.run_scope,
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
