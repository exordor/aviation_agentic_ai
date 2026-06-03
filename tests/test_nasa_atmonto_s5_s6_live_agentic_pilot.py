from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.reporting.nasa_atmonto_s5_s6_live_agentic_pilot import (
    write_nasa_atmonto_s5_s6_live_agentic_pilot,
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


def _fixture_paths(tmp_path: Path) -> dict[str, Path]:
    source_text = (
        "ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS "
        "EFFECTIVE TIME: 151918-160030 USERS CAN EXPECT ARRIVAL DELAYS"
    )
    input_path = tmp_path / "input.jsonl"
    _write_jsonl(
        input_path,
        [
            {
                "sample_id": "ATCSCC-GOLD-001",
                "source_id": "2026-05-15:063",
                "source_family": "atcscc_advisories",
                "source_text": source_text,
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
    return {
        "input_records_path": input_path,
        "schema_slice_path": schema_path,
        "gold_path": gold_path,
        "cq_manifest_path": cq_path,
        "prediction_output_path": tmp_path / "predictions.jsonl",
        "run_metadata_output_path": tmp_path / "metadata.json",
    }


def _fake_invoker(messages: list[dict[str, str]]) -> str:
    system = messages[0]["content"]
    if "Extractor agent" in system:
        return json.dumps(
            {
                "source_id": "2026-05-15:063",
                "source_family": "atcscc_advisories",
                "facts": [
                    {
                        "fact_id": "f-good",
                        "fact_type": "datatype_property",
                        "subject": "urn:test",
                        "subject_class": "TrafficManagementInitiative",
                        "predicate": "advisoryNumber",
                        "datatype": "xsd:integer",
                        "value": 63,
                        "evidence_text": (
                            "ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS"
                        ),
                    },
                    {
                        "fact_id": "f-bad",
                        "fact_type": "object_property",
                        "subject": "urn:test",
                        "subject_class": "TrafficManagementInitiative",
                        "predicate": "controlledNASelement",
                        "object": "urn:aviation-agentic-ai:nas-element:USERS",
                        "object_label": "USERS",
                        "object_class": "TFMcontrolElement",
                        "evidence_text": "USERS CAN EXPECT ARRIVAL DELAYS",
                    },
                ],
            }
        )
    if "Critic agent" in system:
        return json.dumps({"drop_fact_ids": ["f-bad"], "concerns": [], "global_notes": []})
    if "Refiner agent" in system:
        return json.dumps(
            {
                "source_id": "2026-05-15:063",
                "source_family": "atcscc_advisories",
                "facts": [
                    {
                        "fact_id": "f-good",
                        "fact_type": "datatype_property",
                        "subject": "urn:test",
                        "subject_class": "TrafficManagementInitiative",
                        "predicate": "advisoryNumber",
                        "datatype": "xsd:integer",
                        "value": 63,
                        "evidence_text": (
                            "ATCSCC ADVZY 063 SAN/ZLA 05/15/2026 SAN AIRPORT ARRIVAL DELAYS"
                        ),
                    }
                ],
            }
        )
    raise AssertionError(f"Unexpected prompt: {system}")


def test_live_agentic_pilot_runs_extractor_validator_critic_refiner(
    tmp_path: Path,
) -> None:
    paths = _fixture_paths(tmp_path)

    _json_path, _md_path, result = write_nasa_atmonto_s5_s6_live_agentic_pilot(
        output_dir=tmp_path / "reports",
        repo_root=tmp_path,
        invoker=_fake_invoker,
        invoker_label="test_invoker",
        **paths,
    )

    assert result["status"] == "s5_s6_live_agentic_pilot_scored"
    assert result["metadata"]["live_llm_run"] is False
    assert result["metadata"]["s5_fact_count"] == 2
    assert result["metadata"]["s6_fact_count"] == 1
    assert result["quality_counters"]["agent_call_counts"] == {
        "extractor": 1,
        "validator": 1,
        "critic": 1,
        "refiner": 1,
    }
    assert result["quarantine_summary"]["reason_counts"]["live_critic_drop"] == 1
    assert result["metrics"]["s6_live_refined_semantic_metrics"]["f1"] == 1.0


def test_live_agentic_pilot_writes_outputs(
    tmp_path: Path,
) -> None:
    paths = _fixture_paths(tmp_path)
    json_path, md_path, result = write_nasa_atmonto_s5_s6_live_agentic_pilot(
        output_dir=tmp_path / "reports",
        repo_root=tmp_path,
        invoker=_fake_invoker,
        invoker_label="test_invoker",
        **paths,
    )

    assert json_path.exists()
    assert md_path.exists()
    assert paths["prediction_output_path"].exists()
    assert paths["run_metadata_output_path"].exists()
    assert "Live Agentic Pilot" in md_path.read_text(encoding="utf-8")
    assert result["metadata"]["prediction_output"].endswith("predictions.jsonl")
