"""Repeated real-provider experiment for the bounded TMI Query Agent."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Any, Literal, Sequence

from langchain_core.globals import get_llm_cache, set_llm_cache
from pydantic import Field, model_validator
import yaml

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryScope,
    ModelCallRecord,
    StrictModel,
)
from aviation_agentic_ai.agent_system.evaluation_binding import (
    EvaluationBindingBlocked,
    verify_evaluation_revision_unchanged,
)
from aviation_agentic_ai.agent_system.knowledge_query import answer_question
from aviation_agentic_ai.agent_system.live_agent_evaluation import (
    LiveEvaluationTrial,
    _bind_live_query_runtime,
    _live_preflight_failures,
    _resolve_query_event_id,
    _verify_live_evaluation_binding,
    build_hybrid_query_run_artifact,
    score_query_trial,
    write_hybrid_query_run_artifact,
)
from aviation_agentic_ai.agent_system.query_runtime import open_query_runtime
from aviation_agentic_ai.agent_system.query_tool_registry import (
    query_tool_model_role,
)
from aviation_agentic_ai.agent_system.runtime import (
    FROZEN_MODEL,
    FROZEN_PROVIDER,
    FROZEN_TEMPERATURE,
)
from aviation_agentic_ai.agent_system.tool_model import (
    ToolPhase,
    capture_tool_model_calls,
    make_live_tool_calling_model,
)
from aviation_agentic_ai.config import load_environment, load_yaml


class LiveAgentExperimentAuthorizationError(RuntimeError):
    """Raised before writes when real provider execution is not authorized."""


class LiveAgentExperimentSuite(StrictModel):
    """Versioned repeated-measures real-provider experiment."""

    version: Literal["live-agent-experiment-v4"]
    suite_id: str = Field(min_length=1)
    minimum_successful_calls: int = Field(ge=100)
    minimum_cycles: int = Field(ge=1)
    maximum_cycles: int = Field(ge=1)
    future_frozen_evaluation: Literal["not_constructed"] = "not_constructed"
    trials: tuple[LiveEvaluationTrial, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_protocol(self) -> "LiveAgentExperimentSuite":
        if self.maximum_cycles < self.minimum_cycles:
            raise ValueError("maximum_cycles must be at least minimum_cycles")
        trial_ids = [trial.trial_id for trial in self.trials]
        if len(trial_ids) != len(set(trial_ids)):
            raise ValueError("experiment trial IDs must be unique")
        return self

    @property
    def required_source_ids(self) -> tuple[str, ...]:
        return tuple(sorted({trial.source_id for trial in self.trials}))


class ObservedProviderCall(StrictModel):
    """One provider turn captured before workflow-level sanitization."""

    experiment_id: str = Field(min_length=1)
    call_id: str = Field(min_length=1)
    recorded_at: str = Field(min_length=1)
    cycle: int = Field(ge=0)
    trial_id: str = Field(min_length=1)
    kind: Literal["query"]
    source_id: str = Field(min_length=1)
    role: str = Field(min_length=1)
    phase: Literal[
        "select_tool",
        "final_answer",
        "emit_proposal",
        "revision",
        "query_step",
    ]
    provider: str | None = None
    model: str | None = None
    system_fingerprint: str | None = None
    finish_reason: str | None = None
    prompt_set_id: str | None = None
    prompt_version: str | None = None
    temperature: float | None = None
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    latency_ms: float = Field(default=0.0, ge=0.0)
    cache_hit: bool = False
    attempt: int = Field(default=1, ge=1)
    error: str | None = None
    raw_response: str
    tool_calls: tuple[dict[str, Any], ...] = ()
    invalid_tool_calls: tuple[dict[str, Any], ...] = ()
    native_response: dict[str, Any] | None = None
    response_sha256: str = Field(min_length=64, max_length=64)

    @classmethod
    def from_model_call(
        cls,
        *,
        experiment_id: str,
        cycle: int,
        trial_id: str,
        kind: Literal["query"],
        source_id: str,
        phase: ToolPhase,
        record: ModelCallRecord,
        native_response: dict[str, Any] | None,
    ) -> "ObservedProviderCall":
        raw_payload = {
            "native_response": native_response,
            "error": record.error,
        }
        response_sha256 = hashlib.sha256(
            _canonical_json(raw_payload).encode("utf-8")
        ).hexdigest()
        identity = {
            "experiment_id": experiment_id,
            "cycle": cycle,
            "trial_id": trial_id,
            "source_id": source_id,
            "role": record.agent,
            "phase": phase,
            "attempt": record.attempt,
            "response_sha256": response_sha256,
        }
        call_id = "provider-call:" + hashlib.sha256(
            _canonical_json(identity).encode("utf-8")
        ).hexdigest()[:24]
        return cls(
            experiment_id=experiment_id,
            call_id=call_id,
            recorded_at=datetime.now(UTC).isoformat(),
            cycle=cycle,
            trial_id=trial_id,
            kind=kind,
            source_id=source_id,
            role=record.agent,
            phase=phase,
            provider=record.provider,
            model=record.model,
            system_fingerprint=record.system_fingerprint,
            finish_reason=record.finish_reason,
            prompt_set_id=record.prompt_set_id,
            prompt_version=record.prompt_version,
            temperature=record.temperature,
            input_tokens=record.input_tokens,
            output_tokens=record.output_tokens,
            latency_ms=record.latency_ms,
            cache_hit=record.cache_hit,
            attempt=record.attempt,
            error=record.error,
            raw_response=record.raw_response,
            tool_calls=tuple(
                call.model_dump(mode="json") for call in record.tool_calls
            ),
            invalid_tool_calls=tuple(record.invalid_tool_calls),
            native_response=native_response,
            response_sha256=response_sha256,
        )


class LiveAgentExperimentParsedOutput(StrictModel):
    """One parsed trial result linked to its raw provider turns."""

    experiment_id: str = Field(min_length=1)
    cycle: int = Field(ge=1)
    trial_id: str = Field(min_length=1)
    kind: Literal["query"]
    source_id: str = Field(min_length=1)
    role: Literal["query"]
    event_id: str | None = None
    workflow_status: Literal["ok", "insufficient", "blocked", "not_run"]
    model_acceptance_status: Literal[
        "passed",
        "failed",
        "blocked",
        "not_run",
    ]
    failure_code: str = ""
    workflow_provider_call_count: int = Field(ge=0)
    provider_call_ids: tuple[str, ...] = ()
    raw_response_sha256s: tuple[str, ...] = ()
    parsed_output: dict[str, Any] = Field(default_factory=dict)


class LiveAgentExperimentSummary(StrictModel):
    """Aggregate real-provider counts and artifact bindings."""

    manifest_version: Literal["tmi-event-live-agent-experiment-v4"] = (
        "tmi-event-live-agent-experiment-v4"
    )
    suite_id: str = Field(min_length=1)
    suite_checksum: str = Field(min_length=64, max_length=64)
    runner_status: Literal[
        "completed",
        "threshold_not_reached",
        "blocked_before_run",
        "invalidated_after_run",
        "runner_failed",
    ]
    model_identifier: str = FROZEN_MODEL
    provider_identifier: str = FROZEN_PROVIDER
    temperature: float = FROZEN_TEMPERATURE
    thinking: Literal["disabled"] = "disabled"
    automatic_retry_count: Literal[0] = 0
    local_model_cache: Literal["disabled"] = "disabled"
    provider_prompt_context_cache: Literal[
        "observed_automatic",
        "not_reported",
    ]
    provider_prompt_cache_reported_call_count: int = Field(ge=0)
    prompt_cache_hit_tokens: int = Field(ge=0)
    prompt_cache_miss_tokens: int = Field(ge=0)
    prompt_cache_usage_mismatch_count: int = Field(ge=0)
    prompt_set_ids: tuple[str, ...] = ()
    prompt_versions: tuple[str, ...] = ()
    tool_call_count: int = Field(ge=0)
    invalid_tool_call_count: int = Field(ge=0)
    minimum_successful_calls: int = Field(ge=100)
    minimum_cycles: int = Field(ge=1)
    maximum_cycles: int = Field(ge=1)
    completed_cycles: int = Field(ge=0)
    attempted_real_calls: int = Field(ge=0)
    successful_real_calls: int = Field(ge=0)
    failed_real_calls: int = Field(ge=0)
    provider_error_calls: int = Field(ge=0)
    returned_provider_calls: int = Field(ge=0)
    local_cache_hit_count: int = Field(ge=0)
    model_configuration_mismatch_count: int = Field(ge=0)
    unexpected_setup_call_count: int = Field(ge=0)
    call_binding_mismatch_count: int = Field(ge=0)
    missing_trial_execution_count: int = Field(ge=0)
    duplicate_trial_execution_count: int = Field(ge=0)
    unexpected_trial_execution_count: int = Field(ge=0)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    provider_latency_ms: float = Field(ge=0.0)
    trial_count: int = Field(ge=0)
    task_passed_count: int = Field(ge=0)
    task_failed_count: int = Field(ge=0)
    task_blocked_count: int = Field(ge=0)
    task_not_run_count: int = Field(ge=0)
    workflow_ok_count: int = Field(ge=0)
    workflow_insufficient_count: int = Field(ge=0)
    workflow_blocked_count: int = Field(ge=0)
    workflow_not_run_count: int = Field(ge=0)
    assertion_passed_count: int = Field(ge=0)
    assertion_failed_count: int = Field(ge=0)
    integrity_valid: bool
    threshold_satisfied: bool
    raw_response_artifact: str
    parsed_output_artifact: str
    raw_responses_sha256: str | None = None
    parsed_outputs_sha256: str | None = None
    runner_detail_codes: tuple[str, ...] = ()
    claim_boundary: str = (
        "Repeated real-provider behavior on five fixed Query Agent tasks. "
        "Provider-call "
        "success is separate from parsed-contract and task acceptance; calls "
        "are repeated measures, not independent evaluation samples."
    )


def load_live_agent_experiment_suite(
    path: str | Path,
) -> LiveAgentExperimentSuite:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return LiveAgentExperimentSuite.model_validate(payload)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _jsonl_bytes(rows: Sequence[StrictModel]) -> bytes:
    return "".join(
        _canonical_json(row.model_dump(mode="json")) + "\n" for row in rows
    ).encode("utf-8")


def _configuration_matches(call: ObservedProviderCall) -> bool:
    return (
        call.provider == FROZEN_PROVIDER
        and call.model == FROZEN_MODEL
        and call.temperature == FROZEN_TEMPERATURE
    )


def _is_successful_real_call(call: ObservedProviderCall) -> bool:
    has_response = bool(
        call.raw_response or call.tool_calls or call.invalid_tool_calls
    )
    return (
        call.error is None
        and not call.cache_hit
        and _configuration_matches(call)
        and has_response
    )


def _provider_prompt_cache_usage(
    call: ObservedProviderCall,
) -> tuple[int, int, bool]:
    native = call.native_response
    if not isinstance(native, dict):
        return 0, 0, False
    response_metadata = native.get("response_metadata")
    if not isinstance(response_metadata, dict):
        return 0, 0, False
    token_usage = response_metadata.get("token_usage")
    if not isinstance(token_usage, dict):
        return 0, 0, False
    hit = token_usage.get("prompt_cache_hit_tokens")
    miss = token_usage.get("prompt_cache_miss_tokens")
    if (
        not isinstance(hit, int)
        or isinstance(hit, bool)
        or hit < 0
        or not isinstance(miss, int)
        or isinstance(miss, bool)
        or miss < 0
    ):
        return 0, 0, False
    return hit, miss, True


def summarize_live_agent_experiment(
    *,
    suite_id: str,
    suite_checksum: str,
    minimum_successful_calls: int,
    minimum_cycles: int,
    maximum_cycles: int,
    completed_cycles: int,
    calls: Sequence[ObservedProviderCall],
    parsed_outputs: Sequence[LiveAgentExperimentParsedOutput],
    expected_trial_ids: Sequence[str],
    runner_status: Literal[
        "completed",
        "threshold_not_reached",
        "blocked_before_run",
        "invalidated_after_run",
        "runner_failed",
    ],
    raw_response_path: str,
    parsed_output_path: str,
    runner_detail_codes: Sequence[str] = (),
) -> LiveAgentExperimentSummary:
    call_rows = tuple(calls)
    parsed_rows = tuple(parsed_outputs)
    successful = sum(_is_successful_real_call(call) for call in call_rows)
    cache_hits = sum(call.cache_hit for call in call_rows)
    mismatches = sum(
        not _configuration_matches(call) for call in call_rows
    )
    setup_calls = 0
    prompt_cache_usage = tuple(
        _provider_prompt_cache_usage(call) for call in call_rows
    )
    prompt_cache_reported_calls = sum(
        reported for _hit, _miss, reported in prompt_cache_usage
    )
    prompt_cache_hit_tokens = sum(
        hit for hit, _miss, reported in prompt_cache_usage if reported
    )
    prompt_cache_miss_tokens = sum(
        miss for _hit, miss, reported in prompt_cache_usage if reported
    )
    prompt_cache_mismatches = sum(
        reported and hit + miss != call.input_tokens
        for call, (hit, miss, reported) in zip(
            call_rows,
            prompt_cache_usage,
            strict=True,
        )
    )
    duplicate_ids = len(call_rows) - len({call.call_id for call in call_rows})
    evaluation_call_ids = {call.call_id for call in call_rows}
    referenced_call_ids = [
        call_id
        for row in parsed_rows
        for call_id in row.provider_call_ids
    ]
    binding_mismatches = sum(
        row.workflow_provider_call_count != len(row.provider_call_ids)
        for row in parsed_rows
    )
    binding_mismatches += sum(
        call_id not in evaluation_call_ids
        for call_id in referenced_call_ids
    )
    binding_mismatches += len(referenced_call_ids) - len(
        set(referenced_call_ids)
    )
    binding_mismatches += len(
        evaluation_call_ids - set(referenced_call_ids)
    )
    expected_trial_pairs = {
        (cycle, trial_id)
        for cycle in range(1, completed_cycles + 1)
        for trial_id in expected_trial_ids
    }
    actual_trial_pairs = [
        (row.cycle, row.trial_id) for row in parsed_rows
    ]
    actual_trial_pair_set = set(actual_trial_pairs)
    missing_trials = len(expected_trial_pairs - actual_trial_pair_set)
    duplicate_trials = len(actual_trial_pairs) - len(actual_trial_pair_set)
    unexpected_trials = len(
        actual_trial_pair_set - expected_trial_pairs
    )
    assertions = [
        assertion
        for row in parsed_rows
        for assertion in row.parsed_output.get("assertions", ())
        if isinstance(assertion, dict)
    ]
    integrity_valid = (
        cache_hits == 0
        and mismatches == 0
        and setup_calls == 0
        and duplicate_ids == 0
        and binding_mismatches == 0
        and missing_trials == 0
        and duplicate_trials == 0
        and unexpected_trials == 0
        and prompt_cache_mismatches == 0
    )
    threshold_satisfied = (
        successful >= minimum_successful_calls
        and completed_cycles >= minimum_cycles
        and integrity_valid
        and runner_status == "completed"
    )
    return LiveAgentExperimentSummary(
        suite_id=suite_id,
        suite_checksum=suite_checksum,
        runner_status=runner_status,
        minimum_successful_calls=minimum_successful_calls,
        minimum_cycles=minimum_cycles,
        maximum_cycles=maximum_cycles,
        completed_cycles=completed_cycles,
        provider_prompt_context_cache=(
            "observed_automatic"
            if prompt_cache_reported_calls
            else "not_reported"
        ),
        provider_prompt_cache_reported_call_count=(
            prompt_cache_reported_calls
        ),
        prompt_cache_hit_tokens=prompt_cache_hit_tokens,
        prompt_cache_miss_tokens=prompt_cache_miss_tokens,
        prompt_cache_usage_mismatch_count=prompt_cache_mismatches,
        prompt_set_ids=tuple(
            sorted(
                {
                    call.prompt_set_id
                    for call in call_rows
                    if call.prompt_set_id
                }
            )
        ),
        prompt_versions=tuple(
            sorted(
                {
                    call.prompt_version
                    for call in call_rows
                    if call.prompt_version
                }
            )
        ),
        tool_call_count=sum(len(call.tool_calls) for call in call_rows),
        invalid_tool_call_count=sum(
            len(call.invalid_tool_calls) for call in call_rows
        ),
        attempted_real_calls=len(call_rows),
        successful_real_calls=successful,
        failed_real_calls=len(call_rows) - successful,
        provider_error_calls=sum(call.error is not None for call in call_rows),
        returned_provider_calls=sum(call.error is None for call in call_rows),
        local_cache_hit_count=cache_hits,
        model_configuration_mismatch_count=mismatches,
        unexpected_setup_call_count=setup_calls,
        call_binding_mismatch_count=binding_mismatches,
        missing_trial_execution_count=missing_trials,
        duplicate_trial_execution_count=duplicate_trials,
        unexpected_trial_execution_count=unexpected_trials,
        input_tokens=sum(call.input_tokens for call in call_rows),
        output_tokens=sum(call.output_tokens for call in call_rows),
        provider_latency_ms=sum(call.latency_ms for call in call_rows),
        trial_count=len(parsed_rows),
        task_passed_count=sum(
            row.model_acceptance_status == "passed" for row in parsed_rows
        ),
        task_failed_count=sum(
            row.model_acceptance_status == "failed" for row in parsed_rows
        ),
        task_blocked_count=sum(
            row.model_acceptance_status == "blocked" for row in parsed_rows
        ),
        task_not_run_count=sum(
            row.model_acceptance_status == "not_run" for row in parsed_rows
        ),
        workflow_ok_count=sum(
            row.workflow_status == "ok" for row in parsed_rows
        ),
        workflow_insufficient_count=sum(
            row.workflow_status == "insufficient" for row in parsed_rows
        ),
        workflow_blocked_count=sum(
            row.workflow_status == "blocked" for row in parsed_rows
        ),
        workflow_not_run_count=sum(
            row.workflow_status == "not_run" for row in parsed_rows
        ),
        assertion_passed_count=sum(
            assertion.get("passed") is True for assertion in assertions
        ),
        assertion_failed_count=sum(
            assertion.get("passed") is False for assertion in assertions
        ),
        integrity_valid=integrity_valid,
        threshold_satisfied=threshold_satisfied,
        raw_response_artifact=raw_response_path,
        parsed_output_artifact=parsed_output_path,
        runner_detail_codes=tuple(
            sorted(
                {
                    *runner_detail_codes,
                    *(
                        ("duplicate_provider_call_ids",)
                        if duplicate_ids
                        else ()
                    ),
                }
            )
        ),
    )


def _markdown_report(summary: LiveAgentExperimentSummary) -> str:
    return "\n".join(
        [
            "# Query Agent Real-Provider Experiment v4",
            "",
            "## Result",
            "",
            f"- Runner status: `{summary.runner_status}`",
            f"- Integrity valid: `{str(summary.integrity_valid).lower()}`",
            (
                "- Required successful real calls reached: "
                f"`{str(summary.threshold_satisfied).lower()}`"
            ),
            f"- Provider / model: `{summary.provider_identifier}` / "
            f"`{summary.model_identifier}`",
            f"- Temperature / thinking / retries: `{summary.temperature}` / "
            f"`{summary.thinking}` / `{summary.automatic_retry_count}`",
            (
                "- Provider prompt-context cache: "
                f"`{summary.provider_prompt_context_cache}` "
                "(input-prefix KV reuse, not response replay)"
            ),
            (
                "- Prompt-cache hit / miss tokens: "
                f"{summary.prompt_cache_hit_tokens} / "
                f"{summary.prompt_cache_miss_tokens}"
            ),
            f"- Prompt versions: {', '.join(summary.prompt_versions)}",
            f"- Completed cycles: {summary.completed_cycles}",
            f"- Attempted real calls: {summary.attempted_real_calls}",
            f"- Successful real calls: {summary.successful_real_calls}",
            f"- Failed real calls: {summary.failed_real_calls}",
            f"- Input / output tokens: "
            f"{summary.input_tokens} / {summary.output_tokens}",
            f"- Valid / invalid tool calls: "
            f"{summary.tool_call_count} / "
            f"{summary.invalid_tool_call_count}",
            f"- Provider latency: {summary.provider_latency_ms:.2f} ms",
            f"- Raw-response artifact: "
            f"`{summary.raw_response_artifact}`",
            f"- Parsed-output artifact: "
            f"`{summary.parsed_output_artifact}`",
            "",
            "## Task-level acceptance",
            "",
            f"- Acceptance passed / failed / blocked / not run: "
            f"{summary.task_passed_count} / {summary.task_failed_count} / "
            f"{summary.task_blocked_count} / "
            f"{summary.task_not_run_count}",
            f"- Workflow ok / insufficient / blocked / not run: "
            f"{summary.workflow_ok_count} / "
            f"{summary.workflow_insufficient_count} / "
            f"{summary.workflow_blocked_count} / "
            f"{summary.workflow_not_run_count}",
            f"- Assertions passed / failed: "
            f"{summary.assertion_passed_count} / "
            f"{summary.assertion_failed_count}",
            "",
            summary.claim_boundary,
            "",
        ]
    )


def write_live_agent_experiment_artifacts(
    *,
    output_dir: str | Path,
    report_dir: str | Path,
    calls: Sequence[ObservedProviderCall],
    parsed_outputs: Sequence[LiveAgentExperimentParsedOutput],
    summary: LiveAgentExperimentSummary,
) -> tuple[Path, Path, Path, Path, Path]:
    """Write detailed ignored artifacts and a sanitized tracked report."""

    runtime = Path(output_dir)
    reports = Path(report_dir)
    runtime.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    raw_path = runtime / "raw_responses_v4.jsonl"
    parsed_path = runtime / "parsed_outputs_v4.jsonl"
    raw_bytes = _jsonl_bytes(tuple(calls))
    parsed_bytes = _jsonl_bytes(tuple(parsed_outputs))
    raw_path.write_bytes(raw_bytes)
    parsed_path.write_bytes(parsed_bytes)
    final_summary = summary.model_copy(
        update={
            "raw_response_artifact": str(raw_path),
            "parsed_output_artifact": str(parsed_path),
            "raw_responses_sha256": hashlib.sha256(raw_bytes).hexdigest(),
            "parsed_outputs_sha256": hashlib.sha256(
                parsed_bytes
            ).hexdigest(),
        }
    )
    manifest_path = runtime / "experiment_manifest_v4.json"
    manifest_path.write_text(
        final_summary.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    sanitized_trials = [
        {
            "cycle": row.cycle,
            "trial_id": row.trial_id,
            "kind": row.kind,
            "source_id": row.source_id,
            "role": row.role,
            "workflow_status": row.workflow_status,
            "model_acceptance_status": row.model_acceptance_status,
            "failure_code": row.failure_code,
            "provider_call_count": len(row.provider_call_ids),
        }
        for row in parsed_outputs
    ]
    report_json = (
        reports / "agent_system_live_agent_experiment_v4.json"
    )
    report_json.write_text(
        json.dumps(
            {
                "summary": final_summary.model_dump(mode="json"),
                "trials": sanitized_trials,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    report_markdown = (
        reports / "agent_system_live_agent_experiment_v4.md"
    )
    report_markdown.write_text(
        _markdown_report(final_summary),
        encoding="utf-8",
    )
    return (
        raw_path,
        parsed_path,
        manifest_path,
        report_json,
        report_markdown,
    )


def _parsed_from_live_result(
    *,
    experiment_id: str,
    cycle: int,
    result: Any,
    calls: Sequence[ObservedProviderCall],
) -> LiveAgentExperimentParsedOutput:
    return LiveAgentExperimentParsedOutput(
        experiment_id=experiment_id,
        cycle=cycle,
        trial_id=result.trial_id,
        kind=result.kind,
        source_id=result.source_id,
        role=result.role,
        event_id=result.event_id,
        workflow_status=result.workflow_status,
        model_acceptance_status=result.model_acceptance_status,
        failure_code=result.failure_code,
        workflow_provider_call_count=result.provider_call_count,
        provider_call_ids=tuple(call.call_id for call in calls),
        raw_response_sha256s=tuple(
            call.response_sha256 for call in calls
        ),
        parsed_output={
            "detail_status": result.detail_status,
            "assertions": [
                assertion.model_dump(mode="json")
                for assertion in result.assertions
            ],
            "retrieved_fact_count": result.retrieved_fact_count,
            "retrieved_source_count": result.retrieved_source_count,
            "hybrid_query_run_artifact": result.query_run_artifact,
            "hybrid_query_run_artifact_sha256": (
                result.query_run_artifact_sha256
            ),
        },
    )


def _recording_observer(
    *,
    experiment_id: str,
    cycle: int,
    trial: LiveEvaluationTrial,
    calls: list[ObservedProviderCall],
    calls_by_trial: dict[tuple[int, str], list[ObservedProviderCall]],
) -> Any:
    def _observe(
        phase: ToolPhase,
        record: ModelCallRecord,
        native_response: dict[str, Any] | None,
    ) -> None:
        observed = ObservedProviderCall.from_model_call(
            experiment_id=experiment_id,
            cycle=cycle,
            trial_id=trial.trial_id,
            kind="query",
            source_id=trial.source_id,
            phase=phase,
            record=record,
            native_response=native_response,
        )
        calls.append(observed)
        calls_by_trial.setdefault(
            (cycle, trial.trial_id), []
        ).append(observed)

    return _observe


def _current_summary(
    *,
    suite: LiveAgentExperimentSuite,
    suite_checksum: str,
    completed_cycles: int,
    calls: Sequence[ObservedProviderCall],
    parsed_outputs: Sequence[LiveAgentExperimentParsedOutput],
    runner_status: Literal[
        "completed",
        "threshold_not_reached",
        "blocked_before_run",
        "invalidated_after_run",
        "runner_failed",
    ],
    runtime_root: Path,
    detail_codes: Sequence[str] = (),
) -> LiveAgentExperimentSummary:
    return summarize_live_agent_experiment(
        suite_id=suite.suite_id,
        suite_checksum=suite_checksum,
        minimum_successful_calls=suite.minimum_successful_calls,
        minimum_cycles=suite.minimum_cycles,
        maximum_cycles=suite.maximum_cycles,
        completed_cycles=completed_cycles,
        calls=calls,
        parsed_outputs=parsed_outputs,
        expected_trial_ids=tuple(
            trial.trial_id for trial in suite.trials
        ),
        runner_status=runner_status,
        raw_response_path=str(runtime_root / "raw_responses_v4.jsonl"),
        parsed_output_path=str(runtime_root / "parsed_outputs_v4.jsonl"),
        runner_detail_codes=detail_codes,
    )


def _close_query_runtime(runtime: Any | None) -> None:
    if runtime is None:
        return
    close = getattr(runtime.store, "close", None)
    if callable(close):
        close()


def run_live_agent_experiment(
    *,
    config_path: str | Path,
    suite_path: str | Path,
    store_dir: str | Path,
    output_dir: str | Path,
    report_dir: str | Path,
    allow_live_model: bool,
) -> LiveAgentExperimentSummary:
    """Run only the configured real provider until the frozen call gate."""

    if not allow_live_model:
        raise LiveAgentExperimentAuthorizationError(
            "real experiment requires --allow-live-model"
        )
    suite_file = Path(suite_path)
    suite = load_live_agent_experiment_suite(suite_file)
    suite_checksum = hashlib.sha256(suite_file.read_bytes()).hexdigest()
    config = load_yaml(config_path)
    load_environment()
    failures = _live_preflight_failures(config, environ=os.environ)
    runtime = None
    binding = None
    if not failures:
        try:
            runtime = open_query_runtime(config, store_dir=store_dir)
            binding = _bind_live_query_runtime(
                runtime=runtime,
                suite=suite,
            )
            _verify_live_evaluation_binding(binding, runtime)
        except EvaluationBindingBlocked as exc:
            failures = (exc.detail_code,)
        except (OSError, RuntimeError, TypeError, ValueError):
            failures = ("query_runtime_preflight_failed",)
    runtime_root = Path(output_dir)
    if failures:
        summary = _current_summary(
            suite=suite,
            suite_checksum=suite_checksum,
            completed_cycles=0,
            calls=(),
            parsed_outputs=(),
            runner_status="blocked_before_run",
            runtime_root=runtime_root,
            detail_codes=failures,
        )
        paths = write_live_agent_experiment_artifacts(
            output_dir=runtime_root,
            report_dir=report_dir,
            calls=(),
            parsed_outputs=(),
            summary=summary,
        )
        _close_query_runtime(runtime)
        return LiveAgentExperimentSummary.model_validate_json(
            paths[2].read_text(encoding="utf-8")
        )
    assert runtime is not None
    assert binding is not None
    shutil.rmtree(runtime_root, ignore_errors=True)
    runtime_root.mkdir(parents=True, exist_ok=True)
    (runtime_root / "evaluation_data_binding.json").write_text(
        binding.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    set_llm_cache(None)
    if get_llm_cache() is not None:
        summary = _current_summary(
            suite=suite,
            suite_checksum=suite_checksum,
            completed_cycles=0,
            calls=(),
            parsed_outputs=(),
            runner_status="blocked_before_run",
            runtime_root=runtime_root,
            detail_codes=("langchain_cache_not_disabled",),
        )
        paths = write_live_agent_experiment_artifacts(
            output_dir=runtime_root,
            report_dir=report_dir,
            calls=(),
            parsed_outputs=(),
            summary=summary,
        )
        _close_query_runtime(runtime)
        return LiveAgentExperimentSummary.model_validate_json(
            paths[2].read_text(encoding="utf-8")
        )

    calls: list[ObservedProviderCall] = []
    calls_by_trial: dict[
        tuple[int, str], list[ObservedProviderCall]
    ] = {}
    parsed_outputs: list[LiveAgentExperimentParsedOutput] = []
    completed_cycles = 0

    detail_codes: tuple[str, ...] = ()
    try:
        query_event_ids: dict[str, str] = {}
        for source_id in suite.required_source_ids:
            event_id = _resolve_query_event_id(
                source_id=source_id,
                store=runtime.store,
            )
            if event_id is None:
                raise EvaluationBindingBlocked(
                    "query_dependency_event_not_found"
                )
            query_event_ids[source_id] = event_id

        for cycle in range(1, suite.maximum_cycles + 1):
            for trial in suite.trials:
                _verify_live_evaluation_binding(binding, runtime)
                observer = _recording_observer(
                    experiment_id=suite.suite_id,
                    cycle=cycle,
                    trial=trial,
                    calls=calls,
                    calls_by_trial=calls_by_trial,
                )
                with capture_tool_model_calls(observer):
                    outcome = answer_question(
                        runtime=runtime,
                        question=trial.question,
                        scope=HybridQueryScope(
                            event_id=query_event_ids[trial.source_id]
                        ),
                        model_factory=lambda tools: (
                            make_live_tool_calling_model(
                                tools=tools,
                                role=query_tool_model_role(tools),
                            )
                        ),
                    )
                query_run = build_hybrid_query_run_artifact(
                    trial=trial,
                    event_id=query_event_ids[trial.source_id],
                    outcome=outcome,
                )
                query_run_path = write_hybrid_query_run_artifact(
                    runtime_root
                    / "hybrid_query_runs"
                    / f"cycle-{cycle:03d}"
                    / trial.trial_id,
                    query_run,
                )
                result = score_query_trial(
                    trial=trial,
                    repetition=cycle,
                    live_model=True,
                    event_id=query_event_ids[trial.source_id],
                    outcome=outcome,
                    query_run=query_run,
                    query_run_artifact_path=query_run_path,
                )
                parsed_outputs.append(
                    _parsed_from_live_result(
                        experiment_id=suite.suite_id,
                        cycle=cycle,
                        result=result,
                        calls=calls_by_trial.get(
                            (cycle, trial.trial_id), ()
                        ),
                    )
                )

            completed_cycles = cycle
            verify_evaluation_revision_unchanged(
                binding,
                runtime.store,
            )
            provisional = _current_summary(
                suite=suite,
                suite_checksum=suite_checksum,
                completed_cycles=completed_cycles,
                calls=calls,
                parsed_outputs=parsed_outputs,
                runner_status="completed",
                runtime_root=runtime_root,
            )
            status: Literal["completed", "threshold_not_reached"] = (
                "completed"
                if provisional.threshold_satisfied
                else "threshold_not_reached"
            )
            checkpoint = _current_summary(
                suite=suite,
                suite_checksum=suite_checksum,
                completed_cycles=completed_cycles,
                calls=calls,
                parsed_outputs=parsed_outputs,
                runner_status=status,
                runtime_root=runtime_root,
            )
            write_live_agent_experiment_artifacts(
                output_dir=runtime_root,
                report_dir=report_dir,
                calls=calls,
                parsed_outputs=parsed_outputs,
                summary=checkpoint,
            )
            if status == "completed":
                break
        else:
            status = "threshold_not_reached"
        verify_evaluation_revision_unchanged(binding, runtime.store)
    except EvaluationBindingBlocked as exc:
        status = (
            "invalidated_after_run"
            if calls or exc.runner_status == "invalidated_after_run"
            else "blocked_before_run"
        )
        detail_codes = (exc.detail_code,)
    except (OSError, RuntimeError, TypeError, ValueError, KeyError):
        status = "runner_failed"
        detail_codes = ("experiment_runner_exception",)

    final_summary = _current_summary(
        suite=suite,
        suite_checksum=suite_checksum,
        completed_cycles=completed_cycles,
        calls=calls,
        parsed_outputs=parsed_outputs,
        runner_status=status,
        runtime_root=runtime_root,
        detail_codes=detail_codes,
    )
    paths = write_live_agent_experiment_artifacts(
        output_dir=runtime_root,
        report_dir=report_dir,
        calls=calls,
        parsed_outputs=parsed_outputs,
        summary=final_summary,
    )
    _close_query_runtime(runtime)
    return LiveAgentExperimentSummary.model_validate_json(
        paths[2].read_text(encoding="utf-8")
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the versioned repeated DeepSeek experiment until at least "
            "100 successful real provider calls are recorded."
        )
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--store-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--allow-live-model", action="store_true")
    args = parser.parse_args(argv)
    try:
        summary = run_live_agent_experiment(
            config_path=args.config,
            suite_path=args.suite,
            store_dir=args.store_dir,
            output_dir=args.output_dir,
            report_dir=args.report_dir,
            allow_live_model=args.allow_live_model,
        )
    except (
        LiveAgentExperimentAuthorizationError,
        ValueError,
    ) as exc:
        parser.error(str(exc))
    print(
        "Real Agent experiment: "
        f"runner={summary.runner_status}, "
        f"model={summary.model_identifier}, "
        f"attempted={summary.attempted_real_calls}, "
        f"successful={summary.successful_real_calls}, "
        f"failed={summary.failed_real_calls}"
    )
    return 0 if summary.threshold_satisfied else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "LiveAgentExperimentAuthorizationError",
    "LiveAgentExperimentParsedOutput",
    "LiveAgentExperimentSuite",
    "LiveAgentExperimentSummary",
    "ObservedProviderCall",
    "load_live_agent_experiment_suite",
    "run_live_agent_experiment",
    "summarize_live_agent_experiment",
    "write_live_agent_experiment_artifacts",
]
