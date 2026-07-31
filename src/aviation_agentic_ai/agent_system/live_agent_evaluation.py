"""Explicit real-model smoke evaluation for the bounded TMI Query Agent."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Any, Literal, Mapping, Sequence

import yaml
from pydantic import Field, model_validator

from aviation_agentic_ai.agent_system.audit import sanitize_text
from aviation_agentic_ai.agent_system.authority_evidence import (
    AuthorityBuildStatus,
)
from aviation_agentic_ai.agent_system.contracts import (
    ModelCallRecord,
    QueryToolOutcome,
    StrictModel,
)
from aviation_agentic_ai.agent_system.corpus_batch import build_corpus_batch
from aviation_agentic_ai.agent_system.corpus_batch import (
    BatchResources,
    load_batch_resources,
)
from aviation_agentic_ai.agent_system.corpus_query import (
    answer_corpus_question,
)
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusBuildResult,
    CorpusQueryStore,
)
from aviation_agentic_ai.agent_system.hybrid_query_agent import (
    MAX_QUERY_PROVIDER_TURNS,
    MAX_QUERY_TOOL_CALLS,
    validate_hybrid_query_statement,
)
from aviation_agentic_ai.agent_system.prompts import get_prompt_catalog
from aviation_agentic_ai.agent_system.runtime import (
    FROZEN_MODEL,
    FROZEN_PROVIDER,
    FROZEN_TEMPERATURE,
)
from aviation_agentic_ai.agent_system.tool_model import (
    make_live_tool_calling_model,
)
from aviation_agentic_ai.config import (
    load_environment,
    load_yaml,
    resolve_project_path,
)


REQUIRED_LIVE_SOURCE_KEYS = (
    "atcscc_advisories",
    "stationinfo",
    "metar",
    "taf",
    "nasr_zip",
    "nasr_manifest",
    "pilot_controller_glossary",
    "term_seed",
    "bts_on_time_manifest",
    "bts_on_time_snapshot",
)
HYBRID_QUERY_READ_TOOLS = frozenset(
    {
        "find_tmi_events",
        "read_tmi_event_facts",
        "read_weather_context",
        "read_public_observations",
        "read_tmi_event_graph",
        "rank_tmi_events_by_metadata",
    }
)


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
    def build_source_ids(self) -> tuple[str, ...]:
        """All sources needed to build the self-contained smoke corpus."""

        return tuple(sorted({trial.source_id for trial in self.trials}))


class LiveEvaluationAssertion(StrictModel):
    """One bounded, payload-free acceptance check."""

    check_id: str = Field(min_length=1)
    passed: bool
    detail_code: str = Field(min_length=1)


class HybridQueryRunStatement(StrictModel):
    """One sanitized answer statement and its typed citation verdicts."""

    kind: Literal[
        "source_fact",
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
    citation_valid: bool
    claim_boundary_valid: bool
    validation_error: str = ""


class HybridQueryRunSupport(StrictModel):
    """One sanitized evidence-kind and source binding used for validation."""

    kind: Literal[
        "source_fact",
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


class HybridQueryRunTool(StrictModel):
    """One sanitized read-only tool trace retained by the evaluator."""

    name: str = Field(min_length=1)
    status: Literal["ok", "insufficient", "blocked"]
    reference_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()


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
    """Aggregate smoke outcome, separate from canonical corpus identity."""

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
) -> str:
    lines = [
        "# Agent System Query Agent Smoke v4",
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
    return "\n".join(lines)


def write_live_evaluation_artifacts(
    *,
    output_dir: str | Path,
    report_dir: str | Path,
    results: Sequence[LiveEvaluationResult],
    summary: LiveEvaluationSummary,
) -> tuple[Path, Path, Path, Path]:
    """Write ignored detailed rows and tracked sanitized summaries."""

    runtime = Path(output_dir)
    reports = Path(report_dir)
    runtime.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    result_path = runtime / "live_evaluation_results_v4.jsonl"
    result_path.write_bytes(_result_bytes(results))
    manifest_path = runtime / "live_evaluation_manifest_v4.json"
    manifest_path.write_text(
        summary.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    report_json = reports / "agent_system_live_agent_smoke_v4.json"
    report_json.write_text(
        json.dumps(
            {
                "summary": summary.model_dump(mode="json"),
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
    report_markdown = reports / "agent_system_live_agent_smoke_v4.md"
    report_markdown.write_text(
        _markdown_report(summary, results),
        encoding="utf-8",
    )
    return result_path, manifest_path, report_json, report_markdown


def _live_preflight_failures(
    config: Mapping[str, Any],
    *,
    environ: Mapping[str, str],
) -> tuple[str, ...]:
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
    sources = config.get("sources")
    if not isinstance(sources, Mapping):
        failures.append("missing_sources_mapping")
        return tuple(failures)
    for key in REQUIRED_LIVE_SOURCE_KEYS:
        value = sources.get(key)
        if not isinstance(value, (str, Path)) or not str(value):
            failures.append(f"missing_source_config:{key}")
            continue
        if not resolve_project_path(value).is_file():
            failures.append(f"missing_source_file:{key}")
    return tuple(failures)


def _resource_preflight_failures(
    resources: BatchResources,
) -> tuple[str, ...]:
    failures: list[str] = []
    if resources.authority_catalog.facility.status is not AuthorityBuildStatus.OK:
        failures.append("facility_authority_snapshot_not_ready")
    if (
        resources.authority_catalog.terminology.status
        is not AuthorityBuildStatus.OK
    ):
        failures.append("terminology_authority_snapshot_not_ready")
    if resources.weather_failure_reason:
        failures.append("weather_snapshot_not_ready")
    if resources.bts_failure_reason:
        failures.append("bts_snapshot_not_ready")
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
    build_results: Mapping[str, CorpusBuildResult],
    store: CorpusQueryStore,
) -> str | None:
    result = build_results.get(source_id)
    if result is not None and result.event_id and store.get_event(result.event_id):
        return result.event_id
    matches = [
        event.event_id
        for event in store.events
        if event.advisory_source_id == source_id
    ]
    return matches[0] if len(matches) == 1 else None


def _run_live_evaluation_repetition(
    *,
    config: Mapping[str, Any],
    suite: LiveEvaluationSuite,
    resources: BatchResources,
    runtime_root: Path,
    repetition: int,
) -> tuple[LiveEvaluationResult, ...]:
    """Execute one isolated real-provider repetition of the versioned suite."""

    repetition_root = (
        runtime_root
        if suite.repetitions == 1
        else runtime_root / "repetitions" / f"{repetition:03d}"
    )
    corpus_dir = repetition_root / "corpus"

    batch = build_corpus_batch(
        config,
        corpus_dir,
        selection="cohort",
        source_ids=suite.build_source_ids,
        allow_live_model=False,
        resume=False,
        resource_loader=lambda _config: resources,
    )
    build_results = {row.source_id: row for row in batch.results}
    store = (
        CorpusQueryStore(corpus_dir)
        if (corpus_dir / "corpus_manifest.json").is_file()
        else None
    )
    results: list[LiveEvaluationResult] = []
    for trial in suite.trials:
        if store is None:
            results.append(
                _blocked_query_result(
                    trial=trial,
                    repetition=repetition,
                    failure_code="query_dependency_corpus_not_published",
                    live_model=True,
                )
            )
            continue
        event_id = _resolve_query_event_id(
            source_id=trial.source_id,
            build_results=build_results,
            store=store,
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
        outcome = answer_corpus_question(
            corpus_dir=corpus_dir,
            question=trial.question,
            event_id=event_id,
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
        results.append(
            score_query_trial(
                trial=trial,
                repetition=repetition,
                live_model=True,
                event_id=event_id,
                outcome=outcome,
                query_run=query_run,
                query_run_artifact_path=query_run_path,
            )
        )
    return tuple(results)


def run_live_agent_evaluation(
    *,
    config_path: str | Path,
    suite_path: str | Path,
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
    resources: BatchResources | None = None
    if not failures:
        try:
            resources = load_batch_resources(config)
        except (OSError, RuntimeError, TypeError, ValueError):
            failures = ("resource_preflight_failed",)
        else:
            failures = _resource_preflight_failures(resources)
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
        )
        return summary
    assert resources is not None
    runtime_root = Path(output_dir)
    shutil.rmtree(runtime_root, ignore_errors=True)
    results: list[LiveEvaluationResult] = []
    runner_detail_codes: list[str] = []
    for repetition in range(1, repetitions + 1):
        try:
            results.extend(
                _run_live_evaluation_repetition(
                    config=config,
                    suite=suite,
                    resources=resources,
                    runtime_root=runtime_root,
                    repetition=repetition,
                )
            )
        except (OSError, RuntimeError, TypeError, ValueError):
            runner_detail_codes.append(
                f"repetition_{repetition:03d}_runner_exception"
            )
            results.extend(
                _not_run_trial_result(
                    trial=trial,
                    repetition=repetition,
                    failure_code="evaluation_repetition_not_executed",
                )
                for trial in suite.trials
            )
    runner_detail_codes.extend(
        _repetition_matrix_failures(
            suite=suite,
            repetitions=repetitions,
            results=results,
        )
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
    )
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    """Run the explicit frozen live smoke from the command line."""

    parser = argparse.ArgumentParser(
        description="Run the frozen DeepSeek Query Agent smoke evaluation."
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--allow-live-model", action="store_true")
    parser.add_argument("--repetitions", type=int, default=1)
    args = parser.parse_args(argv)
    try:
        summary = run_live_agent_evaluation(
            config_path=args.config,
            suite_path=args.suite,
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
