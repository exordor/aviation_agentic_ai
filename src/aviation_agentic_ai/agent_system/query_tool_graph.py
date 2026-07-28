"""Deterministic bounded reads for registered decision-record questions."""

from __future__ import annotations

import json
import re
import time
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from langchain_core.tools import BaseTool

from aviation_agentic_ai.agent_system.audit import (
    sanitize_json_value,
    sanitize_text,
)
from aviation_agentic_ai.agent_system.case_analysis import (
    run_case_analysis_agent,
    write_case_analysis_artifacts,
)
from aviation_agentic_ai.agent_system.case_analysis_tools import BoundQueryGateway
from aviation_agentic_ai.agent_system.contracts import (
    QueryToolOutcome,
    QueryToolTrace,
)
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    ContractExecutionBinding,
)
from aviation_agentic_ai.agent_system.prompts import (
    DEFAULT_PROMPT_CATALOG,
    get_prompt_catalog,
)
from aviation_agentic_ai.agent_system.query import ontology_labels_for
from aviation_agentic_ai.agent_system.query_context_store import QueryContextStore
from aviation_agentic_ai.agent_system.query_plan import (
    AnalysisIntent,
    compile_query_plan,
)
from aviation_agentic_ai.agent_system.query_tools import (
    QueryGraphStore,
    QueryPredicate,
    QueryToolError,
    QueryToolGateway,
    QueryToolResult,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.tool_model import ToolCallingModel

REGISTERED_COMPETENCY_QUESTION = (
    "What traffic management measure, controlled airport, and effective time "
    "are recorded in this advisory?"
)
MEASURE_QUESTION = "What traffic management measure was published?"
CONTROLLED_FACILITY_QUESTION = "Which airport was controlled?"
OPERATIONAL_PERIOD_QUESTION = "When did the measure apply?"
DECLARED_REASON_QUESTION = "What reason did the advisory state?"
PROVENANCE_QUESTION = "Which source supports this decision record?"
FORECAST_CONTEXT_QUESTION = "What forecast was known at decision time?"
OBSERVED_WEATHER_CONTEXT_QUESTION = "What observed weather context was available?"
PUBLIC_OUTCOME_QUESTION = (
    "What BTS-reported public operational observations are recorded?"
)
RECONSTRUCTED_CASE_QUESTION = "Reconstruct this decision case."
EPISODE_ANALYSIS_QUESTION = "What decision episode is recorded?"
OPERATIONAL_SITUATION_ANALYSIS_QUESTION = (
    "What public operational situation is recorded?"
)
APPLICABILITY_ANALYSIS_QUESTION = (
    "What applicability and observed flight impact are recorded?"
)
HISTORICAL_SIMILARITY_ANALYSIS_QUESTION = (
    "Which historical case is most similar?"
)
RECONSTRUCTION_EVIDENCE_PATH_QUESTION = (
    "Which weather reports and active-window BTS public observations "
    "belong to this reconstructed decision case?"
)


class QueryIntent(str, Enum):
    COMBINED_RECORD = "combined_record"
    MEASURE = "measure"
    CONTROLLED_FACILITY = "controlled_facility"
    OPERATIONAL_PERIOD = "operational_period"
    DECLARED_REASON = "declared_reason"
    PROVENANCE = "provenance"
    FORECAST_CONTEXT = "forecast_context"
    OBSERVED_WEATHER_CONTEXT = "observed_weather_context"
    PUBLIC_OUTCOME = "public_outcome"
    RECONSTRUCTED_CASE = "reconstructed_case"
    RECONSTRUCTION_EVIDENCE_PATHS = "reconstruction_evidence_paths"


ToolModelFactory = Callable[[list[BaseTool]], ToolCallingModel]


def _normalize_question(question: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", question.lower()))


def _passes_capability_gate(question: str) -> bool:
    """Reject non-English and safety-sensitive wording before intent lookup."""

    if not question.isascii():
        return False
    normalized = _normalize_question(question)
    words = set(normalized.split())
    if not normalized:
        return False
    if words.intersection({"live", "current", "now", "today", "realtime"}):
        return False
    if "real time" in normalized:
        return False
    if (
        any(word.startswith("caus") for word in words)
        or words.intersection({"because", "why"})
        or any(
            phrase in normalized
            for phrase in (
                "result in",
                "resulted in",
                "results in",
                "resulting in",
            )
        )
    ):
        return False
    if "flight" in words and any(word.startswith("control") for word in words):
        return False
    return True


def classify_registered_question(
    question: str,
) -> QueryIntent | AnalysisIntent | None:
    """Map only an exact registered English question to one bounded intent."""

    if not _passes_capability_gate(question):
        return None
    normalized = _normalize_question(question)
    exact: dict[str, QueryIntent | AnalysisIntent] = {
        _normalize_question(REGISTERED_COMPETENCY_QUESTION): QueryIntent.COMBINED_RECORD,
        _normalize_question(MEASURE_QUESTION): QueryIntent.MEASURE,
        _normalize_question(CONTROLLED_FACILITY_QUESTION): QueryIntent.CONTROLLED_FACILITY,
        _normalize_question(OPERATIONAL_PERIOD_QUESTION): QueryIntent.OPERATIONAL_PERIOD,
        _normalize_question(DECLARED_REASON_QUESTION): QueryIntent.DECLARED_REASON,
        _normalize_question(PROVENANCE_QUESTION): QueryIntent.PROVENANCE,
        _normalize_question(FORECAST_CONTEXT_QUESTION): QueryIntent.FORECAST_CONTEXT,
        _normalize_question(
            OBSERVED_WEATHER_CONTEXT_QUESTION
        ): QueryIntent.OBSERVED_WEATHER_CONTEXT,
        _normalize_question(PUBLIC_OUTCOME_QUESTION): QueryIntent.PUBLIC_OUTCOME,
        _normalize_question(RECONSTRUCTED_CASE_QUESTION): QueryIntent.RECONSTRUCTED_CASE,
        _normalize_question(
            RECONSTRUCTION_EVIDENCE_PATH_QUESTION
        ): QueryIntent.RECONSTRUCTION_EVIDENCE_PATHS,
        _normalize_question(EPISODE_ANALYSIS_QUESTION): AnalysisIntent.EPISODE,
        _normalize_question(
            OPERATIONAL_SITUATION_ANALYSIS_QUESTION
        ): AnalysisIntent.OPERATIONAL_SITUATION,
        _normalize_question(
            APPLICABILITY_ANALYSIS_QUESTION
        ): AnalysisIntent.APPLICABILITY_AND_IMPACT,
        _normalize_question(
            HISTORICAL_SIMILARITY_ANALYSIS_QUESTION
        ): AnalysisIntent.HISTORICAL_SIMILARITY,
    }
    return exact.get(normalized)


def is_registered_competency_question(question: str) -> bool:
    """Return whether the bounded Query Agent explicitly supports the question."""

    return classify_registered_question(question) is not None


def _deterministic_similarity_outcome(
    *,
    run_dir: Path,
    question: str,
    store: QueryGraphStore,
) -> QueryToolOutcome:
    """Execute the closed corpus gate without constructing a model."""

    plan = compile_query_plan(
        run_dir=run_dir,
        question=question,
        store=store,
    )
    gateway = BoundQueryGateway(plan=plan, store=store)
    observation = gateway.execute_bound_query_step(
        step_id=plan.steps[0].step_id,
    )
    status = "blocked" if observation.status == "blocked" else "insufficient"
    limitation = observation.limitation or "Insufficient graph evidence."
    return QueryToolOutcome(
        status=status,
        answer=limitation,
        failure_reason=limitation if status == "blocked" else "",
    )


def _analysis_outcome(
    *,
    run_dir: Path,
    question: str,
    intent: AnalysisIntent,
    store: QueryGraphStore,
    model_factory: ToolModelFactory,
) -> QueryToolOutcome:
    """Run one exact analysis route or its deterministic corpus gate."""

    if intent is AnalysisIntent.HISTORICAL_SIMILARITY:
        return _deterministic_similarity_outcome(
            run_dir=run_dir,
            question=question,
            store=store,
        )
    plan = compile_query_plan(
        run_dir=run_dir,
        question=question,
        store=store,
    )
    role = get_prompt_catalog(DEFAULT_PROMPT_CATALOG).role(
        "decision_case_analysis"
    )
    binding = ContractExecutionBinding(
        run_id=str(store.manifest["run_id"]),
        created_at=datetime.now(UTC),
        prompt_version=role.prompt_version,
    )
    task, bundle, outcome = run_case_analysis_agent(
        plan=plan,
        gateway=BoundQueryGateway(plan=plan, store=store),
        model_factory=model_factory,
        binding=binding,
    )
    artifact_dir = write_case_analysis_artifacts(
        run_dir=run_dir,
        task=task,
        bundle=bundle,
        outcome=outcome,
    )
    return outcome.model_copy(
        update={"analysis_artifact_dir": str(artifact_dir)}
    )


def _expected_fixed_answer(
    *,
    rows: list[dict[str, Any]],
    ontology_labels: dict[str, str],
) -> tuple[dict[str, str], str]:
    by_predicate = {
        str(row["predicate"]): row
        for row in rows
    }
    type_value = str(by_predicate[QueryPredicate.EVENT_TYPE]["object"])
    measure_label = ontology_labels.get(type_value, type_value).strip()
    measure = measure_label.split("(", 1)[0].strip()
    facility_value = str(
        by_predicate[QueryPredicate.CONTROLLED_NAS_ELEMENT]["object"]
    )
    airport = facility_value.rsplit(":", 1)[-1].rsplit("/", 1)[-1]
    start = str(by_predicate[QueryPredicate.EFFECTIVE_START]["object"])
    end = str(by_predicate[QueryPredicate.EFFECTIVE_END]["object"])
    expected = {
        "MEASURE": measure_label,
        "AIRPORT": airport,
        "START": start,
        "END": end,
    }
    rendered = (
        f"The graph records a {measure} controlling {airport} "
        f"from {start} to {end}."
    )
    return expected, rendered


def _write_query_tool_run(
    *,
    run_dir: Path,
    question: str,
    outcome: QueryToolOutcome,
    event_ids: list[str],
    allowed_predicates: list[str],
    ontology_labels: dict[str, str],
    retrieved_facts: list[dict[str, Any]],
    retrieved_profile_gaps: list[dict[str, Any]] | None = None,
    retrieved_context_associations: list[dict[str, Any]] | None = None,
    retrieved_outcome_summaries: list[dict[str, Any]] | None = None,
    retrieved_outcome_observations: list[dict[str, Any]] | None = None,
) -> None:
    payload = {
        "execution": "deterministic_bound_read",
        "status": outcome.status,
        "question": question,
        "registered_event_ids": event_ids,
        "allowed_predicates": allowed_predicates,
        "ontology_labels": ontology_labels,
        "retrieved_fact_ids": outcome.retrieved_fact_ids,
        "retrieved_profile_gap_ids": outcome.retrieved_profile_gap_ids,
        "retrieved_context_association_ids": (
            outcome.retrieved_context_association_ids
        ),
        "retrieved_outcome_summary_ids": outcome.retrieved_outcome_summary_ids,
        "retrieved_observation_ids": outcome.retrieved_observation_ids,
        "retrieved_derivation_ids": outcome.retrieved_derivation_ids,
        "retrieved_facts": retrieved_facts,
        "retrieved_profile_gaps": retrieved_profile_gaps or [],
        "retrieved_context_associations": (
            retrieved_context_associations or []
        ),
        "retrieved_outcome_summaries": retrieved_outcome_summaries or [],
        "retrieved_outcome_observations": (
            retrieved_outcome_observations or []
        ),
        "source_ids": outcome.source_ids,
        "answer": outcome.answer,
        "failure_reason": outcome.failure_reason,
        "model_calls": [
            record.model_dump(mode="json") for record in outcome.model_calls
        ],
        "tool_calls": [
            trace.model_dump(mode="json") for trace in outcome.tool_calls
        ],
    }
    (run_dir / "query_run.json").write_text(
        json.dumps(sanitize_json_value(payload), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _terminal_outcome(
    *,
    run_dir: Path,
    question: str,
    status: str,
    answer: str,
    reason: str,
) -> QueryToolOutcome:
    outcome = QueryToolOutcome(
        status=status,
        answer=answer,
        failure_reason=reason,
    )
    _write_query_tool_run(
        run_dir=run_dir,
        question=question,
        outcome=outcome,
        event_ids=[],
        allowed_predicates=[],
        ontology_labels={},
        retrieved_facts=[],
        retrieved_profile_gaps=[],
        retrieved_context_associations=[],
        retrieved_outcome_summaries=[],
        retrieved_outcome_observations=[],
    )
    return outcome


def _report_subject(report_id: str) -> str:
    return report_id if report_id.startswith("urn:") else f"urn:aviation-agentic-ai:{report_id}"


def _context_items_for_relations(
    result: QueryToolResult,
    relations: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    associations = [
        item
        for item in result.items
        if item.get("item_type") == "context_association"
        and item.get("relation_type") in relations
    ]
    subjects = {_report_subject(str(item["report_id"])) for item in associations}
    facts = [
        item
        for item in result.items
        if item.get("item_type") == "formal_weather_fact"
        and item.get("subject") in subjects
    ]
    return associations, facts


def _raw_weather_values(
    facts: list[dict[str, Any]],
    predicate: str,
) -> list[str]:
    return sorted(
        {
            str(item.get("object") or "")
            for item in facts
            if item.get("predicate") == predicate and item.get("object")
        }
    )


def _formal_outcome_items(result: QueryToolResult | None) -> list[dict[str, Any]]:
    if result is None:
        return []
    return [
        item
        for item in result.items
        if item.get("item_type") == "formal_outcome_observation"
    ]


def _active_count_values(
    observations: list[dict[str, Any]],
) -> dict[str, int] | None:
    required = {
        "scheduled_arrival_count",
        "completed_arrival_count",
        "cancelled_count",
        "diverted_count",
    }
    selected = [
        item
        for item in observations
        if item.get("phase") == "active"
        and item.get("metric_key") in required
    ]
    by_metric: dict[str, int] = {}
    for item in selected:
        metric_key = str(item["metric_key"])
        value = item.get("value")
        if (
            metric_key in by_metric
            or not isinstance(value, int)
            or isinstance(value, bool)
            or value < 0
        ):
            return None
        by_metric[metric_key] = value
    return by_metric if set(by_metric) == required else None


def _facility_display_code(store: QueryGraphStore, event_id: str) -> str | None:
    values = {
        str(row.get("object") or "").rsplit(":", 1)[-1]
        for row in store.rows
        if row.get("subject") == event_id
        and row.get("predicate") == QueryPredicate.CONTROLLED_NAS_ELEMENT
        and row.get("object")
    }
    if len(values) != 1:
        return None
    code = values.pop()
    return code[1:] if re.fullmatch(r"K[A-Z]{3}", code) else code


def _active_outcome_sentence(
    *,
    observations: list[dict[str, Any]],
    facility_code: str,
) -> str | None:
    counts = _active_count_values(observations)
    if counts is None:
        return None
    return (
        "During the active interval, BTS reported "
        f"{counts['scheduled_arrival_count']} scheduled arrivals, "
        f"{counts['completed_arrival_count']} completed arrivals, "
        f"{counts['cancelled_count']} cancellations, and "
        f"{counts['diverted_count']} diversions for {facility_code} "
        "within the tracked BTS reporting scope."
    )


def _context_trace(
    *,
    tool_call_id: str,
    tool: str,
    arguments: dict[str, Any],
    result: QueryToolResult,
    started: float,
) -> QueryToolTrace:
    return QueryToolTrace(
        tool_call_id=tool_call_id,
        tool=tool,
        arguments=arguments,
        result_refs=result.fact_ids,
        context_association_ids=result.context_association_ids,
        outcome_summary_ids=result.outcome_summary_ids,
        observation_ids=result.observation_ids,
        derivation_ids=result.derivation_ids,
        source_ids=result.source_ids,
        status=result.status,
        duration_ms=(time.perf_counter() - started) * 1000.0,
        error=result.failure_reason or None,
    )


def _deterministic_context_outcome(
    *,
    run_dir: Path,
    question: str,
    intent: QueryIntent,
    store: QueryGraphStore,
    ontology_labels: dict[str, str],
) -> QueryToolOutcome:
    """Answer one registered context question without constructing a model."""

    if len(store.event_ids) != 1:
        return _terminal_outcome(
            run_dir=run_dir,
            question=question,
            status="insufficient",
            answer="Insufficient graph evidence.",
            reason="decision-context questions require exactly one registered event",
        )
    event_id = store.event_ids[0]
    context_store = QueryContextStore(run_dir, graph_store=store)
    core_predicates = [
        QueryPredicate.EVENT_TYPE,
        QueryPredicate.CONTROLLED_NAS_ELEMENT,
        QueryPredicate.EFFECTIVE_START,
        QueryPredicate.EFFECTIVE_END,
    ]
    gateway = QueryToolGateway(
        store,
        allowed_predicates={predicate.value for predicate in core_predicates},
        context_store=context_store,
    )
    traces: list[QueryToolTrace] = []
    context_result: QueryToolResult | None = None
    outcome_result: QueryToolResult | None = None
    core_result: QueryToolResult | None = None

    def blocked(
        exc: Exception,
        *,
        tool: str,
        arguments: dict[str, Any],
        started: float,
    ) -> QueryToolOutcome:
        error = sanitize_text(f"{type(exc).__name__}: {exc}")
        trace = QueryToolTrace(
            tool_call_id=f"deterministic:{intent.value}:{tool}:blocked",
            tool=tool,
            arguments=arguments,
            status="blocked",
            duration_ms=(time.perf_counter() - started) * 1000.0,
            error=error,
        )
        completed_results = [
            result
            for result in (core_result, context_result, outcome_result)
            if result is not None
        ]
        fact_ids = list(
            dict.fromkeys(
                fact_id
                for result in completed_results
                for fact_id in result.fact_ids
            )
        )
        context_ids = list(
            dict.fromkeys(
                association_id
                for result in completed_results
                for association_id in result.context_association_ids
            )
        )
        outcome_ids = list(
            dict.fromkeys(
                summary_id
                for result in completed_results
                for summary_id in result.outcome_summary_ids
            )
        )
        observation_ids = list(
            dict.fromkeys(
                observation_id
                for result in completed_results
                for observation_id in result.observation_ids
            )
        )
        derivation_ids = list(
            dict.fromkeys(
                derivation_id
                for result in completed_results
                for derivation_id in result.derivation_ids
            )
        )
        source_ids = sorted(
            {
                source_id
                for result in completed_results
                for source_id in result.source_ids
            }
        )
        context_items = [
            item
            for result in completed_results
            for item in result.items
            if item.get("item_type") == "context_association"
        ]
        outcome_items = [
            item
            for result in completed_results
            for item in result.items
            if item.get("item_type") == "formal_outcome_observation"
        ]
        return _write_deterministic_result(
            run_dir=run_dir,
            question=question,
            outcome=QueryToolOutcome(
                status="blocked",
                answer="",
                source_ids=source_ids,
                retrieved_fact_ids=fact_ids,
                retrieved_context_association_ids=context_ids,
                retrieved_outcome_summary_ids=outcome_ids,
                retrieved_observation_ids=observation_ids,
                retrieved_derivation_ids=derivation_ids,
                tool_calls=[*traces, trace],
                failure_reason=error,
            ),
            store=store,
            allowed_predicates=[
                predicate.value for predicate in core_predicates
            ]
            if core_result
            else [],
            retrieved_context_associations=context_items,
            retrieved_outcome_observations=outcome_items,
        )

    if intent is QueryIntent.RECONSTRUCTED_CASE:
        arguments = {
            "event_id": event_id,
            "predicates": [predicate.value for predicate in core_predicates],
        }
        started = time.perf_counter()
        try:
            core_result = gateway.get_event_facts(
                event_id=event_id,
                predicates=core_predicates,
            )
        except QueryToolError as exc:
            return blocked(
                exc,
                tool="get_event_facts",
                arguments=arguments,
                started=started,
            )
        traces.append(
            _context_trace(
                tool_call_id="deterministic:reconstructed_case:facts",
                tool="get_event_facts",
                arguments=arguments,
                result=core_result,
                started=started,
            )
        )
        predicate_counts = {
            predicate.value: sum(
                item.get("predicate") == predicate.value
                for item in core_result.items
            )
            for predicate in core_predicates
        }
        if any(count != 1 for count in predicate_counts.values()):
            return _write_deterministic_result(
                run_dir=run_dir,
                question=question,
                outcome=QueryToolOutcome(
                    status="insufficient",
                    answer="Insufficient graph evidence.",
                    retrieved_fact_ids=core_result.fact_ids,
                    tool_calls=traces,
                    failure_reason=(
                        "reconstructed case requires singular core event facts"
                    ),
                ),
                store=store,
                allowed_predicates=[
                    predicate.value for predicate in core_predicates
                ],
            )

    if intent in {
        QueryIntent.FORECAST_CONTEXT,
        QueryIntent.OBSERVED_WEATHER_CONTEXT,
        QueryIntent.RECONSTRUCTED_CASE,
    }:
        arguments = {"event_id": event_id}
        started = time.perf_counter()
        try:
            context_result = gateway.get_decision_context(event_id=event_id)
        except QueryToolError as exc:
            return blocked(
                exc,
                tool="get_decision_context",
                arguments=arguments,
                started=started,
            )
        traces.append(
            _context_trace(
                tool_call_id=f"deterministic:{intent.value}:context",
                tool="get_decision_context",
                arguments=arguments,
                result=context_result,
                started=started,
            )
        )
        if context_result.status == "insufficient":
            return _write_deterministic_result(
                run_dir=run_dir,
                question=question,
                outcome=QueryToolOutcome(
                    status="insufficient",
                    answer="Insufficient graph evidence.",
                    retrieved_fact_ids=core_result.fact_ids if core_result else [],
                    tool_calls=traces,
                    failure_reason="validated decision context is absent",
                ),
                store=store,
                allowed_predicates=[
                    predicate.value for predicate in core_predicates
                ]
                if core_result
                else [],
            )

    if intent in {QueryIntent.PUBLIC_OUTCOME, QueryIntent.RECONSTRUCTED_CASE}:
        arguments = {
            "event_id": event_id,
            "phases": ["baseline", "active", "recovery"],
        }
        started = time.perf_counter()
        try:
            outcome_result = gateway.get_outcome_summary(
                event_id=event_id,
                phases=("baseline", "active", "recovery"),
            )
        except QueryToolError as exc:
            return blocked(
                exc,
                tool="get_outcome_summary",
                arguments=arguments,
                started=started,
            )
        traces.append(
            _context_trace(
                tool_call_id=f"deterministic:{intent.value}:outcomes",
                tool="get_outcome_summary",
                arguments=arguments,
                result=outcome_result,
                started=started,
            )
        )
        if outcome_result.status in {"insufficient", "blocked"}:
            partial_associations = (
                [
                    item
                    for item in context_result.items
                    if item.get("item_type") == "context_association"
                ]
                if context_result
                else []
            )
            partial_observations = _formal_outcome_items(outcome_result)
            is_blocked = outcome_result.status == "blocked"
            return _write_deterministic_result(
                run_dir=run_dir,
                question=question,
                outcome=QueryToolOutcome(
                    status=outcome_result.status,
                    answer="" if is_blocked else "Insufficient graph evidence.",
                    source_ids=sorted(
                        {
                            *(
                                core_result.source_ids
                                if core_result
                                else []
                            ),
                            *(
                                context_result.source_ids
                                if context_result
                                else []
                            ),
                            *outcome_result.source_ids,
                        }
                    ),
                    retrieved_fact_ids=[
                        *(core_result.fact_ids if core_result else []),
                        *(context_result.fact_ids if context_result else []),
                        *outcome_result.fact_ids,
                    ],
                    retrieved_context_association_ids=(
                        context_result.context_association_ids
                        if context_result
                        else []
                    ),
                    retrieved_outcome_summary_ids=(
                        outcome_result.outcome_summary_ids
                    ),
                    retrieved_observation_ids=outcome_result.observation_ids,
                    retrieved_derivation_ids=outcome_result.derivation_ids,
                    tool_calls=traces,
                    failure_reason=(
                        outcome_result.failure_reason
                        or (
                            "validated public observations are blocked"
                            if is_blocked
                            else "validated public observations are absent"
                        )
                    ),
                ),
                store=store,
                allowed_predicates=[
                    predicate.value for predicate in core_predicates
                ]
                if core_result
                else [],
                retrieved_context_associations=partial_associations,
                retrieved_outcome_observations=partial_observations,
            )

    selected_associations: list[dict[str, Any]] = []
    selected_weather_facts: list[dict[str, Any]] = []
    selected_outcomes = _formal_outcome_items(outcome_result)
    source_ids: set[str] = set()
    retrieved_fact_ids: list[str] = core_result.fact_ids if core_result else []
    context_ids: list[str] = []
    outcome_ids = outcome_result.outcome_summary_ids if outcome_result else []
    observation_ids = outcome_result.observation_ids if outcome_result else []
    derivation_ids = outcome_result.derivation_ids if outcome_result else []

    if context_result is not None:
        relations = (
            {"latest_forecast_known_at_issue"}
            if intent is QueryIntent.FORECAST_CONTEXT
            else {
                "latest_observation_at_or_before_issue",
                "observation_during_operation",
            }
            if intent is QueryIntent.OBSERVED_WEATHER_CONTEXT
            else {
                "latest_forecast_known_at_issue",
                "latest_observation_at_or_before_issue",
                "observation_during_operation",
            }
        )
        selected_associations, selected_weather_facts = (
            _context_items_for_relations(context_result, relations)
        )
        if not selected_associations:
            return _write_deterministic_result(
                run_dir=run_dir,
                question=question,
                outcome=QueryToolOutcome(
                    status="insufficient",
                    answer="Insufficient graph evidence.",
                    retrieved_fact_ids=retrieved_fact_ids,
                    tool_calls=traces,
                    failure_reason="requested Weather context relation is absent",
                ),
                store=store,
                allowed_predicates=[
                    predicate.value for predicate in core_predicates
                ]
                if core_result
                else [],
            )
        context_ids = sorted(
            str(item["association_id"]) for item in selected_associations
        )
        retrieved_fact_ids = [
            *retrieved_fact_ids,
            *sorted(str(item["fact_id"]) for item in selected_weather_facts),
        ]
        source_ids.update(
            str(item["source_id"]) for item in selected_associations
        )
    if outcome_result is not None:
        source_ids.update(outcome_result.source_ids)
        retrieved_fact_ids = [
            *retrieved_fact_ids,
            *outcome_result.fact_ids,
        ]
    if core_result is not None:
        source_ids.update(core_result.source_ids)

    if intent is QueryIntent.FORECAST_CONTEXT:
        raw = _raw_weather_values(
            selected_weather_facts,
            "data:tafReportString",
        )
        if not raw:
            answer = "Insufficient graph evidence."
            status = "insufficient"
            reason = "forecast context has no formal TAF report string"
        else:
            answer = (
                "The latest forecast known at decision time is non-causal "
                f"context: {'; '.join(raw)}."
            )
            status = "ok"
            reason = ""
    elif intent is QueryIntent.OBSERVED_WEATHER_CONTEXT:
        raw = _raw_weather_values(
            selected_weather_facts,
            "data:metarReportString",
        )
        if not raw:
            answer = "Insufficient graph evidence."
            status = "insufficient"
            reason = "observed context has no formal METAR report string"
        else:
            answer = (
                "The observed Weather reports are non-causal context: "
                f"{'; '.join(raw)}."
            )
            status = "ok"
            reason = ""
    else:
        facility_code = _facility_display_code(store, event_id)
        active_sentence = (
            _active_outcome_sentence(
                observations=selected_outcomes,
                facility_code=facility_code,
            )
            if facility_code is not None
            else None
        )
        if active_sentence is None:
            return _write_deterministic_result(
                run_dir=run_dir,
                question=question,
                outcome=QueryToolOutcome(
                    status="insufficient",
                    answer="Insufficient graph evidence.",
                    source_ids=sorted(source_ids),
                    retrieved_fact_ids=list(dict.fromkeys(retrieved_fact_ids)),
                    retrieved_context_association_ids=context_ids,
                    retrieved_outcome_summary_ids=outcome_ids,
                    retrieved_observation_ids=observation_ids,
                    retrieved_derivation_ids=derivation_ids,
                    tool_calls=traces,
                    failure_reason=(
                        "formal active public observations are incomplete"
                    ),
                ),
                store=store,
                allowed_predicates=[
                    predicate.value for predicate in core_predicates
                ]
                if core_result
                else [],
                retrieved_context_associations=selected_associations,
                retrieved_outcome_observations=selected_outcomes,
            )
        status = "ok"
        reason = ""
        if intent is QueryIntent.PUBLIC_OUTCOME:
            answer = active_sentence
        else:
            assert core_result is not None
            by_predicate = {
                str(item["predicate"]): item for item in core_result.items
            }
            event_type = str(
                by_predicate[QueryPredicate.EVENT_TYPE]["object"]
            )
            facility = str(
                by_predicate[QueryPredicate.CONTROLLED_NAS_ELEMENT]["object"]
            ).rsplit(":", 1)[-1]
            start = by_predicate[QueryPredicate.EFFECTIVE_START]["object"]
            end = by_predicate[QueryPredicate.EFFECTIVE_END]["object"]
            forecast = _raw_weather_values(
                selected_weather_facts,
                "data:tafReportString",
            )
            observations = _raw_weather_values(
                selected_weather_facts,
                "data:metarReportString",
            )
            weather_text = "; ".join([*forecast, *observations])
            answer = (
                f"The reconstructed decision case records "
                f"{ontology_labels.get(event_type, event_type)} controlling "
                f"{facility} from {start} to {end}. Weather reports are "
                f"non-causal context: {weather_text}. {active_sentence}"
            )

    outcome = QueryToolOutcome(
        status=status,
        answer=answer,
        source_ids=sorted(source_ids),
        retrieved_fact_ids=list(dict.fromkeys(retrieved_fact_ids)),
        retrieved_context_association_ids=context_ids,
        retrieved_outcome_summary_ids=outcome_ids,
        retrieved_observation_ids=observation_ids,
        retrieved_derivation_ids=derivation_ids,
        tool_calls=traces,
        failure_reason=reason,
    )
    return _write_deterministic_result(
        run_dir=run_dir,
        question=question,
        outcome=outcome,
        store=store,
        allowed_predicates=[
            predicate.value for predicate in core_predicates
        ]
        if core_result
        else [],
        retrieved_context_associations=selected_associations,
        retrieved_outcome_observations=selected_outcomes,
    )


def _deterministic_intent_outcome(
    *,
    run_dir: Path,
    question: str,
    intent: QueryIntent,
    store: QueryGraphStore,
    ontology_labels: dict[str, str],
) -> QueryToolOutcome:
    """Answer one bounded field question through validated read-only tools."""

    if len(store.event_ids) != 1:
        return _terminal_outcome(
            run_dir=run_dir,
            question=question,
            status="insufficient",
            answer="Insufficient graph evidence.",
            reason="bounded record questions require exactly one registered event",
        )
    event_id = store.event_ids[0]
    predicates_by_intent = {
        QueryIntent.COMBINED_RECORD: [
            QueryPredicate.EVENT_TYPE,
            QueryPredicate.CONTROLLED_NAS_ELEMENT,
            QueryPredicate.EFFECTIVE_START,
            QueryPredicate.EFFECTIVE_END,
        ],
        QueryIntent.MEASURE: [QueryPredicate.EVENT_TYPE],
        QueryIntent.CONTROLLED_FACILITY: [
            QueryPredicate.CONTROLLED_NAS_ELEMENT
        ],
        QueryIntent.OPERATIONAL_PERIOD: [
            QueryPredicate.EFFECTIVE_START,
            QueryPredicate.EFFECTIVE_END,
        ],
        QueryIntent.PROVENANCE: [QueryPredicate.ADVISORY_NUMBER],
        QueryIntent.DECLARED_REASON: [QueryPredicate.IMPACTING_CONDITION],
    }
    predicates = predicates_by_intent[intent]
    gateway = QueryToolGateway(
        store,
        allowed_predicates={predicate.value for predicate in predicates},
    )
    started = time.perf_counter()
    result = gateway.get_event_facts(
        event_id=event_id,
        predicates=predicates,
    )
    traces = [
        QueryToolTrace(
            tool_call_id=f"deterministic:{intent.value}:facts",
            tool="get_event_facts",
            arguments={
                "event_id": event_id,
                "predicates": [predicate.value for predicate in predicates],
            },
            result_refs=result.fact_ids,
            source_ids=result.source_ids,
            status="ok",
            duration_ms=(time.perf_counter() - started) * 1000.0,
        )
    ]
    profile_result: QueryToolResult | None = None
    if intent is QueryIntent.DECLARED_REASON and not result.items:
        started = time.perf_counter()
        profile_result = gateway.get_profile_gaps(
            event_id=event_id,
            fields=["impacting_condition"],
        )
        traces.append(
            QueryToolTrace(
                tool_call_id="deterministic:declared_reason:profile_gap",
                tool="get_profile_gaps",
                arguments={
                    "event_id": event_id,
                    "fields": ["impacting_condition"],
                },
                result_refs=profile_result.profile_gap_ids,
                source_ids=profile_result.source_ids,
                status="ok",
                duration_ms=(time.perf_counter() - started) * 1000.0,
            )
        )

    if intent is QueryIntent.DECLARED_REASON and profile_result is not None:
        if len(profile_result.items) != 1:
            return _write_deterministic_result(
                run_dir=run_dir,
                question=question,
                outcome=QueryToolOutcome(
                    status="insufficient",
                    answer="Insufficient graph evidence.",
                    tool_calls=traces,
                    failure_reason="the advisory has no singular declared reason",
                ),
                store=store,
                allowed_predicates=[predicate.value for predicate in predicates],
            )
        item = profile_result.items[0]
        answer = (
            f"The advisory states {item['evidence_text']}. "
            "This source-supported field is outside the active formal profile."
        )
        outcome = QueryToolOutcome(
            status="ok",
            answer=answer,
            source_ids=profile_result.source_ids,
            retrieved_profile_gap_ids=profile_result.profile_gap_ids,
            tool_calls=traces,
        )
        return _write_deterministic_result(
            run_dir=run_dir,
            question=question,
            outcome=outcome,
            store=store,
            allowed_predicates=[predicate.value for predicate in predicates],
        )

    expected_count = {
        QueryIntent.COMBINED_RECORD: 4,
        QueryIntent.OPERATIONAL_PERIOD: 2,
    }.get(intent, 1)
    if len(result.items) != expected_count:
        return _write_deterministic_result(
            run_dir=run_dir,
            question=question,
            outcome=QueryToolOutcome(
                status="insufficient",
                answer="Insufficient graph evidence.",
                retrieved_fact_ids=result.fact_ids,
                tool_calls=traces,
                failure_reason="graph evidence is missing or not singular",
            ),
            store=store,
            allowed_predicates=[predicate.value for predicate in predicates],
        )

    by_predicate = {str(item["predicate"]): item for item in result.items}
    if intent is QueryIntent.COMBINED_RECORD:
        _expected_fields, answer = _expected_fixed_answer(
            rows=result.items,
            ontology_labels=ontology_labels,
        )
    elif intent is QueryIntent.MEASURE:
        value = str(by_predicate[QueryPredicate.EVENT_TYPE]["object"])
        answer = (
            "The published traffic-management measure is "
            f"{ontology_labels.get(value, value)}."
        )
    elif intent is QueryIntent.CONTROLLED_FACILITY:
        value = str(
            by_predicate[QueryPredicate.CONTROLLED_NAS_ELEMENT]["object"]
        )
        answer = f"The controlled facility is {value.rsplit(':', 1)[-1]}."
    elif intent is QueryIntent.OPERATIONAL_PERIOD:
        start = by_predicate[QueryPredicate.EFFECTIVE_START]["object"]
        end = by_predicate[QueryPredicate.EFFECTIVE_END]["object"]
        answer = f"The TMI operational period is {start} to {end}."
    elif intent is QueryIntent.DECLARED_REASON:
        item = by_predicate[QueryPredicate.IMPACTING_CONDITION]
        if not str(item.get("evidence_text") or "").strip():
            return _write_deterministic_result(
                run_dir=run_dir,
                question=question,
                outcome=QueryToolOutcome(
                    status="insufficient",
                    answer="Insufficient graph evidence.",
                    retrieved_fact_ids=result.fact_ids,
                    tool_calls=traces,
                    failure_reason="declared reason has no exact source evidence",
                ),
                store=store,
                allowed_predicates=[
                    predicate.value for predicate in predicates
                ],
            )
        answer = (
            f"The advisory records {item['object']} as its impacting condition. "
            f"Source wording: {item['evidence_text']}."
        )
    else:
        item = by_predicate[QueryPredicate.ADVISORY_NUMBER]
        answer = (
            f"Source {result.source_ids[0]} supports advisory "
            f"{item['object']}."
        )
    outcome = QueryToolOutcome(
        status="ok",
        answer=answer,
        source_ids=result.source_ids,
        retrieved_fact_ids=result.fact_ids,
        tool_calls=traces,
    )
    return _write_deterministic_result(
        run_dir=run_dir,
        question=question,
        outcome=outcome,
        store=store,
        allowed_predicates=[predicate.value for predicate in predicates],
    )


def _write_deterministic_result(
    *,
    run_dir: Path,
    question: str,
    outcome: QueryToolOutcome,
    store: QueryGraphStore,
    allowed_predicates: list[str],
    retrieved_context_associations: list[dict[str, Any]] | None = None,
    retrieved_outcome_summaries: list[dict[str, Any]] | None = None,
    retrieved_outcome_observations: list[dict[str, Any]] | None = None,
) -> QueryToolOutcome:
    retrieved_facts = [
        store.fact_by_id[fact_id]
        for fact_id in outcome.retrieved_fact_ids
        if fact_id in store.fact_by_id
    ]
    retrieved_gaps = [
        store.profile_gap_by_id[gap_id].model_dump(mode="json")
        for gap_id in outcome.retrieved_profile_gap_ids
        if gap_id in store.profile_gap_by_id
    ]
    _write_query_tool_run(
        run_dir=run_dir,
        question=question,
        outcome=outcome,
        event_ids=store.event_ids,
        allowed_predicates=allowed_predicates,
        ontology_labels={},
        retrieved_facts=retrieved_facts,
        retrieved_profile_gaps=retrieved_gaps,
        retrieved_context_associations=retrieved_context_associations,
        retrieved_outcome_summaries=retrieved_outcome_summaries,
        retrieved_outcome_observations=retrieved_outcome_observations,
    )
    return outcome


def answer_question_with_tools(
    *,
    run_dir: str | Path,
    question: str,
    model_factory: ToolModelFactory,
) -> QueryToolOutcome:
    """Run one registered decision-record question through read-only tools."""

    path = Path(run_dir)
    intent = classify_registered_question(question)
    if intent is None:
        return _terminal_outcome(
            run_dir=path,
            question=question,
            status="insufficient",
            answer="Insufficient graph evidence.",
            reason="question is outside the registered Query Agent capability",
        )
    if intent is QueryIntent.RECONSTRUCTION_EVIDENCE_PATHS:
        return _terminal_outcome(
            run_dir=path,
            question=question,
            status="insufficient",
            answer=(
                "This graph-path question requires a normalized decision-case corpus."
            ),
            reason="case-scoped graph traversal is corpus-only",
        )

    try:
        store = QueryGraphStore(path)
    except QueryToolError as exc:
        return _terminal_outcome(
            run_dir=path,
            question=question,
            status="blocked",
            answer="",
            reason=str(exc),
        )

    if not store.event_ids:
        return _terminal_outcome(
            run_dir=path,
            question=question,
            status="insufficient",
            answer="Insufficient graph evidence.",
            reason="materialized graph contains no registered event",
        )
    if isinstance(intent, AnalysisIntent):
        try:
            return _analysis_outcome(
                run_dir=path,
                question=question,
                intent=intent,
                store=store,
                model_factory=model_factory,
            )
        except (OSError, RuntimeError, ValueError) as exc:
            return QueryToolOutcome(
                status="blocked",
                failure_reason=sanitize_text(f"{type(exc).__name__}: {exc}"),
            )
    guide = load_schema_guide()
    labels = ontology_labels_for(store.rows, guide)
    if intent in {
        QueryIntent.FORECAST_CONTEXT,
        QueryIntent.OBSERVED_WEATHER_CONTEXT,
        QueryIntent.PUBLIC_OUTCOME,
        QueryIntent.RECONSTRUCTED_CASE,
    }:
        return _deterministic_context_outcome(
            run_dir=path,
            question=question,
            intent=intent,
            store=store,
            ontology_labels=labels,
        )
    try:
        return _deterministic_intent_outcome(
            run_dir=path,
            question=question,
            intent=intent,
            store=store,
            ontology_labels=labels,
        )
    except QueryToolError as exc:
        return _terminal_outcome(
            run_dir=path,
            question=question,
            status="blocked",
            answer="",
            reason=sanitize_text(f"{type(exc).__name__}: {exc}"),
        )
