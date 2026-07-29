"""Focused contracts and shared fixtures for the formal graph store."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.contracts import (
    BTSManifestBinding,
    BTSOnTimeRow,
    BTSOutcomeSummary,
    DecisionCaseMemberBinding,
    DecisionContextEvent,
    SourceFamily,
    SourceSnapshot,
    SourceSnapshotRegistry,
    WeatherContextAssociation,
    WeatherContextBundle,
)
from aviation_agentic_ai.agent_system.bts_outcomes import (
    build_bts_outcome_summaries,
)
from aviation_agentic_ai.agent_system.materialize import (
    write_validated_facts_jsonl,
)
from aviation_agentic_ai.agent_system.public_observations import (
    build_bts_observation_facts,
)
from aviation_agentic_ai.agent_system.decision_case_graph import (
    build_decision_case_graph,
    prepare_decision_case_reconstruction,
)
from aviation_agentic_ai.agent_system.query_tools import (
    QueryGraphStore,
    QueryToolError,
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
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)
from aviation_agentic_ai.cross_source.contracts import (
    CanonicalEntity,
    CodeValue,
    EntityType,
)

EVENT_ID = "urn:aviation-agentic-ai:event:tool-test"
FACILITY_ID = "urn:aviation-agentic-ai:facility:airport:KJFK"
SOURCE_ID = "2026-05-19:123"
ADVISORY_CONTENT = (
    "SIGNATURE:\n"
    "26/05/19 20:30\n"
    "IMPACTING CONDITION: WEATHER / THUNDERSTORMS\n"
)
PROFILE_REGISTRY = load_validation_profile_registry(
    decision_guide=load_schema_guide()
)
PROFILE_BY_LAYER = {
    profile.ref.layer: profile.ref for profile in PROFILE_REGISTRY.profiles
}


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


def _write_graph(
    run_dir: Path,
    rows: list[dict] | None = None,
    *,
    snapshots: list[SourceSnapshot] | tuple[SourceSnapshot, ...] | None = None,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    if snapshots is None:
        snapshots = (
            SourceSnapshot(
                source_id=SOURCE_ID,
                family=SourceFamily.ATCSCC_ADVISORY,
                content=ADVISORY_CONTENT,
                content_sha256=hashlib.sha256(
                    ADVISORY_CONTENT.encode()
                ).hexdigest(),
                snapshot_timestamp="2026-05-19T20:30:00+00:00",
            ),
        )
    registry = SourceSnapshotRegistry(snapshots=tuple(snapshots))
    snapshot_path = registry.write_jsonl(run_dir)
    snapshot_checksums = {
        snapshot.source_id: snapshot.content_sha256
        for snapshot in registry.snapshots
    }
    payload: list[dict[str, object]] = []
    for source_row in rows if rows is not None else _rows():
        row = dict(source_row)
        layer = str(
            row.get("validation_layer")
            or (
                "weather"
                if row.get("subject_class") == "data:MeteorologicalReport"
                else "decision"
            )
        )
        profile = PROFILE_BY_LAYER[layer]
        evidence_mode = str(
            row.get("evidence_mode") or "source_text"
        )
        source_ids = row.get("source_ids")
        if not isinstance(source_ids, list):
            source_ids = [
                source_id.strip()
                for source_id in str(row.get("source_document") or "").split(";")
                if source_id.strip()
            ]
        row.update(
            {
                "evidence_text": str(
                    row.get("evidence_text")
                    or ("SIGNATURE:" if evidence_mode == "source_text" else "")
                ),
                "datatype_iri": str(
                    row.get("datatype_iri")
                    or (
                        XSD_DATETIME
                        if row.get("predicate")
                        in {
                            "atm:effectiveStartTime",
                            "atm:effectiveEndTime",
                        }
                        else XSD_STRING
                        if row.get("object_kind") == "literal"
                        else ""
                    )
                ),
                "profile_id": str(
                    row.get("profile_id") or profile.profile_id
                ),
                "profile_checksum": str(
                    row.get("profile_checksum")
                    or profile.profile_checksum
                ),
                "validation_layer": layer,
                "evidence_mode": evidence_mode,
                "evidence_ref": str(
                    row.get("evidence_ref") or row["triple_id"]
                ),
                "source_ids": source_ids,
                "source_snapshot_checksums": {
                    source_id: snapshot_checksums[source_id]
                    for source_id in source_ids
                    if source_id in snapshot_checksums
                },
            }
        )
        payload.append(row)
    (run_dir / "kg.jsonl").write_text(
        "\n".join(json.dumps(row) for row in payload) + "\n",
        encoding="utf-8",
    )
    layer_counts = {
        layer: sum(
            row["validation_layer"] == layer for row in payload
        )
        for layer in PROFILE_BY_LAYER
    }
    profile_refs = {
        (
            str(row["profile_id"]),
            str(row["profile_checksum"]),
            str(row["validation_layer"]),
        )
        for row in payload
    }
    snapshot_data = snapshot_path.read_bytes()
    decision_trace_by_id = {
        str(row["triple_id"]): {
                "fact_id": row["triple_id"],
                "graph_patch_line": "",
                "source_id": row["source_ids"][0],
                "evidence_text": row["evidence_text"],
                "evidence_agent_role": "advisory",
                "source_snapshot_sha256": row[
                    "source_snapshot_checksums"
                ][row["source_ids"][0]],
            }
        for row in payload
        if row["validation_layer"] == "decision"
        and row["evidence_mode"] == "source_text"
        and row["source_ids"]
    }
    decision_trace_rows = [
        json.dumps(row)
        for row in decision_trace_by_id.values()
    ]
    fact_trace_metadata = _write_artifact(
        run_dir,
        "fact_trace.jsonl",
        decision_trace_rows,
        status="ok",
    )
    weather_trace_rows = [
        json.dumps(
            {
                "fact_id": row["triple_id"],
                "source_id": row["source_ids"][0],
                "source_snapshot_sha256": row[
                    "source_snapshot_checksums"
                ][row["source_ids"][0]],
                "evidence_text": row["evidence_text"],
            }
        )
        for row in payload
        if row["validation_layer"] == "weather"
        and row["evidence_mode"] == "source_text"
        and row["source_ids"]
    ]
    weather_status = (
        "ok" if layer_counts["weather"] else "insufficient"
    )
    weather_trace_metadata = _write_artifact(
        run_dir,
        "weather_fact_trace.jsonl",
        weather_trace_rows,
        status=weather_status,
    )
    observation_trace_metadata = _write_artifact(
        run_dir,
        "observation_fact_trace.jsonl",
        [],
        status="insufficient",
    )
    reconstruction_metadata = _write_artifact(
        run_dir,
        "reconstruction_trace.json",
        [],
        status="insufficient",
    )
    profile_gap_metadata = _write_artifact(
        run_dir,
        "profile_gaps.jsonl",
        [],
        status=(
            "ok" if layer_counts["decision"] else "insufficient"
        ),
    )
    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "manifest_version": "decision-case-run-v1",
                "run_id": run_dir.name,
                "source_id": SOURCE_ID,
                "materialization": {
                    "materialized": True,
                    "fact_count": len(payload),
                    "profile_refs": [
                        {
                            "profile_id": profile_id,
                            "profile_checksum": checksum,
                            "layer": layer,
                        }
                        for profile_id, checksum, layer in sorted(
                            profile_refs
                        )
                    ],
                    "layer_fact_counts": {
                        layer: count
                        for layer, count in layer_counts.items()
                        if count
                    },
                    "artifacts": {
                        "kg_jsonl": str(run_dir / "kg.jsonl"),
                    },
                },
                "formal_layers": {
                    layer: {
                        "status": "ok" if layer_counts[layer] else "insufficient",
                        "profile_id": profile.profile_id,
                        "profile_checksum": profile.profile_checksum,
                        "formal_fact_count": layer_counts[layer],
                    }
                    for layer, profile in PROFILE_BY_LAYER.items()
                },
                "context_artifacts": {
                    "source_snapshots": {
                        "path": "source_snapshots.jsonl",
                        "count": len(registry.snapshots),
                        "sha256": hashlib.sha256(snapshot_data).hexdigest(),
                        "status": "ok",
                    },
                    "fact_trace": fact_trace_metadata,
                    "weather_fact_trace": weather_trace_metadata,
                    "observation_fact_trace": (
                        observation_trace_metadata
                    ),
                    "reconstruction_trace": reconstruction_metadata,
                },
                "profile_gaps": profile_gap_metadata,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
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
    advisory_content = ADVISORY_CONTENT
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
                        json.dumps(
                            {
                                "event_id": EVENT_ID,
                                "facility_id": FACILITY_ID,
                                "phase": phase,
                                "run_id": run_id,
                                "source_id": bts_source_id,
                                "source_snapshot_sha256": snapshots[2].content_sha256,
                                "window_end": window_end.isoformat(),
                                "window_start": window_start.isoformat(),
                            },
                            sort_keys=True,
                            separators=(",", ":"),
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
                scheduled_arrival_count=scheduled,
                completed_arrival_count=completed,
                cancelled_count=cancelled,
                diverted_count=diverted,
                arrival_delay_15_count=1,
                mean_arrival_delay_minutes=None,
                median_arrival_delay_minutes=None,
                carrier_reported_weather_delay_minutes=None,
                carrier_reported_nas_delay_minutes=5.0,
                reporting_scope=(
                    "BTS On-Time reporting carriers and scheduled domestic passenger operations."
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
    _write_graph(run_dir, graph_rows, snapshots=snapshots)
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
    manifest_path = run_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["context_artifacts"].update(metadata)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return report_id, [outcome.summary_id for outcome in outcomes]


def _write_formal_observation_layer(run_dir: Path) -> tuple[list[str], list[str]]:
    """Upgrade the legacy context fixture with Task 5 formal observations."""

    _write_context_layer(run_dir)
    snapshot_rows = [
        SourceSnapshot.model_validate_json(line)
        for line in (run_dir / "source_snapshots.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    arrivals = (
        datetime(2026, 5, 19, 20, 30, tzinfo=UTC),
        datetime(2026, 5, 19, 21, 30, tzinfo=UTC),
        datetime(2026, 5, 19, 23, 0, tzinfo=UTC),
    )
    archive_sha256 = "a" * 64
    bts_rows = [
        BTSOnTimeRow(
            row_id="bts-row:"
            + hashlib.sha256(
                "|".join(
                    (
                        archive_sha256,
                        "2026-05-19",
                        "1",
                        str(index),
                        "1",
                        "2",
                        "1800",
                    )
                ).encode()
            ).hexdigest(),
            FlightDate="2026-05-19",
            DOT_ID_Reporting_Airline=1,
            Reporting_Airline="AA",
            IATA_CODE_Reporting_Airline="AA",
            Flight_Number_Reporting_Airline=index,
            OriginAirportSeqID=1,
            DestAirportSeqID=2,
            CRSDepTime=1800,
            Origin="ORD",
            Dest="JFK",
            CRSArrTime=2000,
            CRSElapsedTime=120,
            scheduled_arrival_utc=arrival,
            Cancelled=0,
            Diverted=0,
            ArrDelay=0.0,
            ArrDel15=0,
            WeatherDelay=None,
            NASDelay=0.0,
        )
        for index, arrival in enumerate(arrivals, 1)
    ]
    bts_content = "".join(
        json.dumps(
            row.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for row in sorted(bts_rows, key=lambda item: item.row_id)
    )
    bts_snapshot = SourceSnapshot(
        source_id="bts_on_time:2026-05:nyc",
        family=SourceFamily.BTS_ON_TIME,
        content=bts_content,
        content_sha256=hashlib.sha256(bts_content.encode()).hexdigest(),
        snapshot_timestamp="2026-05-19T20:00:00+00:00",
    )
    registry = SourceSnapshotRegistry(
        snapshots=tuple(
            bts_snapshot
            if snapshot.family == SourceFamily.BTS_ON_TIME
            else snapshot
            for snapshot in snapshot_rows
        )
    )
    profile_registry = load_validation_profile_registry(
        decision_guide=load_schema_guide()
    )
    public_profile = next(
        profile
        for profile in profile_registry.profiles
        if profile.ref.layer == "public_operational_observation"
    )
    assert public_profile.aggregation_procedure is not None
    event = DecisionContextEvent(
        run_id=run_dir.name,
        event_id=EVENT_ID,
        advisory_source_id=SOURCE_ID,
        advisory_issued_at=datetime(2026, 5, 19, 20, 30, tzinfo=UTC),
        operational_start=datetime(2026, 5, 19, 21, tzinfo=UTC),
        operational_end=datetime(2026, 5, 19, 22, 45, tzinfo=UTC),
    )
    facility = CanonicalEntity(
        entity_id=FACILITY_ID,
        entity_type=EntityType.AIRPORT,
        preferred_label="John F Kennedy International Airport",
        codes=[
            CodeValue(scheme="IATA", value="JFK"),
            CodeValue(scheme="ICAO", value="KJFK"),
        ],
    )
    outcome = build_bts_outcome_summaries(
        event,
        facility,
        bts_rows,
        source_id=bts_snapshot.source_id,
        source_snapshot_sha256=bts_snapshot.content_sha256,
        manifest_binding=BTSManifestBinding(
            source_id=bts_snapshot.source_id,
            archive_sha256=archive_sha256,
            normalized_snapshot_sha256=bts_snapshot.content_sha256,
        ),
        aggregation_procedure=public_profile.aggregation_procedure,
    )
    assert outcome.status == "ok", outcome.failure_reason
    reconstruction_seed = prepare_decision_case_reconstruction(
        event,
        facility,
        WeatherContextBundle(
            status="insufficient",
            failure_reason="no Weather source was provided",
        ),
        outcome,
        registry,
        profile_registry,
    )
    observations = build_bts_observation_facts(
        event,
        facility,
        outcome,
        registry,
        profile_registry,
        reconstruction_seed,
    )
    assert observations.status == "ok"
    core = build_decision_case_graph(
        seed=reconstruction_seed,
        members=(
            DecisionCaseMemberBinding(
                member_iri=event.event_id,
                member_kind="event",
                source_ids=(event.advisory_source_id,),
            ),
            *(
                DecisionCaseMemberBinding(
                    member_iri=observation_id,
                    member_kind="public_observation",
                    source_ids=(bts_snapshot.source_id,),
                )
                for observation_id in observations.observation_ids
            ),
        ),
        profile_registry=profile_registry,
    )
    assert core.status == "ok", core.failure_reason
    assert core.reconstruction_trace is not None
    formal_facts = [*observations.formal_facts, *core.formal_facts]
    formal_dir = run_dir / "formal-observation-fixture"
    formal_path = write_validated_facts_jsonl(
        facts=formal_facts,
        output_dir=formal_dir,
        profile_registry=profile_registry,
        source_snapshot=registry,
    )
    graph_rows = [
        json.loads(line)
        for line in (run_dir / "kg.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    graph_rows.extend(
        json.loads(line)
        for line in Path(formal_path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    _write_graph(run_dir, graph_rows, snapshots=registry.snapshots)
    snapshot_metadata = _write_artifact(
        run_dir,
        "source_snapshots.jsonl",
        [snapshot.model_dump_json() for snapshot in registry.snapshots],
    )
    outcome_metadata = _write_artifact(
        run_dir,
        "outcome_summaries.jsonl",
        [summary.model_dump_json() for summary in outcome.summaries],
    )
    derivation_metadata = _write_artifact(
        run_dir,
        "observation_derivations.jsonl",
        [row.model_dump_json() for row in observations.derivations],
    )
    trace_metadata = _write_artifact(
        run_dir,
        "observation_fact_trace.jsonl",
        [row.model_dump_json() for row in observations.fact_traces],
    )
    reconstruction_metadata = _write_artifact(
        run_dir,
        "reconstruction_trace.json",
        [core.reconstruction_trace.model_dump_json()],
    )
    manifest_path = run_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["context_artifacts"].update(
        {
            "source_snapshots": snapshot_metadata,
            "outcome_summaries": outcome_metadata,
            "observation_derivations": derivation_metadata,
            "observation_fact_trace": trace_metadata,
            "reconstruction_trace": reconstruction_metadata,
        }
    )
    core_profile = next(
        profile
        for profile in profile_registry.profiles
        if profile.ref.layer == "decision_case_core"
    )
    manifest["formal_layers"]["decision_case_core"] = {
        "status": "ok",
        "profile_id": core_profile.ref.profile_id,
        "profile_checksum": core_profile.ref.profile_checksum,
        "formal_fact_count": len(core.formal_facts),
    }
    manifest["formal_layers"]["public_operational_observation"] = {
            "status": "ok",
            "profile_id": public_profile.ref.profile_id,
            "profile_checksum": public_profile.ref.profile_checksum,
            "formal_fact_count": len(observations.formal_facts),
    }
    manifest["public_observation_publication"] = {
        "status": "ok",
        "aggregation_procedure_id": (
            public_profile.aggregation_procedure.procedure_id
        ),
        "aggregation_procedure_checksum": (
            public_profile.aggregation_procedure.checksum
        ),
        "bts_source_id": bts_snapshot.source_id,
        "bts_source_snapshot_sha256": bts_snapshot.content_sha256,
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return (
        [trace.observation_id for trace in observations.fact_traces],
        [row.derivation_id for row in observations.derivations],
    )


def test_store_rejects_self_consistent_weather_reason_owned_by_decision_profile(
    tmp_path,
):
    weather_source_id = "weather-source:metar:KJFK:forged-reason"
    evidence = "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
    snapshot = SourceSnapshot(
        source_id=weather_source_id,
        family=SourceFamily.METAR,
        content=ADVISORY_CONTENT,
        content_sha256=hashlib.sha256(ADVISORY_CONTENT.encode()).hexdigest(),
        snapshot_timestamp="2026-05-19T20:30:00+00:00",
    )
    rows = [
        {
            "triple_id": "fact:forged-type",
            "subject": EVENT_ID,
            "predicate": "rdf:type",
            "object": "atm:GroundStopTMI",
            "subject_class": "atm:GroundStopTMI",
            "object_class": "atm:GroundStopTMI",
            "object_kind": "iri",
            "source_document": weather_source_id,
            "evidence_text": evidence,
        },
        {
            "triple_id": "fact:forged-reason",
            "subject": EVENT_ID,
            "predicate": "atm:impactingCondition",
            "object": "WEATHER / THUNDERSTORMS",
            "subject_class": "atm:GroundStopTMI",
            "object_class": "",
            "object_kind": "literal",
            "source_document": weather_source_id,
            "evidence_text": evidence,
        },
    ]
    _write_graph(tmp_path, rows, snapshots=[snapshot])

    with pytest.raises(QueryToolError, match="publication contract"):
        QueryGraphStore(tmp_path)


def test_store_rejects_graph_row_bound_to_another_direct_fact_trace(tmp_path):
    _write_graph(tmp_path)
    graph_path = tmp_path / "kg.jsonl"
    rows = [
        json.loads(line)
        for line in graph_path.read_text(encoding="utf-8").splitlines()
    ]
    rows[0]["evidence_ref"] = rows[1]["triple_id"]
    graph_path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(QueryToolError, match="evidence reference mismatch"):
        QueryGraphStore(tmp_path)


def test_store_rejects_graph_evidence_text_that_disagrees_with_trace(tmp_path):
    _write_graph(tmp_path)
    graph_path = tmp_path / "kg.jsonl"
    rows = [
        json.loads(line)
        for line in graph_path.read_text(encoding="utf-8").splitlines()
    ]
    rows[0]["evidence_text"] = (
        "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
    )
    graph_path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(QueryToolError, match="evidence text mismatch"):
        QueryGraphStore(tmp_path)


def test_tool_cannot_escape_run_directory_via_symlink(tmp_path):
    run_dir = tmp_path / "run"
    outside = tmp_path / "outside"
    outside.mkdir()
    _write_graph(outside)
    run_dir.mkdir()
    for name in (
        "run_manifest.json",
        "source_snapshots.jsonl",
        "fact_trace.jsonl",
        "weather_fact_trace.jsonl",
        "observation_fact_trace.jsonl",
        "reconstruction_trace.json",
    ):
        (run_dir / name).write_bytes((outside / name).read_bytes())
    (run_dir / "kg.jsonl").symlink_to(outside / "kg.jsonl")
    with pytest.raises(QueryToolError, match="escapes"):
        QueryGraphStore(run_dir)


def test_duplicate_fact_id_blocks_store(tmp_path):
    rows = _rows()
    rows.append(dict(rows[0]))
    _write_graph(tmp_path, rows)
    with pytest.raises(QueryToolError, match="duplicate graph fact ID"):
        QueryGraphStore(tmp_path)


def test_store_blocks_unsourced_fact(tmp_path):
    rows = _rows()
    rows[1]["source_document"] = ""
    _write_graph(tmp_path, rows)
    with pytest.raises(QueryToolError, match="no evidence source"):
        QueryGraphStore(tmp_path)


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
