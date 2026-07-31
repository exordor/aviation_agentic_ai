from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import pytest

import aviation_agentic_ai.agent_system.live_agent_evaluation as live_eval
from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryStatement,
    HybridQuerySupportRecord,
    ModelCallRecord,
    ModelToolCall,
    QueryGraphEdge,
    QueryGraphPath,
    QueryToolOutcome,
    QueryToolTrace,
)
from aviation_agentic_ai.agent_system.live_agent_evaluation import (
    LiveEvaluationAssertion,
    LiveEvaluationAuthorizationError,
    LiveEvaluationResult,
    LiveEvaluationTrial,
    build_hybrid_query_run_artifact,
    load_live_evaluation_suite,
    run_live_agent_evaluation,
    score_query_trial,
    summarize_live_evaluation,
    write_hybrid_query_run_artifact,
    write_live_evaluation_artifacts,
)


def _trial(
    *,
    required_tool_names: tuple[str, ...] = (
        "read_tmi_event_graph",
    ),
    required_graph_path_kinds: tuple[str, ...] = (
        "weather_context_at_controlled_facility",
    ),
) -> LiveEvaluationTrial:
    return LiveEvaluationTrial(
        trial_id="query-084",
        partition="regression",
        source_id="2026-05-20:084",
        question="Show the source-backed weather evidence path.",
        required_tool_names=required_tool_names,
        required_graph_path_kinds=required_graph_path_kinds,
    )


def _live_call(
    *,
    tool_name: str | None = None,
    raw_response: str = "provider payload is not retained",
    error: str | None = None,
) -> ModelCallRecord:
    return ModelCallRecord(
        agent="query",
        raw_response=raw_response,
        prompt_set_id="aviation-tmi-event-agents-v1",
        prompt_version="query-v1",
        provider="deepseek",
        model="deepseek-v4-pro",
        temperature=0.0,
        input_tokens=40,
        output_tokens=20,
        latency_ms=25,
        error=error,
        tool_calls=(
            [
                ModelToolCall(
                    call_id="call:1",
                    name=tool_name,
                    arguments={"event_id": "urn:event:084"},
                )
            ]
            if tool_name
            else []
        ),
    )


def _supported_graph_outcome(
    *,
    path_kind: str = "weather_context_at_controlled_facility",
    tool_name: str = "read_tmi_event_graph",
    statement_text: str = (
        "The event and weather report share the controlled facility; "
        "this is a non-causal context association."
    ),
) -> QueryToolOutcome:
    path = QueryGraphPath(
        path_id="path:weather",
        path_kind=path_kind,
        edges=(
            QueryGraphEdge(
                fact_id="fact:controlled",
                subject_iri="urn:event:084",
                predicate_iri=(
                    "https://data.nasa.gov/ontologies/atmonto/ATM#"
                    "controlledNASelement"
                ),
                object_kind="iri",
                object_value="urn:facility:KEWR",
                source_ids=("2026-05-20:084",),
            ),
        ),
        source_ids=("2026-05-20:084", "metar:KEWR"),
    )
    return QueryToolOutcome(
        status="ok",
        answer=statement_text,
        retrieved_event_ids=["urn:event:084"],
        source_ids=["2026-05-20:084", "metar:KEWR"],
        retrieved_fact_ids=["fact:controlled"],
        retrieved_graph_path_ids=[path.path_id],
        retrieved_graph_paths=[path],
        answer_statements=[
            HybridQueryStatement(
                kind="non_causal_context",
                text=statement_text,
                support_event_ids=("urn:event:084",),
                support_fact_ids=("fact:controlled",),
                support_context_association_ids=("association:weather",),
                support_graph_path_ids=(path.path_id,),
                support_source_ids=("2026-05-20:084", "metar:KEWR"),
            )
        ],
        support_records=[
            HybridQuerySupportRecord(
                kind="non_causal_context",
                event_ids=("urn:event:084",),
                fact_ids=("fact:controlled",),
                context_association_ids=("association:weather",),
                graph_path_ids=(path.path_id,),
                source_ids=("2026-05-20:084", "metar:KEWR"),
            )
        ],
        model_calls=[
            _live_call(tool_name=tool_name, raw_response=""),
            _live_call(raw_response="sk-secret must not be persisted"),
        ],
        tool_calls=[
            QueryToolTrace(
                tool_call_id="trace:1",
                tool=tool_name,
                arguments={
                    "event_id": "urn:event:084",
                    "view": "evidence_paths",
                },
                result_refs=[
                    "fact:controlled",
                    "path:weather",
                    "association:weather",
                ],
                context_association_ids=["association:weather"],
                source_ids=["2026-05-20:084", "metar:KEWR"],
                status="ok",
            )
        ],
    )


def _result(
    trial_id: str,
    *,
    status: str = "passed",
    live_model: bool = False,
) -> LiveEvaluationResult:
    return LiveEvaluationResult(
        trial_id=trial_id,
        repetition=1,
        kind="query",
        source_id=f"source:{trial_id}",
        role="query",
        live_model=live_model,
        workflow_status="ok",
        activation_status="activated",
        model_acceptance_status=status,
        assertions=(
            LiveEvaluationAssertion(
                check_id="agent_activated",
                passed=status == "passed",
                detail_code="observed",
            ),
        ),
        provider="deepseek",
        model="deepseek-v4-pro",
        prompt_set_id="aviation-tmi-event-agents-v1",
        prompt_version="query-v1",
        temperature=0.0,
        provider_call_count=2,
        native_tool_call_count=1,
        bound_tool_execution_count=1,
        input_tokens=20,
        output_tokens=10,
        provider_latency_ms=25.0,
    )


def test_tracked_v4_suite_is_query_only_and_has_graph_path_trial() -> None:
    suite = load_live_evaluation_suite(
        "data/evaluation/agent_system/live_agent_smoke_v4.yaml"
    )

    assert suite.version == "live-agent-smoke-v4"
    assert suite.future_frozen_evaluation == "not_constructed"
    assert len(suite.trials) == 5
    assert {trial.kind for trial in suite.trials} == {"query"}
    assert {trial.expected_role for trial in suite.trials} == {"query"}
    assert suite.build_source_ids == (
        "2026-05-20:084",
        "2026-05-20:115",
        "2026-05-20:159",
    )
    graph_trials = [
        trial
        for trial in suite.trials
        if trial.required_graph_path_kinds
    ]
    assert len(graph_trials) == 1
    assert graph_trials[0].required_tool_names == (
        "read_tmi_event_graph",
    )


def test_suite_rejects_graph_requirement_without_graph_tool() -> None:
    with pytest.raises(
        ValueError,
        match="required graph paths require read_tmi_event_graph",
    ):
        LiveEvaluationTrial(
            trial_id="invalid",
            partition="regression",
            source_id="source:invalid",
            question="Read a graph path.",
            required_graph_path_kinds=("weather_context_at_controlled_facility",),
        )


def test_active_evaluator_has_no_integration_scorer_or_role() -> None:
    source = inspect.getsource(live_eval)

    assert "score_integration_trial" not in source
    assert "event_evidence_integration" not in source
    assert "score_analysis_trial" not in source


def test_hybrid_query_run_artifact_is_sanitized_and_records_path_kind(
    tmp_path: Path,
) -> None:
    trial = _trial()
    outcome = _supported_graph_outcome()
    query_run = build_hybrid_query_run_artifact(
        trial=trial,
        event_id="urn:event:084",
        outcome=outcome,
    )
    artifact_path = write_hybrid_query_run_artifact(
        tmp_path / "query",
        query_run,
    )

    result = score_query_trial(
        trial=trial,
        repetition=1,
        live_model=False,
        event_id="urn:event:084",
        outcome=outcome,
        query_run=query_run,
        query_run_artifact_path=artifact_path,
    )

    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    serialized = artifact_path.read_text(encoding="utf-8")
    assert payload["graph_path_kinds"] == [
        "weather_context_at_controlled_facility"
    ]
    assert "arguments" not in serialized
    assert "raw_response" not in serialized
    assert "sk-secret" not in serialized
    assert result.model_acceptance_status == "passed"


@pytest.mark.parametrize(
    ("tool_name", "path_kind", "failed_check"),
    [
        (
            "read_tmi_event_facts",
            "weather_context_at_controlled_facility",
            "required_tools_observed",
        ),
        (
            "read_tmi_event_graph",
            "unexpected_path",
            "required_graph_paths_observed",
        ),
    ],
)
def test_query_scoring_checks_required_tools_and_structured_graph_paths(
    tool_name: str,
    path_kind: str,
    failed_check: str,
) -> None:
    trial = _trial()
    outcome = _supported_graph_outcome(
        tool_name=tool_name,
        path_kind=path_kind,
    )
    query_run = build_hybrid_query_run_artifact(
        trial=trial,
        event_id="urn:event:084",
        outcome=outcome,
    )

    result = score_query_trial(
        trial=trial,
        repetition=1,
        live_model=False,
        event_id="urn:event:084",
        outcome=outcome,
        query_run=query_run,
    )

    assert result.model_acceptance_status == "failed"
    assert any(
        assertion.check_id == failed_check and not assertion.passed
        for assertion in result.assertions
    )


def test_claim_boundary_violation_fails_query_acceptance() -> None:
    trial = _trial()
    outcome = _supported_graph_outcome(
        statement_text=(
            "The weather report proves that weather caused the TMI decision."
        )
    )
    query_run = build_hybrid_query_run_artifact(
        trial=trial,
        event_id="urn:event:084",
        outcome=outcome,
    )

    result = score_query_trial(
        trial=trial,
        repetition=1,
        live_model=False,
        event_id="urn:event:084",
        outcome=outcome,
        query_run=query_run,
    )

    assert result.model_acceptance_status == "failed"
    assert any(
        assertion.check_id == "statement_claim_boundaries"
        and not assertion.passed
        for assertion in result.assertions
    )


def test_summary_and_v4_artifact_names_are_query_specific(
    tmp_path: Path,
) -> None:
    results = (_result("passed"), _result("failed", status="failed"))
    summary = summarize_live_evaluation(
        suite_id="suite",
        suite_checksum="a" * 64,
        repetitions=1,
        results=results,
        runner_status="completed",
        live_model=False,
    )

    paths = write_live_evaluation_artifacts(
        output_dir=tmp_path / "runtime",
        report_dir=tmp_path / "reports",
        results=results,
        summary=summary,
    )

    assert summary.manifest_version == "tmi-event-live-evaluation-v4"
    assert summary.model_acceptance_status == "failed"
    assert [path.name for path in paths] == [
        "live_evaluation_results_v4.jsonl",
        "live_evaluation_manifest_v4.json",
        "agent_system_live_agent_smoke_v4.json",
        "agent_system_live_agent_smoke_v4.md",
    ]


def test_missing_authorization_rejects_before_writes(tmp_path: Path) -> None:
    with pytest.raises(LiveEvaluationAuthorizationError):
        run_live_agent_evaluation(
            config_path="configs/cross_source_v1.yaml",
            suite_path=(
                "data/evaluation/agent_system/live_agent_smoke_v4.yaml"
            ),
            output_dir=tmp_path / "runtime",
            report_dir=tmp_path / "reports",
            allow_live_model=False,
            repetitions=1,
        )

    assert not (tmp_path / "runtime").exists()


def test_missing_credentials_block_before_provider_calls(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(live_eval, "load_environment", lambda: None)
    monkeypatch.setattr(
        live_eval,
        "load_batch_resources",
        lambda _config: pytest.fail("resources must not load"),
    )

    summary = run_live_agent_evaluation(
        config_path="configs/cross_source_v1.yaml",
        suite_path="data/evaluation/agent_system/live_agent_smoke_v4.yaml",
        output_dir=tmp_path / "runtime",
        report_dir=tmp_path / "reports",
        allow_live_model=True,
        repetitions=1,
    )

    assert summary.runner_status == "blocked_before_run"
    assert summary.provider_call_count == 0
    assert "missing_deepseek_credentials" in summary.runner_detail_codes


def test_pre_refactor_v1_live_artifacts_remain_byte_frozen() -> None:
    expected = {
        "data/evaluation/agent_system/live_agent_smoke_v1.yaml": (
            "e23315ba4656e84c0b2b17d0e4991bc383232e9704f38e24028c34e1b2c56c38"
        ),
        "reports/stages/agent_system_live_agent_smoke_v1.json": (
            "4c74027a49a0800615ec1c3d5c9616af4877c8bda4d23fa91ac6ac65c4b331d1"
        ),
        "reports/stages/agent_system_live_agent_smoke_v1.md": (
            "e351e6c49b91bed4b29d3f8f6ba9c3d220c9d7da7ba94c04f19cf2ceba6a75cb"
        ),
    }

    for path, checksum in expected.items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == checksum
