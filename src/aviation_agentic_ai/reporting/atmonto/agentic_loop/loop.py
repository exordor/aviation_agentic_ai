from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report
from aviation_agentic_ai.reporting.atmonto.agentic_loop.diagnostics import (
    build_code_review_triggers,
    build_system_loop_diagnostics,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.contract import (
    DEFAULT_CQ_MANIFEST_PATH,
    DEFAULT_EVIDENCE_SUPPORT_FINDINGS_REPORT_NAME,
    DEFAULT_EXTRACTION_PLAN_REPORT_NAME,
    DEFAULT_EXTRACTION_SCHEMA_PATH,
    DEFAULT_PLAN_REPORT_NAME,
    DEFAULT_PREDICTION_VALIDATION_PATH,
    DEFAULT_REPAIR_PLAN_REPORT_NAME,
    DEFAULT_SOURCE_BRIEF_REPORT_NAME,
    DEFAULT_SRD_REPORT_NAME,
    DEFAULT_TIP_REPORT_NAME,
    DEFAULT_VALIDATION_FINDINGS_REPORT_NAME,
    METHOD_FAMILIES,
    PIPELINE_STAGES,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.loop_render import (
    write_agentic_loop_markdown,
    write_agentic_supporting_artifacts,
)
from aviation_agentic_ai.reporting.nasa_atmonto_cq import (
    DEFAULT_GOLD_PATH,
    DEFAULT_REJECTION_ADJUDICATION_PATH,
    DEFAULT_SCORING_PATH,
    DEFAULT_SEMANTIC_GROUPS_PATH,
    build_nasa_atmonto_cq_evaluation,
    normalize_atmonto_predicate,
)


def build_nasa_atmonto_agentic_loop(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    gold_path: str | Path = DEFAULT_GOLD_PATH,
    scoring_path: str | Path = DEFAULT_SCORING_PATH,
    semantic_groups_path: str | Path = DEFAULT_SEMANTIC_GROUPS_PATH,
    rejection_adjudication_path: str | Path = DEFAULT_REJECTION_ADJUDICATION_PATH,
    cq_manifest_path: str | Path = DEFAULT_CQ_MANIFEST_PATH,
    prediction_validation_path: str | Path = DEFAULT_PREDICTION_VALIDATION_PATH,
    extraction_schema_path: str | Path = DEFAULT_EXTRACTION_SCHEMA_PATH,
    generated_artifacts: dict[str, str] | None = None,
) -> dict[str, Any]:
    root = Path(repo_root)
    generated = generated_artifacts or _default_generated_artifacts()
    cq_evaluation = build_nasa_atmonto_cq_evaluation(
        repo_root=root,
        gold_path=gold_path,
        scoring_path=scoring_path,
        semantic_groups_path=semantic_groups_path,
        rejection_adjudication_path=rejection_adjudication_path,
    )
    scoring = _read_optional_json(root, scoring_path)
    cq_manifest = _read_optional_json(root, cq_manifest_path)
    prediction_validation = _read_optional_json(root, prediction_validation_path)
    extraction_schema = _read_optional_json(root, extraction_schema_path)
    diagnostics = build_system_loop_diagnostics(scoring, prediction_validation)
    code_review_triggers = build_code_review_triggers(diagnostics)
    result: dict[str, Any] = {
        "source_family": "nasa_atmonto_agentic_loop",
        "status": _loop_status(code_review_triggers),
        "metadata": _metadata(
            root=root,
            gold_path=gold_path,
            scoring_path=scoring_path,
            semantic_groups_path=semantic_groups_path,
            rejection_adjudication_path=rejection_adjudication_path,
            cq_manifest_path=cq_manifest_path,
            prediction_validation_path=prediction_validation_path,
            extraction_schema_path=extraction_schema_path,
            generated_artifacts=generated,
        ),
        "method_families": list(METHOD_FAMILIES),
        "domain_independent_pipeline": list(PIPELINE_STAGES),
        "artifact_inventory": _artifact_inventory(
            root,
            {
                "gold": gold_path,
                "scoring": scoring_path,
                "semantic_groups": semantic_groups_path,
                "rejection_adjudication": rejection_adjudication_path,
                "cq_manifest": cq_manifest_path,
                "prediction_validation": prediction_validation_path,
                "extraction_schema": extraction_schema_path,
            },
        ),
        "cq_evaluation_status": cq_evaluation["status"],
        "gold_summary": cq_evaluation["gold_summary"],
        "cq_manifest_summary": _cq_manifest_summary(cq_manifest),
        "schema_summary": _schema_summary(extraction_schema),
        "prediction_validation_summary": _prediction_validation_summary(prediction_validation),
        "system_loop_diagnostics": diagnostics,
        "code_review_triggers": code_review_triggers,
        "agentic_artifacts": [],
        "srd_seed": _build_srd_seed(cq_evaluation, cq_manifest, extraction_schema),
        "tip_seed": _build_tip_seed(cq_evaluation, diagnostics),
        "loop_policy": {
            "normal_step": "run extractor -> validator -> critic -> repair/abstain -> score",
            "abnormal_step": "if anomaly_flags are emitted, review code or artifact contract before rerun",
            "hard_rule": "Do not explain abnormal results without routing them to review_code or review_artifact.",
        },
        "next_actions": _next_actions(code_review_triggers),
    }
    result["agentic_artifacts"] = _agent_artifacts(result)
    return result


def write_nasa_atmonto_agentic_loop_json(result: dict[str, Any], output_path: str | Path) -> Path:
    return write_json_report(result, output_path, sort_keys=False)


def write_nasa_atmonto_agentic_loop_markdown(
    result: dict[str, Any],
    output_path: str | Path,
) -> Path:
    return write_agentic_loop_markdown(result, output_path)


def write_nasa_atmonto_agentic_loop(
    *,
    output_dir: str | Path,
    report_name: str = "nasa_atmonto_agentic_loop",
    repo_root: str | Path = PROJECT_ROOT,
    gold_path: str | Path = DEFAULT_GOLD_PATH,
    scoring_path: str | Path = DEFAULT_SCORING_PATH,
    semantic_groups_path: str | Path = DEFAULT_SEMANTIC_GROUPS_PATH,
    rejection_adjudication_path: str | Path = DEFAULT_REJECTION_ADJUDICATION_PATH,
    cq_manifest_path: str | Path = DEFAULT_CQ_MANIFEST_PATH,
    prediction_validation_path: str | Path = DEFAULT_PREDICTION_VALIDATION_PATH,
    extraction_schema_path: str | Path = DEFAULT_EXTRACTION_SCHEMA_PATH,
) -> tuple[Path, Path, dict[str, Any]]:
    output = Path(output_dir)
    generated = {
        "source_brief_markdown": project_relative_path(
            output / f"{DEFAULT_SOURCE_BRIEF_REPORT_NAME}.md",
            PROJECT_ROOT,
        ),
        "srd_markdown": project_relative_path(output / f"{DEFAULT_SRD_REPORT_NAME}.md", PROJECT_ROOT),
        "tip_markdown": project_relative_path(output / f"{DEFAULT_TIP_REPORT_NAME}.md", PROJECT_ROOT),
        "plan_markdown": project_relative_path(output / f"{DEFAULT_PLAN_REPORT_NAME}.md", PROJECT_ROOT),
        "extraction_plan_markdown": project_relative_path(
            output / f"{DEFAULT_EXTRACTION_PLAN_REPORT_NAME}.md",
            PROJECT_ROOT,
        ),
        "validation_findings_markdown": project_relative_path(
            output / f"{DEFAULT_VALIDATION_FINDINGS_REPORT_NAME}.md",
            PROJECT_ROOT,
        ),
        "evidence_support_findings_markdown": project_relative_path(
            output / f"{DEFAULT_EVIDENCE_SUPPORT_FINDINGS_REPORT_NAME}.md",
            PROJECT_ROOT,
        ),
        "repair_plan_markdown": project_relative_path(
            output / f"{DEFAULT_REPAIR_PLAN_REPORT_NAME}.md",
            PROJECT_ROOT,
        ),
    }
    result = build_nasa_atmonto_agentic_loop(
        repo_root=repo_root,
        gold_path=gold_path,
        scoring_path=scoring_path,
        semantic_groups_path=semantic_groups_path,
        rejection_adjudication_path=rejection_adjudication_path,
        cq_manifest_path=cq_manifest_path,
        prediction_validation_path=prediction_validation_path,
        extraction_schema_path=extraction_schema_path,
        generated_artifacts=generated,
    )
    write_agentic_supporting_artifacts(
        result,
        output,
        source_brief_report_name=DEFAULT_SOURCE_BRIEF_REPORT_NAME,
        srd_report_name=DEFAULT_SRD_REPORT_NAME,
        tip_report_name=DEFAULT_TIP_REPORT_NAME,
        plan_report_name=DEFAULT_PLAN_REPORT_NAME,
        extraction_plan_report_name=DEFAULT_EXTRACTION_PLAN_REPORT_NAME,
        validation_findings_report_name=DEFAULT_VALIDATION_FINDINGS_REPORT_NAME,
        evidence_support_findings_report_name=DEFAULT_EVIDENCE_SUPPORT_FINDINGS_REPORT_NAME,
        repair_plan_report_name=DEFAULT_REPAIR_PLAN_REPORT_NAME,
    )
    json_path = write_nasa_atmonto_agentic_loop_json(result, output / f"{report_name}.json")
    md_path = write_nasa_atmonto_agentic_loop_markdown(result, output / f"{report_name}.md")
    return json_path, md_path, result


def _default_generated_artifacts() -> dict[str, str]:
    return {
        "source_brief_markdown": f"reports/stages/{DEFAULT_SOURCE_BRIEF_REPORT_NAME}.md",
        "srd_markdown": f"reports/stages/{DEFAULT_SRD_REPORT_NAME}.md",
        "tip_markdown": f"reports/stages/{DEFAULT_TIP_REPORT_NAME}.md",
        "plan_markdown": f"reports/stages/{DEFAULT_PLAN_REPORT_NAME}.md",
        "extraction_plan_markdown": f"reports/stages/{DEFAULT_EXTRACTION_PLAN_REPORT_NAME}.md",
        "validation_findings_markdown": f"reports/stages/{DEFAULT_VALIDATION_FINDINGS_REPORT_NAME}.md",
        "evidence_support_findings_markdown": (
            f"reports/stages/{DEFAULT_EVIDENCE_SUPPORT_FINDINGS_REPORT_NAME}.md"
        ),
        "repair_plan_markdown": f"reports/stages/{DEFAULT_REPAIR_PLAN_REPORT_NAME}.md",
    }


def _loop_status(code_review_triggers: list[dict[str, Any]]) -> str:
    if code_review_triggers:
        return "agentic_loop_ready_with_code_review_triggers"
    return "agentic_loop_ready_for_srd_tip"


def _artifact_path(root: Path, value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def _read_optional_json(root: Path, value: str | Path) -> dict[str, Any]:
    return read_json_object_or_empty(_artifact_path(root, value))


def _metadata(
    *,
    root: Path,
    gold_path: str | Path,
    scoring_path: str | Path,
    semantic_groups_path: str | Path,
    rejection_adjudication_path: str | Path,
    cq_manifest_path: str | Path,
    prediction_validation_path: str | Path,
    extraction_schema_path: str | Path,
    generated_artifacts: dict[str, str],
) -> dict[str, Any]:
    return {
        "boundary": "Retrospective FAA ATCSCC advisory extraction only; no live operational use.",
        "repo_root": project_relative_path(root, root),
        "gold_path": project_relative_path(_artifact_path(root, gold_path), root),
        "scoring_path": project_relative_path(_artifact_path(root, scoring_path), root),
        "semantic_groups_path": project_relative_path(_artifact_path(root, semantic_groups_path), root),
        "rejection_adjudication_path": project_relative_path(
            _artifact_path(root, rejection_adjudication_path),
            root,
        ),
        "cq_manifest_path": project_relative_path(_artifact_path(root, cq_manifest_path), root),
        "prediction_validation_path": project_relative_path(
            _artifact_path(root, prediction_validation_path),
            root,
        ),
        "extraction_schema_path": project_relative_path(_artifact_path(root, extraction_schema_path), root),
        "generated_artifacts": generated_artifacts,
    }


def _artifact_inventory(root: Path, artifacts: dict[str, str | Path]) -> list[dict[str, Any]]:
    inventory = []
    for name, value in artifacts.items():
        path = _artifact_path(root, value)
        inventory.append(
            {
                "name": name,
                "path": project_relative_path(path, root),
                "exists": path.exists(),
            }
        )
    return inventory


def _counter_dict(counter: Counter[str]) -> dict[str, int]:
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def _cq_manifest_summary(cq_manifest: dict[str, Any]) -> dict[str, Any]:
    cqs = [cq for cq in cq_manifest.get("cqs", []) if isinstance(cq, dict)]
    route_counts = Counter(str(cq.get("route_label") or "unspecified") for cq in cqs)
    difficulty_counts = Counter(str(cq.get("difficulty_label") or "unspecified") for cq in cqs)
    graph_decisions = Counter(str(cq.get("graph_use_decision") or "unspecified") for cq in cqs)
    predicates: Counter[str] = Counter()
    for cq in cqs:
        for predicate in cq.get("required_predicates", []):
            predicates[normalize_atmonto_predicate(predicate)] += 1
    return {
        "status": cq_manifest.get("status"),
        "cq_count": len(cqs),
        "route_counts": _counter_dict(route_counts),
        "difficulty_counts": _counter_dict(difficulty_counts),
        "graph_use_decisions": _counter_dict(graph_decisions),
        "required_predicate_counts": _counter_dict(predicates),
        "cqs": [_cq_summary(cq) for cq in cqs],
    }


def _cq_summary(cq: dict[str, Any]) -> dict[str, Any]:
    return {
        "cq_id": cq.get("cq_id"),
        "role": cq.get("role"),
        "route_label": cq.get("route_label"),
        "difficulty_label": cq.get("difficulty_label"),
        "graph_use_decision": cq.get("graph_use_decision"),
        "required_predicates": [
            normalize_atmonto_predicate(predicate) for predicate in cq.get("required_predicates", [])
        ],
        "primary_metrics": cq.get("primary_metrics", []),
        "failure_modes": cq.get("failure_modes", []),
    }


def _schema_summary(schema: dict[str, Any]) -> dict[str, Any]:
    properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
    facts = properties.get("facts") if isinstance(properties.get("facts"), dict) else {}
    facts_schema = facts.get("items") if isinstance(facts.get("items"), dict) else {}
    fact_properties = (
        facts_schema.get("properties") if isinstance(facts_schema.get("properties"), dict) else {}
    )
    return {
        "title": schema.get("title"),
        "required_top_level_fields": schema.get("required", []),
        "required_fact_fields": facts_schema.get("required", []),
        "fact_fields": sorted(str(field) for field in fact_properties),
    }


def _prediction_validation_summary(prediction_validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": prediction_validation.get("status"),
        "selected_source_id_count": prediction_validation.get("selected_source_id_count"),
        "error_count": prediction_validation.get("error_count"),
        "pending_count": prediction_validation.get("pending_count"),
    }


def _agent_artifacts(result: dict[str, Any]) -> list[dict[str, Any]]:
    metadata = result["metadata"]
    cq_summary = result["cq_manifest_summary"]
    return [
        {
            "artifact": "SourceBrief",
            "path": metadata["generated_artifacts"]["source_brief_markdown"],
            "status": "generated",
            "purpose": "Source-family boundary, evidence scope, and non-operational-use limits.",
        },
        {
            "artifact": "SRD",
            "path": metadata["generated_artifacts"]["srd_markdown"],
            "status": "generated",
            "purpose": "Semantic requirements contract from CQs, gold fields, predicates, and evidence rules.",
        },
        {
            "artifact": "TIP",
            "path": metadata["generated_artifacts"]["tip_markdown"],
            "status": "generated",
            "purpose": "Implementation plan for deterministic, LLM, validation, repair, and review stages.",
        },
        {
            "artifact": "ExtractionValidationPlan",
            "path": metadata["generated_artifacts"]["plan_markdown"],
            "status": "generated",
            "purpose": "Runnable loop policy with anomaly-to-review routing.",
        },
        {
            "artifact": "ExtractionPlan",
            "path": metadata["generated_artifacts"]["extraction_plan_markdown"],
            "status": "generated",
            "purpose": "Field-level extractor, evidence, and abstention rules for the ATCSCC profile.",
        },
        {
            "artifact": "ValidationFindings",
            "path": metadata["generated_artifacts"]["validation_findings_markdown"],
            "status": "generated",
            "purpose": "Current schema, scoring, and anomaly findings before another extraction pass.",
        },
        {
            "artifact": "EvidenceSupportFindings",
            "path": metadata["generated_artifacts"]["evidence_support_findings_markdown"],
            "status": "generated",
            "purpose": "Evidence-support boundary for accepted, quarantined, and profile-gap facts.",
        },
        {
            "artifact": "RepairPlan",
            "path": metadata["generated_artifacts"]["repair_plan_markdown"],
            "status": "generated",
            "purpose": "Bounded repair and code-review routing plan for abnormal outputs.",
        },
        {
            "artifact": "CQManifest",
            "path": metadata["cq_manifest_path"],
            "status": "ready" if cq_summary["cq_count"] else "missing_or_empty",
            "purpose": "Executable CQs and route labels for ATCSCC/ATMONTO extraction.",
        },
        {
            "artifact": "PredictionValidation",
            "path": metadata["prediction_validation_path"],
            "status": result["prediction_validation_summary"]["status"] or "missing",
            "purpose": "Saved S0-S4 prediction readiness before scoring and repair decisions.",
        },
    ]


def _build_srd_seed(
    cq_evaluation: dict[str, Any],
    cq_manifest: dict[str, Any],
    extraction_schema: dict[str, Any],
) -> dict[str, Any]:
    gold = cq_evaluation["gold_summary"]
    cq_summary = _cq_manifest_summary(cq_manifest)
    return {
        "subject_classes": gold["candidate_subject_class_counts"],
        "required_predicates": cq_summary["required_predicate_counts"],
        "evidence_contract": {
            "required": True,
            "current_unit": "evidence_text",
            "known_gap": "stable character offsets are not yet a first-class artifact",
        },
        "schema_contract": _schema_summary(extraction_schema),
        "competency_question_count": cq_summary["cq_count"],
        "route_counts": cq_summary["route_counts"],
    }


def _build_tip_seed(
    cq_evaluation: dict[str, Any],
    diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    gold = cq_evaluation["gold_summary"]
    return {
        "accepted_baselines": [
            item["system_id"]
            for item in diagnostics
            if item.get("recommended_action") == "accept_for_current_baseline"
        ],
        "systems_requiring_review": [
            item["system_id"]
            for item in diagnostics
            if item.get("recommended_action") == "review_code_before_rerun"
        ],
        "profile_gap_signals": gold.get("rejected_predicate_counts", {}),
        "implementation_layers": [
            "deterministic backbone for advisory IDs and normalized times",
            "schema-slice constrained LLM for semantic enrichment",
            "validator/repair loop with evidence support as an acceptance criterion",
            "critic layer for unsupported facts, overclaims, and source-boundary violations",
            "GraphRAG/query layer only after source-bounded graph materialization is scored",
        ],
    }


def _next_actions(code_review_triggers: list[dict[str, Any]]) -> list[str]:
    actions = [
        "Use the generated SRD and TIP as the contract before another live LLM run.",
        "Materialize template graph queries for CQ-Q01 before making GraphRAG answer-quality claims.",
        "Add explicit absent-field labels for CQ-A01 if abstention becomes a primary claim.",
    ]
    if code_review_triggers:
        actions.insert(
            0,
            "Review code paths listed in code_review_triggers before rerunning S2/S3 extraction.",
        )
    return actions
