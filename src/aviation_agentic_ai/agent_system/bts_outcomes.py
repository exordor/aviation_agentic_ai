"""Deterministic, audit-only BTS On-Time normalization and observations."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import statistics
import zipfile
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo

from aviation_agentic_ai.agent_system.contracts import (
    BTSManifestBinding,
    BTSOnTimeRow,
    BTSOutcomeBundle,
    BTSOutcomeSummary,
    DecisionContextEvent,
    ObservationDerivationSeed,
)
from aviation_agentic_ai.agent_system.validation_profiles import (
    AggregationProcedureDescriptor,
)
from aviation_agentic_ai.cross_source.contracts import CanonicalEntity, EntityType


ARCHIVE_URL = (
    "https://transtats.bts.gov/PREZIP/"
    "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2026_5.zip"
)
ARCHIVE_NAME = "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2026_5.zip"
ARCHIVE_SHA256 = "4e7b96999440afec8c92dd23bfbc68a5852e14d9a56c3d0d366f884542ea80b3"
MEMBER_NAME = "On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2026_5.csv"
MEMBER_SHA256 = "12470de43703fe0c23e25510b5af6e6e4e1d5d0aa55818dcc7d0f0b407801be8"
TIMEZONE_NAME = "America/New_York"
NORMALIZED_SOURCE_ID = "bts_on_time:2026-05:nyc"
NORMALIZED_SNAPSHOT_SHA256 = "434ef44bae82213607006b7a6888621245528fe5ca8a8a168be919329f84c20d"
REPORTING_SCOPE = "BTS On-Time reporting carriers and scheduled domestic passenger operations."
FILTER_DATES = {"2026-05-19", "2026-05-20"}
FILTER_DESTINATIONS = {"JFK", "EWR", "LGA"}

EXPECTED_FIELDS = (
    "Year", "Quarter", "Month", "DayofMonth", "DayOfWeek", "FlightDate", "Reporting_Airline",
    "DOT_ID_Reporting_Airline", "IATA_CODE_Reporting_Airline", "Tail_Number",
    "Flight_Number_Reporting_Airline", "OriginAirportID", "OriginAirportSeqID",
    "OriginCityMarketID", "Origin", "OriginCityName", "OriginState", "OriginStateFips",
    "OriginStateName", "OriginWac", "DestAirportID", "DestAirportSeqID", "DestCityMarketID",
    "Dest", "DestCityName", "DestState", "DestStateFips", "DestStateName", "DestWac",
    "CRSDepTime", "DepTime", "DepDelay", "DepDelayMinutes", "DepDel15",
    "DepartureDelayGroups", "DepTimeBlk", "TaxiOut", "WheelsOff", "WheelsOn", "TaxiIn",
    "CRSArrTime", "ArrTime", "ArrDelay", "ArrDelayMinutes", "ArrDel15", "ArrivalDelayGroups",
    "ArrTimeBlk", "Cancelled", "CancellationCode", "Diverted", "CRSElapsedTime",
    "ActualElapsedTime", "AirTime", "Flights", "Distance", "DistanceGroup", "CarrierDelay",
    "WeatherDelay", "NASDelay", "SecurityDelay", "LateAircraftDelay", "FirstDepTime",
    "TotalAddGTime", "LongestAddGTime", "DivAirportLandings", "DivReachedDest",
    "DivActualElapsedTime", "DivArrDelay", "DivDistance", "Div1Airport", "Div1AirportID",
    "Div1AirportSeqID", "Div1WheelsOn", "Div1TotalGTime", "Div1LongestGTime", "Div1WheelsOff",
    "Div1TailNum", "Div2Airport", "Div2AirportID", "Div2AirportSeqID", "Div2WheelsOn",
    "Div2TotalGTime", "Div2LongestGTime", "Div2WheelsOff", "Div2TailNum", "Div3Airport",
    "Div3AirportID", "Div3AirportSeqID", "Div3WheelsOn", "Div3TotalGTime", "Div3LongestGTime",
    "Div3WheelsOff", "Div3TailNum", "Div4Airport", "Div4AirportID", "Div4AirportSeqID",
    "Div4WheelsOn", "Div4TotalGTime", "Div4LongestGTime", "Div4WheelsOff", "Div4TailNum",
    "Div5Airport", "Div5AirportID", "Div5AirportSeqID", "Div5WheelsOn", "Div5TotalGTime",
    "Div5LongestGTime", "Div5WheelsOff", "Div5TailNum",
)
NORMALIZED_FIELDS = tuple(BTSOnTimeRow.model_fields)


class BTSNormalizationResult:
    """Result of archive normalization, retaining rows for deterministic use."""

    def __init__(
        self,
        status: str,
        *,
        output_path: Path | None = None,
        manifest_path: Path | None = None,
        rows: list[BTSOnTimeRow] | None = None,
        failure_reason: str = "",
    ) -> None:
        self.status = status
        self.output_path = output_path
        self.manifest_path = manifest_path
        self.rows = rows or []
        self.failure_reason = failure_reason


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_rows_bytes(rows: Iterable[BTSOnTimeRow]) -> bytes:
    """Return the canonical sorted normalized JSONL bytes for source binding."""

    return "".join(
        json.dumps(row.model_dump(mode="json"), sort_keys=True, separators=(",", ":")) + "\n"
        for row in sorted(rows, key=lambda row: row.row_id)
    ).encode("utf-8")


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _as_int(value: str | None, field: str, *, required: bool = True) -> int | None:
    if value in (None, ""):
        if required:
            raise ValueError(f"missing required BTS field: {field}")
        return None
    try:
        parsed_float = float(value)
        parsed = int(parsed_float)
    except ValueError as exc:
        raise ValueError(f"invalid integer BTS field: {field}") from exc
    if parsed_float != parsed:
        raise ValueError(f"non-integral BTS field: {field}")
    return parsed


def _as_float(value: str | None, field: str, *, required: bool = False) -> float | None:
    if value in (None, ""):
        if required:
            raise ValueError(f"missing required BTS field: {field}")
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"invalid numeric BTS field: {field}") from exc


def _hhmm_minutes(value: int, field: str) -> int:
    hours, minutes = divmod(value, 100)
    if hours == 24 and minutes == 0:
        return 24 * 60
    if not 0 <= hours <= 23 or not 0 <= minutes <= 59:
        raise ValueError(f"invalid HHMM BTS field: {field}")
    return hours * 60 + minutes


def infer_destination_arrival_utc(
    flight_date: str,
    crs_dep_time: int,
    crs_arr_time: int,
    crs_elapsed_time: float,
    *,
    timezone_name: str = TIMEZONE_NAME,
) -> datetime:
    """Infer scheduled destination arrival day from schedule consistency."""

    departure = _hhmm_minutes(crs_dep_time, "CRSDepTime")
    arrival = _hhmm_minutes(crs_arr_time, "CRSArrTime")
    candidates = [
        (abs(arrival + 1440 * day_offset - departure - crs_elapsed_time), day_offset)
        for day_offset in (-1, 0, 1, 2)
    ]
    residual = min(residual for residual, _ in candidates)
    offsets = [offset for candidate_residual, offset in candidates if candidate_residual == residual]
    if len(offsets) != 1:
        raise ValueError("ambiguous scheduled destination arrival day")
    if residual > 720:
        raise ValueError("scheduled destination arrival residual exceeds 720 minutes")
    try:
        local_day = date.fromisoformat(flight_date) + timedelta(days=offsets[0])
    except ValueError as exc:
        raise ValueError("invalid FlightDate") from exc
    arrival_day, arrival_minute = divmod(arrival, 1440)
    local_time = time(hour=arrival_minute // 60, minute=arrival_minute % 60)
    return datetime.combine(
        local_day + timedelta(days=arrival_day), local_time, tzinfo=ZoneInfo(timezone_name)
    ).astimezone(UTC)


def _normalize_row(raw: dict[str, str], archive_sha256: str) -> BTSOnTimeRow:
    values = {key: (value if value != "" else None) for key, value in raw.items()}
    required_text = ("FlightDate", "Reporting_Airline", "IATA_CODE_Reporting_Airline", "Origin", "Dest")
    if any(values[field] is None for field in required_text):
        raise ValueError("missing required BTS identity field")
    flight_date = str(values["FlightDate"])
    dep_time = _as_int(values["CRSDepTime"], "CRSDepTime")
    arr_time = _as_int(values["CRSArrTime"], "CRSArrTime")
    elapsed = _as_float(values["CRSElapsedTime"], "CRSElapsedTime", required=True)
    cancelled = _as_int(values["Cancelled"], "Cancelled")
    diverted = _as_int(values["Diverted"], "Diverted")
    if cancelled not in {0, 1} or diverted not in {0, 1}:
        raise ValueError("BTS cancellation/diversion flags must be 0 or 1")
    natural_key = (
        flight_date,
        str(_as_int(values["DOT_ID_Reporting_Airline"], "DOT_ID_Reporting_Airline")),
        str(_as_int(values["Flight_Number_Reporting_Airline"], "Flight_Number_Reporting_Airline")),
        str(_as_int(values["OriginAirportSeqID"], "OriginAirportSeqID")),
        str(_as_int(values["DestAirportSeqID"], "DestAirportSeqID")),
        str(dep_time),
    )
    row_id = "bts-row:" + hashlib.sha256("|".join((archive_sha256, *natural_key)).encode()).hexdigest()
    return BTSOnTimeRow(
        row_id=row_id,
        FlightDate=flight_date,
        DOT_ID_Reporting_Airline=int(natural_key[1]),
        Reporting_Airline=str(values["Reporting_Airline"]),
        IATA_CODE_Reporting_Airline=str(values["IATA_CODE_Reporting_Airline"]),
        Flight_Number_Reporting_Airline=int(natural_key[2]),
        OriginAirportSeqID=int(natural_key[3]),
        DestAirportSeqID=int(natural_key[4]),
        CRSDepTime=dep_time,
        Origin=str(values["Origin"]),
        Dest=str(values["Dest"]),
        CRSArrTime=arr_time,
        CRSElapsedTime=elapsed,
        scheduled_arrival_utc=infer_destination_arrival_utc(flight_date, dep_time, arr_time, elapsed),
        Cancelled=cancelled,
        Diverted=diverted,
        ArrDelay=_as_float(values["ArrDelay"], "ArrDelay"),
        ArrDel15=_as_int(values["ArrDel15"], "ArrDel15", required=False),
        WeatherDelay=_as_float(values["WeatherDelay"], "WeatherDelay"),
        NASDelay=_as_float(values["NASDelay"], "NASDelay"),
    )


def normalize_bts_archive(
    archive_path: str | Path,
    *,
    output_path: str | Path,
    manifest_path: str | Path,
) -> BTSNormalizationResult:
    """Verify the pinned archive and write its deterministic NYC subset."""

    archive = Path(archive_path)
    output = Path(output_path)
    manifest = Path(manifest_path)
    try:
        archive_sha256 = _sha256_path(archive)
        if archive_sha256 != ARCHIVE_SHA256:
            raise ValueError("archive checksum does not match pinned BTS archive")
        with zipfile.ZipFile(archive) as zipped:
            try:
                member_data = zipped.read(MEMBER_NAME)
            except KeyError as exc:
                raise ValueError("pinned BTS CSV member is missing") from exc
        if hashlib.sha256(member_data).hexdigest() != MEMBER_SHA256:
            raise ValueError("BTS CSV member checksum does not match pinned member")
        reader = csv.DictReader(io.TextIOWrapper(io.BytesIO(member_data), encoding="utf-8-sig", newline=""))
        if reader.fieldnames is None:
            raise ValueError("BTS CSV has no header")
        if tuple(reader.fieldnames[:-1]) != EXPECTED_FIELDS or reader.fieldnames[-1] != "":
            raise ValueError("BTS CSV fields do not match the pinned official schema")
        raw_rows = list(reader)
        if any(row.get("") not in (None, "") for row in raw_rows):
            raise ValueError("terminal unnamed BTS CSV column is not empty")
        rows = [
            _normalize_row(row, archive_sha256)
            for row in raw_rows
            if row.get("FlightDate") in FILTER_DATES and row.get("Dest") in FILTER_DESTINATIONS
        ]
        if len(rows) != 1_978:
            raise ValueError("BTS normalized subset count does not match pinned expectation")
        if len({row.row_id for row in rows}) != len(rows):
            raise ValueError("duplicate BTS natural key")
        rows.sort(key=lambda row: row.row_id)
        output.parent.mkdir(parents=True, exist_ok=True)
        serialized = _canonical_rows_bytes(rows)
        normalized_sha256 = hashlib.sha256(serialized).hexdigest()
        if normalized_sha256 != NORMALIZED_SNAPSHOT_SHA256:
            raise ValueError("normalized BTS subset checksum does not match pinned snapshot")
        output.write_bytes(serialized)
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            json.dumps(
                {
                    "archive_name": ARCHIVE_NAME,
                    "archive_sha256": ARCHIVE_SHA256,
                    "expected_named_field_count": len(EXPECTED_FIELDS),
                    "expected_terminal_unnamed_column_count": 1,
                    "expected_total_column_count": len(EXPECTED_FIELDS) + 1,
                    "filter": {"Dest": sorted(FILTER_DESTINATIONS), "FlightDate": sorted(FILTER_DATES)},
                    "member_name": MEMBER_NAME,
                    "member_sha256": MEMBER_SHA256,
                    "natural_key": [
                        "FlightDate", "DOT_ID_Reporting_Airline", "Flight_Number_Reporting_Airline",
                        "OriginAirportSeqID", "DestAirportSeqID", "CRSDepTime",
                    ],
                    "normalized_fields": list(NORMALIZED_FIELDS),
                    "normalized_sha256": normalized_sha256,
                    "row_count": len(rows),
                    "scheduled_arrival_method": "unique day offset minimizing schedule residual over -1,0,1,2",
                    "source_fields": [*EXPECTED_FIELDS, ""],
                    "source_id": NORMALIZED_SOURCE_ID,
                    "timezone": TIMEZONE_NAME,
                    "url": ARCHIVE_URL,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, zipfile.BadZipFile, csv.Error) as exc:
        return BTSNormalizationResult("blocked", failure_reason=str(exc))
    return BTSNormalizationResult("ok", output_path=output, manifest_path=manifest, rows=rows)


def resolve_bts_destination(canonical_facility: CanonicalEntity) -> str:
    """Resolve the three-letter airport code used by BTS destination rows."""

    if canonical_facility.entity_type != EntityType.AIRPORT:
        raise ValueError("canonical facility is not an airport")
    iata = [code.value for code in canonical_facility.codes if code.scheme.upper() == "IATA"]
    icao = [code.value for code in canonical_facility.codes if code.scheme.upper() == "ICAO"]
    if iata:
        if len(iata) != 1:
            raise ValueError("canonical facility must have exactly one IATA airport code")
        destination = iata[0]
    else:
        faa = [code.value for code in canonical_facility.codes if code.scheme.upper() == "FAA"]
        if len(faa) != 1:
            raise ValueError("canonical facility must have exactly one FAA airport code")
        destination = faa[0]
    if len(icao) != 1 or icao[0] != f"K{destination}":
        raise ValueError("canonical facility must have one matching ICAO airport identity")
    return destination


def _summary_and_seed(
    event: DecisionContextEvent,
    facility: CanonicalEntity,
    phase: str,
    window_start: datetime,
    window_end: datetime,
    source_id: str,
    source_snapshot_sha256: str,
    archive_sha256: str,
    aggregation_procedure: AggregationProcedureDescriptor,
    selected: list[BTSOnTimeRow],
) -> tuple[BTSOutcomeSummary, ObservationDerivationSeed]:
    completed = [row for row in selected if row.Cancelled == 0 and row.Diverted == 0]
    arrival_delays = [row.ArrDelay for row in completed if row.ArrDelay is not None]
    weather_delays = [row.WeatherDelay for row in selected if row.WeatherDelay is not None]
    nas_delays = [row.NASDelay for row in selected if row.NASDelay is not None]
    summary_id_payload = {
        "event_id": event.event_id,
        "facility_id": facility.entity_id,
        "phase": phase,
        "run_id": event.run_id,
        "source_id": source_id,
        "source_snapshot_sha256": source_snapshot_sha256,
        "window_end": window_end.isoformat(),
        "window_start": window_start.isoformat(),
    }
    summary_id = "bts-outcome:" + source_id + ":" + hashlib.sha256(
        _canonical_json_bytes(summary_id_payload)
    ).hexdigest()[:24]
    summary = BTSOutcomeSummary(
        summary_id=summary_id,
        run_id=event.run_id,
        event_id=event.event_id,
        facility_id=facility.entity_id,
        phase=phase,
        window_start=window_start,
        window_end=window_end,
        source_id=source_id,
        source_snapshot_sha256=source_snapshot_sha256,
        scheduled_arrival_count=len(selected),
        completed_arrival_count=len(completed),
        cancelled_count=sum(row.Cancelled == 1 for row in selected),
        diverted_count=sum(row.Diverted == 1 for row in selected),
        arrival_delay_15_count=sum(row.ArrDel15 == 1 for row in completed),
        mean_arrival_delay_minutes=statistics.mean(arrival_delays) if arrival_delays else None,
        median_arrival_delay_minutes=statistics.median(arrival_delays) if arrival_delays else None,
        carrier_reported_weather_delay_minutes=sum(weather_delays) if weather_delays else None,
        carrier_reported_nas_delay_minutes=sum(nas_delays) if nas_delays else None,
        reporting_scope=REPORTING_SCOPE,
        causal_claim=False,
    )
    selected_row_ids = tuple(sorted(row.row_id for row in selected))
    selected_row_ids_sha256 = hashlib.sha256(
        _canonical_json_bytes(selected_row_ids)
    ).hexdigest()
    summary_sha256 = hashlib.sha256(
        _canonical_json_bytes(summary.model_dump(mode="json"))
    ).hexdigest()
    derivation_payload = {
        "aggregation_procedure_checksum": aggregation_procedure.checksum,
        "aggregation_procedure_id": aggregation_procedure.procedure_id,
        "archive_sha256": archive_sha256,
        "selected_row_ids_sha256": selected_row_ids_sha256,
        "source_id": source_id,
        "source_snapshot_sha256": source_snapshot_sha256,
        "summary_id": summary.summary_id,
        "summary_sha256": summary_sha256,
    }
    seed = ObservationDerivationSeed(
        derivation_id="bts-derivation:" + hashlib.sha256(
            _canonical_json_bytes(derivation_payload)
        ).hexdigest()[:24],
        summary_id=summary.summary_id,
        summary_sha256=summary_sha256,
        source_id=source_id,
        source_snapshot_sha256=source_snapshot_sha256,
        archive_sha256=archive_sha256,
        aggregation_procedure_id=aggregation_procedure.procedure_id,
        aggregation_procedure_checksum=aggregation_procedure.checksum,
        selected_row_ids=selected_row_ids,
        selected_row_ids_sha256=selected_row_ids_sha256,
    )
    return summary, seed


def build_bts_outcome_summaries(
    event: DecisionContextEvent,
    canonical_facility: CanonicalEntity,
    rows: Iterable[BTSOnTimeRow],
    *,
    source_id: str,
    source_snapshot_sha256: str,
    manifest_binding: BTSManifestBinding,
    aggregation_procedure: AggregationProcedureDescriptor,
    timezone_name: str = TIMEZONE_NAME,
) -> BTSOutcomeBundle:
    """Aggregate BTS-reported arrivals and emit provenance seeds in one pass."""

    try:
        if timezone_name != TIMEZONE_NAME:
            ZoneInfo(timezone_name)
        if source_id != manifest_binding.source_id:
            raise ValueError("BTS outcome source ID does not match the manifest binding")
        if source_snapshot_sha256 != manifest_binding.normalized_snapshot_sha256:
            raise ValueError("BTS outcome source checksum does not match the manifest binding")
        all_rows = list(rows)
        if len({row.row_id for row in all_rows}) != len(all_rows):
            raise ValueError("duplicate normalized BTS row ID")
        reconstructed_sha256 = hashlib.sha256(_canonical_rows_bytes(all_rows)).hexdigest()
        if reconstructed_sha256 != source_snapshot_sha256:
            raise ValueError("BTS outcome rows do not match the supplied normalized snapshot checksum")
        destination = resolve_bts_destination(canonical_facility)
        if any(clock.tzinfo is None or clock.utcoffset() is None for clock in (event.operational_start, event.operational_end)):
            raise ValueError("decision context clocks must be timezone-aware")
        if event.operational_end <= event.operational_start:
            raise ValueError("operational end must be after operational start")
        source_rows = [row for row in all_rows if row.Dest == destination]
        if not source_rows:
            return BTSOutcomeBundle(status="insufficient", failure_reason="no BTS rows for canonical facility")
        phases = (
            ("baseline", event.operational_start - timedelta(hours=2), event.operational_start),
            ("active", event.operational_start, event.operational_end),
            ("recovery", event.operational_end, event.operational_end + timedelta(hours=6)),
        )
        phase_rows = [
            (
                phase,
                start.astimezone(UTC),
                end.astimezone(UTC),
                [
                    row
                    for row in source_rows
                    if start.astimezone(UTC) <= row.scheduled_arrival_utc < end.astimezone(UTC)
                ],
            )
            for phase, start, end in phases
        ]
        if not any(selected for _, _, _, selected in phase_rows):
            return BTSOutcomeBundle(
                status="insufficient",
                failure_reason="no BTS rows in decision-context phase windows",
            )
        summary_seed_pairs = [
            _summary_and_seed(
                event,
                canonical_facility,
                phase,
                start,
                end,
                source_id,
                source_snapshot_sha256,
                manifest_binding.archive_sha256,
                aggregation_procedure,
                selected,
            )
            for phase, start, end, selected in phase_rows
        ]
    except (AttributeError, TypeError, ValueError) as exc:
        return BTSOutcomeBundle(status="blocked", failure_reason=str(exc))
    return BTSOutcomeBundle(
        status="ok",
        summaries=[summary for summary, _ in summary_seed_pairs],
        derivation_seeds=[seed for _, seed in summary_seed_pairs],
    )
