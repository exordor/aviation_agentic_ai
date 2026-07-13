from rdflib import Graph, URIRef

from aviation_agentic_ai.cross_source.contracts import (
    AlignmentCandidate,
    AlignmentDecision,
    AlignmentMethod,
    AlignmentStatus,
    CanonicalEntity,
    CodeValue,
    EntityType,
    Mention,
    MentionType,
)
from aviation_agentic_ai.cross_source.graph.materialize import CS, materialize_graphs


def test_canonical_graph_excludes_quarantined_alignment(tmp_path) -> None:
    facility = CanonicalEntity(
        entity_id="urn:test:facility:KJFK",
        entity_type=EntityType.AIRPORT,
        preferred_label="JFK",
        codes=[CodeValue(scheme="ICAO", value="KJFK")],
    )
    mention = Mention(
        mention_id="mention:1",
        source_id="adv:1",
        source_family="atcscc_advisories",
        surface_form="JFK",
        normalized_form="JFK",
        mention_type=MentionType.FACILITY_CODE,
        evidence_text="JFK",
        span_start=0,
        span_end=3,
        detected_by="test",
    )
    candidate = AlignmentCandidate(
        mention_id=mention.mention_id,
        target_id=facility.entity_id,
        target_label="JFK",
        target_type="airport",
        method=AlignmentMethod.AUTHORITY_EXACT_CODE,
        authority_sources=["faa_nasr"],
        gate_score=1,
        rationale="test",
    )
    decision = AlignmentDecision(
        mention_id=mention.mention_id,
        target_id=facility.entity_id,
        status=AlignmentStatus.QUARANTINED,
        method=AlignmentMethod.CONTEXT_AGENT,
        gate_score=0.7,
        authority_sources=["faa_nasr"],
        snapshot_set_id="snapshot:test",
        trace_id="trace:1",
        decision_reason="quarantined",
    )

    artifacts = materialize_graphs(
        facilities=[facility],
        terms=[],
        mentions=[mention],
        candidates=[candidate],
        decisions=[decision],
        links=[],
        canonical_path=tmp_path / "canonical.ttl",
        audit_path=tmp_path / "audit.ttl",
    )
    canonical = Graph().parse(artifacts.canonical_path)
    audit = Graph().parse(artifacts.audit_path)

    mention_uri = URIRef("urn:aviation-agentic-ai:alignment-mention:mention%3A1")
    assert (mention_uri, CS.denotes, URIRef(facility.entity_id)) not in canonical
    assert (mention_uri, None, None) in audit
