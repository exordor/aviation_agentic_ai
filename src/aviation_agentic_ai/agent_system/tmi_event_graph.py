"""Closed, event-scoped traversal over formally published TMI facts."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol

from aviation_agentic_ai.agent_system.contracts import (
    QueryGraphEdge,
)
from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
)


class GraphFact(Protocol):
    """Minimal formal-fact surface needed by the read-only graph view."""

    fact_id: str
    subject_iri: str
    predicate_iri: str
    object_kind: Literal["iri", "literal"]
    object_value: str
    datatype_iri: str | None
    source_ids: Sequence[str]


@dataclass(frozen=True)
class _EvidenceBoundGraphFact:
    """One semantic fact joined to its publication-scoped logical sources."""

    fact_id: str
    subject_iri: str
    predicate_iri: str
    object_kind: Literal["iri", "literal"]
    object_value: str
    datatype_iri: str | None
    source_ids: tuple[str, ...]


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


class TMIEventGraphView:
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


def build_tmi_event_graph(
    store: AviationEvidenceStore,
    event_id: str,
) -> TMIEventGraphView:
    """Build the active event graph with logical source provenance."""

    facts = store.get_event_facts(event_id)
    sources_by_version = {
        source.source_version_id: source.source_id
        for source in store.get_event_sources(event_id)
    }
    source_ids_by_fact: dict[str, set[str]] = defaultdict(set)
    for link in store.get_event_evidence(event_id):
        if link.owner_kind != "fact":
            continue
        try:
            source_id = sources_by_version[link.source_version_id]
        except KeyError as exc:
            raise ValueError(
                "fact evidence source is outside the event publication"
            ) from exc
        source_ids_by_fact[link.owner_id].add(source_id)

    return TMIEventGraphView(
        tuple(
            _EvidenceBoundGraphFact(
                fact_id=fact.fact_id,
                subject_iri=fact.subject_iri,
                predicate_iri=fact.predicate_iri,
                object_kind=fact.object_kind,
                object_value=fact.object_value,
                datatype_iri=fact.datatype_iri,
                source_ids=tuple(
                    sorted(source_ids_by_fact.get(fact.fact_id, ()))
                ),
            )
            for fact in facts
        )
    )


__all__ = ["TMIEventGraphView", "build_tmi_event_graph"]
