"""CLI for the multi-Agent aviation event knowledge system (design §19).

Five commands:

    aviation-ai agent-system ingest   --source-id <id> --config <cfg> [--allow-live-model]
    aviation-ai agent-system build-corpus --runs-root <dir> --output-dir <dir>
    aviation-ai agent-system ask      --corpus-dir <dir> --question "<q>"
    aviation-ai agent-system neo4j-export --corpus-dir <dir>
    aviation-ai agent-system export-case --corpus-dir <dir> --event-id <id> --output-dir <dir>

``ingest`` runs the fixed multi-Agent topology and materializes a source-bounded
event KG (JSONL + Turtle) in a versioned run directory. Corpus materialization
is the only persisted read backend: ``ask`` and ``neo4j-export`` read its
stable artifacts, while ``export-case`` writes a bounded non-replayable case.
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from aviation_agentic_ai.agent_system.materialize import (
    Neo4jLoadBlocked,
    load_validated_facts_neo4j,
)
from aviation_agentic_ai.agent_system.corpus_store import build_corpus, export_case
from aviation_agentic_ai.agent_system.corpus_query import (
    answer_corpus_question,
)
from aviation_agentic_ai.agent_system.authority_evidence import (
    AuthorityBuildStatus,
    load_authority_catalog,
)
from aviation_agentic_ai.agent_system.prompts import DEFAULT_PROMPT_CATALOG, get_prompt_catalog
from aviation_agentic_ai.agent_system.runtime import (
    MAX_PROVIDER_CALLS,
    create_run_binding,
    write_run_manifest,
)
from aviation_agentic_ai.agent_system.schema_guide import (
    DEFAULT_SCHEMA_SLICE,
    load_schema_guide,
)
from aviation_agentic_ai.agent_system.sources import (
    load_advisory_source,
    load_bts_context_source,
    load_weather_sources,
)
from aviation_agentic_ai.agent_system.tool_model import make_live_tool_calling_model
from aviation_agentic_ai.agent_system.workflow import IngestContext, run_ingest
from aviation_agentic_ai.config import load_yaml, resolve_project_path


@click.group("agent-system")
def agent_system() -> None:
    """Multi-Agent aviation event knowledge system."""


def _load_config(config_path: Path) -> dict:
    return load_yaml(str(config_path))


@agent_system.command("ingest")
@click.option("--source-id", required=True, help="ATCSCC advisory source_id.")
@click.option(
    "--config",
    "config_path",
    type=click.Path(path_type=Path, exists=True),
    default=Path("configs/cross_source_v1.yaml"),
    show_default=True,
)
@click.option("--allow-live-model", is_flag=True, help="Authorize a real DeepSeek run.")
def ingest(source_id: str, config_path: Path, allow_live_model: bool) -> None:
    """Run the fixed multi-Agent topology and materialize an event KG."""

    config = _load_config(config_path)
    advisory = load_advisory_source(config, source_id)
    guide = load_schema_guide()
    catalog = get_prompt_catalog(DEFAULT_PROMPT_CATALOG)
    weather_sources = []
    bts_rows = []
    bts_source = None
    bts_manifest_binding = None
    weather_failure_reason = ""
    bts_failure_reason = ""
    try:
        weather_sources = load_weather_sources(config)
    except (OSError, TypeError, ValueError) as exc:
        weather_failure_reason = str(exc)
    try:
        bts_source, bts_rows, bts_manifest_binding = load_bts_context_source(config)
    except (OSError, TypeError, ValueError) as exc:
        bts_failure_reason = str(exc)
    runs_root = resolve_project_path(
        config.get("paths", {}).get("agent_system_runs_root", "data/runs/agent_system")
    )
    run_binding = create_run_binding(runs_root, source_id)
    run_dir = run_binding.run_dir
    if not allow_live_model:
        raise click.ClickException(
            "ingest requires --allow-live-model to run the real DeepSeek Agents."
        )
    authority_catalog = load_authority_catalog(
        config,
        guide=guide,
        schema_guide_path=DEFAULT_SCHEMA_SLICE,
        created_at=run_binding.run_started_at,
    )
    facilities = (
        list(authority_catalog.facility.entities)
        if authority_catalog.facility.status is AuthorityBuildStatus.OK
        else []
    )
    terms = (
        list(authority_catalog.terminology.registry_terms)
        if authority_catalog.terminology.status is AuthorityBuildStatus.OK
        else []
    )
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=facilities,
        term_candidates=terms,
        weather_sources=weather_sources,
        bts_rows=bts_rows,
        bts_source=bts_source,
        bts_manifest_binding=bts_manifest_binding,
        weather_failure_reason=weather_failure_reason,
        bts_failure_reason=bts_failure_reason,
        guide=guide,
        semantic_resolution_tool_model_factory=lambda tools: make_live_tool_calling_model(
            tools=tools,
            role="semantic_resolution",
            catalog_path=DEFAULT_PROMPT_CATALOG,
        ),
        case_assembly_model_factory=lambda tools: make_live_tool_calling_model(
            tools=tools,
            role="decision_case_assembly",
            catalog_path=DEFAULT_PROMPT_CATALOG,
        ),
        authority_catalog=authority_catalog,
        run_started_at=run_binding.run_started_at,
        run_id=run_binding.run_id,
        output_dir=str(run_dir),
    )
    state = run_ingest(ctx)
    model_calls = state.get("model_calls", [])
    if len(model_calls) > MAX_PROVIDER_CALLS:
        raise click.ClickException(f"provider calls exceeded hard maximum {MAX_PROVIDER_CALLS}")
    materialization = state.get("materialization")
    validation = state.get("validation")
    assembly_graph_patch = state.get("assembly_graph_patch")
    graph_patch_raw = assembly_graph_patch.raw if assembly_graph_patch else None
    evidence_cards = [
        getattr(r, "evidence_card", r)
        for r in (
            state.get("advisory_evidence"),
            state.get("facility_authority_result"),
            state.get("terminology_authority_result"),
        )
        if r and getattr(r, "evidence_card", r)
    ]
    write_run_manifest(
        run_dir=run_dir,
        source_id=source_id,
        model_calls=model_calls,
        materialization=materialization,
        schema_slice_id=guide.schema_slice_id,
        schema_checksum=guide.checksum,
        evidence_cards=evidence_cards,
        graph_patch_raw=graph_patch_raw,
        prompt_set_id=catalog.prompt_set_id,
        profile_gap_count=len(validation.profile_gaps) if validation else 0,
        context_artifacts=state.get("context_artifacts", {}),
        formal_layers=state.get("formal_layers", {}),
        public_observation_publication=state.get(
            "public_observation_publication",
            {},
        ),
        catalog_path=DEFAULT_PROMPT_CATALOG,
        created_at=run_binding.run_started_at,
    )
    click.echo(f"run_dir: {run_dir}")
    click.echo(f"prompt_set_id: {catalog.prompt_set_id}")
    click.echo(f"schema_slice_id: {guide.schema_slice_id}")
    failed = [c for c in model_calls if c.error]
    if failed:
        click.echo(f"failed_attempts: {len(failed)}")
    for call in model_calls:
        click.echo(
            f"call: agent={call.agent} prompt_version={call.prompt_version} "
            f"attempt={call.attempt} "
            f"{'error=' + call.error if call.error else 'tokens=' + str(call.input_tokens) + '/' + str(call.output_tokens)}"
        )
    if materialization:
        click.echo(f"materialized: {materialization.fact_count} validated facts")
        click.echo(f"kg_jsonl: {materialization.jsonl_path}")
    else:
        click.echo("materialized: 0 (abstained — no resolved event type or non-publishable)")


@agent_system.command("build-corpus")
@click.option(
    "--runs-root",
    type=click.Path(path_type=Path, exists=True, file_okay=False),
    required=True,
    help="Directory containing validated Agent-system runs.",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path, file_okay=False),
    required=True,
    help="Destination for the normalized cross-run corpus.",
)
def build_corpus_command(runs_root: Path, output_dir: Path) -> None:
    """Build a deduplicated corpus from current validated run bundles."""

    run_dirs = sorted(
        {
            manifest.parent
            for manifest in runs_root.rglob("run_manifest.json")
        }
    )
    if not run_dirs:
        raise click.ClickException(
            f"no validated run manifests found under {runs_root}"
        )
    manifest = build_corpus(
        run_dirs=run_dirs,
        output_dir=output_dir,
    )
    click.echo(f"corpus_id: {manifest.corpus_id}")
    click.echo(f"cases: {manifest.case_count}")
    click.echo(f"facts: {manifest.fact_count}")
    click.echo(f"source_objects: {manifest.source_object_count}")
    click.echo(f"corpus_manifest: {output_dir / 'corpus_manifest.json'}")


@agent_system.command("ask")
@click.option(
    "--corpus-dir",
    type=click.Path(path_type=Path, exists=True, file_okay=False),
    required=True,
    help="Normalized decision-case corpus directory.",
)
@click.option("--question", required=True, help="Registered corpus question.")
@click.option("--event-id", default=None, help="Exact event for record questions.")
@click.option(
    "--allow-live-model",
    is_flag=True,
    help="Authorize a registered Decision Case Analysis model call when available.",
)
@click.option("--event-type-iri", default=None, help="Exact event-type IRI filter.")
@click.option("--facility-id", default=None, help="Exact canonical facility filter.")
@click.option(
    "--reason-status",
    type=click.Choice(["formal", "profile_gap", "missing"]),
    default=None,
    help="Exact declared-reason state filter.",
)
@click.option("--reason-value", default=None, help="Exact reason-value filter.")
@click.option("--offset", type=click.IntRange(min=0), default=0, show_default=True)
@click.option(
    "--limit",
    type=click.IntRange(min=1, max=100),
    default=20,
    show_default=True,
)
def ask(
    corpus_dir: Path,
    question: str,
    event_id: str | None,
    allow_live_model: bool,
    event_type_iri: str | None,
    facility_id: str | None,
    reason_status: str | None,
    reason_value: str | None,
    offset: int,
    limit: int,
) -> None:
    """Run one deterministic read over the normalized case corpus."""

    del allow_live_model
    outcome = answer_corpus_question(
        corpus_dir=corpus_dir,
        question=question,
        event_id=event_id,
        event_type_iri=event_type_iri,
        facility_id=facility_id,
        reason_status=reason_status,
        reason_value=reason_value,
        offset=offset,
        limit=limit,
    )
    if outcome.status == "blocked":
        raise click.ClickException(
            f"ask BLOCKED: {outcome.failure_reason}"
        )
    click.echo(f"status: {outcome.status}")
    click.echo(f"answer: {outcome.answer}")
    click.echo(f"matching_cases: {outcome.match_count}")
    click.echo(
        "cases_returned: "
        + (
            ", ".join(outcome.retrieved_case_ids)
            if outcome.retrieved_case_ids
            else "(none)"
        )
    )
    click.echo(
        f"sources: {', '.join(outcome.source_ids) if outcome.source_ids else '(none)'}"
    )
    click.echo(f"graph_facts_seen: {len(outcome.retrieved_fact_ids)}")
    click.echo(f"model_calls: {len(outcome.model_calls)}")
    click.echo(f"tool_calls: {len(outcome.tool_calls)}")


@agent_system.command("neo4j-export")
@click.option("--corpus-dir", "corpus_dir", type=click.Path(path_type=Path), required=True)
@click.option("--uri", default=None, help="Neo4j bolt URI. Defaults to NEO4J_URI.")
@click.option("--username", default=None, help="Neo4j username. Defaults to NEO4J_USERNAME.")
@click.option("--password", default=None, help="Neo4j password. Defaults to NEO4J_PASSWORD.")
@click.option("--database", default="neo4j", show_default=True)
def neo4j_export(
    corpus_dir: Path, uri: str | None, username: str | None, password: str | None, database: str
):
    """Load a corpus projection into Neo4j with parameterized MERGE.

    Connects to Neo4j and executes parameterized MERGE for the run's nodes and
    relationships. Missing credentials, failed connectivity, or a load error
    returns ``BLOCKED``. It never clears unrelated graph data (no DETACH
    DELETE); an unrelated sentinel node is preserved. Writes
    ``neo4j_load.json`` with the load summary.
    """

    import os

    nodes_path = corpus_dir / "neo4j_nodes.jsonl"
    rels_path = corpus_dir / "neo4j_relationships.jsonl"
    if not nodes_path.exists():
        raise click.ClickException(f"no corpus Neo4j projection at {nodes_path}")
    uri = uri or os.getenv("NEO4J_URI")
    username = username or os.getenv("NEO4J_USERNAME")
    password = password or os.getenv("NEO4J_PASSWORD")
    # Plan §6.2: missing credentials -> BLOCKED (never fake success).
    if not (uri and username and password):
        click.echo(
            "BLOCKED: missing Neo4j credentials (set NEO4J_URI/NEO4J_USERNAME/NEO4J_PASSWORD)"
        )
        _write_neo4j_load(corpus_dir, {"status": "blocked", "reason": "missing credentials"})
        raise click.ClickException("neo4j-export BLOCKED: missing Neo4j credentials")
    try:
        summary = load_validated_facts_neo4j(
            nodes_path=nodes_path,
            relationships_path=rels_path,
            uri=uri,
            username=username,
            password=password,
            database=database,
        )
    except Neo4jLoadBlocked as exc:
        click.echo(f"BLOCKED: {exc}")
        _write_neo4j_load(corpus_dir, {"status": "blocked", "reason": str(exc)})
        raise click.ClickException(f"neo4j-export BLOCKED: {exc}") from exc
    summary["status"] = "loaded"
    _write_neo4j_load(corpus_dir, summary)
    click.echo(f"loaded nodes: {summary['nodes']} | relationships: {summary['relationships']}")
    click.echo(f"node_labels: {', '.join(summary['node_labels'])}")
    click.echo(f"relationship_types: {', '.join(summary['relationship_types'])}")
    click.echo(f"neo4j_load: {corpus_dir / 'neo4j_load.json'}")


def _write_neo4j_load(run_dir: Path, summary: dict) -> None:
    (run_dir / "neo4j_load.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )


@agent_system.command("export-case")
@click.option("--corpus-dir", type=click.Path(path_type=Path), required=True)
@click.option("--event-id", required=True, help="Exact event to export.")
@click.option("--output-dir", type=click.Path(path_type=Path), required=True)
def export_case_command(corpus_dir: Path, event_id: str, output_dir: Path) -> None:
    """Export one bounded decision case without fabricating a replayable run."""

    try:
        result = export_case(
            corpus_dir=corpus_dir,
            event_id=event_id,
            output_dir=output_dir,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"case_export: {result}")
