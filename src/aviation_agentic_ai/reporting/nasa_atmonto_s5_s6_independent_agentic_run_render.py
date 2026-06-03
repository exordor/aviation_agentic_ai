from __future__ import annotations

from pathlib import Path
from typing import Any


def write_nasa_atmonto_s5_s6_independent_agentic_run_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO S5/S6 Independent Agentic Run",
        "",
        "## Boundary",
        "",
        result["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- Status: `{result['status']}`",
        f"- Input records: {result['metadata']['record_count']}",
        f"- Extractor input system: `{result['metadata']['extractor_input_system_id']}`",
        f"- Independent from S4: `{result['metadata']['independent_from_s4']}`",
        f"- Live LLM run: `{result['metadata']['live_llm_run']}`",
        f"- S5 accepted facts: {result['metadata']['s5_fact_count']}",
        f"- S6 refined facts: {result['metadata']['s6_fact_count']}",
        f"- Quarantined facts: {result['metadata']['quarantined_fact_count']}",
        f"- Prediction output: `{result['metadata']['prediction_output']}`",
        f"- Run metadata: `{result['metadata']['run_metadata_output']}`",
        "",
        "## Agent Roles",
        "",
        "| Agent | Input | Operation | Output |",
        "| --- | --- | --- | --- |",
    ]
    for role in result["agent_roles"]:
        lines.append(
            f"| `{role['agent']}` | {role['input']} | {role['operation']} | {role['output']} |"
        )
    lines.extend(_metrics_table(result))
    lines.extend(_quarantine_section(result))
    lines.extend(_routing_section(result))
    lines.extend(
        [
            "",
            "## SOTA Interpretation",
            "",
            f"- Satisfied: {result['sota_interpretation']['what_is_satisfied']}",
            f"- Remaining gap: {result['sota_interpretation']['remaining_gap']}",
            f"- Claim use: {result['sota_interpretation']['claim_use']}",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _metrics_table(result: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "## Semantic Metrics",
        "",
        "| Layer | Predicted | TP | FP | FN | Precision | Recall | F1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    rows = [
        ("S0 reported", result["metrics"]["s0_reported_semantic_metrics"]),
        ("S5 validator accepted", result["metrics"]["s5_validator_accepted_semantic_metrics"]),
        ("S6 critic refined", result["metrics"]["s6_critic_refined_semantic_metrics"]),
    ]
    for label, metrics in rows:
        lines.append(
            f"| {label} | {metrics.get('predicted_fact_count')} | "
            f"{metrics.get('true_positive_count')} | {metrics.get('false_positive_count')} | "
            f"{metrics.get('false_negative_count')} | {metrics.get('precision')} | "
            f"{metrics.get('recall')} | {metrics.get('f1')} |"
        )
    lines.extend(
        [
            "",
            f"- Delta S6 minus S5: `{result['metrics']['delta_s6_minus_s5']}`",
            f"- Delta S6 minus S0: `{result['metrics']['delta_s6_minus_s0_reported']}`",
        ]
    )
    return lines


def _quarantine_section(result: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "## Critic / Refiner Quarantine",
        "",
        "| Reason | Fact count |",
        "| --- | ---: |",
    ]
    for reason, count in result["quarantine_summary"]["reason_counts"].items():
        lines.append(f"| `{reason}` | {count} |")
    lines.extend(["", "### Examples", ""])
    examples = result["quarantine_summary"]["examples"]
    if not examples:
        lines.append("- None.")
        return lines
    for item in examples:
        reasons = ", ".join(item["reasons"])
        lines.append(
            f"- `{item.get('source_id')}` `{item.get('predicate')}` "
            f"`{item.get('fact_id')}`: {reasons}"
        )
    return lines


def _routing_section(result: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "## CQ / Module Routing",
        "",
        "| Module | Fact count |",
        "| --- | ---: |",
    ]
    for module, count in result["routing_summary"]["module_counts"].items():
        lines.append(f"| `{module}` | {count} |")
    lines.extend(["", f"- Unmapped facts: {result['routing_summary']['unmapped_fact_count']}"])
    return lines
