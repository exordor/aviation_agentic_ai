"""AUTO-SPLIT from ontology/atmonto_experiment.py. See git history."""
from __future__ import annotations

from typing import Any
from pathlib import Path
import json

from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path

from ._io import (
    read_json,
    read_json_if_exists,
    read_jsonl,
)
from ._system_defs import (
    FORMAL_INPUT_RECORDS_PATH,
    FORMAL_SYSTEM_SPECS_PATH,
    GOLD_MANIFEST_PATH,
    GOLD_REVIEW_BATCH_INDEX_MD,
    GOLD_REVIEW_DECISION_INDEX_MD,
    GOLD_REVIEW_DECISION_PROGRESS_JSON,
    GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD,
    GOLD_REVIEW_PRIORITY_PACKET_JSON,
    GOLD_REVIEW_PROGRESS_JSON,
    GOLD_REVIEW_PROGRESS_MD,
    GOLD_REVIEW_SESSION_PLAN_JSON,
    GOLD_REVIEW_SESSION_PLAN_MD,
    GOLD_REVIEW_WORKLIST_MD,
    GOLD_REVIEW_WORKLOAD_PLAN_MD,
    GOLD_SEMANTIC_GROUPS_MD,
    GOLD_TEMPLATE_PATH,
    REJECTION_ANALYSIS_JSON,
    S0_CANDIDATES_PATH,
    S0_VALIDATED_PATH,
    SCHEMA_SLICE_PATH,
    SYSTEMS,
    system_definitions,
)
from ._metrics import (
    accepted_prediction_facts,
    gold_annotation_status,
    json_adherence_from_payloads,
    semantic_metrics,
    structural_metrics,
)
from ._rejection_adjudication import (
    build_rejection_adjudication_report,
)
from ._gold_review import (
    build_gold_review_session_plan,
    build_gold_semantic_groups,
)
from ._extraction import (
    DETERMINISTIC_BACKBONE_PREDICATES,
    selected_validations,
)
from ._scoring import (
    consensus_sota_remediation_constraints,
    formal_scoring_gold_source,
    macro_property_metric,
    metric_interval_text,
    metric_value_text,
    nested_metric,
    score_system_predictions,
    source_family_methodology_boundaries,
    system_score_by_id,
)

def status_record(
    *,
    item_id: str,
    label: str,
    status: str,
    rationale: str,
    evidence: list[str] | None = None,
    falsification_criterion: str | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "id": item_id,
        "label": label,
        "status": status,
        "rationale": rationale,
        "evidence": evidence or [],
    }
    if falsification_criterion:
        record["falsification_criterion"] = falsification_criterion
    return record

def claim_and_hypothesis_statuses(
    *,
    system_scores: list[dict[str, Any]],
    gold_source: dict[str, Any],
    rejection_analysis: dict[str, Any],
    rejection_adjudication: dict[str, Any],
) -> dict[str, Any]:
    by_id = system_score_by_id(system_scores)
    s0 = by_id["S0_rule_only"]
    s1 = by_id["S1_llm_only"]
    s1b = by_id.get("S1b_llm_canonicalized")
    s2 = by_id["S2_llm_schema_slice"]
    s3 = by_id["S3_llm_schema_slice_validator_repair"]
    s4 = by_id.get("S4_hybrid_backbone_enrichment")
    reviewed_gold_ready = bool(gold_source.get("ready_for_formal_scoring"))
    s1_s2_ready = bool(s1.get("available") and s2.get("available"))
    s1b_s2_ready = bool(s1b and s1b.get("available") and s2.get("available"))
    s2_s3_ready = bool(s2.get("available") and s3.get("available"))
    all_llm_ready = bool(s1.get("available") and s2.get("available") and s3.get("available"))
    s4_ready = bool(s4 and s4.get("available"))
    semantic_ready = reviewed_gold_ready and all(
        bool((score.get("semantic_metrics") or {}).get("available"))
        for score in system_scores
    )
    rejection_count = int(rejection_analysis.get("rejected_fact_count", 0))
    rejection_group_total = sum(int(group.get("count", 0)) for group in rejection_analysis.get("groups", []))
    final_rejection_decisions = rejection_adjudication.get("decision_counts_by_fact", {})
    adjudication_complete = bool(rejection_adjudication.get("property_level_complete"))
    manual_review_only = int(final_rejection_decisions.get("manual_review_only", 0))

    s1_violation = nested_metric(s1, "structural_metrics", "schema_violation_rate")
    s1b_violation = (
        nested_metric(s1b, "structural_metrics", "schema_violation_rate") if s1b else None
    )
    s2_violation = nested_metric(s2, "structural_metrics", "schema_violation_rate")
    h1_delta = (
        s1b_violation - s2_violation
        if isinstance(s1b_violation, (int, float)) and isinstance(s2_violation, (int, float))
        else s1_violation - s2_violation
        if isinstance(s1_violation, (int, float)) and isinstance(s2_violation, (int, float))
        else None
    )
    s2_accepted = nested_metric(s2, "structural_metrics", "accepted_fact_count")
    s3_accepted = nested_metric(s3, "structural_metrics", "accepted_fact_count")
    s3_repair_success = nested_metric(s3, "structural_metrics", "repair_success_rate")
    s2_semantic = nested_metric(s2, "semantic_metrics", "manual_semantic_correctness")
    s3_semantic = nested_metric(s3, "semantic_metrics", "manual_semantic_correctness")
    s1_precision = nested_metric(s1, "semantic_metrics", "precision")
    s3_precision = nested_metric(s3, "semantic_metrics", "precision")
    s1_f1 = nested_metric(s1, "semantic_metrics", "f1")
    s3_f1 = nested_metric(s3, "semantic_metrics", "f1")
    s1_scoring_validity = nested_metric(s1, "semantic_metrics", "scoring_validity")
    s1_invalid_direct = s1_scoring_validity == "invalid_direct_schema_scoring"
    h3_semantic_predicates = ("implementationStatus", "reRouteReason", "reRouteType")
    h3_deterministic_predicates = tuple(sorted(DETERMINISTIC_BACKBONE_PREDICATES))
    s0_h3_semantic_f1 = macro_property_metric(s0, h3_semantic_predicates, "f1")
    s4_h3_semantic_f1 = macro_property_metric(s4 or {}, h3_semantic_predicates, "f1")
    s0_deterministic_f1 = macro_property_metric(s0, h3_deterministic_predicates, "f1")
    s4_deterministic_f1 = macro_property_metric(s4 or {}, h3_deterministic_predicates, "f1")

    if s1b_s2_ready:
        h1_baseline_label = "S1b_llm_canonicalized"
        if h1_delta is None:
            h1_status = "inconclusive_missing_metric"
            h1_rationale = "S1b/S2 outputs exist, but schema violation rates are unavailable."
        elif h1_delta >= 0.10:
            h1_status = "supported"
            h1_rationale = (
                "S2 schema guidance reduces target-schema violation rate versus the "
                "canonicalized S1b baseline by at least 10 percentage points."
            )
        else:
            h1_status = "falsified"
            h1_rationale = (
                "S2 did not reduce schema violation rate versus the canonicalized S1b "
                "baseline by the required 10 percentage points."
            )
    elif not s1_s2_ready:
        h1_baseline_label = "S1_llm_only"
        h1_status = "pending_required_inputs"
        h1_rationale = "S1 and S2 prediction outputs are required before schema-violation comparison."
    elif h1_delta is None:
        h1_baseline_label = "S1_llm_only"
        h1_status = "inconclusive_missing_metric"
        h1_rationale = "S1/S2 outputs exist, but schema violation rates are unavailable."
    elif s1_invalid_direct:
        h1_baseline_label = "S1_llm_only"
        h1_status = "inconclusive"
        h1_rationale = (
            "S2 reduces direct target-schema violations versus S1, but S1 is a "
            "schema-free output scored without a canonicalization bridge. Treat this as "
            "structural-drift diagnosis until S1_raw_open_llm and S1b_llm_canonicalized exist."
        )
    elif h1_delta >= 0.10:
        h1_baseline_label = "S1_llm_only"
        h1_status = "supported_structural_only" if not reviewed_gold_ready else "supported"
        h1_rationale = (
            "S2 schema violation rate is at least 10 percentage points lower than S1; "
            "gold-supported fact suppression still needs reviewed gold if unavailable."
        )
    else:
        h1_baseline_label = "S1_llm_only"
        h1_status = "falsified"
        h1_rationale = "S2 did not reduce schema violation rate by the required 10 percentage points."

    if not s2_s3_ready:
        h2_status = "pending_required_inputs"
        h2_rationale = "S2 and S3 prediction outputs are required before repair comparison."
    elif not semantic_ready:
        h2_status = "pending_manual_gold"
        h2_rationale = "Structural repair can be inspected, but semantic preservation requires reviewed gold."
    elif (
        isinstance(s3_repair_success, (int, float))
        and isinstance(s2_semantic, (int, float))
        and isinstance(s3_semantic, (int, float))
        and s3_repair_success >= 0.15
        and (s2_semantic - s3_semantic) <= 0.05
    ):
        h2_status = "supported"
        h2_rationale = "S3 meets the repair-success threshold and preserves semantic correctness."
    else:
        h2_status = "falsified"
        h2_rationale = "S3 failed the repair-success or semantic-preservation criterion."

    if s4_ready and semantic_ready:
        if (
            isinstance(s0_h3_semantic_f1, (int, float))
            and isinstance(s4_h3_semantic_f1, (int, float))
            and isinstance(s0_deterministic_f1, (int, float))
            and isinstance(s4_deterministic_f1, (int, float))
            and s4_h3_semantic_f1 > s0_h3_semantic_f1 + 0.05
            and s4_deterministic_f1 >= s0_deterministic_f1 - 0.02
        ):
            h3_status = "supported"
            h3_rationale = (
                "S4 improves the selected semantic predicate macro-F1 over S0 while "
                "preserving deterministic-field macro-F1 within tolerance."
            )
        else:
            h3_status = "falsified"
            h3_rationale = (
                "S4 did not improve selected semantic predicate macro-F1 over S0 while "
                "preserving deterministic-field macro-F1 within tolerance."
            )
    elif not all_llm_ready:
        h3_status = "pending_required_inputs"
        h3_rationale = "S1-S3 prediction outputs are required before precision/recall/F1 comparison."
    elif not semantic_ready:
        h3_status = "pending_manual_gold"
        h3_rationale = "Precision, recall, F1, and manual semantic correctness require reviewed gold."
    elif s1_invalid_direct:
        h3_status = "inconclusive"
        h3_rationale = (
            "S1 direct target-schema semantic scores are invalid because all schema-free "
            "facts were rejected at the ATMONTO scoring interface. S3>S1 is therefore not "
            "valid evidence for ontology-constrained semantic improvement."
        )
    elif (
        isinstance(s1_precision, (int, float))
        and isinstance(s3_precision, (int, float))
        and isinstance(s1_f1, (int, float))
        and isinstance(s3_f1, (int, float))
        and s3_precision > s1_precision
        and s3_f1 >= s1_f1 - 0.05
    ):
        h3_status = "supported"
        h3_rationale = "S3 improves precision and keeps F1 within the allowed loss threshold."
    else:
        h3_status = "falsified"
        h3_rationale = "S3 did not satisfy the precision/F1 tradeoff criterion."

    if rejection_group_total != rejection_count:
        h4_status = "incomplete_rejection_accounting"
        h4_rationale = (
            "The rejection analysis does not account for all "
            f"{rejection_count} pilot rejections."
        )
    elif not adjudication_complete:
        h4_status = "pending_manual_adjudication"
        h4_rationale = "Property-level adjudication still has unresolved manual-review-only facts."
    elif manual_review_only / rejection_count > 0.20:
        h4_status = "falsified"
        h4_rationale = "More than 20 percent of rejected facts remain manual-review-only."
    else:
        h4_status = "supported"
        h4_rationale = (
            f"All {rejection_count} rejections have final property-level action labels: "
            f"{json.dumps(final_rejection_decisions, sort_keys=True)}."
        )

    claims = [
        status_record(
            item_id="C1",
            label="Runtime NASA ATMONTO profile feasibility",
            status="supported_by_pilot",
            rationale=(
                "The pilot generated the schema catalog, ATCSCC schema slice, and validated "
                "candidate-fact artifact. This remains a schema-engineering claim."
            ),
            evidence=[
                "data/ontology/curated/nasa_atmonto_schema_catalog.json",
                "data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json",
                "data/processed/nasa_atmonto/extraction/2026-05-14/atcscc_schema_slice_validated.jsonl",
            ],
        ),
        status_record(
            item_id="C2",
            label="Schema-slice constraint benefit",
            status=h1_status,
            rationale=h1_rationale,
            evidence=[
                f"{h1_baseline_label} structural metrics",
                "S2_llm_schema_slice structural metrics",
            ],
        ),
        status_record(
            item_id="C3",
            label="Validator/repair benefit",
            status=h2_status,
            rationale=h2_rationale,
            evidence=[
                "S2_llm_schema_slice structural and semantic metrics",
                "S3_llm_schema_slice_validator_repair structural and semantic metrics",
            ],
        ),
        status_record(
            item_id="C4",
            label="Rejection analysis utility",
            status=h4_status,
            rationale=h4_rationale,
            evidence=[
                "reports/stages/nasa_atmonto_rejection_error_analysis.md",
                "reports/stages/nasa_atmonto_rejection_adjudication.md",
            ],
        ),
    ]

    hypotheses = [
        status_record(
            item_id="H1",
            label="Schema guidance reduces structural drift",
            status=h1_status,
            rationale=h1_rationale,
            evidence=[
                f"s1_schema_violation_rate={s1_violation}",
                f"s1b_schema_violation_rate={s1b_violation}",
                f"s2_schema_violation_rate={s2_violation}",
                f"{h1_baseline_label}_minus_s2={h1_delta}",
                f"s1_semantic_scoring_validity={s1_scoring_validity}",
            ],
            falsification_criterion=(
                "Falsified if schema guidance does not reduce unsupported target-schema "
                "terms after a canonicalized S1b baseline exists, or if the reduction only "
                "comes from suppressing more than 25 percent of gold-supported facts."
            ),
        ),
        status_record(
            item_id="H2",
            label="Validator/repair improves valid yield",
            status=h2_status,
            rationale=h2_rationale,
            evidence=[
                f"s2_accepted_fact_count={s2_accepted}",
                f"s3_accepted_fact_count={s3_accepted}",
                f"s3_repair_success_rate={s3_repair_success}",
                f"s2_manual_semantic_correctness={s2_semantic}",
                f"s3_manual_semantic_correctness={s3_semantic}",
            ],
            falsification_criterion=(
                "Falsified if S3 repair success is below 15 percent of initially invalid "
                "facts, or if S3 manual semantic correctness is more than 5 percentage "
                "points lower than S2."
            ),
        ),
        status_record(
            item_id="H3",
            label="Hybrid backbone plus enrichment improves selected semantic predicates",
            status=h3_status,
            rationale=h3_rationale,
            evidence=[
                f"s1_precision={s1_precision}",
                f"s3_precision={s3_precision}",
                f"s1_f1={s1_f1}",
                f"s3_f1={s3_f1}",
                f"s1_semantic_scoring_validity={s1_scoring_validity}",
                f"s0_selected_semantic_macro_f1={s0_h3_semantic_f1}",
                f"s4_selected_semantic_macro_f1={s4_h3_semantic_f1}",
                f"s0_deterministic_macro_f1={s0_deterministic_f1}",
                f"s4_deterministic_macro_f1={s4_deterministic_f1}",
            ],
            falsification_criterion=(
                "Falsified if S4 hybrid does not improve selected semantic "
                "predicate F1 over S0 while preserving deterministic-field F1 within the "
                "pre-registered tolerance."
            ),
        ),
        status_record(
            item_id="H4",
            label="Rejection triage produces actionable engineering decisions",
            status=h4_status,
            rationale=h4_rationale,
            evidence=[
                f"rejected_fact_count={rejection_count}",
                "final_decision_counts_by_fact="
                f"{json.dumps(final_rejection_decisions, sort_keys=True)}",
            ],
            falsification_criterion=(
                "Falsified if more than 20 percent of rejected facts remain manual-review-only "
                "after review, or if profile extensions cannot be tied to source evidence and "
                "NASA ATMONTO terms."
            ),
        ),
    ]
    return {"claims": claims, "hypotheses": hypotheses}

def formal_completion_audit(
    *,
    manifest: dict[str, Any],
    protocol_text: str,
    gold_source: dict[str, Any],
    system_scores: list[dict[str, Any]],
    rejection_analysis: dict[str, Any],
    rejection_adjudication: dict[str, Any],
    claim_statuses: list[dict[str, Any]],
    hypothesis_statuses: list[dict[str, Any]],
) -> dict[str, Any]:
    sample_size = int(manifest.get("sample_size", 0))
    sample_ok = 80 <= sample_size <= 120
    systems_by_id = system_score_by_id(system_scores)
    all_system_outputs = all(score.get("output_exists") for score in system_scores)
    all_semantic = all(
        bool((score.get("semantic_metrics") or {}).get("available"))
        for score in system_scores
    )
    all_scores = all_system_outputs and all_semantic
    rejection_count = int(rejection_analysis.get("rejected_fact_count", 0))
    rejection_group_total = sum(int(group.get("count", 0)) for group in rejection_analysis.get("groups", []))
    final_rejection_decisions = rejection_adjudication.get("decision_counts_by_fact", {})
    adjudication_complete = bool(rejection_adjudication.get("property_level_complete"))
    terminal_statuses = {"supported", "supported_by_pilot", "falsified", "inconclusive"}
    final_claims = all(
        status["status"] in terminal_statuses
        for status in [*claim_statuses, *hypothesis_statuses]
    )
    pilot_positioning = all(
        marker in protocol_text
        for marker in [
            "Prior stage: pilot / feasibility study",
            "## Current Pilot Positioning",
            "bronze_until_reviewed",
            "structural validation is not semantic correctness",
        ]
    )
    protocol_fixed = all(
        marker in protocol_text
        for marker in [
            "## Research Claims",
            "## Hypotheses And Falsification Criteria",
            "## Baselines And Comparators",
            "## Metrics",
            "Falsified if",
            "JSON Adherence",
            "Manual Semantic Correctness",
        ]
    )

    requirements = [
        {
            "id": "R0",
            "requirement": "Position the current NASA ATMONTO loop as pilot / feasibility evidence, not a completed formal experiment.",
            "status": "satisfied" if pilot_positioning else "incomplete_claim_boundary",
            "evidence": "EXPERIMENTS.md contains pilot/feasibility boundary and bronze-until-reviewed language.",
        },
        {
            "id": "R1",
            "requirement": "Sample 80-120 ATCSCC advisories for the formal gold set.",
            "status": "satisfied" if sample_ok else "incomplete",
            "evidence": f"sample_size={sample_size}; manifest=data/evaluation/nasa_atmonto/atcscc_gold_sample_manifest.json",
        },
        {
            "id": "R2",
            "requirement": "Freeze reviewed gold annotations before semantic scoring.",
            "status": (
                "satisfied"
                if gold_source.get("ready_for_formal_scoring")
                else "pending_manual_input"
            ),
            "evidence": (
                f"gold_source={gold_source.get('source')}; "
                f"template_reviewed={gold_source.get('template_reviewed_record_count')}; "
                f"template_pending={gold_source.get('template_pending_record_count')}"
            ),
        },
        {
            "id": "R3",
            "requirement": (
                "Define the corrected system suite: S0, diagnostic S1, S1b, S2, S3, "
                "and S4."
            ),
            "status": (
                "satisfied"
                if set(systems_by_id) == {
                    "S0_rule_only",
                    "S1_llm_only",
                    "S1b_llm_canonicalized",
                    "S2_llm_schema_slice",
                    "S3_llm_schema_slice_validator_repair",
                    "S4_hybrid_backbone_enrichment",
                }
                else "incomplete"
            ),
            "evidence": f"systems={','.join(sorted(systems_by_id))}",
        },
        {
            "id": "R4",
            "requirement": "Run all corrected-stage systems on the identical sampled records.",
            "status": "satisfied" if all_system_outputs else "pending_model_output",
            "evidence": json.dumps(
                {
                    score["system_id"]: bool(score.get("output_exists"))
                    for score in system_scores
                },
                sort_keys=True,
            ),
        },
        {
            "id": "R5",
            "requirement": "Define JSON, schema, semantic, repair, and manual-correctness metrics.",
            "status": "satisfied",
            "evidence": "EXPERIMENTS.md and reports/stages/nasa_atmonto_formal_experiment_scoring.json",
        },
        {
            "id": "R6",
            "requirement": "Report JSON adherence, schema violation rate, precision/recall/F1, repair success, and manual semantic correctness.",
            "status": "satisfied" if all_scores else "pending_scoring",
            "evidence": f"all_system_outputs={all_system_outputs}; all_semantic_metrics_available={all_semantic}",
        },
        {
            "id": "R7",
            "requirement": (
                "Account for all pilot rejections in property-level error analysis."
            ),
            "status": (
                "satisfied"
                if rejection_group_total == rejection_count
                else "incomplete_rejection_accounting"
            ),
            "evidence": f"rejected_fact_count={rejection_count}; grouped_fact_count={rejection_group_total}",
        },
        {
            "id": "R8",
            "requirement": "Finalize whether each rejection group is extractor bug, NASA ATMONTO profile gap, source ambiguity, or manual-review-only.",
            "status": "satisfied" if adjudication_complete else "pending_manual_adjudication",
            "evidence": json.dumps(final_rejection_decisions, sort_keys=True),
        },
        {
            "id": "R9",
            "requirement": "Assign supported, falsified, or inconclusive status to claims C1-C4 and hypotheses H1-H4.",
            "status": "satisfied" if final_claims else "pending_scoring",
            "evidence": json.dumps(
                {
                    status["id"]: status["status"]
                    for status in [*claim_statuses, *hypothesis_statuses]
                },
                sort_keys=True,
            ),
        },
        {
            "id": "R10",
            "requirement": "Fix the protocol artifact with claims, hypotheses, baselines, metrics, and falsification criteria.",
            "status": "satisfied" if protocol_fixed else "incomplete_protocol",
            "evidence": "EXPERIMENTS.md",
        },
    ]
    blockers = [
        requirement["id"]
        for requirement in requirements
        if requirement["status"] != "satisfied"
    ]
    return {
        "overall_status": (
            "formal_experiment_complete" if not blockers else "formal_experiment_pending"
        ),
        "blocking_requirement_ids": blockers,
        "requirements": requirements,
        "claim_boundary": (
            "A satisfied audit means the formal experiment can be reported; pending items "
            "must remain described as pilot/prepared-state evidence."
        ),
    }

def build_formal_experiment_score_report(
    repo_root: str | Path = PROJECT_ROOT,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    input_records = read_jsonl(repo_root / FORMAL_INPUT_RECORDS_PATH)
    schema_slice = read_json(repo_root / SCHEMA_SLICE_PATH)
    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    gold_source = formal_scoring_gold_source(repo_root, selected_ids)
    gold_records = gold_source["records"]
    gold_status = gold_source["gold_status"]
    semantic_groups = build_gold_semantic_groups(repo_root)
    system_scores = [
        score_system_predictions(
            system=system,
            repo_root=repo_root,
            selected_ids=selected_ids,
            input_records=input_records,
            gold_records=gold_records,
            schema_slice=schema_slice,
            semantic_groups=semantic_groups,
        )
        for system in SYSTEMS
    ]
    rejection_analysis = read_json(repo_root / REJECTION_ANALYSIS_JSON)
    rejection_adjudication = build_rejection_adjudication_report(
        repo_root,
        rejection_analysis=rejection_analysis,
    )
    claim_hypothesis_status = claim_and_hypothesis_statuses(
        system_scores=system_scores,
        gold_source=gold_source,
        rejection_analysis=rejection_analysis,
        rejection_adjudication=rejection_adjudication,
    )
    protocol_text = (repo_root / "EXPERIMENTS.md").read_text(encoding="utf-8")
    completion_audit = formal_completion_audit(
        manifest=manifest,
        protocol_text=protocol_text,
        gold_source=gold_source,
        system_scores=system_scores,
        rejection_analysis=rejection_analysis,
        rejection_adjudication=rejection_adjudication,
        claim_statuses=claim_hypothesis_status["claims"],
        hypothesis_statuses=claim_hypothesis_status["hypotheses"],
    )
    missing_inputs: list[str] = []
    if not gold_source["ready_for_formal_scoring"]:
        missing_inputs.append(
            f"frozen reviewed gold set at {gold_source['path']}"
        )
    if gold_source["template_validation_status"] != "ready_for_scoring":
        missing_inputs.append("completed manual gold annotations for 100 sampled advisories")
    for score in system_scores:
        if not score["output_exists"]:
            missing_inputs.append(f"{score['system_id']} predictions at {score['expected_output']}")
    if any(score["semantic_metrics"] and not score["semantic_metrics"]["available"] for score in system_scores):
        missing_inputs.append("manual semantic metrics require reviewed gold facts")

    return {
        "source_family": "nasa_atmonto_formal_experiment_scoring",
        "status": "scored" if not missing_inputs else "pending_required_inputs",
        "protocol": "EXPERIMENTS.md",
        "gold_source": {
            key: value
            for key, value in gold_source.items()
            if key != "records"
        },
        "gold_status": gold_status,
        "semantic_groups": {
            key: value
            for key, value in semantic_groups.items()
            if key != "records"
        },
        "methodology_remediation": source_family_methodology_boundaries(repo_root),
        "consensus_sota_remediation": consensus_sota_remediation_constraints(),
        "systems": system_scores,
        "rejection_adjudication": {
            key: value
            for key, value in rejection_adjudication.items()
            if key != "groups"
        },
        "claim_statuses": claim_hypothesis_status["claims"],
        "hypothesis_statuses": claim_hypothesis_status["hypotheses"],
        "completion_audit": completion_audit,
        "missing_required_inputs": missing_inputs,
        "metrics_reported": [
            "json_adherence",
            "structural_acceptance_rate",
            "schema_violation_rate",
            "triple_precision",
            "triple_recall",
            "triple_f1",
            "semantic_group_triple_precision_recall_f1",
            "repair_success_rate",
            "manual_semantic_correctness",
        ],
        "claim_boundary": (
            "Formal metrics are descriptive until all four systems have predictions and "
            "the frozen reviewed gold set is available."
        ),
    }

def score_report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Formal Experiment Scoring",
        "",
        f"- Status: `{report['status']}`",
        f"- Protocol: `{report['protocol']}`",
        "",
        "## Gold Source",
        "",
        f"- Source: `{report['gold_source']['source']}`",
        f"- Path: `{report['gold_source']['path']}`",
        f"- Exists: `{report['gold_source']['exists']}`",
        f"- Ready for scoring: `{report['gold_source']['ready_for_formal_scoring']}`",
        f"- SHA-256: `{report['gold_source']['sha256']}`",
        "",
        "## Gold Status",
        "",
    ]
    gold = report["gold_status"]
    lines.extend(
        [
            f"- Records: {gold['record_count']}",
            f"- Reviewed records: {gold['reviewed_record_count']}",
            f"- Pending records: {gold['pending_record_count']}",
            f"- Complete: `{gold['complete']}`",
            "",
            "## Methodology Remediation",
            "",
            f"- Status: `{report['methodology_remediation']['status']}`",
            f"- Scope: {report['methodology_remediation']['scope_statement']}",
            f"- Cross-source metric policy: {report['methodology_remediation']['cross_source_metric_policy']}",
            "",
            "| Source family | Data shape | Task | Boundary |",
            "| --- | --- | --- | --- |",
        ]
    )
    for family in report["methodology_remediation"]["source_families"]:
        boundary = (
            "Current scored ATCSCC event extraction."
            if family["id"] == "A"
            else "Next-rerun PDF reference extraction; do not mix definition/procedure F1 with ATCSCC event F1."
        )
        lines.append(
            "| "
            f"`{family['source_family']}` | "
            f"`{family['data_shape']}` | "
            f"{family['task']} | "
            f"{boundary} |"
        )
    pdf_family = next(
        family
        for family in report["methodology_remediation"]["source_families"]
        if family["id"] == "B"
    )
    lines.extend(
        [
            "",
            "- PDF backend policy: `hybrid_docling_pymupdf` is the candidate default; "
            "`pymupdf_text_legacy` is a baseline only.",
            "- PDF target predicates: "
            f"`{', '.join(pdf_family['allowed_predicates'])}`.",
            "- PDF provenance fields: "
            f"`{', '.join(pdf_family['required_provenance_fields'])}`.",
            "",
            "## Consensus SOTA Constraints",
            "",
        ]
    )
    sota = report["consensus_sota_remediation"]
    lines.extend(
        [
            f"- Status: `{sota['status']}`",
            f"- Boundary: {sota['scope_boundary']}",
            "- S1 interpretation: "
            "`S1_raw_open_llm` is a drift diagnostic; "
            "`S1b_llm_canonicalized` is the comparable target-schema baseline.",
            "- Nine-stage pipeline: "
            f"`{' -> '.join(sota['nine_stage_pipeline'])}`.",
            "- Reviewed dev examples artifact: `reviewed_dev_examples`; use 10-20 "
            "examples outside the held-out 100 scoring records.",
            "",
            "| SOTA constraint | Implementation | Claim guardrail |",
            "| --- | --- | --- |",
        ]
    )
    for constraint in sota["sota_adaptations"]:
        lines.append(
            "| "
            f"`{constraint['anchor']}` | "
            f"{constraint['implementation']} | "
            f"{constraint['claim_guardrail']} |"
        )
    s4_policy = sota["s4_merge_policy"]
    artifact_names = [
        artifact.get("path") or artifact.get("component")
        for artifact in sota["planned_artifacts"]
    ]
    lines.extend(
        [
            "",
            "- S4 primary candidate: "
            f"`{s4_policy['primary_candidate_system']}`.",
            "- S0 owns deterministic fields: "
            f"`{', '.join(s4_policy['s0_owns'])}`.",
            "- S3/S4 may add but not overwrite semantic fields: "
            f"`{', '.join(s4_policy['s3_s4_may_add_not_overwrite'])}`.",
            "- Quarantine/review conditions: "
            f"`{', '.join(s4_policy['quarantine_conditions'])}`.",
            "- Planned artifacts/TODO: "
            f"`{', '.join(name for name in artifact_names if name)}`.",
            "- Unverified search leads remain `requiring verification`: "
            f"`{', '.join(sota['unverified_search_leads']['items'])}`.",
            "- GraphRAG boundary: report `KG construction`, `graph retrieval`, and "
            "`answer faithfulness/completeness/citation support` separately; current "
            "remediation makes no end-to-end GraphRAG answer improvement claim.",
            "",
            "## Corrected Stage Results",
            "",
        ]
    )
    score_by_id = {str(score["system_id"]): score for score in report["systems"]}
    s0_score = score_by_id.get("S0_rule_only", {})
    s1b_score = score_by_id.get("S1b_llm_canonicalized", {})
    s4_score = score_by_id.get("S4_hybrid_backbone_enrichment", {})
    if s1b_score:
        s1b_structural = s1b_score.get("structural_metrics") or {}
        s1b_semantic = s1b_score.get("semantic_metrics") or {}
        lines.append(
            "- `S1b_llm_canonicalized`: "
            f"accepted {s1b_structural.get('accepted_fact_count')} / "
            f"{s1b_structural.get('candidate_fact_count')} mapped facts; "
            f"target-schema F1={s1b_semantic.get('f1')}."
        )
    if s4_score:
        s4_semantic_macro = macro_property_metric(
            s4_score,
            ("implementationStatus", "reRouteReason", "reRouteType"),
            "f1",
        )
        s0_semantic_macro = macro_property_metric(
            s0_score,
            ("implementationStatus", "reRouteReason", "reRouteType"),
            "f1",
        )
        s4_deterministic_macro = macro_property_metric(
            s4_score,
            sorted(DETERMINISTIC_BACKBONE_PREDICATES),
            "f1",
        )
        s0_deterministic_macro = macro_property_metric(
            s0_score,
            sorted(DETERMINISTIC_BACKBONE_PREDICATES),
            "f1",
        )
        lines.append(
            "- `S4_hybrid_backbone_enrichment`: selected semantic macro-F1 "
            f"{s0_semantic_macro} -> {s4_semantic_macro}; deterministic macro-F1 "
            f"{s0_deterministic_macro} -> {s4_deterministic_macro}."
        )
    lines.extend(
        [
            "",
            "## System Metrics",
            "",
            "| System | Output | JSON adherence | Candidate facts | Accepted | Rejected | Structural acceptance | Schema violation rate | Repair success | Semantic metrics |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for score in report["systems"]:
        json_metrics = score.get("json_metrics") or {}
        structural = score.get("structural_metrics") or {}
        semantic = score.get("semantic_metrics") or {}
        semantic_text = (
            (
                "`invalid_direct_schema_scoring`; "
                f"diagnostic P={semantic.get('precision')}, R={semantic.get('recall')}, "
                f"F1={semantic.get('f1')}"
            )
            if semantic.get("scoring_validity") == "invalid_direct_schema_scoring"
            else f"P={semantic.get('precision')}, R={semantic.get('recall')}, F1={semantic.get('f1')}"
            if semantic.get("available")
            else f"pending:{semantic.get('reason') or score.get('reason')}"
        )
        lines.append(
            "| "
            f"`{score['system_id']}` | "
            f"`{score['output_exists']}` | "
            f"{metric_value_text(json_metrics.get('json_adherence'))} | "
            f"{metric_value_text(structural.get('candidate_fact_count'))} | "
            f"{metric_value_text(structural.get('accepted_fact_count'))} | "
            f"{metric_value_text(structural.get('rejected_fact_count'))} | "
            f"{metric_value_text(structural.get('structural_acceptance_rate'))} | "
            f"{metric_value_text(structural.get('schema_violation_rate'))} | "
            f"{metric_value_text(structural.get('repair_success_rate'))} | "
            f"{semantic_text} |"
        )
    ci_rows = [
        (score["system_id"], (score.get("semantic_metrics") or {}).get("confidence_intervals"))
        for score in report["systems"]
        if ((score.get("semantic_metrics") or {}).get("confidence_intervals") or {}).get("available")
        and (score.get("semantic_metrics") or {}).get("scoring_validity")
        != "invalid_direct_schema_scoring"
    ]
    if ci_rows:
        lines.extend(
            [
                "",
                "## Semantic Confidence Intervals",
                "",
                "| System | Method | Precision 95% CI | Recall 95% CI | F1 95% CI |",
                "| --- | --- | ---: | ---: | ---: |",
            ]
        )
        for system_id, intervals in ci_rows:
            values = intervals["intervals"]
            lines.append(
                "| "
                f"`{system_id}` | "
                f"`{intervals['method']}` ({intervals['iterations']} iter, seed={intervals['seed']}) | "
                f"{metric_interval_text(values['precision'])} | "
                f"{metric_interval_text(values['recall'])} | "
                f"{metric_interval_text(values['f1'])} |"
            )
    group_rows = [
        (score["system_id"], row)
        for score in report["systems"]
        for row in score.get("semantic_group_metrics", [])
        if (row.get("semantic_metrics") or {}).get("available")
        and (score.get("semantic_metrics") or {}).get("scoring_validity")
        != "invalid_direct_schema_scoring"
    ]
    if group_rows:
        lines.extend(
            [
                "",
                "## Semantic Group Metrics",
                "",
                "- Semantic groups are stratified reporting slices, not train/dev/test splits.",
                "",
                "| System | Group | Records | Gold facts | Predicted facts | Precision | Recall | F1 |",
                "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for system_id, row in group_rows:
            metrics = row["semantic_metrics"]
            lines.append(
                "| "
                f"`{system_id}` | "
                f"`{row['group_id']}` | "
                f"{row['record_count']} | "
                f"{row['gold_fact_count']} | "
                f"{row['predicted_fact_count']} | "
                f"{metric_value_text(metrics.get('precision'))} | "
                f"{metric_value_text(metrics.get('recall'))} | "
                f"{metric_value_text(metrics.get('f1'))} |"
            )
    adjudication = report["rejection_adjudication"]
    lines.extend(
        [
            "",
            "## Rejection Adjudication",
            "",
            f"- Property-level complete: `{adjudication['property_level_complete']}`",
            f"- Decision counts: `{json.dumps(adjudication['decision_counts_by_fact'], sort_keys=True)}`",
            f"- Pending facts: {adjudication['pending_fact_count']}",
        ]
    )
    lines.extend(
        [
            "",
            "## Claim Status",
            "",
            "| Claim | Status | Rationale |",
            "| --- | --- | --- |",
        ]
    )
    for claim in report["claim_statuses"]:
        lines.append(
            f"| `{claim['id']}` {claim['label']} | `{claim['status']}` | {claim['rationale']} |"
        )
    lines.extend(
        [
            "",
            "## Hypothesis Status",
            "",
            "| Hypothesis | Status | Falsification criterion |",
            "| --- | --- | --- |",
        ]
    )
    for hypothesis in report["hypothesis_statuses"]:
        lines.append(
            "| "
            f"`{hypothesis['id']}` {hypothesis['label']} | "
            f"`{hypothesis['status']}` | "
            f"{hypothesis.get('falsification_criterion', '')} |"
        )
    audit = report["completion_audit"]
    lines.extend(
        [
            "",
            "## Completion Audit",
            "",
            f"- Overall status: `{audit['overall_status']}`",
            f"- Blocking requirements: `{json.dumps(audit['blocking_requirement_ids'])}`",
            "",
            "| Requirement | Status | Evidence |",
            "| --- | --- | --- |",
        ]
    )
    for requirement in audit["requirements"]:
        lines.append(
            "| "
            f"`{requirement['id']}` {requirement['requirement']} | "
            f"`{requirement['status']}` | "
            f"{requirement['evidence']} |"
        )
    lines.extend(["", "## Missing Required Inputs", ""])
    for item in report["missing_required_inputs"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Boundary", "", f"- {report['claim_boundary']}"])
    return "\n".join(lines) + "\n"

def build_formal_experiment_readiness(
    repo_root: str | Path = PROJECT_ROOT,
    *,
    session_plan: dict[str, Any] | None = None,
    decision_progress: dict[str, Any] | None = None,
    review_progress: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = Path(repo_root).resolve()
    manifest = read_json(repo_root / GOLD_MANIFEST_PATH)
    gold_records = read_jsonl(repo_root / GOLD_TEMPLATE_PATH)
    s0_payloads = read_jsonl(repo_root / S0_CANDIDATES_PATH)
    s0_validations_all = read_jsonl(repo_root / S0_VALIDATED_PATH)

    selected_ids = set(str(source_id) for source_id in manifest["selected_source_ids"])
    s0_validations = selected_validations(s0_validations_all, selected_ids)
    s0_predictions = accepted_prediction_facts(s0_validations)
    gold_status = gold_annotation_status(gold_records)

    formal_input_status = {
        "input_records": project_relative_path(repo_root / FORMAL_INPUT_RECORDS_PATH, repo_root),
        "input_records_exists": (repo_root / FORMAL_INPUT_RECORDS_PATH).exists(),
        "system_specs": project_relative_path(repo_root / FORMAL_SYSTEM_SPECS_PATH, repo_root),
        "system_specs_exists": (repo_root / FORMAL_SYSTEM_SPECS_PATH).exists(),
    }

    system_output_status: list[dict[str, Any]] = []
    for system in SYSTEMS:
        output_path = repo_root / system.expected_output
        prompt_path = repo_root / system.prompt_batch if system.prompt_batch else None
        system_output_status.append(
            {
                "system_id": system.system_id,
                "expected_output": project_relative_path(output_path, repo_root),
                "exists": output_path.exists(),
                "prompt_batch": (
                    project_relative_path(prompt_path, repo_root) if prompt_path else None
                ),
                "prompt_batch_exists": prompt_path.exists() if prompt_path else None,
                "required_before_formal_scoring": system.system_id != "S0_rule_only",
            }
        )

    s0_structural = structural_metrics(s0_validations, repair_applicable=False)
    s0_json = json_adherence_from_payloads(s0_payloads, selected_ids)
    s0_semantic = semantic_metrics(predictions=s0_predictions, gold_records=gold_records)

    missing_inputs = []
    if not formal_input_status["input_records_exists"]:
        missing_inputs.append("formal input records for the 100 sampled advisories")
    if not formal_input_status["system_specs_exists"]:
        missing_inputs.append("formal system specs for S0-S3")
    if not gold_status["complete"]:
        missing_inputs.append("completed manual gold annotations for 100 sampled advisories")
    for item in system_output_status:
        if item["prompt_batch"] and not item["prompt_batch_exists"]:
            missing_inputs.append(f"{item['system_id']} prompt batch at {item['prompt_batch']}")
        if item["required_before_formal_scoring"] and not item["exists"]:
            missing_inputs.append(f"{item['system_id']} predictions at {item['expected_output']}")

    if not missing_inputs:
        status = "ready_for_scoring"
    elif missing_inputs == ["completed manual gold annotations for 100 sampled advisories"]:
        status = "ready_for_manual_gold_review"
    else:
        status = "ready_for_manual_gold_and_llm_runs"
    session_plan = session_plan or build_gold_review_session_plan(repo_root)
    review_kickoff = build_manual_gold_review_kickoff(
        repo_root,
        gold_status=gold_status,
        session_plan=session_plan,
        decision_progress=decision_progress,
        review_progress=review_progress,
    )

    return {
        "source_family": "nasa_atmonto_formal_experiment_readiness",
        "status": status,
        "protocol": "EXPERIMENTS.md",
        "gold_manifest": project_relative_path(repo_root / GOLD_MANIFEST_PATH, repo_root),
        "gold_template": project_relative_path(repo_root / GOLD_TEMPLATE_PATH, repo_root),
        "manual_review_artifacts": {
            "worklist": project_relative_path(repo_root / GOLD_REVIEW_WORKLIST_MD, repo_root),
            "workload_plan": project_relative_path(
                repo_root / GOLD_REVIEW_WORKLOAD_PLAN_MD,
                repo_root,
            ),
            "semantic_groups": project_relative_path(
                repo_root / GOLD_SEMANTIC_GROUPS_MD,
                repo_root,
            ),
            "session_plan": project_relative_path(
                repo_root / GOLD_REVIEW_SESSION_PLAN_MD,
                repo_root,
            ),
            "priority_packets": project_relative_path(
                repo_root / GOLD_REVIEW_PRIORITY_PACKET_INDEX_MD,
                repo_root,
            ),
            "batch_index": project_relative_path(repo_root / GOLD_REVIEW_BATCH_INDEX_MD, repo_root),
            "decision_templates": project_relative_path(
                repo_root / GOLD_REVIEW_DECISION_INDEX_MD,
                repo_root,
            ),
            "progress": project_relative_path(repo_root / GOLD_REVIEW_PROGRESS_MD, repo_root),
        },
        "manual_gold_review_kickoff": review_kickoff,
        "gold_status": gold_status,
        "formal_input_status": formal_input_status,
        "systems": system_definitions(repo_root),
        "system_output_status": system_output_status,
        "current_s0_rule_only_structural_metrics": {
            **s0_json,
            **s0_structural,
            "semantic_metrics": s0_semantic,
        },
        "metrics_defined": [
            "json_adherence",
            "structural_acceptance_rate",
            "schema_violation_rate",
            "triple_precision",
            "triple_recall",
            "triple_f1",
            "repair_success_rate",
            "manual_semantic_correctness",
        ],
        "missing_required_inputs": missing_inputs,
        "claim_boundary": (
            "This readiness report does not claim formal extraction effectiveness until "
            "manual gold annotations are complete and all required system outputs are present."
        ),
    }

def build_manual_gold_review_kickoff(
    repo_root: Path,
    *,
    gold_status: dict[str, Any],
    session_plan: dict[str, Any] | None = None,
    decision_progress: dict[str, Any] | None = None,
    review_progress: dict[str, Any] | None = None,
) -> dict[str, Any]:
    priority_packets = read_json_if_exists(repo_root / GOLD_REVIEW_PRIORITY_PACKET_JSON)
    decision_progress = decision_progress or read_json_if_exists(
        repo_root / GOLD_REVIEW_DECISION_PROGRESS_JSON
    )
    review_progress = review_progress or read_json_if_exists(repo_root / GOLD_REVIEW_PROGRESS_JSON)
    session_plan = session_plan or read_json_if_exists(repo_root / GOLD_REVIEW_SESSION_PLAN_JSON)
    lanes = priority_packets.get("lanes", [])
    first_lane = lanes[0] if lanes else {}
    first_record = (first_lane.get("records") or [{}])[0]
    complete = bool(gold_status.get("complete"))
    next_session = (
        None
        if complete
        else session_plan.get("next_session") or (session_plan.get("sessions") or [{}])[0]
    )
    return {
        "status": "complete" if complete else "ready_for_manual_gold_review",
        "reviewed_record_count": gold_status.get("reviewed_record_count", 0),
        "pending_record_count": gold_status.get("pending_record_count", 0),
        "decision_progress_status": decision_progress.get("status"),
        "ready_to_apply_record_count": decision_progress.get("ready_to_apply_record_count"),
        "not_started_record_count": decision_progress.get("not_started_record_count"),
        "completed_rejected_fact_decision_count": decision_progress.get(
            "completed_rejected_fact_decision_count"
        ),
        "rejected_fact_decision_count": decision_progress.get("rejected_fact_decision_count"),
        "complete_batch_count": review_progress.get("complete_batch_count"),
        "batch_count": review_progress.get("batch_count"),
        "first_priority_lane": {
            "lane_id": first_lane.get("lane_id"),
            "label": first_lane.get("label"),
            "record_count": first_lane.get("record_count"),
            "estimated_review_minutes": first_lane.get("estimated_review_minutes"),
            "packet_markdown": first_lane.get("path"),
            "first_sample_id": first_record.get("sample_id"),
            "first_source_id": first_record.get("source_id"),
            "first_batch_id": first_record.get("batch_id"),
            "first_decision_template": first_record.get("decision_template"),
            "first_batch_markdown": first_record.get("batch_markdown"),
        },
        "next_review_session": None
        if complete
        else {
            "session_id": next_session.get("session_id"),
            "status": next_session.get("status"),
            "record_count": next_session.get("record_count"),
            "ready_to_apply_record_count": next_session.get("ready_to_apply_record_count"),
            "remaining_record_count": next_session.get("remaining_record_count"),
            "estimated_review_minutes": next_session.get("estimated_review_minutes"),
            "pending_rejected_fact_decision_count": next_session.get(
                "pending_rejected_fact_decision_count"
            ),
            "first_sample_id": (next_session.get("records") or [{}])[0].get("sample_id"),
            "first_source_id": (next_session.get("records") or [{}])[0].get("source_id"),
            "session_plan_markdown": session_plan.get("session_plan_markdown"),
        },
        "next_commands": [
            "uv run python scripts/prepare_nasa_atmonto_gold_review_decision_progress.py",
            "uv run python scripts/apply_nasa_atmonto_gold_review_decisions.py",
            "uv run python scripts/validate_nasa_atmonto_gold_annotations.py",
            "uv run python scripts/freeze_nasa_atmonto_gold_set.py",
            "uv run python scripts/run_nasa_atmonto_formal_experiment.py --skip-prepare-inputs",
        ],
        "review_boundary": (
            "Priority packets and suggested_* fields are work aids only. A record becomes "
            "gold only after source review, completed review_checklist, confirmed decisions, "
            "validation, and frozen reviewed output."
        ),
    }

def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# NASA ATMONTO Formal Experiment Readiness",
        "",
        f"- Status: `{report['status']}`",
        f"- Protocol: `{report['protocol']}`",
        f"- Gold manifest: `{report['gold_manifest']}`",
        f"- Gold template: `{report['gold_template']}`",
        f"- Workload plan: `{report['manual_review_artifacts']['workload_plan']}`",
        f"- Semantic groups: `{report['manual_review_artifacts']['semantic_groups']}`",
        f"- Session plan: `{report['manual_review_artifacts']['session_plan']}`",
        f"- Priority packets: `{report['manual_review_artifacts']['priority_packets']}`",
        f"- Review progress: `{report['manual_review_artifacts']['progress']}`",
        "",
        "## Gold Status",
        "",
    ]
    gold = report["gold_status"]
    lines.extend(
        [
            f"- Records: {gold['record_count']}",
            f"- Reviewed records: {gold['reviewed_record_count']}",
            f"- Pending records: {gold['pending_record_count']}",
            f"- Complete: `{gold['complete']}`",
            f"- Status counts: `{json.dumps(gold['status_counts'], sort_keys=True)}`",
            "",
            "## Manual Gold Review Kickoff",
            "",
        ]
    )
    kickoff = report["manual_gold_review_kickoff"]
    first_lane = kickoff["first_priority_lane"]
    next_session = kickoff["next_review_session"]
    lines.extend(
        [
            f"- Status: `{kickoff['status']}`",
            f"- Reviewed / pending records: {kickoff['reviewed_record_count']} / {kickoff['pending_record_count']}",
            f"- Decision progress: `{kickoff['decision_progress_status']}`",
            f"- Ready to apply / not started: {kickoff['ready_to_apply_record_count']} / {kickoff['not_started_record_count']}",
            "- Rejected-fact decisions confirmed: "
            f"{kickoff['completed_rejected_fact_decision_count']} / "
            f"{kickoff['rejected_fact_decision_count']}",
            "- First priority lane: "
            f"`{first_lane['lane_id']}` ({first_lane['record_count']} records, "
            f"{first_lane['estimated_review_minutes']} est. min)",
            f"- Start packet: `{first_lane['packet_markdown']}`",
            "- First sample: "
            f"`{first_lane['first_sample_id']}` / `{first_lane['first_source_id']}` "
            f"via `{first_lane['first_decision_template']}`",
            f"- Boundary: {kickoff['review_boundary']}",
            "",
        ]
    )
    next_section = ["", "### Next Commands", ""]
    if next_session:
        next_section[:0] = [
            "- Next session sample: "
            f"`{next_session['first_sample_id']}` / `{next_session['first_source_id']}`",
            "- Next review session: "
            f"`{next_session['session_id']}` ({next_session['record_count']} records, "
            f"{next_session['estimated_review_minutes']} est. min, "
            f"status=`{next_session['status']}`) "
            f"from `{next_session['session_plan_markdown']}`",
        ]
    else:
        next_section[:0] = ["- Next review session: `none`; gold review is complete."]
    for command in kickoff["next_commands"]:
        next_section.append(f"- `{command}`")
    lines.extend(next_section)
    lines.extend(
        [
            "",
            "## Formal Inputs",
            "",
            f"- Input records: `{report['formal_input_status']['input_records']}`",
            f"- Input records exists: `{report['formal_input_status']['input_records_exists']}`",
            f"- System specs: `{report['formal_input_status']['system_specs']}`",
            f"- System specs exists: `{report['formal_input_status']['system_specs_exists']}`",
            "",
            "## Systems",
            "",
        ]
    )
    output_status = {item["system_id"]: item for item in report["system_output_status"]}
    for system in report["systems"]:
        status = output_status[system["system_id"]]
        lines.append(
            f"- `{system['system_id']}`: {system['label']} "
            f"(LLM={system['requires_llm']}, schema={system['uses_schema_slice']}, "
            f"repair={system['uses_validator_repair']}, "
            f"prompt_ready={status['prompt_batch_exists']}, output_ready={status['exists']})"
        )
    lines.extend(["", "## Current S0 Structural Metrics", ""])
    s0 = report["current_s0_rule_only_structural_metrics"]
    for key in (
        "attempted_record_count",
        "valid_json_payload_count",
        "json_adherence",
        "candidate_fact_count",
        "accepted_fact_count",
        "rejected_fact_count",
        "structural_acceptance_rate",
        "schema_violation_rate",
        "repair_applicable",
        "repair_attempted_fact_count",
        "repair_accepted_fact_count",
        "repair_success_rate",
    ):
        lines.append(f"- `{key}`: {metric_value_text(s0.get(key))}")
    lines.extend(["", "## Missing Required Inputs", ""])
    for item in report["missing_required_inputs"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            f"- {report['claim_boundary']}",
        ]
    )
    return "\n".join(lines) + "\n"
