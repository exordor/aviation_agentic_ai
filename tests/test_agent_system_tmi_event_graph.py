"""Closed graph traversal over one admitted ATMONTO TMI event."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from aviation_agentic_ai.agent_system.tmi_event_graph import (
    TMIEventGraphView,
    build_tmi_event_graph,
)


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


@dataclass(frozen=True)
class _GraphFact:
    fact_id: str
    subject_iri: str
    predicate_iri: str
    object_kind: Literal["iri", "literal"]
    object_value: str
    datatype_iri: str | None
    source_ids: tuple[str, ...]


def _fact(
    fact_id: str,
    subject: str,
    predicate: str,
    value: str,
    *,
    kind: Literal["iri", "literal"] = "iri",
    sources: tuple[str, ...] = (),
) -> _GraphFact:
    return _GraphFact(
        fact_id=fact_id,
        subject_iri=subject,
        predicate_iri=predicate,
        object_kind=kind,
        object_value=value,
        datatype_iri=(
            "http://www.w3.org/2001/XMLSchema#decimal"
            if kind == "literal"
            else None
        ),
        source_ids=sources,
    )


def _event_facts() -> tuple[_GraphFact, ...]:
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

    graph = TMIEventGraphView(tuple(reversed(_event_facts())))

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

    graph = TMIEventGraphView(_event_facts())

    assert {edge.fact_id for edge in graph.edges()} == {
        fact.fact_id for fact in _event_facts()
    }
    assert {
        edge.fact_id
        for edge in graph.edges(predicate_iris=(CONTROLLED_NAS_ELEMENT,))
    } == {"f02"}


def test_graph_view_is_strictly_limited_to_supplied_event_facts() -> None:
    """The corpus store, not a hard-coded path, owns event isolation."""

    graph = TMIEventGraphView(
        tuple(fact for fact in _event_facts() if fact.fact_id != "f05")
    )

    assert "f05" not in {edge.fact_id for edge in graph.edges()}
    assert {edge.fact_id for edge in graph.edges()} == {
        fact.fact_id for fact in _event_facts() if fact.fact_id != "f05"
    }


def test_store_builder_binds_logical_source_ids_to_graph_edges(
    tmp_path: Path,
) -> None:
    """Dropping the version-to-logical-source join would erase provenance."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )
    from test_agent_system_evidence_store import (
        _minimal_ok_attempt,
        _source_version,
    )

    event_id = "urn:event:store-backed"
    version = _source_version("advisory:store-backed", "GROUND STOP")
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        store.register_source_version(version)
        anchor = store.anchor_source_text(
            version.source_version_id,
            "GROUND STOP",
        )
        store.apply_ingestion_attempt(
            _minimal_ok_attempt(
                version,
                event_id=event_id,
                publication_digest="b" * 64,
                source_anchor_id=anchor.source_anchor_id,
            )
        )

        graph = build_tmi_event_graph(store, event_id)
        edges = graph.edges()

        assert isinstance(graph, TMIEventGraphView)
        assert len(edges) == 1
        assert edges[0].fact_id == f"fact:{event_id}:type"
        assert edges[0].source_ids == ("advisory:store-backed",)
    finally:
        store.close()
