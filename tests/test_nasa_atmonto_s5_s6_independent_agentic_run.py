from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.atmonto.agentic_loop.independent_run import (
    build_nasa_atmonto_s5_s6_independent_agentic_run,
    write_nasa_atmonto_s5_s6_independent_agentic_run,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(record) for record in records) + "\n",
        encoding="utf-8",
    )


def _write_fixture_files(tmp_path: Path) -> dict[str, Path]:
    input_records_path = tmp_path / "input.jsonl"
    _write_jsonl(
        input_records_path,
        [
            {
                "sample_id": "ATCSCC-GOLD-001",
                "source_id": "2026-05-15:063",
                "source_family": "atcscc_advisories",
                "source_text": (
                    "ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS "
                    "EFFECTIVE TIME: 151918-160030 USERS CAN EXPECT ARRIVAL DELAYS"
                ),
            }
        ],
    )
    s0_path = tmp_path / "s0.jsonl"
    _write_jsonl(
        s0_path,
        [
            {
                "system_id": "S0_rule_only",
                "sample_id": "ATCSCC-GOLD-001",
                "source_id": "2026-05-15:063",
                "source_family": "atcscc_advisories",
                "candidate_facts": [
                    {
                        "fact_id": "f1",
                        "source_id": "2026-05-15:063",
                        "fact_type": "datatype_property",
                        "subject": "urn:test",
                        "subject_class": "TrafficManagementInitiative",
                        "predicate": "advisoryNumber",
                        "datatype": "xsd:integer",
                        "value": 63,
                        "evidence_text": "ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS",
                    },
                    {
                        "fact_id": "f2",
                        "source_id": "2026-05-15:063",
                        "fact_type": "object_property",
                        "subject": "urn:test",
                        "subject_class": "TrafficManagementInitiative",
                        "predicate": "controlledNASelement",
                        "object": "urn:aviation-agentic-ai:nas-element:USERS",
                        "object_label": "USERS",
                        "object_class": "TFMcontrolElement",
                        "evidence_text": "USERS CAN EXPECT ARRIVAL DELAYS",
                    },
                    {
                        "fact_id": "f3",
                        "source_id": "2026-05-15:063",
                        "fact_type": "datatype_property",
                        "subject": "urn:test",
                        "subject_class": "TrafficManagementInitiative",
                        "predicate": "advisoryNumber",
                        "datatype": "xsd:integer",
                        "value": 63,
                        "evidence_text": "ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS",
                    },
                ],
            }
        ],
    )
    gold_path = tmp_path / "gold.jsonl"
    _write_jsonl(
        gold_path,
        [
            {
                "source_id": "2026-05-15:063",
                "gold_annotation": {
                    "valid_facts": [
                        {
                            "fact_type": "datatype_property",
                            "subject_class": "TrafficManagementInitiative",
                            "predicate": "advisoryNumber",
                            "datatype": "xsd:integer",
                            "value": 63,
                            "evidence_text": (
                                "ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS"
                            ),
                            "source_id": "2026-05-15:063",
                        }
                    ],
                    "missing_facts": [],
                },
            }
        ],
    )
    schema_path = tmp_path / "schema.json"
    _write_json(
        schema_path,
        {
            "classes": [
                {
                    "iri": "https://data.nasa.gov/ontologies/atmonto/ATM#TrafficManagementInitiative",
                    "prefixed_name": "atm:TrafficManagementInitiative",
                    "local_name": "TrafficManagementInitiative",
                },
                {
                    "iri": "https://data.nasa.gov/ontologies/atmonto/ATM#TFMcontrolElement",
                    "prefixed_name": "atm:TFMcontrolElement",
                    "local_name": "TFMcontrolElement",
                },
            ],
            "object_properties": [
                {
                    "iri": "https://data.nasa.gov/ontologies/atmonto/ATM#controlledNASelement",
                    "prefixed_name": "atm:controlledNASelement",
                    "local_name": "controlledNASelement",
                    "domain_iri_set": [
                        "https://data.nasa.gov/ontologies/atmonto/ATM#TrafficManagementInitiative"
                    ],
                    "range_iri_set": [
                        "https://data.nasa.gov/ontologies/atmonto/ATM#TFMcontrolElement"
                    ],
                }
            ],
            "datatype_properties": [
                {
                    "iri": "https://data.nasa.gov/ontologies/atmonto/ATM#advisoryNumber",
                    "prefixed_name": "atm:advisoryNumber",
                    "local_name": "advisoryNumber",
                    "domain_iri_set": [
                        "https://data.nasa.gov/ontologies/atmonto/ATM#TrafficManagementInitiative"
                    ],
                    "datatype_iri_set": ["http://www.w3.org/2001/XMLSchema#integer"],
                }
            ],
            "class_hierarchy": [],
            "class_property_constraints": [],
        },
    )
    cq_path = tmp_path / "cq.json"
    _write_json(
        cq_path,
        {
            "cqs": [
                {
                    "cq_id": "CQ-D01",
                    "route_label": "deterministic",
                    "graph_use_decision": "avoid_by_default",
                    "required_predicates": ["advisoryNumber"],
                },
                {
                    "cq_id": "CQ-D02",
                    "route_label": "hybrid",
                    "graph_use_decision": "use_graph",
                    "required_predicates": ["controlledNASelement"],
                },
            ]
        },
    )
    scoring_path = tmp_path / "scoring.json"
    _write_json(
        scoring_path,
        {
            "systems": [
                {
                    "system_id": "S0_rule_only",
                    "semantic_metrics": {
                        "available": True,
                        "predicted_fact_count": 2,
                        "gold_fact_count": 1,
                        "true_positive_count": 1,
                        "false_positive_count": 1,
                        "false_negative_count": 0,
                        "precision": 0.5,
                        "recall": 1.0,
                        "f1": 0.6667,
                    },
                }
            ]
        },
    )
    return {
        "input_records_path": input_records_path,
        "s0_predictions_path": s0_path,
        "schema_slice_path": schema_path,
        "gold_path": gold_path,
        "cq_manifest_path": cq_path,
        "scoring_path": scoring_path,
        "prediction_output_path": tmp_path / "predictions.jsonl",
        "run_metadata_output_path": tmp_path / "metadata.json",
    }


def test_independent_agentic_run_quarantines_text_artifact_and_duplicate(
    tmp_path: Path,
) -> None:
    paths = _write_fixture_files(tmp_path)

    result = build_nasa_atmonto_s5_s6_independent_agentic_run(
        repo_root=tmp_path,
        **paths,
    )

    assert result["status"] == "s5_s6_independent_agentic_run_scored"
    assert result["metadata"]["independent_from_s4"] is True
    assert result["metadata"]["live_llm_run"] is False
    assert result["metadata"]["s5_fact_count"] == 3
    assert result["metadata"]["s6_fact_count"] == 1
    assert result["metadata"]["quarantined_fact_count"] == 2
    assert result["quarantine_summary"]["reason_counts"]["text_artifact_controlled_element"] == 1
    assert result["quarantine_summary"]["reason_counts"]["duplicate_canonical_fact"] == 1
    assert result["metrics"]["s6_critic_refined_semantic_metrics"]["f1"] == 1.0


def test_write_independent_agentic_run_outputs_reports_predictions_and_metadata(
    tmp_path: Path,
) -> None:
    paths = _write_fixture_files(tmp_path)
    output_dir = tmp_path / "reports"

    json_path, md_path, result = write_nasa_atmonto_s5_s6_independent_agentic_run(
        output_dir=output_dir,
        repo_root=tmp_path,
        **paths,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert paths["prediction_output_path"].exists()
    assert paths["run_metadata_output_path"].exists()
    assert result["metadata"]["s6_fact_count"] == 1
    markdown = md_path.read_text(encoding="utf-8")
    assert "NASA ATMONTO S5/S6 Independent Agentic Run" in markdown
    assert "Independent from S4" in markdown
    assert "text_artifact_controlled_element" in markdown
