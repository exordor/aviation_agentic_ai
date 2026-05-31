from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.retrieval.indexing import DEFAULT_COLLECTION_NAME, build_chroma_index


@click.group()
def index() -> None:
    """Chunking and vector-index commands."""


@index.command("build")
@click.option("--chunks", "chunks_path", type=click.Path(path_type=Path), default=None)
@click.option("--index-dir", type=click.Path(path_type=Path), default=None)
@click.option("--collection-name", default=None)
@click.option("--reset/--no-reset", default=True, show_default=True)
def index_build(
    chunks_path: Path | None,
    index_dir: Path | None,
    collection_name: str | None,
    reset: bool,
) -> None:
    """Build retrieval indexes."""
    try:
        config = load_default_config()
        index_root = index_dir or resolve_project_path(config["paths"]["index_dir"]) / "chroma"
        report = build_chroma_index(
            chunks_path or resolve_project_path(config["paths"]["chunks_file"]),
            index_root,
            collection_name=collection_name
            or config.get("retrieval", {}).get("collection_name", DEFAULT_COLLECTION_NAME),
            reset=reset,
        )
        click.echo(
            f"Indexed {report['chunks_indexed']} chunks into "
            f"{report['collection_name']} at {report['index_dir']}."
        )
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
