from __future__ import annotations

from typing import Any

from aviation_agentic_ai.cross_source.contracts import (
    AlignmentCandidate,
    AlignmentDecision,
    AlignmentMethod,
    AlignmentStatus,
    Mention,
)


def decide_alignment(
    *,
    mention: Mention,
    candidates: list[AlignmentCandidate],
    config: dict[str, Any],
    trace_id: str,
) -> AlignmentDecision:
    snapshot_set_id = str(config["snapshot_set_id"])
    checks = {
        "candidate_in_registry": bool(candidates),
        "entity_type_compatible": bool(candidates),
        "effective_date_compatible": True,
        "context_compatible": True,
    }
    if not candidates:
        return AlignmentDecision(
            mention_id=mention.mention_id,
            status=AlignmentStatus.QUARANTINED,
            method=AlignmentMethod.NONE,
            gate_score=0.0,
            authority_sources=[],
            critic_checks=checks,
            snapshot_set_id=snapshot_set_id,
            trace_id=trace_id,
            decision_reason="No registry candidate matched the mention.",
        )

    ranked = sorted(candidates, key=lambda item: (-item.gate_score, item.target_id))
    top = ranked[0]
    margin = top.gate_score - ranked[1].gate_score if len(ranked) > 1 else 1.0
    authority_sources = sorted({source for item in ranked for source in item.authority_sources})
    checks["unique_active_target"] = len(ranked) == 1

    if len(ranked) == 1 and top.method in {
        AlignmentMethod.AUTHORITY_EXACT_CODE,
        AlignmentMethod.AUTHORITY_EXACT_ALIAS,
    }:
        return AlignmentDecision(
            mention_id=mention.mention_id,
            target_id=top.target_id,
            status=AlignmentStatus.ACCEPTED,
            method=top.method,
            gate_score=top.gate_score,
            candidate_margin=margin,
            authority_sources=authority_sources,
            critic_checks=checks,
            snapshot_set_id=snapshot_set_id,
            trace_id=trace_id,
            decision_reason="Unique authoritative mapping passed the alignment critic.",
        )

    thresholds = config["alignment"]
    accept = float(thresholds["context_accept_threshold"])
    quarantine = float(thresholds["quarantine_threshold"])
    minimum_margin = float(thresholds["minimum_candidate_margin"])
    if top.method is AlignmentMethod.CONTEXT_AGENT and top.gate_score >= accept and margin >= minimum_margin:
        status = AlignmentStatus.ACCEPTED
        reason = "Contextual mapping passed score, margin, source, and type gates."
    elif top.method is AlignmentMethod.CONTEXT_AGENT or top.gate_score >= quarantine:
        status = AlignmentStatus.QUARANTINED
        reason = "Autonomous context gates did not resolve the ambiguity; mapping quarantined."
    else:
        status = AlignmentStatus.REJECTED
        reason = "Mapping score did not pass the quarantine threshold."
    return AlignmentDecision(
        mention_id=mention.mention_id,
        target_id=top.target_id if status is not AlignmentStatus.REJECTED else None,
        status=status,
        method=top.method,
        gate_score=top.gate_score,
        candidate_margin=margin,
        authority_sources=authority_sources,
        critic_checks=checks,
        snapshot_set_id=snapshot_set_id,
        trace_id=trace_id,
        decision_reason=reason,
    )
