from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path, resolve_output_path
from aviation_agentic_ai.reporting.hygiene import run_report_hygiene


def register_stage_report_commands(report: click.Group) -> None:

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
        try:
            if dry_run and apply_changes:
                raise click.ClickException("Use either --dry-run or --apply, not both.")
            config = load_default_config()
            stages = stage_dir or resolve_project_path(config["paths"]["stage_report_dir"])
            archive = archive_root or resolve_project_path("reports/archive")
            if apply_changes and archive_root is not None:
                archive = resolve_output_path(archive_root)
            if apply_changes and stage_dir is not None:
                stages = resolve_output_path(stage_dir)
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
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc
