from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import project_relative_path


def normalize_report_text(value: Any) -> str:
    """Normalize lightweight report text without changing punctuation."""
    return " ".join(str(value).lower().split())


def read_json_object(path: str | Path) -> dict[str, Any]:
    """Read a JSON report that must exist and contain an object."""
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected object JSON report: {project_relative_path(source)}")
    return payload


def read_json_object_or_empty(
    path: str | Path,
    *,
    wrap_non_object: bool = False,
) -> dict[str, Any]:
    """Read a JSON object report, returning an empty object when absent."""
    source = Path(path)
    if not source.exists():
        return {}
    payload = json.loads(source.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload
    return {"value": payload} if wrap_non_object else {}


def read_json_object_or_none(
    path: str | Path,
    *,
    wrap_non_object: bool = True,
) -> dict[str, Any] | None:
    """Read a JSON object report, returning None when absent."""
    source = Path(path)
    if not source.exists():
        return None
    payload = json.loads(source.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return payload
    return {"value": payload} if wrap_non_object else None


def write_json_report(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
