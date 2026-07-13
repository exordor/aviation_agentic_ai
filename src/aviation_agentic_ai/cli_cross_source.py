from __future__ import annotations

from datetime import date
from pathlib import Path

import click

from aviation_agentic_ai.config import resolve_project_path
from aviation_agentic_ai.cross_source.artifacts import read_jsonl, write_json
from aviation_agentic_ai.cross_source.config import load_cross_source_config
from aviation_agentic_ai.cross_source.evaluation.benchmark import evaluate_benchmark
from aviation_agentic_ai.cross_source.evaluation.mainline import (
    SYSTEM_LABELS,
    evaluate_ambiguity_challenge,
    evaluate_answer_baselines,
    evaluate_independent_answer_audit,
    render_mainline_markdown,
)
from aviation_agentic_ai.cross_source.graph.neo4j import load_neo4j_projection
from aviation_agentic_ai.cross_source.snapshots.registry import (
    SOURCE_GROUPS,
    activate_snapshot_set,
    build_local_snapshot_set,
)
from aviation_agentic_ai.cross_source.supervisor import answer_from_build, build_cross_source
from aviation_agentic_ai.paths import project_relative_path


DEFAULT_CONFIG = Path("configs/cross_source_v1.yaml")


def _config_option(function):
    return click.option(
        "--config",
        "config_path",
        type=click.Path(path_type=Path),
        default=DEFAULT_CONFIG,
        show_default=True,
    )(function)


@click.group("cross-source")
def cross_source_group() -> None:
    """Versioned abbreviation alignment and retrospective cross-source QA."""


@cross_source_group.command("refresh")
@_config_option
@click.option(
    "--source",
    type=click.Choice(["all", *SOURCE_GROUPS]),
    default="all",
    show_default=True,
)
@click.option("--as-of", type=click.DateTime(formats=["%Y-%m-%d"]), default=None)
@click.option("--activate/--candidate", default=False, show_default=True)
def refresh(config_path: Path, source: str, as_of, activate: bool) -> None:
    """Validate local source artifacts and write a checksummed snapshot manifest."""
    try:
        config = load_cross_source_config(config_path)
        snapshot_set = build_local_snapshot_set(config)
        if source != "all":
            selected = [item for item in snapshot_set.snapshots if item.source_family == source]
            snapshot_set = snapshot_set.model_copy(update={"snapshots": selected})
        if as_of is not None:
            requested = as_of.date()
            future = [
                item.source_family
                for item in snapshot_set.snapshots
                if item.effective_start.date() > requested
            ]
            if future:
                raise ValueError(
                    f"Configured snapshots are not effective by {date.isoformat(requested)}: {future}"
                )
        if activate:
            snapshot_set = activate_snapshot_set(snapshot_set)
        output = resolve_project_path(config["paths"]["processed_root"]) / "snapshot_set.json"
        write_json(output, snapshot_set)
        click.echo(f"Wrote {project_relative_path(output)}")
        click.echo(
            f"snapshot_set={snapshot_set.snapshot_set_id} status={snapshot_set.status.value} "
            f"sources={len(snapshot_set.snapshots)}"
        )
        click.echo("Refresh is explicit and local in V1; no network access was used.")
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@cross_source_group.command("align")
@_config_option
@click.option(
    "--context-mode",
    type=click.Choice(["autonomous", "provider"]),
    default="autonomous",
    show_default=True,
    help="Autonomous local policy is the default; provider mode is a future-compatible seam.",
)
def align(config_path: Path, context_mode: str) -> None:
    """Extract and gate facility and operational-term alignments over all advisories."""
    if context_mode == "provider":
        raise click.ClickException(
            "No context-agent provider is configured; use --context-mode autonomous."
        )
    try:
        build = build_cross_source(config_path, write_artifacts=True)
        counts: dict[str, int] = {}
        for decision in build.alignment.decisions:
            counts[decision.status.value] = counts.get(decision.status.value, 0) + 1
        click.echo(
            f"Aligned {len(build.alignment.mentions)} mentions across all advisories: {counts}"
        )
        click.echo(
            "Quarantined decisions were written only to the audit and quarantine artifacts."
        )
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@cross_source_group.command("build")
@_config_option
def build(config_path: Path) -> None:
    """Build the cohort, links, RDF graphs, and Neo4j property-graph projection."""
    try:
        result = build_cross_source(config_path, write_artifacts=True)
        graph = result.graph_artifacts
        click.echo(
            f"Built cohort={len(result.cohort.records)} links={len(result.linking.links)} "
            f"canonical_triples={graph.canonical_triples if graph else 0} "
            f"audit_triples={graph.audit_triples if graph else 0} "
            f"neo4j_nodes={graph.neo4j.node_count if graph else 0} "
            f"neo4j_relationships={graph.neo4j.relationship_count if graph else 0}"
        )
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@cross_source_group.command("neo4j-export")
@_config_option
def neo4j_export(config_path: Path) -> None:
    """Build reproducible Neo4j node and relationship JSONL files."""
    try:
        result = build_cross_source(config_path, write_artifacts=True)
        graph = result.graph_artifacts
        if graph is None:
            raise ValueError("Graph materialization did not produce Neo4j artifacts")
        click.echo(
            f"Wrote {project_relative_path(graph.neo4j.nodes_path)} "
            f"and {project_relative_path(graph.neo4j.relationships_path)}"
        )
        click.echo(
            f"neo4j_nodes={graph.neo4j.node_count} "
            f"neo4j_relationships={graph.neo4j.relationship_count}"
        )
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@cross_source_group.command("neo4j-load")
@_config_option
@click.option("--uri", envvar="NEO4J_URI", required=True, help="Bolt or Neo4j connection URI.")
@click.option("--username", envvar="NEO4J_USERNAME", required=True)
@click.option("--password", envvar="NEO4J_PASSWORD", required=True, hide_input=True)
@click.option("--database", envvar="NEO4J_DATABASE", default="neo4j", show_default=True)
@click.option("--replace-snapshot/--merge", default=False, show_default=True)
@click.option("--batch-size", type=click.IntRange(min=1), default=1000, show_default=True)
def neo4j_load(
    config_path: Path,
    uri: str,
    username: str,
    password: str,
    database: str,
    replace_snapshot: bool,
    batch_size: int,
) -> None:
    """Build and load the canonical property graph into Neo4j over Bolt."""
    try:
        result = build_cross_source(config_path, write_artifacts=True)
        graph = result.graph_artifacts
        if graph is None:
            raise ValueError("Graph materialization did not produce Neo4j artifacts")
        counts = load_neo4j_projection(
            uri=uri,
            username=username,
            password=password,
            database=database,
            nodes_path=graph.neo4j.nodes_path,
            relationships_path=graph.neo4j.relationships_path,
            snapshot_set_id=result.config["snapshot_set_id"],
            replace_snapshot=replace_snapshot,
            batch_size=batch_size,
        )
        click.echo(
            f"Loaded Neo4j database={database} nodes={counts['nodes']} "
            f"relationships={counts['relationships']}"
        )
    except (OSError, RuntimeError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@cross_source_group.command("answer")
@_config_option
@click.option("--source-id", required=True)
@click.option("--question", required=True)
@click.option("--output", type=click.Path(path_type=Path), default=None)
def answer(config_path: Path, source_id: str, question: str, output: Path | None) -> None:
    """Answer from pinned local artifacts with explicit evidence layers."""
    try:
        result = build_cross_source(config_path, write_artifacts=False)
        response = answer_from_build(result, source_id=source_id, question=question)
        if output is not None:
            target = resolve_project_path(output)
            write_json(target, response)
            click.echo(f"Wrote {project_relative_path(target)}")
        click.echo(response.model_dump_json(indent=2))
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@cross_source_group.command("evaluate")
@_config_option
@click.option(
    "--benchmark",
    "benchmark_path",
    type=click.Path(path_type=Path),
    required=True,
)
@click.option("--output", type=click.Path(path_type=Path), default=None)
def evaluate(config_path: Path, benchmark_path: Path, output: Path | None) -> None:
    """Evaluate autonomous policy regressions without claiming human-validated correctness."""
    try:
        config = load_cross_source_config(config_path)
        result = build_cross_source(config_path, write_artifacts=False)
        report = evaluate_benchmark(
            read_jsonl(resolve_project_path(benchmark_path)),
            build=result,
        )
        target = (
            resolve_project_path(output)
            if output is not None
            else resolve_project_path(config["paths"]["evaluation_root"])
            / "benchmark_evaluation.json"
        )
        write_json(target, report)
        click.echo(f"Wrote {project_relative_path(target)}")
        click.echo(str(report["summary"]))
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@cross_source_group.command("evaluate-mainline")
@_config_option
@click.option(
    "--benchmark",
    "benchmark_path",
    type=click.Path(path_type=Path),
    default=Path("data/evaluation/cross_source/v1/automated_regression_v1.jsonl"),
    show_default=True,
)
@click.option(
    "--ambiguity-challenge",
    "challenge_path",
    type=click.Path(path_type=Path),
    default=Path("data/evaluation/cross_source/v1/hard_ambiguity_v1.jsonl"),
    show_default=True,
)
@click.option(
    "--output-json",
    type=click.Path(path_type=Path),
    default=Path("reports/stages/cross_source_mainline_evaluation.json"),
    show_default=True,
)
@click.option(
    "--output-markdown",
    type=click.Path(path_type=Path),
    default=Path("reports/stages/cross_source_mainline_evaluation.md"),
    show_default=True,
)
def evaluate_mainline(
    config_path: Path,
    benchmark_path: Path,
    challenge_path: Path,
    output_json: Path,
    output_markdown: Path,
) -> None:
    """Run matched answer baselines and the hard ambiguity challenge."""
    try:
        result = build_cross_source(config_path, write_artifacts=False)
        report = {
            "snapshot_set_id": result.config["snapshot_set_id"],
            "answer_baselines": evaluate_answer_baselines(
                read_jsonl(resolve_project_path(benchmark_path)), build=result
            ),
            "ambiguity_challenge": evaluate_ambiguity_challenge(
                read_jsonl(resolve_project_path(challenge_path)), build=result
            ),
            "independent_answer_audit": evaluate_independent_answer_audit(
                read_jsonl(resolve_project_path(benchmark_path)), build=result
            ),
        }
        json_target = resolve_project_path(output_json)
        markdown_target = resolve_project_path(output_markdown)
        write_json(json_target, report)
        markdown_target.parent.mkdir(parents=True, exist_ok=True)
        markdown_target.write_text(render_mainline_markdown(report), encoding="utf-8")
        click.echo(f"Wrote {project_relative_path(json_target)}")
        click.echo(f"Wrote {project_relative_path(markdown_target)}")
        click.echo(str(report["ambiguity_challenge"]["summary"]))
        readable_systems = {
            SYSTEM_LABELS[key]: value
            for key, value in report["answer_baselines"]["systems"].items()
        }
        click.echo(str(readable_systems))
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
