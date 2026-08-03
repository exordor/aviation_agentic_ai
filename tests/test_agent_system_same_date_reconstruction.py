from __future__ import annotations

from datetime import date

import pytest

from aviation_agentic_ai.agent_system.same_date_reconstruction import (
    SameDateReconstructionScope,
    SemanticFactSignature,
    compare_same_date_reconstruction,
)


def _fact(
    *,
    subject: str = "flight:F1",
    predicate: str = "atm:departureAirport",
    value: str = "nas:KJFKairport",
    source_id: str | None = None,
) -> SemanticFactSignature:
    return SemanticFactSignature(
        subject_iri=subject,
        predicate_iri=predicate,
        object_kind="iri",
        object_value=value,
        object_class_iri="nas:Airport",
        datatype_iri=None,
        source_id=source_id,
    )


def test_same_date_scope_requires_the_public_baseline_date() -> None:
    with pytest.raises(ValueError, match="baseline date"):
        SameDateReconstructionScope(
            experiment_id="same-date-v1",
            baseline_id="nasa-atmonto-plus-nyc-2014-07-15",
            sample_date=date(2026, 5, 14),
            airport_codes=("KJFK", "KEWR", "KLGA"),
            temporal_domain_id="nasa-atmonto-2014-07-15",
        )


def test_same_date_comparison_excludes_provenance_from_fact_identity() -> None:
    scope = SameDateReconstructionScope(
        experiment_id="same-date-v1",
        baseline_id="nasa-atmonto-plus-nyc-2014-07-15",
        sample_date=date(2014, 7, 15),
        airport_codes=("KJFK", "KEWR", "KLGA"),
        temporal_domain_id="nasa-atmonto-2014-07-15",
    )

    report = compare_same_date_reconstruction(
        scope=scope,
        baseline_facts=(_fact(source_id="nasa-baseline"),),
        reconstructed_facts=(_fact(source_id="raw-llm"),),
    )

    assert report.matched_fact_count == 1
    assert report.missing_fact_count == 0
    assert report.extra_fact_count == 0
    assert report.precision == 1.0
    assert report.recall == 1.0
    assert report.f1 == 1.0
    assert report.baseline_is_reference_only is True


def test_same_date_comparison_reports_missing_and_extra_facts() -> None:
    scope = SameDateReconstructionScope(
        experiment_id="same-date-v1",
        baseline_id="nasa-atmonto-plus-nyc-2014-07-15",
        sample_date=date(2014, 7, 15),
        airport_codes=("KJFK", "KEWR", "KLGA"),
        temporal_domain_id="nasa-atmonto-2014-07-15",
    )

    report = compare_same_date_reconstruction(
        scope=scope,
        baseline_facts=(
            _fact(),
            _fact(predicate="atm:arrivalAirport", value="nas:KEWRairport"),
        ),
        reconstructed_facts=(
            _fact(),
            _fact(predicate="atm:operatedBy", value="carrier:DAL"),
        ),
    )

    assert report.baseline_semantic_fact_count == 2
    assert report.reconstructed_semantic_fact_count == 2
    assert report.matched_fact_count == 1
    assert report.missing_fact_count == 1
    assert report.extra_fact_count == 1
    assert report.precision == 0.5
    assert report.recall == 0.5
    assert report.f1 == 0.5
