"""Build compact, deterministic documents for decision-record retrieval."""

from __future__ import annotations

from datetime import UTC, datetime

from aviation_agentic_ai.agent_system.case_retrieval_contracts import (
    REPRESENTATION_VERSION,
    CaseRetrievalDocument,
    DurationBucket,
)
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusCase,
    CorpusQueryStore,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id


_ATM_NAMESPACE = "https://data.nasa.gov/ontologies/atmonto/ATM#"
_TMI_LABELS = {
    f"{_ATM_NAMESPACE}GroundDelayProgramTMI": "Ground Delay Program",
    f"{_ATM_NAMESPACE}GroundStopTMI": "Ground Stop",
}
_DURATION_LABELS: dict[DurationBucket, str] = {
    "under_1_hour": "under 1 hour",
    "1_to_2_hours": "1 to 2 hours",
    "2_to_4_hours": "2 to 4 hours",
    "4_to_8_hours": "4 to 8 hours",
    "8_hours_or_more": "8 hours or more",
}


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(UTC)


def _duration_bucket(start: str, end: str) -> DurationBucket:
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


def _reviewed_tmi(case: CorpusCase) -> tuple[str, str]:
    reviewed = [
        (iri, _TMI_LABELS[iri])
        for iri in case.event_type_iris
        if iri in _TMI_LABELS
    ]
    if len(reviewed) != 1:
        raise ValueError(
            f"case must have one reviewed TMI type: {case.case_id}"
        )
    return reviewed[0]


def _facility_label(facility_id: str) -> str:
    return facility_id.rsplit(":", 1)[-1]


def _document_text(
    *,
    case: CorpusCase,
    tmi_label: str,
    facility_ids: tuple[str, ...],
    start: datetime,
    end: datetime,
    duration_bucket: DurationBucket,
) -> str:
    lines = [
        f"Traffic management measure: {tmi_label}.",
        "Controlled facility: "
        + ", ".join(_facility_label(value) for value in facility_ids)
        + ".",
        f"Declared reason status: {case.reason_status.replace('_', ' ')}.",
    ]
    if case.reason_status == "formal":
        lines.append(
            f"Declared reason category: {case.reason_value}."
        )
    elif case.reason_status == "profile_gap":
        lines.append(
            f"Source-supported reason category: {case.reason_value}."
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


def build_case_retrieval_documents(
    store: CorpusQueryStore,
) -> tuple[CaseRetrievalDocument, ...]:
    """Return one canonical retrieval document for each accepted corpus case."""

    documents: list[CaseRetrievalDocument] = []
    for case in sorted(store.cases, key=lambda row: row.case_id):
        tmi_type_iri, tmi_label = _reviewed_tmi(case)
        facility_ids = tuple(sorted(case.facility_ids))
        if not facility_ids:
            raise ValueError(f"case has no controlled facility: {case.case_id}")
        if case.operational_start is None or case.operational_end is None:
            raise ValueError(
                f"case has incomplete operational boundaries: {case.case_id}"
            )
        start = _parse_utc(case.operational_start)
        end = _parse_utc(case.operational_end)
        duration_bucket = _duration_bucket(
            case.operational_start,
            case.operational_end,
        )
        text = _document_text(
            case=case,
            tmi_label=tmi_label,
            facility_ids=facility_ids,
            start=start,
            end=end,
            duration_bucket=duration_bucket,
        )
        documents.append(
            CaseRetrievalDocument(
                document_id=stable_id(
                    "case-retrieval-document",
                    REPRESENTATION_VERSION,
                    case.case_id,
                    text,
                ),
                case_id=case.case_id,
                event_id=case.event_id,
                advisory_source_id=case.advisory_source_id,
                text=text,
                tmi_type_iri=tmi_type_iri,
                facility_ids=facility_ids,
                reason_status=case.reason_status,
                reason_value=case.reason_value,
                duration_bucket=duration_bucket,
                operational_start=case.operational_start,
                operational_end=case.operational_end,
            )
        )
    return tuple(documents)
