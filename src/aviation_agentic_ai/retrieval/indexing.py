from __future__ import annotations

from pathlib import Path
from typing import Any

from aviation_agentic_ai.chunking.chunks import SourceChunk, read_chunks_jsonl
from aviation_agentic_ai.paths import project_relative_path


DEFAULT_COLLECTION_NAME = "phak_ch4_chunks"


def _metadata_for_chunk(chunk: SourceChunk) -> dict[str, str | int | float | bool]:
    metadata: dict[str, str | int | float | bool] = {
        "chunk_id": chunk.chunk_id,
        "source_document": chunk.source_document,
        "source_path": chunk.source_path,
        "page": chunk.page,
        "chunk_index": chunk.chunk_index,
        "token_count": chunk.token_count,
        "strategy": chunk.strategy,
        "section": chunk.section,
    }
    if chunk.parent_chunk_id:
        metadata["parent_chunk_id"] = chunk.parent_chunk_id
        metadata["parent_section"] = chunk.parent_section
        metadata["parent_page"] = int(chunk.parent_page) if chunk.parent_page is not None else -1
    if chunk.context_prefix:
        metadata["context_prefix"] = chunk.context_prefix
    for key, value in chunk.metadata.items():
        if isinstance(value, str | int | float | bool):
            metadata[f"chunk_{key}"] = value
    return metadata


def build_chroma_index(
    chunks_path: str | Path,
    index_dir: str | Path,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    reset: bool = True,
) -> dict[str, Any]:
    """Build a persistent Chroma collection from chunk JSONL."""
    try:
        import chromadb
    except ImportError as exc:
        raise RuntimeError(
            "ChromaDB indexing requires optional GraphRAG dependencies. "
            "Install with: uv sync --extra graphrag"
        ) from exc

    chunks = read_chunks_jsonl(chunks_path)
    path = Path(index_dir)
    path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(path))
    if reset:
        try:
            client.delete_collection(collection_name)
        except Exception as exc:
            message = str(exc).lower()
            if not any(phrase in message for phrase in ("not found", "does not exist", "no collection", "nonexistent")):
                raise
    collection = client.get_or_create_collection(collection_name)
    if chunks:
        collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[_metadata_for_chunk(chunk) for chunk in chunks],
        )
    return {
        "index_dir": project_relative_path(path),
        "collection_name": collection_name,
        "chunks_path": project_relative_path(chunks_path),
        "chunks_indexed": len(chunks),
    }


def query_chroma_index(
    question: str,
    index_dir: str | Path,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    try:
        import chromadb
    except ImportError as exc:
        raise RuntimeError(
            "ChromaDB querying requires optional GraphRAG dependencies. "
            "Install with: uv sync --extra graphrag"
        ) from exc

    client = chromadb.PersistentClient(path=str(index_dir))
    collection = client.get_collection(collection_name)
    results = collection.query(
        query_texts=[question],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    hits: list[dict[str, Any]] = []
    for rank, chunk_id in enumerate(ids, start=1):
        metadata = metadatas[rank - 1] if rank - 1 < len(metadatas) else {}
        hits.append(
            {
                "chunk_id": str(chunk_id),
                "rank": rank,
                "score": 1.0 / (1.0 + float(distances[rank - 1]))
                if rank - 1 < len(distances)
                else 0.0,
                "distance": float(distances[rank - 1]) if rank - 1 < len(distances) else None,
                "source": "vector",
                "page": int(metadata.get("page", -1)) if isinstance(metadata, dict) else -1,
                "text": str(documents[rank - 1]) if rank - 1 < len(documents) else "",
                "metadata": metadata,
            }
        )
    return hits
