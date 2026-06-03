from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_s7_candidate_adjudication import (
    build_nasa_atmonto_s7_candidate_adjudication,
    write_nasa_atmonto_s7_candidate_adjudication,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _candidate_report() -> dict:
    return {
        "metadata": {"candidate_count": 2, "failure_candidate_count": 1},
        "candidates": [
            {
                "review_id": "S7-HR-001",
                "priority": "failure",
                "template_id": "QT-Q01-CAUSE-CONDITION",
                "source_id": "2026-05-15:067",
                "mode": "routed_token_matched_dense_graphrag",
                "expected_answer_set": ["impactingConditionMessage=STAFFING / STAFFING"],
                "answer_values": [
                    {"predicate": "impactingCondition", "value": "other"},
                    {"predicate": "impactingConditionMessage", "value": "STAFFING / STAFFING"},
                ],
                "evidence": {
                    "source_chunks": [
                        {
                            "chunk_id": "c1",
                            "text": "IMPACTING CONDITION: STAFFING / STAFFING",
                        }
                    ],
                    "graph_triples": [
                        {
                            "triple_id": "t1",
                            "predicate": "impactingCondition",
                            "object": "other",
                            "evidence_text": "IMPACTING CONDITION: STAFFING / STAFFING",
                        },
                        {
                            "triple_id": "t2",
                            "predicate": "impactingConditionMessage",
                            "object": "STAFFING / STAFFING",
                            "evidence_text": "IMPACTING CONDITION: STAFFING / STAFFING",
                        },
                    ],
                },
            },
            {
                "review_id": "S7-HR-002",
                "priority": "coverage_success",
                "template_id": "QT-Q01-AFFECTED-NAS-ELEMENTS",
                "source_id": "2026-05-19:079",
                "mode": "routed_token_matched_live_tfidf_graphrag",
                "expected_answer_set": ["controlledNASelement=BNA"],
                "answer_values": [{"predicate": "controlledNASelement", "value": "BNA"}],
                "evidence": {"source_chunks": [], "graph_triples": []},
            },
        ],
    }


def test_candidate_adjudication_classifies_staffing_boundary_case(tmp_path: Path) -> None:
    candidate_path = tmp_path / "candidates.json"
    llm_path = tmp_path / "llm.json"
    _write_json(candidate_path, _candidate_report())
    _write_json(llm_path, {"metadata": {"selected_case_count": 60}})

    result = build_nasa_atmonto_s7_candidate_adjudication(
        repo_root=tmp_path,
        candidate_report_path=candidate_path,
        s7_llm_report_path=llm_path,
    )

    assert result["metadata"]["strict_main_metrics_changed"] is False
    assert result["metadata"]["human_review"] is False
    assert result["summary"]["profile_or_gold_boundary_failures"] == 1
    assert result["summary"]["model_hallucination_count"] == 0
    failure = result["adjudications"][0]
    assert failure["adjudication"] == "profile_or_gold_boundary_case"
    assert failure["failure_type"] == "extra_coarse_impacting_condition_for_staffing"
    assert failure["would_pass_if_extra_condition_ignored"] is True
    assert "STAFFING" in failure["recommended_action"]
    assert result["adjudications"][1]["adjudication"] == "coverage_success_not_adjudicated"


def test_write_candidate_adjudication_outputs_markdown(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports" / "stages"
    _write_json(report_dir / "nasa_atmonto_s7_human_review_candidates.json", _candidate_report())
    _write_json(
        report_dir / "nasa_atmonto_s7_llm_answer_generation.json",
        {"metadata": {"selected_case_count": 60}},
    )

    json_path, md_path, result = write_nasa_atmonto_s7_candidate_adjudication(
        output_dir=report_dir,
        repo_root=tmp_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["status"] == "candidate_adjudication_created"
    markdown = md_path.read_text(encoding="utf-8")
    assert "NASA ATMONTO S7 Candidate Adjudication" in markdown
    assert "profile_or_gold_boundary_case" in markdown
    assert "Strict main metrics changed: False" in markdown
