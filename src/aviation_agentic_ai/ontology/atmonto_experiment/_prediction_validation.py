"""AUTO-SPLIT from ontology/atmonto_experiment.py. See git history."""
from __future__ import annotations

from typing import Any
from collections import Counter
from pathlib import Path

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path

from ._io import (
    read_json,
    read_json_lenient,
    read_jsonl_lenient,
    write_json,
)
from ._system_defs import (
    GOLD_MANIFEST_PATH,
    PREDICTION_OUTPUT_VALIDATION_REPORT_JSON,
    PREDICTION_OUTPUT_VALIDATION_REPORT_MD,
    SYSTEMS,
    SystemDefinition,
    system_run_metadata_path,
)

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
        "summary": {
            "normalizer_version": payload.get("normalizer_version"),
            "flattened_schema_object_fact_count": payload.get(
                "flattened_schema_object_fact_count"
            ),
            "reprocessed_from_saved_raw_response": payload.get(
                "reprocessed_from_saved_raw_response",
            ),
            "schema_valid_record_count": payload.get("schema_valid_record_count"),
            "repair_success_record_count": payload.get("repair_success_record_count"),
        },
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
        "| System | Status | Output | Run Metadata | JSON adherence | Missing records | Normalizer | Flattened facts | Schema-valid records | Pending | Errors |",
        "| --- | --- | --- | --- | ---: | ---: | --- | ---: | ---: | --- | --- |",
    ]
    for system in report["systems"]:
        json_metrics = system.get("json_metrics") or {}
        metadata_summary = system.get("run_metadata", {}).get("summary") or {}
        flattened = metadata_summary.get("flattened_schema_object_fact_count")
        schema_valid_records = metadata_summary.get("schema_valid_record_count")
        lines.append(
            "| "
            f"`{system['system_id']}` | "
            f"`{system['status']}` | "
            f"`{system['output_exists']}` | "
            f"`{system['run_metadata']['exists']}` | "
            f"{json_metrics.get('json_adherence')} | "
            f"{json_metrics.get('missing_output_record_count')} | "
            f"`{metadata_summary.get('normalizer_version') or ''}` | "
            f"{'' if flattened is None else flattened} | "
            f"{'' if schema_valid_records is None else schema_valid_records} | "
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
