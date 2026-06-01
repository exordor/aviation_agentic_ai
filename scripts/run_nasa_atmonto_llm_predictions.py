from __future__ import annotations

import argparse
import json
from pathlib import Path

from aviation_agentic_ai.ontology.atmonto_experiment import (
    LLM_RUN_SYSTEM_IDS,
    PROJECT_ROOT,
    run_llm_prediction_system,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run NASA ATMONTO formal experiment LLM prediction systems."
    )
    parser.add_argument("system_id", choices=sorted(LLM_RUN_SYSTEM_IDS))
    parser.add_argument("--repo-root", default=PROJECT_ROOT, type=Path)
    parser.add_argument("--temperature", default=0.0, type=float)
    parser.add_argument("--max-tokens", default=4096, type=int)
    parser.add_argument(
        "--limit",
        type=int,
        help=(
            "Optional smoke-run record limit. Limited runs write to the smoke output "
            "directory by default and are not used for formal scoring."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help=(
            "Optional custom output directory. Defaults to formal outputs for full runs "
            "and data/experiments/nasa_atmonto/formal/smoke for limited runs."
        ),
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from an existing prediction JSONL instead of starting from an empty file.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-record progress logs on stderr.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_llm_prediction_system(
        system_id=args.system_id,
        repo_root=args.repo_root,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        limit=args.limit,
        output_dir=args.output_dir,
        resume=args.resume,
        progress=not args.quiet,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
