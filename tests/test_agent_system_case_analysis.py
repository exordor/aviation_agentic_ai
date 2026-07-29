"""Provider-free tests for the bounded Decision Case Analysis Agent."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from langchain_core.messages import AIMessage

from aviation_agentic_ai.agent_system.contracts import (
    ModelCallRecord,
    ModelToolCall,
)
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    CaseAnalysisTask,
    ContractExecutionBinding,
    QueryEvidenceBundle,
)
from aviation_agentic_ai.agent_system.corpus_query import (
    CorpusAnalysisStoreAdapter,
)
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusQueryStore,
    build_corpus,
)
from aviation_agentic_ai.agent_system.query_plan import compile_query_plan
from aviation_agentic_ai.agent_system.query_tools import QueryGraphStore
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn


_FIXTURE_SPEC = importlib.util.spec_from_file_location(
    "case_analysis_query_tools_fixture",
    Path(__file__).with_name("test_agent_system_query_tools.py"),
)
assert _FIXTURE_SPEC is not None and _FIXTURE_SPEC.loader is not None
_fixture_module = importlib.util.module_from_spec(_FIXTURE_SPEC)
_FIXTURE_SPEC.loader.exec_module(_fixture_module)
EVENT_ID = _fixture_module.EVENT_ID
_write_formal_observation_layer = _fixture_module._write_formal_observation_layer
_write_graph = _fixture_module._write_graph


@pytest.fixture
def store(tmp_path: Path) -> CorpusAnalysisStoreAdapter:
    """A corpus-backed view with formal, Weather, and BTS evidence."""

    run_dir = tmp_path / "run"
    _write_graph(run_dir)
    _write_formal_observation_layer(run_dir)
    context_path = run_dir / "context_associations.jsonl"
    context_data = context_path.read_bytes()
    manifest_path = run_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["context_artifacts"]["context_associations"] = {
        "path": context_path.name,
        "count": len(context_data.splitlines()),
        "sha256": hashlib.sha256(context_data).hexdigest(),
        "status": "ok",
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    corpus_dir = tmp_path / "corpus"
    build_corpus([run_dir], corpus_dir)
    return CorpusAnalysisStoreAdapter(
        CorpusQueryStore(corpus_dir),
        event_id=EVENT_ID,
    )


def _binding(store: QueryGraphStore) -> ContractExecutionBinding:
    return ContractExecutionBinding(
        run_id=str(store.manifest["run_id"]),
        created_at=datetime(2026, 7, 27, 12, 0, tzinfo=UTC),
        prompt_version="decision-case-analysis-v1",
    )


def _tool_turn(*step_ids: str, malformed: dict[str, Any] | None = None) -> ToolModelTurn:
    calls = [
        {
            "call_id": f"call:{index}",
            "name": "execute_bound_query_step",
            "arguments": malformed if malformed is not None else {"step_id": step_id},
        }
        for index, step_id in enumerate(step_ids, start=1)
    ]
    return ToolModelTurn(
        message=AIMessage(
            content="private selection reasoning must not persist",
            tool_calls=[
                {
                    "id": call["call_id"],
                    "name": call["name"],
                    "args": call["arguments"],
                    "type": "tool_call",
                }
                for call in calls
            ],
        ),
        record=ModelCallRecord(
            agent="decision_case_analysis",
            raw_response="private selection reasoning must not persist",
            prompt_version="decision-case-analysis-v1",
            provider="scripted",
            model="scripted",
            tool_calls=[ModelToolCall(**call) for call in calls],
        ),
    )


def _final_turn(payload: dict[str, Any]) -> ToolModelTurn:
    raw = json.dumps(payload)
    return ToolModelTurn(
        message=AIMessage(content=raw),
        record=ModelCallRecord(
            agent="decision_case_analysis",
            raw_response=f"<think>private reasoning</think>{raw}",
            prompt_version="decision-case-analysis-v1",
            provider="scripted",
            model="scripted",
        ),
    )


def _final_turn_with_record_only_tool_call(
    payload: dict[str, Any],
    *,
    step_id: str,
) -> ToolModelTurn:
    """Forge an audit-only synthesis call hidden from the native message."""

    raw = json.dumps(payload)
    return ToolModelTurn(
        message=AIMessage(content=raw),
        record=ModelCallRecord(
            agent="decision_case_analysis",
            raw_response=raw,
            prompt_version="decision-case-analysis-v1",
            provider="scripted",
            model="scripted",
            tool_calls=[
                ModelToolCall(
                    call_id="call:record-only",
                    name="execute_bound_query_step",
                    arguments={"step_id": step_id},
                )
            ],
        ),
    )


def _provider_error_turn(error: str) -> ToolModelTurn:
    return ToolModelTurn(
        message=None,
        record=ModelCallRecord(
            agent="decision_case_analysis",
            raw_response=f"<think>{error}</think>",
            prompt_version="decision-case-analysis-v1",
            provider="scripted",
            model="scripted",
            error=error,
        ),
    )


class _ScriptedAnalysisModel:
    def __init__(self, turns: list[ToolModelTurn]) -> None:
        self.turns = list(turns)
        self.invocations: list[tuple[str, list[Any]]] = []

    def invoke(self, messages: list[Any], *, phase: str) -> ToolModelTurn:
        self.invocations.append((phase, list(messages)))
        return self.turns.pop(0)


class _ModelFactory:
    def __init__(self, model: _ScriptedAnalysisModel) -> None:
        self.model = model
        self.calls = 0
        self.tool_names: list[str] = []

    def __call__(self, tools: list[Any]) -> _ScriptedAnalysisModel:
        self.calls += 1
        self.tool_names = [tool.name for tool in tools]
        return self.model


def _supported_payload(store: QueryGraphStore) -> dict[str, Any]:
    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        read_operational_situation,
    )

    observation = read_operational_situation(store, event_id=EVENT_ID)
    return {
        "statements": [
            {
                "kind": "source_fact",
                "text": "The record contains a source-qualified operational situation.",
                "support_fact_ids": [observation.fact_ids[0]],
                "support_source_ids": [observation.source_ids[0]],
            }
        ],
        "limitations": [],
    }


def _run_operational(
    store: QueryGraphStore,
    model: _ScriptedAnalysisModel,
):
    from aviation_agentic_ai.agent_system.case_analysis import (
        run_case_analysis_agent,
    )
    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        BoundQueryGateway,
    )

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    factory = _ModelFactory(model)
    result = run_case_analysis_agent(
        plan=plan,
        gateway=BoundQueryGateway(plan=plan, store=store),
        model_factory=factory,
        binding=_binding(store),
    )
    return plan, factory, result


def test_analysis_agent_seals_supported_operational_situation(
    store: QueryGraphStore,
) -> None:
    """Skipping the sealed task or support projection would break auditability."""

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    model = _ScriptedAnalysisModel([_final_turn(_supported_payload(store))])

    _plan, factory, (task, bundle, outcome) = _run_operational(store, model)

    assert factory.calls == 1
    assert factory.tool_names == ["execute_bound_query_step"]
    assert outcome.status == "ok"
    assert len(outcome.model_calls) == 1
    assert all(record.raw_response == "" for record in outcome.model_calls)
    assert bundle.task_id == task.task_id
    assert bundle.task_payload_checksum == task.payload_checksum
    assert bundle.executed_step_ids == (plan.steps[0].step_id,)
    assert set(bundle.retrieved_fact_ids).issubset(task.retrieved_fact_ids)
    assert set(bundle.retrieved_source_ids).issubset(task.retrieved_source_ids)
    assert len(bundle.executed_step_ids) <= 3
    assert [phase for phase, _messages in model.invocations] == ["final_answer"]
    final_messages = model.invocations[0][1]
    assert any(task.payload_checksum in str(message.content) for message in final_messages)


def test_required_insufficient_steps_finish_before_provider_construction(
    store: QueryGraphStore,
) -> None:
    """Required applicability evidence must fail closed before any provider exists."""

    from aviation_agentic_ai.agent_system.case_analysis import run_case_analysis_agent
    from aviation_agentic_ai.agent_system.case_analysis_tools import BoundQueryGateway

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What applicability and observed flight impact are recorded?",
        store=store,
    )
    model = _ScriptedAnalysisModel(
        [_tool_turn(*(step.step_id for step in plan.steps))]
    )
    factory = _ModelFactory(model)

    task, bundle, outcome = run_case_analysis_agent(
        plan=plan,
        gateway=BoundQueryGateway(plan=plan, store=store),
        model_factory=factory,
        binding=_binding(store),
    )

    assert factory.calls == 0
    assert model.invocations == []
    assert outcome.status == "insufficient"
    assert outcome.model_calls == []
    assert task.executed_bound_step_ids == tuple(
        step.step_id for step in plan.steps
    )
    assert bundle.executed_step_ids == task.executed_bound_step_ids


def test_blocked_required_step_constructs_no_provider(
    store: QueryGraphStore,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Required-step integrity failures must become a generic blocked result."""

    from aviation_agentic_ai.agent_system.case_analysis import run_case_analysis_agent
    from aviation_agentic_ai.agent_system.case_analysis_tools import BoundQueryGateway

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    gateway = BoundQueryGateway(plan=plan, store=store)

    def fail_integrity(*, step_id: str) -> None:
        del step_id
        raise ValueError("private integrity detail")

    monkeypatch.setattr(gateway, "execute_bound_query_step", fail_integrity)
    model = _ScriptedAnalysisModel([_final_turn(_supported_payload(store))])
    factory = _ModelFactory(model)

    _task, bundle, outcome = run_case_analysis_agent(
        plan=plan,
        gateway=gateway,
        model_factory=factory,
        binding=_binding(store),
    )

    assert factory.calls == 0
    assert model.invocations == []
    assert outcome.status == "blocked"
    assert outcome.failure_reason == "required analysis evidence failed validation"
    assert bundle.answer_statements == ()
    assert outcome.tool_calls[0].error == (
        "required bound step failed integrity validation"
    )


def test_episode_partial_preserves_its_explicit_limit(
    store: QueryGraphStore,
) -> None:
    """A one-record timeline must not silently become a grouped episode."""

    from aviation_agentic_ai.agent_system.case_analysis import run_case_analysis_agent
    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        BoundQueryGateway,
    )

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What decision episode is recorded?",
        store=store,
    )
    model = _ScriptedAnalysisModel([])
    factory = _ModelFactory(model)

    _task, bundle, outcome = run_case_analysis_agent(
        plan=plan,
        gateway=BoundQueryGateway(plan=plan, store=store),
        model_factory=factory,
        binding=_binding(store),
    )

    assert outcome.status == "ok"
    assert factory.calls == 0
    assert model.invocations == []
    assert bundle.limitations == (
        "the corpus records the selected decision record only; no "
        "cross-record lifecycle episode is asserted",
    )
    assert outcome.model_calls == []


def test_episode_partial_is_zero_call_and_cannot_accept_a_lifecycle_claim(
    store: QueryGraphStore,
) -> None:
    """Single-record evidence must never reach a provider that can group a lifecycle."""

    from aviation_agentic_ai.agent_system.case_analysis import run_case_analysis_agent
    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        BoundQueryGateway,
        read_episode_timeline,
    )

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What decision episode is recorded?",
        store=store,
    )
    observation = read_episode_timeline(store, event_id=EVENT_ID)
    malicious_payload = {
        "statements": [
            {
                "kind": "source_fact",
                "text": "These records form one advisory lifecycle group.",
                "support_fact_ids": [observation.fact_ids[0]],
                "support_source_ids": [observation.source_ids[0]],
            }
        ],
        "limitations": [observation.limitation],
    }
    model = _ScriptedAnalysisModel(
        [
            _tool_turn(plan.steps[0].step_id),
            _final_turn(malicious_payload),
        ]
    )
    factory = _ModelFactory(model)

    _task, bundle, outcome = run_case_analysis_agent(
        plan=plan,
        gateway=BoundQueryGateway(plan=plan, store=store),
        model_factory=factory,
        binding=_binding(store),
    )

    assert factory.calls == 0
    assert model.invocations == []
    assert outcome.model_calls == []
    assert bundle.answer_statements == ()
    assert bundle.limitations == (
        "the corpus records the selected decision record only; no "
        "cross-record lifecycle episode is asserted",
    )
    assert "form one advisory lifecycle group" not in outcome.answer


def test_applicability_and_observed_flight_insufficiency_stops_before_synthesis(
    store: QueryGraphStore,
) -> None:
    """Facility/time applicability cannot stand in for observed-flight impact."""

    from aviation_agentic_ai.agent_system.case_analysis import run_case_analysis_agent
    from aviation_agentic_ai.agent_system.case_analysis_tools import BoundQueryGateway

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What applicability and observed flight impact are recorded?",
        store=store,
    )
    model = _ScriptedAnalysisModel([])
    factory = _ModelFactory(model)

    _task, bundle, outcome = run_case_analysis_agent(
        plan=plan,
        gateway=BoundQueryGateway(plan=plan, store=store),
        model_factory=factory,
        binding=_binding(store),
    )

    assert outcome.status == "insufficient"
    assert factory.calls == 0
    assert outcome.model_calls == []
    assert len(bundle.executed_step_ids) == 2
    assert any(
        "do not establish an individual-flight outcome" in limitation
        for limitation in bundle.limitations
    )


@pytest.mark.parametrize(
    "selection_kind",
    (
        "not_optional",
        "repeat",
        "malformed",
    ),
)
def test_optional_step_selection_rejects_unbound_or_malformed_calls(
    selection_kind: str,
) -> None:
    """Only remaining optional IDs with the exact schema may be selected."""

    from aviation_agentic_ai.agent_system.case_analysis import _selection_error

    optional_step_id = "step:optional:1"
    if selection_kind == "repeat":
        turn = _tool_turn(optional_step_id, optional_step_id)
    elif selection_kind == "malformed":
        turn = _tool_turn(
            optional_step_id,
            malformed={"step_id": optional_step_id, "path": "/tmp/escape"},
        )
    else:
        turn = _tool_turn("step:not-optional")
    error, selected = _selection_error(
        turn_message=turn.message,
        record=turn.record,
        selectable_step_ids=frozenset({optional_step_id}),
        remaining_step_budget=2,
    )

    assert error
    assert selected == ()


def test_optional_step_selection_respects_the_remaining_budget() -> None:
    """Required preflight reads reduce the model-selectable step budget."""

    from aviation_agentic_ai.agent_system.case_analysis import _selection_error

    optional_step_ids = frozenset(
        {
            "step:optional:1",
            "step:optional:2",
            "step:optional:3",
        }
    )
    turn = _tool_turn(*sorted(optional_step_ids))
    error, selected = _selection_error(
        turn_message=turn.message,
        record=turn.record,
        selectable_step_ids=optional_step_ids,
        remaining_step_budget=2,
    )

    assert error == "analysis model exceeded the remaining step budget"
    assert selected == ()


def test_foreign_statement_support_blocks_the_answer(
    store: QueryGraphStore,
) -> None:
    """A model citation outside the sealed task must never enter the bundle."""

    payload = {
        "statements": [
            {
                "kind": "source_fact",
                "text": "An unsupported claim.",
                "support_fact_ids": ["fact:foreign"],
                "support_source_ids": ["source:foreign"],
            }
        ],
        "limitations": [],
    }
    model = _ScriptedAnalysisModel([_final_turn(payload)])

    _plan, _factory, (task, bundle, outcome) = _run_operational(store, model)

    assert outcome.status == "blocked"
    assert bundle.task_id == task.task_id
    assert bundle.answer_statements == ()
    assert "outside sealed analysis task" in outcome.failure_reason


def test_same_task_source_must_support_the_cited_fact(
    store: QueryGraphStore,
) -> None:
    """Global containment alone must not let one source mask another fact."""

    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        read_operational_situation,
    )

    observation = read_operational_situation(store, event_id=EVENT_ID)
    formal_item = next(
        item for item in observation.items if item["evidence_role"] == "formal_event_fact"
    )
    wrong_source = next(
        source_id
        for source_id in observation.source_ids
        if source_id not in formal_item["source_ids"]
    )
    payload = {
        "statements": [
            {
                "kind": "source_fact",
                "text": "A source from another evidence item supports this fact.",
                "support_fact_ids": [formal_item["fact_id"]],
                "support_source_ids": [wrong_source],
            }
        ],
        "limitations": [],
    }
    model = _ScriptedAnalysisModel([_final_turn(payload)])

    _plan, _factory, (_task, bundle, outcome) = _run_operational(store, model)

    assert outcome.status == "blocked"
    assert bundle.answer_statements == ()
    assert "does not cover cited fact" in outcome.failure_reason


def test_synthesis_turn_tool_request_blocks_without_a_third_model_call(
    store: QueryGraphStore,
) -> None:
    """A second-turn tool request must terminate instead of extending the loop."""

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    model = _ScriptedAnalysisModel([_tool_turn(plan.steps[0].step_id)])

    _plan, _factory, (_task, bundle, outcome) = _run_operational(store, model)

    assert outcome.status == "blocked"
    assert bundle.answer_statements == ()
    assert len(outcome.model_calls) == 1
    assert [phase for phase, _messages in model.invocations] == ["final_answer"]


def test_synthesis_record_only_tool_request_is_rejected_before_json_parsing(
    store: QueryGraphStore,
) -> None:
    """The native message and persisted synthesis audit must agree exactly."""

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    model = _ScriptedAnalysisModel(
        [
            _final_turn_with_record_only_tool_call(
                _supported_payload(store),
                step_id=plan.steps[0].step_id,
            )
        ]
    )

    _plan, _factory, (_task, bundle, outcome) = _run_operational(store, model)

    assert outcome.status == "blocked"
    assert bundle.answer_statements == ()
    assert outcome.failure_reason == (
        "analysis model tool-call record differs from native message"
    )
    assert len(outcome.model_calls) == 1
    assert len(model.invocations) == 1


def test_analysis_artifacts_are_round_trip_immutable_and_isolated(
    store: QueryGraphStore,
) -> None:
    """Mutable or legacy-path writes would erase the audit boundary."""

    from aviation_agentic_ai.agent_system.case_analysis import (
        write_case_analysis_artifacts,
    )

    model = _ScriptedAnalysisModel([_final_turn(_supported_payload(store))])
    _plan, _factory, (task, bundle, outcome) = _run_operational(store, model)

    analysis_dir = write_case_analysis_artifacts(
        run_dir=store.run_dir,
        task=task,
        bundle=bundle,
        outcome=outcome,
        query_store=store,
    )

    assert analysis_dir.parent == store.run_dir / "analysis"
    assert CaseAnalysisTask.model_validate_json(
        (analysis_dir / "case_analysis_task.json").read_text(encoding="utf-8")
    ) == task
    assert QueryEvidenceBundle.model_validate_json(
        (analysis_dir / "query_evidence_bundle.json").read_text(encoding="utf-8")
    ) == bundle
    run_payload = json.loads(
        (analysis_dir / "case_analysis_run.json").read_text(encoding="utf-8")
    )
    assert run_payload["analysis_run_id"] == analysis_dir.name
    assert "raw_response" not in json.dumps(run_payload)
    assert not (store.run_dir / "query_run.json").exists()
    assert (
        write_case_analysis_artifacts(
            run_dir=store.run_dir,
            task=task,
            bundle=bundle,
            outcome=outcome,
            query_store=store,
        )
        == analysis_dir
    )

    (analysis_dir / "case_analysis_run.json").write_text(
        "{}\n",
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="immutable analysis artifact conflict"):
        write_case_analysis_artifacts(
            run_dir=store.run_dir,
            task=task,
            bundle=bundle,
            outcome=outcome,
            query_store=store,
        )


def test_analysis_artifacts_reject_a_symlinked_analysis_root(
    store: QueryGraphStore,
) -> None:
    """A pre-created analysis symlink must never redirect immutable writes."""

    from aviation_agentic_ai.agent_system.case_analysis import (
        write_case_analysis_artifacts,
    )

    model = _ScriptedAnalysisModel([_final_turn(_supported_payload(store))])
    _plan, _factory, (task, bundle, outcome) = _run_operational(store, model)
    outside = store.run_dir.parent / f"{store.run_dir.name}-outside-analysis"
    outside.mkdir()
    (store.run_dir / "analysis").symlink_to(outside, target_is_directory=True)

    with pytest.raises(RuntimeError, match="symlinked analysis root"):
        write_case_analysis_artifacts(
            run_dir=store.run_dir,
            task=task,
            bundle=bundle,
            outcome=outcome,
            query_store=store,
        )

    assert list(outside.iterdir()) == []


def test_analysis_artifacts_reject_unvalidated_and_cross_run_destinations(
    store: QueryGraphStore,
) -> None:
    """Neither an unrelated directory nor another valid run may receive artifacts."""

    from aviation_agentic_ai.agent_system.case_analysis import (
        write_case_analysis_artifacts,
    )

    model = _ScriptedAnalysisModel([_final_turn(_supported_payload(store))])
    _plan, _factory, (task, bundle, outcome) = _run_operational(store, model)
    unrelated = store.run_dir.parent / f"{store.run_dir.name}-unrelated"
    unrelated.mkdir()
    nonexistent = store.run_dir.parent / f"{store.run_dir.name}-nonexistent"
    other_run = store.run_dir.parent / f"{store.run_dir.name}-other-run"
    _write_graph(other_run)

    for destination in (unrelated, nonexistent, other_run):
        with pytest.raises(RuntimeError, match="analysis destination"):
            write_case_analysis_artifacts(
                run_dir=destination,
                task=task,
                bundle=bundle,
                outcome=outcome,
                query_store=store,
            )
        assert not (destination / "analysis").exists()


def test_analysis_artifacts_reject_incoherent_bundle_and_outcome(
    store: QueryGraphStore,
) -> None:
    """Checksummed objects from unrelated bindings must not be co-persisted."""

    from aviation_agentic_ai.agent_system.case_analysis import (
        write_case_analysis_artifacts,
    )

    model = _ScriptedAnalysisModel([_final_turn(_supported_payload(store))])
    _plan, _factory, (task, bundle, outcome) = _run_operational(store, model)
    foreign_bundle = bundle.model_copy(update={"task_id": "task:foreign"})
    incomplete_outcome = outcome.model_copy(update={"retrieved_fact_ids": []})

    with pytest.raises(RuntimeError, match="analysis artifact binding"):
        write_case_analysis_artifacts(
            run_dir=store.run_dir,
            task=task,
            bundle=foreign_bundle,
            outcome=outcome,
            query_store=store,
        )
    with pytest.raises(RuntimeError, match="analysis artifact binding"):
        write_case_analysis_artifacts(
            run_dir=store.run_dir,
            task=task,
            bundle=bundle,
            outcome=incomplete_outcome,
            query_store=store,
        )
    assert not (store.run_dir / "analysis").exists()


def test_persisted_model_tool_metadata_drops_unvalidated_arguments(
    store: QueryGraphStore,
) -> None:
    """Provider arguments, paths, secrets, and reasoning must not enter JSON."""

    from aviation_agentic_ai.agent_system.case_analysis import (
        write_case_analysis_artifacts,
    )

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    model = _ScriptedAnalysisModel([_final_turn(_supported_payload(store))])
    _plan, _factory, (task, bundle, outcome) = _run_operational(store, model)
    secret = "provider-secret-7f31"
    malicious_record = ModelCallRecord(
        agent="decision_case_analysis",
        raw_response=f"<think>{secret}</think>",
        prompt_version=f"private-prompt-{secret}",
        provider=f"/tmp/{secret}",
        model=f"private-model-{secret}",
        tool_calls=[
            ModelToolCall(
                call_id=f"call:{secret}",
                name="execute_bound_query_step",
                arguments={
                    "step_id": plan.steps[0].step_id,
                    "path": f"/tmp/{secret}",
                    "reasoning": f"hidden {secret}",
                },
            )
        ],
    )
    unsafe_outcome = outcome.model_copy(update={"model_calls": [malicious_record]})

    analysis_dir = write_case_analysis_artifacts(
        run_dir=store.run_dir,
        task=task,
        bundle=bundle,
        outcome=unsafe_outcome,
        query_store=store,
    )
    persisted = (analysis_dir / "case_analysis_run.json").read_text(
        encoding="utf-8"
    )
    model_call = json.loads(persisted)["outcome"]["model_calls"][0]

    assert secret not in persisted
    assert "/tmp/" not in persisted
    assert "reasoning" not in persisted
    assert "raw_response" not in persisted
    assert model_call["tool_calls"] == [
        {
            "call_id": "redacted:1",
            "name": "execute_bound_query_step",
        }
    ]


def test_persisted_provider_error_uses_only_a_generic_status_marker(
    store: QueryGraphStore,
) -> None:
    """Provider error prose and hidden reasoning must not enter artifacts."""

    from aviation_agentic_ai.agent_system.case_analysis import (
        write_case_analysis_artifacts,
    )
    from aviation_agentic_ai.agent_system.case_analysis_tools import BoundQueryGateway
    from aviation_agentic_ai.agent_system.case_analysis import run_case_analysis_agent

    secret_error = "provider-reasoning-token-9f2c: internal chain of thought"
    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    task, bundle, outcome = run_case_analysis_agent(
        plan=plan,
        gateway=BoundQueryGateway(plan=plan, store=store),
        model_factory=_ModelFactory(
            _ScriptedAnalysisModel([_provider_error_turn(secret_error)])
        ),
        binding=_binding(store),
    )

    analysis_dir = write_case_analysis_artifacts(
        run_dir=store.run_dir,
        task=task,
        bundle=bundle,
        outcome=outcome,
        query_store=store,
    )
    persisted = (analysis_dir / "case_analysis_run.json").read_text(
        encoding="utf-8"
    )
    payload = json.loads(persisted)

    assert outcome.status == "blocked"
    assert secret_error not in persisted
    assert "raw_response" not in persisted
    assert payload["outcome"]["model_calls"][0]["status"] == "error"
    assert "error" not in payload["outcome"]["model_calls"][0]
