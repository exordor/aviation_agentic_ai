from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.web_demo import write_web_demo_readiness
from aviation_agentic_ai.reporting.web_demo_smoke import write_web_demo_smoke


def register_web_report_commands(report: click.Group) -> None:
    @report.command("web-demo-readiness")
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--report-name", default="web_demo_readiness", show_default=True)
    def report_web_demo_readiness(output_dir: Path | None, report_name: str) -> None:
        """Write offline-first web demo readiness reports."""
        config = load_default_config()
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, result = write_web_demo_readiness(
            report_dir,
            report_name=report_name,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(
            "Web demo readiness: "
            f"{result['ready']}; default strategy: {result['selected_default_strategy']}."
        )

    @report.command("web-demo-smoke")
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--report-name", default="web_demo_final_smoke", show_default=True)
    def report_web_demo_smoke(output_dir: Path | None, report_name: str) -> None:
        """Run offline FastAPI web demo smoke checks and write evidence reports."""
        config = load_default_config()
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, result = write_web_demo_smoke(
            report_dir,
            report_name=report_name,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(f"Web demo final smoke: {result['ready']}.")
