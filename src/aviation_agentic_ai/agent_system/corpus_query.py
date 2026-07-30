"""LLM-routed HybridRAG queries over the canonical decision-case corpus."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Literal

from langchain_core.tools import BaseTool

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryScope,
    QueryToolOutcome,
)
from aviation_agentic_ai.agent_system.corpus_store import CorpusQueryStore
from aviation_agentic_ai.agent_system.hybrid_query_agent import (
    run_hybrid_query_agent,
)
from aviation_agentic_ai.agent_system.hybrid_query_tools import (
    HybridQueryGateway,
    build_hybrid_query_tools,
)
from aviation_agentic_ai.agent_system.tool_model import ToolCallingModel


ReasonStatus = Literal["formal", "profile_gap", "missing"]
ModelFactory = Callable[[list[BaseTool]], ToolCallingModel]


def answer_corpus_question(
    *,
    corpus_dir: str | Path,
    question: str,
    event_id: str | None = None,
    event_type_iri: str | None = None,
    facility_id: str | None = None,
    reason_status: ReasonStatus | None = None,
    reason_value: str | None = None,
    candidate_scope: Literal["archive", "prior"] = "archive",
    offset: int = 0,
    limit: int = 20,
    model_factory: ModelFactory | None = None,
) -> QueryToolOutcome:
    """Run the always-activated Query Agent over bounded corpus read tools."""

    try:
        store = CorpusQueryStore(corpus_dir)
        scope = HybridQueryScope(
            event_id=event_id,
            event_type_iri=event_type_iri,
            facility_id=facility_id,
            reason_status=reason_status,
            reason_value=reason_value,
            candidate_scope=candidate_scope,
            offset=offset,
            limit=limit,
        )
    except (OSError, ValueError) as exc:
        return QueryToolOutcome(
            status="blocked",
            failure_reason=f"query preflight failed: {exc}",
        )
    if model_factory is None:
        return QueryToolOutcome(
            status="blocked",
            failure_reason="Hybrid Query Agent model factory is unavailable",
        )
    gateway = HybridQueryGateway(store=store, scope=scope)
    tools = build_hybrid_query_tools(gateway)
    return run_hybrid_query_agent(
        question=question,
        scope=scope,
        tools=tools,
        model_factory=model_factory,
    )


__all__ = ["answer_corpus_question"]
