from __future__ import annotations

from pathlib import Path
from typing import Any


def write_nasa_atmonto_s5_s6_live_agentic_pilot_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metrics = result["metrics"]
    lines = [
        f"# {result.get('display_name', 'NASA ATMONTO S5/S6 Live Agentic Pilot')}",
        "",
        "## Boundary",
        "",
        result["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- Status: `{result['status']}`",
        f"- Input records: {result['metadata']['record_count']}",
        f"- Independent from S4: `{result['metadata']['independent_from_s4']}`",
        f"- Live LLM run: `{result['metadata']['live_llm_run']}`",
        f"- Provider/model: `{result['metadata']['provider']}` / `{result['metadata']['model']}`",
        f"- Prompt version: `{result['metadata']['prompt_version']}`",
        f"- Run scope: `{result['metadata']['run_scope']}`",
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
    lines.extend(
        [
            "",
            "## Quality Counters",
            "",
            f"- Failed records: {result['quality_counters']['failed_record_count']}",
            f"- Failure type counts: `{result['quality_counters']['failure_type_counts']}`",
            f"- Extractor JSON adherence: {result['quality_counters']['extractor_json_adherence_count']}",
            f"- Final schema-valid records: {result['quality_counters']['final_schema_valid_record_count']}",
            f"- Refiner fallback count: {result['quality_counters']['refiner_fallback_count']}",
            f"- Agent call counts: `{result['quality_counters']['agent_call_counts']}`",
            "",
            "## Semantic Metrics",
            "",
            "| Layer | Predicted | TP | FP | FN | Precision | Recall | F1 |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    rows = [
        ("S5 validator accepted", metrics["s5_validator_accepted_semantic_metrics"]),
        ("S6 live refined", metrics["s6_live_refined_semantic_metrics"]),
    ]
    for label, row in rows:
        lines.append(
            f"| {label} | {row.get('predicted_fact_count')} | "
            f"{row.get('true_positive_count')} | {row.get('false_positive_count')} | "
            f"{row.get('false_negative_count')} | {row.get('precision')} | "
            f"{row.get('recall')} | {row.get('f1')} |"
        )
    lines.append(f"- Delta S6 minus S5: `{metrics['delta_s6_minus_s5']}`")
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
    lines.extend(["", "| CQ | Fact count |", "| --- | ---: |"])
    for cq_id, count in result["routing_summary"]["cq_fact_counts"].items():
        lines.append(f"| `{cq_id}` | {count} |")
    return lines
