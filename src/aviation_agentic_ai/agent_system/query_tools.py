"""Typed read-only tools for the bounded Query Agent.

The model never receives a filesystem path, Cypher, SPARQL, or a graph-write
operation.  A gateway is scoped to one materialized run and exposes only
registered event/entity IDs and predicates from the active competency question.
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from langchain_core.tools import BaseTool, tool
from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.agent_system.schema_guide import TERM_TO_EVENT_CLASS

_REGISTERED_EVENT_CLASSES = frozenset(TERM_TO_EVENT_CLASS.values())


class QueryToolError(RuntimeError):
    """Raised when a read-only graph operation cannot be executed safely."""


class QueryPredicate(str, Enum):
    """Predicates available to the first Query Agent vertical slice."""

    EVENT_TYPE = "rdf:type"
    CONTROLLED_NAS_ELEMENT = "atm:controlledNASelement"
    EFFECTIVE_START = "atm:effectiveStartTime"
    EFFECTIVE_END = "atm:effectiveEndTime"


class QueryRelation(str, Enum):
    """Relations available to the bounded neighbor tool."""

    CONTROLLED_NAS_ELEMENT = "atm:controlledNASelement"


class FindEventsInput(StrictModel):
    """Filters for event discovery within the current run."""

    source_id: str | None = None
    event_class: str | None = None


class GetEventFactsInput(StrictModel):
    """A registered event and the permitted predicates to retrieve."""

    event_id: str = Field(min_length=1)
    predicates: list[QueryPredicate] = Field(min_length=1, max_length=4)


class GetNeighborsInput(StrictModel):
    """A registered graph entity and one allowed relation."""

    entity_id: str = Field(min_length=1)
    relation: QueryRelation


class GetProvenanceInput(StrictModel):
    """Fact IDs already returned in the current tool session."""

    fact_ids: list[str] = Field(min_length=1, max_length=20)


class QueryToolResult(StrictModel):
    """One deterministic, JSON-serializable graph-tool observation."""

    tool: Literal[
        "find_events",
        "get_event_facts",
        "get_neighbors",
        "get_provenance",
    ]
    status: Literal["ok"] = "ok"
    fact_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    items: list[dict[str, Any]] = Field(default_factory=list)


def _split_source_ids(value: Any) -> list[str]:
    return [
        source_id.strip()
        for source_id in str(value or "").split(";")
        if source_id.strip()
    ]


class QueryGraphStore:
    """Validated read-only view of one run's ``kg.jsonl``."""

    def __init__(self, run_dir: str | Path) -> None:
        root = Path(run_dir).resolve()
        graph_path = root / "kg.jsonl"
        if not graph_path.exists():
            raise QueryToolError(f"materialized graph not found: {graph_path}")
        resolved_graph = graph_path.resolve()
        if not resolved_graph.is_relative_to(root):
            raise QueryToolError("materialized graph escapes the requested run directory")

        rows: list[dict[str, Any]] = []
        seen_fact_ids: set[str] = set()
        for line_number, line in enumerate(
            resolved_graph.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise QueryToolError(
                    f"invalid graph JSON at line {line_number}"
                ) from exc
            if not isinstance(row, dict):
                raise QueryToolError(
                    f"graph row {line_number} is not a JSON object"
                )
            fact_id = str(row.get("triple_id") or row.get("fact_id") or "").strip()
            if not fact_id:
                raise QueryToolError(f"graph row {line_number} has no fact ID")
            if fact_id in seen_fact_ids:
                raise QueryToolError(f"duplicate graph fact ID: {fact_id}")
            subject = str(row.get("subject") or "").strip()
            predicate = str(row.get("predicate") or "").strip()
            if not subject or not predicate:
                raise QueryToolError(
                    f"graph row {line_number} is missing subject or predicate"
                )
            normalized = dict(row)
            normalized["fact_id"] = fact_id
            normalized["source_ids"] = _split_source_ids(
                row.get("source_document")
            )
            rows.append(normalized)
            seen_fact_ids.add(fact_id)

        self.run_dir = root
        self.graph_path = resolved_graph
        self.rows = rows
        self.fact_by_id = {row["fact_id"]: row for row in rows}
        self.event_ids = sorted(
            {
                str(row["subject"])
                for row in rows
                if row["predicate"] == QueryPredicate.EVENT_TYPE
                and str(row.get("object") or "") in _REGISTERED_EVENT_CLASSES
            }
        )
        entity_ids = set(self.event_ids)
        for row in rows:
            if str(row.get("object_kind") or "") == "iri":
                entity_ids.add(str(row.get("object") or ""))
            elif str(row.get("predicate") or "") == QueryPredicate.CONTROLLED_NAS_ELEMENT:
                entity_ids.add(str(row.get("object") or ""))
        self.entity_ids = {entity_id for entity_id in entity_ids if entity_id}

    def event_class(self, event_id: str) -> str:
        for row in self.rows:
            if row["subject"] == event_id and row["predicate"] == QueryPredicate.EVENT_TYPE:
                return str(row.get("object") or row.get("subject_class") or "")
        for row in self.rows:
            if row["subject"] == event_id:
                return str(row.get("subject_class") or "")
        return ""


class QueryToolGateway:
    """Session-scoped authority boundary behind the LangChain tools."""

    def __init__(
        self,
        store: QueryGraphStore,
        *,
        allowed_predicates: set[str],
        max_facts: int = 20,
    ) -> None:
        self.store = store
        self.allowed_predicates = set(allowed_predicates)
        self.max_facts = max_facts
        self.retrieved_fact_ids: set[str] = set()
        self.retrieved_source_ids: set[str] = set()

    def find_events(
        self,
        *,
        source_id: str | None = None,
        event_class: str | None = None,
    ) -> QueryToolResult:
        items: list[dict[str, Any]] = []
        remaining_fact_budget = self.max_facts
        for event_id in self.store.event_ids:
            if remaining_fact_budget <= 0:
                break
            event_rows = sorted(
                (
                    row for row in self.store.rows if row["subject"] == event_id
                ),
                key=lambda row: str(row["fact_id"]),
            )
            row_sources = {
                source
                for row in event_rows
                for source in row["source_ids"]
            }
            current_class = self.store.event_class(event_id)
            if source_id and source_id not in row_sources:
                continue
            if event_class and event_class != current_class:
                continue
            selected_rows = event_rows[:remaining_fact_budget]
            event_fact_ids = [
                str(row["fact_id"]) for row in selected_rows
            ]
            selected_sources = sorted(
                {
                    source
                    for row in selected_rows
                    for source in row["source_ids"]
                }
            )
            items.append(
                {
                    "event_id": event_id,
                    "event_class": current_class,
                    "matching_fact_ids": event_fact_ids,
                    "source_ids": selected_sources,
                }
            )
            remaining_fact_budget -= len(event_fact_ids)
        fact_ids = {
            fact_id
            for item in items
            for fact_id in item["matching_fact_ids"]
        }
        source_ids = {
            source_id
            for item in items
            for source_id in item["source_ids"]
        }
        return QueryToolResult(
            tool="find_events",
            fact_ids=sorted(fact_ids),
            source_ids=sorted(source_ids),
            items=items,
        )

    def get_event_facts(
        self,
        *,
        event_id: str,
        predicates: list[QueryPredicate | str],
    ) -> QueryToolResult:
        if event_id not in self.store.event_ids:
            raise QueryToolError(f"unregistered event ID: {event_id}")
        requested = [str(getattr(value, "value", value)) for value in predicates]
        if len(requested) != len(set(requested)):
            raise QueryToolError("duplicate predicates are not allowed")
        disallowed = sorted(set(requested) - self.allowed_predicates)
        if disallowed:
            raise QueryToolError(
                f"predicates are outside the current query scope: {disallowed}"
            )
        predicate_order = {predicate: index for index, predicate in enumerate(requested)}
        rows = sorted(
            (
                row
                for row in self.store.rows
                if row["subject"] == event_id and row["predicate"] in requested
            ),
            key=lambda row: (
                predicate_order[str(row["predicate"])],
                str(row["fact_id"]),
            ),
        )[: self.max_facts]
        unsourced = [row["fact_id"] for row in rows if not row["source_ids"]]
        if unsourced:
            raise QueryToolError(
                f"retrieved graph facts are missing provenance: {unsourced}"
            )
        fact_ids = [str(row["fact_id"]) for row in rows]
        source_ids = sorted(
            {
                source_id
                for row in rows
                for source_id in row["source_ids"]
            }
        )
        items = [
            {
                "fact_id": row["fact_id"],
                "subject": row["subject"],
                "predicate": row["predicate"],
                "object": row.get("object"),
                "object_class": row.get("object_class") or "",
                "source_ids": row["source_ids"],
            }
            for row in rows
        ]
        self.retrieved_fact_ids.update(fact_ids)
        self.retrieved_source_ids.update(source_ids)
        return QueryToolResult(
            tool="get_event_facts",
            fact_ids=fact_ids,
            source_ids=source_ids,
            items=items,
        )

    def get_neighbors(
        self,
        *,
        entity_id: str,
        relation: QueryRelation | str,
    ) -> QueryToolResult:
        if entity_id not in self.store.entity_ids:
            raise QueryToolError(f"unregistered graph entity ID: {entity_id}")
        relation_value = str(getattr(relation, "value", relation))
        rows = [
            row
            for row in self.store.rows
            if row["predicate"] == relation_value
            and (row["subject"] == entity_id or row.get("object") == entity_id)
        ][: self.max_facts]
        unsourced = [row["fact_id"] for row in rows if not row["source_ids"]]
        if unsourced:
            raise QueryToolError(
                f"retrieved graph facts are missing provenance: {unsourced}"
            )
        fact_ids = [str(row["fact_id"]) for row in rows]
        source_ids = sorted(
            {
                source_id
                for row in rows
                for source_id in row["source_ids"]
            }
        )
        items = [
            {
                "fact_id": row["fact_id"],
                "relation": row["predicate"],
                "from": row["subject"],
                "to": row.get("object"),
                "source_ids": row["source_ids"],
            }
            for row in rows
        ]
        self.retrieved_fact_ids.update(fact_ids)
        self.retrieved_source_ids.update(source_ids)
        return QueryToolResult(
            tool="get_neighbors",
            fact_ids=fact_ids,
            source_ids=source_ids,
            items=items,
        )

    def get_provenance(self, *, fact_ids: list[str]) -> QueryToolResult:
        requested = set(fact_ids)
        unknown = sorted(requested - self.retrieved_fact_ids)
        if unknown:
            raise QueryToolError(
                "provenance may only be requested for facts returned in this "
                f"tool session: {unknown}"
            )
        items: list[dict[str, Any]] = []
        source_ids: set[str] = set()
        for fact_id in sorted(requested):
            row = self.store.fact_by_id[fact_id]
            if not row["source_ids"]:
                raise QueryToolError(
                    f"retrieved graph fact is missing provenance: {fact_id}"
                )
            for source_id in row["source_ids"]:
                items.append({"fact_id": fact_id, "source_id": source_id})
                source_ids.add(source_id)
        self.retrieved_source_ids.update(source_ids)
        return QueryToolResult(
            tool="get_provenance",
            fact_ids=sorted(requested),
            source_ids=sorted(source_ids),
            items=items,
        )


def build_query_tools(gateway: QueryToolGateway) -> list[BaseTool]:
    """Build the four model-visible LangChain tools for one query session."""

    @tool("find_events", args_schema=FindEventsInput)
    def find_events(
        source_id: str | None = None,
        event_class: str | None = None,
    ) -> str:
        """Find registered event IDs in this run; this tool never returns raw source text."""

        return gateway.find_events(
            source_id=source_id,
            event_class=event_class,
        ).model_dump_json()

    @tool("get_event_facts", args_schema=GetEventFactsInput)
    def get_event_facts(
        event_id: str,
        predicates: list[QueryPredicate],
    ) -> str:
        """Read selected validated facts for one registered event ID."""

        return gateway.get_event_facts(
            event_id=event_id,
            predicates=predicates,
        ).model_dump_json()

    @tool("get_neighbors", args_schema=GetNeighborsInput)
    def get_neighbors(entity_id: str, relation: QueryRelation) -> str:
        """Read bounded one-hop neighbors for a registered graph entity."""

        return gateway.get_neighbors(
            entity_id=entity_id,
            relation=relation,
        ).model_dump_json()

    @tool("get_provenance", args_schema=GetProvenanceInput)
    def get_provenance(fact_ids: list[str]) -> str:
        """Read source IDs for fact IDs already returned in this tool session."""

        return gateway.get_provenance(fact_ids=fact_ids).model_dump_json()

    return [find_events, get_event_facts, get_neighbors, get_provenance]


def tool_registry(tools: list[BaseTool]) -> dict[str, BaseTool]:
    """Index tools by their framework-visible names."""

    registry = {tool_.name: tool_ for tool_ in tools}
    if len(registry) != len(tools):
        raise QueryToolError("duplicate Query Agent tool name")
    return registry
