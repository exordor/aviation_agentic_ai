from __future__ import annotations

from pathlib import Path

import click

from aviation_agentic_ai.config import load_default_config, resolve_project_path
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.academic_outputs import (
    write_academic_report,
    write_defense_deck_outline,
    write_defense_notes,
    write_visual_assets,
)
from aviation_agentic_ai.reporting.evaluation_protocol import (
    write_evaluation_protocol_review,
)
from aviation_agentic_ai.reporting.project_report import write_project_report
from aviation_agentic_ai.reporting.thesis_claims import write_thesis_claims_review
from aviation_agentic_ai.reporting.thesis_dashboard import (
    write_thesis_experiment_dashboard,
)


def register_thesis_report_commands(report: click.Group) -> None:
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
        try:
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
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

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
        try:
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
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

    @report.command("evaluation-protocol")
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--report-name", default="evaluation_protocol_review", show_default=True)
    def report_evaluation_protocol(output_dir: Path | None, report_name: str) -> None:
        """Summarize layered mainstream RAG/GraphRAG/KG evaluation coverage."""
        try:
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
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

    @report.command("thesis-experiment-dashboard")
    @click.option("--output-dir", type=click.Path(path_type=Path), default=None)
    @click.option("--report-name", default="thesis_experiment_dashboard", show_default=True)
    def report_thesis_experiment_dashboard(
        output_dir: Path | None,
        report_name: str,
    ) -> None:
        """Aggregate thesis experiment reports into an RQ-oriented dashboard."""
        try:
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
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

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
        try:
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
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

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
        try:
            output = output_dir or resolve_project_path("reports/final")
            md_path, json_path, notes = write_defense_notes(
                output,
                stage_index_path=stage_index,
            )
            click.echo(f"Wrote {project_relative_path(md_path)}")
            click.echo(f"Wrote {project_relative_path(json_path)}")
            click.echo(f"Generated {len(notes['qa_pairs'])} defense Q&A pairs.")
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

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
    def report_defense_deck_outline(
        output_dir: Path | None, stage_index: Path | None
    ) -> None:
        """Generate an academic PPT outline and source pack."""
        try:
            output = output_dir or resolve_project_path("reports/final")
            md_path, json_path, outline = write_defense_deck_outline(
                output,
                stage_index_path=stage_index,
            )
            click.echo(f"Wrote {project_relative_path(md_path)}")
            click.echo(f"Wrote {project_relative_path(json_path)}")
            click.echo(f"Generated {len(outline['slides'])} slide outlines.")
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc

    @report.command("visual-assets")
    @click.option(
        "--output-dir",
        type=click.Path(path_type=Path),
        default=None,
        help="Directory for final visual assets.",
    )
    def report_visual_assets(output_dir: Path | None) -> None:
        """Generate SVG fallback assets and record any externally generated PNG assets."""
        try:
            output = output_dir or resolve_project_path("reports/final")
            paths, manifest = write_visual_assets(output)
            for path in paths:
                click.echo(f"Wrote {project_relative_path(path)}")
            click.echo(
                "Wrote visual asset manifest; AI PNG assets present: "
                f"{manifest['uses_gateway_or_api']}. "
                "No credentials or gateway URL were recorded."
            )
        except Exception as exc:
            raise click.ClickException(str(exc)) from exc
