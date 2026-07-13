from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import quote

from rdflib import DCTERMS, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef

from aviation_agentic_ai.cross_source.contracts import (
    AlignmentCandidate,
    AlignmentDecision,
    AlignmentStatus,
    CanonicalEntity,
    CrossSourceLink,
    Mention,
    TermConcept,
)
from aviation_agentic_ai.cross_source.graph.neo4j import (
    Neo4jArtifacts,
    build_neo4j_projection,
    write_neo4j_projection,
)


CS = Namespace("urn:aviation-agentic-ai:cross-source:")
PROV = Namespace("http://www.w3.org/ns/prov#")


@dataclass(frozen=True)
class GraphArtifacts:
    canonical_path: Path
    audit_path: Path
    canonical_triples: int
    audit_triples: int
    neo4j: Neo4jArtifacts


def _record_uri(source_id: str) -> URIRef:
    return URIRef(f"urn:aviation-agentic-ai:source-record:{quote(source_id, safe='')}")


def _mention_uri(mention_id: str) -> URIRef:
    return URIRef(f"urn:aviation-agentic-ai:alignment-mention:{quote(mention_id, safe='')}")


def _decision_uri(trace_id: str) -> URIRef:
    return URIRef(f"urn:aviation-agentic-ai:alignment-decision:{quote(trace_id, safe='')}")


def _add_registries(
    graph: Graph,
    facilities: Iterable[CanonicalEntity],
    terms: Iterable[TermConcept],
) -> None:
    for facility in facilities:
        subject = URIRef(facility.entity_id)
        graph.add((subject, RDF.type, CS.CanonicalFacility))
        graph.add((subject, CS.entityType, Literal(facility.entity_type.value)))
        graph.add((subject, RDFS.label, Literal(facility.preferred_label)))
        for code in facility.codes:
            code_node = URIRef(
                f"{facility.entity_id}:code:{quote(code.scheme, safe='')}:{quote(code.value, safe='')}"
            )
            graph.add((subject, CS.hasCode, code_node))
            graph.add((code_node, CS.codeScheme, Literal(code.scheme)))
            graph.add((code_node, RDF.value, Literal(code.value)))
        for source_ref in facility.source_refs:
            graph.add((subject, DCTERMS.source, Literal(source_ref)))

    for term in terms:
        subject = URIRef(term.term_id)
        graph.add((subject, RDF.type, CS.OperationalTerm))
        graph.add((subject, RDFS.label, Literal(term.preferred_label)))
        graph.add((subject, CS.abbreviation, Literal(term.abbreviation)))
        graph.add((subject, CS.termCategory, Literal(term.term_category.value)))
        for source_ref in term.source_refs:
            graph.add((subject, DCTERMS.source, Literal(source_ref)))


def _add_accepted_alignments(
    graph: Graph,
    mentions: Iterable[Mention],
    decisions: Iterable[AlignmentDecision],
) -> None:
    mention_by_id = {mention.mention_id: mention for mention in mentions}
    for decision in decisions:
        if decision.status is not AlignmentStatus.ACCEPTED or not decision.target_id:
            continue
        mention = mention_by_id[decision.mention_id]
        subject = _mention_uri(mention.mention_id)
        graph.add((subject, RDF.type, CS.AcceptedAlignmentMention))
        graph.add((subject, CS.surfaceForm, Literal(mention.surface_form)))
        graph.add((subject, CS.normalizedForm, Literal(mention.normalized_form)))
        graph.add((subject, CS.denotes, URIRef(decision.target_id)))
        graph.add((subject, PROV.wasDerivedFrom, _record_uri(mention.source_id)))
        graph.add((subject, CS.gateScore, Literal(decision.gate_score, datatype=XSD.decimal)))
        graph.add((subject, CS.snapshotSet, Literal(decision.snapshot_set_id)))


def _add_links(graph: Graph, links: Iterable[CrossSourceLink]) -> None:
    for link in links:
        subject = _record_uri(link.subject_id)
        obj = _record_uri(link.object_id)
        predicate = CS[link.predicate]
        link_node = URIRef(f"urn:aviation-agentic-ai:cross-source-link:{link.link_id}")
        graph.add((subject, predicate, obj))
        graph.add((link_node, RDF.type, CS.CrossSourceAssociation))
        graph.add((link_node, CS.linkSubject, subject))
        graph.add((link_node, CS.linkPredicate, predicate))
        graph.add((link_node, CS.linkObject, obj))
        graph.add((link_node, CS.linkMethod, Literal(link.link_method)))
        graph.add((link_node, CS.facility, URIRef(link.facility_id)))
        graph.add((link_node, CS.causalClaim, Literal(False)))
        for source_ref in link.authority_sources:
            graph.add((link_node, DCTERMS.source, Literal(source_ref)))


def _add_audit_records(
    graph: Graph,
    mentions: Iterable[Mention],
    candidates: Iterable[AlignmentCandidate],
    decisions: Iterable[AlignmentDecision],
) -> None:
    for mention in mentions:
        subject = _mention_uri(mention.mention_id)
        graph.add((subject, RDF.type, CS.AlignmentMention))
        graph.add((subject, CS.surfaceForm, Literal(mention.surface_form)))
        graph.add((subject, CS.mentionType, Literal(mention.mention_type.value)))
        graph.add((subject, PROV.wasDerivedFrom, _record_uri(mention.source_id)))
        graph.add((subject, CS.evidenceText, Literal(mention.evidence_text)))
    for index, candidate in enumerate(candidates):
        subject = URIRef(
            "urn:aviation-agentic-ai:alignment-candidate:"
            f"{quote(candidate.mention_id, safe='')}:{index}"
        )
        graph.add((subject, RDF.type, CS.AlignmentCandidate))
        graph.add((subject, CS.forMention, _mention_uri(candidate.mention_id)))
        graph.add((subject, CS.candidateTarget, URIRef(candidate.target_id)))
        graph.add((subject, CS.gateScore, Literal(candidate.gate_score, datatype=XSD.decimal)))
        graph.add((subject, CS.rationale, Literal(candidate.rationale)))
    for decision in decisions:
        subject = _decision_uri(decision.trace_id)
        graph.add((subject, RDF.type, CS.AlignmentDecision))
        graph.add((subject, CS.forMention, _mention_uri(decision.mention_id)))
        graph.add((subject, CS.decisionStatus, Literal(decision.status.value)))
        graph.add((subject, CS.decisionMethod, Literal(decision.method.value)))
        graph.add((subject, CS.gateScore, Literal(decision.gate_score, datatype=XSD.decimal)))
        graph.add((subject, CS.rationale, Literal(decision.decision_reason)))
        graph.add((subject, CS.snapshotSet, Literal(decision.snapshot_set_id)))
        if decision.target_id:
            graph.add((subject, CS.acceptedTarget, URIRef(decision.target_id)))


def materialize_graphs(
    *,
    facilities: Iterable[CanonicalEntity],
    terms: Iterable[TermConcept],
    mentions: Iterable[Mention],
    candidates: Iterable[AlignmentCandidate],
    decisions: Iterable[AlignmentDecision],
    links: Iterable[CrossSourceLink],
    canonical_path: str | Path,
    audit_path: str | Path,
) -> GraphArtifacts:
    facilities = tuple(facilities)
    terms = tuple(terms)
    mentions = tuple(mentions)
    candidates = tuple(candidates)
    decisions = tuple(decisions)
    links = tuple(links)
    canonical_target = Path(canonical_path)
    audit_target = Path(audit_path)
    canonical_target.parent.mkdir(parents=True, exist_ok=True)
    audit_target.parent.mkdir(parents=True, exist_ok=True)

    canonical = Graph()
    canonical.bind("cs", CS)
    canonical.bind("prov", PROV)
    _add_registries(canonical, facilities, terms)
    _add_accepted_alignments(canonical, mentions, decisions)
    _add_links(canonical, links)

    audit = Graph()
    audit.bind("cs", CS)
    audit.bind("prov", PROV)
    _add_audit_records(audit, mentions, candidates, decisions)
    _add_links(audit, links)

    canonical.serialize(destination=canonical_target, format="turtle")
    audit.serialize(destination=audit_target, format="turtle")
    snapshot_set_ids = {decision.snapshot_set_id for decision in decisions}
    if len(snapshot_set_ids) != 1:
        raise ValueError("Neo4j projection requires exactly one alignment snapshot set")
    neo4j_nodes, neo4j_relationships = build_neo4j_projection(
        facilities=facilities,
        terms=terms,
        mentions=mentions,
        decisions=decisions,
        links=links,
        snapshot_set_id=next(iter(snapshot_set_ids)),
    )
    neo4j = write_neo4j_projection(
        nodes=neo4j_nodes,
        relationships=neo4j_relationships,
        nodes_path=canonical_target.parent / "neo4j_nodes.jsonl",
        relationships_path=canonical_target.parent / "neo4j_relationships.jsonl",
    )
    return GraphArtifacts(
        canonical_path=canonical_target,
        audit_path=audit_target,
        canonical_triples=len(canonical),
        audit_triples=len(audit),
        neo4j=neo4j,
    )
