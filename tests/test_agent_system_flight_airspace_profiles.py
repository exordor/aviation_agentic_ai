"""ATMONTO application-profile contracts for Flight and Airspace facts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.contracts import (
    FactTraceRow,
    SourceFamily,
    SourceSnapshot,
    SourceSnapshotRegistry,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.materialize import validate_fact_publication
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.validation_profiles import (
    ValidationProfileRegistry,
    load_validation_profile_registry,
)


ROOT = Path(__file__).resolve().parents[1]
ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
NAS = "https://data.nasa.gov/ontologies/atmonto/NAS#"
EQP = "https://data.nasa.gov/ontologies/atmonto/equipment#"
GEN = "https://data.nasa.gov/ontologies/atmonto/general#"


def _registry(**overrides: object) -> ValidationProfileRegistry:
    return load_validation_profile_registry(
        decision_guide=load_schema_guide(),
        include_flight_airspace=True,
        **overrides,
    )


def _profile(layer: str):
    return next(profile for profile in _registry().profiles if profile.ref.layer == layer)


def test_flight_airspace_profiles_are_opt_in() -> None:
    """Adding Flight profiles must not silently change existing TMI callers."""

    default = load_validation_profile_registry(decision_guide=load_schema_guide())
    expanded = _registry()

    assert tuple(profile.ref.layer for profile in default.profiles) == (
        "decision",
        "weather",
        "public_operational_observation",
    )
    assert tuple(profile.ref.layer for profile in expanded.profiles) == (
        "decision",
        "weather",
        "public_operational_observation",
        "flight_operation",
        "aeronautical_reference",
        "trajectory",
    )


def test_public_atmonto_sample_profile_exposes_local_full_tbox() -> None:
    """The public ABox compiler is bounded by the complete local TBox catalog."""

    registry = _registry(include_atmonto_public_sample=True)
    profile = next(
        item for item in registry.profiles if item.ref.layer == "atmonto_public_sample"
    )

    assert profile.ref.profile_id == "nasa_atmonto_public_sample_abox_v1"
    assert len(profile.class_mappings) == 105
    assert len(profile.property_mappings) == 280
    assert f"{ATM}Flight" in {
        mapping["iri"] for mapping in profile.class_mappings.values()
    }
    assert (
        "https://data.nasa.gov/ontologies/atmonto/data#arrivalDemand"
        not in {mapping["iri"] for mapping in profile.property_mappings.values()}
    )


def test_flight_operation_profile_uses_exact_atmonto_signatures() -> None:
    """A renamed or ad-hoc Flight term must not enter the closed profile."""

    profile = _profile("flight_operation")

    assert set(profile.class_mappings) == {
        "atm:ActualFlightRoute",
        "atm:Flight",
        "nas:AirCarrier",
        "nas:Airport",
        "eqp:Aircraft",
    }
    expected_signatures = {
        ATM + "departureAirport": ((ATM + "Flight",), (NAS + "Airport",)),
        ATM + "arrivalAirport": ((ATM + "Flight",), (NAS + "Airport",)),
        ATM + "aircraftFlown": ((ATM + "Flight",), (EQP + "Aircraft",)),
        ATM + "operatedBy": ((ATM + "Flight",), (NAS + "AirCarrier",)),
        ATM + "hasActualRoute": ((ATM + "Flight",), (ATM + "ActualFlightRoute",)),
        ATM + "actualDepartureTime": ((ATM + "Flight",), ()),
        ATM + "callSign": ((ATM + "Flight",), ()),
    }
    assert set(profile.property_mappings) == {
        "atm:departureAirport",
        "atm:arrivalAirport",
        "atm:aircraftFlown",
        "atm:operatedBy",
        "atm:hasActualRoute",
        "atm:actualDepartureTime",
        "atm:callSign",
    }
    for predicate, (domain, range_) in expected_signatures.items():
        assert profile.property_domains[predicate] == domain
        assert profile.property_ranges[predicate] == range_


def test_aeronautical_reference_profile_excludes_unmodeled_fix_types() -> None:
    """Sample-only fix classes must not be promoted beyond the checked catalog."""

    profile = _profile("aeronautical_reference")

    assert profile.class_ancestors[NAS + "Airport"] == (
        NAS + "Airport",
        ATM + "NavigationElement",
        NAS + "NASfacility",
    )
    assert profile.class_mappings["atm:NavigationFix"]["iri"] == (
        ATM + "NavigationFix"
    )
    assert "atm:LatLonFix" not in profile.class_mappings
    assert "atm:IntersectionFix" not in profile.class_mappings
    assert ATM + "LatLonFix" not in profile.class_ancestors
    assert ATM + "IntersectionFix" not in profile.class_ancestors
    assert profile.property_domains[NAS + "withinARTCC"] == (NAS + "Airport",)
    assert profile.property_ranges[NAS + "withinARTCC"] == (NAS + "ARTCC",)
    assert profile.property_domains[EQP + "hasAircraftModel"] == (EQP + "Aircraft",)
    assert profile.property_ranges[EQP + "hasAircraftModel"] == (
        EQP + "AircraftModel",
    )


def test_trajectory_profile_loads_explicit_sequence_ancestry() -> None:
    """Sequence properties must validate subclasses through profile-owned ancestry."""

    profile = _profile("trajectory")

    assert profile.class_ancestors[ATM + "ActualFlightRoute"] == (
        ATM + "ActualFlightRoute",
        GEN + "Sequence",
    )
    assert profile.class_ancestors[ATM + "AircraftTrackPoint"] == (
        ATM + "AircraftTrackPoint",
        GEN + "SequencedItem",
    )
    assert profile.property_domains[GEN + "hasSequencedItem"] == (
        GEN + "Sequence",
    )
    assert profile.property_ranges[GEN + "hasSequencedItem"] == (
        GEN + "SequencedItem",
    )
    assert profile.property_domains[ATM + "aircraftFix"] == (
        ATM + "AircraftTrackPoint",
    )
    assert profile.property_ranges[ATM + "aircraftFix"] == (
        ATM + "NavigationFix",
    )


def test_flight_airspace_profiles_have_bounded_source_policies() -> None:
    """A profile must not admit unrelated source families as formal evidence."""

    policies = {
        profile.ref.layer: profile.source_families_by_evidence_mode["source_text"]
        for profile in _registry().profiles
        if profile.ref.layer
        in {"flight_operation", "aeronautical_reference", "trajectory"}
    }

    assert policies == {
        "flight_operation": (
            SourceFamily.NASA_ATMONTO_INSTANCE,
            SourceFamily.BTS_FLIGHT_OPERATION,
        ),
        "aeronautical_reference": (
            SourceFamily.NASA_ATMONTO_INSTANCE,
            SourceFamily.NASR_AIRSPACE,
            SourceFamily.NASR_FACILITY,
            SourceFamily.FAA_AIRCRAFT_REGISTRY,
        ),
        "trajectory": (
            SourceFamily.NASA_ATMONTO_INSTANCE,
            SourceFamily.NASR_AIRSPACE,
        ),
    }


def test_explicit_class_ancestry_rejects_unadmitted_terms(tmp_path: Path) -> None:
    """A typo in profile ancestry must fail instead of weakening domain checks."""

    source = ROOT / "data/ontology/curated/atmonto_trajectory_slice.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["class_ancestors"]["atm:ActualFlightRoute"] = ["gen:UnknownSequence"]
    malformed = tmp_path / "trajectory.json"
    malformed.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="unknown class ancestor"):
        _registry(trajectory_profile_path=malformed)


def _sequence_fact(profile_ref, source_id: str) -> ValidatedFact:
    fact_id = "urn:aviation-agentic-ai:fact:route-sequence"
    evidence = "atm:Route1 gen:hasSequencedItem atm:TrackPoint1 ."
    return ValidatedFact(
        fact_id=fact_id,
        subject_iri="https://data.nasa.gov/ontologies/atmonto/flightInst#Route1",
        subject_class_iri=ATM + "ActualFlightRoute",
        predicate_iri=GEN + "hasSequencedItem",
        object_kind="iri",
        object_value=(
            "https://data.nasa.gov/ontologies/atmonto/flightInst#TrackPoint1"
        ),
        object_class_iri=ATM + "AircraftTrackPoint",
        source_ids=[source_id],
        evidence_texts=[evidence],
        validation_profile=profile_ref,
        evidence_mode="source_text",
        evidence_ref=fact_id,
    )


def _publication_inputs(family: SourceFamily):
    source_id = "nasa:flightInst:Route1"
    content = "atm:Route1 gen:hasSequencedItem atm:TrackPoint1 ."
    checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
    snapshot = SourceSnapshot(
        source_id=source_id,
        family=family,
        content=content,
        content_sha256=checksum,
    )
    trace = FactTraceRow(
        fact_id="urn:aviation-agentic-ai:fact:route-sequence",
        graph_patch_line=content,
        source_id=source_id,
        evidence_text=content,
        evidence_agent_role="deterministic_atmonto_adapter",
        source_snapshot_sha256=checksum,
    )
    return source_id, SourceSnapshotRegistry(snapshots=(snapshot,)), trace


def test_sequence_ancestry_passes_existing_publication_validation() -> None:
    """The loaded closure must make the real Kernel fact validator accept the edge."""

    registry = _registry()
    profile = next(row for row in registry.profiles if row.ref.layer == "trajectory")
    source_id, snapshots, trace = _publication_inputs(
        SourceFamily.NASA_ATMONTO_INSTANCE
    )

    validate_fact_publication(
        facts=[_sequence_fact(profile.ref, source_id)],
        profile_registry=registry,
        snapshot_registry=snapshots,
        fact_traces=(trace,),
        require_source_text_in_snapshot=True,
    )


@pytest.mark.parametrize(
    ("mutation", "expected_error"),
    [
        ({"subject_class_iri": ATM + "NavigationFix"}, "property domain"),
        ({"object_class_iri": ATM + "NavigationFix"}, "property range"),
    ],
)
def test_sequence_profile_rejects_wrong_domain_or_range(
    mutation: dict[str, str],
    expected_error: str,
) -> None:
    """An admitted but semantically wrong class must not satisfy the sequence edge."""

    registry = _registry()
    profile = next(row for row in registry.profiles if row.ref.layer == "trajectory")
    source_id, snapshots, trace = _publication_inputs(
        SourceFamily.NASA_ATMONTO_INSTANCE
    )
    fact = _sequence_fact(profile.ref, source_id).model_copy(update=mutation)

    with pytest.raises(ValueError, match=expected_error):
        validate_fact_publication(
            facts=[fact],
            profile_registry=registry,
            snapshot_registry=snapshots,
            fact_traces=(trace,),
        )


def test_trajectory_profile_rejects_unrelated_source_family() -> None:
    """METAR text cannot be repurposed as Flight trajectory evidence."""

    registry = _registry()
    profile = next(row for row in registry.profiles if row.ref.layer == "trajectory")
    source_id, snapshots, trace = _publication_inputs(SourceFamily.METAR)

    with pytest.raises(ValueError, match="source family"):
        validate_fact_publication(
            facts=[_sequence_fact(profile.ref, source_id)],
            profile_registry=registry,
            snapshot_registry=snapshots,
            fact_traces=(trace,),
        )
