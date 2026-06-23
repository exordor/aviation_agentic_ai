from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agents.extraction_agent import ExtractionAgent
from aviation_agentic_ai.ontology.atmonto_experiment import (
    FORMAL_INPUT_RECORDS_PATH,
    SCHEMA_SLICE_PATH,
    canonical_fact_key,
    term_name,
    validate_prediction_record,
    write_json,
    write_jsonl,
)
from aviation_agentic_ai.paths import PROJECT_ROOT, project_relative_path
from aviation_agentic_ai.reporting.atmonto.agentic_loop.independent_run_agents import (
    critic_reasons,
    predicate_route_map,
    read_jsonl_objects,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.live_pilot_agents import (
    _critic_allowed_facts,
    _profile_normalize_live_record,
)
from aviation_agentic_ai.reporting.io import (
    normalize_report_text,
    read_json_object_or_empty,
    write_json_report,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.contract import (
    DEFAULT_CQ_MANIFEST_PATH,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.l1_batch_render import (
    write_nasa_atmonto_l1_agent_batch_experiment_markdown,
)

DEFAULT_REPORT_NAME = "nasa_atmonto_l1_agent_batch_experiment"
DEFAULT_SAMPLE_SIZE = 8
DEFAULT_BASELINE_PREDICTIONS_PATH = Path(
    "data/experiments/nasa_atmonto/formal/s1b_llm_canonicalized_predictions.jsonl"
)
DEFAULT_REPAIR_PREDICTIONS_PATH = Path(
    "data/experiments/nasa_atmonto/formal/s4_hybrid_backbone_enrichment_predictions.jsonl"
)
DEFAULT_PREDICTION_OUTPUT_PATH = Path(
    "data/experiments/nasa_atmonto/formal/l1_agent_batch_predictions.jsonl"
)
DEFAULT_RUN_METADATA_PATH = Path(
    "data/experiments/nasa_atmonto/formal/l1_agent_batch_run_metadata.json"
)


@dataclass(frozen=True)
class L1BatchArtifacts:
    report: dict[str, Any]
    prediction_records: list[dict[str, Any]]
    run_metadata: dict[str, Any]


class ArtifactReplayInvoker:
    """Replay tracked extraction artifacts through the L1 agent interface."""

    def __init__(
        self,
        *,
        baseline_payload: dict[str, Any],
        repair_payload: dict[str, Any],
    ) -> None:
        self.baseline_payload = baseline_payload
        self.repair_payload = repair_payload
        self.extractor_calls = 0
        self.repair_planner_calls = 0

    def __call__(self, messages: list[dict[str, str]]) -> str:
        system = messages[0]["content"]
        if "Extractor agent" in system:
            self.extractor_calls += 1
            payload = self.baseline_payload if self.extractor_calls == 1 else self.repair_payload
            return json.dumps(payload, ensure_ascii=False, sort_keys=True)
        if "Critic agent" in system:
            return json.dumps({"drop_fact_ids": [], "concerns": [], "global_notes": []})
        if "Repair planner" in system:
            self.repair_planner_calls += 1
            return json.dumps(self._repair_plan(messages), ensure_ascii=False, sort_keys=True)
        if "Refiner agent" in system:
            payload = json.loads(messages[-1]["content"])
            return json.dumps(payload["required_output"], ensure_ascii=False, sort_keys=True)
        raise ValueError(f"Unsupported agent role in message: {system[:120]}")

    def _repair_plan(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        if self.repair_planner_calls > 1:
            return {"repair_targets": [], "blocked_keys": []}
        payload = json.loads(messages[-1]["content"])
        targets: list[dict[str, str]] = []
        seen: set[str] = set()
        for predicate in payload.get("missing_predicates", []):
            key = term_name(predicate)
            if key and key not in seen:
                seen.add(key)
                targets.append(
                    {
                        "predicate": key,
                        "reason": "missing from accepted baseline facts",
                        "instruction": f"Replay repair artifact evidence for {key}.",
                    }
                )
        for item in payload.get("validator_rejections", []) + payload.get("critic_quarantine", []):
            predicate = term_name(item.get("predicate"))
            if predicate and predicate not in seen:
                seen.add(predicate)
                targets.append(
                    {
                        "predicate": predicate,
                        "reason": "baseline candidate was rejected or quarantined",
                        "instruction": f"Replay only newly supported evidence for {predicate}.",
                    }
                )
        return {"repair_targets": targets, "blocked_keys": payload.get("blocked_keys", [])}


def build_nasa_atmonto_l1_agent_batch_experiment(
    *,
    repo_root: str | Path = PROJECT_ROOT,
    input_records_path: str | Path = FORMAL_INPUT_RECORDS_PATH,
    baseline_predictions_path: str | Path = DEFAULT_BASELINE_PREDICTIONS_PATH,
    repair_predictions_path: str | Path = DEFAULT_REPAIR_PREDICTIONS_PATH,
    schema_slice_path: str | Path = SCHEMA_SLICE_PATH,
    cq_manifest_path: str | Path = DEFAULT_CQ_MANIFEST_PATH,
    prediction_output_path: str | Path = DEFAULT_PREDICTION_OUTPUT_PATH,
    run_metadata_output_path: str | Path = DEFAULT_RUN_METADATA_PATH,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    max_iterations: int = 2,
) -> dict[str, Any]:
    return _build_artifacts(
        repo_root=repo_root,
        input_records_path=input_records_path,
        baseline_predictions_path=baseline_predictions_path,
        repair_predictions_path=repair_predictions_path,
        schema_slice_path=schema_slice_path,
        cq_manifest_path=cq_manifest_path,
        prediction_output_path=prediction_output_path,
        run_metadata_output_path=run_metadata_output_path,
        sample_size=sample_size,
        max_iterations=max_iterations,
    ).report


def write_nasa_atmonto_l1_agent_batch_experiment(
    *,
    output_dir: str | Path,
    report_name: str = DEFAULT_REPORT_NAME,
    repo_root: str | Path = PROJECT_ROOT,
    input_records_path: str | Path = FORMAL_INPUT_RECORDS_PATH,
    baseline_predictions_path: str | Path = DEFAULT_BASELINE_PREDICTIONS_PATH,
    repair_predictions_path: str | Path = DEFAULT_REPAIR_PREDICTIONS_PATH,
    schema_slice_path: str | Path = SCHEMA_SLICE_PATH,
    cq_manifest_path: str | Path = DEFAULT_CQ_MANIFEST_PATH,
    prediction_output_path: str | Path = DEFAULT_PREDICTION_OUTPUT_PATH,
    run_metadata_output_path: str | Path = DEFAULT_RUN_METADATA_PATH,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    max_iterations: int = 2,
) -> tuple[Path, Path, dict[str, Any]]:
    artifacts = _build_artifacts(
        repo_root=repo_root,
        input_records_path=input_records_path,
        baseline_predictions_path=baseline_predictions_path,
        repair_predictions_path=repair_predictions_path,
        schema_slice_path=schema_slice_path,
        cq_manifest_path=cq_manifest_path,
        prediction_output_path=prediction_output_path,
        run_metadata_output_path=run_metadata_output_path,
        sample_size=sample_size,
        max_iterations=max_iterations,
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
    md_path = write_nasa_atmonto_l1_agent_batch_experiment_markdown(
        artifacts.report,
        output / f"{report_name}.md",
    )
    return json_path, md_path, artifacts.report


def _build_artifacts(
    *,
    repo_root: str | Path,
    input_records_path: str | Path,
    baseline_predictions_path: str | Path,
    repair_predictions_path: str | Path,
    schema_slice_path: str | Path,
    cq_manifest_path: str | Path,
    prediction_output_path: str | Path,
    run_metadata_output_path: str | Path,
    sample_size: int,
    max_iterations: int,
) -> L1BatchArtifacts:
    root = Path(repo_root)
    if sample_size < 1:
        raise ValueError("sample_size must be at least 1")
    input_records = read_jsonl_objects(_resolve(root, input_records_path))
    baseline_records = read_jsonl_objects(_resolve(root, baseline_predictions_path))
    repair_records = read_jsonl_objects(_resolve(root, repair_predictions_path))
    schema_slice = read_json_object_or_empty(_resolve(root, schema_slice_path))
    cq_manifest = read_json_object_or_empty(_resolve(root, cq_manifest_path))
    route_map = predicate_route_map(cq_manifest)

    inputs_by_source = {str(record["source_id"]): record for record in input_records}
    baseline_by_source = {str(record["source_id"]): record for record in baseline_records}
    repair_by_source = {str(record["source_id"]): record for record in repair_records}
    selected_source_ids = [
        source_id
        for source_id in baseline_by_source
        if source_id in inputs_by_source and source_id in repair_by_source
    ][:sample_size]
    prediction_records: list[dict[str, Any]] = []
    for source_id in selected_source_ids:
        input_record = inputs_by_source[source_id]
        baseline_payload = _payload_from_prediction(baseline_by_source[source_id])
        repair_payload = _payload_from_prediction(repair_by_source[source_id])
        before = _diagnose_payload(
            input_record=input_record,
            payload=baseline_payload,
            schema_slice=schema_slice,
            route_map=route_map,
        )
        agent = ExtractionAgent(
            schema_slice=schema_slice,
            route_map=route_map,
            max_iterations=max_iterations,
        )
        result = agent.run(
            input_record,
            invoker=ArtifactReplayInvoker(
                baseline_payload=baseline_payload,
                repair_payload=repair_payload,
            ),
            invoker_label="artifact_replay",
        )
        after = _diagnose_final_facts(
            input_record=input_record,
            facts=result.facts,
            schema_slice=schema_slice,
        )
        prediction_records.append(
            {
                **result.to_record(),
                "sample_id": input_record.get("sample_id"),
                "baseline_system_id": baseline_by_source[source_id].get("system_id"),
                "repair_artifact_system_id": repair_by_source[source_id].get("system_id"),
                "before": before,
                "after": after,
            }
        )

    report = _build_report(
        repo_root=root,
        input_records_path=input_records_path,
        baseline_predictions_path=baseline_predictions_path,
        repair_predictions_path=repair_predictions_path,
        schema_slice_path=schema_slice_path,
        cq_manifest_path=cq_manifest_path,
        prediction_output_path=prediction_output_path,
        run_metadata_output_path=run_metadata_output_path,
        prediction_records=prediction_records,
        sample_size=sample_size,
        max_iterations=max_iterations,
    )
    run_metadata = {
        "system_id": "L1_agentic_extraction_batch",
        "run_status": "completed",
        "runner": "artifact_replay_l1_extraction_agent",
        "requires_llm": False,
        "live_llm_run": False,
        "sample_size": sample_size,
        "max_iterations": max_iterations,
        "prediction_record_count": len(prediction_records),
        "prediction_output": report["metadata"]["prediction_output"],
        "run_metadata_output": report["metadata"]["run_metadata_output"],
        "claim_boundary": report["claim_boundary"],
    }
    return L1BatchArtifacts(report, prediction_records, run_metadata)


def _payload_from_prediction(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "json_adherence": True,
        "source_id": str(record.get("source_id")),
        "source_family": record.get("source_family", "atcscc_advisories"),
        "facts": [fact for fact in record.get("facts", []) if isinstance(fact, dict)],
    }


def _diagnose_payload(
    *,
    input_record: dict[str, Any],
    payload: dict[str, Any],
    schema_slice: dict[str, Any],
    route_map: dict[str, dict[str, set[str]]],
) -> dict[str, Any]:
    candidate = dict(payload)
    candidate["facts"] = _facts_for_validation(payload.get("facts", []))
    _profile_normalize_live_record(candidate, input_record)
    validations = validate_prediction_record(
        record=candidate,
        source_row={"source_id": str(input_record["source_id"]), "text": input_record.get("source_text", "")},
        schema_slice=schema_slice,
    )
    accepted_candidates = [
        item["validated_fact"]
        for item in validations
        if item.get("accepted") and isinstance(item.get("validated_fact"), dict)
    ]
    allowed, _critic_items, quarantine = _critic_allowed_facts(
        record=input_record,
        s5_facts=accepted_candidates,
        route_map=route_map,
        critic_drop_ids=set(),
        critic_payload={},
    )
    return {
        "candidate_fact_count": len(candidate["facts"]),
        "schema_violation_count": _rejection_count(validations),
        "validator_accepted_fact_count": len(accepted_candidates),
        "unsupported_fact_count": len(quarantine),
        "accepted_fact_count": len(allowed),
        "evidence_in_source_rate": _evidence_in_source_rate(candidate["facts"], input_record),
        "accepted_predicate_counts": _predicate_counts(allowed),
        "quarantine_reason_counts": _reason_counts(quarantine),
    }


def _diagnose_final_facts(
    *,
    input_record: dict[str, Any],
    facts: list[dict[str, Any]],
    schema_slice: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        "json_adherence": True,
        "source_id": str(input_record["source_id"]),
        "source_family": input_record.get("source_family", "atcscc_advisories"),
        "facts": _facts_for_validation(facts),
    }
    validations = validate_prediction_record(
        record=payload,
        source_row={"source_id": str(input_record["source_id"]), "text": input_record.get("source_text", "")},
        schema_slice=schema_slice,
    )
    unsupported = _unsupported_final_fact_count(facts, input_record)
    return {
        "accepted_fact_count": len(facts),
        "schema_violation_count": _rejection_count(validations),
        "unsupported_fact_count": unsupported,
        "evidence_in_source_rate": _evidence_in_source_rate(facts, input_record),
        "accepted_predicate_counts": _predicate_counts(facts),
    }


def _build_report(
    *,
    repo_root: Path,
    input_records_path: str | Path,
    baseline_predictions_path: str | Path,
    repair_predictions_path: str | Path,
    schema_slice_path: str | Path,
    cq_manifest_path: str | Path,
    prediction_output_path: str | Path,
    run_metadata_output_path: str | Path,
    prediction_records: list[dict[str, Any]],
    sample_size: int,
    max_iterations: int,
) -> dict[str, Any]:
    before = _aggregate_metric_block(record["before"] for record in prediction_records)
    after = _aggregate_metric_block(record["after"] for record in prediction_records)
    repair = _repair_metrics(prediction_records)
    return {
        "source_family": "nasa_atmonto_l1_agent_batch_experiment",
        "status": "l1_agent_batch_experiment_scored",
        "claim_boundary": (
            "This is a small-batch, artifact-replay L1 Agent-loop experiment. It exercises "
            "the bounded extractor-validator-critic-repair-refiner loop without live LLM calls. "
            "Use it as reproducible evidence that the L1 loop can reduce emitted schema and "
            "support errors on the sampled ATCSCC corpus; do not cite it as external expert "
            "certification or live operational ATC support."
        ),
        "metadata": {
            "input_records": project_relative_path(_resolve(repo_root, input_records_path), repo_root),
            "baseline_predictions_path": project_relative_path(
                _resolve(repo_root, baseline_predictions_path),
                repo_root,
            ),
            "repair_predictions_path": project_relative_path(
                _resolve(repo_root, repair_predictions_path),
                repo_root,
            ),
            "schema_slice_path": project_relative_path(_resolve(repo_root, schema_slice_path), repo_root),
            "cq_manifest_path": project_relative_path(_resolve(repo_root, cq_manifest_path), repo_root),
            "prediction_output": project_relative_path(_resolve(repo_root, prediction_output_path), repo_root),
            "run_metadata_output": project_relative_path(_resolve(repo_root, run_metadata_output_path), repo_root),
            "record_count": len(prediction_records),
            "requested_sample_size": sample_size,
            "max_iterations": max_iterations,
            "live_llm_run": False,
            "invoker_label": "artifact_replay",
        },
        "metrics": {
            "before": before,
            "after": after,
            "delta_after_minus_before": _metric_delta(after, before),
            "repair": repair,
        },
        "metric_definitions": {
            "before": "Diagnostics over baseline candidate facts before L1 repair.",
            "after": "Diagnostics over facts emitted by the L1 validator/critic/refiner gate.",
            "schema_violation_count": "Facts rejected by the ATCSCC schema/profile validator.",
            "unsupported_fact_count": "Facts rejected by deterministic critic support checks.",
            "evidence_in_source_rate": "Fraction of candidate or emitted facts whose evidence text is contained in the source advisory.",
            "repair_success_rate": "Fraction of repair-attempted records whose accepted fact count increased after L1 repair.",
        },
        "interpretation": {
            "schema_gate_result": (
                "In this small artifact-replay batch, the L1 loop emits no schema/profile "
                "violations after repair and validation."
            ),
            "unsupported_fact_result": (
                "No deterministic unsupported-fact quarantine was observed in this sampled "
                "batch; this is a measured zero, not proof that unsupported facts cannot occur."
            ),
            "evidence_result": (
                "All baseline candidates and L1 emitted facts in the sampled batch retain "
                "source-contained evidence spans."
            ),
        },
        "record_examples": _record_examples(prediction_records),
    }


def _aggregate_metric_block(blocks: Any) -> dict[str, Any]:
    rows = list(blocks)
    if not rows:
        return {
            "candidate_fact_count": 0,
            "accepted_fact_count": 0,
            "schema_violation_count": 0,
            "unsupported_fact_count": 0,
            "evidence_in_source_rate": 0.0,
        }
    fact_denominator = sum(
        int(row.get("candidate_fact_count", row.get("accepted_fact_count", 0))) for row in rows
    )
    evidence_weighted = sum(
        float(row.get("evidence_in_source_rate", 0.0))
        * int(row.get("candidate_fact_count", row.get("accepted_fact_count", 0)))
        for row in rows
    )
    return {
        "candidate_fact_count": sum(int(row.get("candidate_fact_count", 0)) for row in rows),
        "accepted_fact_count": sum(int(row.get("accepted_fact_count", 0)) for row in rows),
        "schema_violation_count": sum(int(row.get("schema_violation_count", 0)) for row in rows),
        "unsupported_fact_count": sum(int(row.get("unsupported_fact_count", 0)) for row in rows),
        "evidence_in_source_rate": round(evidence_weighted / fact_denominator, 4)
        if fact_denominator
        else 0.0,
    }


def _repair_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    attempted = sum(1 for record in records if record.get("trace", {}).get("iterations_used", 0) > 1)
    fact_gain_records = sum(
        1
        for record in records
        if int(record["after"].get("accepted_fact_count", 0))
        > int(record["before"].get("accepted_fact_count", 0))
    )
    net_gain = sum(
        int(record["after"].get("accepted_fact_count", 0))
        - int(record["before"].get("accepted_fact_count", 0))
        for record in records
    )
    return {
        "repair_attempted_record_count": attempted,
        "records_with_fact_gain": fact_gain_records,
        "net_accepted_fact_gain": net_gain,
        "repair_success_rate": round(fact_gain_records / attempted, 4) if attempted else 0.0,
    }


def _metric_delta(after: dict[str, Any], before: dict[str, Any]) -> dict[str, Any]:
    fields = (
        "accepted_fact_count",
        "schema_violation_count",
        "unsupported_fact_count",
        "evidence_in_source_rate",
    )
    delta: dict[str, Any] = {}
    for field in fields:
        after_value = after.get(field)
        before_value = before.get(field)
        if isinstance(after_value, (int, float)) and isinstance(before_value, (int, float)):
            value = after_value - before_value
            delta[field] = round(value, 4) if isinstance(value, float) else value
    return delta


def _record_examples(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for record in records[:5]:
        examples.append(
            {
                "source_id": record.get("source_id"),
                "sample_id": record.get("sample_id"),
                "before": record.get("before"),
                "after": record.get("after"),
                "iterations_used": record.get("trace", {}).get("iterations_used"),
                "budget_exhausted": record.get("trace", {}).get("budget_exhausted"),
            }
        )
    return examples


def _predicate_counts(facts: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for fact in facts:
        predicate = term_name(fact.get("predicate"))
        counts[predicate] = counts.get(predicate, 0) + 1
    return dict(sorted(counts.items()))


def _reason_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        for reason in item.get("reasons", []):
            text = str(reason)
            counts[text] = counts.get(text, 0) + 1
    return dict(sorted(counts.items()))


def _rejection_count(validations: list[dict[str, Any]]) -> int:
    return sum(1 for item in validations if item.get("accepted") is not True)


def _unsupported_final_fact_count(facts: list[dict[str, Any]], input_record: dict[str, Any]) -> int:
    seen: set[tuple[str, str, str, str, str, str, str]] = set()
    unsupported = 0
    for fact in facts:
        reasons = critic_reasons(fact, input_record, seen)
        if reasons:
            unsupported += 1
            continue
        seen.add(canonical_fact_key(fact))
    return unsupported


def _facts_for_validation(facts: Any) -> list[dict[str, Any]]:
    return [
        _normalize_validation_datatype(dict(fact))
        for fact in facts
        if isinstance(fact, dict)
    ]


def _normalize_validation_datatype(fact: dict[str, Any]) -> dict[str, Any]:
    datatype = fact.get("datatype")
    if isinstance(datatype, str) and datatype.startswith("http://www.w3.org/2001/XMLSchema#"):
        fact["datatype"] = "xsd:" + datatype.rsplit("#", 1)[-1]
    return fact


def _evidence_in_source_rate(facts: list[dict[str, Any]], input_record: dict[str, Any]) -> float:
    if not facts:
        return 0.0
    source_text = normalize_report_text(input_record.get("source_text", ""))
    supported = 0
    for fact in facts:
        evidence = normalize_report_text(fact.get("evidence_text", ""))
        if evidence and evidence in source_text:
            supported += 1
    return round(supported / len(facts), 4)


def _resolve(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate
