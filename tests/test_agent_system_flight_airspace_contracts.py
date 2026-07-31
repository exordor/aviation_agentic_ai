"""Domain contracts for Flight, Airspace, Weather, and TMI associations."""

from __future__ import annotations

from datetime import date, datetime, timezone

from pydantic import ValidationError
import pytest

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.flight_airspace_contracts import (
    ARTCCRecord,
    AirCarrierRecord,
    AircraftModelRecord,
    AircraftRecord,
    AirportARTCCAssignmentRecord,
    AirportRecord,
    FlightAircraftSnapshotMatchRecord,
    FlightPublicationRecord,
    FlightRecord,
    FlightTMIApplicabilityRecord,
    FlightWeatherAssociationRecord,
    NavigationFixRecord,
    RouteRecord,
    SectorPassageRecord,
    SectorRecord,
    TrackPointRecord,
    WeatherObservationRecord,
)


UTC = timezone.utc


def test_flight_root_uses_the_frozen_source_qualified_identity_rule() -> None:
    flight = FlightRecord(
        flight_id="flight:aa1c8fa6035676cb",
        temporal_domain_id="proxy-2026-05",
        source_family=SourceFamily.BTS_FLIGHT_OPERATION,
        service_date=date(2026, 5, 20),
        reporting_carrier="DL",
        flight_number="1512",
        origin_airport_id="KATL",
        destination_airport_id="KJFK",
        scheduled_departure_key="2026-05-20|08:30",
        tail_number="N123DL",
        scheduled_departure=datetime(2026, 5, 20, 8, 30),
        actual_wheels_off=datetime(2026, 5, 20, 8, 42),
        time_basis="origin_local",
        cancelled=False,
        diverted=False,
    )
    assert flight.flight_id == "flight:aa1c8fa6035676cb"

    with pytest.raises(ValidationError, match="Flight identity"):
        FlightRecord.model_validate(
            flight.model_dump() | {"scheduled_departure_key": "2026-05-20|09:30"}
        )


def test_reference_entities_retain_source_qualified_identities() -> None:
    carrier = AirCarrierRecord(
        carrier_id="air-carrier:6550a27f814a62ee",
        temporal_domain_id="nasa-atmonto-2014",
        source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
        carrier_code="DAL",
        display_name="Delta Air Lines",
    )
    aircraft = AircraftRecord(
        aircraft_id="aircraft:de08897232efacfd",
        temporal_domain_id="registry-2026-07-28",
        source_family=SourceFamily.FAA_AIRCRAFT_REGISTRY,
        registration_number="N123DL",
    )
    model = AircraftModelRecord(
        aircraft_model_id="aircraft-model:3a73e436ce09f9b1",
        temporal_domain_id="registry-2026-07-28",
        source_family=SourceFamily.FAA_AIRCRAFT_REGISTRY,
        manufacturer_code="AIRBUS",
        model_code="A319-114",
        display_name="Airbus A319-114",
    )
    assert (carrier.carrier_id, aircraft.aircraft_id, model.aircraft_model_id) == (
        "air-carrier:6550a27f814a62ee",
        "aircraft:de08897232efacfd",
        "aircraft-model:3a73e436ce09f9b1",
    )


def test_airport_artcc_assignment_preserves_role_and_effective_interval() -> None:
    airport = AirportRecord(
        airport_id="airport:eb7406054b61b507",
        temporal_domain_id="nasr-2026-05-14",
        source_family=SourceFamily.NASR_AIRSPACE,
        airport_code="KATL",
        display_name="Hartsfield-Jackson Atlanta International",
    )
    artcc = ARTCCRecord(
        artcc_id="artcc:ea3436eaa3bd1a83",
        temporal_domain_id="nasr-2026-05-14",
        source_family=SourceFamily.NASR_AIRSPACE,
        artcc_code="ZTL",
        display_name="Atlanta Center",
    )
    assignment = AirportARTCCAssignmentRecord(
        assignment_id="airport-artcc-assignment:4dd7e1ecada717c3",
        airport_publication_id="publication:airport:katl",
        artcc_publication_id="publication:artcc:ztl",
        temporal_domain_id="nasr-2026-05-14",
        assignment_role="boundary",
        effective_start=datetime(2026, 5, 14, tzinfo=UTC),
        effective_end=datetime(2026, 6, 11, tzinfo=UTC),
        procedure_id="nasr-airport-artcc-role-v1",
        procedure_checksum="d" * 64,
        derivation_id="derivation:nasr-assignment",
    )
    assert airport.airport_code == "KATL"
    assert artcc.artcc_code == "ZTL"
    assert assignment.assignment_role == "boundary"

    with pytest.raises(ValidationError, match="after effective start"):
        AirportARTCCAssignmentRecord.model_validate(
            assignment.model_dump()
            | {"effective_end": datetime(2026, 5, 1, tzinfo=UTC)}
        )


def test_route_track_point_and_sector_passage_preserve_sequence_and_seconds() -> None:
    fix = NavigationFixRecord(
        fix_id="navigation-fix:a48fa197a20e0b7b",
        temporal_domain_id="nasa-atmonto-2014",
        source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
        fix_identifier="FIX:FOO",
        latitude=33.63,
        longitude=-84.44,
    )
    sector = SectorRecord(
        sector_id="sector:8c51a231f0d3763a",
        temporal_domain_id="nasa-atmonto-2014",
        source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
        sector_identifier="ZTLsector040",
    )
    route = RouteRecord(
        route_id="route:9905a7e449543583",
        flight_publication_id="publication:flight:1",
        temporal_domain_id="nasa-atmonto-2014",
        source_route_key="actual-route:1",
        route_kind="actual",
    )
    point = TrackPointRecord(
        track_point_id="track-point:195ebdb84e0c6a16",
        route_id=route.route_id,
        temporal_domain_id="nasa-atmonto-2014",
        sequence_number=7,
        reporting_time=datetime(2014, 7, 15, 2, 12, 25, tzinfo=UTC),
        latitude=33.63,
        longitude=-84.44,
        ground_speed=420.0,
        navigation_fix_id=fix.fix_id,
        sector_ids=(sector.sector_id,),
        source_version_id="source-version:track",
        source_anchor_id="source-anchor:track",
    )
    passage = SectorPassageRecord(
        passage_id="sector-passage:2e1684d111a83f50",
        flight_publication_id="publication:flight:1",
        route_id=route.route_id,
        track_point_id=point.track_point_id,
        sector_id=sector.sector_id,
        temporal_domain_id="nasa-atmonto-2014",
        reporting_time=point.reporting_time,
        derivation_id="derivation:sector-passage",
    )
    assert fix.fix_identifier == "FIX:FOO"
    assert sector.sector_identifier == "ZTLsector040"
    assert route.route_kind == "actual"
    assert point.reporting_time.second == 25
    assert passage.reporting_time == point.reporting_time

    with pytest.raises(ValidationError, match="timezone-aware"):
        TrackPointRecord.model_validate(
            point.model_dump()
            | {"reporting_time": datetime(2014, 7, 15, 2, 12, 25)}
        )


def test_weather_association_is_non_causal_and_temporal_domain_bound() -> None:
    observation = WeatherObservationRecord(
        observation_id="weather-observation:881e0dea6c49d7af",
        publication_id="publication:weather:1",
        temporal_domain_id="proxy-2026-05",
        source_family=SourceFamily.HISTORICAL_METAR_SPECI,
        station_id="KATL",
        observed_at=datetime(2026, 5, 20, 12, tzinfo=UTC),
        report_type="METAR",
        raw_report="KATL 201200Z 18010KT 5SM RA BKN020",
        phenomenon_tokens=("RA",),
        source_version_id="source-version:metar",
    )
    association = FlightWeatherAssociationRecord(
        association_id="flight-weather-association:f88abc2dc739106d",
        flight_publication_id="publication:flight:1",
        weather_publication_id="publication:weather:1",
        temporal_domain_id="proxy-2026-05",
        flight_time_field="actual_wheels_off",
        flight_time=datetime(2026, 5, 20, 12, 5, tzinfo=UTC),
        observation_time=observation.observed_at,
        delta_seconds=300,
        procedure_id="flight-weather-proximity-v1",
        procedure_checksum="e" * 64,
        derivation_id="derivation:weather-association",
        causal_claim=False,
    )
    assert association.delta_seconds == 300
    assert association.causal_claim is False

    with pytest.raises(ValidationError):
        FlightWeatherAssociationRecord.model_validate(
            association.model_dump() | {"causal_claim": True}
        )


def test_registry_snapshot_match_cannot_claim_historical_aircraft_model() -> None:
    match = FlightAircraftSnapshotMatchRecord(
        match_id="flight-aircraft-snapshot-match:7245573647508bd1",
        flight_publication_id="publication:flight:1",
        aircraft_publication_id="publication:aircraft:n123dl",
        aircraft_model_publication_id="publication:model:a319",
        temporal_domain_id="proxy-2026-05",
        registry_snapshot_at=datetime(2026, 7, 28, tzinfo=UTC),
        matched_registration_number="N123DL",
        match_status="exact",
        procedure_id="tail-registry-snapshot-match-v1",
        procedure_checksum="f" * 64,
        derivation_id="derivation:snapshot-match",
        historical_model_claim=False,
    )
    assert match.historical_model_claim is False

    with pytest.raises(ValidationError):
        FlightAircraftSnapshotMatchRecord.model_validate(
            match.model_dump() | {"historical_model_claim": True}
        )


def test_tmi_applicability_is_a_versioned_candidate_not_actual_control() -> None:
    candidate = FlightTMIApplicabilityRecord(
        applicability_id="flight-tmi-applicability:8a7e25ebecc7396e",
        flight_publication_id="publication:flight:1",
        tmi_publication_id="publication:tmi:138",
        temporal_domain_id="proxy-2026-05",
        tmi_family="ground_delay_program",
        status="applicability_candidate",
        rule_id="tmi-applicability-v1",
        rule_checksum="1" * 64,
        normalized_inputs={"destination_match": True, "temporal_overlap": True},
        limitation="No EDCT or actual-control record is available.",
        derivation_id="derivation:tmi-applicability",
        actual_control_claim=False,
    )
    assert candidate.status == "applicability_candidate"
    assert candidate.actual_control_claim is False

    with pytest.raises(ValidationError, match="applicability identity"):
        FlightTMIApplicabilityRecord.model_validate(
            candidate.model_dump()
            | {
                "normalized_inputs": {
                    "destination_match": False,
                    "temporal_overlap": True,
                }
            }
        )


def test_domain_publication_references_general_publication_and_temporal_domain() -> None:
    publication = FlightPublicationRecord(
        publication_id="publication:flight:1",
        flight_id="flight:aa1c8fa6035676cb",
        temporal_domain_id="proxy-2026-05",
        primary_source_version_id="source-version:bts-row",
    )
    assert publication.flight_id == "flight:aa1c8fa6035676cb"
