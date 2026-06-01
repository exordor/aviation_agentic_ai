from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.ontology.atmonto_experiment import (
    SYSTEMS,
    build_formal_experiment_score_report,
    build_formal_experiment_readiness,
    build_gold_freeze_status,
    build_gold_annotation_validation_report,
    build_gold_review_worklist,
    build_prediction_output_validation_report,
    freeze_reviewed_gold_set,
    formal_scoring_gold_source,
    parse_llm_prediction_payload,
    prepare_formal_experiment_inputs,
    property_level_semantic_metrics,
    run_llm_prediction_system,
    semantic_metrics,
    structural_metrics,
    validate_gold_annotation_records,
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
    assert report["formal_input_status"]["input_records_exists"] is True
    assert report["formal_input_status"]["system_specs_exists"] is True
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
    assert report["formal_input_status"]["input_records_exists"] is True
    assert report["current_s0_rule_only_structural_metrics"]["attempted_record_count"] == 100


def test_prepare_formal_experiment_inputs_generates_batches_and_s0_predictions() -> None:
    result = prepare_formal_experiment_inputs(Path("."))

    assert result["input_record_count"] == 100
    assert result["s0_prediction_record_count"] == 100
    assert set(result["prompt_batches"].values()) == {100}

    s0_records = [
        json.loads(line)
        for line in Path(
            "data/experiments/nasa_atmonto/formal/s0_rule_only_predictions.jsonl"
        ).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(s0_records) == 100
    assert {record["system_id"] for record in s0_records} == {"S0_rule_only"}
    assert all("facts" in record for record in s0_records)


def test_llm_prompt_batches_keep_system_conditions_separate() -> None:
    s1 = json.loads(
        Path("data/experiments/nasa_atmonto/formal/s1_llm_only_prompt_batch.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )
    s2 = json.loads(
        Path("data/experiments/nasa_atmonto/formal/s2_llm_schema_slice_prompt_batch.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )
    s3 = json.loads(
        Path(
            "data/experiments/nasa_atmonto/formal/"
            "s3_llm_schema_slice_validator_repair_prompt_batch.jsonl"
        )
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )

    s1_system_prompt = s1["messages"][0]["content"]
    assert s1["schema_context_ref"] is None
    assert "NASA ATMONTO" not in s1_system_prompt
    assert "atm:" not in s1_system_prompt
    assert "controlledNASelement" not in s1_system_prompt

    s2_system_prompt = s2["messages"][0]["content"]
    assert s2["schema_context_ref"] == "data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json"
    assert "nasa_atmonto_atcscc_tmi_slice" in s2_system_prompt
    assert "atm:GroundStopTMI" in s2_system_prompt
    assert "controlledNASelement" in s2_system_prompt

    assert s3["stages"] == ["initial_extraction", "validate", "repair_if_invalid"]
    assert "Validator/repair condition" in s3["messages"][0]["content"]


def test_llm_prediction_payload_parser_marks_invalid_json_non_adherent() -> None:
    record = parse_llm_prediction_payload(
        raw_response="I could not produce JSON.",
        task={
            "system_id": "S1_llm_only",
            "sample_id": "ATCSCC-GOLD-001",
            "source_id": "2026-05-14:001",
            "source_family": "atcscc_advisories",
        },
    )

    assert record["json_adherence"] is False
    assert record["facts"] is None
    assert record["parse_error"]


def test_s3_llm_runner_repairs_validator_rejected_payload(tmp_path: Path) -> None:
    schema_target = tmp_path / "data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json"
    schema_target.parent.mkdir(parents=True, exist_ok=True)
    schema_target.write_text(
        Path("data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )

    formal_dir = tmp_path / "data/experiments/nasa_atmonto/formal"
    formal_dir.mkdir(parents=True, exist_ok=True)
    input_record = {
        "sample_id": "ATCSCC-GOLD-001",
        "source_id": "2026-05-14:001",
        "source_family": "atcscc_advisories",
        "source_text": "ATCSCC ADVZY 001 PROBABILITY OF EXTENSION: MODERATE",
    }
    (formal_dir / "input_records.jsonl").write_text(
        json.dumps(input_record, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    task = {
        "task_id": "S3_llm_schema_slice_validator_repair:ATCSCC-GOLD-001",
        "system_id": "S3_llm_schema_slice_validator_repair",
        "sample_id": "ATCSCC-GOLD-001",
        "source_id": "2026-05-14:001",
        "source_family": "atcscc_advisories",
        "messages": [
            {"role": "system", "content": "Return JSON only."},
            {"role": "user", "content": "PROBABILITY OF EXTENSION: MODERATE"},
        ],
    }
    (formal_dir / "s3_llm_schema_slice_validator_repair_prompt_batch.jsonl").write_text(
        json.dumps(task, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    initial_payload = {
        "source_id": "2026-05-14:001",
        "source_family": "atcscc_advisories",
        "facts": [
            {
                "fact_type": "datatype_property",
                "subject_class": "ReRouteTMI",
                "predicate": "extensionProbability",
                "value": "MODERATE",
                "datatype": "xsd:string",
                "evidence_text": "PROBABILITY OF EXTENSION: MODERATE",
            }
        ],
    }
    repaired_payload = {
        **initial_payload,
        "facts": [{**initial_payload["facts"][0], "value": "MEDIUM"}],
    }
    responses = [json.dumps(initial_payload), json.dumps(repaired_payload)]

    def fake_invoker(_messages: list[dict[str, str]]) -> str:
        return responses.pop(0)

    result = run_llm_prediction_system(
        system_id="S3_llm_schema_slice_validator_repair",
        repo_root=tmp_path,
        invoker=fake_invoker,
    )

    assert result["prediction_record_count"] == 1
    assert result["repair_attempted_record_count"] == 1
    assert result["repair_success_record_count"] == 1
    output = json.loads(
        (formal_dir / "s3_llm_schema_slice_validator_repair_predictions.jsonl")
        .read_text(encoding="utf-8")
        .strip()
    )
    assert output["json_adherence"] is True
    assert output["repair_attempted"] is True
    assert output["accepted_fact_count"] == 1
    assert output["rejected_fact_count"] == 0


def test_limited_llm_runner_writes_smoke_outputs_without_overwriting_formal_outputs(
    tmp_path: Path,
) -> None:
    schema_target = tmp_path / "data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json"
    schema_target.parent.mkdir(parents=True, exist_ok=True)
    schema_target.write_text(
        Path("data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json").read_text(
            encoding="utf-8"
        ),
        encoding="utf-8",
    )

    formal_dir = tmp_path / "data/experiments/nasa_atmonto/formal"
    formal_dir.mkdir(parents=True, exist_ok=True)
    input_records = [
        {
            "sample_id": "ATCSCC-GOLD-001",
            "source_id": "2026-05-14:001",
            "source_family": "atcscc_advisories",
            "source_text": "ATCSCC ADVZY 001 TEST",
        },
        {
            "sample_id": "ATCSCC-GOLD-002",
            "source_id": "2026-05-14:002",
            "source_family": "atcscc_advisories",
            "source_text": "ATCSCC ADVZY 002 TEST",
        },
    ]
    (formal_dir / "input_records.jsonl").write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in input_records) + "\n",
        encoding="utf-8",
    )
    tasks = [
        {
            "task_id": f"S1_llm_only:{record['sample_id']}",
            "system_id": "S1_llm_only",
            "sample_id": record["sample_id"],
            "source_id": record["source_id"],
            "source_family": "atcscc_advisories",
            "messages": [{"role": "user", "content": record["source_text"]}],
        }
        for record in input_records
    ]
    (formal_dir / "s1_llm_only_prompt_batch.jsonl").write_text(
        "\n".join(json.dumps(task, sort_keys=True) for task in tasks) + "\n",
        encoding="utf-8",
    )

    result = run_llm_prediction_system(
        system_id="S1_llm_only",
        repo_root=tmp_path,
        limit=1,
        invoker=lambda _messages: json.dumps(
            {
                "source_id": "2026-05-14:001",
                "source_family": "atcscc_advisories",
                "facts": [],
            }
        ),
    )

    assert result["output_scope"] == "smoke"
    assert result["run_status"] == "partial"
    assert result["prediction_record_count"] == 1
    assert result["prediction_output"].endswith("formal/smoke/s1_llm_only_predictions.jsonl")
    assert not (formal_dir / "s1_llm_only_predictions.jsonl").exists()
    assert (formal_dir / "smoke/s1_llm_only_predictions.jsonl").exists()
    metadata = json.loads(
        (formal_dir / "smoke/s1_llm_only_run_metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["output_scope"] == "smoke"
    assert metadata["prediction_output"].endswith("formal/smoke/s1_llm_only_predictions.jsonl")


def test_formal_score_report_is_pending_but_scores_s0_structure() -> None:
    prepare_formal_experiment_inputs(Path("."))
    report = build_formal_experiment_score_report(Path("."))

    assert report["status"] == "pending_required_inputs"
    assert report["gold_source"]["source"] == "frozen_reviewed_gold_missing"
    assert report["gold_source"]["ready_for_formal_scoring"] is False
    assert any("frozen reviewed gold set" in item for item in report["missing_required_inputs"])
    s0 = next(score for score in report["systems"] if score["system_id"] == "S0_rule_only")
    assert s0["available"] is True
    assert s0["json_metrics"]["json_adherence"] == 1.0
    assert s0["structural_metrics"]["candidate_fact_count"] == 615
    assert s0["structural_metrics"]["accepted_fact_count"] == 567
    assert s0["structural_metrics"]["rejected_fact_count"] == 48
    assert s0["semantic_metrics"]["available"] is False
    assert s0["semantic_metrics"]["reason"] == "manual_gold_facts_missing"

    s1 = next(score for score in report["systems"] if score["system_id"] == "S1_llm_only")
    assert s1["available"] is False
    assert s1["reason"] == "prediction_output_missing"


def test_formal_scoring_gold_source_prefers_frozen_reviewed_gold(tmp_path: Path) -> None:
    manifest_path = tmp_path / "data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json"
    template_path = tmp_path / "data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl"
    reviewed_path = tmp_path / "data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({"selected_source_ids": ["2026-05-14:001"]}) + "\n",
        encoding="utf-8",
    )
    fact = {
        "fact_id": "fact-1",
        "fact_type": "datatype_property",
        "subject": "urn:test",
        "subject_class": "GroundStopTMI",
        "predicate": "advisoryNumber",
        "value": 1,
        "datatype": "xsd:integer",
        "evidence_text": "ATCSCC ADVZY 001",
        "source_id": "2026-05-14:001",
    }
    reviewed_record = {
        "sample_id": "ATCSCC-GOLD-001",
        "source_id": "2026-05-14:001",
        "source_text": "ATCSCC ADVZY 001 DCC TEST",
        "candidate_facts": [fact],
        "validator_results": [],
        "gold_annotation": {
            "annotation_status": "reviewed",
            "annotator_id": "annotator-a",
            "valid_facts": [fact],
            "invalid_candidate_fact_ids": [],
            "missing_facts": [],
            "rejected_fact_adjudications": [],
        },
    }
    template_path.write_text(
        json.dumps({**reviewed_record, "gold_annotation": {"annotation_status": "pending_manual_gold_annotation"}})
        + "\n",
        encoding="utf-8",
    )
    reviewed_path.write_text(
        json.dumps(reviewed_record, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    source = formal_scoring_gold_source(tmp_path, {"2026-05-14:001"})

    assert source["source"] == "frozen_reviewed_gold"
    assert source["ready_for_formal_scoring"] is True
    assert source["gold_status"]["complete"] is True
    assert source["sha256"]
    assert len(source["records"]) == 1


def test_property_level_semantic_metrics_group_by_predicate() -> None:
    base = {
        "fact_type": "datatype_property",
        "subject_class": "GroundStopTMI",
        "datatype": "xsd:integer",
        "evidence_text": "ATCSCC ADVZY 001",
    }
    gold_fact = {**base, "predicate": "advisoryNumber", "value": 1}
    wrong_fact = {**base, "predicate": "advisoryNumber", "value": 2}
    other_gold = {
        **base,
        "predicate": "issuedTime",
        "value": "2026-05-14T00:01:00Z",
        "datatype": "xsd:dateTime",
    }

    rows = property_level_semantic_metrics(
        predictions=[gold_fact, wrong_fact],
        gold_records=[
            {
                "gold_annotation": {
                    "annotation_status": "reviewed",
                    "valid_facts": [gold_fact],
                    "missing_facts": [other_gold],
                }
            }
        ],
    )

    by_predicate = {row["predicate"]: row for row in rows}
    assert by_predicate["advisoryNumber"]["true_positive_count"] == 1
    assert by_predicate["advisoryNumber"]["false_positive_count"] == 1
    assert by_predicate["issuedTime"]["false_negative_count"] == 1


def test_gold_annotation_validation_reports_current_template_pending() -> None:
    report = build_gold_annotation_validation_report(Path("."))

    assert report["status"] == "pending_manual_annotation"
    assert report["record_count"] == 100
    assert report["reviewed_record_count"] == 0
    assert report["pending_record_count"] == 100
    assert report["error_count"] == 0
    assert report["warning_count"] == 100


def test_gold_annotation_validation_accepts_reviewed_record_with_rejection_decision() -> None:
    fact = {
        "fact_id": "fact-1",
        "fact_type": "datatype_property",
        "subject": "urn:test",
        "subject_class": "GroundStopTMI",
        "predicate": "advisoryNumber",
        "value": 1,
        "datatype": "xsd:integer",
        "evidence_text": "ATCSCC ADVZY 001",
        "source_id": "2026-05-14:001",
    }
    record = {
        "sample_id": "ATCSCC-GOLD-001",
        "source_id": "2026-05-14:001",
        "source_text": "ATCSCC ADVZY 001 DCC TEST",
        "candidate_facts": [fact],
        "validator_results": [
            {"fact_id": "fact-rejected", "accepted": False, "errors": ["range_violation"]}
        ],
        "gold_annotation": {
            "annotation_status": "reviewed",
            "annotator_id": "annotator-a",
            "valid_facts": [fact],
            "invalid_candidate_fact_ids": [],
            "missing_facts": [],
            "rejected_fact_adjudications": [
                {
                    "fact_id": "fact-rejected",
                    "decision": "profile_gap",
                    "rationale": "Source supports the fact but current profile range is too narrow.",
                    "recommended_action": "Review NASA ATMONTO runtime profile extension.",
                }
            ],
        },
    }

    report = validate_gold_annotation_records(
        gold_records=[record],
        selected_source_ids={"2026-05-14:001"},
    )

    assert report["status"] == "ready_for_scoring"
    assert report["error_count"] == 0
    assert report["warning_count"] == 0


def test_gold_freeze_status_blocks_current_pending_template() -> None:
    report = build_gold_freeze_status(Path("."))

    assert report["status"] == "blocked_pending_review"
    assert report["validation_status"] == "pending_manual_annotation"
    assert report["record_count"] == 100
    assert report["pending_record_count"] == 100
    assert report["reviewed_gold_output"].endswith("atcscc_gold_v1.reviewed.jsonl")


def test_freeze_reviewed_gold_set_writes_only_valid_reviewed_gold(tmp_path: Path) -> None:
    manifest_path = tmp_path / "data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json"
    template_path = tmp_path / "data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({"selected_source_ids": ["2026-05-14:001"]}) + "\n",
        encoding="utf-8",
    )
    fact = {
        "fact_id": "fact-1",
        "fact_type": "datatype_property",
        "subject": "urn:test",
        "subject_class": "GroundStopTMI",
        "predicate": "advisoryNumber",
        "value": 1,
        "datatype": "xsd:integer",
        "evidence_text": "ATCSCC ADVZY 001",
        "source_id": "2026-05-14:001",
    }
    reviewed_record = {
        "sample_id": "ATCSCC-GOLD-001",
        "source_id": "2026-05-14:001",
        "source_text": "ATCSCC ADVZY 001 DCC TEST",
        "candidate_facts": [fact],
        "validator_results": [],
        "gold_annotation": {
            "annotation_status": "reviewed",
            "annotator_id": "annotator-a",
            "valid_facts": [fact],
            "invalid_candidate_fact_ids": [],
            "missing_facts": [],
            "rejected_fact_adjudications": [],
        },
    }
    template_path.write_text(
        json.dumps(reviewed_record, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    report = freeze_reviewed_gold_set(tmp_path)

    assert report["status"] == "frozen"
    assert report["validation_status"] == "ready_for_scoring"
    assert report["output_exists"] is True
    assert report["output_sha256"]
    frozen = (
        tmp_path / "data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl"
    ).read_text(encoding="utf-8")
    assert "ATCSCC-GOLD-001" in frozen


def test_prediction_output_validation_reports_s0_ready_and_llm_outputs_pending() -> None:
    prepare_formal_experiment_inputs(Path("."))
    report = build_prediction_output_validation_report(Path("."))

    assert report["status"] == "pending_required_outputs"
    s0 = next(system for system in report["systems"] if system["system_id"] == "S0_rule_only")
    assert s0["status"] == "ready_for_scoring"
    assert s0["json_metrics"]["json_adherence"] == 1.0
    assert s0["run_metadata"]["exists"] is True

    s1 = next(system for system in report["systems"] if system["system_id"] == "S1_llm_only")
    assert s1["status"] == "pending_required_outputs"
    assert "prediction_output_missing" in s1["pending"]
    assert "run_metadata_missing" in s1["pending"]
    assert s1["prompt_batch"]["status"] == "ready"


def test_generated_prediction_output_validation_report_json_is_consistent() -> None:
    report = json.loads(
        Path("reports/stages/nasa_atmonto_prediction_output_validation.json").read_text(
            encoding="utf-8"
        )
    )

    assert report["status"] == "pending_required_outputs"
    assert report["selected_source_id_count"] == 100
    assert any(system["system_id"] == "S0_rule_only" for system in report["systems"])


def test_gold_review_worklist_summarizes_human_annotation_queue() -> None:
    worklist = build_gold_review_worklist(Path("."))

    assert worklist["record_count"] == 100
    assert worklist["selected_source_id_count"] == 100
    assert worklist["records_with_rejections"] == 40
    assert worklist["total_rejected_facts_to_adjudicate"] == 48
    assert worklist["status_counts"] == {"pending_manual_gold_annotation": 100}
    assert worklist["suggested_decision_counts"] == {
        "extractor_normalization_bug_candidate": 8,
        "nasa_atmonto_profile_gap_candidate": 40,
    }

    first_rejected = next(
        fact
        for record in worklist["records"]
        for fact in record["rejected_facts_to_adjudicate"]
    )
    assert first_rejected["fact_id"]
    assert first_rejected["predicate"]
    assert first_rejected["suggested_decision"] in {
        "extractor_normalization_bug_candidate",
        "nasa_atmonto_profile_gap_candidate",
    }
