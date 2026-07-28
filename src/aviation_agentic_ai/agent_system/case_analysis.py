"""Closed two-turn runtime for bounded Decision Case Analysis."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, Literal

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import BaseTool, tool
from pydantic import Field

from aviation_agentic_ai.agent_system.audit import sanitize_json_value, sanitize_text
from aviation_agentic_ai.agent_system.case_analysis_tools import (
    BoundQueryGateway,
    BoundQueryObservation,
)
from aviation_agentic_ai.agent_system.contracts import (
    ModelCallRecord,
    QueryToolOutcome,
    QueryToolTrace as OutcomeToolTrace,
    StrictModel,
)
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    AnswerStatement,
    AnswerStatementKind,
    CaseAnalysisTask,
    CaseAnalysisTaskFields,
    ComponentLayerResult,
    ComponentLayerStatus,
    ContractExecutionBinding,
    QueryEvidenceBundle,
    QueryEvidenceBundleFields,
    QueryStatus,
    SourceSnapshotBinding,
    canonical_id_tuple_token,
    seal_case_analysis_task,
    seal_query_evidence_bundle,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.prompts import (
    DEFAULT_PROMPT_CATALOG,
    assemble_prompt,
)
from aviation_agentic_ai.agent_system.query_plan import AnalysisIntent, QueryPlan
from aviation_agentic_ai.agent_system.query_tools import QueryGraphStore
from aviation_agentic_ai.agent_system.tool_model import ToolCallingModel

MAX_CASE_ANALYSIS_MODEL_CALLS = 2
MAX_CASE_ANALYSIS_BOUND_STEPS = 3
ANSWER_CONTRACT_ID = "decision-case-analysis-answer-v1"

ToolModelFactory = Callable[[list[BaseTool]], ToolCallingModel]

_FORBIDDEN_CLAIM = re.compile(
    r"\b(?:caused?|causal|recommend(?:ed|ation)?|optimal|should|"
    r"safe\s+to\s+fly|flight\s+control)\b",
    flags=re.IGNORECASE,
)
_CJK = re.compile(r"[\u3400-\u9fff]")


class ExecuteBoundQueryStepInput(StrictModel):
    """The complete model-visible input schema for one plan-bound read."""

    step_id: str = Field(min_length=1)


class _StatementPayload(StrictModel):
    """Provider-facing statement shape; stable IDs are generated locally."""

    kind: Literal[
        "source_fact",
        "deterministic_derivation",
        "agent_synthesis",
    ]
    text: str = Field(min_length=1, max_length=600)
    support_fact_ids: list[str] = Field(default_factory=list)
    support_derivation_ids: list[str] = Field(default_factory=list)
    support_profile_gap_ids: list[str] = Field(default_factory=list)
    support_source_ids: list[str] = Field(default_factory=list)
    support_statement_indexes: list[int] = Field(default_factory=list)


class _AnswerPayload(StrictModel):
    """The whole second-turn output contract."""

    statements: list[_StatementPayload] = Field(default_factory=list, max_length=8)
    limitations: list[str] = Field(default_factory=list, max_length=8)


def _model_tools(gateway: BoundQueryGateway) -> list[BaseTool]:
    """Expose exactly one bound-step schema to the model factory."""

    @tool("execute_bound_query_step", args_schema=ExecuteBoundQueryStepInput)
    def execute_bound_query_step(step_id: str) -> str:
        """Execute one step already sealed into the current query plan."""

        return gateway.execute_bound_query_step(step_id=step_id).model_dump_json()

    return [execute_bound_query_step]


def _base_messages(
    plan: QueryPlan,
    *,
    catalog_path: str,
    selectable_step_ids: frozenset[str],
) -> list[BaseMessage]:
    assembled = assemble_prompt(
        "decision_case_analysis",
        {
            "question": plan.question,
            "query_plan_id": plan.query_plan_id,
            "available_bound_steps": "\n".join(
                f"- {step.step_id}: {step.operation}"
                for step in plan.steps
                if step.step_id in selectable_step_ids
            )
            or "(none; required steps were preflighted)",
        },
        catalog_path=catalog_path,
    )
    messages: list[BaseMessage] = []
    for role, content in assembled.messages:
        if role == "system":
            messages.append(SystemMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        else:
            messages.append(HumanMessage(content=content))
    return messages


def _sanitized_record(record: ModelCallRecord) -> ModelCallRecord:
    """Retain call metadata and validated tool selections, never raw reasoning."""

    return record.model_copy(
        update={
            "raw_response": "",
            "error": "model_call_failed" if record.error else None,
        }
    )


def _selection_error(
    *,
    turn_message: AIMessage | None,
    record: ModelCallRecord,
    selectable_step_ids: frozenset[str],
    remaining_step_budget: int,
) -> tuple[str | None, tuple[tuple[str, str], ...]]:
    if record.error:
        return "analysis model call failed", ()
    if turn_message is None:
        return "analysis model returned no tool-selection message", ()
    if record.invalid_tool_calls:
        return "analysis model returned an invalid native tool call", ()
    calls = tuple(record.tool_calls)
    if not calls:
        return None, ()
    if len(calls) > remaining_step_budget:
        return "analysis model exceeded the remaining step budget", ()

    message_calls = tuple(
        (
            str(call.get("id") or ""),
            str(call.get("name") or ""),
            sanitize_json_value(call.get("args")),
        )
        for call in turn_message.tool_calls
    )
    record_calls = tuple(
        (call.call_id, call.name, sanitize_json_value(call.arguments))
        for call in calls
    )
    if message_calls != record_calls:
        return "analysis model tool-call record differs from native message", ()

    selected: list[tuple[str, str]] = []
    seen_call_ids: set[str] = set()
    seen_step_ids: set[str] = set()
    for call in calls:
        if call.call_id in seen_call_ids:
            return "analysis model repeated a tool-call ID", ()
        seen_call_ids.add(call.call_id)
        if call.name != "execute_bound_query_step":
            return "analysis model requested a non-analysis tool", ()
        if set(call.arguments) != {"step_id"}:
            return "execute_bound_query_step accepts only step_id", ()
        step_id = call.arguments.get("step_id")
        if not isinstance(step_id, str) or not step_id:
            return "execute_bound_query_step requires a nonempty step_id", ()
        if step_id not in selectable_step_ids:
            return "analysis model requested a non-optional bound step", ()
        if step_id in seen_step_ids:
            return "analysis model repeated a bound step", ()
        seen_step_ids.add(step_id)
        selected.append((call.call_id, step_id))
    return None, tuple(selected)


def _synthesis_error(
    *,
    turn_message: AIMessage | None,
    record: ModelCallRecord,
) -> str | None:
    """Reject provider failures and any mismatch before parsing answer JSON."""

    if record.error:
        return "analysis model call failed"
    if turn_message is None:
        return "analysis model returned no synthesis message"
    if record.invalid_tool_calls or turn_message.invalid_tool_calls:
        return "analysis model returned an invalid synthesis tool call"
    message_calls = tuple(
        (
            str(call.get("id") or ""),
            str(call.get("name") or ""),
            sanitize_json_value(call.get("args")),
        )
        for call in turn_message.tool_calls
    )
    record_calls = tuple(
        (call.call_id, call.name, sanitize_json_value(call.arguments))
        for call in record.tool_calls
    )
    if message_calls != record_calls:
        return "analysis model tool-call record differs from native message"
    if record_calls:
        return "analysis synthesis turn cannot request another tool"
    return None


def _observation_status(
    observation: BoundQueryObservation,
) -> ComponentLayerStatus:
    if observation.status in {"ok", "partial"}:
        return ComponentLayerStatus.OK
    if observation.status == "insufficient":
        return ComponentLayerStatus.INSUFFICIENT
    return ComponentLayerStatus.BLOCKED


def _component_results(
    *,
    plan: QueryPlan,
    observations: dict[str, BoundQueryObservation],
    trace_ids: dict[str, str],
    runtime_failure: str | None,
) -> tuple[ComponentLayerResult, ...]:
    if runtime_failure:
        return (
            ComponentLayerResult(
                layer_id="analysis_runtime",
                status=ComponentLayerStatus.BLOCKED,
                required_for_task=True,
                blocking_error_id=stable_contract_id(
                    "analysis-runtime-error",
                    plan.query_plan_id,
                    runtime_failure,
                ),
            ),
        )

    rows: list[ComponentLayerResult] = []
    for step in plan.steps:
        observation = observations.get(step.step_id)
        if observation is None:
            if step.required:
                rows.append(
                    ComponentLayerResult(
                        layer_id=step.step_id,
                        status=ComponentLayerStatus.INSUFFICIENT,
                        required_for_task=True,
                        missing_reason_code="required bound step was not executed",
                    )
                )
            continue
        status = _observation_status(observation)
        if status is ComponentLayerStatus.OK:
            artifact_ids = tuple(
                sorted(
                    {
                        trace_ids[step.step_id],
                        *observation.fact_ids,
                        *observation.derivation_ids,
                        *observation.profile_gap_ids,
                        *observation.assessment_ids,
                        *observation.source_ids,
                    }
                )
            )
            rows.append(
                ComponentLayerResult(
                    layer_id=step.step_id,
                    status=status,
                    required_for_task=step.required,
                    artifact_ids=artifact_ids,
                )
            )
        elif status is ComponentLayerStatus.INSUFFICIENT:
            rows.append(
                ComponentLayerResult(
                    layer_id=step.step_id,
                    status=status,
                    required_for_task=step.required,
                    missing_reason_code=observation.limitation
                    or "bound observation is insufficient",
                )
            )
        else:
            rows.append(
                ComponentLayerResult(
                    layer_id=step.step_id,
                    status=status,
                    required_for_task=step.required,
                    blocking_error_id=stable_contract_id(
                        "bound-observation-error",
                        plan.query_plan_id,
                        step.step_id,
                        observation.limitation or "blocked",
                    ),
                )
            )
    return tuple(rows)


def _rollup_status(
    components: Sequence[ComponentLayerResult],
) -> QueryStatus:
    if any(
        row.required_for_task and row.status is ComponentLayerStatus.BLOCKED
        for row in components
    ):
        return QueryStatus.BLOCKED
    if any(
        row.required_for_task
        and row.status is ComponentLayerStatus.INSUFFICIENT
        for row in components
    ):
        return QueryStatus.INSUFFICIENT
    return QueryStatus.OK


def _retrieved_ids(
    observations: Sequence[BoundQueryObservation],
    field_name: str,
) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                identifier
                for observation in observations
                for identifier in getattr(observation, field_name)
            }
        )
    )


def _source_snapshot_bindings(
    gateway: BoundQueryGateway,
    source_ids: tuple[str, ...],
) -> tuple[tuple[SourceSnapshotBinding, ...], tuple[str, ...]]:
    store = gateway._store
    registry = getattr(store, "source_snapshots", None)
    rows: list[SourceSnapshotBinding] = []
    missing: list[str] = []
    for source_id in source_ids:
        snapshot = registry.get(source_id) if registry is not None else None
        if snapshot is None:
            missing.append(source_id)
            continue
        rows.append(
            SourceSnapshotBinding(
                source_id=source_id,
                source_family=snapshot.family,
                source_snapshot_sha256=snapshot.content_sha256,
            )
        )
    return tuple(sorted(rows, key=lambda row: row.source_id)), tuple(sorted(missing))


def _task_id(
    *,
    plan: QueryPlan,
    requested_evidence_layers: tuple[str, ...],
) -> str:
    return stable_contract_id(
        "case-analysis-task",
        plan.run_id,
        plan.query_plan_id,
        canonical_id_tuple_token(
            plan.event_or_case_scope,
            sort_values=False,
        ),
        canonical_id_tuple_token(
            requested_evidence_layers,
            sort_values=True,
        ),
        ANSWER_CONTRACT_ID,
    )


def _seal_analysis_task(
    *,
    plan: QueryPlan,
    gateway: BoundQueryGateway,
    observations: dict[str, BoundQueryObservation],
    binding: ContractExecutionBinding,
    runtime_failure: str | None,
) -> CaseAnalysisTask:
    ordered_observations = tuple(
        observations[step.step_id]
        for step in plan.steps
        if step.step_id in observations
    )
    trace_by_step = {trace.step_id: trace.trace_id for trace in gateway.traces}
    components = _component_results(
        plan=plan,
        observations=observations,
        trace_ids=trace_by_step,
        runtime_failure=runtime_failure,
    )
    fact_ids = _retrieved_ids(ordered_observations, "fact_ids")
    derivation_ids = _retrieved_ids(ordered_observations, "derivation_ids")
    profile_gap_ids = _retrieved_ids(ordered_observations, "profile_gap_ids")
    assessment_ids = _retrieved_ids(ordered_observations, "assessment_ids")
    source_ids = _retrieved_ids(ordered_observations, "source_ids")
    source_bindings, missing_sources = _source_snapshot_bindings(
        gateway,
        source_ids,
    )
    if missing_sources and runtime_failure is None:
        runtime_failure = (
            "retrieved sources lack current-run snapshot bindings: "
            + ", ".join(missing_sources)
        )
        components = _component_results(
            plan=plan,
            observations=observations,
            trace_ids=trace_by_step,
            runtime_failure=runtime_failure,
        )
    limitations = {
        observation.limitation
        for observation in ordered_observations
        if observation.limitation
    }
    if runtime_failure:
        limitations.add(runtime_failure)
    requested_layers = tuple(
        sorted(
            {
                layer
                for step in plan.steps
                for layer in step.allowed_evidence_layers
            }
        )
    )
    return seal_case_analysis_task(
        fields=CaseAnalysisTaskFields(
            task_id=_task_id(
                plan=plan,
                requested_evidence_layers=requested_layers,
            ),
            run_id=plan.run_id,
            question=plan.question,
            intent_family=plan.intent_family.value,
            event_or_case_scope=plan.event_or_case_scope,
            query_plan_id=plan.query_plan_id,
            available_bound_step_ids=tuple(sorted(step.step_id for step in plan.steps)),
            executed_bound_step_ids=tuple(
                step.step_id
                for step in plan.steps
                if step.step_id in observations
            ),
            requested_evidence_layers=requested_layers,
            retrieved_fact_ids=fact_ids,
            retrieved_derivation_ids=derivation_ids,
            retrieved_profile_gap_ids=profile_gap_ids,
            retrieved_assessment_ids=assessment_ids,
            retrieved_source_ids=source_ids,
            component_layer_results=components,
            missing_evidence=tuple(sorted(limitations)),
            source_snapshot_bindings=source_bindings,
            remaining_step_budget=MAX_CASE_ANALYSIS_BOUND_STEPS
            - len(observations),
            answer_status=_rollup_status(components),
            answer_contract_id=ANSWER_CONTRACT_ID,
        ),
        binding=binding,
    )


def _query_id(
    *,
    task: CaseAnalysisTask,
    status: QueryStatus,
) -> str:
    return stable_contract_id(
        "query-evidence-bundle",
        task.task_id,
        task.payload_checksum,
        status.value,
        canonical_id_tuple_token(
            task.executed_bound_step_ids,
            sort_values=False,
        ),
        canonical_id_tuple_token(task.retrieved_fact_ids, sort_values=True),
        canonical_id_tuple_token(task.retrieved_derivation_ids, sort_values=True),
        canonical_id_tuple_token(task.retrieved_profile_gap_ids, sort_values=True),
        canonical_id_tuple_token(task.retrieved_source_ids, sort_values=True),
        task.answer_contract_id,
    )


def _seal_bundle(
    *,
    task: CaseAnalysisTask,
    plan: QueryPlan,
    gateway: BoundQueryGateway,
    binding: ContractExecutionBinding,
    status: QueryStatus,
    statements: tuple[AnswerStatement, ...] = (),
    extra_limitations: tuple[str, ...] = (),
) -> QueryEvidenceBundle:
    limitations = tuple(
        sorted({*task.missing_evidence, *extra_limitations})
    )
    unexecuted = tuple(
        sorted(
            step.step_id
            for step in plan.steps
            if step.required and step.step_id not in task.executed_bound_step_ids
        )
    )
    return seal_query_evidence_bundle(
        task=task,
        fields=QueryEvidenceBundleFields(
            query_id=_query_id(task=task, status=status),
            run_id=task.run_id,
            task_id=task.task_id,
            task_payload_checksum=task.payload_checksum,
            answer_status=status,
            answer_contract_id=task.answer_contract_id,
            component_statuses=tuple(
                row.status for row in task.component_layer_results
            ),
            component_layer_results=task.component_layer_results,
            executed_step_ids=task.executed_bound_step_ids,
            unexecuted_required_step_ids=unexecuted,
            retrieved_fact_ids=task.retrieved_fact_ids,
            retrieved_derivation_ids=task.retrieved_derivation_ids,
            retrieved_profile_gap_ids=task.retrieved_profile_gap_ids,
            retrieved_assessment_ids=task.retrieved_assessment_ids,
            retrieved_source_ids=task.retrieved_source_ids,
            source_snapshot_bindings=task.source_snapshot_bindings,
            tool_trace_ids=tuple(trace.trace_id for trace in gateway.traces),
            answer_statements=statements,
            limitations=limitations,
        ),
        binding=binding,
    )


def _message_text(message: AIMessage) -> str:
    if isinstance(message.content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in message.content
        )
    return str(message.content or "")


def _validate_answer_text(text: str) -> None:
    if _CJK.search(text):
        raise ValueError("analysis answer must be English")
    if _FORBIDDEN_CLAIM.search(text):
        raise ValueError("analysis answer contains a forbidden claim")
    if len(text.split()) > 80:
        raise ValueError("analysis statement exceeds the word budget")


def _statement_id(
    *,
    task: CaseAnalysisTask,
    ordinal: int,
    payload: _StatementPayload,
    support_statement_ids: tuple[str, ...],
) -> str:
    return stable_contract_id(
        "answer-statement",
        task.task_id,
        str(ordinal),
        payload.kind,
        payload.text,
        canonical_id_tuple_token(
            tuple(sorted(payload.support_fact_ids)),
            sort_values=True,
        ),
        canonical_id_tuple_token(
            tuple(sorted(payload.support_derivation_ids)),
            sort_values=True,
        ),
        canonical_id_tuple_token(
            tuple(sorted(payload.support_profile_gap_ids)),
            sort_values=True,
        ),
        canonical_id_tuple_token(
            tuple(sorted(payload.support_source_ids)),
            sort_values=True,
        ),
        canonical_id_tuple_token(
            support_statement_ids,
            sort_values=False,
        ),
    )


def _support_maps(
    observations: Sequence[BoundQueryObservation],
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Recover fact/derivation-to-source bindings from validated observations."""

    fact_sources: dict[str, set[str]] = {}
    derivation_sources: dict[str, set[str]] = {}
    for observation in observations:
        for item in observation.items:
            item_sources = {
                str(source_id) for source_id in item.get("source_ids", ())
            }
            source_id = item.get("source_id")
            if source_id:
                item_sources.add(str(source_id))
            fact_ids = {
                str(fact_id) for fact_id in item.get("fact_ids", ())
            }
            fact_id = item.get("fact_id")
            if fact_id:
                fact_ids.add(str(fact_id))
            for current_fact_id in fact_ids:
                fact_sources.setdefault(current_fact_id, set()).update(
                    item_sources
                )
            derivation_id = item.get("derivation_id")
            if derivation_id:
                derivation_sources.setdefault(
                    str(derivation_id),
                    set(),
                ).update(item_sources)
    return fact_sources, derivation_sources


def _parse_answer(
    *,
    task: CaseAnalysisTask,
    message: AIMessage,
    observations: Sequence[BoundQueryObservation],
) -> tuple[tuple[AnswerStatement, ...], tuple[str, ...]]:
    if message.tool_calls or message.invalid_tool_calls:
        raise ValueError("analysis synthesis turn cannot request another tool")
    try:
        payload = _AnswerPayload.model_validate_json(_message_text(message))
    except Exception as exc:
        raise ValueError("analysis synthesis is not valid strict JSON") from exc
    if not payload.statements:
        raise ValueError("analysis synthesis requires a supported statement")

    allowed = {
        "support_fact_ids": set(task.retrieved_fact_ids),
        "support_derivation_ids": set(task.retrieved_derivation_ids),
        "support_profile_gap_ids": set(task.retrieved_profile_gap_ids),
        "support_source_ids": set(task.retrieved_source_ids),
    }
    fact_sources, derivation_sources = _support_maps(observations)
    statements: list[AnswerStatement] = []
    for index, row in enumerate(payload.statements):
        _validate_answer_text(row.text)
        for field_name, available in allowed.items():
            values = getattr(row, field_name)
            if len(set(values)) != len(values) or not set(values).issubset(available):
                raise ValueError("statement support is outside sealed analysis task")
        if (
            len(set(row.support_statement_indexes))
            != len(row.support_statement_indexes)
            or any(
                statement_index < 0 or statement_index >= index
                for statement_index in row.support_statement_indexes
            )
        ):
            raise ValueError("statement cites a non-prior analysis statement")
        support_statement_ids = tuple(
            statements[statement_index].statement_id
            for statement_index in row.support_statement_indexes
        )
        kind = AnswerStatementKind(row.kind)
        cited_sources = set(row.support_source_ids)
        if kind is AnswerStatementKind.SOURCE_FACT and any(
            not fact_sources.get(fact_id, set()).intersection(cited_sources)
            for fact_id in row.support_fact_ids
        ):
            raise ValueError("cited source does not cover cited fact")
        if kind is AnswerStatementKind.DETERMINISTIC_DERIVATION and any(
            not derivation_sources.get(derivation_id, set()).intersection(
                cited_sources
            )
            for derivation_id in row.support_derivation_ids
        ):
            raise ValueError("cited source does not cover cited derivation")
        statement = AnswerStatement(
            statement_id=_statement_id(
                task=task,
                ordinal=index,
                payload=row,
                support_statement_ids=support_statement_ids,
            ),
            statement_kind=kind,
            text=row.text,
            support_fact_ids=tuple(sorted(row.support_fact_ids)),
            support_derivation_ids=tuple(sorted(row.support_derivation_ids)),
            support_profile_gap_ids=tuple(sorted(row.support_profile_gap_ids)),
            support_source_ids=tuple(sorted(row.support_source_ids)),
            support_statement_ids=support_statement_ids,
        )
        statements.append(statement)

    limitations = tuple(sorted(set(payload.limitations)))
    if not set(limitations).issubset(task.missing_evidence):
        raise ValueError("analysis answer invented a limitation")
    if sum(len(statement.text.split()) for statement in statements) > 200:
        raise ValueError("analysis answer exceeded the total word budget")
    return tuple(statements), limitations


def _outcome_traces(
    *,
    selected: tuple[tuple[str, str], ...],
    observations: dict[str, BoundQueryObservation],
) -> list[OutcomeToolTrace]:
    rows: list[OutcomeToolTrace] = []
    for call_id, step_id in selected:
        observation = observations.get(step_id)
        if observation is None:
            continue
        rows.append(
            OutcomeToolTrace(
                tool_call_id=call_id,
                tool="execute_bound_query_step",
                arguments={"step_id": step_id},
                result_refs=list(observation.fact_ids),
                derivation_ids=list(observation.derivation_ids),
                source_ids=list(observation.source_ids),
                status="ok"
                if observation.status in {"ok", "partial"}
                else observation.status,
                error=(
                    observation.limitation or None
                    if observation.status in {"insufficient", "blocked"}
                    else None
                ),
            )
        )
    return rows


def _outcome(
    *,
    bundle: QueryEvidenceBundle,
    records: list[ModelCallRecord],
    traces: list[OutcomeToolTrace],
    failure_reason: str = "",
) -> QueryToolOutcome:
    status = {
        QueryStatus.OK: "ok",
        QueryStatus.INSUFFICIENT: "insufficient",
        QueryStatus.BLOCKED: "blocked",
        QueryStatus.UNSUPPORTED: "insufficient",
    }[bundle.answer_status]
    answer_parts = [statement.text for statement in bundle.answer_statements]
    answer_parts.extend(bundle.limitations)
    if not answer_parts and status == "insufficient":
        answer_parts.append("Insufficient graph evidence.")
    return QueryToolOutcome(
        status=status,
        answer=" ".join(answer_parts),
        source_ids=list(bundle.retrieved_source_ids),
        retrieved_fact_ids=list(bundle.retrieved_fact_ids),
        retrieved_profile_gap_ids=list(bundle.retrieved_profile_gap_ids),
        retrieved_derivation_ids=list(bundle.retrieved_derivation_ids),
        model_calls=records,
        tool_calls=traces,
        failure_reason=failure_reason,
    )


def run_case_analysis_agent(
    *,
    plan: QueryPlan,
    gateway: BoundQueryGateway,
    model_factory: ToolModelFactory,
    binding: ContractExecutionBinding,
    catalog_path: str = DEFAULT_PROMPT_CATALOG,
) -> tuple[CaseAnalysisTask, QueryEvidenceBundle, QueryToolOutcome]:
    """Run one sealed plan through select, execute, synthesize, and seal."""

    if binding.run_id != plan.run_id:
        raise ValueError("analysis binding run_id differs from query plan")
    if gateway._plan != plan:
        raise ValueError("analysis gateway is not bound to the supplied query plan")

    observations: dict[str, BoundQueryObservation] = {}
    selected: list[tuple[str, str]] = []
    for ordinal, step in enumerate(plan.steps, start=1):
        if not step.required:
            continue
        try:
            observation = gateway.execute_bound_query_step(step_id=step.step_id)
        except (RuntimeError, ValueError):
            observation = BoundQueryObservation(
                step_id=step.step_id,
                status="blocked",
                limitation="required bound step failed integrity validation",
            )
        observations[step.step_id] = observation
        selected.append((f"preflight:{ordinal}", step.step_id))

    task = _seal_analysis_task(
        plan=plan,
        gateway=gateway,
        observations=observations,
        binding=binding,
        runtime_failure=None,
    )
    outcome_traces = _outcome_traces(
        selected=tuple(selected),
        observations=observations,
    )
    if task.answer_status is not QueryStatus.OK:
        status = task.answer_status or QueryStatus.BLOCKED
        bundle = _seal_bundle(
            task=task,
            plan=plan,
            gateway=gateway,
            binding=binding,
            status=status,
        )
        return task, bundle, _outcome(
            bundle=bundle,
            records=[],
            traces=outcome_traces,
            failure_reason=(
                "required analysis evidence failed validation"
                if status is QueryStatus.BLOCKED
                else ""
            ),
        )

    if plan.intent_family is AnalysisIntent.EPISODE:
        bundle = _seal_bundle(
            task=task,
            plan=plan,
            gateway=gateway,
            binding=binding,
            status=QueryStatus.OK,
        )
        return task, bundle, _outcome(
            bundle=bundle,
            records=[],
            traces=outcome_traces,
        )

    optional_step_ids = frozenset(
        step.step_id for step in plan.steps if not step.required
    )
    remaining_step_budget = MAX_CASE_ANALYSIS_BOUND_STEPS - len(observations)
    tools = _model_tools(gateway)
    if [registered.name for registered in tools] != ["execute_bound_query_step"]:
        raise AssertionError("Decision Case Analysis exposed an unexpected tool")
    model = model_factory(tools)
    base_messages = _base_messages(
        plan,
        catalog_path=catalog_path,
        selectable_step_ids=optional_step_ids,
    )
    records: list[ModelCallRecord] = []
    selection_message: AIMessage | None = None
    optional_selected: tuple[tuple[str, str], ...] = ()
    selection_error: str | None = None
    if optional_step_ids:
        selection_turn = model.invoke(base_messages, phase="select_tool")
        records.append(_sanitized_record(selection_turn.record))
        selection_message = selection_turn.message
        selection_error, optional_selected = _selection_error(
            turn_message=selection_turn.message,
            record=selection_turn.record,
            selectable_step_ids=optional_step_ids,
            remaining_step_budget=remaining_step_budget,
        )
        if selection_error is None:
            for _call_id, step_id in optional_selected:
                try:
                    observation = gateway.execute_bound_query_step(
                        step_id=step_id
                    )
                except (RuntimeError, ValueError):
                    observation = BoundQueryObservation(
                        step_id=step_id,
                        status="blocked",
                        limitation=(
                            "optional bound step failed integrity validation"
                        ),
                    )
                observations[step_id] = observation
                if observation.status == "blocked":
                    selection_error = observation.limitation or "bound step blocked"
                    break
        selected.extend(optional_selected)
        task = _seal_analysis_task(
            plan=plan,
            gateway=gateway,
            observations=observations,
            binding=binding,
            runtime_failure=selection_error,
        )
        outcome_traces = _outcome_traces(
            selected=tuple(selected),
            observations=observations,
        )
        if selection_error is not None or task.answer_status is not QueryStatus.OK:
            status = task.answer_status or QueryStatus.BLOCKED
            bundle = _seal_bundle(
                task=task,
                plan=plan,
                gateway=gateway,
                binding=binding,
                status=status,
            )
            return task, bundle, _outcome(
                bundle=bundle,
                records=records,
                traces=outcome_traces,
                failure_reason=selection_error or "",
            )

    optional_tool_messages = [
        ToolMessage(
            content=json.dumps(
                observations[step_id].model_dump(mode="json"),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ),
            tool_call_id=call_id,
            name="execute_bound_query_step",
        )
        for call_id, step_id in optional_selected
    ]
    required_observations = [
        observations[step.step_id].model_dump(mode="json")
        for step in plan.steps
        if step.required
    ]
    final_messages = [
        base_messages[0],
        base_messages[-1],
        HumanMessage(
            content=(
                "PREFLIGHT_REQUIRED_OBSERVATIONS:"
                + json.dumps(
                    required_observations,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                )
                + "\n"
                f"SEALED_CASE_ANALYSIS_TASK:{task.task_id}\n"
                f"TASK_CHECKSUM:{task.payload_checksum}\n"
                "Return the strict answer JSON now."
            )
        ),
    ]
    if selection_message is not None:
        final_messages[2:2] = [
            selection_message,
            *optional_tool_messages,
        ]
    final_turn = model.invoke(final_messages, phase="final_answer")
    records.append(_sanitized_record(final_turn.record))
    failure_reason = _synthesis_error(
        turn_message=final_turn.message,
        record=final_turn.record,
    )
    statements: tuple[AnswerStatement, ...] = ()
    limitations: tuple[str, ...] = ()
    if failure_reason is None:
        try:
            assert final_turn.message is not None
            statements, limitations = _parse_answer(
                task=task,
                message=final_turn.message,
                observations=tuple(observations.values()),
            )
        except ValueError as exc:
            failure_reason = str(exc)

    final_status = QueryStatus.BLOCKED if failure_reason else QueryStatus.OK
    bundle = _seal_bundle(
        task=task,
        plan=plan,
        gateway=gateway,
        binding=binding,
        status=final_status,
        statements=statements if not failure_reason else (),
        extra_limitations=limitations if not failure_reason else (),
    )
    return task, bundle, _outcome(
        bundle=bundle,
        records=records[:MAX_CASE_ANALYSIS_MODEL_CALLS],
        traces=outcome_traces,
        failure_reason=sanitize_text(failure_reason or ""),
    )


def _stable_json_bytes(payload: Any) -> bytes:
    return (
        json.dumps(
            payload,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _expected_outcome_status(bundle: QueryEvidenceBundle) -> str:
    return {
        QueryStatus.OK: "ok",
        QueryStatus.INSUFFICIENT: "insufficient",
        QueryStatus.BLOCKED: "blocked",
        QueryStatus.UNSUPPORTED: "insufficient",
    }[bundle.answer_status]


def _expected_outcome_answer(bundle: QueryEvidenceBundle) -> str:
    answer_parts = [statement.text for statement in bundle.answer_statements]
    answer_parts.extend(bundle.limitations)
    if not answer_parts and bundle.answer_status in {
        QueryStatus.INSUFFICIENT,
        QueryStatus.UNSUPPORTED,
    }:
        answer_parts.append("Insufficient graph evidence.")
    return " ".join(answer_parts)


def _validate_analysis_artifact_binding(
    *,
    root: Path,
    task: CaseAnalysisTask,
    bundle: QueryEvidenceBundle,
    outcome: QueryToolOutcome,
) -> None:
    """Fail closed unless the destination and all three artifact layers agree."""

    try:
        store = QueryGraphStore(root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise RuntimeError(
            "analysis destination is not a validated current run"
        ) from exc
    destination_run_id = str(store.manifest["run_id"])
    if root.name != destination_run_id or not (
        destination_run_id == task.run_id == bundle.run_id
    ):
        raise RuntimeError(
            "analysis destination run_id differs from artifact run"
        )

    try:
        validated_task = CaseAnalysisTask.model_validate(
            task.model_dump(mode="python")
        )
        validated_bundle = QueryEvidenceBundle.model_validate(
            bundle.model_dump(mode="python")
        )
        validated_outcome = QueryToolOutcome.model_validate(
            outcome.model_dump(mode="python")
        )
    except Exception as exc:
        raise RuntimeError("analysis artifact binding is invalid") from exc
    if (
        validated_task != task
        or validated_bundle != bundle
        or validated_outcome != outcome
    ):
        raise RuntimeError("analysis artifact binding is invalid")

    if any(
        (
            bundle.task_id != task.task_id,
            bundle.task_payload_checksum != task.payload_checksum,
            bundle.answer_contract_id != task.answer_contract_id,
            bundle.executed_step_ids != task.executed_bound_step_ids,
            bool(bundle.unexecuted_required_step_ids),
            bundle.component_layer_results != task.component_layer_results,
            bundle.retrieved_fact_ids != task.retrieved_fact_ids,
            bundle.retrieved_derivation_ids != task.retrieved_derivation_ids,
            bundle.retrieved_profile_gap_ids != task.retrieved_profile_gap_ids,
            bundle.retrieved_assessment_ids != task.retrieved_assessment_ids,
            bundle.retrieved_source_ids != task.retrieved_source_ids,
            bundle.source_snapshot_bindings != task.source_snapshot_bindings,
        )
    ):
        raise RuntimeError("analysis artifact binding is incoherent")

    if any(
        (
            outcome.analysis_artifact_dir is not None,
            outcome.status != _expected_outcome_status(bundle),
            outcome.answer != _expected_outcome_answer(bundle),
            tuple(outcome.source_ids) != bundle.retrieved_source_ids,
            tuple(outcome.retrieved_fact_ids) != bundle.retrieved_fact_ids,
            tuple(outcome.retrieved_profile_gap_ids)
            != bundle.retrieved_profile_gap_ids,
            tuple(outcome.retrieved_derivation_ids)
            != bundle.retrieved_derivation_ids,
            bool(outcome.retrieved_context_association_ids),
            bool(outcome.retrieved_outcome_summary_ids),
            bool(outcome.retrieved_observation_ids),
            len(outcome.model_calls) > MAX_CASE_ANALYSIS_MODEL_CALLS,
            len(outcome.tool_calls) > MAX_CASE_ANALYSIS_BOUND_STEPS,
        )
    ):
        raise RuntimeError("analysis artifact binding is incoherent")

    traced_step_ids: list[str] = []
    traced_fact_ids: set[str] = set()
    traced_derivation_ids: set[str] = set()
    traced_source_ids: set[str] = set()
    for trace in outcome.tool_calls:
        step_id = trace.arguments.get("step_id")
        if any(
            (
                trace.tool != "execute_bound_query_step",
                set(trace.arguments) != {"step_id"},
                not isinstance(step_id, str),
                step_id not in bundle.executed_step_ids,
                bool(trace.context_association_ids),
                bool(trace.outcome_summary_ids),
                bool(trace.observation_ids),
                not set(trace.result_refs).issubset(bundle.retrieved_fact_ids),
                not set(trace.derivation_ids).issubset(
                    bundle.retrieved_derivation_ids
                ),
                not set(trace.source_ids).issubset(bundle.retrieved_source_ids),
                trace.status == "ok" and trace.error is not None,
                trace.status != "ok" and not trace.error,
            )
        ):
            raise RuntimeError("analysis artifact binding is incoherent")
        traced_step_ids.append(step_id)
        traced_fact_ids.update(trace.result_refs)
        traced_derivation_ids.update(trace.derivation_ids)
        traced_source_ids.update(trace.source_ids)
    if any(
        (
            tuple(traced_step_ids) != bundle.executed_step_ids,
            traced_fact_ids != set(bundle.retrieved_fact_ids),
            traced_derivation_ids != set(bundle.retrieved_derivation_ids),
            traced_source_ids != set(bundle.retrieved_source_ids),
        )
    ):
        raise RuntimeError("analysis artifact binding is incoherent")


def _sanitized_outcome_payload(
    *,
    task: CaseAnalysisTask,
    outcome: QueryToolOutcome,
) -> dict[str, Any]:
    """Persist stable audit metadata without provider prose or hidden reasoning."""

    return {
        "status": outcome.status,
        "answer": outcome.answer,
        "source_ids": outcome.source_ids,
        "retrieved_fact_ids": outcome.retrieved_fact_ids,
        "retrieved_profile_gap_ids": outcome.retrieved_profile_gap_ids,
        "retrieved_derivation_ids": outcome.retrieved_derivation_ids,
        "failure_reason": "analysis_failed" if outcome.failure_reason else "",
        "model_calls": [
            {
                "agent": "decision_case_analysis",
                "call_index": record_index,
                "status": "error" if record.error else "ok",
                "tool_calls": [
                    {
                        "call_id": f"redacted:{call_index}",
                        "name": (
                            "execute_bound_query_step"
                            if call.name == "execute_bound_query_step"
                            else "unrecognized_tool"
                        ),
                        **(
                            {"step_id": call.arguments["step_id"]}
                            if call.name == "execute_bound_query_step"
                            and set(call.arguments) == {"step_id"}
                            and isinstance(call.arguments.get("step_id"), str)
                            and call.arguments["step_id"]
                            in task.available_bound_step_ids
                            else {}
                        ),
                    }
                    for call_index, call in enumerate(
                        record.tool_calls[:MAX_CASE_ANALYSIS_BOUND_STEPS],
                        start=1,
                    )
                ],
            }
            for record_index, record in enumerate(
                outcome.model_calls,
                start=1,
            )
        ],
        "tool_calls": [
            {
                "tool_call_id": f"trace:{trace_index}",
                "tool": "execute_bound_query_step",
                "step_id": trace.arguments["step_id"],
                "result_refs": trace.result_refs,
                "derivation_ids": trace.derivation_ids,
                "source_ids": trace.source_ids,
                "status": trace.status,
                "error": "bound_step_failed" if trace.error else None,
            }
            for trace_index, trace in enumerate(
                outcome.tool_calls,
                start=1,
            )
        ],
    }


def write_case_analysis_artifacts(
    *,
    run_dir: Path,
    task: CaseAnalysisTask,
    bundle: QueryEvidenceBundle,
    outcome: QueryToolOutcome,
) -> Path:
    """Write one immutable, idempotent per-analysis artifact directory."""

    try:
        root = Path(run_dir).resolve(strict=True)
    except OSError as exc:
        raise RuntimeError(
            "analysis destination is not a validated current run"
        ) from exc
    _validate_analysis_artifact_binding(
        root=root,
        task=task,
        bundle=bundle,
        outcome=outcome,
    )
    sanitized_outcome = _sanitized_outcome_payload(
        task=task,
        outcome=outcome,
    )
    outcome_checksum = hashlib.sha256(
        _stable_json_bytes(sanitized_outcome)
    ).hexdigest()
    analysis_run_id = stable_contract_id(
        "analysis-run",
        task.payload_checksum,
        bundle.payload_checksum,
        outcome_checksum,
    )
    analysis_root = root / "analysis"
    if analysis_root.is_symlink():
        raise RuntimeError("symlinked analysis root is not allowed")
    analysis_root.mkdir(parents=True, exist_ok=True)
    resolved_analysis_root = analysis_root.resolve(strict=True)
    if (
        analysis_root.is_symlink()
        or not resolved_analysis_root.is_relative_to(root)
    ):
        raise RuntimeError("analysis artifact path escaped the resolved run")
    target = analysis_root / analysis_run_id
    if target.is_symlink():
        raise RuntimeError("symlinked analysis artifact target is not allowed")
    resolved_target = target.resolve()
    if (
        not resolved_target.is_relative_to(root)
        or resolved_target.parent != resolved_analysis_root
    ):
        raise RuntimeError("analysis artifact path escaped the resolved run")

    run_payload = {
        "analysis_run_id": analysis_run_id,
        "task_id": task.task_id,
        "task_payload_checksum": task.payload_checksum,
        "query_id": bundle.query_id,
        "query_payload_checksum": bundle.payload_checksum,
        "outcome": sanitized_outcome,
    }
    expected = {
        "case_analysis_task.json": _stable_json_bytes(
            task.model_dump(mode="json")
        ),
        "query_evidence_bundle.json": _stable_json_bytes(
            bundle.model_dump(mode="json")
        ),
        "case_analysis_run.json": _stable_json_bytes(run_payload),
    }
    if target.exists():
        current_names = {path.name for path in target.iterdir()}
        if current_names != set(expected):
            raise RuntimeError("immutable analysis artifact conflict")
        for name, content in expected.items():
            current_path = target / name
            if (
                current_path.is_symlink()
                or not current_path.is_file()
                or not current_path.resolve().is_relative_to(target)
                or current_path.read_bytes() != content
            ):
                raise RuntimeError("immutable analysis artifact conflict")
        return target

    target.mkdir()
    for name, content in expected.items():
        artifact_path = target / name
        if artifact_path.exists() or artifact_path.is_symlink():
            raise RuntimeError("immutable analysis artifact conflict")
        artifact_path.write_bytes(content)
    return target
