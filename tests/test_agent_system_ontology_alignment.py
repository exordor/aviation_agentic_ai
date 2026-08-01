from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

from aviation_agentic_ai.agent_system.ontology_alignment import (
    build_knowledge_alignment_audit,
    load_atmonto_application_profile,
    validate_atmonto_application_profile,
)
ROOT = Path(__file__).resolve().parents[1]
SCHEMA_SLICE_PATH = ROOT / "data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json"
ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"


def test_active_alignment_module_has_no_legacy_ontology_loop_dependency() -> None:
    source = (
        ROOT / "src/aviation_agentic_ai/agent_system/ontology_alignment.py"
    ).read_text(encoding="utf-8")

    assert "aviation_agentic_ai.ontology.atmonto_minimal_loop" not in source


def test_exact_iri_schema_slice_excludes_icarus_bridge_terms() -> None:
    schema_slice = json.loads(SCHEMA_SLICE_PATH.read_text(encoding="utf-8"))

    admitted = {
        str(entry["iri"])
        for category in ("classes", "object_properties", "datatype_properties")
        for entry in schema_slice[category]
    }
    assert ATM + "FlightSpec" in admitted
    assert "urn:absolute:icarus#FlightSpec" not in admitted
    assert not any(iri.startswith("urn:absolute:icarus#") for iri in admitted)


def test_admitted_class_hierarchy_has_no_dangling_endpoints() -> None:
    schema_slice = json.loads(SCHEMA_SLICE_PATH.read_text(encoding="utf-8"))
    admitted_classes = {str(entry["iri"]) for entry in schema_slice["classes"]}

    assert schema_slice["class_hierarchy"]
    assert all(
        str(row["subclass_iri"]) in admitted_classes
        and str(row["superclass_iri"]) in admitted_classes
        for row in schema_slice["class_hierarchy"]
    )


def test_application_profile_pins_sources_and_separates_overlay_values() -> None:
    profile = load_atmonto_application_profile()
    result = validate_atmonto_application_profile(profile, repo_root=ROOT)

    assert result.valid is True
    assert result.errors == ()
    assert len(profile["schema_authority"]["upstream_modules"]) == 6
    assert profile["project_overlays"] == [
        {
            "field": "impacting_condition",
            "note": "FAA source value retained outside the upstream ATMONTO enum",
            "value": "staffing",
        }
    ]

    schema_slice = json.loads(SCHEMA_SLICE_PATH.read_text(encoding="utf-8"))
    impacting_constraints = [
        row
        for row in schema_slice["class_property_constraints"]
        if row["property_iri"] == ATM + "impactingCondition"
    ]
    assert impacting_constraints
    assert all(
        "staffing" not in row.get("allowed_values", [])
        for row in impacting_constraints
    )


def test_application_profile_activates_only_exact_atmonto_tmi_terms() -> None:
    profile = load_atmonto_application_profile()
    active = profile["active_event_profiles"]

    assert [row["code"] for row in active] == ["GDP", "GS", "REROUTE"]
    assert all(
        str(row["ontology_class"]).startswith(
            "https://data.nasa.gov/ontologies/atmonto/ATM#"
        )
        for row in active
    )
    assert profile["atmgraph_alignment"]["role"] == (
        "ABox construction and cross-source query reference; not an imported ontology"
    )


def test_application_profile_rejects_an_unadmitted_atmonto_property() -> None:
    profile = deepcopy(load_atmonto_application_profile())
    profile["active_event_profiles"][0]["field_mappings"]["unknown"] = (
        ATM + "notInTheApplicationSlice"
    )

    result = validate_atmonto_application_profile(profile, repo_root=ROOT)

    assert result.valid is False
    assert result.errors == (
        "unadmitted_active_property:GDP:"
        "https://data.nasa.gov/ontologies/atmonto/ATM#notInTheApplicationSlice",
    )


def test_knowledge_alignment_audit_separates_atmonto_and_standard_terms() -> None:
    profile = SimpleNamespace(layer="decision")
    facts = [
        SimpleNamespace(
            subject_class_iri=ATM + "GroundStopTMI",
            predicate_iri=(
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
            ),
            object_class_iri=ATM + "GroundStopTMI",
            datatype_iri=None,
            validation_profile=profile,
        ),
        SimpleNamespace(
            subject_class_iri="http://www.w3.org/ns/sosa/Observation",
            predicate_iri="http://www.w3.org/ns/sosa/hasResult",
            object_class_iri="http://www.w3.org/ns/sosa/Result",
            datatype_iri=None,
            validation_profile=SimpleNamespace(
                layer="public_operational_observation"
            ),
        ),
    ]

    report = build_knowledge_alignment_audit(facts)

    assert report["report_version"] == "knowledge-alignment-audit-v1"
    assert report["formal_fact_count"] == 2
    assert report["fact_counts_by_validation_layer"] == {
        "decision": 1,
        "public_operational_observation": 1,
    }
    assert ATM + "GroundStopTMI" in report["schema_terms"]["atmonto_core"]
    assert (
        "http://www.w3.org/ns/sosa/hasResult"
        in report["schema_terms"]["external_standard_extension"]
    )
    assert report["schema_terms"]["project_extension"] == []
    assert report["unknown_formal_term_count"] == 0
    assert report["atmgraph_reference"]["verification_scope"] == (
        "declared construction principles; not namespace or instance equivalence"
    )
