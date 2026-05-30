from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.evaluation.gold import GoldLabel
from aviation_agentic_ai.evaluation.metrics import answer_metrics, retrieval_metrics
from aviation_agentic_ai.reporting.evaluation_protocol import (
    EVIDENCE_GAPS,
    METRIC_INTERPRETATION_NOTES,
    write_evaluation_protocol_review,
)


def test_retrieval_metrics_include_mainstream_ir_and_context_recall() -> None:
    hits = [
        {"chunk_id": "wrong-1", "page": 1, "text": "Other evidence."},
        {"chunk_id": "wrong-2", "page": 1, "text": "Other evidence."},
        {"chunk_id": "wrong-3", "page": 1, "text": "Other evidence."},
        {"chunk_id": "wrong-4", "page": 1, "text": "Other evidence."},
        {"chunk_id": "wrong-5", "page": 1, "text": "Other evidence."},
        {"chunk_id": "c2", "page": 2, "text": "Lift causes induced drag."},
    ]
    gold = GoldLabel(
        cq_id="q1",
        source_document="doc",
        source_page=2,
        expected_chunk_ids=("c1", "c2"),
        gold_level="chunk",
    )

    metrics = retrieval_metrics(hits, gold)

    assert metrics["recall_at_5"] is False
    assert metrics["recall_at_10"] is True
    assert metrics["precision_at_5"] == 0.0
    assert metrics["mrr_at_5"] == 0.0
    assert metrics["mrr_at_10"] == 0.1667
    assert metrics["ndcg_at_10"] > 0
    assert metrics["context_recall"] == 0.5


def test_answer_metrics_include_citation_precision_and_recall() -> None:
    metrics = answer_metrics(
        {
            "answer": "Citations: c1, t1, page 3, t999.",
            "fused_chunks": [{"chunk_id": "c1", "page": 3}],
            "graph_triples": [{"triple_id": "t1", "chunk_id": "c1", "page": 3}],
        }
    )

    assert metrics["citation_precision"] == 0.75
    assert metrics["citation_recall"] == 1.0
    assert "t999" in metrics["detected_citations"]
    assert metrics["citation_scoring_method"] == "deterministic_heuristic"


def test_evaluation_protocol_report_generation(tmp_path: Path) -> None:
    json_path, md_path, result = write_evaluation_protocol_review(
        tmp_path,
        project_root=tmp_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["metadata"]["scoring_policy"] == "layered_metrics_no_mixed_overall_score"
    assert any(group["layer"] == "retrieval" for group in result["primary_thesis_metrics"])
    assert any(metric["metric"] == "NDCG@10" for metric in result["metric_catalog"])
    catalog = {metric["metric"]: metric for metric in result["metric_catalog"]}
    implemented = {metric["metric"] for metric in result["implemented_metrics"]}
    pending = {metric["metric"] for metric in result["missing_or_pending_metrics"]}

    assert len(catalog) == 29
    assert catalog["Recall@5"]["field"] == "recall_at_5"
    assert catalog["Recall@5"]["kind"] == "mainstream_ir"
    assert catalog["Context Precision@5"]["field"] == "context_precision_at_5"
    assert catalog["Citation Precision"]["kind"] == "deterministic_answer_heuristic"
    assert catalog["Abstention Accuracy"]["reports"] == (
        "sufficiency_evaluation",
        "robustness_evaluation",
    )
    assert {
        "Recall@5",
        "MRR@10",
        "Context Recall",
        "Citation Precision",
        "Abstention Accuracy",
    } <= implemented
    assert pending == {"Faithfulness", "Answer Correctness", "Answer Relevance"}
    assert len(result["primary_thesis_metrics"]) == 5
    assert len(result["report_presence"]) == 14
    assert any(
        note["topic"] == "precision_denominators"
        for note in payload["metric_interpretation_notes"]
    )
    assert "single mixed overall score" in md_path.read_text(encoding="utf-8")
    assert "Precision@5 divides by the fixed cutoff" in md_path.read_text(encoding="utf-8")


def test_evaluation_protocol_declares_review_and_certification_limits() -> None:
    gaps = "\n".join(EVIDENCE_GAPS)

    assert "no human expert verification" in gaps
    assert "not external aviation-expert certification" in gaps
    assert "LLM-estimated" in gaps


def test_metric_interpretation_notes_prevent_ci_and_precision_overclaims() -> None:
    notes = "\n".join(note["note"] for note in METRIC_INTERPRETATION_NOTES)

    assert "not interchangeable" in notes
    assert "n=0" in notes
    assert "undefined" in notes
    assert "measured zero performance" in notes
