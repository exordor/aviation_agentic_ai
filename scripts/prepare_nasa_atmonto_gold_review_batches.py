from __future__ import annotations

import argparse
import json

from aviation_agentic_ai.ontology.atmonto_experiment import run_gold_review_batches


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare reviewer-friendly NASA ATMONTO gold annotation batches."
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of sampled advisories per Markdown review batch.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_gold_review_batches(batch_size=args.batch_size)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
