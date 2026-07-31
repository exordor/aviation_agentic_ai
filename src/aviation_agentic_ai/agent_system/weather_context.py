"""Deterministic, non-causal weather context selection for a resolved event."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

from aviation_agentic_ai.agent_system.contracts import (
    TMIEventContext,
    SourceFamily,
    SourceSnapshot,
    SourceSnapshotRegistry,
    ValidatedFact,
    ValidationProfileRef,
    WeatherContextAssociation,
    WeatherContextBundle,
    WeatherFactTrace,
)
from aviation_agentic_ai.authority.contracts import CanonicalEntity, EntityType
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.validation_profiles import (
    ValidationProfileRegistry,
    load_validation_profile_registry,
)


RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
XSD_DATETIME = "http://www.w3.org/2001/XMLSchema#dateTime"
XSD_STRING = "http://www.w3.org/2001/XMLSchema#string"
NAS_AIRPORT = "https://data.nasa.gov/ontologies/atmonto/NAS#Airport"
METEOROLOGICAL_REPORT = "https://data.nasa.gov/ontologies/atmonto/data#MeteorologicalReport"
METEOROLOGICAL_CONDITION_STATUS = (
    "https://data.nasa.gov/ontologies/atmonto/data#"
    "meteorologicalConditionStatus"
)
FORECASTING_AIRPORT = "https://data.nasa.gov/ontologies/atmonto/data#forecastingAirport"
METAR_STRING = "https://data.nasa.gov/ontologies/atmonto/data#metarReportString"
TAF_STRING = "https://data.nasa.gov/ontologies/atmonto/data#tafReportString"
INTERVAL_START = "https://data.nasa.gov/ontologies/atmonto/data#dataIntervalStartTime"
INTERVAL_END = "https://data.nasa.gov/ontologies/atmonto/data#dataIntervalEndTime"
FORECAST_ISSUE_TIME = "https://data.nasa.gov/ontologies/atmonto/data#forecastIssueTime"
ICAO_AIRPORT_CODE = re.compile(r"[A-Z]{4}\Z")


@dataclass(frozen=True)
class _WeatherReport:
    source: SourceSnapshot
    family: SourceFamily
    station: str
    logical_time: datetime
    interval_start: datetime
    interval_end: datetime
    raw: str
    report_id: str


def _slice_checksum() -> str:
    path = Path(__file__).parents[3] / "data/ontology/curated/nasa_atmonto_decision_context_weather_slice.json"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _as_datetime(value: object) -> datetime:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            return datetime.fromtimestamp(value, tz=UTC)
        except (OverflowError, OSError, ValueError) as exc:
            raise ValueError("epoch timestamp is out of supported range") from exc
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timestamp must include an offset")
        return parsed.astimezone(UTC)
    raise ValueError("timestamp must be ISO 8601 or epoch seconds")


def _time_token(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def _report_id(
    family: SourceFamily,
    station: str,
    logical_time: datetime,
    raw: str,
    snapshot_checksum: str,
) -> str:
    raw_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return (
        f"weather-report:{family.value}:{station}:{_time_token(logical_time)}:"
        f"{raw_hash}:{snapshot_checksum[:16]}"
    )


def _fact_id(report: _WeatherReport, predicate: str, value: str) -> str:
    digest = hashlib.sha256(
        "|".join((report.report_id, predicate, value, _slice_checksum())).encode("utf-8")
    ).hexdigest()[:24]
    return f"weather-fact:{digest}"


def _parse_report(snapshot: SourceSnapshot) -> _WeatherReport:
    if snapshot.content_sha256 != hashlib.sha256(snapshot.content.encode("utf-8")).hexdigest():
        raise ValueError(f"weather source checksum does not match content: {snapshot.source_id}")
    try:
        row = json.loads(snapshot.content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"weather source is not canonical JSON: {snapshot.source_id}") from exc
    if not isinstance(row, dict):
        raise ValueError(f"weather source row must be an object: {snapshot.source_id}")

    family = SourceFamily(snapshot.family)
    station = row.get("icaoId")
    if not isinstance(station, str) or not ICAO_AIRPORT_CODE.fullmatch(station):
        raise ValueError(f"weather source has invalid ICAO station: {snapshot.source_id}")
    if family == SourceFamily.METAR:
        if "issueTime" in row or "validTimeFrom" in row or "validTimeTo" in row:
            raise ValueError(f"weather source family does not match METAR row: {snapshot.source_id}")
        raw = row.get("rawOb")
        if not isinstance(raw, str) or not raw:
            raise ValueError(f"METAR source has no raw observation: {snapshot.source_id}")
        observed = _as_datetime(row.get("reportTime"))
        return _WeatherReport(
            source=snapshot,
            family=family,
            station=station,
            logical_time=observed,
            interval_start=observed,
            interval_end=observed,
            raw=raw,
            report_id=_report_id(family, station, observed, raw, snapshot.content_sha256),
        )
    if family == SourceFamily.TAF:
        if "reportTime" in row or "rawOb" in row:
            raise ValueError(f"weather source family does not match TAF row: {snapshot.source_id}")
        raw = row.get("rawTAF")
        if not isinstance(raw, str) or not raw:
            raise ValueError(f"TAF source has no raw forecast: {snapshot.source_id}")
        issue = _as_datetime(row.get("issueTime"))
        start = _as_datetime(row.get("validTimeFrom"))
        end = _as_datetime(row.get("validTimeTo"))
        if end <= start:
            raise ValueError(f"TAF source has impossible validity interval: {snapshot.source_id}")
        return _WeatherReport(
            source=snapshot,
            family=family,
            station=station,
            logical_time=issue,
            interval_start=start,
            interval_end=end,
            raw=raw,
            report_id=_report_id(family, station, issue, raw, snapshot.content_sha256),
        )
    raise ValueError(f"unsupported weather source family: {snapshot.source_id}")


def _canonical_airport_code(facility: CanonicalEntity) -> str:
    if facility.entity_type != EntityType.AIRPORT:
        raise ValueError("canonical facility is not an airport")
    icao_codes = [code.value for code in facility.codes if code.scheme.upper() == "ICAO"]
    if len(icao_codes) != 1 or not ICAO_AIRPORT_CODE.fullmatch(icao_codes[0]):
        raise ValueError("canonical facility must have exactly one ICAO airport code")
    return icao_codes[0]


def _require_timezone_aware_event_clock(event: TMIEventContext) -> None:
    clocks = (
        event.advisory_issued_at,
        event.operational_start,
        event.operational_end,
    )
    if any(clock.tzinfo is None or clock.utcoffset() is None for clock in clocks):
        raise ValueError("TMI event context clocks must be timezone-aware")


def _deduplicate_reports(reports: list[_WeatherReport]) -> list[_WeatherReport]:
    by_anchor: dict[tuple[SourceFamily, str, datetime], list[_WeatherReport]] = {}
    for report in reports:
        by_anchor.setdefault((report.family, report.station, report.logical_time), []).append(report)
    selected: list[_WeatherReport] = []
    for anchor in sorted(by_anchor):
        matches = by_anchor[anchor]
        identities = {(report.raw, report.interval_start, report.interval_end) for report in matches}
        if len(identities) > 1:
            raise ValueError("conflicting duplicate weather logical anchor")
        selected.append(min(matches, key=lambda report: (report.source.source_id, report.source.content_sha256)))
    return selected


def _association(
    event: TMIEventContext,
    facility: CanonicalEntity,
    report: _WeatherReport,
    relation_type: Literal[
        "latest_forecast_known_at_issue",
        "latest_observation_at_or_before_issue",
        "observation_during_operation",
    ],
    selection_method: str,
) -> WeatherContextAssociation:
    relevant_times = {
        "advisory_issued_at": event.advisory_issued_at.astimezone(UTC).isoformat(),
        "operational_end": event.operational_end.astimezone(UTC).isoformat(),
        "operational_start": event.operational_start.astimezone(UTC).isoformat(),
    }
    if report.family == SourceFamily.METAR:
        relevant_times["observation_time"] = report.logical_time.isoformat()
    else:
        relevant_times["forecast_issue_time"] = report.logical_time.isoformat()
        relevant_times["forecast_valid_from"] = report.interval_start.isoformat()
        relevant_times["forecast_valid_to"] = report.interval_end.isoformat()
    association_id = "weather-association:" + hashlib.sha256(
        "|".join(
            (
                event.run_id,
                event.event_id,
                report.report_id,
                facility.entity_id,
                relation_type,
                report.source.content_sha256,
            )
        ).encode("utf-8")
    ).hexdigest()[:24]
    return WeatherContextAssociation(
        association_id=association_id,
        run_id=event.run_id,
        event_id=event.event_id,
        report_id=report.report_id,
        facility_id=facility.entity_id,
        relation_type=relation_type,
        selection_method=selection_method,
        relevant_times=relevant_times,
        source_id=report.source.source_id,
        source_snapshot_sha256=report.source.content_sha256,
        causal_claim=False,
    )


def _facts_for_report(
    report: _WeatherReport,
    facility: CanonicalEntity,
    validation_profile: ValidationProfileRef,
) -> list[ValidatedFact]:
    values: list[tuple[str, str, str, str | None, str | None]] = [
        (RDF_TYPE, METEOROLOGICAL_REPORT, "iri", METEOROLOGICAL_REPORT, None),
        (FORECASTING_AIRPORT, facility.entity_id, "iri", NAS_AIRPORT, None),
        (INTERVAL_START, report.interval_start.isoformat(), "literal", None, XSD_DATETIME),
        (INTERVAL_END, report.interval_end.isoformat(), "literal", None, XSD_DATETIME),
        (
            METEOROLOGICAL_CONDITION_STATUS,
            (
                "observed"
                if report.family == SourceFamily.METAR
                else "forecast"
            ),
            "literal",
            None,
            XSD_STRING,
        ),
    ]
    if report.family == SourceFamily.METAR:
        values.append((METAR_STRING, report.raw, "literal", None, XSD_STRING))
    else:
        values.extend(
            [
                (TAF_STRING, report.raw, "literal", None, XSD_STRING),
                (FORECAST_ISSUE_TIME, report.logical_time.isoformat(), "literal", None, XSD_DATETIME),
            ]
        )
    return [
        ValidatedFact(
            fact_id=_fact_id(report, predicate, value),
            subject_iri=f"urn:aviation-agentic-ai:{report.report_id}",
            subject_class_iri=METEOROLOGICAL_REPORT,
            predicate_iri=predicate,
            object_kind=object_kind,
            object_value=value,
            object_class_iri=object_class_iri,
            datatype_iri=datatype_iri,
            source_ids=[report.source.source_id],
            evidence_texts=[report.raw],
            validation_profile=validation_profile,
            evidence_mode="source_text",
            evidence_ref=_fact_id(report, predicate, value),
        )
        for predicate, value, object_kind, object_class_iri, datatype_iri in values
    ]


def build_weather_context(
    event: TMIEventContext,
    canonical_facility: CanonicalEntity,
    snapshot_registry: SourceSnapshotRegistry,
    profile_registry: ValidationProfileRegistry | None = None,
) -> WeatherContextBundle:
    """Select source-pinned METAR/TAF context without asserting causality."""

    try:
        profile_registry = profile_registry or load_validation_profile_registry(
            decision_guide=load_schema_guide()
        )
        weather_ref = next(ref for ref in profile_registry.refs if ref.layer == "weather")
        weather_profile = profile_registry.require_layer(weather_ref, "weather")
        _require_timezone_aware_event_clock(event)
        airport_code = _canonical_airport_code(canonical_facility)
        weather_snapshots = [
            snapshot
            for snapshot in snapshot_registry.snapshots
            if snapshot.family in {SourceFamily.METAR, SourceFamily.TAF}
        ]
        reports = [_parse_report(snapshot) for snapshot in weather_snapshots]
    except (OverflowError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return WeatherContextBundle(status="blocked", failure_reason=str(exc))

    try:
        station_reports = _deduplicate_reports(
            [report for report in reports if report.station == airport_code]
        )
    except ValueError as exc:
        return WeatherContextBundle(status="blocked", failure_reason=str(exc))
    tafs = [
        report
        for report in station_reports
        if report.family == SourceFamily.TAF
        and report.logical_time <= event.advisory_issued_at
        and report.interval_start < event.operational_end
        and report.interval_end > event.operational_start
    ]
    latest_taf: _WeatherReport | None = None
    if tafs:
        latest_time = max(report.logical_time for report in tafs)
        tied = [report for report in tafs if report.logical_time == latest_time]
        if len({report.raw for report in tied}) > 1:
            return WeatherContextBundle(status="blocked", failure_reason="conflicting latest eligible TAF")
        latest_taf = min(tied, key=lambda report: (report.source.source_id, report.source.content_sha256))

    metars = [report for report in station_reports if report.family == SourceFamily.METAR]
    pre_window_start = event.advisory_issued_at - timedelta(hours=2)
    pre_candidates = [
        report
        for report in metars
        if pre_window_start <= report.logical_time <= event.advisory_issued_at
    ]
    latest_metar = (
        min(
            [report for report in pre_candidates if report.logical_time == max(r.logical_time for r in pre_candidates)],
            key=lambda report: (report.source.source_id, report.source.content_sha256),
        )
        if pre_candidates
        else None
    )
    during_metars = sorted(
        [
            report
            for report in metars
            if event.operational_start <= report.logical_time < event.operational_end
        ],
        key=lambda report: (report.logical_time, report.report_id, report.source.source_id),
    )

    association_pairs: list[tuple[_WeatherReport, str, str]] = []
    if latest_taf is not None:
        association_pairs.append(
            (latest_taf, "latest_forecast_known_at_issue", "latest eligible TAF by issue time")
        )
    if latest_metar is not None:
        association_pairs.append(
            (latest_metar, "latest_observation_at_or_before_issue", "latest METAR within two hours")
        )
    association_pairs.extend(
        (report, "observation_during_operation", "METAR in half-open operational period")
        for report in during_metars
    )
    if not association_pairs:
        return WeatherContextBundle(
            status="insufficient",
            failure_reason="no eligible weather reports for canonical facility",
        )

    selected_by_id = {report.report_id: report for report, _, _ in association_pairs}
    formal_facts = sorted(
        [
            fact
            for report in selected_by_id.values()
            for fact in _facts_for_report(report, canonical_facility, weather_profile.ref)
        ],
        key=lambda fact: fact.fact_id,
    )
    sources_by_fact_id = {
        fact.fact_id: selected_by_id[fact.subject_iri.removeprefix("urn:aviation-agentic-ai:")]
        for fact in formal_facts
    }
    associations = sorted(
        [
            _association(event, canonical_facility, report, relation_type, selection_method)
            for report, relation_type, selection_method in association_pairs
        ],
        key=lambda association: association.association_id,
    )
    traces = [
        WeatherFactTrace(
            fact_id=fact.fact_id,
            source_id=sources_by_fact_id[fact.fact_id].source.source_id,
            source_snapshot_sha256=sources_by_fact_id[fact.fact_id].source.content_sha256,
            evidence_text=sources_by_fact_id[fact.fact_id].raw,
        )
        for fact in formal_facts
    ]
    return WeatherContextBundle(
        status="ok",
        selected_report_ids=sorted(selected_by_id),
        formal_facts=formal_facts,
        fact_traces=traces,
        associations=associations,
    )
