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
def store(tmp_path: Path) -> QueryGraphStore:
    """A validated current run with formal, Weather, and BTS evidence."""

    _write_graph(tmp_path)
    _write_formal_observation_layer(tmp_path)
    context_path = tmp_path / "context_associations.jsonl"
    context_data = context_path.read_bytes()
    manifest_path = tmp_path / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["context_artifacts"]["context_associations"] = {
        "path": context_path.name,
        "count": len(context_data.splitlines()),
        "sha256": hashlib.sha256(context_data).hexdigest(),
        "status": "ok",
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return QueryGraphStore(tmp_path)


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
        self.tool_names: list[str] = []

    def __call__(self, tools: list[Any]) -> _ScriptedAnalysisModel:
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
    model = _ScriptedAnalysisModel(
        [_tool_turn(plan.steps[0].step_id), _final_turn(_supported_payload(store))]
    )

    _plan, factory, (task, bundle, outcome) = _run_operational(store, model)

    assert factory.tool_names == ["execute_bound_query_step"]
    assert outcome.status == "ok"
    assert len(outcome.model_calls) == 2
    assert all(record.raw_response == "" for record in outcome.model_calls)
    assert bundle.task_id == task.task_id
    assert bundle.task_payload_checksum == task.payload_checksum
    assert bundle.executed_step_ids == (plan.steps[0].step_id,)
    assert set(bundle.retrieved_fact_ids).issubset(task.retrieved_fact_ids)
    assert set(bundle.retrieved_source_ids).issubset(task.retrieved_source_ids)
    assert len(bundle.executed_step_ids) <= 3
    final_messages = model.invocations[1][1]
    assert any(task.payload_checksum in str(message.content) for message in final_messages)


def test_insufficient_bound_observation_uses_one_model_turn(
    store: QueryGraphStore,
) -> None:
    """Calling synthesis without evidence would invite completion from memory."""

    from aviation_agentic_ai.agent_system.case_analysis import run_case_analysis_agent
    from aviation_agentic_ai.agent_system.case_analysis_tools import BoundQueryGateway

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="Which historical case is most similar?",
        store=store,
    )
    model = _ScriptedAnalysisModel([_tool_turn(plan.steps[0].step_id)])
    task, bundle, outcome = run_case_analysis_agent(
        plan=plan,
        gateway=BoundQueryGateway(plan=plan, store=store),
        model_factory=_ModelFactory(model),
        binding=_binding(store),
    )

    assert outcome.status == "insufficient"
    assert len(outcome.model_calls) == 1
    assert [phase for phase, _messages in model.invocations] == ["select_tool"]
    assert bundle.task_id == task.task_id
    assert bundle.answer_statements == ()
    assert bundle.limitations == (
        "historical similarity requires an approved corpus and comparison profile",
    )


def test_episode_partial_preserves_its_explicit_limit(
    store: QueryGraphStore,
) -> None:
    """A one-record timeline must not silently become a grouped episode."""

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
    payload = {
        "statements": [
            {
                "kind": "source_fact",
                "text": "The record has a bounded single-record timeline.",
                "support_fact_ids": [observation.fact_ids[0]],
                "support_source_ids": [observation.source_ids[0]],
            }
        ],
        "limitations": [observation.limitation],
    }
    model = _ScriptedAnalysisModel(
        [_tool_turn(plan.steps[0].step_id), _final_turn(payload)]
    )

    _task, bundle, outcome = run_case_analysis_agent(
        plan=plan,
        gateway=BoundQueryGateway(plan=plan, store=store),
        model_factory=_ModelFactory(model),
        binding=_binding(store),
    )

    assert outcome.status == "ok"
    assert bundle.limitations == (
        "single-record timeline; no advisory lifecycle grouping evidence",
    )
    assert len(outcome.model_calls) == 2


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
    model = _ScriptedAnalysisModel(
        [_tool_turn(*(step.step_id for step in plan.steps))]
    )

    _task, bundle, outcome = run_case_analysis_agent(
        plan=plan,
        gateway=BoundQueryGateway(plan=plan, store=store),
        model_factory=_ModelFactory(model),
        binding=_binding(store),
    )

    assert outcome.status == "insufficient"
    assert len(outcome.model_calls) == 1
    assert len(bundle.executed_step_ids) == 2
    assert any(
        "do not establish an individual-flight outcome" in limitation
        for limitation in bundle.limitations
    )


@pytest.mark.parametrize(
    "selection",
    (
        ("step:not-bound",),
        ("REPEAT",),
        ("MALFORMED",),
    ),
)
def test_invalid_step_selection_blocks_before_synthesis(
    store: QueryGraphStore,
    selection: tuple[str, ...],
) -> None:
    """Foreign, repeated, or malformed calls must not become retrieval input."""

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    if selection == ("REPEAT",):
        turn = _tool_turn(plan.steps[0].step_id, plan.steps[0].step_id)
    elif selection == ("MALFORMED",):
        turn = _tool_turn(
            plan.steps[0].step_id,
            malformed={"step_id": plan.steps[0].step_id, "path": "/tmp/escape"},
        )
    else:
        turn = _tool_turn(*selection)
    model = _ScriptedAnalysisModel([turn])

    _plan, _factory, (_task, bundle, outcome) = _run_operational(store, model)

    assert outcome.status == "blocked"
    assert len(outcome.model_calls) == 1
    assert bundle.answer_statements == ()
    assert model.invocations[0][0] == "select_tool"


def test_more_than_three_selected_steps_blocks_without_execution(
    store: QueryGraphStore,
) -> None:
    """Removing the batch budget would let one turn execute unbounded reads."""

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    model = _ScriptedAnalysisModel(
        [
            _tool_turn(
                plan.steps[0].step_id,
                plan.steps[0].step_id,
                plan.steps[0].step_id,
                plan.steps[0].step_id,
            )
        ]
    )

    _plan, _factory, (_task, bundle, outcome) = _run_operational(store, model)

    assert outcome.status == "blocked"
    assert len(bundle.executed_step_ids) == 0
    assert len(outcome.model_calls) == 1


def test_foreign_statement_support_blocks_the_answer(
    store: QueryGraphStore,
) -> None:
    """A model citation outside the sealed task must never enter the bundle."""

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
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
    model = _ScriptedAnalysisModel(
        [_tool_turn(plan.steps[0].step_id), _final_turn(payload)]
    )

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

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
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
    model = _ScriptedAnalysisModel(
        [_tool_turn(plan.steps[0].step_id), _final_turn(payload)]
    )

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
    model = _ScriptedAnalysisModel(
        [
            _tool_turn(plan.steps[0].step_id),
            _tool_turn(plan.steps[0].step_id),
        ]
    )

    _plan, _factory, (_task, bundle, outcome) = _run_operational(store, model)

    assert outcome.status == "blocked"
    assert bundle.answer_statements == ()
    assert len(outcome.model_calls) == 2
    assert [phase for phase, _messages in model.invocations] == [
        "select_tool",
        "final_answer",
    ]


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
            _tool_turn(plan.steps[0].step_id),
            _final_turn_with_record_only_tool_call(
                _supported_payload(store),
                step_id=plan.steps[0].step_id,
            ),
        ]
    )

    _plan, _factory, (_task, bundle, outcome) = _run_operational(store, model)

    assert outcome.status == "blocked"
    assert bundle.answer_statements == ()
    assert outcome.failure_reason == (
        "analysis model tool-call record differs from native message"
    )
    assert len(outcome.model_calls) == 2
    assert len(model.invocations) == 2


def test_analysis_artifacts_are_round_trip_immutable_and_isolated(
    store: QueryGraphStore,
) -> None:
    """Mutable or legacy-path writes would erase the audit boundary."""

    from aviation_agentic_ai.agent_system.case_analysis import (
        write_case_analysis_artifacts,
    )

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    model = _ScriptedAnalysisModel(
        [_tool_turn(plan.steps[0].step_id), _final_turn(_supported_payload(store))]
    )
    _plan, _factory, (task, bundle, outcome) = _run_operational(store, model)

    analysis_dir = write_case_analysis_artifacts(
        run_dir=store.run_dir,
        task=task,
        bundle=bundle,
        outcome=outcome,
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
        )


def test_analysis_artifacts_reject_a_symlinked_analysis_root(
    store: QueryGraphStore,
) -> None:
    """A pre-created analysis symlink must never redirect immutable writes."""

    from aviation_agentic_ai.agent_system.case_analysis import (
        write_case_analysis_artifacts,
    )

    plan = compile_query_plan(
        run_dir=store.run_dir,
        question="What public operational situation is recorded?",
        store=store,
    )
    model = _ScriptedAnalysisModel(
        [_tool_turn(plan.steps[0].step_id), _final_turn(_supported_payload(store))]
    )
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
        )

    assert list(outside.iterdir()) == []


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
