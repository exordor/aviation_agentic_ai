"""Read-only Query Agent tools for ontology-constructed knowledge roots."""

from __future__ import annotations

import json
import re
from typing import Literal

from langchain_core.tools import BaseTool, tool
from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryEvidence,
    HybridQueryScope,
    HybridQuerySupportRecord,
    HybridQueryToolObservation,
    QueryGraphEdge,
    QueryGraphPath,
    StrictModel,
)
from aviation_agentic_ai.agent_system.query_runtime import QueryRuntime
from aviation_agentic_ai.agent_system.storage_contracts import (
    ActiveFormalFactBinding,
)
from aviation_agentic_ai.utils.identifiers import stable_id


ONTOLOGY_ROOT_KINDS = frozenset(
    {"ontology_document", "ontology_section", "ontology_paragraph", "ontology_entity"}
)
_KNOWLEDGE_QUERY_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "about",
        "apply",
        "applies",
        "does",
        "faa",
        "for",
        "how",
        "in",
        "is",
        "manual",
        "of",
        "on",
        "or",
        "rule",
        "say",
        "the",
        "to",
        "what",
        "when",
        "which",
        "who",
        "where",
        "jo",
    }
)


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _unique(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


class FindKnowledgeRootsInput(StrictModel):
    """Natural-language terms used to discover constructed knowledge roots."""

    query: str = Field(min_length=1)
    root_kind: str | None = Field(default=None, min_length=1)
    predicate_iri: str | None = Field(default=None, min_length=1)
    offset: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=1, le=100)


class SearchKnowledgeEntitiesInput(StrictModel):
    """Semantic discovery over the rebuildable knowledge entity index."""

    query: str = Field(min_length=1)
    limit: int | None = Field(default=None, ge=1, le=100)


class KnowledgeGraphInput(StrictModel):
    """One bounded neighborhood read over a constructed knowledge root."""

    root_id: str = Field(min_length=1)
    direction: Literal["out", "in"] = "out"
    predicate_iris: tuple[str, ...] = ()
    limit: int = Field(default=50, ge=1, le=100)


class KnowledgeQueryGateway:
    """Apply the immutable query scope to constructed facts in the live store."""

    def __init__(self, *, runtime: QueryRuntime, scope: HybridQueryScope) -> None:
        self.runtime = runtime
        self.store = runtime.store
        self.scope = scope

    def _limit(self, value: int | None) -> int:
        if value is None:
            return self.scope.limit
        return min(value, self.scope.limit)

    def _offset(self, value: int | None) -> int:
        if value is None:
            return self.scope.offset
        if value < self.scope.offset:
            raise ValueError("offset broadens the query scope")
        return value

    def _root_id(self, value: str) -> str:
        if self.scope.root_id is not None and value != self.scope.root_id:
            raise ValueError("root_id is outside the query scope")
        return value

    def _source_ids(self, binding: ActiveFormalFactBinding) -> tuple[str, ...]:
        return _unique(
            source.source_id
            for source in (
                self.store.get_source_version(link.source_version_id)
                for link in binding.evidence_links
            )
            if source is not None
        )

    def _version_ids(self, binding: ActiveFormalFactBinding) -> tuple[str, ...]:
        return _unique(
            link.source_version_id for link in binding.evidence_links
        )

    def _anchor_ids(self, binding: ActiveFormalFactBinding) -> tuple[str, ...]:
        return _unique(
            link.source_anchor_id
            for link in binding.evidence_links
            if link.source_anchor_id
        )

    def _evidence_allowed(
        self,
        source_ids: tuple[str, ...],
        version_ids: tuple[str, ...],
    ) -> bool:
        if self.scope.source_ids and not set(source_ids).intersection(
            self.scope.source_ids
        ):
            return False
        if not self.scope.source_families:
            return True
        allowed = set(self.scope.source_families)
        return any(
            (version := self.store.get_source_version(version_id)) is not None
            and version.family in allowed
            for version_id in version_ids
        )

    def _temporal_allowed(self, binding: ActiveFormalFactBinding) -> bool:
        return (
            self.scope.temporal_domain_id is None
            or binding.temporal_domain_id == self.scope.temporal_domain_id
        )

    @staticmethod
    def _is_knowledge_root(binding: ActiveFormalFactBinding) -> bool:
        return binding.root_kind in ONTOLOGY_ROOT_KINDS

    @staticmethod
    def _terms(query: str) -> tuple[str, ...]:
        return tuple(
            term
            for term in re.findall(r"[a-z0-9][a-z0-9_-]*", query.lower())
            if len(term) > 1 and term not in _KNOWLEDGE_QUERY_STOPWORDS
        )

    @staticmethod
    def _binding_text(binding: ActiveFormalFactBinding) -> str:
        fact = binding.fact
        evidence = " ".join(
            link.evidence_text or "" for link in binding.evidence_links
        )
        return " ".join(
            (
                binding.root_id,
                binding.root_kind,
                binding.temporal_domain_id,
                fact.subject_iri,
                fact.predicate_iri,
                fact.object_value,
                evidence,
            )
        ).lower()

    def _bindings(
        self,
        *,
        root_ids: tuple[str, ...] = (),
    ) -> tuple[ActiveFormalFactBinding, ...]:
        return tuple(
            binding
            for binding in self.store.list_active_formal_fact_bindings(
                root_ids=root_ids
            )
            if self._is_knowledge_root(binding)
            and (
                self.scope.root_id is None
                or binding.root_id == self.scope.root_id
            )
            and self._temporal_allowed(binding)
            and self._evidence_allowed(
                self._source_ids(binding), self._version_ids(binding)
            )
        )

    @staticmethod
    def _observation(
        *,
        payload: object,
        support: list[HybridQuerySupportRecord],
        graph_paths: tuple[QueryGraphPath, ...] = (),
        limitation: str = "",
    ) -> HybridQueryToolObservation:
        def values(field: str) -> tuple[str, ...]:
            return _unique(
                [value for record in support for value in getattr(record, field)]
            )

        evidence = HybridQueryEvidence(
            root_ids=values("root_ids"),
            publication_ids=values("publication_ids"),
            fact_ids=values("fact_ids"),
            graph_path_ids=values("graph_path_ids"),
            source_ids=values("source_ids"),
            source_version_ids=values("source_version_ids"),
            source_anchor_ids=values("source_anchor_ids"),
        )
        return HybridQueryToolObservation(
            status="ok" if support else "insufficient",
            content=_json(payload),
            details=evidence,
            support_records=tuple(support),
            graph_paths=graph_paths,
            limitation=limitation if not support else "",
        )

    def find_knowledge_roots(self, **kwargs: object) -> HybridQueryToolObservation:
        query = FindKnowledgeRootsInput.model_validate(kwargs)
        terms = self._terms(query.query)
        offset = self._offset(query.offset)
        limit = self._limit(query.limit)
        matches = [
            binding
            for binding in self._bindings()
            if (query.root_kind is None or binding.root_kind == query.root_kind)
            and (
                query.predicate_iri is None
                or binding.fact.predicate_iri == query.predicate_iri
            )
            and (
                query.predicate_iri is not None
                or not terms
                or all(term in self._binding_text(binding) for term in terms)
            )
        ]
        grouped: dict[str, list[ActiveFormalFactBinding]] = {}
        for binding in matches:
            grouped.setdefault(binding.root_id, []).append(binding)
        roots = []
        support: list[HybridQuerySupportRecord] = []
        for root_id in sorted(grouped)[offset : offset + limit]:
            bindings = grouped[root_id]
            first = bindings[0]
            source_ids = _unique(
                [source_id for binding in bindings for source_id in self._source_ids(binding)]
            )
            version_ids = _unique(
                [version_id for binding in bindings for version_id in self._version_ids(binding)]
            )
            anchor_ids = _unique(
                [anchor_id for binding in bindings for anchor_id in self._anchor_ids(binding)]
            )
            fact_ids = tuple(binding.fact.fact_id for binding in bindings)
            publication_ids = _unique(binding.publication_id for binding in bindings)
            roots.append(
                {
                    "root_id": root_id,
                    "root_kind": first.root_kind,
                    "temporal_domain_id": first.temporal_domain_id,
                    "publication_ids": publication_ids,
                    "facts": [
                        {
                            "fact_id": binding.fact.fact_id,
                            "predicate_iri": binding.fact.predicate_iri,
                            "object_kind": binding.fact.object_kind,
                            "object_value": binding.fact.object_value,
                        }
                        for binding in bindings
                    ],
                }
            )
            support.append(
                HybridQuerySupportRecord(
                    kind="source_fact",
                    root_ids=(root_id,),
                    publication_ids=publication_ids,
                    fact_ids=fact_ids,
                    source_ids=source_ids,
                    source_version_ids=version_ids,
                    source_anchor_ids=anchor_ids,
                )
            )
        return self._observation(
            payload={
                "query": query.query,
                "predicate_iri": query.predicate_iri,
                "offset": offset,
                "limit": limit,
                "roots": roots,
            },
            support=support,
            limitation="No published ontology-constructed root matched the query.",
        )

    def search_knowledge_entities(self, **kwargs: object) -> HybridQueryToolObservation:
        query = SearchKnowledgeEntitiesInput.model_validate(kwargs)
        if self.runtime.knowledge_index is None:
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json({"query": query.query, "candidates": []}),
                limitation=(
                    "The knowledge entity vector index is unavailable; run reindex "
                    "after publishing ontology-extracted entities."
                ),
            )
        candidate_root_ids = tuple(
            sorted(
                {
                    binding.root_id
                    for binding in self._bindings()
                    if binding.root_kind == "ontology_entity"
                }
            )
        )
        limit = self._limit(query.limit)
        hits = self.runtime.knowledge_index.query_entities(
            query_text=query.query,
            candidate_root_ids=candidate_root_ids,
            n_results=limit,
        )
        support = tuple(
            HybridQuerySupportRecord(
                kind="similarity",
                root_ids=(hit.root_id,),
                publication_ids=(hit.publication_id,),
            )
            for hit in hits
        )
        return HybridQueryToolObservation(
            status="ok" if hits else "insufficient",
            content=_json(
                {
                    "query": query.query,
                    "candidates": [
                        {
                            "root_id": hit.root_id,
                            "publication_id": hit.publication_id,
                            "class_iri": hit.class_iri,
                            "label": hit.label,
                            "similarity": hit.similarity,
                        }
                        for hit in hits
                    ],
                }
            ),
            details=HybridQueryEvidence(
                root_ids=tuple(hit.root_id for hit in hits),
                publication_ids=tuple(hit.publication_id for hit in hits),
            ),
            support_records=support,
            limitation=(
                "Vector matches are discovery candidates, not formal graph facts; "
                "call read_knowledge_graph and read_source before answering."
                if hits
                else "No active knowledge entity matched the semantic query."
            ),
        )

    def read_knowledge_graph(
        self,
        *,
        root_id: str,
        direction: Literal["out", "in"] = "out",
        predicate_iris: tuple[str, ...] = (),
        limit: int = 50,
    ) -> HybridQueryToolObservation:
        query = KnowledgeGraphInput.model_validate(
            {
                "root_id": root_id,
                "direction": direction,
                "predicate_iris": predicate_iris,
                "limit": limit,
            }
        )
        root_id = self._root_id(query.root_id)
        bindings = self._bindings(root_ids=(root_id,))
        paths: list[QueryGraphPath] = []
        support: list[HybridQuerySupportRecord] = []
        for binding in bindings:
            fact = binding.fact
            matches = (
                fact.subject_iri == root_id
                if query.direction == "out"
                else fact.object_kind == "iri" and fact.object_value == root_id
            )
            if not matches or (
                query.predicate_iris
                and fact.predicate_iri not in query.predicate_iris
            ):
                continue
            source_ids = self._source_ids(binding)
            version_ids = self._version_ids(binding)
            anchor_ids = self._anchor_ids(binding)
            related_root_ids = _unique(
                [
                    root_id,
                    fact.subject_iri,
                    *(
                        [fact.object_value]
                        if fact.object_kind == "iri"
                        else []
                    ),
                ]
            )
            path = QueryGraphPath(
                path_id=stable_id(
                    "knowledge-graph-path", root_id, query.direction, fact.fact_id
                ),
                path_kind=f"knowledge_neighbor_{query.direction}",
                edges=(
                    QueryGraphEdge(
                        fact_id=fact.fact_id,
                        subject_iri=fact.subject_iri,
                        predicate_iri=fact.predicate_iri,
                        object_kind=fact.object_kind,
                        object_value=fact.object_value,
                        datatype_iri=fact.datatype_iri,
                        source_ids=source_ids,
                    ),
                ),
                source_ids=source_ids,
            )
            paths.append(path)
            support.append(
                HybridQuerySupportRecord(
                    kind="source_fact",
                    root_ids=related_root_ids,
                    publication_ids=(binding.publication_id,),
                    fact_ids=(fact.fact_id,),
                    graph_path_ids=(path.path_id,),
                    source_ids=source_ids,
                    source_version_ids=version_ids,
                    source_anchor_ids=anchor_ids,
                )
            )
            if len(paths) >= query.limit:
                break
        return self._observation(
            payload={
                "root_id": root_id,
                "direction": query.direction,
                "paths": [path.model_dump(mode="json") for path in paths],
            },
            support=support,
            graph_paths=tuple(paths),
            limitation="No accepted ontology-constructed fact matched the root.",
        )


def build_knowledge_query_tools(gateway: KnowledgeQueryGateway) -> list[BaseTool]:
    """Expose constructed-root discovery and graph reads as bounded tools."""

    @tool("search_knowledge_entities", args_schema=SearchKnowledgeEntitiesInput)
    def search_knowledge_entities_tool(**kwargs: object) -> dict[str, object]:
        """Semantically discover candidate ontology-extracted entities."""

        return gateway.search_knowledge_entities(**kwargs).model_dump(mode="json")

    @tool("find_knowledge_roots", args_schema=FindKnowledgeRootsInput)
    def find_knowledge_roots_tool(**kwargs: object) -> dict[str, object]:
        """Find constructed roots, optionally filtering by predicate IRI."""

        return gateway.find_knowledge_roots(**kwargs).model_dump(mode="json")

    @tool("read_knowledge_graph", args_schema=KnowledgeGraphInput)
    def read_knowledge_graph_tool(**kwargs: object) -> dict[str, object]:
        """Read bounded ATMONTO-aligned constructed-knowledge neighbors."""

        return gateway.read_knowledge_graph(**kwargs).model_dump(mode="json")

    return [
        search_knowledge_entities_tool,
        find_knowledge_roots_tool,
        read_knowledge_graph_tool,
    ]


__all__ = [
    "FindKnowledgeRootsInput",
    "KnowledgeGraphInput",
    "KnowledgeQueryGateway",
    "SearchKnowledgeEntitiesInput",
    "build_knowledge_query_tools",
]
