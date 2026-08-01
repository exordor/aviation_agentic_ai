"""Versioned ATMONTO registry and deterministic task-level ontology slices.

The registry is the complete local ATMONTO semantic authority.  A generation
task receives a small, deterministic slice containing the subject class,
its ancestors, selected property signatures, endpoint classes, and applicable
constraints.  The slice is a prompt/runtime context; it is not a new ontology
and it never creates ABox facts.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from pydantic import Field, model_validator

from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.agent_system.ontology_coverage import (
    AtmontoCatalog,
    CardinalityConstraint,
    OntologyClass,
    OntologyProperty,
    load_atmonto_catalog,
)
from aviation_agentic_ai.paths import PROJECT_ROOT


class OntologySliceRequest(StrictModel):
    """Closed request for the ontology context of one generation task."""

    subject_class_iri: str = Field(min_length=1)
    candidate_property_iris: tuple[str, ...] = ()
    candidate_object_class_iris: tuple[str, ...] = ()
    include_ancestors: bool = True
    include_domain_range_neighbors: bool = True
    profile_id: str | None = None
    profile_checksum: str | None = Field(default=None, min_length=64, max_length=64)

    @model_validator(mode="after")
    def _validate_profile_checksum(self) -> OntologySliceRequest:
        if self.profile_checksum is not None and self.profile_id is None:
            raise ValueError("profile checksum requires profile id")
        return self


class OntologyClassRef(StrictModel):
    iri: str = Field(min_length=1)
    local_name: str = Field(min_length=1)
    label: str = Field(min_length=1)
    comment: str = ""
    source_modules: tuple[str, ...] = ()


class OntologyPropertyRef(StrictModel):
    iri: str = Field(min_length=1)
    local_name: str = Field(min_length=1)
    kind: str = Field(pattern=r"^(ObjectProperty|DataProperty)$")
    label: str = Field(min_length=1)
    comment: str = ""
    domain_iris: tuple[str, ...] = ()
    range_iris: tuple[str, ...] = ()
    datatype_iris: tuple[str, ...] = ()
    functional: bool = False


class OntologyHierarchyRef(StrictModel):
    subclass_iri: str = Field(min_length=1)
    superclass_iri: str = Field(min_length=1)


class OntologyConstraintRef(StrictModel):
    class_iri: str = Field(min_length=1)
    property_iri: str = Field(min_length=1)
    constraint_type: str = Field(min_length=1)
    cardinality: int
    value_iris: tuple[str, ...] = ()
    datatype_iris: tuple[str, ...] = ()


class OntologySlice(StrictModel):
    """Deterministic, task-sized view over the complete ontology registry."""

    ontology_version: str = Field(min_length=1)
    catalog_checksum: str = Field(min_length=64, max_length=64)
    subject_class_iri: str = Field(min_length=1)
    profile_id: str | None = None
    profile_checksum: str | None = Field(default=None, min_length=64, max_length=64)
    classes: tuple[OntologyClassRef, ...] = ()
    properties: tuple[OntologyPropertyRef, ...] = ()
    hierarchy: tuple[OntologyHierarchyRef, ...] = ()
    constraints: tuple[OntologyConstraintRef, ...] = ()


@dataclass(frozen=True)
class OntologyRegistry:
    """Complete ATMONTO catalog plus its content-derived identity."""

    catalog: AtmontoCatalog
    catalog_checksum: str
    ontology_version: str


def _content_checksum(root: Path, catalog: AtmontoCatalog) -> str:
    digest = hashlib.sha256()
    for relative in catalog.module_paths:
        path = root / relative
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def load_ontology_registry(
    repo_root: str | Path = PROJECT_ROOT,
) -> OntologyRegistry:
    """Load the complete pinned local ATMONTO catalog without remote imports."""

    root = Path(repo_root)
    catalog = load_atmonto_catalog(root)
    checksum = _content_checksum(root, catalog)
    return OntologyRegistry(
        catalog=catalog,
        catalog_checksum=checksum,
        ontology_version=f"atmonto-local-{checksum[:16]}",
    )


def _ancestor_map(catalog: AtmontoCatalog) -> dict[str, set[str]]:
    parents: dict[str, set[str]] = {}
    for edge in catalog.class_hierarchy:
        parents.setdefault(edge.subclass_iri, set()).add(edge.superclass_iri)
    return parents


def _closure(
    seeds: set[str],
    parents: dict[str, set[str]],
    *,
    include_ancestors: bool,
) -> set[str]:
    if not include_ancestors:
        return set(seeds)
    selected = set(seeds)
    stack = list(seeds)
    while stack:
        current = stack.pop()
        for parent in parents.get(current, set()):
            if parent not in selected:
                selected.add(parent)
                stack.append(parent)
    return selected


def _class_ref(record: OntologyClass) -> OntologyClassRef:
    return OntologyClassRef(
        iri=record.iri,
        local_name=record.local_name,
        label=record.label,
        comment=record.comment,
        source_modules=record.source_modules,
    )


def _property_ref(record: OntologyProperty) -> OntologyPropertyRef:
    return OntologyPropertyRef(
        iri=record.iri,
        local_name=record.local_name,
        kind=record.kind,
        label=record.label,
        comment=record.comment,
        domain_iris=record.domain_iris,
        range_iris=record.range_iris,
        datatype_iris=record.datatype_iris,
        functional=record.functional,
    )


def _constraint_ref(record: CardinalityConstraint) -> OntologyConstraintRef:
    return OntologyConstraintRef(
        class_iri=record.class_iri,
        property_iri=record.property_iri,
        constraint_type=record.constraint_type,
        cardinality=record.cardinality,
        value_iris=record.value_iris,
        datatype_iris=record.datatype_iris,
    )


def build_ontology_slice(
    registry: OntologyRegistry,
    request: OntologySliceRequest,
) -> OntologySlice:
    """Build a stable task slice and reject every unknown ontology term."""

    catalog = registry.catalog
    if request.subject_class_iri not in catalog.classes:
        raise ValueError(f"unknown ontology class: {request.subject_class_iri}")

    property_records: dict[str, OntologyProperty] = {
        **catalog.object_properties,
        **catalog.datatype_properties,
    }
    for property_iri in request.candidate_property_iris:
        if property_iri not in property_records:
            raise ValueError(f"unknown ontology property: {property_iri}")
    for class_iri in request.candidate_object_class_iris:
        if class_iri not in catalog.classes:
            raise ValueError(f"unknown ontology class: {class_iri}")

    parents = _ancestor_map(catalog)
    selected_class_iris = _closure(
        {request.subject_class_iri, *request.candidate_object_class_iris},
        parents,
        include_ancestors=request.include_ancestors,
    )
    selected_property_iris = set(request.candidate_property_iris)

    if not selected_property_iris:
        subject_closure = _closure(
            {request.subject_class_iri},
            parents,
            include_ancestors=True,
        )
        selected_property_iris.update(
            record.iri
            for record in property_records.values()
            if not record.domain_iris
            or bool(set(record.domain_iris) & subject_closure)
        )

    if request.include_domain_range_neighbors:
        for property_iri in selected_property_iris:
            record = property_records[property_iri]
            selected_class_iris.update(record.domain_iris)
            selected_class_iris.update(record.range_iris)
        selected_class_iris = _closure(
            selected_class_iris,
            parents,
            include_ancestors=request.include_ancestors,
        )

    selected_class_iris.intersection_update(catalog.classes)
    selected_property_iris.intersection_update(property_records)

    classes = tuple(
        _class_ref(catalog.classes[iri])
        for iri in sorted(selected_class_iris)
    )
    properties = tuple(
        _property_ref(property_records[iri])
        for iri in sorted(selected_property_iris)
    )
    hierarchy = tuple(
        OntologyHierarchyRef(
            subclass_iri=edge.subclass_iri,
            superclass_iri=edge.superclass_iri,
        )
        for edge in catalog.class_hierarchy
        if edge.subclass_iri in selected_class_iris
        and edge.superclass_iri in selected_class_iris
    )
    constraints = tuple(
        _constraint_ref(constraint)
        for constraint in catalog.cardinality_constraints
        if constraint.class_iri in selected_class_iris
        and constraint.property_iri in selected_property_iris
    )

    return OntologySlice(
        ontology_version=registry.ontology_version,
        catalog_checksum=registry.catalog_checksum,
        subject_class_iri=request.subject_class_iri,
        profile_id=request.profile_id,
        profile_checksum=request.profile_checksum,
        classes=classes,
        properties=properties,
        hierarchy=hierarchy,
        constraints=constraints,
    )


__all__ = [
    "OntologyClassRef",
    "OntologyConstraintRef",
    "OntologyHierarchyRef",
    "OntologyPropertyRef",
    "OntologyRegistry",
    "OntologySlice",
    "OntologySliceRequest",
    "build_ontology_slice",
    "load_ontology_registry",
]
