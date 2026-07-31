"""Deterministic, source-bound decision-weather context selection."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from aviation_agentic_ai.agent_system.contracts import (
    SourceFamily,
    SourceSnapshot,
    SourceSnapshotRegistry,
)
from aviation_agentic_ai.agent_system.weather_context import (
    TMIEventContext,
    METEOROLOGICAL_CONDITION_STATUS,
    build_weather_context,
)
from aviation_agentic_ai.cross_source.contracts import (
    CanonicalEntity,
    CodeValue,
    EntityType,
)


ISSUED_AT = datetime(2026, 5, 19, 15, tzinfo=UTC)
OPERATIONAL_START = datetime(2026, 5, 19, 16, tzinfo=UTC)
OPERATIONAL_END = datetime(2026, 5, 19, 20, tzinfo=UTC)


def _canonical_json(row: dict[str, object]) -> str:
    return json.dumps(row, sort_keys=True, separators=(",", ":"))


def _snapshot(source_id: str, family: SourceFamily, row: dict[str, object]) -> SourceSnapshot:
    content = _canonical_json(row)
    return SourceSnapshot(
        source_id=source_id,
        family=family,
        content=content,
        content_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        snapshot_timestamp="2026-05-20T00:00:00+00:00",
    )


def _event() -> TMIEventContext:
    return TMIEventContext(
        run_id="run:gs-123",
        event_id="urn:aviation-agentic-ai:event:ground-stop:123",
        advisory_source_id="advisory:gs-123",
        advisory_issued_at=ISSUED_AT,
        operational_start=OPERATIONAL_START,
        operational_end=OPERATIONAL_END,
    )


def _facility(*, airport: bool = True, codes: list[CodeValue] | None = None) -> CanonicalEntity:
    return CanonicalEntity(
        entity_id="urn:aviation-agentic-ai:facility:KJFK",
        entity_type=EntityType.AIRPORT if airport else EntityType.ARTCC,
        preferred_label="John F. Kennedy International Airport",
        codes=codes or [CodeValue(scheme="ICAO", value="KJFK")],
    )


def _taf(
    source_id: str,
    *,
    issue: datetime,
    start: datetime = OPERATIONAL_START - timedelta(hours=1),
    end: datetime = OPERATIONAL_END + timedelta(hours=1),
    station: str = "KJFK",
    raw: str | None = None,
) -> SourceSnapshot:
    return _snapshot(
        source_id,
        SourceFamily.TAF,
        {
            "icaoId": station,
            "issueTime": issue.isoformat(),
            "rawTAF": raw or f"TAF {station} {issue:%d%H%MZ}",
            "validTimeFrom": int(start.timestamp()),
            "validTimeTo": int(end.timestamp()),
        },
    )


def _metar(
    source_id: str,
    *,
    observed: datetime,
    station: str = "KJFK",
    raw: str | None = None,
) -> SourceSnapshot:
    return _snapshot(
        source_id,
        SourceFamily.METAR,
        {
            "icaoId": station,
            "rawOb": raw or f"METAR {station} {observed:%d%H%MZ}",
            "reportTime": observed.isoformat(),
        },
    )


def _registry(*snapshots: SourceSnapshot) -> SourceSnapshotRegistry:
    advisory = _snapshot("advisory:gs-123", SourceFamily.ATCSCC_ADVISORY, {"text": "GS 123"})
    return SourceSnapshotRegistry(snapshots=(advisory, *snapshots))


def test_selects_latest_eligible_taf_and_excludes_post_issue_and_non_overlapping_reports():
    bundle = build_weather_context(
        _event(),
        _facility(),
        _registry(
            _taf("taf:old", issue=ISSUED_AT - timedelta(hours=3)),
            _taf("taf:latest", issue=ISSUED_AT - timedelta(minutes=30)),
            _taf("taf:post", issue=ISSUED_AT + timedelta(minutes=1)),
            _taf(
                "taf:outside",
                issue=ISSUED_AT - timedelta(minutes=5),
                start=OPERATIONAL_END,
                end=OPERATIONAL_END + timedelta(hours=2),
            ),
        ),
    )

    assert bundle.status == "ok"
    assert bundle.selected_report_ids[0].startswith("weather-report:taf:KJFK:20260519T143000Z:")
    assert [association.relation_type for association in bundle.associations] == [
        "latest_forecast_known_at_issue"
    ]


def test_selects_latest_pre_issue_metar_at_inclusive_two_hour_boundary_and_half_open_operation():
    boundary = ISSUED_AT - timedelta(hours=2)
    pre_latest = ISSUED_AT - timedelta(minutes=2)
    operational_start = OPERATIONAL_START
    operational_end = OPERATIONAL_END
    bundle = build_weather_context(
        _event(),
        _facility(),
        _registry(
            _metar("metar:boundary", observed=boundary),
            _metar("metar:latest", observed=pre_latest),
            _metar("metar:start", observed=operational_start),
            _metar("metar:end", observed=operational_end),
        ),
    )

    assert [":".join(report_id.split(":")[:4]) for report_id in bundle.selected_report_ids] == [
        "weather-report:metar:KJFK:20260519T145800Z",
        "weather-report:metar:KJFK:20260519T160000Z",
    ]
    assert [association.relation_type for association in bundle.associations] == [
        "latest_observation_at_or_before_issue",
        "observation_during_operation",
    ]
    assert bundle.associations[0].relevant_times["observation_time"] == pre_latest.isoformat()


def test_excludes_wrong_station_and_returns_insufficient_for_an_empty_eligible_set():
    bundle = build_weather_context(
        _event(),
        _facility(),
        _registry(
            _taf("taf:other", issue=ISSUED_AT - timedelta(minutes=1), station="KEWR"),
            _metar("metar:other", observed=ISSUED_AT, station="KEWR"),
        ),
    )

    assert bundle.status == "insufficient"
    assert bundle.failure_reason == "no eligible weather reports for canonical facility"
    assert bundle.formal_facts == []
    assert bundle.associations == []


def test_wrong_station_conflicts_cannot_block_the_canonical_facility_selection():
    bundle = build_weather_context(
        _event(),
        _facility(),
        _registry(
            _metar("metar:kjfk", observed=ISSUED_AT),
            _metar("metar:ewr-a", observed=ISSUED_AT, station="KEWR", raw="METAR KEWR A"),
            _metar("metar:ewr-b", observed=ISSUED_AT, station="KEWR", raw="METAR KEWR B"),
        ),
    )

    assert bundle.status == "ok"
    assert bundle.selected_report_ids[0].startswith("weather-report:metar:KJFK:")


@pytest.mark.parametrize(
    ("facility", "reason"),
    [
        (_facility(airport=False), "canonical facility is not an airport"),
        (
            _facility(codes=[CodeValue(scheme="ICAO", value="KJFK"), CodeValue(scheme="icao", value="KJFK")]),
            "canonical facility must have exactly one ICAO airport code",
        ),
    ],
)
def test_blocks_malformed_or_ambiguous_canonical_facility(facility, reason):
    bundle = build_weather_context(_event(), facility, _registry())

    assert bundle.status == "blocked"
    assert bundle.failure_reason == reason


def test_fails_closed_for_wrong_family_forged_checksum_and_conflicting_logical_anchor():
    row = {
        "icaoId": "KJFK",
        "reportTime": ISSUED_AT.isoformat(),
        "rawOb": "METAR KJFK 191500Z",
    }
    good = _snapshot("metar:good", SourceFamily.METAR, row)
    wrong_family = good.model_copy(update={"family": SourceFamily.TAF})
    forged = good.model_copy(update={"content_sha256": "0" * 64})
    conflicting = _metar("metar:conflict", observed=ISSUED_AT, raw="METAR KJFK CONFLICT")

    for registry in (
        _registry(wrong_family),
        SourceSnapshotRegistry.model_construct(
            snapshots=(_snapshot("advisory:gs-123", SourceFamily.ATCSCC_ADVISORY, {"text": "GS 123"}), forged)
        ),
        _registry(good, conflicting),
    ):
        bundle = build_weather_context(_event(), _facility(), registry)
        assert bundle.status == "blocked"
        assert bundle.formal_facts == []


def test_exact_duplicate_deduplicates_and_outputs_stable_ids_and_byte_stable_ordering():
    first = _metar("metar:first", observed=ISSUED_AT - timedelta(minutes=1))
    duplicate = first.model_copy(update={"source_id": "metar:duplicate"})
    bundle_a = build_weather_context(_event(), _facility(), _registry(first, duplicate))
    bundle_b = build_weather_context(_event(), _facility(), _registry(duplicate, first))

    assert bundle_a.model_dump_json() == bundle_b.model_dump_json()
    assert len(bundle_a.selected_report_ids) == 1
    assert bundle_a.associations[0].association_id.startswith("weather-association:")
    assert bundle_a.associations[0].causal_claim is False


def test_emits_only_weather_profile_facts_with_exact_source_trace_and_no_event_edge():
    taf = _taf("taf:source", issue=ISSUED_AT - timedelta(minutes=5))
    metar = _metar("metar:source", observed=ISSUED_AT)
    bundle = build_weather_context(_event(), _facility(), _registry(taf, metar))

    allowed_predicates = {
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
        "https://data.nasa.gov/ontologies/atmonto/data#forecastingAirport",
        "https://data.nasa.gov/ontologies/atmonto/data#metarReportString",
        "https://data.nasa.gov/ontologies/atmonto/data#tafReportString",
        "https://data.nasa.gov/ontologies/atmonto/data#dataIntervalStartTime",
        "https://data.nasa.gov/ontologies/atmonto/data#dataIntervalEndTime",
        "https://data.nasa.gov/ontologies/atmonto/data#forecastIssueTime",
        METEOROLOGICAL_CONDITION_STATUS,
    }
    assert {fact.predicate_iri for fact in bundle.formal_facts} <= allowed_predicates
    assert {fact.subject_class_iri for fact in bundle.formal_facts} == {
        "https://data.nasa.gov/ontologies/atmonto/data#MeteorologicalReport"
    }
    assert all(fact.subject_iri != _event().event_id for fact in bundle.formal_facts)
    assert len(bundle.fact_traces) == len(bundle.formal_facts)
    assert all(
        trace.source_snapshot_sha256
        == next(snapshot for snapshot in (taf, metar) if snapshot.source_id == trace.source_id).content_sha256
        for trace in bundle.fact_traces
    )
    status_facts = [
        fact
        for fact in bundle.formal_facts
        if fact.predicate_iri == METEOROLOGICAL_CONDITION_STATUS
    ]
    assert {
        (fact.source_ids[0], fact.object_value)
        for fact in status_facts
    } == {
        ("metar:source", "observed"),
        ("taf:source", "forecast"),
    }
    assert all(
        fact.datatype_iri == "http://www.w3.org/2001/XMLSchema#string"
        for fact in status_facts
    )


def test_weather_slice_is_closed_to_the_approved_nasa_atmonto_terms():
    slice_path = Path("data/ontology/curated/nasa_atmonto_decision_context_weather_slice.json")
    payload = json.loads(slice_path.read_text(encoding="utf-8"))

    assert {entry["prefixed_name"] for entry in payload["classes"]} == {
        "nas:Airport",
        "data:MeteorologicalReport",
        "data:WeatherCondition",
    }
    assert {entry["prefixed_name"] for entry in payload["object_properties"]} == {
        "data:hasMeteorologicalReport",
        "data:forecastingAirport",
    }
    assert {entry["prefixed_name"] for entry in payload["datatype_properties"]} == {
        "data:metarReportString",
        "data:tafReportString",
        "data:dataIntervalStartTime",
        "data:dataIntervalEndTime",
        "data:forecastIssueTime",
        "data:meteorologicalConditionStatus",
    }


@pytest.mark.parametrize(
    "clock_name",
    ["advisory_issued_at", "operational_start", "operational_end"],
)
def test_event_context_event_rejects_timezone_naive_clocks(clock_name):
    clocks = {
        "advisory_issued_at": ISSUED_AT,
        "operational_start": OPERATIONAL_START,
        "operational_end": OPERATIONAL_END,
    }
    clocks[clock_name] = clocks[clock_name].replace(tzinfo=None)

    with pytest.raises(ValidationError, match="timezone-aware"):
        TMIEventContext(
            run_id="run:naive-clock",
            event_id="urn:test:event:naive-clock",
            advisory_source_id="advisory:naive-clock",
            **clocks,
        )


def test_adapter_blocks_a_bypassed_timezone_naive_event_without_leaking_type_error():
    bypassed_event = TMIEventContext.model_construct(
        run_id="run:bypassed-naive-clock",
        event_id="urn:test:event:bypassed-naive-clock",
        advisory_source_id="advisory:bypassed-naive-clock",
        advisory_issued_at=ISSUED_AT.replace(tzinfo=None),
        operational_start=OPERATIONAL_START,
        operational_end=OPERATIONAL_END,
    )

    bundle = build_weather_context(
        bypassed_event,
        _facility(),
        _registry(_metar("metar:bypassed-naive-clock", observed=ISSUED_AT)),
    )

    assert bundle.status == "blocked"
    assert bundle.failure_reason == "TMI event context clocks must be timezone-aware"


def test_extreme_epoch_returns_blocked_instead_of_leaking_a_platform_exception():
    extreme = _snapshot(
        "taf:extreme-epoch",
        SourceFamily.TAF,
        {
            "icaoId": "KJFK",
            "issueTime": ISSUED_AT.isoformat(),
            "rawTAF": "TAF KJFK EXTREME",
            "validTimeFrom": 10**1000,
            "validTimeTo": 10**1000 + 1,
        },
    )

    bundle = build_weather_context(_event(), _facility(), _registry(extreme))

    assert bundle.status == "blocked"
    assert "timestamp" in bundle.failure_reason


@pytest.mark.parametrize(
    ("facility", "report", "reason"),
    [
        (
            _facility(codes=[CodeValue(scheme="ICAO", value="KJF1")]),
            _metar("metar:facility-code", observed=ISSUED_AT, station="KJF1"),
            "canonical facility must have exactly one ICAO airport code",
        ),
        (
            _facility(),
            _metar("metar:station-code", observed=ISSUED_AT, station="KJF1"),
            "weather source has invalid ICAO station",
        ),
    ],
)
def test_blocks_nonalphabetic_icao_codes_before_emitting_airport_facts(facility, report, reason):
    bundle = build_weather_context(_event(), facility, _registry(report))

    assert bundle.status == "blocked"
    assert bundle.failure_reason.startswith(reason)
    assert bundle.formal_facts == []
