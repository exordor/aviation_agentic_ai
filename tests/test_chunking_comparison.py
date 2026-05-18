import json
from pathlib import Path

from aviation_agentic_ai.chunking.chunks import (
    CHUNKING_STRATEGIES,
    SourceChunk,
    chunk_output_path_for_strategy,
    write_chunks_jsonl,
)
from aviation_agentic_ai.ontology.cq import normalize_cq_artifact
from aviation_agentic_ai.reporting.chunking_comparison import (
    retrieval_metrics,
    write_chunking_comparison,
)


def write_boundary_cqs(path: Path) -> None:
    cqs = normalize_cq_artifact(
        {
            "doc": {
                "0": [
                    {
                        "competency_question": "What affects lift?",
                        "key_entities": ["lift"],
                        "odp_hint": "Causal relation",
                        "expected_answer": "Angle of attack affects lift.",
                    }
                ]
            }
        }
    )
    path.write_text(json.dumps(cqs) + "\n", encoding="utf-8")


def make_chunk(strategy: str) -> SourceChunk:
    return SourceChunk(
        chunk_id=f"doc-{strategy}-p00-c00",
        source_document="doc",
        source_path="data/raw/doc.pdf",
        page=0,
        chunk_index=0,
        char_start=0,
        char_end=30,
        text="Angle of attack affects lift.",
        strategy=strategy,
        section="Lift",
    )


def test_retrieval_metrics_calculate_recall_mrr_and_precision() -> None:
    metrics = retrieval_metrics(
        [
            {"chunk_id": "a", "page": 2},
            {"chunk_id": "b", "page": 0},
            {"chunk_id": "c", "page": 0},
        ],
        source_page=0,
        top_k=5,
    )

    assert metrics["recall_at_5"]
    assert metrics["mrr_at_5"] == 0.5
    assert metrics["context_precision_at_5"] == 0.6667


def test_write_chunking_comparison_with_mock_retriever(tmp_path: Path) -> None:
    cq_path = tmp_path / "boundary.json"
    base_chunks_path = tmp_path / "chunks.jsonl"
    write_boundary_cqs(cq_path)
    for strategy in CHUNKING_STRATEGIES:
        write_chunks_jsonl([make_chunk(strategy)], chunk_output_path_for_strategy(base_chunks_path, strategy))

    indexed = []

    def fake_index_builder(chunks_path, index_dir, collection_name, reset):
        indexed.append((chunks_path, index_dir, collection_name, reset))
        return {"chunks_indexed": 1}

    def fake_retriever(question, index_dir, collection_name, top_k):
        return [
            {
                "chunk_id": f"{collection_name}-hit",
                "page": 0,
                "rank": 1,
                "score": 1.0,
                "text": question,
            }
        ][:top_k]

    json_path, md_path, result = write_chunking_comparison(
        tmp_path / "doc.pdf",
        cq_path,
        base_chunks_path,
        tmp_path / "chroma",
        tmp_path,
        index_builder=fake_index_builder,
        retriever=fake_retriever,
        rebuild_chunks=False,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert len(indexed) == len(CHUNKING_STRATEGIES)
    assert result["ranking"][0]["recall_at_5"] == 1.0
    assert set(result["strategies"]) == set(CHUNKING_STRATEGIES)
    assert result["metadata"]["run_manifest"]["rebuild_policy"]["chunks"] is False
    assert result["metadata"]["run_manifest"]["rebuild_policy"]["indexes"] is True
    assert result["strategies"]["fixed_window"]["aggregate"]["retrieval"]["recall_at_5"] == 1.0
    assert result["strategies"]["fixed_window"]["records"][0]["gold"]["gold_level"] == "page"
    assert result["strategies"]["fixed_window"]["explanation"]
    assert result["strategies"]["fixed_window"]["recommendation"]
