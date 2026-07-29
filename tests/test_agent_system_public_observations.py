"""Validation-profile ownership contracts for Decision Case Graph v1."""

from __future__ import annotations

import json
import hashlib
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    BTSManifestBinding,
    BTSOnTimeRow,
    DecisionCaseMemberBinding,
    DecisionContextEvent,
    EvidenceCard,
    EvidenceClaim,
    GraphPatchBlock,
    GraphPatchLine,
    SourceFamily,
    SourceSnapshot,
    SourceSnapshotRegistry,
    ValidatedFact,
    WeatherContextBundle,
)
from aviation_agentic_ai.agent_system.bts_outcomes import build_bts_outcome_summaries
from aviation_agentic_ai.agent_system.context_artifacts import (
    read_observation_derivations,
    read_observation_fact_traces,
    read_reconstruction_trace,
    write_observation_derivations,
    write_observation_fact_traces,
    write_reconstruction_trace,
)
from aviation_agentic_ai.agent_system.formal_graph import validate_graph_patch
from aviation_agentic_ai.agent_system.materialize import (
    FormalPublication,
    FormalPublicationBlocked,
    Neo4jLoadBlocked,
    load_validated_facts_neo4j,
    materialize_formal_publication,
    materialize_validated_facts,
    run_formal_publication_kernel,
    validate_fact_publication,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.validation_profiles import (
    DEFAULT_PUBLIC_OBSERVATION_PROFILE_PATH,
    DEFAULT_WEATHER_PROFILE_PATH,
    ValidationProfileRef,
    ValidationProfileRegistry,
    load_validation_profile_registry,
    validate_fact_for_publication,
)
from aviation_agentic_ai.agent_system.public_observations import (
    build_bts_observation_facts,
)
from aviation_agentic_ai.agent_system.decision_case_graph import (
    build_decision_case_graph,
    prepare_decision_case_reconstruction,
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


def _copy_weather_profile(tmp_path: Path) -> Path:
    payload = json.loads(Path(DEFAULT_WEATHER_PROFILE_PATH).read_text())
    path = tmp_path / "weather-profile.json"
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
        "source_snapshot": SourceSnapshotRegistry(
            snapshots=(snapshot,)
        ),
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
        "decision_case_core_slice_v1",
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


@pytest.mark.parametrize(
    ("field", "malformed_value"),
    [
        ("kind", 7),
        ("label", ["not", "a", "string"]),
    ],
)
def test_registry_rejects_non_string_mapping_metadata(
    tmp_path: Path,
    field: str,
    malformed_value: object,
) -> None:
    """Damaged mapping metadata must fail closed instead of being discarded."""

    path = _copy_public_profile(tmp_path)
    payload = json.loads(path.read_text())
    payload["property_mappings"]["sosa:hasResult"][field] = malformed_value
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="malformed property mapping"):
        _registry(public_observation_profile_path=path)


def test_registry_preserves_valid_property_mapping_kind() -> None:
    """Later writers must receive the declared property kind unchanged."""

    registry = _registry()
    public_ref = next(
        ref
        for ref in registry.refs
        if ref.layer == "public_operational_observation"
    )

    assert (
        registry.resolve(public_ref).property_mappings["sosa:hasResult"]["kind"]
        == "object"
    )


def test_registry_rejects_non_string_list_mapping_metadata(tmp_path: Path) -> None:
    """List-form profile mappings must not discard damaged metadata either."""

    path = _copy_weather_profile(tmp_path)
    payload = json.loads(path.read_text())
    payload["classes"][0]["label"] = 7
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="malformed profile mapping"):
        _registry(weather_profile_path=path)


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


def _observation_input(*, nasr_airport_codes: bool = False) -> dict[str, object]:
    event = DecisionContextEvent(
        run_id="run:observation-test",
        event_id="urn:aviation-agentic-ai:event:observation-test",
        advisory_source_id="advisory:observation-test",
        advisory_issued_at=datetime(2026, 5, 19, 20, tzinfo=UTC),
        operational_start=datetime(2026, 5, 19, 21, tzinfo=UTC),
        operational_end=datetime(2026, 5, 19, 22, tzinfo=UTC),
    )
    facility = CanonicalEntity(
        entity_id="urn:aviation-agentic-ai:facility:airport:KJFK",
        entity_type=EntityType.AIRPORT,
        preferred_label="John F Kennedy International Airport",
        codes=(
            [
                CodeValue(scheme="FAA", value="JFK"),
                CodeValue(scheme="ICAO", value="KJFK"),
            ]
            if nasr_airport_codes
            else [
                CodeValue(scheme="IATA", value="JFK"),
                CodeValue(scheme="ICAO", value="KJFK"),
            ]
        ),
    )
    arrivals = (
        datetime(2026, 5, 19, 20, tzinfo=UTC),
        datetime(2026, 5, 19, 21, 30, tzinfo=UTC),
        datetime(2026, 5, 19, 23, tzinfo=UTC),
    )
    rows = [
        BTSOnTimeRow(
            row_id=f"bts-row:{index}",
            FlightDate="2026-05-19",
            DOT_ID_Reporting_Airline=1,
            Reporting_Airline="AA",
            IATA_CODE_Reporting_Airline="AA",
            Flight_Number_Reporting_Airline=index,
            OriginAirportSeqID=1,
            DestAirportSeqID=2,
            CRSDepTime=1800,
            Origin="ORD",
            Dest="JFK",
            CRSArrTime=2000,
            CRSElapsedTime=120,
            scheduled_arrival_utc=arrival,
            Cancelled=0,
            Diverted=0,
            ArrDelay=None if index == 1 else float(index),
            ArrDel15=0,
            WeatherDelay=None,
            NASDelay=0.0,
        )
        for index, arrival in enumerate(arrivals, 1)
    ]
    content = "".join(
        json.dumps(
            row.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for row in sorted(rows, key=lambda item: item.row_id)
    )
    source_id = "bts_on_time:test"
    source_sha = hashlib.sha256(content.encode()).hexdigest()
    advisory_content = "GS 123"
    snapshot_registry = SourceSnapshotRegistry(
        snapshots=(
            SourceSnapshot(
                source_id=event.advisory_source_id,
                family=SourceFamily.ATCSCC_ADVISORY,
                content=advisory_content,
                content_sha256=hashlib.sha256(advisory_content.encode()).hexdigest(),
                snapshot_timestamp="2026-07-27T00:00:00+00:00",
            ),
            SourceSnapshot(
                source_id=source_id,
                family=SourceFamily.BTS_ON_TIME,
                content=content,
                content_sha256=source_sha,
                snapshot_timestamp="2026-07-27T00:00:00+00:00",
            ),
        )
    )
    profile_registry = _registry()
    public_profile = next(
        profile
        for profile in profile_registry.profiles
        if profile.ref.layer == "public_operational_observation"
    )
    assert public_profile.aggregation_procedure is not None
    outcome_bundle = build_bts_outcome_summaries(
        event,
        facility,
        rows,
        source_id=source_id,
        source_snapshot_sha256=source_sha,
        manifest_binding=BTSManifestBinding(
            source_id=source_id,
            archive_sha256="a" * 64,
            normalized_snapshot_sha256=source_sha,
        ),
        aggregation_procedure=public_profile.aggregation_procedure,
    )
    assert outcome_bundle.status == "ok"
    reconstruction_seed = prepare_decision_case_reconstruction(
        event,
        facility,
        WeatherContextBundle(
            status="insufficient",
            failure_reason="no Weather source was provided",
        ),
        outcome_bundle,
        snapshot_registry,
        profile_registry,
    )
    return {
        "event": event,
        "canonical_facility": facility,
        "outcome_bundle": outcome_bundle,
        "snapshot_registry": snapshot_registry,
        "profile_registry": profile_registry,
        "reconstruction_seed": reconstruction_seed,
    }


def _all_observation_facts(bundle) -> list[ValidatedFact]:
    return list(bundle.formal_facts)


def _case_core(inputs: dict[str, object], bundle):
    core = build_decision_case_graph(
        seed=inputs["reconstruction_seed"],
        members=(
            DecisionCaseMemberBinding(
                member_iri=inputs["event"].event_id,
                member_kind="event",
                source_ids=(inputs["event"].advisory_source_id,),
            ),
            *(
                DecisionCaseMemberBinding(
                    member_iri=observation_id,
                    member_kind="public_observation",
                    source_ids=("bts_on_time:test",),
                )
                for observation_id in bundle.observation_ids
            ),
        ),
        profile_registry=inputs["profile_registry"],
    )
    assert core.status == "ok", core.failure_reason
    assert core.reconstruction_trace is not None
    return core


def test_public_observation_builder_does_not_own_case_identity() -> None:
    """Removing the core builder must not let BTS recreate case identity."""

    bundle = build_bts_observation_facts(**_observation_input())

    assert bundle.status == "ok", bundle.failure_reason
    facts = _all_observation_facts(bundle)
    assert not any(
        fact.object_value
        in {
            "urn:aviation-agentic-ai:decision-case-schema:DecisionCase",
            (
                "urn:aviation-agentic-ai:decision-case-schema:"
                "DecisionCaseReconstruction"
            ),
        }
        for fact in facts
        if fact.predicate_iri
        == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    )
    assert not any(
        fact.predicate_iri
        in {
            "http://www.w3.org/ns/prov#specializationOf",
            "http://www.w3.org/ns/prov#hadMember",
        }
        for fact in facts
    )


def test_observation_builder_emits_typed_noncausal_graph_with_null_omission() -> None:
    inputs = _observation_input()
    bundle = build_bts_observation_facts(**inputs)

    assert bundle.status == "ok", bundle.failure_reason
    facts = _all_observation_facts(bundle)
    assert bundle.observation_ids
    assert {
        fact.object_value
        for fact in facts
        if fact.predicate_iri == "http://www.w3.org/ns/sosa/hasFeatureOfInterest"
    } == {inputs["canonical_facility"].entity_id}
    assert not any(
        fact.object_value == inputs["event"].event_id
        for fact in facts
        if fact.predicate_iri == "http://www.w3.org/ns/sosa/hasFeatureOfInterest"
    )
    assert len(bundle.derivations) == 3
    assert all(
        tuple(sorted(row.selected_row_ids)) == row.selected_row_ids
        for row in bundle.derivations
    )
    assert all(
        fact.validation_profile.layer == "public_operational_observation"
        for fact in facts
    )
    assert {
        fact.evidence_mode
        for fact in facts
    } == {"deterministic_derivation", "profile_definition", "system_membership"}
    assert not any("caused" in fact.predicate_iri.lower() for fact in facts)

    numeric_facts = [
        fact
        for fact in facts
        if fact.predicate_iri == "http://qudt.org/schema/qudt/numericValue"
    ]
    assert any(fact.object_value == "0" for fact in numeric_facts)
    assert not any(
        trace.metric_key == "mean_arrival_delay_minutes"
        and trace.canonical_value is None
        for trace in bundle.fact_traces
    )
    assert all(trace.canonical_value is not None for trace in bundle.fact_traces)
    assert any(
        fact.object_value == "http://qudt.org/vocab/unit/NUM"
        for fact in facts
        if fact.predicate_iri == "http://qudt.org/schema/qudt/unit"
    )
    assert any(
        fact.object_value == "http://qudt.org/vocab/unit/MIN"
        for fact in facts
        if fact.predicate_iri == "http://qudt.org/schema/qudt/unit"
    )
    assert any(
        fact.datatype_iri == "http://www.w3.org/2001/XMLSchema#decimal"
        and Decimal(fact.object_value) == Decimal("0")
        for fact in numeric_facts
    )


def test_observation_builder_materializes_a_nasr_faa_icao_airport() -> None:
    """The formal observation layer must reuse the NASR airport identity."""

    inputs = _observation_input(nasr_airport_codes=True)
    bundle = build_bts_observation_facts(**inputs)

    assert bundle.status == "ok", bundle.failure_reason
    assert {
        fact.object_value
        for fact in _all_observation_facts(bundle)
        if fact.predicate_iri == "http://www.w3.org/ns/sosa/hasFeatureOfInterest"
    } == {"urn:aviation-agentic-ai:facility:airport:KJFK"}


def test_observation_ids_are_stable_and_reconstruction_tracks_exact_inputs() -> None:
    inputs = _observation_input()
    first = build_bts_observation_facts(**inputs)
    second = build_bts_observation_facts(**inputs)
    assert first.model_dump_json() == second.model_dump_json()
    assert first.observation_ids == second.observation_ids

    changed_event = inputs["event"].model_copy(
        update={"event_id": "urn:aviation-agentic-ai:event:changed"}
    )
    blocked = build_bts_observation_facts(**{**inputs, "event": changed_event})
    assert blocked.status == "blocked"
    assert "event" in (blocked.failure_reason or "")


def test_observation_builder_rejects_rehashed_unknown_selected_row_ids() -> None:
    inputs = _observation_input()
    outcome = inputs["outcome_bundle"]
    seed = outcome.derivation_seeds[0]
    selected = ("bts-row:not-in-snapshot",)
    digest = hashlib.sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    derivation_payload = {
        "aggregation_procedure_checksum": seed.aggregation_procedure_checksum,
        "aggregation_procedure_id": seed.aggregation_procedure_id,
        "archive_sha256": seed.archive_sha256,
        "selected_row_ids_sha256": digest,
        "source_id": seed.source_id,
        "source_snapshot_sha256": seed.source_snapshot_sha256,
        "summary_id": seed.summary_id,
        "summary_sha256": seed.summary_sha256,
    }
    derivation_id = "bts-derivation:" + hashlib.sha256(
        json.dumps(
            derivation_payload, sort_keys=True, separators=(",", ":")
        ).encode()
    ).hexdigest()[:24]
    tampered_seed = seed.model_copy(
        update={
            "derivation_id": derivation_id,
            "selected_row_ids": selected,
            "selected_row_ids_sha256": digest,
        }
    )
    tampered = outcome.model_copy(
        update={"derivation_seeds": [tampered_seed, *outcome.derivation_seeds[1:]]}
    )

    bundle = build_bts_observation_facts(
        **{**inputs, "outcome_bundle": tampered}
    )
    assert bundle.status == "blocked"
    assert "selected row ID" in (bundle.failure_reason or "")


def test_observation_builder_rejects_rehashed_existing_row_from_wrong_phase() -> None:
    inputs = _observation_input()
    outcome = inputs["outcome_bundle"]
    baseline = next(
        seed
        for seed in outcome.derivation_seeds
        if seed.summary_id
        == next(
            summary.summary_id
            for summary in outcome.summaries
            if summary.phase == "baseline"
        )
    )
    active = next(
        seed
        for seed in outcome.derivation_seeds
        if seed.summary_id
        == next(
            summary.summary_id
            for summary in outcome.summaries
            if summary.phase == "active"
        )
    )
    assert active.selected_row_ids
    selected = (active.selected_row_ids[0],)
    digest = hashlib.sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    derivation_payload = {
        "aggregation_procedure_checksum": baseline.aggregation_procedure_checksum,
        "aggregation_procedure_id": baseline.aggregation_procedure_id,
        "archive_sha256": baseline.archive_sha256,
        "selected_row_ids_sha256": digest,
        "source_id": baseline.source_id,
        "source_snapshot_sha256": baseline.source_snapshot_sha256,
        "summary_id": baseline.summary_id,
        "summary_sha256": baseline.summary_sha256,
    }
    changed = baseline.model_copy(
        update={
            "derivation_id": "bts-derivation:"
            + hashlib.sha256(
                json.dumps(
                    derivation_payload, sort_keys=True, separators=(",", ":")
                ).encode()
            ).hexdigest()[:24],
            "selected_row_ids": selected,
            "selected_row_ids_sha256": digest,
        }
    )
    tampered = outcome.model_copy(
        update={
            "derivation_seeds": [
                changed if seed.summary_id == baseline.summary_id else seed
                for seed in outcome.derivation_seeds
            ]
        }
    )

    bundle = build_bts_observation_facts(
        **{**inputs, "outcome_bundle": tampered}
    )
    assert bundle.status == "blocked"
    assert "phase window" in (bundle.failure_reason or "")


def test_activity_derivation_evidence_refs_resolve_to_fact_traces() -> None:
    bundle = build_bts_observation_facts(**_observation_input())
    assert bundle.status == "ok"
    trace_ids = {trace.fact_id for trace in bundle.fact_traces}

    activity_facts = [
        fact
        for fact in bundle.formal_facts
        if fact.subject_class_iri == "http://www.w3.org/ns/prov#Activity"
    ]
    assert activity_facts
    assert all(
        fact.evidence_mode == "deterministic_derivation"
        and fact.evidence_ref in trace_ids
        for fact in activity_facts
    )


def test_observation_artifacts_are_byte_stable_and_strict(tmp_path: Path) -> None:
    inputs = _observation_input()
    bundle = build_bts_observation_facts(**inputs)
    assert bundle.status == "ok"
    core = _case_core(inputs, bundle)
    reconstruction_trace = core.reconstruction_trace
    derivation_path = write_observation_derivations(tmp_path, bundle.derivations)
    trace_path = write_observation_fact_traces(tmp_path, bundle.fact_traces)
    reconstruction_path = write_reconstruction_trace(
        tmp_path, reconstruction_trace
    )
    before = {
        path.name: path.read_bytes()
        for path in (derivation_path, trace_path, reconstruction_path)
    }

    assert read_observation_derivations(derivation_path) == bundle.derivations
    assert read_observation_fact_traces(trace_path) == bundle.fact_traces
    assert read_reconstruction_trace(reconstruction_path) == reconstruction_trace
    write_observation_derivations(tmp_path, bundle.derivations)
    write_observation_fact_traces(tmp_path, bundle.fact_traces)
    write_reconstruction_trace(tmp_path, reconstruction_trace)
    assert before == {
        path.name: path.read_bytes()
        for path in (derivation_path, trace_path, reconstruction_path)
    }

    derivation_path.write_text(
        derivation_path.read_text() + derivation_path.read_text().splitlines()[0] + "\n"
    )
    with pytest.raises(ValueError, match="duplicate"):
        read_observation_derivations(derivation_path)


def test_multi_profile_materialization_preserves_explicit_projection_and_audit_metadata(
    tmp_path: Path,
) -> None:
    inputs = _observation_input()
    bundle = build_bts_observation_facts(**inputs)
    assert bundle.status == "ok"
    core = _case_core(inputs, bundle)
    facts = [*bundle.formal_facts, *core.formal_facts]

    first = materialize_validated_facts(
        facts=facts,
        profile_registry=inputs["profile_registry"],
        source_snapshot=inputs["snapshot_registry"],
        observation_fact_traces=bundle.fact_traces,
        reconstruction_trace=core.reconstruction_trace,
        output_dir=tmp_path / "first",
    )
    second = materialize_validated_facts(
        facts=facts,
        profile_registry=inputs["profile_registry"],
        source_snapshot=inputs["snapshot_registry"],
        observation_fact_traces=bundle.fact_traces,
        reconstruction_trace=core.reconstruction_trace,
        output_dir=tmp_path / "second",
    )

    rows = [
        json.loads(line)
        for line in Path(first.jsonl_path).read_text().splitlines()
        if line
    ]
    assert rows
    assert {row["validation_layer"] for row in rows} == {
        "decision_case_core",
        "public_operational_observation",
    }
    assert all(row["evidence_mode"] and row["evidence_ref"] for row in rows)
    nodes = [
        json.loads(line)
        for line in Path(first.nodes_path).read_text().splitlines()
        if line
    ]
    relationships = [
        json.loads(line)
        for line in Path(first.relationships_path).read_text().splitlines()
        if line
    ]
    assert {
        "DecisionCase",
        "DecisionCaseReconstruction",
        "Observation",
        "ObservationResult",
        "TimeInterval",
        "TimeInstant",
        "ObservationPhase",
        "ObservableProperty",
        "Unit",
        "AggregationActivity",
        "ObservationProcedure",
        "Facility",
        "AviationEvent",
        "SourceRecord",
    }.issubset({node["label"] for node in nodes})
    assert {
        "HAS_MEMBER",
        "SPECIALIZATION_OF",
        "HAS_FEATURE_OF_INTEREST",
        "OBSERVED_PROPERTY",
        "PHENOMENON_TIME",
        "HAS_RESULT",
        "USED_PROCEDURE",
        "HAS_BEGINNING",
        "HAS_END",
        "HAS_PHASE",
        "HAS_UNIT",
        "WAS_GENERATED_BY",
        "USED",
        "GENERATED",
        "DERIVED_FROM",
    }.issubset({relationship["type"] for relationship in relationships})
    assert all(
        relationship["properties"]["predicate_iri"]
        for relationship in relationships
    )
    for attribute in ("jsonl_path", "nodes_path", "relationships_path"):
        assert Path(getattr(first, attribute)).read_bytes() == Path(
            getattr(second, attribute)
        ).read_bytes()
    with pytest.raises(Neo4jLoadBlocked, match="credentials"):
        load_validated_facts_neo4j(
            nodes_path=first.nodes_path,
            relationships_path=first.relationships_path,
        )


def test_formal_publication_kernel_validates_without_writing_then_materializes(
    tmp_path: Path,
) -> None:
    inputs = _observation_input()
    bundle = build_bts_observation_facts(**inputs)
    assert bundle.status == "ok"
    core = _case_core(inputs, bundle)
    output_dir = tmp_path / "formal-publication"

    publication = run_formal_publication_kernel(
        facts=[*bundle.formal_facts, *core.formal_facts],
        profile_registry=inputs["profile_registry"],
        source_snapshot=inputs["snapshot_registry"],
        observation_fact_traces=bundle.fact_traces,
        reconstruction_trace=core.reconstruction_trace,
    )

    assert isinstance(publication, FormalPublication)
    assert publication.layer_fact_counts == {
        "decision_case_core": len(core.formal_facts),
        "public_operational_observation": len(bundle.formal_facts),
    }
    assert not output_dir.exists()

    materialization = materialize_formal_publication(
        publication=publication,
        profile_registry=inputs["profile_registry"],
        output_dir=output_dir,
    )

    assert materialization.fact_count == len(publication.accepted)
    assert {
        path.name
        for path in output_dir.iterdir()
    } == {
        "kg.jsonl",
        "kg.ttl",
        "neo4j_nodes.jsonl",
        "neo4j_relationships.jsonl",
    }


def test_formal_publication_kernel_blocks_before_projection_writes(
    tmp_path: Path,
) -> None:
    inputs = _observation_input()
    bundle = build_bts_observation_facts(**inputs)
    assert bundle.status == "ok"
    core = _case_core(inputs, bundle)
    trace = next(
        trace
        for trace in bundle.fact_traces
        if trace.metric_key == "scheduled_arrival_count"
    )
    corrupted = [
        fact.model_copy(update={"object_value": "999999"})
        if fact.fact_id == trace.fact_id
        else fact
        for fact in bundle.formal_facts
    ]
    output_dir = tmp_path / "blocked-publication"

    with pytest.raises(
        FormalPublicationBlocked,
        match="deterministic numeric value mismatch",
    ):
        run_formal_publication_kernel(
            facts=[*corrupted, *core.formal_facts],
            profile_registry=inputs["profile_registry"],
            source_snapshot=inputs["snapshot_registry"],
            observation_fact_traces=bundle.fact_traces,
            reconstruction_trace=core.reconstruction_trace,
        )

    assert not output_dir.exists()


def test_publication_rejects_unknown_derivation_reference_and_class() -> None:
    inputs = _observation_input()
    bundle = build_bts_observation_facts(**inputs)
    core = _case_core(inputs, bundle)
    facts = _all_observation_facts(bundle)
    derived = next(
        fact for fact in facts if fact.evidence_mode == "deterministic_derivation"
    )
    with pytest.raises(ValueError, match="deterministic"):
        validate_fact_publication(
            facts=[derived.model_copy(update={"evidence_ref": "missing-trace"})],
            profile_registry=inputs["profile_registry"],
            snapshot_registry=inputs["snapshot_registry"],
            observation_fact_traces=bundle.fact_traces,
            reconstruction_trace=core.reconstruction_trace,
        )

    definition = next(
        fact for fact in facts if fact.evidence_mode == "profile_definition"
    )
    unknown = definition.model_copy(
        update={
            "subject_class_iri": "urn:unknown:Class",
            "object_value": "urn:unknown:Class",
            "object_class_iri": "urn:unknown:Class",
        }
    )
    with pytest.raises(ValueError, match="class"):
        validate_fact_publication(
            facts=[unknown],
            profile_registry=inputs["profile_registry"],
            snapshot_registry=inputs["snapshot_registry"],
            reconstruction_trace=core.reconstruction_trace,
        )


@pytest.mark.parametrize(
    ("metric_key", "updates", "message"),
    [
        (
            "scheduled_arrival_count",
            {"object_value": "999999"},
            "deterministic numeric value mismatch",
        ),
        (
            "scheduled_arrival_count",
            {"datatype_iri": "http://www.w3.org/2001/XMLSchema#string"},
            "deterministic numeric datatype mismatch",
        ),
        (
            "mean_arrival_delay_minutes",
            {"object_value": "999999.0"},
            "deterministic numeric value mismatch",
        ),
        (
            "mean_arrival_delay_minutes",
            {"datatype_iri": "http://www.w3.org/2001/XMLSchema#integer"},
            "deterministic numeric datatype mismatch",
        ),
    ],
)
def test_publication_rejects_tampered_numeric_fact_with_stale_trace(
    metric_key: str,
    updates: dict[str, str],
    message: str,
) -> None:
    inputs = _observation_input()
    bundle = build_bts_observation_facts(**inputs)
    core = _case_core(inputs, bundle)
    trace = next(
        trace for trace in bundle.fact_traces if trace.metric_key == metric_key
    )
    numeric = next(
        fact
        for fact in _all_observation_facts(bundle)
        if fact.fact_id == trace.fact_id
    )

    with pytest.raises(ValueError, match=message):
        validate_fact_publication(
            facts=[numeric.model_copy(update=updates)],
            profile_registry=inputs["profile_registry"],
            snapshot_registry=inputs["snapshot_registry"],
            observation_fact_traces=bundle.fact_traces,
            reconstruction_trace=core.reconstruction_trace,
        )
