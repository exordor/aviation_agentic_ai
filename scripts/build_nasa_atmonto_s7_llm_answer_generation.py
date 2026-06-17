from __future__ import annotations

import argparse
import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.atmonto.s7.llm_answer_generation import (
    S7_LLM_ANSWER_MODES,
    S7_VECTOR_ONLY_LLM_ANSWER_MODES,
    write_nasa_atmonto_s7_llm_answer_generation,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a fixed-budget LLM answer-generation report over S7 contexts."
    )
    parser.add_argument("--run-llm", action="store_true", help="Call the configured LLM.")
    parser.add_argument("--max-cases-per-mode", type=int, default=12)
    parser.add_argument("--max-cases-per-template", type=int, default=2)
    parser.add_argument("--max-tokens", type=int, default=500)
    parser.add_argument(
        "--modes",
        type=str,
        default=None,
        help=(
            "Comma-separated retrieval modes to run LLM answers over (must exist as "
            "`results[mode]` keys in the S7 retrieval report). Defaults to the KG-RAG "
            "modes. Pass `vector-only` to run the vector-only baseline "
            f"({', '.join(S7_VECTOR_ONLY_LLM_ANSWER_MODES)}) for the RQ3 head-to-head."
        ),
    )
    parser.add_argument(
        "--report-name",
        type=str,
        default="nasa_atmonto_s7_llm_answer_generation",
        help=(
            "Output report stem. Use a distinct name (e.g. "
            "nasa_atmonto_s7_vector_only_llm_answer_generation) for the vector-only arm "
            "so the verified KG-RAG report is not overwritten."
        ),
    )
    return parser.parse_args()


def resolve_modes(raw: str | None) -> tuple[str, ...]:
    if raw is None:
        return S7_LLM_ANSWER_MODES
    if raw.strip() == "vector-only":
        return S7_VECTOR_ONLY_LLM_ANSWER_MODES
    modes = tuple(part.strip() for part in raw.split(",") if part.strip())
    if not modes:
        raise SystemExit("--modes produced no modes after parsing.")
    return modes


def main() -> int:
    args = parse_args()
    modes = resolve_modes(args.modes)
    config = load_default_config()
    report_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_nasa_atmonto_s7_llm_answer_generation(
        output_dir=report_dir,
        report_name=args.report_name,
        modes=modes,
        run_llm=args.run_llm,
        max_cases_per_mode=args.max_cases_per_mode,
        max_cases_per_template=args.max_cases_per_template,
        max_tokens=args.max_tokens,
    )
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "status": result["status"],
                "modes": result["metadata"]["modes"],
            },
            indent=2,
        )
    )
    print(
        f"Selected {result['metadata']['selected_case_count']} S7 LLM answer cases "
        f"across {len(result['metadata']['modes'])} modes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
