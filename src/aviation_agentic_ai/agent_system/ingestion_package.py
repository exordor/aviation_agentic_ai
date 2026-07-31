"""Write-free, transaction-ready event publication packages."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict

from pydantic import Field, model_validator

from aviation_agentic_ai.agent_system.contracts import (
    FactTraceRow,
    ObservationFactTrace,
    PersistedProfileGap,
    StrictModel,
    TMIEventContext,
    WeatherFactTrace,
)
from aviation_agentic_ai.agent_system.materialize import (
    FormalPublication,
    _absolute_event_iri,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    EventEvidenceLink,
    EventProfileGapRecord,
    EventWeatherAssociation,
    IngestionResult,
    PublicObservationRecord,
    SemanticFactRecord,
    SourceAnchorRecord,
    TMIEventRecord,
)
from aviation_agentic_ai.utils.identifiers import stable_id


class EventFactMembership(StrictModel):
    """One fact admitted to one immutable event publication."""

    event_id: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    fact_id: str = Field(min_length=1)


class EventIngestionPackage(StrictModel):
    """All semantic rows accepted for one atomic event publication."""

    event: TMIEventRecord
    formal_publication_digest: str = Field(min_length=64, max_length=64)
    source_version_ids: tuple[str, ...]
    source_anchors: tuple[SourceAnchorRecord, ...]
    facts: tuple[SemanticFactRecord, ...]
    event_fact_memberships: tuple[EventFactMembership, ...]
    evidence_links: tuple[EventEvidenceLink, ...]
    profile_gaps: tuple[EventProfileGapRecord, ...]
    weather_associations: tuple[EventWeatherAssociation, ...]
    public_observations: tuple[PublicObservationRecord, ...]
    observation_fact_ids: dict[str, tuple[str, ...]]

    @model_validator(mode="after")
    def _validate_publication_scope(self) -> EventIngestionPackage:
        event = self.event
        expected_publication_id = stable_id(
            "event-publication",
            event.event_id,
            event.publication_source_version_id,
            self.formal_publication_digest,
        )
        if event.publication_id != expected_publication_id:
            raise ValueError(
                "publication identity does not match digest"
            )
        source_version_ids = set(self.source_version_ids)
        if len(source_version_ids) != len(self.source_version_ids):
            raise ValueError("source version IDs must be unique")
        if event.publication_source_version_id not in source_version_ids:
            raise ValueError(
                "publication source version is not bound to the publication"
            )
        fact_ids = {fact.fact_id for fact in self.facts}
        memberships = set()
        for membership in self.event_fact_memberships:
            if (
                membership.event_id != event.event_id
                or membership.publication_id != event.publication_id
            ):
                raise ValueError("fact membership is outside the publication")
            if membership.fact_id not in fact_ids:
                raise ValueError("fact membership references an unknown fact")
            memberships.add(membership.fact_id)
        if memberships != fact_ids:
            raise ValueError("every publication fact requires one membership")
        for anchor in self.source_anchors:
            if anchor.source_version_id not in source_version_ids:
                raise ValueError("source anchor is outside the publication")
        owner_ids = {
            "fact": fact_ids,
            "profile_gap": {
                row.profile_gap_id for row in self.profile_gaps
            },
            "weather_association": {
                row.association_id for row in self.weather_associations
            },
            "public_observation": {
                row.observation_id for row in self.public_observations
            },
        }
        for link in self.evidence_links:
            if (
                link.event_id != event.event_id
                or link.publication_id != event.publication_id
            ):
                raise ValueError("evidence link is outside the publication")
            if link.owner_id not in owner_ids[link.owner_kind]:
                raise ValueError("evidence link owner is outside the publication")
            if link.source_version_id not in source_version_ids:
                raise ValueError("evidence source is outside the publication")
        for gap in self.profile_gaps:
            if (
                gap.event_id != event.event_id
                or gap.publication_id != event.publication_id
            ):
                raise ValueError("profile gap is outside the publication")
        for association in self.weather_associations:
            if (
                association.event_id != event.event_id
                or association.publication_id != event.publication_id
            ):
                raise ValueError("weather association is outside the publication")
        observation_ids = {
            row.observation_id for row in self.public_observations
        }
        if set(self.observation_fact_ids) != observation_ids:
            raise ValueError(
                "observation fact membership does not match observations"
            )
        for observation in self.public_observations:
            if (
                observation.event_id != event.event_id
                or observation.publication_id != event.publication_id
            ):
                raise ValueError("public observation is outside the publication")
            if tuple(sorted(observation.fact_ids)) != tuple(
                sorted(self.observation_fact_ids[observation.observation_id])
            ):
                raise ValueError("public observation fact membership differs")
        return self


class IngestionAttempt(StrictModel):
    """One source result and optional atomic publication package."""

    result: IngestionResult
    package: EventIngestionPackage | None

    @model_validator(mode="after")
    def _validate_result_package(self) -> IngestionAttempt:
        if self.result.status == "ok":
            if self.package is None:
                raise ValueError("ok ingestion requires a package")
            if (
                self.result.event_id != self.package.event.event_id
                or self.result.publication_id
                != self.package.event.publication_id
            ):
                raise ValueError("ingestion result does not match publication")
        elif self.package is not None:
            raise ValueError("non-ok ingestion cannot carry a package")
        return self


def _formal_publication_digest(
    publication: FormalPublication,
) -> str:
    payload = {
        "facts": [
            fact.model_dump(mode="json")
            for fact in sorted(
                publication.accepted,
                key=lambda row: row.fact_id,
            )
        ],
        "profiles": [
            ref.model_dump(mode="json")
            for ref in sorted(
                publication.profile_refs,
                key=lambda row: (
                    row.layer,
                    row.profile_id,
                    row.profile_checksum,
                ),
            )
        ],
        "layer_fact_counts": dict(
            sorted(publication.layer_fact_counts.items())
        ),
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _source_anchor(
    version,
    evidence_text: str,
) -> SourceAnchorRecord:
    char_start = version.content.find(evidence_text)
    if char_start < 0:
        raise ValueError(
            f"evidence text not found in source version: {version.source_id}"
        )
    char_end = char_start + len(evidence_text)
    return SourceAnchorRecord(
        source_anchor_id=stable_id(
            "source-anchor",
            version.source_version_id,
            char_start,
            char_end,
        ),
        source_version_id=version.source_version_id,
        char_start=char_start,
        char_end=char_end,
        anchor_kind=(
            "full_record"
            if char_start == 0 and char_end == len(version.content)
            else "text_span"
        ),
    )


def _semantic_fact(fact) -> SemanticFactRecord:
    return SemanticFactRecord(
        fact_id=fact.fact_id,
        subject_iri=fact.subject_iri,
        subject_class_iri=fact.subject_class_iri,
        predicate_iri=fact.predicate_iri,
        object_kind=fact.object_kind,
        object_value=fact.object_value,
        object_class_iri=fact.object_class_iri,
        datatype_iri=fact.datatype_iri,
        validation_profile=fact.validation_profile,
        evidence_mode=fact.evidence_mode,
    )


def _version_for_trace(
    *,
    source_id: str,
    source_snapshot_sha256: str,
    versions_by_source: dict[str, tuple],
):
    candidates = versions_by_source.get(source_id, ())
    for version in candidates:
        if version.content_sha256 == source_snapshot_sha256:
            return version
    raise ValueError(
        f"source version is not registered for evidence: {source_id}"
    )


def build_event_ingestion_package(
    *,
    publication: FormalPublication,
    event_context: TMIEventContext,
    advisory_source_version_id: str,
    source_versions: tuple,
    direct_fact_traces: tuple[FactTraceRow, ...],
    weather_fact_traces: tuple[WeatherFactTrace, ...],
    observation_fact_traces: tuple[ObservationFactTrace, ...],
    profile_gaps: tuple[PersistedProfileGap, ...],
    weather_associations: tuple[EventWeatherAssociation, ...],
    public_observations: tuple[PublicObservationRecord, ...],
) -> EventIngestionPackage:
    """Normalize one Kernel-accepted publication without writing artifacts."""

    versions_by_id = {
        version.source_version_id: version for version in source_versions
    }
    if len(versions_by_id) != len(source_versions):
        raise ValueError("source versions must be unique")
    advisory_version = versions_by_id.get(advisory_source_version_id)
    if advisory_version is None:
        raise ValueError("advisory source version is not registered")
    if advisory_version.source_id != event_context.advisory_source_id:
        raise ValueError("advisory source version does not match event context")
    versions_by_source_lists: dict[str, list] = defaultdict(list)
    for version in source_versions:
        versions_by_source_lists[version.source_id].append(version)
    versions_by_source = {
        source_id: tuple(
            sorted(
                versions,
                key=lambda row: row.source_version_id,
            )
        )
        for source_id, versions in versions_by_source_lists.items()
    }

    publication_digest = _formal_publication_digest(publication)
    publication_id = stable_id(
        "event-publication",
        event_context.event_id,
        advisory_source_version_id,
        publication_digest,
    )
    semantic_facts = tuple(
        _semantic_fact(fact)
        for fact in sorted(
            publication.accepted,
            key=lambda row: row.fact_id,
        )
    )
    accepted_by_id = {fact.fact_id: fact for fact in publication.accepted}
    def is_event_fact(fact) -> bool:
        return _absolute_event_iri(fact.subject_iri) == event_context.event_id

    event_type_iris = tuple(
        sorted(
            {
                fact.object_value
                for fact in publication.accepted
                if is_event_fact(fact)
                and fact.predicate_iri
                == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
            }
        )
    )
    facility_ids = tuple(
        sorted(
            {
                fact.object_value
                for fact in publication.accepted
                if is_event_fact(fact)
                and fact.object_kind == "iri"
                and fact.predicate_iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]
                == "controlledNASelement"
            }
        )
    )
    reason_facts = [
        fact
        for fact in publication.accepted
        if is_event_fact(fact)
        and fact.predicate_iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]
        in {"impactingCondition", "reRouteReason"}
    ]
    has_reason_gap = any(
        gap.event_id == event_context.event_id
        and gap.field in {"impacting_condition", "re_route_reason"}
        for gap in profile_gaps
    )
    reason_status = (
        "formal"
        if reason_facts
        else "profile_gap"
        if has_reason_gap
        else "missing"
    )
    event = TMIEventRecord(
        event_id=event_context.event_id,
        publication_id=publication_id,
        advisory_source_id=event_context.advisory_source_id,
        publication_source_version_id=advisory_source_version_id,
        event_type_iris=event_type_iris,
        facility_ids=facility_ids,
        effective_start=event_context.operational_start,
        effective_end=event_context.operational_end,
        issued_at=event_context.advisory_issued_at,
        reason_status=reason_status,
        reason_value=reason_facts[0].object_value if reason_facts else None,
    )

    anchors_by_id: dict[str, SourceAnchorRecord] = {}
    evidence_links: list[EventEvidenceLink] = []
    direct_or_weather_traces = (
        *direct_fact_traces,
        *weather_fact_traces,
    )
    traced_source_text_fact_ids: set[str] = set()
    for trace in sorted(
        direct_or_weather_traces,
        key=lambda row: (
            row.fact_id,
            row.source_id,
            row.evidence_text,
        ),
    ):
        fact = accepted_by_id.get(trace.fact_id)
        if fact is None:
            raise ValueError("fact trace references a fact outside publication")
        version = _version_for_trace(
            source_id=trace.source_id,
            source_snapshot_sha256=trace.source_snapshot_sha256,
            versions_by_source=versions_by_source,
        )
        anchor = _source_anchor(version, trace.evidence_text)
        anchors_by_id[anchor.source_anchor_id] = anchor
        evidence_links.append(
            EventEvidenceLink(
                evidence_link_id=stable_id(
                    "event-evidence-link",
                    publication_id,
                    "fact",
                    fact.fact_id,
                    version.source_version_id,
                    anchor.source_anchor_id,
                    fact.evidence_ref,
                ),
                event_id=event.event_id,
                publication_id=publication_id,
                owner_kind="fact",
                owner_id=fact.fact_id,
                source_version_id=version.source_version_id,
                source_anchor_id=anchor.source_anchor_id,
                evidence_text=trace.evidence_text,
                evidence_ref=fact.evidence_ref,
            )
        )
        traced_source_text_fact_ids.add(fact.fact_id)

    for trace in sorted(
        observation_fact_traces,
        key=lambda row: (
            row.fact_id,
            row.source_id,
            row.observation_id,
        ),
    ):
        fact = accepted_by_id.get(trace.fact_id)
        if fact is None:
            raise ValueError(
                "observation trace references a fact outside publication"
            )
        version = _version_for_trace(
            source_id=trace.source_id,
            source_snapshot_sha256=trace.source_snapshot_sha256,
            versions_by_source=versions_by_source,
        )
        evidence_links.append(
            EventEvidenceLink(
                evidence_link_id=stable_id(
                    "event-evidence-link",
                    publication_id,
                    "fact",
                    fact.fact_id,
                    version.source_version_id,
                    trace.derivation_id,
                    fact.evidence_ref,
                ),
                event_id=event.event_id,
                publication_id=publication_id,
                owner_kind="fact",
                owner_id=fact.fact_id,
                source_version_id=version.source_version_id,
                source_anchor_id=None,
                evidence_text=None,
                evidence_ref=fact.evidence_ref,
            )
        )
    missing_source_text = sorted(
        fact.fact_id
        for fact in publication.accepted
        if fact.evidence_mode == "source_text"
        and fact.fact_id not in traced_source_text_fact_ids
    )
    if missing_source_text:
        raise ValueError(
            "source-text facts lack exact evidence traces: "
            + ", ".join(missing_source_text)
        )

    bound_gaps: list[EventProfileGapRecord] = []
    for gap in sorted(profile_gaps, key=lambda row: row.profile_gap_id):
        version = _version_for_trace(
            source_id=gap.source_id,
            source_snapshot_sha256=gap.source_snapshot_sha256,
            versions_by_source=versions_by_source,
        )
        anchor = _source_anchor(version, gap.evidence_text)
        anchors_by_id[anchor.source_anchor_id] = anchor
        bound = bind_profile_gap(
            gap,
            publication_id=publication_id,
            source_version_id=version.source_version_id,
            source_anchor_id=anchor.source_anchor_id,
        )
        bound_gaps.append(bound)
        evidence_links.append(
            EventEvidenceLink(
                evidence_link_id=stable_id(
                    "event-evidence-link",
                    publication_id,
                    "profile_gap",
                    gap.profile_gap_id,
                    version.source_version_id,
                    anchor.source_anchor_id,
                    gap.evidence_ref,
                ),
                event_id=event.event_id,
                publication_id=publication_id,
                owner_kind="profile_gap",
                owner_id=gap.profile_gap_id,
                source_version_id=version.source_version_id,
                source_anchor_id=anchor.source_anchor_id,
                evidence_text=gap.evidence_text,
                evidence_ref=gap.evidence_ref,
            )
        )

    bound_associations = tuple(
        association.model_copy(
            update={
                "event_id": event.event_id,
                "publication_id": publication_id,
            }
        )
        for association in weather_associations
    )
    for association in bound_associations:
        evidence_links.append(
            EventEvidenceLink(
                evidence_link_id=stable_id(
                    "event-evidence-link",
                    publication_id,
                    "weather_association",
                    association.association_id,
                    association.source_version_id,
                    association.association_id,
                ),
                event_id=event.event_id,
                publication_id=publication_id,
                owner_kind="weather_association",
                owner_id=association.association_id,
                source_version_id=association.source_version_id,
                source_anchor_id=None,
                evidence_text=None,
                evidence_ref=association.association_id,
            )
        )
    bound_observations = tuple(
        observation.model_copy(
            update={
                "event_id": event.event_id,
                "publication_id": publication_id,
            }
        )
        for observation in public_observations
    )
    for observation in bound_observations:
        evidence_links.append(
            EventEvidenceLink(
                evidence_link_id=stable_id(
                    "event-evidence-link",
                    publication_id,
                    "public_observation",
                    observation.observation_id,
                    observation.source_version_id,
                    observation.observation_id,
                ),
                event_id=event.event_id,
                publication_id=publication_id,
                owner_kind="public_observation",
                owner_id=observation.observation_id,
                source_version_id=observation.source_version_id,
                source_anchor_id=None,
                evidence_text=None,
                evidence_ref=observation.observation_id,
            )
        )
    observation_fact_ids = {
        observation.observation_id: tuple(sorted(observation.fact_ids))
        for observation in bound_observations
    }
    return EventIngestionPackage(
        event=event,
        formal_publication_digest=publication_digest,
        source_version_ids=tuple(sorted(versions_by_id)),
        source_anchors=tuple(
            anchors_by_id[anchor_id] for anchor_id in sorted(anchors_by_id)
        ),
        facts=semantic_facts,
        event_fact_memberships=tuple(
            EventFactMembership(
                event_id=event.event_id,
                publication_id=publication_id,
                fact_id=fact.fact_id,
            )
            for fact in semantic_facts
        ),
        evidence_links=tuple(
            sorted(
                evidence_links,
                key=lambda row: row.evidence_link_id,
            )
        ),
        profile_gaps=tuple(bound_gaps),
        weather_associations=bound_associations,
        public_observations=bound_observations,
        observation_fact_ids=observation_fact_ids,
    )


def bind_profile_gap(
    gap: PersistedProfileGap,
    *,
    publication_id: str,
    source_version_id: str,
    source_anchor_id: str,
) -> EventProfileGapRecord:
    """Bind one validated non-formal gap to an immutable publication."""

    return EventProfileGapRecord(
        profile_gap_id=gap.profile_gap_id,
        event_id=gap.event_id,
        publication_id=publication_id,
        field=gap.field,
        value=gap.value,
        evidence_text=gap.evidence_text,
        reason=gap.reason,
        source_version_id=source_version_id,
        source_anchor_id=source_anchor_id,
        evidence_ref=gap.evidence_ref,
        validation_profile=gap.validation_profile,
    )


__all__ = [
    "EventFactMembership",
    "EventIngestionPackage",
    "IngestionAttempt",
    "build_event_ingestion_package",
    "bind_profile_gap",
]
