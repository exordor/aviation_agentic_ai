from __future__ import annotations

import re
from hashlib import sha256

from aviation_agentic_ai.cross_source.contracts import EntityType, TermCategory


def normalize_code(value: object) -> str:
    return re.sub(r"[^A-Z0-9]+", "", str(value).upper())


def canonical_facility_id(entity_type: EntityType | str, authority_code: object) -> str:
    type_value = entity_type.value if isinstance(entity_type, EntityType) else str(entity_type)
    code = normalize_code(authority_code)
    if not code:
        raise ValueError("Canonical facility ID requires a non-empty authority code")
    return f"urn:aviation-agentic-ai:facility:{type_value}:{code}"


def canonical_term_id(category: TermCategory | str, abbreviation: object) -> str:
    category_value = category.value if isinstance(category, TermCategory) else str(category)
    token = normalize_code(abbreviation)
    if not token:
        raise ValueError("Canonical term ID requires a non-empty abbreviation")
    return f"urn:aviation-agentic-ai:term:{category_value}:{token}"


def stable_id(prefix: str, *parts: object) -> str:
    normalized = "|".join(str(part) for part in parts)
    digest = sha256(normalized.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"
