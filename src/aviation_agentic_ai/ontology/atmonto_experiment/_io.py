"""AUTO-SPLIT from ontology/atmonto_experiment.py. See git history."""
from __future__ import annotations

from typing import Any
from collections.abc import Iterable
from pathlib import Path
import json
from hashlib import sha256

def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records

def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)

def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    payload = "\n".join(json.dumps(record, sort_keys=True, ensure_ascii=False) for record in records)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(payload + ("\n" if payload else ""), encoding="utf-8")
    tmp.replace(path)

def append_jsonl_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
        handle.flush()

def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def _jsonl_semantically_equal(
    left: list[dict[str, Any]], right: list[dict[str, Any]]
) -> bool:
    """Compare two JSONL record lists for semantic equality, normalising key order."""
    if len(left) != len(right):
        return False
    for a, b in zip(left, right):
        if json.dumps(a, sort_keys=True, ensure_ascii=False) != json.dumps(
            b, sort_keys=True, ensure_ascii=False
        ):
            return False
    return True

def compact_text(value: object) -> str:
    return " ".join(str(value or "").split())

def ceil_div(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    return -(-numerator // denominator)

def term_name(value: object) -> str:
    text = str(value or "")
    if "#" in text:
        return text.rsplit("#", 1)[-1]
    if "/" in text and text.startswith(("http://", "https://", "urn:")):
        return text.rstrip("/").rsplit("/", 1)[-1]
    if ":" in text and not text.startswith(("http://", "https://", "urn:")):
        return text.rsplit(":", 1)[-1]
    return text

def read_jsonl_lenient(path: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    invalid_lines: list[dict[str, Any]] = []
    if not path.exists():
        return {
            "exists": False,
            "records": records,
            "line_count": 0,
            "invalid_json_line_count": 0,
            "invalid_json_lines": invalid_lines,
        }
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                invalid_lines.append(
                    {
                        "line_number": line_number,
                        "error": exc.msg,
                    }
                )
                continue
            if isinstance(payload, dict):
                records.append(payload)
            else:
                invalid_lines.append(
                    {
                        "line_number": line_number,
                        "error": "top_level_json_value_is_not_object",
                    }
                )
    return {
        "exists": True,
        "records": records,
        "line_count": len(records) + len(invalid_lines),
        "invalid_json_line_count": len(invalid_lines),
        "invalid_json_lines": invalid_lines[:10],
    }

def read_json_lenient(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "payload": None, "error": None}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"exists": True, "payload": None, "error": exc.msg}
    if not isinstance(payload, dict):
        return {"exists": True, "payload": None, "error": "top_level_json_value_is_not_object"}
    return {"exists": True, "payload": payload, "error": None}

def read_json_if_exists(path: Path) -> dict[str, Any]:
    return read_json(path) if path.exists() else {}
