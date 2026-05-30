from __future__ import annotations

import json
import re
from typing import Any

FENCED_JSON_RE = re.compile(
    r"```(?:json)?\s*(.*?)\s*```",
    flags=re.DOTALL | re.IGNORECASE,
)


def extract_json_payload(text: str) -> str:
    """Extract the most likely JSON payload from an LLM response."""
    stripped = text.strip()
    fenced = FENCED_JSON_RE.fullmatch(stripped)
    if fenced:
        stripped = fenced.group(1).strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        return stripped[start : end + 1]
    return stripped


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract and parse a JSON object from an LLM response."""
    payload = json.loads(extract_json_payload(text))
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON object.")
    return payload
