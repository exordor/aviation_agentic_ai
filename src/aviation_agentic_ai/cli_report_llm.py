from __future__ import annotations

import sys
from pathlib import Path

import click

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.benchmark_review_pack import write_answer_eval_subset
from aviation_agentic_ai.reporting.llm_review_reports import (
    write_answer_generation_benchmark_subset,
    write_answer_llm_judge,
    write_benchmark_llm_review,
    write_benchmark_llm_rewrite_proposals,
    write_graph_path_llm_review,
    write_llm_review_consistency,
    write_triple_semantic_llm_review,
)
from aviation_agentic_ai.retrieval.indexing import DEFAULT_COLLECTION_NAME


def register_llm_report_commands(report: click.Group) -> None:
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
