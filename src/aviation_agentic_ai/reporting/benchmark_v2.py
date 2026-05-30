from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from aviation_agentic_ai.evaluation.benchmark_validation import (
    read_benchmark_payload,
    validate_benchmark,
)
from aviation_agentic_ai.reporting.io import write_json_report


def _sample_labels(payload: dict[str, Any], sample_size: int = 2) -> dict[str, list[dict[str, Any]]]:
    samples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for label in payload.get("labels", []):
        if not isinstance(label, dict):
            continue
        question_type = str(label.get("question_type", "<missing>"))
        if len(samples[question_type]) >= sample_size:
            continue
        samples[question_type].append(
            {
                "cq_id": label.get("cq_id", ""),
                "question": label.get("question", ""),
                "source_page": label.get("source_page"),
                "gold_level": label.get("gold_level", ""),
                "expected_abstention": bool(label.get("expected_abstention", False)),
                "answer_key": label.get("answer_key", ""),
            }
        )
    return dict(sorted(samples.items()))


def build_benchmark_v2_summary(
    gold_labels_path: str | Path,
    chunks_paths: list[str | Path] | tuple[str | Path, ...],
) -> dict[str, Any]:
    payload = read_benchmark_payload(gold_labels_path)
    validation = validate_benchmark(gold_labels_path, chunks_paths)
    return {
        "metadata": validation["metadata"],
        "validation": {
            "valid": validation["valid"],
            "errors_total": validation["errors_total"],
            "warnings_total": validation["warnings_total"],
            "errors": validation["errors"],
            "warnings": validation["warnings"],
        },
        "samples": _sample_labels(payload),
    }


def write_benchmark_v2_summary_json(result: dict[str, Any], output_path: str | Path) -> Path:
    return write_json_report(result, output_path)


def write_benchmark_v2_summary_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = result["metadata"]
    evidence = metadata["evidence_span_validation"]
    validation = result["validation"]
    lines = [
        "# Benchmark V2 Summary",
        "",
        f"- Label set: `{metadata['label_set']}`",
        f"- Review status: `{metadata['review_status']}`",
        f"- Labels: {metadata['labels_total']}",
        f"- Supported labels: {metadata['supported_total']}",
        f"- Insufficient-evidence labels: {metadata['no_answer_total']}",
        f"- Span-level labels: {metadata['span_level_count']}",
        f"- Evidence span validation: {evidence['passed']}/{evidence['checked']} passed",
        f"- Validation passed: {validation['valid']}",
        "",
        "## Category Distribution",
        "",
        "| Question type | Count |",
        "| --- | ---: |",
    ]
    for question_type, count in metadata["category_counts"].items():
        lines.append(f"| {question_type} | {count} |")

    lines.extend(
        [
            "",
            "## Missing Fields",
            "",
            "| Field | Count |",
            "| --- | ---: |",
        ]
    )
    missing = metadata["missing_field_counts"]
    if missing:
        for field, count in missing.items():
            lines.append(f"| {field} | {count} |")
    else:
        lines.append("| none | 0 |")

    lines.extend(["", "## Warnings", ""])
    if validation["warnings"]:
        lines.extend(f"- {warning}" for warning in validation["warnings"][:20])
    else:
        lines.append("- none")

    if validation["errors"]:
        lines.extend(["", "## Errors", ""])
        lines.extend(f"- {error}" for error in validation["errors"][:40])

    lines.extend(["", "## Sample Labels", ""])
    for question_type, samples in result["samples"].items():
        lines.extend([f"### {question_type}", ""])
        for sample in samples:
            lines.extend(
                [
                    f"- `{sample['cq_id']}`: {sample['question']}",
                    f"  Answer key: {sample['answer_key']}",
                ]
            )
        lines.append("")

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_benchmark_v2_summary(
    gold_labels_path: str | Path,
    chunks_paths: list[str | Path] | tuple[str | Path, ...],
    output_dir: str | Path,
    *,
    report_name: str = "benchmark_v2_summary",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_benchmark_v2_summary(gold_labels_path, chunks_paths)
    output = Path(output_dir)
    stem = Path(report_name).stem or "benchmark_v2_summary"
    json_path = write_benchmark_v2_summary_json(result, output / f"{stem}.json")
    md_path = write_benchmark_v2_summary_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
