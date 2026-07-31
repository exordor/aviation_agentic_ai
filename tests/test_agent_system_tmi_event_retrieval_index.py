"""Persistent incremental vector indexes over the SQLite evidence store."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Sequence

import pytest

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
    SCHEMA_VERSION,
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
from aviation_agentic_ai.agent_system.tmi_event_retrieval_index import (
    SOURCE_CHUNK_COLLECTION,
    TMI_EVENT_COLLECTION,
    ChromaSourceRetrievalIndex,
    ChromaTMIEventRetrievalIndex,
    mark_vector_indexes_blocked,
    reindex_store,
    update_store_indexes,
)
from aviation_agentic_ai.utils.identifiers import stable_id
from aviation_agentic_ai.retrieval.chroma_store import (
    get_collection,
    open_persistent_client,
)


ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
KJFK = "urn:aviation-agentic-ai:facility:airport:KJFK"


class RecordingEncoder:
    model_id = "test/two-dimensional"

    def __init__(self) -> None:
        self.calls: list[tuple[str, ...]] = []

    def encode(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        self.calls.append(tuple(texts))
        return [
            [float(index + 1), 1.0]
            for index, _text in enumerate(texts)
        ]


class FailingEncoder:
    model_id = "test/failing"

    def encode(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        raise RuntimeError("embedding provider unavailable")


@pytest.fixture
def evidence_store(tmp_path: Path):
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:index",
        create=True,
    )
    try:
        yield store
    finally:
        store.close()


def _source_version(
    source_id: str,
    content: str,
) -> SourceVersionRecord:
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return SourceVersionRecord(
        source_version_id=stable_id("source-version", source_id, digest),
        source_id=source_id,
        family=SourceFamily.ATCSCC_ADVISORY,
        asset_id=None,
        content=content,
        content_sha256=digest,
        source_url=None,
        logical_time="2026-05-19T09:00:00Z",
        metadata={"title": source_id},
    )


def _publish_event(
    store: AviationEvidenceStore,
    *,
    event_id: str = "urn:event:revision",
    source_id: str = "2026-05-19:138",
    content: str,
) -> TMIEventRecord:
    version = _source_version(source_id, content)
    store.register_source_version(version)
    publication_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
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
        facility_ids=(KJFK,),
        effective_start=datetime(2026, 5, 19, 10, tzinfo=UTC),
        effective_end=datetime(2026, 5, 19, 12, tzinfo=UTC),
        issued_at=datetime(2026, 5, 19, 9, tzinfo=UTC),
        reason_status="formal",
        reason_value="weather",
    )
    package = EventIngestionPackage(
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
                tmi_family="ground_delay_program",
                preflight_eligible=True,
            ),
            package=package,
        )
    )
    return event


def _metadata_by_id(collection) -> dict[str, dict[str, object]]:
    payload = collection.get(include=["metadatas"])
    return {
        record_id: metadata
        for record_id, metadata in zip(
            payload["ids"],
            payload["metadatas"],
            strict=True,
        )
    }


def test_incremental_update_persists_both_indexes_and_skips_reencoding(
    evidence_store: AviationEvidenceStore,
    tmp_path: Path,
) -> None:
    """Re-encoding an unchanged store would waste provider work."""

    event = _publish_event(evidence_store, content="GDP ORIGINAL")
    encoder = RecordingEncoder()
    chroma_dir = tmp_path / "chroma"

    first = update_store_indexes(
        evidence_store,
        chroma_dir,
        encoder=encoder,
    )
    second = update_store_indexes(
        evidence_store,
        chroma_dir,
        encoder=encoder,
    )

    assert tuple(state.collection_name for state in first) == (
        TMI_EVENT_COLLECTION,
        SOURCE_CHUNK_COLLECTION,
    )
    assert second == tuple(
        evidence_store.get_vector_index_state(state.collection_name)
        for state in second
    )
    assert len(encoder.calls) == 2
    assert sum(len(call) for call in encoder.calls) == 2
    assert all(state.status == "current" for state in second)
    assert all(state.embedding_dimension == 2 for state in second)
    assert all(
        state.indexed_knowledge_revision
        == evidence_store.get_knowledge_revision()
        for state in second
    )

    chunks = evidence_store.list_source_chunks()
    assert len(chunks) == 1
    assert chunks[0].text == "GDP ORIGINAL"
    assert chunks[0].source_version_id == (
        event.publication_source_version_id
    )
    assert chunks[0].char_start == 0
    assert chunks[0].char_end == len("GDP ORIGINAL")

    client = open_persistent_client(chroma_dir)
    event_collection = get_collection(
        client,
        TMI_EVENT_COLLECTION,
        embedding_function=None,
    )
    source_collection = get_collection(
        client,
        SOURCE_CHUNK_COLLECTION,
        embedding_function=None,
    )
    assert event_collection.count() == 1
    assert source_collection.count() == 1
    assert event_collection.metadata["dataset_id"] == "dataset:index"
    assert (
        event_collection.metadata["evidence_store_schema_version"]
        == SCHEMA_VERSION
    )
    assert next(iter(_metadata_by_id(event_collection).values()))[
        "active"
    ] is True
    assert next(iter(_metadata_by_id(source_collection).values()))[
        "active"
    ] is True

    index = ChromaTMIEventRetrievalIndex(evidence_store, chroma_dir)
    vector = index.get_publication_vector(event.publication_id)
    assert sum(value * value for value in vector) == pytest.approx(1.0)
    hits = index.query_candidates(
        query_vector=vector,
        candidate_publication_ids=(event.publication_id,),
        n_results=1,
    )
    assert tuple(hit.publication_id for hit in hits) == (
        event.publication_id,
    )
    assert hits[0].event_id == event.event_id

    source_index = ChromaSourceRetrievalIndex(
        evidence_store,
        chroma_dir,
        encoder,
    )
    source_hits = source_index.query_chunks(
        query_text="original GDP",
        candidate_source_version_ids=(
            event.publication_source_version_id,
        ),
        n_results=1,
    )
    assert tuple(hit.source_version_id for hit in source_hits) == (
        event.publication_source_version_id,
    )
    assert source_hits[0].chunk_id == chunks[0].chunk_id
    assert source_hits[0].source_anchor_id == chunks[0].source_anchor_id


def test_revision_preserves_old_vectors_and_switches_active_metadata(
    evidence_store: AviationEvidenceStore,
    tmp_path: Path,
) -> None:
    """Deleting a superseded vector would erase immutable publication history."""

    first = _publish_event(evidence_store, content="GDP ORIGINAL")
    encoder = RecordingEncoder()
    chroma_dir = tmp_path / "chroma"
    update_store_indexes(evidence_store, chroma_dir, encoder=encoder)

    revised = _publish_event(evidence_store, content="GDP REVISED")
    states = update_store_indexes(
        evidence_store,
        chroma_dir,
        encoder=encoder,
        source_version_ids=(revised.publication_source_version_id,),
        event_publication_ids=(revised.publication_id,),
    )

    client = open_persistent_client(chroma_dir)
    event_metadata = _metadata_by_id(
        get_collection(
            client,
            TMI_EVENT_COLLECTION,
            embedding_function=None,
        )
    )
    source_metadata = _metadata_by_id(
        get_collection(
            client,
            SOURCE_CHUNK_COLLECTION,
            embedding_function=None,
        )
    )
    event_active_by_publication = {
        metadata["publication_id"]: metadata["active"]
        for metadata in event_metadata.values()
    }
    source_active_by_version = {
        metadata["source_version_id"]: metadata["active"]
        for metadata in source_metadata.values()
    }

    assert event_active_by_publication == {
        first.publication_id: False,
        revised.publication_id: True,
    }
    assert source_active_by_version == {
        first.publication_source_version_id: False,
        revised.publication_source_version_id: True,
    }
    assert tuple(state.document_count for state in states) == (1, 1)
    assert tuple(state.vector_count for state in states) == (2, 2)
    assert sum(len(call) for call in encoder.calls) == 4

    index = ChromaTMIEventRetrievalIndex(evidence_store, chroma_dir)
    historical_vector = index.get_publication_vector(first.publication_id)
    assert len(historical_vector) == 2
    assert len(index.get_publication_vector(revised.publication_id)) == 2
    historical_event_hits = index.query_candidates(
        query_vector=historical_vector,
        candidate_publication_ids=(first.publication_id,),
        n_results=1,
    )
    assert tuple(
        hit.publication_id for hit in historical_event_hits
    ) == (first.publication_id,)
    source_index = ChromaSourceRetrievalIndex(
        evidence_store,
        chroma_dir,
        encoder,
    )
    historical_hits = source_index.query_chunks(
        query_text="original",
        candidate_source_version_ids=(
            first.publication_source_version_id,
        ),
        n_results=1,
    )
    assert tuple(hit.source_version_id for hit in historical_hits) == (
        first.publication_source_version_id,
    )


def test_full_reindex_rebuilds_all_historical_versions(
    evidence_store: AviationEvidenceStore,
    tmp_path: Path,
) -> None:
    """A full rebuild that indexes only active rows would lose history."""

    first = _publish_event(evidence_store, content="GDP ORIGINAL")
    revised = _publish_event(evidence_store, content="GDP REVISED")
    encoder = RecordingEncoder()

    states = reindex_store(
        evidence_store,
        tmp_path / "chroma",
        encoder=encoder,
    )

    assert tuple(state.document_count for state in states) == (1, 1)
    assert tuple(state.vector_count for state in states) == (2, 2)
    assert sum(len(call) for call in encoder.calls) == 4
    index = ChromaTMIEventRetrievalIndex(
        evidence_store,
        tmp_path / "chroma",
    )
    assert len(index.get_publication_vector(first.publication_id)) == 2
    assert len(index.get_publication_vector(revised.publication_id)) == 2


def test_update_failure_records_both_indexes_blocked_before_reraising(
    evidence_store: AviationEvidenceStore,
    tmp_path: Path,
) -> None:
    """A failed derived index must remain visible without changing publication."""

    event = _publish_event(evidence_store, content="GDP ORIGINAL")

    with pytest.raises(RuntimeError, match="provider unavailable"):
        update_store_indexes(
            evidence_store,
            tmp_path / "chroma",
            encoder=FailingEncoder(),
        )

    for collection_name in (
        TMI_EVENT_COLLECTION,
        SOURCE_CHUNK_COLLECTION,
    ):
        state = evidence_store.get_vector_index_state(collection_name)
        assert state is not None
        assert state.status == "blocked"
        assert state.embedding_dimension == 0
        assert state.failure_reason == "embedding provider unavailable"
    assert evidence_store.get_event(event.event_id) == event


def test_explicit_blocked_marker_supports_encoder_initialization_failure(
    evidence_store: AviationEvidenceStore,
) -> None:
    """Inventing a dimension would make pre-initialization failure misleading."""

    states = mark_vector_indexes_blocked(
        evidence_store,
        embedding_model_id="test/not-initialized",
        reason="encoder initialization failed",
    )

    assert tuple(state.embedding_dimension for state in states) == (0, 0)
    assert all(state.status == "blocked" for state in states)
    assert all(
        state.failure_reason == "encoder initialization failed"
        for state in states
    )


def test_source_only_update_does_not_require_an_accepted_event(
    evidence_store: AviationEvidenceStore,
    tmp_path: Path,
) -> None:
    """An insufficient advisory still needs exact source retrieval."""

    version = _source_version(
        "2026-05-19:999",
        "UNSUPPORTED OR INCOMPLETE ADVISORY",
    )
    evidence_store.register_source_version(version)

    states = update_store_indexes(
        evidence_store,
        tmp_path / "chroma",
        encoder=RecordingEncoder(),
        source_version_ids=(version.source_version_id,),
    )

    assert states[0].collection_name == TMI_EVENT_COLLECTION
    assert states[0].status == "blocked"
    assert states[0].document_count == 0
    assert states[1].collection_name == SOURCE_CHUNK_COLLECTION
    assert states[1].status == "current"
    assert states[1].document_count == 1
    source_collection = get_collection(
        open_persistent_client(tmp_path / "chroma"),
        SOURCE_CHUNK_COLLECTION,
        embedding_function=None,
    )
    assert source_collection.count() == 1
