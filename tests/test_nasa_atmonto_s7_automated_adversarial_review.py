from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_s7_automated_adversarial_review import (
    build_nasa_atmonto_s7_automated_adversarial_review,
    write_nasa_atmonto_s7_automated_adversarial_review,
)


def _case(review_id: str, *, failing: bool = False) -> dict:
    expected = ["impactingConditionMessage=STAFFING / STAFFING"]
    answer_values = [{"predicate": "impactingConditionMessage", "value": "STAFFING / STAFFING"}]
    if failing:
        answer_values.append({"predicate": "impactingCondition", "value": "STAFFING"})
    return {
        "review_id": review_id,
        "source_id": "2026-05-15:067",
        "template_id": "QT-Q01-CAUSE-CONDITION",
        "priority": "failure" if failing else "coverage_success",
        "expected_answer_set": expected,
        "answer_values": answer_values,
        "expected_abstention": False,
        "metrics": {
            "answer_correctness": not failing,
            "abstention_correctness": True,
            "evidence_faithfulness": not failing,
            "unsupported_claim_rate": 0.5 if failing else 0.0,
            "citation_precision": 1.0,
            "detected_citations": ["t1"],
            "valid_citations": ["t1"],
        },
    }


def _write_packet(path: Path, *, cases: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "status": "broad_answer_review_packet_created",
                "metadata": {"case_count": len(cases)},
                "cases": cases,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_automated_adversarial_review_scores_role_verdicts(tmp_path: Path) -> None:
    cases = [_case("S7-BR-001"), _case("S7-BR-002", failing=True)]
    _write_packet(
        tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json",
        cases=cases,
    )

    result = build_nasa_atmonto_s7_automated_adversarial_review(repo_root=tmp_path)

    assert result["status"] == "automated_consistency_diagnostic_completed"
    assert result["metadata"]["automated_review_completed"] is True
    assert result["metadata"]["automated_consistency_diagnostic_completed"] is True
    assert result["metadata"]["human_review_completed"] is False
    assert result["metadata"]["external_expert_certified"] is False
    assert result["metadata"]["accepted_case_count"] == 1
    assert result["metadata"]["rejected_case_count"] == 1
    assert result["case_reviews"][0]["automated_verdict"] == "accepted"
    assert result["case_reviews"][1]["automated_verdict"] == "rejected"
    failed_roles = {
        item["role"]
        for item in result["case_reviews"][1]["role_reviews"]
        if item["verdict"] != "pass"
    }
    assert failed_roles == {
        "evidence_verifier",
        "cq_contract_validator",
        "ontology_profile_validator",
        "consistency_critic",
    }


def test_write_automated_adversarial_review_outputs_reports(tmp_path: Path) -> None:
    _write_packet(
        tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json",
        cases=[_case("S7-BR-001"), _case("S7-BR-002", failing=True)],
    )

    json_path, md_path, result = write_nasa_atmonto_s7_automated_adversarial_review(
        output_dir=tmp_path / "reports/stages",
        repo_root=tmp_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["status"] == "automated_consistency_diagnostic_completed"
    markdown = md_path.read_text(encoding="utf-8")
    assert "NASA ATMONTO S7 Automated Consistency Diagnostic" in markdown
    assert "cannot replace human answer review" in markdown
    assert "S7-BR-002" in markdown
