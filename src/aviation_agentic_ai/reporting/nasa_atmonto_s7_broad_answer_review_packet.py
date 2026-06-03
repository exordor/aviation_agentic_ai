from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report
from aviation_agentic_ai.reporting.nasa_atmonto_s7_human_review_candidates import (
    DEFAULT_S7_LLM_REPORT_PATH,
    resolve_report_path,
    review_candidate,
    s7_context_index,
)
from aviation_agentic_ai.reporting.nasa_atmonto_s7_llm_answer_generation import (
    DEFAULT_S7_ANSWER_REPORT_PATH,
)

DEFAULT_REPORT_NAME = "nasa_atmonto_s7_broad_answer_review_packet"


def build_nasa_atmonto_s7_broad_answer_review_packet(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    s7_answer_report_path: str | Path = DEFAULT_S7_ANSWER_REPORT_PATH,
    s7_llm_report_path: str | Path = DEFAULT_S7_LLM_REPORT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    s7_path = resolve_report_path(root, s7_answer_report_path)
    llm_path = resolve_report_path(root, s7_llm_report_path)
    s7_report = read_json_object_or_empty(s7_path)
    llm_report = read_json_object_or_empty(llm_path)
    contexts = s7_context_index(s7_report)
    llm_records = [record for record in llm_report.get("records", []) if isinstance(record, dict)]
    cases = [
        {
            **review_candidate(index, record, contexts),
            "review_id": f"S7-BR-{index:03d}",
        }
        for index, record in enumerate(llm_records, start=1)
    ]
    metrics = [_case_metrics(case) for case in cases]
    return {
        "source_family": "nasa_atmonto_s7_broad_answer_review_packet",
        "status": "broad_answer_review_packet_created",
        "metadata": {
            "s7_answer_report_path": project_relative_path(s7_path, root),
            "s7_llm_report_path": project_relative_path(llm_path, root),
            "source_llm_selected_cases": llm_report.get("metadata", {}).get(
                "selected_case_count"
            ),
            "case_count": len(cases),
            "failure_case_count": sum(1 for item in metrics if item["needs_review"]),
            "coverage_success_case_count": sum(1 for item in metrics if not item["needs_review"]),
            "human_review": False,
            "human_review_completed": False,
            "boundary": (
                "This is a broad reviewer packet over every selected S7 LLM answer case. "
                "It contains automatic metrics and blank reviewer fields, but it is not "
                "human-reviewed evidence until an external reviewer records decisions."
            ),
        },
        "aggregate": aggregate_review_cases(cases),
        "review_schema": review_schema(),
        "cases": cases,
        "claim_boundary": (
            "Use this packet to perform or document human/supervisor review of answer "
            "correctness, evidence support, citation sufficiency, and profile-boundary "
            "cases. Do not cite it as expert validation before reviewer decisions are "
            "filled in."
        ),
    }


def _case_metrics(case: dict[str, Any]) -> dict[str, Any]:
    metrics = case.get("metrics") if isinstance(case.get("metrics"), dict) else {}
    needs_review = (
        metrics.get("answer_correctness") is not True
        or metrics.get("evidence_faithfulness") is not True
        or float(metrics.get("unsupported_claim_rate") or 0.0) > 0.0
    )
    return {
        "needs_review": needs_review,
        "template_id": str(case.get("template_id") or ""),
        "mode": str(case.get("mode") or ""),
    }


def aggregate_review_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = [_case_metrics(case) for case in cases]
    template_counts = Counter(item["template_id"] for item in metrics)
    mode_counts = Counter(item["mode"] for item in metrics)
    review_counts = Counter("needs_review" if item["needs_review"] else "auto_success" for item in metrics)
    return {
        "case_count": len(cases),
        "review_status_counts": dict(sorted(review_counts.items())),
        "template_counts": dict(sorted(template_counts.items())),
        "mode_counts": dict(sorted(mode_counts.items())),
    }


def review_schema() -> list[dict[str, str]]:
    return [
        {
            "field": "review_decision",
            "allowed_values": "correct | partially_correct | incorrect | abstention_correct | profile_boundary | unsure",
        },
        {
            "field": "evidence_support",
            "allowed_values": "fully_supported | partially_supported | unsupported | not_applicable",
        },
        {
            "field": "citation_sufficiency",
            "allowed_values": "sufficient | partial | insufficient | not_applicable",
        },
        {
            "field": "profile_boundary",
            "allowed_values": "yes | no | unsure",
        },
        {
            "field": "reviewer_notes",
            "allowed_values": "free text",
        },
        {
            "field": "reviewer_id_or_initials",
            "allowed_values": "pseudonym or initials",
        },
        {
            "field": "reviewer_role",
            "allowed_values": "external_expert | human_reviewer | supervisor",
        },
        {
            "field": "reviewed_at",
            "allowed_values": "YYYY-MM-DD or ISO timestamp",
        },
    ]


def review_csv_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for case in result["cases"]:
        metrics = case.get("metrics") if isinstance(case.get("metrics"), dict) else {}
        rows.append(
            {
                "review_id": case.get("review_id"),
                "priority": case.get("priority"),
                "template_id": case.get("template_id"),
                "source_id": case.get("source_id"),
                "mode": case.get("mode"),
                "question": case.get("question"),
                "expected_answer_set": " | ".join(str(item) for item in case.get("expected_answer_set", [])),
                "answer_values": repr(case.get("answer_values", [])),
                "answer": case.get("answer"),
                "auto_answer_correctness": metrics.get("answer_correctness"),
                "auto_evidence_faithfulness": metrics.get("evidence_faithfulness"),
                "auto_unsupported_claim_rate": metrics.get("unsupported_claim_rate"),
                "auto_citation_precision": metrics.get("citation_precision"),
                "auto_citation_recall": metrics.get("citation_recall"),
                "review_decision": "",
                "evidence_support": "",
                "citation_sufficiency": "",
                "profile_boundary": "",
                "reviewer_notes": "",
                "reviewer_id_or_initials": "",
                "reviewer_role": "",
                "reviewed_at": "",
            }
        )
    return rows


def write_review_csv(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = review_csv_rows(result)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_nasa_atmonto_s7_broad_answer_review_packet_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO S7 Broad Answer Review Packet",
        "",
        "## Boundary",
        "",
        result["metadata"]["boundary"],
        "",
        "## Summary",
        "",
        f"- Source LLM cases: {result['metadata']['source_llm_selected_cases']}",
        f"- Review packet cases: {result['metadata']['case_count']}",
        f"- Failure / needs-review cases: {result['metadata']['failure_case_count']}",
        f"- Auto-success coverage cases: {result['metadata']['coverage_success_case_count']}",
        f"- Human review completed: `{result['metadata']['human_review_completed']}`",
        "",
        "## Review Schema",
        "",
        "| Field | Allowed values |",
        "| --- | --- |",
    ]
    for item in result["review_schema"]:
        lines.append(f"| `{item['field']}` | {item['allowed_values'].replace('|', '/')} |")
    lines.extend(
        [
            "",
            "## Aggregate",
            "",
            f"- Review status counts: `{result['aggregate']['review_status_counts']}`",
            f"- Template counts: `{result['aggregate']['template_counts']}`",
            f"- Mode counts: `{result['aggregate']['mode_counts']}`",
            "",
            "## Case Index",
            "",
            "| Review ID | Priority | Template | Source | Mode | Auto correct | Unsupported |",
            "| --- | --- | --- | --- | --- | ---: | ---: |",
        ]
    )
    for case in result["cases"]:
        metrics = case.get("metrics") if isinstance(case.get("metrics"), dict) else {}
        lines.append(
            f"| `{case['review_id']}` | {case['priority']} | `{case['template_id']}` | "
            f"`{case['source_id']}` | `{case['mode']}` | "
            f"{metrics.get('answer_correctness')} | {metrics.get('unsupported_claim_rate')} |"
        )
    lines.extend(
        [
            "",
            "## Reviewer Instructions",
            "",
            "1. Start with cases where `Priority` is `failure`.",
            "2. Verify that each returned value is supported by the source chunk or graph triple.",
            "3. Mark profile-boundary cases separately from retrieval or generation errors.",
            "4. Fill the CSV review columns; do not edit automatic metric columns.",
            "5. For browser-based review, use `reports/stages/nasa_atmonto_s7_answer_review_worksheet.html`.",
            "6. For the full handoff protocol, use `reports/stages/nasa_atmonto_s7_answer_review_protocol.md`.",
            "",
            "## Claim Boundary",
            "",
            result["claim_boundary"],
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_nasa_atmonto_s7_broad_answer_review_packet(
    *,
    output_dir: str | Path,
    repo_root: str | Path = PROJECT_ROOT,
    report_name: str = DEFAULT_REPORT_NAME,
) -> tuple[Path, Path, Path, dict[str, Any]]:
    result = build_nasa_atmonto_s7_broad_answer_review_packet(repo_root=repo_root)
    output = Path(output_dir)
    json_path = write_json_report(result, output / f"{report_name}.json")
    md_path = write_nasa_atmonto_s7_broad_answer_review_packet_markdown(
        result,
        output / f"{report_name}.md",
    )
    csv_path = write_review_csv(result, output / f"{report_name}.csv")
    return json_path, md_path, csv_path, result
