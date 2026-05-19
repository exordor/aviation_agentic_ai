import json
from pathlib import Path

from aviation_agentic_ai.reporting.evidence_eval import write_evidence_level_evaluation


def _experiment_report(chunk_id: str) -> dict:
    result = {
        "fused_chunks": [
            {
                "chunk_id": chunk_id,
                "page": 0,
                "text": "Angle of attack affects lift.",
            }
        ],
        "graph_triples": [
            {
                "triple_id": "t1",
                "chunk_id": chunk_id,
                "page": 0,
                "subject": "angle of attack",
                "predicate": "affects",
                "object": "lift",
                "evidence_text": "Angle of attack affects lift.",
            }
        ],
        "answer": f"Angle of attack affects lift. Citations: {chunk_id}, t1, page 0",
    }
    return {
        "metadata": {"questions_total": 1},
        "aggregate": {},
        "records": [
            {
                "cq_id": "cq1",
                "question": "How does angle of attack affect lift?",
                "results": {mode: result for mode in ("vector", "graph", "hybrid")},
            }
        ],
    }


def test_evidence_level_evaluation_separates_layered_metrics(tmp_path: Path) -> None:
    gold_path = tmp_path / "gold.json"
    fixed_path = tmp_path / "fixed.json"
    structure_path = tmp_path / "structure.json"
    gold_path.write_text(
        json.dumps(
            {
                "labels": [
                    {
                        "cq_id": "cq1",
                        "source_document": "doc",
                        "source_page": 0,
                        "expected_chunk_ids": ["doc-p00-c00"],
                        "evidence_spans": [
                            {"page": 0, "text": "Angle of attack affects lift."}
                        ],
                        "key_entities": ["angle of attack", "lift"],
                        "answer_key": "Angle of attack affects lift.",
                        "gold_level": "span",
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    fixed_path.write_text(json.dumps(_experiment_report("doc-p00-c00")) + "\n", encoding="utf-8")
    structure_path.write_text(json.dumps(_experiment_report("doc-p00-c00")) + "\n", encoding="utf-8")

    json_path, md_path, result = write_evidence_level_evaluation(
        gold_path,
        tmp_path,
        fixed_hybrid_path=fixed_path,
        structure_aware_hybrid_path=structure_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert "overall" not in result
    aggregate = result["experiments"]["fixed_window"]["aggregate"]["hybrid"]
    assert aggregate["chunk_recall_at_5"] == 1.0
    assert aggregate["span_hit_rate"] == 1.0
    assert aggregate["key_entity_coverage"] == 1.0
    assert aggregate["citation_validity"] == 1.0
    assert aggregate["answer_support_distribution"]["supported"] == 1
