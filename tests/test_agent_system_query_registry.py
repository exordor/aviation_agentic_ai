"""Contracts for the corpus-first registered-question router."""

from __future__ import annotations

import pytest

from aviation_agentic_ai.agent_system.query_registry import (
    HISTORICAL_SIMILARITY_ANALYSIS_QUESTION,
    OPERATIONAL_SITUATION_ANALYSIS_QUESTION,
    QueryIntent,
    classify_registered_question,
)
from aviation_agentic_ai.agent_system.query_plan import AnalysisIntent


def test_historical_similarity_routes_to_the_deterministic_corpus_intent() -> None:
    """Routing similarity through Analysis would bypass the S3 Chroma path."""

    assert (
        classify_registered_question(HISTORICAL_SIMILARITY_ANALYSIS_QUESTION)
        is QueryIntent.HISTORICAL_SIMILARITY
    )


def test_model_bound_analysis_remains_a_registered_analysis_intent() -> None:
    """Moving the registry must not make bounded Analysis unreachable."""

    assert (
        classify_registered_question(OPERATIONAL_SITUATION_ANALYSIS_QUESTION)
        is AnalysisIntent.OPERATIONAL_SITUATION
    )


@pytest.mark.parametrize(
    "question",
    (
        "Which operational situation is most similar?",
        "Which traffic-management measure is best?",
        "Why did weather cause this GDP?",
        "What is the live operational situation now?",
    ),
)
def test_unregistered_or_unsafe_wording_stays_outside_the_router(
    question: str,
) -> None:
    """Unsafe wording must not reach deterministic or model-bound execution."""

    assert classify_registered_question(question) is None
