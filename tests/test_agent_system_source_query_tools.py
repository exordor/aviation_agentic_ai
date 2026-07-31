"""Source-query boundaries over the live aviation evidence store."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryScope,
    SourceFamily,
)
from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
)
from aviation_agentic_ai.agent_system.hybrid_query_tools import (
    HybridQueryGateway,
)
from aviation_agentic_ai.agent_system.ingestion_package import (
    EventIngestionPackage,
    IngestionAttempt,
)
from aviation_agentic_ai.agent_system.query_runtime import QueryRuntime
from aviation_agentic_ai.agent_system.source_retrieval import (
    build_source_record_chunk,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    IngestionResult,
    SourceChunkRecord,
    SourceVersionRecord,
    TMIEventRecord,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_index import (
    SourceChunkVectorHit,
)
from aviation_agentic_ai.utils.identifiers import stable_id


@dataclass(frozen=True)
class SourceQueryScenario:
    store: AviationEvidenceStore
    event_a: TMIEventRecord
    event_b: TMIEventRecord
    advisory_a: SourceVersionRecord
    advisory_a_revision: SourceVersionRecord
    advisory_b: SourceVersionRecord
    term: SourceVersionRecord
    metar: SourceVersionRecord
    chunks: dict[str, SourceChunkRecord]


class TinySourceIndex:
    """A minimal semantic-index reader used only to test query plumbing."""

    def __init__(
        self,
        hits: tuple[SourceChunkVectorHit, ...],
    ) -> None:
        self.hits = hits
        self.calls: list[dict[str, object]] = []

    def query_chunks(
        self,
        *,
        query_text: str,
        candidate_source_version_ids: tuple[str, ...],
        n_results: int,
    ) -> tuple[SourceChunkVectorHit, ...]:
        self.calls.append(
            {
                "query_text": query_text,
                "candidate_source_version_ids": (
                    candidate_source_version_ids
                ),
                "n_results": n_results,
            }
        )
        allowed = set(candidate_source_version_ids)
        return tuple(
            hit
            for hit in self.hits
            if hit.source_version_id in allowed
        )[:n_results]


def _source_version(
    source_id: str,
    family: SourceFamily,
    content: str,
) -> SourceVersionRecord:
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return SourceVersionRecord(
        source_version_id=stable_id(
            "source-version",
            source_id,
            digest,
        ),
        source_id=source_id,
        family=family,
        asset_id=None,
        content=content,
        content_sha256=digest,
        source_url=f"https://example.test/{source_id}",
        logical_time="2026-05-19T09:00:00Z",
        metadata={"title": source_id},
    )


def _publish_event(
    store: AviationEvidenceStore,
    *,
    event_id: str,
    advisory: SourceVersionRecord,
    bound_sources: tuple[SourceVersionRecord, ...],
) -> TMIEventRecord:
    publication_digest = hashlib.sha256(
        f"{event_id}:{advisory.source_version_id}".encode()
    ).hexdigest()
    publication_id = stable_id(
        "event-publication",
        event_id,
        advisory.source_version_id,
        publication_digest,
    )
    event = TMIEventRecord(
        event_id=event_id,
        publication_id=publication_id,
        advisory_source_id=advisory.source_id,
        publication_source_version_id=advisory.source_version_id,
        event_type_iris=("atm:GroundStopTMI",),
        facility_ids=("urn:facility:KJFK",),
        effective_start=datetime(2026, 5, 19, 10, tzinfo=UTC),
        effective_end=datetime(2026, 5, 19, 12, tzinfo=UTC),
        issued_at=datetime(2026, 5, 19, 9, tzinfo=UTC),
        reason_status="missing",
        reason_value=None,
    )
    package = EventIngestionPackage(
        event=event,
        formal_publication_digest=publication_digest,
        source_version_ids=tuple(
            source.source_version_id for source in bound_sources
        ),
        source_anchors=(),
        facts=(),
        event_fact_memberships=(),
        evidence_links=(),
        profile_gaps=(),
        weather_associations=(),
        public_observations=(),
        observation_fact_ids={},
    )
    store.apply_ingestion_attempt(
        IngestionAttempt(
            result=IngestionResult(
                source_version_id=advisory.source_version_id,
                source_id=advisory.source_id,
                status="ok",
                event_id=event_id,
                publication_id=publication_id,
                reason="accepted",
                provider_call_count=0,
                tmi_family="ground_stop",
                preflight_eligible=True,
            ),
            package=package,
        )
    )
    return event


@pytest.fixture
def source_scenario(tmp_path: Path):
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:source-tools",
        create=True,
    )
    advisory_a = _source_version(
        "source:advisory:A",
        SourceFamily.ATCSCC_ADVISORY,
        "GROUND STOP A DUE TO THUNDERSTORMS",
    )
    advisory_b = _source_version(
        "source:advisory:B",
        SourceFamily.ATCSCC_ADVISORY,
        "GROUND STOP B DUE TO VOLUME",
    )
    term = _source_version(
        "source:term:weather",
        SourceFamily.FAA_TERM,
        "WEATHER includes thunderstorms and rain.",
    )
    metar = _source_version(
        "source:metar:KJFK",
        SourceFamily.METAR,
        "KJFK METAR records rain and reduced visibility.",
    )
    for version in (advisory_a, advisory_b, term, metar):
        store.register_source_version(version)

    event_a = _publish_event(
        store,
        event_id="urn:event:A",
        advisory=advisory_a,
        bound_sources=(advisory_a, term),
    )
    event_b = _publish_event(
        store,
        event_id="urn:event:B",
        advisory=advisory_b,
        bound_sources=(advisory_b,),
    )

    advisory_a_revision = _source_version(
        advisory_a.source_id,
        SourceFamily.ATCSCC_ADVISORY,
        "GROUND STOP A EXTENDED DUE TO THUNDERSTORMS",
    )
    store.register_source_version(advisory_a_revision)

    chunks: dict[str, SourceChunkRecord] = {}
    for version, event_id in (
        (advisory_a, None),
        (advisory_a_revision, None),
        (advisory_b, None),
        (term, None),
        (metar, None),
    ):
        chunk = build_source_record_chunk(version, event_id=event_id)
        assert chunk is not None
        chunks[version.source_version_id] = chunk
    store.upsert_source_chunks(tuple(chunks.values()))

    try:
        yield SourceQueryScenario(
            store=store,
            event_a=event_a,
            event_b=event_b,
            advisory_a=advisory_a,
            advisory_a_revision=advisory_a_revision,
            advisory_b=advisory_b,
            term=term,
            metar=metar,
            chunks=chunks,
        )
    finally:
        store.close()


def _gateway(
    scenario: SourceQueryScenario,
    *,
    scope: HybridQueryScope,
    source_index: TinySourceIndex | None = None,
) -> HybridQueryGateway:
    return HybridQueryGateway(
        runtime=QueryRuntime(
            store=scenario.store,
            source_index=source_index,  # type: ignore[arg-type]
            event_index=None,
        ),
        scope=scope,
    )


def test_lexical_search_returns_candidates_from_the_bound_event_version(
    source_scenario: SourceQueryScenario,
) -> None:
    """Event search must retain its accepted version after a blocked revision."""

    gateway = _gateway(
        source_scenario,
        scope=HybridQueryScope(event_id=source_scenario.event_a.event_id),
    )

    observation = gateway.search_source_text(
        query='"GROUND STOP A"',
        event_id=source_scenario.event_a.event_id,
        limit=10,
    )

    expected_chunk = source_scenario.chunks[
        source_scenario.advisory_a.source_version_id
    ]
    assert observation.status == "ok"
    assert observation.details.source_version_ids == (
        source_scenario.advisory_a.source_version_id,
    )
    assert observation.details.chunk_ids == (expected_chunk.chunk_id,)
    assert observation.support_records == ()
    assert "GROUND STOP A" in observation.content
    assert "EXTENDED" not in observation.content


def test_event_scoped_lexical_search_uses_source_bindings_not_chunk_ownership(
    source_scenario: SourceQueryScenario,
) -> None:
    """A reusable authority chunk remains visible through its event binding."""

    gateway = _gateway(
        source_scenario,
        scope=HybridQueryScope(event_id=source_scenario.event_a.event_id),
    )

    observation = gateway.search_source_text(
        query="WEATHER",
        families=(SourceFamily.FAA_TERM,),
        event_id=source_scenario.event_a.event_id,
        limit=10,
    )

    assert observation.status == "ok"
    assert observation.details.source_version_ids == (
        source_scenario.term.source_version_id,
    )
    assert observation.support_records == ()


def test_semantic_search_returns_candidates_without_statement_support(
    source_scenario: SourceQueryScenario,
) -> None:
    chunk = source_scenario.chunks[
        source_scenario.advisory_a.source_version_id
    ]
    index = TinySourceIndex(
        (
            SourceChunkVectorHit(
                chunk_id=chunk.chunk_id,
                source_version_id=chunk.source_version_id,
                source_anchor_id=chunk.source_anchor_id,
                distance=0.1,
                similarity=0.9,
            ),
        )
    )
    gateway = _gateway(
        source_scenario,
        scope=HybridQueryScope(event_id=source_scenario.event_a.event_id),
        source_index=index,
    )

    observation = gateway.semantic_search_sources(
        query="airport restriction caused by storms",
        event_id=source_scenario.event_a.event_id,
        limit=5,
    )

    assert observation.status == "ok"
    assert observation.details.source_version_ids == (
        source_scenario.advisory_a.source_version_id,
    )
    assert observation.details.source_anchor_ids == (
        chunk.source_anchor_id,
    )
    assert observation.details.chunk_ids == (chunk.chunk_id,)
    assert observation.support_records == ()
    assert index.calls == [
        {
            "query_text": "airport restriction caused by storms",
            "candidate_source_version_ids": tuple(
                sorted(
                    (
                        source_scenario.advisory_a.source_version_id,
                        source_scenario.term.source_version_id,
                    )
                )
            ),
            "n_results": 5,
        }
    ]


def test_exact_source_read_returns_version_and_anchor_support(
    source_scenario: SourceQueryScenario,
) -> None:
    version = source_scenario.advisory_a
    chunk = source_scenario.chunks[version.source_version_id]
    gateway = _gateway(
        source_scenario,
        scope=HybridQueryScope(event_id=source_scenario.event_a.event_id),
    )

    observation = gateway.read_source(
        source_version_id=version.source_version_id,
        source_anchor_id=chunk.source_anchor_id,
        offset=0,
        max_chars=8000,
    )
    payload = json.loads(observation.content)

    assert observation.status == "ok"
    assert payload["source_id"] == version.source_id
    assert payload["source_version_id"] == version.source_version_id
    assert payload["source_anchor_id"] == chunk.source_anchor_id
    assert payload["family"] == SourceFamily.ATCSCC_ADVISORY.value
    assert payload["content_sha256"] == version.content_sha256
    assert payload["bounded_text"] == version.content
    assert payload["offset"] == 0
    assert payload["end"] == len(version.content)
    assert payload["source_url"] == version.source_url
    assert observation.details.source_ids == (version.source_id,)
    assert observation.details.source_version_ids == (
        version.source_version_id,
    )
    assert observation.details.source_anchor_ids == (
        chunk.source_anchor_id,
    )
    assert observation.details.chunk_ids == (chunk.chunk_id,)
    assert len(observation.support_records) == 1
    support = observation.support_records[0]
    assert support.kind == "source_record"
    assert support.source_ids == (version.source_id,)
    assert support.source_version_ids == (version.source_version_id,)
    assert support.source_anchor_ids == (chunk.source_anchor_id,)
    assert support.chunk_ids == (chunk.chunk_id,)


@pytest.mark.parametrize("foreign_kind", ("event", "revision", "anchor"))
def test_exact_read_rejects_sources_outside_the_event_publication(
    source_scenario: SourceQueryScenario,
    foreign_kind: str,
) -> None:
    """Logical identity or an anchor alone must not broaden event scope."""

    gateway = _gateway(
        source_scenario,
        scope=HybridQueryScope(event_id=source_scenario.event_a.event_id),
    )
    version = source_scenario.advisory_a
    anchor = source_scenario.chunks[version.source_version_id].source_anchor_id
    if foreign_kind == "event":
        version = source_scenario.advisory_b
        anchor = source_scenario.chunks[
            version.source_version_id
        ].source_anchor_id
    elif foreign_kind == "revision":
        version = source_scenario.advisory_a_revision
        anchor = source_scenario.chunks[
            version.source_version_id
        ].source_anchor_id
    elif foreign_kind == "anchor":
        anchor = source_scenario.chunks[
            source_scenario.advisory_b.source_version_id
        ].source_anchor_id

    with pytest.raises(ValueError, match="scope|version|anchor"):
        gateway.read_source(
            source_version_id=version.source_version_id,
            source_anchor_id=anchor,
        )


def test_source_and_family_scope_narrow_lexical_candidates(
    source_scenario: SourceQueryScenario,
) -> None:
    gateway = _gateway(
        source_scenario,
        scope=HybridQueryScope(
            source_ids=(source_scenario.term.source_id,),
            source_families=(SourceFamily.FAA_TERM,),
        ),
    )

    observation = gateway.search_source_text(
        query="rain",
        families=(SourceFamily.FAA_TERM,),
        limit=10,
    )

    assert observation.status == "ok"
    assert observation.details.source_ids == (
        source_scenario.term.source_id,
    )
    assert observation.details.source_version_ids == (
        source_scenario.term.source_version_id,
    )
    assert "WEATHER includes" in observation.content
    assert "METAR" not in observation.content

    with pytest.raises(ValueError, match="famil"):
        gateway.search_source_text(
            query="rain",
            families=(SourceFamily.METAR,),
        )


def test_missing_source_vector_index_is_tool_level_insufficient(
    source_scenario: SourceQueryScenario,
) -> None:
    gateway = _gateway(
        source_scenario,
        scope=HybridQueryScope(event_id=source_scenario.event_a.event_id),
        source_index=None,
    )

    observation = gateway.semantic_search_sources(
        query="storm restrictions",
        event_id=source_scenario.event_a.event_id,
    )

    assert observation.status == "insufficient"
    assert observation.details.source_version_ids == ()
    assert observation.details.chunk_ids == ()
    assert observation.support_records == ()
    assert "vector" in (
        f"{observation.content} {observation.limitation}".lower()
    )
