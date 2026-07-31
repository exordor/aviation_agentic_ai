"""Typed persistent records for the aviation evidence store."""

from __future__ import annotations

import hashlib
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator

from aviation_agentic_ai.agent_system.contracts import (
    SourceFamily,
    StrictModel,
    ValidationProfileRef,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id


class SourceAssetRecord(StrictModel):
    """Checksum metadata for one configured source file or URL."""

    asset_id: str = Field(min_length=1)
    asset_key: str = Field(min_length=1)
    family: SourceFamily
    local_path: str = Field(min_length=1)
    source_url: str | None
    media_type: str = Field(min_length=1)
    content_sha256: str = Field(min_length=64, max_length=64)
    byte_count: int = Field(ge=0)
    effective_start: str | None
    effective_end: str | None

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> SourceAssetRecord:
        expected_id = stable_id(
            "source-asset",
            self.asset_key,
            self.content_sha256,
        )
        if self.asset_id != expected_id:
            raise ValueError("source asset identity does not match checksum")
        return self


class SourceVersionRecord(StrictModel):
    """One immutable exact logical source record."""

    source_version_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    family: SourceFamily
    asset_id: str | None
    content: str = Field(min_length=1)
    content_sha256: str = Field(min_length=64, max_length=64)
    source_url: str | None
    logical_time: str | None
    metadata: dict[str, Any]

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> SourceVersionRecord:
        content_sha256 = hashlib.sha256(self.content.encode("utf-8")).hexdigest()
        if self.content_sha256 != content_sha256:
            raise ValueError("source version checksum does not match content")
        expected_id = stable_id(
            "source-version",
            self.source_id,
            content_sha256,
        )
        if self.source_version_id != expected_id:
            raise ValueError("source version identity does not match content")
        return self


class SourceAnchorRecord(StrictModel):
    """One exact immutable character span in a source version."""

    source_anchor_id: str = Field(min_length=1)
    source_version_id: str = Field(min_length=1)
    char_start: int = Field(ge=0)
    char_end: int = Field(gt=0)
    anchor_kind: Literal["full_record", "text_span"]

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> SourceAnchorRecord:
        if self.char_end <= self.char_start:
            raise ValueError("source anchor end must be after start")
        expected_id = stable_id(
            "source-anchor",
            self.source_version_id,
            self.char_start,
            self.char_end,
        )
        if self.source_anchor_id != expected_id:
            raise ValueError("source anchor identity does not match span")
        return self


class IngestionResult(StrictModel):
    """Operational outcome for one immutable source version."""

    source_version_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    status: Literal["ok", "insufficient", "blocked"]
    event_id: str | None
    publication_id: str | None
    reason: str
    provider_call_count: int = Field(ge=0)
    tmi_family: str | None
    preflight_eligible: bool | None


class TMIEventRecord(StrictModel):
    """One immutable publication view of a stable TMI event."""

    event_id: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    advisory_source_id: str = Field(min_length=1)
    publication_source_version_id: str = Field(min_length=1)
    event_type_iris: tuple[str, ...]
    facility_ids: tuple[str, ...]
    effective_start: datetime | None
    effective_end: datetime | None
    issued_at: datetime | None
    reason_status: Literal["formal", "profile_gap", "missing"]
    reason_value: str | None

    @field_validator("effective_start", "effective_end", "issued_at")
    @classmethod
    def _require_timezone(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if (
            value is not None
            and (value.tzinfo is None or value.utcoffset() is None)
        ):
            raise ValueError("TMI event timestamps must be timezone-aware")
        return value


class TMIEventQuery(StrictModel):
    """Exact bounded filters over active TMI event publications."""

    event_type_iri: str | None = Field(default=None, min_length=1)
    facility_id: str | None = Field(default=None, min_length=1)
    reason_status: Literal["formal", "profile_gap", "missing"] | None = None
    reason_value: str | None = Field(default=None, min_length=1)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class TMIEventPage(StrictModel):
    """One deterministic bounded page of active TMI events."""

    dataset_id: str = Field(min_length=1)
    total_matches: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    events: tuple[TMIEventRecord, ...] = ()


class SemanticFactRecord(StrictModel):
    """A provenance-independent formal fact."""

    fact_id: str = Field(min_length=1)
    subject_iri: str = Field(min_length=1)
    subject_class_iri: str = Field(min_length=1)
    predicate_iri: str = Field(min_length=1)
    object_kind: Literal["iri", "literal"]
    object_value: str
    object_class_iri: str | None
    datatype_iri: str | None
    validation_profile: ValidationProfileRef
    evidence_mode: Literal[
        "source_text",
        "deterministic_derivation",
        "profile_definition",
    ]


class EventEvidenceLink(StrictModel):
    """Event-scoped provenance for a formal or non-formal publication member."""

    evidence_link_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    owner_kind: Literal[
        "fact",
        "profile_gap",
        "weather_association",
        "public_observation",
    ]
    owner_id: str = Field(min_length=1)
    source_version_id: str = Field(min_length=1)
    source_anchor_id: str | None
    evidence_text: str | None
    evidence_ref: str = Field(min_length=1)


class EventWeatherAssociation(StrictModel):
    """Stable non-causal event-to-weather association."""

    association_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    report_id: str = Field(min_length=1)
    facility_id: str = Field(min_length=1)
    relation_type: Literal[
        "latest_forecast_known_at_issue",
        "latest_observation_at_or_before_issue",
        "observation_during_operation",
    ]
    selection_method: str = Field(min_length=1)
    relevant_times: dict[str, str] = Field(default_factory=dict)
    source_version_id: str = Field(min_length=1)
    causal_claim: Literal[False] = False


class PublicObservationRecord(StrictModel):
    """One profile-owned, source-qualified public observation."""

    observation_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    phase: Literal["baseline", "active", "recovery"]
    metric_key: str = Field(min_length=1)
    value: int | Decimal | None
    unit_iri: str | None
    fact_ids: tuple[str, ...]
    profile_id: str = Field(min_length=1)
    profile_checksum: str = Field(min_length=64, max_length=64)
    source_version_id: str = Field(min_length=1)


class EventProfileGapRecord(StrictModel):
    """One non-formal, publication-bound profile gap with exact evidence."""

    profile_gap_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    field: str = Field(min_length=1)
    value: str = Field(min_length=1)
    evidence_text: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    source_version_id: str = Field(min_length=1)
    source_anchor_id: str = Field(min_length=1)
    evidence_ref: str = Field(min_length=1)
    validation_profile: ValidationProfileRef


class SourceChunkRecord(StrictModel):
    """One bounded, versioned source representation for text retrieval."""

    chunk_id: str = Field(min_length=1)
    source_version_id: str = Field(min_length=1)
    event_id: str | None
    chunk_kind: Literal["source_record", "tmi_event_summary"]
    text: str = Field(min_length=1)
    char_start: int = Field(ge=0)
    char_end: int = Field(gt=0)
    source_anchor_id: str = Field(min_length=1)
    representation_version: str = Field(min_length=1)
    metadata: dict[str, object]

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> SourceChunkRecord:
        if self.char_end <= self.char_start:
            raise ValueError("source chunk end must be after start")
        expected_id = stable_id(
            "source-chunk",
            self.source_version_id,
            self.chunk_kind,
            self.char_start,
            self.char_end,
            self.representation_version,
        )
        if self.chunk_id != expected_id:
            raise ValueError("source chunk identity does not match span")
        return self
