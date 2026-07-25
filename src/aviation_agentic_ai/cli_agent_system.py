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
        click.echo(
            f"materialized: {materialization.valid_count} valid / "
            f"{materialization.schema_violation_count} schema_violation / "
            f"{materialization.profile_gap_count} profile_gap"
        )
        click.echo(f"kg_jsonl: {materialization.jsonl_path}")
    else:
        click.echo("materialized: 0 (abstained — no resolved event type)")


@agent_system.command("neo4j-export")
@click.option("--run-dir", "run_dir", type=click.Path(path_type=Path), required=True)
def neo4j_export(run_dir: Path):
    """Report the Neo4j nodes/relationships JSONL for a run (MERGE semantics)."""

    nodes_path = run_dir / "neo4j_nodes.jsonl"
    rels_path = run_dir / "neo4j_relationships.jsonl"
    if not nodes_path.exists():
        raise click.ClickException(f"no neo4j projection at {nodes_path}; run ingest first")
    nodes = [json.loads(ln) for ln in nodes_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    rels = [json.loads(ln) for ln in rels_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    # Idempotency check: canonical node ids are unique within a run.
    node_ids = [n["entity_id"] for n in nodes]
    dup_nodes = len(node_ids) - len(set(node_ids))
    node_id_set = set(node_ids)
    rel_keys = [(r["from"], r["to"], r["predicate"]) for r in rels]
    dup_rels = len(rel_keys) - len(set(rel_keys))
    # Endpoint completeness: every relationship endpoint must be a node row.
    missing_endpoints = sum(
        1 for r in rels if not r.get("from") or not r.get("to")
        or r["from"] not in node_id_set or r["to"] not in node_id_set
    )
    click.echo(f"nodes: {len(nodes)} (duplicate canonical ids: {dup_nodes})")
    click.echo(f"relationships: {len(rels)} (duplicate: {dup_rels})")
    click.echo(f"missing endpoints: {missing_endpoints}")
    click.echo(f"nodes_path: {nodes_path}")
    click.echo(f"relationships_path: {rels_path}")


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
    answer, sources, rec, facts = answer_question(
        run_dir=run_dir, question=question, model_invoker=invoker
    )
    click.echo(f"answer: {answer}")
    click.echo(f"sources: {', '.join(sources) if sources else '(none)'}")
    click.echo(f"graph_facts_seen: {len(facts)}")
