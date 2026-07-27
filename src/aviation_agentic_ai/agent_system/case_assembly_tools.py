"""Typed, task-bounded read-only tools for decision case assembly."""

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
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    AssemblyStatus,
    CaseAssemblyEvidenceRecord,
    CaseAssemblyProposal,
    CaseAssemblyProposalFields,
    CaseAssemblyPublicObservation,
    CaseAssemblyResolutionRecord,
    CaseAssemblyTask,
    CaseAssemblyTaskFields,
    CaseFactProposal,
    CaseProfileGapProposal,
    ComponentLayerResult,
    ComponentLayerStatus,
    ContractExecutionBinding,
    SourceSnapshotBinding,
    ValidationFeedback,
    ValidationFeedbackFields,
    canonical_id_tuple_token,
    seal_case_assembly_proposal,
    seal_case_assembly_task,
    seal_validation_feedback,
    stable_contract_id,
)


class CaseAssemblyToolError(RuntimeError):
    """Raised when a case assembly tool request escapes its sealed task."""


class GetEvidenceInput(StrictModel):
    """Selected evidence IDs from the current sealed case assembly task."""

    evidence_ids: list[str] = Field(min_length=1, max_length=10)


class GetResolutionResultInput(StrictModel):
    """Resolution proposal IDs from the current sealed case assembly task."""

    resolution_proposal_ids: list[str] = Field(min_length=1, max_length=5)


class GetContextAssociationsInput(StrictModel):
    """Context association IDs from the current sealed case assembly task."""

    association_ids: list[str] = Field(min_length=1, max_length=10)


class GetPublicObservationsInput(StrictModel):
    """Public observation IDs from the current sealed case assembly task."""

    observation_ids: list[str] = Field(min_length=1, max_length=10)


class CaseAssemblyToolResult(StrictModel):
    """One deterministic, JSON-serializable case-assembly tool observation."""

    tool: Literal[
        "get_case_requirements",
        "get_schema_context",
        "get_source_evidence",
        "get_resolution_result",
        "get_context_associations",
        "get_public_observations",
    ]
    status: Literal["ok", "insufficient", "blocked"] = "ok"
    case_id: str = ""
    required_case_slots: list[str] = Field(default_factory=list)
    optional_case_slots: list[str] = Field(default_factory=list)
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
    evidence_records: list[CaseAssemblyEvidenceRecord] = Field(default_factory=list)
    resolution_records: list[CaseAssemblyResolutionRecord] = Field(
        default_factory=list
    )
    context_associations: list[WeatherContextAssociation] = Field(
        default_factory=list
    )
    public_observations: list[CaseAssemblyPublicObservation] = Field(
        default_factory=list
    )
    source_snapshot_bindings: list[SourceSnapshotBinding] = Field(
        default_factory=list
    )
    failure_reason: str = ""


class CaseAssemblyToolGateway:
    """Read-only view of case assembly material scoped to one ``CaseAssemblyTask``."""

    def __init__(self, *, task: CaseAssemblyTask) -> None:
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

    def get_case_requirements(self) -> CaseAssemblyToolResult:
        """Read required, optional, and missing case slots and available evidence layers."""

        return CaseAssemblyToolResult(
            tool="get_case_requirements",
            case_id=self.task.case_id,
            required_case_slots=list(self.task.required_case_slots),
            optional_case_slots=list(self.task.optional_case_slots),
            missing_slots=list(self.task.missing_slots),
            schema_profile_id=self.task.schema_profile_id,
            available_evidence_layer_ids=list(self.task.available_evidence_layer_ids),
            remaining_tool_budget=self.task.remaining_tool_budget,
        )

    def get_schema_context(self) -> CaseAssemblyToolResult:
        """Read schema profile, context ID, and snapshot SHA for the task."""

        return CaseAssemblyToolResult(
            tool="get_schema_context",
            case_id=self.task.case_id,
            schema_profile_id=self.task.schema_profile_id,
            schema_context_id=self.task.schema_context_id,
            schema_snapshot_sha256=self.task.schema_snapshot_sha256,
        )

    def get_source_evidence(
        self,
        *,
        evidence_ids: list[str],
    ) -> CaseAssemblyToolResult:
        """Read task-bound source evidence claims and snapshot bindings."""

        if len(evidence_ids) != len(set(evidence_ids)):
            raise CaseAssemblyToolError("duplicate evidence IDs are not allowed")
        unknown = sorted(set(evidence_ids) - self._selected_evidence_claim_ids)
        if unknown:
            raise CaseAssemblyToolError(
                f"evidence IDs are outside the sealed task: {unknown}"
            )
        records = [self._evidence_records[row_id] for row_id in sorted(evidence_ids)]
        return CaseAssemblyToolResult(
            tool="get_source_evidence",
            case_id=self.task.case_id,
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
    ) -> CaseAssemblyToolResult:
        """Read resolution proposals bound to the task."""

        if len(resolution_proposal_ids) != len(set(resolution_proposal_ids)):
            raise CaseAssemblyToolError("duplicate resolution proposal IDs not allowed")
        unknown = sorted(set(resolution_proposal_ids) - self._resolution_proposal_ids)
        if unknown:
            raise CaseAssemblyToolError(
                f"resolution proposal IDs are outside the sealed task: {unknown}"
            )
        return CaseAssemblyToolResult(
            tool="get_resolution_result",
            case_id=self.task.case_id,
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
    ) -> CaseAssemblyToolResult:
        """Read context association IDs bound to the task."""

        if len(association_ids) != len(set(association_ids)):
            raise CaseAssemblyToolError("duplicate context association IDs not allowed")
        unknown = sorted(set(association_ids) - self._context_association_ids)
        if unknown:
            raise CaseAssemblyToolError(
                f"context association IDs are outside the sealed task: {unknown}"
            )
        return CaseAssemblyToolResult(
            tool="get_context_associations",
            case_id=self.task.case_id,
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
    ) -> CaseAssemblyToolResult:
        """Read public observation IDs bound to the task."""

        if len(observation_ids) != len(set(observation_ids)):
            raise CaseAssemblyToolError("duplicate public observation IDs not allowed")
        unknown = sorted(set(observation_ids) - self._public_observation_ids)
        if unknown:
            raise CaseAssemblyToolError(
                f"public observation IDs are outside the sealed task: {unknown}"
            )
        return CaseAssemblyToolResult(
            tool="get_public_observations",
            case_id=self.task.case_id,
            observation_ids=sorted(observation_ids),
            public_observations=[
                self._public_observations[row_id]
                for row_id in sorted(observation_ids)
            ],
        )


def build_case_assembly_tools(gateway: CaseAssemblyToolGateway) -> list[BaseTool]:
    """Build the six model-visible read-only tools for one case assembly task."""

    @tool("get_case_requirements")
    def get_case_requirements() -> str:
        """Read case slot requirements and available evidence layers."""
        return gateway.get_case_requirements().model_dump_json()

    @tool("get_schema_context")
    def get_schema_context() -> str:
        """Read schema profile, context ID, and snapshot SHA for the task."""
        return gateway.get_schema_context().model_dump_json()

    @tool("get_source_evidence", args_schema=GetEvidenceInput)
    def get_source_evidence(evidence_ids: list[str]) -> str:
        """Read task-owned source evidence claims and snapshot bindings."""
        return gateway.get_source_evidence(evidence_ids=evidence_ids).model_dump_json()

    @tool("get_resolution_result", args_schema=GetResolutionResultInput)
    def get_resolution_result(resolution_proposal_ids: list[str]) -> str:
        """Read resolution proposals bound to the task."""
        return gateway.get_resolution_result(
            resolution_proposal_ids=resolution_proposal_ids
        ).model_dump_json()

    @tool("get_context_associations", args_schema=GetContextAssociationsInput)
    def get_context_associations(association_ids: list[str]) -> str:
        """Read context association IDs bound to the task."""
        return gateway.get_context_associations(
            association_ids=association_ids
        ).model_dump_json()

    @tool("get_public_observations", args_schema=GetPublicObservationsInput)
    def get_public_observations(observation_ids: list[str]) -> str:
        """Read public observation IDs bound to the task."""
        return gateway.get_public_observations(
            observation_ids=observation_ids
        ).model_dump_json()

    return [
        get_case_requirements,
        get_schema_context,
        get_source_evidence,
        get_resolution_result,
        get_context_associations,
        get_public_observations,
    ]


def build_case_assembly_task(
    *,
    run_id: str,
    case_id: str,
    core_event_fact_ids: Sequence[str],
    resolution_proposal_ids: Sequence[str],
    available_evidence_layer_ids: Sequence[str],
    required_case_slots: Sequence[str],
    optional_case_slots: Sequence[str],
    missing_slots: Sequence[str] = (),
    schema_profile_id: str,
    schema_context_id: str,
    schema_snapshot_sha256: str,
    selected_evidence_claim_ids: Sequence[str],
    evidence_records: Sequence[CaseAssemblyEvidenceRecord] = (),
    resolution_records: Sequence[CaseAssemblyResolutionRecord] = (),
    proposed_facts: Sequence[CaseFactProposal] = (),
    profile_gaps: Sequence[CaseProfileGapProposal] = (),
    context_association_ids: Sequence[str] = (),
    context_associations: Sequence[WeatherContextAssociation] = (),
    public_observation_ids: Sequence[str] = (),
    public_observations: Sequence[CaseAssemblyPublicObservation] = (),
    omitted_slots: Sequence[str] = (),
    validation_feedback: Sequence[ValidationFeedback] = (),
    source_snapshot_bindings: Sequence[SourceSnapshotBinding] = (),
    remaining_tool_budget: int = 6,
    binding: ContractExecutionBinding,
) -> CaseAssemblyTask:
    """Construct and seal one ``CaseAssemblyTask`` deterministically."""

    sorted_core_facts = tuple(sorted(set(core_event_fact_ids)))
    sorted_resolutions = tuple(sorted(set(resolution_proposal_ids)))
    sorted_layers = tuple(sorted(set(available_evidence_layer_ids)))
    sorted_req = tuple(sorted(set(required_case_slots)))
    sorted_opt = tuple(sorted(set(optional_case_slots)))
    sorted_missing = tuple(sorted(set(missing_slots)))
    sorted_selected_evidence = tuple(sorted(set(selected_evidence_claim_ids)))
    sorted_ctx_assoc = tuple(sorted(set(context_association_ids)))
    sorted_pub_obs = tuple(sorted(set(public_observation_ids)))
    sorted_omitted = tuple(sorted(set(omitted_slots)))

    task_id = stable_contract_id(
        "case-assembly-task",
        run_id,
        case_id,
        canonical_id_tuple_token(sorted_core_facts, sort_values=True),
        canonical_id_tuple_token(sorted_resolutions, sort_values=True),
        canonical_id_tuple_token(sorted_selected_evidence, sort_values=True),
        schema_profile_id,
        schema_context_id,
        schema_snapshot_sha256,
    )

    fields = CaseAssemblyTaskFields(
        task_id=task_id,
        run_id=run_id,
        case_id=case_id,
        core_event_fact_ids=sorted_core_facts,
        resolution_proposal_ids=sorted_resolutions,
        available_evidence_layer_ids=sorted_layers,
        required_case_slots=sorted_req,
        optional_case_slots=sorted_opt,
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

    return seal_case_assembly_task(fields=fields, binding=binding)


def compile_case_assembly_proposal(
    *,
    task: CaseAssemblyTask,
    assembly_status: AssemblyStatus | None = None,
    component_layer_results: Sequence[ComponentLayerResult] = (),
    proposed_facts: Sequence[CaseFactProposal] | None = None,
    evidence_bindings: Sequence[str] | None = None,
    resolution_proposal_ids: Sequence[str] | None = None,
    context_association_ids: Sequence[str] | None = None,
    profile_gaps: Sequence[CaseProfileGapProposal] | None = None,
    omitted_slots: Sequence[str] | None = None,
    limitations: Sequence[str] = (),
    tool_trace_ids: Sequence[str] = (),
    source_snapshot_bindings: Sequence[SourceSnapshotBinding] | None = None,
    revision_count: int = 0,
    binding: ContractExecutionBinding,
) -> CaseAssemblyProposal:
    """Compile and seal one ``CaseAssemblyProposal`` deterministically."""

    missing_required_slots = set(task.required_case_slots) & set(task.missing_slots)
    if missing_required_slots and assembly_status in {
        None,
        AssemblyStatus.OK,
        AssemblyStatus.PARTIAL,
    }:
        assembly_status = AssemblyStatus.INSUFFICIENT
    elif assembly_status is None:
        assembly_status = (
            AssemblyStatus.PARTIAL if task.missing_slots else AssemblyStatus.OK
        )

    facts = tuple(task.proposed_facts if proposed_facts is None else proposed_facts)
    gaps = tuple(task.profile_gaps if profile_gaps is None else profile_gaps)
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

    if not component_layer_results:
        layer_status = (
            ComponentLayerStatus.OK
            if assembly_status in (AssemblyStatus.OK, AssemblyStatus.PARTIAL)
            else (
                ComponentLayerStatus.INSUFFICIENT
                if assembly_status is AssemblyStatus.INSUFFICIENT
                else ComponentLayerStatus.BLOCKED
            )
        )
        component_layer_results = (
            ComponentLayerResult(
                layer_id="core",
                status=layer_status,
                required_for_task=True,
                artifact_ids=task.core_event_fact_ids if layer_status is ComponentLayerStatus.OK else (),
                missing_reason_code=(
                    "missing_required_case_evidence"
                    if layer_status is ComponentLayerStatus.INSUFFICIENT
                    else None
                ),
                blocking_error_id=(
                    "core_assembly_blocked"
                    if layer_status is ComponentLayerStatus.BLOCKED
                    else None
                ),
            ),
        )

    fact_item_ids = tuple(item.proposal_item_id for item in facts)
    gap_item_ids = tuple(item.proposal_item_id for item in gaps)

    proposal_id = stable_contract_id(
        "case-assembly-proposal",
        task.task_id,
        task.payload_checksum,
        assembly_status.value,
        canonical_id_tuple_token(fact_item_ids, sort_values=True),
        canonical_id_tuple_token(gap_item_ids, sort_values=True),
        canonical_id_tuple_token(res_proposal_ids, sort_values=True),
    )

    fields = CaseAssemblyProposalFields(
        case_assembly_proposal_id=proposal_id,
        run_id=task.run_id,
        task_id=task.task_id,
        task_payload_checksum=task.payload_checksum,
        case_id=task.case_id,
        assembly_status=assembly_status,
        component_layer_results=tuple(component_layer_results),
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

    return seal_case_assembly_proposal(task=task, fields=fields, binding=binding)


def _make_validation_feedback(
    *,
    task: CaseAssemblyTask,
    proposal: CaseAssemblyProposal,
    affected_item_id: str,
    violation_code: str,
    constraint_id: str,
    repairable: bool,
    allowed_corrections: Sequence[str],
    evidence_ids: Sequence[str],
    binding: ContractExecutionBinding,
) -> ValidationFeedback:
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

    fields = ValidationFeedbackFields(
        feedback_id=feedback_id,
        run_id=task.run_id,
        task_id=task.task_id,
        case_id=task.case_id,
        proposal_payload_checksum=proposal.payload_checksum,
        violation_code=violation_code,
        constraint_id=constraint_id,
        affected_proposal_item_id=affected_item_id,
        repairable=repairable,
        allowed_corrections=sorted_corrections,
        evidence_ids=sorted_evidence,
    )

    return seal_validation_feedback(
        task=task,
        proposal=proposal,
        fields=fields,
        binding=binding,
    )


def preflight_validate_case_assembly_proposal(
    *,
    task: CaseAssemblyTask,
    proposal: CaseAssemblyProposal,
    binding: ContractExecutionBinding,
) -> ValidationFeedback | None:
    """Preflight validate one ``CaseAssemblyProposal`` against its task."""

    if (
        proposal.run_id != task.run_id
        or proposal.task_id != task.task_id
        or proposal.case_id != task.case_id
    ):
        first_item = proposal.proposed_facts[0].proposal_item_id if proposal.proposed_facts else "task"
        return _make_validation_feedback(
            task=task,
            proposal=proposal,
            affected_item_id=first_item,
            violation_code="TASK_BINDING_MISMATCH",
            constraint_id="constraint:binding",
            repairable=False,
            allowed_corrections=(),
            evidence_ids=proposal.evidence_bindings,
            binding=binding,
        )

    if proposal.assembly_status not in (AssemblyStatus.OK, AssemblyStatus.PARTIAL):
        return None

    def feedback(
        *,
        affected_item_id: str,
        violation_code: str,
        constraint_id: str,
        evidence_ids: Sequence[str] = (),
        repairable: bool = False,
        allowed_corrections: Sequence[str] = (),
    ) -> ValidationFeedback:
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
    for layer in proposal.component_layer_results:
        expected_layer = expected_layer_artifacts.get(layer.layer_id)
        if (
            layer.status is not ComponentLayerStatus.OK
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

        if fact.object_value.islower() and (
            fact.predicate_iri in ("atm:controlledFacility", "atm:controlled_facility")
            or fact.object_kind == "iri"
        ):
            corrected = fact.object_value.upper()
            return feedback(
                affected_item_id=fact.proposal_item_id,
                violation_code="ALLOWED_VALUE_FORMAT_DEFECT",
                constraint_id=f"constraint:format:{fact.proposal_item_id}",
                repairable=True,
                allowed_corrections=(corrected,),
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
