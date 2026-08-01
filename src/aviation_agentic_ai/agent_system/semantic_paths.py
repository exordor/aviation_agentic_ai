"""Paths for semantic assets used by the active Agent-system runtime."""

from __future__ import annotations

from pathlib import Path


# The curated slice is the runtime contract. The upstream NASA OWL files are
# reference inputs for producing and auditing this slice, not runtime modules.
ATMONTO_SCHEMA_SLICE_PATH = Path(
    "data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json"
)


__all__ = ["ATMONTO_SCHEMA_SLICE_PATH"]
