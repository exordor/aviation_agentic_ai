from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.thesis_claims import write_thesis_claims_review


def register_thesis_report_commands(report: click.Group) -> None:

    @report.command("thesis-claims")
    @click.option(
        "--output-dir",
        type=click.Path(path_type=Path),
        default=None,
        help="Directory for thesis claim review outputs.",
    )
    @click.option(
        "--scan-path",
        "scan_paths",
        type=click.Path(path_type=Path),
        multiple=True,
        help="Markdown file to scan for unsafe thesis claims. Can be passed more than once.",
    )
    @click.option("--report-name", default="thesis_claims_review", show_default=True)
    def report_thesis_claims(
        output_dir: Path | None,
        scan_paths: tuple[Path, ...],
        report_name: str,
    ) -> None:
        """Review thesis claims, evidence support, and unsafe wording."""
        try:
            config = load_default_config()
            report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
            configured_scan_paths = list(scan_paths) if scan_paths else None
            json_path, md_path, result = write_thesis_claims_review(
                report_dir,
                scan_paths=configured_scan_paths,
                report_name=report_name,
            )
            click.echo(f"Wrote {project_relative_path(json_path)}")
            click.echo(f"Wrote {project_relative_path(md_path)}")
            click.echo(
                f"Reviewed thesis claims; unsafe claims found: "
                f"{result['metadata']['unsafe_claims_total']}."
            )
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc
