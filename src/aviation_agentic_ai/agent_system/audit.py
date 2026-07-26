"""Small shared sanitizers for persisted Agent audit records."""

from __future__ import annotations

import re
from typing import Any

_SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "credentials",
    "password",
    "secret",
    "access_token",
    "refresh_token",
}
_BEARER_RE = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")
_SECRET_TOKEN_RE = re.compile(r"\bsk-[A-Za-z0-9_-]{6,}\b")
_KEY_VALUE_RE = re.compile(
    r"(?i)\b("
    r"password|credential|credentials|api[_-]?key|authorization|"
    r"access[_-]?token|refresh[_-]?token"
    r")\s*[:=]\s*[^\s,;]+"
)


def sanitize_text(value: Any) -> str:
    """Redact common credential forms from an arbitrary error or text value."""

    text = str(value)
    text = _BEARER_RE.sub("Bearer [REDACTED]", text)
    text = _SECRET_TOKEN_RE.sub("[REDACTED]", text)
    return _KEY_VALUE_RE.sub(
        lambda match: f"{match.group(1)}=[REDACTED]",
        text,
    )


def sanitize_json_value(value: Any) -> Any:
    """Return a JSON-safe value with sensitive keys and strings redacted."""

    if isinstance(value, dict):
        safe: dict[str, Any] = {}
        for key, item in value.items():
            normalized = str(key).lower().replace("-", "_")
            safe[str(key)] = (
                "[REDACTED]"
                if normalized in _SENSITIVE_KEYS
                else sanitize_json_value(item)
            )
        return safe
    if isinstance(value, (list, tuple)):
        return [sanitize_json_value(item) for item in value]
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, (int, float, bool)) or value is None:
        return value
    return sanitize_text(value)
