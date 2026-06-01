from __future__ import annotations

import json

from aviation_agentic_ai.ontology.atmonto_experiment import run_gold_review_worklist


def main() -> int:
    result = run_gold_review_worklist()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
