"""Behavior tests for the deterministic BTS on-time outcome adapter."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.bts_outcomes import (
    ARCHIVE_SHA256,
    MEMBER_SHA256,
    build_bts_outcome_summaries,
    infer_destination_arrival_utc,
    normalize_bts_archive,
)
from aviation_agentic_ai.agent_system.contracts import DecisionContextEvent
from aviation_agentic_ai.cross_source.contracts import CanonicalEntity, CodeValue, EntityType


ARCHIVE = Path("/tmp/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2026_5.zip")


def _facility(iata: str, icao: str) -> CanonicalEntity:
    return CanonicalEntity(
        entity_id=f"urn:test:facility:{icao}",
        entity_type=EntityType.AIRPORT,
        preferred_label=icao,
        codes=[CodeValue(scheme="IATA", value=iata), CodeValue(scheme="ICAO", value=icao)],
    )


def _event(event_id: str, start: datetime, end: datetime) -> DecisionContextEvent:
    return DecisionContextEvent(
        run_id=f"run:{event_id}",
        event_id=event_id,
        advisory_source_id=f"advisory:{event_id}",
        advisory_issued_at=start - timedelta(hours=1),
        operational_start=start,
        operational_end=end,
    )


@pytest.fixture(scope="module")
def normalized(tmp_path_factory: pytest.TempPathFactory):
    output_dir = tmp_path_factory.mktemp("bts-normalized")
    result = normalize_bts_archive(
        ARCHIVE,
        output_path=output_dir / "nyc.jsonl",
        manifest_path=output_dir / "manifest.json",
    )
    assert result.status == "ok", result.failure_reason
    return result


def test_normalizes_the_pinned_subset_with_stable_hashes_and_nulls(normalized):
    output = normalized.output_path
    manifest = json.loads(normalized.manifest_path.read_text(encoding="utf-8"))
    lines = output.read_text(encoding="utf-8").splitlines()

    assert ARCHIVE_SHA256 == "4e7b96999440afec8c92dd23bfbc68a5852e14d9a56c3d0d366f884542ea80b3"
    assert MEMBER_SHA256 == "12470de43703fe0c23e25510b5af6e6e4e1d5d0aa55818dcc7d0f0b407801be8"
    assert len(lines) == 1_978
    assert manifest["row_count"] == 1_978
    assert manifest["archive_sha256"] == ARCHIVE_SHA256
    assert manifest["member_sha256"] == MEMBER_SHA256
    assert manifest["expected_named_field_count"] == 110
    assert manifest["terminal_unnamed_column"] == ""
    assert manifest["timezone"] == "America/New_York"
    assert hashlib.sha256(output.read_bytes()).hexdigest() == manifest["normalized_sha256"]
    rows = [json.loads(line) for line in lines]
    assert rows == sorted(rows, key=lambda row: row["row_id"])
    assert len({row["row_id"] for row in rows}) == len(rows)
    assert any(row["WeatherDelay"] is None for row in rows)
    assert all(set(row) == set(manifest["normalized_fields"]) for row in rows)


def test_normalization_is_byte_stable_and_rejects_a_bad_archive_checksum(tmp_path, normalized):
    repeat = normalize_bts_archive(
        ARCHIVE,
        output_path=tmp_path / "repeat.jsonl",
        manifest_path=tmp_path / "repeat-manifest.json",
    )
    assert repeat.status == "ok"
    assert repeat.output_path.read_bytes() == normalized.output_path.read_bytes()

    damaged = tmp_path / "damaged.zip"
    damaged.write_bytes(ARCHIVE.read_bytes() + b"damaged")
    blocked = normalize_bts_archive(
        damaged,
        output_path=tmp_path / "bad.jsonl",
        manifest_path=tmp_path / "bad-manifest.json",
    )
    assert blocked.status == "blocked"
    assert "archive checksum" in blocked.failure_reason


def test_infers_overnight_destination_arrival_and_real_iana_dst_offsets():
    overnight = infer_destination_arrival_utc("2026-05-19", 2300, 45, 105)
    winter = infer_destination_arrival_utc("2026-01-15", 2200, 30, 150)

    assert overnight == datetime(2026, 5, 20, 4, 45, tzinfo=UTC)
    assert winter == datetime(2026, 1, 16, 5, 30, tzinfo=UTC)
    with pytest.raises(ValueError, match="residual"):
        infer_destination_arrival_utc("2026-05-19", 100, 100, 5_000)


def test_summaries_use_half_open_windows_and_preserve_null_aggregates(normalized):
    rows = normalized.rows
    event = _event(
        "urn:test:half-open",
        datetime(2026, 5, 19, 21, tzinfo=UTC),
        datetime(2026, 5, 19, 22, 45, tzinfo=UTC),
    )
    bundle = build_bts_outcome_summaries(
        event,
        _facility("JFK", "KJFK"),
        rows,
        source_id="bts:2026-05",
        source_snapshot_sha256=ARCHIVE_SHA256,
    )

    assert bundle.status == "ok"
    assert [summary.phase for summary in bundle.summaries] == ["baseline", "active", "recovery"]
    active = bundle.summaries[1]
    assert active.window_start == event.operational_start
    assert active.window_end == event.operational_end
    assert active.causal_claim is False
    assert active.scheduled_arrival_semantics == "public scheduled-demand proxy; not FAA arrival demand"
    assert active.weather_delay_semantics == "carrier-reported attribution; not a causal claim"
    assert all("arrivalDemand" not in summary.model_dump_json() for summary in bundle.summaries)


@pytest.mark.parametrize(
    ("event_id", "facility", "start", "end", "expected"),
    [
        (
            "urn:aviation-agentic-ai:event:ground-stop:123",
            _facility("JFK", "KJFK"),
            datetime(2026, 5, 19, 21, tzinfo=UTC),
            datetime(2026, 5, 19, 22, 45, tzinfo=UTC),
            (20, 18, 2, 0),
        ),
        (
            "urn:aviation-agentic-ai:event:ground-delay-program:138",
            _facility("JFK", "KJFK"),
            datetime(2026, 5, 19, 22, 5, tzinfo=UTC),
            datetime(2026, 5, 20, 2, 59, tzinfo=UTC),
            (77, 68, 4, 5),
        ),
        (
            "urn:aviation-agentic-ai:event:ground-delay-program-cancellation:020",
            _facility("EWR", "KEWR"),
            datetime(2026, 5, 20, 1, 24, tzinfo=UTC),
            datetime(2026, 5, 20, 5, 46, tzinfo=UTC),
            (50, 49, 1, 0),
        ),
    ],
)
def test_frozen_cases_have_the_exact_active_proxy_counts(normalized, event_id, facility, start, end, expected):
    bundle = build_bts_outcome_summaries(
        _event(event_id, start, end),
        facility,
        normalized.rows,
        source_id="bts:2026-05",
        source_snapshot_sha256=ARCHIVE_SHA256,
    )
    active = next(summary for summary in bundle.summaries if summary.phase == "active")
    assert (
        active.scheduled_arrival_count_proxy,
        active.completed_arrival_count,
        active.cancelled_count,
        active.diverted_count,
    ) == expected


def test_blocks_ambiguous_facility_binding(normalized):
    facility = CanonicalEntity(
        entity_id="urn:test:facility:ambiguous",
        entity_type=EntityType.AIRPORT,
        preferred_label="ambiguous",
        codes=[CodeValue(scheme="IATA", value="JFK"), CodeValue(scheme="IATA", value="JFK")],
    )
    bundle = build_bts_outcome_summaries(
        _event("urn:test:ambiguous", datetime(2026, 5, 19, 21, tzinfo=UTC), datetime(2026, 5, 19, 22, tzinfo=UTC)),
        facility,
        normalized.rows,
        source_id="bts:2026-05",
        source_snapshot_sha256=ARCHIVE_SHA256,
    )
    assert bundle.status == "blocked"
    assert "exactly one IATA" in bundle.failure_reason
