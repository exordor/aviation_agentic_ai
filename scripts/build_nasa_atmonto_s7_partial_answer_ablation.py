from __future__ import annotations

import argparse
import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.atmonto.s7.partial_answer_ablation import (
    write_nasa_atmonto_s7_partial_answer_ablation,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a route-semantics partial-answer ablation report over S7 contexts."
    )
    parser.add_argument("--run-llm", action="store_true", help="Call the configured LLM.")
    parser.add_argument("--max-cases-per-mode", type=int, default=2)
    parser.add_argument("--max-tokens", type=int, default=500)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_default_config()
    report_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_nasa_atmonto_s7_partial_answer_ablation(
        output_dir=report_dir,
        run_llm=args.run_llm,
        max_cases_per_mode=args.max_cases_per_mode,
        max_tokens=args.max_tokens,
    )
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "status": result["status"],
            },
            indent=2,
        )
    )
    print(
        f"Selected {result['metadata']['selected_case_count']} S7 partial-answer cases "
        f"across {len(result['metadata']['modes'])} modes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
