"""CLI for the multi-Agent aviation event knowledge system (design §19).

Three commands:

    aviation-ai agent-system ingest   --source-id <id> --config <cfg> [--allow-live-model]
    aviation-ai agent-system neo4j-export --run-dir <dir>
    aviation-ai agent-system ask      --run-dir <dir> --question "<q>" [--allow-live-model]

``ingest`` runs the fixed multi-Agent topology and materializes a source-bounded
event KG (JSONL + Turtle) in a versioned run directory. ``neo4j-export`` writes
the Neo4j nodes/relationships JSONL for a run. ``ask`` answers from that run's
materialized graph and lists the supporting source IDs.
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from aviation_agentic_ai.agent_system.materialize import (
    FactMaterialization,
    Neo4jLoadBlocked,
    load_validated_facts_neo4j,
)
from aviation_agentic_ai.agent_system.prompts import DEFAULT_PROMPT_CATALOG, get_prompt_catalog
from aviation_agentic_ai.agent_system.query import answer_question
from aviation_agentic_ai.agent_system.runtime import (
    MAX_PROVIDER_CALLS,
    make_live_model_invoker,
    new_run_directory,
    write_run_manifest,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.sources import (
    facility_candidates,
    load_advisory_source,
    term_candidates,
)
from aviation_agentic_ai.agent_system.workflow import IngestContext, run_ingest
from aviation_agentic_ai.config import load_yaml, resolve_project_path


@click.group("agent-system")
def agent_system() -> None:
    """Multi-Agent aviation event knowledge system (ingest / neo4j-export / ask)."""


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
    facilities = facility_candidates(config)
    terms = term_candidates(config)
    runs_root = resolve_project_path(
        config.get("paths", {}).get("agent_system_runs_root", "data/runs/agent_system")
    )
    run_dir = new_run_directory(runs_root, source_id)
    if not allow_live_model:
        raise click.ClickException(
            "ingest requires --allow-live-model to run the real DeepSeek Agents."
        )
    invoker = make_live_model_invoker(catalog_path=DEFAULT_PROMPT_CATALOG)
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=facilities,
        term_candidates=terms,
        guide=guide,
        model_invoker=invoker,
        run_id=run_dir.name,
        output_dir=str(run_dir),
    )
    state = run_ingest(ctx)
    model_calls = state.get("model_calls", [])
    if sum(1 for c in model_calls if c.error is None) > MAX_PROVIDER_CALLS:
        raise click.ClickException(
            f"provider calls exceeded hard maximum {MAX_PROVIDER_CALLS}"
        )
    materialization = state.get("materialization")
    kg_result = state.get("kg_result")
    graph_patch_raw = kg_result.graph_patch.raw if kg_result and kg_result.graph_patch else None
    evidence_cards = [
        r.evidence_card
        for r in (
            state.get("advisory_result"),
            state.get("facility_result"),
            state.get("terminology_result"),
        )
        if r and r.evidence_card
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
        catalog_path=DEFAULT_PROMPT_CATALOG,
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
        if isinstance(materialization, FactMaterialization):
            click.echo(f"materialized: {materialization.fact_count} validated facts")
        else:
            click.echo(
                f"materialized: {materialization.valid_count} valid / "
                f"{materialization.schema_violation_count} schema_violation / "
                f"{materialization.profile_gap_count} profile_gap"
            )
        click.echo(f"kg_jsonl: {materialization.jsonl_path}")
    else:
        click.echo("materialized: 0 (abstained — no resolved event type or non-publishable)")


@agent_system.command("neo4j-export")
@click.option("--run-dir", "run_dir", type=click.Path(path_type=Path), required=True)
@click.option("--uri", default=None, help="Neo4j bolt URI. Defaults to NEO4J_URI.")
@click.option("--username", default=None, help="Neo4j username. Defaults to NEO4J_USERNAME.")
@click.option("--password", default=None, help="Neo4j password. Defaults to NEO4J_PASSWORD.")
@click.option("--database", default="neo4j", show_default=True)
def neo4j_export(run_dir: Path, uri: str | None, username: str | None, password: str | None, database: str):
    """Load a run's projection into Neo4j with parameterized MERGE (plan §6.2).

    Connects to Neo4j and executes parameterized MERGE for the run's nodes and
    relationships. Missing credentials, failed connectivity, or a load error
    returns ``BLOCKED``. It never clears unrelated graph data (no DETACH
    DELETE); an unrelated sentinel node is preserved. Writes
    ``neo4j_load.json`` with the load summary.
    """

    import os

    nodes_path = run_dir / "neo4j_nodes.jsonl"
    rels_path = run_dir / "neo4j_relationships.jsonl"
    if not nodes_path.exists():
        raise click.ClickException(f"no neo4j projection at {nodes_path}; run ingest first")
    uri = uri or os.getenv("NEO4J_URI")
    username = username or os.getenv("NEO4J_USERNAME")
    password = password or os.getenv("NEO4J_PASSWORD")
    # Plan §6.2: missing credentials -> BLOCKED (never fake success).
    if not (uri and username and password):
        click.echo("BLOCKED: missing Neo4j credentials (set NEO4J_URI/NEO4J_USERNAME/NEO4J_PASSWORD)")
        _write_neo4j_load(run_dir, {"status": "blocked", "reason": "missing credentials"})
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
        _write_neo4j_load(run_dir, {"status": "blocked", "reason": str(exc)})
        raise click.ClickException(f"neo4j-export BLOCKED: {exc}") from exc
    summary["status"] = "loaded"
    _write_neo4j_load(run_dir, summary)
    click.echo(f"loaded nodes: {summary['nodes']} | relationships: {summary['relationships']}")
    click.echo(f"node_labels: {', '.join(summary['node_labels'])}")
    click.echo(f"relationship_types: {', '.join(summary['relationship_types'])}")
    click.echo(f"neo4j_load: {run_dir / 'neo4j_load.json'}")


def _write_neo4j_load(run_dir: Path, summary: dict) -> None:
    (run_dir / "neo4j_load.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )


@agent_system.command("ask")
@click.option("--run-dir", "run_dir", type=click.Path(path_type=Path), required=True)
@click.option("--question", required=True, help="Question to answer from the graph.")
@click.option("--allow-live-model", is_flag=True, help="Authorize the Query Agent model call.")
def ask(run_dir: Path, question: str, allow_live_model: bool) -> None:
    """Answer a question from the materialized graph with source IDs."""

    if not (run_dir / "kg.jsonl").exists():
        raise click.ClickException(f"no materialized KG at {run_dir / 'kg.jsonl'}")
    if not allow_live_model:
        raise click.ClickException("ask requires --allow-live-model to run the Query Agent.")
    invoker = make_live_model_invoker()
    status, answer, sources, rec, facts = answer_question(
        run_dir=run_dir, question=question, model_invoker=invoker
    )
    # §13 T3: a provider failure is reported as BLOCKED with a non-zero exit.
    if status == "blocked":
        click.echo(f"BLOCKED: {rec.error or 'query provider failure'}")
        raise click.ClickException(f"ask BLOCKED: {rec.error or 'query provider failure'}")
    click.echo(f"status: {status}")
    click.echo(f"answer: {answer}")
    click.echo(f"sources: {', '.join(sources) if sources else '(none)'}")
    click.echo(f"graph_facts_seen: {len(facts)}")
