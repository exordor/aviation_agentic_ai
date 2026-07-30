from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

from aviation_agentic_ai.agent_system.contracts import (
    ModelCallRecord,
    ModelToolCall,
)
from aviation_agentic_ai.agent_system.live_agent_experiment import (
    LiveAgentExperimentParsedOutput,
    LiveAgentExperimentSuite,
    ObservedProviderCall,
    load_live_agent_experiment_suite,
    run_live_agent_experiment,
    summarize_live_agent_experiment,
    write_live_agent_experiment_artifacts,
)
from aviation_agentic_ai.agent_system.tool_model import (
    _emit_tool_model_call_observation,
    capture_tool_model_calls,
)


def _call(
    index: int,
    *,
    cycle: int = 1,
    trial_id: str = "assembly-025",
    error: str | None = None,
    cache_hit: bool = False,
    model: str = "deepseek-v4-pro",
) -> ObservedProviderCall:
    record = ModelCallRecord(
        agent="decision_case_assembly",
        raw_response=f"real provider response {index}",
        prompt_set_id="decision-case-agents-v1",
        prompt_version="decision-case-assembly-v2",
        provider="deepseek",
        model=model,
        temperature=0.0,
        input_tokens=100,
        output_tokens=20,
        latency_ms=10.0,
        cache_hit=cache_hit,
        attempt=1,
        error=error,
        tool_calls=[
            ModelToolCall(
                call_id=f"provider-call-{index}",
                name="get_case_evidence",
                arguments={"source_id": "2026-05-20:025"},
            )
        ],
    )
    return ObservedProviderCall.from_model_call(
        experiment_id="experiment-v1",
        cycle=cycle,
        trial_id=trial_id,
        kind="assembly",
        source_id="2026-05-20:025",
        phase="select_tool",
        record=record,
        native_response={
            "type": "ai",
            "content": "",
            "tool_calls": [
                {
                    "id": f"provider-call-{index}",
                    "name": "get_case_evidence",
                    "args": {"source_id": "2026-05-20:025"},
                }
            ],
            "response_metadata": {
                "model_name": model,
                "finish_reason": "tool_calls",
                "token_usage": {
                    "prompt_tokens": 100,
                    "prompt_cache_hit_tokens": 60,
                    "prompt_cache_miss_tokens": 40,
                },
            },
        },
    )


def test_tracked_experiment_suite_freezes_real_call_threshold_and_tasks() -> None:
    suite = load_live_agent_experiment_suite(
        "data/evaluation/agent_system/live_agent_experiment_v2.yaml"
    )

    assert isinstance(suite, LiveAgentExperimentSuite)
    assert suite.minimum_successful_calls == 100
    assert suite.minimum_cycles == 12
    assert suite.maximum_cycles == 20
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


def test_pre_refactor_v1_experiment_artifacts_remain_byte_frozen() -> None:
    expected = {
        "data/evaluation/agent_system/live_agent_experiment_v1.yaml": (
            "d4ca31b365e1fb953cb5ac27c4bf088f31b8a4a250f3e83e455185edf004796b"
        ),
        "reports/stages/agent_system_live_agent_experiment_v1.json": (
            "da02b42848b7aa86cc2415f6bf24687ffe9f0e7dff71ee2d5b1a7ef4a3e56e04"
        ),
        "reports/stages/agent_system_live_agent_experiment_v1.md": (
            "f38c1c65fab498d454eab5c9ca15e42a9a832dbba338e605eba7024caea33525"
        ),
    }

    for path, checksum in expected.items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == checksum


def test_call_observer_sees_native_turn_before_workflow_sanitization() -> None:
    observed: list[tuple[str, ModelCallRecord, object]] = []
    record = ModelCallRecord(
        agent="query",
        raw_response="raw text emitted alongside a native tool call",
        provider="deepseek",
        model="deepseek-v4-pro",
        temperature=0.0,
        tool_calls=[
            ModelToolCall(
                call_id="call-1",
                name="read_public_observations",
                arguments={"event_id": "urn:event:gdp-138"},
            )
        ],
    )
    native_response = {
        "content": [
            {"type": "text", "text": "raw multipart response"}
        ],
        "tool_calls": [
            {
                "id": "call-1",
                "name": "read_public_observations",
                "args": {"event_id": "urn:event:gdp-138"},
            }
        ],
        "response_metadata": {"finish_reason": "tool_calls"},
    }

    with capture_tool_model_calls(
        lambda phase, call, native: observed.append(
            (phase, call, native)
        )
    ):
        _emit_tool_model_call_observation(
            "query_step",
            record,
            native_response,
        )

    assert observed == [("query_step", record, native_response)]
    assert observed[0][1].raw_response.startswith("raw text")
    assert observed[0][2] == native_response


def test_call_observer_accepts_all_existing_agent_runtime_phases() -> None:
    observed: list[str] = []
    record = ModelCallRecord(
        agent="decision_case_assembly",
        raw_response='{"status":"partial"}',
        provider="deepseek",
        model="deepseek-v4-pro",
        temperature=0.0,
    )

    with capture_tool_model_calls(
        lambda phase, _call, _native: observed.append(phase)
    ):
        _emit_tool_model_call_observation("emit_proposal", record)
        _emit_tool_model_call_observation("revision", record)
        _emit_tool_model_call_observation("query_step", record)

    assert observed == ["emit_proposal", "revision", "query_step"]


def test_summary_counts_real_provider_returns_separately_from_task_results() -> None:
    calls = tuple(
        _call(index, cycle=(index % 12) + 1)
        for index in range(100)
    )
    parsed = tuple(
        LiveAgentExperimentParsedOutput(
            experiment_id="experiment-v1",
            cycle=cycle,
            trial_id="assembly-025",
            kind="assembly",
            source_id="2026-05-20:025",
            role="decision_case_assembly",
            workflow_status="insufficient",
            model_acceptance_status="failed",
            workflow_provider_call_count=sum(
                call.cycle == cycle for call in calls
            ),
            provider_call_ids=tuple(
                call.call_id for call in calls if call.cycle == cycle
            ),
            parsed_output={"detail_status": "output_token_cap"},
        )
        for cycle in range(1, 13)
    )

    summary = summarize_live_agent_experiment(
        suite_id="suite-v1",
        suite_checksum="a" * 64,
        minimum_successful_calls=100,
        minimum_cycles=12,
        maximum_cycles=20,
        completed_cycles=12,
        calls=calls,
        parsed_outputs=parsed,
        expected_trial_ids=("assembly-025",),
        runner_status="completed",
        raw_response_path="raw_responses.jsonl",
        parsed_output_path="parsed_outputs.jsonl",
    )

    assert summary.model_identifier == "deepseek-v4-pro"
    assert summary.attempted_real_calls == 100
    assert summary.successful_real_calls == 100
    assert summary.failed_real_calls == 0
    assert summary.input_tokens == 10_000
    assert summary.output_tokens == 2_000
    assert summary.provider_prompt_context_cache == "observed_automatic"
    assert summary.provider_prompt_cache_reported_call_count == 100
    assert summary.prompt_cache_hit_tokens == 6_000
    assert summary.prompt_cache_miss_tokens == 4_000
    assert summary.prompt_cache_usage_mismatch_count == 0
    assert summary.prompt_set_ids == ("decision-case-agents-v1",)
    assert summary.prompt_versions == ("decision-case-assembly-v2",)
    assert summary.tool_call_count == 100
    assert summary.invalid_tool_call_count == 0
    assert summary.threshold_satisfied is True
    assert summary.task_passed_count == 0
    assert summary.task_failed_count == 12
    assert summary.workflow_insufficient_count == 12
    assert summary.workflow_blocked_count == 0
    assert summary.call_binding_mismatch_count == 0
    assert summary.missing_trial_execution_count == 0


def test_summary_rejects_cache_or_wrong_model_as_invalid_experiment() -> None:
    calls = (
        _call(1, cache_hit=True),
        _call(2, model="another-model"),
        _call(3, error="provider timeout"),
    )

    summary = summarize_live_agent_experiment(
        suite_id="suite-v1",
        suite_checksum="b" * 64,
        minimum_successful_calls=100,
        minimum_cycles=12,
        maximum_cycles=20,
        completed_cycles=1,
        calls=calls,
        parsed_outputs=(),
        expected_trial_ids=(),
        runner_status="completed",
        raw_response_path="raw_responses.jsonl",
        parsed_output_path="parsed_outputs.jsonl",
    )

    assert summary.attempted_real_calls == 3
    assert summary.successful_real_calls == 0
    assert summary.failed_real_calls == 3
    assert summary.local_cache_hit_count == 1
    assert summary.model_configuration_mismatch_count == 1
    assert summary.integrity_valid is False
    assert summary.threshold_satisfied is False


def test_raw_and_parsed_artifacts_are_separate_and_checksum_bound(
    tmp_path: Path,
) -> None:
    calls = (_call(1),)
    parsed = (
        LiveAgentExperimentParsedOutput(
            experiment_id="experiment-v1",
            cycle=1,
            trial_id="assembly-025",
            kind="assembly",
            source_id="2026-05-20:025",
            role="decision_case_assembly",
            workflow_status="insufficient",
            model_acceptance_status="failed",
            workflow_provider_call_count=1,
            provider_call_ids=(calls[0].call_id,),
            parsed_output={"detail_status": "insufficient"},
        ),
    )
    summary = summarize_live_agent_experiment(
        suite_id="suite-v1",
        suite_checksum="c" * 64,
        minimum_successful_calls=100,
        minimum_cycles=12,
        maximum_cycles=20,
        completed_cycles=1,
        calls=calls,
        parsed_outputs=parsed,
        expected_trial_ids=("assembly-025",),
        runner_status="threshold_not_reached",
        raw_response_path=str(tmp_path / "raw_responses.jsonl"),
        parsed_output_path=str(tmp_path / "parsed_outputs.jsonl"),
    )

    reports = tmp_path / "reports"
    reports.mkdir()
    legacy_report = reports / "agent_system_live_agent_experiment_v1.json"
    legacy_report.write_text("historical-v1\n", encoding="utf-8")
    paths = write_live_agent_experiment_artifacts(
        output_dir=tmp_path,
        report_dir=reports,
        calls=calls,
        parsed_outputs=parsed,
        summary=summary,
    )

    raw_path, parsed_path, manifest_path, report_json, report_markdown = paths
    raw_text = raw_path.read_text(encoding="utf-8")
    parsed_text = parsed_path.read_text(encoding="utf-8")
    report_text = report_json.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert "real provider response 1" in raw_text
    assert "real provider response 1" not in parsed_text
    assert "real provider response 1" not in report_text
    assert manifest["raw_responses_sha256"]
    assert manifest["parsed_outputs_sha256"]
    assert raw_path.name == "raw_responses_v2.jsonl"
    assert parsed_path.name == "parsed_outputs_v2.jsonl"
    assert manifest_path.name == "experiment_manifest_v2.json"
    assert report_json.name == "agent_system_live_agent_experiment_v2.json"
    assert report_markdown.name == "agent_system_live_agent_experiment_v2.md"
    assert legacy_report.read_text(encoding="utf-8") == "historical-v1\n"
    assert report_markdown.is_file()


def test_summary_rejects_missing_raw_call_or_trial_execution() -> None:
    calls = (_call(1),)
    parsed = (
        LiveAgentExperimentParsedOutput(
            experiment_id="experiment-v1",
            cycle=1,
            trial_id="assembly-025",
            kind="assembly",
            source_id="2026-05-20:025",
            role="decision_case_assembly",
            workflow_status="insufficient",
            model_acceptance_status="failed",
            workflow_provider_call_count=2,
            provider_call_ids=(calls[0].call_id,),
        ),
    )

    summary = summarize_live_agent_experiment(
        suite_id="suite-v1",
        suite_checksum="d" * 64,
        minimum_successful_calls=100,
        minimum_cycles=2,
        maximum_cycles=20,
        completed_cycles=2,
        calls=calls,
        parsed_outputs=parsed,
        expected_trial_ids=("assembly-025",),
        runner_status="completed",
        raw_response_path="raw_responses.jsonl",
        parsed_output_path="parsed_outputs.jsonl",
    )

    assert summary.integrity_valid is False
    assert summary.call_binding_mismatch_count > 0
    assert summary.missing_trial_execution_count == 1
    assert summary.threshold_satisfied is False


def test_public_real_experiment_runner_has_no_model_substitute_injection() -> None:
    parameters = inspect.signature(run_live_agent_experiment).parameters

    assert "model_factory" not in parameters
    assert "case_runner" not in parameters
    assert "response_fixture" not in parameters
    assert "replay_path" not in parameters
