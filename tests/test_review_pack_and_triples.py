from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.benchmark_review_pack import (
    build_answer_eval_subset_payload,
    build_reviewed_subset_payload,
    write_benchmark_review_pack,
)
from aviation_agentic_ai.reporting.triple_semantic_review import write_triple_semantic_review


def _label(cq_id: str, question_type: str, expected_abstention: bool = False) -> dict:
    return {
        "cq_id": cq_id,
        "question": f"What does the chapter say about {cq_id}?",
        "question_type": question_type,
        "answer_key": "Source-backed answer.",
        "source_document": "doc",
        "source_page": -1 if expected_abstention else 1,
        "expected_abstention": expected_abstention,
        "expected_chunk_ids": [] if expected_abstention else ["c1"],
        "evidence_spans": [] if expected_abstention else [{"page": 1, "text": "Source-backed answer."}],
        "key_entities": ["source", "answer"],
        "gold_level": "no_answer" if expected_abstention else "span",
        "review": {"status": "machine_seeded_requires_manual_review"},
        "tags": [question_type],
    }


def _payload_with_counts(counts: dict[str, int]) -> dict:
    labels = []
    for question_type, count in counts.items():
        for index in range(count):
            labels.append(
                _label(
                    f"{question_type}-{index:03d}",
                    question_type,
                    expected_abstention=question_type == "insufficient_evidence",
                )
            )
    return {
        "label_set": "test",
        "review_status": "machine_seeded_requires_manual_review",
        "labels": labels,
    }


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


def test_reviewed_subset_selects_core_60_and_marks_pending_review() -> None:
    payload = _payload_with_counts(
        {
            "concept_definition": 15,
            "relation_causal": 15,
            "cross_page": 10,
            "insufficient_evidence": 20,
            "supported_factual": 5,
        }
    )

    subset = build_reviewed_subset_payload(payload)

    assert len(subset["labels"]) == 60
    assert subset["review_status"] == "project_review_pending_external_review"
    assert subset["label_distribution"] == {
        "concept_definition": 15,
        "cross_page": 10,
        "insufficient_evidence": 20,
        "relation_causal": 15,
    }
    assert subset["labels"][0]["review"]["status"] == "project_review_pending_external_review"
    assert subset["labels"][0]["review"]["project_author_review_status"] == (
        "needs_project_author_review"
    )
    assert subset["labels"][0]["review"]["external_aviation_expert_certified"] is False


def test_answer_eval_subset_is_stratified_and_heuristic_only() -> None:
    payload = _payload_with_counts(
        {
            "supported_factual": 8,
            "concept_definition": 8,
            "relation_causal": 8,
            "cross_page": 8,
            "paraphrase": 8,
            "terminology_variation": 8,
            "insufficient_evidence": 12,
        }
    )

    subset = build_answer_eval_subset_payload(payload)

    assert len(subset["labels"]) == 35
    assert subset["subset_policy"]["score_method"] == "deterministic_heuristic"
    assert subset["subset_policy"]["llm_as_judge_enabled"] is False
    assert subset["label_distribution"]["insufficient_evidence"] == 10


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
    assert result["summary"]["reviewed_total"] == 0
    assert result["summary"]["needs_review_total"] == 1
    annotation = result["records"][0]["annotation"]
    assert annotation["status"] == "needs_manual_review"
    assert annotation["subject_correct"] == "needs_review"
    assert annotation["evidence_supports_triple"] == "needs_review"


def test_triple_semantic_review_computes_rates_only_for_reviewed_annotations(
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
    annotations_path = tmp_path / "annotations.json"
    annotations_path.write_text(
        json.dumps(
            {
                "records": [
                    {
                        "triple": {"triple_id": "t1"},
                        "annotation": {
                            "subject_correct": True,
                            "object_correct": True,
                            "predicate_correct": True,
                            "direction_correct": True,
                            "evidence_supports_triple": True,
                            "too_generic": False,
                            "duplicate_or_near_duplicate": False,
                            "status": "reviewed",
                            "reviewer_notes": "ok",
                        },
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    _, md_path, result = write_triple_semantic_review(
        kg_path,
        tmp_path,
        sample_size=1,
        annotations_path=annotations_path,
    )

    assert result["summary"]["reviewed_total"] == 1
    assert result["summary"]["needs_review_total"] == 0
    assert result["summary"]["semantic_correctness_rate"] == 1.0
    assert result["summary"]["evidence_support_rate"] == 1.0
    assert "Semantic correctness rate" in md_path.read_text(encoding="utf-8")
