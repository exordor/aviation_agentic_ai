from __future__ import annotations

import json
from pathlib import Path


def test_nasa_atmonto_gold_sample_manifest_and_template_are_consistent() -> None:
    manifest_path = Path("data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json")
    template_path = Path("data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = [
        json.loads(line)
        for line in template_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert manifest["sample_status"] == "sample_template_created_gold_labels_pending"
    assert 80 <= manifest["sample_size"] <= 120
    assert manifest["sample_size"] == len(records)
    assert len(manifest["selected_source_ids"]) == len(records)
    assert {record["source_id"] for record in records} == set(manifest["selected_source_ids"])
    assert all(record["gold_annotation"]["annotation_status"] == "reviewed" for record in records)
    assert all(
        record["gold_annotation"]["review_checklist"]
        == {
            "source_text_checked": True,
            "semantic_rubric_checked": True,
            "profile_gap_boundary_checked": True,
            "missing_facts_checked": True,
        }
        for record in records
    )
    assert sum(len(record["gold_annotation"]["valid_facts"]) for record in records) == 462
    assert sum(len(record["gold_annotation"]["missing_facts"]) for record in records) == 181


def test_nasa_atmonto_rejection_analysis_covers_all_rejected_facts() -> None:
    report = json.loads(
        Path("reports/stages/nasa_atmonto_rejection_error_analysis.json").read_text(
            encoding="utf-8"
        )
    )

    group_total = sum(group["count"] for group in report["groups"])
    decision_total = sum(report["decision_counts_by_fact"].values())

    assert report["rejected_fact_count"] == 288
    assert report["rejected_fact_count"] == group_total == decision_total
    assert report["group_count"] == len(report["groups"])
    assert {
        "extractor_normalization_bug_candidate",
        "nasa_atmonto_profile_gap_candidate",
    }.issubset(report["decision_counts_by_fact"])


def test_experiment_protocol_fixes_systems_metrics_and_falsification_criteria() -> None:
    protocol = Path("docs/experiment_protocol.md").read_text(encoding="utf-8")

    for required in [
        "pilot / feasibility study",
        "S0: Rule-Only",
        "S1: LLM-Only",
        "S2: LLM + Schema Slice",
        "S3: LLM + Schema Slice + Validator/Repair",
        "Baselines And Comparators",
        "S0 rule-only",
        "S1 LLM-only",
        "JSON Adherence",
        "Schema Violation Rate",
        "Triple Precision, Recall, And F1",
        "Repair Success Rate",
        "Manual Semantic Correctness",
        "Falsified if",
        "reports/stages/nasa_atmonto_gold_review_session_plan.md",
        "reports/stages/nasa_atmonto_gold_review_multiround_audit.md",
        "prepare_nasa_atmonto_gold_review_session_plan.py",
        "100 sampled advisories have reviewed gold annotations",
        "Assisted Gold Adjudication Workflow",
        "Adversarial ontology/profile review",
        "Gold truth is not created by model agreement alone",
        "multi-round and multi-perspective",
        "extensionProbability:MODERATE->MEDIUM",
        "raw_value",
        "value_normalization",
    ]:
        assert required in protocol


def test_experiment_protocol_matches_current_atmonto_claim_status() -> None:
    protocol = Path("docs/experiment_protocol.md").read_text(encoding="utf-8")

    assert "supported by the formal scoring report" in protocol
    assert "supported on the reviewed 100-record sample" in protocol
    assert "Semantic Stratification" in protocol
    assert "data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl" in protocol
    assert "all 288 pilot rejections" in protocol
    assert "13 `extractor_bug` facts" in protocol
    assert "275 `profile_gap`" in protocol
    assert "final adjudication is pending manual review" not in protocol
    assert "Current status: not yet tested." not in protocol


def test_experiment_protocol_repair_metric_boundary_matches_s3_loop() -> None:
    protocol = Path("docs/experiment_protocol.md").read_text(encoding="utf-8")

    assert "enter the S3 validator/repair loop as initially invalid" in protocol
    assert "initially invalid S2 facts" not in protocol
    assert "must be created by running the LLM prediction runner" not in protocol
    assert "must not be fabricated or manually filled" in protocol
    assert "100 usable records before scoring" in protocol
    assert "`session_01` covers 4 records" in protocol
    assert "review queue only" in protocol


def test_gold_annotation_guide_defines_manual_semantic_rubric() -> None:
    guide = Path("docs/nasa_atmonto_gold_annotation_guide.md").read_text(
        encoding="utf-8"
    )

    for required in [
        "Semantic Correctness Rubric",
        "predicate",
        "subject_class",
        "object_class",
        "evidence_text",
        "True positive",
        "False positive",
        "False negative",
        "Profile-gap candidate",
        "review_checklist",
        "semantic_rubric_checked",
        "keep the record pending",
        "Assisted Review Roles",
        "Primary model screening",
        "Source-evidence audit",
        "Adversarial ontology/profile audit",
        "User adjudication",
        "none of them is gold truth by itself",
        "Reviewed Normalization Policy",
        "extensionProbability",
        "MODERATE",
        "MEDIUM",
        "reviewed_enum_mapping_moderate_to_medium",
        "normalization_policy",
    ]:
        assert required in guide
