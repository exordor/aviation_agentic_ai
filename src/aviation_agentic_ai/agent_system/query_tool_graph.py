"""Bounded LangGraph loop for the native tool-using Query Agent."""

from __future__ import annotations

import json
import operator
import re
import time
from collections.abc import Callable
from enum import Enum
from pathlib import Path
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
from langgraph.graph.message import add_messages

from aviation_agentic_ai.agent_system.agents import parse_query_answer_claims
from aviation_agentic_ai.agent_system.audit import (
    sanitize_json_value,
    sanitize_text,
)
from aviation_agentic_ai.agent_system.contracts import (
    ModelCallRecord,
    QueryToolOutcome,
    QueryToolTrace,
)
from aviation_agentic_ai.agent_system.prompts import (
    DEFAULT_PROMPT_CATALOG,
    assemble_prompt,
)
from aviation_agentic_ai.agent_system.query import ontology_labels_for
from aviation_agentic_ai.agent_system.query_tools import (
    QueryGraphStore,
    QueryPredicate,
    QueryToolError,
    QueryToolGateway,
    QueryToolResult,
    build_query_tools,
    tool_registry,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.tool_model import ToolCallingModel

REGISTERED_COMPETENCY_QUESTION = (
    "What traffic management measure, controlled airport, and effective time "
    "are recorded in this advisory?"
)
MEASURE_QUESTION = "What traffic management measure was published?"
CONTROLLED_FACILITY_QUESTION = "Which airport was controlled?"
OPERATIONAL_PERIOD_QUESTION = "When did the measure apply?"
DECLARED_REASON_QUESTION = "What reason did the advisory state?"
PROVENANCE_QUESTION = "Which source supports this decision record?"


class QueryIntent(str, Enum):
    COMBINED_RECORD = "combined_record"
    MEASURE = "measure"
    CONTROLLED_FACILITY = "controlled_facility"
    OPERATIONAL_PERIOD = "operational_period"
    DECLARED_REASON = "declared_reason"
    PROVENANCE = "provenance"


MAX_MODEL_CALLS = 2
MAX_TOOL_CALLS = 3
MAX_CALLS_PER_TOOL = 1
MAX_ANSWER_WORDS = 200

ToolModelFactory = Callable[[list[BaseTool]], ToolCallingModel]


class QueryToolState(TypedDict, total=False):
    """Explicit state carried through the model-tool-model graph."""

    question: str
    messages: Annotated[list[BaseMessage], add_messages]
    model_calls: Annotated[list[ModelCallRecord], operator.add]
    tool_traces: Annotated[list[QueryToolTrace], operator.add]
    model_call_count: int
    tool_call_count: int
    per_tool_counts: dict[str, int]
    pending_tool_calls: list[dict[str, Any]]
    allowed_predicates: list[str]
    registered_event_ids: list[str]
    retrieved_fact_ids: list[str]
    retrieved_source_ids: list[str]
    cited_source_ids: list[str]
    observed_predicates: list[str]
    phase: str
    status: str
    answer: str
    failure_reason: str
    raw_answer: str


def _normalize_question(question: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", question.lower()))


def classify_registered_question(question: str) -> QueryIntent | None:
    """Map a bounded English question to one registered record intent."""

    if not question.isascii():
        return None
    normalized = _normalize_question(question)
    exact = {
        _normalize_question(REGISTERED_COMPETENCY_QUESTION): QueryIntent.COMBINED_RECORD,
        _normalize_question(MEASURE_QUESTION): QueryIntent.MEASURE,
        _normalize_question(CONTROLLED_FACILITY_QUESTION): QueryIntent.CONTROLLED_FACILITY,
        _normalize_question(OPERATIONAL_PERIOD_QUESTION): QueryIntent.OPERATIONAL_PERIOD,
        _normalize_question(DECLARED_REASON_QUESTION): QueryIntent.DECLARED_REASON,
        _normalize_question(PROVENANCE_QUESTION): QueryIntent.PROVENANCE,
    }
    if normalized in exact:
        return exact[normalized]
    words = set(normalized.split())
    matches: list[QueryIntent] = []
    if words.intersection({"measure", "tmi"}) and words.intersection(
        {"published", "recorded", "type"}
    ):
        matches.append(QueryIntent.MEASURE)
    if words.intersection({"airport", "facility"}) and words.intersection(
        {"controlled", "control"}
    ):
        matches.append(QueryIntent.CONTROLLED_FACILITY)
    if words.intersection({"when", "period", "start", "end"}) and words.intersection(
        {"apply", "applied", "effective", "period", "start", "end"}
    ):
        matches.append(QueryIntent.OPERATIONAL_PERIOD)
    if words.intersection({"reason", "condition"}) and words.intersection(
        {"advisory", "declared", "state", "stated", "impacting"}
    ):
        matches.append(QueryIntent.DECLARED_REASON)
    if words.intersection({"source", "evidence", "provenance"}) and words.intersection(
        {"support", "supports", "record", "statement", "evidence", "provenance"}
    ):
        matches.append(QueryIntent.PROVENANCE)
    return matches[0] if len(set(matches)) == 1 else None


def is_registered_competency_question(question: str) -> bool:
    """Return whether the bounded Query Agent explicitly supports the question."""

    return classify_registered_question(question) is not None


def question_requires_model(question: str) -> bool:
    """Return whether the registered question uses the model-tool-model path."""

    return classify_registered_question(question) is QueryIntent.COMBINED_RECORD


def _base_messages(
    *,
    question: str,
    event_ids: list[str],
    allowed_predicates: list[str],
    ontology_labels: dict[str, str],
    catalog_path: str,
) -> list[BaseMessage]:
    assembled = assemble_prompt(
        "query",
        {
            "user_question": question,
            "graph_scope": "\n".join(f"- {event_id}" for event_id in event_ids),
            "allowed_predicates": "\n".join(
                f"- {predicate}" for predicate in allowed_predicates
            ),
            "ontology_labels": "\n".join(
                f"{name}={label}" for name, label in sorted(ontology_labels.items())
            )
            or "(none)",
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


def _safe_arguments(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    sanitized = sanitize_json_value(value)
    return json.loads(json.dumps(sanitized, default=str))


def _message_text(message: AIMessage) -> str:
    if isinstance(message.content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in message.content
        )
    return str(message.content or "")


def _native_call_signature(call: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(call.get("id") or call.get("call_id") or ""),
        str(call.get("name") or ""),
        json.dumps(
            sanitize_json_value(call.get("args", call.get("arguments", {}))),
            sort_keys=True,
            separators=(",", ":"),
        ),
    )


def _model_call_signatures(message: AIMessage) -> list[tuple[str, str, str]]:
    return [_native_call_signature(dict(call)) for call in message.tool_calls]


def _record_call_signatures(record: ModelCallRecord) -> list[tuple[str, str, str]]:
    return [
        _native_call_signature(
            {
                "call_id": call.call_id,
                "name": call.name,
                "arguments": call.arguments,
            }
        )
        for call in record.tool_calls
    ]


def _parse_fixed_answer_fields(raw: str) -> dict[str, str]:
    """Parse the four low-complexity claim lines used by the fixed question."""

    expected = {"MEASURE", "AIRPORT", "START", "END"}
    fields: dict[str, str] = {}
    in_answer = False
    for line in raw.splitlines():
        stripped = line.strip()
        upper = stripped.upper()
        if upper == "ANSWER":
            in_answer = True
            continue
        if upper == "SOURCES" or upper.startswith("SOURCES:"):
            break
        if not in_answer or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip().upper()
        if key in expected and key not in fields:
            fields[key] = value.strip()
    return fields


def _expected_fixed_answer(
    *,
    rows: list[dict[str, Any]],
    ontology_labels: dict[str, str],
) -> tuple[dict[str, str], str]:
    by_predicate = {
        str(row["predicate"]): row
        for row in rows
    }
    type_value = str(by_predicate[QueryPredicate.EVENT_TYPE]["object"])
    measure_label = ontology_labels.get(type_value, type_value).strip()
    measure = measure_label.split("(", 1)[0].strip()
    facility_value = str(
        by_predicate[QueryPredicate.CONTROLLED_NAS_ELEMENT]["object"]
    )
    airport = facility_value.rsplit(":", 1)[-1].rsplit("/", 1)[-1]
    start = str(by_predicate[QueryPredicate.EFFECTIVE_START]["object"])
    end = str(by_predicate[QueryPredicate.EFFECTIVE_END]["object"])
    expected = {
        "MEASURE": measure_label,
        "AIRPORT": airport,
        "START": start,
        "END": end,
    }
    rendered = (
        f"The graph records a {measure} controlling {airport} "
        f"from {start} to {end}."
    )
    return expected, rendered


def build_query_tool_graph(
    *,
    model: ToolCallingModel,
    gateway: QueryToolGateway,
    tools: list[BaseTool],
    ontology_labels: dict[str, str],
) -> Any:
    """Compile one session-scoped model -> tool -> model graph."""

    registry = tool_registry(tools)

    def model_node(state: QueryToolState) -> dict[str, Any]:
        current_count = int(state.get("model_call_count", 0))
        if current_count >= MAX_MODEL_CALLS:
            return {
                "status": "blocked",
                "failure_reason": "Query Agent model-call budget exceeded",
                "pending_tool_calls": [],
            }
        phase = (
            "select_tool"
            if state.get("phase", "select_tool") == "select_tool"
            else "final_answer"
        )
        turn = model.invoke(list(state["messages"]), phase=phase)
        update: dict[str, Any] = {
            "model_calls": [turn.record],
            "model_call_count": current_count + 1,
            "pending_tool_calls": [],
        }
        if turn.record.error:
            update.update(
                status="blocked",
                failure_reason=turn.record.error,
            )
            return update
        if turn.message is None:
            update.update(
                status="blocked",
                failure_reason="provider returned no AI message",
            )
            return update
        if _model_call_signatures(turn.message) != _record_call_signatures(
            turn.record
        ):
            update.update(
                status="blocked",
                failure_reason=(
                    "native tool calls do not match the persisted model audit"
                ),
            )
            return update
        update["messages"] = [turn.message]
        if phase == "select_tool":
            if not turn.message.tool_calls:
                update.update(
                    status="blocked",
                    failure_reason=(
                        "Query Agent answered before retrieving graph evidence"
                    ),
                )
                return update
            update["pending_tool_calls"] = [
                dict(tool_call) for tool_call in turn.message.tool_calls
            ]
            return update
        if turn.message.tool_calls:
            update.update(
                status="blocked",
                failure_reason=(
                    "Query Agent requested another tool after the one-turn "
                    "tool budget"
                ),
            )
            return update
        raw_answer = _message_text(turn.message).strip()
        if not raw_answer:
            update.update(
                status="blocked",
                failure_reason="provider returned an empty final answer",
            )
            return update
        update["raw_answer"] = raw_answer
        return update

    def tool_node(state: QueryToolState) -> dict[str, Any]:
        pending = list(state.get("pending_tool_calls", []))
        current_total = int(state.get("tool_call_count", 0))
        per_tool = dict(state.get("per_tool_counts", {}))
        seen_call_ids: set[str] = set()
        tool_messages: list[ToolMessage] = []
        traces: list[QueryToolTrace] = []
        retrieved_fact_ids = set(state.get("retrieved_fact_ids", []))
        retrieved_source_ids = set(state.get("retrieved_source_ids", []))
        observed_predicates = set(state.get("observed_predicates", []))

        if current_total + len(pending) > MAX_TOOL_CALLS:
            return {
                "status": "blocked",
                "failure_reason": "Query Agent tool-call budget exceeded",
                "pending_tool_calls": [],
            }

        batch_tool_counts: dict[str, int] = {}
        for call in pending:
            call_id = str(call.get("id") or "").strip()
            name = str(call.get("name") or "").strip()
            arguments = call.get("args")
            if not call_id or call_id in seen_call_ids:
                return {
                    "status": "blocked",
                    "failure_reason": "missing or duplicate native tool-call ID",
                    "pending_tool_calls": [],
                }
            seen_call_ids.add(call_id)
            if name not in registry:
                return {
                    "status": "blocked",
                    "failure_reason": f"unknown Query Agent tool: {name}",
                    "pending_tool_calls": [],
                }
            if not isinstance(arguments, dict):
                return {
                    "status": "blocked",
                    "failure_reason": f"invalid arguments for Query Agent tool: {name}",
                    "pending_tool_calls": [],
                }
            batch_tool_counts[name] = batch_tool_counts.get(name, 0) + 1
            if (
                per_tool.get(name, 0) + batch_tool_counts[name]
                > MAX_CALLS_PER_TOOL
            ):
                return {
                    "status": "blocked",
                    "failure_reason": f"per-tool budget exceeded: {name}",
                    "pending_tool_calls": [],
                }

        if len(pending) != 1:
            return {
                "status": "blocked",
                "failure_reason": (
                    "registered competency requires exactly one tool call"
                ),
                "pending_tool_calls": [],
            }
        selected = pending[0]
        selected_args = selected["args"]
        selected_predicates = selected_args.get("predicates")
        if (
            selected["name"] != "get_event_facts"
            or selected_args.get("event_id")
            not in state["registered_event_ids"]
            or not isinstance(selected_predicates, list)
            or len(selected_predicates) != len(state["allowed_predicates"])
            or set(selected_predicates) != set(state["allowed_predicates"])
        ):
            return {
                "status": "blocked",
                "failure_reason": (
                    "tool selection is outside the registered competency contract"
                ),
                "pending_tool_calls": [],
            }

        for call in pending:
            call_id = str(call["id"])
            name = str(call["name"])
            arguments = call["args"]
            started = time.perf_counter()
            try:
                content = registry[name].invoke(arguments)
                result = QueryToolResult.model_validate_json(str(content))
                if result.tool != name:
                    raise QueryToolError(
                        f"tool result name mismatch: expected {name}, got {result.tool}"
                    )
            except Exception as exc:
                duration = (time.perf_counter() - started) * 1000.0
                trace = QueryToolTrace(
                    tool_call_id=call_id,
                    tool=name,
                    arguments=_safe_arguments(arguments),
                    status="blocked",
                    duration_ms=duration,
                    error=sanitize_text(f"{type(exc).__name__}: {exc}"),
                )
                return {
                    "status": "blocked",
                    "failure_reason": trace.error,
                    "pending_tool_calls": [],
                    "tool_traces": traces + [trace],
                    "tool_call_count": current_total + len(traces) + 1,
                }
            duration = (time.perf_counter() - started) * 1000.0
            tool_messages.append(
                ToolMessage(content=str(content), tool_call_id=call_id)
            )
            traces.append(
                QueryToolTrace(
                    tool_call_id=call_id,
                    tool=name,
                    arguments=_safe_arguments(arguments),
                    result_refs=result.fact_ids,
                    source_ids=result.source_ids,
                    status="ok",
                    duration_ms=duration,
                )
            )
            per_tool[name] = per_tool.get(name, 0) + 1
            retrieved_fact_ids.update(result.fact_ids)
            retrieved_source_ids.update(result.source_ids)
            for item in result.items:
                predicate = str(item.get("predicate") or "")
                if predicate:
                    observed_predicates.add(predicate)

        required = set(state["allowed_predicates"])
        if not retrieved_fact_ids:
            return {
                "messages": tool_messages,
                "tool_traces": traces,
                "tool_call_count": current_total + len(traces),
                "per_tool_counts": per_tool,
                "pending_tool_calls": [],
                "retrieved_fact_ids": [],
                "retrieved_source_ids": [],
                "observed_predicates": sorted(observed_predicates),
                "status": "insufficient",
                "failure_reason": "graph tools returned no matching facts",
            }
        missing = sorted(required - observed_predicates)
        if missing:
            return {
                "messages": tool_messages,
                "tool_traces": traces,
                "tool_call_count": current_total + len(traces),
                "per_tool_counts": per_tool,
                "pending_tool_calls": [],
                "retrieved_fact_ids": sorted(retrieved_fact_ids),
                "retrieved_source_ids": sorted(retrieved_source_ids),
                "observed_predicates": sorted(observed_predicates),
                "status": "insufficient",
                "failure_reason": (
                    "graph evidence does not cover required predicates: "
                    + ", ".join(missing)
                ),
            }
        required_rows = [
            gateway.store.fact_by_id[fact_id]
            for fact_id in retrieved_fact_ids
            if fact_id in gateway.store.fact_by_id
            and gateway.store.fact_by_id[fact_id]["predicate"] in required
        ]
        predicate_counts = {
            predicate: sum(
                1
                for row in required_rows
                if row["predicate"] == predicate
            )
            for predicate in required
        }
        ambiguous = sorted(
            predicate
            for predicate, count in predicate_counts.items()
            if count != 1
        )
        if ambiguous:
            return {
                "messages": tool_messages,
                "tool_traces": traces,
                "tool_call_count": current_total + len(traces),
                "per_tool_counts": per_tool,
                "pending_tool_calls": [],
                "retrieved_fact_ids": sorted(retrieved_fact_ids),
                "retrieved_source_ids": sorted(retrieved_source_ids),
                "observed_predicates": sorted(observed_predicates),
                "status": "insufficient",
                "failure_reason": (
                    "graph evidence is not singular for required predicates: "
                    + ", ".join(ambiguous)
                ),
            }
        if not retrieved_source_ids:
            return {
                "status": "blocked",
                "failure_reason": "retrieved graph facts have no provenance",
                "pending_tool_calls": [],
                "tool_traces": traces,
                "tool_call_count": current_total + len(traces),
            }
        return {
            "messages": tool_messages,
            "tool_traces": traces,
            "tool_call_count": current_total + len(traces),
            "per_tool_counts": per_tool,
            "pending_tool_calls": [],
            "retrieved_fact_ids": sorted(retrieved_fact_ids),
            "retrieved_source_ids": sorted(retrieved_source_ids),
            "observed_predicates": sorted(observed_predicates),
            "phase": "final_answer",
        }

    def finalize_node(state: QueryToolState) -> dict[str, Any]:
        raw = str(state.get("raw_answer") or "")
        answer, claimed_sources = parse_query_answer_claims(raw)
        retrieved_sources = set(state.get("retrieved_source_ids", []))
        unknown_sources = sorted(set(claimed_sources) - retrieved_sources)
        if not answer:
            return {
                "status": "blocked",
                "answer": "",
                "failure_reason": "Query Agent final response contained no answer",
            }
        if unknown_sources:
            return {
                "status": "blocked",
                "answer": "",
                "failure_reason": (
                    "Query Agent cited sources outside retrieved evidence: "
                    + ", ".join(unknown_sources)
                ),
            }
        sources = list(dict.fromkeys(claimed_sources))
        if not sources:
            return {
                "status": "blocked",
                "answer": "",
                "failure_reason": (
                    "Query Agent final response cited no retrieved source"
                ),
            }
        required_predicates = set(state["allowed_predicates"])
        required_rows = [
            gateway.store.fact_by_id[fact_id]
            for fact_id in state.get("retrieved_fact_ids", [])
            if fact_id in gateway.store.fact_by_id
            and gateway.store.fact_by_id[fact_id]["predicate"]
            in required_predicates
        ]
        uncovered_facts = [
            str(row["fact_id"])
            for row in required_rows
            if not set(row["source_ids"]).intersection(sources)
        ]
        if uncovered_facts:
            return {
                "status": "blocked",
                "answer": "",
                "failure_reason": (
                    "Query Agent citations do not cover retrieved facts: "
                    + ", ".join(uncovered_facts)
                ),
            }
        expected_fields, rendered_answer = _expected_fixed_answer(
            rows=required_rows,
            ontology_labels=ontology_labels,
        )
        returned_fields = _parse_fixed_answer_fields(raw)
        if {
            key: value.casefold() for key, value in returned_fields.items()
        } != {
            key: value.casefold() for key, value in expected_fields.items()
        }:
            return {
                "status": "blocked",
                "answer": "",
                "failure_reason": (
                    "Query Agent claim fields do not match required graph values"
                ),
            }
        if len(rendered_answer.split()) > MAX_ANSWER_WORDS:
            return {
                "status": "blocked",
                "answer": "",
                "failure_reason": "Query Agent final answer exceeded the word budget",
            }
        if re.search(r"[\u4e00-\u9fff]", answer):
            return {
                "status": "blocked",
                "answer": "",
                "failure_reason": "Query Agent final answer is not English-only",
            }
        return {
            "status": "ok",
            "answer": rendered_answer,
            "cited_source_ids": sources,
            "failure_reason": "",
        }

    def route_after_model(state: QueryToolState) -> str:
        if state.get("status") == "blocked":
            return "end"
        if state.get("pending_tool_calls"):
            return "tools"
        return "finalize"

    def route_after_tools(state: QueryToolState) -> str:
        if state.get("status") in {"blocked", "insufficient"}:
            return "end"
        return "model"

    graph = StateGraph(QueryToolState)
    graph.add_node("model", model_node)
    graph.add_node("tools", tool_node)
    graph.add_node("finalize", finalize_node)
    graph.add_edge(START, "model")
    graph.add_conditional_edges(
        "model",
        route_after_model,
        {"tools": "tools", "finalize": "finalize", "end": END},
    )
    graph.add_conditional_edges(
        "tools",
        route_after_tools,
        {"model": "model", "end": END},
    )
    graph.add_edge("finalize", END)
    return graph.compile()


def _write_query_tool_run(
    *,
    run_dir: Path,
    question: str,
    outcome: QueryToolOutcome,
    event_ids: list[str],
    allowed_predicates: list[str],
    ontology_labels: dict[str, str],
    retrieved_facts: list[dict[str, Any]],
    retrieved_profile_gaps: list[dict[str, Any]] | None = None,
) -> None:
    payload = {
        "execution": "native_tool_loop",
        "status": outcome.status,
        "question": question,
        "registered_event_ids": event_ids,
        "allowed_predicates": allowed_predicates,
        "ontology_labels": ontology_labels,
        "retrieved_fact_ids": outcome.retrieved_fact_ids,
        "retrieved_profile_gap_ids": outcome.retrieved_profile_gap_ids,
        "retrieved_facts": retrieved_facts,
        "retrieved_profile_gaps": retrieved_profile_gaps or [],
        "source_ids": outcome.source_ids,
        "answer": outcome.answer,
        "failure_reason": outcome.failure_reason,
        "budgets": {
            "maximum_model_calls": MAX_MODEL_CALLS,
            "maximum_tool_calls": MAX_TOOL_CALLS,
            "maximum_calls_per_tool": MAX_CALLS_PER_TOOL,
        },
        "model_calls": [
            record.model_dump(mode="json") for record in outcome.model_calls
        ],
        "tool_calls": [
            trace.model_dump(mode="json") for trace in outcome.tool_calls
        ],
    }
    (run_dir / "query_run.json").write_text(
        json.dumps(sanitize_json_value(payload), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _terminal_outcome(
    *,
    run_dir: Path,
    question: str,
    status: str,
    answer: str,
    reason: str,
) -> QueryToolOutcome:
    outcome = QueryToolOutcome(
        status=status,
        answer=answer,
        failure_reason=reason,
    )
    _write_query_tool_run(
        run_dir=run_dir,
        question=question,
        outcome=outcome,
        event_ids=[],
        allowed_predicates=[],
        ontology_labels={},
        retrieved_facts=[],
        retrieved_profile_gaps=[],
    )
    return outcome


def _deterministic_intent_outcome(
    *,
    run_dir: Path,
    question: str,
    intent: QueryIntent,
    store: QueryGraphStore,
    ontology_labels: dict[str, str],
) -> QueryToolOutcome:
    """Answer one bounded field question through validated read-only tools."""

    if len(store.event_ids) != 1:
        return _terminal_outcome(
            run_dir=run_dir,
            question=question,
            status="insufficient",
            answer="Insufficient graph evidence.",
            reason="bounded field questions require exactly one registered event",
        )
    event_id = store.event_ids[0]
    predicates_by_intent = {
        QueryIntent.MEASURE: [QueryPredicate.EVENT_TYPE],
        QueryIntent.CONTROLLED_FACILITY: [
            QueryPredicate.CONTROLLED_NAS_ELEMENT
        ],
        QueryIntent.OPERATIONAL_PERIOD: [
            QueryPredicate.EFFECTIVE_START,
            QueryPredicate.EFFECTIVE_END,
        ],
        QueryIntent.PROVENANCE: [QueryPredicate.ADVISORY_NUMBER],
        QueryIntent.DECLARED_REASON: [QueryPredicate.IMPACTING_CONDITION],
    }
    predicates = predicates_by_intent[intent]
    gateway = QueryToolGateway(
        store,
        allowed_predicates={predicate.value for predicate in predicates},
    )
    started = time.perf_counter()
    result = gateway.get_event_facts(
        event_id=event_id,
        predicates=predicates,
    )
    traces = [
        QueryToolTrace(
            tool_call_id=f"deterministic:{intent.value}:facts",
            tool="get_event_facts",
            arguments={
                "event_id": event_id,
                "predicates": [predicate.value for predicate in predicates],
            },
            result_refs=result.fact_ids,
            source_ids=result.source_ids,
            status="ok",
            duration_ms=(time.perf_counter() - started) * 1000.0,
        )
    ]
    profile_result: QueryToolResult | None = None
    if intent is QueryIntent.DECLARED_REASON and not result.items:
        started = time.perf_counter()
        profile_result = gateway.get_profile_gaps(
            event_id=event_id,
            fields=["impacting_condition"],
        )
        traces.append(
            QueryToolTrace(
                tool_call_id="deterministic:declared_reason:profile_gap",
                tool="get_profile_gaps",
                arguments={
                    "event_id": event_id,
                    "fields": ["impacting_condition"],
                },
                result_refs=profile_result.profile_gap_ids,
                source_ids=profile_result.source_ids,
                status="ok",
                duration_ms=(time.perf_counter() - started) * 1000.0,
            )
        )

    if intent is QueryIntent.DECLARED_REASON and profile_result is not None:
        if len(profile_result.items) != 1:
            return _write_deterministic_result(
                run_dir=run_dir,
                question=question,
                outcome=QueryToolOutcome(
                    status="insufficient",
                    answer="Insufficient graph evidence.",
                    tool_calls=traces,
                    failure_reason="the advisory has no singular declared reason",
                ),
                store=store,
                allowed_predicates=[predicate.value for predicate in predicates],
            )
        item = profile_result.items[0]
        answer = (
            f"The advisory states {item['evidence_text']}. "
            "This source-supported field is outside the active formal profile."
        )
        outcome = QueryToolOutcome(
            status="ok",
            answer=answer,
            source_ids=profile_result.source_ids,
            retrieved_profile_gap_ids=profile_result.profile_gap_ids,
            tool_calls=traces,
        )
        return _write_deterministic_result(
            run_dir=run_dir,
            question=question,
            outcome=outcome,
            store=store,
            allowed_predicates=[predicate.value for predicate in predicates],
        )

    expected_count = 2 if intent is QueryIntent.OPERATIONAL_PERIOD else 1
    if len(result.items) != expected_count:
        return _write_deterministic_result(
            run_dir=run_dir,
            question=question,
            outcome=QueryToolOutcome(
                status="insufficient",
                answer="Insufficient graph evidence.",
                retrieved_fact_ids=result.fact_ids,
                tool_calls=traces,
                failure_reason="graph evidence is missing or not singular",
            ),
            store=store,
            allowed_predicates=[predicate.value for predicate in predicates],
        )

    by_predicate = {str(item["predicate"]): item for item in result.items}
    if intent is QueryIntent.MEASURE:
        value = str(by_predicate[QueryPredicate.EVENT_TYPE]["object"])
        answer = (
            "The published traffic-management measure is "
            f"{ontology_labels.get(value, value)}."
        )
    elif intent is QueryIntent.CONTROLLED_FACILITY:
        value = str(
            by_predicate[QueryPredicate.CONTROLLED_NAS_ELEMENT]["object"]
        )
        answer = f"The controlled facility is {value.rsplit(':', 1)[-1]}."
    elif intent is QueryIntent.OPERATIONAL_PERIOD:
        start = by_predicate[QueryPredicate.EFFECTIVE_START]["object"]
        end = by_predicate[QueryPredicate.EFFECTIVE_END]["object"]
        answer = f"The TMI operational period is {start} to {end}."
    elif intent is QueryIntent.DECLARED_REASON:
        item = by_predicate[QueryPredicate.IMPACTING_CONDITION]
        if not str(item.get("evidence_text") or "").strip():
            return _write_deterministic_result(
                run_dir=run_dir,
                question=question,
                outcome=QueryToolOutcome(
                    status="insufficient",
                    answer="Insufficient graph evidence.",
                    retrieved_fact_ids=result.fact_ids,
                    tool_calls=traces,
                    failure_reason="declared reason has no exact source evidence",
                ),
                store=store,
                allowed_predicates=[
                    predicate.value for predicate in predicates
                ],
            )
        answer = (
            f"The advisory records {item['object']} as its impacting condition. "
            f"Source wording: {item['evidence_text']}."
        )
    else:
        item = by_predicate[QueryPredicate.ADVISORY_NUMBER]
        answer = (
            f"Source {result.source_ids[0]} supports advisory "
            f"{item['object']}."
        )
    outcome = QueryToolOutcome(
        status="ok",
        answer=answer,
        source_ids=result.source_ids,
        retrieved_fact_ids=result.fact_ids,
        tool_calls=traces,
    )
    return _write_deterministic_result(
        run_dir=run_dir,
        question=question,
        outcome=outcome,
        store=store,
        allowed_predicates=[predicate.value for predicate in predicates],
    )


def _write_deterministic_result(
    *,
    run_dir: Path,
    question: str,
    outcome: QueryToolOutcome,
    store: QueryGraphStore,
    allowed_predicates: list[str],
) -> QueryToolOutcome:
    retrieved_facts = [
        store.fact_by_id[fact_id]
        for fact_id in outcome.retrieved_fact_ids
        if fact_id in store.fact_by_id
    ]
    retrieved_gaps = [
        store.profile_gap_by_id[gap_id].model_dump(mode="json")
        for gap_id in outcome.retrieved_profile_gap_ids
        if gap_id in store.profile_gap_by_id
    ]
    _write_query_tool_run(
        run_dir=run_dir,
        question=question,
        outcome=outcome,
        event_ids=store.event_ids,
        allowed_predicates=allowed_predicates,
        ontology_labels={},
        retrieved_facts=retrieved_facts,
        retrieved_profile_gaps=retrieved_gaps,
    )
    return outcome


def answer_question_with_tools(
    *,
    run_dir: str | Path,
    question: str,
    model_factory: ToolModelFactory,
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
) -> QueryToolOutcome:
    """Run one registered decision-record question through read-only tools."""

    path = Path(run_dir)
    intent = classify_registered_question(question)
    if intent is None:
        return _terminal_outcome(
            run_dir=path,
            question=question,
            status="insufficient",
            answer="Insufficient graph evidence.",
            reason="question is outside the registered Query Agent capability",
        )

    try:
        store = QueryGraphStore(path)
    except QueryToolError as exc:
        return _terminal_outcome(
            run_dir=path,
            question=question,
            status="blocked",
            answer="",
            reason=str(exc),
        )

    if not store.event_ids:
        return _terminal_outcome(
            run_dir=path,
            question=question,
            status="insufficient",
            answer="Insufficient graph evidence.",
            reason="materialized graph contains no registered event",
        )
    guide = load_schema_guide()
    labels = ontology_labels_for(store.rows, guide)
    if intent is not QueryIntent.COMBINED_RECORD:
        return _deterministic_intent_outcome(
            run_dir=path,
            question=question,
            intent=intent,
            store=store,
            ontology_labels=labels,
        )

    allowed_predicates = [
        QueryPredicate.EVENT_TYPE.value,
        QueryPredicate.CONTROLLED_NAS_ELEMENT.value,
        QueryPredicate.EFFECTIVE_START.value,
        QueryPredicate.EFFECTIVE_END.value,
    ]
    gateway = QueryToolGateway(
        store,
        allowed_predicates=set(allowed_predicates),
    )
    tools = build_query_tools(gateway)
    try:
        model = model_factory(tools)
    except Exception as exc:
        return _terminal_outcome(
            run_dir=path,
            question=question,
            status="blocked",
            answer="",
            reason=sanitize_text(f"{type(exc).__name__}: {exc}"),
        )

    messages = _base_messages(
        question=question,
        event_ids=store.event_ids,
        allowed_predicates=allowed_predicates,
        ontology_labels=labels,
        catalog_path=catalog_path,
    )
    graph = build_query_tool_graph(
        model=model,
        gateway=gateway,
        tools=tools,
        ontology_labels=labels,
    )
    state = graph.invoke(
        {
            "question": question,
            "messages": messages,
            "model_calls": [],
            "tool_traces": [],
            "model_call_count": 0,
            "tool_call_count": 0,
            "per_tool_counts": {},
            "pending_tool_calls": [],
            "allowed_predicates": allowed_predicates,
            "registered_event_ids": store.event_ids,
            "retrieved_fact_ids": [],
            "retrieved_source_ids": [],
            "cited_source_ids": [],
            "observed_predicates": [],
            "phase": "select_tool",
            "status": "",
            "answer": "",
            "failure_reason": "",
            "raw_answer": "",
        }
    )
    status = str(state.get("status") or "blocked")
    answer = str(state.get("answer") or "")
    source_ids = list(state.get("cited_source_ids", [])) if status == "ok" else []
    outcome = QueryToolOutcome(
        status=status,
        answer=answer,
        source_ids=source_ids,
        retrieved_fact_ids=list(state.get("retrieved_fact_ids", [])),
        model_calls=list(state.get("model_calls", [])),
        tool_calls=list(state.get("tool_traces", [])),
        failure_reason=str(state.get("failure_reason") or ""),
    )
    retrieved_facts = [
        {
            "fact_id": store.fact_by_id[fact_id]["fact_id"],
            "subject": store.fact_by_id[fact_id]["subject"],
            "predicate": store.fact_by_id[fact_id]["predicate"],
            "object": store.fact_by_id[fact_id].get("object"),
            "source_ids": store.fact_by_id[fact_id]["source_ids"],
        }
        for fact_id in outcome.retrieved_fact_ids
        if fact_id in store.fact_by_id
    ]
    _write_query_tool_run(
        run_dir=path,
        question=question,
        outcome=outcome,
        event_ids=store.event_ids,
        allowed_predicates=allowed_predicates,
        ontology_labels=labels,
        retrieved_facts=retrieved_facts,
    )
    return outcome
