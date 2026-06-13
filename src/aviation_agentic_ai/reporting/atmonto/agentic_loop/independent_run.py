from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aviation_agentic_ai.ontology.atmonto_experiment import (
    FORMAL_INPUT_RECORDS_PATH,
    GOLD_REVIEWED_PATH,
    SCHEMA_SLICE_PATH,
    write_json,
    write_jsonl,
)
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report
from aviation_agentic_ai.reporting.atmonto.agentic_loop.independent_run_agents import (
    agent_roles,
    build_prediction_record,
    facts_from_records,
    metric_delta,
    predicate_route_map,
    quarantine_summary,
    read_jsonl_objects,
    routing_summary,
    scored_semantic_metrics,
    system_semantic_metrics,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.contract import (
    DEFAULT_CQ_MANIFEST_PATH,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.independent_run_render import (
    write_nasa_atmonto_s5_s6_independent_agentic_run_markdown,
)

DEFAULT_REPORT_NAME = "nasa_atmonto_s5_s6_independent_agentic_run"
DEFAULT_S0_PREDICTIONS_PATH = Path(
    "data/experiments/nasa_atmonto/formal/s0_rule_only_predictions.jsonl"
)
DEFAULT_SCORING_PATH = Path("reports/stages/nasa_atmonto_formal_experiment_scoring.json")
DEFAULT_PREDICTION_OUTPUT_PATH = Path(
    "data/experiments/nasa_atmonto/formal/s5_s6_independent_agentic_predictions.jsonl"
)
DEFAULT_RUN_METADATA_PATH = Path(
    "data/experiments/nasa_atmonto/formal/s5_s6_independent_agentic_run_metadata.json"
)

@dataclass(frozen=True)
class IndependentAgenticRunArtifacts:
    report: dict[str, Any]
    prediction_records: list[dict[str, Any]]
    run_metadata: dict[str, Any]


def build_nasa_atmonto_s5_s6_independent_agentic_run(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    input_records_path: str | Path = FORMAL_INPUT_RECORDS_PATH,
    s0_predictions_path: str | Path = DEFAULT_S0_PREDICTIONS_PATH,
    schema_slice_path: str | Path = SCHEMA_SLICE_PATH,
    gold_path: str | Path = GOLD_REVIEWED_PATH,
    cq_manifest_path: str | Path = DEFAULT_CQ_MANIFEST_PATH,
    scoring_path: str | Path = DEFAULT_SCORING_PATH,
    prediction_output_path: str | Path = DEFAULT_PREDICTION_OUTPUT_PATH,
    run_metadata_output_path: str | Path = DEFAULT_RUN_METADATA_PATH,
) -> dict[str, Any]:
    return _build_artifacts(
        repo_root=repo_root,
        input_records_path=input_records_path,
        s0_predictions_path=s0_predictions_path,
        schema_slice_path=schema_slice_path,
        gold_path=gold_path,
        cq_manifest_path=cq_manifest_path,
        scoring_path=scoring_path,
        prediction_output_path=prediction_output_path,
        run_metadata_output_path=run_metadata_output_path,
    ).report


def write_nasa_atmonto_s5_s6_independent_agentic_run(
    *,
    output_dir: str | Path,
    report_name: str = DEFAULT_REPORT_NAME,
    repo_root: str | Path = PROJECT_ROOT,
    input_records_path: str | Path = FORMAL_INPUT_RECORDS_PATH,
    s0_predictions_path: str | Path = DEFAULT_S0_PREDICTIONS_PATH,
    schema_slice_path: str | Path = SCHEMA_SLICE_PATH,
    gold_path: str | Path = GOLD_REVIEWED_PATH,
    cq_manifest_path: str | Path = DEFAULT_CQ_MANIFEST_PATH,
    scoring_path: str | Path = DEFAULT_SCORING_PATH,
    prediction_output_path: str | Path = DEFAULT_PREDICTION_OUTPUT_PATH,
    run_metadata_output_path: str | Path = DEFAULT_RUN_METADATA_PATH,
) -> tuple[Path, Path, dict[str, Any]]:
    artifacts = _build_artifacts(
        repo_root=repo_root,
        input_records_path=input_records_path,
        s0_predictions_path=s0_predictions_path,
        schema_slice_path=schema_slice_path,
        gold_path=gold_path,
        cq_manifest_path=cq_manifest_path,
        scoring_path=scoring_path,
        prediction_output_path=prediction_output_path,
        run_metadata_output_path=run_metadata_output_path,
    )
    root = Path(repo_root)
    write_jsonl(_resolve(root, prediction_output_path), artifacts.prediction_records)
    write_json(_resolve(root, run_metadata_output_path), artifacts.run_metadata)
    output = Path(output_dir)
    json_path = write_json_report(
        artifacts.report,
        output / f"{report_name}.json",
        sort_keys=False,
    )
    md_path = write_nasa_atmonto_s5_s6_independent_agentic_run_markdown(
        artifacts.report,
        output / f"{report_name}.md",
    )
    return json_path, md_path, artifacts.report


def _build_artifacts(
    *,
    repo_root: str | Path,
    input_records_path: str | Path,
    s0_predictions_path: str | Path,
    schema_slice_path: str | Path,
    gold_path: str | Path,
    cq_manifest_path: str | Path,
    scoring_path: str | Path,
    prediction_output_path: str | Path,
    run_metadata_output_path: str | Path,
) -> IndependentAgenticRunArtifacts:
    root = Path(repo_root)
    input_records = read_jsonl_objects(_resolve(root, input_records_path))
    s0_records = read_jsonl_objects(_resolve(root, s0_predictions_path))
    schema_slice = read_json_object_or_empty(_resolve(root, schema_slice_path))
    gold_records = read_jsonl_objects(_resolve(root, gold_path))
    cq_manifest = read_json_object_or_empty(_resolve(root, cq_manifest_path))
    scoring = read_json_object_or_empty(_resolve(root, scoring_path))
    route_map = predicate_route_map(cq_manifest)
    input_by_source_id = {str(record["source_id"]): record for record in input_records}
    prediction_records = [
        build_prediction_record(
            s0_record=record,
            input_record=input_by_source_id[str(record["source_id"])],
            schema_slice=schema_slice,
            route_map=route_map,
        )
        for record in s0_records
        if str(record.get("source_id")) in input_by_source_id
    ]
    s5_facts = facts_from_records(prediction_records, "s5_facts")
    s6_facts = facts_from_records(prediction_records, "facts")
    s0_metrics = system_semantic_metrics(scoring, "S0_rule_only")
    s5_metrics = scored_semantic_metrics(predictions=s5_facts, gold_records=gold_records)
    s6_metrics = scored_semantic_metrics(predictions=s6_facts, gold_records=gold_records)
    quarantine = [
        item
        for record in prediction_records
        for item in record.get("critic_quarantine", [])
        if isinstance(item, dict)
    ]
    report = {
        "source_family": "nasa_atmonto_s5_s6_independent_agentic_run",
        "status": "s5_s6_independent_agentic_run_scored",
        "claim_boundary": (
            "This is an independent, deterministic, artifact-driven S5/S6 run over "
            "source-derived S0 candidates. It is independent from S4 output and scored "
            "against reviewed gold, but it is not a live LLM multi-agent generation run."
        ),
        "metadata": {
            "input_records": project_relative_path(_resolve(root, input_records_path), root),
            "s0_predictions_path": project_relative_path(_resolve(root, s0_predictions_path), root),
            "schema_slice_path": project_relative_path(_resolve(root, schema_slice_path), root),
            "gold_path": project_relative_path(_resolve(root, gold_path), root),
            "cq_manifest_path": project_relative_path(_resolve(root, cq_manifest_path), root),
            "scoring_path": project_relative_path(_resolve(root, scoring_path), root),
            "prediction_output": project_relative_path(_resolve(root, prediction_output_path), root),
            "run_metadata_output": project_relative_path(_resolve(root, run_metadata_output_path), root),
            "record_count": len(prediction_records),
            "extractor_input_system_id": "S0_rule_only",
            "independent_from_s4": True,
            "live_llm_run": False,
            "s5_fact_count": len(s5_facts),
            "s6_fact_count": len(s6_facts),
            "quarantined_fact_count": len(quarantine),
        },
        "agent_roles": agent_roles(),
        "metrics": {
            "s0_reported_semantic_metrics": s0_metrics,
            "s5_validator_accepted_semantic_metrics": s5_metrics,
            "s6_critic_refined_semantic_metrics": s6_metrics,
            "delta_s6_minus_s5": metric_delta(s6_metrics, s5_metrics),
            "delta_s6_minus_s0_reported": metric_delta(s6_metrics, s0_metrics),
        },
        "quarantine_summary": quarantine_summary(quarantine),
        "routing_summary": routing_summary(prediction_records),
        "sota_interpretation": {
            "what_is_satisfied": (
                "The artifact contract now drives an independent scored S5/S6 pass "
                "that starts from source-derived S0 candidates rather than S4 output."
            ),
            "remaining_gap": (
                "A future upgrade should replace the deterministic extractor with live "
                "LLM extractor, validator, critic, and refiner agents under the same contract."
            ),
            "claim_use": (
                "Use this as evidence for an independent artifact-driven loop; do not "
                "cite it as a live autonomous LLM multi-agent extraction result."
            ),
        },
    }
    run_metadata = {
        "system_id": "S5_S6_independent_agentic_run",
        "run_status": "completed",
        "runner": "artifact_driven_extractor_validator_critic_refiner",
        "requires_llm": False,
        "source_systems": ["S0_rule_only"],
        "independent_from_s4": True,
        "input_record_count": len(input_records),
        "prediction_record_count": len(prediction_records),
        "prediction_output": report["metadata"]["prediction_output"],
        "schema_valid_record_count": sum(1 for record in prediction_records if record["schema_valid"]),
        "s5_fact_count": len(s5_facts),
        "s6_fact_count": len(s6_facts),
        "quarantined_fact_count": len(quarantine),
        "claim_boundary": report["claim_boundary"],
    }
    return IndependentAgenticRunArtifacts(report, prediction_records, run_metadata)


def _resolve(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate
