from __future__ import annotations

from pathlib import Path
from typing import Any


def write_nasa_atmonto_s5_s6_agentic_loop_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# NASA ATMONTO S5/S6 Agentic Evidence Loop",
        "",
        "## Boundary",
        "",
        result["metadata"]["boundary"],
        "",
        "## Summary",
        "",
        f"- Input system: `{result['metadata']['input_system_id']}`",
        f"- Records: {result['metadata']['record_count']}",
        f"- S5 routed facts: {result['metadata']['s5_fact_count']}",
        f"- S6 evidence-gated facts: {result['metadata']['s6_fact_count']}",
        f"- S5 unique scored facts: {result['metadata']['s5_unique_scored_fact_count']}",
        f"- S6 unique scored facts: {result['metadata']['s6_unique_scored_fact_count']}",
        f"- Quarantined facts: {result['metadata']['quarantined_fact_count']}",
        f"- Strict main metrics changed: {result['metadata']['strict_main_metrics_changed']}",
        f"- Independent live LLM run: {result['metadata']['independent_live_llm_run']}",
        "",
        "## Stage Definitions",
        "",
        "| Stage | Input | Operation | Claim boundary |",
        "| --- | --- | --- | --- |",
    ]
    for stage in result["stage_definitions"]:
        lines.append(
            f"| `{stage['system_id']}` | {stage['input']} | {stage['operation']} | "
            f"{stage['claim_boundary']} |"
        )
    lines.extend(_metrics_table(result))
    lines.extend(_routing_table(result))
    lines.extend(_quarantine_section(result))
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
        ("S4 reported", result["metrics"]["s4_reported_semantic_metrics"]),
        ("S5 routed", result["metrics"]["s5_routed_semantic_metrics"]),
        ("S6 evidence-gated", result["metrics"]["s6_evidence_gated_semantic_metrics"]),
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
        ]
    )
    return lines


def _routing_table(result: dict[str, Any]) -> list[str]:
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


def _quarantine_section(result: dict[str, Any]) -> list[str]:
    gate = result["evidence_gate"]
    lines = [
        "",
        "## Evidence Gate",
        "",
        f"- Supported facts: {gate['supported_fact_count']}",
        f"- Quarantined facts: {gate['quarantined_fact_count']}",
        f"- Support rate: {gate['support_rate']}",
        "",
        "### Quarantine Examples",
        "",
    ]
    if not gate["quarantine_examples"]:
        lines.append("- None.")
        return lines
    for item in gate["quarantine_examples"]:
        lines.append(
            f"- `{item.get('source_id')}` `{item.get('predicate')}` "
            f"`{item.get('fact_id')}`: evidence was not contained in the source text."
        )
    return lines
