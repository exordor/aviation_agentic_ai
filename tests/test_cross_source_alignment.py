from __future__ import annotations

import json

import pytest

from aviation_agentic_ai.cross_source.alignment.context_agent import ContextAlignmentAgent
from aviation_agentic_ai.cross_source.alignment.mentions import extract_mentions
from aviation_agentic_ai.cross_source.alignment.pipeline import align_records
from aviation_agentic_ai.cross_source.alignment.registry import build_term_registry
from aviation_agentic_ai.cross_source.config import load_cross_source_config
from aviation_agentic_ai.cross_source.contracts import (
    AlignmentCandidate,
    AlignmentMethod,
    AlignmentStatus,
    CanonicalEntity,
    CodeValue,
    EntityType,
    Mention,
    MentionType,
)


def _facilities() -> list[CanonicalEntity]:
    return [
        CanonicalEntity(
            entity_id="urn:aviation-agentic-ai:facility:airport:KEWR",
            entity_type=EntityType.AIRPORT,
            preferred_label="Newark Liberty International Airport",
            codes=[
                CodeValue(scheme="FAA", value="EWR"),
                CodeValue(scheme="IATA", value="EWR"),
                CodeValue(scheme="ICAO", value="KEWR"),
            ],
            aliases=["EWR", "KEWR"],
            source_refs=["faa_nasr:2026-05-14"],
        ),
        CanonicalEntity(
            entity_id="urn:aviation-agentic-ai:facility:artcc:ZNY",
            entity_type=EntityType.ARTCC,
            preferred_label="New York ARTCC",
            codes=[CodeValue(scheme="FAA_ARTCC", value="ZNY")],
            aliases=["ZNY", "New York Center"],
            source_refs=["faa_nasr:2026-05-14"],
        ),
    ]


def _record() -> dict[str, object]:
    return {
        "source_id": "2026-05-20:089",
        "source_family": "atcscc_advisories",
        "text": "ATCSCC ADVZY 089 EWR/ZNY CDM GROUND DELAY PROGRAM GDP DUE TO WX TSTMS",
    }


def test_extract_mentions_keeps_facility_and_term_layers_separate() -> None:
    config = load_cross_source_config("configs/cross_source_v1.yaml")
    terms = build_term_registry(config)

    mentions = extract_mentions(_record(), facilities=_facilities(), terms=terms)
    pairs = {(item.normalized_form, item.mention_type) for item in mentions}

    assert ("EWR", MentionType.FACILITY_CODE) in pairs
    assert ("ZNY", MentionType.FACILITY_CODE) in pairs
    assert ("GDP", MentionType.OPERATIONAL_TERM) in pairs
    assert ("WX", MentionType.OPERATIONAL_TERM) in pairs


def test_unique_authority_mappings_are_accepted_and_bridge_legacy_ids() -> None:
    config = load_cross_source_config("configs/cross_source_v1.yaml")
    terms = build_term_registry(config)

    result = align_records([_record()], facilities=_facilities(), terms=terms, config=config)
    accepted_targets = {
        item.target_id for item in result.decisions if item.status is AlignmentStatus.ACCEPTED
    }

    assert "urn:aviation-agentic-ai:facility:airport:KEWR" in accepted_targets
    assert "urn:aviation-agentic-ai:facility:artcc:ZNY" in accepted_targets
    assert any(item["legacy_id"].endswith(":EWR") for item in result.legacy_bridge)


def test_ambiguous_gs_is_resolved_autonomously_from_tmi_context() -> None:
    config = load_cross_source_config("configs/cross_source_v1.yaml")
    terms = build_term_registry(config)
    record = {
        "source_id": "2026-05-20:001",
        "source_family": "atcscc_advisories",
        "text": "CDM GS FOR EWR",
    }

    result = align_records([record], facilities=_facilities(), terms=terms, config=config)
    gs_decisions = [
        decision
        for mention, decision in zip(result.mentions, result.decisions, strict=True)
        if mention.normalized_form == "GS"
    ]

    assert len(gs_decisions) == 1
    assert gs_decisions[0].status is AlignmentStatus.ACCEPTED
    assert gs_decisions[0].method is AlignmentMethod.CONTEXT_AGENT
    assert gs_decisions[0].gate_score == 0.98


def test_ambiguous_gs_without_discriminating_context_is_quarantined() -> None:
    config = load_cross_source_config("configs/cross_source_v1.yaml")
    terms = build_term_registry(config)
    record = {
        "source_id": "2026-05-20:002",
        "source_family": "atcscc_advisories",
        "text": "REFERENCE GS",
    }

    result = align_records([record], facilities=_facilities(), terms=terms, config=config)
    mention_by_id = {mention.mention_id: mention for mention in result.mentions}
    gs = [
        decision
        for decision in result.decisions
        if mention_by_id[decision.mention_id].normalized_form == "GS"
    ]

    assert len(gs) == 1
    assert gs[0].status is AlignmentStatus.QUARANTINED
    assert gs[0].target_id is not None
    assert gs[0].candidate_margin == 0


def test_context_agent_cannot_create_target_outside_registry() -> None:
    mention = Mention(
        mention_id="mention:gs",
        source_id="source:1",
        source_family="atcscc_advisories",
        surface_form="GS",
        normalized_form="GS",
        mention_type=MentionType.OPERATIONAL_TERM,
        evidence_text="CDM GS FOR EWR",
        span_start=4,
        span_end=6,
        detected_by="test",
    )
    candidates = [
        AlignmentCandidate(
            mention_id=mention.mention_id,
            target_id="term:ground-stop",
            target_label="Ground Stop",
            target_type="traffic_management_initiative",
            method=AlignmentMethod.AUTHORITY_EXACT_CODE,
            authority_sources=["faa"],
            gate_score=1,
            rationale="exact abbreviation",
        ),
        AlignmentCandidate(
            mention_id=mention.mention_id,
            target_id="term:glide-slope",
            target_label="Glide Slope",
            target_type="operational_procedure",
            method=AlignmentMethod.AUTHORITY_EXACT_CODE,
            authority_sources=["faa"],
            gate_score=1,
            rationale="exact abbreviation",
        ),
    ]

    with pytest.raises(ValueError, match="outside the registry"):
        ContextAlignmentAgent().rank(
            mention=mention,
            candidates=candidates,
            invoker=lambda _messages: json.dumps(
                {"target_id": "term:invented", "score": 0.99, "rationale": "invented"}
            ),
        )


def test_context_agent_can_accept_one_supplied_candidate_after_gates() -> None:
    config = load_cross_source_config("configs/cross_source_v1.yaml")
    terms = build_term_registry(config)
    record = {
        "source_id": "2026-05-20:001",
        "source_family": "atcscc_advisories",
        "text": "CDM GS FOR EWR",
    }
    ground_stop = next(
        term.term_id for term in terms if term.abbreviation == "GS" and term.preferred_label == "Ground Stop"
    )

    result = align_records(
        [record],
        facilities=_facilities(),
        terms=terms,
        config=config,
        invoker=lambda _messages: json.dumps(
            {
                "target_id": ground_stop,
                "score": 0.96,
                "rationale": "The advisory traffic-management context and airport object support Ground Stop.",
            }
        ),
    )
    mention_by_id = {mention.mention_id: mention for mention in result.mentions}
    gs = [
        decision
        for decision in result.decisions
        if mention_by_id[decision.mention_id].normalized_form == "GS"
    ]

    assert len(gs) == 1
    assert gs[0].status is AlignmentStatus.ACCEPTED
    assert gs[0].method is AlignmentMethod.CONTEXT_AGENT
    assert gs[0].target_id == ground_stop
