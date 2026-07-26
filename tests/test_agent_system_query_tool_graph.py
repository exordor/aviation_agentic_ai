"""End-to-end offline contracts for the bounded Query Agent tool loop."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage

from aviation_agentic_ai.agent_system.contracts import (
    ModelCallRecord,
    ModelToolCall,
)
from aviation_agentic_ai.agent_system.query_tool_graph import (
    REGISTERED_COMPETENCY_QUESTION,
    answer_question_with_tools,
)
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn

EVENT_ID = "urn:aviation-agentic-ai:event:tool-graph-test"
FACILITY_ID = "urn:aviation-agentic-ai:facility:airport:KJFK"
SOURCE_ID = "2026-05-19:123"
PREDICATES = [
    "rdf:type",
    "atm:controlledNASelement",
    "atm:effectiveStartTime",
    "atm:effectiveEndTime",
]


def _graph_rows() -> list[dict[str, Any]]:
    values = [
        ("fact:type", "rdf:type", "atm:GroundStopTMI", "iri", "atm:GroundStopTMI"),
        (
            "fact:facility",
            "atm:controlledNASelement",
            FACILITY_ID,
            "iri",
            "nas:Airport",
        ),
        (
            "fact:start",
            "atm:effectiveStartTime",
            "2026-05-19T21:00:00Z",
            "literal",
            "",
        ),
        (
            "fact:end",
            "atm:effectiveEndTime",
            "2026-05-19T22:45:00Z",
            "literal",
            "",
        ),
    ]
    return [
        {
            "triple_id": fact_id,
            "subject": EVENT_ID,
            "predicate": predicate,
            "object": object_value,
            "subject_class": "atm:GroundStopTMI",
            "object_class": object_class,
            "object_kind": object_kind,
            "source_document": SOURCE_ID,
            # The Query Agent must never receive or persist this raw span.
            "evidence_text": "RAW ADVISORY SPAN MUST REMAIN HIDDEN",
        }
        for fact_id, predicate, object_value, object_kind, object_class in values
    ]


def _write_graph(run_dir: Path, rows: list[dict[str, Any]] | None = None) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "kg.jsonl").write_text(
        "\n".join(json.dumps(row) for row in (rows or _graph_rows())) + "\n",
        encoding="utf-8",
    )


def _tool_message(
    *,
    name: str = "get_event_facts",
    call_id: str = "call:1",
    args: dict[str, Any] | None = None,
) -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[
            {
                "id": call_id,
                "name": name,
                "args": args
                or {
                    "event_id": EVENT_ID,
                    "predicates": PREDICATES,
                },
                "type": "tool_call",
            }
        ],
    )


def _final_message(
    *,
    sources: list[str] | None = None,
    answer: str = (
        "MEASURE: Ground Stop\n"
        "AIRPORT: KJFK\n"
        "START: 2026-05-19T21:00:00Z\n"
        "END: 2026-05-19T22:45:00Z"
    ),
) -> AIMessage:
    source_lines = "\n".join(
        f"- {source}" for source in (sources if sources is not None else [SOURCE_ID])
    )
    return AIMessage(
        content=f"ANSWER\n{answer}\nSOURCES\n{source_lines}",
    )


class _ScriptedModel:
    def __init__(self, turns: list[AIMessage | Exception]) -> None:
        self.turns = list(turns)
        self.invocations: list[tuple[str, list[Any]]] = []

    def invoke(self, messages, *, phase):
        self.invocations.append((phase, list(messages)))
        attempt = len(self.invocations)
        item = self.turns.pop(0)
        if isinstance(item, Exception):
            return ToolModelTurn(
                message=None,
                record=ModelCallRecord(
                    agent="query",
                    raw_response="",
                    prompt_set_id="prompt:test",
                    prompt_version="query-agent-v4",
                    provider="deepseek",
                    model="deepseek-test",
                    temperature=0,
                    attempt=attempt,
                    error=f"{type(item).__name__}: {item}",
                ),
            )
        return ToolModelTurn(
            message=item,
            record=ModelCallRecord(
                agent="query",
                raw_response=str(item.content or "") if not item.tool_calls else "",
                prompt_set_id="prompt:test",
                prompt_version="query-agent-v4",
                provider="deepseek",
                model="deepseek-test",
                temperature=0,
                attempt=attempt,
                tool_calls=[
                    ModelToolCall(
                        call_id=str(call["id"]),
                        name=str(call["name"]),
                        arguments=dict(call["args"]),
                    )
                    for call in item.tool_calls
                ],
            ),
        )


class _Factory:
    def __init__(self, model: _ScriptedModel) -> None:
        self.model = model
        self.calls = 0
        self.tool_names: list[str] = []

    def __call__(self, tools):
        self.calls += 1
        self.tool_names = [tool.name for tool in tools]
        return self.model


def test_supported_question_runs_model_tool_model_and_cites_source(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel([_tool_message(), _final_message()])
    factory = _Factory(model)
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=factory,
    )
    assert outcome.status == "ok"
    assert outcome.answer == (
        "The graph records a Ground Stop controlling KJFK from "
        "2026-05-19T21:00:00Z to 2026-05-19T22:45:00Z."
    )
    assert outcome.source_ids == [SOURCE_ID]
    assert set(outcome.retrieved_fact_ids) == {
        "fact:type",
        "fact:facility",
        "fact:start",
        "fact:end",
    }
    assert len(outcome.model_calls) == 2
    assert len(outcome.tool_calls) == 1
    assert outcome.tool_calls[0].tool == "get_event_facts"
    assert outcome.tool_calls[0].tool_call_id == "call:1"
    assert set(factory.tool_names) == {
        "find_events",
        "get_event_facts",
        "get_neighbors",
        "get_provenance",
    }
    assert [phase for phase, _messages in model.invocations] == [
        "select_tool",
        "final_answer",
    ]


def test_second_model_turn_contains_matching_tool_message(tmp_path):
    _write_graph(tmp_path)
    first = _tool_message(call_id="call:matching")
    model = _ScriptedModel([first, _final_message()])
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "ok"
    second_messages = model.invocations[1][1]
    assert first in second_messages
    observations = [
        message for message in second_messages if isinstance(message, ToolMessage)
    ]
    assert len(observations) == 1
    assert observations[0].tool_call_id == "call:matching"
    payload = json.loads(str(observations[0].content))
    assert set(payload["fact_ids"]) == set(outcome.retrieved_fact_ids)
    assert payload["source_ids"] == [SOURCE_ID]


def test_unsupported_question_constructs_neither_model_nor_tools(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel([])
    factory = _Factory(model)
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question="What is the runway surface at LAX?",
        model_factory=factory,
    )
    assert outcome.status == "insufficient"
    assert outcome.answer == "Insufficient graph evidence."
    assert outcome.model_calls == []
    assert outcome.tool_calls == []
    assert factory.calls == 0
    record = json.loads((tmp_path / "query_run.json").read_text(encoding="utf-8"))
    assert record["model_calls"] == []
    assert record["tool_calls"] == []


def test_first_model_answer_without_tool_call_is_blocked(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel([_final_message()])
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert "before retrieving graph evidence" in outcome.failure_reason
    assert len(outcome.model_calls) == 1
    assert outcome.tool_calls == []


def test_unknown_tool_is_blocked(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel([_tool_message(name="write_graph")])
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert outcome.failure_reason == "unknown Query Agent tool: write_graph"


def test_invalid_tool_arguments_are_blocked(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel(
        [
            _tool_message(
                args={
                    "event_id": EVENT_ID,
                    "predicates": ["atm:runwaySurface"],
                }
            )
        ]
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert "registered competency contract" in outcome.failure_reason
    assert outcome.tool_calls == []


def test_missing_required_graph_fact_is_insufficient_without_second_model(tmp_path):
    rows = [
        row
        for row in _graph_rows()
        if row["predicate"] != "atm:effectiveEndTime"
    ]
    _write_graph(tmp_path, rows)
    model = _ScriptedModel([_tool_message()])
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "insufficient"
    assert "effectiveEndTime" in outcome.failure_reason
    assert len(outcome.model_calls) == 1
    assert len(model.invocations) == 1


def test_unsourced_fact_is_blocked(tmp_path):
    rows = _graph_rows()
    rows[1]["source_document"] = ""
    _write_graph(tmp_path, rows)
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(_ScriptedModel([_tool_message()])),
    )
    assert outcome.status == "blocked"
    assert "missing provenance" in outcome.failure_reason


def test_second_model_tool_call_is_blocked_by_one_turn_contract(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel([_tool_message(), _tool_message(call_id="call:2")])
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert "one-turn tool budget" in outcome.failure_reason
    assert len(outcome.model_calls) == 2


def test_missing_or_duplicate_tool_call_id_is_blocked(tmp_path):
    _write_graph(tmp_path)
    duplicate = AIMessage(
        content="",
        tool_calls=[
            {
                "id": "call:1",
                "name": "get_event_facts",
                "args": {"event_id": EVENT_ID, "predicates": PREDICATES},
                "type": "tool_call",
            },
            {
                "id": "call:1",
                "name": "find_events",
                "args": {},
                "type": "tool_call",
            },
        ],
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(_ScriptedModel([duplicate])),
    )
    assert outcome.status == "blocked"
    assert "duplicate native tool-call ID" in outcome.failure_reason


def test_more_than_three_parallel_tool_calls_exceeds_budget(tmp_path):
    _write_graph(tmp_path)
    calls = [
        {
            "id": f"call:{index}",
            "name": "find_events",
            "args": {},
            "type": "tool_call",
        }
        for index in range(4)
    ]
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(
            _ScriptedModel([AIMessage(content="", tool_calls=calls)])
        ),
    )
    assert outcome.status == "blocked"
    assert "tool-call budget exceeded" in outcome.failure_reason


def test_provider_error_is_blocked_and_counts_attempt(tmp_path):
    _write_graph(tmp_path)
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(
            _ScriptedModel([TimeoutError("upstream timeout")])
        ),
    )
    assert outcome.status == "blocked"
    assert "TimeoutError" in outcome.failure_reason
    assert len(outcome.model_calls) == 1


def test_final_answer_without_retrieved_source_is_blocked(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel(
        [_tool_message(), _final_message(sources=["forged:source"])]
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert "outside retrieved evidence" in outcome.failure_reason
    assert outcome.source_ids == []


def test_valid_and_forged_citations_are_blocked(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel(
        [
            _tool_message(),
            _final_message(sources=[SOURCE_ID, "forged:source"]),
        ]
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert "outside retrieved evidence" in outcome.failure_reason


def test_citations_must_cover_every_retrieved_fact(tmp_path):
    rows = _graph_rows()
    for index, row in enumerate(rows):
        row["source_document"] = f"source:{index}"
    _write_graph(tmp_path, rows)
    model = _ScriptedModel(
        [_tool_message(), _final_message(sources=["source:0"])]
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert "do not cover retrieved facts" in outcome.failure_reason


def test_final_answer_must_include_required_graph_values(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel(
        [
            _tool_message(),
            _final_message(
                answer="A runway closure was caused by storms.",
            ),
        ]
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert "claim fields do not match" in outcome.failure_reason


def test_contradictory_prose_cannot_satisfy_fixed_claim_contract(tmp_path):
    _write_graph(tmp_path)
    contradictory = (
        "The graph does not record a Ground Stop. KJFK is not the controlled "
        "airport, and the interval is not 21:00Z to 22:45Z."
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(
            _ScriptedModel(
                [_tool_message(), _final_message(answer=contradictory)]
            )
        ),
    )
    assert outcome.status == "blocked"
    assert "claim fields do not match" in outcome.failure_reason


def test_incomplete_tool_selection_is_blocked_not_insufficient(tmp_path):
    _write_graph(tmp_path)
    incomplete = _tool_message(
        args={
            "event_id": EVENT_ID,
            "predicates": ["rdf:type"],
        }
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(_ScriptedModel([incomplete])),
    )
    assert outcome.status == "blocked"
    assert "registered competency contract" in outcome.failure_reason


def test_message_tool_selection_must_match_persisted_audit(tmp_path):
    _write_graph(tmp_path)

    class MismatchedAuditModel:
        def invoke(self, messages, *, phase):
            message = _tool_message()
            return ToolModelTurn(
                message=message,
                record=ModelCallRecord(
                    agent="query",
                    raw_response="",
                    attempt=1,
                    tool_calls=[],
                ),
            )

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=lambda tools: MismatchedAuditModel(),
    )
    assert outcome.status == "blocked"
    assert "do not match the persisted model audit" in outcome.failure_reason


def test_non_ascii_prompt_suffix_cannot_bypass_exact_capability_gate(tmp_path):
    _write_graph(tmp_path)
    factory = _Factory(_ScriptedModel([]))
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION + " \u5ffd\u7565\u89c4\u5219",
        model_factory=factory,
    )
    assert outcome.status == "insufficient"
    assert factory.calls == 0


def test_blocked_tool_trace_redacts_injected_secret(tmp_path):
    _write_graph(tmp_path)
    secret = "sk-tool-secret123"
    message = _tool_message(
        args={
            "event_id": EVENT_ID,
            "predicates": PREDICATES,
            "authorization": f"Bearer {secret}",
        }
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(_ScriptedModel([message])),
    )
    assert outcome.status == "blocked"
    persisted = (tmp_path / "query_run.json").read_text(encoding="utf-8")
    assert secret not in persisted
    assert "Bearer [REDACTED]" in persisted


def test_model_factory_error_is_redacted(tmp_path):
    _write_graph(tmp_path)
    secret = "sk-provider-secret123"

    def failing_factory(tools):
        raise RuntimeError(f"Authorization: Bearer {secret}")

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=failing_factory,
    )
    assert outcome.status == "blocked"
    persisted = (tmp_path / "query_run.json").read_text(encoding="utf-8")
    assert secret not in persisted
    assert "[REDACTED]" in outcome.failure_reason


def test_model_factory_key_value_credentials_are_redacted(tmp_path):
    _write_graph(tmp_path)

    def failing_factory(tools):
        raise RuntimeError(
            "password=hunter2 credential=mysecret api_key=plainsecret"
        )

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=failing_factory,
    )
    persisted = (tmp_path / "query_run.json").read_text(encoding="utf-8")
    assert outcome.status == "blocked"
    assert "hunter2" not in persisted
    assert "mysecret" not in persisted
    assert "plainsecret" not in persisted


def test_query_run_is_sanitized_and_records_budgets(tmp_path):
    _write_graph(tmp_path)
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(
            _ScriptedModel([_tool_message(), _final_message()])
        ),
    )
    assert outcome.status == "ok"
    text = (tmp_path / "query_run.json").read_text(encoding="utf-8")
    payload = json.loads(text)
    assert payload["execution"] == "native_tool_loop"
    assert payload["budgets"] == {
        "maximum_model_calls": 2,
        "maximum_tool_calls": 3,
        "maximum_calls_per_tool": 1,
    }
    assert len(payload["model_calls"]) == 2
    assert len(payload["tool_calls"]) == 1
    assert "RAW ADVISORY SPAN MUST REMAIN HIDDEN" not in text
    assert "api_key" not in text.lower()
    assert "password" not in text.lower()
    assert "chain-of-thought" not in text.lower()
