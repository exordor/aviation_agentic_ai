from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import pytest
import yaml

import aviation_agentic_ai.agent_system.live_agent_evaluation as live_eval
from aviation_agentic_ai.agent_system.agent_usage import AgentUsageRecord
from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryStatement,
    HybridQuerySupportRecord,
    ModelCallRecord,
    ModelToolCall,
    QueryToolOutcome,
    QueryToolTrace,
)
from aviation_agentic_ai.agent_system.corpus_batch import BatchCaseExecution
from aviation_agentic_ai.agent_system.corpus_store import CorpusBuildResult
from aviation_agentic_ai.agent_system.live_agent_evaluation import (
    LiveEvaluationAssertion,
    LiveEvaluationAuthorizationError,
    LiveEvaluationResult,
    LiveEvaluationSuite,
    LiveEvaluationTrial,
    build_hybrid_query_run_artifact,
    load_live_evaluation_suite,
    run_live_agent_evaluation,
    score_analysis_trial,
    score_assembly_trial,
    summarize_live_evaluation,
    write_hybrid_query_run_artifact,
    write_live_evaluation_artifacts,
)


def test_load_live_evaluation_suite_seals_frozen_trials(tmp_path: Path) -> None:
    suite_path = tmp_path / "suite.yaml"
    suite_path.write_text(
        """
version: live-agent-smoke-v2
suite_id: decision-case-live-agent-smoke-v2
repetitions: 1
trials:
  - trial_id: assembly-025
    kind: assembly
    source_id: "2026-05-20:025"
    expected_role: decision_case_assembly
    forbidden_predicate_iris:
      - https://data.nasa.gov/ontologies/atmonto/ATM#impactingCondition
  - trial_id: analysis-138
    kind: analysis
    source_id: "2026-05-19:138"
    expected_role: query
    question: What public operational situation is recorded?
""".strip()
        + "\n",
        encoding="utf-8",
    )

    suite = load_live_evaluation_suite(suite_path)

    assert isinstance(suite, LiveEvaluationSuite)
    assert suite.repetitions == 1
    assert [trial.kind for trial in suite.trials] == ["assembly", "analysis"]
    assert suite.build_source_ids == (
        "2026-05-19:138",
        "2026-05-20:025",
    )


def test_tracked_live_suite_contains_exactly_five_frozen_trials() -> None:
    suite = load_live_evaluation_suite(
        "data/evaluation/agent_system/live_agent_smoke_v2.yaml"
    )

    assert [
        (trial.kind, trial.source_id, trial.question)
        for trial in suite.trials
    ] == [
        ("assembly", "2026-05-20:025", None),
        ("assembly", "2026-05-20:030", None),
        ("assembly", "2026-05-20:070", None),
        ("assembly", "2026-05-20:072", None),
        (
            "analysis",
            "2026-05-19:138",
            "What public operational situation is recorded?",
        ),
    ]
    assert suite.repetitions == 1


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


def _result(
    trial_id: str,
    *,
    status: str = "passed",
    live_model: bool = False,
) -> LiveEvaluationResult:
    return LiveEvaluationResult(
        trial_id=trial_id,
        repetition=1,
        kind="assembly",
        source_id=f"source:{trial_id}",
        role="decision_case_assembly",
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
        prompt_set_id="decision-case-agents-v1",
        prompt_version="v1",
        temperature=0.0,
        provider_call_count=2,
        native_tool_call_count=1,
        bound_tool_execution_count=0,
        input_tokens=20,
        output_tokens=10,
        provider_latency_ms=25.0,
    )


def test_summary_is_derived_from_trials_and_blocked_never_passes() -> None:
    results = (
        *(_result(f"passed-{index}") for index in range(4)),
        _result("blocked", status="blocked"),
    )

    summary = summarize_live_evaluation(
        suite_id="suite",
        suite_checksum="a" * 64,
        repetitions=1,
        results=results,
        runner_status="completed",
        live_model=False,
    )

    assert summary.runner_status == "completed"
    assert summary.model_acceptance_status == "failed"
    assert summary.trial_count == 5
    assert summary.passed_count == 4
    assert summary.blocked_count == 1
    assert summary.live_model is False
    assert summary.provider_call_count == 10


def test_summary_rejects_mixed_live_and_offline_trial_labels() -> None:
    with pytest.raises(ValueError, match="live_model flag"):
        summarize_live_evaluation(
            suite_id="suite",
            suite_checksum="a" * 64,
            repetitions=1,
            results=(_result("live", live_model=True),),
            runner_status="completed",
            live_model=False,
        )


def test_report_projection_contains_only_sanitized_metrics(tmp_path: Path) -> None:
    result = _result("safe")
    summary = summarize_live_evaluation(
        suite_id="suite",
        suite_checksum="b" * 64,
        repetitions=1,
        results=(result,),
        runner_status="completed",
        live_model=False,
    )

    reports = tmp_path / "reports"
    reports.mkdir()
    legacy_report = reports / "agent_system_live_agent_smoke_v1.json"
    legacy_report.write_text("historical-v1\n", encoding="utf-8")
    paths = write_live_evaluation_artifacts(
        output_dir=tmp_path / "runtime",
        report_dir=reports,
        results=(result,),
        summary=summary,
    )
    serialized = "\n".join(
        path.read_text(encoding="utf-8") for path in paths
    )

    assert paths[0].name == "live_evaluation_results_v2.jsonl"
    assert paths[1].name == "live_evaluation_manifest_v2.json"
    assert paths[2].name == "agent_system_live_agent_smoke_v2.json"
    assert paths[3].name == "agent_system_live_agent_smoke_v2.md"
    assert legacy_report.read_text(encoding="utf-8") == "historical-v1\n"
    assert "deepseek-v4-pro" in serialized
    assert "raw_response" not in serialized
    assert "tool_arguments" not in serialized
    assert "tool_result" not in serialized
    assert "<think>" not in serialized
    assert "sk-secret" not in serialized


def _write_frozen_suite(path: Path) -> Path:
    path.write_text(
        yaml.safe_dump(
            {
                "version": "live-agent-smoke-v2",
                "suite_id": "decision-case-live-agent-smoke-v2",
                "repetitions": 1,
                "trials": [
                    {
                        "trial_id": "assembly-025",
                        "kind": "assembly",
                        "source_id": "2026-05-20:025",
                        "expected_role": "decision_case_assembly",
                    },
                    {
                        "trial_id": "analysis-138",
                        "kind": "analysis",
                        "source_id": "2026-05-19:138",
                        "expected_role": "query",
                        "question": (
                            "What public operational situation is recorded?"
                        ),
                    },
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def _write_preflight_config(
    path: Path,
    source_root: Path,
    *,
    missing_key: str | None = None,
) -> Path:
    source_keys = (
        "atcscc_advisories",
        "stationinfo",
        "metar",
        "taf",
        "nasr_zip",
        "nasr_manifest",
        "pilot_controller_glossary",
        "term_seed",
        "bts_on_time_manifest",
        "bts_on_time_snapshot",
    )
    sources: dict[str, str] = {}
    source_root.mkdir(parents=True, exist_ok=True)
    for key in source_keys:
        source_path = source_root / f"{key}.dat"
        if key != missing_key:
            source_path.write_text("fixture\n", encoding="utf-8")
        sources[key] = str(source_path)
    path.write_text(
        yaml.safe_dump(
            {
                "cohort": {
                    "advisory_input": sources["atcscc_advisories"],
                    "airport_codes": ["JFK"],
                    "expected_record_count": 1,
                },
                "sources": sources,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def test_live_runner_requires_explicit_authorization_before_writes(
    tmp_path: Path,
) -> None:
    config_path = _write_preflight_config(
        tmp_path / "config.yaml",
        tmp_path / "sources",
    )
    suite_path = _write_frozen_suite(tmp_path / "suite.yaml")
    output_dir = tmp_path / "runtime"

    with pytest.raises(LiveEvaluationAuthorizationError):
        run_live_agent_evaluation(
            config_path=config_path,
            suite_path=suite_path,
            output_dir=output_dir,
            report_dir=tmp_path / "reports",
            allow_live_model=False,
            repetitions=1,
        )

    assert not output_dir.exists()


def test_public_live_runner_has_no_fake_factory_injection() -> None:
    parameters = inspect.signature(run_live_agent_evaluation).parameters

    assert "model_factory" not in parameters
    assert "case_runner" not in parameters
    assert "resource_loader" not in parameters


def test_missing_credentials_blocks_before_corpus_build(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = _write_preflight_config(
        tmp_path / "config.yaml",
        tmp_path / "sources",
    )
    suite_path = _write_frozen_suite(tmp_path / "suite.yaml")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.setattr(
        live_eval,
        "build_corpus_batch",
        lambda *args, **kwargs: pytest.fail("corpus build must not run"),
        raising=False,
    )

    summary = run_live_agent_evaluation(
        config_path=config_path,
        suite_path=suite_path,
        output_dir=tmp_path / "runtime",
        report_dir=tmp_path / "reports",
        allow_live_model=True,
        repetitions=1,
    )

    assert summary.runner_status == "blocked_before_run"
    assert summary.model_acceptance_status == "blocked"
    assert summary.trial_count == 0
    assert summary.provider_call_count == 0


def test_missing_required_source_blocks_before_corpus_build(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config_path = _write_preflight_config(
        tmp_path / "config.yaml",
        tmp_path / "sources",
        missing_key="metar",
    )
    suite_path = _write_frozen_suite(tmp_path / "suite.yaml")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "fixture-key")
    monkeypatch.setattr(
        live_eval,
        "build_corpus_batch",
        lambda *args, **kwargs: pytest.fail("corpus build must not run"),
        raising=False,
    )

    summary = run_live_agent_evaluation(
        config_path=config_path,
        suite_path=suite_path,
        output_dir=tmp_path / "runtime",
        report_dir=tmp_path / "reports",
        allow_live_model=True,
        repetitions=1,
    )

    assert summary.runner_status == "blocked_before_run"
    assert summary.trial_count == 0
    assert summary.provider_call_count == 0


def test_batch_case_execution_can_return_transient_model_metadata() -> None:
    record = ModelCallRecord(
        agent="decision_case_assembly",
        raw_response="never persisted by evaluator",
        provider="deepseek",
        model="deepseek-v4-pro",
        temperature=0.0,
    )

    execution = BatchCaseExecution(
        result=CorpusBuildResult(
            source_id="2026-05-20:025",
            status="insufficient",
        ),
        model_calls=(record,),
    )

    assert execution.model_calls == (record,)


def _assembly_usage(
    *,
    outcome: str = "accepted",
    detail_status: str = "partial",
) -> AgentUsageRecord:
    return AgentUsageRecord(
        source_id="2026-05-20:025",
        event_id="urn:event:025",
        task_id="task:assembly:025",
        role="decision_case_assembly",
        task_scope="decision_case",
        execution_mode="activated",
        outcome=outcome,
        detail_status=detail_status,
        activation_reason="noncanonical_evidence_or_schema_choice",
        provider_call_count=2,
        tool_call_count=2,
        input_tokens=80,
        output_tokens=40,
        provider_latency_ms=50,
        tool_latency_ms=5,
    )


def _live_call(
    *,
    agent: str,
    tool_name: str | None = None,
    raw_response: str = "provider payload must never enter the report",
    error: str | None = None,
) -> ModelCallRecord:
    return ModelCallRecord(
        agent=agent,
        raw_response=raw_response,
        prompt_set_id="decision-case-agents-v1",
        prompt_version=f"{agent}-v1",
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
                    arguments={"step_id": "step:1"},
                )
            ]
            if tool_name
            else []
        ),
    )


def test_assembly_scoring_requires_agent_activation_partial_publication() -> None:
    trial = LiveEvaluationTrial(
        trial_id="assembly-025",
        kind="assembly",
        source_id="2026-05-20:025",
        expected_role="decision_case_assembly",
        forbidden_predicate_iris=(
            "https://data.nasa.gov/ontologies/atmonto/ATM#impactingCondition",
        ),
    )

    result = score_assembly_trial(
        trial=trial,
        repetition=1,
        live_model=False,
        build_result=CorpusBuildResult(
            source_id=trial.source_id,
            status="ok",
            event_id="urn:event:025",
            case_id="urn:event:025",
        ),
        usage=_assembly_usage(),
        model_calls=(
            _live_call(
                agent="decision_case_assembly",
                tool_name="get_case_evidence",
            ),
            _live_call(agent="decision_case_assembly"),
        ),
        fact_predicate_iris=(
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
        ),
        context_causal_claims=(False, False),
        observation_profile_layers=("public_operational_observation",),
    )

    assert result.live_model is False
    assert result.workflow_status == "ok"
    assert result.activation_status == "activated"
    assert result.model_acceptance_status == "passed"
    assert result.provider_call_count == 2
    assert result.native_tool_call_count == 1
    assert all(assertion.passed for assertion in result.assertions)
    assert "provider payload" not in result.model_dump_json()


def test_assembly_scoring_records_real_contract_failure_without_passing() -> None:
    trial = LiveEvaluationTrial(
        trial_id="assembly-025",
        kind="assembly",
        source_id="2026-05-20:025",
        expected_role="decision_case_assembly",
    )

    result = score_assembly_trial(
        trial=trial,
        repetition=1,
        live_model=False,
        build_result=CorpusBuildResult(
            source_id=trial.source_id,
            status="insufficient",
            reason="model output did not satisfy the contract",
            provider_call_count=2,
        ),
        usage=_assembly_usage(
            outcome="abstained",
            detail_status="insufficient",
        ),
        model_calls=(
            _live_call(agent="decision_case_assembly"),
            _live_call(agent="decision_case_assembly"),
        ),
        fact_predicate_iris=(),
        context_causal_claims=(),
        observation_profile_layers=(),
    )

    assert result.workflow_status == "insufficient"
    assert result.activation_status == "activated"
    assert result.model_acceptance_status == "failed"
    assert result.failure_code == "assembly_acceptance_failed"


def test_assembly_scoring_classifies_output_token_cap_as_model_failure() -> None:
    trial = LiveEvaluationTrial(
        trial_id="assembly-025",
        kind="assembly",
        source_id="2026-05-20:025",
        expected_role="decision_case_assembly",
    )

    result = score_assembly_trial(
        trial=trial,
        repetition=1,
        live_model=False,
        build_result=CorpusBuildResult(
            source_id=trial.source_id,
            status="insufficient",
            reason="Decision Case Assembly Agent output-token cap exceeded",
            provider_call_count=2,
        ),
        usage=_assembly_usage(
            outcome="blocked",
            detail_status="blocked",
        ),
        model_calls=(
            _live_call(agent="decision_case_assembly"),
            _live_call(agent="decision_case_assembly"),
        ),
        fact_predicate_iris=(),
        context_causal_claims=(),
        observation_profile_layers=(),
    )

    assert result.model_acceptance_status == "failed"
    assert result.failure_code == "assembly_output_token_cap_exceeded"


def _supported_query_outcome(*, statement_text: str) -> QueryToolOutcome:
    return QueryToolOutcome(
        status="ok",
        answer=statement_text,
        source_ids=["bts:on-time:2026-05"],
        retrieved_fact_ids=["fact:observation"],
        retrieved_observation_ids=["observation:active"],
        answer_statements=[
            HybridQueryStatement(
                kind="public_observation",
                text=statement_text,
                support_fact_ids=("fact:observation",),
                support_observation_ids=("observation:active",),
                support_source_ids=("bts:on-time:2026-05",),
            )
        ],
        support_records=[
            HybridQuerySupportRecord(
                kind="public_observation",
                fact_ids=("fact:observation",),
                observation_ids=("observation:active",),
                source_ids=("bts:on-time:2026-05",),
            )
        ],
        model_calls=[
            _live_call(
                agent="query",
                tool_name="read_public_observations",
                raw_response="",
            ),
            _live_call(
                agent="query",
                raw_response="sk-secret raw model payload must be ignored",
            ),
        ],
        tool_calls=[
            QueryToolTrace(
                tool_call_id="trace:1",
                tool="read_public_observations",
                arguments={"event_id": "urn:event:gdp-138"},
                result_refs=[
                    "fact:observation",
                    "observation:active",
                ],
                observation_ids=["observation:active"],
                source_ids=["bts:on-time:2026-05"],
                status="ok",
            )
        ],
    )


def test_hybrid_query_run_artifact_is_sanitized_and_drives_scoring(
    tmp_path: Path,
) -> None:
    trial = LiveEvaluationTrial(
        trial_id="query-gdp-138",
        kind="analysis",
        source_id="2026-05-19:138",
        expected_role="query",
        question="What public operational situation is recorded?",
    )
    outcome = _supported_query_outcome(
        statement_text=(
            "BTS reports source-qualified active-period observations."
        )
    )
    query_run = build_hybrid_query_run_artifact(
        trial=trial,
        event_id="urn:event:gdp-138",
        outcome=outcome,
    )
    artifact_path = write_hybrid_query_run_artifact(
        tmp_path / "query",
        query_run,
    )

    result = score_analysis_trial(
        trial=trial,
        repetition=1,
        live_model=False,
        event_id="urn:event:gdp-138",
        outcome=outcome,
        query_run=query_run,
        query_run_artifact_path=artifact_path,
    )

    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    serialized = artifact_path.read_text(encoding="utf-8")
    assert artifact_path.name == "hybrid_query_run.json"
    assert payload["statements"][0]["kind"] == "public_observation"
    assert payload["statements"][0]["observation_ids"] == [
        "observation:active"
    ]
    assert payload["support_records"][0] == {
        "kind": "public_observation",
        "case_ids": [],
        "fact_ids": ["fact:observation"],
        "profile_gap_ids": [],
        "context_association_ids": [],
        "observation_ids": ["observation:active"],
        "graph_path_ids": [],
        "source_ids": ["bts:on-time:2026-05"],
    }
    assert payload["tools"][0] == {
        "name": "read_public_observations",
        "status": "ok",
        "reference_ids": [
            "fact:observation",
            "observation:active",
        ],
        "source_ids": ["bts:on-time:2026-05"],
    }
    assert "arguments" not in serialized
    assert "raw_response" not in serialized
    assert "provider payload" not in serialized
    assert "sk-secret" not in serialized
    assert result.workflow_status == "ok"
    assert result.activation_status == "activated"
    assert result.model_acceptance_status == "passed"
    assert result.bound_tool_execution_count == 1
    assert result.query_run_artifact == str(artifact_path)
    assert result.query_run_artifact_sha256 == hashlib.sha256(
        artifact_path.read_bytes()
    ).hexdigest()


@pytest.mark.parametrize(
    ("statement_text", "expected_failed_check"),
    [
        (
            "BTS observations prove FAA arrival capacity caused the decision.",
            "statement_claim_boundaries",
        ),
    ],
)
def test_hybrid_query_scoring_rejects_claim_boundary_violations(
    statement_text: str,
    expected_failed_check: str,
) -> None:
    trial = LiveEvaluationTrial(
        trial_id="query-gdp-138",
        kind="analysis",
        source_id="2026-05-19:138",
        expected_role="query",
        question="What public operational situation is recorded?",
    )
    outcome = _supported_query_outcome(statement_text=statement_text)
    query_run = build_hybrid_query_run_artifact(
        trial=trial,
        event_id="urn:event:gdp-138",
        outcome=outcome,
    )

    result = score_analysis_trial(
        trial=trial,
        repetition=1,
        live_model=False,
        event_id="urn:event:gdp-138",
        outcome=outcome,
        query_run=query_run,
    )

    failed_checks = {
        assertion.check_id
        for assertion in result.assertions
        if not assertion.passed
    }
    assert expected_failed_check in failed_checks
    assert result.model_acceptance_status == "failed"


def test_hybrid_query_scoring_rejects_statement_citation_not_in_tool_trace() -> None:
    trial = LiveEvaluationTrial(
        trial_id="query-gdp-138",
        kind="analysis",
        source_id="2026-05-19:138",
        expected_role="query",
        question="What public operational situation is recorded?",
    )
    outcome = _supported_query_outcome(
        statement_text="BTS reports an active-period observation."
    )
    outcome = outcome.model_copy(
        update={
            "answer_statements": [
                HybridQueryStatement(
                    kind="public_observation",
                    text="BTS reports an active-period observation.",
                    support_fact_ids=("fact:not-returned",),
                    support_observation_ids=("observation:active",),
                    support_source_ids=("bts:on-time:2026-05",),
                )
            ]
        }
    )
    query_run = build_hybrid_query_run_artifact(
        trial=trial,
        event_id="urn:event:gdp-138",
        outcome=outcome,
    )

    result = score_analysis_trial(
        trial=trial,
        repetition=1,
        live_model=False,
        event_id="urn:event:gdp-138",
        outcome=outcome,
        query_run=query_run,
    )

    assert query_run.statements[0].citation_valid is False
    assert any(
        assertion.check_id == "statement_citations"
        and not assertion.passed
        for assertion in result.assertions
    )
    assert result.model_acceptance_status == "failed"


def test_analysis_contract_rejection_is_failed_not_runner_blocked() -> None:
    trial = LiveEvaluationTrial(
        trial_id="analysis-gdp-138",
        kind="analysis",
        source_id="2026-05-19:138",
        expected_role="query",
        question="What public operational situation is recorded?",
    )
    outcome = QueryToolOutcome(
        status="blocked",
        source_ids=["bts:on-time:2026-05"],
        retrieved_fact_ids=["fact:observation"],
        model_calls=[
            _live_call(
                agent="query",
                tool_name="read_public_observations",
            )
        ],
        tool_calls=[
            QueryToolTrace(
                tool_call_id="trace:1",
                tool="read_public_observations",
                arguments={"event_id": "urn:event:gdp-138"},
                result_refs=["fact:observation"],
                source_ids=["bts:on-time:2026-05"],
                status="ok",
            )
        ],
        failure_reason="model answer failed the typed answer contract",
    )

    result = score_analysis_trial(
        trial=trial,
        repetition=1,
        live_model=False,
        event_id="urn:event:gdp-138",
        outcome=outcome,
    )

    assert result.model_acceptance_status == "failed"
    assert (
        result.failure_code
        == "analysis_answer_contract_or_support_failed"
    )


def test_blocked_corpus_dependency_does_not_activate_analysis() -> None:
    trial = LiveEvaluationTrial(
        trial_id="analysis-gdp-138",
        kind="analysis",
        source_id="2026-05-19:138",
        expected_role="query",
        question="What public operational situation is recorded?",
    )

    result = live_eval._blocked_analysis_result(
        trial=trial,
        repetition=1,
        failure_code="analysis_dependency_corpus_not_published",
        live_model=False,
    )

    assert result.workflow_status == "not_run"
    assert result.activation_status == "not_reached"
    assert result.provider_call_count == 0
    assert result.model_acceptance_status == "not_run"
