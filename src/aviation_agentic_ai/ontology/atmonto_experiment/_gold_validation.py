"""AUTO-SPLIT from ontology/atmonto_experiment.py. See git history."""
from __future__ import annotations

from typing import Any
from collections import Counter
from pathlib import Path

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path

from ._io import (
    _jsonl_semantically_equal,
    compact_text,
    file_sha256,
    read_json,
    read_jsonl,
    write_json,
    write_jsonl,
)
from ._system_defs import (
    ALLOWED_REJECTION_ADJUDICATIONS,
    GOLD_FREEZE_REPORT_JSON,
    GOLD_FREEZE_REPORT_MD,
    GOLD_MANIFEST_PATH,
    GOLD_REVIEWED_PATH,
    GOLD_TEMPLATE_PATH,
    GOLD_VALIDATION_REPORT_JSON,
    GOLD_VALIDATION_REPORT_MD,
    PENDING_GOLD_STATUS,
    REVIEWED_GOLD_STATUS,
    REVIEW_CHECKLIST_FIELDS,
)
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

def review_checklist_template(value: bool = False) -> dict[str, bool]:
    return {field: value for field in REVIEW_CHECKLIST_FIELDS}

def incomplete_review_checklist_fields(checklist: Any) -> list[str]:
    if not isinstance(checklist, dict):
        return list(REVIEW_CHECKLIST_FIELDS)
    return [field for field in REVIEW_CHECKLIST_FIELDS if checklist.get(field) is not True]

def validate_review_checklist(record: dict[str, Any]) -> list[dict[str, Any]]:
    annotation = record.get("gold_annotation", {})
    incomplete = incomplete_review_checklist_fields(annotation.get("review_checklist"))
    if not incomplete:
        return []
    return [
        {
            "sample_id": record.get("sample_id"),
            "source_id": record.get("source_id"),
            "path": "gold_annotation.review_checklist",
            "error": "incomplete_review_checklist",
            "fields": incomplete,
        }
    ]

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
        errors.extend(validate_review_checklist(record))
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
    return "\n".join(lines).rstrip() + "\n"

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

def build_gold_freeze_status(
    repo_root: str | Path = PROJECT_ROOT,
    output_path: str | Path = GOLD_REVIEWED_PATH,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    output = Path(output_path)
    if output.is_absolute():
        output = output.relative_to(repo_root)
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    selected_source_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    validation = validate_gold_annotation_records(
        gold_records=gold_records,
        selected_source_ids=selected_source_ids,
    )
    ready = validation["status"] == "ready_for_scoring"
    output_file = repo_root / output
    output_exists = output_file.exists()
    output_matches_template = output_exists and _jsonl_semantically_equal(read_jsonl(output_file), gold_records)
    status = "blocked_pending_review"
    if ready and output_matches_template:
        status = "frozen"
    elif ready:
        status = "ready_to_freeze"
    return {
        "source_family": "nasa_atmonto_gold_freeze_status",
        "status": status,
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        "reviewed_gold_output": project_relative_path(output_file, repo_root),
        "selected_source_id_count": len(selected_source_ids),
        "record_count": validation["record_count"],
        "validation_status": validation["status"],
        "reviewed_record_count": validation["reviewed_record_count"],
        "pending_record_count": validation["pending_record_count"],
        "error_count": validation["error_count"],
        "warning_count": validation["warning_count"],
        "output_exists": output_exists,
        "output_matches_template": output_matches_template,
        "output_sha256": file_sha256(output_file) if output_exists else None,
        "completion_gate": (
            "The reviewed gold JSONL may be frozen only when gold annotation validation "
            "status is ready_for_scoring."
        ),
    }

def gold_freeze_status_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# NASA ATMONTO Gold Freeze Status",
            "",
            f"- Status: `{report['status']}`",
            f"- Validation status: `{report['validation_status']}`",
            f"- Gold template: `{report['gold_template']}`",
            f"- Reviewed gold output: `{report['reviewed_gold_output']}`",
            f"- Records: {report['record_count']}",
            f"- Reviewed records: {report['reviewed_record_count']}",
            f"- Pending records: {report['pending_record_count']}",
            f"- Errors: {report['error_count']}",
            f"- Warnings: {report['warning_count']}",
            f"- Output exists: `{report['output_exists']}`",
            f"- Output matches template: `{report['output_matches_template']}`",
            f"- Output SHA-256: `{report['output_sha256']}`",
            "",
            "## Completion Gate",
            "",
            f"- {report['completion_gate']}",
        ]
    ) + "\n"

def freeze_reviewed_gold_set(
    repo_root: str | Path = PROJECT_ROOT,
    output_path: str | Path = GOLD_REVIEWED_PATH,
) -> dict[str, Any]:
    from ._llm_runtime import utc_timestamp
    repo_root = Path(repo_root).resolve()
    output = Path(output_path)
    if output.is_absolute():
        output = output.relative_to(repo_root)
    status = build_gold_freeze_status(repo_root, output)
    if status["status"] != "ready_to_freeze":
        write_json(repo_root / GOLD_FREEZE_REPORT_JSON, status)
        (repo_root / GOLD_FREEZE_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
        (repo_root / GOLD_FREEZE_REPORT_MD).write_text(
            gold_freeze_status_markdown(status),
            encoding="utf-8",
        )
        return status

    records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    output_file = repo_root / output
    write_jsonl(output_file, records)
    frozen_status = {
        **build_gold_freeze_status(repo_root, output),
        "status": "frozen",
        "frozen_at": utc_timestamp(),
        "output_exists": True,
        "output_sha256": file_sha256(output_file),
    }
    write_json(repo_root / GOLD_FREEZE_REPORT_JSON, frozen_status)
    (repo_root / GOLD_FREEZE_REPORT_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / GOLD_FREEZE_REPORT_MD).write_text(
        gold_freeze_status_markdown(frozen_status),
        encoding="utf-8",
    )
    return frozen_status
