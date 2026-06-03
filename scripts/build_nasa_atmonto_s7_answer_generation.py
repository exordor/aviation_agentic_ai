from __future__ import annotations

import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.nasa_atmonto_s7_answer_generation import (
    write_nasa_atmonto_s7_answer_generation,
)


def main() -> int:
    config = load_default_config()
    report_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_nasa_atmonto_s7_answer_generation(output_dir=report_dir)
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
            },
            indent=2,
        )
    )
    print(
        f"Generated {result['metadata']['benchmark_label_count']} S7 answer-generation cases "
        f"across {len(result['metadata']['modes'])} modes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
