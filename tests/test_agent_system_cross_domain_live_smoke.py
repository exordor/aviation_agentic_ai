"""Contracts for the real-provider cross-domain HybridRAG smoke."""

from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryStatement,
    HybridQuerySupportRecord,
    ModelCallRecord,
    ModelToolCall,
    QueryRouteTrace,
    QueryToolOutcome,
    QueryToolTrace,
)
from aviation_agentic_ai.agent_system.live_cross_domain_smoke import (
    CrossDomainProviderCall,
    LiveCrossDomainSmokeAuthorizationError,
    build_sanitized_query_output,
    load_cross_domain_smoke_suite,
    run_live_cross_domain_smoke,
    score_cross_domain_trial,
)


def test_tracked_cross_domain_smoke_has_six_unscoped_natural_language_tasks():
    suite = load_cross_domain_smoke_suite(
        "data/evaluation/agent_system/live_hybridrag_cross_domain_v1.yaml"
    )

    assert suite.mode == "live_smoke"
    assert {trial.category for trial in suite.trials} == {
        "tmi",
        "flight",
        "weather",
        "sector",
        "cross_domain",
        "insufficient",
    }
    assert len(suite.trials) == 6
    assert all(trial.question.strip().endswith("?") for trial in suite.trials)
    assert all(trial.scope == {} for trial in suite.trials)
    assert all("source_id" not in trial.model_fields_set for trial in suite.trials)
    assert all("event_id" not in trial.model_fields_set for trial in suite.trials)


def test_live_cross_domain_smoke_requires_explicit_authorization(
    tmp_path: Path,
):
    with pytest.raises(LiveCrossDomainSmokeAuthorizationError):
        run_live_cross_domain_smoke(
            config_path="configs/aviation_knowledge_v1.yaml",
            suite_path=(
                "data/evaluation/agent_system/"
                "live_hybridrag_cross_domain_v1.yaml"
            ),
            store_dir=tmp_path / "store",
            output_dir=tmp_path / "runtime",
            report_dir=tmp_path / "reports",
            allow_live_model=False,
        )

    assert not (tmp_path / "runtime").exists()
    assert not (tmp_path / "reports").exists()


def test_cross_domain_scoring_separates_four_acceptance_axes():
    suite = load_cross_domain_smoke_suite(
        "data/evaluation/agent_system/live_hybridrag_cross_domain_v1.yaml"
    )
    trial = next(row for row in suite.trials if row.category == "flight")
    flight_id = "flight:10715de507eea28f"
    flight_support = HybridQuerySupportRecord(
        kind="flight_fact",
        root_ids=(flight_id,),
        publication_ids=("publication:aal1102",),
        flight_ids=(flight_id,),
    )
    trajectory_support = HybridQuerySupportRecord(
        kind="trajectory_fact",
        root_ids=(flight_id,),
        publication_ids=("publication:aal1102",),
        flight_ids=(flight_id,),
        route_ids=("route:aal1102",),
        track_point_ids=("track:aal1102:1",),
    )
    outcome = QueryToolOutcome(
        status="ok",
        answer="AAL1102 is an accepted flight record with a trajectory.",
        route_trace=QueryRouteTrace(
            status="selected",
            selected_families=("flight_airspace",),
            available_families=("source", "tmi", "flight_airspace"),
            selected_tool_names=("find_flights", "read_flight_trajectory"),
        ),
        tool_calls=[
            QueryToolTrace(
                tool_call_id="tool-call:1",
                tool="find_flights",
                status="ok",
            ),
            QueryToolTrace(
                tool_call_id="tool-call:2",
                tool="read_flight_trajectory",
                status="ok",
            ),
        ],
        answer_statements=[
            HybridQueryStatement(
                kind="flight_fact",
                text="AAL1102 is an accepted flight record.",
                support_root_ids=(flight_id,),
                support_publication_ids=("publication:aal1102",),
                support_flight_ids=(flight_id,),
            ),
            HybridQueryStatement(
                kind="trajectory_fact",
                text="AAL1102 has an accepted trajectory.",
                support_root_ids=(flight_id,),
                support_publication_ids=("publication:aal1102",),
                support_flight_ids=(flight_id,),
                support_route_ids=("route:aal1102",),
                support_track_point_ids=("track:aal1102:1",),
            ),
        ],
        support_records=[flight_support, trajectory_support],
    )

    result = score_cross_domain_trial(trial=trial, outcome=outcome)

    assert result.routing_passed is True
    assert result.retrieval_passed is True
    assert result.grounding_passed is True
    assert result.answer_acceptance_passed is True
    assert result.accepted is True


def test_sanitized_parsed_output_excludes_model_and_tool_payloads():
    outcome = QueryToolOutcome(
        status="blocked",
        answer="",
        model_calls=[
            ModelCallRecord(
                agent="query",
                raw_response="provider-private-response",
                tool_calls=(
                    ModelToolCall(
                        call_id="call:1",
                        name="find_flights",
                        arguments={"tail_number": "private-tool-argument"},
                    ),
                ),
            )
        ],
        tool_calls=[
            QueryToolTrace(
                tool_call_id="call:1",
                tool="find_flights",
                arguments={"tail_number": "private-tool-argument"},
                status="insufficient",
            )
        ],
        failure_reason="provider-private-failure",
    )

    serialized = str(build_sanitized_query_output(outcome))

    assert "provider-private-response" not in serialized
    assert "private-tool-argument" not in serialized
    assert "find_flights" in serialized
    assert "provider-private-failure" in serialized


def test_live_trial_acceptance_requires_router_and_query_provider_calls():
    suite = load_cross_domain_smoke_suite(
        "data/evaluation/agent_system/live_hybridrag_cross_domain_v1.yaml"
    )
    trial = next(row for row in suite.trials if row.category == "flight")
    outcome = QueryToolOutcome(
        status="ok",
        route_trace=QueryRouteTrace(
            status="selected",
            selected_families=("flight_airspace",),
            available_families=("source", "tmi", "flight_airspace"),
            selected_tool_names=("find_flights",),
        ),
        tool_calls=[
            QueryToolTrace(
                tool_call_id="tool-call:1",
                tool="find_flights",
                status="ok",
            )
        ],
        answer_statements=[
            HybridQueryStatement(
                kind="flight_fact",
                text="The requested flight record is accepted.",
                support_flight_ids=("flight:8f3822287af08a20",),
                support_publication_ids=("publication:aal100",),
            )
        ],
        support_records=[
            HybridQuerySupportRecord(
                kind="flight_fact",
                flight_ids=("flight:8f3822287af08a20",),
                publication_ids=("publication:aal100",),
            )
        ],
    )
    router_call = CrossDomainProviderCall(
        call_id="provider:router",
        trial_id=trial.trial_id,
        recorded_at="2026-08-01T00:00:00+00:00",
        phase="select_tool",
        role="query_router",
        provider="deepseek",
        model="deepseek-v4-pro",
        temperature=0.0,
        native_response={},
        response_sha256="a" * 64,
    )

    result = score_cross_domain_trial(
        trial=trial,
        outcome=outcome,
        provider_calls=(router_call,),
        require_live_calls=True,
    )

    assert result.live_calls_passed is False
    assert result.accepted is False
