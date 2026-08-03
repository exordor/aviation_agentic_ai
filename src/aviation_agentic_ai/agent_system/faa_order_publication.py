"""Map Chapter 18 candidate subgraphs into formal incremental KG roots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    EvidenceCard,
    EvidenceClaim,
)
from aviation_agentic_ai.agent_system.faa_order_document import (
    FAAOrderExtractionChunk,
    FAAOrderSourcePackage,
)
from aviation_agentic_ai.agent_system.faa_order_ontology import (
    FAA_ORDER_NAMESPACE,
    POLICY_PARAGRAPH_CLASS,
    POLICY_RULE_CLASS,
    build_faa_order_ontology_slice,
)
from aviation_agentic_ai.agent_system.kg_generation_contracts import (
    CandidateEntity,
    CandidateFact,
    CandidateFactProposal,
    CandidateKnowledgeSubgraph,
    GenerationEvidenceRecord,
    OntologyGenerationTask,
)
from aviation_agentic_ai.agent_system.kg_generation_validation import (
    apply_generated_publication,
    validate_and_prepare_generated_publication,
)
from aviation_agentic_ai.agent_system.validation_profiles import (
    ValidationProfileRegistry,
)
from aviation_agentic_ai.utils.identifiers import stable_id


POLICY_DOCUMENT_CLASS = FAA_ORDER_NAMESPACE + "PolicyDocument"
POLICY_SECTION_CLASS = FAA_ORDER_NAMESPACE + "PolicySection"
RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
XSD_STRING = "http://www.w3.org/2001/XMLSchema#string"


@dataclass(frozen=True)
class FAAOrderPublicationSummary:
    """Result of publishing independently validated document knowledge roots."""

    status: Literal["ok", "insufficient", "blocked"]
    publication_ids: tuple[str, ...]
    accepted_root_count: int
    blocked_root_count: int
    published_fact_count: int = 0
    published_evidence_link_count: int = 0
    reasons: tuple[str, ...] = ()


@dataclass
class _RootAccumulator:
    root_id: str
    class_iri: str
    root_kind: str
    facts: list[CandidateFact] = field(default_factory=list)
    bindings: dict[str, GenerationEvidenceRecord] = field(default_factory=dict)
    candidate_entities: dict[str, CandidateEntity] = field(default_factory=dict)

    def add_fact(
        self,
        fact: CandidateFact,
        binding: GenerationEvidenceRecord,
        object_entity: CandidateEntity | None = None,
    ) -> None:
        self.bindings[binding.evidence_ref] = binding
        if object_entity is not None:
            self.candidate_entities[object_entity.entity_id] = object_entity
        identity = (
            fact.predicate_iri,
            fact.object_kind,
            fact.object_value,
            fact.object_class_iri,
            fact.datatype_iri,
            fact.evidence_ref,
        )
        if identity not in {
            (
                row.predicate_iri,
                row.object_kind,
                row.object_value,
                row.object_class_iri,
                row.datatype_iri,
                row.evidence_ref,
            )
            for row in self.facts
        }:
            self.facts.append(fact)


def _binding(
    package: FAAOrderSourcePackage,
    *,
    evidence_ref: str,
    char_start: int,
    char_end: int,
) -> GenerationEvidenceRecord:
    return GenerationEvidenceRecord(
        evidence_ref=evidence_ref,
        source_id=package.source_version.source_id,
        source_version_id=package.source_version_id,
        source_anchor_id=stable_id(
            "source-anchor",
            package.source_version_id,
            char_start,
            char_end,
        ),
        char_start=char_start,
        char_end=char_end,
        evidence_text=package.source_version.content[char_start:char_end],
    )


def _root(
    roots: dict[str, _RootAccumulator],
    *,
    root_id: str,
    class_iri: str,
    root_kind: str,
) -> _RootAccumulator:
    existing = roots.get(root_id)
    if existing is not None:
        if existing.class_iri != class_iri or existing.root_kind != root_kind:
            raise ValueError("document knowledge root identity is semantically inconsistent")
        return existing
    created = _RootAccumulator(
        root_id=root_id,
        class_iri=class_iri,
        root_kind=root_kind,
    )
    roots[root_id] = created
    return created


def _add_literal(
    root: _RootAccumulator,
    package: FAAOrderSourcePackage,
    *,
    predicate_iri: str,
    value: str,
    evidence_ref: str,
    char_start: int,
    char_end: int,
) -> None:
    root.add_fact(
        CandidateFact(
            predicate_iri=predicate_iri,
            object_kind="literal",
            object_value=value,
            datatype_iri=XSD_STRING,
            evidence_ref=evidence_ref,
        ),
        _binding(
            package,
            evidence_ref=evidence_ref,
            char_start=char_start,
            char_end=char_end,
        ),
    )


def _add_iri(
    root: _RootAccumulator,
    package: FAAOrderSourcePackage,
    *,
    predicate_iri: str,
    object_id: str,
    object_class_iri: str,
    object_label: str,
    evidence_ref: str,
    char_start: int,
    char_end: int,
) -> None:
    root.add_fact(
        CandidateFact(
            predicate_iri=predicate_iri,
            object_kind="iri",
            object_value=object_id,
            object_class_iri=object_class_iri,
            evidence_ref=evidence_ref,
        ),
        _binding(
            package,
            evidence_ref=evidence_ref,
            char_start=char_start,
            char_end=char_end,
        ),
        CandidateEntity(
            entity_id=object_id,
            class_iri=object_class_iri,
            label=object_label,
        ),
    )


def _structure_roots(
    package: FAAOrderSourcePackage,
    chunks: tuple[FAAOrderExtractionChunk, ...],
    roots: dict[str, _RootAccumulator],
) -> dict[str, str]:
    document_id = stable_id("ontology-document", package.source_version_id)
    document = _root(
        roots,
        root_id=document_id,
        class_iri=POLICY_DOCUMENT_CLASS,
        root_kind="ontology_document",
    )
    paragraph_ids: dict[str, str] = {}
    first_by_paragraph: dict[str, FAAOrderExtractionChunk] = {}
    for chunk in chunks:
        first_by_paragraph.setdefault(chunk.paragraph_id, chunk)
    first_by_section: dict[str, FAAOrderExtractionChunk] = {}
    for chunk in first_by_paragraph.values():
        first_by_section.setdefault(chunk.section_id, chunk)

    first_chunk = chunks[0]
    _add_literal(
        document,
        package,
        predicate_iri=RDFS_LABEL,
        value="FAA JO 7210.3EE Facility Operation and Administration",
        evidence_ref=stable_id("document-label-evidence", package.source_version_id),
        char_start=first_chunk.char_start,
        char_end=first_chunk.char_end,
    )
    for section_id, section_chunk in sorted(first_by_section.items()):
        section_root_id = stable_id(
            "ontology-section",
            package.source_version_id,
            section_id,
        )
        section = _root(
            roots,
            root_id=section_root_id,
            class_iri=POLICY_SECTION_CLASS,
            root_kind="ontology_section",
        )
        evidence_ref = stable_id(
            "ontology-structure-evidence",
            package.source_version_id,
            "section",
            section_id,
        )
        _add_iri(
            document,
            package,
            predicate_iri=FAA_ORDER_NAMESPACE + "hasSection",
            object_id=section_root_id,
            object_class_iri=POLICY_SECTION_CLASS,
            object_label=section_id,
            evidence_ref=evidence_ref,
            char_start=section_chunk.char_start,
            char_end=section_chunk.char_end,
        )
        _add_literal(
            section,
            package,
            predicate_iri=RDFS_LABEL,
            value=f"Chapter 18 Section {section_id}",
            evidence_ref=evidence_ref,
            char_start=section_chunk.char_start,
            char_end=section_chunk.char_end,
        )
        _add_literal(
            section,
            package,
            predicate_iri=FAA_ORDER_NAMESPACE + "sectionNumber",
            value=section_id,
            evidence_ref=evidence_ref,
            char_start=section_chunk.char_start,
            char_end=section_chunk.char_end,
        )

    for paragraph_id, chunk in sorted(first_by_paragraph.items()):
        section_root_id = stable_id(
            "ontology-section",
            package.source_version_id,
            chunk.section_id,
        )
        paragraph_root_id = stable_id(
            "ontology-paragraph",
            package.source_version_id,
            paragraph_id,
        )
        paragraph_ids[paragraph_id] = paragraph_root_id
        section = roots[section_root_id]
        paragraph = _root(
            roots,
            root_id=paragraph_root_id,
            class_iri=POLICY_PARAGRAPH_CLASS,
            root_kind="ontology_paragraph",
        )
        evidence_ref = stable_id(
            "ontology-structure-evidence",
            package.source_version_id,
            "paragraph",
            paragraph_id,
        )
        _add_iri(
            section,
            package,
            predicate_iri=FAA_ORDER_NAMESPACE + "hasParagraph",
            object_id=paragraph_root_id,
            object_class_iri=POLICY_PARAGRAPH_CLASS,
            object_label=paragraph_id,
            evidence_ref=evidence_ref,
            char_start=chunk.parent_char_start,
            char_end=chunk.parent_char_end,
        )
        for predicate, value in (
            (RDFS_LABEL, f"{paragraph_id} {chunk.heading}"),
            (FAA_ORDER_NAMESPACE + "paragraphNumber", paragraph_id),
            (FAA_ORDER_NAMESPACE + "pageNumber", str(chunk.page_number)),
            (FAA_ORDER_NAMESPACE + "heading", chunk.heading),
            (FAA_ORDER_NAMESPACE + "topic", chunk.topic),
        ):
            _add_literal(
                paragraph,
                package,
                predicate_iri=predicate,
                value=value,
                evidence_ref=evidence_ref,
                char_start=chunk.parent_char_start,
                char_end=chunk.parent_char_end,
            )
    return paragraph_ids


def _candidate_roots(
    package: FAAOrderSourcePackage,
    subgraphs: tuple[CandidateKnowledgeSubgraph, ...],
    paragraph_ids: dict[str, str],
    roots: dict[str, _RootAccumulator],
) -> None:
    entities_by_id = {
        entity.entity_id: entity for subgraph in subgraphs for entity in subgraph.entities
    }
    for subgraph in subgraphs:
        paragraph = roots[paragraph_ids[subgraph.paragraph_id]]
        for entity in subgraph.entities:
            entity_root = _root(
                roots,
                root_id=entity.entity_id,
                class_iri=entity.class_iri,
                root_kind="ontology_entity",
            )
            evidence_ref = stable_id(
                "ontology-entity-evidence",
                entity.entity_id,
                entity.char_start,
                entity.char_end,
            )
            _add_literal(
                entity_root,
                package,
                predicate_iri=RDFS_LABEL,
                value=entity.canonical_label,
                evidence_ref=evidence_ref,
                char_start=entity.char_start,
                char_end=entity.char_end,
            )
            mention_predicate = (
                FAA_ORDER_NAMESPACE + "hasRule"
                if entity.class_iri == POLICY_RULE_CLASS
                else FAA_ORDER_NAMESPACE + "mentionsEntity"
            )
            _add_iri(
                paragraph,
                package,
                predicate_iri=mention_predicate,
                object_id=entity.entity_id,
                object_class_iri=entity.class_iri,
                object_label=entity.canonical_label,
                evidence_ref=evidence_ref,
                char_start=entity.char_start,
                char_end=entity.char_end,
            )
        for relation in subgraph.relations:
            if relation.quote_char_start is None or relation.quote_char_end is None:
                continue
            subject = entities_by_id.get(relation.subject_id)
            object_ = entities_by_id.get(relation.object_id)
            if subject is None or object_ is None:
                continue
            subject_root = _root(
                roots,
                root_id=subject.entity_id,
                class_iri=subject.class_iri,
                root_kind="ontology_entity",
            )
            evidence_ref = stable_id(
                "ontology-relation-evidence",
                relation.subject_id,
                relation.predicate_iri,
                relation.object_id,
                relation.quote_char_start,
                relation.quote_char_end,
            )
            _add_iri(
                subject_root,
                package,
                predicate_iri=relation.predicate_iri,
                object_id=object_.entity_id,
                object_class_iri=object_.class_iri,
                object_label=object_.canonical_label,
                evidence_ref=evidence_ref,
                char_start=relation.quote_char_start,
                char_end=relation.quote_char_end,
            )


def publish_faa_order_subgraphs(
    package: FAAOrderSourcePackage,
    store: object,
    *,
    chunks: tuple[FAAOrderExtractionChunk, ...],
    subgraphs: tuple[CandidateKnowledgeSubgraph, ...],
    profile_registry: ValidationProfileRegistry,
) -> FAAOrderPublicationSummary:
    """Validate and apply document structure plus accepted candidate ABox."""

    if not chunks:
        return FAAOrderPublicationSummary(
            status="insufficient",
            publication_ids=(),
            accepted_root_count=0,
            blocked_root_count=0,
            reasons=("no document extraction chunks were selected",),
        )
    roots: dict[str, _RootAccumulator] = {}
    paragraph_ids = _structure_roots(package, chunks, roots)
    _candidate_roots(
        package,
        subgraphs,
        paragraph_ids,
        roots,
    )
    publication_ids: list[str] = []
    reasons: list[str] = []
    blocked = 0
    published_fact_count = 0
    published_evidence_link_count = 0
    for root_id in sorted(roots):
        root = roots[root_id]
        if not root.facts:
            continue
        evidence_bindings = tuple(root.bindings[key] for key in sorted(root.bindings))
        evidence = evidence_bindings[0]
        task = OntologyGenerationTask(
            task_id=stable_id(
                "ontology-publication-task",
                package.source_version_id,
                root_id,
            ),
            generation_stage="candidate_subgraph_publication",
            root_id=root_id,
            temporal_domain_id="faa-jo-7210.3ee:2025-02-20",
            ontology_slice=build_faa_order_ontology_slice(
                subject_class_iri=root.class_iri,
                candidate_object_class_iris=tuple(
                    sorted({entity.class_iri for entity in root.candidate_entities.values()})
                ),
            ),
            evidence_cards=(
                EvidenceCard(
                    agent_role="document",
                    status=AgentStatus.RESOLVED,
                    claims=[
                        EvidenceClaim(
                            field_name="document_knowledge",
                            value=root_id,
                            evidence_text=evidence.evidence_text,
                            source_id=evidence.source_id,
                            canonical_ref=evidence.evidence_ref,
                        )
                    ],
                    source_ids=[evidence.source_id],
                    decision_basis="deterministic candidate-subgraph mapping",
                ),
            ),
            evidence_bindings=evidence_bindings,
            candidate_entities=tuple(
                root.candidate_entities[key] for key in sorted(root.candidate_entities)
            ),
        )
        proposal = CandidateFactProposal(
            status="accepted",
            facts=tuple(
                sorted(
                    root.facts,
                    key=lambda row: (
                        row.predicate_iri,
                        row.object_kind,
                        row.object_value,
                        row.evidence_ref,
                    ),
                )
            ),
        )
        result = validate_and_prepare_generated_publication(
            task=task,
            proposal=proposal,
            profile_registry=profile_registry,
            source_versions=(package.source_version,),
            primary_source_version_id=package.source_version_id,
            root_kind=root.root_kind,
        )
        if result.status != "ok":
            blocked += 1
            reasons.append(result.reason or f"publication blocked for {root_id}")
            continue
        assert result.package is not None
        apply_generated_publication(
            store,
            result,
            (package.source_version,),
        )
        publication_ids.append(result.package.publication.publication_id)
        published_fact_count += len(result.package.facts)
        published_evidence_link_count += len(result.package.evidence_links)
    return FAAOrderPublicationSummary(
        status="blocked" if blocked else ("ok" if publication_ids else "insufficient"),
        publication_ids=tuple(publication_ids),
        accepted_root_count=len(publication_ids),
        blocked_root_count=blocked,
        published_fact_count=published_fact_count,
        published_evidence_link_count=published_evidence_link_count,
        reasons=tuple(reasons),
    )


__all__ = [
    "FAAOrderPublicationSummary",
    "POLICY_DOCUMENT_CLASS",
    "POLICY_SECTION_CLASS",
    "publish_faa_order_subgraphs",
]
