"""Native LangChain tool-calling model adapter for bounded Agents.

This is deliberately separate from the text-only ``ModelInvoker``.  It binds a
fixed read-only tool set once, preserves the provider's ``AIMessage`` (including
native tool calls), and emits the same auditable ``ModelCallRecord`` used by the
rest of the system. Query and KG Construction reuse this adapter with different
frozen prompts and session-scoped tools.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar
import json
import time
from dataclasses import dataclass
from itertools import count
from typing import Any, Literal, Protocol

from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.tools import BaseTool

from aviation_agentic_ai.agent_system.audit import (
    sanitize_json_value,
    sanitize_text,
)
from aviation_agentic_ai.agent_system.contracts import (
    ModelCallRecord,
    ModelToolCall,
)
from aviation_agentic_ai.agent_system.prompts import (
    DEFAULT_PROMPT_CATALOG,
    get_prompt_catalog,
)
from aviation_agentic_ai.agent_system.runtime import (
    FROZEN_MAX_OUTPUT_TOKENS,
    FROZEN_MODEL,
    FROZEN_PROVIDER,
    FROZEN_TEMPERATURE,
    FROZEN_TIMEOUT,
    extract_model_metadata,
)

ToolPhase = Literal[
    "select_tool",
    "final_answer",
    "query_step",
    "emit_proposal",
    "extract_entities",
    "extract_relations",
    "revision",
]
NativeToolModelResponse = dict[str, Any] | None
ToolModelCallObserver = Callable[
    [ToolPhase, ModelCallRecord, NativeToolModelResponse],
    None,
]
_TOOL_MODEL_CALL_OBSERVER: ContextVar[ToolModelCallObserver | None] = (
    ContextVar("tool_model_call_observer", default=None)
)


@dataclass(frozen=True)
class ToolModelTurn:
    """One provider turn: the native message plus its audit record."""

    message: AIMessage | None
    record: ModelCallRecord


class ToolCallingModel(Protocol):
    """Narrow native-tool interface shared by bounded Agent loops."""

    def invoke(
        self,
        messages: list[BaseMessage],
        *,
        phase: ToolPhase,
    ) -> ToolModelTurn:
        """Run one native tool-calling turn."""


@contextmanager
def capture_tool_model_calls(
    observer: ToolModelCallObserver,
) -> Iterator[None]:
    """Observe real provider turns before workflow-level sanitization."""

    token = _TOOL_MODEL_CALL_OBSERVER.set(observer)
    try:
        yield
    finally:
        _TOOL_MODEL_CALL_OBSERVER.reset(token)


def _emit_tool_model_call_observation(
    phase: ToolPhase,
    record: ModelCallRecord,
    native_response: NativeToolModelResponse = None,
) -> None:
    observer = _TOOL_MODEL_CALL_OBSERVER.get()
    if observer is not None:
        observer(phase, record, native_response)


def _content_text(message: AIMessage) -> str:
    content = message.content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part) for part in content
        )
    return str(content or "")


def _tool_call_records(message: AIMessage) -> list[ModelToolCall]:
    records: list[ModelToolCall] = []
    for call in message.tool_calls:
        call_id = str(call.get("id") or "").strip()
        name = str(call.get("name") or "").strip()
        arguments = call.get("args")
        if not call_id or not name or not isinstance(arguments, dict):
            continue
        records.append(
            ModelToolCall(
                call_id=call_id,
                name=name,
                arguments=sanitize_json_value(arguments),
            )
        )
    return records


class LangChainToolCallingModel:
    """Bind one fixed tool set to a LangChain chat model."""

    def __init__(
        self,
        *,
        chat_model: Any,
        tools: list[BaseTool],
        prompt_set_id: str,
        prompt_version: str,
        agent: str = "query",
        provider: str = FROZEN_PROVIDER,
        model: str = FROZEN_MODEL,
        temperature: float = FROZEN_TEMPERATURE,
    ) -> None:
        if not tools:
            raise ValueError("tool-calling model requires at least one bound tool")
        self.tools = tuple(tools)
        # Construction roles keep their existing forced-selection/final-answer
        # phases. The public Query Agent uses the separate auto-tool loop below.
        self._tool_selector = chat_model.bind_tools(
            list(self.tools),
            tool_choice="required",
        )
        # Final-answer/proposal turns are genuinely unbound. Some compatible
        # providers serialize attempted tool calls as ordinary text even when
        # a bound schema uses tool_choice="none"; removing the schemas makes
        # answer formation a distinct, tool-free phase.
        self._answer_model = chat_model
        self._query_loop_model = chat_model.bind_tools(
            list(self.tools),
            tool_choice="auto",
        )
        self.prompt_set_id = prompt_set_id
        self.prompt_version = prompt_version
        self.agent = agent
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self._attempts = count(1)

    def invoke(
        self,
        messages: list[BaseMessage],
        *,
        phase: ToolPhase,
    ) -> ToolModelTurn:
        attempt = next(self._attempts)
        if phase == "select_tool":
            runnable = self._tool_selector
        elif phase == "query_step":
            runnable = self._query_loop_model
        else:
            runnable = self._answer_model
        started = time.perf_counter()
        try:
            result = runnable.invoke(messages)
        except Exception as exc:
            latency = (time.perf_counter() - started) * 1000.0
            record = ModelCallRecord(
                agent=self.agent,
                raw_response="",
                prompt_set_id=self.prompt_set_id,
                prompt_version=self.prompt_version,
                provider=self.provider,
                model=self.model,
                temperature=self.temperature,
                latency_ms=latency,
                attempt=attempt,
                error=sanitize_text(f"{type(exc).__name__}: {exc}"),
            )
            _emit_tool_model_call_observation(phase, record, None)
            return ToolModelTurn(
                message=None,
                record=record,
            )
        latency = (time.perf_counter() - started) * 1000.0
        if not isinstance(result, AIMessage):
            record = ModelCallRecord(
                agent=self.agent,
                raw_response="",
                prompt_set_id=self.prompt_set_id,
                prompt_version=self.prompt_version,
                provider=self.provider,
                model=self.model,
                temperature=self.temperature,
                latency_ms=latency,
                attempt=attempt,
                error="provider returned a non-AI message",
            )
            _emit_tool_model_call_observation(phase, record, None)
            return ToolModelTurn(
                message=None,
                record=record,
            )
        (
            input_tokens,
            output_tokens,
            _provider,
            model,
            fingerprint,
            finish_reason,
        ) = extract_model_metadata(result)
        invalid_calls = [sanitize_json_value(dict(call)) for call in result.invalid_tool_calls]
        error = "provider returned an invalid native tool call" if invalid_calls else None
        observed_record = ModelCallRecord(
            agent=self.agent,
            raw_response=_content_text(result),
            prompt_set_id=self.prompt_set_id,
            prompt_version=self.prompt_version,
            provider=self.provider,
            model=model or self.model,
            system_fingerprint=fingerprint,
            finish_reason=finish_reason,
            temperature=self.temperature,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency,
            attempt=attempt,
            error=error,
            tool_calls=_tool_call_records(result),
            invalid_tool_calls=invalid_calls,
        )
        _emit_tool_model_call_observation(
            phase,
            observed_record,
            result.model_dump(mode="json"),
        )
        # The normal workflow retains its prior sanitized contract. The live
        # experiment observer above owns the ignored raw-response artifact.
        record = observed_record.model_copy(
            update={
                "raw_response": (
                    "" if result.tool_calls else observed_record.raw_response
                )
            }
        )
        return ToolModelTurn(message=result, record=record)


def make_live_tool_calling_model(
    *,
    tools: list[BaseTool],
    role: str = "query",
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
) -> LangChainToolCallingModel:
    """Build the frozen DeepSeek native tool adapter for one bounded Agent run."""

    from aviation_agentic_ai.llm.providers import get_deepseek_mve_llm

    catalog = get_prompt_catalog(catalog_path)
    prompt = catalog.role(role)
    chat = get_deepseek_mve_llm(
        model=FROZEN_MODEL,
        temperature=FROZEN_TEMPERATURE,
        max_tokens=min(prompt.max_output_tokens, FROZEN_MAX_OUTPUT_TOKENS),
        timeout=FROZEN_TIMEOUT,
        max_retries=0,
    )
    return LangChainToolCallingModel(
        chat_model=chat,
        tools=tools,
        prompt_set_id=prompt.prompt_set_id,
        prompt_version=prompt.prompt_version,
        agent=role,
    )


def serialize_tool_message_content(payload: dict[str, Any]) -> str:
    """Stable serialization for a ``ToolMessage`` observation."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":"))
