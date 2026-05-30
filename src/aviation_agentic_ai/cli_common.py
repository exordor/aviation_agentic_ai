from __future__ import annotations

from pathlib import Path

from aviation_agentic_ai.config import load_default_config, resolve_project_path


def default_ontology_path() -> Path:
    config = load_default_config()
    curated = config["paths"].get("curated_ontology")
    if curated:
        curated_path = resolve_project_path(curated)
        if curated_path.exists():
            return curated_path
    return resolve_project_path(config["paths"]["baseline_ontology"])
