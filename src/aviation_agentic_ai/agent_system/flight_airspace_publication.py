"""Source-qualified ATMONTO Flight and Airspace fact compilation.

The compiler preserves the source's ATMONTO instance IRIs, except that a
caller may bind a NASA Flight IRI to the source-qualified internal Flight root
used by the evidence store.  It emits only reviewed ATMONTO relations that are
present in the canonical source triples.  High-frequency measurements and
derived associations remain in their structured tables.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Mapping

from rdflib import Literal, URIRef
from rdflib.util import from_n3

from aviation_agentic_ai.agent_system.airspace_sources import (
    NASAActualRouteSourceRecord,
    NASAFlightSourceRecord,
    NASANavigationFixSourceRecord,
    NASARDFSourceTrace,
    NASASectorSourceRecord,
    NASATrackPointSourceRecord,
)
from aviation_agentic_ai.agent_system.contracts import (
    FactTraceRow,
    SourceSnapshotRegistry,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.materialize import (
    FormalPublication,
    run_formal_publication_kernel,
)
from aviation_agentic_ai.agent_system.validation_profiles import (
    LoadedValidationProfile,
    ValidationProfileRegistry,
)
from aviation_agentic_ai.utils.identifiers import stable_id


RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
XSD_DATETIME = "http://www.w3.org/2001/XMLSchema#dateTime"
XSD_STRING = "http://www.w3.org/2001/XMLSchema#string"
ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
NAS = "https://data.nasa.gov/ontologies/atmonto/NAS#"
EQP = "https://data.nasa.gov/ontologies/atmonto/equipment#"
GEN = "https://data.nasa.gov/ontologies/atmonto/general#"

FLIGHT = f"{ATM}Flight"
ACTUAL_ROUTE = f"{ATM}ActualFlightRoute"
TRACK_POINT = f"{ATM}AircraftTrackPoint"
NAVIGATION_FIX = f"{ATM}NavigationFix"
AIRPORT = f"{NAS}Airport"
SECTOR = f"{NAS}Sector"
AIR_CARRIER = f"{NAS}AirCarrier"
AIRCRAFT = f"{EQP}Aircraft"


@dataclass(frozen=True, slots=True)
class FlightAirspaceFactCompilation:
    """Source-bound proposals ready for the Formal Publication Kernel."""

    facts: tuple[ValidatedFact, ...]
    fact_traces: tuple[FactTraceRow, ...]


@dataclass(frozen=True, slots=True)
class _Candidate:
    fact: ValidatedFact
    trace: FactTraceRow


def _profile_for_layer(
    registry: ValidationProfileRegistry,
    layer: str,
) -> LoadedValidationProfile:
    matches = [profile for profile in registry.profiles if profile.ref.layer == layer]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one {layer} validation profile")
    return matches[0]


def _literal_matches(actual: Literal, expected: object) -> bool:
    value = actual.toPython()
    if isinstance(expected, datetime):
        if not isinstance(value, datetime):
            return False
        if value.tzinfo is None or value.utcoffset() is None:
            value = value.replace(tzinfo=UTC)
        expected_value = expected
        if expected_value.tzinfo is None or expected_value.utcoffset() is None:
            expected_value = expected_value.replace(tzinfo=UTC)
        return value.astimezone(UTC) == expected_value.astimezone(UTC)
    return str(value) == str(expected)


def _find_source_triple(
    trace: NASARDFSourceTrace,
    *,
    subject_iri: str,
    predicate_iri: str,
    object_iri: str | None = None,
    literal_value: object | None = None,
) -> str:
    prefix = f"{URIRef(subject_iri).n3()} {URIRef(predicate_iri).n3()} "
    matches: list[str] = []
    for line in trace.canonical_triples:
        if not line.startswith(prefix) or not line.endswith(" ."):
            continue
        object_ = from_n3(line[len(prefix) : -2])
        if object_iri is not None:
            if isinstance(object_, URIRef) and str(object_) == object_iri:
                matches.append(line)
        elif literal_value is not None:
            if isinstance(object_, Literal) and _literal_matches(object_, literal_value):
                matches.append(line)
        else:
            matches.append(line)
    if len(matches) != 1:
        raise ValueError(
            "expected exactly one exact source triple for "
            f"{subject_iri} {predicate_iri}"
        )
    return matches[0]


def _has_source_iri_triple(
    trace: NASARDFSourceTrace,
    *,
    subject_iri: str,
    predicate_iri: str,
    object_iri: str,
) -> bool:
    expected = (
        f"{URIRef(subject_iri).n3()} {URIRef(predicate_iri).n3()} "
        f"{URIRef(object_iri).n3()} ."
    )
    return expected in trace.canonical_triples


def _candidate(
    *,
    trace: NASARDFSourceTrace,
    source_subject_iri: str,
    fact_subject_iri: str,
    subject_class_iri: str,
    predicate_iri: str,
    object_kind: str,
    object_value: str,
    profile: LoadedValidationProfile,
    object_class_iri: str | None = None,
    datatype_iri: str | None = None,
    literal_source_value: object | None = None,
) -> _Candidate:
    evidence_text = _find_source_triple(
        trace,
        subject_iri=source_subject_iri,
        predicate_iri=predicate_iri,
        object_iri=object_value if object_kind == "iri" else None,
        literal_value=literal_source_value if object_kind == "literal" else None,
    )
    fact_id = stable_id(
        "fact",
        fact_subject_iri,
        predicate_iri,
        object_value,
    )
    fact = ValidatedFact(
        fact_id=fact_id,
        subject_iri=fact_subject_iri,
        subject_class_iri=subject_class_iri,
        predicate_iri=predicate_iri,
        object_kind=object_kind,
        object_value=object_value,
        object_class_iri=object_class_iri,
        datatype_iri=datatype_iri,
        source_ids=[trace.source_record_id],
        evidence_texts=[evidence_text],
        validation_profile=profile.ref,
        evidence_mode="source_text",
        evidence_ref=fact_id,
    )
    return _Candidate(
        fact=fact,
        trace=FactTraceRow(
            fact_id=fact_id,
            graph_patch_line=(
                f"{fact_subject_iri} | {predicate_iri} | {object_value}"
            ),
            source_id=trace.source_record_id,
            evidence_text=evidence_text,
            evidence_agent_role="deterministic_nasa_atmonto_compiler",
            source_snapshot_sha256=trace.record_checksum,
        ),
    )


def _iri_candidate(
    *,
    trace: NASARDFSourceTrace,
    source_subject_iri: str,
    fact_subject_iri: str,
    subject_class_iri: str,
    predicate_iri: str,
    object_iri: str,
    object_class_iri: str,
    profile: LoadedValidationProfile,
) -> _Candidate:
    return _candidate(
        trace=trace,
        source_subject_iri=source_subject_iri,
        fact_subject_iri=fact_subject_iri,
        subject_class_iri=subject_class_iri,
        predicate_iri=predicate_iri,
        object_kind="iri",
        object_value=object_iri,
        object_class_iri=object_class_iri,
        profile=profile,
    )


def _literal_candidate(
    *,
    trace: NASARDFSourceTrace,
    source_subject_iri: str,
    fact_subject_iri: str,
    subject_class_iri: str,
    predicate_iri: str,
    value: str,
    source_value: object,
    datatype_iri: str,
    profile: LoadedValidationProfile,
) -> _Candidate:
    return _candidate(
        trace=trace,
        source_subject_iri=source_subject_iri,
        fact_subject_iri=fact_subject_iri,
        subject_class_iri=subject_class_iri,
        predicate_iri=predicate_iri,
        object_kind="literal",
        object_value=value,
        datatype_iri=datatype_iri,
        literal_source_value=source_value,
        profile=profile,
    )


def _type_candidate(
    *,
    trace: NASARDFSourceTrace,
    source_subject_iri: str,
    fact_subject_iri: str,
    class_iri: str,
    profile: LoadedValidationProfile,
) -> _Candidate:
    return _iri_candidate(
        trace=trace,
        source_subject_iri=source_subject_iri,
        fact_subject_iri=fact_subject_iri,
        subject_class_iri=class_iri,
        predicate_iri=RDF_TYPE,
        object_iri=class_iri,
        object_class_iri=class_iri,
        profile=profile,
    )


def _fix_class_by_iri(
    navigation_fixes: tuple[NASANavigationFixSourceRecord, ...],
) -> dict[str, str]:
    # The checked ATMONTO catalog does not admit the bundle's LatLonFix and
    # IntersectionFix classes.  NavigationFix is used here only as the
    # reviewed range/domain class for source-explicit relations; no synthetic
    # rdf:type NavigationFix fact is emitted.
    return {record.subject_iri: NAVIGATION_FIX for record in navigation_fixes}


def compile_nasa_flight_airspace_facts(
    *,
    flights: tuple[NASAFlightSourceRecord, ...] = (),
    routes: tuple[NASAActualRouteSourceRecord, ...] = (),
    track_points: tuple[NASATrackPointSourceRecord, ...] = (),
    navigation_fixes: tuple[NASANavigationFixSourceRecord, ...] = (),
    sectors: tuple[NASASectorSourceRecord, ...] = (),
    flight_root_ids: Mapping[str, str] | None = None,
    profile_registry: ValidationProfileRegistry,
) -> FlightAirspaceFactCompilation:
    """Compile reviewed NASA instance fields into source-text facts.

    The function intentionally omits BTS reporting-carrier semantics,
    aircraft-model guesses, coordinates, speeds, sector-passage derivations,
    temporal associations, TMI applicability, and causal relations.
    """

    flight_profile = _profile_for_layer(profile_registry, "flight_operation")
    trajectory_profile = _profile_for_layer(profile_registry, "trajectory")
    reference_profile = _profile_for_layer(
        profile_registry,
        "aeronautical_reference",
    )
    roots = dict(flight_root_ids or {})
    fix_classes = _fix_class_by_iri(navigation_fixes)
    candidates: list[_Candidate] = []

    for record in flights:
        subject = roots.get(record.subject_iri, record.subject_iri)
        candidates.append(
            _type_candidate(
                trace=record.source,
                source_subject_iri=record.subject_iri,
                fact_subject_iri=subject,
                class_iri=FLIGHT,
                profile=flight_profile,
            )
        )
        if record.call_sign is not None:
            candidates.append(
                _literal_candidate(
                    trace=record.source,
                    source_subject_iri=record.subject_iri,
                    fact_subject_iri=subject,
                    subject_class_iri=FLIGHT,
                    predicate_iri=f"{ATM}callSign",
                    value=record.call_sign,
                    source_value=record.call_sign,
                    datatype_iri=XSD_STRING,
                    profile=flight_profile,
                )
            )
        for predicate, value in (
            (f"{ATM}departureAirport", record.departure_airport_iri),
            (f"{ATM}arrivalAirport", record.arrival_airport_iri),
        ):
            if value is not None:
                candidates.append(
                    _iri_candidate(
                        trace=record.source,
                        source_subject_iri=record.subject_iri,
                        fact_subject_iri=subject,
                        subject_class_iri=FLIGHT,
                        predicate_iri=predicate,
                        object_iri=value,
                        object_class_iri=AIRPORT,
                        profile=flight_profile,
                    )
                )
        if record.actual_departure_time is not None:
            candidates.append(
                _literal_candidate(
                    trace=record.source,
                    source_subject_iri=record.subject_iri,
                    fact_subject_iri=subject,
                    subject_class_iri=FLIGHT,
                    predicate_iri=f"{ATM}actualDepartureTime",
                    value=record.actual_departure_time.isoformat(),
                    source_value=record.actual_departure_time,
                    datatype_iri=XSD_DATETIME,
                    profile=flight_profile,
                )
            )
        if record.operated_by_iri is not None:
            candidates.append(
                _iri_candidate(
                    trace=record.source,
                    source_subject_iri=record.subject_iri,
                    fact_subject_iri=subject,
                    subject_class_iri=FLIGHT,
                    predicate_iri=f"{ATM}operatedBy",
                    object_iri=record.operated_by_iri,
                    object_class_iri=AIR_CARRIER,
                    profile=flight_profile,
                )
            )
        if record.aircraft_iri is not None:
            candidates.append(
                _iri_candidate(
                    trace=record.source,
                    source_subject_iri=record.subject_iri,
                    fact_subject_iri=subject,
                    subject_class_iri=FLIGHT,
                    predicate_iri=f"{ATM}aircraftFlown",
                    object_iri=record.aircraft_iri,
                    object_class_iri=AIRCRAFT,
                    profile=flight_profile,
                )
            )
        for route_iri in record.actual_route_iris:
            candidates.append(
                _iri_candidate(
                    trace=record.source,
                    source_subject_iri=record.subject_iri,
                    fact_subject_iri=subject,
                    subject_class_iri=FLIGHT,
                    predicate_iri=f"{ATM}hasActualRoute",
                    object_iri=route_iri,
                    object_class_iri=ACTUAL_ROUTE,
                    profile=flight_profile,
                )
            )

    for record in routes:
        candidates.append(
            _type_candidate(
                trace=record.source,
                source_subject_iri=record.subject_iri,
                fact_subject_iri=record.subject_iri,
                class_iri=ACTUAL_ROUTE,
                profile=trajectory_profile,
            )
        )
        for point_iri in record.track_point_iris:
            candidates.append(
                _iri_candidate(
                    trace=record.source,
                    source_subject_iri=record.subject_iri,
                    fact_subject_iri=record.subject_iri,
                    subject_class_iri=ACTUAL_ROUTE,
                    predicate_iri=f"{GEN}hasSequencedItem",
                    object_iri=point_iri,
                    object_class_iri=TRACK_POINT,
                    profile=trajectory_profile,
                )
            )

    for record in track_points:
        candidates.append(
            _type_candidate(
                trace=record.source,
                source_subject_iri=record.subject_iri,
                fact_subject_iri=record.subject_iri,
                class_iri=TRACK_POINT,
                profile=trajectory_profile,
            )
        )
        if record.reporting_time is not None:
            candidates.append(
                _literal_candidate(
                    trace=record.source,
                    source_subject_iri=record.subject_iri,
                    fact_subject_iri=record.subject_iri,
                    subject_class_iri=TRACK_POINT,
                    predicate_iri=f"{ATM}reportingTime",
                    value=record.reporting_time.isoformat(),
                    source_value=record.reporting_time,
                    datatype_iri=XSD_DATETIME,
                    profile=trajectory_profile,
                )
            )
        if record.fix_iri is not None:
            candidates.append(
                _iri_candidate(
                    trace=record.source,
                    source_subject_iri=record.subject_iri,
                    fact_subject_iri=record.subject_iri,
                    subject_class_iri=TRACK_POINT,
                    predicate_iri=f"{ATM}aircraftFix",
                    object_iri=record.fix_iri,
                    object_class_iri=fix_classes.get(
                        record.fix_iri,
                        NAVIGATION_FIX,
                    ),
                    profile=trajectory_profile,
                )
            )

    for record in navigation_fixes:
        for sector_iri in record.sector_iris:
            candidates.append(
                _iri_candidate(
                    trace=record.source,
                    source_subject_iri=record.subject_iri,
                    fact_subject_iri=record.subject_iri,
                    subject_class_iri=NAVIGATION_FIX,
                    predicate_iri=f"{ATM}locatedInSector",
                    object_iri=sector_iri,
                    object_class_iri=SECTOR,
                    profile=reference_profile,
                )
            )

    for record in sectors:
        # Some sectors enter the bounded bundle only as the object of an
        # explicit locatedInSector relation.  Keep that relation, but publish
        # the Sector type only when the record itself carries the exact type
        # triple; a reference alone is not evidence for a new formal fact.
        if not _has_source_iri_triple(
            record.source,
            subject_iri=record.subject_iri,
            predicate_iri=RDF_TYPE,
            object_iri=SECTOR,
        ):
            continue
        candidates.append(
            _type_candidate(
                trace=record.source,
                source_subject_iri=record.subject_iri,
                fact_subject_iri=record.subject_iri,
                class_iri=SECTOR,
                profile=reference_profile,
            )
        )

    by_fact_id: dict[str, _Candidate] = {}
    for candidate in candidates:
        previous = by_fact_id.get(candidate.fact.fact_id)
        if previous is None:
            by_fact_id[candidate.fact.fact_id] = candidate
            continue
        previous_semantics = previous.fact.model_dump(
            exclude={"source_ids", "evidence_texts", "evidence_ref"}
        )
        candidate_semantics = candidate.fact.model_dump(
            exclude={"source_ids", "evidence_texts", "evidence_ref"}
        )
        if previous_semantics != candidate_semantics:
            raise ValueError(
                f"conflicting source facts share identity: {candidate.fact.fact_id}"
            )
        if (
            candidate.trace.source_id,
            candidate.trace.evidence_text,
        ) < (
            previous.trace.source_id,
            previous.trace.evidence_text,
        ):
            by_fact_id[candidate.fact.fact_id] = candidate

    selected = tuple(by_fact_id[key] for key in sorted(by_fact_id))
    return FlightAirspaceFactCompilation(
        facts=tuple(candidate.fact for candidate in selected),
        fact_traces=tuple(candidate.trace for candidate in selected),
    )


def run_nasa_flight_airspace_publication_kernel(
    *,
    compilation: FlightAirspaceFactCompilation,
    profile_registry: ValidationProfileRegistry,
    source_snapshot: SourceSnapshotRegistry,
) -> FormalPublication:
    """Apply the shared write-free publication authority to one compilation."""

    return run_formal_publication_kernel(
        facts=list(compilation.facts),
        profile_registry=profile_registry,
        source_snapshot=source_snapshot,
        fact_traces=compilation.fact_traces,
    )


__all__ = [
    "FlightAirspaceFactCompilation",
    "compile_nasa_flight_airspace_facts",
    "run_nasa_flight_airspace_publication_kernel",
]
