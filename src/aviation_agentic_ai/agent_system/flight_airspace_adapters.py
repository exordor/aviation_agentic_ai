"""Source-adapter registry for the Flight/Airspace ingestion domain.

The ingestion service owns orchestration and publication.  This registry owns
the configurable source boundary, so adding or disabling a source does not
require changing the service's selection logic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FlightAirspaceSourceAdapter:
    """Configuration identity for one deterministic source adapter."""

    config_key: str
    source_role: str


SOURCE_ADAPTERS: tuple[FlightAirspaceSourceAdapter, ...] = (
    FlightAirspaceSourceAdapter("bts_flight_operations", "flight_operations"),
    FlightAirspaceSourceAdapter("faa_aircraft_registry", "aircraft_reference"),
    FlightAirspaceSourceAdapter("historical_metar_speci", "weather_observation"),
    FlightAirspaceSourceAdapter("nasa_atmonto_instances", "atmonto_reference"),
    FlightAirspaceSourceAdapter("nasr_airspace_zip", "airspace_reference"),
)

SOURCE_ADAPTER_KEYS = tuple(adapter.config_key for adapter in SOURCE_ADAPTERS)


def configured_source_keys(configured_sources: object) -> tuple[str, ...]:
    """Return known source keys in stable registry order."""

    if not isinstance(configured_sources, dict):
        return ()
    return tuple(key for key in SOURCE_ADAPTER_KEYS if key in configured_sources)


__all__ = [
    "FlightAirspaceSourceAdapter",
    "SOURCE_ADAPTERS",
    "SOURCE_ADAPTER_KEYS",
    "configured_source_keys",
]
