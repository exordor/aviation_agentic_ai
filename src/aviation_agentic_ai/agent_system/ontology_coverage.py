"""Deterministic ATMONTO semantic catalog and profile coverage report.

The active runtime deliberately uses small curated application profiles.  This
module keeps that runtime boundary while exposing the broader ATMONTO semantic
surface needed to measure whether the KG is a real ontology-grounded graph
rather than a collection of relational-looking event fields.

The six local NASA OWL/XML files are treated as read-only semantic authority.
No remote imports are followed, no facts are created, and no OWL inference is
performed.  The output is an inventory of declarations, signatures,
hierarchy axioms, cardinality restrictions, and profile coverage status.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Iterable
from xml.etree import ElementTree as ET

from aviation_agentic_ai.agent_system.semantic_paths import (
    ATMONTO_REFERENCE_MODULE_DIR,
    ATMONTO_REFERENCE_MODULES,
)
from aviation_agentic_ai.paths import PROJECT_ROOT


OWL_NS = "http://www.w3.org/2002/07/owl#"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS_NS = "http://www.w3.org/2000/01/rdf-schema#"
ATMONTO_NAMESPACE_ROOT = "https://data.nasa.gov/ontologies/atmonto/"

ATMONTO_DOMAINS = (
    "airspace_structures_facilities",
    "navigation_routes_fixes",
    "traffic_management_initiatives",
    "flight_carrier_aircraft",
    "airport_surface_operations",
    "weather",
    "sequences",
    "temporal_spatial",
)
UNASSIGNED_DOMAIN = "unassigned"
_DOMAIN_NAMES = frozenset((*ATMONTO_DOMAINS, UNASSIGNED_DOMAIN))

# These are deliberately small, explicit next-scope candidates.  They make
# the coverage report useful for planning without pretending that every term
# in the upstream ontology is already supported by a source adapter.
PLANNED_ATMONTO_TERMS = frozenset(
    {
        "https://data.nasa.gov/ontologies/atmonto/ATM#AbsoluteFix",
        "https://data.nasa.gov/ontologies/atmonto/ATM#FlightPlanSegment",
        "https://data.nasa.gov/ontologies/atmonto/ATM#MilesInTrailTMI",
        "https://data.nasa.gov/ontologies/atmonto/ATM#PlannedFlightRoute",
        "https://data.nasa.gov/ontologies/atmonto/ATM#aircraftTypeFlown",
        "https://data.nasa.gov/ontologies/atmonto/ATM#arrivalRunway",
        "https://data.nasa.gov/ontologies/atmonto/ATM#departureRunway",
        "https://data.nasa.gov/ontologies/atmonto/ATM#hasPlannedRoute",
        "https://data.nasa.gov/ontologies/atmonto/NAS#OperationalRunway",
        "https://data.nasa.gov/ontologies/atmonto/NAS#PhysicalRunway",
        "https://data.nasa.gov/ontologies/atmonto/NAS#TRACON",
        "https://data.nasa.gov/ontologies/atmonto/NAS#hasRunway",
        "https://data.nasa.gov/ontologies/atmonto/data#SurfaceWindCondition",
        "https://data.nasa.gov/ontologies/atmonto/data#VisibilityCondition",
        "https://data.nasa.gov/ontologies/atmonto/data#hasWeatherCondition",
        "https://data.nasa.gov/ontologies/atmonto/equipment#AircraftType",
        "https://data.nasa.gov/ontologies/atmonto/equipment#manufacturedBy",
        "https://data.nasa.gov/ontologies/atmonto/general#PointLocation",
        "https://data.nasa.gov/ontologies/atmonto/general#centerpoint",
    }
)

_DECLARATION_KINDS = frozenset({"Class", "ObjectProperty", "DataProperty"})
_PROPERTY_KINDS = frozenset({"ObjectProperty", "DataProperty"})
_CARDINALITY_RE = re.compile(r"(?:Exact|Min|Max)Cardinality$")


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _tag(name: str) -> str:
    return f"{{{OWL_NS}}}{name}"


@dataclass(frozen=True)
class OntologyClass:
    iri: str
    local_name: str
    label: str
    comment: str
    source_modules: tuple[str, ...]


@dataclass(frozen=True)
class OntologyProperty:
    iri: str
    local_name: str
    kind: str
    label: str
    comment: str
    source_modules: tuple[str, ...]
    domain_iris: tuple[str, ...]
    range_iris: tuple[str, ...]
    datatype_iris: tuple[str, ...]
    functional: bool


@dataclass(frozen=True)
class ClassHierarchyEdge:
    subclass_iri: str
    superclass_iri: str
    source_module: str


@dataclass(frozen=True)
class CardinalityConstraint:
    class_iri: str
    property_iri: str
    constraint_type: str
    cardinality: int
    value_iris: tuple[str, ...]
    datatype_iris: tuple[str, ...]
    source_module: str


@dataclass(frozen=True)
class AtmontoCatalog:
    module_paths: tuple[str, ...]
    classes: dict[str, OntologyClass]
    object_properties: dict[str, OntologyProperty]
    datatype_properties: dict[str, OntologyProperty]
    class_hierarchy: tuple[ClassHierarchyEdge, ...]
    cardinality_constraints: tuple[CardinalityConstraint, ...]


@dataclass
class _MutableProperty:
    iri: str
    local_name: str
    kind: str
    label: str = ""
    comment: str = ""
    source_modules: set[str] | None = None
    domain_iris: set[str] | None = None
    range_iris: set[str] | None = None
    datatype_iris: set[str] | None = None
    functional: bool = False

    def __post_init__(self) -> None:
        self.source_modules = set() if self.source_modules is None else self.source_modules
        self.domain_iris = set() if self.domain_iris is None else self.domain_iris
        self.range_iris = set() if self.range_iris is None else self.range_iris
        self.datatype_iris = set() if self.datatype_iris is None else self.datatype_iris


@dataclass
class _MutableClass:
    iri: str
    local_name: str
    label: str = ""
    comment: str = ""
    source_modules: set[str] | None = None

    def __post_init__(self) -> None:
        self.source_modules = set() if self.source_modules is None else self.source_modules


def _expand(value: str | None, prefixes: dict[str, str], default_base: str) -> str:
    if not value:
        return ""
    if value.startswith("#"):
        return f"{default_base}#{value[1:]}"
    if value.startswith(("http://", "https://", "urn:")):
        return value
    if ":" in value:
        prefix, local = value.split(":", 1)
        if prefix in prefixes:
            return prefixes[prefix] + local
    return value


def _node_iri(node: ET.Element, prefixes: dict[str, str], default_base: str) -> str:
    return _expand(
        node.attrib.get("IRI")
        or node.attrib.get("abbreviatedIRI")
        or node.attrib.get(f"{{{RDF_NS}}}resource"),
        prefixes,
        default_base,
    )


def _is_atmonto_term(iri: str) -> bool:
    """Keep NASA terms and exclude the legacy Icarus bridge vocabulary."""

    return iri.startswith(ATMONTO_NAMESPACE_ROOT)


def _direct_child_iri(
    node: ET.Element,
    prefixes: dict[str, str],
    default_base: str,
    *allowed_tags: str,
) -> str:
    allowed = set(allowed_tags)
    for child in list(node):
        if _local(child.tag) in allowed:
            return _node_iri(child, prefixes, default_base)
    return ""


def _nested_iris(
    node: ET.Element,
    prefixes: dict[str, str],
    default_base: str,
    allowed_tags: frozenset[str],
) -> tuple[str, ...]:
    values = {
        _node_iri(child, prefixes, default_base)
        for child in node.iter()
        if _local(child.tag) in allowed_tags
    }
    return tuple(sorted(value for value in values if value))


def _annotation_values(
    root: ET.Element,
    prefixes: dict[str, str],
    default_base: str,
) -> dict[str, dict[str, str]]:
    values: dict[str, dict[str, str]] = defaultdict(dict)
    for assertion in root.iter(_tag("AnnotationAssertion")):
        children = list(assertion)
        if len(children) < 3:
            continue
        predicate = _expand(
            children[0].attrib.get("abbreviatedIRI")
            or children[0].attrib.get("IRI"),
            prefixes,
            default_base,
        )
        subject = _node_iri(children[1], prefixes, default_base)
        literal = children[2].text or ""
        if subject and predicate in {
            f"{RDFS_NS}label",
            f"{RDFS_NS}comment",
        }:
            values[subject][_local(predicate)] = " ".join(literal.split())
    return values


def _module_prefixes(root: ET.Element) -> tuple[dict[str, str], str]:
    prefixes = {
        element.attrib.get("name", ""): element.attrib.get("IRI", "")
        for element in root.iter(_tag("Prefix"))
    }
    ontology_iri = root.attrib.get("ontologyIRI") or prefixes.get("") or ""
    if ontology_iri.endswith("#"):
        ontology_iri = ontology_iri[:-1]
    return prefixes, ontology_iri


def _read_module(path: Path, module_name: str) -> tuple[
    dict[str, _MutableClass],
    dict[str, _MutableProperty],
    list[ClassHierarchyEdge],
    list[CardinalityConstraint],
]:
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        raise ValueError(f"cannot parse ATMONTO module {path}: {exc}") from exc

    prefixes, default_base = _module_prefixes(root)
    annotations = _annotation_values(root, prefixes, default_base)
    classes: dict[str, _MutableClass] = {}
    properties: dict[str, _MutableProperty] = {}

    for declaration in root.iter(_tag("Declaration")):
        child = next(iter(declaration), None)
        if child is None or _local(child.tag) not in _DECLARATION_KINDS:
            continue
        iri = _node_iri(child, prefixes, default_base)
        if not iri or not _is_atmonto_term(iri):
            continue
        kind = _local(child.tag)
        if kind == "Class":
            record = classes.setdefault(iri, _MutableClass(iri, iri.rsplit("#", 1)[-1]))
        else:
            record = properties.setdefault(
                iri,
                _MutableProperty(iri, iri.rsplit("#", 1)[-1], kind),
            )
        record.source_modules.add(module_name)
        for key, value in annotations.get(iri, {}).items():
            if key == "label":
                record.label = value
            elif key == "comment":
                record.comment = value

    hierarchy: list[ClassHierarchyEdge] = []
    constraints: list[CardinalityConstraint] = []
    for axiom in root.iter(_tag("SubClassOf")):
        direct_classes = [
            _node_iri(child, prefixes, default_base)
            for child in list(axiom)
            if _local(child.tag) == "Class"
        ]
        if (
            len(direct_classes) >= 2
            and _is_atmonto_term(direct_classes[0])
            and _is_atmonto_term(direct_classes[1])
        ):
            hierarchy.append(
                ClassHierarchyEdge(
                    direct_classes[0], direct_classes[1], module_name
                )
            )
        if not direct_classes:
            continue
        subject_iri = direct_classes[0]
        if not _is_atmonto_term(subject_iri):
            continue
        for restriction in axiom.iter():
            restriction_kind = _local(restriction.tag)
            if not _CARDINALITY_RE.search(restriction_kind):
                continue
            raw_cardinality = restriction.attrib.get("cardinality")
            if raw_cardinality is None:
                continue
            try:
                cardinality = int(raw_cardinality)
            except ValueError as exc:
                raise ValueError(
                    f"invalid cardinality in {module_name}: {raw_cardinality}"
                ) from exc
            property_iri = _direct_child_iri(
                restriction,
                prefixes,
                default_base,
                "ObjectProperty",
                "DataProperty",
            )
            if not property_iri or not _is_atmonto_term(property_iri):
                continue
            constraints.append(
                CardinalityConstraint(
                    class_iri=subject_iri,
                    property_iri=property_iri,
                    constraint_type=restriction_kind,
                    cardinality=cardinality,
                    value_iris=_nested_iris(
                        restriction,
                        prefixes,
                        default_base,
                        frozenset({"Class"}),
                    ),
                    datatype_iris=_nested_iris(
                        restriction,
                        prefixes,
                        default_base,
                        frozenset({"Datatype"}),
                    ),
                    source_module=module_name,
                )
            )

    for declaration in root.iter(_tag("ObjectPropertyDomain")):
        property_iri = _direct_child_iri(
            declaration, prefixes, default_base, "ObjectProperty"
        )
        domains = _nested_iris(
            declaration,
            prefixes,
            default_base,
            frozenset({"Class"}),
        )
        if property_iri in properties:
            properties[property_iri].domain_iris.update(domains)
    for declaration in root.iter(_tag("ObjectPropertyRange")):
        property_iri = _direct_child_iri(
            declaration, prefixes, default_base, "ObjectProperty"
        )
        ranges = _nested_iris(
            declaration,
            prefixes,
            default_base,
            frozenset({"Class"}),
        )
        if property_iri in properties:
            properties[property_iri].range_iris.update(ranges)
    for declaration in root.iter(_tag("DataPropertyDomain")):
        property_iri = _direct_child_iri(
            declaration, prefixes, default_base, "DataProperty"
        )
        domains = _nested_iris(
            declaration,
            prefixes,
            default_base,
            frozenset({"Class"}),
        )
        if property_iri in properties:
            properties[property_iri].domain_iris.update(domains)
    for declaration in root.iter(_tag("DataPropertyRange")):
        property_iri = _direct_child_iri(
            declaration, prefixes, default_base, "DataProperty"
        )
        datatypes = _nested_iris(
            declaration,
            prefixes,
            default_base,
            frozenset({"Datatype", "IRI"}),
        )
        if property_iri in properties:
            properties[property_iri].datatype_iris.update(datatypes)

    for predicate in (
        "FunctionalObjectProperty",
        "FunctionalDataProperty",
    ):
        for declaration in root.iter(_tag(predicate)):
            property_iri = _direct_child_iri(
                declaration,
                prefixes,
                default_base,
                "ObjectProperty",
                "DataProperty",
            )
            if property_iri in properties:
                properties[property_iri].functional = True

    return classes, properties, hierarchy, constraints


def load_atmonto_catalog(repo_root: str | Path = PROJECT_ROOT) -> AtmontoCatalog:
    """Load the six pinned local ATMONTO modules without following imports."""

    root = Path(repo_root)
    all_classes: dict[str, _MutableClass] = {}
    all_properties: dict[str, _MutableProperty] = {}
    hierarchy: set[ClassHierarchyEdge] = set()
    constraints: set[CardinalityConstraint] = set()
    module_paths: list[str] = []
    for module_name in ATMONTO_REFERENCE_MODULES:
        relative = ATMONTO_REFERENCE_MODULE_DIR / module_name
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(f"missing ATMONTO reference module: {relative}")
        module_paths.append(relative.as_posix())
        classes, properties, edges, restrictions = _read_module(path, module_name)
        for iri, record in classes.items():
            current = all_classes.setdefault(iri, record)
            current.label = current.label or record.label
            current.comment = current.comment or record.comment
            current.source_modules.update(record.source_modules)
        for iri, record in properties.items():
            current = all_properties.setdefault(iri, record)
            current.label = current.label or record.label
            current.comment = current.comment or record.comment
            current.source_modules.update(record.source_modules)
            current.domain_iris.update(record.domain_iris)
            current.range_iris.update(record.range_iris)
            current.datatype_iris.update(record.datatype_iris)
            current.functional = current.functional or record.functional
        hierarchy.update(edges)
        constraints.update(restrictions)

    def freeze_class(record: _MutableClass) -> OntologyClass:
        return OntologyClass(
            iri=record.iri,
            local_name=record.local_name,
            label=record.label or record.local_name,
            comment=record.comment,
            source_modules=tuple(sorted(record.source_modules)),
        )

    def freeze_property(record: _MutableProperty) -> OntologyProperty:
        return OntologyProperty(
            iri=record.iri,
            local_name=record.local_name,
            kind=record.kind,
            label=record.label or record.local_name,
            comment=record.comment,
            source_modules=tuple(sorted(record.source_modules)),
            domain_iris=tuple(sorted(record.domain_iris)),
            range_iris=tuple(sorted(record.range_iris)),
            datatype_iris=tuple(sorted(record.datatype_iris)),
            functional=record.functional,
        )

    classes = {iri: freeze_class(record) for iri, record in sorted(all_classes.items())}
    properties = {
        iri: freeze_property(record)
        for iri, record in sorted(all_properties.items())
    }
    return AtmontoCatalog(
        module_paths=tuple(module_paths),
        classes=classes,
        object_properties={
            iri: record
            for iri, record in properties.items()
            if record.kind == "ObjectProperty"
        },
        datatype_properties={
            iri: record
            for iri, record in properties.items()
            if record.kind == "DataProperty"
        },
        class_hierarchy=tuple(
            sorted(
                hierarchy,
                key=lambda edge: (
                    edge.subclass_iri,
                    edge.superclass_iri,
                    edge.source_module,
                ),
            )
        ),
        cardinality_constraints=tuple(
            sorted(
                constraints,
                key=lambda constraint: (
                    constraint.class_iri,
                    constraint.property_iri,
                    constraint.constraint_type,
                    constraint.cardinality,
                    constraint.source_module,
                ),
            )
        ),
    )


def _domain_labels(local_name: str, source_modules: Iterable[str]) -> tuple[str, ...]:
    name = local_name.lower()
    sources = set(source_modules)
    domains: set[str] = set()

    if "general.owl" in sources or any(
        token in name
        for token in ("time", "date", "interval", "location", "position", "geometry")
    ):
        domains.add("temporal_spatial")
    if "general.owl" in sources or any(
        token in name
        for token in ("sequence", "subsequence", "sequenced", "list", "ordered")
    ):
        domains.add("sequences")
    if "data.owl" in sources or any(
        token in name
        for token in (
            "weather",
            "metar",
            "taf",
            "wind",
            "visibility",
            "ceiling",
            "precipitation",
            "temperature",
            "pressure",
            "cloud",
        )
    ):
        domains.add("weather")
    if "equipment.owl" in sources or any(
        token in name
        for token in ("flight", "aircraft", "carrier", "airline", "manufacturer")
    ):
        domains.add("flight_carrier_aircraft")
    if any(
        token in name
        for token in ("tmi", "traffic", "delay", "groundstop", "reroute", "flowprogram")
    ):
        domains.add("traffic_management_initiatives")
    if any(
        token in name
        for token in (
            "route",
            "fix",
            "waypoint",
            "airway",
            "procedure",
            "navigation",
        )
    ):
        domains.add("navigation_routes_fixes")
    if "NAS.owl" in sources:
        if any(
            token in name
            for token in ("airport", "runway", "taxi", "terminal", "deicing", "surface")
        ):
            domains.add("airport_surface_operations")
        else:
            domains.add("airspace_structures_facilities")
    if not domains:
        domains.add(UNASSIGNED_DOMAIN)
    return tuple(sorted(domains, key=lambda value: (value == UNASSIGNED_DOMAIN, value)))


def _profile_terms(repo_root: Path) -> tuple[set[str], set[str]]:
    curated = repo_root / "data/ontology/curated"
    active: set[str] = set()
    planned: set[str] = set()
    for path in sorted(curated.glob("*.json")):
        if path.name == "atmonto_semantic_coverage_v1.json":
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for key in ("classes", "object_properties", "datatype_properties"):
            for row in payload.get(key, []):
                if isinstance(row, dict) and row.get("iri"):
                    active.add(str(row["iri"]))
        for key in ("class_mappings", "property_mappings"):
            mappings = payload.get(key, {})
            if isinstance(mappings, dict):
                mapping_rows = mappings.values()
            elif isinstance(mappings, list):
                mapping_rows = mappings
            else:
                mapping_rows = ()
            for row in mapping_rows:
                if isinstance(row, dict) and row.get("iri"):
                    active.add(str(row["iri"]))
        for key in ("active_event_profiles",):
            for row in payload.get(key, []):
                if row.get("ontology_class"):
                    active.add(str(row["ontology_class"]))
                active.update(str(value) for value in row.get("field_mappings", {}).values())
        for key in ("deferred_event_profiles", "boundary_event_profiles"):
            for row in payload.get(key, []):
                if row.get("ontology_class"):
                    planned.add(str(row["ontology_class"]))
                planned.update(str(value) for value in row.get("field_mappings", {}).values())
    planned.difference_update(active)
    return active, planned


def _term_rows(catalog: AtmontoCatalog, repo_root: Path) -> list[dict[str, object]]:
    active, planned = _profile_terms(repo_root)
    planned.update(PLANNED_ATMONTO_TERMS)
    rows: list[dict[str, object]] = []
    for kind, records in (
        ("class", catalog.classes.values()),
        ("object_property", catalog.object_properties.values()),
        ("datatype_property", catalog.datatype_properties.values()),
    ):
        for record in records:
            if record.iri in active:
                status = "active"
            elif record.iri in planned:
                status = "planned"
            else:
                status = "unsupported"
            rows.append(
                {
                    "iri": record.iri,
                    "local_name": record.local_name,
                    "kind": kind,
                    "label": record.label,
                    "source_modules": list(record.source_modules),
                    "domains": list(
                        _domain_labels(record.local_name, record.source_modules)
                    ),
                    "status": status,
                }
            )
    return sorted(rows, key=lambda row: (str(row["kind"]), str(row["iri"])))


def build_atmonto_semantic_coverage(
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, object]:
    """Build a deterministic eight-domain ATMONTO/profile coverage report."""

    root = Path(repo_root)
    catalog = load_atmonto_catalog(root)
    terms = _term_rows(catalog, root)
    status_counts = defaultdict(int)
    domain_summary: dict[str, dict[str, int]] = {
        domain: {"class": 0, "object_property": 0, "datatype_property": 0}
        for domain in ATMONTO_DOMAINS
    }
    domain_summary[UNASSIGNED_DOMAIN] = {
        "class": 0,
        "object_property": 0,
        "datatype_property": 0,
    }
    for row in terms:
        status_counts[str(row["status"])] += 1
        for domain in row["domains"]:
            domain_summary[str(domain)][str(row["kind"])] += 1

    property_rows = []
    for record in (
        *catalog.object_properties.values(),
        *catalog.datatype_properties.values(),
    ):
        property_rows.append(
            {
                "iri": record.iri,
                "local_name": record.local_name,
                "kind": record.kind,
                "label": record.label,
                "comment": record.comment,
                "source_modules": list(record.source_modules),
                "domain_iris": list(record.domain_iris),
                "range_iris": list(record.range_iris),
                "datatype_iris": list(record.datatype_iris),
                "functional": record.functional,
            }
        )

    return {
        "report_version": "atmonto-semantic-coverage-v1",
        "domains": list(ATMONTO_DOMAINS),
        "catalog": {
            "module_count": len(catalog.module_paths),
            "module_paths": list(catalog.module_paths),
            "class_count": len(catalog.classes),
            "object_property_count": len(catalog.object_properties),
            "datatype_property_count": len(catalog.datatype_properties),
            "hierarchy_axiom_count": len(catalog.class_hierarchy),
            "domain_range_signature_count": sum(
                bool(record.domain_iris or record.range_iris or record.datatype_iris)
                for record in (*catalog.object_properties.values(), *catalog.datatype_properties.values())
            ),
            "cardinality_constraint_count": len(catalog.cardinality_constraints),
        },
        "domain_summary": {
            key: value
            for key, value in sorted(domain_summary.items())
            if key != UNASSIGNED_DOMAIN
        },
        "coverage": {
            "active_term_count": status_counts["active"],
            "planned_term_count": status_counts["planned"],
            "unsupported_term_count": status_counts["unsupported"],
            "statuses": ["active", "planned", "unsupported"],
            "planned_term_boundary": (
                "Explicit next-scope ATMONTO terms retained in the semantic "
                "control plane; planned terms are not runtime-admitted facts."
            ),
        },
        "terms": terms,
        "properties": sorted(property_rows, key=lambda row: str(row["iri"])),
        "class_hierarchy": [
            {
                "subclass_iri": edge.subclass_iri,
                "superclass_iri": edge.superclass_iri,
                "source_module": edge.source_module,
            }
            for edge in catalog.class_hierarchy
        ],
        "cardinality_constraints": [
            {
                "class_iri": constraint.class_iri,
                "property_iri": constraint.property_iri,
                "constraint_type": constraint.constraint_type,
                "cardinality": constraint.cardinality,
                "value_iris": list(constraint.value_iris),
                "datatype_iris": list(constraint.datatype_iris),
                "source_module": constraint.source_module,
            }
            for constraint in catalog.cardinality_constraints
        ],
    }


def write_semantic_coverage_report(
    output_path: str | Path,
    *,
    repo_root: str | Path = PROJECT_ROOT,
) -> Path:
    """Write canonical JSON inside the repository and return its path."""

    root = Path(repo_root).resolve()
    target = Path(output_path)
    if not target.is_absolute():
        target = root / target
    target = target.resolve()
    if root not in target.parents:
        raise ValueError("semantic coverage output must be inside the repository")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            build_atmonto_semantic_coverage(root),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return target


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    write_semantic_coverage_report(args.output)
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised by CLI smoke
    raise SystemExit(main())


__all__ = [
    "ATMONTO_DOMAINS",
    "PLANNED_ATMONTO_TERMS",
    "AtmontoCatalog",
    "CardinalityConstraint",
    "ClassHierarchyEdge",
    "OntologyClass",
    "OntologyProperty",
    "build_atmonto_semantic_coverage",
    "load_atmonto_catalog",
    "write_semantic_coverage_report",
]
