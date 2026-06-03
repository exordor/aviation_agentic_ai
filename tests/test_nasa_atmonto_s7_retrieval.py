from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_cq_queries import build_cq_query_manifest
from aviation_agentic_ai.reporting.nasa_atmonto_s7_retrieval import (
    RETRIEVAL_MODES,
    build_nasa_atmonto_s7_retrieval,
    write_nasa_atmonto_s7_retrieval,
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


def _fake_dense_encoder(texts: list[str]) -> list[list[float]]:
    return [[1.0 if "2026-05-19:032" in text else 0.0, 1.0] for text in texts]


def _misleading_dense_encoder(texts: list[str]) -> list[list[float]]:
    vectors: list[list[float]] = []
    for text in texts:
        if text.startswith("2026-05-19:032") or "Which" in text or "expected fields" in text:
            vectors.append([1.0, 0.0])
        elif "2026-05-18:021" in text:
            vectors.append([1.0, 0.0])
        else:
            vectors.append([0.0, 1.0])
    return vectors


def _write_fixture(tmp_path: Path) -> dict[str, Path]:
    source_text = (
        "ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD. "
        "MESSAGE: CONSTRAINED FACILITIES: ZNY. ZNY ADVISES THAT ROUTE L452 IS "
        "CLOSED DUE TO WEATHER. EFFECTIVE TIME: 191322-191630."
    )
    gold_path = tmp_path / "gold.jsonl"
    _write_jsonl(
        gold_path,
        [
            {
                "sample_id": "ATCSCC-GOLD-001",
                "source_id": "2026-05-19:032",
                "source_text": source_text,
                "gold_annotation": {
                    "annotation_status": "reviewed",
                    "valid_facts": [
                        {
                            "predicate": "controlledNASelement",
                            "object_label": "ZNY",
                            "source_id": "2026-05-19:032",
                            "evidence_text": "CONSTRAINED FACILITIES: ZNY",
                        },
                        {
                            "predicate": "effectiveStartTime",
                            "value": "2026-05-19T13:22:00Z",
                            "source_id": "2026-05-19:032",
                            "evidence_text": "EFFECTIVE TIME: 191322-191630",
                        },
                        {
                            "predicate": "effectiveEndTime",
                            "value": "2026-05-19T16:30:00Z",
                            "source_id": "2026-05-19:032",
                            "evidence_text": "EFFECTIVE TIME: 191322-191630",
                        },
                        {
                            "predicate": "impactingCondition",
                            "value": "WEATHER",
                            "source_id": "2026-05-19:032",
                            "evidence_text": "CLOSED DUE TO WEATHER",
                        },
                        {
                            "predicate": "implementationStatus",
                            "value": "RQD",
                            "source_id": "2026-05-19:032",
                            "evidence_text": "OCEANIC ROUTE CLOSURES_RQD",
                        },
                        {
                            "predicate": "reRouteType",
                            "value": "ROUTE",
                            "source_id": "2026-05-19:032",
                            "evidence_text": "OCEANIC ROUTE CLOSURES_RQD",
                        },
                    ],
                    "missing_facts": [
                        {
                            "predicate": "extensionProbability",
                            "value": "unsupported",
                            "source_id": "2026-05-19:032",
                            "evidence_text": "",
                        }
                    ],
                },
            }
        ],
    )
    s4_path = tmp_path / "s4.jsonl"
    _write_jsonl(
        s4_path,
        [
            {
                "source_id": "2026-05-19:032",
                "facts": [
                    {
                        "fact_id": "fact-zny",
                        "predicate": "atm:controlledNASelement",
                        "object_label": "ZNY",
                        "source_id": "2026-05-19:032",
                        "evidence_text": "CONSTRAINED FACILITIES: ZNY",
                        "validator_status": "repaired_accepted",
                    },
                    {
                        "fact_id": "fact-artifact",
                        "predicate": "atm:controlledNASelement",
                        "object_label": "ADVZY",
                        "source_id": "2026-05-19:032",
                        "evidence_text": "ATCSCC ADVZY 032",
                        "validator_status": "repaired_accepted",
                    },
                    {
                        "fact_id": "fact-start",
                        "predicate": "atm:effectiveStartTime",
                        "value": "2026-05-19T13:22:00Z",
                        "source_id": "2026-05-19:032",
                        "evidence_text": "EFFECTIVE TIME: 191322-191630",
                        "validator_status": "repaired_accepted",
                    },
                    {
                        "fact_id": "fact-end",
                        "predicate": "atm:effectiveEndTime",
                        "value": "2026-05-19T16:30:00Z",
                        "source_id": "2026-05-19:032",
                        "evidence_text": "EFFECTIVE TIME: 191322-191630",
                        "validator_status": "repaired_accepted",
                    },
                    {
                        "fact_id": "fact-weather",
                        "predicate": "atm:impactingCondition",
                        "value": "WEATHER",
                        "source_id": "2026-05-19:032",
                        "evidence_text": "CLOSED DUE TO WEATHER",
                        "validator_status": "repaired_accepted",
                    },
                    {
                        "fact_id": "fact-status",
                        "predicate": "atm:implementationStatus",
                        "value": "RQD",
                        "source_id": "2026-05-19:032",
                        "evidence_text": "OCEANIC ROUTE CLOSURES_RQD",
                        "validator_status": "repaired_accepted",
                    },
                    {
                        "fact_id": "fact-route",
                        "predicate": "atm:reRouteType",
                        "value": "ROUTE",
                        "source_id": "2026-05-19:032",
                        "evidence_text": "OCEANIC ROUTE CLOSURES_RQD",
                        "validator_status": "repaired_accepted",
                    },
                ],
            }
        ],
    )
    source_path = tmp_path / "input_records.jsonl"
    _write_jsonl(
        source_path,
        [
            {
                "sample_id": "ATCSCC-GOLD-001",
                "source_id": "2026-05-19:032",
                "advisory_date": "2026-05-19",
                "advisory_number": 32,
                "source_text": source_text,
                "source_url": "https://example.test/advisory/032",
            }
        ],
    )
    manifest_path = tmp_path / "templates.json"
    _write_json(manifest_path, build_cq_query_manifest())
    return {"gold": gold_path, "s4": s4_path, "source": source_path, "manifest": manifest_path}


def _append_misleading_source(source_path: Path) -> None:
    with source_path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "sample_id": "ATCSCC-GOLD-OTHER",
                    "source_id": "2026-05-18:021",
                    "advisory_date": "2026-05-18",
                    "advisory_number": 21,
                    "source_text": "ATCSCC Advisory FAA Home Products Site Map metadata only.",
                    "source_url": "https://example.test/advisory/021",
                }
            )
            + "\n"
        )


def test_build_nasa_atmonto_s7_retrieval_reports_modes_and_gate(tmp_path: Path) -> None:
    paths = _write_fixture(tmp_path)

    result = build_nasa_atmonto_s7_retrieval(
        repo_root=tmp_path,
        gold_path=paths["gold"],
        s4_prediction_path=paths["s4"],
        source_record_path=paths["source"],
        query_manifest_path=paths["manifest"],
        max_cases_per_template=1,
        dense_encoder=_fake_dense_encoder,
    )

    assert result["status"] == "s7_retrieval_gate_evaluated"
    assert result["metadata"]["modes"] == list(RETRIEVAL_MODES)
    assert "live_tfidf_vector" in result["metadata"]["modes"]
    assert "dense_embedding_vector" in result["metadata"]["modes"]
    assert result["metadata"]["retrieval_case_count"] == 6
    assert result["metadata"]["live_source_document_count"] == 1
    assert result["metadata"]["dense_source_document_count"] == 1
    assert result["metadata"]["graph_source_node_count"] == 1
    assert result["metadata"]["graph_fact_node_count"] == 6
    assert result["metadata"]["graph_edge_count"] == 12
    assert result["critic_gate"]["rejected_values"] == ["ADVZY"]
    assert result["aggregate_by_mode"]["token_matched_vector_proxy"]["avg_target_context_tokens"]
    assert result["aggregate_by_mode"]["token_matched_live_tfidf_vector"]["avg_target_context_tokens"]
    assert result["aggregate_by_mode"]["token_matched_dense_embedding_vector"]["avg_target_context_tokens"]
    assert result["aggregate_by_mode"]["live_tfidf_vector"]["target_source_hit_rate"] == 1.0
    assert result["aggregate_by_mode"]["dense_embedding_vector"]["target_source_hit_rate"] == 1.0
    assert result["aggregate_by_mode"]["live_tfidf_vector"]["avg_retrieval_latency_ms"] is not None
    assert result["aggregate_by_mode"]["graph_only"]["avg_retrieval_latency_ms"] is not None
    assert result["aggregate_by_mode"]["hybrid_graphrag"]["avg_path_support_rate"] is not None
    assert result["aggregate_by_mode"]["source_oracle"]["abstention_correctness"] == 1.0
    assert result["aggregate_by_mode"]["vector_rag_proxy"]["abstention_correctness"] == 1.0
    assert result["aggregate_by_mode"]["routed_graphrag"]["abstention_correctness"] == 1.0
    assert result["aggregate_by_mode"]["graph_only"]["abstention_correctness"] == 0.0
    route_summary = result["route_summary"]["by_template"]
    assert route_summary["QT-Q01-TIME-WINDOW"]["underlying_mode"] == "vector_rag"
    assert route_summary["QT-Q01-ROUTE-SEMANTICS"]["underlying_mode"] == "hybrid_graphrag"


def test_source_local_dense_guard_injects_target_source_when_dense_misses(
    tmp_path: Path,
) -> None:
    paths = _write_fixture(tmp_path)
    _append_misleading_source(paths["source"])

    result = build_nasa_atmonto_s7_retrieval(
        repo_root=tmp_path,
        gold_path=paths["gold"],
        s4_prediction_path=paths["s4"],
        source_record_path=paths["source"],
        query_manifest_path=paths["manifest"],
        max_cases_per_template=1,
        live_top_k=1,
        dense_encoder=_misleading_dense_encoder,
    )

    time_window = next(
        record for record in result["records"] if record["template_id"] == "QT-Q01-TIME-WINDOW"
    )
    dense_result = time_window["modes"]["dense_embedding_vector"]

    assert dense_result["target_source_retrieved"] is True
    assert dense_result["retrieval_guards"] == ["source_local_target_source_guard"]
    assert result["aggregate_by_mode"]["dense_embedding_vector"]["retrieval_guard_count"] >= 1


def test_write_nasa_atmonto_s7_retrieval_outputs_reports(tmp_path: Path) -> None:
    paths = _write_fixture(tmp_path)
    output_dir = tmp_path / "reports"

    json_path, md_path, result = write_nasa_atmonto_s7_retrieval(
        output_dir=output_dir,
        repo_root=tmp_path,
        gold_path=paths["gold"],
        s4_prediction_path=paths["s4"],
        source_record_path=paths["source"],
        query_manifest_path=paths["manifest"],
        max_cases_per_template=1,
        dense_encoder=_fake_dense_encoder,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert json.loads(json_path.read_text(encoding="utf-8"))["records"]
    markdown = md_path.read_text(encoding="utf-8")
    assert "S7 Retrieval-Only Graph-Use Gate" in markdown
    assert "token_matched_vector_proxy" in markdown
    assert "live_tfidf_vector" in markdown
    assert "dense_embedding_vector" in markdown
    assert "Dense retrieval model" in markdown
    assert "Target hit" in markdown
    assert "Materialized graph" in markdown
    assert "Avg latency ms" in markdown
    assert result["claim_boundary"]
