from __future__ import annotations

from pathlib import Path

from aviation_agentic_ai.ontology.stats import OntologyStats
from aviation_agentic_ai.utils.io import write_json_document


def write_stats_json(stats: OntologyStats, output_path: str | Path) -> Path:
    return write_json_document(stats.to_dict(), output_path, sort_keys=False)


def write_stats_markdown(stats: OntologyStats, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Ontology Report",
        "",
        f"- Source: `{stats.path}`",
        f"- Triples: {stats.triples}",
        f"- Classes: {stats.classes}",
        f"- Object properties: {stats.object_properties}",
        f"- Datatype properties: {stats.datatype_properties}",
        f"- Named individuals: {stats.named_individuals}",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
