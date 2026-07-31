"""Deterministic source adapters for NASR and NASA atmontoPlus airspace data."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
import zipfile


def _fixed_line(length: int, values: list[tuple[int, str]]) -> str:
    chars = [" "] * length
    for offset, value in values:
        chars[offset : offset + len(value)] = value
    return "".join(chars)


def test_nasr_adapter_streams_airports_artccs_and_distinct_assignment_roles(
    tmp_path: Path,
) -> None:
    from aviation_agentic_ai.agent_system.airspace_sources import (
        NASRAirportARTCCAssignmentSourceRecord,
        NASRAirportSourceRecord,
        NASRARTCCSourceRecord,
        iter_nasr_airspace_records,
    )

    apt_line = _fixed_line(
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
    ztl_line = _fixed_line(
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
    zjx_line = _fixed_line(
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
    archive_path = tmp_path / "nasr.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("subscription/AFF.txt", f"{ztl_line}\n{zjx_line}\n")
        archive.writestr("subscription/APT.txt", f"{apt_line}\r\n")

    records = list(iter_nasr_airspace_records(archive_path))
    airport = next(row for row in records if isinstance(row, NASRAirportSourceRecord))
    artccs = [row for row in records if isinstance(row, NASRARTCCSourceRecord)]
    assignments = [
        row
        for row in records
        if isinstance(row, NASRAirportARTCCAssignmentSourceRecord)
    ]

    assert airport.airport_code == "KATL"
    assert airport.faa_code == "ATL"
    assert airport.effective_start == datetime(2026, 5, 14, tzinfo=UTC)
    assert airport.source.zip_member == "subscription/APT.txt"
    assert airport.source.record_locator == "subscription/APT.txt:1"
    assert airport.source.canonical_content == apt_line
    assert airport.source.record_checksum == hashlib.sha256(
        apt_line.encode("latin-1")
    ).hexdigest()
    assert [(row.artcc_code, row.icao_code) for row in artccs] == [
        ("ZTL", "KZTL"),
        ("ZJX", "KZJX"),
    ]
    assert [
        (row.airport_code, row.artcc_code, row.assignment_role)
        for row in assignments
    ] == [
        ("KATL", "ZTL", "boundary"),
        ("KATL", "ZJX", "responsible"),
    ]


def test_nasa_adapter_preserves_route_sequence_track_seconds_and_all_sectors(
    tmp_path: Path,
) -> None:
    from aviation_agentic_ai.agent_system.airspace_sources import (
        NASAActualRouteSourceRecord,
        NASAFlightSourceRecord,
        NASANavigationFixSourceRecord,
        NASATrackPointSourceRecord,
        iter_nasa_atmonto_airspace_records,
    )

    flight_ttl = """
        @prefix atm: <https://data.nasa.gov/ontologies/atmonto/ATM#> .
        @prefix gen: <https://data.nasa.gov/ontologies/atmonto/general#> .
        @prefix nas: <https://data.nasa.gov/ontologies/atmonto/NAS#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        <urn:test:flight:F1> a atm:Flight ;
            atm:callSign "DAL1" ;
            atm:departureAirport nas:KATLairport ;
            atm:arrivalAirport nas:KJFKairport ;
            atm:actualDepartureTime "2014-07-15T02:00:07"^^xsd:dateTime ;
            atm:hasActualRoute <urn:test:route:F1> .
        <urn:test:route:F1> a atm:ActualFlightRoute ;
            gen:hasSequencedItem <urn:test:point:P2>, <urn:test:point:P1> .
        <urn:test:point:P2> a atm:AircraftTrackPoint ;
            gen:sequenceNumber 2 ;
            atm:reportingTime "2014-07-15T02:06:03"^^xsd:dateTime ;
            atm:aircraftFix <urn:test:fix:P2> .
        <urn:test:point:P1> a atm:AircraftTrackPoint ;
            gen:sequenceNumber 1 ;
            atm:reportingTime "2014-07-15T02:05:25"^^xsd:dateTime ;
            atm:groundSpeed 321 ;
            atm:aircraftFix <urn:test:fix:P1> .
        <urn:test:fix:P1> a atm:LatLonFix ;
            gen:latitude "33.6407"^^xsd:float ;
            gen:longitude "-84.4277"^^xsd:float ;
            gen:altitude "12000"^^xsd:float ;
            atm:locatedInSector nas:ZTLsector040,
                nas:ZTLsector041,
                nas:ZTLsector042 .
        <urn:test:fix:P2> a atm:LatLonFix .
    """
    archive_path = tmp_path / "atmonto.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("allFilesTTL/flightInst.ttl", flight_ttl)
        archive.writestr("allFilesTTL/fixInst.ttl", "@prefix atm: <urn:atm:> .")
        archive.writestr(
            "allFilesTTL/SectorLocationInst.ttl", "@prefix nas: <urn:nas:> ."
        )
        archive.writestr("allFilesTTL/not-allowlisted.ttl", "not valid turtle")

    records = list(
        iter_nasa_atmonto_airspace_records(
            archive_path,
            include_global_fixes=False,
        )
    )
    flight = next(row for row in records if isinstance(row, NASAFlightSourceRecord))
    route = next(row for row in records if isinstance(row, NASAActualRouteSourceRecord))
    points = [row for row in records if isinstance(row, NASATrackPointSourceRecord)]
    fixes = [row for row in records if isinstance(row, NASANavigationFixSourceRecord)]

    assert flight.subject_iri == "urn:test:flight:F1"
    assert flight.call_sign == "DAL1"
    assert flight.actual_departure_time == datetime(2014, 7, 15, 2, 0, 7, tzinfo=UTC)
    assert flight.time_basis == "source_naive_interpreted_utc"
    assert flight.source.zip_member == "allFilesTTL/flightInst.ttl"
    assert route.flight_iris == ("urn:test:flight:F1",)
    assert route.track_point_iris == (
        "urn:test:point:P1",
        "urn:test:point:P2",
    )
    assert [row.sequence_number for row in points] == [1, 2]
    assert points[0].reporting_time == datetime(
        2014, 7, 15, 2, 5, 25, tzinfo=UTC
    )
    assert points[0].reporting_time.second == 25
    assert points[0].ground_speed == 321
    assert points[0].latitude == 33.6407
    assert points[0].longitude == -84.4277
    assert points[0].altitude == 12000
    assert points[0].sector_iris == (
        "https://data.nasa.gov/ontologies/atmonto/NAS#ZTLsector040",
        "https://data.nasa.gov/ontologies/atmonto/NAS#ZTLsector041",
        "https://data.nasa.gov/ontologies/atmonto/NAS#ZTLsector042",
    )
    assert points[0].source.related_subject_iris == ("urn:test:fix:P1",)
    assert len(fixes) == 2
    assert all(row.source.canonical_triples for row in fixes)


def test_nasa_adapter_keeps_canonical_subject_triples_and_checksum(
    tmp_path: Path,
) -> None:
    from aviation_agentic_ai.agent_system.airspace_sources import (
        NASANavigationFixSourceRecord,
        NASASectorSourceRecord,
        iter_nasa_atmonto_airspace_records,
    )

    fix_ttl = """
        @prefix atm: <https://data.nasa.gov/ontologies/atmonto/ATM#> .
        @prefix gen: <https://data.nasa.gov/ontologies/atmonto/general#> .
        @prefix nas: <https://data.nasa.gov/ontologies/atmonto/NAS#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        nas:FixFOO a atm:GPSfix ;
            atm:fixId "FOO"^^xsd:string ;
            atm:locatedInSector nas:ZTLsector040, nas:ZTLsector041 ;
            gen:latitude "33.5"^^xsd:float ;
            gen:longitude "-84.5"^^xsd:float .
    """
    sector_ttl = """
        @prefix nas: <https://data.nasa.gov/ontologies/atmonto/NAS#> .
        nas:ZTLsector040 a nas:Sector .
        nas:ZTLsector041 a nas:Sector .
    """
    archive_path = tmp_path / "atmonto.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("allFilesTTL/flightInst.ttl", "@prefix atm: <urn:atm:> .")
        archive.writestr("allFilesTTL/fixInst.ttl", fix_ttl)
        archive.writestr("allFilesTTL/SectorLocationInst.ttl", sector_ttl)

    records = list(iter_nasa_atmonto_airspace_records(archive_path))
    fix = next(row for row in records if isinstance(row, NASANavigationFixSourceRecord))
    sectors = [row for row in records if isinstance(row, NASASectorSourceRecord)]
    expected_type_triple = (
        "<https://data.nasa.gov/ontologies/atmonto/NAS#FixFOO> "
        "<http://www.w3.org/1999/02/22-rdf-syntax-ns#type> "
        "<https://data.nasa.gov/ontologies/atmonto/ATM#GPSfix> ."
    )

    assert fix.subject_iri == "https://data.nasa.gov/ontologies/atmonto/NAS#FixFOO"
    assert fix.fix_identifier == "FOO"
    assert fix.sector_iris == (
        "https://data.nasa.gov/ontologies/atmonto/NAS#ZTLsector040",
        "https://data.nasa.gov/ontologies/atmonto/NAS#ZTLsector041",
    )
    assert expected_type_triple in fix.source.canonical_triples
    assert (
        fix.source.record_checksum
        == "87a0c2442a6f3f80fb8adcad1e910e6930fd265378b6a7ae497db7c927c9b353"
    )
    assert [row.subject_iri.rsplit("#", 1)[-1] for row in sectors] == [
        "ZTLsector040",
        "ZTLsector041",
    ]


def test_nasa_adapter_requires_each_allowlisted_member_exactly_once(
    tmp_path: Path,
) -> None:
    import pytest

    from aviation_agentic_ai.agent_system.airspace_sources import (
        iter_nasa_atmonto_airspace_records,
    )

    archive_path = tmp_path / "atmonto.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("flightInst.ttl", "@prefix atm: <urn:atm:> .")
        archive.writestr("nested/flightInst.ttl", "@prefix atm: <urn:atm:> .")
        archive.writestr("fixInst.ttl", "@prefix atm: <urn:atm:> .")
        archive.writestr("SectorLocationInst.ttl", "@prefix nas: <urn:nas:> .")

    with pytest.raises(ValueError, match="exactly one flightInst.ttl"):
        list(iter_nasa_atmonto_airspace_records(archive_path))
