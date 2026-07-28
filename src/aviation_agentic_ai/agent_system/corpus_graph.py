"""Closed, case-scoped traversal over canonical corpus facts."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from typing import Literal, Protocol

from aviation_agentic_ai.agent_system.contracts import (
    QueryGraphEdge,
    QueryGraphPath,
)


RDF_TYPE_IRI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
PROV_SPECIALIZATION_OF_IRI = "http://www.w3.org/ns/prov#specializationOf"
PROV_HAD_MEMBER_IRI = "http://www.w3.org/ns/prov#hadMember"
PROV_WAS_DERIVED_FROM_IRI = "http://www.w3.org/ns/prov#wasDerivedFrom"
FORECASTING_AIRPORT_IRI = (
    "https://data.nasa.gov/ontologies/atmonto/data#forecastingAirport"
)
SOSA_HAS_FEATURE_OF_INTEREST_IRI = (
    "http://www.w3.org/ns/sosa/hasFeatureOfInterest"
)
SOSA_PHENOMENON_TIME_IRI = "http://www.w3.org/ns/sosa/phenomenonTime"
SOSA_OBSERVED_PROPERTY_IRI = "http://www.w3.org/ns/sosa/observedProperty"
SOSA_HAS_RESULT_IRI = "http://www.w3.org/ns/sosa/hasResult"
DCTERMS_TYPE_IRI = "http://purl.org/dc/terms/type"
QUDT_NUMERIC_VALUE_IRI = "http://qudt.org/schema/qudt/numericValue"
QUDT_UNIT_IRI = "http://qudt.org/schema/qudt/unit"
ACTIVE_PHASE_IRI = "urn:aviation-agentic-ai:observation-phase:active"

_ALLOWED_PREDICATES = frozenset(
    {
        RDF_TYPE_IRI,
        PROV_SPECIALIZATION_OF_IRI,
        PROV_HAD_MEMBER_IRI,
        FORECASTING_AIRPORT_IRI,
        SOSA_HAS_FEATURE_OF_INTEREST_IRI,
        SOSA_PHENOMENON_TIME_IRI,
        SOSA_OBSERVED_PROPERTY_IRI,
        SOSA_HAS_RESULT_IRI,
        PROV_WAS_DERIVED_FROM_IRI,
        DCTERMS_TYPE_IRI,
        QUDT_NUMERIC_VALUE_IRI,
        QUDT_UNIT_IRI,
    }
)


class GraphFact(Protocol):
    """Minimal formal-fact surface needed by the read-only graph view."""

    fact_id: str
    subject_iri: str
    predicate_iri: str
    object_kind: Literal["iri", "literal"]
    object_value: str
    datatype_iri: str | None
    source_ids: list[str]


def _edge(fact: GraphFact) -> QueryGraphEdge:
    return QueryGraphEdge(
        fact_id=fact.fact_id,
        subject_iri=fact.subject_iri,
        predicate_iri=fact.predicate_iri,
        object_kind=fact.object_kind,
        object_value=fact.object_value,
        datatype_iri=fact.datatype_iri,
        source_ids=tuple(sorted(set(fact.source_ids))),
    )


def _edge_key(edge: QueryGraphEdge) -> tuple[str, str, str, str]:
    return (
        edge.subject_iri,
        edge.predicate_iri,
        edge.object_value,
        edge.fact_id,
    )


class CorpusGraphView:
    """Deterministic adjacency indexes over one selected case's formal facts."""

    def __init__(self, facts: tuple[GraphFact, ...]) -> None:
        outgoing: dict[str, list[QueryGraphEdge]] = defaultdict(list)
        incoming: dict[str, list[QueryGraphEdge]] = defaultdict(list)
        for fact in facts:
            if fact.predicate_iri not in _ALLOWED_PREDICATES:
                continue
            edge = _edge(fact)
            outgoing[edge.subject_iri].append(edge)
            if edge.object_kind == "iri":
                incoming[edge.object_value].append(edge)
        self._outgoing = {
            iri: tuple(sorted(edges, key=_edge_key))
            for iri, edges in outgoing.items()
        }
        self._incoming = {
            iri: tuple(sorted(edges, key=_edge_key))
            for iri, edges in incoming.items()
        }

    def neighbors(
        self,
        entity_iri: str,
        *,
        direction: Literal["out", "in"],
        predicate_iris: tuple[str, ...] = (),
    ) -> tuple[QueryGraphEdge, ...]:
        index = self._outgoing if direction == "out" else self._incoming
        allowed = set(predicate_iris)
        return tuple(
            edge
            for edge in index.get(entity_iri, ())
            if not allowed or edge.predicate_iri in allowed
        )

    def follow(
        self,
        entity_iris: tuple[str, ...],
        *,
        direction: Literal["out", "in"],
        predicate_iri: str,
    ) -> tuple[QueryGraphEdge, ...]:
        return tuple(
            edge
            for entity_iri in sorted(set(entity_iris))
            for edge in self.neighbors(
                entity_iri,
                direction=direction,
                predicate_iris=(predicate_iri,),
            )
        )


def _path(
    kind: Literal[
        "event_member",
        "weather_member",
        "active_public_observation",
    ],
    edges: tuple[QueryGraphEdge, ...],
) -> QueryGraphPath:
    fact_ids = tuple(edge.fact_id for edge in edges)
    path_id = "query-graph-path:" + hashlib.sha256(
        json.dumps(
            fact_ids,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return QueryGraphPath(
        path_id=path_id,
        path_kind=kind,
        edges=edges,
        source_ids=tuple(
            sorted(
                {
                    source_id
                    for edge in edges
                    for source_id in edge.source_ids
                }
            )
        ),
    )


def _one_edge(
    graph: CorpusGraphView,
    subject: str,
    predicate: str,
) -> QueryGraphEdge | None:
    edges = graph.neighbors(
        subject,
        direction="out",
        predicate_iris=(predicate,),
    )
    return edges[0] if len(edges) == 1 else None


def get_reconstructed_case_evidence_paths(
    graph: CorpusGraphView,
    case_iri: str,
    reconstruction_iri: str,
) -> tuple[QueryGraphPath, ...]:
    """Return only the registered event, Weather, and active BTS paths."""

    specialization = _one_edge(
        graph,
        reconstruction_iri,
        PROV_SPECIALIZATION_OF_IRI,
    )
    if specialization is None or specialization.object_value != case_iri:
        return ()

    paths: list[QueryGraphPath] = []
    memberships = graph.neighbors(
        reconstruction_iri,
        direction="out",
        predicate_iris=(PROV_HAD_MEMBER_IRI,),
    )
    for membership in memberships:
        member = membership.object_value
        weather_edges = graph.neighbors(
            member,
            direction="out",
            predicate_iris=(FORECASTING_AIRPORT_IRI,),
        )
        if weather_edges:
            paths.append(
                _path(
                    "weather_member",
                    (specialization, membership, *weather_edges),
                )
            )
            continue

        time_edge = _one_edge(graph, member, SOSA_PHENOMENON_TIME_IRI)
        if time_edge is not None:
            phase_edge = _one_edge(
                graph,
                time_edge.object_value,
                DCTERMS_TYPE_IRI,
            )
            if phase_edge is None or phase_edge.object_value != ACTIVE_PHASE_IRI:
                continue
            detail_edges = tuple(
                edge
                for predicate in (
                    SOSA_HAS_FEATURE_OF_INTEREST_IRI,
                    SOSA_OBSERVED_PROPERTY_IRI,
                    SOSA_HAS_RESULT_IRI,
                    PROV_WAS_DERIVED_FROM_IRI,
                )
                for edge in graph.neighbors(
                    member,
                    direction="out",
                    predicate_iris=(predicate,),
                )
            )
            result_edges: tuple[QueryGraphEdge, ...] = ()
            result = _one_edge(graph, member, SOSA_HAS_RESULT_IRI)
            if result is not None:
                result_edges = tuple(
                    edge
                    for predicate in (QUDT_NUMERIC_VALUE_IRI, QUDT_UNIT_IRI)
                    for edge in graph.neighbors(
                        result.object_value,
                        direction="out",
                        predicate_iris=(predicate,),
                    )
                )
            paths.append(
                _path(
                    "active_public_observation",
                    (
                        specialization,
                        membership,
                        time_edge,
                        phase_edge,
                        *detail_edges,
                        *result_edges,
                    ),
                )
            )
            continue

        paths.append(_path("event_member", (specialization, membership)))

    return tuple(sorted(paths, key=lambda path: (path.path_kind, path.path_id)))


__all__ = [
    "CorpusGraphView",
    "get_reconstructed_case_evidence_paths",
]
