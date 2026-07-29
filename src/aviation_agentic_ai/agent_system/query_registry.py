"""Exact registered questions for the corpus-first read surface."""

from __future__ import annotations

import re
from enum import Enum

from aviation_agentic_ai.agent_system.query_plan import AnalysisIntent


REGISTERED_COMPETENCY_QUESTION = (
    "What traffic management measure, controlled airport, and effective time "
    "are recorded in this advisory?"
)
MEASURE_QUESTION = "What traffic management measure was published?"
CONTROLLED_FACILITY_QUESTION = "Which airport was controlled?"
OPERATIONAL_PERIOD_QUESTION = "When did the measure apply?"
DECLARED_REASON_QUESTION = "What reason did the advisory state?"
PROVENANCE_QUESTION = "Which source supports this decision record?"
FORECAST_CONTEXT_QUESTION = "What forecast was known at decision time?"
OBSERVED_WEATHER_CONTEXT_QUESTION = "What observed weather context was available?"
PUBLIC_OUTCOME_QUESTION = (
    "What BTS-reported public operational observations are recorded?"
)
RECONSTRUCTED_CASE_QUESTION = "Reconstruct this decision case."
EPISODE_ANALYSIS_QUESTION = "What decision episode is recorded?"
OPERATIONAL_SITUATION_ANALYSIS_QUESTION = (
    "What public operational situation is recorded?"
)
APPLICABILITY_ANALYSIS_QUESTION = (
    "What applicability and observed flight impact are recorded?"
)
HISTORICAL_SIMILARITY_ANALYSIS_QUESTION = (
    "Which historical case is most similar?"
)
RECONSTRUCTION_EVIDENCE_PATH_QUESTION = (
    "Which weather reports and active-window BTS public observations "
    "belong to this reconstructed decision case?"
)


class QueryIntent(str, Enum):
    """Deterministic corpus question families."""

    COMBINED_RECORD = "combined_record"
    MEASURE = "measure"
    CONTROLLED_FACILITY = "controlled_facility"
    OPERATIONAL_PERIOD = "operational_period"
    DECLARED_REASON = "declared_reason"
    PROVENANCE = "provenance"
    FORECAST_CONTEXT = "forecast_context"
    OBSERVED_WEATHER_CONTEXT = "observed_weather_context"
    PUBLIC_OUTCOME = "public_outcome"
    RECONSTRUCTED_CASE = "reconstructed_case"
    RECONSTRUCTION_EVIDENCE_PATHS = "reconstruction_evidence_paths"
    HISTORICAL_SIMILARITY = "historical_similarity"


def normalize_question(question: str) -> str:
    """Return the canonical token form used by the exact registry."""

    return " ".join(re.findall(r"[a-z0-9]+", question.lower()))


def _passes_capability_gate(question: str) -> bool:
    """Reject non-English and safety-sensitive wording before intent lookup."""

    if not question.isascii():
        return False
    normalized = normalize_question(question)
    words = set(normalized.split())
    if not normalized:
        return False
    if words.intersection({"live", "current", "now", "today", "realtime"}):
        return False
    if "real time" in normalized:
        return False
    if (
        any(word.startswith("caus") for word in words)
        or words.intersection({"because", "why"})
        or any(
            phrase in normalized
            for phrase in (
                "result in",
                "resulted in",
                "results in",
                "resulting in",
            )
        )
    ):
        return False
    if "flight" in words and any(word.startswith("control") for word in words):
        return False
    return True


def classify_registered_question(
    question: str,
) -> QueryIntent | AnalysisIntent | None:
    """Map only an exact registered English question to one bounded intent."""

    if not _passes_capability_gate(question):
        return None
    exact: dict[str, QueryIntent | AnalysisIntent] = {
        normalize_question(REGISTERED_COMPETENCY_QUESTION): QueryIntent.COMBINED_RECORD,
        normalize_question(MEASURE_QUESTION): QueryIntent.MEASURE,
        normalize_question(CONTROLLED_FACILITY_QUESTION): QueryIntent.CONTROLLED_FACILITY,
        normalize_question(OPERATIONAL_PERIOD_QUESTION): QueryIntent.OPERATIONAL_PERIOD,
        normalize_question(DECLARED_REASON_QUESTION): QueryIntent.DECLARED_REASON,
        normalize_question(PROVENANCE_QUESTION): QueryIntent.PROVENANCE,
        normalize_question(FORECAST_CONTEXT_QUESTION): QueryIntent.FORECAST_CONTEXT,
        normalize_question(
            OBSERVED_WEATHER_CONTEXT_QUESTION
        ): QueryIntent.OBSERVED_WEATHER_CONTEXT,
        normalize_question(PUBLIC_OUTCOME_QUESTION): QueryIntent.PUBLIC_OUTCOME,
        normalize_question(RECONSTRUCTED_CASE_QUESTION): QueryIntent.RECONSTRUCTED_CASE,
        normalize_question(
            RECONSTRUCTION_EVIDENCE_PATH_QUESTION
        ): QueryIntent.RECONSTRUCTION_EVIDENCE_PATHS,
        normalize_question(
            HISTORICAL_SIMILARITY_ANALYSIS_QUESTION
        ): QueryIntent.HISTORICAL_SIMILARITY,
        normalize_question(EPISODE_ANALYSIS_QUESTION): AnalysisIntent.EPISODE,
        normalize_question(
            OPERATIONAL_SITUATION_ANALYSIS_QUESTION
        ): AnalysisIntent.OPERATIONAL_SITUATION,
        normalize_question(
            APPLICABILITY_ANALYSIS_QUESTION
        ): AnalysisIntent.APPLICABILITY_AND_IMPACT,
    }
    return exact.get(normalize_question(question))


__all__ = [
    "APPLICABILITY_ANALYSIS_QUESTION",
    "CONTROLLED_FACILITY_QUESTION",
    "DECLARED_REASON_QUESTION",
    "EPISODE_ANALYSIS_QUESTION",
    "FORECAST_CONTEXT_QUESTION",
    "HISTORICAL_SIMILARITY_ANALYSIS_QUESTION",
    "MEASURE_QUESTION",
    "OBSERVED_WEATHER_CONTEXT_QUESTION",
    "OPERATIONAL_PERIOD_QUESTION",
    "OPERATIONAL_SITUATION_ANALYSIS_QUESTION",
    "PROVENANCE_QUESTION",
    "PUBLIC_OUTCOME_QUESTION",
    "QueryIntent",
    "RECONSTRUCTED_CASE_QUESTION",
    "RECONSTRUCTION_EVIDENCE_PATH_QUESTION",
    "REGISTERED_COMPETENCY_QUESTION",
    "classify_registered_question",
    "normalize_question",
]
