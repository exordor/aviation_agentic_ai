from __future__ import annotations

import sys
from pathlib import Path

import click

from aviation_agentic_ai.cli_chunk import chunk_group
from aviation_agentic_ai.cli_common import default_benchmark_chunks as _default_benchmark_chunks
from aviation_agentic_ai.cli_cqs import cqs
from aviation_agentic_ai.cli_index import index
from aviation_agentic_ai.cli_kg import kg
from aviation_agentic_ai.cli_ontology import ontology
from aviation_agentic_ai.cli_query import query
from aviation_agentic_ai.cli_report_chunking import register_chunking_report_commands
from aviation_agentic_ai.cli_report_web import register_web_report_commands
from aviation_agentic_ai.cli_web import web
from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.academic_outputs import (
    write_academic_report,
    write_defense_deck_outline,
    write_defense_notes,
    write_visual_assets,
)
from aviation_agentic_ai.reporting.answer_eval import write_answer_evaluation
from aviation_agentic_ai.reporting.benchmark_review_pack import (
    write_answer_eval_subset,
    write_benchmark_review_pack,
    write_benchmark_reviewed_subset,
)
from aviation_agentic_ai.reporting.benchmark_v2 import write_benchmark_v2_summary
from aviation_agentic_ai.reporting.evidence_cards import write_evidence_cards
from aviation_agentic_ai.reporting.evidence_eval import write_evidence_level_evaluation
from aviation_agentic_ai.reporting.evaluation_protocol import write_evaluation_protocol_review
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
from aviation_agentic_ai.reporting.llm_review_reports import (
    write_answer_generation_benchmark_subset,
    write_answer_llm_judge,
    write_benchmark_llm_review,
    write_benchmark_llm_rewrite_proposals,
    write_graph_path_llm_review,
    write_llm_review_consistency,
    write_triple_semantic_llm_review,
)
from aviation_agentic_ai.reporting.overnight import write_overnight_summary
from aviation_agentic_ai.reporting.project_report import write_project_report
from aviation_agentic_ai.reporting.reviews import write_review_progress
from aviation_agentic_ai.reporting.retrieval_ablation import write_retrieval_ablation
from aviation_agentic_ai.reporting.robustness import write_robustness_evaluation
from aviation_agentic_ai.reporting.sufficiency_eval import write_sufficiency_evaluation
from aviation_agentic_ai.reporting.thesis_dashboard import write_thesis_experiment_dashboard
from aviation_agentic_ai.reporting.thesis_claims import write_thesis_claims_review
from aviation_agentic_ai.reporting.triple_semantic_review import write_triple_semantic_review
from aviation_agentic_ai.retrieval.indexing import DEFAULT_COLLECTION_NAME


@click.group()
def main() -> None:
    """Aviation Agentic AI CLI."""


main.add_command(web)
main.add_command(chunk_group)
main.add_command(index)
main.add_command(query)
main.add_command(kg)
main.add_command(cqs)
main.add_command(ontology)


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


@report.command("thesis-claims")
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for thesis claim review outputs.",
)
@click.option(
    "--scan-path",
    "scan_paths",
    type=click.Path(path_type=Path),
    multiple=True,
    help="Markdown file to scan for unsafe thesis claims. Can be passed more than once.",
)
@click.option("--report-name", default="thesis_claims_review", show_default=True)
def report_thesis_claims(
    output_dir: Path | None,
    scan_paths: tuple[Path, ...],
    report_name: str,
) -> None:
    """Review thesis claims, evidence support, and unsafe wording."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    configured_scan_paths = list(scan_paths) if scan_paths else None
    json_path, md_path, result = write_thesis_claims_review(
        report_dir,
        scan_paths=configured_scan_paths,
        report_name=report_name,
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        f"Reviewed thesis claims; unsafe claims found: "
        f"{result['metadata']['unsafe_claims_total']}."
    )


@report.command("evaluation-protocol")
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="evaluation_protocol_review", show_default=True)
def report_evaluation_protocol(output_dir: Path | None, report_name: str) -> None:
    """Summarize layered mainstream RAG/GraphRAG/KG evaluation coverage."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_evaluation_protocol_review(
        report_dir,
        report_name=report_name,
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        "Reviewed evaluation protocol metrics; pending gaps: "
        f"{len(result['missing_or_pending_metrics'])}."
    )


@report.command("thesis-experiment-dashboard")
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="thesis_experiment_dashboard", show_default=True)
def report_thesis_experiment_dashboard(
    output_dir: Path | None,
    report_name: str,
) -> None:
    """Aggregate thesis experiment reports into an RQ-oriented dashboard."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_thesis_experiment_dashboard(
        report_dir,
        report_name=report_name,
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        "Built thesis experiment dashboard; consistency checks passed="
        f"{result['consistency_checks']['all_passed']}."
    )


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
@click.option(
    "--graph-fusion-policy",
    type=click.Choice(["rrf", "vector_first_guarded"]),
    default=None,
    help="Limit scenarios to a specific graph fusion policy.",
)
@click.option("--report-name", default="graph_traversal_ablation", show_default=True)
def report_graph_traversal_ablation(
    boundary_cqs: Path | None,
    gold_labels: Path | None,
    chunks_path: Path | None,
    kg_path: Path | None,
    index_dir: Path | None,
    output_dir: Path | None,
    collection_name: str | None,
    graph_fusion_policy: str | None,
    report_name: str,
) -> None:
    """Compare lexical KG retrieval with bounded graph traversal variants."""
    config = load_default_config()
    retrieval_config = config.get("retrieval", {})
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    scenarios = None
    if graph_fusion_policy is not None:
        from aviation_agentic_ai.reporting.graph_traversal_ablation import (
            DEFAULT_GRAPH_TRAVERSAL_SCENARIOS,
        )

        scenarios = tuple(
            scenario
            for scenario in DEFAULT_GRAPH_TRAVERSAL_SCENARIOS
            if scenario.get("graph_fusion_policy", "rrf") == graph_fusion_policy
        )
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
        **({"scenarios": scenarios} if scenarios is not None else {}),
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


@report.command("benchmark-llm-review")
@click.option(
    "--gold-labels",
    type=click.Path(path_type=Path),
    default=None,
    help="Benchmark v2 gold label JSON file.",
)
@click.option(
    "--subset-labels",
    type=click.Path(path_type=Path),
    default=None,
    help="Optional subset labels for bounded LLM review.",
)
@click.option("--max-items", type=int, default=60, show_default=True)
@click.option("--run-llm/--no-run-llm", default=True, show_default=True)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="benchmark_llm_review", show_default=True)
def report_benchmark_llm_review(
    gold_labels: Path | None,
    subset_labels: Path | None,
    max_items: int,
    run_llm: bool,
    output_dir: Path | None,
    report_name: str,
) -> None:
    """Run model-based benchmark label review without claiming human certification."""
    config = load_default_config()
    label_path = gold_labels or resolve_project_path(
        "data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"
    )
    default_subset = resolve_project_path(
        "data/cqs/06_phak_ch4_0.benchmark_v2.reviewed_subset.gold.json"
    )
    subset_path = subset_labels or (default_subset if default_subset.exists() else None)
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_benchmark_llm_review(
        label_path,
        report_dir,
        subset_labels_path=subset_path,
        max_items=max_items,
        run_llm=run_llm,
        report_name=report_name,
        command=" ".join(["aviation-ai", *sys.argv[1:]]),
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        "Benchmark LLM review records="
        f"{result['summary']['items_total']}; reviewed="
        f"{result['summary']['llm_reviewed_total']}."
    )


@report.command("benchmark-llm-rewrite-proposals")
@click.option("--review-report", type=click.Path(path_type=Path), default=None)
@click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="benchmark_llm_rewrite_proposals", show_default=True)
@click.option("--write-candidate/--no-write-candidate", default=False, show_default=True)
@click.option("--candidate-output", type=click.Path(path_type=Path), default=None)
def report_benchmark_llm_rewrite_proposals(
    review_report: Path | None,
    gold_labels: Path | None,
    output_dir: Path | None,
    report_name: str,
    write_candidate: bool,
    candidate_output: Path | None,
) -> None:
    """Create proposal-only benchmark rewrites from model-based review output."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    review_path = review_report or report_dir / "benchmark_llm_review.json"
    label_path = gold_labels or resolve_project_path(
        "data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"
    )
    json_path, md_path, candidate_path, result = write_benchmark_llm_rewrite_proposals(
        review_path,
        report_dir,
        source_gold_path=label_path,
        write_candidate=write_candidate,
        candidate_output_path=candidate_output,
        report_name=report_name,
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    if candidate_path is not None:
        click.echo(f"Wrote {project_relative_path(candidate_path)}")
    click.echo(f"Prepared {result['metadata']['proposals_total']} rewrite proposals.")


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


@report.command("sufficiency-eval")
@click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
@click.option("--retrieval-report", type=click.Path(path_type=Path), default=None)
@click.option("--scenario-name", default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="sufficiency_evaluation", show_default=True)
def report_sufficiency_eval(
    gold_labels: Path | None,
    retrieval_report: Path | None,
    scenario_name: str | None,
    output_dir: Path | None,
    report_name: str,
) -> None:
    """Evaluate deterministic evidence sufficiency and abstention behavior."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    default_report = report_dir / "retrieval_ablation_benchmark_v2.json"
    json_path, md_path, result = write_sufficiency_evaluation(
        gold_labels or resolve_project_path("data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"),
        retrieval_report or default_report,
        report_dir,
        scenario_name=scenario_name,
        report_name=report_name,
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        "Sufficiency evaluation complete; insufficient-evidence abstention accuracy="
        f"{result['metrics']['insufficient_evidence_abstention_accuracy']}."
    )


@report.command("triple-semantic-review")
@click.option("--kg-file", "kg_path", type=click.Path(path_type=Path), default=None)
@click.option("--sample-size", type=int, default=100, show_default=True)
@click.option(
    "--annotations",
    "annotations_path",
    type=click.Path(path_type=Path),
    default=None,
    help="Optional existing review JSON with manual annotations to merge.",
)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
def report_triple_semantic_review(
    kg_path: Path | None,
    sample_size: int,
    annotations_path: Path | None,
    output_dir: Path | None,
) -> None:
    """Prepare a KG triple semantic review sample with empty manual annotations."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_triple_semantic_review(
        kg_path or resolve_project_path("data/kg/06_phak_ch4_0.structure_aware.kg.jsonl"),
        report_dir,
        sample_size=sample_size,
        annotations_path=annotations_path,
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"Prepared {result['metadata']['sample_size']} triples for semantic review.")


@report.command("triple-semantic-llm-review")
@click.option("--review-sample", type=click.Path(path_type=Path), default=None)
@click.option("--max-items", type=int, default=50, show_default=True)
@click.option("--run-llm/--no-run-llm", default=True, show_default=True)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="triple_semantic_llm_review", show_default=True)
def report_triple_semantic_llm_review(
    review_sample: Path | None,
    max_items: int,
    run_llm: bool,
    output_dir: Path | None,
    report_name: str,
) -> None:
    """Run model-based KG triple semantic review without expert certification."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    sample_path = review_sample or report_dir / "triple_semantic_review_sample.json"
    json_path, md_path, result = write_triple_semantic_llm_review(
        sample_path,
        report_dir,
        max_items=max_items,
        run_llm=run_llm,
        report_name=report_name,
        command=" ".join(["aviation-ai", *sys.argv[1:]]),
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        "Triple LLM review records="
        f"{result['summary']['items_total']}; reviewed="
        f"{result['summary']['llm_reviewed_total']}."
    )


@report.command("graph-path-llm-review")
@click.option("--graph-report", type=click.Path(path_type=Path), default=None)
@click.option("--max-items", type=int, default=50, show_default=True)
@click.option("--run-llm/--no-run-llm", default=True, show_default=True)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="graph_path_llm_review", show_default=True)
def report_graph_path_llm_review(
    graph_report: Path | None,
    max_items: int,
    run_llm: bool,
    output_dir: Path | None,
    report_name: str,
) -> None:
    """Run model-based graph path relevance review without treating it as final truth."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    source = graph_report or report_dir / "graph_traversal_ablation_benchmark_v2.json"
    json_path, md_path, result = write_graph_path_llm_review(
        source,
        report_dir,
        max_items=max_items,
        run_llm=run_llm,
        report_name=report_name,
        command=" ".join(["aviation-ai", *sys.argv[1:]]),
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        "Graph path LLM review records="
        f"{result['summary']['items_total']}; reviewed="
        f"{result['summary']['llm_reviewed_total']}."
    )


@report.command("answer-generation-benchmark-subset")
@click.option("--gold-labels", type=click.Path(path_type=Path), default=None)
@click.option("--chunks", "chunks_path", type=click.Path(path_type=Path), default=None)
@click.option("--kg-file", "kg_path", type=click.Path(path_type=Path), default=None)
@click.option("--index-dir", type=click.Path(path_type=Path), default=None)
@click.option("--collection-name", default=DEFAULT_COLLECTION_NAME, show_default=True)
@click.option("--max-questions", type=int, default=45, show_default=True)
@click.option("--run-llm/--no-run-llm", default=True, show_default=True)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="answer_generation_benchmark_subset", show_default=True)
def report_answer_generation_benchmark_subset(
    gold_labels: Path | None,
    chunks_path: Path | None,
    kg_path: Path | None,
    index_dir: Path | None,
    collection_name: str,
    max_questions: int,
    run_llm: bool,
    output_dir: Path | None,
    report_name: str,
) -> None:
    """Generate benchmark-subset answers for later model-based judging."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    label_path = gold_labels or resolve_project_path(
        "data/cqs/06_phak_ch4_0.answer_eval_subset.gold.json"
    )
    if not label_path.exists():
        label_path, _subset = write_answer_eval_subset(
            resolve_project_path("data/cqs/06_phak_ch4_0.benchmark_v2.gold.json"),
            label_path,
        )
    json_path, md_path, result = write_answer_generation_benchmark_subset(
        label_path,
        chunks_path or resolve_project_path("data/chunks/06_phak_ch4_0.structure_aware.jsonl"),
        kg_path or resolve_project_path("data/kg/06_phak_ch4_0.structure_aware.kg.jsonl"),
        index_dir or resolve_project_path(config["paths"]["index_dir"]) / "chroma",
        report_dir,
        collection_name=collection_name,
        max_questions=max_questions,
        run_llm=run_llm,
        report_name=report_name,
        command=" ".join(["aviation-ai", *sys.argv[1:]]),
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(f"Generated {result['metadata']['answers_total']} benchmark-subset answers.")


@report.command("answer-llm-judge")
@click.option("--answer-report", type=click.Path(path_type=Path), default=None)
@click.option("--max-items", type=int, default=60, show_default=True)
@click.option("--run-llm/--no-run-llm", default=True, show_default=True)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="answer_llm_judge", show_default=True)
def report_answer_llm_judge(
    answer_report: Path | None,
    max_items: int,
    run_llm: bool,
    output_dir: Path | None,
    report_name: str,
) -> None:
    """Judge generated answers with a model-based rubric."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    source = answer_report or report_dir / "answer_generation_benchmark_subset.json"
    json_path, md_path, result = write_answer_llm_judge(
        source,
        report_dir,
        max_items=max_items,
        run_llm=run_llm,
        report_name=report_name,
        command=" ".join(["aviation-ai", *sys.argv[1:]]),
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        "Answer LLM judge records="
        f"{result['summary']['items_total']}; reviewed="
        f"{result['summary']['llm_reviewed_total']}."
    )


@report.command("llm-review-consistency")
@click.option("--benchmark-review", type=click.Path(path_type=Path), default=None)
@click.option("--triple-review", type=click.Path(path_type=Path), default=None)
@click.option("--graph-path-review", type=click.Path(path_type=Path), default=None)
@click.option("--answer-judge", type=click.Path(path_type=Path), default=None)
@click.option("--output-dir", type=click.Path(path_type=Path), default=None)
@click.option("--report-name", default="llm_review_consistency", show_default=True)
def report_llm_review_consistency(
    benchmark_review: Path | None,
    triple_review: Path | None,
    graph_path_review: Path | None,
    answer_judge: Path | None,
    output_dir: Path | None,
    report_name: str,
) -> None:
    """Compare role-based LLM review decisions across review artifacts."""
    config = load_default_config()
    report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
    json_path, md_path, result = write_llm_review_consistency(
        report_dir,
        benchmark_review_path=benchmark_review or report_dir / "benchmark_llm_review.json",
        triple_review_path=triple_review or report_dir / "triple_semantic_llm_review.json",
        graph_path_review_path=graph_path_review or report_dir / "graph_path_llm_review.json",
        answer_judge_path=answer_judge or report_dir / "answer_llm_judge.json",
        report_name=report_name,
    )
    click.echo(f"Wrote {project_relative_path(json_path)}")
    click.echo(f"Wrote {project_relative_path(md_path)}")
    click.echo(
        "LLM review consistency measured="
        f"{not result['summary']['consistency_not_measured']}."
    )


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


register_web_report_commands(report)
register_chunking_report_commands(report)
