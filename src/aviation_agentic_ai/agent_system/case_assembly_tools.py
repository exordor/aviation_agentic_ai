"""Typed, task-bounded read-only tools for decision case assembly."""

from __future__ import annotations

from typing import Literal
from langchain_core.tools import BaseTool, tool
from pydantic import Field

from collections.abc import Sequence
from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    AssemblyStatus,
    CaseAssemblyProposal,
    CaseAssemblyProposalFields,
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
    source_snapshot_bindings: list[dict[str, str]] = Field(default_factory=list)
    failure_reason: str = ""


class CaseAssemblyToolGateway:
    """Read-only view of case assembly material scoped to one ``CaseAssemblyTask``."""

    def __init__(self, *, task: CaseAssemblyTask) -> None:
        self.task = task
        self._selected_evidence_claim_ids = set(task.selected_evidence_claim_ids)
        self._resolution_proposal_ids = set(task.resolution_proposal_ids)
        self._context_association_ids = set(task.context_association_ids)
        self._public_observation_ids = set(task.public_observation_ids)

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
        bindings = [
            {
                "source_id": b.source_id,
                "source_family": b.source_family.value,
                "source_snapshot_sha256": b.source_snapshot_sha256,
            }
            for b in self.task.source_snapshot_bindings
        ]
        return CaseAssemblyToolResult(
            tool="get_source_evidence",
            case_id=self.task.case_id,
            requested_evidence_ids=sorted(evidence_ids),
            source_snapshot_bindings=bindings,
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
    proposed_facts: Sequence[CaseFactProposal] = (),
    profile_gaps: Sequence[CaseProfileGapProposal] = (),
    context_association_ids: Sequence[str] = (),
    public_observation_ids: Sequence[str] = (),
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
        proposed_facts=tuple(proposed_facts),
        profile_gaps=tuple(profile_gaps),
        context_association_ids=sorted_ctx_assoc,
        public_observation_ids=sorted_pub_obs,
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

    for fact in proposal.proposed_facts:
        pred_lower = fact.predicate_iri.lower()
        if "caused" in pred_lower or "causal" in pred_lower or "reasonfor" in pred_lower:
            return _make_validation_feedback(
                task=task,
                proposal=proposal,
                affected_item_id=fact.proposal_item_id,
                violation_code="FORBIDDEN_CAUSAL_CLAIM",
                constraint_id=f"constraint:no_causal:{fact.proposal_item_id}",
                repairable=False,
                allowed_corrections=(),
                evidence_ids=fact.evidence_claim_ids,
                binding=binding,
            )

        if fact.validation_profile_id != task.schema_profile_id:
            return _make_validation_feedback(
                task=task,
                proposal=proposal,
                affected_item_id=fact.proposal_item_id,
                violation_code="OUT_OF_PROFILE_ASSERTION",
                constraint_id=f"constraint:profile:{fact.proposal_item_id}",
                repairable=False,
                allowed_corrections=(),
                evidence_ids=fact.evidence_claim_ids,
                binding=binding,
            )

        if fact.object_value.islower() and (
            fact.predicate_iri in ("atm:controlledFacility", "atm:controlled_facility")
            or fact.object_kind == "iri"
        ):
            corrected = fact.object_value.upper()
            return _make_validation_feedback(
                task=task,
                proposal=proposal,
                affected_item_id=fact.proposal_item_id,
                violation_code="ALLOWED_VALUE_FORMAT_DEFECT",
                constraint_id=f"constraint:format:{fact.proposal_item_id}",
                repairable=True,
                allowed_corrections=(corrected,),
                evidence_ids=fact.evidence_claim_ids,
                binding=binding,
            )

    return None
