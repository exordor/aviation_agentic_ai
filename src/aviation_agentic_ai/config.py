from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

import yaml

from aviation_agentic_ai.paths import PROJECT_ROOT

_ENVIRONMENT_LOADED = False
_ENV_LOCK = threading.Lock()


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def load_yaml(path: str | Path) -> dict[str, Any]:
    config_path = resolve_project_path(path)
    with config_path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in YAML config: {config_path}")
    return data


def load_default_config() -> dict[str, Any]:
    return load_yaml("configs/default.yaml")


def configured_dataset_id(config: dict[str, Any]) -> str:
    """Return the persistent evidence-store dataset identity."""

    agent_system = config.get("agent_system")
    configured = agent_system if isinstance(agent_system, dict) else {}
    dataset_id = configured.get("dataset_id")
    if not isinstance(dataset_id, str) or not dataset_id:
        raise ValueError(
            "config.agent_system.dataset_id must be a non-empty string"
        )
    return dataset_id


def configured_store_root(config: dict[str, Any]) -> Path:
    """Return the configured project-local evidence-store root."""

    agent_system = config.get("agent_system")
    configured = agent_system if isinstance(agent_system, dict) else {}
    storage = configured.get("storage")
    storage_config = storage if isinstance(storage, dict) else {}
    store_root = storage_config.get("root")
    if not isinstance(store_root, str) or not store_root:
        raise ValueError(
            "config.agent_system.storage.root must be a non-empty path"
        )
    return resolve_project_path(store_root)


def load_environment(*, force: bool = False) -> bool:
    """Load `.env` once from the configuration layer.

    Returns true when python-dotenv was available and asked to load environment
    variables. Callers should still read `os.environ` directly so tests can use
    monkeypatching without resetting this loader.
    """
    with _ENV_LOCK:
        global _ENVIRONMENT_LOADED
        if _ENVIRONMENT_LOADED and not force:
            return False

        try:
            from dotenv import load_dotenv
        except ImportError:
            _ENVIRONMENT_LOADED = True
            return False

        load_dotenv(PROJECT_ROOT / ".env")
        _ENVIRONMENT_LOADED = True
        return True
