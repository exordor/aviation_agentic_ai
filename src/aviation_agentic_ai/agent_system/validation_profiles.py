"""Checksum-pinned ownership for the formal graph validation profiles."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import ConfigDict, Field, model_validator

from aviation_agentic_ai.agent_system.contracts import (
    SourceFamily,
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
    "data/ontology/curated/public_observation_slice.json"
)
DEFAULT_FLIGHT_OPERATION_PROFILE_PATH = (
    "data/ontology/curated/atmonto_flight_operation_slice.json"
)
DEFAULT_AERONAUTICAL_REFERENCE_PROFILE_PATH = (
    "data/ontology/curated/atmonto_aeronautical_reference_slice.json"
)
DEFAULT_TRAJECTORY_PROFILE_PATH = (
    "data/ontology/curated/atmonto_trajectory_slice.json"
)
DEFAULT_FAA_ORDER_ONTOLOGY_PROFILE_PATH = (
    "data/ontology/curated/faa_jo_7210_3ee_ontology_profile_v2.json"
)

ValidationLayer = Literal[
    "decision",
    "weather",
    "public_operational_observation",
    "flight_operation",
    "aeronautical_reference",
    "trajectory",
    "atmonto_public_sample",
    "document_reference",
]
EvidenceMode = Literal[
    "source_text",
    "deterministic_derivation",
    "profile_definition",
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
    class_ancestors: dict[str, tuple[str, ...]] = Field(
        default_factory=dict
    )
    property_domains: dict[str, tuple[str, ...]] = Field(
        default_factory=dict
    )
    property_ranges: dict[str, tuple[str, ...]] = Field(
        default_factory=dict
    )
    allowed_evidence_modes: tuple[EvidenceMode, ...]
    source_families_by_evidence_mode: dict[
        EvidenceMode,
        tuple[SourceFamily, ...],
    ]
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
        if not self.allowed_evidence_modes:
            raise ValueError("validation profile admits no evidence modes")
        if set(self.source_families_by_evidence_mode) != set(
            self.allowed_evidence_modes
        ):
            raise ValueError(
                "validation profile evidence modes and source policies disagree"
            )
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


def validate_fact_for_publication(
    fact: ValidatedFact,
    registry: ValidationProfileRegistry,
) -> None:
    """Require exact profile ownership and evidence before publication."""

    profile = registry.resolve(fact.validation_profile)
    if not fact.evidence_ref.strip():
        raise ValueError("new facts require a non-empty evidence_ref")
    if fact.evidence_mode not in profile.allowed_evidence_modes:
        raise ValueError(
            f"evidence mode is not admitted by owning profile: "
            f"{fact.evidence_mode}"
        )


def _file_checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _mapping_entry(
    entry: dict[str, object],
    *,
    kind: str | None = None,
) -> tuple[str, dict[str, str]]:
    if not all(isinstance(key, str) for key in entry):
        raise ValueError("malformed profile mapping entry")
    structural_fields = {"domain_iri_set", "range_iri_set", "aliases"}
    for field, value in entry.items():
        if field in structural_fields:
            if not isinstance(value, list) or not all(
                isinstance(item, str) and item for item in value
            ):
                raise ValueError("malformed profile mapping entry")
        elif field == "functional":
            if not isinstance(value, bool):
                raise ValueError("malformed profile mapping entry")
        elif not isinstance(value, str):
            raise ValueError("malformed profile mapping entry")
    name = entry.get("prefixed_name") or entry.get("local_name") or entry.get("iri")
    iri = entry.get("iri")
    if not isinstance(name, str) or not isinstance(iri, str):
        raise ValueError("malformed profile mapping entry")
    mapping: dict[str, str] = {"iri": iri}
    label = entry.get("label")
    if isinstance(label, str):
        mapping["label"] = label
    entry_kind = entry.get("kind")
    if isinstance(entry_kind, str):
        mapping["kind"] = entry_kind
    elif kind is not None:
        mapping["kind"] = kind
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
    class_mappings = _parse_mappings(raw_classes, "class")
    raw_properties = payload.get("property_mappings")
    if raw_properties is None:
        raw_object_properties = payload.get("object_properties", [])
        raw_datatype_properties = payload.get("datatype_properties", [])
        property_mappings = {
            **_parse_mappings(
                raw_object_properties,
                "property",
                list_kind="object",
            ),
            **_parse_mappings(
                raw_datatype_properties,
                "property",
                list_kind="datatype",
            ),
        }
        property_entries = [
            *raw_object_properties,
            *raw_datatype_properties,
        ]
    else:
        property_mappings = _parse_mappings(raw_properties, "property")
        # Keep the list entries when a profile supplies both mappings and
        # explicit domain/range metadata.  Dropping them silently turns a
        # seemingly constrained profile into a vocabulary-only profile.
        property_entries = raw_properties if isinstance(raw_properties, list) else []
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
    class_ancestors = _parse_class_ancestors(
        payload.get("class_ancestors"),
        class_mappings,
    )
    property_domains = _property_class_sets(
        property_entries,
        field="domain_iri_set",
    )
    property_ranges = _property_class_sets(
        property_entries,
        field="range_iri_set",
    )
    evidence_modes, source_policies = _profile_evidence_policy(layer)
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
        class_ancestors=class_ancestors,
        property_domains=property_domains,
        property_ranges=property_ranges,
        allowed_evidence_modes=evidence_modes,
        source_families_by_evidence_mode=source_policies,
        forbidden_predicates=tuple(forbidden),
        aggregation_procedure=procedure,
    )


def _parse_mappings(
    raw: object,
    kind: str,
    *,
    list_kind: str | None = None,
) -> dict[str, dict[str, str]]:
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
        return dict(
            _mapping_entry(entry, kind=list_kind)
            for entry in raw
        )
    raise ValueError(f"malformed {kind} mappings")


def _property_class_sets(
    entries: object,
    *,
    field: str,
) -> dict[str, tuple[str, ...]]:
    if not isinstance(entries, list):
        return {}
    result: dict[str, tuple[str, ...]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("iri"), str):
            continue
        values = entry.get(field, [])
        if isinstance(values, list) and all(
            isinstance(value, str) and value
            for value in values
        ):
            result[entry["iri"]] = tuple(values)
    return result


def _parse_class_ancestors(
    raw: object,
    class_mappings: dict[str, dict[str, str]],
) -> dict[str, tuple[str, ...]]:
    """Resolve a profile's explicit, closed class ancestry to exact IRIs."""

    names_by_iri = {
        mapping["iri"]: name
        for name, mapping in class_mappings.items()
        if isinstance(mapping.get("iri"), str) and mapping["iri"]
    }
    iris_by_name = {
        **{
            name: mapping["iri"]
            for name, mapping in class_mappings.items()
            if isinstance(mapping.get("iri"), str) and mapping["iri"]
        },
        **{iri: iri for iri in names_by_iri},
    }
    result = {iri: (iri,) for iri in names_by_iri}
    if raw is None:
        return result
    if not isinstance(raw, dict):
        raise ValueError("class_ancestors must be a class-to-ancestor mapping")
    for class_name, ancestor_names in raw.items():
        if not isinstance(class_name, str) or class_name not in iris_by_name:
            raise ValueError(f"unknown class ancestry subject: {class_name!r}")
        if not isinstance(ancestor_names, list) or not all(
            isinstance(name, str) and name for name in ancestor_names
        ):
            raise ValueError(f"malformed class ancestors: {class_name!r}")
        class_iri = iris_by_name[class_name]
        resolved = [class_iri]
        for ancestor_name in ancestor_names:
            ancestor_iri = iris_by_name.get(ancestor_name)
            if ancestor_iri is None:
                raise ValueError(f"unknown class ancestor: {ancestor_name!r}")
            if ancestor_iri not in resolved:
                resolved.append(ancestor_iri)
        result[class_iri] = tuple(resolved)
    return result


def _profile_evidence_policy(
    layer: ValidationLayer,
) -> tuple[
    tuple[EvidenceMode, ...],
    dict[EvidenceMode, tuple[SourceFamily, ...]],
]:
    if layer == "decision":
        families = (
            SourceFamily.ATCSCC_ADVISORY,
            SourceFamily.NASR_FACILITY,
            SourceFamily.FAA_TERM,
        )
        return ("source_text",), {"source_text": families}
    if layer == "weather":
        families = (SourceFamily.METAR, SourceFamily.TAF)
        return ("source_text",), {"source_text": families}
    if layer == "public_operational_observation":
        return (
            (
                "deterministic_derivation",
                "profile_definition",
            ),
            {
                "deterministic_derivation": (SourceFamily.BTS_ON_TIME,),
                "profile_definition": (),
            },
        )
    if layer == "flight_operation":
        families = (
            SourceFamily.NASA_ATMONTO_INSTANCE,
            SourceFamily.BTS_FLIGHT_OPERATION,
        )
        return ("source_text",), {"source_text": families}
    if layer == "aeronautical_reference":
        families = (
            SourceFamily.NASA_ATMONTO_INSTANCE,
            SourceFamily.NASR_AIRSPACE,
            SourceFamily.NASR_FACILITY,
            SourceFamily.FAA_AIRCRAFT_REGISTRY,
        )
        return ("source_text",), {"source_text": families}
    if layer == "trajectory":
        families = (
            SourceFamily.NASA_ATMONTO_INSTANCE,
            SourceFamily.NASR_AIRSPACE,
        )
        return ("source_text",), {"source_text": families}
    if layer == "atmonto_public_sample":
        # The public NASA bundle is already a canonical RDF/Turtle source.
        # This profile is intentionally source-text-only: it admits exact
        # ABox statements from the bundle, but never turns a derived table or
        # a model assertion into an ATMONTO fact.
        return (
            ("source_text",),
            {"source_text": (SourceFamily.NASA_ATMONTO_INSTANCE,)},
        )
    if layer == "document_reference":
        return (
            ("source_text",),
            {"source_text": (SourceFamily.WEB_DOCUMENT,)},
        )
    raise ValueError(f"unsupported validation layer: {layer}")


def _nasa_public_sample_profile() -> LoadedValidationProfile:
    """Build a full ATMONTO TBox profile for the public NASA ABox bundle.

    The regular runtime profiles are intentionally small application slices.
    The 2014 public sample is different: it is a multi-source RDF bundle that
    already contains Airport, Flight, route, track, weather, ASPM and TMI
    instances.  A dedicated runtime profile exposes the complete local TBox
    catalog to the deterministic ABox compiler while keeping the profile
    bounded to exact NASA source text.

    The sample contains a handful of source-local instance classes (for
    example ``METARreport`` and ``LatLonFix``) that are not TBox declarations.
    Adapters normalize those types to their ATMONTO superclass before they
    become formal facts; the original source type remains in the evidence
    anchor.
    """

    # Import lazily so the common TMI-only path does not parse all six OWL
    # modules during ordinary CLI startup.
    from aviation_agentic_ai.agent_system.ontology_coverage import (
        load_atmonto_catalog,
    )

    catalog = load_atmonto_catalog()
    all_classes = dict(catalog.classes)
    all_properties = {
        **catalog.object_properties,
        **catalog.datatype_properties,
    }
    forbidden = set(_FORBIDDEN_OPERATIONAL_OR_CAUSAL_PREDICATES)

    namespaces = {
        "atm": "https://data.nasa.gov/ontologies/atmonto/ATM#",
        "nas": "https://data.nasa.gov/ontologies/atmonto/NAS#",
        "data": "https://data.nasa.gov/ontologies/atmonto/data#",
        "eqp": "https://data.nasa.gov/ontologies/atmonto/equipment#",
        "gen": "https://data.nasa.gov/ontologies/atmonto/general#",
    }

    def prefixed(iri: str) -> str:
        for prefix, namespace in sorted(
            namespaces.items(), key=lambda item: len(item[1]), reverse=True
        ):
            if iri.startswith(namespace):
                return f"{prefix}:{iri[len(namespace):]}"
        return iri

    class_mappings = {
        prefixed(iri): {
            "iri": iri,
            "label": record.label,
            "kind": "class",
        }
        for iri, record in all_classes.items()
    }
    property_mappings = {
        prefixed(iri): {
            "iri": iri,
            "label": record.label,
            "kind": "object" if record.kind == "ObjectProperty" else "datatype",
        }
        for iri, record in all_properties.items()
        if iri not in forbidden
    }

    # Compute the transitive class closure.  The publication kernel accepts a
    # concrete source class for a range, then uses this closure to verify
    # superclass-based ATMONTO domains and ranges (Airport ->
    # NavigationElement -> TFMcontrolElement, for example).
    parents: dict[str, set[str]] = {iri: set() for iri in all_classes}
    for edge in catalog.class_hierarchy:
        parents.setdefault(edge.subclass_iri, set()).add(edge.superclass_iri)
    class_ancestors: dict[str, tuple[str, ...]] = {}
    for class_iri in sorted(all_classes):
        closure = {class_iri}
        frontier = [class_iri]
        while frontier:
            current = frontier.pop()
            for parent in sorted(parents.get(current, ())):
                if parent not in closure:
                    closure.add(parent)
                    frontier.append(parent)
        class_ancestors[class_iri] = tuple(sorted(closure))

    property_domains = {
        iri: record.domain_iris
        for iri, record in all_properties.items()
        if iri not in forbidden
    }
    property_ranges = {
        iri: record.range_iris
        for iri, record in catalog.object_properties.items()
        if iri not in forbidden
    }

    # The profile checksum binds the exact six local ontology modules and the
    # profile-construction policy.  It is not a user-provided or model-
    # provided value.
    payload = {
        "profile_id": "nasa_atmonto_public_sample_abox_v1",
        "module_paths": list(catalog.module_paths),
        "classes": sorted(all_classes),
        "properties": sorted(property_mappings),
        "forbidden": sorted(forbidden),
    }
    checksum = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    evidence_modes, source_policies = _profile_evidence_policy(
        "atmonto_public_sample"
    )
    return LoadedValidationProfile(
        ref=ValidationProfileRef(
            profile_id=payload["profile_id"],
            profile_checksum=checksum,
            layer="atmonto_public_sample",
        ),
        source_path="runtime:local-atmonto-tbox-catalog",
        namespace_prefixes=namespaces,
        class_mappings=class_mappings,
        property_mappings=property_mappings,
        class_ancestors=class_ancestors,
        property_domains=property_domains,
        property_ranges=property_ranges,
        allowed_evidence_modes=evidence_modes,
        source_families_by_evidence_mode=source_policies,
    )


def _decision_profile(decision_guide: SchemaGuide) -> LoadedValidationProfile:
    classes = {
        name: {"iri": item.iri, "label": item.label}
        for name, item in decision_guide.classes.items()
    }
    properties = {
        **{
            name: {"iri": item.iri, "label": item.label, "kind": "object"}
            for name, item in decision_guide.object_properties.items()
        },
        **{
            name: {"iri": item.iri, "label": item.label, "kind": "datatype"}
            for name, item in decision_guide.datatype_properties.items()
        },
    }
    class_ancestors = {
        item.iri: tuple(
            decision_guide.classes[ancestor].iri
            for ancestor in sorted(decision_guide.superclasses(name))
            if ancestor in decision_guide.classes
        )
        for name, item in decision_guide.classes.items()
    }
    property_domains = {
        item.iri: tuple(
            decision_guide.classes[domain].iri
            for domain in sorted(item.domain)
            if domain in decision_guide.classes
        )
        for item in {
            **decision_guide.object_properties,
            **decision_guide.datatype_properties,
        }.values()
    }
    property_ranges = {
        item.iri: tuple(
            decision_guide.classes[range_class].iri
            for range_class in sorted(item.range)
            if range_class in decision_guide.classes
        )
        for item in decision_guide.object_properties.values()
    }
    evidence_modes, source_policies = _profile_evidence_policy("decision")
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
        class_ancestors=class_ancestors,
        property_domains=property_domains,
        property_ranges=property_ranges,
        allowed_evidence_modes=evidence_modes,
        source_families_by_evidence_mode=source_policies,
    )


def load_validation_profile_registry(
    *,
    decision_guide: SchemaGuide,
    weather_profile_path: str | Path = DEFAULT_WEATHER_PROFILE_PATH,
    public_observation_profile_path: str | Path = DEFAULT_PUBLIC_OBSERVATION_PROFILE_PATH,
    include_flight_airspace: bool = False,
    flight_operation_profile_path: str | Path = DEFAULT_FLIGHT_OPERATION_PROFILE_PATH,
    aeronautical_reference_profile_path: str | Path = DEFAULT_AERONAUTICAL_REFERENCE_PROFILE_PATH,
    trajectory_profile_path: str | Path = DEFAULT_TRAJECTORY_PROFILE_PATH,
    include_atmonto_public_sample: bool = False,
    include_faa_order: bool = False,
    faa_order_profile_path: str | Path = DEFAULT_FAA_ORDER_ONTOLOGY_PROFILE_PATH,
) -> ValidationProfileRegistry:
    """Load checksum-pinned profiles, optionally adding Flight/Airspace layers."""

    weather_path = resolve_project_path(weather_profile_path)
    observation_path = resolve_project_path(public_observation_profile_path)
    profiles = [
        _decision_profile(decision_guide),
        _load_json_profile(weather_path, "weather"),
        _load_json_profile(observation_path, "public_operational_observation"),
    ]
    if include_flight_airspace:
        profiles.extend(
            (
                _load_json_profile(
                    resolve_project_path(flight_operation_profile_path),
                    "flight_operation",
                ),
                _load_json_profile(
                    resolve_project_path(aeronautical_reference_profile_path),
                    "aeronautical_reference",
                ),
                _load_json_profile(
                    resolve_project_path(trajectory_profile_path),
                    "trajectory",
                ),
            )
        )
    if include_atmonto_public_sample:
        profiles.append(_nasa_public_sample_profile())
    if include_faa_order:
        profiles.append(
            _load_json_profile(
                resolve_project_path(faa_order_profile_path),
                "document_reference",
            )
        )
    return ValidationProfileRegistry(profiles=tuple(profiles))


__all__ = [
    "AggregationProcedureDescriptor",
    "DEFAULT_AERONAUTICAL_REFERENCE_PROFILE_PATH",
    "DEFAULT_FLIGHT_OPERATION_PROFILE_PATH",
    "DEFAULT_PUBLIC_OBSERVATION_PROFILE_PATH",
    "DEFAULT_TRAJECTORY_PROFILE_PATH",
    "DEFAULT_FAA_ORDER_ONTOLOGY_PROFILE_PATH",
    "DEFAULT_WEATHER_PROFILE_PATH",
    "LoadedValidationProfile",
    "ValidationProfileRef",
    "ValidationProfileRegistry",
    "load_validation_profile_registry",
    "validate_fact_for_publication",
]
