from __future__ import annotations

from typing import Any


def nested_value(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Safely traverse nested dictionaries to retrieve a value.

    Returns *default* (None by default) if any intermediate key is missing
    or if the intermediate value is not a dict.
    """
    current: Any = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current
