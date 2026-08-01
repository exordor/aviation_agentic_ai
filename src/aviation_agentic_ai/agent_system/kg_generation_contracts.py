"""Sealed contracts for ontology-constrained LLM fact generation.

These models deliberately describe a *proposal* boundary.  They do not carry
source-version identity or persistence instructions, and they cannot by
themselves publish a semantic fact.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from aviation_agentic_ai.agent_system.contracts import EvidenceCard, StrictModel
from aviation_agentic_ai.agent_system.ontology_registry import OntologySlice


class CandidateEntity(StrictModel):
    """A runtime-resolved entity that the model may reference."""

    entity_id: str = Field(min_length=1)
    class_iri: str = Field(min_length=1)
    label: str = Field(min_length=1)


class GenerationAbstention(StrictModel):
    """A reason why the model declined to emit a candidate fact."""

    reason: str = Field(min_length=1)
    evidence_refs: tuple[str, ...] = ()


class ProfileGapProposal(StrictModel):
    """A source-supported fact without a currently publishable profile term."""

    field: str = Field(min_length=1)
    value: str = Field(min_length=1)
    evidence_ref: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class CandidateFact(StrictModel):
    """One candidate predicate/object pair for the runtime-owned subject."""

    predicate_iri: str = Field(min_length=1)
    object_kind: Literal["iri", "literal"]
    object_value: str = Field(min_length=1)
    object_class_iri: str | None = None
    datatype_iri: str | None = None
    evidence_ref: str = Field(min_length=1)


class OntologyGenerationTask(StrictModel):
    """Closed context handed to one ontology-constrained generation call."""

    task_id: str = Field(min_length=1)
    root_id: str = Field(min_length=1)
    ontology_slice: OntologySlice
    evidence_cards: tuple[EvidenceCard, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    candidate_entities: tuple[CandidateEntity, ...] = ()

    @model_validator(mode="after")
    def _validate_task_scope(self) -> OntologyGenerationTask:
        if not self.evidence_cards:
            raise ValueError("at least one evidence card is required")
        if not self.evidence_refs:
            raise ValueError("at least one evidence reference is required")
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise ValueError("evidence references must be unique")

        class_iris = {row.iri for row in self.ontology_slice.classes}
        entity_ids: set[str] = set()
        for entity in self.candidate_entities:
            if entity.entity_id in entity_ids:
                raise ValueError("candidate entity IDs must be unique")
            entity_ids.add(entity.entity_id)
            if entity.class_iri not in class_iris:
                raise ValueError("candidate entity class is outside ontology slice")
        return self


class CandidateFactProposal(StrictModel):
    """Strict model output before ontology/evidence/publication validation."""

    status: Literal["accepted", "abstained"]
    facts: tuple[CandidateFact, ...] = ()
    abstentions: tuple[GenerationAbstention, ...] = ()
    profile_gaps: tuple[ProfileGapProposal, ...] = ()

    def validate_against(self, task: OntologyGenerationTask) -> None:
        """Reject references that were not made available by the runtime."""

        property_by_iri = {row.iri: row for row in task.ontology_slice.properties}
        class_iris = {row.iri for row in task.ontology_slice.classes}
        evidence_refs = set(task.evidence_refs)
        entities = {entity.entity_id: entity for entity in task.candidate_entities}

        for fact in self.facts:
            prop = property_by_iri.get(fact.predicate_iri)
            if prop is None:
                raise ValueError("predicate is outside the ontology slice")
            if fact.evidence_ref not in evidence_refs:
                raise ValueError("fact evidence reference is outside the task")

            if fact.object_kind == "iri":
                if prop.kind != "ObjectProperty":
                    raise ValueError("IRI object requires an object property")
                entity = entities.get(fact.object_value)
                if entity is None:
                    raise ValueError("IRI object is outside candidate entities")
                if fact.object_class_iri != entity.class_iri:
                    raise ValueError("object class does not match candidate entity")
                if fact.object_class_iri not in class_iris:
                    raise ValueError("object class is outside the ontology slice")
                if not _range_accepts(
                    fact.object_class_iri,
                    prop.range_iris,
                    task.ontology_slice,
                ):
                    raise ValueError("object class violates ontology property range")
                if fact.datatype_iri is not None:
                    raise ValueError("IRI object cannot carry a datatype")
            else:
                if prop.kind != "DataProperty":
                    raise ValueError("literal object requires a datatype property")
                if fact.object_class_iri is not None:
                    raise ValueError("literal object cannot carry an object class")
                if fact.datatype_iri is None:
                    raise ValueError("literal object requires a datatype")
                if prop.datatype_iris and fact.datatype_iri not in prop.datatype_iris:
                    raise ValueError("literal datatype violates ontology property range")

        for abstention in self.abstentions:
            _validate_evidence_refs(abstention.evidence_refs, evidence_refs)
        for gap in self.profile_gaps:
            _validate_evidence_refs((gap.evidence_ref,), evidence_refs)


def _validate_evidence_refs(
    refs: tuple[str, ...],
    allowed_refs: set[str],
) -> None:
    unknown = set(refs) - allowed_refs
    if unknown:
        raise ValueError("evidence reference is outside the task")


def _range_accepts(
    object_class_iri: str,
    range_iris: tuple[str, ...],
    ontology_slice: OntologySlice,
) -> bool:
    if not range_iris:
        return True
    parents: dict[str, set[str]] = {}
    for edge in ontology_slice.hierarchy:
        parents.setdefault(edge.subclass_iri, set()).add(edge.superclass_iri)
    seen: set[str] = set()
    stack = [object_class_iri]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(parents.get(current, set()) - seen)
    return bool(seen & set(range_iris))


__all__ = [
    "CandidateEntity",
    "CandidateFact",
    "CandidateFactProposal",
    "GenerationAbstention",
    "OntologyGenerationTask",
    "ProfileGapProposal",
]
