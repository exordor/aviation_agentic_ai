"""Shared authority entities used by ingestion and historical experiments."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StrictAuthorityModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EntityType(str, Enum):
    AIRPORT = "airport"
    WEATHER_STATION = "weather_station"
    ARTCC = "artcc"
    TRACON = "tracon"
    ATCT = "atct"
    NAVAID = "navaid"
    FIX = "fix"
    AIRSPACE = "airspace"
    UNKNOWN_FACILITY = "unknown_facility"


class TermCategory(str, Enum):
    TRAFFIC_MANAGEMENT_INITIATIVE = "traffic_management_initiative"
    FLOW_MANAGEMENT = "flow_management"
    FACILITY_TYPE = "facility_type"
    ROUTE_OR_AIRSPACE = "route_or_airspace"
    WEATHER = "weather"
    STATUS_OR_ACTION = "status_or_action"
    OPERATIONAL_PROCEDURE = "operational_procedure"


class CodeValue(StrictAuthorityModel):
    scheme: str = Field(min_length=1)
    value: str = Field(min_length=1)


class CanonicalEntity(StrictAuthorityModel):
    entity_id: str = Field(min_length=1)
    entity_type: EntityType
    preferred_label: str = Field(min_length=1)
    codes: list[CodeValue]
    aliases: list[str] = Field(default_factory=list)
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    source_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TermDefinition(StrictAuthorityModel):
    text: str = Field(min_length=1)
    source_ref: str = Field(min_length=1)


class TermConcept(StrictAuthorityModel):
    term_id: str = Field(min_length=1)
    abbreviation: str = Field(min_length=1)
    preferred_label: str = Field(min_length=1)
    term_category: TermCategory
    aliases: list[str] = Field(default_factory=list)
    definitions: list[TermDefinition] = Field(default_factory=list)
    denotes_schema_term: str | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    source_refs: list[str] = Field(default_factory=list)
