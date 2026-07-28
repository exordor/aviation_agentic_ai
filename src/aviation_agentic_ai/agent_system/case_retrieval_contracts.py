"""Typed contracts for deterministic historical case retrieval."""

from __future__ import annotations

from typing import Literal, Protocol, Sequence

from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import StrictModel


REPRESENTATION_VERSION = "decision-record-v1"
DEFAULT_CASE_EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

DurationBucket = Literal[
    "under_1_hour",
    "1_to_2_hours",
    "2_to_4_hours",
    "4_to_8_hours",
    "8_hours_or_more",
]


class CaseRetrievalDocument(StrictModel):
    """One deterministic decision-record document prepared for embedding."""

    document_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    advisory_source_id: str = Field(min_length=1)
    representation_version: Literal["decision-record-v1"] = (
        REPRESENTATION_VERSION
    )
    text: str = Field(min_length=1)
    tmi_type_iri: str = Field(min_length=1)
    facility_ids: tuple[str, ...]
    reason_status: Literal["formal", "profile_gap", "missing"]
    reason_value: str | None
    duration_bucket: DurationBucket
    operational_start: str = Field(min_length=1)
    operational_end: str = Field(min_length=1)


class CaseEncoder(Protocol):
    """Embedding boundary used by the rebuildable case index."""

    model_id: str

    def encode(
        self,
        texts: Sequence[str],
    ) -> Sequence[Sequence[float]]: ...


class CaseDocumentArtifact(StrictModel):
    """Registered canonical-document file used to build the index."""

    path: str = Field(min_length=1)
    count: int = Field(ge=0)
    sha256: str = Field(min_length=64, max_length=64)


class CaseIndexManifest(StrictModel):
    """Corpus-bound metadata for one persistent case-vector index."""

    manifest_version: Literal["decision-case-index-v1"] = (
        "decision-case-index-v1"
    )
    corpus_id: str = Field(min_length=1)
    representation_version: Literal["decision-record-v1"] = (
        REPRESENTATION_VERSION
    )
    vector_backend: Literal["chromadb"] = "chromadb"
    collection_name: str = Field(min_length=1)
    distance_metric: Literal["cosine"] = "cosine"
    embedding_model_id: str = Field(min_length=1)
    embedding_dimension: int = Field(ge=1)
    document_count: int = Field(ge=0)
    vector_count: int = Field(ge=0)
    case_documents: CaseDocumentArtifact


class CaseVectorHit(StrictModel):
    """One Chroma result retaining distance and cosine similarity."""

    case_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    advisory_source_id: str = Field(min_length=1)
    distance: float
    similarity: float
