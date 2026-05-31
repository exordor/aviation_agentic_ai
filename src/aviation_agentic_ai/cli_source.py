from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.sources.nasa_web import ingest_nasa_sources


@click.group("source")
def source_group() -> None:
    """Source ingestion commands."""


@source_group.command("ingest-nasa")
@click.option(
    "--manifest",
    type=click.Path(path_type=Path),
    default=None,
    help="NASA source manifest YAML.",
)
@click.option(
    "--raw-output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for normalized NASA page JSON/Markdown.",
)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option(
    "--fixture-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Optional HTML fixture directory for network-free ingestion.",
)
@click.option("--workers", type=int, default=4, show_default=True)
def ingest_nasa(
    manifest: Path | None,
    raw_output_dir: Path | None,
    output_dir: Path | None,
    fixture_dir: Path | None,
    workers: int,
) -> None:
    """Ingest NASA Glenn BGA aerodynamics pages from manifest."""
    try:
        config = load_default_config()
        manifest_path = manifest or resolve_project_path(
            "data/sources/nasa_bga_aerodynamics_sources.yaml"
        )
        raw_dir = raw_output_dir or resolve_project_path("data/raw/nasa_bga_aerodynamics")
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, result = ingest_nasa_sources(
            manifest_path,
            raw_output_dir=raw_dir,
            report_output_dir=report_dir,
            fixture_dir=fixture_dir,
            workers=workers,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(
            "Ingested "
            f"{result['metadata']['pages_total']} NASA pages with "
            f"{result['metadata']['valid_pages']} valid normalized pages."
        )
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
