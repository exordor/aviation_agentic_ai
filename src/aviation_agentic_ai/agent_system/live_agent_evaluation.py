"""Explicit real-model smoke evaluation for the bounded TMI Query Agent."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Any, Literal, Mapping, Sequence

import yaml
from pydantic import Field, model_validator

from aviation_agentic_ai.agent_system.audit import sanitize_text
from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryScope,
    ModelCallRecord,
    QueryToolOutcome,
    StrictModel,
)
from aviation_agentic_ai.agent_system.evaluation_binding import (
    EvaluationBindingBlocked,
    EvaluationDataBinding,
    bind_evaluation_data,
    verify_evaluation_data_binding,
    verify_evaluation_revision_unchanged,
)
from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
)
from aviation_agentic_ai.agent_system.knowledge_query import (
    answer_question,
)
from aviation_agentic_ai.agent_system.hybrid_query_agent import (
    MAX_QUERY_PROVIDER_TURNS,
    MAX_QUERY_TOOL_CALLS,
    validate_hybrid_query_statement,
)
from aviation_agentic_ai.agent_system.prompts import get_prompt_catalog
from aviation_agentic_ai.agent_system.query_runtime import (
    QueryRuntime,
    open_query_runtime,
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
from aviation_agentic_ai.agent_system.query_tool_registry import (
    QUERY_CONTROL_TOOL_NAMES,
    QUERY_EVIDENCE_TOOL_NAMES,
)
from aviation_agentic_ai.config import (
    load_environment,
    load_yaml,
)


HYBRID_QUERY_READ_TOOLS = QUERY_EVIDENCE_TOOL_NAMES
HYBRID_QUERY_CONTROL_TOOLS = QUERY_CONTROL_TOOL_NAMES
DEFAULT_LIVE_EVALUATION_REPORT_STEM = "agent_system_live_agent_smoke_v4"
LIVE_EVALUATION_REPORT_STEM_PATTERN = r"^[a-z0-9][a-z0-9_-]*$"


class LiveEvaluationAuthorizationError(RuntimeError):
    """Raised before any write when live execution was not authorized."""


class LiveEvaluationTrial(StrictModel):
    """One versioned development or regression Query Agent trial."""

    trial_id: str = Field(min_length=1)
    kind: Literal["query"] = "query"
    partition: Literal["development", "regression"]
    source_id: str = Field(min_length=1)
    expected_role: Literal["query"] = "query"
    question: str = Field(min_length=1)
    required_tool_names: tuple[str, ...] = ()
    required_graph_path_kinds: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _validate_requirements(self) -> "LiveEvaluationTrial":
        unknown = set(self.required_tool_names) - HYBRID_QUERY_READ_TOOLS
        if unknown:
            raise ValueError(
                "required_tool_names contains unknown Query Agent tools"
            )
        if (
            self.required_graph_path_kinds
            and "read_tmi_event_graph" not in self.required_tool_names
        ):
            raise ValueError(
                "required graph paths require read_tmi_event_graph"
            )
        return self


class LiveEvaluationSuite(StrictModel):
    """Versioned development/regression smoke-evaluation manifest."""

    version: Literal["live-agent-smoke-v4"]
    suite_id: str = Field(min_length=1)
    report_stem: str = Field(
        default=DEFAULT_LIVE_EVALUATION_REPORT_STEM,
        min_length=1,
        max_length=128,
        pattern=LIVE_EVALUATION_REPORT_STEM_PATTERN,
    )
    repetitions: int = Field(default=1, ge=1)
    future_frozen_evaluation: Literal["not_constructed"] = "not_constructed"
    trials: tuple[LiveEvaluationTrial, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_trials(self) -> "LiveEvaluationSuite":
        trial_ids = [trial.trial_id for trial in self.trials]
        if len(trial_ids) != len(set(trial_ids)):
            raise ValueError("live evaluation trial IDs must be unique")
        return self

    @property
    def required_source_ids(self) -> tuple[str, ...]:
        """Logical advisory sources that must resolve in the live store."""

        return tuple(sorted({trial.source_id for trial in self.trials}))


class LiveEvaluationProviderCall(StrictModel):
    """One native provider turn retained only in the ignored runtime output."""

    suite_id: str = Field(min_length=1)
    call_id: str = Field(min_length=1)
    recorded_at: str = Field(min_length=1)
    repetition: int = Field(ge=1)
    trial_id: str = Field(min_length=1)
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
        suite_id: str,
        repetition: int,
        trial: LiveEvaluationTrial,
        phase: ToolPhase,
        record: ModelCallRecord,
        native_response: dict[str, Any] | None,
    ) -> "LiveEvaluationProviderCall":
        """Bind one observed provider turn to exactly one evaluation trial."""

        response_sha256 = hashlib.sha256(
            _canonical_json(
                {
                    "native_response": native_response,
                    "error": record.error,
                }
            ).encode("utf-8")
        ).hexdigest()
        identity = {
            "suite_id": suite_id,
            "repetition": repetition,
            "trial_id": trial.trial_id,
            "source_id": trial.source_id,
            "role": record.agent,
            "phase": phase,
            "attempt": record.attempt,
            "response_sha256": response_sha256,
        }
        call_id = "provider-call:" + hashlib.sha256(
            _canonical_json(identity).encode("utf-8")
        ).hexdigest()[:24]
        return cls(
            suite_id=suite_id,
            call_id=call_id,
            recorded_at=datetime.now(UTC).isoformat(),
            repetition=repetition,
            trial_id=trial.trial_id,
            source_id=trial.source_id,
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


class LiveEvaluationAssertion(StrictModel):
    """One bounded, payload-free acceptance check."""

    check_id: str = Field(min_length=1)
    passed: bool
    detail_code: str = Field(min_length=1)


class HybridQueryRunStatement(StrictModel):
    """One sanitized answer statement and its typed citation verdicts."""

    kind: Literal[
        "source_fact",
        "source_record",
        "non_causal_context",
        "public_observation",
        "similarity",
    ]
    text: str = Field(min_length=1)
    event_ids: tuple[str, ...] = ()
    fact_ids: tuple[str, ...] = ()
    profile_gap_ids: tuple[str, ...] = ()
    context_association_ids: tuple[str, ...] = ()
    observation_ids: tuple[str, ...] = ()
    graph_path_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    source_version_ids: tuple[str, ...] = ()
    source_anchor_ids: tuple[str, ...] = ()
    chunk_ids: tuple[str, ...] = ()
    citation_valid: bool
    claim_boundary_valid: bool
    validation_error: str = ""


class HybridQueryRunSupport(StrictModel):
    """One sanitized evidence-kind and source binding used for validation."""

    kind: Literal[
        "source_fact",
        "source_record",
        "non_causal_context",
        "public_observation",
        "similarity",
    ]
    event_ids: tuple[str, ...] = ()
    fact_ids: tuple[str, ...] = ()
    profile_gap_ids: tuple[str, ...] = ()
    context_association_ids: tuple[str, ...] = ()
    observation_ids: tuple[str, ...] = ()
    graph_path_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    source_version_ids: tuple[str, ...] = ()
    source_anchor_ids: tuple[str, ...] = ()
    chunk_ids: tuple[str, ...] = ()


class HybridQueryRunTool(StrictModel):
    """One sanitized read-only tool trace retained by the evaluator."""

    name: str = Field(min_length=1)
    status: Literal["ok", "insufficient", "blocked"]
    reference_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    source_version_ids: tuple[str, ...] = ()
    source_anchor_ids: tuple[str, ...] = ()
    chunk_ids: tuple[str, ...] = ()


class HybridQueryRunArtifact(StrictModel):
    """Evaluator-owned Hybrid Query trace without raw model/tool payloads."""

    manifest_version: Literal["tmi-event-query-run-v1"] = (
        "tmi-event-query-run-v1"
    )
    trial_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    run_status: Literal["ok", "insufficient", "blocked"]
    answer_contract_status: Literal["valid", "invalid", "missing"]
    statements: tuple[HybridQueryRunStatement, ...] = ()
    support_records: tuple[HybridQueryRunSupport, ...] = ()
    tools: tuple[HybridQueryRunTool, ...] = ()
    graph_path_kinds: tuple[str, ...] = ()


class LiveEvaluationResult(StrictModel):
    """One sanitized live or offline trial result."""

    trial_id: str = Field(min_length=1)
    repetition: int = Field(ge=1)
    kind: Literal["query"]
    source_id: str = Field(min_length=1)
    event_id: str | None = None
    role: Literal["query"]
    live_model: bool
    workflow_status: Literal["ok", "insufficient", "blocked", "not_run"]
    activation_status: Literal["activated", "not_activated", "not_reached"]
    model_acceptance_status: Literal["passed", "failed", "blocked", "not_run"]
    detail_status: str = ""
    assertions: tuple[LiveEvaluationAssertion, ...] = ()
    provider: str | None = None
    model: str | None = None
    system_fingerprints: tuple[str, ...] = ()
    prompt_set_id: str | None = None
    prompt_version: str | None = None
    temperature: float | None = None
    provider_call_count: int = Field(default=0, ge=0)
    provider_call_ids: tuple[str, ...] = ()
    native_tool_call_count: int = Field(default=0, ge=0)
    bound_tool_execution_count: int = Field(default=0, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    provider_latency_ms: float = Field(default=0.0, ge=0.0)
    tool_latency_ms: float = Field(default=0.0, ge=0.0)
    retrieved_fact_count: int = Field(default=0, ge=0)
    retrieved_source_count: int = Field(default=0, ge=0)
    query_run_artifact: str | None = None
    query_run_artifact_sha256: str | None = Field(
        default=None,
        min_length=64,
        max_length=64,
    )
    failure_code: str = ""


class LiveEvaluationSummary(StrictModel):
    """Aggregate smoke outcome over one frozen live-store binding."""

    manifest_version: Literal["tmi-event-live-evaluation-v4"] = (
        "tmi-event-live-evaluation-v4"
    )
    suite_id: str = Field(min_length=1)
    suite_checksum: str = Field(min_length=64, max_length=64)
    results_checksum: str = Field(min_length=64, max_length=64)
    repetitions: int = Field(ge=1)
    runner_status: Literal[
        "completed",
        "blocked_before_run",
        "runner_failed",
    ]
    model_acceptance_status: Literal[
        "passed",
        "failed",
        "blocked",
        "not_run",
    ]
    live_model: bool
    provider: Literal["deepseek"] = "deepseek"
    model: Literal["deepseek-v4-pro"] = "deepseek-v4-pro"
    temperature: Literal[0.0] = 0.0
    thinking: Literal["disabled"] = "disabled"
    automatic_retry_count: Literal[0] = 0
    runner_detail_codes: tuple[str, ...] = ()
    semantic_resolution_status: Literal[
        "not_evaluated_no_natural_ambiguity"
    ] = "not_evaluated_no_natural_ambiguity"
    trial_count: int = Field(ge=0)
    passed_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)
    blocked_count: int = Field(ge=0)
    not_run_count: int = Field(ge=0)
    provider_call_count: int = Field(ge=0)
    native_tool_call_count: int = Field(ge=0)
    bound_tool_execution_count: int = Field(ge=0)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    provider_latency_ms: float = Field(ge=0.0)
    tool_latency_ms: float = Field(ge=0.0)
    claim_boundary: str = (
        "Provider compatibility and bounded-behavior measurements over a "
        "versioned development/regression task suite; repetitions are "
        "repeated measurements, not independent samples, a frozen holdout, "
        "or a Semantic Resolution evaluation."
    )


def _assertion(
    check_id: str,
    passed: bool,
    *,
    passed_code: str,
    failed_code: str,
) -> LiveEvaluationAssertion:
    return LiveEvaluationAssertion(
        check_id=check_id,
        passed=passed,
        detail_code=passed_code if passed else failed_code,
    )


def _model_configuration_ok(
    calls: Sequence[ModelCallRecord],
    *,
    role: str,
) -> bool:
    return bool(calls) and all(
        call.agent == role
        and call.provider == FROZEN_PROVIDER
        and call.model == FROZEN_MODEL
        and call.temperature == FROZEN_TEMPERATURE
        and call.error is None
        for call in calls
    )


def _shared_model_metadata(
    calls: Sequence[ModelCallRecord],
) -> dict[str, Any]:
    prompt_set_ids = {call.prompt_set_id for call in calls if call.prompt_set_id}
    prompt_versions = {call.prompt_version for call in calls if call.prompt_version}
    return {
        "provider": FROZEN_PROVIDER if calls else None,
        "model": FROZEN_MODEL if calls else None,
        "system_fingerprints": tuple(
            sorted(
                {
                    call.system_fingerprint
                    for call in calls
                    if call.system_fingerprint
                }
            )
        ),
        "prompt_set_id": (
            next(iter(prompt_set_ids)) if len(prompt_set_ids) == 1 else None
        ),
        "prompt_version": (
            next(iter(prompt_versions)) if len(prompt_versions) == 1 else None
        ),
        "temperature": FROZEN_TEMPERATURE if calls else None,
        "provider_call_count": len(calls),
        "native_tool_call_count": sum(
            len(call.tool_calls) for call in calls
        ),
        "input_tokens": sum(call.input_tokens for call in calls),
        "output_tokens": sum(call.output_tokens for call in calls),
        "provider_latency_ms": sum(call.latency_ms for call in calls),
    }


def build_hybrid_query_run_artifact(
    *,
    trial: LiveEvaluationTrial,
    event_id: str,
    outcome: QueryToolOutcome,
) -> HybridQueryRunArtifact:
    """Build the evaluator's sanitized statement/tool evidence record."""

    support_records = list(outcome.support_records)
    statements = tuple(
        HybridQueryRunStatement(
            kind=statement.kind,
            text=sanitize_text(statement.text),
            event_ids=statement.support_event_ids,
            fact_ids=statement.support_fact_ids,
            profile_gap_ids=statement.support_profile_gap_ids,
            context_association_ids=(
                statement.support_context_association_ids
            ),
            observation_ids=statement.support_observation_ids,
            graph_path_ids=statement.support_graph_path_ids,
            source_ids=statement.support_source_ids,
            source_version_ids=statement.support_source_version_ids,
            source_anchor_ids=statement.support_source_anchor_ids,
            chunk_ids=statement.support_chunk_ids,
            citation_valid=(
                validate_hybrid_query_statement(
                    statement.model_copy(
                        update={"text": "Evidence-supported statement."}
                    ),
                    support_records,
                )
                is None
            ),
            claim_boundary_valid=(
                (
                    validation_error := validate_hybrid_query_statement(
                        statement,
                        support_records,
                    )
                )
                is None
                or "claim boundary" not in validation_error
            ),
            validation_error=sanitize_text(validation_error or ""),
        )
        for statement in outcome.answer_statements
    )
    support_summaries = tuple(
        HybridQueryRunSupport(
            kind=record.kind,
            event_ids=record.event_ids,
            fact_ids=record.fact_ids,
            profile_gap_ids=record.profile_gap_ids,
            context_association_ids=record.context_association_ids,
            observation_ids=record.observation_ids,
            graph_path_ids=record.graph_path_ids,
            source_ids=record.source_ids,
            source_version_ids=record.source_version_ids,
            source_anchor_ids=record.source_anchor_ids,
            chunk_ids=record.chunk_ids,
        )
        for record in support_records
    )
    tools = tuple(
        HybridQueryRunTool(
            name=trace.tool,
            status=trace.status,
            reference_ids=tuple(
                sorted(
                    {
                        *trace.result_refs,
                        *trace.context_association_ids,
                        *trace.observation_ids,
                        *trace.derivation_ids,
                    }
                )
            ),
            source_ids=tuple(sorted(set(trace.source_ids))),
            source_version_ids=tuple(
                sorted(set(trace.source_version_ids))
            ),
            source_anchor_ids=tuple(
                sorted(set(trace.source_anchor_ids))
            ),
            chunk_ids=tuple(sorted(set(trace.chunk_ids))),
        )
        for trace in outcome.tool_calls
    )
    return HybridQueryRunArtifact(
        trial_id=trial.trial_id,
        event_id=event_id,
        run_status=outcome.status,
        answer_contract_status=(
            "valid"
            if outcome.status in {"ok", "insufficient"}
            else "invalid"
        ),
        statements=statements,
        support_records=support_summaries,
        tools=tools,
        graph_path_kinds=tuple(
            sorted(
                {
                    path.path_kind
                    for path in outcome.retrieved_graph_paths
                }
            )
        ),
    )


def write_hybrid_query_run_artifact(
    output_dir: str | Path,
    artifact: HybridQueryRunArtifact,
) -> Path:
    """Persist one evaluator-owned, payload-free Hybrid Query run."""

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / "hybrid_query_run.json"
    path.write_text(
        artifact.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def score_query_trial(
    *,
    trial: LiveEvaluationTrial,
    repetition: int,
    live_model: bool,
    event_id: str,
    outcome: QueryToolOutcome,
    query_run: HybridQueryRunArtifact | None = None,
    query_run_artifact_path: str | Path | None = None,
) -> LiveEvaluationResult:
    """Score one real always-on Hybrid Query Agent execution."""

    calls = tuple(
        call
        for call in outcome.model_calls
        if call.agent == "query"
    )
    native_tools = [
        tool_call.name for call in calls for tool_call in call.tool_calls
    ]
    bound_tools = [trace.tool for trace in outcome.tool_calls]
    assertions = (
        _assertion(
            "agent_activated",
            bool(calls),
            passed_code="activated_with_real_provider_calls",
            failed_code="query_agent_not_activated",
        ),
        _assertion(
            "bounded_execution",
            1 <= len(calls) <= MAX_QUERY_PROVIDER_TURNS
            and len(outcome.tool_calls) <= MAX_QUERY_TOOL_CALLS,
            passed_code="within_existing_model_and_tool_budgets",
            failed_code="query_budget_not_satisfied",
        ),
        _assertion(
            "frozen_model_contract",
            _model_configuration_ok(
                calls,
                role="query",
            ),
            passed_code="frozen_deepseek_configuration_observed",
            failed_code="model_configuration_or_provider_call_failed",
        ),
        _assertion(
            "read_only_registered_tools",
            bool(bound_tools)
            and all(
                name in HYBRID_QUERY_READ_TOOLS
                for name in (*native_tools, *bound_tools)
            ),
            passed_code="only_hybrid_query_read_tools_observed",
            failed_code="unregistered_or_write_tool_observed",
        ),
        _assertion(
            "query_run_contract",
            outcome.status == "ok"
            and query_run is not None
            and query_run.run_status == outcome.status
            and query_run.answer_contract_status == "valid"
            and bool(query_run.statements)
            and query_run_artifact_path is not None
            and Path(query_run_artifact_path).is_file(),
            passed_code="evaluator_owned_query_run_is_valid",
            failed_code="valid_evaluator_owned_query_run_not_observed",
        ),
        _assertion(
            "statement_citations",
            query_run is not None
            and bool(query_run.statements)
            and all(
                statement.citation_valid
                for statement in query_run.statements
            ),
            passed_code="every_statement_has_trace_bound_citations",
            failed_code="statement_citation_not_supported_by_tool_trace",
        ),
        _assertion(
            "statement_claim_boundaries",
            query_run is not None
            and bool(query_run.statements)
            and all(
                statement.claim_boundary_valid
                for statement in query_run.statements
            ),
            passed_code="every_statement_respects_claim_boundaries",
            failed_code="statement_crossed_claim_boundary",
        ),
        _assertion(
            "tool_trace_status",
            query_run is not None
            and bool(query_run.tools)
            and len(query_run.tools) == len(outcome.tool_calls)
            and any(tool.status == "ok" for tool in query_run.tools)
            and all(
                tool.name in HYBRID_QUERY_READ_TOOLS
                and tool.status != "blocked"
                for tool in query_run.tools
            ),
            passed_code="query_tool_trace_has_support_without_blocked_tools",
            failed_code="query_tool_trace_missing_or_unsuccessful",
        ),
        _assertion(
            "required_tools_observed",
            set(trial.required_tool_names).issubset(bound_tools),
            passed_code="all_required_query_tools_observed",
            failed_code="required_query_tool_not_observed",
        ),
        _assertion(
            "required_graph_paths_observed",
            set(trial.required_graph_path_kinds).issubset(
                {
                    path.path_kind
                    for path in outcome.retrieved_graph_paths
                }
            ),
            passed_code="all_required_graph_path_kinds_observed",
            failed_code="required_graph_path_kind_not_observed",
        ),
    )
    blocked = any(call.error for call in calls)
    if blocked:
        acceptance: Literal["passed", "failed", "blocked", "not_run"] = (
            "blocked"
        )
    elif all(assertion.passed for assertion in assertions):
        acceptance = "passed"
    else:
        acceptance = "failed"
    return LiveEvaluationResult(
        trial_id=trial.trial_id,
        repetition=repetition,
        kind="query",
        source_id=trial.source_id,
        event_id=event_id,
        role="query",
        live_model=live_model,
        workflow_status=outcome.status,
        activation_status="activated" if calls else "not_activated",
        model_acceptance_status=acceptance,
        assertions=assertions,
        bound_tool_execution_count=len(outcome.tool_calls),
        tool_latency_ms=sum(
            trace.duration_ms for trace in outcome.tool_calls
        ),
        retrieved_fact_count=len(set(outcome.retrieved_fact_ids)),
        retrieved_source_count=len(set(outcome.source_ids)),
        query_run_artifact=(
            str(query_run_artifact_path)
            if query_run_artifact_path is not None
            else None
        ),
        query_run_artifact_sha256=(
            hashlib.sha256(
                Path(query_run_artifact_path).read_bytes()
            ).hexdigest()
            if query_run_artifact_path is not None
            and Path(query_run_artifact_path).is_file()
            else None
        ),
        failure_code=(
            ""
            if acceptance == "passed"
            else (
                "query_provider_or_model_call_error"
                if acceptance == "blocked"
                else (
                    "query_answer_contract_or_support_failed"
                    if outcome.status == "blocked"
                    else "query_acceptance_failed"
                )
            )
        ),
        **_shared_model_metadata(calls),
    )


def load_live_evaluation_suite(
    path: str | Path,
) -> LiveEvaluationSuite:
    """Load and validate one tracked YAML suite."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return LiveEvaluationSuite.model_validate(payload)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _result_bytes(results: Sequence[LiveEvaluationResult]) -> bytes:
    return "".join(
        _canonical_json(result.model_dump(mode="json")) + "\n"
        for result in results
    ).encode("utf-8")


def _provider_call_bytes(
    calls: Sequence[LiveEvaluationProviderCall],
) -> bytes:
    return "".join(
        _canonical_json(call.model_dump(mode="json")) + "\n"
        for call in calls
    ).encode("utf-8")


def _is_successful_real_call(call: LiveEvaluationProviderCall) -> bool:
    """Require a returned native response under the frozen provider contract."""

    expected_sha256 = hashlib.sha256(
        _canonical_json(
            {
                "native_response": call.native_response,
                "error": call.error,
            }
        ).encode("utf-8")
    ).hexdigest()
    return (
        call.error is None
        and call.provider == FROZEN_PROVIDER
        and call.model == FROZEN_MODEL
        and call.temperature == FROZEN_TEMPERATURE
        and call.native_response is not None
        and call.response_sha256 == expected_sha256
    )


def _provider_call_binding_failures(
    results: Sequence[LiveEvaluationResult],
    calls: Sequence[LiveEvaluationProviderCall],
) -> tuple[str, ...]:
    """Verify one-to-one raw-call binding before reporting live results."""

    failures: list[str] = []
    call_ids = [call.call_id for call in calls]
    if len(call_ids) != len(set(call_ids)):
        failures.append("duplicate_raw_provider_call_id")
    calls_by_id = {call.call_id: call for call in calls}
    referenced_ids: list[str] = []
    for result in results:
        ids = tuple(result.provider_call_ids)
        referenced_ids.extend(ids)
        if result.activation_status == "activated" and not ids:
            failures.append("activated_trial_missing_raw_provider_call")
        if result.provider_call_count != len(ids):
            failures.append("parsed_raw_provider_call_count_mismatch")
        for call_id in ids:
            call = calls_by_id.get(call_id)
            if call is None:
                failures.append("parsed_trial_references_missing_raw_call")
                continue
            if (
                call.repetition != result.repetition
                or call.trial_id != result.trial_id
                or call.source_id != result.source_id
            ):
                failures.append("raw_call_bound_to_wrong_parsed_trial")
    if len(referenced_ids) != len(set(referenced_ids)):
        failures.append("raw_provider_call_referenced_more_than_once")
    if set(call_ids) - set(referenced_ids):
        failures.append("orphan_raw_provider_call")
    return tuple(sorted(set(failures)))


def summarize_live_evaluation(
    *,
    suite_id: str,
    suite_checksum: str,
    repetitions: int,
    results: Sequence[LiveEvaluationResult],
    runner_status: Literal[
        "completed",
        "blocked_before_run",
        "runner_failed",
    ],
    live_model: bool,
    runner_detail_codes: Sequence[str] = (),
) -> LiveEvaluationSummary:
    """Aggregate typed trial rows without inspecting model payloads."""

    rows = tuple(results)
    if any(row.live_model is not live_model for row in rows):
        raise ValueError(
            "summary live_model flag disagrees with trial records"
        )
    passed = sum(row.model_acceptance_status == "passed" for row in rows)
    failed = sum(row.model_acceptance_status == "failed" for row in rows)
    blocked = sum(row.model_acceptance_status == "blocked" for row in rows)
    not_run = sum(row.model_acceptance_status == "not_run" for row in rows)
    if runner_status != "completed":
        acceptance: Literal["passed", "failed", "blocked", "not_run"] = (
            "blocked"
        )
    elif not rows:
        acceptance = "not_run"
    elif passed == len(rows):
        acceptance = "passed"
    else:
        acceptance = "failed"
    return LiveEvaluationSummary(
        suite_id=suite_id,
        suite_checksum=suite_checksum,
        results_checksum=hashlib.sha256(_result_bytes(rows)).hexdigest(),
        repetitions=repetitions,
        runner_status=runner_status,
        model_acceptance_status=acceptance,
        live_model=live_model,
        runner_detail_codes=tuple(sorted(set(runner_detail_codes))),
        trial_count=len(rows),
        passed_count=passed,
        failed_count=failed,
        blocked_count=blocked,
        not_run_count=not_run,
        provider_call_count=sum(row.provider_call_count for row in rows),
        native_tool_call_count=sum(
            row.native_tool_call_count for row in rows
        ),
        bound_tool_execution_count=sum(
            row.bound_tool_execution_count for row in rows
        ),
        input_tokens=sum(row.input_tokens for row in rows),
        output_tokens=sum(row.output_tokens for row in rows),
        provider_latency_ms=sum(row.provider_latency_ms for row in rows),
        tool_latency_ms=sum(row.tool_latency_ms for row in rows),
    )


def _markdown_report(
    summary: LiveEvaluationSummary,
    results: Sequence[LiveEvaluationResult],
    *,
    raw_response_artifact: str | None = None,
    raw_responses_sha256: str | None = None,
    raw_response_count: int | None = None,
    successful_real_call_count: int | None = None,
    failed_real_call_count: int | None = None,
    raw_parsed_binding_status: str | None = None,
    parsed_output_artifact: str | None = None,
    parsed_outputs_sha256: str | None = None,
) -> str:
    lines = [
        f"# Agent System Live Query Smoke: {summary.suite_id}",
        "",
        "## Boundary",
        "",
        summary.claim_boundary,
        "",
        "## Summary",
        "",
        f"- Runner status: `{summary.runner_status}`",
        f"- Model acceptance: `{summary.model_acceptance_status}`",
        f"- Live model: `{str(summary.live_model).lower()}`",
        f"- Provider / model: `{summary.provider}` / `{summary.model}`",
        f"- Temperature / thinking / retries: "
        f"`{summary.temperature}` / `{summary.thinking}` / "
        f"`{summary.automatic_retry_count}`",
        f"- Trials: {summary.trial_count}",
        f"- Passed / failed / blocked / not run: "
        f"{summary.passed_count} / {summary.failed_count} / "
        f"{summary.blocked_count} / {summary.not_run_count}",
        f"- Provider calls: {summary.provider_call_count}",
        f"- Native / bound tool calls: "
        f"{summary.native_tool_call_count} / "
        f"{summary.bound_tool_execution_count}",
        f"- Input / output tokens: "
        f"{summary.input_tokens} / {summary.output_tokens}",
        f"- Provider / tool latency (ms): "
        f"{summary.provider_latency_ms:.3f} / "
        f"{summary.tool_latency_ms:.3f}",
        "- Semantic Resolution: "
        f"`{summary.semantic_resolution_status}`",
        (
            "- Runner details: "
            + (
                ", ".join(
                    f"`{code}`" for code in summary.runner_detail_codes
                )
                if summary.runner_detail_codes
                else "`none`"
            )
        ),
        "",
        "## Trials",
        "",
        "| Repetition | Trial | Role | Workflow | Activation | Acceptance | Calls | Tokens |",
        "| ---: | --- | --- | --- | --- | --- | ---: | ---: |",
    ]
    for row in results:
        lines.append(
            f"| {row.repetition} | `{row.trial_id}` | `{row.role}` | "
            f"`{row.workflow_status}` | "
            f"`{row.activation_status}` | `{row.model_acceptance_status}` | "
            f"{row.provider_call_count} | "
            f"{row.input_tokens}/{row.output_tokens} |"
        )
    lines.extend(
        [
            "",
            "Temperature 0 reduces sampling variance but does not guarantee "
            "identical provider outputs.",
            "",
        ]
    )
    if parsed_output_artifact is not None:
        lines.extend(
            [
                "## Runtime artifacts",
                "",
                f"- Parsed outputs: `{parsed_output_artifact}`",
                f"- Parsed outputs SHA-256: `{parsed_outputs_sha256}`",
                f"- Raw provider responses: `{raw_response_artifact}`",
                f"- Attempted / successful / failed real calls: "
                f"{raw_response_count} / {successful_real_call_count} / "
                f"{failed_real_call_count}",
                f"- Raw / parsed binding: "
                f"`{raw_parsed_binding_status}`",
                f"- Raw responses SHA-256: `{raw_responses_sha256}`",
                "",
                "Raw provider responses and parsed outputs are gitignored; "
                "only this sanitized summary is tracked.",
                "",
            ]
        )
    return "\n".join(lines)


def write_live_evaluation_artifacts(
    *,
    output_dir: str | Path,
    report_dir: str | Path,
    results: Sequence[LiveEvaluationResult],
    summary: LiveEvaluationSummary,
    report_stem: str = DEFAULT_LIVE_EVALUATION_REPORT_STEM,
    provider_calls: Sequence[LiveEvaluationProviderCall] | None = None,
) -> tuple[Path, Path, Path, Path]:
    """Write ignored detailed rows and tracked sanitized summaries."""

    runtime = Path(output_dir)
    reports = Path(report_dir)
    runtime.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    result_path = runtime / "live_evaluation_results_v4.jsonl"
    result_bytes = _result_bytes(results)
    result_path.write_bytes(result_bytes)
    raw_path: Path | None = None
    raw_bytes: bytes | None = None
    if provider_calls is not None:
        raw_path = runtime / "raw_responses_v4.jsonl"
        raw_bytes = _provider_call_bytes(provider_calls)
        raw_path.write_bytes(raw_bytes)
    artifact_summary = {
        "parsed_output_artifact": str(result_path),
        "parsed_outputs_sha256": hashlib.sha256(result_bytes).hexdigest(),
        "raw_response_artifact": (
            str(raw_path) if raw_path is not None else None
        ),
        "raw_responses_sha256": (
            hashlib.sha256(raw_bytes).hexdigest()
            if raw_bytes is not None
            else None
        ),
        "raw_response_count": (
            len(provider_calls) if provider_calls is not None else None
        ),
        "successful_real_call_count": (
            sum(_is_successful_real_call(call) for call in provider_calls)
            if provider_calls is not None
            else None
        ),
        "failed_real_call_count": (
            sum(
                not _is_successful_real_call(call)
                for call in provider_calls
            )
            if provider_calls is not None
            else None
        ),
        "raw_parsed_binding_status": (
            (
                "valid"
                if not _provider_call_binding_failures(
                    results,
                    provider_calls,
                )
                else "invalid"
            )
            if provider_calls is not None
            else None
        ),
    }
    manifest_path = runtime / "live_evaluation_manifest_v4.json"
    manifest_path.write_text(
        summary.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    report_json = reports / f"{report_stem}.json"
    report_json.write_text(
        json.dumps(
            {
                "summary": summary.model_dump(mode="json"),
                "artifacts": artifact_summary,
                "results": [
                    row.model_dump(mode="json") for row in results
                ],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    report_markdown = reports / f"{report_stem}.md"
    report_markdown.write_text(
        _markdown_report(
            summary,
            results,
            raw_response_artifact=artifact_summary[
                "raw_response_artifact"
            ],
            raw_responses_sha256=artifact_summary[
                "raw_responses_sha256"
            ],
            raw_response_count=artifact_summary["raw_response_count"],
            successful_real_call_count=artifact_summary[
                "successful_real_call_count"
            ],
            failed_real_call_count=artifact_summary[
                "failed_real_call_count"
            ],
            raw_parsed_binding_status=artifact_summary[
                "raw_parsed_binding_status"
            ],
            parsed_output_artifact=artifact_summary[
                "parsed_output_artifact"
            ],
            parsed_outputs_sha256=artifact_summary[
                "parsed_outputs_sha256"
            ],
        ),
        encoding="utf-8",
    )
    return result_path, manifest_path, report_json, report_markdown


def _live_preflight_failures(
    config: Mapping[str, Any],
    *,
    environ: Mapping[str, str],
) -> tuple[str, ...]:
    del config
    failures: list[str] = []
    if not environ.get("DEEPSEEK_API_KEY", "").strip():
        failures.append("missing_deepseek_credentials")
    if FROZEN_PROVIDER != "deepseek":
        failures.append("provider_binding_not_frozen")
    if FROZEN_MODEL != "deepseek-v4-pro":
        failures.append("model_binding_not_frozen")
    if FROZEN_TEMPERATURE != 0.0:
        failures.append("temperature_not_zero")
    catalog = get_prompt_catalog()
    for role in ("query",):
        prompt = catalog.role(role)
        if prompt.temperature != 0.0:
            failures.append(f"{role}_temperature_not_zero")
        if prompt.thinking != "disabled":
            failures.append(f"{role}_thinking_not_disabled")
        if prompt.max_retries != 0:
            failures.append(f"{role}_retries_not_zero")
    return tuple(failures)


def _blocked_query_result(
    *,
    trial: LiveEvaluationTrial,
    repetition: int,
    failure_code: str,
    live_model: bool,
) -> LiveEvaluationResult:
    return LiveEvaluationResult(
        trial_id=trial.trial_id,
        repetition=repetition,
        kind="query",
        source_id=trial.source_id,
        role="query",
        live_model=live_model,
        workflow_status="not_run",
        activation_status="not_reached",
        model_acceptance_status="not_run",
        assertions=(
            LiveEvaluationAssertion(
                check_id="query_dependency",
                passed=False,
                detail_code=failure_code,
            ),
        ),
        failure_code=failure_code,
    )


def _not_run_trial_result(
    *,
    trial: LiveEvaluationTrial,
    repetition: int,
    failure_code: str,
) -> LiveEvaluationResult:
    """Record one trial that could not reach its real-provider execution."""

    return LiveEvaluationResult(
        trial_id=trial.trial_id,
        repetition=repetition,
        kind=trial.kind,
        source_id=trial.source_id,
        role=trial.expected_role,
        live_model=True,
        workflow_status="not_run",
        activation_status="not_reached",
        model_acceptance_status="not_run",
        assertions=(
            LiveEvaluationAssertion(
                check_id="repetition_execution",
                passed=False,
                detail_code=failure_code,
            ),
        ),
        failure_code=failure_code,
    )


def _repetition_matrix_failures(
    *,
    suite: LiveEvaluationSuite,
    repetitions: int,
    results: Sequence[LiveEvaluationResult],
) -> tuple[str, ...]:
    """Validate exact repetition-by-trial result coverage and metadata."""

    expected_trials = {trial.trial_id: trial for trial in suite.trials}
    expected_pairs = {
        (repetition, trial_id)
        for repetition in range(1, repetitions + 1)
        for trial_id in expected_trials
    }
    observed_pairs = [(row.repetition, row.trial_id) for row in results]
    observed_pair_set = set(observed_pairs)
    failures: list[str] = []
    if len(observed_pairs) != len(observed_pair_set):
        failures.append("duplicate_repetition_trial_result")
    if expected_pairs - observed_pair_set:
        failures.append("missing_repetition_trial_result")
    if observed_pair_set - expected_pairs:
        failures.append("unexpected_repetition_trial_result")
    for row in results:
        trial = expected_trials.get(row.trial_id)
        if trial is None:
            continue
        if (
            row.kind != trial.kind
            or row.source_id != trial.source_id
            or row.role != trial.expected_role
        ):
            failures.append("repetition_trial_metadata_mismatch")
            break
    return tuple(sorted(set(failures)))


def _resolve_query_event_id(
    *,
    source_id: str,
    store: AviationEvidenceStore,
) -> str | None:
    """Resolve exactly one active TMI event for a logical advisory source."""

    matches = tuple(
        event.event_id
        for event in store.list_tmi_event_publications(active_only=True)
        if event.advisory_source_id == source_id
    )
    return matches[0] if len(matches) == 1 else None


def _active_collection_candidates(
    runtime: QueryRuntime,
    *,
    source_versions: bool,
) -> tuple[str, ...]:
    index = runtime.source_index if source_versions else runtime.event_index
    if index is None:
        raise EvaluationBindingBlocked(
            (
                "source_vector_index_unavailable"
                if source_versions
                else "event_vector_index_unavailable"
            )
        )
    identity_field = (
        "source_version_id" if source_versions else "publication_id"
    )
    payload = index.collection.get(include=["metadatas"])
    candidates = {
        str(metadata[identity_field])
        for metadata in payload.get("metadatas") or ()
        if metadata is not None
        and metadata.get("active") is True
        and identity_field in metadata
    }
    if not candidates:
        raise EvaluationBindingBlocked(
            (
                "source_vector_candidates_unavailable"
                if source_versions
                else "event_vector_candidates_unavailable"
            )
        )
    return tuple(sorted(candidates))


def _selected_suite_events(
    store: AviationEvidenceStore,
    suite: LiveEvaluationSuite,
) -> dict[str, str]:
    selected: dict[str, str] = {}
    for source_id in suite.required_source_ids:
        event_id = _resolve_query_event_id(
            source_id=source_id,
            store=store,
        )
        if event_id is None:
            raise EvaluationBindingBlocked(
                "required_active_event_not_found"
            )
        selected[source_id] = event_id
    return selected


def _validation_profile_checksums(
    store: AviationEvidenceStore,
    event_ids: Sequence[str],
) -> tuple[str, ...]:
    checksums: set[str] = set()
    for event_id in event_ids:
        checksums.update(
            fact.validation_profile.profile_checksum
            for fact in store.get_event_facts(event_id)
        )
        checksums.update(
            gap.validation_profile.profile_checksum
            for gap in store.get_event_profile_gaps(event_id)
        )
        checksums.update(
            observation.profile_checksum
            for observation in store.get_event_observations(
                event_id,
                ("baseline", "active", "recovery"),
            )
        )
    return tuple(sorted(checksums))


def _bind_live_query_runtime(
    *,
    runtime: QueryRuntime,
    suite: LiveEvaluationSuite,
) -> EvaluationDataBinding:
    """Freeze the exact store and vector universe before provider calls."""

    if runtime.source_index is None:
        raise EvaluationBindingBlocked("source_vector_index_unavailable")
    if runtime.event_index is None:
        raise EvaluationBindingBlocked("event_vector_index_unavailable")
    selected = _selected_suite_events(runtime.store, suite)
    events = tuple(
        runtime.store.get_event(event_id)
        for event_id in selected.values()
    )
    if any(event is None for event in events):
        raise EvaluationBindingBlocked("required_active_event_not_found")
    selected_events = tuple(event for event in events if event is not None)
    required_source_version_ids = tuple(
        sorted(
            {
                source.source_version_id
                for event in selected_events
                for source in runtime.store.get_event_sources(event.event_id)
            }
        )
    )
    if not required_source_version_ids:
        raise EvaluationBindingBlocked("required_source_versions_unavailable")
    source_candidates = set(
        _active_collection_candidates(runtime, source_versions=True)
    )
    source_candidate_version_ids = tuple(
        sorted(source_candidates.intersection(required_source_version_ids))
    )
    required_advisory_versions = {
        event.publication_source_version_id for event in selected_events
    }
    if not required_advisory_versions <= set(source_candidate_version_ids):
        raise EvaluationBindingBlocked(
            "required_advisory_source_vector_unavailable"
        )
    event_candidate_publication_ids = _active_collection_candidates(
        runtime,
        source_versions=False,
    )
    required_event_publication_ids = tuple(
        sorted(event.publication_id for event in selected_events)
    )
    if not set(required_event_publication_ids) <= set(
        event_candidate_publication_ids
    ):
        raise EvaluationBindingBlocked(
            "required_event_vector_unavailable"
        )
    return bind_evaluation_data(
        runtime.store,
        source_index=runtime.source_index,
        event_index=runtime.event_index,
        required_source_version_ids=required_source_version_ids,
        required_event_publication_ids=required_event_publication_ids,
        source_candidate_version_ids=source_candidate_version_ids,
        event_candidate_publication_ids=event_candidate_publication_ids,
        validation_profile_checksums=_validation_profile_checksums(
            runtime.store,
            tuple(selected.values()),
        ),
    )


def _verify_live_evaluation_binding(
    binding: EvaluationDataBinding,
    runtime: QueryRuntime,
) -> None:
    if runtime.source_index is None:
        raise EvaluationBindingBlocked("source_vector_index_unavailable")
    if runtime.event_index is None:
        raise EvaluationBindingBlocked("event_vector_index_unavailable")
    verify_evaluation_data_binding(
        binding,
        runtime.store,
        source_index=runtime.source_index,
        event_index=runtime.event_index,
        validation_profile_checksums=binding.validation_profile_checksums,
    )


def _run_live_evaluation_repetition(
    *,
    suite: LiveEvaluationSuite,
    runtime: QueryRuntime,
    binding: EvaluationDataBinding,
    runtime_root: Path,
    repetition: int,
    provider_calls: list[LiveEvaluationProviderCall] | None = None,
) -> tuple[tuple[LiveEvaluationResult, ...], tuple[str, ...]]:
    """Execute one real-provider repetition against the frozen live store."""

    repetition_root = (
        runtime_root
        if suite.repetitions == 1
        else runtime_root / "repetitions" / f"{repetition:03d}"
    )
    results: list[LiveEvaluationResult] = []
    runner_detail_codes: list[str] = []
    for trial in suite.trials:
        trial_provider_calls: list[LiveEvaluationProviderCall] = []
        try:
            _verify_live_evaluation_binding(binding, runtime)
            event_id = _resolve_query_event_id(
                source_id=trial.source_id,
                store=runtime.store,
            )
            if event_id is None:
                results.append(
                    _blocked_query_result(
                        trial=trial,
                        repetition=repetition,
                        failure_code="query_dependency_event_not_found",
                        live_model=True,
                    )
                )
                continue
            def _observe(
                phase: ToolPhase,
                record: ModelCallRecord,
                native_response: dict[str, Any] | None,
            ) -> None:
                if provider_calls is None:
                    return
                observed = LiveEvaluationProviderCall.from_model_call(
                    suite_id=suite.suite_id,
                    repetition=repetition,
                    trial=trial,
                    phase=phase,
                    record=record,
                    native_response=native_response,
                )
                trial_provider_calls.append(observed)
                provider_calls.append(observed)

            with capture_tool_model_calls(_observe):
                outcome = answer_question(
                    runtime=runtime,
                    question=trial.question,
                    scope=HybridQueryScope(event_id=event_id),
                    model_factory=lambda tools: make_live_tool_calling_model(
                        tools=tools,
                        role="query",
                    ),
                )
            query_run = build_hybrid_query_run_artifact(
                trial=trial,
                event_id=event_id,
                outcome=outcome,
            )
            query_run_path = write_hybrid_query_run_artifact(
                repetition_root / "hybrid_query_runs" / trial.trial_id,
                query_run,
            )
            result = score_query_trial(
                trial=trial,
                repetition=repetition,
                live_model=True,
                event_id=event_id,
                outcome=outcome,
                query_run=query_run,
                query_run_artifact_path=query_run_path,
            )
            results.append(
                result.model_copy(
                    update={
                        "provider_call_ids": tuple(
                            call.call_id for call in trial_provider_calls
                        )
                    }
                )
            )
        except EvaluationBindingBlocked as exc:
            runner_detail_codes.append(exc.detail_code)
            result = _not_run_trial_result(
                trial=trial,
                repetition=repetition,
                failure_code="evaluation_binding_changed",
            )
            results.append(
                result.model_copy(
                    update={
                        "provider_call_ids": tuple(
                            call.call_id for call in trial_provider_calls
                        ),
                        "provider_call_count": len(
                            trial_provider_calls
                        ),
                    }
                )
            )
        except (OSError, RuntimeError, TypeError, ValueError):
            runner_detail_codes.append(
                f"repetition_{repetition:03d}_{trial.trial_id}_runner_exception"
            )
            result = _not_run_trial_result(
                trial=trial,
                repetition=repetition,
                failure_code="evaluation_trial_not_executed",
            )
            results.append(
                result.model_copy(
                    update={
                        "activation_status": (
                            "activated"
                            if trial_provider_calls
                            else "not_reached"
                        ),
                        "provider_call_ids": tuple(
                            call.call_id for call in trial_provider_calls
                        ),
                        "provider_call_count": len(
                            trial_provider_calls
                        ),
                        "input_tokens": sum(
                            call.input_tokens
                            for call in trial_provider_calls
                        ),
                        "output_tokens": sum(
                            call.output_tokens
                            for call in trial_provider_calls
                        ),
                        "provider_latency_ms": sum(
                            call.latency_ms
                            for call in trial_provider_calls
                        ),
                    }
                )
            )
    return tuple(results), tuple(runner_detail_codes)


def run_live_agent_evaluation(
    *,
    config_path: str | Path,
    suite_path: str | Path,
    store_dir: str | Path | None,
    output_dir: str | Path,
    report_dir: str | Path,
    allow_live_model: bool,
    repetitions: int,
) -> LiveEvaluationSummary:
    """Run the fixed real-model smoke; never accepts a model/executor override."""

    if not allow_live_model:
        raise LiveEvaluationAuthorizationError(
            "live evaluation requires --allow-live-model"
        )
    suite_file = Path(suite_path)
    suite = load_live_evaluation_suite(suite_file)
    if repetitions != suite.repetitions:
        raise ValueError(
            "requested repetitions differ from the versioned suite"
        )
    config = load_yaml(config_path)
    load_environment()
    failures = _live_preflight_failures(config, environ=os.environ)
    suite_checksum = hashlib.sha256(suite_file.read_bytes()).hexdigest()
    runtime: QueryRuntime | None = None
    binding: EvaluationDataBinding | None = None
    if not failures:
        try:
            runtime = open_query_runtime(
                config,
                store_dir=store_dir,
                allow_model_download=False,
            )
            binding = _bind_live_query_runtime(
                runtime=runtime,
                suite=suite,
            )
            _verify_live_evaluation_binding(binding, runtime)
        except EvaluationBindingBlocked as exc:
            failures = (exc.detail_code,)
        except (OSError, RuntimeError, TypeError, ValueError):
            failures = ("query_runtime_preflight_failed",)
    if failures:
        summary = summarize_live_evaluation(
            suite_id=suite.suite_id,
            suite_checksum=suite_checksum,
            repetitions=repetitions,
            results=(),
            runner_status="blocked_before_run",
            live_model=True,
            runner_detail_codes=failures,
        )
        write_live_evaluation_artifacts(
            output_dir=output_dir,
            report_dir=report_dir,
            results=(),
            summary=summary,
            report_stem=suite.report_stem,
            provider_calls=(),
        )
        if runtime is not None:
            runtime.store.close()
        return summary
    assert runtime is not None
    assert binding is not None
    runtime_root = Path(output_dir)
    shutil.rmtree(runtime_root, ignore_errors=True)
    runtime_root.mkdir(parents=True, exist_ok=True)
    (runtime_root / "evaluation_data_binding.json").write_text(
        binding.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    results: list[LiveEvaluationResult] = []
    provider_calls: list[LiveEvaluationProviderCall] = []
    runner_detail_codes: list[str] = []
    for repetition in range(1, repetitions + 1):
        repetition_results, repetition_details = (
            _run_live_evaluation_repetition(
                suite=suite,
                runtime=runtime,
                binding=binding,
                runtime_root=runtime_root,
                repetition=repetition,
                provider_calls=provider_calls,
            )
        )
        results.extend(repetition_results)
        runner_detail_codes.extend(repetition_details)
    try:
        verify_evaluation_revision_unchanged(binding, runtime.store)
    except EvaluationBindingBlocked as exc:
        runner_detail_codes.append(exc.detail_code)
    runner_detail_codes.extend(
        _repetition_matrix_failures(
            suite=suite,
            repetitions=repetitions,
            results=results,
        )
    )
    runner_detail_codes.extend(
        _provider_call_binding_failures(results, provider_calls)
    )
    summary = summarize_live_evaluation(
        suite_id=suite.suite_id,
        suite_checksum=suite_checksum,
        repetitions=repetitions,
        results=results,
        runner_status=(
            "runner_failed" if runner_detail_codes else "completed"
        ),
        live_model=True,
        runner_detail_codes=runner_detail_codes,
    )
    write_live_evaluation_artifacts(
        output_dir=runtime_root,
        report_dir=report_dir,
        results=results,
        summary=summary,
        report_stem=suite.report_stem,
        provider_calls=provider_calls,
    )
    runtime.store.close()
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    """Run the explicit frozen live smoke from the command line."""

    parser = argparse.ArgumentParser(
        description="Run the frozen DeepSeek Query Agent smoke evaluation."
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--store-dir")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--allow-live-model", action="store_true")
    parser.add_argument("--repetitions", type=int, default=1)
    args = parser.parse_args(argv)
    try:
        summary = run_live_agent_evaluation(
            config_path=args.config,
            suite_path=args.suite,
            store_dir=args.store_dir,
            output_dir=args.output_dir,
            report_dir=args.report_dir,
            allow_live_model=args.allow_live_model,
            repetitions=args.repetitions,
        )
    except (LiveEvaluationAuthorizationError, ValueError) as exc:
        parser.error(str(exc))
    print(
        "Query Agent smoke: "
        f"runner={summary.runner_status}, "
        f"acceptance={summary.model_acceptance_status}, "
        f"trials={summary.trial_count}, "
        f"provider_calls={summary.provider_call_count}"
    )
    return (
        0
        if summary.runner_status == "completed"
        and summary.model_acceptance_status == "passed"
        else 1
    )


__all__ = [
    "HybridQueryRunArtifact",
    "HybridQueryRunStatement",
    "HybridQueryRunSupport",
    "HybridQueryRunTool",
    "LiveEvaluationAssertion",
    "LiveEvaluationAuthorizationError",
    "LiveEvaluationResult",
    "LiveEvaluationProviderCall",
    "LiveEvaluationSummary",
    "LiveEvaluationSuite",
    "LiveEvaluationTrial",
    "build_hybrid_query_run_artifact",
    "load_live_evaluation_suite",
    "main",
    "run_live_agent_evaluation",
    "score_query_trial",
    "summarize_live_evaluation",
    "write_hybrid_query_run_artifact",
    "write_live_evaluation_artifacts",
]


if __name__ == "__main__":
    raise SystemExit(main())
