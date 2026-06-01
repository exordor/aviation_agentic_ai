from __future__ import annotations

import argparse
import json
from pathlib import Path

from aviation_agentic_ai.ontology.atmonto_experiment import (
    GOLD_REVIEW_DECISION_DRAFT_PATH,
    GOLD_REVIEW_DECISION_DIR,
    apply_gold_review_decisions,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply reviewed NASA ATMONTO decision JSONL files to a gold template draft."
    )
    parser.add_argument(
        "--decision-dir",
        type=Path,
        default=GOLD_REVIEW_DECISION_DIR,
        help="Directory containing batch_*.jsonl decision files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=GOLD_REVIEW_DECISION_DRAFT_PATH,
        help="Output JSONL path for the reviewed gold draft.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = apply_gold_review_decisions(
        decision_dir=args.decision_dir,
        output_path=args.output,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
