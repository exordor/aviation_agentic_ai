from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from aviation_agentic_ai.cli import main
from aviation_agentic_ai.reporting.atmonto.agentic_loop.l1_batch_experiment import (
    build_nasa_atmonto_l1_agent_batch_experiment,
    write_nasa_atmonto_l1_agent_batch_experiment,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def _schema_slice() -> dict:
    return {
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
                "datatype_set": ["xsd:integer"],
                "datatype_iri_set": ["http://www.w3.org/2001/XMLSchema#integer"],
            },
            {
                "iri": "https://data.nasa.gov/ontologies/atmonto/ATM#impactingCondition",
                "prefixed_name": "atm:impactingCondition",
                "local_name": "impactingCondition",
                "domain_iri_set": [
                    "https://data.nasa.gov/ontologies/atmonto/ATM#TrafficManagementInitiative"
                ],
                "datatype_set": ["xsd:string"],
                "datatype_iri_set": ["http://www.w3.org/2001/XMLSchema#string"],
            },
        ],
        "class_hierarchy": [],
        "class_property_constraints": [],
    }


def _number_fact(fact_id: str = "base-number") -> dict:
    return {
        "fact_id": fact_id,
        "fact_type": "datatype_property",
        "source_id": "2026-05-15:063",
        "subject": "urn:test:tmi:063",
        "subject_class": "TrafficManagementInitiative",
        "predicate": "advisoryNumber",
        "datatype": "xsd:integer",
        "value": 63,
        "evidence_text": "ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS",
    }


def _bad_schema_fact() -> dict:
    return {
        "fact_id": "base-bad-schema",
        "fact_type": "datatype_property",
        "source_id": "2026-05-15:063",
        "subject": "urn:test:tmi:063",
        "subject_class": "TrafficManagementInitiative",
        "predicate": "unmappedOperationalClaim",
        "datatype": "xsd:string",
        "value": "requires unsupported schema extension",
        "evidence_text": "ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS",
    }


def _unsupported_text_artifact_fact() -> dict:
    return {
        "fact_id": "base-users-artifact",
        "fact_type": "object_property",
        "source_id": "2026-05-15:063",
        "subject": "urn:test:tmi:063",
        "subject_class": "TrafficManagementInitiative",
        "predicate": "controlledNASelement",
        "object": "urn:aviation-agentic-ai:nas-element:USERS",
        "object_label": "USERS",
        "object_class": "TFMcontrolElement",
        "evidence_text": "USERS CAN EXPECT ARRIVAL DELAYS",
    }


def _good_repair_facts() -> list[dict]:
    return [
        _number_fact("repair-number"),
        {
            "fact_id": "repair-zla",
            "fact_type": "object_property",
            "source_id": "2026-05-15:063",
            "subject": "urn:test:tmi:063",
            "subject_class": "TrafficManagementInitiative",
            "predicate": "controlledNASelement",
            "object": "urn:aviation-agentic-ai:nas-element:ZLA",
            "object_label": "ZLA",
            "object_class": "TFMcontrolElement",
            "evidence_text": "CONSTRAINED FACILITIES: ZLA",
        },
        {
            "fact_id": "repair-condition",
            "fact_type": "datatype_property",
            "source_id": "2026-05-15:063",
            "subject": "urn:test:tmi:063",
            "subject_class": "TrafficManagementInitiative",
            "predicate": "impactingCondition",
            "datatype": "xsd:string",
            "value": "COMPACTED DEMAND",
            "evidence_text": "DUE TO COMPACTED DEMAND",
        },
    ]


def _write_fixture_files(tmp_path: Path) -> dict[str, Path]:
    input_records_path = tmp_path / "input.jsonl"
    _write_jsonl(
        input_records_path,
        [
            {
                "sample_id": "ATCSCC-GOLD-002",
                "source_id": "2026-05-15:063",
                "source_family": "atcscc_advisories",
                "candidate_subject_class": "TrafficManagementInitiative",
                "source_text": (
                    "ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS "
                    "MESSAGE: CONSTRAINED FACILITIES: ZLA USERS CAN EXPECT ARRIVAL DELAYS "
                    "DUE TO COMPACTED DEMAND"
                ),
            }
        ],
    )
    baseline_predictions_path = tmp_path / "baseline.jsonl"
    _write_jsonl(
        baseline_predictions_path,
        [
            {
                "system_id": "baseline_fixture",
                "sample_id": "ATCSCC-GOLD-002",
                "source_id": "2026-05-15:063",
                "source_family": "atcscc_advisories",
                "facts": [_number_fact(), _bad_schema_fact(), _unsupported_text_artifact_fact()],
            }
        ],
    )
    repair_predictions_path = tmp_path / "repair.jsonl"
    _write_jsonl(
        repair_predictions_path,
        [
            {
                "system_id": "repair_fixture",
                "sample_id": "ATCSCC-GOLD-002",
                "source_id": "2026-05-15:063",
                "source_family": "atcscc_advisories",
                "facts": _good_repair_facts(),
            }
        ],
    )
    schema_slice_path = tmp_path / "schema.json"
    _write_json(schema_slice_path, _schema_slice())
    cq_manifest_path = tmp_path / "cq.json"
    _write_json(
        cq_manifest_path,
        {
            "cqs": [
                {
                    "cq_id": "CQ-D01",
                    "route_label": "deterministic",
                    "graph_use_decision": "avoid_by_default",
                    "required_predicates": ["advisoryNumber"],
                },
                {
                    "cq_id": "CQ-G01",
                    "route_label": "graph",
                    "graph_use_decision": "use_for_answer_set",
                    "required_predicates": ["controlledNASelement", "impactingCondition"],
                },
            ]
        },
    )
    return {
        "input_records_path": input_records_path,
        "baseline_predictions_path": baseline_predictions_path,
        "repair_predictions_path": repair_predictions_path,
        "schema_slice_path": schema_slice_path,
        "cq_manifest_path": cq_manifest_path,
        "prediction_output_path": tmp_path / "l1_predictions.jsonl",
        "run_metadata_output_path": tmp_path / "l1_metadata.json",
    }


def test_l1_agent_batch_experiment_reports_before_after_metrics(tmp_path: Path) -> None:
    paths = _write_fixture_files(tmp_path)

    result = build_nasa_atmonto_l1_agent_batch_experiment(
        repo_root=tmp_path,
        sample_size=1,
        **paths,
    )

    assert result["status"] == "l1_agent_batch_experiment_scored"
    assert result["metadata"]["record_count"] == 1
    assert result["metadata"]["live_llm_run"] is False
    assert result["metrics"]["before"]["schema_violation_count"] == 1
    assert result["metrics"]["before"]["unsupported_fact_count"] == 1
    assert result["metrics"]["after"]["schema_violation_count"] == 0
    assert result["metrics"]["after"]["unsupported_fact_count"] == 0
    assert result["metrics"]["after"]["evidence_in_source_rate"] == 1.0
    assert result["metrics"]["repair"]["records_with_fact_gain"] == 1
    assert result["metrics"]["repair"]["net_accepted_fact_gain"] == 2


def test_write_l1_agent_batch_experiment_outputs_report_and_predictions(
    tmp_path: Path,
) -> None:
    paths = _write_fixture_files(tmp_path)
    output_dir = tmp_path / "reports"

    json_path, md_path, result = write_nasa_atmonto_l1_agent_batch_experiment(
        output_dir=output_dir,
        repo_root=tmp_path,
        sample_size=1,
        **paths,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert paths["prediction_output_path"].exists()
    assert paths["run_metadata_output_path"].exists()
    assert result["metrics"]["repair"]["repair_success_rate"] == 1.0
    markdown = md_path.read_text(encoding="utf-8")
    assert "NASA ATMONTO L1 Agent Batch Experiment" in markdown
    assert "Before vs After" in markdown
    assert "Schema violations" in markdown
    assert "Repair success rate" in markdown


def test_l1_agent_batch_cli_registers_report_command(tmp_path: Path) -> None:
    paths = _write_fixture_files(tmp_path)
    output_dir = tmp_path / "reports"

    result = CliRunner().invoke(
        main,
        [
            "report",
            "nasa-atmonto-l1-agent-batch",
            "--input-records",
            str(paths["input_records_path"]),
            "--baseline-predictions",
            str(paths["baseline_predictions_path"]),
            "--repair-predictions",
            str(paths["repair_predictions_path"]),
            "--schema-slice",
            str(paths["schema_slice_path"]),
            "--cq-manifest",
            str(paths["cq_manifest_path"]),
            "--prediction-output",
            str(paths["prediction_output_path"]),
            "--run-metadata-output",
            str(paths["run_metadata_output_path"]),
            "--sample-size",
            "1",
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "L1 agent batch status: l1_agent_batch_experiment_scored" in result.output
    assert (output_dir / "nasa_atmonto_l1_agent_batch_experiment.md").exists()
