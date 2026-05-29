from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

from aviation_agentic_ai.evaluation.benchmark_validation import read_benchmark_payload
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.retrieval.sufficiency import detect_risk_category


UNNATURAL_PATTERNS = (
    "source-backed fact connects",
    "evidence mentioning",
    "according to phak chapter 4",
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _span_key(span: dict[str, Any]) -> str:
    return f"{span.get('page')}::{_normalize(str(span.get('text', '')))}"


def _label_findings(label: dict[str, Any], duplicate_spans: set[str]) -> list[str]:
    findings: list[str] = []
    question = str(label.get("question", ""))
    normalized_question = _normalize(question)
    if any(pattern in normalized_question for pattern in UNNATURAL_PATTERNS) or len(question) > 180:
        findings.append("unnatural_machine_generated_wording")
    if any(_span_key(span) in duplicate_spans for span in label.get("evidence_spans", [])):
        findings.append("duplicate_evidence_span")
    if (
        len(question.split()) < 7
        or "what source-backed fact" in normalized_question
        or len(label.get("key_entities", [])) < 2
    ):
        findings.append("weak_or_generic_question")
    pages = {
        span.get("page")
        for span in label.get("evidence_spans", [])
        if isinstance(span, dict)
    }
    if len(pages) > 1 and len(str(label.get("answer_key", "")).split()) < 18:
        findings.append("cross_page_label_with_insufficient_synthesis")
    risk_category = detect_risk_category(question)[0]
    if label.get("expected_abstention") and risk_category != "training_question":
        findings.append("insufficient_evidence_label_needs_aviation_safety_review")
    return findings


def build_reviewed_benchmark_payload(payload: dict[str, Any]) -> dict[str, Any]:
    reviewed = deepcopy(payload)
    reviewed["review_status"] = "manual_review_pending"
    reviewed["notes"] = (
        "Working copy created for manual review. Labels are not externally aviation-expert "
        "certified and semantic correctness remains pending."
    )
    for label in reviewed.get("labels", []):
        if not isinstance(label, dict):
            continue
        review = dict(label.get("review", {}))
        review["status"] = "needs_manual_review"
        review.setdefault("reviewer_notes", "")
        review.setdefault("reviewed_at", None)
        label["review"] = review
    return reviewed


def build_benchmark_review_pack(gold_labels_path: str | Path) -> dict[str, Any]:
    payload = read_benchmark_payload(gold_labels_path)
    labels = [label for label in payload.get("labels", []) if isinstance(label, dict)]
    span_counts = Counter(
        _span_key(span)
        for label in labels
        for span in label.get("evidence_spans", [])
        if isinstance(span, dict) and span.get("text")
    )
    duplicate_spans = {key for key, count in span_counts.items() if count > 1}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    finding_counts: Counter[str] = Counter()
    for label in labels:
        findings = _label_findings(label, duplicate_spans)
        finding_counts.update(findings)
        grouped[str(label.get("question_type", "<missing>"))].append(
            {
                "cq_id": label.get("cq_id"),
                "question": label.get("question"),
                "answer_key": label.get("answer_key"),
                "source_page": label.get("source_page"),
                "expected_abstention": bool(label.get("expected_abstention")),
                "review_status": label.get("review", {}).get("status"),
                "risk_category": detect_risk_category(str(label.get("question", "")))[0],
                "findings": findings,
            }
        )
    return {
        "metadata": {
            "gold_labels_path": project_relative_path(gold_labels_path),
            "labels_total": len(labels),
            "question_types_total": len(grouped),
            "review_status": payload.get("review_status", ""),
            "external_certification": False,
        },
        "finding_counts": dict(sorted(finding_counts.items())),
        "groups": dict(sorted(grouped.items())),
        "review_policy": {
            "manual_review_required": True,
            "external_aviation_expert_certified": False,
            "do_not_claim_certification": True,
        },
    }


def write_benchmark_review_pack_json(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_benchmark_review_pack_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Benchmark Review Pack",
        "",
        f"- Gold labels: `{result['metadata']['gold_labels_path']}`",
        f"- Labels: {result['metadata']['labels_total']}",
        f"- Question types: {result['metadata']['question_types_total']}",
        "- External aviation expert certification: no",
        "- Purpose: prepare manual review; do not treat these findings as completed review.",
        "",
        "## Finding Counts",
        "",
        "| Finding | Count |",
        "| --- | ---: |",
    ]
    if result["finding_counts"]:
        for finding, count in result["finding_counts"].items():
            lines.append(f"| {finding} | {count} |")
    else:
        lines.append("| none | 0 |")
    lines.extend(["", "## Labels By Question Type", ""])
    for question_type, labels in result["groups"].items():
        lines.extend([f"### {question_type}", ""])
        for label in labels[:20]:
            findings = ", ".join(label["findings"]) if label["findings"] else "no automatic finding"
            lines.append(
                f"- `{label['cq_id']}` [{label['risk_category']}]: {label['question']} "
                f"({findings})"
            )
        if len(labels) > 20:
            lines.append(f"- ... {len(labels) - 20} additional labels omitted from Markdown preview")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_reviewed_benchmark_payload(payload: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    reviewed = build_reviewed_benchmark_payload(payload)
    path.write_text(json.dumps(reviewed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_benchmark_review_pack(
    gold_labels_path: str | Path,
    output_dir: str | Path,
    *,
    report_name: str = "benchmark_review_pack",
    reviewed_output_path: str | Path | None = None,
) -> tuple[Path, Path, Path | None, dict[str, Any]]:
    result = build_benchmark_review_pack(gold_labels_path)
    output = Path(output_dir)
    stem = Path(report_name).stem or "benchmark_review_pack"
    json_path = write_benchmark_review_pack_json(result, output / f"{stem}.json")
    md_path = write_benchmark_review_pack_markdown(result, output / f"{stem}.md")
    reviewed_path = None
    if reviewed_output_path is not None:
        payload = read_benchmark_payload(gold_labels_path)
        reviewed_path = write_reviewed_benchmark_payload(payload, reviewed_output_path)
    return json_path, md_path, reviewed_path, result
