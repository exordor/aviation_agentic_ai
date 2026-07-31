"""Shared Chroma lifecycle used by chunk and TMI-event indexes."""

from __future__ import annotations

from pathlib import Path

import pytest

from aviation_agentic_ai.retrieval.chroma_store import (
    cosine_similarity,
    get_collection,
    get_stored_embedding,
    open_persistent_client,
    query_explicit_embeddings,
    recreate_collection,
    upsert_explicit_embeddings,
)


def test_explicit_embeddings_and_metadata_filter_reach_collection() -> None:
    calls: dict[str, object] = {}

    class FakeCollection:
        def upsert(self, **kwargs: object) -> None:
            calls["upsert"] = kwargs

        def query(self, **kwargs: object) -> dict[str, object]:
            calls["query"] = kwargs
            return {
                "ids": [["document:b"]],
                "metadatas": [[{"event_id": "event:b"}]],
                "distances": [[0.25]],
            }

    collection = FakeCollection()
    upsert_explicit_embeddings(
        collection,
        ids=["document:a", "document:b"],
        embeddings=[[1.0, 0.0], [0.0, 1.0]],
        documents=["A", "B"],
        metadatas=[
            {"event_id": "event:a"},
            {"event_id": "event:b"},
        ],
    )
    result = query_explicit_embeddings(
        collection,
        query_embedding=[0.0, 1.0],
        where={"event_id": {"$in": ["event:b"]}},
        n_results=1,
    )

    assert calls["upsert"] == {
        "ids": ["document:a", "document:b"],
        "embeddings": [[1.0, 0.0], [0.0, 1.0]],
        "documents": ["A", "B"],
        "metadatas": [
            {"event_id": "event:a"},
            {"event_id": "event:b"},
        ],
    }
    assert calls["query"] == {
        "query_embeddings": [[0.0, 1.0]],
        "where": {"event_id": {"$in": ["event:b"]}},
        "n_results": 1,
        "include": ["metadatas", "distances"],
    }
    assert result["ids"] == [["document:b"]]
    assert cosine_similarity(0.25) == pytest.approx(0.75)


def test_real_persistent_collection_reopens_and_filters_candidates(
    tmp_path: Path,
) -> None:
    path = tmp_path / "chroma"
    client = open_persistent_client(path)
    collection = recreate_collection(
        client,
        "tmi_events",
        embedding_function=None,
        configuration={"hnsw": {"space": "cosine"}},
        metadata={"corpus_id": "corpus:test"},
    )
    upsert_explicit_embeddings(
        collection,
        ids=["document:a", "document:b"],
        embeddings=[[1.0, 0.0], [0.0, 1.0]],
        documents=["A", "B"],
        metadatas=[
            {"event_id": "event:a"},
            {"event_id": "event:b"},
        ],
    )

    reopened = get_collection(
        open_persistent_client(path),
        "tmi_events",
        embedding_function=None,
    )
    result = query_explicit_embeddings(
        reopened,
        query_embedding=[1.0, 0.0],
        where={"event_id": {"$in": ["event:b"]}},
        n_results=1,
    )

    assert reopened.count() == 2
    assert get_stored_embedding(reopened, "document:a") == pytest.approx(
        (1.0, 0.0)
    )
    assert result["ids"] == [["document:b"]]
