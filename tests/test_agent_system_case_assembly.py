"""Tests for bounded Case Assembly tools, preflight validator, and agent loop."""

from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
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


class _ScriptedAssemblyModel:
    def __init__(self, turns: list) -> None:
        self.turns = list(turns)

    def invoke(self, messages: list, *, phase: str):
        return self.turns.pop(0)


def _assembly_tool_turn():
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord, ModelToolCall
    from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
    from langchain_core.messages import AIMessage

    calls = [
        {
            "id": "call:ev-1",
            "name": "get_source_evidence",
            "args": {"evidence_ids": ["evidence:event:type"]},
            "type": "tool_call",
        }
    ]
    return ToolModelTurn(
        message=AIMessage(content="", tool_calls=calls),
        record=ModelCallRecord(
            agent="decision_case_assembly",
            raw_response="",
            prompt_version="decision-case-assembly-v1",
            tool_calls=[
                ModelToolCall(
                    call_id="call:ev-1",
                    name="get_source_evidence",
                    arguments={"evidence_ids": ["evidence:event:type"]},
                )
            ],
        ),
    )


def _valid_proposal_text() -> str:
    return (
        'GRAPH_PATCH\n'
        '{"proposal_item_id":"proposal-fact-1","subject_id":"event-1","predicate_iri":"rdf:type","object_kind":"iri","object_value":"atm:GroundStopTMI","evidence_claim_ids":["evidence:event:type"],"derivation_ids":[],"validation_profile_id":"profile-1"}\n\n'
        'PROFILE_GAPS\n'
        '{"proposal_item_id":"proposal-gap-1","event_id":"event-1","field":"impacting_condition","normalized_value":"weather","evidence_claim_ids":["evidence:event:weather"],"schema_mapping_reason_code":"not_in_profile","validation_profile_id":"profile-1"}\n'
    )


def test_case_assembly_agent_evidence_schema_choice_success() -> None:
    from aviation_agentic_ai.agent_system.case_assembly import run_case_assembly_agent
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
    from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
    from langchain_core.messages import AIMessage

    task = _assembly_task()
    turn_1 = _assembly_tool_turn()
    turn_2 = ToolModelTurn(
        message=AIMessage(content=_valid_proposal_text()),
        record=ModelCallRecord(
            agent="decision_case_assembly",
            raw_response=_valid_proposal_text(),
            prompt_version="decision-case-assembly-v1",
        ),
    )
    scripted_model = _ScriptedAssemblyModel([turn_1, turn_2])

    result = run_case_assembly_agent(
        task=task,
        binding=_binding(),
        tool_model_factory=lambda tools: scripted_model,
    )

    assert result.proposal.assembly_status.value == "ok"
    assert len(result.model_calls) == 2
    assert len(result.tool_traces) == 1
    assert result.feedback is None
    assert result.failure_reason is None


def test_case_assembly_agent_one_allowed_revision_success() -> None:
    from aviation_agentic_ai.agent_system.case_assembly import run_case_assembly_agent
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
    from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
    from langchain_core.messages import AIMessage

    task = _assembly_task()
    turn_1 = _assembly_tool_turn()

    # Repairable formatting defect: lowercase 'kjfk' for facility
    repairable_text = (
        'GRAPH_PATCH\n'
        '{"proposal_item_id":"proposal-fact-1","subject_id":"event-1","predicate_iri":"atm:controlledFacility","object_kind":"iri","object_value":"kjfk","evidence_claim_ids":["evidence:event:type"],"derivation_ids":[],"validation_profile_id":"profile-1"}\n\n'
        'PROFILE_GAPS\nNONE\n'
    )
    turn_2 = ToolModelTurn(
        message=AIMessage(content=repairable_text),
        record=ModelCallRecord(
            agent="decision_case_assembly",
            raw_response=repairable_text,
            prompt_version="decision-case-assembly-v1",
        ),
    )

    # Turn 3 applies allowed correction 'KJFK'
    corrected_text = (
        'GRAPH_PATCH\n'
        '{"proposal_item_id":"proposal-fact-1","subject_id":"event-1","predicate_iri":"atm:controlledFacility","object_kind":"iri","object_value":"KJFK","evidence_claim_ids":["evidence:event:type"],"derivation_ids":[],"validation_profile_id":"profile-1"}\n\n'
        'PROFILE_GAPS\nNONE\n'
    )
    turn_3 = ToolModelTurn(
        message=AIMessage(content=corrected_text),
        record=ModelCallRecord(
            agent="decision_case_assembly",
            raw_response=corrected_text,
            prompt_version="decision-case-assembly-v1",
        ),
    )

    scripted_model = _ScriptedAssemblyModel([turn_1, turn_2, turn_3])

    result = run_case_assembly_agent(
        task=task,
        binding=_binding(),
        tool_model_factory=lambda tools: scripted_model,
    )

    assert result.proposal.assembly_status.value == "ok"
    assert result.proposal.revision_count == 1
    assert len(result.model_calls) == 3
    assert result.feedback is None


def test_case_assembly_agent_hard_semantic_violation_blocks() -> None:
    from aviation_agentic_ai.agent_system.case_assembly import run_case_assembly_agent
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
    from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
    from langchain_core.messages import AIMessage

    task = _assembly_task()
    turn_1 = _assembly_tool_turn()

    # Forbidden causal claim
    forbidden_text = (
        'GRAPH_PATCH\n'
        '{"proposal_item_id":"proposal-fact-1","subject_id":"event-1","predicate_iri":"atm:causedByWeather","object_kind":"iri","object_value":"atm:Thunderstorm","evidence_claim_ids":["evidence:event:type"],"derivation_ids":[],"validation_profile_id":"profile-1"}\n\n'
        'PROFILE_GAPS\nNONE\n'
    )
    turn_2 = ToolModelTurn(
        message=AIMessage(content=forbidden_text),
        record=ModelCallRecord(
            agent="decision_case_assembly",
            raw_response=forbidden_text,
            prompt_version="decision-case-assembly-v1",
        ),
    )

    scripted_model = _ScriptedAssemblyModel([turn_1, turn_2])

    result = run_case_assembly_agent(
        task=task,
        binding=_binding(),
        tool_model_factory=lambda tools: scripted_model,
    )

    assert result.proposal.assembly_status.value == "blocked"
    assert len(result.model_calls) == 2  # No turn 3 attempted!
    assert result.feedback is not None
    assert result.feedback.repairable is False


def test_case_assembly_agent_malformed_output_blocks_without_repair() -> None:
    from aviation_agentic_ai.agent_system.case_assembly import run_case_assembly_agent
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
    from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
    from langchain_core.messages import AIMessage

    task = _assembly_task()
    turn_1 = _assembly_tool_turn()
    turn_2 = ToolModelTurn(
        message=AIMessage(content="GRAPH_PATCH\nnot a json line\n"),
        record=ModelCallRecord(
            agent="decision_case_assembly",
            raw_response="GRAPH_PATCH\nnot a json line\n",
            prompt_version="decision-case-assembly-v1",
        ),
    )

    scripted_model = _ScriptedAssemblyModel([turn_1, turn_2])

    result = run_case_assembly_agent(
        task=task,
        binding=_binding(),
        tool_model_factory=lambda tools: scripted_model,
    )

    assert result.proposal.assembly_status.value == "blocked"
    assert len(result.model_calls) == 2


def test_case_assembly_agent_replay_stability() -> None:
    from aviation_agentic_ai.agent_system.case_assembly import run_case_assembly_agent
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
    from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
    from langchain_core.messages import AIMessage

    task = _assembly_task()

    def _make_model():
        turn_1 = _assembly_tool_turn()
        turn_2 = ToolModelTurn(
            message=AIMessage(content=_valid_proposal_text()),
            record=ModelCallRecord(
                agent="decision_case_assembly",
                raw_response=_valid_proposal_text(),
                prompt_version="decision-case-assembly-v1",
            ),
        )
        return _ScriptedAssemblyModel([turn_1, turn_2])

    res1 = run_case_assembly_agent(task=task, binding=_binding(), tool_model_factory=lambda tools: _make_model())
    res2 = run_case_assembly_agent(task=task, binding=_binding(), tool_model_factory=lambda tools: _make_model())

    assert res1.proposal.case_assembly_proposal_id == res2.proposal.case_assembly_proposal_id
    assert res1.proposal.payload_checksum == res2.proposal.payload_checksum


def test_workflow_three_cases_decision_case_assembly_regression(tmp_path: Path) -> None:
    from aviation_agentic_ai.agent_system.sources import load_advisory_source
    from aviation_agentic_ai.agent_system.workflow import IngestContext, run_ingest
    from aviation_agentic_ai.cross_source.contracts import CanonicalEntity, CodeValue, EntityType
    from test_agent_system_authority_evidence import _catalog, _test_inputs

    config, _ = _test_inputs(tmp_path)
    catalog = _catalog(tmp_path)
    facilities = {
        "KJFK": CanonicalEntity(
            entity_id="urn:aviation-agentic-ai:facility:airport:KJFK",
            entity_type=EntityType.AIRPORT,
            preferred_label="John F Kennedy International Airport",
            codes=[CodeValue(scheme="IATA", value="JFK"), CodeValue(scheme="ICAO", value="KJFK")],
        ),
        "KEWR": CanonicalEntity(
            entity_id="urn:aviation-agentic-ai:facility:airport:KEWR",
            entity_type=EntityType.AIRPORT,
            preferred_label="Newark Liberty International Airport",
            codes=[CodeValue(scheme="IATA", value="EWR"), CodeValue(scheme="ICAO", value="KEWR")],
        ),
    }

    test_cases = [
        ("2026-05-19:123", "KJFK", "GroundStopTMI", True),
        ("2026-05-19:138", "KJFK", "GroundDelayProgramTMI", False),
        ("2026-05-20:020", "KEWR", "GroundDelayProgramTMI", False),
    ]

    now = datetime.now(UTC)
    for source_id, fac_code, expected_class, is_gs in test_cases:
        advisory = load_advisory_source(config, source_id)
        out_dir = tmp_path / source_id.replace(":", "_")
        ctx = IngestContext(
            advisory=advisory,
            facility_candidates=[facilities[fac_code]],
            authority_catalog=catalog,
            run_id=f"run:{source_id}",
            run_started_at=now,
            output_dir=str(out_dir),
        )

        state = run_ingest(ctx)

        # 1. Zero Assembly model calls
        assert len(state["model_calls"]) == 0

        # 2. CaseAssemblyTask & Proposal state present
        task = state.get("case_assembly_task")
        proposal = state.get("case_assembly_proposal")
        assert task is not None
        assert proposal is not None
        assert proposal.assembly_status.value == "ok"

        # 3. Canonical facility verification
        fac_facts = [f for f in proposal.proposed_facts if f.predicate_iri == "atm:controlledNASelement"]
        assert len(fac_facts) == 1
        assert fac_facts[0].object_value == facilities[fac_code].entity_id

        # 4. Reason / Profile Gap verification
        if is_gs:
            # Ground Stop has impacting_condition as profile gap
            assert len(proposal.profile_gaps) == 1
            assert proposal.profile_gaps[0].field == "impacting_condition"
            assert proposal.profile_gaps[0].normalized_value == "weather"
            reason_facts = [f for f in proposal.proposed_facts if f.predicate_iri == "atm:impactingCondition"]
            assert len(reason_facts) == 0
        elif source_id == "2026-05-19:138":
            # GDP has impacting_condition as formal fact
            reason_facts = [f for f in proposal.proposed_facts if f.predicate_iri == "atm:impactingCondition"]
            assert len(reason_facts) == 1
            assert reason_facts[0].object_value == "weather"
            assert len(proposal.profile_gaps) == 0
        elif source_id == "2026-05-20:020":
            # GDP cancellation has missing impacting_condition
            reason_facts = [f for f in proposal.proposed_facts if f.predicate_iri == "atm:impactingCondition"]
            assert len(reason_facts) == 0
            assert "impacting_condition" in task.missing_slots


def test_workflow_canonical_node_identity_and_idempotency(tmp_path: Path) -> None:
    from aviation_agentic_ai.agent_system.sources import load_advisory_source
    from aviation_agentic_ai.agent_system.workflow import IngestContext, run_ingest
    from aviation_agentic_ai.cross_source.contracts import CanonicalEntity, CodeValue, EntityType
    from test_agent_system_authority_evidence import _catalog, _test_inputs

    config, _ = _test_inputs(tmp_path)
    catalog = _catalog(tmp_path)
    fac_jfk = CanonicalEntity(
        entity_id="urn:aviation-agentic-ai:facility:airport:KJFK",
        entity_type=EntityType.AIRPORT,
        preferred_label="John F Kennedy International Airport",
        codes=[CodeValue(scheme="IATA", value="JFK"), CodeValue(scheme="ICAO", value="KJFK")],
    )

    adv123 = load_advisory_source(config, "2026-05-19:123")
    adv138 = load_advisory_source(config, "2026-05-19:138")

    now = datetime.now(UTC)
    ctx1 = IngestContext(advisory=adv123, facility_candidates=[fac_jfk], authority_catalog=catalog, run_id="run:123", run_started_at=now, output_dir=str(tmp_path / "run123"))
    ctx2 = IngestContext(advisory=adv138, facility_candidates=[fac_jfk], authority_catalog=catalog, run_id="run:138", run_started_at=now, output_dir=str(tmp_path / "run138"))

    state1 = run_ingest(ctx1)
    state2 = run_ingest(ctx2)

    prop1 = state1["case_assembly_proposal"]
    prop2 = state2["case_assembly_proposal"]

    # Both KJFK records use the exact same canonical facility node ID
    fac1 = [f for f in prop1.proposed_facts if f.predicate_iri == "atm:controlledNASelement"][0]
    fac2 = [f for f in prop2.proposed_facts if f.predicate_iri == "atm:controlledNASelement"][0]
    assert fac1.object_value == fac2.object_value == "urn:aviation-agentic-ai:facility:airport:KJFK"

    # Idempotency check: run state1 again with identical inputs
    state1_repeat = run_ingest(ctx1)
    prop1_repeat = state1_repeat["case_assembly_proposal"]
    assert prop1.case_assembly_proposal_id == prop1_repeat.case_assembly_proposal_id
    assert prop1.payload_checksum == prop1_repeat.payload_checksum



