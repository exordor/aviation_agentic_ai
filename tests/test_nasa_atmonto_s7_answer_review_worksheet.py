from __future__ import annotations

import csv
import json
from pathlib import Path

from aviation_agentic_ai.reporting.atmonto.s7.answer_review_worksheet import (
    build_nasa_atmonto_s7_answer_review_worksheet,
    write_nasa_atmonto_s7_answer_review_worksheet,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "review_id",
        "priority",
        "template_id",
        "source_id",
        "mode",
        "question",
        "expected_answer_set",
        "answer_values",
        "answer",
        "auto_answer_correctness",
        "auto_evidence_faithfulness",
        "auto_unsupported_claim_rate",
        "auto_citation_precision",
        "auto_citation_recall",
        "review_decision",
        "evidence_support",
        "citation_sufficiency",
        "profile_boundary",
        "reviewer_notes",
        "reviewer_id_or_initials",
        "reviewer_role",
        "reviewed_at",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _packet() -> dict:
    return {
        "status": "broad_answer_review_packet_created",
        "metadata": {"case_count": 1},
        "cases": [
            {
                "review_id": "S7-BR-001",
                "priority": "failure",
                "template_id": "QT-Q01-AFFECTED-NAS-ELEMENTS",
                "source_id": "2026-05-19:079",
                "mode": "routed_token_matched_live_tfidf_graphrag",
                "question": "Which NAS elements are affected?",
                "answer": "BNA Citations: c1, t1.",
                "raw_response": '{"answer":"BNA"}',
                "expected_answer_set": ["controlledNASelement=BNA"],
                "answer_values": [{"predicate": "controlledNASelement", "value": "BNA"}],
                "metrics": {
                    "answer_correctness": True,
                    "evidence_faithfulness": True,
                    "unsupported_claim_rate": 0.0,
                },
                "evidence": {
                    "source_chunks": [
                        {"chunk_id": "c1", "text": "CTL ELEMENT: BNA"},
                    ],
                    "graph_triples": [
                        {
                            "triple_id": "t1",
                            "predicate": "controlledNASelement",
                            "object": "BNA",
                            "evidence_text": "CTL ELEMENT: BNA",
                        },
                    ],
                },
                "review_questions": [
                    "Does each answer value appear directly supported?",
                ],
            }
        ],
    }


def test_worksheet_builds_cases_and_prefills_existing_review_csv(tmp_path: Path) -> None:
    _write_json(tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json", _packet())
    _write_csv(
        tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv",
        [
            {
                "review_id": "S7-BR-001",
                "review_decision": "correct",
                "evidence_support": "fully_supported",
                "citation_sufficiency": "sufficient",
                "profile_boundary": "no",
                "reviewer_notes": "checked against source span",
                "reviewer_id_or_initials": "R1",
                "reviewer_role": "human_reviewer",
                "reviewed_at": "2026-06-03",
            }
        ],
    )

    result = build_nasa_atmonto_s7_answer_review_worksheet(repo_root=tmp_path)

    assert result["status"] == "answer_review_worksheet_created"
    assert result["metadata"]["case_count"] == 1
    assert result["metadata"]["failure_case_count"] == 1
    assert result["cases"][0]["csv_row"]["review_decision"] == "correct"
    assert result["cases"][0]["csv_row"]["reviewer_notes"] == "checked against source span"
    assert "review_decision" in result["csv_columns"]


def test_write_worksheet_outputs_static_html(tmp_path: Path) -> None:
    _write_json(tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json", _packet())
    _write_csv(
        tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv",
        [{"review_id": "S7-BR-001"}],
    )

    html_path, result = write_nasa_atmonto_s7_answer_review_worksheet(
        output_dir=tmp_path / "reports/stages",
        repo_root=tmp_path,
    )

    assert html_path.exists()
    assert result["metadata"]["human_review_completed"] is False
    html = html_path.read_text(encoding="utf-8")
    assert "NASA ATMONTO S7 Answer Review Worksheet" in html
    assert "Download reviewed CSV" in html
    assert "S7-BR-001" in html
    assert "CTL ELEMENT: BNA" in html
    assert "correct" in html
