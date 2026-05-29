from __future__ import annotations

import sys
from pathlib import Path

import click

from aviation_agentic_ai.chunking.chunks import (
    CHUNKING_STRATEGIES,
    build_chunk_file,
    chunk_output_path_for_strategy,
)
from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.evaluation.benchmark_validation import validate_benchmark
from aviation_agentic_ai.evaluation.gold_draft import build_gold_draft
from aviation_agentic_ai.kg.extraction import (
    KGValidationError,
    extract_kg_file,
    validate_kg_file,
    write_kg_ttl,
    write_kg_validation_reports,
)
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.ontology.cq import CQValidationError, generate_cqs, load_cq_artifact
from aviation_agentic_ai.ontology.evaluation import evaluate_ontology
from aviation_agentic_ai.ontology.generation import generate_ontology
from aviation_agentic_ai.ontology.reporting import write_stats_json, write_stats_markdown
from aviation_agentic_ai.ontology.source_scope import write_source_scope_reports
from aviation_agentic_ai.ontology.stats import collect_stats, load_graph
from aviation_agentic_ai.reporting.academic_outputs import (
    write_academic_report,
    write_defense_deck_outline,
    write_defense_notes,
    write_visual_assets,
)
from aviation_agentic_ai.reporting.answer_eval import write_answer_evaluation
from aviation_agentic_ai.reporting.benchmark_v2 import write_benchmark_v2_summary
from aviation_agentic_ai.reporting.chunking_comparison import write_chunking_comparison
from aviation_agentic_ai.reporting.evidence_cards import write_evidence_cards
from aviation_agentic_ai.reporting.evidence_eval import write_evidence_level_evaluation
from aviation_agentic_ai.reporting.final_evaluation import write_final_evaluation_review
from aviation_agentic_ai.reporting.graphrag_review import write_graphrag_review
from aviation_agentic_ai.reporting.graph_traversal_ablation import (
    write_graph_traversal_ablation,
)
from aviation_agentic_ai.reporting.hybrid_rag import write_hybrid_rag_experiment
from aviation_agentic_ai.reporting.generation_runs import write_generation_run_summary
from aviation_agentic_ai.reporting.hygiene import run_report_hygiene
from aviation_agentic_ai.reporting.kg_extraction_comparison import (
    write_kg_extraction_comparison,
)
from aviation_agentic_ai.reporting.overnight import write_overnight_summary
from aviation_agentic_ai.reporting.project_report import write_project_report
from aviation_agentic_ai.reporting.reviews import write_review_progress
from aviation_agentic_ai.reporting.retrieval_ablation import write_retrieval_ablation
from aviation_agentic_ai.reporting.robustness import write_robustness_evaluation
from aviation_agentic_ai.reporting.web_demo import write_web_demo_readiness
from aviation_agentic_ai.reporting.web_demo_smoke import write_web_demo_smoke
from aviation_agentic_ai.retrieval.hybrid import run_query, write_query_result
from aviation_agentic_ai.retrieval.indexing import DEFAULT_COLLECTION_NAME, build_chroma_index
from aviation_agentic_ai.web.server import serve_web_app


def _default_ontology_path() -> Path:
    config = load_default_config()
    curated = config["paths"].get("curated_ontology")
    if curated:
        curated_path = resolve_project_path(curated)
        if curated_path.exists():
            return curated_path
    return resolve_project_path(config["paths"]["baseline_ontology"])


def _ontology_generation_config() -> dict:
    from aviation_agentic_ai.config import load_yaml

    return load_yaml("configs/ontology_generation.yaml")


@click.group()
def main() -> None:
    """Aviation Agentic AI CLI."""


@main.group()
def web() -> None:
    """Local web demo commands."""


@web.command("serve")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", type=int, default=8000, show_default=True)
@click.option("--reload/--no-reload", default=False, show_default=True)
@click.option(
    "--enable-live-query/--disable-live-query",
    default=None,
    help="Force-enable or force-disable live LLM querying. Default: auto-detect readiness.",
)
def web_serve(host: str, port: int, reload: bool, enable_live_query: bool | None) -> None:
    """Serve the offline-first FastAPI web demo."""
    try:
        serve_web_app(
            host=host,
            port=port,
            reload=reload,
            enable_live_query=enable_live_query,
        )
    except RuntimeError as exc:
        raise click.ClickException(str(exc)) from exc


@main.group()
def ontology() -> None:
    """Ontology generation, validation, and reporting commands."""


@ontology.command("validate")
@click.option(
    "--ontology-file",
    type=click.Path(path_type=Path),
    default=None,
    help="TTL/RDF ontology file to validate.",
)
def ontology_validate(ontology_file: Path | None) -> None:
    """Parse an ontology file and report basic RDF validity."""
    path = ontology_file or _default_ontology_path()
    graph = load_graph(path)
    click.echo(f"OK: parsed {len(graph)} triples from {project_relative_path(path)}")


@ontology.command("report")
@click.option(
    "--ontology-file",
    type=click.Path(path_type=Path),
    default=None,
    help="TTL/RDF ontology file to report on.",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for JSON and Markdown report outputs.",
)
def ontology_report(ontology_file: Path | None, output_dir: Path | None) -> None:
    """Write ontology statistics reports."""
    config = load_default_config()
    path = ontology_file or _default_ontology_path()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    stats = collect_stats(path)
    json_path = write_stats_json(stats, report_dir / "ontology_stats.json")
    md_path = write_stats_markdown(stats, report_dir / "ontology_report.md")
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")


@ontology.command("evaluate")
@click.option(
    "--ontology-file",
    type=click.Path(path_type=Path),
    default=None,
    help="TTL/RDF ontology file to evaluate.",
)
@click.option(
    "--cq-file",
    type=click.Path(path_type=Path),
    default=None,
    help="Generated CQ JSON file to use for silver-CQ coverage evaluation.",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for JSON and Markdown evaluation outputs.",
)
@click.option("--sample-size", type=int, default=50, show_default=True)
@click.option("--seed", type=int, default=42, show_default=True)
@click.option(
    "--generated",
    is_flag=True,
    help="Evaluate the configured generated ontology instead of the baseline ontology.",
)
@click.option(
    "--report-name",
    default=None,
    help="Base filename for JSON/Markdown report outputs.",
)
@click.option(
    "--ai-review/--no-ai-review",
    default=False,
    show_default=True,
    help="Opt into or skip LLM-based CQ semantic review.",
)
def ontology_evaluate(
    ontology_file: Path | None,
    cq_file: Path | None,
    output_dir: Path | None,
    sample_size: int,
    seed: int,
    generated: bool,
    report_name: str | None,
    ai_review: bool,
) -> None:
    """Evaluate baseline ontology structure and silver-CQ coverage."""
    config = load_default_config()
    generation_config = _ontology_generation_config()
    if ontology_file is not None:
        path = ontology_file
    elif generated:
        path = resolve_project_path(generation_config["ontology_output"])
    else:
        path = _default_ontology_path()
    cqs = cq_file or resolve_project_path(generation_config["cq_output"])
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    output_name = report_name or ("generated_ontology_evaluation" if generated else "ontology_evaluation")
    result = evaluate_ontology(
        ontology_file=path,
        cq_file=cqs,
        output_dir=report_dir,
        sample_size=sample_size,
        seed=seed,
        ai_review=ai_review,
        report_name=output_name,
    )
    click.echo(f"Wrote {result['output_paths']['json']}")
    click.echo(f"Wrote {result['output_paths']['markdown']}")
    mode = "with AI review" if ai_review else "without AI review"
    click.echo(f"Evaluation completed {mode}.")


@ontology.command("scope")
@click.option("--pdf", "pdf_path", type=click.Path(path_type=Path), default=None)
@click.option("--existing-cqs", "existing_cq_path", type=click.Path(path_type=Path), default=None)
@click.option("--boundary-output", type=click.Path(path_type=Path), default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
def ontology_scope(
    pdf_path: Path | None,
    existing_cq_path: Path | None,
    boundary_output: Path | None,
    output_dir: Path | None,
) -> None:
    """Write PDF source scope, boundary CQs, and CQ gap review reports."""
    config = load_default_config()
    generation_config = _ontology_generation_config()
    pdf = pdf_path or resolve_project_path(generation_config["input_pdf"])
    existing_cqs = existing_cq_path or resolve_project_path(generation_config["cq_output"])
    boundary_cqs = boundary_output or resolve_project_path("data/cqs/06_phak_ch4_0.boundary.json")
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    result = write_source_scope_reports(pdf, existing_cqs, boundary_cqs, report_dir)
    for path in result["paths"].values():
        click.echo(f"Wrote {path}")
    click.echo(
        f"Source scope completed with {len(result['source_scope']['core_themes'])} themes "
        f"and {result['gap_review']['boundary_cq_count']} boundary CQs."
    )


@ontology.command("cqs")
@click.option("--pdf", "pdf_path", type=click.Path(path_type=Path), default=None)
@click.option("--output", "output_path", type=click.Path(path_type=Path), default=None)
@click.option("--domain-profile", default=None)
@click.option("--max-page-chars", type=int, default=None)
@click.option("--max-pages", type=int, default=None)
@click.option("--dry-run", is_flag=True, help="Build prompt previews without calling an LLM.")
def ontology_cqs(
    pdf_path: Path | None,
    output_path: Path | None,
    domain_profile: str | None,
    max_page_chars: int | None,
    max_pages: int | None,
    dry_run: bool,
) -> None:
    """Generate competency questions from source PDFs."""
    config = _ontology_generation_config()
    result = generate_cqs(
        pdf_path=pdf_path or resolve_project_path(config["input_pdf"]),
        output_path=output_path or resolve_project_path(config["cq_output"]),
        domain_profile=domain_profile or config["domain_profile"],
        max_page_chars=max_page_chars or config["max_page_chars"],
        max_pages=max_pages if max_pages is not None else config.get("max_pages"),
        dry_run=dry_run,
    )
    pages = len(next(iter(result.values()))) if result else 0
    click.echo(f"Wrote CQ output for {pages} pages.")


@main.group("cqs")
def cqs() -> None:
    """Competency-question gold label utilities."""


def _default_benchmark_chunks() -> list[Path]:
    config = load_default_config()
    default_chunks = resolve_project_path(config["paths"]["chunks_file"])
    structure_chunks = chunk_output_path_for_strategy(default_chunks, "structure_aware")
    return [path for path in (structure_chunks, default_chunks) if path.exists()]


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
    chunk_inputs = list(chunks_paths) or _default_benchmark_chunks()
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


@ontology.command("validate-cqs")
@click.option(
    "--cq-file",
    type=click.Path(path_type=Path),
    default=None,
    help="Generated normalized CQ JSON file to validate.",
)
def ontology_validate_cqs(cq_file: Path | None) -> None:
    """Validate normalized Competency Question artifacts."""
    config = _ontology_generation_config()
    path = cq_file or resolve_project_path(config["cq_output"])
    try:
        data = load_cq_artifact(path)
    except CQValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    count = 0
    for pages in data.values():
        if isinstance(pages, dict):
            count += sum(len(items) for items in pages.values() if isinstance(items, list))
    click.echo(f"OK: validated {count} normalized CQs from {project_relative_path(path)}")


@ontology.command("generate")
@click.option("--pdf", "pdf_path", type=click.Path(path_type=Path), default=None)
@click.option("--cqs", "cq_path", type=click.Path(path_type=Path), default=None)
@click.option("--output", "output_path", type=click.Path(path_type=Path), default=None)
@click.option("--domain-profile", default=None)
@click.option("--max-page-chars", type=int, default=None)
@click.option("--max-pages", type=int, default=None)
@click.option("--max-qa-cycles", type=int, default=None)
@click.option(
    "--artifact-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Optional directory for generation manifests and per-page checkpoints.",
)
@click.option("--run-id", default=None, help="Optional generation run identifier.")
@click.option("--dry-run", is_flag=True, help="Write the seed ontology without calling an LLM.")
def ontology_generate(
    pdf_path: Path | None,
    cq_path: Path | None,
    output_path: Path | None,
    domain_profile: str | None,
    max_page_chars: int | None,
    max_pages: int | None,
    max_qa_cycles: int | None,
    artifact_dir: Path | None,
    run_id: str | None,
    dry_run: bool,
) -> None:
    """Generate an ontology from source text and CQs."""
    config = _ontology_generation_config()
    result = generate_ontology(
        pdf_path=pdf_path or resolve_project_path(config["input_pdf"]),
        cq_path=cq_path or resolve_project_path(config["cq_output"]),
        output_path=output_path or resolve_project_path(config["ontology_output"]),
        domain_profile=domain_profile or config["domain_profile"],
        max_page_chars=max_page_chars or config["max_page_chars"],
        max_pages=max_pages if max_pages is not None else config.get("max_pages"),
        max_qa_cycles=max_qa_cycles if max_qa_cycles is not None else config["max_qa_cycles"],
        dry_run=dry_run,
        temperature=config["temperature"],
        max_tokens=config["max_tokens"],
        artifact_dir=artifact_dir,
        run_id=run_id,
    )
    status = "valid" if result.rdf_valid else "invalid"
    click.echo(
        f"Wrote {project_relative_path(result.output_path)} "
        f"({status}, pages processed: {result.pages_processed}). "
        f"{result.validation_message}"
    )


@main.group()
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
    temperature: float,
    max_tokens: int,
) -> None:
    """Extract a focused provenance-aware ABox."""
    config = load_default_config()
    kg_config = config.get("kg_extraction", {})
    chunks = chunks_path or resolve_project_path(config["paths"]["chunks_file"])
    output = output_path or resolve_project_path(config["paths"]["kg_file"])
    profile = profile_path or resolve_project_path("configs/extraction_profile.yaml")
    ontology_path = ontology_file or _default_ontology_path()

    def progress(index: int, total: int, chunk, triples_count: int) -> None:
        click.echo(
            f"Extracted KG chunk {index}/{total}: {chunk.chunk_id} "
            f"({triples_count} triples)."
        )

    try:
        path, triples, report = extract_kg_file(
            chunks,
            output,
            profile,
            ontology_path=ontology_path,
            max_chunks=max_chunks,
            dry_run=dry_run,
            temperature=temperature
            if temperature is not None
            else float(kg_config.get("temperature", 0.0)),
            max_tokens=max_tokens if max_tokens is not None else int(kg_config.get("max_tokens", 4096)),
            progress_callback=progress,
        )
    except KGValidationError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(
        f"Wrote {project_relative_path(path)} with {len(triples)} triples "
        f"({report['errors_total']} validation errors)."
    )
    if ttl_output is not None:
        ttl_path = write_kg_ttl(triples, ttl_output)
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
        ontology_path=ontology_file or _default_ontology_path(),
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


@main.group("chunk")
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


@main.group()
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


@main.command()
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
        graph_hops=int(retrieval_config.get("graph_hops", 2)),
        graph_method=graph_method or retrieval_config.get("graph_method", "lexical"),
        vector_top_k=int(retrieval_config.get("vector_top_k", 5)),
        hybrid_top_k=int(retrieval_config.get("hybrid_top_k", 8)),
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if output_path is not None:
        path = write_query_result(result, output_path)
        click.echo(f"Wrote {project_relative_path(path)}")
    click.echo(result["answer"])


@main.group()
def report() -> None:
    """Research report commands."""


@report.command("stages")
@click.option(
    "--reviews-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory containing review report JSON files.",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for stage report outputs.",
)
def report_stages(reviews_dir: Path | None, output_dir: Path | None) -> None:
    """Build stage reports."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    review_source_dir = reviews_dir or resolve_project_path("reports/reviews")
    review_json, review_md, progress = write_review_progress(
        review_source_dir, report_dir
    )
    generation_json, generation_md, _ = write_generation_run_summary(
        report_dir / "generation_runs", report_dir
    )
    overnight_json, overnight_md, _ = write_overnight_summary(report_dir)
    click.echo(f"Wrote {project_relative_path(review_json)}")
    click.echo(f"Wrote {project_relative_path(review_md)}")
    click.echo(f"Wrote {project_relative_path(generation_json)}")
    click.echo(f"Wrote {project_relative_path(generation_md)}")
    click.echo(f"Wrote {project_relative_path(overnight_json)}")
    click.echo(f"Wrote {project_relative_path(overnight_md)}")
    click.echo(
        f"Built stage reports from {progress['reviews_total']} review reports "
        f"with {len(progress['open_actions'])} open actions."
    )


@report.command("reviews")
@click.option(
    "--reviews-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory containing review report JSON files.",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for review progress outputs.",
)
def report_reviews(reviews_dir: Path | None, output_dir: Path | None) -> None:
    """Aggregate review reports into progress tracking outputs."""
    config = load_default_config()
    review_source_dir = reviews_dir or resolve_project_path("reports/reviews")
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, progress = write_review_progress(review_source_dir, report_dir)
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        f"Aggregated {progress['reviews_total']} review reports, "
        f"{progress['findings_total']} findings, and {progress['actions_total']} actions."
    )


@report.command("generation-runs")
@click.option(
    "--runs-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory containing generation run manifests.",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for generation run summary outputs.",
)
def report_generation_runs(runs_dir: Path | None, output_dir: Path | None) -> None:
    """Aggregate ontology generation run manifests."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    source_dir = runs_dir or report_dir / "generation_runs"
    json_path, md_path, summary = write_generation_run_summary(source_dir, report_dir)
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"Aggregated {summary['runs_total']} generation runs.")


@report.command("overnight")
@click.option(
    "--stage-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Stage report directory to summarize.",
)
def report_overnight(stage_dir: Path | None) -> None:
    """Write the overnight ontology optimization summary report."""
    config = load_default_config()
    report_dir = stage_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, summary = write_overnight_summary(report_dir)
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        "Overnight summary completed with "
        f"{len(summary['ontology_evaluation']['failed_quality_gates'])} failed quality gates."
    )


@report.command("hygiene")
@click.option(
    "--stage-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Stage report directory to clean into a dashboard.",
)
@click.option(
    "--archive-root",
    type=click.Path(path_type=Path),
    default=None,
    help="Archive root for stage artifacts.",
)
@click.option(
    "--reviews-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Review report directory to index but not archive.",
)
@click.option("--apply", "apply_changes", is_flag=True, help="Move artifacts and write index files.")
@click.option("--dry-run", "dry_run", is_flag=True, help="Print the hygiene plan only.")
def report_hygiene(
    stage_dir: Path | None,
    archive_root: Path | None,
    reviews_dir: Path | None,
    apply_changes: bool,
    dry_run: bool,
) -> None:
    """Plan or apply report hygiene for stage artifacts."""
    if dry_run and apply_changes:
        raise click.ClickException("Use either --dry-run or --apply, not both.")
    config = load_default_config()
    stages = stage_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    archive = archive_root or resolve_project_path("reports/archive")
    reviews = reviews_dir or resolve_project_path("reports/reviews")
    json_path, md_path, plan = run_report_hygiene(
        stages,
        archive,
        reviews,
        apply=apply_changes,
    )
    if apply_changes:
        click.echo(f"Wrote {project_relative_path(json_path)}")
        click.echo(f"Wrote {project_relative_path(md_path)}")
        click.echo(
            f"Archived {len(plan.get('moved_items', []))} stage artifacts into "
            f"{plan['archive_dir']}."
        )
    else:
        click.echo(
            f"Dry run: {plan['archive_items_total']} stage artifacts would be archived "
            f"into {plan['archive_dir']}."
        )
        click.echo(f"Review artifacts indexed in place: {plan['review_items_total']}.")


@report.command("project")
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for final project report outputs.",
)
@click.option(
    "--stage-index",
    type=click.Path(path_type=Path),
    default=None,
    help="Stage index JSON to use as primary evidence.",
)
@click.option("--ai/--no-ai", "use_ai", default=False, show_default=True)
@click.option("--temperature", type=float, default=0.0, show_default=True)
@click.option("--max-tokens", type=int, default=4096, show_default=True)
def report_project(
    output_dir: Path | None,
    stage_index: Path | None,
    use_ai: bool,
    temperature: float,
    max_tokens: int,
) -> None:
    """Generate the final project report from curated evidence."""
    output = output_dir or resolve_project_path("reports/final")
    md_path, sources_path, result = write_project_report(
        output,
        stage_index_path=stage_index,
        use_ai=use_ai,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"Wrote {project_relative_path(sources_path)}")
    mode = "AI-polished" if result["used_ai"] else "deterministic"
    click.echo(f"Generated {mode} project report.")


@report.command("academic-paper")
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for academic report outputs.",
)
@click.option(
    "--stage-index",
    type=click.Path(path_type=Path),
    default=None,
    help="Stage index JSON to use as primary evidence.",
)
@click.option("--ai/--no-ai", "use_ai", default=False, show_default=True)
def report_academic_paper(
    output_dir: Path | None,
    stage_index: Path | None,
    use_ai: bool,
) -> None:
    """Generate a paper-style academic project report from evidence."""
    if use_ai:
        raise click.ClickException(
            "AI polishing is intentionally disabled for this command in v1. "
            "Use --no-ai and review the deterministic draft."
        )
    output = output_dir or resolve_project_path("reports/final")
    md_path, sources_path, result = write_academic_report(
        output,
        stage_index_path=stage_index,
    )
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"Wrote {project_relative_path(sources_path)}")
    click.echo(
        "Generated deterministic academic report from "
        f"{len(result['summary']['source_paths'])} evidence sources."
    )


@report.command("defense-notes")
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for defense note outputs.",
)
@click.option(
    "--stage-index",
    type=click.Path(path_type=Path),
    default=None,
    help="Stage index JSON to use as primary evidence.",
)
def report_defense_notes(output_dir: Path | None, stage_index: Path | None) -> None:
    """Generate project defense notes and Q&A from evidence."""
    output = output_dir or resolve_project_path("reports/final")
    md_path, json_path, notes = write_defense_notes(
        output,
        stage_index_path=stage_index,
    )
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Generated {len(notes['qa_pairs'])} defense Q&A pairs.")


@report.command("defense-deck-outline")
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for defense deck outline outputs.",
)
@click.option(
    "--stage-index",
    type=click.Path(path_type=Path),
    default=None,
    help="Stage index JSON to use as primary evidence.",
)
def report_defense_deck_outline(output_dir: Path | None, stage_index: Path | None) -> None:
    """Generate an academic PPT outline and source pack."""
    output = output_dir or resolve_project_path("reports/final")
    md_path, json_path, outline = write_defense_deck_outline(
        output,
        stage_index_path=stage_index,
    )
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Generated {len(outline['slides'])} slide outlines.")


@report.command("visual-assets")
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for final visual assets.",
)
def report_visual_assets(output_dir: Path | None) -> None:
    """Generate SVG fallback assets and record any externally generated PNG assets."""
    output = output_dir or resolve_project_path("reports/final")
    paths, manifest = write_visual_assets(output)
    for path in paths:
        click.echo(f"Wrote {project_relative_path(path)}")
    click.echo(
        "Wrote visual asset manifest; AI PNG assets present: "
        f"{manifest['uses_gateway_or_api']}. "
        "No credentials or gateway URL were recorded."
    )


@report.command("hybrid-rag")
@click.option("--boundary-cqs", type=click.Path(path_type=Path), default=None)
@click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
@click.option("--chunks", "chunks_path", type=click.Path(path_type=Path), default=None)
@click.option("--kg-file", "kg_path", type=click.Path(path_type=Path), default=None)
@click.option("--index-dir", type=click.Path(path_type=Path), default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--collection-name", default=None)
@click.option("--chunking-strategy", default=None)
@click.option("--report-name", default="hybrid_rag_experiment", show_default=True)
@click.option("--max-questions", type=int, default=None)
def report_hybrid_rag(
    boundary_cqs: Path | None,
    gold_labels: Path | None,
    chunks_path: Path | None,
    kg_path: Path | None,
    index_dir: Path | None,
    output_dir: Path | None,
    collection_name: str | None,
    chunking_strategy: str | None,
    report_name: str,
    max_questions: int | None,
) -> None:
    """Run and report the boundary-CQ Hybrid RAG experiment."""
    config = load_default_config()
    retrieval_config = config.get("retrieval", {})
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_hybrid_rag_experiment(
        boundary_cqs or resolve_project_path("data/cqs/06_phak_ch4_0.boundary.json"),
        chunks_path or resolve_project_path(config["paths"]["chunks_file"]),
        kg_path or resolve_project_path(config["paths"]["kg_file"]),
        index_dir or resolve_project_path(config["paths"]["index_dir"]) / "chroma",
        report_dir,
        collection_name=collection_name
        or retrieval_config.get("collection_name", DEFAULT_COLLECTION_NAME),
        graph_hops=int(retrieval_config.get("graph_hops", 2)),
        vector_top_k=int(retrieval_config.get("vector_top_k", 5)),
        hybrid_top_k=int(retrieval_config.get("hybrid_top_k", 8)),
        max_questions=max_questions,
        gold_labels_path=gold_labels,
        chunking_strategy=chunking_strategy,
        report_name=report_name,
        command=" ".join(["aviation-ai", *sys.argv[1:]]),
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"Evaluated {result['metadata']['questions_total']} boundary CQs.")


@report.command("graphrag-review")
@click.option("--chunking-comparison", type=click.Path(path_type=Path), default=None)
@click.option("--fixed-hybrid", type=click.Path(path_type=Path), default=None)
@click.option("--structure-aware-hybrid", type=click.Path(path_type=Path), default=None)
@click.option("--evidence-eval", type=click.Path(path_type=Path), default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="graphrag_review", show_default=True)
def report_graphrag_review(
    chunking_comparison: Path | None,
    fixed_hybrid: Path | None,
    structure_aware_hybrid: Path | None,
    evidence_eval: Path | None,
    output_dir: Path | None,
    report_name: str,
) -> None:
    """Review GraphRAG value and failure modes across experiment reports."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    default_structure = report_dir / "hybrid_rag_structure_aware.json"
    structure_path = structure_aware_hybrid or (
        default_structure if default_structure.exists() else None
    )
    default_evidence = report_dir / "evidence_level_evaluation.json"
    evidence_path = evidence_eval or (default_evidence if default_evidence.exists() else None)
    json_path, md_path, result = write_graphrag_review(
        chunking_comparison or report_dir / "chunking_comparison.json",
        fixed_hybrid or report_dir / "hybrid_rag_experiment.json",
        report_dir,
        structure_aware_hybrid_path=structure_path,
        evidence_eval_path=evidence_path,
        report_name=report_name,
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    structure_status = "included" if result["metadata"]["structure_aware_present"] else "missing"
    evidence_status = "included" if result["metadata"]["evidence_eval_present"] else "missing"
    click.echo(
        f"Reviewed GraphRAG reports; structure-aware experiment: {structure_status}; "
        f"evidence evaluation: {evidence_status}."
    )


@report.command("evidence-eval")
@click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
@click.option("--fixed-hybrid", type=click.Path(path_type=Path), default=None)
@click.option("--structure-aware-hybrid", type=click.Path(path_type=Path), default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="evidence_level_evaluation", show_default=True)
def report_evidence_eval(
    gold_labels: Path | None,
    fixed_hybrid: Path | None,
    structure_aware_hybrid: Path | None,
    output_dir: Path | None,
    report_name: str,
) -> None:
    """Evaluate Hybrid RAG reports against chunk/span gold labels."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_evidence_level_evaluation(
        gold_labels or resolve_project_path("data/cqs/06_phak_ch4_0.gold.json"),
        report_dir,
        fixed_hybrid_path=fixed_hybrid or report_dir / "hybrid_rag_experiment.json",
        structure_aware_hybrid_path=structure_aware_hybrid
        or report_dir / "hybrid_rag_structure_aware.json",
        report_name=report_name,
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"Evaluated evidence-level metrics for {result['metadata']['labels_total']} CQs.")


@report.command("evidence-cards")
@click.option("--hybrid-report", type=click.Path(path_type=Path), default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="evidence_cards", show_default=True)
@click.option("--top-k", type=int, default=5, show_default=True)
def report_evidence_cards(
    hybrid_report: Path | None,
    output_dir: Path | None,
    report_name: str,
    top_k: int,
) -> None:
    """Write per-question evidence cards from an existing Hybrid RAG report."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    stage_dir = resolve_project_path(config["paths"]["stage_report_dir"])
    structure_report = stage_dir / "hybrid_rag_structure_aware.json"
    default_report = (
        structure_report
        if structure_report.exists()
        else stage_dir / "hybrid_rag_experiment.json"
    )
    json_path, md_path, result = write_evidence_cards(
        report_dir,
        hybrid_report_path=hybrid_report or default_report,
        report_name=report_name,
        top_k=top_k,
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"Wrote {result['metadata']['cards_total']} per-question evidence cards.")


@report.command("retrieval-ablation")
@click.option("--boundary-cqs", type=click.Path(path_type=Path), default=None)
@click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
@click.option("--chunks", "chunks_path", type=click.Path(path_type=Path), default=None)
@click.option("--kg-file", "kg_path", type=click.Path(path_type=Path), default=None)
@click.option("--index-dir", type=click.Path(path_type=Path), default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--collection-name", default=None)
@click.option(
    "--graph-method",
    type=click.Choice(["lexical", "traversal"]),
    default="lexical",
    show_default=True,
)
@click.option("--report-name", default="retrieval_ablation", show_default=True)
def report_retrieval_ablation(
    boundary_cqs: Path | None,
    gold_labels: Path | None,
    chunks_path: Path | None,
    kg_path: Path | None,
    index_dir: Path | None,
    output_dir: Path | None,
    collection_name: str | None,
    graph_method: str,
    report_name: str,
) -> None:
    """Compare vector, graph, hybrid, hops, and top-k retrieval settings."""
    config = load_default_config()
    retrieval_config = config.get("retrieval", {})
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_retrieval_ablation(
        boundary_cqs or resolve_project_path("data/cqs/06_phak_ch4_0.boundary.json"),
        chunks_path or resolve_project_path("data/chunks/06_phak_ch4_0.structure_aware.jsonl"),
        kg_path or resolve_project_path("data/kg/06_phak_ch4_0.structure_aware.kg.jsonl"),
        index_dir or resolve_project_path(config["paths"]["index_dir"]) / "chroma",
        report_dir,
        collection_name=collection_name
        or retrieval_config.get("structure_aware_collection_name", "phak_ch4_chunks_structure_aware"),
        gold_labels_path=gold_labels
        or resolve_project_path("data/cqs/06_phak_ch4_0.expanded.gold.json"),
        graph_method=graph_method,
        report_name=report_name,
        command=" ".join(["aviation-ai", *sys.argv[1:]]),
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        f"Evaluated {result['metadata']['scenarios_total']} retrieval ablation scenarios "
        f"for {result['metadata']['questions_total']} CQs."
    )


@report.command("graph-traversal-ablation")
@click.option("--boundary-cqs", type=click.Path(path_type=Path), default=None)
@click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
@click.option("--chunks", "chunks_path", type=click.Path(path_type=Path), default=None)
@click.option("--kg-file", "kg_path", type=click.Path(path_type=Path), default=None)
@click.option("--index-dir", type=click.Path(path_type=Path), default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--collection-name", default=None)
@click.option("--report-name", default="graph_traversal_ablation", show_default=True)
def report_graph_traversal_ablation(
    boundary_cqs: Path | None,
    gold_labels: Path | None,
    chunks_path: Path | None,
    kg_path: Path | None,
    index_dir: Path | None,
    output_dir: Path | None,
    collection_name: str | None,
    report_name: str,
) -> None:
    """Compare lexical KG retrieval with bounded graph traversal variants."""
    config = load_default_config()
    retrieval_config = config.get("retrieval", {})
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_graph_traversal_ablation(
        boundary_cqs or resolve_project_path("data/cqs/06_phak_ch4_0.boundary.json"),
        chunks_path or resolve_project_path("data/chunks/06_phak_ch4_0.structure_aware.jsonl"),
        kg_path or resolve_project_path("data/kg/06_phak_ch4_0.structure_aware.kg.jsonl"),
        index_dir or resolve_project_path(config["paths"]["index_dir"]) / "chroma",
        report_dir,
        collection_name=collection_name
        or retrieval_config.get("structure_aware_collection_name", "phak_ch4_chunks_structure_aware"),
        gold_labels_path=gold_labels
        or resolve_project_path("data/cqs/06_phak_ch4_0.expanded.gold.json"),
        vector_top_k=int(retrieval_config.get("vector_top_k", 5)),
        hybrid_top_k=int(retrieval_config.get("hybrid_top_k", 8)),
        report_name=report_name,
        command=" ".join(["aviation-ai", *sys.argv[1:]]),
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        f"Evaluated {result['metadata']['scenarios_total']} graph traversal scenarios "
        f"for {result['metadata']['questions_total']} CQs."
    )


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
    chunk_inputs = list(chunks_paths) or _default_benchmark_chunks()
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


@report.command("kg-extraction-comparison")
@click.option("--fixed-kg", type=click.Path(path_type=Path), default=None)
@click.option("--structure-aware-kg", type=click.Path(path_type=Path), default=None)
@click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="kg_extraction_comparison", show_default=True)
def report_kg_extraction_comparison(
    fixed_kg: Path | None,
    structure_aware_kg: Path | None,
    gold_labels: Path | None,
    output_dir: Path | None,
    report_name: str,
) -> None:
    """Compare fixed-window and structure-aware KG extraction artifacts."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_kg_extraction_comparison(
        report_dir,
        fixed_kg_path=fixed_kg or resolve_project_path("data/kg/06_phak_ch4_0.kg.jsonl"),
        structure_aware_kg_path=structure_aware_kg
        or resolve_project_path("data/kg/06_phak_ch4_0.structure_aware.kg.jsonl"),
        gold_labels_path=gold_labels
        or resolve_project_path("data/cqs/06_phak_ch4_0.expanded.gold.json"),
        report_name=report_name,
        command=" ".join(["aviation-ai", *sys.argv[1:]]),
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"Compared {len(result['experiments'])} KG extraction artifacts.")


@report.command("answer-eval")
@click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
@click.option("--hybrid-report", type=click.Path(path_type=Path), default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="answer_evaluation", show_default=True)
def report_answer_eval(
    gold_labels: Path | None,
    hybrid_report: Path | None,
    output_dir: Path | None,
    report_name: str,
) -> None:
    """Evaluate answer citations, abstention, relevance, and advisory boundary behavior."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_answer_evaluation(
        report_dir,
        gold_labels_path=gold_labels
        or resolve_project_path("data/cqs/06_phak_ch4_0.gold.json"),
        hybrid_report_path=hybrid_report or report_dir / "hybrid_rag_structure_aware.json",
        report_name=report_name,
        command=" ".join(["aviation-ai", *sys.argv[1:]]),
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"Evaluated {result['metadata']['answers_total']} answers.")


@report.command("robustness")
@click.option("--robustness-cases", type=click.Path(path_type=Path), default=None)
@click.option("--chunks", "chunks_path", type=click.Path(path_type=Path), default=None)
@click.option("--kg-file", "kg_path", type=click.Path(path_type=Path), default=None)
@click.option("--index-dir", type=click.Path(path_type=Path), default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--collection-name", default=None)
@click.option("--report-name", default="robustness_evaluation", show_default=True)
def report_robustness(
    robustness_cases: Path | None,
    chunks_path: Path | None,
    kg_path: Path | None,
    index_dir: Path | None,
    output_dir: Path | None,
    collection_name: str | None,
    report_name: str,
) -> None:
    """Evaluate paraphrase, terminology, ambiguity, cross-page, and unsupported cases."""
    config = load_default_config()
    retrieval_config = config.get("retrieval", {})
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_robustness_evaluation(
        robustness_cases or resolve_project_path("data/cqs/06_phak_ch4_0.robustness.json"),
        chunks_path or resolve_project_path("data/chunks/06_phak_ch4_0.structure_aware.jsonl"),
        kg_path or resolve_project_path("data/kg/06_phak_ch4_0.structure_aware.kg.jsonl"),
        index_dir or resolve_project_path(config["paths"]["index_dir"]) / "chroma",
        report_dir,
        collection_name=collection_name
        or retrieval_config.get("structure_aware_collection_name", "phak_ch4_chunks_structure_aware"),
        report_name=report_name,
        command=" ".join(["aviation-ai", *sys.argv[1:]]),
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"Evaluated {result['metadata']['cases_total']} robustness cases.")


@report.command("final-evaluation")
@click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
@click.option("--chunking-comparison", type=click.Path(path_type=Path), default=None)
@click.option("--fixed-hybrid", type=click.Path(path_type=Path), default=None)
@click.option("--structure-aware-hybrid", type=click.Path(path_type=Path), default=None)
@click.option("--evidence-eval", type=click.Path(path_type=Path), default=None)
@click.option("--graphrag-review", type=click.Path(path_type=Path), default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="final_evaluation_review", show_default=True)
def report_final_evaluation(
    gold_labels: Path | None,
    chunking_comparison: Path | None,
    fixed_hybrid: Path | None,
    structure_aware_hybrid: Path | None,
    evidence_eval: Path | None,
    graphrag_review: Path | None,
    output_dir: Path | None,
    report_name: str,
) -> None:
    """Write final layered evaluation and submission-readiness review."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_final_evaluation_review(
        report_dir,
        gold_labels_path=gold_labels
        or resolve_project_path("data/cqs/06_phak_ch4_0.gold.json"),
        chunking_comparison_path=chunking_comparison or report_dir / "chunking_comparison.json",
        fixed_hybrid_path=fixed_hybrid or report_dir / "hybrid_rag_experiment.json",
        structure_aware_hybrid_path=structure_aware_hybrid
        or report_dir / "hybrid_rag_structure_aware.json",
        evidence_eval_path=evidence_eval or report_dir / "evidence_level_evaluation.json",
        graphrag_review_path=graphrag_review or report_dir / "graphrag_review.json",
        report_name=report_name,
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        "Final evaluation review complete; recommended default strategy: "
        f"{result['default_strategy_decision']['recommended_default']}."
    )


@report.command("web-demo-readiness")
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="web_demo_readiness", show_default=True)
def report_web_demo_readiness(output_dir: Path | None, report_name: str) -> None:
    """Write offline-first web demo readiness reports."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_web_demo_readiness(
        report_dir,
        report_name=report_name,
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        "Web demo readiness: "
        f"{result['ready']}; default strategy: {result['selected_default_strategy']}."
    )


@report.command("web-demo-smoke")
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="web_demo_final_smoke", show_default=True)
def report_web_demo_smoke(output_dir: Path | None, report_name: str) -> None:
    """Run offline FastAPI web demo smoke checks and write evidence reports."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_web_demo_smoke(
        report_dir,
        report_name=report_name,
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"Web demo final smoke: {result['ready']}.")


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
