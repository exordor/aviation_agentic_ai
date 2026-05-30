from __future__ import annotations

from typing import Any


def hit_summary(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "chunk_id": str(hit.get("chunk_id", "")),
            "page": hit.get("page"),
            "rank": hit.get("rank"),
            "source": hit.get("source"),
        }
        for hit in hits
    ]


def triple_summary(triples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "triple_id": str(triple.get("triple_id", "")),
            "chunk_id": str(triple.get("chunk_id", "")),
            "page": triple.get("page"),
            "rank": triple.get("rank"),
            "subject": triple.get("subject"),
            "predicate": triple.get("predicate"),
            "object": triple.get("object"),
        }
        for triple in triples
    ]
