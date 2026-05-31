from __future__ import annotations

import re
from typing import Any

from aviation_agentic_ai.evaluation.gold import GoldLabel
from aviation_agentic_ai.retrieval.hybrid import tokenize


RISK_TRIGGERS: dict[str, tuple[str, ...]] = {
    "live_weather": (
        "current weather",
        "live weather",
        "weather now",
        "metar",
        "taf",
        "winds aloft",
    ),
    "current_notam": ("notam", "current notice", "tfr", "temporary flight restriction"),
    "atc_clearance": ("atc", "clearance", "tower instruction", "air traffic control"),
    "aircraft_specific_vspeeds": (
        "v-speed",
        "vspeed",
        "v speeds",
        "v-speeds",
        "rotate speed",
        "best glide speed",
        "vx",
        "vy",
    ),
    "poh_or_checklist": (
        "poh",
        "afm",
        "pilot operating handbook",
        "checklist",
        "approved checklist",
    ),
    "emergency_procedure": (
        "emergency",
        "engine failure",
        "fire",
        "forced landing",
        "emergency procedure",
    ),
    "weight_and_balance": (
        "weight and balance",
        "center of gravity",
        "cg limit",
        "loading",
    ),
    "go_no_go_decision": (
        "go/no-go",
        "go no go",
        "go-nogo",
        "safe to fly",
        "safe to depart",
        "should i fly today",
        "should i fly now",
        "should i fly this flight",
        "depart today",
        "take off now",
        "continue the flight",
        "continue flight",
    ),
    "unknown_operational": (
        "right now",
        "today",
        "this flight",
        "my flight",
        "can i fly",
        "legally cleared",
        "legal vfr",
        "maintenance logbook",
        "airworthy",
        "icing along",
        "pireps",
        "fuel must",
        "planned route",
        "obstacle departure procedure",
        "runway will",
        "operational",
    ),
}

BOUNDARY_ORDER = (
    "live_weather",
    "current_notam",
    "atc_clearance",
    "aircraft_specific_vspeeds",
    "poh_or_checklist",
    "emergency_procedure",
    "weight_and_balance",
    "go_no_go_decision",
    "unknown_operational",
)


# Confidence thresholds for evidence sufficiency decisions.
# TODO: Calibrate these values against empirical evaluation data.
BOUNDARY_ABSTENTION_CONFIDENCE = 0.9
EVIDENCE_MATCH_ANSWER_CONFIDENCE = 0.85
EVIDENCE_MISMATCH_ABSTENTION_CONFIDENCE = 0.7


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def detect_risk_category(question: str) -> tuple[str, list[str]]:
    normalized = _normalize(question)
    for category in BOUNDARY_ORDER:
        matches = [
            trigger
            for trigger in RISK_TRIGGERS[category]
            if re.search(r"\b" + re.escape(trigger) + r"\b", normalized)
        ]
        if matches:
            return category, matches
    return "training_question", []


def _chunk_texts(chunks: list[dict[str, Any]]) -> str:
    return "\n".join(str(chunk.get("text", "")) for chunk in chunks)


def _expected_evidence_match(chunks: list[dict[str, Any]], gold_label: GoldLabel | None) -> bool:
    if gold_label is None or gold_label.expected_abstention:
        return False
    chunk_ids = {str(chunk.get("chunk_id", "")) for chunk in chunks}
    if gold_label.expected_chunk_ids and chunk_ids & set(gold_label.expected_chunk_ids):
        return True
    combined_text = _normalize(_chunk_texts(chunks))
    return any(
        _normalize(span.text) and _normalize(span.text) in combined_text
        for span in gold_label.evidence_spans
    )


def _evidence_signals(
    retrieval_result: dict[str, Any],
    gold_label: GoldLabel | None,
) -> dict[str, Any]:
    chunks = retrieval_result.get("fused_chunks", []) or []
    triples = retrieval_result.get("graph_triples", []) or []
    paths = retrieval_result.get("graph_paths", []) or []
    expected_match = _expected_evidence_match(chunks, gold_label)
    top_chunk = chunks[0] if chunks else {}
    return {
        "fused_chunk_count": len(chunks),
        "graph_triple_count": len(triples),
        "graph_path_count": len(paths),
        "top_chunk_id": top_chunk.get("chunk_id"),
        "top_chunk_has_text": bool(str(top_chunk.get("text", "")).strip()),
        "kg_evidence_present": bool(triples or paths),
        "expected_evidence_match": expected_match,
        "has_any_evidence": bool(chunks or triples or paths),
    }


def evaluate_evidence_sufficiency(
    question: str,
    retrieval_result: dict[str, Any],
    gold_label: GoldLabel | None = None,
) -> dict[str, Any]:
    """Make a deterministic answer/abstain decision from retrieval evidence and risk terms.

    When ``gold_label`` is supplied, the benchmark mode may use expected chunks or
    spans to measure whether retrieved evidence matches the answer key. Without a
    gold label, the same function runs in evidence-only mode and relies only on
    boundary terms and lexical overlap in retrieved context.
    """
    risk_category, matched_terms = detect_risk_category(question)
    evaluation_mode = "gold_aided_benchmark" if gold_label is not None else "evidence_only"
    signals = _evidence_signals(retrieval_result, gold_label)
    question_terms = tokenize(question)
    evidence_terms = tokenize(_chunk_texts(retrieval_result.get("fused_chunks", []) or []))
    lexical_overlap = sorted(question_terms & evidence_terms)
    signals["question_evidence_token_overlap"] = lexical_overlap
    signals["question_evidence_token_overlap_count"] = len(lexical_overlap)

    if risk_category != "training_question":
        return {
            "decision": "abstain",
            "reason": f"Question matches aviation boundary risk category `{risk_category}`.",
            "risk_category": risk_category,
            "confidence": BOUNDARY_ABSTENTION_CONFIDENCE,
            "matched_boundary_terms": matched_terms,
            "evidence_signals": signals,
            "evaluation_mode": evaluation_mode,
            "gold_aided_expected_evidence_used": False,
        }

    if gold_label is not None and not gold_label.expected_abstention:
        if signals["expected_evidence_match"]:
            decision = "answer"
            reason = "Retrieved evidence matches expected benchmark chunks or spans."
            confidence = EVIDENCE_MATCH_ANSWER_CONFIDENCE
        else:
            decision = "abstain"
            reason = "Retrieved evidence does not match expected benchmark evidence."
            confidence = EVIDENCE_MISMATCH_ABSTENTION_CONFIDENCE
    elif signals["has_any_evidence"] and signals["question_evidence_token_overlap_count"] >= 2:
        decision = "answer"
        reason = "Retrieved evidence has lexical overlap with the training question."
        confidence = 0.65
    else:
        decision = "abstain"
        reason = "No sufficient retrieved evidence was found for the training question."
        confidence = 0.6

    return {
        "decision": decision,
        "reason": reason,
        "risk_category": risk_category,
        "confidence": confidence,
        "matched_boundary_terms": matched_terms,
        "evidence_signals": signals,
        "evaluation_mode": evaluation_mode,
        "gold_aided_expected_evidence_used": bool(
            gold_label is not None and not gold_label.expected_abstention
        ),
    }
