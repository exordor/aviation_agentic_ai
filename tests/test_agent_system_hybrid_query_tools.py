"""Corpus-bound read-tool tests for the HybridRAG Query Agent."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.case_retrieval_index import (
    build_case_retrieval_index,
)
from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryScope,
    HybridQueryToolObservation,
)
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusQueryStore,
    build_corpus,
)
from aviation_agentic_ai.agent_system.hybrid_query_tools import (
    HybridQueryGateway,
    build_hybrid_query_tools,
)


_FIXTURE_SPEC = importlib.util.spec_from_file_location(
    "hybrid_query_corpus_fixture",
    Path(__file__).with_name("test_agent_system_corpus_store.py"),
)
assert _FIXTURE_SPEC is not None and _FIXTURE_SPEC.loader is not None
_fixture = importlib.util.module_from_spec(_FIXTURE_SPEC)
_FIXTURE_SPEC.loader.exec_module(_fixture)

CONTEXT_EVENT_ID = _fixture._fixture_module.EVENT_ID
FORMAL_EVENT_ID = "urn:event:formal-reason"
GAP_EVENT_ID = "urn:event:profile-gap"
MISSING_EVENT_ID = "urn:event:missing-reason"


class _TinyEncoder:
    model_id = "test/tiny-encoder"

    def encode(self, texts):  # type: ignore[no-untyped-def]
        return [
            [float(index + 1), float(len(text) % 7 + 1), 1.0]
            for index, text in enumerate(texts)
        ]


def _corpus(tmp_path: Path, *, with_index: bool = False) -> Path:
    context_run = tmp_path / "run-context"
    formal_run = tmp_path / "run-formal"
    gap_run = tmp_path / "run-gap"
    missing_run = tmp_path / "run-missing"
    _fixture._write_context_run(context_run)
    _fixture._write_run(
        formal_run,
        event_id=FORMAL_EVENT_ID,
        suffix="formal",
        event_type="atm:GroundDelayProgramTMI",
        formal_reason="weather",
    )
    _fixture._write_run(
        gap_run,
        event_id=GAP_EVENT_ID,
        suffix="gap",
    )
    _fixture._write_reason_profile_gap(gap_run, event_id=GAP_EVENT_ID)
    _fixture._write_run(
        missing_run,
        event_id=MISSING_EVENT_ID,
        suffix="missing",
    )
    corpus_dir = tmp_path / "corpus"
    build_corpus(
        [context_run, formal_run, gap_run, missing_run],
        corpus_dir,
    )
    if with_index:
        build_case_retrieval_index(corpus_dir, encoder=_TinyEncoder())
    return corpus_dir


def _scope(**updates: object) -> HybridQueryScope:
    return HybridQueryScope(
        candidate_scope="archive",
        offset=0,
        limit=20,
    ).model_copy(update=updates)


def _observation_corpus(tmp_path: Path) -> Path:
    run_dir = tmp_path / "run-observations"
    _fixture._fixture_module._write_formal_observation_layer(run_dir)
    corpus_dir = tmp_path / "observation-corpus"
    build_corpus([run_dir], corpus_dir)
    return corpus_dir


def _gateway(
    corpus_dir: Path,
    **scope_updates: object,
) -> HybridQueryGateway:
    return HybridQueryGateway(
        store=CorpusQueryStore(corpus_dir),
        scope=_scope(**scope_updates),
    )


def test_tool_registry_exposes_only_six_read_only_tools(tmp_path: Path) -> None:
    gateway = _gateway(_corpus(tmp_path))

    tools = build_hybrid_query_tools(gateway)

    assert [tool.name for tool in tools] == [
        "find_cases",
        "read_case_facts",
        "read_weather_context",
        "read_public_observations",
        "read_case_graph",
        "find_similar_cases",
    ]
    result = next(tool for tool in tools if tool.name == "read_case_facts").invoke(
        {"event_id": FORMAL_EVENT_ID}
    )
    assert HybridQueryToolObservation.model_validate(result).status == "ok"


def test_find_cases_returns_bounded_case_identifiers(tmp_path: Path) -> None:
    gateway = _gateway(_corpus(tmp_path), limit=2)

    observation = gateway.find_cases(limit=2)
    payload = json.loads(observation.content)

    assert observation.status == "ok"
    assert payload["total_matches"] == 4
    assert len(payload["cases"]) == 2
    assert len(observation.details.case_ids) == 2


def test_explicit_event_scope_cannot_be_broadened(tmp_path: Path) -> None:
    gateway = _gateway(
        _corpus(tmp_path),
        event_id=FORMAL_EVENT_ID,
    )

    assert gateway.read_case_facts(event_id=FORMAL_EVENT_ID).status == "ok"
    with pytest.raises(ValueError, match="outside the query scope"):
        gateway.read_weather_context(event_id=CONTEXT_EVENT_ID)
    with pytest.raises(ValueError, match="outside the query scope"):
        gateway.read_case_graph(event_id=MISSING_EVENT_ID)


def test_catalog_filters_and_page_bounds_cannot_be_broadened(
    tmp_path: Path,
) -> None:
    facility = _fixture._fixture_module.FACILITY_ID
    gateway = _gateway(
        _corpus(tmp_path),
        facility_id=facility,
        reason_status="formal",
        offset=1,
        limit=2,
    )

    observation = gateway.find_cases(
        facility_id=facility,
        reason_status="formal",
        offset=1,
        limit=1,
    )

    assert observation.status in {"ok", "insufficient"}
    with pytest.raises(ValueError, match="facility_id"):
        gateway.find_cases(facility_id="urn:facility:other")
    with pytest.raises(ValueError, match="offset"):
        gateway.find_cases(offset=0)
    with pytest.raises(ValueError, match="limit"):
        gateway.find_cases(offset=1, limit=3)
    with pytest.raises(ValueError, match="outside the query scope"):
        gateway.read_case_facts(event_id=MISSING_EVENT_ID)


def test_case_facts_preserve_formal_gap_and_missing_reason_states(
    tmp_path: Path,
) -> None:
    gateway = _gateway(_corpus(tmp_path))

    formal_observation = gateway.read_case_facts(event_id=FORMAL_EVENT_ID)
    formal = json.loads(formal_observation.content)
    gap_observation = gateway.read_case_facts(event_id=GAP_EVENT_ID)
    gap = json.loads(gap_observation.content)
    missing = json.loads(
        gateway.read_case_facts(event_id=MISSING_EVENT_ID).content
    )

    assert formal["case"]["reason_status"] == "formal"
    assert formal["case"]["reason_value"] == "weather"
    assert formal["facts"]
    assert all(
        fact["subject_iri"] == FORMAL_EVENT_ID for fact in formal["facts"]
    )
    assert len(formal_observation.details.fact_ids) == len(formal["facts"])
    assert gap["case"]["reason_status"] == "profile_gap"
    assert gap["profile_gaps"][0]["evidence_text"] == (
        "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
    )
    assert gap_observation.details.profile_gap_ids
    assert missing["case"]["reason_status"] == "missing"
    assert missing["case"]["reason_value"] is None


def test_weather_and_bts_tools_keep_their_evidence_roles(tmp_path: Path) -> None:
    gateway = _gateway(_corpus(tmp_path))
    observation_gateway = _gateway(_observation_corpus(tmp_path))

    weather = gateway.read_weather_context(event_id=CONTEXT_EVENT_ID)
    observations = observation_gateway.read_public_observations(
        event_id=CONTEXT_EVENT_ID,
        phases=("active",),
    )
    weather_payload = json.loads(weather.content)
    observation_payload = json.loads(observations.content)

    assert weather.status == "ok"
    assert weather_payload["causal_claim"] is False
    assert weather.details.context_association_ids
    assert {record.kind for record in weather.support_records} == {
        "non_causal_context"
    }
    assert all(
        record.context_association_ids and record.source_ids
        for record in weather.support_records
    )
    assert observation_payload["evidence_role"] == (
        "bts_reported_public_observation"
    )
    assert observation_payload["not_interpreted_as"] == [
        "FAA demand",
        "FAA capacity",
        "FAA AAR",
        "FAA EDCT",
        "decision cause",
    ]
    assert all(
        "fact_ids" not in row for row in observation_payload["observations"]
    )
    assert observations.details.observation_ids
    assert {record.kind for record in observations.support_records} == {
        "public_observation"
    }
    assert all(
        record.observation_ids and record.source_ids
        for record in observations.support_records
    )


def test_case_graph_is_general_and_case_scoped(tmp_path: Path) -> None:
    gateway = _gateway(_corpus(tmp_path))

    graph = gateway.read_case_graph(event_id=FORMAL_EVENT_ID)
    payload = json.loads(graph.content)

    assert graph.status == "ok"
    assert payload["event_id"] == FORMAL_EVENT_ID
    assert any(edge["subject_iri"] == FORMAL_EVENT_ID for edge in payload["edges"])
    assert not any(
        edge["subject_iri"] == MISSING_EVENT_ID for edge in payload["edges"]
    )
    assert graph.details.fact_ids
    assert {record.kind for record in graph.support_records} == {"source_fact"}
    assert all(
        record.fact_ids and record.source_ids
        for record in graph.support_records
    )


def test_similarity_uses_the_corpus_bound_index(tmp_path: Path) -> None:
    corpus_dir = _corpus(tmp_path, with_index=True)
    gateway = _gateway(corpus_dir)

    observation = gateway.find_similar_cases(
        reference_event_id=FORMAL_EVENT_ID,
        candidate_scope="archive",
        limit=2,
    )

    assert observation.status == "ok"
    assert observation.similarity_matches
    assert FORMAL_EVENT_ID not in {
        match.event_id for match in observation.similarity_matches
    }
    assert observation.details.case_ids == tuple(
        match.case_id for match in observation.similarity_matches
    )
    assert {record.kind for record in observation.support_records} == {
        "similarity"
    }


def test_missing_case_index_is_insufficient(tmp_path: Path) -> None:
    gateway = _gateway(_corpus(tmp_path))

    observation = gateway.find_similar_cases(
        reference_event_id=FORMAL_EVENT_ID,
        candidate_scope="archive",
    )

    assert observation.status == "insufficient"
    assert "index-cases" in observation.limitation
