"""Bounded model-tool-observation loop for live HybridRAG queries."""

from __future__ import annotations

import json
import re
import time
from collections.abc import Callable
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from pydantic import ValidationError

from aviation_agentic_ai.agent_system.audit import sanitize_json_value, sanitize_text
from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryAnswer,
    HybridQueryEvidence,
    HybridQueryScope,
    HybridQueryStatement,
    HybridQuerySupportRecord,
    HybridQueryToolObservation,
    ModelCallRecord,
    QueryToolOutcome,
    QueryToolTrace,
)
from aviation_agentic_ai.agent_system.prompts import (
    DEFAULT_PROMPT_CATALOG,
    get_prompt_catalog,
)
from aviation_agentic_ai.agent_system.tool_model import ToolCallingModel


MAX_QUERY_PROVIDER_TURNS = 4
MAX_QUERY_TOOL_CALLS_PER_TURN = 3
MAX_QUERY_TOOL_CALLS = 6

ModelFactory = Callable[[list[BaseTool]], ToolCallingModel]


def _message_text(message: AIMessage) -> str:
    content = message.content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
        )
    return str(content or "")


def _blocked(
    *,
    reason: str,
    model_calls: list[ModelCallRecord],
    tool_calls: list[QueryToolTrace],
) -> QueryToolOutcome:
    return QueryToolOutcome(
        status="blocked",
        failure_reason=sanitize_text(reason),
        model_calls=model_calls,
        tool_calls=tool_calls,
    )


def _base_messages(
    *,
    question: str,
    scope: HybridQueryScope,
    catalog_path: str,
) -> list[Any]:
    role = get_prompt_catalog(catalog_path).role("query")
    return [
        SystemMessage(content=role.system),
        HumanMessage(
            content=role.user_template.replace("${user_question}", question).replace(
                "${query_scope}",
                json.dumps(
                    scope.model_dump(mode="json"),
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            )
        ),
    ]


def _observation_from_result(result: Any) -> HybridQueryToolObservation:
    if isinstance(result, HybridQueryToolObservation):
        return result
    if isinstance(result, str):
        return HybridQueryToolObservation.model_validate_json(result)
    return HybridQueryToolObservation.model_validate(result)


def _model_observation(observation: HybridQueryToolObservation) -> str:
    payload = {
        "status": observation.status,
        "content": observation.content,
        "support_records": [
            record.model_dump(mode="json")
            for record in observation.support_records
        ],
        "graph_paths": [
            path.model_dump(mode="json")
            for path in observation.graph_paths
        ],
        "similarity_matches": [
            match.model_dump(mode="json")
            for match in observation.similarity_matches
        ],
        "limitation": observation.limitation,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _result_refs(evidence: HybridQueryEvidence) -> list[str]:
    return sorted(
        {
            *evidence.event_ids,
            *evidence.fact_ids,
            *evidence.profile_gap_ids,
            *evidence.context_association_ids,
            *evidence.observation_ids,
            *evidence.graph_path_ids,
            *evidence.source_version_ids,
            *evidence.source_anchor_ids,
            *evidence.chunk_ids,
        }
    )


def _merge_evidence(
    observations: list[HybridQueryToolObservation],
) -> HybridQueryEvidence:
    return HybridQueryEvidence(
        event_ids=tuple(
            sorted({value for row in observations for value in row.details.event_ids})
        ),
        fact_ids=tuple(
            sorted({value for row in observations for value in row.details.fact_ids})
        ),
        profile_gap_ids=tuple(
            sorted(
                {
                    value
                    for row in observations
                    for value in row.details.profile_gap_ids
                }
            )
        ),
        context_association_ids=tuple(
            sorted(
                {
                    value
                    for row in observations
                    for value in row.details.context_association_ids
                }
            )
        ),
        observation_ids=tuple(
            sorted(
                {
                    value
                    for row in observations
                    for value in row.details.observation_ids
                }
            )
        ),
        graph_path_ids=tuple(
            sorted(
                {
                    value
                    for row in observations
                    for value in row.details.graph_path_ids
                }
            )
        ),
        source_ids=tuple(
            sorted({value for row in observations for value in row.details.source_ids})
        ),
        source_version_ids=tuple(
            sorted(
                {
                    value
                    for row in observations
                    for value in row.details.source_version_ids
                }
            )
        ),
        source_anchor_ids=tuple(
            sorted(
                {
                    value
                    for row in observations
                    for value in row.details.source_anchor_ids
                }
            )
        ),
        chunk_ids=tuple(
            sorted({value for row in observations for value in row.details.chunk_ids})
        ),
    )


def _unsupported_ids(
    statement: HybridQueryStatement,
    evidence: HybridQueryEvidence,
) -> set[str]:
    checks = (
        (statement.support_event_ids, evidence.event_ids),
        (statement.support_fact_ids, evidence.fact_ids),
        (statement.support_profile_gap_ids, evidence.profile_gap_ids),
        (
            statement.support_context_association_ids,
            evidence.context_association_ids,
        ),
        (statement.support_observation_ids, evidence.observation_ids),
        (statement.support_graph_path_ids, evidence.graph_path_ids),
        (statement.support_source_ids, evidence.source_ids),
        (
            statement.support_source_version_ids,
            evidence.source_version_ids,
        ),
        (statement.support_source_anchor_ids, evidence.source_anchor_ids),
        (statement.support_chunk_ids, evidence.chunk_ids),
    )
    return {
        value
        for supplied, available in checks
        for value in supplied
        if value not in set(available)
    }


_SUPPORT_ID_FIELDS = (
    ("support_event_ids", "event_ids"),
    ("support_fact_ids", "fact_ids"),
    ("support_profile_gap_ids", "profile_gap_ids"),
    ("support_context_association_ids", "context_association_ids"),
    ("support_observation_ids", "observation_ids"),
    ("support_graph_path_ids", "graph_path_ids"),
    ("support_source_version_ids", "source_version_ids"),
    ("support_source_anchor_ids", "source_anchor_ids"),
    ("support_chunk_ids", "chunk_ids"),
)


def _matching_support_records(
    statement: HybridQueryStatement,
    support_records: list[HybridQuerySupportRecord],
) -> list[HybridQuerySupportRecord]:
    return [
        record
        for record in support_records
        if record.kind == statement.kind
    ]


def _support_binding_error(
    statement: HybridQueryStatement,
    support_records: list[HybridQuerySupportRecord],
) -> str | None:
    """Require every cited item to remain paired with its tool-provided source."""

    records = _matching_support_records(statement, support_records)
    if not records:
        return "statement has no evidence binding for its declared kind"
    if statement.kind == "source_record":
        cited_sources = set(statement.support_source_ids)
        cited_versions = set(statement.support_source_version_ids)
        cited_anchors = set(statement.support_source_anchor_ids)
        cited_chunks = set(statement.support_chunk_ids)
        exact_record = any(
            cited_sources.issubset(record.source_ids)
            and cited_versions.issubset(record.source_version_ids)
            and cited_anchors.issubset(record.source_anchor_ids)
            and cited_chunks.issubset(record.chunk_ids)
            for record in records
        )
        if not exact_record:
            return "source record IDs do not share one exact evidence binding"
    cited_sources = set(statement.support_source_ids)
    cited_non_event_ids = {
        value
        for statement_field, _record_field in _SUPPORT_ID_FIELDS
        if statement_field != "support_event_ids"
        for value in getattr(statement, statement_field)
    }
    cited_event_ids = set(statement.support_event_ids)
    for statement_field, record_field in _SUPPORT_ID_FIELDS:
        for value in getattr(statement, statement_field):
            matching = [
                record
                for record in records
                if value in getattr(record, record_field)
            ]
            if statement_field == "support_event_ids" and not cited_non_event_ids:
                matching = [
                    record
                    for record in matching
                    if not any(
                        getattr(record, other_record_field)
                        for other_statement_field, other_record_field
                        in _SUPPORT_ID_FIELDS
                        if other_statement_field != "support_event_ids"
                    )
                ]
            if not matching:
                return "statement cites an ID outside its evidence binding"
            if cited_sources and not any(
                cited_sources.intersection(record.source_ids)
                for record in matching
            ):
                return "statement mixes an evidence ID with an unrelated source"
    for source_id in statement.support_source_ids:
        matching = [
            record for record in records if source_id in record.source_ids
        ]
        if not matching:
            return "statement cites a source outside its evidence binding"
        if cited_non_event_ids and not any(
            cited_non_event_ids.intersection(
                {
                    value
                    for statement_field, record_field in _SUPPORT_ID_FIELDS
                    if statement_field != "support_event_ids"
                    for value in getattr(record, record_field)
                }
            )
            for record in matching
        ):
            return "statement cites a source unrelated to its evidence IDs"
        if not cited_non_event_ids and cited_event_ids and not any(
            cited_event_ids.intersection(record.event_ids)
            and not any(
                getattr(record, record_field)
                for statement_field, record_field in _SUPPORT_ID_FIELDS
                if statement_field != "support_event_ids"
            )
            for record in matching
        ):
            return "statement cites a source unrelated to its event metadata"
    return None


def _parse_answer(message: AIMessage) -> HybridQueryAnswer:
    text = _message_text(message).strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        fenced = re.findall(
            r"```(?:json)?\s*(\{.*?\})\s*```",
            text,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if len(fenced) != 1:
            raise ValueError("final answer is not valid JSON")
        try:
            payload = json.loads(fenced[0])
        except json.JSONDecodeError as exc:
            raise ValueError("final answer is not valid JSON") from exc
    try:
        return HybridQueryAnswer.model_validate(payload)
    except ValidationError as exc:
        raise ValueError("final answer violates the Hybrid Query JSON contract") from exc


def _claim_boundary_error(statement: HybridQueryStatement) -> str | None:
    normalized = " ".join(statement.text.lower().split())
    causal_phrases = (
        " cause ",
        " caused ",
        " causes ",
        " because ",
        " resulted in ",
        " leading to ",
        " led to ",
        " trigger ",
        " triggered ",
        " triggers ",
        " drove ",
        " driven by ",
        " prompted ",
        "\u5bfc\u81f4",
        "\u56e0\u4e3a",
        "\u5f15\u53d1",
        "\u9020\u6210",
        "\u4fc3\u4f7f",
    )
    recommendation_phrases = (
        " should ",
        " recommend",
        " best decision",
        " optimal",
        "\u5efa\u8bae",
        "\u5e94\u8be5",
        "\u6700\u4f18",
    )
    padded = f" {normalized} "
    if any(phrase in padded for phrase in causal_phrases):
        return "causal statement crosses the claim boundary"
    if statement.kind == "public_observation" and any(
        phrase in padded
        for phrase in (
            " faa demand",
            " arrival capacity",
            " airport capacity",
            " aar ",
            " edct ",
            "\u51b3\u7b56\u539f\u56e0",
        )
    ):
        return "public observation statement crosses the claim boundary"
    if statement.kind == "similarity" and any(
        phrase in padded for phrase in recommendation_phrases
    ):
        return "similarity statement crosses the claim boundary"
    return None


def _statement_support_error(statement: HybridQueryStatement) -> str | None:
    if not statement.support_source_ids:
        return "statement has no supporting source ID"
    if statement.kind == "non_causal_context" and not (
        statement.support_context_association_ids
    ):
        return "non-causal context statement has no context association"
    if (
        statement.kind == "public_observation"
        and not statement.support_observation_ids
    ):
        return "public observation statement has no observation"
    if statement.kind == "similarity" and not statement.support_event_ids:
        return "similarity statement has no event support"
    if statement.kind == "source_fact" and not (
        statement.support_fact_ids
        or statement.support_profile_gap_ids
        or statement.support_event_ids
    ):
        return "source fact statement has no formal or source-bound support"
    if statement.kind == "source_record" and not (
        statement.support_source_version_ids
        and statement.support_source_anchor_ids
    ):
        return "source record statement has no exact source version and anchor"
    return None


def validate_hybrid_query_statement(
    statement: HybridQueryStatement,
    support_records: list[HybridQuerySupportRecord],
) -> str | None:
    """Validate one answer statement against typed, source-bound tool evidence."""

    boundary_error = _claim_boundary_error(statement)
    if boundary_error:
        return boundary_error
    support_error = _statement_support_error(statement)
    if support_error:
        return support_error
    binding_error = _support_binding_error(statement, support_records)
    if binding_error:
        return f"evidence binding failed: {binding_error}"
    return None


def _answer_text(answer: HybridQueryAnswer) -> str:
    parts = [statement.text for statement in answer.statements]
    parts.extend(answer.limitations)
    return "\n".join(part for part in parts if part).strip()


def run_hybrid_query_agent(
    *,
    question: str,
    scope: HybridQueryScope,
    tools: list[BaseTool],
    model_factory: ModelFactory,
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
) -> QueryToolOutcome:
    """Run one required retrieval turn and one evidence-bound answer turn."""

    model_calls: list[ModelCallRecord] = []
    traces: list[QueryToolTrace] = []
    observations: list[HybridQueryToolObservation] = []
    if not question.strip():
        return _blocked(
            reason="query question must be nonempty",
            model_calls=model_calls,
            tool_calls=traces,
        )
    if not tools:
        return _blocked(
            reason="Hybrid Query Agent has no read-only tools",
            model_calls=model_calls,
            tool_calls=traces,
        )
    registry = {tool.name: tool for tool in tools}
    messages = _base_messages(
        question=question,
        scope=scope,
        catalog_path=catalog_path,
    )
    try:
        model = model_factory(tools)
    except Exception as exc:
        return _blocked(
            reason=f"Hybrid Query Agent model construction failed: {type(exc).__name__}: {exc}",
            model_calls=model_calls,
            tool_calls=traces,
        )

    active_messages = list(messages)
    seen_call_ids: set[str] = set()
    answer: HybridQueryAnswer | None = None
    for turn_number in range(1, MAX_QUERY_PROVIDER_TURNS + 1):
        try:
            turn = model.invoke(active_messages, phase="query_step")
        except Exception as exc:
            model_calls.append(
                ModelCallRecord(
                    agent="query",
                    raw_response="",
                    attempt=turn_number,
                    error=sanitize_text(f"{type(exc).__name__}: {exc}"),
                )
            )
            return _blocked(
                reason=(
                    f"Hybrid Query Agent provider failed: "
                    f"{type(exc).__name__}: {exc}"
                ),
                model_calls=model_calls,
                tool_calls=traces,
            )
        model_calls.append(turn.record)
        if turn.record.error:
            return _blocked(
                reason=turn.record.error,
                model_calls=model_calls,
                tool_calls=traces,
            )
        if turn.message is None:
            return _blocked(
                reason="provider returned no query-step message",
                model_calls=model_calls,
                tool_calls=traces,
            )
        calls = [dict(call) for call in turn.message.tool_calls]
        if not calls:
            if not observations:
                return _blocked(
                    reason="Hybrid Query Agent did not select a retrieval tool",
                    model_calls=model_calls,
                    tool_calls=traces,
                )
            try:
                answer = _parse_answer(turn.message)
            except ValueError as exc:
                return _blocked(
                    reason=str(exc),
                    model_calls=model_calls,
                    tool_calls=traces,
                )
            break
        if len(calls) > MAX_QUERY_TOOL_CALLS_PER_TURN:
            return _blocked(
                reason="Hybrid Query Agent per-turn tool-call budget exceeded",
                model_calls=model_calls,
                tool_calls=traces,
            )
        if len(traces) + len(calls) > MAX_QUERY_TOOL_CALLS:
            return _blocked(
                reason="Hybrid Query Agent total tool-call budget exceeded",
                model_calls=model_calls,
                tool_calls=traces,
            )

        tool_messages: list[ToolMessage] = []
        for call in calls:
            call_id = str(call.get("id") or "").strip()
            name = str(call.get("name") or "").strip()
            arguments = call.get("args")
            if not call_id or call_id in seen_call_ids:
                return _blocked(
                    reason="missing or duplicate native tool-call ID",
                    model_calls=model_calls,
                    tool_calls=traces,
                )
            if name not in registry:
                return _blocked(
                    reason=f"unknown Hybrid Query Agent tool: {name}",
                    model_calls=model_calls,
                    tool_calls=traces,
                )
            if not isinstance(arguments, dict):
                return _blocked(
                    reason=f"invalid arguments for query tool: {name}",
                    model_calls=model_calls,
                    tool_calls=traces,
                )
            seen_call_ids.add(call_id)
            started = time.perf_counter()
            try:
                result = registry[name].invoke(arguments)
                observation = _observation_from_result(result)
            except Exception as exc:
                duration_ms = (time.perf_counter() - started) * 1000.0
                trace = QueryToolTrace(
                    tool_call_id=call_id,
                    tool=name,
                    arguments=sanitize_json_value(arguments),
                    status="blocked",
                    duration_ms=duration_ms,
                    error=sanitize_text(f"{type(exc).__name__}: {exc}"),
                )
                traces.append(trace)
                return _blocked(
                    reason=f"invalid arguments or blocked query tool: {name}",
                    model_calls=model_calls,
                    tool_calls=traces,
                )
            duration_ms = (time.perf_counter() - started) * 1000.0
            traces.append(
                QueryToolTrace(
                    tool_call_id=call_id,
                    tool=name,
                    arguments=sanitize_json_value(arguments),
                    result_refs=_result_refs(observation.details),
                    context_association_ids=list(
                        observation.details.context_association_ids
                    ),
                    observation_ids=list(observation.details.observation_ids),
                    source_ids=list(observation.details.source_ids),
                    source_version_ids=list(
                        observation.details.source_version_ids
                    ),
                    source_anchor_ids=list(
                        observation.details.source_anchor_ids
                    ),
                    chunk_ids=list(observation.details.chunk_ids),
                    status=observation.status,
                    duration_ms=duration_ms,
                    error=(
                        observation.limitation
                        if observation.status == "blocked"
                        else None
                    ),
                )
            )
            observations.append(observation)
            if observation.status == "blocked":
                return _blocked(
                    reason=observation.limitation or f"query tool blocked: {name}",
                    model_calls=model_calls,
                    tool_calls=traces,
                )
            tool_messages.append(
                ToolMessage(
                    content=_model_observation(observation),
                    tool_call_id=call_id,
                )
            )
        active_messages.extend([turn.message, *tool_messages])

    if answer is None:
        return _blocked(
            reason="Hybrid Query Agent provider-turn budget exceeded",
            model_calls=model_calls,
            tool_calls=traces,
        )

    evidence = _merge_evidence(observations)
    support_records = [
        record
        for observation in observations
        for record in observation.support_records
    ]
    if answer.status == "ok" and not any(
        observation.status == "ok" for observation in observations
    ):
        return _blocked(
            reason="ok answer cannot be supported by insufficient tool evidence",
            model_calls=model_calls,
            tool_calls=traces,
        )
    for statement in answer.statements:
        unsupported = _unsupported_ids(statement, evidence)
        if unsupported:
            return _blocked(
                reason="final answer cites unsupported evidence IDs",
                model_calls=model_calls,
                tool_calls=traces,
            )
        validation_error = validate_hybrid_query_statement(
            statement,
            support_records,
        )
        if validation_error:
            return _blocked(
                reason=f"final answer statement rejected: {validation_error}",
                model_calls=model_calls,
                tool_calls=traces,
            )
    if answer.status == "ok" and not answer.statements:
        return _blocked(
            reason="ok answer has no evidence-bound statements",
            model_calls=model_calls,
            tool_calls=traces,
        )
    if answer.status == "insufficient" and not answer.limitations:
        return _blocked(
            reason="insufficient answer has no limitation",
            model_calls=model_calls,
            tool_calls=traces,
        )

    graph_paths = sorted(
        {
            path.path_id: path
            for observation in observations
            for path in observation.graph_paths
        }.values(),
        key=lambda path: path.path_id,
    )
    similarity_matches = sorted(
        {
            match.event_id: match
            for observation in observations
            for match in observation.similarity_matches
        }.values(),
        key=lambda match: match.rank,
    )
    return QueryToolOutcome(
        status=answer.status,
        answer=_answer_text(answer),
        match_count=len(evidence.event_ids),
        retrieved_event_ids=list(evidence.event_ids),
        source_ids=list(evidence.source_ids),
        retrieved_fact_ids=list(evidence.fact_ids),
        retrieved_profile_gap_ids=list(evidence.profile_gap_ids),
        retrieved_context_association_ids=list(
            evidence.context_association_ids
        ),
        retrieved_observation_ids=list(evidence.observation_ids),
        retrieved_graph_path_ids=list(evidence.graph_path_ids),
        retrieved_source_version_ids=list(evidence.source_version_ids),
        retrieved_source_anchor_ids=list(evidence.source_anchor_ids),
        retrieved_chunk_ids=list(evidence.chunk_ids),
        retrieved_graph_paths=graph_paths,
        similarity_matches=similarity_matches,
        answer_statements=list(answer.statements),
        support_records=support_records,
        model_calls=model_calls,
        tool_calls=traces,
    )


__all__ = [
    "MAX_QUERY_PROVIDER_TURNS",
    "MAX_QUERY_TOOL_CALLS",
    "MAX_QUERY_TOOL_CALLS_PER_TURN",
    "run_hybrid_query_agent",
    "validate_hybrid_query_statement",
]
