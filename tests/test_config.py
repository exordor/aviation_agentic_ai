import builtins
from types import ModuleType

from aviation_agentic_ai import config as config_module
from aviation_agentic_ai.config import (
    load_default_config,
    load_environment,
    load_yaml,
    resolve_project_path,
)
from aviation_agentic_ai.paths import PROJECT_ROOT


def test_load_default_config() -> None:
    config = load_default_config()

    assert config["project"]["name"] == "aviation_agentic_ai"
    assert "curated_ontology" in config["paths"]
    assert "baseline_ontology" in config["paths"]
    assert config["kg_extraction"]["max_tokens"] == 4096


def test_resolve_project_path() -> None:
    path = resolve_project_path("configs/default.yaml")

    assert path.name == "default.yaml"
    assert path.exists()


def test_ontology_generation_config_uses_larger_token_budget() -> None:
    config = load_yaml("configs/ontology_generation.yaml")

    assert config["max_tokens"] == 8192


def test_load_environment_loads_dotenv_once_and_can_force(monkeypatch) -> None:
    calls: list[object] = []
    dotenv_module = ModuleType("dotenv")
    dotenv_module.load_dotenv = lambda dotenv_path=None: calls.append(dotenv_path)
    monkeypatch.setitem(__import__("sys").modules, "dotenv", dotenv_module)
    monkeypatch.setattr(config_module, "_ENVIRONMENT_LOADED", False)

    assert load_environment() is True
    assert load_environment() is False
    assert load_environment(force=True) is True
    assert calls == [PROJECT_ROOT / ".env", PROJECT_ROOT / ".env"]


def test_load_environment_caches_missing_dotenv(monkeypatch) -> None:
    import_calls: list[str] = []
    real_import = builtins.__import__

    def fake_import(name: str, *args, **kwargs):
        if name == "dotenv":
            import_calls.append(name)
            raise ImportError("dotenv unavailable")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    monkeypatch.setattr(config_module, "_ENVIRONMENT_LOADED", False)

    assert load_environment() is False
    assert load_environment() is False
    assert import_calls == ["dotenv"]
