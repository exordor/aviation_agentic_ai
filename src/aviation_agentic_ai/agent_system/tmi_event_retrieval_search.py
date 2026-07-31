"""Filtered TMI-event vector retrieval over a verified corpus."""

from __future__ import annotations

from datetime import UTC, datetime

from aviation_agentic_ai.agent_system.contracts import (
    TMIEventSimilarityMatch,
)
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusEventQuery,
    CorpusQueryStore,
    CorpusTMIEvent,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
    TMIEventSimilarityQuery,
    TMIEventSimilarityResult,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_index import (
    ChromaTMIEventRetrievalIndex,
)
from aviation_agentic_ai.agent_system.tmi_profiles import active_tmi_profiles


_RETRIEVABLE_TMI_TYPES = {
    profile.ontology_class
    for profile in active_tmi_profiles()
    if profile.ontology_class is not None
}
_FILTER_PAGE_SIZE = 100


def _parse_utc(value: str | datetime) -> datetime:
    parsed = (
        value
        if isinstance(value, datetime)
        else datetime.fromisoformat(value.replace("Z", "+00:00"))
    )
    return parsed.astimezone(UTC)


def _exact_candidates(
    store: CorpusQueryStore,
    query: TMIEventSimilarityQuery,
) -> list[CorpusTMIEvent]:
    candidates: list[CorpusTMIEvent] = []
    page_offset = 0
    while True:
        page = store.find_events(
            CorpusEventQuery(
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


def _tmi_type(event: CorpusTMIEvent) -> str:
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


def find_similar_tmi_events(
    store: CorpusQueryStore,
    index: ChromaTMIEventRetrievalIndex,
    query: TMIEventSimilarityQuery,
) -> TMIEventSimilarityResult:
    """Apply exact corpus filters before Chroma cosine recall."""

    anchor = store.get_event(query.reference_event_id)
    if anchor is None:
        return TMIEventSimilarityResult(
            status="insufficient",
            query=query,
            candidate_count=0,
            representation_version=index.manifest.representation_version,
            embedding_model_id=index.manifest.embedding_model_id,
            limitation="The reference event is not present in this corpus.",
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
                representation_version=index.manifest.representation_version,
                embedding_model_id=index.manifest.embedding_model_id,
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
            representation_version=index.manifest.representation_version,
            embedding_model_id=index.manifest.embedding_model_id,
            limitation=(
                "No historical TMI events match the exact candidate filters."
            ),
        )

    try:
        reference_vector = index.get_event_vector(anchor.event_id)
        hits = index.query_candidates(
            query_vector=reference_vector,
            candidate_event_ids=[event.event_id for event in candidates],
            n_results=min(len(candidates), query.offset + query.limit),
        )
    except ValueError as exc:
        return TMIEventSimilarityResult(
            status="blocked",
            query=query,
            candidate_count=len(candidates),
            representation_version=index.manifest.representation_version,
            embedding_model_id=index.manifest.embedding_model_id,
            limitation=str(exc),
        )

    candidate_by_id = {event.event_id: event for event in candidates}
    ranked_hits = sorted(
        hits,
        key=lambda hit: (-hit.similarity, hit.event_id),
    )
    selected_hits = ranked_hits[query.offset : query.offset + query.limit]
    try:
        matches = tuple(
            TMIEventSimilarityMatch(
                rank=query.offset + position,
                event_id=hit.event_id,
                advisory_source_id=(
                    candidate_by_id[hit.event_id].advisory_source_id
                ),
                score=round(hit.similarity, 6),
                tmi_type_iri=_tmi_type(candidate_by_id[hit.event_id]),
                facility_ids=tuple(
                    sorted(candidate_by_id[hit.event_id].facility_ids)
                ),
                reason_status=candidate_by_id[hit.event_id].reason_status,
                reason_value=candidate_by_id[hit.event_id].reason_value,
            )
            for position, hit in enumerate(selected_hits, start=1)
        )
    except (KeyError, ValueError) as exc:
        return TMIEventSimilarityResult(
            status="blocked",
            query=query,
            candidate_count=len(candidates),
            representation_version=index.manifest.representation_version,
            embedding_model_id=index.manifest.embedding_model_id,
            limitation=str(exc),
        )
    return TMIEventSimilarityResult(
        status="ok" if matches else "insufficient",
        query=query,
        candidate_count=len(candidates),
        representation_version=index.manifest.representation_version,
        embedding_model_id=index.manifest.embedding_model_id,
        matches=matches,
        limitation=(
            ""
            if matches
            else "No ranked TMI events are available on the requested page."
        ),
    )
