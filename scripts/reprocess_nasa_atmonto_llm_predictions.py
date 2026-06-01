from __future__ import annotations

import argparse
import json
from pathlib import Path

from aviation_agentic_ai.ontology.atmonto_experiment import (
    LLM_RUN_SYSTEM_IDS,
    PROJECT_ROOT,
    reprocess_llm_prediction_system_outputs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild NASA ATMONTO LLM prediction records from saved raw_response fields "
            "without calling an LLM."
        )
    )
    parser.add_argument("system_id", choices=sorted(LLM_RUN_SYSTEM_IDS | {"all"}))
    parser.add_argument("--repo-root", default=PROJECT_ROOT, type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional custom output directory. Defaults to the formal output directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    system_ids = sorted(LLM_RUN_SYSTEM_IDS) if args.system_id == "all" else [args.system_id]
    results = [
        reprocess_llm_prediction_system_outputs(
            system_id=system_id,
            repo_root=args.repo_root,
            output_dir=args.output_dir,
        )
        for system_id in system_ids
    ]
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
