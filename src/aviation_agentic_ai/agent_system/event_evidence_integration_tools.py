"""Typed, task-bounded read-only tools for TMI event evidence integration."""

from __future__ import annotations

from typing import Literal
from langchain_core.tools import BaseTool, tool
from pydantic import Field

from collections.abc import Sequence
from aviation_agentic_ai.agent_system.contracts import (
    SourceFamily,
    StrictModel,
    WeatherContextAssociation,
)
from aviation_agentic_ai.agent_system.construction_contracts import (
    EventEvidenceIntegrationStatus,
    EventEvidenceIntegrationEvidenceRecord,
    EventEvidenceIntegrationProposal,
    EventEvidenceIntegrationProposalFields,
    EventEvidenceIntegrationPublicObservation,
    EventEvidenceIntegrationResolutionRecord,
    EventEvidenceIntegrationTask,
    EventEvidenceIntegrationTaskFields,
    EventEvidenceFactProposal,
    EventEvidenceProfileGapProposal,
    EvidenceLayerResult,
    EvidenceLayerStatus,
    ContractExecutionBinding,
    SourceSnapshotBinding,
    EventEvidenceIntegrationFeedback,
    EventEvidenceIntegrationFeedbackFields,
    canonical_id_tuple_token,
    seal_event_evidence_integration_proposal,
    seal_event_evidence_integration_task,
    seal_event_evidence_integration_feedback,
    stable_contract_id,
)


class EventEvidenceIntegrationToolError(RuntimeError):
    """Raised when a event evidence integration tool request escapes its sealed task."""


class GetEvidenceInput(StrictModel):
    """Selected evidence IDs from the current sealed event evidence integration task."""

    evidence_ids: list[str] = Field(min_length=1, max_length=10)


class GetResolutionResultInput(StrictModel):
    """Resolution proposal IDs from the current sealed event evidence integration task."""

    resolution_proposal_ids: list[str] = Field(min_length=1, max_length=5)


class GetContextAssociationsInput(StrictModel):
    """Context association IDs from the current sealed event evidence integration task."""

    association_ids: list[str] = Field(min_length=1, max_length=10)


class GetPublicObservationsInput(StrictModel):
    """Public observation IDs from the current sealed event evidence integration task."""

    observation_ids: list[str] = Field(min_length=1, max_length=10)


class EventEvidenceIntegrationCandidateFactSummary(StrictModel):
    """Compact model-visible projection of one sealed formal-fact candidate."""

    proposal_item_id: str
    predicate_iri: str
    object_kind: Literal["iri", "literal"]
    object_value: str
    evidence_claim_ids: tuple[str, ...] = ()
    derivation_ids: tuple[str, ...] = ()


class EventEvidenceIntegrationCandidateProfileGapSummary(StrictModel):
    """Compact model-visible projection of one sealed profile-gap candidate."""

    proposal_item_id: str
    field: str
    normalized_value: str
    evidence_claim_ids: tuple[str, ...]
    schema_mapping_reason_code: str


class EventEvidenceIntegrationToolResult(StrictModel):
    """One deterministic, JSON-serializable event-evidence-integration tool observation."""

    tool: Literal[
        "get_event_requirements",
        "get_schema_context",
        "get_source_evidence",
        "get_resolution_result",
        "get_context_associations",
        "get_public_observations",
        "get_candidate_bundle",
    ]
    status: Literal["ok", "insufficient", "blocked"] = "ok"
    event_id: str = ""
    required_event_slots: list[str] = Field(default_factory=list)
    optional_event_slots: list[str] = Field(default_factory=list)
    missing_slots: list[str] = Field(default_factory=list)
    schema_profile_id: str = ""
    schema_context_id: str = ""
    schema_snapshot_sha256: str | None = None
    available_evidence_layer_ids: list[str] = Field(default_factory=list)
    remaining_tool_budget: int = 6
    requested_evidence_ids: list[str] = Field(default_factory=list)
    resolution_proposal_ids: list[str] = Field(default_factory=list)
    association_ids: list[str] = Field(default_factory=list)
    observation_ids: list[str] = Field(default_factory=list)
    evidence_records: list[EventEvidenceIntegrationEvidenceRecord] = Field(default_factory=list)
    resolution_records: list[EventEvidenceIntegrationResolutionRecord] = Field(
        default_factory=list
    )
    context_associations: list[WeatherContextAssociation] = Field(
        default_factory=list
    )
    public_observations: list[EventEvidenceIntegrationPublicObservation] = Field(
        default_factory=list
    )
    candidate_bundle_id: str = ""
    candidate_facts: list[EventEvidenceIntegrationCandidateFactSummary] = Field(
        default_factory=list
    )
    candidate_profile_gaps: list[EventEvidenceIntegrationCandidateProfileGapSummary] = Field(
        default_factory=list
    )
    context_association_count: int = Field(default=0, ge=0)
    public_observation_count: int = Field(default=0, ge=0)
    source_snapshot_bindings: list[SourceSnapshotBinding] = Field(
        default_factory=list
    )
    failure_reason: str = ""


class EventEvidenceIntegrationToolGateway:
    """Read-only view of event evidence integration material scoped to one ``EventEvidenceIntegrationTask``."""

    def __init__(self, *, task: EventEvidenceIntegrationTask) -> None:
        self.task = task
        self._selected_evidence_claim_ids = set(task.selected_evidence_claim_ids)
        self._resolution_proposal_ids = set(task.resolution_proposal_ids)
        self._context_association_ids = set(task.context_association_ids)
        self._public_observation_ids = set(task.public_observation_ids)
        self._evidence_records = {
            row.evidence_id: row for row in task.evidence_records
        }
        self._resolution_records = {
            row.resolution_proposal_id: row for row in task.resolution_records
        }
        self._context_associations = {
            row.association_id: row for row in task.context_associations
        }
        self._public_observations = {
            row.observation_id: row for row in task.public_observations
        }

    def get_event_requirements(self) -> EventEvidenceIntegrationToolResult:
        """Read required, optional, and missing event slots and evidence layers."""

        return EventEvidenceIntegrationToolResult(
            tool="get_event_requirements",
            event_id=self.task.event_id,
            required_event_slots=list(self.task.required_event_slots),
            optional_event_slots=list(self.task.optional_event_slots),
            missing_slots=list(self.task.missing_slots),
            schema_profile_id=self.task.schema_profile_id,
            available_evidence_layer_ids=list(self.task.available_evidence_layer_ids),
            remaining_tool_budget=self.task.remaining_tool_budget,
        )

    def get_candidate_bundle(self) -> EventEvidenceIntegrationToolResult:
        """Read the compact sealed candidates and evidence needed for acceptance."""

        candidate_bundle_id = stable_contract_id(
            "event-evidence-integration-candidate-bundle",
            self.task.task_id,
            self.task.payload_checksum,
        )
        model_visible_source_ids = {
            *(record.source_id for record in self.task.evidence_records),
            *(
                source_id
                for record in self.task.resolution_records
                for source_id in record.authority_source_ids
            ),
        }
        return EventEvidenceIntegrationToolResult(
            tool="get_candidate_bundle",
            event_id=self.task.event_id,
            schema_profile_id=self.task.schema_profile_id,
            schema_context_id=self.task.schema_context_id,
            schema_snapshot_sha256=self.task.schema_snapshot_sha256,
            available_evidence_layer_ids=list(
                self.task.available_evidence_layer_ids
            ),
            candidate_bundle_id=candidate_bundle_id,
            candidate_facts=[
                EventEvidenceIntegrationCandidateFactSummary(
                    proposal_item_id=row.proposal_item_id,
                    predicate_iri=row.predicate_iri,
                    object_kind=row.object_kind,
                    object_value=row.object_value,
                    evidence_claim_ids=row.evidence_claim_ids,
                    derivation_ids=row.derivation_ids,
                )
                for row in self.task.proposed_facts
            ],
            candidate_profile_gaps=[
                EventEvidenceIntegrationCandidateProfileGapSummary(
                    proposal_item_id=row.proposal_item_id,
                    field=row.field,
                    normalized_value=row.normalized_value,
                    evidence_claim_ids=row.evidence_claim_ids,
                    schema_mapping_reason_code=row.schema_mapping_reason_code,
                )
                for row in self.task.profile_gaps
            ],
            evidence_records=list(self.task.evidence_records),
            resolution_proposal_ids=list(self.task.resolution_proposal_ids),
            resolution_records=list(self.task.resolution_records),
            context_association_count=len(self.task.context_associations),
            public_observation_count=len(self.task.public_observations),
            source_snapshot_bindings=[
                binding
                for binding in self.task.source_snapshot_bindings
                if binding.source_id in model_visible_source_ids
            ],
        )

    def get_schema_context(self) -> EventEvidenceIntegrationToolResult:
        """Read schema profile, context ID, and snapshot SHA for the task."""

        return EventEvidenceIntegrationToolResult(
            tool="get_schema_context",
            event_id=self.task.event_id,
            schema_profile_id=self.task.schema_profile_id,
            schema_context_id=self.task.schema_context_id,
            schema_snapshot_sha256=self.task.schema_snapshot_sha256,
        )

    def get_source_evidence(
        self,
        *,
        evidence_ids: list[str],
    ) -> EventEvidenceIntegrationToolResult:
        """Read task-bound source evidence claims and snapshot bindings."""

        if len(evidence_ids) != len(set(evidence_ids)):
            raise EventEvidenceIntegrationToolError("duplicate evidence IDs are not allowed")
        unknown = sorted(set(evidence_ids) - self._selected_evidence_claim_ids)
        if unknown:
            raise EventEvidenceIntegrationToolError(
                f"evidence IDs are outside the sealed task: {unknown}"
            )
        records = [self._evidence_records[row_id] for row_id in sorted(evidence_ids)]
        return EventEvidenceIntegrationToolResult(
            tool="get_source_evidence",
            event_id=self.task.event_id,
            requested_evidence_ids=sorted(evidence_ids),
            evidence_records=records,
            source_snapshot_bindings=[
                binding
                for binding in self.task.source_snapshot_bindings
                if binding.source_id
                in {record.source_id for record in records}
            ],
        )

    def get_resolution_result(
        self,
        *,
        resolution_proposal_ids: list[str],
    ) -> EventEvidenceIntegrationToolResult:
        """Read resolution proposals bound to the task."""

        if len(resolution_proposal_ids) != len(set(resolution_proposal_ids)):
            raise EventEvidenceIntegrationToolError("duplicate resolution proposal IDs not allowed")
        unknown = sorted(set(resolution_proposal_ids) - self._resolution_proposal_ids)
        if unknown:
            raise EventEvidenceIntegrationToolError(
                f"resolution proposal IDs are outside the sealed task: {unknown}"
            )
        return EventEvidenceIntegrationToolResult(
            tool="get_resolution_result",
            event_id=self.task.event_id,
            resolution_proposal_ids=sorted(resolution_proposal_ids),
            resolution_records=[
                self._resolution_records[row_id]
                for row_id in sorted(resolution_proposal_ids)
            ],
        )

    def get_context_associations(
        self,
        *,
        association_ids: list[str],
    ) -> EventEvidenceIntegrationToolResult:
        """Read context association IDs bound to the task."""

        if len(association_ids) != len(set(association_ids)):
            raise EventEvidenceIntegrationToolError("duplicate context association IDs not allowed")
        unknown = sorted(set(association_ids) - self._context_association_ids)
        if unknown:
            raise EventEvidenceIntegrationToolError(
                f"context association IDs are outside the sealed task: {unknown}"
            )
        return EventEvidenceIntegrationToolResult(
            tool="get_context_associations",
            event_id=self.task.event_id,
            association_ids=sorted(association_ids),
            context_associations=[
                self._context_associations[row_id]
                for row_id in sorted(association_ids)
            ],
        )

    def get_public_observations(
        self,
        *,
        observation_ids: list[str],
    ) -> EventEvidenceIntegrationToolResult:
        """Read public observation IDs bound to the task."""

        if len(observation_ids) != len(set(observation_ids)):
            raise EventEvidenceIntegrationToolError("duplicate public observation IDs not allowed")
        unknown = sorted(set(observation_ids) - self._public_observation_ids)
        if unknown:
            raise EventEvidenceIntegrationToolError(
                f"public observation IDs are outside the sealed task: {unknown}"
            )
        return EventEvidenceIntegrationToolResult(
            tool="get_public_observations",
            event_id=self.task.event_id,
            observation_ids=sorted(observation_ids),
            public_observations=[
                self._public_observations[row_id]
                for row_id in sorted(observation_ids)
            ],
        )


def build_event_evidence_integration_tools(gateway: EventEvidenceIntegrationToolGateway) -> list[BaseTool]:
    """Expose the single compact, task-scoped candidate bundle to the Agent."""

    @tool("get_candidate_bundle")
    def get_candidate_bundle() -> str:
        """Read compact sealed fact/gap candidates and their source evidence."""
        return gateway.get_candidate_bundle().model_dump_json(
            exclude_defaults=True,
        )

    return [get_candidate_bundle]


def build_event_evidence_integration_task(
    *,
    run_id: str,
    event_id: str,
    core_event_fact_ids: Sequence[str],
    resolution_proposal_ids: Sequence[str],
    available_evidence_layer_ids: Sequence[str],
    required_event_slots: Sequence[str],
    optional_event_slots: Sequence[str],
    missing_slots: Sequence[str] = (),
    schema_profile_id: str,
    schema_context_id: str,
    schema_snapshot_sha256: str,
    selected_evidence_claim_ids: Sequence[str],
    evidence_records: Sequence[EventEvidenceIntegrationEvidenceRecord] = (),
    resolution_records: Sequence[EventEvidenceIntegrationResolutionRecord] = (),
    proposed_facts: Sequence[EventEvidenceFactProposal] = (),
    profile_gaps: Sequence[EventEvidenceProfileGapProposal] = (),
    context_association_ids: Sequence[str] = (),
    context_associations: Sequence[WeatherContextAssociation] = (),
    public_observation_ids: Sequence[str] = (),
    public_observations: Sequence[EventEvidenceIntegrationPublicObservation] = (),
    omitted_slots: Sequence[str] = (),
    validation_feedback: Sequence[EventEvidenceIntegrationFeedback] = (),
    source_snapshot_bindings: Sequence[SourceSnapshotBinding] = (),
    remaining_tool_budget: int = 6,
    binding: ContractExecutionBinding,
) -> EventEvidenceIntegrationTask:
    """Construct and seal one ``EventEvidenceIntegrationTask`` deterministically."""

    sorted_core_facts = tuple(sorted(set(core_event_fact_ids)))
    sorted_resolutions = tuple(sorted(set(resolution_proposal_ids)))
    sorted_layers = tuple(sorted(set(available_evidence_layer_ids)))
    sorted_req = tuple(sorted(set(required_event_slots)))
    sorted_opt = tuple(sorted(set(optional_event_slots)))
    sorted_missing = tuple(sorted(set(missing_slots)))
    sorted_selected_evidence = tuple(sorted(set(selected_evidence_claim_ids)))
    sorted_ctx_assoc = tuple(sorted(set(context_association_ids)))
    sorted_pub_obs = tuple(sorted(set(public_observation_ids)))
    sorted_omitted = tuple(sorted(set(omitted_slots)))

    task_id = stable_contract_id(
        "event-evidence-integration-task",
        run_id,
        event_id,
        canonical_id_tuple_token(sorted_core_facts, sort_values=True),
        canonical_id_tuple_token(sorted_resolutions, sort_values=True),
        canonical_id_tuple_token(sorted_selected_evidence, sort_values=True),
        schema_profile_id,
        schema_context_id,
        schema_snapshot_sha256,
    )

    fields = EventEvidenceIntegrationTaskFields(
        task_id=task_id,
        run_id=run_id,
        event_id=event_id,
        core_event_fact_ids=sorted_core_facts,
        resolution_proposal_ids=sorted_resolutions,
        available_evidence_layer_ids=sorted_layers,
        required_event_slots=sorted_req,
        optional_event_slots=sorted_opt,
        missing_slots=sorted_missing,
        schema_profile_id=schema_profile_id,
        schema_context_id=schema_context_id,
        schema_snapshot_sha256=schema_snapshot_sha256,
        selected_evidence_claim_ids=sorted_selected_evidence,
        evidence_records=tuple(
            sorted(evidence_records, key=lambda row: row.evidence_id)
        ),
        resolution_records=tuple(
            sorted(
                resolution_records,
                key=lambda row: row.resolution_proposal_id,
            )
        ),
        proposed_facts=tuple(proposed_facts),
        profile_gaps=tuple(profile_gaps),
        context_association_ids=sorted_ctx_assoc,
        context_associations=tuple(
            sorted(
                context_associations,
                key=lambda row: row.association_id,
            )
        ),
        public_observation_ids=sorted_pub_obs,
        public_observations=tuple(
            sorted(
                public_observations,
                key=lambda row: row.observation_id,
            )
        ),
        omitted_slots=sorted_omitted,
        validation_feedback=tuple(validation_feedback),
        source_snapshot_bindings=tuple(source_snapshot_bindings),
        remaining_tool_budget=remaining_tool_budget,
    )

    return seal_event_evidence_integration_task(fields=fields, binding=binding)


def compile_event_evidence_integration_proposal(
    *,
    task: EventEvidenceIntegrationTask,
    integration_status: EventEvidenceIntegrationStatus | None = None,
    evidence_layer_results: Sequence[EvidenceLayerResult] = (),
    proposed_facts: Sequence[EventEvidenceFactProposal] | None = None,
    evidence_bindings: Sequence[str] | None = None,
    resolution_proposal_ids: Sequence[str] | None = None,
    context_association_ids: Sequence[str] | None = None,
    profile_gaps: Sequence[EventEvidenceProfileGapProposal] | None = None,
    omitted_slots: Sequence[str] | None = None,
    limitations: Sequence[str] = (),
    tool_trace_ids: Sequence[str] = (),
    source_snapshot_bindings: Sequence[SourceSnapshotBinding] | None = None,
    revision_count: int = 0,
    binding: ContractExecutionBinding,
) -> EventEvidenceIntegrationProposal:
    """Compile and seal one ``EventEvidenceIntegrationProposal`` deterministically."""

    missing_required_slots = set(task.required_event_slots) & set(task.missing_slots)
    if missing_required_slots and integration_status in {
        None,
        EventEvidenceIntegrationStatus.OK,
        EventEvidenceIntegrationStatus.PARTIAL,
    }:
        integration_status = EventEvidenceIntegrationStatus.INSUFFICIENT
    elif integration_status is None:
        integration_status = (
            EventEvidenceIntegrationStatus.PARTIAL if task.missing_slots else EventEvidenceIntegrationStatus.OK
        )

    facts = tuple(task.proposed_facts if proposed_facts is None else proposed_facts)
    gaps = tuple(task.profile_gaps if profile_gaps is None else profile_gaps)
    if not facts and integration_status in {
        EventEvidenceIntegrationStatus.OK,
        EventEvidenceIntegrationStatus.PARTIAL,
    }:
        integration_status = EventEvidenceIntegrationStatus.INSUFFICIENT
    if integration_status in {
        EventEvidenceIntegrationStatus.BLOCKED,
        EventEvidenceIntegrationStatus.INSUFFICIENT,
    }:
        facts = ()
        gaps = ()
        evidence_bindings = ()
        resolution_proposal_ids = ()
        context_association_ids = ()
        source_snapshot_bindings = ()
    ev_bindings = tuple(
        sorted(set(task.selected_evidence_claim_ids if evidence_bindings is None else evidence_bindings))
    )
    res_proposal_ids = tuple(
        sorted(set(task.resolution_proposal_ids if resolution_proposal_ids is None else resolution_proposal_ids))
    )
    ctx_assoc_ids = tuple(
        sorted(set(task.context_association_ids if context_association_ids is None else context_association_ids))
    )
    omitted = tuple(
        sorted(set(task.omitted_slots if omitted_slots is None else omitted_slots))
    )
    src_bindings = tuple(
        task.source_snapshot_bindings if source_snapshot_bindings is None else source_snapshot_bindings
    )

    if not evidence_layer_results:
        layer_status = (
            EvidenceLayerStatus.OK
            if integration_status in (EventEvidenceIntegrationStatus.OK, EventEvidenceIntegrationStatus.PARTIAL)
            else (
                EvidenceLayerStatus.INSUFFICIENT
                if integration_status is EventEvidenceIntegrationStatus.INSUFFICIENT
                else EvidenceLayerStatus.BLOCKED
            )
        )
        evidence_layer_results = (
            EvidenceLayerResult(
                layer_id="core",
                status=layer_status,
                required_for_task=True,
                artifact_ids=task.core_event_fact_ids if layer_status is EvidenceLayerStatus.OK else (),
                missing_reason_code=(
                    "missing_required_event_evidence"
                    if layer_status is EvidenceLayerStatus.INSUFFICIENT
                    else None
                ),
                blocking_error_id=(
                    "core_integration_blocked"
                    if layer_status is EvidenceLayerStatus.BLOCKED
                    else None
                ),
            ),
        )

    fact_item_ids = tuple(item.proposal_item_id for item in facts)
    gap_item_ids = tuple(item.proposal_item_id for item in gaps)

    proposal_id = stable_contract_id(
        "event-evidence-integration-proposal",
        task.task_id,
        task.payload_checksum,
        integration_status.value,
        canonical_id_tuple_token(fact_item_ids, sort_values=True),
        canonical_id_tuple_token(gap_item_ids, sort_values=True),
        canonical_id_tuple_token(res_proposal_ids, sort_values=True),
    )

    fields = EventEvidenceIntegrationProposalFields(
        event_evidence_integration_proposal_id=proposal_id,
        run_id=task.run_id,
        task_id=task.task_id,
        task_payload_checksum=task.payload_checksum,
        event_id=task.event_id,
        integration_status=integration_status,
        evidence_layer_results=tuple(evidence_layer_results),
        proposed_facts=facts,
        evidence_bindings=ev_bindings,
        resolution_proposal_ids=res_proposal_ids,
        context_association_ids=ctx_assoc_ids,
        profile_gaps=gaps,
        omitted_slots=omitted,
        limitations=tuple(sorted(set(limitations))),
        tool_trace_ids=tuple(tool_trace_ids),
        source_snapshot_bindings=src_bindings,
        revision_count=revision_count,
    )

    return seal_event_evidence_integration_proposal(task=task, fields=fields, binding=binding)


def _make_validation_feedback(
    *,
    task: EventEvidenceIntegrationTask,
    proposal: EventEvidenceIntegrationProposal,
    affected_item_id: str,
    violation_code: str,
    constraint_id: str,
    repairable: bool,
    allowed_corrections: Sequence[str],
    evidence_ids: Sequence[str],
    binding: ContractExecutionBinding,
) -> EventEvidenceIntegrationFeedback:
    sorted_corrections = tuple(allowed_corrections)
    sorted_evidence = tuple(sorted(set(evidence_ids)))

    feedback_id = stable_contract_id(
        "validation-feedback",
        task.task_id,
        proposal.payload_checksum,
        affected_item_id,
        violation_code,
        constraint_id,
        canonical_id_tuple_token(sorted_corrections, sort_values=False),
        canonical_id_tuple_token(sorted_evidence, sort_values=True),
    )

    fields = EventEvidenceIntegrationFeedbackFields(
        feedback_id=feedback_id,
        run_id=task.run_id,
        task_id=task.task_id,
        event_id=task.event_id,
        proposal_payload_checksum=proposal.payload_checksum,
        violation_code=violation_code,
        constraint_id=constraint_id,
        affected_proposal_item_id=affected_item_id,
        repairable=repairable,
        allowed_corrections=sorted_corrections,
        evidence_ids=sorted_evidence,
    )

    return seal_event_evidence_integration_feedback(
        task=task,
        proposal=proposal,
        fields=fields,
        binding=binding,
    )


def preflight_validate_event_evidence_proposal(
    *,
    task: EventEvidenceIntegrationTask,
    proposal: EventEvidenceIntegrationProposal,
    binding: ContractExecutionBinding,
) -> EventEvidenceIntegrationFeedback | None:
    """Preflight validate one ``EventEvidenceIntegrationProposal`` against its task."""

    if (
        proposal.run_id != task.run_id
        or proposal.task_id != task.task_id
        or proposal.event_id != task.event_id
    ):
        return _make_validation_feedback(
            task=task,
            proposal=proposal,
            affected_item_id=task.task_id,
            violation_code="TASK_BINDING_MISMATCH",
            constraint_id="constraint:binding",
            repairable=False,
            allowed_corrections=(),
            evidence_ids=(),
            binding=binding,
        )

    if proposal.integration_status not in (EventEvidenceIntegrationStatus.OK, EventEvidenceIntegrationStatus.PARTIAL):
        return None

    def feedback(
        *,
        affected_item_id: str,
        violation_code: str,
        constraint_id: str,
        evidence_ids: Sequence[str] = (),
        repairable: bool = False,
        allowed_corrections: Sequence[str] = (),
    ) -> EventEvidenceIntegrationFeedback:
        return _make_validation_feedback(
            task=task,
            proposal=proposal,
            affected_item_id=affected_item_id,
            violation_code=violation_code,
            constraint_id=constraint_id,
            repairable=repairable,
            allowed_corrections=allowed_corrections,
            evidence_ids=evidence_ids,
            binding=binding,
        )

    task_fact_by_id = {
        item.proposal_item_id: item for item in task.proposed_facts
    }
    proposal_fact_by_id = {
        item.proposal_item_id: item for item in proposal.proposed_facts
    }
    if not proposal_fact_by_id:
        return feedback(
            affected_item_id=task.task_id,
            violation_code="MISSING_REQUIRED_FORMAL_SLOT",
            constraint_id="constraint:required-formal:empty",
        )
    required_fact_ids = set(task.core_event_fact_ids)
    proposal_fact_ids = set(proposal_fact_by_id)
    missing_fact_ids = sorted(required_fact_ids - proposal_fact_ids)
    if missing_fact_ids:
        return feedback(
            affected_item_id=task.task_id,
            violation_code="MISSING_REQUIRED_FORMAL_SLOT",
            constraint_id=f"constraint:required-formal:{missing_fact_ids[0]}",
        )
    extra_fact_ids = sorted(proposal_fact_ids - required_fact_ids)
    if extra_fact_ids:
        extra_id = extra_fact_ids[0]
        return feedback(
            affected_item_id=extra_id,
            violation_code="OUT_OF_TASK_FORMAL_FACT",
            constraint_id=f"constraint:task-fact:{extra_id}",
            evidence_ids=proposal_fact_by_id[extra_id].evidence_claim_ids,
        )

    task_gap_by_id = {
        item.proposal_item_id: item for item in task.profile_gaps
    }
    proposal_gap_by_id = {
        item.proposal_item_id: item for item in proposal.profile_gaps
    }
    missing_gap_ids = sorted(set(task_gap_by_id) - set(proposal_gap_by_id))
    if missing_gap_ids:
        anchor = next(iter(proposal_fact_by_id), task.task_id)
        return feedback(
            affected_item_id=anchor,
            violation_code="MISSING_REQUIRED_PROFILE_GAP",
            constraint_id=f"constraint:required-gap:{missing_gap_ids[0]}",
        )
    extra_gap_ids = sorted(set(proposal_gap_by_id) - set(task_gap_by_id))
    if extra_gap_ids:
        extra_id = extra_gap_ids[0]
        return feedback(
            affected_item_id=extra_id,
            violation_code="OUT_OF_TASK_PROFILE_GAP",
            constraint_id=f"constraint:task-gap:{extra_id}",
            evidence_ids=proposal_gap_by_id[extra_id].evidence_claim_ids,
        )

    anchor = next(iter(proposal_fact_by_id), task.task_id)
    exact_top_level_sets = (
        (
            proposal.evidence_bindings,
            task.selected_evidence_claim_ids,
            "TASK_EVIDENCE_SET_MISMATCH",
            "constraint:task-evidence-set",
        ),
        (
            proposal.resolution_proposal_ids,
            task.resolution_proposal_ids,
            "TASK_RESOLUTION_SET_MISMATCH",
            "constraint:task-resolution-set",
        ),
        (
            proposal.context_association_ids,
            task.context_association_ids,
            "TASK_CONTEXT_SET_MISMATCH",
            "constraint:task-context-set",
        ),
    )
    for actual, expected, code, constraint_id in exact_top_level_sets:
        if actual != expected:
            return feedback(
                affected_item_id=anchor,
                violation_code=code,
                constraint_id=constraint_id,
            )
    if proposal.source_snapshot_bindings != task.source_snapshot_bindings:
        return feedback(
            affected_item_id=anchor,
            violation_code="TASK_SOURCE_BINDING_SET_MISMATCH",
            constraint_id="constraint:task-source-bindings",
        )

    expected_layer_artifacts = {
        "core": (
            task.core_event_fact_ids,
            "OUT_OF_TASK_FORMAL_FACT",
        ),
        "weather": (
            task.context_association_ids,
            "OUT_OF_TASK_CONTEXT_ASSOCIATION",
        ),
        "layer:weather": (
            task.context_association_ids,
            "OUT_OF_TASK_CONTEXT_ASSOCIATION",
        ),
        "bts": (
            task.public_observation_ids,
            "OUT_OF_TASK_PUBLIC_OBSERVATION",
        ),
        "layer:bts": (
            task.public_observation_ids,
            "OUT_OF_TASK_PUBLIC_OBSERVATION",
        ),
    }
    for layer in proposal.evidence_layer_results:
        expected_layer = expected_layer_artifacts.get(layer.layer_id)
        if (
            layer.status is not EvidenceLayerStatus.OK
            or expected_layer is None
        ):
            continue
        expected_artifacts, violation_code = expected_layer
        if layer.artifact_ids != expected_artifacts:
            return feedback(
                affected_item_id=anchor,
                violation_code=violation_code,
                constraint_id=f"constraint:component:{layer.layer_id}",
            )

    evidence_by_id = {
        record.evidence_id: record for record in task.evidence_records
    }
    source_binding_by_id = {
        row.source_id: row for row in task.source_snapshot_bindings
    }

    def reason_support_is_advisory_only(
        evidence_ids: Sequence[str],
    ) -> bool:
        if not evidence_ids:
            return False
        for evidence_id in evidence_ids:
            record = evidence_by_id.get(evidence_id)
            if record is None:
                return False
            source_binding = source_binding_by_id.get(record.source_id)
            if (
                source_binding is None
                or source_binding.source_family
                is not SourceFamily.ATCSCC_ADVISORY
            ):
                return False
        return True

    for fact in proposal.proposed_facts:
        task_fact = task_fact_by_id[fact.proposal_item_id]
        pred_lower = fact.predicate_iri.lower()
        if "caused" in pred_lower or "causal" in pred_lower or "reasonfor" in pred_lower:
            return feedback(
                affected_item_id=fact.proposal_item_id,
                violation_code="FORBIDDEN_CAUSAL_CLAIM",
                constraint_id=f"constraint:no_causal:{fact.proposal_item_id}",
                evidence_ids=fact.evidence_claim_ids,
            )

        if fact.subject_id != task_fact.subject_id:
            return feedback(
                affected_item_id=fact.proposal_item_id,
                violation_code="OUT_OF_TASK_EVENT",
                constraint_id=f"constraint:event:{fact.proposal_item_id}",
                evidence_ids=fact.evidence_claim_ids,
            )
        if fact.validation_profile_id != task.schema_profile_id:
            return feedback(
                affected_item_id=fact.proposal_item_id,
                violation_code="OUT_OF_PROFILE_ASSERTION",
                constraint_id=f"constraint:profile:{fact.proposal_item_id}",
                evidence_ids=fact.evidence_claim_ids,
            )
        if (
            fact.predicate_iri != task_fact.predicate_iri
            or fact.object_kind != task_fact.object_kind
            or (
                task_fact.predicate_iri == "rdf:type"
                and fact.object_value != task_fact.object_value
            )
        ):
            return feedback(
                affected_item_id=fact.proposal_item_id,
                violation_code="OUT_OF_SCHEMA_ASSERTION",
                constraint_id=f"constraint:schema-slice:{fact.proposal_item_id}",
                evidence_ids=fact.evidence_claim_ids,
            )
        if fact.evidence_claim_ids != task_fact.evidence_claim_ids:
            return feedback(
                affected_item_id=fact.proposal_item_id,
                violation_code="OUT_OF_TASK_EVIDENCE",
                constraint_id=f"constraint:evidence:{fact.proposal_item_id}",
                evidence_ids=fact.evidence_claim_ids,
            )
        if fact.derivation_ids != task_fact.derivation_ids:
            return feedback(
                affected_item_id=fact.proposal_item_id,
                violation_code="OUT_OF_TASK_DERIVATION",
                constraint_id=f"constraint:derivation:{fact.proposal_item_id}",
                evidence_ids=fact.evidence_claim_ids,
            )
        if fact.predicate_iri == "atm:impactingCondition" and (
            fact.derivation_ids
            or not reason_support_is_advisory_only(fact.evidence_claim_ids)
        ):
            return feedback(
                affected_item_id=fact.proposal_item_id,
                violation_code="INVALID_DECLARED_REASON_SUPPORT",
                constraint_id=f"constraint:declared-reason:{fact.proposal_item_id}",
                evidence_ids=fact.evidence_claim_ids,
            )
        if fact.object_value != task_fact.object_value:
            if (
                fact.object_value.islower()
                and fact.object_value.upper() == task_fact.object_value
            ):
                return feedback(
                    affected_item_id=fact.proposal_item_id,
                    violation_code="ALLOWED_VALUE_FORMAT_DEFECT",
                    constraint_id=f"constraint:format:{fact.proposal_item_id}",
                    repairable=True,
                    allowed_corrections=(task_fact.object_value,),
                    evidence_ids=fact.evidence_claim_ids,
                )
            return feedback(
                affected_item_id=fact.proposal_item_id,
                violation_code="OUT_OF_TASK_OBJECT_VALUE",
                constraint_id=f"constraint:object-value:{fact.proposal_item_id}",
                evidence_ids=fact.evidence_claim_ids,
            )

    for gap in proposal.profile_gaps:
        task_gap = task_gap_by_id[gap.proposal_item_id]
        if gap.event_id != task_gap.event_id:
            return feedback(
                affected_item_id=gap.proposal_item_id,
                violation_code="OUT_OF_TASK_EVENT",
                constraint_id=f"constraint:gap-event:{gap.proposal_item_id}",
                evidence_ids=gap.evidence_claim_ids,
            )
        if gap.validation_profile_id != task.schema_profile_id:
            return feedback(
                affected_item_id=gap.proposal_item_id,
                violation_code="OUT_OF_PROFILE_ASSERTION",
                constraint_id=f"constraint:gap-profile:{gap.proposal_item_id}",
                evidence_ids=gap.evidence_claim_ids,
            )
        if gap.evidence_claim_ids != task_gap.evidence_claim_ids:
            return feedback(
                affected_item_id=gap.proposal_item_id,
                violation_code="OUT_OF_TASK_EVIDENCE",
                constraint_id=f"constraint:gap-evidence:{gap.proposal_item_id}",
                evidence_ids=gap.evidence_claim_ids,
            )
        if (
            gap.field != task_gap.field
            or gap.normalized_value != task_gap.normalized_value
            or gap.schema_mapping_reason_code
            != task_gap.schema_mapping_reason_code
        ):
            return feedback(
                affected_item_id=gap.proposal_item_id,
                violation_code="OUT_OF_TASK_PROFILE_GAP",
                constraint_id=f"constraint:gap-signature:{gap.proposal_item_id}",
                evidence_ids=gap.evidence_claim_ids,
            )
        if gap.field == "impacting_condition" and not reason_support_is_advisory_only(
            gap.evidence_claim_ids
        ):
            return feedback(
                affected_item_id=gap.proposal_item_id,
                violation_code="INVALID_DECLARED_REASON_SUPPORT",
                constraint_id=f"constraint:declared-reason-gap:{gap.proposal_item_id}",
                evidence_ids=gap.evidence_claim_ids,
            )

    return None
