from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report
from aviation_agentic_ai.reporting.nasa_atmonto_s7_human_review_candidates import (
    DEFAULT_S7_LLM_REPORT_PATH,
    trim_text,
)

DEFAULT_S7_CANDIDATE_PATH = Path("reports/stages/nasa_atmonto_s7_human_review_candidates.json")


def build_nasa_atmonto_s7_candidate_adjudication(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    candidate_report_path: str | Path = DEFAULT_S7_CANDIDATE_PATH,
    s7_llm_report_path: str | Path = DEFAULT_S7_LLM_REPORT_PATH,
) -> dict[str, Any]:
    root = Path(repo_root)
    candidate_path = resolve_report_path(root, candidate_report_path)
    llm_path = resolve_report_path(root, s7_llm_report_path)
    candidate_report = read_json_object_or_empty(candidate_path)
    llm_report = read_json_object_or_empty(llm_path)
    candidates = [
        candidate
        for candidate in candidate_report.get("candidates", [])
        if isinstance(candidate, dict)
    ]
    adjudications = [adjudicate_candidate(candidate) for candidate in candidates]
    failure_adjudications = [
        item for item in adjudications if item.get("priority") == "failure"
    ]
    decision_counts = Counter(str(item["adjudication"]) for item in adjudications)
    failure_type_counts = Counter(
        str(item["failure_type"])
        for item in failure_adjudications
        if item.get("failure_type")
    )
    return {
        "source_family": "nasa_atmonto_s7_candidate_adjudication",
        "status": "candidate_adjudication_created",
        "metadata": {
            "candidate_report_path": project_relative_path(candidate_path, root),
            "s7_llm_report_path": project_relative_path(llm_path, root),
            "candidate_count": len(candidates),
            "failure_candidate_count": len(failure_adjudications),
            "source_llm_selected_cases": llm_report.get("metadata", {}).get(
                "selected_case_count"
            ),
            "strict_main_metrics_changed": False,
            "human_review": False,
            "external_expert_certified": False,
            "boundary": (
                "This is deterministic project adjudication of review candidates. "
                "It is not human review and does not change the S7 main answer metrics."
            ),
        },
        "summary": {
            "decision_counts": dict(sorted(decision_counts.items())),
            "failure_type_counts": dict(sorted(failure_type_counts.items())),
            "profile_or_gold_boundary_failures": decision_counts.get(
                "profile_or_gold_boundary_case",
                0,
            ),
            "retrieval_failure_count": decision_counts.get("retrieval_failure", 0),
            "model_hallucination_count": decision_counts.get("model_hallucination", 0),
            "recommended_policy": (
                "Keep strict S7 metrics unchanged. Treat the current failures as "
                "profile/gold-boundary review targets unless a reviewer approves either "
                "a STAFFING impactingCondition value extension or a predicate-whitelist "
                "rule for this CQ template."
            ),
        },
        "adjudications": adjudications,
        "claim_boundary": (
            "Cite this artifact as failure-analysis evidence only. Do not cite it as "
            "expert validation, operational readiness, or corrected answer accuracy."
        ),
    }


def resolve_report_path(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def adjudicate_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    priority = str(candidate.get("priority") or "")
    if priority != "failure":
        return {
            "review_id": candidate.get("review_id"),
            "priority": priority,
            "template_id": candidate.get("template_id"),
            "source_id": candidate.get("source_id"),
            "mode": candidate.get("mode"),
            "adjudication": "coverage_success_not_adjudicated",
            "failure_type": None,
            "strict_metric_action": "unchanged",
            "rationale": "Coverage examples are retained for later review calibration.",
            "recommended_action": "Use as positive-control evidence during manual review.",
        }
    if is_staffing_condition_boundary_case(candidate):
        return staffing_boundary_adjudication(candidate)
    if has_expected_source_evidence(candidate):
        return generic_overanswer_adjudication(candidate)
    return {
        "review_id": candidate.get("review_id"),
        "priority": priority,
        "template_id": candidate.get("template_id"),
        "source_id": candidate.get("source_id"),
        "mode": candidate.get("mode"),
        "adjudication": "manual_review_only",
        "failure_type": "unclassified_failure",
        "strict_metric_action": "unchanged",
        "rationale": (
            "The candidate does not match a deterministic adjudication rule. Inspect "
            "source evidence, graph triples, and answer values manually."
        ),
        "recommended_action": "Keep the current failure until a reviewer records a decision.",
    }


def is_staffing_condition_boundary_case(candidate: dict[str, Any]) -> bool:
    if candidate.get("template_id") != "QT-Q01-CAUSE-CONDITION":
        return False
    expected = set(candidate.get("expected_answer_set") or [])
    answer_values = candidate.get("answer_values") or []
    has_expected_message = "impactingConditionMessage=STAFFING / STAFFING" in expected
    has_extra_condition = any(
        isinstance(item, dict)
        and str(item.get("predicate")) == "impactingCondition"
        and str(item.get("value", "")).strip().lower() in {"staffing", "other"}
        for item in answer_values
    )
    has_message_answer = any(
        isinstance(item, dict)
        and str(item.get("predicate")) == "impactingConditionMessage"
        and str(item.get("value")) == "STAFFING / STAFFING"
        for item in answer_values
    )
    evidence_text = candidate_evidence_text(candidate).lower()
    graph_has_other = any(
        isinstance(item, dict)
        and str(item.get("predicate")) == "impactingCondition"
        and str(item.get("object", "")).strip().lower() == "other"
        for item in candidate.get("evidence", {}).get("graph_triples", [])
    )
    return (
        has_expected_message
        and has_message_answer
        and has_extra_condition
        and "staffing / staffing" in evidence_text
        and graph_has_other
    )


def staffing_boundary_adjudication(candidate: dict[str, Any]) -> dict[str, Any]:
    extra_values = [
        item
        for item in candidate.get("answer_values", [])
        if isinstance(item, dict) and str(item.get("predicate")) == "impactingCondition"
    ]
    return {
        "review_id": candidate.get("review_id"),
        "priority": candidate.get("priority"),
        "template_id": candidate.get("template_id"),
        "source_id": candidate.get("source_id"),
        "mode": candidate.get("mode"),
        "adjudication": "profile_or_gold_boundary_case",
        "failure_type": "extra_coarse_impacting_condition_for_staffing",
        "strict_metric_action": "unchanged",
        "would_pass_if_extra_condition_ignored": True,
        "extra_answer_values": extra_values,
        "rationale": (
            "The source supports the raw condition message STAFFING / STAFFING and the "
            "answer includes that expected value. The failure is caused by an extra "
            "coarse impactingCondition value. Current graph evidence maps the coarse "
            "value to other, while another LLM output may normalize the surface value "
            "to staffing. That mismatch is a NASA ATMONTO profile/gold boundary issue, "
            "not a retrieval miss."
        ),
        "recommended_action": (
            "Do not change the main S7 score without review. Either approve STAFFING as "
            "an impactingCondition profile extension and add it to gold answer sets, or "
            "keep the CQ answer-set scoped to impactingConditionMessage and enforce a "
            "predicate whitelist for this template."
        ),
        "evidence_snapshot": trim_text(candidate_evidence_text(candidate), 600),
    }


def has_expected_source_evidence(candidate: dict[str, Any]) -> bool:
    evidence_text = candidate_evidence_text(candidate).lower()
    return bool(evidence_text.strip()) and any(
        str(item).split("=", 1)[-1].strip().lower() in evidence_text
        for item in candidate.get("expected_answer_set", [])
    )


def generic_overanswer_adjudication(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "review_id": candidate.get("review_id"),
        "priority": candidate.get("priority"),
        "template_id": candidate.get("template_id"),
        "source_id": candidate.get("source_id"),
        "mode": candidate.get("mode"),
        "adjudication": "model_overanswer_or_template_boundary",
        "failure_type": "extra_answer_value_with_expected_evidence_present",
        "strict_metric_action": "unchanged",
        "rationale": (
            "The source appears to support at least one expected value, but the answer "
            "contains extra values or predicates that fail strict answer-set scoring."
        ),
        "recommended_action": (
            "Keep the current failure and review whether the CQ template should whitelist "
            "predicates more tightly or the gold answer set should be expanded."
        ),
    }


def candidate_evidence_text(candidate: dict[str, Any]) -> str:
    evidence = candidate.get("evidence", {})
    parts: list[str] = []
    for chunk in evidence.get("source_chunks", []):
        if isinstance(chunk, dict):
            parts.append(str(chunk.get("text") or ""))
    for triple in evidence.get("graph_triples", []):
        if isinstance(triple, dict):
            parts.append(str(triple.get("evidence_text") or ""))
            parts.append(f"{triple.get('predicate')}={triple.get('object')}")
    return " ".join(parts)


def write_nasa_atmonto_s7_candidate_adjudication_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    summary = result["summary"]
    lines = [
        "# NASA ATMONTO S7 Candidate Adjudication",
        "",
        "## Boundary",
        "",
        result["metadata"]["boundary"],
        "",
        "## Summary",
        "",
        f"- Source LLM cases: {result['metadata']['source_llm_selected_cases']}",
        f"- Candidate total: {result['metadata']['candidate_count']}",
        f"- Failure candidates: {result['metadata']['failure_candidate_count']}",
        f"- Strict main metrics changed: {result['metadata']['strict_main_metrics_changed']}",
        f"- Decision counts: `{summary['decision_counts']}`",
        f"- Failure type counts: `{summary['failure_type_counts']}`",
        f"- Recommended policy: {summary['recommended_policy']}",
        "",
        "## Failure Adjudications",
        "",
        "| Review ID | Template | Source | Mode | Adjudication | Failure type | Action |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in result["adjudications"]:
        if item.get("priority") != "failure":
            continue
        lines.append(
            f"| `{item.get('review_id')}` | `{item.get('template_id')}` | "
            f"`{item.get('source_id')}` | `{item.get('mode')}` | "
            f"{item.get('adjudication')} | {item.get('failure_type')} | "
            f"{item.get('strict_metric_action')} |"
        )
    lines.extend(["", "## Details", ""])
    for item in result["adjudications"]:
        if item.get("priority") != "failure":
            continue
        lines.extend(
            [
                f"### {item.get('review_id')}",
                "",
                f"- Adjudication: `{item.get('adjudication')}`",
                f"- Failure type: `{item.get('failure_type')}`",
                f"- Would pass if extra condition ignored: "
                f"`{item.get('would_pass_if_extra_condition_ignored', False)}`",
                f"- Rationale: {item.get('rationale')}",
                f"- Recommended action: {item.get('recommended_action')}",
                "",
            ]
        )
    lines.extend(["## Claim Boundary", "", result["claim_boundary"]])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_nasa_atmonto_s7_candidate_adjudication(
    *,
    output_dir: str | Path,
    repo_root: str | Path = PROJECT_ROOT,
    report_name: str = "nasa_atmonto_s7_candidate_adjudication",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_nasa_atmonto_s7_candidate_adjudication(repo_root=repo_root)
    output = Path(output_dir)
    json_path = write_json_report(result, output / f"{report_name}.json")
    md_path = write_nasa_atmonto_s7_candidate_adjudication_markdown(
        result,
        output / f"{report_name}.md",
    )
    return json_path, md_path, result
