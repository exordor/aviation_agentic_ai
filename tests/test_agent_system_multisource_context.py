"""End-to-end contracts for deterministic Decision Context Case integration."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
import pytest

import aviation_agentic_ai.agent_system.context_artifacts as context_artifacts_module
import aviation_agentic_ai.agent_system.weather_context as weather_context_module
import aviation_agentic_ai.agent_system.workflow as workflow_module
from aviation_agentic_ai.agent_system.context_artifacts import (
    integrate_event_context,
    parse_advisory_signature,
    prepare_event_context,
)
from aviation_agentic_ai.agent_system.authority_evidence import AuthorityBuildStatus
from aviation_agentic_ai.agent_system.authority_resolution import (
    AuthorityResolutionResult,
    FacilityAuthorityResolutionInput,
    resolve_facility_authority,
)
from aviation_agentic_ai.agent_system.contracts import (
    AgentStatus,
    AgentTask,
    BTSObservationBundle,
    EvidenceCard,
    EvidenceClaim,
    FactTraceRow,
    GraphPatchBlock,
    GraphPatchLine,
    GraphValidationResult,
    PersistedProfileGap,
    SourceFamily,
    SourceRecord,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.construction_contracts import stable_contract_id
from aviation_agentic_ai.agent_system.materialize import (
    FormalPublicationBlocked,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)
from aviation_agentic_ai.agent_system.sources import (
    build_source_snapshot_registry,
    load_advisory_source,
    load_bts_context_source,
    load_weather_sources,
)
from aviation_agentic_ai.agent_system.weather_context import (
    FORECASTING_AIRPORT,
    INTERVAL_END,
    INTERVAL_START,
    METAR_STRING,
    METEOROLOGICAL_CONDITION_STATUS,
    TAF_STRING,
)
from aviation_agentic_ai.agent_system.workflow import (
    AuthoritySourceRecordRegistry,
    AuthoritySourceRegistryStatus,
    IngestContext,
    build_ingest_graph,
    run_ingest,
)
from aviation_agentic_ai.config import load_yaml
from aviation_agentic_ai.authority.contracts import (
    CanonicalEntity,
    CodeValue,
    EntityType,
)
from aviation_agentic_ai.utils.identifiers import stable_id


ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
NAS = "https://data.nasa.gov/ontologies/atmonto/NAS#"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
XSD_DATETIME = "http://www.w3.org/2001/XMLSchema#dateTime"
XSD_STRING = "http://www.w3.org/2001/XMLSchema#string"
FACILITIES = {
    "KJFK": CanonicalEntity(
        entity_id="urn:aviation-agentic-ai:facility:airport:KJFK",
        entity_type=EntityType.AIRPORT,
        preferred_label="John F Kennedy International Airport",
        codes=[
            CodeValue(scheme="IATA", value="JFK"),
            CodeValue(scheme="ICAO", value="KJFK"),
        ],
    ),
    "KEWR": CanonicalEntity(
        entity_id="urn:aviation-agentic-ai:facility:airport:KEWR",
        entity_type=EntityType.AIRPORT,
        preferred_label="Newark Liberty International Airport",
        codes=[
            CodeValue(scheme="IATA", value="EWR"),
            CodeValue(scheme="ICAO", value="KEWR"),
        ],
    ),
}

DECISION_PROFILE_REF = next(
    ref
    for ref in load_validation_profile_registry(decision_guide=load_schema_guide()).refs
    if ref.layer == "decision"
)


class _NoDeterministicModelFactory:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, tools):
        self.calls += 1
        raise AssertionError("complete deterministic cases must not construct a model")


def _fact(
    fact_id: str,
    event_id: str,
    event_class: str,
    predicate_iri: str,
    object_value: str,
    *,
    object_kind: str = "literal",
    object_class_iri: str | None = None,
    datatype_iri: str | None = XSD_STRING,
    source_id: str,
) -> ValidatedFact:
    return ValidatedFact(
        fact_id=fact_id,
        subject_iri=event_id,
        subject_class_iri=f"{ATM}{event_class}",
        predicate_iri=predicate_iri,
        object_kind=object_kind,
        object_value=object_value,
        object_class_iri=object_class_iri,
        datatype_iri=datatype_iri if object_kind == "literal" else None,
        source_ids=[source_id],
        evidence_texts=["source-bound core evidence"],
        validation_profile=DECISION_PROFILE_REF,
        evidence_mode="source_text",
        evidence_ref=fact_id,
    )


def _core_facts(
    *,
    event_id: str,
    event_class: str,
    facility: CanonicalEntity,
    start: str,
    end: str,
    source_id: str,
    reason: str | None,
) -> list[ValidatedFact]:
    facts = [
        _fact(
            "core:type",
            event_id,
            event_class,
            RDF_TYPE,
            f"{ATM}{event_class}",
            object_kind="iri",
            object_class_iri=f"{ATM}{event_class}",
            source_id=source_id,
        ),
        _fact(
            "core:facility",
            event_id,
            event_class,
            f"{ATM}controlledNASelement",
            facility.entity_id,
            object_kind="iri",
            object_class_iri=f"{NAS}Airport",
            source_id=source_id,
        ),
        _fact(
            "core:start",
            event_id,
            event_class,
            f"{ATM}effectiveStartTime",
            start,
            datatype_iri=XSD_DATETIME,
            source_id=source_id,
        ),
        _fact(
            "core:end",
            event_id,
            event_class,
            f"{ATM}effectiveEndTime",
            end,
            datatype_iri=XSD_DATETIME,
            source_id=source_id,
        ),
    ]
    if reason is not None:
        facts.append(
            _fact(
                "core:reason",
                event_id,
                event_class,
                f"{ATM}impactingCondition",
                reason,
                source_id=source_id,
            )
        )
    return facts


def _facility_authority_result(
    facility: CanonicalEntity, source_id: str
) -> AuthorityResolutionResult:
    run_id = f"fixture:{source_id}:{facility.entity_id}"
    mention = facility.codes[0].value
    guide = load_schema_guide()
    result = resolve_facility_authority(
        task=AgentTask(
            run_id=run_id,
            source_id=source_id,
            objective="build a contract-valid context fixture",
            allowed_tools=[
                "lookup_nasr_facility",
                "lookup_artcc",
                "resolve_facility_alias",
            ],
        ),
        request=FacilityAuthorityResolutionInput(
            mention=mention,
            source_id=source_id,
            structural_slot="controlled_nas_element",
            expected_entity_type="airport",
            advisory_evidence="source-bound core evidence",
            resolution_event_mention=mention,
            resolution_event_id=stable_contract_id(
                "resolution-event",
                run_id,
                source_id,
                mention.upper(),
            ),
            run_started_at=datetime(2026, 7, 27, 12, 0, tzinfo=UTC),
            schema_slice_id=guide.schema_slice_id,
            schema_snapshot_sha256=guide.checksum,
            resolution_tool_version="authority-resolution-v1",
            authority_domain_status=AuthorityBuildStatus.INSUFFICIENT,
            authority_domain_reason_code="FIXTURE_HAS_NO_AUTHORITY_CANDIDATE",
        ),
    )
    return replace(
        result,
        evidence_card=EvidenceCard(
            agent_role="facility",
            status=AgentStatus.RESOLVED,
            canonical_refs=[facility.entity_id],
            source_ids=[source_id],
            claims=[
                EvidenceClaim(
                    field_name="controlled_facility",
                    value=mention,
                    ontology_target="nas:Airport",
                    evidence_text="source-bound core evidence",
                    source_id=source_id,
                    canonical_ref=facility.entity_id,
                )
            ],
        ),
    )


def _authority_records(facility_code: str, *, ground_stop: bool) -> tuple[SourceRecord, ...]:
    records = [
        SourceRecord(
            source_id=f"authority:nasr:{facility_code}",
            family=SourceFamily.NASR_FACILITY,
            content=f'{{"authority_text":"{facility_code} airport"}}',
        ),
        SourceRecord(
            source_id=(
                "authority:pcg:ground-stop" if ground_stop else "authority:pcg:ground-delay-program"
            ),
            family=SourceFamily.FAA_TERM,
            content=(
                '{"authority_text":"Ground Stop"}'
                if ground_stop
                else '{"authority_text":"Ground Delay Program"}'
            ),
        ),
    ]
    if ground_stop:
        records.append(
            SourceRecord(
                source_id="authority:pcg:glide-slope",
                family=SourceFamily.FAA_TERM,
                content='{"authority_text":"Glide Slope"}',
            )
        )
    return tuple(sorted(records, key=lambda record: record.source_id))


def _core_fact_traces(
    facts: list[ValidatedFact],
    registry,
    *,
    evidence_text: str,
) -> tuple[FactTraceRow, ...]:
    """Build direct advisory traces without creating a run artifact."""

    snapshot = registry.snapshots[0]
    return tuple(
        FactTraceRow(
            fact_id=fact.fact_id,
            graph_patch_line="fixture graph patch line",
            source_id=snapshot.source_id,
            evidence_text=evidence_text,
            evidence_agent_role="fixture",
            source_snapshot_sha256=snapshot.content_sha256,
        )
        for fact in facts
    )


@pytest.fixture(scope="module")
def config() -> dict:
    return load_yaml("configs/aviation_knowledge_v1.yaml")


@pytest.fixture(scope="module")
def weather_sources(config) -> list:
    return load_weather_sources(config)


@pytest.fixture(scope="module")
def bts_context(config):
    return load_bts_context_source(config)


@pytest.mark.parametrize(
    "source_key",
    ["bts_on_time_snapshot", "bts_on_time_manifest"],
)
def test_bts_loader_uses_configured_snapshot_paths(
    config,
    tmp_path,
    source_key,
):
    configured = {"sources": dict(config["sources"])}
    configured["sources"][source_key] = str(tmp_path / "missing-bts-source")

    with pytest.raises(FileNotFoundError):
        load_bts_context_source(configured)


@pytest.fixture(scope="module")
def weather_validation_case(config, weather_sources):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    facts = _core_facts(
        event_id="evt:weather-validator",
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=source_id,
        reason="weather",
    )
    event = context_artifacts_module._build_event(
        IngestContext(advisory=advisory, run_id="run:weather-validator"),
        {
            "event_uri": "evt:weather-validator",
            "validation": GraphValidationResult(accepted=facts, publishable=True),
        },
    )
    registry = build_source_snapshot_registry([advisory, *weather_sources])
    bundle = context_artifacts_module.build_weather_context(event, facility, registry)
    assert bundle.status == "ok"
    return event, facility, registry, bundle


def test_signature_parser_uses_signature_and_rejects_missing_or_malformed_values():
    text = "EFFECTIVE TIME:\n192138-192345\nSIGNATURE:\n26/05/19 21:38\n"
    assert parse_advisory_signature(text) == datetime(2026, 5, 19, 21, 38, tzinfo=UTC)
    assert parse_advisory_signature("EFFECTIVE TIME:\n192138-192345\n") is None
    with pytest.raises(ValueError, match="malformed SIGNATURE"):
        parse_advisory_signature("SIGNATURE:\n26/13/99 90:90\n")


@pytest.mark.parametrize(
    ("content", "expected_status"),
    [
        ("EFFECTIVE TIME:\n192138-192345\n", "insufficient"),
        ("SIGNATURE:\n26/13/99 90:90\n", "blocked"),
    ],
)
def test_missing_or_malformed_signature_fails_the_optional_context_layer(
    tmp_path,
    config,
    content,
    expected_status,
):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id).model_copy(update={"content": content})
    facility = FACILITIES["KJFK"]
    facts = [
        fact.model_copy(update={"evidence_texts": [content]})
        for fact in _core_facts(
            event_id="evt:signature-status",
            event_class="GroundDelayProgramTMI",
            facility=facility,
            start="2026-05-19T22:05:00Z",
            end="2026-05-20T02:59:00Z",
            source_id=source_id,
            reason="weather",
        )
    ]
    registry = build_source_snapshot_registry([advisory])
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=[facility],
        run_id="run:signature-status",
    )
    state = {
        "event_uri": "evt:signature-status",
        "facility_authority_result": _facility_authority_result(
            facility,
            source_id,
        ),
        "validation": GraphValidationResult(
            accepted=facts,
            publishable=True,
        ),
        "direct_fact_traces": _core_fact_traces(
            facts,
            registry,
            evidence_text=content,
        ),
        "profile_gap_rows": (),
    }
    prepared = prepare_event_context(ctx, state)
    assert prepared["weather_context"].status == expected_status
    assert prepared["public_observation_context"].status == expected_status

    result = integrate_event_context(ctx, {**state, **prepared})
    assert result["publication_status"] == expected_status
    assert result["formal_publication"] is None
    assert result["ingestion_package"] is None
    assert list(tmp_path.iterdir()) == []


def test_loaders_preserve_exact_weather_rows_and_the_pinned_bts_snapshot(
    config,
    weather_sources,
    bts_context,
):
    metar_path = Path(config["sources"]["metar"])
    exact_metar_rows = {
        line for line in metar_path.read_text(encoding="utf-8").splitlines() if line
    }
    assert weather_sources
    assert all(
        source.content in exact_metar_rows or source.family == SourceFamily.TAF
        for source in weather_sources
    )
    assert len({source.source_id for source in weather_sources}) == len(weather_sources)

    bts_source, bts_rows, binding = bts_context
    manifest = json.loads(
        Path("data/sources/bts_on_time_2026_05_manifest.json").read_text(encoding="utf-8")
    )
    assert len(bts_rows) == 1_978
    assert bts_source.source_id == manifest["source_id"]
    assert (
        hashlib.sha256(bts_source.content.encode("utf-8")).hexdigest()
        == manifest["normalized_sha256"]
    )
    assert binding.source_id == manifest["source_id"]
    assert binding.normalized_snapshot_sha256 == manifest["normalized_sha256"]
    assert binding.archive_sha256 == manifest["archive_sha256"]


def test_gdp_138_assembly_sees_only_prepared_validated_multisource_rows(
    tmp_path,
    config,
    weather_sources,
    bts_context,
    monkeypatch,
):
    """Assembly consumes in-memory validated context before publication."""

    import aviation_agentic_ai.agent_system.workflow as workflow_module
    from test_agent_system_authority_evidence import _catalog

    advisory = load_advisory_source(config, "2026-05-19:138")
    catalog = _catalog(tmp_path)
    bts_source, bts_rows, bts_binding = bts_context
    observed_before_assembly: dict[str, object] = {}
    original_builder = workflow_module._build_event_evidence_integration_task_from_state

    def capture_prepared_task(ctx, state, *, event_uri, event_class):
        observed_before_assembly["weather_status"] = state["weather_context"].status
        observed_before_assembly["observation_status"] = state["observation_context"].status
        observed_before_assembly["formal_publication"] = state.get(
            "formal_publication"
        )
        observed_before_assembly["ingestion_package"] = state.get(
            "ingestion_package"
        )
        return original_builder(
            ctx,
            state,
            event_uri=event_uri,
            event_class=event_class,
        )

    monkeypatch.setattr(
        workflow_module,
        "_build_event_evidence_integration_task_from_state",
        capture_prepared_task,
    )
    state = run_ingest(
        IngestContext(
            advisory=advisory,
            facility_candidates=[FACILITIES["KJFK"]],
            term_candidates=list(catalog.terminology.registry_terms),
            weather_sources=weather_sources,
            bts_rows=bts_rows,
            bts_source=bts_source,
            bts_manifest_binding=bts_binding,
            authority_catalog=catalog,
            guide=load_schema_guide(),
            run_id="run:gdp-138-prepared-context",
            run_started_at=datetime(2026, 5, 19, 20, 0, tzinfo=UTC),
        )
    )

    task = state["event_evidence_integration_task"]
    weather = state["weather_context"]
    observations = state["observation_context"]
    assert observations.status == "ok", observations.failure_reason
    assert observed_before_assembly == {
        "weather_status": "ok",
        "observation_status": "ok",
        "formal_publication": None,
        "ingestion_package": None,
    }
    assert task.available_evidence_layer_ids == (
        "layer:advisory",
        "layer:bts",
        "layer:weather",
    )
    assert task.context_association_ids == tuple(
        sorted(association.association_id for association in weather.associations)
    )
    expected_observation_ids = tuple(
        sorted({trace.observation_id for trace in observations.fact_traces})
    )
    assert task.public_observation_ids == expected_observation_ids
    assert (
        tuple(row.association_id for row in task.context_associations)
        == task.context_association_ids
    )
    assert (
        tuple(row.observation_id for row in task.public_observations) == task.public_observation_ids
    )
    expected_source_ids = {
        advisory.source_id,
        bts_source.source_id,
        *(association.source_id for association in weather.associations),
        *(
            authority_source_id
            for record in task.resolution_records
            for authority_source_id in record.authority_source_ids
        ),
    }
    assert {binding.source_id for binding in task.source_snapshot_bindings} == expected_source_ids
    assert state["validation"].publishable
    assert state["formal_publication"] is not None
    assert state["ingestion_package"] is not None
    assert "materialization" not in state


def test_prepared_context_is_rejected_when_kernel_accepts_a_different_event(
    tmp_path,
    config,
    weather_sources,
):
    advisory = load_advisory_source(config, "2026-05-19:138")
    facility = FACILITIES["KJFK"]
    event_id = "evt:prepared-kernel-recheck"
    candidate_facts = _core_facts(
        event_id=event_id,
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=advisory.source_id,
        reason="weather",
    )
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=[facility],
        weather_sources=weather_sources,
        guide=load_schema_guide(),
        run_id="run:prepared-kernel-recheck",
    )
    base_state = {
        "event_uri": event_id,
        "facility_authority_result": _facility_authority_result(facility, advisory.source_id),
        "validation": GraphValidationResult(
            accepted=candidate_facts,
            publishable=True,
        ),
    }
    prepared = prepare_event_context(ctx, base_state)
    changed_facts = [
        fact.model_copy(update={"object_value": "2026-05-20T03:30:00Z"})
        if fact.predicate_iri == f"{ATM}effectiveEndTime"
        else fact
        for fact in candidate_facts
    ]

    result = integrate_event_context(
        ctx,
        {
            **base_state,
            **prepared,
            "validation": GraphValidationResult(
                accepted=changed_facts,
                publishable=True,
            ),
        },
    )

    assert result["weather_context"].status == "blocked"
    assert "differs from Formal Graph Kernel" in (result["weather_context"].failure_reason)
    assert result["publication_status"] == "blocked"
    assert result["formal_publication"] is None
    assert result["ingestion_package"] is None
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    (
        "source_id",
        "event_class",
        "facility",
        "start",
        "end",
        "reason_state",
        "active_counts",
    ),
    [
        (
            "2026-05-19:123",
            "GroundStopTMI",
            "KJFK",
            "2026-05-19T21:00:00Z",
            "2026-05-19T22:45:00Z",
            "profile_gap",
            (20, 18, 2, 0),
        ),
        (
            "2026-05-19:138",
            "GroundDelayProgramTMI",
            "KJFK",
            "2026-05-19T22:05:00Z",
            "2026-05-20T02:59:00Z",
            "formal_weather",
            (77, 68, 4, 5),
        ),
        (
            "2026-05-20:020",
            "GroundDelayProgramTMI",
            "KEWR",
            "2026-05-20T01:24:00Z",
            "2026-05-20T05:46:00Z",
            "missing",
            (50, 49, 1, 0),
        ),
    ],
)
def test_three_cases_integrate_weather_and_bts_without_widening_core_semantics(
    tmp_path,
    config,
    weather_sources,
    bts_context,
    monkeypatch,
    source_id,
    event_class,
    facility,
    start,
    end,
    reason_state,
    active_counts,
):
    advisory = load_advisory_source(config, source_id)
    facility_entity = FACILITIES[facility]
    event_id = f"evt:{source_id.replace(':', '-')}"
    facts = [
        fact.model_copy(update={"evidence_texts": [advisory.content]})
        for fact in _core_facts(
            event_id=event_id,
            event_class=event_class,
            facility=facility_entity,
            start=start,
            end=end,
            source_id=source_id,
            reason="weather" if reason_state == "formal_weather" else None,
        )
    ]
    validation = GraphValidationResult(accepted=facts, publishable=True)
    advisory_registry = build_source_snapshot_registry([advisory])
    direct_fact_traces = _core_fact_traces(
        facts,
        advisory_registry,
        evidence_text=advisory.content,
    )
    profile_gap_rows = ()
    if source_id.endswith(":123"):
        evidence = "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
        snapshot = advisory_registry.snapshots[0]
        evidence_ref = stable_id(
            "profile-gap-evidence",
            source_id,
            snapshot.content_sha256,
            "impacting_condition",
            "weather",
            evidence,
        )
        persisted_event_id = (
            "urn:aviation-agentic-ai:event:"
            f"{event_id.removeprefix('evt:')}"
        )
        gap = PersistedProfileGap(
            profile_gap_id=stable_id(
                "profile-gap",
                persisted_event_id,
                "impacting_condition",
                "weather",
                "not_in_profile",
                evidence_ref,
                DECISION_PROFILE_REF.profile_id,
                DECISION_PROFILE_REF.profile_checksum,
                DECISION_PROFILE_REF.layer,
            ),
            event_id=persisted_event_id,
            field="impacting_condition",
            value="weather",
            evidence_text=evidence,
            reason="not_in_profile",
            source_id=source_id,
            source_snapshot_sha256=snapshot.content_sha256,
            evidence_ref=evidence_ref,
            validation_profile=DECISION_PROFILE_REF,
        )
        profile_gap_rows = (gap,)

    bts_source, bts_rows, bts_binding = bts_context
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=[facility_entity],
        weather_sources=weather_sources,
        bts_rows=bts_rows,
        bts_source=bts_source,
        bts_manifest_binding=bts_binding,
        run_id=f"run:{source_id}",
    )
    state = {
        "event_uri": event_id,
        "event_class": f"atm:{event_class}",
        "facility_authority_result": _facility_authority_result(facility_entity, source_id),
        "validation": validation,
        "direct_fact_traces": direct_fact_traces,
        "profile_gap_rows": profile_gap_rows,
        "source_snapshot": advisory_registry,
        "authority_source_records": AuthoritySourceRecordRegistry(
            records=_authority_records(
                facility,
                ground_stop=source_id.endswith(":123"),
            )
        ),
        "model_calls": ["existing-call"],
    }
    publication_calls = []
    original_publication_kernel = (
        context_artifacts_module.run_formal_publication_kernel
    )

    def capture_publication(**kwargs):
        publication = original_publication_kernel(**kwargs)
        publication_calls.append(publication)
        return publication

    monkeypatch.setattr(
        context_artifacts_module,
        "run_formal_publication_kernel",
        capture_publication,
    )

    result = integrate_event_context(ctx, state)

    assert len(publication_calls) == 1
    assert set(publication_calls[0].layer_fact_counts) == {
        "decision",
        "weather",
        "public_operational_observation",
    }
    assert publication_calls[0] == result["formal_publication"]
    package = result["ingestion_package"]
    assert package is not None
    assert result["publication_status"] == "ok"
    assert result["model_calls"] == []
    assert list(tmp_path.iterdir()) == []
    assert result["event_context_event"].operational_start == datetime.fromisoformat(
        start.replace("Z", "+00:00")
    )
    assert result["event_context_event"].operational_end == datetime.fromisoformat(
        end.replace("Z", "+00:00")
    )
    assert result["event_context_event"].advisory_issued_at == parse_advisory_signature(
        advisory.content
    )
    assert result["weather_context"].status == "ok"
    assert result["public_observation_context"].status == "ok"
    assert result["observation_context"].status == "ok", result[
        "observation_context"
    ].failure_reason
    assert {
        layer: metadata["status"] for layer, metadata in result["formal_layers"].items()
    } == {
        "decision": "ok",
        "weather": "ok",
        "public_operational_observation": "ok",
    }
    assert package.event.reason_status == {
        "formal_weather": "formal",
        "profile_gap": "profile_gap",
        "missing": "missing",
    }[reason_state]
    assert package.event.reason_value == (
        "weather" if reason_state == "formal_weather" else None
    )
    assert package.weather_associations
    assert all(
        association.causal_claim is False
        and association.event_id == package.event.event_id
        and association.publication_id == package.event.publication_id
        for association in package.weather_associations
    )
    assert package.public_observations
    active_observations = {
        observation.metric_key: observation.value
        for observation in package.public_observations
        if observation.phase == "active"
    }
    assert tuple(
        active_observations[metric]
        for metric in (
            "scheduled_arrival_count",
            "completed_arrival_count",
            "cancelled_count",
            "diverted_count",
        )
    ) == active_counts
    assert all(
        observation.event_id == package.event.event_id
        and observation.publication_id == package.event.publication_id
        and observation.source_version_id in package.source_version_ids
        for observation in package.public_observations
    )
    assert {
        observation.observation_id for observation in package.public_observations
    } == set(package.observation_fact_ids)

    event_facts = [
        fact
        for fact in package.facts
        if fact.subject_iri in {event_id, package.event.event_id}
    ]
    reasons = [
        fact.object_value
        for fact in event_facts
        if fact.predicate_iri.endswith("impactingCondition")
    ]
    assert reasons == (["weather"] if reason_state == "formal_weather" else [])
    if reason_state == "profile_gap":
        assert len(package.profile_gaps) == 1
        assert (
            package.profile_gaps[0].evidence_text
            == "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
        )
    else:
        assert package.profile_gaps == ()
    assert not any(
        fact.predicate_iri.startswith(
            "https://data.nasa.gov/ontologies/atmonto/data#"
        )
        for fact in event_facts
    )
    assert not any(
        "arrivalDemand" in fact.predicate_iri
        or "airportArrivalRate" in fact.predicate_iri
        for fact in package.facts
    )
    assert not any(
        fact.predicate_iri.endswith(("causedBy", "motivatedBy", "affectedBy"))
        for fact in package.facts
    )
    repeated = integrate_event_context(ctx, state)
    assert (
        repeated["formal_publication"].accepted
        == result["formal_publication"].accepted
    )
    assert (
        repeated["formal_publication"].layer_fact_counts
        == result["formal_publication"].layer_fact_counts
    )
    assert repeated["ingestion_package"] == package
    assert list(tmp_path.iterdir()) == []

    if source_id == "2026-05-19:138":
        monkeypatch.setattr(
            context_artifacts_module,
            "build_bts_observation_facts",
            lambda *args, **kwargs: BTSObservationBundle(
                status="blocked",
                failure_reason="injected observation validation failure",
            ),
        )
        blocked = integrate_event_context(ctx, state)
        assert blocked["observation_context"].status == "blocked"
        assert blocked["publication_status"] == "blocked"
        assert blocked["formal_publication"] is None
        assert blocked["ingestion_package"] is None
        assert list(tmp_path.iterdir()) == []

        insufficient = integrate_event_context(
            replace(
                ctx,
                bts_rows=[],
                bts_source=None,
                bts_manifest_binding=None,
            ),
            state,
        )
        assert insufficient["observation_context"].status == "insufficient"
        assert insufficient["publication_status"] == "ok"
        assert insufficient["formal_publication"] is not None
        assert insufficient["formal_publication"].layer_fact_counts == {
            "decision": len(facts),
            "weather": len(insufficient["weather_context"].formal_facts),
        }
        assert insufficient["ingestion_package"] is not None
        assert insufficient["ingestion_package"].public_observations == ()
        assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    (
        "source_id",
        "facility_code",
        "start",
        "end",
        "reason_state",
        "active_counts",
    ),
    [
        (
            "2026-05-19:123",
            "KJFK",
            "2026-05-19T21:00:00Z",
            "2026-05-19T22:45:00Z",
            "profile_gap",
            (20, 18, 2, 0),
        ),
        (
            "2026-05-19:138",
            "KJFK",
            "2026-05-19T22:05:00Z",
            "2026-05-20T02:59:00Z",
            "formal_weather",
            (77, 68, 4, 5),
        ),
        (
            "2026-05-20:020",
            "KEWR",
            "2026-05-20T01:24:00Z",
            "2026-05-20T05:46:00Z",
            "missing",
            (50, 49, 1, 0),
        ),
    ],
)
def test_current_authority_to_write_free_package_preserves_all_three_cases(
    tmp_path,
    config,
    weather_sources,
    bts_context,
    source_id,
    facility_code,
    start,
    end,
    reason_state,
    active_counts,
):
    from test_agent_system_authority_evidence import _catalog

    advisory = load_advisory_source(config, source_id)
    bts_source, bts_rows, bts_binding = bts_context
    semantic_factory = _NoDeterministicModelFactory()
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=[FACILITIES[facility_code]],
        weather_sources=weather_sources,
        bts_rows=bts_rows,
        bts_source=bts_source,
        bts_manifest_binding=bts_binding,
        authority_catalog=_catalog(tmp_path),
        semantic_resolution_tool_model_factory=semantic_factory,
        run_started_at=datetime(2026, 7, 27, 12, 0, tzinfo=UTC),
        run_id=f"run:{source_id}",
    )

    state = run_ingest(ctx)
    validation = state["validation"]
    publication = state["formal_publication"]
    package = state["ingestion_package"]

    assert state["event_evidence_integration_task"] is not None
    assert state["event_evidence_integration_proposal"] is not None
    assert validation.publishable
    assert publication is not None
    assert package is not None
    assert "materialization" not in state
    assert state["model_calls"] == []
    assert semantic_factory.calls == 0

    event_facts = [
        fact
        for fact in validation.accepted
        if fact.subject_iri == state["event_uri"]
    ]
    facility_fact = next(
        fact for fact in event_facts if fact.predicate_iri.endswith("controlledNASelement")
    )
    assert facility_fact.object_value == FACILITIES[facility_code].entity_id
    period = {
        fact.predicate_iri.rsplit("#", 1)[-1]: fact.object_value
        for fact in event_facts
        if fact.predicate_iri.endswith(("effectiveStartTime", "effectiveEndTime"))
    }
    assert period == {
        "effectiveStartTime": start,
        "effectiveEndTime": end,
    }
    reason_facts = [
        fact for fact in event_facts if fact.predicate_iri.endswith("impactingCondition")
    ]
    if reason_state == "formal_weather":
        assert [fact.object_value for fact in reason_facts] == ["weather"]
        assert reason_facts[0].evidence_texts == [
            "IMPACTING CONDITION: WEATHER / THUNDERSTORMS"
        ]
        assert reason_facts[0].evidence_texts[0].endswith("THUNDERSTORMS")
    else:
        assert reason_facts == []
    if reason_state == "profile_gap":
        assert len(package.profile_gaps) == 1
        assert package.profile_gaps[0].field == "impacting_condition"
    else:
        assert package.profile_gaps == ()

    active = {
        observation.metric_key: observation.value
        for observation in package.public_observations
        if observation.phase == "active"
    }
    assert tuple(
        active[metric]
        for metric in (
            "scheduled_arrival_count",
            "completed_arrival_count",
            "cancelled_count",
            "diverted_count",
        )
    ) == active_counts
    assert package.event.reason_status == {
        "formal_weather": "formal",
        "profile_gap": "profile_gap",
        "missing": "missing",
    }[reason_state]
    assert package.weather_associations
    assert all(
        association.causal_claim is False
        for association in package.weather_associations
    )
    assert not any(
        (tmp_path / name).exists()
        for name in (
            "run_manifest.json",
            "kg.jsonl",
            "kg.ttl",
            "neo4j_nodes.jsonl",
            "neo4j_relationships.jsonl",
        )
    )


def test_blocked_optional_context_prevents_write_free_publication(
    tmp_path,
    config,
):
    source_id = "2026-05-20:020"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KEWR"]
    event_id = "evt:optional-layer-failure"
    facts = [
        fact.model_copy(update={"evidence_texts": [advisory.content]})
        for fact in _core_facts(
            event_id=event_id,
            event_class="GroundDelayProgramTMI",
            facility=facility,
            start="2026-05-20T01:24:00Z",
            end="2026-05-20T05:46:00Z",
            source_id=source_id,
            reason=None,
        )
    ]
    registry = build_source_snapshot_registry([advisory])
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=[facility],
        weather_failure_reason="weather loader checksum mismatch",
        bts_failure_reason="BTS manifest checksum mismatch",
        run_id="run:blocked-context",
    )

    result = integrate_event_context(
        ctx,
        {
            "event_uri": event_id,
            "event_class": "atm:GroundDelayProgramTMI",
            "facility_authority_result": _facility_authority_result(facility, source_id),
            "validation": GraphValidationResult(accepted=facts, publishable=True),
            "direct_fact_traces": _core_fact_traces(
                facts,
                registry,
                evidence_text=advisory.content,
            ),
            "profile_gap_rows": (),
            "source_snapshot": registry,
            "authority_source_records": AuthoritySourceRecordRegistry(
                status=AuthoritySourceRegistryStatus.BLOCKED,
                reason_code="AUTHORITY_SOURCE_ID_CONFLICT",
                error_id="authority-source-registry-error:test",
            ),
        },
    )

    assert result["weather_context"].status == "blocked"
    assert result["public_observation_context"].status == "blocked"
    assert result["publication_status"] == "blocked"
    assert result["formal_publication"] is None
    assert result["ingestion_package"] is None
    assert {snapshot.source_id for snapshot in result["source_snapshot"].snapshots} == {source_id}
    assert list(tmp_path.iterdir()) == []


def test_duplicate_weather_fact_fails_closed_at_the_optional_layer(
    tmp_path,
    config,
    weather_sources,
    monkeypatch,
):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    event_id = "evt:duplicate-weather"
    facts = [
        fact.model_copy(update={"evidence_texts": [advisory.content]})
        for fact in _core_facts(
            event_id=event_id,
            event_class="GroundDelayProgramTMI",
            facility=facility,
            start="2026-05-19T22:05:00Z",
            end="2026-05-20T02:59:00Z",
            source_id=source_id,
            reason="weather",
        )
    ]
    registry = build_source_snapshot_registry([advisory])
    event = context_artifacts_module._build_event(
        IngestContext(advisory=advisory, run_id="run:duplicate"),
        {
            "event_uri": event_id,
            "validation": GraphValidationResult(accepted=facts, publishable=True),
        },
    )
    transient = build_source_snapshot_registry([advisory, *weather_sources])
    valid = context_artifacts_module.build_weather_context(
        event,
        facility,
        transient,
    )
    corrupted = valid.model_copy(
        update={"formal_facts": [*valid.formal_facts, valid.formal_facts[0]]}
    )
    monkeypatch.setattr(
        context_artifacts_module,
        "build_weather_context",
        lambda *args, **kwargs: corrupted,
    )
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=[facility],
        weather_sources=weather_sources,
        run_id="run:duplicate",
    )

    result = integrate_event_context(
        ctx,
        {
            "event_uri": event_id,
            "facility_authority_result": _facility_authority_result(facility, source_id),
            "validation": GraphValidationResult(accepted=facts, publishable=True),
            "direct_fact_traces": _core_fact_traces(
                facts,
                registry,
                evidence_text=advisory.content,
            ),
            "profile_gap_rows": (),
            "source_snapshot": registry,
        },
    )

    assert result["weather_context"].status == "blocked"
    assert "duplicate weather fact ID" in result["weather_context"].failure_reason
    assert result["publication_status"] == "blocked"
    assert result["formal_publication"] is None
    assert result["ingestion_package"] is None
    assert list(tmp_path.iterdir()) == []


def test_malformed_admitted_bts_layer_blocks_write_free_publication(
    tmp_path,
    config,
    weather_sources,
    bts_context,
):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    event_id = "evt:malformed-admitted-bts"
    facts = [
        fact.model_copy(update={"evidence_texts": [advisory.content]})
        for fact in _core_facts(
            event_id=event_id,
            event_class="GroundDelayProgramTMI",
            facility=facility,
            start="2026-05-19T22:05:00Z",
            end="2026-05-20T02:59:00Z",
            source_id=source_id,
            reason="weather",
        )
    ]
    registry = build_source_snapshot_registry([advisory])
    bts_source, bts_rows, bts_binding = bts_context
    ctx = IngestContext(
        advisory=advisory,
        facility_candidates=[facility],
        weather_sources=weather_sources,
        bts_rows=bts_rows,
        bts_source=bts_source,
        bts_manifest_binding=bts_binding,
        run_id="run:malformed-admitted-bts",
    )
    state = {
        "event_uri": event_id,
        "event_class": "atm:GroundDelayProgramTMI",
        "facility_authority_result": _facility_authority_result(
            facility,
            source_id,
        ),
        "validation": GraphValidationResult(
            accepted=facts,
            publishable=True,
        ),
        "direct_fact_traces": _core_fact_traces(
            facts,
            registry,
            evidence_text=advisory.content,
        ),
        "profile_gap_rows": (),
        "source_snapshot": registry,
    }
    prepared = prepare_event_context(ctx, state)
    observation_bundle = prepared["observation_context"]
    trace = next(
        item
        for item in observation_bundle.fact_traces
        if item.metric_key == "scheduled_arrival_count"
    )
    corrupted_facts = [
        fact.model_copy(update={"object_value": "999999"})
        if fact.fact_id == trace.fact_id
        else fact
        for fact in observation_bundle.formal_facts
    ]
    corrupted_bundle = observation_bundle.model_copy(
        update={"formal_facts": corrupted_facts}
    )

    with pytest.raises(
        FormalPublicationBlocked,
        match="deterministic numeric value mismatch",
    ):
        integrate_event_context(
            ctx,
            {
                **state,
                **prepared,
                "observation_context": corrupted_bundle,
            },
        )

    assert list(tmp_path.iterdir()) == []


def test_integration_blocks_a_self_consistent_rdf_type_retarget_from_the_builder(
    tmp_path,
    config,
    weather_sources,
    monkeypatch,
):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    event_id = "evt:retargeted-weather-type"
    facts = [
        fact.model_copy(update={"evidence_texts": [advisory.content]})
        for fact in _core_facts(
            event_id=event_id,
            event_class="GroundDelayProgramTMI",
            facility=facility,
            start="2026-05-19T22:05:00Z",
            end="2026-05-20T02:59:00Z",
            source_id=source_id,
            reason="weather",
        )
    ]
    registry = build_source_snapshot_registry([advisory])
    event = context_artifacts_module._build_event(
        IngestContext(advisory=advisory, run_id="run:retargeted-type"),
        {
            "event_uri": event_id,
            "validation": GraphValidationResult(accepted=facts, publishable=True),
        },
    )
    transient = build_source_snapshot_registry([advisory, *weather_sources])
    valid = context_artifacts_module.build_weather_context(
        event,
        facility,
        transient,
    )
    rdf_type = next(fact for fact in valid.formal_facts if fact.predicate_iri == RDF_TYPE)
    retargeted = rdf_type.model_copy(
        update={
            "object_value": f"{ATM}GroundDelayProgramTMI",
            "object_class_iri": f"{ATM}GroundDelayProgramTMI",
        }
    )
    corrupted = valid.model_copy(
        update={
            "formal_facts": [
                retargeted if fact.fact_id == rdf_type.fact_id else fact
                for fact in valid.formal_facts
            ]
        }
    )
    monkeypatch.setattr(
        context_artifacts_module,
        "build_weather_context",
        lambda *args, **kwargs: corrupted,
    )

    result = integrate_event_context(
        IngestContext(
            advisory=advisory,
            facility_candidates=[facility],
            weather_sources=weather_sources,
            run_id="run:retargeted-type",
        ),
        {
            "event_uri": event_id,
            "facility_authority_result": _facility_authority_result(facility, source_id),
            "validation": GraphValidationResult(accepted=facts, publishable=True),
            "direct_fact_traces": _core_fact_traces(
                facts,
                registry,
                evidence_text=advisory.content,
            ),
            "profile_gap_rows": (),
            "source_snapshot": registry,
        },
    )

    assert result["weather_context"].status == "blocked"
    assert "rdf:type" in result["weather_context"].failure_reason
    assert result["publication_status"] == "blocked"
    assert result["formal_publication"] is None
    assert result["ingestion_package"] is None
    assert list(tmp_path.iterdir()) == []


def test_integration_blocks_self_consistent_raw_evidence_from_a_regressed_parser(
    tmp_path,
    config,
    weather_sources,
    monkeypatch,
):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    event_id = "evt:regressed-weather-parser"
    facts = [
        fact.model_copy(update={"evidence_texts": [advisory.content]})
        for fact in _core_facts(
            event_id=event_id,
            event_class="GroundDelayProgramTMI",
            facility=facility,
            start="2026-05-19T22:05:00Z",
            end="2026-05-20T02:59:00Z",
            source_id=source_id,
            reason="weather",
        )
    ]
    registry = build_source_snapshot_registry([advisory])
    original_parse_report = weather_context_module._parse_report

    def regressed_parse_report(snapshot):
        parsed = original_parse_report(snapshot)
        raw = f"FORGED PARSER OUTPUT FOR {parsed.source.source_id}"
        raw_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        time_token = parsed.logical_time.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
        report_id = (
            f"weather-report:{parsed.family.value}:{parsed.station}:{time_token}:"
            f"{raw_hash}:{parsed.source.content_sha256[:16]}"
        )
        return replace(parsed, raw=raw, report_id=report_id)

    monkeypatch.setattr(
        weather_context_module,
        "_parse_report",
        regressed_parse_report,
    )

    result = integrate_event_context(
        IngestContext(
            advisory=advisory,
            facility_candidates=[facility],
            weather_sources=weather_sources,
            run_id="run:regressed-weather-parser",
        ),
        {
            "event_uri": event_id,
            "facility_authority_result": _facility_authority_result(facility, source_id),
            "validation": GraphValidationResult(
                accepted=facts,
                publishable=True,
            ),
            "direct_fact_traces": _core_fact_traces(
                facts,
                registry,
                evidence_text=advisory.content,
            ),
            "profile_gap_rows": (),
            "source_snapshot": registry,
        },
    )

    assert result["weather_context"].status == "blocked"
    assert "selected report IDs" in result["weather_context"].failure_reason
    assert result["publication_status"] == "blocked"
    assert result["formal_publication"] is None
    assert result["ingestion_package"] is None
    assert list(tmp_path.iterdir()) == []


def test_weather_bundle_rejects_conflicting_report_source_bindings(
    config,
    weather_sources,
):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    facts = _core_facts(
        event_id="evt:weather-source-conflict",
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=source_id,
        reason="weather",
    )
    event = context_artifacts_module._build_event(
        IngestContext(advisory=advisory, run_id="run:source-conflict"),
        {
            "event_uri": "evt:weather-source-conflict",
            "validation": GraphValidationResult(accepted=facts, publishable=True),
        },
    )
    registry = build_source_snapshot_registry([advisory, *weather_sources])
    valid = context_artifacts_module.build_weather_context(
        event,
        facility,
        registry,
    )
    original = valid.associations[0]
    alternate = next(
        snapshot
        for snapshot in registry.snapshots
        if snapshot.source_id != original.source_id
        and snapshot.family == registry.get(original.source_id).family
    )
    conflicting = original.model_copy(
        update={
            "association_id": f"{original.association_id}:conflict",
            "source_id": alternate.source_id,
            "source_snapshot_sha256": alternate.content_sha256,
        }
    )
    corrupted = valid.model_copy(update={"associations": [conflicting, *valid.associations]})

    with pytest.raises(ValueError, match="conflicting weather report source binding"):
        context_artifacts_module.validate_weather_context_bundle(
            corrupted,
            event=event,
            facility=facility,
            registry=registry,
        )


def test_public_observation_bundle_rejects_duplicate_phase_with_a_distinct_id(
    config,
    bts_context,
):
    guide = load_schema_guide()
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    facts = _core_facts(
        event_id="evt:duplicate-outcome-phase",
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=source_id,
        reason="weather",
    )
    event = context_artifacts_module._build_event(
        IngestContext(advisory=advisory, run_id="run:duplicate-phase"),
        {
            "event_uri": "evt:duplicate-outcome-phase",
            "validation": GraphValidationResult(accepted=facts, publishable=True),
        },
    )
    bts_source, bts_rows, bts_binding = bts_context
    registry = build_source_snapshot_registry([bts_source])
    valid = context_artifacts_module.build_bts_public_observation_summaries(
        event,
        facility,
        bts_rows,
        source_id=bts_source.source_id,
        source_snapshot_sha256=registry.snapshots[0].content_sha256,
        manifest_binding=bts_binding,
        aggregation_procedure=next(
            profile.aggregation_procedure
            for profile in load_validation_profile_registry(decision_guide=guide).profiles
            if profile.ref.layer == "public_operational_observation"
        ),
    )
    duplicate = valid.summaries[0].model_copy(
        update={"summary_id": f"{valid.summaries[0].summary_id}:duplicate"}
    )
    corrupted = valid.model_copy(update={"summaries": [*valid.summaries, duplicate]})

    with pytest.raises(ValueError, match="exactly one summary per phase"):
        context_artifacts_module._validate_public_observations(
            corrupted,
            event=event,
            facility=facility,
            registry=registry,
        )


@pytest.mark.parametrize(
    "corruption",
    [
        "rdf_type_target",
        "literal_forecasting_airport",
        "empty_formal_fact_set",
        "metar_as_forecast",
        "arbitrary_association_id",
        "forged_relevant_times",
        "wrong_interval_datatype",
        "missing_required_fact",
        "arbitrary_fact_id",
        "forged_raw_report_value",
        "forged_condition_status",
    ],
)
def test_weather_validator_rejects_semantically_malformed_adapter_bundles(
    weather_validation_case,
    corruption,
):
    event, facility, registry, valid = weather_validation_case
    facts = list(valid.formal_facts)
    traces = list(valid.fact_traces)
    associations = list(valid.associations)

    def replace_fact(original, replacement):
        return [replacement if fact.fact_id == original.fact_id else fact for fact in facts]

    if corruption == "rdf_type_target":
        original = next(fact for fact in facts if fact.predicate_iri == RDF_TYPE)
        facts = replace_fact(
            original,
            original.model_copy(update={"object_value": f"{NAS}Airport"}),
        )
    elif corruption == "literal_forecasting_airport":
        original = next(fact for fact in facts if fact.predicate_iri == FORECASTING_AIRPORT)
        facts = replace_fact(
            original,
            original.model_copy(
                update={
                    "object_kind": "literal",
                    "object_class_iri": None,
                    "datatype_iri": XSD_STRING,
                }
            ),
        )
    elif corruption == "empty_formal_fact_set":
        facts = []
        traces = []
    elif corruption == "metar_as_forecast":
        index = next(
            index
            for index, association in enumerate(associations)
            if registry.get(association.source_id).family == SourceFamily.METAR
        )
        associations[index] = associations[index].model_copy(
            update={"relation_type": "latest_forecast_known_at_issue"}
        )
    elif corruption == "arbitrary_association_id":
        associations[0] = associations[0].model_copy(
            update={"association_id": "weather-association:arbitrary"}
        )
    elif corruption == "forged_relevant_times":
        associations[0] = associations[0].model_copy(
            update={"relevant_times": {"advisory_issued_at": "1999-01-01T00:00:00Z"}}
        )
    elif corruption == "wrong_interval_datatype":
        original = next(fact for fact in facts if fact.predicate_iri == INTERVAL_START)
        facts = replace_fact(
            original,
            original.model_copy(update={"datatype_iri": XSD_STRING}),
        )
    elif corruption == "missing_required_fact":
        original = next(fact for fact in facts if fact.predicate_iri == INTERVAL_END)
        facts = [fact for fact in facts if fact.fact_id != original.fact_id]
        traces = [trace for trace in traces if trace.fact_id != original.fact_id]
    elif corruption == "arbitrary_fact_id":
        original = facts[0]
        replacement = original.model_copy(update={"fact_id": "weather-fact:arbitrary"})
        facts = replace_fact(original, replacement)
        traces = [
            trace.model_copy(update={"fact_id": replacement.fact_id})
            if trace.fact_id == original.fact_id
            else trace
            for trace in traces
        ]
    elif corruption == "forged_raw_report_value":
        original = next(
            fact
            for fact in facts
            if fact.predicate_iri
            in {
                METAR_STRING,
                TAF_STRING,
            }
        )
        facts = replace_fact(
            original,
            original.model_copy(update={"object_value": "FORGED WEATHER REPORT"}),
        )
    elif corruption == "forged_condition_status":
        original = next(
            fact
            for fact in facts
            if fact.predicate_iri == METEOROLOGICAL_CONDITION_STATUS
        )
        facts = replace_fact(
            original,
            original.model_copy(
                update={
                    "object_value": (
                        "forecast"
                        if original.object_value == "observed"
                        else "observed"
                    )
                }
            ),
        )
    corrupted = valid.model_copy(
        update={
            "formal_facts": facts,
            "fact_traces": traces,
            "associations": associations,
        }
    )

    with pytest.raises(ValueError):
        context_artifacts_module.validate_weather_context_bundle(
            corrupted,
            event=event,
            facility=facility,
            registry=registry,
        )


def test_outcome_validator_rejects_event_unbound_1999_windows(
    config,
    bts_context,
):
    source_id = "2026-05-19:138"
    advisory = load_advisory_source(config, source_id)
    facility = FACILITIES["KJFK"]
    facts = _core_facts(
        event_id="evt:outcome-window",
        event_class="GroundDelayProgramTMI",
        facility=facility,
        start="2026-05-19T22:05:00Z",
        end="2026-05-20T02:59:00Z",
        source_id=source_id,
        reason="weather",
    )
    event = context_artifacts_module._build_event(
        IngestContext(advisory=advisory, run_id="run:outcome-window"),
        {
            "event_uri": "evt:outcome-window",
            "validation": GraphValidationResult(accepted=facts, publishable=True),
        },
    )
    bts_source, bts_rows, bts_binding = bts_context
    registry = build_source_snapshot_registry([bts_source])
    valid = context_artifacts_module.build_bts_public_observation_summaries(
        event,
        facility,
        bts_rows,
        source_id=bts_source.source_id,
        source_snapshot_sha256=registry.snapshots[0].content_sha256,
        manifest_binding=bts_binding,
        aggregation_procedure=next(
            profile.aggregation_procedure
            for profile in load_validation_profile_registry(
                decision_guide=load_schema_guide()
            ).profiles
            if profile.ref.layer == "public_operational_observation"
        ),
    )
    active = next(summary for summary in valid.summaries if summary.phase == "active")
    forged = active.model_copy(
        update={
            "window_start": datetime(1999, 1, 1, tzinfo=UTC),
            "window_end": datetime(1999, 1, 2, tzinfo=UTC),
        }
    )
    corrupted = valid.model_copy(
        update={
            "summaries": [
                forged if summary.phase == "active" else summary for summary in valid.summaries
            ]
        }
    )

    with pytest.raises(ValueError, match="BTS public observation window mismatch"):
        context_artifacts_module._validate_public_observations(
            corrupted,
            event=event,
            facility=facility,
            registry=registry,
        )


def test_ingest_graph_names_explicit_validation_and_publication_nodes():
    graph = build_ingest_graph()
    graph_json = graph.get_graph().to_json()
    edges = {(edge["source"], edge["target"]) for edge in graph_json["edges"]}
    assert ("integrate_event_evidence", "validate_event_patch") in edges
    assert ("validate_event_patch", "publish_event") in edges
    assert ("publish_event", "__end__") in edges
    assert not {"materialize", "decision_context"} & {
        node["id"] for node in graph_json["nodes"]
    }


def test_event_preflight_rejection_does_not_call_final_publication_kernel(
    tmp_path,
    monkeypatch,
):
    calls: list[object] = []
    monkeypatch.setattr(
        context_artifacts_module,
        "run_formal_publication_kernel",
        lambda **kwargs: calls.append(kwargs),
    )
    advisory = SourceRecord(
        source_id="fixture:rejected-event",
        family=SourceFamily.ATCSCC_ADVISORY,
        content="GROUND STOP",
    )
    monkeypatch.setattr(
        workflow_module,
        "_CTX_HOLDER",
        IngestContext(
            advisory=advisory,
            run_id="run:rejected-event",
        ),
    )
    event_id = "urn:aviation-agentic-ai:event:rejected-event"
    state = {
        "integration_graph_patch": GraphPatchBlock(
            patch_lines=[
                GraphPatchLine(
                    subject=event_id,
                    predicate="rdf:type",
                    object="atm:GroundStopTMI",
                    source_ids=[advisory.source_id],
                )
            ]
        ),
        "event_uri": event_id,
        "event_class": "atm:GroundStopTMI",
        "advisory_evidence": EvidenceCard(
            agent_role="advisory",
            status=AgentStatus.RESOLVED,
            source_ids=[advisory.source_id],
            claims=[
                EvidenceClaim(
                    field_name="event_type",
                    value="GS",
                    ontology_target="atm:GroundStopTMI",
                    evidence_text="GROUND STOP",
                    source_id=advisory.source_id,
                )
            ],
        ),
    }

    event_validation = workflow_module._validate_event_patch_node(state)
    assert event_validation["validation"] is not None
    assert event_validation["validation"].publishable is False
    assert event_validation["validation"].accepted
    assert event_validation["validation"].graph_errors

    published = workflow_module._publish_event_node(
        {
            **state,
            **event_validation,
        }
    )

    assert published["formal_publication"] is None
    assert published["ingestion_package"] is None
    assert published["publication_status"] == "blocked"
    assert published["formal_layers"]["decision"]["status"] == "blocked"
    assert calls == []
