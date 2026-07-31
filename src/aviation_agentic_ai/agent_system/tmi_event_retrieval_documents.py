"""Build compact, deterministic documents for TMI-event retrieval."""

from __future__ import annotations

from datetime import UTC, datetime

from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
    REPRESENTATION_VERSION,
    TMIEventRetrievalDocument,
    DurationBucket,
)
from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    TMIEventQuery,
    TMIEventRecord,
)
from aviation_agentic_ai.agent_system.tmi_profiles import active_tmi_profiles
from aviation_agentic_ai.utils.identifiers import stable_id


_EVENT_PAGE_SIZE = 100
_TMI_LABELS = {
    ontology_class: profile.retrieval_label
    for profile in active_tmi_profiles()
    for ontology_class in (
        profile.ontology_class,
        profile.prefixed_ontology_class,
    )
    if ontology_class is not None
}
_DURATION_LABELS: dict[DurationBucket, str] = {
    "under_1_hour": "under 1 hour",
    "1_to_2_hours": "1 to 2 hours",
    "2_to_4_hours": "2 to 4 hours",
    "4_to_8_hours": "4 to 8 hours",
    "8_hours_or_more": "8 hours or more",
}


def _parse_utc(value: str | datetime) -> datetime:
    parsed = (
        value
        if isinstance(value, datetime)
        else datetime.fromisoformat(value.replace("Z", "+00:00"))
    )
    return parsed.astimezone(UTC)


def _duration_bucket(
    start: str | datetime,
    end: str | datetime,
) -> DurationBucket:
    start_time = _parse_utc(start)
    end_time = _parse_utc(end)
    minutes = (end_time - start_time).total_seconds() / 60
    if minutes < 60:
        return "under_1_hour"
    if minutes < 120:
        return "1_to_2_hours"
    if minutes < 240:
        return "2_to_4_hours"
    if minutes < 480:
        return "4_to_8_hours"
    return "8_hours_or_more"


def _reviewed_tmi(event: TMIEventRecord) -> tuple[str, str]:
    reviewed = [
        (iri, _TMI_LABELS[iri])
        for iri in event.event_type_iris
        if iri in _TMI_LABELS
    ]
    if len(reviewed) != 1:
        raise ValueError(
            f"event must have one reviewed TMI type: {event.event_id}"
        )
    return reviewed[0]


def _facility_label(facility_id: str) -> str:
    return facility_id.rsplit(":", 1)[-1]


def _document_text(
    *,
    event: TMIEventRecord,
    tmi_label: str,
    facility_ids: tuple[str, ...],
    start: datetime,
    end: datetime,
    duration_bucket: DurationBucket,
) -> str:
    lines = [
        f"Traffic management measure: {tmi_label}.",
        f"Declared reason status: {event.reason_status.replace('_', ' ')}.",
    ]
    if facility_ids:
        lines.insert(
            1,
            "Controlled facility: "
            + ", ".join(_facility_label(value) for value in facility_ids)
            + ".",
        )
    else:
        lines.insert(
            1,
            "Controlled scope: not represented by a formal facility edge "
            "in the active profile.",
        )
    if event.reason_status == "formal":
        lines.append(
            f"Declared reason category: {event.reason_value}."
        )
    elif event.reason_status == "profile_gap":
        lines.append(
            f"Source-supported reason category: {event.reason_value}."
        )
    lines.extend(
        (
            f"Operational start time (UTC): {start:%H:%M}.",
            f"Operational end time (UTC): {end:%H:%M}.",
            "Operational duration category: "
            f"{_DURATION_LABELS[duration_bucket]}.",
        )
    )
    return "\n".join(lines)


def build_tmi_event_retrieval_document(
    store: AviationEvidenceStore,
    event: TMIEventRecord,
) -> TMIEventRetrievalDocument:
    """Build one deterministic document for an immutable publication."""

    tmi_type_iri, tmi_label = _reviewed_tmi(event)
    facility_ids = tuple(sorted(event.facility_ids))
    if event.effective_start is None or event.effective_end is None:
        raise ValueError(
            f"event has incomplete effective boundaries: {event.event_id}"
        )
    start = _parse_utc(event.effective_start)
    end = _parse_utc(event.effective_end)
    duration_bucket = _duration_bucket(
        event.effective_start,
        event.effective_end,
    )
    text = _document_text(
        event=event,
        tmi_label=tmi_label,
        facility_ids=facility_ids,
        start=start,
        end=end,
        duration_bucket=duration_bucket,
    )
    source_version_ids = tuple(
        row.source_version_id
        for row in store.get_event_sources(
            event.event_id,
            publication_id=event.publication_id,
        )
    )
    fact_ids = tuple(
        row.fact_id
        for row in store.get_event_facts(
            event.event_id,
            publication_id=event.publication_id,
        )
    )
    return TMIEventRetrievalDocument(
        document_id=stable_id(
            "tmi-event-retrieval-document",
            REPRESENTATION_VERSION,
            event.publication_id,
            text,
        ),
        event_id=event.event_id,
        publication_id=event.publication_id,
        advisory_source_id=event.advisory_source_id,
        publication_source_version_id=(
            event.publication_source_version_id
        ),
        source_version_ids=source_version_ids,
        fact_ids=fact_ids,
        text=text,
        tmi_type_iri=tmi_type_iri,
        facility_ids=facility_ids,
        reason_status=event.reason_status,
        reason_value=event.reason_value,
        duration_bucket=duration_bucket,
        effective_start=event.effective_start,
        effective_end=event.effective_end,
    )


def build_tmi_event_retrieval_documents(
    store: AviationEvidenceStore,
) -> tuple[TMIEventRetrievalDocument, ...]:
    """Return one document for each active accepted TMI publication."""

    documents: list[TMIEventRetrievalDocument] = []
    offset = 0
    while True:
        page = store.find_tmi_events(
            TMIEventQuery(offset=offset, limit=_EVENT_PAGE_SIZE)
        )
        documents.extend(
            build_tmi_event_retrieval_document(store, event)
            for event in page.events
        )
        offset += len(page.events)
        if offset >= page.total_matches or not page.events:
            break
    return tuple(
        sorted(
            documents,
            key=lambda row: (row.event_id, row.publication_id),
        )
    )
