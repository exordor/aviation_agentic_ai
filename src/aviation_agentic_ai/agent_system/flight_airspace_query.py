"""Deterministic structured queries over accepted Flight/Airspace knowledge."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import date, datetime
from itertools import combinations, product
from typing import Any, Literal

from pydantic import Field, field_validator

from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.utils.identifiers import stable_id


def _aware(value: datetime, label: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must be timezone-aware")
    return value


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


class FlightQuery(StrictModel):
    flight_id: str | None = Field(default=None, min_length=1)
    reporting_carrier: str | None = Field(default=None, min_length=1)
    flight_number: str | None = Field(default=None, min_length=1)
    origin_airport_id: str | None = Field(default=None, min_length=1)
    destination_airport_id: str | None = Field(default=None, min_length=1)
    temporal_domain_id: str | None = Field(default=None, min_length=1)
    service_date_start: date | None = None
    service_date_end: date | None = None
    cancelled: bool | None = None
    diverted: bool | None = None
    source_ids: tuple[str, ...] = ()
    source_families: tuple[str, ...] = ()
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class FlightView(StrictModel):
    flight_id: str
    publication_id: str
    temporal_domain_id: str
    source_family: str
    service_date: date
    reporting_carrier: str
    flight_number: str
    tail_number: str | None
    origin_airport_id: str
    destination_airport_id: str
    scheduled_departure_key: str
    scheduled_departure: datetime | None
    actual_wheels_off: datetime | None
    time_basis: str
    cancelled: bool
    diverted: bool
    source_ids: tuple[str, ...] = ()
    source_version_ids: tuple[str, ...] = ()


class FlightPage(StrictModel):
    total_matches: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    flights: tuple[FlightView, ...] = ()


class AirportQuery(StrictModel):
    airport_id: str | None = Field(default=None, min_length=1)
    airport_code: str | None = Field(default=None, min_length=1)
    artcc_code: str | None = Field(default=None, min_length=1)
    assignment_role: Literal["boundary", "responsible"] | None = None
    temporal_domain_id: str | None = Field(default=None, min_length=1)
    source_ids: tuple[str, ...] = ()
    source_families: tuple[str, ...] = ()
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class AirportView(StrictModel):
    airport_id: str
    publication_id: str
    temporal_domain_id: str
    source_family: str
    airport_code: str
    display_name: str | None
    artcc_ids: tuple[str, ...] = ()
    artcc_codes: tuple[str, ...] = ()
    assignment_ids: tuple[str, ...] = ()
    assignment_roles: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    source_version_ids: tuple[str, ...] = ()


class AirportPage(StrictModel):
    total_matches: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    airports: tuple[AirportView, ...] = ()


class RouteView(StrictModel):
    route_id: str
    flight_publication_id: str
    temporal_domain_id: str
    source_route_key: str
    route_kind: Literal["actual", "planned"]


class TrackPointView(StrictModel):
    track_point_id: str
    route_id: str
    temporal_domain_id: str
    sequence_number: int
    reporting_time: datetime
    latitude: float | None
    longitude: float | None
    ground_speed: float | None
    navigation_fix_id: str | None
    sector_ids: tuple[str, ...]
    source_version_id: str
    source_anchor_id: str


class FlightRouteView(StrictModel):
    flight_id: str
    publication_id: str
    routes: tuple[RouteView, ...]
    track_points: tuple[TrackPointView, ...]


class QueryDerivation(StrictModel):
    derivation_id: str
    operation: str
    method_version: str
    store_revision: int = Field(ge=0)
    normalized_parameters: dict[str, Any]
    input_publication_ids: tuple[str, ...]
    input_source_version_ids: tuple[str, ...]
    input_entity_ids: tuple[str, ...]
    result_checksum: str = Field(min_length=64, max_length=64)
    result_summary: str


class SectorTrafficRow(StrictModel):
    sector_id: str
    distinct_flight_count: int = Field(ge=0)
    passage_count: int = Field(ge=0)
    flight_ids: tuple[str, ...]
    passage_ids: tuple[str, ...]


class SectorPassageQuery(StrictModel):
    sector_id: str | None = Field(default=None, min_length=1)
    flight_id: str | None = Field(default=None, min_length=1)
    temporal_domain_id: str | None = Field(default=None, min_length=1)
    start: datetime | None = None
    end: datetime | None = None
    source_ids: tuple[str, ...] = ()
    source_families: tuple[str, ...] = ()
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)

    @field_validator("start", "end")
    @classmethod
    def _validate_times(cls, value: datetime | None) -> datetime | None:
        return _aware(value, "passage query time") if value is not None else None


class SectorPassageView(StrictModel):
    passage_id: str
    sector_id: str
    flight_id: str
    flight_publication_id: str
    route_id: str
    track_point_id: str
    passage_time: datetime
    temporal_domain_id: str
    derivation_id: str
    source_ids: tuple[str, ...] = ()
    source_version_ids: tuple[str, ...] = ()
    source_anchor_ids: tuple[str, ...] = ()


class SectorPassagePage(StrictModel):
    total_matches: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    passages: tuple[SectorPassageView, ...] = ()


class SectorTrafficAnalysis(StrictModel):
    rows: tuple[SectorTrafficRow, ...]
    derivation: QueryDerivation


class SectorPassagePair(StrictModel):
    sector_id: str
    first_flight_id: str
    first_passage_id: str
    first_reporting_time: datetime
    second_flight_id: str
    second_passage_id: str
    second_reporting_time: datetime
    seconds_apart: int = Field(ge=0)


class SectorPairAnalysis(StrictModel):
    rows: tuple[SectorPassagePair, ...]
    derivation: QueryDerivation


class FlightWeatherAssociationView(StrictModel):
    association_id: str
    flight_id: str
    flight_publication_id: str
    weather_observation_id: str
    weather_publication_id: str
    temporal_domain_id: str
    station_id: str
    observed_at: datetime
    phenomenon_tokens: tuple[str, ...]
    raw_report: str
    delta_seconds: int
    flight_time_field: str
    derivation_id: str
    causal_claim: Literal[False]
    source_ids: tuple[str, ...]
    source_version_ids: tuple[str, ...]
    source_anchor_ids: tuple[str, ...] = ()


class TMIApplicabilityQuery(StrictModel):
    applicability_id: str | None = Field(default=None, min_length=1)
    flight_id: str | None = Field(default=None, min_length=1)
    tmi_root_id: str | None = Field(default=None, min_length=1)
    tmi_family: str | None = Field(default=None, min_length=1)
    status: Literal[
        "applicability_candidate", "unknown", "not_applicable"
    ] | None = None
    temporal_domain_id: str | None = Field(default=None, min_length=1)
    source_ids: tuple[str, ...] = ()
    source_families: tuple[str, ...] = ()
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class TMIApplicabilityView(StrictModel):
    applicability_id: str
    flight_id: str
    flight_publication_id: str
    tmi_root_id: str
    tmi_publication_id: str
    temporal_domain_id: str
    tmi_family: str
    status: str
    rule_id: str
    rule_checksum: str
    normalized_inputs: dict[str, Any]
    limitation: str
    derivation_id: str
    actual_control_claim: Literal[False]
    source_ids: tuple[str, ...] = ()
    source_version_ids: tuple[str, ...] = ()


class TMIApplicabilityPage(StrictModel):
    total_matches: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    candidates: tuple[TMIApplicabilityView, ...] = ()


class FlightAirspaceQueryService:
    """Bounded SQL and exact arithmetic; no natural-language routing."""

    def __init__(self, store: AviationEvidenceStore) -> None:
        self.store = store
        self._connection = store._connection

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    def _publication_sources(
        self,
        publication_ids: tuple[str, ...],
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        if not publication_ids:
            return (), ()
        placeholders = ",".join("?" for _ in publication_ids)
        rows = self._connection.execute(
            f"""
            SELECT source.source_id, member.source_version_id
            FROM publication_sources AS member
            JOIN source_versions AS source
              ON source.source_version_id = member.source_version_id
            WHERE member.publication_id IN ({placeholders})
            ORDER BY source.source_id, member.source_version_id
            """,
            publication_ids,
        ).fetchall()
        return (
            tuple(sorted({row["source_id"] for row in rows})),
            tuple(sorted({row["source_version_id"] for row in rows})),
        )

    @staticmethod
    def _append_source_scope(
        predicates: list[str],
        parameters: list[object],
        *,
        publication_expression: str,
        source_ids: tuple[str, ...],
        source_families: tuple[str, ...],
    ) -> None:
        if not source_ids and not source_families:
            return
        clauses = [f"member.publication_id {publication_expression}"]
        if source_ids:
            placeholders = ",".join("?" for _ in source_ids)
            clauses.append(f"source.source_id IN ({placeholders})")
            parameters.extend(source_ids)
        if source_families:
            placeholders = ",".join("?" for _ in source_families)
            clauses.append(f"source.family IN ({placeholders})")
            parameters.extend(source_families)
        predicates.append(
            "EXISTS (SELECT 1 FROM publication_sources AS member "
            "JOIN source_versions AS source "
            "ON source.source_version_id = member.source_version_id "
            f"WHERE {' AND '.join(clauses)})"
        )

    def find_flights(self, query: FlightQuery) -> FlightPage:
        predicates: list[str] = []
        parameters: list[object] = []
        mappings = (
            ("root.root_id", query.flight_id),
            ("detail.reporting_carrier", query.reporting_carrier),
            ("detail.flight_number", query.flight_number),
            ("detail.origin_airport_id", query.origin_airport_id),
            ("detail.destination_airport_id", query.destination_airport_id),
            ("root.temporal_domain_id", query.temporal_domain_id),
        )
        for column, value in mappings:
            if value is not None:
                predicates.append(f"{column} = ?")
                parameters.append(value)
        if query.service_date_start is not None:
            predicates.append("detail.service_date >= ?")
            parameters.append(query.service_date_start.isoformat())
        if query.service_date_end is not None:
            predicates.append("detail.service_date < ?")
            parameters.append(query.service_date_end.isoformat())
        if query.cancelled is not None:
            predicates.append("detail.cancelled = ?")
            parameters.append(int(query.cancelled))
        if query.diverted is not None:
            predicates.append("detail.diverted = ?")
            parameters.append(int(query.diverted))
        self._append_source_scope(
            predicates,
            parameters,
            publication_expression="= root.active_publication_id",
            source_ids=query.source_ids,
            source_families=query.source_families,
        )
        where = " AND ".join(predicates) if predicates else "1 = 1"
        base = f"""
            FROM knowledge_roots AS root
            JOIN flights AS flight ON flight.flight_id = root.root_id
            JOIN flight_publications AS detail
              ON detail.publication_id = root.active_publication_id
            WHERE {where}
        """
        total = int(
            self._connection.execute(
                f"SELECT COUNT(*) {base}", parameters
            ).fetchone()[0]
        )
        rows = self._connection.execute(
            f"""
            SELECT root.root_id, root.active_publication_id,
                   root.temporal_domain_id, flight.source_family, detail.*
            {base}
            ORDER BY detail.service_date, detail.reporting_carrier,
                     detail.flight_number, root.root_id
            LIMIT ? OFFSET ?
            """,
            [*parameters, query.limit, query.offset],
        ).fetchall()
        flights = tuple(self._flight_view(row) for row in rows)
        return FlightPage(
            total_matches=total,
            offset=query.offset,
            limit=query.limit,
            flights=flights,
        )

    def _flight_view(self, row: Any) -> FlightView:
        publication_id = str(row["active_publication_id"])
        source_ids, source_version_ids = self._publication_sources(
            (publication_id,)
        )
        return FlightView(
            flight_id=row["root_id"],
            publication_id=publication_id,
            temporal_domain_id=row["temporal_domain_id"],
            source_family=row["source_family"],
            service_date=date.fromisoformat(row["service_date"]),
            reporting_carrier=row["reporting_carrier"],
            flight_number=row["flight_number"],
            tail_number=row["tail_number"],
            origin_airport_id=row["origin_airport_id"],
            destination_airport_id=row["destination_airport_id"],
            scheduled_departure_key=row["scheduled_departure_key"],
            scheduled_departure=self._parse_datetime(row["scheduled_departure_time"]),
            actual_wheels_off=self._parse_datetime(row["actual_wheels_off_time"]),
            time_basis=row["time_basis"],
            cancelled=bool(row["cancelled"]),
            diverted=bool(row["diverted"]),
            source_ids=source_ids,
            source_version_ids=source_version_ids,
        )

    def get_flight(self, flight_id: str) -> FlightView | None:
        page = self.find_flights(FlightQuery(flight_id=flight_id, limit=1))
        return page.flights[0] if page.flights else None

    def find_airports(self, query: AirportQuery) -> AirportPage:
        predicates: list[str] = []
        parameters: list[object] = []
        for column, value in (
            ("root.root_id", query.airport_id),
            ("airport.identifier", query.airport_code),
            ("artcc.identifier", query.artcc_code),
            ("assignment.assignment_role", query.assignment_role),
            ("root.temporal_domain_id", query.temporal_domain_id),
        ):
            if value is not None:
                predicates.append(f"{column} = ?")
                parameters.append(value)
        self._append_source_scope(
            predicates,
            parameters,
            publication_expression="= root.active_publication_id",
            source_ids=query.source_ids,
            source_families=query.source_families,
        )
        where = " AND ".join(predicates) if predicates else "1 = 1"
        base = f"""
            FROM knowledge_roots AS root
            JOIN airports AS airport ON airport.airport_id = root.root_id
            LEFT JOIN airport_artcc_assignments AS assignment
              ON assignment.airport_publication_id = root.active_publication_id
            LEFT JOIN knowledge_publications AS artcc_publication
              ON artcc_publication.publication_id = assignment.artcc_publication_id
            LEFT JOIN artccs AS artcc
              ON artcc.artcc_id = artcc_publication.root_id
            WHERE {where}
        """
        total = int(
            self._connection.execute(
                f"SELECT COUNT(DISTINCT root.root_id) {base}", parameters
            ).fetchone()[0]
        )
        root_rows = self._connection.execute(
            f"""
            SELECT root.root_id
            {base}
            GROUP BY root.root_id
            ORDER BY airport.identifier, root.root_id
            LIMIT ? OFFSET ?
            """,
            [*parameters, query.limit, query.offset],
        ).fetchall()
        airports: list[AirportView] = []
        for root_row in root_rows:
            rows = self._connection.execute(
                """
                SELECT root.root_id, root.active_publication_id,
                       root.temporal_domain_id, airport.source_family,
                       airport.identifier, airport.display_name,
                       assignment.assignment_id, assignment.assignment_role,
                       assignment.artcc_publication_id,
                       artcc_publication.root_id AS artcc_id,
                       artcc.identifier AS artcc_code
                FROM knowledge_roots AS root
                JOIN airports AS airport ON airport.airport_id = root.root_id
                LEFT JOIN airport_artcc_assignments AS assignment
                  ON assignment.airport_publication_id = root.active_publication_id
                LEFT JOIN knowledge_publications AS artcc_publication
                  ON artcc_publication.publication_id = assignment.artcc_publication_id
                LEFT JOIN artccs AS artcc
                  ON artcc.artcc_id = artcc_publication.root_id
                WHERE root.root_id = ?
                ORDER BY assignment.assignment_role, artcc.identifier
                """,
                (root_row["root_id"],),
            ).fetchall()
            row = rows[0]
            publication_ids = tuple(
                sorted(
                    {
                        row["active_publication_id"],
                        *(
                            item["artcc_publication_id"]
                            for item in rows
                            if item["artcc_publication_id"]
                        ),
                    }
                )
            )
            source_ids, source_version_ids = self._publication_sources(
                publication_ids
            )
            airports.append(
                AirportView(
                    airport_id=row["root_id"],
                    publication_id=row["active_publication_id"],
                    temporal_domain_id=row["temporal_domain_id"],
                    source_family=row["source_family"],
                    airport_code=row["identifier"],
                    display_name=row["display_name"],
                    artcc_ids=tuple(
                        sorted(
                            {
                                item["artcc_id"]
                                for item in rows
                                if item["artcc_id"]
                            }
                        )
                    ),
                    artcc_codes=tuple(
                        sorted(
                            {
                                item["artcc_code"]
                                for item in rows
                                if item["artcc_code"]
                            }
                        )
                    ),
                    assignment_ids=tuple(
                        sorted(
                            {
                                item["assignment_id"]
                                for item in rows
                                if item["assignment_id"]
                            }
                        )
                    ),
                    assignment_roles=tuple(
                        sorted(
                            {
                                item["assignment_role"]
                                for item in rows
                                if item["assignment_role"]
                            }
                        )
                    ),
                    source_ids=source_ids,
                    source_version_ids=source_version_ids,
                )
            )
        return AirportPage(
            total_matches=total,
            offset=query.offset,
            limit=query.limit,
            airports=tuple(airports),
        )

    def get_flight_route(self, flight_id: str) -> FlightRouteView:
        flight = self.get_flight(flight_id)
        if flight is None:
            raise KeyError(f"flight does not exist: {flight_id}")
        route_rows = self._connection.execute(
            """
            SELECT * FROM routes
            WHERE flight_publication_id = ?
            ORDER BY route_kind, route_id
            """,
            (flight.publication_id,),
        ).fetchall()
        routes = tuple(
            RouteView(
                route_id=row["route_id"],
                flight_publication_id=row["flight_publication_id"],
                temporal_domain_id=row["temporal_domain_id"],
                source_route_key=row["source_route_key"],
                route_kind=row["route_kind"],
            )
            for row in route_rows
        )
        points: list[TrackPointView] = []
        for route in routes:
            point_rows = self._connection.execute(
                """
                SELECT * FROM track_points
                WHERE route_id = ?
                ORDER BY sequence_number, track_point_id
                """,
                (route.route_id,),
            ).fetchall()
            for row in point_rows:
                sectors = tuple(
                    item["sector_id"]
                    for item in self._connection.execute(
                        """
                        SELECT sector_id FROM track_point_sectors
                        WHERE track_point_id = ? ORDER BY sector_id
                        """,
                        (row["track_point_id"],),
                    ).fetchall()
                )
                points.append(
                    TrackPointView(
                        track_point_id=row["track_point_id"],
                        route_id=row["route_id"],
                        temporal_domain_id=row["temporal_domain_id"],
                        sequence_number=row["sequence_number"],
                        reporting_time=datetime.fromisoformat(row["reporting_time"]),
                        latitude=row["latitude"],
                        longitude=row["longitude"],
                        ground_speed=row["ground_speed"],
                        navigation_fix_id=row["fix_id"],
                        sector_ids=sectors,
                        source_version_id=row["source_version_id"],
                        source_anchor_id=row["source_anchor_id"],
                    )
                )
        return FlightRouteView(
            flight_id=flight.flight_id,
            publication_id=flight.publication_id,
            routes=routes,
            track_points=tuple(points),
        )

    def find_sector_passages(
        self,
        query: SectorPassageQuery,
    ) -> SectorPassagePage:
        if query.start is not None and query.end is not None and query.end <= query.start:
            raise ValueError("end must be after start")
        predicates: list[str] = []
        parameters: list[object] = []
        for column, value in (
            ("passage.sector_id", query.sector_id),
            ("flight.flight_id", query.flight_id),
            ("passage.temporal_domain_id", query.temporal_domain_id),
        ):
            if value is not None:
                predicates.append(f"{column} = ?")
                parameters.append(value)
        if query.start is not None:
            predicates.append(
                "julianday(passage.passage_time) >= julianday(?)"
            )
            parameters.append(query.start.isoformat())
        if query.end is not None:
            predicates.append(
                "julianday(passage.passage_time) < julianday(?)"
            )
            parameters.append(query.end.isoformat())
        if query.source_ids:
            placeholders = ",".join("?" for _ in query.source_ids)
            predicates.append(f"source.source_id IN ({placeholders})")
            parameters.extend(query.source_ids)
        if query.source_families:
            placeholders = ",".join("?" for _ in query.source_families)
            predicates.append(f"source.family IN ({placeholders})")
            parameters.extend(query.source_families)
        where = " AND ".join(predicates) if predicates else "1 = 1"
        base = f"""
            FROM sector_passages AS passage
            JOIN flight_publications AS detail
              ON detail.publication_id = passage.flight_publication_id
            JOIN flights AS flight ON flight.flight_id = detail.flight_id
            JOIN track_points AS point
              ON point.track_point_id = passage.track_point_id
            JOIN source_versions AS source
              ON source.source_version_id = point.source_version_id
            WHERE {where}
        """
        total = int(
            self._connection.execute(
                f"SELECT COUNT(*) {base}", parameters
            ).fetchone()[0]
        )
        rows = self._connection.execute(
            f"""
            SELECT passage.*, flight.flight_id, point.source_version_id,
                   point.source_anchor_id, source.source_id
            {base}
            ORDER BY julianday(passage.passage_time), passage.sector_id,
                     flight.flight_id, passage.sector_passage_id
            LIMIT ? OFFSET ?
            """,
            [*parameters, query.limit, query.offset],
        ).fetchall()
        return SectorPassagePage(
            total_matches=total,
            offset=query.offset,
            limit=query.limit,
            passages=tuple(
                SectorPassageView(
                    passage_id=row["sector_passage_id"],
                    sector_id=row["sector_id"],
                    flight_id=row["flight_id"],
                    flight_publication_id=row["flight_publication_id"],
                    route_id=row["route_id"],
                    track_point_id=row["track_point_id"],
                    passage_time=datetime.fromisoformat(row["passage_time"]),
                    temporal_domain_id=row["temporal_domain_id"],
                    derivation_id=row["derivation_id"],
                    source_ids=(row["source_id"],),
                    source_version_ids=(row["source_version_id"],),
                    source_anchor_ids=(row["source_anchor_id"],),
                )
                for row in rows
            ),
        )

    def rank_sector_traffic(
        self,
        *,
        start: datetime,
        end: datetime,
        limit: int = 20,
        source_ids: tuple[str, ...] = (),
        source_families: tuple[str, ...] = (),
    ) -> SectorTrafficAnalysis:
        _aware(start, "start")
        _aware(end, "end")
        if end <= start:
            raise ValueError("end must be after start")
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        predicates = [
            "julianday(passage.passage_time) >= julianday(?)",
            "julianday(passage.passage_time) < julianday(?)",
        ]
        parameters: list[object] = [start.isoformat(), end.isoformat()]
        if source_ids:
            placeholders = ",".join("?" for _ in source_ids)
            predicates.append(f"source.source_id IN ({placeholders})")
            parameters.extend(source_ids)
        if source_families:
            placeholders = ",".join("?" for _ in source_families)
            predicates.append(f"source.family IN ({placeholders})")
            parameters.extend(source_families)
        rows = self._connection.execute(
            f"""
            SELECT passage.sector_id, flight.flight_id,
                   passage.flight_publication_id,
                   passage.sector_passage_id
            FROM sector_passages AS passage
            JOIN flight_publications AS detail
              ON detail.publication_id = passage.flight_publication_id
            JOIN flights AS flight ON flight.flight_id = detail.flight_id
            JOIN track_points AS point
              ON point.track_point_id = passage.track_point_id
            JOIN source_versions AS source
              ON source.source_version_id = point.source_version_id
            WHERE {" AND ".join(predicates)}
            ORDER BY passage.sector_id, flight.flight_id,
                     passage.sector_passage_id
            """,
            parameters,
        ).fetchall()
        grouped: dict[str, list[Any]] = defaultdict(list)
        for row in rows:
            grouped[row["sector_id"]].append(row)
        ranked = sorted(
            (
                SectorTrafficRow(
                    sector_id=sector_id,
                    distinct_flight_count=len(
                        {row["flight_id"] for row in sector_rows}
                    ),
                    passage_count=len(sector_rows),
                    flight_ids=tuple(
                        sorted({row["flight_id"] for row in sector_rows})
                    ),
                    passage_ids=tuple(
                        sorted(row["sector_passage_id"] for row in sector_rows)
                    ),
                )
                for sector_id, sector_rows in grouped.items()
            ),
            key=lambda row: (
                -row.distinct_flight_count,
                -row.passage_count,
                row.sector_id,
            ),
        )[:limit]
        parameters = {
            "interval": {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "boundary": "half_open",
            },
            "limit": limit,
            "source_ids": list(source_ids),
            "source_families": list(source_families),
        }
        publication_ids = tuple(
            sorted({row["flight_publication_id"] for row in rows})
        )
        _, source_version_ids = self._publication_sources(publication_ids)
        return SectorTrafficAnalysis(
            rows=tuple(ranked),
            derivation=self._query_derivation(
                operation="rank_sector_traffic",
                method_version="sector-traffic-v1",
                parameters=parameters,
                publication_ids=publication_ids,
                source_version_ids=source_version_ids,
                entity_ids=tuple(
                    sorted(
                        {
                            *[row["flight_id"] for row in rows],
                            *[row["sector_id"] for row in rows],
                            *[row["sector_passage_id"] for row in rows],
                        }
                    )
                ),
                result=[row.model_dump(mode="json") for row in ranked],
            ),
        )

    def find_close_sector_passage_pairs(
        self,
        *,
        sector_id: str,
        start: datetime,
        end: datetime,
        max_seconds: int,
        source_ids: tuple[str, ...] = (),
        source_families: tuple[str, ...] = (),
    ) -> SectorPairAnalysis:
        _aware(start, "start")
        _aware(end, "end")
        if end <= start:
            raise ValueError("end must be after start")
        if max_seconds <= 0:
            raise ValueError("max_seconds must be positive")
        predicates = [
            "passage.sector_id = ?",
            "julianday(passage.passage_time) >= julianday(?)",
            "julianday(passage.passage_time) < julianday(?)",
        ]
        parameters: list[object] = [
            sector_id,
            start.isoformat(),
            end.isoformat(),
        ]
        if source_ids:
            placeholders = ",".join("?" for _ in source_ids)
            predicates.append(f"source.source_id IN ({placeholders})")
            parameters.extend(source_ids)
        if source_families:
            placeholders = ",".join("?" for _ in source_families)
            predicates.append(f"source.family IN ({placeholders})")
            parameters.extend(source_families)
        rows = self._connection.execute(
            f"""
            SELECT passage.sector_passage_id, passage.flight_publication_id,
                   passage.passage_time, flight.flight_id
            FROM sector_passages AS passage
            JOIN flight_publications AS detail
              ON detail.publication_id = passage.flight_publication_id
            JOIN flights AS flight ON flight.flight_id = detail.flight_id
            JOIN track_points AS point
              ON point.track_point_id = passage.track_point_id
            JOIN source_versions AS source
              ON source.source_version_id = point.source_version_id
            WHERE {" AND ".join(predicates)}
            ORDER BY flight.flight_id, julianday(passage.passage_time),
                     passage.sector_passage_id
            """,
            parameters,
        ).fetchall()
        by_flight: dict[str, list[Any]] = defaultdict(list)
        for row in rows:
            by_flight[row["flight_id"]].append(row)
        pairs: list[SectorPassagePair] = []
        for first_id, second_id in combinations(sorted(by_flight), 2):
            first, second = min(
                product(by_flight[first_id], by_flight[second_id]),
                key=lambda pair: (
                    abs(
                        (
                            datetime.fromisoformat(pair[1]["passage_time"])
                            - datetime.fromisoformat(pair[0]["passage_time"])
                        ).total_seconds()
                    ),
                    pair[0]["passage_time"],
                    pair[1]["passage_time"],
                ),
            )
            first_time = datetime.fromisoformat(first["passage_time"])
            second_time = datetime.fromisoformat(second["passage_time"])
            seconds = int(abs((second_time - first_time).total_seconds()))
            if seconds >= max_seconds:
                continue
            pairs.append(
                SectorPassagePair(
                    sector_id=sector_id,
                    first_flight_id=first_id,
                    first_passage_id=first["sector_passage_id"],
                    first_reporting_time=first_time,
                    second_flight_id=second_id,
                    second_passage_id=second["sector_passage_id"],
                    second_reporting_time=second_time,
                    seconds_apart=seconds,
                )
            )
        parameters = {
            "sector_id": sector_id,
            "interval": {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "boundary": "half_open",
            },
            "max_seconds": max_seconds,
            "comparison": "strict_less_than",
            "source_ids": list(source_ids),
            "source_families": list(source_families),
        }
        publication_ids = tuple(
            sorted({row["flight_publication_id"] for row in rows})
        )
        _, source_version_ids = self._publication_sources(publication_ids)
        return SectorPairAnalysis(
            rows=tuple(pairs),
            derivation=self._query_derivation(
                operation="find_close_sector_passage_pairs",
                method_version="sector-pair-v1",
                parameters=parameters,
                publication_ids=publication_ids,
                source_version_ids=source_version_ids,
                entity_ids=tuple(
                    sorted(
                        {
                            sector_id,
                            *[row["flight_id"] for row in rows],
                            *[row["sector_passage_id"] for row in rows],
                        }
                    )
                ),
                result=[row.model_dump(mode="json") for row in pairs],
            ),
        )

    def find_flight_weather_associations(
        self,
        *,
        flight_id: str,
        match_mode: Literal["nearest", "all"] = "nearest",
    ) -> tuple[FlightWeatherAssociationView, ...]:
        rows = self._connection.execute(
            """
            SELECT association.*, flight.flight_id,
                   observation.weather_observation_id,
                   observation.station_id, observation.observed_at,
                   observation.phenomenon_tokens_json,
                   observation.raw_report, observation.source_version_id,
                   source.source_id
            FROM knowledge_roots AS root
            JOIN flight_publications AS detail
              ON detail.publication_id = root.active_publication_id
            JOIN flights AS flight ON flight.flight_id = detail.flight_id
            JOIN flight_weather_associations AS association
              ON association.flight_publication_id = detail.publication_id
            JOIN weather_observations AS observation
              ON observation.publication_id = association.weather_publication_id
            JOIN source_versions AS source
              ON source.source_version_id = observation.source_version_id
            WHERE root.root_id = ?
            ORDER BY association.delta_seconds, observation.observed_at,
                     association.association_id
            """,
            (flight_id,),
        ).fetchall()
        if match_mode == "nearest":
            rows = rows[:1]
        associations: list[FlightWeatherAssociationView] = []
        for row in rows:
            publication_ids = (
                row["flight_publication_id"],
                row["weather_publication_id"],
            )
            source_ids, source_version_ids = self._publication_sources(
                publication_ids
            )
            anchor_rows = self._connection.execute(
                """
                SELECT DISTINCT source_anchor_id
                FROM publication_evidence_links
                WHERE publication_id IN (?, ?)
                  AND owner_kind = 'structured_record'
                  AND owner_id = ?
                  AND source_anchor_id IS NOT NULL
                ORDER BY source_anchor_id
                """,
                (*publication_ids, row["association_id"]),
            ).fetchall()
            associations.append(
                FlightWeatherAssociationView(
                association_id=row["association_id"],
                flight_id=row["flight_id"],
                flight_publication_id=row["flight_publication_id"],
                weather_observation_id=row["weather_observation_id"],
                weather_publication_id=row["weather_publication_id"],
                temporal_domain_id=row["temporal_domain_id"],
                station_id=row["station_id"],
                observed_at=datetime.fromisoformat(row["observed_at"]),
                phenomenon_tokens=tuple(
                    json.loads(row["phenomenon_tokens_json"])
                ),
                raw_report=row["raw_report"],
                delta_seconds=row["delta_seconds"],
                flight_time_field=row["flight_time_field"],
                derivation_id=row["derivation_id"],
                causal_claim=False,
                source_ids=source_ids,
                source_version_ids=source_version_ids,
                source_anchor_ids=tuple(
                    item["source_anchor_id"] for item in anchor_rows
                ),
            )
            )
        return tuple(associations)

    def find_tmi_applicability_candidates(
        self,
        query: TMIApplicabilityQuery,
    ) -> TMIApplicabilityPage:
        predicates: list[str] = []
        parameters: list[object] = []
        for column, value in (
            ("candidate.applicability_id", query.applicability_id),
            ("flight.flight_id", query.flight_id),
            ("tmi.root_id", query.tmi_root_id),
            ("candidate.tmi_family", query.tmi_family),
            ("candidate.status", query.status),
            ("candidate.temporal_domain_id", query.temporal_domain_id),
        ):
            if value is not None:
                predicates.append(f"{column} = ?")
                parameters.append(value)
        self._append_source_scope(
            predicates,
            parameters,
            publication_expression=(
                "IN (candidate.flight_publication_id, "
                "candidate.tmi_publication_id)"
            ),
            source_ids=query.source_ids,
            source_families=query.source_families,
        )
        where = " AND ".join(predicates) if predicates else "1 = 1"
        base = f"""
            FROM flight_tmi_applicability AS candidate
            JOIN flight_publications AS flight_detail
              ON flight_detail.publication_id = candidate.flight_publication_id
            JOIN flights AS flight ON flight.flight_id = flight_detail.flight_id
            JOIN knowledge_publications AS tmi
              ON tmi.publication_id = candidate.tmi_publication_id
            WHERE {where}
        """
        total = int(
            self._connection.execute(
                f"SELECT COUNT(*) {base}", parameters
            ).fetchone()[0]
        )
        rows = self._connection.execute(
            f"""
            SELECT candidate.*, flight.flight_id, tmi.root_id AS tmi_root_id
            {base}
            ORDER BY candidate.applicability_id
            LIMIT ? OFFSET ?
            """,
            [*parameters, query.limit, query.offset],
        ).fetchall()
        candidates: list[TMIApplicabilityView] = []
        for row in rows:
            source_ids, source_version_ids = self._publication_sources(
                (
                    row["flight_publication_id"],
                    row["tmi_publication_id"],
                )
            )
            candidates.append(
                TMIApplicabilityView(
                    applicability_id=row["applicability_id"],
                    flight_id=row["flight_id"],
                    flight_publication_id=row["flight_publication_id"],
                    tmi_root_id=row["tmi_root_id"],
                    tmi_publication_id=row["tmi_publication_id"],
                    temporal_domain_id=row["temporal_domain_id"],
                    tmi_family=row["tmi_family"],
                    status=row["status"],
                    rule_id=row["rule_id"],
                    rule_checksum=row["rule_checksum"],
                    normalized_inputs=json.loads(row["normalized_inputs_json"]),
                    limitation=row["limitation"],
                    derivation_id=row["derivation_id"],
                    actual_control_claim=False,
                    source_ids=source_ids,
                    source_version_ids=source_version_ids,
                )
            )
        return TMIApplicabilityPage(
            total_matches=total,
            offset=query.offset,
            limit=query.limit,
            candidates=tuple(candidates),
        )

    def _query_derivation(
        self,
        *,
        operation: str,
        method_version: str,
        parameters: dict[str, Any],
        publication_ids: tuple[str, ...],
        source_version_ids: tuple[str, ...],
        entity_ids: tuple[str, ...],
        result: object,
    ) -> QueryDerivation:
        revision = self.store.get_knowledge_revision()
        checksum = hashlib.sha256(_canonical(result).encode()).hexdigest()
        derivation_id = stable_id(
            "query-derivation",
            self.store.dataset_id,
            revision,
            operation,
            method_version,
            _canonical(parameters),
            _canonical(publication_ids),
            _canonical(source_version_ids),
            _canonical(entity_ids),
            checksum,
        )
        return QueryDerivation(
            derivation_id=derivation_id,
            operation=operation,
            method_version=method_version,
            store_revision=revision,
            normalized_parameters=parameters,
            input_publication_ids=publication_ids,
            input_source_version_ids=source_version_ids,
            input_entity_ids=entity_ids,
            result_checksum=checksum,
            result_summary=f"{len(result) if isinstance(result, list) else 1} result rows",
        )


__all__ = [
    "AirportPage",
    "AirportQuery",
    "AirportView",
    "FlightAirspaceQueryService",
    "FlightPage",
    "FlightQuery",
    "FlightRouteView",
    "FlightView",
    "FlightWeatherAssociationView",
    "QueryDerivation",
    "SectorPairAnalysis",
    "SectorPassagePage",
    "SectorPassagePair",
    "SectorPassageQuery",
    "SectorPassageView",
    "SectorTrafficAnalysis",
    "SectorTrafficRow",
    "TMIApplicabilityPage",
    "TMIApplicabilityQuery",
    "TMIApplicabilityView",
]
