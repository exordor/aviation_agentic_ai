from __future__ import annotations

from pathlib import Path

from aviation_agentic_ai.reporting.atmonto.s7.answer_review_protocol import (
    build_nasa_atmonto_s7_answer_review_protocol,
    write_nasa_atmonto_s7_answer_review_protocol,
)


def test_answer_review_protocol_defines_completion_gate() -> None:
    result = build_nasa_atmonto_s7_answer_review_protocol()

    assert result["status"] == "answer_review_protocol_created"
    assert result["review_scope"]["case_count"] == 60
    assert result["review_scope"]["failure_priority_cases"] == 3
    assert "review_decision" in result["allowed_values"]
    assert "validate_reviewed_csv" in result["commands"]
    assert "human_review_completed=True" in result["claim_boundary"]


def test_write_answer_review_protocol_outputs_markdown(tmp_path: Path) -> None:
    md_path, result = write_nasa_atmonto_s7_answer_review_protocol(
        output_dir=tmp_path / "reports/stages",
        repo_root=tmp_path,
    )

    assert md_path.exists()
    assert result["status"] == "answer_review_protocol_created"
    markdown = md_path.read_text(encoding="utf-8")
    assert "NASA ATMONTO S7 Answer Review Protocol" in markdown
    assert "Completion Gate" in markdown
    assert "validate_reviewed_csv" in markdown
    assert "human_review_completed=true" in markdown
