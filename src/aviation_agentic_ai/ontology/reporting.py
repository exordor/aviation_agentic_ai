from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.ontology.stats import OntologyStats


def write_stats_json(stats: OntologyStats, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(stats.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


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
