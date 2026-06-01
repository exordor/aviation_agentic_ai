from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path


NASA_ATMONTO_DIR = Path("data/ontology/external/icarus_ontology/NASA")
SCHEMA_CATALOG_PATH = Path("data/ontology/curated/nasa_atmonto_schema_catalog.json")
SCHEMA_SLICE_PATH = Path("data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json")
EXTRACTION_SCHEMA_PATH = Path(
    "data/ontology/curated/nasa_atmonto_atcscc_extraction_schema.json"
)
DEFAULT_ATCSCC_JSONL = Path(
    "data/processed/nasa_atmonto/aligned/2026-05-14/atcscc_advisories.jsonl"
)
DEFAULT_EXTRACTION_DIR = Path("data/processed/nasa_atmonto/extraction/2026-05-14")
VALIDATION_REPORT_JSON = Path("reports/stages/nasa_atmonto_minimal_loop_validation.json")
VALIDATION_REPORT_MD = Path("reports/stages/nasa_atmonto_minimal_loop_validation.md")

OWL_NS = "http://www.w3.org/2002/07/owl#"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS_NS = "http://www.w3.org/2000/01/rdf-schema#"
XSD_NS = "http://www.w3.org/2001/XMLSchema#"
PLAIN_LITERAL = f"{RDF_NS}PlainLiteral"

DEFAULT_PREFIXES = {
    "owl": OWL_NS,
    "rdf": RDF_NS,
    "rdfs": RDFS_NS,
    "xsd": XSD_NS,
}

ATCSCC_CLASS_TARGETS = {
    "AirspaceFlowProgramTMI",
    "AirportSpec",
    "FlightSpec",
    "GroundDelayProgramTMI",
    "GroundStopTMI",
    "ReRouteSegment",
    "ReRouteTMI",
    "TFMcontrolElement",
    "TrafficManagementInitiative",
    "ARTCC",
    "ARTCCtier",
    "Airport",
    "AirspaceInfrastructureComponent",
    "AirspaceRoute",
    "NASfacility",
    "WeatherCondition",
    "MeteorologicalCondition",
}

ATCSCC_OBJECT_PROPERTY_TARGETS = {
    "allowedRoute",
    "controlledNASelement",
    "departureScope",
    "excludesARTCC",
    "excludesAirport",
    "flightExclusionSpec",
    "flightInclusionSpec",
    "includesARTCC",
    "includesAirport",
    "withinARTCC",
}

ATCSCC_DATA_PROPERTY_TARGETS = {
    "advisoryNumber",
    "effectiveEndTime",
    "effectiveStartTime",
    "extensionProbability",
    "impactingCondition",
    "impactingConditionMessage",
    "implementationStatus",
    "initiativeComments",
    "issuedTime",
    "reRouteReason",
    "reRouteType",
}

DATATYPE_ALIASES = {
    "string": f"{XSD_NS}string",
    "integer": f"{XSD_NS}integer",
    "int": f"{XSD_NS}integer",
    "float": f"{XSD_NS}float",
    "dateTime": f"{XSD_NS}dateTime",
    "datetime": f"{XSD_NS}dateTime",
    "xsd:string": f"{XSD_NS}string",
    "xsd:integer": f"{XSD_NS}integer",
    "xsd:int": f"{XSD_NS}integer",
    "xsd:float": f"{XSD_NS}float",
    "xsd:dateTime": f"{XSD_NS}dateTime",
}


@dataclass(frozen=True)
class OwlXmlDocument:
    source_file: Path
    ontology_iri: str
    prefixes: dict[str, str]
    imports: tuple[str, ...]
    classes: frozenset[str]
    object_properties: frozenset[str]
    datatype_properties: frozenset[str]
    class_hierarchy: tuple[dict[str, object], ...]
    object_property_domains: tuple[dict[str, object], ...]
    object_property_ranges: tuple[dict[str, object], ...]
    datatype_property_domains: tuple[dict[str, object], ...]
    datatype_property_ranges: tuple[dict[str, object], ...]
    class_property_constraints: tuple[dict[str, object], ...]
    annotations: dict[str, dict[str, str]]
    functional_object_properties: frozenset[str]
    functional_datatype_properties: frozenset[str]


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: Iterable[dict[str, object]]) -> None:
    payload = "\n".join(json.dumps(record, sort_keys=True, ensure_ascii=False) for record in records)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload + ("\n" if payload else ""), encoding="utf-8")


def local_xml_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def local_name(iri: str | None) -> str:
    if not iri:
        return ""
    if "#" in iri:
        return iri.rsplit("#", 1)[-1]
    return iri.rstrip("/").rsplit("/", 1)[-1]


def namespace_of(iri: str) -> str:
    if "#" in iri:
        return iri.rsplit("#", 1)[0] + "#"
    return iri.rstrip("/").rsplit("/", 1)[0] + "/"


def first_direct_child(node: ET.Element, name: str) -> ET.Element | None:
    for child in node:
        if local_xml_name(child.tag) == name:
            return child
    return None


def direct_children(node: ET.Element, name: str | None = None) -> list[ET.Element]:
    return [child for child in node if name is None or local_xml_name(child.tag) == name]


def child_identifier(
    node: ET.Element | None,
    *,
    ontology_iri: str,
    prefixes: dict[str, str],
) -> str | None:
    if node is None:
        return None
    if value := node.attrib.get("IRI"):
        return resolve_iri(value, ontology_iri=ontology_iri, prefixes=prefixes)
    if value := node.attrib.get("abbreviatedIRI"):
        return resolve_abbreviated_iri(value, prefixes)
    if local_xml_name(node.tag) in {"IRI", "AbbreviatedIRI"} and node.text:
        text = node.text.strip()
        if local_xml_name(node.tag) == "AbbreviatedIRI":
            return resolve_abbreviated_iri(text, prefixes)
        return resolve_iri(text, ontology_iri=ontology_iri, prefixes=prefixes)
    return None


def resolve_abbreviated_iri(value: str, prefixes: dict[str, str]) -> str:
    prefix, _, suffix = value.partition(":")
    namespace = prefixes.get(prefix)
    if not namespace:
        return value
    return namespace + suffix


def resolve_iri(value: str, *, ontology_iri: str, prefixes: dict[str, str]) -> str:
    if value.startswith("http://") or value.startswith("https://") or value.startswith("urn:"):
        return value
    if value.startswith("#"):
        return ontology_iri.rstrip("#") + value
    if ":" in value and not value.startswith("/"):
        prefix, _, suffix = value.partition(":")
        if prefix in prefixes:
            return prefixes[prefix] + suffix
    if ontology_iri:
        return ontology_iri.rstrip("#/") + "#" + value.lstrip("#/")
    return value


def collect_class_refs(
    node: ET.Element,
    *,
    ontology_iri: str,
    prefixes: dict[str, str],
) -> list[str]:
    refs: list[str] = []
    for child in node.iter():
        if local_xml_name(child.tag) != "Class":
            continue
        iri = child_identifier(child, ontology_iri=ontology_iri, prefixes=prefixes)
        if iri:
            refs.append(iri)
    return list(dict.fromkeys(refs))


def collect_datatype_refs(
    node: ET.Element,
    *,
    ontology_iri: str,
    prefixes: dict[str, str],
) -> list[str]:
    refs: list[str] = []
    for child in node.iter():
        if local_xml_name(child.tag) != "Datatype":
            continue
        iri = child_identifier(child, ontology_iri=ontology_iri, prefixes=prefixes)
        if iri:
            refs.append(iri)
    return list(dict.fromkeys(refs))


def collect_literals(node: ET.Element) -> list[str]:
    values: list[str] = []
    for child in node.iter():
        if local_xml_name(child.tag) == "Literal" and child.text is not None:
            values.append(" ".join(child.text.split()))
    return values


def direct_property_identifier(
    node: ET.Element,
    property_tag: str,
    *,
    ontology_iri: str,
    prefixes: dict[str, str],
) -> str | None:
    property_node = first_direct_child(node, property_tag)
    return child_identifier(property_node, ontology_iri=ontology_iri, prefixes=prefixes)


def parse_prefixes(root: ET.Element) -> tuple[str, dict[str, str], tuple[str, ...]]:
    prefixes = dict(DEFAULT_PREFIXES)
    ontology_iri = root.attrib.get("ontologyIRI") or root.attrib.get("IRI") or ""
    imports: list[str] = []
    for child in direct_children(root):
        name = local_xml_name(child.tag)
        if name == "Prefix":
            prefixes[child.attrib.get("name", "")] = child.attrib.get("IRI", "")
        elif name == "Import" and child.text:
            imports.append(child.text.strip())
    return ontology_iri, prefixes, tuple(imports)


def parse_declarations(
    root: ET.Element,
    *,
    ontology_iri: str,
    prefixes: dict[str, str],
) -> tuple[set[str], set[str], set[str]]:
    classes: set[str] = set()
    object_properties: set[str] = set()
    datatype_properties: set[str] = set()
    for declaration in direct_children(root, "Declaration"):
        for child in direct_children(declaration):
            iri = child_identifier(child, ontology_iri=ontology_iri, prefixes=prefixes)
            if not iri:
                continue
            name = local_xml_name(child.tag)
            if name == "Class":
                classes.add(iri)
            elif name == "ObjectProperty":
                object_properties.add(iri)
            elif name == "DataProperty":
                datatype_properties.add(iri)
    return classes, object_properties, datatype_properties


def parse_annotations(
    root: ET.Element,
    *,
    ontology_iri: str,
    prefixes: dict[str, str],
) -> dict[str, dict[str, str]]:
    annotations: dict[str, dict[str, str]] = defaultdict(dict)
    for assertion in direct_children(root, "AnnotationAssertion"):
        children = direct_children(assertion)
        if len(children) < 3:
            continue
        annotation_property = child_identifier(
            children[0],
            ontology_iri=ontology_iri,
            prefixes=prefixes,
        )
        target = child_identifier(children[1], ontology_iri=ontology_iri, prefixes=prefixes)
        literal = " ".join((children[2].text or "").split())
        if not annotation_property or not target or not literal:
            continue
        if annotation_property == f"{RDFS_NS}label":
            annotations[target]["label"] = literal
        elif annotation_property == f"{RDFS_NS}comment":
            annotations[target]["comment"] = literal
    return {key: dict(value) for key, value in annotations.items()}


def parse_property_axioms(
    root: ET.Element,
    *,
    ontology_iri: str,
    prefixes: dict[str, str],
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    set[str],
    set[str],
]:
    object_domains: list[dict[str, object]] = []
    object_ranges: list[dict[str, object]] = []
    datatype_domains: list[dict[str, object]] = []
    datatype_ranges: list[dict[str, object]] = []
    functional_object: set[str] = set()
    functional_datatype: set[str] = set()

    for node in direct_children(root):
        name = local_xml_name(node.tag)
        if name == "ObjectPropertyDomain":
            prop = direct_property_identifier(
                node,
                "ObjectProperty",
                ontology_iri=ontology_iri,
                prefixes=prefixes,
            )
            class_set = collect_class_refs(node, ontology_iri=ontology_iri, prefixes=prefixes)
            if prop:
                object_domains.append({"property_iri": prop, "class_set": class_set})
        elif name == "ObjectPropertyRange":
            prop = direct_property_identifier(
                node,
                "ObjectProperty",
                ontology_iri=ontology_iri,
                prefixes=prefixes,
            )
            class_set = collect_class_refs(node, ontology_iri=ontology_iri, prefixes=prefixes)
            if prop:
                object_ranges.append({"property_iri": prop, "class_set": class_set})
        elif name == "DataPropertyDomain":
            prop = direct_property_identifier(
                node,
                "DataProperty",
                ontology_iri=ontology_iri,
                prefixes=prefixes,
            )
            class_set = collect_class_refs(node, ontology_iri=ontology_iri, prefixes=prefixes)
            if prop:
                datatype_domains.append({"property_iri": prop, "class_set": class_set})
        elif name == "DataPropertyRange":
            prop = direct_property_identifier(
                node,
                "DataProperty",
                ontology_iri=ontology_iri,
                prefixes=prefixes,
            )
            datatype_set = collect_datatype_refs(node, ontology_iri=ontology_iri, prefixes=prefixes)
            if prop:
                datatype_ranges.append({"property_iri": prop, "datatype_set": datatype_set})
        elif name == "FunctionalObjectProperty":
            prop = direct_property_identifier(
                node,
                "ObjectProperty",
                ontology_iri=ontology_iri,
                prefixes=prefixes,
            )
            if prop:
                functional_object.add(prop)
        elif name == "FunctionalDataProperty":
            prop = direct_property_identifier(
                node,
                "DataProperty",
                ontology_iri=ontology_iri,
                prefixes=prefixes,
            )
            if prop:
                functional_datatype.add(prop)
    return (
        object_domains,
        object_ranges,
        datatype_domains,
        datatype_ranges,
        functional_object,
        functional_datatype,
    )


def parse_subclass_axioms(
    root: ET.Element,
    *,
    ontology_iri: str,
    prefixes: dict[str, str],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    hierarchy: list[dict[str, object]] = []
    constraints: list[dict[str, object]] = []
    for node in direct_children(root, "SubClassOf"):
        children = direct_children(node)
        if len(children) < 2 or local_xml_name(children[0].tag) != "Class":
            continue
        subclass = child_identifier(children[0], ontology_iri=ontology_iri, prefixes=prefixes)
        if not subclass:
            continue
        expression = children[1]
        expression_name = local_xml_name(expression.tag)
        if expression_name == "Class":
            superclass = child_identifier(
                expression,
                ontology_iri=ontology_iri,
                prefixes=prefixes,
            )
            if superclass:
                hierarchy.append({"subclass_iri": subclass, "superclass_iri": superclass})
            continue

        if expression_name == "ObjectAllValuesFrom":
            prop = direct_property_identifier(
                expression,
                "ObjectProperty",
                ontology_iri=ontology_iri,
                prefixes=prefixes,
            )
            class_set = collect_class_refs(
                expression,
                ontology_iri=ontology_iri,
                prefixes=prefixes,
            )
            if prop:
                constraints.append(
                    {
                        "class_iri": subclass,
                        "property_iri": prop,
                        "constraint_type": "object_all_values_from",
                        "class_set": class_set,
                    }
                )
        elif expression_name == "DataAllValuesFrom":
            prop = direct_property_identifier(
                expression,
                "DataProperty",
                ontology_iri=ontology_iri,
                prefixes=prefixes,
            )
            datatype_set = collect_datatype_refs(
                expression,
                ontology_iri=ontology_iri,
                prefixes=prefixes,
            )
            allowed_values = collect_literals(expression)
            if prop:
                constraints.append(
                    {
                        "class_iri": subclass,
                        "property_iri": prop,
                        "constraint_type": "data_all_values_from",
                        "datatype_set": datatype_set,
                        "allowed_values": allowed_values,
                    }
                )
        elif expression_name in {"ObjectExactCardinality", "DataExactCardinality"}:
            property_tag = "ObjectProperty" if expression_name.startswith("Object") else "DataProperty"
            prop = direct_property_identifier(
                expression,
                property_tag,
                ontology_iri=ontology_iri,
                prefixes=prefixes,
            )
            if prop:
                constraints.append(
                    {
                        "class_iri": subclass,
                        "property_iri": prop,
                        "constraint_type": expression_name[0].lower() + expression_name[1:],
                        "cardinality": expression.attrib.get("cardinality"),
                        "class_set": collect_class_refs(
                            expression,
                            ontology_iri=ontology_iri,
                            prefixes=prefixes,
                        ),
                        "datatype_set": collect_datatype_refs(
                            expression,
                            ontology_iri=ontology_iri,
                            prefixes=prefixes,
                        ),
                    }
                )
    return hierarchy, constraints


def parse_owl_xml_file(path: str | Path) -> OwlXmlDocument:
    source_file = Path(path)
    root = ET.fromstring(source_file.read_bytes())
    ontology_iri, prefixes, imports = parse_prefixes(root)
    classes, object_properties, datatype_properties = parse_declarations(
        root,
        ontology_iri=ontology_iri,
        prefixes=prefixes,
    )
    class_hierarchy, class_property_constraints = parse_subclass_axioms(
        root,
        ontology_iri=ontology_iri,
        prefixes=prefixes,
    )
    (
        object_domains,
        object_ranges,
        datatype_domains,
        datatype_ranges,
        functional_object,
        functional_datatype,
    ) = parse_property_axioms(root, ontology_iri=ontology_iri, prefixes=prefixes)

    for relation in class_hierarchy:
        classes.add(str(relation["subclass_iri"]))
        classes.add(str(relation["superclass_iri"]))
    for relation in object_domains + object_ranges + datatype_domains:
        for class_iri in relation.get("class_set", []):
            classes.add(str(class_iri))
    for relation in datatype_ranges:
        datatype_properties.add(str(relation["property_iri"]))
    for relation in object_domains + object_ranges:
        object_properties.add(str(relation["property_iri"]))
    for relation in datatype_domains:
        datatype_properties.add(str(relation["property_iri"]))
    for constraint in class_property_constraints:
        classes.add(str(constraint["class_iri"]))
        prop = str(constraint["property_iri"])
        if str(constraint["constraint_type"]).startswith("object"):
            object_properties.add(prop)
            for class_iri in constraint.get("class_set", []):
                classes.add(str(class_iri))
        else:
            datatype_properties.add(prop)

    return OwlXmlDocument(
        source_file=source_file,
        ontology_iri=ontology_iri,
        prefixes=prefixes,
        imports=imports,
        classes=frozenset(classes),
        object_properties=frozenset(object_properties),
        datatype_properties=frozenset(datatype_properties),
        class_hierarchy=tuple(class_hierarchy),
        object_property_domains=tuple(object_domains),
        object_property_ranges=tuple(object_ranges),
        datatype_property_domains=tuple(datatype_domains),
        datatype_property_ranges=tuple(datatype_ranges),
        class_property_constraints=tuple(class_property_constraints),
        annotations=parse_annotations(root, ontology_iri=ontology_iri, prefixes=prefixes),
        functional_object_properties=frozenset(functional_object),
        functional_datatype_properties=frozenset(functional_datatype),
    )


def compact_iri(iri: str, prefixes: dict[str, str]) -> str:
    candidates = [
        (prefix, namespace)
        for prefix, namespace in prefixes.items()
        if prefix and namespace and iri.startswith(namespace)
    ]
    if candidates:
        prefix, namespace = max(candidates, key=lambda item: len(item[1]))
        return f"{prefix}:{iri.removeprefix(namespace)}"
    return iri


def merge_set_relations(
    relations: Iterable[dict[str, object]],
    key_field: str,
    value_field: str,
) -> dict[str, set[str]]:
    merged: dict[str, set[str]] = defaultdict(set)
    for relation in relations:
        key = str(relation[key_field])
        for value in relation.get(value_field, []):
            merged[key].add(str(value))
    return merged


def source_index(documents: Iterable[OwlXmlDocument]) -> dict[str, set[str]]:
    sources: dict[str, set[str]] = defaultdict(set)
    for document in documents:
        source_file = document.source_file.as_posix()
        for iri in (
            set(document.classes)
            | set(document.object_properties)
            | set(document.datatype_properties)
        ):
            sources[iri].add(source_file)
        for annotation_target in document.annotations:
            sources[annotation_target].add(source_file)
    return sources


def term_entry(
    iri: str,
    *,
    prefixes: dict[str, str],
    annotations: dict[str, dict[str, str]],
    sources: dict[str, set[str]],
    repo_root: Path,
) -> dict[str, object]:
    return {
        "iri": iri,
        "prefixed_name": compact_iri(iri, prefixes),
        "local_name": local_name(iri),
        "label": annotations.get(iri, {}).get("label", ""),
        "comment": annotations.get(iri, {}).get("comment", ""),
        "namespace": namespace_of(iri),
        "source_files": [
            project_relative_path(path, repo_root) for path in sorted(sources.get(iri, []))
        ],
    }


def build_nasa_atmonto_schema_catalog(
    ontology_dir: str | Path,
    *,
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, object]:
    repo_root = Path(repo_root).resolve()
    ontology_dir = Path(ontology_dir)
    documents = [parse_owl_xml_file(path) for path in sorted(ontology_dir.glob("*.owl"))]
    if not documents:
        raise FileNotFoundError(f"No .owl files found in {ontology_dir}")

    prefixes = dict(DEFAULT_PREFIXES)
    ontology_iris: list[str] = []
    imports: set[str] = set()
    for document in documents:
        prefixes.update({k: v for k, v in document.prefixes.items() if v})
        if document.ontology_iri:
            ontology_iris.append(document.ontology_iri)
        imports.update(document.imports)

    annotations: dict[str, dict[str, str]] = defaultdict(dict)
    for document in documents:
        for iri, values in document.annotations.items():
            annotations[iri].update(values)

    sources = source_index(documents)
    classes = sorted(set().union(*(document.classes for document in documents)))
    object_properties = sorted(set().union(*(document.object_properties for document in documents)))
    datatype_properties = sorted(set().union(*(document.datatype_properties for document in documents)))

    object_domains = merge_set_relations(
        (relation for document in documents for relation in document.object_property_domains),
        "property_iri",
        "class_set",
    )
    object_ranges = merge_set_relations(
        (relation for document in documents for relation in document.object_property_ranges),
        "property_iri",
        "class_set",
    )
    datatype_domains = merge_set_relations(
        (relation for document in documents for relation in document.datatype_property_domains),
        "property_iri",
        "class_set",
    )
    datatype_ranges = merge_set_relations(
        (relation for document in documents for relation in document.datatype_property_ranges),
        "property_iri",
        "datatype_set",
    )
    functional_object_properties = sorted(
        set().union(*(document.functional_object_properties for document in documents))
    )
    functional_datatype_properties = sorted(
        set().union(*(document.functional_datatype_properties for document in documents))
    )

    hierarchy = sorted(
        (
            {
                "subclass_iri": str(relation["subclass_iri"]),
                "subclass": compact_iri(str(relation["subclass_iri"]), prefixes),
                "superclass_iri": str(relation["superclass_iri"]),
                "superclass": compact_iri(str(relation["superclass_iri"]), prefixes),
                "source_file": project_relative_path(document.source_file, repo_root),
            }
            for document in documents
            for relation in document.class_hierarchy
        ),
        key=lambda item: (str(item["subclass_iri"]), str(item["superclass_iri"])),
    )
    constraints = sorted(
        (
            {
                **constraint,
                "class": compact_iri(str(constraint["class_iri"]), prefixes),
                "property": compact_iri(str(constraint["property_iri"]), prefixes),
                "class_set": [
                    compact_iri(str(class_iri), prefixes)
                    for class_iri in constraint.get("class_set", [])
                ],
                "class_iri_set": [str(class_iri) for class_iri in constraint.get("class_set", [])],
                "datatype_set": [
                    compact_iri(str(datatype_iri), prefixes)
                    for datatype_iri in constraint.get("datatype_set", [])
                ],
                "datatype_iri_set": [
                    str(datatype_iri) for datatype_iri in constraint.get("datatype_set", [])
                ],
                "source_file": project_relative_path(document.source_file, repo_root),
            }
            for document in documents
            for constraint in document.class_property_constraints
        ),
        key=lambda item: (
            str(item["class_iri"]),
            str(item["property_iri"]),
            str(item["constraint_type"]),
        ),
    )

    class_entries = [
        term_entry(
            iri,
            prefixes=prefixes,
            annotations=annotations,
            sources=sources,
            repo_root=repo_root,
        )
        for iri in classes
    ]
    object_property_entries = [
        {
            **term_entry(
                iri,
                prefixes=prefixes,
                annotations=annotations,
                sources=sources,
                repo_root=repo_root,
            ),
            "domain_iri_set": sorted(object_domains.get(iri, set())),
            "domain_set": [compact_iri(value, prefixes) for value in sorted(object_domains.get(iri, set()))],
            "range_iri_set": sorted(object_ranges.get(iri, set())),
            "range_set": [compact_iri(value, prefixes) for value in sorted(object_ranges.get(iri, set()))],
            "functional": iri in functional_object_properties,
        }
        for iri in object_properties
    ]
    datatype_property_entries = [
        {
            **term_entry(
                iri,
                prefixes=prefixes,
                annotations=annotations,
                sources=sources,
                repo_root=repo_root,
            ),
            "domain_iri_set": sorted(datatype_domains.get(iri, set())),
            "domain_set": [
                compact_iri(value, prefixes) for value in sorted(datatype_domains.get(iri, set()))
            ],
            "datatype_iri_set": sorted(datatype_ranges.get(iri, set())),
            "datatype_set": [
                compact_iri(value, prefixes) for value in sorted(datatype_ranges.get(iri, set()))
            ],
            "functional": iri in functional_datatype_properties,
        }
        for iri in datatype_properties
    ]

    catalog = {
        "source_family": "nasa_atmonto_owl_xml",
        "ontology_id": "nasa_atmonto",
        "parser_version": "aviation_agentic_ai.ontology.atmonto_minimal_loop.v1",
        "role": "primary_schema_constraint",
        "boundary": "schema_constraint_not_abox_ground_truth",
        "ontology_iris": sorted(set(ontology_iris)),
        "imports": sorted(imports),
        "source_files": [
            project_relative_path(document.source_file, repo_root) for document in documents
        ],
        "namespaces": [
            {"prefix": prefix, "namespace": namespace}
            for prefix, namespace in sorted(prefixes.items())
            if namespace
        ],
        "counts": {
            "source_files": len(documents),
            "classes": len(class_entries),
            "object_properties": len(object_property_entries),
            "datatype_properties": len(datatype_property_entries),
            "class_hierarchy_axioms": len(hierarchy),
            "class_property_constraints": len(constraints),
            "object_property_signatures": len(object_property_entries),
            "datatype_property_signatures": len(datatype_property_entries),
        },
        "classes": class_entries,
        "object_properties": object_property_entries,
        "datatype_properties": datatype_property_entries,
        "class_hierarchy": hierarchy,
        "class_property_constraints": constraints,
        "schema_catalog": {
            "object_property_signatures": object_property_entries,
            "datatype_property_signatures": datatype_property_entries,
        },
    }
    return catalog


def by_local_name(entries: Iterable[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {str(entry["local_name"]): entry for entry in entries}


def selected_terms_by_local(
    entries: Iterable[dict[str, object]],
    local_targets: set[str],
) -> list[dict[str, object]]:
    return sorted(
        [entry for entry in entries if str(entry["local_name"]) in local_targets],
        key=lambda entry: str(entry["prefixed_name"]),
    )


def build_atcscc_schema_slice(catalog: dict[str, object]) -> dict[str, object]:
    class_map = by_local_name(catalog["classes"])  # type: ignore[arg-type]
    object_property_map = by_local_name(catalog["object_properties"])  # type: ignore[arg-type]
    datatype_property_map = by_local_name(catalog["datatype_properties"])  # type: ignore[arg-type]

    selected_classes = selected_terms_by_local(catalog["classes"], ATCSCC_CLASS_TARGETS)  # type: ignore[arg-type]
    selected_object_properties = selected_terms_by_local(
        catalog["object_properties"],  # type: ignore[arg-type]
        ATCSCC_OBJECT_PROPERTY_TARGETS,
    )
    selected_datatype_properties = selected_terms_by_local(
        catalog["datatype_properties"],  # type: ignore[arg-type]
        ATCSCC_DATA_PROPERTY_TARGETS,
    )

    selected_class_iris = {str(entry["iri"]) for entry in selected_classes}
    for prop in selected_object_properties + selected_datatype_properties:
        for field in ("domain_iri_set", "range_iri_set"):
            for iri in prop.get(field, []):
                selected_class_iris.add(str(iri))
    for constraint in catalog["class_property_constraints"]:  # type: ignore[index]
        if (
            local_name(str(constraint["class_iri"])) in ATCSCC_CLASS_TARGETS
            or local_name(str(constraint["property_iri"]))
            in ATCSCC_OBJECT_PROPERTY_TARGETS | ATCSCC_DATA_PROPERTY_TARGETS
        ):
            selected_class_iris.add(str(constraint["class_iri"]))
            for class_iri in constraint.get("class_iri_set", []):
                selected_class_iris.add(str(class_iri))

    selected_classes = sorted(
        [
            entry
            for entry in catalog["classes"]  # type: ignore[index]
            if str(entry["iri"]) in selected_class_iris
        ],
        key=lambda entry: str(entry["prefixed_name"]),
    )

    selected_property_iris = {
        str(entry["iri"]) for entry in selected_object_properties + selected_datatype_properties
    }
    selected_constraint_rows = [
        constraint
        for constraint in catalog["class_property_constraints"]  # type: ignore[index]
        if str(constraint["class_iri"]) in selected_class_iris
        and str(constraint["property_iri"]) in selected_property_iris
    ]
    selected_hierarchy = [
        relation
        for relation in catalog["class_hierarchy"]  # type: ignore[index]
        if str(relation["subclass_iri"]) in selected_class_iris
        or str(relation["superclass_iri"]) in selected_class_iris
    ]

    missing_targets = {
        "classes": sorted(name for name in ATCSCC_CLASS_TARGETS if name not in class_map),
        "object_properties": sorted(
            name for name in ATCSCC_OBJECT_PROPERTY_TARGETS if name not in object_property_map
        ),
        "datatype_properties": sorted(
            name for name in ATCSCC_DATA_PROPERTY_TARGETS if name not in datatype_property_map
        ),
    }
    return {
        "schema_slice_id": "nasa_atmonto_atcscc_tmi_slice",
        "source_catalog": "nasa_atmonto",
        "selection_policy": {
            "primary_source": "NASA ATMONTO OWL/XML TBox",
            "source_family": "atcscc_advisories",
            "selected_by": "exact local-name targets for ATCSCC TMI fields plus domain/range dependencies",
            "boundary": "closed-world runtime validation slice derived from open-world OWL axioms",
        },
        "classes": selected_classes,
        "object_properties": selected_object_properties,
        "datatype_properties": selected_datatype_properties,
        "class_hierarchy": selected_hierarchy,
        "class_property_constraints": selected_constraint_rows,
        "missing_targets": missing_targets,
        "counts": {
            "classes": len(selected_classes),
            "object_properties": len(selected_object_properties),
            "datatype_properties": len(selected_datatype_properties),
            "class_hierarchy_axioms": len(selected_hierarchy),
            "class_property_constraints": len(selected_constraint_rows),
        },
    }


def schema_identifiers(entries: Iterable[dict[str, object]]) -> list[str]:
    values: set[str] = set()
    for entry in entries:
        values.add(str(entry["iri"]))
        values.add(str(entry["prefixed_name"]))
        values.add(str(entry["local_name"]))
    return sorted(values)


def build_extraction_json_schema(schema_slice: dict[str, object]) -> dict[str, object]:
    class_identifiers = schema_identifiers(schema_slice["classes"])  # type: ignore[arg-type]
    object_property_identifiers = schema_identifiers(
        schema_slice["object_properties"]  # type: ignore[arg-type]
    )
    datatype_property_identifiers = schema_identifiers(
        schema_slice["datatype_properties"]  # type: ignore[arg-type]
    )
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:aviation-agentic-ai:nasa-atmonto:atcscc-extraction-schema",
        "title": "NASA ATMONTO ATCSCC schema-slice extraction payload",
        "type": "object",
        "additionalProperties": False,
        "required": ["source_id", "facts"],
        "properties": {
            "source_id": {"type": "string"},
            "source_family": {"const": "atcscc_advisories"},
            "facts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": True,
                    "required": [
                        "fact_id",
                        "fact_type",
                        "subject",
                        "subject_class",
                        "predicate",
                        "evidence_text",
                    ],
                    "properties": {
                        "fact_id": {"type": "string"},
                        "fact_type": {
                            "enum": ["datatype_property", "object_property"],
                        },
                        "subject": {"type": "string"},
                        "subject_class": {"enum": class_identifiers},
                        "predicate": {
                            "anyOf": [
                                {"enum": object_property_identifiers},
                                {"enum": datatype_property_identifiers},
                            ]
                        },
                        "object": {"type": "string"},
                        "object_class": {"enum": class_identifiers},
                        "value": {},
                        "datatype": {
                            "enum": sorted(
                                set(DATATYPE_ALIASES) | set(DATATYPE_ALIASES.values())
                            )
                        },
                        "evidence_text": {"type": "string", "minLength": 1},
                    },
                },
            },
        },
    }


def read_jsonl(path: Path, *, limit: int | None = None) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            records.append(json.loads(line))
            if limit is not None and len(records) >= limit:
                break
    return records


def hash_id(*parts: object, length: int = 16) -> str:
    body = "|".join(str(part) for part in parts)
    return sha256(body.encode("utf-8")).hexdigest()[:length]


def source_entity_iri(source_id: str) -> str:
    return "urn:aviation-agentic-ai:atcscc-advisory:" + source_id.replace(":", ":")


def nas_entity_iri(code: str) -> str:
    return "urn:aviation-agentic-ai:nas-element:" + code.upper()


def classify_tmi(text: str) -> str:
    upper = text.upper()
    if "GROUND DELAY PROGRAM" in upper or re.search(r"\bGDP\b", upper):
        return "GroundDelayProgramTMI"
    if "GROUND STOP" in upper:
        return "GroundStopTMI"
    if "AIRSPACE FLOW PROGRAM" in upper or re.search(r"\bAFP\b", upper):
        return "AirspaceFlowProgramTMI"
    if "REROUTE" in upper or "RE-ROUTE" in upper or "NRP SUSPENSION" in upper or " ROUTE " in upper:
        return "ReRouteTMI"
    return "TrafficManagementInitiative"


def evidence_match(text: str, pattern: str) -> re.Match[str] | None:
    return re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)


def compact_evidence(value: str) -> str:
    return " ".join(value.split())


def add_datatype_fact(
    facts: list[dict[str, object]],
    *,
    source_id: str,
    subject: str,
    subject_class: str,
    predicate: str,
    value: object,
    datatype: str,
    evidence_text: str,
    value_normalization: str = "literal",
) -> None:
    facts.append(
        {
            "fact_id": "fact-" + hash_id(source_id, predicate, value, evidence_text),
            "source_id": source_id,
            "fact_type": "datatype_property",
            "subject": subject,
            "subject_class": subject_class,
            "predicate": predicate,
            "value": value,
            "datatype": datatype,
            "evidence_text": evidence_text,
            "value_normalization": value_normalization,
            "extraction_method": "schema_slice_rule_baseline",
            "review_status": "bronze_until_reviewed",
        }
    )


def add_object_fact(
    facts: list[dict[str, object]],
    *,
    source_id: str,
    subject: str,
    subject_class: str,
    predicate: str,
    object_value: str,
    object_label: str,
    object_class: str,
    evidence_text: str,
) -> None:
    facts.append(
        {
            "fact_id": "fact-" + hash_id(source_id, predicate, object_value, evidence_text),
            "source_id": source_id,
            "fact_type": "object_property",
            "subject": subject,
            "subject_class": subject_class,
            "predicate": predicate,
            "object": object_value,
            "object_label": object_label,
            "object_class": object_class,
            "evidence_text": evidence_text,
            "extraction_method": "schema_slice_rule_baseline",
            "review_status": "bronze_until_reviewed",
        }
    )


def interval_by_basis(row: dict[str, object], basis: str) -> dict[str, object] | None:
    alignment = row.get("temporal_alignment")
    if not isinstance(alignment, dict):
        return None
    for interval in alignment.get("parsed_intervals", []):
        if isinstance(interval, dict) and interval.get("basis") == basis:
            return interval
    return None


def evidence_for_block(text: str, label: str) -> str | None:
    pattern = rf"{re.escape(label)}:\s*(.+?)(?=\n[A-Z][A-Z /]+:|\s+[A-Z][A-Z /]+:|\nFAA\.gov|\Z)"
    match = evidence_match(text, pattern)
    if not match:
        return None
    return compact_evidence(match.group(0))


def evidence_for_field(text: str, label: str, value_pattern: str) -> tuple[str, str] | None:
    pattern = rf"{re.escape(label)}:\s*({value_pattern})"
    match = evidence_match(text, pattern)
    if not match:
        return None
    return compact_evidence(match.group(0)), compact_evidence(match.group(1))


def classify_controlled_element(code: str, element_type: str | None = None) -> str:
    if element_type and element_type.upper() == "APT":
        return "Airport"
    if code.upper().startswith("Z") and len(code) == 3:
        return "ARTCC"
    if len(code) in {3, 4}:
        return "Airport"
    return "TFMcontrolElement"


def extract_atcscc_candidate_payload(row: dict[str, object]) -> dict[str, object]:
    source_id = str(row["source_id"])
    text = str(row.get("text", ""))
    subject = source_entity_iri(source_id)
    subject_class = classify_tmi(text)
    facts: list[dict[str, object]] = []

    advisory_number = row.get("advisory_number")
    header_match = evidence_match(text, r"ATCSCC ADVZY\s+(\d{3})\s+[^\n]+")
    header_evidence = compact_evidence(header_match.group(0)) if header_match else source_id
    if advisory_number is not None:
        add_datatype_fact(
            facts,
            source_id=source_id,
            subject=subject,
            subject_class=subject_class,
            predicate="advisoryNumber",
            value=advisory_number,
            datatype="xsd:integer",
            evidence_text=header_evidence,
            value_normalization="source_json_integer",
        )

    issued_interval = interval_by_basis(row, "issued_time")
    if issued_interval and issued_interval.get("start"):
        evidence = evidence_for_block(text, "SIGNATURE") or header_evidence
        add_datatype_fact(
            facts,
            source_id=source_id,
            subject=subject,
            subject_class=subject_class,
            predicate="issuedTime",
            value=issued_interval["start"],
            datatype="xsd:dateTime",
            evidence_text=evidence,
            value_normalization="aligned_interval_start",
        )

    effective_interval = interval_by_basis(row, "compact_effective_range")
    if effective_interval and effective_interval.get("start") and effective_interval.get("end"):
        evidence = evidence_for_block(text, "EFFECTIVE TIME") or header_evidence
        add_datatype_fact(
            facts,
            source_id=source_id,
            subject=subject,
            subject_class=subject_class,
            predicate="effectiveStartTime",
            value=effective_interval["start"],
            datatype="xsd:dateTime",
            evidence_text=evidence,
            value_normalization="aligned_effective_interval_start",
        )
        add_datatype_fact(
            facts,
            source_id=source_id,
            subject=subject,
            subject_class=subject_class,
            predicate="effectiveEndTime",
            value=effective_interval["end"],
            datatype="xsd:dateTime",
            evidence_text=evidence,
            value_normalization="aligned_effective_interval_end",
        )

    control_match = evidence_for_field(text, "CTL ELEMENT", r"[A-Z0-9]{2,5}")
    element_type_match = evidence_for_field(text, "ELEMENT TYPE", r"[A-Z0-9]{2,12}")
    if control_match:
        evidence, code = control_match
        element_type = element_type_match[1] if element_type_match else None
        add_object_fact(
            facts,
            source_id=source_id,
            subject=subject,
            subject_class=subject_class,
            predicate="controlledNASelement",
            object_value=nas_entity_iri(code),
            object_label=code,
            object_class=classify_controlled_element(code, element_type),
            evidence_text=evidence,
        )
    else:
        constrained_match = evidence_for_field(
            text,
            "CONSTRAINED FACILITIES",
            r"[A-Z0-9 /]+?(?=\s+DUE TO|\s+REASON:|\n|$)",
        )
        if constrained_match:
            evidence, code_list = constrained_match
            for code in re.findall(r"\b[A-Z][A-Z0-9]{2,4}\b", code_list):
                add_object_fact(
                    facts,
                    source_id=source_id,
                    subject=subject,
                    subject_class=subject_class,
                    predicate="controlledNASelement",
                    object_value=nas_entity_iri(code),
                    object_label=code,
                    object_class=classify_controlled_element(code),
                    evidence_text=evidence,
                )

    extension_match = evidence_for_field(text, "PROBABILITY OF EXTENSION", r"[A-Z]+")
    if extension_match:
        evidence, value = extension_match
        add_datatype_fact(
            facts,
            source_id=source_id,
            subject=subject,
            subject_class=subject_class,
            predicate="extensionProbability",
            value=value.upper(),
            datatype="xsd:string",
            evidence_text=evidence,
            value_normalization="upper_enum",
        )

    impact_match = evidence_for_field(
        text,
        "IMPACTING CONDITION",
        r"[A-Z /]+?(?=\s+COMMENTS:|\s+EFFECTIVE TIME:|\n|$)",
    )
    if impact_match:
        evidence, value = impact_match
        condition = value.split("/")[0].strip().lower()
        add_datatype_fact(
            facts,
            source_id=source_id,
            subject=subject,
            subject_class=subject_class,
            predicate="impactingCondition",
            value=condition,
            datatype="xsd:string",
            evidence_text=evidence,
            value_normalization="lower_first_token",
        )
        add_datatype_fact(
            facts,
            source_id=source_id,
            subject=subject,
            subject_class=subject_class,
            predicate="impactingConditionMessage",
            value=value,
            datatype="xsd:string",
            evidence_text=evidence,
            value_normalization="literal",
        )

    comments_match = evidence_for_field(text, "COMMENTS", r".+?(?=\s+EFFECTIVE TIME:|\nEFFECTIVE TIME:|\Z)")
    if comments_match:
        evidence, value = comments_match
        add_datatype_fact(
            facts,
            source_id=source_id,
            subject=subject,
            subject_class=subject_class,
            predicate="initiativeComments",
            value=value.strip(),
            datatype="xsd:string",
            evidence_text=evidence,
            value_normalization="literal",
        )

    implementation_match = evidence_match(text, r"_(FYI|PLN|RMD|RQD)\b")
    if implementation_match and subject_class == "ReRouteTMI":
        add_datatype_fact(
            facts,
            source_id=source_id,
            subject=subject,
            subject_class=subject_class,
            predicate="implementationStatus",
            value=implementation_match.group(1).upper(),
            datatype="xsd:string",
            evidence_text=implementation_match.group(0),
            value_normalization="upper_enum",
        )

    return {
        "source_id": source_id,
        "source_family": "atcscc_advisories",
        "source_url": row.get("source_url"),
        "subject": subject,
        "subject_class": subject_class,
        "facts": facts,
    }


class CatalogIndex:
    def __init__(self, schema_slice: dict[str, object]) -> None:
        self.entries_by_iri: dict[str, dict[str, object]] = {}
        self.identifier_to_iri: dict[str, str] = {}
        self.classes: set[str] = set()
        self.object_properties: set[str] = set()
        self.datatype_properties: set[str] = set()
        self.datatypes = dict(DATATYPE_ALIASES)
        self.parents: dict[str, set[str]] = defaultdict(set)
        self.class_property_constraints = schema_slice["class_property_constraints"]

        for category in ("classes", "object_properties", "datatype_properties"):
            for entry in schema_slice[category]:  # type: ignore[index]
                iri = str(entry["iri"])
                self.entries_by_iri[iri] = entry
                self.identifier_to_iri[iri] = iri
                self.identifier_to_iri[str(entry["prefixed_name"])] = iri
                self.identifier_to_iri[str(entry["local_name"])] = iri
                self.identifier_to_iri[str(entry["local_name"]).lower()] = iri
                if category == "classes":
                    self.classes.add(iri)
                elif category == "object_properties":
                    self.object_properties.add(iri)
                else:
                    self.datatype_properties.add(iri)

        for relation in schema_slice["class_hierarchy"]:  # type: ignore[index]
            self.parents[str(relation["subclass_iri"])].add(str(relation["superclass_iri"]))

    def expand(self, value: object, *, expected: str) -> tuple[str | None, list[str]]:
        if value is None:
            return None, []
        raw = str(value)
        if expected == "datatype":
            expanded = self.datatypes.get(raw) or self.datatypes.get(raw.lower())
            if expanded:
                return expanded, [] if expanded == raw else [f"datatype_expansion:{raw}->{expanded}"]
            return None, []
        expanded = self.identifier_to_iri.get(raw) or self.identifier_to_iri.get(raw.lower())
        if not expanded:
            return None, []
        if expanded == raw:
            return expanded, []
        return expanded, [f"identifier_expansion:{raw}->{compact_iri(expanded, self.prefixes)}"]

    @property
    def prefixes(self) -> dict[str, str]:
        prefixes: dict[str, str] = dict(DEFAULT_PREFIXES)
        for iri, entry in self.entries_by_iri.items():
            prefixed_name = str(entry.get("prefixed_name", ""))
            if ":" in prefixed_name and not prefixed_name.startswith("http"):
                prefix, _, suffix = prefixed_name.partition(":")
                if suffix and iri.endswith(suffix):
                    prefixes[prefix] = iri.removesuffix(suffix)
        return prefixes

    def ancestors_inclusive(self, class_iri: str) -> set[str]:
        visited = {class_iri}
        queue: deque[str] = deque([class_iri])
        while queue:
            current = queue.popleft()
            for parent in self.parents.get(current, set()):
                if parent not in visited:
                    visited.add(parent)
                    queue.append(parent)
        return visited

    def class_matches(self, candidate_class: str, allowed_classes: Iterable[str]) -> bool:
        candidate_ancestors = self.ancestors_inclusive(candidate_class)
        return any(allowed in candidate_ancestors for allowed in allowed_classes)

    def class_specific_ranges(self, class_iri: str, property_iri: str) -> set[str]:
        classes_to_check = self.ancestors_inclusive(class_iri)
        ranges: set[str] = set()
        for constraint in self.class_property_constraints:  # type: ignore[union-attr]
            if (
                str(constraint["constraint_type"]) == "object_all_values_from"
                and str(constraint["property_iri"]) == property_iri
                and str(constraint["class_iri"]) in classes_to_check
            ):
                ranges.update(str(value) for value in constraint.get("class_iri_set", []))
        return ranges

    def class_specific_domains(self, property_iri: str) -> set[str]:
        return {
            str(constraint["class_iri"])
            for constraint in self.class_property_constraints  # type: ignore[union-attr]
            if str(constraint["property_iri"]) == property_iri
        }

    def allowed_values(self, class_iri: str, property_iri: str) -> dict[str, str]:
        classes_to_check = self.ancestors_inclusive(class_iri)
        values: dict[str, str] = {}
        for constraint in self.class_property_constraints:  # type: ignore[union-attr]
            if (
                str(constraint["constraint_type"]) == "data_all_values_from"
                and str(constraint["property_iri"]) == property_iri
                and str(constraint["class_iri"]) in classes_to_check
            ):
                for value in constraint.get("allowed_values", []):
                    values[str(value).lower()] = str(value)
        return values


def coerce_value(value: object, datatype_iri: str) -> tuple[object, list[str], list[str]]:
    repairs: list[str] = []
    errors: list[str] = []
    if datatype_iri in {f"{XSD_NS}integer", f"{XSD_NS}int"}:
        if isinstance(value, int):
            return value, repairs, errors
        if isinstance(value, str) and re.fullmatch(r"[-+]?\d+", value.strip()):
            repairs.append(f"datatype_coercion:{value}->integer")
            return int(value), repairs, errors
        errors.append("datatype_value_not_integer")
    elif datatype_iri == f"{XSD_NS}float":
        if isinstance(value, int | float):
            return float(value), repairs, errors
        if isinstance(value, str):
            try:
                return float(value.strip()), [f"datatype_coercion:{value}->float"], errors
            except ValueError:
                errors.append("datatype_value_not_float")
    elif datatype_iri == f"{XSD_NS}dateTime":
        if isinstance(value, str):
            candidate = value.replace("Z", "+00:00")
            try:
                datetime.fromisoformat(candidate)
                return value, repairs, errors
            except ValueError:
                errors.append("datatype_value_not_datetime")
        else:
            errors.append("datatype_value_not_datetime")
    elif datatype_iri == f"{XSD_NS}string":
        if isinstance(value, str):
            return value, repairs, errors
        repairs.append(f"datatype_coercion:{value}->string")
        return str(value), repairs, errors
    return value, repairs, errors


def validate_candidate_fact(
    fact: dict[str, object],
    *,
    source_text: str,
    index: CatalogIndex,
) -> dict[str, object]:
    repaired = dict(fact)
    repairs: list[str] = []
    warnings: list[str] = []
    errors: list[str] = []

    subject_class, subject_repairs = index.expand(fact.get("subject_class"), expected="class")
    repairs.extend(subject_repairs)
    if not subject_class or subject_class not in index.classes:
        errors.append("unknown_subject_class")

    predicate, predicate_repairs = index.expand(fact.get("predicate"), expected="property")
    repairs.extend(predicate_repairs)
    if not predicate:
        errors.append("unknown_predicate")

    fact_type = str(fact.get("fact_type"))
    property_entry = index.entries_by_iri.get(predicate or "")
    if predicate and fact_type == "object_property" and predicate not in index.object_properties:
        errors.append("predicate_not_object_property")
    if predicate and fact_type == "datatype_property" and predicate not in index.datatype_properties:
        errors.append("predicate_not_datatype_property")

    if subject_class and property_entry:
        domain_set = [str(value) for value in property_entry.get("domain_iri_set", [])]
        if predicate:
            domain_set.extend(sorted(index.class_specific_domains(predicate)))
        if domain_set and not index.class_matches(subject_class, domain_set):
            errors.append("domain_violation")
        elif not domain_set:
            warnings.append("domain_unconstrained")

    evidence_text = str(fact.get("evidence_text", ""))
    if not evidence_text:
        errors.append("missing_evidence")
    elif evidence_text not in source_text:
        collapsed_source = compact_evidence(source_text)
        collapsed_evidence = compact_evidence(evidence_text)
        if collapsed_evidence and collapsed_evidence in collapsed_source:
            repairs.append("evidence_whitespace_normalization")
        else:
            errors.append("evidence_not_found_in_source")

    if fact_type == "object_property":
        object_class, object_repairs = index.expand(fact.get("object_class"), expected="class")
        repairs.extend(object_repairs)
        if not object_class or object_class not in index.classes:
            errors.append("unknown_object_class")
        elif subject_class and property_entry:
            range_set = {str(value) for value in property_entry.get("range_iri_set", [])}
            range_set.update(index.class_specific_ranges(subject_class, predicate or ""))
            if range_set and not index.class_matches(object_class, range_set):
                errors.append("range_violation")
            elif not range_set:
                warnings.append("range_unconstrained")
        repaired["object_class"] = object_class
    elif fact_type == "datatype_property":
        datatype, datatype_repairs = index.expand(fact.get("datatype"), expected="datatype")
        repairs.extend(datatype_repairs)
        if not datatype:
            errors.append("unknown_datatype")
        elif property_entry:
            datatype_set = [str(value) for value in property_entry.get("datatype_iri_set", [])]
            if datatype_set and datatype not in datatype_set:
                errors.append("datatype_range_violation")
            value, value_repairs, value_errors = coerce_value(fact.get("value"), datatype)
            repairs.extend(value_repairs)
            errors.extend(value_errors)
            if subject_class and predicate:
                allowed_values = index.allowed_values(subject_class, predicate)
                if allowed_values:
                    value_key = str(value).lower()
                    if value_key not in allowed_values:
                        errors.append("allowed_value_violation")
                    elif value != allowed_values[value_key]:
                        repairs.append(f"allowed_value_normalization:{value}->{allowed_values[value_key]}")
                        value = allowed_values[value_key]
            repaired["value"] = value
            repaired["datatype"] = datatype
    else:
        errors.append("unknown_fact_type")

    repaired["subject_class"] = subject_class
    repaired["predicate"] = predicate
    if errors:
        status = "rejected_schema"
        if any(error.startswith("evidence") or error == "missing_evidence" for error in errors):
            status = "rejected_evidence"
    elif repairs:
        status = "repaired_accepted"
    elif warnings:
        status = "accepted_with_warnings"
    else:
        status = "accepted_deterministic"

    return {
        "source_id": fact.get("source_id"),
        "fact_id": fact.get("fact_id"),
        "candidate": fact,
        "validated_fact": repaired if not errors else None,
        "status": status,
        "accepted": not errors,
        "repairs": repairs,
        "warnings": warnings,
        "errors": errors,
        "review_status": "bronze_until_reviewed",
    }


def validate_candidate_payloads(
    payloads: list[dict[str, object]],
    source_rows: list[dict[str, object]],
    schema_slice: dict[str, object],
) -> list[dict[str, object]]:
    source_text_by_id = {str(row["source_id"]): str(row.get("text", "")) for row in source_rows}
    index = CatalogIndex(schema_slice)
    validations: list[dict[str, object]] = []
    for payload in payloads:
        source_id = str(payload["source_id"])
        source_text = source_text_by_id[source_id]
        for fact in payload.get("facts", []):
            if isinstance(fact, dict):
                validations.append(
                    validate_candidate_fact(fact, source_text=source_text, index=index)
                )
    return validations


def report_markdown(report: dict[str, object]) -> str:
    status_counts = report["status_counts"]
    error_counts = report["error_counts"]
    lines = [
        "# NASA ATMONTO Minimal Loop Validation",
        "",
        f"- Source catalog: `{report['schema_catalog']}`",
        f"- Schema slice: `{report['schema_slice']}`",
        f"- Extraction schema: `{report['extraction_schema']}`",
        f"- Candidate facts: `{report['candidate_facts']}`",
        f"- Validated facts: `{report['validated_facts']}`",
        f"- ATCSCC records processed: {report['records_processed']}",
        f"- Candidate fact count: {report['candidate_fact_count']}",
        f"- Accepted fact count: {report['accepted_fact_count']}",
        f"- Rejected fact count: {report['rejected_fact_count']}",
        f"- Repaired accepted fact count: {report['repaired_fact_count']}",
        "",
        "## Status Counts",
        "",
    ]
    assert isinstance(status_counts, dict)
    for status, count in sorted(status_counts.items()):
        lines.append(f"- `{status}`: {count}")
    lines.extend(["", "## Error Counts", ""])
    assert isinstance(error_counts, dict)
    if error_counts:
        for error, count in sorted(error_counts.items()):
            lines.append(f"- `{error}`: {count}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This validates schema adherence, identifier repair, datatype coercion, and evidence anchoring.",
            "- Accepted facts remain `bronze_until_reviewed`; this is not an operational truth or safety claim.",
            "- Rejections identify schema/surface-form mismatches that require either extraction changes or explicit profile extensions.",
            "",
        ]
    )
    return "\n".join(lines)


def run_nasa_atmonto_minimal_loop(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    ontology_dir: str | Path = NASA_ATMONTO_DIR,
    atcscc_jsonl: str | Path = DEFAULT_ATCSCC_JSONL,
    extraction_dir: str | Path = DEFAULT_EXTRACTION_DIR,
    limit: int | None = 25,
) -> dict[str, object]:
    repo_root = Path(repo_root).resolve()
    ontology_path = repo_root / ontology_dir if not Path(ontology_dir).is_absolute() else Path(ontology_dir)
    atcscc_path = repo_root / atcscc_jsonl if not Path(atcscc_jsonl).is_absolute() else Path(atcscc_jsonl)
    output_dir = repo_root / extraction_dir if not Path(extraction_dir).is_absolute() else Path(extraction_dir)

    catalog = build_nasa_atmonto_schema_catalog(ontology_path, repo_root=repo_root)
    schema_slice = build_atcscc_schema_slice(catalog)
    extraction_schema = build_extraction_json_schema(schema_slice)

    catalog_path = repo_root / SCHEMA_CATALOG_PATH
    slice_path = repo_root / SCHEMA_SLICE_PATH
    extraction_schema_path = repo_root / EXTRACTION_SCHEMA_PATH
    write_json(catalog_path, catalog)
    write_json(slice_path, schema_slice)
    write_json(extraction_schema_path, extraction_schema)

    rows = read_jsonl(atcscc_path, limit=limit)
    payloads = [extract_atcscc_candidate_payload(row) for row in rows]
    validations = validate_candidate_payloads(payloads, rows, schema_slice)

    candidate_path = output_dir / "atcscc_schema_slice_candidates.jsonl"
    validated_path = output_dir / "atcscc_schema_slice_validated.jsonl"
    write_jsonl(candidate_path, payloads)
    write_jsonl(validated_path, validations)

    status_counts = Counter(str(result["status"]) for result in validations)
    error_counts = Counter(
        error for result in validations for error in result.get("errors", [])  # type: ignore[union-attr]
    )
    repair_counts = Counter(
        repair.split(":", 1)[0]
        for result in validations
        for repair in result.get("repairs", [])  # type: ignore[union-attr]
    )
    accepted = [result for result in validations if result["accepted"]]
    rejected = [result for result in validations if not result["accepted"]]
    report = {
        "source_family": "nasa_atmonto_minimal_loop",
        "records_processed": len(rows),
        "schema_catalog": project_relative_path(catalog_path, repo_root),
        "schema_slice": project_relative_path(slice_path, repo_root),
        "extraction_schema": project_relative_path(extraction_schema_path, repo_root),
        "candidate_facts": project_relative_path(candidate_path, repo_root),
        "validated_facts": project_relative_path(validated_path, repo_root),
        "schema_slice_counts": schema_slice["counts"],
        "candidate_fact_count": sum(len(payload["facts"]) for payload in payloads),
        "validation_count": len(validations),
        "accepted_fact_count": len(accepted),
        "rejected_fact_count": len(rejected),
        "repaired_fact_count": status_counts.get("repaired_accepted", 0),
        "status_counts": dict(sorted(status_counts.items())),
        "error_counts": dict(sorted(error_counts.items())),
        "repair_counts": dict(sorted(repair_counts.items())),
        "missing_schema_targets": schema_slice["missing_targets"],
        "sample_accepted": accepted[:3],
        "sample_rejected": rejected[:3],
        "claim_boundary": (
            "Structural schema validation and evidence anchoring only; accepted ATCSCC facts are "
            "bronze_until_reviewed and not operational ground truth."
        ),
    }
    report_json_path = repo_root / VALIDATION_REPORT_JSON
    report_md_path = repo_root / VALIDATION_REPORT_MD
    write_json(report_json_path, report)
    report_md_path.parent.mkdir(parents=True, exist_ok=True)
    report_md_path.write_text(report_markdown(report) + "\n", encoding="utf-8")
    return {
        "schema_catalog": project_relative_path(catalog_path, repo_root),
        "schema_slice": project_relative_path(slice_path, repo_root),
        "extraction_schema": project_relative_path(extraction_schema_path, repo_root),
        "candidate_facts": project_relative_path(candidate_path, repo_root),
        "validated_facts": project_relative_path(validated_path, repo_root),
        "report_json": project_relative_path(report_json_path, repo_root),
        "report_markdown": project_relative_path(report_md_path, repo_root),
        "records_processed": report["records_processed"],
        "candidate_fact_count": report["candidate_fact_count"],
        "accepted_fact_count": report["accepted_fact_count"],
        "rejected_fact_count": report["rejected_fact_count"],
        "status_counts": report["status_counts"],
        "error_counts": report["error_counts"],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the NASA ATMONTO -> ATCSCC schema-slice extraction loop."
    )
    parser.add_argument("--repo-root", default=PROJECT_ROOT, type=Path)
    parser.add_argument("--ontology-dir", default=NASA_ATMONTO_DIR, type=Path)
    parser.add_argument("--atcscc-jsonl", default=DEFAULT_ATCSCC_JSONL, type=Path)
    parser.add_argument("--extraction-dir", default=DEFAULT_EXTRACTION_DIR, type=Path)
    parser.add_argument("--limit", default=25, type=int)
    parser.add_argument(
        "--all-records",
        action="store_true",
        help="Process every ATCSCC advisory row instead of the default bounded smoke run.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_nasa_atmonto_minimal_loop(
        args.repo_root,
        ontology_dir=args.ontology_dir,
        atcscc_jsonl=args.atcscc_jsonl,
        extraction_dir=args.extraction_dir,
        limit=None if args.all_records else args.limit,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"NASA ATMONTO minimal loop failed: {exc}", file=sys.stderr)
        raise
