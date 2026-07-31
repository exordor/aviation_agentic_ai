"""Typed contracts for deterministic historical TMI-event retrieval."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Protocol, Sequence

from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import (
    StrictModel,
    TMIEventSimilarityMatch,
)


REPRESENTATION_VERSION = "tmi-event-record-v1"
DEFAULT_TMI_EVENT_EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

DurationBucket = Literal[
    "under_1_hour",
    "1_to_2_hours",
    "2_to_4_hours",
    "4_to_8_hours",
    "8_hours_or_more",
]


class TMIEventRetrievalDocument(StrictModel):
    """One immutable event-publication document prepared for embedding."""

    document_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    advisory_source_id: str = Field(min_length=1)
    publication_source_version_id: str = Field(min_length=1)
    source_version_ids: tuple[str, ...]
    fact_ids: tuple[str, ...]
    representation_version: Literal["tmi-event-record-v1"] = (
        REPRESENTATION_VERSION
    )
    text: str = Field(min_length=1)
    tmi_type_iri: str = Field(min_length=1)
    facility_ids: tuple[str, ...]
    reason_status: Literal["formal", "profile_gap", "missing"]
    reason_value: str | None
    duration_bucket: DurationBucket
    effective_start: datetime
    effective_end: datetime


class TMIEventEncoder(Protocol):
    """Embedding boundary used by the rebuildable TMI-event index."""

    model_id: str

    def encode(
        self,
        texts: Sequence[str],
    ) -> Sequence[Sequence[float]]: ...


class TMIEventVectorHit(StrictModel):
    """One Chroma result retaining distance and cosine similarity."""

    event_id: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    advisory_source_id: str = Field(min_length=1)
    distance: float
    similarity: float


class TMIEventSimilarityQuery(StrictModel):
    """Exact candidate scope and ranked-page request for one anchor event."""

    reference_event_id: str = Field(min_length=1)
    candidate_scope: Literal["archive", "prior"] = "archive"
    event_type_iri: str | None = Field(default=None, min_length=1)
    facility_id: str | None = Field(default=None, min_length=1)
    reason_status: Literal["formal", "profile_gap", "missing"] | None = None
    reason_value: str | None = Field(default=None, min_length=1)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class TMIEventSimilarityResult(StrictModel):
    """Ranked derived retrieval records or one bounded limitation."""

    status: Literal["ok", "insufficient", "blocked"]
    query: TMIEventSimilarityQuery
    candidate_count: int = Field(ge=0)
    representation_version: str = Field(min_length=1)
    embedding_model_id: str = Field(min_length=1)
    matches: tuple[TMIEventSimilarityMatch, ...] = ()
    limitation: str = ""
