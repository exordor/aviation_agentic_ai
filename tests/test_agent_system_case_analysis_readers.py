"""Behavior tests for the bounded Decision Case Analysis readers."""

from __future__ import annotations

import importlib.util
import json
import hashlib
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.query_tools import QueryGraphStore


_FIXTURE_SPEC = importlib.util.spec_from_file_location(
    "query_tools_fixture",
    Path(__file__).with_name("test_agent_system_query_tools.py"),
)
assert _FIXTURE_SPEC is not None and _FIXTURE_SPEC.loader is not None
_fixture_module = importlib.util.module_from_spec(_FIXTURE_SPEC)
_FIXTURE_SPEC.loader.exec_module(_fixture_module)
EVENT_ID = _fixture_module.EVENT_ID
_write_context_layer = _fixture_module._write_context_layer
_write_formal_observation_layer = _fixture_module._write_formal_observation_layer
_write_graph = _fixture_module._write_graph


@pytest.fixture
def store(tmp_path) -> QueryGraphStore:
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


def test_episode_reader_returns_single_record_partial_without_grouping(
    store: QueryGraphStore,
) -> None:
    """Removing the no-grouping limit would overstate one record as an episode."""

    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        read_episode_timeline,
    )

    result = read_episode_timeline(store, event_id=EVENT_ID)

    assert result.status == "partial"
    assert result.limitation == (
        "single-record timeline; no advisory lifecycle grouping evidence"
    )
    assert {item["evidence_role"] for item in result.items} == {
        "formal_event_fact"
    }
    assert {
        item["predicate"] for item in result.items
    } >= {
        "rdf:type",
        "atm:effectiveStartTime",
        "atm:effectiveEndTime",
    }


def test_operational_situation_preserves_evidence_roles(
    store: QueryGraphStore,
) -> None:
    """Collapsing evidence roles would permit causal or source-role overclaiming."""

    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        read_operational_situation,
    )

    result = read_operational_situation(store, event_id=EVENT_ID)

    assert result.status == "ok"
    assert {item["evidence_role"] for item in result.items} >= {
        "formal_event_fact",
        "non_causal_weather_context",
        "bts_reported_public_observation",
    }
    weather_items = [
        item
        for item in result.items
        if item["evidence_role"] == "non_causal_weather_context"
    ]
    assert weather_items
    assert all(item["causal_claim"] is False for item in weather_items)
    bts_items = [
        item
        for item in result.items
        if item["evidence_role"] == "bts_reported_public_observation"
    ]
    assert bts_items
    assert all(item["causal_claim"] is False for item in bts_items)
    assert all(
        not {"faa_capacity", "faa_demand", "edct"}.intersection(item)
        for item in bts_items
    )


def test_operational_situation_requires_active_bts_observations(tmp_path) -> None:
    """Treating a missing active public-observation layer as ok hides a gap."""

    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        read_operational_situation,
    )

    _write_graph(tmp_path)
    _write_context_layer(tmp_path)
    result = read_operational_situation(
        QueryGraphStore(tmp_path),
        event_id=EVENT_ID,
    )

    assert result.status == "insufficient"
    assert result.limitation == "missing evidence layer: active BTS observation"


def test_readers_block_an_unknown_event(store: QueryGraphStore) -> None:
    """Accepting an unknown ID would let the fixed plan escape its run scope."""

    from aviation_agentic_ai.agent_system.case_analysis_tools import (
        read_episode_timeline,
        read_operational_situation,
    )

    unknown = "urn:aviation-agentic-ai:event:unknown"

    assert read_episode_timeline(store, event_id=unknown).status == "blocked"
    assert read_operational_situation(store, event_id=unknown).status == "blocked"
