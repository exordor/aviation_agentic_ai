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


def test_llm_provider_helpers_expose_shared_defaults(monkeypatch) -> None:
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "vllm")

    assert providers.SUPPORTED_LLM_PROVIDERS == frozenset({"openai", "deepseek", "newapi", "sub2api", "vllm"})
    assert providers.configured_llm_provider() == "vllm"
    assert providers.configured_llm_model("openai") == "gpt-4o-mini"
    assert providers.configured_llm_model("deepseek") == "deepseek-chat"
    assert providers.configured_llm_model("newapi") == "glm-5.2"
    assert providers.configured_llm_model("sub2api") == "gpt-5.5"
    assert providers.configured_llm_model("vllm") == "Qwen/Qwen3-30B-A3B-Instruct-2507-FP8"
    assert providers.configured_llm_model("unknown-provider") == "unknown"


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
        "timeout": 120.0,
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
        "timeout": 120.0,
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


def test_get_llm_routes_newapi_to_openai_compatible_endpoint(monkeypatch) -> None:
    _install_fake_langchain_openai(monkeypatch)
    monkeypatch.setattr(providers, "load_environment", lambda: None)
    monkeypatch.setenv("LLM_PROVIDER", "newapi")
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.setenv("NEWAPI_BASE_URL", "http://localhost:3000")
    monkeypatch.setenv("NEWAPI_API_KEY", "newapi-key")

    llm = providers.get_llm(temperature=0.2, max_tokens=789)

    assert llm.kwargs == {
        "model": "glm-5.2",
        "base_url": "http://localhost:3000/v1",
        "api_key": "newapi-key",
        "temperature": 0.2,
        "max_tokens": 789,
        "timeout": 120.0,
    }


def test_get_llm_preserves_newapi_base_url_with_v1_path(monkeypatch) -> None:
    _install_fake_langchain_openai(monkeypatch)
    monkeypatch.setattr(providers, "load_environment", lambda: None)
    monkeypatch.setenv("LLM_PROVIDER", "newapi")
    monkeypatch.setenv("MODEL_NAME", "deepseek-v4-pro")
    monkeypatch.setenv("NEWAPI_BASE_URL", "http://localhost:3000/v1")
    monkeypatch.setenv("NEWAPI_API_KEY", "newapi-key")

    llm = providers.get_llm()

    assert llm.kwargs["model"] == "deepseek-v4-pro"
    assert llm.kwargs["base_url"] == "http://localhost:3000/v1"


def test_get_llm_rejects_newapi_without_api_key(monkeypatch) -> None:
    _install_fake_langchain_openai(monkeypatch)
    monkeypatch.setattr(providers, "load_environment", lambda: None)
    monkeypatch.setenv("LLM_PROVIDER", "newapi")
    monkeypatch.delenv("NEWAPI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="NEWAPI_API_KEY"):
        providers.get_llm()

    assert FakeChatOpenAI.calls == []


def test_get_llm_routes_sub2api_to_openai_compatible_endpoint(monkeypatch) -> None:
    _install_fake_langchain_openai(monkeypatch)
    monkeypatch.setattr(providers, "load_environment", lambda: None)
    monkeypatch.setenv("LLM_PROVIDER", "sub2api")
    monkeypatch.delenv("MODEL_NAME", raising=False)
    monkeypatch.setenv("SUB2API_BASE_URL", "http://127.0.0.1:8080")
    monkeypatch.setenv("SUB2API_API_KEY", "sub2api-key")

    llm = providers.get_llm(temperature=0.2, max_tokens=789)

    assert llm.kwargs == {
        "model": "gpt-5.5",
        "base_url": "http://127.0.0.1:8080/v1",
        "api_key": "sub2api-key",
        "temperature": 0.2,
        "max_tokens": 789,
        "timeout": 120.0,
        "reasoning_effort": "medium",
    }


def test_get_llm_preserves_sub2api_base_url_with_v1_path(monkeypatch) -> None:
    _install_fake_langchain_openai(monkeypatch)
    monkeypatch.setattr(providers, "load_environment", lambda: None)
    monkeypatch.setenv("LLM_PROVIDER", "sub2api")
    monkeypatch.setenv("MODEL_NAME", "gpt-5.4")
    monkeypatch.setenv("SUB2API_BASE_URL", "http://127.0.0.1:8080/v1")
    monkeypatch.setenv("SUB2API_API_KEY", "sub2api-key")

    llm = providers.get_llm()

    assert llm.kwargs["model"] == "gpt-5.4"
    assert llm.kwargs["base_url"] == "http://127.0.0.1:8080/v1"


def test_get_llm_rejects_sub2api_without_api_key(monkeypatch) -> None:
    _install_fake_langchain_openai(monkeypatch)
    monkeypatch.setattr(providers, "load_environment", lambda: None)
    monkeypatch.setenv("LLM_PROVIDER", "sub2api")
    monkeypatch.delenv("SUB2API_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="SUB2API_API_KEY"):
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
        "timeout": 120.0,
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
