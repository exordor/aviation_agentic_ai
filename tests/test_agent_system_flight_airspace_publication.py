"""Source-qualified ATMONTO Flight/Airspace publication tests."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from datetime import UTC, datetime

import pytest

from aviation_agentic_ai.agent_system.airspace_sources import (
    NASAActualRouteSourceRecord,
    NASAFlightSourceRecord,
    NASANavigationFixSourceRecord,
    NASARDFSourceTrace,
    NASASectorSourceRecord,
    NASATrackPointSourceRecord,
)
from aviation_agentic_ai.agent_system.contracts import (
    SourceFamily,
    SourceSnapshot,
    SourceSnapshotRegistry,
    ValidationProfileRef,
)
from aviation_agentic_ai.agent_system.flight_airspace_publication import (
    compile_nasa_flight_airspace_facts,
    run_nasa_flight_airspace_publication_kernel,
)
from aviation_agentic_ai.agent_system.materialize import FormalPublicationBlocked
from aviation_agentic_ai.agent_system.validation_profiles import (
    LoadedValidationProfile,
    ValidationProfileRegistry,
)


RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
XSD_DATETIME = "http://www.w3.org/2001/XMLSchema#dateTime"
XSD_STRING = "http://www.w3.org/2001/XMLSchema#string"
ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
NAS = "https://data.nasa.gov/ontologies/atmonto/NAS#"
EQP = "https://data.nasa.gov/ontologies/atmonto/equipment#"
GEN = "https://data.nasa.gov/ontologies/atmonto/general#"


def _profile(
    layer: str,
    *,
    classes: dict[str, tuple[str, ...]],
    properties: dict[str, tuple[str, tuple[str, ...], tuple[str, ...]]],
) -> LoadedValidationProfile:
    checksum = hashlib.sha256(layer.encode()).hexdigest()
    return LoadedValidationProfile(
        ref=ValidationProfileRef(
            profile_id=f"test-{layer}",
            profile_checksum=checksum,
            layer=layer,
        ),
        source_path=f"test:{layer}",
        namespace_prefixes={
            "atm": ATM,
            "nas": NAS,
            "eqp": EQP,
            "gen": GEN,
        },
        class_mappings={
            iri: {"iri": iri, "label": iri.rsplit("#", 1)[-1]}
            for iri in classes
        },
        property_mappings={
            iri: {"iri": iri, "kind": kind}
            for iri, (kind, _domain, _range) in properties.items()
        },
        class_ancestors=classes,
        property_domains={
            iri: domain for iri, (_kind, domain, _range) in properties.items()
        },
        property_ranges={
            iri: range_ for iri, (_kind, _domain, range_) in properties.items()
        },
        allowed_evidence_modes=("source_text",),
        source_families_by_evidence_mode={
            "source_text": (SourceFamily.NASA_ATMONTO_INSTANCE,)
        },
    )


def _registry() -> ValidationProfileRegistry:
    flight = f"{ATM}Flight"
    route = f"{ATM}ActualFlightRoute"
    point = f"{ATM}AircraftTrackPoint"
    nav_fix = f"{ATM}NavigationFix"
    sector = f"{NAS}Sector"
    airport = f"{NAS}Airport"
    carrier = f"{NAS}AirCarrier"
    aircraft = f"{EQP}Aircraft"
    sequence = f"{GEN}Sequence"
    sequenced_item = f"{GEN}SequencedItem"
    return ValidationProfileRegistry(
        profiles=(
            _profile(
                "flight_operation",
                classes={
                    flight: (flight,),
                    route: (route, sequence),
                    airport: (airport,),
                    carrier: (carrier,),
                    aircraft: (aircraft,),
                },
                properties={
                    f"{ATM}callSign": ("datatype", (flight,), ()),
                    f"{ATM}departureAirport": ("object", (flight,), (airport,)),
                    f"{ATM}arrivalAirport": ("object", (flight,), (airport,)),
                    f"{ATM}actualDepartureTime": ("datatype", (flight,), ()),
                    f"{ATM}operatedBy": ("object", (flight,), (carrier,)),
                    f"{ATM}aircraftFlown": ("object", (flight,), (aircraft,)),
                    f"{ATM}hasActualRoute": ("object", (flight,), (route,)),
                },
            ),
            _profile(
                "trajectory",
                classes={
                    route: (route, sequence),
                    point: (point, sequenced_item),
                    nav_fix: (nav_fix,),
                },
                properties={
                    f"{GEN}hasSequencedItem": (
                        "object",
                        (sequence,),
                        (sequenced_item,),
                    ),
                    f"{ATM}reportingTime": ("datatype", (point,), ()),
                    f"{ATM}aircraftFix": ("object", (point,), (nav_fix,)),
                },
            ),
            _profile(
                "aeronautical_reference",
                classes={
                    nav_fix: (nav_fix,),
                    sector: (sector,),
                },
                properties={
                    f"{ATM}locatedInSector": (
                        "object",
                        (nav_fix,),
                        (sector,),
                    ),
                },
            ),
        )
    )


def _trace(source_id: str, subject: str, triples: tuple[str, ...]) -> NASARDFSourceTrace:
    content = "\n".join(sorted(triples))
    return NASARDFSourceTrace(
        source_record_id=source_id,
        archive_checksum="a" * 64,
        zip_member="flightInst.ttl",
        record_locator=f"flightInst.ttl#{subject}",
        subject_iri=subject,
        related_subject_iris=(),
        canonical_triples=tuple(sorted(triples)),
        record_checksum=hashlib.sha256(content.encode()).hexdigest(),
    )


def _source_records() -> tuple[
    NASAFlightSourceRecord,
    NASAActualRouteSourceRecord,
    NASATrackPointSourceRecord,
    NASANavigationFixSourceRecord,
    NASASectorSourceRecord,
]:
    flight_iri = "urn:test:flight:1"
    route_iri = "urn:test:route:1"
    point_iri = "urn:test:point:1"
    fix_iri = "urn:test:fix:1"
    sector_iri = f"{NAS}ZTLsector040"
    airport_from = f"{NAS}KATLairport"
    airport_to = f"{NAS}KJFKairport"
    carrier = f"{NAS}DALairline"
    aircraft = "urn:test:aircraft:N12345"
    flight_trace = _trace(
        "nasa-flight-1",
        flight_iri,
        (
            f"<{flight_iri}> <{RDF_TYPE}> <{ATM}Flight> .",
            f"<{flight_iri}> <{ATM}callSign> \"DAL1\" .",
            f"<{flight_iri}> <{ATM}departureAirport> <{airport_from}> .",
            f"<{flight_iri}> <{ATM}arrivalAirport> <{airport_to}> .",
            f"<{flight_iri}> <{ATM}actualDepartureTime> \"2014-07-15T02:00:07+00:00\"^^<{XSD_DATETIME}> .",
            f"<{flight_iri}> <{ATM}operatedBy> <{carrier}> .",
            f"<{flight_iri}> <{ATM}aircraftFlown> <{aircraft}> .",
            f"<{flight_iri}> <{ATM}hasActualRoute> <{route_iri}> .",
        ),
    )
    route_trace = _trace(
        "nasa-route-1",
        route_iri,
        (
            f"<{route_iri}> <{RDF_TYPE}> <{ATM}ActualFlightRoute> .",
            f"<{route_iri}> <{GEN}hasSequencedItem> <{point_iri}> .",
        ),
    )
    point_trace = _trace(
        "nasa-point-1",
        point_iri,
        (
            f"<{point_iri}> <{RDF_TYPE}> <{ATM}AircraftTrackPoint> .",
            f"<{point_iri}> <{ATM}reportingTime> \"2014-07-15T02:05:25+00:00\"^^<{XSD_DATETIME}> .",
            f"<{point_iri}> <{ATM}aircraftFix> <{fix_iri}> .",
        ),
    )
    fix_trace = _trace(
        "nasa-fix-1",
        fix_iri,
        (
            f"<{fix_iri}> <{RDF_TYPE}> <{ATM}LatLonFix> .",
            f"<{fix_iri}> <{ATM}locatedInSector> <{sector_iri}> .",
        ),
    )
    sector_trace = _trace(
        "nasa-sector-1",
        sector_iri,
        (f"<{sector_iri}> <{RDF_TYPE}> <{NAS}Sector> .",),
    )
    return (
        NASAFlightSourceRecord(
            source=flight_trace,
            subject_iri=flight_iri,
            call_sign="DAL1",
            departure_airport_iri=airport_from,
            arrival_airport_iri=airport_to,
            actual_departure_time=datetime(2014, 7, 15, 2, 0, 7, tzinfo=UTC),
            actual_arrival_time=datetime(2014, 7, 15, 4, 0, 7, tzinfo=UTC),
            time_basis="explicit_utc",
            actual_route_iris=(route_iri,),
            operated_by_iri=carrier,
            aircraft_iri=aircraft,
            aircraft_type_iri="urn:test:aircraft-model:A319",
        ),
        NASAActualRouteSourceRecord(
            source=route_trace,
            subject_iri=route_iri,
            flight_iris=(flight_iri,),
            track_point_iris=(point_iri,),
        ),
        NASATrackPointSourceRecord(
            source=point_trace,
            subject_iri=point_iri,
            route_iris=(route_iri,),
            sequence_number=1,
            reporting_time=datetime(2014, 7, 15, 2, 5, 25, tzinfo=UTC),
            time_basis="explicit_utc",
            ground_speed=321,
            fix_iri=fix_iri,
            latitude=33.6407,
            longitude=-84.4277,
            altitude=12000,
            sector_iris=(sector_iri,),
        ),
        NASANavigationFixSourceRecord(
            source=fix_trace,
            subject_iri=fix_iri,
            fix_identifier="LatLonFix1",
            latitude=33.6407,
            longitude=-84.4277,
            altitude=12000,
            sector_iris=(sector_iri,),
        ),
        NASASectorSourceRecord(
            source=sector_trace,
            subject_iri=sector_iri,
            sector_identifier="ZTLsector040",
        ),
    )


def _snapshots(records: tuple[object, ...], family: SourceFamily = SourceFamily.NASA_ATMONTO_INSTANCE) -> SourceSnapshotRegistry:
    snapshots = []
    for record in records:
        trace = record.source
        content = "\n".join(trace.canonical_triples)
        snapshots.append(
            SourceSnapshot(
                source_id=trace.source_record_id,
                family=family,
                content=content,
                content_sha256=hashlib.sha256(content.encode()).hexdigest(),
            )
        )
    return SourceSnapshotRegistry(snapshots=tuple(snapshots))


def _semantic_rows(compilation) -> set[tuple[str, str, str]]:
    return {
        (fact.subject_iri, fact.predicate_iri, fact.object_value)
        for fact in compilation.facts
    }


def test_compiles_source_supported_flight_route_point_fix_and_sector_facts() -> None:
    """Deleting any core compiler branch must remove an expected ATMONTO fact."""

    flight, route, point, fix, sector = _source_records()
    registry = _registry()
    flight_root = "urn:test:internal-flight-root:1"

    compilation = compile_nasa_flight_airspace_facts(
        flights=(flight,),
        routes=(route,),
        track_points=(point,),
        navigation_fixes=(fix,),
        sectors=(sector,),
        flight_root_ids={flight.subject_iri: flight_root},
        profile_registry=registry,
    )
    publication = run_nasa_flight_airspace_publication_kernel(
        compilation=compilation,
        profile_registry=registry,
        source_snapshot=_snapshots((flight, route, point, fix, sector)),
    )

    assert len(publication.accepted) == 15
    assert _semantic_rows(compilation) == {
        (flight_root, RDF_TYPE, f"{ATM}Flight"),
        (flight_root, f"{ATM}callSign", "DAL1"),
        (flight_root, f"{ATM}departureAirport", flight.departure_airport_iri),
        (flight_root, f"{ATM}arrivalAirport", flight.arrival_airport_iri),
        (
            flight_root,
            f"{ATM}actualDepartureTime",
            "2014-07-15T02:00:07+00:00",
        ),
        (flight_root, f"{ATM}operatedBy", flight.operated_by_iri),
        (flight_root, f"{ATM}aircraftFlown", flight.aircraft_iri),
        (flight_root, f"{ATM}hasActualRoute", route.subject_iri),
        (route.subject_iri, RDF_TYPE, f"{ATM}ActualFlightRoute"),
        (route.subject_iri, f"{GEN}hasSequencedItem", point.subject_iri),
        (point.subject_iri, RDF_TYPE, f"{ATM}AircraftTrackPoint"),
        (
            point.subject_iri,
            f"{ATM}reportingTime",
            "2014-07-15T02:05:25+00:00",
        ),
        (point.subject_iri, f"{ATM}aircraftFix", fix.subject_iri),
        (fix.subject_iri, f"{ATM}locatedInSector", sector.subject_iri),
        (sector.subject_iri, RDF_TYPE, f"{NAS}Sector"),
    }
    assert len(compilation.facts) == len(compilation.fact_traces)
    traces = {trace.fact_id: trace for trace in compilation.fact_traces}
    assert all(
        fact.evidence_texts == [traces[fact.fact_id].evidence_text]
        for fact in compilation.facts
    )
    assert {fact.validation_profile.layer for fact in compilation.facts} == {
        "flight_operation",
        "trajectory",
        "aeronautical_reference",
    }
    assert all(
        fact.predicate_iri
        not in {
            "urn:aviation-agentic-ai:affectedBy",
            "urn:aviation-agentic-ai:causedBy",
            "urn:aviation-agentic-ai:motivatedBy",
        }
        for fact in compilation.facts
    )
    assert all(
        fact.object_value != "urn:test:aircraft-model:A319"
        for fact in compilation.facts
    )
    assert (
        fix.subject_iri,
        RDF_TYPE,
        f"{ATM}NavigationFix",
    ) not in _semantic_rows(compilation)


def test_compiler_rejects_normalized_value_without_exact_source_triple() -> None:
    """Removing exact source evidence must block publication of that value."""

    flight, route, point, fix, sector = _source_records()
    altered = replace(flight, call_sign="DAL999")

    with pytest.raises(ValueError, match="exact source triple"):
        compile_nasa_flight_airspace_facts(
            flights=(altered,),
            routes=(route,),
            track_points=(point,),
            navigation_fixes=(fix,),
            sectors=(sector,),
            profile_registry=_registry(),
        )


def test_referenced_sector_without_explicit_type_does_not_block_flight() -> None:
    """A relation-only sector reference must not invent or require its type."""

    flight, route, point, fix, sector = _source_records()
    referenced_sector = replace(
        sector,
        source=fix.source,
    )
    registry = _registry()

    compilation = compile_nasa_flight_airspace_facts(
        flights=(flight,),
        routes=(route,),
        track_points=(point,),
        navigation_fixes=(fix,),
        sectors=(referenced_sector,),
        profile_registry=registry,
    )
    publication = run_nasa_flight_airspace_publication_kernel(
        compilation=compilation,
        profile_registry=registry,
        source_snapshot=_snapshots((flight, route, point, fix)),
    )

    assert len(publication.accepted) == 14
    assert (
        fix.subject_iri,
        f"{ATM}locatedInSector",
        sector.subject_iri,
    ) in _semantic_rows(compilation)
    assert (
        sector.subject_iri,
        RDF_TYPE,
        f"{NAS}Sector",
    ) not in _semantic_rows(compilation)


def test_publication_kernel_rejects_non_nasa_source_family() -> None:
    """Changing the bound source family must be rejected by profile policy."""

    flight, route, point, fix, sector = _source_records()
    records = (flight, route, point, fix, sector)
    registry = _registry()
    compilation = compile_nasa_flight_airspace_facts(
        flights=(flight,),
        routes=(route,),
        track_points=(point,),
        navigation_fixes=(fix,),
        sectors=(sector,),
        profile_registry=registry,
    )

    with pytest.raises(FormalPublicationBlocked, match="source family"):
        run_nasa_flight_airspace_publication_kernel(
            compilation=compilation,
            profile_registry=registry,
            source_snapshot=_snapshots(records, SourceFamily.BTS_FLIGHT_OPERATION),
        )
