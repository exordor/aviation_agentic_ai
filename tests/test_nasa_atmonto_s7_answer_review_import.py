from __future__ import annotations

import csv
import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_s7_answer_review_import import (
    build_nasa_atmonto_s7_answer_review_import,
    write_nasa_atmonto_s7_answer_review_import,
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
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
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


def test_review_import_rejects_missing_reviewed_csv(tmp_path: Path) -> None:
    _write_packet(tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json")

    result = build_nasa_atmonto_s7_answer_review_import(
        repo_root=tmp_path,
        reviewed_csv_path=tmp_path / "missing.csv",
    )

    assert result["status"] == "review_import_rejected"
    assert result["metadata"]["can_import"] is False
    assert "reviewed CSV does not exist" in result["failure_reasons"]


def test_review_import_rejects_incomplete_reviewed_csv_without_overwriting(
    tmp_path: Path,
) -> None:
    _write_packet(tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json")
    canonical = tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv"
    reviewed = tmp_path / "exports/reviewed.csv"
    _write_csv(canonical, [{"review_id": "S7-BR-001"}, {"review_id": "S7-BR-002"}])
    _write_csv(reviewed, [_complete_row("S7-BR-001", "correct")])

    _json_path, _md_path, result = write_nasa_atmonto_s7_answer_review_import(
        output_dir=tmp_path / "reports/stages",
        repo_root=tmp_path,
        reviewed_csv_path=reviewed,
        import_if_valid=True,
    )

    assert result["status"] == "review_import_rejected"
    assert result["metadata"]["imported"] is False
    assert "reviewed CSV is missing expected review IDs" in result["failure_reasons"]
    assert "S7-BR-002" in canonical.read_text(encoding="utf-8")


def test_review_import_copies_complete_reviewed_csv_and_backs_up_canonical(
    tmp_path: Path,
) -> None:
    _write_packet(tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json")
    canonical = tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv"
    reviewed = tmp_path / "exports/reviewed.csv"
    _write_csv(canonical, [{"review_id": "S7-BR-001"}, {"review_id": "S7-BR-002"}])
    _write_csv(
        reviewed,
        [
            _complete_row("S7-BR-001", "correct"),
            _complete_row("S7-BR-002", "profile_boundary"),
        ],
    )

    json_path, md_path, result = write_nasa_atmonto_s7_answer_review_import(
        output_dir=tmp_path / "reports/stages",
        repo_root=tmp_path,
        reviewed_csv_path=reviewed,
        import_if_valid=True,
    )

    backup = tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.pre_review_import.csv"
    assert json_path.exists()
    assert md_path.exists()
    assert result["status"] == "review_import_imported"
    assert result["metadata"]["can_import"] is True
    assert result["metadata"]["imported"] is True
    assert backup.exists()
    assert "profile_boundary" in canonical.read_text(encoding="utf-8")
    assert "review_import_imported" in md_path.read_text(encoding="utf-8")


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
