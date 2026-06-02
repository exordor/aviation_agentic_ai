from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.reporting.io import (
    normalize_report_text,
    read_json_object,
)
from aviation_agentic_ai.reporting.nasa_atmonto_cq import normalize_atmonto_predicate
from aviation_agentic_ai.reporting.nasa_atmonto_cq_queries import (
    QUERY_TEMPLATES,
    build_cq_query_manifest,
)


def resolve_path(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def read_jsonl_objects(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"Expected object at {project_relative_path(path)}:{line_number}")
        records.append(payload)
    return records


def local_name(value: object) -> str:
    text = str(value or "").strip()
    for separator in ("#", ":", "/"):
        if separator in text:
            text = text.rsplit(separator, 1)[1]
    return text


def predicate_name(predicate: object) -> str:
    return local_name(normalize_atmonto_predicate(predicate))


def answer_value(fact: dict[str, Any]) -> str:
    value = fact.get("object_label")
    if value in (None, ""):
        value = fact.get("value", fact.get("object"))
    return str(local_name(value)).strip()


def fact_status_accepted(fact: dict[str, Any]) -> bool:
    status = str(fact.get("validator_status") or fact.get("status") or "").lower()
    if not status:
        return True
    return "accepted" in status and "rejected" not in status


def source_id(record: dict[str, Any]) -> str:
    annotation = record.get("gold_annotation") if isinstance(record.get("gold_annotation"), dict) else {}
    return str(
        record.get("source_id")
        or record.get("advisory_source_id")
        or annotation.get("source_id")
        or record.get("sample_id")
        or ""
    )


def chunk_id(source_identifier: str) -> str:
    safe = "".join(character.lower() if character.isalnum() else "-" for character in source_identifier)
    safe = "-".join(part for part in safe.split("-") if part)
    return f"atcscc-{safe}-p1-c1"


def dedupe_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for item in items:
        key = (
            str(item.get("source_id") or ""),
            str(item.get("predicate") or ""),
            normalize_report_text(item.get("value") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def load_query_manifest(
    root: Path,
    query_manifest_path: str | Path | None,
    default_query_manifest_path: Path,
) -> dict[str, Any]:
    if query_manifest_path is None:
        manifest_path = resolve_path(root, default_query_manifest_path)
    else:
        manifest_path = resolve_path(root, query_manifest_path)
    return read_json_object(manifest_path) if manifest_path.exists() else build_cq_query_manifest()


def query_templates(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    templates = manifest.get("templates")
    if isinstance(templates, list) and templates:
        return [template for template in templates if isinstance(template, dict)]
    return [{**template, "predicates": list(template["predicates"])} for template in QUERY_TEMPLATES]


def build_answer_eval_benchmark(
    *,
    gold_records: list[dict[str, Any]],
    query_manifest: dict[str, Any],
    max_cases_per_template: int = 3,
) -> dict[str, Any]:
    labels: list[dict[str, Any]] = []
    for template in query_templates(query_manifest):
        predicates = {predicate_name(predicate) for predicate in template.get("predicates", [])}
        candidates = _labels_for_template(template, predicates, gold_records)
        labels.extend(candidates[:max_cases_per_template])
    return {
        "source_family": "nasa_atmonto_answer_eval_benchmark",
        "status": "ready",
        "metadata": {
            "template_count": len(query_templates(query_manifest)),
            "label_count": len(labels),
            "max_cases_per_template": max_cases_per_template,
            "selection_policy": "first_source_bounded_reviewed_case_per_template",
            "boundary": "Retrospective ATCSCC advisory answer evaluation only; no live operational use.",
        },
        "labels": labels,
    }


def _labels_for_template(
    template: dict[str, Any],
    predicates: set[str],
    gold_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    labels: list[dict[str, Any]] = []
    is_abstention_template = str(template.get("id")) == "QT-A01-ABSTENTION-FIELDS"
    for record in gold_records:
        record_source_id = source_id(record)
        if not record_source_id:
            continue
        source_text = str(record.get("source_text") or "")
        answer_items = _answer_items_from_record(record, predicates)
        absent_predicates = _missing_predicates_from_record(record, predicates)
        expected_abstention = is_abstention_template and bool(absent_predicates)
        if not answer_items and not expected_abstention:
            continue
        labels.append(
            _label_from_items(
                template=template,
                predicates=predicates,
                source_identifier=record_source_id,
                source_text=source_text,
                answer_items=answer_items,
                absent_predicates=absent_predicates if expected_abstention else [],
            )
        )
    return labels


def _label_from_items(
    *,
    template: dict[str, Any],
    predicates: set[str],
    source_identifier: str,
    source_text: str,
    answer_items: list[dict[str, Any]],
    absent_predicates: list[str],
) -> dict[str, Any]:
    expected_evidence = [
        {
            "predicate": item["predicate"],
            "value": item["value"],
            "text": item.get("evidence_text", ""),
            "source_id": item["source_id"],
        }
        for item in answer_items
        if item.get("evidence_text")
    ]
    expected_values = [
        {"predicate": item["predicate"], "value": item["value"]} for item in answer_items
    ]
    answer_set = [f"{item['predicate']}={item['value']}" for item in answer_items]
    if absent_predicates:
        answer_set = [f"absent:{predicate}" for predicate in absent_predicates]
    source_chunk_id = chunk_id(source_identifier)
    return {
        "cq_id": f"{template['id']}::{source_identifier}",
        "template_id": template["id"],
        "cq_ids": list(template.get("cq_ids", [])),
        "source_id": source_identifier,
        "source_document": "ATCSCC advisory",
        "source_page": 1,
        "source_text": source_text,
        "chunk_id": source_chunk_id,
        "question": template["question"],
        "question_type": str(template.get("answer_type", "")),
        "predicates": sorted(predicates),
        "expected_values": expected_values,
        "expected_evidence": expected_evidence,
        "expected_abstention": bool(absent_predicates),
        "absent_predicates": absent_predicates,
        "answer_set": answer_set,
        "evidence_spans": [
            _evidence_span(source_text, evidence["text"])
            for evidence in expected_evidence
            if evidence.get("text")
        ],
        "expected_chunk_ids": [source_chunk_id],
        "answer_key": "; ".join(answer_set),
        "gold_level": "no_answer" if absent_predicates else "span",
        "route": template.get("route", ""),
    }


def _gold_facts(record: dict[str, Any], field_name: str) -> list[dict[str, Any]]:
    annotation = record.get("gold_annotation") if isinstance(record.get("gold_annotation"), dict) else {}
    facts = annotation.get(field_name, []) if isinstance(annotation, dict) else []
    return [fact for fact in facts if isinstance(fact, dict)]


def _answer_items_from_record(
    record: dict[str, Any],
    predicates: set[str],
) -> list[dict[str, Any]]:
    record_source_id = source_id(record)
    items: list[dict[str, Any]] = []
    for fact in _gold_facts(record, "valid_facts"):
        predicate = predicate_name(fact.get("predicate"))
        if predicate not in predicates:
            continue
        value = answer_value(fact)
        if not value:
            continue
        items.append(
            {
                "source_id": str(fact.get("source_id") or record_source_id),
                "predicate": predicate,
                "value": value,
                "evidence_text": str(fact.get("evidence_text") or ""),
                "fact_id": fact.get("fact_id"),
            }
        )
    return dedupe_items(items)


def _missing_predicates_from_record(
    record: dict[str, Any],
    predicates: set[str],
) -> list[str]:
    missing = {
        predicate_name(fact.get("predicate"))
        for fact in _gold_facts(record, "missing_facts")
        if predicate_name(fact.get("predicate")) in predicates
    }
    present = {item["predicate"] for item in _answer_items_from_record(record, predicates)}
    return sorted((predicates - present) | missing)


def _evidence_span(source_text: str, evidence_text: str) -> dict[str, Any]:
    start = source_text.find(evidence_text) if evidence_text else -1
    return {
        "page": 1,
        "text": evidence_text,
        "char_start": start if start >= 0 else None,
        "char_end": start + len(evidence_text) if start >= 0 else None,
    }
