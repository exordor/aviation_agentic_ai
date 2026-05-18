from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from aviation_agentic_ai.paths import PROJECT_ROOT


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
