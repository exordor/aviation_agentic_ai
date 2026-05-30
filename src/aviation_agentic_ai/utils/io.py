from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import project_relative_path


class JSONDocumentReadError(json.JSONDecodeError):
    """Raised when a JSON document cannot be parsed with file context."""


def read_json_document(path: str | Path) -> Any:
    """Read a JSON document that must exist."""
    source = Path(path)
    try:
        return json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise JSONDocumentReadError(
            f"Invalid JSON document in {project_relative_path(source)}: {exc.msg}",
            exc.doc,
            exc.pos,
        ) from exc


def read_json_document_or_none(path: str | Path) -> Any | None:
    """Read any JSON document, returning None when absent."""
    source = Path(path)
    if not source.exists():
        return None
    return read_json_document(source)


def write_json_document(
    data: Any,
    output_path: str | Path,
    *,
    sort_keys: bool = True,
) -> Path:
    """Write a JSON document with the project's stable report formatting."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, sort_keys=sort_keys) + "\n",
        encoding="utf-8",
    )
    return path
