"""Read-only execution gateway for sealed Decision Case Analysis plans."""

from __future__ import annotations

from typing import Any, Literal

from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    QueryToolTrace,
    canonical_id_tuple_token,
    stable_contract_id,
)
from aviation_agentic_ai.agent_system.query_plan import (
    BoundQueryStep,
    QueryPlan,
    validate_registered_evidence_layers,
)
from aviation_agentic_ai.agent_system.query_context_store import (
    QueryContextError,
    QueryContextStore,
)
from aviation_agentic_ai.agent_system.query_tools import QueryGraphStore


class BoundQueryObservation(StrictModel):
    """One validated, source-bounded result of an allowed plan step."""

    step_id: str
    status: Literal["ok", "partial", "insufficient", "blocked"]
    fact_ids: tuple[str, ...] = ()
    derivation_ids: tuple[str, ...] = ()
    profile_gap_ids: tuple[str, ...] = ()
    assessment_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    items: tuple[dict[str, Any], ...] = ()
    limitation: str = ""


def _rows_for_step(
    *,
    step: BoundQueryStep,
    store: QueryGraphStore,
) -> tuple[dict[str, Any], ...]:
    return tuple(
        sorted(
            (
                row
                for row in store.rows
                if row["subject"] in step.event_ids
            ),
            key=lambda row: str(row["fact_id"]),
        )
    )


def _item_for_fact(row: dict[str, Any]) -> dict[str, Any]:
    """Project exactly the fields a D1 formal-row observation may expose."""

    return {
        "fact_id": str(row["fact_id"]),
        "subject": str(row["subject"]),
        "predicate": str(row["predicate"]),
        "object": row.get("object"),
        "source_ids": tuple(row["source_ids"]),
    }


def _formal_observation(
    *,
    step: BoundQueryStep,
    store: QueryGraphStore,
    status: Literal["ok", "partial"],
    limitation: str = "",
) -> BoundQueryObservation:
    rows = _rows_for_step(step=step, store=store)
    if not rows:
        return BoundQueryObservation(
            step_id=step.step_id,
            status="insufficient",
            limitation="no formal event facts in the bound scope",
        )
    source_ids = tuple(
        sorted({source_id for row in rows for source_id in row["source_ids"]})
    )
    return BoundQueryObservation(
        step_id=step.step_id,
        status=status,
        fact_ids=tuple(str(row["fact_id"]) for row in rows),
        source_ids=source_ids,
        items=tuple(_item_for_fact(row) for row in rows),
        limitation=limitation,
    )


def _formal_item(row: dict[str, Any]) -> dict[str, Any]:
    return {"evidence_role": "formal_event_fact", **_item_for_fact(row)}


def read_episode_timeline(
    store: QueryGraphStore,
    *,
    event_id: str,
    step_id: str = "episode-timeline",
) -> BoundQueryObservation:
    """Return the record-level timeline without inferring a lifecycle episode."""

    read = QueryContextStore(
        store.run_dir,
        graph_store=store,
    ).get_episode_timeline(event_id)
    return BoundQueryObservation(
        step_id=step_id,
        status=read.status,
        fact_ids=tuple(str(row["fact_id"]) for row in read.formal_fact_rows),
        source_ids=read.source_ids,
        items=tuple(_formal_item(row) for row in read.formal_fact_rows),
        limitation=read.limitation,
    )


def read_operational_situation(
    store: QueryGraphStore,
    *,
    event_id: str,
    step_id: str = "operational-situation",
) -> BoundQueryObservation:
    """Return source-qualified current-run evidence without operational causation."""

    try:
        read = QueryContextStore(
            store.run_dir,
            graph_store=store,
        ).get_operational_situation(event_id)
    except QueryContextError:
        return BoundQueryObservation(
            step_id=step_id,
            status="insufficient",
            limitation="missing evidence layer: active BTS observation",
        )
    bts_fact_ids = tuple(
        fact_id
        for observation in read.public_observations
        for fact_id in observation.fact_ids
    )
    return BoundQueryObservation(
        step_id=step_id,
        status=read.status,
        fact_ids=tuple(
            str(row["fact_id"]) for row in read.formal_fact_rows
        )
        + bts_fact_ids,
        derivation_ids=tuple(
            observation.derivation_id for observation in read.public_observations
        ),
        source_ids=read.source_ids,
        items=tuple(_formal_item(row) for row in read.formal_fact_rows)
        + tuple(
            {
                "evidence_role": "non_causal_weather_context",
                **association.model_dump(mode="json"),
            }
            for association in read.weather_associations
        )
        + tuple(
            {
                "evidence_role": "bts_reported_public_observation",
                "causal_claim": False,
                **observation.model_dump(mode="json"),
            }
            for observation in read.public_observations
        ),
        limitation=read.limitation,
    )


def _execute_registered_step(
    *,
    step: BoundQueryStep,
    store: QueryGraphStore,
) -> BoundQueryObservation:
    """Execute the fixed operation set without generic retrieval input."""

    if step.operation == "read_episode_timeline":
        return read_episode_timeline(
            store,
            event_id=step.event_ids[0],
            step_id=step.step_id,
        )
    if step.operation == "read_operational_situation":
        return read_operational_situation(
            store,
            event_id=step.event_ids[0],
            step_id=step.step_id,
        )
    if step.operation in {
        "read_applicability",
        "read_observed_flight_outcome",
        "read_similarity_corpus_gate",
    }:
        return BoundQueryObservation(
            step_id=step.step_id,
            status="blocked",
            limitation="registered operation is not available in the D1 gateway",
        )
    raise AssertionError("validated query plan contains an unknown operation")


class BoundQueryGateway:
    """One-use, plan-bound reader over the supplied current graph-store view."""

    def __init__(self, *, plan: QueryPlan, store: QueryGraphStore) -> None:
        store_run_id = store.manifest.get("run_id")
        if plan.run_id != store_run_id:
            raise ValueError("query plan run_id does not match the current store")
        if not set(plan.event_or_case_scope).issubset(store.event_ids):
            raise ValueError("query plan scope is outside the current store")
        for step in plan.steps:
            validate_registered_evidence_layers(step)
            if not set(step.event_ids).issubset(plan.event_or_case_scope):
                raise ValueError("query plan step scope is outside the plan scope")
        self._store = store
        self._steps_by_id = {step.step_id: step for step in plan.steps}
        self._plan = plan
        self._executed: set[str] = set()
        self._traces: list[QueryToolTrace] = []

    @property
    def traces(self) -> tuple[QueryToolTrace, ...]:
        """Validated, identifier-only traces in successful execution order."""

        return tuple(self._traces)

    def execute_bound_query_step(self, *, step_id: str) -> BoundQueryObservation:
        if step_id in self._executed:
            return BoundQueryObservation(
                step_id=step_id,
                status="blocked",
                limitation="bound step already executed",
            )
        step = self._steps_by_id.get(step_id)
        if step is None:
            return BoundQueryObservation(
                step_id=step_id,
                status="blocked",
                limitation="step is not bound by query plan",
            )
        self._executed.add(step_id)
        observation = _execute_registered_step(step=step, store=self._store)
        self._validate_observation(step=step, observation=observation)
        self._traces.append(
            QueryToolTrace(
                trace_id=stable_contract_id(
                    "query-tool-trace",
                    self._plan.query_plan_id,
                    step.step_id,
                    step.operation,
                    observation.status,
                    canonical_id_tuple_token(observation.fact_ids, sort_values=True),
                    canonical_id_tuple_token(
                        observation.derivation_ids,
                        sort_values=True,
                    ),
                    canonical_id_tuple_token(
                        observation.profile_gap_ids,
                        sort_values=True,
                    ),
                    canonical_id_tuple_token(
                        observation.assessment_ids,
                        sort_values=True,
                    ),
                    canonical_id_tuple_token(observation.source_ids, sort_values=True),
                ),
                query_plan_id=self._plan.query_plan_id,
                step_id=step.step_id,
                operation=step.operation,
                observation_status=observation.status,
                fact_ids=tuple(sorted(observation.fact_ids)),
                derivation_ids=tuple(sorted(observation.derivation_ids)),
                profile_gap_ids=tuple(sorted(observation.profile_gap_ids)),
                assessment_ids=tuple(sorted(observation.assessment_ids)),
                source_ids=tuple(sorted(observation.source_ids)),
            )
        )
        return observation

    def _validate_observation(
        self,
        *,
        step: BoundQueryStep,
        observation: BoundQueryObservation,
    ) -> None:
        if observation.step_id != step.step_id:
            raise ValueError("bound observation step_id differs from executing step")
        if step.operation == "read_episode_timeline":
            expected = read_episode_timeline(
                self._store,
                event_id=step.event_ids[0],
                step_id=step.step_id,
            )
            if observation != expected:
                raise ValueError("episode observation does not match current store")
            return
        if step.operation == "read_operational_situation":
            if (self._store.run_dir / "run_manifest.json").is_file():
                expected = read_operational_situation(
                    self._store,
                    event_id=step.event_ids[0],
                    step_id=step.step_id,
                )
                if observation != expected:
                    raise ValueError(
                        "operational situation observation does not match current store"
                    )
                return
        if len(set(observation.fact_ids)) != len(observation.fact_ids):
            raise ValueError("bound observation contains duplicate fact IDs")
        if not set(observation.fact_ids).issubset(self._store.fact_by_id):
            raise ValueError("bound observation cites a fact outside the current store")
        cited_rows = tuple(
            self._store.fact_by_id[fact_id] for fact_id in observation.fact_ids
        )
        if any(row["subject"] not in step.event_ids for row in cited_rows):
            raise ValueError("bound observation cites a fact outside the bound step scope")
        expected_source_ids = tuple(
            sorted(
                {
                    source_id
                    for row in cited_rows
                    for source_id in row["source_ids"]
                }
            )
        )
        if observation.source_ids != expected_source_ids:
            raise ValueError(
                "bound observation sources are not bound to cited facts"
            )
        expected_items = tuple(_item_for_fact(row) for row in cited_rows)
        if observation.items != expected_items:
            raise ValueError("bound observation item does not match its cited fact")
