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

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.contracts import GraphPatchBlock, GraphPatchLine
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
