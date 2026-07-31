"""Live-store read-tool tests for the HybridRAG Query Agent."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryScope,
    HybridQueryToolObservation,
    SourceFamily,
    ValidationProfileRef,
)
from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
)
from aviation_agentic_ai.agent_system.hybrid_query_tools import (
    HybridQueryGateway,
    build_hybrid_query_tools,
)
from aviation_agentic_ai.agent_system.ingestion_package import (
    EventFactMembership,
    EventIngestionPackage,
    IngestionAttempt,
)
from aviation_agentic_ai.agent_system.query_runtime import QueryRuntime
from aviation_agentic_ai.agent_system.source_retrieval import (
    build_source_record_chunk,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    EventEvidenceLink,
    EventProfileGapRecord,
    EventWeatherAssociation,
    IngestionResult,
    PublicObservationRecord,
    SemanticFactRecord,
    SourceVersionRecord,
    TMIEventRecord,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
    TMIEventVectorHit,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id


FORMAL_EVENT_ID = "urn:event:formal-reason"
GAP_EVENT_ID = "urn:event:profile-gap"
MISSING_EVENT_ID = "urn:event:missing-reason"
FACILITY_ID = "urn:facility:KJFK"
GDP_IRI = (
    "https://data.nasa.gov/ontologies/atmonto/ATM#"
    "GroundDelayProgramTMI"
)
PROFILE = ValidationProfileRef(
    profile_id="profile:query-test",
    profile_checksum="a" * 64,
    layer="decision",
)
WEATHER_PROFILE = ValidationProfileRef(
    profile_id="profile:query-weather",
    profile_checksum="b" * 64,
    layer="weather",
)
OBSERVATION_PROFILE = ValidationProfileRef(
    profile_id="profile:query-observation",
    profile_checksum="c" * 64,
    layer="public_operational_observation",
)


@dataclass(frozen=True)
class LiveQueryScenario:
    store: AviationEvidenceStore
    events: dict[str, TMIEventRecord]
    facts: dict[str, SemanticFactRecord]
    sources: dict[str, SourceVersionRecord]


@dataclass(frozen=True)
class _IndexState:
    representation_version: str = "tmi-event-metadata-v1"
    embedding_model_id: str = "test/tiny"


class TinyEventIndex:
    state = _IndexState()

    def __init__(self, events: dict[str, TMIEventRecord]) -> None:
        self.events = events

    def get_publication_vector(
        self,
        publication_id: str,
    ) -> tuple[float, ...]:
        assert publication_id in {
            event.publication_id for event in self.events.values()
        }
        return (1.0, 0.0)

    def query_candidates(
        self,
        *,
        query_vector,
        candidate_publication_ids,
        n_results: int,
    ) -> tuple[TMIEventVectorHit, ...]:
        assert tuple(query_vector) == (1.0, 0.0)
        by_publication = {
            event.publication_id: event for event in self.events.values()
        }
        return tuple(
            TMIEventVectorHit(
                event_id=by_publication[publication_id].event_id,
                publication_id=publication_id,
                advisory_source_id=by_publication[
                    publication_id
                ].advisory_source_id,
                distance=0.1,
                similarity=0.9,
            )
            for publication_id in candidate_publication_ids[:n_results]
        )


def _source(
    source_id: str,
    family: SourceFamily,
    content: str,
) -> SourceVersionRecord:
    digest = hashlib.sha256(content.encode()).hexdigest()
    return SourceVersionRecord(
        source_version_id=stable_id("source-version", source_id, digest),
        source_id=source_id,
        family=family,
        asset_id=None,
        content=content,
        content_sha256=digest,
        source_url=f"https://example.test/{source_id}",
        logical_time="2026-05-20T10:00:00Z",
        metadata={},
    )


def _fact(
    fact_id: str,
    subject: str,
    predicate: str,
    object_value: str,
    *,
    object_kind: str = "iri",
    profile: ValidationProfileRef = PROFILE,
) -> SemanticFactRecord:
    return SemanticFactRecord(
        fact_id=fact_id,
        subject_iri=subject,
        subject_class_iri="atm:TrafficManagementInitiative",
        predicate_iri=predicate,
        object_kind=object_kind,  # type: ignore[arg-type]
        object_value=object_value,
        object_class_iri=(
            "owl:Thing" if object_kind == "iri" else None
        ),
        datatype_iri=(
            None if object_kind == "iri" else "xsd:string"
        ),
        validation_profile=profile,
        evidence_mode="source_text",
    )


def _event(
    event_id: str,
    advisory: SourceVersionRecord,
    *,
    reason_status: str,
    reason_value: str | None,
) -> TMIEventRecord:
    digest = hashlib.sha256(
        f"{event_id}:{advisory.source_version_id}".encode()
    ).hexdigest()
    return TMIEventRecord(
        event_id=event_id,
        publication_id=stable_id(
            "event-publication",
            event_id,
            advisory.source_version_id,
            digest,
        ),
        advisory_source_id=advisory.source_id,
        publication_source_version_id=advisory.source_version_id,
        event_type_iris=(GDP_IRI,),
        facility_ids=(FACILITY_ID,),
        effective_start=datetime(2026, 5, 20, 12, tzinfo=UTC),
        effective_end=datetime(2026, 5, 20, 15, tzinfo=UTC),
        issued_at=datetime(2026, 5, 20, 11, tzinfo=UTC),
        reason_status=reason_status,  # type: ignore[arg-type]
        reason_value=reason_value,
    )


def _publication_digest(event: TMIEventRecord) -> str:
    return hashlib.sha256(
        (
            f"{event.event_id}:"
            f"{event.publication_source_version_id}"
        ).encode()
    ).hexdigest()


def _publish(
    store: AviationEvidenceStore,
    *,
    event: TMIEventRecord,
    sources: tuple[SourceVersionRecord, ...],
    facts: tuple[SemanticFactRecord, ...],
    links: tuple[EventEvidenceLink, ...],
    gaps: tuple[EventProfileGapRecord, ...] = (),
    weather: tuple[EventWeatherAssociation, ...] = (),
    observations: tuple[PublicObservationRecord, ...] = (),
) -> None:
    package = EventIngestionPackage(
        event=event,
        formal_publication_digest=_publication_digest(event),
        source_version_ids=tuple(
            source.source_version_id for source in sources
        ),
        source_anchors=(),
        facts=facts,
        event_fact_memberships=tuple(
            EventFactMembership(
                event_id=event.event_id,
                publication_id=event.publication_id,
                fact_id=fact.fact_id,
            )
            for fact in facts
        ),
        evidence_links=links,
        profile_gaps=gaps,
        weather_associations=weather,
        public_observations=observations,
        observation_fact_ids={
            observation.observation_id: observation.fact_ids
            for observation in observations
        },
    )
    store.apply_ingestion_attempt(
        IngestionAttempt(
            result=IngestionResult(
                source_version_id=event.publication_source_version_id,
                source_id=event.advisory_source_id,
                status="ok",
                event_id=event.event_id,
                publication_id=event.publication_id,
                reason="accepted",
                provider_call_count=0,
                tmi_family="ground_delay_program",
                preflight_eligible=True,
            ),
            package=package,
        )
    )


def _link(
    *,
    event: TMIEventRecord,
    owner_kind: str,
    owner_id: str,
    source: SourceVersionRecord,
    anchor_id: str,
    evidence_text: str | None = None,
) -> EventEvidenceLink:
    return EventEvidenceLink(
        evidence_link_id=stable_id(
            "event-evidence",
            event.publication_id,
            owner_kind,
            owner_id,
            source.source_version_id,
        ),
        event_id=event.event_id,
        publication_id=event.publication_id,
        owner_kind=owner_kind,  # type: ignore[arg-type]
        owner_id=owner_id,
        source_version_id=source.source_version_id,
        source_anchor_id=anchor_id,
        evidence_text=evidence_text or source.content,
        evidence_ref=f"{source.source_id}#record",
    )


def _live_store(tmp_path: Path) -> LiveQueryScenario:
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:hybrid-query",
        create=True,
    )
    sources = {
        "formal": _source(
            "source:advisory:formal",
            SourceFamily.ATCSCC_ADVISORY,
            "GDP FOR KJFK. IMPACTING CONDITION: WEATHER.",
        ),
        "gap": _source(
            "source:advisory:gap",
            SourceFamily.ATCSCC_ADVISORY,
            "GDP FOR KJFK. WEATHER / THUNDERSTORMS.",
        ),
        "missing": _source(
            "source:advisory:missing",
            SourceFamily.ATCSCC_ADVISORY,
            "GDP CANCELLATION FOR KJFK.",
        ),
        "taf": _source(
            "source:taf:KJFK",
            SourceFamily.TAF,
            "TAF KJFK TEMPO TSRA.",
        ),
        "bts": _source(
            "source:bts:KJFK",
            SourceFamily.BTS_ON_TIME,
            "KJFK active delayed flights: 12",
        ),
    }
    chunks = {}
    anchors = {}
    for source in sources.values():
        store.register_source_version(source)
        anchors[source.source_version_id] = store.register_source_anchor(
            source.source_version_id,
            char_start=0,
            char_end=len(source.content),
        )
        chunk = build_source_record_chunk(source)
        if chunk is not None:
            chunks[source.source_version_id] = chunk
    store.upsert_source_chunks(tuple(chunks.values()))

    events = {
        FORMAL_EVENT_ID: _event(
            FORMAL_EVENT_ID,
            sources["formal"],
            reason_status="formal",
            reason_value="weather",
        ),
        GAP_EVENT_ID: _event(
            GAP_EVENT_ID,
            sources["gap"],
            reason_status="profile_gap",
            reason_value=None,
        ),
        MISSING_EVENT_ID: _event(
            MISSING_EVENT_ID,
            sources["missing"],
            reason_status="missing",
            reason_value=None,
        ),
    }
    formal = events[FORMAL_EVENT_ID]
    formal_facts = (
        _fact(
            "fact:formal:type",
            FORMAL_EVENT_ID,
            "rdf:type",
            "atm:GroundDelayProgramTMI",
        ),
        _fact(
            "fact:formal:facility",
            FORMAL_EVENT_ID,
            "atm:controlledNASelement",
            FACILITY_ID,
        ),
        _fact(
            "fact:formal:reason",
            FORMAL_EVENT_ID,
            "atm:impactingCondition",
            "atm:WeatherCondition",
        ),
        _fact(
            "fact:taf:facility",
            "urn:aviation-agentic-ai:taf:KJFK",
            "atm:forecastingAirport",
            FACILITY_ID,
            profile=WEATHER_PROFILE,
        ),
        _fact(
            "fact:bts:facility",
            "urn:observation:bts:active",
            "sosa:hasFeatureOfInterest",
            FACILITY_ID,
            profile=OBSERVATION_PROFILE,
        ),
    )
    facts = {fact.fact_id: fact for fact in formal_facts}
    formal_anchor = anchors[
        sources["formal"].source_version_id
    ].source_anchor_id
    taf_anchor = anchors[sources["taf"].source_version_id].source_anchor_id
    bts_anchor = anchors[sources["bts"].source_version_id].source_anchor_id
    links = tuple(
        [
            *(
                _link(
                    event=formal,
                    owner_kind="fact",
                    owner_id=fact.fact_id,
                    source=(
                        sources["taf"]
                        if fact.fact_id == "fact:taf:facility"
                        else sources["bts"]
                        if fact.fact_id == "fact:bts:facility"
                        else sources["formal"]
                    ),
                    anchor_id=(
                        taf_anchor
                        if fact.fact_id == "fact:taf:facility"
                        else bts_anchor
                        if fact.fact_id == "fact:bts:facility"
                        else formal_anchor
                    ),
                )
                for fact in formal_facts
            ),
            _link(
                event=formal,
                owner_kind="weather_association",
                owner_id="association:taf",
                source=sources["taf"],
                anchor_id=taf_anchor,
            ),
            _link(
                event=formal,
                owner_kind="public_observation",
                owner_id="observation:bts:active",
                source=sources["bts"],
                anchor_id=bts_anchor,
            ),
        ]
    )
    _publish(
        store,
        event=formal,
        sources=(sources["formal"], sources["taf"], sources["bts"]),
        facts=formal_facts,
        links=links,
        weather=(
            EventWeatherAssociation(
                association_id="association:taf",
                event_id=FORMAL_EVENT_ID,
                publication_id=formal.publication_id,
                report_id="taf:KJFK",
                facility_id=FACILITY_ID,
                relation_type="latest_forecast_known_at_issue",
                selection_method="bounded_test_fixture",
                relevant_times={"issued": "2026-05-20T11:00:00Z"},
                source_version_id=sources["taf"].source_version_id,
                causal_claim=False,
            ),
        ),
        observations=(
            PublicObservationRecord(
                observation_id="observation:bts:active",
                event_id=FORMAL_EVENT_ID,
                publication_id=formal.publication_id,
                phase="active",
                metric_key="delayed_flights",
                value=Decimal("12"),
                unit_iri="unit:flight",
                fact_ids=("fact:bts:facility",),
                profile_id=OBSERVATION_PROFILE.profile_id,
                profile_checksum=OBSERVATION_PROFILE.profile_checksum,
                source_version_id=sources["bts"].source_version_id,
            ),
        ),
    )

    gap = events[GAP_EVENT_ID]
    gap_fact = _fact(
        "fact:gap:type",
        GAP_EVENT_ID,
        "rdf:type",
        "atm:GroundDelayProgramTMI",
    )
    facts[gap_fact.fact_id] = gap_fact
    gap_evidence = "WEATHER / THUNDERSTORMS"
    gap_full_anchor = anchors[
        sources["gap"].source_version_id
    ].source_anchor_id
    gap_anchor = store.anchor_source_text(
        sources["gap"].source_version_id,
        gap_evidence,
    ).source_anchor_id
    gap_record = EventProfileGapRecord(
        profile_gap_id="gap:reason",
        event_id=GAP_EVENT_ID,
        publication_id=gap.publication_id,
        field="impacting_condition",
        value="WEATHER / THUNDERSTORMS",
        evidence_text=gap_evidence,
        reason="No reviewed ontology mapping.",
        source_version_id=sources["gap"].source_version_id,
        source_anchor_id=gap_anchor,
        evidence_ref="source:advisory:gap#reason",
        validation_profile=PROFILE,
    )
    _publish(
        store,
        event=gap,
        sources=(sources["gap"],),
        facts=(gap_fact,),
        links=(
            _link(
                event=gap,
                owner_kind="fact",
                owner_id=gap_fact.fact_id,
                source=sources["gap"],
                anchor_id=gap_full_anchor,
            ),
            _link(
                event=gap,
                owner_kind="profile_gap",
                owner_id=gap_record.profile_gap_id,
                source=sources["gap"],
                anchor_id=gap_anchor,
                evidence_text=gap_evidence,
            ),
        ),
        gaps=(gap_record,),
    )

    missing = events[MISSING_EVENT_ID]
    missing_fact = _fact(
        "fact:missing:type",
        MISSING_EVENT_ID,
        "rdf:type",
        "atm:GroundDelayProgramTMI",
    )
    facts[missing_fact.fact_id] = missing_fact
    missing_anchor = anchors[
        sources["missing"].source_version_id
    ].source_anchor_id
    _publish(
        store,
        event=missing,
        sources=(sources["missing"],),
        facts=(missing_fact,),
        links=(
            _link(
                event=missing,
                owner_kind="fact",
                owner_id=missing_fact.fact_id,
                source=sources["missing"],
                anchor_id=missing_anchor,
            ),
        ),
    )
    return LiveQueryScenario(
        store=store,
        events=events,
        facts=facts,
        sources=sources,
    )


def _scope(**updates: object) -> HybridQueryScope:
    return HybridQueryScope().model_copy(update=updates)


def _gateway(
    scenario: LiveQueryScenario,
    *,
    with_event_index: bool = False,
    **scope_updates: object,
) -> HybridQueryGateway:
    return HybridQueryGateway(
        runtime=QueryRuntime(
            store=scenario.store,
            source_index=None,
            event_index=(
                TinyEventIndex(scenario.events)  # type: ignore[arg-type]
                if with_event_index
                else None
            ),
        ),
        scope=_scope(**scope_updates),
    )


def test_tool_registry_exposes_nine_read_only_tools(tmp_path: Path) -> None:
    scenario = _live_store(tmp_path)
    tools = build_hybrid_query_tools(_gateway(scenario))

    assert [tool.name for tool in tools] == [
        "find_tmi_events",
        "read_tmi_event_facts",
        "read_tmi_operational_context",
        "read_public_observations",
        "read_tmi_event_graph",
        "find_similar_tmi_events",
        "search_source_text",
        "semantic_search_sources",
        "read_source",
    ]
    result = next(
        tool for tool in tools if tool.name == "read_tmi_event_facts"
    ).invoke({"event_id": FORMAL_EVENT_ID})
    assert HybridQueryToolObservation.model_validate(result).status == "ok"
    scenario.store.close()


def test_find_events_and_scope_cannot_be_broadened(tmp_path: Path) -> None:
    scenario = _live_store(tmp_path)
    gateway = _gateway(scenario, event_id=FORMAL_EVENT_ID, limit=2)

    observation = gateway.find_tmi_events(limit=1)
    assert observation.details.event_ids == (FORMAL_EVENT_ID,)
    with pytest.raises(ValueError, match="outside the query scope"):
        gateway.read_tmi_event_facts(event_id=MISSING_EVENT_ID)
    with pytest.raises(ValueError, match="limit"):
        gateway.find_tmi_events(limit=3)
    scenario.store.close()


def test_source_family_scope_applies_across_structured_query_tools(
    tmp_path: Path,
) -> None:
    scenario = _live_store(tmp_path)
    gateway = _gateway(
        scenario,
        event_id=FORMAL_EVENT_ID,
        source_families=(SourceFamily.TAF,),
    )

    found = gateway.find_tmi_events()
    facts = gateway.read_tmi_event_facts(event_id=FORMAL_EVENT_ID)
    context = gateway.read_tmi_operational_context(
        event_id=FORMAL_EVENT_ID
    )
    observations = gateway.read_public_observations(
        event_id=FORMAL_EVENT_ID
    )
    graph = gateway.read_tmi_event_graph(event_id=FORMAL_EVENT_ID)

    for observation in (found, facts, context, observations, graph):
        for record in observation.support_records:
            assert record.source_version_ids
            assert all(
                scenario.store.get_source_version(source_version_id).family
                == SourceFamily.TAF
                for source_version_id in record.source_version_ids
            )
    facts_payload = json.loads(facts.content)
    assert facts_payload["event"] == {"event_id": FORMAL_EVENT_ID}
    assert facts_payload["facts"] == []
    assert facts.status == "insufficient"
    assert observations.status == "insufficient"
    assert observations.support_records == ()
    scenario.store.close()


def test_reason_states_weather_and_bts_roles_are_preserved(
    tmp_path: Path,
) -> None:
    scenario = _live_store(tmp_path)
    gateway = _gateway(scenario)

    formal = json.loads(
        gateway.read_tmi_event_facts(
            event_id=FORMAL_EVENT_ID
        ).content
    )
    gap = json.loads(
        gateway.read_tmi_event_facts(event_id=GAP_EVENT_ID).content
    )
    missing = json.loads(
        gateway.read_tmi_event_facts(
            event_id=MISSING_EVENT_ID
        ).content
    )
    weather = gateway.read_tmi_operational_context(
        event_id=FORMAL_EVENT_ID
    )
    observations = gateway.read_public_observations(
        event_id=FORMAL_EVENT_ID,
        phases=("active",),
    )
    assert formal["event"]["reason_status"] == "formal"
    assert formal["event"]["reason_value"] == "weather"
    assert gap["event"]["reason_status"] == "profile_gap"
    assert gap["profile_gaps"][0]["evidence_text"] == (
        "WEATHER / THUNDERSTORMS"
    )
    assert missing["event"]["reason_status"] == "missing"
    assert missing["event"]["reason_value"] is None
    assert json.loads(weather.content)["causal_claim"] is False
    assert {record.kind for record in weather.support_records} == {
        "non_causal_context"
    }
    observation_payload = json.loads(observations.content)
    assert observation_payload["evidence_role"] == (
        "bts_reported_public_observation"
    )
    assert "FAA capacity" in observation_payload["not_interpreted_as"]
    assert {record.kind for record in observations.support_records} == {
        "public_observation"
    }
    scenario.store.close()


def test_event_graph_and_reviewed_paths_are_event_scoped(
    tmp_path: Path,
) -> None:
    scenario = _live_store(tmp_path)
    gateway = _gateway(scenario)

    graph = gateway.read_tmi_event_graph(event_id=FORMAL_EVENT_ID)
    paths = gateway.read_tmi_event_graph(
        event_id=FORMAL_EVENT_ID,
        view="evidence_paths",
    )

    assert graph.status == "ok"
    assert FORMAL_EVENT_ID in {
        edge["subject_iri"] for edge in json.loads(graph.content)["edges"]
    }
    assert MISSING_EVENT_ID not in {
        edge["subject_iri"] for edge in json.loads(graph.content)["edges"]
    }
    assert paths.status == "ok"
    assert {
        path.path_kind for path in paths.graph_paths
    } == {
        "weather_context_at_controlled_facility",
        "public_observation_at_controlled_facility",
    }
    assert {
        record.kind for record in paths.support_records
    } == {"non_causal_context", "public_observation"}
    scenario.store.close()


def test_similarity_is_optional_and_uses_live_event_index(
    tmp_path: Path,
) -> None:
    scenario = _live_store(tmp_path)
    missing = _gateway(scenario).find_similar_tmi_events(
        reference_event_id=FORMAL_EVENT_ID
    )
    available = _gateway(
        scenario,
        with_event_index=True,
    ).find_similar_tmi_events(
        reference_event_id=FORMAL_EVENT_ID,
        limit=2,
    )

    assert missing.status == "insufficient"
    assert "unavailable" in missing.limitation
    assert available.status == "ok"
    assert available.similarity_matches
    assert FORMAL_EVENT_ID not in {
        match.event_id for match in available.similarity_matches
    }
    assert {record.kind for record in available.support_records} == {
        "similarity"
    }
    scenario.store.close()
