from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.atmonto.audit.reviewer_defense_audit import (
    build_nasa_atmonto_reviewer_defense_audit,
    write_nasa_atmonto_reviewer_defense_audit,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_fixture_reports(tmp_path: Path) -> None:
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_sota_goal_audit.json",
        {
            "status": "sota_goal_audit_created",
            "completion_claim": "internal_diagnostic_package_complete",
            "metadata": {
                "s7_completion_scope": "internal_diagnostic",
                "s7_human_answer_review_completed": False,
                "s7_expert_certification_completed": False,
            },
            "completion_gate": {"passed": True},
            "claim_scope_gates": [
                {
                    "id": "internal_diagnostic_package",
                    "passed": True,
                    "status": "Complete for internal thesis diagnostics.",
                    "blocked_by": [],
                },
                {
                    "id": "human_answer_quality_review",
                    "passed": False,
                    "status": "Human answer review remains incomplete.",
                    "blocked_by": ["reviewed S7 answer CSV is not complete"],
                },
            ],
        },
    )
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_formal_experiment_scoring.json",
        {
            "status": "scored",
            "gold_status": {"record_count": 100},
            "systems": [
                {
                    "system_id": "S2_llm_schema_slice",
                    "structural_metrics": {
                        "accepted_fact_count": 584,
                        "rejected_fact_count": 124,
                        "structural_acceptance_rate": 0.8249,
                    },
                    "semantic_metrics": {
                        "precision": 0.2062,
                        "recall": 0.1866,
                        "f1": 0.1959,
                    },
                },
                {
                    "system_id": "S3_llm_schema_slice_validator_repair",
                    "structural_metrics": {
                        "accepted_fact_count": 355,
                        "rejected_fact_count": 41,
                        "structural_acceptance_rate": 0.8965,
                    },
                    "semantic_metrics": {
                        "precision": 0.2423,
                        "recall": 0.1337,
                        "f1": 0.1723,
                    },
                },
                {
                    "system_id": "S4_hybrid_backbone_enrichment",
                    "structural_metrics": {
                        "accepted_fact_count": 686,
                        "rejected_fact_count": 0,
                        "structural_acceptance_rate": 1.0,
                    },
                    "semantic_metrics": {
                        "precision": 0.7168,
                        "recall": 0.7636,
                        "f1": 0.7395,
                    },
                },
            ],
        },
    )
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_s7_retrieval.json",
        {
            "status": "s7_retrieval_gate_evaluated",
            "metadata": {"retrieval_case_count": 317},
            "aggregate_by_mode": {
                "token_matched_live_tfidf_vector": {
                    "answer_set": {"micro_f1": 0.8235},
                    "target_source_hit_rate": 1.0,
                    "avg_estimated_context_tokens": 38.96,
                },
                "token_matched_dense_embedding_vector": {
                    "answer_set": {"micro_f1": 0.5166},
                    "target_source_hit_rate": 0.571,
                    "avg_estimated_context_tokens": 38.96,
                },
                "routed_token_matched_live_tfidf_graphrag": {
                    "answer_set": {"micro_f1": 0.8534},
                    "target_source_hit_rate": 1.0,
                    "avg_estimated_context_tokens": 38.96,
                },
                "routed_token_matched_dense_graphrag": {
                    "answer_set": {"micro_f1": 0.6105},
                    "target_source_hit_rate": 0.9685,
                    "avg_estimated_context_tokens": 38.96,
                },
            },
        },
    )
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_s7_llm_answer_generation.json",
        {
            "status": "s7_llm_answer_generation_evaluated",
            "metadata": {
                "selected_case_count": 60,
                "max_cases_per_template": 5,
                "reviewer_model": "gpt-5.4-mini",
            },
            "answer_quality": {
                "aggregate_by_mode": {
                    "routed_token_matched_live_tfidf_graphrag": {
                        "selected_total": 30,
                        "answer_correctness": 0.9667,
                        "citation_recall": 0.6084,
                        "evidence_faithfulness": 0.9667,
                        "unsupported_claim_rate": 0.0167,
                        "avg_estimated_context_tokens": 33.03,
                    }
                }
            },
        },
    )
    _write_json(
        tmp_path / "reports/stages/nasa_atmonto_s7_automated_adversarial_review.json",
        {
            "status": "automated_consistency_diagnostic_completed",
            "metadata": {
                "reviewed_case_count": 60,
                "accepted_case_count": 57,
                "rejected_case_count": 3,
            },
        },
    )


def test_reviewer_defense_audit_summarizes_claim_gates_and_metrics(
    tmp_path: Path,
) -> None:
    _write_fixture_reports(tmp_path)

    result = build_nasa_atmonto_reviewer_defense_audit(repo_root=tmp_path)

    assert result["status"] == "reviewer_defense_audit_created"
    assert result["metadata"]["completion_scope"] == "internal_diagnostic"
    assert result["metadata"]["human_answer_review_completed"] is False
    assert result["metadata"]["expert_certification_completed"] is False
    assert result["metadata"]["retrieval_case_count"] == 317
    assert result["metadata"]["s7_llm_selected_case_count"] == 60
    assert result["metadata"]["formal_systems"][0]["system_id"] == "S2_llm_schema_slice"
    assert result["metadata"]["formal_systems"][1]["f1"] == 0.1723
    assert len(result["reviewer_findings"]) == 6
    assert "not human review" in result["safe_thesis_claim"]


def test_write_reviewer_defense_audit_outputs_markdown(tmp_path: Path) -> None:
    _write_fixture_reports(tmp_path)

    json_path, md_path, result = write_nasa_atmonto_reviewer_defense_audit(
        output_dir=tmp_path / "reports/stages",
        repo_root=tmp_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["metadata"]["completion_claim"] == "internal_diagnostic_package_complete"
    markdown = md_path.read_text(encoding="utf-8")
    assert "NASA ATMONTO Reviewer Defense Audit" in markdown
    assert "No-Go Claims" in markdown
    assert "S2_llm_schema_slice" in markdown
    assert "selected 60-case LLM diagnostics" in markdown
