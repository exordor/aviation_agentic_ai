"""Focused contracts for the Query Agent's read-only graph tools."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from aviation_agentic_ai.agent_system.query_tools import (
    QueryGraphStore,
    QueryPredicate,
    QueryToolError,
    QueryToolGateway,
    build_query_tools,
    tool_registry,
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


def _gateway(run_dir: Path) -> QueryToolGateway:
    return QueryToolGateway(
        QueryGraphStore(run_dir),
        allowed_predicates={predicate.value for predicate in QueryPredicate},
    )


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
