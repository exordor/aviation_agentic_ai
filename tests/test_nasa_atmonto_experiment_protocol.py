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
    assert all(
        record["gold_annotation"]["annotation_status"] == "pending_manual_gold_annotation"
        for record in records
    )
    assert all(
        record["gold_annotation"]["review_checklist"]
        == {
            "source_text_checked": False,
            "semantic_rubric_checked": False,
            "profile_gap_boundary_checked": False,
            "missing_facts_checked": False,
        }
        for record in records
    )


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
        "100 sampled advisories have reviewed gold annotations",
    ]:
        assert required in protocol


def test_experiment_protocol_matches_current_atmonto_claim_status() -> None:
    protocol = Path("docs/experiment_protocol.md").read_text(encoding="utf-8")

    assert "supported as structural-only evidence" in protocol
    assert "semantic preservation is pending reviewed gold" in protocol
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
    ]:
        assert required in guide
