"""Filtered TMI-event vector retrieval over the live evidence store."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Protocol

from aviation_agentic_ai.agent_system.contracts import (
    TMIEventSimilarityMatch,
)
from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    TMIEventQuery,
    TMIEventRecord,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
    TMIEventSimilarityQuery,
    TMIEventSimilarityResult,
    TMIEventVectorHit,
)
from aviation_agentic_ai.agent_system.tmi_profiles import active_tmi_profiles


_RETRIEVABLE_TMI_TYPES = {
    profile.ontology_class
    for profile in active_tmi_profiles()
    if profile.ontology_class is not None
}
_FILTER_PAGE_SIZE = 100


class _IndexState(Protocol):
    representation_version: str
    embedding_model_id: str


class TMIEventRetrievalIndex(Protocol):
    """Read-only publication-vector boundary used by deterministic ranking."""

    state: _IndexState

    def get_publication_vector(
        self,
        publication_id: str,
    ) -> tuple[float, ...]: ...

    def query_candidates(
        self,
        *,
        query_vector: Sequence[float],
        candidate_publication_ids: Sequence[str],
        n_results: int,
    ) -> tuple[TMIEventVectorHit, ...]: ...


def _parse_utc(value: str | datetime) -> datetime:
    parsed = (
        value
        if isinstance(value, datetime)
        else datetime.fromisoformat(value.replace("Z", "+00:00"))
    )
    return parsed.astimezone(UTC)


def _exact_candidates(
    store: AviationEvidenceStore,
    query: TMIEventSimilarityQuery,
) -> list[TMIEventRecord]:
    candidates: list[TMIEventRecord] = []
    page_offset = 0
    while True:
        page = store.find_tmi_events(
            TMIEventQuery(
                event_type_iri=query.event_type_iri,
                facility_id=query.facility_id,
                reason_status=query.reason_status,
                reason_value=query.reason_value,
                offset=page_offset,
                limit=_FILTER_PAGE_SIZE,
            )
        )
        candidates.extend(page.events)
        page_offset += len(page.events)
        if page_offset >= page.total_matches or not page.events:
            return candidates


def _tmi_type(event: TMIEventRecord) -> str:
    reviewed = sorted(
        iri
        for iri in event.event_type_iris
        if iri in _RETRIEVABLE_TMI_TYPES
    )
    if len(reviewed) != 1:
        raise ValueError(
            f"event has no single retrievable TMI type: {event.event_id}"
        )
    return reviewed[0]


def rank_tmi_events_by_metadata(
    store: AviationEvidenceStore,
    index: TMIEventRetrievalIndex,
    query: TMIEventSimilarityQuery,
) -> TMIEventSimilarityResult:
    """Rank TMI events with exact filters and metadata-conditioned recall."""

    anchor = store.get_event(query.reference_event_id)
    if anchor is None:
        return TMIEventSimilarityResult(
            status="insufficient",
            query=query,
            candidate_count=0,
            representation_version=index.state.representation_version,
            embedding_model_id=index.state.embedding_model_id,
            limitation=(
                "The reference event is not present in this evidence store."
            ),
        )

    candidates = [
        event
        for event in _exact_candidates(store, query)
        if event.event_id != anchor.event_id
    ]
    if query.candidate_scope == "prior":
        if anchor.effective_start is None:
            return TMIEventSimilarityResult(
                status="blocked",
                query=query,
                candidate_count=0,
                representation_version=index.state.representation_version,
                embedding_model_id=index.state.embedding_model_id,
                limitation=(
                    "The reference event has no effective start boundary."
                ),
            )
        anchor_start = _parse_utc(anchor.effective_start)
        candidates = [
            event
            for event in candidates
            if event.effective_end is not None
            and _parse_utc(event.effective_end) < anchor_start
        ]
    candidates.sort(key=lambda event: event.event_id)
    if not candidates:
        return TMIEventSimilarityResult(
            status="insufficient",
            query=query,
            candidate_count=0,
            representation_version=index.state.representation_version,
            embedding_model_id=index.state.embedding_model_id,
            limitation=(
                "No historical TMI events match the exact candidate filters."
            ),
        )

    try:
        reference_vector = index.get_publication_vector(
            anchor.publication_id
        )
        hits = index.query_candidates(
            query_vector=reference_vector,
            candidate_publication_ids=[
                event.publication_id for event in candidates
            ],
            n_results=min(len(candidates), query.offset + query.limit),
        )
    except ValueError as exc:
        return TMIEventSimilarityResult(
            status="blocked",
            query=query,
            candidate_count=len(candidates),
            representation_version=index.state.representation_version,
            embedding_model_id=index.state.embedding_model_id,
            limitation=str(exc),
        )

    candidate_by_publication = {
        event.publication_id: event for event in candidates
    }
    ranked_hits = sorted(
        hits,
        key=lambda hit: (-hit.similarity, hit.event_id),
    )
    selected_hits = ranked_hits[query.offset : query.offset + query.limit]
    try:
        matches: list[TMIEventSimilarityMatch] = []
        for position, hit in enumerate(selected_hits, start=1):
            candidate = candidate_by_publication[hit.publication_id]
            if candidate.event_id != hit.event_id:
                raise ValueError(
                    "vector hit does not match its event publication"
                )
            matches.append(
                TMIEventSimilarityMatch(
                    rank=query.offset + position,
                    event_id=candidate.event_id,
                    advisory_source_id=candidate.advisory_source_id,
                    score=round(hit.similarity, 6),
                    tmi_type_iri=_tmi_type(candidate),
                    facility_ids=tuple(sorted(candidate.facility_ids)),
                    reason_status=candidate.reason_status,
                    reason_value=candidate.reason_value,
                )
            )
    except (KeyError, ValueError) as exc:
        return TMIEventSimilarityResult(
            status="blocked",
            query=query,
            candidate_count=len(candidates),
            representation_version=index.state.representation_version,
            embedding_model_id=index.state.embedding_model_id,
            limitation=str(exc),
        )
    return TMIEventSimilarityResult(
        status="ok" if matches else "insufficient",
        query=query,
        candidate_count=len(candidates),
        representation_version=index.state.representation_version,
        embedding_model_id=index.state.embedding_model_id,
        matches=tuple(matches),
        limitation=(
            ""
            if matches
            else "No ranked TMI events are available on the requested page."
        ),
    )
