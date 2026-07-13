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
    assert sum(len(record["gold_annotation"]["valid_facts"]) for record in records) == 470
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
    protocol = Path("EXPERIMENTS.md").read_text(encoding="utf-8")

    for required in [
        "pilot / feasibility study",
        "Source Families",
        "faa_atcscc_advisories",
        "faa_nasa_pdf_reference_documents",
        "hybrid_docling_pymupdf",
        "pymupdf_text_legacy",
        "term_has_definition",
        "procedure_mentions_concept",
        "SOTA-Informed Adaptation For The Rerun",
        "Extract-Define-Canonicalize",
        "reviewed_dev_examples",
        "held-out 100 scoring records",
        "canonicalizers",
        "evidence checkers",
        "profile-gap explainers",
        "nine-stage pipeline",
        "ATCSCC parsing",
        "schema/atcscc_tmi_profile.yaml",
        "predicate_uri",
        "repair-induced false positive",
        "format error",
        "predicate drift",
        "entity canonicalization error",
        "fuzzy-only mappings",
        "repair-only facts",
        "log/review/quarantine",
        "GraphRAG evaluation remains layered",
        "end-to-end GraphRAG answer improvement",
        "requiring verification",
        "JSON-Schema-guided information extraction",
        "Deterministic Rule Baseline",
        "Raw Schema-Free LLM Diagnostic",
        "Schema-Guided LLM Extraction",
        "Schema-Guided LLM With Validator And Repair",
        "Hybrid Backbone Plus Semantic Enrichment",
        "Baselines And Comparators",
        "Deterministic rules",
        "Raw schema-free LLM",
        "Canonicalized schema-free extraction",
        "Hybrid backbone enrichment",
        "invalid_direct_schema_scoring",
        "JSON Adherence",
        "Schema Violation Rate",
        "Triple Precision, Recall, And F1",
        "Canonicalization Yield",
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
    protocol = Path("EXPERIMENTS.md").read_text(encoding="utf-8")

    assert "supported on the corrected stage" in protocol
    assert "six named extraction" in protocol
    assert "supported on the reviewed 100-record sample" in protocol
    assert "Semantic Stratification" in protocol
    assert "data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl" in protocol
    assert "all 288 pilot rejections" in protocol
    assert "13 `extractor_bug` facts" in protocol
    assert "275 `profile_gap`" in protocol
    assert "final adjudication is pending manual review" not in protocol
    assert "Current status: not yet tested." not in protocol


def test_experiment_protocol_repair_metric_boundary_matches_validator_loop() -> None:
    protocol = Path("EXPERIMENTS.md").read_text(encoding="utf-8")

    assert "enter the validator/repair loop as initially invalid" in protocol
    assert "initially invalid schema-guided facts" not in protocol
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
