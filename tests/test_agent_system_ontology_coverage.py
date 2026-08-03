from __future__ import annotations

from pathlib import Path
import shutil

from aviation_agentic_ai.agent_system.ontology_coverage import (
    ATMONTO_DOMAINS,
    build_atmonto_semantic_coverage,
    load_atmonto_catalog,
    write_semantic_coverage_report,
)


ROOT = Path(__file__).resolve().parents[1]
ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
NAS = "https://data.nasa.gov/ontologies/atmonto/NAS#"


def test_catalog_reads_all_pinned_owl_modules_not_only_the_tmi_slice() -> None:
    catalog = load_atmonto_catalog(ROOT)

    assert len(catalog.classes) > 100
    assert len(catalog.object_properties) > 100
    assert len(catalog.datatype_properties) > 100
    assert ATM + "TrafficManagementInitiative" in catalog.classes
    assert NAS + "Airport" in catalog.classes
    assert ATM + "controlledNASelement" in catalog.object_properties
    assert ATM + "advisoryNumber" in catalog.datatype_properties


def test_catalog_preserves_hierarchy_signatures_and_cardinality_constraints() -> None:
    catalog = load_atmonto_catalog(ROOT)

    assert any(
        edge.subclass_iri.endswith("GroundStopTMI")
        and edge.superclass_iri.endswith("TrafficManagementInitiative")
        for edge in catalog.class_hierarchy
    )
    controlled = catalog.object_properties[ATM + "controlledNASelement"]
    assert controlled.domain_iris
    assert controlled.range_iris
    assert catalog.cardinality_constraints


def test_coverage_report_has_eight_domains_and_explicit_statuses() -> None:
    report = build_atmonto_semantic_coverage(ROOT)

    assert tuple(report["domains"]) == ATMONTO_DOMAINS
    assert report["catalog"]["class_count"] > 100
    assert report["catalog"]["object_property_count"] > 100
    assert report["catalog"]["datatype_property_count"] > 100
    assert report["coverage"]["active_term_count"] > 0
    assert report["coverage"]["planned_term_count"] > 0
    assert report["coverage"]["unsupported_term_count"] > 0
    assert set(report["coverage"]["statuses"]) == {
        "active",
        "planned",
        "unsupported",
    }
    assert set(report["domain_summary"]) == set(ATMONTO_DOMAINS)


def test_coverage_terms_have_domain_and_status() -> None:
    report = build_atmonto_semantic_coverage(ROOT)

    assert all(
        row["status"] in {"active", "planned", "unsupported"}
        and row["domains"]
        for row in report["terms"]
    )
    ground_stop = next(
        row
        for row in report["terms"]
        if row["iri"] == ATM + "GroundStopTMI"
    )
    assert ground_stop["status"] == "active"
    assert "traffic_management_initiatives" in ground_stop["domains"]


def test_coverage_report_writer_is_deterministic_and_repository_bound() -> None:
    target_dir = ROOT / "data/ontology/curated/.coverage-test"
    target_dir.mkdir(parents=True, exist_ok=True)
    try:
        first = write_semantic_coverage_report(
            target_dir / "coverage.json",
            repo_root=ROOT,
        )
        first_bytes = first.read_bytes()
        second = write_semantic_coverage_report(
            target_dir / "coverage-again.json",
            repo_root=ROOT,
        )

        assert first_bytes == second.read_bytes()
        try:
            write_semantic_coverage_report(
                "/tmp/coverage-outside-repo.json", repo_root=ROOT
            )
        except ValueError as exc:
            assert "inside the repository" in str(exc)
        else:
            raise AssertionError("outside-repository output was accepted")
    finally:
        shutil.rmtree(target_dir, ignore_errors=True)
