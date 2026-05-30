from __future__ import annotations

from typing import Any


def nested_value(data: dict[str, Any], *keys: str, default: Any = "TBD") -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current
