"""Focused checks for the Flight/Airspace source adapter registry."""

from aviation_agentic_ai.agent_system.flight_airspace_adapters import (
    SOURCE_ADAPTER_KEYS,
    configured_source_keys,
)


def test_configured_source_keys_are_known_and_stable() -> None:
    configured = {
        "nasa_atmonto_instances": {},
        "unknown_source": {},
        "bts_flight_operations": {},
    }

    assert configured_source_keys(configured) == (
        "bts_flight_operations",
        "nasa_atmonto_instances",
    )
    assert SOURCE_ADAPTER_KEYS == (
        "bts_flight_operations",
        "faa_aircraft_registry",
        "historical_metar_speci",
        "nasa_atmonto_instances",
        "nasr_airspace_zip",
    )
