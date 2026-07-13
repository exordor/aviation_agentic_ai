from __future__ import annotations

from datetime import UTC, date, datetime, time
from hashlib import sha256
from pathlib import Path
from typing import Any

from aviation_agentic_ai.config import resolve_project_path
from aviation_agentic_ai.cross_source.contracts import (
    SnapshotArtifact,
    SnapshotSet,
    SnapshotStatus,
    SourceSnapshot,
)
from aviation_agentic_ai.paths import project_relative_path


SOURCE_GROUPS: dict[str, tuple[str, ...]] = {
    "atcscc_advisories": ("atcscc_advisories",),
    "aviationweather": ("stationinfo", "metar", "taf"),
    "faa_nasr": ("nasr_zip", "nasr_manifest"),
    "faa_pilot_controller_glossary": ("pilot_controller_glossary",),
    "faa_atcscc_terms": ("term_seed",),
}

SOURCE_URL_KEYS = {
    "atcscc_advisories": "faa_atcscc",
    "aviationweather": "aviationweather",
    "faa_nasr": "faa_nasr",
    "faa_pilot_controller_glossary": "faa_pilot_controller_glossary",
    "faa_atcscc_terms": "faa_tmi_glossary",
}


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    digest = sha256()
    with Path(path).open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def _line_count(path: Path) -> int:
    if path.suffix.lower() != ".jsonl":
        return 1
    with path.open("rb") as stream:
        return sum(1 for line in stream if line.strip())


def _effective_datetime(value: object) -> datetime:
    parsed = date.fromisoformat(str(value))
    return datetime.combine(parsed, time.min, tzinfo=UTC)


def build_local_snapshot_set(
    config: dict[str, Any],
    *,
    retrieved_at: datetime | None = None,
) -> SnapshotSet:
    now = retrieved_at or datetime.now(UTC)
    source_paths = dict(config["sources"])
    metadata = dict(config.get("source_metadata", {}))
    source_urls = dict(config.get("source_urls", {}))
    snapshots: list[SourceSnapshot] = []

    for source_family, keys in SOURCE_GROUPS.items():
        artifacts: list[SnapshotArtifact] = []
        record_count = 0
        errors: list[str] = []
        for key in keys:
            raw_path = source_paths.get(key)
            if not raw_path:
                errors.append(f"missing configured source path: {key}")
                continue
            path = resolve_project_path(raw_path)
            if not path.exists():
                errors.append(f"source path does not exist: {project_relative_path(path)}")
                continue
            artifacts.append(
                SnapshotArtifact(
                    path=project_relative_path(path),
                    sha256=sha256_file(path),
                    byte_count=path.stat().st_size,
                )
            )
            record_count += _line_count(path)

        family_metadata = dict(metadata.get(source_family, {}))
        effective_start = _effective_datetime(
            family_metadata.get("effective_start", config["cohort"].get("as_of", "2026-05-20"))
        )
        status = SnapshotStatus.CANDIDATE if not errors else SnapshotStatus.REJECTED
        snapshots.append(
            SourceSnapshot(
                snapshot_id=f"{config['snapshot_set_id']}:{source_family}",
                source_family=source_family,
                source_url=str(source_urls.get(SOURCE_URL_KEYS[source_family], "local")),
                effective_start=effective_start,
                effective_end=None,
                retrieved_at=now,
                parser_name=f"cross_source_{source_family}",
                parser_version="1.0.0",
                artifacts=artifacts,
                record_count=record_count,
                status=status,
                validation_errors=errors,
            )
        )

    set_status = (
        SnapshotStatus.CANDIDATE
        if all(snapshot.status is SnapshotStatus.CANDIDATE for snapshot in snapshots)
        else SnapshotStatus.REJECTED
    )
    return SnapshotSet(
        snapshot_set_id=str(config["snapshot_set_id"]),
        created_at=now,
        snapshots=snapshots,
        status=set_status,
    )


def activate_snapshot_set(snapshot_set: SnapshotSet) -> SnapshotSet:
    failed = [item.source_family for item in snapshot_set.snapshots if item.validation_errors]
    if failed:
        raise ValueError(f"Cannot activate snapshot set with invalid sources: {failed}")
    active_snapshots = [
        snapshot.model_copy(update={"status": SnapshotStatus.ACTIVE})
        for snapshot in snapshot_set.snapshots
    ]
    return snapshot_set.model_copy(
        update={"status": SnapshotStatus.ACTIVE, "snapshots": active_snapshots}
    )
