import json
from pathlib import Path

from aviation_agentic_ai.chunking.chunks import (
    PILOT_CHUNKING_STRATEGIES,
    SourceChunk,
    chunk_output_path_for_strategy,
    write_chunks_jsonl,
)
from aviation_agentic_ai.ontology.cq import normalize_cq_artifact
from aviation_agentic_ai.reporting.chunking_comparison import (
    build_chunking_category_analysis_v2_from_result,
    build_chunking_failure_cards_v2,
    build_chunking_topk_sensitivity_v2_from_result,
    retrieval_metrics,
    write_chunking_comparison,
    write_chunking_implementation_audit,
    write_chunking_comparison_v2,
)
from aviation_agentic_ai.utils.pdf import PdfPage


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


def test_write_chunking_implementation_audit_marks_partial_methods(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from aviation_agentic_ai.chunking import chunks as chunk_module

    monkeypatch.setattr(
        chunk_module,
        "extract_pages",
        lambda *_args, **_kwargs: [
            PdfPage(
                page_number=0,
                text=(
                    "Lift Section\n"
                    "Lift is the upward force. Angle of attack affects lift. "
                    "Weather changes visibility."
                ),
            )
        ],
    )
    monkeypatch.setattr(
        chunk_module,
        "_embedding_similarity_fn",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("missing")),
    )

    json_path, md_path, result = write_chunking_implementation_audit(
        tmp_path / "doc.pdf",
        tmp_path / "chunks",
        tmp_path,
        strategies=("embedding_semantic", "hierarchical_parent_child", "proposition_like"),
    )

    assert json_path.name == "chunking_implementation_audit.json"
    assert md_path.exists()
    rows = {row["strategy"]: row for row in result["strategies"]}
    assert rows["embedding_semantic"]["semantic_backend"] == "fallback_lexical"
    assert rows["embedding_semantic"]["name_accuracy"] == "fallback_not_true_semantic_for_this_run"
    assert rows["hierarchical_parent_child"]["implementation_status"] == "partial"
    assert rows["proposition_like"]["returned_context_unit"] == "proposition_only"


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
    for strategy in PILOT_CHUNKING_STRATEGIES:
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
    assert len(indexed) == len(PILOT_CHUNKING_STRATEGIES)
    assert result["ranking"][0]["recall_at_5"] == 1.0
    assert set(result["strategies"]) == set(PILOT_CHUNKING_STRATEGIES)
    assert result["metadata"]["run_manifest"]["rebuild_policy"]["chunks"] is False
    assert result["metadata"]["run_manifest"]["rebuild_policy"]["indexes"] is True
    assert result["strategies"]["fixed_window"]["aggregate"]["retrieval"]["recall_at_5"] == 1.0
    assert result["strategies"]["fixed_window"]["records"][0]["gold"]["gold_level"] == "page"
    assert result["strategies"]["fixed_window"]["explanation"]
    assert result["strategies"]["fixed_window"]["recommendation"]


def write_benchmark_v2_gold(path: Path) -> None:
    payload = {
        "label_set": "test_benchmark_v2",
        "labels": [
            {
                "cq_id": "q-supported",
                "question": "What affects lift?",
                "question_type": "relation_causal",
                "source_document": "doc",
                "source_page": 0,
                "gold_level": "span",
                "expected_abstention": False,
                "evidence_spans": [{"page": 0, "text": "Angle of attack affects lift."}],
                "key_entities": ["angle of attack", "lift"],
                "answer_key": "Angle of attack affects lift.",
            },
            {
                "cq_id": "q-no-answer",
                "question": "What is the current METAR?",
                "question_type": "insufficient_evidence",
                "source_document": "doc",
                "source_page": -1,
                "gold_level": "no_answer",
                "expected_abstention": True,
                "evidence_spans": [],
                "expected_chunk_ids": [],
                "key_entities": ["current METAR"],
                "answer_key": "",
            },
        ],
    }
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_write_chunking_comparison_v2_with_mock_retriever(tmp_path: Path) -> None:
    gold_path = tmp_path / "benchmark_v2.gold.json"
    chunks_dir = tmp_path / "chunks"
    base_chunks_path = chunks_dir / "doc.fixed_small.benchmark_v2.jsonl"
    write_benchmark_v2_gold(gold_path)
    chunks_dir.mkdir()
    for strategy in ("fixed_small", "recursive_large"):
        write_chunks_jsonl(
            [make_chunk(strategy)],
            chunks_dir / f"doc.{strategy}.benchmark_v2.jsonl",
        )

    indexed = []

    def fake_index_builder(chunks_path, index_dir, collection_name, reset):
        indexed.append((chunks_path, index_dir, collection_name, reset))
        Path(index_dir).mkdir(parents=True, exist_ok=True)
        (Path(index_dir) / "index.bin").write_text("index", encoding="utf-8")
        return {"chunks_indexed": 1}

    def fake_retriever(question, index_dir, collection_name, top_k):
        if "METAR" in question:
            return [
                {
                    "chunk_id": f"{collection_name}-metar",
                    "page": 0,
                    "rank": 1,
                    "score": 0.5,
                    "source": "vector",
                    "text": "The current METAR context is not in PHAK Chapter 4.",
                    "metadata": {},
                }
            ][:top_k]
        return [
            {
                "chunk_id": f"{collection_name}-hit",
                "page": 0,
                "rank": 1,
                "score": 1.0,
                "source": "vector",
                "text": "Angle of attack affects lift.",
                "metadata": {},
            }
        ][:top_k]

    json_path, md_path, failure_json, failure_md, result, failures = write_chunking_comparison_v2(
        tmp_path / "doc.pdf",
        gold_path,
        chunks_dir,
        tmp_path / "indexes",
        tmp_path,
        strategies=("fixed_small", "recursive_large"),
        rebuild_chunks=False,
        index_builder=fake_index_builder,
        retriever=fake_retriever,
    )

    assert json_path.name == "chunking_comparison_benchmark_v2.json"
    assert md_path.exists()
    assert failure_json.name == "chunking_failure_cards_benchmark_v2.json"
    assert failure_md.exists()
    assert len(indexed) == 2
    assert base_chunks_path.exists()
    assert result["metadata"]["label_breakdown"]["supported_total"] == 1
    assert result["metadata"]["label_breakdown"]["no_answer_total"] == 1
    fixed = result["strategies"]["fixed_small"]["aggregate"]
    assert fixed["retrieval_supported_only"]["recall_at_5"] == 1.0
    assert fixed["retrieval_confidence_intervals_supported_only"]["recall_at_5"]["n"] == 1
    assert fixed["retrieval_confidence_intervals_supported_only"]["recall_at_5"]["seed"] == 17
    assert fixed["no_answer_diagnostics"]["key_entity_overlap_rate_at_5"] == 1.0
    assert "relation_causal" in fixed["category_breakdown"]
    assert "fixed" in result["chunk_size_sensitivity"]
    assert result["strategies"]["fixed_small"]["records"][0]["top_k_metrics"]["3"]["recall"]
    assert failures["strategies"]["fixed_small"]["no_answer_retrieved_misleading_context"][
        "samples_total"
    ] == 1
    assert "Chunk Size Sensitivity" in md_path.read_text(encoding="utf-8")

    topk = build_chunking_topk_sensitivity_v2_from_result(result)
    assert set(topk["rankings"]) == {"3", "5", "10", "20"}
    assert topk["strategies"]["fixed_small"]["top_k"]["5"]["n"] == 1

    category = build_chunking_category_analysis_v2_from_result(result)
    assert category["best_by_category"]["relation_causal"]["strategy"] == "fixed_small"
    assert category["best_by_category"]["insufficient_evidence"]["strategy"] == "diagnostic_only"


def test_write_chunking_comparison_v2_fixed_budget_output(tmp_path: Path) -> None:
    gold_path = tmp_path / "benchmark_v2.gold.json"
    chunks_dir = tmp_path / "chunks"
    write_benchmark_v2_gold(gold_path)
    chunks_dir.mkdir()
    write_chunks_jsonl(
        [make_chunk("fixed_large")],
        chunks_dir / "doc.fixed_large.benchmark_v2.jsonl",
    )

    def fake_index_builder(chunks_path, index_dir, collection_name, reset):
        Path(index_dir).mkdir(parents=True, exist_ok=True)
        return {"chunks_indexed": 1}

    def fake_retriever(question, index_dir, collection_name, top_k):
        return [
            {
                "chunk_id": f"{collection_name}-{idx}",
                "page": 0,
                "rank": idx + 1,
                "score": 1.0 - idx / 100,
                "source": "vector",
                "text": "Angle of attack affects lift." if idx == 0 else "extra context " * 20,
                "metadata": {},
            }
            for idx in range(top_k)
        ]

    json_path, md_path, *_rest = write_chunking_comparison_v2(
        tmp_path / "doc.pdf",
        gold_path,
        chunks_dir,
        tmp_path / "indexes",
        tmp_path,
        strategies=("fixed_large",),
        rebuild_chunks=False,
        index_builder=fake_index_builder,
        retriever=fake_retriever,
        evaluation_mode="fixed_context_budget",
        context_budget_chars=80,
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert json_path.name == "chunking_comparison_benchmark_v2_budget.json"
    assert md_path.name == "chunking_comparison_benchmark_v2_budget.md"
    assert payload["metadata"]["evaluation_mode"] == "fixed_context_budget"
    record = payload["strategies"]["fixed_large"]["records"][0]
    assert record["context_budget"]["context_budget_chars"] == 80
    assert record["context_budget"]["scored_context_chars"] <= 80


def test_build_chunking_failure_cards_v2_has_all_failure_types() -> None:
    result = {
        "strategies": {
            "fixed_small": {
                "aggregate": {"chunking": {"avg_chars": 100.0, "p95_chars": 200}},
                "records": [],
            }
        }
    }

    cards = build_chunking_failure_cards_v2(result)

    assert set(cards["strategies"]["fixed_small"]) >= {
        "missed_gold_evidence_at_5",
        "chunk_too_small_lost_context",
        "chunk_too_large_low_precision",
        "section_boundary_split",
        "semantic_boundary_error",
        "cross_page_evidence_split",
        "no_answer_retrieved_misleading_context",
        "proposition_context_loss",
        "parent_child_not_used",
    }
