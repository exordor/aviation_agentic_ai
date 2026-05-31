from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.cli_common import default_ontology_path
from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.kg.extraction import (
    extract_kg_file,
    validate_kg_file,
    write_kg_ttl,
    write_kg_validation_reports,
)
from aviation_agentic_ai.paths import project_relative_path, resolve_output_path


@click.group()
def kg() -> None:
    """Knowledge graph extraction and validation commands."""


@kg.command("extract")
@click.option("--chunks", "chunks_path", type=click.Path(path_type=Path), default=None)
@click.option("--output", "output_path", type=click.Path(path_type=Path), default=None)
@click.option("--profile", "profile_path", type=click.Path(path_type=Path), default=None)
@click.option("--ontology-file", type=click.Path(path_type=Path), default=None)
@click.option("--ttl-output", type=click.Path(path_type=Path), default=None)
@click.option("--max-chunks", type=int, default=None)
@click.option("--dry-run", is_flag=True, help="Use deterministic profile-seed triples.")
@click.option(
    "--temperature",
    type=float,
    default=None,
    help="Override configs/default.yaml kg_extraction.temperature.",
)
@click.option(
    "--max-tokens",
    type=int,
    default=None,
    help="Override configs/default.yaml kg_extraction.max_tokens.",
)
def kg_extract(
    chunks_path: Path | None,
    output_path: Path | None,
    profile_path: Path | None,
    ontology_file: Path | None,
    ttl_output: Path | None,
    max_chunks: int | None,
    dry_run: bool,
    temperature: float | None,
    max_tokens: int | None,
) -> None:
    """Extract a focused provenance-aware ABox."""
    config = load_default_config()
    kg_config = config.get("kg_extraction", {})
    chunks = chunks_path or resolve_project_path(config["paths"]["chunks_file"])
    output = output_path or resolve_project_path(config["paths"]["kg_file"])
    if output_path is not None:
        output = resolve_output_path(output_path)
    profile = profile_path or resolve_project_path("configs/extraction_profile.yaml")
    ontology_path = ontology_file or default_ontology_path()

    def progress(index: int, total: int, chunk, triples_count: int) -> None:
        click.echo(
            f"Extracted KG chunk {index}/{total}: {chunk.chunk_id} "
            f"({triples_count} triples)."
        )

    path, triples, report = extract_kg_file(
        chunks,
        output,
        profile,
        ontology_path=ontology_path,
        max_chunks=max_chunks,
        dry_run=dry_run,
        temperature=temperature
        if temperature is not None
        else float(kg_config.get("temperature") or 0.0),
        max_tokens=max_tokens
        if max_tokens is not None
        else int(kg_config.get("max_tokens") or 4096),
        progress_callback=progress,
    )
    partial_info = ""
    if report.get("partial_success"):
        partial_info = (
            f" (partial: {report.get('valid_triples_written', 0)} valid written, "
            f"{report.get('invalid_triples_discarded', 0)} invalid discarded)"
        )
    elif not report.get("valid", True) and not report.get("partial_success"):
        click.echo(
            f"Warning: all {report.get('triples_total', len(triples))} triples failed validation "
            f"({report.get('errors_total', 0)} errors); wrote empty KG file.",
            err=True,
        )
    click.echo(
        f"Wrote {project_relative_path(path)} with {len(triples)} triples "
        f"({report['errors_total']} validation errors, "
        f"{report.get('extraction_errors_total', 0)} extraction errors).{partial_info}"
    )
    if ttl_output is not None:
        ttl_path = write_kg_ttl(triples, resolve_output_path(ttl_output))
        click.echo(f"Wrote {project_relative_path(ttl_path)}")


@kg.command("validate")
@click.option("--kg-file", "kg_path", type=click.Path(path_type=Path), default=None)
@click.option("--chunks", "chunks_path", type=click.Path(path_type=Path), default=None)
@click.option("--profile", "profile_path", type=click.Path(path_type=Path), default=None)
@click.option("--ontology-file", type=click.Path(path_type=Path), default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="kg_validation", show_default=True)
def kg_validate(
    kg_path: Path | None,
    chunks_path: Path | None,
    profile_path: Path | None,
    ontology_file: Path | None,
    output_dir: Path | None,
    report_name: str,
) -> None:
    """Validate KG artifacts."""
    config = load_default_config()
    report = validate_kg_file(
        kg_path or resolve_project_path(config["paths"]["kg_file"]),
        chunks_path or resolve_project_path(config["paths"]["chunks_file"]),
        profile_path or resolve_project_path("configs/extraction_profile.yaml"),
        ontology_path=ontology_file or default_ontology_path(),
    )
    if not report["valid"]:
        raise click.ClickException(
            f"KG validation failed with {report['errors_total']} errors: "
            f"{report['errors'][:3]}"
        )
    if output_dir is not None:
        json_path, md_path = write_kg_validation_reports(
            report,
            output_dir,
            report_name=report_name,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"OK: validated {report['triples_total']} KG triples.")
