"""Typed Flight, Airspace, Weather, and bounded-association records."""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator

from aviation_agentic_ai.agent_system.contracts import (
    SourceFamily,
    StrictModel,
)
from aviation_agentic_ai.agent_system.knowledge_publication import (
    KnowledgePublicationPackage,
)
from aviation_agentic_ai.utils.identifiers import stable_id


def _source_family_value(value: SourceFamily) -> str:
    return value.value


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _require_aware(value: datetime | None, label: str) -> datetime | None:
    if value is not None and (value.tzinfo is None or value.utcoffset() is None):
        raise ValueError(f"{label} must be timezone-aware")
    return value


class FlightRecord(StrictModel):
    """One source-qualified Flight root under the frozen identity rule."""

    flight_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    source_family: SourceFamily
    service_date: date
    reporting_carrier: str = Field(min_length=1)
    flight_number: str = Field(min_length=1)
    origin_airport_id: str = Field(min_length=1)
    destination_airport_id: str = Field(min_length=1)
    scheduled_departure_key: str = Field(min_length=1)
    tail_number: str | None = Field(default=None, min_length=1)
    scheduled_departure: datetime | None = None
    actual_wheels_off: datetime | None = None
    time_basis: Literal["origin_local", "utc", "unknown"]
    cancelled: bool
    diverted: bool

    @model_validator(mode="after")
    def _validate_record(self) -> FlightRecord:
        expected_id = stable_id(
            "flight",
            _source_family_value(self.source_family),
            self.service_date.isoformat(),
            self.reporting_carrier,
            self.flight_number,
            self.origin_airport_id,
            self.destination_airport_id,
            self.scheduled_departure_key,
        )
        if self.flight_id != expected_id:
            raise ValueError("Flight identity does not match the source-qualified key")
        if self.time_basis == "utc":
            _require_aware(self.scheduled_departure, "scheduled departure")
            _require_aware(self.actual_wheels_off, "actual wheels-off time")
        return self


class FlightPublicationRecord(StrictModel):
    """Flight detail row referencing the general publication spine."""

    publication_id: str = Field(min_length=1)
    flight_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    primary_source_version_id: str = Field(min_length=1)


class AirCarrierRecord(StrictModel):
    carrier_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    source_family: SourceFamily
    carrier_code: str = Field(min_length=1)
    display_name: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> AirCarrierRecord:
        expected_id = stable_id(
            "air-carrier", _source_family_value(self.source_family), self.carrier_code
        )
        if self.carrier_id != expected_id:
            raise ValueError("air carrier identity does not match source key")
        return self


class AircraftRecord(StrictModel):
    aircraft_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    source_family: SourceFamily
    registration_number: str = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> AircraftRecord:
        expected_id = stable_id(
            "aircraft",
            _source_family_value(self.source_family),
            self.registration_number,
        )
        if self.aircraft_id != expected_id:
            raise ValueError("aircraft identity does not match source key")
        return self


class AircraftModelRecord(StrictModel):
    aircraft_model_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    source_family: SourceFamily
    manufacturer_code: str = Field(min_length=1)
    model_code: str = Field(min_length=1)
    display_name: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> AircraftModelRecord:
        expected_id = stable_id(
            "aircraft-model",
            _source_family_value(self.source_family),
            self.manufacturer_code,
            self.model_code,
        )
        if self.aircraft_model_id != expected_id:
            raise ValueError("aircraft model identity does not match source key")
        return self


class AirportRecord(StrictModel):
    airport_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    source_family: SourceFamily
    airport_code: str = Field(min_length=1)
    display_name: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> AirportRecord:
        expected_id = stable_id(
            "airport", _source_family_value(self.source_family), self.airport_code
        )
        if self.airport_id != expected_id:
            raise ValueError("airport identity does not match source key")
        return self


class ARTCCRecord(StrictModel):
    artcc_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    source_family: SourceFamily
    artcc_code: str = Field(min_length=1)
    display_name: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> ARTCCRecord:
        expected_id = stable_id(
            "artcc", _source_family_value(self.source_family), self.artcc_code
        )
        if self.artcc_id != expected_id:
            raise ValueError("ARTCC identity does not match source key")
        return self


class AirportARTCCAssignmentRecord(StrictModel):
    """One role-preserving, publication-version-bound NASR assignment."""

    assignment_id: str = Field(min_length=1)
    airport_publication_id: str = Field(min_length=1)
    artcc_publication_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    assignment_role: Literal["boundary", "responsible"]
    effective_start: datetime | None = None
    effective_end: datetime | None = None
    procedure_id: str = Field(min_length=1)
    procedure_checksum: str = Field(min_length=64, max_length=64)
    derivation_id: str = Field(min_length=1)

    @field_validator("effective_start", "effective_end")
    @classmethod
    def _validate_timezones(cls, value: datetime | None) -> datetime | None:
        return _require_aware(value, "assignment effective time")

    @model_validator(mode="after")
    def _validate_record(self) -> AirportARTCCAssignmentRecord:
        if (
            self.effective_start is not None
            and self.effective_end is not None
            and self.effective_end <= self.effective_start
        ):
            raise ValueError("effective end must be after effective start")
        expected_id = stable_id(
            "airport-artcc-assignment",
            self.airport_publication_id,
            self.artcc_publication_id,
            self.assignment_role,
            self.effective_start.isoformat() if self.effective_start else "",
            self.effective_end.isoformat() if self.effective_end else "",
            self.procedure_checksum,
        )
        if self.assignment_id != expected_id:
            raise ValueError("airport ARTCC assignment identity does not match")
        return self


class NavigationFixRecord(StrictModel):
    fix_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    source_family: SourceFamily
    fix_identifier: str = Field(min_length=1)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> NavigationFixRecord:
        expected_id = stable_id(
            "navigation-fix",
            _source_family_value(self.source_family),
            self.fix_identifier,
        )
        if self.fix_id != expected_id:
            raise ValueError("navigation fix identity does not match source key")
        return self


class SectorRecord(StrictModel):
    sector_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    source_family: SourceFamily
    sector_identifier: str = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> SectorRecord:
        if (
            self.source_family is SourceFamily.NASA_ATMONTO_INSTANCE
            and self.sector_id.startswith(("http://", "https://", "urn:"))
        ):
            return self
        expected_id = stable_id(
            "sector",
            _source_family_value(self.source_family),
            self.sector_identifier,
        )
        if self.sector_id != expected_id:
            raise ValueError("sector identity does not match source key")
        return self


class RouteRecord(StrictModel):
    route_id: str = Field(min_length=1)
    flight_publication_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    source_route_key: str = Field(min_length=1)
    route_kind: Literal["actual", "planned"]

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> RouteRecord:
        expected_id = stable_id(
            "route", self.flight_publication_id, self.source_route_key
        )
        if self.route_id != expected_id:
            raise ValueError("route identity does not match source key")
        return self


class TrackPointRecord(StrictModel):
    track_point_id: str = Field(min_length=1)
    route_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    sequence_number: int = Field(ge=0)
    reporting_time: datetime
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    ground_speed: float | None = Field(default=None, ge=0)
    navigation_fix_id: str | None = Field(default=None, min_length=1)
    sector_ids: tuple[str, ...] = ()
    source_version_id: str = Field(min_length=1)
    source_anchor_id: str = Field(min_length=1)

    @field_validator("reporting_time")
    @classmethod
    def _validate_reporting_time(cls, value: datetime) -> datetime:
        return _require_aware(value, "track-point reporting time")  # type: ignore[return-value]

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> TrackPointRecord:
        expected_id = stable_id(
            "track-point",
            self.route_id,
            self.sequence_number,
            self.source_version_id,
            self.source_anchor_id,
        )
        if self.track_point_id != expected_id:
            raise ValueError("track-point identity does not match source record")
        if len(set(self.sector_ids)) != len(self.sector_ids):
            raise ValueError("track-point sectors must be unique")
        return self


class SectorPassageRecord(StrictModel):
    passage_id: str = Field(min_length=1)
    flight_publication_id: str = Field(min_length=1)
    route_id: str = Field(min_length=1)
    track_point_id: str = Field(min_length=1)
    sector_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    reporting_time: datetime
    derivation_id: str = Field(min_length=1)

    @field_validator("reporting_time")
    @classmethod
    def _validate_reporting_time(cls, value: datetime) -> datetime:
        return _require_aware(value, "sector-passage reporting time")  # type: ignore[return-value]

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> SectorPassageRecord:
        expected_id = stable_id(
            "sector-passage",
            self.flight_publication_id,
            self.track_point_id,
            self.sector_id,
            self.derivation_id,
        )
        if self.passage_id != expected_id:
            raise ValueError("sector-passage identity does not match inputs")
        return self


class WeatherObservationRecord(StrictModel):
    observation_id: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    source_family: SourceFamily
    station_id: str = Field(min_length=1)
    observed_at: datetime
    report_type: Literal["METAR", "SPECI"]
    raw_report: str = Field(min_length=1)
    phenomenon_tokens: tuple[str, ...] = ()
    source_version_id: str = Field(min_length=1)
    time_basis: Literal["utc"] = "utc"

    @field_validator("observed_at")
    @classmethod
    def _validate_observed_at(cls, value: datetime) -> datetime:
        return _require_aware(value, "weather observation time")  # type: ignore[return-value]

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> WeatherObservationRecord:
        expected_id = stable_id(
            "weather-observation",
            _source_family_value(self.source_family),
            self.station_id,
            self.observed_at.isoformat(),
            self.source_version_id,
        )
        if self.observation_id != expected_id:
            raise ValueError("weather observation identity does not match source record")
        return self


class FlightWeatherAssociationRecord(StrictModel):
    """One stored proximity observation; nearest/all is selected at query time."""

    association_id: str = Field(min_length=1)
    flight_publication_id: str = Field(min_length=1)
    weather_publication_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    flight_time_field: str = Field(min_length=1)
    flight_time: datetime
    observation_time: datetime
    delta_seconds: int = Field(ge=0)
    procedure_id: str = Field(min_length=1)
    procedure_checksum: str = Field(min_length=64, max_length=64)
    derivation_id: str = Field(min_length=1)
    causal_claim: Literal[False] = False

    @field_validator("flight_time", "observation_time")
    @classmethod
    def _validate_times(cls, value: datetime) -> datetime:
        return _require_aware(value, "flight-weather association time")  # type: ignore[return-value]

    @model_validator(mode="after")
    def _validate_record(self) -> FlightWeatherAssociationRecord:
        observed_delta = int(abs((self.flight_time - self.observation_time).total_seconds()))
        if self.delta_seconds != observed_delta:
            raise ValueError("weather association delta does not match timestamps")
        expected_id = stable_id(
            "flight-weather-association",
            self.flight_publication_id,
            self.weather_publication_id,
            self.flight_time_field,
            self.procedure_checksum,
        )
        if self.association_id != expected_id:
            raise ValueError("flight-weather association identity does not match")
        return self


class FlightAircraftSnapshotMatchRecord(StrictModel):
    """A later registry-snapshot join, never a historical model assertion."""

    match_id: str = Field(min_length=1)
    flight_publication_id: str = Field(min_length=1)
    aircraft_publication_id: str = Field(min_length=1)
    aircraft_model_publication_id: str | None = Field(default=None, min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    registry_snapshot_at: datetime
    matched_registration_number: str = Field(min_length=1)
    match_status: Literal["exact", "ambiguous", "unmatched"]
    procedure_id: str = Field(min_length=1)
    procedure_checksum: str = Field(min_length=64, max_length=64)
    derivation_id: str = Field(min_length=1)
    historical_model_claim: Literal[False] = False

    @field_validator("registry_snapshot_at")
    @classmethod
    def _validate_snapshot_time(cls, value: datetime) -> datetime:
        return _require_aware(value, "registry snapshot time")  # type: ignore[return-value]

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> FlightAircraftSnapshotMatchRecord:
        expected_id = stable_id(
            "flight-aircraft-snapshot-match",
            self.flight_publication_id,
            self.aircraft_publication_id,
            self.aircraft_model_publication_id or "",
            self.procedure_checksum,
        )
        if self.match_id != expected_id:
            raise ValueError("aircraft snapshot match identity does not match")
        return self


class FlightTMIApplicabilityRecord(StrictModel):
    """Versioned candidate evaluation, not proof of actual TMI control."""

    applicability_id: str = Field(min_length=1)
    flight_publication_id: str = Field(min_length=1)
    tmi_publication_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    tmi_family: str = Field(min_length=1)
    status: Literal["applicability_candidate", "unknown", "not_applicable"]
    rule_id: str = Field(min_length=1)
    rule_checksum: str = Field(min_length=64, max_length=64)
    normalized_inputs: dict[str, Any]
    limitation: str = Field(min_length=1)
    derivation_id: str = Field(min_length=1)
    actual_control_claim: Literal[False] = False

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> FlightTMIApplicabilityRecord:
        expected_id = stable_id(
            "flight-tmi-applicability",
            self.flight_publication_id,
            self.tmi_publication_id,
            self.rule_checksum,
            _canonical_json(self.normalized_inputs),
        )
        if self.applicability_id != expected_id:
            raise ValueError("TMI applicability identity does not match rule inputs")
        return self


class FlightAirspaceMaterialization(StrictModel):
    """Domain rows atomically materialized with one accepted publication.

    High-frequency Route, TrackPoint, and SectorPassage records are structured
    children of an immutable Flight publication; they are not promoted to
    independent generic publications.
    """

    publication: KnowledgePublicationPackage
    flight: FlightRecord | None = None
    flight_publication: FlightPublicationRecord | None = None
    air_carriers: tuple[AirCarrierRecord, ...] = ()
    aircraft: tuple[AircraftRecord, ...] = ()
    aircraft_models: tuple[AircraftModelRecord, ...] = ()
    airports: tuple[AirportRecord, ...] = ()
    artccs: tuple[ARTCCRecord, ...] = ()
    airport_artcc_assignments: tuple[AirportARTCCAssignmentRecord, ...] = ()
    navigation_fixes: tuple[NavigationFixRecord, ...] = ()
    sectors: tuple[SectorRecord, ...] = ()
    routes: tuple[RouteRecord, ...] = ()
    track_points: tuple[TrackPointRecord, ...] = ()
    sector_passages: tuple[SectorPassageRecord, ...] = ()
    weather_observations: tuple[WeatherObservationRecord, ...] = ()
    flight_weather_associations: tuple[FlightWeatherAssociationRecord, ...] = ()
    aircraft_snapshot_matches: tuple[FlightAircraftSnapshotMatchRecord, ...] = ()
    tmi_applicability: tuple[FlightTMIApplicabilityRecord, ...] = ()

    @model_validator(mode="after")
    def _validate_domain_scope(self) -> FlightAirspaceMaterialization:
        package = self.publication
        publication_id = package.publication.publication_id
        temporal_domain_id = package.publication.temporal_domain_id
        if (self.flight is None) != (self.flight_publication is None):
            raise ValueError("flight root and publication detail must occur together")
        if self.flight is not None and self.flight_publication is not None:
            if package.root.root_kind != "flight":
                raise ValueError("flight detail requires a flight publication")
            if self.flight.flight_id != package.root.root_id:
                raise ValueError("flight detail differs from publication root")
            if self.flight_publication.publication_id != publication_id:
                raise ValueError("flight detail references another publication")
            if self.flight_publication.flight_id != self.flight.flight_id:
                raise ValueError("flight publication references another flight")
        for collection in (
            self.air_carriers,
            self.aircraft,
            self.aircraft_models,
            self.airports,
            self.artccs,
            self.airport_artcc_assignments,
            self.navigation_fixes,
            self.sectors,
            self.routes,
            self.track_points,
            self.sector_passages,
            self.weather_observations,
            self.flight_weather_associations,
            self.aircraft_snapshot_matches,
            self.tmi_applicability,
        ):
            for record in collection:
                if record.temporal_domain_id != temporal_domain_id:
                    raise ValueError("domain row differs from publication temporal domain")
        if self.sectors and package.root.root_kind == "sector":
            if len(self.sectors) != 1 or self.sectors[0].sector_id != package.root.root_id:
                raise ValueError("sector detail differs from publication root")
        if self.weather_observations:
            if package.root.root_kind != "weather_observation":
                raise ValueError("weather detail requires a weather publication")
            for observation in self.weather_observations:
                if observation.observation_id != package.root.root_id:
                    raise ValueError("weather detail differs from publication root")
                if observation.publication_id != publication_id:
                    raise ValueError("weather detail references another publication")
        route_ids = {route.route_id for route in self.routes}
        point_ids = {point.track_point_id for point in self.track_points}
        for route in self.routes:
            if self.flight_publication is None or (
                route.flight_publication_id != self.flight_publication.publication_id
            ):
                raise ValueError("route is outside the flight publication")
        for point in self.track_points:
            if point.route_id not in route_ids:
                raise ValueError("track point references an unknown route")
        for passage in self.sector_passages:
            if passage.route_id not in route_ids or passage.track_point_id not in point_ids:
                raise ValueError("sector passage references an unknown route or point")
        structured_owner_ids = {
            package.root.root_id,
            *(route.route_id for route in self.routes),
            *(point.track_point_id for point in self.track_points),
            *(passage.passage_id for passage in self.sector_passages),
            *(observation.observation_id for observation in self.weather_observations),
            *(row.assignment_id for row in self.airport_artcc_assignments),
            *(row.association_id for row in self.flight_weather_associations),
            *(row.match_id for row in self.aircraft_snapshot_matches),
            *(row.applicability_id for row in self.tmi_applicability),
        }
        for link in package.evidence_links:
            if (
                link.owner_kind == "structured_record"
                and link.owner_id not in structured_owner_ids
            ):
                raise ValueError("structured evidence owner is not materialized")
        return self
