"""End-to-end Flight/Airspace ingestion through the authoritative store."""

from __future__ import annotations

import csv
import io
import json
from datetime import UTC, datetime
import zipfile
from pathlib import Path

from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore


def _write_bts_archive(
    path: Path,
    *,
    rows: list[dict[str, str]] | None = None,
) -> None:
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
    writer.writerows(
        rows
        or [
            {
            "FlightDate": "2026-05-17",
            "IATA_CODE_Reporting_Airline": "DL",
            "Flight_Number_Reporting_Airline": "201",
            "Tail_Number": "N201AA",
            "Origin": "ATL",
            "Dest": "JFK",
            "CRSDepTime": "1530",
            "WheelsOff": "1545",
            "Cancelled": "0",
            "Diverted": "0",
            }
        ]
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("monthly/on_time.csv", buffer.getvalue())


def _fixed_width(length: int, values: list[tuple[int, str]]) -> str:
    characters = [" "] * length
    for offset, value in values:
        characters[offset : offset + len(value)] = value
    return "".join(characters)


def test_ingests_configured_bts_and_weather_records_with_exact_anchors(
    tmp_path: Path,
) -> None:
    """Dropping anchors or bypassing Store v2 must break this public behavior."""

    from aviation_agentic_ai.agent_system.flight_airspace_ingestion import (
        run_flight_airspace_ingestion,
    )

    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    bts_path = raw_root / "bts.zip"
    weather_path = raw_root / "weather.csv"
    _write_bts_archive(bts_path)
    weather_path.write_text(
        "station,valid,wxcodes,metar\n"
        'ATL,2026-05-17 19:56,-TSRA,"KATL 171956Z 2SM -TSRA"\n',
        encoding="utf-8",
    )
    config = {
        "sources": {
            "bts_flight_operations": "bts.zip",
            "historical_metar_speci": "weather.csv",
        },
        "source_metadata": {
            "bts_flight_operations": {
                "temporal_domain_id": "proxy-2026-05",
                "origin_timezones": {"ATL": "America/New_York"},
                "ingestion_scope": {"mode": "all"},
            },
            "historical_metar_speci": {
                "temporal_domain_id": "proxy-2026-05",
            },
        },
    }
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="flight-airspace-ingestion-test",
        create=True,
    )
    try:
        summary = run_flight_airspace_ingestion(
            config=config,
            store=store,
            source_root=raw_root,
            project_root=tmp_path / "unused-project",
            chunk_size=1,
            max_result_records=1,
        )

        assert summary.asset_count == 2
        assert summary.root_count == 2
        assert summary.discovered_count == 2
        assert summary.selected_count == 2
        assert summary.attempted_count == 2
        assert summary.skipped_count == 0
        assert summary.ok_count == 2
        assert summary.insufficient_count == 0
        assert summary.blocked_count == 0
        assert len(summary.results) == 1

        flight_row = store._connection.execute(
            "SELECT * FROM flight_publications"
        ).fetchone()
        weather_row = store._connection.execute(
            "SELECT * FROM weather_observations"
        ).fetchone()
        assert flight_row is not None
        assert flight_row["reporting_carrier"] == "DL"
        assert flight_row["origin_airport_id"] == "ATL"
        assert flight_row["destination_airport_id"] == "JFK"
        assert flight_row["time_basis"] == "utc"
        assert weather_row is not None
        assert weather_row["station_id"] == "KATL"
        assert weather_row["report_type"] == "METAR"

        links = store._connection.execute(
            """
            SELECT link.evidence_text, anchor.char_start, anchor.char_end,
                   version.content
            FROM publication_evidence_links AS link
            JOIN source_anchors AS anchor
              ON anchor.source_anchor_id = link.source_anchor_id
            JOIN source_versions AS version
              ON version.source_version_id = link.source_version_id
            ORDER BY link.evidence_link_id
            """
        ).fetchall()
        assert len(links) == 2
        assert all(row["char_start"] == 0 for row in links)
        assert all(row["char_end"] == len(row["content"]) for row in links)
        assert all(row["evidence_text"] == row["content"] for row in links)
    finally:
        store.close()


def test_ingests_registry_record_as_two_source_bound_technical_roots(
    tmp_path: Path,
) -> None:
    """Registry ingestion must retain technical data without owner fields."""

    from aviation_agentic_ai.agent_system.flight_airspace_ingestion import (
        ingest_flight_airspace_sources,
    )

    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    with zipfile.ZipFile(raw_root / "registry.zip", "w") as archive:
        archive.writestr(
            "registry/MASTER.txt",
            "N-NUMBER,MFR MDL CODE,NAME,STREET\n"
            "201-aa,1234567,PERSON NAME,PRIVATE ADDRESS\n",
        )
        archive.writestr(
            "registry/ACFTREF.txt",
            "CODE,MFR,MODEL\n1234567,AIRBUS INDUSTRIE,A-319-114\n",
        )
    config = {
        "sources": {"faa_aircraft_registry": "registry.zip"},
        "source_metadata": {
            "faa_aircraft_registry": {
                "temporal_domain_id": "registry-2026-07-28",
                "registry_snapshot_at": "2026-07-28T00:00:00+00:00",
            }
        },
    }
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="registry-ingestion-test",
        create=True,
    )
    try:
        summary = ingest_flight_airspace_sources(
            config=config,
            store=store,
            source_root=raw_root,
            project_root=tmp_path / "unused-project",
            chunk_size=10,
        )

        assert summary.root_count == 2
        assert summary.ok_count == 2
        assert {result.root_kind for result in summary.results} == {
            "aircraft",
            "aircraft_model",
        }
        aircraft = store._connection.execute("SELECT * FROM aircraft").fetchone()
        model = store._connection.execute("SELECT * FROM aircraft_models").fetchone()
        version = store.list_source_versions()[0]
        assert aircraft["registration_mark"] == "N201AA"
        assert model["manufacturer_code"] == "AIRBUS INDUSTRIE"
        assert model["model_code"] == "1234567"
        assert model["display_name"] == "A-319-114"
        assert version.logical_time == datetime(
            2026, 7, 28, tzinfo=UTC
        ).isoformat()
        serialized = version.content + json.dumps(version.metadata)
        assert "PERSON NAME" not in serialized
        assert "PRIVATE ADDRESS" not in serialized
        assert store._connection.execute(
            "SELECT COUNT(*) FROM publication_evidence_links"
        ).fetchone()[0] == 2
    finally:
        store.close()


def test_incomplete_bts_row_is_insufficient_without_hiding_later_flight(
    tmp_path: Path,
) -> None:
    """One incomplete source row must not terminate the remaining stream."""

    from aviation_agentic_ai.agent_system.flight_airspace_ingestion import (
        ingest_flight_airspace_sources,
    )

    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    _write_bts_archive(
        raw_root / "bts.zip",
        rows=[
            {
                "FlightDate": "2026-05-17",
                "IATA_CODE_Reporting_Airline": "DL",
                "Flight_Number_Reporting_Airline": "200",
                "Tail_Number": "N200AA",
                "Origin": "ATL",
                "Dest": "",
                "CRSDepTime": "1500",
                "WheelsOff": "1510",
                "Cancelled": "0",
                "Diverted": "0",
            },
            {
                "FlightDate": "2026-05-17",
                "IATA_CODE_Reporting_Airline": "DL",
                "Flight_Number_Reporting_Airline": "201",
                "Tail_Number": "N201AA",
                "Origin": "ATL",
                "Dest": "JFK",
                "CRSDepTime": "1530",
                "WheelsOff": "1545",
                "Cancelled": "0",
                "Diverted": "0",
            },
        ],
    )
    config = {
        "sources": {"bts_flight_operations": "bts.zip"},
        "source_metadata": {
            "bts_flight_operations": {
                "temporal_domain_id": "proxy-2026-05",
                "origin_timezones": {"ATL": "America/New_York"},
                "ingestion_scope": {"mode": "all"},
            }
        },
    }
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="flight-airspace-failure-isolation-test",
        create=True,
    )
    try:
        summary = ingest_flight_airspace_sources(
            config=config,
            store=store,
            source_root=raw_root,
            project_root=tmp_path / "unused-project",
            chunk_size=2,
        )

        assert summary.root_count == 2
        assert summary.insufficient_count == 1
        assert summary.ok_count == 1
        assert summary.blocked_count == 0
        assert summary.results[0].status == "insufficient"
        assert summary.results[0].root_id is None
        assert summary.results[0].publication_id is None
        assert "destination" in summary.results[0].reason
        assert store._connection.execute(
            "SELECT COUNT(*) FROM source_versions"
        ).fetchone()[0] == 2
        assert store._connection.execute(
            "SELECT COUNT(*) FROM flight_publications"
        ).fetchone()[0] == 1
    finally:
        store.close()


def test_bts_ingestion_uses_explicit_bounded_prototype_scope(
    tmp_path: Path,
) -> None:
    """Only records inside the configured day and airport set enter Store v2."""

    from aviation_agentic_ai.agent_system.flight_airspace_ingestion import (
        run_flight_airspace_ingestion,
    )

    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    _write_bts_archive(
        raw_root / "bts.zip",
        rows=[
            {
                "FlightDate": "2026-05-19",
                "IATA_CODE_Reporting_Airline": "DL",
                "Flight_Number_Reporting_Airline": "199",
                "Tail_Number": "N199AA",
                "Origin": "ATL",
                "Dest": "JFK",
                "CRSDepTime": "1400",
                "WheelsOff": "1415",
                "Cancelled": "0",
                "Diverted": "0",
            },
            {
                "FlightDate": "2026-05-20",
                "IATA_CODE_Reporting_Airline": "DL",
                "Flight_Number_Reporting_Airline": "200",
                "Tail_Number": "N200AA",
                "Origin": "ATL",
                "Dest": "JFK",
                "CRSDepTime": "1500",
                "WheelsOff": "1515",
                "Cancelled": "0",
                "Diverted": "0",
            },
            {
                "FlightDate": "2026-05-20",
                "IATA_CODE_Reporting_Airline": "B6",
                "Flight_Number_Reporting_Airline": "201",
                "Tail_Number": "N201AA",
                "Origin": "BOS",
                "Dest": "JFK",
                "CRSDepTime": "1600",
                "WheelsOff": "1615",
                "Cancelled": "0",
                "Diverted": "0",
            },
        ],
    )
    config = {
        "sources": {"bts_flight_operations": "bts.zip"},
        "source_metadata": {
            "bts_flight_operations": {
                "temporal_domain_id": "prototype-2026-05-20",
                "origin_timezones": {"ATL": "America/New_York"},
                "ingestion_scope": {
                    "mode": "bounded",
                    "service_date_from": "2026-05-20",
                    "service_date_to": "2026-05-20",
                    "routes": [["ATL", "JFK"], ["JFK", "ATL"]],
                },
            }
        },
    }
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="bounded-flight-ingestion-test",
        create=True,
    )
    try:
        summary = run_flight_airspace_ingestion(
            config,
            store,
            source_root=raw_root,
            project_root=tmp_path / "unused-project",
            chunk_size=2,
        )

        assert summary.root_count == 1
        row = store._connection.execute(
            "SELECT service_date, origin_airport_id FROM flight_publications"
        ).fetchone()
        assert (row["service_date"], row["origin_airport_id"]) == (
            "2026-05-20",
            "ATL",
        )
    finally:
        store.close()


def test_bts_ingestion_rejects_implicit_full_month_scope(tmp_path: Path) -> None:
    """A full monthly scan must be an explicit configuration choice."""

    from aviation_agentic_ai.agent_system.flight_airspace_ingestion import (
        run_flight_airspace_ingestion,
    )

    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    _write_bts_archive(raw_root / "bts.zip")
    config = {
        "sources": {"bts_flight_operations": "bts.zip"},
        "source_metadata": {
            "bts_flight_operations": {
                "temporal_domain_id": "proxy-2026-05",
                "origin_timezones": {"ATL": "America/New_York"},
            }
        },
    }
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="implicit-full-month-rejection-test",
        create=True,
    )
    try:
        import pytest

        with pytest.raises(ValueError, match="ingestion_scope"):
            run_flight_airspace_ingestion(
                config,
                store,
                source_root=raw_root,
                project_root=tmp_path / "unused-project",
            )
    finally:
        store.close()


def test_ingests_nasr_airport_artccs_and_role_preserving_assignments(
    tmp_path: Path,
) -> None:
    """Collapsing boundary and responsible ARTCC roles must fail this test."""

    from aviation_agentic_ai.agent_system.flight_airspace_ingestion import (
        ingest_flight_airspace_sources,
    )

    apt = _fixed_width(
        1532,
        [
            (0, "APT"),
            (27, "ATL "),
            (31, "05/14/2026"),
            (48, "GA"),
            (93, "ATLANTA"),
            (133, "HARTSFIELD JACKSON ATLANTA INTL"),
            (637, "ZTL "),
            (674, "ZJX "),
            (1210, "KATL   "),
        ],
    )
    ztl = _fixed_width(
        240,
        [
            (0, "AFF1"),
            (4, "ZTL "),
            (8, "ATLANTA CENTER"),
            (128, "ARTCC"),
            (133, "05/14/2026"),
            (143, "GA"),
            (225, "KZTL"),
        ],
    )
    zjx = _fixed_width(
        240,
        [
            (0, "AFF1"),
            (4, "ZJX "),
            (8, "JACKSONVILLE CENTER"),
            (128, "ARTCC"),
            (133, "05/14/2026"),
            (143, "FL"),
            (225, "KZJX"),
        ],
    )
    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    with zipfile.ZipFile(raw_root / "nasr.zip", "w") as archive:
        archive.writestr("subscription/APT.txt", f"{apt}\n")
        archive.writestr("subscription/AFF.txt", f"{ztl}\n{zjx}\n")
    config = {
        "sources": {"nasr_airspace_zip": "nasr.zip"},
        "source_metadata": {
            "nasr_airspace": {
                "temporal_domain_id": "nasr-2026-05-14",
            }
        },
    }
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="nasr-airspace-ingestion-test",
        create=True,
    )
    try:
        summary = ingest_flight_airspace_sources(
            config=config,
            store=store,
            source_root=raw_root,
            project_root=tmp_path / "unused-project",
            chunk_size=2,
        )

        assert summary.root_count == 5
        assert summary.ok_count == 5
        assert store._connection.execute(
            "SELECT COUNT(*) FROM airports"
        ).fetchone()[0] == 1
        assert store._connection.execute(
            "SELECT COUNT(*) FROM artccs"
        ).fetchone()[0] == 2
        assignments = store._connection.execute(
            """
            SELECT assignment_role, effective_start
            FROM airport_artcc_assignments
            ORDER BY assignment_role
            """
        ).fetchall()
        assert [(row["assignment_role"], row["effective_start"]) for row in assignments] == [
            ("boundary", "2026-05-14T00:00:00+00:00"),
            ("responsible", "2026-05-14T00:00:00+00:00"),
        ]
        assert store._connection.execute(
            "SELECT COUNT(*) FROM publication_evidence_links"
        ).fetchone()[0] == 5
    finally:
        store.close()


def test_nasa_flight_trajectory_is_published_without_forcing_bts_semantics(
    tmp_path: Path,
) -> None:
    """One NASA Flight publication owns its route and exact track evidence."""

    from aviation_agentic_ai.agent_system.flight_airspace_ingestion import (
        run_flight_airspace_ingestion,
    )

    raw_root = tmp_path / "raw"
    raw_root.mkdir()
    with zipfile.ZipFile(raw_root / "atmonto.zip", "w") as archive:
        archive.writestr(
            "flightInst.ttl",
            "@prefix atm: <https://data.nasa.gov/ontologies/atmonto/ATM#> .\n"
            "@prefix gen: <https://data.nasa.gov/ontologies/atmonto/general#> .\n"
            "@prefix nas: <https://data.nasa.gov/ontologies/atmonto/NAS#> .\n"
            "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
            "<urn:test:flight:1> a atm:Flight ;\n"
            "  atm:callSign \"DAL1\" ;\n"
            "  atm:departureAirport nas:KATLairport ;\n"
            "  atm:arrivalAirport nas:KJFKairport ;\n"
            "  atm:actualDepartureTime \"2014-07-15T02:00:07\"^^xsd:dateTime ;\n"
            "  atm:actualArrivalTime \"2014-07-15T04:00:07\"^^xsd:dateTime ;\n"
            "  atm:operatedBy nas:DALairline ;\n"
            "  atm:hasActualRoute <urn:test:route:1> .\n"
            "<urn:test:route:1> a atm:ActualFlightRoute ;\n"
            "  gen:hasSequencedItem <urn:test:point:1> .\n"
            "<urn:test:point:1> a atm:AircraftTrackPoint ;\n"
            "  gen:sequenceNumber 1 ;\n"
            "  atm:reportingTime \"2014-07-15T02:05:25\"^^xsd:dateTime ;\n"
            "  atm:groundSpeed 321 ;\n"
            "  atm:aircraftFix <urn:test:fix:1> .\n"
            "<urn:test:fix:1> a atm:LatLonFix ;\n"
            "  gen:latitude \"33.6407\"^^xsd:float ;\n"
            "  gen:longitude \"-84.4277\"^^xsd:float .\n",
        )
        archive.writestr(
            "fixInst.ttl",
            "@prefix atm: <https://data.nasa.gov/ontologies/atmonto/ATM#> .\n"
            "@prefix nas: <https://data.nasa.gov/ontologies/atmonto/NAS#> .\n"
            "<urn:test:fix:1> a atm:LatLonFix ;\n"
            "  atm:locatedInSector nas:ZTLsector040 .\n",
        )
        archive.writestr(
            "SectorLocationInst.ttl",
            "@prefix nas: <https://data.nasa.gov/ontologies/atmonto/NAS#> .\n",
        )
        common = (
            "@prefix atm: <https://data.nasa.gov/ontologies/atmonto/ATM#> .\n"
            "@prefix data: <https://data.nasa.gov/ontologies/atmonto/data#> .\n"
            "@prefix nas: <https://data.nasa.gov/ontologies/atmonto/NAS#> .\n"
            "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        )
        archive.writestr(
            "METARinst.ttl",
            common
            + "data:M1 a data:METARreport ; "
            "data:associatedMETARreportingStation nas:KJFKairport ; "
            "data:dataIntervalStartTime \"2014-07-15T02:00:00\"^^xsd:dateTime ; "
            "data:metarReportString \"KJFK 150200Z 10SM CLR\" .\n",
        )
        archive.writestr(
            "TAFinst.ttl",
            common
            + "data:T1 a data:TAFreport ; "
            "data:forecastingAirport nas:KJFKairport ; "
            "data:forecastIssueTime \"2014-07-15T01:30:00\"^^xsd:dateTime ; "
            "data:dataIntervalStartTime \"2014-07-15T02:00:00\"^^xsd:dateTime ; "
            "data:dataIntervalEndTime \"2014-07-16T02:00:00\"^^xsd:dateTime ; "
            "data:tafReportString \"TAF KJFK 150130Z\" .\n",
        )
        archive.writestr(
            "ASPMinst.ttl",
            common
            + "nas:KJFKairport data:hasAirportData data:A1 .\n"
            "data:A1 a data:AirportData ; "
            "data:dataIntervalStartTime \"2014-07-15T02:00:00\"^^xsd:dateTime ; "
            "data:dataIntervalEndTime \"2014-07-15T03:00:00\"^^xsd:dateTime ; "
            "data:airportArrivalRate 31 ; data:arrivalDemand 42 .\n",
        )
        archive.writestr(
            "TMIinst.ttl",
            common
            + "atm:G1 a atm:GroundDelayProgramTMI ; "
            "atm:controlledNASelement nas:KJFKairport ; "
            "atm:issuedTime \"2014-07-15T01:30:00\"^^xsd:dateTime ; "
            "atm:effectiveStartTime \"2014-07-15T02:00:00\"^^xsd:dateTime ; "
            "atm:effectiveEndTime \"2014-07-15T03:00:00\"^^xsd:dateTime ; "
            "atm:impactingCondition \"WEATHER\" .\n",
        )
    config = {
        "sources": {"nasa_atmonto_instances": "atmonto.zip"},
        "source_metadata": {
            "nasa_atmonto_instances": {
                "temporal_domain_id": "nasa-atmonto-2014",
                "include_public_sample_layers": True,
                "sample_date": "2014-07-15",
                "weather_aspm_airport_codes": ["KJFK", "KEWR", "KLGA"],
            }
        },
    }
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="nasa-ingestion-test",
        create=True,
    )
    try:
        summary = run_flight_airspace_ingestion(
            config,
            store,
            source_root=raw_root,
            project_root=tmp_path / "unused-project",
            chunk_size=2,
        )

        assert summary.discovered_count == 7
        assert summary.ok_count == 7
        assert summary.insufficient_count == 0
        assert store._connection.execute(
            "SELECT COUNT(*) FROM source_versions"
        ).fetchone()[0] == 8
        sector = store._connection.execute("SELECT * FROM sectors").fetchone()
        assert sector["sector_id"].endswith("#ZTLsector040")
        flight = store._connection.execute(
            "SELECT * FROM flight_publications"
        ).fetchone()
        assert flight["source_flight_key"] == "urn:test:flight:1"
        assert flight["call_sign"] == "DAL1"
        assert flight["reporting_carrier"] is None
        assert flight["scheduled_departure_key"] is None
        assert flight["actual_departure_time"] == "2014-07-15T02:00:07+00:00"
        assert flight["actual_arrival_time"] == "2014-07-15T04:00:07+00:00"
        assert store._connection.execute("SELECT COUNT(*) FROM routes").fetchone()[0] == 1
        assert store._connection.execute(
            "SELECT COUNT(*) FROM track_points"
        ).fetchone()[0] == 1
        assert store._connection.execute(
            "SELECT COUNT(*) FROM sector_passages"
        ).fetchone()[0] == 1
        assert store._connection.execute(
            "SELECT COUNT(*) FROM weather_observations"
        ).fetchone()[0] == 1
        assert store._connection.execute(
            "SELECT COUNT(*) FROM weather_forecasts"
        ).fetchone()[0] == 1
        assert store._connection.execute(
            "SELECT COUNT(*) FROM airport_operational_observations"
        ).fetchone()[0] == 1
        assert store._connection.execute(
            "SELECT COUNT(*) FROM source_tmi_publications"
        ).fetchone()[0] == 1
        assert store._connection.execute(
            "SELECT COUNT(*) FROM publication_sources"
        ).fetchone()[0] == 9
    finally:
        store.close()
