from __future__ import annotations

import pytest

from aviation_agentic_ai.agent_system.ontology_registry import (
    OntologySliceRequest,
    build_ontology_slice,
    load_ontology_registry,
)


GROUND_DELAY_PROGRAM = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#GroundDelayProgramTMI"
)
CONTROLLED_NAS_ELEMENT = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#controlledNASelement"
)
AIRPORT = "https://data.nasa.gov/ontologies/atmonto/NAS#Airport"


def test_slice_contains_subject_ancestors_properties_and_constraints() -> None:
    registry = load_ontology_registry()

    slice_ = build_ontology_slice(
        registry,
        OntologySliceRequest(
            subject_class_iri=GROUND_DELAY_PROGRAM,
            candidate_property_iris=(CONTROLLED_NAS_ELEMENT,),
            candidate_object_class_iris=(AIRPORT,),
            profile_id="test-profile-v1",
        ),
    )

    assert slice_.ontology_version
    assert slice_.catalog_checksum
    assert slice_.subject_class_iri == GROUND_DELAY_PROGRAM
    assert GROUND_DELAY_PROGRAM in {row.iri for row in slice_.classes}
    assert any(
        row.iri.endswith("TrafficManagementInitiative")
        for row in slice_.classes
    )
    assert CONTROLLED_NAS_ELEMENT in {row.iri for row in slice_.properties}
    assert AIRPORT in {row.iri for row in slice_.classes}
    assert slice_.constraints


def test_slice_rejects_unknown_ontology_property() -> None:
    registry = load_ontology_registry()

    with pytest.raises(ValueError, match="unknown ontology property"):
        build_ontology_slice(
            registry,
            OntologySliceRequest(
                subject_class_iri=GROUND_DELAY_PROGRAM,
                candidate_property_iris=("https://example.org/notInAtmonto",),
            ),
        )


def test_slice_is_deterministic_and_contains_only_selected_property_family() -> None:
    registry = load_ontology_registry()
    request = OntologySliceRequest(
        subject_class_iri=GROUND_DELAY_PROGRAM,
        candidate_property_iris=(CONTROLLED_NAS_ELEMENT,),
        candidate_object_class_iris=(AIRPORT,),
    )

    first = build_ontology_slice(registry, request)
    second = build_ontology_slice(registry, request)

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert {row.iri for row in first.properties} == {CONTROLLED_NAS_ELEMENT}

