from __future__ import annotations

import json
import random
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from rdflib import Graph, OWL, RDF, RDFS, URIRef

from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.ontology.cq import load_cq_artifact


ONTOLOGY_NAMESPACE = "http://www.example.org/aviation/phak#"
STANDARD_SCHEMA_NAMESPACES = (
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "http://www.w3.org/2000/01/rdf-schema#",
    "http://www.w3.org/2001/XMLSchema#",
    "http://www.w3.org/2002/07/owl#",
)
OPPOSING_RESTRICTION_PAIRS = (
    ("lessThanAtmosphericPressure", "greaterThanAtmosphericPressure"),
    ("belowAltitude", "aboveAltitude"),
    ("heavierThan", "lighterThan"),
)


@dataclass(frozen=True)
class OntologyTerm:
    iri: str
    local_name: str
    kind: str
    normalized: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class CompetencyQuestionRecord:
    cq_id: str
    document_id: str
    page: str
    page_index: int
    question_index: int
    competency_question: str
    key_entities: list[str]
    canonical_entities: list[str]
    odp_hint: str
    odp_id: str
    cq_type: str
    expected_answer: str
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StructuralMetrics:
    path: str
    rdf_valid: bool
    parse_error: str | None
    triples: int
    classes: int
    object_properties: int
    datatype_properties: int
    declared_named_individuals: int
    non_schema_typed_resources: int
    tbox_only: bool
    ontology_declarations: int
    imports: int
    subclass_edges: int
    subproperty_edges: int
    owl_restrictions: int
    some_values_from: int
    equivalent_classes: int
    disjoint_classes: int
    inverse_properties: int
    root_classes: int
    root_class_names: list[str]
    leaf_classes: int
    isolated_classes: int
    isolated_class_names: list[str]
    properties_total: int
    properties_with_domain: int
    properties_with_range: int
    properties_missing_domain: list[str]
    properties_missing_range: list[str]
    class_label_coverage: float
    class_comment_coverage: float
    property_label_coverage: float
    property_comment_coverage: float
    out_of_namespace_schema_terms: int
    out_of_namespace_schema_term_names: list[str]
    rdf_valid_tbox_extraction_prototype: bool
    valid_tbox_prototype: bool
    publication_ready_ontology: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def local_name(node: URIRef | Any) -> str:
    text = str(node)
    if "#" in text:
        return text.rsplit("#", 1)[-1]
    return text.rstrip("/").rsplit("/", 1)[-1]


def normalize_term(text: str) -> str:
    normalized = local_name(text).lower()
    normalized = re.sub(r"^(cl|objprop|dataprop|op|dp)[_:-]+", "", normalized)
    return re.sub(r"[^a-z0-9]+", "", normalized)


def _candidate_normalizations(text: str) -> list[str]:
    normalized = normalize_term(text)
    candidates = [normalized]
    if normalized.endswith("ies") and len(normalized) > 4:
        candidates.append(f"{normalized[:-3]}y")
    if normalized.endswith("s") and len(normalized) > 4:
        candidates.append(normalized[:-1])
    return list(dict.fromkeys(c for c in candidates if c))


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def _is_project_or_standard_iri(node: URIRef) -> bool:
    text = str(node)
    return text.startswith(ONTOLOGY_NAMESPACE) or text.startswith(STANDARD_SCHEMA_NAMESPACES)


def _empty_structural_metrics(path: Path, parse_error: str) -> StructuralMetrics:
    return StructuralMetrics(
        path=project_relative_path(path),
        rdf_valid=False,
        parse_error=parse_error,
        triples=0,
        classes=0,
        object_properties=0,
        datatype_properties=0,
        declared_named_individuals=0,
        non_schema_typed_resources=0,
        tbox_only=False,
        ontology_declarations=0,
        imports=0,
        subclass_edges=0,
        subproperty_edges=0,
        owl_restrictions=0,
        some_values_from=0,
        equivalent_classes=0,
        disjoint_classes=0,
        inverse_properties=0,
        root_classes=0,
        root_class_names=[],
        leaf_classes=0,
        isolated_classes=0,
        isolated_class_names=[],
        properties_total=0,
        properties_with_domain=0,
        properties_with_range=0,
        properties_missing_domain=[],
        properties_missing_range=[],
        class_label_coverage=0.0,
        class_comment_coverage=0.0,
        property_label_coverage=0.0,
        property_comment_coverage=0.0,
        out_of_namespace_schema_terms=0,
        out_of_namespace_schema_term_names=[],
        rdf_valid_tbox_extraction_prototype=False,
        valid_tbox_prototype=False,
        publication_ready_ontology=False,
    )


def collect_structural_metrics(path: str | Path) -> StructuralMetrics:
    ontology_path = Path(path)
    graph = Graph()
    try:
        graph.parse(str(ontology_path))
    except Exception as exc:  # noqa: BLE001 - report parse failures as evaluation data.
        return _empty_structural_metrics(ontology_path, str(exc))

    classes = set(graph.subjects(RDF.type, OWL.Class))
    object_properties = set(graph.subjects(RDF.type, OWL.ObjectProperty))
    datatype_properties = set(graph.subjects(RDF.type, OWL.DatatypeProperty))
    properties = object_properties | datatype_properties
    ontology_declarations = set(graph.subjects(RDF.type, OWL.Ontology))
    restrictions = set(graph.subjects(RDF.type, OWL.Restriction))
    declared_named_individuals = set(graph.subjects(RDF.type, OWL.NamedIndividual))

    schema_terms = classes | properties | ontology_declarations
    out_of_namespace_schema_terms = sorted(
        (
            term
            for term in schema_terms
            if isinstance(term, URIRef) and not _is_project_or_standard_iri(term)
        ),
        key=local_name,
    )
    typed_uri_subjects = {subject for subject in graph.subjects(RDF.type, None) if isinstance(subject, URIRef)}
    non_schema_typed_resources = {
        subject
        for subject in typed_uri_subjects
        if subject not in schema_terms and subject not in declared_named_individuals
    }

    class_parents: dict[URIRef, set[URIRef]] = defaultdict(set)
    class_children: dict[URIRef, set[URIRef]] = defaultdict(set)
    for subject, parent in graph.subject_objects(RDFS.subClassOf):
        if subject in classes and parent in classes:
            class_parents[subject].add(parent)
            class_children[parent].add(subject)

    root_classes = sorted((item for item in classes if not class_parents[item]), key=local_name)
    leaf_classes = sorted((item for item in classes if not class_children[item]), key=local_name)

    used_in_schema: set[URIRef] = set()
    ignored_predicates = {RDF.type, RDFS.label, RDFS.comment}
    for subject, predicate, obj in graph:
        if predicate in ignored_predicates:
            continue
        if subject in classes:
            used_in_schema.add(subject)
        if obj in classes:
            used_in_schema.add(obj)
    isolated_classes = sorted((item for item in classes if item not in used_in_schema), key=local_name)

    properties_with_domain = {item for item in properties if list(graph.objects(item, RDFS.domain))}
    properties_with_range = {item for item in properties if list(graph.objects(item, RDFS.range))}
    properties_missing_domain = sorted(properties - properties_with_domain, key=local_name)
    properties_missing_range = sorted(properties - properties_with_range, key=local_name)

    class_labels = {item for item in classes if list(graph.objects(item, RDFS.label))}
    class_comments = {item for item in classes if list(graph.objects(item, RDFS.comment))}
    property_labels = {item for item in properties if list(graph.objects(item, RDFS.label))}
    property_comments = {item for item in properties if list(graph.objects(item, RDFS.comment))}

    missing_domain_ratio = _safe_ratio(len(properties_missing_domain), len(properties))
    missing_range_ratio = _safe_ratio(len(properties_missing_range), len(properties))
    tbox_only = not declared_named_individuals and not non_schema_typed_resources
    rdf_valid_tbox_extraction_prototype = (
        len(graph) > 0
        and bool(classes)
        and bool(properties)
        and tbox_only
        and len(class_parents) > 0
    )
    valid_tbox_prototype = (
        rdf_valid_tbox_extraction_prototype
        and bool(ontology_declarations)
        and not out_of_namespace_schema_terms
        and _safe_ratio(len(class_labels), len(classes)) >= 0.8
        and _safe_ratio(len(property_labels), len(properties)) >= 0.8
        and missing_domain_ratio <= 0.1
        and missing_range_ratio <= 0.1
    )
    publication_ready_ontology = (
        valid_tbox_prototype
        and bool(ontology_declarations)
        and _safe_ratio(len(class_labels), len(classes)) >= 0.8
        and _safe_ratio(len(property_labels), len(properties)) >= 0.8
        and _safe_ratio(len(class_comments), len(classes)) >= 0.5
    )

    return StructuralMetrics(
        path=project_relative_path(ontology_path),
        rdf_valid=True,
        parse_error=None,
        triples=len(graph),
        classes=len(classes),
        object_properties=len(object_properties),
        datatype_properties=len(datatype_properties),
        declared_named_individuals=len(declared_named_individuals),
        non_schema_typed_resources=len(non_schema_typed_resources),
        tbox_only=tbox_only,
        ontology_declarations=len(ontology_declarations),
        imports=len(list(graph.triples((None, OWL.imports, None)))),
        subclass_edges=sum(len(parents) for parents in class_parents.values()),
        subproperty_edges=len(list(graph.triples((None, RDFS.subPropertyOf, None)))),
        owl_restrictions=len(restrictions),
        some_values_from=len(list(graph.triples((None, OWL.someValuesFrom, None)))),
        equivalent_classes=len(list(graph.triples((None, OWL.equivalentClass, None)))),
        disjoint_classes=len(list(graph.triples((None, OWL.disjointWith, None)))),
        inverse_properties=len(list(graph.triples((None, OWL.inverseOf, None)))),
        root_classes=len(root_classes),
        root_class_names=[local_name(item) for item in root_classes],
        leaf_classes=len(leaf_classes),
        isolated_classes=len(isolated_classes),
        isolated_class_names=[local_name(item) for item in isolated_classes],
        properties_total=len(properties),
        properties_with_domain=len(properties_with_domain),
        properties_with_range=len(properties_with_range),
        properties_missing_domain=[local_name(item) for item in properties_missing_domain],
        properties_missing_range=[local_name(item) for item in properties_missing_range],
        class_label_coverage=_safe_ratio(len(class_labels), len(classes)),
        class_comment_coverage=_safe_ratio(len(class_comments), len(classes)),
        property_label_coverage=_safe_ratio(len(property_labels), len(properties)),
        property_comment_coverage=_safe_ratio(len(property_comments), len(properties)),
        out_of_namespace_schema_terms=len(out_of_namespace_schema_terms),
        out_of_namespace_schema_term_names=[local_name(item) for item in out_of_namespace_schema_terms],
        rdf_valid_tbox_extraction_prototype=rdf_valid_tbox_extraction_prototype,
        valid_tbox_prototype=valid_tbox_prototype,
        publication_ready_ontology=publication_ready_ontology,
    )


def _restriction_records(graph: Graph) -> list[dict[str, URIRef]]:
    records: list[dict[str, URIRef]] = []
    for subject, restriction in graph.subject_objects(RDFS.subClassOf):
        if not isinstance(subject, URIRef):
            continue
        if (restriction, RDF.type, OWL.Restriction) not in graph:
            continue
        properties = [item for item in graph.objects(restriction, OWL.onProperty) if isinstance(item, URIRef)]
        fillers = [
            item
            for item in list(graph.objects(restriction, OWL.someValuesFrom))
            + list(graph.objects(restriction, OWL.allValuesFrom))
            if isinstance(item, URIRef)
        ]
        for prop in properties:
            for filler in fillers:
                records.append({"subject": subject, "property": prop, "filler": filler})
    return records


def collect_semantic_smells(graph: Graph) -> list[dict[str, Any]]:
    smells: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add_smell(
        smell_id: str,
        severity: str,
        title: str,
        evidence: str,
        recommendation: str,
    ) -> None:
        if smell_id in seen:
            return
        seen.add(smell_id)
        smells.append(
            {
                "id": smell_id,
                "severity": severity,
                "title": title,
                "evidence": evidence,
                "recommendation": recommendation,
            }
        )

    restrictions = _restriction_records(graph)
    restrictions_by_subject_filler: dict[tuple[URIRef, URIRef], set[str]] = defaultdict(set)

    for item in restrictions:
        subject = item["subject"]
        prop = item["property"]
        filler = item["filler"]
        subject_name = local_name(subject)
        prop_name = local_name(prop)
        filler_name = local_name(filler)
        restrictions_by_subject_filler[(subject, filler)].add(prop_name)

        if prop_name == "hasQuantity" and subject == filler:
            add_smell(
                smell_id=f"self-quantity-{subject_name}",
                severity="high",
                title="Class has itself as a quantity filler",
                evidence=f"{subject_name} has an owl:someValuesFrom restriction via hasQuantity to itself.",
                recommendation="Model the quantity kind, measured value, and subject class separately.",
            )

        if (
            subject_name == "Cl_PerfectlyDryAir"
            and prop_name in {"hasConstituent", "hasComponent", "composedOf", "hasMember"}
            and filler_name == "Cl_WaterVapor"
        ):
            add_smell(
                smell_id="perfectly-dry-air-has-water-vapor",
                severity="high",
                title="Perfectly dry air is modeled with water vapor",
                evidence=(
                    "Cl_PerfectlyDryAir has a constituent/component restriction "
                    "to Cl_WaterVapor."
                ),
                recommendation="Represent water-vapor exclusion or humidity state explicitly.",
            )

    for (subject, filler), properties in restrictions_by_subject_filler.items():
        subject_name = local_name(subject)
        filler_name = local_name(filler)
        for lower_property, upper_property in OPPOSING_RESTRICTION_PAIRS:
            if lower_property not in properties or upper_property not in properties:
                continue
            add_smell(
                smell_id=f"opposing-{subject_name}-{lower_property}-{upper_property}-{filler_name}",
                severity="high",
                title="Class has opposing restrictions to the same filler",
                evidence=(
                    f"{subject_name} has both {lower_property} and {upper_property} "
                    f"restrictions to {filler_name}."
                ),
                recommendation=(
                    "Split the concept into contextual subclasses or model the comparison "
                    "as a qualified situation."
                ),
            )

    return sorted(smells, key=lambda item: (item["severity"], item["id"]))


def build_quality_gates(
    structural: StructuralMetrics,
    coverage: dict[str, Any],
    semantic_smells: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    high_semantic_smells = [item for item in semantic_smells if item["severity"] == "high"]
    unique_coverage = float(coverage.get("unique_entity_coverage_ratio", 0.0)) if coverage else 0.0

    def gate(
        gate_id: str,
        title: str,
        passed: bool,
        severity: str,
        evidence: str,
    ) -> dict[str, Any]:
        return {
            "id": gate_id,
            "title": title,
            "passed": passed,
            "severity": severity,
            "evidence": evidence,
        }

    return [
        gate(
            "rdf_valid",
            "RDF/Turtle parses successfully",
            structural.rdf_valid,
            "high",
            "RDF parser completed without errors."
            if structural.rdf_valid
            else str(structural.parse_error or "RDF parser failed."),
        ),
        gate(
            "tbox_only",
            "No ABox-like typed resources",
            structural.tbox_only,
            "high",
            f"Non-schema typed resources: {structural.non_schema_typed_resources}; "
            f"declared named individuals: {structural.declared_named_individuals}.",
        ),
        gate(
            "ontology_metadata",
            "Ontology metadata declaration is present",
            structural.ontology_declarations > 0,
            "high",
            f"owl:Ontology declarations: {structural.ontology_declarations}.",
        ),
        gate(
            "annotation_coverage",
            "Minimum human-readable label coverage is met",
            structural.class_label_coverage >= 0.8 and structural.property_label_coverage >= 0.8,
            "high",
            f"Class labels: {structural.class_label_coverage}; "
            f"property labels: {structural.property_label_coverage}.",
        ),
        gate(
            "domain_range_completeness",
            "Property domain/range completeness is acceptable",
            structural.properties_total > 0
            and _safe_ratio(
                structural.properties_total - structural.properties_with_domain,
                structural.properties_total,
            )
            <= 0.1
            and _safe_ratio(
                structural.properties_total - structural.properties_with_range,
                structural.properties_total,
            )
            <= 0.1,
            "high",
            f"Missing domain: {len(structural.properties_missing_domain)}; "
            f"missing range: {len(structural.properties_missing_range)}.",
        ),
        gate(
            "namespace_policy",
            "Schema terms stay inside the configured aviation namespace",
            structural.out_of_namespace_schema_terms == 0,
            "high",
            f"Out-of-namespace schema terms: {structural.out_of_namespace_schema_terms}.",
        ),
        gate(
            "semantic_smells_absent",
            "No high-severity semantic smells are detected",
            not high_semantic_smells,
            "high",
            f"High-severity semantic smells: {len(high_semantic_smells)}.",
        ),
        gate(
            "cq_unique_lexical_coverage",
            "Silver-CQ unique entity lexical coverage is above threshold",
            unique_coverage >= 0.8,
            "medium",
            f"Unique entity coverage ratio: {unique_coverage}.",
        ),
    ]


def build_ontology_terms(graph: Graph) -> list[OntologyTerm]:
    terms: list[OntologyTerm] = []
    for kind, rdf_type in (
        ("class", OWL.Class),
        ("object_property", OWL.ObjectProperty),
        ("datatype_property", OWL.DatatypeProperty),
    ):
        for iri in sorted(set(graph.subjects(RDF.type, rdf_type)), key=local_name):
            if not isinstance(iri, URIRef):
                continue
            name = local_name(iri)
            terms.append(
                OntologyTerm(
                    iri=str(iri),
                    local_name=name,
                    kind=kind,
                    normalized=normalize_term(name),
                )
            )
    return terms


def _term_index(terms: list[OntologyTerm]) -> dict[str, list[OntologyTerm]]:
    index: dict[str, list[OntologyTerm]] = defaultdict(list)
    for term in terms:
        index[term.normalized].append(term)
    return dict(index)


def match_entity(entity: str, term_index: dict[str, list[OntologyTerm]]) -> list[dict[str, str]]:
    for candidate in _candidate_normalizations(entity):
        if candidate in term_index:
            return [
                {**term.to_dict(), "match_type": "normalized"}
                for term in sorted(term_index[candidate], key=lambda item: (item.kind, item.local_name))
            ]

    partial_matches: list[OntologyTerm] = []
    for candidate in _candidate_normalizations(entity):
        if len(candidate) < 6:
            continue
        partial_matches.extend(
            term
            for key, terms in term_index.items()
            if candidate in key or key in candidate
            for term in terms
        )
    unique = {(term.kind, term.local_name): term for term in partial_matches}
    return [
        {**term.to_dict(), "match_type": "partial"}
        for term in sorted(unique.values(), key=lambda item: (item.kind, item.local_name))[:5]
    ]


_EXPECTED_ANSWER_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}


def expected_answer_terms(expected_answer: str) -> list[str]:
    normalized_full = normalize_term(expected_answer)
    terms: list[str] = []
    if normalized_full:
        terms.append(expected_answer)

    for raw in re.split(r"[,;/|()\[\]{}]+|\band\b|\bor\b", expected_answer, flags=re.IGNORECASE):
        phrase = raw.strip(" .:\t\r\n\"'")
        if not phrase:
            continue
        normalized = normalize_term(phrase)
        if not normalized or normalized in _EXPECTED_ANSWER_STOPWORDS:
            continue
        if len(normalized) < 3 and normalized not in {"aoa"}:
            continue
        terms.append(phrase)

    return list(dict.fromkeys(terms))


def _unique_matches(
    values: list[str],
    index: dict[str, list[OntologyTerm]],
) -> tuple[list[dict[str, str]], int, int]:
    matches_by_key: dict[tuple[str, str], dict[str, str]] = {}
    matched_values = 0
    total_values = 0
    for value in values:
        if not normalize_term(value):
            continue
        total_values += 1
        matches = match_entity(value, index)
        if matches:
            matched_values += 1
        for match in matches:
            matches_by_key[(match["kind"], match["iri"])] = match
    return (
        sorted(matches_by_key.values(), key=lambda item: (item["kind"], item["local_name"])),
        matched_values,
        total_values,
    )


def _subclass_related(
    graph: Graph,
    left: URIRef,
    right: URIRef,
    ancestor_cache: dict[URIRef, set[URIRef]] | None = None,
) -> bool:
    if left == right:
        return True
    if ancestor_cache is None:
        ancestor_cache = {}
    if left not in ancestor_cache:
        ancestor_cache[left] = {
            item for item in graph.transitive_objects(left, RDFS.subClassOf) if isinstance(item, URIRef)
        }
    if right not in ancestor_cache:
        ancestor_cache[right] = {
            item for item in graph.transitive_objects(right, RDFS.subClassOf) if isinstance(item, URIRef)
        }
    left_ancestors = ancestor_cache[left]
    right_ancestors = ancestor_cache[right]
    return right in left_ancestors or left in right_ancestors


def _class_property_connected(
    graph: Graph,
    class_iri: URIRef,
    property_iri: URIRef,
    restrictions: list[dict[str, URIRef]] | None = None,
    ancestor_cache: dict[URIRef, set[URIRef]] | None = None,
) -> bool:
    for predicate in (RDFS.domain, RDFS.range):
        for endpoint in graph.objects(property_iri, predicate):
            if isinstance(endpoint, URIRef) and _subclass_related(
                graph, class_iri, endpoint, ancestor_cache
            ):
                return True

    for restriction in restrictions if restrictions is not None else _restriction_records(graph):
        if restriction["property"] != property_iri:
            continue
        if _subclass_related(graph, class_iri, restriction["subject"], ancestor_cache):
            return True
        if _subclass_related(graph, class_iri, restriction["filler"], ancestor_cache):
            return True
    return False


def _class_class_connected(
    graph: Graph,
    left: URIRef,
    right: URIRef,
    restrictions: list[dict[str, URIRef]] | None = None,
    ancestor_cache: dict[URIRef, set[URIRef]] | None = None,
) -> bool:
    if _subclass_related(graph, left, right, ancestor_cache):
        return True
    for restriction in restrictions if restrictions is not None else _restriction_records(graph):
        subject = restriction["subject"]
        filler = restriction["filler"]
        if _subclass_related(graph, left, subject, ancestor_cache) and _subclass_related(
            graph, right, filler, ancestor_cache
        ):
            return True
        if _subclass_related(graph, right, subject, ancestor_cache) and _subclass_related(
            graph, left, filler, ancestor_cache
        ):
            return True
    return False


def analyze_answerability_metrics(
    cqs: list[CompetencyQuestionRecord],
    graph: Graph,
) -> dict[str, Any]:
    terms = build_ontology_terms(graph)
    index = _term_index(terms)
    restrictions = _restriction_records(graph)
    ancestor_cache: dict[URIRef, set[URIRef]] = {}
    per_cq: list[dict[str, Any]] = []
    totals = Counter()

    for cq in cqs:
        entity_values = cq_entities_for_matching(cq)
        answer_values = expected_answer_terms(cq.expected_answer)
        entity_matches, matched_entity_values, total_entity_values = _unique_matches(entity_values, index)
        answer_matches, matched_answer_values, total_answer_values = _unique_matches(answer_values, index)

        all_matches_by_iri = {match["iri"]: match for match in entity_matches + answer_matches}
        class_matches = [match for match in all_matches_by_iri.values() if match["kind"] == "class"]
        property_matches = [
            match
            for match in all_matches_by_iri.values()
            if match["kind"] in {"object_property", "datatype_property"}
        ]
        answer_property_matches = [
            match
            for match in answer_matches
            if match["kind"] in {"object_property", "datatype_property"}
        ]

        connected_pairs: list[dict[str, str]] = []
        for class_match in class_matches:
            class_iri = URIRef(class_match["iri"])
            for property_match in property_matches:
                property_iri = URIRef(property_match["iri"])
                if _class_property_connected(
                    graph,
                    class_iri,
                    property_iri,
                    restrictions,
                    ancestor_cache,
                ):
                    connected_pairs.append(
                        {
                            "class": class_match["local_name"],
                            "property": property_match["local_name"],
                        }
                    )

        connected_class_pairs: list[dict[str, str]] = []
        for left_index, left_match in enumerate(class_matches):
            for right_match in class_matches[left_index + 1 :]:
                if _class_class_connected(
                    graph,
                    URIRef(left_match["iri"]),
                    URIRef(right_match["iri"]),
                    restrictions,
                    ancestor_cache,
                ):
                    connected_class_pairs.append(
                        {
                            "source_class": left_match["local_name"],
                            "target_class": right_match["local_name"],
                        }
                    )

        expected_answer_coverage = _safe_ratio(matched_answer_values, total_answer_values)
        entity_coverage = _safe_ratio(matched_entity_values, total_entity_values)
        has_connected_property_support = bool(connected_pairs)
        has_class_only_support = bool(class_matches) and (len(class_matches) == 1 or bool(connected_class_pairs))

        if matched_answer_values == 0 and total_answer_values > 0:
            support = "no"
            rationale = "Expected-answer terms did not map to ontology schema terms."
        elif property_matches:
            if has_connected_property_support and entity_coverage == 1.0 and expected_answer_coverage == 1.0:
                support = "yes"
                rationale = "Matched class/property terms have domain, range, or restriction support."
            elif has_connected_property_support:
                support = "partial"
                rationale = "Some matched class/property terms are structurally connected."
            else:
                support = "no"
                rationale = "Matched class/property terms were not connected by domain, range, or restrictions."
        elif has_class_only_support and entity_coverage == 1.0 and expected_answer_coverage == 1.0:
            support = "yes"
            rationale = "Matched class terms are present and structurally plausible for a class-level CQ."
        elif entity_matches or answer_matches:
            support = "partial"
            rationale = "Some expected-answer or key terms mapped, but structural support is incomplete."
        else:
            support = "no"
            rationale = "No CQ terms mapped to ontology schema terms."

        totals["expected_answer_terms_total"] += total_answer_values
        totals["matched_expected_answer_terms"] += matched_answer_values
        totals["entity_values_total"] += total_entity_values
        totals["matched_entity_values"] += matched_entity_values
        totals["cqs_with_property_or_relation_match"] += int(bool(property_matches))
        totals["cqs_with_answer_property_match"] += int(bool(answer_property_matches))
        totals["cqs_with_connected_class_property"] += int(has_connected_property_support)
        totals["object_property_matches"] += sum(1 for match in property_matches if match["kind"] == "object_property")
        totals["datatype_property_matches"] += sum(1 for match in property_matches if match["kind"] == "datatype_property")
        totals[support] += 1

        per_cq.append(
            {
                "cq_id": cq.cq_id,
                "support": support,
                "expected_answer_terms_total": total_answer_values,
                "matched_expected_answer_terms": matched_answer_values,
                "expected_answer_term_coverage_ratio": expected_answer_coverage,
                "key_entity_terms_total": total_entity_values,
                "matched_key_entity_terms": matched_entity_values,
                "key_entity_term_coverage_ratio": entity_coverage,
                "matched_classes": sorted(match["local_name"] for match in class_matches),
                "matched_properties": sorted(match["local_name"] for match in property_matches),
                "matched_object_properties": sorted(
                    match["local_name"] for match in property_matches if match["kind"] == "object_property"
                ),
                "matched_datatype_properties": sorted(
                    match["local_name"] for match in property_matches if match["kind"] == "datatype_property"
                ),
                "connected_class_property_pairs": connected_pairs,
                "connected_class_pairs": connected_class_pairs,
                "rationale": rationale,
            }
        )

    score = totals["yes"] + (0.5 * totals["partial"])
    return {
        "metric_standard": (
            "Deterministic silver heuristic using normalized CQ terms and OWL schema "
            "structure; not gold-standard answerability."
        ),
        "cqs_total": len(cqs),
        "yes": totals["yes"],
        "partial": totals["partial"],
        "no": totals["no"],
        "support_score": _safe_ratio(score, len(cqs)),
        "expected_answer_terms_total": totals["expected_answer_terms_total"],
        "matched_expected_answer_terms": totals["matched_expected_answer_terms"],
        "expected_answer_term_coverage_ratio": _safe_ratio(
            totals["matched_expected_answer_terms"],
            totals["expected_answer_terms_total"],
        ),
        "key_entity_term_coverage_ratio": _safe_ratio(
            totals["matched_entity_values"],
            totals["entity_values_total"],
        ),
        "property_relation_coverage_ratio": _safe_ratio(
            totals["cqs_with_property_or_relation_match"],
            len(cqs),
        ),
        "answer_property_coverage_ratio": _safe_ratio(
            totals["cqs_with_answer_property_match"],
            len(cqs),
        ),
        "connected_class_property_ratio": _safe_ratio(
            totals["cqs_with_connected_class_property"],
            len(cqs),
        ),
        "cqs_with_property_or_relation_match": totals["cqs_with_property_or_relation_match"],
        "cqs_with_answer_property_match": totals["cqs_with_answer_property_match"],
        "cqs_with_connected_class_property": totals["cqs_with_connected_class_property"],
        "object_property_matches": totals["object_property_matches"],
        "datatype_property_matches": totals["datatype_property_matches"],
        "per_cq": per_cq,
    }


def load_cqs(path: str | Path) -> list[CompetencyQuestionRecord]:
    cq_path = Path(path)
    raw = load_cq_artifact(cq_path)

    records: list[CompetencyQuestionRecord] = []
    for document_id, pages in raw.items():
        if not isinstance(pages, dict):
            continue
        for page, questions in pages.items():
            if not isinstance(questions, list):
                continue
            page_index = int(page) if str(page).isdigit() else -1
            for index, item in enumerate(questions):
                if not isinstance(item, dict):
                    continue
                records.append(
                    CompetencyQuestionRecord(
                        cq_id=str(item["id"]),
                        document_id=str(document_id),
                        page=str(page),
                        page_index=page_index,
                        question_index=index,
                        competency_question=str(item.get("competency_question", "")),
                        key_entities=[str(entity) for entity in item.get("key_entities", [])],
                        canonical_entities=[
                            str(entity) for entity in item.get("canonical_entities", [])
                        ],
                        odp_hint=str(item.get("odp_hint", "")),
                        odp_id=str(item.get("odp_id", "")),
                        cq_type=str(item.get("cq_type", "")),
                        expected_answer=str(item.get("expected_answer", "")),
                        status=str(item.get("status", "")),
                    )
                )
    return records


def cq_entities_for_matching(cq: CompetencyQuestionRecord) -> list[str]:
    return cq.canonical_entities or cq.key_entities


def analyze_cq_coverage(cqs: list[CompetencyQuestionRecord], graph: Graph) -> dict[str, Any]:
    terms = build_ontology_terms(graph)
    index = _term_index(terms)
    page_stats: dict[str, Counter[str]] = defaultdict(Counter)
    odp_stats: dict[str, Counter[str]] = defaultdict(Counter)
    entity_stats: dict[str, Counter[str]] = defaultdict(Counter)

    matched_mentions = 0
    total_mentions = 0
    for cq in cqs:
        page_stats[cq.page]["cqs"] += 1
        odp_key = cq.odp_id or "unspecified"
        odp_stats[odp_key]["cqs"] += 1
        for entity in cq_entities_for_matching(cq):
            total_mentions += 1
            matches = match_entity(entity, index)
            matched = bool(matches)
            if matched:
                matched_mentions += 1
            page_stats[cq.page]["entity_mentions"] += 1
            page_stats[cq.page]["matched_entity_mentions"] += int(matched)
            odp_stats[odp_key]["entity_mentions"] += 1
            odp_stats[odp_key]["matched_entity_mentions"] += int(matched)
            entity_key = entity.strip().lower()
            entity_stats[entity_key]["count"] += 1
            entity_stats[entity_key]["matched"] += int(matched)

    def finalize_group_stats(stats: dict[str, Counter[str]]) -> dict[str, dict[str, Any]]:
        output: dict[str, dict[str, Any]] = {}
        for key, counter in sorted(stats.items()):
            mentions = int(counter["entity_mentions"])
            matched = int(counter["matched_entity_mentions"])
            output[key] = {
                "cqs": int(counter["cqs"]),
                "entity_mentions": mentions,
                "matched_entity_mentions": matched,
                "coverage_ratio": _safe_ratio(matched, mentions),
            }
        return output

    unique_entities = len(entity_stats)
    unique_matched_entities = sum(1 for counter in entity_stats.values() if counter["matched"] > 0)
    top_entities = [
        {
            "entity": entity,
            "count": int(counter["count"]),
            "matched_mentions": int(counter["matched"]),
            "matched": counter["matched"] > 0,
        }
        for entity, counter in sorted(
            entity_stats.items(), key=lambda item: (-item[1]["count"], item[0])
        )[:40]
    ]
    top_missing_entities = [
        {"entity": entity, "count": int(counter["count"])}
        for entity, counter in sorted(
            entity_stats.items(), key=lambda item: (-item[1]["count"], item[0])
        )
        if counter["matched"] == 0
    ][:40]

    answerability_metrics = analyze_answerability_metrics(cqs, graph)

    return {
        "cqs_total": len(cqs),
        "entity_mentions_total": total_mentions,
        "matched_entity_mentions": matched_mentions,
        "entity_mention_coverage_ratio": _safe_ratio(matched_mentions, total_mentions),
        "unique_entities_total": unique_entities,
        "unique_matched_entities": unique_matched_entities,
        "unique_entity_coverage_ratio": _safe_ratio(unique_matched_entities, unique_entities),
        "by_page": finalize_group_stats(page_stats),
        "by_odp_id": finalize_group_stats(odp_stats),
        "top_entities": top_entities,
        "top_missing_entities": top_missing_entities,
        "answerability_metrics": answerability_metrics,
    }


def stratified_sample_cqs(
    cqs: list[CompetencyQuestionRecord], sample_size: int, seed: int
) -> list[CompetencyQuestionRecord]:
    if sample_size <= 0 or not cqs:
        return []
    if sample_size >= len(cqs):
        return sorted(cqs, key=lambda item: item.cq_id)

    rng = random.Random(seed)
    selected: list[CompetencyQuestionRecord] = []
    selected_ids: set[str] = set()

    def add_one(group: list[CompetencyQuestionRecord]) -> None:
        if len(selected) >= sample_size:
            return
        choices = [item for item in group if item.cq_id not in selected_ids]
        if not choices:
            return
        item = rng.choice(sorted(choices, key=lambda record: record.cq_id))
        selected.append(item)
        selected_ids.add(item.cq_id)

    by_page: dict[str, list[CompetencyQuestionRecord]] = defaultdict(list)
    by_odp: dict[str, list[CompetencyQuestionRecord]] = defaultdict(list)
    for cq in cqs:
        by_page[cq.page].append(cq)
        by_odp[cq.odp_id or "unspecified"].append(cq)

    for page in sorted(by_page, key=lambda value: int(value) if value.isdigit() else value):
        add_one(by_page[page])
    for odp_id, _ in Counter(cq.odp_id or "unspecified" for cq in cqs).most_common():
        add_one(by_odp[odp_id])

    remaining = [item for item in sorted(cqs, key=lambda record: record.cq_id) if item.cq_id not in selected_ids]
    rng.shuffle(remaining)
    for item in remaining:
        if len(selected) >= sample_size:
            break
        selected.append(item)
        selected_ids.add(item.cq_id)

    return sorted(selected, key=lambda item: item.cq_id)


def _terms_by_iri(graph: Graph) -> dict[str, OntologyTerm]:
    return {term.iri: term for term in build_ontology_terms(graph)}


def build_cq_context(cq: CompetencyQuestionRecord, graph: Graph) -> dict[str, Any]:
    terms = build_ontology_terms(graph)
    index = _term_index(terms)
    by_iri = _terms_by_iri(graph)
    matched_context: list[dict[str, Any]] = []
    unmatched_entities: list[str] = []

    for entity in cq_entities_for_matching(cq):
        matches = match_entity(entity, index)
        if not matches:
            unmatched_entities.append(entity)
            continue
        for match in matches:
            iri = URIRef(match["iri"])
            parents = [
                local_name(parent)
                for parent in graph.objects(iri, RDFS.subClassOf)
                if isinstance(parent, URIRef) and str(parent) in by_iri
            ]
            children = [
                local_name(child)
                for child in graph.subjects(RDFS.subClassOf, iri)
                if isinstance(child, URIRef) and str(child) in by_iri
            ]
            domains = [local_name(item) for item in graph.objects(iri, RDFS.domain) if isinstance(item, URIRef)]
            ranges = [local_name(item) for item in graph.objects(iri, RDFS.range) if isinstance(item, URIRef)]
            related_properties = [
                local_name(prop)
                for prop in set(graph.subjects(RDFS.domain, iri)) | set(graph.subjects(RDFS.range, iri))
                if isinstance(prop, URIRef)
            ]
            matched_context.append(
                {
                    "entity": entity,
                    "term": match["local_name"],
                    "kind": match["kind"],
                    "match_type": match["match_type"],
                    "parents": sorted(parents)[:10],
                    "children": sorted(children)[:10],
                    "domain": sorted(domains)[:10],
                    "range": sorted(ranges)[:10],
                    "related_properties": sorted(related_properties)[:15],
                }
            )

    return {
        "cq_id": cq.cq_id,
        "matched_context": matched_context[:25],
        "unmatched_entities": unmatched_entities,
    }


def build_ai_review_prompt(cq: CompetencyQuestionRecord, context: dict[str, Any]) -> str:
    payload = {
        "cq_id": cq.cq_id,
        "competency_question": cq.competency_question,
        "expected_answer": cq.expected_answer,
        "key_entities": cq.key_entities,
        "canonical_entities": cq.canonical_entities,
        "odp_hint": cq.odp_hint,
        "odp_id": cq.odp_id,
        "cq_type": cq.cq_type,
        "ontology_context": context,
    }
    schema = {
        "supported": "yes | partial | no",
        "confidence": "number from 0.0 to 1.0",
        "matched_terms": ["ontology terms that support the CQ"],
        "missing_terms": ["terms or relations missing from the ontology"],
        "rationale": "brief evidence-grounded assessment",
        "suggested_fixes": ["specific ontology improvements, if any"],
    }
    return (
        "You are evaluating whether an aviation OWL ontology can support an "
        "AI-generated silver Competency Question. Use only the provided ontology "
        "context. Do not assume domain facts that are absent from the context. "
        "Return JSON only using this schema:\n"
        f"{json.dumps(schema, indent=2)}\n\n"
        f"Evaluation input:\n{json.dumps(payload, indent=2)}\n"
    )


def _extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("AI reviewer response did not contain a JSON object.")
    return json.loads(stripped[start : end + 1])


def parse_ai_review_response(cq_id: str, text: str) -> dict[str, Any]:
    raw = _extract_json_object(text)
    supported = str(raw.get("supported", "partial")).strip().lower()
    if supported not in {"yes", "partial", "no"}:
        supported = "partial"
    try:
        confidence = float(raw.get("confidence", 0.0))
    except (TypeError, ValueError):
        confidence = 0.0
    confidence = min(1.0, max(0.0, confidence))

    def string_list(value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        if value:
            return [str(value)]
        return []

    return {
        "cq_id": cq_id,
        "supported": supported,
        "confidence": confidence,
        "matched_terms": string_list(raw.get("matched_terms", [])),
        "missing_terms": string_list(raw.get("missing_terms", [])),
        "rationale": str(raw.get("rationale", "")),
        "suggested_fixes": string_list(raw.get("suggested_fixes", [])),
    }


def _invoke_ai_review(prompt: str, max_tokens: int = 1000) -> str:
    try:
        from langchain_core.messages import HumanMessage
    except ImportError as exc:
        raise RuntimeError(
            "AI ontology evaluation requires optional ontology-generation dependencies. "
            "Install with: uv sync --extra ontology-generation"
        ) from exc

    from aviation_agentic_ai.llm.providers import get_llm

    llm = get_llm(temperature=0.0, max_tokens=max_tokens)
    response = llm.invoke([HumanMessage(content=prompt)])
    return str(getattr(response, "content", response)).strip()


def summarize_ai_reviews(results: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(result["supported"] for result in results)
    score_values = {"yes": 1.0, "partial": 0.5, "no": 0.0}
    score = sum(score_values.get(result["supported"], 0.0) for result in results)
    confidence = sum(float(result.get("confidence", 0.0)) for result in results)
    return {
        "reviewed_cqs": len(results),
        "yes": counts["yes"],
        "partial": counts["partial"],
        "no": counts["no"],
        "support_score": _safe_ratio(score, len(results)),
        "average_confidence": _safe_ratio(confidence, len(results)),
    }


def build_judgment(
    structural: StructuralMetrics, quality_gates: list[dict[str, Any]]
) -> dict[str, Any]:
    rationale: list[str] = []
    failed_high_gates = [
        gate for gate in quality_gates if gate["severity"] == "high" and not gate["passed"]
    ]
    failed_gate_ids = [gate["id"] for gate in failed_high_gates]
    valid_tbox_prototype = structural.valid_tbox_prototype and not failed_high_gates
    publication_ready_ontology = (
        structural.publication_ready_ontology
        and valid_tbox_prototype
        and all(gate["passed"] for gate in quality_gates)
    )

    if structural.rdf_valid_tbox_extraction_prototype:
        rationale.append("The ontology is an RDF-valid TBox extraction prototype.")
    else:
        rationale.append("The ontology does not yet satisfy the RDF-valid TBox extraction threshold.")
    if valid_tbox_prototype:
        rationale.append("All high-severity ontology quality gates passed.")
    else:
        rationale.append(
            "The ontology is not a valid TBox prototype under the configured quality gates."
        )
    if structural.tbox_only:
        rationale.append("No ABox individuals were detected in the ontology.")
    else:
        rationale.append("ABox-like typed resources were detected and should be reviewed.")
    if failed_gate_ids:
        rationale.append(f"Failed high-severity quality gates: {', '.join(failed_gate_ids)}.")
    if structural.properties_missing_domain or structural.properties_missing_range:
        rationale.append("Some properties are missing domain or range declarations.")
    if structural.class_label_coverage == 0.0 and structural.property_label_coverage == 0.0:
        rationale.append("Human-readable labels are missing for classes and properties.")
    if structural.ontology_declarations == 0:
        rationale.append("No owl:Ontology metadata declaration is present.")
    return {
        "rdf_valid_tbox_extraction_prototype": structural.rdf_valid_tbox_extraction_prototype,
        "valid_tbox_prototype": valid_tbox_prototype,
        "publication_ready_ontology": publication_ready_ontology,
        "failed_high_quality_gates": failed_gate_ids,
        "rationale": rationale,
    }


def evaluate_ontology(
    ontology_file: str | Path,
    cq_file: str | Path,
    output_dir: str | Path,
    sample_size: int = 50,
    seed: int = 42,
    ai_review: bool = True,
    report_name: str = "ontology_evaluation",
) -> dict[str, Any]:
    ontology_path = Path(ontology_file)
    cq_path = Path(cq_file)
    report_dir = Path(output_dir)
    report_stem = report_name.strip() or "ontology_evaluation"

    structural = collect_structural_metrics(ontology_path)
    graph = Graph()
    if structural.rdf_valid:
        graph.parse(str(ontology_path))

    cqs = load_cqs(cq_path)
    coverage = analyze_cq_coverage(cqs, graph) if structural.rdf_valid else {}
    semantic_smells = collect_semantic_smells(graph) if structural.rdf_valid else []
    quality_gates = build_quality_gates(structural, coverage, semantic_smells)
    sample = stratified_sample_cqs(cqs, sample_size=sample_size, seed=seed)

    ai_results: list[dict[str, Any]] = []
    if ai_review:
        if not structural.rdf_valid:
            raise RuntimeError("Cannot run AI review because the ontology did not parse.")
        for cq in sample:
            context = build_cq_context(cq, graph)
            prompt = build_ai_review_prompt(cq, context)
            ai_results.append(parse_ai_review_response(cq.cq_id, _invoke_ai_review(prompt)))

    ai_review_summary = summarize_ai_reviews(ai_results)
    result = {
        "metadata": {
            "ontology_file": project_relative_path(ontology_path),
            "cq_file": project_relative_path(cq_path),
            "output_dir": project_relative_path(report_dir),
            "report_name": report_stem,
            "cq_standard": "AI-generated silver CQs, not domain-expert gold annotations",
            "sample_size_requested": sample_size,
            "sample_size_actual": len(sample),
            "seed": seed,
            "ai_review_enabled": ai_review,
        },
        "structural_metrics": structural.to_dict(),
        "quality_gates": quality_gates,
        "semantic_smells": semantic_smells,
        "cq_coverage": coverage,
        "ai_review": {
            "enabled": ai_review,
            "sampled_cq_ids": [cq.cq_id for cq in sample],
            "summary": ai_review_summary,
            "results": ai_results,
        },
        "judgment": build_judgment(structural, quality_gates),
    }

    json_path = report_dir / f"{report_stem}.json"
    markdown_path = report_dir / f"{report_stem}.md"
    write_evaluation_json(result, json_path)
    write_evaluation_markdown(result, markdown_path)
    result["output_paths"] = {
        "json": project_relative_path(json_path),
        "markdown": project_relative_path(markdown_path),
    }
    return result


def write_evaluation_json(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return path


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def write_evaluation_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    structural = result["structural_metrics"]
    quality_gates = result.get("quality_gates", [])
    semantic_smells = result.get("semantic_smells", [])
    coverage = result.get("cq_coverage", {})
    ai_review = result["ai_review"]
    judgment = result["judgment"]

    top_missing = coverage.get("top_missing_entities", [])[:10] if coverage else []
    answerability = coverage.get("answerability_metrics", {}) if coverage else {}
    missing_entities = ", ".join(item["entity"] for item in top_missing) or "None"
    missing_domain = ", ".join(structural["properties_missing_domain"]) or "None"
    missing_range = ", ".join(structural["properties_missing_range"]) or "None"

    lines = [
        "# Ontology Evaluation Report",
        "",
        f"- Ontology: `{result['metadata']['ontology_file']}`",
        f"- CQ file: `{result['metadata']['cq_file']}`",
        "- CQ standard: AI-generated silver CQs, not domain-expert gold annotations",
        f"- AI review enabled: {_yes_no(ai_review['enabled'])}",
        "",
        "## Overall Judgment",
        "",
        f"- RDF-valid TBox extraction prototype: "
        f"{_yes_no(judgment['rdf_valid_tbox_extraction_prototype'])}",
        f"- Valid TBox prototype: {_yes_no(judgment['valid_tbox_prototype'])}",
        f"- Publication-ready ontology: {_yes_no(judgment['publication_ready_ontology'])}",
        "",
        *[f"- {item}" for item in judgment["rationale"]],
        "",
        "## Structural Metrics",
        "",
        f"- RDF valid: {_yes_no(structural['rdf_valid'])}",
        f"- Triples: {structural['triples']}",
        f"- Classes: {structural['classes']}",
        f"- Object properties: {structural['object_properties']}",
        f"- Datatype properties: {structural['datatype_properties']}",
        f"- Declared named individuals: {structural['declared_named_individuals']}",
        f"- Non-schema typed resources: {structural['non_schema_typed_resources']}",
        f"- TBox only: {_yes_no(structural['tbox_only'])}",
        f"- Root classes: {structural['root_classes']}",
        f"- Leaf classes: {structural['leaf_classes']}",
        f"- Isolated classes: {structural['isolated_classes']}",
        f"- OWL restrictions: {structural['owl_restrictions']}",
        f"- `owl:someValuesFrom`: {structural['some_values_from']}",
        f"- Class label coverage: {structural['class_label_coverage']}",
        f"- Class comment coverage: {structural['class_comment_coverage']}",
        f"- Property label coverage: {structural['property_label_coverage']}",
        f"- Property comment coverage: {structural['property_comment_coverage']}",
        f"- Out-of-namespace schema terms: {structural['out_of_namespace_schema_terms']}",
        f"- Properties missing domain: {missing_domain}",
        f"- Properties missing range: {missing_range}",
        "",
        "## Quality Gates",
        "",
        "| Gate | Status | Severity | Evidence |",
        "| --- | --- | --- | --- |",
        *[
            f"| {gate['title']} | {'pass' if gate['passed'] else 'fail'} | "
            f"{gate['severity']} | {gate['evidence']} |"
            for gate in quality_gates
        ],
        "",
        "## Semantic Smell Checks",
        "",
        f"- Total smells: {len(semantic_smells)}",
        f"- High-severity smells: {sum(1 for item in semantic_smells if item['severity'] == 'high')}",
        "",
        *[
            f"- {item['severity']}: {item['title']} ({item['evidence']})"
            for item in semantic_smells[:10]
        ],
        "",
        "## CQ Lexical Coverage",
        "",
        f"- CQs: {coverage.get('cqs_total', 0)}",
        f"- Entity mentions: {coverage.get('matched_entity_mentions', 0)} / "
        f"{coverage.get('entity_mentions_total', 0)}",
        f"- Entity mention coverage ratio: {coverage.get('entity_mention_coverage_ratio', 0.0)}",
        f"- Unique entity coverage ratio: {coverage.get('unique_entity_coverage_ratio', 0.0)}",
        f"- Top missing entities: {missing_entities}",
        "",
        "## Silver Answerability Heuristics",
        "",
        "- Standard: deterministic silver heuristics from normalized CQ terms and OWL schema structure; not gold-standard answerability.",
        f"- Yes / partial / no: {answerability.get('yes', 0)} / "
        f"{answerability.get('partial', 0)} / {answerability.get('no', 0)}",
        f"- Heuristic support score: {answerability.get('support_score', 0.0)}",
        f"- Expected-answer term coverage ratio: "
        f"{answerability.get('expected_answer_term_coverage_ratio', 0.0)}",
        f"- Property/relation coverage ratio: "
        f"{answerability.get('property_relation_coverage_ratio', 0.0)}",
        f"- Answer property coverage ratio: "
        f"{answerability.get('answer_property_coverage_ratio', 0.0)}",
        f"- Connected class/property ratio: "
        f"{answerability.get('connected_class_property_ratio', 0.0)}",
        f"- Object property matches: {answerability.get('object_property_matches', 0)}",
        f"- Datatype property matches: {answerability.get('datatype_property_matches', 0)}",
        "",
        "## AI Review",
        "",
    ]
    if ai_review["enabled"]:
        summary = ai_review["summary"]
        lines.extend(
            [
                f"- Reviewed CQs: {summary['reviewed_cqs']}",
                f"- Yes / partial / no: {summary['yes']} / {summary['partial']} / {summary['no']}",
                f"- Support score: {summary['support_score']}",
                f"- Average confidence: {summary['average_confidence']}",
            ]
        )
    else:
        lines.append("- AI review skipped. Run with `--ai-review` after configuring a rotated API key.")

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
