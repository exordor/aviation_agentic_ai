"""Stable identifiers shared by current and historical subsystems."""

from __future__ import annotations

from hashlib import sha256


def stable_id(prefix: str, *parts: object) -> str:
    """Build the project's existing deterministic short identifier."""

    normalized = "|".join(str(part) for part in parts)
    digest = sha256(normalized.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"
