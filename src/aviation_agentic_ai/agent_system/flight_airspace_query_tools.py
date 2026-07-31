"""Generic read-only Flight/Airspace tools for the existing Query Agent."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Literal

from langchain_core.tools import BaseTool, tool
from pydantic import Field, model_validator

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryEvidence,
    HybridQueryScope,
    HybridQuerySupportRecord,
    HybridQueryToolObservation,
    QueryGraphEdge,
    QueryGraphPath,
    StrictModel,
)
from aviation_agentic_ai.agent_system.flight_airspace_query import (
    AirportQuery,
    FlightAirspaceQueryService,
    FlightQuery,
    SectorPassageQuery,
    TMIApplicabilityQuery,
)
from aviation_agentic_ai.agent_system.query_runtime import QueryRuntime
from aviation_agentic_ai.utils.identifiers import stable_id


def _json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=lambda item: item.isoformat()
        if isinstance(item, datetime)
        else str(item),
    )


def _unique(values: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


class FindFlightsInput(StrictModel):
    flight_id: str | None = Field(default=None, min_length=1)
    reporting_carrier: str | None = Field(default=None, min_length=1)
    flight_number: str | None = Field(default=None, min_length=1)
    origin_airport_id: str | None = Field(default=None, min_length=1)
    destination_airport_id: str | None = Field(default=None, min_length=1)
    temporal_domain_id: str | None = Field(default=None, min_length=1)
    cancelled: bool | None = None
    diverted: bool | None = None
    offset: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=1, le=100)


class FlightInput(StrictModel):
    flight_id: str = Field(min_length=1)


class FindAirportsInput(StrictModel):
    airport_id: str | None = Field(default=None, min_length=1)
    airport_code: str | None = Field(default=None, min_length=1)
    artcc_code: str | None = Field(default=None, min_length=1)
    assignment_role: Literal["boundary", "responsible"] | None = None
    temporal_domain_id: str | None = Field(default=None, min_length=1)
    offset: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=1, le=100)


class FindSectorPassagesInput(StrictModel):
    sector_id: str | None = Field(default=None, min_length=1)
    flight_id: str | None = Field(default=None, min_length=1)
    temporal_domain_id: str | None = Field(default=None, min_length=1)
    start: datetime | None = None
    end: datetime | None = None
    offset: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=1, le=100)


class AnalyzeSectorTrafficInput(StrictModel):
    analysis: Literal["ranking", "close_pairs"] = "ranking"
    start: datetime
    end: datetime
    sector_id: str | None = Field(default=None, min_length=1)
    max_seconds: int | None = Field(default=None, gt=0)
    limit: int = Field(default=20, ge=1, le=100)

    @model_validator(mode="after")
    def _validate_mode(self) -> AnalyzeSectorTrafficInput:
        if self.analysis == "close_pairs" and (
            self.sector_id is None or self.max_seconds is None
        ):
            raise ValueError(
                "close_pairs requires sector_id and max_seconds"
            )
        return self


class FlightWeatherInput(FlightInput):
    match_mode: Literal["nearest", "all"] = "nearest"


class FindTMIApplicabilityInput(StrictModel):
    applicability_id: str | None = Field(default=None, min_length=1)
    flight_id: str | None = Field(default=None, min_length=1)
    tmi_root_id: str | None = Field(default=None, min_length=1)
    tmi_family: str | None = Field(default=None, min_length=1)
    status: Literal[
        "applicability_candidate", "unknown", "not_applicable"
    ] | None = None
    temporal_domain_id: str | None = Field(default=None, min_length=1)
    offset: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=1, le=100)


class AviationGraphInput(StrictModel):
    root_id: str = Field(min_length=1)
    direction: Literal["out", "in"] = "out"
    predicate_iris: tuple[str, ...] = ()
    limit: int = Field(default=50, ge=1, le=100)


class FlightAirspaceQueryGateway:
    """Apply one immutable user scope around deterministic domain queries."""

    def __init__(self, *, runtime: QueryRuntime, scope: HybridQueryScope) -> None:
        self.runtime = runtime
        self.store = runtime.store
        self.scope = scope
        self.service = FlightAirspaceQueryService(self.store)

    def _limit(self, value: int | None) -> int:
        if value is None:
            return self.scope.limit
        if value > self.scope.limit:
            raise ValueError("limit broadens the query scope")
        return value

    def _offset(self, value: int | None) -> int:
        if value is None:
            return self.scope.offset
        if value < self.scope.offset:
            raise ValueError("offset broadens the query scope")
        return value

    def _flight_id(self, value: str | None) -> str | None:
        fixed = self.scope.flight_id
        if fixed is not None and value not in {None, fixed}:
            raise ValueError("flight_id is outside the query scope")
        return fixed or value

    def _root_id(self, value: str) -> str:
        fixed = self.scope.root_id or self.scope.flight_id
        if fixed is not None and value != fixed:
            raise ValueError("root_id is outside the query scope")
        return value

    def _tmi_root_id(self, value: str | None) -> str | None:
        fixed = self.scope.event_id
        if fixed is not None and value not in {None, fixed}:
            raise ValueError("TMI root is outside the event query scope")
        return fixed or value

    def _temporal_domain(self, value: str | None) -> str | None:
        fixed = self.scope.temporal_domain_id
        if fixed is not None and value not in {None, fixed}:
            raise ValueError("temporal_domain_id is outside the query scope")
        return fixed or value

    def _interval(
        self,
        start: datetime | None,
        end: datetime | None,
    ) -> tuple[datetime | None, datetime | None]:
        if self.scope.start is not None and start is not None and start < self.scope.start:
            raise ValueError("start broadens the query scope")
        if self.scope.end is not None and end is not None and end > self.scope.end:
            raise ValueError("end broadens the query scope")
        effective_start = start if start is not None else self.scope.start
        effective_end = end if end is not None else self.scope.end
        return effective_start, effective_end

    def _source_ids_for_versions(
        self,
        version_ids: tuple[str, ...],
    ) -> tuple[str, ...]:
        values: list[str] = []
        for version_id in version_ids:
            version = self.store.get_source_version(version_id)
            if version is not None:
                values.append(version.source_id)
        return _unique(values)

    def _evidence_allowed(
        self,
        source_ids: tuple[str, ...],
        source_version_ids: tuple[str, ...],
    ) -> bool:
        if self.scope.source_ids and not set(source_ids).intersection(
            self.scope.source_ids
        ):
            return False
        if not self.scope.source_families:
            return True
        allowed = set(self.scope.source_families)
        return any(
            (version := self.store.get_source_version(version_id)) is not None
            and version.family in allowed
            for version_id in source_version_ids
        )

    def _observation(
        self,
        *,
        payload: object,
        support: list[HybridQuerySupportRecord],
        graph_paths: tuple[QueryGraphPath, ...] = (),
        limitation: str = "",
    ) -> HybridQueryToolObservation:
        def values(field: str) -> tuple[str, ...]:
            return _unique(
                [
                    value
                    for record in support
                    for value in getattr(record, field)
                ]
            )

        evidence = HybridQueryEvidence(
            event_ids=values("event_ids"),
            root_ids=values("root_ids"),
            publication_ids=values("publication_ids"),
            flight_ids=values("flight_ids"),
            aircraft_ids=values("aircraft_ids"),
            airport_artcc_assignment_ids=values(
                "airport_artcc_assignment_ids"
            ),
            snapshot_match_ids=values("snapshot_match_ids"),
            route_ids=values("route_ids"),
            track_point_ids=values("track_point_ids"),
            sector_passage_ids=values("sector_passage_ids"),
            derivation_ids=values("derivation_ids"),
            temporal_association_ids=values("temporal_association_ids"),
            tmi_applicability_ids=values("tmi_applicability_ids"),
            fact_ids=values("fact_ids"),
            graph_path_ids=values("graph_path_ids"),
            source_ids=values("source_ids"),
            source_version_ids=values("source_version_ids"),
            source_anchor_ids=values("source_anchor_ids"),
        )
        return HybridQueryToolObservation(
            status="ok" if support else "insufficient",
            content=_json(payload),
            details=evidence,
            support_records=tuple(support),
            graph_paths=graph_paths,
            limitation=limitation if not support else "",
        )

    def find_flights(self, **kwargs: object) -> HybridQueryToolObservation:
        query = FindFlightsInput.model_validate(kwargs)
        page = self.service.find_flights(
            FlightQuery(
                flight_id=self._flight_id(query.flight_id),
                reporting_carrier=query.reporting_carrier,
                flight_number=query.flight_number,
                origin_airport_id=query.origin_airport_id,
                destination_airport_id=query.destination_airport_id,
                temporal_domain_id=self._temporal_domain(
                    query.temporal_domain_id
                ),
                cancelled=query.cancelled,
                diverted=query.diverted,
                source_ids=self.scope.source_ids,
                source_families=tuple(
                    family.value for family in self.scope.source_families
                ),
                offset=self._offset(query.offset),
                limit=self._limit(query.limit),
            )
        )
        rows = tuple(
            row
            for row in page.flights
            if self._evidence_allowed(row.source_ids, row.source_version_ids)
        )
        support = [
            HybridQuerySupportRecord(
                kind="flight_fact",
                root_ids=(row.flight_id,),
                publication_ids=(row.publication_id,),
                flight_ids=(row.flight_id,),
                source_ids=row.source_ids,
                source_version_ids=row.source_version_ids,
            )
            for row in rows
        ]
        return self._observation(
            payload={
                "total_matches": page.total_matches,
                "returned": len(rows),
                "flights": [row.model_dump(mode="json") for row in rows],
            },
            support=support,
            limitation="No accepted Flight matched the bounded filters.",
        )

    def read_flight(self, flight_id: str) -> HybridQueryToolObservation:
        return self.find_flights(flight_id=flight_id, limit=1)

    def find_airports(self, **kwargs: object) -> HybridQueryToolObservation:
        query = FindAirportsInput.model_validate(kwargs)
        page = self.service.find_airports(
            AirportQuery(
                airport_id=query.airport_id,
                airport_code=query.airport_code,
                artcc_code=query.artcc_code,
                assignment_role=query.assignment_role,
                temporal_domain_id=self._temporal_domain(
                    query.temporal_domain_id
                ),
                source_ids=self.scope.source_ids,
                source_families=tuple(
                    family.value for family in self.scope.source_families
                ),
                offset=self._offset(query.offset),
                limit=self._limit(query.limit),
            )
        )
        rows = tuple(
            row
            for row in page.airports
            if self._evidence_allowed(row.source_ids, row.source_version_ids)
        )
        support = [
            HybridQuerySupportRecord(
                kind=(
                    "reference_association"
                    if row.assignment_ids
                    else "source_fact"
                ),
                root_ids=(row.airport_id,),
                publication_ids=(row.publication_id,),
                airport_artcc_assignment_ids=row.assignment_ids,
                source_ids=row.source_ids,
                source_version_ids=row.source_version_ids,
            )
            for row in rows
        ]
        return self._observation(
            payload={
                "total_matches": len(rows),
                "offset": page.offset,
                "limit": page.limit,
                "airports": [row.model_dump(mode="json") for row in rows],
            },
            support=support,
            limitation="No accepted Airport matched the bounded filters.",
        )

    def read_flight_trajectory(
        self,
        flight_id: str,
    ) -> HybridQueryToolObservation:
        flight_id = self._flight_id(flight_id) or flight_id
        route = self.service.get_flight_route(flight_id)
        flight = self.service.get_flight(flight_id)
        if flight is None or not self._evidence_allowed(
            flight.source_ids,
            flight.source_version_ids,
        ):
            raise ValueError("flight_id is outside the source query scope")
        versions = _unique(
            [point.source_version_id for point in route.track_points]
        )
        anchors = _unique([point.source_anchor_id for point in route.track_points])
        sources = self._source_ids_for_versions(versions)
        support = []
        if route.routes and route.track_points:
            support.append(
                HybridQuerySupportRecord(
                    kind="trajectory_fact",
                    root_ids=(route.flight_id,),
                    publication_ids=(route.publication_id,),
                    flight_ids=(route.flight_id,),
                    route_ids=tuple(item.route_id for item in route.routes),
                    track_point_ids=tuple(
                        item.track_point_id for item in route.track_points
                    ),
                    source_ids=sources,
                    source_version_ids=versions,
                    source_anchor_ids=anchors,
                )
            )
        return self._observation(
            payload=route.model_dump(mode="json"),
            support=support,
            limitation="The Flight has no accepted trajectory records.",
        )

    def find_sector_passages(
        self,
        **kwargs: object,
    ) -> HybridQueryToolObservation:
        query = FindSectorPassagesInput.model_validate(kwargs)
        start, end = self._interval(query.start, query.end)
        page = self.service.find_sector_passages(
            SectorPassageQuery(
                sector_id=query.sector_id,
                flight_id=self._flight_id(query.flight_id),
                temporal_domain_id=self._temporal_domain(
                    query.temporal_domain_id
                ),
                start=start,
                end=end,
                source_ids=self.scope.source_ids,
                source_families=tuple(
                    family.value for family in self.scope.source_families
                ),
                offset=self._offset(query.offset),
                limit=self._limit(query.limit),
            )
        )
        rows = tuple(
            row
            for row in page.passages
            if self._evidence_allowed(row.source_ids, row.source_version_ids)
        )
        support = [
            HybridQuerySupportRecord(
                kind="sector_passage",
                publication_ids=(row.flight_publication_id,),
                flight_ids=(row.flight_id,),
                route_ids=(row.route_id,),
                track_point_ids=(row.track_point_id,),
                sector_passage_ids=(row.passage_id,),
                derivation_ids=(row.derivation_id,),
                source_ids=row.source_ids,
                source_version_ids=row.source_version_ids,
                source_anchor_ids=row.source_anchor_ids,
            )
            for row in rows
        ]
        return self._observation(
            payload={
                "total_matches": len(rows),
                "offset": page.offset,
                "limit": page.limit,
                "passages": [row.model_dump(mode="json") for row in rows],
            },
            support=support,
            limitation="No accepted SectorPassage matched the bounded filters.",
        )

    def analyze_sector_traffic(
        self,
        **kwargs: object,
    ) -> HybridQueryToolObservation:
        query = AnalyzeSectorTrafficInput.model_validate(kwargs)
        start, end = self._interval(query.start, query.end)
        if start is None or end is None:
            raise ValueError("sector analysis requires a UTC interval")
        if query.analysis == "ranking":
            result = self.service.rank_sector_traffic(
                start=start,
                end=end,
                limit=self._limit(query.limit),
                source_ids=self.scope.source_ids,
                source_families=tuple(
                    family.value for family in self.scope.source_families
                ),
            )
            flight_ids = _unique(
                [value for row in result.rows for value in row.flight_ids]
            )
            passage_ids = _unique(
                [value for row in result.rows for value in row.passage_ids]
            )
        else:
            result = self.service.find_close_sector_passage_pairs(
                sector_id=query.sector_id or "",
                start=start,
                end=end,
                max_seconds=query.max_seconds or 0,
                source_ids=self.scope.source_ids,
                source_families=tuple(
                    family.value for family in self.scope.source_families
                ),
            )
            flight_ids = _unique(
                [
                    value
                    for row in result.rows
                    for value in (row.first_flight_id, row.second_flight_id)
                ]
            )
            passage_ids = _unique(
                [
                    value
                    for row in result.rows
                    for value in (row.first_passage_id, row.second_passage_id)
                ]
            )
        derivation = result.derivation
        source_ids = self._source_ids_for_versions(
            derivation.input_source_version_ids
        )
        if not self._evidence_allowed(
            source_ids,
            derivation.input_source_version_ids,
        ):
            raise ValueError("sector analysis broadens the source query scope")
        support = []
        if result.rows:
            support.append(
                HybridQuerySupportRecord(
                    kind="aggregate_result",
                    publication_ids=derivation.input_publication_ids,
                    flight_ids=flight_ids,
                    sector_passage_ids=passage_ids,
                    derivation_ids=(derivation.derivation_id,),
                    source_ids=source_ids,
                    source_version_ids=derivation.input_source_version_ids,
                )
            )
        return self._observation(
            payload=result.model_dump(mode="json"),
            support=support,
            limitation="The bounded interval produced no sector-analysis rows.",
        )

    def find_flight_weather_associations(
        self,
        *,
        flight_id: str,
        match_mode: Literal["nearest", "all"] = "nearest",
    ) -> HybridQueryToolObservation:
        flight_id = self._flight_id(flight_id) or flight_id
        rows = self.service.find_flight_weather_associations(
            flight_id=flight_id,
            match_mode=match_mode,
        )
        rows = tuple(
            row
            for row in rows
            if self._evidence_allowed(row.source_ids, row.source_version_ids)
        )
        support = [
            HybridQuerySupportRecord(
                kind="temporal_association",
                publication_ids=(
                    row.flight_publication_id,
                    row.weather_publication_id,
                ),
                flight_ids=(row.flight_id,),
                derivation_ids=(row.derivation_id,),
                temporal_association_ids=(row.association_id,),
                source_ids=row.source_ids,
                source_version_ids=row.source_version_ids,
                source_anchor_ids=row.source_anchor_ids,
            )
            for row in rows
        ]
        return self._observation(
            payload={
                "match_mode": match_mode,
                "causal_claim": False,
                "associations": [
                    row.model_dump(mode="json") for row in rows
                ],
            },
            support=support,
            limitation="No non-causal Flight-Weather association was found.",
        )

    def find_tmi_applicability_candidates(
        self,
        **kwargs: object,
    ) -> HybridQueryToolObservation:
        query = FindTMIApplicabilityInput.model_validate(kwargs)
        page = self.service.find_tmi_applicability_candidates(
            TMIApplicabilityQuery(
                applicability_id=query.applicability_id,
                flight_id=self._flight_id(query.flight_id),
                tmi_root_id=self._tmi_root_id(query.tmi_root_id),
                tmi_family=query.tmi_family,
                status=query.status,
                temporal_domain_id=self._temporal_domain(
                    query.temporal_domain_id
                ),
                source_ids=self.scope.source_ids,
                source_families=tuple(
                    family.value for family in self.scope.source_families
                ),
                offset=self._offset(query.offset),
                limit=self._limit(query.limit),
            )
        )
        rows = tuple(
            row
            for row in page.candidates
            if self._evidence_allowed(row.source_ids, row.source_version_ids)
        )
        support = [
            HybridQuerySupportRecord(
                kind="tmi_applicability",
                root_ids=(row.flight_id, row.tmi_root_id),
                publication_ids=(
                    row.flight_publication_id,
                    row.tmi_publication_id,
                ),
                flight_ids=(row.flight_id,),
                derivation_ids=(row.derivation_id,),
                tmi_applicability_ids=(row.applicability_id,),
                source_ids=row.source_ids,
                source_version_ids=row.source_version_ids,
            )
            for row in rows
        ]
        return self._observation(
            payload={
                "total_matches": len(rows),
                "offset": page.offset,
                "limit": page.limit,
                "candidates": [row.model_dump(mode="json") for row in rows],
                "actual_control_claim": False,
            },
            support=support,
            limitation="No evidence-bounded TMI applicability candidate was found.",
        )

    def read_aviation_graph(
        self,
        *,
        root_id: str,
        direction: Literal["out", "in"] = "out",
        predicate_iris: tuple[str, ...] = (),
        limit: int = 50,
    ) -> HybridQueryToolObservation:
        root_id = self._root_id(root_id)
        root_row = self.store._connection.execute(
            """
            SELECT temporal_domain_id FROM knowledge_roots WHERE root_id = ?
            """,
            (root_id,),
        ).fetchone()
        if (
            root_row is not None
            and self.scope.temporal_domain_id is not None
            and root_row["temporal_domain_id"] != self.scope.temporal_domain_id
        ):
            raise ValueError("root_id is outside the temporal-domain query scope")
        predicate = (
            "fact.subject_iri = ?"
            if direction == "out"
            else "fact.object_kind = 'iri' AND fact.object_value = ?"
        )
        parameters: list[object] = [root_id]
        if predicate_iris:
            placeholders = ",".join("?" for _ in predicate_iris)
            predicate += f" AND fact.predicate_iri IN ({placeholders})"
            parameters.extend(predicate_iris)
        rows = self.store._connection.execute(
            f"""
            SELECT fact.*, root.active_publication_id,
                   source.source_id, evidence.source_version_id,
                   evidence.source_anchor_id
            FROM knowledge_roots AS root
            JOIN publication_facts AS member
              ON member.publication_id = root.active_publication_id
            JOIN semantic_facts AS fact ON fact.fact_id = member.fact_id
            LEFT JOIN publication_evidence_links AS evidence
              ON evidence.publication_id = root.active_publication_id
             AND evidence.owner_kind = 'fact'
             AND evidence.owner_id = fact.fact_id
            LEFT JOIN source_versions AS source
              ON source.source_version_id = evidence.source_version_id
            WHERE root.root_id = ? AND {predicate}
            ORDER BY fact.predicate_iri, fact.fact_id, source.source_id
            LIMIT ?
            """,
            [root_id, *parameters, limit],
        ).fetchall()
        grouped: dict[str, list[object]] = {}
        for row in rows:
            grouped.setdefault(row["fact_id"], []).append(row)
        paths: list[QueryGraphPath] = []
        support: list[HybridQuerySupportRecord] = []
        for fact_id, fact_rows in grouped.items():
            row = fact_rows[0]
            source_ids = _unique(
                [item["source_id"] for item in fact_rows if item["source_id"]]
            )
            source_version_ids = _unique(
                [
                    item["source_version_id"]
                    for item in fact_rows
                    if item["source_version_id"]
                ]
            )
            source_anchor_ids = _unique(
                [
                    item["source_anchor_id"]
                    for item in fact_rows
                    if item["source_anchor_id"]
                ]
            )
            if not self._evidence_allowed(
                source_ids,
                source_version_ids,
            ):
                continue
            edge = QueryGraphEdge(
                fact_id=fact_id,
                subject_iri=row["subject_iri"],
                predicate_iri=row["predicate_iri"],
                object_kind=row["object_kind"],
                object_value=row["object_value"],
                datatype_iri=row["datatype_iri"],
                source_ids=source_ids,
            )
            path = QueryGraphPath(
                path_id=stable_id(
                    "aviation-graph-path", root_id, direction, fact_id
                ),
                path_kind=f"semantic_neighbor_{direction}",
                edges=(edge,),
                source_ids=source_ids,
            )
            paths.append(path)
            support.append(
                HybridQuerySupportRecord(
                    kind="source_fact",
                    root_ids=(root_id,),
                    publication_ids=(row["active_publication_id"],),
                    fact_ids=(fact_id,),
                    graph_path_ids=(path.path_id,),
                    source_ids=source_ids,
                    source_version_ids=source_version_ids,
                    source_anchor_ids=source_anchor_ids,
                )
            )
        return self._observation(
            payload={
                "root_id": root_id,
                "direction": direction,
                "paths": [path.model_dump(mode="json") for path in paths],
            },
            support=support,
            graph_paths=tuple(paths),
            limitation="No accepted semantic neighbor was found.",
        )


def build_flight_airspace_query_tools(
    gateway: FlightAirspaceQueryGateway,
) -> list[BaseTool]:
    """Expose generic deterministic domain operations to the Query Agent."""

    @tool("find_flights", args_schema=FindFlightsInput)
    def find_flights_tool(**kwargs: object) -> dict[str, object]:
        """Find accepted Flights using structured filters and paging."""

        return gateway.find_flights(**kwargs).model_dump(mode="json")

    @tool("read_flight", args_schema=FlightInput)
    def read_flight_tool(flight_id: str) -> dict[str, object]:
        """Read one accepted Flight publication and exact source binding."""

        return gateway.read_flight(flight_id).model_dump(mode="json")

    @tool("find_airports", args_schema=FindAirportsInput)
    def find_airports_tool(**kwargs: object) -> dict[str, object]:
        """Find Airports and source-qualified ARTCC role assignments."""

        return gateway.find_airports(**kwargs).model_dump(mode="json")

    @tool("read_flight_trajectory", args_schema=FlightInput)
    def read_flight_trajectory_tool(flight_id: str) -> dict[str, object]:
        """Read accepted Route, TrackPoint, Fix, and Sector records."""

        return gateway.read_flight_trajectory(flight_id).model_dump(
            mode="json"
        )

    @tool("find_sector_passages", args_schema=FindSectorPassagesInput)
    def find_sector_passages_tool(**kwargs: object) -> dict[str, object]:
        """Find source-bound Flight passages through named Sectors."""

        return gateway.find_sector_passages(**kwargs).model_dump(mode="json")

    @tool("analyze_sector_traffic", args_schema=AnalyzeSectorTrafficInput)
    def analyze_sector_traffic_tool(**kwargs: object) -> dict[str, object]:
        """Rank Sector traffic or compare close passages over an interval."""

        return gateway.analyze_sector_traffic(**kwargs).model_dump(mode="json")

    @tool("find_flight_weather_associations", args_schema=FlightWeatherInput)
    def find_flight_weather_associations_tool(
        flight_id: str,
        match_mode: Literal["nearest", "all"] = "nearest",
    ) -> dict[str, object]:
        """Read non-causal nearest or all Flight-Weather associations."""

        return gateway.find_flight_weather_associations(
            flight_id=flight_id,
            match_mode=match_mode,
        ).model_dump(mode="json")

    @tool(
        "find_tmi_applicability_candidates",
        args_schema=FindTMIApplicabilityInput,
    )
    def find_tmi_applicability_candidates_tool(
        **kwargs: object,
    ) -> dict[str, object]:
        """Find rule-derived candidates, never proof of actual TMI control."""

        return gateway.find_tmi_applicability_candidates(**kwargs).model_dump(
            mode="json"
        )

    @tool("read_aviation_graph", args_schema=AviationGraphInput)
    def read_aviation_graph_tool(**kwargs: object) -> dict[str, object]:
        """Read bounded accepted semantic neighbors for one knowledge root."""

        return gateway.read_aviation_graph(**kwargs).model_dump(mode="json")  # type: ignore[arg-type]

    return [
        find_flights_tool,
        read_flight_tool,
        find_airports_tool,
        read_flight_trajectory_tool,
        find_sector_passages_tool,
        analyze_sector_traffic_tool,
        find_flight_weather_associations_tool,
        find_tmi_applicability_candidates_tool,
        read_aviation_graph_tool,
    ]


__all__ = [
    "FlightAirspaceQueryGateway",
    "build_flight_airspace_query_tools",
]
