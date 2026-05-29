from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.benchmark_review_pack import write_benchmark_review_pack
from aviation_agentic_ai.reporting.triple_semantic_review import write_triple_semantic_review


def test_benchmark_review_pack_flags_machine_wording_and_writes_review_copy(
    tmp_path: Path,
) -> None:
    gold_path = tmp_path / "benchmark.json"
    reviewed_path = tmp_path / "reviewed.json"
    gold_path.write_text(
        json.dumps(
            {
                "review_status": "machine_seeded_requires_manual_review",
                "labels": [
                    {
                        "cq_id": "q1",
                        "question": (
                            "According to PHAK Chapter 4, what source-backed fact "
                            "connects lift with drag in the evidence mentioning lift?"
                        ),
                        "question_type": "supported_factual",
                        "answer_key": "Lift causes induced drag.",
                        "source_page": 4,
                        "expected_abstention": False,
                        "key_entities": ["lift", "drag"],
                        "evidence_spans": [{"page": 4, "text": "Lift causes induced drag."}],
                        "review": {"status": "machine_seeded_requires_manual_review"},
                    },
                    {
                        "cq_id": "q2",
                        "question": "What is the current NOTAM?",
                        "question_type": "insufficient_evidence",
                        "answer_key": "Insufficient evidence.",
                        "source_page": -1,
                        "expected_abstention": True,
                        "key_entities": ["NOTAM"],
                        "evidence_spans": [],
                        "review": {"status": "machine_seeded_requires_manual_review"},
                    },
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    json_path, md_path, created_reviewed, result = write_benchmark_review_pack(
        gold_path,
        tmp_path,
        reviewed_output_path=reviewed_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert created_reviewed == reviewed_path
    assert result["finding_counts"]["unnatural_machine_generated_wording"] == 1
    assert (
        result["finding_counts"]["insufficient_evidence_label_needs_aviation_safety_review"]
        == 1
    )
    reviewed = json.loads(reviewed_path.read_text(encoding="utf-8"))
    assert reviewed["review_status"] == "manual_review_pending"
    assert reviewed["labels"][0]["review"]["status"] == "needs_manual_review"


def test_triple_semantic_review_initializes_annotations_as_needs_review(
    tmp_path: Path,
) -> None:
    kg_path = tmp_path / "kg.jsonl"
    kg_path.write_text(
        json.dumps(
            {
                "triple_id": "t1",
                "subject": "angle of attack",
                "predicate": "affects",
                "object": "lift",
                "subject_class": "Cl_AngleOfAttack",
                "object_class": "Cl_Lift",
                "source_document": "doc",
                "page": 1,
                "section": "page-1",
                "chunk_id": "c1",
                "evidence_text": "Angle of attack affects lift.",
                "model": "test",
                "confidence": 0.9,
                "extracted_at": "2026-05-30T00:00:00+00:00",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    json_path, md_path, result = write_triple_semantic_review(
        kg_path,
        tmp_path,
        sample_size=1,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["metadata"]["semantic_correctness_claimed"] is False
    annotation = result["records"][0]["annotation"]
    assert annotation["status"] == "needs_manual_review"
    assert annotation["subject_correct"] == "needs_review"
    assert annotation["evidence_supports_triple"] == "needs_review"
