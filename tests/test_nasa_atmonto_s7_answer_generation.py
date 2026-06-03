from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_cq_queries import build_cq_query_manifest
from aviation_agentic_ai.reporting.nasa_atmonto_s7_answer_generation import (
    S7_ANSWER_MODES,
    build_nasa_atmonto_s7_answer_generation,
    write_nasa_atmonto_s7_answer_generation,
)


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


def _fake_dense_encoder(texts: list[str]) -> list[list[float]]:
    return [[1.0 if "2026-05-19:032" in text else 0.0, 1.0] for text in texts]


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


def test_build_nasa_atmonto_s7_answer_generation_uses_live_retrieval_contexts(
    tmp_path: Path,
) -> None:
    paths = _write_fixture(tmp_path)

    result = build_nasa_atmonto_s7_answer_generation(
        repo_root=tmp_path,
        gold_path=paths["gold"],
        s4_prediction_path=paths["s4"],
        source_record_path=paths["source"],
        query_manifest_path=paths["manifest"],
        max_cases_per_template=1,
        dense_encoder=_fake_dense_encoder,
    )

    assert result["status"] == "s7_answer_generation_evaluated"
    assert result["metadata"]["modes"] == list(S7_ANSWER_MODES)
    assert result["metadata"]["benchmark_label_count"] == 6
    assert result["metadata"]["live_source_document_count"] == 1
    assert result["metadata"]["dense_source_document_count"] == 1
    assert result["critic_gate"]["rejected_values"] == ["ADVZY"]

    aggregate = result["answer_quality"]["aggregate_by_mode"]
    assert aggregate["routed_token_matched_live_tfidf_graphrag"]["answers_total"] == 6
    assert aggregate["routed_token_matched_dense_graphrag"]["avg_target_context_tokens"]
    assert aggregate["token_matched_live_tfidf_vector"]["avg_estimated_context_tokens"]
    assert aggregate["token_matched_dense_embedding_vector"]["avg_estimated_context_tokens"]

    by_template = result["answer_quality"]["aggregate_by_template"]
    assert "QT-Q01-AFFECTED-NAS-ELEMENTS" in by_template
    affected = next(
        record
        for record in result["records"]
        if record["template_id"] == "QT-Q01-AFFECTED-NAS-ELEMENTS"
    )
    routed_live = affected["results"]["routed_token_matched_live_tfidf_graphrag"]
    assert routed_live["underlying_mode"] == "hybrid_graphrag"
    assert routed_live["graph_triples"]
    assert "ADVZY" not in routed_live["answer"]

    time_window = next(
        record for record in result["records"] if record["template_id"] == "QT-Q01-TIME-WINDOW"
    )
    routed_time = time_window["results"]["routed_token_matched_live_tfidf_graphrag"]
    assert routed_time["underlying_mode"] == "live_tfidf_vector"
    assert routed_time["fused_chunks"]
    assert routed_time["context_budget"]["target_estimated_context_tokens"] is not None


def test_write_nasa_atmonto_s7_answer_generation_outputs_reports(tmp_path: Path) -> None:
    paths = _write_fixture(tmp_path)
    output_dir = tmp_path / "reports"

    json_path, md_path, result = write_nasa_atmonto_s7_answer_generation(
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
    assert "S7 Live-Retrieval Answer Generation" in markdown
    assert "routed_token_matched_live_tfidf_graphrag" in markdown
    assert "routed_token_matched_dense_graphrag" in markdown
    assert "CQ Template Breakdown" in markdown
    assert result["claim_boundary"]
