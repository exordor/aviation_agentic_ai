from __future__ import annotations

import os
from typing import TYPE_CHECKING

from aviation_agentic_ai.config import load_environment

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel


DEFAULT_LLM_MODELS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "deepseek": "deepseek-chat",
    "vllm": "Qwen/Qwen3-30B-A3B-Instruct-2507-FP8",
}
SUPPORTED_LLM_PROVIDERS = frozenset(DEFAULT_LLM_MODELS)


def configured_llm_provider() -> str:
    return os.getenv("LLM_PROVIDER", "openai").lower()


def default_model_for_provider(provider: str) -> str:
    return DEFAULT_LLM_MODELS.get(provider, "unknown")


def configured_llm_model(provider: str | None = None) -> str:
    effective_provider = provider or configured_llm_provider()
    return os.getenv("MODEL_NAME", default_model_for_provider(effective_provider))


def _required_env(name: str, provider: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(
        f"LLM_PROVIDER={provider} requires {name}. Configure the environment before "
        "requesting an LLM, or select a provider that does not require that key."
    )


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
    provider = configured_llm_provider()
    model = configured_llm_model(provider)

    if provider == "openai":
        return ChatOpenAI(
            model=model,
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=_required_env("OPENAI_API_KEY", provider),
            temperature=temperature,
            max_tokens=max_tokens,
        )

    if provider == "deepseek":
        return ChatOpenAI(
            model=model,
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            api_key=_required_env("DEEPSEEK_API_KEY", provider),
            temperature=temperature,
            max_tokens=max_tokens,
        )

    if provider == "vllm":
        return ChatOpenAI(
            model=model,
            base_url=f"http://localhost:{os.getenv('VLLM_PORT', '8000')}/v1",
            api_key=os.getenv("VLLM_API_KEY", "not-needed"),
            temperature=temperature,
            max_tokens=max_tokens,
        )

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")
