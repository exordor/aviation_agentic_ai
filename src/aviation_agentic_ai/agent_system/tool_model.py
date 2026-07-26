"""Native tool-calling model adapter for the Query Agent.

This is deliberately separate from the text-only ``ModelInvoker``.  It binds a
fixed read-only tool set once, preserves the provider's ``AIMessage`` (including
native tool calls), and emits the same auditable ``ModelCallRecord`` used by the
rest of the system.
"""

from __future__ import annotations

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

ToolPhase = Literal["select_tool", "final_answer"]


@dataclass(frozen=True)
class ToolModelTurn:
    """One provider turn: the native message plus its audit record."""

    message: AIMessage | None
    record: ModelCallRecord


class ToolCallingModel(Protocol):
    """Narrow model interface consumed by the Query Agent graph."""

    def invoke(
        self,
        messages: list[BaseMessage],
        *,
        phase: ToolPhase,
    ) -> ToolModelTurn:
        """Run one native tool-calling turn."""


def _content_text(message: AIMessage) -> str:
    content = message.content
    if isinstance(content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in content
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
        provider: str = FROZEN_PROVIDER,
        model: str = FROZEN_MODEL,
        temperature: float = FROZEN_TEMPERATURE,
    ) -> None:
        if not tools:
            raise ValueError("tool-calling model requires at least one bound tool")
        self.tools = tuple(tools)
        # The first turn must select a tool; the second must return a natural-
        # language answer. Local graph logic still validates both phases.
        self._tool_selector = chat_model.bind_tools(
            list(self.tools),
            tool_choice="required",
        )
        # The second turn has no available action: it composes the answer from
        # the matching ToolMessage. Keeping it unbound avoids sending unused
        # tool schemas again and works with providers that do not implement
        # ``tool_choice="none"`` consistently.
        self._answer_model = chat_model
        self.prompt_set_id = prompt_set_id
        self.prompt_version = prompt_version
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
        runnable = (
            self._tool_selector if phase == "select_tool" else self._answer_model
        )
        started = time.perf_counter()
        try:
            result = runnable.invoke(messages)
        except Exception as exc:
            latency = (time.perf_counter() - started) * 1000.0
            return ToolModelTurn(
                message=None,
                record=ModelCallRecord(
                    agent="query",
                    raw_response="",
                    prompt_set_id=self.prompt_set_id,
                    prompt_version=self.prompt_version,
                    provider=self.provider,
                    model=self.model,
                    temperature=self.temperature,
                    latency_ms=latency,
                    attempt=attempt,
                    error=sanitize_text(f"{type(exc).__name__}: {exc}"),
                ),
            )
        latency = (time.perf_counter() - started) * 1000.0
        if not isinstance(result, AIMessage):
            return ToolModelTurn(
                message=None,
                record=ModelCallRecord(
                    agent="query",
                    raw_response="",
                    prompt_set_id=self.prompt_set_id,
                    prompt_version=self.prompt_version,
                    provider=self.provider,
                    model=self.model,
                    temperature=self.temperature,
                    latency_ms=latency,
                    attempt=attempt,
                    error="provider returned a non-AI message",
                ),
            )
        input_tokens, output_tokens, _provider, model, fingerprint = (
            extract_model_metadata(result)
        )
        invalid_calls = [
            sanitize_json_value(dict(call)) for call in result.invalid_tool_calls
        ]
        error = "provider returned an invalid native tool call" if invalid_calls else None
        record = ModelCallRecord(
            agent="query",
            # A tool-selection turn is represented by its sanitized native tool
            # calls. Any accompanying prose may contain unrequested reasoning
            # and is intentionally not persisted.
            raw_response="" if result.tool_calls else _content_text(result),
            prompt_set_id=self.prompt_set_id,
            prompt_version=self.prompt_version,
            provider=self.provider,
            model=model or self.model,
            system_fingerprint=fingerprint,
            temperature=self.temperature,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency,
            attempt=attempt,
            error=error,
            tool_calls=_tool_call_records(result),
            invalid_tool_calls=invalid_calls,
        )
        return ToolModelTurn(message=result, record=record)


def make_live_tool_calling_model(
    *,
    tools: list[BaseTool],
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
) -> LangChainToolCallingModel:
    """Build the frozen DeepSeek native tool adapter for one Query run."""

    from aviation_agentic_ai.llm.providers import get_deepseek_mve_llm

    catalog = get_prompt_catalog(catalog_path)
    prompt = catalog.role("query")
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
    )


def serialize_tool_message_content(payload: dict[str, Any]) -> str:
    """Stable serialization for a ``ToolMessage`` observation."""

    return json.dumps(payload, sort_keys=True, separators=(",", ":"))
