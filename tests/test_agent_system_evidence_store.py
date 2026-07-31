"""Focused contracts for the persistent aviation evidence store."""

from __future__ import annotations

import hashlib
import sqlite3
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from aviation_agentic_ai.agent_system.contracts import (
    SourceFamily,
    ValidationProfileRef,
)
from aviation_agentic_ai.agent_system.ingestion_package import (
    EventFactMembership,
    EventIngestionPackage,
    IngestionAttempt,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    EventEvidenceLink,
    EventProfileGapRecord,
    EventWeatherAssociation,
    IngestionResult,
    PublicObservationRecord,
    SemanticFactRecord,
    SourceChunkRecord,
    SourceVersionRecord,
    TMIEventRecord,
    VectorIndexStateRecord,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id


SCHEMA_VERSION = "aviation-evidence-store-v1"
REQUIRED_STORE_TABLES = {
    "agent_usage",
    "event_facilities",
    "event_facts",
    "event_publications",
    "event_sources",
    "event_types",
    "evidence_links",
    "ingestion_results",
    "ingestion_runs",
    "observation_facts",
    "profile_gaps",
    "public_observations",
    "semantic_facts",
    "source_anchors",
    "source_assets",
    "source_chunks",
    "source_chunks_fts",
    "source_versions",
    "sources",
    "store_metadata",
    "tmi_events",
    "vector_index_state",
    "weather_associations",
}


def _source_version(
    source_id: str,
    content: str,
    *,
    logical_time: str | None = None,
) -> SourceVersionRecord:
    content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return SourceVersionRecord(
        source_version_id=stable_id(
            "source-version",
            source_id,
            content_sha256,
        ),
        source_id=source_id,
        family=SourceFamily.ATCSCC_ADVISORY,
        asset_id=None,
        content=content,
        content_sha256=content_sha256,
        source_url=None,
        logical_time=logical_time,
        metadata={},
    )


def _minimal_ok_attempt(
    version: SourceVersionRecord,
    *,
    event_id: str,
    publication_digest: str,
    source_anchor_id: str | None,
    evidence_text: str = "GROUND STOP",
    source_roles: dict[str, str] | None = None,
    evidence_links: tuple[EventEvidenceLink, ...] | None = None,
) -> IngestionAttempt:
    publication_id = stable_id(
        "event-publication",
        event_id,
        version.source_version_id,
        publication_digest,
    )
    fact = SemanticFactRecord(
        fact_id=f"fact:{event_id}:type",
        subject_iri=event_id,
        subject_class_iri="atm:GroundStopTMI",
        predicate_iri="rdf:type",
        object_kind="iri",
        object_value="atm:GroundStopTMI",
        object_class_iri="atm:GroundStopTMI",
        datatype_iri=None,
        validation_profile=ValidationProfileRef(
            profile_id="profile:decision:test",
            profile_checksum="a" * 64,
            layer="decision",
        ),
        evidence_mode="source_text",
    )
    links = evidence_links
    if links is None:
        links = (
            ()
            if source_anchor_id is None
            else (
                EventEvidenceLink(
                    evidence_link_id=f"evidence:{publication_id}:fact",
                    event_id=event_id,
                    publication_id=publication_id,
                    owner_kind="fact",
                    owner_id=fact.fact_id,
                    source_version_id=version.source_version_id,
                    source_anchor_id=source_anchor_id,
                    evidence_text=evidence_text,
                    evidence_ref=fact.fact_id,
                ),
            )
        )
    return IngestionAttempt(
        result=IngestionResult(
            source_version_id=version.source_version_id,
            source_id=version.source_id,
            status="ok",
            event_id=event_id,
            publication_id=publication_id,
            reason="",
            provider_call_count=0,
            tmi_family="ground_stop",
            preflight_eligible=True,
        ),
        package=_event_package(
            event=TMIEventRecord(
                event_id=event_id,
                publication_id=publication_id,
                advisory_source_id=version.source_id,
                publication_source_version_id=version.source_version_id,
                event_type_iris=("atm:GroundStopTMI",),
                facility_ids=(),
                effective_start=None,
                effective_end=None,
                issued_at=None,
                reason_status="missing",
                reason_value=None,
            ),
            publication_digest=publication_digest,
            source_roles=(
                {version.source_version_id: "advisory"}
                if source_roles is None
                else source_roles
            ),
            facts=(fact,),
            evidence_links=links,
        ),
    )


def _event_package(
    *,
    event: TMIEventRecord,
    publication_digest: str,
    source_roles: dict[str, str],
    facts: tuple[SemanticFactRecord, ...],
    evidence_links: tuple[EventEvidenceLink, ...],
    profile_gaps: tuple[EventProfileGapRecord, ...] = (),
    weather_associations: tuple[EventWeatherAssociation, ...] = (),
    public_observations: tuple[PublicObservationRecord, ...] = (),
) -> EventIngestionPackage:
    return EventIngestionPackage(
        event=event,
        formal_publication_digest=publication_digest,
        source_version_ids=tuple(sorted(source_roles)),
        source_anchors=(),
        facts=facts,
        event_fact_memberships=tuple(
            EventFactMembership(
                event_id=event.event_id,
                publication_id=event.publication_id,
                fact_id=fact.fact_id,
            )
            for fact in facts
        ),
        evidence_links=evidence_links,
        profile_gaps=profile_gaps,
        weather_associations=weather_associations,
        public_observations=public_observations,
        observation_fact_ids={
            observation.observation_id: observation.fact_ids
            for observation in public_observations
        },
    )


def test_store_creation_persists_schema_version(tmp_path: Path) -> None:
    """A missing or wrongly versioned schema must make store creation fail."""

    try:
        from aviation_agentic_ai.agent_system.evidence_store import (
            AviationEvidenceStore,
        )
    except ModuleNotFoundError:
        pytest.fail("AviationEvidenceStore is not implemented")

    root = tmp_path / "store"
    store = AviationEvidenceStore.open(
        root,
        dataset_id="dataset:test",
        create=True,
    )
    try:
        with sqlite3.connect(
            root / "aviation_evidence.sqlite3"
        ) as connection:
            metadata = dict(
                connection.execute(
                    "SELECT key, value FROM store_metadata ORDER BY key"
                ).fetchall()
            )
        assert metadata["schema_version"] == SCHEMA_VERSION
        assert metadata["dataset_id"] == "dataset:test"
    finally:
        store.close()


def test_store_creation_installs_the_v1_schema_tables(tmp_path: Path) -> None:
    """Omitting a contract table makes the v1 store incomplete."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )

    root = tmp_path / "store"
    store = AviationEvidenceStore.open(
        root,
        dataset_id="dataset:test",
        create=True,
    )
    try:
        table_names = {
            row[0]
            for row in store._connection.execute(  # noqa: SLF001
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                ORDER BY name
                """
            ).fetchall()
        }
        assert REQUIRED_STORE_TABLES <= table_names
    finally:
        store.close()


def test_store_v1_reserves_complete_index_and_agent_usage_contracts(
    tmp_path: Path,
) -> None:
    """A partial fixed schema would force an unsupported migration in I2/I3."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        vector_columns = tuple(
            row[1]
            for row in store._connection.execute(  # noqa: SLF001
                "PRAGMA table_info(vector_index_state)"
            ).fetchall()
        )
        usage_columns = tuple(
            row[1]
            for row in store._connection.execute(  # noqa: SLF001
                "PRAGMA table_info(agent_usage)"
            ).fetchall()
        )
        assert vector_columns == (
            "collection_name",
            "representation_version",
            "embedding_model_id",
            "embedding_dimension",
            "indexed_knowledge_revision",
            "document_count",
            "vector_count",
            "status",
            "updated_at",
            "failure_reason",
        )
        assert usage_columns == (
            "ingestion_run_id",
            "source_id",
            "event_id",
            "task_id",
            "role",
            "task_scope",
            "execution_mode",
            "outcome",
            "detail_status",
            "activation_reason",
            "provider_call_count",
            "tool_call_count",
            "input_tokens",
            "output_tokens",
            "provider_latency_ms",
            "tool_latency_ms",
        )
    finally:
        store.close()


def test_store_reopens_only_for_the_same_dataset(tmp_path: Path) -> None:
    """A store opened for another dataset must not expose the first dataset."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )

    root = tmp_path / "store"
    AviationEvidenceStore.open(
        root,
        dataset_id="dataset:first",
        create=True,
    ).close()

    reopened = AviationEvidenceStore.open(root, dataset_id="dataset:first")
    reopened.close()

    with pytest.raises(ValueError, match="dataset"):
        AviationEvidenceStore.open(root, dataset_id="dataset:other")


def test_registers_exact_advisory_source_version(tmp_path: Path) -> None:
    """A changed checksum or identity must not masquerade as the exact content."""

    try:
        from aviation_agentic_ai.agent_system.storage_contracts import (
            SourceVersionRecord,
        )
    except ModuleNotFoundError:
        pytest.fail("SourceVersionRecord is not implemented")
    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )

    source_id = "2026-05-19:123"
    content = "ATCSCC ADVZY 123\nGROUND STOP"
    content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
    source_version_id = stable_id(
        "source-version",
        source_id,
        content_sha256,
    )
    version = SourceVersionRecord(
        source_version_id=source_version_id,
        source_id=source_id,
        family=SourceFamily.ATCSCC_ADVISORY,
        asset_id=None,
        content=content,
        content_sha256=content_sha256,
        source_url="https://www.fly.faa.gov/adv/advADB.jsp",
        logical_time="2026-05-19T21:35:00Z",
        metadata={"advisory_number": "123"},
    )

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        assert store.register_source_version(version) == "inserted"
        assert store.get_source_version(source_version_id) == version
        assert store.get_latest_source_version(source_id) == version
    finally:
        store.close()


def test_revised_content_preserves_both_source_versions(tmp_path: Path) -> None:
    """Overwriting the first version or keeping it latest is a data-loss bug."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )

    first = _source_version(
        "2026-05-19:123",
        "ATCSCC ADVZY 123\nGROUND STOP",
        logical_time="2026-05-19T21:35:00Z",
    )
    revised = _source_version(
        "2026-05-19:123",
        "ATCSCC ADVZY 123\nGROUND STOP EXTENDED",
        logical_time="2026-05-19T22:00:00Z",
    )
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        assert store.register_source_version(first) == "inserted"
        assert store.register_source_version(revised) == "inserted"
        assert store.get_source_version(first.source_version_id) == first
        assert store.get_source_version(revised.source_version_id) == revised
        assert store.get_latest_source_version(first.source_id) == revised
    finally:
        store.close()


def test_identical_content_registration_is_a_no_op(tmp_path: Path) -> None:
    """Duplicate registration must not create or mutate a source version."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )

    version = _source_version("2026-05-19:123", "ATCSCC ADVZY 123")
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        assert store.register_source_version(version) == "inserted"
        assert store.register_source_version(version) == "existing"
        count = store._connection.execute(  # noqa: SLF001 - contract-level audit
            "SELECT COUNT(*) FROM source_versions"
        ).fetchone()[0]
        assert count == 1
    finally:
        store.close()


def test_source_anchors_are_stable_deduplicated_and_bounded(
    tmp_path: Path,
) -> None:
    """Wrong spans, duplicate rows, or unbounded reads break exact evidence."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )

    content = "WEATHER WEATHER"
    version = _source_version("2026-05-19:123", content)
    revised = _source_version("2026-05-19:123", content + " EXTENDED")
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        store.register_source_version(version)
        store.register_source_version(revised)

        full = store.register_source_anchor(
            version.source_version_id,
            char_start=0,
            char_end=len(content),
        )
        first_weather = store.register_source_anchor(
            version.source_version_id,
            char_start=0,
            char_end=7,
        )
        duplicate = store.register_source_anchor(
            version.source_version_id,
            char_start=0,
            char_end=7,
        )

        assert full.source_anchor_id == stable_id(
            "source-anchor",
            version.source_version_id,
            0,
            len(content),
        )
        assert full.anchor_kind == "full_record"
        assert first_weather.anchor_kind == "text_span"
        assert duplicate == first_weather
        assert store.get_source_anchor(first_weather.source_anchor_id) == first_weather
        assert (
            store.read_source_anchor(
                first_weather.source_anchor_id,
                source_version_id=version.source_version_id,
                max_chars=7,
            )
            == "WEATHER"
        )

        with pytest.raises(ValueError, match="limit"):
            store.read_source_anchor(
                first_weather.source_anchor_id,
                max_chars=6,
            )
        with pytest.raises(ValueError, match="source version"):
            store.read_source_anchor(
                first_weather.source_anchor_id,
                source_version_id=revised.source_version_id,
                max_chars=7,
            )
    finally:
        store.close()


def test_source_text_anchor_uses_lowest_match_and_rejects_missing_text(
    tmp_path: Path,
) -> None:
    """Choosing a later duplicate or inventing a span breaks reproducibility."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )

    version = _source_version("2026-05-19:123", "WEATHER / WEATHER")
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        store.register_source_version(version)
        anchor = store.anchor_source_text(
            version.source_version_id,
            "WEATHER",
        )
        assert (anchor.char_start, anchor.char_end) == (0, 7)
        with pytest.raises(ValueError, match="not found"):
            store.anchor_source_text(
                version.source_version_id,
                "THUNDERSTORMS",
            )
    finally:
        store.close()


def test_semantic_publication_rolls_back_when_evidence_anchor_is_invalid(
    tmp_path: Path,
) -> None:
    """A bad evidence link must not leave an event, fact, or publication behind."""

    from aviation_agentic_ai.agent_system.contracts import ValidationProfileRef
    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )
    from aviation_agentic_ai.agent_system.storage_contracts import (
        EventEvidenceLink,
        IngestionResult,
        SemanticFactRecord,
        TMIEventRecord,
    )

    version = _source_version("2026-05-19:123", "GROUND STOP")
    event_id = "urn:aviation-agentic-ai:event:test"
    publication_digest = hashlib.sha256(b"publication:test").hexdigest()
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
        event_type_iris=("atm:GroundStopTMI",),
        facility_ids=("urn:aviation-agentic-ai:facility:airport:JFK",),
        effective_start=datetime(2026, 5, 19, 21, 0, tzinfo=UTC),
        effective_end=datetime(2026, 5, 19, 22, 45, tzinfo=UTC),
        issued_at=datetime(2026, 5, 19, 20, 30, tzinfo=UTC),
        reason_status="formal",
        reason_value="weather",
    )
    profile = ValidationProfileRef(
        profile_id="profile:decision:test",
        profile_checksum="a" * 64,
        layer="decision",
    )
    fact = SemanticFactRecord(
        fact_id="fact:shared",
        subject_iri=event_id,
        subject_class_iri="atm:GroundStopTMI",
        predicate_iri="rdf:type",
        object_kind="iri",
        object_value="atm:GroundStopTMI",
        object_class_iri="atm:GroundStopTMI",
        datatype_iri=None,
        validation_profile=profile,
        evidence_mode="source_text",
    )
    result = IngestionResult(
        source_version_id=version.source_version_id,
        source_id=version.source_id,
        status="ok",
        event_id=event_id,
        publication_id=publication_id,
        reason="",
        provider_call_count=0,
        tmi_family="ground_stop",
        preflight_eligible=True,
    )
    attempt = IngestionAttempt(
        result=result,
        package=_event_package(
            event=event,
            publication_digest=publication_digest,
            source_roles={version.source_version_id: "advisory"},
            facts=(fact,),
            evidence_links=(
                EventEvidenceLink(
                    evidence_link_id="evidence:invalid-anchor",
                    event_id=event_id,
                    publication_id=publication_id,
                    owner_kind="fact",
                    owner_id=fact.fact_id,
                    source_version_id=version.source_version_id,
                    source_anchor_id="source-anchor:missing",
                    evidence_text="GROUND STOP",
                    evidence_ref=fact.fact_id,
                ),
            ),
        ),
    )

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        store.register_source_version(version)
        with pytest.raises(ValueError, match="anchor"):
            store.apply_ingestion_attempt(attempt)
        assert store.get_event(event_id) is None
        assert store.get_event_facts(event_id) == ()
        assert store.get_source_version(version.source_version_id) == version
    finally:
        store.close()


def test_source_text_fact_requires_exact_anchored_evidence(
    tmp_path: Path,
) -> None:
    """A source-text fact without an exact span is not publishable knowledge."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )

    version = _source_version("2026-05-19:123", "GROUND STOP")
    event_id = "urn:aviation-agentic-ai:event:exact-evidence"
    digest = hashlib.sha256(b"exact-evidence").hexdigest()
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        store.register_source_version(version)
        anchor = store.register_source_anchor(
            version.source_version_id,
            char_start=0,
            char_end=len(version.content),
        )
        without_link = _minimal_ok_attempt(
            version,
            event_id=event_id,
            publication_digest=digest,
            source_anchor_id=None,
        )
        with pytest.raises(ValueError, match="source-text evidence"):
            store.apply_ingestion_attempt(without_link)
        assert store.get_event(event_id) is None

        mismatched_text = _minimal_ok_attempt(
            version,
            event_id=event_id,
            publication_digest=digest,
            source_anchor_id=anchor.source_anchor_id,
            evidence_text="GROUND",
        )
        with pytest.raises(ValueError, match="evidence text"):
            store.apply_ingestion_attempt(mismatched_text)
        assert store.get_event(event_id) is None
    finally:
        store.close()


@pytest.mark.parametrize(
    "owner_kind",
    (
        "profile_gap",
        "weather_association",
        "public_observation",
    ),
)
def test_evidence_link_rejects_unknown_publication_owner(
    tmp_path: Path,
    owner_kind: str,
) -> None:
    """An event link cannot cite a publication member that does not exist."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )

    version = _source_version("2026-05-19:123", "GROUND STOP")
    event_id = f"urn:aviation-agentic-ai:event:dangling:{owner_kind}"
    digest = hashlib.sha256(owner_kind.encode("utf-8")).hexdigest()
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        store.register_source_version(version)
        anchor = store.register_source_anchor(
            version.source_version_id,
            char_start=0,
            char_end=len(version.content),
        )
        base = _minimal_ok_attempt(
            version,
            event_id=event_id,
            publication_digest=digest,
            source_anchor_id=anchor.source_anchor_id,
        )
        assert base.package is not None
        dangling = EventEvidenceLink(
            evidence_link_id=(
                f"evidence:{base.package.event.publication_id}:dangling"
            ),
            event_id=event_id,
            publication_id=base.package.event.publication_id,
            owner_kind=owner_kind,
            owner_id="owner:missing",
            source_version_id=version.source_version_id,
            source_anchor_id=anchor.source_anchor_id,
            evidence_text=version.content,
            evidence_ref="owner:missing",
        )
        with pytest.raises(ValidationError, match="owner"):
            EventIngestionPackage.model_validate(
                {
                    **base.package.model_dump(mode="python"),
                    "evidence_links": (
                        *base.package.evidence_links,
                        dangling,
                    ),
                }
            )
        assert store.get_event(event_id) is None
    finally:
        store.close()


def test_profile_gap_is_published_and_read_with_exact_source_binding(
    tmp_path: Path,
) -> None:
    """Losing the GS declared-reason gap would silently change its semantics."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )
    from aviation_agentic_ai.agent_system.storage_contracts import (
        EventProfileGapRecord,
    )

    version = _source_version(
        "2026-05-19:123",
        "GROUND STOP\nREASON: WEATHER",
    )
    event_id = "urn:aviation-agentic-ai:event:profile-gap"
    digest = hashlib.sha256(b"profile-gap").hexdigest()
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        store.register_source_version(version)
        fact_anchor = store.anchor_source_text(
            version.source_version_id,
            "GROUND STOP",
        )
        gap_anchor = store.anchor_source_text(
            version.source_version_id,
            "WEATHER",
        )
        base = _minimal_ok_attempt(
            version,
            event_id=event_id,
            publication_digest=digest,
            source_anchor_id=fact_anchor.source_anchor_id,
        )
        assert base.package is not None
        gap = EventProfileGapRecord(
            profile_gap_id=stable_id(
                "profile-gap",
                event_id,
                "impacting_condition",
                "weather",
                base.package.event.publication_id,
            ),
            event_id=event_id,
            publication_id=base.package.event.publication_id,
            field="impacting_condition",
            value="weather",
            evidence_text="WEATHER",
            reason="not_in_profile",
            source_version_id=version.source_version_id,
            source_anchor_id=gap_anchor.source_anchor_id,
            evidence_ref="profile-gap:weather",
            validation_profile=ValidationProfileRef(
                profile_id="profile:decision:test",
                profile_checksum="a" * 64,
                layer="decision",
            ),
        )
        gap_link = EventEvidenceLink(
            evidence_link_id=(
                f"evidence:{base.package.event.publication_id}:gap"
            ),
            event_id=event_id,
            publication_id=base.package.event.publication_id,
            owner_kind="profile_gap",
            owner_id=gap.profile_gap_id,
            source_version_id=version.source_version_id,
            source_anchor_id=gap_anchor.source_anchor_id,
            evidence_text="WEATHER",
            evidence_ref=gap.evidence_ref,
        )
        package = EventIngestionPackage.model_validate(
            {
                **base.package.model_dump(mode="python"),
                "event": base.package.event.model_copy(
                    update={
                        "reason_status": "profile_gap",
                        "reason_value": None,
                    }
                ).model_dump(mode="python"),
                "profile_gaps": (gap,),
                "evidence_links": (
                    *base.package.evidence_links,
                    gap_link,
                ),
            }
        )
        attempt = IngestionAttempt(result=base.result, package=package)

        assert store.apply_ingestion_attempt(attempt) == "inserted"
        assert store.get_event_profile_gaps(event_id) == (gap,)
    finally:
        store.close()


def test_events_share_semantic_fact_but_keep_evidence_links_disjoint(
    tmp_path: Path,
) -> None:
    """Fact deduplication must never merge event-scoped provenance."""

    from aviation_agentic_ai.agent_system.contracts import ValidationProfileRef
    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )
    from aviation_agentic_ai.agent_system.storage_contracts import (
        EventEvidenceLink,
        IngestionResult,
        SemanticFactRecord,
        TMIEventRecord,
    )

    first_version = _source_version("2026-05-19:123", "CTL ELEMENT: JFK")
    second_version = _source_version("2026-05-20:020", "CTL ELEMENT: JFK")
    profile = ValidationProfileRef(
        profile_id="profile:decision:test",
        profile_checksum="a" * 64,
        layer="decision",
    )
    shared_fact = SemanticFactRecord(
        fact_id="fact:facility-jfk-is-airport",
        subject_iri="urn:aviation-agentic-ai:facility:airport:JFK",
        subject_class_iri="atm:Airport",
        predicate_iri="rdf:type",
        object_kind="iri",
        object_value="atm:Airport",
        object_class_iri="atm:Airport",
        datatype_iri=None,
        validation_profile=profile,
        evidence_mode="source_text",
    )
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )

    def attempt_for(
        version: SourceVersionRecord,
        event_id: str,
        anchor_id: str,
    ) -> IngestionAttempt:
        publication_digest = hashlib.sha256(
            f"publication:{event_id}".encode("utf-8")
        ).hexdigest()
        publication_id = stable_id(
            "event-publication",
            event_id,
            version.source_version_id,
            publication_digest,
        )
        return IngestionAttempt(
            result=IngestionResult(
                source_version_id=version.source_version_id,
                source_id=version.source_id,
                status="ok",
                event_id=event_id,
                publication_id=publication_id,
                reason="",
                provider_call_count=0,
                tmi_family="ground_stop",
                preflight_eligible=True,
            ),
            package=_event_package(
                event=TMIEventRecord(
                    event_id=event_id,
                    publication_id=publication_id,
                    advisory_source_id=version.source_id,
                    publication_source_version_id=version.source_version_id,
                    event_type_iris=("atm:GroundStopTMI",),
                    facility_ids=(
                        "urn:aviation-agentic-ai:facility:airport:JFK",
                    ),
                    effective_start=None,
                    effective_end=None,
                    issued_at=None,
                    reason_status="missing",
                    reason_value=None,
                ),
                publication_digest=publication_digest,
                source_roles={version.source_version_id: "advisory"},
                facts=(shared_fact,),
                evidence_links=(
                    EventEvidenceLink(
                        evidence_link_id=f"evidence:{event_id}",
                        event_id=event_id,
                        publication_id=publication_id,
                        owner_kind="fact",
                        owner_id=shared_fact.fact_id,
                        source_version_id=version.source_version_id,
                        source_anchor_id=anchor_id,
                        evidence_text="JFK",
                        evidence_ref=shared_fact.fact_id,
                    ),
                ),
            ),
        )

    try:
        store.register_source_version(first_version)
        store.register_source_version(second_version)
        first_anchor = store.anchor_source_text(
            first_version.source_version_id,
            "JFK",
        )
        second_anchor = store.anchor_source_text(
            second_version.source_version_id,
            "JFK",
        )
        first_event_id = "urn:aviation-agentic-ai:event:first"
        second_event_id = "urn:aviation-agentic-ai:event:second"

        store.apply_ingestion_attempt(
            attempt_for(
                first_version,
                first_event_id,
                first_anchor.source_anchor_id,
            )
        )
        store.apply_ingestion_attempt(
            attempt_for(
                second_version,
                second_event_id,
                second_anchor.source_anchor_id,
            )
        )

        assert store.get_event_facts(first_event_id) == (shared_fact,)
        assert store.get_event_facts(second_event_id) == (shared_fact,)
        first_links = store.get_event_evidence(first_event_id)
        second_links = store.get_event_evidence(second_event_id)
        assert tuple(link.evidence_link_id for link in first_links) == (
            f"evidence:{first_event_id}",
        )
        assert tuple(link.evidence_link_id for link in second_links) == (
            f"evidence:{second_event_id}",
        )
        assert first_links[0].source_version_id != second_links[0].source_version_id
    finally:
        store.close()


def test_ok_attempt_requires_primary_publication_source_binding() -> None:
    """A publication must bind the immutable version that defines its identity."""

    version = _source_version("2026-05-19:123", "GROUND STOP")
    with pytest.raises(ValidationError, match="publication source"):
        _minimal_ok_attempt(
            version,
            event_id="urn:aviation-agentic-ai:event:missing-primary",
            publication_digest=hashlib.sha256(b"same-facts").hexdigest(),
            source_anchor_id="source-anchor:not-read",
            source_roles={},
        )


def test_same_semantics_from_revised_source_activates_new_publication(
    tmp_path: Path,
) -> None:
    """A new immutable source version must not be lost behind a shared digest."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )

    source_id = "2026-05-19:123"
    first_version = _source_version(source_id, "GROUND STOP")
    revised_version = _source_version(
        source_id,
        "GROUND STOP\nREMARKS: FORMAT REVISION",
    )
    event_id = "urn:aviation-agentic-ai:event:same-semantics"
    shared_digest = hashlib.sha256(b"same-formal-publication").hexdigest()
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        store.register_source_version(first_version)
        store.register_source_version(revised_version)
        first_anchor = store.anchor_source_text(
            first_version.source_version_id,
            "GROUND STOP",
        )
        revised_anchor = store.anchor_source_text(
            revised_version.source_version_id,
            "GROUND STOP",
        )
        first = _minimal_ok_attempt(
            first_version,
            event_id=event_id,
            publication_digest=shared_digest,
            source_anchor_id=first_anchor.source_anchor_id,
        )
        revised = _minimal_ok_attempt(
            revised_version,
            event_id=event_id,
            publication_digest=shared_digest,
            source_anchor_id=revised_anchor.source_anchor_id,
        )

        assert store.apply_ingestion_attempt(first) == "inserted"
        assert store.apply_ingestion_attempt(revised) == "activated"
        assert revised.package is not None
        assert first.package is not None
        assert store.get_event(event_id) == revised.package.event
        assert (
            store.get_event(
                event_id,
                publication_id=first.package.event.publication_id,
            )
            == first.package.event
        )
        assert (
            store._connection.execute(  # noqa: SLF001
                """
                SELECT COUNT(*)
                FROM event_publications
                WHERE event_id = ?
                """,
                (event_id,),
            ).fetchone()[0]
            == 2
        )
    finally:
        store.close()


def test_accepted_revision_activates_new_immutable_publication(
    tmp_path: Path,
) -> None:
    """Updating the active event must not rewrite its earlier publication."""

    from aviation_agentic_ai.agent_system.contracts import ValidationProfileRef
    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )
    from aviation_agentic_ai.agent_system.storage_contracts import (
        EventEvidenceLink,
        IngestionResult,
        SemanticFactRecord,
        TMIEventRecord,
    )

    source_id = "2026-05-19:123"
    first_version = _source_version(source_id, "GROUND STOP")
    second_version = _source_version(source_id, "GROUND STOP EXTENDED")
    event_id = "urn:aviation-agentic-ai:event:revision"
    profile = ValidationProfileRef(
        profile_id="profile:decision:test",
        profile_checksum="a" * 64,
        layer="decision",
    )
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )

    def attempt_for(
        version: SourceVersionRecord,
        *,
        end_hour: int,
        fact_id: str,
        fact_value: str,
        anchor_id: str,
    ) -> IngestionAttempt:
        publication_digest = hashlib.sha256(
            f"{version.source_version_id}:{fact_value}".encode("utf-8")
        ).hexdigest()
        publication_id = stable_id(
            "event-publication",
            event_id,
            version.source_version_id,
            publication_digest,
        )
        fact = SemanticFactRecord(
            fact_id=fact_id,
            subject_iri=event_id,
            subject_class_iri="atm:GroundStopTMI",
            predicate_iri="atm:hasEndTime",
            object_kind="literal",
            object_value=fact_value,
            object_class_iri=None,
            datatype_iri="xsd:dateTime",
            validation_profile=profile,
            evidence_mode="source_text",
        )
        return IngestionAttempt(
            result=IngestionResult(
                source_version_id=version.source_version_id,
                source_id=version.source_id,
                status="ok",
                event_id=event_id,
                publication_id=publication_id,
                reason="",
                provider_call_count=0,
                tmi_family="ground_stop",
                preflight_eligible=True,
            ),
            package=_event_package(
                event=TMIEventRecord(
                    event_id=event_id,
                    publication_id=publication_id,
                    advisory_source_id=source_id,
                    publication_source_version_id=version.source_version_id,
                    event_type_iris=("atm:GroundStopTMI",),
                    facility_ids=(
                        "urn:aviation-agentic-ai:facility:airport:JFK",
                    ),
                    effective_start=datetime(
                        2026,
                        5,
                        19,
                        21,
                        0,
                        tzinfo=UTC,
                    ),
                    effective_end=datetime(
                        2026,
                        5,
                        19,
                        end_hour,
                        0,
                        tzinfo=UTC,
                    ),
                    issued_at=datetime(
                        2026,
                        5,
                        19,
                        20,
                        30,
                        tzinfo=UTC,
                    ),
                    reason_status="missing",
                    reason_value=None,
                ),
                publication_digest=publication_digest,
                source_roles={version.source_version_id: "advisory"},
                facts=(fact,),
                evidence_links=(
                    EventEvidenceLink(
                        evidence_link_id=f"evidence:{publication_id}",
                        event_id=event_id,
                        publication_id=publication_id,
                        owner_kind="fact",
                        owner_id=fact.fact_id,
                        source_version_id=version.source_version_id,
                        source_anchor_id=anchor_id,
                        evidence_text="GROUND STOP",
                        evidence_ref=fact.fact_id,
                    ),
                ),
            ),
        )

    try:
        store.register_source_version(first_version)
        store.register_source_version(second_version)
        first_anchor = store.anchor_source_text(
            first_version.source_version_id,
            "GROUND STOP",
        )
        second_anchor = store.anchor_source_text(
            second_version.source_version_id,
            "GROUND STOP",
        )
        first = attempt_for(
            first_version,
            end_hour=22,
            fact_id="fact:end:first",
            fact_value="2026-05-19T22:00:00+00:00",
            anchor_id=first_anchor.source_anchor_id,
        )
        second = attempt_for(
            second_version,
            end_hour=23,
            fact_id="fact:end:second",
            fact_value="2026-05-19T23:00:00+00:00",
            anchor_id=second_anchor.source_anchor_id,
        )

        assert store.apply_ingestion_attempt(first) == "inserted"
        assert store.apply_ingestion_attempt(second) == "activated"
        assert second.package is not None
        assert first.package is not None
        assert store.get_event(event_id) == second.package.event
        assert (
            store.get_event(
                event_id,
                publication_id=first.package.event.publication_id,
            )
            == first.package.event
        )
        assert store.get_event_facts(event_id) == second.package.facts
        assert store.get_event_facts(
            event_id,
            publication_id=first.package.event.publication_id,
        ) == first.package.facts
    finally:
        store.close()


def test_blocked_revision_preserves_prior_accepted_publication(
    tmp_path: Path,
) -> None:
    """A blocked revision may be inspected but must not displace accepted knowledge."""

    from aviation_agentic_ai.agent_system.contracts import ValidationProfileRef
    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )
    from aviation_agentic_ai.agent_system.storage_contracts import (
        EventEvidenceLink,
        IngestionResult,
        SemanticFactRecord,
        TMIEventRecord,
    )

    source_id = "2026-05-19:123"
    accepted_version = _source_version(source_id, "GROUND STOP")
    blocked_version = _source_version(source_id, "MALFORMED REVISION")
    event_id = "urn:aviation-agentic-ai:event:blocked-revision"
    publication_digest = hashlib.sha256(b"accepted").hexdigest()
    publication_id = stable_id(
        "event-publication",
        event_id,
        accepted_version.source_version_id,
        publication_digest,
    )
    fact = SemanticFactRecord(
        fact_id="fact:type:ground-stop",
        subject_iri=event_id,
        subject_class_iri="atm:GroundStopTMI",
        predicate_iri="rdf:type",
        object_kind="iri",
        object_value="atm:GroundStopTMI",
        object_class_iri="atm:GroundStopTMI",
        datatype_iri=None,
        validation_profile=ValidationProfileRef(
            profile_id="profile:decision:test",
            profile_checksum="a" * 64,
            layer="decision",
        ),
        evidence_mode="source_text",
    )
    accepted_event = TMIEventRecord(
        event_id=event_id,
        publication_id=publication_id,
        advisory_source_id=source_id,
        publication_source_version_id=accepted_version.source_version_id,
        event_type_iris=("atm:GroundStopTMI",),
        facility_ids=(),
        effective_start=None,
        effective_end=None,
        issued_at=None,
        reason_status="missing",
        reason_value=None,
    )
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        store.register_source_version(accepted_version)
        anchor = store.anchor_source_text(
            accepted_version.source_version_id,
            "GROUND STOP",
        )
        accepted = IngestionAttempt(
            result=IngestionResult(
                source_version_id=accepted_version.source_version_id,
                source_id=source_id,
                status="ok",
                event_id=event_id,
                publication_id=publication_id,
                reason="",
                provider_call_count=0,
                tmi_family="ground_stop",
                preflight_eligible=True,
            ),
            package=_event_package(
                event=accepted_event,
                publication_digest=publication_digest,
                source_roles={
                    accepted_version.source_version_id: "advisory"
                },
                facts=(fact,),
                evidence_links=(
                    EventEvidenceLink(
                        evidence_link_id="evidence:accepted",
                        event_id=event_id,
                        publication_id=publication_id,
                        owner_kind="fact",
                        owner_id=fact.fact_id,
                        source_version_id=accepted_version.source_version_id,
                        source_anchor_id=anchor.source_anchor_id,
                        evidence_text="GROUND STOP",
                        evidence_ref=fact.fact_id,
                    ),
                ),
            ),
        )
        store.apply_ingestion_attempt(accepted)

        store.register_source_version(blocked_version)
        blocked_result = IngestionResult(
            source_version_id=blocked_version.source_version_id,
            source_id=source_id,
            status="blocked",
            event_id=None,
            publication_id=None,
            reason="parser contract failed",
            provider_call_count=0,
            tmi_family=None,
            preflight_eligible=None,
        )
        assert (
            store.apply_ingestion_attempt(
                IngestionAttempt(result=blocked_result, package=None)
            )
            == "inserted"
        )

        assert store.get_latest_source_version(source_id) == blocked_version
        assert store.get_ingestion_result(
            blocked_version.source_version_id
        ) == blocked_result
        assert store.get_event(event_id) == accepted_event
    finally:
        store.close()


def test_configured_source_assets_keep_files_external_to_sqlite(
    tmp_path: Path,
) -> None:
    """Missing assets or binary BLOB storage would break reproducible intake."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )
    from aviation_agentic_ai.agent_system.sources import discover_source_assets
    from aviation_agentic_ai.config import (
        configured_dataset_id,
        configured_store_root,
        load_yaml,
        resolve_project_path,
    )

    config = load_yaml("configs/cross_source_v1.yaml")
    assert config["snapshot_set_id"] == "cross-source-2026-05-v1"
    assert config["cohort"]["expected_record_count"] == 68
    assert config["agent_system"] == {
        "dataset_id": "cross-source-2026-05-v1",
        "storage": {
            "root": (
                "data/stores/aviation/"
                "cross-source-2026-05-v1"
            ),
            "sqlite": "aviation_evidence.sqlite3",
            "chroma": "chroma",
            "exports": "exports",
            "embedding_model": (
                "sentence-transformers/all-MiniLM-L6-v2"
            ),
        },
    }
    assert configured_dataset_id(config) == "cross-source-2026-05-v1"
    assert configured_store_root(config) == resolve_project_path(
        "data/stores/aviation/cross-source-2026-05-v1"
    )

    assets = discover_source_assets(config)
    assert tuple(asset.asset_key for asset in assets) == tuple(
        sorted(config["sources"])
    )
    pcg = next(
        asset
        for asset in assets
        if asset.asset_key == "pilot_controller_glossary"
    )
    pcg_path = resolve_project_path(pcg.local_path)
    assert pcg.byte_count == pcg_path.stat().st_size
    assert pcg.content_sha256 == hashlib.sha256(pcg_path.read_bytes()).hexdigest()
    assert pcg.asset_id == stable_id(
        "source-asset",
        pcg.asset_key,
        pcg.content_sha256,
    )

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id=config["agent_system"]["dataset_id"],
        create=True,
    )
    try:
        store.register_source_asset(pcg)
        assert store.get_source_asset(pcg.asset_id) == pcg
        columns = tuple(
            row[1]
            for row in store._connection.execute(  # noqa: SLF001
                "PRAGMA table_info(source_assets)"
            ).fetchall()
        )
        assert "content" not in columns
    finally:
        store.close()


def test_source_record_builds_exact_persistent_version() -> None:
    """Dropping asset, time, or metadata would make text records unauditable."""

    from aviation_agentic_ai.agent_system.contracts import SourceRecord
    from aviation_agentic_ai.agent_system.sources import build_source_version

    content = '{"icaoId":"KJFK","rawOb":"METAR KJFK 192051Z"}'
    record = SourceRecord(
        source_id="weather-source:metar:KJFK:20260519T205100Z:test",
        family=SourceFamily.METAR,
        content=content,
        title="METAR KJFK",
        source_url="https://connect.aviationweather.gov/data/api/",
        asset_id="source-asset:test",
        logical_time="2026-05-19T20:51:00Z",
        metadata={"station": "KJFK"},
    )

    version = build_source_version(record)
    content_sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
    assert version.source_version_id == stable_id(
        "source-version",
        record.source_id,
        content_sha256,
    )
    assert version.content == content
    assert version.content_sha256 == content_sha256
    assert version.asset_id == "source-asset:test"
    assert version.logical_time == "2026-05-19T20:51:00Z"
    assert version.metadata == {"station": "KJFK", "title": "METAR KJFK"}


def test_semantic_ingestion_attempt_rejects_source_chunks() -> None:
    """Chunk writes belong to the post-publication indexing boundary."""

    content = "GROUND STOP DUE TO THUNDERSTORMS"
    version = _source_version("2026-05-19:123", content)
    event_id = "urn:aviation-agentic-ai:event:search"
    digest = hashlib.sha256(b"publication:search").hexdigest()
    anchor_id = stable_id(
        "source-anchor",
        version.source_version_id,
        0,
        len(content),
    )
    chunk = SourceChunkRecord(
        chunk_id=stable_id(
            "source-chunk",
            version.source_version_id,
            "source_record",
            0,
            len(content),
            "aviation-source-chunk-v1",
        ),
        source_version_id=version.source_version_id,
        event_id=event_id,
        chunk_kind="source_record",
        text=content,
        char_start=0,
        char_end=len(content),
        source_anchor_id=anchor_id,
        representation_version="aviation-source-chunk-v1",
        metadata={},
    )
    attempt = _minimal_ok_attempt(
        version,
        event_id=event_id,
        publication_digest=digest,
        source_anchor_id=anchor_id,
        evidence_text=content,
    )
    with pytest.raises(ValidationError, match="chunks"):
        IngestionAttempt.model_validate(
            {
                **attempt.model_dump(mode="python"),
                "chunks": (chunk,),
            }
        )


def test_source_chunks_and_vector_state_are_persisted_as_derived_data(
    tmp_path: Path,
) -> None:
    """Chunk/index state must persist without becoming semantic publication."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )

    content = "GROUND STOP DUE TO THUNDERSTORMS"
    version = _source_version("2026-05-19:123", content)
    chunk = SourceChunkRecord(
        chunk_id=stable_id(
            "source-chunk",
            version.source_version_id,
            "source_record",
            0,
            len(content),
            "aviation-source-chunk-v1",
        ),
        source_version_id=version.source_version_id,
        event_id=None,
        chunk_kind="source_record",
        text=content,
        char_start=0,
        char_end=len(content),
        source_anchor_id=stable_id(
            "source-anchor",
            version.source_version_id,
            0,
            len(content),
        ),
        representation_version="aviation-source-chunk-v1",
        metadata={"source_id": version.source_id},
    )
    state = VectorIndexStateRecord(
        collection_name="aviation_source_chunks_v1",
        representation_version="aviation-source-chunk-v1",
        embedding_model_id="test/two-dimensional",
        embedding_dimension=2,
        indexed_knowledge_revision=1,
        document_count=1,
        vector_count=1,
        status="current",
        updated_at=datetime(2026, 5, 19, tzinfo=UTC),
        failure_reason=None,
    )
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test",
        create=True,
    )
    try:
        store.register_source_version(version)
        assert store.list_source_versions() == (version,)
        assert store.list_source_versions(current_only=True) == (version,)
        assert store.upsert_source_chunks((chunk,)) == 1
        assert store.get_knowledge_revision() == 1
        assert store.upsert_source_chunks((chunk,)) == 0
        assert store.get_knowledge_revision() == 1
        assert store.get_source_chunk(chunk.chunk_id) == chunk
        assert store.list_source_chunks() == (chunk,)
        assert store.search_source_text("THUNDERSTORMS") == (chunk,)

        store.set_vector_index_state(state)

        assert store.get_vector_index_state(state.collection_name) == state
        assert store.get_knowledge_revision() == 1
    finally:
        store.close()


def test_unknown_vector_dimension_is_reserved_for_blocked_initialization(
) -> None:
    blocked = VectorIndexStateRecord(
        collection_name="aviation_source_chunks_v1",
        representation_version="aviation-source-chunk-v1",
        embedding_model_id="test/unavailable",
        embedding_dimension=0,
        indexed_knowledge_revision=0,
        document_count=0,
        vector_count=0,
        status="blocked",
        updated_at=datetime(2026, 5, 19, tzinfo=UTC),
        failure_reason="encoder could not be initialized",
    )

    assert blocked.embedding_dimension == 0
    with pytest.raises(ValidationError, match="zero embedding dimension"):
        VectorIndexStateRecord.model_validate(
            {**blocked.model_dump(), "status": "current"}
        )


def test_source_text_search_defaults_to_latest_observed_version(
    tmp_path: Path,
) -> None:
    """Normal retrieval must not surface superseded source text."""

    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )

    original = _source_version("source:revision", "ORIGINAL GROUND STOP")
    revised = _source_version("source:revision", "REVISED GROUND STOP")

    def chunk_for(version: SourceVersionRecord) -> SourceChunkRecord:
        return SourceChunkRecord(
            chunk_id=stable_id(
                "source-chunk",
                version.source_version_id,
                "source_record",
                0,
                len(version.content),
                "aviation-source-chunk-v1",
            ),
            source_version_id=version.source_version_id,
            event_id=None,
            chunk_kind="source_record",
            text=version.content,
            char_start=0,
            char_end=len(version.content),
            source_anchor_id=stable_id(
                "source-anchor",
                version.source_version_id,
                0,
                len(version.content),
            ),
            representation_version="aviation-source-chunk-v1",
            metadata={"source_id": version.source_id},
        )

    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="test",
        create=True,
    )
    try:
        store.register_source_version(original)
        store.upsert_source_chunks((chunk_for(original),))
        store.register_source_version(revised)
        store.upsert_source_chunks((chunk_for(revised),))

        assert store.search_source_text("ORIGINAL") == ()
        assert store.search_source_text(
            "ORIGINAL",
            current_only=False,
        ) == (chunk_for(original),)
        assert store.search_source_text("REVISED") == (chunk_for(revised),)
    finally:
        store.close()


def test_event_listing_and_sources_use_active_bounded_publication(
    tmp_path: Path,
) -> None:
    """Unbounded listings or stale source bindings would expose wrong evidence."""

    from aviation_agentic_ai.agent_system.contracts import ValidationProfileRef
    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )
    from aviation_agentic_ai.agent_system.storage_contracts import (
        EventEvidenceLink,
        IngestionResult,
        SemanticFactRecord,
        TMIEventQuery,
        TMIEventRecord,
    )

    advisory = _source_version("2026-05-19:123", "GROUND STOP JFK")
    authority = _source_version("authority:jfk", "JFK IS AN AIRPORT")
    event_id = "urn:aviation-agentic-ai:event:list"
    digest = hashlib.sha256(b"publication:list").hexdigest()
    publication_id = stable_id(
        "event-publication",
        event_id,
        advisory.source_version_id,
        digest,
    )
    event = TMIEventRecord(
        event_id=event_id,
        publication_id=publication_id,
        advisory_source_id=advisory.source_id,
        publication_source_version_id=advisory.source_version_id,
        event_type_iris=("atm:GroundStopTMI",),
        facility_ids=("urn:aviation-agentic-ai:facility:airport:JFK",),
        effective_start=None,
        effective_end=None,
        issued_at=None,
        reason_status="formal",
        reason_value="weather",
    )
    fact = SemanticFactRecord(
        fact_id="fact:list:type",
        subject_iri=event_id,
        subject_class_iri="atm:GroundStopTMI",
        predicate_iri="rdf:type",
        object_kind="iri",
        object_value="atm:GroundStopTMI",
        object_class_iri="atm:GroundStopTMI",
        datatype_iri=None,
        validation_profile=ValidationProfileRef(
            profile_id="profile:decision:test",
            profile_checksum="a" * 64,
            layer="decision",
        ),
        evidence_mode="source_text",
    )
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        store.register_source_version(advisory)
        store.register_source_version(authority)
        anchor = store.anchor_source_text(
            advisory.source_version_id,
            "GROUND STOP",
        )
        store.apply_ingestion_attempt(
            IngestionAttempt(
                result=IngestionResult(
                    source_version_id=advisory.source_version_id,
                    source_id=advisory.source_id,
                    status="ok",
                    event_id=event_id,
                    publication_id=publication_id,
                    reason="",
                    provider_call_count=0,
                    tmi_family="ground_stop",
                    preflight_eligible=True,
                ),
                package=_event_package(
                    event=event,
                    publication_digest=digest,
                    source_roles={
                        advisory.source_version_id: "advisory",
                        authority.source_version_id: "facility_authority",
                    },
                    facts=(fact,),
                    evidence_links=(
                        EventEvidenceLink(
                            evidence_link_id="evidence:list",
                            event_id=event_id,
                            publication_id=publication_id,
                            owner_kind="fact",
                            owner_id=fact.fact_id,
                            source_version_id=advisory.source_version_id,
                            source_anchor_id=anchor.source_anchor_id,
                            evidence_text="GROUND STOP",
                            evidence_ref=fact.fact_id,
                        ),
                    ),
                ),
            )
        )

        page = store.find_tmi_events(
            TMIEventQuery(
                event_type_iri="atm:GroundStopTMI",
                facility_id="urn:aviation-agentic-ai:facility:airport:JFK",
                reason_status="formal",
                reason_value="weather",
                offset=0,
                limit=1,
            )
        )
        assert page.dataset_id == "dataset:test"
        assert page.total_matches == 1
        assert page.events == (event,)
        assert store.list_tmi_event_publications() == (event,)
        assert store.list_tmi_event_publications(
            active_only=True
        ) == (event,)
        assert store.get_event_sources(event_id) == tuple(
            sorted(
                (advisory, authority),
                key=lambda row: row.source_version_id,
            )
        )
    finally:
        store.close()


def test_event_weather_and_observations_read_active_publication(
    tmp_path: Path,
) -> None:
    """Cross-source records must stay publication-bound and phase-filtered."""

    from aviation_agentic_ai.agent_system.contracts import ValidationProfileRef
    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )
    from aviation_agentic_ai.agent_system.storage_contracts import (
        EventEvidenceLink,
        EventWeatherAssociation,
        IngestionResult,
        PublicObservationRecord,
        SemanticFactRecord,
        TMIEventRecord,
    )

    advisory = _source_version("2026-05-19:123", "GROUND STOP")
    weather_source = _source_version("metar:kjfk", "METAR KJFK")
    observation_source = _source_version("bts:jfk", "BTS JFK ARRIVALS")
    event_id = "urn:aviation-agentic-ai:event:context"
    digest = hashlib.sha256(b"publication:context").hexdigest()
    publication_id = stable_id(
        "event-publication",
        event_id,
        advisory.source_version_id,
        digest,
    )
    fact = SemanticFactRecord(
        fact_id="fact:context:type",
        subject_iri=event_id,
        subject_class_iri="atm:GroundStopTMI",
        predicate_iri="rdf:type",
        object_kind="iri",
        object_value="atm:GroundStopTMI",
        object_class_iri="atm:GroundStopTMI",
        datatype_iri=None,
        validation_profile=ValidationProfileRef(
            profile_id="profile:decision:test",
            profile_checksum="a" * 64,
            layer="decision",
        ),
        evidence_mode="source_text",
    )
    weather = EventWeatherAssociation(
        association_id="weather-association:test",
        event_id=event_id,
        publication_id=publication_id,
        report_id="metar-report:test",
        facility_id="urn:aviation-agentic-ai:facility:airport:JFK",
        relation_type="latest_observation_at_or_before_issue",
        selection_method="latest_at_or_before_issue",
        relevant_times={
            "observed_at": "2026-05-19T20:51:00+00:00",
        },
        source_version_id=weather_source.source_version_id,
        causal_claim=False,
    )
    observation = PublicObservationRecord(
        observation_id="observation:active:arrivals",
        event_id=event_id,
        publication_id=publication_id,
        phase="active",
        metric_key="scheduled_arrival_count",
        value=Decimal("12"),
        unit_iri="unit:count",
        fact_ids=(fact.fact_id,),
        profile_id="profile:public:test",
        profile_checksum="b" * 64,
        source_version_id=observation_source.source_version_id,
    )
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        for version in (advisory, weather_source, observation_source):
            store.register_source_version(version)
        anchor = store.anchor_source_text(
            advisory.source_version_id,
            "GROUND STOP",
        )
        store.apply_ingestion_attempt(
            IngestionAttempt(
                result=IngestionResult(
                    source_version_id=advisory.source_version_id,
                    source_id=advisory.source_id,
                    status="ok",
                    event_id=event_id,
                    publication_id=publication_id,
                    reason="",
                    provider_call_count=0,
                    tmi_family="ground_stop",
                    preflight_eligible=True,
                ),
                package=_event_package(
                    event=TMIEventRecord(
                        event_id=event_id,
                        publication_id=publication_id,
                        advisory_source_id=advisory.source_id,
                        publication_source_version_id=(
                            advisory.source_version_id
                        ),
                        event_type_iris=("atm:GroundStopTMI",),
                        facility_ids=(
                            "urn:aviation-agentic-ai:facility:airport:JFK",
                        ),
                        effective_start=None,
                        effective_end=None,
                        issued_at=None,
                        reason_status="missing",
                        reason_value=None,
                    ),
                    publication_digest=digest,
                    source_roles={
                        advisory.source_version_id: "advisory",
                        weather_source.source_version_id: "weather",
                        observation_source.source_version_id: (
                            "public_observation"
                        ),
                    },
                    facts=(fact,),
                    evidence_links=(
                        EventEvidenceLink(
                            evidence_link_id="evidence:context",
                            event_id=event_id,
                            publication_id=publication_id,
                            owner_kind="fact",
                            owner_id=fact.fact_id,
                            source_version_id=advisory.source_version_id,
                            source_anchor_id=anchor.source_anchor_id,
                            evidence_text="GROUND STOP",
                            evidence_ref=fact.fact_id,
                        ),
                    ),
                    weather_associations=(weather,),
                    public_observations=(observation,),
                ),
            )
        )

        assert store.get_event_weather(event_id) == (weather,)
        assert store.get_event_observations(
            event_id,
            phases=("active",),
        ) == (observation,)
        assert store.get_event_observations(
            event_id,
            phases=("baseline",),
        ) == ()
    finally:
        store.close()
