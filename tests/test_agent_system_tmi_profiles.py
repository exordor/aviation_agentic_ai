from __future__ import annotations

from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.tmi_profiles import (
    active_tmi_profiles,
    classify_tmi_family,
    detected_family_counts,
    get_tmi_profile,
)
from aviation_agentic_ai.agent_system.contracts import (
    SourceFamily,
    SourceRecord,
)
from aviation_agentic_ai.agent_system.ingestion_pipeline import (
    preflight_advisory,
)
from aviation_agentic_ai.cross_source.artifacts import read_jsonl
from aviation_agentic_ai.cross_source.evaluation.cohort import (
    select_cross_source_cohort,
)


ROOT = Path(__file__).resolve().parents[1]
ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
ADVISORY_PATH = (
    ROOT
    / "data/processed/nasa_atmonto/aligned/2026-05-14/atcscc_advisories.jsonl"
)


def _frozen_source(source_id: str) -> SourceRecord:
    row = next(
        item
        for item in read_jsonl(ADVISORY_PATH)
        if item["source_id"] == source_id
    )
    return SourceRecord(
        source_id=source_id,
        family=SourceFamily.ATCSCC_ADVISORY,
        content=str(row["text"]),
    )


def test_active_profiles_share_the_tmi_root_and_exact_atmonto_terms() -> None:
    profiles = {profile.code: profile for profile in active_tmi_profiles()}

    assert set(profiles) == {"GDP", "GS", "REROUTE"}
    assert profiles["GDP"].ontology_class == ATM + "GroundDelayProgramTMI"
    assert profiles["GS"].ontology_class == ATM + "GroundStopTMI"
    assert profiles["REROUTE"].ontology_class == ATM + "ReRouteTMI"
    assert profiles["REROUTE"].retrieval_label == "Required Reroute"
    assert all(profile.publication_status == "active" for profile in profiles.values())
    assert profiles["REROUTE"].required_fields == (
        "effective_start",
        "effective_end",
        "extension_probability",
        "implementation_status",
        "issued_time",
        "re_route_reason",
        "re_route_time_type",
        "re_route_type",
    )
    assert "issued_time" in profiles["GDP"].required_fields
    assert "issued_time" in profiles["GS"].required_fields
    assert "extension_probability" in profiles["GS"].required_fields
    assert profiles["REROUTE"].field_mappings == {
        "advisory_number": ATM + "advisoryNumber",
        "effective_end": ATM + "effectiveEndTime",
        "effective_start": ATM + "effectiveStartTime",
        "extension_probability": ATM + "extensionProbability",
        "implementation_status": ATM + "implementationStatus",
        "issued_time": ATM + "issuedTime",
        "re_route_reason": ATM + "reRouteReason",
        "re_route_time_type": ATM + "reRouteTimeType",
        "re_route_type": ATM + "reRouteType",
    }


@pytest.mark.parametrize(
    ("text", "family"),
    [
        ("ATCSCC ADVZY 001 CDM GROUND DELAY PROGRAM", "GDP"),
        ("ATCSCC ADVZY 002 CDM GROUND STOP", "GS"),
        ("ATCSCC ADVZY 003 DCC ROUTE RQD /FL", "REROUTE"),
        ("ATCSCC ADVZY 004 DCC REROUTE CANCELLATION", "REROUTE_CANCELLATION"),
        ("ATCSCC ADVZY 005 DCC/ZBW NATOTS_RQD", "NATOTS"),
        ("ATCSCC ADVZY 006 JFK AIRPORT ARRIVAL DELAYS", "ARRIVAL_DELAY"),
        ("ATCSCC ADVZY 007 ZBW INTERNATIONAL SWAP_FYI", "SWAP"),
        ("ATCSCC ADVZY 008 NY METRO HOTLINE_FYI", "HOTLINE"),
        ("ATCSCC ADVZY 009 INFORMATION ONLY", None),
    ],
)
def test_family_detection_keeps_active_deferred_and_boundary_outcomes_distinct(
    text: str,
    family: str | None,
) -> None:
    assert classify_tmi_family(text) == family


def test_deferred_and_boundary_families_are_not_publishable_profiles() -> None:
    assert get_tmi_profile("REROUTE_CANCELLATION") is not None
    assert get_tmi_profile("REROUTE_CANCELLATION", publishable_only=True) is None
    assert get_tmi_profile("ARRIVAL_DELAY") is not None
    assert get_tmi_profile("ARRIVAL_DELAY", publishable_only=True) is None
    assert get_tmi_profile("UNKNOWN") is None


def test_registry_classifies_the_legacy_nyc_mention_selection() -> None:
    rows = read_jsonl(
        ROOT
        / "data/processed/nasa_atmonto/aligned/2026-05-14/atcscc_advisories.jsonl"
    )
    selection = select_cross_source_cohort(
        rows,
        airport_codes=["JFK", "EWR", "LGA", "KJFK", "KEWR", "KLGA"],
        expected_count=68,
    )

    assert detected_family_counts(selection.records) == {
        "ARRIVAL_DELAY": 7,
        "GDP": 21,
        "GS": 24,
        "HOTLINE": 3,
        "NATOTS": 7,
        "REROUTE": 4,
        "REROUTE_CANCELLATION": 1,
        "SWAP": 1,
    }


def test_legacy_nyc_mention_selection_reproduces_preflight_split() -> None:
    rows = read_jsonl(ADVISORY_PATH)
    selection = select_cross_source_cohort(
        rows,
        airport_codes=["JFK", "EWR", "LGA", "KJFK", "KEWR", "KLGA"],
        expected_count=68,
    )
    results = [
        preflight_advisory(
            SourceRecord(
                source_id=str(row["source_id"]),
                family=SourceFamily.ATCSCC_ADVISORY,
                content=str(row["text"]),
            )
        )
        for row in selection.records
    ]

    assert sum(result is None for result in results) == 46
    assert sum(
        result is not None
        and result.reason == "incomplete core advisory fields"
        for result in results
    ) == 3
    assert sum(
        result is not None
        and result.reason
        == "recognized advisory family outside active publication profile"
        for result in results
    ) == 18
    assert sum(
        result is not None
        and result.reason == "deferred traffic-management lifecycle event"
        for result in results
    ) == 1


@pytest.mark.parametrize(
    "source_id",
    (
        "2026-05-19:138",
        "2026-05-20:020",
        "2026-05-19:123",
        "2026-05-19:120",
        "2026-05-19:108",
        "2026-05-20:137",
    ),
)
def test_cross_family_regression_records_reach_active_preflight(
    source_id: str,
) -> None:
    assert preflight_advisory(_frozen_source(source_id)) is None


@pytest.mark.parametrize(
    ("source_id", "family"),
    (
        ("2026-05-14:059", "ARRIVAL_DELAY"),
        ("2026-05-19:092", "HOTLINE"),
    ),
)
def test_cross_family_boundary_records_remain_non_publishable(
    source_id: str,
    family: str,
) -> None:
    result = preflight_advisory(_frozen_source(source_id))

    assert result is not None
    assert result.status == "insufficient"
    assert result.tmi_family == family
    assert result.reason == (
        "recognized advisory family outside active publication profile"
    )


def test_active_tmi_without_issued_time_is_incomplete() -> None:
    result = preflight_advisory(
        SourceRecord(
            source_id="example:gdp-without-signature",
            family=SourceFamily.ATCSCC_ADVISORY,
            content=(
                "ATCSCC ADVZY 001 CDM 05/19/2026 GROUND DELAY PROGRAM\n"
                "CTL ELEMENT: JFK ELEMENT TYPE: APT\n"
                "PERIOD: 19/2100Z - 19/2245Z\n"
            ),
        )
    )

    assert result is not None
    assert result.status == "insufficient"
    assert result.reason == "incomplete core advisory fields"
