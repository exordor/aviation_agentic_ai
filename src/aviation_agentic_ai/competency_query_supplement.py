"""Bounded data supplement for the four ATMONTO competency queries.

This offline supplement is not ingested into the authoritative evidence store
or exposed through the public Query Agent. It reconstructs flight/trajectory
query inputs that the current TMI-event vertical slice does not contain.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter, defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from itertools import combinations, product
from pathlib import Path
from zoneinfo import ZoneInfo

from rdflib import Graph, Namespace, RDF

from aviation_agentic_ai.config import load_yaml, resolve_project_path
from aviation_agentic_ai.cross_source.alignment.registry import parse_nasr_apt_line


ATM = Namespace("https://data.nasa.gov/ontologies/atmonto/ATM#")
GEN = Namespace("https://data.nasa.gov/ontologies/atmonto/general#")


@dataclass(frozen=True)
class SectorPassage:
    """One reported flight-track point associated with an ATC sector."""

    flight_id: str
    call_sign: str
    track_point_id: str
    fix_id: str
    sector_id: str
    reporting_time: datetime


@dataclass(frozen=True)
class SectorRanking:
    """Flight and track-point counts for one sector during one UTC hour."""

    sector_id: str
    hour: int
    unique_flight_count: int
    track_point_count: int
    source_dates: tuple[date, ...]


@dataclass(frozen=True)
class FlightPair:
    """Closest observed passages for two distinct flights in one sector."""

    sector_id: str
    passage_date: date
    first_flight_id: str
    first_call_sign: str
    first_reporting_time: datetime
    second_flight_id: str
    second_call_sign: str
    second_reporting_time: datetime
    minutes_apart: int


@dataclass(frozen=True)
class FlightDeparture:
    """Minimal public flight record needed by F1 and F3S."""

    flight_id: str
    flight_date: date
    reporting_carrier: str
    flight_number: str
    tail_number: str
    origin: str
    destination: str
    wheels_off: datetime | None
    wheels_off_time_basis: str = "UTC"


@dataclass(frozen=True)
class AircraftTechnicalRecord:
    """Non-personal FAA aircraft-registry fields used for model lookup."""

    tail_number: str
    manufacturer: str
    model: str


@dataclass(frozen=True)
class AircraftMatchedDeparture:
    """A flight departure joined to a technical aircraft-model snapshot."""

    flight_id: str
    flight_date: date
    reporting_carrier: str
    carrier_role: str
    flight_number: str
    tail_number: str
    origin: str
    destination: str
    aircraft_manufacturer: str
    aircraft_model: str


@dataclass(frozen=True)
class WeatherObservation:
    """A timestamped airport weather observation used as context."""

    station: str
    observed_at: datetime
    weather_codes: tuple[str, ...]
    raw_text: str


@dataclass(frozen=True)
class RainAssociatedDeparture:
    """A temporal association between a departure and a rain observation."""

    flight_id: str
    flight_date: date
    origin: str
    wheels_off: datetime
    station: str
    observed_at: datetime
    weather_codes: tuple[str, ...]
    minutes_apart: float
    association_role: str
    causal_claim: bool
    weather_raw_text: str = ""
    reporting_carrier: str = ""
    flight_number: str = ""


def extract_sector_passages(graph: Graph) -> list[SectorPassage]:
    """Extract flight-track passages from an ATMONTO-compatible RDF graph."""

    passages: list[SectorPassage] = []
    for flight in graph.subjects(RDF.type, ATM.Flight):
        call_sign = graph.value(flight, ATM.callSign)
        for route in graph.objects(flight, ATM.hasActualRoute):
            for track_point in graph.objects(route, GEN.hasSequencedItem):
                reporting_time = graph.value(track_point, ATM.reportingTime)
                if reporting_time is None:
                    continue
                parsed_time = reporting_time.toPython()
                if not isinstance(parsed_time, datetime):
                    continue
                for fix in graph.objects(track_point, ATM.aircraftFix):
                    for sector in graph.objects(fix, ATM.locatedInSector):
                        passages.append(
                            SectorPassage(
                                flight_id=str(flight),
                                call_sign=str(call_sign or ""),
                                track_point_id=str(track_point),
                                fix_id=str(fix),
                                sector_id=str(sector),
                                reporting_time=parsed_time,
                            )
                        )
    return sorted(
        passages,
        key=lambda item: (
            item.reporting_time,
            item.flight_id,
            item.track_point_id,
            item.sector_id,
        ),
    )


def rank_busiest_sectors(
    passages: list[SectorPassage],
    *,
    hour: int,
) -> list[SectorRanking]:
    """Rank sectors by distinct flights, retaining raw track-point counts."""

    if not 0 <= hour <= 23:
        raise ValueError("hour must be between 0 and 23")

    grouped: dict[str, list[SectorPassage]] = defaultdict(list)
    for passage in passages:
        if passage.reporting_time.hour == hour:
            grouped[passage.sector_id].append(passage)

    rankings = [
        SectorRanking(
            sector_id=sector_id,
            hour=hour,
            unique_flight_count=len({passage.flight_id for passage in sector_passages}),
            track_point_count=len(sector_passages),
            source_dates=tuple(
                sorted({passage.reporting_time.date() for passage in sector_passages})
            ),
        )
        for sector_id, sector_passages in grouped.items()
    ]
    return sorted(
        rankings,
        key=lambda item: (
            -item.unique_flight_count,
            -item.track_point_count,
            item.sector_id,
        ),
    )


def find_close_flight_pairs(
    passages: list[SectorPassage],
    *,
    sector_id: str,
    max_minutes: int = 30,
) -> list[FlightPair]:
    """Find distinct-flight pairs whose closest sector reports are within a window."""

    if max_minutes <= 0:
        raise ValueError("max_minutes must be positive")

    by_date_and_flight: dict[tuple[date, str], list[SectorPassage]] = defaultdict(list)
    for passage in passages:
        if passage.sector_id == sector_id:
            by_date_and_flight[(passage.reporting_time.date(), passage.flight_id)].append(
                passage
            )

    pairs: list[FlightPair] = []
    dates = sorted({passage_date for passage_date, _ in by_date_and_flight})
    for passage_date in dates:
        flight_ids = sorted(
            flight_id
            for candidate_date, flight_id in by_date_and_flight
            if candidate_date == passage_date
        )
        for first_flight_id, second_flight_id in combinations(flight_ids, 2):
            candidates = product(
                by_date_and_flight[(passage_date, first_flight_id)],
                by_date_and_flight[(passage_date, second_flight_id)],
            )
            first, second = min(
                candidates,
                key=lambda item: (
                    abs((item[1].reporting_time - item[0].reporting_time).total_seconds()),
                    item[0].reporting_time,
                    item[1].reporting_time,
                ),
            )
            seconds_apart = abs((second.reporting_time - first.reporting_time).total_seconds())
            if seconds_apart >= max_minutes * 60:
                continue
            pairs.append(
                FlightPair(
                    sector_id=sector_id,
                    passage_date=passage_date,
                    first_flight_id=first.flight_id,
                    first_call_sign=first.call_sign,
                    first_reporting_time=first.reporting_time,
                    second_flight_id=second.flight_id,
                    second_call_sign=second.call_sign,
                    second_reporting_time=second.reporting_time,
                    minutes_apart=int(seconds_apart // 60),
                )
            )
    return pairs


def _normalize_tail_number(value: str) -> str:
    normalized = re.sub(r"[^A-Z0-9]", "", value.upper())
    if normalized and not normalized.startswith("N"):
        return f"N{normalized}"
    return normalized


def _is_a319_model(value: str) -> bool:
    return re.sub(r"[^A-Z0-9]", "", value.upper()).startswith("A319")


def find_delta_a319_departures(
    flights: list[FlightDeparture],
    *,
    aircraft_by_tail: dict[str, AircraftTechnicalRecord],
    ztl_airports: set[str],
    require_actual_departure: bool = True,
) -> list[AircraftMatchedDeparture]:
    """Return DL-reporting A319 departures from airports assigned to ZTL."""

    normalized_aircraft = {
        _normalize_tail_number(tail_number): record
        for tail_number, record in aircraft_by_tail.items()
    }
    normalized_ztl = {airport.upper() for airport in ztl_airports}
    matches: list[AircraftMatchedDeparture] = []
    for flight in flights:
        record = normalized_aircraft.get(_normalize_tail_number(flight.tail_number))
        if (
            flight.reporting_carrier.upper() != "DL"
            or flight.origin.upper() not in normalized_ztl
            or (require_actual_departure and flight.wheels_off is None)
            or record is None
            or not _is_a319_model(record.model)
        ):
            continue
        matches.append(
            AircraftMatchedDeparture(
                flight_id=flight.flight_id,
                flight_date=flight.flight_date,
                reporting_carrier=flight.reporting_carrier,
                carrier_role="reporting_carrier",
                flight_number=flight.flight_number,
                tail_number=_normalize_tail_number(flight.tail_number),
                origin=flight.origin,
                destination=flight.destination,
                aircraft_manufacturer=record.manufacturer,
                aircraft_model=record.model,
            )
        )
    return sorted(matches, key=lambda item: (item.flight_date, item.flight_id))


def _station_matches_airport(station: str, airport: str) -> bool:
    normalized_station = station.upper()
    normalized_airport = airport.upper()
    return normalized_station in {normalized_airport, f"K{normalized_airport}"}


def _reports_rain(observation: WeatherObservation) -> bool:
    return any("RA" in code.upper() for code in observation.weather_codes)


def find_rain_associated_departures(
    flights: list[FlightDeparture],
    *,
    observations: list[WeatherObservation],
    airport: str,
    max_minutes: int = 30,
) -> list[RainAssociatedDeparture]:
    """Join departures to nearby rain observations without asserting causality."""

    if max_minutes <= 0:
        raise ValueError("max_minutes must be positive")

    rain_observations = [
        observation
        for observation in observations
        if _station_matches_airport(observation.station, airport)
        and _reports_rain(observation)
    ]
    matches: list[RainAssociatedDeparture] = []
    for flight in flights:
        if (
            flight.origin.upper() != airport.upper()
            or flight.wheels_off is None
            or flight.wheels_off_time_basis != "UTC"
        ):
            continue
        candidates = [
            (
                abs((observation.observed_at - flight.wheels_off).total_seconds()),
                observation,
            )
            for observation in rain_observations
        ]
        candidates = [
            candidate for candidate in candidates if candidate[0] < max_minutes * 60
        ]
        if not candidates:
            continue
        seconds_apart, observation = min(
            candidates,
            key=lambda item: (item[0], item[1].observed_at),
        )
        matches.append(
            RainAssociatedDeparture(
                flight_id=flight.flight_id,
                flight_date=flight.flight_date,
                origin=flight.origin,
                wheels_off=flight.wheels_off,
                station=observation.station,
                observed_at=observation.observed_at,
                weather_codes=observation.weather_codes,
                minutes_apart=round(seconds_apart / 60, 3),
                association_role="temporal_weather_context",
                causal_claim=False,
                weather_raw_text=observation.raw_text,
                reporting_carrier=flight.reporting_carrier,
                flight_number=flight.flight_number,
            )
        )
    return sorted(matches, key=lambda item: (item.wheels_off, item.flight_id))


def _find_zip_member(archive: zipfile.ZipFile, basename: str) -> str:
    matches = [
        name
        for name in archive.namelist()
        if not name.endswith("/") and name.rsplit("/", 1)[-1] == basename
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {basename} member")
    return matches[0]


def load_nasr_artcc_airports(path: str | Path, *, artcc: str) -> set[str]:
    """Load FAA airport codes assigned to an ARTCC in a pinned NASR archive."""

    target = artcc.upper()
    airport_codes: set[str] = set()
    with zipfile.ZipFile(Path(path)) as archive:
        member = _find_zip_member(archive, "APT.txt")
        with archive.open(member) as raw_stream:
            stream = io.TextIOWrapper(raw_stream, encoding="latin-1", newline="")
            for line in stream:
                entity = parse_nasr_apt_line(line)
                if entity is None:
                    continue
                metadata = entity.metadata
                if target not in {
                    str(metadata.get("boundary_artcc") or "").upper(),
                    str(metadata.get("responsible_artcc") or "").upper(),
                }:
                    continue
                faa_code = next(
                    (code.value for code in entity.codes if code.scheme.upper() == "FAA"),
                    None,
                )
                if faa_code:
                    airport_codes.add(faa_code.upper())
    return airport_codes


def _single_csv_member(archive: zipfile.ZipFile) -> str:
    candidates = [
        name
        for name in archive.namelist()
        if not name.endswith("/") and name.lower().endswith(".csv")
    ]
    if len(candidates) != 1:
        raise ValueError("expected exactly one CSV member")
    return candidates[0]


def _parse_wheels_off(
    *,
    flight_date: date,
    raw_value: str,
    timezone_name: str | None,
) -> tuple[datetime | None, str]:
    text = raw_value.strip()
    if not text:
        return None, "not_reported"
    try:
        hhmm = int(float(text))
    except ValueError:
        return None, "not_reported"
    day_offset = 1 if hhmm == 2400 else 0
    if hhmm == 2400:
        hhmm = 0
    hour, minute = divmod(hhmm, 100)
    if hour > 23 or minute > 59:
        return None, "not_reported"
    local_value = datetime.combine(flight_date, datetime.min.time()).replace(
        hour=hour,
        minute=minute,
    ) + timedelta(days=day_offset)
    if timezone_name is None:
        return local_value, "origin_local"
    utc_value = (
        local_value.replace(tzinfo=ZoneInfo(timezone_name))
        .astimezone(UTC)
        .replace(tzinfo=None)
    )
    return utc_value, "UTC"


def load_bts_departures(
    path: str | Path,
    *,
    start_date: date,
    end_date: date,
    origins: set[str],
    origin_timezones: Mapping[str, str],
) -> list[FlightDeparture]:
    """Load a bounded flight subset from an official BTS monthly archive."""

    if end_date <= start_date:
        raise ValueError("end_date must be later than start_date")
    normalized_origins = {origin.upper() for origin in origins}
    normalized_timezones = {
        origin.upper(): timezone_name
        for origin, timezone_name in origin_timezones.items()
    }
    flights: list[FlightDeparture] = []
    with zipfile.ZipFile(Path(path)) as archive:
        member = _single_csv_member(archive)
        with archive.open(member) as raw_stream:
            stream = io.TextIOWrapper(raw_stream, encoding="utf-8-sig", newline="")
            for row_number, row in enumerate(csv.DictReader(stream), start=2):
                try:
                    flight_date = date.fromisoformat(str(row["FlightDate"]).strip())
                except (KeyError, TypeError, ValueError):
                    continue
                origin = str(row.get("Origin") or "").strip().upper()
                if (
                    not start_date <= flight_date < end_date
                    or origin not in normalized_origins
                ):
                    continue
                wheels_off, time_basis = _parse_wheels_off(
                    flight_date=flight_date,
                    raw_value=str(row.get("WheelsOff") or ""),
                    timezone_name=normalized_timezones.get(origin),
                )
                carrier = str(
                    row.get("IATA_CODE_Reporting_Airline")
                    or row.get("Reporting_Airline")
                    or ""
                ).strip()
                flight_number = str(
                    row.get("Flight_Number_Reporting_Airline") or ""
                ).strip()
                tail_number = str(row.get("Tail_Number") or "").strip()
                destination = str(row.get("Dest") or "").strip().upper()
                flights.append(
                    FlightDeparture(
                        flight_id=(
                            f"bts:{flight_date.isoformat()}:{carrier}:{flight_number}:"
                            f"{origin}:{destination}:{row_number}"
                        ),
                        flight_date=flight_date,
                        reporting_carrier=carrier,
                        flight_number=flight_number,
                        tail_number=tail_number,
                        origin=origin,
                        destination=destination,
                        wheels_off=wheels_off,
                        wheels_off_time_basis=time_basis,
                    )
                )
    return flights


def load_aircraft_technical_records(
    path: str | Path,
    *,
    tail_numbers: set[str],
) -> dict[str, AircraftTechnicalRecord]:
    """Join FAA MASTER and ACFTREF using technical columns only."""

    targets = {_normalize_tail_number(value) for value in tail_numbers if value}
    tail_to_model_code: dict[str, str] = {}
    with zipfile.ZipFile(Path(path)) as archive:
        master_member = _find_zip_member(archive, "MASTER.txt")
        with archive.open(master_member) as raw_stream:
            stream = io.TextIOWrapper(raw_stream, encoding="utf-8-sig", newline="")
            reader = csv.reader(stream)
            header = [column.strip() for column in next(reader)]
            tail_index = header.index("N-NUMBER")
            model_code_index = header.index("MFR MDL CODE")
            for row in reader:
                if len(row) <= max(tail_index, model_code_index):
                    continue
                tail_number = _normalize_tail_number(row[tail_index])
                if tail_number in targets:
                    tail_to_model_code[tail_number] = row[model_code_index].strip()

        required_codes = set(tail_to_model_code.values())
        code_to_technical: dict[str, tuple[str, str]] = {}
        reference_member = _find_zip_member(archive, "ACFTREF.txt")
        with archive.open(reference_member) as raw_stream:
            stream = io.TextIOWrapper(raw_stream, encoding="utf-8-sig", newline="")
            reader = csv.reader(stream)
            header = [column.strip() for column in next(reader)]
            code_index = header.index("CODE")
            manufacturer_index = header.index("MFR")
            model_index = header.index("MODEL")
            for row in reader:
                if len(row) <= max(code_index, manufacturer_index, model_index):
                    continue
                model_code = row[code_index].strip()
                if model_code in required_codes:
                    code_to_technical[model_code] = (
                        row[manufacturer_index].strip(),
                        row[model_index].strip(),
                    )

    records: dict[str, AircraftTechnicalRecord] = {}
    for tail_number, model_code in tail_to_model_code.items():
        technical = code_to_technical.get(model_code)
        if technical is None:
            continue
        manufacturer, model = technical
        records[tail_number] = AircraftTechnicalRecord(
            tail_number=tail_number,
            manufacturer=manufacturer,
            model=model,
        )
    return records


def load_iem_asos_observations(
    path: str | Path,
    *,
    start: datetime,
    end: datetime,
) -> list[WeatherObservation]:
    """Load a bounded UTC observation window from an IEM ASOS CSV export."""

    if end <= start:
        raise ValueError("end must be later than start")
    observations: list[WeatherObservation] = []
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            try:
                observed_at = datetime.fromisoformat(str(row["valid"]).strip())
            except (KeyError, TypeError, ValueError):
                continue
            if not start <= observed_at < end:
                continue
            station = str(row.get("station") or "").strip().upper()
            if len(station) == 3:
                station = f"K{station}"
            raw_codes = str(row.get("wxcodes") or "").strip()
            weather_codes = (
                ()
                if raw_codes.lower() in {"", "null", "none", "nan"}
                else tuple(raw_codes.split())
            )
            observations.append(
                WeatherObservation(
                    station=station,
                    observed_at=observed_at,
                    weather_codes=weather_codes,
                    raw_text=str(row.get("metar") or "").strip(),
                )
            )
    return sorted(observations, key=lambda item: (item.observed_at, item.station))


def load_nasa_sector_passages(path: str | Path) -> list[SectorPassage]:
    """Load the flight and fix slices needed for S4/S1S from atmontoPlus."""

    graph = Graph()
    with zipfile.ZipFile(Path(path)) as archive:
        for basename in ("flightInst.ttl", "fixInst.ttl"):
            member = _find_zip_member(archive, basename)
            graph.parse(
                data=archive.read(member).decode("utf-8"),
                format="turtle",
            )
    return extract_sector_passages(graph)


def _f1_record(record: AircraftMatchedDeparture) -> dict[str, object]:
    return {
        "flight_id": record.flight_id,
        "flight_date": record.flight_date.isoformat(),
        "reporting_carrier": record.reporting_carrier,
        "carrier_role": record.carrier_role,
        "flight_number": record.flight_number,
        "origin": record.origin,
        "destination": record.destination,
        "aircraft_manufacturer": record.aircraft_manufacturer,
        "aircraft_model": record.aircraft_model,
    }


def _f3_record(record: RainAssociatedDeparture) -> dict[str, object]:
    return {
        "flight_id": record.flight_id,
        "flight_date": record.flight_date.isoformat(),
        "origin": record.origin,
        "reporting_carrier": record.reporting_carrier,
        "flight_number": record.flight_number,
        "wheels_off_utc": record.wheels_off.isoformat(),
        "station": record.station,
        "observed_at_utc": record.observed_at.isoformat(),
        "weather_codes": list(record.weather_codes),
        "weather_raw_text": record.weather_raw_text,
        "minutes_apart": record.minutes_apart,
        "association_role": record.association_role,
        "causal_claim": record.causal_claim,
    }


def _ranking_record(record: SectorRanking) -> dict[str, object]:
    return {
        "sector_id": record.sector_id,
        "sector_name": record.sector_id.rsplit("#", 1)[-1],
        "hour_utc": record.hour,
        "distinct_flight_count": record.unique_flight_count,
        "appendix_binding_count": record.track_point_count,
        "source_dates": [value.isoformat() for value in record.source_dates],
    }


def _pair_record(record: FlightPair) -> dict[str, object]:
    return {
        "sector_id": record.sector_id,
        "passage_date": record.passage_date.isoformat(),
        "first_flight_id": record.first_flight_id,
        "first_call_sign": record.first_call_sign,
        "first_reporting_time": record.first_reporting_time.isoformat(),
        "second_flight_id": record.second_flight_id,
        "second_call_sign": record.second_call_sign,
        "second_reporting_time": record.second_reporting_time.isoformat(),
        "minutes_apart": record.minutes_apart,
    }


def compile_competency_query_report(
    *,
    sources: list[dict[str, object]],
    ztl_airport_count: int,
    f1_scheduled: list[AircraftMatchedDeparture],
    f1_actual: list[AircraftMatchedDeparture],
    f3_matches: list[RainAssociatedDeparture],
    sector_rankings: list[SectorRanking],
    close_pairs: list[FlightPair],
    sector_id: str,
) -> dict[str, object]:
    """Compile explicit query results without blending the two data eras."""

    sample_limit = 20
    ranking_rows = [_ranking_record(record) for record in sector_rankings[:sample_limit]]
    f1_origin_counts = dict(
        sorted(Counter(record.origin for record in f1_actual).items())
    )
    f3_carrier_counts = dict(
        sorted(Counter(record.reporting_carrier for record in f3_matches).items())
    )
    f3_observation_counts = dict(
        sorted(
            Counter(record.observed_at.isoformat() for record in f3_matches).items()
        )
    )
    return {
        "schema_version": "atmonto-competency-query-supplement-v1",
        "authoritative_store_integration": False,
        "query_agent_integration": False,
        "purpose": (
            "Deterministic flight/weather/sector competency-query supplement; "
            "not ingested into the authoritative evidence store."
        ),
        "sources": sorted(sources, key=lambda row: str(row.get("source_id", ""))),
        "query_results": {
            "F1": {
                "question": "Delta A319 departures from ZTL-region airports",
                "original_query_status": "not_executed_original_2012_data_unavailable",
                "execution_variant": "F1_modern_proxy",
                "scope": "BTS May 2026 + FAA NASR and aircraft-registry snapshots",
                "ztl_assignment_basis": "NASR boundary_or_responsible_artcc",
                "ztl_airport_count": ztl_airport_count,
                "carrier_semantics": "BTS reporting carrier DL",
                "scheduled_record_count": len(f1_scheduled),
                "actual_wheels_off_count": len(f1_actual),
                "actual_origin_counts": f1_origin_counts,
                "record_count": len(f1_actual),
                "record_sample_limit": sample_limit,
                "records_truncated": len(f1_actual) > sample_limit,
                "records": [
                    _f1_record(record) for record in f1_actual[:sample_limit]
                ],
                "limitations": [
                    "This is not the original 2012 LOA/TRACON-based F1 query.",
                    "Aircraft model is a later FAA technical-registry snapshot association.",
                ],
            },
            "F3S": {
                "question": "KATL departures temporally associated with reported rain",
                "original_query_status": "not_executed_original_2012_data_unavailable",
                "execution_variant": "F3S_modern_proxy",
                "join_rule": "absolute UTC difference < 30 minutes",
                "weather_rule": "explicit RA token in METAR weather codes",
                "weather_product_scope": "routine_and_special_METAR_reports",
                "causal_claim": False,
                "reporting_carrier_counts": f3_carrier_counts,
                "matched_observation_counts": f3_observation_counts,
                "record_count": len(f3_matches),
                "record_sample_limit": sample_limit,
                "records_truncated": len(f3_matches) > sample_limit,
                "records": [
                    _f3_record(record) for record in f3_matches[:sample_limit]
                ],
                "limitations": [
                    "The temporal association does not assert weather causality.",
                    "BTS is limited to reporting-carrier on-time performance records.",
                ],
            },
            "S4": {
                "question": "Sector with the most sampled flights during UTC hour 02",
                "original_query_status": "executed_on_2014_atmonto_plus_sample",
                "execution_variant": "S4_published_sample",
                "counting_note": (
                    "The appendix COUNT(?flight) is a track-point binding count; "
                    "distinct_flight_count implements the English question."
                ),
                "top_sector": ranking_rows[0] if ranking_rows else None,
                "ranking_count": len(sector_rankings),
                "ranking_sample_limit": sample_limit,
                "ranking_truncated": len(sector_rankings) > sample_limit,
                "ranking": ranking_rows,
            },
            "S1S": {
                "question": "Flight pairs traversing the same sector within 30 minutes",
                "original_query_status": "executed_on_2014_atmonto_plus_sample",
                "execution_variant": "S1S_published_sample",
                "sector_id": sector_id,
                "join_rule": "same date and closest absolute difference < 30 minutes",
                "pair_count": len(close_pairs),
                "pairs": [_pair_record(record) for record in close_pairs],
            },
        },
    }


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_source_artifacts(
    sources: Mapping[str, Mapping[str, object]],
) -> list[dict[str, object]]:
    """Verify pinned local source files and return report-safe metadata."""

    verified: list[dict[str, object]] = []
    for source_id, config in sorted(sources.items()):
        configured_path = str(config["path"])
        path = resolve_project_path(configured_path)
        if not path.is_file():
            raise ValueError(f"source artifact missing: {source_id}")
        actual_sha256 = _sha256_path(path)
        expected_sha256 = str(config["sha256"])
        if actual_sha256 != expected_sha256:
            raise ValueError(f"source artifact checksum mismatch: {source_id}")
        row: dict[str, object] = {
            "source_id": source_id,
            "path": configured_path,
            "url": str(config["url"]),
            "sha256": actual_sha256,
            "byte_count": path.stat().st_size,
            "role": str(config["role"]),
            "temporal_scope": str(config["temporal_scope"]),
        }
        if config.get("license_url"):
            row["license_url"] = str(config["license_url"])
        if config.get("retrieved_on"):
            row["retrieved_on"] = str(config["retrieved_on"])
        verified.append(row)
    return verified


def build_competency_query_report(config_path: str | Path) -> dict[str, object]:
    """Execute all four bounded query variants from checksum-pinned sources."""

    config = load_yaml(resolve_project_path(config_path))
    sources_config = config.get("sources")
    queries = config.get("queries")
    if not isinstance(sources_config, Mapping) or not isinstance(queries, Mapping):
        raise ValueError("competency config requires sources and queries mappings")
    sources = verify_source_artifacts(sources_config)
    paths = {
        source_id: resolve_project_path(str(source_config["path"]))
        for source_id, source_config in sources_config.items()
    }

    f1_config = queries["F1"]
    f3_config = queries["F3S"]
    s4_config = queries["S4"]
    s1s_config = queries["S1S"]
    artcc = str(f1_config["artcc"])
    ztl_airports = load_nasr_artcc_airports(
        paths["faa_nasr_2026_05_14"],
        artcc=artcc,
    )
    flights = load_bts_departures(
        paths["bts_on_time_2026_05"],
        start_date=date.fromisoformat(str(f1_config["start_date"])),
        end_date=date.fromisoformat(str(f1_config["end_date"])),
        origins=ztl_airports,
        origin_timezones={
            str(f3_config["airport"]): str(f3_config["airport_timezone"])
        },
    )
    aircraft = load_aircraft_technical_records(
        paths["faa_aircraft_registry_2026_07_28"],
        tail_numbers={flight.tail_number for flight in flights if flight.tail_number},
    )
    f1_scheduled = find_delta_a319_departures(
        flights,
        aircraft_by_tail=aircraft,
        ztl_airports=ztl_airports,
        require_actual_departure=False,
    )
    f1_actual = find_delta_a319_departures(
        flights,
        aircraft_by_tail=aircraft,
        ztl_airports=ztl_airports,
        require_actual_departure=True,
    )

    weather_start = datetime.fromisoformat(str(f3_config["start"]))
    weather_end = datetime.fromisoformat(str(f3_config["end"]))
    observations = load_iem_asos_observations(
        paths["iem_katl_metar_2026_05_14_22"],
        start=weather_start,
        end=weather_end,
    )
    f3_matches = find_rain_associated_departures(
        flights,
        observations=observations,
        airport=str(f3_config["airport"]),
        max_minutes=int(f3_config["max_minutes"]),
    )

    passages = load_nasa_sector_passages(paths["nasa_atmonto_plus"])
    sector_rankings = rank_busiest_sectors(
        passages,
        hour=int(s4_config["hour_utc"]),
    )
    target_sector = str(s1s_config["sector_id"])
    close_pairs = find_close_flight_pairs(
        passages,
        sector_id=target_sector,
        max_minutes=int(s1s_config["max_minutes"]),
    )
    return compile_competency_query_report(
        sources=sources,
        ztl_airport_count=len(ztl_airports),
        f1_scheduled=f1_scheduled,
        f1_actual=f1_actual,
        f3_matches=f3_matches,
        sector_rankings=sector_rankings,
        close_pairs=close_pairs,
        sector_id=target_sector,
    )


def render_competency_query_markdown(report: Mapping[str, object]) -> str:
    """Render a compact reader-facing summary from the JSON report."""

    results = report["query_results"]
    if not isinstance(results, Mapping):
        raise ValueError("report query_results must be a mapping")
    f1 = results["F1"]
    f3 = results["F3S"]
    s4 = results["S4"]
    s1s = results["S1S"]
    if not all(isinstance(item, Mapping) for item in (f1, f3, s4, s1s)):
        raise ValueError("query result rows must be mappings")
    top_sector = s4.get("top_sector")
    if not isinstance(top_sector, Mapping):
        raise ValueError("S4 requires a top sector")
    sources = report.get("sources")
    if not isinstance(sources, list):
        raise ValueError("report sources must be a list")

    lines = [
        "# ATMONTO Competency-Query Data Supplement",
        "",
        "This deterministic sidecar fills flight, aircraft-type, weather, and "
        "sector-trajectory data gaps without entering the authoritative evidence "
        "store or public Query Agent runtime.",
        "",
        "## Results",
        "",
        "| Query | Executed form | Result |",
        "|---|---|---:|",
        (
            f"| F1 | Modern May 2026 proxy | "
            f"{f1['actual_wheels_off_count']} actual departures "
            f"({f1['scheduled_record_count']} BTS records) |"
        ),
        f"| F3S | Modern KATL temporal association | {f3['record_count']} flights |",
        (
            f"| S4 | NASA 2014 sample, hour 02 UTC | "
            f"{top_sector['sector_name']}: {top_sector['distinct_flight_count']} flights "
            f"/ {top_sector['appendix_binding_count']} track-point bindings |"
        ),
        f"| S1S | NASA 2014 sample, ZTLsector040 | {s1s['pair_count']} pairs |",
        "",
        "## Interpretation boundaries",
        "",
        "- F1 and F3S are modern proxy executions because the original 2012 KATL dataset "
        "is not publicly available in the recovered bundle.",
        "- F3S is a symmetric time association around explicit rain observations; it is "
        "not a causal claim.",
        "- S4 reports both distinct flights and the appendix's track-point binding count.",
        "- NASA 2014 flight-track data remains a local, checksum-bound source and is not "
        "redistributed by this repository.",
        "- FAA aircraft-registry processing retains only tail-to-manufacturer/model fields; "
        "owner and address fields are not materialized.",
        "",
        "## Pinned sources",
        "",
        "| Source | Role | SHA-256 |",
        "|---|---|---|",
    ]
    for source in sources:
        if not isinstance(source, Mapping):
            continue
        lines.append(
            f"| {source['source_id']} | {source['role']} | `{source['sha256']}` |"
        )
    return "\n".join(lines) + "\n"


def write_competency_query_report(
    report: Mapping[str, object],
    *,
    json_path: str | Path,
    markdown_path: str | Path,
) -> None:
    """Write deterministic JSON and Markdown report projections."""

    resolved_json_path = resolve_project_path(json_path)
    resolved_markdown_path = resolve_project_path(markdown_path)
    resolved_json_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_markdown_path.parent.mkdir(parents=True, exist_ok=True)
    resolved_json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    resolved_markdown_path.write_text(
        render_competency_query_markdown(report),
        encoding="utf-8",
    )


def run_competency_query_supplement(config_path: str | Path) -> dict[str, object]:
    """Build and write the configured competency-query supplement."""

    resolved_config_path = resolve_project_path(config_path)
    config = load_yaml(resolved_config_path)
    outputs = config.get("outputs")
    if not isinstance(outputs, Mapping):
        raise ValueError("competency config requires an outputs mapping")
    report = build_competency_query_report(resolved_config_path)
    write_competency_query_report(
        report,
        json_path=str(outputs["json"]),
        markdown_path=str(outputs["markdown"]),
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the checksum-bound ATMONTO competency-query supplement."
    )
    parser.add_argument(
        "--config",
        default="configs/flight_competency_v1.yaml",
        help="Path to the supplement YAML configuration.",
    )
    args = parser.parse_args(argv)
    report = run_competency_query_supplement(args.config)
    query_results = report["query_results"]
    assert isinstance(query_results, Mapping)
    summary = {
        "F1": query_results["F1"]["record_count"],
        "F3S": query_results["F3S"]["record_count"],
        "S4": query_results["S4"]["top_sector"],
        "S1S": query_results["S1S"]["pair_count"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
