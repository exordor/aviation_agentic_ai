"""Optional exports over the live aviation evidence store."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import rdflib

from aviation_agentic_ai.agent_system.contracts import (
    SourceFamily,
    ValidationProfileRef,
)
from aviation_agentic_ai.agent_system.evidence_export import (
    build_store_kg_projection,
    export_event,
)
from aviation_agentic_ai.agent_system.evidence_store import (
    AviationEvidenceStore,
)
from aviation_agentic_ai.agent_system.ingestion_package import (
    EventFactMembership,
    EventIngestionPackage,
    IngestionAttempt,
)
from aviation_agentic_ai.agent_system.knowledge_publication import (
    KnowledgePublicationPackage,
    KnowledgePublicationRecord,
    KnowledgeRootRecord,
    PublicationEvidenceLink,
    PublicationFactMembership,
    PublicationSourceMembership,
    stable_knowledge_publication_id,
)
from aviation_agentic_ai.agent_system.materialize import (
    _validate_neo4j_projection,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    EventEvidenceLink,
    EventWeatherAssociation,
    IngestionResult,
    SemanticFactRecord,
    SourceVersionRecord,
    TMIEventRecord,
)
from aviation_agentic_ai.utils.identifiers import stable_id


ATM = "https://data.nasa.gov/ontologies/atmonto/ATM#"
DATA = "https://data.nasa.gov/ontologies/atmonto/data#"
NAS = "https://data.nasa.gov/ontologies/atmonto/NAS#"
GEN = "https://data.nasa.gov/ontologies/atmonto/general#"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
EVENT_A = "urn:aviation-agentic-ai:event:A"
EVENT_B = "urn:aviation-agentic-ai:event:B"
FACILITY = "urn:aviation-agentic-ai:facility:airport:KJFK"
PROFILE = ValidationProfileRef(
    profile_id="profile:decision:export-test",
    profile_checksum="a" * 64,
    layer="decision",
)
WEATHER_PROFILE = ValidationProfileRef(
    profile_id="profile:weather:export-test",
    profile_checksum="b" * 64,
    layer="weather",
)
FLIGHT_PROFILE = ValidationProfileRef(
    profile_id="profile:flight:export-test",
    profile_checksum="c" * 64,
    layer="flight_operation",
)


def _jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _version(
    source_id: str,
    content: str,
    family: SourceFamily,
) -> SourceVersionRecord:
    checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return SourceVersionRecord(
        source_version_id=stable_id(
            "source-version",
            source_id,
            checksum,
        ),
        source_id=source_id,
        family=family,
        asset_id=None,
        content=content,
        content_sha256=checksum,
        source_url=f"https://example.test/{source_id}",
        logical_time="2026-05-20T11:00:00Z",
        metadata={},
    )


def _fact(
    fact_id: str,
    subject: str,
    predicate: str,
    object_value: str,
    *,
    object_kind: str = "iri",
    object_class_iri: str | None = None,
    profile: ValidationProfileRef = PROFILE,
    evidence_mode: str = "source_text",
) -> SemanticFactRecord:
    return SemanticFactRecord(
        fact_id=fact_id,
        subject_iri=subject,
        subject_class_iri=f"{ATM}TrafficManagementInitiative",
        predicate_iri=predicate,
        object_kind=object_kind,  # type: ignore[arg-type]
        object_value=object_value,
        object_class_iri=object_class_iri,
        datatype_iri=(
            "http://www.w3.org/2001/XMLSchema#string"
            if object_kind == "literal"
            else None
        ),
        validation_profile=profile,
        evidence_mode=evidence_mode,  # type: ignore[arg-type]
    )


def _publish(
    store: AviationEvidenceStore,
    *,
    event_id: str,
    advisory: SourceVersionRecord,
    facts: tuple[SemanticFactRecord, ...],
    links: tuple[EventEvidenceLink, ...],
    other_sources: tuple[SourceVersionRecord, ...] = (),
    weather: tuple[EventWeatherAssociation, ...] = (),
) -> TMIEventRecord:
    digest = hashlib.sha256(
        (
            advisory.source_version_id
            + "|"
            + "|".join(fact.fact_id for fact in facts)
        ).encode("utf-8")
    ).hexdigest()
    publication_id = stable_id(
        "knowledge-publication",
        event_id,
        advisory.source_version_id,
        digest,
    )
    event = TMIEventRecord(
        event_id=event_id,
        publication_id=publication_id,
        advisory_source_id=advisory.source_id,
        publication_source_version_id=advisory.source_version_id,
        event_type_iris=(f"{ATM}GroundDelayProgramTMI",),
        facility_ids=(FACILITY,),
        effective_start=datetime(2026, 5, 20, 12, tzinfo=UTC),
        effective_end=datetime(2026, 5, 20, 15, tzinfo=UTC),
        issued_at=datetime(2026, 5, 20, 11, tzinfo=UTC),
        reason_status="missing",
        reason_value=None,
    )
    scoped_links = tuple(
        link.model_copy(
            update={
                "event_id": event_id,
                "publication_id": publication_id,
            }
        )
        for link in links
    )
    scoped_weather = tuple(
        row.model_copy(
            update={
                "event_id": event_id,
                "publication_id": publication_id,
            }
        )
        for row in weather
    )
    package = EventIngestionPackage(
        event=event,
        formal_publication_digest=digest,
        source_version_ids=tuple(
            source.source_version_id
            for source in (advisory, *other_sources)
        ),
        source_anchors=(),
        facts=facts,
        event_fact_memberships=tuple(
            EventFactMembership(
                event_id=event_id,
                publication_id=publication_id,
                fact_id=fact.fact_id,
            )
            for fact in facts
        ),
        evidence_links=scoped_links,
        profile_gaps=(),
        weather_associations=scoped_weather,
        public_observations=(),
        observation_fact_ids={},
    )
    store.apply_ingestion_attempt(
        IngestionAttempt(
            result=IngestionResult(
                source_version_id=advisory.source_version_id,
                source_id=advisory.source_id,
                status="ok",
                event_id=event_id,
                publication_id=publication_id,
                reason="accepted",
                provider_call_count=0,
                tmi_family="ground_delay_program",
                preflight_eligible=True,
            ),
            package=package,
        )
    )
    return event


def _store(tmp_path: Path) -> tuple[AviationEvidenceStore, dict[str, object]]:
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:evidence-export",
        create=True,
    )
    advisory_a_old = _version(
        "source:advisory:A",
        "GDP FOR KJFK.",
        SourceFamily.ATCSCC_ADVISORY,
    )
    advisory_a = _version(
        "source:advisory:A",
        "GDP FOR KJFK. UPDATED.",
        SourceFamily.ATCSCC_ADVISORY,
    )
    weather = _version(
        "source:taf:KJFK",
        "TAF KJFK TEMPO TSRA.",
        SourceFamily.TAF,
    )
    advisory_b = _version(
        "source:advisory:B",
        "GDP FOR KEWR.",
        SourceFamily.ATCSCC_ADVISORY,
    )
    versions = (advisory_a_old, advisory_a, weather, advisory_b)
    anchors = {}
    for version in versions:
        store.register_source_version(version)
        anchors[version.source_version_id] = store.register_source_anchor(
            version.source_version_id,
            char_start=0,
            char_end=len(version.content),
        )

    old_fact = _fact(
        "fact:A:retired",
        EVENT_A,
        RDF_TYPE,
        f"{ATM}GroundDelayProgramTMI",
        object_class_iri=f"{ATM}GroundDelayProgramTMI",
    )
    _publish(
        store,
        event_id=EVENT_A,
        advisory=advisory_a_old,
        facts=(old_fact,),
        links=(
            EventEvidenceLink(
                evidence_link_id="link:A:retired",
                event_id=EVENT_A,
                publication_id="placeholder",
                owner_kind="fact",
                owner_id=old_fact.fact_id,
                source_version_id=advisory_a_old.source_version_id,
                source_anchor_id=anchors[
                    advisory_a_old.source_version_id
                ].source_anchor_id,
                evidence_text=advisory_a_old.content,
                evidence_ref="advisory:A:retired",
            ),
        ),
    )

    type_fact = _fact(
        "fact:A:type",
        EVENT_A,
        RDF_TYPE,
        f"{ATM}GroundDelayProgramTMI",
        object_class_iri=f"{ATM}GroundDelayProgramTMI",
    )
    facility_fact = _fact(
        "fact:A:facility",
        EVENT_A,
        f"{ATM}controlledNASelement",
        FACILITY,
        object_class_iri=f"{NAS}Airport",
    )
    weather_fact = _fact(
        "fact:A:weather",
        "urn:aviation-agentic-ai:taf:KJFK",
        f"{DATA}forecastingAirport",
        FACILITY,
        object_class_iri=f"{NAS}Airport",
        profile=WEATHER_PROFILE,
    )
    derived_fact = _fact(
        "fact:A:derived",
        EVENT_A,
        f"{ATM}hasStatus",
        "published",
        object_kind="literal",
        evidence_mode="deterministic_derivation",
    )
    fact_sources = {
        type_fact.fact_id: advisory_a,
        facility_fact.fact_id: advisory_a,
        weather_fact.fact_id: weather,
    }
    links = tuple(
        EventEvidenceLink(
            evidence_link_id=f"link:{fact.fact_id}",
            event_id=EVENT_A,
            publication_id="placeholder",
            owner_kind="fact",
            owner_id=fact.fact_id,
            source_version_id=source.source_version_id,
            source_anchor_id=anchors[
                source.source_version_id
            ].source_anchor_id,
            evidence_text=source.content,
            evidence_ref=f"{source.source_id}#record",
        )
        for fact, source in (
            (type_fact, fact_sources[type_fact.fact_id]),
            (facility_fact, fact_sources[facility_fact.fact_id]),
            (weather_fact, fact_sources[weather_fact.fact_id]),
        )
    ) + (
        EventEvidenceLink(
            evidence_link_id="link:fact:A:derived",
            event_id=EVENT_A,
            publication_id="placeholder",
            owner_kind="fact",
            owner_id=derived_fact.fact_id,
            source_version_id=advisory_a.source_version_id,
            source_anchor_id=None,
            evidence_text=None,
            evidence_ref="deterministic:event-status-v1",
        ),
    )
    association = EventWeatherAssociation(
        association_id="association:A:taf",
        event_id=EVENT_A,
        publication_id="placeholder",
        report_id="taf:KJFK",
        facility_id=FACILITY,
        relation_type="latest_forecast_known_at_issue",
        selection_method="test_temporal_join",
        relevant_times={"issued": "2026-05-20T11:00:00Z"},
        source_version_id=weather.source_version_id,
        causal_claim=False,
    )
    active_a = _publish(
        store,
        event_id=EVENT_A,
        advisory=advisory_a,
        facts=(type_fact, facility_fact, weather_fact, derived_fact),
        links=links,
        other_sources=(weather,),
        weather=(association,),
    )

    b_fact = _fact(
        "fact:B:type",
        EVENT_B,
        RDF_TYPE,
        f"{ATM}GroundDelayProgramTMI",
        object_class_iri=f"{ATM}GroundDelayProgramTMI",
    )
    active_b = _publish(
        store,
        event_id=EVENT_B,
        advisory=advisory_b,
        facts=(b_fact,),
        links=(
            EventEvidenceLink(
                evidence_link_id="link:B:type",
                event_id=EVENT_B,
                publication_id="placeholder",
                owner_kind="fact",
                owner_id=b_fact.fact_id,
                source_version_id=advisory_b.source_version_id,
                source_anchor_id=anchors[
                    advisory_b.source_version_id
                ].source_anchor_id,
                evidence_text=advisory_b.content,
                evidence_ref="source:advisory:B#record",
            ),
        ),
    )
    return store, {
        "active_a": active_a,
        "active_b": active_b,
        "advisory_a_old": advisory_a_old,
        "advisory_a": advisory_a,
        "weather": weather,
        "association": association,
    }


def _publish_flight_graph(store: AviationEvidenceStore) -> tuple[str, set[str]]:
    source = _version(
        "source:flight:DL100",
        "DL100 KATL-KJFK route R1 crossed ZTL sector 42.",
        SourceFamily.BTS_FLIGHT_OPERATION,
    )
    store.register_source_version(source)
    anchor = store.register_source_anchor(
        source.source_version_id,
        char_start=0,
        char_end=len(source.content),
    )
    flight_id = "urn:nasa:flight:DL100"
    route_id = "urn:nasa:route:DL100"
    point_id = "urn:nasa:track-point:DL100:1"
    fix_id = "urn:nasa:fix:ATL01"
    sector_id = "urn:nasa:sector:ZTL42"
    facts = (
        SemanticFactRecord(
            fact_id="fact:flight:type",
            subject_iri=flight_id,
            subject_class_iri=f"{ATM}Flight",
            predicate_iri=RDF_TYPE,
            object_kind="iri",
            object_value=f"{ATM}Flight",
            object_class_iri=f"{ATM}Flight",
            datatype_iri=None,
            validation_profile=FLIGHT_PROFILE,
            evidence_mode="source_text",
        ),
        SemanticFactRecord(
            fact_id="fact:flight:route",
            subject_iri=flight_id,
            subject_class_iri=f"{ATM}Flight",
            predicate_iri=f"{ATM}hasActualRoute",
            object_kind="iri",
            object_value=route_id,
            object_class_iri=f"{ATM}ActualFlightRoute",
            datatype_iri=None,
            validation_profile=FLIGHT_PROFILE,
            evidence_mode="source_text",
        ),
        SemanticFactRecord(
            fact_id="fact:route:point",
            subject_iri=route_id,
            subject_class_iri=f"{ATM}ActualFlightRoute",
            predicate_iri=f"{GEN}hasSequencedItem",
            object_kind="iri",
            object_value=point_id,
            object_class_iri=f"{ATM}AircraftTrackPoint",
            datatype_iri=None,
            validation_profile=FLIGHT_PROFILE,
            evidence_mode="source_text",
        ),
        SemanticFactRecord(
            fact_id="fact:point:fix",
            subject_iri=point_id,
            subject_class_iri=f"{ATM}AircraftTrackPoint",
            predicate_iri=f"{ATM}aircraftFix",
            object_kind="iri",
            object_value=fix_id,
            object_class_iri=f"{ATM}NavigationFix",
            datatype_iri=None,
            validation_profile=FLIGHT_PROFILE,
            evidence_mode="source_text",
        ),
        SemanticFactRecord(
            fact_id="fact:fix:sector",
            subject_iri=fix_id,
            subject_class_iri=f"{ATM}NavigationFix",
            predicate_iri=f"{ATM}locatedInSector",
            object_kind="iri",
            object_value=sector_id,
            object_class_iri=f"{NAS}Sector",
            datatype_iri=None,
            validation_profile=FLIGHT_PROFILE,
            evidence_mode="source_text",
        ),
    )
    digest = hashlib.sha256(
        "|".join(fact.fact_id for fact in facts).encode("utf-8")
    ).hexdigest()
    publication_id = stable_knowledge_publication_id(
        flight_id,
        source.source_version_id,
        digest,
    )
    package = KnowledgePublicationPackage(
        root=KnowledgeRootRecord(
            root_id=flight_id,
            root_kind="flight",
            temporal_domain_id="test-flight-domain",
            active_publication_id=publication_id,
        ),
        publication=KnowledgePublicationRecord(
            publication_id=publication_id,
            root_id=flight_id,
            temporal_domain_id="test-flight-domain",
            primary_source_version_id=source.source_version_id,
            formal_publication_digest=digest,
        ),
        publication_sources=(
            PublicationSourceMembership(
                membership_id=stable_id(
                    "publication-source",
                    publication_id,
                    source.source_version_id,
                    "primary",
                ),
                publication_id=publication_id,
                source_version_id=source.source_version_id,
                source_role="primary",
            ),
        ),
        source_anchors=(anchor,),
        facts=facts,
        fact_memberships=tuple(
            PublicationFactMembership(
                membership_id=stable_id(
                    "publication-fact",
                    publication_id,
                    fact.fact_id,
                ),
                publication_id=publication_id,
                fact_id=fact.fact_id,
            )
            for fact in facts
        ),
        evidence_links=tuple(
            PublicationEvidenceLink(
                evidence_link_id=stable_id(
                    "publication-evidence",
                    publication_id,
                    "fact",
                    fact.fact_id,
                    source.source_version_id,
                    anchor.source_anchor_id,
                    "full_record",
                ),
                publication_id=publication_id,
                owner_kind="fact",
                owner_id=fact.fact_id,
                source_version_id=source.source_version_id,
                source_anchor_id=anchor.source_anchor_id,
                evidence_text=source.content,
                evidence_ref="full_record",
            )
            for fact in facts
        ),
    )
    store.apply_knowledge_publication(package)
    return flight_id, {fact.fact_id for fact in facts}


def test_export_event_isolates_active_event_and_exact_source_versions(
    tmp_path: Path,
) -> None:
    store, rows = _store(tmp_path)

    manifest_path = export_event(store, EVENT_A, tmp_path / "event-export")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    output_dir = manifest_path.parent
    event = json.loads((output_dir / "event.json").read_text(encoding="utf-8"))
    fact_ids = {row["fact_id"] for row in _jsonl(output_dir / "facts.jsonl")}
    versions = {
        row["source_version_id"]
        for row in _jsonl(output_dir / "source_versions.jsonl")
    }
    links = _jsonl(output_dir / "evidence_links.jsonl")
    anchor_ids = {
        row["source_anchor_id"]
        for row in _jsonl(output_dir / "source_anchors.jsonl")
    }

    assert manifest["format"] == "aviation-event-export-v1"
    assert event["event_id"] == EVENT_A
    assert event["publication_id"] == rows["active_a"].publication_id
    assert fact_ids == {
        "fact:A:type",
        "fact:A:facility",
        "fact:A:weather",
        "fact:A:derived",
    }
    assert "fact:A:retired" not in fact_ids
    assert "fact:B:type" not in fact_ids
    assert versions == {
        rows["advisory_a"].source_version_id,
        rows["weather"].source_version_id,
    }
    assert rows["advisory_a_old"].source_version_id not in versions
    assert any(
        row["owner_id"] == "fact:A:derived"
        and row["source_anchor_id"] is None
        and row["evidence_ref"] == "deterministic:event-status-v1"
        for row in links
    )
    assert None not in anchor_ids
    assert {
        row["source_anchor_id"]
        for row in links
        if row["source_anchor_id"] is not None
    } <= anchor_ids
    assert all(
        row["event_id"] == EVENT_A
        and row["publication_id"] == rows["active_a"].publication_id
        for row in links
    )


def test_store_kg_projection_equals_active_facts_and_excludes_context(
    tmp_path: Path,
) -> None:
    store, rows = _store(tmp_path)

    projection = build_store_kg_projection(store, tmp_path / "kg-export")

    kg_rows = _jsonl(Path(projection.jsonl_path))
    projected_fact_ids = {row["fact_id"] for row in kg_rows}
    active_fact_ids = {
        fact.fact_id
        for event in store.list_tmi_event_publications(active_only=True)
        for fact in store.get_event_facts(
            event.event_id,
            publication_id=event.publication_id,
        )
    }
    graph = rdflib.Graph().parse(projection.ttl_path, format="turtle")
    exported_text = Path(projection.jsonl_path).read_text(encoding="utf-8")

    assert projected_fact_ids == active_fact_ids
    assert "fact:A:retired" not in projected_fact_ids
    assert "fact:A:weather" in projected_fact_ids
    assert rows["association"].association_id not in exported_text
    assert (
        rdflib.URIRef("urn:aviation-agentic-ai:taf:KJFK"),
        rdflib.URIRef(f"{DATA}forecastingAirport"),
        rdflib.URIRef(FACILITY),
    ) in graph
    assert projection.fact_count == len(active_fact_ids)
    assert Path(projection.manifest_path).exists()


def test_store_kg_projection_includes_all_active_knowledge_roots(
    tmp_path: Path,
) -> None:
    store, rows = _store(tmp_path)
    flight_id, flight_fact_ids = _publish_flight_graph(store)

    projection = build_store_kg_projection(store, tmp_path / "mixed-kg")

    kg_rows = _jsonl(Path(projection.jsonl_path))
    fact_ids = {row["fact_id"] for row in kg_rows}
    manifest = json.loads(Path(projection.manifest_path).read_text())
    node_rows = _jsonl(Path(projection.nodes_path))
    relationship_rows = _jsonl(Path(projection.relationships_path))
    labels_by_id = {row["id"]: row["label"] for row in node_rows}

    assert flight_fact_ids <= fact_ids
    assert manifest["format"] == "aviation-evidence-kg-export-v2"
    assert manifest["formal_root_kind_counts"] == {
        "flight": 1,
        "tmi_event": 2,
    }
    assert projection.root_count == 3
    assert projection.root_kind_counts == {"flight": 1, "tmi_event": 2}
    flight_row = next(row for row in kg_rows if row["fact_id"] == "fact:flight:route")
    assert flight_row["publication_bindings"][0]["root_id"] == flight_id
    assert flight_row["publication_bindings"][0]["root_kind"] == "flight"
    assert labels_by_id[flight_id] == "Flight"
    assert labels_by_id["urn:nasa:route:DL100"] == "FlightRoute"
    assert labels_by_id["urn:nasa:track-point:DL100:1"] == "TrackPoint"
    assert labels_by_id["urn:nasa:fix:ATL01"] == "NavigationFix"
    assert labels_by_id["urn:nasa:sector:ZTL42"] == "Sector"
    assert {
        row["type"]
        for row in relationship_rows
        if row["start_id"].startswith("urn:nasa:")
    } >= {
        "HAS_ACTUAL_ROUTE",
        "HAS_SEQUENCED_ITEM",
        "AIRCRAFT_FIX",
        "LOCATED_IN_SECTOR",
    }
    route_relationship = next(
        row
        for row in relationship_rows
        if row["type"] == "HAS_ACTUAL_ROUTE"
    )
    assert route_relationship["properties"]["root_ids"] == [flight_id]
    assert route_relationship["properties"]["root_kinds"] == ["flight"]
    assert route_relationship["properties"]["publication_ids"]
    assert route_relationship["properties"]["source_version_ids"]
    _validate_neo4j_projection(node_rows, relationship_rows)
    exported = Path(projection.jsonl_path).read_text(encoding="utf-8")
    assert rows["association"].association_id not in exported
