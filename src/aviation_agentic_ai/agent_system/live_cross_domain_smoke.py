"""Real-provider cross-domain HybridRAG smoke evaluation.

The suite is deliberately user-facing: every trial starts from an unscoped
natural-language question and therefore exercises the Query Agent's routing
stage before any evidence tool is available.
"""

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
import yaml
from pydantic import Field, model_validator

from aviation_agentic_ai.agent_system.audit import sanitize_text
from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryScope,
    ModelCallRecord,
    QueryToolOutcome,
    StrictModel,
)
from aviation_agentic_ai.agent_system.hybrid_query_agent import (
    validate_hybrid_query_statement,
)
from aviation_agentic_ai.agent_system.knowledge_query import answer_question
from aviation_agentic_ai.agent_system.prompts import get_prompt_catalog
from aviation_agentic_ai.agent_system.query_runtime import open_query_runtime
from aviation_agentic_ai.agent_system.query_tool_registry import (
    QueryToolFamily,
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


CrossDomainCategory = Literal[
    "tmi",
    "flight",
    "weather",
    "sector",
    "cross_domain",
    "insufficient",
]


class CrossDomainSmokeTrial(StrictModel):
    """One ordinary-user question in the cross-domain live smoke."""

    trial_id: str = Field(min_length=1)
    category: CrossDomainCategory
    question: str = Field(min_length=1)
    required_families: tuple[QueryToolFamily, ...] = Field(min_length=1)
    required_tool_names: tuple[str, ...] = ()
    required_support_kinds: tuple[str, ...] = ()
    required_event_ids: tuple[str, ...] = ()
    required_flight_ids: tuple[str, ...] = ()
    required_answer_terms: tuple[str, ...] = ()
    expected_status: Literal["ok", "insufficient"]
    scope: dict[str, object] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _require_public_unscoped_question(self) -> CrossDomainSmokeTrial:
        if self.scope:
            raise ValueError("cross-domain smoke questions must be unscoped")
        if not self.question.strip().endswith("?"):
            raise ValueError("cross-domain smoke questions must be questions")
        return self


class CrossDomainSmokeSuite(StrictModel):
    """Frozen six-category compatibility suite for the live HybridRAG path."""

    version: Literal["live-hybridrag-cross-domain-v1"]
    suite_id: str = Field(min_length=1)
    mode: Literal["live_smoke"] = "live_smoke"
    provider: Literal["deepseek"] = "deepseek"
    model: Literal["deepseek-v4-flash"] = "deepseek-v4-flash"
    temperature: Literal[0.0] = 0.0
    thinking: Literal["disabled"] = "disabled"
    automatic_retry_count: Literal[0] = 0
    trials: tuple[CrossDomainSmokeTrial, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _require_frozen_category_matrix(self) -> CrossDomainSmokeSuite:
        expected: set[str] = {
            "tmi",
            "flight",
            "weather",
            "sector",
            "cross_domain",
            "insufficient",
        }
        categories = [trial.category for trial in self.trials]
        if len(categories) != len(set(categories)):
            raise ValueError("cross-domain smoke categories must be unique")
        if set(categories) != expected:
            raise ValueError("cross-domain smoke must contain all six categories")
        trial_ids = [trial.trial_id for trial in self.trials]
        if len(trial_ids) != len(set(trial_ids)):
            raise ValueError("cross-domain smoke trial IDs must be unique")
        return self


def load_cross_domain_smoke_suite(
    path: str | Path,
) -> CrossDomainSmokeSuite:
    """Load and validate the tracked real-provider cross-domain suite."""

    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("cross-domain smoke suite must be a mapping")
    return CrossDomainSmokeSuite.model_validate(payload)


class LiveCrossDomainSmokeAuthorizationError(RuntimeError):
    """Raised before any artifact write when live execution is not authorized."""


class CrossDomainProviderCall(StrictModel):
    """One native provider turn stored only in the ignored runtime directory."""

    call_id: str = Field(min_length=1)
    trial_id: str = Field(min_length=1)
    recorded_at: str = Field(min_length=1)
    phase: str = Field(min_length=1)
    role: str = Field(min_length=1)
    provider: str | None = None
    model: str | None = None
    prompt_set_id: str | None = None
    prompt_version: str | None = None
    temperature: float | None = None
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    latency_ms: float = Field(default=0.0, ge=0.0)
    error: str | None = None
    raw_response: str = ""
    native_response: dict[str, Any] | None = None
    response_sha256: str = Field(min_length=64, max_length=64)

    @property
    def returned(self) -> bool:
        return self.native_response is not None

    @property
    def successful(self) -> bool:
        return (
            self.returned
            and self.error is None
            and self.provider == FROZEN_PROVIDER
            and self.model == FROZEN_MODEL
            and self.temperature == FROZEN_TEMPERATURE
        )


class CrossDomainTrialResult(StrictModel):
    """Payload-free acceptance result for one natural-language trial."""

    trial_id: str = Field(min_length=1)
    category: CrossDomainCategory
    expected_status: Literal["ok", "insufficient"]
    workflow_status: Literal["ok", "insufficient", "blocked", "not_run"]
    selected_families: tuple[QueryToolFamily, ...] = ()
    tool_names: tuple[str, ...] = ()
    statement_count: int = Field(default=0, ge=0)
    routing_passed: bool
    retrieval_passed: bool
    grounding_passed: bool
    answer_acceptance_passed: bool
    live_calls_passed: bool = True
    accepted: bool
    provider_call_ids: tuple[str, ...] = ()
    failure_codes: tuple[str, ...] = ()


class CrossDomainSmokeSummary(StrictModel):
    """Sanitized report that keeps model and task success distinct."""

    manifest_version: Literal["live-hybridrag-cross-domain-report-v1"] = (
        "live-hybridrag-cross-domain-report-v1"
    )
    suite_id: str = Field(min_length=1)
    suite_checksum: str = Field(min_length=64, max_length=64)
    mode: Literal["live_smoke"] = "live_smoke"
    runner_status: Literal["completed", "blocked_before_run", "runner_failed"]
    provider: Literal["deepseek"] = "deepseek"
    model: Literal["deepseek-v4-flash"] = "deepseek-v4-flash"
    prompt_versions: tuple[str, ...] = ()
    temperature: Literal[0.0] = 0.0
    thinking: Literal["disabled"] = "disabled"
    automatic_retry_count: Literal[0] = 0
    dataset_id: str | None = None
    knowledge_revision: int | None = Field(default=None, ge=0)
    trial_count: int = Field(ge=0)
    accepted_trial_count: int = Field(ge=0)
    routing_pass_count: int = Field(ge=0)
    retrieval_pass_count: int = Field(ge=0)
    grounding_pass_count: int = Field(ge=0)
    answer_acceptance_pass_count: int = Field(ge=0)
    live_call_binding_pass_count: int = Field(ge=0)
    attempted_real_calls: int = Field(ge=0)
    returned_real_calls: int = Field(ge=0)
    successful_real_calls: int = Field(ge=0)
    failed_real_calls: int = Field(ge=0)
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    provider_latency_ms: float = Field(ge=0.0)
    raw_response_artifact: str | None = None
    raw_response_sha256: str | None = Field(default=None, min_length=64, max_length=64)
    parsed_output_artifact: str | None = None
    parsed_output_sha256: str | None = Field(default=None, min_length=64, max_length=64)
    artifact_integrity: Literal["verified", "failed", "not_written"]
    detail_codes: tuple[str, ...] = ()
    results: tuple[CrossDomainTrialResult, ...] = ()
    claim_boundary: str = (
        "Six-task real-provider compatibility smoke over the current persistent "
        "HybridRAG runtime; this is not a statistical benchmark, causal study, "
        "or decision-recommendation evaluation."
    )


def score_cross_domain_trial(
    *,
    trial: CrossDomainSmokeTrial,
    outcome: QueryToolOutcome,
    provider_calls: Sequence[CrossDomainProviderCall] = (),
    require_live_calls: bool = False,
) -> CrossDomainTrialResult:
    """Score routing, retrieval, grounding, and answer acceptance separately."""

    trace = outcome.route_trace
    selected = (
        tuple(QueryToolFamily(value) for value in trace.selected_families)
        if trace is not None
        else ()
    )
    routing_passed = bool(
        trace is not None
        and trace.status == "selected"
        and set(trial.required_families).issubset(selected)
    )
    observed_tool_names = {call.tool for call in outcome.tool_calls}
    observed_support_kinds = {record.kind for record in outcome.support_records}
    retrieved_event_ids = {
        value
        for record in outcome.support_records
        for value in record.event_ids
    }
    retrieved_flight_ids = {
        value
        for record in outcome.support_records
        for value in record.flight_ids
    }
    retrieval_passed = bool(outcome.tool_calls) and all(
        call.status != "blocked" for call in outcome.tool_calls
    ) and set(trial.required_tool_names).issubset(observed_tool_names)
    retrieval_passed = retrieval_passed and set(
        trial.required_support_kinds
    ).issubset(observed_support_kinds)
    retrieval_passed = retrieval_passed and set(
        trial.required_event_ids
    ).issubset(retrieved_event_ids)
    retrieval_passed = retrieval_passed and set(
        trial.required_flight_ids
    ).issubset(retrieved_flight_ids)
    validation_errors = [
        error
        for statement in outcome.answer_statements
        if (
            error := validate_hybrid_query_statement(
                statement,
                outcome.support_records,
            )
        )
    ]
    grounding_passed = bool(
        outcome.status != "blocked"
        and not validation_errors
        and (
            bool(outcome.answer_statements)
            if outcome.status == "ok"
            else not outcome.answer_statements
        )
    )
    cited_event_ids = {
        value
        for statement in outcome.answer_statements
        for value in statement.support_event_ids
    }
    cited_flight_ids = {
        value
        for statement in outcome.answer_statements
        for value in statement.support_flight_ids
    }
    normalized_answer = outcome.answer.casefold()
    answer_passed = (
        outcome.status == trial.expected_status
        and set(trial.required_event_ids).issubset(cited_event_ids)
        and set(trial.required_flight_ids).issubset(cited_flight_ids)
        and all(term.casefold() in normalized_answer for term in trial.required_answer_terms)
    )
    successful_roles = {
        call.role for call in provider_calls if call.successful
    }
    live_calls_passed = (
        not require_live_calls
        or {"query_router", "query"}.issubset(successful_roles)
    )
    failures: list[str] = []
    if not routing_passed:
        failures.append("routing_family_mismatch")
    if not retrieval_passed:
        failures.append("retrieval_not_completed")
    if not grounding_passed:
        failures.append("grounding_or_claim_boundary_failed")
    if not answer_passed:
        failures.append("answer_status_mismatch")
    if not live_calls_passed:
        failures.append("required_live_provider_roles_missing")
    accepted = not failures
    return CrossDomainTrialResult(
        trial_id=trial.trial_id,
        category=trial.category,
        expected_status=trial.expected_status,
        workflow_status=outcome.status,
        selected_families=selected,
        tool_names=tuple(call.tool for call in outcome.tool_calls),
        statement_count=len(outcome.answer_statements),
        routing_passed=routing_passed,
        retrieval_passed=retrieval_passed,
        grounding_passed=grounding_passed,
        answer_acceptance_passed=answer_passed,
        live_calls_passed=live_calls_passed,
        accepted=accepted,
        failure_codes=tuple(failures),
    )


def build_sanitized_query_output(outcome: QueryToolOutcome) -> dict[str, Any]:
    """Return parsed evidence structure without provider or tool payloads."""

    return {
        "status": outcome.status,
        "answer": outcome.answer,
        "route_trace": (
            outcome.route_trace.model_dump(mode="json")
            if outcome.route_trace is not None
            else None
        ),
        "tools": [
            {
                "name": trace.tool,
                "status": trace.status,
                "result_refs": trace.result_refs,
            }
            for trace in outcome.tool_calls
        ],
        "statements": [
            statement.model_dump(mode="json")
            for statement in outcome.answer_statements
        ],
        "support_records": [
            record.model_dump(mode="json") for record in outcome.support_records
        ],
        "failure_code": (
            "query_blocked" if outcome.status == "blocked" else ""
        ),
        "failure_reason": (
            sanitize_text(outcome.failure_reason)
            if outcome.status == "blocked"
            else ""
        ),
    }


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _jsonl_bytes(rows: Sequence[dict[str, Any]]) -> bytes:
    if not rows:
        return b""
    return ("\n".join(_canonical_json(row) for row in rows) + "\n").encode(
        "utf-8"
    )


def _observed_call(
    *,
    suite_id: str,
    trial_id: str,
    ordinal: int,
    phase: ToolPhase,
    record: ModelCallRecord,
    native_response: dict[str, Any] | None,
) -> CrossDomainProviderCall:
    response_sha = hashlib.sha256(
        _canonical_json(
            {"native_response": native_response, "error": record.error}
        ).encode("utf-8")
    ).hexdigest()
    call_id = "provider-call:" + hashlib.sha256(
        f"{suite_id}|{trial_id}|{ordinal}|{response_sha}".encode("utf-8")
    ).hexdigest()[:24]
    return CrossDomainProviderCall(
        call_id=call_id,
        trial_id=trial_id,
        recorded_at=datetime.now(UTC).isoformat(),
        phase=phase,
        role=record.agent,
        provider=record.provider,
        model=record.model,
        prompt_set_id=record.prompt_set_id,
        prompt_version=record.prompt_version,
        temperature=record.temperature,
        input_tokens=record.input_tokens,
        output_tokens=record.output_tokens,
        latency_ms=record.latency_ms,
        error=record.error,
        raw_response=record.raw_response,
        native_response=native_response,
        response_sha256=response_sha,
    )


def _preflight_failures() -> tuple[str, ...]:
    failures: list[str] = []
    if not os.environ.get("DEEPSEEK_API_KEY", "").strip():
        failures.append("missing_deepseek_credentials")
    if (FROZEN_PROVIDER, FROZEN_MODEL, FROZEN_TEMPERATURE) != (
        "deepseek",
        "deepseek-v4-flash",
        0.0,
    ):
        failures.append("frozen_model_configuration_changed")
    catalog = get_prompt_catalog()
    for role_name in ("query_router", "query"):
        role = catalog.role(role_name)
        if role.temperature != 0.0:
            failures.append(f"{role_name}_temperature_not_zero")
        if role.thinking != "disabled":
            failures.append(f"{role_name}_thinking_not_disabled")
        if role.max_retries != 0:
            failures.append(f"{role_name}_automatic_retry_enabled")
    return tuple(failures)


def _summary(
    *,
    suite: CrossDomainSmokeSuite,
    suite_checksum: str,
    runner_status: Literal["completed", "blocked_before_run", "runner_failed"],
    results: Sequence[CrossDomainTrialResult],
    calls: Sequence[CrossDomainProviderCall],
    dataset_id: str | None,
    knowledge_revision: int | None,
    raw_path: Path | None,
    parsed_path: Path | None,
    artifact_integrity: Literal["verified", "failed", "not_written"] = "not_written",
    detail_codes: Sequence[str] = (),
) -> CrossDomainSmokeSummary:
    raw_sha = hashlib.sha256(raw_path.read_bytes()).hexdigest() if raw_path else None
    parsed_sha = (
        hashlib.sha256(parsed_path.read_bytes()).hexdigest()
        if parsed_path
        else None
    )
    return CrossDomainSmokeSummary(
        suite_id=suite.suite_id,
        suite_checksum=suite_checksum,
        runner_status=runner_status,
        prompt_versions=tuple(
            sorted({call.prompt_version for call in calls if call.prompt_version})
        ),
        dataset_id=dataset_id,
        knowledge_revision=knowledge_revision,
        trial_count=len(results),
        accepted_trial_count=sum(row.accepted for row in results),
        routing_pass_count=sum(row.routing_passed for row in results),
        retrieval_pass_count=sum(row.retrieval_passed for row in results),
        grounding_pass_count=sum(row.grounding_passed for row in results),
        answer_acceptance_pass_count=sum(
            row.answer_acceptance_passed for row in results
        ),
        live_call_binding_pass_count=sum(row.live_calls_passed for row in results),
        attempted_real_calls=len(calls),
        returned_real_calls=sum(call.returned for call in calls),
        successful_real_calls=sum(call.successful for call in calls),
        failed_real_calls=sum(not call.successful for call in calls),
        input_tokens=sum(call.input_tokens for call in calls),
        output_tokens=sum(call.output_tokens for call in calls),
        provider_latency_ms=sum(call.latency_ms for call in calls),
        raw_response_artifact=str(raw_path) if raw_path else None,
        raw_response_sha256=raw_sha,
        parsed_output_artifact=str(parsed_path) if parsed_path else None,
        parsed_output_sha256=parsed_sha,
        artifact_integrity=artifact_integrity,
        detail_codes=tuple(detail_codes),
        results=tuple(results),
    )


def _markdown(summary: CrossDomainSmokeSummary) -> str:
    lines = [
        "# Cross-Domain HybridRAG Live Smoke v1",
        "",
        f"- Mode: `{summary.mode}`",
        f"- Runner: `{summary.runner_status}`",
        f"- Provider / model: `{summary.provider}` / `{summary.model}`",
        f"- Prompt versions: `{', '.join(summary.prompt_versions)}`",
        f"- Temperature / thinking / retries: `{summary.temperature}` / "
        f"`{summary.thinking}` / `{summary.automatic_retry_count}`",
        f"- Dataset / knowledge revision: `{summary.dataset_id}` / "
        f"`{summary.knowledge_revision}`",
        f"- Trials accepted: {summary.accepted_trial_count}/{summary.trial_count}",
        f"- Routing / retrieval / grounding / answer acceptance: "
        f"{summary.routing_pass_count}/{summary.trial_count} / "
        f"{summary.retrieval_pass_count}/{summary.trial_count} / "
        f"{summary.grounding_pass_count}/{summary.trial_count} / "
        f"{summary.answer_acceptance_pass_count}/{summary.trial_count}",
        f"- Trial/provider binding: {summary.live_call_binding_pass_count}/"
        f"{summary.trial_count}",
        f"- Real calls attempted / successful / failed: "
        f"{summary.attempted_real_calls} / {summary.successful_real_calls} / "
        f"{summary.failed_real_calls}",
        f"- Tokens input / output: {summary.input_tokens} / {summary.output_tokens}",
        f"- Raw provider artifact: `{summary.raw_response_artifact}`",
        f"- Raw SHA-256: `{summary.raw_response_sha256}`",
        f"- Parsed output artifact: `{summary.parsed_output_artifact}`",
        f"- Parsed SHA-256: `{summary.parsed_output_sha256}`",
        f"- Artifact integrity: `{summary.artifact_integrity}`",
        "",
        "| Category | Status | Route | Retrieval | Grounding | Answer | Accepted |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for result in summary.results:
        lines.append(
            f"| {result.category} | {result.workflow_status} | "
            f"{int(result.routing_passed)} | {int(result.retrieval_passed)} | "
            f"{int(result.grounding_passed)} | "
            f"{int(result.answer_acceptance_passed)} | {int(result.accepted)} |"
        )
    lines.extend(
        [
            "",
            "This is a real-provider compatibility smoke, not a statistical "
            "benchmark. Weather links remain temporal/non-causal, TMI "
            "applicability remains a candidate relation, and no result proves "
            "optimality or supports an operational recommendation.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_reports(
    *,
    report_dir: Path,
    summary: CrossDomainSmokeSummary,
) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    stem = "live_hybridrag_cross_domain_v1"
    (report_dir / f"{stem}.json").write_text(
        summary.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    (report_dir / f"{stem}.md").write_text(
        _markdown(summary),
        encoding="utf-8",
    )


def run_live_cross_domain_smoke(
    *,
    config_path: str | Path,
    suite_path: str | Path,
    store_dir: str | Path,
    output_dir: str | Path,
    report_dir: str | Path,
    allow_live_model: bool,
) -> CrossDomainSmokeSummary:
    """Run the six natural-language tasks against the configured real provider."""

    if not allow_live_model:
        raise LiveCrossDomainSmokeAuthorizationError(
            "cross-domain live smoke requires --allow-live-model"
        )
    suite_file = Path(suite_path)
    suite = load_cross_domain_smoke_suite(suite_file)
    suite_checksum = hashlib.sha256(suite_file.read_bytes()).hexdigest()
    load_environment()
    failures = _preflight_failures()
    if failures:
        summary = _summary(
            suite=suite,
            suite_checksum=suite_checksum,
            runner_status="blocked_before_run",
            results=(),
            calls=(),
            dataset_id=None,
            knowledge_revision=None,
            raw_path=None,
            parsed_path=None,
            detail_codes=failures,
        )
        _write_reports(report_dir=Path(report_dir), summary=summary)
        return summary

    config = load_yaml(config_path)
    runtime = open_query_runtime(
        config,
        store_dir=store_dir,
        allow_model_download=False,
    )
    runtime_root = Path(output_dir)
    store_root = Path(store_dir).resolve()
    resolved_runtime_root = runtime_root.resolve()
    if (
        resolved_runtime_root == store_root
        or store_root.is_relative_to(resolved_runtime_root)
    ):
        runtime.store.close()
        raise ValueError("live smoke output directory cannot contain the store")
    shutil.rmtree(runtime_root, ignore_errors=True)
    runtime_root.mkdir(parents=True, exist_ok=True)
    set_llm_cache(None)
    if get_llm_cache() is not None:
        runtime.store.close()
        summary = _summary(
            suite=suite,
            suite_checksum=suite_checksum,
            runner_status="blocked_before_run",
            results=(),
            calls=(),
            dataset_id=runtime.store.dataset_id,
            knowledge_revision=None,
            raw_path=None,
            parsed_path=None,
            detail_codes=("langchain_cache_not_disabled",),
        )
        _write_reports(report_dir=Path(report_dir), summary=summary)
        return summary

    calls: list[CrossDomainProviderCall] = []
    results: list[CrossDomainTrialResult] = []
    parsed_rows: list[dict[str, Any]] = []
    runner_details: list[str] = []
    knowledge_revision = runtime.store.get_knowledge_revision()
    dataset_id = runtime.store.dataset_id
    for trial in suite.trials:
        trial_calls: list[CrossDomainProviderCall] = []

        def observe(
            phase: ToolPhase,
            record: ModelCallRecord,
            native_response: dict[str, Any] | None,
        ) -> None:
            call = _observed_call(
                suite_id=suite.suite_id,
                trial_id=trial.trial_id,
                ordinal=len(trial_calls) + 1,
                phase=phase,
                record=record,
                native_response=native_response,
            )
            trial_calls.append(call)
            calls.append(call)

        try:
            with capture_tool_model_calls(observe):
                outcome = answer_question(
                    runtime=runtime,
                    question=trial.question,
                    scope=HybridQueryScope.model_validate(trial.scope),
                    model_factory=lambda tools: make_live_tool_calling_model(
                        tools=tools,
                        role=query_tool_model_role(tools),
                    ),
                )
            result = score_cross_domain_trial(
                trial=trial,
                outcome=outcome,
                provider_calls=trial_calls,
                require_live_calls=True,
            )
            result = result.model_copy(
                update={
                    "provider_call_ids": tuple(call.call_id for call in trial_calls)
                }
            )
            parsed_rows.append(
                {
                    "suite_id": suite.suite_id,
                    "trial_id": trial.trial_id,
                    "category": trial.category,
                    "provider_call_ids": [call.call_id for call in trial_calls],
                    "query_outcome": build_sanitized_query_output(outcome),
                }
            )
        except Exception as exc:  # preserve an observed provider/runtime failure
            runner_details.append(
                f"{trial.trial_id}:{type(exc).__name__}"
            )
            result = CrossDomainTrialResult(
                trial_id=trial.trial_id,
                category=trial.category,
                expected_status=trial.expected_status,
                workflow_status="not_run",
                routing_passed=False,
                retrieval_passed=False,
                grounding_passed=False,
                answer_acceptance_passed=False,
                accepted=False,
                provider_call_ids=tuple(call.call_id for call in trial_calls),
                failure_codes=("trial_runner_exception",),
            )
            parsed_rows.append(
                {
                    "suite_id": suite.suite_id,
                    "trial_id": trial.trial_id,
                    "category": trial.category,
                    "provider_call_ids": [call.call_id for call in trial_calls],
                    "query_outcome": None,
                    "runner_error": f"{type(exc).__name__}: {exc}",
                }
            )
        results.append(result)

    raw_path = runtime_root / "raw_provider_responses.jsonl"
    parsed_path = runtime_root / "parsed_trial_outputs.jsonl"
    raw_path.write_bytes(
        _jsonl_bytes([call.model_dump(mode="json") for call in calls])
    )
    parsed_path.write_bytes(_jsonl_bytes(parsed_rows))
    referenced = [
        call_id for result in results for call_id in result.provider_call_ids
    ]
    call_ids = [call.call_id for call in calls]
    binding_verified = (
        sorted(referenced) == sorted(call_ids)
        and len(call_ids) == len(set(call_ids))
    )
    if not binding_verified:
        runner_details.append("provider_call_binding_failed")
    if runtime.store.get_knowledge_revision() != knowledge_revision:
        runner_details.append("knowledge_revision_changed_during_smoke")
    artifact_integrity: Literal["verified", "failed"] = (
        "verified" if binding_verified else "failed"
    )
    summary = _summary(
        suite=suite,
        suite_checksum=suite_checksum,
        runner_status="runner_failed" if runner_details else "completed",
        results=results,
        calls=calls,
        dataset_id=dataset_id,
        knowledge_revision=knowledge_revision,
        raw_path=raw_path,
        parsed_path=parsed_path,
        artifact_integrity=artifact_integrity,
        detail_codes=runner_details,
    )
    _write_reports(report_dir=Path(report_dir), summary=summary)
    runtime.store.close()
    return summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the real DeepSeek cross-domain HybridRAG smoke."
    )
    parser.add_argument("--config", required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--store-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--allow-live-model", action="store_true")
    args = parser.parse_args(argv)
    try:
        summary = run_live_cross_domain_smoke(
            config_path=args.config,
            suite_path=args.suite,
            store_dir=args.store_dir,
            output_dir=args.output_dir,
            report_dir=args.report_dir,
            allow_live_model=args.allow_live_model,
        )
    except LiveCrossDomainSmokeAuthorizationError as exc:
        parser.error(str(exc))
    print(
        "Cross-domain HybridRAG smoke: "
        f"runner={summary.runner_status}, "
        f"accepted={summary.accepted_trial_count}/{summary.trial_count}, "
        f"real_calls={summary.successful_real_calls}/"
        f"{summary.attempted_real_calls}"
    )
    return 0 if summary.runner_status == "completed" else 1


__all__ = [
    "CrossDomainProviderCall",
    "CrossDomainSmokeSuite",
    "CrossDomainSmokeSummary",
    "CrossDomainSmokeTrial",
    "CrossDomainTrialResult",
    "LiveCrossDomainSmokeAuthorizationError",
    "build_sanitized_query_output",
    "load_cross_domain_smoke_suite",
    "main",
    "run_live_cross_domain_smoke",
    "score_cross_domain_trial",
]


if __name__ == "__main__":
    raise SystemExit(main())
