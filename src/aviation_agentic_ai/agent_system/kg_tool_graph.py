"""Bounded native-tool loop for the Knowledge Graph Construction Agent.

The internal LangGraph is intentionally small:

    model selects read-only context tools
      -> deterministic tools return ToolMessages
      -> model emits the existing text Graph Patch
      -> deterministic parser classifies the response

The Formal Graph Kernel remains the publication gate in the outer ingest
workflow. This subgraph does not write RDF, Neo4j, or any other graph store.
"""

from __future__ import annotations

import json
import operator
import time
from typing import Annotated, Any, TypedDict

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph

from aviation_agentic_ai.agent_system.audit import (
    sanitize_json_value,
    sanitize_text,
)
from aviation_agentic_ai.agent_system.contracts import (
    AgentResult,
    AgentStatus,
    EvidenceCard,
    ModelCallRecord,
    ToolTraceEntry,
)
from aviation_agentic_ai.agent_system.graph_patch import (
    PATCH_OK,
    PATCH_PARSED_EMPTY,
    classify_graph_patch_response,
    parse_graph_patch_block,
)
from aviation_agentic_ai.agent_system.kg_tools import (
    KGConstructionToolResult,
    kg_tool_registry,
)
from aviation_agentic_ai.agent_system.prompts import (
    DEFAULT_PROMPT_CATALOG,
    assemble_prompt,
)
from aviation_agentic_ai.agent_system.tool_model import ToolCallingModel

MAX_KG_MODEL_CALLS = 2
MAX_KG_TOOL_CALLS = 3
MAX_KG_CALLS_PER_TOOL = 1
_REQUIRED_BASE_TOOLS = {"get_schema_context", "get_source_evidence"}


class KGToolState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    model_calls: Annotated[list[ModelCallRecord], operator.add]
    tool_traces: Annotated[list[ToolTraceEntry], operator.add]
    pending_tool_calls: list[dict[str, Any]]
    model_call_count: int
    tool_call_count: int
    observed_tools: list[str]
    observed_result_refs: list[str]
    raw_patch: str
    status: str
    failure_reason: str


def _base_messages(
    *,
    event_uri: str,
    event_class: str,
    schema_slice_id: str,
    allowed_source_ids: set[str],
    canonical_entities: dict[str, str],
    evidence_cards: dict[str, EvidenceCard],
    catalog_path: str,
) -> list[BaseMessage]:
    assembled = assemble_prompt(
        "knowledge_graph_construction",
        {
            "event_uri": event_uri,
            "event_class": event_class,
            "schema_slice_id": schema_slice_id,
            "allowed_source_ids": "; ".join(sorted(allowed_source_ids)),
            "available_canonical_refs": (
                "\n".join(f"- {ref}" for ref in sorted(canonical_entities))
                or "- NONE"
            ),
            "available_evidence_roles": "\n".join(
                f"- {role}: {card.status.value}"
                for role, card in sorted(evidence_cards.items())
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


def _message_text(message: AIMessage) -> str:
    if isinstance(message.content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in message.content
        )
    return str(message.content or "")


def _call_signature(call: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(call.get("id") or call.get("call_id") or ""),
        str(call.get("name") or ""),
        json.dumps(
            sanitize_json_value(call.get("args", call.get("arguments", {}))),
            sort_keys=True,
            separators=(",", ":"),
        ),
    )


def _message_call_signatures(message: AIMessage) -> list[tuple[str, str, str]]:
    return [_call_signature(dict(call)) for call in message.tool_calls]


def _record_call_signatures(record: ModelCallRecord) -> list[tuple[str, str, str]]:
    return [
        _call_signature(
            {
                "call_id": call.call_id,
                "name": call.name,
                "arguments": call.arguments,
            }
        )
        for call in record.tool_calls
    ]


def _safe_parameters(arguments: dict[str, Any]) -> dict[str, str]:
    sanitized = sanitize_json_value(arguments)
    if not isinstance(sanitized, dict):
        return {}
    return {
        str(key): json.dumps(value, sort_keys=True, default=str)
        for key, value in sanitized.items()
    }


def build_kg_tool_graph(
    *,
    model: ToolCallingModel,
    tools: list[BaseTool],
    required_tool_names: set[str],
    required_evidence_refs: set[str],
) -> Any:
    """Compile one model -> tools -> model construction session."""

    registry = kg_tool_registry(tools)

    def select_context_node(state: KGToolState) -> dict[str, Any]:
        if int(state.get("model_call_count", 0)) >= MAX_KG_MODEL_CALLS:
            return {
                "status": "blocked",
                "failure_reason": "KG Construction Agent model-call budget exceeded",
                "pending_tool_calls": [],
            }
        turn = model.invoke(list(state["messages"]), phase="select_tool")
        update: dict[str, Any] = {
            "model_calls": [turn.record],
            "model_call_count": int(state.get("model_call_count", 0)) + 1,
            "pending_tool_calls": [],
        }
        if turn.record.error:
            update.update(status="blocked", failure_reason=turn.record.error)
            return update
        if turn.message is None:
            update.update(
                status="blocked",
                failure_reason="provider returned no AI message",
            )
            return update
        if _message_call_signatures(turn.message) != _record_call_signatures(
            turn.record
        ):
            update.update(
                status="blocked",
                failure_reason=(
                    "native tool calls do not match the persisted model audit"
                ),
            )
            return update
        calls = [dict(call) for call in turn.message.tool_calls]
        if not calls:
            update.update(
                status="blocked",
                failure_reason=(
                    "KG Construction Agent generated a patch before inspecting "
                    "the registered context tools"
                ),
            )
            return update
        if len(calls) > MAX_KG_TOOL_CALLS:
            update.update(
                status="blocked",
                failure_reason="KG Construction Agent tool-call budget exceeded",
            )
            return update

        call_ids: set[str] = set()
        names: set[str] = set()
        for call in calls:
            call_id = str(call.get("id") or "").strip()
            name = str(call.get("name") or "").strip()
            arguments = call.get("args")
            if not call_id or call_id in call_ids:
                update.update(
                    status="blocked",
                    failure_reason="missing or duplicate native tool-call ID",
                )
                return update
            if name not in registry:
                update.update(
                    status="blocked",
                    failure_reason=f"unknown KG Construction Agent tool: {name}",
                )
                return update
            if name in names:
                update.update(
                    status="blocked",
                    failure_reason=f"per-tool budget exceeded: {name}",
                )
                return update
            if not isinstance(arguments, dict):
                update.update(
                    status="blocked",
                    failure_reason=f"invalid arguments for construction tool: {name}",
                )
                return update
            call_ids.add(call_id)
            names.add(name)

        if not required_tool_names.issubset(names):
            update.update(
                status="blocked",
                failure_reason=(
                    "KG Construction Agent did not select required context tools: "
                    + ", ".join(sorted(required_tool_names - names))
                ),
            )
            return update
        update["messages"] = [turn.message]
        update["pending_tool_calls"] = calls
        return update

    def context_tools_node(state: KGToolState) -> dict[str, Any]:
        pending = list(state.get("pending_tool_calls", []))
        if int(state.get("tool_call_count", 0)) + len(pending) > MAX_KG_TOOL_CALLS:
            return {
                "status": "blocked",
                "failure_reason": "KG Construction Agent tool-call budget exceeded",
                "pending_tool_calls": [],
            }

        tool_messages: list[ToolMessage] = []
        traces: list[ToolTraceEntry] = []
        observed_tools: set[str] = set(state.get("observed_tools", []))
        observed_refs: set[str] = set(state.get("observed_result_refs", []))
        for call in pending:
            call_id = str(call["id"])
            name = str(call["name"])
            arguments = dict(call["args"])
            started = time.perf_counter()
            try:
                content = registry[name].invoke(arguments)
                result = KGConstructionToolResult.model_validate_json(str(content))
                if result.tool != name:
                    raise ValueError(
                        f"tool result name mismatch: expected {name}, got {result.tool}"
                    )
            except Exception as exc:
                duration = (time.perf_counter() - started) * 1000.0
                trace = ToolTraceEntry(
                    tool_call_id=call_id,
                    tool=name,
                    parameters=_safe_parameters(arguments),
                    status="blocked",
                    duration_ms=duration,
                    error=sanitize_text(f"{type(exc).__name__}: {exc}"),
                )
                return {
                    "status": "blocked",
                    "failure_reason": trace.error or "construction tool failed",
                    "pending_tool_calls": [],
                    "tool_traces": traces + [trace],
                    "tool_call_count": int(state.get("tool_call_count", 0))
                    + len(traces)
                    + 1,
                }
            duration = (time.perf_counter() - started) * 1000.0
            tool_messages.append(
                ToolMessage(content=str(content), tool_call_id=call_id)
            )
            traces.append(
                ToolTraceEntry(
                    tool_call_id=call_id,
                    tool=name,
                    parameters=_safe_parameters(arguments),
                    result_refs=result.result_refs,
                    source_ids=result.source_ids,
                    status="ok",
                    duration_ms=duration,
                )
            )
            observed_tools.add(name)
            observed_refs.update(result.result_refs)

        missing_refs = sorted(required_evidence_refs - observed_refs)
        if missing_refs:
            return {
                "status": "blocked",
                "failure_reason": (
                    "KG Construction Agent did not retrieve required evidence: "
                    + ", ".join(missing_refs)
                ),
                "pending_tool_calls": [],
                "tool_traces": traces,
                "tool_call_count": int(state.get("tool_call_count", 0))
                + len(traces),
                "observed_tools": sorted(observed_tools),
                "observed_result_refs": sorted(observed_refs),
            }
        return {
            "messages": tool_messages,
            "tool_traces": traces,
            "tool_call_count": int(state.get("tool_call_count", 0)) + len(traces),
            "pending_tool_calls": [],
            "observed_tools": sorted(observed_tools),
            "observed_result_refs": sorted(observed_refs),
        }

    def draft_patch_node(state: KGToolState) -> dict[str, Any]:
        if int(state.get("model_call_count", 0)) >= MAX_KG_MODEL_CALLS:
            return {
                "status": "blocked",
                "failure_reason": "KG Construction Agent model-call budget exceeded",
            }
        turn = model.invoke(list(state["messages"]), phase="final_answer")
        update: dict[str, Any] = {
            "model_calls": [turn.record],
            "model_call_count": int(state.get("model_call_count", 0)) + 1,
        }
        if turn.record.error:
            update.update(status="blocked", failure_reason=turn.record.error)
            return update
        if turn.message is None:
            update.update(
                status="blocked",
                failure_reason="provider returned no AI message",
            )
            return update
        if turn.message.tool_calls:
            update.update(
                status="blocked",
                failure_reason=(
                    "KG Construction Agent requested another tool after the "
                    "one-round context budget"
                ),
            )
            return update
        raw_patch = _message_text(turn.message).strip()
        if not raw_patch:
            update.update(
                status="blocked",
                failure_reason="provider returned an empty Graph Patch",
            )
            return update
        update["messages"] = [turn.message]
        update["raw_patch"] = raw_patch
        return update

    def route_after_step(state: KGToolState) -> str:
        return "end" if state.get("status") == "blocked" else "continue"

    graph = StateGraph(KGToolState)
    graph.add_node("select_context", select_context_node)
    graph.add_node("context_tools", context_tools_node)
    graph.add_node("draft_patch", draft_patch_node)
    graph.add_edge(START, "select_context")
    graph.add_conditional_edges(
        "select_context",
        route_after_step,
        {"continue": "context_tools", "end": END},
    )
    graph.add_conditional_edges(
        "context_tools",
        route_after_step,
        {"continue": "draft_patch", "end": END},
    )
    graph.add_edge("draft_patch", END)
    return graph.compile()


def run_kg_tool_agent(
    *,
    model: ToolCallingModel,
    tools: list[BaseTool],
    event_uri: str,
    event_class: str,
    schema_slice_id: str,
    allowed_source_ids: set[str],
    canonical_entities: dict[str, str],
    evidence_cards: dict[str, EvidenceCard],
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
) -> AgentResult:
    """Run one bounded construction-tool session and classify its patch."""

    if not event_class:
        return AgentResult(
            status=AgentStatus.ABSTAIN,
            failure_reason="missing resolved event type; no graph constructed",
        )
    required_tool_names = set(_REQUIRED_BASE_TOOLS)
    if canonical_entities:
        required_tool_names.add("resolve_canonical_ref")
    required_evidence_refs = {
        f"evidence:{role}"
        for role, card in evidence_cards.items()
        if role in {"advisory", "terminology"}
        or card.status == AgentStatus.RESOLVED
    }
    graph = build_kg_tool_graph(
        model=model,
        tools=tools,
        required_tool_names=required_tool_names,
        required_evidence_refs=required_evidence_refs,
    )
    final = graph.invoke(
        {
            "messages": _base_messages(
                event_uri=event_uri,
                event_class=event_class,
                schema_slice_id=schema_slice_id,
                allowed_source_ids=allowed_source_ids,
                canonical_entities=canonical_entities,
                evidence_cards=evidence_cards,
                catalog_path=catalog_path,
            ),
            "model_calls": [],
            "tool_traces": [],
            "pending_tool_calls": [],
            "model_call_count": 0,
            "tool_call_count": 0,
            "observed_tools": [],
            "observed_result_refs": [],
            "raw_patch": "",
            "status": "",
            "failure_reason": "",
        }
    )
    model_calls = list(final.get("model_calls", []))
    tool_traces = list(final.get("tool_traces", []))
    source_ids = sorted(allowed_source_ids)
    if final.get("status") == "blocked":
        card = EvidenceCard(
            agent_role="knowledge_graph_construction",
            status=AgentStatus.BLOCKED,
            source_ids=source_ids,
            tool_trace=tool_traces,
            decision_basis=str(final.get("failure_reason") or "blocked"),
        )
        return AgentResult(
            status=AgentStatus.BLOCKED,
            evidence_card=card,
            model_calls=model_calls,
            failure_reason=str(final.get("failure_reason") or "blocked"),
        )

    raw_patch = str(final.get("raw_patch") or "")
    block = parse_graph_patch_block(raw_patch)
    outcome, reason = classify_graph_patch_response(raw_patch, block)
    if outcome == PATCH_PARSED_EMPTY:
        status = AgentStatus.ABSTAIN
        decision = "GRAPH_PATCH parsed with zero formal facts"
        graph_patch = None
    elif outcome != PATCH_OK:
        status = AgentStatus.BLOCKED
        decision = f"fail-closed: {reason}"
        graph_patch = None
    else:
        status = AgentStatus.RESOLVED
        decision = (
            f"selected {len(tool_traces)} context tools and generated "
            f"{len(block.patch_lines)} patch lines"
        )
        graph_patch = block
    card = EvidenceCard(
        agent_role="knowledge_graph_construction",
        status=status,
        source_ids=source_ids,
        canonical_refs=sorted(canonical_entities),
        tool_trace=tool_traces,
        decision_basis=decision,
    )
    return AgentResult(
        status=status,
        artifact_ref="graph_patch" if graph_patch is not None else None,
        evidence_card=card,
        model_calls=model_calls,
        graph_patch=graph_patch,
        failure_reason=reason if status != AgentStatus.RESOLVED else None,
    )


__all__ = [
    "KGToolState",
    "MAX_KG_MODEL_CALLS",
    "MAX_KG_TOOL_CALLS",
    "build_kg_tool_graph",
    "run_kg_tool_agent",
]
