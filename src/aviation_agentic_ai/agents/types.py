from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any

from aviation_agentic_ai.ontology.atmonto_experiment import compact_text


FactIdentityKey = tuple[str, ...]


def evidence_span_hash(value: object) -> str:
    """Return a stable evidence-span hash for iterative extraction bookkeeping."""
    normalized = compact_text(value)
    return sha256(normalized.encode("utf-8")).hexdigest()


def identity_key_label(key: FactIdentityKey) -> str:
    return "|".join(key)


@dataclass
class ExtractionTrace:
    iterations_used: int = 0
    budget_exhausted: bool = False
    blocked_repeat_count: int = 0
    accepted_identity_keys: set[FactIdentityKey] = field(default_factory=set)
    blocked_identity_keys: set[FactIdentityKey] = field(default_factory=set)
    accepted_evidence_hashes: dict[str, str] = field(default_factory=dict)
    blocked_evidence_hashes: dict[str, str] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ExtractionResult:
    facts: list[dict[str, Any]]
    blocked: list[dict[str, Any]]
    trace: ExtractionTrace
    metadata: dict[str, Any]

    def to_record(self) -> dict[str, Any]:
        return {
            "system_id": self.metadata.get("system_id", "L1_agentic_extraction"),
            "source_id": self.metadata.get("source_id"),
            "source_family": self.metadata.get("source_family", "atcscc_advisories"),
            "facts": self.facts,
            "blocked": self.blocked,
            "metadata": self.metadata,
            "trace": {
                "iterations_used": self.trace.iterations_used,
                "budget_exhausted": self.trace.budget_exhausted,
                "blocked_repeat_count": self.trace.blocked_repeat_count,
                "accepted_identity_keys": sorted(identity_key_label(key) for key in self.trace.accepted_identity_keys),
                "blocked_identity_keys": sorted(identity_key_label(key) for key in self.trace.blocked_identity_keys),
                "accepted_evidence_hashes": self.trace.accepted_evidence_hashes,
                "blocked_evidence_hashes": self.trace.blocked_evidence_hashes,
                "events": self.trace.events,
            },
        }
