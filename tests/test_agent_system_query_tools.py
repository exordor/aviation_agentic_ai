"""Focused contracts for the Query Agent's read-only graph tools."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from aviation_agentic_ai.agent_system.contracts import (
    BTSOutcomeSummary,
    SourceFamily,
    SourceSnapshot,
    WeatherContextAssociation,
)
from aviation_agentic_ai.agent_system.query_context_store import QueryContextStore
from aviation_agentic_ai.agent_system.query_tools import (
    QueryGraphStore,
    QueryPredicate,
    QueryToolError,
    QueryToolGateway,
    build_context_query_tools,
    build_query_tools,
    tool_registry,
)
from aviation_agentic_ai.agent_system.weather_context import (
    FORECASTING_AIRPORT,
    FORECAST_ISSUE_TIME,
    INTERVAL_END,
    INTERVAL_START,
    RDF_TYPE,
    TAF_STRING,
    XSD_DATETIME,
    XSD_STRING,
)
from aviation_agentic_ai.agent_system.weather_context_validation import (
    expected_weather_fact_id,
)

EVENT_ID = "urn:aviation-agentic-ai:event:tool-test"
FACILITY_ID = "urn:aviation-agentic-ai:facility:airport:KJFK"
SOURCE_ID = "2026-05-19:123"


def _rows() -> list[dict]:
    return [
        {
            "triple_id": "fact:type",
            "subject": EVENT_ID,
            "predicate": "rdf:type",
            "object": "atm:GroundStopTMI",
            "subject_class": "atm:GroundStopTMI",
            "object_class": "atm:GroundStopTMI",
            "object_kind": "iri",
            "source_document": SOURCE_ID,
        },
        {
            "triple_id": "fact:facility",
            "subject": EVENT_ID,
            "predicate": "atm:controlledNASelement",
            "object": FACILITY_ID,
            "subject_class": "atm:GroundStopTMI",
            "object_class": "nas:Airport",
            "object_kind": "iri",
            "source_document": SOURCE_ID,
        },
        {
            "triple_id": "fact:start",
            "subject": EVENT_ID,
            "predicate": "atm:effectiveStartTime",
            "object": "2026-05-19T21:00:00Z",
            "subject_class": "atm:GroundStopTMI",
            "object_class": "",
            "object_kind": "literal",
            "source_document": SOURCE_ID,
        },
        {
            "triple_id": "fact:end",
            "subject": EVENT_ID,
            "predicate": "atm:effectiveEndTime",
            "object": "2026-05-19T22:45:00Z",
            "subject_class": "atm:GroundStopTMI",
            "object_class": "",
            "object_kind": "literal",
            "source_document": SOURCE_ID,
        },
    ]


def _write_graph(run_dir: Path, rows: list[dict] | None = None) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    payload = rows if rows is not None else _rows()
    (run_dir / "kg.jsonl").write_text(
        "\n".join(json.dumps(row) for row in payload) + "\n",
        encoding="utf-8",
    )


def _gateway(
    run_dir: Path,
    *,
    with_context: bool = False,
) -> QueryToolGateway:
    store = QueryGraphStore(run_dir)
    return QueryToolGateway(
        store,
        allowed_predicates={predicate.value for predicate in QueryPredicate},
        context_store=QueryContextStore(run_dir, graph_store=store)
        if with_context
        else None,
    )


def _write_artifact(
    run_dir: Path,
    name: str,
    rows: list[str],
    *,
    status: str = "ok",
) -> dict[str, object]:
    path = run_dir / name
    data = "".join(row + "\n" for row in rows).encode("utf-8")
    path.write_bytes(data)
    return {
        "path": name,
        "count": len(rows),
        "sha256": hashlib.sha256(data).hexdigest(),
        "status": status,
    }


def _weather_fact_row(
    *,
    report_id: str,
    predicate: str,
    predicate_iri: str,
    value: str,
    source_id: str,
    object_kind: str,
    object_class: str = "",
    datatype_iri: str = "",
) -> dict[str, object]:
    return {
        "triple_id": expected_weather_fact_id(
            report_id,
            predicate_iri,
            value,
        ),
        "subject": f"urn:aviation-agentic-ai:{report_id}",
        "predicate": predicate,
        "object": value,
        "subject_class": "data:MeteorologicalReport",
        "object_class": object_class,
        "object_kind": object_kind,
        "source_document": source_id,
        "evidence_text": "TAF KJFK TEST",
        "datatype_iri": datatype_iri,
    }


def _write_context_layer(run_dir: Path) -> tuple[str, list[str]]:
    run_id = run_dir.name
    taf_source_id = "weather-source:taf:KJFK:test"
    bts_source_id = "bts_on_time:2026-05:nyc"
    advisory_content = (
        "SIGNATURE:\n"
        "26/05/19 20:30\n"
        "IMPACTING CONDITION: WEATHER / THUNDERSTORMS\n"
    )
    taf_content = json.dumps(
        {
            "icaoId": "KJFK",
            "issueTime": "2026-05-19T20:00:00Z",
            "rawTAF": "TAF KJFK TEST",
            "validTimeFrom": int(
                datetime(2026, 5, 19, 20, tzinfo=UTC).timestamp()
            ),
            "validTimeTo": int(
                datetime(2026, 5, 20, 2, tzinfo=UTC).timestamp()
            ),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    bts_content = "{}\n"
    snapshots = [
        SourceSnapshot(
            source_id=SOURCE_ID,
            family=SourceFamily.ATCSCC_ADVISORY,
            content=advisory_content,
            content_sha256=hashlib.sha256(
                advisory_content.encode()
            ).hexdigest(),
            snapshot_timestamp="2026-05-19T20:30:00+00:00",
        ),
        SourceSnapshot(
            source_id=taf_source_id,
            family=SourceFamily.TAF,
            content=taf_content,
            content_sha256=hashlib.sha256(taf_content.encode()).hexdigest(),
            snapshot_timestamp="2026-05-19T20:00:00+00:00",
        ),
        SourceSnapshot(
            source_id=bts_source_id,
            family=SourceFamily.BTS_ON_TIME,
            content=bts_content,
            content_sha256=hashlib.sha256(bts_content.encode()).hexdigest(),
            snapshot_timestamp="2026-05-19T20:00:00+00:00",
        ),
    ]
    taf_issue = datetime(2026, 5, 19, 20, tzinfo=UTC)
    taf_start = taf_issue
    taf_end = datetime(2026, 5, 20, 2, tzinfo=UTC)
    raw_taf = "TAF KJFK TEST"
    report_id = (
        "weather-report:taf:KJFK:20260519T200000Z:"
        f"{hashlib.sha256(raw_taf.encode()).hexdigest()[:16]}:"
        f"{snapshots[1].content_sha256[:16]}"
    )
    association_id = "weather-association:" + hashlib.sha256(
        "|".join(
            (
                run_id,
                EVENT_ID,
                report_id,
                FACILITY_ID,
                "latest_forecast_known_at_issue",
                snapshots[1].content_sha256,
            )
        ).encode()
    ).hexdigest()[:24]
    association = WeatherContextAssociation(
        association_id=association_id,
        run_id=run_id,
        event_id=EVENT_ID,
        report_id=report_id,
        facility_id=FACILITY_ID,
        relation_type="latest_forecast_known_at_issue",
        selection_method="latest eligible TAF by issue time",
        relevant_times={
            "advisory_issued_at": "2026-05-19T20:30:00+00:00",
            "forecast_issue_time": "2026-05-19T20:00:00+00:00",
            "forecast_valid_from": "2026-05-19T20:00:00+00:00",
            "forecast_valid_to": "2026-05-20T02:00:00+00:00",
            "operational_start": "2026-05-19T21:00:00+00:00",
            "operational_end": "2026-05-19T22:45:00+00:00",
        },
        source_id=taf_source_id,
        source_snapshot_sha256=snapshots[1].content_sha256,
        causal_claim=False,
    )
    start = datetime(2026, 5, 19, 21, tzinfo=UTC)
    end = datetime(2026, 5, 19, 22, 45, tzinfo=UTC)
    windows = {
        "baseline": (start - timedelta(hours=2), start),
        "active": (start, end),
        "recovery": (end, end + timedelta(hours=6)),
    }
    counts = {
        "baseline": (10, 9, 1, 0),
        "active": (20, 18, 2, 0),
        "recovery": (30, 28, 1, 1),
    }
    outcomes = []
    for phase, (window_start, window_end) in windows.items():
        scheduled, completed, cancelled, diverted = counts[phase]
        outcomes.append(
            BTSOutcomeSummary(
                summary_id=(
                    f"bts-outcome:{bts_source_id}:"
                    + hashlib.sha256(
                        "|".join(
                            (
                                run_id,
                                EVENT_ID,
                                FACILITY_ID,
                                phase,
                                window_start.isoformat(),
                                window_end.isoformat(),
                                bts_source_id,
                                snapshots[2].content_sha256,
                            )
                        ).encode()
                    ).hexdigest()[:24]
                ),
                run_id=run_id,
                event_id=EVENT_ID,
                facility_id=FACILITY_ID,
                phase=phase,
                window_start=window_start,
                window_end=window_end,
                source_id=bts_source_id,
                source_snapshot_sha256=snapshots[2].content_sha256,
                scheduled_arrival_count_proxy=scheduled,
                completed_arrival_count=completed,
                cancelled_count=cancelled,
                diverted_count=diverted,
                arrival_delay_15_count=1,
                mean_arrival_delay_minutes=None,
                median_arrival_delay_minutes=None,
                carrier_reported_weather_delay_minutes=None,
                carrier_reported_nas_delay_minutes=5.0,
                scheduled_arrival_semantics=(
                    "public scheduled-demand proxy; not FAA arrival demand"
                ),
                weather_delay_semantics=(
                    "carrier-reported attribution; not a causal claim"
                ),
                nas_delay_semantics=(
                    "carrier-reported attribution; not a causal claim"
                ),
                causal_claim=False,
            )
        )

    graph_rows = _rows()
    graph_rows.extend(
        [
            _weather_fact_row(
                report_id=report_id,
                predicate="rdf:type",
                predicate_iri=RDF_TYPE,
                value=(
                    "https://data.nasa.gov/ontologies/atmonto/"
                    "data#MeteorologicalReport"
                ),
                source_id=taf_source_id,
                object_kind="iri",
                object_class="data:MeteorologicalReport",
            ),
            _weather_fact_row(
                report_id=report_id,
                predicate="data:forecastingAirport",
                predicate_iri=FORECASTING_AIRPORT,
                value=FACILITY_ID,
                source_id=taf_source_id,
                object_kind="iri",
                object_class="nas:Airport",
            ),
            _weather_fact_row(
                report_id=report_id,
                predicate="data:tafReportString",
                predicate_iri=TAF_STRING,
                value="TAF KJFK TEST",
                source_id=taf_source_id,
                object_kind="literal",
                datatype_iri=XSD_STRING,
            ),
            _weather_fact_row(
                report_id=report_id,
                predicate="data:dataIntervalStartTime",
                predicate_iri=INTERVAL_START,
                value=taf_start.isoformat(),
                source_id=taf_source_id,
                object_kind="literal",
                datatype_iri=XSD_DATETIME,
            ),
            _weather_fact_row(
                report_id=report_id,
                predicate="data:dataIntervalEndTime",
                predicate_iri=INTERVAL_END,
                value=taf_end.isoformat(),
                source_id=taf_source_id,
                object_kind="literal",
                datatype_iri=XSD_DATETIME,
            ),
            _weather_fact_row(
                report_id=report_id,
                predicate="data:forecastIssueTime",
                predicate_iri=FORECAST_ISSUE_TIME,
                value=taf_issue.isoformat(),
                source_id=taf_source_id,
                object_kind="literal",
                datatype_iri=XSD_DATETIME,
            ),
        ]
    )
    _write_graph(run_dir, graph_rows)
    metadata = {
        "source_snapshots": _write_artifact(
            run_dir,
            "source_snapshots.jsonl",
            [snapshot.model_dump_json() for snapshot in snapshots],
        ),
        "context_associations": _write_artifact(
            run_dir,
            "context_associations.jsonl",
            [association.model_dump_json()],
        ),
        "outcome_summaries": _write_artifact(
            run_dir,
            "outcome_summaries.jsonl",
            [outcome.model_dump_json() for outcome in outcomes],
        ),
    }
    (run_dir / "run_manifest.json").write_text(
        json.dumps({"run_id": run_id, "context_artifacts": metadata}),
        encoding="utf-8",
    )
    return report_id, [outcome.summary_id for outcome in outcomes]


def _replace_registered_artifact(
    run_dir: Path,
    key: str,
    rows: list[dict[str, object]],
) -> None:
    manifest_path = run_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    filename = str(manifest["context_artifacts"][key]["path"])
    manifest["context_artifacts"][key] = _write_artifact(
        run_dir,
        filename,
        [json.dumps(row) for row in rows],
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def test_tool_registry_contains_only_read_only_query_tools(tmp_path):
    _write_graph(tmp_path)
    registry = tool_registry(build_query_tools(_gateway(tmp_path)))
    assert set(registry) == {
        "find_events",
        "get_event_facts",
        "get_neighbors",
        "get_profile_gaps",
        "get_provenance",
    }
    assert not any(
        token in name
        for name in registry
        for token in ("write", "create", "delete", "merge", "cypher", "sparql")
    )


def test_context_tools_are_typed_read_only_and_not_model_visible(tmp_path):
    _write_graph(tmp_path)
    report_id, outcome_ids = _write_context_layer(tmp_path)
    gateway = _gateway(tmp_path, with_context=True)

    model_registry = tool_registry(build_query_tools(gateway))
    context_registry = tool_registry(build_context_query_tools(gateway))

    assert set(model_registry) == {
        "find_events",
        "get_event_facts",
        "get_neighbors",
        "get_profile_gaps",
        "get_provenance",
    }
    assert set(context_registry) == {
        "get_decision_context",
        "get_outcome_summary",
    }
    context = json.loads(
        context_registry["get_decision_context"].invoke({"event_id": EVENT_ID})
    )
    outcomes = json.loads(
        context_registry["get_outcome_summary"].invoke(
            {"event_id": EVENT_ID}
        )
    )
    persisted_association = json.loads(
        (tmp_path / "context_associations.jsonl").read_text(encoding="utf-8")
    )
    assert context["context_association_ids"] == [
        persisted_association["association_id"]
    ]
    assert context["fact_ids"] == sorted(
        [
            expected_weather_fact_id(
                report_id,
                RDF_TYPE,
                (
                    "https://data.nasa.gov/ontologies/atmonto/"
                    "data#MeteorologicalReport"
                ),
            ),
            expected_weather_fact_id(
                report_id,
                FORECASTING_AIRPORT,
                FACILITY_ID,
            ),
            expected_weather_fact_id(
                report_id,
                TAF_STRING,
                "TAF KJFK TEST",
            ),
            expected_weather_fact_id(
                report_id,
                INTERVAL_START,
                "2026-05-19T20:00:00+00:00",
            ),
            expected_weather_fact_id(
                report_id,
                INTERVAL_END,
                "2026-05-20T02:00:00+00:00",
            ),
            expected_weather_fact_id(
                report_id,
                FORECAST_ISSUE_TIME,
                "2026-05-19T20:00:00+00:00",
            ),
        ]
    )
    assert outcomes["outcome_summary_ids"] == outcome_ids
    assert outcomes["items"][1]["mean_arrival_delay_minutes"] is None


def test_context_artifact_checksum_corruption_fails_closed(tmp_path):
    _write_graph(tmp_path)
    _write_context_layer(tmp_path)
    (tmp_path / "context_associations.jsonl").write_text(
        "{}\n",
        encoding="utf-8",
    )

    with pytest.raises(QueryToolError, match="checksum"):
        _gateway(tmp_path, with_context=True).get_decision_context(
            event_id=EVENT_ID
        )


def test_optional_artifact_without_manifest_registration_fails_closed(tmp_path):
    _write_graph(tmp_path)
    _write_context_layer(tmp_path)
    manifest_path = tmp_path / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["context_artifacts"].pop("context_associations")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(QueryToolError, match="without manifest registration"):
        _gateway(tmp_path, with_context=True).get_decision_context(
            event_id=EVENT_ID
        )


def test_optional_artifact_without_any_manifest_fails_closed(tmp_path):
    _write_graph(tmp_path)
    (tmp_path / "context_associations.jsonl").write_text("", encoding="utf-8")

    with pytest.raises(QueryToolError, match="without manifest registration"):
        _gateway(tmp_path, with_context=True).get_decision_context(
            event_id=EVENT_ID
        )


@pytest.mark.parametrize("status", ["insufficient", "blocked"])
def test_non_ok_context_manifest_status_cannot_hide_nonempty_rows(
    tmp_path,
    status,
):
    _write_graph(tmp_path)
    _write_context_layer(tmp_path)
    manifest_path = tmp_path / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["context_artifacts"]["context_associations"]["status"] = status
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(QueryToolError, match=f"{status} decision context"):
        _gateway(tmp_path, with_context=True).get_decision_context(
            event_id=EVENT_ID
        )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("run_id", "another-run", "run binding mismatch"),
        (
            "facility_id",
            "urn:aviation-agentic-ai:facility:airport:KEWR",
            "facility binding mismatch",
        ),
        ("source_snapshot_sha256", "0" * 64, "source binding mismatch"),
    ],
)
def test_context_cross_bindings_fail_closed(
    tmp_path,
    field,
    value,
    message,
):
    _write_graph(tmp_path)
    _write_context_layer(tmp_path)
    association = json.loads(
        (tmp_path / "context_associations.jsonl").read_text(encoding="utf-8")
    )
    association[field] = value
    _replace_registered_artifact(
        tmp_path,
        "context_associations",
        [association],
    )

    with pytest.raises(QueryToolError, match=message):
        _gateway(tmp_path, with_context=True).get_decision_context(
            event_id=EVENT_ID
        )


def test_duplicate_outcome_phase_fails_closed(tmp_path):
    _write_graph(tmp_path)
    _write_context_layer(tmp_path)
    rows = [
        json.loads(line)
        for line in (tmp_path / "outcome_summaries.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    rows[1]["phase"] = rows[0]["phase"]
    _replace_registered_artifact(tmp_path, "outcome_summaries", rows)

    with pytest.raises(QueryToolError, match="duplicate outcome phase"):
        _gateway(tmp_path, with_context=True).get_outcome_summary(
            event_id=EVENT_ID,
        )


def test_legacy_run_without_optional_context_keeps_core_queries_available(tmp_path):
    _write_graph(tmp_path)
    store = QueryGraphStore(tmp_path)
    gateway = QueryToolGateway(
        store,
        allowed_predicates={QueryPredicate.EVENT_TYPE.value},
        context_store=QueryContextStore(tmp_path, graph_store=store),
    )

    core = gateway.get_event_facts(
        event_id=EVENT_ID,
        predicates=[QueryPredicate.EVENT_TYPE],
    )
    context = gateway.get_decision_context(event_id=EVENT_ID)

    assert core.fact_ids == ["fact:type"]
    assert context.status == "insufficient"
    assert context.context_association_ids == []


def test_get_event_facts_returns_registered_facts_and_sources(tmp_path):
    _write_graph(tmp_path)
    gateway = _gateway(tmp_path)
    result = gateway.get_event_facts(
        event_id=EVENT_ID,
        predicates=list(QueryPredicate),
    )
    assert result.fact_ids == [
        "fact:type",
        "fact:facility",
        "fact:start",
        "fact:end",
    ]
    assert result.source_ids == [SOURCE_ID]
    assert {item["fact_id"] for item in result.items} == set(result.fact_ids)
    assert gateway.retrieved_fact_ids == set(result.fact_ids)


def test_get_event_facts_rejects_predicate_outside_current_scope(tmp_path):
    _write_graph(tmp_path)
    gateway = QueryToolGateway(
        QueryGraphStore(tmp_path),
        allowed_predicates={"rdf:type"},
    )
    with pytest.raises(QueryToolError, match="outside the current query scope"):
        gateway.get_event_facts(
            event_id=EVENT_ID,
            predicates=[QueryPredicate.CONTROLLED_NAS_ELEMENT],
        )


def test_framework_tool_schema_rejects_unknown_predicate(tmp_path):
    _write_graph(tmp_path)
    registry = tool_registry(build_query_tools(_gateway(tmp_path)))
    with pytest.raises(ValidationError):
        registry["get_event_facts"].invoke(
            {
                "event_id": EVENT_ID,
                "predicates": ["atm:runwaySurface"],
            }
        )


def test_provenance_requires_previously_retrieved_fact_ids(tmp_path):
    _write_graph(tmp_path)
    gateway = _gateway(tmp_path)
    with pytest.raises(QueryToolError, match="returned in this tool session"):
        gateway.get_provenance(fact_ids=["fact:type"])
    gateway.get_event_facts(
        event_id=EVENT_ID,
        predicates=[QueryPredicate.EVENT_TYPE],
    )
    result = gateway.get_provenance(fact_ids=["fact:type"])
    assert result.source_ids == [SOURCE_ID]
    assert result.items == [{"fact_id": "fact:type", "source_id": SOURCE_ID}]


def test_tool_blocks_unsourced_fact(tmp_path):
    rows = _rows()
    rows[1]["source_document"] = ""
    _write_graph(tmp_path, rows)
    gateway = _gateway(tmp_path)
    with pytest.raises(QueryToolError, match="missing provenance"):
        gateway.get_event_facts(
            event_id=EVENT_ID,
            predicates=[QueryPredicate.CONTROLLED_NAS_ELEMENT],
        )


def test_tool_cannot_escape_run_directory_via_symlink(tmp_path):
    run_dir = tmp_path / "run"
    outside = tmp_path / "outside"
    outside.mkdir()
    _write_graph(outside)
    run_dir.mkdir()
    (run_dir / "kg.jsonl").symlink_to(outside / "kg.jsonl")
    with pytest.raises(QueryToolError, match="escapes"):
        QueryGraphStore(run_dir)


def test_duplicate_fact_id_blocks_store(tmp_path):
    rows = _rows()
    rows.append(dict(rows[0]))
    _write_graph(tmp_path, rows)
    with pytest.raises(QueryToolError, match="duplicate graph fact ID"):
        QueryGraphStore(tmp_path)


def test_find_events_exposes_scope_metadata_not_fact_values(tmp_path):
    _write_graph(tmp_path)
    result = _gateway(tmp_path).find_events(source_id=SOURCE_ID)
    assert result.items[0]["event_id"] == EVENT_ID
    serialized = result.model_dump_json()
    assert "2026-05-19T21:00:00Z" not in serialized


def test_registered_events_require_an_event_type_assertion(tmp_path):
    rows = _rows()
    rows.append(
        {
            "triple_id": "fact:facility-type",
            "subject": "urn:aviation-agentic-ai:facility:airport:KLAX",
            "predicate": "rdf:type",
            "object": "nas:Airport",
            "subject_class": "nas:Airport",
            "object_class": "nas:Airport",
            "object_kind": "iri",
            "source_document": SOURCE_ID,
        }
    )
    _write_graph(tmp_path, rows)
    store = QueryGraphStore(tmp_path)
    assert store.event_ids == [EVENT_ID]


def test_valid_fact_request_with_no_match_returns_empty_observation(tmp_path):
    rows = [
        row
        for row in _rows()
        if row["predicate"] != QueryPredicate.EFFECTIVE_END.value
    ]
    _write_graph(tmp_path, rows)
    gateway = _gateway(tmp_path)
    result = gateway.get_event_facts(
        event_id=EVENT_ID,
        predicates=[QueryPredicate.EFFECTIVE_END],
    )
    assert result.fact_ids == []
    assert result.source_ids == []
    assert result.items == []


def test_find_events_caps_flattened_fact_references(tmp_path):
    rows = _rows()
    for index in range(25):
        rows.append(
            {
                "triple_id": f"fact:extra:{index:02d}",
                "subject": EVENT_ID,
                "predicate": "atm:advisoryNumber",
                "object": str(index),
                "subject_class": "atm:GroundStopTMI",
                "object_class": "",
                "object_kind": "literal",
                "source_document": SOURCE_ID,
            }
        )
    _write_graph(tmp_path, rows)
    result = _gateway(tmp_path).find_events()
    assert len(result.fact_ids) == 20
    assert len(result.items[0]["matching_fact_ids"]) == 20
