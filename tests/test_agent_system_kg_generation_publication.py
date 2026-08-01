from __future__ import annotations

import hashlib

from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    EvidenceCard,
    EvidenceClaim,
    SourceFamily,
)
from aviation_agentic_ai.agent_system.kg_generation_contracts import (
    CandidateEntity,
    CandidateFact,
    CandidateFactProposal,
    GenerationEvidenceRecord,
    OntologyGenerationTask,
)
from aviation_agentic_ai.agent_system.kg_generation_validation import (
    apply_generated_publication,
    merge_candidate_fact_proposals,
    validate_and_prepare_generated_publication,
)
from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.ontology_registry import (
    OntologySliceRequest,
    build_ontology_slice,
    load_ontology_registry,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.storage_contracts import SourceVersionRecord
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)
from aviation_agentic_ai.utils.identifiers import stable_id


TMI_CLASS = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#GroundDelayProgramTMI"
)
CONTROLLED_NAS_ELEMENT = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#controlledNASelement"
)
AIRPORT = "https://data.nasa.gov/ontologies/atmonto/NAS#Airport"
SOURCE_ID = "advisory-001"
SOURCE_CONTENT = "CONTROLLED ELEMENT: KJFK"
SOURCE_VERSION_ID = stable_id(
    "source-version",
    SOURCE_ID,
    hashlib.sha256(SOURCE_CONTENT.encode("utf-8")).hexdigest(),
)


def _profile_registry():
    return load_validation_profile_registry(decision_guide=load_schema_guide())


def _task(content: str = SOURCE_CONTENT, family: SourceFamily = SourceFamily.ATCSCC_ADVISORY):
    source_version_id = stable_id(
        "source-version",
        SOURCE_ID,
        hashlib.sha256(content.encode("utf-8")).hexdigest(),
    )
    registry = load_ontology_registry()
    profile_registry = _profile_registry()
    decision_profile = next(
        profile for profile in profile_registry.profiles if profile.ref.layer == "decision"
    )
    ontology_slice = build_ontology_slice(
        registry,
        OntologySliceRequest(
            subject_class_iri=TMI_CLASS,
            candidate_property_iris=(CONTROLLED_NAS_ELEMENT,),
            candidate_object_class_iris=(AIRPORT,),
            profile_id=decision_profile.ref.profile_id,
            profile_checksum=decision_profile.ref.profile_checksum,
        ),
    )
    evidence_text = SOURCE_CONTENT
    anchor_id = stable_id("source-anchor", source_version_id, 0, len(evidence_text))
    card = EvidenceCard(
        agent_role="facility",
        status=AgentStatus.RESOLVED,
        claims=[
            EvidenceClaim(
                field_name="controlled_facility",
                value="KJFK",
                evidence_text=evidence_text,
                source_id=SOURCE_ID,
                canonical_ref="airport:KJFK",
            )
        ],
        source_ids=[SOURCE_ID],
    )
    task = OntologyGenerationTask(
        task_id="generation-task-publication",
        root_id="event:publication-001",
        temporal_domain_id="test-domain-v1",
        ontology_slice=ontology_slice,
        evidence_cards=(card,),
        evidence_bindings=(
            GenerationEvidenceRecord(
                evidence_ref="ev-facility",
                source_id=SOURCE_ID,
                source_version_id=source_version_id,
                source_anchor_id=anchor_id,
                char_start=0,
                char_end=len(evidence_text),
                evidence_text=evidence_text,
            ),
        ),
        candidate_entities=(
            CandidateEntity(
                entity_id="https://data.nasa.gov/ontologies/atmonto/NAS#KJFK",
                class_iri=AIRPORT,
                label="John F. Kennedy International Airport",
            ),
        ),
    )
    source_version = SourceVersionRecord(
        source_version_id=source_version_id,
        source_id=SOURCE_ID,
        family=family,
        asset_id=None,
        content=content,
        content_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        source_url=None,
        logical_time=None,
        metadata={},
    )
    return task, source_version, profile_registry, source_version_id


def _proposal() -> CandidateFactProposal:
    return CandidateFactProposal(
        status="accepted",
        facts=(
            CandidateFact(
                predicate_iri=CONTROLLED_NAS_ELEMENT,
                object_kind="iri",
                object_value="https://data.nasa.gov/ontologies/atmonto/NAS#KJFK",
                object_class_iri=AIRPORT,
                evidence_ref="ev-facility",
            ),
        ),
    )


def test_candidate_fact_reaches_shared_publication_kernel_and_package() -> None:
    task, source_version, profiles, source_version_id = _task()

    result = validate_and_prepare_generated_publication(
        task=task,
        proposal=_proposal(),
        profile_registry=profiles,
        source_versions=(source_version,),
        primary_source_version_id=source_version_id,
    )

    assert result.status == "ok"
    assert result.formal_publication is not None
    assert result.package is not None
    assert len(result.accepted_facts) == 1
    assert result.package.facts[0].predicate_iri == CONTROLLED_NAS_ELEMENT
    assert result.package.evidence_links[0].source_anchor_id


def test_missing_source_anchor_content_blocks_before_package_creation() -> None:
    task, source_version, profiles, source_version_id = _task(content="A different record")

    result = validate_and_prepare_generated_publication(
        task=task,
        proposal=_proposal(),
        profile_registry=profiles,
        source_versions=(source_version,),
        primary_source_version_id=source_version_id,
    )

    assert result.status == "blocked"
    assert result.package is None
    assert "anchor" in (result.reason or "")


def test_profile_gap_is_preserved_without_creating_a_formal_fact() -> None:
    task, source_version, profiles, source_version_id = _task()
    proposal = CandidateFactProposal(
        status="abstained",
        profile_gaps=(
            {
                "field": "declared_reason",
                "value": "LOCAL_CODE_NOT_IN_PROFILE",
                "evidence_ref": "ev-facility",
                "reason": "no active ATMONTO application-profile property",
            },
        ),
    )

    result = validate_and_prepare_generated_publication(
        task=task,
        proposal=proposal,
        profile_registry=profiles,
        source_versions=(source_version,),
        primary_source_version_id=source_version_id,
    )

    assert result.status == "abstained"
    assert result.package is None
    assert len(result.profile_gaps) == 1


def test_weather_source_cannot_publish_as_decision_fact() -> None:
    task, source_version, profiles, source_version_id = _task(family=SourceFamily.METAR)

    result = validate_and_prepare_generated_publication(
        task=task,
        proposal=_proposal(),
        profile_registry=profiles,
        source_versions=(source_version,),
        primary_source_version_id=source_version_id,
    )

    assert result.status == "blocked"
    assert result.package is None
    assert "source family" in (result.reason or "")


def test_incremental_duplicate_fact_keeps_one_fact_and_two_evidence_links() -> None:
    task, source_version, profiles, source_version_id = _task()
    second_content = SOURCE_CONTENT
    second_source_id = "advisory-002"
    second_version_id = stable_id(
        "source-version",
        second_source_id,
        hashlib.sha256(second_content.encode("utf-8")).hexdigest(),
    )
    second_anchor_id = stable_id(
        "source-anchor",
        second_version_id,
        0,
        len(second_content),
    )
    second_binding = GenerationEvidenceRecord(
        evidence_ref="ev-facility-2",
        source_id=second_source_id,
        source_version_id=second_version_id,
        source_anchor_id=second_anchor_id,
        char_start=0,
        char_end=len(second_content),
        evidence_text=second_content,
    )
    task = task.model_copy(
        update={
            "evidence_bindings": (*task.evidence_bindings, second_binding),
            "evidence_refs": ("ev-facility", "ev-facility-2"),
        }
    )
    duplicate_proposal = _proposal().model_copy(
        update={
            "facts": (
                *_proposal().facts,
                _proposal().facts[0].model_copy(
                    update={"evidence_ref": "ev-facility-2"}
                ),
            )
        }
    )
    second_source = SourceVersionRecord(
        source_version_id=second_version_id,
        source_id=second_source_id,
        family=SourceFamily.ATCSCC_ADVISORY,
        asset_id=None,
        content=second_content,
        content_sha256=hashlib.sha256(second_content.encode("utf-8")).hexdigest(),
        source_url=None,
        logical_time=None,
        metadata={},
    )

    result = validate_and_prepare_generated_publication(
        task=task,
        proposal=duplicate_proposal,
        profile_registry=profiles,
        source_versions=(source_version, second_source),
        primary_source_version_id=source_version_id,
    )

    assert result.status == "ok"
    assert len(result.accepted_facts) == 1
    assert result.package is not None
    assert len(result.package.evidence_links) == 2
    assert len({link.owner_id for link in result.package.evidence_links}) == 1


def test_exact_incremental_replay_rows_are_deduplicated() -> None:
    proposal = _proposal()
    merged = merge_candidate_fact_proposals([proposal, proposal])

    assert len(merged.facts) == 1
    assert merged.facts[0].evidence_ref == "ev-facility"


def test_accepted_publication_is_idempotent_in_the_semantic_store(tmp_path) -> None:
    task, source_version, profiles, source_version_id = _task()
    result = validate_and_prepare_generated_publication(
        task=task,
        proposal=_proposal(),
        profile_registry=profiles,
        source_versions=(source_version,),
        primary_source_version_id=source_version_id,
    )
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="kg-generation-test",
        create=True,
    )
    try:
        assert apply_generated_publication(store, result, (source_version,)) == "inserted"
        assert apply_generated_publication(store, result, (source_version,)) == "unchanged"
        active = store.list_active_formal_fact_bindings()
        assert len(active) == 1
        assert len(active[0].evidence_links) == 1
    finally:
        store.close()
