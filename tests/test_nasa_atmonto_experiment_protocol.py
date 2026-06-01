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
