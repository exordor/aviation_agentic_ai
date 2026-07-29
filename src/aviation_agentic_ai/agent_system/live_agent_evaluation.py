"""Explicit real-model smoke evaluation for bounded decision-case Agents."""

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

from aviation_agentic_ai.agent_system.agent_usage import AgentUsageRecord
from aviation_agentic_ai.agent_system.authority_evidence import (
    AuthorityBuildStatus,
)
from aviation_agentic_ai.agent_system.case_analysis import (
    MAX_CASE_ANALYSIS_BOUND_STEPS,
    MAX_CASE_ANALYSIS_MODEL_CALLS,
)
from aviation_agentic_ai.agent_system.case_assembly import (
    MAX_ASSEMBLY_PROVIDER_TURNS,
    MAX_ASSEMBLY_TOOL_CALLS,
)
from aviation_agentic_ai.agent_system.contracts import (
    ModelCallRecord,
    QueryToolOutcome,
    StrictModel,
)
from aviation_agentic_ai.agent_system.corpus_batch import build_corpus_batch
from aviation_agentic_ai.agent_system.corpus_batch import (
    BatchCaseExecution,
    BatchResources,
    load_batch_resources,
    run_batch_case,
)
from aviation_agentic_ai.agent_system.corpus_query import (
    answer_corpus_question,
)
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusBuildResult,
    CorpusQueryStore,
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
FORBIDDEN_OPERATIONAL_OR_CAUSAL_PREDICATES = frozenset(
    {
        "https://data.nasa.gov/ontologies/atmonto/data#arrivalDemand",
        "https://data.nasa.gov/ontologies/atmonto/data#airportArrivalRate",
        "urn:aviation-agentic-ai:causedBy",
        "urn:aviation-agentic-ai:motivatedBy",
        "urn:aviation-agentic-ai:affectedBy",
    }
)


class LiveEvaluationAuthorizationError(RuntimeError):
    """Raised before any write when live execution was not authorized."""


class LiveEvaluationTrial(StrictModel):
    """One frozen Assembly or Analysis trial."""

    trial_id: str = Field(min_length=1)
    kind: Literal["assembly", "analysis"]
    source_id: str = Field(min_length=1)
    expected_role: Literal[
        "decision_case_assembly",
        "decision_case_analysis",
    ]
    question: str | None = None
    forbidden_predicate_iris: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _validate_kind(self) -> "LiveEvaluationTrial":
        if self.kind == "analysis" and not self.question:
            raise ValueError("analysis trial requires question")
        if self.kind == "assembly" and self.question is not None:
            raise ValueError("assembly trial does not accept question")
        expected = {
            "assembly": "decision_case_assembly",
            "analysis": "decision_case_analysis",
        }[self.kind]
        if self.expected_role != expected:
            raise ValueError("trial kind and expected_role disagree")
        return self


class LiveEvaluationSuite(StrictModel):
    """Frozen smoke-evaluation manifest."""

    version: Literal["live-agent-smoke-v1"]
    suite_id: str = Field(min_length=1)
    repetitions: int = Field(default=1, ge=1)
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


class LiveEvaluationResult(StrictModel):
    """One sanitized live or offline trial result."""

    trial_id: str = Field(min_length=1)
    repetition: int = Field(ge=1)
    kind: Literal["assembly", "analysis"]
    source_id: str = Field(min_length=1)
    event_id: str | None = None
    role: Literal[
        "decision_case_assembly",
        "decision_case_analysis",
    ]
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
    failure_code: str = ""


class LiveEvaluationSummary(StrictModel):
    """Aggregate smoke outcome, separate from canonical corpus identity."""

    manifest_version: Literal["decision-case-live-evaluation-v1"] = (
        "decision-case-live-evaluation-v1"
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
        "Single-run provider compatibility and bounded-behavior smoke only; "
        "not a benchmark, statistical reliability result, or Semantic "
        "Resolution evaluation."
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


def _assembly_failure_code(
    *,
    build_result: CorpusBuildResult,
    calls: Sequence[ModelCallRecord],
) -> str:
    reason = build_result.reason.lower()
    if "output-token cap exceeded" in reason:
        return "assembly_output_token_cap_exceeded"
    if "malformed case assembly proposal output" in reason:
        return "assembly_malformed_contract_output"
    if any(call.error for call in calls):
        return "assembly_provider_or_model_call_error"
    if build_result.status == "blocked":
        return "assembly_execution_blocked"
    return "assembly_acceptance_failed"


def score_assembly_trial(
    *,
    trial: LiveEvaluationTrial,
    repetition: int,
    live_model: bool,
    build_result: CorpusBuildResult,
    usage: AgentUsageRecord,
    model_calls: Sequence[ModelCallRecord],
    fact_predicate_iris: Sequence[str],
    context_causal_claims: Sequence[bool],
    observation_profile_layers: Sequence[str],
) -> LiveEvaluationResult:
    """Score one real Assembly execution without retaining model payloads."""

    calls = tuple(
        call
        for call in model_calls
        if call.agent == "decision_case_assembly"
    )
    native_tool_count = sum(len(call.tool_calls) for call in calls)
    forbidden = {
        *trial.forbidden_predicate_iris,
        *FORBIDDEN_OPERATIONAL_OR_CAUSAL_PREDICATES,
    }
    assertions = (
        _assertion(
            "agent_activated",
            usage.execution_mode == "activated" and bool(calls),
            passed_code="activated_with_real_provider_calls",
            failed_code="assembly_agent_not_activated",
        ),
        _assertion(
            "bounded_execution",
            1 <= len(calls) <= MAX_ASSEMBLY_PROVIDER_TURNS
            and native_tool_count <= MAX_ASSEMBLY_TOOL_CALLS,
            passed_code="within_existing_model_and_tool_budgets",
            failed_code="assembly_budget_not_satisfied",
        ),
        _assertion(
            "frozen_model_contract",
            _model_configuration_ok(
                calls,
                role="decision_case_assembly",
            ),
            passed_code="frozen_deepseek_configuration_observed",
            failed_code="model_configuration_or_provider_call_failed",
        ),
        _assertion(
            "publishable_partial_case",
            build_result.status == "ok"
            and bool(build_result.event_id)
            and usage.outcome == "accepted"
            and usage.detail_status == "partial",
            passed_code="partial_case_passed_formal_publication",
            failed_code="partial_case_not_published",
        ),
        _assertion(
            "missing_reason_not_invented",
            not forbidden.intersection(fact_predicate_iris),
            passed_code="forbidden_reason_predicates_absent",
            failed_code="forbidden_reason_predicate_published",
        ),
        _assertion(
            "context_remains_noncausal",
            not any(context_causal_claims),
            passed_code="all_context_associations_noncausal",
            failed_code="causal_context_association_observed",
        ),
        _assertion(
            "public_observation_role_preserved",
            all(
                layer == "public_operational_observation"
                for layer in observation_profile_layers
            ),
            passed_code="all_bts_facts_use_public_observation_profile",
            failed_code="bts_fact_escaped_public_observation_profile",
        ),
    )
    blocked = build_result.status == "blocked"
    if blocked:
        acceptance: Literal["passed", "failed", "blocked", "not_run"] = (
            "blocked"
        )
    elif all(assertion.passed for assertion in assertions):
        acceptance = "passed"
    else:
        acceptance = "failed"
    activation = (
        "activated"
        if usage.execution_mode == "activated"
        else (
            "not_reached"
            if usage.execution_mode == "not_reached"
            else "not_activated"
        )
    )
    return LiveEvaluationResult(
        trial_id=trial.trial_id,
        repetition=repetition,
        kind="assembly",
        source_id=trial.source_id,
        event_id=build_result.event_id or usage.event_id,
        role="decision_case_assembly",
        live_model=live_model,
        workflow_status=build_result.status,
        activation_status=activation,
        model_acceptance_status=acceptance,
        detail_status=usage.detail_status,
        assertions=assertions,
        bound_tool_execution_count=0,
        tool_latency_ms=usage.tool_latency_ms,
        failure_code=(
            ""
            if acceptance == "passed"
            else _assembly_failure_code(
                build_result=build_result,
                calls=calls,
            )
        ),
        **_shared_model_metadata(calls),
    )


def _analysis_artifacts_present(path: str | None) -> bool:
    if not path:
        return False
    root = Path(path)
    return all(
        (root / name).is_file()
        for name in (
            "case_analysis_task.json",
            "query_evidence_bundle.json",
            "case_analysis_run.json",
        )
    )


def score_analysis_trial(
    *,
    trial: LiveEvaluationTrial,
    repetition: int,
    live_model: bool,
    event_id: str,
    outcome: QueryToolOutcome,
) -> LiveEvaluationResult:
    """Score one real Analysis execution over its sealed evidence bundle."""

    calls = tuple(
        call
        for call in outcome.model_calls
        if call.agent == "decision_case_analysis"
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
            failed_code="analysis_agent_not_activated",
        ),
        _assertion(
            "bounded_execution",
            1 <= len(calls) <= MAX_CASE_ANALYSIS_MODEL_CALLS
            and len(outcome.tool_calls) <= MAX_CASE_ANALYSIS_BOUND_STEPS,
            passed_code="within_existing_model_and_tool_budgets",
            failed_code="analysis_budget_not_satisfied",
        ),
        _assertion(
            "frozen_model_contract",
            _model_configuration_ok(
                calls,
                role="decision_case_analysis",
            ),
            passed_code="frozen_deepseek_configuration_observed",
            failed_code="model_configuration_or_provider_call_failed",
        ),
        _assertion(
            "read_only_registered_tools",
            all(
                name == "execute_bound_query_step"
                for name in (*native_tools, *bound_tools)
            ),
            passed_code="only_registered_bound_read_tool_observed",
            failed_code="unregistered_or_write_tool_observed",
        ),
        _assertion(
            "evidence_bundle_support",
            outcome.status == "ok"
            and bool(outcome.retrieved_fact_ids)
            and bool(outcome.source_ids)
            and _analysis_artifacts_present(
                outcome.analysis_artifact_dir
            ),
            passed_code="sealed_supported_evidence_bundle_persisted",
            failed_code="supported_evidence_bundle_not_observed",
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
        kind="analysis",
        source_id=trial.source_id,
        event_id=event_id,
        role="decision_case_analysis",
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
        failure_code=(
            ""
            if acceptance == "passed"
            else (
                "analysis_provider_or_model_call_error"
                if acceptance == "blocked"
                else (
                    "analysis_answer_contract_or_support_failed"
                    if outcome.status == "blocked"
                    else "analysis_acceptance_failed"
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
        "# Agent System Live Agent Smoke v1",
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
        "| Trial | Role | Workflow | Activation | Acceptance | Calls | Tokens |",
        "| --- | --- | --- | --- | --- | ---: | ---: |",
    ]
    for row in results:
        lines.append(
            f"| `{row.trial_id}` | `{row.role}` | `{row.workflow_status}` | "
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
    result_path = runtime / "live_evaluation_results.jsonl"
    result_path.write_bytes(_result_bytes(results))
    manifest_path = runtime / "live_evaluation_manifest.json"
    manifest_path.write_text(
        summary.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    report_json = reports / "agent_system_live_agent_smoke_v1.json"
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
    report_markdown = reports / "agent_system_live_agent_smoke_v1.md"
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
    for role in ("decision_case_assembly", "decision_case_analysis"):
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


def _blocked_analysis_result(
    *,
    trial: LiveEvaluationTrial,
    repetition: int,
    failure_code: str,
    live_model: bool,
) -> LiveEvaluationResult:
    return LiveEvaluationResult(
        trial_id=trial.trial_id,
        repetition=repetition,
        kind="analysis",
        source_id=trial.source_id,
        role="decision_case_analysis",
        live_model=live_model,
        workflow_status="not_run",
        activation_status="not_reached",
        model_acceptance_status="not_run",
        assertions=(
            LiveEvaluationAssertion(
                check_id="analysis_dependency",
                passed=False,
                detail_code=failure_code,
            ),
        ),
        failure_code=failure_code,
    )


def _assembly_usage_from_execution(
    execution: BatchCaseExecution | None,
    *,
    source_id: str,
) -> AgentUsageRecord:
    if execution is not None:
        for row in execution.agent_usage_records:
            if (
                row.role == "decision_case_assembly"
                and row.task_scope == "decision_case"
            ):
                return row
    return AgentUsageRecord(
        source_id=source_id,
        event_id=None,
        task_id=f"live-evaluation:not-reached:{source_id}",
        role="decision_case_assembly",
        task_scope="decision_case",
        execution_mode="not_reached",
        outcome="blocked",
        detail_status="workflow_exception",
        activation_reason="execution_not_returned_to_recording_runner",
    )


def _score_assembly_results(
    *,
    suite: LiveEvaluationSuite,
    repetition: int,
    build_results: Mapping[str, CorpusBuildResult],
    executions: Mapping[str, BatchCaseExecution],
    store: CorpusQueryStore | None,
) -> list[LiveEvaluationResult]:
    scored: list[LiveEvaluationResult] = []
    for trial in suite.trials:
        if trial.kind != "assembly":
            continue
        build_result = build_results.get(
            trial.source_id,
            CorpusBuildResult(
                source_id=trial.source_id,
                status="blocked",
                reason="missing batch result",
            ),
        )
        execution = executions.get(trial.source_id)
        usage = _assembly_usage_from_execution(
            execution,
            source_id=trial.source_id,
        )
        facts = (
            store.get_event_facts(build_result.event_id)
            if store is not None and build_result.event_id
            else ()
        )
        context = (
            store.get_decision_context(build_result.event_id)
            if store is not None and build_result.event_id
            else ()
        )
        observations = (
            store.get_outcome_observations(build_result.event_id)
            if store is not None and build_result.event_id
            else ()
        )
        facts_by_id = {fact.fact_id: fact for fact in facts}
        observation_layers = tuple(
            facts_by_id[fact_id].validation_profile.layer
            for observation in observations
            for fact_id in observation.fact_ids
            if fact_id in facts_by_id
        )
        scored.append(
            score_assembly_trial(
                trial=trial,
                repetition=repetition,
                live_model=True,
                build_result=build_result,
                usage=usage,
                model_calls=(
                    execution.model_calls if execution is not None else ()
                ),
                fact_predicate_iris=tuple(
                    fact.predicate_iri for fact in facts
                ),
                context_causal_claims=tuple(
                    row.causal_claim for row in context
                ),
                observation_profile_layers=observation_layers,
            )
        )
    return scored


def _resolve_analysis_event_id(
    *,
    source_id: str,
    build_results: Mapping[str, CorpusBuildResult],
    store: CorpusQueryStore,
) -> str | None:
    result = build_results.get(source_id)
    if result is not None and result.event_id and store.get_case(result.event_id):
        return result.event_id
    matches = [
        case.event_id
        for case in store.cases
        if case.advisory_source_id == source_id
    ]
    return matches[0] if len(matches) == 1 else None


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
            "requested repetitions differ from the frozen suite"
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
    corpus_dir = runtime_root / "corpus"
    shutil.rmtree(runtime_root, ignore_errors=True)
    executions: dict[str, BatchCaseExecution] = {}

    def recording_runner(
        advisory: Any,
        shared_resources: BatchResources,
        staging_dir: Path,
        authorized: bool,
    ) -> BatchCaseExecution:
        execution = run_batch_case(
            advisory,
            shared_resources,
            staging_dir,
            authorized,
        )
        executions[advisory.source_id] = execution
        return execution

    results: list[LiveEvaluationResult] = []
    try:
        batch = build_corpus_batch(
            config,
            corpus_dir,
            selection="cohort",
            source_ids=suite.build_source_ids,
            allow_live_model=True,
            resume=False,
            resource_loader=lambda _config: resources,
            case_runner=recording_runner,
        )
        build_results = {
            row.source_id: row for row in batch.results
        }
        store = (
            CorpusQueryStore(corpus_dir)
            if (corpus_dir / "corpus_manifest.json").is_file()
            else None
        )
        results.extend(
            _score_assembly_results(
                suite=suite,
                repetition=1,
                build_results=build_results,
                executions=executions,
                store=store,
            )
        )
        analysis_trials = [
            trial for trial in suite.trials if trial.kind == "analysis"
        ]
        for trial in analysis_trials:
            if store is None:
                results.append(
                    _blocked_analysis_result(
                        trial=trial,
                        repetition=1,
                        failure_code="analysis_dependency_corpus_not_published",
                        live_model=True,
                    )
                )
                continue
            event_id = _resolve_analysis_event_id(
                source_id=trial.source_id,
                build_results=build_results,
                store=store,
            )
            if event_id is None:
                results.append(
                    _blocked_analysis_result(
                        trial=trial,
                        repetition=1,
                        failure_code="analysis_dependency_event_not_found",
                        live_model=True,
                    )
                )
                continue
            assert trial.question is not None
            outcome = answer_corpus_question(
                corpus_dir=corpus_dir,
                question=trial.question,
                event_id=event_id,
                allow_live_model=True,
                model_factory=lambda tools: make_live_tool_calling_model(
                    tools=tools,
                    role="decision_case_analysis",
                ),
            )
            results.append(
                score_analysis_trial(
                    trial=trial,
                    repetition=1,
                    live_model=True,
                    event_id=event_id,
                    outcome=outcome,
                )
            )
        summary = summarize_live_evaluation(
            suite_id=suite.suite_id,
            suite_checksum=suite_checksum,
            repetitions=repetitions,
            results=results,
            runner_status="completed",
            live_model=True,
        )
    except (OSError, RuntimeError, TypeError, ValueError):
        summary = summarize_live_evaluation(
            suite_id=suite.suite_id,
            suite_checksum=suite_checksum,
            repetitions=repetitions,
            results=results,
            runner_status="runner_failed",
            live_model=True,
            runner_detail_codes=("evaluation_runner_exception",),
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
        description="Run the frozen DeepSeek bounded-Agent smoke evaluation."
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
        "Live Agent smoke: "
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
    "LiveEvaluationAssertion",
    "LiveEvaluationAuthorizationError",
    "LiveEvaluationResult",
    "LiveEvaluationSummary",
    "LiveEvaluationSuite",
    "LiveEvaluationTrial",
    "load_live_evaluation_suite",
    "main",
    "run_live_agent_evaluation",
    "score_analysis_trial",
    "score_assembly_trial",
    "summarize_live_evaluation",
    "write_live_evaluation_artifacts",
]


if __name__ == "__main__":
    raise SystemExit(main())
