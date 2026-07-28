"""Thin lazy Chroma lifecycle helpers shared by vector indexes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence


_UNSET = object()
_MISSING_COLLECTION_PHRASES = (
    "not found",
    "does not exist",
    "no collection",
    "nonexistent",
)


def open_persistent_client(path: str | Path) -> Any:
    """Open a local persistent Chroma client without eager imports."""

    import chromadb

    root = Path(path)
    root.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(root))


def recreate_collection(
    client: Any,
    name: str,
    *,
    embedding_function: object = _UNSET,
    configuration: Mapping[str, object] | None = None,
    metadata: Mapping[str, str | int | float | bool] | None = None,
) -> Any:
    """Delete an old collection if present and create a fresh one."""

    try:
        client.delete_collection(name)
    except Exception as exc:
        if not any(
            phrase in str(exc).lower()
            for phrase in _MISSING_COLLECTION_PHRASES
        ):
            raise
    kwargs: dict[str, object] = {}
    if embedding_function is not _UNSET:
        kwargs["embedding_function"] = embedding_function
    if configuration is not None:
        kwargs["configuration"] = dict(configuration)
    if metadata is not None:
        kwargs["metadata"] = dict(metadata)
    if not kwargs:
        return client.get_or_create_collection(name)
    return client.get_or_create_collection(name=name, **kwargs)


def get_collection(
    client: Any,
    name: str,
    *,
    embedding_function: object = _UNSET,
) -> Any:
    """Open an existing collection, optionally disabling embedding functions."""

    if embedding_function is _UNSET:
        return client.get_collection(name)
    return client.get_collection(
        name=name,
        embedding_function=embedding_function,
    )


def upsert_explicit_embeddings(
    collection: Any,
    *,
    ids: Sequence[str],
    embeddings: Sequence[Sequence[float]],
    documents: Sequence[str],
    metadatas: Sequence[Mapping[str, str | int | float | bool]],
) -> None:
    """Upsert already-computed vectors and their scalar metadata."""

    collection.upsert(
        ids=list(ids),
        embeddings=[list(vector) for vector in embeddings],
        documents=list(documents),
        metadatas=[dict(metadata) for metadata in metadatas],
    )


def get_stored_embedding(
    collection: Any,
    record_id: str,
) -> tuple[float, ...]:
    """Return one explicit vector by stable Chroma record ID."""

    result = collection.get(ids=[record_id], include=["embeddings"])
    ids = result.get("ids") or []
    embeddings = result.get("embeddings")
    if ids != [record_id] or embeddings is None or len(embeddings) != 1:
        raise ValueError(f"stored vector is missing: {record_id}")
    return tuple(float(value) for value in embeddings[0])


def query_explicit_embeddings(
    collection: Any,
    *,
    query_embedding: Sequence[float],
    where: Mapping[str, object],
    n_results: int,
) -> dict[str, object]:
    """Run one precomputed-vector query with a metadata candidate filter."""

    return collection.query(
        query_embeddings=[list(query_embedding)],
        where=dict(where),
        n_results=n_results,
        include=["metadatas", "distances"],
    )


def cosine_similarity(distance: float) -> float:
    """Convert Chroma cosine distance to higher-is-more-similar form."""

    return 1.0 - float(distance)
