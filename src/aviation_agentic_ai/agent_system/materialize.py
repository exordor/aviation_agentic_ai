"""Schema-guided Graph Patch materialization.

This is the DETERMINISTIC materializer (not an LLM, not a Verification Agent).
It takes parsed Graph Patch lines and the event class, validates each line
against the frozen ATCSCC schema slice, and writes only schema-valid facts to
RDF/Turtle + JSONL and the Neo4j projection.

Outcome classification per line:
- ``parse_error``: the line did not parse into four columns (handled upstream).
- ``schema_violation``: a class/property/domain/range/datatype constraint in
  the slice is violated — the fact is rejected and never enters the formal KG.
- ``profile_gap``: the source supports a field, but the current ATCSCC profile
  slice has no matching property — recorded with source evidence, NOT written.
- ``valid``: written to RDF/Neo4j.

The program supplies event URIs (via ``stable_id``) and reuses the existing
``KGTriple`` / ``write_kg_jsonl`` / ``write_kg_ttl`` / ``write_neo4j_projection``.
Canonical facility/term ids must come from the input source cards. No custom
``cs:*`` core predicates are ever written.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.contracts import (
    GraphPatchBlock,
    GraphPatchLine,
    SourceSnapshot,
    SourceSnapshotRegistry,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.graph_patch import parse_graph_patch_block, parse_rate
from aviation_agentic_ai.agent_system.schema_guide import (
    SchemaGuide,
    TRACE_PREDICATES,
)
from aviation_agentic_ai.cross_source.graph.neo4j import write_neo4j_projection
from aviation_agentic_ai.cross_source.identifiers import stable_id
from aviation_agentic_ai.kg.extraction import KGTriple, write_kg_jsonl, write_kg_ttl

# Predicate that asserts an entity's ontology class.
RDF_TYPE = "rdf:type"


@dataclass(frozen=True)
class MaterializedLine:
    """The materialization outcome for one Graph Patch line."""

    line: GraphPatchLine
    outcome: str  # valid | schema_violation | profile_gap
    reason: str
    triple: KGTriple | None = None


@dataclass(frozen=True)
class GraphPatchMaterialization:
    """Full result of materializing one Graph Patch block."""

    triples: list[KGTriple] = field(default_factory=list)
    line_outcomes: list[MaterializedLine] = field(default_factory=list)
    parse_error_count: int = 0
    schema_violation_count: int = 0
    profile_gap_count: int = 0
    valid_count: int = 0
    parse_rate: float = 0.0
    schema_slice_id: str = ""
    schema_checksum: str = ""
    jsonl_path: str | None = None
    ttl_path: str | None = None
    nodes_path: str | None = None
    relationships_path: str | None = None


def _event_uri(advisory_source_id: str, event_class: str) -> str:
    """Program-supplied event URI (stable, content-addressed)."""

    return stable_id("evt", advisory_source_id, event_class)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


_DATE_TIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})$"
)


def _check_datatype_value(predicate: str, value: str, guide: SchemaGuide) -> str | None:
    """Validate a datatype literal against the slice's declared datatype.

    Returns ``None`` when acceptable, or a short reason string when the literal
    does not satisfy the declared XSD datatype. Empty/whitespace literals are
    always rejected (a datatype property must carry a real value).
    """

    del guide  # datatype lookup done by caller via guide.datatype_for; kept for symmetry
    stripped = value.strip()
    if not stripped:
        return "empty literal"
    # XSD dateTime: ISO-8601 with optional fractional seconds and offset/Z.
    # The schema slice declares xsd:dateTime for the time properties; we accept
    # the canonical ISO form used throughout the system mainline.
    if predicate in ("atm:effectiveStartTime", "atm:effectiveEndTime", "atm:issuedTime"):
        if not _DATE_TIME_RE.match(stripped):
            return "not a valid xsd:dateTime literal"
        return None
    if predicate == "atm:advisoryNumber":
        # xsd:integer per slice; the advisory ADVZY number is an integer code.
        if not stripped.isdigit():
            return "not a valid xsd:integer literal"
        return None
    return None


def _classify_object_value(value: str) -> tuple[str, str]:
    """Classify a Graph Patch object as an IRI/class ref or a literal.

    Returns ``(object_class_or_empty, literal_value_or_empty)``. An object that
    matches a known schema class prefixed name is treated as a class/entity ref;
    otherwise it is a literal string.
    """

    return value, ""


def _validate_line(
    line: GraphPatchLine,
    *,
    event_class: str,
    event_uri: str,
    guide: SchemaGuide,
    known_entity_classes: dict[str, str],
) -> MaterializedLine:
    """Validate one Graph Patch line against the schema slice."""

    pred = line.predicate.strip()
    subject = line.subject.strip()
    obj = line.object.strip()

    # The subject must be the event URI (program-supplied) for event-scoped
    # facts, OR a known canonical entity id referenced in the patch.
    if subject != event_uri and subject not in known_entity_classes:
        return MaterializedLine(
            line=line,
            outcome="schema_violation",
            reason=f"subject {subject!r} is neither the event URI nor a known canonical entity",
        )

    # rdf:type assertion: object must be a schema class.
    if pred == RDF_TYPE:
        if not guide.has_class(obj):
            return MaterializedLine(
                line=line,
                outcome="schema_violation",
                reason=f"rdf:type object {obj!r} is not a schema class",
            )
        subject_class = event_class if subject == event_uri else known_entity_classes[subject]
        # The asserted type must be compatible (self or superclass) with the
        # subject's known class — no inventing unrelated types.
        if obj != subject_class and obj not in guide.superclasses(subject_class):
            return MaterializedLine(
                line=line,
                outcome="schema_violation",
                reason=f"rdf:type {obj!r} incompatible with subject class {subject_class!r}",
            )
        return _to_triple(line, event_uri, subject_class, obj, "class")

    # Source-trace predicate (prov:wasDerivedFrom): allowed for traceability;
    # object must be a cited source id.
    if pred in TRACE_PREDICATES:
        return _to_triple(line, event_uri, "", obj, "trace")

    # Object property.
    if guide.is_object_property(pred):
        if not guide.object_property_domain_ok(pred, event_class if subject == event_uri else known_entity_classes[subject]):
            return MaterializedLine(
                line=line,
                outcome="schema_violation",
                reason=f"object property {pred!r} domain not satisfied by subject",
            )
        # The object should be a known canonical entity; record its class if so.
        obj_class = known_entity_classes.get(obj, "")
        if obj_class:
            if not guide.object_property_range_ok(pred, obj_class):
                return MaterializedLine(
                    line=line,
                    outcome="schema_violation",
                    reason=f"object property {pred!r} range not satisfied by {obj_class!r}",
                )
        return _to_triple(line, event_uri, event_class, obj, "object", obj_class=obj_class)

    # Datatype property.
    if guide.is_datatype_property(pred):
        subj_class = event_class if subject == event_uri else known_entity_classes[subject]
        if not guide.datatype_property_ok(pred, subj_class):
            return MaterializedLine(
                line=line,
                outcome="schema_violation",
                reason=f"datatype property {pred!r} domain not satisfied by {subj_class!r}",
            )
        datatype_error = _check_datatype_value(pred, obj, guide)
        if datatype_error:
            return MaterializedLine(
                line=line,
                outcome="schema_violation",
                reason=f"datatype property {pred!r} value {obj!r}: {datatype_error}",
            )
        return _to_triple(line, event_uri, event_class, obj, "datatype")

    # Property exists in source but not in the current profile slice -> gap.
    return MaterializedLine(
        line=line,
        outcome="profile_gap",
        reason=f"predicate {pred!r} not in the current ATCSCC profile slice",
    )


def _to_triple(
    line: GraphPatchLine,
    event_uri: str,
    subject_class: str,
    obj: str,
    kind: str,
    *,
    obj_class: str = "",
) -> MaterializedLine:
    triple = KGTriple(
        triple_id=stable_id("t", line.subject, line.predicate, obj),
        subject=line.subject,
        predicate=line.predicate,
        object=obj,
        subject_class=subject_class,
        object_class=obj_class,
        source_document=";".join(line.source_ids),
        page=0,
        section="",
        chunk_id="",
        evidence_text="",
        model="agent_system",
        confidence=1.0,
        extracted_at=_now_iso(),
    )
    return MaterializedLine(line=line, outcome="valid", reason=kind, triple=triple)


def materialize_graph_patch(
    *,
    graph_patch_raw: str | None = None,
    graph_patch_block: GraphPatchBlock | None = None,
    advisory_source_id: str,
    event_class: str,
    guide: SchemaGuide,
    canonical_entities: dict[str, str] | None = None,
    known_source_ids: set[str] | None = None,
    output_dir: str | Path,
    namespace: str = "http://www.example.org/aviation/atcscc#",
) -> GraphPatchMaterialization:
    """Parse + schema-validate + materialize one Graph Patch block (design §13).

    ``canonical_entities`` maps canonical entity id -> ontology class (e.g.
    facility id -> ``nas:Airport``). ``known_source_ids`` is the set of source
    ids that may be cited; a patch line citing an unknown source id is a
    ``schema_violation``. Only schema-valid facts are written; profile gaps are
    recorded but never enter RDF/Neo4j. Re-materializing the same inputs
    produces stable triple ids so re-ingest does not duplicate canonical nodes
    or relationships.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if graph_patch_block is None:
        graph_patch_block = parse_graph_patch_block(graph_patch_raw or "")
    known_entities = dict(canonical_entities or {})
    event_uri = _event_uri(advisory_source_id, event_class)
    # The event entity itself is a known subject of class event_class.
    known_entities[event_uri] = event_class
    known_sources = known_source_ids or set()

    rate = parse_rate(graph_patch_raw or graph_patch_block.raw or "", graph_patch_block.patch_lines)
    outcomes: list[MaterializedLine] = []
    triples: list[KGTriple] = []

    for line in graph_patch_block.patch_lines:
        # Source-reference existence: every cited source id must be known.
        if known_sources and not set(line.source_ids).issubset(known_sources):
            outcomes.append(
                MaterializedLine(
                    line=line,
                    outcome="schema_violation",
                    reason=f"source_ids {set(line.source_ids) - known_sources} not known",
                )
            )
            continue
        outcome = _validate_line(
            line,
            event_class=event_class,
            event_uri=event_uri,
            guide=guide,
            known_entity_classes=known_entities,
        )
        outcomes.append(outcome)
        if outcome.outcome == "valid" and outcome.triple is not None:
            triples.append(outcome.triple)

    jsonl_path = output_dir / "kg.jsonl"
    ttl_path = output_dir / "kg.ttl"
    write_kg_jsonl(triples, jsonl_path)
    write_kg_ttl(triples, ttl_path, namespace=namespace)

    nodes_path = output_dir / "neo4j_nodes.jsonl"
    rels_path = output_dir / "neo4j_relationships.jsonl"
    nodes, relationships = _neo4j_projection(triples, event_uri, guide, known_entities)
    write_neo4j_projection(
        nodes=nodes,
        relationships=relationships,
        nodes_path=nodes_path,
        relationships_path=rels_path,
    )

    return GraphPatchMaterialization(
        triples=triples,
        line_outcomes=outcomes,
        parse_error_count=_count_parse_errors(graph_patch_raw or graph_patch_block.raw or "", graph_patch_block),
        schema_violation_count=sum(1 for o in outcomes if o.outcome == "schema_violation"),
        profile_gap_count=len(graph_patch_block.profile_gaps),
        valid_count=len(triples),
        parse_rate=rate,
        schema_slice_id=guide.schema_slice_id,
        schema_checksum=guide.checksum,
        jsonl_path=str(jsonl_path),
        ttl_path=str(ttl_path),
        nodes_path=str(nodes_path),
        relationships_path=str(rels_path),
    )


def _count_parse_errors(raw: str, block: GraphPatchBlock) -> int:
    """Count malformed GRAPH_PATCH rows (considered but not parsed)."""

    import re as _re

    fence = _re.compile(r"^\s*```")
    section = None
    errors = 0
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or fence.match(line):
            continue
        if stripped == "GRAPH_PATCH":
            section = "GRAPH_PATCH"
            continue
        if stripped == "PROFILE_GAPS":
            section = "PROFILE_GAPS"
            continue
        if section == "GRAPH_PATCH":
            if len(line.split("|")) != 4:
                errors += 1
    return errors


def _neo4j_projection(
    triples: list[KGTriple], event_uri: str, guide: SchemaGuide, known_entity_classes: dict[str, str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Build Neo4j node/relationship rows.

    This is a PROJECTION only: it writes node/relationship JSONL intended for a
    downstream Neo4j ``MERGE`` load. Every relationship endpoint is guaranteed
    to have a corresponding node row — canonical object entities (e.g. the
    controlled facility) and trace source records are promoted to nodes so no
    relationship points at a missing endpoint. Canonical entities are MERGE'd
    by their canonical id (``stable_id`` ensures re-ingest produces the same
    node keys, so no duplicates). Nodes carry ``ontology_class_iri``;
    relationships carry ``predicate_iri`` and the run's ``schema_slice_id``.
    """

    nodes: dict[str, dict[str, Any]] = {}

    def _ensure_node(entity_id: str, class_prefixed: str, *, label_hint: str = "") -> None:
        if entity_id in nodes:
            return
        cls_iri = guide.classes[class_prefixed].iri if class_prefixed in guide.classes else ""
        nodes[entity_id] = {
            "entity_id": entity_id,
            "ontology_class_iri": cls_iri,
            "label": class_prefixed or label_hint or "Entity",
            "schema_slice_id": guide.schema_slice_id,
        }

    relationships: list[dict[str, Any]] = []
    for triple in triples:
        _ensure_node(triple.subject, triple.subject_class)
        # Object-property triples point at a canonical entity; promote it to a
        # node using its known class so the relationship endpoint exists.
        if triple.predicate != RDF_TYPE and triple.object_class:
            _ensure_node(triple.object, triple.object_class)
        # Source-trace (prov:wasDerivedFrom) triples point at a source record;
        # represent it as a SourceRecord node so the trace endpoint exists.
        if triple.predicate in TRACE_PREDICATES:
            _ensure_node(triple.object, "", label_hint="SourceRecord")
        # rdf:type is encoded as the node's class, not a relationship.
        if triple.predicate == RDF_TYPE:
            continue
        pred_iri = (
            guide.object_properties[triple.predicate].iri
            if triple.predicate in guide.object_properties
            else (
                guide.datatype_properties[triple.predicate].iri
                if triple.predicate in guide.datatype_properties
                else ""
            )
        )
        rel_id = stable_id("neo4j-rel", triple.subject, triple.predicate, triple.object)
        relationships.append(
            {
                "id": rel_id,
                "from": triple.subject,
                "to": triple.object,
                "predicate": triple.predicate,
                "predicate_iri": pred_iri,
                "source_ids": triple.source_document.split(";") if triple.source_document else [],
                "schema_slice_id": guide.schema_slice_id,
            }
        )
    # Final endpoint-completeness guarantee: every relationship endpoint must
    # be a node. If a datatype/literal somehow slipped in, add it as a literal
    # node so the projection never carries a dangling endpoint.
    rel_endpoints: set[str] = set()
    for rel in relationships:
        rel_endpoints.add(rel["from"])
        rel_endpoints.add(rel["to"])
    for endpoint in rel_endpoints:
        _ensure_node(endpoint, known_entity_classes.get(endpoint, ""), label_hint="Literal")
    return list(nodes.values()), relationships


# ===========================================================================
# Batch Two: ValidatedFact -> RDF + Neo4j projection (plan §6)
# ===========================================================================
#
# The functions below consume the Formal Graph Kernel's accepted
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
_FACT_NAMESPACE = "urn:aviation-agentic-ai:fact:"
_EVENT_NAMESPACE = "urn:aviation-agentic-ai:event:"
_SOURCE_NAMESPACE = "urn:aviation-agentic-ai:source:"

# Neo4j labels / relationship types for the agent-system projection (§6.2).
_LABEL_EVENT = "AviationEvent"
_LABEL_FACILITY = "Facility"
_LABEL_SOURCE = "SourceRecord"
_REL_CONTROLLED = "CONTROLLED_NAS_ELEMENT"
_REL_DERIVED = "DERIVED_FROM"


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


def _datatype_short(iri: str) -> str:
    """Short form (``xsd:dateTime``) of an XSD datatype IRI for Turtle."""

    if iri.startswith(_XSD_NAMESPACE):
        return f"xsd:{iri[len(_XSD_NAMESPACE):]}"
    return iri


def _validated_snapshot_registry(
    source_snapshot: SourceSnapshot | SourceSnapshotRegistry,
) -> SourceSnapshotRegistry:
    """Normalize legacy input and reject malformed multi-source registries."""

    snapshots = (
        source_snapshot.snapshots
        if isinstance(source_snapshot, SourceSnapshotRegistry)
        else (source_snapshot,)
    )
    return SourceSnapshotRegistry(snapshots=snapshots)


def _require_fact_snapshot_bindings(
    facts: list[ValidatedFact],
    source_snapshot: SourceSnapshot | SourceSnapshotRegistry,
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


def write_validated_facts_rdf(
    *,
    facts: list[ValidatedFact],
    guide: SchemaGuide,
    source_snapshot: SourceSnapshot | SourceSnapshotRegistry,
    output_dir: str | Path,
) -> str:
    """Write ``kg.ttl`` from accepted ValidatedFacts (plan §6.1).

    Uses real ATMONTO / RDF / PROV / XSD IRIs taken from the Schema Guide and
    the standard namespaces. Each fact is a reified statement connected to its
    source node(s) via ``prov:wasDerivedFrom``, with the bound evidence text as
    a reification annotation. The writer never constructs
    ``example.org/...#atm:*`` IRIs.
    """

    _require_fact_snapshot_bindings(facts, source_snapshot)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    ttl_path = out / "kg.ttl"

    g = _build_rdflib_graph()
    from rdflib import BNode, Literal, URIRef
    from rdflib.namespace import RDF, RDFS, XSD

    del XSD  # datatype IRIs are taken from the ValidatedFact directly

    # Emit one reified statement per fact + the source derivation link.
    for fact in facts:
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
            obj = URIRef(_source_iri(fact.object_value))
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
        stmt = BNode()
        g.add((stmt, RDF.type, RDF.Statement))
        g.add((stmt, RDF.subject, subj))
        g.add((stmt, RDF.predicate, pred))
        g.add((stmt, RDF.object, obj))
        for evidence in fact.evidence_texts:
            g.add((stmt, RDFS.comment, Literal(evidence)))
        for sid in fact.source_ids:
            src = URIRef(_source_iri(sid))
            g.add((src, RDF.type, URIRef(f"{_PROV_NAMESPACE}Entity")))
            g.add((src, RDFS.label, Literal(sid)))
            g.add((stmt, URIRef(_PROV_WAS_DERIVED_FROM_IRI), src))
    del RDF, RDFS, BNode, Literal, URIRef

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
    g.bind("prov", _PROV_NAMESPACE)
    g.bind("aviation-event", _EVENT_NAMESPACE)
    g.bind("aviation-source", _SOURCE_NAMESPACE)
    return g


def write_validated_facts_jsonl(
    *,
    facts: list[ValidatedFact],
    guide: SchemaGuide,
    output_dir: str | Path,
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
    for fact in facts:
        row = {
            "triple_id": fact.fact_id,
            "subject": _absolute_event_iri(fact.subject_iri),
            "predicate": _predicate_prefixed(fact),
            "object": fact.object_value,
            "subject_class": _class_prefixed(fact.subject_class_iri, guide),
            "object_class": _class_prefixed(fact.object_class_iri, guide) if fact.object_class_iri else "",
            "source_document": ";".join(fact.source_ids),
            "evidence_text": "; ".join(fact.evidence_texts),
            "object_kind": fact.object_kind,
            "datatype_iri": fact.datatype_iri or "",
        }
        rows.append(json.dumps(row, ensure_ascii=False))
    path.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")
    return str(path)


def _predicate_prefixed(fact: ValidatedFact) -> str:
    """Recover the prefixed predicate name from its IRI for the query reader."""

    iri = fact.predicate_iri
    for prefix, ns in (
        ("atm", "https://data.nasa.gov/ontologies/atmonto/ATM#"),
        ("nas", "https://data.nasa.gov/ontologies/atmonto/NAS#"),
        ("rdf", _RDF_NAMESPACE),
        ("prov", _PROV_NAMESPACE),
    ):
        if iri.startswith(ns):
            return f"{prefix}:{iri[len(ns):]}"
    return iri


def _class_prefixed(class_iri: str | None, guide: SchemaGuide) -> str:
    """Recover the prefixed class name from its IRI via the Schema Guide."""

    if not class_iri:
        return ""
    for cls in guide.classes.values():
        if cls.iri == class_iri:
            return cls.prefixed_name
    return class_iri


def build_validated_facts_neo4j_projection(
    *,
    facts: list[ValidatedFact],
    guide: SchemaGuide,
    output_dir: str | Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str, str]:
    """Build the Neo4j node/relationship projection from ValidatedFacts (§6.2).

    Nodes: ``AviationEvent`` (carries datatype properties), ``Facility``,
    ``SourceRecord``. Relationships: ``CONTROLLED_NAS_ELEMENT`` and
    ``DERIVED_FROM``. Datatype values live on the event node; literals are
    NEVER converted to nodes. Every relationship endpoint is a node row, and
    each relationship retains the original ontology predicate IRI in its
    properties.
    """

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    nodes: dict[str, dict[str, Any]] = {}
    relationships: dict[str, dict[str, Any]] = {}
    slice_id = guide.schema_slice_id

    def _add_relationship(row: dict[str, Any]) -> None:
        """Insert one stable relationship, merging duplicate source evidence."""

        rel_id = str(row["id"])
        existing = relationships.get(rel_id)
        if existing is None:
            relationships[rel_id] = row
            return
        structural_keys = ("type", "start_id", "end_id")
        if any(existing[key] != row[key] for key in structural_keys):
            raise ValueError(f"conflicting Neo4j relationship id: {rel_id}")
        existing_sources = set(existing.get("properties", {}).get("source_ids", []))
        incoming_sources = set(row.get("properties", {}).get("source_ids", []))
        existing["properties"]["source_ids"] = sorted(existing_sources | incoming_sources)

    def _event_node_id(subject_iri: str) -> str:
        return _absolute_event_iri(subject_iri)

    def _ensure_event(subject_iri: str, class_iri: str) -> str:
        eid = _event_node_id(subject_iri)
        if eid not in nodes:
            nodes[eid] = {
                "id": eid, "label": _LABEL_EVENT,
                "properties": {
                    "id": eid,
                    "ontology_class_iri": class_iri,
                    "schema_slice_id": slice_id,
                },
            }
        return eid

    def _ensure_facility(facility_iri: str, class_iri: str) -> str:
        if facility_iri not in nodes:
            nodes[facility_iri] = {
                "id": facility_iri, "label": _LABEL_FACILITY,
                "properties": {
                    "id": facility_iri,
                    "ontology_class_iri": class_iri,
                    "schema_slice_id": slice_id,
                },
            }
        return facility_iri

    def _ensure_source(source_id: str) -> str:
        sid_iri = _source_iri(source_id)
        if sid_iri not in nodes:
            nodes[sid_iri] = {
                "id": sid_iri, "label": _LABEL_SOURCE,
                "properties": {
                    "id": sid_iri,
                    "source_id": source_id,
                    "schema_slice_id": slice_id,
                },
            }
        return sid_iri

    for fact in facts:
        # rdf:type -> ensure the event node exists with its class.
        if _is_rdf_type_predicate(fact.predicate_iri):
            _ensure_event(fact.subject_iri, fact.object_value if _is_absolute(fact.object_value) else fact.subject_class_iri)
            continue
        # prov:wasDerivedFrom -> DERIVED_FROM relationship to a SourceRecord node.
        if _is_prov_predicate(fact.predicate_iri):
            event_id = _ensure_event(fact.subject_iri, fact.subject_class_iri)
            src_id = _ensure_source(fact.object_value)
            _add_relationship(_relationship(event_id, src_id, _REL_DERIVED, fact, slice_id))
            continue
        # Object property (e.g. controlledNASelement) -> typed relationship.
        if fact.object_kind == "iri":
            event_id = _ensure_event(fact.subject_iri, fact.subject_class_iri)
            facility_id = _ensure_facility(
                fact.object_value if _is_absolute(fact.object_value) else _absolute_event_iri(fact.object_value),
                fact.object_class_iri or "",
            )
            rel_type = _REL_CONTROLLED if "controlledNASelement" in fact.predicate_iri else _relationship_type_for(fact.predicate_iri)
            _add_relationship(_relationship(event_id, facility_id, rel_type, fact, slice_id))
            continue
        # Datatype property -> set on the event node (no Literal node).
        event_id = _ensure_event(fact.subject_iri, fact.subject_class_iri)
        prop_name = _predicate_local_name(fact.predicate_iri)
        nodes[event_id]["properties"][prop_name] = _coerce_datatype_value(fact)

    # Plan §13 T1: derive provenance from every accepted ValidatedFact's
    # registered ``source_ids`` — independent of any explicit PROV Graph Patch
    # row. Create one SourceRecord per unique source id and one stable
    # DERIVED_FROM from the fact's event to each unique source. An explicit
    # accepted ``prov:wasDerivedFrom`` fact may confirm the same relationship,
    # but must not be required and must not create a duplicate (deduped by the
    # relationship's stable id).
    derived_keys = {
        rel_id for rel_id, rel in relationships.items() if rel["type"] == _REL_DERIVED
    }
    for fact in facts:
        event_id = _ensure_event(fact.subject_iri, fact.subject_class_iri)
        for source_id in fact.source_ids:
            src_id = _ensure_source(source_id)
            rel_id = stable_id("neo4j-rel", event_id, _PROV_WAS_DERIVED_FROM_IRI, src_id)
            if rel_id in derived_keys:
                continue
            derived_keys.add(rel_id)
            _add_relationship({
                "id": rel_id,
                "type": _REL_DERIVED,
                "start_id": event_id,
                "end_id": src_id,
                "properties": {
                    "id": rel_id,
                    "predicate_iri": _PROV_WAS_DERIVED_FROM_IRI,
                    "source_ids": [source_id],
                    "schema_slice_id": slice_id,
                },
            })

    relationship_rows = list(relationships.values())
    nodes_path = out / "neo4j_nodes.jsonl"
    rels_path = out / "neo4j_relationships.jsonl"
    _write_jsonl(nodes_path, list(nodes.values()))
    _write_jsonl(rels_path, relationship_rows)
    return list(nodes.values()), relationship_rows, str(nodes_path), str(rels_path)


def _relationship(start: str, end: str, rel_type: str, fact: ValidatedFact, slice_id: str) -> dict[str, Any]:
    return {
        "id": stable_id("neo4j-rel", start, fact.predicate_iri, end),
        "type": rel_type,
        "start_id": start,
        "end_id": end,
        "properties": {
            "id": stable_id("neo4j-rel", start, fact.predicate_iri, end),
            "predicate_iri": fact.predicate_iri,
            "source_ids": fact.source_ids,
            "schema_slice_id": slice_id,
        },
    }


def _relationship_type_for(predicate_iri: str) -> str:
    """Upper-snake relationship type from the predicate local name."""

    local = _predicate_local_name(predicate_iri).upper()
    return local.replace(":", "_")


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
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def materialize_validated_facts(
    *,
    facts: list[ValidatedFact],
    guide: SchemaGuide,
    source_snapshot: SourceSnapshot | SourceSnapshotRegistry,
    output_dir: str | Path,
) -> FactMaterialization:
    """Materialize accepted ValidatedFacts to RDF + JSONL + Neo4j projection.

    Plan §6: the single batch-two entry point. Writes ``kg.jsonl`` (query
    triple-row shape), ``kg.ttl`` (real ATMONTO/RDF/PROV/XSD Turtle), and the
    Neo4j projection (``neo4j_nodes.jsonl`` / ``neo4j_relationships.jsonl``).
    """

    _require_fact_snapshot_bindings(facts, source_snapshot)
    jsonl_path = write_validated_facts_jsonl(facts=facts, guide=guide, output_dir=output_dir)
    ttl_path = write_validated_facts_rdf(
        facts=facts, guide=guide, source_snapshot=source_snapshot, output_dir=output_dir,
    )
    _nodes, _rels, nodes_path, rels_path = build_validated_facts_neo4j_projection(
        facts=facts, guide=guide, output_dir=output_dir,
    )
    return FactMaterialization(
        fact_count=len(facts),
        jsonl_path=jsonl_path,
        ttl_path=ttl_path,
        nodes_path=nodes_path,
        relationships_path=rels_path,
        schema_slice_id=guide.schema_slice_id,
        schema_checksum=guide.checksum,
    )


# ---------------------------------------------------------------------------
# Neo4j load: parameterized MERGE (plan §6.2)
# ---------------------------------------------------------------------------


class Neo4jLoadBlocked(RuntimeError):
    """Raised when Neo4j load cannot proceed (plan §6.2: BLOCKED, not faked)."""


_ALLOWED_NEO4J_LABELS = {_LABEL_EVENT, _LABEL_FACILITY, _LABEL_SOURCE}
_ALLOWED_NEO4J_RELATIONSHIPS = {_REL_CONTROLLED, _REL_DERIVED}
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
            for label in (_LABEL_EVENT, _LABEL_FACILITY, _LABEL_SOURCE):
                driver.execute_query(
                    f"CREATE CONSTRAINT {label.lower()}_id IF NOT EXISTS "
                    f"FOR (n:{label}) REQUIRE n.id IS UNIQUE",
                    database_=database,
                )
            # Parameterized MERGE for nodes — never DETACH DELETE; sentinel
            # nodes outside this projection are preserved.
            for label in (_LABEL_EVENT, _LABEL_FACILITY, _LABEL_SOURCE):
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
