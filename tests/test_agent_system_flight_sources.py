from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from collections.abc import Iterator
from datetime import UTC, date, datetime
from pathlib import Path

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.flight_sources import (
    iter_bts_flight_sources,
    iter_faa_registry_technical_sources,
    iter_iem_weather_sources,
)


def _write_bts_archive(path: Path, rows: list[dict[str, str]]) -> None:
    columns = [
        "FlightDate",
        "IATA_CODE_Reporting_Airline",
        "Flight_Number_Reporting_Airline",
        "Tail_Number",
        "Origin",
        "Dest",
        "CRSDepTime",
        "WheelsOff",
        "Cancelled",
        "Diverted",
    ]
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("nested/On_Time_Reporting.csv", buffer.getvalue())


def test_bts_adapter_streams_rows_with_utc_times_and_operational_states(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "bts.zip"
    _write_bts_archive(
        archive_path,
        [
            {
                "FlightDate": "2026-05-17",
                "IATA_CODE_Reporting_Airline": "DL",
                "Flight_Number_Reporting_Airline": "201",
                "Tail_Number": " n201-aa ",
                "Origin": "ATL",
                "Dest": "DCA",
                "CRSDepTime": "2400",
                "WheelsOff": "15:30",
                "Cancelled": "0.00",
                "Diverted": "1.00",
            },
            {
                "FlightDate": "2026-05-17",
                "IATA_CODE_Reporting_Airline": "DL",
                "Flight_Number_Reporting_Airline": "202",
                "Tail_Number": "",
                "Origin": "ATL",
                "Dest": "JFK",
                "CRSDepTime": "1700",
                "WheelsOff": "",
                "Cancelled": "1",
                "Diverted": "0",
            },
        ],
    )

    records = iter_bts_flight_sources(
        archive_path,
        origin_timezones={"ATL": "America/New_York"},
        asset_id="asset:bts-may-2026",
        asset_sha256="a" * 64,
    )

    assert isinstance(records, Iterator)
    first, second = records
    assert first.source.family is SourceFamily.BTS_FLIGHT_OPERATION
    assert first.source.source_id.startswith(
        "bts-row:" + "a" * 64 + ":nested/On_Time_Reporting.csv:2:"
    )
    assert first.tail_number == "N201AA"
    assert first.scheduled_departure == datetime(2026, 5, 18, 4, 0, tzinfo=UTC)
    assert first.actual_wheels_off == datetime(2026, 5, 17, 19, 30, tzinfo=UTC)
    assert first.time_basis == "utc"
    assert first.cancelled is False
    assert first.diverted is True
    assert first.source.asset_id == "asset:bts-may-2026"
    assert first.source.metadata["member"] == "nested/On_Time_Reporting.csv"
    assert first.source.metadata["row_number"] == 2
    assert len(str(first.source.metadata["raw_row_sha256"])) == 64
    assert first.source.metadata["time_basis"] == "utc"
    assert json.loads(first.source.content) == {
        "actual_wheels_off": "2026-05-17T19:30:00+00:00",
        "cancelled": False,
        "destination": "DCA",
        "diverted": True,
        "flight_date": "2026-05-17",
        "flight_number": "201",
        "origin": "ATL",
        "reporting_carrier": "DL",
        "scheduled_departure": "2026-05-18T04:00:00+00:00",
        "tail_number": "N201AA",
        "time_basis": "utc",
    }
    assert second.cancelled is True
    assert second.diverted is False
    assert second.actual_wheels_off is None


def test_bts_adapter_preserves_origin_local_time_when_timezone_is_unknown(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "bts.zip"
    _write_bts_archive(
        archive_path,
        [
            {
                "FlightDate": "2026-05-17",
                "IATA_CODE_Reporting_Airline": "9X",
                "Flight_Number_Reporting_Airline": "77",
                "Tail_Number": "123ab",
                "Origin": "ZZZ",
                "Dest": "ATL",
                "CRSDepTime": "0915",
                "WheelsOff": "0930",
                "Cancelled": "0",
                "Diverted": "0",
            }
        ],
    )

    record = next(iter_bts_flight_sources(archive_path, origin_timezones={}))

    assert record.scheduled_departure == datetime(2026, 5, 17, 9, 15)
    assert record.actual_wheels_off == datetime(2026, 5, 17, 9, 30)
    assert record.time_basis == "origin_local"
    assert record.tail_number == "N123AB"
    assert record.source.logical_time == "2026-05-17T09:15:00"


def test_bts_adapter_filters_service_dates_with_inclusive_boundaries(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "bts.zip"
    _write_bts_archive(
        archive_path,
        [
            {
                "FlightDate": service_date,
                "IATA_CODE_Reporting_Airline": "DL",
                "Flight_Number_Reporting_Airline": flight_number,
                "Tail_Number": "N100DL",
                "Origin": "ATL",
                "Dest": "DCA",
                "CRSDepTime": "0900",
                "WheelsOff": "0910",
                "Cancelled": "0",
                "Diverted": "0",
            }
            for service_date, flight_number in (
                ("2026-05-14", "114"),
                ("2026-05-15", "115"),
                ("2026-05-17", "117"),
                ("2026-05-18", "118"),
            )
        ],
    )

    records = list(
        iter_bts_flight_sources(
            archive_path,
            origin_timezones={"ATL": "America/New_York"},
            service_date_from=date(2026, 5, 15),
            service_date_to=date(2026, 5, 17),
        )
    )

    assert [record.flight_date for record in records] == [
        date(2026, 5, 15),
        date(2026, 5, 17),
    ]


def test_bts_adapter_filters_origins_after_normalizing_codes(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "bts.zip"
    _write_bts_archive(
        archive_path,
        [
            {
                "FlightDate": "2026-05-17",
                "IATA_CODE_Reporting_Airline": "DL",
                "Flight_Number_Reporting_Airline": flight_number,
                "Tail_Number": "N100DL",
                "Origin": origin,
                "Dest": "DCA",
                "CRSDepTime": "0900",
                "WheelsOff": "0910",
                "Cancelled": "0",
                "Diverted": "0",
            }
            for origin, flight_number in (("atl", "201"), ("JFK", "202"))
        ],
    )

    records = list(
        iter_bts_flight_sources(
            archive_path,
            origin_timezones={"ATL": "America/New_York"},
            origin_airports={" atl "},
        )
    )

    assert [(record.origin, record.flight_number) for record in records] == [
        ("ATL", "201")
    ]


def test_bts_adapter_filters_exact_directed_routes_after_normalizing_codes(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "bts.zip"
    _write_bts_archive(
        archive_path,
        [
            {
                "FlightDate": "2026-05-17",
                "IATA_CODE_Reporting_Airline": "DL",
                "Flight_Number_Reporting_Airline": flight_number,
                "Tail_Number": "N100DL",
                "Origin": origin,
                "Dest": destination,
                "CRSDepTime": "0900",
                "WheelsOff": "0910",
                "Cancelled": "0",
                "Diverted": "0",
            }
            for origin, destination, flight_number in (
                ("atl", "dca", "301"),
                ("DCA", "ATL", "302"),
                ("ATL", "JFK", "303"),
            )
        ],
    )

    records = list(
        iter_bts_flight_sources(
            archive_path,
            origin_timezones={"ATL": "America/New_York"},
            routes={(" atl ", " dca ")},
        )
    )

    assert [
        (record.origin, record.destination, record.flight_number)
        for record in records
    ] == [("ATL", "DCA", "301")]


def test_faa_registry_adapter_joins_technical_fields_without_personal_data(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "registry.zip"
    master_row = "201-aa,1234567,PERSON NAME,PRIVATE ADDRESS\n"
    reference_row = "1234567,AIRBUS INDUSTRIE,A-319-114\n"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(
            "registry/MASTER.txt",
            "N-NUMBER,MFR MDL CODE,NAME,STREET\n" + master_row,
        )
        archive.writestr(
            "registry/ACFTREF.txt",
            "CODE,MFR,MODEL\n" + reference_row,
        )

    record = next(
        iter_faa_registry_technical_sources(
            archive_path,
            registry_snapshot_at=datetime(2026, 5, 21, tzinfo=UTC),
            tail_numbers={"n201aa"},
            asset_sha256="b" * 64,
        )
    )

    assert record.source.family is SourceFamily.FAA_AIRCRAFT_REGISTRY
    assert record.tail_number == "N201AA"
    assert record.model_code == "1234567"
    assert record.manufacturer == "AIRBUS INDUSTRIE"
    assert record.model == "A-319-114"
    assert record.registry_snapshot_at == datetime(2026, 5, 21, tzinfo=UTC)
    assert record.source.effective_date == datetime(2026, 5, 21, tzinfo=UTC)
    assert record.source.metadata["master_member"] == "registry/MASTER.txt"
    assert record.source.metadata["reference_member"] == "registry/ACFTREF.txt"
    assert record.source.metadata["master_raw_row_sha256"] == hashlib.sha256(
        master_row.encode()
    ).hexdigest()
    assert record.source.metadata["reference_raw_row_sha256"] == hashlib.sha256(
        reference_row.encode()
    ).hexdigest()
    serialized = record.source.content + json.dumps(record.source.metadata)
    assert "PERSON NAME" not in serialized
    assert "PRIVATE ADDRESS" not in serialized
    assert json.loads(record.source.content) == {
        "manufacturer": "AIRBUS INDUSTRIE",
        "model": "A-319-114",
        "model_code": "1234567",
        "registry_snapshot_at": "2026-05-21T00:00:00+00:00",
        "tail_number": "N201AA",
    }


def test_iem_adapter_preserves_metar_and_speci_reports_with_utc_identity(
    tmp_path: Path,
) -> None:
    path = tmp_path / "asos.csv"
    path.write_text(
        "station,valid,wxcodes,metar\n"
        'ATL,2026-05-17 19:56,-TSRA,"KATL 171956Z 2SM -TSRA"\n'
        'ATL,2026-05-17T20:00:00+00:00,TS,"SPECI KATL 172000Z 10SM TS"\n'
        'ATL,2026-05-17 21:00,null,"KATL 172100Z 10SM CLR"\n',
        encoding="utf-8",
    )

    records = list(
        iter_iem_weather_sources(
            path,
            asset_id="asset:iem-atl",
            asset_sha256="c" * 64,
        )
    )

    assert [record.report_type for record in records] == ["METAR", "SPECI", "METAR"]
    assert records[0].station_id == "KATL"
    assert records[0].observed_at == datetime(2026, 5, 17, 19, 56, tzinfo=UTC)
    assert records[0].phenomenon_tokens == ("-TSRA",)
    assert records[0].raw_report == "KATL 171956Z 2SM -TSRA"
    assert records[1].raw_report == "SPECI KATL 172000Z 10SM TS"
    assert records[1].phenomenon_tokens == ("TS",)
    assert records[2].phenomenon_tokens == ()
    assert records[0].source.family is SourceFamily.HISTORICAL_METAR_SPECI
    assert records[0].source.logical_time == "2026-05-17T19:56:00+00:00"
    assert records[0].source.metadata["time_basis"] == "utc"
    assert records[0].source.metadata["row_number"] == 2
    assert records[0].source.asset_id == "asset:iem-atl"
    assert len(str(records[0].source.metadata["raw_row_sha256"])) == 64
    assert json.loads(records[1].source.content)["report_type"] == "SPECI"
