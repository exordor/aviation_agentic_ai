from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_s7_llm_answer_generation import (
    S7_LLM_ANSWER_MODES,
    build_s7_llm_answer_prompt,
    build_nasa_atmonto_s7_llm_answer_generation,
    result_from_llm_payload,
    write_nasa_atmonto_s7_llm_answer_generation,
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _source_report() -> dict:
    return {
        "status": "s7_answer_generation_evaluated",
        "records": [
            {
                "cq_id": "QT-Q01-AFFECTED-NAS-ELEMENTS::2026-05-19:079",
                "template_id": "QT-Q01-AFFECTED-NAS-ELEMENTS",
                "source_id": "2026-05-19:079",
                "question": "Which NAS elements are affected?",
                "expected_abstention": False,
                "answer_set": ["controlledNASelement=BNA"],
                "results": {
                    "routed_token_matched_live_tfidf_graphrag": {
                        "requested_mode": "routed_token_matched_live_tfidf_graphrag",
                        "underlying_mode": "hybrid_graphrag",
                        "evidence_route": "source_span_plus_critic_gated_s4_graph",
                        "answer": "controlledNASelement=BNA. Citations: c1, t1.",
                        "answer_values": [{"predicate": "controlledNASelement", "value": "BNA"}],
                        "fused_chunks": [
                            {
                                "chunk_id": "atcscc-2026-05-19-079-p1-c1",
                                "page": 1,
                                "text": "CONSTRAINED FACILITIES: BNA",
                                "source_id": "2026-05-19:079",
                            }
                        ],
                        "graph_triples": [
                            {
                                "triple_id": "t1",
                                "chunk_id": "atcscc-2026-05-19-079-p1-c1",
                                "page": 1,
                                "predicate": "controlledNASelement",
                                "object": "BNA",
                                "evidence_text": "CONSTRAINED FACILITIES: BNA",
                                "source_id": "2026-05-19:079",
                            }
                        ],
                        "context_budget": {"estimated_context_tokens": 6},
                        "runtime": {"retrieval_latency_ms": 0.1},
                        "target_source_retrieved": True,
                    },
                    "routed_token_matched_dense_graphrag": {
                        "requested_mode": "routed_token_matched_dense_graphrag",
                        "underlying_mode": "hybrid_graphrag",
                        "evidence_route": "source_span_plus_critic_gated_s4_graph",
                        "answer": "controlledNASelement=BNA. Citations: c1, t1.",
                        "answer_values": [{"predicate": "controlledNASelement", "value": "BNA"}],
                        "fused_chunks": [
                            {
                                "chunk_id": "atcscc-2026-05-19-079-p1-c1",
                                "page": 1,
                                "text": "CONSTRAINED FACILITIES: BNA",
                                "source_id": "2026-05-19:079",
                            }
                        ],
                        "graph_triples": [
                            {
                                "triple_id": "t1",
                                "chunk_id": "atcscc-2026-05-19-079-p1-c1",
                                "page": 1,
                                "predicate": "controlledNASelement",
                                "object": "BNA",
                                "evidence_text": "CONSTRAINED FACILITIES: BNA",
                                "source_id": "2026-05-19:079",
                            }
                        ],
                        "context_budget": {"estimated_context_tokens": 6},
                        "runtime": {"retrieval_latency_ms": 0.1},
                        "target_source_retrieved": True,
                    },
                },
            }
        ],
    }


def _fake_runner(
    _system_prompt: str,
    _user_prompt: str,
    _temperature: float,
    _max_tokens: int,
) -> str:
    return json.dumps(
        {
            "answer": "controlledNASelement=BNA.",
            "answer_values": [{"predicate": "controlledNASelement", "value": "BNA"}],
            "abstain": False,
            "citations": ["atcscc-2026-05-19-079-p1-c1", "t1"],
            "rationale": "The source chunk and graph triple identify BNA.",
        }
    )


def test_build_nasa_atmonto_s7_llm_answer_generation_scores_runner_output(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "s7_answer.json"
    _write_json(source_path, _source_report())

    result = build_nasa_atmonto_s7_llm_answer_generation(
        repo_root=tmp_path,
        s7_answer_report_path=source_path,
        max_cases_per_mode=1,
        max_cases_per_template=1,
        runner=_fake_runner,
    )

    assert result["status"] == "s7_llm_answer_generation_evaluated"
    assert result["metadata"]["modes"] == list(S7_LLM_ANSWER_MODES)
    assert result["metadata"]["selected_case_count"] == 2
    for metrics in result["answer_quality"]["aggregate_by_mode"].values():
        assert metrics["llm_answered_total"] == 1
        assert metrics["answer_correctness"] == 1.0
        assert metrics["citation_precision"] == 1.0
        assert metrics["unsupported_claim_rate"] == 0.0
    by_template = result["answer_quality"]["aggregate_by_template"]
    assert by_template["QT-Q01-AFFECTED-NAS-ELEMENTS"][
        "routed_token_matched_live_tfidf_graphrag"
    ]["llm_answered_total"] == 1


def test_write_nasa_atmonto_s7_llm_answer_generation_records_not_run(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "s7_answer.json"
    _write_json(source_path, _source_report())
    output_dir = tmp_path / "reports"

    json_path, md_path, result = write_nasa_atmonto_s7_llm_answer_generation(
        output_dir=output_dir,
        repo_root=tmp_path,
        s7_answer_report_path=source_path,
        max_cases_per_mode=1,
        max_cases_per_template=1,
        run_llm=False,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["status"] == "s7_llm_answer_generation_not_run"
    assert result["answer_quality"]["aggregate_by_mode"][
        "routed_token_matched_live_tfidf_graphrag"
    ]["not_run_total"] == 1
    markdown = md_path.read_text(encoding="utf-8")
    assert "Fixed-Budget LLM Answer Generation" in markdown
    assert "CQ Template Breakdown" in markdown
    assert "Run LLM requested: False" in markdown


def test_result_from_llm_payload_normalizes_atcscc_time_window() -> None:
    result = result_from_llm_payload(
        {},
        {
            "answer": "The advisory is effective from 191322 to 191630.",
            "answer_values": [{"predicate": "EFFECTIVE TIME", "value": "191322-191630"}],
            "citations": ["atcscc-2026-05-19-032-p1-c1"],
        },
        source_id="2026-05-19:032",
    )

    assert result["answer_values"] == [
        {"predicate": "effectiveStartTime", "value": "2026-05-19T13:22:00Z"},
        {"predicate": "effectiveEndTime", "value": "2026-05-19T16:30:00Z"},
    ]


def test_result_from_llm_payload_normalizes_cross_day_atcscc_time_window() -> None:
    result = result_from_llm_payload(
        {},
        {
            "answer": "The advisory is effective from 151918 to 160030.",
            "answer_values": [{"predicate": "EFFECTIVE TIME", "value": "151918-160030"}],
            "citations": ["atcscc-2026-05-15-063-p1-c1"],
        },
        source_id="2026-05-15:063",
    )

    assert result["answer_values"] == [
        {"predicate": "effectiveStartTime", "value": "2026-05-15T19:18:00Z"},
        {"predicate": "effectiveEndTime", "value": "2026-05-16T00:30:00Z"},
    ]


def test_result_from_llm_payload_repairs_iso_time_window_from_target_evidence() -> None:
    result = result_from_llm_payload(
        {
            "fused_chunks": [
                {
                    "source_id": "2026-05-15:063",
                    "text": "EFFECTIVE TIME: 151918-160030",
                }
            ]
        },
        {
            "answer": "The advisory is effective until 2026-05-16T00:03:00Z.",
            "answer_values": [
                {"predicate": "effectiveStartTime", "value": "2026-05-15T19:18:00Z"},
                {"predicate": "effectiveEndTime", "value": "2026-05-16T00:03:00Z"},
            ],
            "citations": ["atcscc-2026-05-15-063-p1-c1"],
        },
        source_id="2026-05-15:063",
    )

    assert result["answer_values"] == [
        {"predicate": "effectiveStartTime", "value": "2026-05-15T19:18:00Z"},
        {"predicate": "effectiveEndTime", "value": "2026-05-16T00:30:00Z"},
    ]


def test_result_from_llm_payload_does_not_repair_from_wrong_source_evidence() -> None:
    result = result_from_llm_payload(
        {
            "fused_chunks": [
                {
                    "source_id": "2026-05-19:144",
                    "text": "EFFECTIVE TIME: 191000-191100",
                }
            ]
        },
        {
            "answer": "The advisory is effective until 2026-05-16T00:03:00Z.",
            "answer_values": [
                {"predicate": "effectiveStartTime", "value": "2026-05-15T19:18:00Z"},
                {"predicate": "effectiveEndTime", "value": "2026-05-16T00:03:00Z"},
            ],
            "citations": ["atcscc-2026-05-19-144-p1-c1"],
        },
        source_id="2026-05-15:063",
    )

    assert result["answer_values"] == [
        {"predicate": "effectiveStartTime", "value": "2026-05-15T19:18:00Z"},
        {"predicate": "effectiveEndTime", "value": "2026-05-16T00:03:00Z"},
    ]


def test_result_from_llm_payload_clears_answer_values_when_abstaining() -> None:
    result = result_from_llm_payload(
        {},
        {
            "answer": "abstain",
            "answer_values": [{"predicate": "abstain", "value": "True"}],
            "abstain": True,
            "citations": ["atcscc-2026-05-19-032-p1-c1"],
        },
        source_id="2026-05-19:032",
    )

    assert result["answer_values"] == []


def test_s7_llm_prompt_requests_atcscc_time_window_normalization() -> None:
    _, user_prompt = build_s7_llm_answer_prompt(_source_report()["records"][0], {}, "mode")

    assert "normalize raw DDHHMM-DDHHMM" in user_prompt
    assert "effectiveStartTime and effectiveEndTime" in user_prompt
