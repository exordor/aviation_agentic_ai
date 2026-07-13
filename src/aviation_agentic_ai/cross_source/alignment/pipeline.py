from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from aviation_agentic_ai.cross_source.alignment.context_agent import (
    ContextAlignmentAgent,
    ContextInvoker,
)
from aviation_agentic_ai.cross_source.alignment.critic import decide_alignment
from aviation_agentic_ai.cross_source.alignment.mentions import extract_mentions
from aviation_agentic_ai.cross_source.alignment.resolver import AlignmentRegistry
from aviation_agentic_ai.cross_source.contracts import (
    AlignmentCandidate,
    AlignmentDecision,
    AlignmentStatus,
    CanonicalEntity,
    Mention,
    MentionType,
    TermConcept,
    TraceEvent,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id


@dataclass
class AlignmentRun:
    mentions: list[Mention]
    candidates: list[AlignmentCandidate]
    decisions: list[AlignmentDecision]
    legacy_bridge: list[dict[str, str]]
    trace_events: list[TraceEvent]


def align_records(
    records: Iterable[dict[str, Any]],
    *,
    facilities: list[CanonicalEntity],
    terms: list[TermConcept],
    config: dict[str, Any],
    invoker: ContextInvoker | None = None,
) -> AlignmentRun:
    registry = AlignmentRegistry(facilities, terms)
    context_agent = ContextAlignmentAgent()
    mentions: list[Mention] = []
    candidates: list[AlignmentCandidate] = []
    decisions: list[AlignmentDecision] = []
    trace_events: list[TraceEvent] = []
    bridge_by_pair: dict[tuple[str, str], dict[str, str]] = {}

    for record in records:
        record_mentions = extract_mentions(record, facilities=facilities, terms=terms)
        mentions.extend(record_mentions)
        for mention in record_mentions:
            trace_id = stable_id("trace", mention.source_id, mention.mention_id)
            ranked = registry.candidates(mention)
            if len(ranked) > 1:
                ranked = context_agent.rank(mention=mention, candidates=ranked, invoker=invoker)
            candidates.extend(ranked)
            decision = decide_alignment(
                mention=mention,
                candidates=ranked,
                config=config,
                trace_id=trace_id,
            )
            decisions.append(decision)
            trace_events.append(
                TraceEvent(
                    trace_id=trace_id,
                    node_id="alignment_critic",
                    status=(
                        "success"
                        if decision.status is AlignmentStatus.ACCEPTED
                        else "quarantined"
                        if decision.status is AlignmentStatus.QUARANTINED
                        else "rejected"
                    ),
                    input_summary={
                        "mention_id": mention.mention_id,
                        "candidate_count": len(ranked),
                    },
                    output_summary={
                        "status": decision.status.value,
                        "target_id": decision.target_id,
                    },
                )
            )
            if (
                decision.status is AlignmentStatus.ACCEPTED
                and decision.target_id
                and mention.mention_type is MentionType.FACILITY_CODE
            ):
                legacy = f"urn:aviation-agentic-ai:nas-element:{mention.normalized_form}"
                bridge_by_pair[(legacy, decision.target_id)] = {
                    "legacy_id": legacy,
                    "canonical_id": decision.target_id,
                    "source_id": mention.source_id,
                    "mention_id": mention.mention_id,
                }

    return AlignmentRun(
        mentions=mentions,
        candidates=candidates,
        decisions=decisions,
        legacy_bridge=[bridge_by_pair[key] for key in sorted(bridge_by_pair)],
        trace_events=trace_events,
    )
