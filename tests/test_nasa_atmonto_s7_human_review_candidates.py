from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_s7_human_review_candidates import (
    build_nasa_atmonto_s7_human_review_candidates,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_build_human_review_candidates_selects_failures_and_coverage(tmp_path: Path) -> None:
    s7_path = tmp_path / "s7.json"
    llm_path = tmp_path / "llm.json"
    _write_json(
        s7_path,
        {
            "records": [
                {
                    "cq_id": "CQ::1",
                    "template_id": "T1",
                    "question": "What is affected?",
                    "answer_set": ["controlledNASelement=BNA"],
                    "expected_abstention": False,
                    "results": {
                        "mode-a": {
                            "fused_chunks": [{"chunk_id": "c1", "source_id": "S1", "text": "CTL ELEMENT: BNA"}],
                            "graph_triples": [
                                {
                                    "triple_id": "t1",
                                    "predicate": "controlledNASelement",
                                    "object": "BNA",
                                    "evidence_text": "CTL ELEMENT: BNA",
                                }
                            ],
                        }
                    },
                },
                {
                    "cq_id": "CQ::2",
                    "template_id": "T2",
                    "question": "What condition?",
                    "answer_set": ["impactingConditionMessage=STAFFING / STAFFING"],
                    "expected_abstention": False,
                    "results": {"mode-a": {"fused_chunks": [], "graph_triples": []}},
                },
            ]
        },
    )
    _write_json(
        llm_path,
        {
            "metadata": {"selected_case_count": 2},
            "answer_quality": {"aggregate_by_mode": {"mode-a": {"answer_correctness": 0.5}}},
            "records": [
                {
                    "cq_id": "CQ::1",
                    "template_id": "T1",
                    "source_id": "S1",
                    "mode": "mode-a",
                    "answer": "BNA",
                    "answer_values": [{"predicate": "controlledNASelement", "value": "BNA"}],
                    "metrics": {
                        "answer_correctness": True,
                        "evidence_faithfulness": True,
                        "unsupported_claim_rate": 0.0,
                    },
                },
                {
                    "cq_id": "CQ::2",
                    "template_id": "T2",
                    "source_id": "S2",
                    "mode": "mode-a",
                    "answer": "STAFFING",
                    "answer_values": [{"predicate": "impactingCondition", "value": "staffing"}],
                    "metrics": {
                        "answer_correctness": False,
                        "evidence_faithfulness": False,
                        "unsupported_claim_rate": 1.0,
                    },
                },
            ],
        },
    )

    result = build_nasa_atmonto_s7_human_review_candidates(
        repo_root=tmp_path,
        s7_answer_report_path=s7_path,
        s7_llm_report_path=llm_path,
    )

    assert result["status"] == "candidate_package_created"
    assert result["metadata"]["failure_candidate_count"] == 1
    assert result["metadata"]["coverage_candidate_count"] == 1
    assert [item["priority"] for item in result["candidates"]] == [
        "failure",
        "coverage_success",
    ]
    assert result["candidates"][1]["evidence"]["source_chunks"][0]["chunk_id"] == "c1"
