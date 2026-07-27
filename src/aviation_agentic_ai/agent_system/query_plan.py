"""Immutable, registered query plans for Decision Case Analysis."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from aviation_agentic_ai.agent_system.decision_case_contracts import (
    DECISION_CASE_CONTRACT_VERSION,
    ChecksummedContract,
    ContractExecutionBinding,
    FrozenContractModel,
    canonical_id_tuple_token,
    canonical_payload_bytes,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.query_tools import QueryGraphStore


class AnalysisIntent(str, Enum):
    """The only analysis question families that may receive a bound plan."""

    EPISODE = "episode"
    OPERATIONAL_SITUATION = "operational_situation"
    APPLICABILITY_AND_IMPACT = "applicability_and_impact"
    HISTORICAL_SIMILARITY = "historical_similarity"


BoundOperation = Literal[
    "read_episode_timeline",
    "read_operational_situation",
    "read_applicability",
    "read_observed_flight_outcome",
    "read_similarity_corpus_gate",
]

_OPERATIONS_BY_INTENT: dict[AnalysisIntent, tuple[BoundOperation, ...]] = {
    AnalysisIntent.EPISODE: ("read_episode_timeline",),
    AnalysisIntent.OPERATIONAL_SITUATION: ("read_operational_situation",),
    AnalysisIntent.APPLICABILITY_AND_IMPACT: (
        "read_applicability",
        "read_observed_flight_outcome",
    ),
    AnalysisIntent.HISTORICAL_SIMILARITY: ("read_similarity_corpus_gate",),
}

_EVIDENCE_LAYERS_BY_OPERATION: dict[BoundOperation, tuple[str, ...]] = {
    "read_episode_timeline": ("formal",),
    "read_operational_situation": (
        "formal",
        "non_causal_weather_context",
        "bts_reported_public_observation",
    ),
    "read_applicability": ("formal",),
    "read_observed_flight_outcome": ("observed_flight_outcome",),
    "read_similarity_corpus_gate": ("approved_similarity_corpus",),
}

_REGISTERED_ANALYSIS_QUESTIONS: dict[str, AnalysisIntent] = {
    "what decision episode is recorded": AnalysisIntent.EPISODE,
    "what public operational situation is recorded": (
        AnalysisIntent.OPERATIONAL_SITUATION
    ),
    "what applicability and observed flight impact are recorded": (
        AnalysisIntent.APPLICABILITY_AND_IMPACT
    ),
    "which historical case is most similar": AnalysisIntent.HISTORICAL_SIMILARITY,
}


def registered_evidence_layers(operation: BoundOperation) -> tuple[str, ...]:
    """Return the complete evidence contract for one closed operation."""

    return _EVIDENCE_LAYERS_BY_OPERATION[operation]


def validate_registered_evidence_layers(step: "BoundQueryStep") -> None:
    """Reject an operation whose declared evidence contract was altered."""

    expected = registered_evidence_layers(step.operation)
    if step.allowed_evidence_layers != expected:
        raise ValueError(
            "step evidence layers do not match the registered operation"
        )


def _validate_nonempty_unique(values: tuple[str, ...], field_name: str) -> None:
    if not values or any(not value for value in values):
        raise ValueError(f"{field_name} must contain nonempty IDs")
    if len(set(values)) != len(values):
        raise ValueError(f"{field_name} contains duplicate IDs")


class BoundQueryStep(FrozenContractModel):
    """One fixed read operation scoped to already registered event IDs."""

    step_id: str = Field(min_length=1)
    operation: BoundOperation
    event_ids: tuple[str, ...]
    required: bool
    allowed_evidence_layers: tuple[str, ...]

    @model_validator(mode="after")
    def validate_bound_step(self) -> Self:
        _validate_nonempty_unique(self.event_ids, "event_ids")
        _validate_nonempty_unique(
            self.allowed_evidence_layers,
            "allowed_evidence_layers",
        )
        validate_registered_evidence_layers(self)
        return self


class QueryPlanFields(FrozenContractModel):
    """Checksum-covered fields used to seal one immutable query plan."""

    query_plan_id: str
    run_id: str
    question: str
    intent_family: AnalysisIntent
    event_or_case_scope: tuple[str, ...]
    steps: tuple[BoundQueryStep, ...]
    max_steps: Literal[3] = 3


class QueryPlan(ChecksummedContract):
    """A sealed list of registered reads, never a generic retrieval program."""

    query_plan_id: str
    run_id: str
    question: str
    intent_family: AnalysisIntent
    event_or_case_scope: tuple[str, ...]
    steps: tuple[BoundQueryStep, ...]
    max_steps: Literal[3] = 3

    @model_validator(mode="after")
    def validate_query_plan(self) -> Self:
        if not self.run_id:
            raise ValueError("run_id must be nonempty")
        if not self.question.strip():
            raise ValueError("question must be nonempty")
        _validate_nonempty_unique(
            self.event_or_case_scope,
            "event_or_case_scope",
        )
        if len(self.steps) > self.max_steps:
            raise ValueError("query plan exceeds max_steps")
        if not self.steps:
            raise ValueError("query plan must contain a bound step")
        step_ids = tuple(step.step_id for step in self.steps)
        if len(set(step_ids)) != len(step_ids):
            raise ValueError("query plan contains duplicate step IDs")
        allowed_operations = set(_OPERATIONS_BY_INTENT[self.intent_family])
        scope = set(self.event_or_case_scope)
        for step in self.steps:
            if step.operation not in allowed_operations:
                raise ValueError("step operation is not registered for intent")
            validate_registered_evidence_layers(step)
            if not set(step.event_ids).issubset(scope):
                raise ValueError("step event IDs are outside event_or_case_scope")
        if _registered_intent(self.question) is not self.intent_family:
            raise ValueError("question does not match the registered analysis intent")
        if (
            self.intent_family is not AnalysisIntent.HISTORICAL_SIMILARITY
            and len(self.event_or_case_scope) != 1
        ):
            raise ValueError("non-similarity plan requires exactly one event")
        if self.steps != _plan_steps(
            intent=self.intent_family,
            event_ids=self.event_or_case_scope,
        ):
            raise ValueError("query plan steps must equal the exact registered sequence")
        expected = _query_plan_id(
            run_id=self.run_id,
            question=self.question,
            intent_family=self.intent_family,
            event_or_case_scope=self.event_or_case_scope,
            steps=self.steps,
        )
        if self.query_plan_id != expected:
            raise ValueError("query plan_id is not stable")
        return self


def _step_token(steps: tuple[BoundQueryStep, ...]) -> str:
    return json.dumps(
        [step.model_dump(mode="json") for step in steps],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _query_plan_id(
    *,
    run_id: str,
    question: str,
    intent_family: AnalysisIntent,
    event_or_case_scope: tuple[str, ...],
    steps: tuple[BoundQueryStep, ...],
) -> str:
    return stable_contract_id(
        "query-plan",
        run_id,
        question,
        intent_family.value,
        canonical_id_tuple_token(event_or_case_scope, sort_values=False),
        _step_token(steps),
    )


def _registered_intent(question: str) -> AnalysisIntent:
    normalized = " ".join(
        token
        for token in "".join(
            character.lower() if character.isalnum() else " "
            for character in question
        ).split()
    )
    try:
        return _REGISTERED_ANALYSIS_QUESTIONS[normalized]
    except KeyError as exc:
        raise ValueError("question is not an exact registered analysis question") from exc


def _run_id(store: QueryGraphStore) -> str:
    run_id = store.manifest.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("current query store has no run_id")
    return run_id


def _plan_steps(
    *,
    intent: AnalysisIntent,
    event_ids: tuple[str, ...],
) -> tuple[BoundQueryStep, ...]:
    return tuple(
        BoundQueryStep(
            step_id=f"step:{intent.value}:{index}",
            operation=operation,
            event_ids=event_ids,
            required=True,
            allowed_evidence_layers=_EVIDENCE_LAYERS_BY_OPERATION[operation],
        )
        for index, operation in enumerate(_OPERATIONS_BY_INTENT[intent], start=1)
    )


def _seal_query_plan(fields: QueryPlanFields) -> QueryPlan:
    binding = ContractExecutionBinding(
        run_id=fields.run_id,
        created_at=datetime(1970, 1, 1, tzinfo=UTC),
        tool_version="bounded-query-plan-v1",
    )
    payload_bytes = canonical_payload_bytes(QueryPlan, fields, binding)
    payload = fields.model_dump(mode="python")
    payload.update(
        {
            "contract_version": DECISION_CASE_CONTRACT_VERSION,
            "payload_checksum": hashlib.sha256(payload_bytes).hexdigest(),
            "created_at": binding.created_at,
            "prompt_version": binding.prompt_version,
            "tool_version": binding.tool_version,
        }
    )
    return QueryPlan.model_validate(payload)


def compile_query_plan(
    *,
    run_dir: Path,
    question: str,
    event_id: str | None = None,
    store: QueryGraphStore,
) -> QueryPlan:
    """Compile one registered question into an immutable, closed plan."""

    if Path(run_dir).resolve() != store.run_dir.resolve():
        raise ValueError("run_dir must match the current query store")
    intent = _registered_intent(question)
    current_event_ids = tuple(store.event_ids)
    _validate_nonempty_unique(current_event_ids, "event_or_case_scope")
    if intent is AnalysisIntent.HISTORICAL_SIMILARITY:
        if event_id is not None:
            raise ValueError("similarity plan binds the current corpus, not event_id")
        event_ids = current_event_ids
    else:
        if event_id is None:
            if len(current_event_ids) != 1:
                raise ValueError(
                    "non-similarity plan requires an explicit event_id for a "
                    "multi-event store"
                )
            event_id = current_event_ids[0]
        if event_id not in current_event_ids:
            raise ValueError("event_id is outside the current query store")
        event_ids = (event_id,)
    steps = _plan_steps(intent=intent, event_ids=event_ids)
    run_id = _run_id(store)
    return _seal_query_plan(
        QueryPlanFields(
            query_plan_id=_query_plan_id(
                run_id=run_id,
                question=question,
                intent_family=intent,
                event_or_case_scope=event_ids,
                steps=steps,
            ),
            run_id=run_id,
            question=question,
            intent_family=intent,
            event_or_case_scope=event_ids,
            steps=steps,
        )
    )
