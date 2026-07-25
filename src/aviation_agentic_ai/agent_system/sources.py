"""Source loaders for the multi-Agent KG system.

Reuses the existing authority readers at the base commit: ``read_jsonl`` for
advisory JSONL, ``build_facility_registry`` for NASR facility cards, and
``build_term_registry`` for the FAA operational-term seed. No new registry or
extraction code is introduced; this module only adapts those readers into
``SourceRecord`` cards the Agents consume.

Also provides the deterministic source-snapshot writer (plan §5.2): every
accepted formal fact binds to a source whose exact content and SHA-256 are
persisted, so provenance is auditable end-to-end.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.contracts import SourceFamily, SourceRecord, SourceSnapshot
from aviation_agentic_ai.cross_source.alignment.registry import (
    build_facility_registry,
    build_term_registry,
)
from aviation_agentic_ai.cross_source.artifacts import read_jsonl
from aviation_agentic_ai.config import resolve_project_path


def _cross_source_config(config: dict[str, Any]) -> dict[str, Any]:
    """Adapt the agent-system config to the cross_source registry-builder shape."""

    sources = dict(config["sources"])
    return {
        "snapshot_set_id": config.get("snapshot_set_id", "agent-system-v1"),
        "cohort": {
            "advisory_input": sources.get("atcscc_advisories", ""),
            "airport_codes": list(config.get("cohort", {}).get("airport_codes", [])),
            "expected_record_count": 1,
        },
        "sources": sources,
        "authority_priority": config.get("authority_priority", {}),
        "alignment": {
            "context_accept_threshold": 0.9,
            "minimum_candidate_margin": 0.2,
            "quarantine_threshold": 0.6,
            "reject_out_of_registry_targets": True,
        },
        "temporal_linking": {
            "metar_before_minutes": 60,
            "metar_after_minutes": 60,
            "require_taf_validity_overlap": True,
        },
        "answering": {
            "require_citations": True,
            "forbid_inferred_causality": True,
            "require_evidence_layers": True,
        },
        "paths": {
            "processed_root": "data/processed/agent_system",
            "kg_root": "data/kg/agent_system",
            "evaluation_root": config.get("paths", {}).get(
                "evaluation_root", "data/evaluation/agent_system"
            ),
        },
        "source_metadata": config.get("source_metadata", {}),
        "source_urls": config.get("source_urls", {}),
    }


def load_advisory_source(config: dict[str, Any], source_id: str) -> SourceRecord:
    """Load one ATCSCC advisory by ``source_id`` from the configured JSONL."""

    path = resolve_project_path(config["sources"]["atcscc_advisories"])
    for row in read_jsonl(path):
        if str(row.get("source_id")) == source_id:
            return SourceRecord(
                source_id=source_id,
                family=SourceFamily.ATCSCC_ADVISORY,
                content=str(row.get("text", "")),
                title=str(row.get("title") or row.get("advisory_number") or source_id),
                source_url=str(row.get("source_url") or "") or None,
            )
    raise KeyError(f"advisory source_id not found: {source_id}")


def load_facility_source(config: dict[str, Any], canonical_facility_id: str) -> SourceRecord:
    """Load one NASR facility card by canonical facility id."""

    facilities = build_facility_registry(_cross_source_config(config))
    for entity in facilities:
        if entity.entity_id == canonical_facility_id:
            codes = ", ".join(f"{c.scheme}={c.value}" for c in entity.codes)
            content = (
                f"Facility: {entity.preferred_label}\n"
                f"Canonical ID: {entity.entity_id}\n"
                f"Type: {entity.entity_type.value}\n"
                f"Codes: {codes}\n"
                f"Source refs: {', '.join(entity.source_refs)}"
            )
            return SourceRecord(
                source_id=entity.entity_id,
                family=SourceFamily.NASR_FACILITY,
                content=content,
                title=entity.preferred_label,
            )
    raise KeyError(f"facility canonical id not found: {canonical_facility_id}")


def load_term_source(config: dict[str, Any], canonical_term_id: str) -> SourceRecord:
    """Load one FAA term card by canonical term id (from the term seed)."""

    terms = build_term_registry(_cross_source_config(config))
    for term in terms:
        if term.term_id == canonical_term_id:
            definitions = "\n".join(d.text for d in term.definitions) or term.preferred_label
            content = (
                f"Term: {term.preferred_label} ({term.abbreviation})\n"
                f"Canonical ID: {term.term_id}\n"
                f"Category: {term.term_category.value}\n"
                f"Definitions:\n{definitions}"
            )
            return SourceRecord(
                source_id=term.term_id,
                family=SourceFamily.FAA_TERM,
                content=content,
                title=term.preferred_label,
            )
    raise KeyError(f"term canonical id not found: {canonical_term_id}")


def facility_candidates(config: dict[str, Any]) -> list[Any]:
    """Return all NASR facility entities for the configured cohort."""

    return build_facility_registry(_cross_source_config(config))


def term_candidates(config: dict[str, Any]) -> list[Any]:
    """Return all FAA term concepts from the term seed."""

    return build_term_registry(_cross_source_config(config))


# ---------------------------------------------------------------------------
# Source snapshot (plan §5.2)
# ---------------------------------------------------------------------------


def _content_sha256(content: str) -> str:
    """SHA-256 of the exact source content (UTF-8)."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def build_source_snapshot(record: SourceRecord) -> SourceSnapshot:
    """Build a versioned :class:`SourceSnapshot` from a :class:`SourceRecord`.

    The snapshot pins the exact source content and its SHA-256 so the Formal
    Graph Kernel can bind every accepted fact to source-contained evidence
    (plan §5.2). The snapshot is deterministic in ``record`` and timestamp.
    """

    return SourceSnapshot(
        source_id=record.source_id,
        family=record.family.value,
        source_url=record.source_url,
        content=record.content,
        content_sha256=_content_sha256(record.content),
        snapshot_timestamp=datetime.now(UTC).isoformat(),
    )


def write_source_snapshot(snapshot: SourceSnapshot, output_dir: str | Path) -> Path:
    """Write ``source_snapshot.json`` for one source (plan §5.2)."""

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / "source_snapshot.json"
    path.write_text(
        snapshot.model_dump_json(indent=2, exclude_none=True),
        encoding="utf-8",
    )
    return path
