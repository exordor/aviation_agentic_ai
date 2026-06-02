from __future__ import annotations

from typing import Any


BASELINE_SYSTEM_IDS = {"S0_rule_only", "S4_hybrid_backbone_enrichment"}


def round_metric(value: object) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return None


def metric_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def recommended_action(system_id: str, flags: list[str]) -> str:
    if not flags:
        if system_id in BASELINE_SYSTEM_IDS:
            return "accept_for_current_baseline"
        return "monitor"
    if "invalid_target_schema_scoring" in flags or "schema_rejection_collapse" in flags:
        return "quarantine_before_rerun"
    if (
        "repair_did_not_improve_semantic_f1" in flags
        or "structural_repair_without_semantic_gain" in flags
        or "semantic_f1_below_minimum" in flags
    ):
        return "review_code_before_rerun"
    return "review_artifact_before_rerun"


def build_system_loop_diagnostics(
    scoring: dict[str, Any],
    prediction_validation: dict[str, Any],
) -> list[dict[str, Any]]:
    validation_by_system = {
        str(system.get("system_id", "")): system
        for system in prediction_validation.get("systems", [])
        if isinstance(system, dict)
    }
    diagnostics: list[dict[str, Any]] = []
    for system in scoring.get("systems", []):
        if not isinstance(system, dict):
            continue
        system_id = str(system.get("system_id") or "")
        semantic = system.get("semantic_metrics") if isinstance(system.get("semantic_metrics"), dict) else {}
        structural = (
            system.get("structural_metrics") if isinstance(system.get("structural_metrics"), dict) else {}
        )
        validation = validation_by_system.get(system_id, {})
        json_metrics = validation.get("json_metrics") if isinstance(validation.get("json_metrics"), dict) else {}
        f1 = round_metric(semantic.get("f1"))
        schema_violation = round_metric(structural.get("schema_violation_rate"))
        structural_acceptance = round_metric(structural.get("structural_acceptance_rate"))
        json_adherence = round_metric(json_metrics.get("json_adherence"))
        scoring_validity = semantic.get("scoring_validity")
        flags = _base_anomaly_flags(
            system_id=system_id,
            validation=validation,
            scoring_validity=scoring_validity,
            schema_violation=schema_violation,
            structural_acceptance=structural_acceptance,
            json_adherence=json_adherence,
            f1=f1,
        )
        diagnostics.append(
            {
                "system_id": system_id,
                "label": str(system.get("label") or system_id),
                "available": bool(system.get("available")),
                "precision": round_metric(semantic.get("precision")),
                "recall": round_metric(semantic.get("recall")),
                "f1": f1,
                "scoring_validity": scoring_validity,
                "schema_violation_rate": schema_violation,
                "structural_acceptance_rate": structural_acceptance,
                "repair_success_rate": round_metric(structural.get("repair_success_rate")),
                "json_adherence": json_adherence,
                "prediction_status": validation.get("status"),
                "anomaly_flags": flags,
            }
        )

    _add_repair_delta_flags(diagnostics)
    for item in diagnostics:
        item["recommended_action"] = recommended_action(
            str(item["system_id"]),
            list(item.get("anomaly_flags", [])),
        )
    return diagnostics


def _base_anomaly_flags(
    *,
    system_id: str,
    validation: dict[str, Any],
    scoring_validity: object,
    schema_violation: float | None,
    structural_acceptance: float | None,
    json_adherence: float | None,
    f1: float | None,
) -> list[str]:
    flags: list[str] = []
    if validation and validation.get("status") != "ready_for_scoring":
        flags.append("prediction_output_not_ready")
    if scoring_validity and scoring_validity != "valid_target_schema_scoring":
        flags.append("invalid_target_schema_scoring")
    if schema_violation is not None and schema_violation >= 0.9:
        flags.append("schema_rejection_collapse")
    if json_adherence is not None and json_adherence < 1.0:
        flags.append("json_adherence_gap")
    if structural_acceptance is not None and structural_acceptance < 0.6:
        flags.append("structural_acceptance_low")
    if f1 is not None and f1 < 0.3 and system_id not in BASELINE_SYSTEM_IDS:
        flags.append("semantic_f1_below_minimum")
    return flags


def _add_repair_delta_flags(diagnostics: list[dict[str, Any]]) -> None:
    by_id = {item["system_id"]: item for item in diagnostics}
    s2 = by_id.get("S2_llm_schema_slice")
    s3 = by_id.get("S3_llm_schema_slice_validator_repair")
    if not s2 or not s3:
        return
    s2_f1 = metric_float(s2.get("f1"))
    s3_f1 = metric_float(s3.get("f1"))
    s2_acceptance = metric_float(s2.get("structural_acceptance_rate"))
    s3_acceptance = metric_float(s3.get("structural_acceptance_rate"))
    if s3_acceptance <= s2_acceptance or s3_f1 > s2_f1:
        return
    for flag in ("repair_did_not_improve_semantic_f1", "structural_repair_without_semantic_gain"):
        if flag not in s3["anomaly_flags"]:
            s3["anomaly_flags"].append(flag)


def build_code_review_triggers(diagnostics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    triggers = []
    for item in diagnostics:
        flags = list(item.get("anomaly_flags", []))
        if item.get("recommended_action") != "review_code_before_rerun":
            continue
        triggers.append(
            {
                "system_id": item["system_id"],
                "label": item["label"],
                "flags": flags,
                "review_focus": review_focus_for_system(str(item["system_id"]), flags),
                "required_before": "next_live_or_saved_prediction_rerun",
            }
        )
    return triggers


def review_focus_for_system(system_id: str, flags: list[str]) -> list[str]:
    focus = []
    if system_id.startswith("S2"):
        focus.extend(
            [
                "schema-slice prompt contract",
                "predicate routing and enum canonicalization",
                "evidence-span preservation before validation",
            ]
        )
    if system_id.startswith("S3"):
        focus.extend(
            [
                "validator repair rules in atmonto_experiment.py",
                "repair acceptance criteria that may privilege structural validity over semantic support",
                "post-repair evidence support checks",
            ]
        )
    if "semantic_f1_below_minimum" in flags:
        focus.append("false-positive and false-negative examples by predicate")
    return focus or ["prediction generation and validation path"]
