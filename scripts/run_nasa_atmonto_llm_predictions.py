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
        help="Optional smoke-run record limit. Omit for the formal full 100-record run.",
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
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
