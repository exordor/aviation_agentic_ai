"""Shared Agent contracts for the multi-Agent KG system (design §6).

These are the small Pydantic shapes that cross Agent and deterministic
publication boundaries. Event Evidence Integration emits the only graph
publication proposal; the Query Agent returns a natural-language answer plus
source IDs.

Every accepted claim must carry ``source_id`` and ``evidence_text``. Missing
evidence produces ``abstain`` (or ``profile_gap`` / ``blocked``), never a model
completion from memory. The runtime never requests or stores hidden
chain-of-thought.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from aviation_agentic_ai.cross_source.identifiers import stable_id


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SourceFamily(str, Enum):
    """The source families the system ingests."""

    ATCSCC_ADVISORY = "atcscc_advisory"
    NASR_FACILITY = "nasr_facility"
    FAA_TERM = "faa_term"
    METAR = "metar"
    TAF = "taf"
    BTS_ON_TIME = "bts_on_time"


class AgentStatus(str, Enum):
    """The bounded lifecycle outcome every Agent decides (design §7)."""

    RESOLVED = "resolved"
    ABSTAIN = "abstain"
    PROFILE_GAP = "profile_gap"
    BLOCKED = "blocked"


# ---------------------------------------------------------------------------
# Source + evidence primitives
# ---------------------------------------------------------------------------


class SourceRecord(StrictModel):
    """One ingested source record handed to an Agent."""

    source_id: str = Field(min_length=1)
    family: SourceFamily
    content: str = Field(min_length=1)
    title: str | None = None
    effective_date: datetime | None = None
    source_url: str | None = None


class EvidenceClaim(StrictModel):
    """One authority-backed claim. Every accepted claim carries source + text."""

    field_name: str = Field(min_length=1)
    value: str = Field(min_length=1)
    ontology_target: str | None = None
    evidence_text: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    canonical_ref: str | None = None
    uncertainty: str | None = None


class ToolTraceEntry(StrictModel):
    """A safe tool-trace record: tool name, safe params, result refs, timing."""

    tool_call_id: str | None = None
    tool: str = Field(min_length=1)
    parameters: dict[str, str] = Field(default_factory=dict)
    result_refs: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    status: Literal["ok", "blocked"] = "ok"
    duration_ms: float = Field(default=0.0, ge=0.0)
    error: str | None = None


class EvidenceCard(StrictModel):
    """An Agent's evidence card (design §6.3). No hidden chain-of-thought."""

    agent_role: Literal[
        "advisory",
        "facility",
        "terminology",
    ]
    status: AgentStatus
    claims: list[EvidenceClaim] = Field(default_factory=list)
    canonical_refs: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    tool_trace: list[ToolTraceEntry] = Field(default_factory=list)
    decision_basis: str = ""


class ValidationProfileRef(StrictModel):
    """Immutable identity of the validation profile that owns one publication."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    profile_id: str = Field(min_length=1)
    profile_checksum: str = Field(min_length=64, max_length=64)
    layer: Literal[
        "decision",
        "decision_case_core",
        "weather",
        "public_operational_observation",
    ]


# ---------------------------------------------------------------------------
# Graph Patch output (design §11.5)
# ---------------------------------------------------------------------------


class GraphPatchLine(StrictModel):
    """One parsed Graph Patch line: ``subject | predicate | object | source_ids``."""

    subject: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    object: str = Field(min_length=1)
    source_ids: list[str] = Field(min_length=1)


class ProfileGap(StrictModel):
    """One parsed PROFILE_GAPS line: ``field | value | evidence | reason``.

    A source-supported field with no valid representation in the active profile.
    Recorded with evidence, never written to the formal KG.
    """

    field: str = Field(min_length=1)
    value: str = Field(min_length=1)
    evidence: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    source_id: str | None = None
    source_snapshot_sha256: str | None = None
    evidence_ref: str | None = None
    validation_profile: ValidationProfileRef | None = None


class GraphPatchBlock(StrictModel):
    """The parsed GRAPH_PATCH + PROFILE_GAPS sections of the KG Agent output."""

    patch_lines: list[GraphPatchLine] = Field(default_factory=list)
    profile_gaps: list[ProfileGap] = Field(default_factory=list)
    raw: str | None = None


# ---------------------------------------------------------------------------
# Task / result / model-call records
# ---------------------------------------------------------------------------


class AgentTask(StrictModel):
    """The task the Coordinator hands to an Agent (design §6.1)."""

    run_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    context_refs: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)
    schema_slice_id: str | None = None


class AgentResult(StrictModel):
    """An Agent's result (design §6.4).

    ``model_calls`` and ``graph_patch`` carry the audit records / parsed patch
    produced by model-driven Agents (None for deterministic-only Agents).
    """

    status: AgentStatus
    artifact_ref: str | None = None
    evidence_card: EvidenceCard | None = None
    failure_reason: str | None = None
    model_calls: list[ModelCallRecord] = Field(default_factory=list)
    graph_patch: GraphPatchBlock | None = None


class ModelToolCall(StrictModel):
    """Sanitized native tool-call metadata retained for replay."""

    call_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


class ModelCallRecord(StrictModel):
    """One model call's audit record (raw response + provider metadata).

    The call ledger is per-Agent and per-attempt (design §§16-17): ``agent`` is
    the role key that issued the call, ``prompt_set_id`` / ``prompt_version``
    identify the frozen prompt that was assembled, ``attempt`` is the 1-based
    index of this attempt within the run, and ``error`` records any provider
    failure so the trace shows every attempt (no silent retries).
    """

    agent: str = Field(min_length=1)
    raw_response: str
    prompt_set_id: str | None = None
    prompt_version: str | None = None
    provider: str | None = None
    model: str | None = None
    system_fingerprint: str | None = None
    finish_reason: str | None = None
    temperature: float | None = None
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    latency_ms: float = Field(default=0.0, ge=0.0)
    cache_hit: bool = False
    attempt: int = Field(default=1, ge=1)
    error: str | None = None
    tool_calls: list[ModelToolCall] = Field(default_factory=list)
    invalid_tool_calls: list[dict[str, Any]] = Field(default_factory=list)


class QueryToolTrace(StrictModel):
    """One validated Query Agent tool execution."""

    tool_call_id: str = Field(min_length=1)
    tool: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    result_refs: list[str] = Field(default_factory=list)
    context_association_ids: list[str] = Field(default_factory=list)
    outcome_summary_ids: list[str] = Field(default_factory=list)
    observation_ids: list[str] = Field(default_factory=list)
    derivation_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    status: Literal["ok", "insufficient", "blocked"]
    duration_ms: float = Field(default=0.0, ge=0.0)
    error: str | None = None


class CaseSimilarityMatch(StrictModel):
    """One ranked historical decision-record retrieval match."""

    rank: int = Field(ge=1)
    case_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    advisory_source_id: str = Field(min_length=1)
    score: float
    tmi_type_iri: str = Field(min_length=1)
    facility_ids: tuple[str, ...]
    reason_status: Literal["formal", "profile_gap", "missing"]
    reason_value: str | None


class QueryGraphEdge(StrictModel):
    """One formal fact carried by a bounded corpus graph path."""

    fact_id: str = Field(min_length=1)
    subject_iri: str = Field(min_length=1)
    predicate_iri: str = Field(min_length=1)
    object_kind: Literal["iri", "literal"]
    object_value: str = Field(min_length=1)
    datatype_iri: str | None = None
    source_ids: tuple[str, ...] = ()


class QueryGraphPath(StrictModel):
    """One case-scoped graph path retained as structured query evidence."""

    path_id: str = Field(min_length=1)
    path_kind: str = Field(min_length=1)
    edges: tuple[QueryGraphEdge, ...]
    source_ids: tuple[str, ...] = ()


class HybridQueryScope(StrictModel):
    """User-supplied bounds passed to every HybridRAG query tool."""

    event_id: str | None = Field(default=None, min_length=1)
    event_type_iri: str | None = Field(default=None, min_length=1)
    facility_id: str | None = Field(default=None, min_length=1)
    reason_status: Literal["formal", "profile_gap", "missing"] | None = None
    reason_value: str | None = Field(default=None, min_length=1)
    candidate_scope: Literal["archive", "prior"] = "archive"
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class HybridQueryEvidence(StrictModel):
    """Structured evidence retained outside model-visible answer prose."""

    case_ids: tuple[str, ...] = ()
    fact_ids: tuple[str, ...] = ()
    profile_gap_ids: tuple[str, ...] = ()
    context_association_ids: tuple[str, ...] = ()
    observation_ids: tuple[str, ...] = ()
    graph_path_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()


class HybridQuerySupportRecord(StrictModel):
    """One evidence-layer-specific binding exposed by a read-only query tool."""

    kind: Literal[
        "source_fact",
        "non_causal_context",
        "public_observation",
        "similarity",
    ]
    case_ids: tuple[str, ...] = ()
    fact_ids: tuple[str, ...] = ()
    profile_gap_ids: tuple[str, ...] = ()
    context_association_ids: tuple[str, ...] = ()
    observation_ids: tuple[str, ...] = ()
    graph_path_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()


class HybridQueryToolObservation(StrictModel):
    """One deterministic tool result with content/details separation."""

    status: Literal["ok", "insufficient", "blocked"]
    content: str = Field(min_length=1)
    details: HybridQueryEvidence = Field(default_factory=HybridQueryEvidence)
    support_records: tuple[HybridQuerySupportRecord, ...] = ()
    graph_paths: tuple[QueryGraphPath, ...] = ()
    similarity_matches: tuple[CaseSimilarityMatch, ...] = ()
    limitation: str = ""


class HybridQueryStatement(StrictModel):
    """One model-generated statement with evidence-layer-specific support."""

    kind: Literal[
        "source_fact",
        "non_causal_context",
        "public_observation",
        "similarity",
    ]
    text: str = Field(min_length=1)
    support_case_ids: tuple[str, ...] = ()
    support_fact_ids: tuple[str, ...] = ()
    support_profile_gap_ids: tuple[str, ...] = ()
    support_context_association_ids: tuple[str, ...] = ()
    support_observation_ids: tuple[str, ...] = ()
    support_graph_path_ids: tuple[str, ...] = ()
    support_source_ids: tuple[str, ...] = ()


class HybridQueryAnswer(StrictModel):
    """Compact model response validated against current-turn observations."""

    status: Literal["ok", "insufficient"]
    statements: tuple[HybridQueryStatement, ...] = ()
    limitations: tuple[str, ...] = ()


class QueryToolOutcome(StrictModel):
    """Final outcome of one bounded Query Agent tool loop."""

    status: Literal["ok", "insufficient", "blocked"]
    answer: str = ""
    match_count: int = Field(default=0, ge=0)
    retrieved_case_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    retrieved_fact_ids: list[str] = Field(default_factory=list)
    retrieved_profile_gap_ids: list[str] = Field(default_factory=list)
    retrieved_context_association_ids: list[str] = Field(default_factory=list)
    retrieved_outcome_summary_ids: list[str] = Field(default_factory=list)
    retrieved_observation_ids: list[str] = Field(default_factory=list)
    retrieved_derivation_ids: list[str] = Field(default_factory=list)
    retrieved_graph_path_ids: list[str] = Field(default_factory=list)
    retrieved_graph_paths: list[QueryGraphPath] = Field(default_factory=list)
    similarity_matches: list[CaseSimilarityMatch] = Field(
        default_factory=list
    )
    answer_statements: list[HybridQueryStatement] = Field(default_factory=list)
    support_records: list[HybridQuerySupportRecord] = Field(default_factory=list)
    model_calls: list[ModelCallRecord] = Field(default_factory=list)
    tool_calls: list[QueryToolTrace] = Field(default_factory=list)
    failure_reason: str = ""


class AgentRunResult(StrictModel):
    """The full result of one ``ingest`` run of the multi-Agent workflow."""

    run_id: str
    advisory_source_id: str
    evidence_cards: list[EvidenceCard] = Field(default_factory=list)
    graph_patch: GraphPatchBlock | None = None
    model_calls: list[ModelCallRecord] = Field(default_factory=list)
    materialized: bool = False


# ---------------------------------------------------------------------------
# Formal Graph Kernel contracts (design §13; plan §4.1, §5.4, §5.5)
# ---------------------------------------------------------------------------


class ValidatedFact(StrictModel):
    """One formal graph fact that passed the Formal Graph Kernel (plan §4.1).

    This is the single canonical internal representation shared by RDF, Neo4j,
    and Query. Graph Patch, RDF, Neo4j, and Query must not interpret the same
    strings independently.
    """

    fact_id: str = Field(min_length=1)
    subject_iri: str = Field(min_length=1)
    subject_class_iri: str = Field(min_length=1)
    predicate_iri: str = Field(min_length=1)
    object_kind: Literal["iri", "literal"]
    object_value: str = Field(min_length=1)
    object_class_iri: str | None = None
    datatype_iri: str | None = None
    source_ids: list[str] = Field(default_factory=list)
    evidence_texts: list[str] = Field(default_factory=list)
    validation_profile: ValidationProfileRef
    evidence_mode: Literal[
        "source_text",
        "deterministic_derivation",
        "profile_definition",
        "system_membership",
    ] = "source_text"
    evidence_ref: str = Field(min_length=1)


class RejectedFact(StrictModel):
    """A proposed Graph Patch row rejected by the Formal Graph Kernel.

    Carries the offending line text, the rule it failed, and a human-readable
    reason. Rejected rows never reach RDF/Neo4j.
    """

    graph_patch_line: str
    rule: str
    reason: str


class SourceSnapshot(StrictModel):
    """A versioned snapshot of one ingested source (plan §5.2).

    The Formal Graph Kernel binds every accepted fact to a source whose exact
    content and checksum are persisted, so provenance is auditable.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_id: str = Field(min_length=1)
    family: SourceFamily
    source_url: str | None = None
    content: str = Field(min_length=1)
    content_sha256: str = Field(min_length=1)
    snapshot_timestamp: str = Field(min_length=1)


class SourceSnapshotRegistry(StrictModel):
    """Immutable, source-ID-addressable snapshots for one ingest run."""

    snapshots: tuple[SourceSnapshot, ...] = Field(min_length=1)
    expected_families: dict[str, SourceFamily] = Field(default_factory=dict, exclude=True)

    @model_validator(mode="after")
    def _reject_duplicate_source_ids(self) -> "SourceSnapshotRegistry":
        source_ids = [snapshot.source_id for snapshot in self.snapshots]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("duplicate source snapshot ID")
        for snapshot in self.snapshots:
            if snapshot.content_sha256 != hashlib.sha256(
                snapshot.content.encode("utf-8")
            ).hexdigest():
                raise ValueError(
                    f"source snapshot checksum does not match content: {snapshot.source_id}"
                )
            expected_family = self.expected_families.get(snapshot.source_id)
            if expected_family is not None and snapshot.family != expected_family:
                raise ValueError(
                    f"source snapshot family mismatch: {snapshot.source_id}"
                )
        return self

    def get(self, source_id: str) -> SourceSnapshot | None:
        """Return the one snapshot bound to ``source_id``, if registered."""

        return next(
            (snapshot for snapshot in self.snapshots if snapshot.source_id == source_id),
            None,
        )

    def write_jsonl(self, output_dir: str | Path) -> Path:
        """Persist canonical multi-source snapshots for a new run."""

        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        path = output / "source_snapshots.jsonl"
        path.write_text(
            "\n".join(snapshot.model_dump_json() for snapshot in self.snapshots) + "\n",
            encoding="utf-8",
        )
        return path

    @classmethod
    def read_jsonl(cls, path: str | Path) -> "SourceSnapshotRegistry":
        """Load and validate the canonical multi-source snapshot artifact."""

        rows: list[SourceSnapshot] = []
        for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                rows.append(SourceSnapshot.model_validate_json(line))
            except Exception as exc:
                raise ValueError(f"invalid source snapshot JSON at line {line_number}") from exc
        return cls(snapshots=tuple(rows))


class DecisionContextEvent(StrictModel):
    """Resolved event clock used by deterministic decision-context adapters."""

    run_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    advisory_source_id: str = Field(min_length=1)
    advisory_issued_at: datetime
    operational_start: datetime
    operational_end: datetime

    @model_validator(mode="after")
    def _require_nonempty_operational_period(self) -> "DecisionContextEvent":
        clocks = (
            self.advisory_issued_at,
            self.operational_start,
            self.operational_end,
        )
        if any(clock.tzinfo is None or clock.utcoffset() is None for clock in clocks):
            raise ValueError("decision context clocks must be timezone-aware")
        if self.operational_end <= self.operational_start:
            raise ValueError("operational end must be after operational start")
        return self


class WeatherContextAssociation(StrictModel):
    """Non-causal audit association between an event and a weather report."""

    association_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    report_id: str = Field(min_length=1)
    facility_id: str = Field(min_length=1)
    relation_type: Literal[
        "latest_forecast_known_at_issue",
        "latest_observation_at_or_before_issue",
        "observation_during_operation",
    ]
    selection_method: str = Field(min_length=1)
    relevant_times: dict[str, str] = Field(default_factory=dict)
    source_id: str = Field(min_length=1)
    source_snapshot_sha256: str = Field(min_length=1)
    causal_claim: Literal[False] = False


class WeatherFactTrace(StrictModel):
    """Exact source binding for one deterministic weather fact."""

    fact_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_snapshot_sha256: str = Field(min_length=1)
    evidence_text: str = Field(min_length=1)


class WeatherContextBundle(StrictModel):
    """Selection result only; Task 4 owns graph/artifact materialization."""

    status: Literal["ok", "insufficient", "blocked"]
    selected_report_ids: list[str] = Field(default_factory=list)
    formal_facts: list[ValidatedFact] = Field(default_factory=list)
    fact_traces: list[WeatherFactTrace] = Field(default_factory=list)
    associations: list[WeatherContextAssociation] = Field(default_factory=list)
    failure_reason: str = ""


class BTSOnTimeRow(StrictModel):
    """One normalized, source-pinned BTS scheduled-arrival record."""

    row_id: str = Field(min_length=1)
    FlightDate: str = Field(min_length=1)
    DOT_ID_Reporting_Airline: int
    Reporting_Airline: str = Field(min_length=1)
    IATA_CODE_Reporting_Airline: str = Field(min_length=1)
    Flight_Number_Reporting_Airline: int
    OriginAirportSeqID: int
    DestAirportSeqID: int
    CRSDepTime: int = Field(ge=0)
    Origin: str = Field(min_length=1)
    Dest: str = Field(min_length=1)
    CRSArrTime: int = Field(ge=0)
    CRSElapsedTime: float = Field(ge=0)
    scheduled_arrival_utc: datetime
    Cancelled: Literal[0, 1]
    Diverted: Literal[0, 1]
    ArrDelay: float | None = None
    ArrDel15: Literal[0, 1] | None = None
    WeatherDelay: float | None = None
    NASDelay: float | None = None

    @model_validator(mode="after")
    def _require_timezone_aware_arrival(self) -> "BTSOnTimeRow":
        if (
            self.scheduled_arrival_utc.tzinfo is None
            or self.scheduled_arrival_utc.utcoffset() is None
        ):
            raise ValueError("scheduled_arrival_utc must be timezone-aware")
        return self


class BTSManifestBinding(StrictModel):
    """Immutable, loader-verified BTS archive and normalized-snapshot binding."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_id: str = Field(min_length=1)
    archive_sha256: str = Field(min_length=1)
    normalized_snapshot_sha256: str = Field(min_length=1)


class BTSPublicObservationSummary(StrictModel):
    """BTS-reported public operational observations for one TMI event phase."""

    summary_id: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    facility_id: str = Field(min_length=1)
    phase: Literal["baseline", "active", "recovery"]
    window_start: datetime
    window_end: datetime
    source_id: str = Field(min_length=1)
    source_snapshot_sha256: str = Field(min_length=1)
    scheduled_arrival_count: int = Field(ge=0)
    completed_arrival_count: int = Field(ge=0)
    cancelled_count: int = Field(ge=0)
    diverted_count: int = Field(ge=0)
    arrival_delay_15_count: int = Field(ge=0)
    mean_arrival_delay_minutes: float | None = None
    median_arrival_delay_minutes: float | None = None
    carrier_reported_weather_delay_minutes: float | None = None
    carrier_reported_nas_delay_minutes: float | None = None
    reporting_scope: Literal[
        "BTS On-Time reporting carriers and scheduled domestic passenger operations."
    ]
    causal_claim: Literal[False] = False


class ObservationDerivationSeed(StrictModel):
    """Checksum-bound row selection used to derive one BTS summary."""

    derivation_id: str = Field(min_length=1)
    summary_id: str = Field(min_length=1)
    summary_sha256: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_snapshot_sha256: str = Field(min_length=1)
    archive_sha256: str = Field(min_length=1)
    aggregation_procedure_id: str = Field(min_length=1)
    aggregation_procedure_checksum: str = Field(min_length=1)
    selected_row_ids: tuple[str, ...]
    selected_row_ids_sha256: str = Field(min_length=1)


class BTSPublicObservationBundle(StrictModel):
    """Deterministic, source-bound BTS public-observation adapter result."""

    status: Literal["ok", "insufficient", "blocked"]
    summaries: list[BTSPublicObservationSummary] = Field(default_factory=list)
    derivation_seeds: list[ObservationDerivationSeed] = Field(default_factory=list)
    failure_reason: str = ""


class SourceBinding(StrictModel):
    """Checksum-bound source identity included in one reconstruction."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_id: str = Field(min_length=1)
    source_family: SourceFamily
    snapshot_sha256: str = Field(min_length=64, max_length=64)


class ObservationDerivation(StrictModel):
    """Audit bridge from one BTS phase summary to its aggregation activity."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    derivation_id: str = Field(min_length=1)
    activity_iri: str = Field(min_length=1)
    summary_id: str = Field(min_length=1)
    summary_sha256: str = Field(min_length=64, max_length=64)
    source_id: str = Field(min_length=1)
    source_snapshot_sha256: str = Field(min_length=64, max_length=64)
    archive_sha256: str = Field(min_length=64, max_length=64)
    aggregation_procedure_id: str = Field(min_length=1)
    aggregation_procedure_checksum: str = Field(min_length=1)
    selected_row_ids: tuple[str, ...]
    selected_row_ids_sha256: str = Field(min_length=64, max_length=64)


class ObservationFactTrace(StrictModel):
    """Typed provenance for one deterministically derived observation value."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    fact_id: str = Field(min_length=1)
    observation_id: str = Field(min_length=1)
    derivation_id: str = Field(min_length=1)
    summary_id: str = Field(min_length=1)
    metric_key: str = Field(min_length=1)
    canonical_value: int | Decimal | None
    source_id: str = Field(min_length=1)
    source_snapshot_sha256: str = Field(min_length=64, max_length=64)
    summary_sha256: str = Field(min_length=64, max_length=64)
    aggregation_procedure_id: str = Field(min_length=1)
    aggregation_procedure_checksum: str = Field(min_length=1)


class PublicObservationRead(StrictModel):
    """One profile-owned public observation reconstructed from formal facts."""

    observation_id: str = Field(min_length=1)
    fact_ids: tuple[str, ...]
    phase: Literal["baseline", "active", "recovery"]
    metric_key: str = Field(min_length=1)
    label: str = Field(min_length=1)
    value: int | Decimal
    datatype_iri: str = Field(min_length=1)
    unit_iri: str = Field(min_length=1)
    derivation_id: str = Field(min_length=1)
    evidence_ref: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_snapshot_sha256: str = Field(min_length=64, max_length=64)
    profile_id: str = Field(min_length=1)
    profile_checksum: str = Field(min_length=64, max_length=64)


class PublicObservationSetRead(StrictModel):
    """Validated formal public observations exposed to the bounded query tool."""

    status: Literal["ok", "insufficient", "blocked"]
    event_id: str = Field(min_length=1)
    observations: tuple[PublicObservationRead, ...] = ()
    source_ids: tuple[str, ...] = ()
    failure_reason: str | None = None


class DecisionCaseReconstructionSeed(StrictModel):
    """Stable source and profile binding prepared before case membership."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    conceptual_case_iri: str = Field(min_length=1)
    reconstruction_iri: str = Field(min_length=1)
    reconstruction_trace_id: str = Field(min_length=1)
    reconstruction_input_sha256: str = Field(min_length=64, max_length=64)
    profile_refs: tuple[ValidationProfileRef, ...]
    source_bindings: tuple[SourceBinding, ...]
    builder_id: str = Field(min_length=1)
    builder_checksum: str = Field(min_length=64, max_length=64)
    aggregation_procedure_id: str | None = None
    aggregation_procedure_checksum: str | None = None


class ReconstructionTrace(DecisionCaseReconstructionSeed):
    """Exact immutable input and member binding for one reconstruction."""

    member_iris: tuple[str, ...]


class DecisionCaseMemberBinding(StrictModel):
    """One accepted formal member and the sources that establish it."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    member_iri: str = Field(min_length=1)
    member_kind: Literal["event", "weather_report", "public_observation"]
    source_ids: tuple[str, ...]


class DecisionCaseGraphBundle(StrictModel):
    """Formal source-independent DecisionCase core graph."""

    status: Literal["ok", "blocked"]
    case_iri: str | None = None
    reconstruction_iri: str | None = None
    formal_facts: list[ValidatedFact] = Field(default_factory=list)
    reconstruction_trace: ReconstructionTrace | None = None
    failure_reason: str = ""


class BTSObservationBundle(StrictModel):
    """Validated formal public-observation layer and its audit artifacts."""

    status: Literal["ok", "insufficient", "blocked"]
    formal_facts: list[ValidatedFact] = Field(default_factory=list)
    observation_ids: tuple[str, ...] = ()
    fact_traces: list[ObservationFactTrace] = Field(default_factory=list)
    derivations: list[ObservationDerivation] = Field(default_factory=list)
    failure_reason: str | None = None


class FactTraceRow(StrictModel):
    """One row of ``fact_trace.jsonl`` (plan §5.5).

    Normalized graph values may differ from their source spelling, but the
    original evidence text and source SHA-256 are preserved exactly.
    """

    fact_id: str = Field(min_length=1)
    graph_patch_line: str
    source_id: str = Field(min_length=1)
    evidence_text: str
    evidence_agent_role: str = Field(min_length=1)
    source_snapshot_sha256: str = Field(min_length=1)


class PersistedProfileGap(StrictModel):
    """One validated source-bound row in ``profile_gaps.jsonl``."""

    profile_gap_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    field: str = Field(min_length=1)
    value: str = Field(min_length=1)
    evidence_text: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_snapshot_sha256: str = Field(min_length=1)
    evidence_ref: str = Field(min_length=1)
    validation_profile: ValidationProfileRef

    @model_validator(mode="after")
    def validate_publication_binding(self) -> "PersistedProfileGap":
        expected_evidence_ref = stable_id(
            "profile-gap-evidence",
            self.source_id,
            self.source_snapshot_sha256,
            self.field,
            self.value,
            self.evidence_text,
        )
        if self.evidence_ref != expected_evidence_ref:
            raise ValueError("profile gap evidence_ref is not stable")
        expected_gap_id = stable_id(
            "profile-gap",
            self.event_id,
            self.field,
            self.value,
            self.reason,
            self.evidence_ref,
            self.validation_profile.profile_id,
            self.validation_profile.profile_checksum,
            self.validation_profile.layer,
        )
        if self.profile_gap_id != expected_gap_id:
            raise ValueError("profile gap ID is not stable")
        return self


class GraphValidationResult(StrictModel):
    """The full outcome of running the Formal Graph Kernel on one patch (§5.4).

    ``publishable`` is the single boolean gate: only when True may any accepted
    fact be written to RDF/Neo4j. A single non-publishable result must not
    produce formal graph artifacts.

    ``profile_gaps`` carries source-supported fields the active profile cannot
    represent (plan §12). A profile gap is NOT a formal fact and NOT a rejected
    row — it is recorded with its verbatim source evidence and a short
    schema-mapping reason, and it must not enter the formal graph.
    """

    accepted: list[ValidatedFact] = Field(default_factory=list)
    rejected: list[RejectedFact] = Field(default_factory=list)
    profile_gaps: list[ProfileGap] = Field(default_factory=list)
    graph_errors: list[str] = Field(default_factory=list)
    publishable: bool = False
