"""End-to-end contracts for deterministic Decision Context Case integration."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import pytest

import aviation_agentic_ai.agent_system.context_artifacts as context_artifacts_module
import aviation_agentic_ai.agent_system.weather_context as weather_context_module
from aviation_agentic_ai.agent_system.context_artifacts import (
    integrate_decision_context,
    parse_advisory_signature,
    prepare_decision_context,
    read_context_associations,
    read_outcome_summaries,
    read_weather_fact_traces,
)
from aviation_agentic_ai.agent_system.authority_resolution import AuthorityResolutionResult
from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    BTSObservationBundle,
    EvidenceCard,
    EvidenceClaim,
    FactTraceRow,
    GraphValidationResult,
    PersistedProfileGap,
    SourceFamily,
    SourceRecord,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.materialize import materialize_validated_facts
from aviation_agentic_ai.agent_system.runtime import write_run_manifest
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)
from aviation_agentic_ai.agent_system.sources import (
    build_source_snapshot_registry,
    load_advisory_source,
    load_bts_context_source,
    load_weather_sources,
)
from aviation_agentic_ai.agent_system.weather_context import (
    FORECASTING_AIRPORT,
    INTERVAL_END,
    INTERVAL_START,
    METAR_STRING,
    TAF_STRING,
)
from aviation_agentic_ai.agent_system.workflow import (
    AuthoritySourceRecordRegistry,
    AuthoritySourceRegistryStatus,
    IngestContext,
    build_ingest_graph,
    run_ingest,
)
from aviation_agentic_ai.config import load_yaml
from aviation_agentic_ai.cross_source.contracts import (
    CanonicalEntity,
    CodeValue,
    EntityType,
)


ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
NAS = "https://data.nasa.gov/ontologies/atmonto/NAS#"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
XSD_DATETIME = "http://www.w3.org/2001/XMLSchema#dateTime"
XSD_STRING = "http://www.w3.org/2001/XMLSchema#string"
FACILITIES = {
    "KJFK": CanonicalEntity(
        entity_id="urn:aviation-agentic-ai:facility:airport:KJFK",
        entity_type=EntityType.AIRPORT,
        preferred_label="John F Kennedy International Airport",
        codes=[
            CodeValue(scheme="IATA", value="JFK"),
            CodeValue(scheme="ICAO", value="KJFK"),
        ],
    ),
    "KEWR": CanonicalEntity(
        entity_id="urn:aviation-agentic-ai:facility:airport:KEWR",
        entity_type=EntityType.AIRPORT,
        preferred_label="Newark Liberty International Airport",
        codes=[
            CodeValue(scheme="IATA", value="EWR"),
            CodeValue(scheme="ICAO", value="KEWR"),
        ],
    ),
}

DECISION_PROFILE_REF = next(
    ref
    for ref in load_validation_profile_registry(decision_guide=load_schema_guide()).refs
    if ref.layer == "decision"
)


def _fact(
    fact_id: str,
    event_id: str,
    event_class: str,
    predicate_iri: str,
    object_value: str,
    *,
    object_kind: str = "literal",
    object_class_iri: str | None = None,
    datatype_iri: str | None = XSD_STRING,
    source_id: str,
) -> ValidatedFact:
    return ValidatedFact(
        fact_id=fact_id,
        subject_iri=event_id,
        subject_class_iri=f"{ATM}{event_class}",
        predicate_iri=predicate_iri,
        object_kind=object_kind,
        object_value=object_value,
        object_class_iri=object_class_iri,
        datatype_iri=datatype_iri if object_kind == "literal" else None,
        source_ids=[source_id],
        evidence_texts=["source-bound core evidence"],
        validation_profile=DECISION_PROFILE_REF,
        evidence_mode="source_text",
        evidence_ref=fact_id,
    )


def _core_facts(
    *,
    event_id: str,
    event_class: str,
    facility: CanonicalEntity,
    start: str,
    end: str,
    source_id: str,
    reason: str | None,
) -> list[ValidatedFact]:
    facts = [
        _fact(
            "core:type",
            event_id,
            event_class,
            RDF_TYPE,
            f"{ATM}{event_class}",
            object_kind="iri",
            object_class_iri=f"{ATM}{event_class}",
            source_id=source_id,
        ),
        _fact(
            "core:facility",
            event_id,
            event_class,
            f"{ATM}controlledNASelement",
            facility.entity_id,
            object_kind="iri",
            object_class_iri=f"{NAS}Airport",
            source_id=source_id,
        ),
        _fact(
            "core:start",
            event_id,
            event_class,
            f"{ATM}effectiveStartTime",
            start,
            datatype_iri=XSD_DATETIME,
            source_id=source_id,
        ),
        _fact(
            "core:end",
            event_id,
            event_class,
            f"{ATM}effectiveEndTime",
            end,
            datatype_iri=XSD_DATETIME,
            source_id=source_id,
        ),
    ]
    if reason is not None:
        facts.append(
            _fact(
                "core:reason",
                event_id,
                event_class,
                f"{ATM}impactingCondition",
                reason,
                source_id=source_id,
            )
        )
    return facts


def _facility_authority_result(
    facility: CanonicalEntity, source_id: str
) -> AuthorityResolutionResult:
    return AuthorityResolutionResult(
        evidence_card=EvidenceCard(
            agent_role="facility",
            status=AgentStatus.RESOLVED,
            canonical_refs=[facility.entity_id],
            source_ids=[source_id],
            claims=[
                EvidenceClaim(
                    field_name="controlled_facility",
                    value=facility.codes[0].value,
                    ontology_target="nas:Airport",
                    evidence_text="source-bound core evidence",
                    source_id=source_id,
                    canonical_ref=facility.entity_id,
                )
            ],
        ),
        domain_outcome=cast(Any, None),
        authority_source_records=(),
        resolution_task=cast(Any, None),
        resolution_proposal=cast(Any, None),
    )


def _authority_records(facility_code: str, *, ground_stop: bool) -> tuple[SourceRecord, ...]:
    records = [
        SourceRecord(
            source_id=f"authority:nasr:{facility_code}",
            family=SourceFamily.NASR_FACILITY,
            content=f'{{"authority_text":"{facility_code} airport"}}',
        ),
        SourceRecord(
            source_id=(
                "authority:pcg:ground-stop" if ground_stop else "authority:pcg:ground-delay-program"
            ),
            family=SourceFamily.FAA_TERM,
            content=(
                '{"authority_text":"Ground Stop"}'
                if ground_stop
                else '{"authority_text":"Ground Delay Program"}'
            ),
        ),
    ]
    if ground_stop:
        records.append(
            SourceRecord(
                source_id="authority:pcg:glide-slope",
                family=SourceFamily.FAA_TERM,
                content='{"authority_text":"Glide Slope"}',
            )
        )
    return tuple(sorted(records, key=lambda record: record.source_id))


def _write_core_fact_trace(
    output_dir: Path,
    facts: list[ValidatedFact],
    registry,
) -> list[FactTraceRow]:
    snapshot = registry.snapshots[0]
    rows = [
        FactTraceRow(
            fact_id=fact.fact_id,
            graph_patch_line="fixture graph patch line",
            source_id=snapshot.source_id,
            evidence_text=fact.evidence_texts[0],
            evidence_agent_role="fixture",
            source_snapshot_sha256=snapshot.content_sha256,
        )
        for fact in facts
    ]
    (output_dir / "fact_trace.jsonl").write_text(
        "".join(row.model_dump_json() + "\n" for row in rows),
        encoding="utf-8",
    )
    return rows


def _materialize_core_current(
    *,
    facts: list[ValidatedFact],
    source_snapshot,
    output_dir: Path,
):
    traces = _write_core_fact_trace(
        output_dir,
        facts,
        source_snapshot,
    )
    return materialize_validated_facts(
        facts=facts,
        profile_registry=load_validation_profile_registry(
            decision_guide=load_schema_guide()
        ),
        source_snapshot=source_snapshot,
        fact_traces=traces,
        output_dir=output_dir,
    )


@pytest.fixture(scope="module")
def config() -> dict:
    return load_yaml("configs/cross_source_v1.yaml")


@pytest.fixture(scope="module")
def weather_sources(config) -> list:
    return load_weather_sources(config)


@pytest.fixture(scope="module")
def bts_context(config):
    return load_bts_context_source(config)


@pytest.mark.parametrize(
    "source_key",
    ["bts_on_time_snapshot", "bts_on_time_manifest"],
)
def test_bts_loader_uses_configured_snapshot_paths(
    config,
    tmp_path,
    source_key,
):
    configured = {"sources": dict(config["sources"])}
    configured["sources"][source_key] = str(tmp_path / "missing-bts-source")

    with pytest.raises(FileNotFoundError):
        load_bts_context_source(configured)


@pytest.fixture(scope="module")
def weather_validation_case(config, weather_sources):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    facts = _core_facts(
        event_id="evt:weather-validator",
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=source_id,
        reason="weather",
    )
    event = context_artifacts_module._build_event(
        IngestContext(advisory=advisory, run_id="run:weather-validator"),
        {
            "event_uri": "evt:weather-validator",
            "validation": GraphValidationResult(accepted=facts, publishable=True),
        },
    )
    registry = build_source_snapshot_registry([advisory, *weather_sources])
    bundle = context_artifacts_module.build_weather_context(event, facility, registry)
    assert bundle.status == "ok"
    return event, facility, registry, bundle


def test_signature_parser_uses_signature_and_rejects_missing_or_malformed_values():
    text = "EFFECTIVE TIME:\n192138-192345\nSIGNATURE:\n26/05/19 21:38\n"
    assert parse_advisory_signature(text) == datetime(2026, 5, 19, 21, 38, tzinfo=UTC)
    assert parse_advisory_signature("EFFECTIVE TIME:\n192138-192345\n") is None
    with pytest.raises(ValueError, match="malformed SIGNATURE"):
        parse_advisory_signature("SIGNATURE:\n26/13/99 90:90\n")


@pytest.mark.parametrize(
    ("content", "expected_status"),
    [
        ("EFFECTIVE TIME:\n192138-192345\n", "insufficient"),
        ("SIGNATURE:\n26/13/99 90:90\n", "blocked"),
    ],
)
def test_missing_or_malformed_signature_fails_the_optional_context_layer(
    tmp_path,
    config,
    content,
    expected_status,
):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id).model_copy(update={"content": content})
    facility = FACILITIES["KJFK"]
    facts = _core_facts(
        event_id="evt:signature-status",
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=source_id,
        reason="weather",
    )
    core_materialization = object()
    result = integrate_decision_context(
        IngestContext(
            advisory=advisory,
            facility_candidates=[facility],
            run_id="run:signature-status",
            output_dir=str(tmp_path),
        ),
        {
            "event_uri": "evt:signature-status",
            "facility_authority_result": _facility_authority_result(facility, source_id),
            "validation": GraphValidationResult(accepted=facts, publishable=True),
            "materialization": core_materialization,
        },
    )

    assert result["weather_context"].status == expected_status
    assert result["outcome_context"].status == expected_status
    assert result["materialization"] is core_materialization
    assert (tmp_path / "context_associations.jsonl").read_bytes() == b""
    assert (tmp_path / "outcome_summaries.jsonl").read_bytes() == b""


def test_loaders_preserve_exact_weather_rows_and_the_pinned_bts_snapshot(
    config,
    weather_sources,
    bts_context,
):
    metar_path = Path(config["sources"]["metar"])
    exact_metar_rows = {
        line for line in metar_path.read_text(encoding="utf-8").splitlines() if line
    }
    assert weather_sources
    assert all(
        source.content in exact_metar_rows or source.family == SourceFamily.TAF
        for source in weather_sources
    )
    assert len({source.source_id for source in weather_sources}) == len(weather_sources)

    bts_source, bts_rows, binding = bts_context
    manifest = json.loads(
        Path("data/sources/bts_on_time_2026_05_manifest.json").read_text(encoding="utf-8")
    )
    assert len(bts_rows) == 1_978
    assert bts_source.source_id == manifest["source_id"]
    assert (
        hashlib.sha256(bts_source.content.encode("utf-8")).hexdigest()
        == manifest["normalized_sha256"]
    )
    assert binding.source_id == manifest["source_id"]
    assert binding.normalized_snapshot_sha256 == manifest["normalized_sha256"]
    assert binding.archive_sha256 == manifest["archive_sha256"]


def test_gdp_138_assembly_sees_only_prepared_validated_multisource_rows(
    tmp_path,
    config,
    weather_sources,
    bts_context,
    monkeypatch,
):
    """Assembly consumes in-memory validated context before publication."""

    import aviation_agentic_ai.agent_system.workflow as workflow_module
    from test_agent_system_authority_evidence import _catalog

    advisory = load_advisory_source(config, "2026-05-19:138")
    catalog = _catalog(tmp_path)
    bts_source, bts_rows, bts_binding = bts_context
    output_dir = tmp_path / "gdp-138-prepared-context"
    provider_constructions: list[str] = []
    observed_before_assembly: dict[str, object] = {}
    original_builder = workflow_module._build_case_assembly_task_from_state

    def capture_prepared_task(ctx, state, *, event_uri, event_class):
        observed_before_assembly["weather_status"] = state["weather_context"].status
        observed_before_assembly["observation_status"] = state["observation_context"].status
        observed_before_assembly["artifacts_exist"] = any(
            (output_dir / name).exists()
            for name in (
                "context_associations.jsonl",
                "outcome_summaries.jsonl",
                "source_snapshots.jsonl",
            )
        )
        return original_builder(
            ctx,
            state,
            event_uri=event_uri,
            event_class=event_class,
        )

    monkeypatch.setattr(
        workflow_module,
        "_build_case_assembly_task_from_state",
        capture_prepared_task,
    )
    state = run_ingest(
        IngestContext(
            advisory=advisory,
            facility_candidates=[FACILITIES["KJFK"]],
            term_candidates=list(catalog.terminology.registry_terms),
            weather_sources=weather_sources,
            bts_rows=bts_rows,
            bts_source=bts_source,
            bts_manifest_binding=bts_binding,
            authority_catalog=catalog,
            guide=load_schema_guide(),
            run_id="run:gdp-138-prepared-context",
            run_started_at=datetime(2026, 5, 19, 20, 0, tzinfo=UTC),
            output_dir=str(output_dir),
            case_assembly_model_factory=lambda tools: (
                provider_constructions.append("assembly") or object()
            ),
        )
    )

    task = state["case_assembly_task"]
    weather = state["weather_context"]
    observations = state["observation_context"]
    assert observations.status == "ok", observations.failure_reason
    assert observed_before_assembly == {
        "weather_status": "ok",
        "observation_status": "ok",
        "artifacts_exist": False,
    }
    assert provider_constructions == []
    assert task.available_evidence_layer_ids == (
        "layer:advisory",
        "layer:bts",
        "layer:weather",
    )
    assert task.context_association_ids == tuple(
        sorted(association.association_id for association in weather.associations)
    )
    expected_observation_ids = tuple(
        sorted({trace.observation_id for trace in observations.fact_traces})
    )
    assert task.public_observation_ids == expected_observation_ids
    assert (
        tuple(row.association_id for row in task.context_associations)
        == task.context_association_ids
    )
    assert (
        tuple(row.observation_id for row in task.public_observations) == task.public_observation_ids
    )
    expected_source_ids = {
        advisory.source_id,
        bts_source.source_id,
        *(association.source_id for association in weather.associations),
        *(
            authority_source_id
            for record in task.resolution_records
            for authority_source_id in record.authority_source_ids
        ),
    }
    assert {binding.source_id for binding in task.source_snapshot_bindings} == expected_source_ids
    assert state["validation"].publishable
    assert state["materialization"] is not None


def test_prepared_context_is_rejected_when_kernel_accepts_a_different_event(
    tmp_path,
    config,
    weather_sources,
):
    advisory = load_advisory_source(config, "2026-05-19:138")
    facility = FACILITIES["KJFK"]
    event_id = "evt:prepared-kernel-recheck"
    candidate_facts = _core_facts(
        event_id=event_id,
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=advisory.source_id,
        reason="weather",
    )
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=[facility],
        weather_sources=weather_sources,
        guide=load_schema_guide(),
        run_id="run:prepared-kernel-recheck",
        output_dir=str(tmp_path),
    )
    base_state = {
        "event_uri": event_id,
        "facility_authority_result": _facility_authority_result(facility, advisory.source_id),
        "validation": GraphValidationResult(
            accepted=candidate_facts,
            publishable=True,
        ),
    }
    prepared = prepare_decision_context(ctx, base_state)
    changed_facts = [
        fact.model_copy(update={"object_value": "2026-05-20T03:30:00Z"})
        if fact.predicate_iri == f"{ATM}effectiveEndTime"
        else fact
        for fact in candidate_facts
    ]

    result = integrate_decision_context(
        ctx,
        {
            **base_state,
            **prepared,
            "validation": GraphValidationResult(
                accepted=changed_facts,
                publishable=True,
            ),
        },
    )

    assert result["weather_context"].status == "blocked"
    assert "differs from Formal Graph Kernel" in (result["weather_context"].failure_reason)
    assert (tmp_path / "context_associations.jsonl").read_bytes() == b""


@pytest.mark.parametrize(
    (
        "source_id",
        "event_class",
        "facility_code",
        "start",
        "end",
        "reason",
        "active_counts",
    ),
    [
        (
            "2026-05-19:123",
            "GroundStopTMI",
            "KJFK",
            "2026-05-19T21:00:00Z",
            "2026-05-19T22:45:00Z",
            None,
            (20, 18, 2, 0),
        ),
        (
            "2026-05-19:138",
            "GroundDelayProgramTMI",
            "KJFK",
            "2026-05-19T22:05:00Z",
            "2026-05-20T02:59:00Z",
            "weather",
            (77, 68, 4, 5),
        ),
        (
            "2026-05-20:020",
            "GroundDelayProgramTMI",
            "KEWR",
            "2026-05-20T01:24:00Z",
            "2026-05-20T05:46:00Z",
            None,
            (50, 49, 1, 0),
        ),
    ],
)
def test_three_cases_integrate_weather_and_bts_without_widening_core_semantics(
    tmp_path,
    config,
    weather_sources,
    bts_context,
    monkeypatch,
    source_id,
    event_class,
    facility_code,
    start,
    end,
    reason,
    active_counts,
):
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES[facility_code]
    event_id = f"evt:{source_id.replace(':', '-')}"
    facts = _core_facts(
        event_id=event_id,
        event_class=event_class,
        facility=facility,
        start=start,
        end=end,
        source_id=source_id,
        reason=reason,
    )
    validation = GraphValidationResult(accepted=facts, publishable=True)
    advisory_registry = build_source_snapshot_registry([advisory])
    core_materialization = _materialize_core_current(
        facts=facts,
        source_snapshot=advisory_registry,
        output_dir=tmp_path,
    )
    _write_core_fact_trace(tmp_path, facts, advisory_registry)
    if source_id.endswith(":123"):
        gap = PersistedProfileGap(
            profile_gap_id="gap:reason:123",
            event_id=f"urn:aviation-agentic-ai:event:{event_id.removeprefix('evt:')}",
            field="impacting_condition",
            value="weather",
            evidence_text="IMPACTING CONDITION: WEATHER / THUNDERSTORMS",
            reason="Ground Stop reason is outside the active profile",
            source_id=source_id,
            source_snapshot_sha256=advisory_registry.snapshots[0].content_sha256,
        )
        (tmp_path / "profile_gaps.jsonl").write_text(gap.model_dump_json() + "\n", encoding="utf-8")

    bts_source, bts_rows, bts_binding = bts_context
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=[facility],
        weather_sources=weather_sources,
        bts_rows=bts_rows,
        bts_source=bts_source,
        bts_manifest_binding=bts_binding,
        run_id=f"run:{source_id}",
        output_dir=str(tmp_path),
    )
    state = {
        "event_uri": event_id,
        "event_class": f"atm:{event_class}",
        "facility_authority_result": _facility_authority_result(facility, source_id),
        "validation": validation,
        "materialization": core_materialization,
        "source_snapshot": advisory_registry,
        "authority_source_records": AuthoritySourceRecordRegistry(
            records=_authority_records(
                facility_code,
                ground_stop=source_id.endswith(":123"),
            )
        ),
        "model_calls": ["existing-call"],
    }

    result = integrate_decision_context(ctx, state)

    assert result["model_calls"] == []
    assert result["decision_context_event"].operational_start == datetime.fromisoformat(
        start.replace("Z", "+00:00")
    )
    assert result["decision_context_event"].operational_end == datetime.fromisoformat(
        end.replace("Z", "+00:00")
    )
    assert result["decision_context_event"].advisory_issued_at == parse_advisory_signature(
        advisory.content
    )
    assert result["weather_context"].status == "ok"
    assert result["outcome_context"].status == "ok"
    if source_id == "2026-05-19:138":
        assert result["observation_context"].status == "ok", result[
            "observation_context"
        ].failure_reason
        assert result["materialization"].layer_fact_counts["decision"] == len(facts)
        assert result["materialization"].layer_fact_counts["weather"] == len(
            result["weather_context"].formal_facts
        )
        assert result["materialization"].layer_fact_counts["public_operational_observation"] > 0
        for artifact_name in (
            "observation_derivations",
            "observation_fact_trace",
            "reconstruction_trace",
        ):
            assert result["context_artifacts"][artifact_name]["status"] == "ok"
            assert result["context_artifacts"][artifact_name]["count"] > 0
        assert {
            layer: metadata["status"] for layer, metadata in result["formal_layers"].items()
        } == {
            "decision": "ok",
            "weather": "ok",
            "public_operational_observation": "ok",
        }
        publication = result["public_observation_publication"]
        assert publication["status"] == "ok"
        assert publication["bts_source_id"] == bts_source.source_id
        assert (
            publication["aggregation_procedure_checksum"]
            == result["observation_context"].reconstruction_trace.aggregation_procedure_checksum
        )
    active = next(
        summary for summary in result["outcome_context"].summaries if summary.phase == "active"
    )
    assert (
        active.scheduled_arrival_count,
        active.completed_arrival_count,
        active.cancelled_count,
        active.diverted_count,
    ) == active_counts

    kg_rows = [
        json.loads(line)
        for line in Path(result["materialization"].jsonl_path)
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    event_rows = [row for row in kg_rows if row["subject"].endswith(event_id.removeprefix("evt:"))]
    reasons = [row["object"] for row in event_rows if row["predicate"] == "atm:impactingCondition"]
    assert reasons == ([reason] if reason is not None else [])
    assert not any(
        row["subject"].endswith(event_id.removeprefix("evt:"))
        and row["predicate"].startswith("data:")
        for row in kg_rows
    )
    assert not any(
        "arrivalDemand" in row["predicate"] or "airportArrivalRate" in row["predicate"]
        for row in kg_rows
    )
    assert not any("authority:" in json.dumps(row) for row in kg_rows)

    associations = read_context_associations(tmp_path / "context_associations.jsonl")
    summaries = read_outcome_summaries(tmp_path / "outcome_summaries.jsonl")
    traces = read_weather_fact_traces(tmp_path / "weather_fact_trace.jsonl")
    assert associations and summaries and traces
    assert all(association.causal_claim is False for association in associations)
    assert all(
        association.event_id == result["decision_context_event"].event_id
        for association in associations
    )
    assert all(
        summary.event_id == result["decision_context_event"].event_id for summary in summaries
    )
    selected_sources = {association.source_id for association in associations}
    registry_sources = {snapshot.source_id for snapshot in result["source_snapshot"].snapshots}
    assert selected_sources <= registry_sources
    assert bts_source.source_id in registry_sources
    authority_records = state["authority_source_records"].records
    assert {record.source_id for record in authority_records} <= registry_sources
    assert len(registry_sources) == len(selected_sources) + 2 + len(authority_records)
    if source_id.endswith(":123"):
        assert {
            "authority:pcg:ground-stop",
            "authority:pcg:glide-slope",
        } <= registry_sources
    assert all(
        association.source_snapshot_sha256
        == result["source_snapshot"].get(association.source_id).content_sha256
        for association in associations
    )

    ttl = Path(result["materialization"].ttl_path).read_text(encoding="utf-8")
    nodes = [
        json.loads(line)
        for line in Path(result["materialization"].nodes_path)
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    relationships = [
        json.loads(line)
        for line in Path(result["materialization"].relationships_path)
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert "authority:" not in ttl
    assert not any("authority:" in json.dumps(row) for row in [*nodes, *relationships])
    assert "@prefix data:" in ttl
    assert any(node["label"] == "MeteorologicalReport" for node in nodes)
    assert any(rel["type"] == "FORECASTING_AIRPORT" for rel in relationships)
    assert not any(
        rel["type"] == "FORECASTING_AIRPORT"
        and rel["start_id"] == result["decision_context_event"].event_id
        for rel in relationships
    )

    if source_id.endswith(":123"):
        assert "gap:reason:123" in (tmp_path / "profile_gaps.jsonl").read_text(encoding="utf-8")
    if source_id.endswith(":020"):
        assert not reasons

    first_associations = (tmp_path / "context_associations.jsonl").read_bytes()
    first_outcomes = (tmp_path / "outcome_summaries.jsonl").read_bytes()
    first_traces = (tmp_path / "weather_fact_trace.jsonl").read_bytes()
    repeated = integrate_decision_context(ctx, state)
    assert (tmp_path / "context_associations.jsonl").read_bytes() == first_associations
    assert (tmp_path / "outcome_summaries.jsonl").read_bytes() == first_outcomes
    assert (tmp_path / "weather_fact_trace.jsonl").read_bytes() == first_traces
    first_authority_bindings = {
        snapshot.source_id: snapshot.content_sha256
        for snapshot in result["source_snapshot"].snapshots
        if snapshot.source_id.startswith("authority:")
    }
    assert {
        snapshot.source_id: snapshot.content_sha256
        for snapshot in repeated["source_snapshot"].snapshots
        if snapshot.source_id.startswith("authority:")
    } == first_authority_bindings
    repeated_nodes = [
        json.loads(line)
        for line in Path(repeated["materialization"].nodes_path)
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert len({node["id"] for node in repeated_nodes}) == len(repeated_nodes)
    assert sum(node["id"] == facility.entity_id for node in repeated_nodes) == 1

    if source_id == "2026-05-19:138":
        monkeypatch.setattr(
            context_artifacts_module,
            "build_bts_observation_facts",
            lambda *args, **kwargs: BTSObservationBundle(
                status="blocked",
                failure_reason="injected observation validation failure",
            ),
        )
        blocked = integrate_decision_context(ctx, state)
        assert blocked["observation_context"].status == "blocked"
        assert blocked["materialization"].layer_fact_counts == {
            "decision": len(facts),
            "weather": len(blocked["weather_context"].formal_facts),
        }
        for artifact_name in (
            "observation_derivations.jsonl",
            "observation_fact_trace.jsonl",
            "reconstruction_trace.json",
        ):
            assert (tmp_path / artifact_name).read_bytes() == b""

        insufficient = integrate_decision_context(
            replace(
                ctx,
                bts_rows=[],
                bts_source=None,
                bts_manifest_binding=None,
            ),
            state,
        )
        assert insufficient["observation_context"].status == "insufficient"
        assert insufficient["materialization"].layer_fact_counts == {
            "decision": len(facts),
            "weather": len(insufficient["weather_context"].formal_facts),
        }


def test_optional_context_failure_keeps_the_materialized_core_and_writes_empty_artifacts(
    tmp_path,
    config,
):
    source_id = "2026-05-20:020"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KEWR"]
    event_id = "evt:optional-layer-failure"
    facts = _core_facts(
        event_id=event_id,
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-20T01:24:00Z",
        end="2026-05-20T05:46:00Z",
        source_id=source_id,
        reason=None,
    )
    registry = build_source_snapshot_registry([advisory])
    core = _materialize_core_current(
        facts=facts,
        source_snapshot=registry,
        output_dir=tmp_path,
    )
    before = Path(core.jsonl_path).read_bytes()
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=[facility],
        weather_failure_reason="weather loader checksum mismatch",
        bts_failure_reason="BTS manifest checksum mismatch",
        run_id="run:blocked-context",
        output_dir=str(tmp_path),
    )

    result = integrate_decision_context(
        ctx,
        {
            "event_uri": event_id,
            "event_class": "atm:GroundDelayProgramTMI",
            "facility_authority_result": _facility_authority_result(facility, source_id),
            "validation": GraphValidationResult(accepted=facts, publishable=True),
            "materialization": core,
            "source_snapshot": registry,
            "authority_source_records": AuthoritySourceRecordRegistry(
                status=AuthoritySourceRegistryStatus.BLOCKED,
                reason_code="AUTHORITY_SOURCE_ID_CONFLICT",
                error_id="authority-source-registry-error:test",
            ),
        },
    )

    assert result["weather_context"].status == "blocked"
    assert result["outcome_context"].status == "blocked"
    assert Path(core.jsonl_path).read_bytes() == before
    for name in (
        "context_associations.jsonl",
        "outcome_summaries.jsonl",
        "weather_fact_trace.jsonl",
    ):
        assert (tmp_path / name).read_bytes() == b""
    assert result["context_artifacts"]["context_associations"]["status"] == "blocked"
    assert result["context_artifacts"]["outcome_summaries"]["status"] == "blocked"
    assert result["context_artifacts"]["source_snapshots"]["status"] == "blocked"
    assert {snapshot.source_id for snapshot in result["source_snapshot"].snapshots} == {source_id}


def test_reconstruction_rejects_an_extra_unvalidated_weather_member(
    tmp_path,
    config,
    weather_sources,
    bts_context,
    monkeypatch,
):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    event_id = "evt:extra-weather-member"
    facts = _core_facts(
        event_id=event_id,
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=source_id,
        reason="weather",
    )
    registry = build_source_snapshot_registry([advisory])
    core = _materialize_core_current(
        facts=facts,
        source_snapshot=registry,
        output_dir=tmp_path,
    )
    _write_core_fact_trace(tmp_path, facts, registry)
    bts_source, bts_rows, bts_binding = bts_context
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=[facility],
        weather_sources=weather_sources,
        bts_rows=bts_rows,
        bts_source=bts_source,
        bts_manifest_binding=bts_binding,
        run_id="run:extra-weather-member",
        output_dir=str(tmp_path),
    )
    original_builder = context_artifacts_module.build_bts_observation_facts

    def build_with_extra_weather_member(*args, **kwargs):
        bundle = original_builder(*args, **kwargs)
        assert bundle.reconstruction_trace is not None
        trace = bundle.reconstruction_trace.model_copy(
            update={
                "member_iris": tuple(
                    sorted(
                        {
                            *bundle.reconstruction_trace.member_iris,
                            ("urn:aviation-agentic-ai:weather-report:unvalidated-extra"),
                        }
                    )
                )
            }
        )
        return bundle.model_copy(update={"reconstruction_trace": trace})

    monkeypatch.setattr(
        context_artifacts_module,
        "build_bts_observation_facts",
        build_with_extra_weather_member,
    )

    result = integrate_decision_context(
        ctx,
        {
            "event_uri": event_id,
            "event_class": "atm:GroundDelayProgramTMI",
            "facility_authority_result": _facility_authority_result(facility, source_id),
            "validation": GraphValidationResult(accepted=facts, publishable=True),
            "materialization": core,
            "source_snapshot": registry,
        },
    )

    assert result["observation_context"].status == "blocked"
    assert "validated weather members" in (result["observation_context"].failure_reason or "")
    assert result["materialization"].layer_fact_counts == {
        "decision": len(facts),
        "weather": len(result["weather_context"].formal_facts),
    }


def test_duplicate_weather_fact_fails_closed_at_the_optional_layer(
    tmp_path,
    config,
    weather_sources,
    monkeypatch,
):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    event_id = "evt:duplicate-weather"
    facts = _core_facts(
        event_id=event_id,
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=source_id,
        reason="weather",
    )
    registry = build_source_snapshot_registry([advisory])
    core = _materialize_core_current(
        facts=facts,
        source_snapshot=registry,
        output_dir=tmp_path,
    )
    event = context_artifacts_module._build_event(
        IngestContext(advisory=advisory, run_id="run:duplicate"),
        {
            "event_uri": event_id,
            "validation": GraphValidationResult(accepted=facts, publishable=True),
        },
    )
    transient = build_source_snapshot_registry([advisory, *weather_sources])
    valid = context_artifacts_module.build_weather_context(
        event,
        facility,
        transient,
    )
    corrupted = valid.model_copy(
        update={"formal_facts": [*valid.formal_facts, valid.formal_facts[0]]}
    )
    monkeypatch.setattr(
        context_artifacts_module,
        "build_weather_context",
        lambda *args, **kwargs: corrupted,
    )
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=[facility],
        weather_sources=weather_sources,
        run_id="run:duplicate",
        output_dir=str(tmp_path),
    )

    result = integrate_decision_context(
        ctx,
        {
            "event_uri": event_id,
            "facility_authority_result": _facility_authority_result(facility, source_id),
            "validation": GraphValidationResult(accepted=facts, publishable=True),
            "materialization": core,
            "source_snapshot": registry,
        },
    )

    assert result["weather_context"].status == "blocked"
    assert "duplicate weather fact ID" in result["weather_context"].failure_reason
    assert (tmp_path / "context_associations.jsonl").read_bytes() == b""
    assert (
        Path(result["materialization"].jsonl_path).read_bytes()
        == Path(core.jsonl_path).read_bytes()
    )


def test_integration_blocks_a_self_consistent_rdf_type_retarget_from_the_builder(
    tmp_path,
    config,
    weather_sources,
    monkeypatch,
):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    event_id = "evt:retargeted-weather-type"
    facts = _core_facts(
        event_id=event_id,
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=source_id,
        reason="weather",
    )
    registry = build_source_snapshot_registry([advisory])
    core = _materialize_core_current(
        facts=facts,
        source_snapshot=registry,
        output_dir=tmp_path,
    )
    event = context_artifacts_module._build_event(
        IngestContext(advisory=advisory, run_id="run:retargeted-type"),
        {
            "event_uri": event_id,
            "validation": GraphValidationResult(accepted=facts, publishable=True),
        },
    )
    transient = build_source_snapshot_registry([advisory, *weather_sources])
    valid = context_artifacts_module.build_weather_context(
        event,
        facility,
        transient,
    )
    rdf_type = next(fact for fact in valid.formal_facts if fact.predicate_iri == RDF_TYPE)
    retargeted = rdf_type.model_copy(
        update={
            "object_value": f"{ATM}GroundDelayProgramTMI",
            "object_class_iri": f"{ATM}GroundDelayProgramTMI",
        }
    )
    corrupted = valid.model_copy(
        update={
            "formal_facts": [
                retargeted if fact.fact_id == rdf_type.fact_id else fact
                for fact in valid.formal_facts
            ]
        }
    )
    monkeypatch.setattr(
        context_artifacts_module,
        "build_weather_context",
        lambda *args, **kwargs: corrupted,
    )

    result = integrate_decision_context(
        IngestContext(
            advisory=advisory,
            facility_candidates=[facility],
            weather_sources=weather_sources,
            run_id="run:retargeted-type",
            output_dir=str(tmp_path),
        ),
        {
            "event_uri": event_id,
            "facility_authority_result": _facility_authority_result(facility, source_id),
            "validation": GraphValidationResult(accepted=facts, publishable=True),
            "materialization": core,
            "source_snapshot": registry,
        },
    )

    assert result["weather_context"].status == "blocked"
    assert "rdf:type" in result["weather_context"].failure_reason
    assert (
        Path(result["materialization"].jsonl_path).read_bytes()
        == Path(core.jsonl_path).read_bytes()
    )
    assert (tmp_path / "context_associations.jsonl").read_bytes() == b""


def test_integration_blocks_self_consistent_raw_evidence_from_a_regressed_parser(
    tmp_path,
    config,
    weather_sources,
    monkeypatch,
):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    event_id = "evt:regressed-weather-parser"
    facts = _core_facts(
        event_id=event_id,
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=source_id,
        reason="weather",
    )
    registry = build_source_snapshot_registry([advisory])
    core = _materialize_core_current(
        facts=facts,
        source_snapshot=registry,
        output_dir=tmp_path,
    )
    original_parse_report = weather_context_module._parse_report

    def regressed_parse_report(snapshot):
        parsed = original_parse_report(snapshot)
        raw = f"FORGED PARSER OUTPUT FOR {parsed.source.source_id}"
        raw_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        time_token = parsed.logical_time.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
        report_id = (
            f"weather-report:{parsed.family.value}:{parsed.station}:{time_token}:"
            f"{raw_hash}:{parsed.source.content_sha256[:16]}"
        )
        return replace(parsed, raw=raw, report_id=report_id)

    monkeypatch.setattr(
        weather_context_module,
        "_parse_report",
        regressed_parse_report,
    )

    result = integrate_decision_context(
        IngestContext(
            advisory=advisory,
            facility_candidates=[facility],
            weather_sources=weather_sources,
            run_id="run:regressed-weather-parser",
            output_dir=str(tmp_path),
        ),
        {
            "event_uri": event_id,
            "facility_authority_result": _facility_authority_result(facility, source_id),
            "validation": GraphValidationResult(
                accepted=facts,
                publishable=True,
            ),
            "materialization": core,
            "source_snapshot": registry,
        },
    )

    assert result["weather_context"].status == "blocked"
    assert "selected report IDs" in result["weather_context"].failure_reason
    assert (
        Path(result["materialization"].jsonl_path).read_bytes()
        == Path(core.jsonl_path).read_bytes()
    )
    assert (tmp_path / "context_associations.jsonl").read_bytes() == b""


def test_weather_bundle_rejects_conflicting_report_source_bindings(
    config,
    weather_sources,
):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    facts = _core_facts(
        event_id="evt:weather-source-conflict",
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=source_id,
        reason="weather",
    )
    event = context_artifacts_module._build_event(
        IngestContext(advisory=advisory, run_id="run:source-conflict"),
        {
            "event_uri": "evt:weather-source-conflict",
            "validation": GraphValidationResult(accepted=facts, publishable=True),
        },
    )
    registry = build_source_snapshot_registry([advisory, *weather_sources])
    valid = context_artifacts_module.build_weather_context(
        event,
        facility,
        registry,
    )
    original = valid.associations[0]
    alternate = next(
        snapshot
        for snapshot in registry.snapshots
        if snapshot.source_id != original.source_id
        and snapshot.family == registry.get(original.source_id).family
    )
    conflicting = original.model_copy(
        update={
            "association_id": f"{original.association_id}:conflict",
            "source_id": alternate.source_id,
            "source_snapshot_sha256": alternate.content_sha256,
        }
    )
    corrupted = valid.model_copy(update={"associations": [conflicting, *valid.associations]})

    with pytest.raises(ValueError, match="conflicting weather report source binding"):
        context_artifacts_module.validate_weather_context_bundle(
            corrupted,
            event=event,
            facility=facility,
            registry=registry,
        )


def test_outcome_bundle_rejects_duplicate_phase_with_a_distinct_id(
    config,
    bts_context,
):
    guide = load_schema_guide()
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    facts = _core_facts(
        event_id="evt:duplicate-outcome-phase",
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=source_id,
        reason="weather",
    )
    event = context_artifacts_module._build_event(
        IngestContext(advisory=advisory, run_id="run:duplicate-phase"),
        {
            "event_uri": "evt:duplicate-outcome-phase",
            "validation": GraphValidationResult(accepted=facts, publishable=True),
        },
    )
    bts_source, bts_rows, bts_binding = bts_context
    registry = build_source_snapshot_registry([bts_source])
    valid = context_artifacts_module.build_bts_outcome_summaries(
        event,
        facility,
        bts_rows,
        source_id=bts_source.source_id,
        source_snapshot_sha256=registry.snapshots[0].content_sha256,
        manifest_binding=bts_binding,
        aggregation_procedure=next(
            profile.aggregation_procedure
            for profile in load_validation_profile_registry(decision_guide=guide).profiles
            if profile.ref.layer == "public_operational_observation"
        ),
    )
    duplicate = valid.summaries[0].model_copy(
        update={"summary_id": f"{valid.summaries[0].summary_id}:duplicate"}
    )
    corrupted = valid.model_copy(update={"summaries": [*valid.summaries, duplicate]})

    with pytest.raises(ValueError, match="exactly one summary per phase"):
        context_artifacts_module._validate_outcomes(
            corrupted,
            event=event,
            facility=facility,
            registry=registry,
        )


@pytest.mark.parametrize(
    "corruption",
    [
        "rdf_type_target",
        "literal_forecasting_airport",
        "empty_formal_fact_set",
        "metar_as_forecast",
        "arbitrary_association_id",
        "forged_relevant_times",
        "wrong_interval_datatype",
        "missing_required_fact",
        "arbitrary_fact_id",
        "forged_raw_report_value",
    ],
)
def test_weather_validator_rejects_semantically_malformed_adapter_bundles(
    weather_validation_case,
    corruption,
):
    event, facility, registry, valid = weather_validation_case
    facts = list(valid.formal_facts)
    traces = list(valid.fact_traces)
    associations = list(valid.associations)

    def replace_fact(original, replacement):
        return [replacement if fact.fact_id == original.fact_id else fact for fact in facts]

    if corruption == "rdf_type_target":
        original = next(fact for fact in facts if fact.predicate_iri == RDF_TYPE)
        facts = replace_fact(
            original,
            original.model_copy(update={"object_value": f"{NAS}Airport"}),
        )
    elif corruption == "literal_forecasting_airport":
        original = next(fact for fact in facts if fact.predicate_iri == FORECASTING_AIRPORT)
        facts = replace_fact(
            original,
            original.model_copy(
                update={
                    "object_kind": "literal",
                    "object_class_iri": None,
                    "datatype_iri": XSD_STRING,
                }
            ),
        )
    elif corruption == "empty_formal_fact_set":
        facts = []
        traces = []
    elif corruption == "metar_as_forecast":
        index = next(
            index
            for index, association in enumerate(associations)
            if registry.get(association.source_id).family == SourceFamily.METAR
        )
        associations[index] = associations[index].model_copy(
            update={"relation_type": "latest_forecast_known_at_issue"}
        )
    elif corruption == "arbitrary_association_id":
        associations[0] = associations[0].model_copy(
            update={"association_id": "weather-association:arbitrary"}
        )
    elif corruption == "forged_relevant_times":
        associations[0] = associations[0].model_copy(
            update={"relevant_times": {"advisory_issued_at": "1999-01-01T00:00:00Z"}}
        )
    elif corruption == "wrong_interval_datatype":
        original = next(fact for fact in facts if fact.predicate_iri == INTERVAL_START)
        facts = replace_fact(
            original,
            original.model_copy(update={"datatype_iri": XSD_STRING}),
        )
    elif corruption == "missing_required_fact":
        original = next(fact for fact in facts if fact.predicate_iri == INTERVAL_END)
        facts = [fact for fact in facts if fact.fact_id != original.fact_id]
        traces = [trace for trace in traces if trace.fact_id != original.fact_id]
    elif corruption == "arbitrary_fact_id":
        original = facts[0]
        replacement = original.model_copy(update={"fact_id": "weather-fact:arbitrary"})
        facts = replace_fact(original, replacement)
        traces = [
            trace.model_copy(update={"fact_id": replacement.fact_id})
            if trace.fact_id == original.fact_id
            else trace
            for trace in traces
        ]
    elif corruption == "forged_raw_report_value":
        original = next(
            fact
            for fact in facts
            if fact.predicate_iri
            in {
                METAR_STRING,
                TAF_STRING,
            }
        )
        facts = replace_fact(
            original,
            original.model_copy(update={"object_value": "FORGED WEATHER REPORT"}),
        )
    corrupted = valid.model_copy(
        update={
            "formal_facts": facts,
            "fact_traces": traces,
            "associations": associations,
        }
    )

    with pytest.raises(ValueError):
        context_artifacts_module.validate_weather_context_bundle(
            corrupted,
            event=event,
            facility=facility,
            registry=registry,
        )


def test_outcome_validator_rejects_event_unbound_1999_windows(
    config,
    bts_context,
):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    facts = _core_facts(
        event_id="evt:outcome-window",
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=source_id,
        reason="weather",
    )
    event = context_artifacts_module._build_event(
        IngestContext(advisory=advisory, run_id="run:outcome-window"),
        {
            "event_uri": "evt:outcome-window",
            "validation": GraphValidationResult(accepted=facts, publishable=True),
        },
    )
    bts_source, bts_rows, bts_binding = bts_context
    registry = build_source_snapshot_registry([bts_source])
    valid = context_artifacts_module.build_bts_outcome_summaries(
        event,
        facility,
        bts_rows,
        source_id=bts_source.source_id,
        source_snapshot_sha256=registry.snapshots[0].content_sha256,
        manifest_binding=bts_binding,
        aggregation_procedure=next(
            profile.aggregation_procedure
            for profile in load_validation_profile_registry(
                decision_guide=load_schema_guide()
            ).profiles
            if profile.ref.layer == "public_operational_observation"
        ),
    )
    active = next(summary for summary in valid.summaries if summary.phase == "active")
    forged = active.model_copy(
        update={
            "window_start": datetime(1999, 1, 1, tzinfo=UTC),
            "window_end": datetime(1999, 1, 2, tzinfo=UTC),
        }
    )
    corrupted = valid.model_copy(
        update={
            "summaries": [
                forged if summary.phase == "active" else summary for summary in valid.summaries
            ]
        }
    )

    with pytest.raises(ValueError, match="BTS outcome window mismatch"):
        context_artifacts_module._validate_outcomes(
            corrupted,
            event=event,
            facility=facility,
            registry=registry,
        )


def test_ingest_graph_has_deterministic_context_node_after_materialization():
    graph = build_ingest_graph()
    graph_json = graph.get_graph().to_json()
    edges = {(edge["source"], edge["target"]) for edge in graph_json["edges"]}
    assert ("materialize", "decision_context") in edges
    assert ("decision_context", "__end__") in edges


def test_run_manifest_registers_exact_context_artifact_metadata(tmp_path):
    artifact = tmp_path / "context_associations.jsonl"
    artifact.write_text("", encoding="utf-8")
    metadata = {
        "context_associations": {
            "path": artifact.name,
            "count": 0,
            "sha256": hashlib.sha256(b"").hexdigest(),
            "status": "insufficient",
        }
    }

    path = write_run_manifest(
        run_dir=tmp_path,
        source_id="2026-05-20:020",
        model_calls=[],
        materialization=None,
        schema_slice_id="slice:test",
        schema_checksum="checksum:test",
        evidence_cards=[],
        graph_patch_raw=None,
        prompt_set_id="prompt:test",
        profile_gap_count=0,
        context_artifacts=metadata,
    )

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["context_artifacts"] == metadata
