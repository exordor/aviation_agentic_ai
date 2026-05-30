from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from aviation_agentic_ai.evaluation.bootstrap_ci import bootstrap_metric_ci
from aviation_agentic_ai.evaluation.gold import GoldLabel, load_gold_labels
from aviation_agentic_ai.paths import project_relative_path
from aviation_agentic_ai.retrieval.sufficiency import (
    detect_risk_category,
    evaluate_evidence_sufficiency,
)


def _load_json(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.exists():
        return {}
    data = json.loads(source.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"value": data}


def _records_by_cq(retrieval_report: dict[str, Any], scenario_name: str | None) -> dict[str, dict[str, Any]]:
    scenarios = retrieval_report.get("scenarios", {})
    scenario: dict[str, Any] = {}
    if scenario_name and scenario_name in scenarios:
        scenario = scenarios[scenario_name]
    elif "hybrid_hops2_v5_h8" in scenarios:
        scenario = scenarios["hybrid_hops2_v5_h8"]
    elif "hybrid_vector_traversal_guarded" in scenarios:
        scenario = scenarios["hybrid_vector_traversal_guarded"]
    elif "vector_hops2_v5_h8" in scenarios:
        scenario = scenarios["vector_hops2_v5_h8"]
    elif scenarios:
        scenario = next(iter(scenarios.values()))
    return {
        str(record.get("cq_id")): record
        for record in scenario.get("records", [])
        if isinstance(record, dict)
    }


def _retrieval_result_from_record(record: dict[str, Any] | None) -> dict[str, Any]:
    if not record:
        return {"fused_chunks": [], "graph_triples": [], "graph_paths": []}
    return {
        "fused_chunks": record.get("hits", []),
        "graph_triples": record.get("graph_triples", []),
        "graph_paths": record.get("graph_paths", []),
    }


def _expected_risk(label: GoldLabel) -> str:
    return detect_risk_category(label.question)[0]


def _safe_rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def build_sufficiency_evaluation(
    gold_labels_path: str | Path,
    retrieval_report_path: str | Path,
    *,
    scenario_name: str | None = None,
) -> dict[str, Any]:
    labels = load_gold_labels(gold_labels_path)
    retrieval_report = _load_json(retrieval_report_path)
    retrieval_records = _records_by_cq(retrieval_report, scenario_name)
    records: list[dict[str, Any]] = []
    for label in labels.values():
        retrieval_record = retrieval_records.get(label.cq_id)
        decision = evaluate_evidence_sufficiency(
            label.question,
            _retrieval_result_from_record(retrieval_record),
            gold_label=label,
        )
        expected_decision = "abstain" if label.expected_abstention else "answer"
        expected_risk = _expected_risk(label)
        boundary_violation = (
            label.expected_abstention
            and decision["decision"] == "answer"
        ) or (
            decision["risk_category"] != "training_question"
            and decision["decision"] == "answer"
        )
        records.append(
            {
                "cq_id": label.cq_id,
                "question": label.question,
                "question_type": label.question_type,
                "expected_decision": expected_decision,
                "expected_risk_category": expected_risk,
                "expected_abstention": label.expected_abstention,
                "decision": decision,
                "correct_decision": decision["decision"] == expected_decision,
                "risk_category_correct": decision["risk_category"] == expected_risk,
                "boundary_violation": boundary_violation,
            }
        )

    supported = [record for record in records if not record["expected_abstention"]]
    no_answer = [record for record in records if record["expected_abstention"]]
    supported_answer_correct = sum(
        int(record["decision"]["decision"] == "answer") for record in supported
    )
    no_answer_abstain_correct = sum(
        int(record["decision"]["decision"] == "abstain") for record in no_answer
    )
    false_answers = sum(int(record["decision"]["decision"] == "answer") for record in no_answer)
    false_abstentions = sum(
        int(record["decision"]["decision"] == "abstain") for record in supported
    )
    risk_correct = sum(int(record["risk_category_correct"]) for record in records)
    boundary_violations = sum(int(record["boundary_violation"]) for record in records)
    risk_counts = Counter(record["decision"]["risk_category"] for record in records)
    no_answer_ids = {record["cq_id"] for record in no_answer}
    supported_ids = {record["cq_id"] for record in supported}
    return {
        "metadata": {
            "gold_labels_path": project_relative_path(gold_labels_path),
            "retrieval_report_path": project_relative_path(retrieval_report_path),
            "scenario_name": scenario_name,
            "labels_total": len(records),
            "supported_total": len(supported),
            "insufficient_evidence_total": len(no_answer),
            "scoring_policy": "sufficiency_and_safety_metrics_separate_from_retrieval",
        },
        "metrics": {
            "abstention_accuracy": _safe_rate(
                no_answer_abstain_correct,
                len(no_answer),
            ),
            "supported_answer_decision_accuracy": _safe_rate(
                supported_answer_correct,
                len(supported),
            ),
            "insufficient_evidence_abstention_accuracy": _safe_rate(
                no_answer_abstain_correct,
                len(no_answer),
            ),
            "false_answer_rate": _safe_rate(
                false_answers,
                len(no_answer),
            ),
            "false_answer_rate_on_no_answer_questions": _safe_rate(
                false_answers,
                len(no_answer),
            ),
            "false_abstention_rate": _safe_rate(
                false_abstentions,
                len(supported),
            ),
            "false_abstention_rate_on_supported_questions": _safe_rate(
                false_abstentions,
                len(supported),
            ),
            "risk_category_accuracy": _safe_rate(risk_correct, len(records)),
            "advisory_boundary_violation_count": boundary_violations,
            "boundary_violation_count": boundary_violations,
            "risk_category_counts": dict(sorted(risk_counts.items())),
        },
        "confidence_intervals": {
            "abstention_accuracy": bootstrap_metric_ci(
                no_answer,
                lambda record: record["decision"]["decision"] == "abstain",
            ),
            "false_answer_rate": bootstrap_metric_ci(
                no_answer,
                lambda record: record["decision"]["decision"] == "answer",
            ),
            "false_abstention_rate": bootstrap_metric_ci(
                supported,
                lambda record: record["decision"]["decision"] == "abstain",
            ),
            "risk_category_accuracy": bootstrap_metric_ci(
                records,
                lambda record: bool(record["risk_category_correct"]),
            ),
            "ci_policy": {
                "method": "deterministic_bootstrap_mean",
                "confidence": 0.95,
                "samples": 1000,
                "no_answer_records": len(no_answer_ids),
                "supported_records": len(supported_ids),
            },
        },
        "records": records,
    }


def write_sufficiency_evaluation_json(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_sufficiency_evaluation_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metrics = result["metrics"]
    lines = [
        "# Sufficiency Evaluation",
        "",
        f"- Gold labels: `{result['metadata']['gold_labels_path']}`",
        f"- Retrieval report: `{result['metadata']['retrieval_report_path']}`",
        f"- Labels: {result['metadata']['labels_total']}",
        f"- Supported labels: {result['metadata']['supported_total']}",
        f"- Insufficient-evidence labels: {result['metadata']['insufficient_evidence_total']}",
        "- Metrics are safety/evidence sufficiency metrics and are not mixed with retrieval scores.",
        "- Confidence intervals: deterministic bootstrap 95% CIs over benchmark labels.",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Supported answer decision accuracy | {metrics['supported_answer_decision_accuracy']} |",
        f"| Abstention accuracy | {metrics['abstention_accuracy']} |",
        f"| Insufficient-evidence abstention accuracy | {metrics['insufficient_evidence_abstention_accuracy']} |",
        f"| False answer rate | {metrics['false_answer_rate']} |",
        f"| False answer rate on no-answer questions | {metrics['false_answer_rate_on_no_answer_questions']} |",
        f"| False abstention rate | {metrics['false_abstention_rate']} |",
        f"| False abstention rate on supported questions | {metrics['false_abstention_rate_on_supported_questions']} |",
        f"| Risk-category accuracy | {metrics['risk_category_accuracy']} |",
        f"| Advisory boundary violation count | {metrics['advisory_boundary_violation_count']} |",
        f"| Boundary violation count | {metrics['boundary_violation_count']} |",
        "",
        "## Risk Categories",
        "",
        "| Risk category | Count |",
        "| --- | ---: |",
    ]
    for category, count in metrics["risk_category_counts"].items():
        lines.append(f"| {category} | {count} |")
    lines.extend(["", "## Decision Errors", ""])
    errors = [record for record in result["records"] if not record["correct_decision"]]
    if not errors:
        lines.append("- none")
    else:
        for record in errors[:30]:
            lines.append(
                f"- `{record['cq_id']}` expected {record['expected_decision']} but "
                f"got {record['decision']['decision']}: {record['decision']['reason']}"
            )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def write_sufficiency_evaluation(
    gold_labels_path: str | Path,
    retrieval_report_path: str | Path,
    output_dir: str | Path,
    *,
    scenario_name: str | None = None,
    report_name: str = "sufficiency_evaluation",
) -> tuple[Path, Path, dict[str, Any]]:
    result = build_sufficiency_evaluation(
        gold_labels_path,
        retrieval_report_path,
        scenario_name=scenario_name,
    )
    output = Path(output_dir)
    stem = Path(report_name).stem or "sufficiency_evaluation"
    json_path = write_sufficiency_evaluation_json(result, output / f"{stem}.json")
    md_path = write_sufficiency_evaluation_markdown(result, output / f"{stem}.md")
    return json_path, md_path, result
