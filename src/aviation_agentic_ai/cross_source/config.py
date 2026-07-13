from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.config import load_yaml


REQUIRED_SECTIONS = {
    "snapshot_set_id",
    "cohort",
    "sources",
    "authority_priority",
    "alignment",
    "temporal_linking",
    "answering",
    "paths",
}


def load_cross_source_config(path: str | Path) -> dict[str, Any]:
    config = load_yaml(path)
    missing = sorted(REQUIRED_SECTIONS - config.keys())
    if missing:
        raise ValueError(f"Cross-source config is missing required sections: {missing}")
    expected = int(config["cohort"]["expected_record_count"])
    if expected <= 0:
        raise ValueError("cohort.expected_record_count must be positive")
    thresholds = config["alignment"]
    accept = float(thresholds["context_accept_threshold"])
    quarantine = float(thresholds["quarantine_threshold"])
    if not 0 <= quarantine < accept <= 1:
        raise ValueError("alignment thresholds must satisfy 0 <= quarantine < accept <= 1")
    return config
