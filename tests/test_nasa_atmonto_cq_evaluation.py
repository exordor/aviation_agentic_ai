from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_cq import (
    build_nasa_atmonto_cq_evaluation,
    write_nasa_atmonto_cq_evaluation,
)


def _write_fixture_files(tmp_path: Path) -> dict[str, Path]:
    gold_path = tmp_path / "gold.jsonl"
    source_text = (
        "ATCSCC ADVZY 032 OCEANIC ROUTE CLOSURES. "
        "CONSTRAINED FACILITIES: ZNY. EFFECTIVE TIME: 191322-191630."
    )
    gold_record = {
        "sample_id": "ATCSCC-GOLD-001",
        "candidate_subject_class": "ReRouteTMI",
        "source_text": source_text,
        "gold_annotation": {
            "annotation_status": "reviewed",
            "invalid_candidate_fact_ids": ["bad-fact-1"],
            "valid_facts": [
                {
                    "predicate": "advisoryNumber",
                    "value": 32,
                    "evidence_text": "ATCSCC ADVZY 032",
                    "source_id": "2026-05-19:032",
                },
                {
                    "predicate": "controlledNASelement",
                    "value": "ZNY",
                    "evidence_text": "CONSTRAINED FACILITIES: ZNY",
                    "source_id": "2026-05-19:032",
                },
            ],
            "missing_facts": [
                {
                    "predicate": "atm:reRouteType",
                    "value": "ROUTE",
                    "evidence_text": "OCEANIC ROUTE CLOSURES",
                    "source_id": "2026-05-19:032",
                }
            ],
            "rejected_fact_adjudications": [
                {
                    "predicate": "controlledNASelement",
                    "decision": "profile_gap",
                    "evidence_text": "CONSTRAINED FACILITIES: ZNY",
                }
            ],
        },
    }
    gold_path.write_text(json.dumps(gold_record) + "\n", encoding="utf-8")

    scoring_path = tmp_path / "scoring.json"
    scoring_path.write_text(
        json.dumps(
            {
                "status": "formal_experiment_complete",
                "systems": [
                    {
                        "system_id": "S4_hybrid_backbone_enrichment",
                        "label": "Hybrid backbone + semantic enrichment",
                        "available": True,
                        "semantic_metrics": {
                            "precision": 0.75,
                            "recall": 0.6,
                            "f1": 0.6667,
                            "scoring_validity": "valid_target_schema_scoring",
                        },
                        "property_level_semantic_metrics": [
                            {
                                "predicate": "advisoryNumber",
                                "predicted_fact_count": 1,
                                "gold_fact_count": 1,
                                "true_positive_count": 1,
                                "false_positive_count": 0,
                                "false_negative_count": 0,
                            },
                            {
                                "predicate": "controlledNASelement",
                                "predicted_fact_count": 1,
                                "gold_fact_count": 1,
                                "true_positive_count": 1,
                                "false_positive_count": 0,
                                "false_negative_count": 0,
                            },
                            {
                                "predicate": "reRouteType",
                                "predicted_fact_count": 0,
                                "gold_fact_count": 1,
                                "true_positive_count": 0,
                                "false_positive_count": 0,
                                "false_negative_count": 1,
                            },
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    semantic_groups_path = tmp_path / "semantic_groups.json"
    semantic_groups_path.write_text(
        json.dumps(
            {
                "status": "semantic_groups_ready",
                "semantic_group_count": 1,
                "record_count": 1,
                "groups": [{"group_id": "reroute", "label": "Reroute", "record_count": 1}],
            }
        ),
        encoding="utf-8",
    )

    rejection_path = tmp_path / "rejection.json"
    rejection_path.write_text(
        json.dumps(
            {
                "property_level_complete": True,
                "rejected_fact_count": 1,
                "pending_fact_count": 0,
                "decision_counts_by_fact": {"profile_gap": 1},
            }
        ),
        encoding="utf-8",
    )
    return {
        "gold_path": gold_path,
        "scoring_path": scoring_path,
        "semantic_groups_path": semantic_groups_path,
        "rejection_path": rejection_path,
    }


def test_build_nasa_atmonto_cq_evaluation_normalizes_predicates(tmp_path: Path) -> None:
    paths = _write_fixture_files(tmp_path)

    result = build_nasa_atmonto_cq_evaluation(
        repo_root=tmp_path,
        gold_path=paths["gold_path"],
        scoring_path=paths["scoring_path"],
        semantic_groups_path=paths["semantic_groups_path"],
        rejection_adjudication_path=paths["rejection_path"],
    )

    assert result["metadata"]["cq_count"] == 12
    assert result["evaluation_status_counts"] == {
        "directly_measurable_now": 9,
        "partially_measurable_now": 3,
    }
    assert result["gold_summary"]["predicate_counts"]["reRouteType"] == 1
    assert result["gold_summary"]["evidence"]["containment_rate"] == 1.0

    cq_by_id = {item["id"]: item for item in result["cq_evaluations"]}
    assert cq_by_id["CQ-D02"]["gold_coverage"]["gold_fact_count"] == 1
    assert cq_by_id["CQ-D02"]["best_system"]["system_id"] == "S4_hybrid_backbone_enrichment"
    assert cq_by_id["CQ-D01"]["gold_coverage"]["coverage_scope"] == "records"
    assert cq_by_id["CQ-D01"]["best_system"] is None
    assert cq_by_id["CQ-P01"]["gold_coverage"]["coverage_scope"] == "all_gold_facts"
    assert cq_by_id["CQ-P01"]["gold_coverage"]["gold_fact_count"] == 3
    assert cq_by_id["CQ-Q01"]["evaluation_status"] == "partially_measurable_now"


def test_write_nasa_atmonto_cq_evaluation_outputs_reports(tmp_path: Path) -> None:
    paths = _write_fixture_files(tmp_path)
    output_dir = tmp_path / "reports"

    json_path, md_path, result = write_nasa_atmonto_cq_evaluation(
        output_dir=output_dir,
        repo_root=tmp_path,
        gold_path=paths["gold_path"],
        scoring_path=paths["scoring_path"],
        semantic_groups_path=paths["semantic_groups_path"],
        rejection_adjudication_path=paths["rejection_path"],
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["status"] == "cq_evaluation_mapping_ready"
    markdown = md_path.read_text(encoding="utf-8")
    assert "CQ Evaluation Matrix" in markdown
    assert "CQ-D02" in markdown
