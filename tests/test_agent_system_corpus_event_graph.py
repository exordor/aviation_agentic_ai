"""Closed graph traversal over one admitted ATMONTO TMI event."""

from __future__ import annotations

from aviation_agentic_ai.agent_system.contracts import ValidationProfileRef
from aviation_agentic_ai.agent_system.corpus_event_graph import CorpusEventGraphView
from aviation_agentic_ai.agent_system.corpus_store import CorpusFact


RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
GROUND_STOP = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#GroundStopTMI"
)
CONTROLLED_NAS_ELEMENT = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#controlledNASelement"
)
EFFECTIVE_START = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#effectiveStartTime"
)
FORECASTING_AIRPORT = (
    "https://data.nasa.gov/ontologies/atmonto/data#forecastingAirport"
)
SOSA_FEATURE = "http://www.w3.org/ns/sosa/hasFeatureOfInterest"
QUDT_NUMERIC = "http://qudt.org/schema/qudt/numericValue"


PROFILE = ValidationProfileRef(
    profile_id="profile:test",
    profile_checksum="a" * 64,
    layer="decision",
)


def _fact(
    fact_id: str,
    subject: str,
    predicate: str,
    value: str,
    *,
    kind: str = "iri",
    sources: tuple[str, ...] = (),
) -> CorpusFact:
    return CorpusFact(
        fact_id=fact_id,
        subject_iri=subject,
        subject_class_iri="urn:class:Entity",
        predicate_iri=predicate,
        object_kind=kind,
        object_value=value,
        datatype_iri=(
            "http://www.w3.org/2001/XMLSchema#decimal"
            if kind == "literal"
            else None
        ),
        source_ids=list(sources),
        validation_profile=PROFILE,
        evidence_mode="source_text",
        evidence_ref="source:test",
    )


def _event_facts() -> tuple[CorpusFact, ...]:
    event = "urn:event:1"
    airport = "urn:airport:KJFK"
    weather = "urn:weather:taf:1"
    observation = "urn:observation:active"
    result = "urn:result:active"
    return (
        _fact("f01", event, RDF_TYPE, GROUND_STOP, sources=("advisory:1",)),
        _fact(
            "f02",
            event,
            CONTROLLED_NAS_ELEMENT,
            airport,
            sources=("advisory:1",),
        ),
        _fact(
            "f03",
            event,
            EFFECTIVE_START,
            "2026-05-19T21:00:00Z",
            kind="literal",
            sources=("advisory:1",),
        ),
        _fact(
            "f04",
            weather,
            FORECASTING_AIRPORT,
            airport,
            sources=("taf:1",),
        ),
        _fact(
            "f05",
            observation,
            SOSA_FEATURE,
            airport,
            sources=("bts:1",),
        ),
        _fact(
            "f06",
            result,
            QUDT_NUMERIC,
            "20",
            kind="literal",
            sources=("bts:1",),
        ),
    )


def test_graph_view_supports_sorted_incoming_outgoing_and_literal_edges() -> None:
    """Reversing adjacency direction or dropping literal terminals is a query bug."""

    graph = CorpusEventGraphView(tuple(reversed(_event_facts())))

    outgoing = graph.neighbors("urn:event:1", direction="out")
    incoming = graph.neighbors("urn:airport:KJFK", direction="in")
    literal = graph.neighbors(
        "urn:result:active",
        direction="out",
        predicate_iris=(QUDT_NUMERIC,),
    )

    assert [edge.fact_id for edge in outgoing] == ["f01", "f02", "f03"]
    assert {edge.fact_id for edge in incoming} == {"f02", "f04", "f05"}
    assert [(edge.object_kind, edge.object_value) for edge in literal] == [
        ("literal", "20")
    ]


def test_graph_view_exposes_all_formal_facts_and_predicate_filters() -> None:
    """The runtime graph tool must not be limited to one registered path shape."""

    graph = CorpusEventGraphView(_event_facts())

    assert {edge.fact_id for edge in graph.edges()} == {
        fact.fact_id for fact in _event_facts()
    }
    assert {
        edge.fact_id
        for edge in graph.edges(predicate_iris=(CONTROLLED_NAS_ELEMENT,))
    } == {"f02"}


def test_graph_view_is_strictly_limited_to_supplied_event_facts() -> None:
    """The corpus store, not a hard-coded path, owns event isolation."""

    graph = CorpusEventGraphView(
        tuple(fact for fact in _event_facts() if fact.fact_id != "f05")
    )

    assert "f05" not in {edge.fact_id for edge in graph.edges()}
    assert {edge.fact_id for edge in graph.edges()} == {
        fact.fact_id for fact in _event_facts() if fact.fact_id != "f05"
    }
