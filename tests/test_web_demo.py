from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from aviation_agentic_ai.cli import main
from aviation_agentic_ai.reporting.web_demo import build_web_demo_readiness
from aviation_agentic_ai.reporting.web_demo_smoke import build_web_demo_smoke
from aviation_agentic_ai.web.data import (
    build_demo_explanation,
    build_demo_status,
    build_question_detail,
    build_question_kg_graph,
    build_questions,
)


def _mode_result(cq_id: str, mode: str) -> dict:
    return {
        "answer": f"{mode} answer for {cq_id} [chunk-{cq_id}]",
        "fused_chunks": [
            {
                "chunk_id": f"chunk-{cq_id}",
                "page": 1,
                "rank": 1,
                "score": 1.0,
                "source": mode,
                "text": "Lift is supported by pressure and airflow evidence.",
            }
        ],
        "graph_triples": [
            {
                "triple_id": f"triple-{cq_id}",
                "subject": "Lift",
                "subject_class": "AerodynamicForce",
                "predicate": "affectedBy",
                "object": "AngleOfAttack",
                "object_class": "FlightCondition",
                "chunk_id": f"chunk-{cq_id}",
                "page": 1,
                "rank": 1,
                "score": 1,
                "confidence": 0.92,
                "evidence_text": "angle of attack affects lift",
            },
            {
                "triple_id": f"triple-evidence-{cq_id}",
                "subject": "Lift",
                "subject_class": "AerodynamicForce",
                "predicate": "supportedByEvidence",
                "object": "Evidence",
                "object_class": "Evidence",
                "chunk_id": f"chunk-{cq_id}",
                "page": 1,
                "rank": 2,
                "score": 0.8,
                "confidence": 0.88,
                "evidence_text": "Lift is supported by pressure and airflow evidence.",
            }
        ]
        if mode != "vector"
        else [],
        "metrics": {
            "kg_evidence": {
                "evidence_coverage": mode != "vector",
                "key_entity_coverage": mode != "vector",
            },
            "llm_answer": {"citation_completeness": True},
        },
    }


def _hybrid_report(strategy: str, cq_ids: list[str]) -> dict:
    return {
        "metadata": {
            "questions_total": len(cq_ids),
            "chunking_strategy": strategy,
            "collection_name": f"phak_ch4_chunks_{strategy}",
        },
        "aggregate": {
            "hybrid": {
                "retrieval": {"recall_at_5": 1.0},
                "kg_evidence": {"evidence_coverage": 0.9},
            }
        },
        "records": [
            {
                "cq_id": cq_id,
                "question": f"What is question {cq_id}?",
                "source_page": 1,
                "key_entities": ["lift"],
                "results": {
                    mode: _mode_result(cq_id, mode)
                    for mode in ("vector", "graph", "hybrid")
                },
            }
            for cq_id in cq_ids
        ],
    }


def _evidence_eval(cq_ids: list[str]) -> dict:
    mode_eval = {
        "chunk": {"chunk_recall_at_5": True},
        "span": {"span_hit": True},
        "kg_evidence": {"evidence_coverage": True},
        "citation": {"citation_completeness": True},
        "answer_support": "supported",
    }
    return {
        "metadata": {
            "labels_total": len(cq_ids),
            "scoring_policy": "layered_metrics_no_mixed_overall_score",
        },
        "experiments": {
            strategy: {
                "present": True,
                "aggregate": {
                    "hybrid": {
                        "chunk_recall_at_5": 1.0,
                        "span_hit_rate": 1.0,
                        "kg_triple_relevance": 1.0,
                        "answer_support_distribution": {"supported": len(cq_ids)},
                    },
                    "graph": {
                        "chunk_recall_at_5": 1.0,
                        "span_hit_rate": 1.0,
                        "kg_triple_relevance": 1.0,
                        "answer_support_distribution": {"supported": len(cq_ids)},
                    },
                    "vector": {
                        "chunk_recall_at_5": 1.0,
                        "span_hit_rate": 1.0,
                        "kg_triple_relevance": 0.0,
                        "answer_support_distribution": {"partially_supported": len(cq_ids)},
                    },
                },
                "records": [
                    {
                        "cq_id": cq_id,
                        "question": f"What is question {cq_id}?",
                        "gold_level": "span",
                        "source_page": 1,
                        "modes": {
                            mode: mode_eval
                            for mode in ("vector", "graph", "hybrid")
                        },
                    }
                    for cq_id in cq_ids
                ],
            }
            for strategy in ("fixed_window", "structure_aware")
        },
    }


def _write_web_fixture(root: Path) -> list[str]:
    cq_ids = [f"cq-{index:02d}" for index in range(10)]
    (root / "data" / "cqs").mkdir(parents=True)
    (root / "data" / "kg").mkdir(parents=True)
    (root / "data" / "chunks").mkdir(parents=True)
    (root / "reports" / "stages").mkdir(parents=True)
    (root / "data" / "kg" / "06_phak_ch4_0.structure_aware.kg.jsonl").write_text(
        "",
        encoding="utf-8",
    )
    (root / "data" / "chunks" / "06_phak_ch4_0.structure_aware.jsonl").write_text(
        "",
        encoding="utf-8",
    )
    (root / "data" / "cqs" / "06_phak_ch4_0.gold.json").write_text(
        json.dumps(
            {
                "metadata": {"review_required": True},
                "labels": [
                    {
                        "cq_id": cq_id,
                        "source_page": 1,
                        "gold_level": "span",
                        "key_entities": ["lift"],
                        "expected_chunk_ids": [f"chunk-{cq_id}"],
                        "evidence_spans": [
                            {
                                "page": 1,
                                "text": "angle of attack affects lift",
                                "char_start": 0,
                                "char_end": 28,
                            }
                        ],
                    }
                    for cq_id in cq_ids
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "reports" / "stages" / "hybrid_rag_experiment.json").write_text(
        json.dumps(_hybrid_report("fixed_window", cq_ids)) + "\n",
        encoding="utf-8",
    )
    (root / "reports" / "stages" / "hybrid_rag_structure_aware.json").write_text(
        json.dumps(_hybrid_report("structure_aware", cq_ids)) + "\n",
        encoding="utf-8",
    )
    (root / "reports" / "stages" / "evidence_level_evaluation.json").write_text(
        json.dumps(_evidence_eval(cq_ids)) + "\n",
        encoding="utf-8",
    )
    (root / "reports" / "stages" / "graphrag_review.json").write_text(
        json.dumps({"recommendations": ["Use structure-aware chunks."]}) + "\n",
        encoding="utf-8",
    )
    return cq_ids


def test_web_data_loads_questions_and_detail(tmp_path: Path) -> None:
    cq_ids = _write_web_fixture(tmp_path)

    status = build_demo_status(tmp_path)
    questions = build_questions(tmp_path)
    detail = build_question_detail(cq_ids[0], tmp_path)

    assert status["ready"]
    assert status["default_strategy"] == "structure_aware"
    assert len(questions) == 10
    assert detail is not None
    assert detail["experiments"]["structure_aware"]["modes"]["hybrid"]["present"]
    assert detail["experiments"]["structure_aware"]["modes"]["hybrid"]["graph_triples"]


def test_question_kg_graph_builds_question_scoped_nodes_and_edges(tmp_path: Path) -> None:
    cq_ids = _write_web_fixture(tmp_path)

    graph = build_question_kg_graph(cq_ids[0], tmp_path)
    vector_graph = build_question_kg_graph(cq_ids[0], tmp_path, mode="vector")

    assert graph is not None
    assert graph["metadata"]["cq_id"] == cq_ids[0]
    assert graph["metadata"]["experiment"] == "structure_aware"
    assert graph["metadata"]["mode"] == "hybrid"
    assert graph["metadata"]["graph_scope"] == "question_scoped_retrieved_evidence"
    assert graph["metadata"]["node_count"] == 3
    assert graph["metadata"]["edge_count"] == 2
    assert graph["nodes"][0]["id"] == "Lift"
    assert graph["nodes"][0]["degree"] == 2
    assert graph["nodes"][0]["source_pages"] == [1]
    assert graph["edges"][0]["triple_id"] == f"triple-{cq_ids[0]}"
    assert graph["edges"][0]["chunk_id"] == f"chunk-{cq_ids[0]}"
    assert graph["edges"][0]["evidence_text"] == "angle of attack affects lift"
    assert vector_graph is not None
    assert vector_graph["nodes"] == []
    assert vector_graph["edges"] == []


def test_question_kg_graph_rejects_invalid_scope(tmp_path: Path) -> None:
    cq_ids = _write_web_fixture(tmp_path)

    with pytest.raises(ValueError, match="Unsupported experiment"):
        build_question_kg_graph(cq_ids[0], tmp_path, experiment="global")

    with pytest.raises(ValueError, match="Unsupported retrieval mode"):
        build_question_kg_graph(cq_ids[0], tmp_path, mode="rerank")


def test_demo_explanation_payload_describes_pipeline_modes_and_strategy(tmp_path: Path) -> None:
    _write_web_fixture(tmp_path)

    explanation = build_demo_explanation(tmp_path)

    assert explanation["narrative"]["default_path"] == "structure_aware + hybrid"
    assert len(explanation["pipeline_steps"]) == 7
    assert explanation["mode_explanations"]["vector"]["label"] == "Vector"
    assert "KG graph is empty" in explanation["mode_explanations"]["vector"]["tradeoff"]
    assert explanation["mode_explanations"]["hybrid"]["label"] == "Hybrid"
    assert "mixed overall score" in explanation["metric_explanations"]["policy"]
    assert {
        item["label"] for item in explanation["metric_explanations"]["items"]
    } >= {"Chunk Recall@5", "MRR@5", "Citation completeness"}
    assert explanation["strategy_decision"]["recommended"] == "structure_aware"
    assert explanation["strategy_decision"]["baseline"] == "fixed_window"
    assert explanation["demo_script"]


def test_web_demo_readiness_uses_layered_metrics(tmp_path: Path) -> None:
    _write_web_fixture(tmp_path)

    result = build_web_demo_readiness(tmp_path)

    assert result["ready"]
    assert result["selected_default_strategy"] == "structure_aware"
    assert result["consistency_checks"]["layered_scoring_policy"]
    assert result["consistency_checks"]["demo_explanation_ready"]
    assert result["explanation"]["ready"]
    assert result["explanation"]["recommended_strategy"] == "structure_aware"
    assert "overall_score" not in result
    assert "overall_score" not in result["metrics"]


def test_fastapi_web_demo_serves_offline_api(tmp_path: Path) -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from aviation_agentic_ai.web.app import create_app

    cq_ids = _write_web_fixture(tmp_path)
    client = TestClient(create_app(project_root=tmp_path))

    root = client.get("/")
    status = client.get("/api/status")
    explanation = client.get("/api/demo/explanation")
    questions = client.get("/api/questions")
    detail = client.get(f"/api/questions/{cq_ids[0]}")
    graph = client.get(f"/api/questions/{cq_ids[0]}/kg-graph")
    vector_graph = client.get(f"/api/questions/{cq_ids[0]}/kg-graph?mode=vector")
    live = client.post("/api/query", json={"question": "What affects lift?"})
    favicon = client.get("/favicon.ico")

    assert root.status_code == 200
    assert "question-list" in root.text
    assert "sidebar-toggle" in root.text
    assert "pipeline-toggle" in root.text
    assert "mode-toggle" in root.text
    assert "live-query-badge" in root.text
    assert "toolbar-group" in root.text
    assert "Retrieved Chunks" in root.text
    assert "KG Relationship Graph" in root.text
    assert "Demo Narrative" in root.text
    assert root.text.index("Optional Live Query") < root.text.index("Demo Narrative")
    assert "Pipeline Explanation" in root.text
    assert root.text.index("Grounded Answer") < root.text.index("Pipeline Explanation")
    assert "Why This Result" in root.text
    assert "Metric Guide" in root.text
    assert "metric-guide" in root.text
    assert "kg-graph-canvas" in root.text
    assert "vendor/cytoscape.min.js" in root.text
    assert status.status_code == 200
    assert status.json()["advisory_boundary"]
    assert status.json()["live_query_enabled"] is False
    assert status.json()["live_query_readiness"]["enabled"] is False
    assert status.json()["live_query_readiness"]["reason"]
    assert explanation.status_code == 200
    assert explanation.json()["strategy_decision"]["recommended"] == "structure_aware"
    assert explanation.json()["mode_explanations"]["hybrid"]["label"] == "Hybrid"
    assert explanation.json()["metric_explanations"]["items"][0]["meaning"]
    assert questions.status_code == 200
    assert len(questions.json()["questions"]) == 10
    assert detail.status_code == 200
    assert detail.json()["experiments"]["structure_aware"]["modes"]["hybrid"]["present"]
    assert graph.status_code == 200
    assert graph.json()["metadata"]["edge_count"] == 2
    assert graph.json()["nodes"][0]["id"] == "Lift"
    assert vector_graph.status_code == 200
    assert vector_graph.json()["metadata"]["edge_count"] == 0
    assert live.status_code == 503
    assert favicon.status_code == 204


def test_live_query_does_not_call_runner_when_not_ready(tmp_path: Path, monkeypatch) -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from aviation_agentic_ai.web import app as web_app

    _write_web_fixture(tmp_path)

    def fail_runner(*_args, **_kwargs):
        raise AssertionError("run_query should not be called when live query is unavailable")

    monkeypatch.setattr(web_app, "run_query", fail_runner)
    client = TestClient(web_app.create_app(project_root=tmp_path))
    response = client.post("/api/query", json={"question": "What affects lift?", "mode": "hybrid"})

    assert response.status_code == 503
    assert response.json()["detail"]


def test_live_query_abstains_on_operational_boundary_before_runner(
    tmp_path: Path,
    monkeypatch,
) -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from aviation_agentic_ai.web import app as web_app

    _write_web_fixture(tmp_path)

    def ready(*_args, **_kwargs):
        return {"enabled": True, "reason": "ready"}

    def fail_runner(*_args, **_kwargs):
        raise AssertionError("run_query should not be called for operational boundary prompts")

    monkeypatch.setattr(web_app, "build_live_query_readiness", ready)
    monkeypatch.setattr(web_app, "run_query", fail_runner)
    client = TestClient(web_app.create_app(project_root=tmp_path, enable_live_query=True))
    response = client.post(
        "/api/query",
        json={"question": "Should I take off now based on current weather?", "mode": "hybrid"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["sufficiency_decision"]["decision"] == "abstain"
    assert payload["sufficiency_decision"]["risk_category"] != "training_question"
    assert payload["evidence_summary"]["chunk_count"] == 0


def test_live_query_calls_runner_with_selected_mode_and_evidence_summary(
    tmp_path: Path,
    monkeypatch,
) -> None:
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from aviation_agentic_ai.web import app as web_app

    _write_web_fixture(tmp_path)
    calls = {}

    def ready(*_args, **_kwargs):
        return {
            "enabled": True,
            "reason": "Live query is ready.",
            "provider": "vllm",
            "model": "local-test-model",
            "collection_name": "phak_ch4_chunks_structure_aware",
        }

    def fake_runner(question, mode, *_args, **_kwargs):
        calls["question"] = question
        calls["mode"] = mode
        return {
            "question": question,
            "mode": mode,
            "answer": "Grounded live answer. Citations: chunk-live, triple-live.",
            "fused_chunks": [
                {
                    "chunk_id": "chunk-live",
                    "page": 2,
                    "source": "graph+vector",
                    "text": "Live evidence text.",
                }
            ],
            "graph_triples": [
                {
                    "triple_id": "triple-live",
                    "page": 2,
                    "subject": "Lift",
                    "predicate": "affectedBy",
                    "object": "AngleOfAttack",
                }
            ],
        }

    monkeypatch.setattr(web_app, "build_live_query_readiness", ready)
    monkeypatch.setattr(web_app, "run_query", fake_runner)
    client = TestClient(web_app.create_app(project_root=tmp_path, enable_live_query=True))
    response = client.post("/api/query", json={"question": "  What affects lift?  ", "mode": "graph"})

    assert response.status_code == 200
    payload = response.json()
    assert calls == {"question": "What affects lift?", "mode": "graph"}
    assert payload["mode"] == "graph"
    assert payload["answer"].startswith("Grounded live answer")
    assert payload["evidence_summary"]["chunk_count"] == 1
    assert payload["evidence_summary"]["triple_count"] == 1
    assert payload["evidence_summary"]["top_chunk"]["chunk_id"] == "chunk-live"
    assert payload["evidence_summary"]["top_triple"]["triple_id"] == "triple-live"


def test_web_demo_smoke_uses_fastapi_testclient(tmp_path: Path) -> None:
    pytest.importorskip("fastapi")
    _write_web_fixture(tmp_path)

    result = build_web_demo_smoke(tmp_path)

    assert result["ready"]
    assert result["payloads"]["status"]["default_strategy"] == "structure_aware"
    assert result["payloads"]["questions"]["count"] == 10
    assert result["payloads"]["kg_graph"]["hybrid_edges"] == 2
    assert result["payloads"]["kg_graph"]["vector_edges"] == 0
    assert "overall_score" not in result


def test_cli_report_web_demo_readiness_uses_mocked_writer(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(output_dir, *, report_name):
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        json_path = output / f"{report_name}.json"
        md_path = output / f"{report_name}.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# Web Demo Readiness\n", encoding="utf-8")
        return json_path, md_path, {
            "ready": True,
            "selected_default_strategy": "structure_aware",
        }

    monkeypatch.setattr(cli, "write_web_demo_readiness", fake_writer)
    result = CliRunner().invoke(
        main,
        [
            "report",
            "web-demo-readiness",
            "--output-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Web demo readiness: True" in result.output


def test_cli_report_web_demo_smoke_uses_mocked_writer(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli

    def fake_writer(output_dir, *, report_name):
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        json_path = output / f"{report_name}.json"
        md_path = output / f"{report_name}.md"
        json_path.write_text("{}\n", encoding="utf-8")
        md_path.write_text("# Web Demo Final Smoke\n", encoding="utf-8")
        return json_path, md_path, {"ready": True}

    monkeypatch.setattr(cli, "write_web_demo_smoke", fake_writer)
    result = CliRunner().invoke(
        main,
        ["report", "web-demo-smoke", "--output-dir", str(tmp_path)],
    )

    assert result.exit_code == 0, result.output
    assert "Web demo final smoke: True" in result.output


def test_cli_web_serve_uses_mocked_server(monkeypatch) -> None:
    from aviation_agentic_ai import cli

    calls = {}

    def fake_server(**kwargs):
        calls.update(kwargs)

    monkeypatch.setattr(cli, "serve_web_app", fake_server)
    result = CliRunner().invoke(
        main,
        ["web", "serve", "--port", "8123"],
    )

    assert result.exit_code == 0, result.output
    assert calls["port"] == 8123
    assert calls["enable_live_query"] is None

    calls.clear()
    result = CliRunner().invoke(
        main,
        ["web", "serve", "--port", "8123", "--enable-live-query"],
    )

    assert result.exit_code == 0, result.output
    assert calls["port"] == 8123
    assert calls["enable_live_query"] is True

    calls.clear()
    result = CliRunner().invoke(
        main,
        ["web", "serve", "--port", "8123", "--disable-live-query"],
    )

    assert result.exit_code == 0, result.output
    assert calls["port"] == 8123
    assert calls["enable_live_query"] is False
