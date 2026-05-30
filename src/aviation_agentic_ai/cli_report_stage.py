from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.generation_runs import write_generation_run_summary
from aviation_agentic_ai.reporting.hygiene import run_report_hygiene
from aviation_agentic_ai.reporting.overnight import write_overnight_summary
from aviation_agentic_ai.reporting.reviews import write_review_progress


def register_stage_report_commands(report: click.Group) -> None:
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
