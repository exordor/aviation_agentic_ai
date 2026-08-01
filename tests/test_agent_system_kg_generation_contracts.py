from __future__ import annotations

import pytest
from pydantic import ValidationError

from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    EvidenceCard,
    EvidenceClaim,
)
from aviation_agentic_ai.agent_system.kg_generation_contracts import (
    CandidateEntity,
    CandidateFact,
    CandidateFactProposal,
    GenerationEvidenceRecord,
    GenerationAbstention,
    OntologyGenerationTask,
)
from aviation_agentic_ai.agent_system.ontology_registry import (
    OntologySliceRequest,
    build_ontology_slice,
    load_ontology_registry,
)
from aviation_agentic_ai.utils.identifiers import stable_id


GROUND_DELAY_PROGRAM = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#GroundDelayProgramTMI"
)
CONTROLLED_NAS_ELEMENT = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#controlledNASelement"
)
TFM_CONTROL_ELEMENT = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#TFMcontrolElement"
)
AIRPORT = "https://data.nasa.gov/ontologies/atmonto/NAS#Airport"


def _task() -> OntologyGenerationTask:
    registry = load_ontology_registry()
    ontology_slice = build_ontology_slice(
        registry,
        OntologySliceRequest(
            subject_class_iri=GROUND_DELAY_PROGRAM,
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
        temporal_domain_id="test-domain-v1",
        ontology_slice=ontology_slice,
        evidence_cards=(evidence,),
        evidence_bindings=(
            GenerationEvidenceRecord(
                evidence_ref="ev-003",
                source_id="source-advisory-1",
                source_version_id="source-version-1",
                source_anchor_id=stable_id(
                    "source-anchor",
                    "source-version-1",
                    0,
                    24,
                ),
                char_start=0,
                char_end=24,
                evidence_text="CONTROLLED ELEMENT: KJFK",
            ),
        ),
        candidate_entities=(
            CandidateEntity(
                entity_id="airport:KJFK",
                class_iri=AIRPORT,
                label="John F. Kennedy International Airport",
            ),
        ),
    )


def test_generation_task_requires_nonempty_evidence_and_unique_entities() -> None:
    task = _task()
    assert task.root_id == "event:runtime-owned-1"
    assert task.evidence_refs == ("ev-003",)

    invalid_data = task.model_dump(mode="python")
    invalid_data["evidence_cards"] = ()
    with pytest.raises(ValidationError, match="at least one evidence card"):
        OntologyGenerationTask(**invalid_data)


def test_candidate_proposal_accepts_only_task_bound_fact_references() -> None:
    task = _task()
    proposal = CandidateFactProposal(
        status="accepted",
        facts=(
            CandidateFact(
                predicate_iri=CONTROLLED_NAS_ELEMENT,
                object_kind="iri",
                object_value="airport:KJFK",
                object_class_iri=AIRPORT,
                datatype_iri=None,
                evidence_ref="ev-003",
            ),
        ),
    )

    proposal.validate_against(task)


def test_candidate_proposal_rejects_unknown_predicate_or_evidence() -> None:
    task = _task()
    proposal = CandidateFactProposal(
        status="accepted",
        facts=(
            CandidateFact(
                predicate_iri="https://example.org/not-allowed",
                object_kind="iri",
                object_value="airport:KJFK",
                object_class_iri=AIRPORT,
                datatype_iri=None,
                evidence_ref="ev-unknown",
            ),
        ),
    )

    with pytest.raises(ValueError, match="predicate.*ontology slice"):
        proposal.validate_against(task)


def test_candidate_proposal_rejects_subject_outside_property_domain() -> None:
    task = _task()
    invalid_slice = task.ontology_slice.model_copy(
        update={"subject_class_iri": AIRPORT}
    )
    invalid_task = task.model_copy(update={"ontology_slice": invalid_slice})

    with pytest.raises(ValueError, match="property domain"):
        CandidateFactProposal(
            status="accepted",
            facts=(
                CandidateFact(
                    predicate_iri=CONTROLLED_NAS_ELEMENT,
                    object_kind="iri",
                    object_value="airport:KJFK",
                    object_class_iri=AIRPORT,
                    evidence_ref="ev-003",
                ),
            ),
        ).validate_against(invalid_task)


def test_abstention_can_reference_only_task_evidence() -> None:
    task = _task()
    proposal = CandidateFactProposal(
        status="abstained",
        abstentions=(
            GenerationAbstention(
                reason="evidence does not identify a supported facility",
                evidence_refs=("ev-003",),
            ),
        ),
    )

    proposal.validate_against(task)

    invalid = proposal.model_copy(
        update={
            "abstentions": (
                GenerationAbstention(
                    reason="unknown evidence",
                    evidence_refs=("ev-not-real",),
                ),
            )
        }
    )
    with pytest.raises(ValueError, match="evidence reference"):
        invalid.validate_against(task)
