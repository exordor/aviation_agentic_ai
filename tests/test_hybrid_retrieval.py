import sys
from pathlib import Path
from types import SimpleNamespace

from aviation_agentic_ai.chunking.chunks import SourceChunk, write_chunks_jsonl
from aviation_agentic_ai.kg.extraction import KGTriple, write_kg_jsonl
from aviation_agentic_ai.retrieval.hybrid import (
    build_answer_prompt,
    graph_search,
    reciprocal_rank_fusion,
)
from aviation_agentic_ai.retrieval.indexing import build_chroma_index


def test_reciprocal_rank_fusion_uses_ranks_and_top_k() -> None:
    fused = reciprocal_rank_fusion(
        [
            [{"chunk_id": "a", "rank": 1, "score": 100, "source": "vector"}],
            [
                {"chunk_id": "b", "rank": 1, "score": 1, "source": "graph"},
                {"chunk_id": "a", "rank": 2, "score": 1, "source": "graph"},
            ],
        ],
        top_k=1,
    )

    assert len(fused) == 1
    assert fused[0]["chunk_id"] == "a"
    assert fused[0]["score"] < 1


def test_answer_prompt_contains_grounding_constraints() -> None:
    prompt = build_answer_prompt(
        "How does angle of attack affect lift?",
        [{"chunk_id": "c1", "page": 0, "source": "hybrid", "text": "Lift evidence."}],
        [
            {
                "triple_id": "t1",
                "chunk_id": "c1",
                "page": 0,
                "subject": "angle of attack",
                "subject_class": "Cl_AngleOfAttack",
                "predicate": "affects",
                "object": "lift",
                "object_class": "Cl_Lift",
                "evidence_text": "Lift evidence.",
            }
        ],
    )

    assert "Answer only from the retrieved evidence" in prompt
    assert "insufficient" in prompt
    assert "Do not claim to replace" in prompt
    assert "triple_id=t1" in prompt


def test_graph_search_returns_triple_and_chunk_evidence(tmp_path: Path) -> None:
    chunk = SourceChunk(
        chunk_id="doc-p00-c00",
        source_document="doc",
        source_path="data/raw/doc.pdf",
        page=0,
        chunk_index=0,
        char_start=0,
        char_end=40,
        text="Angle of attack affects lift.",
    )
    triple = KGTriple(
        triple_id="t1",
        subject="angle of attack",
        predicate="affects",
        object="lift",
        subject_class="Cl_AngleOfAttack",
        object_class="Cl_Lift",
        source_document="doc",
        page=0,
        section="page-0",
        chunk_id=chunk.chunk_id,
        evidence_text=chunk.text,
        model="test",
        confidence=1.0,
        extracted_at="2026-05-18T00:00:00+00:00",
    )
    chunks_path = write_chunks_jsonl([chunk], tmp_path / "chunks.jsonl")
    kg_path = write_kg_jsonl([triple], tmp_path / "kg.jsonl")

    chunks, triples = graph_search("What affects lift?", kg_path, chunks_path)

    assert chunks[0]["chunk_id"] == chunk.chunk_id
    assert triples[0]["triple_id"] == "t1"


def test_chroma_index_builder_can_use_mock_client(tmp_path: Path, monkeypatch) -> None:
    calls = {}

    class FakeCollection:
        def add(self, ids, documents, metadatas):
            calls["ids"] = ids
            calls["documents"] = documents
            calls["metadatas"] = metadatas

    class FakeClient:
        def __init__(self, path):
            calls["path"] = path

        def delete_collection(self, _name):
            calls["deleted"] = True

        def get_or_create_collection(self, name):
            calls["collection"] = name
            return FakeCollection()

    monkeypatch.setitem(sys.modules, "chromadb", SimpleNamespace(PersistentClient=FakeClient))
    chunk = SourceChunk(
        chunk_id="doc-p00-c00",
        source_document="doc",
        source_path="data/raw/doc.pdf",
        page=0,
        chunk_index=0,
        char_start=0,
        char_end=10,
        text="Air lift.",
    )
    chunks_path = write_chunks_jsonl([chunk], tmp_path / "chunks.jsonl")

    report = build_chroma_index(chunks_path, tmp_path / "chroma", collection_name="test")

    assert report["chunks_indexed"] == 1
    assert calls["collection"] == "test"
    assert calls["ids"] == ["doc-p00-c00"]
