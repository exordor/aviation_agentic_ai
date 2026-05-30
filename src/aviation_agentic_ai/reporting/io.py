from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.utils.io import (
    JSONDocumentReadError,
    read_json_document,
    read_json_document_or_none,
    write_json_document,
)

__all__ = [
    "JSONDocumentReadError",
    "normalize_report_text",
    "read_json_document",
    "read_json_document_or_none",
    "read_json_object",
    "read_json_object_or_empty",
    "read_json_object_or_none",
    "write_json_report",
]


def normalize_report_text(value: Any) -> str:
    """Normalize lightweight report text without changing punctuation."""
    return " ".join(str(value).lower().split())


def read_json_object(path: str | Path) -> dict[str, Any]:
    """Read a JSON report that must exist and contain an object."""
    source = Path(path)
    payload = read_json_document(source)
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
    payload = read_json_document_or_none(source)
    if payload is None:
        return {}
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
    payload = read_json_document_or_none(source)
    if payload is None:
        return None
    if isinstance(payload, dict):
        return payload
    return {"value": payload} if wrap_non_object else None


def write_json_report(
    result: dict[str, Any],
    output_path: str | Path,
    *,
    sort_keys: bool = True,
) -> Path:
    return write_json_document(result, output_path, sort_keys=sort_keys)
