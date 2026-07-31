"""Frozen store and vector-index bindings for model-dependent evaluation."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import Field, model_validator

from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
    SCHEMA_VERSION,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_index import (
    ChromaSourceRetrievalIndex,
    ChromaTMIEventRetrievalIndex,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    SourceVersionRecord,
)


class EvaluationBindingBlocked(RuntimeError):
    """A frozen evaluation universe could not be established or retained."""

    def __init__(
        self,
        detail_code: str,
        *,
        runner_status: Literal[
            "blocked_before_run",
            "invalidated_after_run",
        ] = "blocked_before_run",
    ) -> None:
        super().__init__(detail_code)
        self.detail_code = detail_code
        self.runner_status = runner_status


class EvaluationVectorBinding(StrictModel):
    """Exact metadata and candidate documents for one Chroma collection."""

    collection_name: str = Field(min_length=1)
    representation_version: str = Field(min_length=1)
    embedding_model_id: str = Field(min_length=1)
    embedding_dimension: int = Field(ge=1)
    indexed_knowledge_revision: int = Field(ge=0)
    document_ids: tuple[str, ...]

    @model_validator(mode="after")
    def _require_stable_document_order(self) -> EvaluationVectorBinding:
        if self.document_ids != tuple(sorted(set(self.document_ids))):
            raise ValueError(
                "evaluation vector document IDs must be sorted and unique"
            )
        return self


class EvaluationDataBinding(StrictModel):
    """Frozen evidence-store and retrieval universe for one evaluation."""

    store_schema_version: str = Field(min_length=1)
    dataset_id: str = Field(min_length=1)
    knowledge_revision: int = Field(ge=0)
    required_source_versions: dict[str, str]
    required_source_hashes: dict[str, str]
    required_event_publication_ids: tuple[str, ...]
    source_candidate_version_ids: tuple[str, ...]
    event_candidate_publication_ids: tuple[str, ...]
    source_vector_index: EvaluationVectorBinding
    event_vector_index: EvaluationVectorBinding
    validation_profile_checksums: tuple[str, ...]

    @model_validator(mode="after")
    def _validate_exact_sets(self) -> EvaluationDataBinding:
        ordered_fields = (
            self.required_event_publication_ids,
            self.source_candidate_version_ids,
            self.event_candidate_publication_ids,
            self.validation_profile_checksums,
        )
        if any(values != tuple(sorted(set(values))) for values in ordered_fields):
            raise ValueError("evaluation binding tuples must be sorted and unique")
        if set(self.required_source_hashes) != set(
            self.required_source_versions.values()
        ):
            raise ValueError(
                "required source hashes must cover exact required versions"
            )
        if any(
            len(checksum) != 64
            for checksum in (
                *self.required_source_hashes.values(),
                *self.validation_profile_checksums,
            )
        ):
            raise ValueError("evaluation checksums must be SHA-256 hex values")
        return self


def _blocked(detail_code: str) -> EvaluationBindingBlocked:
    return EvaluationBindingBlocked(detail_code)


def _require_source_versions(
    store: AviationEvidenceStore,
    source_version_ids: Sequence[str],
    *,
    kind: Literal["required", "candidate"],
) -> tuple[SourceVersionRecord, ...]:
    records = []
    for source_version_id in sorted(set(source_version_ids)):
        record = store.get_source_version(source_version_id)
        if record is None:
            raise _blocked(f"missing_{kind}_source_version")
        records.append(record)
    return tuple(records)


def _publication_ids(store: AviationEvidenceStore) -> set[str]:
    return {
        event.publication_id
        for event in store.list_tmi_event_publications()
    }


def _require_publications(
    store: AviationEvidenceStore,
    publication_ids: Sequence[str],
    *,
    kind: Literal["required", "candidate"],
) -> None:
    known = _publication_ids(store)
    if set(publication_ids) - known:
        raise _blocked(f"missing_{kind}_event_publication")


def _verify_collection_metadata(
    *,
    store: AviationEvidenceStore,
    index: ChromaSourceRetrievalIndex | ChromaTMIEventRetrievalIndex,
    binding: EvaluationVectorBinding | None = None,
) -> None:
    state = index.state
    metadata = index.collection.metadata or {}
    expected_metadata = {
        "dataset_id": store.dataset_id,
        "evidence_store_schema_version": SCHEMA_VERSION,
        "representation_version": state.representation_version,
        "embedding_model_id": state.embedding_model_id,
        "embedding_dimension": state.embedding_dimension,
        "distance_metric": "cosine",
    }
    if any(
        metadata.get(key) != value
        for key, value in expected_metadata.items()
    ):
        raise _blocked(f"{state.collection_name}_metadata_mismatch")
    if state.indexed_knowledge_revision != store.get_knowledge_revision():
        raise _blocked(f"{state.collection_name}_revision_mismatch")
    if index.store.dataset_id != store.dataset_id:
        raise _blocked(f"{state.collection_name}_store_mismatch")
    if binding is not None:
        observed = EvaluationVectorBinding(
            collection_name=state.collection_name,
            representation_version=state.representation_version,
            embedding_model_id=state.embedding_model_id,
            embedding_dimension=state.embedding_dimension,
            indexed_knowledge_revision=state.indexed_knowledge_revision,
            document_ids=binding.document_ids,
        )
        if observed != binding:
            raise _blocked(f"{state.collection_name}_state_changed")


def _candidate_document_ids(
    index: ChromaSourceRetrievalIndex | ChromaTMIEventRetrievalIndex,
    *,
    metadata_field: Literal["source_version_id", "publication_id"],
    candidate_ids: Sequence[str],
    mismatch_code: str,
) -> tuple[str, ...]:
    candidates = tuple(sorted(set(candidate_ids)))
    if not candidates:
        return ()
    payload = index.collection.get(
        where={metadata_field: {"$in": list(candidates)}},
        include=["metadatas"],
    )
    document_ids = tuple(sorted(payload.get("ids") or ()))
    metadatas = payload.get("metadatas") or ()
    observed_candidates = {
        str(metadata[metadata_field])
        for metadata in metadatas
        if metadata is not None and metadata_field in metadata
    }
    if observed_candidates != set(candidates) or not document_ids:
        raise _blocked(mismatch_code)
    if (
        metadata_field == "publication_id"
        and len(document_ids) != len(candidates)
    ):
        raise _blocked(mismatch_code)
    return document_ids


def _capture_vector_binding(
    *,
    store: AviationEvidenceStore,
    index: ChromaSourceRetrievalIndex | ChromaTMIEventRetrievalIndex,
    metadata_field: Literal["source_version_id", "publication_id"],
    candidate_ids: Sequence[str],
    mismatch_code: str,
) -> EvaluationVectorBinding:
    _verify_collection_metadata(store=store, index=index)
    state = index.state
    return EvaluationVectorBinding(
        collection_name=state.collection_name,
        representation_version=state.representation_version,
        embedding_model_id=state.embedding_model_id,
        embedding_dimension=state.embedding_dimension,
        indexed_knowledge_revision=state.indexed_knowledge_revision,
        document_ids=_candidate_document_ids(
            index,
            metadata_field=metadata_field,
            candidate_ids=candidate_ids,
            mismatch_code=mismatch_code,
        ),
    )


def bind_evaluation_data(
    store: AviationEvidenceStore,
    *,
    source_index: ChromaSourceRetrievalIndex | None,
    event_index: ChromaTMIEventRetrievalIndex | None,
    required_source_version_ids: Sequence[str],
    required_event_publication_ids: Sequence[str],
    source_candidate_version_ids: Sequence[str],
    event_candidate_publication_ids: Sequence[str],
    validation_profile_checksums: Sequence[str],
) -> EvaluationDataBinding:
    """Validate and freeze the exact retrieval universe before model calls."""

    if source_index is None:
        raise _blocked("missing_source_vector_index")
    if event_index is None:
        raise _blocked("missing_event_vector_index")
    required_sources = _require_source_versions(
        store,
        required_source_version_ids,
        kind="required",
    )
    candidate_source_ids = tuple(sorted(set(source_candidate_version_ids)))
    _require_source_versions(
        store,
        candidate_source_ids,
        kind="candidate",
    )
    required_publication_ids = tuple(
        sorted(set(required_event_publication_ids))
    )
    candidate_publication_ids = tuple(
        sorted(set(event_candidate_publication_ids))
    )
    _require_publications(
        store,
        required_publication_ids,
        kind="required",
    )
    _require_publications(
        store,
        candidate_publication_ids,
        kind="candidate",
    )
    required_by_source = {
        record.source_id: record.source_version_id
        for record in required_sources
    }
    if len(required_by_source) != len(required_sources):
        raise _blocked("multiple_required_versions_for_source")
    binding = EvaluationDataBinding(
        store_schema_version=SCHEMA_VERSION,
        dataset_id=store.dataset_id,
        knowledge_revision=store.get_knowledge_revision(),
        required_source_versions=dict(sorted(required_by_source.items())),
        required_source_hashes={
            record.source_version_id: record.content_sha256
            for record in required_sources
        },
        required_event_publication_ids=required_publication_ids,
        source_candidate_version_ids=candidate_source_ids,
        event_candidate_publication_ids=candidate_publication_ids,
        source_vector_index=_capture_vector_binding(
            store=store,
            index=source_index,
            metadata_field="source_version_id",
            candidate_ids=candidate_source_ids,
            mismatch_code="source_candidate_documents_changed",
        ),
        event_vector_index=_capture_vector_binding(
            store=store,
            index=event_index,
            metadata_field="publication_id",
            candidate_ids=candidate_publication_ids,
            mismatch_code="event_candidate_documents_changed",
        ),
        validation_profile_checksums=tuple(
            sorted(set(validation_profile_checksums))
        ),
    )
    verify_evaluation_data_binding(
        binding,
        store,
        source_index=source_index,
        event_index=event_index,
        validation_profile_checksums=validation_profile_checksums,
    )
    return binding


def verify_evaluation_data_binding(
    binding: EvaluationDataBinding,
    store: AviationEvidenceStore,
    *,
    source_index: ChromaSourceRetrievalIndex | None,
    event_index: ChromaTMIEventRetrievalIndex | None,
    validation_profile_checksums: Sequence[str],
) -> None:
    """Revalidate one captured binding before the first provider call."""

    if source_index is None:
        raise _blocked("missing_source_vector_index")
    if event_index is None:
        raise _blocked("missing_event_vector_index")
    if binding.store_schema_version != SCHEMA_VERSION:
        raise _blocked("store_schema_version_changed")
    if binding.dataset_id != store.dataset_id:
        raise _blocked("dataset_id_changed")
    if binding.knowledge_revision != store.get_knowledge_revision():
        raise _blocked("knowledge_revision_changed")
    expected_profiles = tuple(sorted(set(validation_profile_checksums)))
    if binding.validation_profile_checksums != expected_profiles:
        raise _blocked("validation_profile_checksums_changed")

    required_records = _require_source_versions(
        store,
        tuple(binding.required_source_versions.values()),
        kind="required",
    )
    observed_required_versions = {
        record.source_id: record.source_version_id
        for record in required_records
    }
    if observed_required_versions != binding.required_source_versions:
        raise _blocked("required_source_version_changed")
    observed_hashes = {
        record.source_version_id: record.content_sha256
        for record in required_records
    }
    if observed_hashes != binding.required_source_hashes:
        raise _blocked("required_source_hash_changed")

    _require_publications(
        store,
        binding.required_event_publication_ids,
        kind="required",
    )
    _require_source_versions(
        store,
        binding.source_candidate_version_ids,
        kind="candidate",
    )
    _require_publications(
        store,
        binding.event_candidate_publication_ids,
        kind="candidate",
    )

    _verify_collection_metadata(
        store=store,
        index=source_index,
        binding=binding.source_vector_index,
    )
    source_document_ids = _candidate_document_ids(
        source_index,
        metadata_field="source_version_id",
        candidate_ids=binding.source_candidate_version_ids,
        mismatch_code="source_candidate_documents_changed",
    )
    if source_document_ids != binding.source_vector_index.document_ids:
        raise _blocked("source_candidate_documents_changed")

    _verify_collection_metadata(
        store=store,
        index=event_index,
        binding=binding.event_vector_index,
    )
    event_document_ids = _candidate_document_ids(
        event_index,
        metadata_field="publication_id",
        candidate_ids=binding.event_candidate_publication_ids,
        mismatch_code="event_candidate_documents_changed",
    )
    if event_document_ids != binding.event_vector_index.document_ids:
        raise _blocked("event_candidate_documents_changed")


def verify_evaluation_revision_unchanged(
    binding: EvaluationDataBinding,
    store: AviationEvidenceStore,
) -> None:
    """Invalidate post-call metrics if the authoritative store changed."""

    if binding.knowledge_revision != store.get_knowledge_revision():
        raise EvaluationBindingBlocked(
            "knowledge_revision_changed",
            runner_status="invalidated_after_run",
        )


__all__ = [
    "EvaluationBindingBlocked",
    "EvaluationDataBinding",
    "EvaluationVectorBinding",
    "bind_evaluation_data",
    "verify_evaluation_data_binding",
    "verify_evaluation_revision_unchanged",
]
