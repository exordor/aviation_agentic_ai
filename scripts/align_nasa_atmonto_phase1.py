#!/usr/bin/env python3
"""Create a common-period view over the phase-1 NASA ATMONTO source snapshot."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--snapshot-date",
        default="2026-06-01",
        help="Collected snapshot date to align, YYYY-MM-DD.",
    )
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Repository root.",
    )
    return parser.parse_args()


def parse_source_time(value: Any) -> datetime:
    if isinstance(value, int | float):
        return datetime.fromtimestamp(value, UTC)
    if isinstance(value, str):
        if value.endswith("Z"):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return datetime.fromisoformat(value)
    raise TypeError(f"Unsupported time value: {value!r}")


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def iso(value: datetime) -> str:
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_rel(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def manifest_record_paths(
    manifest: dict[str, Any], record_type: str, repo_root: Path
) -> list[Path]:
    paths = [
        repo_root / entry["raw_file"]
        for entry in manifest.get("files", [])
        if entry.get("record_type") == record_type
    ]
    if not paths:
        raise KeyError(f"No {record_type!r} entries in manifest")
    return paths


def load_manifest_records(
    manifest: dict[str, Any],
    record_type: str,
    repo_root: Path,
    dedupe_fields: tuple[str, ...],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for path in manifest_record_paths(manifest, record_type, repo_root):
        for record in load_json(path):
            key = tuple(record.get(field) for field in dedupe_fields)
            if key in seen:
                continue
            seen.add(key)
            rows.append(record)
    return rows


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return len(rows)


def intervals_intersect(
    source_start: datetime,
    source_end: datetime,
    window_start: datetime,
    window_end: datetime,
) -> bool:
    if source_start == source_end:
        return window_start <= source_start <= window_end
    return source_start <= window_end and source_end >= window_start


def day_hhmm_to_datetime(token: str, base_year: int, base_month: int) -> datetime:
    clean = token.replace("/", "").rstrip("Z")
    if not re.fullmatch(r"\d{6}", clean):
        raise ValueError(f"Expected DDHHMM token, got {token!r}")
    day = int(clean[:2])
    hour = int(clean[2:4])
    minute = int(clean[4:6])
    return datetime(base_year, base_month, day, hour, minute, tzinfo=UTC)


def parse_advisory_date(text: str, fallback: date) -> date:
    match = re.search(r"ADVZY\s+\d+\s+.*?\s+(\d{2})/(\d{2})/(\d{4})", text)
    if match:
        month, day, year = (int(part) for part in match.groups())
        return date(year, month, day)
    return fallback


def parse_atcscc_temporal_intervals(
    row: dict[str, Any], fallback_date: date
) -> list[dict[str, str]]:
    text = " ".join(str(row.get("text", "")).split())
    advisory_date = parse_advisory_date(text, fallback_date)
    intervals: list[dict[str, str]] = []

    range_patterns = [
        (
            re.compile(
                r"([A-Z][A-Z0-9 /]*?(?:TIME|PERIOD)):\s*"
                r"(\d{2}/\d{4}Z?)\s*-\s*(\d{2}/\d{4}Z?)"
            ),
            "slash_range",
        ),
        (
            re.compile(r"(EFFECTIVE TIME):\s*(\d{6})-(\d{6})"),
            "compact_effective_range",
        ),
    ]
    for pattern, basis in range_patterns:
        for match in pattern.finditer(text):
            label = " ".join(match.group(1).split())
            start = day_hhmm_to_datetime(match.group(2), advisory_date.year, advisory_date.month)
            end = day_hhmm_to_datetime(match.group(3), advisory_date.year, advisory_date.month)
            if end < start:
                end = end + timedelta(days=1)
            intervals.append(
                {
                    "basis": basis,
                    "label": label,
                    "start": iso(start),
                    "end": iso(end),
                }
            )

    for match in re.finditer(r"DTG:\s*(\d{8})/(\d{4})Z", text):
        stamp = datetime.strptime("".join(match.groups()), "%Y%m%d%H%M").replace(tzinfo=UTC)
        intervals.append(
            {
                "basis": "issued_time",
                "label": "DTG",
                "start": iso(stamp),
                "end": iso(stamp),
            }
        )

    for match in re.finditer(r"SIGNATURE:\s*(\d{2})/(\d{2})/(\d{2})\s+(\d{2}):(\d{2})", text):
        year, month, day, hour, minute = (int(part) for part in match.groups())
        stamp = datetime(2000 + year, month, day, hour, minute, tzinfo=UTC)
        intervals.append(
            {
                "basis": "issued_time",
                "label": "SIGNATURE",
                "start": iso(stamp),
                "end": iso(stamp),
            }
        )

    return intervals


def add_alignment(
    row: dict[str, Any],
    *,
    window_start: datetime,
    window_end: datetime,
    source_period_start: datetime,
    source_period_end: datetime,
    source_period_basis: str,
    alignment_role: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    aligned = dict(row)
    aligned["temporal_alignment"] = {
        "alignment_window_start": iso(window_start),
        "alignment_window_end": iso(window_end),
        "source_period_start": iso(source_period_start),
        "source_period_end": iso(source_period_end),
        "source_period_basis": source_period_basis,
        "alignment_role": alignment_role,
    }
    if extra:
        aligned["temporal_alignment"].update(extra)
    return aligned


def derive_common_window(
    metar_records: list[dict[str, Any]],
    taf_records: list[dict[str, Any]],
    nasr_effective_date: date,
    snapshot_date: date,
) -> tuple[datetime, datetime, dict[str, Any]]:
    metar_report_times = [parse_source_time(record["reportTime"]) for record in metar_records]
    taf_valid_starts = [parse_source_time(record["validTimeFrom"]) for record in taf_records]
    taf_valid_ends = [parse_source_time(record["validTimeTo"]) for record in taf_records]

    nasr_cycle_start = datetime.combine(nasr_effective_date, datetime.min.time(), tzinfo=UTC)
    nasr_cycle_end = nasr_cycle_start + timedelta(days=28)
    atcscc_day_start = datetime.combine(snapshot_date, datetime.min.time(), tzinfo=UTC)
    atcscc_day_end = atcscc_day_start + timedelta(days=1)

    coverage = {
        "aviationweather_metar": {
            "basis": "reportTime",
            "start": iso(min(metar_report_times)),
            "end": iso(max(metar_report_times)),
        },
        "aviationweather_taf": {
            "basis": "TAF validity union across collected forecasts",
            "start": iso(min(taf_valid_starts)),
            "end": iso(max(taf_valid_ends)),
        },
        "faa_nasr": {
            "basis": "28-day effective cycle",
            "start": iso(nasr_cycle_start),
            "end": iso(nasr_cycle_end),
            "end_boundary": "exclusive",
        },
        "atcscc_advisories": {
            "basis": "advisory database day",
            "start": iso(atcscc_day_start),
            "end": iso(atcscc_day_end),
        },
    }

    window_start = max(
        min(metar_report_times),
        min(taf_valid_starts),
        nasr_cycle_start,
        atcscc_day_start,
    )
    window_end = min(
        max(metar_report_times),
        max(taf_valid_ends),
        nasr_cycle_end,
        atcscc_day_end,
    )
    if window_end < window_start:
        raise RuntimeError("Source coverage has no shared temporal overlap")
    return window_start, window_end, coverage


def ensure_window_is_covered(
    window_start: datetime, window_end: datetime, source_coverage: dict[str, Any]
) -> None:
    gaps = []
    for source_name, coverage in source_coverage.items():
        source_start = parse_source_time(coverage["start"])
        source_end = parse_source_time(coverage["end"])
        if source_start > window_start or source_end < window_end:
            gaps.append(
                f"{source_name} covers {coverage['start']} to {coverage['end']}, "
                f"not {iso(window_start)} to {iso(window_end)}"
            )
    if gaps:
        raise RuntimeError("Fixed alignment window is not fully covered: " + "; ".join(gaps))


def align_sources(repo_root: Path, snapshot_date_text: str) -> dict[str, Any]:
    snapshot_day = parse_date(snapshot_date_text)
    raw_root = repo_root / "data/raw/nasa_atmonto" / snapshot_date_text
    processed_root = repo_root / "data/processed/nasa_atmonto"
    source_processed_root = processed_root / "source" / snapshot_date_text
    if not source_processed_root.exists():
        source_processed_root = processed_root
    aligned_root = processed_root / "aligned" / snapshot_date_text
    reports_root = repo_root / "reports/stages"

    aviationweather_manifest = load_json(raw_root / "aviationweather" / "manifest.json")
    metar_records = load_manifest_records(
        aviationweather_manifest,
        "metar",
        repo_root,
        ("icaoId", "reportTime", "rawOb"),
    )
    taf_records = load_manifest_records(
        aviationweather_manifest,
        "taf",
        repo_root,
        ("icaoId", "issueTime", "rawTAF"),
    )
    station_records = load_manifest_records(
        aviationweather_manifest,
        "stationinfo",
        repo_root,
        ("icaoId", "id"),
    )
    atcscc_rows = load_jsonl(source_processed_root / "atcscc_advisories.jsonl")
    nasr_rows = load_jsonl(source_processed_root / "faa_nasr_zip_inventory.jsonl")
    nasr_manifest = load_json(raw_root / "faa_nasr" / "manifest.json")
    nasr_effective_date = parse_date(nasr_manifest["scope"]["effective_date"])

    derived_start, derived_end, source_coverage = derive_common_window(
        metar_records, taf_records, nasr_effective_date, snapshot_day
    )
    aw_scope = aviationweather_manifest.get("scope", {})
    selected_airports = aw_scope.get("airports", [])
    if "alignment_window_start" in aw_scope and "alignment_window_end" in aw_scope:
        window_start = parse_source_time(aw_scope["alignment_window_start"])
        window_end = parse_source_time(aw_scope["alignment_window_end"])
        source_coverage["aviationweather_metar"] = {
            "basis": "AviationWeather METAR query window; individual records are filtered by reportTime",
            "start": iso(window_start),
            "end": iso(window_end),
            "observed_record_span": {
                "start": source_coverage["aviationweather_metar"]["start"],
                "end": source_coverage["aviationweather_metar"]["end"],
                "basis": source_coverage["aviationweather_metar"]["basis"],
            },
        }
        source_coverage["aviationweather_taf"] = {
            "basis": "AviationWeather TAF query timestamps covering fixed window; records are filtered by validity interval",
            "start": iso(window_start),
            "end": iso(window_end),
            "observed_validity_span": {
                "start": source_coverage["aviationweather_taf"]["start"],
                "end": source_coverage["aviationweather_taf"]["end"],
                "basis": source_coverage["aviationweather_taf"]["basis"],
            },
        }
        source_coverage["atcscc_advisories"] = {
            "basis": "advisory database dates covering fixed alignment window",
            "start": iso(window_start),
            "end": iso(window_end),
        }
        ensure_window_is_covered(window_start, window_end, source_coverage)
        alignment_policy = "fixed historical UTC window selected before retrieval"
    else:
        window_start = derived_start
        window_end = derived_end
        alignment_policy = "common temporal overlap across collected dynamic sources"
    nasr_cycle_start = datetime.combine(nasr_effective_date, datetime.min.time(), tzinfo=UTC)
    nasr_cycle_end = nasr_cycle_start + timedelta(days=28)

    aligned_metar = []
    for record in metar_records:
        report_time = parse_source_time(record["reportTime"])
        if window_start <= report_time <= window_end:
            aligned_metar.append(
                add_alignment(
                    record,
                    window_start=window_start,
                    window_end=window_end,
                    source_period_start=report_time,
                    source_period_end=report_time,
                    source_period_basis="METAR reportTime",
                    alignment_role="weather_observation",
                )
            )

    aligned_taf = []
    for record in taf_records:
        valid_start = parse_source_time(record["validTimeFrom"])
        valid_end = parse_source_time(record["validTimeTo"])
        if intervals_intersect(valid_start, valid_end, window_start, window_end):
            aligned_taf.append(
                add_alignment(
                    record,
                    window_start=window_start,
                    window_end=window_end,
                    source_period_start=valid_start,
                    source_period_end=valid_end,
                    source_period_basis="TAF validTimeFrom/validTimeTo",
                    alignment_role="weather_forecast",
                )
            )

    aligned_station = [
        add_alignment(
            record,
            window_start=window_start,
            window_end=window_end,
            source_period_start=window_start,
            source_period_end=window_end,
            source_period_basis="station metadata attached to aligned window",
            alignment_role="station_context",
        )
        for record in station_records
    ]

    aligned_nasr = [
        add_alignment(
            record,
            window_start=window_start,
            window_end=window_end,
            source_period_start=nasr_cycle_start,
            source_period_end=nasr_cycle_end,
            source_period_basis="NASR 28-day effective cycle [start, end)",
            alignment_role="reference_cycle",
        )
        for record in nasr_rows
        if intervals_intersect(nasr_cycle_start, nasr_cycle_end, window_start, window_end)
    ]

    aligned_atcscc = []
    for row in atcscc_rows:
        row_advisory_day = parse_date(str(row.get("advisory_date", snapshot_date_text)))
        intervals = parse_atcscc_temporal_intervals(row, row_advisory_day)
        overlaps = [
            interval
            for interval in intervals
            if intervals_intersect(
                parse_source_time(interval["start"]),
                parse_source_time(interval["end"]),
                window_start,
                window_end,
            )
        ]
        if overlaps:
            interval_starts = [parse_source_time(interval["start"]) for interval in overlaps]
            interval_ends = [parse_source_time(interval["end"]) for interval in overlaps]
            aligned_atcscc.append(
                add_alignment(
                    row,
                    window_start=window_start,
                    window_end=window_end,
                    source_period_start=min(interval_starts),
                    source_period_end=max(interval_ends),
                    source_period_basis="ATCSCC parsed advisory time fields",
                    alignment_role="traffic_management_advisory",
                    extra={
                        "parsed_intervals": intervals,
                        "overlapping_intervals": overlaps,
                    },
                )
            )

    outputs = {
        "aviationweather_metar": {
            "path": aligned_root / "aviationweather_metar.jsonl",
            "count": write_jsonl(aligned_root / "aviationweather_metar.jsonl", aligned_metar),
        },
        "aviationweather_taf": {
            "path": aligned_root / "aviationweather_taf.jsonl",
            "count": write_jsonl(aligned_root / "aviationweather_taf.jsonl", aligned_taf),
        },
        "aviationweather_stationinfo": {
            "path": aligned_root / "aviationweather_stationinfo.jsonl",
            "count": write_jsonl(
                aligned_root / "aviationweather_stationinfo.jsonl", aligned_station
            ),
        },
        "faa_nasr_zip_inventory": {
            "path": aligned_root / "faa_nasr_zip_inventory.jsonl",
            "count": write_jsonl(aligned_root / "faa_nasr_zip_inventory.jsonl", aligned_nasr),
        },
        "atcscc_advisories": {
            "path": aligned_root / "atcscc_advisories.jsonl",
            "count": write_jsonl(aligned_root / "atcscc_advisories.jsonl", aligned_atcscc),
        },
    }

    manifest = {
        "artifact": "nasa_atmonto_phase1_temporal_alignment",
        "snapshot_date": snapshot_date_text,
        "alignment_policy": alignment_policy,
        "alignment_window": {
            "start": iso(window_start),
            "end": iso(window_end),
            "boundary_rule": "inclusive for instant records; interval records are included when they intersect the window",
        },
        "selected_airports": selected_airports,
        "source_coverage": source_coverage,
        "outputs": {
            name: {
                "path": repo_rel(info["path"], repo_root),
                "record_count": info["count"],
            }
            for name, info in outputs.items()
        },
        "limitations": [
            "The aligned window is a fixed past UTC window selected before retrieval and verified against each source coverage.",
            "NASR is cycle-valid reference data; every zip member is attached as the reference layer covering the aligned window.",
            "ATCSCC advisory intervals are parsed from public HTML text and should be reviewed before treating them as gold timestamps.",
        ],
    }
    manifest_path = aligned_root / "temporal_alignment_manifest.json"
    write_json(manifest_path, manifest)
    manifest["outputs"]["temporal_alignment_manifest"] = {
        "path": repo_rel(manifest_path, repo_root),
        "record_count": 1,
    }
    write_json(manifest_path, manifest)

    report_path = reports_root / "nasa_atmonto_temporal_alignment.json"
    write_json(report_path, manifest)
    write_alignment_markdown(
        reports_root / "nasa_atmonto_temporal_alignment.md",
        manifest,
    )
    return manifest


def write_alignment_markdown(path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# NASA ATMONTO Temporal Alignment",
        "",
        f"- Snapshot date: {manifest['snapshot_date']}",
        f"- Policy: {manifest['alignment_policy']}",
        f"- Aligned window: {manifest['alignment_window']['start']} to {manifest['alignment_window']['end']}",
        f"- Boundary rule: {manifest['alignment_window']['boundary_rule']}",
        "",
        "## Source Coverage",
        "",
    ]
    for source_name, coverage in manifest["source_coverage"].items():
        lines.append(
            f"- {source_name}: {coverage['start']} to {coverage['end']} ({coverage['basis']})"
        )
    lines.extend(["", "## Aligned Outputs", ""])
    for output_name, info in manifest["outputs"].items():
        lines.append(f"- {output_name}: {info['record_count']} records, `{info['path']}`")
    lines.extend(["", "## Limitations", ""])
    for limitation in manifest["limitations"]:
        lines.append(f"- {limitation}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    manifest = align_sources(args.repo_root.resolve(), args.snapshot_date)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
