from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.evaluation.gold import GoldLabel
from aviation_agentic_ai.reporting.sufficiency_eval import write_sufficiency_evaluation
from aviation_agentic_ai.retrieval.sufficiency import (
    detect_risk_category,
    evaluate_evidence_sufficiency,
)


def test_sufficiency_risk_category_detection() -> None:
    assert detect_risk_category("What is the current METAR?")[0] == "live_weather"
    assert detect_risk_category("Can ATC clear me through this airspace?")[0] == "atc_clearance"
    assert detect_risk_category("What V-speeds should I use in this aircraft?")[0] == (
        "aircraft_specific_vspeeds"
    )
    assert detect_risk_category("How does angle of attack affect lift?")[0] == "training_question"


def test_no_answer_operational_question_abstains() -> None:
    decision = evaluate_evidence_sufficiency(
        "Should I depart today based on the current weather?",
        {"fused_chunks": [{"chunk_id": "c1", "text": "Lift depends on air density."}]},
    )

    assert decision["decision"] == "abstain"
    assert decision["risk_category"] in {"live_weather", "go_no_go_decision"}


def test_supported_question_answers_when_expected_chunk_retrieved() -> None:
    label = GoldLabel(
        cq_id="q1",
        source_document="doc",
        source_page=1,
        question="How does angle of attack affect lift?",
        expected_chunk_ids=("c1",),
        key_entities=("angle of attack", "lift"),
        gold_level="chunk",
    )
    decision = evaluate_evidence_sufficiency(
        label.question,
        {"fused_chunks": [{"chunk_id": "c1", "text": "Angle of attack affects lift."}]},
        gold_label=label,
    )

    assert decision["decision"] == "answer"
    assert decision["evaluation_mode"] == "gold_aided_benchmark"
    assert decision["gold_aided_expected_evidence_used"] is True
    assert decision["evidence_signals"]["expected_evidence_match"] is True


def test_supported_question_evidence_only_mode_does_not_use_expected_chunks() -> None:
    decision = evaluate_evidence_sufficiency(
        "How does angle of attack affect lift?",
        {"fused_chunks": [{"chunk_id": "wrong", "text": "Angle of attack affects lift."}]},
    )

    assert decision["decision"] == "answer"
    assert decision["evaluation_mode"] == "evidence_only"
    assert decision["gold_aided_expected_evidence_used"] is False
    assert decision["evidence_signals"]["expected_evidence_match"] is False


def test_sufficiency_evaluation_report_counts_false_answers(tmp_path: Path) -> None:
    gold_path = tmp_path / "gold.json"
    retrieval_path = tmp_path / "retrieval.json"
    gold_path.write_text(
        json.dumps(
            {
                "labels": [
                    {
                        "cq_id": "q1",
                        "source_document": "doc",
                        "source_page": 1,
                        "question": "How does angle of attack affect lift?",
                        "question_type": "supported_factual",
                        "expected_chunk_ids": ["c1"],
                        "evidence_spans": [],
                        "key_entities": ["angle of attack", "lift"],
                        "answer_key": "Angle of attack affects lift.",
                        "gold_level": "chunk",
                        "expected_abstention": False,
                    },
                    {
                        "cq_id": "q2",
                        "source_document": "doc",
                        "source_page": -1,
                        "question": "What is the current NOTAM?",
                        "question_type": "insufficient_evidence",
                        "expected_chunk_ids": [],
                        "evidence_spans": [],
                        "key_entities": ["NOTAM"],
                        "answer_key": "Insufficient evidence.",
                        "gold_level": "no_answer",
                        "expected_abstention": True,
                    },
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    retrieval_path.write_text(
        json.dumps(
            {
                "scenarios": {
                    "hybrid_hops2_v5_h8": {
                        "records": [
                            {"cq_id": "q1", "hits": [{"chunk_id": "c1", "text": "Angle of attack affects lift."}]},
                            {"cq_id": "q2", "hits": [{"chunk_id": "c2", "text": "Weather changes."}]},
                        ]
                    }
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )

    json_path, md_path, result = write_sufficiency_evaluation(
        gold_path,
        retrieval_path,
        tmp_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["metrics"]["supported_answer_decision_accuracy"] == 1.0
    assert result["metrics"]["abstention_accuracy"] == 1.0
    assert result["metrics"]["insufficient_evidence_abstention_accuracy"] == 1.0
    assert result["metrics"]["false_answer_rate"] == 0.0
    assert result["metrics"]["false_abstention_rate"] == 0.0
    assert result["metrics"]["evidence_only_supported_answer_decision_accuracy"] == 1.0
    assert result["metrics"]["evidence_only_false_answer_rate"] == 0.0
    assert result["metrics"]["advisory_boundary_violation_count"] == 0
    assert result["metrics"]["boundary_violation_count"] == 0
    ci = result["confidence_intervals"]["false_answer_rate"]
    assert ci["n"] == 1
    assert ci["confidence"] == 0.95
    assert ci["seed"] == 17
    markdown = md_path.read_text(encoding="utf-8")
    assert "Confidence Intervals" in markdown
    assert "gold-aided benchmark validation" in markdown
    assert "evidence-only diagnostic" in markdown
