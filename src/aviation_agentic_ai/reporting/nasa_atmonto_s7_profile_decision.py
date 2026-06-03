from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report
from aviation_agentic_ai.reporting.nasa_atmonto_answer_scoring import evaluate_result
from aviation_agentic_ai.reporting.nasa_atmonto_s7_llm_answer_generation import (
    S7_LLM_ANSWER_MODES,
    aggregate_llm_answer_records,
    label_from_s7_record,
    resolve_report_path,
)

DEFAULT_S7_LLM_REPORT_PATH = Path("reports/stages/nasa_atmonto_s7_llm_answer_generation.json")
DEFAULT_S7_ADJUDICATION_PATH = Path("reports/stages/nasa_atmonto_s7_candidate_adjudication.json")
STAFFING_MESSAGE = "STAFFING / STAFFING"
STAFFING_BOUNDARY_FAILURE_TYPE = "extra_coarse_impacting_condition_for_staffing"


def build_nasa_atmonto_s7_profile_decision(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    s7_llm_report_path: str | Path = DEFAULT_S7_LLM_REPORT_PATH,
    s7_adjudication_path: str | Path = DEFAULT_S7_ADJUDICATION_PATH,
    modes: tuple[str, ...] = S7_LLM_ANSWER_MODES,
) -> dict[str, Any]:
    root = Path(repo_root)
    llm_path = resolve_report_path(root, s7_llm_report_path)
    adjudication_path = resolve_report_path(root, s7_adjudication_path)
    llm_report = read_json_object_or_empty(llm_path)
    adjudication_report = read_json_object_or_empty(adjudication_path)
    records = [record for record in llm_report.get("records", []) if isinstance(record, dict)]
    boundary_adjudications = staffing_boundary_adjudications(adjudication_report)
    correction_keys = {
        record_key(item)
        for item in boundary_adjudications
        if item.get("would_pass_if_extra_condition_ignored") is True
    }
    derived_records = [
        what_if_record(record, correction_keys=correction_keys) for record in records
    ]
    corrected_records = [
        record
        for record in derived_records
        if record.get("profile_decision_what_if", {}).get("corrected_by_policy")
    ]
    strict_by_mode = llm_report.get("answer_quality", {}).get("aggregate_by_mode", {})
    if not isinstance(strict_by_mode, dict):
        strict_by_mode = {}
    what_if_by_mode = aggregate_llm_answer_records(derived_records, modes)
    corrected_by_mode = Counter(str(record.get("mode") or "") for record in corrected_records)
    return {
        "source_family": "nasa_atmonto_s7_profile_decision",
        "status": "profile_decision_what_if_created",
        "metadata": {
            "s7_llm_report_path": project_relative_path(llm_path, root),
            "s7_adjudication_path": project_relative_path(adjudication_path, root),
            "source_llm_selected_cases": llm_report.get("metadata", {}).get(
                "selected_case_count"
            ),
            "boundary_adjudication_count": len(boundary_adjudications),
            "corrected_record_count": len(corrected_records),
            "strict_main_metrics_changed": False,
            "gold_or_profile_changed": False,
            "what_if_metrics_replace_main": False,
            "human_review": False,
            "external_expert_certified": False,
            "boundary": (
                "This report converts deterministic S7 candidate adjudication into a "
                "profile-policy sensitivity analysis. It does not modify the NASA "
                "ATMONTO profile, gold labels, S7 main metrics, or generated answers."
            ),
        },
        "summary": {
            "recommended_policy": (
                "Keep strict S7 metrics unchanged. Report the predicate-whitelist "
                "what-if as a sensitivity analysis, and treat STAFFING as a proposed "
                "profile extension that requires human or supervisor approval before "
                "changing gold/profile artifacts."
            ),
            "strict_best_mode": best_mode(strict_by_mode),
            "strict_aggregate_by_mode": strict_by_mode,
            "what_if_aggregate_by_mode": what_if_by_mode,
            "corrected_record_count_by_mode": dict(sorted(corrected_by_mode.items())),
            "decision_options": decision_options(len(corrected_records)),
        },
        "case_decisions": case_decisions(boundary_adjudications),
        "records": derived_records,
        "claim_boundary": (
            "Cite this as profile-decision sensitivity evidence only. It is not human "
            "review, not a gold-label update, and not proof that NASA ATMONTO already "
            "contains STAFFING as an approved impactingCondition value."
        ),
    }


def staffing_boundary_adjudications(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in report.get("adjudications", [])
        if isinstance(item, dict)
        and item.get("priority") == "failure"
        and item.get("adjudication") == "profile_or_gold_boundary_case"
        and item.get("failure_type") == STAFFING_BOUNDARY_FAILURE_TYPE
    ]


def record_key(item: dict[str, Any]) -> tuple[str, str, str]:
    return (
        str(item.get("mode") or ""),
        str(item.get("template_id") or ""),
        str(item.get("source_id") or ""),
    )


def what_if_record(
    record: dict[str, Any],
    *,
    correction_keys: set[tuple[str, str, str]],
) -> dict[str, Any]:
    derived = dict(record)
    key = record_key(record)
    original_metrics = record.get("metrics") if isinstance(record.get("metrics"), dict) else None
    corrected_by_policy = False
    policy_removed_values: list[dict[str, Any]] = []
    if key in correction_keys:
        answer_values = [
            item for item in record.get("answer_values", []) if isinstance(item, dict)
        ]
        kept_values: list[dict[str, Any]] = []
        for item in answer_values:
            if is_extra_staffing_condition_value(item):
                policy_removed_values.append(dict(item))
                continue
            kept_values.append(dict(item))
        if policy_removed_values and has_staffing_message_answer(kept_values):
            corrected_by_policy = True
            derived["answer_values"] = kept_values
            derived["metrics"] = corrected_metrics(record, derived)
    derived["profile_decision_what_if"] = {
        "policy": "predicate_whitelist_current_profile",
        "eligible": key in correction_keys,
        "corrected_by_policy": corrected_by_policy,
        "removed_answer_values": policy_removed_values,
        "strict_answer_correctness_before": original_metrics.get("answer_correctness")
        if original_metrics
        else None,
        "strict_answer_correctness_after": derived.get("metrics", {}).get("answer_correctness")
        if isinstance(derived.get("metrics"), dict)
        else None,
    }
    return derived


def corrected_metrics(original: dict[str, Any], derived: dict[str, Any]) -> dict[str, Any]:
    metrics = evaluate_result(label_from_s7_record(original), derived)
    original_metrics = original.get("metrics") if isinstance(original.get("metrics"), dict) else {}
    for key in (
        "citation_precision",
        "citation_recall",
        "valid_citations",
        "detected_citations",
        "available_citation_units",
    ):
        if key in original_metrics:
            metrics[key] = original_metrics[key]
    metrics["evidence_faithfulness"] = bool(metrics.get("valid_citations")) and (
        metrics.get("unsupported_claim_rate") == 0.0
    )
    if metrics.get("expected_abstention") and metrics.get("actual_abstention"):
        metrics["evidence_faithfulness"] = True
    return metrics


def is_extra_staffing_condition_value(item: dict[str, Any]) -> bool:
    predicate = str(item.get("predicate") or "")
    value = str(item.get("value") or "").strip().lower()
    return predicate == "impactingCondition" and value in {"staffing", "other"}


def has_staffing_message_answer(answer_values: list[dict[str, Any]]) -> bool:
    return any(
        str(item.get("predicate") or "") == "impactingConditionMessage"
        and str(item.get("value") or "") == STAFFING_MESSAGE
        for item in answer_values
    )


def best_mode(aggregate_by_mode: dict[str, Any]) -> str | None:
    if not aggregate_by_mode:
        return None
    def correctness(mode: str) -> float:
        metrics = aggregate_by_mode.get(mode)
        if not isinstance(metrics, dict):
            return -1.0
        value = metrics.get("answer_correctness")
        if value is None:
            return -1.0
        return float(value)

    return max(
        aggregate_by_mode,
        key=correctness,
    )


def decision_options(corrected_count: int) -> list[dict[str, Any]]:
    return [
        {
            "id": "predicate_whitelist_current_profile",
            "decision_status": "recommended_for_reporting",
            "main_metric_action": "unchanged",
            "what_if_effect": (
                "Ignore only the extra coarse impactingCondition value when the same "
                "answer already returns the scored STAFFING / STAFFING "
                "impactingConditionMessage and deterministic adjudication marks the "
                "case as a profile/gold boundary."
            ),
            "corrected_case_count": corrected_count,
            "required_follow_up": (
                "Use as a sensitivity analysis in the thesis; do not replace strict "
                "main S7 metrics."
            ),
        },
        {
            "id": "staffing_profile_extension_proposal",
            "decision_status": "requires_human_or_supervisor_review",
            "main_metric_action": "not_applied",
            "what_if_effect": (
                "Treat staffing as a candidate extension for impactingCondition while "
                "preserving the raw STAFFING / STAFFING literal in "
                "impactingConditionMessage."
            ),
            "corrected_case_count": corrected_count,
            "required_follow_up": (
                "Review ATCSCC source frequency, profile semantics, and NASA ATMONTO "
                "alignment before changing ontology/profile/gold artifacts."
            ),
        },
    ]


def case_decisions(adjudications: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "review_id": item.get("review_id"),
            "template_id": item.get("template_id"),
            "source_id": item.get("source_id"),
            "mode": item.get("mode"),
            "failure_type": item.get("failure_type"),
            "strict_metric_action": "unchanged",
            "profile_policy_decision": "what_if_only",
            "profile_extension_decision": "proposed_not_applied",
            "extra_answer_values": item.get("extra_answer_values", []),
        }
        for item in adjudications
    ]


def write_nasa_atmonto_s7_profile_decision_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO S7 Profile Decision What-If",
        "",
        "## Boundary",
        "",
        result["metadata"]["boundary"],
        "",
        "## Decision Summary",
        "",
        f"- Boundary adjudications: {result['metadata']['boundary_adjudication_count']}",
        f"- Corrected records under what-if: {result['metadata']['corrected_record_count']}",
        f"- Strict main metrics changed: {result['metadata']['strict_main_metrics_changed']}",
        f"- Gold or profile changed: {result['metadata']['gold_or_profile_changed']}",
        f"- What-if metrics replace main metrics: {result['metadata']['what_if_metrics_replace_main']}",
        f"- Recommended policy: {result['summary']['recommended_policy']}",
        "",
        "## Strict vs What-If Metrics",
        "",
        (
            "| Mode | Strict correctness | What-if correctness | Strict unsupported claim rate | "
            "What-if unsupported claim rate | Corrected records |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    strict = result["summary"]["strict_aggregate_by_mode"]
    what_if = result["summary"]["what_if_aggregate_by_mode"]
    corrected = result["summary"]["corrected_record_count_by_mode"]
    for mode, metrics in what_if.items():
        strict_metrics = strict.get(mode, {}) if isinstance(strict, dict) else {}
        lines.append(
            f"| `{mode}` | {_display_metric(strict_metrics.get('answer_correctness'))} | "
            f"{_display_metric(metrics.get('answer_correctness'))} | "
            f"{_display_metric(strict_metrics.get('unsupported_claim_rate'))} | "
            f"{_display_metric(metrics.get('unsupported_claim_rate'))} | "
            f"{corrected.get(mode, 0)} |"
        )
    lines.extend(
        [
            "",
            "## Decision Options",
            "",
            "| Option | Status | Main metric action | Required follow-up |",
            "| --- | --- | --- | --- |",
        ]
    )
    for option in result["summary"]["decision_options"]:
        lines.append(
            f"| `{option['id']}` | {option['decision_status']} | "
            f"{option['main_metric_action']} | {option['required_follow_up']} |"
        )
    lines.extend(
        [
            "",
            "## Case Decisions",
            "",
            "| Review ID | Source | Mode | Failure type | Profile policy | Profile extension |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in result["case_decisions"]:
        lines.append(
            f"| `{item['review_id']}` | `{item['source_id']}` | `{item['mode']}` | "
            f"{item['failure_type']} | {item['profile_policy_decision']} | "
            f"{item['profile_extension_decision']} |"
        )
    lines.extend(["", "## Claim Boundary", "", result["claim_boundary"]])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def _display_metric(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.4f}".rstrip("0").rstrip(".")
    return str(value)


def write_nasa_atmonto_s7_profile_decision(
    *,
    output_dir: str | Path,
    repo_root: str | Path = PROJECT_ROOT,
    report_name: str = "nasa_atmonto_s7_profile_decision",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_nasa_atmonto_s7_profile_decision(repo_root=repo_root)
    output = Path(output_dir)
    json_path = write_json_report(result, output / f"{report_name}.json")
    md_path = write_nasa_atmonto_s7_profile_decision_markdown(
        result,
        output / f"{report_name}.md",
    )
    return json_path, md_path, result
