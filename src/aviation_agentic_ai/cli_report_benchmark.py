from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.cli_common import default_benchmark_chunks
from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.benchmark_review_pack import (
    write_answer_eval_subset,
    write_benchmark_review_pack,
    write_benchmark_reviewed_subset,
)
from aviation_agentic_ai.reporting.benchmark_v2 import write_benchmark_v2_summary


def register_benchmark_report_commands(report: click.Group) -> None:
    @report.command("benchmark-v2")
    @click.option(
        "--gold-labels",
        type=click.Path(path_type=Path),
        default=None,
        help="Benchmark v2 gold label JSON file.",
    )
    @click.option(
        "--chunks",
        "chunks_paths",
        type=click.Path(path_type=Path),
        multiple=True,
        help="Source chunk JSONL files used to validate evidence spans.",
    )
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--report-name", default="benchmark_v2_summary", show_default=True)
    def report_benchmark_v2(
        gold_labels: Path | None,
        chunks_paths: tuple[Path, ...],
        output_dir: Path | None,
        report_name: str,
    ) -> None:
        """Write a summary and validation report for the thesis benchmark v2 labels."""
        config = load_default_config()
        label_path = gold_labels or resolve_project_path(
            "data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"
        )
        chunk_inputs = list(chunks_paths) or default_benchmark_chunks()
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, result = write_benchmark_v2_summary(
            label_path,
            chunk_inputs,
            report_dir,
            report_name=report_name,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(
            f"Summarized {result['metadata']['labels_total']} benchmark labels "
            f"with validation_passed={result['validation']['valid']}."
        )

    @report.command("benchmark-review-pack")
    @click.option(
        "--gold-labels",
        type=click.Path(path_type=Path),
        default=None,
        help="Benchmark v2 gold label JSON file.",
    )
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--report-name", default="benchmark_review_pack", show_default=True)
    @click.option(
        "--reviewed-output",
        type=click.Path(path_type=Path),
        default=None,
        help="Optional reviewed working-copy output path.",
    )
    @click.option(
        "--write-reviewed/--no-write-reviewed",
        default=True,
        show_default=True,
        help="Write the model-review working-copy file with LLM-review-pending statuses.",
    )
    def report_benchmark_review_pack(
        gold_labels: Path | None,
        output_dir: Path | None,
        report_name: str,
        reviewed_output: Path | None,
        write_reviewed: bool,
    ) -> None:
        """Prepare benchmark v2 labels for model-based review without certifying them."""
        config = load_default_config()
        label_path = gold_labels or resolve_project_path(
            "data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"
        )
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        reviewed_path = None
        if write_reviewed:
            reviewed_path = reviewed_output or resolve_project_path(
                "data/cqs/06_phak_ch4_0.benchmark_v2.reviewed.gold.json"
            )
        json_path, md_path, created_reviewed, result = write_benchmark_review_pack(
            label_path,
            report_dir,
            report_name=report_name,
            reviewed_output_path=reviewed_path,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        if created_reviewed is not None:
            click.echo(f"Wrote {project_relative_path(created_reviewed)}")
        click.echo(
            f"Prepared {result['metadata']['labels_total']} benchmark labels for model review."
        )

    @report.command("benchmark-reviewed-subset")
    @click.option(
        "--gold-labels",
        type=click.Path(path_type=Path),
        default=None,
        help="Benchmark v2 gold label JSON file.",
    )
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--report-name", default="benchmark_reviewed_subset_summary", show_default=True)
    @click.option(
        "--subset-output",
        type=click.Path(path_type=Path),
        default=None,
        help="Reviewed-subset gold label output path.",
    )
    def report_benchmark_reviewed_subset(
        gold_labels: Path | None,
        output_dir: Path | None,
        report_name: str,
        subset_output: Path | None,
    ) -> None:
        """Create the deterministic 60-label reviewed-subset scaffold and summary."""
        config = load_default_config()
        label_path = gold_labels or resolve_project_path(
            "data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"
        )
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        subset_path = subset_output or resolve_project_path(
            "data/cqs/06_phak_ch4_0.benchmark_v2.reviewed_subset.gold.json"
        )
        json_path, md_path, created_subset, result = write_benchmark_reviewed_subset(
            label_path,
            report_dir,
            subset_output_path=subset_path,
            report_name=report_name,
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(f"Wrote {project_relative_path(created_subset)}")
        click.echo(
            f"Prepared reviewed subset scaffold with {result['metadata']['labels_total']} labels."
        )

    @report.command("answer-eval-subset")
    @click.option(
        "--gold-labels",
        type=click.Path(path_type=Path),
        default=None,
        help="Benchmark v2 gold label JSON file.",
    )
    @click.option(
        "--subset-output",
        type=click.Path(path_type=Path),
        default=None,
        help="Answer-evaluation subset gold label output path.",
    )
    def report_answer_eval_subset(
        gold_labels: Path | None,
        subset_output: Path | None,
    ) -> None:
        """Create the deterministic answer-evaluation subset gold labels."""
        label_path = gold_labels or resolve_project_path(
            "data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"
        )
        subset_path = subset_output or resolve_project_path(
            "data/cqs/06_phak_ch4_0.answer_eval_subset.gold.json"
        )
        created_subset, result = write_answer_eval_subset(label_path, subset_path)
        click.echo(f"Wrote {project_relative_path(created_subset)}")
        click.echo(
            f"Prepared answer-eval subset with {len(result['labels'])} labels "
            "for deterministic heuristic scoring."
        )
