import json
from pathlib import Path

from aviation_agentic_ai.evaluation.benchmark_validation import validate_benchmark
from aviation_agentic_ai.reporting.benchmark_v2 import write_benchmark_v2_summary


def _write_chunks(path: Path, text: str = "Angle of attack affects lift.") -> None:
    path.write_text(
        json.dumps(
            {
                "chunk_id": "doc-structure_aware-p00-c00",
                "source_document": "doc",
                "source_path": "doc.pdf",
                "page": 0,
                "chunk_index": 0,
                "char_start": 0,
                "char_end": len(text),
                "text": text,
                "strategy": "structure_aware",
            }
        )
        + "\n",
        encoding="utf-8",
    )


def _supported_label(**overrides):
    label = {
        "answer_key": "Angle of attack affects lift.",
        "cq_id": "q1",
        "evidence_spans": [{"page": 0, "text": "Angle of attack affects lift."}],
        "expected_abstention": False,
        "expected_chunk_ids": ["doc-structure_aware-p00-c00"],
        "gold_level": "span",
        "key_entities": ["angle of attack", "lift"],
        "question": "What affects lift?",
        "question_type": "supported_factual",
        "review": {"status": "llm_review_pending_not_human_certified"},
        "source_document": "doc",
        "source_page": 0,
        "tags": ["supported_factual", "supported"],
    }
    label.update(overrides)
    return label


def _no_answer_label(**overrides):
    label = {
        "answer_key": "Insufficient evidence in PHAK Chapter 4.",
        "cq_id": "q2",
        "evidence_spans": [],
        "expected_abstention": True,
        "expected_chunk_ids": [],
        "gold_level": "no_answer",
        "key_entities": ["current weather"],
        "question": "What is the current weather?",
        "question_type": "insufficient_evidence",
        "review": {"status": "llm_review_pending_not_human_certified"},
        "source_document": "doc",
        "source_page": -1,
        "tags": ["insufficient_evidence", "no_answer"],
    }
    label.update(overrides)
    return label


def _write_benchmark(path: Path, labels: list[dict]) -> None:
    path.write_text(
        json.dumps(
            {
                "label_set": "test_benchmark",
                "review_status": "llm_review_pending_not_human_certified",
                "notes": "test",
                "label_distribution": {"supported_factual": 1},
                "labels": labels,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_benchmark_v2_validates_against_real_chunks() -> None:
    result = validate_benchmark(
        "data/cqs/06_phak_ch4_0.benchmark_v2.gold.json",
        [
            "data/chunks/06_phak_ch4_0.structure_aware.jsonl",
            "data/chunks/06_phak_ch4_0.jsonl",
        ],
    )

    assert result["valid"] is True
    assert result["errors_total"] == 0
    assert result["metadata"]["labels_total"] == 120
    assert result["metadata"]["supported_total"] == 100
    assert result["metadata"]["no_answer_total"] == 20
    assert result["metadata"]["category_counts"]["insufficient_evidence"] == 20
    assert result["metadata"]["evidence_span_validation"]["pass"] is True


def test_benchmark_validation_fails_on_duplicate_ids(tmp_path: Path) -> None:
    chunks = tmp_path / "chunks.jsonl"
    gold = tmp_path / "gold.json"
    _write_chunks(chunks)
    _write_benchmark(gold, [_supported_label(), _supported_label(question="Different?")])

    result = validate_benchmark(gold, [chunks], min_labels=1)

    assert result["valid"] is False
    assert any("Duplicate cq_id `q1`" in error for error in result["errors"])


def test_benchmark_validation_fails_on_missing_evidence(tmp_path: Path) -> None:
    chunks = tmp_path / "chunks.jsonl"
    gold = tmp_path / "gold.json"
    _write_chunks(chunks)
    _write_benchmark(gold, [_supported_label(evidence_spans=[])])

    result = validate_benchmark(gold, [chunks], min_labels=1)

    assert result["valid"] is False
    assert any("missing required field `evidence_spans`" in error for error in result["errors"])


def test_benchmark_validation_fails_when_span_is_not_on_same_page(tmp_path: Path) -> None:
    chunks = tmp_path / "chunks.jsonl"
    gold = tmp_path / "gold.json"
    _write_chunks(chunks)
    _write_benchmark(
        gold,
        [
            _supported_label(
                evidence_spans=[{"page": 0, "text": "This sentence is not in the chunk."}]
            )
        ],
    )

    result = validate_benchmark(gold, [chunks], min_labels=1)

    assert result["valid"] is False
    assert any("does not appear in any source chunk" in error for error in result["errors"])


def test_benchmark_validation_fails_on_bad_no_answer_format(tmp_path: Path) -> None:
    chunks = tmp_path / "chunks.jsonl"
    gold = tmp_path / "gold.json"
    _write_chunks(chunks)
    _write_benchmark(
        gold,
        [
            _no_answer_label(
                expected_chunk_ids=["doc-structure_aware-p00-c00"],
                evidence_spans=[{"page": 0, "text": "Angle of attack affects lift."}],
                source_page=0,
            )
        ],
    )

    result = validate_benchmark(gold, [chunks], min_labels=1)

    assert result["valid"] is False
    assert any("source_page=-1" in error for error in result["errors"])
    assert any("empty expected_chunk_ids" in error for error in result["errors"])
    assert any("empty evidence_spans" in error for error in result["errors"])


def test_benchmark_v2_summary_writes_reports(tmp_path: Path) -> None:
    json_path, md_path, result = write_benchmark_v2_summary(
        "data/cqs/06_phak_ch4_0.benchmark_v2.gold.json",
        [
            "data/chunks/06_phak_ch4_0.structure_aware.jsonl",
            "data/chunks/06_phak_ch4_0.jsonl",
        ],
        tmp_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["validation"]["valid"] is True
    assert result["metadata"]["labels_total"] == 120
