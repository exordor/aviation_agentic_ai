"""Sequential, resumable construction of a corpus from advisory records."""

from __future__ import annotations

import shutil
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.agents import parse_structured_fields
from aviation_agentic_ai.agent_system.tmi_profiles import (
    classify_tmi_family,
    get_tmi_profile,
)
from aviation_agentic_ai.agent_system.agent_usage import (
    AgentUsageManifest,
    AgentUsageRecord,
    agent_usage_key,
    build_blocked_agent_usage_records,
    build_agent_usage_records,
    read_agent_usage_manifest,
    read_agent_usage_records,
    write_agent_usage_records,
    write_agent_usage_sidecar,
)
from aviation_agentic_ai.agent_system.authority_evidence import (
    AuthorityBuildStatus,
    LoadedAuthorityCatalog,
    load_authority_catalog,
)
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusBuildManifest,
    CorpusBuildResult,
    build_corpus,
)
from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
from aviation_agentic_ai.agent_system.prompts import (
    DEFAULT_PROMPT_CATALOG,
    get_prompt_catalog,
)
from aviation_agentic_ai.agent_system.runtime import (
    MAX_PROVIDER_CALLS,
    create_run_binding,
    write_run_manifest,
)
from aviation_agentic_ai.agent_system.schema_guide import (
    DEFAULT_SCHEMA_SLICE,
    SchemaGuide,
    load_schema_guide,
)
from aviation_agentic_ai.agent_system.sources import (
    load_bts_context_source,
    load_weather_sources,
)
from aviation_agentic_ai.agent_system.tool_model import make_live_tool_calling_model
from aviation_agentic_ai.agent_system.workflow import IngestContext, run_ingest
from aviation_agentic_ai.config import resolve_project_path
from aviation_agentic_ai.cross_source.artifacts import read_jsonl, write_jsonl
from aviation_agentic_ai.cross_source.evaluation.cohort import select_cross_source_cohort


@dataclass(frozen=True)
class BatchResources:
    """Shared immutable inputs loaded once before eligible cases run."""

    guide: SchemaGuide | Any
    authority_catalog: LoadedAuthorityCatalog | Any
    facility_candidates: list[Any]
    term_candidates: list[Any]
    weather_sources: list[Any]
    bts_rows: list[Any]
    bts_source: Any | None
    bts_manifest_binding: Any | None
    weather_failure_reason: str = ""
    bts_failure_reason: str = ""
    run_started_at: datetime | None = None


@dataclass(frozen=True)
class BatchCaseExecution:
    """The result and transient validated run bundle from one advisory."""

    result: CorpusBuildResult
    run_dir: Path | None = None
    agent_usage_records: tuple[AgentUsageRecord, ...] = ()
    model_calls: tuple[ModelCallRecord, ...] = ()


@dataclass(frozen=True)
class CorpusBatchSummary:
    """Stable user-facing summary of one batch invocation."""

    selected_count: int
    ok_count: int
    insufficient_count: int
    blocked_count: int
    results: tuple[CorpusBuildResult, ...]
    manifest: CorpusBuildManifest | Any | None = None
    agent_usage_manifest: AgentUsageManifest | None = None


ResourceLoader = Callable[[dict[str, Any]], BatchResources]
CaseRunner = Callable[[Any, BatchResources, Path, bool], BatchCaseExecution]
CorpusNormalizer = Callable[..., CorpusBuildManifest]


def build_corpus_batch(
    config: dict[str, Any],
    output_dir: str | Path,
    *,
    selection: str = "cohort",
    source_ids: Sequence[str] = (),
    allow_live_model: bool = False,
    resume: bool = False,
    resource_loader: ResourceLoader = None,  # type: ignore[assignment]
    case_runner: CaseRunner = None,  # type: ignore[assignment]
    corpus_normalizer: CorpusNormalizer = build_corpus,
) -> CorpusBatchSummary:
    """Build selected advisories sequentially and normalize only if all finish.

    ``ok`` and ``insufficient`` results are terminal.  A resumed build retries
    just previously blocked cases and reuses their transient validated bundles.
    """

    selected = _select_advisories(config, selection=selection, source_ids=source_ids)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    staging = output / ".staging"
    manifest_path = output / "corpus_manifest.json"
    if not resume:
        shutil.rmtree(staging, ignore_errors=True)
        manifest_path.unlink(missing_ok=True)
        shutil.rmtree(output / "agent_usage", ignore_errors=True)
    staging.mkdir(parents=True, exist_ok=True)

    previous = _load_previous_results(staging, output) if resume else {}
    selected_source_ids = {str(row["source_id"]) for row in selected}
    if (
        resume
        and _read_manifest(manifest_path) is not None
        and selected_source_ids - previous.keys()
    ):
        raise ValueError(
            "cannot expand a finalized corpus with --resume; "
            "rebuild without --resume"
        )
    run_paths = _load_run_paths(staging) if resume else {}
    usage_records = _load_agent_usage_progress(staging) if resume else {}
    results: dict[str, CorpusBuildResult] = {}
    pending: list[Any] = []
    for advisory in selected:
        source_id = str(advisory["source_id"])
        source = _source_record(advisory)
        prior = previous.get(source_id)
        if prior is not None and prior.status in {"ok", "insufficient"}:
            results[source_id] = _with_tmi_metadata(
                prior,
                source,
                preflight_eligible=(
                    prior.status == "ok" or _preflight(source) is None
                ),
            )
            continue
        preflight = _preflight(source)
        if preflight is not None:
            results[source_id] = preflight
            continue
        pending.append(source)

    if not pending and resume and manifest_path.is_file() and not any(
        result.status == "blocked" for result in results.values()
    ):
        return _summary(
            results,
            manifest=_read_manifest(manifest_path),
            agent_usage_manifest=read_agent_usage_manifest(output),
        )

    if pending:
        manifest_path.unlink(missing_ok=True)

    loader = resource_loader or load_batch_resources
    runner = case_runner or run_batch_case
    resources = loader(config) if pending else None
    for advisory in pending:
        source_id = advisory.source_id
        case_staging = staging / "case_runs" / _safe_path_component(source_id)
        case_staging.mkdir(parents=True, exist_ok=True)
        try:
            execution = runner(advisory, resources, case_staging, allow_live_model)
            result = execution.result
            if result.source_id != source_id:
                raise ValueError("case runner returned a result for another advisory")
            if result.status == "ok" and execution.run_dir is None:
                raise ValueError("ok case runner result is missing a staged run bundle")
            execution = BatchCaseExecution(
                result=_with_tmi_metadata(
                    result,
                    advisory,
                    preflight_eligible=True,
                ),
                run_dir=execution.run_dir,
                agent_usage_records=execution.agent_usage_records,
                model_calls=execution.model_calls,
            )
        except Exception as exc:  # preserve the rest of the independent cohort
            execution = BatchCaseExecution(
                result=CorpusBuildResult(
                    source_id=source_id,
                    status="blocked",
                    reason=f"{type(exc).__name__}: {exc}",
                    tmi_family=classify_tmi_family(advisory.content)
                    or "UNCLASSIFIED",
                    preflight_eligible=True,
                ),
                agent_usage_records=build_blocked_agent_usage_records(
                    source_id=source_id,
                ),
            )
        results[source_id] = execution.result
        for key in tuple(usage_records):
            if key[0] == source_id:
                del usage_records[key]
        normalized_usage = _normalize_case_usage(
            source_id,
            execution.agent_usage_records,
        )
        for usage_record in normalized_usage:
            usage_records[agent_usage_key(usage_record)] = usage_record
        if execution.result.status == "ok" and execution.run_dir is not None:
            run_paths[source_id] = str(execution.run_dir)
        elif execution.result.status != "ok":
            run_paths.pop(source_id, None)
        _persist_progress(staging, output, results, run_paths, usage_records)

    _persist_progress(staging, output, results, run_paths, usage_records)
    if any(result.status == "blocked" for result in results.values()):
        manifest_path.unlink(missing_ok=True)
        return _summary(results)

    ordered_results = _ordered_results(results)
    successful_runs = [
        Path(run_paths[source_id])
        for source_id, result in sorted(results.items())
        if result.status == "ok" and source_id in run_paths
    ]
    manifest = corpus_normalizer(
        run_dirs=successful_runs,
        output_dir=output,
        build_results=ordered_results,
    )
    corpus_id = _corpus_id(manifest)
    usage_manifest = (
        write_agent_usage_sidecar(
            output,
            corpus_id=corpus_id,
            records=tuple(usage_records.values()),
        )
        if corpus_id is not None
        else None
    )
    shutil.rmtree(staging / "case_runs", ignore_errors=True)
    _persist_progress(staging, output, results, {}, usage_records)
    return _summary(
        results,
        manifest=manifest,
        agent_usage_manifest=usage_manifest,
    )


def load_batch_resources(config: dict[str, Any]) -> BatchResources:
    """Load the shared schema, authority, Weather, and BTS inputs once."""

    run_started_at = datetime.now(UTC)
    guide = load_schema_guide()
    authority_catalog = load_authority_catalog(
        config,
        guide=guide,
        schema_guide_path=DEFAULT_SCHEMA_SLICE,
        created_at=run_started_at,
    )
    weather_sources: list[Any] = []
    bts_rows: list[Any] = []
    bts_source: Any | None = None
    bts_manifest_binding: Any | None = None
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
    return BatchResources(
        guide=guide,
        authority_catalog=authority_catalog,
        facility_candidates=facilities,
        term_candidates=terms,
        weather_sources=weather_sources,
        bts_rows=bts_rows,
        bts_source=bts_source,
        bts_manifest_binding=bts_manifest_binding,
        weather_failure_reason=weather_failure_reason,
        bts_failure_reason=bts_failure_reason,
        run_started_at=run_started_at,
    )


def run_batch_case(
    advisory: Any,
    resources: BatchResources,
    staging_dir: Path,
    allow_live_model: bool,
) -> BatchCaseExecution:
    """Run the existing workflow once, retaining its bundle only when valid."""

    source_id = advisory.source_id
    family = classify_tmi_family(advisory.content) or "UNCLASSIFIED"
    if not allow_live_model:
        return BatchCaseExecution(
            result=CorpusBuildResult(
                source_id=source_id,
                status="blocked",
                reason="build-corpus requires --allow-live-model for eligible advisories",
                tmi_family=family,
                preflight_eligible=True,
            )
        )
    binding = create_run_binding(
        staging_dir,
        source_id,
        started_at=resources.run_started_at,
    )
    catalog = get_prompt_catalog(DEFAULT_PROMPT_CATALOG)
    context = IngestContext(
        advisory=advisory,
        facility_candidates=resources.facility_candidates,
        term_candidates=resources.term_candidates,
        weather_sources=resources.weather_sources,
        bts_rows=resources.bts_rows,
        bts_source=resources.bts_source,
        bts_manifest_binding=resources.bts_manifest_binding,
        weather_failure_reason=resources.weather_failure_reason,
        bts_failure_reason=resources.bts_failure_reason,
        guide=resources.guide,
        semantic_resolution_tool_model_factory=lambda tools: make_live_tool_calling_model(
            tools=tools,
            role="semantic_resolution",
            catalog_path=DEFAULT_PROMPT_CATALOG,
        ),
        event_evidence_integration_model_factory=lambda tools: make_live_tool_calling_model(
            tools=tools,
            role="event_evidence_integration",
            catalog_path=DEFAULT_PROMPT_CATALOG,
        ),
        authority_catalog=resources.authority_catalog,
        run_started_at=binding.run_started_at,
        run_id=binding.run_id,
        output_dir=str(binding.run_dir),
    )
    state = run_ingest(context)
    agent_usage_records = build_agent_usage_records(
        source_id=source_id,
        state=state,
    )
    model_calls = state.get("model_calls", [])
    if len(model_calls) > MAX_PROVIDER_CALLS:
        raise ValueError(f"provider calls exceeded hard maximum {MAX_PROVIDER_CALLS}")
    materialization = state.get("materialization")
    if materialization is None:
        return BatchCaseExecution(
            result=CorpusBuildResult(
                source_id=source_id,
                status="insufficient",
                reason=str(
                    state.get("integration_failure_reason")
                    or state.get("resolution_preflight_reason")
                    or "workflow did not publish validated TMI event evidence"
                ),
                provider_call_count=len(model_calls),
                tmi_family=family,
                preflight_eligible=True,
            ),
            agent_usage_records=agent_usage_records,
            model_calls=tuple(model_calls),
        )
    validation = state.get("validation")
    graph_patch = state.get("integration_graph_patch")
    evidence_cards = [
        getattr(result, "evidence_card", result)
        for result in (
            state.get("advisory_evidence"),
            state.get("facility_authority_result"),
            state.get("terminology_authority_result"),
        )
        if result and getattr(result, "evidence_card", result)
    ]
    write_run_manifest(
        run_dir=binding.run_dir,
        source_id=source_id,
        model_calls=model_calls,
        materialization=materialization,
        schema_slice_id=resources.guide.schema_slice_id,
        schema_checksum=resources.guide.checksum,
        evidence_cards=evidence_cards,
        graph_patch_raw=graph_patch.raw if graph_patch else None,
        prompt_set_id=catalog.prompt_set_id,
        profile_gap_count=len(validation.profile_gaps) if validation else 0,
        context_artifacts=state.get("context_artifacts", {}),
        formal_layers=state.get("formal_layers", {}),
        public_observation_publication=state.get("public_observation_publication", {}),
        catalog_path=DEFAULT_PROMPT_CATALOG,
        created_at=binding.run_started_at,
    )
    event_id = state.get("event_uri")
    return BatchCaseExecution(
        result=CorpusBuildResult(
            source_id=source_id,
            status="ok",
            event_id=event_id,
            reason="validated run staged",
            provider_call_count=len(model_calls),
            tmi_family=family,
            preflight_eligible=True,
        ),
        run_dir=binding.run_dir,
        agent_usage_records=agent_usage_records,
        model_calls=tuple(model_calls),
    )


def _select_advisories(
    config: dict[str, Any],
    *,
    selection: str,
    source_ids: Sequence[str],
) -> list[dict[str, Any]]:
    advisories = read_jsonl(resolve_project_path(config["sources"]["atcscc_advisories"]))
    if selection == "cohort":
        selected = select_cross_source_cohort(
            advisories,
            airport_codes=config["cohort"]["airport_codes"],
            expected_count=int(config["cohort"]["expected_record_count"]),
        ).records
    elif selection == "all":
        selected = advisories
    else:
        raise ValueError("selection must be 'cohort' or 'all'")
    requested = set(source_ids)
    available = {str(row.get("source_id") or "") for row in selected}
    unknown = sorted(requested - available)
    if unknown:
        raise ValueError(f"source_id is not in selected advisories: {unknown[0]}")
    return [row for row in selected if not requested or str(row["source_id"]) in requested]


def _preflight(advisory: Any) -> CorpusBuildResult | None:
    source_id = advisory.source_id
    mentions = parse_structured_fields(advisory.content)
    family = classify_tmi_family(advisory.content)
    profile = get_tmi_profile(family or "")
    if profile is None:
        return CorpusBuildResult(
            source_id=source_id,
            status="insufficient",
            reason="unsupported traffic-management initiative",
            tmi_family=family or "UNCLASSIFIED",
            preflight_eligible=False,
        )
    if profile.publication_status == "deferred":
        return CorpusBuildResult(
            source_id=source_id,
            status="insufficient",
            reason="deferred traffic-management lifecycle event",
            tmi_family=family,
            preflight_eligible=False,
        )
    if profile.publication_status == "boundary":
        return CorpusBuildResult(
            source_id=source_id,
            status="insufficient",
            reason="recognized advisory family outside active publication profile",
            tmi_family=family,
            preflight_eligible=False,
        )
    if any(not getattr(mentions, field, None) for field in profile.required_fields):
        return CorpusBuildResult(
            source_id=source_id,
            status="insufficient",
            reason="incomplete core advisory fields",
            tmi_family=family,
            preflight_eligible=False,
        )
    return None


def _with_tmi_metadata(
    result: CorpusBuildResult,
    advisory: Any,
    *,
    preflight_eligible: bool,
) -> CorpusBuildResult:
    """Bind a runner result to the deterministic source-family classification."""

    family = classify_tmi_family(advisory.content) or "UNCLASSIFIED"
    return result.model_copy(
        update={
            "tmi_family": result.tmi_family or family,
            "preflight_eligible": (
                result.preflight_eligible
                if result.preflight_eligible is not None
                else preflight_eligible
            ),
        }
    )


def _source_record(row: dict[str, Any]) -> Any:
    from aviation_agentic_ai.agent_system.contracts import SourceFamily, SourceRecord

    source_id = str(row.get("source_id") or "")
    return SourceRecord(
        source_id=source_id,
        family=SourceFamily.ATCSCC_ADVISORY,
        content=str(row.get("text") or " "),
        title=str(row.get("title") or row.get("advisory_number") or source_id),
        source_url=str(row.get("source_url") or "") or None,
    )


def _persist_progress(
    staging: Path,
    output: Path,
    results: dict[str, CorpusBuildResult],
    run_paths: dict[str, str],
    usage_records: dict[
        tuple[str, str, str],
        AgentUsageRecord,
    ],
) -> None:
    rows = [row.model_dump(mode="json") for row in _ordered_results(results)]
    write_jsonl(staging / "build_results.jsonl", rows)
    write_jsonl(output / "build_results.jsonl", rows)
    write_jsonl(
        staging / "run_paths.jsonl",
        [
            {"source_id": source_id, "run_dir": run_dir}
            for source_id, run_dir in sorted(run_paths.items())
        ],
    )
    write_agent_usage_records(
        staging / "agent_usage.jsonl",
        tuple(usage_records.values()),
    )


def _load_previous_results(staging: Path, output: Path) -> dict[str, CorpusBuildResult]:
    for path in (staging / "build_results.jsonl", output / "build_results.jsonl"):
        if path.is_file():
            return {
                result.source_id: result
                for result in (
                    CorpusBuildResult.model_validate(row) for row in read_jsonl(path)
                )
            }
    return {}


def _load_run_paths(staging: Path) -> dict[str, str]:
    path = staging / "run_paths.jsonl"
    if not path.is_file():
        return {}
    return {
        str(row["source_id"]): str(row["run_dir"])
        for row in read_jsonl(path)
        if row.get("source_id") and row.get("run_dir")
    }


def _load_agent_usage_progress(
    staging: Path,
) -> dict[tuple[str, str, str], AgentUsageRecord]:
    return {
        agent_usage_key(record): record
        for record in read_agent_usage_records(staging / "agent_usage.jsonl")
    }


def _normalize_case_usage(
    source_id: str,
    records: tuple[AgentUsageRecord, ...],
) -> tuple[AgentUsageRecord, ...]:
    expected = {
        ("semantic_resolution", "facility"),
        ("semantic_resolution", "terminology"),
        ("event_evidence_integration", "tmi_event_evidence"),
    }
    keys = {(row.role, row.task_scope) for row in records}
    if (
        len(records) == 3
        and len(keys) == 3
        and keys == expected
        and all(row.source_id == source_id for row in records)
    ):
        return records
    return build_blocked_agent_usage_records(
        source_id=source_id,
        activation_reason="workflow_usage_missing_or_invalid",
    )


def _ordered_results(results: dict[str, CorpusBuildResult]) -> list[CorpusBuildResult]:
    return [results[source_id] for source_id in sorted(results)]


def _summary(
    results: dict[str, CorpusBuildResult],
    *,
    manifest: CorpusBuildManifest | Any | None = None,
    agent_usage_manifest: AgentUsageManifest | None = None,
) -> CorpusBatchSummary:
    ordered = tuple(_ordered_results(results))
    return CorpusBatchSummary(
        selected_count=len(ordered),
        ok_count=sum(result.status == "ok" for result in ordered),
        insufficient_count=sum(result.status == "insufficient" for result in ordered),
        blocked_count=sum(result.status == "blocked" for result in ordered),
        results=ordered,
        manifest=manifest,
        agent_usage_manifest=agent_usage_manifest,
    )


def _read_manifest(path: Path) -> CorpusBuildManifest | None:
    try:
        return CorpusBuildManifest.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _corpus_id(manifest: CorpusBuildManifest | Any) -> str | None:
    value = (
        manifest.get("corpus_id")
        if isinstance(manifest, dict)
        else getattr(manifest, "corpus_id", None)
    )
    return str(value) if value else None


def _safe_path_component(source_id: str) -> str:
    return source_id.replace("/", "_").replace(":", "_")
