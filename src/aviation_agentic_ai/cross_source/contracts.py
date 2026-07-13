from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SnapshotStatus(str, Enum):
    CANDIDATE = "candidate"
    ACTIVE = "active"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


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


class MentionType(str, Enum):
    FACILITY_CODE = "facility_code"
    OPERATIONAL_TERM = "operational_term"


class AlignmentStatus(str, Enum):
    ACCEPTED = "accepted"
    QUARANTINED = "quarantined"
    REJECTED = "rejected"


class AlignmentMethod(str, Enum):
    AUTHORITY_EXACT_CODE = "authority_exact_code"
    AUTHORITY_EXACT_ALIAS = "authority_exact_alias"
    CONTEXT_AGENT = "context_agent"
    NONE = "none"


class EvidenceLayer(str, Enum):
    SOURCE_ASSERTION = "source_assertion"
    OBSERVATION = "observation"
    FORECAST = "forecast"
    SYSTEM_ASSOCIATION = "system_association"


class CodeValue(StrictModel):
    scheme: str = Field(min_length=1)
    value: str = Field(min_length=1)


class SourceReference(StrictModel):
    source_ref: str = Field(min_length=1)
    source_url: str | None = None
    effective_start: datetime | None = None
    effective_end: datetime | None = None


class SnapshotArtifact(StrictModel):
    path: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    byte_count: int = Field(ge=0)


class SourceSnapshot(StrictModel):
    snapshot_id: str = Field(min_length=1)
    source_family: str = Field(min_length=1)
    source_url: str
    effective_start: datetime
    effective_end: datetime | None = None
    retrieved_at: datetime
    parser_name: str = Field(min_length=1)
    parser_version: str = Field(min_length=1)
    artifacts: list[SnapshotArtifact]
    record_count: int = Field(ge=0)
    status: SnapshotStatus = SnapshotStatus.CANDIDATE
    previous_snapshot_id: str | None = None
    validation_errors: list[str] = Field(default_factory=list)
    validation_warnings: list[str] = Field(default_factory=list)


class SnapshotSet(StrictModel):
    snapshot_set_id: str = Field(min_length=1)
    created_at: datetime
    snapshots: list[SourceSnapshot]
    status: SnapshotStatus = SnapshotStatus.CANDIDATE


class CanonicalEntity(StrictModel):
    entity_id: str = Field(min_length=1)
    entity_type: EntityType
    preferred_label: str = Field(min_length=1)
    codes: list[CodeValue]
    aliases: list[str] = Field(default_factory=list)
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    source_refs: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TermDefinition(StrictModel):
    text: str = Field(min_length=1)
    source_ref: str = Field(min_length=1)


class TermConcept(StrictModel):
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


class Mention(StrictModel):
    mention_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_family: str = Field(min_length=1)
    surface_form: str = Field(min_length=1)
    normalized_form: str = Field(min_length=1)
    mention_type: MentionType
    evidence_text: str = Field(min_length=1)
    span_start: int = Field(ge=0)
    span_end: int = Field(ge=0)
    record_time: datetime | None = None
    detected_by: str = Field(min_length=1)


class AlignmentCandidate(StrictModel):
    mention_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    target_label: str = Field(min_length=1)
    target_type: str = Field(min_length=1)
    method: AlignmentMethod
    authority_sources: list[str]
    gate_score: float = Field(ge=0.0, le=1.0)
    rationale: str = Field(min_length=1)


class AlignmentDecision(StrictModel):
    mention_id: str = Field(min_length=1)
    target_id: str | None = None
    status: AlignmentStatus
    method: AlignmentMethod
    gate_score: float = Field(ge=0.0, le=1.0)
    candidate_margin: float | None = Field(default=None, ge=0.0, le=1.0)
    authority_sources: list[str] = Field(default_factory=list)
    critic_checks: dict[str, bool] = Field(default_factory=dict)
    snapshot_set_id: str = Field(min_length=1)
    trace_id: str = Field(min_length=1)
    decision_reason: str = Field(min_length=1)


class TimeInterval(StrictModel):
    start: datetime
    end: datetime


class CrossSourceLink(StrictModel):
    link_id: str = Field(min_length=1)
    subject_id: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    object_id: str = Field(min_length=1)
    link_method: str = Field(min_length=1)
    facility_id: str = Field(min_length=1)
    advisory_interval: TimeInterval
    evidence_interval: TimeInterval
    authority_sources: list[str]
    evidence_text: str = Field(min_length=1)
    causal_claim: Literal[False] = False


class EvidenceStatement(StrictModel):
    layer: EvidenceLayer
    text: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    evidence_text: str = Field(min_length=1)
    facility_id: str | None = None
    interval: TimeInterval | None = None


class AnswerCitation(StrictModel):
    source_id: str = Field(min_length=1)
    evidence_text: str = Field(min_length=1)
    layer: EvidenceLayer


class AlignmentExplanation(StrictModel):
    mention_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    surface_form: str = Field(min_length=1)
    evidence_text: str = Field(min_length=1)
    candidates: list[AlignmentCandidate]
    decision_status: AlignmentStatus
    mapping_confidence: float = Field(ge=0.0, le=1.0)
    confidence_basis: str = Field(min_length=1)
    candidate_margin: float | None = Field(default=None, ge=0.0, le=1.0)
    decision_reason: str = Field(min_length=1)
    selected_target_id: str | None = None
    selected_target_label: str | None = None
    autonomous_action: Literal["accepted", "quarantined", "rejected"]
    write_to_formal_kg: bool


class CrossSourceAnswer(StrictModel):
    question: str = Field(min_length=1)
    source_assertions: list[EvidenceStatement] = Field(default_factory=list)
    observation_evidence: list[EvidenceStatement] = Field(default_factory=list)
    forecast_evidence: list[EvidenceStatement] = Field(default_factory=list)
    system_associations: list[EvidenceStatement] = Field(default_factory=list)
    alignment_explanations: list[AlignmentExplanation] = Field(default_factory=list)
    citations: list[AnswerCitation] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    abstain: bool
    rationale: str = Field(min_length=1)
    snapshot_set_id: str = Field(min_length=1)
    trace_id: str = Field(min_length=1)


class TraceEvent(StrictModel):
    trace_id: str = Field(min_length=1)
    node_id: str = Field(min_length=1)
    status: Literal["success", "quarantined", "rejected", "error"]
    input_summary: dict[str, Any] = Field(default_factory=dict)
    output_summary: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


class NodeResult(StrictModel):
    node_id: str = Field(min_length=1)
    status: Literal["success", "quarantined", "rejected", "error"]
    state_patch: dict[str, Any] = Field(default_factory=dict)
    trace_event: TraceEvent
    errors: list[str] = Field(default_factory=list)


class CrossSourceState(StrictModel):
    """Scheduler-neutral immutable state passed between workflow nodes."""

    run_id: str = Field(min_length=1)
    snapshot_set_id: str = Field(min_length=1)
    selected_advisory_ids: list[str] = Field(default_factory=list)
    question: str | None = None
    mentions: list[Mention] = Field(default_factory=list)
    alignment_candidates: list[AlignmentCandidate] = Field(default_factory=list)
    alignment_decisions: list[AlignmentDecision] = Field(default_factory=list)
    cross_source_links: list[CrossSourceLink] = Field(default_factory=list)
    retrieved_evidence: list[EvidenceStatement] = Field(default_factory=list)
    final_answer: CrossSourceAnswer | None = None
    trace_events: list[TraceEvent] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
