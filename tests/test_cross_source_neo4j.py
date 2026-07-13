from datetime import UTC, datetime

from aviation_agentic_ai.cross_source.contracts import (
    AlignmentDecision,
    AlignmentMethod,
    AlignmentStatus,
    CanonicalEntity,
    CodeValue,
    CrossSourceLink,
    EntityType,
    Mention,
    MentionType,
    TimeInterval,
)
from aviation_agentic_ai.cross_source.graph.neo4j import (
    build_neo4j_projection,
    load_neo4j_projection,
    write_neo4j_projection,
)


def _projection():
    facility_id = "urn:test:facility:KJFK"
    facility = CanonicalEntity(
        entity_id=facility_id,
        entity_type=EntityType.AIRPORT,
        preferred_label="JFK",
        codes=[CodeValue(scheme="ICAO", value="KJFK")],
        source_refs=["faa_nasr"],
    )
    mention = Mention(
        mention_id="mention:1",
        source_id="adv:1",
        source_family="atcscc_advisories",
        surface_form="JFK",
        normalized_form="JFK",
        mention_type=MentionType.FACILITY_CODE,
        evidence_text="JFK GS",
        span_start=0,
        span_end=3,
        detected_by="test",
    )
    decision = AlignmentDecision(
        mention_id=mention.mention_id,
        target_id=facility_id,
        status=AlignmentStatus.ACCEPTED,
        method=AlignmentMethod.AUTHORITY_EXACT_CODE,
        gate_score=1,
        authority_sources=["faa_nasr"],
        snapshot_set_id="snapshot:test",
        trace_id="trace:1",
        decision_reason="accepted",
    )
    interval = TimeInterval(
        start=datetime(2026, 5, 20, 12, tzinfo=UTC),
        end=datetime(2026, 5, 20, 13, tzinfo=UTC),
    )
    link = CrossSourceLink(
        link_id="link:1",
        subject_id="adv:1",
        predicate="hasContemporaneousObservation",
        object_id="metar:1",
        link_method="accepted_facility_plus_metar_window",
        facility_id=facility_id,
        advisory_interval=interval,
        evidence_interval=interval,
        authority_sources=["snapshot:test"],
        evidence_text="METAR KJFK TEST",
        causal_claim=False,
    )
    return build_neo4j_projection(
        facilities=[facility],
        terms=[],
        mentions=[mention],
        decisions=[decision],
        links=[link],
        snapshot_set_id="snapshot:test",
    )


def test_neo4j_projection_preserves_canonical_nodes_and_evidence_edges() -> None:
    nodes, relationships = _projection()

    assert {row["label"] for row in nodes} == {
        "AcceptedMention",
        "Facility",
        "SourceRecord",
        "WeatherRecord",
    }
    assert {row["type"] for row in relationships} == {
        "DENOTES",
        "DERIVED_FROM",
        "HAS_CONTEMPORANEOUS_OBSERVATION",
    }
    weather_edge = next(
        row for row in relationships if row["type"] == "HAS_CONTEMPORANEOUS_OBSERVATION"
    )
    assert weather_edge["properties"]["causal_claim"] is False
    assert weather_edge["properties"]["facility_id"] == "urn:test:facility:KJFK"


def test_neo4j_loader_uses_constraint_and_batched_parameterized_queries(tmp_path) -> None:
    nodes, relationships = _projection()
    artifacts = write_neo4j_projection(
        nodes=nodes,
        relationships=relationships,
        nodes_path=tmp_path / "nodes.jsonl",
        relationships_path=tmp_path / "relationships.jsonl",
    )
    calls = []

    class FakeDriver:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def verify_connectivity(self):
            calls.append(("verify", {}))

        def execute_query(self, query, **parameters):
            calls.append((query, parameters))

    counts = load_neo4j_projection(
        uri="bolt://example:7687",
        username="neo4j",
        password="secret",
        database="neo4j",
        nodes_path=artifacts.nodes_path,
        relationships_path=artifacts.relationships_path,
        snapshot_set_id="snapshot:test",
        replace_snapshot=True,
        batch_size=2,
        driver_factory=lambda *_args, **_kwargs: FakeDriver(),
    )

    assert counts == {"nodes": 4, "relationships": 3}
    assert any("CREATE CONSTRAINT" in query for query, _parameters in calls if query != "verify")
    assert any("DETACH DELETE" in query for query, _parameters in calls if query != "verify")
    assert any("UNWIND $rows" in query for query, _parameters in calls if query != "verify")
