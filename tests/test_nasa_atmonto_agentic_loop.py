from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main
from aviation_agentic_ai.reporting.nasa_atmonto_agentic_loop import (
    build_nasa_atmonto_agentic_loop,
    write_nasa_atmonto_agentic_loop,
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

    systems = [
        {
            "system_id": "S1_llm_only",
            "label": "Open LLM",
            "available": True,
            "semantic_metrics": {
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "scoring_validity": "invalid_direct_schema_scoring",
            },
            "structural_metrics": {
                "schema_violation_rate": 1.0,
                "structural_acceptance_rate": 0.0,
            },
            "property_level_semantic_metrics": [],
        },
        {
            "system_id": "S2_llm_schema_slice",
            "label": "Schema-slice LLM",
            "available": True,
            "semantic_metrics": {
                "precision": 0.25,
                "recall": 0.2,
                "f1": 0.2222,
                "scoring_validity": "valid_target_schema_scoring",
            },
            "structural_metrics": {
                "schema_violation_rate": 0.5,
                "structural_acceptance_rate": 0.5,
            },
            "property_level_semantic_metrics": [],
        },
        {
            "system_id": "S3_llm_schema_slice_validator_repair",
            "label": "Validator repair",
            "available": True,
            "semantic_metrics": {
                "precision": 0.24,
                "recall": 0.18,
                "f1": 0.2057,
                "scoring_validity": "valid_target_schema_scoring",
            },
            "structural_metrics": {
                "schema_violation_rate": 0.2,
                "structural_acceptance_rate": 0.8,
                "repair_success_rate": 0.8,
            },
            "property_level_semantic_metrics": [],
        },
        {
            "system_id": "S4_hybrid_backbone_enrichment",
            "label": "Hybrid backbone",
            "available": True,
            "semantic_metrics": {
                "precision": 0.8,
                "recall": 0.7,
                "f1": 0.7467,
                "scoring_validity": "valid_target_schema_scoring",
            },
            "structural_metrics": {
                "schema_violation_rate": 0.0,
                "structural_acceptance_rate": 1.0,
                "repair_success_rate": 1.0,
            },
            "property_level_semantic_metrics": [
                {
                    "predicate": "controlledNASelement",
                    "predicted_fact_count": 1,
                    "gold_fact_count": 1,
                    "true_positive_count": 1,
                    "false_positive_count": 0,
                    "false_negative_count": 0,
                }
            ],
        },
    ]
    scoring_path = tmp_path / "scoring.json"
    scoring_path.write_text(
        json.dumps({"status": "formal_experiment_complete", "systems": systems}),
        encoding="utf-8",
    )

    prediction_validation_path = tmp_path / "prediction_validation.json"
    prediction_validation_path.write_text(
        json.dumps(
            {
                "status": "ready_for_scoring",
                "selected_source_id_count": 1,
                "error_count": 0,
                "pending_count": 0,
                "systems": [
                    {
                        "system_id": system["system_id"],
                        "status": "ready_for_scoring",
                        "json_metrics": {"json_adherence": 1.0},
                    }
                    for system in systems
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

    cq_manifest_path = tmp_path / "cq_manifest.json"
    cq_manifest_path.write_text(
        json.dumps(
            {
                "status": "ready",
                "cqs": [
                    {
                        "cq_id": "CQ-D01",
                        "role": "domain_typing",
                        "route_label": "deterministic",
                        "difficulty_label": "direct_fact",
                        "graph_use_decision": "avoid_by_default",
                        "required_predicates": ["rdf:type", "advisoryNumber"],
                        "primary_metrics": ["primary_type_accuracy"],
                        "failure_modes": ["generic_tmi_overuse"],
                    },
                    {
                        "cq_id": "CQ-D02",
                        "role": "entity_role",
                        "route_label": "hybrid",
                        "difficulty_label": "entity_resolution",
                        "graph_use_decision": "use_for_answer_set",
                        "required_predicates": ["controlledNASelement"],
                        "primary_metrics": ["role_aware_entity_f1"],
                        "failure_modes": ["unresolved_element"],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    extraction_schema_path = tmp_path / "schema.json"
    extraction_schema_path.write_text(
        json.dumps(
            {
                "title": "ATCSCC extraction schema",
                "type": "object",
                "required": ["source_id", "facts"],
                "properties": {
                    "facts": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["fact_id", "predicate", "evidence_text"],
                            "properties": {
                                "fact_id": {"type": "string"},
                                "predicate": {"type": "string"},
                                "evidence_text": {"type": "string"},
                            },
                        },
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    return {
        "gold_path": gold_path,
        "scoring_path": scoring_path,
        "semantic_groups_path": semantic_groups_path,
        "rejection_path": rejection_path,
        "cq_manifest_path": cq_manifest_path,
        "prediction_validation_path": prediction_validation_path,
        "extraction_schema_path": extraction_schema_path,
    }


def test_build_nasa_atmonto_agentic_loop_routes_abnormal_results_to_code_review(
    tmp_path: Path,
) -> None:
    paths = _write_fixture_files(tmp_path)

    result = build_nasa_atmonto_agentic_loop(
        repo_root=tmp_path,
        gold_path=paths["gold_path"],
        scoring_path=paths["scoring_path"],
        semantic_groups_path=paths["semantic_groups_path"],
        rejection_adjudication_path=paths["rejection_path"],
        cq_manifest_path=paths["cq_manifest_path"],
        prediction_validation_path=paths["prediction_validation_path"],
        extraction_schema_path=paths["extraction_schema_path"],
    )

    assert result["status"] == "agentic_loop_ready_with_code_review_triggers"
    diagnostics = {item["system_id"]: item for item in result["system_loop_diagnostics"]}
    assert diagnostics["S1_llm_only"]["recommended_action"] == "quarantine_before_rerun"
    assert diagnostics["S3_llm_schema_slice_validator_repair"][
        "recommended_action"
    ] == "review_code_before_rerun"
    assert "repair_did_not_improve_semantic_f1" in diagnostics[
        "S3_llm_schema_slice_validator_repair"
    ]["anomaly_flags"]
    assert result["code_review_triggers"]
    assert result["srd_seed"]["competency_question_count"] == 2
    assert result["tip_seed"]["accepted_baselines"] == ["S4_hybrid_backbone_enrichment"]
    artifact_names = {artifact["artifact"] for artifact in result["agentic_artifacts"]}
    assert {
        "SourceBrief",
        "SRD",
        "TIP",
        "ExtractionValidationPlan",
        "ExtractionPlan",
        "ValidationFindings",
        "EvidenceSupportFindings",
        "RepairPlan",
        "CQManifest",
        "PredictionValidation",
    } <= artifact_names


def test_write_nasa_atmonto_agentic_loop_outputs_supporting_artifacts(tmp_path: Path) -> None:
    paths = _write_fixture_files(tmp_path)
    output_dir = tmp_path / "reports"

    json_path, md_path, result = write_nasa_atmonto_agentic_loop(
        output_dir=output_dir,
        repo_root=tmp_path,
        gold_path=paths["gold_path"],
        scoring_path=paths["scoring_path"],
        semantic_groups_path=paths["semantic_groups_path"],
        rejection_adjudication_path=paths["rejection_path"],
        cq_manifest_path=paths["cq_manifest_path"],
        prediction_validation_path=paths["prediction_validation_path"],
        extraction_schema_path=paths["extraction_schema_path"],
    )

    assert json_path.exists()
    assert md_path.exists()
    assert result["status"] == "agentic_loop_ready_with_code_review_triggers"
    assert (output_dir / "atcscc_source_brief.md").exists()
    assert (output_dir / "atcscc_semantic_requirements.md").exists()
    assert (output_dir / "atcscc_technical_implementation_plan.md").exists()
    assert (output_dir / "atcscc_extraction_validation_plan.md").exists()
    assert (output_dir / "atcscc_extraction_plan.md").exists()
    assert (output_dir / "atcscc_validation_findings.md").exists()
    assert (output_dir / "atcscc_evidence_support_findings.md").exists()
    assert (output_dir / "atcscc_repair_plan.md").exists()
    markdown = md_path.read_text(encoding="utf-8")
    assert "Multi-Paper Method Transfer" in markdown
    assert "Agentic Loop Diagnostics" in markdown
    assert "SourceBrief" in markdown
    assert "RepairPlan" in markdown
    assert "repair_did_not_improve_semantic_f1" in markdown


def test_cli_nasa_atmonto_agentic_loop_uses_mocked_writer(tmp_path: Path, monkeypatch) -> None:
    from aviation_agentic_ai import cli_report_nasa

    calls: dict[str, object] = {}

    def fake_writer(**kwargs):
        calls.update(kwargs)
        output_dir = Path(kwargs["output_dir"])
        report_name = str(kwargs["report_name"])
        json_path = output_dir / f"{report_name}.json"
        md_path = output_dir / f"{report_name}.md"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text("{}", encoding="utf-8")
        md_path.write_text("# report\n", encoding="utf-8")
        return (
            json_path,
            md_path,
            {
                "status": "agentic_loop_ready_with_code_review_triggers",
                "code_review_triggers": [{"system_id": "S3"}],
            },
        )

    monkeypatch.setattr(cli_report_nasa, "write_nasa_atmonto_agentic_loop", fake_writer)
    result = CliRunner().invoke(
        main,
        [
            "report",
            "nasa-atmonto-agentic-loop",
            "--output-dir",
            str(tmp_path / "stage"),
            "--report-name",
            "agentic",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Agentic loop status: agentic_loop_ready_with_code_review_triggers" in result.output
    assert "1 code-review trigger" in result.output
    assert calls["report_name"] == "agentic"
