from __future__ import annotations

import sys
from pathlib import Path

import click

from aviation_agentic_ai.cli_chunk import chunk_group
from aviation_agentic_ai.cli_cqs import cqs
from aviation_agentic_ai.cli_index import index
from aviation_agentic_ai.cli_kg import kg
from aviation_agentic_ai.cli_ontology import ontology
from aviation_agentic_ai.cli_query import query
from aviation_agentic_ai.cli_report_benchmark import register_benchmark_report_commands
from aviation_agentic_ai.cli_report_chunking import register_chunking_report_commands
from aviation_agentic_ai.cli_report_llm import register_llm_report_commands
from aviation_agentic_ai.cli_report_stage import register_stage_report_commands
from aviation_agentic_ai.cli_report_thesis import register_thesis_report_commands
from aviation_agentic_ai.cli_report_web import register_web_report_commands
from aviation_agentic_ai.cli_web import web
from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.answer_eval import write_answer_evaluation
from aviation_agentic_ai.reporting.evidence_cards import write_evidence_cards
from aviation_agentic_ai.reporting.evidence_eval import write_evidence_level_evaluation
from aviation_agentic_ai.reporting.final_evaluation import write_final_evaluation_review
from aviation_agentic_ai.reporting.graphrag_review import write_graphrag_review
from aviation_agentic_ai.reporting.graph_traversal_ablation import (
    write_graph_traversal_ablation,
)
from aviation_agentic_ai.reporting.hybrid_rag import write_hybrid_rag_experiment
from aviation_agentic_ai.reporting.kg_extraction_comparison import (
    write_kg_extraction_comparison,
)
from aviation_agentic_ai.reporting.retrieval_ablation import write_retrieval_ablation
from aviation_agentic_ai.reporting.robustness import write_robustness_evaluation
from aviation_agentic_ai.reporting.sufficiency_eval import write_sufficiency_evaluation
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


register_stage_report_commands(report)
register_thesis_report_commands(report)


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


register_benchmark_report_commands(report)
register_llm_report_commands(report)


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
