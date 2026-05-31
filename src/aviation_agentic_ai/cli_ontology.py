from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.cli_common import default_ontology_path
from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.ontology.cq import CQValidationError, generate_cqs, load_cq_artifact
from aviation_agentic_ai.ontology.evaluation import evaluate_ontology
from aviation_agentic_ai.ontology.generation import generate_ontology
from aviation_agentic_ai.ontology.reporting import write_stats_json, write_stats_markdown
from aviation_agentic_ai.ontology.source_scope import write_source_scope_reports
from aviation_agentic_ai.ontology.stats import collect_stats, load_graph
from aviation_agentic_ai.paths import project_relative_path


def _ontology_generation_config() -> dict:
    from aviation_agentic_ai.config import load_yaml

    return load_yaml("configs/ontology_generation.yaml")


@click.group()
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
    path = ontology_file or default_ontology_path()
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
    path = ontology_file or default_ontology_path()
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
        path = default_ontology_path()
    cqs = cq_file or resolve_project_path(generation_config["cq_output"])
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    output_name = report_name or (
        "generated_ontology_evaluation" if generated else "ontology_evaluation"
    )
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
        max_pages=max_pages if max_pages is not None else (config.get("max_pages") or None),
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
