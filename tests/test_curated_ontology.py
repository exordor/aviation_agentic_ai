from pathlib import Path

from rdflib import OWL, RDF, RDFS, Graph, URIRef

from aviation_agentic_ai.kg.extraction import load_extraction_profile
from aviation_agentic_ai.ontology.evaluation import local_name


CURATED_ONTOLOGY = Path("data/ontology/curated/06_phak_ch4_0.curated.ttl")
PROFILE = Path("configs/extraction_profile.yaml")


def _load_curated_graph() -> Graph:
    graph = Graph()
    graph.parse(CURATED_ONTOLOGY)
    return graph


def _local_terms(graph: Graph, rdf_type: URIRef) -> set[str]:
    return {
        local_name(subject)
        for subject in graph.subjects(RDF.type, rdf_type)
        if isinstance(subject, URIRef)
    }


def test_curated_ontology_is_parseable_tbox_only() -> None:
    graph = _load_curated_graph()

    assert len(graph) > 0
    assert not list(graph.subjects(RDF.type, OWL.NamedIndividual))


def test_extraction_profile_terms_are_declared_in_curated_ontology() -> None:
    graph = _load_curated_graph()
    profile = load_extraction_profile(PROFILE)

    classes = _local_terms(graph, OWL.Class)
    properties = _local_terms(graph, OWL.ObjectProperty) | _local_terms(graph, OWL.DatatypeProperty)

    assert set(profile.instantiable_classes).issubset(classes)
    assert set(profile.relation_properties).issubset(properties)


def test_curated_ontology_terms_have_human_explanations() -> None:
    graph = _load_curated_graph()
    terms = set(graph.subjects(RDF.type, OWL.Class)) | set(
        graph.subjects(RDF.type, OWL.ObjectProperty)
    )

    missing_label = [local_name(term) for term in terms if not list(graph.objects(term, RDFS.label))]
    missing_comment = [
        local_name(term) for term in terms if not list(graph.objects(term, RDFS.comment))
    ]

    assert missing_label == []
    assert missing_comment == []


def test_curated_relation_properties_have_domain_and_range() -> None:
    graph = _load_curated_graph()
    properties = set(graph.subjects(RDF.type, OWL.ObjectProperty))

    missing_domain = [
        local_name(prop) for prop in properties if not list(graph.objects(prop, RDFS.domain))
    ]
    missing_range = [
        local_name(prop) for prop in properties if not list(graph.objects(prop, RDFS.range))
    ]

    assert missing_domain == []
    assert missing_range == []
