"""Write-free publication package contracts for incremental ingestion."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from aviation_agentic_ai.agent_system.contracts import (
    FactTraceRow,
    SourceFamily,
    SourceRecord,
    TMIEventContext,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.ingestion_package import (
    EventFactMembership,
    EventIngestionPackage,
    IngestionAttempt,
    build_event_ingestion_package,
)
from aviation_agentic_ai.agent_system.materialize import FormalPublication
from aviation_agentic_ai.agent_system.sources import build_source_version
from aviation_agentic_ai.agent_system.sources import build_source_snapshot_registry
from aviation_agentic_ai.agent_system.storage_contracts import (
    IngestionResult,
    SemanticFactRecord,
    SourceAnchorRecord,
    TMIEventRecord,
)
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.cross_source.identifiers import stable_id


def _source_version():
    return build_source_version(
        SourceRecord(
            source_id="2026-05-20:138",
            family=SourceFamily.ATCSCC_ADVISORY,
            content="HEADER\nREASON: WEATHER\nREASON: WEATHER\n",
        )
    )


def _package() -> EventIngestionPackage:
    version = _source_version()
    event_id = "urn:aviation-agentic-ai:event:gdp-138"
    profile = next(
        ref
        for ref in load_validation_profile_registry(
            decision_guide=load_schema_guide()
        ).refs
        if ref.layer == "decision"
    )
    fact = SemanticFactRecord(
        fact_id="fact:reason",
        subject_iri=event_id,
        subject_class_iri=(
            "https://data.nasa.gov/ontologies/atmonto/ATM#"
            "GroundDelayProgramTMI"
        ),
        predicate_iri=(
            "https://data.nasa.gov/ontologies/atmonto/ATM#"
            "impactingCondition"
        ),
        object_kind="iri",
        object_value=(
            "https://data.nasa.gov/ontologies/atmonto/ATM#Weather"
        ),
        object_class_iri=(
            "https://data.nasa.gov/ontologies/atmonto/ATM#"
            "TMIImpactingCondition"
        ),
        datatype_iri=None,
        validation_profile=profile,
        evidence_mode="source_text",
    )
    start = version.content.index("REASON: WEATHER")
    anchor = SourceAnchorRecord(
        source_anchor_id=stable_id(
            "source-anchor",
            version.source_version_id,
            start,
            start + len("REASON: WEATHER"),
        ),
        source_version_id=version.source_version_id,
        char_start=start,
        char_end=start + len("REASON: WEATHER"),
        anchor_kind="text_span",
    )
    publication_digest = hashlib.sha256(b"formal-publication").hexdigest()
    publication_id = stable_id(
        "event-publication",
        event_id,
        version.source_version_id,
        publication_digest,
    )
    event = TMIEventRecord(
        event_id=event_id,
        publication_id=publication_id,
        advisory_source_id=version.source_id,
        publication_source_version_id=version.source_version_id,
        event_type_iris=(fact.subject_class_iri,),
        facility_ids=("urn:aviation-agentic-ai:facility:airport:KJFK",),
        effective_start=datetime(2026, 5, 20, 12, tzinfo=UTC),
        effective_end=datetime(2026, 5, 20, 14, tzinfo=UTC),
        issued_at=datetime(2026, 5, 20, 11, 30, tzinfo=UTC),
        reason_status="formal",
        reason_value=fact.object_value,
    )
    return EventIngestionPackage(
        event=event,
        formal_publication_digest=publication_digest,
        source_version_ids=(version.source_version_id,),
        source_anchors=(anchor,),
        facts=(fact,),
        event_fact_memberships=(
            EventFactMembership(
                event_id=event_id,
                publication_id=publication_id,
                fact_id=fact.fact_id,
            ),
        ),
        evidence_links=(),
        profile_gaps=(),
        weather_associations=(),
        public_observations=(),
        observation_fact_ids={},
    )


def test_ingestion_attempt_requires_package_only_for_ok() -> None:
    package = _package()
    ok_result = IngestionResult(
        source_version_id=package.event.publication_source_version_id,
        source_id=package.event.advisory_source_id,
        status="ok",
        event_id=package.event.event_id,
        publication_id=package.event.publication_id,
        reason="published",
        provider_call_count=0,
        tmi_family="GDP",
        preflight_eligible=True,
    )
    assert IngestionAttempt(result=ok_result, package=package).package == package

    with pytest.raises(ValidationError, match="ok ingestion requires a package"):
        IngestionAttempt(result=ok_result, package=None)

    insufficient = ok_result.model_copy(
        update={
            "status": "insufficient",
            "event_id": None,
            "publication_id": None,
        }
    )
    with pytest.raises(
        ValidationError,
        match="non-ok ingestion cannot carry a package",
    ):
        IngestionAttempt(result=insufficient, package=package)


def test_package_rejects_membership_outside_its_publication() -> None:
    package = _package()
    wrong = package.event_fact_memberships[0].model_copy(
        update={"publication_id": "publication:other"}
    )
    with pytest.raises(
        ValidationError,
        match="fact membership is outside the publication",
    ):
        EventIngestionPackage(
            **{
                **package.model_dump(),
                "event_fact_memberships": (wrong,),
            }
        )


def test_package_rejects_publication_identity_outside_its_digest() -> None:
    package = _package()
    with pytest.raises(
        ValidationError,
        match="publication identity does not match digest",
    ):
        EventIngestionPackage(
            **{
                **package.model_dump(),
                "formal_publication_digest": hashlib.sha256(
                    b"other-publication"
                ).hexdigest(),
            }
        )


def test_source_text_anchor_uses_lowest_duplicate_offset() -> None:
    version = _source_version()
    package = _package()

    assert package.source_anchors[0].source_version_id == version.source_version_id
    assert package.source_anchors[0].char_start == version.content.index(
        "REASON: WEATHER"
    )


def test_package_builder_anchors_lowest_exact_source_span() -> None:
    record = SourceRecord(
        source_id="2026-05-20:138",
        family=SourceFamily.ATCSCC_ADVISORY,
        content="REASON: WEATHER\nREASON: WEATHER\n",
    )
    version = build_source_version(record)
    profile = next(
        ref
        for ref in load_validation_profile_registry(
            decision_guide=load_schema_guide()
        ).refs
        if ref.layer == "decision"
    )
    event_id = "urn:aviation-agentic-ai:event:gdp-138"
    fact = ValidatedFact(
        fact_id="run-fact:reason",
        subject_iri=event_id,
        subject_class_iri=(
            "https://data.nasa.gov/ontologies/atmonto/ATM#"
            "GroundDelayProgramTMI"
        ),
        predicate_iri=(
            "https://data.nasa.gov/ontologies/atmonto/ATM#"
            "impactingCondition"
        ),
        object_kind="iri",
        object_value=(
            "https://data.nasa.gov/ontologies/atmonto/ATM#Weather"
        ),
        object_class_iri=(
            "https://data.nasa.gov/ontologies/atmonto/ATM#"
            "TMIImpactingCondition"
        ),
        datatype_iri=None,
        source_ids=[record.source_id],
        evidence_texts=["REASON: WEATHER"],
        validation_profile=profile,
        evidence_mode="source_text",
        evidence_ref="evidence:reason",
    )
    publication = FormalPublication(
        accepted=(fact,),
        snapshot_registry=build_source_snapshot_registry([record]),
        profile_refs=(profile,),
        layer_fact_counts={"decision": 1},
    )
    event_context = TMIEventContext(
        run_id="run:gdp-138",
        event_id=event_id,
        advisory_source_id=record.source_id,
        advisory_issued_at=datetime(2026, 5, 20, 11, 30, tzinfo=UTC),
        operational_start=datetime(2026, 5, 20, 12, tzinfo=UTC),
        operational_end=datetime(2026, 5, 20, 14, tzinfo=UTC),
    )
    package = build_event_ingestion_package(
        publication=publication,
        event_context=event_context,
        advisory_source_version_id=version.source_version_id,
        source_versions=(version,),
        direct_fact_traces=(
            FactTraceRow(
                fact_id=fact.fact_id,
                graph_patch_line="",
                source_id=record.source_id,
                evidence_text="REASON: WEATHER",
                evidence_agent_role="advisory",
                source_snapshot_sha256=version.content_sha256,
            ),
        ),
        weather_fact_traces=(),
        observation_fact_traces=(),
        profile_gaps=(),
        weather_associations=(),
        public_observations=(),
    )

    assert len(package.source_anchors) == 1
    assert package.source_anchors[0].char_start == 0
    assert package.evidence_links[0].source_anchor_id == (
        package.source_anchors[0].source_anchor_id
    )


def test_package_builder_blocks_missing_source_text() -> None:
    record = SourceRecord(
        source_id="2026-05-20:138",
        family=SourceFamily.ATCSCC_ADVISORY,
        content="REASON: WEATHER\n",
    )
    version = build_source_version(record)
    profile = next(
        ref
        for ref in load_validation_profile_registry(
            decision_guide=load_schema_guide()
        ).refs
        if ref.layer == "decision"
    )
    event_id = "urn:aviation-agentic-ai:event:gdp-138"
    fact = ValidatedFact(
        fact_id="run-fact:reason",
        subject_iri=event_id,
        subject_class_iri="atm:GroundDelayProgramTMI",
        predicate_iri="atm:impactingCondition",
        object_kind="iri",
        object_value="atm:Weather",
        object_class_iri="atm:TMIImpactingCondition",
        datatype_iri=None,
        source_ids=[record.source_id],
        evidence_texts=["REASON: THUNDERSTORMS"],
        validation_profile=profile,
        evidence_mode="source_text",
        evidence_ref="evidence:reason",
    )
    publication = FormalPublication(
        accepted=(fact,),
        snapshot_registry=build_source_snapshot_registry([record]),
        profile_refs=(profile,),
        layer_fact_counts={"decision": 1},
    )
    event_context = TMIEventContext(
        run_id="run:gdp-138",
        event_id=event_id,
        advisory_source_id=record.source_id,
        advisory_issued_at=datetime(2026, 5, 20, 11, 30, tzinfo=UTC),
        operational_start=datetime(2026, 5, 20, 12, tzinfo=UTC),
        operational_end=datetime(2026, 5, 20, 14, tzinfo=UTC),
    )

    with pytest.raises(ValueError, match="not found in source version"):
        build_event_ingestion_package(
            publication=publication,
            event_context=event_context,
            advisory_source_version_id=version.source_version_id,
            source_versions=(version,),
            direct_fact_traces=(
                FactTraceRow(
                    fact_id=fact.fact_id,
                    graph_patch_line="",
                    source_id=record.source_id,
                    evidence_text="REASON: THUNDERSTORMS",
                    evidence_agent_role="advisory",
                    source_snapshot_sha256=version.content_sha256,
                ),
            ),
            weather_fact_traces=(),
            observation_fact_traces=(),
            profile_gaps=(),
            weather_associations=(),
            public_observations=(),
        )
