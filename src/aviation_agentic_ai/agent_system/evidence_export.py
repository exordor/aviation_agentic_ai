"""Optional, reproducible exports from the live aviation evidence store.

The SQLite evidence store remains authoritative.  These files are bounded
artifacts for interchange, inspection, and external graph loading; their
manifests are never required by the query runtime.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable

from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    EventEvidenceLink,
    SemanticFactRecord,
    SourceVersionRecord,
    TMIEventRecord,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id


_RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
_RDFS = "http://www.w3.org/2000/01/rdf-schema#"
_XSD = "http://www.w3.org/2001/XMLSchema#"
_PROV = "http://www.w3.org/ns/prov#"
_ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
_NAS = "https://data.nasa.gov/ontologies/atmonto/NAS#"
_DATA = "https://data.nasa.gov/ontologies/atmonto/data#"
_SOSA = "http://www.w3.org/ns/sosa/"
_TIME = "http://www.w3.org/2006/time#"
_QUDT = "http://qudt.org/schema/qudt/"
_DCTERMS = "http://purl.org/dc/terms/"

_PREFIXES = {
    "rdf": _RDF,
    "rdfs": _RDFS,
    "xsd": _XSD,
    "prov": _PROV,
    "atm": _ATM,
    "nas": _NAS,
    "data": _DATA,
    "sosa": _SOSA,
    "time": _TIME,
    "qudt": _QUDT,
    "dcterms": _DCTERMS,
}

_RELATIONSHIP_TYPES = {
    f"{_ATM}controlledNASelement": "CONTROLLED_NAS_ELEMENT",
    f"{_DATA}forecastingAirport": "FORECASTING_AIRPORT",
    f"{_SOSA}hasFeatureOfInterest": "HAS_FEATURE_OF_INTEREST",
    f"{_SOSA}observedProperty": "OBSERVED_PROPERTY",
    f"{_SOSA}phenomenonTime": "PHENOMENON_TIME",
    f"{_SOSA}hasResult": "HAS_RESULT",
    f"{_SOSA}usedProcedure": "USED_PROCEDURE",
    f"{_TIME}hasBeginning": "HAS_BEGINNING",
    f"{_TIME}hasEnd": "HAS_END",
    f"{_DCTERMS}type": "HAS_PHASE",
    f"{_QUDT}unit": "HAS_UNIT",
    f"{_PROV}wasGeneratedBy": "WAS_GENERATED_BY",
    f"{_PROV}used": "USED",
    f"{_PROV}generated": "GENERATED",
    f"{_PROV}wasDerivedFrom": "DERIVED_FROM",
}


@dataclass(frozen=True)
class KGProjection:
    """Paths and counts for one rebuildable formal graph export."""

    output_dir: str
    manifest_path: str
    jsonl_path: str
    ttl_path: str
    nodes_path: str
    relationships_path: str
    event_count: int
    fact_count: int
    evidence_link_count: int


def export_event(
    store: AviationEvidenceStore,
    event_id: str,
    output_dir: str | Path,
) -> Path:
    """Export only the active publication and exact evidence of one event."""

    event = store.get_event(event_id)
    if event is None:
        raise KeyError(f"TMI event does not exist: {event_id}")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    facts = store.get_event_facts(
        event.event_id,
        publication_id=event.publication_id,
    )
    links = store.get_event_evidence(
        event.event_id,
        publication_id=event.publication_id,
    )
    gaps = store.get_event_profile_gaps(
        event.event_id,
        publication_id=event.publication_id,
    )
    weather = store.get_event_weather(event.event_id)
    observations = store.get_event_observations(
        event.event_id,
        ("baseline", "active", "recovery"),
    )

    version_ids = {
        version.source_version_id
        for version in store.get_event_sources(
            event.event_id,
            publication_id=event.publication_id,
        )
    }
    version_ids.update(link.source_version_id for link in links)
    version_ids.update(gap.source_version_id for gap in gaps)
    version_ids.update(row.source_version_id for row in weather)
    version_ids.update(row.source_version_id for row in observations)
    versions = tuple(
        version
        for version_id in sorted(version_ids)
        if (version := store.get_source_version(version_id)) is not None
    )

    anchor_ids = {
        link.source_anchor_id
        for link in links
        if link.source_anchor_id is not None
    }
    anchor_ids.update(gap.source_anchor_id for gap in gaps)
    anchors = tuple(
        anchor
        for anchor_id in sorted(anchor_ids)
        if (anchor := store.get_source_anchor(anchor_id)) is not None
    )

    _write_json(out / "event.json", event.model_dump(mode="json"))
    _write_models(out / "facts.jsonl", facts)
    _write_models(out / "evidence_links.jsonl", links)
    _write_models(out / "profile_gaps.jsonl", gaps)
    _write_models(out / "weather_associations.jsonl", weather)
    _write_models(out / "public_observations.jsonl", observations)
    _write_models(out / "source_versions.jsonl", versions)
    _write_models(out / "source_anchors.jsonl", anchors)

    projection = _build_projection(
        store,
        out,
        events=(event,),
    )
    artifact_names = (
        "event.json",
        "facts.jsonl",
        "evidence_links.jsonl",
        "profile_gaps.jsonl",
        "weather_associations.jsonl",
        "public_observations.jsonl",
        "source_versions.jsonl",
        "source_anchors.jsonl",
        "kg.jsonl",
        "kg.ttl",
        "neo4j_nodes.jsonl",
        "neo4j_relationships.jsonl",
        Path(projection.manifest_path).name,
    )
    manifest = {
        "format": "aviation-event-export-v1",
        "dataset_id": store.dataset_id,
        "knowledge_revision": store.get_knowledge_revision(),
        "event_id": event.event_id,
        "publication_id": event.publication_id,
        "artifacts": {
            name: _file_record(out / name) for name in artifact_names
        },
    }
    manifest_path = out / "event_export_manifest.json"
    _write_json(manifest_path, manifest)
    return manifest_path


def build_store_kg_projection(
    store: AviationEvidenceStore,
    output_dir: str | Path,
) -> KGProjection:
    """Project all active formal facts and exact event provenance."""

    events = store.list_tmi_event_publications(active_only=True)
    return _build_projection(store, Path(output_dir), events=events)


def _build_projection(
    store: AviationEvidenceStore,
    output_dir: Path,
    *,
    events: tuple[TMIEventRecord, ...],
) -> KGProjection:
    output_dir.mkdir(parents=True, exist_ok=True)
    facts: dict[str, SemanticFactRecord] = {}
    bindings: dict[str, list[dict[str, Any]]] = defaultdict(list)
    versions: dict[str, SourceVersionRecord] = {}
    evidence_link_count = 0

    for event in sorted(events, key=lambda row: row.event_id):
        event_facts = store.get_event_facts(
            event.event_id,
            publication_id=event.publication_id,
        )
        event_links = tuple(
            link
            for link in store.get_event_evidence(
                event.event_id,
                publication_id=event.publication_id,
            )
            if link.owner_kind == "fact"
        )
        links_by_fact: dict[str, list[EventEvidenceLink]] = defaultdict(list)
        for link in event_links:
            links_by_fact[link.owner_id].append(link)
            version = store.get_source_version(link.source_version_id)
            if version is not None:
                versions[version.source_version_id] = version
        evidence_link_count += len(event_links)
        for fact in event_facts:
            previous = facts.setdefault(fact.fact_id, fact)
            if previous != fact:
                raise ValueError(f"conflicting semantic fact: {fact.fact_id}")
            bindings[fact.fact_id].append(
                {
                    "event_id": event.event_id,
                    "publication_id": event.publication_id,
                    "evidence_links": [
                        link.model_dump(mode="json")
                        for link in sorted(
                            links_by_fact.get(fact.fact_id, ()),
                            key=lambda row: row.evidence_link_id,
                        )
                    ],
                }
            )

    jsonl_rows = [
        {
            **facts[fact_id].model_dump(mode="json"),
            "event_bindings": sorted(
                bindings[fact_id],
                key=lambda row: (
                    row["event_id"],
                    row["publication_id"],
                ),
            ),
        }
        for fact_id in sorted(facts)
    ]
    jsonl_path = output_dir / "kg.jsonl"
    _write_jsonl(jsonl_path, jsonl_rows)
    ttl_path = output_dir / "kg.ttl"
    _write_rdf(
        ttl_path,
        facts=facts,
        bindings=bindings,
        versions=versions,
    )
    nodes_path = output_dir / "neo4j_nodes.jsonl"
    relationships_path = output_dir / "neo4j_relationships.jsonl"
    node_rows, relationship_rows = _neo4j_rows(
        facts=facts,
        bindings=bindings,
        versions=versions,
    )
    _write_jsonl(nodes_path, node_rows)
    _write_jsonl(relationships_path, relationship_rows)

    manifest = {
        "format": "aviation-evidence-kg-export-v1",
        "dataset_id": store.dataset_id,
        "knowledge_revision": store.get_knowledge_revision(),
        "active_event_count": len(events),
        "fact_count": len(facts),
        "fact_evidence_link_count": evidence_link_count,
        "artifacts": {
            path.name: _file_record(path)
            for path in (
                jsonl_path,
                ttl_path,
                nodes_path,
                relationships_path,
            )
        },
    }
    manifest_path = output_dir / "kg_projection_manifest.json"
    _write_json(manifest_path, manifest)
    return KGProjection(
        output_dir=str(output_dir),
        manifest_path=str(manifest_path),
        jsonl_path=str(jsonl_path),
        ttl_path=str(ttl_path),
        nodes_path=str(nodes_path),
        relationships_path=str(relationships_path),
        event_count=len(events),
        fact_count=len(facts),
        evidence_link_count=evidence_link_count,
    )


def _write_rdf(
    path: Path,
    *,
    facts: dict[str, SemanticFactRecord],
    bindings: dict[str, list[dict[str, Any]]],
    versions: dict[str, SourceVersionRecord],
) -> None:
    from rdflib import Graph, Literal, URIRef
    from rdflib.namespace import RDF, RDFS

    graph = Graph()
    for prefix, namespace in _PREFIXES.items():
        graph.bind(prefix, namespace)
    for fact_id in sorted(facts):
        fact = facts[fact_id]
        subject = URIRef(_expand_iri(fact.subject_iri))
        predicate = URIRef(_expand_iri(fact.predicate_iri))
        if fact.object_kind == "literal":
            datatype = (
                URIRef(_expand_iri(fact.datatype_iri))
                if fact.datatype_iri
                else None
            )
            obj: Any = Literal(fact.object_value, datatype=datatype)
        else:
            obj = URIRef(_expand_iri(fact.object_value))
        graph.add((subject, predicate, obj))
        graph.add(
            (
                subject,
                RDF.type,
                URIRef(_expand_iri(fact.subject_class_iri)),
            )
        )
        if fact.object_kind == "iri" and fact.object_class_iri:
            graph.add(
                (
                    obj,
                    RDF.type,
                    URIRef(_expand_iri(fact.object_class_iri)),
                )
            )
        statement = URIRef(
            f"urn:aviation-agentic-ai:fact-statement:{fact.fact_id}"
        )
        graph.add((statement, RDF.type, RDF.Statement))
        graph.add((statement, RDF.subject, subject))
        graph.add((statement, RDF.predicate, predicate))
        graph.add((statement, RDF.object, obj))
        graph.add((statement, URIRef(f"{_DCTERMS}identifier"), Literal(fact_id)))
        for binding in bindings[fact_id]:
            graph.add(
                (
                    statement,
                    URIRef("urn:aviation-agentic-ai:publication"),
                    URIRef(
                        "urn:aviation-agentic-ai:event-publication:"
                        f"{binding['publication_id']}"
                    ),
                )
            )
            for link in binding["evidence_links"]:
                source_version_id = link["source_version_id"]
                source = URIRef(_source_version_iri(source_version_id))
                graph.add((source, RDF.type, URIRef(f"{_PROV}Entity")))
                graph.add(
                    (
                        source,
                        URIRef(f"{_DCTERMS}identifier"),
                        Literal(source_version_id),
                    )
                )
                version = versions.get(source_version_id)
                if version is not None:
                    graph.add(
                        (
                            source,
                            URIRef(f"{_DCTERMS}source"),
                            Literal(version.source_id),
                        )
                    )
                graph.add(
                    (
                        statement,
                        URIRef(f"{_PROV}wasDerivedFrom"),
                        source,
                    )
                )
                graph.add(
                    (
                        statement,
                        RDFS.seeAlso,
                        Literal(link["evidence_ref"]),
                    )
                )
                if link["source_anchor_id"] is not None:
                    graph.add(
                        (
                            statement,
                            URIRef(
                                "urn:aviation-agentic-ai:sourceAnchor"
                            ),
                            URIRef(
                                "urn:aviation-agentic-ai:source-anchor:"
                                f"{link['source_anchor_id']}"
                            ),
                        )
                    )
    graph.serialize(destination=str(path), format="turtle")


def _neo4j_rows(
    *,
    facts: dict[str, SemanticFactRecord],
    bindings: dict[str, list[dict[str, Any]]],
    versions: dict[str, SourceVersionRecord],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    nodes: dict[str, dict[str, Any]] = {}
    relationships: dict[str, dict[str, Any]] = {}

    def ensure_node(
        node_id: str,
        *,
        class_iri: str | None = None,
        label: str | None = None,
    ) -> dict[str, Any]:
        resolved = _expand_iri(node_id)
        selected_label = label or _node_label(resolved, class_iri)
        node = nodes.setdefault(
            resolved,
            {
                "id": resolved,
                "label": selected_label,
                "properties": {
                    "id": resolved,
                    "ontology_class_iris": [],
                    "fact_ids": [],
                },
            },
        )
        if class_iri:
            classes = set(node["properties"]["ontology_class_iris"])
            classes.add(_expand_iri(class_iri))
            node["properties"]["ontology_class_iris"] = sorted(classes)
        return node

    for fact_id in sorted(facts):
        fact = facts[fact_id]
        subject_id = _expand_iri(fact.subject_iri)
        subject = ensure_node(
            subject_id,
            class_iri=fact.subject_class_iri,
        )
        subject["properties"]["fact_ids"] = sorted(
            set(subject["properties"]["fact_ids"]) | {fact_id}
        )
        predicate = _expand_iri(fact.predicate_iri)
        if predicate == f"{_RDF}type":
            subject["properties"]["ontology_class_iris"] = sorted(
                set(subject["properties"]["ontology_class_iris"])
                | {
                    _expand_iri(
                        fact.object_class_iri or fact.object_value
                    )
                }
            )
        elif fact.object_kind == "literal":
            _merge_node_property(
                subject["properties"],
                _local_name(predicate),
                _native_literal(fact),
            )
        else:
            object_id = _expand_iri(fact.object_value)
            ensure_node(
                object_id,
                class_iri=fact.object_class_iri,
            )
            relationship_type = _RELATIONSHIP_TYPES.get(predicate)
            if relationship_type is None:
                _merge_node_property(
                    subject["properties"],
                    f"{_local_name(predicate)}_iris",
                    object_id,
                )
            else:
                relationship_id = stable_id(
                    "neo4j-rel",
                    subject_id,
                    predicate,
                    object_id,
                )
                relationships[relationship_id] = {
                    "id": relationship_id,
                    "type": relationship_type,
                    "start_id": subject_id,
                    "end_id": object_id,
                    "properties": {
                        "id": relationship_id,
                        "predicate_iri": predicate,
                        "fact_ids": [fact_id],
                    },
                }
        for binding in bindings[fact_id]:
            for link in binding["evidence_links"]:
                source_version_id = link["source_version_id"]
                source_iri = _source_version_iri(source_version_id)
                version = versions.get(source_version_id)
                source = ensure_node(source_iri, label="SourceRecord")
                if version is not None:
                    source["properties"].update(
                        {
                            "source_version_id": source_version_id,
                            "source_id": version.source_id,
                            "family": version.family.value,
                            "content_sha256": version.content_sha256,
                            "source_url": version.source_url,
                        }
                    )
                relationship_id = stable_id(
                    "neo4j-rel",
                    subject_id,
                    f"{_PROV}wasDerivedFrom",
                    source_version_id,
                    link["evidence_link_id"],
                )
                relationships[relationship_id] = {
                    "id": relationship_id,
                    "type": "DERIVED_FROM",
                    "start_id": subject_id,
                    "end_id": source_iri,
                    "properties": {
                        "id": relationship_id,
                        "predicate_iri": f"{_PROV}wasDerivedFrom",
                        "fact_ids": [fact_id],
                        "event_id": binding["event_id"],
                        "publication_id": binding["publication_id"],
                        "source_version_id": source_version_id,
                        "source_anchor_id": link["source_anchor_id"],
                        "evidence_ref": link["evidence_ref"],
                    },
                }
    return (
        [nodes[key] for key in sorted(nodes)],
        [relationships[key] for key in sorted(relationships)],
    )


def _node_label(resource_iri: str, class_iri: str | None) -> str:
    resolved_class = _expand_iri(class_iri) if class_iri else ""
    if resource_iri.startswith("urn:aviation-agentic-ai:facility:"):
        return "Facility"
    if resolved_class.endswith("Airport"):
        return "Facility"
    if resolved_class == f"{_DATA}MeteorologicalReport":
        return "MeteorologicalReport"
    if resolved_class == f"{_SOSA}Observation":
        return "Observation"
    if resolved_class == f"{_SOSA}Result":
        return "ObservationResult"
    if resolved_class == f"{_TIME}Interval":
        return "TimeInterval"
    if resolved_class == f"{_TIME}Instant":
        return "TimeInstant"
    return "AviationEvent"


def _merge_node_property(
    properties: dict[str, Any],
    key: str,
    value: Any,
) -> None:
    if key not in properties:
        properties[key] = value
        return
    existing = properties[key]
    if existing == value:
        return
    values = existing if isinstance(existing, list) else [existing]
    if value not in values:
        values.append(value)
    properties[key] = sorted(values, key=str)


def _native_literal(fact: SemanticFactRecord) -> Any:
    datatype = fact.datatype_iri or ""
    if datatype.endswith("integer"):
        try:
            return int(fact.object_value)
        except ValueError:
            return fact.object_value
    if datatype.endswith("decimal"):
        try:
            return float(Decimal(fact.object_value))
        except Exception:
            return fact.object_value
    return fact.object_value


def _source_version_iri(source_version_id: str) -> str:
    return f"urn:aviation-agentic-ai:source-version:{source_version_id}"


def _expand_iri(value: str | None) -> str:
    if value is None:
        return ""
    if "://" in value or value.startswith("urn:"):
        return value
    if ":" in value:
        prefix, local = value.split(":", 1)
        namespace = _PREFIXES.get(prefix)
        if namespace is not None:
            return f"{namespace}{local}"
    return f"urn:aviation-agentic-ai:term:{value}"


def _local_name(iri: str) -> str:
    return iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def _write_models(path: Path, rows: Iterable[Any]) -> None:
    _write_jsonl(
        path,
        [row.model_dump(mode="json") for row in rows],
    )


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "\n".join(
            json.dumps(
                row,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            for row in rows
        )
        + ("\n" if rows else ""),
        encoding="utf-8",
    )


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _file_record(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "byte_count": len(data),
        "record_count": (
            len([line for line in data.splitlines() if line.strip()])
            if path.suffix == ".jsonl"
            else 1
        ),
    }

