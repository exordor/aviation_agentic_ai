"""Tests for the sealed, read-only Decision Case Analysis gateway."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from aviation_agentic_ai.agent_system.query_plan import (
    BoundQueryStep,
    QueryPlan,
    compile_query_plan,
)
from aviation_agentic_ai.agent_system.query_tools import QueryGraphStore


EVENT_ID = "urn:aviation-agentic-ai:event:bound-query"
SOURCE_ID = "source:advisory:bound-query"


@pytest.fixture
def store() -> QueryGraphStore:
    """A current-store view containing one already validated event."""

    view = object.__new__(QueryGraphStore)
    view.run_dir = Path("/tmp/bound-query-run")
    view.manifest = {"run_id": "bound-query-run"}
    view.event_ids = [EVENT_ID]
    view.rows = [
        {
            "fact_id": "fact:type",
            "subject": EVENT_ID,
            "predicate": "rdf:type",
            "object": "atm:GroundStopTMI",
            "source_ids": [SOURCE_ID],
        },
        {
            "fact_id": "fact:facility",
            "subject": EVENT_ID,
            "predicate": "atm:controlledNASelement",
            "object": "urn:aviation-agentic-ai:facility:airport:KJFK",
            "source_ids": [SOURCE_ID],
        },
    ]
    view.fact_by_id = {row["fact_id"]: row for row in view.rows}
    return view


def test_gateway_executes_only_a_declared_step_once(
    store: QueryGraphStore,
) -> None:
    """Removing the one-use guard would allow the same bound read twice."""

    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        BoundQueryGateway,
    )

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    gateway = BoundQueryGateway(plan=plan, store=store)
    step_id = plan.steps[0].step_id

    assert gateway.execute_bound_query_step(step_id=step_id).status == "ok"
    assert gateway.execute_bound_query_step(step_id=step_id).status == "blocked"
    assert (
        gateway.execute_bound_query_step(step_id="step:not-bound").status
        == "blocked"
    )


def test_compiled_plan_has_a_stable_canonical_id_and_checksum(
    store: QueryGraphStore,
) -> None:
    """Changing plan inputs must change its sealed canonical representation."""

    question = "What public operational situation is recorded?"
    first = compile_query_plan(
        run_dir=store.run_dir,
        question=question,
        store=store,
    )
    second = compile_query_plan(
        run_dir=store.run_dir,
        question=question,
        store=store,
    )

    assert first.query_plan_id.startswith("query-plan:")
    assert second.query_plan_id == first.query_plan_id
    assert second.payload_checksum == first.payload_checksum

    with pytest.raises(ValidationError, match="query plan_id is not stable"):
        QueryPlan.model_validate(
            {
                **first.model_dump(mode="python"),
                "query_plan_id": "query-plan:foreign",
            },
            context={"skip_payload_checksum": True},
        )


def test_compiled_plan_cannot_be_mutated_after_sealing(
    store: QueryGraphStore,
) -> None:
    """Mutating a nested step would invalidate an otherwise sealed plan."""

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )

    with pytest.raises(ValidationError):
        plan.steps[0].step_id = "step:mutated"


def test_query_plan_rejects_duplicate_steps_and_foreign_event_scope(
    store: QueryGraphStore,
) -> None:
    """A plan may not widen its precomputed event scope by malformed steps."""

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    duplicate_step = BoundQueryStep(
        step_id=plan.steps[0].step_id,
        operation=plan.steps[0].operation,
        event_ids=plan.steps[0].event_ids,
        required=plan.steps[0].required,
        allowed_evidence_layers=plan.steps[0].allowed_evidence_layers,
    )
    with pytest.raises(ValidationError, match="duplicate step IDs"):
        QueryPlan.model_validate(
            {
                **plan.model_dump(mode="python"),
                "steps": (plan.steps[0], duplicate_step),
            },
            context={"skip_payload_checksum": True},
        )

    foreign_step = BoundQueryStep(
        step_id="step:foreign",
        operation=plan.steps[0].operation,
        event_ids=("urn:aviation-agentic-ai:event:foreign",),
        required=True,
        allowed_evidence_layers=("formal",),
    )
    with pytest.raises(ValidationError, match="outside event_or_case_scope"):
        QueryPlan.model_validate(
            {
                **plan.model_dump(mode="python"),
                "steps": (foreign_step,),
            },
            context={"skip_payload_checksum": True},
        )


def test_gateway_observation_cites_only_current_store_sources(
    store: QueryGraphStore,
) -> None:
    """A gateway result cannot cite data outside the current store view."""

    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        BoundQueryGateway,
    )

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    observation = BoundQueryGateway(plan=plan, store=store).execute_bound_query_step(
        step_id=plan.steps[0].step_id
    )

    source_ids_in_store = {
        source_id for row in store.rows for source_id in row["source_ids"]
    }
    assert observation.status == "ok"
    assert set(observation.source_ids).issubset(source_ids_in_store)
    assert set(observation.fact_ids).issubset(store.fact_by_id)
    assert {
        source_id
        for item in observation.items
        for source_id in item["source_ids"]
    }.issubset(source_ids_in_store)
