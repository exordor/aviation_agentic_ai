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
from aviation_agentic_ai.agent_system.hybrid_query_tools import (
    HybridQueryGateway,
    build_hybrid_query_tools,
)
from aviation_agentic_ai.agent_system.query_runtime import QueryRuntime
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
    return run_hybrid_query_agent(
        question=question,
        scope=scope,
        tools=build_hybrid_query_tools(gateway),
        model_factory=model_factory,
    )


__all__ = ["answer_question"]
