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
    source_brief_report_name: str,
    srd_report_name: str,
    tip_report_name: str,
    plan_report_name: str,
    extraction_plan_report_name: str,
    validation_findings_report_name: str,
    evidence_support_findings_report_name: str,
    repair_plan_report_name: str,
) -> dict[str, Path]:
    output = Path(output_dir)
    paths = {
        "source_brief_markdown": output / f"{source_brief_report_name}.md",
        "srd_markdown": output / f"{srd_report_name}.md",
        "tip_markdown": output / f"{tip_report_name}.md",
        "plan_markdown": output / f"{plan_report_name}.md",
        "extraction_plan_markdown": output / f"{extraction_plan_report_name}.md",
        "validation_findings_markdown": output / f"{validation_findings_report_name}.md",
        "evidence_support_findings_markdown": output / f"{evidence_support_findings_report_name}.md",
        "repair_plan_markdown": output / f"{repair_plan_report_name}.md",
    }
    write_source_brief_markdown(result, paths["source_brief_markdown"])
    write_srd_markdown(result, paths["srd_markdown"])
    write_tip_markdown(result, paths["tip_markdown"])
    write_plan_markdown(result, paths["plan_markdown"])
    write_extraction_plan_markdown(result, paths["extraction_plan_markdown"])
    write_validation_findings_markdown(result, paths["validation_findings_markdown"])
    write_evidence_support_findings_markdown(result, paths["evidence_support_findings_markdown"])
    write_repair_plan_markdown(result, paths["repair_plan_markdown"])
    return paths


def write_source_brief_markdown(result: dict[str, Any], output_path: Path) -> Path:
    metadata = result["metadata"]
    lines = [
        "# ATCSCC Source Brief",
        "",
        "## Source Family",
        "",
        "- Domain corpus: retrospective FAA ATCSCC advisory records only.",
        f"- Boundary: {metadata['boundary']}",
        f"- Reviewed gold artifact: `{metadata['gold_path']}`",
        f"- CQ manifest: `{metadata['cq_manifest_path']}`",
        f"- Reference schema/profile: `{metadata['extraction_schema_path']}`",
        "- Support sources may explain terms, but they do not override the frozen advisory evidence.",
        "",
        "## Included Source Artifacts",
        "",
        "| Artifact | Path | Exists |",
        "| --- | --- | --- |",
    ]
    lines.extend(
        f"| `{item['name']}` | `{item['path']}` | `{item['exists']}` |"
        for item in result["artifact_inventory"]
    )
    lines.extend(
        [
            "",
            "## Non-Scope",
            "",
            "- Live air-traffic management decisions.",
            "- Complete NASA ATMONTO coverage beyond the ATCSCC application profile.",
            "- Facts inferred from aviation common sense without advisory evidence.",
            "",
        ]
    )
    return _write_lines(output_path, lines)


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


def write_extraction_plan_markdown(result: dict[str, Any], output_path: Path) -> Path:
    schema = result["schema_summary"]
    seed = result["srd_seed"]
    lines = [
        "# ATCSCC Extraction Plan",
        "",
        "## Extraction Boundary",
        "",
        "- Extract only source-bounded ATCSCC advisory facts required by the 12 primary CQs.",
        "- Preserve deterministic backbone fields before LLM semantic enrichment.",
        "- Route unsupported or ambiguous facts to abstention or repair; do not complete from common sense.",
        "",
        "## Required Schema Fields",
        "",
        f"- Top-level fields: `{', '.join(schema['required_top_level_fields']) or 'none'}`",
        f"- Fact fields: `{', '.join(schema['required_fact_fields']) or 'none'}`",
        f"- Available fact fields: `{', '.join(schema['fact_fields']) or 'none'}`",
        "",
        "## Predicate Coverage Plan",
        "",
        "| Predicate | CQ mentions | Extraction route | Evidence rule |",
        "| --- | ---: | --- | --- |",
    ]
    for predicate, count in seed["required_predicates"].items():
        route = "deterministic/backbone" if predicate in {"rdf:type", "advisoryNumber"} else "hybrid"
        lines.append(
            f"| `{predicate}` | {count} | `{route}` | Require source ID and advisory text excerpt. |"
        )
    lines.extend(
        [
            "",
            "## Implementation Layers",
            "",
        ]
    )
    lines.extend(f"- {layer}" for layer in result["tip_seed"]["implementation_layers"])
    lines.extend(
        [
            "",
            "## Abstention Rules",
            "",
            "- Missing field in the advisory: emit an explicit absent/unknown label only when the CQ requires it.",
            "- Unsupported value: quarantine rather than repair.",
            "- Out-of-profile predicate: report as a profile gap, not as existing ATMONTO truth.",
            "",
        ]
    )
    return _write_lines(output_path, lines)


def write_validation_findings_markdown(result: dict[str, Any], output_path: Path) -> Path:
    summary = result["prediction_validation_summary"]
    lines = [
        "# ATCSCC Validation Findings",
        "",
        "## Prediction Output Readiness",
        "",
        f"- Status: `{summary['status'] or 'missing'}`",
        f"- Selected source IDs: `{summary['selected_source_id_count']}`",
        f"- Error count: `{summary['error_count']}`",
        f"- Pending count: `{summary['pending_count']}`",
    ]
    lines.extend(_diagnostics_table(result))
    lines.extend(_code_review_section(result))
    lines.extend(
        [
            "",
            "## Validation Boundary",
            "",
            "- Schema validity is not semantic truth.",
            "- Semantic correctness is not operational readiness.",
            "- Abnormal metrics trigger code or artifact review before another extraction run.",
            "",
        ]
    )
    return _write_lines(output_path, lines)


def write_evidence_support_findings_markdown(result: dict[str, Any], output_path: Path) -> Path:
    evidence = result["srd_seed"]["evidence_contract"]
    lines = [
        "# ATCSCC Evidence Support Findings",
        "",
        "## Evidence Contract",
        "",
        f"- Evidence required: `{evidence['required']}`",
        f"- Current support unit: `{evidence['current_unit']}`",
        f"- Known gap: {evidence['known_gap']}.",
        "",
        "## Profile Gap Signals",
        "",
        "| Predicate | Rejected/adjudicated count | Treatment |",
        "| --- | ---: | --- |",
    ]
    profile_gaps = result["tip_seed"]["profile_gap_signals"]
    if profile_gaps:
        lines.extend(
            f"| `{predicate}` | {count} | Report as profile/application-scope boundary. |"
            for predicate, count in profile_gaps.items()
        )
    else:
        lines.append("| none | 0 | No current profile-gap signal. |")
    lines.extend(
        [
            "",
            "## Support Labels",
            "",
            "- `supported`: value is directly grounded in the cited advisory text.",
            "- `ambiguous`: source text is present but does not determine a unique value.",
            "- `unsupported`: no matching advisory evidence; fact must be rejected or quarantined.",
            "- `profile_gap`: source-supported candidate is outside the current ATCSCC profile slice.",
            "",
        ]
    )
    return _write_lines(output_path, lines)


def write_repair_plan_markdown(result: dict[str, Any], output_path: Path) -> Path:
    lines = [
        "# ATCSCC Repair Plan",
        "",
        "## Loop Policy",
        "",
        f"- Normal step: {result['loop_policy']['normal_step']}",
        f"- Abnormal step: {result['loop_policy']['abnormal_step']}",
        f"- Hard rule: {result['loop_policy']['hard_rule']}",
        "",
        "## Repair Routing",
        "",
        "| System | Recommended action | Flags |",
        "| --- | --- | --- |",
    ]
    for item in result["system_loop_diagnostics"]:
        flags = ", ".join(item.get("anomaly_flags", [])) or "none"
        lines.append(f"| `{item['system_id']}` | `{item['recommended_action']}` | `{flags}` |")
    lines.extend(_code_review_section(result))
    lines.extend(
        [
            "",
            "## Repair Bounds",
            "",
            "- Maximum repair cycles per item: 2.",
            "- Repair cannot introduce facts without explicit advisory evidence.",
            "- Profile extensions remain proposed gaps until separately reviewed.",
            "- Main strict metrics are preserved when reporting profile-decision what-if analyses.",
            "",
            "## Next Actions",
            "",
        ]
    )
    lines.extend(f"- {action}" for action in result["next_actions"])
    lines.append("")
    return _write_lines(output_path, lines)


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


def _write_lines(output_path: Path, lines: list[str]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
