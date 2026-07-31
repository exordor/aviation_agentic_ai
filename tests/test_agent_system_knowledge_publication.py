"""Contracts for the general, domain-neutral knowledge publication spine."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError
import pytest

from aviation_agentic_ai.agent_system.contracts import (
    SourceFamily,
    ValidationProfileRef,
)
from aviation_agentic_ai.agent_system.knowledge_publication import (
    DeterministicDerivationRecord,
    KnowledgePublicationBatch,
    KnowledgePublicationPackage,
    KnowledgePublicationRecord,
    KnowledgeRootRecord,
    PublicationEvidenceLink,
    PublicationFactMembership,
    PublicationSourceMembership,
    stable_knowledge_publication_id,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    KnowledgeIngestionResult,
    SemanticFactRecord,
    SourceAnchorRecord,
    SourceVersionRecord,
)
from aviation_agentic_ai.utils.identifiers import stable_id


ROOT_ID = "urn:nasa:flight:1"
PUBLICATION_ID = "knowledge-publication:35e193eaa2b01c00"
PRIMARY_SOURCE = "source-version:primary"
SUPPORT_SOURCE = "source-version:support"
ANCHOR_ID = "source-anchor:558472490bf5db42"
FACT_ID = "fact:departure"
PROFILE = ValidationProfileRef(
    profile_id="profile:flight-operation-v1",
    profile_checksum="f" * 64,
    layer="flight_operation",
)


def _root(*, active_publication_id: str = PUBLICATION_ID) -> KnowledgeRootRecord:
    return KnowledgeRootRecord(
        root_id=ROOT_ID,
        root_kind="flight",
        temporal_domain_id="nasa-atmonto-2014",
        active_publication_id=active_publication_id,
    )


def _publication() -> KnowledgePublicationRecord:
    return KnowledgePublicationRecord(
        publication_id=PUBLICATION_ID,
        root_id=ROOT_ID,
        temporal_domain_id="nasa-atmonto-2014",
        primary_source_version_id=PRIMARY_SOURCE,
        formal_publication_digest="a" * 64,
    )


def _source_memberships() -> tuple[PublicationSourceMembership, ...]:
    return (
        PublicationSourceMembership(
            membership_id="publication-source:d01229f1e690d60a",
            publication_id=PUBLICATION_ID,
            source_version_id=PRIMARY_SOURCE,
            source_role="primary",
        ),
        PublicationSourceMembership(
            membership_id="publication-source:96ae14ff5756603f",
            publication_id=PUBLICATION_ID,
            source_version_id=SUPPORT_SOURCE,
            source_role="supporting",
        ),
    )


def _fact() -> SemanticFactRecord:
    return SemanticFactRecord(
        fact_id=FACT_ID,
        subject_iri="urn:nasa:flight:1",
        subject_class_iri="https://data.nasa.gov/ontologies/atmonto/ATM#Flight",
        predicate_iri="https://data.nasa.gov/ontologies/atmonto/ATM#departureAirport",
        object_kind="iri",
        object_value="urn:nasa:airport:KATL",
        object_class_iri="https://data.nasa.gov/ontologies/atmonto/NAS#Airport",
        datatype_iri=None,
        validation_profile=PROFILE,
        evidence_mode="source_text",
    )


def _fact_membership() -> PublicationFactMembership:
    return PublicationFactMembership(
        membership_id="publication-fact:cb308740d890d535",
        publication_id=PUBLICATION_ID,
        fact_id=FACT_ID,
    )


def _anchor() -> SourceAnchorRecord:
    return SourceAnchorRecord(
        source_anchor_id=ANCHOR_ID,
        source_version_id=PRIMARY_SOURCE,
        char_start=0,
        char_end=42,
        anchor_kind="full_record",
    )


def _evidence_link() -> PublicationEvidenceLink:
    return PublicationEvidenceLink(
        evidence_link_id="publication-evidence:001e140d3de492de",
        publication_id=PUBLICATION_ID,
        owner_kind="fact",
        owner_id=FACT_ID,
        source_version_id=PRIMARY_SOURCE,
        source_anchor_id=ANCHOR_ID,
        evidence_text="Flight 1 departed KATL.",
        evidence_ref="record#departure",
    )


def _package() -> KnowledgePublicationPackage:
    return KnowledgePublicationPackage(
        root=_root(),
        publication=_publication(),
        publication_sources=_source_memberships(),
        source_anchors=(_anchor(),),
        facts=(_fact(),),
        fact_memberships=(_fact_membership(),),
        evidence_links=(_evidence_link(),),
    )


def test_general_root_and_publication_have_stable_content_bound_identities() -> None:
    assert _root().root_id == ROOT_ID
    assert _publication().publication_id == PUBLICATION_ID
    assert stable_knowledge_publication_id(
        ROOT_ID,
        PRIMARY_SOURCE,
        "a" * 64,
    ) == PUBLICATION_ID

    with pytest.raises(ValidationError, match="publication identity"):
        KnowledgePublicationRecord.model_validate(
            _publication().model_dump()
            | {"formal_publication_digest": "b" * 64}
        )


def test_publication_memberships_and_evidence_links_have_stable_ids() -> None:
    assert _source_memberships()[0].membership_id == (
        "publication-source:d01229f1e690d60a"
    )
    assert _fact_membership().membership_id == "publication-fact:cb308740d890d535"
    assert _evidence_link().evidence_link_id == (
        "publication-evidence:001e140d3de492de"
    )

    with pytest.raises(ValidationError, match="evidence link identity"):
        PublicationEvidenceLink.model_validate(
            _evidence_link().model_dump() | {"evidence_ref": "record#other"}
        )


def test_derivation_identity_binds_method_parameters_inputs_and_result() -> None:
    derivation = DeterministicDerivationRecord(
        derivation_id="derivation:fd238d8765e6f01a",
        publication_id=PUBLICATION_ID,
        temporal_domain_id="nasa-atmonto-2014",
        procedure_id="nearest-weather-v1",
        procedure_checksum="b" * 64,
        normalized_parameters={"max_seconds": 1800, "boundary": "strict"},
        input_publication_ids=(PUBLICATION_ID, "knowledge-publication:weather"),
        input_source_version_ids=(PRIMARY_SOURCE, "source-version:weather"),
        input_entity_ids=("flight:1", "weather:1"),
        result_checksum="c" * 64,
        result_summary="one observation matched",
    )
    assert derivation.derivation_id == "derivation:fd238d8765e6f01a"

    with pytest.raises(ValidationError, match="derivation identity"):
        DeterministicDerivationRecord.model_validate(
            derivation.model_dump()
            | {"normalized_parameters": {"max_seconds": 1801, "boundary": "strict"}}
        )


def test_package_requires_exact_publication_fact_and_source_scope() -> None:
    package = _package()
    assert package.root.active_publication_id == package.publication.publication_id

    with pytest.raises(ValidationError, match="every publication fact"):
        KnowledgePublicationPackage.model_validate(
            package.model_dump() | {"fact_memberships": []}
        )

    with pytest.raises(ValidationError, match="outside the publication"):
        KnowledgePublicationPackage.model_validate(
            package.model_dump()
            | {
                "evidence_links": [
                        _evidence_link().model_dump()
                        | {
                            "evidence_link_id": "publication-evidence:984ac7b223892920",
                            "source_version_id": "source-version:unbound",
                        }
                ]
            }
        )


def test_package_rejects_cross_temporal_domain_publication() -> None:
    package = _package()
    with pytest.raises(ValidationError, match="temporal domain"):
        KnowledgePublicationPackage.model_validate(
            package.model_dump()
            | {
                "publication": _publication().model_dump()
                | {"temporal_domain_id": "proxy-2026"}
            }
        )


def test_source_text_fact_requires_exact_anchored_evidence() -> None:
    package = _package()
    link = _evidence_link()
    with pytest.raises(ValidationError, match="exact anchored evidence"):
        KnowledgePublicationPackage.model_validate(
            package.model_dump()
            | {
                "evidence_links": [
                    link.model_dump()
                    | {
                        "source_anchor_id": None,
                        "evidence_text": None,
                        "evidence_link_id": stable_id(
                            "publication-evidence",
                            PUBLICATION_ID,
                            "fact",
                            FACT_ID,
                            PRIMARY_SOURCE,
                            "",
                            "record#departure",
                        ),
                    }
                ]
            }
        )


def test_batch_partitions_publication_by_unique_semantic_root() -> None:
    package = _package()
    batch = KnowledgePublicationBatch(packages=(package,))
    assert batch.packages == (package,)

    with pytest.raises(ValidationError, match="unique root"):
        KnowledgePublicationBatch(packages=(package, package))


def test_generic_ingestion_result_records_deterministic_adapter_identity() -> None:
    result = KnowledgeIngestionResult(
        source_version_id=PRIMARY_SOURCE,
        adapter_id="nasa-atmonto-instance",
        adapter_version="1.0.0",
        profile_checksum="f" * 64,
        status="ok",
        root_id=ROOT_ID,
        publication_id=PUBLICATION_ID,
        reason="published",
        recorded_at=datetime(2026, 7, 31, tzinfo=timezone.utc),
    )
    assert result.adapter_id == "nasa-atmonto-instance"

    with pytest.raises(ValidationError, match="timezone-aware"):
        KnowledgeIngestionResult.model_validate(
            result.model_dump() | {"recorded_at": datetime(2026, 7, 31)}
        )


def test_store_applies_general_publication_once_through_common_spine(
    tmp_path: Path,
) -> None:
    from aviation_agentic_ai.agent_system.evidence_store import (
        AviationEvidenceStore,
    )

    def source_version(source_id: str, content: str) -> SourceVersionRecord:
        digest = hashlib.sha256(content.encode()).hexdigest()
        return SourceVersionRecord(
            source_version_id=stable_id("source-version", source_id, digest),
            source_id=source_id,
            family=SourceFamily.NASA_ATMONTO_INSTANCE,
            asset_id=None,
            content=content,
            content_sha256=digest,
            source_url=None,
            logical_time="2014-07-15T00:00:00+00:00",
            metadata={"temporal_domain_id": "nasa-atmonto-2014"},
        )

    primary = source_version("source:primary", "Flight 1 departed KATL.")
    support = source_version("source:support", "Supporting record.")
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:test",
        create=True,
    )
    try:
        store.register_source_version(primary)
        store.register_source_version(support)
        anchor = store.register_source_anchor(
            primary.source_version_id,
            char_start=0,
            char_end=len(primary.content),
        )
        publication_id = stable_knowledge_publication_id(
            ROOT_ID,
            primary.source_version_id,
            "a" * 64,
        )
        link = PublicationEvidenceLink(
            evidence_link_id=stable_id(
                "publication-evidence",
                publication_id,
                "fact",
                FACT_ID,
                primary.source_version_id,
                anchor.source_anchor_id,
                "record#departure",
            ),
            publication_id=publication_id,
            owner_kind="fact",
            owner_id=FACT_ID,
            source_version_id=primary.source_version_id,
            source_anchor_id=anchor.source_anchor_id,
            evidence_text=primary.content,
            evidence_ref="record#departure",
        )
        package = KnowledgePublicationPackage(
            root=KnowledgeRootRecord(
                root_id=ROOT_ID,
                root_kind="flight",
                temporal_domain_id="nasa-atmonto-2014",
                active_publication_id=publication_id,
            ),
            publication=KnowledgePublicationRecord(
                publication_id=publication_id,
                root_id=ROOT_ID,
                temporal_domain_id="nasa-atmonto-2014",
                primary_source_version_id=primary.source_version_id,
                formal_publication_digest="a" * 64,
            ),
            publication_sources=(
                PublicationSourceMembership(
                    membership_id=stable_id(
                        "publication-source",
                        publication_id,
                        primary.source_version_id,
                        "primary",
                    ),
                    publication_id=publication_id,
                    source_version_id=primary.source_version_id,
                    source_role="primary",
                ),
                PublicationSourceMembership(
                    membership_id=stable_id(
                        "publication-source",
                        publication_id,
                        support.source_version_id,
                        "supporting",
                    ),
                    publication_id=publication_id,
                    source_version_id=support.source_version_id,
                    source_role="supporting",
                ),
            ),
            source_anchors=(anchor,),
            facts=(_fact(),),
            fact_memberships=(
                PublicationFactMembership(
                    membership_id=stable_id(
                        "publication-fact",
                        publication_id,
                        FACT_ID,
                    ),
                    publication_id=publication_id,
                    fact_id=FACT_ID,
                ),
            ),
            evidence_links=(link,),
        )
        assert store.apply_knowledge_publication(package) == "inserted"
        assert store.apply_knowledge_publication(package) == "unchanged"
        ingestion_result = KnowledgeIngestionResult(
            source_version_id=primary.source_version_id,
            adapter_id="nasa-atmonto-instance",
            adapter_version="1.0.0",
            profile_checksum="f" * 64,
            status="ok",
            root_id=ROOT_ID,
            publication_id=publication_id,
            reason="published",
            recorded_at=datetime(2026, 7, 31, tzinfo=timezone.utc),
        )
        store.record_knowledge_ingestion_result(ingestion_result)
        assert store.get_knowledge_ingestion_result(
            source_version_id=primary.source_version_id,
            adapter_id="nasa-atmonto-instance",
            adapter_version="1.0.0",
        ) == ingestion_result
        assert store.get_knowledge_revision() == 1
        row = store._connection.execute(  # noqa: SLF001
            """
            SELECT active_publication_id
            FROM knowledge_roots
            WHERE root_id = ?
            """,
            (ROOT_ID,),
        ).fetchone()
        assert row[0] == publication_id
    finally:
        store.close()
