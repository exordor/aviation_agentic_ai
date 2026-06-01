from __future__ import annotations

import json

from aviation_agentic_ai.ontology.atmonto_experiment import (
    run_system_candidate_review_package,
)


def main() -> int:
    result = run_system_candidate_review_package()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
