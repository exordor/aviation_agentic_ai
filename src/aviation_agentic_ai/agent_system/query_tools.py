"""Typed read-only tools for the bounded Query Agent.

The model never receives a filesystem path, Cypher, SPARQL, or a graph-write
operation.  A gateway is scoped to one materialized run and exposes only
registered event/entity IDs and predicates from the active competency question.
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from langchain_core.tools import BaseTool, tool
from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import (
    PersistedProfileGap,
    SourceSnapshot,
    StrictModel,
)
from aviation_agentic_ai.agent_system.query_context_store import (
    QueryContextError,
    QueryContextStore,
)
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
    ADVISORY_NUMBER = "atm:advisoryNumber"
    IMPACTING_CONDITION = "atm:impactingCondition"


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
    predicates: list[QueryPredicate] = Field(min_length=1, max_length=6)


class GetProfileGapsInput(StrictModel):
    """A registered event and the source-only field to retrieve."""

    event_id: str = Field(min_length=1)
    fields: list[str] = Field(min_length=1, max_length=2)


class GetDecisionContextInput(StrictModel):
    """A registered event whose validated non-causal context is requested."""

    event_id: str = Field(min_length=1)


class GetOutcomeSummaryInput(StrictModel):
    """A registered event and the bounded public outcome phases to retrieve."""

    event_id: str = Field(min_length=1)
    phases: list[Literal["baseline", "active", "recovery"]] = Field(
        default_factory=lambda: ["baseline", "active", "recovery"],
        min_length=1,
        max_length=3,
    )


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
        "get_profile_gaps",
        "get_decision_context",
        "get_outcome_summary",
    ]
    status: Literal["ok", "insufficient"] = "ok"
    fact_ids: list[str] = Field(default_factory=list)
    profile_gap_ids: list[str] = Field(default_factory=list)
    context_association_ids: list[str] = Field(default_factory=list)
    outcome_summary_ids: list[str] = Field(default_factory=list)
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
        self.profile_gaps = self._load_profile_gaps(root)
        self.profile_gap_by_id = {
            gap.profile_gap_id: gap for gap in self.profile_gaps
        }

    def _load_profile_gaps(self, root: Path) -> list[PersistedProfileGap]:
        path = root / "profile_gaps.jsonl"
        if not path.exists():
            return []
        resolved = path.resolve()
        if not resolved.is_relative_to(root):
            raise QueryToolError("profile-gap artifact escapes the requested run directory")

        gaps: list[PersistedProfileGap] = []
        seen_ids: set[str] = set()
        event_sources = {
            event_id: {
                source_id
                for row in self.rows
                if row["subject"] == event_id
                for source_id in row["source_ids"]
            }
            for event_id in self.event_ids
        }
        for line_number, line in enumerate(
            resolved.read_text(encoding="utf-8").splitlines(),
            start=1,
        ):
            if not line.strip():
                continue
            try:
                gap = PersistedProfileGap.model_validate_json(line)
            except Exception as exc:
                raise QueryToolError(
                    f"invalid profile-gap JSON at line {line_number}"
                ) from exc
            if gap.profile_gap_id in seen_ids:
                raise QueryToolError(
                    f"duplicate profile-gap ID: {gap.profile_gap_id}"
                )
            if gap.event_id not in self.event_ids:
                raise QueryToolError(
                    f"profile gap references an unregistered event: {gap.event_id}"
                )
            if gap.source_id not in event_sources[gap.event_id]:
                raise QueryToolError(
                    f"profile gap source is not bound to its event: {gap.profile_gap_id}"
                )
            seen_ids.add(gap.profile_gap_id)
            gaps.append(gap)
        snapshots = self._load_profile_gap_snapshots(
            root,
            {gap.source_id for gap in gaps},
        )
        for gap in gaps:
            snapshot = snapshots.get(gap.source_id)
            if (
                snapshot is None
                or gap.source_snapshot_sha256 != snapshot.content_sha256
                or gap.evidence_text not in snapshot.content
            ):
                raise QueryToolError(
                    f"profile gap does not match the run snapshot: {gap.profile_gap_id}"
                )
        return gaps

    @staticmethod
    def _load_profile_gap_snapshots(
        root: Path,
        required_source_ids: set[str],
    ) -> dict[str, SourceSnapshot]:
        if not required_source_ids:
            return {}
        registry_path = root / "source_snapshots.jsonl"
        legacy_snapshot_path = root / "source_snapshot.json"
        selected: dict[str, SourceSnapshot] = {}
        if registry_path.exists():
            resolved_registry = registry_path.resolve()
            if not resolved_registry.is_relative_to(root):
                raise QueryToolError(
                    "source-snapshot artifact escapes the requested run directory"
                )
            for line_number, line in enumerate(
                resolved_registry.read_text(encoding="utf-8").splitlines(),
                1,
            ):
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if (
                    not isinstance(payload, dict)
                    or payload.get("source_id") not in required_source_ids
                ):
                    continue
                source_id = str(payload["source_id"])
                if source_id in selected:
                    raise QueryToolError(
                        f"duplicate profile-gap source snapshot ID: {source_id}"
                    )
                try:
                    snapshot = SourceSnapshot.model_validate(payload)
                except Exception as exc:
                    raise QueryToolError(
                        f"invalid profile-gap source snapshot at line {line_number}"
                    ) from exc
                if snapshot.content_sha256 != hashlib.sha256(
                    snapshot.content.encode("utf-8")
                ).hexdigest():
                    raise QueryToolError(
                        f"profile-gap source snapshot checksum mismatch: {source_id}"
                    )
                selected[source_id] = snapshot
        elif legacy_snapshot_path.exists():
            resolved_snapshot = legacy_snapshot_path.resolve()
            if not resolved_snapshot.is_relative_to(root):
                raise QueryToolError(
                    "source-snapshot artifact escapes the requested run directory"
                )
            try:
                snapshot = SourceSnapshot.model_validate_json(
                    resolved_snapshot.read_text(encoding="utf-8")
                )
            except Exception as exc:
                raise QueryToolError(
                    "invalid source snapshot for profile gaps"
                ) from exc
            if snapshot.source_id in required_source_ids:
                if snapshot.content_sha256 != hashlib.sha256(
                    snapshot.content.encode("utf-8")
                ).hexdigest():
                    raise QueryToolError(
                        "profile-gap source snapshot checksum mismatch: "
                        f"{snapshot.source_id}"
                    )
                selected[snapshot.source_id] = snapshot
        else:
            raise QueryToolError("profile-gap artifact has no source snapshot")
        missing = sorted(required_source_ids - set(selected))
        if missing:
            raise QueryToolError(
                f"profile-gap source snapshot is missing: {missing[0]}"
            )
        return selected

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
        context_store: QueryContextStore | None = None,
        max_facts: int = 20,
    ) -> None:
        self.store = store
        self.context_store = context_store
        self.allowed_predicates = set(allowed_predicates)
        self.max_facts = max_facts
        self.retrieved_fact_ids: set[str] = set()
        self.retrieved_profile_gap_ids: set[str] = set()
        self.retrieved_context_association_ids: set[str] = set()
        self.retrieved_outcome_summary_ids: set[str] = set()
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
                "evidence_text": str(row.get("evidence_text") or ""),
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

    def get_profile_gaps(
        self,
        *,
        event_id: str,
        fields: list[str],
    ) -> QueryToolResult:
        if event_id not in self.store.event_ids:
            raise QueryToolError(f"unregistered event ID: {event_id}")
        requested = [field.strip() for field in fields if field.strip()]
        if len(requested) != len(fields) or len(requested) != len(set(requested)):
            raise QueryToolError("profile-gap fields must be unique and non-empty")
        if set(requested) - {"impacting_condition"}:
            raise QueryToolError("profile-gap field is outside the current query scope")
        gaps = sorted(
            (
                gap
                for gap in self.store.profile_gaps
                if gap.event_id == event_id and gap.field in requested
            ),
            key=lambda gap: gap.profile_gap_id,
        )
        ids = [gap.profile_gap_id for gap in gaps]
        source_ids = sorted({gap.source_id for gap in gaps})
        self.retrieved_profile_gap_ids.update(ids)
        self.retrieved_source_ids.update(source_ids)
        return QueryToolResult(
            tool="get_profile_gaps",
            profile_gap_ids=ids,
            source_ids=source_ids,
            items=[gap.model_dump(mode="json") for gap in gaps],
        )

    def get_decision_context(self, *, event_id: str) -> QueryToolResult:
        """Read validated, non-causal Weather context for one event."""

        if self.context_store is None:
            raise QueryToolError("decision-context store is not configured")
        try:
            read = self.context_store.get_decision_context(event_id)
        except QueryContextError as exc:
            raise QueryToolError(str(exc)) from exc
        if read.status == "insufficient":
            return QueryToolResult(
                tool="get_decision_context",
                status="insufficient",
            )
        association_ids = [
            association.association_id for association in read.associations
        ]
        fact_ids = [str(row["fact_id"]) for row in read.formal_fact_rows]
        items = [
            {
                "item_type": "context_association",
                **association.model_dump(mode="json"),
            }
            for association in read.associations
        ]
        items.extend(
            {
                "item_type": "formal_weather_fact",
                "fact_id": row["fact_id"],
                "subject": row["subject"],
                "predicate": row["predicate"],
                "object": row.get("object"),
                "object_class": row.get("object_class") or "",
                "source_ids": sorted(_split_source_ids(row.get("source_document"))),
            }
            for row in read.formal_fact_rows
        )
        items.extend(
            {
                "item_type": "source_record",
                **snapshot.model_dump(mode="json"),
            }
            for snapshot in read.source_records
        )
        self.retrieved_context_association_ids.update(association_ids)
        self.retrieved_fact_ids.update(fact_ids)
        self.retrieved_source_ids.update(read.source_ids)
        return QueryToolResult(
            tool="get_decision_context",
            fact_ids=fact_ids,
            context_association_ids=association_ids,
            source_ids=list(read.source_ids),
            items=items,
        )

    def get_outcome_summary(
        self,
        *,
        event_id: str,
        phases: list[str] | tuple[str, ...] = (
            "baseline",
            "active",
            "recovery",
        ),
    ) -> QueryToolResult:
        """Read validated public BTS proxies for the requested phases."""

        if self.context_store is None:
            raise QueryToolError("decision-context store is not configured")
        try:
            read = self.context_store.get_outcome_summaries(
                event_id,
                tuple(phases),
            )
        except QueryContextError as exc:
            raise QueryToolError(str(exc)) from exc
        if read.status == "insufficient":
            return QueryToolResult(
                tool="get_outcome_summary",
                status="insufficient",
            )
        summary_ids = [summary.summary_id for summary in read.summaries]
        self.retrieved_outcome_summary_ids.update(summary_ids)
        self.retrieved_source_ids.update(read.source_ids)
        return QueryToolResult(
            tool="get_outcome_summary",
            outcome_summary_ids=summary_ids,
            source_ids=list(read.source_ids),
            items=[summary.model_dump(mode="json") for summary in read.summaries],
        )


def build_query_tools(gateway: QueryToolGateway) -> list[BaseTool]:
    """Build the five model-visible LangChain tools for one query session."""

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

    @tool("get_profile_gaps", args_schema=GetProfileGapsInput)
    def get_profile_gaps(event_id: str, fields: list[str]) -> str:
        """Read source-bound fields excluded from the active formal profile."""

        return gateway.get_profile_gaps(
            event_id=event_id,
            fields=fields,
        ).model_dump_json()

    return [
        find_events,
        get_event_facts,
        get_neighbors,
        get_provenance,
        get_profile_gaps,
    ]


def build_context_query_tools(gateway: QueryToolGateway) -> list[BaseTool]:
    """Build deterministic context tools kept outside the model-visible surface."""

    @tool("get_decision_context", args_schema=GetDecisionContextInput)
    def get_decision_context(event_id: str) -> str:
        """Read validated non-causal Weather context for one registered event."""

        return gateway.get_decision_context(event_id=event_id).model_dump_json()

    @tool("get_outcome_summary", args_schema=GetOutcomeSummaryInput)
    def get_outcome_summary(
        event_id: str,
        phases: list[Literal["baseline", "active", "recovery"]],
    ) -> str:
        """Read validated public BTS outcome proxies for selected phases."""

        return gateway.get_outcome_summary(
            event_id=event_id,
            phases=phases,
        ).model_dump_json()

    return [get_decision_context, get_outcome_summary]


def tool_registry(tools: list[BaseTool]) -> dict[str, BaseTool]:
    """Index tools by their framework-visible names."""

    registry = {tool_.name: tool_ for tool_ in tools}
    if len(registry) != len(tools):
        raise QueryToolError("duplicate Query Agent tool name")
    return registry
