"""Fixed LangGraph collaboration topology for ingest (design §14).

The Workflow Coordinator is a deterministic LangGraph controller:

    START
      -> Advisory Agent
      -> parallel fan-out:
           Facility Agent
           Terminology Agent
      -> evidence-card join
      -> Knowledge Graph Construction Agent
      -> Graph Patch parser + schema validator + RDF/Neo4j materializer
      -> END

The Coordinator creates tasks, fans out, joins, and records state transitions.
It does NOT call an LLM and is not an Agent role.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json
import operator
from typing import Annotated, Any, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import model_validator

from aviation_agentic_ai.agent_system.agents import (
    FacilityCandidates,
    KGConstructionInput,
    TermCandidates,
    _resolve_facility_compatibility,
    _resolve_terminology_compatibility,
    parse_structured_fields,
    run_advisory_agent,
    run_kg_construction_agent,
)
from aviation_agentic_ai.agent_system.authority_evidence import (
    AuthorityBuildStatus,
    LoadedAuthorityCatalog,
    build_facility_resolution_candidate,
    build_term_resolution_candidate,
)
from aviation_agentic_ai.agent_system.contracts import (
    BTSManifestBinding,
    AgentResult,
    AgentStatus,
    AgentTask,
    BTSOnTimeRow,
    GraphValidationResult,
    SourceFamily,
    SourceRecord,
)
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    FrozenContractModel,
    ResolutionDecision,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.context_artifacts import (
    integrate_decision_context,
)
from aviation_agentic_ai.agent_system.formal_graph import (
    validate_graph_patch,
    write_fact_trace,
    write_profile_gaps,
)
from aviation_agentic_ai.agent_system.schema_guide import SchemaGuide, load_schema_guide
from aviation_agentic_ai.agent_system.sources import (
    build_source_snapshot_registry,
    write_source_snapshot_registry,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id
from aviation_agentic_ai.agent_system.runtime import (
    ModelInvoker,
    ModelInvokerFactory,
)

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
                raise ValueError(
                    "blocked authority registry requires an error and no records"
                )
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
    model_invoker: ModelInvoker | None = None
    model_invoker_factory: ModelInvokerFactory | None = None
    semantic_resolution_tool_model_factory: ToolModelFactory | None = None
    kg_tool_model_factory: ToolModelFactory | None = None
    authority_catalog: LoadedAuthorityCatalog | None = None
    run_started_at: datetime | None = None
    run_id: str = "agent-system"
    output_dir: str = ""


def _event_uri(run_id: str, source_id: str, event_class: str) -> str:
    return stable_id("evt", source_id, event_class)


# Typed state schema for the ingest graph. Additive reducers (operator.add)
# let the parallel Facility/Terminology branches contribute to ``model_calls``
# without a concurrent-write conflict; each branch also writes its own distinct
# result key.
class IngestState(TypedDict):
    mentions: Any
    advisory_result: Any
    facility_result: Any
    terminology_result: Any
    facility_resolution_outcome: Any
    terminology_resolution_outcome: Any
    facility_resolution_task: Any
    facility_resolution_proposal: Any
    facility_resolution_tool_traces: Any
    terminology_resolution_task: Any
    terminology_resolution_proposal: Any
    terminology_resolution_tool_traces: Any
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
    kg_result: Any
    event_uri: str
    event_class: str
    materialization: Any
    validation: Any
    source_snapshot: Any
    decision_context_event: Any
    weather_context: Any
    outcome_context: Any
    observation_context: Any
    context_artifacts: Any
    formal_layers: Any
    public_observation_publication: Any
    model_calls: Annotated[list, operator.add]


def build_ingest_graph() -> Any:
    """Compile the fixed ingest topology as a LangGraph StateGraph."""

    sg = StateGraph(IngestState)
    sg.add_node("advisory", _advisory_node)
    sg.add_node("facility", _facility_node)
    sg.add_node("terminology", _terminology_node)
    sg.add_node("join", _join_node)
    sg.add_node("kg_construction", _kg_construction_node)
    sg.add_node("materialize", _materialize_node)
    sg.add_node("decision_context", _decision_context_node)
    sg.add_edge(START, "advisory")
    # Parallel fan-out after the Advisory Agent.
    sg.add_edge("advisory", "facility")
    sg.add_edge("advisory", "terminology")
    # Join after the two specialist Agents.
    sg.add_edge("facility", "join")
    sg.add_edge("terminology", "join")
    sg.add_edge("join", "kg_construction")
    sg.add_edge("kg_construction", "materialize")
    sg.add_edge("materialize", "decision_context")
    sg.add_edge("decision_context", END)
    return sg.compile()


# ---------------------------------------------------------------------------
# Node functions (receive/return the shared state dict)
# ---------------------------------------------------------------------------

# The ingest context is set on the module-level holder by ``run_ingest`` so the
# parallel fan-out nodes (facility/terminology) can read it without depending
# on LangGraph's parallel-branch state merge (which may drop non-output keys).
_CTX_HOLDER: IngestContext | None = None


def _ctx() -> IngestContext:
    if _CTX_HOLDER is None:
        raise RuntimeError("ingest context not set; call run_ingest()")
    return _CTX_HOLDER


def _advisory_node(state: dict) -> dict:
    ctx: IngestContext = _ctx()
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
        for event_class in (
            guide.event_class_for_term("GDP"),
            guide.event_class_for_term("GS"),
        )
        if event_class
    ]
    result = run_advisory_agent(
        task=task,
        advisory=ctx.advisory,
        event_classes=event_classes,
        mentions=mentions,
        model_invoker=ctx.model_invoker,
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
        _event_uri(ctx.run_id, ctx.advisory.source_id, event_class_hint)
        if event_class_hint
        else ""
    )
    return {
        "advisory_result": result,
        "mentions": mentions,
        "resolution_event_id": resolution_event_id,
        "resolution_event_mention": event_mention,
        "event_class_hint": event_class_hint or "",
        "formal_event_uri_hint": formal_event_uri_hint,
        "model_calls": list(result.model_calls),
    }


def _facility_candidates_for_mention(
    all_candidates: list,
    mention: str,
    expected_entity_type: str | None = None,
) -> list:
    """Filter authority facility candidates to those matching the mention token.

    A candidate matches if the mention equals one of its codes or aliases
    (normalized, uppercase). This turns the facility registry into the
    authority lookup the Facility Agent uses (design §9.4). Expected type is
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


def _facility_node(state: dict) -> dict:
    ctx: IngestContext = _ctx()
    mentions = state.get("mentions")
    mention_token = (
        getattr(mentions, "controlled_facility", None)
        or "MISSING_FACILITY_MENTION"
    )
    # §11.4: pass the exact advisory evidence span (e.g. ``CTL ELEMENT: JFK``)
    # to the Facility Agent so its claim carries source-contained evidence, not
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
        domain_reason = (
            authority_catalog.facility.reason_code
            or "FACILITY_AUTHORITY_BLOCKED"
        )
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
                    getattr(mentions, "facility_structural_slot", None)
                    or "controlled_nas_element"
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
    cands = FacilityCandidates(
        mention=mention_token,
        candidates=matched,
        source_id=ctx.advisory.source_id,
        structural_slot=(
            getattr(mentions, "facility_structural_slot", None)
            or "controlled_nas_element"
        ),
        expected_entity_type=(
            getattr(mentions, "facility_expected_entity_type", None)
            or "unknown_facility_type"
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
        resolution_tool_version="resolution-compatibility-v1",
        authority_domain_status=domain_status,
        authority_domain_reason_code=domain_reason,
        authority_domain_error_id=domain_error,
        authority_candidate_results=built,
    )
    resolution_kwargs = {"task": task, "candidates": cands}
    if ctx.semantic_resolution_tool_model_factory is not None:
        resolution_kwargs["semantic_resolution_tool_model_factory"] = (
            ctx.semantic_resolution_tool_model_factory
        )
    compatibility = _resolve_facility_compatibility(**resolution_kwargs)
    result = compatibility.agent_result
    # model_calls uses an additive reducer so parallel branches can each contribute.
    return {
        "facility_result": result,
        "facility_resolution_outcome": compatibility.domain_outcome,
        "facility_resolution_task": compatibility.resolution_task,
        "facility_resolution_proposal": compatibility.resolution_proposal,
        "facility_resolution_tool_traces": compatibility.resolution_tool_traces,
        "authority_source_records": _authority_source_registry(
            compatibility.authority_source_records
        ),
        "model_calls": list(result.model_calls),
    }


def _term_candidates_for_mention(all_terms: list, mention: str) -> list:
    """Filter authority term candidates to those whose abbreviation matches.

    A term matches if its abbreviation equals the mention token (normalized,
    uppercase). This is the authority lookup the Terminology Agent uses
    (design §10.4); e.g. a ``GS`` mention yields both the Ground Stop TMI and
    the Glide Slope procedure, which the Agent then disambiguates by category.
    """

    if not mention:
        return []
    token = mention.upper()
    return sorted(
        (
            term
            for term in all_terms
            if getattr(term, "abbreviation", "").upper() == token
        ),
        key=lambda term: term.term_id,
    )


def _terminology_node(state: dict) -> dict:
    ctx: IngestContext = _ctx()
    mentions = state.get("mentions")
    mention_token = (
        getattr(mentions, "operational_term", None) or "MISSING_EVENT_MENTION"
    )
    # §11.4: pass the exact advisory evidence span (the Ground Stop mention in
    # context) to the Terminology Agent so the resolved term claim carries
    # source-contained evidence the Formal Graph Kernel can bind rdf:type to.
    spans = getattr(mentions, "evidence_spans", {}) or {}
    advisory_evidence = spans.get("operational_term", "") or spans.get("event_type", "")
    task = AgentTask(
        run_id=ctx.run_id,
        source_id=ctx.advisory.source_id,
        objective="resolve operational term",
        allowed_tools=["lookup_faa_glossary", "lookup_pcg_term", "resolve_term_registry", "resolve_schema_event_class"],
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
        domain_reason = (
            authority_catalog.terminology.reason_code
            or "TERMINOLOGY_AUTHORITY_BLOCKED"
        )
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
    cands = TermCandidates(
        mention=mention_token,
        candidates=matched,
        source_id=ctx.advisory.source_id,
        guide=guide,
        structural_slot=(
            getattr(mentions, "term_structural_slot", None)
            or "traffic_management_initiative_type"
        ),
        expected_entity_type=(
            getattr(mentions, "term_expected_entity_type", None)
            or "traffic_management_initiative"
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
        resolution_tool_version="resolution-compatibility-v1",
        authority_domain_status=domain_status,
        authority_domain_reason_code=domain_reason,
        authority_domain_error_id=domain_error,
        authority_candidate_results=built,
    )
    resolution_kwargs = {"task": task, "candidates": cands}
    if ctx.semantic_resolution_tool_model_factory is not None:
        resolution_kwargs["semantic_resolution_tool_model_factory"] = (
            ctx.semantic_resolution_tool_model_factory
        )
    compatibility = _resolve_terminology_compatibility(**resolution_kwargs)
    result = compatibility.agent_result
    return {
        "terminology_result": result,
        "terminology_resolution_outcome": compatibility.domain_outcome,
        "terminology_resolution_task": compatibility.resolution_task,
        "terminology_resolution_proposal": compatibility.resolution_proposal,
        "terminology_resolution_tool_traces": compatibility.resolution_tool_traces,
        "authority_source_records": _authority_source_registry(
            compatibility.authority_source_records
        ),
        "model_calls": list(result.model_calls),
    }


def _join_node(state: dict) -> dict:
    """Join independently audited domains and compute the required preflight."""

    outcomes = (
        state.get("facility_resolution_outcome"),
        state.get("terminology_resolution_outcome"),
    )
    authority_registry = state.get("authority_source_records")
    if (
        authority_registry is not None
        and authority_registry.status is AuthoritySourceRegistryStatus.BLOCKED
    ):
        status = "blocked"
        reason = (
            authority_registry.reason_code
            or "authority source registry blocked"
        )
    elif any(
        outcome is None or outcome.decision is ResolutionDecision.BLOCKED
        for outcome in outcomes
    ):
        status = "blocked"
        reason = "required resolution domain blocked"
    elif any(
        outcome.decision is not ResolutionDecision.ACCEPTED
        for outcome in outcomes
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


def _accepted_event_source_ids(
    advisory_source_id: str,
    *results: AgentResult | None,
) -> set[str]:
    """Return source IDs from retained event claims, bound to this advisory."""

    return {
        claim.source_id
        for result in results
        if result is not None and result.evidence_card is not None
        for claim in result.evidence_card.claims
        if claim.source_id == advisory_source_id
    }


def _kg_construction_node(state: dict) -> dict:
    ctx: IngestContext = _ctx()
    preflight = state.get("resolution_preflight_status", "blocked")
    if preflight != "resolved":
        blocked = preflight == "blocked"
        return {
            "kg_result": AgentResult(
                status=AgentStatus.BLOCKED if blocked else AgentStatus.ABSTAIN,
                failure_reason=state.get(
                    "resolution_preflight_reason",
                    "required resolution preflight did not pass",
                ),
            )
        }
    advisory_result: AgentResult = state["advisory_result"]
    facility_result: AgentResult = state["facility_result"]
    terminology_result: AgentResult = state["terminology_result"]
    if ctx.guide is None:
        ctx.guide = load_schema_guide()
    # The resolved event class comes ONLY from the Terminology Agent. If no
    # event type was resolved the system abstains and constructs no graph
    # (design §11.6); there is no default GDP fallback.
    event_class = next(
        (c.ontology_target for c in terminology_result.evidence_card.claims if c.ontology_target),
        "",
    )
    event_uri = _event_uri(ctx.run_id, ctx.advisory.source_id, event_class or "UNRESOLVED")
    event_class_hint = state.get("event_class_hint", "")
    formal_event_uri_hint = state.get("formal_event_uri_hint", "")
    if (
        (event_class_hint and event_class != event_class_hint)
        or (
            formal_event_uri_hint
            and event_uri != formal_event_uri_hint
        )
    ):
        return {
            "kg_result": AgentResult(
                status=AgentStatus.BLOCKED,
                failure_reason="resolved event class differs from upstream schema binding",
            ),
            "event_uri": event_uri,
            "event_class": event_class,
        }
    task = AgentTask(
        run_id=ctx.run_id,
        source_id=ctx.advisory.source_id,
        objective="construct event graph patch",
        allowed_tools=["get_schema_context", "resolve_canonical_ref", "get_source_evidence"],
        schema_slice_id=ctx.guide.schema_slice_id,
    )
    allowed_source_ids = _accepted_event_source_ids(
        ctx.advisory.source_id,
        advisory_result,
        facility_result,
        terminology_result,
    )
    inputs = KGConstructionInput(
        advisory=ctx.advisory,
        advisory_card=advisory_result.evidence_card,  # type: ignore[arg-type]
        facility_card=facility_result.evidence_card,  # type: ignore[arg-type]
        terminology_card=terminology_result.evidence_card,  # type: ignore[arg-type]
        event_uri=event_uri,
        event_class=event_class,
        guide=ctx.guide,
        allowed_source_ids=allowed_source_ids,
    )
    if ctx.kg_tool_model_factory is None:
        # Offline/contract path: no native tool model -> abstain (no formal patch).
        return {
            "kg_result": AgentResult(
                status=AgentStatus.ABSTAIN,
                failure_reason="no KG tool model factory",
            )
        }
    result = run_kg_construction_agent(
        task=task,
        inputs=inputs,
        tool_model_factory=ctx.kg_tool_model_factory,
    )
    return {
        "kg_result": result,
        "event_uri": event_uri,
        "event_class": event_class,
        "model_calls": list(result.model_calls),
    }


def _materialize_node(state: dict) -> dict:
    ctx: IngestContext = _ctx()
    kg_result: AgentResult = state.get("kg_result")
    if kg_result is None or kg_result.graph_patch is None:
        return {"materialization": None, "validation": None}
    # No resolved event class -> the system abstained; do not materialize.
    event_class = state.get("event_class", "")
    if not event_class:
        return {"materialization": None, "validation": None}
    guide = ctx.guide or load_schema_guide()
    facility_result: AgentResult | None = state.get("facility_result")
    terminology_result: AgentResult | None = state.get("terminology_result")
    advisory_result: AgentResult | None = state.get("advisory_result")
    known_source_ids = _accepted_event_source_ids(
        ctx.advisory.source_id,
        advisory_result,
        facility_result,
        terminology_result,
    )
    # Canonical entities resolved by the Facility Agent.
    canonical_entities: dict[str, str] = {}
    if facility_result and facility_result.evidence_card:
        for claim in facility_result.evidence_card.claims:
            if (
                claim.source_id in known_source_ids
                and claim.canonical_ref
                and claim.ontology_target
            ):
                canonical_entities[claim.canonical_ref] = claim.ontology_target
    evidence_cards = []
    if facility_result and facility_result.evidence_card:
        evidence_cards.append(facility_result.evidence_card)
    if terminology_result and terminology_result.evidence_card:
        evidence_cards.append(terminology_result.evidence_card)
    if advisory_result and advisory_result.evidence_card:
        evidence_cards.append(advisory_result.evidence_card)

    # Persist the source snapshot (plan §5.2) so every accepted fact binds to
    # auditable, checksum-pinned source content.
    snapshot_registry = build_source_snapshot_registry([ctx.advisory])
    write_source_snapshot_registry(snapshot_registry, ctx.output_dir)

    # Formal Graph Kernel: the deterministic gate between model output and the
    # formal graph (plan §4, §5.4). Runs the 10 authority/schema/source/
    # evidence checks and the GroundStop graph-level constraints before any
    # materialization. A non-publishable result produces no formal artifacts.
    event_uri = state.get("event_uri", "") or _event_uri(ctx.run_id, ctx.advisory.source_id, event_class)
    validation: GraphValidationResult = validate_graph_patch(
        block=kg_result.graph_patch,
        event_iri=event_uri,
        event_class=event_class,
        schema_guide=guide,
        canonical_entities=canonical_entities,
        known_source_ids=known_source_ids,
        evidence_cards=evidence_cards,
        source_snapshot=snapshot_registry,
    )
    # Fact trace: one row per accepted fact (plan §5.5), written regardless of
    # publishability so rejected/blocked runs still leave an audit trail.
    write_fact_trace(
        result=validation,
        block=kg_result.graph_patch,
        evidence_cards=evidence_cards,
        source_snapshot=snapshot_registry,
        output_dir=ctx.output_dir,
    )
    write_profile_gaps(
        result=validation,
        event_id=event_uri,
        source_snapshot=snapshot_registry,
        output_dir=ctx.output_dir,
    )
    if not validation.publishable:
        # Fail-closed: do not produce formal graph artifacts for a rejected or
        # constraint-violating patch.
        return {
            "materialization": None,
            "validation": validation,
            "source_snapshot": snapshot_registry,
        }

    # The deterministic context node owns the one canonical publication after
    # all independently validated layers have been selected. Keeping the core
    # validation and audit artifacts here prevents optional context failures
    # from weakening the Formal Graph Kernel without writing a stale partial KG.
    return {
        "materialization": None,
        "validation": validation,
        "source_snapshot": snapshot_registry,
    }


def _decision_context_node(state: dict) -> dict:
    """Attach deterministic optional context without issuing model calls."""

    return integrate_decision_context(_ctx(), state)


def run_ingest(ctx: IngestContext) -> dict:
    """Run the fixed ingest graph and return the final state."""

    global _CTX_HOLDER  # noqa: PLW0603
    _CTX_HOLDER = ctx
    graph = build_ingest_graph()
    return graph.invoke({}, config={"recursion_limit": 20})
