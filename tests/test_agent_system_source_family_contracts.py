from __future__ import annotations

import pytest

from aviation_agentic_ai.agent_system.contracts import (
    SourceFamily,
    SourceRecord,
    ValidationProfileRef,
)


def test_extended_source_families_serialize_through_source_record_contract() -> None:
    expected_values = {
        "BTS_FLIGHT_OPERATION": "bts_flight_operation",
        "FAA_AIRCRAFT_REGISTRY": "faa_aircraft_registry",
        "NASA_ATMONTO_INSTANCE": "nasa_atmonto_instance",
        "NASR_AIRSPACE": "nasr_airspace",
        "HISTORICAL_METAR_SPECI": "historical_metar_speci",
    }

    serialized = {
        member_name: SourceRecord(
            source_id=f"source:{member_value}",
            family=getattr(SourceFamily, member_name),
            content="source evidence",
        ).model_dump(mode="json")["family"]
        for member_name, member_value in expected_values.items()
    }

    assert serialized == expected_values


def test_existing_source_family_values_remain_available() -> None:
    assert {
        "ATCSCC_ADVISORY": SourceFamily.ATCSCC_ADVISORY.value,
        "NASR_FACILITY": SourceFamily.NASR_FACILITY.value,
        "FAA_TERM": SourceFamily.FAA_TERM.value,
        "METAR": SourceFamily.METAR.value,
        "TAF": SourceFamily.TAF.value,
        "BTS_ON_TIME": SourceFamily.BTS_ON_TIME.value,
    } == {
        "ATCSCC_ADVISORY": "atcscc_advisory",
        "NASR_FACILITY": "nasr_facility",
        "FAA_TERM": "faa_term",
        "METAR": "metar",
        "TAF": "taf",
        "BTS_ON_TIME": "bts_on_time",
    }


@pytest.mark.parametrize(
    "layer",
    [
        "decision",
        "weather",
        "public_operational_observation",
        "flight_operation",
        "aeronautical_reference",
        "trajectory",
    ],
)
def test_validation_profile_ref_accepts_current_and_flight_airspace_layers(
    layer: str,
) -> None:
    profile = ValidationProfileRef(
        profile_id=f"profile:{layer}",
        profile_checksum="a" * 64,
        layer=layer,
    )

    assert profile.model_dump(mode="json")["layer"] == layer
