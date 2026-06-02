from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_agentic_loop_markdown(result: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metadata = result["metadata"]
    lines = [
        "# NASA ATMONTO Agentic Extraction-Validation Loop",
        "",
        "## Scope",
        "",
        f"- Boundary: {metadata['boundary']}",
        f"- CQ manifest: `{metadata['cq_manifest_path']}`",
        f"- Scoring report: `{metadata['scoring_path']}`",
        f"- Prediction validation: `{metadata['prediction_validation_path']}`",
        f"- Status: `{result['status']}`",
        "",
        "## Multi-Paper Method Transfer",
        "",
    ]
    lines.extend(
        f"- **{item['family']}**: {item['transferred_principle']}"
        for item in result["method_families"]
    )
    lines.extend(_pipeline_table(result))
    lines.extend(_artifact_table(result))
    lines.extend(_diagnostics_table(result))
    lines.extend(_code_review_section(result))
    lines.extend(_srd_tip_seed_section(result))
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in result["next_actions"])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_agentic_supporting_artifacts(
    result: dict[str, Any],
    output_dir: str | Path,
    *,
    srd_report_name: str,
    tip_report_name: str,
    plan_report_name: str,
) -> dict[str, Path]:
    output = Path(output_dir)
    paths = {
        "srd_markdown": output / f"{srd_report_name}.md",
        "tip_markdown": output / f"{tip_report_name}.md",
        "plan_markdown": output / f"{plan_report_name}.md",
    }
    write_srd_markdown(result, paths["srd_markdown"])
    write_tip_markdown(result, paths["tip_markdown"])
    write_plan_markdown(result, paths["plan_markdown"])
    return paths


def write_srd_markdown(result: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    seed = result["srd_seed"]
    lines = [
        "# ATCSCC Semantic Requirements Document",
        "",
        "## Boundary",
        "",
        f"- {result['metadata']['boundary']}",
        "- NASA ATMONTO is the primary ontology/profile reference for this experiment.",
        "- The gold set is reviewed retrospective ATCSCC advisory evidence, not live truth.",
        "",
        "## Competency Question Contract",
        "",
        f"- CQ count: {seed['competency_question_count']}",
        f"- Route counts: `{json.dumps(seed['route_counts'], sort_keys=True)}`",
        "",
        "## Required Predicates",
        "",
        "| Predicate | CQ mentions |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{predicate}` | {count} |" for predicate, count in seed["required_predicates"].items())
    lines.extend(["", "## Subject Classes", "", "| Class | Records |", "| --- | ---: |"])
    lines.extend(f"| `{class_name}` | {count} |" for class_name, count in seed["subject_classes"].items())
    lines.extend(
        [
            "",
            "## Evidence Contract",
            "",
            "- Every extracted fact must carry source-bounded `evidence_text`.",
            "- Facts without source support must be rejected or marked for abstention.",
            f"- Known gap: {seed['evidence_contract']['known_gap']}.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def write_tip_markdown(result: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    seed = result["tip_seed"]
    lines = [
        "# ATCSCC Technical Implementation Plan",
        "",
        "## Baseline Decision",
        "",
        f"- Accepted current baselines: `{', '.join(seed['accepted_baselines']) or 'none'}`",
        f"- Systems requiring review: `{', '.join(seed['systems_requiring_review']) or 'none'}`",
        "",
        "## Implementation Layers",
        "",
    ]
    lines.extend(f"- {layer}" for layer in seed["implementation_layers"])
    lines.extend(["", "## Profile Gap Signals", "", "| Predicate | Rejected/adjudicated count |", "| --- | ---: |"])
    lines.extend(
        f"| `{predicate}` | {count} |" for predicate, count in seed["profile_gap_signals"].items()
    )
    lines.extend(["", "## Review Gates", ""])
    if result["code_review_triggers"]:
        lines.extend(
            f"- `{trigger['system_id']}`: review {', '.join(trigger['review_focus'])} "
            f"before `{trigger['required_before']}`."
            for trigger in result["code_review_triggers"]
        )
    else:
        lines.append("- No code review gate is currently active.")
    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def write_plan_markdown(result: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# ATCSCC Extraction-Validation Plan",
        "",
        "## Loop Policy",
        "",
        f"- Normal step: {result['loop_policy']['normal_step']}",
        f"- Abnormal step: {result['loop_policy']['abnormal_step']}",
        f"- Hard rule: {result['loop_policy']['hard_rule']}",
        "",
        "## System Routing",
        "",
        "| System | Action | Flags |",
        "| --- | --- | --- |",
    ]
    for item in result["system_loop_diagnostics"]:
        flags = ", ".join(item.get("anomaly_flags", [])) or "none"
        lines.append(f"| `{item['system_id']}` | `{item['recommended_action']}` | `{flags}` |")
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"- {action}" for action in result["next_actions"])
    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def _pipeline_table(result: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "## Domain-Independent Pipeline",
        "",
        "| Stage | Name | Role |",
        "| --- | --- | --- |",
    ]
    lines.extend(
        f"| `{stage['stage_id']}` | `{stage['name']}` | {stage['role']} |"
        for stage in result["domain_independent_pipeline"]
    )
    return lines


def _artifact_table(result: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "## Generated Artifacts",
        "",
        "| Artifact | Status | Path | Purpose |",
        "| --- | --- | --- | --- |",
    ]
    lines.extend(
        f"| `{artifact['artifact']}` | `{artifact['status']}` | `{artifact['path']}` | "
        f"{artifact['purpose']} |"
        for artifact in result["agentic_artifacts"]
    )
    return lines


def _diagnostics_table(result: dict[str, Any]) -> list[str]:
    lines = [
        "",
        "## Agentic Loop Diagnostics",
        "",
        "| System | F1 | Schema violation | Structural acceptance | JSON adherence | Action | Flags |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for item in result["system_loop_diagnostics"]:
        flags = ", ".join(item.get("anomaly_flags", [])) or "none"
        lines.append(
            f"| `{item['system_id']}` | {item['f1']} | {item['schema_violation_rate']} | "
            f"{item['structural_acceptance_rate']} | {item['json_adherence']} | "
            f"`{item['recommended_action']}` | `{flags}` |"
        )
    return lines


def _code_review_section(result: dict[str, Any]) -> list[str]:
    lines = ["", "## Code Review Triggers", ""]
    if not result["code_review_triggers"]:
        lines.append("- None.")
        return lines
    lines.extend(
        f"- `{trigger['system_id']}`: flags=`{', '.join(trigger['flags'])}`; "
        f"focus={'; '.join(trigger['review_focus'])}"
        for trigger in result["code_review_triggers"]
    )
    return lines


def _srd_tip_seed_section(result: dict[str, Any]) -> list[str]:
    return [
        "",
        "## SRD Seed",
        "",
        f"- Competency questions: {result['srd_seed']['competency_question_count']}",
        f"- Route counts: `{json.dumps(result['srd_seed']['route_counts'], sort_keys=True)}`",
        f"- Required predicates: "
        f"`{json.dumps(result['srd_seed']['required_predicates'], sort_keys=True)}`",
        f"- Subject classes: "
        f"`{json.dumps(result['srd_seed']['subject_classes'], sort_keys=True)}`",
        "",
        "## TIP Seed",
        "",
        f"- Accepted baselines: `{', '.join(result['tip_seed']['accepted_baselines']) or 'none'}`",
        f"- Systems requiring review: "
        f"`{', '.join(result['tip_seed']['systems_requiring_review']) or 'none'}`",
    ]
