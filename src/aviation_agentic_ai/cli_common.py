from __future__ import annotations

from pathlib import Path

from aviation_agentic_ai.chunking.chunks import chunk_output_path_for_strategy
from aviation_agentic_ai.config import load_default_config, resolve_project_path


def _configured_path(key: str, fallback: str) -> Path:
    config = load_default_config()
    paths = config.get("paths", {})
    value = paths.get(key) if isinstance(paths, dict) else None
    return resolve_project_path(value or fallback)


def default_ontology_path() -> Path:
    config = load_default_config()
    paths = config.get("paths", {})
    curated = paths.get("curated_ontology") if isinstance(paths, dict) else None
    if curated:
        curated_path = resolve_project_path(curated)
        if curated_path.exists():
            return curated_path
    baseline = paths.get("baseline_ontology") if isinstance(paths, dict) else None
    return resolve_project_path(baseline or "data/ontology/baseline/06_phak_ch4_0.ttl")


def default_benchmark_chunks() -> list[Path]:
    config = load_default_config()
    paths = config.get("paths", {})
    chunks_file = paths.get("chunks_file") if isinstance(paths, dict) else None
    default_chunks = resolve_project_path(chunks_file or "data/chunks/06_phak_ch4_0.jsonl")
    structure_chunks = chunk_output_path_for_strategy(default_chunks, "structure_aware")
    return [path for path in (structure_chunks, default_chunks) if path.exists()]


def default_benchmark_v2_gold_labels() -> Path:
    return _configured_path(
        "benchmark_v2_gold_labels",
        "data/cqs/06_phak_ch4_0.benchmark_v2.gold.json",
    )


def default_benchmark_v2_reviewed_gold_labels() -> Path:
    return _configured_path(
        "benchmark_v2_reviewed_gold_labels",
        "data/cqs/06_phak_ch4_0.benchmark_v2.reviewed.gold.json",
    )


def default_benchmark_v2_reviewed_subset_gold_labels() -> Path:
    return _configured_path(
        "benchmark_v2_reviewed_subset_gold_labels",
        "data/cqs/06_phak_ch4_0.benchmark_v2.reviewed_subset.gold.json",
    )


def default_answer_eval_subset_gold_labels() -> Path:
    return _configured_path(
        "answer_eval_subset_gold_labels",
        "data/cqs/06_phak_ch4_0.answer_eval_subset.gold.json",
    )


def default_boundary_cqs() -> Path:
    return _configured_path(
        "boundary_cqs",
        "data/cqs/06_phak_ch4_0.boundary.json",
    )


def default_gold_labels() -> Path:
    return _configured_path(
        "gold_labels",
        "data/cqs/06_phak_ch4_0.gold.json",
    )


def default_expanded_gold_labels() -> Path:
    return _configured_path(
        "expanded_gold_labels",
        "data/cqs/06_phak_ch4_0.expanded.gold.json",
    )


def default_structure_aware_chunks() -> Path:
    return _configured_path(
        "structure_aware_chunks",
        "data/chunks/06_phak_ch4_0.structure_aware.jsonl",
    )


def default_structure_aware_kg() -> Path:
    return _configured_path(
        "structure_aware_kg",
        "data/kg/06_phak_ch4_0.structure_aware.kg.jsonl",
    )


def default_robustness_cases() -> Path:
    return _configured_path(
        "robustness_cases",
        "data/cqs/06_phak_ch4_0.robustness.json",
    )


def default_chunks_dir() -> Path:
    return _configured_path("chunks_dir", "data/chunks")


def _safe_path(key: str, fallback: str) -> Path:
    """Resolve a path from config with a hardcoded fallback.

    Uses ``.get()`` to avoid KeyError when the ``paths`` section or a
    specific key is missing from config.
    """
    config = load_default_config()
    paths = config.get("paths", {})
    value = paths.get(key) if isinstance(paths, dict) else None
    return resolve_project_path(value or fallback)
