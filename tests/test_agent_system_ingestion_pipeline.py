"""Incremental ingestion contracts for the ingestion-first runtime."""

from __future__ import annotations

import importlib
import hashlib
import json
from collections.abc import Callable
from pathlib import Path

from aviation_agentic_ai.agent_system.agent_usage import AgentUsageRecord
from aviation_agentic_ai.agent_system.contracts import SourceFamily, SourceRecord
from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.ingestion_package import (
    EventFactMembership,
    EventIngestionPackage,
    IngestionAttempt,
)
from aviation_agentic_ai.agent_system.sources import build_source_version
from aviation_agentic_ai.agent_system.storage_contracts import (
    IngestionResult,
    SourceAssetRecord,
    TMIEventRecord,
)
from aviation_agentic_ai.utils.identifiers import stable_id


def _pipeline_api():
    return importlib.import_module(
        "aviation_agentic_ai.agent_system.ingestion_pipeline"
    )


def _eligible_advisory(source_id: str, *, suffix: str = "") -> dict[str, str]:
    return {
        "source_id": source_id,
        "title": source_id,
        "text": (
            "ATCSCC ADVZY 001 JFK/ZNY 05/19/2026 GROUND STOP "
            "CTL ELEMENT: JFK GROUND STOP PERIOD: 19/2100Z - 19/2245Z "
            "PROBABILITY OF EXTENSION: MEDIUM "
            f"SIGNATURE: 26/05/19 20:30 {suffix}"
        ).strip(),
    }


def _unsupported_advisory(source_id: str) -> dict[str, str]:
    return {
        "source_id": source_id,
        "title": source_id,
        "text": "ATCSCC ADVZY 001 JFK/ZNY 05/19/2026 ROUTE ADVISORY",
    }


def _write_advisories(path: Path, rows: list[dict[str, str]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _config(path: Path) -> dict[str, object]:
    return {
        "agent_system": {"dataset_id": "test-ingestion"},
        "sources": {"atcscc_advisories": str(path)},
    }


def _resources(api, *, logical_sources: tuple[SourceRecord, ...] = ()):
    return api.IngestionResources(
        guide=None,
        authority_catalog=None,
        facility_candidates=(),
        term_candidates=(),
        weather_sources=(),
        bts_rows=(),
        bts_source=None,
        bts_manifest_binding=None,
        logical_sources=logical_sources,
    )


def _ok_attempt(record: SourceRecord) -> IngestionAttempt:
    version = build_source_version(record)
    event_id = stable_id(
        "evt",
        record.source_id,
        "https://data.nasa.gov/ontologies/atmonto/ATM#GroundStopTMI",
    )
    digest = ("a" * 63) + ("b" if record.content.endswith("REVISED") else "a")
    publication_id = stable_id(
        "event-publication",
        event_id,
        version.source_version_id,
        digest,
    )
    event = TMIEventRecord(
        event_id=event_id,
        publication_id=publication_id,
        advisory_source_id=record.source_id,
        publication_source_version_id=version.source_version_id,
        event_type_iris=(
            "https://data.nasa.gov/ontologies/atmonto/ATM#GroundStopTMI",
        ),
        facility_ids=("urn:aviation-agentic-ai:facility:airport:JFK",),
        effective_start=None,
        effective_end=None,
        issued_at=None,
        reason_status="missing",
        reason_value=None,
    )
    package = EventIngestionPackage(
        event=event,
        formal_publication_digest=digest,
        source_version_ids=(version.source_version_id,),
        source_anchors=(),
        facts=(),
        event_fact_memberships=tuple(
            EventFactMembership(
                event_id=event_id,
                publication_id=publication_id,
                fact_id=fact.fact_id,
            )
            for fact in ()
        ),
        evidence_links=(),
        profile_gaps=(),
        weather_associations=(),
        public_observations=(),
        observation_fact_ids={},
    )
    return IngestionAttempt(
        result=IngestionResult(
            source_version_id=version.source_version_id,
            source_id=record.source_id,
            status="ok",
            event_id=event_id,
            publication_id=publication_id,
            reason="published",
            provider_call_count=0,
            tmi_family="GS",
            preflight_eligible=True,
        ),
        package=package,
    )


def _blocked_attempt(record: SourceRecord) -> IngestionAttempt:
    version = build_source_version(record)
    return IngestionAttempt(
        result=IngestionResult(
            source_version_id=version.source_version_id,
            source_id=record.source_id,
            status="blocked",
            event_id=None,
            publication_id=None,
            reason="runner blocked",
            provider_call_count=1,
            tmi_family="GS",
            preflight_eligible=True,
        ),
        package=None,
    )


def _execution(api, attempt: IngestionAttempt, record: SourceRecord):
    return api.IngestionCaseExecution(
        attempt=attempt,
        source_versions=(build_source_version(record),),
        agent_usage_records=(),
    )


def _run(
    *,
    api,
    config: dict[str, object],
    store: AviationEvidenceStore,
    resources,
    runner: Callable,
    source_ids: tuple[str, ...] = (),
):
    return api.run_ingestion_pipeline(
        config,
        store,
        source_ids=source_ids,
        resource_loader=lambda _config: resources,
        case_runner=runner,
        retrieval_indexer=lambda *_args, **_kwargs: (),
    )


def test_source_filter_limits_construction_but_all_advisories_are_registered(
    tmp_path: Path,
) -> None:
    """Dropping the registration pass would hide the two unselected records."""

    api = _pipeline_api()
    path = tmp_path / "advisories.jsonl"
    rows = [_eligible_advisory(f"source:{index}") for index in range(3)]
    _write_advisories(path, rows)
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-ingestion",
        create=True,
    )
    calls: list[str] = []
    resources = _resources(api)

    def runner(record, _resources, _allow_live_model):  # type: ignore[no-untyped-def]
        calls.append(record.source_id)
        return _execution(api, _ok_attempt(record), record)

    summary = _run(
        api=api,
        config=_config(path),
        store=store,
        resources=resources,
        runner=runner,
        source_ids=("source:1",),
    )

    assert summary.discovered_count == 3
    assert summary.selected_count == 1
    assert calls == ["source:1"]
    assert all(
        store.get_latest_source_version(row["source_id"]) is not None
        for row in rows
    )
    store.close()


def test_shared_resources_load_once_and_are_registered_before_first_case(
    tmp_path: Path,
) -> None:
    """Reloading resources per record or late registration breaks batch semantics."""

    api = _pipeline_api()
    path = tmp_path / "advisories.jsonl"
    _write_advisories(
        path,
        [_eligible_advisory("source:1"), _eligible_advisory("source:2")],
    )
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-ingestion",
        create=True,
    )
    weather = SourceRecord(
        source_id="metar:KJFK:1",
        family=SourceFamily.METAR,
        content="KJFK 192151Z TSRA",
    )
    resources = _resources(api, logical_sources=(weather,))
    resource_loads = 0
    resource_ids: list[int] = []

    def load_resources(_config):  # type: ignore[no-untyped-def]
        nonlocal resource_loads
        resource_loads += 1
        return resources

    def runner(record, loaded, _allow_live_model):  # type: ignore[no-untyped-def]
        resource_ids.append(id(loaded))
        assert store.get_source_version(
            build_source_version(weather).source_version_id
        ) is not None
        return _execution(api, _ok_attempt(record), record)

    summary = api.run_ingestion_pipeline(
        _config(path),
        store,
        resource_loader=load_resources,
        case_runner=runner,
        retrieval_indexer=lambda *_args, **_kwargs: (),
    )

    assert summary.ok_count == 2
    assert resource_loads == 1
    assert resource_ids == [id(resources), id(resources)]
    store.close()


def test_case_versions_reuse_configured_asset_binding(
    tmp_path: Path,
) -> None:
    """Workflow records must match versions registered during resource loading."""

    api = _pipeline_api()
    path = tmp_path / "advisories.jsonl"
    row = _eligible_advisory("source:asset-binding")
    _write_advisories(path, [row])
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-ingestion",
        create=True,
    )
    weather = SourceRecord(
        source_id="metar:KJFK:asset-binding",
        family=SourceFamily.METAR,
        content="KJFK 192151Z TSRA",
    )
    asset_content = b"configured METAR source asset"
    asset_sha256 = hashlib.sha256(asset_content).hexdigest()
    asset = SourceAssetRecord(
        asset_id=stable_id("source-asset", "metar", asset_sha256),
        asset_key="metar",
        family=SourceFamily.METAR,
        local_path=str(tmp_path / "metar.jsonl"),
        source_url=None,
        media_type="application/x-ndjson",
        content_sha256=asset_sha256,
        byte_count=len(asset_content),
        effective_start=None,
        effective_end=None,
    )
    resources = _resources(api, logical_sources=(weather,))

    def runner(record, _resources, _allow_live_model):  # type: ignore[no-untyped-def]
        return api.IngestionCaseExecution(
            attempt=_ok_attempt(record),
            source_versions=(
                build_source_version(record),
                build_source_version(weather),
            ),
            agent_usage_records=(),
        )

    summary = api.run_ingestion_pipeline(
        _config(path),
        store,
        resource_loader=lambda _config: resources,
        case_runner=runner,
        asset_discoverer=lambda _config: (asset,),
        retrieval_indexer=lambda *_args, **_kwargs: (),
    )
    stored_weather = store.get_latest_source_version(weather.source_id)

    assert summary.ok_count == 1
    assert summary.blocked_count == 0
    assert stored_weather is not None
    assert stored_weather.asset_id == asset.asset_id
    store.close()


def test_preflight_insufficient_is_persisted_without_running_case(
    tmp_path: Path,
) -> None:
    """Calling the runner for an unsupported advisory would waste a model call."""

    api = _pipeline_api()
    path = tmp_path / "advisories.jsonl"
    row = _unsupported_advisory("source:unsupported")
    _write_advisories(path, [row])
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-ingestion",
        create=True,
    )
    runner_calls = 0

    def runner(*_args):  # type: ignore[no-untyped-def]
        nonlocal runner_calls
        runner_calls += 1
        raise AssertionError("preflight-insufficient record reached runner")

    summary = _run(
        api=api,
        config=_config(path),
        store=store,
        resources=_resources(api),
        runner=runner,
    )
    version = store.get_latest_source_version("source:unsupported")
    assert version is not None
    result = store.get_ingestion_result(version.source_version_id)

    assert summary.insufficient_count == 1
    assert runner_calls == 0
    assert result is not None
    assert result.provider_call_count == 0
    assert result.preflight_eligible is False
    assert store.find_tmi_events(api.TMIEventQuery()).total_matches == 0
    store.close()


def test_blocked_record_does_not_prevent_later_record_from_committing(
    tmp_path: Path,
) -> None:
    """Stopping on the first blocked record would restore batch publication."""

    api = _pipeline_api()
    path = tmp_path / "advisories.jsonl"
    _write_advisories(
        path,
        [_eligible_advisory("source:blocked"), _eligible_advisory("source:ok")],
    )
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-ingestion",
        create=True,
    )

    def runner(record, _resources, _allow_live_model):  # type: ignore[no-untyped-def]
        attempt = (
            _blocked_attempt(record)
            if record.source_id == "source:blocked"
            else _ok_attempt(record)
        )
        return _execution(api, attempt, record)

    summary = _run(
        api=api,
        config=_config(path),
        store=store,
        resources=_resources(api),
        runner=runner,
    )

    assert summary.blocked_count == 1
    assert summary.ok_count == 1
    assert store.find_tmi_events(api.TMIEventQuery()).total_matches == 1
    store.close()


def test_unchanged_terminal_results_skip_work_but_blocked_results_retry(
    tmp_path: Path,
) -> None:
    """Treating blocked as terminal would make recovery impossible."""

    api = _pipeline_api()
    path = tmp_path / "advisories.jsonl"
    _write_advisories(
        path,
        [
            _eligible_advisory("source:ok"),
            _unsupported_advisory("source:insufficient"),
            _eligible_advisory("source:blocked"),
        ],
    )
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-ingestion",
        create=True,
    )
    calls: list[str] = []

    def runner(record, _resources, _allow_live_model):  # type: ignore[no-untyped-def]
        calls.append(record.source_id)
        attempt = (
            _blocked_attempt(record)
            if record.source_id == "source:blocked"
            else _ok_attempt(record)
        )
        return _execution(api, attempt, record)

    resources = _resources(api)
    _run(
        api=api,
        config=_config(path),
        store=store,
        resources=resources,
        runner=runner,
    )
    _run(
        api=api,
        config=_config(path),
        store=store,
        resources=resources,
        runner=runner,
    )

    assert calls == ["source:ok", "source:blocked", "source:blocked"]
    store.close()


def test_accepted_revision_becomes_active_without_mutating_prior_publication(
    tmp_path: Path,
) -> None:
    """Overwriting an event would make frozen historical reads irreproducible."""

    api = _pipeline_api()
    path = tmp_path / "advisories.jsonl"
    original = _eligible_advisory("source:revision")
    _write_advisories(path, [original])
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-ingestion",
        create=True,
    )

    def runner(record, _resources, _allow_live_model):  # type: ignore[no-untyped-def]
        return _execution(api, _ok_attempt(record), record)

    resources = _resources(api)
    _run(
        api=api,
        config=_config(path),
        store=store,
        resources=resources,
        runner=runner,
    )
    first_version = store.get_latest_source_version("source:revision")
    assert first_version is not None
    first_attempt = _ok_attempt(
        SourceRecord(
            source_id="source:revision",
            family=SourceFamily.ATCSCC_ADVISORY,
            content=original["text"],
            title=original["title"],
        )
    )
    first_publication_id = first_attempt.result.publication_id

    revised = _eligible_advisory("source:revision", suffix="REVISED")
    _write_advisories(path, [revised])
    _run(
        api=api,
        config=_config(path),
        store=store,
        resources=resources,
        runner=runner,
    )

    active = store.get_event(first_attempt.result.event_id or "")
    historical = store.get_event(
        first_attempt.result.event_id or "",
        publication_id=first_publication_id,
    )
    assert active is not None
    assert historical is not None
    assert active.publication_id != historical.publication_id
    assert historical.publication_source_version_id == first_version.source_version_id
    store.close()


def test_blocked_revision_advances_observed_version_not_active_publication(
    tmp_path: Path,
) -> None:
    """A failed revision must not replace the last accepted semantic event."""

    api = _pipeline_api()
    path = tmp_path / "advisories.jsonl"
    original = _eligible_advisory("source:revision")
    _write_advisories(path, [original])
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-ingestion",
        create=True,
    )
    resources = _resources(api)

    def accepted_runner(record, _resources, _allow_live_model):  # type: ignore[no-untyped-def]
        return _execution(api, _ok_attempt(record), record)

    _run(
        api=api,
        config=_config(path),
        store=store,
        resources=resources,
        runner=accepted_runner,
    )
    accepted_attempt = _ok_attempt(
        SourceRecord(
            source_id="source:revision",
            family=SourceFamily.ATCSCC_ADVISORY,
            content=original["text"],
            title=original["title"],
        )
    )
    accepted_publication_id = accepted_attempt.result.publication_id

    revised = _eligible_advisory("source:revision", suffix="REVISED")
    _write_advisories(path, [revised])

    def blocked_runner(record, _resources, _allow_live_model):  # type: ignore[no-untyped-def]
        return _execution(api, _blocked_attempt(record), record)

    _run(
        api=api,
        config=_config(path),
        store=store,
        resources=resources,
        runner=blocked_runner,
    )

    latest = store.get_latest_source_version("source:revision")
    active = store.get_event(accepted_attempt.result.event_id or "")
    assert latest is not None
    assert latest.content.endswith("REVISED")
    assert active is not None
    assert active.publication_id == accepted_publication_id
    assert store.get_ingestion_result(latest.source_version_id).status == "blocked"  # type: ignore[union-attr]
    store.close()


def test_payload_free_agent_usage_is_bound_to_the_ingestion_run(
    tmp_path: Path,
) -> None:
    """Discarding case usage would hide whether bounded Agents actually ran."""

    api = _pipeline_api()
    path = tmp_path / "advisories.jsonl"
    _write_advisories(path, [_eligible_advisory("source:usage")])
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-ingestion",
        create=True,
    )
    usage = AgentUsageRecord(
        source_id="source:usage",
        event_id=None,
        task_id="task:usage",
        role="semantic_resolution",
        task_scope="facility",
        execution_mode="activated",
        outcome="accepted",
        detail_status="resolved",
        activation_reason="multiple_candidates",
        provider_call_count=1,
        tool_call_count=1,
        input_tokens=12,
        output_tokens=4,
        provider_latency_ms=7.5,
        tool_latency_ms=1.5,
    )

    def runner(record, _resources, _allow_live_model):  # type: ignore[no-untyped-def]
        return api.IngestionCaseExecution(
            attempt=_ok_attempt(record),
            source_versions=(build_source_version(record),),
            agent_usage_records=(usage,),
        )

    _run(
        api=api,
        config=_config(path),
        store=store,
        resources=_resources(api),
        runner=runner,
    )
    records = store.list_agent_usage()

    assert len(records) == 1
    assert records[0].source_id == "source:usage"
    assert records[0].role == "semantic_resolution"
    assert records[0].provider_call_count == 1
    assert records[0].input_tokens == 12
    store.close()


def test_post_model_publication_failure_preserves_real_usage_counts(
    tmp_path: Path,
) -> None:
    """A failed publication must not erase model work that already occurred."""

    api = _pipeline_api()
    path = tmp_path / "advisories.jsonl"
    _write_advisories(path, [_eligible_advisory("source:usage-failure")])
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-ingestion",
        create=True,
    )
    usage = AgentUsageRecord(
        source_id="source:usage-failure",
        event_id=None,
        task_id="task:usage-failure",
        role="semantic_resolution",
        task_scope="facility",
        execution_mode="activated",
        outcome="accepted",
        detail_status="resolved",
        activation_reason="multiple_candidates",
        provider_call_count=1,
        tool_call_count=2,
        input_tokens=21,
        output_tokens=8,
        provider_latency_ms=9.5,
        tool_latency_ms=2.5,
    )

    def runner(record, _resources, _allow_live_model):  # type: ignore[no-untyped-def]
        accepted = _ok_attempt(record)
        mismatched = accepted.result.model_copy(
            update={"source_version_id": "source-version:wrong"}
        )
        return api.IngestionCaseExecution(
            attempt=IngestionAttempt(
                result=mismatched,
                package=accepted.package,
            ),
            source_versions=(build_source_version(record),),
            agent_usage_records=(usage,),
        )

    summary = _run(
        api=api,
        config=_config(path),
        store=store,
        resources=_resources(api),
        runner=runner,
    )
    records = store.list_agent_usage()

    assert summary.blocked_count == 1
    assert len(records) == 1
    assert records[0].execution_mode == "activated"
    assert records[0].outcome == "blocked"
    assert records[0].provider_call_count == 1
    assert records[0].tool_call_count == 2
    assert records[0].input_tokens == 21
    assert records[0].output_tokens == 8
    store.close()


def test_ingestion_indexes_only_new_versions_and_publications(
    tmp_path: Path,
) -> None:
    """An unchanged second ingestion must not invoke embedding/index work."""

    api = _pipeline_api()
    path = tmp_path / "advisories.jsonl"
    rows = [
        _eligible_advisory("source:selected"),
        _unsupported_advisory("source:registered-only"),
    ]
    _write_advisories(path, rows)
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-ingestion",
        create=True,
    )
    calls: list[dict[str, object]] = []

    def runner(record, _resources, _allow_live_model):  # type: ignore[no-untyped-def]
        return _execution(api, _ok_attempt(record), record)

    def indexer(  # type: ignore[no-untyped-def]
        indexed_store,
        *,
        source_version_ids,
        event_publication_ids,
        allow_model_download,
        model_name,
    ):
        calls.append(
            {
                "store": indexed_store,
                "source_version_ids": source_version_ids,
                "event_publication_ids": event_publication_ids,
                "allow_model_download": allow_model_download,
                "model_name": model_name,
            }
        )
        return ()

    config = _config(path)
    resources = _resources(api)
    first = api.run_ingestion_pipeline(
        config,
        store,
        source_ids=("source:selected",),
        resource_loader=lambda _config: resources,
        case_runner=runner,
        retrieval_indexer=indexer,
    )
    second = api.run_ingestion_pipeline(
        config,
        store,
        source_ids=("source:selected",),
        resource_loader=lambda _config: resources,
        case_runner=runner,
        retrieval_indexer=indexer,
    )

    selected = store.get_latest_source_version("source:selected")
    registered_only = store.get_latest_source_version(
        "source:registered-only"
    )
    assert selected is not None
    assert registered_only is not None
    assert first.ok_count == 1
    assert second.skipped_count == 1
    assert len(calls) == 1
    assert calls[0]["store"] is store
    assert calls[0]["source_version_ids"] == tuple(
        sorted(
            (
                selected.source_version_id,
                registered_only.source_version_id,
            )
        )
    )
    assert calls[0]["event_publication_ids"] == (
        _ok_attempt(
            SourceRecord(
                source_id="source:selected",
                family=SourceFamily.ATCSCC_ADVISORY,
                content=rows[0]["text"],
                title=rows[0]["title"],
            )
        ).result.publication_id,
    )
    store.close()


def test_vector_index_failure_does_not_rollback_semantic_publication(
    tmp_path: Path,
) -> None:
    """A rebuildable-index error is not a semantic ingestion failure."""

    api = _pipeline_api()
    path = tmp_path / "advisories.jsonl"
    _write_advisories(path, [_eligible_advisory("source:index-failure")])
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-ingestion",
        create=True,
    )

    def runner(record, _resources, _allow_live_model):  # type: ignore[no-untyped-def]
        return _execution(api, _ok_attempt(record), record)

    def failing_indexer(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        raise RuntimeError("embedding unavailable")

    summary = api.run_ingestion_pipeline(
        _config(path),
        store,
        resource_loader=lambda _config: _resources(api),
        case_runner=runner,
        retrieval_indexer=failing_indexer,
    )

    assert summary.ok_count == 1
    assert summary.blocked_count == 0
    assert store.find_tmi_events(api.TMIEventQuery()).total_matches == 1
    store.close()


def test_encoder_initialization_failure_keeps_exact_source_search(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Chunking/FTS precede embedding and survive an unavailable model."""

    api = _pipeline_api()
    record = SourceRecord(
        source_id="source:fts-before-vector",
        family=SourceFamily.ATCSCC_ADVISORY,
        content="GROUND STOP SOURCE REMAINS SEARCHABLE",
    )
    version = build_source_version(record)
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test-ingestion",
        create=True,
    )
    store.register_source_version(version)
    index_module = importlib.import_module(
        "aviation_agentic_ai.agent_system.tmi_event_retrieval_index"
    )

    class UnavailableEncoder:
        def __init__(self, *_args, **_kwargs):
            raise RuntimeError("embedding model unavailable")

    monkeypatch.setattr(
        index_module,
        "SentenceTransformerTMIEventEncoder",
        UnavailableEncoder,
    )

    api._update_retrieval_indexes(
        store,
        source_version_ids=(version.source_version_id,),
        event_publication_ids=(),
        allow_model_download=False,
        model_name="test/unavailable",
    )

    assert tuple(
        chunk.source_version_id
        for chunk in store.search_source_text("SEARCHABLE")
    ) == (version.source_version_id,)
    source_state = store.get_vector_index_state(
        "aviation_source_chunks_v1"
    )
    assert source_state is not None
    assert source_state.status == "blocked"
    store.close()
