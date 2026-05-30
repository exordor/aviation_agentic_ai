from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.chunking.chunks import chunk_output_path_for_strategy
from aviation_agentic_ai.cli_common import default_benchmark_chunks
from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.evaluation.benchmark_validation import validate_benchmark
from aviation_agentic_ai.evaluation.gold_draft import build_gold_draft
from aviation_agentic_ai.paths import project_relative_path


@click.group("cqs")
def cqs() -> None:
    """Competency-question gold label utilities."""


@cqs.command("gold-draft")
@click.option("--boundary-cqs", type=click.Path(path_type=Path), default=None)
@click.option("--chunks", "chunks_paths", type=click.Path(path_type=Path), multiple=True)
@click.option("--output", "output_path", type=click.Path(path_type=Path), default=None)
@click.option("--max-chunks-per-strategy", type=int, default=3, show_default=True)
@click.option("--max-spans", type=int, default=2, show_default=True)
def cqs_gold_draft(
    boundary_cqs: Path | None,
    chunks_paths: tuple[Path, ...],
    output_path: Path | None,
    max_chunks_per_strategy: int,
    max_spans: int,
) -> None:
    """Draft chunk/span gold labels from source chunks."""
    config = load_default_config()
    default_chunks = resolve_project_path(config["paths"]["chunks_file"])
    default_structure_chunks = chunk_output_path_for_strategy(default_chunks, "structure_aware")
    chunk_inputs = list(chunks_paths) or [
        path for path in (default_chunks, default_structure_chunks) if path.exists()
    ]
    output = output_path or resolve_project_path("data/cqs/06_phak_ch4_0.gold.json")
    payload = build_gold_draft(
        boundary_cqs or resolve_project_path("data/cqs/06_phak_ch4_0.boundary.json"),
        chunk_inputs,
        output_path=output,
        max_chunks_per_strategy=max_chunks_per_strategy,
        max_spans=max_spans,
    )
    click.echo(f"Wrote {project_relative_path(output)}")
    click.echo(f"Drafted {len(payload['labels'])} gold labels from {len(chunk_inputs)} chunk files.")


@cqs.command("validate-benchmark")
@click.option(
    "--gold-labels",
    type=click.Path(path_type=Path),
    default=None,
    help="Benchmark gold label JSON file to validate.",
)
@click.option(
    "--chunks",
    "chunks_paths",
    type=click.Path(path_type=Path),
    multiple=True,
    help="Source chunk JSONL files used to validate evidence spans.",
)
@click.option("--min-labels", type=int, default=100, show_default=True)
def cqs_validate_benchmark(
    gold_labels: Path | None,
    chunks_paths: tuple[Path, ...],
    min_labels: int,
) -> None:
    """Validate thesis benchmark gold labels against source chunks."""
    label_path = gold_labels or resolve_project_path(
        "data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"
    )
    chunk_inputs = list(chunks_paths) or default_benchmark_chunks()
    result = validate_benchmark(label_path, chunk_inputs, min_labels=min_labels)
    if not result["valid"]:
        details = "\n".join(result["errors"][:10])
        raise click.ClickException(
            f"Benchmark validation failed with {result['errors_total']} errors.\n{details}"
        )
    metadata = result["metadata"]
    click.echo(
        f"OK: validated {metadata['labels_total']} benchmark labels from "
        f"{project_relative_path(label_path)}"
    )
    click.echo(
        f"Supported: {metadata['supported_total']}; "
        f"insufficient-evidence: {metadata['no_answer_total']}; "
        f"warnings: {result['warnings_total']}"
    )
