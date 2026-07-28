"""Persistent Chroma sidecar for deterministic decision-record documents."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Sequence

from aviation_agentic_ai.agent_system.case_retrieval_contracts import (
    DEFAULT_CASE_EMBEDDING_MODEL,
    REPRESENTATION_VERSION,
    CaseDocumentArtifact,
    CaseEncoder,
    CaseIndexManifest,
    CaseRetrievalDocument,
    CaseVectorHit,
)
from aviation_agentic_ai.agent_system.case_retrieval_documents import (
    build_case_retrieval_documents,
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


CASE_INDEX_MANIFEST = "case_index_manifest.json"
CASE_DOCUMENTS = "case_documents.jsonl"
CASE_COLLECTION = "decision_cases"


class SentenceTransformerCaseEncoder:
    """Lazy Sentence Transformers encoder for canonical case documents."""

    def __init__(
        self,
        model_name: str = DEFAULT_CASE_EMBEDDING_MODEL,
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
    documents: Sequence[CaseRetrievalDocument],
) -> CaseDocumentArtifact:
    data = "".join(
        document.model_dump_json() + "\n"
        for document in documents
    ).encode("utf-8")
    path.write_bytes(data)
    return CaseDocumentArtifact(
        path=path.name,
        count=len(documents),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def build_case_retrieval_index(
    corpus_dir: str | Path,
    *,
    encoder: CaseEncoder,
    index_dir: str | Path | None = None,
) -> CaseIndexManifest:
    """Rebuild one persistent case-vector sidecar and publish its manifest."""

    store = CorpusQueryStore(corpus_dir)
    documents = build_case_retrieval_documents(store)
    if not documents:
        raise ValueError("corpus has no accepted cases to index")
    root = Path(index_dir or (store.root / "case_index"))
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / CASE_INDEX_MANIFEST
    manifest_path.unlink(missing_ok=True)

    vectors = _normalized_vectors(
        encoder.encode([document.text for document in documents]),
        expected_count=len(documents),
    )
    dimension = len(vectors[0])
    document_artifact = _write_documents(
        root / CASE_DOCUMENTS,
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
        CASE_COLLECTION,
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
                "case_id": document.case_id,
                "event_id": document.event_id,
                "advisory_source_id": document.advisory_source_id,
            }
            for document in documents
        ],
    )
    vector_count = int(collection.count())
    if vector_count != len(documents):
        raise ValueError("case vector collection count mismatch")
    manifest = CaseIndexManifest(
        corpus_id=store.manifest.corpus_id,
        collection_name=CASE_COLLECTION,
        embedding_model_id=encoder.model_id,
        embedding_dimension=dimension,
        document_count=len(documents),
        vector_count=vector_count,
        case_documents=document_artifact,
    )
    manifest_path.write_text(
        manifest.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


class ChromaCaseRetrievalIndex:
    """Validated read-only view of one corpus-bound Chroma case index."""

    def __init__(
        self,
        store: CorpusQueryStore,
        index_dir: str | Path,
    ) -> None:
        root = Path(index_dir)
        try:
            manifest = CaseIndexManifest.model_validate_json(
                (root / CASE_INDEX_MANIFEST).read_text(encoding="utf-8")
            )
        except (OSError, ValueError) as exc:
            raise ValueError("invalid case index manifest") from exc
        if manifest.corpus_id != store.manifest.corpus_id:
            raise ValueError("case index belongs to another corpus")

        documents_path = root / manifest.case_documents.path
        try:
            data = documents_path.read_bytes()
        except OSError as exc:
            raise ValueError("case documents are missing") from exc
        if hashlib.sha256(data).hexdigest() != manifest.case_documents.sha256:
            raise ValueError("case documents checksum mismatch")
        documents = tuple(
            CaseRetrievalDocument.model_validate_json(line)
            for line in data.splitlines()
            if line.strip()
        )
        if (
            len(documents) != manifest.case_documents.count
            or len(documents) != manifest.document_count
        ):
            raise ValueError("case document count mismatch")

        try:
            collection = get_collection(
                open_persistent_client(root / "chroma"),
                manifest.collection_name,
                embedding_function=None,
            )
        except Exception as exc:
            raise ValueError("case vector collection is missing") from exc
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
            raise ValueError("case vector dimension mismatch")
        if collection.metadata != expected_metadata:
            raise ValueError("case vector collection metadata mismatch")
        if (
            collection.count() != manifest.vector_count
            or manifest.vector_count != manifest.document_count
        ):
            raise ValueError("case vector count mismatch")
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
                raise ValueError("case vector dimension mismatch")

        self.store = store
        self.root = root
        self.manifest = manifest
        self.collection = collection
        self.documents = documents
        self._document_by_case = {
            document.case_id: document
            for document in documents
        }

    def get_case_vector(self, case_id: str) -> tuple[float, ...]:
        """Return the stored normalized vector for one corpus case."""

        try:
            document = self._document_by_case[case_id]
        except KeyError as exc:
            raise ValueError(f"case is not indexed: {case_id}") from exc
        vector = get_stored_embedding(
            self.collection,
            document.document_id,
        )
        if len(vector) != self.manifest.embedding_dimension:
            raise ValueError("case vector dimension mismatch")
        return vector

    def query_candidates(
        self,
        *,
        query_vector: Sequence[float],
        candidate_case_ids: Sequence[str],
        n_results: int,
    ) -> tuple[CaseVectorHit, ...]:
        """Query explicit vectors after the caller has selected candidates."""

        candidate_ids = sorted(set(candidate_case_ids))
        if not candidate_ids:
            return ()
        if len(query_vector) != self.manifest.embedding_dimension:
            raise ValueError("query vector dimension mismatch")
        result = query_explicit_embeddings(
            self.collection,
            query_embedding=query_vector,
            where={"case_id": {"$in": candidate_ids}},
            n_results=min(n_results, len(candidate_ids)),
        )
        ids = (result.get("ids") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        hits: list[CaseVectorHit] = []
        for index, _record_id in enumerate(ids):
            metadata = metadatas[index]
            distance = float(distances[index])
            hits.append(
                CaseVectorHit(
                    case_id=str(metadata["case_id"]),
                    event_id=str(metadata["event_id"]),
                    advisory_source_id=str(
                        metadata["advisory_source_id"]
                    ),
                    distance=distance,
                    similarity=cosine_similarity(distance),
                )
            )
        return tuple(hits)
