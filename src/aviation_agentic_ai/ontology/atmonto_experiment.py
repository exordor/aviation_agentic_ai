from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha1
import json
from pathlib import Path
import sys
from typing import Any, Callable

from aviation_agentic_ai.llm.providers import configured_llm_model, configured_llm_provider, get_llm
from aviation_agentic_ai.ontology.atmonto_minimal_loop import validate_candidate_payloads
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.utils.json_extraction import (
    JSONPayloadExtractionError,
    extract_json_object,
)


GOLD_MANIFEST_PATH = Path("data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json")
GOLD_TEMPLATE_PATH = Path("data/evaluation/nasa_atmonto/atcscc_gold_annotation_template.jsonl")
GOLD_REVIEW_WORKLIST_JSON = Path("data/evaluation/nasa_atmonto/atcscc_gold_review_worklist.json")
GOLD_REVIEW_WORKLIST_MD = Path("data/evaluation/nasa_atmonto/atcscc_gold_review_worklist.md")
REJECTION_ANALYSIS_JSON = Path("reports/stages/nasa_atmonto_rejection_error_analysis.json")
SCHEMA_SLICE_PATH = Path("data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json")
EXTRACTION_SCHEMA_PATH = Path(
    "data/ontology/curated/nasa_atmonto_atcscc_extraction_schema.json"
)
S0_CANDIDATES_PATH = Path(
    "data/processed/nasa_atmonto/extraction/2026-05-14/atcscc_schema_slice_candidates.jsonl"
)
S0_VALIDATED_PATH = Path(
    "data/processed/nasa_atmonto/extraction/2026-05-14/atcscc_schema_slice_validated.jsonl"
)
FORMAL_OUTPUT_DIR = Path("data/experiments/nasa_atmonto/formal")
FORMAL_INPUT_RECORDS_PATH = FORMAL_OUTPUT_DIR / "input_records.jsonl"
FORMAL_SYSTEM_SPECS_PATH = FORMAL_OUTPUT_DIR / "system_specs.json"
S1_PROMPT_BATCH_PATH = FORMAL_OUTPUT_DIR / "s1_llm_only_prompt_batch.jsonl"
S2_PROMPT_BATCH_PATH = FORMAL_OUTPUT_DIR / "s2_llm_schema_slice_prompt_batch.jsonl"
S3_PROMPT_BATCH_PATH = FORMAL_OUTPUT_DIR / "s3_llm_schema_slice_validator_repair_prompt_batch.jsonl"
READINESS_REPORT_JSON = Path("reports/stages/nasa_atmonto_formal_experiment_readiness.json")
READINESS_REPORT_MD = Path("reports/stages/nasa_atmonto_formal_experiment_readiness.md")
SCORING_REPORT_JSON = Path("reports/stages/nasa_atmonto_formal_experiment_scoring.json")
SCORING_REPORT_MD = Path("reports/stages/nasa_atmonto_formal_experiment_scoring.md")
GOLD_VALIDATION_REPORT_JSON = Path(
    "reports/stages/nasa_atmonto_gold_annotation_validation.json"
)
GOLD_VALIDATION_REPORT_MD = Path(
    "reports/stages/nasa_atmonto_gold_annotation_validation.md"
)
PREDICTION_OUTPUT_VALIDATION_REPORT_JSON = Path(
    "reports/stages/nasa_atmonto_prediction_output_validation.json"
)
PREDICTION_OUTPUT_VALIDATION_REPORT_MD = Path(
    "reports/stages/nasa_atmonto_prediction_output_validation.md"
)

REVIEWED_GOLD_STATUS = "reviewed"
PENDING_GOLD_STATUS = "pending_manual_gold_annotation"
ALLOWED_REJECTION_ADJUDICATIONS = {
    "extractor_bug",
    "profile_gap",
    "source_ambiguity",
    "manual_review_only",
}


@dataclass(frozen=True)
class SystemDefinition:
    system_id: str
    label: str
    description: str
    expected_output: Path
    prompt_batch: Path | None
    requires_llm: bool
    uses_schema_slice: bool
    uses_validator_repair: bool


SYSTEMS: tuple[SystemDefinition, ...] = (
    SystemDefinition(
        system_id="S0_rule_only",
        label="Rule-only",
        description="Deterministic ATCSCC surface-pattern extractor used by the pilot.",
        expected_output=FORMAL_OUTPUT_DIR / "s0_rule_only_predictions.jsonl",
        prompt_batch=None,
        requires_llm=False,
        uses_schema_slice=True,
        uses_validator_repair=False,
    ),
    SystemDefinition(
        system_id="S1_llm_only",
        label="LLM-only",
        description="LLM extractor without NASA ATMONTO schema terms in the prompt.",
        expected_output=FORMAL_OUTPUT_DIR / "s1_llm_only_predictions.jsonl",
        prompt_batch=S1_PROMPT_BATCH_PATH,
        requires_llm=True,
        uses_schema_slice=False,
        uses_validator_repair=False,
    ),
    SystemDefinition(
        system_id="S2_llm_schema_slice",
        label="LLM + schema slice",
        description="LLM extractor constrained by the ATCSCC schema slice and JSON shape.",
        expected_output=FORMAL_OUTPUT_DIR / "s2_llm_schema_slice_predictions.jsonl",
        prompt_batch=S2_PROMPT_BATCH_PATH,
        requires_llm=True,
        uses_schema_slice=True,
        uses_validator_repair=False,
    ),
    SystemDefinition(
        system_id="S3_llm_schema_slice_validator_repair",
        label="LLM + schema slice + validator/repair",
        description="S2 with custom validation and one repair attempt for invalid payloads.",
        expected_output=FORMAL_OUTPUT_DIR
        / "s3_llm_schema_slice_validator_repair_predictions.jsonl",
        prompt_batch=S3_PROMPT_BATCH_PATH,
        requires_llm=True,
        uses_schema_slice=True,
        uses_validator_repair=True,
    ),
)

LLM_RUN_SYSTEM_IDS = {system.system_id for system in SYSTEMS if system.requires_llm}
LLMInvoker = Callable[[list[dict[str, str]]], str]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    payload = "\n".join(json.dumps(record, sort_keys=True, ensure_ascii=False) for record in records)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload + ("\n" if payload else ""), encoding="utf-8")


def compact_text(value: object) -> str:
    return " ".join(str(value or "").split())


def term_name(value: object) -> str:
    text = str(value or "")
    if "#" in text:
        return text.rsplit("#", 1)[-1]
    if "/" in text and text.startswith(("http://", "https://", "urn:")):
        return text.rstrip("/").rsplit("/", 1)[-1]
    if ":" in text and not text.startswith(("http://", "https://", "urn:")):
        return text.rsplit(":", 1)[-1]
    return text


def canonical_fact_key(fact: dict[str, Any]) -> tuple[str, str, str, str, str, str]:
    value = fact.get("object") if fact.get("fact_type") == "object_property" else fact.get("value")
    return (
        term_name(fact.get("subject_class")),
        term_name(fact.get("predicate")),
        compact_text(value).lower(),
        term_name(fact.get("object_class")),
        term_name(fact.get("datatype")),
        compact_text(fact.get("evidence_text")).lower(),
    )


def system_definitions(repo_root: Path) -> list[dict[str, Any]]:
    return [
        {
            "system_id": system.system_id,
            "label": system.label,
            "description": system.description,
            "expected_output": project_relative_path(repo_root / system.expected_output, repo_root),
            "prompt_batch": (
                project_relative_path(repo_root / system.prompt_batch, repo_root)
                if system.prompt_batch
                else None
            ),
            "run_metadata": project_relative_path(
                repo_root / system_run_metadata_path(system),
                repo_root,
            ),
            "requires_llm": system.requires_llm,
            "uses_schema_slice": system.uses_schema_slice,
            "uses_validator_repair": system.uses_validator_repair,
        }
        for system in SYSTEMS
    ]


def system_output_stem(system: SystemDefinition) -> str:
    return system.expected_output.name.removesuffix("_predictions.jsonl")


def system_run_metadata_path(system: SystemDefinition) -> Path:
    return FORMAL_OUTPUT_DIR / f"{system_output_stem(system)}_run_metadata.json"


def gold_annotation_status(gold_records: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = Counter(
        str(record.get("gold_annotation", {}).get("annotation_status", "missing_status"))
        for record in gold_records
    )
    reviewed = statuses.get(REVIEWED_GOLD_STATUS, 0)
    pending = len(gold_records) - reviewed
    completed = reviewed == len(gold_records) and bool(gold_records)
    valid_fact_count = sum(
        len(record.get("gold_annotation", {}).get("valid_facts", []))
        for record in gold_records
    )
    missing_fact_count = sum(
        len(record.get("gold_annotation", {}).get("missing_facts", []))
        for record in gold_records
    )
    return {
        "record_count": len(gold_records),
        "status_counts": dict(sorted(statuses.items())),
        "reviewed_record_count": reviewed,
        "pending_record_count": pending,
        "valid_fact_count": valid_fact_count,
        "missing_fact_count": missing_fact_count,
        "complete": completed,
    }


def gold_fact_keys(gold_records: list[dict[str, Any]]) -> set[tuple[str, str, str, str, str, str]]:
    keys: set[tuple[str, str, str, str, str, str]] = set()
    for record in gold_records:
        for fact in record.get("gold_annotation", {}).get("valid_facts", []):
            if isinstance(fact, dict):
                keys.add(canonical_fact_key(fact))
        for fact in record.get("gold_annotation", {}).get("missing_facts", []):
            if isinstance(fact, dict):
                keys.add(canonical_fact_key(fact))
    return keys


def accepted_prediction_facts(
    validations: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    for item in validations:
        if item.get("accepted") and isinstance(item.get("validated_fact"), dict):
            facts.append(item["validated_fact"])
    return facts


def structural_metrics(validations: list[dict[str, Any]]) -> dict[str, Any]:
    candidate_count = len(validations)
    rejected = [item for item in validations if not item.get("accepted")]
    accepted = [item for item in validations if item.get("accepted")]
    repaired = [item for item in accepted if item.get("repairs")]
    initially_invalid = len(repaired) + len(rejected)
    return {
        "candidate_fact_count": candidate_count,
        "accepted_fact_count": len(accepted),
        "rejected_fact_count": len(rejected),
        "schema_violation_rate": (len(rejected) / candidate_count) if candidate_count else None,
        "repair_success_rate": (len(repaired) / initially_invalid) if initially_invalid else None,
        "status_counts": dict(sorted(Counter(str(item.get("status")) for item in validations).items())),
        "error_counts": dict(
            sorted(
                Counter(
                    str(error)
                    for item in validations
                    for error in item.get("errors", [])
                ).items()
            )
        ),
    }


def json_adherence_from_payloads(payloads: list[dict[str, Any]], selected_ids: set[str]) -> dict[str, Any]:
    attempted = len(selected_ids)
    valid = sum(1 for payload in payloads if str(payload.get("source_id")) in selected_ids)
    return {
        "attempted_record_count": attempted,
        "valid_json_payload_count": valid,
        "json_adherence": (valid / attempted) if attempted else None,
    }


def semantic_metrics(
    *,
    predictions: list[dict[str, Any]],
    gold_records: list[dict[str, Any]],
) -> dict[str, Any]:
    gold_keys = gold_fact_keys(gold_records)
    if not gold_keys:
        return {
            "available": False,
            "reason": "manual_gold_facts_missing",
            "precision": None,
            "recall": None,
            "f1": None,
            "manual_semantic_correctness": None,
        }
    prediction_keys = {canonical_fact_key(fact) for fact in predictions}
    true_positive = prediction_keys & gold_keys
    false_positive = prediction_keys - gold_keys
    false_negative = gold_keys - prediction_keys
    precision = len(true_positive) / len(prediction_keys) if prediction_keys else 0.0
    recall = len(true_positive) / len(gold_keys) if gold_keys else 0.0
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        "available": True,
        "predicted_fact_count": len(prediction_keys),
        "gold_fact_count": len(gold_keys),
        "true_positive_count": len(true_positive),
        "false_positive_count": len(false_positive),
        "false_negative_count": len(false_negative),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "manual_semantic_correctness": precision,
    }


def evidence_in_source(evidence_text: object, source_text: object) -> bool:
    evidence = str(evidence_text or "")
    source = str(source_text or "")
    if not evidence:
        return False
    if evidence in source:
        return True
    return compact_text(evidence) in compact_text(source)


def fact_has_object_or_value(fact: dict[str, Any]) -> bool:
    if fact.get("fact_type") == "object_property":
        return any(fact.get(key) not in (None, "") for key in ("object", "object_id"))
    if fact.get("fact_type") == "datatype_property":
        return "value" in fact and fact.get("datatype") not in (None, "")
    return False


def validate_gold_fact(
    *,
    fact: dict[str, Any],
    record: dict[str, Any],
    fact_path: str,
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for field in ("fact_type", "subject_class", "predicate", "evidence_text"):
        if fact.get(field) in (None, ""):
            errors.append(
                {
                    "sample_id": record.get("sample_id"),
                    "source_id": record.get("source_id"),
                    "path": fact_path,
                    "error": f"missing_{field}",
                }
            )
    if fact.get("fact_type") not in {"object_property", "datatype_property"}:
        errors.append(
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "path": fact_path,
                "error": "invalid_fact_type",
            }
        )
    if not fact_has_object_or_value(fact):
        errors.append(
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "path": fact_path,
                "error": "missing_object_or_value",
            }
        )
    if fact.get("source_id") and str(fact.get("source_id")) != str(record.get("source_id")):
        errors.append(
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "path": fact_path,
                "error": "fact_source_id_mismatch",
            }
        )
    if not evidence_in_source(fact.get("evidence_text"), record.get("source_text")):
        errors.append(
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "path": fact_path,
                "error": "evidence_not_found_in_source_text",
            }
        )
    return errors


def rejected_fact_ids(record: dict[str, Any]) -> set[str]:
    return {
        str(item.get("fact_id"))
        for item in record.get("validator_results", [])
        if isinstance(item, dict) and item.get("accepted") is False and item.get("fact_id")
    }


def validate_rejection_adjudications(record: dict[str, Any]) -> list[dict[str, Any]]:
    annotation = record.get("gold_annotation", {})
    adjudications = annotation.get("rejected_fact_adjudications", [])
    errors: list[dict[str, Any]] = []
    if not isinstance(adjudications, list):
        return [
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "path": "gold_annotation.rejected_fact_adjudications",
                "error": "not_a_list",
            }
        ]

    rejected_ids = rejected_fact_ids(record)
    by_fact_id = {
        str(item.get("fact_id")): item
        for item in adjudications
        if isinstance(item, dict) and item.get("fact_id")
    }
    if rejected_ids and set(by_fact_id) != rejected_ids:
        errors.append(
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "path": "gold_annotation.rejected_fact_adjudications",
                "error": "rejected_fact_adjudication_ids_do_not_match_validator_rejections",
                "expected_fact_ids": sorted(rejected_ids),
                "actual_fact_ids": sorted(by_fact_id),
            }
        )
    for fact_id, adjudication in by_fact_id.items():
        decision = str(adjudication.get("decision", ""))
        if decision not in ALLOWED_REJECTION_ADJUDICATIONS:
            errors.append(
                {
                    "sample_id": record.get("sample_id"),
                    "source_id": record.get("source_id"),
                    "path": f"gold_annotation.rejected_fact_adjudications[{fact_id}].decision",
                    "error": "invalid_rejection_adjudication_decision",
                    "allowed_values": sorted(ALLOWED_REJECTION_ADJUDICATIONS),
                }
            )
        for field in ("rationale", "recommended_action"):
            if not adjudication.get(field):
                errors.append(
                    {
                        "sample_id": record.get("sample_id"),
                        "source_id": record.get("source_id"),
                        "path": f"gold_annotation.rejected_fact_adjudications[{fact_id}].{field}",
                        "error": f"missing_{field}",
                    }
                )
    return errors


def validate_gold_annotation_records(
    *,
    gold_records: list[dict[str, Any]],
    selected_source_ids: set[str],
) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    source_ids = [str(record.get("source_id")) for record in gold_records]
    source_counter = Counter(source_ids)
    duplicate_source_ids = sorted(source_id for source_id, count in source_counter.items() if count > 1)
    missing_source_ids = sorted(selected_source_ids - set(source_ids))
    unexpected_source_ids = sorted(set(source_ids) - selected_source_ids)

    if duplicate_source_ids:
        errors.append({"error": "duplicate_source_ids", "source_ids": duplicate_source_ids})
    if missing_source_ids:
        errors.append({"error": "missing_selected_source_ids", "source_ids": missing_source_ids})
    if unexpected_source_ids:
        errors.append({"error": "unexpected_source_ids", "source_ids": unexpected_source_ids})

    for record in gold_records:
        annotation = record.get("gold_annotation")
        if not isinstance(annotation, dict):
            errors.append(
                {
                    "sample_id": record.get("sample_id"),
                    "source_id": record.get("source_id"),
                    "path": "gold_annotation",
                    "error": "missing_gold_annotation",
                }
            )
            continue
        status = str(annotation.get("annotation_status", ""))
        if status == PENDING_GOLD_STATUS:
            warnings.append(
                {
                    "sample_id": record.get("sample_id"),
                    "source_id": record.get("source_id"),
                    "warning": "pending_manual_gold_annotation",
                }
            )
            continue
        if status != REVIEWED_GOLD_STATUS:
            errors.append(
                {
                    "sample_id": record.get("sample_id"),
                    "source_id": record.get("source_id"),
                    "path": "gold_annotation.annotation_status",
                    "error": "invalid_annotation_status",
                    "allowed_values": [PENDING_GOLD_STATUS, REVIEWED_GOLD_STATUS],
                }
            )
            continue
        if not annotation.get("annotator_id"):
            errors.append(
                {
                    "sample_id": record.get("sample_id"),
                    "source_id": record.get("source_id"),
                    "path": "gold_annotation.annotator_id",
                    "error": "missing_annotator_id",
                }
            )
        for field in ("valid_facts", "invalid_candidate_fact_ids", "missing_facts"):
            if not isinstance(annotation.get(field), list):
                errors.append(
                    {
                        "sample_id": record.get("sample_id"),
                        "source_id": record.get("source_id"),
                        "path": f"gold_annotation.{field}",
                        "error": "not_a_list",
                    }
                )
        candidate_fact_ids = {
            str(fact.get("fact_id"))
            for fact in record.get("candidate_facts", [])
            if isinstance(fact, dict) and fact.get("fact_id")
        }
        invalid_ids = [str(value) for value in annotation.get("invalid_candidate_fact_ids", [])]
        unknown_invalid = sorted(set(invalid_ids) - candidate_fact_ids)
        if unknown_invalid:
            errors.append(
                {
                    "sample_id": record.get("sample_id"),
                    "source_id": record.get("source_id"),
                    "path": "gold_annotation.invalid_candidate_fact_ids",
                    "error": "unknown_candidate_fact_ids",
                    "fact_ids": unknown_invalid,
                }
            )
        for index, fact in enumerate(annotation.get("valid_facts", [])):
            if isinstance(fact, dict):
                errors.extend(
                    validate_gold_fact(
                        fact=fact,
                        record=record,
                        fact_path=f"gold_annotation.valid_facts[{index}]",
                    )
                )
            else:
                errors.append(
                    {
                        "sample_id": record.get("sample_id"),
                        "source_id": record.get("source_id"),
                        "path": f"gold_annotation.valid_facts[{index}]",
                        "error": "not_an_object",
                    }
                )
        for index, fact in enumerate(annotation.get("missing_facts", [])):
            if isinstance(fact, dict):
                errors.extend(
                    validate_gold_fact(
                        fact=fact,
                        record=record,
                        fact_path=f"gold_annotation.missing_facts[{index}]",
                    )
                )
            else:
                errors.append(
                    {
                        "sample_id": record.get("sample_id"),
                        "source_id": record.get("source_id"),
                        "path": f"gold_annotation.missing_facts[{index}]",
                        "error": "not_an_object",
                    }
                )
        errors.extend(validate_rejection_adjudications(record))

    status = "ready_for_scoring"
    if errors:
        status = "needs_revision"
    elif warnings:
        status = "pending_manual_annotation"

    return {
        "status": status,
        "record_count": len(gold_records),
        "selected_source_id_count": len(selected_source_ids),
        "reviewed_record_count": sum(
            1
            for record in gold_records
            if record.get("gold_annotation", {}).get("annotation_status") == REVIEWED_GOLD_STATUS
        ),
        "pending_record_count": sum(
            1
            for record in gold_records
            if record.get("gold_annotation", {}).get("annotation_status") != REVIEWED_GOLD_STATUS
        ),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors[:100],
        "warnings": warnings[:100],
        "completion_gate": (
            "Gold annotations are usable for formal precision/recall/F1 only when status is "
            "ready_for_scoring."
        ),
    }


def build_gold_annotation_validation_report(
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    selected_source_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    validation = validate_gold_annotation_records(
        gold_records=gold_records,
        selected_source_ids=selected_source_ids,
    )
    return {
        "source_family": "nasa_atmonto_gold_annotation_validation",
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        **validation,
    }


def gold_validation_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Annotation Validation",
        "",
        f"- Status: `{report['status']}`",
        f"- Gold template: `{report['gold_template']}`",
        f"- Gold manifest: `{report['gold_manifest']}`",
        f"- Records: {report['record_count']}",
        f"- Reviewed records: {report['reviewed_record_count']}",
        f"- Pending records: {report['pending_record_count']}",
        f"- Errors: {report['error_count']}",
        f"- Warnings: {report['warning_count']}",
        "",
        "## Completion Gate",
        "",
        f"- {report['completion_gate']}",
        "",
        "## Required Rejection Decisions",
        "",
        "- For each reviewed record, every rejected validator fact must have a "
        "`rejected_fact_adjudications` entry.",
        "- Allowed decisions: "
        + ", ".join(f"`{value}`" for value in sorted(ALLOWED_REJECTION_ADJUDICATIONS)),
        "",
        "## Current Warnings",
        "",
    ]
    for warning in report["warnings"][:20]:
        lines.append(
            f"- `{warning.get('sample_id')}` / `{warning.get('source_id')}`: "
            f"{warning.get('warning')}"
        )
    if len(report["warnings"]) > 20:
        lines.append(f"- ... {len(report['warnings']) - 20} more warnings omitted")
    lines.extend(["", "## Current Errors", ""])
    for error in report["errors"][:20]:
        lines.append(f"- `{error.get('path', '<manifest>')}`: {error.get('error')}")
    if len(report["errors"]) > 20:
        lines.append(f"- ... {len(report['errors']) - 20} more errors omitted")
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def run_gold_annotation_validation(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    report = build_gold_annotation_validation_report(repo_root)
    write_json(repo_root / GOLD_VALIDATION_REPORT_JSON, report)
    (repo_root / GOLD_VALIDATION_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_VALIDATION_REPORT_MD).write_text(
        gold_validation_markdown(report),
        encoding="utf-8",
    )
    return {
        "report_json": project_relative_path(repo_root / GOLD_VALIDATION_REPORT_JSON, repo_root),
        "report_markdown": project_relative_path(repo_root / GOLD_VALIDATION_REPORT_MD, repo_root),
        "status": report["status"],
        "error_count": report["error_count"],
        "warning_count": report["warning_count"],
    }


def rejection_group_lookup(rejection_analysis: dict[str, Any]) -> dict[tuple[str, tuple[str, ...]], dict[str, Any]]:
    lookup: dict[tuple[str, tuple[str, ...]], dict[str, Any]] = {}
    for group in rejection_analysis.get("groups", []):
        if not isinstance(group, dict):
            continue
        predicate = str(group.get("predicate", ""))
        errors = tuple(str(error) for error in group.get("errors", []))
        lookup[(predicate, errors)] = group
    return lookup


def summarize_rejected_fact(
    *,
    record: dict[str, Any],
    validator_result: dict[str, Any],
    candidate_by_id: dict[str, dict[str, Any]],
    group_lookup: dict[tuple[str, tuple[str, ...]], dict[str, Any]],
) -> dict[str, Any]:
    fact_id = str(validator_result.get("fact_id", ""))
    candidate = candidate_by_id.get(fact_id, {})
    errors = tuple(str(error) for error in validator_result.get("errors", []))
    predicate = str(candidate.get("predicate", ""))
    group = group_lookup.get((predicate, errors), {})
    return {
        "fact_id": fact_id,
        "predicate": predicate,
        "errors": list(errors),
        "subject_class": candidate.get("subject_class"),
        "object_class": candidate.get("object_class"),
        "object": candidate.get("object"),
        "value": candidate.get("value"),
        "evidence_text": candidate.get("evidence_text"),
        "suggested_decision": group.get("decision"),
        "suggested_rationale": group.get("rationale"),
        "suggested_action": group.get("recommended_action"),
    }


def build_gold_review_worklist(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    rejection_analysis = read_json(repo_root / REJECTION_ANALYSIS_JSON)
    group_lookup = rejection_group_lookup(rejection_analysis)

    work_records: list[dict[str, Any]] = []
    total_rejected_facts = 0
    records_with_rejections = 0
    class_counts: Counter[str] = Counter()
    status_counts: Counter[str] = Counter()
    suggested_decision_counts: Counter[str] = Counter()

    for record in gold_records:
        annotation = record.get("gold_annotation", {})
        status = str(annotation.get("annotation_status", "missing_status"))
        status_counts[status] += 1
        class_name = str(record.get("candidate_subject_class", ""))
        class_counts[class_name] += 1
        candidate_by_id = {
            str(candidate.get("fact_id")): candidate
            for candidate in record.get("candidate_facts", [])
            if isinstance(candidate, dict) and candidate.get("fact_id")
        }
        rejected = [
            summarize_rejected_fact(
                record=record,
                validator_result=result,
                candidate_by_id=candidate_by_id,
                group_lookup=group_lookup,
            )
            for result in record.get("validator_results", [])
            if isinstance(result, dict) and result.get("accepted") is False
        ]
        if rejected:
            records_with_rejections += 1
        total_rejected_facts += len(rejected)
        for item in rejected:
            if item.get("suggested_decision"):
                suggested_decision_counts[str(item["suggested_decision"])] += 1
        work_records.append(
            {
                "sample_id": record.get("sample_id"),
                "source_id": record.get("source_id"),
                "source_url": record.get("source_url"),
                "advisory_date": record.get("advisory_date"),
                "advisory_number": record.get("advisory_number"),
                "candidate_subject_class": record.get("candidate_subject_class"),
                "annotation_status": status,
                "candidate_fact_count": record.get("candidate_fact_count", 0),
                "accepted_fact_count": record.get("accepted_fact_count", 0),
                "rejected_fact_count": len(rejected),
                "source_text_excerpt": record.get("source_text_excerpt", ""),
                "required_tasks": [
                    "mark valid candidate facts",
                    "mark invalid candidate fact IDs",
                    "add missing gold facts with evidence_text",
                    "adjudicate validator-rejected facts",
                ],
                "rejected_facts_to_adjudicate": rejected,
            }
        )

    return {
        "source_family": "nasa_atmonto_gold_review_worklist",
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        "annotation_guide": "docs/nasa_atmonto_gold_annotation_guide.md",
        "selected_source_id_count": len(manifest["selected_source_ids"]),
        "record_count": len(work_records),
        "records_with_rejections": records_with_rejections,
        "total_rejected_facts_to_adjudicate": total_rejected_facts,
        "status_counts": dict(sorted(status_counts.items())),
        "candidate_subject_class_counts": dict(sorted(class_counts.items())),
        "suggested_decision_counts": dict(sorted(suggested_decision_counts.items())),
        "records": work_records,
        "completion_gate": (
            "Use this worklist to complete reviewed gold annotations; scoring still requires "
            "the JSONL template to pass gold annotation validation."
        ),
    }


def gold_review_worklist_markdown(worklist: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Gold Annotation Review Worklist",
        "",
        f"- Gold template: `{worklist['gold_template']}`",
        f"- Annotation guide: `{worklist['annotation_guide']}`",
        f"- Records: {worklist['record_count']}",
        f"- Records with validator rejections: {worklist['records_with_rejections']}",
        f"- Rejected facts to adjudicate: {worklist['total_rejected_facts_to_adjudicate']}",
        f"- Status counts: `{json.dumps(worklist['status_counts'], sort_keys=True)}`",
        f"- Suggested decisions: `{json.dumps(worklist['suggested_decision_counts'], sort_keys=True)}`",
        "",
        "## Review Queue",
        "",
        "| Sample | Source | Class | Candidates | Accepted | Rejected | Status |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for record in worklist["records"]:
        lines.append(
            "| "
            f"`{record['sample_id']}` | "
            f"`{record['source_id']}` | "
            f"`{record['candidate_subject_class']}` | "
            f"{record['candidate_fact_count']} | "
            f"{record['accepted_fact_count']} | "
            f"{record['rejected_fact_count']} | "
            f"`{record['annotation_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Rejected Facts Needing Adjudication",
            "",
            "| Sample | Fact | Predicate | Errors | Suggested decision | Evidence |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for record in worklist["records"]:
        for fact in record["rejected_facts_to_adjudicate"]:
            evidence = compact_text(fact.get("evidence_text"))[:140]
            lines.append(
                "| "
                f"`{record['sample_id']}` | "
                f"`{fact['fact_id']}` | "
                f"`{fact['predicate']}` | "
                f"`{', '.join(fact['errors'])}` | "
                f"`{fact.get('suggested_decision')}` | "
                f"{evidence} |"
            )
    lines.extend(["", "## Completion Gate", "", f"- {worklist['completion_gate']}"])
    return "\n".join(lines) + "\n"


def run_gold_review_worklist(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    worklist = build_gold_review_worklist(repo_root)
    write_json(repo_root / GOLD_REVIEW_WORKLIST_JSON, worklist)
    (repo_root / GOLD_REVIEW_WORKLIST_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_REVIEW_WORKLIST_MD).write_text(
        gold_review_worklist_markdown(worklist),
        encoding="utf-8",
    )
    return {
        "worklist_json": project_relative_path(repo_root / GOLD_REVIEW_WORKLIST_JSON, repo_root),
        "worklist_markdown": project_relative_path(repo_root / GOLD_REVIEW_WORKLIST_MD, repo_root),
        "record_count": worklist["record_count"],
        "records_with_rejections": worklist["records_with_rejections"],
        "total_rejected_facts_to_adjudicate": worklist["total_rejected_facts_to_adjudicate"],
    }


def selected_validations(
    validations: list[dict[str, Any]],
    selected_ids: set[str],
) -> list[dict[str, Any]]:
    return [item for item in validations if str(item.get("source_id")) in selected_ids]


def selected_payloads(
    payloads: list[dict[str, Any]],
    selected_ids: set[str],
) -> list[dict[str, Any]]:
    return [item for item in payloads if str(item.get("source_id")) in selected_ids]


def formal_input_records(gold_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for record in gold_records:
        records.append(
            {
                "sample_id": record["sample_id"],
                "source_id": record["source_id"],
                "source_family": record.get("source_family", "atcscc_advisories"),
                "source_url": record.get("source_url"),
                "advisory_date": record.get("advisory_date"),
                "advisory_number": record.get("advisory_number"),
                "candidate_subject_class": record.get("candidate_subject_class"),
                "source_text": record.get("source_text", ""),
                "source_text_excerpt": record.get("source_text_excerpt", ""),
            }
        )
    return records


def group_by_source_id(records: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(str(record.get("source_id")), []).append(record)
    return grouped


def build_s0_prediction_records(
    *,
    input_records: list[dict[str, Any]],
    s0_validations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    validations_by_source = group_by_source_id(s0_validations)
    predictions: list[dict[str, Any]] = []
    for record in input_records:
        source_id = str(record["source_id"])
        validations = validations_by_source.get(source_id, [])
        accepted = [item for item in validations if item.get("accepted")]
        rejected = [item for item in validations if not item.get("accepted")]
        facts = [
            item["validated_fact"]
            for item in accepted
            if isinstance(item.get("validated_fact"), dict)
        ]
        predictions.append(
            {
                "system_id": "S0_rule_only",
                "sample_id": record["sample_id"],
                "source_id": source_id,
                "source_family": record["source_family"],
                "json_adherence": True,
                "facts": facts,
                "candidate_facts": [
                    item["candidate"]
                    for item in validations
                    if isinstance(item.get("candidate"), dict)
                ],
                "validator_results": validations,
                "candidate_fact_count": len(validations),
                "accepted_fact_count": len(facts),
                "rejected_fact_count": len(rejected),
                "rejected_candidate_fact_ids": [
                    item.get("fact_id") for item in rejected if item.get("fact_id")
                ],
                "claim_boundary": (
                    "Rule-only predictions are structurally validated pilot outputs; "
                    "manual gold review is still required for semantic correctness."
                ),
            }
        )
    return predictions


def build_s0_run_metadata(
    *,
    repo_root: Path,
    input_record_count: int,
    prediction_record_count: int,
) -> dict[str, Any]:
    return {
        "system_id": "S0_rule_only",
        "run_status": "completed",
        "runner": "schema_slice_rule_baseline",
        "requires_llm": False,
        "input_records": project_relative_path(repo_root / FORMAL_INPUT_RECORDS_PATH, repo_root),
        "prediction_output": project_relative_path(repo_root / SYSTEMS[0].expected_output, repo_root),
        "input_record_count": input_record_count,
        "prediction_record_count": prediction_record_count,
        "source_candidates": project_relative_path(repo_root / S0_CANDIDATES_PATH, repo_root),
        "source_validations": project_relative_path(repo_root / S0_VALIDATED_PATH, repo_root),
        "claim_boundary": (
            "S0 is deterministic baseline output. It is not manual gold truth and "
            "semantic correctness must be evaluated against reviewed annotations."
        ),
    }


def extraction_output_contract() -> dict[str, Any]:
    return {
        "required_top_level_fields": ["source_id", "source_family", "facts"],
        "fact_fields": [
            "fact_type",
            "subject",
            "subject_class",
            "predicate",
            "object",
            "object_class",
            "value",
            "datatype",
            "evidence_text",
        ],
        "fact_type_values": ["object_property", "datatype_property"],
        "evidence_rule": (
            "Every fact must include a short evidence_text copied from the advisory text. "
            "Do not invent evidence."
        ),
        "empty_case": "If no fact is supported, return an empty facts list.",
    }


def compact_term(row: dict[str, Any]) -> dict[str, Any]:
    compact = {
        "term": row.get("prefixed_name") or row.get("local_name") or row.get("iri"),
        "local_name": row.get("local_name"),
    }
    if row.get("domain_set"):
        compact["domain"] = row["domain_set"]
    if row.get("range_set"):
        compact["range"] = row["range_set"]
    if row.get("datatype_set"):
        compact["datatype"] = row["datatype_set"]
    if row.get("comment"):
        compact["comment"] = compact_text(row["comment"])
    return compact


def compact_schema_context(schema_slice: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_slice_id": schema_slice["schema_slice_id"],
        "classes": [compact_term(row) for row in schema_slice.get("classes", [])],
        "object_properties": [
            compact_term(row) for row in schema_slice.get("object_properties", [])
        ],
        "datatype_properties": [
            compact_term(row) for row in schema_slice.get("datatype_properties", [])
        ],
        "class_property_constraints": schema_slice.get("class_property_constraints", []),
        "boundary": (
            "Use only these schema-slice terms when a prompt condition says schema terms "
            "are allowed. The slice is a constraint, not manual ground truth."
        ),
    }


def prompt_user_content(record: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"sample_id: {record['sample_id']}",
            f"source_id: {record['source_id']}",
            f"source_family: {record['source_family']}",
            f"advisory_date: {record.get('advisory_date')}",
            f"advisory_number: {record.get('advisory_number')}",
            "",
            "ATCSCC advisory text:",
            str(record.get("source_text", "")),
        ]
    )


def llm_only_system_prompt() -> str:
    return (
        "Extract a compact knowledge-graph fact payload from one ATCSCC advisory. "
        "Return strict JSON only. Use descriptive class and predicate labels derived "
        "from the text. Do not use any external ontology term list or schema "
        "vocabulary. Every fact must quote evidence_text from the advisory."
    )


def schema_slice_system_prompt(schema_context: dict[str, Any]) -> str:
    return "\n".join(
        [
            "Extract a compact knowledge-graph fact payload from one ATCSCC advisory.",
            "Return strict JSON only.",
            "Use only the provided NASA ATMONTO ATCSCC schema-slice classes and properties.",
            "Every fact must quote evidence_text from the advisory.",
            "Schema slice:",
            json.dumps(schema_context, ensure_ascii=False, sort_keys=True),
        ]
    )


def validator_repair_system_prompt(schema_context: dict[str, Any]) -> str:
    return "\n".join(
        [
            schema_slice_system_prompt(schema_context),
            "",
            "Validator/repair condition:",
            "After the initial payload is checked, repair only facts called out by validator "
            "errors. Do not add unsupported facts during repair. Preserve raw source evidence "
            "and return strict JSON only for the repaired payload.",
        ]
    )


def build_prompt_batch(
    *,
    system: SystemDefinition,
    input_records: list[dict[str, Any]],
    schema_context: dict[str, Any],
) -> list[dict[str, Any]]:
    if system.system_id == "S1_llm_only":
        system_prompt = llm_only_system_prompt()
        schema_context_ref = None
        stages = ["initial_extraction"]
    elif system.system_id == "S2_llm_schema_slice":
        system_prompt = schema_slice_system_prompt(schema_context)
        schema_context_ref = SCHEMA_SLICE_PATH.as_posix()
        stages = ["initial_extraction"]
    elif system.system_id == "S3_llm_schema_slice_validator_repair":
        system_prompt = validator_repair_system_prompt(schema_context)
        schema_context_ref = SCHEMA_SLICE_PATH.as_posix()
        stages = ["initial_extraction", "validate", "repair_if_invalid"]
    else:
        raise ValueError(f"No LLM prompt batch for {system.system_id}")

    return [
        {
            "task_id": f"{system.system_id}:{record['sample_id']}",
            "system_id": system.system_id,
            "sample_id": record["sample_id"],
            "source_id": record["source_id"],
            "source_family": record["source_family"],
            "schema_context_ref": schema_context_ref,
            "stages": stages,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_user_content(record)},
            ],
            "expected_output_contract": extraction_output_contract(),
            "expected_output_record": {
                "source_id": record["source_id"],
                "source_family": record["source_family"],
                "facts": [],
            },
        }
        for record in input_records
    ]


def build_system_specs(repo_root: Path, schema_context: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_family": "nasa_atmonto_formal_experiment_system_specs",
        "input_records": project_relative_path(repo_root / FORMAL_INPUT_RECORDS_PATH, repo_root),
        "schema_slice": project_relative_path(repo_root / SCHEMA_SLICE_PATH, repo_root),
        "extraction_schema": project_relative_path(repo_root / EXTRACTION_SCHEMA_PATH, repo_root),
        "llm_prediction_runner": "scripts/run_nasa_atmonto_llm_predictions.py",
        "systems": system_definitions(repo_root),
        "common_output_contract": extraction_output_contract(),
        "schema_context_summary": {
            "schema_slice_id": schema_context["schema_slice_id"],
            "class_count": len(schema_context["classes"]),
            "object_property_count": len(schema_context["object_properties"]),
            "datatype_property_count": len(schema_context["datatype_properties"]),
        },
        "execution_boundary": (
            "Prompt batches prepare model inputs only. S1-S3 predictions are produced by "
            "the explicit LLM runner and are not fabricated; formal scoring waits for "
            "reviewed gold annotations and S1-S3 predictions."
        ),
    }


def prepare_formal_experiment_inputs(
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    schema_slice = read_json(repo_root / SCHEMA_SLICE_PATH)
    s0_validations_all = read_jsonl(repo_root / S0_VALIDATED_PATH)

    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    input_records = formal_input_records(gold_records)
    if {str(record["source_id"]) for record in input_records} != selected_ids:
        raise ValueError("Formal input records do not match selected gold sample IDs")

    s0_validations = selected_validations(s0_validations_all, selected_ids)
    s0_predictions = build_s0_prediction_records(
        input_records=input_records,
        s0_validations=s0_validations,
    )
    schema_context = compact_schema_context(schema_slice)
    prompt_batches = {
        S1_PROMPT_BATCH_PATH: build_prompt_batch(
            system=SYSTEMS[1],
            input_records=input_records,
            schema_context=schema_context,
        ),
        S2_PROMPT_BATCH_PATH: build_prompt_batch(
            system=SYSTEMS[2],
            input_records=input_records,
            schema_context=schema_context,
        ),
        S3_PROMPT_BATCH_PATH: build_prompt_batch(
            system=SYSTEMS[3],
            input_records=input_records,
            schema_context=schema_context,
        ),
    }

    write_jsonl(repo_root / FORMAL_INPUT_RECORDS_PATH, input_records)
    write_jsonl(repo_root / SYSTEMS[0].expected_output, s0_predictions)
    write_json(
        repo_root / system_run_metadata_path(SYSTEMS[0]),
        build_s0_run_metadata(
            repo_root=repo_root,
            input_record_count=len(input_records),
            prediction_record_count=len(s0_predictions),
        ),
    )
    for path, records in prompt_batches.items():
        write_jsonl(repo_root / path, records)
    write_json(repo_root / FORMAL_SYSTEM_SPECS_PATH, build_system_specs(repo_root, schema_context))

    return {
        "input_records": project_relative_path(repo_root / FORMAL_INPUT_RECORDS_PATH, repo_root),
        "input_record_count": len(input_records),
        "s0_predictions": project_relative_path(repo_root / SYSTEMS[0].expected_output, repo_root),
        "s0_run_metadata": project_relative_path(
            repo_root / system_run_metadata_path(SYSTEMS[0]),
            repo_root,
        ),
        "s0_prediction_record_count": len(s0_predictions),
        "prompt_batches": {
            path.as_posix(): len(records)
            for path, records in sorted(
                prompt_batches.items(),
                key=lambda item: item[0].as_posix(),
            )
        },
        "system_specs": project_relative_path(repo_root / FORMAL_SYSTEM_SPECS_PATH, repo_root),
    }


def utc_timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def llm_response_text(response: object) -> str:
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if text:
                    parts.append(str(text))
            elif item:
                parts.append(str(item))
        return "\n".join(parts).strip()
    return str(content).strip()


def invoke_llm_messages(
    messages: list[dict[str, str]],
    *,
    temperature: float,
    max_tokens: int,
) -> str:
    return build_default_llm_invoker(temperature=temperature, max_tokens=max_tokens)(messages)


def build_langchain_messages(messages: list[dict[str, str]]) -> list[Any]:
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
    except ImportError as exc:
        raise RuntimeError(
            "NASA ATMONTO LLM prediction runs require optional LLM dependencies. "
            "Install with: uv sync --extra ontology-generation"
        ) from exc

    chat_messages = []
    for message in messages:
        role = str(message.get("role", "user"))
        content = str(message.get("content", ""))
        if role == "system":
            chat_messages.append(SystemMessage(content=content))
        else:
            chat_messages.append(HumanMessage(content=content))
    return chat_messages


def build_default_llm_invoker(
    *,
    temperature: float,
    max_tokens: int,
) -> LLMInvoker:
    llm = get_llm(temperature=temperature, max_tokens=max_tokens)

    def invoke(messages: list[dict[str, str]]) -> str:
        return llm_response_text(llm.invoke(build_langchain_messages(messages)))

    return invoke


def stable_llm_fact_id(
    *,
    system_id: str,
    sample_id: str,
    index: int,
    fact: dict[str, Any],
) -> str:
    material = json.dumps(fact, sort_keys=True, ensure_ascii=False)
    digest = sha1(material.encode("utf-8")).hexdigest()[:12]
    return f"{system_id}:{sample_id}:fact-{index + 1:02d}-{digest}"


def normalize_llm_facts(
    *,
    payload: dict[str, Any],
    task: dict[str, Any],
) -> tuple[list[dict[str, Any]], int]:
    facts_raw = payload.get("facts", [])
    if not isinstance(facts_raw, list):
        raise ValueError("facts_not_a_list")
    facts: list[dict[str, Any]] = []
    skipped = 0
    for index, fact in enumerate(facts_raw):
        if not isinstance(fact, dict):
            skipped += 1
            continue
        normalized = dict(fact)
        normalized.setdefault("source_id", task["source_id"])
        normalized.setdefault("source_family", task.get("source_family", "atcscc_advisories"))
        normalized.setdefault(
            "subject",
            f"urn:aviation-agentic-ai:tmi:{task['source_id']}",
        )
        normalized.setdefault(
            "fact_id",
            stable_llm_fact_id(
                system_id=str(task["system_id"]),
                sample_id=str(task["sample_id"]),
                index=index,
                fact=normalized,
            ),
        )
        facts.append(normalized)
    return facts, skipped


def parse_llm_prediction_payload(
    *,
    raw_response: str,
    task: dict[str, Any],
) -> dict[str, Any]:
    try:
        payload = extract_json_object(raw_response)
        facts, skipped_fact_count = normalize_llm_facts(payload=payload, task=task)
    except (JSONPayloadExtractionError, ValueError) as exc:
        return {
            "system_id": task["system_id"],
            "sample_id": task["sample_id"],
            "source_id": task["source_id"],
            "source_family": task.get("source_family", "atcscc_advisories"),
            "json_adherence": False,
            "facts": None,
            "raw_response": raw_response,
            "parse_error": str(exc),
        }
    return {
        "system_id": task["system_id"],
        "sample_id": task["sample_id"],
        "source_id": str(payload.get("source_id") or task["source_id"]),
        "source_family": str(
            payload.get("source_family") or task.get("source_family", "atcscc_advisories")
        ),
        "json_adherence": True,
        "facts": facts,
        "raw_response": raw_response,
        "parse_error": None,
        "skipped_non_object_fact_count": skipped_fact_count,
    }


def source_row_for_task(task: dict[str, Any], input_by_source_id: dict[str, dict[str, Any]]) -> dict[str, object]:
    source_id = str(task["source_id"])
    input_record = input_by_source_id[source_id]
    return {"source_id": source_id, "text": input_record.get("source_text", "")}


def validate_prediction_record(
    *,
    record: dict[str, Any],
    source_row: dict[str, object],
    schema_slice: dict[str, Any],
) -> list[dict[str, Any]]:
    if not record.get("json_adherence") or not isinstance(record.get("facts"), list):
        return []
    return validate_candidate_payloads(
        prediction_payloads_for_validation([record]),
        [source_row],
        schema_slice,
    )


def rejected_validation_summary(validation_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "fact_id": item.get("fact_id"),
            "errors": item.get("errors", []),
            "candidate": item.get("candidate"),
        }
        for item in validation_results
        if item.get("accepted") is False
    ]


def build_repair_messages(
    *,
    task: dict[str, Any],
    initial_record: dict[str, Any],
    validation_results: list[dict[str, Any]],
) -> list[dict[str, str]]:
    rejected = rejected_validation_summary(validation_results)
    repair_context = {
        "sample_id": task["sample_id"],
        "source_id": task["source_id"],
        "parse_error": initial_record.get("parse_error"),
        "validator_rejections": rejected,
        "instruction": (
            "Return one complete corrected JSON object with source_id, source_family, and facts. "
            "Remove unsupported facts instead of inventing replacements. Keep evidence_text copied "
            "from the advisory."
        ),
    }
    messages = list(task["messages"])
    messages.append(
        {
            "role": "user",
            "content": "\n".join(
                [
                    "The initial extraction payload failed validation.",
                    "Initial raw response:",
                    str(initial_record.get("raw_response", "")),
                    "",
                    "Validation feedback:",
                    json.dumps(repair_context, ensure_ascii=False, sort_keys=True),
                ]
            ),
        }
    )
    return messages


def prediction_record_counts(record: dict[str, Any]) -> dict[str, int]:
    validation_results = [
        item for item in record.get("validator_results", []) if isinstance(item, dict)
    ]
    return {
        "candidate_fact_count": len(record.get("facts") or []),
        "accepted_fact_count": sum(1 for item in validation_results if item.get("accepted")),
        "rejected_fact_count": sum(1 for item in validation_results if not item.get("accepted")),
    }


def build_llm_prediction_record(
    *,
    system: SystemDefinition,
    task: dict[str, Any],
    raw_response: str,
    source_row: dict[str, object],
    schema_slice: dict[str, Any],
    invoker: LLMInvoker,
) -> dict[str, Any]:
    initial_record = parse_llm_prediction_payload(raw_response=raw_response, task=task)
    initial_validation = validate_prediction_record(
        record=initial_record,
        source_row=source_row,
        schema_slice=schema_slice,
    )
    final_record = dict(initial_record)
    repair_attempted = False
    repair_raw_response = None
    repair_parse_error = None
    repair_reason = None

    should_repair = system.uses_validator_repair and (
        not initial_record.get("json_adherence")
        or any(item.get("accepted") is False for item in initial_validation)
    )
    if should_repair:
        repair_attempted = True
        repair_reason = "parse_error" if not initial_record.get("json_adherence") else "validator_rejections"
        repair_raw_response = invoker(
            build_repair_messages(
                task=task,
                initial_record=initial_record,
                validation_results=initial_validation,
            )
        )
        repaired_record = parse_llm_prediction_payload(raw_response=repair_raw_response, task=task)
        repair_parse_error = repaired_record.get("parse_error")
        if repaired_record.get("json_adherence"):
            final_record = repaired_record

    final_validation = validate_prediction_record(
        record=final_record,
        source_row=source_row,
        schema_slice=schema_slice,
    )
    final_record["validator_results"] = final_validation
    final_record["initial_validator_results"] = initial_validation
    final_record["repair_attempted"] = repair_attempted
    final_record["repair_reason"] = repair_reason
    final_record["repair_raw_response"] = repair_raw_response
    final_record["repair_parse_error"] = repair_parse_error
    final_record["schema_valid"] = (
        final_record.get("json_adherence") is True
        and isinstance(final_record.get("facts"), list)
        and all(item.get("accepted") for item in final_validation)
    )
    final_record.update(prediction_record_counts(final_record))
    return final_record


def system_by_id(system_id: str) -> SystemDefinition:
    for system in SYSTEMS:
        if system.system_id == system_id:
            return system
    raise ValueError(f"Unknown system_id: {system_id}")


def build_llm_run_metadata(
    *,
    repo_root: Path,
    system: SystemDefinition,
    prompt_count: int,
    records: list[dict[str, Any]],
    started_at: str,
    completed_at: str,
    temperature: float,
    max_tokens: int,
    limit: int | None,
) -> dict[str, Any]:
    repair_attempted = sum(1 for record in records if record.get("repair_attempted"))
    repair_success = sum(
        1
        for record in records
        if record.get("repair_attempted")
        and record.get("repair_parse_error") is None
        and record.get("schema_valid")
    )
    return {
        "system_id": system.system_id,
        "run_status": "completed" if limit is None or len(records) == prompt_count else "partial",
        "runner": "nasa_atmonto_prompt_batch_llm_runner",
        "provider": configured_llm_provider(),
        "model": configured_llm_model(),
        "temperature": temperature,
        "max_tokens": max_tokens,
        "started_at": started_at,
        "completed_at": completed_at,
        "input_records": project_relative_path(repo_root / FORMAL_INPUT_RECORDS_PATH, repo_root),
        "prompt_batch": project_relative_path(repo_root / system.prompt_batch, repo_root)
        if system.prompt_batch
        else None,
        "prediction_output": project_relative_path(repo_root / system.expected_output, repo_root),
        "prompt_count": prompt_count,
        "prediction_record_count": len(records),
        "parse_error_count": sum(1 for record in records if not record.get("json_adherence")),
        "schema_valid_record_count": sum(1 for record in records if record.get("schema_valid")),
        "repair_attempted_record_count": repair_attempted,
        "repair_success_record_count": repair_success,
        "limit": limit,
        "claim_boundary": (
            "LLM predictions are experiment outputs only; formal extraction effectiveness still "
            "requires reviewed gold annotations and scoring."
        ),
    }


def run_llm_prediction_system(
    *,
    system_id: str,
    repo_root: str | Path = PROJECT_ROOT,
    temperature: float = 0.0,
    max_tokens: int = 4096,
    limit: int | None = None,
    invoker: LLMInvoker | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    system = system_by_id(system_id)
    if not system.requires_llm:
        raise ValueError(f"{system_id} is not an LLM prediction system")
    if not system.prompt_batch:
        raise ValueError(f"{system_id} does not define a prompt batch")
    if limit is not None and limit < 1:
        raise ValueError("limit must be >= 1 when provided")

    prompt_records = read_jsonl(repo_root / system.prompt_batch)
    input_records = read_jsonl(repo_root / FORMAL_INPUT_RECORDS_PATH)
    schema_slice = read_json(repo_root / SCHEMA_SLICE_PATH)
    input_by_source_id = {str(record["source_id"]): record for record in input_records}
    effective_records = prompt_records[:limit] if limit is not None else prompt_records
    effective_invoker = invoker or build_default_llm_invoker(
        temperature=temperature,
        max_tokens=max_tokens,
    )

    started_at = utc_timestamp()
    predictions: list[dict[str, Any]] = []
    for task in effective_records:
        source_row = source_row_for_task(task, input_by_source_id)
        raw_response = effective_invoker(task["messages"])
        predictions.append(
            build_llm_prediction_record(
                system=system,
                task=task,
                raw_response=raw_response,
                source_row=source_row,
                schema_slice=schema_slice,
                invoker=effective_invoker,
            )
        )
    completed_at = utc_timestamp()
    metadata = build_llm_run_metadata(
        repo_root=repo_root,
        system=system,
        prompt_count=len(prompt_records),
        records=predictions,
        started_at=started_at,
        completed_at=completed_at,
        temperature=temperature,
        max_tokens=max_tokens,
        limit=limit,
    )
    write_jsonl(repo_root / system.expected_output, predictions)
    write_json(repo_root / system_run_metadata_path(system), metadata)
    return {
        "system_id": system.system_id,
        "prediction_output": project_relative_path(repo_root / system.expected_output, repo_root),
        "run_metadata": project_relative_path(
            repo_root / system_run_metadata_path(system),
            repo_root,
        ),
        "run_status": metadata["run_status"],
        "prompt_count": len(prompt_records),
        "prediction_record_count": len(predictions),
        "parse_error_count": metadata["parse_error_count"],
        "schema_valid_record_count": metadata["schema_valid_record_count"],
        "repair_attempted_record_count": metadata["repair_attempted_record_count"],
        "repair_success_record_count": metadata["repair_success_record_count"],
    }


def read_jsonl_lenient(path: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    invalid_lines: list[dict[str, Any]] = []
    if not path.exists():
        return {
            "exists": False,
            "records": records,
            "line_count": 0,
            "invalid_json_line_count": 0,
            "invalid_json_lines": invalid_lines,
        }
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                invalid_lines.append(
                    {
                        "line_number": line_number,
                        "error": exc.msg,
                    }
                )
                continue
            if isinstance(payload, dict):
                records.append(payload)
            else:
                invalid_lines.append(
                    {
                        "line_number": line_number,
                        "error": "top_level_json_value_is_not_object",
                    }
                )
    return {
        "exists": True,
        "records": records,
        "line_count": len(records) + len(invalid_lines),
        "invalid_json_line_count": len(invalid_lines),
        "invalid_json_lines": invalid_lines[:10],
    }


def read_json_lenient(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "payload": None, "error": None}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"exists": True, "payload": None, "error": exc.msg}
    if not isinstance(payload, dict):
        return {"exists": True, "payload": None, "error": "top_level_json_value_is_not_object"}
    return {"exists": True, "payload": payload, "error": None}


def is_valid_prediction_payload(record: dict[str, Any], selected_ids: set[str]) -> bool:
    return str(record.get("source_id")) in selected_ids and isinstance(record.get("facts"), list)


def prediction_json_metrics(
    *,
    parse_result: dict[str, Any],
    selected_ids: set[str],
) -> dict[str, Any]:
    records = [record for record in parse_result["records"] if isinstance(record, dict)]
    valid_records = [record for record in records if is_valid_prediction_payload(record, selected_ids)]
    valid_source_counts = Counter(str(record["source_id"]) for record in valid_records)
    valid_source_ids = set(valid_source_counts)
    duplicate_count = sum(count - 1 for count in valid_source_counts.values() if count > 1)
    invalid_payload_count = len(records) - len(valid_records)
    attempted = len(selected_ids)
    return {
        "attempted_record_count": attempted,
        "line_count": parse_result["line_count"],
        "valid_json_payload_count": len(valid_source_ids),
        "invalid_json_line_count": parse_result["invalid_json_line_count"],
        "invalid_payload_count": invalid_payload_count,
        "duplicate_output_record_count": duplicate_count,
        "missing_output_record_count": len(selected_ids - valid_source_ids),
        "json_adherence": (len(valid_source_ids) / attempted) if attempted else None,
    }


def valid_prediction_records(
    parse_result: dict[str, Any],
    selected_ids: set[str],
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    records: list[dict[str, Any]] = []
    for record in parse_result["records"]:
        source_id = str(record.get("source_id"))
        if source_id in seen or not is_valid_prediction_payload(record, selected_ids):
            continue
        seen.add(source_id)
        records.append(record)
    return records


def prompt_batch_validation(
    *,
    system: SystemDefinition,
    repo_root: Path,
    selected_ids: set[str],
) -> dict[str, Any]:
    if not system.prompt_batch:
        return {
            "path": None,
            "exists": None,
            "task_count": None,
            "valid_task_count": None,
            "missing_source_id_count": None,
            "duplicate_source_id_count": None,
            "invalid_json_line_count": None,
            "status": "not_applicable",
            "errors": [],
        }
    path = repo_root / system.prompt_batch
    parse_result = read_jsonl_lenient(path)
    errors: list[str] = []
    if not parse_result["exists"]:
        return {
            "path": project_relative_path(path, repo_root),
            "exists": False,
            "task_count": 0,
            "valid_task_count": 0,
            "missing_source_id_count": len(selected_ids),
            "duplicate_source_id_count": 0,
            "invalid_json_line_count": 0,
            "status": "missing",
            "errors": ["prompt_batch_missing"],
        }
    records = [record for record in parse_result["records"] if isinstance(record, dict)]
    valid_records = [
        record
        for record in records
        if str(record.get("source_id")) in selected_ids
        and record.get("system_id") == system.system_id
        and isinstance(record.get("messages"), list)
        and isinstance(record.get("expected_output_contract"), dict)
    ]
    source_counts = Counter(str(record.get("source_id")) for record in valid_records)
    duplicate_count = sum(count - 1 for count in source_counts.values() if count > 1)
    missing_count = len(selected_ids - set(source_counts))
    if parse_result["invalid_json_line_count"]:
        errors.append("prompt_batch_invalid_json")
    if len(valid_records) != len(records):
        errors.append("prompt_batch_invalid_task_shape")
    if duplicate_count:
        errors.append("prompt_batch_duplicate_source_ids")
    if missing_count:
        errors.append("prompt_batch_missing_source_ids")
    return {
        "path": project_relative_path(path, repo_root),
        "exists": True,
        "task_count": parse_result["line_count"],
        "valid_task_count": len(valid_records),
        "missing_source_id_count": missing_count,
        "duplicate_source_id_count": duplicate_count,
        "invalid_json_line_count": parse_result["invalid_json_line_count"],
        "status": "ready" if not errors else "needs_revision",
        "errors": errors,
    }


def run_metadata_validation(
    *,
    system: SystemDefinition,
    repo_root: Path,
    output_exists: bool,
) -> dict[str, Any]:
    path = repo_root / system_run_metadata_path(system)
    parse_result = read_json_lenient(path)
    errors: list[str] = []
    warnings: list[str] = []
    if not parse_result["exists"]:
        return {
            "path": project_relative_path(path, repo_root),
            "exists": False,
            "status": "missing" if system.requires_llm or output_exists else "optional_missing",
            "errors": [],
            "warnings": ["run_metadata_missing"],
        }
    payload = parse_result["payload"] or {}
    if parse_result["error"]:
        errors.append("run_metadata_invalid_json")
    if payload.get("system_id") != system.system_id:
        errors.append("run_metadata_system_id_mismatch")
    if output_exists and payload.get("run_status") not in {"completed", "reviewed"}:
        errors.append("run_metadata_run_status_not_completed")
    for field in ("prediction_output", "input_records"):
        if output_exists and not payload.get(field):
            errors.append(f"run_metadata_missing_{field}")
    return {
        "path": project_relative_path(path, repo_root),
        "exists": True,
        "status": "ready" if not errors else "needs_revision",
        "errors": errors,
        "warnings": warnings,
    }


def validate_prediction_output_system(
    *,
    system: SystemDefinition,
    repo_root: Path,
    selected_ids: set[str],
) -> dict[str, Any]:
    output_path = repo_root / system.expected_output
    parse_result = read_jsonl_lenient(output_path)
    prompt_status = prompt_batch_validation(
        system=system,
        repo_root=repo_root,
        selected_ids=selected_ids,
    )
    metadata_status = run_metadata_validation(
        system=system,
        repo_root=repo_root,
        output_exists=parse_result["exists"],
    )
    errors: list[str] = []
    pending: list[str] = []
    json_metrics = None

    if prompt_status["status"] == "needs_revision":
        errors.extend(prompt_status["errors"])
    elif prompt_status["status"] == "missing":
        pending.append("prompt_batch_missing")

    if not parse_result["exists"]:
        pending.append("prediction_output_missing")
    else:
        json_metrics = prediction_json_metrics(parse_result=parse_result, selected_ids=selected_ids)
        if json_metrics["invalid_json_line_count"]:
            errors.append("prediction_output_invalid_json_lines")
        if json_metrics["invalid_payload_count"]:
            errors.append("prediction_output_invalid_payload_shape")
        if json_metrics["duplicate_output_record_count"]:
            errors.append("prediction_output_duplicate_source_ids")
        if json_metrics["missing_output_record_count"]:
            errors.append("prediction_output_missing_source_ids")

    if metadata_status["status"] == "needs_revision":
        errors.extend(metadata_status["errors"])
    elif metadata_status["status"] == "missing":
        pending.append("run_metadata_missing")

    if errors:
        status = "needs_revision"
    elif pending:
        status = "pending_required_outputs"
    else:
        status = "ready_for_scoring"

    return {
        "system_id": system.system_id,
        "label": system.label,
        "expected_output": project_relative_path(output_path, repo_root),
        "output_exists": parse_result["exists"],
        "prompt_batch": prompt_status,
        "run_metadata": metadata_status,
        "json_metrics": json_metrics,
        "status": status,
        "errors": errors,
        "pending": pending,
    }


def build_prediction_output_validation_report(
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    system_reports = [
        validate_prediction_output_system(
            system=system,
            repo_root=repo_root,
            selected_ids=selected_ids,
        )
        for system in SYSTEMS
    ]
    error_count = sum(len(report["errors"]) for report in system_reports)
    pending_count = sum(len(report["pending"]) for report in system_reports)
    if error_count:
        status = "needs_revision"
    elif pending_count:
        status = "pending_required_outputs"
    else:
        status = "ready_for_scoring"
    return {
        "source_family": "nasa_atmonto_prediction_output_validation",
        "status": status,
        "selected_source_id_count": len(selected_ids),
        "systems": system_reports,
        "error_count": error_count,
        "pending_count": pending_count,
        "completion_gate": (
            "Prediction outputs are usable for formal scoring only when every system status is "
            "ready_for_scoring."
        ),
    }


def prediction_output_validation_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Prediction Output Validation",
        "",
        f"- Status: `{report['status']}`",
        f"- Selected source IDs: {report['selected_source_id_count']}",
        f"- Errors: {report['error_count']}",
        f"- Pending items: {report['pending_count']}",
        "",
        "## Completion Gate",
        "",
        f"- {report['completion_gate']}",
        "",
        "## Systems",
        "",
        "| System | Status | Output | Run Metadata | JSON adherence | Missing records | Pending | Errors |",
        "| --- | --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    for system in report["systems"]:
        json_metrics = system.get("json_metrics") or {}
        lines.append(
            "| "
            f"`{system['system_id']}` | "
            f"`{system['status']}` | "
            f"`{system['output_exists']}` | "
            f"`{system['run_metadata']['exists']}` | "
            f"{json_metrics.get('json_adherence')} | "
            f"{json_metrics.get('missing_output_record_count')} | "
            f"`{', '.join(system['pending'])}` | "
            f"`{', '.join(system['errors'])}` |"
        )
    return "\n".join(lines) + "\n"


def run_prediction_output_validation(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    report = build_prediction_output_validation_report(repo_root)
    write_json(repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_JSON, report)
    (repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD).write_text(
        prediction_output_validation_markdown(report),
        encoding="utf-8",
    )
    return {
        "report_json": project_relative_path(
            repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_JSON,
            repo_root,
        ),
        "report_markdown": project_relative_path(
            repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD,
            repo_root,
        ),
        "status": report["status"],
        "error_count": report["error_count"],
        "pending_count": report["pending_count"],
    }


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
    predicates = sorted({key[1] for key in gold_keys | prediction_keys})
    rows: list[dict[str, Any]] = []
    for predicate in predicates:
        gold_for_predicate = {key for key in gold_keys if key[1] == predicate}
        pred_for_predicate = {key for key in prediction_keys if key[1] == predicate}
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


def score_system_predictions(
    *,
    system: SystemDefinition,
    repo_root: Path,
    selected_ids: set[str],
    input_records: list[dict[str, Any]],
    gold_records: list[dict[str, Any]],
    schema_slice: dict[str, Any],
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
    return {
        **base,
        "available": True,
        "reason": None,
        "json_metrics": json_metrics,
        "structural_metrics": structural_metrics(validation_results),
        "semantic_metrics": semantic,
        "property_level_semantic_metrics": (
            property_level_semantic_metrics(
                predictions=prediction_facts,
                gold_records=gold_records,
            )
            if semantic["available"]
            else []
        ),
    }


def build_formal_experiment_score_report(
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    input_records = read_jsonl(repo_root / FORMAL_INPUT_RECORDS_PATH)
    schema_slice = read_json(repo_root / SCHEMA_SLICE_PATH)
    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    gold_status = gold_annotation_status(gold_records)
    system_scores = [
        score_system_predictions(
            system=system,
            repo_root=repo_root,
            selected_ids=selected_ids,
            input_records=input_records,
            gold_records=gold_records,
            schema_slice=schema_slice,
        )
        for system in SYSTEMS
    ]
    missing_inputs: list[str] = []
    if not gold_status["complete"]:
        missing_inputs.append("completed manual gold annotations for 100 sampled advisories")
    for score in system_scores:
        if not score["output_exists"]:
            missing_inputs.append(f"{score['system_id']} predictions at {score['expected_output']}")
    if any(score["semantic_metrics"] and not score["semantic_metrics"]["available"] for score in system_scores):
        missing_inputs.append("manual semantic metrics require reviewed gold facts")

    return {
        "source_family": "nasa_atmonto_formal_experiment_scoring",
        "status": "scored" if not missing_inputs else "pending_required_inputs",
        "protocol": "docs/experiment_protocol.md",
        "gold_status": gold_status,
        "systems": system_scores,
        "missing_required_inputs": missing_inputs,
        "metrics_reported": [
            "json_adherence",
            "schema_violation_rate",
            "triple_precision",
            "triple_recall",
            "triple_f1",
            "repair_success_rate",
            "manual_semantic_correctness",
        ],
        "claim_boundary": (
            "Formal metrics are descriptive until all four systems have predictions and "
            "manual gold annotations are complete."
        ),
    }


def score_report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Formal Experiment Scoring",
        "",
        f"- Status: `{report['status']}`",
        f"- Protocol: `{report['protocol']}`",
        "",
        "## Gold Status",
        "",
    ]
    gold = report["gold_status"]
    lines.extend(
        [
            f"- Records: {gold['record_count']}",
            f"- Reviewed records: {gold['reviewed_record_count']}",
            f"- Pending records: {gold['pending_record_count']}",
            f"- Complete: `{gold['complete']}`",
            "",
            "## System Metrics",
            "",
            "| System | Output | JSON adherence | Candidate facts | Accepted | Rejected | Schema violation rate | Repair success | Semantic metrics |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for score in report["systems"]:
        json_metrics = score.get("json_metrics") or {}
        structural = score.get("structural_metrics") or {}
        semantic = score.get("semantic_metrics") or {}
        semantic_text = (
            f"P={semantic.get('precision')}, R={semantic.get('recall')}, F1={semantic.get('f1')}"
            if semantic.get("available")
            else f"pending:{semantic.get('reason') or score.get('reason')}"
        )
        lines.append(
            "| "
            f"`{score['system_id']}` | "
            f"`{score['output_exists']}` | "
            f"{json_metrics.get('json_adherence')} | "
            f"{structural.get('candidate_fact_count')} | "
            f"{structural.get('accepted_fact_count')} | "
            f"{structural.get('rejected_fact_count')} | "
            f"{structural.get('schema_violation_rate')} | "
            f"{structural.get('repair_success_rate')} | "
            f"{semantic_text} |"
        )
    lines.extend(["", "## Missing Required Inputs", ""])
    for item in report["missing_required_inputs"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Boundary", "", f"- {report['claim_boundary']}"])
    return "\n".join(lines) + "\n"


def build_formal_experiment_readiness(
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    s0_payloads = read_jsonl(repo_root / S0_CANDIDATES_PATH)
    s0_validations_all = read_jsonl(repo_root / S0_VALIDATED_PATH)

    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    s0_validations = selected_validations(s0_validations_all, selected_ids)
    s0_predictions = accepted_prediction_facts(s0_validations)
    gold_status = gold_annotation_status(gold_records)

    formal_input_status = {
        "input_records": project_relative_path(repo_root / FORMAL_INPUT_RECORDS_PATH, repo_root),
        "input_records_exists": (repo_root / FORMAL_INPUT_RECORDS_PATH).exists(),
        "system_specs": project_relative_path(repo_root / FORMAL_SYSTEM_SPECS_PATH, repo_root),
        "system_specs_exists": (repo_root / FORMAL_SYSTEM_SPECS_PATH).exists(),
    }

    system_output_status: list[dict[str, Any]] = []
    for system in SYSTEMS:
        output_path = repo_root / system.expected_output
        prompt_path = repo_root / system.prompt_batch if system.prompt_batch else None
        system_output_status.append(
            {
                "system_id": system.system_id,
                "expected_output": project_relative_path(output_path, repo_root),
                "exists": output_path.exists(),
                "prompt_batch": (
                    project_relative_path(prompt_path, repo_root) if prompt_path else None
                ),
                "prompt_batch_exists": prompt_path.exists() if prompt_path else None,
                "required_before_formal_scoring": system.system_id != "S0_rule_only",
            }
        )

    s0_structural = structural_metrics(s0_validations)
    s0_json = json_adherence_from_payloads(s0_payloads, selected_ids)
    s0_semantic = semantic_metrics(predictions=s0_predictions, gold_records=gold_records)

    missing_inputs = []
    if not formal_input_status["input_records_exists"]:
        missing_inputs.append("formal input records for the 100 sampled advisories")
    if not formal_input_status["system_specs_exists"]:
        missing_inputs.append("formal system specs for S0-S3")
    if not gold_status["complete"]:
        missing_inputs.append("completed manual gold annotations for 100 sampled advisories")
    for item in system_output_status:
        if item["prompt_batch"] and not item["prompt_batch_exists"]:
            missing_inputs.append(f"{item['system_id']} prompt batch at {item['prompt_batch']}")
        if item["required_before_formal_scoring"] and not item["exists"]:
            missing_inputs.append(f"{item['system_id']} predictions at {item['expected_output']}")

    return {
        "source_family": "nasa_atmonto_formal_experiment_readiness",
        "status": "ready_for_manual_gold_and_llm_runs" if missing_inputs else "ready_for_scoring",
        "protocol": "docs/experiment_protocol.md",
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "gold_status": gold_status,
        "formal_input_status": formal_input_status,
        "systems": system_definitions(repo_root),
        "system_output_status": system_output_status,
        "current_s0_rule_only_structural_metrics": {
            **s0_json,
            **s0_structural,
            "semantic_metrics": s0_semantic,
        },
        "metrics_defined": [
            "json_adherence",
            "schema_violation_rate",
            "triple_precision",
            "triple_recall",
            "triple_f1",
            "repair_success_rate",
            "manual_semantic_correctness",
        ],
        "missing_required_inputs": missing_inputs,
        "claim_boundary": (
            "This readiness report does not claim formal extraction effectiveness until "
            "manual gold annotations and S1-S3 outputs are present."
        ),
    }


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Formal Experiment Readiness",
        "",
        f"- Status: `{report['status']}`",
        f"- Protocol: `{report['protocol']}`",
        f"- Gold manifest: `{report['gold_manifest']}`",
        f"- Gold template: `{report['gold_template']}`",
        "",
        "## Gold Status",
        "",
    ]
    gold = report["gold_status"]
    lines.extend(
        [
            f"- Records: {gold['record_count']}",
            f"- Reviewed records: {gold['reviewed_record_count']}",
            f"- Pending records: {gold['pending_record_count']}",
            f"- Complete: `{gold['complete']}`",
            f"- Status counts: `{json.dumps(gold['status_counts'], sort_keys=True)}`",
            "",
            "## Formal Inputs",
            "",
            f"- Input records: `{report['formal_input_status']['input_records']}`",
            f"- Input records exists: `{report['formal_input_status']['input_records_exists']}`",
            f"- System specs: `{report['formal_input_status']['system_specs']}`",
            f"- System specs exists: `{report['formal_input_status']['system_specs_exists']}`",
            "",
            "## Systems",
            "",
        ]
    )
    output_status = {item["system_id"]: item for item in report["system_output_status"]}
    for system in report["systems"]:
        status = output_status[system["system_id"]]
        lines.append(
            f"- `{system['system_id']}`: {system['label']} "
            f"(LLM={system['requires_llm']}, schema={system['uses_schema_slice']}, "
            f"repair={system['uses_validator_repair']}, "
            f"prompt_ready={status['prompt_batch_exists']}, output_ready={status['exists']})"
        )
    lines.extend(["", "## Current S0 Structural Metrics", ""])
    s0 = report["current_s0_rule_only_structural_metrics"]
    for key in (
        "attempted_record_count",
        "valid_json_payload_count",
        "json_adherence",
        "candidate_fact_count",
        "accepted_fact_count",
        "rejected_fact_count",
        "schema_violation_rate",
        "repair_success_rate",
    ):
        lines.append(f"- `{key}`: {s0.get(key)}")
    lines.extend(["", "## Missing Required Inputs", ""])
    for item in report["missing_required_inputs"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            f"- {report['claim_boundary']}",
        ]
    )
    return "\n".join(lines) + "\n"


def run_formal_experiment_readiness(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    prepare_inputs: bool = True,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    prepared = prepare_formal_experiment_inputs(repo_root) if prepare_inputs else None
    gold_worklist = build_gold_review_worklist(repo_root)
    gold_validation = build_gold_annotation_validation_report(repo_root)
    prediction_validation = build_prediction_output_validation_report(repo_root)
    report = build_formal_experiment_readiness(repo_root)
    score_report = build_formal_experiment_score_report(repo_root)
    write_json(repo_root / GOLD_REVIEW_WORKLIST_JSON, gold_worklist)
    write_json(repo_root / GOLD_VALIDATION_REPORT_JSON, gold_validation)
    write_json(repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_JSON, prediction_validation)
    write_json(repo_root / READINESS_REPORT_JSON, report)
    write_json(repo_root / SCORING_REPORT_JSON, score_report)
    (repo_root / GOLD_REVIEW_WORKLIST_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_REVIEW_WORKLIST_MD).write_text(
        gold_review_worklist_markdown(gold_worklist),
        encoding="utf-8",
    )
    (repo_root / GOLD_VALIDATION_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_VALIDATION_REPORT_MD).write_text(
        gold_validation_markdown(gold_validation),
        encoding="utf-8",
    )
    (repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD).write_text(
        prediction_output_validation_markdown(prediction_validation),
        encoding="utf-8",
    )
    (repo_root / READINESS_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / READINESS_REPORT_MD).write_text(markdown_report(report), encoding="utf-8")
    (repo_root / SCORING_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / SCORING_REPORT_MD).write_text(
        score_report_markdown(score_report),
        encoding="utf-8",
    )
    return {
        "prepared_inputs": prepared,
        "gold_review_worklist_json": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLIST_JSON,
            repo_root,
        ),
        "gold_review_worklist_markdown": project_relative_path(
            repo_root / GOLD_REVIEW_WORKLIST_MD,
            repo_root,
        ),
        "gold_validation_report_json": project_relative_path(
            repo_root / GOLD_VALIDATION_REPORT_JSON,
            repo_root,
        ),
        "gold_validation_report_markdown": project_relative_path(
            repo_root / GOLD_VALIDATION_REPORT_MD,
            repo_root,
        ),
        "prediction_output_validation_report_json": project_relative_path(
            repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_JSON,
            repo_root,
        ),
        "prediction_output_validation_report_markdown": project_relative_path(
            repo_root / PREDICTION_OUTPUT_VALIDATION_REPORT_MD,
            repo_root,
        ),
        "report_json": project_relative_path(repo_root / READINESS_REPORT_JSON, repo_root),
        "report_markdown": project_relative_path(repo_root / READINESS_REPORT_MD, repo_root),
        "scoring_report_json": project_relative_path(repo_root / SCORING_REPORT_JSON, repo_root),
        "scoring_report_markdown": project_relative_path(repo_root / SCORING_REPORT_MD, repo_root),
        "gold_validation_status": gold_validation["status"],
        "prediction_output_validation_status": prediction_validation["status"],
        "status": report["status"],
        "scoring_status": score_report["status"],
        "missing_required_inputs": report["missing_required_inputs"],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare NASA ATMONTO formal experiment inputs and readiness report."
    )
    parser.add_argument("--repo-root", default=PROJECT_ROOT, type=Path)
    parser.add_argument(
        "--skip-prepare-inputs",
        action="store_true",
        help="Only rebuild the readiness report; do not regenerate input and prompt batches.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = run_formal_experiment_readiness(
        args.repo_root,
        prepare_inputs=not args.skip_prepare_inputs,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"NASA ATMONTO formal experiment readiness failed: {exc}", file=sys.stderr)
        raise
