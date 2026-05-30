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
REVIEWED_SUBSET_QUESTION_TYPES = (
    "concept_definition",
    "relation_causal",
    "cross_page",
    "insufficient_evidence",
)
REVIEWED_SUBSET_EXPECTED_COUNTS = {
    "concept_definition": 15,
    "relation_causal": 15,
    "cross_page": 10,
    "insufficient_evidence": 20,
}
ANSWER_EVAL_SUBSET_RULES = (
    ("supported_factual", 5),
    ("concept_definition", 5),
    ("relation_causal", 5),
    ("cross_page", 5),
    ("paraphrase", 3),
    ("terminology_variation", 2),
    ("insufficient_evidence", 10),
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


def _labels_by_question_type(labels: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for label in labels:
        grouped[str(label.get("question_type", "<missing>"))].append(label)
    return dict(grouped)


def _copy_subset_payload(
    payload: dict[str, Any],
    selected_labels: list[dict[str, Any]],
    *,
    label_set: str,
    review_status: str,
    notes: str,
    subset_policy: dict[str, Any],
) -> dict[str, Any]:
    subset = {
        key: deepcopy(value)
        for key, value in payload.items()
        if key not in {"labels", "label_distribution", "label_set", "notes", "review_status"}
    }
    labels = [deepcopy(label) for label in selected_labels]
    distribution = Counter(str(label.get("question_type", "<missing>")) for label in labels)
    subset.update(
        {
            "label_set": label_set,
            "review_status": review_status,
            "notes": notes,
            "subset_policy": subset_policy,
            "label_distribution": dict(sorted(distribution.items())),
            "labels": labels,
        }
    )
    return subset


def _add_review_metadata(label: dict[str, Any]) -> None:
    review = dict(label.get("review", {}))
    review.update(
        {
            "status": "project_review_pending_external_review",
            "project_author_review_status": "needs_project_author_review",
            "review_decision": "pending",
            "reviewer_notes": review.get("reviewer_notes", ""),
            "reviewed_at": review.get("reviewed_at"),
            "external_aviation_expert_certified": False,
            "manual_review_fields": {
                "natural_question_ok": "needs_review",
                "answer_span_complete": "needs_review",
                "evidence_supports_answer": "needs_review",
                "cross_page_synthesis_ok": "needs_review",
                "safety_boundary_ok": "needs_review",
            },
        }
    )
    label["review"] = review
    tags = list(label.get("tags", []))
    for tag in ("reviewed_subset", "project_review_pending_external_review"):
        if tag not in tags:
            tags.append(tag)
    label["tags"] = tags


def build_reviewed_subset_payload(payload: dict[str, Any]) -> dict[str, Any]:
    labels = [label for label in payload.get("labels", []) if isinstance(label, dict)]
    grouped = _labels_by_question_type(labels)
    selected: list[dict[str, Any]] = []
    for question_type in REVIEWED_SUBSET_QUESTION_TYPES:
        items = grouped.get(question_type, [])
        expected = REVIEWED_SUBSET_EXPECTED_COUNTS[question_type]
        if len(items) != expected:
            raise ValueError(
                f"Expected {expected} `{question_type}` labels for reviewed subset; "
                f"found {len(items)}."
            )
        selected.extend(items)
    subset = _copy_subset_payload(
        payload,
        selected,
        label_set="06_phak_ch4_0.benchmark_v2.reviewed_subset",
        review_status="project_review_pending_external_review",
        notes=(
            "Deterministic 60-label reviewed-subset scaffold. Original questions, "
            "answer keys, and evidence spans are preserved; no project-author or "
            "external aviation expert review is claimed."
        ),
        subset_policy={
            "selection": "all concept_definition, relation_causal, cross_page, and insufficient_evidence labels",
            "labels_total": len(selected),
            "external_aviation_expert_certified": False,
            "manual_review_completed": False,
            "counts_by_question_type": dict(REVIEWED_SUBSET_EXPECTED_COUNTS),
        },
    )
    for label in subset["labels"]:
        _add_review_metadata(label)
    return subset


def build_answer_eval_subset_payload(payload: dict[str, Any]) -> dict[str, Any]:
    labels = [label for label in payload.get("labels", []) if isinstance(label, dict)]
    grouped = _labels_by_question_type(labels)
    selected: list[dict[str, Any]] = []
    selection_counts: dict[str, int] = {}
    for question_type, count in ANSWER_EVAL_SUBSET_RULES:
        items = grouped.get(question_type, [])
        if len(items) < count:
            raise ValueError(
                f"Expected at least {count} `{question_type}` labels for answer-eval subset; "
                f"found {len(items)}."
            )
        selected.extend(items[:count])
        selection_counts[question_type] = count
    subset = _copy_subset_payload(
        payload,
        selected,
        label_set="06_phak_ch4_0.answer_eval_subset",
        review_status="deterministic_answer_eval_subset_requires_manual_review",
        notes=(
            "Stratified answer-evaluation subset for deterministic heuristic scoring. "
            "Scores from this subset are not manual review or LLM-as-judge results unless "
            "separate annotation artifacts are supplied."
        ),
        subset_policy={
            "selection": "deterministic first-N stratified sample by question_type",
            "labels_total": len(selected),
            "counts_by_question_type": selection_counts,
            "score_method": "deterministic_heuristic",
            "manual_review_completed": False,
            "llm_as_judge_enabled": False,
        },
    )
    return subset


def build_benchmark_reviewed_subset_summary(subset_payload: dict[str, Any]) -> dict[str, Any]:
    labels = [label for label in subset_payload.get("labels", []) if isinstance(label, dict)]
    review_statuses = Counter(
        str(label.get("review", {}).get("status", "<missing>")) for label in labels
    )
    question_types = Counter(str(label.get("question_type", "<missing>")) for label in labels)
    expected_abstention_total = sum(int(bool(label.get("expected_abstention"))) for label in labels)
    findings = Counter(
        finding
        for label in labels
        for finding in _label_findings(label, set())
    )
    return {
        "metadata": {
            "label_set": subset_payload.get("label_set"),
            "labels_total": len(labels),
            "review_status": subset_payload.get("review_status"),
            "manual_review_completed": False,
            "external_aviation_expert_certified": False,
            "expected_abstention_total": expected_abstention_total,
        },
        "question_type_counts": dict(sorted(question_types.items())),
        "review_status_counts": dict(sorted(review_statuses.items())),
        "finding_counts": dict(sorted(findings.items())),
        "subset_policy": subset_payload.get("subset_policy", {}),
    }


def write_subset_payload(payload: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_benchmark_reviewed_subset_summary_json(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_benchmark_reviewed_subset_summary_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = result["metadata"]
    lines = [
        "# Benchmark Reviewed Subset Summary",
        "",
        f"- Label set: `{metadata['label_set']}`",
        f"- Labels: {metadata['labels_total']}",
        f"- Review status: `{metadata['review_status']}`",
        "- Manual review completed: no",
        "- External aviation expert certification: no",
        "- Scope: scaffold for project-author review; no labels are certified by this report.",
        "",
        "## Question Types",
        "",
        "| Question type | Count |",
        "| --- | ---: |",
    ]
    for question_type, count in result["question_type_counts"].items():
        lines.append(f"| {question_type} | {count} |")
    lines.extend(["", "## Review Status Counts", "", "| Status | Count |", "| --- | ---: |"])
    for status, count in result["review_status_counts"].items():
        lines.append(f"| {status} | {count} |")
    lines.extend(["", "## Automatic Review Findings", "", "| Finding | Count |", "| --- | ---: |"])
    if result["finding_counts"]:
        for finding, count in result["finding_counts"].items():
            lines.append(f"| {finding} | {count} |")
    else:
        lines.append("| none | 0 |")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_benchmark_reviewed_subset(
    gold_labels_path: str | Path,
    output_dir: str | Path,
    *,
    subset_output_path: str | Path,
    report_name: str = "benchmark_reviewed_subset_summary",
) -> tuple[Path, Path, Path, dict[str, Any]]:
    payload = read_benchmark_payload(gold_labels_path)
    subset = build_reviewed_subset_payload(payload)
    subset_path = write_subset_payload(subset, subset_output_path)
    summary = build_benchmark_reviewed_subset_summary(subset)
    output = Path(output_dir)
    stem = Path(report_name).stem or "benchmark_reviewed_subset_summary"
    json_path = write_benchmark_reviewed_subset_summary_json(summary, output / f"{stem}.json")
    md_path = write_benchmark_reviewed_subset_summary_markdown(summary, output / f"{stem}.md")
    return json_path, md_path, subset_path, summary


def write_answer_eval_subset(
    gold_labels_path: str | Path,
    subset_output_path: str | Path,
) -> tuple[Path, dict[str, Any]]:
    payload = read_benchmark_payload(gold_labels_path)
    subset = build_answer_eval_subset_payload(payload)
    subset_path = write_subset_payload(subset, subset_output_path)
    return subset_path, subset


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
