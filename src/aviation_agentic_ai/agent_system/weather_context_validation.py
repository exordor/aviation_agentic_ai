"""Independent source-derived validation for deterministic weather context."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

from aviation_agentic_ai.agent_system.contracts import (
    DecisionContextEvent,
    SourceFamily,
    SourceSnapshot,
    SourceSnapshotRegistry,
    ValidatedFact,
    WeatherContextAssociation,
    WeatherContextBundle,
    WeatherFactTrace,
)
from aviation_agentic_ai.agent_system.weather_context import (
    FORECASTING_AIRPORT,
    FORECAST_ISSUE_TIME,
    INTERVAL_END,
    INTERVAL_START,
    METAR_STRING,
    METEOROLOGICAL_REPORT,
    NAS_AIRPORT,
    RDF_TYPE,
    TAF_STRING,
    XSD_DATETIME,
    XSD_STRING,
)
from aviation_agentic_ai.cross_source.contracts import CanonicalEntity, EntityType


_RelationType = Literal[
    "latest_forecast_known_at_issue",
    "latest_observation_at_or_before_issue",
    "observation_during_operation",
]
_ICAO_AIRPORT_CODE = re.compile(r"[A-Z]{4}\Z")


@dataclass(frozen=True)
class _SourceWeatherReport:
    source: SourceSnapshot
    family: SourceFamily
    station: str
    logical_time: datetime
    interval_start: datetime
    interval_end: datetime
    raw: str
    report_id: str


def _source_datetime(value: object) -> datetime:
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


def _expected_report_id(
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


def _weather_slice_checksum() -> str:
    path = (
        Path(__file__).parents[3]
        / "data/ontology/curated/nasa_atmonto_decision_context_weather_slice.json"
    )
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expected_fact_id(
    report: _SourceWeatherReport,
    predicate: str,
    value: str,
) -> str:
    digest = hashlib.sha256(
        "|".join(
            (
                report.report_id,
                predicate,
                value,
                _weather_slice_checksum(),
            )
        ).encode("utf-8")
    ).hexdigest()[:24]
    return f"weather-fact:{digest}"


def _parse_source_report(snapshot: SourceSnapshot) -> _SourceWeatherReport:
    content_checksum = hashlib.sha256(snapshot.content.encode("utf-8")).hexdigest()
    if snapshot.content_sha256 != content_checksum:
        raise ValueError(
            f"weather source checksum does not match content: {snapshot.source_id}"
        )
    try:
        row = json.loads(snapshot.content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"weather source is not canonical JSON: {snapshot.source_id}"
        ) from exc
    if not isinstance(row, dict):
        raise ValueError(
            f"weather source row must be an object: {snapshot.source_id}"
        )

    family = SourceFamily(snapshot.family)
    station = row.get("icaoId")
    if (
        not isinstance(station, str)
        or not _ICAO_AIRPORT_CODE.fullmatch(station)
    ):
        raise ValueError(
            f"weather source has invalid ICAO station: {snapshot.source_id}"
        )
    if family == SourceFamily.METAR:
        if any(
            field in row for field in ("issueTime", "validTimeFrom", "validTimeTo")
        ):
            raise ValueError(
                f"weather source family does not match METAR row: {snapshot.source_id}"
            )
        raw = row.get("rawOb")
        if not isinstance(raw, str) or not raw:
            raise ValueError(
                f"METAR source has no raw observation: {snapshot.source_id}"
            )
        observed = _source_datetime(row.get("reportTime"))
        return _SourceWeatherReport(
            source=snapshot,
            family=family,
            station=station,
            logical_time=observed,
            interval_start=observed,
            interval_end=observed,
            raw=raw,
            report_id=_expected_report_id(
                family,
                station,
                observed,
                raw,
                snapshot.content_sha256,
            ),
        )
    if family == SourceFamily.TAF:
        if "reportTime" in row or "rawOb" in row:
            raise ValueError(
                f"weather source family does not match TAF row: {snapshot.source_id}"
            )
        raw = row.get("rawTAF")
        if not isinstance(raw, str) or not raw:
            raise ValueError(
                f"TAF source has no raw forecast: {snapshot.source_id}"
            )
        issue = _source_datetime(row.get("issueTime"))
        start = _source_datetime(row.get("validTimeFrom"))
        end = _source_datetime(row.get("validTimeTo"))
        if end <= start:
            raise ValueError(
                f"TAF source has impossible validity interval: {snapshot.source_id}"
            )
        return _SourceWeatherReport(
            source=snapshot,
            family=family,
            station=station,
            logical_time=issue,
            interval_start=start,
            interval_end=end,
            raw=raw,
            report_id=_expected_report_id(
                family,
                station,
                issue,
                raw,
                snapshot.content_sha256,
            ),
        )
    raise ValueError(f"unsupported weather source family: {snapshot.source_id}")


def _source_airport_code(facility: CanonicalEntity) -> str:
    if facility.entity_type != EntityType.AIRPORT:
        raise ValueError("canonical facility is not an airport")
    icao_codes = [
        code.value for code in facility.codes if code.scheme.upper() == "ICAO"
    ]
    if (
        len(icao_codes) != 1
        or not _ICAO_AIRPORT_CODE.fullmatch(icao_codes[0])
    ):
        raise ValueError(
            "canonical facility must have exactly one ICAO airport code"
        )
    return icao_codes[0]


def _deduplicate_source_reports(
    reports: list[_SourceWeatherReport],
) -> list[_SourceWeatherReport]:
    by_anchor: dict[
        tuple[SourceFamily, str, datetime],
        list[_SourceWeatherReport],
    ] = {}
    for report in reports:
        anchor = (report.family, report.station, report.logical_time)
        by_anchor.setdefault(anchor, []).append(report)
    selected: list[_SourceWeatherReport] = []
    for anchor in sorted(by_anchor):
        matches = by_anchor[anchor]
        identities = {
            (report.raw, report.interval_start, report.interval_end)
            for report in matches
        }
        if len(identities) > 1:
            raise ValueError("conflicting duplicate weather logical anchor")
        selected.append(
            min(
                matches,
                key=lambda report: (
                    report.source.source_id,
                    report.source.content_sha256,
                ),
            )
        )
    return selected


def _source_weather_reports(
    registry: SourceSnapshotRegistry,
    facility: CanonicalEntity,
) -> list[_SourceWeatherReport]:
    airport_code = _source_airport_code(facility)
    parsed = [
        _parse_source_report(snapshot)
        for snapshot in registry.snapshots
        if snapshot.family in {SourceFamily.METAR, SourceFamily.TAF}
    ]
    return _deduplicate_source_reports(
        [report for report in parsed if report.station == airport_code]
    )


def _expected_selections(
    event: DecisionContextEvent,
    reports: list[_SourceWeatherReport],
) -> list[tuple[_SourceWeatherReport, _RelationType, str]]:
    tafs = [
        report
        for report in reports
        if report.family == SourceFamily.TAF
        and report.logical_time <= event.advisory_issued_at
        and report.interval_start < event.operational_end
        and report.interval_end > event.operational_start
    ]
    selections: list[tuple[_SourceWeatherReport, _RelationType, str]] = []
    if tafs:
        latest_issue = max(report.logical_time for report in tafs)
        latest = min(
            [report for report in tafs if report.logical_time == latest_issue],
            key=lambda report: (
                report.source.source_id,
                report.source.content_sha256,
            ),
        )
        selections.append(
            (
                latest,
                "latest_forecast_known_at_issue",
                "latest eligible TAF by issue time",
            )
        )

    metars = [
        report for report in reports if report.family == SourceFamily.METAR
    ]
    pre_start = event.advisory_issued_at - timedelta(hours=2)
    pre_issue = [
        report
        for report in metars
        if pre_start <= report.logical_time <= event.advisory_issued_at
    ]
    if pre_issue:
        latest_observation = max(report.logical_time for report in pre_issue)
        latest = min(
            [
                report
                for report in pre_issue
                if report.logical_time == latest_observation
            ],
            key=lambda report: (
                report.source.source_id,
                report.source.content_sha256,
            ),
        )
        selections.append(
            (
                latest,
                "latest_observation_at_or_before_issue",
                "latest METAR within two hours",
            )
        )
    during = sorted(
        [
            report
            for report in metars
            if event.operational_start
            <= report.logical_time
            < event.operational_end
        ],
        key=lambda report: (
            report.logical_time,
            report.report_id,
            report.source.source_id,
        ),
    )
    selections.extend(
        (
            report,
            "observation_during_operation",
            "METAR in half-open operational period",
        )
        for report in during
    )
    return selections


def _expected_facts(
    report: _SourceWeatherReport,
    facility: CanonicalEntity,
) -> list[ValidatedFact]:
    values: list[tuple[str, str, str, str | None, str | None]] = [
        (
            RDF_TYPE,
            METEOROLOGICAL_REPORT,
            "iri",
            METEOROLOGICAL_REPORT,
            None,
        ),
        (
            FORECASTING_AIRPORT,
            facility.entity_id,
            "iri",
            NAS_AIRPORT,
            None,
        ),
        (
            INTERVAL_START,
            report.interval_start.isoformat(),
            "literal",
            None,
            XSD_DATETIME,
        ),
        (
            INTERVAL_END,
            report.interval_end.isoformat(),
            "literal",
            None,
            XSD_DATETIME,
        ),
    ]
    if report.family == SourceFamily.METAR:
        values.append(
            (METAR_STRING, report.raw, "literal", None, XSD_STRING)
        )
    else:
        values.extend(
            [
                (TAF_STRING, report.raw, "literal", None, XSD_STRING),
                (
                    FORECAST_ISSUE_TIME,
                    report.logical_time.isoformat(),
                    "literal",
                    None,
                    XSD_DATETIME,
                ),
            ]
        )
    return [
        ValidatedFact(
            fact_id=_expected_fact_id(report, predicate, value),
            subject_iri=f"urn:aviation-agentic-ai:{report.report_id}",
            subject_class_iri=METEOROLOGICAL_REPORT,
            predicate_iri=predicate,
            object_kind=object_kind,
            object_value=value,
            object_class_iri=object_class_iri,
            datatype_iri=datatype_iri,
            source_ids=[report.source.source_id],
            evidence_texts=[report.raw],
        )
        for predicate, value, object_kind, object_class_iri, datatype_iri in values
    ]


def _relevant_times(
    event: DecisionContextEvent,
    report: _SourceWeatherReport,
) -> dict[str, str]:
    values = {
        "advisory_issued_at": event.advisory_issued_at.astimezone(UTC).isoformat(),
        "operational_end": event.operational_end.astimezone(UTC).isoformat(),
        "operational_start": event.operational_start.astimezone(UTC).isoformat(),
    }
    if report.family == SourceFamily.METAR:
        values["observation_time"] = report.logical_time.isoformat()
    else:
        values["forecast_issue_time"] = report.logical_time.isoformat()
        values["forecast_valid_from"] = report.interval_start.isoformat()
        values["forecast_valid_to"] = report.interval_end.isoformat()
    return values


def _expected_association(
    event: DecisionContextEvent,
    facility: CanonicalEntity,
    report: _SourceWeatherReport,
    relation_type: _RelationType,
    selection_method: str,
) -> WeatherContextAssociation:
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
        relevant_times=_relevant_times(event, report),
        source_id=report.source.source_id,
        source_snapshot_sha256=report.source.content_sha256,
        causal_claim=False,
    )


def _expected_bundle(
    event: DecisionContextEvent,
    facility: CanonicalEntity,
    registry: SourceSnapshotRegistry,
) -> WeatherContextBundle:
    selections = _expected_selections(
        event,
        _source_weather_reports(registry, facility),
    )
    if not selections:
        return WeatherContextBundle(
            status="insufficient",
            failure_reason="no eligible weather reports for canonical facility",
        )
    selected = {report.report_id: report for report, _, _ in selections}
    facts = sorted(
        [
            fact
            for report in selected.values()
            for fact in _expected_facts(report, facility)
        ],
        key=lambda fact: fact.fact_id,
    )
    associations = sorted(
        [
            _expected_association(
                event,
                facility,
                report,
                relation_type,
                selection_method,
            )
            for report, relation_type, selection_method in selections
        ],
        key=lambda association: association.association_id,
    )
    reports_by_id = {report.report_id: report for report in selected.values()}
    traces = [
        WeatherFactTrace(
            fact_id=fact.fact_id,
            source_id=reports_by_id[
                fact.subject_iri.removeprefix("urn:aviation-agentic-ai:")
            ].source.source_id,
            source_snapshot_sha256=reports_by_id[
                fact.subject_iri.removeprefix("urn:aviation-agentic-ai:")
            ].source.content_sha256,
            evidence_text=reports_by_id[
                fact.subject_iri.removeprefix("urn:aviation-agentic-ai:")
            ].raw,
        )
        for fact in facts
    ]
    return WeatherContextBundle(
        status="ok",
        selected_report_ids=sorted(selected),
        formal_facts=facts,
        fact_traces=traces,
        associations=associations,
    )


def _unique_map(rows: list[object], id_field: str, label: str) -> dict[str, object]:
    identifiers = [str(getattr(row, id_field)) for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError(f"duplicate {label} ID")
    return {identifier: row for identifier, row in zip(identifiers, rows, strict=True)}


def validate_weather_context_bundle(
    bundle: WeatherContextBundle,
    *,
    event: DecisionContextEvent,
    facility: CanonicalEntity,
    registry: SourceSnapshotRegistry,
) -> None:
    """Validate a bundle independently against its pinned weather snapshots."""

    expected = _expected_bundle(event, facility, registry)
    if bundle.status != expected.status:
        raise ValueError("weather bundle status does not match eligible source context")
    if bundle.status != "ok":
        if (
            bundle.selected_report_ids
            or bundle.formal_facts
            or bundle.fact_traces
            or bundle.associations
        ):
            raise ValueError("non-ok weather bundle contains publishable rows")
        if bundle.failure_reason != expected.failure_reason:
            raise ValueError("weather bundle failure reason is not source-derived")
        return

    if bundle.selected_report_ids != expected.selected_report_ids:
        raise ValueError("weather selected report IDs are not source-derived")
    actual_facts = _unique_map(bundle.formal_facts, "fact_id", "weather fact")
    expected_facts = _unique_map(expected.formal_facts, "fact_id", "weather fact")
    if set(actual_facts) != set(expected_facts):
        raise ValueError("weather fact ID set is incomplete or unexpected")
    for fact_id, expected_fact in expected_facts.items():
        actual_fact = actual_facts[fact_id]
        if actual_fact != expected_fact:
            predicate = (
                "rdf:type"
                if expected_fact.predicate_iri == RDF_TYPE
                else expected_fact.predicate_iri
            )
            raise ValueError(
                f"weather fact violates source-derived {predicate} contract"
            )

    actual_traces = _unique_map(
        bundle.fact_traces,
        "fact_id",
        "weather trace",
    )
    expected_traces = _unique_map(
        expected.fact_traces,
        "fact_id",
        "weather trace",
    )
    if actual_traces != expected_traces:
        raise ValueError("weather fact traces are not source-derived")

    actual_associations = _unique_map(
        bundle.associations,
        "association_id",
        "weather association",
    )
    expected_associations = _unique_map(
        expected.associations,
        "association_id",
        "weather association",
    )
    if actual_associations != expected_associations:
        report_sources: dict[str, tuple[str, str]] = {}
        for association in bundle.associations:
            binding = (
                association.source_id,
                association.source_snapshot_sha256,
            )
            existing = report_sources.get(association.report_id)
            if existing is not None and existing != binding:
                raise ValueError("conflicting weather report source binding")
            report_sources[association.report_id] = binding
        raise ValueError(
            "weather associations violate source-derived family, time, or ID contract"
        )
