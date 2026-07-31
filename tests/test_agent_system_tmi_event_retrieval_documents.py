"""Deterministic event-publication documents used by vector retrieval."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
)
from aviation_agentic_ai.agent_system.ingestion_package import (
    EventIngestionPackage,
    IngestionAttempt,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    IngestionResult,
    SourceVersionRecord,
    TMIEventRecord,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_documents import (
    build_tmi_event_retrieval_document,
    build_tmi_event_retrieval_documents,
)
from aviation_agentic_ai.agent_system.contracts import SourceFamily
from aviation_agentic_ai.cross_source.identifiers import stable_id


ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
PROV_ENTITY = "http://www.w3.org/ns/prov#Entity"
KJFK = "urn:aviation-agentic-ai:facility:airport:KJFK"
KEWR = "urn:aviation-agentic-ai:facility:airport:KEWR"


@pytest.fixture
def evidence_store(tmp_path: Path):
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:retrieval-documents",
        create=True,
    )
    try:
        yield store
    finally:
        store.close()


def _source_version(source_id: str, content: str) -> SourceVersionRecord:
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return SourceVersionRecord(
        source_version_id=stable_id("source-version", source_id, digest),
        source_id=source_id,
        family=SourceFamily.ATCSCC_ADVISORY,
        asset_id=None,
        content=content,
        content_sha256=digest,
        source_url=None,
        logical_time=None,
        metadata={},
    )


def _publish_event(
    store: AviationEvidenceStore,
    *,
    name: str,
    source_id: str,
    event_type_iris: tuple[str, ...],
    facility_ids: tuple[str, ...] = (KJFK,),
    start: str = "2026-05-19T10:00:00+00:00",
    end: str = "2026-05-19T11:00:00+00:00",
    reason_status: str = "formal",
    reason_value: str | None = "weather",
    content_suffix: str = "",
) -> TMIEventRecord:
    version = _source_version(
        source_id,
        f"ADVISORY {source_id} {content_suffix}".rstrip(),
    )
    store.register_source_version(version)
    event_id = f"urn:event:{name}"
    publication_digest = hashlib.sha256(
        f"{name}:{version.source_version_id}".encode("utf-8")
    ).hexdigest()
    publication_id = stable_id(
        "event-publication",
        event_id,
        version.source_version_id,
        publication_digest,
    )
    event = TMIEventRecord(
        event_id=event_id,
        publication_id=publication_id,
        advisory_source_id=source_id,
        publication_source_version_id=version.source_version_id,
        event_type_iris=event_type_iris,
        facility_ids=facility_ids,
        effective_start=datetime.fromisoformat(start),
        effective_end=datetime.fromisoformat(end),
        issued_at=datetime(2026, 5, 19, 9, tzinfo=UTC),
        reason_status=reason_status,
        reason_value=reason_value,
    )
    package = EventIngestionPackage(
        event=event,
        formal_publication_digest=publication_digest,
        source_version_ids=(version.source_version_id,),
        source_anchors=(),
        facts=(),
        event_fact_memberships=(),
        evidence_links=(),
        profile_gaps=(),
        weather_associations=(),
        public_observations=(),
        observation_fact_ids={},
    )
    store.apply_ingestion_attempt(
        IngestionAttempt(
            result=IngestionResult(
                source_version_id=version.source_version_id,
                source_id=source_id,
                status="ok",
                event_id=event_id,
                publication_id=publication_id,
                reason="accepted",
                provider_call_count=0,
                tmi_family=name,
                preflight_eligible=True,
            ),
            package=package,
        )
    )
    return event


def _publish_three_reason_states(
    store: AviationEvidenceStore,
) -> None:
    _publish_event(
        store,
        name="formal",
        source_id="2026-05-19:138",
        event_type_iris=(PROV_ENTITY, f"{ATM}GroundDelayProgramTMI"),
        start="2026-05-19T22:05:00+00:00",
        end="2026-05-20T02:59:00+00:00",
        reason_status="formal",
        reason_value="weather",
    )
    _publish_event(
        store,
        name="profile-gap",
        source_id="2026-05-19:123",
        event_type_iris=(f"{ATM}GroundStopTMI", PROV_ENTITY),
        start="2026-05-19T21:00:00+00:00",
        end="2026-05-19T21:30:00+00:00",
        reason_status="profile_gap",
        reason_value="weather",
    )
    _publish_event(
        store,
        name="missing",
        source_id="2026-05-20:020",
        event_type_iris=(f"{ATM}GroundDelayProgramTMI",),
        facility_ids=(KEWR,),
        start="2026-05-20T12:00:00+00:00",
        end="2026-05-20T13:30:00+00:00",
        reason_status="missing",
        reason_value=None,
    )


def test_three_reason_states_have_distinct_canonical_documents(
    evidence_store: AviationEvidenceStore,
) -> None:
    _publish_three_reason_states(evidence_store)

    documents = {
        row.advisory_source_id: row
        for row in build_tmi_event_retrieval_documents(evidence_store)
    }

    assert "Declared reason status: profile gap." in documents[
        "2026-05-19:123"
    ].text
    assert "Source-supported reason category: weather." in documents[
        "2026-05-19:123"
    ].text
    assert documents["2026-05-19:138"].text == (
        "Traffic management measure: Ground Delay Program.\n"
        "Controlled facility: KJFK.\n"
        "Declared reason status: formal.\n"
        "Declared reason category: weather.\n"
        "Operational start time (UTC): 22:05.\n"
        "Operational end time (UTC): 02:59.\n"
        "Operational duration category: 4 to 8 hours."
    )
    assert "Declared reason status: missing." in documents[
        "2026-05-20:020"
    ].text
    assert "Declared reason category:" not in documents[
        "2026-05-20:020"
    ].text
    assert "Source-supported reason category:" not in documents[
        "2026-05-20:020"
    ].text


def test_decision_record_document_excludes_non_record_context(
    evidence_store: AviationEvidenceStore,
) -> None:
    event = _publish_event(
        evidence_store,
        name="formal",
        source_id="2026-05-19:138",
        event_type_iris=(f"{ATM}GroundDelayProgramTMI",),
    )

    document = build_tmi_event_retrieval_document(evidence_store, event)
    forbidden = (
        document.event_id,
        document.advisory_source_id,
        "METAR",
        "TAF",
        "scheduled_arrival_count",
        "cancelled_count",
        "2026-05",
    )

    assert all(value not in document.text for value in forbidden)


@pytest.mark.parametrize(
    ("start", "end", "expected_bucket", "expected_text"),
    [
        (
            "2026-05-19T10:00:00+00:00",
            "2026-05-19T10:59:00+00:00",
            "under_1_hour",
            "under 1 hour",
        ),
        (
            "2026-05-19T10:00:00+00:00",
            "2026-05-19T11:00:00+00:00",
            "1_to_2_hours",
            "1 to 2 hours",
        ),
        (
            "2026-05-19T10:00:00+00:00",
            "2026-05-19T12:00:00+00:00",
            "2_to_4_hours",
            "2 to 4 hours",
        ),
        (
            "2026-05-19T10:00:00+00:00",
            "2026-05-19T14:00:00+00:00",
            "4_to_8_hours",
            "4 to 8 hours",
        ),
        (
            "2026-05-19T10:00:00+00:00",
            "2026-05-19T18:00:00+00:00",
            "8_hours_or_more",
            "8 hours or more",
        ),
    ],
)
def test_duration_boundaries_are_canonical(
    evidence_store: AviationEvidenceStore,
    start: str,
    end: str,
    expected_bucket: str,
    expected_text: str,
) -> None:
    event = _publish_event(
        evidence_store,
        name="duration",
        source_id=f"source:{expected_bucket}",
        event_type_iris=(f"{ATM}GroundDelayProgramTMI",),
        start=start,
        end=end,
    )

    document = build_tmi_event_retrieval_document(evidence_store, event)

    assert document.duration_bucket == expected_bucket
    assert (
        f"Operational duration category: {expected_text}."
        in document.text
    )


def test_document_identity_is_publication_aware(
    evidence_store: AviationEvidenceStore,
) -> None:
    first_event = _publish_event(
        evidence_store,
        name="revision",
        source_id="source:revision",
        event_type_iris=(f"{ATM}GroundDelayProgramTMI",),
        content_suffix="first",
    )
    first = build_tmi_event_retrieval_document(
        evidence_store,
        first_event,
    )
    second_event = _publish_event(
        evidence_store,
        name="revision",
        source_id="source:revision",
        event_type_iris=(f"{ATM}GroundDelayProgramTMI",),
        content_suffix="second",
    )
    historical = evidence_store.get_event(
        first_event.event_id,
        publication_id=first_event.publication_id,
    )
    assert historical is not None

    reopened_first = build_tmi_event_retrieval_document(
        evidence_store,
        historical,
    )
    second = build_tmi_event_retrieval_document(
        evidence_store,
        second_event,
    )

    assert first == reopened_first
    assert first.document_id != second.document_id
    assert first.publication_id == first_event.publication_id
    assert second.publication_id == second_event.publication_id
    assert first.publication_source_version_id != (
        second.publication_source_version_id
    )


def test_document_identity_and_facilities_are_stable(
    evidence_store: AviationEvidenceStore,
) -> None:
    event = _publish_event(
        evidence_store,
        name="facility-order",
        source_id="source:facility-order",
        event_type_iris=(f"{ATM}GroundDelayProgramTMI",),
        facility_ids=(KJFK, KEWR),
    )

    first = build_tmi_event_retrieval_document(evidence_store, event)
    second = build_tmi_event_retrieval_document(evidence_store, event)

    assert first == second
    assert first.document_id.startswith("tmi-event-retrieval-document:")
    assert first.facility_ids == (KEWR, KJFK)
    assert "Controlled facility: KEWR, KJFK." in first.text


@pytest.mark.parametrize(
    "updates",
    [
        {"event_type_iris": (PROV_ENTITY,)},
        {"effective_start": None},
        {"effective_end": None},
    ],
)
def test_incomplete_accepted_case_does_not_publish_a_partial_document(
    evidence_store: AviationEvidenceStore,
    updates: dict[str, object],
) -> None:
    event = _publish_event(
        evidence_store,
        name="incomplete",
        source_id="source:incomplete",
        event_type_iris=(f"{ATM}GroundDelayProgramTMI",),
    ).model_copy(update=updates)

    with pytest.raises(ValueError):
        build_tmi_event_retrieval_document(evidence_store, event)


def test_case_without_formal_facility_edge_remains_retrievable(
    evidence_store: AviationEvidenceStore,
) -> None:
    event = _publish_event(
        evidence_store,
        name="no-facility",
        source_id="source:no-facility",
        event_type_iris=(f"{ATM}GroundDelayProgramTMI",),
        facility_ids=(),
    )

    document = build_tmi_event_retrieval_document(evidence_store, event)

    assert document.facility_ids == ()
    assert (
        "Controlled scope: not represented by a formal facility edge "
        "in the active profile."
        in document.text
    )
