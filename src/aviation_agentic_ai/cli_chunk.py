from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.chunking.chunks import (
    CHUNKING_STRATEGIES,
    build_chunk_file,
    chunk_output_path_for_strategy,
)
from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path


@click.group("chunk")
def chunk_group() -> None:
    """PDF chunking commands."""


@chunk_group.command("build")
@click.option("--pdf", "pdf_path", type=click.Path(path_type=Path), default=None)
@click.option("--output", "output_path", type=click.Path(path_type=Path), default=None)
@click.option(
    "--strategy",
    type=click.Choice(CHUNKING_STRATEGIES),
    default="fixed_window",
    show_default=True,
)
@click.option("--max-chars", type=int, default=1200, show_default=True)
@click.option("--overlap-chars", type=int, default=150, show_default=True)
@click.option("--max-pages", type=int, default=None)
def chunk_build(
    pdf_path: Path | None,
    output_path: Path | None,
    strategy: str,
    max_chars: int,
    overlap_chars: int,
    max_pages: int | None,
) -> None:
    """Build stable JSONL chunks from a source PDF."""
    config = load_default_config()
    default_output = chunk_output_path_for_strategy(
        resolve_project_path(config["paths"]["chunks_file"]),
        strategy,
    )
    path, chunks = build_chunk_file(
        pdf_path or resolve_project_path(config["paths"]["raw_pdf"]),
        output_path or default_output,
        max_chars=max_chars,
        overlap_chars=overlap_chars,
        max_pages=max_pages,
        strategy=strategy,
    )
    pages = sorted({chunk.page for chunk in chunks})
    click.echo(
        f"Wrote {project_relative_path(path)} with {len(chunks)} {strategy} chunks "
        f"from {len(pages)} pages."
    )
