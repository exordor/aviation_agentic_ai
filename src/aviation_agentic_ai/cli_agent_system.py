"""CLI for the ingestion-first HybridRAG aviation knowledge system.

The persistent evidence store is authoritative. SQLite holds immutable source
versions and accepted semantics; FTS and Chroma are rebuildable indexes; RDF
and Neo4j files are optional exports.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import click

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryScope,
    SourceFamily,
)
from aviation_agentic_ai.agent_system.evidence_export import (
    build_store_kg_projection,
    export_event,
)
from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
)
from aviation_agentic_ai.agent_system.ingestion_pipeline import (
    run_ingestion_pipeline,
)
from aviation_agentic_ai.agent_system.knowledge_query import answer_question
from aviation_agentic_ai.agent_system.materialize import (
    Neo4jLoadBlocked,
    load_validated_facts_neo4j,
)
from aviation_agentic_ai.agent_system.query_runtime import open_query_runtime
from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
    DEFAULT_TMI_EVENT_EMBEDDING_MODEL,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_index import (
    SentenceTransformerTMIEventEncoder,
    reindex_store,
)
from aviation_agentic_ai.agent_system.tool_model import (
    make_live_tool_calling_model,
)
from aviation_agentic_ai.config import (
    configured_dataset_id,
    configured_store_root,
    load_environment,
    load_yaml,
    resolve_project_path,
)


@click.group("agent-system")
def agent_system() -> None:
    """Ingest and query the live aviation HybridRAG knowledge runtime."""


def _load_config(config_path: Path) -> dict[str, Any]:
    return load_yaml(str(config_path))


def _store_root(
    config: dict[str, Any],
    store_dir: Path | None,
) -> Path:
    return (
        configured_store_root(config)
        if store_dir is None
        else resolve_project_path(store_dir)
    )


def _open_store(
    config: dict[str, Any],
    store_dir: Path | None,
    *,
    create: bool,
) -> AviationEvidenceStore:
    return AviationEvidenceStore.open(
        _store_root(config, store_dir),
        dataset_id=configured_dataset_id(config),
        create=create,
    )


def _storage_config(config: dict[str, Any]) -> dict[str, Any]:
    agent_system_config = config.get("agent_system")
    if not isinstance(agent_system_config, dict):
        raise ValueError("config.agent_system must be a mapping")
    storage = agent_system_config.get("storage")
    if not isinstance(storage, dict):
        raise ValueError("config.agent_system.storage must be a mapping")
    return storage


def _storage_path(
    config: dict[str, Any],
    store: AviationEvidenceStore,
    key: str,
    default: str,
) -> Path:
    configured = _storage_config(config).get(key, default)
    if not isinstance(configured, str) or not configured:
        raise ValueError(
            f"config.agent_system.storage.{key} must be a non-empty path"
        )
    path = Path(configured)
    return path if path.is_absolute() else Path(store.root) / path


def _embedding_model(
    config: dict[str, Any],
    override: str | None,
) -> str:
    if override:
        return override
    configured = _storage_config(config).get(
        "embedding_model",
        DEFAULT_TMI_EVENT_EMBEDDING_MODEL,
    )
    if not isinstance(configured, str) or not configured:
        raise ValueError(
            "config.agent_system.storage.embedding_model must be a "
            "non-empty string"
        )
    return configured


def _source_display_label(version: Any) -> str:
    """Return a human-readable citation label without exposing an internal ID."""

    metadata = version.metadata if isinstance(version.metadata, dict) else {}
    family = str(version.family.value)
    authority = {
        SourceFamily.ATCSCC_ADVISORY.value: "FAA ATCSCC",
        SourceFamily.NASR_FACILITY.value: "FAA NASR",
        SourceFamily.FAA_TERM.value: "FAA terminology",
        SourceFamily.METAR.value: "AviationWeather METAR",
        SourceFamily.TAF.value: "AviationWeather TAF",
        SourceFamily.BTS_ON_TIME.value: "BTS On-Time",
    }.get(family, family.replace("_", " ").title())
    title = str(metadata.get("title") or authority)
    if family == SourceFamily.ATCSCC_ADVISORY.value:
        advisory_number = metadata.get("advisory_number")
        advisory_date = metadata.get("advisory_date")
        if advisory_number is None or advisory_date is None:
            date_part, separator, number_part = version.source_id.partition(":")
            advisory_date = advisory_date or (date_part if separator else None)
            advisory_number = advisory_number or (number_part if separator else None)
        title = "ATCSCC Advisory"
        if advisory_number is not None:
            title += f" {advisory_number}"
        if advisory_date is not None:
            title += f" ({advisory_date})"
    elif version.logical_time:
        title += f" ({version.logical_time})"
    label = f"{title} — {authority}"
    if version.source_url:
        label += f" — {version.source_url}"
    return label


def _config_option(function):
    return click.option(
        "--config",
        "config_path",
        type=click.Path(path_type=Path, exists=True, dir_okay=False),
        default=Path("configs/aviation_knowledge_v1.yaml"),
        show_default=True,
    )(function)


def _store_option(function):
    return click.option(
        "--store-dir",
        type=click.Path(path_type=Path, file_okay=False),
        default=None,
        help="Override config.agent_system.storage.root.",
    )(function)


@agent_system.command("ingest")
@_config_option
@_store_option
@click.option(
    "--advisory-id",
    "advisory_ids",
    multiple=True,
    help="Build or backfill only the named ATCSCC advisory records.",
)
@click.option("--allow-live-model", is_flag=True)
@click.option("--allow-model-download", is_flag=True)
def ingest_command(
    config_path: Path,
    store_dir: Path | None,
    advisory_ids: tuple[str, ...],
    allow_live_model: bool,
    allow_model_download: bool,
) -> None:
    """Incrementally ingest configured sources into the persistent store."""

    config = _load_config(config_path)
    store = _open_store(config, store_dir, create=True)
    try:
        summary = run_ingestion_pipeline(
            config,
            store,
            advisory_ids=advisory_ids,
            allow_live_model=allow_live_model,
            allow_model_download=allow_model_download,
        )
        revision = store.get_knowledge_revision()
    finally:
        store.close()
    click.echo(f"discovered: {summary.discovered_count}")
    click.echo(f"selected: {summary.selected_count}")
    click.echo(f"attempted: {summary.attempted_count}")
    click.echo(f"skipped: {summary.skipped_count}")
    click.echo(f"ok: {summary.ok_count}")
    click.echo(f"insufficient: {summary.insufficient_count}")
    click.echo(f"blocked: {summary.blocked_count}")
    click.echo(f"knowledge_revision: {revision}")


@agent_system.command("reindex")
@_config_option
@_store_option
@click.option("--model-name", default=None)
@click.option("--allow-model-download", is_flag=True)
def reindex_command(
    config_path: Path,
    store_dir: Path | None,
    model_name: str | None,
    allow_model_download: bool,
) -> None:
    """Rebuild source and TMI-event vector indexes from the live store."""

    config = _load_config(config_path)
    store = _open_store(config, store_dir, create=False)
    model = _embedding_model(config, model_name)
    try:
        encoder = SentenceTransformerTMIEventEncoder(
            model,
            allow_download=allow_model_download,
        )
        states = reindex_store(
            store,
            _storage_path(config, store, "chroma", "chroma"),
            encoder=encoder,
        )
    except ImportError as exc:
        raise click.ClickException(
            "Install retrieval dependencies with "
            "uv sync --extra tmi-event-retrieval."
        ) from exc
    except Exception as exc:
        raise click.ClickException(f"reindex BLOCKED: {exc}") from exc
    finally:
        store.close()
    for state in states:
        click.echo(
            "index: "
            f"{state.collection_name} "
            f"status={state.status} "
            f"documents={state.document_count} "
            f"vectors={state.vector_count}"
        )


@agent_system.command("ask")
@_config_option
@_store_option
@click.option("--question", required=True)
@click.option(
    "--source-family",
    "source_families",
    multiple=True,
    type=click.Choice([family.value for family in SourceFamily]),
)
@click.option("--event-id", default=None)
@click.option("--event-type-iri", default=None)
@click.option("--facility-id", default=None)
@click.option(
    "--reason-status",
    type=click.Choice(["formal", "profile_gap", "missing"]),
    default=None,
)
@click.option("--reason-value", default=None)
@click.option(
    "--candidate-scope",
    type=click.Choice(["archive", "prior"]),
    default="archive",
    show_default=True,
)
@click.option("--offset", type=click.IntRange(min=0), default=0)
@click.option("--limit", type=click.IntRange(min=1, max=100), default=20)
@click.option("--allow-model-download", is_flag=True)
def ask_command(
    config_path: Path,
    store_dir: Path | None,
    question: str,
    source_families: tuple[str, ...],
    event_id: str | None,
    event_type_iri: str | None,
    facility_id: str | None,
    reason_status: str | None,
    reason_value: str | None,
    candidate_scope: str,
    offset: int,
    limit: int,
    allow_model_download: bool,
) -> None:
    """Ask a natural-language question through the bounded Query Agent."""

    config = _load_config(config_path)
    load_environment()
    runtime = open_query_runtime(
        config,
        store_dir=store_dir,
        allow_model_download=allow_model_download,
    )
    source_labels: list[str] = []
    try:
        outcome = answer_question(
            runtime=runtime,
            question=question,
            scope=HybridQueryScope(
                event_id=event_id,
                event_type_iri=event_type_iri,
                facility_id=facility_id,
                reason_status=reason_status,  # type: ignore[arg-type]
                reason_value=reason_value,
                source_families=tuple(
                    SourceFamily(value) for value in source_families
                ),
                candidate_scope=candidate_scope,  # type: ignore[arg-type]
                offset=offset,
                limit=limit,
            ),
            model_factory=lambda tools: make_live_tool_calling_model(
                tools=tools,
                role="query",
            ),
        )
        cited_source_version_ids = dict.fromkeys(
            source_version_id
            for statement in outcome.answer_statements
            for source_version_id in statement.support_source_version_ids
        )
        for source_version_id in cited_source_version_ids:
            version = runtime.store.get_source_version(source_version_id)
            if version is not None:
                source_labels.append(_source_display_label(version))
    finally:
        runtime.store.close()
    if outcome.status == "blocked":
        raise click.ClickException(
            f"ask BLOCKED: {outcome.failure_reason}"
        )
    click.echo(f"status: {outcome.status}")
    click.echo(f"answer: {outcome.answer}")
    click.echo(f"events_retrieved: {len(outcome.retrieved_event_ids)}")
    click.echo("evidence_sources:")
    if source_labels:
        for label in dict.fromkeys(source_labels):
            click.echo(f"- {label}")
    else:
        click.echo("- (none reported)")
    click.echo(f"model_calls: {len(outcome.model_calls)}")
    click.echo(f"tool_calls: {len(outcome.tool_calls)}")


@agent_system.command("neo4j-export")
@_config_option
@_store_option
@click.option("--uri", default=None)
@click.option("--username", default=None)
@click.option("--password", default=None)
@click.option("--database", default="neo4j", show_default=True)
def neo4j_export_command(
    config_path: Path,
    store_dir: Path | None,
    uri: str | None,
    username: str | None,
    password: str | None,
    database: str,
) -> None:
    """Build the current store projection and load it into Neo4j."""

    config = _load_config(config_path)
    store = _open_store(config, store_dir, create=False)
    try:
        projection = build_store_kg_projection(
            store,
            _storage_path(config, store, "exports", "exports")
            / "neo4j-current",
        )
    finally:
        store.close()
    uri = uri or os.getenv("NEO4J_URI")
    username = username or os.getenv("NEO4J_USERNAME")
    password = password or os.getenv("NEO4J_PASSWORD")
    if not (uri and username and password):
        raise click.ClickException(
            "neo4j-export BLOCKED: missing Neo4j credentials"
        )
    try:
        summary = load_validated_facts_neo4j(
            nodes_path=projection.nodes_path,
            relationships_path=projection.relationships_path,
            uri=uri,
            username=username,
            password=password,
            database=database,
        )
    except Neo4jLoadBlocked as exc:
        raise click.ClickException(
            f"neo4j-export BLOCKED: {exc}"
        ) from exc
    load_path = Path(projection.output_dir) / "neo4j_load.json"
    load_path.write_text(
        json.dumps(
            {"status": "loaded", **summary},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    click.echo(
        f"loaded nodes: {summary['nodes']} | "
        f"relationships: {summary['relationships']}"
    )
    click.echo(f"neo4j_load: {load_path}")


@agent_system.command("export-event")
@_config_option
@_store_option
@click.option("--event-id", required=True)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path, file_okay=False),
    required=True,
)
def export_event_command(
    config_path: Path,
    store_dir: Path | None,
    event_id: str,
    output_dir: Path,
) -> None:
    """Export one active event without creating a runtime snapshot."""

    config = _load_config(config_path)
    store = _open_store(config, store_dir, create=False)
    try:
        result = export_event(store, event_id, output_dir)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    finally:
        store.close()
    click.echo(f"event_export: {result}")
