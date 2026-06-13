from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aviation_agentic_ai.llm.providers import configured_llm_model, configured_llm_provider
from aviation_agentic_ai.ontology.atmonto_experiment import (
    FORMAL_INPUT_RECORDS_PATH,
    GOLD_REVIEWED_PATH,
    SCHEMA_SLICE_PATH,
    build_default_llm_invoker,
    utc_timestamp,
    write_json,
    write_jsonl,
)
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.io import read_json_object_or_empty, write_json_report
from aviation_agentic_ai.reporting.atmonto.agentic_loop.contract import (
    DEFAULT_CQ_MANIFEST_PATH,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.independent_run_agents import (
    facts_from_records,
    metric_delta,
    predicate_route_map,
    quarantine_summary,
    read_jsonl_objects,
    routing_summary,
    scored_semantic_metrics,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.live_pilot_agents import (
    PROMPT_VERSION,
    AgentInvoker,
    agent_roles,
    quality_counters,
    run_live_agentic_record,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.live_pilot_render import (
    write_nasa_atmonto_s5_s6_live_agentic_pilot_markdown,
)

DEFAULT_REPORT_NAME = "nasa_atmonto_s5_s6_live_agentic_pilot"
DEFAULT_PREDICTION_OUTPUT_PATH = Path(
    "data/experiments/nasa_atmonto/formal/s5_s6_live_agentic_pilot_predictions.jsonl"
)
DEFAULT_RUN_METADATA_PATH = Path(
    "data/experiments/nasa_atmonto/formal/s5_s6_live_agentic_pilot_run_metadata.json"
)
FULL_RUN_REPORT_NAME = "nasa_atmonto_s5_s6_live_agentic_full_run"
FULL_RUN_PREDICTION_OUTPUT_PATH = Path(
    "data/experiments/nasa_atmonto/formal/s5_s6_live_agentic_full_run_predictions.jsonl"
)
FULL_RUN_METADATA_PATH = Path(
    "data/experiments/nasa_atmonto/formal/s5_s6_live_agentic_full_run_metadata.json"
)


@dataclass(frozen=True)
class LiveAgenticPilotArtifacts:
    report: dict[str, Any]
    prediction_records: list[dict[str, Any]]
    run_metadata: dict[str, Any]


def write_nasa_atmonto_s5_s6_live_agentic_pilot(
    *,
    output_dir: str | Path,
    report_name: str = DEFAULT_REPORT_NAME,
    repo_root: str | Path = PROJECT_ROOT,
    input_records_path: str | Path = FORMAL_INPUT_RECORDS_PATH,
    schema_slice_path: str | Path = SCHEMA_SLICE_PATH,
    gold_path: str | Path = GOLD_REVIEWED_PATH,
    cq_manifest_path: str | Path = DEFAULT_CQ_MANIFEST_PATH,
    prediction_output_path: str | Path = DEFAULT_PREDICTION_OUTPUT_PATH,
    run_metadata_output_path: str | Path = DEFAULT_RUN_METADATA_PATH,
    limit: int = 5,
    temperature: float = 0.0,
    max_tokens: int = 1400,
    run_scope: str = "pilot",
    invoker: AgentInvoker | None = None,
    invoker_label: str | None = None,
    progress: bool = False,
) -> tuple[Path, Path, dict[str, Any]]:
    if run_scope not in {"pilot", "full_run"}:
        raise ValueError("run_scope must be 'pilot' or 'full_run'")
    artifacts = _build_artifacts(
        repo_root=repo_root,
        input_records_path=input_records_path,
        schema_slice_path=schema_slice_path,
        gold_path=gold_path,
        cq_manifest_path=cq_manifest_path,
        prediction_output_path=prediction_output_path,
        run_metadata_output_path=run_metadata_output_path,
        limit=limit,
        temperature=temperature,
        max_tokens=max_tokens,
        run_scope=run_scope,
        invoker=invoker,
        invoker_label=invoker_label,
        progress=progress,
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
    md_path = write_nasa_atmonto_s5_s6_live_agentic_pilot_markdown(
        artifacts.report,
        output / f"{report_name}.md",
    )
    return json_path, md_path, artifacts.report


def _build_artifacts(
    *,
    repo_root: str | Path,
    input_records_path: str | Path,
    schema_slice_path: str | Path,
    gold_path: str | Path,
    cq_manifest_path: str | Path,
    prediction_output_path: str | Path,
    run_metadata_output_path: str | Path,
    limit: int,
    temperature: float,
    max_tokens: int,
    run_scope: str,
    invoker: AgentInvoker | None,
    invoker_label: str | None,
    progress: bool,
) -> LiveAgenticPilotArtifacts:
    if limit < 1:
        raise ValueError("limit must be >= 1")
    root = Path(repo_root)
    records = read_jsonl_objects(_resolve(root, input_records_path))[:limit]
    schema_slice = read_json_object_or_empty(_resolve(root, schema_slice_path))
    gold_records = read_jsonl_objects(_resolve(root, gold_path))
    cq_manifest = read_json_object_or_empty(_resolve(root, cq_manifest_path))
    route_map = predicate_route_map(cq_manifest)
    effective_invoker = invoker or build_default_llm_invoker(
        temperature=temperature,
        max_tokens=max_tokens,
    )
    label = invoker_label or ("live_llm" if invoker is None else "custom_invoker")
    started_at = utc_timestamp()
    prediction_records = []
    for index, record in enumerate(records, start=1):
        try:
            prediction_records.append(
                run_live_agentic_record(
                    record=record,
                    schema_slice=schema_slice,
                    route_map=route_map,
                    invoker=effective_invoker,
                    progress=progress,
                    index=index,
                    total=len(records),
                )
            )
        except Exception as exc:
            prediction_records.append(
                _failed_prediction_record(
                    record=record,
                    run_scope=run_scope,
                    exception=exc,
                )
            )
    completed_at = utc_timestamp()
    selected_source_ids = {str(record["source_id"]) for record in records}
    scoped_gold_records = [
        record for record in gold_records if str(record.get("source_id")) in selected_source_ids
    ]
    s5_facts = facts_from_records(prediction_records, "s5_facts")
    s6_facts = facts_from_records(prediction_records, "facts")
    quarantine = [
        item
        for record in prediction_records
        for item in record.get("critic_quarantine", [])
        if isinstance(item, dict)
    ]
    report = _build_report(
        root=root,
        input_records_path=input_records_path,
        schema_slice_path=schema_slice_path,
        gold_path=gold_path,
        cq_manifest_path=cq_manifest_path,
        prediction_output_path=prediction_output_path,
        run_metadata_output_path=run_metadata_output_path,
        prediction_records=prediction_records,
        scoped_gold_records=scoped_gold_records,
        s5_facts=s5_facts,
        s6_facts=s6_facts,
        quarantine=quarantine,
        limit=limit,
        temperature=temperature,
        max_tokens=max_tokens,
        run_scope=run_scope,
        label=label,
        started_at=started_at,
        completed_at=completed_at,
    )
    return LiveAgenticPilotArtifacts(
        report=report,
        prediction_records=prediction_records,
        run_metadata=_run_metadata(report, records, prediction_records, s5_facts, s6_facts, quarantine),
    )


def _build_report(
    *,
    root: Path,
    input_records_path: str | Path,
    schema_slice_path: str | Path,
    gold_path: str | Path,
    cq_manifest_path: str | Path,
    prediction_output_path: str | Path,
    run_metadata_output_path: str | Path,
    prediction_records: list[dict[str, Any]],
    scoped_gold_records: list[dict[str, Any]],
    s5_facts: list[dict[str, Any]],
    s6_facts: list[dict[str, Any]],
    quarantine: list[dict[str, Any]],
    limit: int,
    temperature: float,
    max_tokens: int,
    run_scope: str,
    label: str,
    started_at: str,
    completed_at: str,
) -> dict[str, Any]:
    scope_config = _scope_config(run_scope=run_scope, record_count=len(prediction_records))
    report = {
        "source_family": scope_config["source_family"],
        "status": scope_config["status"],
        "display_name": scope_config["display_name"],
        "claim_boundary": scope_config["claim_boundary"],
        "metadata": _metadata(
            root=root,
            input_records_path=input_records_path,
            schema_slice_path=schema_slice_path,
            gold_path=gold_path,
            cq_manifest_path=cq_manifest_path,
            prediction_output_path=prediction_output_path,
            run_metadata_output_path=run_metadata_output_path,
            record_count=len(prediction_records),
            limit=limit,
            temperature=temperature,
            max_tokens=max_tokens,
            run_scope=run_scope,
            label=label,
            s5_fact_count=len(s5_facts),
            s6_fact_count=len(s6_facts),
            quarantined_fact_count=len(quarantine),
            scored_gold_record_count=len(scoped_gold_records),
            started_at=started_at,
            completed_at=completed_at,
        ),
        "agent_roles": agent_roles(),
        "metrics": {
            "s5_validator_accepted_semantic_metrics": scored_semantic_metrics(
                predictions=s5_facts,
                gold_records=scoped_gold_records,
            ),
            "s6_live_refined_semantic_metrics": scored_semantic_metrics(
                predictions=s6_facts,
                gold_records=scoped_gold_records,
            ),
        },
        "quality_counters": quality_counters(prediction_records),
        "quarantine_summary": quarantine_summary(quarantine),
        "routing_summary": routing_summary(prediction_records),
        "sota_interpretation": _sota_interpretation(run_scope),
    }
    report["metrics"]["delta_s6_minus_s5"] = metric_delta(
        report["metrics"]["s6_live_refined_semantic_metrics"],
        report["metrics"]["s5_validator_accepted_semantic_metrics"],
    )
    return report


def _metadata(
    *,
    root: Path,
    input_records_path: str | Path,
    schema_slice_path: str | Path,
    gold_path: str | Path,
    cq_manifest_path: str | Path,
    prediction_output_path: str | Path,
    run_metadata_output_path: str | Path,
    record_count: int,
    limit: int,
    temperature: float,
    max_tokens: int,
    run_scope: str,
    label: str,
    s5_fact_count: int,
    s6_fact_count: int,
    quarantined_fact_count: int,
    scored_gold_record_count: int,
    started_at: str,
    completed_at: str,
) -> dict[str, Any]:
    return {
        "input_records": project_relative_path(_resolve(root, input_records_path), root),
        "schema_slice_path": project_relative_path(_resolve(root, schema_slice_path), root),
        "gold_path": project_relative_path(_resolve(root, gold_path), root),
        "cq_manifest_path": project_relative_path(_resolve(root, cq_manifest_path), root),
        "prediction_output": project_relative_path(_resolve(root, prediction_output_path), root),
        "run_metadata_output": project_relative_path(_resolve(root, run_metadata_output_path), root),
        "record_count": record_count,
        "limit": limit,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "run_scope": run_scope,
        "prompt_version": PROMPT_VERSION,
        "invoker_label": label,
        "provider": configured_llm_provider() if label == "live_llm" else label,
        "model": configured_llm_model() if label == "live_llm" else label,
        "independent_from_s4": True,
        "live_llm_run": label == "live_llm",
        "s5_fact_count": s5_fact_count,
        "s6_fact_count": s6_fact_count,
        "quarantined_fact_count": quarantined_fact_count,
        "scored_gold_record_count": scored_gold_record_count,
        "started_at": started_at,
        "completed_at": completed_at,
    }


def _run_metadata(
    report: dict[str, Any],
    input_records: list[dict[str, Any]],
    prediction_records: list[dict[str, Any]],
    s5_facts: list[dict[str, Any]],
    s6_facts: list[dict[str, Any]],
    quarantine: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "system_id": report["source_family"],
        "run_status": "completed",
        "runner": report["source_family"],
        "requires_llm": True,
        "live_llm_run": report["metadata"]["live_llm_run"],
        "provider": report["metadata"]["provider"],
        "model": report["metadata"]["model"],
        "input_record_count": len(input_records),
        "prediction_record_count": len(prediction_records),
        "prediction_output": report["metadata"]["prediction_output"],
        "s5_fact_count": len(s5_facts),
        "s6_fact_count": len(s6_facts),
        "quarantined_fact_count": len(quarantine),
        "quality_counters": report["quality_counters"],
        "claim_boundary": report["claim_boundary"],
    }


def _failed_prediction_record(
    *,
    record: dict[str, Any],
    run_scope: str,
    exception: Exception,
) -> dict[str, Any]:
    return {
        "system_id": (
            "S5_S6_live_agentic_full_run"
            if run_scope == "full_run"
            else "S5_S6_live_agentic_pilot"
        ),
        "run_status": "failed",
        "sample_id": record.get("sample_id"),
        "source_id": str(record["source_id"]),
        "source_family": record.get("source_family", "atcscc_advisories"),
        "json_adherence": False,
        "schema_valid": False,
        "candidate_fact_count": 0,
        "validator_accepted_fact_count": 0,
        "validator_rejected_fact_count": 0,
        "critic_quarantined_fact_count": 0,
        "accepted_fact_count": 0,
        "facts": [],
        "s5_facts": [],
        "validator_results": [],
        "critic_results": [],
        "live_critic_payload": {
            "raw_response": "",
            "payload": {},
            "parse_error": "record_failed_before_or_during_critic",
            "drop_fact_ids": [],
        },
        "critic_quarantine": [],
        "refiner_results": {
            "raw_response": "",
            "json_adherence": False,
            "parse_error": "record_failed_before_or_during_refiner",
            "contract_failed": False,
            "fallback_used": False,
        },
        "failure": {
            "exception_type": type(exception).__name__,
            "message": str(exception),
        },
        "agent_call_counts": {
            "extractor": 0,
            "validator": 0,
            "critic": 0,
            "refiner": 0,
        },
    }


def _scope_config(*, run_scope: str, record_count: int) -> dict[str, str]:
    if run_scope == "full_run":
        return {
            "source_family": "nasa_atmonto_s5_s6_live_agentic_full_run",
            "status": "s5_s6_live_agentic_full_run_scored",
            "display_name": "NASA ATMONTO S5/S6 Live Agentic Full Run",
            "claim_boundary": (
                f"This is a live multi-agent LLM run over {record_count} reviewed ATCSCC "
                "samples. It exercises extractor, deterministic validator, live critic, "
                "and live refiner roles under hard ontology/evidence gates. It supports "
                "method-level evaluation of event-centric semantic KG extraction, but it "
                "must not be cited as operational decision support."
            ),
        }
    return {
        "source_family": "nasa_atmonto_s5_s6_live_agentic_pilot",
        "status": "s5_s6_live_agentic_pilot_scored",
        "display_name": "NASA ATMONTO S5/S6 Live Agentic Pilot",
        "claim_boundary": (
            "This is a bounded live multi-agent LLM pilot over reviewed ATCSCC samples. "
            "It exercises extractor, deterministic validator, live critic, and live refiner "
            "roles under hard ontology/evidence gates. It is not a full 100-record formal run "
            "and must not be cited as operational decision support."
        ),
    }


def _sota_interpretation(run_scope: str) -> dict[str, str]:
    if run_scope == "full_run":
        return {
            "what_is_satisfied": (
                "The project has a live LLM multi-agent S5/S6 run over the full reviewed "
                "ATCSCC input set, using the same ATMONTO profile, evidence gates, and "
                "semantic scoring layer as the deterministic controls."
            ),
            "remaining_gap": (
                "A full SOTA claim still requires cost/latency accounting, answer-layer "
                "human review, and ideally transfer to a second event-centric domain."
            ),
            "claim_use": (
                "Use this artifact as full-set live-agent evidence for the extraction "
                "method. Do not present it as operational readiness or as proof of "
                "general-domain transfer."
            ),
        }
    return {
        "what_is_satisfied": (
            "The project now has a bounded live LLM multi-agent S5/S6 pilot that "
            "uses the same ATMONTO profile, evidence gates, and scoring layer as "
            "the deterministic run."
        ),
        "remaining_gap": (
            "The live pilot is intentionally small. A full SOTA claim would require "
            "a full 100-record live run, cost/latency accounting, and human review of "
            "the answer layer."
        ),
        "claim_use": (
            "Use this artifact as live-pilot evidence for the method design, not as "
            "proof that autonomous agents outperform the deterministic extractor."
        ),
    }


def _resolve(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate
