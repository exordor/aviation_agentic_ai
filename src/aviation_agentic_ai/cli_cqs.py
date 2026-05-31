from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.chunking.chunks import chunk_output_path_for_strategy
from aviation_agentic_ai.cli_common import (
    _safe_path,
    default_benchmark_chunks,
    default_benchmark_v2_gold_labels,
    default_boundary_cqs,
    default_gold_labels,
)
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
    try:
        default_chunks = _safe_path("chunks_file", "data/chunks/06_phak_ch4_0.jsonl")
        default_structure_chunks = chunk_output_path_for_strategy(default_chunks, "structure_aware")
        chunk_inputs = list(chunks_paths) or [
            path for path in (default_chunks, default_structure_chunks) if path.exists()
        ]
        output = output_path or default_gold_labels()
        payload = build_gold_draft(
            boundary_cqs or default_boundary_cqs(),
            chunk_inputs,
            output_path=output,
            max_chunks_per_strategy=max_chunks_per_strategy,
            max_spans=max_spans,
        )
        click.echo(f"Wrote {project_relative_path(output)}")
        click.echo(f"Drafted {len(payload['labels'])} gold labels from {len(chunk_inputs)} chunk files.")
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc


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
    try:
        label_path = gold_labels or default_benchmark_v2_gold_labels()
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
    except Exception as exc:
        raise click.ClickException(str(exc)) from exc
