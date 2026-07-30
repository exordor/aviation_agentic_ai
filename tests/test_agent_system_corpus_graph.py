"""Closed graph traversal over one formal decision-case reconstruction."""

from __future__ import annotations

from aviation_agentic_ai.agent_system.contracts import ValidationProfileRef
from aviation_agentic_ai.agent_system.corpus_graph import CorpusGraphView
from aviation_agentic_ai.agent_system.corpus_store import CorpusFact


RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
PROV_SPECIALIZATION_OF = "http://www.w3.org/ns/prov#specializationOf"
PROV_HAD_MEMBER = "http://www.w3.org/ns/prov#hadMember"
PROV_WAS_DERIVED_FROM = "http://www.w3.org/ns/prov#wasDerivedFrom"
FORECASTING_AIRPORT = (
    "https://data.nasa.gov/ontologies/atmonto/data#forecastingAirport"
)
SOSA_FEATURE = "http://www.w3.org/ns/sosa/hasFeatureOfInterest"
SOSA_TIME = "http://www.w3.org/ns/sosa/phenomenonTime"
SOSA_PROPERTY = "http://www.w3.org/ns/sosa/observedProperty"
SOSA_RESULT = "http://www.w3.org/ns/sosa/hasResult"
DCTERMS_TYPE = "http://purl.org/dc/terms/type"
QUDT_NUMERIC = "http://qudt.org/schema/qudt/numericValue"
QUDT_UNIT = "http://qudt.org/schema/qudt/unit"
PHASE_ACTIVE = "urn:aviation-agentic-ai:observation-phase:active"
PHASE_RECOVERY = "urn:aviation-agentic-ai:observation-phase:recovery"


PROFILE = ValidationProfileRef(
    profile_id="profile:test",
    profile_checksum="a" * 64,
    layer="decision_case_core",
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
        evidence_mode="system_membership",
        evidence_ref="trace:test",
    )


def _case_facts() -> tuple[CorpusFact, ...]:
    case = "urn:case:1"
    reconstruction = "urn:reconstruction:1"
    event = "urn:event:1"
    weather = "urn:weather:taf:1"
    airport = "urn:airport:KJFK"
    active_observation = "urn:observation:active"
    recovery_observation = "urn:observation:recovery"
    active_interval = "urn:interval:active"
    recovery_interval = "urn:interval:recovery"
    metric = "urn:metric:scheduled-arrivals"
    active_result = "urn:result:active"
    recovery_result = "urn:result:recovery"
    bts_source = "urn:source:bts"
    return (
        _fact("f01", reconstruction, PROV_SPECIALIZATION_OF, case),
        _fact("f02", reconstruction, PROV_HAD_MEMBER, event, sources=("advisory:1",)),
        _fact("f03", reconstruction, PROV_HAD_MEMBER, weather, sources=("taf:1",)),
        _fact(
            "f04",
            reconstruction,
            PROV_HAD_MEMBER,
            active_observation,
            sources=("bts:1",),
        ),
        _fact(
            "f05",
            reconstruction,
            PROV_HAD_MEMBER,
            recovery_observation,
            sources=("bts:1",),
        ),
        _fact("f06", weather, FORECASTING_AIRPORT, airport, sources=("taf:1",)),
        _fact("f07", active_observation, SOSA_FEATURE, airport, sources=("bts:1",)),
        _fact(
            "f08",
            active_observation,
            SOSA_TIME,
            active_interval,
            sources=("bts:1",),
        ),
        _fact("f09", active_interval, DCTERMS_TYPE, PHASE_ACTIVE, sources=("bts:1",)),
        _fact(
            "f10",
            active_observation,
            SOSA_PROPERTY,
            metric,
            sources=("bts:1",),
        ),
        _fact(
            "f11",
            active_observation,
            SOSA_RESULT,
            active_result,
            sources=("bts:1",),
        ),
        _fact(
            "f12",
            active_observation,
            PROV_WAS_DERIVED_FROM,
            bts_source,
            sources=("bts:1",),
        ),
        _fact("f13", active_result, QUDT_NUMERIC, "20", kind="literal", sources=("bts:1",)),
        _fact("f14", active_result, QUDT_UNIT, "http://qudt.org/vocab/unit/NUM", sources=("bts:1",)),
        _fact("f15", recovery_observation, SOSA_TIME, recovery_interval, sources=("bts:1",)),
        _fact("f16", recovery_interval, DCTERMS_TYPE, PHASE_RECOVERY, sources=("bts:1",)),
        _fact("f17", recovery_observation, SOSA_RESULT, recovery_result, sources=("bts:1",)),
        _fact("f18", recovery_result, QUDT_NUMERIC, "30", kind="literal", sources=("bts:1",)),
    )


def test_graph_view_supports_sorted_incoming_outgoing_and_literal_edges() -> None:
    """Reversing adjacency direction or dropping literal terminals is a query bug."""

    graph = CorpusGraphView(tuple(reversed(_case_facts())))

    outgoing = graph.neighbors("urn:reconstruction:1", direction="out")
    incoming = graph.neighbors("urn:weather:taf:1", direction="in")
    literal = graph.neighbors(
        "urn:result:active",
        direction="out",
        predicate_iris=(QUDT_NUMERIC,),
    )

    assert [edge.fact_id for edge in outgoing] == ["f02", "f04", "f05", "f03", "f01"]
    assert [edge.fact_id for edge in incoming] == ["f03"]
    assert [(edge.object_kind, edge.object_value) for edge in literal] == [
        ("literal", "20")
    ]


def test_graph_view_exposes_all_formal_facts_and_predicate_filters() -> None:
    """The runtime graph tool must not be limited to one registered path shape."""

    graph = CorpusGraphView(_case_facts())

    assert {edge.fact_id for edge in graph.edges()} == {
        fact.fact_id for fact in _case_facts()
    }
    assert {
        edge.fact_id
        for edge in graph.edges(predicate_iris=(PROV_HAD_MEMBER,))
    } == {"f02", "f03", "f04", "f05"}


def test_graph_view_is_strictly_limited_to_supplied_case_facts() -> None:
    """The corpus store, not a hard-coded path, owns case isolation."""

    graph = CorpusGraphView(
        tuple(fact for fact in _case_facts() if fact.fact_id != "f05")
    )

    assert "f05" not in {edge.fact_id for edge in graph.edges()}
    assert {edge.fact_id for edge in graph.edges()} == {
        fact.fact_id for fact in _case_facts() if fact.fact_id != "f05"
    }
