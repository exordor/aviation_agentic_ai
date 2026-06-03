from __future__ import annotations

from collections import Counter
import math
import re
from typing import Any, Callable, Iterable

from aviation_agentic_ai.reporting.nasa_atmonto_answer_benchmark import chunk_id

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_:/.-]*", re.IGNORECASE)
DEFAULT_DENSE_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DenseEncoder = Callable[[list[str]], Iterable[Iterable[float]]]


def tokenize_for_retrieval(text: object) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_RE.finditer(str(text or ""))]


def source_record_document(record: dict[str, Any]) -> dict[str, Any]:
    source_id = str(record.get("source_id") or record.get("sample_id") or "")
    source_text = str(record.get("source_text") or record.get("text") or "")
    advisory_number = record.get("advisory_number")
    advisory_date = record.get("advisory_date") or source_id.split(":", 1)[0]
    header = " ".join(
        part
        for part in (
            f"source_id {source_id}" if source_id else "",
            f"advisory_date {advisory_date}" if advisory_date else "",
            f"advisory_number {advisory_number}" if advisory_number not in (None, "") else "",
            str(record.get("title") or ""),
        )
        if part
    )
    text = f"{header}\n{source_text}".strip()
    return {
        "source_id": source_id,
        "chunk_id": chunk_id(source_id),
        "text": text,
        "source_url": record.get("source_url"),
        "advisory_date": advisory_date,
        "advisory_number": advisory_number,
    }


def build_live_tfidf_source_index(source_records: list[dict[str, Any]]) -> dict[str, Any]:
    documents = [
        source_record_document(record)
        for record in source_records
        if record.get("source_id") or record.get("sample_id")
    ]
    token_counts: list[Counter[str]] = []
    document_frequency: Counter[str] = Counter()
    for document in documents:
        counts = Counter(tokenize_for_retrieval(document["text"]))
        token_counts.append(counts)
        document_frequency.update(counts.keys())
    document_count = len(documents)
    idf = {
        token: math.log((1 + document_count) / (1 + frequency)) + 1.0
        for token, frequency in document_frequency.items()
    }
    vectors = [_tfidf_vector(counts, idf) for counts in token_counts]
    norms = [_vector_norm(vector) for vector in vectors]
    return {
        "documents": documents,
        "idf": idf,
        "vectors": vectors,
        "norms": norms,
        "document_count": document_count,
        "retriever": "live_tfidf_vector",
    }


def query_live_tfidf_source_index(
    index: dict[str, Any],
    query: str,
    *,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    idf = index.get("idf") if isinstance(index.get("idf"), dict) else {}
    query_vector = _tfidf_vector(Counter(tokenize_for_retrieval(query)), idf)
    query_norm = _vector_norm(query_vector)
    scored: list[dict[str, Any]] = []
    documents = index.get("documents", [])
    vectors = index.get("vectors", [])
    norms = index.get("norms", [])
    for position, document in enumerate(documents):
        vector = vectors[position] if position < len(vectors) else {}
        norm = float(norms[position]) if position < len(norms) else 0.0
        score = _cosine(query_vector, query_norm, vector, norm)
        scored.append({"score": score, "document": document})
    scored.sort(
        key=lambda item: (
            -float(item["score"]),
            str(item["document"].get("source_id") or ""),
        )
    )
    hits: list[dict[str, Any]] = []
    for rank, item in enumerate(scored[:top_k], start=1):
        document = item["document"]
        hits.append(
            {
                "kind": "source_chunk",
                "chunk_id": document["chunk_id"],
                "page": 1,
                "rank": rank,
                "score": round(float(item["score"]), 6),
                "text": document["text"],
                "source_id": document["source_id"],
                "source": "live_tfidf_vector",
                "metadata": {
                    "source_url": document.get("source_url"),
                    "advisory_date": document.get("advisory_date"),
                    "advisory_number": document.get("advisory_number"),
                },
            }
        )
    return hits


def build_dense_source_index(
    source_records: list[dict[str, Any]],
    *,
    model_name: str = DEFAULT_DENSE_MODEL_NAME,
    local_files_only: bool = True,
    encoder: DenseEncoder | None = None,
) -> dict[str, Any]:
    documents = [
        source_record_document(record)
        for record in source_records
        if record.get("source_id") or record.get("sample_id")
    ]
    if encoder is None:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(model_name, local_files_only=local_files_only)

        def encode_texts(texts: list[str]) -> Iterable[Iterable[float]]:
            return model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

        active_encoder: DenseEncoder = encode_texts
    else:
        active_encoder = encoder
    embeddings = [_normalize_dense_vector(vector) for vector in active_encoder([doc["text"] for doc in documents])]
    return {
        "documents": documents,
        "embeddings": embeddings,
        "document_count": len(documents),
        "retriever": "dense_embedding_vector",
        "model_name": model_name,
        "local_files_only": local_files_only,
        "_encoder": active_encoder,
    }


def query_dense_source_index(
    index: dict[str, Any],
    query: str,
    *,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    encoder = index.get("_encoder")
    if not callable(encoder):
        raise RuntimeError("Dense source index is missing an encoder")
    query_vector = _normalize_dense_vector(next(iter(encoder([query]))))
    scored: list[dict[str, Any]] = []
    documents = index.get("documents", [])
    embeddings = index.get("embeddings", [])
    for position, document in enumerate(documents):
        embedding = embeddings[position] if position < len(embeddings) else []
        scored.append({"score": _dense_dot(query_vector, embedding), "document": document})
    scored.sort(
        key=lambda item: (
            -float(item["score"]),
            str(item["document"].get("source_id") or ""),
        )
    )
    hits: list[dict[str, Any]] = []
    for rank, item in enumerate(scored[:top_k], start=1):
        document = item["document"]
        hits.append(
            {
                "kind": "source_chunk",
                "chunk_id": document["chunk_id"],
                "page": 1,
                "rank": rank,
                "score": round(float(item["score"]), 6),
                "text": document["text"],
                "source_id": document["source_id"],
                "source": "dense_embedding_vector",
                "metadata": {
                    "source_url": document.get("source_url"),
                    "advisory_date": document.get("advisory_date"),
                    "advisory_number": document.get("advisory_number"),
                    "model_name": index.get("model_name"),
                },
            }
        )
    return hits


def _tfidf_vector(counts: Counter[str], idf: dict[str, float]) -> dict[str, float]:
    total = sum(counts.values()) or 1
    return {
        token: (count / total) * float(idf.get(token, 0.0))
        for token, count in counts.items()
        if token in idf
    }


def _vector_norm(vector: dict[str, float]) -> float:
    return math.sqrt(sum(value * value for value in vector.values()))


def _cosine(
    left: dict[str, float],
    left_norm: float,
    right: dict[str, float],
    right_norm: float,
) -> float:
    if left_norm <= 0.0 or right_norm <= 0.0:
        return 0.0
    if len(left) > len(right):
        left, right = right, left
    dot = sum(value * right.get(token, 0.0) for token, value in left.items())
    return dot / (left_norm * right_norm)


def _normalize_dense_vector(vector: Iterable[float]) -> list[float]:
    values = [float(value) for value in vector]
    norm = math.sqrt(sum(value * value for value in values))
    if norm <= 0.0:
        return values
    return [value / norm for value in values]


def _dense_dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=False))
