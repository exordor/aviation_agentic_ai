from types import ModuleType

import pytest

from aviation_agentic_ai.llm import providers


class FakeChatOpenAI:
    calls: list[dict[str, object]] = []

    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs
        self.calls.append(kwargs)


def _install_fake_langchain_openai(monkeypatch) -> None:
    FakeChatOpenAI.calls = []
    module = ModuleType("langchain_openai")
    module.ChatOpenAI = FakeChatOpenAI
    monkeypatch.setitem(__import__("sys").modules, "langchain_openai", module)


def test_get_llm_uses_environment_loader_and_openai_defaults(monkeypatch) -> None:
    _install_fake_langchain_openai(monkeypatch)
    load_calls: list[str] = []
    monkeypatch.setattr(providers, "load_environment", lambda: load_calls.append("loaded"))
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    llm = providers.get_llm(temperature=0.1, max_tokens=123)

    assert isinstance(llm, FakeChatOpenAI)
    assert load_calls == ["loaded"]
    assert llm.kwargs == {
        "model": "gpt-4o-mini",
        "base_url": "https://api.openai.com/v1",
        "api_key": "sk-test",
        "temperature": 0.1,
        "max_tokens": 123,
    }


def test_get_llm_routes_deepseek_to_openai_compatible_endpoint(monkeypatch) -> None:
    _install_fake_langchain_openai(monkeypatch)
    monkeypatch.setattr(providers, "load_environment", lambda: None)
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("MODEL_NAME", "deepseek-reasoner")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://deepseek.example/v1")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key")

    llm = providers.get_llm(temperature=0.0, max_tokens=456)

    assert llm.kwargs == {
        "model": "deepseek-reasoner",
        "base_url": "https://deepseek.example/v1",
        "api_key": "deepseek-key",
        "temperature": 0.0,
        "max_tokens": 456,
    }


def test_get_llm_rejects_openai_without_api_key(monkeypatch) -> None:
    _install_fake_langchain_openai(monkeypatch)
    monkeypatch.setattr(providers, "load_environment", lambda: None)
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        providers.get_llm()

    assert FakeChatOpenAI.calls == []


def test_get_llm_rejects_deepseek_without_api_key(monkeypatch) -> None:
    _install_fake_langchain_openai(monkeypatch)
    monkeypatch.setattr(providers, "load_environment", lambda: None)
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY"):
        providers.get_llm()

    assert FakeChatOpenAI.calls == []


def test_get_llm_routes_vllm_to_local_openai_compatible_endpoint(monkeypatch) -> None:
    _install_fake_langchain_openai(monkeypatch)
    monkeypatch.setattr(providers, "load_environment", lambda: None)
    monkeypatch.setenv("LLM_PROVIDER", "vllm")
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.setenv("VLLM_PORT", "9000")

    llm = providers.get_llm()

    assert llm.kwargs == {
        "model": "Qwen/Qwen3-30B-A3B-Instruct-2507-FP8",
        "base_url": "http://localhost:9000/v1",
        "api_key": "not-needed",
        "temperature": 0.3,
        "max_tokens": 4096,
    }


def test_get_llm_rejects_unsupported_provider_after_loading_environment(monkeypatch) -> None:
    _install_fake_langchain_openai(monkeypatch)
    load_calls: list[str] = []
    monkeypatch.setattr(providers, "load_environment", lambda: load_calls.append("loaded"))
    monkeypatch.setenv("LLM_PROVIDER", "unknown-provider")

    with pytest.raises(ValueError, match="Unsupported LLM_PROVIDER: unknown-provider"):
        providers.get_llm()

    assert load_calls == ["loaded"]
    assert FakeChatOpenAI.calls == []
