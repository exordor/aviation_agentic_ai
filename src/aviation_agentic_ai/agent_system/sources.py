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
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.contracts import (
    BTSManifestBinding,
    BTSOnTimeRow,
    SourceFamily,
    SourceRecord,
    SourceSnapshot,
    SourceSnapshotRegistry,
)
from aviation_agentic_ai.agent_system.bts_outcomes import (
    ARCHIVE_SHA256,
    NORMALIZED_SNAPSHOT_SHA256,
    NORMALIZED_SOURCE_ID,
)
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


def _weather_logical_time(row: dict[str, Any], family: SourceFamily) -> str:
    field = "reportTime" if family == SourceFamily.METAR else "issueTime"
    value = row.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{family.value} row has no {field}")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{family.value} {field} must be timezone-aware")
    return parsed.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")


def _weather_source_id(
    row: dict[str, Any],
    family: SourceFamily,
) -> str:
    station = row.get("icaoId")
    raw_field = "rawOb" if family == SourceFamily.METAR else "rawTAF"
    raw = row.get(raw_field)
    if not isinstance(station, str) or not station:
        raise ValueError(f"{family.value} row has no ICAO station")
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"{family.value} row has no raw report")
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return (
        f"weather-source:{family.value}:{station}:"
        f"{_weather_logical_time(row, family)}:{digest}"
    )


def _load_weather_file(path: Path, family: SourceFamily) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"invalid {family.value} JSON at line {line_number}"
            ) from exc
        if not isinstance(row, dict):
            raise ValueError(f"{family.value} row must be an object at line {line_number}")
        records.append(
            SourceRecord(
                source_id=_weather_source_id(row, family),
                family=family,
                content=line,
                title=f"{family.value.upper()} {row.get('icaoId', '')}".strip(),
            )
        )
    source_ids = [record.source_id for record in records]
    if len(source_ids) != len(set(source_ids)):
        raise ValueError(f"duplicate {family.value} source ID")
    return records


def load_weather_sources(config: dict[str, Any]) -> list[SourceRecord]:
    """Load exact configured METAR/TAF JSONL rows as deterministic sources."""

    sources = config.get("sources")
    configured = sources if isinstance(sources, dict) else {}
    missing = [
        family
        for family in ("metar", "taf")
        if not configured.get(family)
    ]
    if missing:
        raise ValueError(
            "optional weather source paths are not configured: "
            + ", ".join(missing)
        )
    metar = _load_weather_file(
        resolve_project_path(configured["metar"]),
        SourceFamily.METAR,
    )
    taf = _load_weather_file(
        resolve_project_path(configured["taf"]),
        SourceFamily.TAF,
    )
    return sorted([*metar, *taf], key=lambda record: record.source_id)


def load_bts_context_source(
    config: dict[str, Any] | None = None,
) -> tuple[SourceRecord, list[BTSOnTimeRow], BTSManifestBinding]:
    """Load the configured, checksum-pinned BTS normalized snapshot."""

    configured = (
        config.get("sources", {})
        if isinstance(config, dict)
        else {}
    )
    data_path = resolve_project_path(
        configured.get(
            "bts_on_time_snapshot",
            "data/sources/bts_on_time_2026_05_nyc.jsonl",
        )
    )
    manifest_path = resolve_project_path(
        configured.get(
            "bts_on_time_manifest",
            "data/sources/bts_on_time_2026_05_manifest.json",
        )
    )
    content = data_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("BTS manifest must be an object")
    if manifest.get("source_id") != NORMALIZED_SOURCE_ID:
        raise ValueError("BTS manifest source ID does not match the pinned snapshot")
    if manifest.get("archive_sha256") != ARCHIVE_SHA256:
        raise ValueError("BTS manifest archive checksum does not match the pinned archive")
    checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if (
        manifest.get("normalized_sha256") != checksum
        or checksum != NORMALIZED_SNAPSHOT_SHA256
    ):
        raise ValueError("BTS normalized snapshot checksum mismatch")
    rows: list[BTSOnTimeRow] = []
    for line_number, line in enumerate(content.splitlines(), 1):
        if not line:
            continue
        try:
            rows.append(BTSOnTimeRow.model_validate_json(line))
        except Exception as exc:
            raise ValueError(
                f"invalid normalized BTS row at line {line_number}"
            ) from exc
    if len(rows) != manifest.get("row_count"):
        raise ValueError("BTS normalized row count does not match manifest")
    if len({row.row_id for row in rows}) != len(rows):
        raise ValueError("duplicate normalized BTS row ID")
    return (
        SourceRecord(
            source_id=NORMALIZED_SOURCE_ID,
            family=SourceFamily.BTS_ON_TIME,
            content=content,
            title="BTS On-Time Performance 2026-05 NYC subset",
            source_url=str(manifest.get("url") or "") or None,
        ),
        rows,
        BTSManifestBinding(
            source_id=str(manifest["source_id"]),
            archive_sha256=str(manifest["archive_sha256"]),
            normalized_snapshot_sha256=str(manifest["normalized_sha256"]),
        ),
    )


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


def build_source_snapshot_registry(records: list[SourceRecord]) -> SourceSnapshotRegistry:
    """Build checksum-pinned, family-bound snapshots for one ingest run."""

    return SourceSnapshotRegistry(
        snapshots=tuple(build_source_snapshot(record) for record in records),
        expected_families={record.source_id: record.family for record in records},
    )


def write_source_snapshot_registry(
    registry: SourceSnapshotRegistry, output_dir: str | Path
) -> Path:
    """Write the canonical ``source_snapshots.jsonl`` artifact for a new run."""

    return registry.write_jsonl(output_dir)


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
