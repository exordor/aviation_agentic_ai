import builtins
from datetime import date
from pathlib import Path
from types import ModuleType

import pytest

from aviation_agentic_ai import config as config_module
from aviation_agentic_ai.config import (
    load_environment,
    load_yaml,
    resolved_config_checksum,
)
from aviation_agentic_ai.paths import PROJECT_ROOT


def test_load_yaml_recursively_deep_merges_relative_includes(
    tmp_path: Path,
) -> None:
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    (tmp_path / "base.yaml").write_text(
        """
runtime:
  storage:
    root: base-store
    sqlite: evidence.sqlite3
  limits:
    turns: 2
sequence:
  - base
""".strip(),
        encoding="utf-8",
    )
    (nested_dir / "first.yaml").write_text(
        """
includes:
  - ../base.yaml
runtime:
  storage:
    root: first-store
  limits:
    tools: 4
sources:
  advisory: advisory.jsonl
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "second.yaml").write_text(
        """
runtime:
  storage:
    chroma: vector-index
  limits:
    turns: 3
sequence:
  - second
""".strip(),
        encoding="utf-8",
    )
    root_config = tmp_path / "root.yaml"
    root_config.write_text(
        """
includes:
  - nested/first.yaml
  - second.yaml
runtime:
  storage:
    root: local-store
  local: true
""".strip(),
        encoding="utf-8",
    )

    config = load_yaml(root_config)

    assert config == {
        "runtime": {
            "storage": {
                "root": "local-store",
                "sqlite": "evidence.sqlite3",
                "chroma": "vector-index",
            },
            "limits": {"turns": 3, "tools": 4},
            "local": True,
        },
        "sequence": ["second"],
        "sources": {"advisory": "advisory.jsonl"},
    }


def test_load_yaml_rejects_recursive_include_cycles(tmp_path: Path) -> None:
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    first = tmp_path / "first.yaml"
    second = nested_dir / "second.yaml"
    first.write_text("includes:\n  - nested/second.yaml\n", encoding="utf-8")
    second.write_text("includes:\n  - ../first.yaml\n", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match=r"YAML include cycle.*first\.yaml.*second\.yaml.*first\.yaml",
    ):
        load_yaml(first)


def test_resolved_config_checksum_is_canonical_and_content_sensitive() -> None:
    first = {"sources": {"b": 2, "a": 1}, "runtime": {"enabled": True}}
    reordered = {"runtime": {"enabled": True}, "sources": {"a": 1, "b": 2}}
    changed = {"runtime": {"enabled": False}, "sources": {"a": 1, "b": 2}}

    assert resolved_config_checksum(first) == resolved_config_checksum(reordered)
    assert resolved_config_checksum(first) != resolved_config_checksum(changed)
    assert len(resolved_config_checksum(first)) == 64


def test_resolved_config_checksum_accepts_yaml_date_values() -> None:
    assert resolved_config_checksum({"sample_date": date(2014, 7, 15)}) == (
        resolved_config_checksum({"sample_date": "2014-07-15"})
    )


def test_active_aviation_config_composes_runtime_sources_and_dataset_scope(
) -> None:
    config = load_yaml("configs/aviation_knowledge_v1.yaml")

    assert config["snapshot_set_id"] == "aviation-knowledge-2026-05-v1"
    assert config["agent_system"] == {
        "dataset_id": "aviation-knowledge-2026-05-v1",
        "storage": {
            "root": "data/stores/aviation/aviation-knowledge-2026-05-v1",
            "sqlite": "aviation_evidence.sqlite3",
            "chroma": "chroma",
            "exports": "exports",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        },
    }
    assert config["sources"]["nasa_atmonto_instances"] == (
        "data/raw/nasa_atmonto_prototype/allFilesTTL.zip"
    )
    assert config["source_checksums"]["nasa_atmonto_instances"] == (
        "93dc9675772649079bef11fe3519e6d99fe0d549318a6696af888b7f2b74df47"
    )
    assert config["source_urls"]["nasa_atmonto_instances"] == (
        "https://data.nasa.gov/docs/ontologies/atmonto/allFilesTTL.zip"
    )
    nasa_metadata = config["source_metadata"]["nasa_atmonto_instances"]
    assert nasa_metadata["naive_time_basis"] == (
        "source_naive_interpreted_utc"
    )
    assert nasa_metadata["naive_time_interpretation"] == {
        "assumed_timezone": "UTC",
        "source_declares_timezone": False,
        "status": "ingestion_interpretation",
    }


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
