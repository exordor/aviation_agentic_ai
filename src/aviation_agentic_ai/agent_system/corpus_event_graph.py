"""Closed, event-scoped traversal over canonical corpus facts."""

from __future__ import annotations

from collections import defaultdict
from typing import Literal, Protocol

from aviation_agentic_ai.agent_system.contracts import (
    QueryGraphEdge,
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


class CorpusEventGraphView:
    """Deterministic adjacency indexes over one selected event's formal facts."""

    def __init__(self, facts: tuple[GraphFact, ...]) -> None:
        outgoing: dict[str, list[QueryGraphEdge]] = defaultdict(list)
        incoming: dict[str, list[QueryGraphEdge]] = defaultdict(list)
        all_edges: list[QueryGraphEdge] = []
        for fact in facts:
            edge = _edge(fact)
            all_edges.append(edge)
            outgoing[edge.subject_iri].append(edge)
            if edge.object_kind == "iri":
                incoming[edge.object_value].append(edge)
        self._edges = tuple(sorted(all_edges, key=_edge_key))
        self._outgoing = {
            iri: tuple(sorted(edges, key=_edge_key))
            for iri, edges in outgoing.items()
        }
        self._incoming = {
            iri: tuple(sorted(edges, key=_edge_key))
            for iri, edges in incoming.items()
        }

    def edges(
        self,
        *,
        entity_iri: str | None = None,
        direction: Literal["out", "in"] = "out",
        predicate_iris: tuple[str, ...] = (),
    ) -> tuple[QueryGraphEdge, ...]:
        """Return bounded formal edges from this event-scoped graph view."""

        if entity_iri is not None:
            return self.neighbors(
                entity_iri,
                direction=direction,
                predicate_iris=predicate_iris,
            )
        allowed = set(predicate_iris)
        return tuple(
            edge
            for edge in self._edges
            if not allowed or edge.predicate_iri in allowed
        )

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

__all__ = ["CorpusEventGraphView"]
