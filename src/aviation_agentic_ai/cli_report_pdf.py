from __future__ import annotations

import sys
from pathlib import Path

import click

from aviation_agentic_ai.cli_common import default_benchmark_v2_gold_labels
from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.pdf_extraction import (
    write_pdf_backend_chunking_comparison,
    write_pdf_extraction_comparison,
)


def register_pdf_report_commands(report: click.Group) -> None:
    @report.command("pdf-extraction-comparison")
    @click.option("--pdf", "pdf_path", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--normalized-output", type=click.Path(path_type=Path), default=None)
    @click.option("--reviews-dir", type=click.Path(path_type=Path), default=None)
    def report_pdf_extraction_comparison(
        pdf_path: Path | None,
        output_dir: Path | None,
        normalized_output: Path | None,
        reviews_dir: Path | None,
    ) -> None:
        """Compare PyMuPDF, Docling, and hybrid PDF extraction backends."""
        try:
            config = load_default_config()
            report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
            json_path, md_path, result = write_pdf_extraction_comparison(
                pdf_path or resolve_project_path(config["paths"]["raw_pdf"]),
                report_dir,
                normalized_output_path=normalized_output,
                reviews_dir=reviews_dir,
                command=" ".join(["aviation-ai", *sys.argv[1:]]),
            )
            legacy = result["backends"].get("pymupdf_text_legacy", {})
            docling = result["backends"].get("docling_structure", {})
            hybrid = result["backends"].get("hybrid_docling_pymupdf", {})
            click.echo(f"Wrote {project_relative_path(json_path)}")
            click.echo(f"Wrote {project_relative_path(md_path)}")
            click.echo(
                "Compared PDF backends; legacy false headings="
                f"{legacy.get('false_heading_count')}, Docling recall="
                f"{docling.get('heading_recall')}, hybrid repairs="
                f"{hybrid.get('repaired_artifact_count', 0)}."
            )
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

    @report.command("pdf-backend-chunking-comparison")
    @click.option("--pdf", "pdf_path", type=click.Path(path_type=Path), default=None)
    @click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
    @click.option("--chunks-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--max-labels", type=int, default=None)
    def report_pdf_backend_chunking_comparison(
        pdf_path: Path | None,
        gold_labels: Path | None,
        chunks_dir: Path | None,
        output_dir: Path | None,
        max_labels: int | None,
    ) -> None:
        """Compare downstream chunking impact of PDF extraction backends."""
        try:
            config = load_default_config()
            report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
            json_path, md_path, result = write_pdf_backend_chunking_comparison(
                pdf_path or resolve_project_path(config["paths"]["raw_pdf"]),
                gold_labels or default_benchmark_v2_gold_labels(),
                chunks_dir or resolve_project_path("data/chunks"),
                report_dir,
                max_labels=max_labels,
                command=" ".join(["aviation-ai", *sys.argv[1:]]),
            )
            best = result["ranking"][0]["strategy"] if result["ranking"] else "none"
            click.echo(f"Wrote {project_relative_path(json_path)}")
            click.echo(f"Wrote {project_relative_path(md_path)}")
            click.echo(
                "Compared PDF backend chunking strategies; best supported Recall@5 strategy: "
                f"{best}; recommended backend="
                f"{result['metadata']['recommended_default_backend']}."
            )
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc
