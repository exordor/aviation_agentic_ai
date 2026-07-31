"""Exact corpus filtering followed by TMI-event vector recall."""

from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
    TMIEventSimilarityQuery,
    TMIEventVectorHit,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_search import (
    rank_tmi_events_by_metadata,
)
from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusArtifactMetadata,
    CorpusBuildManifest,
    CorpusTMIEvent,
    CorpusQueryStore,
)


ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
KJFK = "urn:aviation-agentic-ai:facility:airport:KJFK"
KEWR = "urn:aviation-agentic-ai:facility:airport:KEWR"


def _event(
    name: str,
    *,
    facility_id: str = KJFK,
    start: str = "2026-05-19T08:00:00+00:00",
    end: str = "2026-05-19T10:00:00+00:00",
    reason_status: str = "formal",
    reason_value: str | None = "weather",
) -> CorpusTMIEvent:
    return CorpusTMIEvent(
        event_id=f"event:{name}",
        advisory_source_id=f"2026-05-19:{name}",
        event_type_iris=[f"{ATM}GroundDelayProgramTMI"],
        facility_ids=[facility_id],
        effective_start=start,
        effective_end=end,
        reason_status=reason_status,
        reason_value=reason_value,
    )


def _write_jsonl(
    path: Path,
    rows: list[StrictModel],
) -> CorpusArtifactMetadata:
    data = "".join(row.model_dump_json() + "\n" for row in rows).encode()
    path.write_bytes(data)
    return CorpusArtifactMetadata(
        path=path.name,
        count=len(rows),
        sha256=hashlib.sha256(data).hexdigest(),
    )


def _store(tmp_path: Path, events: list[CorpusTMIEvent]) -> CorpusQueryStore:
    artifacts = {
        "events": _write_jsonl(tmp_path / "events.jsonl", events),
        "facts": _write_jsonl(tmp_path / "facts.jsonl", []),
        "event_facts": _write_jsonl(tmp_path / "event_facts.jsonl", []),
        "source_bindings": _write_jsonl(
            tmp_path / "source_bindings.jsonl",
            [],
        ),
    }
    manifest = CorpusBuildManifest(
        corpus_id="corpus:search-test",
        run_count=len(events),
        event_count=len(events),
        fact_count=0,
        source_binding_count=0,
        source_object_count=0,
        artifacts=artifacts,
    )
    (tmp_path / "corpus_manifest.json").write_text(
        manifest.model_dump_json() + "\n",
        encoding="utf-8",
    )
    return CorpusQueryStore(tmp_path)


class FakeIndex:
    def __init__(
        self,
        events: list[CorpusTMIEvent],
        scores: dict[str, float],
    ) -> None:
        self.manifest = SimpleNamespace(
            representation_version="tmi-event-record-v1",
            embedding_model_id="test/four-dimensional",
        )
        self._event_by_id = {event.event_id: event for event in events}
        self._scores = scores
        self.last_candidate_event_ids: tuple[str, ...] = ()
        self.last_n_results = 0
        self.anchor_event_id = ""

    def get_event_vector(self, event_id: str) -> tuple[float, ...]:
        self.anchor_event_id = event_id
        return (1.0, 0.0, 0.0, 0.0)

    def query_candidates(
        self,
        *,
        query_vector,
        candidate_event_ids,
        n_results,
    ) -> tuple[TMIEventVectorHit, ...]:
        assert tuple(query_vector) == (1.0, 0.0, 0.0, 0.0)
        self.last_candidate_event_ids = tuple(candidate_event_ids)
        self.last_n_results = n_results
        reverse_ties = sorted(candidate_event_ids, reverse=True)
        ranked = sorted(
            reverse_ties,
            key=lambda event_id: self._scores[event_id],
            reverse=True,
        )
        return tuple(
            TMIEventVectorHit(
                event_id=event_id,
                advisory_source_id=self._event_by_id[
                    event_id
                ].advisory_source_id,
                distance=1.0 - self._scores[event_id],
                similarity=self._scores[event_id],
            )
            for event_id in ranked[:n_results]
        )


def test_exact_filters_are_applied_before_cosine_ranking(
    tmp_path: Path,
) -> None:
    events = [
        _event("query"),
        _event("kjfk-nearest"),
        _event("kjfk-second"),
        _event("kewr-higher-score", facility_id=KEWR),
    ]
    store = _store(tmp_path, events)
    index = FakeIndex(
        events,
        {
            "event:query": 1.0,
            "event:kjfk-nearest": 0.91,
            "event:kjfk-second": 0.82,
            "event:kewr-higher-score": 0.99,
        },
    )

    result = rank_tmi_events_by_metadata(
        store,
        index,
        TMIEventSimilarityQuery(
            reference_event_id="event:query",
            facility_id=KJFK,
            limit=3,
        ),
    )

    assert result.status == "ok"
    assert result.candidate_count == 2
    assert [row.event_id for row in result.matches] == [
        "event:kjfk-nearest",
        "event:kjfk-second",
    ]
    assert all(row.facility_ids == (KJFK,) for row in result.matches)
    assert index.anchor_event_id == "event:query"
    assert index.last_candidate_event_ids == (
        "event:kjfk-nearest",
        "event:kjfk-second",
    )


def test_prior_scope_excludes_same_time_and_later_events(
    tmp_path: Path,
) -> None:
    events = [
        _event(
            "query",
            start="2026-05-19T12:00:00+00:00",
            end="2026-05-19T14:00:00+00:00",
        ),
        _event("earlier", end="2026-05-19T11:59:59+00:00"),
        _event("same-time", end="2026-05-19T12:00:00+00:00"),
        _event("later", end="2026-05-19T13:00:00+00:00"),
    ]
    store = _store(tmp_path, events)
    index = FakeIndex(
        events,
        {
            "event:query": 1.0,
            "event:earlier": 0.7,
            "event:same-time": 0.99,
            "event:later": 0.98,
        },
    )

    result = rank_tmi_events_by_metadata(
        store,
        index,
        TMIEventSimilarityQuery(
            reference_event_id="event:query",
            candidate_scope="prior",
        ),
    )

    assert result.status == "ok"
    assert result.candidate_count == 1
    assert [row.event_id for row in result.matches] == ["event:earlier"]
    assert index.last_candidate_event_ids == ("event:earlier",)


def test_equal_scores_are_tied_by_event_id(tmp_path: Path) -> None:
    events = [
        _event("query"),
        _event("b"),
        _event("a"),
        _event("c"),
    ]
    store = _store(tmp_path, events)
    index = FakeIndex(
        events,
        {
            "event:query": 1.0,
            "event:a": 0.8,
            "event:b": 0.8,
            "event:c": 0.9,
        },
    )

    result = rank_tmi_events_by_metadata(
        store,
        index,
        TMIEventSimilarityQuery(
            reference_event_id="event:query",
            limit=3,
        ),
    )

    assert [row.event_id for row in result.matches] == [
        "event:c",
        "event:a",
        "event:b",
    ]
    assert [row.rank for row in result.matches] == [1, 2, 3]


def test_offset_and_limit_are_applied_after_ranking(
    tmp_path: Path,
) -> None:
    events = [
        _event("query"),
        _event("a"),
        _event("b"),
        _event("c"),
    ]
    store = _store(tmp_path, events)
    index = FakeIndex(
        events,
        {
            "event:query": 1.0,
            "event:a": 0.8,
            "event:b": 0.7,
            "event:c": 0.9,
        },
    )

    result = rank_tmi_events_by_metadata(
        store,
        index,
        TMIEventSimilarityQuery(
            reference_event_id="event:query",
            offset=1,
            limit=1,
        ),
    )

    assert result.candidate_count == 3
    assert [row.event_id for row in result.matches] == ["event:a"]
    assert [row.rank for row in result.matches] == [2]
    assert index.last_n_results == 2


def test_empty_exact_candidate_set_is_insufficient(
    tmp_path: Path,
) -> None:
    events = [_event("query"), _event("other", facility_id=KEWR)]
    store = _store(tmp_path, events)
    index = FakeIndex(
        events,
        {"event:query": 1.0, "event:other": 0.9},
    )

    result = rank_tmi_events_by_metadata(
        store,
        index,
        TMIEventSimilarityQuery(
            reference_event_id="event:query",
            facility_id="urn:aviation-agentic-ai:facility:airport:KLGA",
        ),
    )

    assert result.status == "insufficient"
    assert result.candidate_count == 0
    assert result.matches == ()
    assert index.anchor_event_id == ""
