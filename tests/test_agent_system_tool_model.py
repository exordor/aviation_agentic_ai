"""Contracts for the native LangChain tool-calling model adapter."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool

from aviation_agentic_ai.agent_system.tool_model import (
    LangChainToolCallingModel,
)


@tool
def fictional_lookup(candidate_id: str) -> str:
    """Look up one fictional candidate."""

    return candidate_id


class _FakeBoundModel:
    def __init__(self, owner: "_FakeChat", tool_choice: str) -> None:
        self.owner = owner
        self.tool_choice = tool_choice

    def invoke(self, messages):
        self.owner.invocations.append((self.tool_choice, list(messages)))
        response = self.owner.responses[self.tool_choice].pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class _FakeChat:
    def __init__(
        self,
        *,
        required: list[Any] | None = None,
        none: list[Any] | None = None,
    ) -> None:
        self.responses = {
            "required": list(required or []),
            "none": list(none or []),
        }
        self.bind_calls: list[dict[str, Any]] = []
        self.invocations: list[tuple[str, list[Any]]] = []

    def bind_tools(self, tools, **kwargs):
        self.bind_calls.append({"tools": list(tools), **kwargs})
        return _FakeBoundModel(self, kwargs["tool_choice"])

    def invoke(self, messages):
        self.invocations.append(("unbound", list(messages)))
        response = self.responses["none"].pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def _adapter(chat: _FakeChat) -> LangChainToolCallingModel:
    return LangChainToolCallingModel(
        chat_model=chat,
        tools=[fictional_lookup],
        prompt_set_id="prompt:test",
        prompt_version="query-tool-test-v1",
        provider="deepseek",
        model="deepseek-test",
        temperature=0,
    )


def _tool_call_message() -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[
            {
                "id": "call:1",
                "name": "fictional_lookup",
                "args": {"candidate_id": "candidate:alpha"},
                "type": "tool_call",
            }
        ],
        usage_metadata={
            "input_tokens": 12,
            "output_tokens": 4,
            "total_tokens": 16,
        },
        response_metadata={
            "model_name": "deepseek-test",
            "system_fingerprint": "fp-test",
            "finish_reason": "tool_calls",
        },
    )


def test_adapter_preserves_native_tool_call_and_metadata():
    message = _tool_call_message()
    adapter = _adapter(_FakeChat(required=[message]))
    turn = adapter.invoke(
        [HumanMessage(content="Use the registered lookup.")],
        phase="select_tool",
    )
    assert turn.message is message
    assert turn.record.provider == "deepseek"
    assert turn.record.model == "deepseek-test"
    assert turn.record.temperature == 0
    assert turn.record.input_tokens == 12
    assert turn.record.output_tokens == 4
    assert turn.record.system_fingerprint == "fp-test"
    assert turn.record.finish_reason == "tool_calls"
    assert turn.record.tool_calls[0].call_id == "call:1"
    assert turn.record.tool_calls[0].arguments == {
        "candidate_id": "candidate:alpha"
    }


def test_adapter_records_the_configured_active_agent_role():
    message = _tool_call_message()
    adapter = LangChainToolCallingModel(
        chat_model=_FakeChat(required=[message]),
        tools=[fictional_lookup],
        prompt_set_id="prompt:test",
        prompt_version="event-evidence-integration-v1",
        agent="event_evidence_integration",
        provider="deepseek",
        model="deepseek-test",
        temperature=0,
    )
    turn = adapter.invoke(
        [HumanMessage(content="Inspect the registered context.")],
        phase="select_tool",
    )
    assert turn.record.agent == "event_evidence_integration"


def test_adapter_binds_tools_for_construction_and_query_without_strict_schema():
    chat = _FakeChat(required=[_tool_call_message()])
    _adapter(chat)
    assert [call["tool_choice"] for call in chat.bind_calls] == [
        "required",
        "none",
        "auto",
    ]
    for call in chat.bind_calls:
        assert [bound.name for bound in call["tools"]] == ["fictional_lookup"]
        assert "response_format" not in call
        assert "strict" not in call


def test_final_turn_receives_original_ai_message_and_matching_tool_message():
    first = _tool_call_message()
    final = AIMessage(content="ANSWER\nA result.\nSOURCES\n- example:001")
    chat = _FakeChat(required=[first], none=[final])
    adapter = _adapter(chat)
    initial = [HumanMessage(content="Use the registered lookup.")]
    first_turn = adapter.invoke(initial, phase="select_tool")
    observation = ToolMessage(
        content='{"source_ids":["example:001"]}',
        tool_call_id="call:1",
    )
    second_turn = adapter.invoke(
        initial + [first_turn.message, observation],
        phase="final_answer",
    )
    assert second_turn.message is final
    phase, captured = chat.invocations[-1]
    assert phase == "none"
    assert captured[-2] is first
    assert captured[-1] is observation
    assert captured[-1].tool_call_id == first.tool_calls[0]["id"]


def test_provider_exception_is_a_recorded_attempt():
    adapter = _adapter(_FakeChat(required=[TimeoutError("upstream timeout")]))
    turn = adapter.invoke(
        [HumanMessage(content="Use a tool.")],
        phase="select_tool",
    )
    assert turn.message is None
    assert turn.record.attempt == 1
    assert turn.record.provider == "deepseek"
    assert turn.record.model == "deepseek-test"
    assert turn.record.error == "TimeoutError: upstream timeout"
    assert turn.record.latency_ms >= 0


def test_provider_exception_redacts_credentials():
    adapter = _adapter(
        _FakeChat(
            required=[
                RuntimeError("Authorization: Bearer sk-provider-secret123")
            ]
        )
    )
    turn = adapter.invoke(
        [HumanMessage(content="Use a tool.")],
        phase="select_tool",
    )
    assert "sk-provider-secret123" not in str(turn.record.error)
    assert "[REDACTED]" in str(turn.record.error)


def test_invalid_native_tool_call_is_explicitly_recorded():
    invalid = AIMessage(
        content="",
        invalid_tool_calls=[
            {
                "id": "call:bad",
                "name": "fictional_lookup",
                "args": "{not-json",
                "error": "invalid JSON",
                "type": "invalid_tool_call",
            }
        ],
    )
    adapter = _adapter(_FakeChat(required=[invalid]))
    turn = adapter.invoke(
        [HumanMessage(content="Use a tool.")],
        phase="select_tool",
    )
    assert turn.message is invalid
    assert turn.record.error == "provider returned an invalid native tool call"
    assert turn.record.invalid_tool_calls[0]["id"] == "call:bad"


def test_attempt_counter_includes_failed_and_successful_turns():
    final = AIMessage(content="ANSWER\nDone.\nSOURCES\n- example:001")
    adapter = _adapter(
        _FakeChat(
            required=[RuntimeError("first failed")],
            none=[final],
        )
    )
    failed = adapter.invoke(
        [HumanMessage(content="Use a tool.")],
        phase="select_tool",
    )
    succeeded = adapter.invoke(
        [HumanMessage(content="Answer.")],
        phase="final_answer",
    )
    assert failed.record.attempt == 1
    assert succeeded.record.attempt == 2
