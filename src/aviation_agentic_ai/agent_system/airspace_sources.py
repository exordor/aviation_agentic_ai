"""Streaming deterministic adapters for NASR and NASA airspace sources.

The adapters expose source-qualified records only.  They do not create formal
facts, merge identities across source families, or write to the evidence store.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import io
from pathlib import Path
from typing import Literal, TypeAlias
import zipfile

from rdflib import Graph, Literal as RDFLiteral, Namespace, RDF, URIRef
from rdflib.term import Node

from aviation_agentic_ai.authority.nasr import (
    parse_nasr_aff_line,
    parse_nasr_apt_line,
)
from aviation_agentic_ai.utils.identifiers import stable_id


ATM = Namespace("https://data.nasa.gov/ontologies/atmonto/ATM#")
GEN = Namespace("https://data.nasa.gov/ontologies/atmonto/general#")
NAS = Namespace("https://data.nasa.gov/ontologies/atmonto/NAS#")

NASA_ATMONTO_AIRSPACE_MEMBER_BASENAMES = (
    "flightInst.ttl",
    "fixInst.ttl",
    "SectorLocationInst.ttl",
)


@dataclass(frozen=True, slots=True)
class NASRSourceTrace:
    """Exact fixed-width source row and immutable archive binding."""

    source_record_id: str
    archive_checksum: str
    zip_member: str
    line_number: int
    record_locator: str
    canonical_content: str
    record_checksum: str


@dataclass(frozen=True, slots=True)
class NASRAirportSourceRecord:
    record_id: str
    source: NASRSourceTrace
    airport_code: str
    faa_code: str
    display_name: str
    city: str | None
    state: str | None
    effective_start: datetime | None


@dataclass(frozen=True, slots=True)
class NASRARTCCSourceRecord:
    record_id: str
    source: NASRSourceTrace
    artcc_code: str
    icao_code: str | None
    display_name: str
    state: str | None
    effective_start: datetime | None


@dataclass(frozen=True, slots=True)
class NASRAirportARTCCAssignmentSourceRecord:
    record_id: str
    source: NASRSourceTrace
    airport_code: str
    artcc_code: str
    assignment_role: Literal["boundary", "responsible"]
    effective_start: datetime | None


NASRAirspaceSourceRecord: TypeAlias = (
    NASRAirportSourceRecord
    | NASRARTCCSourceRecord
    | NASRAirportARTCCAssignmentSourceRecord
)


@dataclass(frozen=True, slots=True)
class NASARDFSourceTrace:
    """Canonical subject-level RDF evidence from one allowlisted ZIP member."""

    source_record_id: str
    archive_checksum: str
    zip_member: str
    record_locator: str
    subject_iri: str
    related_subject_iris: tuple[str, ...]
    canonical_triples: tuple[str, ...]
    record_checksum: str


@dataclass(frozen=True, slots=True)
class NASAFlightSourceRecord:
    source: NASARDFSourceTrace
    subject_iri: str
    call_sign: str | None
    departure_airport_iri: str | None
    arrival_airport_iri: str | None
    actual_departure_time: datetime | None
    actual_arrival_time: datetime | None
    time_basis: Literal["explicit_utc", "source_naive_interpreted_utc"] | None
    actual_route_iris: tuple[str, ...]
    operated_by_iri: str | None
    aircraft_iri: str | None
    aircraft_type_iri: str | None


@dataclass(frozen=True, slots=True)
class NASAActualRouteSourceRecord:
    source: NASARDFSourceTrace
    subject_iri: str
    flight_iris: tuple[str, ...]
    track_point_iris: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NASATrackPointSourceRecord:
    source: NASARDFSourceTrace
    subject_iri: str
    route_iris: tuple[str, ...]
    sequence_number: int | None
    reporting_time: datetime | None
    time_basis: Literal["explicit_utc", "source_naive_interpreted_utc"] | None
    ground_speed: float | None
    fix_iri: str | None
    latitude: float | None
    longitude: float | None
    altitude: float | None
    sector_iris: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NASANavigationFixSourceRecord:
    source: NASARDFSourceTrace
    subject_iri: str
    fix_identifier: str
    latitude: float | None
    longitude: float | None
    altitude: float | None
    sector_iris: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NASASectorSourceRecord:
    source: NASARDFSourceTrace
    subject_iri: str
    sector_identifier: str


NASAAirspaceSourceRecord: TypeAlias = (
    NASAFlightSourceRecord
    | NASAActualRouteSourceRecord
    | NASATrackPointSourceRecord
    | NASANavigationFixSourceRecord
    | NASASectorSourceRecord
)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _find_zip_member(archive: zipfile.ZipFile, basename: str) -> str:
    matches = [
        name
        for name in archive.namelist()
        if not name.endswith("/") and name.rsplit("/", 1)[-1] == basename
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {basename} member")
    return matches[0]


def _nasr_source_trace(
    *,
    archive_checksum: str,
    member_name: str,
    line_number: int,
    raw_line: bytes,
) -> NASRSourceTrace:
    canonical_bytes = raw_line.rstrip(b"\r\n")
    canonical_content = canonical_bytes.decode("latin-1")
    record_checksum = hashlib.sha256(canonical_bytes).hexdigest()
    record_locator = f"{member_name}:{line_number}"
    return NASRSourceTrace(
        source_record_id=stable_id(
            "nasr-source-record",
            archive_checksum,
            member_name,
            line_number,
            record_checksum,
        ),
        archive_checksum=archive_checksum,
        zip_member=member_name,
        line_number=line_number,
        record_locator=record_locator,
        canonical_content=canonical_content,
        record_checksum=record_checksum,
    )


def _code(entity: object, scheme: str) -> str | None:
    codes = getattr(entity, "codes", ())
    return next(
        (
            str(candidate.value)
            for candidate in codes
            if str(candidate.scheme).upper() == scheme.upper()
        ),
        None,
    )


def iter_nasr_airspace_records(
    path: str | Path,
) -> Iterator[NASRAirspaceSourceRecord]:
    """Stream role-preserving APT/AFF records from one pinned NASR archive."""

    archive_path = Path(path)
    archive_checksum = _file_sha256(archive_path)
    with zipfile.ZipFile(archive_path) as archive:
        apt_member = _find_zip_member(archive, "APT.txt")
        aff_member = _find_zip_member(archive, "AFF.txt")

        with archive.open(apt_member) as stream:
            for line_number, raw_line in enumerate(stream, start=1):
                trace = _nasr_source_trace(
                    archive_checksum=archive_checksum,
                    member_name=apt_member,
                    line_number=line_number,
                    raw_line=raw_line,
                )
                entity = parse_nasr_apt_line(trace.canonical_content)
                if entity is None:
                    continue
                airport_code = _code(entity, "ICAO")
                faa_code = _code(entity, "FAA")
                if airport_code is None or faa_code is None:
                    continue
                yield NASRAirportSourceRecord(
                    record_id=stable_id(
                        "nasr-airport-source", trace.source_record_id, airport_code
                    ),
                    source=trace,
                    airport_code=airport_code,
                    faa_code=faa_code,
                    display_name=entity.preferred_label,
                    city=entity.metadata.get("city"),
                    state=entity.metadata.get("state"),
                    effective_start=entity.valid_from,
                )
                for role, metadata_key in (
                    ("boundary", "boundary_artcc"),
                    ("responsible", "responsible_artcc"),
                ):
                    artcc_code = str(entity.metadata.get(metadata_key) or "").strip()
                    if not artcc_code:
                        continue
                    yield NASRAirportARTCCAssignmentSourceRecord(
                        record_id=stable_id(
                            "nasr-airport-artcc-source",
                            trace.source_record_id,
                            airport_code,
                            artcc_code,
                            role,
                        ),
                        source=trace,
                        airport_code=airport_code,
                        artcc_code=artcc_code,
                        assignment_role=role,
                        effective_start=entity.valid_from,
                    )

        with archive.open(aff_member) as stream:
            for line_number, raw_line in enumerate(stream, start=1):
                trace = _nasr_source_trace(
                    archive_checksum=archive_checksum,
                    member_name=aff_member,
                    line_number=line_number,
                    raw_line=raw_line,
                )
                entity = parse_nasr_aff_line(trace.canonical_content)
                if entity is None:
                    continue
                artcc_code = _code(entity, "FAA_ARTCC")
                if artcc_code is None:
                    continue
                yield NASRARTCCSourceRecord(
                    record_id=stable_id(
                        "nasr-artcc-source", trace.source_record_id, artcc_code
                    ),
                    source=trace,
                    artcc_code=artcc_code,
                    icao_code=_code(entity, "ICAO_ARTCC"),
                    display_name=entity.preferred_label,
                    state=entity.metadata.get("state"),
                    effective_start=entity.valid_from,
                )


def _triple_text(subject: Node, predicate: Node, object_: Node) -> str:
    return f"{subject.n3()} {predicate.n3()} {object_.n3()} ."


def _canonical_triples(triples: set[tuple[Node, Node, Node]]) -> tuple[str, ...]:
    return tuple(sorted(_triple_text(*triple) for triple in triples))


def _rdf_trace(
    *,
    archive_checksum: str,
    member_name: str,
    subject: URIRef,
    graph: Graph,
    related_subjects: tuple[URIRef, ...] = (),
    relation_triples: tuple[tuple[Node, Node, Node], ...] = (),
) -> NASARDFSourceTrace:
    triples = set(graph.triples((subject, None, None)))
    for related_subject in related_subjects:
        triples.update(graph.triples((related_subject, None, None)))
    triples.update(relation_triples)
    canonical = _canonical_triples(triples)
    record_checksum = hashlib.sha256("\n".join(canonical).encode("utf-8")).hexdigest()
    subject_iri = str(subject)
    return NASARDFSourceTrace(
        source_record_id=stable_id(
            "nasa-atmonto-source-record",
            archive_checksum,
            member_name,
            subject_iri,
            record_checksum,
        ),
        archive_checksum=archive_checksum,
        zip_member=member_name,
        record_locator=f"{member_name}#{subject_iri}",
        subject_iri=subject_iri,
        related_subject_iris=tuple(str(value) for value in related_subjects),
        canonical_triples=canonical,
        record_checksum=record_checksum,
    )


def _first_uri(graph: Graph, subject: URIRef, predicate: URIRef) -> str | None:
    return next(
        (str(value) for value in graph.objects(subject, predicate) if isinstance(value, URIRef)),
        None,
    )


def _uri_values(graph: Graph, subject: URIRef, predicate: URIRef) -> tuple[str, ...]:
    return tuple(
        sorted(
            str(value)
            for value in graph.objects(subject, predicate)
            if isinstance(value, URIRef)
        )
    )


def _literal_value(graph: Graph, subject: URIRef, predicate: URIRef) -> object | None:
    return next(
        (
            value.toPython()
            for value in graph.objects(subject, predicate)
            if isinstance(value, RDFLiteral)
        ),
        None,
    )


def _text_value(graph: Graph, subject: URIRef, predicate: URIRef) -> str | None:
    value = _literal_value(graph, subject, predicate)
    return None if value is None else str(value)


def _float_value(graph: Graph, subject: URIRef, predicate: URIRef) -> float | None:
    value = _literal_value(graph, subject, predicate)
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def _int_value(graph: Graph, subject: URIRef, predicate: URIRef) -> int | None:
    value = _literal_value(graph, subject, predicate)
    try:
        return None if value is None else int(value)
    except (TypeError, ValueError):
        return None


def _datetime_value(
    graph: Graph,
    subject: URIRef,
    predicate: URIRef,
) -> tuple[
    datetime | None,
    Literal["explicit_utc", "source_naive_interpreted_utc"] | None,
]:
    value = _literal_value(graph, subject, predicate)
    if not isinstance(value, datetime):
        return None, None
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=UTC), "source_naive_interpreted_utc"
    return value.astimezone(UTC), "explicit_utc"


def _subject_fragment(subject: URIRef) -> str:
    value = str(subject)
    if "#" in value:
        return value.rsplit("#", 1)[-1]
    return value.rstrip("/").rsplit("/", 1)[-1]


def _parse_turtle_member(archive: zipfile.ZipFile, member_name: str) -> Graph:
    with archive.open(member_name) as raw_stream:
        stream = io.TextIOWrapper(raw_stream, encoding="utf-8")
        graph = Graph()
        graph.parse(data=stream.read(), format="turtle")
    return graph


def _iter_flight_member_records(
    graph: Graph,
    *,
    archive_checksum: str,
    member_name: str,
) -> Iterator[NASAAirspaceSourceRecord]:
    flights = tuple(sorted(set(graph.subjects(RDF.type, ATM.Flight)), key=str))
    for subject in flights:
        if not isinstance(subject, URIRef):
            continue
        departure_time, departure_basis = _datetime_value(
            graph, subject, ATM.actualDepartureTime
        )
        arrival_time, arrival_basis = _datetime_value(
            graph, subject, ATM.actualArrivalTime
        )
        time_basis = departure_basis or arrival_basis
        yield NASAFlightSourceRecord(
            source=_rdf_trace(
                archive_checksum=archive_checksum,
                member_name=member_name,
                subject=subject,
                graph=graph,
            ),
            subject_iri=str(subject),
            call_sign=_text_value(graph, subject, ATM.callSign),
            departure_airport_iri=_first_uri(graph, subject, ATM.departureAirport),
            arrival_airport_iri=_first_uri(graph, subject, ATM.arrivalAirport),
            actual_departure_time=departure_time,
            actual_arrival_time=arrival_time,
            time_basis=time_basis,
            actual_route_iris=_uri_values(graph, subject, ATM.hasActualRoute),
            operated_by_iri=_first_uri(graph, subject, ATM.operatedBy),
            aircraft_iri=_first_uri(graph, subject, ATM.aircraftFlown),
            aircraft_type_iri=_first_uri(graph, subject, ATM.aircraftTypeFlown),
        )

    routes = tuple(
        sorted(set(graph.subjects(RDF.type, ATM.ActualFlightRoute)), key=str)
    )
    point_routes: dict[URIRef, set[URIRef]] = {}
    for route in routes:
        if not isinstance(route, URIRef):
            continue
        flight_links = tuple(graph.triples((None, ATM.hasActualRoute, route)))
        point_nodes = {
            value
            for value in graph.objects(route, GEN.hasSequencedItem)
            if isinstance(value, URIRef)
        }
        for point in point_nodes:
            point_routes.setdefault(point, set()).add(route)
        ordered_points = tuple(
            str(point)
            for point in sorted(
                point_nodes,
                key=lambda value: (
                    _int_value(graph, value, GEN.sequenceNumber) is None,
                    _int_value(graph, value, GEN.sequenceNumber) or 0,
                    str(value),
                ),
            )
        )
        yield NASAActualRouteSourceRecord(
            source=_rdf_trace(
                archive_checksum=archive_checksum,
                member_name=member_name,
                subject=route,
                graph=graph,
                relation_triples=flight_links,
            ),
            subject_iri=str(route),
            flight_iris=tuple(
                sorted(
                    str(flight)
                    for flight, _, _ in flight_links
                    if isinstance(flight, URIRef)
                )
            ),
            track_point_iris=ordered_points,
        )

    points = tuple(
        sorted(
            set(graph.subjects(RDF.type, ATM.AircraftTrackPoint)),
            key=lambda value: (
                min((str(route) for route in point_routes.get(value, set())), default=""),
                _int_value(graph, value, GEN.sequenceNumber) is None,
                _int_value(graph, value, GEN.sequenceNumber) or 0,
                str(value),
            ),
        )
    )
    embedded_fixes: set[URIRef] = set()
    for subject in points:
        if not isinstance(subject, URIRef):
            continue
        fix = next(
            (
                value
                for value in graph.objects(subject, ATM.aircraftFix)
                if isinstance(value, URIRef)
            ),
            None,
        )
        related = () if fix is None else (fix,)
        if fix is not None:
            embedded_fixes.add(fix)
        route_links = tuple(
            graph.triples((route, GEN.hasSequencedItem, subject))
            for route in sorted(point_routes.get(subject, set()), key=str)
        )
        flattened_route_links = tuple(item for group in route_links for item in group)
        reporting_time, time_basis = _datetime_value(graph, subject, ATM.reportingTime)
        sector_values = set(_uri_values(graph, subject, ATM.locatedInSector))
        if fix is not None:
            sector_values.update(_uri_values(graph, fix, ATM.locatedInSector))
        coordinate_subject = subject if fix is None else fix
        yield NASATrackPointSourceRecord(
            source=_rdf_trace(
                archive_checksum=archive_checksum,
                member_name=member_name,
                subject=subject,
                graph=graph,
                related_subjects=related,
                relation_triples=flattened_route_links,
            ),
            subject_iri=str(subject),
            route_iris=tuple(
                sorted(str(route) for route in point_routes.get(subject, set()))
            ),
            sequence_number=_int_value(graph, subject, GEN.sequenceNumber),
            reporting_time=reporting_time,
            time_basis=time_basis,
            ground_speed=_float_value(graph, subject, ATM.groundSpeed),
            fix_iri=None if fix is None else str(fix),
            latitude=_float_value(graph, coordinate_subject, GEN.latitude),
            longitude=_float_value(graph, coordinate_subject, GEN.longitude),
            altitude=_float_value(graph, coordinate_subject, GEN.altitude),
            sector_iris=tuple(sorted(sector_values)),
        )

    yield from _iter_fix_records(
        graph,
        subjects=embedded_fixes,
        archive_checksum=archive_checksum,
        member_name=member_name,
    )


def _iter_fix_records(
    graph: Graph,
    *,
    subjects: set[URIRef] | None,
    archive_checksum: str,
    member_name: str,
) -> Iterator[NASANavigationFixSourceRecord]:
    if subjects is None:
        candidates = {
            subject
            for predicate in (ATM.fixId, ATM.locatedInSector, GEN.latitude, GEN.longitude)
            for subject in graph.subjects(predicate, None)
            if isinstance(subject, URIRef)
        }
    else:
        candidates = subjects
    for subject in sorted(candidates, key=str):
        yield NASANavigationFixSourceRecord(
            source=_rdf_trace(
                archive_checksum=archive_checksum,
                member_name=member_name,
                subject=subject,
                graph=graph,
            ),
            subject_iri=str(subject),
            fix_identifier=_text_value(graph, subject, ATM.fixId)
            or _subject_fragment(subject),
            latitude=_float_value(graph, subject, GEN.latitude),
            longitude=_float_value(graph, subject, GEN.longitude),
            altitude=_float_value(graph, subject, GEN.altitude),
            sector_iris=_uri_values(graph, subject, ATM.locatedInSector),
        )


def _iter_sector_records(
    graph: Graph,
    *,
    archive_checksum: str,
    member_name: str,
) -> Iterator[NASASectorSourceRecord]:
    subjects = tuple(sorted(set(graph.subjects(RDF.type, NAS.Sector)), key=str))
    for subject in subjects:
        if not isinstance(subject, URIRef):
            continue
        yield NASASectorSourceRecord(
            source=_rdf_trace(
                archive_checksum=archive_checksum,
                member_name=member_name,
                subject=subject,
                graph=graph,
            ),
            subject_iri=str(subject),
            sector_identifier=_subject_fragment(subject),
        )


def iter_nasa_atmonto_airspace_records(
    path: str | Path,
    *,
    include_global_fixes: bool = True,
) -> Iterator[NASAAirspaceSourceRecord]:
    """Stream typed records from the three reviewed atmontoPlus members.

    Each member is parsed and discarded independently.  No aggregate 138 MB
    graph is constructed, and non-allowlisted members are never parsed.
    """

    archive_path = Path(path)
    archive_checksum = _file_sha256(archive_path)
    with zipfile.ZipFile(archive_path) as archive:
        members = {
            basename: _find_zip_member(archive, basename)
            for basename in NASA_ATMONTO_AIRSPACE_MEMBER_BASENAMES
        }
        flight_member = members["flightInst.ttl"]
        flight_graph = _parse_turtle_member(archive, flight_member)
        flight_records = tuple(
            _iter_flight_member_records(
                flight_graph,
                archive_checksum=archive_checksum,
                member_name=flight_member,
            )
        )
        del flight_graph
        yield from flight_records

        referenced_fixes = {
            URIRef(record.fix_iri)
            for record in flight_records
            if isinstance(record, NASATrackPointSourceRecord)
            and record.fix_iri is not None
        }
        fix_member = members["fixInst.ttl"]
        fix_graph = _parse_turtle_member(archive, fix_member)
        yield from _iter_fix_records(
            fix_graph,
            subjects=None if include_global_fixes else referenced_fixes,
            archive_checksum=archive_checksum,
            member_name=fix_member,
        )
        del fix_graph

        sector_member = members["SectorLocationInst.ttl"]
        sector_graph = _parse_turtle_member(archive, sector_member)
        yield from _iter_sector_records(
            sector_graph,
            archive_checksum=archive_checksum,
            member_name=sector_member,
        )


__all__ = [
    "NASAActualRouteSourceRecord",
    "NASAAirspaceSourceRecord",
    "NASAFlightSourceRecord",
    "NASANavigationFixSourceRecord",
    "NASARDFSourceTrace",
    "NASASectorSourceRecord",
    "NASATrackPointSourceRecord",
    "NASRAirportARTCCAssignmentSourceRecord",
    "NASRAirportSourceRecord",
    "NASRAirspaceSourceRecord",
    "NASRARTCCSourceRecord",
    "NASRSourceTrace",
    "iter_nasa_atmonto_airspace_records",
    "iter_nasr_airspace_records",
]
