from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from types import SimpleNamespace

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
    LiveEvaluationProviderCall,
    LiveEvaluationResult,
    LiveEvaluationSuite,
    LiveEvaluationTrial,
    build_hybrid_query_run_artifact,
    load_live_evaluation_suite,
    run_live_agent_evaluation,
    score_query_trial,
    summarize_live_evaluation,
    write_hybrid_query_run_artifact,
    write_live_evaluation_artifacts,
)
from aviation_agentic_ai.agent_system.evaluation_binding import (
    EvaluationDataBinding,
    EvaluationVectorBinding,
)
from aviation_agentic_ai.agent_system.query_runtime import QueryRuntime


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
    assert suite.report_stem == "agent_system_live_agent_smoke_v4"
    assert suite.future_frozen_evaluation == "not_constructed"
    assert len(suite.trials) == 5
    assert {trial.kind for trial in suite.trials} == {"query"}
    assert {trial.expected_role for trial in suite.trials} == {"query"}
    assert suite.required_source_ids == (
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


def test_ingestion_hybridrag_suite_has_three_natural_language_routes() -> None:
    suite = load_live_evaluation_suite(
        "data/evaluation/agent_system/"
        "live_ingestion_hybridrag_smoke_v1.yaml"
    )

    assert suite.report_stem == (
        "agent_system_live_ingestion_hybridrag_smoke_v1"
    )
    assert suite.required_source_ids == (
        "2026-05-19:123",
        "2026-05-19:138",
    )
    assert [trial.required_tool_names for trial in suite.trials] == [
        ("semantic_search_sources", "read_source"),
        ("read_tmi_event_facts", "read_tmi_event_graph"),
        ("read_tmi_operational_context", "read_public_observations"),
    ]
    assert all(
        tool_name not in trial.question
        for trial in suite.trials
        for tool_name in live_eval.HYBRID_QUERY_READ_TOOLS
    )


def test_flagship_walkthrough_suite_is_one_natural_cross_source_query() -> None:
    suite = load_live_evaluation_suite(
        "data/evaluation/agent_system/"
        "live_flagship_gdp138_walkthrough_v1.yaml"
    )

    expected_question = (
        "What did ATCSCC publish for JFK in Advisory 138? Verify the "
        "source-declared reason from the original record, then summarize "
        "the time-aligned Weather reports and BTS public observations "
        "without inferring causality."
    )
    assert suite.version == "live-agent-smoke-v4"
    assert suite.suite_id == "flagship-gdp138-walkthrough-v1"
    assert suite.report_stem == (
        "agent_system_live_flagship_gdp138_walkthrough_v1"
    )
    assert suite.future_frozen_evaluation == "not_constructed"
    assert suite.required_source_ids == ("2026-05-19:138",)
    assert len(suite.trials) == 1

    trial = suite.trials[0]
    assert trial.kind == "query"
    assert trial.expected_role == "query"
    assert trial.source_id == "2026-05-19:138"
    assert trial.question == expected_question
    assert trial.required_tool_names == (
        "read_tmi_event_facts",
        "read_source",
        "read_tmi_operational_context",
        "read_public_observations",
    )
    assert all(
        tool_name not in trial.question
        for tool_name in live_eval.HYBRID_QUERY_READ_TOOLS
    )


def test_suite_rejects_unsafe_report_stem() -> None:
    with pytest.raises(ValueError):
        LiveEvaluationSuite(
            version="live-agent-smoke-v4",
            suite_id="invalid-report-stem",
            report_stem="../overwrite-historical-report",
            trials=(_trial(),),
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
    assert "corpus_batch" not in source
    assert "corpus_query" not in source
    assert "corpus_store" not in source
    assert "build_corpus_batch" not in source
    assert "answer_corpus_question" not in source


def test_live_evaluator_uses_the_current_nine_read_tools() -> None:
    assert live_eval.HYBRID_QUERY_READ_TOOLS == {
        "find_tmi_events",
        "read_tmi_event_facts",
        "read_tmi_operational_context",
        "read_public_observations",
        "read_tmi_event_graph",
        "find_similar_tmi_events",
        "search_source_text",
        "semantic_search_sources",
        "read_source",
    }
    assert "store_dir" in inspect.signature(
        run_live_agent_evaluation
    ).parameters


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


def test_query_run_artifact_preserves_exact_source_record_bindings() -> None:
    trial = _trial(
        required_tool_names=("read_source",),
        required_graph_path_kinds=(),
    )
    statement = HybridQueryStatement(
        kind="source_record",
        text="The exact advisory source states that the TMI is a GDP.",
        support_source_ids=("2026-05-20:084",),
        support_source_version_ids=("source-version:084",),
        support_source_anchor_ids=("anchor:084:line-1",),
        support_chunk_ids=("chunk:084:1",),
    )
    support = HybridQuerySupportRecord(
        kind="source_record",
        source_ids=("2026-05-20:084",),
        source_version_ids=("source-version:084",),
        source_anchor_ids=("anchor:084:line-1",),
        chunk_ids=("chunk:084:1",),
    )
    outcome = QueryToolOutcome(
        status="ok",
        answer=statement.text,
        source_ids=["2026-05-20:084"],
        retrieved_source_version_ids=["source-version:084"],
        retrieved_source_anchor_ids=["anchor:084:line-1"],
        retrieved_chunk_ids=["chunk:084:1"],
        answer_statements=[statement],
        support_records=[support],
        model_calls=[
            _live_call(tool_name="read_source", raw_response=""),
        ],
        tool_calls=[
            QueryToolTrace(
                tool_call_id="trace:source",
                tool="read_source",
                status="ok",
                result_refs=["source-version:084", "anchor:084:line-1"],
                source_ids=["2026-05-20:084"],
                source_version_ids=["source-version:084"],
                source_anchor_ids=["anchor:084:line-1"],
                chunk_ids=["chunk:084:1"],
            )
        ],
    )

    artifact = build_hybrid_query_run_artifact(
        trial=trial,
        event_id="urn:event:084",
        outcome=outcome,
    )

    assert artifact.statements[0].kind == "source_record"
    assert artifact.statements[0].source_version_ids == (
        "source-version:084",
    )
    assert artifact.support_records[0].source_anchor_ids == (
        "anchor:084:line-1",
    )
    assert artifact.tools[0].chunk_ids == ("chunk:084:1",)


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
    report = paths[-1].read_text(encoding="utf-8")
    assert "- Provider calls: 4" in report
    assert "- Input / output tokens: 40 / 20" in report


def test_artifact_writer_accepts_a_suite_specific_report_stem(
    tmp_path: Path,
) -> None:
    results = (_result("passed"),)
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
        report_stem="agent_system_live_ingestion_hybridrag_smoke_v1",
    )

    assert [path.name for path in paths] == [
        "live_evaluation_results_v4.jsonl",
        "live_evaluation_manifest_v4.json",
        "agent_system_live_ingestion_hybridrag_smoke_v1.json",
        "agent_system_live_ingestion_hybridrag_smoke_v1.md",
    ]


def test_live_artifacts_separate_raw_provider_and_parsed_outputs(
    tmp_path: Path,
) -> None:
    trial = _trial(required_tool_names=(), required_graph_path_kinds=())
    provider_call = LiveEvaluationProviderCall.from_model_call(
        suite_id="suite",
        repetition=1,
        trial=trial,
        phase="query_step",
        record=_live_call(
            tool_name="read_source",
            raw_response="native provider content",
        ),
        native_response={
            "content": "native provider content",
            "tool_calls": [
                {
                    "name": "read_source",
                    "args": {"source_id": trial.source_id},
                }
            ],
        },
    )
    result = _result(trial.trial_id).model_copy(
        update={
            "source_id": trial.source_id,
            "provider_call_count": 1,
            "provider_call_ids": (provider_call.call_id,),
            "input_tokens": provider_call.input_tokens,
            "output_tokens": provider_call.output_tokens,
        }
    )
    results = (result,)
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
        provider_calls=(provider_call,),
    )

    raw_path = tmp_path / "runtime" / "raw_responses_v4.jsonl"
    assert raw_path.exists()
    assert "native provider content" in raw_path.read_text(encoding="utf-8")
    report_json = json.loads(paths[-2].read_text(encoding="utf-8"))
    assert report_json["artifacts"]["raw_response_count"] == 1
    assert report_json["artifacts"]["successful_real_call_count"] == 1
    assert report_json["artifacts"]["failed_real_call_count"] == 0
    assert report_json["artifacts"]["raw_parsed_binding_status"] == "valid"
    assert report_json["artifacts"]["raw_response_artifact"] == str(raw_path)
    assert (
        report_json["artifacts"]["parsed_output_artifact"]
        == str(paths[0])
    )
    assert "native provider content" not in paths[-2].read_text(
        encoding="utf-8"
    )


def test_live_call_binding_rejects_orphan_raw_calls() -> None:
    trial = _trial(required_tool_names=(), required_graph_path_kinds=())
    provider_call = LiveEvaluationProviderCall.from_model_call(
        suite_id="suite",
        repetition=1,
        trial=trial,
        phase="query_step",
        record=_live_call(),
        native_response={"content": "returned"},
    )
    result = _result(trial.trial_id).model_copy(
        update={
            "source_id": trial.source_id,
            "provider_call_count": 0,
            "provider_call_ids": (),
        }
    )

    failures = live_eval._provider_call_binding_failures(
        (result,),
        (provider_call,),
    )

    assert "activated_trial_missing_raw_provider_call" in failures
    assert "orphan_raw_provider_call" in failures


def test_missing_authorization_rejects_before_writes(tmp_path: Path) -> None:
    with pytest.raises(LiveEvaluationAuthorizationError):
        run_live_agent_evaluation(
            config_path="configs/aviation_knowledge_v1.yaml",
            suite_path=(
                "data/evaluation/agent_system/live_agent_smoke_v4.yaml"
            ),
            store_dir=tmp_path / "store",
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
        "open_query_runtime",
        lambda *_args, **_kwargs: pytest.fail("store must not open"),
    )

    summary = run_live_agent_evaluation(
        config_path="configs/aviation_knowledge_v1.yaml",
        suite_path="data/evaluation/agent_system/live_agent_smoke_v4.yaml",
        store_dir=tmp_path / "store",
        output_dir=tmp_path / "runtime",
        report_dir=tmp_path / "reports",
        allow_live_model=True,
        repetitions=1,
    )

    assert summary.runner_status == "blocked_before_run"
    assert summary.provider_call_count == 0
    assert "missing_deepseek_credentials" in summary.runner_detail_codes


def test_blocked_runner_uses_suite_specific_report_stem(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(live_eval, "load_environment", lambda: None)
    monkeypatch.setattr(
        live_eval,
        "open_query_runtime",
        lambda *_args, **_kwargs: pytest.fail("store must not open"),
    )

    run_live_agent_evaluation(
        config_path="configs/aviation_knowledge_v1.yaml",
        suite_path=(
            "data/evaluation/agent_system/"
            "live_ingestion_hybridrag_smoke_v1.yaml"
        ),
        store_dir=tmp_path / "store",
        output_dir=tmp_path / "runtime",
        report_dir=tmp_path / "reports",
        allow_live_model=True,
        repetitions=1,
    )

    assert (
        tmp_path
        / "reports"
        / "agent_system_live_ingestion_hybridrag_smoke_v1.json"
    ).is_file()
    assert (
        tmp_path
        / "reports"
        / "agent_system_live_ingestion_hybridrag_smoke_v1.md"
    ).is_file()


def test_live_runner_reads_existing_store_without_building_a_corpus(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class ExistingStore:
        dataset_id = "dataset:live-store"

        def __init__(self) -> None:
            self.closed = False

        def list_tmi_event_publications(self, *, active_only: bool = False):
            assert active_only
            return tuple(
                SimpleNamespace(
                    event_id=f"urn:event:{source_id.rsplit(':', 1)[-1]}",
                    advisory_source_id=source_id,
                )
                for source_id in (
                    "2026-05-20:084",
                    "2026-05-20:115",
                    "2026-05-20:159",
                )
            )

        def get_knowledge_revision(self) -> int:
            return 7

        def close(self) -> None:
            self.closed = True

    store = ExistingStore()
    runtime = QueryRuntime(
        store=store,  # type: ignore[arg-type]
        source_index=None,
        event_index=None,
    )
    vector = EvaluationVectorBinding(
        collection_name="test",
        representation_version="v1",
        embedding_model_id="test/model",
        embedding_dimension=2,
        indexed_knowledge_revision=7,
        document_ids=(),
    )
    binding = EvaluationDataBinding(
        store_schema_version="aviation-evidence-store-v1",
        dataset_id=store.dataset_id,
        knowledge_revision=7,
        required_source_versions={},
        required_source_hashes={},
        required_event_publication_ids=(),
        source_candidate_version_ids=(),
        event_candidate_publication_ids=(),
        source_vector_index=vector,
        event_vector_index=vector.model_copy(
            update={"collection_name": "events"}
        ),
        validation_profile_checksums=(),
    )
    opened: list[Path] = []
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-only")
    monkeypatch.setattr(live_eval, "load_environment", lambda: None)
    monkeypatch.setattr(
        live_eval,
        "open_query_runtime",
        lambda _config, *, store_dir, allow_model_download: (
            opened.append(Path(store_dir)) or runtime
        ),
    )
    monkeypatch.setattr(
        live_eval,
        "_bind_live_query_runtime",
        lambda **_kwargs: binding,
    )
    monkeypatch.setattr(
        live_eval,
        "_verify_live_evaluation_binding",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        live_eval,
        "_provider_call_binding_failures",
        lambda *_args, **_kwargs: (),
    )

    def answer_from_existing_store(*, runtime, question, scope, model_factory):
        del question, model_factory
        assert runtime is not None
        assert scope.event_id is not None
        trial = next(
            trial
            for trial in load_live_evaluation_suite(
                "data/evaluation/agent_system/live_agent_smoke_v4.yaml"
            ).trials
            if trial.source_id.endswith(scope.event_id.rsplit(":", 1)[-1])
        )
        return _supported_graph_outcome(
            tool_name=trial.required_tool_names[0],
        )

    monkeypatch.setattr(
        live_eval,
        "answer_question",
        answer_from_existing_store,
    )
    suite_path = tmp_path / "custom-report-suite.yaml"
    suite_path.write_text(
        Path(
            "data/evaluation/agent_system/live_agent_smoke_v4.yaml"
        )
        .read_text(encoding="utf-8")
        .replace(
            "suite_id: tmi-event-query-agent-smoke-v4\n",
            "suite_id: tmi-event-query-agent-smoke-v4\n"
            "report_stem: custom_completed_smoke\n",
        ),
        encoding="utf-8",
    )
    store_dir = tmp_path / "existing-store"
    summary = run_live_agent_evaluation(
        config_path="configs/aviation_knowledge_v1.yaml",
        suite_path=suite_path,
        store_dir=store_dir,
        output_dir=tmp_path / "runtime",
        report_dir=tmp_path / "reports",
        allow_live_model=True,
        repetitions=1,
    )

    assert opened == [store_dir]
    assert summary.runner_status == "completed"
    assert summary.provider_call_count == 10
    assert (tmp_path / "runtime" / "evaluation_data_binding.json").is_file()
    assert not (tmp_path / "runtime" / "corpus").exists()
    assert (
        tmp_path / "reports" / "custom_completed_smoke.json"
    ).is_file()
    assert (
        tmp_path / "reports" / "custom_completed_smoke.md"
    ).is_file()
    assert store.get_knowledge_revision() == 7
    assert store.closed


def test_later_trial_failure_preserves_completed_real_call_accounting(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A later runner error must not erase an earlier provider-backed result."""

    first = _trial()
    second = first.model_copy(
        update={
            "trial_id": "query-115",
            "source_id": "2026-05-20:115",
        }
    )
    suite = SimpleNamespace(
        repetitions=1,
        trials=(first, second),
    )

    class Store:
        def list_tmi_event_publications(self, *, active_only: bool = False):
            assert active_only
            return (
                SimpleNamespace(
                    event_id="urn:event:084",
                    advisory_source_id=first.source_id,
                ),
                SimpleNamespace(
                    event_id="urn:event:115",
                    advisory_source_id=second.source_id,
                ),
            )

    runtime = QueryRuntime(
        store=Store(),  # type: ignore[arg-type]
        source_index=None,
        event_index=None,
    )
    monkeypatch.setattr(
        live_eval,
        "_verify_live_evaluation_binding",
        lambda *_args, **_kwargs: None,
    )
    attempts = 0

    def answer_once(**_kwargs):
        nonlocal attempts
        attempts += 1
        if attempts == 2:
            raise RuntimeError("later trial failed")
        return _supported_graph_outcome()

    monkeypatch.setattr(live_eval, "answer_question", answer_once)

    results, details = live_eval._run_live_evaluation_repetition(
        suite=suite,  # type: ignore[arg-type]
        runtime=runtime,
        binding=object(),  # type: ignore[arg-type]
        runtime_root=tmp_path,
        repetition=1,
    )

    assert len(results) == 2
    assert results[0].trial_id == first.trial_id
    assert results[0].provider_call_count == 2
    assert results[0].model_acceptance_status == "passed"
    assert results[1].trial_id == second.trial_id
    assert results[1].model_acceptance_status == "not_run"
    assert details == ("repetition_001_query-115_runner_exception",)


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
