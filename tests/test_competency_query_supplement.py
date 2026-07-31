from __future__ import annotations

import csv
from datetime import date, datetime
import io
from importlib import import_module
from pathlib import Path
import zipfile

import pytest
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD


ATM = Namespace("https://data.nasa.gov/ontologies/atmonto/ATM#")
GEN = Namespace("https://data.nasa.gov/ontologies/atmonto/general#")


def _fixed_line(length: int, fields: list[tuple[int, str]]) -> str:
    chars = [" "] * length
    for start, value in fields:
        chars[start : start + len(value)] = value
    return "".join(chars)


def _supplement_module():
    try:
        return import_module("aviation_agentic_ai.competency_query_supplement")
    except ModuleNotFoundError:
        pytest.fail("competency query supplement is not implemented")


def _add_passage(
    graph: Graph,
    *,
    flight: str,
    call_sign: str,
    point: str,
    fix: str,
    sector: str,
    reporting_time: str,
) -> None:
    flight_uri = URIRef(f"urn:test:flight:{flight}")
    route_uri = URIRef(f"urn:test:route:{flight}")
    point_uri = URIRef(f"urn:test:point:{point}")
    fix_uri = URIRef(f"urn:test:fix:{fix}")
    graph.add((flight_uri, RDF.type, ATM.Flight))
    graph.add((flight_uri, ATM.callSign, Literal(call_sign)))
    graph.add((flight_uri, ATM.actualDepartureDay, URIRef("urn:test:day:2026-05-17")))
    graph.add((flight_uri, ATM.hasActualRoute, route_uri))
    graph.add((route_uri, GEN.hasSequencedItem, point_uri))
    graph.add(
        (
            point_uri,
            ATM.reportingTime,
            Literal(reporting_time, datatype=XSD.dateTime),
        )
    )
    graph.add((point_uri, ATM.aircraftFix, fix_uri))
    graph.add((fix_uri, ATM.locatedInSector, URIRef(f"urn:test:sector:{sector}")))


def test_busiest_sector_counts_unique_flights_not_repeated_track_points() -> None:
    supplement = _supplement_module()
    graph = Graph()
    _add_passage(
        graph,
        flight="F1",
        call_sign="DAL1",
        point="F1-1",
        fix="F1-1",
        sector="A",
        reporting_time="2026-05-17T02:05:00",
    )
    _add_passage(
        graph,
        flight="F1",
        call_sign="DAL1",
        point="F1-2",
        fix="F1-2",
        sector="A",
        reporting_time="2026-05-17T02:15:00",
    )
    _add_passage(
        graph,
        flight="F2",
        call_sign="DAL2",
        point="F2-1",
        fix="F2-1",
        sector="A",
        reporting_time="2026-05-17T02:20:00",
    )
    _add_passage(
        graph,
        flight="F3",
        call_sign="DAL3",
        point="F3-1",
        fix="F3-1",
        sector="B",
        reporting_time="2026-05-17T02:25:00",
    )

    passages = supplement.extract_sector_passages(graph)
    ranking = supplement.rank_busiest_sectors(passages, hour=2)

    assert len(passages) == 4
    assert ranking[0].sector_id == "urn:test:sector:A"
    assert ranking[0].unique_flight_count == 2
    assert ranking[0].track_point_count == 3
    assert ranking[0].hour == 2
    assert ranking[0].source_dates == (datetime(2026, 5, 17).date(),)


def test_close_flight_pairs_use_closest_distinct_flights_and_strict_window() -> None:
    supplement = _supplement_module()
    graph = Graph()
    _add_passage(
        graph,
        flight="F1",
        call_sign="DAL1",
        point="F1-1",
        fix="F1-1",
        sector="A",
        reporting_time="2026-05-17T02:00:00",
    )
    _add_passage(
        graph,
        flight="F1",
        call_sign="DAL1",
        point="F1-2",
        fix="F1-2",
        sector="A",
        reporting_time="2026-05-17T02:10:00",
    )
    _add_passage(
        graph,
        flight="F2",
        call_sign="DAL2",
        point="F2-1",
        fix="F2-1",
        sector="A",
        reporting_time="2026-05-17T02:29:00",
    )
    _add_passage(
        graph,
        flight="G1",
        call_sign="UAL1",
        point="G1-1",
        fix="G1-1",
        sector="B",
        reporting_time="2026-05-17T02:00:00",
    )
    _add_passage(
        graph,
        flight="G2",
        call_sign="UAL2",
        point="G2-1",
        fix="G2-1",
        sector="B",
        reporting_time="2026-05-17T02:30:00",
    )

    passages = supplement.extract_sector_passages(graph)
    pairs = supplement.find_close_flight_pairs(
        passages,
        sector_id="urn:test:sector:A",
        max_minutes=30,
    )

    assert len(pairs) == 1
    assert pairs[0].first_call_sign == "DAL1"
    assert pairs[0].second_call_sign == "DAL2"
    assert pairs[0].minutes_apart == 19
    assert pairs[0].first_reporting_time == datetime(2026, 5, 17, 2, 10)
    assert pairs[0].second_reporting_time == datetime(2026, 5, 17, 2, 29)
    assert (
        supplement.find_close_flight_pairs(
            passages,
            sector_id="urn:test:sector:B",
            max_minutes=30,
        )
        == []
    )


def test_delta_a319_departures_require_reporting_carrier_type_and_ztl_origin() -> None:
    supplement = _supplement_module()
    flights = [
        supplement.FlightDeparture(
            flight_id="DL-101",
            flight_date=date(2026, 5, 17),
            reporting_carrier="DL",
            flight_number="101",
            tail_number="N101AA",
            origin="ATL",
            destination="DCA",
            wheels_off=datetime(2026, 5, 17, 14, 30),
        ),
        supplement.FlightDeparture(
            flight_id="DL-102",
            flight_date=date(2026, 5, 17),
            reporting_carrier="DL",
            flight_number="102",
            tail_number="N102AA",
            origin="ATL",
            destination="JFK",
            wheels_off=None,
        ),
        supplement.FlightDeparture(
            flight_id="UA-103",
            flight_date=date(2026, 5, 17),
            reporting_carrier="UA",
            flight_number="103",
            tail_number="N101AA",
            origin="ATL",
            destination="ORD",
            wheels_off=None,
        ),
        supplement.FlightDeparture(
            flight_id="DL-104",
            flight_date=date(2026, 5, 17),
            reporting_carrier="DL",
            flight_number="104",
            tail_number="N101AA",
            origin="JFK",
            destination="ATL",
            wheels_off=None,
        ),
        supplement.FlightDeparture(
            flight_id="DL-105",
            flight_date=date(2026, 5, 17),
            reporting_carrier="DL",
            flight_number="105",
            tail_number="N101AA",
            origin="ATL",
            destination="ORD",
            wheels_off=None,
        ),
    ]
    aircraft = {
        "N101AA": supplement.AircraftTechnicalRecord(
            tail_number="N101AA",
            manufacturer="AIRBUS INDUSTRIE",
            model="A-319-114",
        ),
        "N102AA": supplement.AircraftTechnicalRecord(
            tail_number="N102AA",
            manufacturer="AIRBUS",
            model="A-320-214",
        ),
    }

    matches = supplement.find_delta_a319_departures(
        flights,
        aircraft_by_tail=aircraft,
        ztl_airports={"ATL"},
    )

    assert [match.flight_id for match in matches] == ["DL-101"]
    assert matches[0].aircraft_model == "A-319-114"
    assert matches[0].carrier_role == "reporting_carrier"
    scheduled_matches = supplement.find_delta_a319_departures(
        flights,
        aircraft_by_tail=aircraft,
        ztl_airports={"ATL"},
        require_actual_departure=False,
    )
    assert [match.flight_id for match in scheduled_matches] == ["DL-101", "DL-105"]


def test_rainy_departures_use_wheels_off_and_noncausal_strict_time_join() -> None:
    supplement = _supplement_module()
    flights = [
        supplement.FlightDeparture(
            flight_id="DL-201",
            flight_date=date(2026, 5, 17),
            reporting_carrier="DL",
            flight_number="201",
            tail_number="N201AA",
            origin="ATL",
            destination="DCA",
            wheels_off=datetime(2026, 5, 17, 20, 0),
        ),
        supplement.FlightDeparture(
            flight_id="DL-202",
            flight_date=date(2026, 5, 17),
            reporting_carrier="DL",
            flight_number="202",
            tail_number="N202AA",
            origin="ATL",
            destination="JFK",
            wheels_off=None,
        ),
    ]
    observations = [
        supplement.WeatherObservation(
            station="KATL",
            observed_at=datetime(2026, 5, 17, 19, 31),
            weather_codes=("-RA",),
            raw_text="KATL 171931Z 00000KT 10SM -RA",
        ),
        supplement.WeatherObservation(
            station="KATL",
            observed_at=datetime(2026, 5, 17, 20, 0),
            weather_codes=("TS",),
            raw_text="KATL 172000Z 00000KT 10SM TS",
        ),
        supplement.WeatherObservation(
            station="KATL",
            observed_at=datetime(2026, 5, 17, 20, 30),
            weather_codes=("+TSRA",),
            raw_text="KATL 172030Z 00000KT 2SM +TSRA",
        ),
    ]

    matches = supplement.find_rain_associated_departures(
        flights,
        observations=observations,
        airport="ATL",
        max_minutes=30,
    )

    assert len(matches) == 1
    assert matches[0].flight_id == "DL-201"
    assert matches[0].weather_codes == ("-RA",)
    assert matches[0].minutes_apart == 29
    assert matches[0].association_role == "temporal_weather_context"
    assert matches[0].causal_claim is False
    assert matches[0].reporting_carrier == "DL"


def test_load_nasr_artcc_airports_uses_boundary_or_responsible_assignment(
    tmp_path: Path,
) -> None:
    supplement = _supplement_module()
    ztl_boundary = _fixed_line(
        1532,
        [
            (0, "APT"),
            (27, "ATL "),
            (31, "05/14/2026"),
            (133, "HARTSFIELD JACKSON ATLANTA INTL"),
            (637, "ZTL "),
            (674, "ZTL "),
            (1210, "KATL   "),
        ],
    )
    ztl_responsible = _fixed_line(
        1532,
        [
            (0, "APT"),
            (27, "TST "),
            (31, "05/14/2026"),
            (133, "TEST AIRPORT"),
            (637, "ZJX "),
            (674, "ZTL "),
            (1210, "KTST   "),
        ],
    )
    unrelated = _fixed_line(
        1532,
        [
            (0, "APT"),
            (27, "JFK "),
            (31, "05/14/2026"),
            (133, "JOHN F KENNEDY INTL"),
            (637, "ZNY "),
            (674, "ZNY "),
            (1210, "KJFK   "),
        ],
    )
    archive_path = tmp_path / "nasr.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("APT.txt", "\n".join((ztl_boundary, ztl_responsible, unrelated)))

    airports = supplement.load_nasr_artcc_airports(archive_path, artcc="ZTL")

    assert airports == {"ATL", "TST"}


def test_load_bts_departures_normalizes_known_origin_time_to_utc(tmp_path: Path) -> None:
    supplement = _supplement_module()
    archive_path = tmp_path / "bts.zip"
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=[
            "FlightDate",
            "IATA_CODE_Reporting_Airline",
            "Flight_Number_Reporting_Airline",
            "Tail_Number",
            "Origin",
            "Dest",
            "WheelsOff",
        ],
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerow(
        {
            "FlightDate": "2026-05-17",
            "IATA_CODE_Reporting_Airline": "DL",
            "Flight_Number_Reporting_Airline": "201",
            "Tail_Number": "N201AA",
            "Origin": "ATL",
            "Dest": "DCA",
            "WheelsOff": "1530",
        }
    )
    writer.writerow(
        {
            "FlightDate": "2026-05-17",
            "IATA_CODE_Reporting_Airline": "DL",
            "Flight_Number_Reporting_Airline": "202",
            "Tail_Number": "N202AA",
            "Origin": "ATL",
            "Dest": "JFK",
            "WheelsOff": "",
        }
    )
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("bts.csv", buffer.getvalue())

    flights = supplement.load_bts_departures(
        archive_path,
        start_date=date(2026, 5, 17),
        end_date=date(2026, 5, 18),
        origins={"ATL"},
        origin_timezones={"ATL": "America/New_York"},
    )

    assert len(flights) == 2
    assert flights[0].wheels_off == datetime(2026, 5, 17, 19, 30)
    assert flights[0].wheels_off_time_basis == "UTC"
    assert flights[1].wheels_off is None


def test_aircraft_registry_loader_keeps_only_technical_fields(tmp_path: Path) -> None:
    supplement = _supplement_module()
    archive_path = tmp_path / "registry.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(
            "ACFTREF.txt",
            "CODE,MFR,MODEL\n"
            "1234567,AIRBUS INDUSTRIE,A-319-114\n"
            "7654321,BOEING,737-900\n",
        )
        archive.writestr(
            "MASTER.txt",
            "N-NUMBER,MFR MDL CODE,NAME,STREET\n"
            "201AA,1234567,PERSON NAME,PRIVATE ADDRESS\n"
            "999ZZ,7654321,OTHER NAME,OTHER ADDRESS\n",
        )

    records = supplement.load_aircraft_technical_records(
        archive_path,
        tail_numbers={"N201AA"},
    )

    assert set(records) == {"N201AA"}
    assert records["N201AA"].__dict__ == {
        "tail_number": "N201AA",
        "manufacturer": "AIRBUS INDUSTRIE",
        "model": "A-319-114",
    }


def test_iem_weather_loader_preserves_codes_time_and_raw_metar(tmp_path: Path) -> None:
    supplement = _supplement_module()
    path = tmp_path / "asos.csv"
    path.write_text(
        "station,valid,wxcodes,metar\n"
        'ATL,2026-05-17 19:56,-TSRA,"KATL 171956Z 2SM -TSRA"\n'
        'ATL,2026-05-17 20:00,TS,"KATL 172000Z 10SM TS"\n'
        'ATL,2026-05-18 00:00,null,"KATL 180000Z 10SM CLR"\n',
        encoding="utf-8",
    )

    observations = supplement.load_iem_asos_observations(
        path,
        start=datetime(2026, 5, 17, 19, 0),
        end=datetime(2026, 5, 17, 21, 0),
    )

    assert len(observations) == 2
    assert observations[0].station == "KATL"
    assert observations[0].observed_at == datetime(2026, 5, 17, 19, 56)
    assert observations[0].weather_codes == ("-TSRA",)
    assert observations[0].raw_text == "KATL 171956Z 2SM -TSRA"


def test_nasa_bundle_loader_extracts_flight_sector_passages(tmp_path: Path) -> None:
    supplement = _supplement_module()
    archive_path = tmp_path / "atmonto.zip"
    flight_ttl = """
        @prefix atm: <https://data.nasa.gov/ontologies/atmonto/ATM#> .
        @prefix gen: <https://data.nasa.gov/ontologies/atmonto/general#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        <urn:test:flight:F1> a atm:Flight ;
            atm:callSign "DAL1" ;
            atm:hasActualRoute <urn:test:route:F1> .
        <urn:test:route:F1> gen:hasSequencedItem <urn:test:point:F1-1> .
        <urn:test:point:F1-1>
            atm:reportingTime "2014-07-15T02:05:00"^^xsd:dateTime ;
            atm:aircraftFix <urn:test:fix:F1-1> .
    """
    fix_ttl = """
        @prefix atm: <https://data.nasa.gov/ontologies/atmonto/ATM#> .
        <urn:test:fix:F1-1> atm:locatedInSector <urn:test:sector:A> .
    """
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("allFilesTTL/flightInst.ttl", flight_ttl)
        archive.writestr("allFilesTTL/fixInst.ttl", fix_ttl)

    passages = supplement.load_nasa_sector_passages(archive_path)

    assert len(passages) == 1
    assert passages[0].call_sign == "DAL1"
    assert passages[0].sector_id == "urn:test:sector:A"


def test_compiled_report_separates_original_queries_from_modern_proxies() -> None:
    supplement = _supplement_module()
    f1_record = supplement.AircraftMatchedDeparture(
        flight_id="bts:flight:1",
        flight_date=date(2026, 5, 17),
        reporting_carrier="DL",
        carrier_role="reporting_carrier",
        flight_number="101",
        tail_number="N101AA",
        origin="ATL",
        destination="DCA",
        aircraft_manufacturer="AIRBUS INDUSTRIE",
        aircraft_model="A319-114",
    )
    f3_record = supplement.RainAssociatedDeparture(
        flight_id="bts:flight:2",
        flight_date=date(2026, 5, 17),
        origin="ATL",
        wheels_off=datetime(2026, 5, 17, 19, 30),
        station="KATL",
        observed_at=datetime(2026, 5, 17, 19, 52),
        weather_codes=("-RA",),
        minutes_apart=22,
        association_role="temporal_weather_context",
        causal_claim=False,
    )
    ranking = supplement.SectorRanking(
        sector_id="urn:test:sector:A",
        hour=2,
        unique_flight_count=12,
        track_point_count=146,
        source_dates=(date(2014, 7, 15),),
    )
    pair = supplement.FlightPair(
        sector_id="urn:test:sector:ZTL040",
        passage_date=date(2014, 7, 15),
        first_flight_id="urn:test:flight:F1",
        first_call_sign="DAL1",
        first_reporting_time=datetime(2014, 7, 15, 2, 0),
        second_flight_id="urn:test:flight:F2",
        second_call_sign="JBU2",
        second_reporting_time=datetime(2014, 7, 15, 2, 20),
        minutes_apart=20,
    )

    report = supplement.compile_competency_query_report(
        sources=[{"source_id": "nasa-atmonto-plus", "sha256": "a" * 64}],
        ztl_airport_count=131,
        f1_scheduled=[f1_record],
        f1_actual=[f1_record],
        f3_matches=[f3_record],
        sector_rankings=[ranking],
        close_pairs=[pair],
        sector_id="urn:test:sector:ZTL040",
    )

    assert report["authoritative_store_integration"] is False
    assert report["query_agent_integration"] is False
    assert (
        report["query_results"]["F1"]["original_query_status"]
        == "not_executed_original_2012_data_unavailable"
    )
    assert report["query_results"]["F1"]["execution_variant"] == "F1_modern_proxy"
    assert "tail_number" not in report["query_results"]["F1"]["records"][0]
    assert report["query_results"]["F3S"]["causal_claim"] is False
    assert report["query_results"]["S4"]["top_sector"]["distinct_flight_count"] == 12
    assert report["query_results"]["S4"]["top_sector"]["appendix_binding_count"] == 146
    assert report["query_results"]["S1S"]["pair_count"] == 1


def test_source_artifact_verification_is_checksum_bound(tmp_path: Path) -> None:
    supplement = _supplement_module()
    source_path = tmp_path / "source.txt"
    source_path.write_text("pinned source", encoding="utf-8")
    source_config = {
        "sample": {
            "path": str(source_path),
            "url": "https://example.test/source",
            "sha256": "0" * 64,
            "role": "test",
            "temporal_scope": "2026-05",
        }
    }

    with pytest.raises(ValueError, match="checksum mismatch"):
        supplement.verify_source_artifacts(source_config)
