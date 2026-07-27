"""Typed, task-bounded read-only tools for decision case assembly."""

from __future__ import annotations

from typing import Literal
from langchain_core.tools import BaseTool, tool
from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    CaseAssemblyTask,
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
