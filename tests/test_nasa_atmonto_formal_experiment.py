from __future__ import annotations

import json
from pathlib import Path

from aviation_agentic_ai.ontology.atmonto_experiment import (
    SYSTEMS,
    build_formal_experiment_score_report,
    build_formal_experiment_readiness,
    build_gold_freeze_status,
    build_gold_annotation_validation_report,
    build_gold_review_priority_packets,
    build_gold_review_worklist,
    build_gold_review_workload_plan,
    build_gold_review_batches,
    build_gold_review_decision_templates,
    build_gold_review_progress,
    build_prediction_output_validation_report,
    build_rejection_adjudication_report,
    build_system_candidate_review_package,
    apply_gold_review_decisions,
    freeze_reviewed_gold_set,
    formal_scoring_gold_source,
    parse_llm_prediction_payload,
    prepare_formal_experiment_inputs,
    property_level_semantic_metrics,
    reprocess_llm_prediction_system_outputs,
    rejection_adjudication_markdown,
    run_llm_prediction_system,
    gold_review_batch_index_markdown,
    gold_review_batch_markdown,
    gold_review_decision_index_markdown,
    gold_review_priority_packet_index_markdown,
    gold_review_priority_packet_markdown,
    gold_review_progress_markdown,
    gold_review_workload_plan_markdown,
    score_report_markdown,
    semantic_metrics,
    structural_metrics,
    system_candidate_review_markdown,
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


def test_readiness_report_marks_manual_gold_as_pending_after_llm_outputs() -> None:
    report = build_formal_experiment_readiness(Path("."))

    assert report["status"] == "ready_for_manual_gold_review"
    assert report["gold_status"]["record_count"] == 100
    assert report["gold_status"]["complete"] is False
    assert report["formal_input_status"]["input_records_exists"] is True
    assert report["formal_input_status"]["system_specs_exists"] is True
    assert report["manual_review_artifacts"]["workload_plan"].endswith(
        "nasa_atmonto_gold_review_workload_plan.md"
    )
    assert report["manual_review_artifacts"]["priority_packets"].endswith(
        "review_priority_packets/index.md"
    )
    assert "completed manual gold annotations" in report["missing_required_inputs"][0]
    assert not any("predictions" in item for item in report["missing_required_inputs"])


def test_generated_readiness_report_json_is_consistent() -> None:
    report = json.loads(
        Path("reports/stages/nasa_atmonto_formal_experiment_readiness.json").read_text(
            encoding="utf-8"
        )
    )

    assert report["status"] == "ready_for_manual_gold_review"
    assert report["gold_status"]["pending_record_count"] == 100
    assert report["formal_input_status"]["input_records_exists"] is True
    assert report["manual_review_artifacts"]["workload_plan"].endswith(
        "nasa_atmonto_gold_review_workload_plan.md"
    )
    assert report["manual_review_artifacts"]["priority_packets"].endswith(
        "review_priority_packets/index.md"
    )
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


def test_llm_prediction_payload_parser_flattens_schema_object_shape() -> None:
    schema_slice = json.loads(
        Path("data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json").read_text(
            encoding="utf-8"
        )
    )
    record = parse_llm_prediction_payload(
        raw_response=json.dumps(
            {
                "source_id": "2026-05-14:001",
                "source_family": "atcscc_advisories",
                "facts": [
                    {
                        "subject": "urn:aviation-agentic-ai:tmi:2026-05-14:001",
                        "type": "atm:TrafficManagementInitiative",
                        "properties": {
                            "atm:advisoryNumber": [
                                {
                                    "value": 1,
                                    "evidence_text": "ATCSCC ADVZY 001",
                                }
                            ],
                            "atm:issuedTime": [
                                {
                                    "value": "2026-05-14T00:01:00Z",
                                    "evidence_text": "SIGNATURE: 26/05/14 00:01",
                                }
                            ],
                            "atm:controlledNASelement": [
                                {
                                    "value": {"label": "ZNY", "type": "nas:ARTCC"},
                                    "evidence_text": "CONSTRAINED FACILITIES: ZNY",
                                }
                            ],
                        },
                    }
                ],
            }
        ),
        task={
            "system_id": "S2_llm_schema_slice",
            "sample_id": "ATCSCC-GOLD-001",
            "source_id": "2026-05-14:001",
            "source_family": "atcscc_advisories",
        },
        schema_slice=schema_slice,
    )

    assert record["json_adherence"] is True
    assert record["flattened_schema_object_fact_count"] == 3
    assert [fact["predicate"] for fact in record["facts"]] == [
        "atm:advisoryNumber",
        "atm:issuedTime",
        "atm:controlledNASelement",
    ]
    assert all(fact["subject_class"] == "atm:TrafficManagementInitiative" for fact in record["facts"])
    assert record["facts"][2]["fact_type"] == "object_property"
    assert record["facts"][2]["object"] == "ZNY"
    assert record["facts"][2]["object_class"] == "nas:ARTCC"


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


def test_reprocess_llm_predictions_rebuilds_saved_schema_object_raw_response(
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
    input_record = {
        "sample_id": "ATCSCC-GOLD-001",
        "source_id": "2026-05-14:001",
        "source_family": "atcscc_advisories",
        "source_text": "ATCSCC ADVZY 001 SIGNATURE: 26/05/14 00:01",
    }
    (formal_dir / "input_records.jsonl").write_text(
        json.dumps(input_record, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    task = {
        "task_id": "S2_llm_schema_slice:ATCSCC-GOLD-001",
        "system_id": "S2_llm_schema_slice",
        "sample_id": "ATCSCC-GOLD-001",
        "source_id": "2026-05-14:001",
        "source_family": "atcscc_advisories",
        "messages": [{"role": "user", "content": input_record["source_text"]}],
    }
    (formal_dir / "s2_llm_schema_slice_prompt_batch.jsonl").write_text(
        json.dumps(task, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    raw_response = json.dumps(
        {
            "source_id": "2026-05-14:001",
            "source_family": "atcscc_advisories",
            "facts": [
                {
                    "type": "atm:TrafficManagementInitiative",
                    "properties": {
                        "atm:advisoryNumber": {
                            "value": 1,
                            "evidence_text": "ATCSCC ADVZY 001",
                        }
                    },
                }
            ],
        }
    )
    stale_record = {
        "system_id": "S2_llm_schema_slice",
        "sample_id": "ATCSCC-GOLD-001",
        "source_id": "2026-05-14:001",
        "source_family": "atcscc_advisories",
        "json_adherence": True,
        "facts": [{"type": "atm:TrafficManagementInitiative", "properties": {}}],
        "raw_response": raw_response,
        "parse_error": None,
        "validator_results": [
            {
                "accepted": False,
                "fact_id": "stale",
                "errors": ["unknown_fact_type"],
            }
        ],
    }
    (formal_dir / "s2_llm_schema_slice_predictions.jsonl").write_text(
        json.dumps(stale_record, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (formal_dir / "s2_llm_schema_slice_run_metadata.json").write_text(
        json.dumps({"system_id": "S2_llm_schema_slice"}, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = reprocess_llm_prediction_system_outputs(
        system_id="S2_llm_schema_slice",
        repo_root=tmp_path,
    )

    assert result["prediction_record_count"] == 1
    assert result["flattened_schema_object_fact_count"] == 1
    output = json.loads(
        (formal_dir / "s2_llm_schema_slice_predictions.jsonl").read_text(encoding="utf-8")
    )
    assert output["reprocessed_from_saved_raw_response"] is True
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
    assert metadata["resumed"] is False
    assert metadata["skipped_existing_record_count"] == 0
    assert metadata["prediction_output"].endswith("formal/smoke/s1_llm_only_predictions.jsonl")


def test_llm_runner_checkpoints_and_resumes_existing_predictions(tmp_path: Path) -> None:
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
    existing_prediction = {
        "system_id": "S1_llm_only",
        "sample_id": "ATCSCC-GOLD-001",
        "source_id": "2026-05-14:001",
        "source_family": "atcscc_advisories",
        "json_adherence": True,
        "facts": [],
        "raw_response": '{"facts":[]}',
        "parse_error": None,
        "validator_results": [],
        "schema_valid": True,
        "candidate_fact_count": 0,
        "accepted_fact_count": 0,
        "rejected_fact_count": 0,
    }
    (formal_dir / "s1_llm_only_predictions.jsonl").write_text(
        json.dumps(existing_prediction, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    invoked_source_ids: list[str] = []

    def fake_invoker(messages: list[dict[str, str]]) -> str:
        invoked_source_ids.append(messages[-1]["content"])
        return json.dumps(
            {
                "source_id": "2026-05-14:002",
                "source_family": "atcscc_advisories",
                "facts": [],
            }
        )

    result = run_llm_prediction_system(
        system_id="S1_llm_only",
        repo_root=tmp_path,
        resume=True,
        invoker=fake_invoker,
    )

    assert result["prediction_record_count"] == 2
    assert len(invoked_source_ids) == 1
    output_lines = [
        json.loads(line)
        for line in (formal_dir / "s1_llm_only_predictions.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    assert [record["source_id"] for record in output_lines] == [
        "2026-05-14:001",
        "2026-05-14:002",
    ]
    metadata = json.loads(
        (formal_dir / "s1_llm_only_run_metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["resumed"] is True
    assert metadata["skipped_existing_record_count"] == 1
    assert metadata["run_status"] == "completed"


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
    assert s1["available"] is True
    assert s1["json_metrics"]["json_adherence"] == 1.0
    assert s1["structural_metrics"]["candidate_fact_count"] == 1211
    assert s1["structural_metrics"]["rejected_fact_count"] == 1211
    assert s1["semantic_metrics"]["reason"] == "manual_gold_facts_missing"

    audit = report["completion_audit"]
    assert audit["overall_status"] == "formal_experiment_pending"
    by_requirement = {item["id"]: item for item in audit["requirements"]}
    assert by_requirement["R1"]["status"] == "satisfied"
    assert by_requirement["R2"]["status"] == "pending_manual_input"
    assert by_requirement["R4"]["status"] == "satisfied"
    assert by_requirement["R7"]["status"] == "satisfied"
    assert by_requirement["R8"]["status"] == "satisfied"

    claim_status = {item["id"]: item["status"] for item in report["claim_statuses"]}
    hypothesis_status = {item["id"]: item["status"] for item in report["hypothesis_statuses"]}
    assert claim_status["C1"] == "supported_by_pilot"
    assert claim_status["C2"] == "supported_structural_only"
    assert claim_status["C4"] == "supported"
    assert hypothesis_status["H1"] == "supported_structural_only"
    assert hypothesis_status["H4"] == "supported"
    assert report["rejection_adjudication"]["property_level_complete"] is True
    assert report["rejection_adjudication"]["decision_counts_by_fact"] == {
        "extractor_bug": 13,
        "profile_gap": 275,
    }

    markdown = score_report_markdown(report)
    assert "## Rejection Adjudication" in markdown
    assert "## Claim Status" in markdown
    assert "## Hypothesis Status" in markdown
    assert "## Completion Audit" in markdown
    assert "`R2` Freeze reviewed gold annotations before semantic scoring." in markdown


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


def test_prediction_output_validation_reports_all_systems_ready() -> None:
    prepare_formal_experiment_inputs(Path("."))
    report = build_prediction_output_validation_report(Path("."))

    assert report["status"] == "ready_for_scoring"
    s0 = next(system for system in report["systems"] if system["system_id"] == "S0_rule_only")
    assert s0["status"] == "ready_for_scoring"
    assert s0["json_metrics"]["json_adherence"] == 1.0
    assert s0["run_metadata"]["exists"] is True

    s1 = next(system for system in report["systems"] if system["system_id"] == "S1_llm_only")
    assert s1["status"] == "ready_for_scoring"
    assert s1["pending"] == []
    assert s1["json_metrics"]["attempted_record_count"] == 100
    assert s1["run_metadata"]["status"] == "ready"
    assert s1["prompt_batch"]["status"] == "ready"


def test_generated_prediction_output_validation_report_json_is_consistent() -> None:
    report = json.loads(
        Path("reports/stages/nasa_atmonto_prediction_output_validation.json").read_text(
            encoding="utf-8"
        )
    )

    assert report["status"] == "ready_for_scoring"
    assert report["selected_source_id_count"] == 100
    assert all(system["status"] == "ready_for_scoring" for system in report["systems"])


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


def test_gold_review_workload_plan_prioritizes_manual_review_queue() -> None:
    plan = build_gold_review_workload_plan(Path("."))

    assert plan["record_count"] == 100
    assert plan["batch_count"] == 10
    assert plan["records_with_rejections"] == 40
    assert plan["total_rejected_facts_to_adjudicate"] == 48
    assert plan["estimated_total_review_minutes"] > 0
    assert sum(plan["complexity_counts"].values()) == 100
    assert sum(plan["priority_lane_counts"].values()) == 100
    assert plan["priority_lane_counts"]["1_rejection_adjudication"] == 40

    first = plan["recommended_review_order"][0]
    assert first["priority_lane"] == "1_rejection_adjudication"
    assert first["rejected_fact_count"] > 0
    assert first["batch_id"].startswith("batch_")

    first_batch = plan["batches"][0]
    assert first_batch["batch_id"] == "batch_01"
    assert first_batch["estimated_review_minutes"] > 0
    assert sum(first_batch["complexity_counts"].values()) == first_batch["record_count"]

    markdown = gold_review_workload_plan_markdown(plan)
    assert "Gold Review Workload Plan" in markdown
    assert "Recommended Review Order" in markdown
    assert "does not create gold truth" in markdown


def test_gold_review_priority_packets_expose_copyable_review_ids() -> None:
    report = build_gold_review_priority_packets(Path("."))

    assert report["record_count"] == 100
    assert report["lane_count"] == 3
    assert report["priority_lane_counts"] == {
        "1_rejection_adjudication": 40,
        "2_high_cross_system_coverage": 7,
        "3_standard_review": 53,
    }

    first_lane = report["lanes"][0]
    assert first_lane["lane_id"] == "1_rejection_adjudication"
    assert first_lane["record_count"] == 40
    assert first_lane["records"][0]["rejected_facts_to_adjudicate"]

    first_cluster = next(
        cluster
        for record in first_lane["records"]
        for cluster in record["candidate_clusters"]
        if cluster["s0_fact_ids"] or cluster["schema_valid_cross_system_fact_ids"]
    )
    assert first_cluster["candidate_id"]
    assert first_cluster["s0_fact_ids"] or first_cluster["schema_valid_cross_system_fact_ids"]

    index_markdown = gold_review_priority_packet_index_markdown(report)
    packet_markdown = gold_review_priority_packet_markdown(first_lane)
    assert "Gold Review Priority Packets" in index_markdown
    assert "valid_candidate_fact_ids" in packet_markdown
    assert "valid_cross_system_fact_ids" in packet_markdown
    assert "Rejected facts to adjudicate" in packet_markdown


def test_system_candidate_review_package_covers_all_prediction_systems() -> None:
    report = build_system_candidate_review_package(Path("."))

    assert report["record_count"] == 100
    assert report["selected_source_id_count"] == 100
    assert report["system_ids"] == [
        "S0_rule_only",
        "S1_llm_only",
        "S2_llm_schema_slice",
        "S3_llm_schema_slice_validator_repair",
    ]
    assert all(report["prediction_outputs_exist_by_system"].values())
    assert report["raw_fact_counts_by_system"]["S0_rule_only"] == 615
    assert report["raw_fact_counts_by_system"]["S1_llm_only"] == 1211
    assert report["raw_fact_counts_by_system"]["S2_llm_schema_slice"] == 708
    assert report["raw_fact_counts_by_system"]["S3_llm_schema_slice_validator_repair"] == 396
    assert report["candidate_cluster_count"] > report["raw_fact_counts_by_system"]["S0_rule_only"]

    first = report["records"][0]
    assert first["sample_id"] == "ATCSCC-GOLD-001"
    assert first["candidate_cluster_count"] > 0
    assert any(
        "S1_llm_only" in cluster["source_systems"]
        for cluster in first["candidate_clusters"]
    )

    markdown = system_candidate_review_markdown(report)
    assert "Cross-System Candidate Review" in markdown
    assert "not itself reviewed gold" in markdown


def test_gold_review_batches_split_cross_system_candidates_for_manual_review() -> None:
    candidate_review = build_system_candidate_review_package(Path("."))
    report = build_gold_review_batches(Path("."), candidate_review=candidate_review)

    assert report["batch_size"] == 10
    assert report["batch_count"] == 10
    assert report["record_count"] == 100
    assert report["candidate_cluster_count"] == candidate_review["candidate_cluster_count"]

    first_batch = report["batches"][0]
    assert first_batch["batch_id"] == "batch_01"
    assert first_batch["record_count"] == 10
    assert first_batch["first_sample_id"] == "ATCSCC-GOLD-001"
    assert first_batch["last_sample_id"] == "ATCSCC-GOLD-010"
    assert first_batch["candidate_cluster_count"] > 0

    batch_markdown = gold_review_batch_markdown(first_batch)
    assert "Batch Checklist" in batch_markdown
    assert "ATCSCC-GOLD-001" in batch_markdown
    assert "valid facts selected" in batch_markdown

    index_markdown = gold_review_batch_index_markdown(report)
    assert "Gold Review Batches" in index_markdown
    assert "batch_10" in index_markdown


def test_gold_review_progress_tracks_batch_completion_against_template() -> None:
    candidate_review = build_system_candidate_review_package(Path("."))
    batch_report = build_gold_review_batches(Path("."), candidate_review=candidate_review)
    report = build_gold_review_progress(Path("."), batch_report=batch_report)

    assert report["status"] == "pending_manual_review"
    assert report["record_count"] == 100
    assert report["reviewed_record_count"] == 0
    assert report["pending_record_count"] == 100
    assert report["batch_count"] == 10
    assert report["complete_batch_count"] == 0
    assert report["validation_status"] == "pending_manual_annotation"
    assert all(batch["status"] == "not_started" for batch in report["batch_progress"])

    first = report["batch_progress"][0]
    assert first["batch_id"] == "batch_01"
    assert first["record_count"] == 10
    assert first["pending_record_count"] == 10
    assert first["records"][0]["sample_id"] == "ATCSCC-GOLD-001"
    assert first["records"][0]["annotation_status"] == "pending_manual_gold_annotation"

    markdown = gold_review_progress_markdown(report)
    assert "Gold Review Progress" in markdown
    assert "pending_manual_review" in markdown
    assert "batch_01" in markdown


def test_gold_review_decision_templates_prepare_structured_review_inputs() -> None:
    candidate_review = build_system_candidate_review_package(Path("."))
    batch_report = build_gold_review_batches(Path("."), candidate_review=candidate_review)
    report = build_gold_review_decision_templates(Path("."), batch_report=batch_report)

    assert report["batch_count"] == 10
    assert report["record_count"] == 100
    first_batch = report["batches"][0]
    assert first_batch["batch_id"] == "batch_01"
    assert first_batch["record_count"] == 10
    assert first_batch["rejected_fact_adjudication_count"] > 0

    first_record = first_batch["records"][0]
    assert first_record["sample_id"] == "ATCSCC-GOLD-001"
    assert first_record["annotation_status"] == "pending_manual_gold_annotation"
    assert first_record["valid_candidate_fact_ids"] == []
    assert first_record["valid_cross_system_fact_ids"] == []
    assert first_record["review_context"]["candidate_cluster_count"] > 0
    assert first_record["review_context"]["cross_system_fact_ids"]
    assert first_record["review_context"]["cross_system_candidate_options"]
    first_adjudication = first_record["rejected_fact_adjudications"][0]
    assert first_adjudication["decision"] == ""
    assert first_adjudication["suggested_decision"] in {"extractor_bug", "profile_gap"}
    assert first_adjudication["suggested_rationale"]
    assert first_adjudication["suggested_recommended_action"]

    markdown = gold_review_decision_index_markdown(report)
    assert "Gold Review Decision Templates" in markdown
    assert "batch_10" in markdown
    assert "suggested_*" in markdown


def test_apply_gold_review_decisions_writes_reviewed_gold_draft(tmp_path: Path) -> None:
    eval_dir = tmp_path / "data/evaluation/nasa_atmonto"
    eval_dir.mkdir(parents=True)
    (eval_dir / "atcscc_gold_sample_manifest.json").write_text(
        json.dumps({"selected_source_ids": ["SRC1"]}) + "\n",
        encoding="utf-8",
    )
    fact = {
        "fact_id": "fact-1",
        "fact_type": "datatype_property",
        "subject_class": "TrafficManagementInitiative",
        "predicate": "advisoryNumber",
        "value": 1,
        "datatype": "xsd:integer",
        "evidence_text": "ADVZY 001",
        "source_id": "SRC1",
    }
    record = {
        "sample_id": "ATCSCC-GOLD-001",
        "source_id": "SRC1",
        "source_text": "ATCSCC ADVZY 001 SIGNATURE 00:01",
        "candidate_facts": [fact],
        "validator_results": [],
        "gold_annotation": {
            "annotation_status": "pending_manual_gold_annotation",
            "annotator_id": "",
            "valid_facts": [],
            "invalid_candidate_fact_ids": [],
            "missing_facts": [],
            "rejected_fact_adjudications": [],
            "notes": "",
        },
    }
    (eval_dir / "atcscc_gold_annotation_template.jsonl").write_text(
        json.dumps(record, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    formal_dir = tmp_path / "data/experiments/nasa_atmonto/formal"
    formal_dir.mkdir(parents=True)
    cross_fact = {
        "fact_id": "S2:fact-1",
        "fact_type": "datatype_property",
        "subject_class": "TrafficManagementInitiative",
        "predicate": "issuedTime",
        "value": "2026-05-14T00:01:00Z",
        "datatype": "xsd:dateTime",
        "evidence_text": "SIGNATURE 00:01",
        "source_id": "SRC1",
    }
    s2_record = {
        "system_id": "S2_llm_schema_slice",
        "sample_id": "ATCSCC-GOLD-001",
        "source_id": "SRC1",
        "source_family": "atcscc_advisories",
        "json_adherence": True,
        "facts": [cross_fact],
        "validator_results": [
            {
                "fact_id": "S2:fact-1",
                "accepted": True,
                "validated_fact": cross_fact,
                "status": "repaired_accepted",
                "errors": [],
            }
        ],
    }
    for filename in (
        "s1_llm_only_predictions.jsonl",
        "s3_llm_schema_slice_validator_repair_predictions.jsonl",
    ):
        (formal_dir / filename).write_text("", encoding="utf-8")
    (formal_dir / "s2_llm_schema_slice_predictions.jsonl").write_text(
        json.dumps(s2_record, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    decision_dir = eval_dir / "review_decisions"
    decision_dir.mkdir()
    decision = {
        "sample_id": "ATCSCC-GOLD-001",
        "source_id": "SRC1",
        "annotation_status": "reviewed",
        "annotator_id": "reviewer-1",
        "valid_candidate_fact_ids": ["fact-1"],
        "valid_cross_system_fact_ids": ["S2:fact-1"],
        "invalid_candidate_fact_ids": [],
        "missing_facts": [],
        "rejected_fact_adjudications": [],
        "notes": "source checked",
    }
    (decision_dir / "batch_01.jsonl").write_text(
        json.dumps(decision, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    output = eval_dir / "reviewed_draft.jsonl"
    report = apply_gold_review_decisions(
        tmp_path,
        decision_dir=decision_dir,
        output_path=output,
    )

    assert report["output_written"] is True
    assert report["validation_status"] == "ready_for_scoring"
    assert report["reviewed_record_count"] == 1
    draft = json.loads(output.read_text(encoding="utf-8").strip())
    assert draft["gold_annotation"]["annotation_status"] == "reviewed"
    assert draft["gold_annotation"]["valid_facts"][0]["fact_id"] == "fact-1"
    assert draft["gold_annotation"]["missing_facts"][0]["fact_id"] == "S2:fact-1"
    assert draft["gold_annotation"]["missing_facts"][0]["source_system_id"] == (
        "S2_llm_schema_slice"
    )


def test_rejection_adjudication_finalizes_property_level_decisions() -> None:
    report = build_rejection_adjudication_report(Path("."))

    assert report["rejected_fact_count"] == 288
    assert report["grouped_fact_count"] == 288
    assert report["property_level_complete"] is True
    assert report["pending_fact_count"] == 0
    assert report["decision_counts_by_fact"] == {
        "extractor_bug": 13,
        "profile_gap": 275,
    }

    by_predicate = {group["predicate"]: group for group in report["groups"]}
    assert by_predicate["extensionProbability"]["final_decision"] == "extractor_bug"
    assert by_predicate["controlledNASelement"]["final_decision"] == "profile_gap"
    assert by_predicate["impactingConditionMessage"]["final_decision"] == "profile_gap"
    assert by_predicate["impactingCondition"]["final_decision"] == "profile_gap"

    markdown = rejection_adjudication_markdown(report)
    assert "## Final Decision Counts By Fact" in markdown
    assert "`extractor_bug`: 13" in markdown
    assert "`profile_gap`: 275" in markdown
    assert "does not automatically approve profile extensions" in markdown
