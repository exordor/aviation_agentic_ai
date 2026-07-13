from datetime import UTC, datetime

from aviation_agentic_ai.cross_source.contracts import (
    AlignmentDecision,
    AlignmentMethod,
    AlignmentStatus,
    CanonicalEntity,
    CodeValue,
    EntityType,
    Mention,
    MentionType,
)
from aviation_agentic_ai.cross_source.linking.temporal import link_weather_records


FACILITY_ID = "urn:aviation-agentic-ai:facility:airport:KJFK"


def _mention() -> Mention:
    return Mention(
        mention_id="mention:1",
        source_id="2026-05-14:001",
        source_family="atcscc_advisories",
        surface_form="JFK",
        normalized_form="JFK",
        mention_type=MentionType.FACILITY_CODE,
        evidence_text="JFK",
        span_start=0,
        span_end=3,
        detected_by="test",
    )


def _decision(status: AlignmentStatus) -> AlignmentDecision:
    return AlignmentDecision(
        mention_id="mention:1",
        target_id=FACILITY_ID,
        status=status,
        method=AlignmentMethod.AUTHORITY_EXACT_CODE,
        gate_score=1,
        authority_sources=["faa_nasr"],
        snapshot_set_id="snapshot:test",
        trace_id="trace:test",
        decision_reason="test",
    )


def _config() -> dict:
    return {
        "snapshot_set_id": "snapshot:test",
        "temporal_linking": {
            "metar_before_minutes": 60,
            "metar_after_minutes": 60,
            "require_taf_validity_overlap": True,
        },
    }


def test_only_accepted_facility_mapping_creates_weather_links() -> None:
    advisory = {
        "source_id": "2026-05-14:001",
        "temporal_alignment": {
            "source_period_start": "2026-05-14T12:00:00Z",
            "source_period_end": "2026-05-14T13:00:00Z",
        },
    }
    facility = CanonicalEntity(
        entity_id=FACILITY_ID,
        entity_type=EntityType.AIRPORT,
        preferred_label="John F Kennedy International",
        codes=[CodeValue(scheme="ICAO", value="KJFK")],
    )
    metar = {
        "icaoId": "KJFK",
        "reportTime": "2026-05-14T13:30:00Z",
        "rawOb": "METAR KJFK TEST",
    }
    taf = {
        "icaoId": "KJFK",
        "validTimeFrom": datetime(2026, 5, 14, 11, tzinfo=UTC).timestamp(),
        "validTimeTo": datetime(2026, 5, 14, 14, tzinfo=UTC).timestamp(),
        "rawTAF": "TAF KJFK TEST",
    }

    accepted = link_weather_records(
        [advisory],
        mentions=[_mention()],
        decisions=[_decision(AlignmentStatus.ACCEPTED)],
        facilities=[facility],
        metar_rows=[metar],
        taf_rows=[taf],
        config=_config(),
    )
    quarantined = link_weather_records(
        [advisory],
        mentions=[_mention()],
        decisions=[_decision(AlignmentStatus.QUARANTINED)],
        facilities=[facility],
        metar_rows=[metar],
        taf_rows=[taf],
        config=_config(),
    )

    assert {link.predicate for link in accepted.links} == {
        "hasContemporaneousObservation",
        "hasOverlappingForecast",
    }
    assert all(link.causal_claim is False for link in accepted.links)
    assert quarantined.links == []
