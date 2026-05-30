import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

from aviation_agentic_ai.chunking.chunks import SourceChunk, write_chunks_jsonl
from aviation_agentic_ai.kg.extraction import KGTriple, write_kg_jsonl
from aviation_agentic_ai.retrieval.hybrid import (
    SOURCE_DELIMITER,
    UNKNOWN_SOURCE,
    _merged_source,
    _score,
    build_answer_prompt,
    generate_grounded_answer,
    graph_search,
    reciprocal_rank_fusion,
    run_query,
    run_retrieval,
    vector_first_guarded_fusion,
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


def test_reciprocal_rank_fusion_uses_unknown_for_missing_source() -> None:
    fused = reciprocal_rank_fusion(
        [[{"chunk_id": "a", "rank": 1, "score": 1.0, "source": ""}]],
        top_k=1,
    )

    assert fused[0]["source"] == "unknown"


def test_reciprocal_rank_fusion_normalizes_merged_source_labels() -> None:
    fused = reciprocal_rank_fusion(
        [
            [{"chunk_id": "a", "rank": 1, "score": 1.0, "source": "vector+graph"}],
            [{"chunk_id": "a", "rank": 1, "score": 1.0, "source": "graph"}],
            [{"chunk_id": "a", "rank": 1, "score": 1.0, "source": UNKNOWN_SOURCE}],
        ],
        top_k=1,
    )

    assert SOURCE_DELIMITER == "+"
    assert fused[0]["source"] == "graph+vector"
    assert _merged_source(" vector ", "graph+unknown") == "graph+vector"


def test_score_defaults_invalid_values_to_zero() -> None:
    assert _score({"score": 2}) == 2.0
    assert _score({"score": "2.5"}) == 2.5
    assert _score({"score": None}) == 0.0
    assert _score({"score": "not-a-number"}) == 0.0


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


def test_generate_grounded_answer_returns_non_answer_when_llm_fails(
    monkeypatch,
) -> None:
    class FakeHumanMessage:
        def __init__(self, content: str) -> None:
            self.content = content

    messages_module = ModuleType("langchain_core.messages")
    messages_module.HumanMessage = FakeHumanMessage
    monkeypatch.setitem(sys.modules, "langchain_core", ModuleType("langchain_core"))
    monkeypatch.setitem(sys.modules, "langchain_core.messages", messages_module)

    from aviation_agentic_ai.llm import providers

    class FailingLLM:
        def invoke(self, _messages):
            raise ConnectionError("offline provider")

    monkeypatch.setattr(providers, "get_llm", lambda **_kwargs: FailingLLM())

    answer, prompt = generate_grounded_answer(
        "What affects lift?",
        [{"chunk_id": "c1", "page": 0, "source": "vector", "text": "Lift evidence."}],
        [],
    )

    assert "Insufficient evidence to generate an LLM answer" in answer
    assert "ConnectionError" in answer
    assert "Citations: none" in answer
    assert "What affects lift?" in prompt
    assert "Lift evidence." in prompt


def test_generate_grounded_answer_abstains_without_retrieved_evidence(
    monkeypatch,
) -> None:
    from aviation_agentic_ai.llm import providers

    def fail_get_llm(**_kwargs):
        raise AssertionError("LLM should not be called without retrieved evidence")

    monkeypatch.setattr(providers, "get_llm", fail_get_llm)

    answer, prompt = generate_grounded_answer(
        "Current runway closure status?",
        [],
        [],
    )

    assert "retrieval returned no chunks or KG triples" in answer
    assert "Citations: none" in answer
    assert "Retrieved chunks:\nNone" in prompt
    assert "KG evidence:\nNone" in prompt


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


def test_graph_search_returns_empty_results_without_overlap(tmp_path: Path) -> None:
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

    chunks, triples = graph_search("Current runway closure status?", kg_path, chunks_path)

    assert chunks == []
    assert triples == []


def test_run_query_graph_no_overlap_abstains_without_llm(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from aviation_agentic_ai.llm import providers

    def fail_get_llm(**_kwargs):
        raise AssertionError("LLM should not be called without retrieved evidence")

    monkeypatch.setattr(providers, "get_llm", fail_get_llm)
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

    result = run_query(
        "Current runway closure status?",
        mode="graph",
        chunks_path=chunks_path,
        kg_path=kg_path,
        index_dir=tmp_path / "index",
    )

    assert result["graph_hits"] == []
    assert result["graph_triples"] == []
    assert result["fused_chunks"] == []
    assert "retrieval returned no chunks or KG triples" in result["answer"]
    assert "Citations: none" in result["answer"]


def test_run_query_hybrid_routes_retrieved_evidence_into_llm_prompt(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from aviation_agentic_ai.llm import providers
    from aviation_agentic_ai.retrieval import hybrid

    class FakeHumanMessage:
        def __init__(self, content: str) -> None:
            self.content = content

    messages_module = ModuleType("langchain_core.messages")
    messages_module.HumanMessage = FakeHumanMessage
    monkeypatch.setitem(sys.modules, "langchain_core", ModuleType("langchain_core"))
    monkeypatch.setitem(sys.modules, "langchain_core.messages", messages_module)

    captured: dict[str, object] = {}

    class FakeLLM:
        def invoke(self, messages):
            captured["prompt"] = messages[0].content
            return SimpleNamespace(content="Grounded answer.\n\nCitations: vector-c1, t1")

    def fake_get_llm(**kwargs):
        captured["llm_kwargs"] = kwargs
        return FakeLLM()

    monkeypatch.setattr(providers, "get_llm", fake_get_llm)
    monkeypatch.setattr(
        hybrid,
        "query_chroma_index",
        lambda *_args, **_kwargs: [
            {
                "chunk_id": "vector-c1",
                "rank": 1,
                "score": 0.99,
                "source": "vector",
                "page": 0,
                "text": "Vector lift evidence.",
                "metadata": {},
            }
        ],
    )
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

    result = run_query(
        "How does angle of attack affect lift?",
        mode="hybrid",
        chunks_path=chunks_path,
        kg_path=kg_path,
        index_dir=tmp_path / "index",
        graph_method="lexical",
        graph_fusion_policy="rrf",
        temperature=0.2,
        max_tokens=77,
    )

    assert result["answer"] == "Grounded answer.\n\nCitations: vector-c1, t1"
    assert result["vector_hits"][0]["chunk_id"] == "vector-c1"
    assert result["graph_triples"][0]["triple_id"] == "t1"
    assert {item["chunk_id"] for item in result["fused_chunks"]} == {
        "doc-p00-c00",
        "vector-c1",
    }
    assert captured["llm_kwargs"] == {"temperature": 0.2, "max_tokens": 77}
    prompt = str(captured["prompt"])
    assert "Vector lift evidence." in prompt
    assert "triple_id=t1" in prompt
    assert "Answer only from the retrieved evidence" in prompt


def test_run_retrieval_hybrid_records_lexical_hops_as_not_applicable(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from aviation_agentic_ai.retrieval import hybrid

    chunk = SourceChunk(
        chunk_id="doc-p00-c00",
        source_document="doc",
        source_path="data/raw/doc.pdf",
        page=0,
        chunk_index=0,
        char_start=0,
        char_end=40,
        text="Air affects wing lift.",
    )
    triple = KGTriple(
        triple_id="t1",
        subject="air",
        predicate="affects",
        object="wing",
        subject_class="Cl_Air",
        object_class="Cl_Wing",
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
    monkeypatch.setattr(
        hybrid,
        "query_chroma_index",
        lambda *_args, **_kwargs: [
            {
                "chunk_id": "vector-c1",
                "rank": 1,
                "score": 1.0,
                "source": "vector",
                "page": 1,
                "text": "Vector evidence.",
                "metadata": {},
            }
        ],
    )

    result = run_retrieval(
        "What affects thrust?",
        mode="hybrid",
        chunks_path=chunks_path,
        kg_path=kg_path,
        index_dir=tmp_path / "index",
        graph_method="lexical",
        graph_hops=99,
        graph_fusion_policy="rrf",
    )

    assert result["graph_hops_requested"] == 99
    assert result["graph_hops_effective"] is None
    assert "lexical" in result["graph_hops_note"]
    assert result["vector_hits"]
    assert result["graph_hits"]
    assert result["fused_chunks"]


def test_vector_first_guarded_fusion_preserves_vector_when_graph_overlap_is_weak() -> None:
    fused = vector_first_guarded_fusion(
        "What affects thrust?",
        vector_hits=[
            {"chunk_id": "v1", "rank": 1, "score": 1.0, "source": "vector"},
            {"chunk_id": "v2", "rank": 2, "score": 0.9, "source": "vector"},
        ],
        graph_hits=[{"chunk_id": "g1", "rank": 1, "score": 1.0, "source": "graph"}],
        graph_triples=[
            {
                "triple_id": "t1",
                "subject": "air",
                "predicate": "affects",
                "object": "wing",
                "evidence_text": "Air affects wing lift.",
            }
        ],
        graph_paths=[],
        top_k=3,
    )

    assert [item["chunk_id"] for item in fused] == ["v1", "v2", "g1"]
    assert [item["rank"] for item in fused] == [1, 2, 3]


def test_vector_first_guarded_fusion_merges_duplicate_weak_graph_hit() -> None:
    fused = vector_first_guarded_fusion(
        "What affects thrust?",
        vector_hits=[
            {"chunk_id": "v1", "rank": 1, "score": 1.0, "source": "vector"},
            {"chunk_id": "shared", "rank": 2, "score": 0.1, "source": "vector"},
        ],
        graph_hits=[
            {"chunk_id": "shared", "rank": 1, "score": 5.0, "source": "graph"},
        ],
        graph_triples=[],
        graph_paths=[],
        top_k=2,
        preserve_top_n=1,
    )

    assert [item["chunk_id"] for item in fused] == ["v1", "shared"]
    assert fused[1]["score"] == 5.0
    assert fused[1]["source"] == "graph+vector"


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


def test_chroma_index_builder_ignores_missing_collection_on_reset(
    tmp_path: Path,
    monkeypatch,
) -> None:
    class FakeCollection:
        def add(self, ids, documents, metadatas):
            pass

    class FakeClient:
        def __init__(self, path):
            self.path = path

        def delete_collection(self, _name):
            raise ValueError("Collection does not exist")

        def get_or_create_collection(self, _name):
            return FakeCollection()

    monkeypatch.setitem(sys.modules, "chromadb", SimpleNamespace(PersistentClient=FakeClient))
    chunks_path = write_chunks_jsonl([], tmp_path / "chunks.jsonl")

    report = build_chroma_index(chunks_path, tmp_path / "chroma", collection_name="test")

    assert report["chunks_indexed"] == 0


def test_chroma_index_builder_raises_unexpected_delete_errors(
    tmp_path: Path,
    monkeypatch,
) -> None:
    class FakeClient:
        def __init__(self, path):
            self.path = path

        def delete_collection(self, _name):
            raise RuntimeError("permission denied")

    monkeypatch.setitem(sys.modules, "chromadb", SimpleNamespace(PersistentClient=FakeClient))
    chunks_path = write_chunks_jsonl([], tmp_path / "chunks.jsonl")

    try:
        build_chroma_index(chunks_path, tmp_path / "chroma", collection_name="test")
    except RuntimeError as exc:
        message = str(exc)
    else:  # pragma: no cover - assertion guard.
        raise AssertionError("Expected RuntimeError")

    assert "permission denied" in message
