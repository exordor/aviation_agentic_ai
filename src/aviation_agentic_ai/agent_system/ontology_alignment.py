"""Validation helpers for the versioned ATMONTO application profile."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.tmi_profiles import (
    APPLICATION_PROFILE_PATH,
)
from aviation_agentic_ai.ontology.atmonto_minimal_loop import SCHEMA_SLICE_PATH
from aviation_agentic_ai.paths import PROJECT_ROOT


ATMONTO_NAMESPACE_ROOT = "https://data.nasa.gov/ontologies/atmonto/"
_EXTERNAL_STANDARD_NAMESPACES = (
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "http://www.w3.org/2001/XMLSchema#",
    "http://www.w3.org/ns/prov#",
    "http://www.w3.org/ns/sosa/",
    "http://www.w3.org/2006/time#",
    "http://www.w3.org/2004/02/skos/core#",
    "http://qudt.org/schema/qudt/",
    "http://purl.org/dc/terms/",
)
_ATMONTO_PREFIXES = ("atm:", "nas:", "data:", "equipment:", "general:")
_EXTERNAL_PREFIXES = (
    "rdf:",
    "xsd:",
    "prov:",
    "sosa:",
    "time:",
    "skos:",
    "qudt:",
    "dcterms:",
)


@dataclass(frozen=True)
class ApplicationProfileValidation:
    valid: bool
    errors: tuple[str, ...]


def load_atmonto_application_profile(
    path: str | Path | None = None,
) -> dict[str, Any]:
    target = Path(path) if path is not None else PROJECT_ROOT / APPLICATION_PROFILE_PATH
    return json.loads(target.read_text(encoding="utf-8"))


def validate_atmonto_application_profile(
    profile: dict[str, Any],
    *,
    repo_root: str | Path = PROJECT_ROOT,
) -> ApplicationProfileValidation:
    """Validate source pins and the active ATMONTO term boundary."""

    root = Path(repo_root)
    errors: list[str] = []
    if profile.get("profile_id") != "atmonto-application-profile-v1":
        errors.append("unexpected_profile_id")

    modules = profile.get("schema_authority", {}).get("upstream_modules", [])
    for module in modules:
        relative_path = Path(str(module.get("path") or ""))
        expected = str(module.get("sha256") or "")
        source = root / relative_path
        if not source.is_file():
            errors.append(f"missing_upstream_module:{relative_path.as_posix()}")
            continue
        actual = sha256(source.read_bytes()).hexdigest()
        if actual != expected:
            errors.append(f"upstream_checksum_mismatch:{relative_path.as_posix()}")

    schema_slice_path = root / SCHEMA_SLICE_PATH
    if schema_slice_path.is_file():
        schema_slice = json.loads(schema_slice_path.read_text(encoding="utf-8"))
        admitted_classes = {
            str(row["iri"]) for row in schema_slice.get("classes", [])
        }
        admitted_properties = {
            str(row["iri"])
            for category in ("object_properties", "datatype_properties")
            for row in schema_slice.get(category, [])
        }
    else:
        admitted_classes = set()
        admitted_properties = set()
        errors.append(f"missing_schema_slice:{SCHEMA_SLICE_PATH.as_posix()}")

    for row in profile.get("active_event_profiles", []):
        code = str(row.get("code") or "")
        event_class = str(row.get("ontology_class") or "")
        if not event_class.startswith(ATMONTO_NAMESPACE_ROOT):
            errors.append(f"non_atmonto_active_class:{code}")
        elif event_class not in admitted_classes:
            errors.append(f"unadmitted_active_class:{code}:{event_class}")
        for predicate in row.get("field_mappings", {}).values():
            if not str(predicate).startswith(ATMONTO_NAMESPACE_ROOT):
                errors.append(
                    f"non_atmonto_active_property:{code}:{predicate}"
                )
            elif str(predicate) not in admitted_properties:
                errors.append(f"unadmitted_active_property:{code}:{predicate}")

    return ApplicationProfileValidation(valid=not errors, errors=tuple(errors))


def build_knowledge_alignment_audit(
    facts: Iterable[Any],
    *,
    profile_path: str | Path | None = None,
) -> dict[str, Any]:
    """Summarize formal vocabulary alignment without creating a new ledger."""

    target = (
        Path(profile_path)
        if profile_path is not None
        else PROJECT_ROOT / APPLICATION_PROFILE_PATH
    )
    profile = load_atmonto_application_profile(target)
    rows = tuple(facts)
    layer_counts = Counter(
        str(fact.validation_profile.layer)
        for fact in rows
    )
    terms = {
        str(value)
        for fact in rows
        for value in (
            fact.subject_class_iri,
            fact.predicate_iri,
            fact.object_class_iri,
            fact.datatype_iri,
        )
        if value
    }
    classified: dict[str, list[str]] = {
        "atmonto_core": [],
        "external_standard_extension": [],
        "project_extension": [],
        "unknown": [],
    }
    for term in sorted(terms):
        if term.startswith(ATMONTO_NAMESPACE_ROOT) or term.startswith(
            _ATMONTO_PREFIXES
        ):
            classified["atmonto_core"].append(term)
        elif term.startswith(_EXTERNAL_STANDARD_NAMESPACES) or term.startswith(
            _EXTERNAL_PREFIXES
        ):
            classified["external_standard_extension"].append(term)
        elif term.startswith("urn:aviation-agentic-ai:"):
            classified["project_extension"].append(term)
        else:
            classified["unknown"].append(term)

    return {
        "report_version": "knowledge-alignment-audit-v1",
        "application_profile": {
            "profile_id": str(profile["profile_id"]),
            "profile_version": str(profile["profile_version"]),
            "sha256": sha256(target.read_bytes()).hexdigest(),
        },
        "atmgraph_reference": {
            "role": str(profile["atmgraph_alignment"]["role"]),
            "principles": list(profile["atmgraph_alignment"]["principles"]),
            "verification_scope": (
                "declared construction principles; not namespace or "
                "instance equivalence"
            ),
        },
        "formal_fact_count": len(rows),
        "fact_counts_by_validation_layer": dict(sorted(layer_counts.items())),
        "schema_terms": classified,
        "unknown_formal_term_count": len(classified["unknown"]),
    }


__all__ = [
    "ApplicationProfileValidation",
    "build_knowledge_alignment_audit",
    "load_atmonto_application_profile",
    "validate_atmonto_application_profile",
]
