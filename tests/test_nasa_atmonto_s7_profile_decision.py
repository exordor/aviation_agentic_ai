from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_s7_profile_decision import (
    build_nasa_atmonto_s7_profile_decision,
    write_nasa_atmonto_s7_profile_decision,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _llm_report() -> dict:
    return {
        "metadata": {"selected_case_count": 1},
        "answer_quality": {
            "aggregate_by_mode": {
                "routed_token_matched_live_tfidf_graphrag": {
                    "selected_total": 1,
                    "llm_answered_total": 1,
                    "answer_correctness": 0.0,
                    "unsupported_claim_rate": 0.5,
                    "citation_precision": 1.0,
                    "citation_recall": 1.0,
                    "evidence_faithfulness": 0.0,
                    "abstention_correctness": 1.0,
                    "avg_estimated_context_tokens": 12,
                    "status_counts": {"answered": 1},
                    "not_run_total": 0,
                    "failed_total": 0,
                },
                "routed_token_matched_dense_graphrag": {
                    "selected_total": 0,
                    "llm_answered_total": 0,
                    "answer_correctness": None,
                    "unsupported_claim_rate": None,
                    "citation_precision": None,
                    "citation_recall": None,
                    "evidence_faithfulness": None,
                    "abstention_correctness": None,
                    "avg_estimated_context_tokens": 0,
                    "status_counts": {},
                    "not_run_total": 0,
                    "failed_total": 0,
                },
            }
        },
        "records": [
            {
                "cq_id": "QT-Q01-CAUSE-CONDITION::2026-05-15:067",
                "template_id": "QT-Q01-CAUSE-CONDITION",
                "source_id": "2026-05-15:067",
                "mode": "routed_token_matched_live_tfidf_graphrag",
                "underlying_mode": "hybrid_graphrag",
                "llm_status": "answered",
                "expected_abstention": False,
                "answer": "STAFFING / STAFFING Citations: c1.",
                "answer_set": ["impactingConditionMessage=STAFFING / STAFFING"],
                "answer_values": [
                    {"predicate": "impactingCondition", "value": "staffing"},
                    {"predicate": "impactingConditionMessage", "value": "STAFFING / STAFFING"},
                ],
                "abstain": False,
                "context_budget": {"estimated_context_tokens": 12},
                "metrics": {
                    "answer_correctness": False,
                    "citation_precision": 1.0,
                    "citation_recall": 1.0,
                    "evidence_faithfulness": False,
                    "unsupported_claim_rate": 0.5,
                    "abstention_correctness": True,
                },
            }
        ],
    }


def _adjudication_report() -> dict:
    return {
        "adjudications": [
            {
                "review_id": "S7-HR-001",
                "priority": "failure",
                "template_id": "QT-Q01-CAUSE-CONDITION",
                "source_id": "2026-05-15:067",
                "mode": "routed_token_matched_live_tfidf_graphrag",
                "adjudication": "profile_or_gold_boundary_case",
                "failure_type": "extra_coarse_impacting_condition_for_staffing",
                "would_pass_if_extra_condition_ignored": True,
                "extra_answer_values": [{"predicate": "impactingCondition", "value": "staffing"}],
            }
        ]
    }


def test_profile_decision_recomputes_staffing_what_if_without_changing_main_metrics(
    tmp_path: Path,
) -> None:
    llm_path = tmp_path / "llm.json"
    adjudication_path = tmp_path / "adjudication.json"
    _write_json(llm_path, _llm_report())
    _write_json(adjudication_path, _adjudication_report())

    result = build_nasa_atmonto_s7_profile_decision(
        repo_root=tmp_path,
        s7_llm_report_path=llm_path,
        s7_adjudication_path=adjudication_path,
    )

    assert result["metadata"]["strict_main_metrics_changed"] is False
    assert result["metadata"]["gold_or_profile_changed"] is False
    assert result["metadata"]["corrected_record_count"] == 1
    live = result["summary"]["what_if_aggregate_by_mode"][
        "routed_token_matched_live_tfidf_graphrag"
    ]
    assert live["answer_correctness"] == 1.0
    assert live["unsupported_claim_rate"] == 0.0
    assert result["records"][0]["profile_decision_what_if"]["corrected_by_policy"] is True
    assert result["records"][0]["answer_values"] == [
        {"predicate": "impactingConditionMessage", "value": "STAFFING / STAFFING"}
    ]


def test_write_profile_decision_outputs_markdown(tmp_path: Path) -> None:
    stages = tmp_path / "reports" / "stages"
    _write_json(stages / "nasa_atmonto_s7_llm_answer_generation.json", _llm_report())
    _write_json(stages / "nasa_atmonto_s7_candidate_adjudication.json", _adjudication_report())

    json_path, md_path, result = write_nasa_atmonto_s7_profile_decision(
        output_dir=stages,
        repo_root=tmp_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["status"] == "profile_decision_what_if_created"
    markdown = md_path.read_text(encoding="utf-8")
    assert "NASA ATMONTO S7 Profile Decision What-If" in markdown
    assert "predicate_whitelist_current_profile" in markdown
    assert "Gold or profile changed: False" in markdown
