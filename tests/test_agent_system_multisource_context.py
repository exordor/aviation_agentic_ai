"""End-to-end contracts for deterministic Decision Context Case integration."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

import aviation_agentic_ai.agent_system.context_artifacts as context_artifacts_module
from aviation_agentic_ai.agent_system.context_artifacts import (
    integrate_decision_context,
    parse_advisory_signature,
    read_context_associations,
    read_outcome_summaries,
    read_weather_fact_traces,
)
from aviation_agentic_ai.agent_system.contracts import (
    AgentResult,
    AgentStatus,
    EvidenceCard,
    EvidenceClaim,
    GraphValidationResult,
    PersistedProfileGap,
    SourceFamily,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.materialize import materialize_validated_facts
from aviation_agentic_ai.agent_system.runtime import write_run_manifest
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.sources import (
    build_source_snapshot_registry,
    load_advisory_source,
    load_bts_context_source,
    load_weather_sources,
)
from aviation_agentic_ai.agent_system.workflow import IngestContext, build_ingest_graph
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


def _facility_result(facility: CanonicalEntity, source_id: str) -> AgentResult:
    return AgentResult(
        status=AgentStatus.RESOLVED,
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
    advisory = load_advisory_source(config, source_id).model_copy(
        update={"content": content}
    )
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
            "facility_result": _facility_result(facility, source_id),
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
    assert all(source.content in exact_metar_rows or source.family == SourceFamily.TAF for source in weather_sources)
    assert len({source.source_id for source in weather_sources}) == len(weather_sources)

    bts_source, bts_rows = bts_context
    manifest = json.loads(
        Path("data/sources/bts_on_time_2026_05_manifest.json").read_text(encoding="utf-8")
    )
    assert len(bts_rows) == 1_978
    assert bts_source.source_id == manifest["source_id"]
    assert hashlib.sha256(bts_source.content.encode("utf-8")).hexdigest() == manifest[
        "normalized_sha256"
    ]


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
    source_id,
    event_class,
    facility_code,
    start,
    end,
    reason,
    active_counts,
):
    guide = load_schema_guide()
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
    core_materialization = materialize_validated_facts(
        facts=facts,
        guide=guide,
        source_snapshot=advisory_registry,
        output_dir=tmp_path,
    )
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
        (tmp_path / "profile_gaps.jsonl").write_text(
            gap.model_dump_json() + "\n", encoding="utf-8"
        )

    bts_source, bts_rows = bts_context
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=[facility],
        guide=guide,
        weather_sources=weather_sources,
        bts_rows=bts_rows,
        bts_source=bts_source,
        run_id=f"run:{source_id}",
        output_dir=str(tmp_path),
    )
    state = {
        "event_uri": event_id,
        "event_class": f"atm:{event_class}",
        "facility_result": _facility_result(facility, source_id),
        "validation": validation,
        "materialization": core_materialization,
        "source_snapshot": advisory_registry,
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
    active = next(
        summary
        for summary in result["outcome_context"].summaries
        if summary.phase == "active"
    )
    assert (
        active.scheduled_arrival_count_proxy,
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
    reasons = [
        row["object"]
        for row in event_rows
        if row["predicate"] == "atm:impactingCondition"
    ]
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

    associations = read_context_associations(tmp_path / "context_associations.jsonl")
    summaries = read_outcome_summaries(tmp_path / "outcome_summaries.jsonl")
    traces = read_weather_fact_traces(tmp_path / "weather_fact_trace.jsonl")
    assert associations and summaries and traces
    assert all(association.causal_claim is False for association in associations)
    assert all(association.event_id == result["decision_context_event"].event_id for association in associations)
    assert all(summary.event_id == result["decision_context_event"].event_id for summary in summaries)
    selected_sources = {
        association.source_id for association in associations
    }
    registry_sources = {
        snapshot.source_id for snapshot in result["source_snapshot"].snapshots
    }
    assert selected_sources <= registry_sources
    assert bts_source.source_id in registry_sources
    assert len(registry_sources) == len(selected_sources) + 2
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
    assert "@prefix data:" in ttl
    assert any(node["label"] == "MeteorologicalReport" for node in nodes)
    assert any(rel["type"] == "FORECASTING_AIRPORT" for rel in relationships)
    assert not any(
        rel["type"] == "FORECASTING_AIRPORT"
        and rel["start_id"] == result["decision_context_event"].event_id
        for rel in relationships
    )

    if source_id.endswith(":123"):
        assert "gap:reason:123" in (tmp_path / "profile_gaps.jsonl").read_text(
            encoding="utf-8"
        )
    if source_id.endswith(":020"):
        assert not reasons

    first_associations = (tmp_path / "context_associations.jsonl").read_bytes()
    first_outcomes = (tmp_path / "outcome_summaries.jsonl").read_bytes()
    first_traces = (tmp_path / "weather_fact_trace.jsonl").read_bytes()
    repeated = integrate_decision_context(ctx, state)
    assert (tmp_path / "context_associations.jsonl").read_bytes() == first_associations
    assert (tmp_path / "outcome_summaries.jsonl").read_bytes() == first_outcomes
    assert (tmp_path / "weather_fact_trace.jsonl").read_bytes() == first_traces
    repeated_nodes = [
        json.loads(line)
        for line in Path(repeated["materialization"].nodes_path)
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert len({node["id"] for node in repeated_nodes}) == len(repeated_nodes)
    assert sum(node["id"] == facility.entity_id for node in repeated_nodes) == 1


def test_optional_context_failure_keeps_the_materialized_core_and_writes_empty_artifacts(
    tmp_path,
    config,
):
    guide = load_schema_guide()
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
    core = materialize_validated_facts(
        facts=facts,
        guide=guide,
        source_snapshot=registry,
        output_dir=tmp_path,
    )
    before = Path(core.jsonl_path).read_bytes()
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=[facility],
        guide=guide,
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
            "facility_result": _facility_result(facility, source_id),
            "validation": GraphValidationResult(accepted=facts, publishable=True),
            "materialization": core,
            "source_snapshot": registry,
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


def test_duplicate_weather_fact_fails_closed_at_the_optional_layer(
    tmp_path,
    config,
    weather_sources,
    monkeypatch,
):
    guide = load_schema_guide()
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
    core = materialize_validated_facts(
        facts=facts,
        guide=guide,
        source_snapshot=registry,
        output_dir=tmp_path,
    )
    event = context_artifacts_module._build_event(
        IngestContext(advisory=advisory, guide=guide, run_id="run:duplicate"),
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
        guide=guide,
        weather_sources=weather_sources,
        run_id="run:duplicate",
        output_dir=str(tmp_path),
    )

    result = integrate_decision_context(
        ctx,
        {
            "event_uri": event_id,
            "facility_result": _facility_result(facility, source_id),
            "validation": GraphValidationResult(accepted=facts, publishable=True),
            "materialization": core,
            "source_snapshot": registry,
        },
    )

    assert result["weather_context"].status == "blocked"
    assert "duplicate weather fact ID" in result["weather_context"].failure_reason
    assert (tmp_path / "context_associations.jsonl").read_bytes() == b""
    assert Path(result["materialization"].jsonl_path).read_bytes() == Path(
        core.jsonl_path
    ).read_bytes()


def test_weather_bundle_rejects_conflicting_report_source_bindings(
    config,
    weather_sources,
):
    guide = load_schema_guide()
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
        IngestContext(advisory=advisory, guide=guide, run_id="run:source-conflict"),
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
    corrupted = valid.model_copy(
        update={"associations": [conflicting, *valid.associations]}
    )

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
        IngestContext(advisory=advisory, guide=guide, run_id="run:duplicate-phase"),
        {
            "event_uri": "evt:duplicate-outcome-phase",
            "validation": GraphValidationResult(accepted=facts, publishable=True),
        },
    )
    bts_source, bts_rows = bts_context
    registry = build_source_snapshot_registry([bts_source])
    valid = context_artifacts_module.build_bts_outcome_summaries(
        event,
        facility,
        bts_rows,
        source_id=bts_source.source_id,
        source_snapshot_sha256=registry.snapshots[0].content_sha256,
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
