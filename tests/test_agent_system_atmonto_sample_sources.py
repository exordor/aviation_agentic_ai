"""NASA atmontoPlus public-sample source adapter contracts."""

from __future__ import annotations

from datetime import UTC, date, datetime
import hashlib
from pathlib import Path
import zipfile

from aviation_agentic_ai.agent_system.atmonto_sample_sources import (
    ATMONTOAirportDataSourceRecord,
    ATMONTHistoricalWeatherSourceRecord,
    ATMONTOTAFSourceRecord,
    ATMONTOTMISourceRecord,
    iter_atmonto_public_sample_records,
)


def _write_public_sample_archive(path: Path) -> None:
    prefixes = """
        @prefix atm: <https://data.nasa.gov/ontologies/atmonto/ATM#> .
        @prefix data: <https://data.nasa.gov/ontologies/atmonto/data#> .
        @prefix nas: <https://data.nasa.gov/ontologies/atmonto/NAS#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    """
    metar = prefixes + """
        data:METAR_KJFK201407151200 a data:METARreport ;
            data:associatedMETARreportingStation nas:KJFKairport ;
            data:dataIntervalStartTime "2014-07-15T12:00:00"^^xsd:dateTime ;
            data:dataIntervalEndTime "2014-07-15T12:35:00"^^xsd:dateTime ;
            data:metarReportString "KJFK 151200Z 10SM CLR" .
        data:METAR_KLAX201407151200 a data:METARreport ;
            data:associatedMETARreportingStation nas:KLAXairport ;
            data:dataIntervalStartTime "2014-07-15T12:00:00"^^xsd:dateTime ;
            data:metarReportString "KLAX 151200Z 10SM CLR" .
        data:METAR_KEWR201407161200 a data:METARreport ;
            data:associatedMETARreportingStation nas:KEWRairport ;
            data:dataIntervalStartTime "2014-07-16T12:00:00"^^xsd:dateTime ;
            data:metarReportString "KEWR 161200Z 10SM CLR" .
    """
    taf = prefixes + """
        data:TAF_KEWR201407150530 a data:TAFreport ;
            data:forecastingAirport nas:KEWRairport ;
            data:forecastIssueTime "2014-07-15T05:30:00"^^xsd:dateTime ;
            data:dataIntervalStartTime "2014-07-15T06:00:00"^^xsd:dateTime ;
            data:dataIntervalEndTime "2014-07-16T06:00:00"^^xsd:dateTime ;
            data:tafReportString "TAF KEWR 150530Z 1506/1606 18005KT P6SM" .
        data:TAF_KLGA201407140530 a data:TAFreport ;
            data:forecastingAirport nas:KLGAairport ;
            data:forecastIssueTime "2014-07-14T05:30:00"^^xsd:dateTime ;
            data:dataIntervalStartTime "2014-07-14T06:00:00"^^xsd:dateTime ;
            data:dataIntervalEndTime "2014-07-15T06:00:00"^^xsd:dateTime ;
            data:tafReportString "TAF KLGA 140530Z" .
    """
    aspm = prefixes + """
        nas:KLGAairport data:hasAirportData data:KLGAairportData20140715230000 .
        data:KLGAairportData20140715230000 a data:AirportData ;
            data:dataIntervalStartTime "2014-07-15T23:00:00"^^xsd:dateTime ;
            data:dataIntervalEndTime "2014-07-16T00:00:00"^^xsd:dateTime ;
            data:airportArrivalRate 31 ;
            data:arrivalDemand 42 ;
            data:scheduledArrivals 39 .
        nas:KJFKairport data:hasAirportData data:KJFKairportData20140716000000 .
        data:KJFKairportData20140716000000 a data:AirportData ;
            data:dataIntervalStartTime "2014-07-16T00:00:00"^^xsd:dateTime ;
            data:airportArrivalRate 40 .
    """
    tmi = prefixes + """
        atm:GDP20140715057 a atm:GroundDelayProgramTMI ;
            atm:controlledNASelement nas:KLGAairport ;
            atm:issuedTime "2014-07-15T14:19:00"^^xsd:dateTime ;
            atm:effectiveStartTime "2014-07-15T14:17:00"^^xsd:dateTime ;
            atm:effectiveEndTime "2014-07-16T05:59:00"^^xsd:dateTime ;
            atm:impactingCondition "WEATHER / THUNDERSTORMS" .
        atm:GS20140715016 a atm:GroundStopTMI ;
            atm:controlledNASelement nas:KJFKairport ;
            atm:issuedTime "2014-07-15T01:42:00"^^xsd:dateTime ;
            atm:effectiveStartTime "2014-07-15T01:28:00"^^xsd:dateTime ;
            atm:effectiveEndTime "2014-07-15T02:45:00"^^xsd:dateTime ;
            atm:impactingCondition "WEATHER" .
        atm:RRT20140715002 a atm:ReRouteTMI ;
            atm:controlledNASelement nas:ZMEcenter ;
            atm:issuedTime "2014-07-15T00:12:00"^^xsd:dateTime ;
            atm:effectiveStartTime "2014-07-15T00:12:00"^^xsd:dateTime ;
            atm:effectiveEndTime "2014-07-15T02:30:00"^^xsd:dateTime ;
            atm:reRouteReason "WEATHER" .
        atm:GDP20140716001 a atm:GroundDelayProgramTMI ;
            atm:controlledNASelement nas:KJFKairport ;
            atm:issuedTime "2014-07-16T00:01:00"^^xsd:dateTime ;
            atm:effectiveStartTime "2014-07-16T00:01:00"^^xsd:dateTime ;
            atm:effectiveEndTime "2014-07-16T01:00:00"^^xsd:dateTime .
    """
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("allFilesTTL/METARinst.ttl", metar)
        archive.writestr("allFilesTTL/TAFinst.ttl", taf)
        archive.writestr("allFilesTTL/ASPMinst.ttl", aspm)
        archive.writestr("allFilesTTL/TMIinst.ttl", tmi)
        archive.writestr("allFilesTTL/aggregate.ttl", "this is not Turtle")


def test_atmonto_public_sample_adapter_selects_typed_records_by_date_and_airport(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "allFilesTTL.zip"
    _write_public_sample_archive(archive_path)

    records = list(iter_atmonto_public_sample_records(archive_path))

    weather = [
        row for row in records if isinstance(row, ATMONTHistoricalWeatherSourceRecord)
    ]
    taf = [row for row in records if isinstance(row, ATMONTOTAFSourceRecord)]
    airport_data = [
        row for row in records if isinstance(row, ATMONTOAirportDataSourceRecord)
    ]
    tmis = [row for row in records if isinstance(row, ATMONTOTMISourceRecord)]

    assert len(weather) == 1
    assert weather[0].airport_iri.endswith("#KJFKairport")
    assert weather[0].observed_at == datetime(2014, 7, 15, 12, tzinfo=UTC)
    assert weather[0].report_text == "KJFK 151200Z 10SM CLR"

    assert len(taf) == 1
    assert taf[0].airport_iri.endswith("#KEWRairport")
    assert taf[0].issued_at == datetime(2014, 7, 15, 5, 30, tzinfo=UTC)
    assert taf[0].valid_to == datetime(2014, 7, 16, 6, tzinfo=UTC)
    assert taf[0].report_text.startswith("TAF KEWR")

    assert len(airport_data) == 1
    assert airport_data[0].airport_iri.endswith("#KLGAairport")
    assert airport_data[0].interval_start == datetime(
        2014, 7, 15, 23, tzinfo=UTC
    )
    assert dict(airport_data[0].metrics) == {
        "https://data.nasa.gov/ontologies/atmonto/data#airportArrivalRate": "31",
        "https://data.nasa.gov/ontologies/atmonto/data#arrivalDemand": "42",
        "https://data.nasa.gov/ontologies/atmonto/data#scheduledArrivals": "39",
    }

    assert [(row.tmi_type, row.reason) for row in tmis] == [
        ("GroundDelayProgramTMI", "WEATHER / THUNDERSTORMS"),
        ("GroundStopTMI", "WEATHER"),
        ("ReRouteTMI", "WEATHER"),
    ]
    assert tmis[2].controlled_element_iri.endswith("#ZMEcenter")
    assert tmis[2].airport_iri is None
    assert tmis[0].issued_at == datetime(2014, 7, 15, 14, 19, tzinfo=UTC)
    assert tmis[0].effective_to == datetime(2014, 7, 16, 5, 59, tzinfo=UTC)


def test_atmonto_public_sample_trace_binds_subject_member_and_canonical_triples(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "allFilesTTL.zip"
    _write_public_sample_archive(archive_path)

    record = next(iter_atmonto_public_sample_records(archive_path))
    canonical_payload = "\n".join(record.source.canonical_subject_triples)

    assert record.subject_iri == record.source.subject_iri
    assert record.source.zip_member == "allFilesTTL/METARinst.ttl"
    assert record.source.record_locator.endswith("#" + record.subject_iri)
    assert record.source.archive_checksum == hashlib.sha256(
        archive_path.read_bytes()
    ).hexdigest()
    assert record.source.record_checksum == hashlib.sha256(
        canonical_payload.encode("utf-8")
    ).hexdigest()
    assert any("METARreport" in triple for triple in record.source.canonical_subject_triples)


def test_atmonto_public_sample_adapter_accepts_explicit_sample_scope(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "allFilesTTL.zip"
    _write_public_sample_archive(archive_path)

    records = list(
        iter_atmonto_public_sample_records(
            archive_path,
            sample_date=date(2014, 7, 16),
            airport_codes={" kjfk ", " kewr "},
        )
    )

    assert [record.subject_iri.rsplit("#", 1)[-1] for record in records] == [
        "METAR_KEWR201407161200",
        "KJFKairportData20140716000000",
        "GDP20140716001",
    ]

