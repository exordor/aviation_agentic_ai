"""Persistent incremental Chroma indexes over the SQLite evidence store."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
    SCHEMA_VERSION,
)
from aviation_agentic_ai.agent_system.source_retrieval import (
    SOURCE_CHUNK_REPRESENTATION_VERSION,
    build_source_record_chunks,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    SourceChunkRecord,
    SourceVersionRecord,
    VectorIndexStateRecord,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
    DEFAULT_TMI_EVENT_EMBEDDING_MODEL,
    REPRESENTATION_VERSION,
    TMIEventEncoder,
    TMIEventRetrievalDocument,
    TMIEventVectorHit,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_documents import (
    build_tmi_event_retrieval_document,
)
from aviation_agentic_ai.retrieval.chroma_store import (
    cosine_similarity,
    get_collection,
    get_or_create_collection,
    open_persistent_client,
    query_explicit_embeddings,
    recreate_collection,
    update_record_metadatas,
    upsert_explicit_embeddings,
)


TMI_EVENT_COLLECTION = "tmi_events_v1"
SOURCE_CHUNK_COLLECTION = "aviation_source_chunks_v1"
_DISTANCE_METRIC = "cosine"
_MISSING_COLLECTION_PHRASES = (
    "not found",
    "does not exist",
    "no collection",
    "nonexistent",
)


class SentenceTransformerTMIEventEncoder:
    """Lazy Sentence Transformers encoder shared by both vector views."""

    def __init__(
        self,
        model_name: str = DEFAULT_TMI_EVENT_EMBEDDING_MODEL,
        *,
        allow_download: bool = False,
    ) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_id = model_name
        self._model = SentenceTransformer(
            model_name,
            local_files_only=not allow_download,
        )

    def encode(
        self,
        texts: Sequence[str],
    ) -> Sequence[Sequence[float]]:
        vectors = self._model.encode(
            list(texts),
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [
            [float(value) for value in vector]
            for vector in vectors
        ]


@dataclass(frozen=True)
class SourceChunkVectorHit:
    """One source-vector result retaining its exact SQLite anchor."""

    chunk_id: str
    source_version_id: str
    source_anchor_id: str
    distance: float
    similarity: float


def _normalized_vectors(
    vectors: Sequence[Sequence[float]],
    *,
    expected_count: int,
) -> tuple[tuple[float, ...], ...]:
    if len(vectors) != expected_count:
        raise ValueError("encoder returned an unexpected vector count")
    normalized: list[tuple[float, ...]] = []
    dimension: int | None = None
    for vector in vectors:
        values = tuple(float(value) for value in vector)
        if dimension is None:
            dimension = len(values)
        if not values or len(values) != dimension:
            raise ValueError("encoder returned inconsistent vector dimensions")
        norm = math.sqrt(sum(value * value for value in values))
        if norm == 0:
            raise ValueError("encoder returned a zero-length vector")
        normalized.append(tuple(value / norm for value in values))
    return tuple(normalized)


def _collection_metadata(
    *,
    dataset_id: str,
    representation_version: str,
    embedding_model_id: str,
    embedding_dimension: int,
) -> dict[str, str | int]:
    return {
        "dataset_id": dataset_id,
        "evidence_store_schema_version": SCHEMA_VERSION,
        "representation_version": representation_version,
        "embedding_model_id": embedding_model_id,
        "embedding_dimension": embedding_dimension,
        "distance_metric": _DISTANCE_METRIC,
    }


def _get_collection_if_present(
    client: Any,
    collection_name: str,
) -> Any | None:
    try:
        return get_collection(
            client,
            collection_name,
            embedding_function=None,
        )
    except Exception as exc:
        if any(
            phrase in str(exc).lower()
            for phrase in _MISSING_COLLECTION_PHRASES
        ):
            return None
        raise


def _validate_collection_metadata(
    collection: Any,
    *,
    dataset_id: str,
    representation_version: str,
    embedding_model_id: str,
) -> int:
    metadata = collection.metadata or {}
    expected = {
        "dataset_id": dataset_id,
        "evidence_store_schema_version": SCHEMA_VERSION,
        "representation_version": representation_version,
        "embedding_model_id": embedding_model_id,
        "distance_metric": _DISTANCE_METRIC,
    }
    if any(metadata.get(key) != value for key, value in expected.items()):
        raise ValueError(
            "vector collection metadata changed; run a full reindex"
        )
    dimension = metadata.get("embedding_dimension")
    if not isinstance(dimension, int) or dimension < 1:
        raise ValueError("vector collection dimension is invalid")
    return dimension


def _record_ids(collection: Any) -> set[str]:
    return set(collection.get(include=[])["ids"])


def _patch_active_metadata(
    collection: Any,
    *,
    active_identity_field: str,
    active_identity_ids: set[str],
) -> None:
    payload = collection.get(include=["metadatas"])
    ids = payload.get("ids") or []
    metadatas = payload.get("metadatas") or []
    if not ids:
        return
    revised = []
    for metadata in metadatas:
        values = dict(metadata or {})
        values["active"] = (
            values.get(active_identity_field) in active_identity_ids
        )
        revised.append(values)
    update_record_metadatas(
        collection,
        ids=ids,
        metadatas=revised,
    )


def _sync_collection(
    *,
    client: Any,
    dataset_id: str,
    collection_name: str,
    representation_version: str,
    encoder: TMIEventEncoder,
    record_ids: Sequence[str],
    texts: Sequence[str],
    metadatas: Sequence[dict[str, str | bool]],
    active_identity_field: str,
    active_identity_ids: set[str],
    full_reindex: bool,
) -> tuple[Any, int]:
    if not record_ids:
        raise ValueError(
            f"no documents are available for {collection_name}"
        )
    collection = (
        None
        if full_reindex
        else _get_collection_if_present(client, collection_name)
    )
    existing_dimension = (
        _validate_collection_metadata(
            collection,
            dataset_id=dataset_id,
            representation_version=representation_version,
            embedding_model_id=encoder.model_id,
        )
        if collection is not None
        else None
    )
    existing_ids = _record_ids(collection) if collection is not None else set()
    missing_positions = [
        index
        for index, record_id in enumerate(record_ids)
        if record_id not in existing_ids
    ]
    vectors: tuple[tuple[float, ...], ...] = ()
    if missing_positions:
        vectors = _normalized_vectors(
            encoder.encode([texts[index] for index in missing_positions]),
            expected_count=len(missing_positions),
        )
    dimension = (
        len(vectors[0])
        if vectors
        else existing_dimension
    )
    if dimension is None:
        raise ValueError("vector collection dimension is unavailable")
    if existing_dimension is not None and dimension != existing_dimension:
        raise ValueError("encoder vector dimension changed; run a full reindex")
    metadata = _collection_metadata(
        dataset_id=dataset_id,
        representation_version=representation_version,
        embedding_model_id=encoder.model_id,
        embedding_dimension=dimension,
    )
    if full_reindex:
        collection = recreate_collection(
            client,
            collection_name,
            embedding_function=None,
            configuration={"hnsw": {"space": _DISTANCE_METRIC}},
            metadata=metadata,
        )
        missing_positions = list(range(len(record_ids)))
    elif collection is None:
        collection = get_or_create_collection(
            client,
            collection_name,
            embedding_function=None,
            configuration={"hnsw": {"space": _DISTANCE_METRIC}},
            metadata=metadata,
        )
    if missing_positions:
        upsert_explicit_embeddings(
            collection,
            ids=[record_ids[index] for index in missing_positions],
            embeddings=vectors,
            documents=[texts[index] for index in missing_positions],
            metadatas=[metadatas[index] for index in missing_positions],
        )
    _patch_active_metadata(
        collection,
        active_identity_field=active_identity_field,
        active_identity_ids=active_identity_ids,
    )
    return collection, dimension


def _event_metadata(
    document: TMIEventRetrievalDocument,
    *,
    active: bool,
) -> dict[str, str | bool]:
    return {
        "event_id": document.event_id,
        "publication_id": document.publication_id,
        "advisory_source_id": document.advisory_source_id,
        "publication_source_version_id": (
            document.publication_source_version_id
        ),
        "active": active,
    }


def _source_metadata(
    chunk: SourceChunkRecord,
    version: SourceVersionRecord,
    *,
    active: bool,
) -> dict[str, str | bool]:
    metadata: dict[str, str | bool] = {
        "chunk_id": chunk.chunk_id,
        "source_version_id": chunk.source_version_id,
        "source_anchor_id": chunk.source_anchor_id,
        "source_id": version.source_id,
        "source_family": version.family.value,
        "active": active,
    }
    if chunk.event_id is not None:
        metadata["event_id"] = chunk.event_id
    return metadata


def _selected_event_documents(
    store: AviationEvidenceStore,
    *,
    publication_ids: Sequence[str],
    full_reindex: bool,
) -> tuple[
    tuple[TMIEventRetrievalDocument, ...],
    set[str],
]:
    active_events = store.list_tmi_event_publications(active_only=True)
    active_publication_ids = {
        event.publication_id for event in active_events
    }
    all_events = store.list_tmi_event_publications()
    event_by_publication = {
        event.publication_id: event for event in all_events
    }
    unknown = set(publication_ids) - set(event_by_publication)
    if unknown:
        raise ValueError(
            "unknown event publication IDs: " + ", ".join(sorted(unknown))
        )
    selected_publication_ids = (
        set(event_by_publication)
        if full_reindex
        else active_publication_ids | set(publication_ids)
    )
    documents = tuple(
        build_tmi_event_retrieval_document(
            store,
            event_by_publication[publication_id],
        )
        for publication_id in sorted(selected_publication_ids)
    )
    return documents, active_publication_ids


def _selected_source_chunks(
    store: AviationEvidenceStore,
    *,
    source_version_ids: Sequence[str],
    full_reindex: bool,
) -> tuple[
    tuple[SourceChunkRecord, ...],
    dict[str, SourceVersionRecord],
    set[str],
]:
    all_versions = store.list_source_versions()
    version_by_id = {
        version.source_version_id: version for version in all_versions
    }
    unknown = set(source_version_ids) - set(version_by_id)
    if unknown:
        raise ValueError(
            "unknown source version IDs: " + ", ".join(sorted(unknown))
        )
    current_version_ids = {
        version.source_version_id
        for version in store.list_source_versions(current_only=True)
    }
    selected_version_ids = (
        set(version_by_id)
        if full_reindex
        else current_version_ids | set(source_version_ids)
    )
    selected_versions = tuple(
        version_by_id[source_version_id]
        for source_version_id in sorted(selected_version_ids)
    )
    chunks = build_source_record_chunks(selected_versions)
    store.upsert_source_chunks(chunks)
    active_chunk_version_ids = {
        chunk.source_version_id
        for chunk in build_source_record_chunks(
            tuple(
                version_by_id[source_version_id]
                for source_version_id in sorted(current_version_ids)
            )
        )
    }
    return chunks, version_by_id, active_chunk_version_ids


def _state(
    *,
    collection_name: str,
    representation_version: str,
    encoder_model_id: str,
    dimension: int,
    knowledge_revision: int,
    document_count: int,
    vector_count: int,
    status: str = "current",
    failure_reason: str | None = None,
) -> VectorIndexStateRecord:
    return VectorIndexStateRecord(
        collection_name=collection_name,
        representation_version=representation_version,
        embedding_model_id=encoder_model_id,
        embedding_dimension=dimension,
        indexed_knowledge_revision=knowledge_revision,
        document_count=document_count,
        vector_count=vector_count,
        status=status,
        updated_at=datetime.now(UTC),
        failure_reason=failure_reason,
    )


def mark_vector_indexes_blocked(
    store: AviationEvidenceStore,
    *,
    embedding_model_id: str,
    reason: str,
) -> tuple[VectorIndexStateRecord, ...]:
    """Record a vector failure, including before a dimension is known."""

    states: list[VectorIndexStateRecord] = []
    for collection_name, representation_version in (
        (TMI_EVENT_COLLECTION, REPRESENTATION_VERSION),
        (
            SOURCE_CHUNK_COLLECTION,
            SOURCE_CHUNK_REPRESENTATION_VERSION,
        ),
    ):
        existing = store.get_vector_index_state(collection_name)
        same_model = (
            existing is not None
            and existing.embedding_model_id == embedding_model_id
        )
        state = _state(
            collection_name=collection_name,
            representation_version=representation_version,
            encoder_model_id=embedding_model_id,
            dimension=existing.embedding_dimension if same_model else 0,
            knowledge_revision=store.get_knowledge_revision(),
            document_count=existing.document_count if existing else 0,
            vector_count=existing.vector_count if existing else 0,
            status="blocked",
            failure_reason=reason,
        )
        store.set_vector_index_state(state)
        states.append(state)
    return tuple(states)


def _update_store_indexes(
    store: AviationEvidenceStore,
    chroma_dir: str | Path,
    *,
    encoder: TMIEventEncoder,
    source_version_ids: Sequence[str],
    event_publication_ids: Sequence[str],
    full_reindex: bool,
) -> tuple[VectorIndexStateRecord, ...]:
    client = open_persistent_client(chroma_dir)
    documents, active_publication_ids = _selected_event_documents(
        store,
        publication_ids=event_publication_ids,
        full_reindex=full_reindex,
    )
    chunks, version_by_id, active_source_version_ids = (
        _selected_source_chunks(
            store,
            source_version_ids=source_version_ids,
            full_reindex=full_reindex,
        )
    )
    event_collection = None
    event_dimension = 0
    if documents:
        event_collection, event_dimension = _sync_collection(
            client=client,
            dataset_id=store.dataset_id,
            collection_name=TMI_EVENT_COLLECTION,
            representation_version=REPRESENTATION_VERSION,
            encoder=encoder,
            record_ids=[document.document_id for document in documents],
            texts=[document.text for document in documents],
            metadatas=[
                _event_metadata(
                    document,
                    active=(
                        document.publication_id in active_publication_ids
                    ),
                )
                for document in documents
            ],
            active_identity_field="publication_id",
            active_identity_ids=active_publication_ids,
            full_reindex=full_reindex,
        )
    source_collection = None
    source_dimension = 0
    if chunks:
        source_collection, source_dimension = _sync_collection(
            client=client,
            dataset_id=store.dataset_id,
            collection_name=SOURCE_CHUNK_COLLECTION,
            representation_version=SOURCE_CHUNK_REPRESENTATION_VERSION,
            encoder=encoder,
            record_ids=[chunk.chunk_id for chunk in chunks],
            texts=[chunk.text for chunk in chunks],
            metadatas=[
                _source_metadata(
                    chunk,
                    version_by_id[chunk.source_version_id],
                    active=(
                        chunk.source_version_id
                        in active_source_version_ids
                    ),
                )
                for chunk in chunks
            ],
            active_identity_field="source_version_id",
            active_identity_ids=active_source_version_ids,
            full_reindex=full_reindex,
        )
    knowledge_revision = store.get_knowledge_revision()
    known_dimension = event_dimension or source_dimension
    states = (
        _state(
            collection_name=TMI_EVENT_COLLECTION,
            representation_version=REPRESENTATION_VERSION,
            encoder_model_id=encoder.model_id,
            dimension=event_dimension or known_dimension,
            knowledge_revision=knowledge_revision,
            document_count=len(active_publication_ids),
            vector_count=(
                int(event_collection.count())
                if event_collection is not None
                else 0
            ),
            status=(
                "current" if event_collection is not None else "blocked"
            ),
            failure_reason=(
                None
                if event_collection is not None
                else "no accepted TMI event publications are available"
            ),
        ),
        _state(
            collection_name=SOURCE_CHUNK_COLLECTION,
            representation_version=SOURCE_CHUNK_REPRESENTATION_VERSION,
            encoder_model_id=encoder.model_id,
            dimension=source_dimension or known_dimension,
            knowledge_revision=knowledge_revision,
            document_count=len(active_source_version_ids),
            vector_count=(
                int(source_collection.count())
                if source_collection is not None
                else 0
            ),
            status=(
                "current" if source_collection is not None else "blocked"
            ),
            failure_reason=(
                None
                if source_collection is not None
                else "no textual source versions are available"
            ),
        ),
    )
    for state in states:
        store.set_vector_index_state(state)
    return states


def update_store_indexes(
    store: AviationEvidenceStore,
    chroma_dir: str | Path,
    *,
    encoder: TMIEventEncoder,
    source_version_ids: Sequence[str] = (),
    event_publication_ids: Sequence[str] = (),
) -> tuple[VectorIndexStateRecord, ...]:
    """Incrementally synchronize active and explicitly changed store rows."""

    try:
        return _update_store_indexes(
            store,
            chroma_dir,
            encoder=encoder,
            source_version_ids=source_version_ids,
            event_publication_ids=event_publication_ids,
            full_reindex=False,
        )
    except Exception as exc:
        mark_vector_indexes_blocked(
            store,
            embedding_model_id=encoder.model_id,
            reason=str(exc),
        )
        raise


def reindex_store(
    store: AviationEvidenceStore,
    chroma_dir: str | Path,
    *,
    encoder: TMIEventEncoder,
) -> tuple[VectorIndexStateRecord, ...]:
    """Explicitly recreate both collections from all immutable store rows."""

    try:
        return _update_store_indexes(
            store,
            chroma_dir,
            encoder=encoder,
            source_version_ids=(),
            event_publication_ids=(),
            full_reindex=True,
        )
    except Exception as exc:
        mark_vector_indexes_blocked(
            store,
            embedding_model_id=encoder.model_id,
            reason=str(exc),
        )
        raise


class _ValidatedChromaIndex:
    def __init__(
        self,
        store: AviationEvidenceStore,
        chroma_dir: str | Path,
        *,
        collection_name: str,
        representation_version: str,
        embedding_model_id: str | None = None,
    ) -> None:
        state = store.get_vector_index_state(collection_name)
        if state is None:
            raise ValueError(f"vector index state is missing: {collection_name}")
        if state.status != "current":
            raise ValueError(
                f"vector index is not current: {collection_name}"
            )
        if state.indexed_knowledge_revision != store.get_knowledge_revision():
            raise ValueError(
                f"vector index is stale: {collection_name}"
            )
        if state.representation_version != representation_version:
            raise ValueError("vector index representation version mismatch")
        if (
            embedding_model_id is not None
            and state.embedding_model_id != embedding_model_id
        ):
            raise ValueError("vector index embedding model mismatch")
        collection = get_collection(
            open_persistent_client(chroma_dir),
            collection_name,
            embedding_function=None,
        )
        dimension = _validate_collection_metadata(
            collection,
            dataset_id=store.dataset_id,
            representation_version=state.representation_version,
            embedding_model_id=state.embedding_model_id,
        )
        if dimension != state.embedding_dimension:
            raise ValueError("vector index dimension mismatch")
        if int(collection.count()) != state.vector_count:
            raise ValueError("vector index count mismatch")
        self.store = store
        self.state = state
        self.collection = collection


class ChromaTMIEventRetrievalIndex(_ValidatedChromaIndex):
    """Validated read-only view of active and historical TMI publications."""

    def __init__(
        self,
        store: AviationEvidenceStore,
        chroma_dir: str | Path,
    ) -> None:
        super().__init__(
            store,
            chroma_dir,
            collection_name=TMI_EVENT_COLLECTION,
            representation_version=REPRESENTATION_VERSION,
        )

    def get_publication_vector(
        self,
        publication_id: str,
    ) -> tuple[float, ...]:
        """Return one stored publication vector, including historical rows."""

        result = self.collection.get(
            where={"publication_id": publication_id},
            include=["embeddings"],
        )
        ids = result.get("ids") or []
        embeddings = result.get("embeddings")
        if len(ids) != 1 or embeddings is None or len(embeddings) != 1:
            raise ValueError(
                f"TMI event publication is not indexed: {publication_id}"
            )
        vector = tuple(float(value) for value in embeddings[0])
        if len(vector) != self.state.embedding_dimension:
            raise ValueError("TMI-event vector dimension mismatch")
        return vector

    def query_candidates(
        self,
        *,
        query_vector: Sequence[float],
        candidate_publication_ids: Sequence[str],
        n_results: int,
    ) -> tuple[TMIEventVectorHit, ...]:
        """Query vectors inside the caller's exact publication whitelist."""

        candidate_ids = sorted(set(candidate_publication_ids))
        if not candidate_ids:
            return ()
        if n_results < 1:
            raise ValueError("n_results must be positive")
        if len(query_vector) != self.state.embedding_dimension:
            raise ValueError("query vector dimension mismatch")
        result = query_explicit_embeddings(
            self.collection,
            query_embedding=query_vector,
            where={"publication_id": {"$in": candidate_ids}},
            n_results=min(n_results, len(candidate_ids)),
        )
        ids = (result.get("ids") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        hits: list[TMIEventVectorHit] = []
        for index, _record_id in enumerate(ids):
            metadata = metadatas[index]
            distance = float(distances[index])
            hits.append(
                TMIEventVectorHit(
                    event_id=str(metadata["event_id"]),
                    publication_id=str(metadata["publication_id"]),
                    advisory_source_id=str(
                        metadata["advisory_source_id"]
                    ),
                    distance=distance,
                    similarity=cosine_similarity(distance),
                )
            )
        return tuple(hits)


class ChromaSourceRetrievalIndex(_ValidatedChromaIndex):
    """Validated source-semantic reader bounded by exact version IDs."""

    def __init__(
        self,
        store: AviationEvidenceStore,
        chroma_dir: str | Path,
        encoder: TMIEventEncoder,
    ) -> None:
        super().__init__(
            store,
            chroma_dir,
            collection_name=SOURCE_CHUNK_COLLECTION,
            representation_version=SOURCE_CHUNK_REPRESENTATION_VERSION,
            embedding_model_id=encoder.model_id,
        )
        self.encoder = encoder

    def query_chunks(
        self,
        *,
        query_text: str,
        candidate_source_version_ids: Sequence[str],
        n_results: int,
    ) -> tuple[SourceChunkVectorHit, ...]:
        """Rank chunks only inside the caller's exact source-version scope."""

        if not query_text.strip():
            raise ValueError("source vector query must not be empty")
        candidate_ids = sorted(set(candidate_source_version_ids))
        if not candidate_ids:
            return ()
        if n_results < 1:
            raise ValueError("n_results must be positive")
        query_vector = _normalized_vectors(
            self.encoder.encode([query_text]),
            expected_count=1,
        )[0]
        if len(query_vector) != self.state.embedding_dimension:
            raise ValueError("query vector dimension mismatch")
        result = query_explicit_embeddings(
            self.collection,
            query_embedding=query_vector,
            where={"source_version_id": {"$in": candidate_ids}},
            n_results=min(n_results, len(candidate_ids)),
        )
        ids = (result.get("ids") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        return tuple(
            SourceChunkVectorHit(
                chunk_id=str(metadatas[index]["chunk_id"]),
                source_version_id=str(
                    metadatas[index]["source_version_id"]
                ),
                source_anchor_id=str(
                    metadatas[index]["source_anchor_id"]
                ),
                distance=float(distances[index]),
                similarity=cosine_similarity(float(distances[index])),
            )
            for index, _record_id in enumerate(ids)
        )
