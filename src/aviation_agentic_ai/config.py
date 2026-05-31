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
