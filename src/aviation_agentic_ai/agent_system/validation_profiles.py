"""Checksum-pinned ownership for the formal graph validation profiles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import ConfigDict, Field, model_validator

from aviation_agentic_ai.agent_system.contracts import (
    StrictModel,
    ValidatedFact,
    ValidationProfileRef,
)
from aviation_agentic_ai.agent_system.schema_guide import (
    DEFAULT_SCHEMA_SLICE,
    SchemaGuide,
)
from aviation_agentic_ai.config import resolve_project_path

DEFAULT_WEATHER_PROFILE_PATH = "data/ontology/curated/nasa_atmonto_decision_context_weather_slice.json"
DEFAULT_PUBLIC_OBSERVATION_PROFILE_PATH = (
    "data/ontology/curated/decision_case_public_observation_slice.json"
)

ValidationLayer = Literal["decision", "weather", "public_operational_observation"]
EvidenceMode = Literal[
    "source_text",
    "deterministic_derivation",
    "profile_definition",
    "system_membership",
]

_FORBIDDEN_OPERATIONAL_OR_CAUSAL_PREDICATES = frozenset(
    {
        "https://data.nasa.gov/ontologies/atmonto/data#arrivalDemand",
        "https://data.nasa.gov/ontologies/atmonto/data#airportArrivalRate",
        "http://www.w3.org/2002/07/owl#equivalentProperty",
        "http://www.w3.org/2000/01/rdf-schema#subPropertyOf",
        "http://www.w3.org/2004/02/skos/core#exactMatch",
        "http://www.w3.org/2004/02/skos/core#closeMatch",
        "urn:aviation-agentic-ai:causedBy",
        "urn:aviation-agentic-ai:motivatedBy",
        "urn:aviation-agentic-ai:affectedBy",
    }
)


class AggregationProcedureDescriptor(StrictModel):
    """Pinned deterministic aggregation procedure admitted by one profile."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    procedure_id: str = Field(min_length=1)
    checksum: str = Field(min_length=1)
    null_rule: str = Field(min_length=1)


class LoadedValidationProfile(StrictModel):
    """A checksum-verified profile with mappings needed by later writers."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    ref: ValidationProfileRef
    source_path: str = Field(min_length=1)
    namespace_prefixes: dict[str, str]
    class_mappings: dict[str, dict[str, str]]
    property_mappings: dict[str, dict[str, str]]
    forbidden_predicates: tuple[str, ...] = ()
    aggregation_procedure: AggregationProcedureDescriptor | None = None

    @model_validator(mode="after")
    def _validate_mappings(self) -> "LoadedValidationProfile":
        if any(not prefix or not iri for prefix, iri in self.namespace_prefixes.items()):
            raise ValueError("namespace prefixes must have non-empty keys and IRIs")
        for kind, mappings in (
            ("class", self.class_mappings),
            ("property", self.property_mappings),
        ):
            for name, mapping in mappings.items():
                if not name or not isinstance(mapping.get("iri"), str) or not mapping["iri"]:
                    raise ValueError(f"malformed {kind} mapping: {name!r}")
        forbidden = set(self.forbidden_predicates) | _FORBIDDEN_OPERATIONAL_OR_CAUSAL_PREDICATES
        admitted = {
            mapping["iri"]
            for mapping in self.property_mappings.values()
            if "iri" in mapping
        }
        conflict = sorted(admitted & forbidden)
        if conflict:
            raise ValueError(f"forbidden predicate admitted by profile: {conflict[0]}")
        if (
            self.ref.layer == "public_operational_observation"
            and self.aggregation_procedure is None
        ):
            raise ValueError("public-observation profile has no aggregation procedure")
        return self


class ValidationProfileRegistry(StrictModel):
    """An immutable, exact-match registry of independent semantic profiles."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    profiles: tuple[LoadedValidationProfile, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _reject_duplicate_ids(self) -> "ValidationProfileRegistry":
        identifiers = [profile.ref.profile_id for profile in self.profiles]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("duplicate validation profile ID")
        return self

    @property
    def refs(self) -> tuple[ValidationProfileRef, ...]:
        return tuple(profile.ref for profile in self.profiles)

    def resolve(self, ref: ValidationProfileRef) -> LoadedValidationProfile:
        """Resolve only the exact ID, checksum, and semantic layer reference."""

        candidates = [profile for profile in self.profiles if profile.ref.profile_id == ref.profile_id]
        if not candidates:
            raise ValueError(f"unknown validation profile: {ref.profile_id}")
        profile = candidates[0]
        if profile.ref.profile_checksum != ref.profile_checksum:
            raise ValueError(f"validation profile checksum mismatch: {ref.profile_id}")
        if profile.ref.layer != ref.layer:
            raise ValueError(f"validation profile layer mismatch: {ref.profile_id}")
        return profile

    def require_layer(self, ref: ValidationProfileRef, layer: ValidationLayer) -> LoadedValidationProfile:
        """Resolve a profile and reject a fact routed to the wrong layer."""

        profile = self.resolve(ref)
        if profile.ref.layer != layer:
            raise ValueError(f"validation profile has wrong layer: expected {layer}")
        return profile


class LegacyValidatedFact(StrictModel):
    """Read-only decoder shape for artifacts written before profile ownership."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    fact_id: str = Field(min_length=1)
    subject_iri: str = Field(min_length=1)
    subject_class_iri: str = Field(min_length=1)
    predicate_iri: str = Field(min_length=1)
    object_kind: Literal["iri", "literal"]
    object_value: str = Field(min_length=1)
    object_class_iri: str | None = None
    datatype_iri: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    evidence_texts: list[str] = Field(default_factory=list)
    validation_profile: ValidationProfileRef


def decode_legacy_validated_fact(
    payload: dict[str, object],
    *,
    registry: ValidationProfileRegistry,
) -> LegacyValidatedFact:
    """Decode an old fact for inspection only; never return a writable fact."""

    decision_ref = next((ref for ref in registry.refs if ref.layer == "decision"), None)
    if decision_ref is None:
        raise ValueError("legacy decoder requires a decision validation profile")
    legacy_payload = dict(payload)
    legacy_payload["validation_profile"] = decision_ref
    return LegacyValidatedFact.model_validate(legacy_payload)


def validate_fact_for_publication(
    fact: ValidatedFact | LegacyValidatedFact,
    registry: ValidationProfileRegistry,
) -> None:
    """Reject ownership-less and read-only legacy facts before publication."""

    if isinstance(fact, LegacyValidatedFact):
        raise ValueError("legacy facts are read-only and cannot enter new publication")
    registry.resolve(fact.validation_profile)
    if not fact.evidence_ref.strip():
        raise ValueError("new facts require a non-empty evidence_ref")


def _file_checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mapping_entry(entry: dict[str, object]) -> tuple[str, dict[str, str]]:
    if not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in entry.items()
    ):
        raise ValueError("malformed profile mapping entry")
    name = entry.get("prefixed_name") or entry.get("local_name") or entry.get("iri")
    iri = entry.get("iri")
    if not isinstance(name, str) or not isinstance(iri, str):
        raise ValueError("malformed profile mapping entry")
    mapping: dict[str, str] = {"iri": iri}
    label = entry.get("label")
    if isinstance(label, str):
        mapping["label"] = label
    return name, mapping


def _load_json_profile(path: Path, layer: ValidationLayer) -> LoadedValidationProfile:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"validation profile is not an object: {path}")
    profile_id = payload.get("profile_id") or payload.get("schema_slice_id")
    if not isinstance(profile_id, str) or not profile_id:
        raise ValueError(f"validation profile has no ID: {path}")
    namespaces = payload.get("namespace_prefixes", {})
    if not isinstance(namespaces, dict) or not all(
        isinstance(prefix, str) and isinstance(iri, str)
        for prefix, iri in namespaces.items()
    ):
        raise ValueError("namespace_prefixes must be a string mapping")
    raw_classes = payload.get("class_mappings", payload.get("classes", []))
    raw_properties = payload.get("property_mappings")
    if raw_properties is None:
        raw_properties = [
            *payload.get("object_properties", []),
            *payload.get("datatype_properties", []),
        ]
    class_mappings = _parse_mappings(raw_classes, "class")
    property_mappings = _parse_mappings(raw_properties, "property")
    forbidden = payload.get("forbidden_predicates", [])
    if not isinstance(forbidden, list) or not all(isinstance(value, str) for value in forbidden):
        raise ValueError("forbidden_predicates must be a string list")
    raw_procedure = payload.get("aggregation_procedure")
    if raw_procedure is None:
        procedure = None
    elif isinstance(raw_procedure, dict) and all(
        isinstance(raw_procedure.get(field), str) and raw_procedure[field]
        for field in ("id", "checksum", "null_rule")
    ):
        procedure = AggregationProcedureDescriptor(
            procedure_id=raw_procedure["id"],
            checksum=raw_procedure["checksum"],
            null_rule=raw_procedure["null_rule"],
        )
    else:
        raise ValueError("aggregation_procedure must be a complete string descriptor")
    return LoadedValidationProfile(
        ref=ValidationProfileRef(
            profile_id=profile_id,
            profile_checksum=_file_checksum(path),
            layer=layer,
        ),
        source_path=str(path),
        namespace_prefixes=namespaces,
        class_mappings=class_mappings,
        property_mappings=property_mappings,
        forbidden_predicates=tuple(forbidden),
        aggregation_procedure=procedure,
    )


def _parse_mappings(raw: object, kind: str) -> dict[str, dict[str, str]]:
    if isinstance(raw, dict):
        mappings: dict[str, dict[str, str]] = {}
        for name, mapping in raw.items():
            if not isinstance(name, str) or not isinstance(mapping, dict):
                raise ValueError(f"malformed {kind} mappings")
            if not all(
                isinstance(key, str) and isinstance(value, str)
                for key, value in mapping.items()
            ):
                raise ValueError(f"malformed {kind} mapping: {name!r}")
            mappings[name] = dict(mapping)
        return mappings
    if isinstance(raw, list) and all(isinstance(entry, dict) for entry in raw):
        return dict(_mapping_entry(entry) for entry in raw)
    raise ValueError(f"malformed {kind} mappings")


def _decision_profile(decision_guide: SchemaGuide) -> LoadedValidationProfile:
    classes = {
        name: {"iri": item.iri, "label": item.label}
        for name, item in decision_guide.classes.items()
    }
    properties = {
        name: {"iri": item.iri, "label": item.label}
        for name, item in {
            **decision_guide.object_properties,
            **decision_guide.datatype_properties,
        }.items()
    }
    return LoadedValidationProfile(
        ref=ValidationProfileRef(
            profile_id=decision_guide.schema_slice_id,
            profile_checksum=decision_guide.checksum,
            layer="decision",
        ),
        source_path=str(resolve_project_path(DEFAULT_SCHEMA_SLICE)),
        namespace_prefixes={"atm": "https://data.nasa.gov/ontologies/atmonto/ATM#", "nas": "https://data.nasa.gov/ontologies/atmonto/NAS#"},
        class_mappings=classes,
        property_mappings=properties,
    )


def load_validation_profile_registry(
    *,
    decision_guide: SchemaGuide,
    weather_profile_path: str | Path = DEFAULT_WEATHER_PROFILE_PATH,
    public_observation_profile_path: str | Path = DEFAULT_PUBLIC_OBSERVATION_PROFILE_PATH,
) -> ValidationProfileRegistry:
    """Load the three independent profiles and pin each file's SHA-256."""

    weather_path = resolve_project_path(weather_profile_path)
    observation_path = resolve_project_path(public_observation_profile_path)
    return ValidationProfileRegistry(
        profiles=(
            _decision_profile(decision_guide),
            _load_json_profile(weather_path, "weather"),
            _load_json_profile(observation_path, "public_operational_observation"),
        )
    )


__all__ = [
    "AggregationProcedureDescriptor",
    "DEFAULT_PUBLIC_OBSERVATION_PROFILE_PATH",
    "DEFAULT_WEATHER_PROFILE_PATH",
    "LegacyValidatedFact",
    "LoadedValidationProfile",
    "ValidationProfileRef",
    "ValidationProfileRegistry",
    "decode_legacy_validated_fact",
    "load_validation_profile_registry",
    "validate_fact_for_publication",
]
