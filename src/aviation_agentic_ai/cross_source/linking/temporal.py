from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Iterable

from aviation_agentic_ai.cross_source.contracts import (
    AlignmentDecision,
    AlignmentStatus,
    CanonicalEntity,
    CrossSourceLink,
    EntityType,
    Mention,
    MentionType,
    TimeInterval,
)
from aviation_agentic_ai.cross_source.identifiers import normalize_code, stable_id


@dataclass(frozen=True)
class LinkingRun:
    links: list[CrossSourceLink]
    weather_records: dict[str, dict[str, Any]]


def _parse_datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, (int, float)):
        parsed = datetime.fromtimestamp(value, tz=UTC)
    else:
        text = str(value).strip()
        if not text:
            raise ValueError("Cannot parse an empty datetime")
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _record_interval(record: dict[str, Any], *, source_family: str) -> TimeInterval:
    temporal = dict(record.get("temporal_alignment") or {})
    start = temporal.get("source_period_start")
    end = temporal.get("source_period_end")
    if start is None or end is None:
        if source_family == "metar":
            start = end = record.get("reportTime") or record.get("obsTime")
        elif source_family == "taf":
            start = record.get("validTimeFrom")
            end = record.get("validTimeTo")
    interval = TimeInterval(start=_parse_datetime(start), end=_parse_datetime(end))
    if interval.end < interval.start:
        raise ValueError(f"Invalid {source_family} interval: end precedes start")
    return interval


def _advisory_interval(record: dict[str, Any]) -> TimeInterval:
    temporal = dict(record.get("temporal_alignment") or {})
    interval = TimeInterval(
        start=_parse_datetime(temporal.get("source_period_start")),
        end=_parse_datetime(temporal.get("source_period_end")),
    )
    if interval.end < interval.start:
        raise ValueError("Invalid advisory interval: end precedes start")
    return interval


def _weather_id(record: dict[str, Any], source_family: str) -> str:
    station = normalize_code(record.get("icaoId"))
    if source_family == "metar":
        anchor = record.get("reportTime") or record.get("obsTime")
    else:
        anchor = record.get("issueTime") or record.get("validTimeFrom")
    return stable_id(source_family, station, anchor, record.get("rawOb") or record.get("rawTAF"))


def _airport_icao_codes(facilities: Iterable[CanonicalEntity]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for facility in facilities:
        if facility.entity_type is not EntityType.AIRPORT:
            continue
        codes = {
            normalize_code(code.value)
            for code in facility.codes
            if code.scheme.upper() == "ICAO" and normalize_code(code.value)
        }
        if codes:
            result[facility.entity_id] = codes
    return result


def _accepted_airports_by_source(
    mentions: Iterable[Mention],
    decisions: Iterable[AlignmentDecision],
    airport_ids: set[str],
) -> dict[str, set[str]]:
    mention_by_id = {mention.mention_id: mention for mention in mentions}
    accepted: dict[str, set[str]] = defaultdict(set)
    for decision in decisions:
        mention = mention_by_id.get(decision.mention_id)
        if (
            mention is None
            or mention.mention_type is not MentionType.FACILITY_CODE
            or decision.status is not AlignmentStatus.ACCEPTED
            or decision.target_id not in airport_ids
        ):
            continue
        accepted[mention.source_id].add(str(decision.target_id))
    return accepted


def _overlaps(left: TimeInterval, right: TimeInterval) -> bool:
    return left.start <= right.end and right.start <= left.end


def link_weather_records(
    advisories: Iterable[dict[str, Any]],
    *,
    mentions: Iterable[Mention],
    decisions: Iterable[AlignmentDecision],
    facilities: Iterable[CanonicalEntity],
    metar_rows: Iterable[dict[str, Any]],
    taf_rows: Iterable[dict[str, Any]],
    config: dict[str, Any],
) -> LinkingRun:
    facility_icaos = _airport_icao_codes(facilities)
    accepted = _accepted_airports_by_source(mentions, decisions, set(facility_icaos))
    linking_config = config["temporal_linking"]
    before = timedelta(minutes=int(linking_config["metar_before_minutes"]))
    after = timedelta(minutes=int(linking_config["metar_after_minutes"]))

    weather_by_station: dict[tuple[str, str], list[tuple[str, dict[str, Any], TimeInterval]]] = (
        defaultdict(list)
    )
    weather_records: dict[str, dict[str, Any]] = {}
    for family, rows in (("metar", metar_rows), ("taf", taf_rows)):
        for row in rows:
            station = normalize_code(row.get("icaoId"))
            if not station:
                continue
            source_id = _weather_id(row, family)
            interval = _record_interval(row, source_family=family)
            weather_records[source_id] = row
            weather_by_station[(family, station)].append((source_id, row, interval))

    links_by_id: dict[str, CrossSourceLink] = {}
    for advisory in advisories:
        source_id = str(advisory["source_id"])
        interval = _advisory_interval(advisory)
        expanded_metar = TimeInterval(start=interval.start - before, end=interval.end + after)
        for facility_id in sorted(accepted.get(source_id, set())):
            for station in sorted(facility_icaos[facility_id]):
                for family in ("metar", "taf"):
                    for weather_id, row, evidence_interval in weather_by_station.get(
                        (family, station), []
                    ):
                        if family == "metar":
                            linked = _overlaps(expanded_metar, evidence_interval)
                            method = "accepted_facility_plus_metar_window"
                            predicate = "hasContemporaneousObservation"
                            evidence_text = str(row.get("rawOb") or "")
                        else:
                            linked = _overlaps(interval, evidence_interval)
                            method = "accepted_facility_plus_taf_validity_overlap"
                            predicate = "hasOverlappingForecast"
                            evidence_text = str(row.get("rawTAF") or "")
                        if not linked or not evidence_text:
                            continue
                        link_id = stable_id(
                            "link", source_id, predicate, weather_id, facility_id
                        )
                        links_by_id[link_id] = CrossSourceLink(
                            link_id=link_id,
                            subject_id=source_id,
                            predicate=predicate,
                            object_id=weather_id,
                            link_method=method,
                            facility_id=facility_id,
                            advisory_interval=interval,
                            evidence_interval=evidence_interval,
                            authority_sources=[
                                config["snapshot_set_id"],
                                "accepted_facility_alignment",
                            ],
                            evidence_text=evidence_text,
                            causal_claim=False,
                        )

    return LinkingRun(
        links=[links_by_id[key] for key in sorted(links_by_id)],
        weather_records=weather_records,
    )
