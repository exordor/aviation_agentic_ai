"""Exact store filtering followed by active-publication vector recall."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
)
from aviation_agentic_ai.agent_system.ingestion_package import (
    EventIngestionPackage,
    IngestionAttempt,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    IngestionResult,
    SourceVersionRecord,
    TMIEventRecord,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
    TMIEventSimilarityQuery,
    TMIEventVectorHit,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_search import (
    rank_tmi_events_by_metadata,
)
from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.utils.identifiers import stable_id


ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
KJFK = "urn:aviation-agentic-ai:facility:airport:KJFK"
KEWR = "urn:aviation-agentic-ai:facility:airport:KEWR"


def _version(source_id: str) -> SourceVersionRecord:
    content = f"ADVISORY {source_id}"
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return SourceVersionRecord(
        source_version_id=stable_id("source-version", source_id, digest),
        source_id=source_id,
        family=SourceFamily.ATCSCC_ADVISORY,
        asset_id=None,
        content=content,
        content_sha256=digest,
        source_url=None,
        logical_time=None,
        metadata={},
    )


def _event(
    store: AviationEvidenceStore,
    name: str,
    *,
    facility_id: str = KJFK,
    start: str = "2026-05-19T08:00:00+00:00",
    end: str = "2026-05-19T10:00:00+00:00",
    reason_status: str = "formal",
    reason_value: str | None = "weather",
) -> TMIEventRecord:
    source_id = f"2026-05-19:{name}"
    version = _version(source_id)
    store.register_source_version(version)
    event_id = f"event:{name}"
    publication_digest = hashlib.sha256(
        event_id.encode("utf-8")
    ).hexdigest()
    publication_id = stable_id(
        "knowledge-publication",
        event_id,
        version.source_version_id,
        publication_digest,
    )
    event = TMIEventRecord(
        event_id=event_id,
        publication_id=publication_id,
        advisory_source_id=source_id,
        publication_source_version_id=version.source_version_id,
        event_type_iris=(f"{ATM}GroundDelayProgramTMI",),
        facility_ids=(facility_id,),
        effective_start=datetime.fromisoformat(start),
        effective_end=datetime.fromisoformat(end),
        issued_at=datetime(2026, 5, 19, 7, tzinfo=UTC),
        reason_status=reason_status,
        reason_value=reason_value,
    )
    store.apply_ingestion_attempt(
        IngestionAttempt(
            result=IngestionResult(
                source_version_id=version.source_version_id,
                source_id=source_id,
                status="ok",
                event_id=event_id,
                publication_id=publication_id,
                reason="accepted",
                provider_call_count=0,
                tmi_family="GDP",
                preflight_eligible=True,
            ),
            package=EventIngestionPackage(
                event=event,
                formal_publication_digest=publication_digest,
                source_version_ids=(version.source_version_id,),
                source_anchors=(),
                facts=(),
                event_fact_memberships=(),
                evidence_links=(),
                profile_gaps=(),
                weather_associations=(),
                public_observations=(),
                observation_fact_ids={},
            ),
        )
    )
    return event


def _store(
    tmp_path: Path,
    specs: list[tuple[str, dict[str, object]]],
) -> tuple[AviationEvidenceStore, list[TMIEventRecord]]:
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:search-test",
        create=True,
    )
    events = [_event(store, name, **kwargs) for name, kwargs in specs]
    return store, events


class FakeIndex:
    def __init__(
        self,
        events: list[TMIEventRecord],
        scores: dict[str, float],
    ) -> None:
        self.state = SimpleNamespace(
            representation_version="tmi-event-record-v1",
            embedding_model_id="test/four-dimensional",
        )
        self._event_by_publication = {
            event.publication_id: event for event in events
        }
        self._scores = scores
        self.last_candidate_publication_ids: tuple[str, ...] = ()
        self.last_n_results = 0
        self.anchor_publication_id = ""

    def get_publication_vector(
        self,
        publication_id: str,
    ) -> tuple[float, ...]:
        self.anchor_publication_id = publication_id
        return (1.0, 0.0, 0.0, 0.0)

    def query_candidates(
        self,
        *,
        query_vector,
        candidate_publication_ids,
        n_results,
    ) -> tuple[TMIEventVectorHit, ...]:
        assert tuple(query_vector) == (1.0, 0.0, 0.0, 0.0)
        self.last_candidate_publication_ids = tuple(
            candidate_publication_ids
        )
        self.last_n_results = n_results
        reverse_ties = sorted(candidate_publication_ids, reverse=True)
        ranked = sorted(
            reverse_ties,
            key=lambda publication_id: self._scores[
                self._event_by_publication[publication_id].event_id
            ],
            reverse=True,
        )
        return tuple(
            TMIEventVectorHit(
                event_id=self._event_by_publication[
                    publication_id
                ].event_id,
                publication_id=publication_id,
                advisory_source_id=self._event_by_publication[
                    publication_id
                ].advisory_source_id,
                distance=(
                    1.0
                    - self._scores[
                        self._event_by_publication[
                            publication_id
                        ].event_id
                    ]
                ),
                similarity=self._scores[
                    self._event_by_publication[publication_id].event_id
                ],
            )
            for publication_id in ranked[:n_results]
        )


def test_exact_filters_are_applied_before_cosine_ranking(
    tmp_path: Path,
) -> None:
    store, events = _store(
        tmp_path,
        [
            ("query", {}),
            ("kjfk-nearest", {}),
            ("kjfk-second", {}),
            ("kewr-higher-score", {"facility_id": KEWR}),
        ],
    )
    try:
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
        assert index.anchor_publication_id == events[0].publication_id
        assert index.last_candidate_publication_ids == (
            events[1].publication_id,
            events[2].publication_id,
        )
    finally:
        store.close()


def test_prior_scope_excludes_same_time_and_later_events(
    tmp_path: Path,
) -> None:
    store, events = _store(
        tmp_path,
        [
            (
                "query",
                {
                    "start": "2026-05-19T12:00:00+00:00",
                    "end": "2026-05-19T14:00:00+00:00",
                },
            ),
            ("earlier", {"end": "2026-05-19T11:59:59+00:00"}),
            ("same-time", {"end": "2026-05-19T12:00:00+00:00"}),
            ("later", {"end": "2026-05-19T13:00:00+00:00"}),
        ],
    )
    try:
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
        assert index.last_candidate_publication_ids == (
            events[1].publication_id,
        )
    finally:
        store.close()


def test_equal_scores_are_tied_by_event_id(tmp_path: Path) -> None:
    store, events = _store(
        tmp_path,
        [("query", {}), ("b", {}), ("a", {}), ("c", {})],
    )
    try:
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
    finally:
        store.close()


def test_offset_and_limit_are_applied_after_ranking(
    tmp_path: Path,
) -> None:
    store, events = _store(
        tmp_path,
        [("query", {}), ("a", {}), ("b", {}), ("c", {})],
    )
    try:
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
    finally:
        store.close()


def test_empty_exact_candidate_set_is_insufficient(
    tmp_path: Path,
) -> None:
    store, events = _store(
        tmp_path,
        [("query", {}), ("other", {"facility_id": KEWR})],
    )
    try:
        index = FakeIndex(
            events,
            {"event:query": 1.0, "event:other": 0.9},
        )

        result = rank_tmi_events_by_metadata(
            store,
            index,
            TMIEventSimilarityQuery(
                reference_event_id="event:query",
                facility_id=(
                    "urn:aviation-agentic-ai:facility:airport:KLGA"
                ),
            ),
        )

        assert result.status == "insufficient"
        assert result.candidate_count == 0
        assert result.matches == ()
        assert index.anchor_publication_id == ""
    finally:
        store.close()
