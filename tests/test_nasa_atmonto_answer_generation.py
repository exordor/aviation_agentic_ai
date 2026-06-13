from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.atmonto.core.answer_generation import (
    ANSWER_MODES,
    build_nasa_atmonto_answer_generation,
    write_nasa_atmonto_answer_generation,
)
from aviation_agentic_ai.reporting.atmonto.core.answer_benchmark import answer_value
from aviation_agentic_ai.reporting.atmonto.core.cq_queries import build_cq_query_manifest
from aviation_agentic_ai.reporting.atmonto.core.answer_scoring import evaluate_result


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


def _write_fixture(tmp_path: Path) -> dict[str, Path]:
    source_text = (
        "ATCSCC ADVZY 032 DCC 05/19/2026 OCEANIC ROUTE CLOSURES_RQD. "
        "MESSAGE: CONSTRAINED FACILITIES: ZNY. ZNY ADVISES THAT ROUTE L452 IS "
        "CLOSED DUE TO WEATHER. EFFECTIVE TIME: 191322-191630. "
        "CUSTOMERS ARE ENCOURAGED TO FILE ALTERNATE ROUTES."
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
                    "notes": "Rejected parser artifacts include ADVZY, THAT, and ADDS.",
                },
            }
        ],
    )
    s4_path = tmp_path / "s4.jsonl"
    _write_jsonl(
        s4_path,
        [
            {
                "sample_id": "ATCSCC-GOLD-001",
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
                        "fact_id": "fact-unsupported-extra",
                        "predicate": "atm:controlledNASelement",
                        "object_label": "Airport",
                        "source_id": "2026-05-19:032",
                        "evidence_text": "ROUTE L452 IS CLOSED",
                        "validator_status": "repaired_accepted",
                    },
                    {
                        "fact_id": "fact-metadata-extra",
                        "predicate": "atm:controlledNASelement",
                        "object_label": '{"@type": "nas:Airport"}',
                        "source_id": "2026-05-19:032",
                        "evidence_text": "CTL ELEMENT: ZNY ELEMENT TYPE: APT",
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
    manifest_path = tmp_path / "templates.json"
    _write_json(manifest_path, build_cq_query_manifest())
    return {"gold": gold_path, "s4": s4_path, "manifest": manifest_path}


def test_answer_value_preserves_iso_datetimes() -> None:
    assert answer_value({"value": "2026-05-19T13:22:00Z"}) == "2026-05-19T13:22:00Z"
    assert answer_value({"object": "urn:aviation-agentic-ai:nas-element:BNA"}) == "BNA"
    assert answer_value({"predicate": "atm:effectiveStartTime", "value": "13:22"}) == "13:22"


def test_evaluate_result_accepts_structured_abstain_flag() -> None:
    metrics = evaluate_result(
        {"expected_abstention": True, "expected_values": []},
        {"answer": "", "answer_values": [], "abstain": True},
    )

    assert metrics["answer_correctness"] is True
    assert metrics["abstention_correctness"] is True
    assert metrics["actual_abstention"] is True


def test_build_nasa_atmonto_answer_generation_materializes_benchmark_modes_and_metrics(
    tmp_path: Path,
) -> None:
    paths = _write_fixture(tmp_path)

    result = build_nasa_atmonto_answer_generation(
        repo_root=tmp_path,
        gold_path=paths["gold"],
        s4_prediction_path=paths["s4"],
        query_manifest_path=paths["manifest"],
        max_cases_per_template=1,
    )

    assert result["status"] == "answer_generation_evaluated"
    assert result["metadata"]["modes"] == list(ANSWER_MODES)
    assert result["metadata"]["template_count"] == 6
    assert result["metadata"]["benchmark_label_count"] == 6

    label = result["benchmark"]["labels"][0]
    assert label["expected_values"]
    assert label["answer_set"]
    assert label["expected_evidence"]
    assert label["evidence_spans"][0]["text"] in label["source_text"]

    by_template = {record["template_id"]: record for record in result["records"]}
    affected = by_template["QT-Q01-AFFECTED-NAS-ELEMENTS"]
    assert set(affected["results"]) == set(ANSWER_MODES)
    assert "ZNY" in affected["results"]["graph_only"]["answer"]
    assert "ADVZY" not in affected["results"]["graph_only"]["answer"]
    assert "ADVZY" not in affected["results"]["hybrid_graphrag"]["answer"]
    assert "ADVZY" not in affected["results"]["routed_graphrag"]["answer"]
    assert affected["results"]["routed_graphrag"]["underlying_mode"] == "hybrid_graphrag"
    assert (
        affected["results"]["token_matched_vector_rag"]["context_budget"][
            "token_match_target_mode"
        ]
        == "hybrid_graphrag"
    )
    assert "Airport" not in affected["results"]["graph_only"]["answer"]
    assert "@type" not in affected["results"]["graph_only"]["answer"]
    assert affected["metrics"]["graph_only"]["unsupported_claim_rate"] == 0
    assert affected["metrics"]["graph_only"]["answer_correctness"] is True

    critic = result["critic_gate"]
    assert critic["rejected_fact_count"] == 3
    assert critic["rejected_values"] == ["ADVZY", "Airport", '{"@type": "nas:Airport"}']

    aggregate = result["answer_quality"]["aggregate_by_mode"]
    for mode in ANSWER_MODES:
        metrics = aggregate[mode]
        assert metrics["answers_total"] == 6
        for key in (
            "answer_correctness",
            "citation_precision",
            "citation_recall",
            "evidence_faithfulness",
            "unsupported_claim_rate",
            "abstention_correctness",
            "avg_estimated_context_tokens",
            "max_estimated_context_tokens",
        ):
            assert key in metrics
    gate = result["answer_quality"]["secondary_metrics"]["graph_use_gate"]
    assert gate["status"] == "deterministic_proxy_gate"
    assert gate["decision_counts"]["hybrid_graphrag"] >= 1
    assert result["answer_quality"]["secondary_metrics"]["cost_latency"]["provider"] == "none"
    assert result["answer_quality"]["secondary_metrics"]["cost_latency"]["elapsed_seconds"] == 0.0


def test_write_nasa_atmonto_answer_generation_outputs_reports_and_chapter(
    tmp_path: Path,
) -> None:
    paths = _write_fixture(tmp_path)
    output_dir = tmp_path / "reports"
    benchmark_path = tmp_path / "benchmark.json"
    chapter_path = tmp_path / "chapter.md"

    json_path, md_path, benchmark_json, chapter_md, result = write_nasa_atmonto_answer_generation(
        output_dir=output_dir,
        benchmark_path=benchmark_path,
        chapter_path=chapter_path,
        repo_root=tmp_path,
        gold_path=paths["gold"],
        s4_prediction_path=paths["s4"],
        query_manifest_path=paths["manifest"],
        max_cases_per_template=1,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert benchmark_json.exists()
    assert chapter_md.exists()
    assert json.loads(benchmark_json.read_text(encoding="utf-8"))["labels"]
    markdown = md_path.read_text(encoding="utf-8")
    assert "GraphRAG Answer Generation" in markdown
    assert "S7 Graph-Use Gate" in markdown
    chapter = chapter_md.read_text(encoding="utf-8")
    assert "Schema-constrained Agentic KG-RAG" in chapter
    assert "RQ1: Can schema-constrained LLM extraction" in chapter
    assert "Experiment A: Schema-constrained advisory event extraction" in chapter
    assert "Experiment B: Agentic validation and CQ queryability" in chapter
    assert "Experiment C: KG-RAG grounding and answer generation" in chapter
    assert "Experiment D: Failure analysis and human-review boundary" in chapter
    assert result["experiment_chapter_draft"]["claim_boundary"]


def test_write_nasa_atmonto_answer_generation_default_chapter_is_scoped(
    tmp_path: Path,
) -> None:
    paths = _write_fixture(tmp_path)

    _json_path, _md_path, _benchmark_json, chapter_md, _result = write_nasa_atmonto_answer_generation(
        output_dir=tmp_path / "reports",
        repo_root=tmp_path,
        gold_path=paths["gold"],
        s4_prediction_path=paths["s4"],
        query_manifest_path=paths["manifest"],
        max_cases_per_template=1,
    )

    assert chapter_md == tmp_path / "reports/stages/nasa_atmonto_answer_generation_chapter_section.md"
    assert chapter_md.exists()
    assert not (tmp_path / "reports/stages/nasa_atmonto_experiment_chapter_draft.md").exists()
