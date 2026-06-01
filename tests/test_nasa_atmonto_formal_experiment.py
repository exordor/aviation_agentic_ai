from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.ontology.atmonto_experiment import (
    SYSTEMS,
    build_formal_experiment_readiness,
    semantic_metrics,
    structural_metrics,
)


def test_formal_experiment_registers_four_required_systems() -> None:
    assert [system.system_id for system in SYSTEMS] == [
        "S0_rule_only",
        "S1_llm_only",
        "S2_llm_schema_slice",
        "S3_llm_schema_slice_validator_repair",
    ]
    assert [system.requires_llm for system in SYSTEMS] == [False, True, True, True]
    assert [system.uses_validator_repair for system in SYSTEMS] == [
        False,
        False,
        False,
        True,
    ]


def test_structural_metrics_report_schema_violation_and_repair_rates() -> None:
    metrics = structural_metrics(
        [
            {"accepted": True, "status": "accepted_deterministic", "repairs": []},
            {"accepted": True, "status": "repaired_accepted", "repairs": ["identifier_expansion"]},
            {"accepted": False, "status": "rejected_schema", "errors": ["domain_violation"]},
        ]
    )

    assert metrics["candidate_fact_count"] == 3
    assert metrics["accepted_fact_count"] == 2
    assert metrics["rejected_fact_count"] == 1
    assert metrics["schema_violation_rate"] == 1 / 3
    assert metrics["repair_success_rate"] == 1 / 2
    assert metrics["error_counts"] == {"domain_violation": 1}


def test_semantic_metrics_wait_for_manual_gold_when_gold_is_empty() -> None:
    metrics = semantic_metrics(
        predictions=[
            {
                "fact_type": "datatype_property",
                "subject_class": "GroundStopTMI",
                "predicate": "advisoryNumber",
                "value": 1,
                "datatype": "xsd:integer",
                "evidence_text": "ATCSCC ADVZY 001",
            }
        ],
        gold_records=[
            {
                "gold_annotation": {
                    "annotation_status": "pending_manual_gold_annotation",
                    "valid_facts": [],
                    "missing_facts": [],
                }
            }
        ],
    )

    assert metrics["available"] is False
    assert metrics["reason"] == "manual_gold_facts_missing"
    assert metrics["precision"] is None


def test_semantic_metrics_compute_precision_recall_f1_when_gold_exists() -> None:
    fact = {
        "fact_type": "datatype_property",
        "subject_class": "GroundStopTMI",
        "predicate": "advisoryNumber",
        "value": 1,
        "datatype": "xsd:integer",
        "evidence_text": "ATCSCC ADVZY 001",
    }

    metrics = semantic_metrics(
        predictions=[fact, {**fact, "value": 2}],
        gold_records=[
            {
                "gold_annotation": {
                    "annotation_status": "reviewed",
                    "valid_facts": [fact],
                    "missing_facts": [{**fact, "predicate": "issuedTime", "value": "2026-05-14T00:01:00Z"}],
                }
            }
        ],
    )

    assert metrics["available"] is True
    assert metrics["true_positive_count"] == 1
    assert metrics["false_positive_count"] == 1
    assert metrics["false_negative_count"] == 1
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5
    assert metrics["f1"] == 0.5


def test_readiness_report_marks_gold_and_llm_outputs_as_pending() -> None:
    report = build_formal_experiment_readiness(Path("."))

    assert report["status"] == "ready_for_manual_gold_and_llm_runs"
    assert report["gold_status"]["record_count"] == 100
    assert report["gold_status"]["complete"] is False
    assert "completed manual gold annotations" in report["missing_required_inputs"][0]
    assert any("S1_llm_only predictions" in item for item in report["missing_required_inputs"])


def test_generated_readiness_report_json_is_consistent() -> None:
    report = json.loads(
        Path("reports/stages/nasa_atmonto_formal_experiment_readiness.json").read_text(
            encoding="utf-8"
        )
    )

    assert report["status"] == "ready_for_manual_gold_and_llm_runs"
    assert report["gold_status"]["pending_record_count"] == 100
    assert report["current_s0_rule_only_structural_metrics"]["attempted_record_count"] == 100
