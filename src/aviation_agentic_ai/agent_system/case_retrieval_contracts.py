"""Typed contracts for deterministic historical case retrieval."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import StrictModel


REPRESENTATION_VERSION = "decision-record-v1"

DurationBucket = Literal[
    "under_1_hour",
    "1_to_2_hours",
    "2_to_4_hours",
    "4_to_8_hours",
    "8_hours_or_more",
]


class CaseRetrievalDocument(StrictModel):
    """One deterministic decision-record document prepared for embedding."""

    document_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    advisory_source_id: str = Field(min_length=1)
    representation_version: Literal["decision-record-v1"] = (
        REPRESENTATION_VERSION
    )
    text: str = Field(min_length=1)
    tmi_type_iri: str = Field(min_length=1)
    facility_ids: tuple[str, ...]
    reason_status: Literal["formal", "profile_gap", "missing"]
    reason_value: str | None
    duration_bucket: DurationBucket
    operational_start: str = Field(min_length=1)
    operational_end: str = Field(min_length=1)
