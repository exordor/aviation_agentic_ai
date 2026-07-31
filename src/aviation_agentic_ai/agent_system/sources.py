"""Deterministic source loaders for the multi-Agent KG system.

Raw advisory, Weather, and BTS records are adapted into ``SourceRecord`` cards
without introducing a second authority-registry path.

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
from aviation_agentic_ai.agent_system.storage_contracts import (
    SourceAssetRecord,
    SourceVersionRecord,
)
from aviation_agentic_ai.agent_system.source_path_resolver import (
    resolve_source_path,
)
from aviation_agentic_ai.agent_system.bts_observations import (
    ARCHIVE_SHA256,
    NORMALIZED_SNAPSHOT_SHA256,
    NORMALIZED_SOURCE_ID,
)
from aviation_agentic_ai.config import resolve_project_path
from aviation_agentic_ai.paths import PROJECT_ROOT
from aviation_agentic_ai.utils.identifiers import stable_id
from aviation_agentic_ai.utils.io import read_jsonl_objects


_SOURCE_ASSET_SPECS: dict[
    str,
    tuple[SourceFamily, str, str, str],
] = {
    "atcscc_advisories": (
        SourceFamily.ATCSCC_ADVISORY,
        "application/x-ndjson",
        "atcscc_advisories",
        "faa_atcscc",
    ),
    "stationinfo": (
        SourceFamily.NASR_FACILITY,
        "application/x-ndjson",
        "aviationweather",
        "aviationweather",
    ),
    "metar": (
        SourceFamily.METAR,
        "application/x-ndjson",
        "aviationweather",
        "aviationweather",
    ),
    "taf": (
        SourceFamily.TAF,
        "application/x-ndjson",
        "aviationweather",
        "aviationweather",
    ),
    "nasr_zip": (
        SourceFamily.NASR_FACILITY,
        "application/zip",
        "faa_nasr",
        "faa_nasr",
    ),
    "nasr_manifest": (
        SourceFamily.NASR_FACILITY,
        "application/json",
        "faa_nasr",
        "faa_nasr",
    ),
    "pilot_controller_glossary": (
        SourceFamily.FAA_TERM,
        "application/pdf",
        "faa_pilot_controller_glossary",
        "faa_pilot_controller_glossary",
    ),
    "term_seed": (
        SourceFamily.FAA_TERM,
        "application/yaml",
        "faa_atcscc_terms",
        "faa_tmi_glossary",
    ),
    "bts_on_time_manifest": (
        SourceFamily.BTS_ON_TIME,
        "application/json",
        "bts_on_time",
        "bts_on_time_archive",
    ),
    "bts_on_time_snapshot": (
        SourceFamily.BTS_ON_TIME,
        "application/x-ndjson",
        "bts_on_time",
        "bts_on_time_archive",
    ),
    "bts_flight_operations": (
        SourceFamily.BTS_FLIGHT_OPERATION,
        "application/zip",
        "bts_flight_operations",
        "bts_flight_operations",
    ),
    "faa_aircraft_registry": (
        SourceFamily.FAA_AIRCRAFT_REGISTRY,
        "application/zip",
        "faa_aircraft_registry",
        "faa_aircraft_registry",
    ),
    "historical_metar_speci": (
        SourceFamily.HISTORICAL_METAR_SPECI,
        "text/csv",
        "historical_metar_speci",
        "historical_metar_speci",
    ),
    "nasa_atmonto_instances": (
        SourceFamily.NASA_ATMONTO_INSTANCE,
        "application/zip",
        "nasa_atmonto_instances",
        "nasa_atmonto_instances",
    ),
    "nasr_airspace_zip": (
        SourceFamily.NASR_AIRSPACE,
        "application/zip",
        "nasr_airspace",
        "faa_nasr",
    ),
}


def discover_source_assets(
    config: dict[str, Any],
    *,
    source_root: str | Path | None = None,
    project_root: str | Path = PROJECT_ROOT,
) -> tuple[SourceAssetRecord, ...]:
    """Checksum every configured external source asset without storing bytes."""

    configured_sources = config.get("sources")
    if not isinstance(configured_sources, dict):
        raise ValueError("config.sources must be a mapping")
    unknown = sorted(set(configured_sources) - set(_SOURCE_ASSET_SPECS))
    if unknown:
        raise ValueError(
            "unsupported configured source assets: " + ", ".join(unknown)
        )
    metadata = config.get("source_metadata")
    source_metadata = metadata if isinstance(metadata, dict) else {}
    urls = config.get("source_urls")
    source_urls = urls if isinstance(urls, dict) else {}
    checksums = config.get("source_checksums")
    source_checksums = checksums if isinstance(checksums, dict) else {}
    assets: list[SourceAssetRecord] = []
    for asset_key in sorted(configured_sources):
        configured_path = configured_sources[asset_key]
        if not isinstance(configured_path, str) or not configured_path:
            raise ValueError(
                f"config.sources.{asset_key} must be a non-empty path"
            )
        family, media_type, metadata_key, url_key = _SOURCE_ASSET_SPECS[
            asset_key
        ]
        path = resolve_source_path(
            configured_path,
            project_root=project_root,
            source_root=source_root,
        ).resolved_path
        digest = hashlib.sha256()
        byte_count = 0
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
                byte_count += len(chunk)
        content_sha256 = digest.hexdigest()
        expected_checksum = source_checksums.get(asset_key)
        if expected_checksum is not None and expected_checksum != content_sha256:
            raise ValueError(
                f"source checksum mismatch for {asset_key}: "
                f"expected {expected_checksum}, observed {content_sha256}"
            )
        family_metadata = source_metadata.get(metadata_key)
        effective = (
            family_metadata if isinstance(family_metadata, dict) else {}
        )
        source_url = source_urls.get(url_key)
        assets.append(
            SourceAssetRecord(
                asset_id=stable_id(
                    "source-asset",
                    asset_key,
                    content_sha256,
                ),
                asset_key=asset_key,
                family=family,
                local_path=Path(configured_path).as_posix(),
                source_url=(
                    source_url
                    if isinstance(source_url, str) and source_url
                    else None
                ),
                media_type=media_type,
                content_sha256=content_sha256,
                byte_count=byte_count,
                effective_start=(
                    str(effective["effective_start"])
                    if effective.get("effective_start") is not None
                    else None
                ),
                effective_end=(
                    str(effective["effective_end"])
                    if effective.get("effective_end") is not None
                    else None
                ),
            )
        )
    return tuple(assets)


def load_advisory_source(config: dict[str, Any], source_id: str) -> SourceRecord:
    """Load one ATCSCC advisory by ``source_id`` from the configured JSONL."""

    path = resolve_project_path(config["sources"]["atcscc_advisories"])
    for row in read_jsonl_objects(path):
        if str(row.get("source_id")) == source_id:
            return SourceRecord(
                source_id=source_id,
                family=SourceFamily.ATCSCC_ADVISORY,
                content=str(row.get("text", "")),
                title=str(row.get("title") or row.get("advisory_number") or source_id),
                source_url=str(row.get("source_url") or "") or None,
            )
    raise KeyError(f"advisory source_id not found: {source_id}")


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


def build_source_version(record: SourceRecord) -> SourceVersionRecord:
    """Build an immutable persistent version from one exact logical record."""

    content_sha256 = _content_sha256(record.content)
    metadata = dict(record.metadata)
    if record.title is not None:
        metadata.setdefault("title", record.title)
    return SourceVersionRecord(
        source_version_id=stable_id(
            "source-version",
            record.source_id,
            content_sha256,
        ),
        source_id=record.source_id,
        family=record.family,
        asset_id=record.asset_id,
        content=record.content,
        content_sha256=content_sha256,
        source_url=record.source_url,
        logical_time=record.logical_time,
        metadata=metadata,
    )


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
