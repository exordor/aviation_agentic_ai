from aviation_agentic_ai.reporting.retrieval_summaries import hit_summary, triple_summary


def test_hit_summary_preserves_public_retrieval_fields() -> None:
    assert hit_summary(
        [
            {
                "chunk_id": 123,
                "page": 4,
                "rank": 1,
                "score": 0.9,
                "source": "graph+vector",
                "text": "omitted",
            }
        ]
    ) == [
        {
            "chunk_id": "123",
            "page": 4,
            "rank": 1,
            "source": "graph+vector",
        }
    ]


def test_triple_summary_preserves_public_kg_fields() -> None:
    assert triple_summary(
        [
            {
                "triple_id": 7,
                "chunk_id": "c1",
                "page": 2,
                "rank": 3,
                "subject": "lift",
                "predicate": "affects",
                "object": "drag",
                "evidence_text": "omitted",
            }
        ]
    ) == [
        {
            "triple_id": "7",
            "chunk_id": "c1",
            "page": 2,
            "rank": 3,
            "subject": "lift",
            "predicate": "affects",
            "object": "drag",
        }
    ]
