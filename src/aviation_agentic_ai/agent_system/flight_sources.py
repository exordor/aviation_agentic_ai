"""Deterministic source adapters for flight and historical weather records.

The adapters in this module preserve record-level source identity while
returning small typed records for later semantic conversion.  They do not
publish graph facts and they deliberately exclude FAA Registry owner fields.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import zipfile
from collections.abc import Iterator, Mapping, Set
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Literal, TextIO
from zoneinfo import ZoneInfo

from aviation_agentic_ai.agent_system.contracts import SourceFamily, SourceRecord


FLIGHT_SOURCE_ADAPTER_VERSION = "flight-source-adapters-v1"

TimeBasis = Literal["utc", "origin_local", "unknown"]
WeatherReportType = Literal["METAR", "SPECI"]


@dataclass(frozen=True)
class BTSFlightSourceRecord:
    """One BTS on-time row normalized without changing its source identity."""

    source: SourceRecord
    flight_date: date
    reporting_carrier: str
    flight_number: str
    tail_number: str | None
    origin: str
    destination: str
    scheduled_departure_key: str
    scheduled_departure: datetime | None
    actual_wheels_off: datetime | None
    time_basis: TimeBasis
    cancelled: bool
    diverted: bool


@dataclass(frozen=True)
class FAAAircraftTechnicalSourceRecord:
    """Technical-only FAA Registry join between MASTER and ACFTREF."""

    source: SourceRecord
    tail_number: str
    model_code: str
    manufacturer: str
    model: str
    registry_snapshot_at: datetime


@dataclass(frozen=True)
class IEMWeatherSourceRecord:
    """One UTC IEM METAR or SPECI observation row."""

    source: SourceRecord
    station_id: str
    observed_at: datetime
    report_type: WeatherReportType
    raw_report: str
    phenomenon_tokens: tuple[str, ...]


class _TrackedLines(Iterator[str]):
    """Track the exact decoded physical lines consumed by ``csv.reader``."""

    def __init__(self, stream: TextIO) -> None:
        self._stream = stream
        self._current: list[str] = []

    def __next__(self) -> str:
        line = next(self._stream)
        self._current.append(line)
        return line

    def take_record(self) -> str:
        value = "".join(self._current)
        self._current.clear()
        return value


def _iter_csv_rows_with_raw(stream: TextIO) -> Iterator[tuple[int, dict[str, str], str]]:
    tracked = _TrackedLines(stream)
    reader = csv.reader(tracked)
    try:
        header = [column.strip() for column in next(reader)]
    except StopIteration:
        return
    tracked.take_record()
    for row_number, values in enumerate(reader, start=2):
        raw_record = tracked.take_record()
        row = {
            column: values[index] if index < len(values) else ""
            for index, column in enumerate(header)
        }
        yield row_number, row, raw_record


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _row_sha256(raw_record: str) -> str:
    return hashlib.sha256(raw_record.encode("utf-8")).hexdigest()


def _canonical_json(value: dict[str, object]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _find_zip_member(archive: zipfile.ZipFile, basename: str) -> str:
    matches = [
        name
        for name in archive.namelist()
        if not name.endswith("/") and name.rsplit("/", 1)[-1] == basename
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {basename} member")
    return matches[0]


def _single_csv_member(archive: zipfile.ZipFile) -> str:
    members = [
        name
        for name in archive.namelist()
        if not name.endswith("/") and name.lower().endswith(".csv")
    ]
    if len(members) != 1:
        raise ValueError("expected exactly one CSV member")
    return members[0]


def _normalize_tail_number(value: str) -> str:
    normalized = re.sub(r"[^A-Z0-9]", "", value.strip().upper())
    if normalized and not normalized.startswith("N"):
        normalized = f"N{normalized}"
    return normalized


def _parse_flag(value: str) -> bool:
    try:
        return float(value.strip() or "0") != 0.0
    except ValueError:
        return False


def _parse_local_clock(
    *,
    service_date: date,
    raw_value: str,
    timezone_name: str | None,
) -> tuple[datetime | None, TimeBasis]:
    text = raw_value.strip()
    if not text:
        return None, "unknown"
    try:
        if ":" in text:
            hour_text, minute_text = text.split(":", 1)
            hour = int(hour_text)
            minute = int(minute_text)
            day_offset = 0
        else:
            hhmm = int(float(text))
            day_offset = 1 if hhmm == 2400 else 0
            if hhmm == 2400:
                hhmm = 0
            hour, minute = divmod(hhmm, 100)
    except ValueError:
        return None, "unknown"
    if hour > 23 or minute > 59 or hour < 0 or minute < 0:
        return None, "unknown"
    local_value = datetime.combine(service_date, datetime.min.time()).replace(
        hour=hour,
        minute=minute,
    ) + timedelta(days=day_offset)
    if timezone_name is None:
        return local_value, "origin_local"
    return (
        local_value.replace(tzinfo=ZoneInfo(timezone_name)).astimezone(UTC),
        "utc",
    )


def _combined_time_basis(
    scheduled_basis: TimeBasis,
    actual_basis: TimeBasis,
) -> TimeBasis:
    reported = {basis for basis in (scheduled_basis, actual_basis) if basis != "unknown"}
    if not reported:
        return "unknown"
    if reported == {"utc"}:
        return "utc"
    return "origin_local"


def iter_bts_flight_sources(
    path: str | Path,
    *,
    origin_timezones: Mapping[str, str],
    service_date_from: date | None = None,
    service_date_to: date | None = None,
    origin_airports: Set[str] | None = None,
    routes: Set[tuple[str, str]] | None = None,
    asset_id: str | None = None,
    asset_sha256: str | None = None,
    source_url: str | None = None,
) -> Iterator[BTSFlightSourceRecord]:
    """Stream normalized flight-operation records from one BTS monthly ZIP."""

    archive_path = Path(path)
    asset_checksum = asset_sha256 or _sha256_path(archive_path)
    timezones = {
        origin.strip().upper(): zone for origin, zone in origin_timezones.items()
    }
    allowed_origins = (
        None
        if origin_airports is None
        else {origin.strip().upper() for origin in origin_airports if origin.strip()}
    )
    allowed_routes = (
        None
        if routes is None
        else {
            (origin.strip().upper(), destination.strip().upper())
            for origin, destination in routes
        }
    )
    with zipfile.ZipFile(archive_path) as archive:
        member = _single_csv_member(archive)
        with archive.open(member) as raw_stream:
            stream = io.TextIOWrapper(raw_stream, encoding="utf-8-sig", newline="")
            for row_number, row, raw_record in _iter_csv_rows_with_raw(stream):
                try:
                    service_date = date.fromisoformat(row.get("FlightDate", "").strip())
                except ValueError:
                    continue
                if service_date_from is not None and service_date < service_date_from:
                    continue
                if service_date_to is not None and service_date > service_date_to:
                    continue
                origin = row.get("Origin", "").strip().upper()
                if allowed_origins is not None and origin not in allowed_origins:
                    continue
                destination = row.get("Dest", "").strip().upper()
                if (
                    allowed_routes is not None
                    and (origin, destination) not in allowed_routes
                ):
                    continue
                carrier = (
                    row.get("IATA_CODE_Reporting_Airline", "").strip()
                    or row.get("Reporting_Airline", "").strip()
                )
                flight_number = row.get("Flight_Number_Reporting_Airline", "").strip()
                raw_tail = row.get("Tail_Number", "")
                tail_number = _normalize_tail_number(raw_tail) or None
                timezone_name = timezones.get(origin)
                raw_scheduled = row.get("CRSDepTime", "")
                raw_actual = row.get("WheelsOff", "")
                scheduled, scheduled_basis = _parse_local_clock(
                    service_date=service_date,
                    raw_value=raw_scheduled,
                    timezone_name=timezone_name,
                )
                actual, actual_basis = _parse_local_clock(
                    service_date=service_date,
                    raw_value=raw_actual,
                    timezone_name=timezone_name,
                )
                time_basis = _combined_time_basis(scheduled_basis, actual_basis)
                row_checksum = _row_sha256(raw_record)
                scheduled_key = (
                    f"{service_date.isoformat()}|{raw_scheduled.strip()}"
                    if raw_scheduled.strip()
                    else f"row:{row_number}:{row_checksum}"
                )
                cancelled = _parse_flag(row.get("Cancelled", ""))
                diverted = _parse_flag(row.get("Diverted", ""))
                content = {
                    "actual_wheels_off": actual.isoformat() if actual else None,
                    "cancelled": cancelled,
                    "destination": destination,
                    "diverted": diverted,
                    "flight_date": service_date.isoformat(),
                    "flight_number": flight_number,
                    "origin": origin,
                    "reporting_carrier": carrier,
                    "scheduled_departure": scheduled.isoformat() if scheduled else None,
                    "tail_number": tail_number,
                    "time_basis": time_basis,
                }
                source = SourceRecord(
                    source_id=(
                        f"bts-row:{asset_checksum}:{member}:{row_number}:{row_checksum}"
                    ),
                    family=SourceFamily.BTS_FLIGHT_OPERATION,
                    content=_canonical_json(content),
                    title=f"BTS flight {carrier}{flight_number} {service_date.isoformat()}",
                    effective_date=scheduled or actual,
                    source_url=source_url,
                    asset_id=asset_id,
                    logical_time=(scheduled or actual).isoformat()
                    if scheduled or actual
                    else service_date.isoformat(),
                    metadata={
                        "asset_sha256": asset_checksum,
                        "member": member,
                        "parser_version": FLIGHT_SOURCE_ADAPTER_VERSION,
                        "raw_crs_departure": raw_scheduled.strip(),
                        "raw_row_sha256": row_checksum,
                        "raw_wheels_off": raw_actual.strip(),
                        "row_number": row_number,
                        "scheduled_departure_key": scheduled_key,
                        "time_basis": time_basis,
                    },
                )
                yield BTSFlightSourceRecord(
                    source=source,
                    flight_date=service_date,
                    reporting_carrier=carrier,
                    flight_number=flight_number,
                    tail_number=tail_number,
                    origin=origin,
                    destination=destination,
                    scheduled_departure_key=scheduled_key,
                    scheduled_departure=scheduled,
                    actual_wheels_off=actual,
                    time_basis=time_basis,
                    cancelled=cancelled,
                    diverted=diverted,
                )


def iter_faa_registry_technical_sources(
    path: str | Path,
    *,
    registry_snapshot_at: datetime,
    tail_numbers: Set[str] | None = None,
    asset_id: str | None = None,
    asset_sha256: str | None = None,
    source_url: str | None = None,
) -> Iterator[FAAAircraftTechnicalSourceRecord]:
    """Stream technical aircraft records joined without owner/address columns."""

    archive_path = Path(path)
    asset_checksum = asset_sha256 or _sha256_path(archive_path)
    snapshot = (
        registry_snapshot_at.replace(tzinfo=UTC)
        if registry_snapshot_at.tzinfo is None
        else registry_snapshot_at.astimezone(UTC)
    )
    targets = (
        {_normalize_tail_number(value) for value in tail_numbers if value}
        if tail_numbers is not None
        else None
    )
    with zipfile.ZipFile(archive_path) as archive:
        reference_member = _find_zip_member(archive, "ACFTREF.txt")
        technical_by_code: dict[str, tuple[str, str, int, str]] = {}
        with archive.open(reference_member) as raw_stream:
            stream = io.TextIOWrapper(raw_stream, encoding="utf-8-sig", newline="")
            for row_number, row, raw_record in _iter_csv_rows_with_raw(stream):
                code = row.get("CODE", "").strip()
                if not code:
                    continue
                technical_by_code[code] = (
                    row.get("MFR", "").strip(),
                    row.get("MODEL", "").strip(),
                    row_number,
                    _row_sha256(raw_record),
                )

        master_member = _find_zip_member(archive, "MASTER.txt")
        with archive.open(master_member) as raw_stream:
            stream = io.TextIOWrapper(raw_stream, encoding="utf-8-sig", newline="")
            for row_number, row, raw_record in _iter_csv_rows_with_raw(stream):
                tail_number = _normalize_tail_number(row.get("N-NUMBER", ""))
                if not tail_number or (targets is not None and tail_number not in targets):
                    continue
                model_code = row.get("MFR MDL CODE", "").strip()
                technical = technical_by_code.get(model_code)
                if technical is None:
                    continue
                manufacturer, model, reference_row_number, reference_row_checksum = (
                    technical
                )
                master_row_checksum = _row_sha256(raw_record)
                content = {
                    "manufacturer": manufacturer,
                    "model": model,
                    "model_code": model_code,
                    "registry_snapshot_at": snapshot.isoformat(),
                    "tail_number": tail_number,
                }
                source = SourceRecord(
                    source_id=(
                        f"faa-registry-technical:{asset_checksum}:{tail_number}:"
                        f"{master_row_checksum}:{reference_row_checksum}"
                    ),
                    family=SourceFamily.FAA_AIRCRAFT_REGISTRY,
                    content=_canonical_json(content),
                    title=f"FAA aircraft technical record {tail_number}",
                    effective_date=snapshot,
                    source_url=source_url,
                    asset_id=asset_id,
                    logical_time=snapshot.isoformat(),
                    metadata={
                        "asset_sha256": asset_checksum,
                        "master_member": master_member,
                        "master_raw_row_sha256": master_row_checksum,
                        "master_row_number": row_number,
                        "parser_version": FLIGHT_SOURCE_ADAPTER_VERSION,
                        "reference_member": reference_member,
                        "reference_raw_row_sha256": reference_row_checksum,
                        "reference_row_number": reference_row_number,
                        "time_basis": "utc",
                    },
                )
                yield FAAAircraftTechnicalSourceRecord(
                    source=source,
                    tail_number=tail_number,
                    model_code=model_code,
                    manufacturer=manufacturer,
                    model=model,
                    registry_snapshot_at=snapshot,
                )


def _parse_iem_time(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def iter_iem_weather_sources(
    path: str | Path,
    *,
    asset_id: str | None = None,
    asset_sha256: str | None = None,
    source_url: str | None = None,
) -> Iterator[IEMWeatherSourceRecord]:
    """Stream UTC METAR/SPECI records from one IEM ASOS CSV export."""

    source_path = Path(path)
    asset_checksum = asset_sha256 or _sha256_path(source_path)
    with source_path.open(encoding="utf-8-sig", newline="") as stream:
        for row_number, row, raw_record in _iter_csv_rows_with_raw(stream):
            observed_at = _parse_iem_time(row.get("valid", ""))
            if observed_at is None:
                continue
            station = row.get("station", "").strip().upper()
            if len(station) == 3:
                station = f"K{station}"
            raw_report = row.get("metar", "").strip()
            explicit_type = row.get("report_type", "").strip().upper()
            report_type: WeatherReportType = (
                "SPECI"
                if explicit_type == "SPECI" or raw_report.upper().startswith("SPECI ")
                else "METAR"
            )
            raw_codes = row.get("wxcodes", "").strip()
            phenomenon_tokens = (
                ()
                if raw_codes.lower() in {"", "null", "none", "nan"}
                else tuple(raw_codes.split())
            )
            row_checksum = _row_sha256(raw_record)
            content = {
                "observed_at": observed_at.isoformat(),
                "phenomenon_tokens": list(phenomenon_tokens),
                "raw_report": raw_report,
                "report_type": report_type,
                "station_id": station,
            }
            source = SourceRecord(
                source_id=(
                    f"iem-weather-row:{asset_checksum}:{row_number}:{row_checksum}"
                ),
                family=SourceFamily.HISTORICAL_METAR_SPECI,
                content=_canonical_json(content),
                title=f"IEM {report_type} {station} {observed_at.isoformat()}",
                effective_date=observed_at,
                source_url=source_url,
                asset_id=asset_id,
                logical_time=observed_at.isoformat(),
                metadata={
                    "asset_sha256": asset_checksum,
                    "parser_version": FLIGHT_SOURCE_ADAPTER_VERSION,
                    "raw_row_sha256": row_checksum,
                    "row_number": row_number,
                    "time_basis": "utc",
                },
            )
            yield IEMWeatherSourceRecord(
                source=source,
                station_id=station,
                observed_at=observed_at,
                report_type=report_type,
                raw_report=raw_report,
                phenomenon_tokens=phenomenon_tokens,
            )
