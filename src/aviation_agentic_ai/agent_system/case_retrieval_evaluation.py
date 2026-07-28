"""Evaluate the bounded historical-case retrieval smoke set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Literal, Sequence

from pydantic import Field

from aviation_agentic_ai.agent_system.case_retrieval_contracts import (
    CaseSimilarityQuery,
)
from aviation_agentic_ai.agent_system.case_retrieval_index import (
    ChromaCaseRetrievalIndex,
)
from aviation_agentic_ai.agent_system.case_retrieval_search import (
    find_similar_cases,
)
from aviation_agentic_ai.agent_system.contracts import (
    CaseSimilarityMatch,
    StrictModel,
)
from aviation_agentic_ai.agent_system.corpus_store import CorpusQueryStore
from aviation_agentic_ai.config import load_yaml


class RetrievalSmokeMetrics(StrictModel):
    """Aggregate metrics for the small reviewed retrieval smoke set."""

    query_count: int = Field(ge=0)
    ranked_query_count: int = Field(ge=0)
    hit_count_at_1: int = Field(ge=0)
    hit_count_at_3: int = Field(ge=0)
    hit_rate_at_1: float = Field(ge=0.0, le=1.0)
    hit_rate_at_3: float = Field(ge=0.0, le=1.0)
    mean_reciprocal_rank: float = Field(ge=0.0, le=1.0)
    expected_insufficient_count: int = Field(ge=0)
    expected_insufficient_pass_count: int = Field(ge=0)


class _SmokeFilters(StrictModel):
    event_type_iri: str | None = None
    facility_id: str | None = None
    reason_status: Literal["formal", "profile_gap", "missing"] | None = None
    reason_value: str | None = None


class _SmokeQuery(StrictModel):
    query_source_id: str = Field(min_length=1)
    expected_status: Literal["ok", "insufficient"]
    filters: _SmokeFilters
    relevant_source_ids: tuple[str, ...] = ()


class _SmokeSet(StrictModel):
    version: Literal["case-retrieval-smoke-v1"]
    queries: tuple[_SmokeQuery, ...]


def _validate_match(
    match: CaseSimilarityMatch,
    *,
    anchor_case_id: str,
    filters: _SmokeFilters,
) -> None:
    if match.case_id == anchor_case_id:
        raise ValueError("ranked result contains the anchor case")
    if (
        filters.event_type_iri is not None
        and match.tmi_type_iri != filters.event_type_iri
    ):
        raise ValueError("ranked result violates the event-type filter")
    if (
        filters.facility_id is not None
        and filters.facility_id not in match.facility_ids
    ):
        raise ValueError("ranked result violates the facility filter")
    if (
        filters.reason_status is not None
        and match.reason_status != filters.reason_status
    ):
        raise ValueError("ranked result violates the reason-status filter")
    if (
        filters.reason_value is not None
        and match.reason_value != filters.reason_value
    ):
        raise ValueError("ranked result violates the reason-value filter")


def evaluate_case_retrieval_smoke(
    corpus_dir: str | Path,
    gold_path: str | Path,
) -> RetrievalSmokeMetrics:
    """Run the reviewed six-query relevance smoke set."""

    smoke = _SmokeSet.model_validate(load_yaml(gold_path))
    store = CorpusQueryStore(corpus_dir)
    index = ChromaCaseRetrievalIndex(
        store,
        store.root / "case_index",
    )
    case_by_source = {
        case.advisory_source_id: case for case in store.cases
    }
    for row in smoke.queries:
        if row.query_source_id not in case_by_source:
            raise ValueError(
                f"unknown query_source_id: {row.query_source_id}"
            )
        for source_id in row.relevant_source_ids:
            if source_id not in case_by_source:
                raise ValueError(
                    f"unknown relevant_source_id: {source_id}"
                )

    ranked_query_count = 0
    hit_count_at_1 = 0
    hit_count_at_3 = 0
    reciprocal_rank_sum = 0.0
    expected_insufficient_count = 0
    expected_insufficient_pass_count = 0
    for row in smoke.queries:
        anchor = case_by_source[row.query_source_id]
        query = CaseSimilarityQuery(
            reference_event_id=anchor.event_id,
            event_type_iri=row.filters.event_type_iri,
            facility_id=row.filters.facility_id,
            reason_status=row.filters.reason_status,
            reason_value=row.filters.reason_value,
            limit=20,
        )
        result = find_similar_cases(store, index, query)
        if result.status == "blocked":
            raise ValueError(
                f"retrieval blocked for {row.query_source_id}: "
                f"{result.limitation}"
            )
        for match in result.matches:
            _validate_match(
                match,
                anchor_case_id=anchor.case_id,
                filters=row.filters,
            )
        if row.expected_status == "insufficient":
            expected_insufficient_count += 1
            if result.status == "insufficient":
                expected_insufficient_pass_count += 1
            continue

        ranked_query_count += 1
        relevant = set(row.relevant_source_ids)
        relevant_rank = next(
            (
                match.rank
                for match in result.matches
                if match.advisory_source_id in relevant
            ),
            None,
        )
        if relevant_rank is None:
            continue
        if relevant_rank <= 1:
            hit_count_at_1 += 1
        if relevant_rank <= 3:
            hit_count_at_3 += 1
        reciprocal_rank_sum += 1.0 / relevant_rank

    return RetrievalSmokeMetrics(
        query_count=len(smoke.queries),
        ranked_query_count=ranked_query_count,
        hit_count_at_1=hit_count_at_1,
        hit_count_at_3=hit_count_at_3,
        hit_rate_at_1=(
            hit_count_at_1 / ranked_query_count
            if ranked_query_count
            else 0.0
        ),
        hit_rate_at_3=(
            hit_count_at_3 / ranked_query_count
            if ranked_query_count
            else 0.0
        ),
        mean_reciprocal_rank=(
            reciprocal_rank_sum / ranked_query_count
            if ranked_query_count
            else 0.0
        ),
        expected_insufficient_count=expected_insufficient_count,
        expected_insufficient_pass_count=(
            expected_insufficient_pass_count
        ),
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the smoke evaluator and print stable JSON metrics."""

    parser = argparse.ArgumentParser(
        description="Evaluate historical decision-case retrieval."
    )
    parser.add_argument("--corpus-dir", required=True)
    parser.add_argument("--gold", required=True)
    args = parser.parse_args(argv)
    metrics = evaluate_case_retrieval_smoke(
        corpus_dir=args.corpus_dir,
        gold_path=args.gold,
    )
    print(
        json.dumps(
            metrics.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
