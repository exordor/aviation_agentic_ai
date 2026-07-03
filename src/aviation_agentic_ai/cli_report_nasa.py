from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.atmonto.agentic_loop.loop import (
    write_nasa_atmonto_agentic_loop,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.l1_batch_experiment import (
    DEFAULT_SAMPLE_SIZE,
    write_nasa_atmonto_l1_agent_batch_experiment,
)
from aviation_agentic_ai.reporting.atmonto.core.answer_generation import (
    write_nasa_atmonto_answer_generation,
)
from aviation_agentic_ai.reporting.atmonto.core.cq import write_nasa_atmonto_cq_evaluation
from aviation_agentic_ai.reporting.atmonto.core.cq_queries import (
    write_nasa_atmonto_cq_query_evaluation,
)


def register_nasa_report_commands(report: click.Group) -> None:

    @report.command("nasa-atmonto-cq-evaluation")
    @click.option(
        "--gold-file",
        type=click.Path(path_type=Path),
        default=None,
        help="Reviewed ATCSCC gold JSONL file.",
    )
    @click.option(
        "--scoring-file",
        type=click.Path(path_type=Path),
        default=None,
        help="Formal experiment scoring JSON report.",
    )
    @click.option(
        "--semantic-groups-file",
        type=click.Path(path_type=Path),
        default=None,
        help="Gold semantic groups JSON report.",
    )
    @click.option(
        "--rejection-file",
        type=click.Path(path_type=Path),
        default=None,
        help="Rejection adjudication JSON report.",
    )
    @click.option(
        "--output-dir",
        type=click.Path(path_type=Path),
        default=None,
        help="Directory for CQ evaluation report outputs.",
    )
    @click.option(
        "--report-name",
        default="nasa_atmonto_cq_evaluation",
        show_default=True,
        help="Output report stem.",
    )
    def report_nasa_atmonto_cq_evaluation(
        gold_file: Path | None,
        scoring_file: Path | None,
        semantic_groups_file: Path | None,
        rejection_file: Path | None,
        output_dir: Path | None,
        report_name: str,
    ) -> None:
        """Build NASA ATMONTO competency-question evaluation reports."""
        try:
            config = load_default_config()
            report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
            report_kwargs = {
                "output_dir": report_dir,
                "report_name": report_name,
            }
            if gold_file is not None:
                report_kwargs["gold_path"] = gold_file
            if scoring_file is not None:
                report_kwargs["scoring_path"] = scoring_file
            if semantic_groups_file is not None:
                report_kwargs["semantic_groups_path"] = semantic_groups_file
            if rejection_file is not None:
                report_kwargs["rejection_adjudication_path"] = rejection_file
            json_path, md_path, result = write_nasa_atmonto_cq_evaluation(**report_kwargs)
            click.echo(f"Wrote {project_relative_path(json_path)}")
            click.echo(f"Wrote {project_relative_path(md_path)}")
            click.echo(
                f"Mapped {result['metadata']['cq_count']} CQs against "
                f"{result['gold_summary']['reviewed_records']} reviewed ATCSCC gold records."
            )
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

    @report.command("nasa-atmonto-cq-query-evaluation")
    @click.option(
        "--gold-file",
        type=click.Path(path_type=Path),
        default=None,
        help="Reviewed ATCSCC gold JSONL file.",
    )
    @click.option(
        "--manifest-path",
        type=click.Path(path_type=Path),
        default=None,
        help="Output path for the CQ query manifest.",
    )
    @click.option(
        "--output-dir",
        type=click.Path(path_type=Path),
        default=None,
        help="Directory for CQ query evaluation report outputs.",
    )
    @click.option(
        "--report-name",
        default="nasa_atmonto_cq_query_evaluation",
        show_default=True,
        help="Output report stem.",
    )
    def report_nasa_atmonto_cq_query_evaluation(
        gold_file: Path | None,
        manifest_path: Path | None,
        output_dir: Path | None,
        report_name: str,
    ) -> None:
        """Materialize ATCSCC CQ query templates and deterministic answer-quality scoring."""
        try:
            config = load_default_config()
            report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
            report_kwargs = {
                "output_dir": report_dir,
                "report_name": report_name,
            }
            if gold_file is not None:
                report_kwargs["gold_path"] = gold_file
            if manifest_path is not None:
                report_kwargs["manifest_path"] = manifest_path
            json_path, md_path, manifest_json, manifest_md, result = (
                write_nasa_atmonto_cq_query_evaluation(**report_kwargs)
            )
            click.echo(f"Wrote {project_relative_path(json_path)}")
            click.echo(f"Wrote {project_relative_path(md_path)}")
            click.echo(f"Wrote {project_relative_path(manifest_json)}")
            click.echo(f"Wrote {project_relative_path(manifest_md)}")
            click.echo(
                f"Evaluated {result['metadata']['template_count']} CQ query templates "
                f"against {result['metadata']['system_count']} systems."
            )
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

    @report.command("nasa-atmonto-answer-generation")
    @click.option(
        "--gold-file",
        type=click.Path(path_type=Path),
        default=None,
        help="Reviewed ATCSCC gold JSONL file.",
    )
    @click.option(
        "--s4-predictions",
        type=click.Path(path_type=Path),
        default=None,
        help="S4 hybrid prediction JSONL file.",
    )
    @click.option(
        "--query-manifest",
        type=click.Path(path_type=Path),
        default=None,
        help="ATCSCC CQ query manifest JSON.",
    )
    @click.option(
        "--benchmark-path",
        type=click.Path(path_type=Path),
        default=None,
        help="Output path for the ATCSCC answer-eval benchmark.",
    )
    @click.option(
        "--chapter-path",
        type=click.Path(path_type=Path),
        default=None,
        help="Output path for the scoped answer-generation chapter section.",
    )
    @click.option(
        "--output-dir",
        type=click.Path(path_type=Path),
        default=None,
        help="Directory for answer-generation report outputs.",
    )
    @click.option(
        "--report-name",
        default="nasa_atmonto_answer_generation",
        show_default=True,
        help="Output report stem.",
    )
    @click.option("--max-cases-per-template", default=3, show_default=True, type=int)
    def report_nasa_atmonto_answer_generation(
        gold_file: Path | None,
        s4_predictions: Path | None,
        query_manifest: Path | None,
        benchmark_path: Path | None,
        chapter_path: Path | None,
        output_dir: Path | None,
        report_name: str,
        max_cases_per_template: int,
    ) -> None:
        """Generate ATCSCC answer-eval benchmark and deterministic GraphRAG answers."""
        try:
            config = load_default_config()
            report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
            report_kwargs = {
                "output_dir": report_dir,
                "report_name": report_name,
                "max_cases_per_template": max_cases_per_template,
            }
            if gold_file is not None:
                report_kwargs["gold_path"] = gold_file
            if s4_predictions is not None:
                report_kwargs["s4_prediction_path"] = s4_predictions
            if query_manifest is not None:
                report_kwargs["query_manifest_path"] = query_manifest
            if benchmark_path is not None:
                report_kwargs["benchmark_path"] = benchmark_path
            if chapter_path is not None:
                report_kwargs["chapter_path"] = chapter_path
            json_path, md_path, benchmark_json, chapter_md, result = (
                write_nasa_atmonto_answer_generation(**report_kwargs)
            )
            click.echo(f"Wrote {project_relative_path(json_path)}")
            click.echo(f"Wrote {project_relative_path(md_path)}")
            click.echo(f"Wrote {project_relative_path(benchmark_json)}")
            click.echo(f"Wrote {project_relative_path(chapter_md)}")
            click.echo(
                f"Generated {result['metadata']['benchmark_label_count']} "
                "ATCSCC answer-eval labels; "
                f"critic-gate rejected {result['critic_gate']['rejected_fact_count']} S4 facts."
            )
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

    @report.command("nasa-atmonto-agentic-loop")
    @click.option(
        "--gold-file",
        type=click.Path(path_type=Path),
        default=None,
        help="Reviewed ATCSCC gold JSONL file.",
    )
    @click.option(
        "--scoring-file",
        type=click.Path(path_type=Path),
        default=None,
        help="Formal experiment scoring JSON report.",
    )
    @click.option(
        "--semantic-groups-file",
        type=click.Path(path_type=Path),
        default=None,
        help="Gold semantic groups JSON report.",
    )
    @click.option(
        "--rejection-file",
        type=click.Path(path_type=Path),
        default=None,
        help="Rejection adjudication JSON report.",
    )
    @click.option(
        "--cq-manifest",
        type=click.Path(path_type=Path),
        default=None,
        help="ATCSCC CQ query manifest.",
    )
    @click.option(
        "--prediction-validation-file",
        type=click.Path(path_type=Path),
        default=None,
        help="Prediction output validation JSON report.",
    )
    @click.option(
        "--extraction-schema",
        type=click.Path(path_type=Path),
        default=None,
        help="ATCSCC extraction JSON schema.",
    )
    @click.option(
        "--output-dir",
        type=click.Path(path_type=Path),
        default=None,
        help="Directory for agentic loop report outputs.",
    )
    @click.option(
        "--report-name",
        default="nasa_atmonto_agentic_loop",
        show_default=True,
        help="Output report stem.",
    )
    def report_nasa_atmonto_agentic_loop(
        gold_file: Path | None,
        scoring_file: Path | None,
        semantic_groups_file: Path | None,
        rejection_file: Path | None,
        cq_manifest: Path | None,
        prediction_validation_file: Path | None,
        extraction_schema: Path | None,
        output_dir: Path | None,
        report_name: str,
    ) -> None:
        """Build the ATCSCC/ATMONTO agentic extraction-validation loop reports."""
        try:
            config = load_default_config()
            report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
            report_kwargs = {
                "output_dir": report_dir,
                "report_name": report_name,
            }
            if gold_file is not None:
                report_kwargs["gold_path"] = gold_file
            if scoring_file is not None:
                report_kwargs["scoring_path"] = scoring_file
            if semantic_groups_file is not None:
                report_kwargs["semantic_groups_path"] = semantic_groups_file
            if rejection_file is not None:
                report_kwargs["rejection_adjudication_path"] = rejection_file
            if cq_manifest is not None:
                report_kwargs["cq_manifest_path"] = cq_manifest
            if prediction_validation_file is not None:
                report_kwargs["prediction_validation_path"] = prediction_validation_file
            if extraction_schema is not None:
                report_kwargs["extraction_schema_path"] = extraction_schema
            json_path, md_path, result = write_nasa_atmonto_agentic_loop(**report_kwargs)
            click.echo(f"Wrote {project_relative_path(json_path)}")
            click.echo(f"Wrote {project_relative_path(md_path)}")
            click.echo(
                f"Agentic loop status: {result['status']} with "
                f"{len(result['code_review_triggers'])} code-review trigger(s)."
            )
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

    @report.command("nasa-atmonto-l1-agent-batch")
    @click.option(
        "--input-records",
        type=click.Path(path_type=Path),
        default=None,
        help="ATCSCC formal input records JSONL.",
    )
    @click.option(
        "--baseline-predictions",
        type=click.Path(path_type=Path),
        default=None,
        help="Baseline prediction JSONL used for the first extractor pass.",
    )
    @click.option(
        "--repair-predictions",
        type=click.Path(path_type=Path),
        default=None,
        help="Repair artifact prediction JSONL replayed in the second extractor pass.",
    )
    @click.option(
        "--schema-slice",
        type=click.Path(path_type=Path),
        default=None,
        help="ATCSCC schema slice JSON.",
    )
    @click.option(
        "--cq-manifest",
        type=click.Path(path_type=Path),
        default=None,
        help="ATCSCC CQ route manifest.",
    )
    @click.option(
        "--prediction-output",
        type=click.Path(path_type=Path),
        default=None,
        help="Output JSONL for L1 batch prediction records.",
    )
    @click.option(
        "--run-metadata-output",
        type=click.Path(path_type=Path),
        default=None,
        help="Output JSON for L1 batch run metadata.",
    )
    @click.option(
        "--sample-size",
        type=int,
        default=DEFAULT_SAMPLE_SIZE,
        show_default=True,
        help="Maximum matched ATCSCC records to run.",
    )
    @click.option(
        "--max-iterations",
        type=int,
        default=2,
        show_default=True,
        help="L1 repair-loop iteration budget.",
    )
    @click.option(
        "--output-dir",
        type=click.Path(path_type=Path),
        default=None,
        help="Directory for L1 batch report outputs.",
    )
    @click.option(
        "--report-name",
        default="nasa_atmonto_l1_agent_batch_experiment",
        show_default=True,
        help="Output report stem.",
    )
    def report_nasa_atmonto_l1_agent_batch(
        input_records: Path | None,
        baseline_predictions: Path | None,
        repair_predictions: Path | None,
        schema_slice: Path | None,
        cq_manifest: Path | None,
        prediction_output: Path | None,
        run_metadata_output: Path | None,
        sample_size: int,
        max_iterations: int,
        output_dir: Path | None,
        report_name: str,
    ) -> None:
        """Run the small-batch L1 ATCSCC Agent-loop before/after experiment."""
        try:
            config = load_default_config()
            report_dir = output_dir or resolve_project_path(config["paths"]["stage_report_dir"])
            report_kwargs = {
                "output_dir": report_dir,
                "report_name": report_name,
                "sample_size": sample_size,
                "max_iterations": max_iterations,
            }
            if input_records is not None:
                report_kwargs["input_records_path"] = input_records
            if baseline_predictions is not None:
                report_kwargs["baseline_predictions_path"] = baseline_predictions
            if repair_predictions is not None:
                report_kwargs["repair_predictions_path"] = repair_predictions
            if schema_slice is not None:
                report_kwargs["schema_slice_path"] = schema_slice
            if cq_manifest is not None:
                report_kwargs["cq_manifest_path"] = cq_manifest
            if prediction_output is not None:
                report_kwargs["prediction_output_path"] = prediction_output
            if run_metadata_output is not None:
                report_kwargs["run_metadata_output_path"] = run_metadata_output
            json_path, md_path, result = write_nasa_atmonto_l1_agent_batch_experiment(
                **report_kwargs
            )
            click.echo(f"Wrote {project_relative_path(json_path)}")
            click.echo(f"Wrote {project_relative_path(md_path)}")
            click.echo(
                f"L1 agent batch status: {result['status']} with "
                f"{result['metadata']['record_count']} record(s)."
            )
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc
