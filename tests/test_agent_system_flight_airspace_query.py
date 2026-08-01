"""Store-backed Flight/Airspace query behavior over accepted publications."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from langchain_core.messages import AIMessage

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryAnswer,
    HybridQueryScope,
    HybridQueryStatement,
    ModelCallRecord,
    ModelToolCall,
    SourceFamily,
)
from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.flight_airspace_contracts import (
    ARTCCRecord,
    AirportARTCCAssignmentRecord,
    AirportRecord,
    FlightAirspaceMaterialization,
    FlightPublicationRecord,
    FlightRecord,
    RouteRecord,
    SectorPassageRecord,
    SectorRecord,
    TrackPointRecord,
    TMIPublicationRecord,
    WeatherObservationRecord,
)
from aviation_agentic_ai.agent_system.cross_source_associations import (
    materialize_cross_source_associations,
)
from aviation_agentic_ai.agent_system.flight_airspace_query import (
    AirportQuery,
    FlightAirspaceQueryService,
    FlightQuery,
    SectorPassageQuery,
    TMIApplicabilityQuery,
)
from aviation_agentic_ai.agent_system.flight_airspace_query_tools import (
    FlightAirspaceQueryGateway,
    build_flight_airspace_query_tools,
)
from aviation_agentic_ai.agent_system.knowledge_publication import (
    KnowledgePublicationPackage,
    KnowledgePublicationRecord,
    KnowledgeRootRecord,
    PublicationEvidenceLink,
    PublicationSourceMembership,
    stable_knowledge_publication_id,
)
from aviation_agentic_ai.agent_system.knowledge_query import answer_question
from aviation_agentic_ai.agent_system.storage_contracts import SourceVersionRecord
from aviation_agentic_ai.agent_system.query_runtime import QueryRuntime
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
from aviation_agentic_ai.utils.identifiers import stable_id


DOMAIN = "nasa-atmonto-2014"
SECTOR_ID = "https://data.nasa.gov/ontologies/atmonto/NAS#ZTLsector040"


def _source(
    store: AviationEvidenceStore,
    *,
    source_id: str,
    content: str,
    family: SourceFamily = SourceFamily.NASA_ATMONTO_INSTANCE,
) -> SourceVersionRecord:
    checksum = hashlib.sha256(content.encode()).hexdigest()
    version = SourceVersionRecord(
        source_version_id=stable_id("source-version", source_id, checksum),
        source_id=source_id,
        family=family,
        asset_id=None,
        content=content,
        content_sha256=checksum,
        source_url=None,
        logical_time="2014-07-15T00:00:00+00:00",
        metadata={"temporal_domain_id": DOMAIN},
    )
    store.register_source_version(version)
    return version


def _package(
    store: AviationEvidenceStore,
    *,
    root_id: str,
    root_kind: str,
    source: SourceVersionRecord,
) -> KnowledgePublicationPackage:
    digest = hashlib.sha256(
        f"{root_id}|{source.source_version_id}".encode()
    ).hexdigest()
    publication_id = stable_knowledge_publication_id(
        root_id,
        source.source_version_id,
        digest,
    )
    anchor = store.register_source_anchor(
        source.source_version_id,
        char_start=0,
        char_end=len(source.content),
    )
    return KnowledgePublicationPackage(
        root=KnowledgeRootRecord(
            root_id=root_id,
            root_kind=root_kind,
            temporal_domain_id=DOMAIN,
            active_publication_id=publication_id,
        ),
        publication=KnowledgePublicationRecord(
            publication_id=publication_id,
            root_id=root_id,
            temporal_domain_id=DOMAIN,
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
        facts=(),
        fact_memberships=(),
        evidence_links=(
            PublicationEvidenceLink(
                evidence_link_id=stable_id(
                    "publication-evidence",
                    publication_id,
                    "structured_record",
                    root_id,
                    source.source_version_id,
                    anchor.source_anchor_id,
                    "record",
                ),
                publication_id=publication_id,
                owner_kind="structured_record",
                owner_id=root_id,
                source_version_id=source.source_version_id,
                source_anchor_id=anchor.source_anchor_id,
                evidence_text=source.content,
                evidence_ref="record",
            ),
        ),
    )


def _flight_materialization(
    store: AviationEvidenceStore,
    *,
    label: str,
    call_sign: str,
    reporting_time: datetime,
    sequence_number: int,
) -> FlightAirspaceMaterialization:
    source = _source(
        store,
        source_id=f"nasa-flight:{label}",
        content=f"Flight {label} {call_sign} at {reporting_time.isoformat()}",
    )
    flight_id = stable_id(
        "flight",
        SourceFamily.NASA_ATMONTO_INSTANCE.value,
        "2014-07-15",
        "DAL",
        label,
        "KATL",
        "KJFK",
        f"2014-07-15T02:{sequence_number:02d}:00Z",
    )
    package = _package(
        store,
        root_id=flight_id,
        root_kind="flight",
        source=source,
    )
    publication_id = package.publication.publication_id
    route = RouteRecord(
        route_id=stable_id("route", publication_id, f"actual:{label}"),
        flight_publication_id=publication_id,
        temporal_domain_id=DOMAIN,
        source_route_key=f"actual:{label}",
        route_kind="actual",
    )
    anchor = package.source_anchors[0]
    point = TrackPointRecord(
        track_point_id=stable_id(
            "track-point",
            route.route_id,
            sequence_number,
            source.source_version_id,
            anchor.source_anchor_id,
        ),
        route_id=route.route_id,
        temporal_domain_id=DOMAIN,
        sequence_number=sequence_number,
        reporting_time=reporting_time,
        latitude=33.63,
        longitude=-84.44,
        ground_speed=420.0,
        navigation_fix_id=None,
        sector_ids=(SECTOR_ID,),
        source_version_id=source.source_version_id,
        source_anchor_id=anchor.source_anchor_id,
    )
    derivation_id = f"derivation:sector:{label}"
    passage = SectorPassageRecord(
        passage_id=stable_id(
            "sector-passage",
            publication_id,
            point.track_point_id,
            SECTOR_ID,
            derivation_id,
        ),
        flight_publication_id=publication_id,
        route_id=route.route_id,
        track_point_id=point.track_point_id,
        sector_id=SECTOR_ID,
        temporal_domain_id=DOMAIN,
        reporting_time=reporting_time,
        derivation_id=derivation_id,
    )
    flight = FlightRecord(
        flight_id=flight_id,
        temporal_domain_id=DOMAIN,
        source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
        service_date=date(2014, 7, 15),
        reporting_carrier="DAL",
        flight_number=label,
        origin_airport_id="KATL",
        destination_airport_id="KJFK",
        scheduled_departure_key=f"2014-07-15T02:{sequence_number:02d}:00Z",
        tail_number=None,
        scheduled_departure=datetime(2014, 7, 15, 2, tzinfo=UTC),
        actual_wheels_off=datetime(2014, 7, 15, 2, tzinfo=UTC),
        time_basis="utc",
        cancelled=False,
        diverted=False,
    )
    return FlightAirspaceMaterialization(
        publication=package,
        flight=flight,
        flight_publication=FlightPublicationRecord(
            publication_id=publication_id,
            flight_id=flight_id,
            temporal_domain_id=DOMAIN,
            primary_source_version_id=source.source_version_id,
        ),
        routes=(route,),
        track_points=(point,),
        sector_passages=(passage,),
    )


def _store_with_trajectory(tmp_path: Path) -> AviationEvidenceStore:
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="dataset:flight-query",
        create=True,
    )
    sector_source = _source(
        store,
        source_id="nasa-sector:ztl040",
        content="ZTL sector 040",
    )
    sector_package = _package(
        store,
        root_id=SECTOR_ID,
        root_kind="sector",
        source=sector_source,
    )
    store.apply_flight_airspace_publication(
        FlightAirspaceMaterialization(
            publication=sector_package,
            sectors=(
                SectorRecord(
                    sector_id=SECTOR_ID,
                    temporal_domain_id=DOMAIN,
                    source_family=SourceFamily.NASA_ATMONTO_INSTANCE,
                    sector_identifier="ZTLsector040",
                ),
            ),
        )
    )
    store.apply_flight_airspace_publication(
        _flight_materialization(
            store,
            label="101",
            call_sign="DAL101",
            reporting_time=datetime(2014, 7, 15, 2, 0, 0, tzinfo=UTC),
            sequence_number=1,
        )
    )
    store.apply_flight_airspace_publication(
        _flight_materialization(
            store,
            label="102",
            call_sign="DAL102",
            reporting_time=datetime(2014, 7, 15, 2, 25, 25, tzinfo=UTC),
            sequence_number=2,
        )
    )
    return store


def test_active_flight_filters_and_trajectory_round_trip(tmp_path: Path) -> None:
    store = _store_with_trajectory(tmp_path)
    try:
        service = FlightAirspaceQueryService(store)
        page = service.find_flights(
            FlightQuery(
                reporting_carrier="DAL",
                origin_airport_id="KATL",
                temporal_domain_id=DOMAIN,
                limit=10,
            )
        )

        assert page.total_matches == 2
        assert [row.flight_number for row in page.flights] == ["101", "102"]
        trajectory = service.get_flight_route(page.flights[0].flight_id)
        assert len(trajectory.routes) == 1
        assert trajectory.routes[0].route_kind == "actual"
        assert trajectory.track_points[0].sequence_number == 1
        assert trajectory.track_points[0].sector_ids == (SECTOR_ID,)
        assert trajectory.track_points[0].ground_speed == 420.0
    finally:
        store.close()


def test_new_publication_reuses_stable_flight_identity(tmp_path: Path) -> None:
    store = _store_with_trajectory(tmp_path)
    try:
        first = _flight_materialization(
            store,
            label="103",
            call_sign="DAL103",
            reporting_time=datetime(2014, 7, 15, 2, 40, tzinfo=UTC),
            sequence_number=3,
        )
        store.apply_flight_airspace_publication(first)
        assert first.flight is not None

        replacement_source = _source(
            store,
            source_id="nasa-flight:103",
            content="Corrected Flight 103 record",
        )
        replacement_package = _package(
            store,
            root_id=first.flight.flight_id,
            root_kind="flight",
            source=replacement_source,
        )
        replacement = FlightAirspaceMaterialization(
            publication=replacement_package,
            flight=first.flight.model_copy(
                update={
                    "actual_wheels_off": datetime(
                        2014, 7, 15, 2, 10, tzinfo=UTC
                    )
                }
            ),
            flight_publication=FlightPublicationRecord(
                publication_id=replacement_package.publication.publication_id,
                flight_id=first.flight.flight_id,
                temporal_domain_id=DOMAIN,
                primary_source_version_id=(
                    replacement_source.source_version_id
                ),
            ),
        )

        assert store.apply_flight_airspace_publication(replacement) == "activated"
        active = FlightAirspaceQueryService(store).get_flight(
            first.flight.flight_id
        )
        assert active is not None
        assert active.publication_id == replacement_package.publication.publication_id
        assert active.actual_wheels_off == datetime(
            2014, 7, 15, 2, 10, tzinfo=UTC
        )
    finally:
        store.close()


def test_sector_analysis_uses_half_open_interval_and_exact_seconds(
    tmp_path: Path,
) -> None:
    store = _store_with_trajectory(tmp_path)
    try:
        service = FlightAirspaceQueryService(store)
        start = datetime(2014, 7, 15, 2, tzinfo=UTC)
        end = datetime(2014, 7, 15, 3, tzinfo=UTC)

        ranking = service.rank_sector_traffic(start=start, end=end, limit=5)
        assert ranking.rows[0].sector_id == SECTOR_ID
        assert ranking.rows[0].distinct_flight_count == 2
        assert ranking.rows[0].passage_count == 2
        assert ranking.derivation.normalized_parameters["interval"] == {
            "start": "2014-07-15T02:00:00+00:00",
            "end": "2014-07-15T03:00:00+00:00",
            "boundary": "half_open",
        }

        pairs = service.find_close_sector_passage_pairs(
            sector_id=SECTOR_ID,
            start=start,
            end=end,
            max_seconds=1800,
        )
        assert len(pairs.rows) == 1
        assert pairs.rows[0].seconds_apart == 1525
        assert pairs.rows[0].first_flight_id != pairs.rows[0].second_flight_id
    finally:
        store.close()


def test_weather_association_nearest_and_all_remain_non_causal(
    tmp_path: Path,
) -> None:
    store = _store_with_trajectory(tmp_path)
    try:
        flight = FlightAirspaceQueryService(store).find_flights(
            FlightQuery(flight_number="101", limit=10)
        ).flights[0]
        weather_source = _source(
            store,
            source_id="iem:katl:2014-07-15T02:10Z",
            content="KATL 150210Z 18010KT 5SM RA BKN020",
            family=SourceFamily.HISTORICAL_METAR_SPECI,
        )
        observation_id = stable_id(
            "weather-observation",
            SourceFamily.HISTORICAL_METAR_SPECI.value,
            "KATL",
            "2014-07-15T02:10:00+00:00",
            weather_source.source_version_id,
        )
        weather_package = _package(
            store,
            root_id=observation_id,
            root_kind="weather_observation",
            source=weather_source,
        )
        weather_publication_id = weather_package.publication.publication_id
        store.apply_flight_airspace_publication(
            FlightAirspaceMaterialization(
                publication=weather_package,
                weather_observations=(
                    WeatherObservationRecord(
                        observation_id=observation_id,
                        publication_id=weather_publication_id,
                        temporal_domain_id=DOMAIN,
                        source_family=SourceFamily.HISTORICAL_METAR_SPECI,
                        station_id="KATL",
                        observed_at=datetime(2014, 7, 15, 2, 10, tzinfo=UTC),
                        report_type="METAR",
                        raw_report=weather_source.content,
                        phenomenon_tokens=("RA",),
                        source_version_id=weather_source.source_version_id,
                        time_basis="utc",
                    ),
                ),
            )
        )
        associations = materialize_cross_source_associations(
            store=store,
            temporal_domain_id=DOMAIN,
        )
        association_id = next(
            row.association_id
            for row in associations.flight_weather_associations
            if row.flight_publication_id == flight.publication_id
        )

        service = FlightAirspaceQueryService(store)
        nearest = service.find_flight_weather_associations(
            flight_id=flight.flight_id,
            match_mode="nearest",
        )
        all_matches = service.find_flight_weather_associations(
            flight_id=flight.flight_id,
            match_mode="all",
        )

        assert len(nearest) == len(all_matches) == 1
        assert nearest[0].association_id == association_id
        assert nearest[0].phenomenon_tokens == ("RA",)
        assert nearest[0].causal_claim is False
        assert set(nearest[0].source_ids) == {
            "nasa-flight:101",
            "iem:katl:2014-07-15T02:10Z",
        }
        assert len(nearest[0].source_version_ids) == 2
    finally:
        store.close()


def test_reference_passage_and_applicability_queries_are_generic(
    tmp_path: Path,
) -> None:
    store = _store_with_trajectory(tmp_path)
    try:
        artcc_source = _source(
            store,
            source_id="nasr:artcc:ztl",
            content="ARTCC ZTL",
            family=SourceFamily.NASR_AIRSPACE,
        )
        artcc_id = stable_id(
            "artcc", SourceFamily.NASR_AIRSPACE.value, "ZTL"
        )
        artcc_package = _package(
            store,
            root_id=artcc_id,
            root_kind="artcc",
            source=artcc_source,
        )
        store.apply_flight_airspace_publication(
            FlightAirspaceMaterialization(
                publication=artcc_package,
                artccs=(
                    ARTCCRecord(
                        artcc_id=artcc_id,
                        temporal_domain_id=DOMAIN,
                        source_family=SourceFamily.NASR_AIRSPACE,
                        artcc_code="ZTL",
                        display_name="Atlanta Center",
                    ),
                ),
            )
        )

        airport_source = _source(
            store,
            source_id="nasr:airport:katl",
            content="Airport KATL",
            family=SourceFamily.NASR_AIRSPACE,
        )
        airport_id = stable_id(
            "airport", SourceFamily.NASR_AIRSPACE.value, "KATL"
        )
        airport_package = _package(
            store,
            root_id=airport_id,
            root_kind="airport",
            source=airport_source,
        )
        assignment_checksum = "b" * 64
        assignment_id = stable_id(
            "airport-artcc-assignment",
            airport_package.publication.publication_id,
            artcc_package.publication.publication_id,
            "responsible",
            "",
            "",
            assignment_checksum,
        )
        store.apply_flight_airspace_publication(
            FlightAirspaceMaterialization(
                publication=airport_package,
                airports=(
                    AirportRecord(
                        airport_id=airport_id,
                        temporal_domain_id=DOMAIN,
                        source_family=SourceFamily.NASR_AIRSPACE,
                        airport_code="KATL",
                        display_name="Hartsfield-Jackson Atlanta",
                    ),
                ),
                airport_artcc_assignments=(
                    AirportARTCCAssignmentRecord(
                        assignment_id=assignment_id,
                        airport_publication_id=(
                            airport_package.publication.publication_id
                        ),
                        artcc_publication_id=(
                            artcc_package.publication.publication_id
                        ),
                        temporal_domain_id=DOMAIN,
                        assignment_role="responsible",
                        procedure_id="nasr-artcc-assignment-v1",
                        procedure_checksum=assignment_checksum,
                        derivation_id="derivation:airport-artcc:katl",
                    ),
                ),
            )
        )

        flight = FlightAirspaceQueryService(store).find_flights(
            FlightQuery(flight_number="101", limit=1)
        ).flights[0]
        tmi_source = _source(
            store,
            source_id="atcscc:2014:001",
            content="TMI for KJFK",
            family=SourceFamily.ATCSCC_ADVISORY,
        )
        tmi_package = _package(
            store,
            root_id="urn:tmi:2014:001",
            root_kind="tmi",
            source=tmi_source,
        )
        store.apply_flight_airspace_publication(
            FlightAirspaceMaterialization(
                publication=tmi_package,
                tmi_publications=(
                    TMIPublicationRecord(
                        tmi_id="urn:tmi:2014:001",
                        publication_id=tmi_package.publication.publication_id,
                        temporal_domain_id=DOMAIN,
                        source_family=SourceFamily.ATCSCC_ADVISORY,
                        tmi_type="GroundDelayProgramTMI",
                        controlled_element_id="KJFK",
                        airport_id="KJFK",
                        departure_scope_declared=True,
                        departure_scope_airport_ids=("KATL",),
                        issued_at=datetime(
                            2014, 7, 15, 1, 30, tzinfo=UTC
                        ),
                        effective_from=datetime(
                            2014, 7, 15, 1, 30, tzinfo=UTC
                        ),
                        effective_to=datetime(
                            2014, 7, 15, 2, 30, tzinfo=UTC
                        ),
                        source_version_id=tmi_source.source_version_id,
                    ),
                ),
            )
        )
        associations = materialize_cross_source_associations(
            store=store,
            temporal_domain_id=DOMAIN,
        )
        applicability_id = next(
            row.applicability_id
            for row in associations.tmi_applicability
            if row.flight_publication_id == flight.publication_id
        )

        service = FlightAirspaceQueryService(store)
        airports = service.find_airports(
            AirportQuery(artcc_code="ZTL", assignment_role="responsible")
        )
        assert airports.total_matches == 1
        assert airports.airports[0].airport_code == "KATL"
        assert airports.airports[0].assignment_ids == (assignment_id,)

        passages = service.find_sector_passages(
            SectorPassageQuery(sector_id=SECTOR_ID, flight_id=flight.flight_id)
        )
        assert passages.total_matches == 1
        assert passages.passages[0].flight_id == flight.flight_id

        candidates = service.find_tmi_applicability_candidates(
            TMIApplicabilityQuery(flight_id=flight.flight_id)
        )
        assert candidates.total_matches == 1
        assert candidates.candidates[0].applicability_id == applicability_id
        assert candidates.candidates[0].actual_control_claim is False

        by_human_reference = service.find_tmi_applicability_candidates(
            TMIApplicabilityQuery(tmi_reference="TMI 001")
        )
        assert by_human_reference.total_matches == 2
        assert {
            row.tmi_root_id for row in by_human_reference.candidates
        } == {"urn:tmi:2014:001"}
    finally:
        store.close()


def test_generic_query_tools_return_typed_agent_evidence(tmp_path: Path) -> None:
    store = _store_with_trajectory(tmp_path)
    try:
        runtime = QueryRuntime(store=store, source_index=None, event_index=None)
        gateway = FlightAirspaceQueryGateway(
            runtime=runtime,
            scope=HybridQueryScope(limit=10),
        )
        tools = {
            tool.name: tool
            for tool in build_flight_airspace_query_tools(gateway)
        }

        flights = tools["find_flights"].invoke(
            {"reporting_carrier": "DAL", "origin_airport_id": "KATL"}
        )
        assert flights["status"] == "ok"
        assert len(flights["details"]["flight_ids"]) == 2
        assert flights["support_records"][0]["kind"] == "flight_fact"
        assert flights["support_records"][0]["source_ids"] == []
        assert "source_ids" not in json.loads(flights["content"])["flights"][0]

        analysis = tools["analyze_sector_traffic"].invoke(
            {
                "analysis": "close_pairs",
                "sector_id": SECTOR_ID,
                "start": "2014-07-15T02:00:00Z",
                "end": "2014-07-15T03:00:00Z",
                "max_seconds": 1800,
            }
        )
        assert analysis["status"] == "ok"
        assert len(analysis["details"]["derivation_ids"]) == 1
        assert analysis["support_records"][0]["kind"] == "aggregate_result"
        assert analysis["details"]["root_ids"] == [SECTOR_ID]
        assert analysis["support_records"][0]["source_ids"] == []
        assert "1525" in analysis["content"]
        compact_analysis = json.loads(analysis["content"])
        assert "input_source_version_ids" not in compact_analysis["derivation"]
        assert compact_analysis["derivation"]["input_source_version_count"] > 0
        assert "passage_ids" not in compact_analysis["rows"][0]

        bounded_gateway = FlightAirspaceQueryGateway(
            runtime=runtime,
            scope=HybridQueryScope(
                start=datetime(2014, 7, 15, 2, tzinfo=UTC),
                end=datetime(2014, 7, 15, 3, tzinfo=UTC),
                limit=10,
            ),
        )
        bounded_tools = {
            tool.name: tool
            for tool in build_flight_airspace_query_tools(bounded_gateway)
        }
        narrower = bounded_tools["analyze_sector_traffic"].invoke(
            {
                "analysis": "ranking",
                "start": "2014-07-15T02:20:00Z",
                "end": "2014-07-15T02:30:00Z",
                "limit": 5,
            }
        )
        payload = json.loads(narrower["content"])
        assert payload["derivation"]["normalized_parameters"]["interval"] == {
            "boundary": "half_open",
            "end": "2014-07-15T02:30:00+00:00",
            "start": "2014-07-15T02:20:00+00:00",
        }
        assert payload["rows"][0]["distinct_flight_count"] == 1

        source_scoped_gateway = FlightAirspaceQueryGateway(
            runtime=runtime,
            scope=HybridQueryScope(
                source_ids=("nasa-flight:102",),
                limit=1,
            ),
        )
        source_scoped_tools = {
            tool.name: tool
            for tool in build_flight_airspace_query_tools(
                source_scoped_gateway
            )
        }
        scoped = source_scoped_tools["find_flights"].invoke(
            {"reporting_carrier": "DAL", "limit": 1}
        )
        scoped_payload = json.loads(scoped["content"])
        assert scoped_payload["total_matches"] == 1
        assert scoped_payload["flights"][0]["flight_number"] == "102"
    finally:
        store.close()


def test_natural_language_query_agent_selects_generic_flight_tool(
    tmp_path: Path,
) -> None:
    store = _store_with_trajectory(tmp_path)
    try:
        flight = FlightAirspaceQueryService(store).find_flights(
            FlightQuery(flight_number="101", limit=1)
        ).flights[0]

        class FlightQueryModel:
            def __init__(self) -> None:
                self.turn = 0

            def invoke(
                self,
                messages: list[Any],
                *,
                phase: str,
            ) -> ToolModelTurn:
                assert phase == "query_step"
                self.turn += 1
                if self.turn == 1:
                    call = {
                        "id": "find-flight",
                        "name": "find_flights",
                        "args": {
                            "reporting_carrier": "DAL",
                            "flight_number": "101",
                        },
                    }
                    return ToolModelTurn(
                        message=AIMessage(content="", tool_calls=[call]),
                        record=ModelCallRecord(
                            agent="query",
                            raw_response="",
                            provider="scripted",
                            model="scripted",
                            tool_calls=(
                                ModelToolCall(
                                    call_id="find-flight",
                                    name="find_flights",
                                    arguments=call["args"],
                                ),
                            ),
                        ),
                    )
                answer = HybridQueryAnswer(
                    status="ok",
                    statements=(
                        HybridQueryStatement(
                            kind="flight_fact",
                            text="DAL flight 101 is recorded from KATL to KJFK.",
                            support_flight_ids=(flight.flight_id,),
                            support_publication_ids=(flight.publication_id,),
                        ),
                    ),
                ).model_dump_json()
                return ToolModelTurn(
                    message=AIMessage(content=answer),
                    record=ModelCallRecord(
                        agent="query",
                        raw_response=answer,
                        provider="scripted",
                        model="scripted",
                        attempt=2,
                    ),
                )

        available_tool_sets: list[set[str]] = []

        class RouterModel:
            def invoke(
                self,
                messages: list[Any],
                *,
                phase: str,
            ) -> ToolModelTurn:
                assert phase == "select_tool"
                call = {
                    "id": "route-flight",
                    "name": "select_query_tool_families",
                    "args": {"families": ["flight_airspace"]},
                }
                return ToolModelTurn(
                    message=AIMessage(content="", tool_calls=[call]),
                    record=ModelCallRecord(
                        agent="query",
                        raw_response="",
                        provider="scripted",
                        model="scripted",
                        tool_calls=(
                            ModelToolCall(
                                call_id="route-flight",
                                name="select_query_tool_families",
                                arguments={"families": ["flight_airspace"]},
                            ),
                        ),
                    ),
                )

        def factory(tools: list[Any]):  # type: ignore[no-untyped-def]
            names = {tool.name for tool in tools}
            available_tool_sets.append(names)
            if names == {"select_query_tool_families"}:
                return RouterModel()
            return FlightQueryModel()

        outcome = answer_question(
            runtime=QueryRuntime(
                store=store,
                source_index=None,
                event_index=None,
            ),
            question="Which recorded DAL flight 101 departed Atlanta?",
            scope=HybridQueryScope(limit=10),
            model_factory=factory,
        )

        assert outcome.status == "ok", outcome.failure_reason
        assert outcome.match_count == 1
        assert outcome.route_trace is not None
        assert outcome.route_trace.selected_families == ("flight_airspace",)
        assert outcome.tool_calls[0].tool == "find_flights"
        assert outcome.retrieved_flight_ids == [flight.flight_id]
        assert available_tool_sets[0] == {"select_query_tool_families"}
        assert "find_tmi_events" not in available_tool_sets[1]
        assert "find_flights" in available_tool_sets[1]
        assert "analyze_sector_traffic" in available_tool_sets[1]
    finally:
        store.close()
