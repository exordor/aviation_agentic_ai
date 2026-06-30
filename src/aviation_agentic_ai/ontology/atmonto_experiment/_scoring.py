"""AUTO-SPLIT from ontology/atmonto_experiment.py. See git history."""
from __future__ import annotations

from typing import Any
from collections.abc import Iterable
from pathlib import Path

from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.ontology.atmonto_minimal_loop import (
    validate_candidate_payloads,
)

from ._io import (
    file_sha256,
    read_jsonl,
    read_jsonl_lenient,
)
from ._fact_keys import (
    canonical_fact_key,
    fact_key_predicate,
)
from ._system_defs import (
    GOLD_REVIEWED_PATH,
    GOLD_TEMPLATE_PATH,
    SystemDefinition,
)
from ._metrics import (
    accepted_prediction_facts,
    gold_annotation_status,
    gold_fact_keys,
    semantic_metrics,
    structural_metrics,
)
from ._prediction_validation import (
    prediction_json_metrics,
    valid_prediction_records,
)

def prediction_payloads_for_validation(
    records: list[dict[str, Any]],
) -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for record in records:
        facts: list[dict[str, Any]] = []
        for fact in record.get("facts", []):
            if isinstance(fact, dict):
                normalized = dict(fact)
                normalized.setdefault("source_id", record.get("source_id"))
                facts.append(normalized)
        payloads.append(
            {
                "source_id": record["source_id"],
                "source_family": record.get("source_family", "atcscc_advisories"),
                "facts": facts,
            }
        )
    return payloads

def source_rows_for_validation(input_records: list[dict[str, Any]]) -> list[dict[str, object]]:
    return [
        {
            "source_id": record["source_id"],
            "text": record.get("source_text", ""),
        }
        for record in input_records
    ]

def embedded_validator_results(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for record in records:
        for item in record.get("validator_results", []):
            if isinstance(item, dict):
                results.append(item)
    return results

def property_level_semantic_metrics(
    *,
    predictions: list[dict[str, Any]],
    gold_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    gold_keys = gold_fact_keys(gold_records)
    if not gold_keys:
        return []
    prediction_keys = {canonical_fact_key(fact) for fact in predictions}
    predicates = sorted({fact_key_predicate(key) for key in gold_keys | prediction_keys})
    rows: list[dict[str, Any]] = []
    for predicate in predicates:
        gold_for_predicate = {
            key for key in gold_keys if fact_key_predicate(key) == predicate
        }
        pred_for_predicate = {
            key for key in prediction_keys if fact_key_predicate(key) == predicate
        }
        true_positive = pred_for_predicate & gold_for_predicate
        false_positive = pred_for_predicate - gold_for_predicate
        false_negative = gold_for_predicate - pred_for_predicate
        precision = (
            len(true_positive) / len(pred_for_predicate)
            if pred_for_predicate
            else 0.0
        )
        recall = len(true_positive) / len(gold_for_predicate) if gold_for_predicate else 0.0
        f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
        rows.append(
            {
                "predicate": predicate,
                "predicted_fact_count": len(pred_for_predicate),
                "gold_fact_count": len(gold_for_predicate),
                "true_positive_count": len(true_positive),
                "false_positive_count": len(false_positive),
                "false_negative_count": len(false_negative),
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }
        )
    return rows

def semantic_group_semantic_metrics(
    *,
    predictions: list[dict[str, Any]],
    gold_records: list[dict[str, Any]],
    semantic_groups: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    gold_by_source_id = {str(record.get("source_id")): record for record in gold_records}
    for group in semantic_groups.get("groups", []):
        source_ids = {
            str(record.get("source_id"))
            for record in semantic_groups.get("records", [])
            if record.get("semantic_group_id") == group.get("group_id")
        }
        group_gold_records = [
            gold_by_source_id[source_id]
            for source_id in sorted(source_ids)
            if source_id in gold_by_source_id
        ]
        group_predictions = [
            fact for fact in predictions if str(fact.get("source_id")) in source_ids
        ]
        rows.append(
            {
                "group_id": group["group_id"],
                "label": group["label"],
                "record_count": group["record_count"],
                "gold_fact_count": len(gold_fact_keys(group_gold_records)),
                "predicted_fact_count": len(
                    {canonical_fact_key(fact) for fact in group_predictions}
                ),
                "semantic_metrics": semantic_metrics(
                    predictions=group_predictions,
                    gold_records=group_gold_records,
                ),
            }
        )
    return rows

def semantic_scoring_validity(
    *,
    system: SystemDefinition,
    structural: dict[str, Any],
) -> dict[str, Any]:
    if (
        system.system_id == "S1_llm_only"
        and int(structural.get("candidate_fact_count") or 0) > 0
        and int(structural.get("accepted_fact_count") or 0) == 0
        and float(structural.get("schema_violation_rate") or 0.0) >= 0.999
    ):
        return {
            "scoring_validity": "invalid_direct_schema_scoring",
            "valid_for_baseline_comparison": False,
            "interpretation": (
                "The schema-free LLM output is JSON-adherent but all candidate facts "
                "are rejected by the target ATMONTO validator. Direct target-schema "
                "precision/recall/F1 are diagnostic zeros, not a valid semantic baseline. "
                "Use S1_raw_open_llm diagnostics and S1b_llm_canonicalized for future "
                "target-schema semantic comparisons."
            ),
        }
    return {
        "scoring_validity": "valid_target_schema_scoring",
        "valid_for_baseline_comparison": True,
        "interpretation": "Target-schema precision/recall/F1 are interpretable for this system.",
    }

def source_family_methodology_boundaries(repo_root: Path) -> dict[str, Any]:
    return {
        "status": "methodology_remediation",
        "scope_statement": (
            "The current scored run is a narrow FAA ATCSCC advisory / NASA ATMONTO "
            "ATCSCC schema-slice experiment. PDF reference documents are added only as "
            "a second source-family design for the next rerun; PDF definition/procedure "
            "metrics must not be mixed into the ATCSCC event F1 table."
        ),
        "source_families": [
            {
                "id": "A",
                "source_family": "faa_atcscc_advisories",
                "data_shape": "semi_structured_short_advisories",
                "task": "TMI/event ABox extraction",
                "preferred_system_design": (
                    "S0 deterministic backbone plus S3 semantic enrichment and validator gate"
                ),
                "current_gold": "100 reviewed advisories from 2026-05-14 through 2026-05-20",
            },
            {
                "id": "B",
                "source_family": "faa_nasa_pdf_reference_documents",
                "data_shape": "unstructured_or_long_form_reference_text",
                "task": (
                    "definition, terminology, procedure, and source-mapping evidence extraction"
                ),
                "candidate_documents": [
                    project_relative_path(
                        repo_root
                        / "data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/"
                        "PCG_Bsc_w_Chg_1_and_2_dtd_1-22-26.pdf",
                        repo_root,
                    ),
                    project_relative_path(
                        repo_root
                        / "data/raw/nasa_atmonto/2026-06-01/faa_reference_documents/"
                        "7110.65BB_Bsc_w_Chg_1_and_2_dtd_1-22-26_Final.pdf",
                        repo_root,
                    ),
                    project_relative_path(
                        repo_root
                        / "data/papers/ntrs_ontology_selection/"
                        "20170006095_nasa_air_traffic_management_ontology.pdf",
                        repo_root,
                    ),
                ],
                "allowed_predicates": [
                    "term_has_definition",
                    "term_has_alias",
                    "procedure_mentions_concept",
                    "document_defines_or_constrains",
                    "source_supports_mapping",
                ],
                "required_provenance_fields": [
                    "document_id",
                    "page",
                    "section",
                    "span",
                    "evidence_text",
                ],
                "backend_policy": {
                    "candidate_default": "hybrid_docling_pymupdf",
                    "legacy_baseline": "pymupdf_text_legacy",
                    "policy_reports": [
                        "reports/stages/pdf_extraction_comparison.md",
                        "reports/stages/pdf_backend_chunking_comparison.md",
                    ],
                },
            },
        ],
        "cross_source_metric_policy": (
            "Compare structural conformance, evidence grounding, and canonicalization yield "
            "across source families. Report semantic F1 within each task family only."
        ),
    }

def consensus_sota_remediation_constraints() -> dict[str, Any]:
    from ._extraction import HYBRID_SEMANTIC_ENRICHMENT_PREDICATES
    return {
        "status": "rerun_design_constraint",
        "scope_boundary": (
            "These constraints refine the narrow ATCSCC / ATMONTO rerun. They are "
            "not a pivot to a general aviation KG or an end-to-end GraphRAG claim."
        ),
        "s1_interpretation": {
            "current_system": "S1_llm_only",
            "current_label": "invalid_direct_schema_scoring",
            "future_raw_system": "S1_raw_open_llm",
            "future_comparable_system": "S1b_llm_canonicalized",
            "rule": (
                "Report raw S1 coverage, JSON adherence, and evidence containment only. "
                "Compute target-schema precision/recall/F1 only after canonicalization."
            ),
        },
        "nine_stage_pipeline": [
            "ATCSCC parsing",
            "S0 deterministic backbone",
            "schema-slice retrieval",
            "LLM semantic extraction",
            "canonicalization",
            "validator gate",
            "repair with trace",
            "graph materialization",
            "layered evaluation",
        ],
        "sota_adaptations": [
            {
                "anchor": "Extract-Define-Canonicalize",
                "implementation": "Split open extraction from target-schema canonicalization.",
                "claim_guardrail": "Do not score raw open LLM output with ATMONTO P/R/F1.",
            },
            {
                "anchor": "ontology_guided_domain_short_text_kgc",
                "implementation": (
                    "Use 10-20 reviewed dev examples for S2/S3 by advisory type and "
                    "predicate family."
                ),
                "claim_guardrail": "Do not draw examples from the held-out 100 scoring records.",
            },
            {
                "anchor": "llm_as_kg_support_module",
                "implementation": (
                    "Use LLMs as canonicalizer, semantic enrichment module, evidence checker, "
                    "and profile-gap explainer."
                ),
                "claim_guardrail": "Do not make pure LLM extraction the primary thesis system.",
            },
            {
                "anchor": "production_ontology_guided_pipeline",
                "implementation": (
                    "Combine pattern/rule extraction, ontology-guided prompting, grounding, "
                    "corroboration, and validator gating."
                ),
                "claim_guardrail": "Quarantine conflicts, unsupported spans, and rejected repairs.",
            },
            {
                "anchor": "source_family_separation",
                "implementation": (
                    "Keep ATCSCC event extraction and PDF reference extraction in separate "
                    "metric tables."
                ),
                "claim_guardrail": "Do not compare PDF definition F1 with ATCSCC event F1.",
            },
            {
                "anchor": "graph_rag_layered_evaluation",
                "implementation": (
                    "Report KG construction, graph retrieval, and answer generation metrics "
                    "as separate layers."
                ),
                "claim_guardrail": (
                    "Current remediation supports KG construction metrics only; no "
                    "end-to-end GraphRAG answer improvement claim."
                ),
            },
        ],
        "s4_merge_policy": {
            "primary_candidate_system": "S4_hybrid_backbone_enrichment",
            "s0_owns": [
                "advisoryNumber",
                "issuedTime",
                "effectiveStartTime",
                "effectiveEndTime",
                "header/template fields",
            ],
            "s3_s4_may_add_not_overwrite": sorted(HYBRID_SEMANTIC_ENRICHMENT_PREDICATES),
            "quarantine_conditions": [
                "conflict",
                "unsupported span",
                "fuzzy-only mapping",
                "validator rejected fact",
                "repair-only fact with semantic-change flag",
            ],
        },
        "planned_artifacts": [
            {
                "path": "schema/atcscc_tmi_profile.yaml",
                "required_fields": [
                    "class",
                    "predicate_uri",
                    "label",
                    "aliases",
                    "domain",
                    "range",
                    "cardinality",
                    "allowed_enum",
                    "normalizer",
                    "validator_rule",
                    "example_spans",
                    "profile_version",
                    "source_doc",
                    "commit_hash",
                ],
            },
            {"component": "predicate canonicalizer"},
            {"component": "enum canonicalizer"},
            {"component": "entity canonicalizer"},
            {"component": "time normalizer"},
            {
                "component": "repair trace",
                "fields": [
                    "pre_error",
                    "repair_action",
                    "post_validation_status",
                    "semantic_change_flag",
                    "evidence_status",
                ],
            },
            {
                "component": "error taxonomy",
                "categories": [
                    "format error",
                    "predicate drift",
                    "class/domain error",
                    "range error",
                    "enum error",
                    "entity canonicalization error",
                    "unsupported span",
                    "temporal normalization error",
                    "duplicate/merge error",
                ],
            },
        ],
        "unverified_search_leads": {
            "status": "requiring verification",
            "rule": "Do not cite these as formal evidence until fetched and checked directly.",
            "items": [
                "OntoLogX",
                "JSON-Schema-guided information extraction",
                "Graphusion",
                "RAKG",
                "RAGAS",
                "STaRK",
                "Microsoft GraphRAG",
            ],
        },
    }

def formal_scoring_gold_source(repo_root: Path, selected_ids: set[str]) -> dict[str, Any]:
    from ._gold_validation import validate_gold_annotation_records
    reviewed_path = repo_root / GOLD_REVIEWED_PATH
    template_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    template_validation = validate_gold_annotation_records(
        gold_records=template_records,
        selected_source_ids=selected_ids,
    )
    if not reviewed_path.exists():
        return {
            "source": "frozen_reviewed_gold_missing",
            "path": project_relative_path(reviewed_path, repo_root),
            "exists": False,
            "sha256": None,
            "records": [],
            "gold_status": gold_annotation_status([]),
            "template_validation_status": template_validation["status"],
            "template_reviewed_record_count": template_validation["reviewed_record_count"],
            "template_pending_record_count": template_validation["pending_record_count"],
            "ready_for_formal_scoring": False,
        }

    reviewed_records = read_jsonl(reviewed_path)
    reviewed_validation = validate_gold_annotation_records(
        gold_records=reviewed_records,
        selected_source_ids=selected_ids,
    )
    ready = reviewed_validation["status"] == "ready_for_scoring"
    return {
        "source": "frozen_reviewed_gold",
        "path": project_relative_path(reviewed_path, repo_root),
        "exists": True,
        "sha256": file_sha256(reviewed_path),
        "records": reviewed_records,
        "gold_status": gold_annotation_status(reviewed_records),
        "validation_status": reviewed_validation["status"],
        "error_count": reviewed_validation["error_count"],
        "warning_count": reviewed_validation["warning_count"],
        "template_validation_status": template_validation["status"],
        "template_reviewed_record_count": template_validation["reviewed_record_count"],
        "template_pending_record_count": template_validation["pending_record_count"],
        "ready_for_formal_scoring": ready,
    }

def score_system_predictions(
    *,
    system: SystemDefinition,
    repo_root: Path,
    selected_ids: set[str],
    input_records: list[dict[str, Any]],
    gold_records: list[dict[str, Any]],
    schema_slice: dict[str, Any],
    semantic_groups: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output_path = repo_root / system.expected_output
    parse_result = read_jsonl_lenient(output_path)
    base = {
        "system_id": system.system_id,
        "label": system.label,
        "expected_output": project_relative_path(output_path, repo_root),
        "output_exists": parse_result["exists"],
    }
    if not parse_result["exists"]:
        return {
            **base,
            "available": False,
            "reason": "prediction_output_missing",
            "json_metrics": None,
            "structural_metrics": None,
            "semantic_metrics": None,
            "property_level_semantic_metrics": [],
            "semantic_group_metrics": [],
        }

    json_metrics = prediction_json_metrics(parse_result=parse_result, selected_ids=selected_ids)
    records = valid_prediction_records(parse_result, selected_ids)
    validation_results = embedded_validator_results(records)
    if not validation_results:
        validation_results = validate_candidate_payloads(
            prediction_payloads_for_validation(records),
            source_rows_for_validation(input_records),
            schema_slice,
        )
    prediction_facts = accepted_prediction_facts(validation_results)
    semantic = semantic_metrics(predictions=prediction_facts, gold_records=gold_records)
    structural = structural_metrics(
        validation_results,
        repair_applicable=system.uses_validator_repair,
    )
    semantic.update(
        semantic_scoring_validity(
            system=system,
            structural=structural,
        )
    )
    return {
        **base,
        "available": True,
        "reason": None,
        "json_metrics": json_metrics,
        "structural_metrics": structural,
        "semantic_metrics": semantic,
        "property_level_semantic_metrics": (
            property_level_semantic_metrics(
                predictions=prediction_facts,
                gold_records=gold_records,
            )
            if semantic["available"]
            else []
        ),
        "semantic_group_metrics": (
            semantic_group_semantic_metrics(
                predictions=prediction_facts,
                gold_records=gold_records,
                semantic_groups=semantic_groups,
            )
            if semantic["available"] and semantic_groups
            else []
        ),
    }

def system_score_by_id(system_scores: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(score["system_id"]): score for score in system_scores}

def nested_metric(score: dict[str, Any], group: str, key: str) -> Any:
    metrics = score.get(group)
    if not isinstance(metrics, dict):
        return None
    return metrics.get(key)

def property_metric_value(score: dict[str, Any], predicate: str, metric: str) -> float | None:
    for row in score.get("property_level_semantic_metrics", []):
        if row.get("predicate") == predicate and isinstance(row.get(metric), (int, float)):
            return float(row[metric])
    return None

def macro_property_metric(
    score: dict[str, Any],
    predicates: Iterable[str],
    metric: str,
) -> float | None:
    values = [
        value
        for predicate in predicates
        if (value := property_metric_value(score, predicate, metric)) is not None
    ]
    return sum(values) / len(values) if values else None

def metric_value_text(value: Any) -> str:
    return "n/a" if value is None else str(value)

def metric_interval_text(interval: dict[str, Any] | None) -> str:
    if interval is None:
        return "n/a"
    if not interval:
        return "n/a (empty)"
    return f"{metric_value_text(interval.get('low'))} - {metric_value_text(interval.get('high'))}"
