"""Natural-language HybridRAG queries over the live aviation knowledge runtime."""

from __future__ import annotations

from collections.abc import Callable

from langchain_core.tools import BaseTool

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryScope,
    QueryToolOutcome,
)
from aviation_agentic_ai.agent_system.hybrid_query_agent import (
    run_hybrid_query_agent,
)
from aviation_agentic_ai.agent_system.flight_airspace_query_tools import (
    FlightAirspaceQueryGateway,
    build_flight_airspace_query_tools,
)
from aviation_agentic_ai.agent_system.hybrid_query_tools import (
    HybridQueryGateway,
    build_hybrid_query_tools,
)
from aviation_agentic_ai.agent_system.query_runtime import QueryRuntime
from aviation_agentic_ai.agent_system.query_tool_registry import (
    QueryRoutingBlocked,
    build_query_route_tool,
    build_query_tool_registry,
    select_query_tools,
)
from aviation_agentic_ai.agent_system.tool_model import ToolCallingModel


ModelFactory = Callable[[list[BaseTool]], ToolCallingModel]


def answer_question(
    *,
    runtime: QueryRuntime,
    question: str,
    scope: HybridQueryScope,
    model_factory: ModelFactory | None,
) -> QueryToolOutcome:
    """Always activate the bounded Query Agent over the live read runtime."""

    if model_factory is None:
        return QueryToolOutcome(
            status="blocked",
            failure_reason="Hybrid Query Agent model factory is unavailable",
        )
    gateway = HybridQueryGateway(runtime=runtime, scope=scope)
    flight_airspace_gateway = FlightAirspaceQueryGateway(
        runtime=runtime,
        scope=scope,
    )
    registry = build_query_tool_registry(
        [
            *build_hybrid_query_tools(gateway),
            *build_flight_airspace_query_tools(flight_airspace_gateway),
        ]
    )
    route_tool = build_query_route_tool()
    try:
        route_model = model_factory([route_tool])
        selected_tools, route_trace, route_record = select_query_tools(
            question=question,
            scope=scope,
            registry=registry,
            model=route_model,
        )
    except QueryRoutingBlocked as exc:
        return QueryToolOutcome(
            status="blocked",
            failure_reason=str(exc),
            model_calls=[exc.record] if exc.record is not None else [],
        )
    except Exception as exc:
        return QueryToolOutcome(
            status="blocked",
            failure_reason=(
                "Hybrid Query Agent routing construction failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        )
    outcome = run_hybrid_query_agent(
        question=question,
        scope=scope,
        tools=selected_tools,
        model_factory=model_factory,
    )
    routed_records = [route_record]
    routed_records.extend(
        record.model_copy(update={"attempt": index})
        for index, record in enumerate(outcome.model_calls, start=2)
    )
    return outcome.model_copy(
        update={
            "route_trace": route_trace,
            "model_calls": routed_records,
        }
    )


__all__ = ["answer_question"]
