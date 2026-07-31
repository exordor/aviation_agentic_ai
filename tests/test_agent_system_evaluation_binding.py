"""Exact data/index bindings for live evaluation."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Sequence

import pytest

from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.agent_system.evaluation_binding import (
    EvaluationBindingBlocked,
    bind_evaluation_data,
    verify_evaluation_data_binding,
    verify_evaluation_revision_unchanged,
)
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
    ChromaSourceRetrievalIndex,
    ChromaTMIEventRetrievalIndex,
    update_store_indexes,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id


ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
PROFILE_CHECKSUM = "a" * 64


class TwoDimensionalEncoder:
    model_id = "test/evaluation-binding"

    def encode(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        return [
            [float(index + 1), 1.0]
            for index, _text in enumerate(texts)
        ]


def _source_version(source_id: str, content: str) -> SourceVersionRecord:
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
    source_id: str,
    event_id: str,
    content: str,
) -> tuple[SourceVersionRecord, TMIEventRecord]:
    version = _source_version(source_id, content)
    store.register_source_version(version)
    publication_digest = hashlib.sha256(
        f"publication:{content}".encode("utf-8")
    ).hexdigest()
    publication_id = stable_id(
        "event-publication",
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
        facility_ids=("urn:facility:KJFK",),
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
    return version, event


@pytest.fixture
def indexed_evaluation_store(tmp_path: Path):
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:evaluation-binding",
        create=True,
    )
    version, event = _publish_event(
        store,
        source_id="2026-05-19:138",
        event_id="urn:event:gdp:138",
        content="GDP AT KJFK DUE TO WEATHER",
    )
    encoder = TwoDimensionalEncoder()
    chroma_dir = tmp_path / "chroma"
    update_store_indexes(
        store,
        chroma_dir,
        encoder=encoder,
    )
    source_index = ChromaSourceRetrievalIndex(
        store,
        chroma_dir,
        encoder,
    )
    event_index = ChromaTMIEventRetrievalIndex(store, chroma_dir)
    try:
        yield store, source_index, event_index, version, event
    finally:
        store.close()


def test_binding_captures_and_verifies_the_exact_retrieval_universe(
    indexed_evaluation_store,
) -> None:
    """Dropping IDs, hashes, or vector documents must invalidate a run."""

    store, source_index, event_index, version, event = (
        indexed_evaluation_store
    )

    binding = bind_evaluation_data(
        store,
        source_index=source_index,
        event_index=event_index,
        required_source_version_ids=(version.source_version_id,),
        required_event_publication_ids=(event.publication_id,),
        source_candidate_version_ids=(version.source_version_id,),
        event_candidate_publication_ids=(event.publication_id,),
        validation_profile_checksums=(PROFILE_CHECKSUM,),
    )

    assert binding.store_schema_version == SCHEMA_VERSION
    assert binding.dataset_id == "dataset:evaluation-binding"
    assert binding.knowledge_revision == 2
    assert binding.required_source_versions == {
        version.source_id: version.source_version_id,
    }
    assert binding.required_source_hashes == {
        version.source_version_id: version.content_sha256,
    }
    assert binding.required_event_publication_ids == (
        event.publication_id,
    )
    assert binding.source_candidate_version_ids == (
        version.source_version_id,
    )
    assert binding.event_candidate_publication_ids == (
        event.publication_id,
    )
    assert len(binding.source_vector_index.document_ids) == 1
    assert len(binding.event_vector_index.document_ids) == 1
    assert binding.validation_profile_checksums == (PROFILE_CHECKSUM,)

    verify_evaluation_data_binding(
        binding,
        store,
        source_index=source_index,
        event_index=event_index,
        validation_profile_checksums=(PROFILE_CHECKSUM,),
    )


def test_missing_required_source_blocks_before_provider_execution(
    indexed_evaluation_store,
) -> None:
    """A missing frozen source must not silently shrink the evaluation."""

    store, source_index, event_index, _version, event = (
        indexed_evaluation_store
    )

    with pytest.raises(EvaluationBindingBlocked) as caught:
        bind_evaluation_data(
            store,
            source_index=source_index,
            event_index=event_index,
            required_source_version_ids=("missing-source-version",),
            required_event_publication_ids=(event.publication_id,),
            source_candidate_version_ids=(),
            event_candidate_publication_ids=(event.publication_id,),
            validation_profile_checksums=(PROFILE_CHECKSUM,),
        )

    assert caught.value.runner_status == "blocked_before_run"
    assert caught.value.detail_code == "missing_required_source_version"


def test_missing_vector_index_blocks_before_provider_execution(
    indexed_evaluation_store,
) -> None:
    """An optional runtime index cannot be silently omitted in evaluation."""

    store, _source_index, event_index, version, event = (
        indexed_evaluation_store
    )

    with pytest.raises(EvaluationBindingBlocked) as caught:
        bind_evaluation_data(
            store,
            source_index=None,
            event_index=event_index,
            required_source_version_ids=(version.source_version_id,),
            required_event_publication_ids=(event.publication_id,),
            source_candidate_version_ids=(version.source_version_id,),
            event_candidate_publication_ids=(event.publication_id,),
            validation_profile_checksums=(PROFILE_CHECKSUM,),
        )

    assert caught.value.runner_status == "blocked_before_run"
    assert caught.value.detail_code == "missing_source_vector_index"


def test_candidate_document_change_blocks_before_provider_execution(
    indexed_evaluation_store,
) -> None:
    """A Chroma candidate mismatch must not be accepted as the frozen index."""

    store, source_index, event_index, version, event = (
        indexed_evaluation_store
    )
    binding = bind_evaluation_data(
        store,
        source_index=source_index,
        event_index=event_index,
        required_source_version_ids=(version.source_version_id,),
        required_event_publication_ids=(event.publication_id,),
        source_candidate_version_ids=(version.source_version_id,),
        event_candidate_publication_ids=(event.publication_id,),
        validation_profile_checksums=(PROFILE_CHECKSUM,),
    )
    source_index.collection.delete(
        ids=list(binding.source_vector_index.document_ids),
    )

    with pytest.raises(EvaluationBindingBlocked) as caught:
        verify_evaluation_data_binding(
            binding,
            store,
            source_index=source_index,
            event_index=event_index,
            validation_profile_checksums=(PROFILE_CHECKSUM,),
        )

    assert caught.value.runner_status == "blocked_before_run"
    assert caught.value.detail_code == "source_candidate_documents_changed"


def test_revision_change_after_model_calls_invalidates_metrics(
    indexed_evaluation_store,
) -> None:
    """Metrics must not mix pre-call retrieval with a later store revision."""

    store, source_index, event_index, version, event = (
        indexed_evaluation_store
    )
    binding = bind_evaluation_data(
        store,
        source_index=source_index,
        event_index=event_index,
        required_source_version_ids=(version.source_version_id,),
        required_event_publication_ids=(event.publication_id,),
        source_candidate_version_ids=(version.source_version_id,),
        event_candidate_publication_ids=(event.publication_id,),
        validation_profile_checksums=(PROFILE_CHECKSUM,),
    )
    _publish_event(
        store,
        source_id="2026-05-19:139",
        event_id="urn:event:gdp:139",
        content="SECOND GDP AT KJFK",
    )

    with pytest.raises(EvaluationBindingBlocked) as caught:
        verify_evaluation_revision_unchanged(binding, store)

    assert caught.value.runner_status == "invalidated_after_run"
    assert caught.value.detail_code == "knowledge_revision_changed"
