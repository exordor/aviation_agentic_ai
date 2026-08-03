"""Registered read-only HybridRAG tool families.

The gateway owns query semantics and scope enforcement; this module owns the
model-facing tool contracts.  Keeping registration separate makes it possible
to add another retrieval family without enlarging the gateway implementation.
"""

from __future__ import annotations

from typing import Any, Literal

from langchain_core.tools import BaseTool, tool

from aviation_agentic_ai.agent_system.hybrid_query_tools import (
    EventInput,
    FindTMIEventsInput,
    PublicObservationsInput,
    ReadSourceInput,
    SearchSourceTextInput,
    SemanticSearchSourcesInput,
    SimilarTMIEventsInput,
    TMIEventGraphInput,
)

ObservationPhase = Literal["baseline", "active", "recovery"]
GraphView = Literal["edges", "evidence_paths"]


def build_query_tool_families(gateway: Any) -> list[BaseTool]:
    """Expose the bounded source, TMI, and graph read-only tool families."""

    @tool("find_tmi_events", args_schema=FindTMIEventsInput)
    def find_tmi_events_tool(**kwargs: object) -> dict[str, object]:
        """Find TMI events using exact filters and bounded paging."""

        return gateway.find_tmi_events(**kwargs).model_dump(mode="json")

    @tool("read_tmi_event_facts", args_schema=EventInput)
    def read_tmi_event_facts_tool(event_id: str) -> dict[str, object]:
        """Read formal TMI facts and the declared-reason state."""

        return gateway.read_tmi_event_facts(event_id=event_id).model_dump(mode="json")

    @tool("read_tmi_operational_context", args_schema=EventInput)
    def read_tmi_operational_context_tool(event_id: str) -> dict[str, object]:
        """Read retained Weather context without treating it as rationale."""

        return gateway.read_tmi_operational_context(
            event_id=event_id
        ).model_dump(mode="json")

    @tool("read_public_observations", args_schema=PublicObservationsInput)
    def read_public_observations_tool(
        event_id: str,
        phases: tuple[ObservationPhase, ...],
    ) -> dict[str, object]:
        """Read BTS-reported public observations for selected phases."""

        return gateway.read_public_observations(
            event_id=event_id,
            phases=phases,
        ).model_dump(mode="json")

    @tool("read_tmi_event_graph", args_schema=TMIEventGraphInput)
    def read_tmi_event_graph_tool(
        event_id: str,
        view: GraphView = "edges",
        entity_iri: str | None = None,
        direction: Literal["out", "in"] = "out",
        predicate_iris: tuple[str, ...] = (),
        limit: int = 50,
    ) -> dict[str, object]:
        """Read bounded formal edges or reviewed non-causal paths."""

        return gateway.read_tmi_event_graph(
            event_id=event_id,
            view=view,
            entity_iri=entity_iri,
            direction=direction,
            predicate_iris=predicate_iris,
            limit=limit,
        ).model_dump(mode="json")

    @tool("find_similar_tmi_events", args_schema=SimilarTMIEventsInput)
    def find_similar_tmi_events_tool(**kwargs: object) -> dict[str, object]:
        """Find metadata-conditioned historical TMI event candidates."""

        return gateway.find_similar_tmi_events(**kwargs).model_dump(mode="json")

    @tool("search_source_text", args_schema=SearchSourceTextInput)
    def search_source_text_tool(**kwargs: object) -> dict[str, object]:
        """Find lexical source candidates; verify with read_source."""

        return gateway.search_source_text(**kwargs).model_dump(mode="json")

    @tool("semantic_search_sources", args_schema=SemanticSearchSourcesInput)
    def semantic_search_sources_tool(**kwargs: object) -> dict[str, object]:
        """Find semantic source candidates; verify with read_source."""

        return gateway.semantic_search_sources(**kwargs).model_dump(mode="json")

    @tool("read_source", args_schema=ReadSourceInput)
    def read_source_tool(**kwargs: object) -> dict[str, object]:
        """Read exact bounded source text with immutable anchor support."""

        return gateway.read_source(**kwargs).model_dump(mode="json")

    return [
        find_tmi_events_tool,
        read_tmi_event_facts_tool,
        read_tmi_operational_context_tool,
        read_public_observations_tool,
        read_tmi_event_graph_tool,
        find_similar_tmi_events_tool,
        search_source_text_tool,
        semantic_search_sources_tool,
        read_source_tool,
    ]


__all__ = ["build_query_tool_families"]
