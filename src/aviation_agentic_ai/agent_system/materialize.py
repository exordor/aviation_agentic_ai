"""Profile-owned ValidatedFact materialization.

The deterministic publisher accepts only facts owned by an exact validation
profile and bound to the run's canonical multi-source snapshot registry. It
writes the JSONL, RDF/Turtle, and Neo4j projections consumed by current runs.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.contracts import (
    FactTraceRow,
    ObservationFactTrace,
    ReconstructionTrace,
    SourceSnapshotRegistry,
    ValidatedFact,
    ValidationProfileRef,
    WeatherFactTrace,
)
from aviation_agentic_ai.agent_system.validation_profiles import (
    LoadedValidationProfile,
    ValidationProfileRegistry,
    validate_fact_for_publication,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id

# Predicate that asserts an entity's ontology class.
RDF_TYPE = "rdf:type"
QUDT_NUMERIC_VALUE = "http://qudt.org/schema/qudt/numericValue"
XSD_INTEGER = "http://www.w3.org/2001/XMLSchema#integer"
XSD_DECIMAL = "http://www.w3.org/2001/XMLSchema#decimal"

_COUNT_METRIC_KEYS = frozenset(
    {
        "scheduled_arrival_count",
        "completed_arrival_count",
        "cancelled_count",
        "diverted_count",
        "arrival_delay_15_count",
    }
)
_MINUTE_METRIC_KEYS = frozenset(
    {
        "mean_arrival_delay_minutes",
        "median_arrival_delay_minutes",
        "carrier_reported_weather_delay_minutes",
        "carrier_reported_nas_delay_minutes",
    }
)


# ===========================================================================
# ValidatedFact -> RDF + Neo4j projection (plan §6)
# ===========================================================================
#
# The functions below consume the Formal Publication Kernel's accepted
# ``ValidatedFact`` objects (plan §4.1) and emit the formal artifacts:
#
# - ``kg.jsonl``  — one fact row in the Query Agent's triple-row shape;
# - ``kg.ttl``    — real ATMONTO/RDF/PROV/XSD Turtle, parsed by rdflib;
# - ``neo4j_nodes.jsonl`` / ``neo4j_relationships.jsonl`` — the Neo4j
#   projection (AviationEvent / Facility / SourceRecord nodes;
#   CONTROLLED_NAS_ELEMENT / DERIVED_FROM relationships; datatype properties
#   on the event node; never Literal nodes).
#
# The writer must NOT construct ``example.org/...#atm:*`` IRIs (plan §6.1).

# Standard IRIs reused across facts (plan §6.1).
_RDF_TYPE_IRI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
_PROV_WAS_DERIVED_FROM_IRI = "http://www.w3.org/ns/prov#wasDerivedFrom"
_PROV_NAMESPACE = "http://www.w3.org/ns/prov#"
_RDF_NAMESPACE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
_XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema#"
_DATA_NAMESPACE = "https://data.nasa.gov/ontologies/atmonto/data#"
_METEOROLOGICAL_REPORT_IRI = f"{_DATA_NAMESPACE}MeteorologicalReport"
_FORECASTING_AIRPORT_IRI = f"{_DATA_NAMESPACE}forecastingAirport"
_FACT_NAMESPACE = "urn:aviation-agentic-ai:fact:"
_EVENT_NAMESPACE = "urn:aviation-agentic-ai:event:"
_SOURCE_NAMESPACE = "urn:aviation-agentic-ai:source:"

# Neo4j labels / relationship types for the agent-system projection (§6.2).
_LABEL_EVENT = "AviationEvent"
_LABEL_FACILITY = "Facility"
_LABEL_SOURCE = "SourceRecord"
_LABEL_WEATHER_REPORT = "MeteorologicalReport"
_REL_CONTROLLED = "CONTROLLED_NAS_ELEMENT"
_REL_DERIVED = "DERIVED_FROM"
_REL_FORECASTING_AIRPORT = "FORECASTING_AIRPORT"

_PUBLIC_CLASS_LABELS = {
    "urn:aviation-agentic-ai:decision-case-schema:DecisionCase": "DecisionCase",
    "urn:aviation-agentic-ai:decision-case-schema:DecisionCaseReconstruction": "DecisionCaseReconstruction",
    "http://www.w3.org/ns/sosa/Observation": "Observation",
    "http://www.w3.org/ns/sosa/Result": "ObservationResult",
    "http://qudt.org/schema/qudt/QuantityValue": "ObservationResult",
    "http://www.w3.org/2006/time#Interval": "TimeInterval",
    "http://www.w3.org/2006/time#Instant": "TimeInstant",
    "urn:aviation-agentic-ai:decision-case-schema:ObservationPhase": "ObservationPhase",
    "http://www.w3.org/ns/sosa/ObservableProperty": "ObservableProperty",
    "http://qudt.org/schema/qudt/Unit": "Unit",
    "http://www.w3.org/ns/prov#Activity": "AggregationActivity",
    "http://www.w3.org/ns/sosa/Procedure": "ObservationProcedure",
    "http://www.w3.org/ns/prov#Plan": "ObservationProcedure",
}
_PUBLIC_RELATIONSHIP_TYPES = {
    "http://www.w3.org/ns/prov#hadMember": "HAS_MEMBER",
    "http://www.w3.org/ns/prov#specializationOf": "SPECIALIZATION_OF",
    "http://www.w3.org/ns/sosa/hasFeatureOfInterest": "HAS_FEATURE_OF_INTEREST",
    "http://www.w3.org/ns/sosa/observedProperty": "OBSERVED_PROPERTY",
    "http://www.w3.org/ns/sosa/phenomenonTime": "PHENOMENON_TIME",
    "http://www.w3.org/ns/sosa/hasResult": "HAS_RESULT",
    "http://www.w3.org/ns/sosa/usedProcedure": "USED_PROCEDURE",
    "http://www.w3.org/2006/time#hasBeginning": "HAS_BEGINNING",
    "http://www.w3.org/2006/time#hasEnd": "HAS_END",
    "http://purl.org/dc/terms/type": "HAS_PHASE",
    "http://qudt.org/schema/qudt/unit": "HAS_UNIT",
    "http://www.w3.org/ns/prov#wasGeneratedBy": "WAS_GENERATED_BY",
    "http://www.w3.org/ns/prov#used": "USED",
    "http://www.w3.org/ns/prov#generated": "GENERATED",
    _PROV_WAS_DERIVED_FROM_IRI: _REL_DERIVED,
    _FORECASTING_AIRPORT_IRI: _REL_FORECASTING_AIRPORT,
    "https://data.nasa.gov/ontologies/atmonto/ATM#controlledNASelement": _REL_CONTROLLED,
}
_LABEL_PRIORITY = {
    label: priority
    for priority, label in enumerate(
        (
            "DecisionCase",
            "DecisionCaseReconstruction",
            "Observation",
            "ObservationResult",
            "TimeInterval",
            "TimeInstant",
            "ObservationPhase",
            "ObservableProperty",
            "Unit",
            "AggregationActivity",
            "ObservationProcedure",
            "MeteorologicalReport",
            "Facility",
            "AviationEvent",
            "SourceRecord",
        )
    )
}


@dataclass(frozen=True)
class FactMaterialization:
    """Result of materializing accepted ValidatedFacts (plan §6)."""

    fact_count: int
    jsonl_path: str
    ttl_path: str
    nodes_path: str
    relationships_path: str
    schema_slice_id: str
    schema_checksum: str
    profile_refs: tuple[ValidationProfileRef, ...] = ()
    layer_fact_counts: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class FormalPublication:
    """Validated, write-free input to the formal graph projections."""

    accepted: tuple[ValidatedFact, ...]
    snapshot_registry: SourceSnapshotRegistry
    profile_refs: tuple[ValidationProfileRef, ...]
    layer_fact_counts: dict[str, int] = field(default_factory=dict)


class FormalPublicationBlocked(ValueError):
    """Raised when the final multi-profile publication gate rejects a case."""


def _absolute_event_iri(subject_iri: str) -> str:
    """Canonicalize an event subject to an absolute ``urn:...:event:*`` URI.

    The Formal Graph Kernel carries the event subject as ``evt:<sha>``; RDF
    requires absolute IRIs (plan §6.1). Facility/source ids are already
    absolute and pass through unchanged.
    """

    if subject_iri.startswith("evt:"):
        return f"{_EVENT_NAMESPACE}{subject_iri[len('evt:'):]}"
    return subject_iri


def _source_iri(source_id: str) -> str:
    """Stable absolute PROV source URI; the display id is retained as a node
    property (plan §6.1)."""

    safe = source_id.replace(" ", "_")
    return f"{_SOURCE_NAMESPACE}{safe}"


def _is_rdf_type_predicate(predicate_iri: str) -> bool:
    return predicate_iri == _RDF_TYPE_IRI


def _is_prov_predicate(predicate_iri: str) -> bool:
    return predicate_iri == _PROV_WAS_DERIVED_FROM_IRI


def _validated_snapshot_registry(
    source_snapshot: SourceSnapshotRegistry,
) -> SourceSnapshotRegistry:
    """Revalidate the canonical multi-source registry at publication time."""

    return SourceSnapshotRegistry(snapshots=source_snapshot.snapshots)


def _require_fact_snapshot_bindings(
    facts: list[ValidatedFact],
    source_snapshot: SourceSnapshotRegistry,
) -> None:
    """Ensure materialization cannot persist sources absent from a valid snapshot."""

    registry = _validated_snapshot_registry(source_snapshot)
    registered_source_ids = {snapshot.source_id for snapshot in registry.snapshots}
    missing_source_ids = {
        source_id
        for fact in facts
        for source_id in fact.source_ids
        if source_id not in registered_source_ids
    }
    if missing_source_ids:
        raise ValueError(
            "facts cite source IDs without checksum-valid source snapshots: "
            f"{sorted(missing_source_ids)}"
        )


def _profile_iris(
    profile: LoadedValidationProfile,
    mapping_kind: str,
) -> set[str]:
    mappings = (
        profile.class_mappings
        if mapping_kind == "class"
        else profile.property_mappings
    )
    return {mapping["iri"] for mapping in mappings.values()}


def _profile_mapping_for_iri(
    profile: LoadedValidationProfile,
    iri: str,
    mapping_kind: str,
) -> dict[str, str]:
    mappings = (
        profile.class_mappings
        if mapping_kind == "class"
        else profile.property_mappings
    )
    matches = [mapping for mapping in mappings.values() if mapping["iri"] == iri]
    if len(matches) != 1:
        raise ValueError(
            f"{mapping_kind} IRI is not uniquely admitted by profile "
            f"{profile.ref.profile_id}: {iri}"
        )
    return matches[0]


def _validate_observation_numeric_fact(
    fact: ValidatedFact,
    trace: ObservationFactTrace,
) -> None:
    """Bind a published QUDT numeric literal to its owning metric trace."""

    if trace.metric_key in _COUNT_METRIC_KEYS:
        expected_datatype = XSD_INTEGER
        expected_value = str(trace.canonical_value)
    elif trace.metric_key in _MINUTE_METRIC_KEYS:
        expected_datatype = XSD_DECIMAL
        expected_value = format(Decimal(str(trace.canonical_value)), "f")
    else:
        raise ValueError(
            f"unsupported deterministic observation metric: {trace.metric_key}"
        )
    if fact.datatype_iri != expected_datatype:
        raise ValueError(
            f"deterministic numeric datatype mismatch: {fact.fact_id}"
        )
    try:
        numerically_equal = Decimal(fact.object_value) == Decimal(expected_value)
    except InvalidOperation:
        numerically_equal = False
    if fact.object_value != expected_value or not numerically_equal:
        raise ValueError(f"deterministic numeric value mismatch: {fact.fact_id}")


def validate_fact_publication(
    *,
    facts: list[ValidatedFact],
    profile_registry: ValidationProfileRegistry,
    snapshot_registry: SourceSnapshotRegistry,
    fact_traces: tuple[FactTraceRow, ...] | list[FactTraceRow] = (),
    weather_fact_traces: tuple[WeatherFactTrace, ...] | list[WeatherFactTrace] = (),
    observation_fact_traces: (
        tuple[ObservationFactTrace, ...] | list[ObservationFactTrace]
    ) = (),
    reconstruction_trace: ReconstructionTrace | None = None,
    require_source_text_in_snapshot: bool = False,
) -> None:
    """Fail closed before publishing facts from independent semantic profiles."""

    registry = _validated_snapshot_registry(snapshot_registry)
    snapshots = {snapshot.source_id: snapshot for snapshot in registry.snapshots}
    direct_traces: dict[str, FactTraceRow | WeatherFactTrace] = {}
    for trace in [*fact_traces, *weather_fact_traces]:
        previous = direct_traces.setdefault(trace.fact_id, trace)
        if previous != trace:
            raise ValueError(f"conflicting source-text fact trace: {trace.fact_id}")
    derived_traces = {trace.fact_id: trace for trace in observation_fact_traces}
    if len(derived_traces) != len(observation_fact_traces):
        raise ValueError("duplicate deterministic observation fact trace")

    reconstruction_bindings = (
        {binding.source_id: binding for binding in reconstruction_trace.source_bindings}
        if reconstruction_trace is not None
        else {}
    )
    for fact in facts:
        profile = profile_registry.resolve(fact.validation_profile)
        validate_fact_for_publication(fact, profile_registry)
        class_iris = _profile_iris(profile, "class")
        if fact.subject_class_iri not in class_iris:
            raise ValueError(
                f"subject class is not admitted by owning profile: "
                f"{fact.subject_class_iri}"
            )
        if _is_rdf_type_predicate(fact.predicate_iri):
            asserted_class = fact.object_class_iri or fact.object_value
            if asserted_class not in class_iris:
                raise ValueError(
                    f"rdf:type class is not admitted by owning profile: "
                    f"{asserted_class}"
                )
        else:
            mapping = _profile_mapping_for_iri(
                profile, fact.predicate_iri, "property"
            )
            expected_kind = mapping.get("kind")
            expected_kind = {
                "datatype": "literal",
                "object": "iri",
            }.get(expected_kind, expected_kind)
            if expected_kind and expected_kind != fact.object_kind:
                raise ValueError(
                    f"property object kind mismatch for {fact.predicate_iri}"
                )
            admitted_subject_classes = set(
                profile.class_ancestors.get(
                    fact.subject_class_iri,
                    (fact.subject_class_iri,),
                )
            )
            domains = set(
                profile.property_domains.get(fact.predicate_iri, ())
            )
            if domains and not domains.intersection(admitted_subject_classes):
                raise ValueError(
                    f"property domain does not admit subject class: "
                    f"{fact.predicate_iri}"
                )
        if fact.object_kind == "iri" and not _is_rdf_type_predicate(
            fact.predicate_iri
        ):
            if not fact.object_class_iri:
                raise ValueError(
                    f"IRI object has no explicit class: {fact.object_value}"
                )
            if fact.object_class_iri not in class_iris:
                raise ValueError(
                    f"object class is not admitted by owning profile: "
                    f"{fact.object_class_iri}"
                )
            admitted_object_classes = set(
                profile.class_ancestors.get(
                    fact.object_class_iri,
                    (fact.object_class_iri,),
                )
            )
            ranges = set(
                profile.property_ranges.get(fact.predicate_iri, ())
            )
            if ranges and not ranges.intersection(admitted_object_classes):
                raise ValueError(
                    f"property range does not admit object class: "
                    f"{fact.predicate_iri}"
                )
        if fact.object_kind == "literal" and not fact.datatype_iri:
            raise ValueError(f"literal fact has no datatype: {fact.fact_id}")

        for source_id in fact.source_ids:
            snapshot = snapshots.get(source_id)
            if snapshot is None:
                raise ValueError(
                    f"fact source is absent from snapshot registry: {source_id}"
                )
            allowed_families = profile.source_families_by_evidence_mode[
                fact.evidence_mode
            ]
            if snapshot.family not in allowed_families:
                raise ValueError(
                    f"source family is not admitted by owning profile: "
                    f"{snapshot.family.value}"
                )

        if fact.evidence_mode == "source_text":
            if fact.evidence_ref != fact.fact_id:
                raise ValueError(
                    f"source-text evidence reference mismatch: "
                    f"{fact.evidence_ref}"
                )
            trace = direct_traces.get(fact.evidence_ref)
            if trace is None:
                raise ValueError(
                    f"source-text evidence reference is absent: {fact.evidence_ref}"
                )
            snapshot = snapshots.get(trace.source_id)
            if snapshot is None or snapshot.content_sha256 != trace.source_snapshot_sha256:
                raise ValueError(
                    f"source-text evidence checksum mismatch: {fact.evidence_ref}"
                )
            if trace.source_id not in fact.source_ids:
                raise ValueError(
                    f"source-text evidence source mismatch: {fact.evidence_ref}"
                )
            if fact.evidence_texts != [trace.evidence_text]:
                raise ValueError(
                    f"source-text evidence text mismatch: {fact.evidence_ref}"
                )
            if (
                require_source_text_in_snapshot
                and
                trace.evidence_text
                and trace.evidence_text not in snapshot.content
            ):
                raise ValueError(
                    f"source-text evidence is absent from snapshot: "
                    f"{fact.evidence_ref}"
                )
        elif fact.evidence_mode == "deterministic_derivation":
            trace = derived_traces.get(fact.evidence_ref)
            if trace is None:
                raise ValueError(
                    f"deterministic evidence reference is absent: "
                    f"{fact.evidence_ref}"
                )
            snapshot = snapshots.get(trace.source_id)
            if snapshot is None or snapshot.content_sha256 != trace.source_snapshot_sha256:
                raise ValueError(
                    f"deterministic evidence checksum mismatch: "
                    f"{fact.evidence_ref}"
                )
            if trace.source_id not in fact.source_ids:
                raise ValueError(
                    f"deterministic evidence source mismatch: "
                    f"{fact.evidence_ref}"
                )
            if fact.evidence_texts:
                raise ValueError("deterministic facts cannot carry source text")
            if fact.predicate_iri == QUDT_NUMERIC_VALUE:
                _validate_observation_numeric_fact(fact, trace)
        elif fact.evidence_mode == "profile_definition":
            expected_ref = (
                f"{fact.validation_profile.profile_id}:"
                f"{fact.validation_profile.profile_checksum}"
            )
            if fact.evidence_ref != expected_ref:
                raise ValueError("profile-definition evidence reference mismatch")
            if fact.source_ids or fact.evidence_texts:
                raise ValueError("profile-definition facts cannot cite source text")
        elif fact.evidence_mode == "system_membership":
            if (
                reconstruction_trace is None
                or fact.evidence_ref
                != reconstruction_trace.reconstruction_trace_id
            ):
                raise ValueError("system-membership evidence reference mismatch")
            for source_id in fact.source_ids:
                binding = reconstruction_bindings.get(source_id)
                snapshot = snapshots.get(source_id)
                if (
                    binding is None
                    or snapshot is None
                    or binding.snapshot_sha256 != snapshot.content_sha256
                ):
                    raise ValueError(
                        f"system-membership source binding mismatch: {source_id}"
                    )
            if fact.evidence_texts:
                raise ValueError("system-membership facts cannot carry source text")
        else:  # pragma: no cover - Pydantic constrains this before publication
            raise ValueError(f"unsupported evidence mode: {fact.evidence_mode}")


def write_validated_facts_rdf(
    *,
    facts: list[ValidatedFact],
    source_snapshot: SourceSnapshotRegistry,
    output_dir: str | Path,
    profile_registry: ValidationProfileRegistry,
) -> str:
    """Write ``kg.ttl`` from accepted ValidatedFacts (plan §6.1).

    Uses real ATMONTO / RDF / PROV / XSD IRIs taken from the Schema Guide and
    the standard namespaces. Each fact is a reified statement connected to its
    source node(s) via ``prov:wasDerivedFrom``, with the bound evidence text as
    a reification annotation. The writer never constructs
    ``example.org/...#atm:*`` IRIs.
    """

    _require_fact_snapshot_bindings(facts, source_snapshot)
    for fact in facts:
        profile_registry.resolve(fact.validation_profile)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ttl_path = out / "kg.ttl"

    g = _build_rdflib_graph()
    from rdflib import Literal, URIRef
    from rdflib.namespace import RDF, RDFS, XSD

    del XSD  # datatype IRIs are taken from the ValidatedFact directly

    # Emit one reified statement per fact + the source derivation link.
    for fact in sorted(facts, key=lambda item: item.fact_id):
        subj = URIRef(_absolute_event_iri(fact.subject_iri))
        pred = URIRef(fact.predicate_iri)
        if fact.object_kind == "literal":
            datatype = URIRef(fact.datatype_iri) if fact.datatype_iri else None
            obj: Any = Literal(fact.object_value, datatype=datatype) if datatype else Literal(fact.object_value)
        elif _is_rdf_type_predicate(fact.predicate_iri):
            # rdf:type object must be the absolute class IRI (object_class_iri),
            # not the prefixed name carried on object_value (plan §6.1).
            obj = URIRef(fact.object_class_iri or fact.object_value)
        elif _is_prov_predicate(fact.predicate_iri):
            # The Graph Patch carries the registered display source ID. RDF
            # must use the same stable source URI as the reified fact trace,
            # never a relative URI such as ``<2026-05-19:123>``.
            obj = URIRef(
                fact.object_value
                if _is_absolute(fact.object_value)
                else _source_iri(fact.object_value)
            )
        else:
            obj = URIRef(fact.object_value if _is_absolute(fact.object_value) else _absolute_event_iri(fact.object_value))
        # The base triple.
        g.add((subj, pred, obj))
        # rdf:type for the subject class.
        if fact.subject_class_iri:
            g.add((subj, RDF.type, URIRef(fact.subject_class_iri)))
        # Object class for IRI objects.
        if fact.object_kind == "iri" and fact.object_class_iri:
            g.add((obj, RDF.type, URIRef(fact.object_class_iri)))
        # Reified statement connected to its source(s) (plan §6.1).
        stmt = URIRef(f"{_FACT_NAMESPACE}{fact.fact_id}")
        g.add((stmt, RDF.type, RDF.Statement))
        g.add((stmt, RDF.subject, subj))
        g.add((stmt, RDF.predicate, pred))
        g.add((stmt, RDF.object, obj))
        if fact.evidence_mode == "source_text":
            for evidence in fact.evidence_texts:
                g.add((stmt, RDFS.comment, Literal(evidence)))
            for sid in fact.source_ids:
                src = URIRef(_source_iri(sid))
                g.add((src, RDF.type, URIRef(f"{_PROV_NAMESPACE}Entity")))
                g.add((src, RDFS.label, Literal(sid)))
                g.add((stmt, URIRef(_PROV_WAS_DERIVED_FROM_IRI), src))
        else:
            evidence_entity = URIRef(
                stable_id(
                    "publication-evidence",
                    fact.evidence_mode,
                    fact.evidence_ref,
                )
            )
            g.add(
                (
                    evidence_entity,
                    RDF.type,
                    URIRef(f"{_PROV_NAMESPACE}Entity"),
                )
            )
            g.add((evidence_entity, RDFS.label, Literal(fact.evidence_ref)))
            g.add(
                (
                    stmt,
                    URIRef(_PROV_WAS_DERIVED_FROM_IRI),
                    evidence_entity,
                )
            )
    del RDF, RDFS, Literal, URIRef

    g.serialize(destination=str(ttl_path), format="turtle")
    return str(ttl_path)


def _is_absolute(value: str) -> bool:
    return "://" in value or value.startswith("urn:")


def _build_rdflib_graph() -> Any:
    """Build the rdflib Graph with the bound prefixes used in Turtle output."""

    from rdflib import Graph
    from rdflib.namespace import RDF, RDFS, XSD

    g = Graph()
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    g.bind("atm", "https://data.nasa.gov/ontologies/atmonto/ATM#")
    g.bind("nas", "https://data.nasa.gov/ontologies/atmonto/NAS#")
    g.bind("data", _DATA_NAMESPACE)
    g.bind("prov", _PROV_NAMESPACE)
    g.bind("sosa", "http://www.w3.org/ns/sosa/")
    g.bind("time", "http://www.w3.org/2006/time#")
    g.bind("qudt", "http://qudt.org/schema/qudt/")
    g.bind("unit", "http://qudt.org/vocab/unit/")
    g.bind("skos", "http://www.w3.org/2004/02/skos/core#")
    g.bind("dcterms", "http://purl.org/dc/terms/")
    g.bind("case", "urn:aviation-agentic-ai:decision-case-schema:")
    g.bind("aviation-event", _EVENT_NAMESPACE)
    g.bind("aviation-source", _SOURCE_NAMESPACE)
    return g


def write_validated_facts_jsonl(
    *,
    facts: list[ValidatedFact],
    output_dir: str | Path,
    profile_registry: ValidationProfileRegistry,
    source_snapshot: SourceSnapshotRegistry,
) -> str:
    """Write ``kg.jsonl`` in the Query Agent's triple-row shape (plan §6).

    Each row mirrors the existing query-reader keys (subject/predicate/object/
    source_document/subject_class/object_class) so the Query Agent continues to
    read facts without a separate adapter.
    """

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "kg.jsonl"
    rows: list[str] = []
    registry = _validated_snapshot_registry(source_snapshot)
    snapshot_checksums = {
        snapshot.source_id: snapshot.content_sha256
        for snapshot in registry.snapshots
    }
    for fact in sorted(facts, key=lambda item: item.fact_id):
        profile = profile_registry.resolve(fact.validation_profile)
        row = {
            "triple_id": fact.fact_id,
            "subject": _absolute_event_iri(fact.subject_iri),
            "predicate": _prefixed_iri(fact.predicate_iri, profile),
            "object": fact.object_value,
            "subject_class": _prefixed_iri(
                fact.subject_class_iri,
                profile,
            ),
            "object_class": (
                _prefixed_iri(fact.object_class_iri, profile)
                if fact.object_class_iri
                else ""
            ),
            "source_document": ";".join(fact.source_ids),
            "evidence_text": "; ".join(fact.evidence_texts),
            "object_kind": fact.object_kind,
            "datatype_iri": fact.datatype_iri or "",
            "profile_id": fact.validation_profile.profile_id,
            "profile_checksum": fact.validation_profile.profile_checksum,
            "validation_layer": fact.validation_profile.layer,
            "evidence_mode": fact.evidence_mode,
            "evidence_ref": fact.evidence_ref,
            "source_ids": sorted(fact.source_ids),
            "source_snapshot_checksums": {
                source_id: snapshot_checksums[source_id]
                for source_id in sorted(fact.source_ids)
                if source_id in snapshot_checksums
            },
        }
        rows.append(json.dumps(row, ensure_ascii=False, sort_keys=True))
    path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")
    return str(path)


def _prefixed_iri(
    iri: str,
    profile: LoadedValidationProfile,
) -> str:
    namespaces = {
        "rdf": _RDF_NAMESPACE,
        "prov": _PROV_NAMESPACE,
        **profile.namespace_prefixes,
    }
    for prefix, namespace in sorted(
        namespaces.items(), key=lambda item: len(item[1]), reverse=True
    ):
        if iri.startswith(namespace):
            return f"{prefix}:{iri[len(namespace):]}"
    return iri


def _explicit_node_label(resource_iri: str, class_iris: set[str]) -> str:
    candidates = {
        _PUBLIC_CLASS_LABELS[class_iri]
        for class_iri in class_iris
        if class_iri in _PUBLIC_CLASS_LABELS
    }
    if _METEOROLOGICAL_REPORT_IRI in class_iris:
        candidates.add(_LABEL_WEATHER_REPORT)
    if (
        resource_iri.startswith("urn:aviation-agentic-ai:facility:")
        or "https://data.nasa.gov/ontologies/atmonto/NAS#Airport" in class_iris
        or "http://www.w3.org/ns/sosa/FeatureOfInterest" in class_iris
    ):
        candidates.add(_LABEL_FACILITY)
    if (
        resource_iri.startswith(_EVENT_NAMESPACE)
        or any(
            class_iri.startswith(
                "https://data.nasa.gov/ontologies/atmonto/ATM#"
            )
            for class_iri in class_iris
        )
    ):
        candidates.add(_LABEL_EVENT)
    if (
        resource_iri.startswith("urn:aviation-agentic-ai:source-record:")
        or resource_iri.startswith(_SOURCE_NAMESPACE)
    ):
        candidates.add(_LABEL_SOURCE)
    if (
        resource_iri.startswith("urn:aviation-agentic-ai:observation-phase:")
        and "http://www.w3.org/2004/02/skos/core#Concept" in class_iris
    ):
        candidates.add("ObservationPhase")
    if not candidates:
        raise ValueError(
            f"IRI resource has no explicit Neo4j label: {resource_iri}"
        )
    return min(candidates, key=lambda label: _LABEL_PRIORITY[label])


def _fact_projection_metadata(
    fact: ValidatedFact,
    snapshot_checksums: dict[str, str],
) -> dict[str, Any]:
    return {
        "fact_ids": [fact.fact_id],
        "profile_refs": [
            {
                "profile_id": fact.validation_profile.profile_id,
                "profile_checksum": fact.validation_profile.profile_checksum,
                "layer": fact.validation_profile.layer,
            }
        ],
        "evidence_modes": [fact.evidence_mode],
        "evidence_refs": [fact.evidence_ref],
        "source_ids": sorted(fact.source_ids),
        "source_snapshot_checksums": {
            source_id: snapshot_checksums[source_id]
            for source_id in sorted(fact.source_ids)
            if source_id in snapshot_checksums
        },
    }


def _merge_projection_metadata(
    properties: dict[str, Any],
    incoming: dict[str, Any],
) -> None:
    for key in ("fact_ids", "evidence_modes", "evidence_refs", "source_ids"):
        properties[key] = sorted(
            set(properties.get(key, [])) | set(incoming.get(key, []))
        )
    profile_refs = {
        (
            ref["profile_id"],
            ref["profile_checksum"],
            ref["layer"],
        ): ref
        for ref in [
            *properties.get("profile_refs", []),
            *incoming.get("profile_refs", []),
        ]
    }
    properties["profile_refs"] = [
        profile_refs[key] for key in sorted(profile_refs)
    ]
    checksums = dict(properties.get("source_snapshot_checksums", {}))
    for source_id, checksum in incoming.get(
        "source_snapshot_checksums", {}
    ).items():
        previous = checksums.setdefault(source_id, checksum)
        if previous != checksum:
            raise ValueError(
                f"conflicting source snapshot checksum: {source_id}"
            )
    properties["source_snapshot_checksums"] = dict(sorted(checksums.items()))


def _build_multi_profile_neo4j_projection(
    *,
    facts: list[ValidatedFact],
    profile_registry: ValidationProfileRegistry,
    source_snapshot: SourceSnapshotRegistry,
    output_dir: str | Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    snapshots = _validated_snapshot_registry(source_snapshot)
    snapshot_checksums = {
        snapshot.source_id: snapshot.content_sha256
        for snapshot in snapshots.snapshots
    }
    resource_classes: dict[str, set[str]] = {}
    for fact in facts:
        profile_registry.resolve(fact.validation_profile)
        subject = _absolute_event_iri(fact.subject_iri)
        resource_classes.setdefault(subject, set()).add(
            fact.subject_class_iri
        )
        if _is_rdf_type_predicate(fact.predicate_iri):
            resource_classes[subject].add(
                fact.object_class_iri or fact.object_value
            )
        elif fact.object_kind == "iri":
            obj = (
                _source_iri(fact.object_value)
                if _is_prov_predicate(fact.predicate_iri)
                and not _is_absolute(fact.object_value)
                else (
                    fact.object_value
                    if _is_absolute(fact.object_value)
                    else _absolute_event_iri(fact.object_value)
                )
            )
            if fact.object_class_iri:
                resource_classes.setdefault(obj, set()).add(
                    fact.object_class_iri
                )

    nodes: dict[str, dict[str, Any]] = {}
    relationships: dict[str, dict[str, Any]] = {}

    def ensure_node(resource_iri: str, fact: ValidatedFact) -> dict[str, Any]:
        classes = resource_classes.get(resource_iri, set())
        label = _explicit_node_label(resource_iri, classes)
        metadata = _fact_projection_metadata(fact, snapshot_checksums)
        existing = nodes.get(resource_iri)
        if existing is None:
            existing = {
                "id": resource_iri,
                "label": label,
                "properties": {
                    "id": resource_iri,
                    "ontology_class_iris": sorted(classes),
                    **metadata,
                },
            }
            nodes[resource_iri] = existing
        else:
            if existing["label"] != label:
                raise ValueError(
                    f"conflicting explicit Neo4j label: {resource_iri}"
                )
            existing["properties"]["ontology_class_iris"] = sorted(
                set(existing["properties"].get("ontology_class_iris", []))
                | classes
            )
            _merge_projection_metadata(existing["properties"], metadata)
        return existing

    for fact in sorted(facts, key=lambda item: item.fact_id):
        subject = _absolute_event_iri(fact.subject_iri)
        subject_node = ensure_node(subject, fact)
        if _is_rdf_type_predicate(fact.predicate_iri):
            continue
        if fact.object_kind == "literal":
            property_name = _predicate_local_name(fact.predicate_iri)
            value = _coerce_datatype_value(fact)
            previous = subject_node["properties"].setdefault(
                property_name, value
            )
            if previous != value:
                raise ValueError(
                    f"conflicting Neo4j literal property: "
                    f"{subject} {fact.predicate_iri}"
                )
            continue
        obj = (
            _source_iri(fact.object_value)
            if _is_prov_predicate(fact.predicate_iri)
            and not _is_absolute(fact.object_value)
            else (
                fact.object_value
                if _is_absolute(fact.object_value)
                else _absolute_event_iri(fact.object_value)
            )
        )
        ensure_node(obj, fact)
        rel_type = _PUBLIC_RELATIONSHIP_TYPES.get(fact.predicate_iri)
        if rel_type is None:
            raise ValueError(
                f"predicate has no explicit Neo4j relationship mapping: "
                f"{fact.predicate_iri}"
            )
        rel_id = stable_id("neo4j-rel", subject, fact.predicate_iri, obj)
        metadata = _fact_projection_metadata(fact, snapshot_checksums)
        incoming = {
            "id": rel_id,
            "type": rel_type,
            "start_id": subject,
            "end_id": obj,
            "properties": {
                "id": rel_id,
                "predicate_iri": fact.predicate_iri,
                **metadata,
            },
        }
        existing = relationships.get(rel_id)
        if existing is None:
            relationships[rel_id] = incoming
        else:
            if any(
                existing[key] != incoming[key]
                for key in ("type", "start_id", "end_id")
            ):
                raise ValueError(
                    f"conflicting Neo4j relationship id: {rel_id}"
                )
            _merge_projection_metadata(
                existing["properties"], incoming["properties"]
            )

    # Preserve source binding in the current profile-owned projection even
    # when no explicit PROV fact was proposed. One canonical SourceRecord and
    # DERIVED_FROM edge is derived from each fact's validated source IDs.
    for fact in sorted(facts, key=lambda item: item.fact_id):
        subject = _absolute_event_iri(fact.subject_iri)
        ensure_node(subject, fact)
        for source_id in sorted(fact.source_ids):
            source = _source_iri(source_id)
            source_node = ensure_node(source, fact)
            source_node["properties"]["source_id"] = source_id
            rel_id = stable_id(
                "neo4j-rel",
                subject,
                _PROV_WAS_DERIVED_FROM_IRI,
                source,
            )
            metadata = _fact_projection_metadata(fact, snapshot_checksums)
            incoming = {
                "id": rel_id,
                "type": _REL_DERIVED,
                "start_id": subject,
                "end_id": source,
                "properties": {
                    "id": rel_id,
                    "predicate_iri": _PROV_WAS_DERIVED_FROM_IRI,
                    **metadata,
                },
            }
            existing = relationships.get(rel_id)
            if existing is None:
                relationships[rel_id] = incoming
            else:
                _merge_projection_metadata(
                    existing["properties"],
                    incoming["properties"],
                )

    node_rows = [nodes[key] for key in sorted(nodes)]
    relationship_rows = [
        relationships[key] for key in sorted(relationships)
    ]
    nodes_path = out / "neo4j_nodes.jsonl"
    rels_path = out / "neo4j_relationships.jsonl"
    _write_jsonl(nodes_path, node_rows)
    _write_jsonl(rels_path, relationship_rows)
    return node_rows, relationship_rows, str(nodes_path), str(rels_path)


def build_validated_facts_neo4j_projection(
    *,
    facts: list[ValidatedFact],
    output_dir: str | Path,
    profile_registry: ValidationProfileRegistry,
    source_snapshot: SourceSnapshotRegistry,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str, str]:
    """Build the profile-owned Neo4j projection for the current run."""

    return _build_multi_profile_neo4j_projection(
        facts=facts,
        profile_registry=profile_registry,
        source_snapshot=source_snapshot,
        output_dir=output_dir,
    )


def _predicate_local_name(iri: str) -> str:
    for sep in ("#", "/"):
        if sep in iri:
            return iri.rsplit(sep, 1)[-1]
    return iri


def _coerce_datatype_value(fact: ValidatedFact) -> Any:
    """Coerce a literal to its native Python type for the Neo4j property."""

    if fact.datatype_iri and fact.datatype_iri.endswith("integer"):
        try:
            return int(fact.object_value)
        except ValueError:
            return fact.object_value
    return fact.object_value


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(
            json.dumps(r, ensure_ascii=False, sort_keys=True) for r in rows
        )
        + ("\n" if rows else ""),
        encoding="utf-8",
    )


def run_formal_publication_kernel(
    *,
    facts: list[ValidatedFact],
    profile_registry: ValidationProfileRegistry,
    source_snapshot: SourceSnapshotRegistry,
    fact_traces: tuple[FactTraceRow, ...] | list[FactTraceRow] = (),
    weather_fact_traces: tuple[WeatherFactTrace, ...] | list[WeatherFactTrace] = (),
    observation_fact_traces: (
        tuple[ObservationFactTrace, ...] | list[ObservationFactTrace]
    ) = (),
    reconstruction_trace: ReconstructionTrace | None = None,
) -> FormalPublication:
    """Validate every admitted formal layer without writing projections."""

    try:
        registry = _validated_snapshot_registry(source_snapshot)
        _require_fact_snapshot_bindings(facts, registry)
        validate_fact_publication(
            facts=facts,
            profile_registry=profile_registry,
            snapshot_registry=registry,
            fact_traces=fact_traces,
            weather_fact_traces=weather_fact_traces,
            observation_fact_traces=observation_fact_traces,
            reconstruction_trace=reconstruction_trace,
        )
    except ValueError as exc:
        raise FormalPublicationBlocked(str(exc)) from exc
    profile_refs = tuple(
        sorted(
            {fact.validation_profile for fact in facts},
            key=lambda ref: (ref.layer, ref.profile_id, ref.profile_checksum),
        )
    )
    layer_fact_counts: dict[str, int] = {}
    for fact in facts:
        layer = fact.validation_profile.layer
        layer_fact_counts[layer] = layer_fact_counts.get(layer, 0) + 1
    return FormalPublication(
        accepted=tuple(facts),
        snapshot_registry=registry,
        profile_refs=profile_refs,
        layer_fact_counts=dict(sorted(layer_fact_counts.items())),
    )


def materialize_formal_publication(
    *,
    publication: FormalPublication,
    profile_registry: ValidationProfileRegistry,
    output_dir: str | Path,
) -> FactMaterialization:
    """Write the projections of a previously accepted formal publication."""

    facts = list(publication.accepted)
    registry = publication.snapshot_registry
    jsonl_path = write_validated_facts_jsonl(
        facts=facts,
        output_dir=output_dir,
        profile_registry=profile_registry,
        source_snapshot=registry,
    )
    ttl_path = write_validated_facts_rdf(
        facts=facts,
        source_snapshot=registry,
        output_dir=output_dir,
        profile_registry=profile_registry,
    )
    _nodes, _rels, nodes_path, rels_path = build_validated_facts_neo4j_projection(
        facts=facts,
        output_dir=output_dir,
        profile_registry=profile_registry,
        source_snapshot=registry,
    )
    profile_refs = publication.profile_refs
    decision_only = bool(profile_refs) and all(
        ref.layer == "decision" for ref in profile_refs
    )
    return FactMaterialization(
        fact_count=len(facts),
        jsonl_path=jsonl_path,
        ttl_path=ttl_path,
        nodes_path=nodes_path,
        relationships_path=rels_path,
        schema_slice_id=profile_refs[0].profile_id if decision_only else "",
        schema_checksum=(
            profile_refs[0].profile_checksum if decision_only else ""
        ),
        profile_refs=profile_refs,
        layer_fact_counts=publication.layer_fact_counts,
    )


def materialize_validated_facts(
    *,
    facts: list[ValidatedFact],
    profile_registry: ValidationProfileRegistry,
    source_snapshot: SourceSnapshotRegistry,
    fact_traces: tuple[FactTraceRow, ...] | list[FactTraceRow] = (),
    weather_fact_traces: tuple[WeatherFactTrace, ...] | list[WeatherFactTrace] = (),
    observation_fact_traces: (
        tuple[ObservationFactTrace, ...] | list[ObservationFactTrace]
    ) = (),
    reconstruction_trace: ReconstructionTrace | None = None,
    output_dir: str | Path,
) -> FactMaterialization:
    """Low-level helper composing the final gate and projection writer."""

    publication = run_formal_publication_kernel(
        facts=facts,
        profile_registry=profile_registry,
        source_snapshot=source_snapshot,
        fact_traces=fact_traces,
        weather_fact_traces=weather_fact_traces,
        observation_fact_traces=observation_fact_traces,
        reconstruction_trace=reconstruction_trace,
    )
    return materialize_formal_publication(
        publication=publication,
        profile_registry=profile_registry,
        output_dir=output_dir,
    )


# ---------------------------------------------------------------------------
# Neo4j load: parameterized MERGE (plan §6.2)
# ---------------------------------------------------------------------------


class Neo4jLoadBlocked(RuntimeError):
    """Raised when Neo4j load cannot proceed (plan §6.2: BLOCKED, not faked)."""


_ALLOWED_NEO4J_LABELS = {
    _LABEL_EVENT,
    _LABEL_FACILITY,
    _LABEL_SOURCE,
    _LABEL_WEATHER_REPORT,
    *_PUBLIC_CLASS_LABELS.values(),
}
_ALLOWED_NEO4J_RELATIONSHIPS = {
    _REL_CONTROLLED,
    _REL_DERIVED,
    _REL_FORECASTING_AIRPORT,
    *_PUBLIC_RELATIONSHIP_TYPES.values(),
}
_SAFE_NEO4J_TOKEN = re.compile(r"^[A-Z][A-Z0-9_]*$")


def _validate_neo4j_projection(
    nodes: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
) -> None:
    """Fail closed before connecting when a projection is not loadable."""

    node_ids: set[str] = set()
    for row in nodes:
        node_id = str(row.get("id") or "").strip()
        label = str(row.get("label") or "").strip()
        if not node_id:
            raise Neo4jLoadBlocked("Neo4j projection contains a node without an id")
        if node_id in node_ids:
            raise Neo4jLoadBlocked(f"duplicate Neo4j node id: {node_id}")
        if label not in _ALLOWED_NEO4J_LABELS:
            raise Neo4jLoadBlocked(f"unsupported Neo4j node label: {label}")
        node_ids.add(node_id)

    relationship_ids: set[str] = set()
    for row in relationships:
        relationship_id = str(row.get("id") or "").strip()
        relationship_type = str(row.get("type") or "").strip()
        start_id = str(row.get("start_id") or "").strip()
        end_id = str(row.get("end_id") or "").strip()
        if not relationship_id:
            raise Neo4jLoadBlocked(
                "Neo4j projection contains a relationship without an id"
            )
        if relationship_id in relationship_ids:
            raise Neo4jLoadBlocked(
                f"duplicate Neo4j relationship id: {relationship_id}"
            )
        if (
            relationship_type not in _ALLOWED_NEO4J_RELATIONSHIPS
            or not _SAFE_NEO4J_TOKEN.fullmatch(relationship_type)
        ):
            raise Neo4jLoadBlocked(
                f"unsupported Neo4j relationship type: {relationship_type}"
            )
        if start_id not in node_ids or end_id not in node_ids:
            raise Neo4jLoadBlocked(
                "Neo4j relationship endpoint is not materialized: "
                f"{relationship_id} ({start_id} -> {end_id})"
            )
        relationship_ids.add(relationship_id)


def load_validated_facts_neo4j(
    *,
    nodes_path: str | Path,
    relationships_path: str | Path,
    uri: str | None = None,
    username: str | None = None,
    password: str | None = None,
    database: str = "neo4j",
    batch_size: int = 500,
    driver_factory: Any | None = None,
) -> dict[str, Any]:
    """Load the agent-system projection with parameterized MERGE (plan §6.2).

    Missing credentials or a connectivity/load failure raises
    ``Neo4jLoadBlocked``; the caller (CLI) maps that to ``BLOCKED``. This loader
    NEVER clears unrelated graph data — it only MERGEs the run's nodes and
    relationships by stable id, so a sentinel node is preserved across loads.
    """

    nodes = _read_jsonl(nodes_path)
    relationships = _read_jsonl(relationships_path)
    if batch_size <= 0:
        raise Neo4jLoadBlocked("batch_size must be positive")
    _validate_neo4j_projection(nodes, relationships)
    if uri is None or username is None or password is None:
        raise Neo4jLoadBlocked("missing Neo4j credentials (uri/username/password)")
    factory = driver_factory
    driver_errors: tuple[type[Exception], ...] = (Exception,)
    if factory is None:
        try:
            from neo4j import GraphDatabase
            from neo4j.exceptions import DriverError, Neo4jError
        except ImportError as exc:
            raise Neo4jLoadBlocked(
                "Neo4j driver not installed; run `uv sync --extra neo4j`"
            ) from exc
        factory = GraphDatabase.driver
        driver_errors = (DriverError, Neo4jError,)

    try:
        with factory(uri, auth=(username, password)) as driver:
            driver.verify_connectivity()
            # Ensure id uniqueness constraints for each label (idempotent).
            for label in sorted(_ALLOWED_NEO4J_LABELS):
                driver.execute_query(
                    f"CREATE CONSTRAINT {label.lower()}_id IF NOT EXISTS "
                    f"FOR (n:{label}) REQUIRE n.id IS UNIQUE",
                    database_=database,
                )
            # Parameterized MERGE for nodes — never DETACH DELETE; sentinel
            # nodes outside this projection are preserved.
            for label in sorted(_ALLOWED_NEO4J_LABELS):
                rows = [r for r in nodes if r.get("label") == label]
                for start in range(0, len(rows), batch_size):
                    driver.execute_query(
                        f"UNWIND $rows AS row MERGE (n:{label} {{id: row.id}}) "
                        "SET n += row.properties",
                        rows=rows[start : start + batch_size],
                        database_=database,
                    )
            # Parameterized MERGE for relationships by stable id.
            rel_types = sorted({r["type"] for r in relationships})
            for rel_type in rel_types:
                rows = [r for r in relationships if r["type"] == rel_type]
                for start in range(0, len(rows), batch_size):
                    driver.execute_query(
                        "UNWIND $rows AS row "
                        "MATCH (a {id: row.start_id}) MATCH (b {id: row.end_id}) "
                        f"MERGE (a)-[r:{rel_type} {{id: row.id}}]->(b) "
                        "SET r += row.properties",
                        rows=rows[start : start + batch_size],
                        database_=database,
                    )
    except driver_errors as exc:  # connectivity / load failure -> BLOCKED
        raise Neo4jLoadBlocked(f"Neo4j load failed: {exc}") from exc
    return {
        "nodes": len(nodes),
        "relationships": len(relationships),
        "node_labels": sorted({r.get("label", "") for r in nodes}),
        "relationship_types": sorted({r.get("type", "") for r in relationships}),
    }
def _read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return []
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
