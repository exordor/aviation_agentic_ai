from __future__ import annotations

import json

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.reporting.nasa_bga_domain_transfer_pilot import (
    write_nasa_bga_domain_transfer_pilot,
)


def main() -> int:
    config = load_default_config()
    output_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_nasa_bga_domain_transfer_pilot(
        output_dir=output_dir,
    )
    print(
        json.dumps(
            {
                "json_path": str(json_path),
                "markdown_path": str(md_path),
                "status": result["status"],
                "transfer_domain": result["metadata"]["transfer_domain"],
                "contract_statuses": {
                    item["step"]: item["status"]
                    for item in result["contract_coverage"]
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
