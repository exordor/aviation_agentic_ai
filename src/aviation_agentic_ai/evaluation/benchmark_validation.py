from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import project_relative_path


NO_ANSWER_LEVELS = {"no_answer", "none", "unsupported", "insufficient_evidence"}
CORE_REQUIRED_FIELDS = ("cq_id", "question", "question_type", "answer_key", "key_entities")
SUPPORTED_REQUIRED_FIELDS = (
    "source_document",
    "source_page",
    "gold_level",
    "expected_abstention",
    "expected_chunk_ids",
    "evidence_spans",
    "review",
)


class BenchmarkValidationReadError(ValueError):
    """Raised when benchmark validation input artifacts cannot be parsed."""


def normalize_evidence_text(text: str) -> str:
    """Normalize whitespace while preserving source casing."""
    return " ".join(str(text).split())


def read_benchmark_payload(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BenchmarkValidationReadError(
            f"Invalid benchmark payload JSON in {project_relative_path(source)}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise BenchmarkValidationReadError(
            f"Benchmark payload must be a JSON object: {project_relative_path(source)}"
        )
    labels = payload.get("labels")
    if not isinstance(labels, list):
        raise BenchmarkValidationReadError(
            f"Benchmark payload has non-list labels: {project_relative_path(source)}"
        )
    return payload


def _read_chunks(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    chunks: list[dict[str, Any]] = []
    for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
            if not isinstance(item, dict):
                raise TypeError("expected JSON object")
            int(item.get("page", -1))
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise BenchmarkValidationReadError(
                f"Invalid chunk validation JSONL record in {project_relative_path(source)} "
                f"at line {line_number}: {exc}"
            ) from exc
        chunks.append(item)
    return chunks


def _load_chunks_by_page(chunks_paths: list[str | Path] | tuple[str | Path, ...]) -> dict[int, list[dict[str, Any]]]:
    chunks_by_page: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for chunks_path in chunks_paths:
        for chunk in _read_chunks(chunks_path):
            chunks_by_page[int(chunk.get("page", -1))].append(chunk)
    return dict(chunks_by_page)


def _field_missing(label: dict[str, Any], field: str) -> bool:
    if field not in label:
        return True
    value = label[field]
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if field in {"key_entities", "expected_chunk_ids", "evidence_spans"}:
        return not isinstance(value, list) or len(value) == 0
    return False


def _is_no_answer(label: dict[str, Any]) -> bool:
    level = str(label.get("gold_level", "")).strip().lower()
    return bool(label.get("expected_abstention", False)) or level in NO_ANSWER_LEVELS


def _span_matches_page_chunks(
    span: dict[str, Any],
    chunks_by_page: dict[int, list[dict[str, Any]]],
) -> bool:
    try:
        page = int(span.get("page", -1))
    except (TypeError, ValueError):
        return False
    needle = normalize_evidence_text(str(span.get("text", "")))
    if not needle:
        return False
    return any(
        needle in normalize_evidence_text(str(chunk.get("text", "")))
        for chunk in chunks_by_page.get(page, [])
    )


def _duplicate_warnings(values: dict[str, list[str]], label: str) -> list[str]:
    warnings: list[str] = []
    for value, cq_ids in sorted(values.items()):
        if value and len(cq_ids) > 1:
            warnings.append(f"Duplicate {label} used by {', '.join(sorted(cq_ids))}: {value[:120]}")
    return warnings


def validate_benchmark(
    gold_labels_path: str | Path,
    chunks_paths: list[str | Path] | tuple[str | Path, ...],
    *,
    min_labels: int = 100,
) -> dict[str, Any]:
    payload = read_benchmark_payload(gold_labels_path)
    labels = [item for item in payload.get("labels", []) if isinstance(item, dict)]
    chunks_by_page = _load_chunks_by_page(chunks_paths)

    errors: list[str] = []
    warnings: list[str] = []
    missing_field_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    gold_level_counts: Counter[str] = Counter()
    cq_ids: Counter[str] = Counter()
    questions: dict[str, list[str]] = defaultdict(list)
    evidence_texts: dict[str, list[str]] = defaultdict(list)
    evidence_spans_checked = 0
    evidence_span_failures = 0
    supported_total = 0
    no_answer_total = 0
    span_level_count = 0

    if len(labels) < min_labels:
        errors.append(f"Benchmark has {len(labels)} labels; expected at least {min_labels}.")

    for index, label in enumerate(labels, start=1):
        cq_id = str(label.get("cq_id") or label.get("id") or f"<missing-{index}>")
        cq_ids[cq_id] += 1
        question_type = str(label.get("question_type", "")).strip()
        category_counts[question_type or "<missing>"] += 1
        gold_level = str(label.get("gold_level", "")).strip().lower()
        gold_level_counts[gold_level or "<missing>"] += 1
        if gold_level == "span":
            span_level_count += 1

        question_key = normalize_evidence_text(str(label.get("question", ""))).lower()
        questions[question_key].append(cq_id)

        no_answer = _is_no_answer(label)
        required_fields = list(CORE_REQUIRED_FIELDS)
        if not no_answer:
            required_fields.extend(SUPPORTED_REQUIRED_FIELDS)
        for field in required_fields:
            if _field_missing(label, field):
                missing_field_counts[field] += 1
                errors.append(f"{cq_id}: missing required field `{field}`.")

        if no_answer:
            no_answer_total += 1
            if gold_level != "no_answer":
                errors.append(f"{cq_id}: no-answer labels must use gold_level `no_answer`.")
            if bool(label.get("expected_abstention", False)) is not True:
                errors.append(f"{cq_id}: no-answer labels must set expected_abstention=true.")
            if int(label.get("source_page", 0)) != -1:
                errors.append(f"{cq_id}: no-answer labels must set source_page=-1.")
            if label.get("expected_chunk_ids", []) != []:
                errors.append(f"{cq_id}: no-answer labels must have empty expected_chunk_ids.")
            if label.get("evidence_spans", []) != []:
                errors.append(f"{cq_id}: no-answer labels must have empty evidence_spans.")
            continue

        supported_total += 1
        if bool(label.get("expected_abstention", False)):
            errors.append(f"{cq_id}: supported labels must set expected_abstention=false.")
        spans = label.get("evidence_spans", [])
        if not isinstance(spans, list) or not spans:
            errors.append(f"{cq_id}: supported labels must include non-empty evidence_spans.")
            continue
        for span in spans:
            if not isinstance(span, dict):
                errors.append(f"{cq_id}: evidence span must be an object.")
                evidence_span_failures += 1
                continue
            evidence_spans_checked += 1
            span_text = normalize_evidence_text(str(span.get("text", "")))
            evidence_texts[span_text].append(cq_id)
            if not _span_matches_page_chunks(span, chunks_by_page):
                evidence_span_failures += 1
                errors.append(
                    f"{cq_id}: evidence span does not appear in any source chunk on page "
                    f"{span.get('page')}: {span_text[:120]}"
                )

    for cq_id, count in sorted(cq_ids.items()):
        if count > 1:
            errors.append(f"Duplicate cq_id `{cq_id}` appears {count} times.")

    warnings.extend(_duplicate_warnings(questions, "question"))
    warnings.extend(_duplicate_warnings(evidence_texts, "evidence span"))

    chunk_paths = [project_relative_path(path) for path in chunks_paths]
    result = {
        "valid": not errors,
        "validation_passed": not errors,
        "errors_total": len(errors),
        "warnings_total": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "metadata": {
            "gold_labels_path": project_relative_path(gold_labels_path),
            "chunks_paths": chunk_paths,
            "label_set": payload.get("label_set", ""),
            "review_status": payload.get("review_status", ""),
            "notes": payload.get("notes", ""),
            "label_distribution": payload.get("label_distribution", {}),
            "labels_total": len(labels),
            "supported_total": supported_total,
            "no_answer_total": no_answer_total,
            "span_level_count": span_level_count,
            "category_counts": dict(sorted(category_counts.items())),
            "gold_level_counts": dict(sorted(gold_level_counts.items())),
            "missing_field_counts": dict(sorted(missing_field_counts.items())),
            "evidence_span_validation": {
                "checked": evidence_spans_checked,
                "passed": evidence_spans_checked - evidence_span_failures,
                "failed": evidence_span_failures,
                "pass": evidence_span_failures == 0,
            },
        },
    }
    return result
