"""Tests for bounded Case Assembly tools, preflight validator, and agent loop."""

from __future__ import annotations

from datetime import UTC, datetime
import json
import pytest

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    CaseAssemblyTask,
    CaseAssemblyTaskFields,
    CaseFactProposal,
    CaseProfileGapProposal,
    ContractExecutionBinding,
    SourceSnapshotBinding,
    canonical_id_tuple_token,
    seal_case_assembly_task,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.case_assembly_tools import (
    CaseAssemblyToolError,
    CaseAssemblyToolGateway,
    build_case_assembly_tools,
)

SHA_A = "a" * 64
SHA_B = "b" * 64
STARTED = datetime(2026, 5, 19, 20, 15, tzinfo=UTC)


def _binding(run_id: str = "run-1") -> ContractExecutionBinding:
    return ContractExecutionBinding(
        run_id=run_id,
        created_at=STARTED,
        tool_version="deterministic-assembly-v1",
    )


def _assembly_task(
    *,
    case_id: str = "case-1",
    resolution_proposal_id: str = "res-prop-1",
) -> CaseAssemblyTask:
    fact = CaseFactProposal(
        proposal_item_id="proposal-fact-1",
        subject_id="event-1",
        predicate_iri="rdf:type",
        object_kind="iri",
        object_value="atm:GroundStopTMI",
        evidence_claim_ids=("evidence:event:type",),
        validation_profile_id="profile-1",
    )
    gap = CaseProfileGapProposal(
        proposal_item_id="proposal-gap-1",
        event_id="event-1",
        field="impacting_condition",
        normalized_value="weather",
        evidence_claim_ids=("evidence:event:weather",),
        schema_mapping_reason_code="not_in_profile",
        validation_profile_id="profile-1",
    )
    selected = ("evidence:event:type", "evidence:event:weather")
    task_id = stable_contract_id(
        "case-assembly-task",
        "run-1",
        case_id,
        canonical_id_tuple_token(("fact:event:type",), sort_values=True),
        canonical_id_tuple_token((resolution_proposal_id,), sort_values=True),
        canonical_id_tuple_token(selected, sort_values=True),
        "profile-1",
        "context-1",
        SHA_A,
    )
    fields = CaseAssemblyTaskFields(
        task_id=task_id,
        run_id="run-1",
        case_id=case_id,
        core_event_fact_ids=("fact:event:type",),
        resolution_proposal_ids=(resolution_proposal_id,),
        available_evidence_layer_ids=("layer:advisory", "layer:weather"),
        required_case_slots=("controlled_facility", "event_type"),
        optional_case_slots=("impacting_condition",),
        missing_slots=(),
        schema_profile_id="profile-1",
        schema_context_id="context-1",
        schema_snapshot_sha256=SHA_A,
        selected_evidence_claim_ids=selected,
        proposed_facts=(fact,),
        profile_gaps=(gap,),
        context_association_ids=("assoc-weather-1",),
        public_observation_ids=("obs-bts-1",),
        omitted_slots=(),
        validation_feedback=(),
        source_snapshot_bindings=(
            SourceSnapshotBinding(
                source_id="source:event",
                source_family=SourceFamily.ATCSCC_ADVISORY,
                source_snapshot_sha256=SHA_B,
            ),
        ),
        remaining_tool_budget=6,
    )
    return seal_case_assembly_task(fields=fields, binding=_binding())


def test_case_assembly_gateway_get_case_requirements() -> None:
    task = _assembly_task()
    gateway = CaseAssemblyToolGateway(task=task)
    result = gateway.get_case_requirements()

    assert result.status == "ok"
    assert result.case_id == "case-1"
    assert result.required_case_slots == ["controlled_facility", "event_type"]
    assert result.optional_case_slots == ["impacting_condition"]
    assert result.schema_profile_id == "profile-1"
    assert result.available_evidence_layer_ids == ["layer:advisory", "layer:weather"]
    assert result.remaining_tool_budget == 6


def test_case_assembly_gateway_get_schema_context() -> None:
    task = _assembly_task()
    gateway = CaseAssemblyToolGateway(task=task)
    result = gateway.get_schema_context()

    assert result.status == "ok"
    assert result.schema_profile_id == "profile-1"
    assert result.schema_context_id == "context-1"
    assert result.schema_snapshot_sha256 == SHA_A


def test_case_assembly_gateway_get_source_evidence() -> None:
    task = _assembly_task()
    gateway = CaseAssemblyToolGateway(task=task)
    result = gateway.get_source_evidence(evidence_ids=["evidence:event:type"])

    assert result.status == "ok"
    assert result.requested_evidence_ids == ["evidence:event:type"]
    assert len(result.source_snapshot_bindings) == 1

    # Foreign evidence ID must fail closed
    with pytest.raises(CaseAssemblyToolError):
        gateway.get_source_evidence(evidence_ids=["foreign-evidence"])


def test_case_assembly_gateway_get_resolution_result() -> None:
    task = _assembly_task()
    gateway = CaseAssemblyToolGateway(task=task)
    result = gateway.get_resolution_result(resolution_proposal_ids=["res-prop-1"])

    assert result.status == "ok"
    assert result.resolution_proposal_ids == ["res-prop-1"]

    with pytest.raises(CaseAssemblyToolError):
        gateway.get_resolution_result(resolution_proposal_ids=["unknown-proposal"])


def test_case_assembly_gateway_get_context_associations() -> None:
    task = _assembly_task()
    gateway = CaseAssemblyToolGateway(task=task)
    result = gateway.get_context_associations(association_ids=["assoc-weather-1"])

    assert result.status == "ok"
    assert result.association_ids == ["assoc-weather-1"]

    with pytest.raises(CaseAssemblyToolError):
        gateway.get_context_associations(association_ids=["unknown-assoc"])


def test_case_assembly_gateway_get_public_observations() -> None:
    task = _assembly_task()
    gateway = CaseAssemblyToolGateway(task=task)
    result = gateway.get_public_observations(observation_ids=["obs-bts-1"])

    assert result.status == "ok"
    assert result.observation_ids == ["obs-bts-1"]

    with pytest.raises(CaseAssemblyToolError):
        gateway.get_public_observations(observation_ids=["unknown-obs"])


def test_build_case_assembly_tools_returns_six_tools() -> None:
    task = _assembly_task()
    gateway = CaseAssemblyToolGateway(task=task)
    tools = build_case_assembly_tools(gateway)

    assert len(tools) == 6
    names = [t.name for t in tools]
    expected_names = [
        "get_case_requirements",
        "get_schema_context",
        "get_source_evidence",
        "get_resolution_result",
        "get_context_associations",
        "get_public_observations",
    ]
    assert names == expected_names

    # Test executing a tool
    req_tool = tools[0]
    out = req_tool.invoke({})
    parsed = json.loads(out)
    assert parsed["status"] == "ok"
    assert parsed["case_id"] == "case-1"


def test_deterministic_compiler_compiles_fixed_proposal() -> None:
    from aviation_agentic_ai.agent_system.case_assembly_tools import (
        compile_case_assembly_proposal,
    )

    task = _assembly_task()
    proposal = compile_case_assembly_proposal(
        task=task,
        binding=_binding(),
    )

    assert proposal.case_id == "case-1"
    assert proposal.assembly_status.value == "ok"
    assert proposal.task_payload_checksum == task.payload_checksum
    assert len(proposal.proposed_facts) == 1
    assert len(proposal.profile_gaps) == 1


def test_preflight_validator_repairable_formatting_defect() -> None:
    from aviation_agentic_ai.agent_system.case_assembly_tools import (
        compile_case_assembly_proposal,
        preflight_validate_case_assembly_proposal,
    )

    task = _assembly_task()
    # Fact with repairable formatting issue (e.g. lowercase facility code in object_value requiring uppercase)
    repairable_fact = CaseFactProposal(
        proposal_item_id="proposal-fact-1",
        subject_id="event-1",
        predicate_iri="atm:controlledFacility",
        object_kind="iri",
        object_value="kjfk",
        evidence_claim_ids=("evidence:event:type",),
        validation_profile_id="profile-1",
    )
    proposal = compile_case_assembly_proposal(
        task=task,
        proposed_facts=(repairable_fact,),
        binding=_binding(),
    )
    feedback = preflight_validate_case_assembly_proposal(
        task=task,
        proposal=proposal,
        binding=_binding(),
    )

    assert feedback is not None
    assert feedback.repairable is True
    assert "KJFK" in feedback.allowed_corrections or "https://example.test/facility/KJFK" in feedback.allowed_corrections or len(feedback.allowed_corrections) > 0


def test_preflight_validator_hard_causal_violation() -> None:
    from aviation_agentic_ai.agent_system.case_assembly_tools import (
        compile_case_assembly_proposal,
        preflight_validate_case_assembly_proposal,
    )

    task = _assembly_task()
    # Fact attempting forbidden causal assertion
    forbidden_fact = CaseFactProposal(
        proposal_item_id="proposal-fact-1",
        subject_id="event-1",
        predicate_iri="atm:causedByWeather",
        object_kind="iri",
        object_value="atm:Thunderstorm",
        evidence_claim_ids=("evidence:event:type",),
        validation_profile_id="profile-1",
    )
    proposal = compile_case_assembly_proposal(
        task=task,
        proposed_facts=(forbidden_fact,),
        binding=_binding(),
    )
    feedback = preflight_validate_case_assembly_proposal(
        task=task,
        proposal=proposal,
        binding=_binding(),
    )

    assert feedback is not None
    assert feedback.repairable is False
    assert feedback.allowed_corrections == ()


def test_mutated_bindings_fail_closed() -> None:
    from aviation_agentic_ai.agent_system.case_assembly_tools import (
        compile_case_assembly_proposal,
    )

    task = _assembly_task()
    wrong_binding_source = SourceSnapshotBinding(
        source_id="source:event:mutated",
        source_family=SourceFamily.ATCSCC_ADVISORY,
        source_snapshot_sha256=SHA_B,
    )

    with pytest.raises(ValueError, match="source binding differs"):
        compile_case_assembly_proposal(
            task=task,
            source_snapshot_bindings=(wrong_binding_source,),
            binding=_binding(),
        )


def test_repeated_compilation_produces_identical_ids() -> None:
    from aviation_agentic_ai.agent_system.case_assembly_tools import (
        compile_case_assembly_proposal,
    )

    task = _assembly_task()
    p1 = compile_case_assembly_proposal(task=task, binding=_binding())
    p2 = compile_case_assembly_proposal(task=task, binding=_binding())

    assert p1.case_assembly_proposal_id == p2.case_assembly_proposal_id
    assert p1.payload_checksum == p2.payload_checksum

