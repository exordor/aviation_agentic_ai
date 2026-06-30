"""AUTO-SPLIT from ontology/atmonto_experiment.py. See git history."""
from __future__ import annotations

from typing import Any
from collections import Counter
from pathlib import Path

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path

from ._io import (
    read_json,
    write_json,
)
from ._system_defs import (
    REJECTION_ADJUDICATION_JSON,
    REJECTION_ADJUDICATION_MD,
    REJECTION_ANALYSIS_JSON,
)
def build_rejection_adjudication_report(
    repo_root: str | Path = PROJECT_ROOT,
    rejection_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from ._gold_review import final_rejection_group_decision
    repo_root = Path(repo_root).resolve()
    if rejection_analysis is None:
        rejection_analysis = read_json(repo_root / REJECTION_ANALYSIS_JSON)
    groups: list[dict[str, Any]] = []
    decision_counts: Counter[str] = Counter()
    confidence_counts: Counter[str] = Counter()

    for group in rejection_analysis.get("groups", []):
        decision = final_rejection_group_decision(group)
        count = int(group.get("count", 0))
        decision_counts[decision["final_decision"]] += count
        confidence_counts[decision["confidence"]] += count
        groups.append(
            {
                "predicate": group.get("predicate"),
                "errors": group.get("errors", []),
                "count": count,
                "initial_decision": group.get("decision"),
                "final_decision": decision["final_decision"],
                "confidence": decision["confidence"],
                "decision_basis": decision["decision_basis"],
                "required_follow_up": decision["required_follow_up"],
                "subject_class_counts": group.get("subject_class_counts", {}),
                "object_class_counts": group.get("object_class_counts", {}),
                "value_counts": group.get("value_counts", {}),
                "sample_rejections": group.get("sample_rejections", []),
            }
        )

    rejected_fact_count = int(rejection_analysis.get("rejected_fact_count", 0))
    grouped_fact_count = sum(group["count"] for group in groups)
    pending_fact_count = int(decision_counts.get("manual_review_only", 0))
    complete = rejected_fact_count == grouped_fact_count and pending_fact_count == 0
    return {
        "source_family": "nasa_atmonto_rejection_adjudication",
        "input_rejection_analysis": project_relative_path(
            repo_root / REJECTION_ANALYSIS_JSON,
            repo_root,
        ),
        "rejected_fact_count": rejected_fact_count,
        "grouped_fact_count": grouped_fact_count,
        "group_count": len(groups),
        "decision_counts_by_fact": dict(sorted(decision_counts.items())),
        "confidence_counts_by_fact": dict(sorted(confidence_counts.items())),
        "pending_fact_count": pending_fact_count,
        "property_level_complete": complete,
        "groups": groups,
        "boundary": (
            "This artifact finalizes property-level error categories for the "
            f"{rejected_fact_count} pilot rejections. It does not automatically approve "
            "profile extensions or convert validator-rejected facts into semantic gold facts."
        ),
    }

def rejection_adjudication_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Rejection Adjudication",
        "",
        f"- Input: `{report['input_rejection_analysis']}`",
        f"- Rejected facts: {report['rejected_fact_count']}",
        f"- Grouped facts: {report['grouped_fact_count']}",
        f"- Property-level complete: `{report['property_level_complete']}`",
        f"- Pending manual-review-only facts: {report['pending_fact_count']}",
        "",
        "## Final Decision Counts By Fact",
        "",
    ]
    for decision, count in report["decision_counts_by_fact"].items():
        lines.append(f"- `{decision}`: {count}")
    lines.extend(
        [
            "",
            "## Property-Level Decisions",
            "",
            "| Predicate | Errors | Count | Initial decision | Final decision | Confidence |",
            "| --- | --- | ---: | --- | --- | --- |",
        ]
    )
    for group in report["groups"]:
        lines.append(
            "| "
            f"`{group['predicate']}` | "
            f"`{', '.join(group['errors'])}` | "
            f"{group['count']} | "
            f"`{group['initial_decision']}` | "
            f"`{group['final_decision']}` | "
            f"`{group['confidence']}` |"
        )
    lines.extend(["", "## Decision Rationale", ""])
    for group in report["groups"]:
        lines.extend(
            [
                f"### {group['predicate']} / {', '.join(group['errors'])}",
                "",
                f"- Final decision: `{group['final_decision']}`",
                f"- Basis: {group['decision_basis']}",
                f"- Follow-up: {group['required_follow_up']}",
                "",
            ]
        )
    lines.extend(["## Boundary", "", f"- {report['boundary']}"])
    return "\n".join(lines) + "\n"

def run_rejection_adjudication(repo_root: str | Path = PROJECT_ROOT) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    report = build_rejection_adjudication_report(repo_root)
    write_json(repo_root / REJECTION_ADJUDICATION_JSON, report)
    (repo_root / REJECTION_ADJUDICATION_MD).parent.mkdir(parents=True, exist_ok=True)
    (repo_root / REJECTION_ADJUDICATION_MD).write_text(
        rejection_adjudication_markdown(report),
        encoding="utf-8",
    )
    return {
        "report_json": project_relative_path(repo_root / REJECTION_ADJUDICATION_JSON, repo_root),
        "report_markdown": project_relative_path(repo_root / REJECTION_ADJUDICATION_MD, repo_root),
        "property_level_complete": report["property_level_complete"],
        "decision_counts_by_fact": report["decision_counts_by_fact"],
    }
