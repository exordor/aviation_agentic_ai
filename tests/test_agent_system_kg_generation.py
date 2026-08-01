from __future__ import annotations

import json

from langchain_core.messages import AIMessage

from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    EvidenceCard,
    EvidenceClaim,
    ModelCallRecord,
)
from aviation_agentic_ai.agent_system.kg_generation import generate_candidate_facts
from aviation_agentic_ai.agent_system.kg_generation_contracts import (
    OntologyGenerationTask,
)
from aviation_agentic_ai.agent_system.ontology_registry import (
    OntologySliceRequest,
    build_ontology_slice,
    load_ontology_registry,
)
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn


CONTROLLED_NAS_ELEMENT = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#controlledNASelement"
)
AIRPORT = "https://data.nasa.gov/ontologies/atmonto/NAS#Airport"


def _task() -> OntologyGenerationTask:
    registry = load_ontology_registry()
    ontology_slice = build_ontology_slice(
        registry,
        OntologySliceRequest(
            subject_class_iri=(
                "https://data.nasa.gov/ontologies/atmonto/ATM#GroundDelayProgramTMI"
            ),
            candidate_property_iris=(CONTROLLED_NAS_ELEMENT,),
            candidate_object_class_iris=(AIRPORT,),
            profile_id="test-profile-v1",
        ),
    )
    evidence = EvidenceCard(
        agent_role="facility",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="controlled_facility",
                value="KJFK",
                evidence_text="CONTROLLED ELEMENT: KJFK",
                source_id="source-advisory-1",
                canonical_ref="airport:KJFK",
            )
        ],
        source_ids=["source-advisory-1"],
    )
    return OntologyGenerationTask(
        task_id="generation-task-1",
        root_id="event:runtime-owned-1",
        ontology_slice=ontology_slice,
        evidence_cards=(evidence,),
        evidence_refs=("ev-003",),
        candidate_entities=(
            {
                "entity_id": "airport:KJFK",
                "class_iri": AIRPORT,
                "label": "John F. Kennedy International Airport",
            },
        ),
    )


class _ScriptedProposalModel:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload
        self.phases: list[str] = []
        self.messages: list[list[object]] = []

    def invoke(self, messages, *, phase: str) -> ToolModelTurn:
        self.phases.append(phase)
        self.messages.append(list(messages))
        raw = json.dumps(self.payload, sort_keys=True)
        return ToolModelTurn(
            message=AIMessage(content=raw),
            record=ModelCallRecord(
                agent="kg_generation",
                raw_response=raw,
                prompt_set_id="ontology-grounded-kg-v1",
                prompt_version="candidate-fact-v1",
                provider="scripted",
                model="scripted-model",
                temperature=0,
                input_tokens=10,
                output_tokens=4,
            ),
        )


def _accepted_payload() -> dict[str, object]:
    return {
        "status": "accepted",
        "facts": [
            {
                "predicate_iri": CONTROLLED_NAS_ELEMENT,
                "object_kind": "iri",
                "object_value": "airport:KJFK",
                "object_class_iri": AIRPORT,
                "datatype_iri": None,
                "evidence_ref": "ev-003",
            }
        ],
        "abstentions": [],
        "profile_gaps": [],
    }


def test_generator_returns_typed_candidate_fact_without_storage_write() -> None:
    task = _task()
    model = _ScriptedProposalModel(_accepted_payload())

    result = generate_candidate_facts(task, model)

    assert result.status == "accepted"
    assert result.proposal is not None
    assert len(result.proposal.facts) == 1
    assert model.phases == ["emit_proposal"]
    assert "raw_response" not in result.proposal.model_dump()


def test_generator_preserves_model_abstention() -> None:
    task = _task()
    model = _ScriptedProposalModel(
        {
            "status": "abstained",
            "facts": [],
            "abstentions": [
                {
                    "reason": "the evidence does not identify a supported airport",
                    "evidence_refs": ["ev-003"],
                }
            ],
            "profile_gaps": [],
        }
    )

    result = generate_candidate_facts(task, model)

    assert result.status == "abstained"
    assert result.proposal is not None
    assert result.proposal.abstentions[0].evidence_refs == ("ev-003",)


def test_generator_blocks_unknown_predicate_before_publication() -> None:
    task = _task()
    payload = _accepted_payload()
    payload["facts"] = [
        {
            **payload["facts"][0],  # type: ignore[index]
            "predicate_iri": "https://example.org/not-in-slice",
        }
    ]
    model = _ScriptedProposalModel(payload)

    result = generate_candidate_facts(task, model)

    assert result.status == "blocked"
    assert result.proposal is None
    assert result.failure_reason == "candidate proposal violates task contract"


def test_generator_rejects_model_tool_calls_in_proposal_phase() -> None:
    task: OntologyGenerationTask = _task()
    model = _ScriptedProposalModel(_accepted_payload())
    turn = model.invoke([], phase="emit_proposal")
    model.invoke = lambda messages, *, phase: ToolModelTurn(  # type: ignore[method-assign]
        message=AIMessage(
            content="{}",
            tool_calls=[
                {
                    "id": "call-1",
                    "name": "forbidden_tool",
                    "args": {},
                    "type": "tool_call",
                }
            ],
        ),
        record=turn.record,
    )

    result = generate_candidate_facts(task, model)

    assert result.status == "blocked"
    assert result.failure_reason == "proposal phase returned a tool call"
