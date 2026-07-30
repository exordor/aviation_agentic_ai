"""ATMONTO-aligned Traffic Management Initiative family profiles.

The curated application profile is the single registry for publishable,
deferred, and explicit boundary families.  Source detection remains a
deterministic adapter concern; it does not promote boundary notices to formal
ATMONTO event types.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT


APPLICATION_PROFILE_PATH = Path(
    "data/ontology/curated/atmonto_application_profile_v1.json"
)


@dataclass(frozen=True)
class TMIEventProfile:
    """A source-family policy bound to an exact ATMONTO class when active."""

    code: str
    ontology_class: str | None
    publication_status: str
    required_fields: tuple[str, ...]
    retrieval_label: str
    field_mappings: dict[str, str]

    @property
    def publishable(self) -> bool:
        return self.publication_status == "active" and self.ontology_class is not None

    @property
    def authority_term(self) -> str:
        """FAA term-registry abbreviation used for this event family."""

        return "RR" if self.code == "REROUTE" else self.code

    @property
    def prefixed_ontology_class(self) -> str | None:
        """Return the exact ATMONTO class in the runtime prefix form."""

        namespace = "https://data.nasa.gov/ontologies/atmonto/ATM#"
        if self.ontology_class is None:
            return None
        if not self.ontology_class.startswith(namespace):
            raise ValueError(
                f"active TMI class is outside the ATMONTO ATM namespace: {self.code}"
            )
        return "atm:" + self.ontology_class.removeprefix(namespace)

    def prefixed_property(self, field: str) -> str | None:
        """Return one admitted ATMONTO property in runtime prefix form."""

        iri = self.field_mappings.get(field)
        if iri is None:
            return None
        namespace = "https://data.nasa.gov/ontologies/atmonto/ATM#"
        if not iri.startswith(namespace):
            raise ValueError(
                f"TMI field mapping is outside the ATMONTO ATM namespace: "
                f"{self.code}.{field}"
            )
        return "atm:" + iri.removeprefix(namespace)


def _load_registry_rows() -> tuple[dict[str, Any], ...]:
    path = PROJECT_ROOT / APPLICATION_PROFILE_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = [
        *payload["active_event_profiles"],
        *payload["deferred_event_profiles"],
        *payload["boundary_event_profiles"],
    ]
    return tuple(rows)


def _to_profile(row: Mapping[str, Any]) -> TMIEventProfile:
    return TMIEventProfile(
        code=str(row["code"]),
        ontology_class=(
            str(row["ontology_class"]) if row.get("ontology_class") is not None else None
        ),
        publication_status=str(row["publication_status"]),
        required_fields=tuple(str(value) for value in row.get("required_fields", [])),
        retrieval_label=str(row["retrieval_label"]),
        field_mappings={
            str(field): str(predicate)
            for field, predicate in row.get("field_mappings", {}).items()
        },
    )


def _profiles_by_code() -> dict[str, TMIEventProfile]:
    return {
        profile.code: profile
        for profile in (_to_profile(row) for row in _load_registry_rows())
    }


def get_tmi_profile(
    code: str,
    *,
    publishable_only: bool = False,
) -> TMIEventProfile | None:
    """Return a registered family profile, optionally restricted to active ones."""

    profile = _profiles_by_code().get(code.upper())
    if profile is None or (publishable_only and not profile.publishable):
        return None
    return profile


def active_tmi_profiles() -> tuple[TMIEventProfile, ...]:
    """Return active profiles in the order frozen by the application profile."""

    return tuple(
        profile
        for row in _load_registry_rows()
        if (profile := _to_profile(row)).publishable
    )


def registered_tmi_profiles() -> tuple[TMIEventProfile, ...]:
    """Return all active, deferred, and boundary profiles in file order."""

    return tuple(_to_profile(row) for row in _load_registry_rows())


_HEADER_RE = re.compile(r"ATCSCC\s+ADVZY\b[^\r\n]*", re.IGNORECASE)


def _header(text: str) -> str:
    match = _HEADER_RE.search(text)
    return match.group(0).upper() if match else text.upper()


def classify_tmi_family(text: str) -> str | None:
    """Classify one advisory without conflating reference notices with TMIs."""

    header = _header(text)
    if "REROUTE CANCELLATION" in header:
        return "REROUTE_CANCELLATION"
    if "GROUND DELAY PROGRAM" in header or re.search(r"\bGDP\b", header):
        return "GDP"
    if "GROUND STOP" in header or re.search(r"\bGS\b", header):
        return "GS"
    if re.search(r"\bROUTE\s+RQD\b", header):
        return "REROUTE"
    if re.search(r"\bNATOTS(?:_| )RQD\b", header):
        return "NATOTS"
    if "ARRIVAL DELAYS" in header:
        return "ARRIVAL_DELAY"
    if re.search(r"\bSWAP(?:_| )FYI\b", header):
        return "SWAP"
    if re.search(r"\bHOTLINE(?:_| )FYI\b", header):
        return "HOTLINE"
    return None


def detected_family_counts(records: Iterable[Mapping[str, object] | str]) -> dict[str, int]:
    """Count recognized active, deferred, and boundary families."""

    counts: Counter[str] = Counter()
    for record in records:
        text = record if isinstance(record, str) else str(record.get("text") or "")
        if family := classify_tmi_family(text):
            counts[family] += 1
    return dict(sorted(counts.items()))


__all__ = [
    "APPLICATION_PROFILE_PATH",
    "TMIEventProfile",
    "active_tmi_profiles",
    "classify_tmi_family",
    "detected_family_counts",
    "get_tmi_profile",
    "registered_tmi_profiles",
]
