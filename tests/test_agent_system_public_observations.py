"""Validation-profile ownership contracts for Decision Case Graph v1."""

from __future__ import annotations

import json
import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    DecisionContextEvent,
    EvidenceCard,
    EvidenceClaim,
    GraphPatchBlock,
    GraphPatchLine,
    SourceFamily,
    SourceSnapshot,
    SourceSnapshotRegistry,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.formal_graph import validate_graph_patch
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.validation_profiles import (
    DEFAULT_PUBLIC_OBSERVATION_PROFILE_PATH,
    LegacyValidatedFact,
    ValidationProfileRef,
    ValidationProfileRegistry,
    decode_legacy_validated_fact,
    load_validation_profile_registry,
    validate_fact_for_publication,
)
from aviation_agentic_ai.agent_system.weather_context import build_weather_context
from aviation_agentic_ai.cross_source.contracts import (
    CanonicalEntity,
    CodeValue,
    EntityType,
)


def _registry(**overrides: object) -> ValidationProfileRegistry:
    return load_validation_profile_registry(
        decision_guide=load_schema_guide(),
        **overrides,
    )


def _copy_public_profile(tmp_path: Path) -> Path:
    payload = json.loads(Path(DEFAULT_PUBLIC_OBSERVATION_PROFILE_PATH).read_text())
    path = tmp_path / "public-observation-profile.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


@pytest.fixture
def valid_graph_input() -> dict[str, object]:
    """A minimum source-bound Ground Stop patch for the real graph kernel."""

    source_id = "advisory:profile-test"
    content = "GS 123\nCTL ELEMENT: JFK\nPROBABILITY OF EXTENSION: MEDIUM"
    snapshot = SourceSnapshot(
        source_id=source_id,
        family=SourceFamily.ATCSCC_ADVISORY,
        content=content,
        content_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        snapshot_timestamp="2026-07-27T00:00:00+00:00",
    )
    event_iri = "urn:aviation-agentic-ai:event:profile-test"
    facility_iri = "urn:aviation-agentic-ai:facility:airport:KJFK"
    return {
        "block": GraphPatchBlock(
            patch_lines=[
                GraphPatchLine(subject=event_iri, predicate="rdf:type", object="atm:GroundStopTMI", source_ids=[source_id]),
                GraphPatchLine(subject=event_iri, predicate="atm:controlledNASelement", object=facility_iri, source_ids=[source_id]),
                GraphPatchLine(subject=event_iri, predicate="atm:extensionProbability", object="MEDIUM", source_ids=[source_id]),
            ]
        ),
        "event_iri": event_iri,
        "event_class": "atm:GroundStopTMI",
        "schema_guide": load_schema_guide(),
        "canonical_entities": {facility_iri: "nas:Airport"},
        "known_source_ids": {source_id},
        "evidence_cards": [
            EvidenceCard(
                agent_role="advisory",
                status=AgentStatus.RESOLVED,
                claims=[
                    EvidenceClaim(field_name="event_type", value="GS", evidence_text="GS 123", source_id=source_id),
                    EvidenceClaim(field_name="extension_probability", value="MEDIUM", evidence_text="PROBABILITY OF EXTENSION: MEDIUM", source_id=source_id),
                ],
            ),
            EvidenceCard(
                agent_role="facility",
                status=AgentStatus.RESOLVED,
                claims=[
                    EvidenceClaim(field_name="controlled_facility", value=facility_iri, evidence_text="CTL ELEMENT: JFK", source_id=source_id, canonical_ref=facility_iri),
                ],
            ),
            EvidenceCard(
                agent_role="terminology",
                status=AgentStatus.RESOLVED,
                claims=[
                    EvidenceClaim(field_name="operational_term", value="GS", ontology_target="atm:GroundStopTMI", evidence_text="GS 123", source_id=source_id),
                ],
            ),
        ],
        "source_snapshot": snapshot,
    }


@pytest.fixture
def weather_build_input() -> dict[str, object]:
    """A source-pinned METAR input for the real Weather builder."""

    metar_row = json.dumps(
        {"icaoId": "KJFK", "rawOb": "METAR KJFK 271500Z", "reportTime": "2026-07-27T15:00:00+00:00"},
        sort_keys=True,
        separators=(",", ":"),
    )
    advisory_content = '{"text":"GS 123"}'
    return {
        "event": DecisionContextEvent(
            run_id="run:profile-test",
            event_id="urn:aviation-agentic-ai:event:profile-test",
            advisory_source_id="advisory:profile-test",
            advisory_issued_at=datetime(2026, 7, 27, 15, tzinfo=UTC),
            operational_start=datetime(2026, 7, 27, 16, tzinfo=UTC),
            operational_end=datetime(2026, 7, 27, 17, tzinfo=UTC),
        ),
        "canonical_facility": CanonicalEntity(
            entity_id="urn:aviation-agentic-ai:facility:airport:KJFK",
            entity_type=EntityType.AIRPORT,
            preferred_label="John F Kennedy International Airport",
            codes=[CodeValue(scheme="ICAO", value="KJFK")],
        ),
        "snapshot_registry": SourceSnapshotRegistry(
            snapshots=(
                SourceSnapshot(source_id="advisory:profile-test", family=SourceFamily.ATCSCC_ADVISORY, content=advisory_content, content_sha256=hashlib.sha256(advisory_content.encode("utf-8")).hexdigest(), snapshot_timestamp="2026-07-27T00:00:00+00:00"),
                SourceSnapshot(source_id="metar:profile-test", family=SourceFamily.METAR, content=metar_row, content_sha256=hashlib.sha256(metar_row.encode("utf-8")).hexdigest(), snapshot_timestamp="2026-07-27T00:00:00+00:00"),
            )
        ),
    }


def test_registry_resolves_each_independent_profile_by_exact_ref() -> None:
    """Changing an ID, checksum, or layer must make profile resolution fail."""

    registry = _registry()

    assert {
        registry.require_layer(ref, ref.layer).ref.profile_id
        for ref in registry.refs
    } == {
        "nasa_atmonto_atcscc_tmi_slice",
        "nasa_atmonto_decision_context_weather_slice",
        "decision_case_public_observation_slice_v1",
    }
    for ref in registry.refs:
        assert registry.resolve(ref).ref == ref
        assert registry.require_layer(ref, ref.layer).ref == ref

    decision_ref = next(ref for ref in registry.refs if ref.layer == "decision")
    with pytest.raises(ValueError, match="checksum"):
        registry.resolve(decision_ref.model_copy(update={"profile_checksum": "0" * 64}))
    with pytest.raises(ValueError, match="layer"):
        registry.require_layer(decision_ref, "weather")
    with pytest.raises(ValueError, match="unknown"):
        registry.resolve(
            ValidationProfileRef(
                profile_id="unknown-profile",
                profile_checksum=decision_ref.profile_checksum,
                layer="decision",
            )
        )


def test_registry_rejects_duplicate_ids_malformed_mappings_and_forbidden_predicates(
    tmp_path: Path,
) -> None:
    """A duplicate or invalid profile cannot enter the immutable registry."""

    path = _copy_public_profile(tmp_path)
    payload = json.loads(path.read_text())
    payload["class_mappings"] = {"case:DecisionCase": {"label": "missing IRI"}}
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="class mapping"):
        _registry(public_observation_profile_path=path)

    path = _copy_public_profile(tmp_path)
    payload = json.loads(path.read_text())
    payload["profile_id"] = "nasa_atmonto_decision_context_weather_slice"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        _registry(public_observation_profile_path=path)

    path = _copy_public_profile(tmp_path)
    payload = json.loads(path.read_text())
    payload["property_mappings"]["arrival-demand"] = {
        "iri": "https://data.nasa.gov/ontologies/atmonto/data#arrivalDemand",
        "kind": "object",
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="forbidden"):
        _registry(public_observation_profile_path=path)


def test_registry_rejects_profile_file_changed_after_its_ref_is_pinned(tmp_path: Path) -> None:
    """The checksum ref catches a file changed after an owner pins it."""

    path = _copy_public_profile(tmp_path)
    registry = _registry(public_observation_profile_path=path)
    ref = next(ref for ref in registry.refs if ref.layer == "public_operational_observation")
    path.write_text(path.read_text() + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="checksum"):
        _registry(public_observation_profile_path=path).resolve(ref)


def test_new_fact_contract_requires_explicit_profile_ownership_and_evidence_reference() -> None:
    """Removing either ownership field makes a newly published fact invalid."""

    registry = _registry()
    decision_ref = next(ref for ref in registry.refs if ref.layer == "decision")
    payload = {
        "fact_id": "fact:1",
        "subject_iri": "urn:event:1",
        "subject_class_iri": "https://example.test/Event",
        "predicate_iri": "https://example.test/property",
        "object_kind": "literal",
        "object_value": "value",
        "source_ids": ["source:1"],
        "evidence_texts": ["value"],
        "validation_profile": decision_ref,
        "evidence_mode": "source_text",
        "evidence_ref": "fact:1",
    }
    assert validate_fact_for_publication(ValidatedFact.model_validate(payload), registry) is None

    with pytest.raises(ValidationError, match="validation_profile"):
        ValidatedFact.model_validate({key: value for key, value in payload.items() if key != "validation_profile"})
    with pytest.raises(ValueError, match="evidence_ref"):
        validate_fact_for_publication(
            ValidatedFact.model_validate({**payload, "evidence_ref": ""}), registry
        )


def test_legacy_fact_is_read_only_and_cannot_enter_new_publication() -> None:
    """The legacy adapter is decode-only, so old artifacts cannot bypass ownership."""

    registry = _registry()
    legacy = decode_legacy_validated_fact(
        {
            "fact_id": "legacy:1",
            "subject_iri": "urn:event:1",
            "subject_class_iri": "https://example.test/Event",
            "predicate_iri": "https://example.test/property",
            "object_kind": "literal",
            "object_value": "value",
            "source_ids": ["source:1"],
            "evidence_texts": ["value"],
        },
        registry=registry,
    )

    assert isinstance(legacy, LegacyValidatedFact)
    assert legacy.validation_profile.layer == "decision"
    with pytest.raises(ValueError, match="legacy"):
        validate_fact_for_publication(legacy, registry)


def test_graph_kernel_stamps_source_facts_with_decision_profile_and_trace_ref(
    valid_graph_input: dict[str, object],
) -> None:
    """The decision builder must stamp its own profile, not a global schema ID."""

    result = validate_graph_patch(**valid_graph_input)

    assert result.publishable
    assert {
        fact.validation_profile.layer for fact in result.accepted
    } == {"decision"}
    assert all(fact.evidence_mode == "source_text" for fact in result.accepted)
    assert {fact.evidence_ref for fact in result.accepted} == {
        fact.fact_id for fact in result.accepted
    }


def test_weather_builder_stamps_weather_profile_and_exact_trace_ref(
    weather_build_input: dict[str, object],
) -> None:
    """A Weather fact must own the Weather profile and cite its trace row."""

    bundle = build_weather_context(**weather_build_input)

    assert bundle.status == "ok"
    assert {fact.validation_profile.layer for fact in bundle.formal_facts} == {"weather"}
    assert all(fact.evidence_mode == "source_text" for fact in bundle.formal_facts)
    assert {fact.evidence_ref for fact in bundle.formal_facts} == {
        trace.fact_id for trace in bundle.fact_traces
    }
