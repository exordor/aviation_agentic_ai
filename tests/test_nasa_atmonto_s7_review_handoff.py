from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_s7_review_handoff import (
    ARTIFACTS,
    build_nasa_atmonto_s7_review_handoff,
    write_nasa_atmonto_s7_review_handoff,
)


def _write_text(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("fixture\n", encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_fixture_reports(tmp_path: Path) -> None:
    for _label, rel_path, _purpose in ARTIFACTS:
        if rel_path.endswith(".json"):
            _write_json(tmp_path / rel_path, {"status": "fixture_ready"})
        else:
            _write_text(tmp_path / rel_path)
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json",
        {
            "status": "broad_answer_review_packet_created",
            "metadata": {
                "case_count": 60,
                "failure_case_count": 3,
                "coverage_success_case_count": 57,
            },
        },
    )
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_s7_answer_review_import.json",
        {
            "status": "review_import_rejected",
            "metadata": {
                "can_import": False,
                "reviewed_csv_exists": False,
            },
        },
    )
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_s7_answer_review_decisions.json",
        {
            "status": "s7_answer_review_decisions_pending",
            "metadata": {
                "completed_case_count": 0,
                "pending_case_count": 60,
                "invalid_case_count": 0,
                "human_review_completed": False,
            },
        },
    )
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_sota_goal_audit.json",
        {
            "metadata": {
                "s7_review_completion_mode": "none",
                "s7_completion_scope": "pending",
                "s7_human_answer_review_completed": False,
                "s7_expert_certification_completed": False,
            },
            "completion_gate": {
                "passed": False,
                "failed_criteria": [
                    "no_remaining_blockers",
                    "s7_internal_answer_diagnostic_completed",
                ],
            },
        },
    )


def test_s7_review_handoff_summarizes_pending_review_state(tmp_path: Path) -> None:
    _write_fixture_reports(tmp_path)

    result = build_nasa_atmonto_s7_review_handoff(repo_root=tmp_path)

    assert result["status"] == "s7_review_handoff_created"
    assert result["metadata"]["case_count"] == 60
    assert result["metadata"]["failure_case_count"] == 3
    assert result["metadata"]["coverage_success_case_count"] == 57
    assert result["metadata"]["import_status"] == "review_import_rejected"
    assert result["metadata"]["decision_status"] == "s7_answer_review_decisions_pending"
    assert result["metadata"]["completed_case_count"] == 0
    assert result["metadata"]["pending_case_count"] == 60
    assert result["metadata"]["automated_review_status"] is None
    assert result["metadata"]["review_completion_mode"] == "none"
    assert result["metadata"]["completion_scope"] == "pending"
    assert result["metadata"]["human_answer_review_completed"] is False
    assert result["metadata"]["expert_certification_completed"] is False
    assert result["metadata"]["completion_gate_passed"] is False
    assert result["metadata"]["failed_completion_criteria"] == [
        "no_remaining_blockers",
        "s7_internal_answer_diagnostic_completed",
    ]
    assert result["metadata"]["present_artifact_count"] == result["metadata"]["artifact_count"]
    assert all(artifact["present"] for artifact in result["artifacts"])
    assert "does not certify answer correctness" in result["claim_boundary"]


def test_write_s7_review_handoff_outputs_json_and_markdown(tmp_path: Path) -> None:
    _write_fixture_reports(tmp_path)

    json_path, md_path, result = write_nasa_atmonto_s7_review_handoff(
        output_dir=tmp_path / "reports/stages",
        repo_root=tmp_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["status"] == "s7_review_handoff_created"
    markdown = md_path.read_text(encoding="utf-8")
    assert "NASA ATMONTO S7 Review Handoff" in markdown
    assert "reports/stages/nasa_atmonto_s7_answer_review_worksheet.html" in markdown
    assert "failure-priority cases first" in markdown
    assert "build_nasa_atmonto_sota_goal_audit.py --require-complete" in markdown
    assert "build_nasa_atmonto_sota_goal_audit.py --require-human-review" in markdown
    assert "This handoff is a reviewer-facing work aid" in markdown
    assert "Automated consistency diagnostics" in markdown
