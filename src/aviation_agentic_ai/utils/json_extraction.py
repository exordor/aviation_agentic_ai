from __future__ import annotations

import json
import re
from typing import Any


class JSONPayloadExtractionError(ValueError):
    """Raised when an LLM-style response does not contain valid JSON payload."""


FENCED_JSON_RE = re.compile(
    r"```(?:json)?\s*(.*?)\s*```",
    flags=re.DOTALL | re.IGNORECASE,
)


def _json_starts(text: str) -> list[int]:
    return sorted(
        [index for index, char in enumerate(text) if char in {"{", "["}],
    )


def _first_decodable_payload(text: str) -> str | None:
    decoder = json.JSONDecoder()
    for start in _json_starts(text):
        try:
            _value, end = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            continue
        return text[start : start + end]
    return None


def extract_json_payload(text: str) -> str:
    """Extract the most likely JSON object or array payload from an LLM response."""
    stripped = text.strip()
    if not stripped:
        return ""
    fenced = FENCED_JSON_RE.fullmatch(stripped)
    if fenced:
        return fenced.group(1).strip()
    try:
        _value, end = json.JSONDecoder().raw_decode(stripped)
    except json.JSONDecodeError:
        embedded = _first_decodable_payload(stripped)
        if embedded is not None:
            return embedded
    else:
        if not stripped[end:].strip():
            return stripped
    embedded = _first_decodable_payload(stripped)
    if embedded is not None:
        return embedded
    return stripped


def parse_json_payload(text: str) -> Any:
    """Extract and parse JSON from text, raising a contextual error on failure."""
    payload = extract_json_payload(text)
    if not payload:
        raise JSONPayloadExtractionError("No JSON payload found in empty text.")
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        preview = payload[:160].replace("\n", "\\n")
        raise JSONPayloadExtractionError(
            f"Invalid JSON payload near: {preview}"
        ) from exc


def extract_json_object(text: str) -> dict[str, Any]:
    """Extract and parse a JSON object from text."""
    payload = parse_json_payload(text)
    if not isinstance(payload, dict):
        raise JSONPayloadExtractionError("Expected a JSON object.")
    return payload
