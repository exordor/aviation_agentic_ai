"""Rebuildable semantic discovery index for ontology-extracted entities."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
    TMIEventEncoder,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_index import (
    _ValidatedChromaIndex,
    _normalized_vectors,
    _state,
    _sync_collection,
)
from aviation_agentic_ai.agent_system.chroma_store import (
    cosine_similarity,
    open_persistent_client,
    query_explicit_embeddings,
)
from aviation_agentic_ai.utils.identifiers import stable_id


KNOWLEDGE_ENTITY_COLLECTION = "knowledge_entities_v1"
KNOWLEDGE_ENTITY_REPRESENTATION_VERSION = "knowledge-entity-representation-v1"
RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"


@dataclass(frozen=True)
class KnowledgeEntityRetrievalDocument:
    """One evidence-bound representation of an ontology-extracted entity."""

    document_id: str
    root_id: str
    publication_id: str
    class_iri: str
    label: str
    aliases: tuple[str, ...]
    source_version_ids: tuple[str, ...]
    source_anchor_ids: tuple[str, ...]
    text: str


@dataclass(frozen=True)
class KnowledgeEntityVectorHit:
    """One semantic candidate; exact facts must still be read from SQLite."""

    root_id: str
    publication_id: str
    class_iri: str
    label: str
    distance: float
    similarity: float


def _local_name(value: str) -> str:
    return value.rsplit("#", 1)[-1].rsplit("/", 1)[-1].rsplit(":", 1)[-1]


def build_knowledge_entity_retrieval_documents(
    store: AviationEvidenceStore,
) -> tuple[KnowledgeEntityRetrievalDocument, ...]:
    """Compile extracted entities without treating vectors as authority."""

    grouped: dict[str, list[object]] = {}
    for binding in store.list_active_formal_fact_bindings():
        if binding.root_kind == "ontology_entity":
            grouped.setdefault(binding.root_id, []).append(binding)
    documents: list[KnowledgeEntityRetrievalDocument] = []
    for root_id, raw_bindings in sorted(grouped.items()):
        bindings = tuple(raw_bindings)
        first = bindings[0]
        class_iri = first.fact.subject_class_iri
        class_label = _local_name(class_iri)
        aliases: tuple[str, ...] = ()
        label = next(
            (
                binding.fact.object_value
                for binding in bindings
                if binding.fact.predicate_iri == RDFS_LABEL
                and binding.fact.object_kind == "literal"
            ),
            class_label,
        )
        relation_rows = tuple(
            sorted(
                {
                    f"{_local_name(binding.fact.predicate_iri)} -> "
                    f"{_local_name(binding.fact.object_value)}"
                    for binding in bindings
                    if binding.fact.predicate_iri != RDFS_LABEL
                }
            )
        )
        source_version_ids = tuple(
            sorted(
                {
                    link.source_version_id
                    for binding in bindings
                    for link in binding.evidence_links
                }
            )
        )
        source_anchor_ids = tuple(
            sorted(
                {
                    link.source_anchor_id
                    for binding in bindings
                    for link in binding.evidence_links
                    if link.source_anchor_id is not None
                }
            )
        )
        evidence_refs = tuple(
            sorted(
                {
                    link.evidence_ref
                    for binding in bindings
                    for link in binding.evidence_links
                }
            )
        )
        text = "\n".join(
            row
            for row in (
                f"Entity: {label}",
                f"Class: {class_label} ({class_iri})",
                f"Aliases: {', '.join(aliases)}" if aliases else "",
                "Relations: " + "; ".join(relation_rows)
                if relation_rows
                else "",
                "Source paragraphs: " + "; ".join(evidence_refs)
                if evidence_refs
                else "",
            )
            if row
        )
        documents.append(
            KnowledgeEntityRetrievalDocument(
                document_id=stable_id(
                    "knowledge-entity-vector",
                    root_id,
                    first.publication_id,
                    KNOWLEDGE_ENTITY_REPRESENTATION_VERSION,
                ),
                root_id=root_id,
                publication_id=first.publication_id,
                class_iri=class_iri,
                label=label,
                aliases=aliases,
                source_version_ids=source_version_ids,
                source_anchor_ids=source_anchor_ids,
                text=text,
            )
        )
    return tuple(documents)


def reindex_knowledge_entities(
    store: AviationEvidenceStore,
    chroma_dir: str | Path,
    *,
    encoder: TMIEventEncoder,
):
    """Recreate the knowledge entity collection at the current store revision."""

    documents = build_knowledge_entity_retrieval_documents(store)
    revision = store.get_knowledge_revision()
    if not documents:
        state = _state(
            collection_name=KNOWLEDGE_ENTITY_COLLECTION,
            representation_version=KNOWLEDGE_ENTITY_REPRESENTATION_VERSION,
            encoder_model_id=encoder.model_id,
            dimension=0,
            knowledge_revision=revision,
            document_count=0,
            vector_count=0,
            status="blocked",
            failure_reason="no active ontology-extracted entities are available",
        )
        store.set_vector_index_state(state)
        return state
    try:
        client = open_persistent_client(chroma_dir)
        collection, dimension = _sync_collection(
            client=client,
            dataset_id=store.dataset_id,
            collection_name=KNOWLEDGE_ENTITY_COLLECTION,
            representation_version=KNOWLEDGE_ENTITY_REPRESENTATION_VERSION,
            encoder=encoder,
            record_ids=[document.document_id for document in documents],
            texts=[document.text for document in documents],
            metadatas=[
                {
                    "root_id": document.root_id,
                    "publication_id": document.publication_id,
                    "class_iri": document.class_iri,
                    "label": document.label,
                    "active": True,
                }
                for document in documents
            ],
            active_identity_field="root_id",
            active_identity_ids={document.root_id for document in documents},
            full_reindex=True,
        )
        state = _state(
            collection_name=KNOWLEDGE_ENTITY_COLLECTION,
            representation_version=KNOWLEDGE_ENTITY_REPRESENTATION_VERSION,
            encoder_model_id=encoder.model_id,
            dimension=dimension,
            knowledge_revision=revision,
            document_count=len(documents),
            vector_count=int(collection.count()),
        )
    except Exception as exc:
        state = _state(
            collection_name=KNOWLEDGE_ENTITY_COLLECTION,
            representation_version=KNOWLEDGE_ENTITY_REPRESENTATION_VERSION,
            encoder_model_id=encoder.model_id,
            dimension=0,
            knowledge_revision=revision,
            document_count=len(documents),
            vector_count=0,
            status="blocked",
            failure_reason=str(exc),
        )
        store.set_vector_index_state(state)
        raise
    store.set_vector_index_state(state)
    return state


class ChromaKnowledgeEntityRetrievalIndex(_ValidatedChromaIndex):
    """Validated reader for semantic discovery over extracted entities."""

    def __init__(
        self,
        store: AviationEvidenceStore,
        chroma_dir: str | Path,
        encoder: TMIEventEncoder,
    ) -> None:
        super().__init__(
            store,
            chroma_dir,
            collection_name=KNOWLEDGE_ENTITY_COLLECTION,
            representation_version=KNOWLEDGE_ENTITY_REPRESENTATION_VERSION,
            embedding_model_id=encoder.model_id,
        )
        self.encoder = encoder

    def query_entities(
        self,
        *,
        query_text: str,
        candidate_root_ids: Sequence[str],
        n_results: int,
    ) -> tuple[KnowledgeEntityVectorHit, ...]:
        if not query_text.strip():
            raise ValueError("knowledge entity vector query must not be empty")
        root_ids = sorted(set(candidate_root_ids))
        if not root_ids:
            return ()
        if n_results < 1:
            raise ValueError("n_results must be positive")
        query_vector = _normalized_vectors(
            self.encoder.encode([query_text]),
            expected_count=1,
        )[0]
        result = query_explicit_embeddings(
            self.collection,
            query_embedding=query_vector,
            where={"root_id": {"$in": root_ids}},
            n_results=min(n_results, len(root_ids)),
        )
        ids = (result.get("ids") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        return tuple(
            KnowledgeEntityVectorHit(
                root_id=str(metadatas[index]["root_id"]),
                publication_id=str(metadatas[index]["publication_id"]),
                class_iri=str(metadatas[index]["class_iri"]),
                label=str(metadatas[index]["label"]),
                distance=float(distances[index]),
                similarity=cosine_similarity(float(distances[index])),
            )
            for index, _record_id in enumerate(ids)
        )


__all__ = [
    "KNOWLEDGE_ENTITY_COLLECTION",
    "KNOWLEDGE_ENTITY_REPRESENTATION_VERSION",
    "ChromaKnowledgeEntityRetrievalIndex",
    "KnowledgeEntityRetrievalDocument",
    "KnowledgeEntityVectorHit",
    "build_knowledge_entity_retrieval_documents",
    "reindex_knowledge_entities",
]
