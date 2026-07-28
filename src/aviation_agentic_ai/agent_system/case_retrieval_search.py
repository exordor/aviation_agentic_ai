"""Filtered case-level vector retrieval over a verified corpus."""

from __future__ import annotations

from datetime import UTC, datetime

from aviation_agentic_ai.agent_system.case_retrieval_contracts import (
    CaseSimilarityQuery,
    CaseSimilarityResult,
)
from aviation_agentic_ai.agent_system.case_retrieval_index import (
    ChromaCaseRetrievalIndex,
)
from aviation_agentic_ai.agent_system.contracts import CaseSimilarityMatch
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusCase,
    CorpusCaseQuery,
    CorpusQueryStore,
)


_ATM_NAMESPACE = "https://data.nasa.gov/ontologies/atmonto/ATM#"
_RETRIEVABLE_TMI_TYPES = {
    f"{_ATM_NAMESPACE}GroundDelayProgramTMI",
    f"{_ATM_NAMESPACE}GroundStopTMI",
}
_FILTER_PAGE_SIZE = 100


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    ).astimezone(UTC)


def _exact_candidates(
    store: CorpusQueryStore,
    query: CaseSimilarityQuery,
) -> list[CorpusCase]:
    candidates: list[CorpusCase] = []
    page_offset = 0
    while True:
        page = store.find_cases(
            CorpusCaseQuery(
                event_type_iri=query.event_type_iri,
                facility_id=query.facility_id,
                reason_status=query.reason_status,
                reason_value=query.reason_value,
                offset=page_offset,
                limit=_FILTER_PAGE_SIZE,
            )
        )
        candidates.extend(page.cases)
        page_offset += len(page.cases)
        if page_offset >= page.total_matches or not page.cases:
            return candidates


def _tmi_type(case: CorpusCase) -> str:
    reviewed = sorted(
        iri
        for iri in case.event_type_iris
        if iri in _RETRIEVABLE_TMI_TYPES
    )
    if len(reviewed) != 1:
        raise ValueError(
            f"case has no single retrievable TMI type: {case.case_id}"
        )
    return reviewed[0]


def find_similar_cases(
    store: CorpusQueryStore,
    index: ChromaCaseRetrievalIndex,
    query: CaseSimilarityQuery,
) -> CaseSimilarityResult:
    """Apply exact corpus filters before Chroma cosine recall."""

    anchor = store.get_case(query.reference_event_id)
    if anchor is None:
        return CaseSimilarityResult(
            status="insufficient",
            query=query,
            candidate_count=0,
            representation_version=index.manifest.representation_version,
            embedding_model_id=index.manifest.embedding_model_id,
            limitation="The reference event is not present in this corpus.",
        )

    candidates = [
        case
        for case in _exact_candidates(store, query)
        if case.case_id != anchor.case_id
    ]
    if query.candidate_scope == "prior":
        if anchor.operational_start is None:
            return CaseSimilarityResult(
                status="blocked",
                query=query,
                candidate_count=0,
                representation_version=(
                    index.manifest.representation_version
                ),
                embedding_model_id=index.manifest.embedding_model_id,
                limitation=(
                    "The reference case has no operational start boundary."
                ),
            )
        anchor_start = _parse_utc(anchor.operational_start)
        candidates = [
            case
            for case in candidates
            if case.operational_end is not None
            and _parse_utc(case.operational_end) < anchor_start
        ]
    candidates.sort(key=lambda case: case.case_id)
    if not candidates:
        return CaseSimilarityResult(
            status="insufficient",
            query=query,
            candidate_count=0,
            representation_version=index.manifest.representation_version,
            embedding_model_id=index.manifest.embedding_model_id,
            limitation=(
                "No historical cases match the exact candidate filters."
            ),
        )

    try:
        reference_vector = index.get_case_vector(anchor.case_id)
        hits = index.query_candidates(
            query_vector=reference_vector,
            candidate_case_ids=[
                case.case_id for case in candidates
            ],
            n_results=min(
                len(candidates),
                query.offset + query.limit,
            ),
        )
    except ValueError as exc:
        return CaseSimilarityResult(
            status="blocked",
            query=query,
            candidate_count=len(candidates),
            representation_version=index.manifest.representation_version,
            embedding_model_id=index.manifest.embedding_model_id,
            limitation=str(exc),
        )

    candidate_by_id = {case.case_id: case for case in candidates}
    ranked_hits = sorted(
        hits,
        key=lambda hit: (-hit.similarity, hit.case_id),
    )
    selected_hits = ranked_hits[
        query.offset : query.offset + query.limit
    ]
    try:
        matches = tuple(
            CaseSimilarityMatch(
                rank=query.offset + position,
                case_id=hit.case_id,
                event_id=candidate_by_id[hit.case_id].event_id,
                advisory_source_id=(
                    candidate_by_id[hit.case_id].advisory_source_id
                ),
                score=round(hit.similarity, 6),
                tmi_type_iri=_tmi_type(candidate_by_id[hit.case_id]),
                facility_ids=tuple(
                    sorted(candidate_by_id[hit.case_id].facility_ids)
                ),
                reason_status=candidate_by_id[
                    hit.case_id
                ].reason_status,
                reason_value=candidate_by_id[hit.case_id].reason_value,
            )
            for position, hit in enumerate(selected_hits, start=1)
        )
    except (KeyError, ValueError) as exc:
        return CaseSimilarityResult(
            status="blocked",
            query=query,
            candidate_count=len(candidates),
            representation_version=index.manifest.representation_version,
            embedding_model_id=index.manifest.embedding_model_id,
            limitation=str(exc),
        )
    return CaseSimilarityResult(
        status="ok" if matches else "insufficient",
        query=query,
        candidate_count=len(candidates),
        representation_version=index.manifest.representation_version,
        embedding_model_id=index.manifest.embedding_model_id,
        matches=matches,
        limitation=(
            ""
            if matches
            else "No ranked cases are available on the requested page."
        ),
    )
