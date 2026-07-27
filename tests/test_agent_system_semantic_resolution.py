"""Candidate-bounded read-only tools for semantic resolution."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

import pytest
from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool

from aviation_agentic_ai.agent_system.decision_case_contracts import (
    AuthorityRecordEvidenceClaim,
    CandidateBuildStatus,
    ConstraintCheck,
    ConstraintCheckStatus,
    ContractExecutionBinding,
    RawResolutionCandidateRef,
    ResolutionCandidate,
    ResolutionCandidateAudit,
    ResolutionTaskFields,
    canonical_id_tuple_token,
    canonicalize_contract_value,
    seal_resolution_task,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.resolution_tools import (
    ResolutionToolError,
    ResolutionToolGateway,
    build_resolution_tools,
)
from aviation_agentic_ai.agent_system.tool_model import ToolCallingModel, ToolModelTurn


SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
NOW = datetime(2026, 7, 27, 12, 0, tzinfo=UTC)


def _authority_claim(candidate_id: str) -> AuthorityRecordEvidenceClaim:
    source_id = stable_contract_id(
        "authority-source",
        "facility",
        candidate_id,
        f"NASR:APT:{candidate_id.rsplit(':', maxsplit=1)[-1]}",
        SHA_B,
    )
    evidence_id = stable_contract_id(
        "authority-evidence",
        candidate_id,
        source_id,
        SHA_B,
        SHA_C,
    )
    return AuthorityRecordEvidenceClaim(
        evidence_id=evidence_id,
        candidate_id=candidate_id,
        evidence_kind="facility_record",
        authority_record_text=f"{candidate_id} authority record",
        authority_record_locator=f"APT.txt:{candidate_id}",
        authority_record_sha256=SHA_A,
        authority_source_ref=f"NASR:APT:{candidate_id.rsplit(':', maxsplit=1)[-1]}",
        source_id=source_id,
        source_snapshot_sha256=SHA_B,
        authority_artifact_key="nasr_zip",
        authority_artifact_sha256=SHA_C,
        manifest_artifact_key="nasr_manifest",
        manifest_artifact_sha256=SHA_A,
    )


def _check(
    candidate_id: str,
    check_kind: str,
    *,
    status: ConstraintCheckStatus = ConstraintCheckStatus.PASS,
    evidence_ids: tuple[str, ...] = (),
) -> ConstraintCheck:
    return ConstraintCheck(
        constraint_id=stable_contract_id(
            "resolution-constraint",
            candidate_id,
            check_kind,
            "controlled_facility",
            "airport",
            SHA_A,
        ),
        candidate_id=candidate_id,
        check_kind=check_kind,
        status=status,
        reason_code=f"{check_kind}:{status.value}",
        evidence_ids=evidence_ids,
        schema_snapshot_sha256=SHA_A if check_kind == "schema_compatibility" else None,
    )


def _candidate(
    candidate_id: str,
    *,
    eligible: bool = True,
) -> ResolutionCandidate:
    claim = _authority_claim(candidate_id)
    schema_status = ConstraintCheckStatus.PASS if eligible else ConstraintCheckStatus.FAIL
    return ResolutionCandidate(
        candidate_id=candidate_id,
        candidate_kind="facility",
        preferred_label=f"{candidate_id} AIRPORT",
        surface_form=candidate_id.rsplit(":", maxsplit=1)[-1],
        candidate_type="airport",
        ontology_class_prefixed="atm:Airport",
        ontology_class_iri="https://example.test/atm#Airport",
        authority_evidence_ids=(claim.evidence_id,),
        constraint_checks=(
            _check(candidate_id, "structural_slot"),
            _check(candidate_id, "expected_entity_type"),
            _check(
                candidate_id,
                "schema_compatibility",
                status=schema_status,
                evidence_ids=(claim.evidence_id,),
            ),
        ),
    )


def _candidate_checksum(candidate: ResolutionCandidate) -> str:
    payload = canonicalize_contract_value(
        candidate.model_dump(mode="python", exclude_computed_fields=True)
    )
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode()
    ).hexdigest()


def _audit(candidate: ResolutionCandidate) -> ResolutionCandidateAudit:
    claim = _authority_claim(candidate.candidate_id)
    checksum = _candidate_checksum(candidate)
    return ResolutionCandidateAudit(
        candidate_audit_id=stable_contract_id(
            "resolution-candidate-audit",
            candidate.candidate_id,
            candidate.candidate_kind,
            "ok",
            checksum,
            claim.evidence_id,
            claim.source_id,
            "NONE",
            "NONE",
        ),
        candidate_id=candidate.candidate_id,
        candidate_kind=candidate.candidate_kind,
        build_status=CandidateBuildStatus.OK,
        candidate_payload_checksum=checksum,
        evidence_id=claim.evidence_id,
        source_id=claim.source_id,
    )


def _task(
    *,
    candidate_ids: tuple[str, ...] = ("facility:KJFK", "facility:KBOS"),
    eligible_ids: tuple[str, ...] = ("facility:KJFK",),
):
    candidates = tuple(
        _candidate(candidate_id, eligible=candidate_id in eligible_ids)
        for candidate_id in sorted(candidate_ids)
    )
    audits = tuple(
        sorted(
            (_audit(candidate) for candidate in candidates), key=lambda row: row.candidate_audit_id
        )
    )
    claims = tuple(
        sorted(
            (_authority_claim(candidate.candidate_id) for candidate in candidates),
            key=lambda row: row.evidence_id,
        )
    )
    task_id = stable_contract_id(
        "resolution-task",
        "run-1",
        "event-1",
        "JFK",
        "controlled_facility",
        "airport",
        canonical_id_tuple_token(
            tuple(sorted(audit.candidate_audit_id for audit in audits)),
            sort_values=True,
        ),
        "schema-slice-1",
        SHA_A,
    )
    return seal_resolution_task(
        fields=ResolutionTaskFields(
            task_id=task_id,
            run_id="run-1",
            event_id="event-1",
            mention="JFK",
            structural_slot="controlled_facility",
            expected_entity_type="airport",
            authority_domain_status=CandidateBuildStatus.OK,
            raw_candidate_refs=tuple(
                RawResolutionCandidateRef(
                    candidate_id=candidate.candidate_id,
                    candidate_kind=candidate.candidate_kind,
                )
                for candidate in candidates
            ),
            candidates=candidates,
            candidate_audits=audits,
            authority_evidence=claims,
            authority_source_ids=tuple(sorted(claim.source_id for claim in claims)),
            ontology_constraints=("atm:Airport",),
            schema_slice_id="schema-slice-1",
            schema_snapshot_sha256=SHA_A,
            remaining_tool_budget=3,
        ),
        binding=ContractExecutionBinding(
            run_id="run-1",
            created_at=NOW,
            tool_version="semantic-resolution-tools-v1",
        ),
    )


def test_resolution_tools_expose_only_the_five_registered_names():
    tools = build_resolution_tools(ResolutionToolGateway(task=_task()))

    assert [tool.name for tool in tools] == [
        "get_resolution_candidates",
        "get_authority_record",
        "get_ontology_context",
        "check_candidate_constraints",
        "compare_candidate_evidence",
    ]


def test_resolution_candidates_return_only_eligible_task_owned_candidates():
    result = ResolutionToolGateway(task=_task()).get_resolution_candidates()

    assert result.candidate_ids == ["facility:KJFK"]
    assert [item.model_dump() for item in result.items] == [
        {
            "candidate_id": "facility:KJFK",
            "candidate_kind": "facility",
            "candidate_type": "airport",
            "ontology_class_iri": "https://example.test/atm#Airport",
            "ontology_class_prefixed": "atm:Airport",
        }
    ]


def test_authority_record_projects_exact_task_owned_evidence_and_source():
    task = _task()
    claim = next(
        claim for claim in task.authority_evidence if claim.candidate_id == "facility:KJFK"
    )

    result = ResolutionToolGateway(task=task).get_authority_record(candidate_id="facility:KJFK")

    assert result.authority_evidence_ids == [claim.evidence_id]
    assert result.authority_source_ids == [claim.source_id]
    assert [item.model_dump() for item in result.items] == [
        {
            "authority_record_locator": "APT.txt:facility:KJFK",
            "authority_record_text": "facility:KJFK authority record",
            "candidate_id": "facility:KJFK",
            "evidence_id": claim.evidence_id,
            "evidence_kind": "facility_record",
            "source_id": claim.source_id,
        }
    ]


@pytest.mark.parametrize(
    ("candidate_ids", "message"),
    [
        (["facility:KXXX"], "outside the sealed task"),
        (["facility:KJFK", "facility:KJFK"], "duplicate candidate IDs"),
        (["facility:KBOS"], "ineligible candidate IDs"),
    ],
)
def test_candidate_requests_fail_closed_outside_the_eligible_task_scope(candidate_ids, message):
    gateway = ResolutionToolGateway(task=_task())

    with pytest.raises(ResolutionToolError, match=message):
        gateway.get_ontology_context(candidate_ids=candidate_ids)


def test_cross_task_candidate_request_fails_closed():
    other_task = _task(candidate_ids=("facility:KORD",))
    gateway = ResolutionToolGateway(task=_task())

    with pytest.raises(ResolutionToolError, match="outside the sealed task"):
        gateway.get_authority_record(candidate_id=other_task.candidates[0].candidate_id)


def test_source_mismatched_task_is_refused_before_candidate_reads():
    task = _task()
    source_mismatched = task.model_copy(update={"authority_source_ids": ()})

    with pytest.raises(ResolutionToolError, match="source is not task-owned"):
        ResolutionToolGateway(task=source_mismatched)


def test_constraints_and_schema_context_are_typed_task_observations():
    task = _task()
    candidate = next(
        candidate for candidate in task.candidates if candidate.candidate_id == "facility:KJFK"
    )
    gateway = ResolutionToolGateway(task=task)

    constraint_result = gateway.check_candidate_constraints(candidate_ids=[candidate.candidate_id])
    ontology_result = gateway.get_ontology_context(candidate_ids=[candidate.candidate_id])

    assert constraint_result.constraint_ids == sorted(
        check.constraint_id for check in candidate.constraint_checks
    )
    assert constraint_result.items[0].status is ConstraintCheckStatus.PASS
    assert ontology_result.schema_slice_ids == [task.schema_slice_id]
    assert ontology_result.schema_snapshot_sha256 == task.schema_snapshot_sha256
    assert [item.model_dump() for item in ontology_result.items] == [
        {
            "candidate_id": candidate.candidate_id,
            "ontology_class_iri": candidate.ontology_class_iri,
            "ontology_class_prefixed": candidate.ontology_class_prefixed,
            "schema_slice_id": task.schema_slice_id,
            "schema_snapshot_sha256": task.schema_snapshot_sha256,
        }
    ]


def test_result_serialization_is_stable_and_evidence_comparison_is_source_bound():
    task = _task()
    gateway = ResolutionToolGateway(task=task)
    claim = next(
        claim for claim in task.authority_evidence if claim.candidate_id == "facility:KJFK"
    )

    result = gateway.compare_candidate_evidence(candidate_ids=["facility:KJFK"])

    assert result.authority_evidence_ids == [claim.evidence_id]
    assert result.authority_source_ids == [claim.source_id]
    assert result.model_dump_json() == result.model_dump_json()
    assert result.model_dump_json() == (
        '{"tool":"compare_candidate_evidence","status":"ok",'
        '"candidate_ids":["facility:KJFK"],'
        f'"authority_evidence_ids":["{claim.evidence_id}"],'
        f'"authority_source_ids":["{claim.source_id}"],'
        '"constraint_ids":[],"schema_slice_ids":[],'
        '"schema_snapshot_sha256":null,"result_ids":[],"items":[],'
        '"failure_reason":""}'
    )


class _ScriptedToolModel:
    """Provider-free native-tool replay used to test the real local loop."""

    def __init__(self, turns: list[ToolModelTurn]) -> None:
        self.turns = list(turns)
        self.invocations: list[str] = []

    def invoke(self, messages, *, phase: str) -> ToolModelTurn:
        self.invocations.append(phase)
        return self.turns.pop(0)


def _record(
    *, raw_response: str = "", output_tokens: int = 1, error: str | None = None, tool_calls=()
):
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord, ModelToolCall

    return ModelCallRecord(
        agent="semantic_resolution",
        raw_response=raw_response,
        prompt_set_id="prompt:test",
        prompt_version="semantic-resolution-agent-v1",
        provider="scripted",
        model="scripted-model",
        temperature=0,
        input_tokens=1,
        output_tokens=output_tokens,
        error=error,
        tool_calls=[ModelToolCall(**call) for call in tool_calls],
    )


def _tool_turn(*calls: dict, output_tokens: int = 1) -> ToolModelTurn:
    return ToolModelTurn(
        message=AIMessage(
            content="",
            tool_calls=[
                {
                    "id": call["call_id"],
                    "name": call["name"],
                    "args": call["arguments"],
                    "type": "tool_call",
                }
                for call in calls
            ],
        ),
        record=_record(tool_calls=calls, output_tokens=output_tokens),
    )


def _final_turn(payload: str, *, output_tokens: int = 1) -> ToolModelTurn:
    return ToolModelTurn(
        message=AIMessage(content=payload),
        record=_record(raw_response=payload, output_tokens=output_tokens),
    )


def _binding() -> ContractExecutionBinding:
    return ContractExecutionBinding(
        run_id="run-1",
        created_at=NOW,
        prompt_version="semantic-resolution-agent-v1",
    )


def _run(task, model: ToolCallingModel):
    from aviation_agentic_ai.agent_system.semantic_resolution import (
        run_semantic_resolution_agent,
    )

    return run_semantic_resolution_agent(
        task=task,
        binding=_binding(),
        tool_model_factory=lambda _tools: model,
    )


def test_semantic_resolution_seals_a_selected_candidate_from_observed_authority_support():
    task = _task(eligible_ids=("facility:KJFK", "facility:KBOS"))
    model = _ScriptedToolModel(
        [
            _tool_turn(
                {
                    "call_id": "call:authority",
                    "name": "get_authority_record",
                    "arguments": {"candidate_id": "facility:KJFK"},
                },
                {
                    "call_id": "call:constraints",
                    "name": "check_candidate_constraints",
                    "arguments": {"candidate_ids": ["facility:KJFK"]},
                },
            ),
            _final_turn(
                '{"decision":"accepted","selected_candidate_id":"facility:KJFK","rejected_candidate_ids":["facility:KBOS"],"limitation":null}'
            ),
        ]
    )

    result = _run(task, model)
    claim = next(row for row in task.authority_evidence if row.candidate_id == "facility:KJFK")

    assert result.failure_reason is None
    assert result.proposal.decision.value == "accepted"
    assert result.proposal.selected_candidate_id == "facility:KJFK"
    assert result.proposal.supporting_evidence_claim_ids == (claim.evidence_id,)
    assert result.proposal.authority_source_ids == (claim.source_id,)
    assert result.proposal.tool_trace_ids == ("call:authority", "call:constraints")
    assert model.invocations == ["select_tool", "final_answer"]


def test_semantic_resolution_seals_honest_abstention_after_a_bounded_observation_batch():
    task = _task(eligible_ids=("facility:KJFK", "facility:KBOS"))
    model = _ScriptedToolModel(
        [
            _tool_turn(
                {
                    "call_id": "call:candidates",
                    "name": "get_resolution_candidates",
                    "arguments": {},
                },
            ),
            _final_turn(
                '{"decision":"abstained","selected_candidate_id":null,"rejected_candidate_ids":["facility:KBOS","facility:KJFK"],"limitation":"The observed candidates remain ambiguous."}'
            ),
        ]
    )

    result = _run(task, model)

    assert result.failure_reason is None
    assert result.proposal.decision.value == "abstained"
    assert result.proposal.selected_candidate_id is None
    assert result.proposal.supporting_evidence_claim_ids == ()
    assert result.proposal.authority_source_ids == ()


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (
            '{"decision":"accepted","selected_candidate_id":"facility:KXXX","rejected_candidate_ids":["facility:KBOS","facility:KJFK"],"limitation":null}',
            "not an eligible task candidate",
        ),
        (
            '{"decision":"accepted","selected_candidate_id":"facility:KJFK","rejected_candidate_ids":["facility:KBOS"],"limitation":null}',
            "did not observe authority support",
        ),
    ],
)
def test_semantic_resolution_rejects_uncontained_or_unsupported_acceptance(payload, expected):
    task = _task(eligible_ids=("facility:KJFK", "facility:KBOS"))
    model = _ScriptedToolModel(
        [
            _tool_turn(
                {
                    "call_id": "call:candidates",
                    "name": "get_resolution_candidates",
                    "arguments": {},
                },
            ),
            _final_turn(payload),
        ]
    )

    result = _run(task, model)

    assert result.proposal.decision.value == "blocked"
    assert expected in str(result.failure_reason)
    assert model.invocations == ["select_tool", "final_answer"]


def test_semantic_resolution_blocks_malformed_final_json_without_a_repair_retry():
    task = _task(eligible_ids=("facility:KJFK", "facility:KBOS"))
    model = _ScriptedToolModel(
        [
            _tool_turn(
                {
                    "call_id": "call:candidates",
                    "name": "get_resolution_candidates",
                    "arguments": {},
                },
            ),
            _final_turn('{"decision":"abstained"} trailing'),
        ]
    )

    result = _run(task, model)

    assert result.proposal.decision.value == "blocked"
    assert "strict JSON" in str(result.failure_reason)
    assert model.invocations == ["select_tool", "final_answer"]


def test_semantic_resolution_records_provider_failure_as_a_consumed_single_attempt():
    from aviation_agentic_ai.agent_system.contracts import ModelCallRecord

    task = _task(eligible_ids=("facility:KJFK", "facility:KBOS"))
    model = _ScriptedToolModel(
        [
            ToolModelTurn(
                message=None,
                record=ModelCallRecord(
                    agent="semantic_resolution",
                    raw_response="",
                    error="TimeoutError: scripted upstream timeout",
                ),
            )
        ]
    )

    result = _run(task, model)

    assert result.proposal.decision.value == "blocked"
    assert result.failure_reason == "TimeoutError: scripted upstream timeout"
    assert len(result.model_calls) == 1
    assert model.invocations == ["select_tool"]


def test_semantic_resolution_enforces_three_tool_and_two_provider_turn_budgets():
    task = _task(eligible_ids=("facility:KJFK", "facility:KBOS"))
    model = _ScriptedToolModel(
        [
            _tool_turn(
                {"call_id": "one", "name": "get_resolution_candidates", "arguments": {}},
                {
                    "call_id": "two",
                    "name": "get_ontology_context",
                    "arguments": {"candidate_ids": ["facility:KJFK"]},
                },
                {
                    "call_id": "three",
                    "name": "check_candidate_constraints",
                    "arguments": {"candidate_ids": ["facility:KJFK"]},
                },
                {
                    "call_id": "four",
                    "name": "compare_candidate_evidence",
                    "arguments": {"candidate_ids": ["facility:KJFK"]},
                },
            )
        ]
    )

    result = _run(task, model)

    assert result.proposal.decision.value == "blocked"
    assert "tool-call budget" in str(result.failure_reason)
    assert len(result.model_calls) == 1
    assert model.invocations == ["select_tool"]


def test_semantic_resolution_blocks_oversize_rendered_input_before_constructing_a_model():
    task = _task(eligible_ids=("facility:KJFK", "facility:KBOS"))
    oversized = task.model_copy(
        update={"mention": "J" * 20000},
        deep=True,
    )
    factory_calls = 0

    def _factory(_tools: list[BaseTool]) -> ToolCallingModel:
        nonlocal factory_calls
        factory_calls += 1
        raise AssertionError("input overflow must not construct a provider model")

    from aviation_agentic_ai.agent_system.semantic_resolution import (
        run_semantic_resolution_agent,
    )

    result = run_semantic_resolution_agent(
        task=oversized,
        binding=_binding(),
        tool_model_factory=_factory,
    )

    assert result.proposal.decision.value == "blocked"
    assert "input budget" in str(result.failure_reason)
    assert factory_calls == 0


def test_semantic_resolution_counts_bound_tool_schemas_in_first_provider_input_budget(
    monkeypatch,
):
    from aviation_agentic_ai.agent_system import semantic_resolution

    task = _task(eligible_ids=("facility:KJFK", "facility:KBOS"))
    model = _ScriptedToolModel(
        [
            _tool_turn(
                {
                    "call_id": "call:authority",
                    "name": "get_authority_record",
                    "arguments": {"candidate_id": "facility:KJFK"},
                },
            ),
            _final_turn(
                '{"decision":"accepted","selected_candidate_id":"facility:KJFK","rejected_candidate_ids":["facility:KBOS"],"limitation":null}'
            ),
        ]
    )
    monkeypatch.setattr(semantic_resolution, "MAX_RENDERED_INPUT_TOKENS", 700)

    result = _run(task, model)

    assert result.proposal.decision.value == "blocked"
    assert "input budget" in str(result.failure_reason)
    assert model.invocations == []


def test_semantic_resolution_counts_tool_observations_in_final_provider_input_budget(
    monkeypatch,
):
    from aviation_agentic_ai.agent_system import semantic_resolution

    task = _task(eligible_ids=("facility:KJFK", "facility:KBOS"))
    claim = next(row for row in task.authority_evidence if row.candidate_id == "facility:KJFK")
    enlarged_claim = claim.model_copy(
        update={"authority_record_text": "facility:KJFK " + "X" * 20000}
    )
    oversized_observation_task = task.model_copy(
        update={
            "authority_evidence": tuple(
                enlarged_claim if row.evidence_id == claim.evidence_id else row
                for row in task.authority_evidence
            )
        }
    )
    model = _ScriptedToolModel(
        [
            _tool_turn(
                {
                    "call_id": "call:authority",
                    "name": "get_authority_record",
                    "arguments": {"candidate_id": "facility:KJFK"},
                },
            ),
            _final_turn(
                '{"decision":"accepted","selected_candidate_id":"facility:KJFK","rejected_candidate_ids":["facility:KBOS"],"limitation":null}'
            ),
        ]
    )
    monkeypatch.setattr(semantic_resolution, "MAX_RENDERED_INPUT_TOKENS", 4096)

    result = _run(oversized_observation_task, model)

    assert result.proposal.decision.value == "blocked"
    assert "input budget" in str(result.failure_reason)
    assert model.invocations == ["select_tool"]


def test_semantic_resolution_final_budget_excludes_unbound_tool_schemas(
    monkeypatch,
):
    from aviation_agentic_ai.agent_system import semantic_resolution
    from aviation_agentic_ai.agent_system.resolution_tools import (
        ResolutionToolGateway,
        build_resolution_tools,
    )

    task = _task(eligible_ids=("facility:KJFK", "facility:KBOS"))
    first_budget = semantic_resolution._estimated_input_tokens(
        semantic_resolution._base_messages(
            task, catalog_path="configs/prompts/agent_system_v1.yaml"
        ),
        bound_tools=build_resolution_tools(ResolutionToolGateway(task=task)),
    )
    model = _ScriptedToolModel(
        [
            _tool_turn(
                {
                    "call_id": "call:authority",
                    "name": "get_authority_record",
                    "arguments": {"candidate_id": "facility:KJFK"},
                },
                {
                    "call_id": "call:constraints",
                    "name": "check_candidate_constraints",
                    "arguments": {"candidate_ids": ["facility:KJFK"]},
                },
            ),
            _final_turn(
                '{"decision":"accepted","selected_candidate_id":"facility:KJFK","rejected_candidate_ids":["facility:KBOS"],"limitation":null}'
            ),
        ]
    )
    monkeypatch.setattr(semantic_resolution, "MAX_RENDERED_INPUT_TOKENS", first_budget)

    result = _run(task, model)

    assert result.proposal.decision.value == "accepted"
    assert result.failure_reason is None
    assert model.invocations == ["select_tool", "final_answer"]


def test_semantic_resolution_requires_observed_candidate_distinguishing_authority_content():
    task = _task(eligible_ids=("facility:KJFK", "facility:KBOS"))
    claim = next(row for row in task.authority_evidence if row.candidate_id == "facility:KJFK")
    generic_claim = claim.model_copy(
        update={
            "authority_record_text": "generic airport authority record",
            "authority_record_locator": "APT.txt:generic",
        }
    )
    non_distinguishing_task = task.model_copy(
        update={
            "authority_evidence": tuple(
                generic_claim if row.evidence_id == claim.evidence_id else row
                for row in task.authority_evidence
            )
        }
    )
    model = _ScriptedToolModel(
        [
            _tool_turn(
                {
                    "call_id": "call:authority",
                    "name": "get_authority_record",
                    "arguments": {"candidate_id": "facility:KJFK"},
                },
            ),
            _final_turn(
                '{"decision":"accepted","selected_candidate_id":"facility:KJFK","rejected_candidate_ids":["facility:KBOS"],"limitation":null}'
            ),
        ]
    )

    result = _run(non_distinguishing_task, model)

    assert result.proposal.decision.value == "blocked"
    assert "distinguishing authority content" in str(result.failure_reason)


def test_semantic_resolution_enforces_the_256_token_provider_output_cap():
    task = _task(eligible_ids=("facility:KJFK", "facility:KBOS"))
    model = _ScriptedToolModel(
        [
            _tool_turn(
                {
                    "call_id": "call:candidates",
                    "name": "get_resolution_candidates",
                    "arguments": {},
                },
                output_tokens=257,
            )
        ]
    )

    result = _run(task, model)

    assert result.proposal.decision.value == "blocked"
    assert "output-token cap" in str(result.failure_reason)
    assert model.invocations == ["select_tool"]


def test_semantic_resolution_scripted_replay_seals_byte_stable_proposals():
    task = _task(eligible_ids=("facility:KJFK", "facility:KBOS"))
    turns = [
        _tool_turn(
            {
                "call_id": "call:authority",
                "name": "get_authority_record",
                "arguments": {"candidate_id": "facility:KJFK"},
            },
        ),
        _final_turn(
            '{"decision":"accepted","selected_candidate_id":"facility:KJFK","rejected_candidate_ids":["facility:KBOS"],"limitation":null}'
        ),
    ]

    first = _run(task, _ScriptedToolModel(turns))
    second = _run(task, _ScriptedToolModel(turns))

    assert first.proposal.model_dump_json() == second.proposal.model_dump_json()
