from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agents.end_to_end_agent import ATCSCCEndToEndAgent
from aviation_agentic_ai.agents.types import EndToEndAnswer
from aviation_agentic_ai.ontology.atmonto_experiment import (
    FORMAL_INPUT_RECORDS_PATH,
    SCHEMA_SLICE_PATH,
)
from aviation_agentic_ai.paths import PROJECT_ROOT
from aviation_agentic_ai.reporting.atmonto.agentic_loop.contract import (
    DEFAULT_CQ_MANIFEST_PATH,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.independent_run_agents import (
    predicate_route_map,
    read_jsonl_objects,
)
from aviation_agentic_ai.reporting.atmonto.agentic_loop.l1_batch_experiment import (
    DEFAULT_BASELINE_PREDICTIONS_PATH,
    DEFAULT_REPAIR_PREDICTIONS_PATH,
    ArtifactReplayInvoker,
    _payload_from_prediction,
)
from aviation_agentic_ai.reporting.io import read_json_object_or_empty

DEFAULT_AGENT_DEMO_SOURCE_ID = "2026-05-19:032"
DEFAULT_AGENT_DEMO_QUESTION = "Which NAS elements are affected by this ATCSCC advisory?"


@dataclass(frozen=True)
class AgentDemoRun:
    advisory: dict[str, Any]
    answer: EndToEndAnswer
    baseline_fact_count: int
    repair_fact_count: int


def run_atcscc_agent_demo(
    *,
    source_id: str = DEFAULT_AGENT_DEMO_SOURCE_ID,
    question: str = DEFAULT_AGENT_DEMO_QUESTION,
    repo_root: str | Path = PROJECT_ROOT,
    input_records_path: str | Path = FORMAL_INPUT_RECORDS_PATH,
    baseline_predictions_path: str | Path = DEFAULT_BASELINE_PREDICTIONS_PATH,
    repair_predictions_path: str | Path = DEFAULT_REPAIR_PREDICTIONS_PATH,
    schema_slice_path: str | Path = SCHEMA_SLICE_PATH,
    cq_manifest_path: str | Path = DEFAULT_CQ_MANIFEST_PATH,
    max_iterations: int = 2,
) -> AgentDemoRun:
    """Run the deterministic L2 Agent demo with L1 artifact replay."""
    root = Path(repo_root)
    advisory = _record_by_source_id(_resolve(root, input_records_path), source_id)
    baseline = _record_by_source_id(_resolve(root, baseline_predictions_path), source_id)
    repair = _record_by_source_id(_resolve(root, repair_predictions_path), source_id)
    schema_slice = read_json_object_or_empty(_resolve(root, schema_slice_path))
    cq_manifest = read_json_object_or_empty(_resolve(root, cq_manifest_path))

    agent = ATCSCCEndToEndAgent(
        schema_slice=schema_slice,
        route_map=predicate_route_map(cq_manifest),
        max_iterations=max_iterations,
    )
    baseline_payload = _payload_from_prediction(baseline)
    repair_payload = _payload_from_prediction(repair)
    answer = agent.process(
        advisory,
        question=question,
        invoker=ArtifactReplayInvoker(
            baseline_payload=baseline_payload,
            repair_payload=repair_payload,
        ),
        invoker_label="artifact_replay",
    )
    return AgentDemoRun(
        advisory=advisory,
        answer=answer,
        baseline_fact_count=len(baseline_payload.get("facts", [])),
        repair_fact_count=len(repair_payload.get("facts", [])),
    )


def _resolve(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else root / candidate


def _record_by_source_id(path: Path, source_id: str) -> dict[str, Any]:
    for record in read_jsonl_objects(path):
        if str(record.get("source_id")) == source_id:
            return record
    raise ValueError(f"No record with source_id={source_id!r} in {path}")
