"""Sealed contracts for ontology-constrained LLM fact generation.

These models deliberately describe a *proposal* boundary.  They do not carry
source-version identity or persistence instructions, and they cannot by
themselves publish a semantic fact.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from aviation_agentic_ai.agent_system.contracts import EvidenceCard, StrictModel
from aviation_agentic_ai.agent_system.storage_contracts import SourceAnchorRecord
from aviation_agentic_ai.agent_system.ontology_registry import OntologySlice


class OntologyExtractionClass(StrictModel):
    """One compact class descriptor exposed to NER."""

    iri: str = Field(min_length=1)
    label: str = Field(min_length=1)
    description: str = Field(min_length=1)
    aliases: tuple[str, ...] = ()
    ancestor_iris: tuple[str, ...] = ()


class OntologyExtractionProperty(StrictModel):
    """One compact relation descriptor exposed to RE."""

    iri: str = Field(min_length=1)
    label: str = Field(min_length=1)
    description: str = Field(min_length=1)
    aliases: tuple[str, ...] = ()
    kind: Literal["object", "datatype"]
    domain_iris: tuple[str, ...] = ()
    range_iris: tuple[str, ...] = ()


class OntologyExtractionSchema(StrictModel):
    """Checksum-bound, LLM-friendly schema slice for one evidence chunk."""

    profile_id: str = Field(min_length=1)
    profile_checksum: str = Field(min_length=1)
    schema_checksum: str = Field(min_length=1)
    evidence_ref: str = Field(min_length=1)
    classes: tuple[OntologyExtractionClass, ...] = Field(min_length=1)
    properties: tuple[OntologyExtractionProperty, ...] = Field(min_length=1)
    prompt_schema: str = Field(min_length=1)


class EntityMentionCandidate(StrictModel):
    """One exact source mention proposed by the NER call."""

    mention_id: str = Field(min_length=1)
    surface_text: str = Field(min_length=1)
    class_iri: str = Field(min_length=1)
    evidence_ref: str = Field(min_length=1)
    concept_or_instance: Literal["concept", "instance"]
    confidence: float = Field(ge=0.0, le=1.0)


class GenerationAbstention(StrictModel):
    """A reason why the model declined to emit a candidate fact."""

    reason: str = Field(min_length=1)
    evidence_refs: tuple[str, ...] = ()


class EntityExtractionTask(StrictModel):
    """Closed task for one extraction chunk and one compact schema."""

    task_id: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)
    paragraph_id: str = Field(min_length=1)
    evidence_ref: str = Field(min_length=1)
    evidence_text: str = Field(min_length=1)
    ontology_schema: OntologyExtractionSchema
    few_shot_examples: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _bind_schema_to_evidence(self) -> EntityExtractionTask:
        if self.ontology_schema.evidence_ref != self.evidence_ref:
            raise ValueError("extraction schema is not bound to task evidence")
        return self


class EntityExtractionProposal(StrictModel):
    """Strict NER output before deterministic mention resolution."""

    status: Literal["accepted", "abstained"]
    mentions: tuple[EntityMentionCandidate, ...] = ()
    unmapped_mentions: tuple[str, ...] = ()
    abstentions: tuple[GenerationAbstention, ...] = ()

    def validate_against(self, task: EntityExtractionTask) -> None:
        class_iris = {row.iri for row in task.ontology_schema.classes}
        mention_ids: set[str] = set()
        for mention in self.mentions:
            if mention.mention_id in mention_ids:
                raise ValueError("mention IDs must be unique within one task")
            mention_ids.add(mention.mention_id)
            if mention.class_iri not in class_iris:
                raise ValueError("mention class is outside the extraction schema")
            if mention.evidence_ref != task.evidence_ref:
                raise ValueError("mention evidence is outside the extraction task")
        for abstention in self.abstentions:
            _validate_evidence_refs(
                abstention.evidence_refs,
                {task.evidence_ref},
            )


class ResolvedKnowledgeEntity(StrictModel):
    """A deterministically identified entity backed by exact source text."""

    entity_id: str = Field(min_length=1)
    class_iri: str = Field(min_length=1)
    canonical_label: str = Field(min_length=1)
    aliases: tuple[str, ...] = ()
    concept_or_instance: Literal["concept", "instance"]
    mention_ids: tuple[str, ...] = Field(min_length=1)
    evidence_ref: str = Field(min_length=1)
    evidence_text: str = Field(min_length=1)
    source_version_id: str = Field(min_length=1)
    paragraph_id: str = Field(min_length=1)
    char_start: int = Field(ge=0)
    char_end: int = Field(gt=0)
    confidence: float = Field(ge=0.0, le=1.0)


class EntityResolutionResult(StrictModel):
    """Resolved entities plus mentions intentionally left outside the profile."""

    entities: tuple[ResolvedKnowledgeEntity, ...] = ()
    unmapped_mentions: tuple[str, ...] = ()


class RelationExtractionTask(StrictModel):
    """Closed RE task over already resolved entity IDs."""

    task_id: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)
    paragraph_id: str = Field(min_length=1)
    evidence_ref: str = Field(min_length=1)
    evidence_text: str = Field(min_length=1)
    ontology_schema: OntologyExtractionSchema
    entities: tuple[ResolvedKnowledgeEntity, ...] = Field(min_length=2)
    few_shot_examples: tuple[str, ...] = ()


class RelationCandidate(StrictModel):
    """One evidence-quoted relation proposed between resolved entities."""

    subject_id: str = Field(min_length=1)
    predicate_iri: str = Field(min_length=1)
    object_id: str = Field(min_length=1)
    evidence_ref: str = Field(min_length=1)
    evidence_quote: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    quote_char_start: int | None = Field(default=None, ge=0)
    quote_char_end: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def _paired_quote_offsets(self) -> RelationCandidate:
        if (self.quote_char_start is None) != (self.quote_char_end is None):
            raise ValueError("relation quote offsets must be supplied together")
        if (
            self.quote_char_start is not None
            and self.quote_char_end is not None
            and self.quote_char_end <= self.quote_char_start
        ):
            raise ValueError("relation quote offsets are not ordered")
        return self


class RelationExtractionProposal(StrictModel):
    """Strict RE output before deterministic evidence localization."""

    status: Literal["accepted", "abstained", "not_applicable"]
    relations: tuple[RelationCandidate, ...] = ()
    abstentions: tuple[GenerationAbstention, ...] = ()

    def validate_against(self, task: RelationExtractionTask) -> None:
        entity_by_id = {row.entity_id: row for row in task.entities}
        property_by_iri = {
            row.iri: row
            for row in task.ontology_schema.properties
            if row.kind == "object"
        }
        class_by_iri = {row.iri: row for row in task.ontology_schema.classes}
        for relation in self.relations:
            subject = entity_by_id.get(relation.subject_id)
            object_ = entity_by_id.get(relation.object_id)
            if subject is None or object_ is None:
                raise ValueError("relation endpoint is outside resolved entities")
            prop = property_by_iri.get(relation.predicate_iri)
            if prop is None:
                raise ValueError("relation predicate is outside the extraction schema")
            if not _extraction_class_satisfies(
                subject.class_iri,
                prop.domain_iris,
                class_by_iri,
            ):
                raise ValueError("relation subject violates property domain")
            if not _extraction_class_satisfies(
                object_.class_iri,
                prop.range_iris,
                class_by_iri,
            ):
                raise ValueError("relation object violates property range")
            if relation.evidence_ref != task.evidence_ref:
                raise ValueError("relation evidence is outside the extraction task")
        for abstention in self.abstentions:
            _validate_evidence_refs(
                abstention.evidence_refs,
                {task.evidence_ref},
            )


class CandidateKnowledgeSubgraph(StrictModel):
    """One chunk-scoped candidate ABox after NER, normalization, and RE."""

    chunk_id: str = Field(min_length=1)
    source_version_id: str = Field(min_length=1)
    source_anchor_id: str = Field(min_length=1)
    paragraph_id: str = Field(min_length=1)
    profile_id: str = Field(min_length=1)
    profile_checksum: str = Field(min_length=1)
    schema_checksum: str = Field(min_length=1)
    entities: tuple[ResolvedKnowledgeEntity, ...] = ()
    relations: tuple[RelationCandidate, ...] = ()
    unmapped_mentions: tuple[str, ...] = ()


def _extraction_class_satisfies(
    class_iri: str,
    accepted_iris: tuple[str, ...],
    class_by_iri: dict[str, OntologyExtractionClass],
) -> bool:
    if not accepted_iris:
        return True
    row = class_by_iri.get(class_iri)
    represented = {class_iri, *(row.ancestor_iris if row is not None else ())}
    return bool(represented & set(accepted_iris))


class CandidateEntity(StrictModel):
    """A runtime-resolved entity that the model may reference."""

    entity_id: str = Field(min_length=1)
    class_iri: str = Field(min_length=1)
    label: str = Field(min_length=1)


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


class GenerationEvidenceRecord(StrictModel):
    """Runtime-owned binding from a prompt evidence reference to a source span.

    The model sees the stable ``evidence_ref`` and the quoted text, while the
    deterministic publication stage uses the version and anchor fields to
    prove that the reference resolves to an immutable source record.  The
    generator cannot create these bindings.
    """

    evidence_ref: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    source_version_id: str = Field(min_length=1)
    source_anchor_id: str = Field(min_length=1)
    char_start: int = Field(ge=0)
    char_end: int = Field(gt=0)
    evidence_text: str = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_anchor_identity(self) -> GenerationEvidenceRecord:
        expected_anchor_id = SourceAnchorRecord(
            source_anchor_id=self.source_anchor_id,
            source_version_id=self.source_version_id,
            char_start=self.char_start,
            char_end=self.char_end,
            # The task does not carry the complete source content, so the
            # anchor kind is finalized by the publication bridge.
            anchor_kind="text_span",
        ).source_anchor_id
        if self.source_anchor_id != expected_anchor_id:
            raise ValueError("generation evidence anchor identity is not stable")
        return self


class OntologyGenerationTask(StrictModel):
    """Closed context handed to one ontology-constrained generation call."""

    task_id: str = Field(min_length=1)
    generation_stage: str = Field(default="default", min_length=1)
    root_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    ontology_slice: OntologySlice
    evidence_cards: tuple[EvidenceCard, ...] = ()
    evidence_bindings: tuple[GenerationEvidenceRecord, ...] = Field(min_length=1)
    evidence_refs: tuple[str, ...] = ()
    candidate_entities: tuple[CandidateEntity, ...] = ()

    @model_validator(mode="after")
    def _validate_task_scope(self) -> OntologyGenerationTask:
        if not self.evidence_cards:
            raise ValueError("at least one evidence card is required")
        binding_refs = tuple(binding.evidence_ref for binding in self.evidence_bindings)
        if len(set(binding_refs)) != len(binding_refs):
            raise ValueError("evidence references must be unique")
        if self.evidence_refs and self.evidence_refs != binding_refs:
            raise ValueError("evidence_refs must match evidence_bindings")
        self.evidence_refs = binding_refs

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
            if not _class_satisfies(
                task.ontology_slice.subject_class_iri,
                prop.domain_iris,
                task.ontology_slice,
            ):
                raise ValueError("subject class violates ontology property domain")
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
                if not _class_satisfies(
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


def _class_satisfies(
    class_iri: str,
    accepted_iris: tuple[str, ...],
    ontology_slice: OntologySlice,
) -> bool:
    if not accepted_iris:
        return True
    parents: dict[str, set[str]] = {}
    for edge in ontology_slice.hierarchy:
        parents.setdefault(edge.subclass_iri, set()).add(edge.superclass_iri)
    seen: set[str] = set()
    stack = [class_iri]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(parents.get(current, set()) - seen)
    return bool(seen & set(accepted_iris))


__all__ = [
    "CandidateEntity",
    "CandidateKnowledgeSubgraph",
    "CandidateFact",
    "CandidateFactProposal",
    "GenerationAbstention",
    "GenerationEvidenceRecord",
    "EntityExtractionProposal",
    "EntityExtractionTask",
    "EntityMentionCandidate",
    "EntityResolutionResult",
    "OntologyGenerationTask",
    "OntologyExtractionClass",
    "OntologyExtractionProperty",
    "OntologyExtractionSchema",
    "RelationCandidate",
    "RelationExtractionProposal",
    "RelationExtractionTask",
    "ResolvedKnowledgeEntity",
    "ProfileGapProposal",
]
