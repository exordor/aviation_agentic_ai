from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from pydantic import BaseModel

from aviation_agentic_ai.utils.io import (
    read_json_document,
    read_jsonl_objects,
    write_json_document,
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    return value


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    return read_jsonl_objects(path)


def write_jsonl(path: str | Path, rows: Iterable[Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(
        json.dumps(_jsonable(row), sort_keys=True, ensure_ascii=False) + "\n" for row in rows
    )
    target.write_text(payload, encoding="utf-8")
    return target


def read_json(path: str | Path) -> Any:
    return read_json_document(path)


def write_json(path: str | Path, payload: Any) -> Path:
    return write_json_document(_jsonable(payload), path)
