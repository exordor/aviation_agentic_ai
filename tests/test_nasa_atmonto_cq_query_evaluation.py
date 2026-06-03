from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_cq_queries import (
    build_nasa_atmonto_cq_query_evaluation,
    write_nasa_atmonto_cq_query_evaluation,
)


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


def _write_fixture(tmp_path: Path) -> dict[str, Path]:
    gold_path = tmp_path / "gold.jsonl"
    _write_jsonl(
        gold_path,
        [
            {
                "sample_id": "ATCSCC-GOLD-001",
                "source_id": "2026-05-19:032",
                "source_text": "ADVZY 032. CONSTRAINED FACILITIES: ZNY. EFFECTIVE TIME: 191322-191630.",
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
                    ],
                    "missing_facts": [
                        {
                            "predicate": "reRouteReason",
                            "value": "WEATHER",
                            "source_id": "2026-05-19:032",
                            "evidence_text": "CONSTRAINED FACILITIES: ZNY",
                        }
                    ],
                },
            }
        ],
    )
    prediction_path = tmp_path / "s4.jsonl"
    _write_jsonl(
        prediction_path,
        [
            {
                "source_id": "2026-05-19:032",
                "facts": [
                    {
                        "predicate": "https://data.nasa.gov/ontologies/atmonto/ATM#controlledNASelement",
                        "object_label": "ZNY",
                        "source_id": "2026-05-19:032",
                        "evidence_text": "CONSTRAINED FACILITIES: ZNY",
                        "validator_status": "repaired_accepted",
                    },
                    {
                        "predicate": "atm:controlledNASelement",
                        "object_label": "BAD",
                        "source_id": "2026-05-19:032",
                        "evidence_text": "CONSTRAINED FACILITIES: ZNY",
                        "validator_status": "repaired_accepted",
                    },
                    {
                        "predicate": "atm:effectiveStartTime",
                        "value": "2026-05-19T13:22:00Z",
                        "source_id": "2026-05-19:032",
                        "evidence_text": "EFFECTIVE TIME: 191322-191630",
                        "validator_status": "repaired_accepted",
                    },
                ],
            }
        ],
    )
    candidate_path = tmp_path / "s0.jsonl"
    _write_jsonl(
        candidate_path,
        [
            {
                "source_id": "2026-05-19:032",
                "candidate_facts": [
                    {
                        "predicate": "controlledNASelement",
                        "object_label": "ZNY",
                        "source_id": "2026-05-19:032",
                        "evidence_text": "CONSTRAINED FACILITIES: ZNY",
                    }
                ],
            }
        ],
    )
    return {"gold": gold_path, "s4": prediction_path, "s0": candidate_path}


def test_build_nasa_atmonto_cq_query_evaluation_scores_answer_sets(tmp_path: Path) -> None:
    paths = _write_fixture(tmp_path)

    result = build_nasa_atmonto_cq_query_evaluation(
        repo_root=tmp_path,
        gold_path=paths["gold"],
        system_prediction_paths={
            "S0_rule_only": paths["s0"],
            "S4_hybrid_backbone_enrichment": paths["s4"],
        },
    )

    assert result["status"] == "cq_query_answer_quality_ready"
    assert result["metadata"]["template_count"] == 6
    assert result["metadata"]["aggregation_policy"] == "template_weighted_predicate_answers"
    assert result["graphrag_answer_quality"]["llm_generation_status"] == "not_run"

    by_template = {item["template_id"]: item for item in result["template_results"]}
    affected = next(
        item
        for item in by_template["QT-Q01-AFFECTED-NAS-ELEMENTS"]["system_results"]
        if item["system_id"] == "S4_hybrid_backbone_enrichment"
    )
    assert affected["metrics"]["gold_answer_count"] == 1
    assert affected["metrics"]["predicted_answer_count"] == 2
    assert affected["metrics"]["precision"] == 0.5
    assert affected["metrics"]["recall"] == 1.0

    aggregate = result["aggregate_by_system"]["S4_hybrid_backbone_enrichment"]
    assert aggregate["true_positive_count"] == 4
    assert aggregate["false_positive_count"] == 3
    assert aggregate["micro_f1"] is not None
    assert result["aggregate_by_system"]["S0_rule_only"]["true_positive_count"] == 3
    gate = result["graph_use_gate_proxy"]
    assert gate["status"] == "deterministic_queryability_proxy"
    assert gate["aggregate"]["micro_f1"] is not None
    selected = {item["template_id"]: item["selected_system"] for item in gate["selected_templates"]}
    assert selected["QT-Q01-TIME-WINDOW"] == "S0_rule_only"
    assert selected["QT-Q01-AFFECTED-NAS-ELEMENTS"] == "S4_hybrid_backbone_enrichment"


def test_write_nasa_atmonto_cq_query_evaluation_outputs_reports(tmp_path: Path) -> None:
    paths = _write_fixture(tmp_path)
    output_dir = tmp_path / "reports"
    manifest_path = tmp_path / "manifest.json"

    json_path, md_path, manifest_json, manifest_md, result = write_nasa_atmonto_cq_query_evaluation(
        output_dir=output_dir,
        manifest_path=manifest_path,
        repo_root=tmp_path,
        gold_path=paths["gold"],
        system_prediction_paths={"S4_hybrid_backbone_enrichment": paths["s4"]},
    )

    assert json_path.exists()
    assert md_path.exists()
    assert manifest_json.exists()
    assert manifest_md.exists()
    assert result["query_manifest"]["status"] == "query_templates_ready"
    markdown = md_path.read_text(encoding="utf-8")
    assert "CQ Query and Answer-Quality" in markdown
    assert "S7 Graph-Use Gate Proxy" in markdown
    assert "ATCSCC CQ Query Manifest" in manifest_md.read_text(encoding="utf-8")
