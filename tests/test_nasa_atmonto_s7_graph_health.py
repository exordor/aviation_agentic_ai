from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.atmonto.s7.graph_health import (
    build_nasa_atmonto_s7_graph_health,
    write_nasa_atmonto_s7_graph_health,
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _mode_result(
    *,
    mode: str,
    graph_context_count: int,
    source_context_count: int,
    f1: float | None,
    path_support: float | None,
    target_hit: bool = True,
    expected_abstention: bool = False,
    abstention_correct: bool | None = None,
) -> dict:
    return {
        "requested_mode": mode,
        "underlying_mode": "hybrid_graphrag" if graph_context_count else "vector_rag",
        "retrieval": {"recall_at_5": target_hit, "context_recall": 1.0 if target_hit else 0.0},
        "answer_set": {
            "expected_count": 1,
            "retrieved_count": 1 if f1 else 0,
            "true_positive_count": 1 if f1 == 1.0 else 0,
            "false_positive_count": 0,
            "false_negative_count": 0 if f1 == 1.0 else 1,
            "precision": f1,
            "recall": f1,
            "f1": f1,
            "expected_abstention": expected_abstention,
            "abstention_correct": abstention_correct,
        },
        "path_support": None
        if path_support is None
        else {
            "expected_graph_answer_count": 1,
            "supported_graph_answer_count": int(path_support),
            "path_support_rate": path_support,
        },
        "context_budget": {
            "estimated_context_tokens": graph_context_count * 5 + source_context_count * 3,
            "graph_context_count": graph_context_count,
            "source_context_count": source_context_count,
        },
        "runtime": {"retrieval_latency_ms": 0.1},
        "target_source_retrieved": target_hit,
        "graph_use_decision": {"decision": "hybrid_graphrag" if graph_context_count else "vector_rag"},
    }


def _retrieval_report() -> dict:
    modes = {
        "graph_only": _mode_result(
            mode="graph_only",
            graph_context_count=1,
            source_context_count=0,
            f1=1.0,
            path_support=1.0,
        ),
        "hybrid_graphrag": _mode_result(
            mode="hybrid_graphrag",
            graph_context_count=1,
            source_context_count=1,
            f1=1.0,
            path_support=1.0,
        ),
        "routed_graphrag": _mode_result(
            mode="routed_graphrag",
            graph_context_count=1,
            source_context_count=1,
            f1=1.0,
            path_support=1.0,
        ),
        "routed_token_matched_live_tfidf_graphrag": _mode_result(
            mode="routed_token_matched_live_tfidf_graphrag",
            graph_context_count=1,
            source_context_count=1,
            f1=1.0,
            path_support=1.0,
        ),
        "routed_token_matched_dense_graphrag": _mode_result(
            mode="routed_token_matched_dense_graphrag",
            graph_context_count=0,
            source_context_count=1,
            f1=None,
            path_support=None,
            target_hit=False,
        ),
    }
    abstention_modes = {
        name: _mode_result(
            mode=name,
            graph_context_count=0 if name.startswith("routed") else 1,
            source_context_count=1,
            f1=1.0,
            path_support=None if name.startswith("routed") else 0.0,
            expected_abstention=True,
            abstention_correct=name.startswith("routed"),
        )
        for name in modes
    }
    return {
        "status": "s7_retrieval_gate_evaluated",
        "metadata": {
            "graph_source_node_count": 1,
            "graph_fact_node_count": 2,
            "graph_edge_count": 4,
        },
        "records": [
            {
                "cq_id": "QT-Q01-AFFECTED-NAS-ELEMENTS::s1",
                "template_id": "QT-Q01-AFFECTED-NAS-ELEMENTS",
                "source_id": "s1",
                "route": "graph_template",
                "modes": modes,
            },
            {
                "cq_id": "QT-A01-ABSTENTION-FIELDS::s2",
                "template_id": "QT-A01-ABSTENTION-FIELDS",
                "source_id": "s2",
                "route": "vector_template",
                "modes": abstention_modes,
            },
        ],
    }


def test_build_nasa_atmonto_s7_graph_health_aggregates_by_template_and_route(
    tmp_path: Path,
) -> None:
    report_path = tmp_path / "s7_retrieval.json"
    _write_json(report_path, _retrieval_report())

    result = build_nasa_atmonto_s7_graph_health(
        repo_root=tmp_path,
        s7_retrieval_report_path=report_path,
    )

    assert result["status"] == "s7_graph_health_evaluated"
    assert result["metadata"]["retrieval_case_count"] == 2
    assert result["aggregate_by_mode"]["hybrid_graphrag"]["graph_context_case_rate"] == 1.0
    assert result["aggregate_by_mode"]["routed_token_matched_dense_graphrag"][
        "target_source_hit_rate"
    ] == 0.5
    assert result["aggregate_by_template"]["QT-Q01-AFFECTED-NAS-ELEMENTS"]["graph_only"][
        "avg_path_support_rate"
    ] == 1.0
    assert result["aggregate_by_route"]["vector_template"]["routed_graphrag"][
        "abstention_correctness"
    ] == 1.0


def test_write_nasa_atmonto_s7_graph_health_outputs_markdown(tmp_path: Path) -> None:
    report_path = tmp_path / "s7_retrieval.json"
    _write_json(report_path, _retrieval_report())
    output_dir = tmp_path / "reports"

    json_path, md_path, result = write_nasa_atmonto_s7_graph_health(
        output_dir=output_dir,
        repo_root=tmp_path,
        s7_retrieval_report_path=report_path,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["claim_boundary"]
    markdown = md_path.read_text(encoding="utf-8")
    assert "S7 Graph Health by CQ Group" in markdown
    assert "CQ Template Graph Health" in markdown
    assert "Graph-context rate" in markdown
