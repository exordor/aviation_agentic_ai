from __future__ import annotations

import argparse
import json
from pathlib import Path

from aviation_agentic_ai.ontology.atmonto_experiment import (
    GOLD_REVIEWED_PATH,
    PROJECT_ROOT,
    freeze_reviewed_gold_set,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze reviewed NASA ATMONTO gold annotations for formal scoring."
    )
    parser.add_argument("--repo-root", default=PROJECT_ROOT, type=Path)
    parser.add_argument("--output", default=GOLD_REVIEWED_PATH, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = freeze_reviewed_gold_set(repo_root=args.repo_root, output_path=args.output)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "frozen" else 1


if __name__ == "__main__":
    raise SystemExit(main())
