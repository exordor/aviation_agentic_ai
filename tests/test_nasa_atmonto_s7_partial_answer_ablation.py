from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.atmonto.s7.partial_answer_ablation import (
    PARTIAL_ANSWER_MODES,
    build_nasa_atmonto_s7_partial_answer_ablation,
    build_partial_answer_prompt,
    partial_result_from_payload,
    write_nasa_atmonto_s7_partial_answer_ablation,
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _source_report() -> dict:
    route_record = {
        "cq_id": "QT-Q01-ROUTE-SEMANTICS::2026-05-19:074",
        "template_id": "QT-Q01-ROUTE-SEMANTICS",
        "source_id": "2026-05-19:074",
        "question": "What reroute type, reroute reason, and constrained element are represented?",
        "expected_abstention": False,
        "answer_set": ["controlledNASelement=BNA"],
        "results": {},
    }
    for mode in PARTIAL_ANSWER_MODES:
        route_record["results"][mode] = {
            "requested_mode": mode,
            "underlying_mode": "hybrid_graphrag",
            "evidence_route": "source_span_plus_critic_gated_s4_graph",
            "answer": "controlledNASelement=BNA. Citations: c1, t1.",
            "answer_values": [{"predicate": "controlledNASelement", "value": "BNA"}],
            "fused_chunks": [
                {
                    "chunk_id": "atcscc-2026-05-19-074-p1-c1",
                    "page": 1,
                    "text": "CTL ELEMENT: BNA",
                    "source_id": "2026-05-19:074",
                }
            ],
            "graph_triples": [
                {
                    "triple_id": "t1",
                    "chunk_id": "atcscc-2026-05-19-074-p1-c1",
                    "page": 1,
                    "predicate": "controlledNASelement",
                    "object": "BNA",
                    "evidence_text": "CTL ELEMENT: BNA",
                    "source_id": "2026-05-19:074",
                }
            ],
            "context_budget": {"estimated_context_tokens": 10},
            "runtime": {"retrieval_latency_ms": 0.1},
            "target_source_retrieved": True,
        }
    return {"status": "s7_answer_generation_evaluated", "records": [route_record]}


def _partial_runner(
    _system_prompt: str,
    _user_prompt: str,
    _temperature: float,
    _max_tokens: int,
) -> str:
    return json.dumps(
        {
            "answer": "The constrained element is BNA; reroute type and reason are not present.",
            "answer_values": [{"predicate": "controlledNASelement", "value": "BNA"}],
            "abstain": False,
            "citations": ["atcscc-2026-05-19-074-p1-c1", "t1"],
            "missing_predicates": ["reRouteType", "reRouteReason"],
            "rationale": "The evidence says CTL ELEMENT: BNA and provides no reroute reason.",
        }
    )


def test_partial_answer_ablation_scores_supported_route_field(tmp_path: Path) -> None:
    source_path = tmp_path / "s7_answer.json"
    _write_json(source_path, _source_report())

    result = build_nasa_atmonto_s7_partial_answer_ablation(
        repo_root=tmp_path,
        s7_answer_report_path=source_path,
        max_cases_per_mode=1,
        runner=_partial_runner,
    )

    assert result["status"] == "s7_partial_answer_ablation_evaluated"
    assert result["metadata"]["selected_case_count"] == 2
    for metrics in result["answer_quality"]["aggregate_by_mode"].values():
        assert metrics["llm_answered_total"] == 1
        assert metrics["strict_answer_correctness"] == 1.0
        assert metrics["partial_contract_satisfied_rate"] == 1.0
        assert metrics["partial_value_f1"] == 1.0
        assert metrics["payload_abstain_rate"] == 0.0
    assert result["records"][0]["missing_predicates"] == ["reRouteReason", "reRouteType"]


def test_partial_answer_ablation_writer_records_not_run(tmp_path: Path) -> None:
    source_path = tmp_path / "s7_answer.json"
    _write_json(source_path, _source_report())
    output_dir = tmp_path / "reports"

    json_path, md_path, result = write_nasa_atmonto_s7_partial_answer_ablation(
        output_dir=output_dir,
        repo_root=tmp_path,
        s7_answer_report_path=source_path,
        max_cases_per_mode=1,
        run_llm=False,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["status"] == "s7_partial_answer_ablation_not_run"
    markdown = md_path.read_text(encoding="utf-8")
    assert "Route-Semantics Partial-Answer Ablation" in markdown
    assert "Partial contract" in markdown


def test_partial_answer_prompt_makes_abstention_policy_explicit() -> None:
    record = _source_report()["records"][0]
    _system_prompt, user_prompt = build_partial_answer_prompt(
        record,
        record["results"]["routed_token_matched_live_tfidf_graphrag"],
        "routed_token_matched_live_tfidf_graphrag",
    )

    assert "If at least one requested predicate is directly supported" in user_prompt
    assert "missing_predicates" in user_prompt
    assert "Never invent reroute type or reroute reason values" in user_prompt


def test_partial_result_accepts_object_shaped_values_and_citations() -> None:
    result = partial_result_from_payload(
        {
            "fused_chunks": [
                {
                    "chunk_id": "atcscc-2026-05-19-074-p1-c1",
                    "source_id": "2026-05-19:074",
                    "text": "CTL ELEMENT: BNA",
                }
            ],
            "graph_triples": [],
        },
        {
            "answer": "Only the constrained element is supported.",
            "answer_values": {"controlledNASelement": "BNA"},
            "abstain": False,
            "citations": [{"chunk_id": "atcscc-2026-05-19-074-p1-c1"}],
        },
        source_id="2026-05-19:074",
    )

    assert result["answer_values"] == [{"predicate": "controlledNASelement", "value": "BNA"}]
    assert "Citations: atcscc-2026-05-19-074-p1-c1" in result["answer"]
