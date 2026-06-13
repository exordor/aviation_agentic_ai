from __future__ import annotations

import argparse
import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.atmonto.s7.profile_decision import (
    write_nasa_atmonto_s7_profile_decision,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build S7 profile-decision what-if metrics without changing main scores."
    )
    return parser.parse_args()


def main() -> int:
    parse_args()
    config = load_default_config()
    report_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_nasa_atmonto_s7_profile_decision(
        output_dir=report_dir,
    )
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "status": result["status"],
                "corrected_record_count": result["metadata"]["corrected_record_count"],
                "strict_main_metrics_changed": result["metadata"][
                    "strict_main_metrics_changed"
                ],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
