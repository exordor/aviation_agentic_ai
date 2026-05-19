from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from rdflib import Graph, OWL, RDF, URIRef

from aviation_agentic_ai.paths import project_relative_path


@dataclass(frozen=True)
class OntologyStats:
    path: str
    triples: int
    classes: int
    object_properties: int
    datatype_properties: int
    named_individuals: int

    def to_dict(self) -> dict[str, int | str]:
        return asdict(self)


def load_graph(path: str | Path) -> Graph:
    graph = Graph()
    graph.parse(str(path))
    return graph


def collect_stats(path: str | Path) -> OntologyStats:
    ontology_path = Path(path)
    graph = load_graph(ontology_path)
    classes = set(graph.subjects(RDF.type, OWL.Class))
    object_properties = set(graph.subjects(RDF.type, OWL.ObjectProperty))
    datatype_properties = set(graph.subjects(RDF.type, OWL.DatatypeProperty))
    named_individuals = {
        subject
        for subject in graph.subjects(RDF.type, None)
        if isinstance(subject, URIRef)
        and subject not in classes
        and subject not in object_properties
        and subject not in datatype_properties
        and (subject, RDF.type, OWL.Ontology) not in graph
    }
    return OntologyStats(
        path=project_relative_path(ontology_path),
        triples=len(graph),
        classes=len(classes),
        object_properties=len(object_properties),
        datatype_properties=len(datatype_properties),
        named_individuals=len(named_individuals),
    )
