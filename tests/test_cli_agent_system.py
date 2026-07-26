"""CLI contracts for the active native tool-using Query Agent."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from langchain_core.messages import AIMessage

import aviation_agentic_ai.cli_agent_system as cli_module
from aviation_agentic_ai.agent_system.contracts import (
    ModelCallRecord,
    ModelToolCall,
)
from aviation_agentic_ai.agent_system.query_tool_graph import (
    REGISTERED_COMPETENCY_QUESTION,
)
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn

EVENT_ID = "urn:aviation-agentic-ai:event:cli-test"
SOURCE_ID = "2026-05-19:123"


def _write_graph(run_dir: Path) -> None:
    values = [
        ("fact:type", "rdf:type", "atm:GroundStopTMI", "atm:GroundStopTMI"),
        (
            "fact:facility",
            "atm:controlledNASelement",
            "urn:aviation-agentic-ai:facility:airport:KJFK",
            "nas:Airport",
        ),
        (
            "fact:start",
            "atm:effectiveStartTime",
            "2026-05-19T21:00:00Z",
            "",
        ),
        (
            "fact:end",
            "atm:effectiveEndTime",
            "2026-05-19T22:45:00Z",
            "",
        ),
    ]
    rows = [
        {
            "triple_id": fact_id,
            "subject": EVENT_ID,
            "predicate": predicate,
            "object": value,
            "subject_class": "atm:GroundStopTMI",
            "object_class": object_class,
            "source_document": SOURCE_ID,
        }
        for fact_id, predicate, value, object_class in values
    ]
    (run_dir / "kg.jsonl").write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


class _SuccessfulModel:
    def __init__(self) -> None:
        self.attempt = 0

    def invoke(self, messages, *, phase):
        self.attempt += 1
        if phase == "select_tool":
            message = AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": "call:cli",
                        "name": "get_event_facts",
                        "args": {
                            "event_id": EVENT_ID,
                            "predicates": [
                                "rdf:type",
                                "atm:controlledNASelement",
                                "atm:effectiveStartTime",
                                "atm:effectiveEndTime",
                            ],
                        },
                        "type": "tool_call",
                    }
                ],
            )
        else:
            message = AIMessage(
                content=(
                    "ANSWER\n"
                    "MEASURE: Ground Stop\n"
                    "AIRPORT: KJFK\n"
                    "START: 2026-05-19T21:00:00Z\n"
                    "END: 2026-05-19T22:45:00Z\n"
                    f"SOURCES\n- {SOURCE_ID}"
                )
            )
        return ToolModelTurn(
            message=message,
            record=ModelCallRecord(
                agent="query",
                raw_response=str(message.content or "") if not message.tool_calls else "",
                attempt=self.attempt,
                tool_calls=[
                    ModelToolCall(
                        call_id=str(call["id"]),
                        name=str(call["name"]),
                        arguments=dict(call["args"]),
                    )
                    for call in message.tool_calls
                ],
            ),
        )


def test_unsupported_cli_question_needs_no_live_authorization(tmp_path, monkeypatch):
    _write_graph(tmp_path)

    def forbidden_factory(*args, **kwargs):
        raise AssertionError("unsupported question constructed a live model")

    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        forbidden_factory,
    )
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--run-dir",
            str(tmp_path),
            "--question",
            "What is the runway surface at LAX?",
        ],
    )
    assert result.exit_code == 0
    assert "status: insufficient" in result.output
    assert "model_calls: 0" in result.output
    assert "tool_calls: 0" in result.output


def test_supported_cli_question_requires_live_authorization(tmp_path):
    _write_graph(tmp_path)
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--run-dir",
            str(tmp_path),
            "--question",
            REGISTERED_COMPETENCY_QUESTION,
        ],
    )
    assert result.exit_code != 0
    assert "requires --allow-live-model" in result.output


def test_supported_cli_question_runs_native_tool_loop(tmp_path, monkeypatch):
    _write_graph(tmp_path)
    model = _SuccessfulModel()
    monkeypatch.setattr(
        cli_module,
        "make_live_tool_calling_model",
        lambda *, tools: model,
    )
    result = CliRunner().invoke(
        cli_module.agent_system,
        [
            "ask",
            "--run-dir",
            str(tmp_path),
            "--question",
            REGISTERED_COMPETENCY_QUESTION,
            "--allow-live-model",
        ],
    )
    assert result.exit_code == 0
    assert "status: ok" in result.output
    assert f"sources: {SOURCE_ID}" in result.output
    assert "graph_facts_seen: 4" in result.output
    assert "model_calls: 2" in result.output
    assert "tool_calls: 1" in result.output
