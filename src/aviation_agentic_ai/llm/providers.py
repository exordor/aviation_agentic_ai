from __future__ import annotations

import os
from typing import TYPE_CHECKING

from aviation_agentic_ai.config import load_environment

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel


DEFAULT_LLM_MODELS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "deepseek": "deepseek-chat",
    "newapi": "glm-5.2",
    "sub2api": "gpt-5.5",
    "vllm": "Qwen/Qwen3-30B-A3B-Instruct-2507-FP8",
}
SUPPORTED_LLM_PROVIDERS = frozenset(DEFAULT_LLM_MODELS)
PROVIDER_API_KEY_ENV: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "newapi": "NEWAPI_API_KEY",
    "sub2api": "SUB2API_API_KEY",
}


def normalize_openai_compatible_base_url(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if normalized.endswith("/v1"):
        return normalized
    return f"{normalized}/v1"


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


def required_api_key_env_for_provider(provider: str) -> str | None:
    return PROVIDER_API_KEY_ENV.get(provider)


def has_required_llm_credentials(provider: str) -> bool:
    api_key_env = required_api_key_env_for_provider(provider)
    return api_key_env is None or bool(os.getenv(api_key_env))


def get_llm(
    temperature: float = 0.3,
    max_tokens: int = 4096,
    timeout: float | None = 120.0,
    reasoning_effort: str | None = None,
) -> "BaseChatModel":
    """Return a LangChain-compatible chat model from environment configuration."""
    if not (0.0 <= temperature <= 2.0):
        raise ValueError(f"temperature must be in [0.0, 2.0], got {temperature}")
    if max_tokens < 1:
        raise ValueError(f"max_tokens must be >= 1, got {max_tokens}")

    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The active Agent-system runtime requires optional LLM dependencies. "
            "Install with: uv sync --extra agent-system"
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
            timeout=timeout,
        )

    if provider == "deepseek":
        return ChatOpenAI(
            model=model,
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            api_key=_required_env("DEEPSEEK_API_KEY", provider),
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    if provider == "newapi":
        return ChatOpenAI(
            model=model,
            base_url=normalize_openai_compatible_base_url(
                os.getenv("NEWAPI_BASE_URL", "http://localhost:3000")
            ),
            api_key=_required_env("NEWAPI_API_KEY", provider),
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    if provider == "sub2api":
        # gpt-5.x are reasoning models; reasoning_effort controls latency vs.
        # deliberation. Default to "medium" (low only saved ~14% latency in
        # tests, not worth the quality drop). Override via
        # SUB2API_REASONING_EFFORT (low|medium|high) for specific workloads.
        effective_reasoning_effort = reasoning_effort or os.getenv(
            "SUB2API_REASONING_EFFORT", "medium"
        )
        return ChatOpenAI(
            model=model,
            base_url=normalize_openai_compatible_base_url(
                os.getenv("SUB2API_BASE_URL", "http://127.0.0.1:8080")
            ),
            api_key=_required_env("SUB2API_API_KEY", provider),
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            reasoning_effort=effective_reasoning_effort,
        )

    if provider == "vllm":
        vllm_port_str = os.getenv("VLLM_PORT", "8000")
        try:
            vllm_port = int(vllm_port_str)
        except ValueError as exc:
            raise ValueError(f"VLLM_PORT must be an integer, got {vllm_port_str!r}") from exc
        if not (1 <= vllm_port <= 65535):
            raise ValueError(f"VLLM_PORT must be in [1, 65535], got {vllm_port}")
        return ChatOpenAI(
            model=model,
            base_url=f"http://localhost:{vllm_port}/v1",
            api_key=os.getenv("VLLM_API_KEY", "not-needed"),
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )

    raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")


def get_deepseek_mve_llm(
    *,
    model: str,
    temperature: float = 0.0,
    max_tokens: int = 10_000,
    timeout: float | None = 120.0,
    max_retries: int = 0,
) -> "BaseChatModel":
    """Bind the EXACT frozen DeepSeek model for the agent-system mainline.

    Pins the model id explicitly and refuses to run without a real DeepSeek
    API key/base URL (no silent provider substitution via the ambient
    LLM_PROVIDER env var). Disables DeepSeek v4 thinking via the non-thinking
    request parameter and sets ``max_retries=0`` so every provider attempt is
    visible to the run trace.
    """

    if not (0.0 <= temperature <= 2.0):
        raise ValueError(f"temperature must be in [0.0, 2.0], got {temperature}")
    if max_tokens < 1:
        raise ValueError(f"max_tokens must be >= 1, got {max_tokens}")

    try:
        from langchain_openai import ChatOpenAI
    except ImportError as exc:
        raise RuntimeError(
            "Agent-system live run requires optional LLM dependencies. "
            "Install with: uv sync --extra agent-system"
        ) from exc

    load_environment()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError(
            "DeepSeek live run requires DEEPSEEK_API_KEY. Set it in the "
            "environment before requesting a live model; the system never "
            "silently substitutes another provider."
        )
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    return ChatOpenAI(
        model=model,
        base_url=base_url,
        api_key=api_key,
        cache=False,
        temperature=temperature,
        timeout=timeout,
        max_retries=max_retries,
        extra_body={
            "thinking": {"type": "disabled"},
            # DeepSeek's OpenAI-compatible endpoint accepts ``max_tokens``.
            # Passing it as ChatOpenAI's top-level argument is rewritten by
            # langchain-openai 1.2.x to ``max_completion_tokens``, which this
            # endpoint does not enforce.
            "max_tokens": max_tokens,
        },
    )
