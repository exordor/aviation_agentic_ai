"""CLI for the multi-Agent aviation event knowledge system (design §19).

Five commands:

    aviation-ai agent-system build-corpus --config <cfg> --output-dir <dir> [--allow-live-model] [--resume]
    aviation-ai agent-system ask      --corpus-dir <dir> --question "<q>"
    aviation-ai agent-system index-events --corpus-dir <dir>
    aviation-ai agent-system neo4j-export --corpus-dir <dir>
    aviation-ai agent-system export-event --corpus-dir <dir> --event-id <id> --output-dir <dir>

Corpus materialization is the only persisted read backend: ``build-corpus``
executes the selected advisory batch, ``ask`` and ``neo4j-export`` read its
stable artifacts, and ``export-event`` writes a bounded non-replayable event.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import click

from aviation_agentic_ai.agent_system.materialize import (
    Neo4jLoadBlocked,
    load_validated_facts_neo4j,
)
from aviation_agentic_ai.agent_system.corpus_batch import build_corpus_batch
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusBuildManifest,
    export_event,
)
from aviation_agentic_ai.agent_system.corpus_query import (
    answer_corpus_question,
)
from aviation_agentic_ai.agent_system.tool_model import make_live_tool_calling_model
from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
    DEFAULT_TMI_EVENT_EMBEDDING_MODEL,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_index import (
    SentenceTransformerTMIEventEncoder,
    build_tmi_event_retrieval_index,
)
from aviation_agentic_ai.config import load_yaml


@click.group("agent-system")
def agent_system() -> None:
    """Multi-Agent aviation event knowledge system."""


def _load_config(config_path: Path) -> dict:
    return load_yaml(str(config_path))


@agent_system.command("build-corpus")
@click.option(
    "--config",
    "config_path",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    default=Path("configs/cross_source_v1.yaml"),
    show_default=True,
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path, file_okay=False),
    required=True,
    help="Destination for the normalized cross-run corpus.",
)
@click.option(
    "--selection",
    type=click.Choice(["cohort", "all"]),
    default="cohort",
    show_default=True,
)
@click.option("--source-id", "source_ids", multiple=True)
@click.option("--allow-live-model", is_flag=True)
@click.option("--resume", is_flag=True)
def build_corpus_command(
    config_path: Path,
    output_dir: Path,
    selection: str,
    source_ids: tuple[str, ...],
    allow_live_model: bool,
    resume: bool,
) -> None:
    """Build or resume the selected advisory corpus."""

    summary = build_corpus_batch(
        _load_config(config_path),
        output_dir=output_dir,
        selection=selection,
        source_ids=source_ids,
        allow_live_model=allow_live_model,
        resume=resume,
    )
    click.echo(f"selected: {summary.selected_count}")
    click.echo(f"ok: {summary.ok_count}")
    click.echo(f"insufficient: {summary.insufficient_count}")
    click.echo(f"blocked: {summary.blocked_count}")
    usage_manifest = getattr(summary, "agent_usage_manifest", None)
    if usage_manifest is not None:
        totals = usage_manifest.totals
        click.echo(
            "agent_usage: "
            f"activated={totals.activated_count} "
            f"bypass={totals.deterministic_bypass_count} "
            f"accepted={totals.accepted_count} "
            f"abstained={totals.abstained_count} "
            f"blocked={totals.blocked_count}"
        )
        click.echo(
            "agent_calls: "
            f"provider={totals.provider_call_count} "
            f"tool={totals.tool_call_count} "
            f"tokens={totals.input_tokens}/{totals.output_tokens} "
            "latency_ms="
            f"{totals.provider_latency_ms:.3f}/{totals.tool_latency_ms:.3f}"
        )
    if summary.manifest is not None:
        click.echo(f"corpus_id: {summary.manifest.corpus_id}")
        click.echo(f"corpus_manifest: {output_dir / 'corpus_manifest.json'}")


@agent_system.command("index-events")
@click.option(
    "--corpus-dir",
    type=click.Path(path_type=Path, exists=True, file_okay=False),
    required=True,
    help="Normalized TMI-event corpus directory.",
)
@click.option(
    "--model-name",
    default=DEFAULT_TMI_EVENT_EMBEDDING_MODEL,
    show_default=True,
)
@click.option("--allow-model-download", is_flag=True)
def index_events_command(
    corpus_dir: Path,
    model_name: str,
    allow_model_download: bool,
) -> None:
    """Build the persistent TMI-event-level Chroma index."""

    try:
        encoder = SentenceTransformerTMIEventEncoder(
            model_name,
            allow_download=allow_model_download,
        )
    except ImportError as exc:
        raise click.ClickException(
            "Install TMI-event retrieval dependencies with "
            "uv sync --extra tmi-event-retrieval."
        ) from exc
    except Exception as exc:
        if not allow_model_download:
            raise click.ClickException(
                "The embedding model is not cached. Rerun with "
                "--allow-model-download."
            ) from exc
        raise click.ClickException(
            f"index-events BLOCKED: {exc}"
        ) from exc
    try:
        manifest = build_tmi_event_retrieval_index(
            corpus_dir,
            encoder=encoder,
        )
    except ImportError as exc:
        raise click.ClickException(
            "Install TMI-event retrieval dependencies with "
            "uv sync --extra tmi-event-retrieval."
        ) from exc
    except Exception as exc:
        raise click.ClickException(
            f"index-events BLOCKED: {exc}"
        ) from exc
    click.echo(f"indexed_events: {manifest.document_count}")
    click.echo(f"vector_backend: {manifest.vector_backend}")
    click.echo(f"collection_name: {manifest.collection_name}")
    click.echo(f"embedding_model: {manifest.embedding_model_id}")
    click.echo(f"embedding_dimension: {manifest.embedding_dimension}")
    click.echo(
        "tmi_event_index_manifest: "
        f"{corpus_dir / 'tmi_event_index' / 'tmi_event_index_manifest.json'}"
    )


@agent_system.command("ask")
@click.option(
    "--corpus-dir",
    type=click.Path(path_type=Path, exists=True, file_okay=False),
    required=True,
    help="Normalized TMI-event corpus directory.",
)
@click.option(
    "--question",
    required=True,
    help="Free natural-language question over the TMI-event corpus.",
)
@click.option("--event-id", default=None, help="Exact event for record questions.")
@click.option("--event-type-iri", default=None, help="Exact event-type IRI filter.")
@click.option("--facility-id", default=None, help="Exact canonical facility filter.")
@click.option(
    "--reason-status",
    type=click.Choice(["formal", "profile_gap", "missing"]),
    default=None,
    help="Exact declared-reason state filter.",
)
@click.option("--reason-value", default=None, help="Exact reason-value filter.")
@click.option(
    "--candidate-scope",
    type=click.Choice(["archive", "prior"]),
    default="archive",
    show_default=True,
    help="Historical candidate set available to similarity retrieval.",
)
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
    event_type_iri: str | None,
    facility_id: str | None,
    reason_status: str | None,
    reason_value: str | None,
    candidate_scope: str,
    offset: int,
    limit: int,
) -> None:
    """Run the LLM-routed HybridRAG Query Agent."""

    outcome = answer_corpus_question(
        corpus_dir=corpus_dir,
        question=question,
        event_id=event_id,
        event_type_iri=event_type_iri,
        facility_id=facility_id,
        reason_status=reason_status,
        reason_value=reason_value,
        candidate_scope=candidate_scope,
        offset=offset,
        limit=limit,
        model_factory=lambda tools: make_live_tool_calling_model(
            tools=tools,
            role="query",
        ),
    )
    if outcome.status == "blocked":
        raise click.ClickException(
            f"ask BLOCKED: {outcome.failure_reason}"
        )
    click.echo(f"status: {outcome.status}")
    click.echo(f"answer: {outcome.answer}")
    click.echo(f"matching_events: {outcome.match_count}")
    click.echo(
        "events_returned: "
        + (
            ", ".join(outcome.retrieved_event_ids)
            if outcome.retrieved_event_ids
            else "(none)"
        )
    )
    for match in outcome.similarity_matches:
        click.echo(
            "similar_event: "
            f"rank={match.rank} "
            f"event_id={match.event_id} "
            f"source_id={match.advisory_source_id} "
            f"score={match.score:.6f}"
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

    try:
        nodes_path, rels_path = _validated_neo4j_projection(corpus_dir)
    except ValueError as exc:
        raise click.ClickException(f"neo4j-export BLOCKED: {exc}") from exc
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


def _validated_neo4j_projection(corpus_dir: Path) -> tuple[Path, Path]:
    manifest_path = corpus_dir / "corpus_manifest.json"
    try:
        manifest = CorpusBuildManifest.model_validate_json(
            manifest_path.read_text(encoding="utf-8")
        )
    except (OSError, ValueError) as exc:
        raise ValueError(
            "a published tmi-event-corpus-v3 manifest is required"
        ) from exc

    paths: list[Path] = []
    for artifact_name in ("neo4j_nodes", "neo4j_relationships"):
        metadata = manifest.artifacts.get(artifact_name)
        if metadata is None:
            raise ValueError(
                f"manifest does not register {artifact_name}"
            )
        artifact_path = corpus_dir / metadata.path
        if not artifact_path.is_file():
            raise ValueError(
                f"missing Neo4j projection artifact: {metadata.path}"
            )
        data = artifact_path.read_bytes()
        count = sum(1 for line in data.splitlines() if line.strip())
        if count != metadata.count:
            raise ValueError(
                f"Neo4j projection row-count mismatch: {metadata.path}"
            )
        if hashlib.sha256(data).hexdigest() != metadata.sha256:
            raise ValueError(
                f"Neo4j projection checksum mismatch: {metadata.path}"
            )
        paths.append(artifact_path)
    return paths[0], paths[1]


def _write_neo4j_load(run_dir: Path, summary: dict) -> None:
    (run_dir / "neo4j_load.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )


@agent_system.command("export-event")
@click.option("--corpus-dir", type=click.Path(path_type=Path), required=True)
@click.option("--event-id", required=True, help="Exact event to export.")
@click.option("--output-dir", type=click.Path(path_type=Path), required=True)
def export_event_command(corpus_dir: Path, event_id: str, output_dir: Path) -> None:
    """Export one bounded TMI event without fabricating a replayable run."""

    try:
        result = export_event(
            corpus_dir=corpus_dir,
            event_id=event_id,
            output_dir=output_dir,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"event_export: {result}")
