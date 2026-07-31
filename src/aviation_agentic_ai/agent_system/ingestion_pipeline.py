"""Sequential ingestion from configured source records into the evidence store."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from aviation_agentic_ai.agent_system.agent_usage import (
    AgentUsageRecord,
    build_agent_usage_records,
    build_blocked_agent_usage_records,
)
from aviation_agentic_ai.agent_system.agents import parse_structured_fields
from aviation_agentic_ai.agent_system.authority_evidence import (
    AuthorityBuildStatus,
    LoadedAuthorityCatalog,
    load_authority_catalog,
)
from aviation_agentic_ai.agent_system.contracts import (
    BTSManifestBinding,
    BTSOnTimeRow,
    SourceFamily,
    SourceRecord,
)
from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.ingestion_package import (
    IngestionAttempt,
)
from aviation_agentic_ai.agent_system.prompts import DEFAULT_PROMPT_CATALOG
from aviation_agentic_ai.agent_system.schema_guide import (
    DEFAULT_SCHEMA_SLICE,
    SchemaGuide,
    load_schema_guide,
)
from aviation_agentic_ai.agent_system.sources import (
    build_source_version,
    discover_source_assets,
    load_bts_context_source,
    load_weather_sources,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    IngestionResult,
    SourceAssetRecord,
    SourceVersionRecord,
    TMIEventQuery,
)
from aviation_agentic_ai.agent_system.tmi_profiles import (
    classify_tmi_family,
    get_tmi_profile,
)
from aviation_agentic_ai.agent_system.tool_model import (
    make_live_tool_calling_model,
)
from aviation_agentic_ai.agent_system.workflow import IngestContext, run_ingest
from aviation_agentic_ai.config import resolve_project_path
from aviation_agentic_ai.utils.identifiers import stable_id


@dataclass(frozen=True)
class IngestionResources:
    """Shared immutable inputs loaded once for one ingestion invocation."""

    guide: SchemaGuide | Any
    authority_catalog: LoadedAuthorityCatalog | Any
    facility_candidates: tuple[Any, ...]
    term_candidates: tuple[Any, ...]
    weather_sources: tuple[SourceRecord, ...]
    bts_rows: tuple[BTSOnTimeRow, ...]
    bts_source: SourceRecord | None
    bts_manifest_binding: BTSManifestBinding | None
    logical_sources: tuple[SourceRecord, ...]
    weather_failure_reason: str = ""
    bts_failure_reason: str = ""
    run_started_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True)
class IngestionCaseExecution:
    """One workflow outcome plus source versions registered before publication."""

    attempt: IngestionAttempt
    source_versions: tuple[SourceVersionRecord, ...]
    agent_usage_records: tuple[AgentUsageRecord, ...] = ()


@dataclass(frozen=True)
class AdvisoryPreflightResult:
    """Deterministic admission outcome before any Agent is activated."""

    status: str
    reason: str
    tmi_family: str
    preflight_eligible: bool


@dataclass(frozen=True)
class IngestionSummary:
    """Compact outcome of one incremental ingestion invocation."""

    discovered_count: int
    selected_count: int
    attempted_count: int
    skipped_count: int
    ok_count: int
    insufficient_count: int
    blocked_count: int
    results: tuple[IngestionResult, ...]


ResourceLoader = Callable[[dict[str, Any]], IngestionResources]
CaseRunner = Callable[
    [SourceRecord, IngestionResources, bool],
    IngestionCaseExecution,
]
AssetDiscoverer = Callable[[dict[str, Any]], tuple[SourceAssetRecord, ...]]


class RetrievalIndexer(Protocol):
    """Derived-index update boundary kept outside semantic transactions."""

    def __call__(
        self,
        store: AviationEvidenceStore,
        *,
        source_version_ids: Sequence[str],
        event_publication_ids: Sequence[str],
        allow_model_download: bool,
        model_name: str,
    ) -> object: ...


def load_ingestion_resources(config: dict[str, Any]) -> IngestionResources:
    """Load schema, authority, Weather, and BTS inputs exactly once."""

    run_started_at = datetime.now(UTC)
    guide = load_schema_guide()
    authority_catalog = load_authority_catalog(
        config,
        guide=guide,
        schema_guide_path=DEFAULT_SCHEMA_SLICE,
        created_at=run_started_at,
    )
    weather_sources: tuple[SourceRecord, ...] = ()
    bts_rows: tuple[BTSOnTimeRow, ...] = ()
    bts_source: SourceRecord | None = None
    bts_manifest_binding: BTSManifestBinding | None = None
    weather_failure_reason = ""
    bts_failure_reason = ""
    try:
        weather_sources = tuple(load_weather_sources(config))
    except (OSError, TypeError, ValueError) as exc:
        weather_failure_reason = str(exc)
    try:
        loaded_source, loaded_rows, loaded_binding = load_bts_context_source(
            config
        )
        bts_source = loaded_source
        bts_rows = tuple(loaded_rows)
        bts_manifest_binding = loaded_binding
    except (OSError, TypeError, ValueError) as exc:
        bts_failure_reason = str(exc)
    facilities = (
        tuple(authority_catalog.facility.entities)
        if authority_catalog.facility.status is AuthorityBuildStatus.OK
        else ()
    )
    terms = (
        tuple(authority_catalog.terminology.registry_terms)
        if authority_catalog.terminology.status is AuthorityBuildStatus.OK
        else ()
    )
    logical_sources = (
        *weather_sources,
        *((bts_source,) if bts_source is not None else ()),
    )
    return IngestionResources(
        guide=guide,
        authority_catalog=authority_catalog,
        facility_candidates=facilities,
        term_candidates=terms,
        weather_sources=weather_sources,
        bts_rows=bts_rows,
        bts_source=bts_source,
        bts_manifest_binding=bts_manifest_binding,
        logical_sources=logical_sources,
        weather_failure_reason=weather_failure_reason,
        bts_failure_reason=bts_failure_reason,
        run_started_at=run_started_at,
    )


def run_ingestion_pipeline(
    config: dict[str, object],
    store: AviationEvidenceStore,
    *,
    source_ids: tuple[str, ...] = (),
    allow_live_model: bool = False,
    allow_model_download: bool = False,
    resource_loader: ResourceLoader | None = None,
    case_runner: CaseRunner | None = None,
    asset_discoverer: AssetDiscoverer = discover_source_assets,
    retrieval_indexer: RetrievalIndexer | None = None,
) -> IngestionSummary:
    """Register configured evidence, then process selected advisories one by one.

    ``source_ids`` bounds only advisory event construction. The first pass
    still registers every configured advisory version, and shared logical
    sources are registered before the first semantic publication.
    """

    typed_config = dict(config)
    changed_source_version_ids: set[str] = set()
    changed_event_publication_ids: set[str] = set()
    assets = asset_discoverer(typed_config)
    for asset in assets:
        store.register_source_asset(asset)
    assets_by_key = {asset.asset_key: asset for asset in assets}

    discovered_count = 0
    available_source_ids: set[str] = set()
    for advisory in _iter_advisories(typed_config, assets_by_key):
        discovered_count += 1
        available_source_ids.add(advisory.source_id)
        advisory_version = build_source_version(advisory)
        if store.register_source_version(advisory_version) == "inserted":
            changed_source_version_ids.add(
                advisory_version.source_version_id
            )
    requested = set(source_ids)
    unknown = sorted(requested - available_source_ids)
    if unknown:
        raise ValueError(f"source_id is not in configured advisories: {unknown[0]}")

    loader = resource_loader or load_ingestion_resources
    resources = loader(typed_config)
    for record in resources.logical_sources:
        bound_record = _bind_logical_source_asset(record, assets_by_key)
        source_version = build_source_version(bound_record)
        if store.register_source_version(source_version) == "inserted":
            changed_source_version_ids.add(
                source_version.source_version_id
            )

    selected_count = (
        discovered_count if not requested else len(requested)
    )
    run_started_at = datetime.now(UTC)
    ingestion_run_id = stable_id(
        "ingestion-run",
        store.dataset_id,
        run_started_at.isoformat(),
    )
    store.start_ingestion_run(
        ingestion_run_id,
        started_at=run_started_at,
    )

    runner = case_runner or _run_case
    attempted_count = 0
    skipped_count = 0
    results: list[IngestionResult] = []
    for advisory in _iter_advisories(typed_config, assets_by_key):
        if requested and advisory.source_id not in requested:
            continue
        advisory_version = build_source_version(advisory)
        previous = store.get_ingestion_result(
            advisory_version.source_version_id
        )
        if previous is not None and previous.status in {"ok", "insufficient"}:
            skipped_count += 1
            results.append(previous)
            continue

        attempted_count += 1
        preflight = _preflight_result(advisory, advisory_version)
        if preflight is not None:
            attempt = IngestionAttempt(result=preflight, package=None)
            store.apply_ingestion_attempt(attempt)
            results.append(preflight)
            continue

        usage_records: tuple[AgentUsageRecord, ...] = ()
        try:
            execution = runner(advisory, resources, allow_live_model)
            usage_records = execution.agent_usage_records
            for version in execution.source_versions:
                bound_version = _bind_source_version_asset(
                    version,
                    assets_by_key,
                )
                if (
                    store.register_source_version(bound_version)
                    == "inserted"
                ):
                    changed_source_version_ids.add(
                        bound_version.source_version_id
                    )
            if (
                execution.attempt.result.source_version_id
                != advisory_version.source_version_id
            ):
                raise ValueError(
                    "case runner returned a result for another source version"
                )
            store.apply_ingestion_attempt(execution.attempt)
            result = execution.attempt.result
            if result.status == "ok" and result.publication_id is not None:
                changed_event_publication_ids.add(result.publication_id)
        except Exception as exc:
            provider_call_count = sum(
                row.provider_call_count for row in usage_records
            )
            result = IngestionResult(
                source_version_id=advisory_version.source_version_id,
                source_id=advisory.source_id,
                status="blocked",
                event_id=None,
                publication_id=None,
                reason=f"{type(exc).__name__}: {exc}",
                provider_call_count=provider_call_count,
                tmi_family=classify_tmi_family(advisory.content)
                or "UNCLASSIFIED",
                preflight_eligible=True,
            )
            store.apply_ingestion_attempt(
                IngestionAttempt(result=result, package=None)
            )
            if usage_records:
                usage_records = tuple(
                    row.model_copy(
                        update={
                            "outcome": "blocked",
                            "detail_status": (
                                f"publication_failed:{type(exc).__name__}"
                            ),
                        }
                    )
                    for row in usage_records
                )
            else:
                usage_records = build_blocked_agent_usage_records(
                    source_id=advisory.source_id
                )
        store.replace_agent_usage(ingestion_run_id, usage_records)
        results.append(result)

    summary = _summarize(
        discovered_count=discovered_count,
        selected_count=selected_count,
        attempted_count=attempted_count,
        skipped_count=skipped_count,
        results=results,
    )
    store.finish_ingestion_run(
        ingestion_run_id,
        ended_at=datetime.now(UTC),
        status="blocked" if summary.blocked_count else "completed",
        attempted_count=summary.attempted_count,
        ok_count=summary.ok_count,
        insufficient_count=summary.insufficient_count,
        blocked_count=summary.blocked_count,
    )
    if changed_source_version_ids or changed_event_publication_ids:
        indexer = retrieval_indexer or _update_retrieval_indexes
        try:
            indexer(
                store,
                source_version_ids=tuple(
                    sorted(changed_source_version_ids)
                ),
                event_publication_ids=tuple(
                    sorted(changed_event_publication_ids)
                ),
                allow_model_download=allow_model_download,
                model_name=_embedding_model_name(typed_config),
            )
        except Exception:
            # Semantic publication is authoritative and already committed.
            # The default indexer records its own rebuildable failure state.
            pass
    return summary


def _embedding_model_name(config: dict[str, Any]) -> str:
    from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
        DEFAULT_TMI_EVENT_EMBEDDING_MODEL,
    )

    agent_system = config.get("agent_system")
    if not isinstance(agent_system, dict):
        return DEFAULT_TMI_EVENT_EMBEDDING_MODEL
    storage = agent_system.get("storage")
    if not isinstance(storage, dict):
        return DEFAULT_TMI_EVENT_EMBEDDING_MODEL
    configured = storage.get("embedding_model")
    return (
        configured
        if isinstance(configured, str) and configured
        else DEFAULT_TMI_EVENT_EMBEDDING_MODEL
    )


def _update_retrieval_indexes(
    store: AviationEvidenceStore,
    *,
    source_version_ids: Sequence[str],
    event_publication_ids: Sequence[str],
    allow_model_download: bool,
    model_name: str,
) -> object:
    from aviation_agentic_ai.agent_system.source_retrieval import (
        build_source_record_chunks,
    )
    from aviation_agentic_ai.agent_system.tmi_event_retrieval_index import (
        SentenceTransformerTMIEventEncoder,
        mark_vector_indexes_blocked,
        update_store_indexes,
    )

    source_versions = tuple(
        version
        for source_version_id in source_version_ids
        if (
            version := store.get_source_version(source_version_id)
        )
        is not None
    )
    store.upsert_source_chunks(
        build_source_record_chunks(source_versions)
    )
    try:
        encoder = SentenceTransformerTMIEventEncoder(
            model_name,
            allow_download=allow_model_download,
        )
    except Exception as exc:
        return mark_vector_indexes_blocked(
            store,
            embedding_model_id=model_name,
            reason=f"{type(exc).__name__}: {exc}",
        )
    try:
        return update_store_indexes(
            store,
            Path(store.root) / "chroma",
            encoder=encoder,
            source_version_ids=source_version_ids,
            event_publication_ids=event_publication_ids,
        )
    except Exception:
        return ()


def _run_case(
    advisory: SourceRecord,
    resources: IngestionResources,
    allow_live_model: bool,
) -> IngestionCaseExecution:
    """Execute the existing bounded workflow without creating run artifacts."""

    context = IngestContext(
        advisory=advisory,
        facility_candidates=list(resources.facility_candidates),
        term_candidates=list(resources.term_candidates),
        weather_sources=list(resources.weather_sources),
        bts_rows=list(resources.bts_rows),
        bts_source=resources.bts_source,
        bts_manifest_binding=resources.bts_manifest_binding,
        weather_failure_reason=resources.weather_failure_reason,
        bts_failure_reason=resources.bts_failure_reason,
        guide=resources.guide,
        semantic_resolution_tool_model_factory=(
            (
                lambda tools: make_live_tool_calling_model(
                    tools=tools,
                    role="semantic_resolution",
                    catalog_path=DEFAULT_PROMPT_CATALOG,
                )
            )
            if allow_live_model
            else None
        ),
        authority_catalog=resources.authority_catalog,
        run_started_at=resources.run_started_at,
        run_id=stable_id(
            "ingestion-task",
            advisory.source_id,
            resources.run_started_at.isoformat(),
        ),
    )
    state = run_ingest(context)
    model_calls = tuple(state.get("model_calls") or ())
    package = state.get("ingestion_package")
    versions = tuple(state.get("source_versions") or ())
    if not versions:
        versions = (build_source_version(advisory),)
    family = classify_tmi_family(advisory.content) or "UNCLASSIFIED"
    if package is not None:
        result = IngestionResult(
            source_version_id=build_source_version(
                advisory
            ).source_version_id,
            source_id=advisory.source_id,
            status="ok",
            event_id=package.event.event_id,
            publication_id=package.event.publication_id,
            reason="formal publication accepted",
            provider_call_count=len(model_calls),
            tmi_family=family,
            preflight_eligible=True,
        )
    else:
        blocked = (
            state.get("publication_status") == "blocked"
            or state.get("resolution_preflight_status") == "blocked"
        )
        result = IngestionResult(
            source_version_id=build_source_version(
                advisory
            ).source_version_id,
            source_id=advisory.source_id,
            status="blocked" if blocked else "insufficient",
            event_id=None,
            publication_id=None,
            reason=str(
                state.get("publication_failure_reason")
                or state.get("integration_failure_reason")
                or state.get("resolution_preflight_reason")
                or "workflow did not publish a TMI event"
            ),
            provider_call_count=len(model_calls),
            tmi_family=family,
            preflight_eligible=True,
        )
    return IngestionCaseExecution(
        attempt=IngestionAttempt(result=result, package=package),
        source_versions=versions,
        agent_usage_records=build_agent_usage_records(
            source_id=advisory.source_id,
            state=state,
        ),
    )


def _iter_advisories(
    config: dict[str, Any],
    assets_by_key: dict[str, SourceAssetRecord],
) -> Iterator[SourceRecord]:
    sources = config.get("sources")
    if not isinstance(sources, dict):
        raise ValueError("config.sources must be a mapping")
    configured = sources.get("atcscc_advisories")
    if not isinstance(configured, str) or not configured:
        raise ValueError("ATCSCC advisory source is not configured")
    asset = assets_by_key.get("atcscc_advisories")
    path = resolve_project_path(configured)
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"invalid advisory JSON at line {line_number}"
                ) from exc
            if not isinstance(row, dict):
                raise ValueError(
                    f"advisory row must be an object at line {line_number}"
                )
            source_id = str(row.get("source_id") or "")
            text = str(row.get("text") or "")
            yield SourceRecord(
                source_id=source_id,
                family=SourceFamily.ATCSCC_ADVISORY,
                content=text,
                title=str(
                    row.get("title")
                    or row.get("advisory_number")
                    or source_id
                ),
                source_url=str(row.get("source_url") or "") or None,
                asset_id=asset.asset_id if asset is not None else None,
                metadata={
                    key: value
                    for key, value in row.items()
                    if key not in {"text", "source_url"}
                },
            )


def _bind_logical_source_asset(
    record: SourceRecord,
    assets_by_key: dict[str, SourceAssetRecord],
) -> SourceRecord:
    if record.asset_id is not None:
        return record
    asset_key = {
        SourceFamily.METAR: "metar",
        SourceFamily.TAF: "taf",
        SourceFamily.BTS_ON_TIME: "bts_on_time_snapshot",
        SourceFamily.NASR_FACILITY: "nasr_zip",
        SourceFamily.FAA_TERM: "term_seed",
        SourceFamily.ATCSCC_ADVISORY: "atcscc_advisories",
    }[record.family]
    asset = assets_by_key.get(asset_key)
    return record.model_copy(
        update={"asset_id": asset.asset_id if asset is not None else None}
    )


def _bind_source_version_asset(
    version: SourceVersionRecord,
    assets_by_key: dict[str, SourceAssetRecord],
) -> SourceVersionRecord:
    """Apply the configured asset binding before immutable registration."""

    if version.asset_id is not None:
        return version
    asset_key = {
        SourceFamily.METAR: "metar",
        SourceFamily.TAF: "taf",
        SourceFamily.BTS_ON_TIME: "bts_on_time_snapshot",
        SourceFamily.NASR_FACILITY: "nasr_zip",
        SourceFamily.FAA_TERM: "term_seed",
        SourceFamily.ATCSCC_ADVISORY: "atcscc_advisories",
    }[version.family]
    asset = assets_by_key.get(asset_key)
    if asset is None:
        return version
    return version.model_copy(update={"asset_id": asset.asset_id})


def _preflight_result(
    advisory: SourceRecord,
    version: SourceVersionRecord,
) -> IngestionResult | None:
    preflight = preflight_advisory(advisory)
    if preflight is None:
        return None
    return IngestionResult(
        source_version_id=version.source_version_id,
        source_id=advisory.source_id,
        status="insufficient",
        event_id=None,
        publication_id=None,
        reason=preflight.reason,
        provider_call_count=0,
        tmi_family=preflight.tmi_family,
        preflight_eligible=False,
    )


def preflight_advisory(
    advisory: SourceRecord,
) -> AdvisoryPreflightResult | None:
    """Classify unsupported or incomplete advisories without a model call."""

    mentions = parse_structured_fields(advisory.content)
    family = classify_tmi_family(advisory.content)
    profile = get_tmi_profile(family or "")
    reason: str | None = None
    if profile is None:
        reason = "unsupported traffic-management initiative"
    elif profile.publication_status == "deferred":
        reason = "deferred traffic-management lifecycle event"
    elif profile.publication_status == "boundary":
        reason = (
            "recognized advisory family outside active publication profile"
        )
    elif any(
        not getattr(mentions, field, None)
        for field in profile.required_fields
    ):
        reason = "incomplete core advisory fields"
    if reason is None:
        return None
    return AdvisoryPreflightResult(
        status="insufficient",
        reason=reason,
        tmi_family=family or "UNCLASSIFIED",
        preflight_eligible=False,
    )


def _summarize(
    *,
    discovered_count: int,
    selected_count: int,
    attempted_count: int,
    skipped_count: int,
    results: Sequence[IngestionResult],
) -> IngestionSummary:
    ordered = tuple(sorted(results, key=lambda row: row.source_id))
    return IngestionSummary(
        discovered_count=discovered_count,
        selected_count=selected_count,
        attempted_count=attempted_count,
        skipped_count=skipped_count,
        ok_count=sum(row.status == "ok" for row in ordered),
        insufficient_count=sum(
            row.status == "insufficient" for row in ordered
        ),
        blocked_count=sum(row.status == "blocked" for row in ordered),
        results=ordered,
    )


__all__ = [
    "AdvisoryPreflightResult",
    "IngestionCaseExecution",
    "IngestionResources",
    "IngestionSummary",
    "TMIEventQuery",
    "load_ingestion_resources",
    "preflight_advisory",
    "run_ingestion_pipeline",
]
