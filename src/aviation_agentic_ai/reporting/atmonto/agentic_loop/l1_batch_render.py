from __future__ import annotations

from pathlib import Path
from typing import Any


def write_nasa_atmonto_l1_agent_batch_experiment_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metrics = result["metrics"]
    lines = [
        "# NASA ATMONTO L1 Agent Batch Experiment",
        "",
        "## Boundary",
        "",
        result["claim_boundary"],
        "",
        "## Summary",
        "",
        f"- Status: `{result['status']}`",
        f"- Records: {result['metadata']['record_count']}",
        f"- Live LLM run: `{result['metadata']['live_llm_run']}`",
        f"- Invoker: `{result['metadata']['invoker_label']}`",
        f"- Max iterations: {result['metadata']['max_iterations']}",
        f"- Baseline predictions: `{result['metadata']['baseline_predictions_path']}`",
        f"- Repair artifact: `{result['metadata']['repair_predictions_path']}`",
        f"- Prediction output: `{result['metadata']['prediction_output']}`",
        f"- Run metadata: `{result['metadata']['run_metadata_output']}`",
        "",
        "## Before vs After",
        "",
        "| Metric | Before baseline candidates | After L1 emitted facts | Delta |",
        "| --- | ---: | ---: | ---: |",
        _metric_row(result, "Accepted facts", "accepted_fact_count"),
        _metric_row(result, "Schema violations", "schema_violation_count"),
        _metric_row(result, "Unsupported facts", "unsupported_fact_count"),
        _metric_row(result, "Evidence-in-source rate", "evidence_in_source_rate"),
        "",
        "### Metric Definitions",
        "",
        f"- Schema violations: {result['metric_definitions']['schema_violation_count']}",
        f"- Unsupported facts: {result['metric_definitions']['unsupported_fact_count']}",
        f"- Evidence-in-source rate: {result['metric_definitions']['evidence_in_source_rate']}",
        f"- Repair success rate: {result['metric_definitions']['repair_success_rate']}",
        "",
        "### Interpretation",
        "",
        f"- {result['interpretation']['schema_gate_result']}",
        f"- {result['interpretation']['unsupported_fact_result']}",
        f"- {result['interpretation']['evidence_result']}",
        "",
        "## Repair",
        "",
        f"- Repair attempted records: {metrics['repair']['repair_attempted_record_count']}",
        f"- Records with fact gain: {metrics['repair']['records_with_fact_gain']}",
        f"- Net accepted fact gain: {metrics['repair']['net_accepted_fact_gain']}",
        f"- Repair success rate: {metrics['repair']['repair_success_rate']}",
        "",
        "## Example Records",
        "",
        "| Source | Iterations | Before accepted | After accepted | Before schema violations | Before unsupported |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result.get("record_examples", []):
        before = row.get("before") or {}
        after = row.get("after") or {}
        lines.append(
            f"| `{row.get('source_id')}` | {row.get('iterations_used')} | "
            f"{before.get('accepted_fact_count')} | {after.get('accepted_fact_count')} | "
            f"{before.get('schema_violation_count')} | {before.get('unsupported_fact_count')} |"
        )
    lines.extend(
        [
            "",
            "## Claim Use",
            "",
            "- Use this report as evidence that the L1 loop is connected to a repeatable ATCSCC batch run.",
            "- Treat the current run as artifact-replay diagnostics, not live autonomous LLM performance.",
            "- The next stronger experiment is a live or fixed-model LLM run under the same metrics.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _metric_row(result: dict[str, Any], label: str, field: str) -> str:
    metrics = result["metrics"]
    return (
        f"| {label} | {metrics['before'].get(field)} | {metrics['after'].get(field)} | "
        f"{metrics['delta_after_minus_before'].get(field)} |"
    )
