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

    assert (
        gateway.execute_bound_query_step(step_id=step_id).status == "insufficient"
    )
    assert gateway.execute_bound_query_step(step_id=step_id).status == "blocked"
    assert (
        gateway.execute_bound_query_step(step_id="step:not-bound").status
        == "blocked"
    )


def test_gateway_refuses_a_no_manifest_operational_situation(
    store: QueryGraphStore,
) -> None:
    """Removing the D2 context gate must not expose formal-only status=ok."""

    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        BoundQueryGateway,
    )

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )

    result = BoundQueryGateway(plan=plan, store=store).execute_bound_query_step(
        step_id=plan.steps[0].step_id
    )

    assert result.status == "insufficient"
    assert result.limitation == "missing evidence layer: active BTS observation"


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


def test_query_plan_rejects_evidence_layers_not_registered_for_operation(
    store: QueryGraphStore,
) -> None:
    """An arbitrary layer must not become executable by changing one step."""

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    unregistered_layer_step = plan.steps[0].model_copy(
        update={"allowed_evidence_layers": ("made_up_layer",)}
    )

    with pytest.raises(ValidationError, match="evidence layers"):
        QueryPlan.model_validate(
            {
                **plan.model_dump(mode="python"),
                "steps": (unregistered_layer_step,),
            },
            context={"skip_payload_checksum": True},
        )


def test_gateway_rejects_a_tampered_plan_evidence_layer(
    store: QueryGraphStore,
) -> None:
    """The gateway must repeat layer checks before it dispatches a step."""

    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        BoundQueryGateway,
    )

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    tampered_step = plan.steps[0].model_copy(
        update={"allowed_evidence_layers": ("made_up_layer",)}
    )
    tampered_plan = plan.model_copy(update={"steps": (tampered_step,)})

    with pytest.raises(ValueError, match="sealed query plan"):
        BoundQueryGateway(plan=tampered_plan, store=store)


@pytest.mark.parametrize(
    "update",
    (
        {"payload_checksum": "0" * 64},
        {"query_plan_id": "query-plan:stale"},
        {"question": "What decision episode is recorded?"},
    ),
)
def test_gateway_revalidates_the_complete_sealed_plan(
    store: QueryGraphStore,
    update: dict[str, object],
) -> None:
    """A frozen model_copy must not bypass checksum, ID, or question binding."""

    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        BoundQueryGateway,
    )

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )

    with pytest.raises(ValueError, match="sealed query plan"):
        BoundQueryGateway(plan=plan.model_copy(update=update), store=store)


def test_query_plan_requires_the_exact_registered_step_sequence(
    store: QueryGraphStore,
) -> None:
    """Reordering or making a registered step optional changes the contract."""

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What applicability and observed flight impact are recorded?",
        store=store,
    )
    reversed_steps = tuple(reversed(plan.steps))
    optional_step = plan.steps[0].model_copy(update={"required": False})

    for steps in (reversed_steps, (optional_step, plan.steps[1])):
        with pytest.raises(ValidationError, match="exact registered sequence"):
            QueryPlan.model_validate(
                {**plan.model_dump(mode="python"), "steps": steps},
                context={"skip_payload_checksum": True},
            )


@pytest.mark.parametrize(
    "question",
    (
        "What public operational situation caused this?",
        "What is the live operational situation now?",
        "Please describe the decision episode.",
        "Which operational situation is most similar?",
        "What applicability is recommended?",
    ),
)
def test_compile_query_plan_rejects_nonexact_analysis_questions(
    store: QueryGraphStore,
    question: str,
) -> None:
    """Direct compiler callers must not bypass the router's exact gate."""

    with pytest.raises(ValueError, match="exact registered analysis question"):
        compile_query_plan(
            run_dir=store.run_dir,
            question=question,
            store=store,
        )


def test_non_similarity_plan_requires_one_selected_event(
    store: QueryGraphStore,
) -> None:
    """A multi-event store must not silently select event_ids[0]."""

    second_event_id = "urn:aviation-agentic-ai:event:second"
    store.event_ids.append(second_event_id)

    with pytest.raises(ValueError, match="explicit event_id"):
        compile_query_plan(
            run_dir=store.run_dir,
            question="What public operational situation is recorded?",
            store=store,
        )

    selected = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        event_id=EVENT_ID,
        store=store,
    )
    corpus = compile_query_plan(
        run_dir=store.run_dir,
        question="Which historical case is most similar?",
        store=store,
    )

    assert selected.event_or_case_scope == (EVENT_ID,)
    assert all(step.event_ids == (EVENT_ID,) for step in selected.steps)
    assert corpus.event_or_case_scope == (EVENT_ID, second_event_id)
    assert corpus.steps[0].event_ids == (EVENT_ID, second_event_id)


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
        allowed_evidence_layers=plan.steps[0].allowed_evidence_layers,
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
    """An insufficient result cannot cite data outside the current store view."""

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
    assert observation.status == "insufficient"
    assert observation.fact_ids == ()
    assert observation.source_ids == ()
    assert set(observation.source_ids).issubset(source_ids_in_store)
    assert set(observation.fact_ids).issubset(store.fact_by_id)
    assert {
        source_id
        for item in observation.items
        for source_id in item["source_ids"]
    }.issubset(source_ids_in_store)


def test_gateway_reconstructs_no_manifest_operational_observation(
    store: QueryGraphStore,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A missing manifest must not activate the generic formal-fact fallback."""

    from aviation_agentic_ai.agent_system import case_analysis_tools
    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        BoundQueryGateway,
        BoundQueryObservation,
    )

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    forged = BoundQueryObservation(
        step_id=plan.steps[0].step_id,
        status="ok",
        fact_ids=("fact:type",),
        source_ids=(SOURCE_ID,),
        items=(
            {
                "fact_id": "fact:type",
                "subject": EVENT_ID,
                "predicate": "rdf:type",
                "object": "atm:GroundStopTMI",
                "source_ids": (SOURCE_ID,),
            },
        ),
    )
    monkeypatch.setattr(
        case_analysis_tools,
        "_execute_registered_step",
        lambda **_: forged,
    )

    with pytest.raises(ValueError, match="operational situation observation"):
        BoundQueryGateway(plan=plan, store=store).execute_bound_query_step(
            step_id=plan.steps[0].step_id
        )


def test_gateway_rejects_a_fact_outside_the_executing_step_scope(
    store: QueryGraphStore,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A current-store fact is still forbidden when its event is not bound."""

    from aviation_agentic_ai.agent_system import case_analysis_tools
    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        BoundQueryGateway,
        BoundQueryObservation,
    )

    foreign_event_id = "urn:aviation-agentic-ai:event:foreign"
    foreign_source_id = "source:advisory:foreign"
    foreign_row = {
        "fact_id": "fact:foreign",
        "subject": foreign_event_id,
        "predicate": "rdf:type",
        "object": "atm:GroundStopTMI",
        "source_ids": [foreign_source_id],
    }
    store.rows.append(foreign_row)
    store.fact_by_id["fact:foreign"] = foreign_row
    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    forged = BoundQueryObservation(
        step_id=plan.steps[0].step_id,
        status="ok",
        fact_ids=("fact:foreign",),
        source_ids=(foreign_source_id,),
        items=(
            {
                "fact_id": "fact:foreign",
                "subject": foreign_event_id,
                "predicate": "rdf:type",
                "object": "atm:GroundStopTMI",
                "source_ids": (foreign_source_id,),
            },
        ),
    )
    monkeypatch.setattr(
        case_analysis_tools,
        "_execute_registered_step",
        lambda **_: forged,
    )

    with pytest.raises(ValueError, match="operational situation observation"):
        BoundQueryGateway(plan=plan, store=store).execute_bound_query_step(
            step_id=plan.steps[0].step_id
        )


def test_gateway_rejects_forged_item_content_for_a_cited_fact(
    store: QueryGraphStore,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A cited ID cannot be paired with an altered item projection."""

    from aviation_agentic_ai.agent_system import case_analysis_tools
    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        BoundQueryGateway,
        BoundQueryObservation,
    )

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    forged = BoundQueryObservation(
        step_id=plan.steps[0].step_id,
        status="ok",
        fact_ids=("fact:type",),
        source_ids=(SOURCE_ID,),
        items=(
            {
                "fact_id": "fact:type",
                "subject": EVENT_ID,
                "predicate": "rdf:type",
                "object": "forged-object",
                "source_ids": (SOURCE_ID,),
            },
        ),
    )
    monkeypatch.setattr(
        case_analysis_tools,
        "_execute_registered_step",
        lambda **_: forged,
    )

    with pytest.raises(ValueError, match="operational situation observation"):
        BoundQueryGateway(plan=plan, store=store).execute_bound_query_step(
            step_id=plan.steps[0].step_id
        )


def test_gateway_rejects_sources_not_bound_to_cited_facts(
    store: QueryGraphStore,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A store source cannot be cited unless the returned fact carries it."""

    from aviation_agentic_ai.agent_system import case_analysis_tools
    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        BoundQueryGateway,
        BoundQueryObservation,
    )

    unrelated_source_id = "source:advisory:unrelated"
    store.rows.append(
        {
            "fact_id": "fact:unrelated",
            "subject": EVENT_ID,
            "predicate": "rdf:type",
            "object": "atm:GroundStopTMI",
            "source_ids": [unrelated_source_id],
        }
    )
    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    forged = BoundQueryObservation(
        step_id=plan.steps[0].step_id,
        status="ok",
        fact_ids=("fact:type",),
        source_ids=(unrelated_source_id,),
        items=(
            {
                "fact_id": "fact:type",
                "subject": EVENT_ID,
                "predicate": "rdf:type",
                "object": "atm:GroundStopTMI",
                "source_ids": (SOURCE_ID,),
            },
        ),
    )
    monkeypatch.setattr(
        case_analysis_tools,
        "_execute_registered_step",
        lambda **_: forged,
    )

    with pytest.raises(ValueError, match="operational situation observation"):
        BoundQueryGateway(plan=plan, store=store).execute_bound_query_step(
            step_id=plan.steps[0].step_id
        )
