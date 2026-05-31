from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.retrieval.hybrid import run_query, write_query_result
from aviation_agentic_ai.retrieval.indexing import DEFAULT_COLLECTION_NAME


@click.command()
@click.argument("question", required=False)
@click.option("--mode", type=click.Choice(["graph", "vector", "hybrid"]), default="hybrid")
@click.option("--chunks", "chunks_path", type=click.Path(path_type=Path), default=None)
@click.option("--kg-file", "kg_path", type=click.Path(path_type=Path), default=None)
@click.option("--index-dir", type=click.Path(path_type=Path), default=None)
@click.option("--collection-name", default=None)
@click.option("--graph-method", type=click.Choice(["lexical", "traversal"]), default=None)
@click.option("--output", "output_path", type=click.Path(path_type=Path), default=None)
@click.option("--temperature", type=float, default=0.0, show_default=True)
@click.option("--max-tokens", type=int, default=1200, show_default=True)
def query(
    question: str | None,
    mode: str,
    chunks_path: Path | None,
    kg_path: Path | None,
    index_dir: Path | None,
    collection_name: str | None,
    graph_method: str | None,
    output_path: Path | None,
    temperature: float,
    max_tokens: int,
) -> None:
    """Query the GraphRAG prototype."""
    try:
        if not question:
            raise click.ClickException("Question is required.")
        config = load_default_config()
        retrieval_config = config.get("retrieval", {})
        result = run_query(
            question,
            mode,
            chunks_path or resolve_project_path(config["paths"]["chunks_file"]),
            kg_path or resolve_project_path(config["paths"]["kg_file"]),
            index_dir or resolve_project_path(config["paths"]["index_dir"]) / "chroma",
            collection_name=collection_name
            or retrieval_config.get("collection_name", DEFAULT_COLLECTION_NAME),
            graph_hops=int(retrieval_config.get("graph_hops") or 2),
            graph_method=graph_method or retrieval_config.get("graph_method", "lexical"),
            vector_top_k=int(retrieval_config.get("vector_top_k") or 5),
            hybrid_top_k=int(retrieval_config.get("hybrid_top_k") or 8),
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if output_path is not None:
            path = write_query_result(result, output_path)
            click.echo(f"Wrote {project_relative_path(path)}")
        click.echo(result["answer"])
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
