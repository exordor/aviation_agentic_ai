"""Paths for semantic assets used by the active Agent-system runtime."""

from __future__ import annotations

from pathlib import Path


# The curated slice is the runtime contract. The upstream NASA OWL files are
# checksum-pinned semantic authority inputs for producing and auditing the
# active slices; they are never fetched remotely at runtime.
ATMONTO_SCHEMA_SLICE_PATH = Path(
    "data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json"
)

ATMONTO_REFERENCE_MODULE_DIR = Path(
    "data/ontology/external/icarus_ontology/NASA"
)
ATMONTO_REFERENCE_MODULES = (
    "ATM.owl",
    "NAS.owl",
    "data.owl",
    "equipment.owl",
    "general.owl",
    "atmontoCore.owl",
)


__all__ = [
    "ATMONTO_REFERENCE_MODULE_DIR",
    "ATMONTO_REFERENCE_MODULES",
    "ATMONTO_SCHEMA_SLICE_PATH",
]
