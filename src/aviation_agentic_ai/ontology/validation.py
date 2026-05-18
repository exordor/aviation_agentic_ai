from __future__ import annotations

from pathlib import Path

from rdflib import Graph


def verify_rdf_syntax(file_path: str | Path) -> tuple[bool, str]:
    """Return RDF parse status for a Turtle/RDF file."""
    try:
        graph = Graph()
        graph.parse(str(file_path))
    except Exception as exc:  # rdflib raises several parser-specific exceptions
        return False, str(exc)
    return True, f"Parsed {len(graph)} triples."


def verify_turtle_text(turtle_text: str) -> tuple[bool, str]:
    """Return RDF parse status for Turtle text."""
    try:
        graph = Graph()
        graph.parse(data=turtle_text, format="turtle")
    except Exception as exc:
        return False, str(exc)
    return True, f"Parsed {len(graph)} triples."
