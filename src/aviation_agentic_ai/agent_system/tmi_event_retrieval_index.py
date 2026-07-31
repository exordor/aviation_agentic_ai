"""Persistent Chroma sidecar for deterministic TMI-event documents."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Sequence

from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
    DEFAULT_TMI_EVENT_EMBEDDING_MODEL,
    REPRESENTATION_VERSION,
    TMIEventDocumentArtifact,
    TMIEventEncoder,
    TMIEventIndexManifest,
    TMIEventRetrievalDocument,
    TMIEventVectorHit,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_documents import (
    build_tmi_event_retrieval_documents,
)
from aviation_agentic_ai.agent_system.corpus_store import CorpusQueryStore
from aviation_agentic_ai.retrieval.chroma_store import (
    cosine_similarity,
    get_collection,
    get_stored_embedding,
    open_persistent_client,
    query_explicit_embeddings,
    recreate_collection,
    upsert_explicit_embeddings,
)


TMI_EVENT_INDEX_MANIFEST = "tmi_event_index_manifest.json"
TMI_EVENT_DOCUMENTS = "tmi_event_documents.jsonl"
TMI_EVENT_COLLECTION = "tmi_events"


class SentenceTransformerTMIEventEncoder:
    """Lazy Sentence Transformers encoder for canonical event documents."""

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


def _write_documents(
    path: Path,
    documents: Sequence[TMIEventRetrievalDocument],
) -> TMIEventDocumentArtifact:
    data = "".join(
        document.model_dump_json() + "\n"
        for document in documents
    ).encode("utf-8")
    path.write_bytes(data)
    return TMIEventDocumentArtifact(
        path=path.name,
        count=len(documents),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def build_tmi_event_retrieval_index(
    corpus_dir: str | Path,
    *,
    encoder: TMIEventEncoder,
    index_dir: str | Path | None = None,
) -> TMIEventIndexManifest:
    """Rebuild one persistent event-vector sidecar and publish its manifest."""

    store = CorpusQueryStore(corpus_dir)
    documents = build_tmi_event_retrieval_documents(store)
    if not documents:
        raise ValueError("corpus has no accepted TMI events to index")
    root = Path(index_dir or (store.root / "tmi_event_index"))
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / TMI_EVENT_INDEX_MANIFEST
    manifest_path.unlink(missing_ok=True)

    vectors = _normalized_vectors(
        encoder.encode([document.text for document in documents]),
        expected_count=len(documents),
    )
    dimension = len(vectors[0])
    document_artifact = _write_documents(
        root / TMI_EVENT_DOCUMENTS,
        documents,
    )
    collection_metadata: dict[str, str | int | float | bool] = {
        "corpus_id": store.manifest.corpus_id,
        "representation_version": REPRESENTATION_VERSION,
        "embedding_model_id": encoder.model_id,
        "embedding_dimension": dimension,
        "distance_metric": "cosine",
    }
    collection = recreate_collection(
        open_persistent_client(root / "chroma"),
        TMI_EVENT_COLLECTION,
        embedding_function=None,
        configuration={"hnsw": {"space": "cosine"}},
        metadata=collection_metadata,
    )
    upsert_explicit_embeddings(
        collection,
        ids=[document.document_id for document in documents],
        embeddings=vectors,
        documents=[document.text for document in documents],
        metadatas=[
            {
                "event_id": document.event_id,
                "advisory_source_id": document.advisory_source_id,
            }
            for document in documents
        ],
    )
    vector_count = int(collection.count())
    if vector_count != len(documents):
        raise ValueError("TMI-event vector collection count mismatch")
    manifest = TMIEventIndexManifest(
        corpus_id=store.manifest.corpus_id,
        embedding_model_id=encoder.model_id,
        embedding_dimension=dimension,
        document_count=len(documents),
        vector_count=vector_count,
        tmi_event_documents=document_artifact,
    )
    manifest_path.write_text(
        manifest.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


class ChromaTMIEventRetrievalIndex:
    """Validated read-only view of one corpus-bound Chroma event index."""

    def __init__(
        self,
        store: CorpusQueryStore,
        index_dir: str | Path,
    ) -> None:
        root = Path(index_dir)
        try:
            manifest = TMIEventIndexManifest.model_validate_json(
                (root / TMI_EVENT_INDEX_MANIFEST).read_text(encoding="utf-8")
            )
        except (OSError, ValueError) as exc:
            raise ValueError("invalid TMI-event index manifest") from exc
        if manifest.corpus_id != store.manifest.corpus_id:
            raise ValueError("TMI-event index belongs to another corpus")

        documents_path = root / manifest.tmi_event_documents.path
        try:
            data = documents_path.read_bytes()
        except OSError as exc:
            raise ValueError("TMI-event documents are missing") from exc
        if (
            hashlib.sha256(data).hexdigest()
            != manifest.tmi_event_documents.sha256
        ):
            raise ValueError("TMI-event documents checksum mismatch")
        documents = tuple(
            TMIEventRetrievalDocument.model_validate_json(line)
            for line in data.splitlines()
            if line.strip()
        )
        if (
            len(documents) != manifest.tmi_event_documents.count
            or len(documents) != manifest.document_count
        ):
            raise ValueError("TMI-event document count mismatch")

        try:
            collection = get_collection(
                open_persistent_client(root / "chroma"),
                manifest.collection_name,
                embedding_function=None,
            )
        except Exception as exc:
            raise ValueError("TMI-event vector collection is missing") from exc
        expected_metadata = {
            "corpus_id": manifest.corpus_id,
            "representation_version": manifest.representation_version,
            "embedding_model_id": manifest.embedding_model_id,
            "embedding_dimension": manifest.embedding_dimension,
            "distance_metric": manifest.distance_metric,
        }
        if (
            (collection.metadata or {}).get("embedding_dimension")
            != manifest.embedding_dimension
        ):
            raise ValueError("TMI-event vector dimension mismatch")
        if collection.metadata != expected_metadata:
            raise ValueError("TMI-event vector collection metadata mismatch")
        if (
            collection.count() != manifest.vector_count
            or manifest.vector_count != manifest.document_count
        ):
            raise ValueError("TMI-event vector count mismatch")
        for document in documents:
            if (
                len(
                    get_stored_embedding(
                        collection,
                        document.document_id,
                    )
                )
                != manifest.embedding_dimension
            ):
                raise ValueError("TMI-event vector dimension mismatch")

        self.store = store
        self.root = root
        self.manifest = manifest
        self.collection = collection
        self.documents = documents
        self._document_by_event = {
            document.event_id: document
            for document in documents
        }

    def get_event_vector(self, event_id: str) -> tuple[float, ...]:
        """Return the stored normalized vector for one corpus TMI event."""

        try:
            document = self._document_by_event[event_id]
        except KeyError as exc:
            raise ValueError(f"TMI event is not indexed: {event_id}") from exc
        vector = get_stored_embedding(
            self.collection,
            document.document_id,
        )
        if len(vector) != self.manifest.embedding_dimension:
            raise ValueError("TMI-event vector dimension mismatch")
        return vector

    def query_candidates(
        self,
        *,
        query_vector: Sequence[float],
        candidate_event_ids: Sequence[str],
        n_results: int,
    ) -> tuple[TMIEventVectorHit, ...]:
        """Query explicit vectors after the caller has selected candidates."""

        candidate_ids = sorted(set(candidate_event_ids))
        if not candidate_ids:
            return ()
        if len(query_vector) != self.manifest.embedding_dimension:
            raise ValueError("query vector dimension mismatch")
        result = query_explicit_embeddings(
            self.collection,
            query_embedding=query_vector,
            where={"event_id": {"$in": candidate_ids}},
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
                    advisory_source_id=str(
                        metadata["advisory_source_id"]
                    ),
                    distance=distance,
                    similarity=cosine_similarity(distance),
                )
            )
        return tuple(hits)
