from __future__ import annotations

from datetime import UTC, datetime

import pytest

from aviation_agentic_ai.cross_source.config import load_cross_source_config
from aviation_agentic_ai.cross_source.contracts import (
    CodeValue,
    CrossSourceLink,
    EntityType,
    TimeInterval,
)
from aviation_agentic_ai.cross_source.identifiers import canonical_facility_id


def test_cross_source_config_loads_pinned_cohort() -> None:
    config = load_cross_source_config("configs/cross_source_v1.yaml")

    assert config["snapshot_set_id"] == "cross-source-2026-05-v1"
    assert config["cohort"]["expected_record_count"] == 68
    assert config["sources"]["atcscc_advisories"] == config["cohort"]["advisory_input"]
    assert config["alignment"]["reject_out_of_registry_targets"] is True


def test_canonical_facility_id_keeps_entity_type_and_authority_code() -> None:
    assert (
        canonical_facility_id(EntityType.AIRPORT, "k-jfk")
        == "urn:aviation-agentic-ai:facility:airport:KJFK"
    )
    assert CodeValue(scheme="ICAO", value="KJFK").value == "KJFK"


def test_cross_source_link_cannot_claim_causality() -> None:
    interval = TimeInterval(
        start=datetime(2026, 5, 20, 10, tzinfo=UTC),
        end=datetime(2026, 5, 20, 11, tzinfo=UTC),
    )

    with pytest.raises(ValueError):
        CrossSourceLink(
            link_id="link:test",
            subject_id="advisory:test",
            predicate="overlapsObservationWindow",
            object_id="metar:test",
            link_method="canonical_facility_and_temporal_overlap",
            facility_id="urn:aviation-agentic-ai:facility:airport:KJFK",
            advisory_interval=interval,
            evidence_interval=interval,
            authority_sources=["atcscc:test", "aviationweather:test"],
            evidence_text="linked by facility and time",
            causal_claim=True,
        )
