"""Deterministic adapters for the public NASA atmontoPlus sample layers.

Each allowlisted Turtle member is parsed independently.  The adapter emits
source-qualified records for a caller-selected date and airport set; it does
not load the aggregate ontology graph or infer missing source values.
"""

from __future__ import annotations

from collections.abc import Iterator, Set
from dataclasses import dataclass
from datetime import UTC, date, datetime
import hashlib
from pathlib import Path
from typing import Literal, TypeAlias
import zipfile

from rdflib import Graph, Literal as RDFLiteral, Namespace, RDF, RDFS, URIRef
from rdflib.term import Node

from aviation_agentic_ai.utils.identifiers import stable_id


ATM = Namespace("https://data.nasa.gov/ontologies/atmonto/ATM#")
DATA = Namespace("https://data.nasa.gov/ontologies/atmonto/data#")
NAS = Namespace("https://data.nasa.gov/ontologies/atmonto/NAS#")

ATMONTO_PUBLIC_SAMPLE_DATE = date(2014, 7, 15)
ATMONTO_PUBLIC_SAMPLE_AIRPORT_CODES = frozenset({"KJFK", "KEWR", "KLGA"})
ATMONTO_PUBLIC_SAMPLE_MEMBER_BASENAMES = (
    "METARinst.ttl",
    "TAFinst.ttl",
    "ASPMinst.ttl",
    "TMIinst.ttl",
)

TMIType = Literal["GroundDelayProgramTMI", "GroundStopTMI", "ReRouteTMI"]


@dataclass(frozen=True, slots=True)
class ATMONTHOSourceTrace:
    """Immutable subject-level trace into one Turtle member."""

    source_record_id: str
    archive_checksum: str
    zip_member: str
    record_locator: str
    subject_iri: str
    canonical_subject_triples: tuple[str, ...]
    association_triples: tuple[str, ...]
    record_checksum: str


@dataclass(frozen=True, slots=True)
class ATMONTHistoricalWeatherSourceRecord:
    source: ATMONTHOSourceTrace
    subject_iri: str
    airport_iri: str
    observed_at: datetime
    interval_end: datetime | None
    report_text: str | None


@dataclass(frozen=True, slots=True)
class ATMONTOTAFSourceRecord:
    source: ATMONTHOSourceTrace
    subject_iri: str
    airport_iri: str
    issued_at: datetime
    valid_from: datetime | None
    valid_to: datetime | None
    report_text: str | None


@dataclass(frozen=True, slots=True)
class ATMONTOAirportDataSourceRecord:
    source: ATMONTHOSourceTrace
    subject_iri: str
    airport_iri: str
    interval_start: datetime
    interval_end: datetime | None
    metrics: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class ATMONTOTMISourceRecord:
    source: ATMONTHOSourceTrace
    subject_iri: str
    tmi_type: TMIType
    controlled_element_iri: str | None
    airport_iri: str | None
    reason: str | None
    issued_at: datetime
    effective_from: datetime | None
    effective_to: datetime | None


ATMONTHOPublicSampleSourceRecord: TypeAlias = (
    ATMONTHistoricalWeatherSourceRecord
    | ATMONTOTAFSourceRecord
    | ATMONTOAirportDataSourceRecord
    | ATMONTOTMISourceRecord
)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _find_member(archive: zipfile.ZipFile, basename: str) -> str:
    matches = [
        name
        for name in archive.namelist()
        if not name.endswith("/") and name.rsplit("/", 1)[-1] == basename
    ]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {basename} member")
    return matches[0]


def _triple_text(subject: Node, predicate: Node, object_: Node) -> str:
    return f"{subject.n3()} {predicate.n3()} {object_.n3()} ."


def _canonical_triples(
    triples: Iterator[tuple[Node, Node, Node]],
) -> tuple[str, ...]:
    return tuple(sorted(_triple_text(*triple) for triple in triples))


def _source_trace(
    *,
    archive_checksum: str,
    member_name: str,
    graph: Graph,
    subject: URIRef,
    association_triples: tuple[tuple[Node, Node, Node], ...] = (),
) -> ATMONTHOSourceTrace:
    canonical = _canonical_triples(graph.triples((subject, None, None)))
    associations = _canonical_triples(iter(association_triples))
    record_checksum = hashlib.sha256("\n".join(canonical).encode("utf-8")).hexdigest()
    subject_iri = str(subject)
    return ATMONTHOSourceTrace(
        source_record_id=stable_id(
            "nasa-atmonto-public-sample-source",
            archive_checksum,
            member_name,
            subject_iri,
            record_checksum,
        ),
        archive_checksum=archive_checksum,
        zip_member=member_name,
        record_locator=f"{member_name}#{subject_iri}",
        subject_iri=subject_iri,
        canonical_subject_triples=canonical,
        association_triples=associations,
        record_checksum=record_checksum,
    )


def _datetime_value(graph: Graph, subject: URIRef, predicate: URIRef) -> datetime | None:
    value = graph.value(subject, predicate)
    if not isinstance(value, RDFLiteral):
        return None
    parsed = value.toPython()
    if not isinstance(parsed, datetime):
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _text_value(graph: Graph, subject: URIRef, predicate: URIRef) -> str | None:
    value = graph.value(subject, predicate)
    return str(value) if isinstance(value, RDFLiteral) else None


def _iri_value(graph: Graph, subject: URIRef, predicate: URIRef) -> URIRef | None:
    value = graph.value(subject, predicate)
    return value if isinstance(value, URIRef) else None


def _airport_iris(airport_codes: Set[str]) -> frozenset[str]:
    normalized = {
        code.strip().upper() for code in airport_codes if code.strip()
    }
    return frozenset(str(NAS[f"{code}airport"]) for code in normalized)


def _iter_metar(
    graph: Graph,
    *,
    archive_checksum: str,
    member_name: str,
    sample_date: date,
    allowed_airports: frozenset[str],
) -> Iterator[ATMONTHistoricalWeatherSourceRecord]:
    for subject in sorted(graph.subjects(RDF.type, DATA.METARreport), key=str):
        if not isinstance(subject, URIRef):
            continue
        observed_at = _datetime_value(graph, subject, DATA.dataIntervalStartTime)
        airport = _iri_value(graph, subject, DATA.associatedMETARreportingStation)
        if (
            observed_at is None
            or observed_at.date() != sample_date
            or airport is None
            or str(airport) not in allowed_airports
        ):
            continue
        yield ATMONTHistoricalWeatherSourceRecord(
            source=_source_trace(
                archive_checksum=archive_checksum,
                member_name=member_name,
                graph=graph,
                subject=subject,
            ),
            subject_iri=str(subject),
            airport_iri=str(airport),
            observed_at=observed_at,
            interval_end=_datetime_value(graph, subject, DATA.dataIntervalEndTime),
            report_text=_text_value(graph, subject, DATA.metarReportString),
        )


def _iter_taf(
    graph: Graph,
    *,
    archive_checksum: str,
    member_name: str,
    sample_date: date,
    allowed_airports: frozenset[str],
) -> Iterator[ATMONTOTAFSourceRecord]:
    for subject in sorted(graph.subjects(RDF.type, DATA.TAFreport), key=str):
        if not isinstance(subject, URIRef):
            continue
        issued_at = _datetime_value(graph, subject, DATA.forecastIssueTime)
        airport = _iri_value(graph, subject, DATA.forecastingAirport)
        if (
            issued_at is None
            or issued_at.date() != sample_date
            or airport is None
            or str(airport) not in allowed_airports
        ):
            continue
        yield ATMONTOTAFSourceRecord(
            source=_source_trace(
                archive_checksum=archive_checksum,
                member_name=member_name,
                graph=graph,
                subject=subject,
            ),
            subject_iri=str(subject),
            airport_iri=str(airport),
            issued_at=issued_at,
            valid_from=_datetime_value(graph, subject, DATA.dataIntervalStartTime),
            valid_to=_datetime_value(graph, subject, DATA.dataIntervalEndTime),
            report_text=_text_value(graph, subject, DATA.tafReportString),
        )


_AIRPORT_DATA_NON_METRIC_PREDICATES = frozenset(
    {
        RDF.type,
        RDFS.label,
        DATA.dataIntervalStartTime,
        DATA.dataIntervalEndTime,
    }
)


def _airport_data_metrics(
    graph: Graph,
    subject: URIRef,
) -> tuple[tuple[str, str], ...]:
    return tuple(
        sorted(
            (str(predicate), str(value))
            for predicate, value in graph.predicate_objects(subject)
            if isinstance(value, RDFLiteral)
            and predicate not in _AIRPORT_DATA_NON_METRIC_PREDICATES
        )
    )


def _iter_airport_data(
    graph: Graph,
    *,
    archive_checksum: str,
    member_name: str,
    sample_date: date,
    allowed_airports: frozenset[str],
) -> Iterator[ATMONTOAirportDataSourceRecord]:
    for subject in sorted(graph.subjects(RDF.type, DATA.AirportData), key=str):
        if not isinstance(subject, URIRef):
            continue
        interval_start = _datetime_value(graph, subject, DATA.dataIntervalStartTime)
        airport_candidates = sorted(
            {
                airport
                for airport in graph.subjects(DATA.hasAirportData, subject)
                if isinstance(airport, URIRef) and str(airport) in allowed_airports
            },
            key=str,
        )
        if (
            interval_start is None
            or interval_start.date() != sample_date
            or len(airport_candidates) != 1
        ):
            continue
        airport = airport_candidates[0]
        association = (airport, DATA.hasAirportData, subject)
        yield ATMONTOAirportDataSourceRecord(
            source=_source_trace(
                archive_checksum=archive_checksum,
                member_name=member_name,
                graph=graph,
                subject=subject,
                association_triples=(association,),
            ),
            subject_iri=str(subject),
            airport_iri=str(airport),
            interval_start=interval_start,
            interval_end=_datetime_value(graph, subject, DATA.dataIntervalEndTime),
            metrics=_airport_data_metrics(graph, subject),
        )


_TMI_CLASSES: tuple[tuple[URIRef, TMIType, URIRef], ...] = (
    (ATM.GroundDelayProgramTMI, "GroundDelayProgramTMI", ATM.impactingCondition),
    (ATM.GroundStopTMI, "GroundStopTMI", ATM.impactingCondition),
    (ATM.ReRouteTMI, "ReRouteTMI", ATM.reRouteReason),
)


def _iter_tmis(
    graph: Graph,
    *,
    archive_checksum: str,
    member_name: str,
    sample_date: date,
) -> Iterator[ATMONTOTMISourceRecord]:
    for class_iri, tmi_type, reason_predicate in _TMI_CLASSES:
        for subject in sorted(graph.subjects(RDF.type, class_iri), key=str):
            if not isinstance(subject, URIRef):
                continue
            issued_at = _datetime_value(graph, subject, ATM.issuedTime)
            if issued_at is None or issued_at.date() != sample_date:
                continue
            controlled = _iri_value(graph, subject, ATM.controlledNASelement)
            controlled_text = str(controlled) if controlled is not None else None
            airport_iri = (
                controlled_text
                if controlled_text is not None and controlled_text.endswith("airport")
                else None
            )
            yield ATMONTOTMISourceRecord(
                source=_source_trace(
                    archive_checksum=archive_checksum,
                    member_name=member_name,
                    graph=graph,
                    subject=subject,
                ),
                subject_iri=str(subject),
                tmi_type=tmi_type,
                controlled_element_iri=controlled_text,
                airport_iri=airport_iri,
                reason=_text_value(graph, subject, reason_predicate),
                issued_at=issued_at,
                effective_from=_datetime_value(graph, subject, ATM.effectiveStartTime),
                effective_to=_datetime_value(graph, subject, ATM.effectiveEndTime),
            )


def iter_atmonto_public_sample_records(
    path: str | Path,
    *,
    sample_date: date = ATMONTO_PUBLIC_SAMPLE_DATE,
    airport_codes: Set[str] = ATMONTO_PUBLIC_SAMPLE_AIRPORT_CODES,
) -> Iterator[ATMONTHOPublicSampleSourceRecord]:
    """Yield the selected public atmontoPlus records from four source members."""

    archive_path = Path(path)
    archive_checksum = _file_sha256(archive_path)
    allowed_airports = _airport_iris(airport_codes)
    with zipfile.ZipFile(archive_path) as archive:
        for basename in ATMONTO_PUBLIC_SAMPLE_MEMBER_BASENAMES:
            member_name = _find_member(archive, basename)
            graph = Graph()
            graph.parse(data=archive.read(member_name), format="turtle")
            if basename == "METARinst.ttl":
                yield from _iter_metar(
                    graph,
                    archive_checksum=archive_checksum,
                    member_name=member_name,
                    sample_date=sample_date,
                    allowed_airports=allowed_airports,
                )
            elif basename == "TAFinst.ttl":
                yield from _iter_taf(
                    graph,
                    archive_checksum=archive_checksum,
                    member_name=member_name,
                    sample_date=sample_date,
                    allowed_airports=allowed_airports,
                )
            elif basename == "ASPMinst.ttl":
                yield from _iter_airport_data(
                    graph,
                    archive_checksum=archive_checksum,
                    member_name=member_name,
                    sample_date=sample_date,
                    allowed_airports=allowed_airports,
                )
            else:
                yield from _iter_tmis(
                    graph,
                    archive_checksum=archive_checksum,
                    member_name=member_name,
                    sample_date=sample_date,
                )

