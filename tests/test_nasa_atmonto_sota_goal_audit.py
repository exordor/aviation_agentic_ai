from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_sota_goal_audit import (
    SOTA_REQUIREMENTS,
    build_nasa_atmonto_sota_goal_audit,
    write_nasa_atmonto_sota_goal_audit,
)


def _write_text(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("fixture\n", encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_all_evidence(tmp_path: Path, *, human_review_completed: bool = False) -> None:
    for requirement in SOTA_REQUIREMENTS:
        for rel_path in requirement["evidence"]:
            path = tmp_path / rel_path
            if path.suffix == ".json":
                _write_json(path, {"status": "fixture_ready"})
            else:
                _write_text(path)
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_formal_experiment_scoring.json",
        {"status": "scored"},
    )
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_s5_s6_agentic_loop.json",
        {"status": "s5_s6_agentic_evidence_gate_scored"},
    )
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_s5_s6_independent_agentic_run.json",
        {"status": "s5_s6_independent_agentic_run_scored"},
    )
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_s5_s6_live_agentic_pilot.json",
        {"status": "s5_s6_live_agentic_pilot_scored"},
    )
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.json",
        {"status": "s5_s6_live_agentic_full_run_scored"},
    )
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_s7_llm_answer_generation.json",
        {"status": "s7_llm_answer_generation_evaluated"},
    )
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_s7_broad_answer_review_packet.json",
        {
            "status": "broad_answer_review_packet_created",
            "metadata": {"case_count": 60},
        },
    )
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_s7_answer_review_decisions.json",
        {
            "status": (
                "s7_answer_review_decisions_completed"
                if human_review_completed
                else "s7_answer_review_decisions_pending"
            ),
            "metadata": {
                "completed_case_count": 60 if human_review_completed else 0,
                "human_review_completed": human_review_completed,
            },
        },
    )
    _write_json(
        tmp_path / "reports/stages/nasa_bga_domain_transfer_pilot.json",
        {
            "status": "second_domain_transfer_pilot_created",
            "metadata": {"transfer_domain": "NASA Beginner's Guide to Aerodynamics"},
        },
    )


def test_sota_goal_audit_maps_requirements_to_present_evidence(tmp_path: Path) -> None:
    _write_all_evidence(tmp_path)

    result = build_nasa_atmonto_sota_goal_audit(repo_root=tmp_path)

    assert result["status"] == "sota_goal_audit_created"
    assert result["completion_claim"] == "active_not_complete"
    assert result["metadata"]["requirement_count"] == len(SOTA_REQUIREMENTS)
    assert result["metadata"]["formal_scoring_status"] == "scored"
    assert result["metadata"]["s5_s6_status"] == "s5_s6_agentic_evidence_gate_scored"
    assert result["metadata"]["s5_s6_independent_status"] == "s5_s6_independent_agentic_run_scored"
    assert result["metadata"]["s5_s6_live_pilot_status"] == "s5_s6_live_agentic_pilot_scored"
    assert result["metadata"]["s5_s6_live_full_run_status"] == "s5_s6_live_agentic_full_run_scored"
    assert result["metadata"]["s7_llm_status"] == "s7_llm_answer_generation_evaluated"
    assert result["metadata"]["s7_broad_review_packet_status"] == "broad_answer_review_packet_created"
    assert result["metadata"]["s7_broad_review_case_count"] == 60
    assert result["metadata"]["s7_answer_review_decision_status"] == "s7_answer_review_decisions_pending"
    assert result["metadata"]["s7_answer_review_completed_case_count"] == 0
    assert result["metadata"]["s7_answer_review_human_completed"] is False
    assert result["metadata"]["s7_automated_adversarial_review_status"] is None
    assert result["metadata"]["s7_automated_adversarial_review_completed"] is False
    assert result["metadata"]["s7_automated_consistency_diagnostic_completed"] is False
    assert result["metadata"]["s7_review_completion_mode"] == "none"
    assert result["metadata"]["s7_completion_scope"] == "pending"
    assert result["metadata"]["s7_answer_review_completed"] is False
    assert result["metadata"]["s7_expert_certification_completed"] is False
    assert result["metadata"]["second_domain_transfer_status"] == "second_domain_transfer_pilot_created"
    assert result["metadata"]["second_domain_transfer_domain"] == "NASA Beginner's Guide to Aerodynamics"
    assert result["metadata"]["status_counts"]["satisfied"] == 5
    assert result["metadata"]["status_counts"]["mostly_satisfied"] == 4
    assert "partial" not in result["metadata"]["status_counts"]
    assert all(item["missing_evidence"] == [] for item in result["requirements"])
    assert "Neither human answer review nor automated consistency diagnostic" in (
        result["remaining_blockers"][0]
    )
    assert len(result["remaining_blockers"]) == 1
    assert result["completion_gate"]["passed"] is False
    assert result["completion_gate"]["failed_criteria"] == [
        "no_remaining_blockers",
        "s7_internal_answer_diagnostic_completed",
    ]
    assert result["claim_scope_gates"][2]["id"] == "human_answer_quality_review"
    assert result["claim_scope_gates"][2]["passed"] is False


def test_write_sota_goal_audit_outputs_json_and_markdown(tmp_path: Path) -> None:
    _write_all_evidence(tmp_path)
    output_dir = tmp_path / "reports/stages"

    json_path, md_path, result = write_nasa_atmonto_sota_goal_audit(
        output_dir=output_dir,
        repo_root=tmp_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert "partial" not in result["metadata"]["status_counts"]
    markdown = md_path.read_text(encoding="utf-8")
    assert "NASA ATMONTO SOTA Goal Completion Audit" in markdown
    assert "Requirement Evidence" in markdown
    assert "active_not_complete" in markdown
    assert "full 100-record live LLM" not in markdown
    assert "S7 broad review packet cases: 60" in markdown
    assert "S7 answer review decision status: `s7_answer_review_decisions_pending`" in markdown
    assert "S7 review completion mode: `none`" in markdown
    assert "S7 completion scope: `pending`" in markdown
    assert "Completion gate passed: `False`" in markdown
    assert "s7_internal_answer_diagnostic_completed" in markdown
    assert "Claim Scope Gates" in markdown
    assert "Second-domain transfer status: `second_domain_transfer_pilot_created`" in markdown
    assert "Neither human answer review nor automated consistency diagnostic" in markdown


def test_sota_goal_completion_gate_passes_when_review_decisions_are_complete(
    tmp_path: Path,
) -> None:
    _write_all_evidence(tmp_path, human_review_completed=True)

    result = build_nasa_atmonto_sota_goal_audit(repo_root=tmp_path)

    assert (
        result["completion_claim"]
        == "sota_comparable_retrospective_case_study_human_reviewed"
    )
    assert result["remaining_blockers"] == []
    assert result["completion_gate"]["passed"] is True
    assert result["completion_gate"]["failed_criteria"] == []
    assert result["metadata"]["s7_answer_review_completed_case_count"] == 60
    assert result["metadata"]["s7_answer_review_human_completed"] is True
    assert result["metadata"]["s7_review_completion_mode"] == "human"
    assert result["metadata"]["s7_completion_scope"] == "human_review"
    assert result["metadata"]["s7_answer_review_completed"] is True


def test_sota_goal_completion_gate_passes_when_automated_review_is_complete(
    tmp_path: Path,
) -> None:
    _write_all_evidence(tmp_path)
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_s7_automated_adversarial_review.json",
        {
            "status": "automated_consistency_diagnostic_completed",
            "metadata": {
                "reviewed_case_count": 60,
                "automated_review_completed": True,
                "automated_consistency_diagnostic_completed": True,
                "human_review_completed": False,
                "external_expert_certified": False,
                "unresolved_conflict_count": 0,
                "accepted_case_count": 57,
                "rejected_case_count": 3,
            },
        },
    )

    result = build_nasa_atmonto_sota_goal_audit(repo_root=tmp_path)

    assert result["completion_claim"] == "internal_diagnostic_package_complete"
    assert result["remaining_blockers"] == []
    assert result["completion_gate"]["passed"] is True
    assert result["completion_gate"]["failed_criteria"] == []
    assert result["metadata"]["s7_answer_review_human_completed"] is False
    assert result["metadata"]["s7_automated_adversarial_review_completed"] is True
    assert result["metadata"]["s7_automated_consistency_diagnostic_completed"] is True
    assert result["metadata"]["s7_review_completion_mode"] == "automated_diagnostic"
    assert result["metadata"]["s7_completion_scope"] == "internal_diagnostic"
    assert result["metadata"]["s7_answer_review_completed"] is False
    assert result["metadata"]["s7_expert_certification_completed"] is False
    assert result["claim_scope_gates"][0]["id"] == "internal_diagnostic_package"
    assert result["claim_scope_gates"][0]["passed"] is True
    assert result["claim_scope_gates"][2]["id"] == "human_answer_quality_review"
    assert result["claim_scope_gates"][2]["passed"] is False
