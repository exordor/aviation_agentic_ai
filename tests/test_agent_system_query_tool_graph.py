"""End-to-end offline contracts for the bounded Query Agent tool loop."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from langchain_core.messages import AIMessage, ToolMessage

from aviation_agentic_ai.agent_system.contracts import (
    BTSOutcomeSummary,
    ModelCallRecord,
    ModelToolCall,
    PersistedProfileGap,
    SourceFamily,
    SourceSnapshot,
    WeatherContextAssociation,
)
from aviation_agentic_ai.agent_system.query_tool_graph import (
    DECLARED_REASON_QUESTION,
    FORECAST_CONTEXT_QUESTION,
    MEASURE_QUESTION,
    OBSERVED_WEATHER_CONTEXT_QUESTION,
    OPERATIONAL_PERIOD_QUESTION,
    PUBLIC_OUTCOME_QUESTION,
    PROVENANCE_QUESTION,
    RECONSTRUCTED_CASE_QUESTION,
    REGISTERED_COMPETENCY_QUESTION,
    answer_question_with_tools,
    question_requires_model,
)
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn

EVENT_ID = "urn:aviation-agentic-ai:event:tool-graph-test"
FACILITY_ID = "urn:aviation-agentic-ai:facility:airport:KJFK"
SOURCE_ID = "2026-05-19:123"
PREDICATES = [
    "rdf:type",
    "atm:controlledNASelement",
    "atm:effectiveStartTime",
    "atm:effectiveEndTime",
]


def _graph_rows() -> list[dict[str, Any]]:
    values = [
        ("fact:type", "rdf:type", "atm:GroundStopTMI", "iri", "atm:GroundStopTMI"),
        (
            "fact:facility",
            "atm:controlledNASelement",
            FACILITY_ID,
            "iri",
            "nas:Airport",
        ),
        (
            "fact:start",
            "atm:effectiveStartTime",
            "2026-05-19T21:00:00Z",
            "literal",
            "",
        ),
        (
            "fact:end",
            "atm:effectiveEndTime",
            "2026-05-19T22:45:00Z",
            "literal",
            "",
        ),
    ]
    return [
        {
            "triple_id": fact_id,
            "subject": EVENT_ID,
            "predicate": predicate,
            "object": object_value,
            "subject_class": "atm:GroundStopTMI",
            "object_class": object_class,
            "object_kind": object_kind,
            "source_document": SOURCE_ID,
            # The Query Agent must never receive or persist this raw span.
            "evidence_text": "RAW ADVISORY SPAN MUST REMAIN HIDDEN",
        }
        for fact_id, predicate, object_value, object_kind, object_class in values
    ]


def _write_graph(run_dir: Path, rows: list[dict[str, Any]] | None = None) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "kg.jsonl").write_text(
        "\n".join(json.dumps(row) for row in (rows or _graph_rows())) + "\n",
        encoding="utf-8",
    )


def _write_profile_gap(
    run_dir: Path,
    *,
    event_id: str = EVENT_ID,
    source_id: str = SOURCE_ID,
    profile_gap_id: str = "profile-gap:reason",
) -> None:
    evidence = "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
    content = f"{evidence}\n"
    import hashlib

    checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
    snapshot = SourceSnapshot(
        source_id=source_id,
        family="atcscc_advisory",
        content=content,
        content_sha256=checksum,
        snapshot_timestamp="2026-05-19T21:00:00+00:00",
    )
    (run_dir / "source_snapshot.json").write_text(
        snapshot.model_dump_json(),
        encoding="utf-8",
    )
    gap = PersistedProfileGap(
        profile_gap_id=profile_gap_id,
        event_id=event_id,
        field="impacting_condition",
        value="weather",
        evidence_text=evidence,
        reason="atm:impactingCondition domain is GDP-only in the active slice",
        source_id=source_id,
        source_snapshot_sha256=checksum,
    )
    (run_dir / "profile_gaps.jsonl").write_text(
        gap.model_dump_json() + "\n",
        encoding="utf-8",
    )


def _artifact(
    run_dir: Path,
    name: str,
    rows: list[str],
    *,
    status: str = "ok",
) -> dict[str, object]:
    data = "".join(row + "\n" for row in rows).encode("utf-8")
    (run_dir / name).write_bytes(data)
    return {
        "path": name,
        "count": len(rows),
        "sha256": hashlib.sha256(data).hexdigest(),
        "status": status,
    }


def _write_query_context(
    run_dir: Path,
    *,
    active_counts: tuple[int, int, int, int] = (20, 18, 2, 0),
) -> None:
    run_id = run_dir.name
    taf_source = "weather-source:taf:KJFK:test"
    metar_source = "weather-source:metar:KJFK:test"
    bts_source = "bts_on_time:2026-05:nyc"
    taf_content = json.dumps(
        {
            "icaoId": "KJFK",
            "issueTime": "2026-05-19T20:00:00Z",
            "rawTAF": "TAF KJFK TEST",
            "validTimeFrom": "2026-05-19T20:00:00Z",
            "validTimeTo": "2026-05-20T02:00:00Z",
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    metar_content = json.dumps(
        {
            "icaoId": "KJFK",
            "rawOb": "METAR KJFK TEST",
            "reportTime": "2026-05-19T20:15:00Z",
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    bts_content = "{}\n"
    snapshots = [
        SourceSnapshot(
            source_id=SOURCE_ID,
            family=SourceFamily.ATCSCC_ADVISORY,
            content="IMPACTING CONDITION: WEATHER / THUNDERSTORMS\n",
            content_sha256=hashlib.sha256(
                b"IMPACTING CONDITION: WEATHER / THUNDERSTORMS\n"
            ).hexdigest(),
            snapshot_timestamp="2026-05-19T20:30:00+00:00",
        ),
        SourceSnapshot(
            source_id=taf_source,
            family=SourceFamily.TAF,
            content=taf_content,
            content_sha256=hashlib.sha256(taf_content.encode()).hexdigest(),
            snapshot_timestamp="2026-05-19T20:00:00+00:00",
        ),
        SourceSnapshot(
            source_id=metar_source,
            family=SourceFamily.METAR,
            content=metar_content,
            content_sha256=hashlib.sha256(metar_content.encode()).hexdigest(),
            snapshot_timestamp="2026-05-19T20:15:00+00:00",
        ),
        SourceSnapshot(
            source_id=bts_source,
            family=SourceFamily.BTS_ON_TIME,
            content=bts_content,
            content_sha256=hashlib.sha256(bts_content.encode()).hexdigest(),
            snapshot_timestamp="2026-05-19T20:00:00+00:00",
        ),
    ]
    reports = [
        (
            "weather-report:taf:KJFK:test",
            taf_source,
            "latest_forecast_known_at_issue",
            "TAF KJFK TEST",
            "data:tafReportString",
        ),
        (
            "weather-report:metar:KJFK:test",
            metar_source,
            "latest_observation_at_or_before_issue",
            "METAR KJFK TEST",
            "data:metarReportString",
        ),
    ]
    associations = []
    rows = _graph_rows()
    for index, (report_id, source_id, relation, raw, raw_predicate) in enumerate(
        reports
    ):
        associations.append(
            WeatherContextAssociation(
                association_id=f"weather-association:{index}",
                run_id=run_id,
                event_id=EVENT_ID,
                report_id=report_id,
                facility_id=FACILITY_ID,
                relation_type=relation,
                selection_method="deterministic test selection",
                relevant_times={
                    "advisory_issued_at": "2026-05-19T20:30:00+00:00",
                    "operational_start": "2026-05-19T21:00:00+00:00",
                    "operational_end": "2026-05-19T22:45:00+00:00",
                },
                source_id=source_id,
                source_snapshot_sha256=next(
                    snapshot.content_sha256
                    for snapshot in snapshots
                    if snapshot.source_id == source_id
                ),
                causal_claim=False,
            )
        )
        subject = f"urn:aviation-agentic-ai:{report_id}"
        rows.extend(
            [
                {
                    "triple_id": f"weather:{index}:type",
                    "subject": subject,
                    "predicate": "rdf:type",
                    "object": (
                        "https://data.nasa.gov/ontologies/atmonto/"
                        "data#MeteorologicalReport"
                    ),
                    "subject_class": "data:MeteorologicalReport",
                    "object_class": "data:MeteorologicalReport",
                    "object_kind": "iri",
                    "source_document": source_id,
                },
                {
                    "triple_id": f"weather:{index}:facility",
                    "subject": subject,
                    "predicate": "data:forecastingAirport",
                    "object": FACILITY_ID,
                    "subject_class": "data:MeteorologicalReport",
                    "object_class": "nas:Airport",
                    "object_kind": "iri",
                    "source_document": source_id,
                },
                {
                    "triple_id": f"weather:{index}:raw",
                    "subject": subject,
                    "predicate": raw_predicate,
                    "object": raw,
                    "subject_class": "data:MeteorologicalReport",
                    "object_class": "",
                    "object_kind": "literal",
                    "source_document": source_id,
                },
            ]
        )
    _write_graph(run_dir, rows)

    start = datetime(2026, 5, 19, 21, tzinfo=UTC)
    end = datetime(2026, 5, 19, 22, 45, tzinfo=UTC)
    windows = {
        "baseline": (start - timedelta(hours=2), start),
        "active": (start, end),
        "recovery": (end, end + timedelta(hours=6)),
    }
    summaries = []
    for phase, (window_start, window_end) in windows.items():
        scheduled, completed, cancelled, diverted = (
            active_counts if phase == "active" else (10, 9, 1, 0)
        )
        summaries.append(
            BTSOutcomeSummary(
                summary_id=f"bts-outcome:{phase}",
                run_id=run_id,
                event_id=EVENT_ID,
                facility_id=FACILITY_ID,
                phase=phase,
                window_start=window_start,
                window_end=window_end,
                source_id=bts_source,
                source_snapshot_sha256=snapshots[-1].content_sha256,
                scheduled_arrival_count_proxy=scheduled,
                completed_arrival_count=completed,
                cancelled_count=cancelled,
                diverted_count=diverted,
                arrival_delay_15_count=1,
                mean_arrival_delay_minutes=None,
                median_arrival_delay_minutes=None,
                carrier_reported_weather_delay_minutes=None,
                carrier_reported_nas_delay_minutes=5.0,
                scheduled_arrival_semantics="public scheduled-demand proxy",
                weather_delay_semantics="carrier-reported attribution",
                nas_delay_semantics="carrier-reported attribution",
                causal_claim=False,
            )
        )
    metadata = {
        "source_snapshots": _artifact(
            run_dir,
            "source_snapshots.jsonl",
            [snapshot.model_dump_json() for snapshot in snapshots],
        ),
        "context_associations": _artifact(
            run_dir,
            "context_associations.jsonl",
            [association.model_dump_json() for association in associations],
        ),
        "outcome_summaries": _artifact(
            run_dir,
            "outcome_summaries.jsonl",
            [summary.model_dump_json() for summary in summaries],
        ),
    }
    (run_dir / "run_manifest.json").write_text(
        json.dumps({"run_id": run_id, "context_artifacts": metadata}),
        encoding="utf-8",
    )


def _tool_message(
    *,
    name: str = "get_event_facts",
    call_id: str = "call:1",
    args: dict[str, Any] | None = None,
) -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[
            {
                "id": call_id,
                "name": name,
                "args": args
                or {
                    "event_id": EVENT_ID,
                    "predicates": PREDICATES,
                },
                "type": "tool_call",
            }
        ],
    )


def _final_message(
    *,
    sources: list[str] | None = None,
    answer: str = (
        "MEASURE: Ground Stop (GS)\n"
        "AIRPORT: KJFK\n"
        "START: 2026-05-19T21:00:00Z\n"
        "END: 2026-05-19T22:45:00Z"
    ),
) -> AIMessage:
    source_lines = "\n".join(
        f"- {source}" for source in (sources if sources is not None else [SOURCE_ID])
    )
    return AIMessage(
        content=f"ANSWER\n{answer}\nSOURCES\n{source_lines}",
    )


class _ScriptedModel:
    def __init__(self, turns: list[AIMessage | Exception]) -> None:
        self.turns = list(turns)
        self.invocations: list[tuple[str, list[Any]]] = []

    def invoke(self, messages, *, phase):
        self.invocations.append((phase, list(messages)))
        attempt = len(self.invocations)
        item = self.turns.pop(0)
        if isinstance(item, Exception):
            return ToolModelTurn(
                message=None,
                record=ModelCallRecord(
                    agent="query",
                    raw_response="",
                    prompt_set_id="prompt:test",
                    prompt_version="query-agent-v4",
                    provider="deepseek",
                    model="deepseek-test",
                    temperature=0,
                    attempt=attempt,
                    error=f"{type(item).__name__}: {item}",
                ),
            )
        return ToolModelTurn(
            message=item,
            record=ModelCallRecord(
                agent="query",
                raw_response=str(item.content or "") if not item.tool_calls else "",
                prompt_set_id="prompt:test",
                prompt_version="query-agent-v4",
                provider="deepseek",
                model="deepseek-test",
                temperature=0,
                attempt=attempt,
                tool_calls=[
                    ModelToolCall(
                        call_id=str(call["id"]),
                        name=str(call["name"]),
                        arguments=dict(call["args"]),
                    )
                    for call in item.tool_calls
                ],
            ),
        )


class _Factory:
    def __init__(self, model: _ScriptedModel) -> None:
        self.model = model
        self.calls = 0
        self.tool_names: list[str] = []

    def __call__(self, tools):
        self.calls += 1
        self.tool_names = [tool.name for tool in tools]
        return self.model


def test_only_preexisting_combined_question_requires_a_model():
    assert question_requires_model(REGISTERED_COMPETENCY_QUESTION) is True
    assert all(
        question_requires_model(question) is False
        for question in (
            FORECAST_CONTEXT_QUESTION,
            OBSERVED_WEATHER_CONTEXT_QUESTION,
            PUBLIC_OUTCOME_QUESTION,
            RECONSTRUCTED_CASE_QUESTION,
        )
    )


def test_supported_question_runs_model_tool_model_and_cites_source(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel([_tool_message(), _final_message()])
    factory = _Factory(model)
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=factory,
    )
    assert outcome.status == "ok"
    assert outcome.answer == (
        "The graph records a Ground Stop controlling KJFK from "
        "2026-05-19T21:00:00Z to 2026-05-19T22:45:00Z."
    )
    assert outcome.source_ids == [SOURCE_ID]
    assert set(outcome.retrieved_fact_ids) == {
        "fact:type",
        "fact:facility",
        "fact:start",
        "fact:end",
    }
    assert len(outcome.model_calls) == 2
    assert len(outcome.tool_calls) == 1
    assert outcome.tool_calls[0].tool == "get_event_facts"
    assert outcome.tool_calls[0].tool_call_id == "call:1"
    assert set(factory.tool_names) == {
        "find_events",
        "get_event_facts",
        "get_neighbors",
        "get_profile_gaps",
        "get_provenance",
    }
    assert [phase for phase, _messages in model.invocations] == [
        "select_tool",
        "final_answer",
    ]


def test_forecast_context_is_deterministic_non_causal_and_query_run_is_separate(
    tmp_path,
):
    _write_graph(tmp_path)
    _write_query_context(tmp_path)
    factory = _Factory(_ScriptedModel([]))

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=FORECAST_CONTEXT_QUESTION,
        model_factory=factory,
    )

    assert outcome.status == "ok"
    assert "non-causal context" in outcome.answer
    assert "TAF KJFK TEST" in outcome.answer
    assert outcome.model_calls == []
    assert factory.calls == 0
    assert [trace.tool for trace in outcome.tool_calls] == [
        "get_decision_context"
    ]
    assert outcome.retrieved_context_association_ids == [
        "weather-association:0"
    ]
    record = json.loads((tmp_path / "query_run.json").read_text(encoding="utf-8"))
    assert record["retrieved_context_association_ids"] == [
        "weather-association:0"
    ]
    assert record["retrieved_outcome_summary_ids"] == []
    assert record["retrieved_facts"]
    assert record["retrieved_context_associations"]
    assert record["retrieved_outcome_summaries"] == []


def test_observed_context_uses_only_metar_associations_without_model(tmp_path):
    _write_graph(tmp_path)
    _write_query_context(tmp_path)
    factory = _Factory(_ScriptedModel([]))

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=OBSERVED_WEATHER_CONTEXT_QUESTION,
        model_factory=factory,
    )

    assert outcome.status == "ok"
    assert "non-causal context" in outcome.answer
    assert "METAR KJFK TEST" in outcome.answer
    assert "TAF KJFK TEST" not in outcome.answer
    assert outcome.retrieved_context_association_ids == [
        "weather-association:1"
    ]
    assert len(outcome.tool_calls) == 1
    assert factory.calls == 0


@pytest.mark.parametrize(
    "active_counts",
    [
        (20, 18, 2, 0),
        (77, 68, 4, 5),
        (50, 49, 1, 0),
    ],
)
def test_public_outcome_response_preserves_three_case_active_counts(
    tmp_path,
    active_counts,
):
    _write_graph(tmp_path)
    _write_query_context(tmp_path, active_counts=active_counts)
    factory = _Factory(_ScriptedModel([]))

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=PUBLIC_OUTCOME_QUESTION,
        model_factory=factory,
    )

    scheduled, completed, cancelled, diverted = active_counts
    assert outcome.status == "ok"
    assert "public scheduled-demand proxy, not FAA arrival demand" in outcome.answer
    assert "carrier-reported attribution" in outcome.answer
    assert (
        f"active: scheduled {scheduled}, completed {completed}, "
        f"cancelled {cancelled}, diverted {diverted}"
    ) in outcome.answer
    assert outcome.retrieved_fact_ids == []
    assert outcome.retrieved_outcome_summary_ids == [
        "bts-outcome:baseline",
        "bts-outcome:active",
        "bts-outcome:recovery",
    ]
    assert outcome.model_calls == []
    assert factory.calls == 0


def test_reconstructed_case_uses_three_tools_without_retrieving_reason(tmp_path):
    rows = _graph_rows()
    rows.append(
        {
            "triple_id": "fact:reason",
            "subject": EVENT_ID,
            "predicate": "atm:impactingCondition",
            "object": "weather",
            "subject_class": "atm:GroundDelayProgramTMI",
            "object_class": "",
            "object_kind": "literal",
            "source_document": SOURCE_ID,
            "evidence_text": "IMPACTING CONDITION: WEATHER",
        }
    )
    _write_graph(tmp_path, rows)
    _write_query_context(tmp_path)
    factory = _Factory(_ScriptedModel([]))

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=RECONSTRUCTED_CASE_QUESTION,
        model_factory=factory,
    )

    assert outcome.status == "ok"
    assert len(outcome.tool_calls) == 3
    assert [trace.tool for trace in outcome.tool_calls] == [
        "get_event_facts",
        "get_decision_context",
        "get_outcome_summary",
    ]
    assert "fact:reason" not in outcome.retrieved_fact_ids
    assert "impacting condition" not in outcome.answer.lower()
    assert "non-causal context" in outcome.answer
    assert "public scheduled-demand proxy, not FAA arrival demand" in outcome.answer
    assert outcome.model_calls == []
    assert factory.calls == 0


def test_absent_context_is_insufficient_before_model_construction(tmp_path):
    _write_graph(tmp_path)
    factory = _Factory(_ScriptedModel([]))

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=FORECAST_CONTEXT_QUESTION,
        model_factory=factory,
    )

    assert outcome.status == "insufficient"
    assert outcome.model_calls == []
    assert [trace.tool for trace in outcome.tool_calls] == [
        "get_decision_context"
    ]
    assert factory.calls == 0


def test_optional_context_corruption_does_not_block_old_core_question(tmp_path):
    _write_graph(tmp_path)
    (tmp_path / "context_associations.jsonl").write_text(
        "not-json\n",
        encoding="utf-8",
    )
    factory = _Factory(_ScriptedModel([]))

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=MEASURE_QUESTION,
        model_factory=factory,
    )

    assert outcome.status == "ok"
    assert "Ground Stop" in outcome.answer
    assert outcome.model_calls == []
    assert factory.calls == 0


def test_reconstructed_case_persists_partial_context_when_outcomes_are_absent(
    tmp_path,
):
    _write_graph(tmp_path)
    _write_query_context(tmp_path)
    manifest_path = tmp_path / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["context_artifacts"]["outcome_summaries"] = _artifact(
        tmp_path,
        "outcome_summaries.jsonl",
        [],
        status="insufficient",
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=RECONSTRUCTED_CASE_QUESTION,
        model_factory=_Factory(_ScriptedModel([])),
    )

    assert outcome.status == "insufficient"
    record = json.loads((tmp_path / "query_run.json").read_text(encoding="utf-8"))
    assert record["retrieved_context_association_ids"]
    assert {
        item["association_id"]
        for item in record["retrieved_context_associations"]
    } == set(record["retrieved_context_association_ids"])
    assert {
        item["fact_id"] for item in record["retrieved_facts"]
    } == set(record["retrieved_fact_ids"])
    assert record["retrieved_outcome_summary_ids"] == []
    assert record["retrieved_outcome_summaries"] == []


def test_weather_context_never_changes_the_three_reason_states(tmp_path):
    ground_stop = tmp_path / "ground-stop"
    _write_graph(ground_stop)
    _write_query_context(ground_stop)
    _write_profile_gap(ground_stop)
    ground_stop_factory = _Factory(_ScriptedModel([]))
    ground_stop_outcome = answer_question_with_tools(
        run_dir=ground_stop,
        question=DECLARED_REASON_QUESTION,
        model_factory=ground_stop_factory,
    )
    assert ground_stop_outcome.status == "ok"
    assert ground_stop_outcome.retrieved_profile_gap_ids == [
        "profile-gap:reason"
    ]
    assert ground_stop_outcome.retrieved_fact_ids == []

    gdp = tmp_path / "gdp"
    _write_graph(gdp)
    _write_query_context(gdp)
    gdp_rows = [
        json.loads(line)
        for line in (gdp / "kg.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    gdp_rows.append(
        {
            "triple_id": "fact:reason",
            "subject": EVENT_ID,
            "predicate": "atm:impactingCondition",
            "object": "weather",
            "subject_class": "atm:GroundDelayProgramTMI",
            "object_class": "",
            "object_kind": "literal",
            "source_document": SOURCE_ID,
            "evidence_text": "IMPACTING CONDITION: WEATHER / THUNDERSTORMS",
        }
    )
    _write_graph(gdp, gdp_rows)
    gdp_factory = _Factory(_ScriptedModel([]))
    gdp_outcome = answer_question_with_tools(
        run_dir=gdp,
        question=DECLARED_REASON_QUESTION,
        model_factory=gdp_factory,
    )
    assert gdp_outcome.status == "ok"
    assert gdp_outcome.retrieved_fact_ids == ["fact:reason"]
    assert "records weather" in gdp_outcome.answer

    cancellation = tmp_path / "cancellation"
    _write_graph(cancellation)
    _write_query_context(cancellation)
    cancellation_factory = _Factory(_ScriptedModel([]))
    cancellation_outcome = answer_question_with_tools(
        run_dir=cancellation,
        question=DECLARED_REASON_QUESTION,
        model_factory=cancellation_factory,
    )
    assert cancellation_outcome.status == "insufficient"
    assert cancellation_outcome.retrieved_fact_ids == []

    assert ground_stop_factory.calls == 0
    assert gdp_factory.calls == 0
    assert cancellation_factory.calls == 0


def test_ground_stop_reason_uses_profile_gap_without_model_call(tmp_path):
    _write_graph(tmp_path)
    _write_profile_gap(tmp_path)
    factory = _Factory(_ScriptedModel([]))

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=DECLARED_REASON_QUESTION,
        model_factory=factory,
    )

    assert outcome.status == "ok"
    assert "IMPACTING CONDITION: WEATHER / THUNDERSTORMS" in outcome.answer
    assert "outside the active formal profile" in outcome.answer
    assert outcome.retrieved_fact_ids == []
    assert outcome.retrieved_profile_gap_ids == ["profile-gap:reason"]
    assert outcome.source_ids == [SOURCE_ID]
    assert outcome.model_calls == []
    assert factory.calls == 0
    assert [trace.tool for trace in outcome.tool_calls] == [
        "get_event_facts",
        "get_profile_gaps",
    ]


def test_gdp_reason_uses_formal_fact_and_exact_source_wording(tmp_path):
    rows = _graph_rows()
    rows.append(
        {
            "triple_id": "fact:reason",
            "subject": EVENT_ID,
            "predicate": "atm:impactingCondition",
            "object": "weather",
            "subject_class": "atm:GroundDelayProgramTMI",
            "object_class": "",
            "object_kind": "literal",
            "source_document": "2026-05-19:138",
            "evidence_text": (
                "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
            ),
        }
    )
    for row in rows:
        row["source_document"] = "2026-05-19:138"
    _write_graph(tmp_path, rows)
    factory = _Factory(_ScriptedModel([]))

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=DECLARED_REASON_QUESTION,
        model_factory=factory,
    )

    assert outcome.status == "ok"
    assert "records weather as its impacting condition" in outcome.answer
    assert (
        "IMPACTING CONDITION: WEATHER / THUNDERSTORMS" in outcome.answer
    )
    assert outcome.retrieved_fact_ids == ["fact:reason"]
    assert outcome.retrieved_profile_gap_ids == []
    assert outcome.source_ids == ["2026-05-19:138"]
    assert outcome.model_calls == []
    assert factory.calls == 0


def test_missing_reason_is_insufficient_before_model_construction(tmp_path):
    rows = _graph_rows()
    for row in rows:
        row["source_document"] = "2026-05-20:020"
    _write_graph(tmp_path, rows)
    factory = _Factory(_ScriptedModel([]))

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=DECLARED_REASON_QUESTION,
        model_factory=factory,
    )

    assert outcome.status == "insufficient"
    assert outcome.answer == "Insufficient graph evidence."
    assert outcome.model_calls == []
    assert factory.calls == 0


def test_operational_period_question_uses_only_time_predicates(tmp_path):
    _write_graph(tmp_path)
    factory = _Factory(_ScriptedModel([]))

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=OPERATIONAL_PERIOD_QUESTION,
        model_factory=factory,
    )

    assert outcome.status == "ok"
    assert (
        "2026-05-19T21:00:00Z to 2026-05-19T22:45:00Z"
        in outcome.answer
    )
    assert set(outcome.retrieved_fact_ids) == {"fact:start", "fact:end"}
    assert outcome.model_calls == []
    assert factory.calls == 0


def test_provenance_question_requires_advisory_number(tmp_path):
    rows = _graph_rows()
    rows.append(
        {
            "triple_id": "fact:advisory",
            "subject": EVENT_ID,
            "predicate": "atm:advisoryNumber",
            "object": "123",
            "subject_class": "atm:GroundStopTMI",
            "object_class": "",
            "object_kind": "literal",
            "source_document": SOURCE_ID,
            "evidence_text": "ADVZY 123",
        }
    )
    _write_graph(tmp_path, rows)

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=PROVENANCE_QUESTION,
        model_factory=_Factory(_ScriptedModel([])),
    )

    assert outcome.status == "ok"
    assert outcome.answer == f"Source {SOURCE_ID} supports advisory 123."
    assert outcome.retrieved_fact_ids == ["fact:advisory"]


def test_malformed_or_duplicate_profile_gap_artifact_blocks_before_model(tmp_path):
    _write_graph(tmp_path)
    _write_profile_gap(tmp_path)
    path = tmp_path / "profile_gaps.jsonl"
    path.write_text(
        path.read_text(encoding="utf-8") * 2,
        encoding="utf-8",
    )
    factory = _Factory(_ScriptedModel([]))

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=DECLARED_REASON_QUESTION,
        model_factory=factory,
    )

    assert outcome.status == "blocked"
    assert "duplicate profile-gap ID" in outcome.failure_reason
    assert factory.calls == 0


def test_profile_gap_cannot_reference_another_event(tmp_path):
    _write_graph(tmp_path)
    _write_profile_gap(
        tmp_path,
        event_id="urn:aviation-agentic-ai:event:other",
    )
    factory = _Factory(_ScriptedModel([]))

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=DECLARED_REASON_QUESTION,
        model_factory=factory,
    )

    assert outcome.status == "blocked"
    assert "unregistered event" in outcome.failure_reason
    assert factory.calls == 0


def test_second_model_turn_contains_matching_tool_message(tmp_path):
    _write_graph(tmp_path)
    first = _tool_message(call_id="call:matching")
    model = _ScriptedModel([first, _final_message()])
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "ok"
    second_messages = model.invocations[1][1]
    assert first in second_messages
    observations = [
        message for message in second_messages if isinstance(message, ToolMessage)
    ]
    assert len(observations) == 1
    assert observations[0].tool_call_id == "call:matching"
    payload = json.loads(str(observations[0].content))
    assert set(payload["fact_ids"]) == set(outcome.retrieved_fact_ids)
    assert payload["source_ids"] == [SOURCE_ID]


def test_unsupported_question_constructs_neither_model_nor_tools(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel([])
    factory = _Factory(model)
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question="What is the runway surface at LAX?",
        model_factory=factory,
    )
    assert outcome.status == "insufficient"
    assert outcome.answer == "Insufficient graph evidence."
    assert outcome.model_calls == []
    assert outcome.tool_calls == []
    assert factory.calls == 0
    record = json.loads((tmp_path / "query_run.json").read_text(encoding="utf-8"))
    assert record["model_calls"] == []
    assert record["tool_calls"] == []


def test_first_model_answer_without_tool_call_is_blocked(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel([_final_message()])
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert "before retrieving graph evidence" in outcome.failure_reason
    assert len(outcome.model_calls) == 1
    assert outcome.tool_calls == []


def test_unknown_tool_is_blocked(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel([_tool_message(name="write_graph")])
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert outcome.failure_reason == "unknown Query Agent tool: write_graph"


def test_invalid_tool_arguments_are_blocked(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel(
        [
            _tool_message(
                args={
                    "event_id": EVENT_ID,
                    "predicates": ["atm:runwaySurface"],
                }
            )
        ]
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert "registered competency contract" in outcome.failure_reason
    assert outcome.tool_calls == []


def test_missing_required_graph_fact_is_insufficient_without_second_model(tmp_path):
    rows = [
        row
        for row in _graph_rows()
        if row["predicate"] != "atm:effectiveEndTime"
    ]
    _write_graph(tmp_path, rows)
    model = _ScriptedModel([_tool_message()])
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "insufficient"
    assert "effectiveEndTime" in outcome.failure_reason
    assert len(outcome.model_calls) == 1
    assert len(model.invocations) == 1


def test_unsourced_fact_is_blocked(tmp_path):
    rows = _graph_rows()
    rows[1]["source_document"] = ""
    _write_graph(tmp_path, rows)
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(_ScriptedModel([_tool_message()])),
    )
    assert outcome.status == "blocked"
    assert "missing provenance" in outcome.failure_reason


def test_second_model_tool_call_is_blocked_by_one_turn_contract(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel([_tool_message(), _tool_message(call_id="call:2")])
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert "one-turn tool budget" in outcome.failure_reason
    assert len(outcome.model_calls) == 2


def test_missing_or_duplicate_tool_call_id_is_blocked(tmp_path):
    _write_graph(tmp_path)
    duplicate = AIMessage(
        content="",
        tool_calls=[
            {
                "id": "call:1",
                "name": "get_event_facts",
                "args": {"event_id": EVENT_ID, "predicates": PREDICATES},
                "type": "tool_call",
            },
            {
                "id": "call:1",
                "name": "find_events",
                "args": {},
                "type": "tool_call",
            },
        ],
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(_ScriptedModel([duplicate])),
    )
    assert outcome.status == "blocked"
    assert "duplicate native tool-call ID" in outcome.failure_reason


def test_more_than_three_parallel_tool_calls_exceeds_budget(tmp_path):
    _write_graph(tmp_path)
    calls = [
        {
            "id": f"call:{index}",
            "name": "find_events",
            "args": {},
            "type": "tool_call",
        }
        for index in range(4)
    ]
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(
            _ScriptedModel([AIMessage(content="", tool_calls=calls)])
        ),
    )
    assert outcome.status == "blocked"
    assert "tool-call budget exceeded" in outcome.failure_reason


def test_provider_error_is_blocked_and_counts_attempt(tmp_path):
    _write_graph(tmp_path)
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(
            _ScriptedModel([TimeoutError("upstream timeout")])
        ),
    )
    assert outcome.status == "blocked"
    assert "TimeoutError" in outcome.failure_reason
    assert len(outcome.model_calls) == 1


def test_final_answer_without_retrieved_source_is_blocked(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel(
        [_tool_message(), _final_message(sources=["forged:source"])]
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert "outside retrieved evidence" in outcome.failure_reason
    assert outcome.source_ids == []


def test_valid_and_forged_citations_are_blocked(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel(
        [
            _tool_message(),
            _final_message(sources=[SOURCE_ID, "forged:source"]),
        ]
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert "outside retrieved evidence" in outcome.failure_reason


def test_citations_must_cover_every_retrieved_fact(tmp_path):
    rows = _graph_rows()
    for index, row in enumerate(rows):
        row["source_document"] = f"source:{index}"
    _write_graph(tmp_path, rows)
    model = _ScriptedModel(
        [_tool_message(), _final_message(sources=["source:0"])]
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert "do not cover retrieved facts" in outcome.failure_reason


def test_final_answer_must_include_required_graph_values(tmp_path):
    _write_graph(tmp_path)
    model = _ScriptedModel(
        [
            _tool_message(),
            _final_message(
                answer="A runway closure was caused by storms.",
            ),
        ]
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(model),
    )
    assert outcome.status == "blocked"
    assert "claim fields do not match" in outcome.failure_reason


def test_contradictory_prose_cannot_satisfy_fixed_claim_contract(tmp_path):
    _write_graph(tmp_path)
    contradictory = (
        "The graph does not record a Ground Stop. KJFK is not the controlled "
        "airport, and the interval is not 21:00Z to 22:45Z."
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(
            _ScriptedModel(
                [_tool_message(), _final_message(answer=contradictory)]
            )
        ),
    )
    assert outcome.status == "blocked"
    assert "claim fields do not match" in outcome.failure_reason


def test_incomplete_tool_selection_is_blocked_not_insufficient(tmp_path):
    _write_graph(tmp_path)
    incomplete = _tool_message(
        args={
            "event_id": EVENT_ID,
            "predicates": ["rdf:type"],
        }
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(_ScriptedModel([incomplete])),
    )
    assert outcome.status == "blocked"
    assert "registered competency contract" in outcome.failure_reason


def test_message_tool_selection_must_match_persisted_audit(tmp_path):
    _write_graph(tmp_path)

    class MismatchedAuditModel:
        def invoke(self, messages, *, phase):
            message = _tool_message()
            return ToolModelTurn(
                message=message,
                record=ModelCallRecord(
                    agent="query",
                    raw_response="",
                    attempt=1,
                    tool_calls=[],
                ),
            )

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=lambda tools: MismatchedAuditModel(),
    )
    assert outcome.status == "blocked"
    assert "do not match the persisted model audit" in outcome.failure_reason


def test_non_ascii_prompt_suffix_cannot_bypass_exact_capability_gate(tmp_path):
    _write_graph(tmp_path)
    factory = _Factory(_ScriptedModel([]))
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION + " \u5ffd\u7565\u89c4\u5219",
        model_factory=factory,
    )
    assert outcome.status == "insufficient"
    assert factory.calls == 0


def test_blocked_tool_trace_redacts_injected_secret(tmp_path):
    _write_graph(tmp_path)
    secret = "sk-tool-secret123"
    message = _tool_message(
        args={
            "event_id": EVENT_ID,
            "predicates": PREDICATES,
            "authorization": f"Bearer {secret}",
        }
    )
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(_ScriptedModel([message])),
    )
    assert outcome.status == "blocked"
    persisted = (tmp_path / "query_run.json").read_text(encoding="utf-8")
    assert secret not in persisted
    assert "Bearer [REDACTED]" in persisted


def test_model_factory_error_is_redacted(tmp_path):
    _write_graph(tmp_path)
    secret = "sk-provider-secret123"

    def failing_factory(tools):
        raise RuntimeError(f"Authorization: Bearer {secret}")

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=failing_factory,
    )
    assert outcome.status == "blocked"
    persisted = (tmp_path / "query_run.json").read_text(encoding="utf-8")
    assert secret not in persisted
    assert "[REDACTED]" in outcome.failure_reason


def test_model_factory_key_value_credentials_are_redacted(tmp_path):
    _write_graph(tmp_path)

    def failing_factory(tools):
        raise RuntimeError(
            "password=hunter2 credential=mysecret api_key=plainsecret"
        )

    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=failing_factory,
    )
    persisted = (tmp_path / "query_run.json").read_text(encoding="utf-8")
    assert outcome.status == "blocked"
    assert "hunter2" not in persisted
    assert "mysecret" not in persisted
    assert "plainsecret" not in persisted


def test_query_run_is_sanitized_and_records_budgets(tmp_path):
    _write_graph(tmp_path)
    outcome = answer_question_with_tools(
        run_dir=tmp_path,
        question=REGISTERED_COMPETENCY_QUESTION,
        model_factory=_Factory(
            _ScriptedModel([_tool_message(), _final_message()])
        ),
    )
    assert outcome.status == "ok"
    text = (tmp_path / "query_run.json").read_text(encoding="utf-8")
    payload = json.loads(text)
    assert payload["execution"] == "native_tool_loop"
    assert payload["budgets"] == {
        "maximum_model_calls": 2,
        "maximum_tool_calls": 3,
        "maximum_calls_per_tool": 1,
    }
    assert len(payload["model_calls"]) == 2
    assert len(payload["tool_calls"]) == 1
    assert "RAW ADVISORY SPAN MUST REMAIN HIDDEN" not in text
    assert "api_key" not in text.lower()
    assert "password" not in text.lower()
    assert "chain-of-thought" not in text.lower()
