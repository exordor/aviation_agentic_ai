from types import SimpleNamespace

from aviation_agentic_ai.cross_source.contracts import (
    AlignmentCandidate,
    AlignmentDecision,
    AlignmentMethod,
    AlignmentStatus,
    CrossSourceLink,
    Mention,
    MentionType,
    TimeInterval,
)
from aviation_agentic_ai.cross_source.qa.answering import (
    AnswerEvidenceCritic,
    build_cross_source_answer,
)
from aviation_agentic_ai.cross_source.supervisor import answer_from_build


def test_answer_separates_evidence_layers_and_disclaims_causality() -> None:
    interval = TimeInterval(
        start="2026-05-14T12:00:00Z", end="2026-05-14T13:00:00Z"
    )
    link = CrossSourceLink(
        link_id="link:1",
        subject_id="adv:1",
        predicate="hasContemporaneousObservation",
        object_id="metar:1",
        link_method="accepted_facility_plus_metar_window",
        facility_id="facility:KJFK",
        advisory_interval=interval,
        evidence_interval=interval,
        authority_sources=["snapshot:test"],
        evidence_text="METAR KJFK TEST",
        causal_claim=False,
    )
    answer = build_cross_source_answer(
        "What weather evidence overlaps the advisory?",
        advisory={"source_id": "adv:1", "text": "MESSAGE:\nJFK GROUND STOP"},
        links=[link],
        weather_records={"metar:1": {"icaoId": "KJFK", "rawOb": "METAR KJFK TEST"}},
        snapshot_set_id="snapshot:test",
    )

    assert answer.abstain is False
    assert answer.source_assertions
    assert answer.observation_evidence
    assert answer.system_associations
    assert "does not establish causation" in answer.system_associations[0].text.lower()
    assert AnswerEvidenceCritic().validate(answer) == []


def test_live_operational_question_abstains() -> None:
    answer = build_cross_source_answer(
        "Should the flight depart right now?",
        advisory={"source_id": "adv:1", "text": "MESSAGE:\nJFK GROUND STOP"},
        links=[],
        weather_records={},
        snapshot_set_id="snapshot:test",
    )

    assert answer.abstain is True
    assert answer.citations == []
    assert "live operational" in answer.rationale


def test_question_facility_filters_multi_airport_evidence() -> None:
    interval = TimeInterval(
        start="2026-05-20T12:00:00Z", end="2026-05-20T13:00:00Z"
    )
    links = [
        CrossSourceLink(
            link_id=f"link:{code}",
            subject_id="adv:1",
            predicate="hasContemporaneousObservation",
            object_id=f"metar:{code}",
            link_method="accepted_facility_plus_metar_window",
            facility_id=f"urn:aviation-agentic-ai:facility:airport:{code}",
            advisory_interval=interval,
            evidence_interval=interval,
            authority_sources=["snapshot:test"],
            evidence_text=f"METAR {code} TEST",
            causal_claim=False,
        )
        for code in ("KJFK", "KEWR")
    ]
    answer = build_cross_source_answer(
        "What weather evidence is associated with EWR?",
        advisory={"source_id": "adv:1", "text": "MESSAGE:\nJFK EWR ADVISORY"},
        links=links,
        weather_records={
            f"metar:{code}": {"icaoId": code, "rawOb": f"METAR {code} TEST"}
            for code in ("KJFK", "KEWR")
        },
        snapshot_set_id="snapshot:test",
    )

    assert len(answer.observation_evidence) == 1
    assert "KEWR" in answer.observation_evidence[0].text


def test_raw_text_answer_selects_requested_airport_sections() -> None:
    answer = build_cross_source_answer(
        "What did the SWAP source say about JFK and EWR?",
        advisory={
            "source_id": "adv:raw",
            "text": (
                "ATCSCC ADVZY 050 ZBW INTERNATIONAL SWAP_FYI\n"
                "RAW TEXT:\n"
                "EVENT TIME: TEST JFK: IF JFK ROUTE DETAILS EWR: IF EWR ROUTE DETAILS "
                "PHL: IF PHL ROUTE DETAILS"
            ),
        },
        links=[],
        weather_records={},
        snapshot_set_id="snapshot:test",
    )

    evidence = answer.source_assertions[0].evidence_text
    assert evidence == "JFK: IF JFK ROUTE DETAILS EWR: IF EWR ROUTE DETAILS"
    assert "PHL" not in evidence


def test_quarantined_term_answer_exposes_autonomous_evidence_and_abstains() -> None:
    mention = Mention(
        mention_id="mention:gs",
        source_id="adv:gs",
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
            target_id=target_id,
            target_label=label,
            target_type=target_type,
            method=AlignmentMethod.AUTHORITY_EXACT_CODE,
            authority_sources=["faa_pilot_controller_glossary"],
            gate_score=1,
            rationale="authoritative abbreviation candidate",
        )
        for target_id, label, target_type in (
            ("term:ground-stop", "Ground Stop", "traffic_management_initiative"),
            ("term:glide-slope", "Glide Slope", "operational_procedure"),
        )
    ]
    decision = AlignmentDecision(
        mention_id=mention.mention_id,
        target_id="term:ground-stop",
        status=AlignmentStatus.QUARANTINED,
        method=AlignmentMethod.CONTEXT_AGENT,
        gate_score=0.5,
        candidate_margin=0,
        authority_sources=["faa_pilot_controller_glossary"],
        snapshot_set_id="snapshot:test",
        trace_id="trace:gs",
        decision_reason="Autonomous context gates did not resolve the ambiguity.",
    )
    build = SimpleNamespace(
        advisories_by_id={"adv:gs": {"source_id": "adv:gs", "text": "CDM GS FOR EWR"}},
        config={"snapshot_set_id": "snapshot:test"},
        alignment=SimpleNamespace(
            mentions=[mention],
            candidates=candidates,
            decisions=[decision],
        ),
    )

    answer = answer_from_build(build, source_id="adv:gs", question="What does GS mean?")

    assert answer.abstain is True
    assert len(answer.alignment_explanations) == 1
    notice = answer.alignment_explanations[0]
    assert {candidate.target_label for candidate in notice.candidates} == {
        "Ground Stop",
        "Glide Slope",
    }
    assert notice.evidence_text == "CDM GS FOR EWR"
    assert notice.mapping_confidence == 0.5
    assert notice.candidate_margin == 0
    assert notice.write_to_formal_kg is False
    assert notice.autonomous_action == "quarantined"
    assert answer.citations[0].evidence_text == "CDM GS FOR EWR"
    assert AnswerEvidenceCritic().validate(answer) == []
