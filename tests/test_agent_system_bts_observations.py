"""Behavior tests for the deterministic BTS on-time public-observation adapter."""

from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

import aviation_agentic_ai.agent_system.bts_observations as bts_observations
from aviation_agentic_ai.agent_system.bts_observations import (
    ARCHIVE_SHA256,
    MEMBER_SHA256,
    NORMALIZED_SNAPSHOT_SHA256,
    NORMALIZED_SOURCE_ID,
    EXPECTED_FIELDS,
    build_bts_public_observation_summaries,
    infer_destination_arrival_utc,
    normalize_bts_archive,
)
from aviation_agentic_ai.agent_system.contracts import (
    BTSManifestBinding,
    TMIEventContext,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)
from aviation_agentic_ai.authority.contracts import (
    CanonicalEntity,
    CodeValue,
    EntityType,
)


ARCHIVE = Path("/tmp/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2026_5.zip")


def _facility(iata: str, icao: str) -> CanonicalEntity:
    return CanonicalEntity(
        entity_id=f"urn:test:facility:{icao}",
        entity_type=EntityType.AIRPORT,
        preferred_label=icao,
        codes=[CodeValue(scheme="IATA", value=iata), CodeValue(scheme="ICAO", value=icao)],
    )


def _event(event_id: str, start: datetime, end: datetime) -> TMIEventContext:
    return TMIEventContext(
        run_id=f"run:{event_id}",
        event_id=event_id,
        advisory_source_id=f"advisory:{event_id}",
        advisory_issued_at=start - timedelta(hours=1),
        operational_start=start,
        operational_end=end,
    )


def _seed_inputs(snapshot_sha256: str = NORMALIZED_SNAPSHOT_SHA256) -> dict[str, object]:
    profile = next(
        profile
        for profile in load_validation_profile_registry(
            decision_guide=load_schema_guide()
        ).profiles
        if profile.ref.layer == "public_operational_observation"
    )
    assert profile.aggregation_procedure is not None
    return {
        "manifest_binding": BTSManifestBinding(
            source_id=NORMALIZED_SOURCE_ID,
            archive_sha256=ARCHIVE_SHA256,
            normalized_snapshot_sha256=snapshot_sha256,
        ),
        "aggregation_procedure": profile.aggregation_procedure,
    }


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
    assert manifest["expected_total_column_count"] == 110
    assert manifest["expected_named_field_count"] == 109
    assert manifest["expected_terminal_unnamed_column_count"] == 1
    assert manifest["source_fields"] == [*EXPECTED_FIELDS, ""]
    assert manifest["timezone"] == "America/New_York"
    assert hashlib.sha256(output.read_bytes()).hexdigest() == manifest["normalized_sha256"]
    assert manifest["normalized_sha256"] == NORMALIZED_SNAPSHOT_SHA256
    assert manifest["source_id"] == NORMALIZED_SOURCE_ID
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


def test_normalization_rejects_the_member_checksum_before_parsing(monkeypatch, tmp_path):
    monkeypatch.setattr("aviation_agentic_ai.agent_system.bts_observations.MEMBER_SHA256", "0" * 64)
    blocked = normalize_bts_archive(
        ARCHIVE,
        output_path=tmp_path / "bad-member.jsonl",
        manifest_path=tmp_path / "bad-member-manifest.json",
    )
    assert blocked.status == "blocked"
    assert "member checksum" in blocked.failure_reason


def test_normalization_rejects_a_nonempty_terminal_column(monkeypatch, tmp_path):
    archive = tmp_path / "terminal.zip"
    with zipfile.ZipFile(archive, "w") as zipped:
        zipped.writestr(
            "member.csv",
            ",".join((*EXPECTED_FIELDS, "")) + "\n" + ",".join(("" for _ in EXPECTED_FIELDS)) + ",not-empty\n",
        )
    monkeypatch.setattr("aviation_agentic_ai.agent_system.bts_observations.ARCHIVE_SHA256", hashlib.sha256(archive.read_bytes()).hexdigest())
    monkeypatch.setattr("aviation_agentic_ai.agent_system.bts_observations.MEMBER_NAME", "member.csv")
    with zipfile.ZipFile(archive) as zipped:
        monkeypatch.setattr("aviation_agentic_ai.agent_system.bts_observations.MEMBER_SHA256", hashlib.sha256(zipped.read("member.csv")).hexdigest())
    blocked = normalize_bts_archive(
        archive,
        output_path=tmp_path / "terminal.jsonl",
        manifest_path=tmp_path / "terminal-manifest.json",
    )
    assert blocked.status == "blocked"
    assert "terminal unnamed" in blocked.failure_reason


def test_normalization_rejects_duplicate_natural_keys(monkeypatch, tmp_path):
    row = {field: "" for field in EXPECTED_FIELDS}
    row.update(
        {
            "FlightDate": "2026-05-19",
            "Reporting_Airline": "AA",
            "DOT_ID_Reporting_Airline": "19805",
            "IATA_CODE_Reporting_Airline": "AA",
            "Flight_Number_Reporting_Airline": "100",
            "OriginAirportSeqID": "1234501",
            "Origin": "ORD",
            "DestAirportSeqID": "1247805",
            "Dest": "JFK",
            "CRSDepTime": "0100",
            "CRSArrTime": "0200",
            "CRSElapsedTime": "60.00",
            "Cancelled": "0.00",
            "Diverted": "0.00",
        }
    )
    archive = tmp_path / "duplicates.zip"
    member = "member.csv"
    with zipfile.ZipFile(archive, "w") as zipped:
        header = ",".join((*EXPECTED_FIELDS, "")) + "\n"
        row_line = ",".join(row[field] for field in EXPECTED_FIELDS) + ",\n"
        zipped.writestr(member, header + row_line * 1_978)
    monkeypatch.setattr(
        bts_observations, "ARCHIVE_SHA256", hashlib.sha256(archive.read_bytes()).hexdigest()
    )
    monkeypatch.setattr(bts_observations, "MEMBER_NAME", member)
    with zipfile.ZipFile(archive) as zipped:
        monkeypatch.setattr(
            bts_observations, "MEMBER_SHA256", hashlib.sha256(zipped.read(member)).hexdigest()
        )
    blocked = normalize_bts_archive(
        archive,
        output_path=tmp_path / "duplicates.jsonl",
        manifest_path=tmp_path / "duplicates-manifest.json",
    )
    assert blocked.status == "blocked"
    assert "duplicate BTS natural key" in blocked.failure_reason


def test_infers_overnight_destination_arrival_and_real_iana_dst_offsets():
    same_day = infer_destination_arrival_utc("2026-05-19", 900, 1130, 150)
    overnight = infer_destination_arrival_utc("2026-05-19", 2300, 45, 105)
    winter = infer_destination_arrival_utc("2026-01-15", 2200, 30, 150)

    assert same_day == datetime(2026, 5, 19, 15, 30, tzinfo=UTC)
    assert overnight == datetime(2026, 5, 20, 4, 45, tzinfo=UTC)
    assert winter == datetime(2026, 1, 16, 5, 30, tzinfo=UTC)
    with pytest.raises(ValueError, match="residual"):
        infer_destination_arrival_utc("2026-05-19", 100, 100, 5_000)
    with pytest.raises(ValueError, match="ambiguous"):
        infer_destination_arrival_utc("2026-05-19", 100, 100, 720)
    assert infer_destination_arrival_utc("2026-05-19", 2300, 2400, 60) == datetime(
        2026, 5, 20, 4, tzinfo=UTC
    )


def test_summaries_use_half_open_windows_and_preserve_null_aggregates(normalized):
    rows = normalized.rows
    event = _event(
        "urn:test:half-open",
        datetime(2026, 5, 19, 21, tzinfo=UTC),
        datetime(2026, 5, 19, 22, 45, tzinfo=UTC),
    )
    bundle = build_bts_public_observation_summaries(
        event,
        _facility("JFK", "KJFK"),
        rows,
        source_id=NORMALIZED_SOURCE_ID,
        source_snapshot_sha256=NORMALIZED_SNAPSHOT_SHA256,
        **_seed_inputs(),
    )

    assert bundle.status == "ok"
    assert [summary.phase for summary in bundle.summaries] == ["baseline", "active", "recovery"]
    active = bundle.summaries[1]
    assert active.window_start == event.operational_start
    assert active.window_end == event.operational_end
    assert active.causal_claim is False
    assert active.reporting_scope == (
        "BTS On-Time reporting carriers and scheduled domestic passenger operations."
    )
    assert all("arrivalDemand" not in summary.model_dump_json() for summary in bundle.summaries)
    assert active.summary_id != ""


def test_summary_windows_and_ids_are_canonical_utc(normalized):
    event = _event(
        "urn:test:offset-clocks",
        datetime(2026, 5, 19, 17, tzinfo=ZoneInfo("America/New_York")),
        datetime(2026, 5, 19, 18, tzinfo=ZoneInfo("America/New_York")),
    )
    bundle = build_bts_public_observation_summaries(
        event,
        _facility("JFK", "KJFK"),
        normalized.rows,
        source_id=NORMALIZED_SOURCE_ID,
        source_snapshot_sha256=NORMALIZED_SNAPSHOT_SHA256,
        **_seed_inputs(),
    )
    active = bundle.summaries[1]
    assert active.window_start == datetime(2026, 5, 19, 21, tzinfo=UTC)
    assert active.window_end == datetime(2026, 5, 19, 22, tzinfo=UTC)
    assert NORMALIZED_SOURCE_ID in active.summary_id


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
def test_frozen_cases_have_the_exact_active_bts_reported_counts(normalized, event_id, facility, start, end, expected):
    bundle = build_bts_public_observation_summaries(
        _event(event_id, start, end),
        facility,
        normalized.rows,
        source_id=NORMALIZED_SOURCE_ID,
        source_snapshot_sha256=NORMALIZED_SNAPSHOT_SHA256,
        **_seed_inputs(),
    )
    active = next(summary for summary in bundle.summaries if summary.phase == "active")
    assert (
        active.scheduled_arrival_count,
        active.completed_arrival_count,
        active.cancelled_count,
        active.diverted_count,
    ) == expected


def test_summary_selects_bts_rows_for_a_nasr_faa_icao_airport(normalized):
    """A NASR airport without IATA metadata must still select BTS JFK rows."""

    facility = CanonicalEntity(
        entity_id="urn:test:facility:airport:KJFK",
        entity_type=EntityType.AIRPORT,
        preferred_label="John F Kennedy International Airport",
        codes=[
            CodeValue(scheme="FAA", value="JFK"),
            CodeValue(scheme="ICAO", value="KJFK"),
        ],
    )
    bundle = build_bts_public_observation_summaries(
        _event(
            "urn:test:nasr-faa-icao",
            datetime(2026, 5, 19, 21, tzinfo=UTC),
            datetime(2026, 5, 19, 22, 45, tzinfo=UTC),
        ),
        facility,
        normalized.rows,
        source_id=NORMALIZED_SOURCE_ID,
        source_snapshot_sha256=NORMALIZED_SNAPSHOT_SHA256,
        **_seed_inputs(),
    )

    assert bundle.status == "ok", bundle.failure_reason
    assert next(
        summary for summary in bundle.summaries if summary.phase == "active"
    ).scheduled_arrival_count == 20


def test_blocks_ambiguous_facility_binding(normalized):
    facility = CanonicalEntity(
        entity_id="urn:test:facility:ambiguous",
        entity_type=EntityType.AIRPORT,
        preferred_label="ambiguous",
        codes=[CodeValue(scheme="IATA", value="JFK"), CodeValue(scheme="IATA", value="JFK")],
    )
    bundle = build_bts_public_observation_summaries(
        _event("urn:test:ambiguous", datetime(2026, 5, 19, 21, tzinfo=UTC), datetime(2026, 5, 19, 22, tzinfo=UTC)),
        facility,
        normalized.rows,
        source_id=NORMALIZED_SOURCE_ID,
        source_snapshot_sha256=NORMALIZED_SNAPSHOT_SHA256,
        **_seed_inputs(),
    )
    assert bundle.status == "blocked"
    assert "exactly one IATA" in bundle.failure_reason


def test_blocks_a_nasr_faa_code_when_icao_does_not_match(normalized):
    facility = CanonicalEntity(
        entity_id="urn:test:facility:mismatched",
        entity_type=EntityType.AIRPORT,
        preferred_label="mismatched",
        codes=[
            CodeValue(scheme="FAA", value="JFK"),
            CodeValue(scheme="ICAO", value="KEWR"),
        ],
    )
    bundle = build_bts_public_observation_summaries(
        _event(
            "urn:test:mismatched",
            datetime(2026, 5, 19, 21, tzinfo=UTC),
            datetime(2026, 5, 19, 22, tzinfo=UTC),
        ),
        facility,
        normalized.rows,
        source_id=NORMALIZED_SOURCE_ID,
        source_snapshot_sha256=NORMALIZED_SNAPSHOT_SHA256,
        **_seed_inputs(),
    )

    assert bundle.status == "blocked"
    assert "matching ICAO" in bundle.failure_reason


@pytest.mark.parametrize("field,value", [("Cancelled", 2), ("Diverted", -1), ("ArrDel15", 3)])
def test_persisted_rows_reject_invalid_status_values(normalized, field, value):
    payload = normalized.rows[0].model_dump()
    payload[field] = value
    with pytest.raises(ValidationError):
        type(normalized.rows[0]).model_validate(payload)


def test_persisted_rows_reject_a_timezone_naive_arrival(normalized):
    payload = normalized.rows[0].model_dump()
    payload["scheduled_arrival_utc"] = datetime(2026, 5, 20, 1)
    with pytest.raises(ValidationError, match="timezone-aware"):
        type(normalized.rows[0]).model_validate(payload)


@pytest.mark.parametrize(
    ("source_id", "source_sha256", "rows"),
    [
        ("wrong-source", NORMALIZED_SNAPSHOT_SHA256, lambda rows: rows),
        (NORMALIZED_SOURCE_ID, "0" * 64, lambda rows: rows),
        (NORMALIZED_SOURCE_ID, NORMALIZED_SNAPSHOT_SHA256, lambda rows: rows[1:]),
    ],
)
def test_summary_fails_closed_for_unbound_or_modified_normalized_snapshot(
    normalized, source_id, source_sha256, rows
):
    bundle = build_bts_public_observation_summaries(
        _event("urn:test:source-binding", datetime(2026, 5, 19, 21, tzinfo=UTC), datetime(2026, 5, 19, 22, tzinfo=UTC)),
        _facility("JFK", "KJFK"),
        rows(normalized.rows),
        source_id=source_id,
        source_snapshot_sha256=source_sha256,
        **_seed_inputs(source_sha256),
    )
    assert bundle.status == "blocked"


def test_summary_uses_half_open_boundaries_and_null_aggregates(monkeypatch, normalized):
    selected = [
        normalized.rows[0].model_copy(update={"Dest": "JFK", "scheduled_arrival_utc": datetime(2026, 5, 19, 21, tzinfo=UTC), "ArrDelay": None, "WeatherDelay": None, "NASDelay": None}),
        normalized.rows[1].model_copy(update={"Dest": "JFK", "scheduled_arrival_utc": datetime(2026, 5, 19, 22, tzinfo=UTC), "ArrDelay": None, "WeatherDelay": None, "NASDelay": None}),
    ]
    serialized = "".join(
        json.dumps(row.model_dump(mode="json"), sort_keys=True, separators=(",", ":")) + "\n"
        for row in sorted(selected, key=lambda row: row.row_id)
    ).encode()
    snapshot_sha256 = hashlib.sha256(serialized).hexdigest()
    monkeypatch.setattr(bts_observations, "NORMALIZED_SNAPSHOT_SHA256", snapshot_sha256)
    bundle = build_bts_public_observation_summaries(
        _event("urn:test:nulls", datetime(2026, 5, 19, 21, tzinfo=UTC), datetime(2026, 5, 19, 22, tzinfo=UTC)),
        _facility("JFK", "KJFK"),
        selected,
        source_id=NORMALIZED_SOURCE_ID,
        source_snapshot_sha256=snapshot_sha256,
        **_seed_inputs(snapshot_sha256),
    )
    assert bundle.status == "ok"
    active, recovery = bundle.summaries[1:]
    assert active.scheduled_arrival_count == 1
    assert recovery.scheduled_arrival_count == 1
    assert active.mean_arrival_delay_minutes is None
    assert active.median_arrival_delay_minutes is None
    assert active.carrier_reported_weather_delay_minutes is None
    assert active.carrier_reported_nas_delay_minutes is None


def test_summary_includes_lower_bounds_and_excludes_upper_bounds(monkeypatch, normalized):
    event = _event(
        "urn:test:all-window-boundaries",
        datetime(2026, 5, 19, 21, tzinfo=UTC),
        datetime(2026, 5, 19, 22, tzinfo=UTC),
    )
    timestamps = (
        event.operational_start - timedelta(hours=2),
        event.operational_start,
        event.operational_end,
        event.operational_end + timedelta(hours=6),
    )
    rows = [
        row.model_copy(update={"Dest": "JFK", "scheduled_arrival_utc": timestamp})
        for row, timestamp in zip(normalized.rows[:4], timestamps, strict=True)
    ]
    serialized = "".join(
        json.dumps(row.model_dump(mode="json"), sort_keys=True, separators=(",", ":")) + "\n"
        for row in sorted(rows, key=lambda row: row.row_id)
    ).encode()
    snapshot_sha256 = hashlib.sha256(serialized).hexdigest()
    monkeypatch.setattr(bts_observations, "NORMALIZED_SNAPSHOT_SHA256", snapshot_sha256)

    bundle = build_bts_public_observation_summaries(
        event,
        _facility("JFK", "KJFK"),
        rows,
        source_id=NORMALIZED_SOURCE_ID,
        source_snapshot_sha256=snapshot_sha256,
        **_seed_inputs(snapshot_sha256),
    )

    assert bundle.status == "ok"
    assert [summary.scheduled_arrival_count for summary in bundle.summaries] == [1, 1, 1]


def test_public_observation_bundle_emits_one_byte_stable_seed_per_phase(normalized):
    event = _event(
        "urn:test:derivation-seeds",
        datetime(2026, 5, 19, 21, tzinfo=UTC),
        datetime(2026, 5, 19, 22, 45, tzinfo=UTC),
    )

    first = build_bts_public_observation_summaries(
        event,
        _facility("JFK", "KJFK"),
        normalized.rows,
        source_id=NORMALIZED_SOURCE_ID,
        source_snapshot_sha256=NORMALIZED_SNAPSHOT_SHA256,
        **_seed_inputs(),
    )
    second = build_bts_public_observation_summaries(
        event,
        _facility("JFK", "KJFK"),
        reversed(normalized.rows),
        source_id=NORMALIZED_SOURCE_ID,
        source_snapshot_sha256=NORMALIZED_SNAPSHOT_SHA256,
        **_seed_inputs(),
    )

    assert [seed.summary_id for seed in first.derivation_seeds] == [
        summary.summary_id for summary in first.summaries
    ]
    assert [seed.selected_row_ids for seed in first.derivation_seeds] == [
        tuple(sorted(seed.selected_row_ids)) for seed in first.derivation_seeds
    ]
    assert first.derivation_seeds == second.derivation_seeds
    assert [seed.summary_sha256 for seed in first.derivation_seeds] == [
        seed.summary_sha256 for seed in second.derivation_seeds
    ]
    assert [seed.selected_row_ids_sha256 for seed in first.derivation_seeds] == [
        seed.selected_row_ids_sha256 for seed in second.derivation_seeds
    ]


def test_emitted_seed_procedure_is_the_checksum_verified_profile_descriptor(normalized):
    profile = next(
        profile
        for profile in load_validation_profile_registry(
            decision_guide=load_schema_guide()
        ).profiles
        if profile.ref.layer == "public_operational_observation"
    )
    bundle = build_bts_public_observation_summaries(
        _event(
            "urn:test:profile-procedure",
            datetime(2026, 5, 19, 21, tzinfo=UTC),
            datetime(2026, 5, 19, 22, 45, tzinfo=UTC),
        ),
        _facility("JFK", "KJFK"),
        normalized.rows,
        source_id=NORMALIZED_SOURCE_ID,
        source_snapshot_sha256=NORMALIZED_SNAPSHOT_SHA256,
        **_seed_inputs(),
    )

    assert bundle.status == "ok"
    assert {
        (seed.aggregation_procedure_id, seed.aggregation_procedure_checksum)
        for seed in bundle.derivation_seeds
    } == {
        (profile.aggregation_procedure.procedure_id, profile.aggregation_procedure.checksum)
    }


def test_derivation_seed_uses_the_explicit_manifest_archive_binding(normalized):
    event = _event(
        "urn:test:derivation-integrity",
        datetime(2026, 5, 19, 21, tzinfo=UTC),
        datetime(2026, 5, 19, 22, 45, tzinfo=UTC),
    )
    kwargs = {
        "source_id": NORMALIZED_SOURCE_ID,
        "source_snapshot_sha256": NORMALIZED_SNAPSHOT_SHA256,
        **_seed_inputs(),
    }

    for changed in ({"manifest_binding": BTSManifestBinding(
        source_id=NORMALIZED_SOURCE_ID,
        archive_sha256="0" * 64,
        normalized_snapshot_sha256=NORMALIZED_SNAPSHOT_SHA256,
    )},):
        bundle = build_bts_public_observation_summaries(
            event,
            _facility("JFK", "KJFK"),
            normalized.rows,
            **(kwargs | changed),
        )
        assert bundle.status == "ok"
        assert bundle.derivation_seeds[0].archive_sha256 == "0" * 64


def test_valid_bts_source_with_no_selected_phase_rows_is_insufficient(normalized):
    bundle = build_bts_public_observation_summaries(
        _event(
            "urn:test:no-selected-rows",
            datetime(2026, 5, 25, 21, tzinfo=UTC),
            datetime(2026, 5, 25, 22, tzinfo=UTC),
        ),
        _facility("JFK", "KJFK"),
        normalized.rows,
        source_id=NORMALIZED_SOURCE_ID,
        source_snapshot_sha256=NORMALIZED_SNAPSHOT_SHA256,
        **_seed_inputs(),
    )

    assert bundle.status == "insufficient"
    assert bundle.summaries == []
    assert bundle.derivation_seeds == []


def test_invalid_normalized_row_schema_blocks_the_bundle():
    bundle = build_bts_public_observation_summaries(
        _event(
            "urn:test:invalid-row-schema",
            datetime(2026, 5, 19, 21, tzinfo=UTC),
            datetime(2026, 5, 19, 22, tzinfo=UTC),
        ),
        _facility("JFK", "KJFK"),
        [object()],
        source_id=NORMALIZED_SOURCE_ID,
        source_snapshot_sha256=NORMALIZED_SNAPSHOT_SHA256,
        **_seed_inputs(),
    )

    assert bundle.status == "blocked"
