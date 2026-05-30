from __future__ import annotations

import os
from typing import TYPE_CHECKING

from aviation_agentic_ai.config import load_environment

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel


def get_llm(temperature: float = 0.3, max_tokens: int = 4096) -> "BaseChatModel":
    """Return a LangChain-compatible chat model from environment configuration."""
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "Ontology generation requires optional LLM dependencies. "
            "Install with: uv sync --extra ontology-generation"
        ) from exc

    load_environment()
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openai":
        return ChatOpenAI(
            model=os.getenv("MODEL_NAME", "gpt-4o-mini"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=temperature,
            max_tokens=max_tokens,
        )

    if provider == "deepseek":
        return ChatOpenAI(
            model=os.getenv("MODEL_NAME", "deepseek-chat"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            temperature=temperature,
            max_tokens=max_tokens,
        )

    if provider == "vllm":
        return ChatOpenAI(
            model=os.getenv("MODEL_NAME", "Qwen/Qwen3-30B-A3B-Instruct-2507-FP8"),
            base_url=f"http://localhost:{os.getenv('VLLM_PORT', '8000')}/v1",
            api_key="not-needed",
            temperature=temperature,
            max_tokens=max_tokens,
        )

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")
