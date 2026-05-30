from __future__ import annotations

import sys
from pathlib import Path

import click

from aviation_agentic_ai.chunking.chunks import DEFAULT_SEMANTIC_EMBEDDING_MODEL
from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.chunking_comparison import (
    write_chunking_category_analysis_v2,
    write_chunking_comparison,
    write_chunking_comparison_v2,
    write_chunking_implementation_audit,
    write_chunking_topk_sensitivity_v2,
)
from aviation_agentic_ai.retrieval.indexing import DEFAULT_COLLECTION_NAME


def register_chunking_report_commands(report: click.Group) -> None:
    @report.command("chunking-comparison")
    @click.option("--pdf", "pdf_path", type=click.Path(path_type=Path), default=None)
    @click.option("--boundary-cqs", type=click.Path(path_type=Path), default=None)
    @click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
    @click.option("--chunks", "chunks_path", type=click.Path(path_type=Path), default=None)
    @click.option("--index-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--collection-name", default=None)
    @click.option("--max-chars", type=int, default=1200, show_default=True)
    @click.option("--overlap-chars", type=int, default=150, show_default=True)
    @click.option("--max-questions", type=int, default=None)
    @click.option("--rebuild-chunks/--reuse-chunks", default=True, show_default=True)
    @click.option("--rebuild-indexes/--reuse-indexes", default=True, show_default=True)
    def report_chunking_comparison(
        pdf_path: Path | None,
        boundary_cqs: Path | None,
        gold_labels: Path | None,
        chunks_path: Path | None,
        index_dir: Path | None,
        output_dir: Path | None,
        collection_name: str | None,
        max_chars: int,
        overlap_chars: int,
        max_questions: int | None,
        rebuild_chunks: bool,
        rebuild_indexes: bool,
    ) -> None:
        """Compare chunking strategies using boundary-CQ vector retrieval."""
        config = load_default_config()
        retrieval_config = config.get("retrieval", {})
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, result = write_chunking_comparison(
            pdf_path or resolve_project_path(config["paths"]["raw_pdf"]),
            boundary_cqs or resolve_project_path("data/cqs/06_phak_ch4_0.boundary.json"),
            chunks_path or resolve_project_path(config["paths"]["chunks_file"]),
            index_dir or resolve_project_path(config["paths"]["index_dir"]) / "chroma",
            report_dir,
            collection_name=collection_name
            or retrieval_config.get("collection_name", DEFAULT_COLLECTION_NAME),
            max_chars=max_chars,
            overlap_chars=overlap_chars,
            vector_top_k=int(retrieval_config.get("vector_top_k", 5)),
            max_questions=max_questions,
            rebuild_chunks=rebuild_chunks,
            rebuild_indexes=rebuild_indexes,
            gold_labels_path=gold_labels,
            command=" ".join(["aviation-ai", *sys.argv[1:]]),
        )
        best = result["ranking"][0]["strategy"] if result["ranking"] else "none"
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(f"Compared {len(result['strategies'])} chunking strategies; best: {best}.")

    @report.command("chunking-implementation-audit")
    @click.option("--pdf", "pdf_path", type=click.Path(path_type=Path), default=None)
    @click.option("--chunks-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--max-pages", type=int, default=None)
    @click.option("--rebuild-chunks/--reuse-chunks", default=True, show_default=True)
    @click.option("--embedding-model", default=DEFAULT_SEMANTIC_EMBEDDING_MODEL, show_default=True)
    @click.option("--semantic-download/--no-semantic-download", default=True, show_default=True)
    def report_chunking_implementation_audit(
        pdf_path: Path | None,
        chunks_dir: Path | None,
        output_dir: Path | None,
        max_pages: int | None,
        rebuild_chunks: bool,
        embedding_model: str,
        semantic_download: bool,
    ) -> None:
        """Audit chunking strategy names against implemented behavior."""
        config = load_default_config()
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, result = write_chunking_implementation_audit(
            pdf_path or resolve_project_path(config["paths"]["raw_pdf"]),
            chunks_dir or resolve_project_path("data/chunks"),
            report_dir,
            max_pages=max_pages,
            rebuild_chunks=rebuild_chunks,
            embedding_model=embedding_model,
            semantic_download=semantic_download,
            command=" ".join(["aviation-ai", *sys.argv[1:]]),
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(f"Audited {result['metadata']['strategies_total']} chunking strategies.")

    @report.command("chunking-comparison-v2")
    @click.option("--pdf", "pdf_path", type=click.Path(path_type=Path), default=None)
    @click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
    @click.option("--chunks-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--index-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--collection-prefix", default="phak_ch4_chunking_v2", show_default=True)
    @click.option("--max-labels", type=int, default=None)
    @click.option("--rebuild-chunks/--reuse-chunks", default=True, show_default=True)
    @click.option("--rebuild-indexes/--reuse-indexes", default=True, show_default=True)
    @click.option("--embedding-model", default=DEFAULT_SEMANTIC_EMBEDDING_MODEL, show_default=True)
    @click.option("--semantic-download/--no-semantic-download", default=True, show_default=True)
    @click.option(
        "--evaluation-mode",
        type=click.Choice(["top_k", "fixed_context_budget"]),
        default="top_k",
        show_default=True,
    )
    @click.option("--context-budget-chars", type=int, default=4000, show_default=True)
    def report_chunking_comparison_v2(
        pdf_path: Path | None,
        gold_labels: Path | None,
        chunks_dir: Path | None,
        index_dir: Path | None,
        output_dir: Path | None,
        collection_prefix: str,
        max_labels: int | None,
        rebuild_chunks: bool,
        rebuild_indexes: bool,
        embedding_model: str,
        semantic_download: bool,
        evaluation_mode: str,
        context_budget_chars: int,
    ) -> None:
        """Compare mainstream chunking strategies on benchmark v2."""
        config = load_default_config()
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, failure_json, failure_md, result, _failures = (
            write_chunking_comparison_v2(
                pdf_path or resolve_project_path(config["paths"]["raw_pdf"]),
                gold_labels
                or resolve_project_path("data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"),
                chunks_dir or resolve_project_path("data/chunks"),
                index_dir or resolve_project_path("data/indexes") / "chunking_benchmark_v2",
                report_dir,
                collection_prefix=collection_prefix,
                max_labels=max_labels,
                rebuild_chunks=rebuild_chunks,
                rebuild_indexes=rebuild_indexes,
                embedding_model=embedding_model,
                semantic_download=semantic_download,
                evaluation_mode=evaluation_mode,
                context_budget_chars=context_budget_chars,
                command=" ".join(["aviation-ai", *sys.argv[1:]]),
            )
        )
        best = result["ranking"][0]["strategy"] if result["ranking"] else "none"
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(f"Wrote {project_relative_path(failure_json)}")
        click.echo(f"Wrote {project_relative_path(failure_md)}")
        click.echo(
            "Compared "
            f"{len(result['strategies'])} benchmark-v2 chunking strategies; "
            f"top supported-only Recall@5 strategy: {best}; mode={evaluation_mode}."
        )

    @report.command("chunking-topk-sensitivity-v2")
    @click.option("--pdf", "pdf_path", type=click.Path(path_type=Path), default=None)
    @click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
    @click.option("--chunks-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--index-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--collection-prefix", default="phak_ch4_chunking_v2", show_default=True)
    @click.option("--max-labels", type=int, default=None)
    @click.option("--rebuild-chunks/--reuse-chunks", default=True, show_default=True)
    @click.option("--rebuild-indexes/--reuse-indexes", default=True, show_default=True)
    @click.option("--embedding-model", default=DEFAULT_SEMANTIC_EMBEDDING_MODEL, show_default=True)
    @click.option("--semantic-download/--no-semantic-download", default=True, show_default=True)
    def report_chunking_topk_sensitivity_v2(
        pdf_path: Path | None,
        gold_labels: Path | None,
        chunks_dir: Path | None,
        index_dir: Path | None,
        output_dir: Path | None,
        collection_prefix: str,
        max_labels: int | None,
        rebuild_chunks: bool,
        rebuild_indexes: bool,
        embedding_model: str,
        semantic_download: bool,
    ) -> None:
        """Write benchmark-v2 top-k sensitivity diagnostics for chunking strategies."""
        config = load_default_config()
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, result = write_chunking_topk_sensitivity_v2(
            pdf_path or resolve_project_path(config["paths"]["raw_pdf"]),
            gold_labels or resolve_project_path("data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"),
            chunks_dir or resolve_project_path("data/chunks"),
            index_dir or resolve_project_path("data/indexes") / "chunking_benchmark_v2",
            report_dir,
            collection_prefix=collection_prefix,
            max_labels=max_labels,
            rebuild_chunks=rebuild_chunks,
            rebuild_indexes=rebuild_indexes,
            embedding_model=embedding_model,
            semantic_download=semantic_download,
            command=" ".join(["aviation-ai", *sys.argv[1:]]),
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(
            "Wrote top-k sensitivity for k="
            f"{result['metadata']['top_k_values']}."
        )

    @report.command("chunking-category-analysis-v2")
    @click.option("--pdf", "pdf_path", type=click.Path(path_type=Path), default=None)
    @click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
    @click.option("--chunks-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--index-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--collection-prefix", default="phak_ch4_chunking_v2", show_default=True)
    @click.option("--max-labels", type=int, default=None)
    @click.option("--rebuild-chunks/--reuse-chunks", default=True, show_default=True)
    @click.option("--rebuild-indexes/--reuse-indexes", default=True, show_default=True)
    @click.option("--embedding-model", default=DEFAULT_SEMANTIC_EMBEDDING_MODEL, show_default=True)
    @click.option("--semantic-download/--no-semantic-download", default=True, show_default=True)
    def report_chunking_category_analysis_v2(
        pdf_path: Path | None,
        gold_labels: Path | None,
        chunks_dir: Path | None,
        index_dir: Path | None,
        output_dir: Path | None,
        collection_prefix: str,
        max_labels: int | None,
        rebuild_chunks: bool,
        rebuild_indexes: bool,
        embedding_model: str,
        semantic_download: bool,
    ) -> None:
        """Write benchmark-v2 category analysis for chunking strategies."""
        config = load_default_config()
        report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
        json_path, md_path, result = write_chunking_category_analysis_v2(
            pdf_path or resolve_project_path(config["paths"]["raw_pdf"]),
            gold_labels or resolve_project_path("data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"),
            chunks_dir or resolve_project_path("data/chunks"),
            index_dir or resolve_project_path("data/indexes") / "chunking_benchmark_v2",
            report_dir,
            collection_prefix=collection_prefix,
            max_labels=max_labels,
            rebuild_chunks=rebuild_chunks,
            rebuild_indexes=rebuild_indexes,
            embedding_model=embedding_model,
            semantic_download=semantic_download,
            command=" ".join(["aviation-ai", *sys.argv[1:]]),
        )
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(
            "Wrote category analysis for "
            f"{len(result['metadata']['categories'])} benchmark-v2 categories."
        )
