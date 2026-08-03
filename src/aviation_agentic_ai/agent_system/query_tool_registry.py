"""Shared capability registry and model-routed tool-family selection."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import BaseTool, tool
from pydantic import Field, ValidationError

from aviation_agentic_ai.agent_system.audit import sanitize_text
from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryScope,
    ModelCallRecord,
    QueryRouteTrace,
    StrictModel,
)
from aviation_agentic_ai.agent_system.prompts import (
    DEFAULT_PROMPT_CATALOG,
    assemble_prompt,
)
from aviation_agentic_ai.agent_system.tool_model import ToolCallingModel


QUERY_ROUTE_TOOL_NAME = "select_query_tool_families"


class QueryToolFamily(StrEnum):
    SOURCE = "source"
    TMI = "tmi"
    FLIGHT_AIRSPACE = "flight_airspace"
    KNOWLEDGE = "knowledge"
    WEB = "web"


class QueryRouteDecision(StrictModel):
    families: tuple[QueryToolFamily, ...] = Field(min_length=1, max_length=5)


@dataclass(frozen=True)
class QueryToolFamilySpec:
    family: QueryToolFamily
    description: str
    tool_names: tuple[str, ...]


@dataclass(frozen=True)
class QueryToolRegistry:
    tools_by_name: Mapping[str, BaseTool]
    family_specs: Mapping[QueryToolFamily, QueryToolFamilySpec]

    @property
    def evidence_tool_names(self) -> frozenset[str]:
        return frozenset(self.tools_by_name)

    def routing_cards(self) -> tuple[dict[str, object], ...]:
        return tuple(
            {
                "family": spec.family.value,
                "description": spec.description,
            }
            for spec in self.family_specs.values()
        )

    def tools_for(
        self,
        families: Sequence[QueryToolFamily],
    ) -> list[BaseTool]:
        selected_names = {
            name
            for family in families
            for name in self.family_specs[family].tool_names
        }
        return [
            tool
            for name, tool in self.tools_by_name.items()
            if name in selected_names
        ]


SOURCE_TOOL_NAMES = (
    "search_source_text",
    "semantic_search_sources",
    "read_source",
)
TMI_TOOL_NAMES = (
    "find_tmi_events",
    "read_tmi_event_facts",
    "read_tmi_operational_context",
    "read_public_observations",
    "read_tmi_event_graph",
    "find_similar_tmi_events",
)
FLIGHT_AIRSPACE_TOOL_NAMES = (
    "find_flights",
    "read_flight",
    "find_airports",
    "read_flight_trajectory",
    "find_sector_passages",
    "analyze_sector_traffic",
    "find_flight_weather_associations",
    "find_tmi_applicability_candidates",
    "read_aviation_graph",
)
KNOWLEDGE_TOOL_NAMES = (
    "search_knowledge_entities",
    "find_knowledge_roots",
    "read_knowledge_graph",
    "read_source",
)
WEB_TOOL_NAMES = (
    "web_search",
    "web_fetch",
    "web_extract",
)
QUERY_EVIDENCE_TOOL_NAMES = frozenset(
    (
        *SOURCE_TOOL_NAMES,
        *TMI_TOOL_NAMES,
        *FLIGHT_AIRSPACE_TOOL_NAMES,
        *KNOWLEDGE_TOOL_NAMES,
    )
)
OPTIONAL_QUERY_EVIDENCE_TOOL_NAMES = frozenset(WEB_TOOL_NAMES)
QUERY_CONTROL_TOOL_NAMES = frozenset({QUERY_ROUTE_TOOL_NAME})


def query_tool_model_role(tools: Sequence[BaseTool]) -> str:
    """Return the registered prompt role for one dynamically bound tool set."""

    names = frozenset(candidate.name for candidate in tools)
    if names == QUERY_CONTROL_TOOL_NAMES:
        return "query_router"
    if names and names <= (
        QUERY_EVIDENCE_TOOL_NAMES | OPTIONAL_QUERY_EVIDENCE_TOOL_NAMES
    ):
        return "query"
    raise ValueError(f"unsupported Query Agent tool binding: {sorted(names)}")


def build_query_tool_registry(tools: Iterable[BaseTool]) -> QueryToolRegistry:
    ordered_tools: dict[str, BaseTool] = {}
    for candidate in tools:
        if candidate.name in ordered_tools:
            raise ValueError(f"duplicate query tool name: {candidate.name}")
        ordered_tools[candidate.name] = candidate
    missing = QUERY_EVIDENCE_TOOL_NAMES.difference(ordered_tools)
    extra = set(ordered_tools).difference(
        QUERY_EVIDENCE_TOOL_NAMES | OPTIONAL_QUERY_EVIDENCE_TOOL_NAMES
    )
    optional = set(ordered_tools).intersection(OPTIONAL_QUERY_EVIDENCE_TOOL_NAMES)
    if optional and optional != set(OPTIONAL_QUERY_EVIDENCE_TOOL_NAMES):
        raise ValueError(
            "query tool registry must expose all optional web tools together"
        )
    if missing or extra:
        raise ValueError(
            "query tool registry does not match the active contract: "
            f"missing={sorted(missing)}, extra={sorted(extra)}"
        )
    specs = {
        QueryToolFamily.SOURCE: QueryToolFamilySpec(
            family=QueryToolFamily.SOURCE,
            description=(
                "Lexical or semantic source discovery followed by exact "
                "source-version and anchor reads."
            ),
            tool_names=SOURCE_TOOL_NAMES,
        ),
        QueryToolFamily.TMI: QueryToolFamilySpec(
            family=QueryToolFamily.TMI,
            description=(
                "Persisted ATCSCC traffic-management event records, declared "
                "reasons, Weather context, BTS observations, event graphs, "
                "and TMI similarity."
            ),
            tool_names=TMI_TOOL_NAMES,
        ),
        QueryToolFamily.FLIGHT_AIRSPACE: QueryToolFamilySpec(
            family=QueryToolFamily.FLIGHT_AIRSPACE,
            description=(
                "Flights, airports and ARTCC roles, routes, track points, "
                "sectors, temporal Weather associations, and rule-derived TMI "
                "applicability over generic knowledge roots."
            ),
            tool_names=FLIGHT_AIRSPACE_TOOL_NAMES,
        ),
        QueryToolFamily.KNOWLEDGE: QueryToolFamilySpec(
            family=QueryToolFamily.KNOWLEDGE,
            description=(
                "Ontology-constructed knowledge entities and graph facts from "
                "configured documents, with the shared exact source reader "
                "for text and anchor evidence."
            ),
            tool_names=KNOWLEDGE_TOOL_NAMES,
        ),
    }
    if optional:
        specs[QueryToolFamily.WEB] = QueryToolFamilySpec(
            family=QueryToolFamily.WEB,
            description=(
                "Explicitly authorized Web Evidence candidates and exact, "
                "source-bound fetch/extract reads; search results alone are "
                "not evidence."
            ),
            tool_names=WEB_TOOL_NAMES,
        )
    return QueryToolRegistry(tools_by_name=ordered_tools, family_specs=specs)


def build_query_route_tool() -> BaseTool:
    @tool(QUERY_ROUTE_TOOL_NAME, args_schema=QueryRouteDecision)
    def select_query_tool_families(
        families: tuple[QueryToolFamily, ...],
    ) -> dict[str, object]:
        """Select one or more bounded evidence-tool families for this query."""

        return {"families": [family.value for family in families]}

    return select_query_tool_families


def _router_messages(
    *,
    question: str,
    scope: HybridQueryScope,
    registry: QueryToolRegistry,
    catalog_path: str,
) -> list[BaseMessage]:
    assembled = assemble_prompt(
        "query_router",
        {
            "user_question": question,
            "query_scope": json.dumps(
                scope.model_dump(mode="json"),
                sort_keys=True,
                separators=(",", ":"),
            ),
            "family_cards": json.dumps(
                registry.routing_cards(),
                sort_keys=True,
                separators=(",", ":"),
            ),
        },
        catalog_path=catalog_path,
    )
    messages: list[BaseMessage] = []
    for role, content in assembled.messages:
        if role == "system":
            messages.append(SystemMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        else:
            messages.append(HumanMessage(content=content))
    return messages


class QueryRoutingBlocked(RuntimeError):
    def __init__(self, message: str, *, record: ModelCallRecord | None = None) -> None:
        super().__init__(sanitize_text(message))
        self.record = record


def select_query_tools(
    *,
    question: str,
    scope: HybridQueryScope,
    registry: QueryToolRegistry,
    model: ToolCallingModel,
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
) -> tuple[list[BaseTool], QueryRouteTrace, ModelCallRecord]:
    try:
        turn = model.invoke(
            _router_messages(
                question=question,
                scope=scope,
                registry=registry,
                catalog_path=catalog_path,
            ),
            phase="select_tool",
        )
    except Exception as exc:
        raise QueryRoutingBlocked(
            f"Query Agent routing provider failed: {type(exc).__name__}: {exc}"
        ) from exc
    if turn.record.error:
        raise QueryRoutingBlocked(turn.record.error, record=turn.record)
    if turn.message is None:
        raise QueryRoutingBlocked(
            "provider returned no query-routing message",
            record=turn.record,
        )
    calls = [dict(call) for call in turn.message.tool_calls]
    if len(calls) != 1:
        raise QueryRoutingBlocked(
            "Query Agent routing must select exactly one control tool",
            record=turn.record,
        )
    call = calls[0]
    if str(call.get("name") or "") != QUERY_ROUTE_TOOL_NAME:
        raise QueryRoutingBlocked(
            "Query Agent routing selected an unknown control tool",
            record=turn.record,
        )
    try:
        decision = QueryRouteDecision.model_validate(call.get("args"))
    except ValidationError as exc:
        raise QueryRoutingBlocked(
            f"Query Agent routing returned invalid families: {exc}",
            record=turn.record,
        ) from exc
    families = tuple(dict.fromkeys(decision.families))
    selected_tools = registry.tools_for(families)
    if not selected_tools:
        raise QueryRoutingBlocked(
            "Query Agent routing selected no evidence tools",
            record=turn.record,
        )
    trace = QueryRouteTrace(
        status="selected",
        selected_families=tuple(family.value for family in families),
        available_families=tuple(family.value for family in registry.family_specs),
        selected_tool_names=tuple(tool.name for tool in selected_tools),
    )
    return selected_tools, trace, turn.record


__all__ = [
    "FLIGHT_AIRSPACE_TOOL_NAMES",
    "KNOWLEDGE_TOOL_NAMES",
    "QUERY_CONTROL_TOOL_NAMES",
    "QUERY_EVIDENCE_TOOL_NAMES",
    "OPTIONAL_QUERY_EVIDENCE_TOOL_NAMES",
    "QUERY_ROUTE_TOOL_NAME",
    "QueryRouteDecision",
    "QueryRoutingBlocked",
    "QueryToolFamily",
    "QueryToolRegistry",
    "SOURCE_TOOL_NAMES",
    "TMI_TOOL_NAMES",
    "WEB_TOOL_NAMES",
    "build_query_route_tool",
    "build_query_tool_registry",
    "query_tool_model_role",
    "select_query_tools",
]
