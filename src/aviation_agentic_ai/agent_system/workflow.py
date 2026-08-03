"""LangGraph ingest topology for source-bound aviation evidence.

The Workflow Coordinator is a deterministic LangGraph controller:

    START
      -> deterministic advisory evidence builder
      -> parallel fan-out:
           facility authority service
           terminology authority service
      -> evidence-card join
      -> deterministic event-evidence integration
      -> event-patch validation + final publication
      -> END

The Coordinator creates tasks, fans out, joins, and records state transitions.
It does NOT call an LLM and is not an Agent role.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
import hashlib
import json
import operator
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from pydantic import model_validator

from aviation_agentic_ai.agent_system.agents import build_advisory_evidence, parse_structured_fields
from aviation_agentic_ai.agent_system.authority_resolution import (
    AuthorityResolutionResult,
    FacilityAuthorityResolutionInput,
    TerminologyAuthorityResolutionInput,
    resolve_facility_authority,
    resolve_terminology_authority,
)
from aviation_agentic_ai.agent_system.authority_evidence import (
    AuthorityBuildStatus,
    LoadedAuthorityCatalog,
    build_facility_resolution_candidate,
    build_term_resolution_candidate,
)
from aviation_agentic_ai.agent_system.contracts import (
    BTSManifestBinding,
    AgentTask,
    BTSOnTimeRow,
    GraphValidationResult,
    GraphPatchBlock,
    GraphPatchLine,
    ProfileGap,
    SourceFamily,
    SourceRecord,
)
from aviation_agentic_ai.agent_system.construction_contracts import (
    EventEvidenceIntegrationStatus,
    EventEvidenceIntegrationEvidenceRecord,
    EventEvidenceIntegrationPublicObservation,
    EventEvidenceIntegrationResolutionRecord,
    EventEvidenceIntegrationProposal,
    EventEvidenceIntegrationTask,
    EventEvidenceFactProposal,
    EventEvidenceProfileGapProposal,
    EvidenceLayerResult,
    EvidenceLayerStatus,
    ContractExecutionBinding,
    FrozenContractModel,
    ResolutionDecision,
    SourceSnapshotBinding,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.event_evidence_integration import (
    EventEvidenceIntegrationResult,
)
from aviation_agentic_ai.agent_system.event_evidence_integration_tools import (
    build_event_evidence_integration_task,
    compile_event_evidence_integration_proposal,
    preflight_validate_event_evidence_proposal,
)
from aviation_agentic_ai.agent_system.context_artifacts import (
    integrate_event_context,
    prepare_event_context,
)
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)
from aviation_agentic_ai.agent_system.formal_graph import (
    build_fact_trace_rows,
    build_profile_gap_rows,
    validate_graph_patch,
)
from aviation_agentic_ai.agent_system.schema_guide import SchemaGuide, load_schema_guide
from aviation_agentic_ai.agent_system.sources import (
    build_source_snapshot_registry,
)
from aviation_agentic_ai.agent_system.tmi_profiles import (
    active_tmi_profiles,
    get_tmi_profile,
)
from aviation_agentic_ai.utils.identifiers import stable_id

ToolModelFactory = Any


class AuthoritySourceRegistryStatus(str, Enum):
    """Outcome of the parallel authority-audit source channel."""

    OK = "ok"
    BLOCKED = "blocked"


class AuthoritySourceRecordRegistry(FrozenContractModel):
    """Task-referenced authority rows carried outside the formal KG."""

    status: AuthoritySourceRegistryStatus = AuthoritySourceRegistryStatus.OK
    records: tuple[SourceRecord, ...] = ()
    reason_code: str | None = None
    error_id: str | None = None

    @model_validator(mode="after")
    def validate_status_shape(self) -> "AuthoritySourceRecordRegistry":
        if self.status is AuthoritySourceRegistryStatus.BLOCKED:
            if self.records or not self.reason_code or not self.error_id:
                raise ValueError("blocked authority registry requires an error and no records")
        elif self.reason_code is not None or self.error_id is not None:
            raise ValueError("ok authority registry cannot carry an error")
        return self


_AUTHORITY_SOURCE_FAMILIES = {
    SourceFamily.NASR_FACILITY,
    SourceFamily.FAA_TERM,
}


def _blocked_authority_registry(
    reason_code: str,
    source_id: str,
) -> AuthoritySourceRecordRegistry:
    return AuthoritySourceRecordRegistry(
        status=AuthoritySourceRegistryStatus.BLOCKED,
        reason_code=reason_code,
        error_id=stable_contract_id(
            "authority-source-registry-error",
            reason_code,
            source_id,
        ),
    )


def _canonical_source_record(record: SourceRecord) -> str:
    return json.dumps(
        record.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def merge_authority_source_records(
    left: AuthoritySourceRecordRegistry,
    right: AuthoritySourceRecordRegistry,
) -> AuthoritySourceRecordRegistry:
    """Merge parallel authority audit rows, failing closed without partial data."""

    blocked = sorted(
        (
            registry
            for registry in (left, right)
            if registry.status is AuthoritySourceRegistryStatus.BLOCKED
        ),
        key=lambda registry: (registry.reason_code or "", registry.error_id or ""),
    )
    if blocked:
        return blocked[0]

    records_by_id: dict[str, SourceRecord] = {}
    canonical_by_id: dict[str, tuple[str, str]] = {}
    for record in (*left.records, *right.records):
        if record.family not in _AUTHORITY_SOURCE_FAMILIES:
            return _blocked_authority_registry(
                "AUTHORITY_SOURCE_FAMILY_NOT_ALLOWED",
                record.source_id,
            )
        canonical = _canonical_source_record(record)
        content_sha256 = hashlib.sha256(record.content.encode("utf-8")).hexdigest()
        existing = canonical_by_id.get(record.source_id)
        if existing is not None and existing != (canonical, content_sha256):
            return _blocked_authority_registry(
                "AUTHORITY_SOURCE_ID_CONFLICT",
                record.source_id,
            )
        canonical_by_id[record.source_id] = (canonical, content_sha256)
        records_by_id[record.source_id] = record.model_copy(deep=True)
    return AuthoritySourceRecordRegistry(
        records=tuple(records_by_id[source_id] for source_id in sorted(records_by_id)),
    )


def _authority_source_registry(
    records: tuple[SourceRecord, ...],
) -> AuthoritySourceRecordRegistry:
    return merge_authority_source_records(
        AuthoritySourceRecordRegistry(),
        AuthoritySourceRecordRegistry(records=records),
    )


@dataclass
class IngestContext:
    """The frozen inputs the Coordinator hands to the ingest graph."""

    advisory: SourceRecord
    facility_candidates: list[Any] = field(default_factory=list)
    term_candidates: list[Any] = field(default_factory=list)
    weather_sources: list[SourceRecord] = field(default_factory=list)
    bts_rows: list[BTSOnTimeRow] = field(default_factory=list)
    bts_source: SourceRecord | None = None
    bts_manifest_binding: BTSManifestBinding | None = None
    weather_failure_reason: str = ""
    bts_failure_reason: str = ""
    guide: SchemaGuide | None = None
    semantic_resolution_tool_model_factory: ToolModelFactory | None = None
    authority_catalog: LoadedAuthorityCatalog | None = None
    run_started_at: datetime | None = None
    run_id: str = "agent-system"


def _event_uri(run_id: str, source_id: str, event_class: str) -> str:
    return stable_id("evt", source_id, event_class)


# Typed state schema for the ingest graph. Additive reducers (operator.add)
# let the parallel authority-service branches contribute to ``model_calls``
# without a concurrent-write conflict; each branch also writes its own distinct
# result key.
class IngestState(TypedDict):
    mentions: Any
    advisory_evidence: Any
    facility_authority_result: AuthorityResolutionResult
    terminology_authority_result: AuthorityResolutionResult
    authority_source_records: Annotated[
        AuthoritySourceRecordRegistry,
        merge_authority_source_records,
    ]
    resolution_event_id: str
    resolution_event_mention: str
    event_class_hint: str
    formal_event_uri_hint: str
    resolution_preflight_status: str
    resolution_preflight_reason: str
    joined: bool
    event_evidence_integration_task: Any
    event_evidence_integration_proposal: Any
    event_evidence_integration_feedback: Any
    event_evidence_integration_result: Any
    integration_graph_patch: GraphPatchBlock | None
    integration_failure_reason: str | None
    event_uri: str
    event_class: str
    validation: Any
    direct_fact_traces: Any
    profile_gap_rows: Any
    formal_publication: Any
    ingestion_package: Any
    source_snapshot: Any
    source_versions: Any
    event_context_event: Any
    event_context_prepared: bool
    prepared_source_snapshot: Any
    weather_context: Any
    public_observation_context: Any
    observation_context: Any
    formal_layers: Any
    public_observation_publication: Any
    publication_status: str
    publication_failure_reason: str
    model_calls: Annotated[list, operator.add]


def build_ingest_graph() -> Any:
    """Compile the fixed ingest topology as a LangGraph StateGraph."""

    sg = StateGraph(IngestState, context_schema=IngestContext)
    sg.add_node("advisory", _advisory_node)
    sg.add_node("facility_authority", _facility_authority_node)
    sg.add_node("terminology_authority", _terminology_authority_node)
    sg.add_node("join", _join_node)
    sg.add_node("prepare_context", _prepare_context_node)
    sg.add_node("integrate_event_evidence", _integrate_event_evidence_node)
    sg.add_node("validate_event_patch", _validate_event_patch_node)
    sg.add_node("publish_event", _publish_event_node)
    sg.add_edge(START, "advisory")
    # Parallel fan-out after deterministic advisory evidence construction.
    sg.add_edge("advisory", "facility_authority")
    sg.add_edge("advisory", "terminology_authority")
    # Join after the two deterministic authority services.
    sg.add_edge("facility_authority", "join")
    sg.add_edge("terminology_authority", "join")
    sg.add_edge("join", "prepare_context")
    sg.add_edge("prepare_context", "integrate_event_evidence")
    sg.add_edge("integrate_event_evidence", "validate_event_patch")
    sg.add_edge("validate_event_patch", "publish_event")
    sg.add_edge("publish_event", END)
    return sg.compile()


# ---------------------------------------------------------------------------
# Node functions (receive/return the shared state dict)
# ---------------------------------------------------------------------------

def _ctx(runtime: Runtime[IngestContext]) -> IngestContext:
    """Return immutable run-scoped dependencies injected by LangGraph."""

    if runtime.context is None:
        raise RuntimeError("ingest context not provided; call run_ingest()")
    return runtime.context


def _advisory_node(state: dict, runtime: Runtime[IngestContext]) -> dict:
    ctx: IngestContext = _ctx(runtime)
    guide = ctx.guide or load_schema_guide()
    task = AgentTask(
        run_id=ctx.run_id,
        source_id=ctx.advisory.source_id,
        objective="extract advisory mentions",
        allowed_tools=["get_advisory", "parse_structured_fields", "get_schema_event_classes"],
        schema_slice_id=guide.schema_slice_id,
    )
    mentions = parse_structured_fields(ctx.advisory.content)
    event_classes = [
        event_class
        for profile in active_tmi_profiles()
        if (event_class := profile.prefixed_ontology_class) is not None
    ]
    evidence = build_advisory_evidence(
        task=task,
        advisory=ctx.advisory,
        event_classes=event_classes,
        mentions=mentions,
    )
    event_mention = (
        mentions.operational_term.strip().upper()
        if mentions.operational_term
        else "MISSING_EVENT_MENTION"
    )
    resolution_event_id = stable_contract_id(
        "resolution-event",
        ctx.run_id,
        ctx.advisory.source_id,
        event_mention,
    )
    event_class_hint = (
        guide.event_class_for_term(event_mention)
        if event_mention != "MISSING_EVENT_MENTION"
        else None
    )
    formal_event_uri_hint = (
        _event_uri(ctx.run_id, ctx.advisory.source_id, event_class_hint) if event_class_hint else ""
    )
    return {
        "advisory_evidence": evidence,
        "mentions": mentions,
        "resolution_event_id": resolution_event_id,
        "resolution_event_mention": event_mention,
        "event_class_hint": event_class_hint or "",
        "formal_event_uri_hint": formal_event_uri_hint,
        "model_calls": [],
    }


def _facility_candidates_for_mention(
    all_candidates: list,
    mention: str,
    expected_entity_type: str | None = None,
) -> list:
    """Filter authority facility candidates to those matching the mention token.

    A candidate matches if the mention equals one of its codes or aliases
    (normalized, uppercase). This turns the facility registry into the
    authority lookup the facility resolution service uses (design §9.4). Expected type is
    carried to candidate-level audit and never removes a mention match here.
    """

    del expected_entity_type
    if not mention:
        return []
    token = mention.upper()
    matches = []
    for entity in all_candidates:
        codes = {c.value.upper() for c in getattr(entity, "codes", [])}
        aliases = {a.upper() for a in getattr(entity, "aliases", [])}
        if token in codes or token in aliases:
            matches.append(entity)
    return sorted(matches, key=lambda entity: entity.entity_id)


def _candidate_domain_status(
    results: tuple[Any, ...],
    *,
    missing_reason: str,
) -> tuple[AuthorityBuildStatus, str, str]:
    blocked = next(
        (row for row in results if row.status is AuthorityBuildStatus.BLOCKED),
        None,
    )
    if blocked is not None:
        return (
            AuthorityBuildStatus.BLOCKED,
            blocked.reason_code or "AUTHORITY_CANDIDATE_BLOCKED",
            blocked.error_id or "",
        )
    insufficient = next(
        (row for row in results if row.status is AuthorityBuildStatus.INSUFFICIENT),
        None,
    )
    if insufficient is not None:
        return (
            AuthorityBuildStatus.INSUFFICIENT,
            insufficient.reason_code or "AUTHORITY_EVIDENCE_INSUFFICIENT",
            "",
        )
    if not results:
        return AuthorityBuildStatus.INSUFFICIENT, missing_reason, ""
    return AuthorityBuildStatus.OK, "", ""


def _facility_authority_node(state: dict, runtime: Runtime[IngestContext]) -> dict:
    ctx: IngestContext = _ctx(runtime)
    mentions = state.get("mentions")
    mention_token = getattr(mentions, "controlled_facility", None) or "MISSING_FACILITY_MENTION"
    # §11.4: pass the exact advisory evidence span (e.g. ``CTL ELEMENT: JFK``)
    # to the facility resolution service so its claim carries source-contained evidence, not
    # a synthetic string.
    spans = getattr(mentions, "evidence_spans", {}) or {}
    advisory_evidence = spans.get("controlled_facility", "")
    task = AgentTask(
        run_id=ctx.run_id,
        source_id=ctx.advisory.source_id,
        objective="resolve facility mention",
        allowed_tools=["lookup_nasr_facility", "lookup_artcc", "resolve_facility_alias"],
    )
    guide = ctx.guide or load_schema_guide()
    authority_catalog = ctx.authority_catalog
    if authority_catalog is None:
        matched = []
        built = ()
        domain_status = AuthorityBuildStatus.BLOCKED
        domain_reason = "AUTHORITY_CATALOG_NOT_LOADED"
        domain_error = stable_contract_id(
            "resolution-error",
            ctx.run_id,
            "facility",
            domain_reason,
        )
    elif authority_catalog.facility.status is AuthorityBuildStatus.BLOCKED:
        matched = []
        built = ()
        domain_status = AuthorityBuildStatus.BLOCKED
        domain_reason = authority_catalog.facility.reason_code or "FACILITY_AUTHORITY_BLOCKED"
        domain_error = authority_catalog.facility.error_id or ""
    else:
        matched = _facility_candidates_for_mention(
            list(authority_catalog.facility.entities),
            mention_token,
            getattr(mentions, "facility_expected_entity_type", None),
        )
        built = tuple(
            build_facility_resolution_candidate(
                entity,
                structural_slot=(
                    getattr(mentions, "facility_structural_slot", None) or "controlled_nas_element"
                ),
                expected_entity_type=(
                    getattr(mentions, "facility_expected_entity_type", None)
                    or "unknown_facility_type"
                ),
                catalog=authority_catalog.facility,
                authority_snapshots=authority_catalog.snapshots,
                guide=guide,
            )
            for entity in matched
        )
        domain_status, domain_reason, domain_error = _candidate_domain_status(
            built,
            missing_reason="FACILITY_MENTION_OR_CANDIDATES_MISSING",
        )
    cands = FacilityAuthorityResolutionInput(
        mention=mention_token,
        candidates=matched,
        source_id=ctx.advisory.source_id,
        structural_slot=(
            getattr(mentions, "facility_structural_slot", None) or "controlled_nas_element"
        ),
        expected_entity_type=(
            getattr(mentions, "facility_expected_entity_type", None) or "unknown_facility_type"
        ),
        advisory_evidence=advisory_evidence,
        resolution_event_id=state.get("resolution_event_id", ""),
        resolution_event_mention=state.get(
            "resolution_event_mention",
            "MISSING_EVENT_MENTION",
        ),
        run_started_at=ctx.run_started_at,
        schema_slice_id=guide.schema_slice_id,
        schema_snapshot_sha256=guide.checksum,
        resolution_tool_version="authority-resolution-v1",
        authority_domain_status=domain_status,
        authority_domain_reason_code=domain_reason,
        authority_domain_error_id=domain_error,
        authority_candidate_results=built,
    )
    resolution_kwargs = {"task": task, "request": cands}
    if ctx.semantic_resolution_tool_model_factory is not None:
        resolution_kwargs["semantic_resolution_tool_model_factory"] = (
            ctx.semantic_resolution_tool_model_factory
        )
    authority_result = resolve_facility_authority(**resolution_kwargs)
    # model_calls uses an additive reducer so parallel branches can each contribute.
    return {
        "facility_authority_result": authority_result,
        "authority_source_records": _authority_source_registry(
            authority_result.authority_source_records
        ),
        "model_calls": list(authority_result.model_calls),
    }


def _term_candidates_for_mention(all_terms: list, mention: str) -> list:
    """Filter authority term candidates to those whose abbreviation matches.

    A term matches if its abbreviation equals the mention token (normalized,
    uppercase). This is the authority lookup the terminology resolution service uses
    (design §10.4); e.g. a ``GS`` mention yields both the Ground Stop TMI and
    the Glide Slope procedure, which the Agent then disambiguates by category.
    """

    if not mention:
        return []
    token = mention.upper()
    return sorted(
        (term for term in all_terms if getattr(term, "abbreviation", "").upper() == token),
        key=lambda term: term.term_id,
    )


def _terminology_authority_node(state: dict, runtime: Runtime[IngestContext]) -> dict:
    ctx: IngestContext = _ctx(runtime)
    mentions = state.get("mentions")
    mention_token = getattr(mentions, "operational_term", None) or "MISSING_EVENT_MENTION"
    # §11.4: pass the exact advisory evidence span (the Ground Stop mention in
    # context) to the terminology resolution service so the resolved term claim carries
    # source-contained evidence the Formal Graph Kernel can bind rdf:type to.
    spans = getattr(mentions, "evidence_spans", {}) or {}
    advisory_evidence = spans.get("operational_term", "") or spans.get("event_type", "")
    task = AgentTask(
        run_id=ctx.run_id,
        source_id=ctx.advisory.source_id,
        objective="resolve operational term",
        allowed_tools=[
            "lookup_faa_glossary",
            "lookup_pcg_term",
            "resolve_term_registry",
            "resolve_schema_event_class",
        ],
    )
    guide = ctx.guide or load_schema_guide()
    authority_catalog = ctx.authority_catalog
    if authority_catalog is None:
        matched = []
        built = ()
        domain_status = AuthorityBuildStatus.BLOCKED
        domain_reason = "AUTHORITY_CATALOG_NOT_LOADED"
        domain_error = stable_contract_id(
            "resolution-error",
            ctx.run_id,
            "terminology",
            domain_reason,
        )
    elif authority_catalog.terminology.status is AuthorityBuildStatus.BLOCKED:
        matched = []
        built = ()
        domain_status = AuthorityBuildStatus.BLOCKED
        domain_reason = authority_catalog.terminology.reason_code or "TERMINOLOGY_AUTHORITY_BLOCKED"
        domain_error = authority_catalog.terminology.error_id or ""
    else:
        matched = _term_candidates_for_mention(
            list(authority_catalog.terminology.registry_terms),
            mention_token,
        )
        built = tuple(
            build_term_resolution_candidate(
                term,
                structural_slot=(
                    getattr(mentions, "term_structural_slot", None)
                    or "traffic_management_initiative_type"
                ),
                expected_entity_type=(
                    getattr(mentions, "term_expected_entity_type", None)
                    or "traffic_management_initiative"
                ),
                catalog=authority_catalog.terminology,
                authority_snapshots=authority_catalog.snapshots,
                guide=guide,
            )
            for term in matched
        )
        domain_status, domain_reason, domain_error = _candidate_domain_status(
            built,
            missing_reason="EVENT_MENTION_OR_CANDIDATES_MISSING",
        )
    cands = TerminologyAuthorityResolutionInput(
        mention=mention_token,
        candidates=matched,
        source_id=ctx.advisory.source_id,
        structural_slot=(
            getattr(mentions, "term_structural_slot", None) or "traffic_management_initiative_type"
        ),
        expected_entity_type=(
            getattr(mentions, "term_expected_entity_type", None) or "traffic_management_initiative"
        ),
        advisory_evidence=advisory_evidence,
        resolution_event_id=state.get("resolution_event_id", ""),
        resolution_event_mention=state.get(
            "resolution_event_mention",
            "MISSING_EVENT_MENTION",
        ),
        run_started_at=ctx.run_started_at,
        schema_slice_id=guide.schema_slice_id,
        schema_snapshot_sha256=guide.checksum,
        resolution_tool_version="authority-resolution-v1",
        authority_domain_status=domain_status,
        authority_domain_reason_code=domain_reason,
        authority_domain_error_id=domain_error,
        authority_candidate_results=built,
    )
    resolution_kwargs = {"task": task, "request": cands}
    if ctx.semantic_resolution_tool_model_factory is not None:
        resolution_kwargs["semantic_resolution_tool_model_factory"] = (
            ctx.semantic_resolution_tool_model_factory
        )
    authority_result = resolve_terminology_authority(**resolution_kwargs)
    return {
        "terminology_authority_result": authority_result,
        "authority_source_records": _authority_source_registry(
            authority_result.authority_source_records
        ),
        "model_calls": list(authority_result.model_calls),
    }


def _join_node(state: dict) -> dict:
    """Join independently audited domains and compute the required preflight."""

    mentions = state.get("mentions")
    profile = get_tmi_profile(
        getattr(mentions, "event_type", ""),
        publishable_only=True,
    )
    facility_required = bool(
        profile is not None and "controlled_facility" in profile.required_fields
    )
    required_outcomes = (
        (state.get("facility_authority_result"),)
        if facility_required
        else ()
    )
    authority_registry = state.get("authority_source_records")
    if (
        authority_registry is not None
        and authority_registry.status is AuthoritySourceRegistryStatus.BLOCKED
    ):
        status = "blocked"
        reason = authority_registry.reason_code or "authority source registry blocked"
    elif any(
        outcome is None or outcome.domain_outcome.decision is ResolutionDecision.BLOCKED
        for outcome in required_outcomes
    ):
        status = "blocked"
        reason = "required resolution domain blocked"
    elif any(
        outcome.domain_outcome.decision is not ResolutionDecision.ACCEPTED
        for outcome in required_outcomes
    ):
        status = "insufficient"
        reason = "required resolution domain insufficient"
    else:
        status = "resolved"
        reason = ""
    return {
        "joined": True,
        "resolution_preflight_status": status,
        "resolution_preflight_reason": reason,
    }


def _prepare_context_node(state: dict, runtime: Runtime[IngestContext]) -> dict:
    """Prepare validated optional context in memory before Event Evidence Integration."""

    return prepare_event_context(_ctx(runtime), state)


def _accepted_event_source_ids(
    advisory_source_id: str,
    *evidence_sources: Any,
) -> set[str]:
    """Return source IDs from retained event claims, bound to this advisory."""

    return {
        claim.source_id
        for source in evidence_sources
        for card in (getattr(source, "evidence_card", source),)
        if card is not None
        for claim in card.claims
        if claim.source_id == advisory_source_id
    }


def _proposal_to_graph_patch_block(
    proposal: EventEvidenceIntegrationProposal,
    *,
    evidence_spans: dict[str, str],
) -> GraphPatchBlock:
    patch_lines: list[GraphPatchLine] = []
    for fact in proposal.proposed_facts:
        patch_lines.append(
            GraphPatchLine(
                subject=fact.subject_id,
                predicate=fact.predicate_iri,
                object=fact.object_value,
                source_ids=list(fact.evidence_claim_ids),
            )
        )
    profile_gaps: list[ProfileGap] = []
    for gap in proposal.profile_gaps:
        profile_gaps.append(
            ProfileGap(
                field=gap.field,
                value=gap.normalized_value,
                evidence=evidence_spans.get(gap.field, ""),
                reason=gap.schema_mapping_reason_code,
            )
        )
    return GraphPatchBlock(
        patch_lines=patch_lines,
        profile_gaps=profile_gaps,
        raw="",
    )


def _build_event_evidence_integration_task_from_state(
    ctx: IngestContext,
    state: dict,
    *,
    event_uri: str,
    event_class: str,
) -> EventEvidenceIntegrationTask:
    guide = ctx.guide or load_schema_guide()
    facility_authority_result: AuthorityResolutionResult = state["facility_authority_result"]

    evidence_records = (
        EventEvidenceIntegrationEvidenceRecord(
            evidence_id=ctx.advisory.source_id,
            field_name="advisory_record",
            value=ctx.advisory.source_id,
            evidence_text=ctx.advisory.content,
            source_id=ctx.advisory.source_id,
        ),
    )
    selected_claims = (ctx.advisory.source_id,)

    facility_prop = facility_authority_result.resolution_proposal
    term_prop = state["terminology_authority_result"].resolution_proposal
    resolution_records = tuple(
        sorted(
            (
                EventEvidenceIntegrationResolutionRecord(
                    resolution_proposal_id=proposal.resolution_proposal_id,
                    decision=proposal.decision,
                    selected_candidate_id=proposal.selected_candidate_id,
                    supporting_evidence_claim_ids=(proposal.supporting_evidence_claim_ids),
                    authority_source_ids=proposal.authority_source_ids,
                )
                for proposal in (facility_prop, term_prop)
            ),
            key=lambda row: row.resolution_proposal_id,
        )
    )
    res_prop_ids = tuple(row.resolution_proposal_id for row in resolution_records)

    mentions = state.get("mentions") or parse_structured_fields(ctx.advisory.content)
    event_profile = get_tmi_profile(
        getattr(mentions, "event_type", ""),
        publishable_only=True,
    )
    if event_profile is None:
        raise ValueError("active TMI event profile is unavailable")
    profile_id = (
        f"profile-{event_class.split(':')[-1].lower() if ':' in event_class else 'default'}"
    )

    proposed_facts: list[EventEvidenceFactProposal] = []
    profile_gaps: list[EventEvidenceProfileGapProposal] = []

    def append_literal(field_name: str, value: str) -> None:
        predicate = event_profile.prefixed_property(field_name)
        if not value or predicate is None:
            return
        proposed_facts.append(
            EventEvidenceFactProposal(
                proposal_item_id=stable_contract_id(
                    "proposal-fact",
                    ctx.run_id,
                    event_uri,
                    predicate,
                    value,
                ),
                subject_id=event_uri,
                predicate_iri=predicate,
                object_kind="literal",
                object_value=value,
                evidence_claim_ids=tuple(sorted({ctx.advisory.source_id})),
                validation_profile_id=profile_id,
            )
        )

    proposed_facts.append(
        EventEvidenceFactProposal(
            proposal_item_id=stable_contract_id(
                "proposal-fact", ctx.run_id, event_uri, "rdf:type", event_class
            ),
            subject_id=event_uri,
            predicate_iri="rdf:type",
            object_kind="iri",
            object_value=event_class,
            evidence_claim_ids=tuple(sorted({ctx.advisory.source_id})),
            validation_profile_id=profile_id,
        )
    )

    fac_ref = ""
    if (
        facility_authority_result
        and facility_authority_result.evidence_card
        and facility_authority_result.evidence_card.canonical_refs
    ):
        fac_ref = facility_authority_result.evidence_card.canonical_refs[0]
        facility_class = next(
            (
                claim.ontology_target
                for claim in facility_authority_result.evidence_card.claims
                if claim.canonical_ref == fac_ref and claim.ontology_target
            ),
            "",
        )
        controlled_predicate = event_profile.prefixed_property(
            "controlled_facility"
        )
        if (
            controlled_predicate
            and facility_class
            and guide.object_property_range_ok(
                controlled_predicate,
                facility_class,
            )
        ):
            proposed_facts.append(
                EventEvidenceFactProposal(
                    proposal_item_id=stable_contract_id(
                        "proposal-fact",
                        ctx.run_id,
                        event_uri,
                        controlled_predicate,
                        fac_ref,
                    ),
                    subject_id=event_uri,
                    predicate_iri=controlled_predicate,
                    object_kind="iri",
                    object_value=fac_ref,
                    evidence_claim_ids=tuple(sorted({ctx.advisory.source_id})),
                    validation_profile_id=profile_id,
                )
            )
        elif getattr(mentions, "constrained_area", None):
            profile_gaps.append(
                EventEvidenceProfileGapProposal(
                    proposal_item_id=stable_contract_id(
                        "proposal-gap",
                        ctx.run_id,
                        event_uri,
                        "constrained_area",
                        mentions.constrained_area,
                    ),
                    event_id=event_uri,
                    field="constrained_area",
                    normalized_value=mentions.constrained_area,
                    evidence_claim_ids=tuple(sorted({ctx.advisory.source_id})),
                    schema_mapping_reason_code="range_not_admitted",
                    validation_profile_id=profile_id,
                )
            )
    if (
        getattr(mentions, "constrained_area", None)
        and not any(gap.field == "constrained_area" for gap in profile_gaps)
    ):
        profile_gaps.append(
            EventEvidenceProfileGapProposal(
                proposal_item_id=stable_contract_id(
                    "proposal-gap",
                    ctx.run_id,
                    event_uri,
                    "constrained_area",
                    mentions.constrained_area,
                ),
                event_id=event_uri,
                field="constrained_area",
                normalized_value=mentions.constrained_area,
                evidence_claim_ids=tuple(sorted({ctx.advisory.source_id})),
                schema_mapping_reason_code="range_not_admitted",
                validation_profile_id=profile_id,
            )
        )

    adv_num = getattr(mentions, "advisory_number", "")
    append_literal("advisory_number", adv_num)
    append_literal("issued_time", getattr(mentions, "issued_time", ""))

    extension_probability = getattr(mentions, "extension_probability", "")
    if event_profile.code in {"GS", "REROUTE"}:
        append_literal("extension_probability", extension_probability)

    start_time = getattr(mentions, "effective_start", "")
    end_time = getattr(mentions, "effective_end", "")
    append_literal("effective_start", start_time)
    append_literal("effective_end", end_time)

    impacting = getattr(mentions, "impacting_condition", "")
    if impacting:
        if event_profile.code == "GS":
            profile_gaps.append(
                EventEvidenceProfileGapProposal(
                    proposal_item_id=stable_contract_id(
                        "proposal-gap",
                        ctx.run_id,
                        event_uri,
                        "impacting_condition",
                        impacting,
                    ),
                    event_id=event_uri,
                    field="impacting_condition",
                    normalized_value=impacting,
                    evidence_claim_ids=tuple(sorted({ctx.advisory.source_id})),
                    schema_mapping_reason_code="not_in_profile",
                    validation_profile_id=profile_id,
                )
            )
        elif event_profile.code == "GDP":
            append_literal("impacting_condition", impacting)

    append_literal(
        "implementation_status",
        getattr(mentions, "implementation_status", ""),
    )
    append_literal("re_route_type", getattr(mentions, "re_route_type", ""))
    append_literal("re_route_reason", getattr(mentions, "re_route_reason", ""))
    append_literal(
        "re_route_time_type",
        getattr(mentions, "re_route_time_type", ""),
    )

    required_slots = ("event_type", *event_profile.required_fields)
    optional_slots = (
        ("impacting_condition",)
        if event_profile.code in {"GDP", "GS"}
        else ()
    )
    missing_slots = tuple(
        slot
        for slot, value in (
            ("controlled_facility", fac_ref),
            ("event_type", event_class),
            ("extension_probability", extension_probability),
            ("impacting_condition", impacting),
            ("effective_start", start_time),
            ("effective_end", end_time),
            (
                "implementation_status",
                getattr(mentions, "implementation_status", ""),
            ),
            ("re_route_type", getattr(mentions, "re_route_type", "")),
            ("re_route_reason", getattr(mentions, "re_route_reason", "")),
            (
                "re_route_time_type",
                getattr(mentions, "re_route_time_type", ""),
            ),
        )
        if slot in (*required_slots, *optional_slots) and not value
    )

    weather_bundle = state.get("weather_context")
    context_associations = tuple(
        sorted(
            (
                weather_bundle.associations
                if weather_bundle is not None and weather_bundle.status == "ok"
                else ()
            ),
            key=lambda row: row.association_id,
        )
    )
    public_observations = state.get("public_observation_context")
    observation_bundle = state.get("observation_context")
    profile_registry = load_validation_profile_registry(decision_guide=guide)
    public_profile = next(
        profile
        for profile in profile_registry.profiles
        if profile.ref.layer == "public_operational_observation"
    )
    summaries_by_id = {
        summary.summary_id: summary
        for summary in (
            public_observations.summaries
            if public_observations is not None and public_observations.status == "ok"
            else ()
        )
    }
    public_observations = tuple(
        sorted(
            (
                EventEvidenceIntegrationPublicObservation(
                    observation_id=trace.observation_id,
                    run_id=summaries_by_id[trace.summary_id].run_id,
                    event_id=summaries_by_id[trace.summary_id].event_id,
                    phase=summaries_by_id[trace.summary_id].phase,
                    metric_key=trace.metric_key,
                    value=trace.canonical_value,
                    derivation_id=trace.derivation_id,
                    validation_profile_id=public_profile.ref.profile_id,
                    validation_profile_checksum=(public_profile.ref.profile_checksum),
                    source_id=trace.source_id,
                    source_snapshot_sha256=trace.source_snapshot_sha256,
                )
                for trace in (
                    observation_bundle.fact_traces
                    if observation_bundle is not None and observation_bundle.status == "ok"
                    else ()
                )
                if trace.canonical_value is not None
            ),
            key=lambda row: row.observation_id,
        )
    )
    prepared_registry = state.get("prepared_source_snapshot")
    resolution_source_ids = {
        source_id for row in resolution_records for source_id in row.authority_source_ids
    }
    authority_registry = state.get("authority_source_records")
    authority_records_by_id = {
        record.source_id: record
        for record in (
            authority_registry.records
            if authority_registry is not None
            and authority_registry.status is AuthoritySourceRegistryStatus.OK
            else ()
        )
    }
    missing_authority_source_ids = resolution_source_ids - set(authority_records_by_id)
    if missing_authority_source_ids:
        raise ValueError(
            "resolution authority sources are unavailable for snapshot binding: "
            f"{sorted(missing_authority_source_ids)!r}"
        )
    authority_snapshots = (
        build_source_snapshot_registry(
            [authority_records_by_id[source_id] for source_id in sorted(resolution_source_ids)]
        ).snapshots
        if resolution_source_ids
        else ()
    )
    selected_source_ids = {
        ctx.advisory.source_id,
        *resolution_source_ids,
        *(row.source_id for row in context_associations),
        *(row.source_id for row in public_observations),
    }
    prepared_snapshots = (
        prepared_registry.snapshots
        if prepared_registry is not None
        else build_source_snapshot_registry([ctx.advisory]).snapshots
    )
    selected_snapshots_by_id = {
        snapshot.source_id: snapshot
        for snapshot in (*prepared_snapshots, *authority_snapshots)
        if snapshot.source_id in selected_source_ids
    }
    missing_source_ids = selected_source_ids - set(selected_snapshots_by_id)
    if missing_source_ids:
        raise ValueError(
            f"event evidence integration source snapshots are unavailable: {sorted(missing_source_ids)!r}"
        )
    source_bindings = tuple(
        SourceSnapshotBinding(
            source_id=source_id,
            source_family=selected_snapshots_by_id[source_id].family,
            source_snapshot_sha256=selected_snapshots_by_id[source_id].content_sha256,
        )
        for source_id in sorted(selected_source_ids)
    )
    available_layers = ["layer:advisory"]
    if context_associations:
        available_layers.append("layer:weather")
    if public_observations:
        available_layers.append("layer:bts")

    binding = ContractExecutionBinding(
        run_id=ctx.run_id,
        created_at=ctx.run_started_at or datetime.now(UTC),
        tool_version="deterministic-event-evidence-integration-v1",
    )

    sorted_proposed_facts = tuple(sorted(proposed_facts, key=lambda f: f.proposal_item_id))
    sorted_profile_gaps = tuple(sorted(profile_gaps, key=lambda g: g.proposal_item_id))

    return build_event_evidence_integration_task(
        run_id=ctx.run_id,
        event_id=event_uri,
        core_event_fact_ids=tuple(f.proposal_item_id for f in sorted_proposed_facts),
        resolution_proposal_ids=res_prop_ids,
        available_evidence_layer_ids=available_layers,
        required_event_slots=required_slots,
        optional_event_slots=optional_slots,
        missing_slots=missing_slots,
        schema_profile_id=profile_id,
        schema_context_id=guide.schema_slice_id,
        schema_snapshot_sha256=guide.checksum,
        selected_evidence_claim_ids=selected_claims,
        evidence_records=evidence_records,
        resolution_records=resolution_records,
        proposed_facts=sorted_proposed_facts,
        profile_gaps=sorted_profile_gaps,
        context_association_ids=tuple(row.association_id for row in context_associations),
        context_associations=context_associations,
        public_observation_ids=tuple(row.observation_id for row in public_observations),
        public_observations=public_observations,
        source_snapshot_bindings=source_bindings,
        binding=binding,
    )


def _integrate_event_evidence_node(
    state: dict,
    runtime: Runtime[IngestContext],
) -> dict:
    ctx: IngestContext = _ctx(runtime)
    preflight = state.get("resolution_preflight_status", "blocked")
    if preflight != "resolved":
        return {
            "event_evidence_integration_task": None,
            "event_evidence_integration_proposal": None,
            "event_evidence_integration_feedback": None,
            "event_evidence_integration_result": None,
            "integration_graph_patch": None,
            "integration_failure_reason": state.get(
                "resolution_preflight_reason",
                "required resolution preflight did not pass",
            ),
            "event_uri": "",
            "event_class": "",
            "model_calls": [],
        }
    if ctx.guide is None:
        ctx.guide = load_schema_guide()
    # Exact active-family classification is bound by the versioned ATMONTO
    # application profile. Terminology authority remains useful supporting
    # evidence, but a missing PCG definition does not erase an unambiguous
    # source-pattern-to-schema mapping.
    mentions = state.get("mentions") or parse_structured_fields(
        ctx.advisory.content
    )
    event_profile = get_tmi_profile(
        getattr(mentions, "event_type", ""),
        publishable_only=True,
    )
    event_class = (
        event_profile.prefixed_ontology_class
        if event_profile is not None
        else ""
    )
    event_uri = _event_uri(ctx.run_id, ctx.advisory.source_id, event_class or "UNRESOLVED")
    event_class_hint = state.get("event_class_hint", "")
    formal_event_uri_hint = state.get("formal_event_uri_hint", "")
    if not event_class or (event_class_hint and event_class != event_class_hint) or (
        formal_event_uri_hint and event_uri != formal_event_uri_hint
    ):
        return {
            "event_evidence_integration_task": None,
            "event_evidence_integration_proposal": None,
            "event_evidence_integration_feedback": None,
            "event_evidence_integration_result": None,
            "integration_graph_patch": None,
            "integration_failure_reason": "resolved event class differs from upstream schema binding",
            "event_uri": event_uri,
            "event_class": event_class,
        }

    # Construct EventEvidenceIntegrationTask
    integration_task = _build_event_evidence_integration_task_from_state(
        ctx, state, event_uri=event_uri, event_class=event_class
    )
    binding = ContractExecutionBinding(
        run_id=ctx.run_id,
        created_at=ctx.run_started_at or datetime.now(UTC),
        tool_version="deterministic-event-evidence-integration-v1",
    )

    optional_layer_results: list[EvidenceLayerResult] = [
        EvidenceLayerResult(
            layer_id="core",
            status=EvidenceLayerStatus.OK,
            required_for_task=True,
            artifact_ids=integration_task.core_event_fact_ids,
        )
    ]
    optional_limitations: list[str] = []
    for layer_id, bundle, artifact_ids in (
        (
            "layer:weather",
            state.get("weather_context"),
            integration_task.context_association_ids,
        ),
        (
            "layer:bts",
            state.get("observation_context"),
            integration_task.public_observation_ids,
        ),
    ):
        status = getattr(bundle, "status", "insufficient")
        failure_reason = getattr(bundle, "failure_reason", "") or (
            f"{layer_id} context is unavailable"
        )
        if status == "ok" and artifact_ids:
            optional_layer_results.append(
                EvidenceLayerResult(
                    layer_id=layer_id,
                    status=EvidenceLayerStatus.OK,
                    required_for_task=False,
                    artifact_ids=artifact_ids,
                )
            )
        elif status == "blocked":
            optional_layer_results.append(
                EvidenceLayerResult(
                    layer_id=layer_id,
                    status=EvidenceLayerStatus.BLOCKED,
                    required_for_task=False,
                    blocking_error_id=stable_contract_id(
                        "event-evidence-integration-layer-error",
                        ctx.run_id,
                        layer_id,
                        failure_reason,
                    ),
                )
            )
            optional_limitations.append(f"{layer_id}: {failure_reason}")
        else:
            optional_layer_results.append(
                EvidenceLayerResult(
                    layer_id=layer_id,
                    status=EvidenceLayerStatus.INSUFFICIENT,
                    required_for_task=False,
                    missing_reason_code=failure_reason,
                )
            )
            optional_limitations.append(f"{layer_id}: {failure_reason}")

    proposal = compile_event_evidence_integration_proposal(
        task=integration_task,
        integration_status=(
            EventEvidenceIntegrationStatus.PARTIAL
            if optional_limitations
            else None
        ),
        evidence_layer_results=optional_layer_results,
        limitations=optional_limitations,
        binding=binding,
    )
    integration_result = EventEvidenceIntegrationResult(
        proposal=proposal,
        feedback=None,
    )

    feedback = preflight_validate_event_evidence_proposal(
        task=integration_task,
        proposal=proposal,
        binding=binding,
    )
    if feedback is not None and not feedback.repairable:
        proposal = compile_event_evidence_integration_proposal(
            task=integration_task,
            integration_status=EventEvidenceIntegrationStatus.BLOCKED,
            evidence_layer_results=proposal.evidence_layer_results,
            proposed_facts=proposal.proposed_facts,
            evidence_bindings=proposal.evidence_bindings,
            resolution_proposal_ids=proposal.resolution_proposal_ids,
            context_association_ids=proposal.context_association_ids,
            profile_gaps=proposal.profile_gaps,
            omitted_slots=proposal.omitted_slots,
            limitations=(*proposal.limitations, feedback.violation_code),
            tool_trace_ids=proposal.tool_trace_ids,
            source_snapshot_bindings=proposal.source_snapshot_bindings,
            revision_count=proposal.revision_count,
            binding=binding,
        )
        integration_result = EventEvidenceIntegrationResult(
            proposal=proposal,
            feedback=feedback,
            failure_reason=feedback.violation_code,
        )

    publishable_integration = proposal.integration_status in {
        EventEvidenceIntegrationStatus.OK,
        EventEvidenceIntegrationStatus.PARTIAL,
    }
    mentions = state.get("mentions") or parse_structured_fields(ctx.advisory.content)
    block = (
        _proposal_to_graph_patch_block(
            proposal,
            evidence_spans=mentions.evidence_spans,
        )
        if publishable_integration
        else None
    )
    return {
        "event_evidence_integration_task": integration_task,
        "event_evidence_integration_proposal": proposal,
        "event_evidence_integration_feedback": feedback,
        "event_evidence_integration_result": integration_result,
        "integration_graph_patch": block,
        "integration_failure_reason": integration_result.failure_reason,
        "event_uri": event_uri,
        "event_class": event_class,
        "model_calls": [],
    }


def _validate_event_patch_node(
    state: dict,
    runtime: Runtime[IngestContext],
) -> dict:
    ctx: IngestContext = _ctx(runtime)
    integration_graph_patch: GraphPatchBlock | None = state.get("integration_graph_patch")
    if integration_graph_patch is None:
        return {
            "validation": None,
            "direct_fact_traces": (),
            "profile_gap_rows": (),
            "formal_publication": None,
            "ingestion_package": None,
        }
    # No resolved event class -> the system abstained; do not materialize.
    event_class = state.get("event_class", "")
    if not event_class:
        return {
            "validation": None,
            "direct_fact_traces": (),
            "profile_gap_rows": (),
            "formal_publication": None,
            "ingestion_package": None,
        }
    guide = ctx.guide or load_schema_guide()
    facility_authority_result: AuthorityResolutionResult | None = state.get(
        "facility_authority_result"
    )
    terminology_authority_result: AuthorityResolutionResult | None = state.get(
        "terminology_authority_result"
    )
    advisory_evidence = state.get("advisory_evidence")
    known_source_ids = _accepted_event_source_ids(
        ctx.advisory.source_id,
        advisory_evidence,
        facility_authority_result,
        terminology_authority_result,
    )
    # Canonical entities resolved by the facility resolution service.
    canonical_entities: dict[str, str] = {}
    if facility_authority_result and facility_authority_result.evidence_card:
        for claim in facility_authority_result.evidence_card.claims:
            if (
                claim.source_id in known_source_ids
                and claim.canonical_ref
                and claim.ontology_target
            ):
                canonical_entities[claim.canonical_ref] = claim.ontology_target
    evidence_cards = []
    if facility_authority_result and facility_authority_result.evidence_card:
        evidence_cards.append(facility_authority_result.evidence_card)
    if terminology_authority_result and terminology_authority_result.evidence_card:
        evidence_cards.append(terminology_authority_result.evidence_card)
    if advisory_evidence:
        evidence_cards.append(advisory_evidence)

    # Keep the provisional advisory registry in memory for Kernel and trace
    # validation. ``integrate_event_context`` owns the one final,
    # multi-source ``source_snapshots.jsonl`` artifact for the run.
    snapshot_registry = build_source_snapshot_registry([ctx.advisory])

    # Event-patch Formal Graph Kernel: the deterministic admissibility gate
    # between model output and case publication (plan §4, §5.4). It runs the
    # authority/schema/source/evidence checks and GroundStop graph constraints
    # before the final multi-profile publication step.
    event_uri = state.get("event_uri", "") or _event_uri(
        ctx.run_id, ctx.advisory.source_id, event_class
    )
    validation: GraphValidationResult = validate_graph_patch(
        block=integration_graph_patch,
        event_iri=event_uri,
        event_class=event_class,
        schema_guide=guide,
        canonical_entities=canonical_entities,
        known_source_ids=known_source_ids,
        evidence_cards=evidence_cards,
        source_snapshot=snapshot_registry,
    )
    # Build exact provenance rows in memory. Persistence happens only after the
    # final publication package is accepted by the evidence-store transaction.
    direct_fact_traces = build_fact_trace_rows(
        result=validation,
        block=integration_graph_patch,
        evidence_cards=evidence_cards,
        source_snapshot=snapshot_registry,
    )
    profile_gap_rows = build_profile_gap_rows(
        result=validation,
        event_id=event_uri,
        source_snapshot=snapshot_registry,
    )
    if not validation.publishable:
        return {
            "validation": validation,
            "direct_fact_traces": direct_fact_traces,
            "profile_gap_rows": profile_gap_rows,
            "formal_publication": None,
            "ingestion_package": None,
            "source_snapshot": snapshot_registry,
        }

    return {
        "validation": validation,
        "direct_fact_traces": direct_fact_traces,
        "profile_gap_rows": profile_gap_rows,
        "formal_publication": None,
        "ingestion_package": None,
        "source_snapshot": snapshot_registry,
    }


def _publish_event_node(state: dict, runtime: Runtime[IngestContext]) -> dict:
    """Run the final multi-profile publication path without model calls."""

    return integrate_event_context(_ctx(runtime), state)


def run_ingest(ctx: IngestContext) -> dict:
    """Run one ingest graph invocation with isolated run-scoped context."""

    graph = build_ingest_graph()
    return graph.invoke({}, context=ctx, config={"recursion_limit": 20})
