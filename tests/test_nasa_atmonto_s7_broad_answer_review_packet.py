from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.atmonto.s7.broad_answer_review_packet import (
    build_nasa_atmonto_s7_broad_answer_review_packet,
    write_nasa_atmonto_s7_broad_answer_review_packet,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_fixture_reports(tmp_path: Path) -> None:
    stages = tmp_path / "reports/stages"
    _write_json(
        stages / "nasa_atmonto_s7_answer_generation.json",
        {
            "records": [
                {
                    "cq_id": "CQ-001",
                    "question": "Which airport is affected?",
                    "answer_set": ["controlledNASelement=BNA"],
                    "expected_abstention": False,
                    "results": {
                        "mode-a": {
                            "fused_chunks": [
                                {
                                    "chunk_id": "c1",
                                    "source_id": "src-1",
                                    "text": "CTL ELEMENT: BNA",
                                }
                            ],
                            "graph_triples": [
                                {
                                    "triple_id": "t1",
                                    "predicate": "controlledNASelement",
                                    "object": "BNA",
                                    "evidence_text": "CTL ELEMENT: BNA",
                                }
                            ],
                        }
                    },
                }
            ]
        },
    )
    _write_json(
        stages / "nasa_atmonto_s7_llm_answer_generation.json",
        {
            "metadata": {"selected_case_count": 2},
            "records": [
                {
                    "cq_id": "CQ-001",
                    "template_id": "QT-A",
                    "source_id": "src-1",
                    "mode": "mode-a",
                    "answer": "BNA",
                    "answer_values": [{"predicate": "controlledNASelement", "value": "BNA"}],
                    "metrics": {
                        "answer_correctness": True,
                        "evidence_faithfulness": True,
                        "unsupported_claim_rate": 0.0,
                    },
                },
                {
                    "cq_id": "CQ-001",
                    "template_id": "QT-A",
                    "source_id": "src-1",
                    "mode": "mode-a",
                    "answer": "BNA and XYZ",
                    "answer_values": [
                        {"predicate": "controlledNASelement", "value": "BNA"},
                        {"predicate": "controlledNASelement", "value": "XYZ"},
                    ],
                    "metrics": {
                        "answer_correctness": False,
                        "evidence_faithfulness": False,
                        "unsupported_claim_rate": 0.5,
                    },
                },
            ],
        },
    )


def test_broad_answer_review_packet_covers_all_llm_cases(tmp_path: Path) -> None:
    _write_fixture_reports(tmp_path)

    result = build_nasa_atmonto_s7_broad_answer_review_packet(repo_root=tmp_path)

    assert result["status"] == "broad_answer_review_packet_created"
    assert result["metadata"]["case_count"] == 2
    assert result["metadata"]["failure_case_count"] == 1
    assert result["metadata"]["coverage_success_case_count"] == 1
    assert result["metadata"]["human_review_completed"] is False
    assert result["aggregate"]["review_status_counts"] == {
        "auto_success": 1,
        "needs_review": 1,
    }
    assert result["cases"][0]["review_id"] == "S7-BR-001"
    assert result["cases"][1]["priority"] == "failure"


def test_write_broad_answer_review_packet_outputs_json_markdown_and_csv(tmp_path: Path) -> None:
    _write_fixture_reports(tmp_path)

    json_path, md_path, csv_path, result = write_nasa_atmonto_s7_broad_answer_review_packet(
        output_dir=tmp_path / "reports/stages",
        repo_root=tmp_path,
    )

    assert result["metadata"]["case_count"] == 2
    assert json_path.exists()
    assert md_path.exists()
    assert csv_path.exists()
    assert "Broad Answer Review Packet" in md_path.read_text(encoding="utf-8")
    csv_text = csv_path.read_text(encoding="utf-8")
    assert "review_decision" in csv_text
    assert "S7-BR-002" in csv_text
