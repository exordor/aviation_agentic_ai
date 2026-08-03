from __future__ import annotations

from aviation_agentic_ai.agent_system.faa_order_document import (
    build_faa_order_source_package,
)
from aviation_agentic_ai.agent_system.faa_order_ontology import (
    FAA_ORDER_PROFILE_ID,
    compile_faa_order_extraction_schema,
    normalize_faa_order_entities,
)
from aviation_agentic_ai.agent_system.kg_generation_contracts import (
    EntityExtractionProposal,
    EntityMentionCandidate,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)
from aviation_agentic_ai.utils.pdf import PdfPage


def test_faa_order_profile_admits_document_evidence() -> None:
    registry = load_validation_profile_registry(
        decision_guide=load_schema_guide(),
        include_faa_order=True,
    )

    profile = next(
        profile
        for profile in registry.profiles
        if profile.ref.profile_id == FAA_ORDER_PROFILE_ID
    )

    assert profile.ref.layer == "document_reference"
    assert tuple(
        family.value
        for family in profile.source_families_by_evidence_mode["source_text"]
    ) == ("web_document",)
    assert "faa:hasParagraph" in profile.property_mappings
    assert profile.property_domains[
        "urn:aviation-agentic-ai:faa7210.3ee#hasRule"
    ] == ("urn:aviation-agentic-ai:faa7210.3ee#PolicyParagraph",)


def test_document_extraction_schema_is_compact_versioned_and_checksum_bound() -> None:
    package = build_faa_order_source_package(
        (
            PdfPage(
                page_number=410,
                text="18−10−1. POLICY\nGDP policy text.\n",
            ),
        ),
        pdf_sha256="b" * 64,
        pdf_byte_count=321,
    )

    schema = compile_faa_order_extraction_schema(package.extraction_chunks[0])

    assert schema.profile_id == FAA_ORDER_PROFILE_ID
    assert schema.profile_checksum
    assert schema.schema_checksum
    assert schema.evidence_ref == package.extraction_chunks[0].evidence_ref
    assert len(schema.classes) < 40
    assert len(schema.properties) < 30
    assert "complete ATMONTO" not in schema.prompt_schema
    assert "classes:" in schema.prompt_schema
    assert "relations:" in schema.prompt_schema


def test_document_extraction_schema_exposes_aliases_and_domain_range_constraints() -> None:
    package = build_faa_order_source_package(
        (
            PdfPage(
                page_number=410,
                text="18−10−1. POLICY\nGDP policy text.\n",
            ),
        ),
        pdf_sha256="c" * 64,
        pdf_byte_count=321,
    )

    schema = compile_faa_order_extraction_schema(package.extraction_chunks[0])
    classes = {row.iri: row for row in schema.classes}
    properties = {row.iri: row for row in schema.properties}

    gdp = next(row for row in classes.values() if row.iri.endswith("GroundDelayProgramTMI"))
    ground_stop = next(row for row in classes.values() if row.iri.endswith("GroundStopTMI"))
    mit = next(row for row in classes.values() if row.iri.endswith("MilesInTrailTMI"))
    assert "GDP" in gdp.aliases
    assert "GS" in ground_stop.aliases
    assert "MIT" in mit.aliases
    applies_to = next(row for row in properties.values() if row.iri.endswith("appliesToTMI"))
    assert applies_to.domain_iris
    assert applies_to.range_iris
    assert applies_to.description
    assert any(row.iri.endswith("mentionsEntity") for row in properties.values())
    assert any(row.iri.endswith("label") for row in properties.values())
    mentions_entity = next(
        row for row in properties.values() if row.iri.endswith("mentionsEntity")
    )
    for class_row in classes.values():
        assert {
            class_row.iri,
            *class_row.ancestor_iris,
        }.intersection(mentions_entity.range_iris), class_row.iri


def test_document_entity_identity_is_class_stable_across_ambiguous_facility_codes() -> None:
    package = build_faa_order_source_package(
        (
            PdfPage(
                page_number=410,
                text="18−10−1. POLICY\nN90 coordinates with N90.\n",
            ),
        ),
        pdf_sha256="d" * 64,
        pdf_byte_count=321,
    )
    chunk = package.extraction_chunks[0]
    schema = compile_faa_order_extraction_schema(chunk)
    artcc_iri = "https://data.nasa.gov/ontologies/atmonto/NAS#ARTCC"
    facility_iri = "https://data.nasa.gov/ontologies/atmonto/NAS#NASfacility"
    proposal = EntityExtractionProposal(
        status="accepted",
        mentions=(
            EntityMentionCandidate(
                mention_id="m1",
                surface_text="N90",
                class_iri=artcc_iri,
                evidence_ref=chunk.evidence_ref,
                concept_or_instance="instance",
                confidence=0.8,
            ),
            EntityMentionCandidate(
                mention_id="m2",
                surface_text="N90",
                class_iri=facility_iri,
                evidence_ref=chunk.evidence_ref,
                concept_or_instance="instance",
                confidence=0.8,
            ),
        ),
    )

    result = normalize_faa_order_entities(
        package,
        chunk,
        proposal,
        schema,
    )

    assert len(result.entities) == 2
    assert len({row.entity_id for row in result.entities}) == 2
    assert {row.class_iri for row in result.entities} == {artcc_iri, facility_iri}
