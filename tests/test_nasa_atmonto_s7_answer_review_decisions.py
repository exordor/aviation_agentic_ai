from __future__ import annotations

import csv
import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_s7_answer_review_decisions import (
    build_nasa_atmonto_s7_answer_review_decisions,
    write_nasa_atmonto_s7_answer_review_decisions,
)

FIELDNAMES = [
    "review_id",
    "review_decision",
    "evidence_support",
    "citation_sufficiency",
    "profile_boundary",
    "reviewer_notes",
    "reviewer_id_or_initials",
    "reviewer_role",
    "reviewed_at",
]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _write_packet(path: Path) -> None:
    _write_json(
        path,
        {
            "status": "broad_answer_review_packet_created",
            "cases": [
                {"review_id": "S7-BR-001"},
                {"review_id": "S7-BR-002"},
            ],
        },
    )


def test_review_decision_status_is_pending_when_csv_is_blank(tmp_path: Path) -> None:
    _write_packet(tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json")
    _write_csv(
        tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv",
        [{"review_id": "S7-BR-001"}, {"review_id": "S7-BR-002"}],
    )

    result = build_nasa_atmonto_s7_answer_review_decisions(repo_root=tmp_path)

    assert result["status"] == "s7_answer_review_decisions_pending"
    assert result["metadata"]["human_review_completed"] is False
    assert result["metadata"]["pending_case_count"] == 2
    assert result["aggregate"]["row_status_counts"] == {"pending": 2}


def test_review_decision_status_is_completed_when_all_rows_are_valid(tmp_path: Path) -> None:
    _write_packet(tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json")
    _write_csv(
        tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv",
        [
            _complete_row("S7-BR-001", "correct"),
            _complete_row("S7-BR-002", "profile_boundary"),
        ],
    )

    result = build_nasa_atmonto_s7_answer_review_decisions(repo_root=tmp_path)

    assert result["status"] == "s7_answer_review_decisions_completed"
    assert result["metadata"]["human_review_completed"] is True
    assert result["metadata"]["completed_case_count"] == 2
    assert result["aggregate"]["review_decision_counts"] == {
        "correct": 1,
        "profile_boundary": 1,
    }


def test_review_decision_status_reports_invalid_rows(tmp_path: Path) -> None:
    _write_packet(tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json")
    row = _complete_row("S7-BR-001", "correct")
    row["reviewer_role"] = "llm"
    _write_csv(
        tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv",
        [row, {"review_id": "S7-BR-002", "review_decision": "correct"}],
    )

    result = build_nasa_atmonto_s7_answer_review_decisions(repo_root=tmp_path)

    assert result["status"] == "s7_answer_review_decisions_partial_or_invalid"
    assert result["metadata"]["human_review_completed"] is False
    assert result["metadata"]["invalid_case_count"] == 2
    errors = {item["review_id"]: item["errors"] for item in result["row_results"]}
    assert "invalid reviewer_role: llm" in errors["S7-BR-001"]
    assert "missing evidence_support" in errors["S7-BR-002"]


def test_write_review_decisions_outputs_json_and_markdown(tmp_path: Path) -> None:
    _write_packet(tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json")
    _write_csv(
        tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv",
        [{"review_id": "S7-BR-001"}, {"review_id": "S7-BR-002"}],
    )

    json_path, md_path, result = write_nasa_atmonto_s7_answer_review_decisions(
        output_dir=tmp_path / "reports/stages",
        repo_root=tmp_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["metadata"]["pending_case_count"] == 2
    markdown = md_path.read_text(encoding="utf-8")
    assert "NASA ATMONTO S7 Answer Review Decisions" in markdown
    assert "Human review completed: `False`" in markdown


def test_write_review_decisions_accepts_explicit_review_csv_path(tmp_path: Path) -> None:
    _write_packet(tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json")
    reviewed_csv = tmp_path / "exports/reviewed.csv"
    _write_csv(
        reviewed_csv,
        [
            _complete_row("S7-BR-001", "correct"),
            _complete_row("S7-BR-002", "profile_boundary"),
        ],
    )

    json_path, md_path, result = write_nasa_atmonto_s7_answer_review_decisions(
        output_dir=tmp_path / "reports/stages",
        repo_root=tmp_path,
        review_csv_path=reviewed_csv,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["status"] == "s7_answer_review_decisions_completed"
    assert result["metadata"]["review_csv_path"] == "exports/reviewed.csv"
    assert result["metadata"]["human_review_completed"] is True


def _complete_row(review_id: str, decision: str) -> dict[str, str]:
    return {
        "review_id": review_id,
        "review_decision": decision,
        "evidence_support": "fully_supported",
        "citation_sufficiency": "sufficient",
        "profile_boundary": "no",
        "reviewer_notes": "",
        "reviewer_id_or_initials": "R1",
        "reviewer_role": "human_reviewer",
        "reviewed_at": "2026-06-03",
    }
