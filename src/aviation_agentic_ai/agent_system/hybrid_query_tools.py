"""Read-only structured, graph, vector, and source tools for HybridRAG."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from typing import Literal

from langchain_core.tools import BaseTool, tool
from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryEvidence,
    HybridQueryScope,
    HybridQuerySupportRecord,
    HybridQueryToolObservation,
    QueryGraphEdge,
    QueryGraphPath,
    SourceFamily,
    StrictModel,
)
from aviation_agentic_ai.agent_system.query_runtime import QueryRuntime
from aviation_agentic_ai.agent_system.storage_contracts import (
    EventEvidenceLink,
    EventWeatherAssociation,
    SourceChunkRecord,
    SourceVersionRecord,
    TMIEventQuery,
    TMIEventRecord,
)
from aviation_agentic_ai.agent_system.tmi_event_graph import (
    build_tmi_event_graph,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
    TMIEventSimilarityQuery,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_search import (
    rank_tmi_events_by_metadata as search_ranked_tmi_events,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id


ReasonStatus = Literal["formal", "profile_gap", "missing"]
ObservationPhase = Literal["baseline", "active", "recovery"]
GraphView = Literal["edges", "evidence_paths"]


class EventEvidencePath(StrictModel):
    """One reviewed event-scoped graph path and its exact support binding."""

    path: QueryGraphPath
    support_kind: Literal["non_causal_context", "public_observation"]
    event_id: str = Field(min_length=1)
    fact_ids: tuple[str, ...]
    context_association_ids: tuple[str, ...] = ()
    observation_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...]
    source_version_ids: tuple[str, ...] = ()
    source_anchor_ids: tuple[str, ...] = ()

    def support_record(self) -> HybridQuerySupportRecord:
        return HybridQuerySupportRecord(
            kind=self.support_kind,
            event_ids=(self.event_id,),
            fact_ids=self.fact_ids,
            context_association_ids=self.context_association_ids,
            observation_ids=self.observation_ids,
            graph_path_ids=(self.path.path_id,),
            source_ids=self.source_ids,
            source_version_ids=self.source_version_ids,
            source_anchor_ids=self.source_anchor_ids,
        )


class FindTMIEventsInput(StrictModel):
    event_type_iri: str | None = Field(default=None, min_length=1)
    facility_id: str | None = Field(default=None, min_length=1)
    reason_status: ReasonStatus | None = None
    reason_value: str | None = Field(default=None, min_length=1)
    offset: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=1, le=100)


class EventInput(StrictModel):
    event_id: str = Field(min_length=1)


class PublicObservationsInput(EventInput):
    phases: tuple[ObservationPhase, ...] = (
        "baseline",
        "active",
        "recovery",
    )


class TMIEventGraphInput(EventInput):
    view: GraphView = "edges"
    entity_iri: str | None = Field(default=None, min_length=1)
    direction: Literal["out", "in"] = "out"
    predicate_iris: tuple[str, ...] = ()
    limit: int = Field(default=50, ge=1, le=100)


class SimilarTMIEventsInput(StrictModel):
    reference_event_id: str = Field(min_length=1)
    candidate_scope: Literal["archive", "prior"] | None = None
    event_type_iri: str | None = Field(default=None, min_length=1)
    facility_id: str | None = Field(default=None, min_length=1)
    reason_status: ReasonStatus | None = None
    reason_value: str | None = Field(default=None, min_length=1)
    offset: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=1, le=100)


class SearchSourceTextInput(StrictModel):
    query: str = Field(min_length=1)
    families: tuple[SourceFamily, ...] = ()
    event_id: str | None = Field(default=None, min_length=1)
    limit: int = Field(default=10, ge=1, le=20)


class SemanticSearchSourcesInput(SearchSourceTextInput):
    pass


class ReadSourceInput(StrictModel):
    source_version_id: str = Field(min_length=1)
    source_anchor_id: str | None = Field(default=None, min_length=1)
    offset: int = Field(default=0, ge=0)
    max_chars: int = Field(default=6000, ge=1, le=8000)


def _json(payload: object) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=(
            lambda value: value.isoformat()
            if isinstance(value, datetime)
            else str(value)
        ),
    )


def _local_name(iri: str) -> str:
    return iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1].rsplit(":", 1)[-1]


def _formal_report_iri(report_id: str) -> str:
    return report_id if report_id.startswith("urn:") else f"urn:aviation-agentic-ai:{report_id}"


def _path(
    *,
    event_id: str,
    path_kind: str,
    binding_id: str,
    controlled_edge: QueryGraphEdge,
    related_edge: QueryGraphEdge,
    additional_source_id: str,
) -> QueryGraphPath:
    source_ids = tuple(
        sorted(
            {
                *controlled_edge.source_ids,
                *related_edge.source_ids,
                additional_source_id,
            }
        )
    )
    return QueryGraphPath(
        path_id=stable_id(
            "tmi-event-evidence-path",
            event_id,
            path_kind,
            binding_id,
            controlled_edge.fact_id,
            related_edge.fact_id,
        ),
        path_kind=path_kind,
        edges=(controlled_edge, related_edge),
        source_ids=source_ids,
    )


def _unique(values: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


class HybridQueryGateway:
    """Enforce one immutable user scope around all live query tools."""

    def __init__(
        self,
        *,
        runtime: QueryRuntime,
        scope: HybridQueryScope,
    ) -> None:
        self.runtime = runtime
        self.store = runtime.store
        self.scope = scope

    def _event_matches_scope(self, event: TMIEventRecord) -> bool:
        if not all(
            (
                self.scope.event_type_iri is None
                or self.scope.event_type_iri in event.event_type_iris,
                self.scope.facility_id is None
                or self.scope.facility_id in event.facility_ids,
                self.scope.reason_status is None
                or self.scope.reason_status == event.reason_status,
                self.scope.reason_value is None
                or self.scope.reason_value == event.reason_value,
            )
        ):
            return False
        if not self.scope.source_ids and not self.scope.source_families:
            return True
        sources = self.store.get_event_sources(event.event_id)
        return any(
            (
                not self.scope.source_ids
                or source.source_id in self.scope.source_ids
            )
            and (
                not self.scope.source_families
                or source.family in self.scope.source_families
            )
            for source in sources
        )

    def _event_id(self, event_id: str) -> str:
        if self.scope.event_id is not None and event_id != self.scope.event_id:
            raise ValueError("event_id is outside the query scope")
        event = self.store.get_event(event_id)
        if event is not None and not self._event_matches_scope(event):
            raise ValueError("event_id is outside the query scope")
        return event_id

    def _filter(
        self,
        field_name: Literal[
            "event_type_iri",
            "facility_id",
            "reason_status",
            "reason_value",
        ],
        requested: str | None,
    ) -> str | None:
        fixed = getattr(self.scope, field_name)
        if fixed is not None and requested not in {None, fixed}:
            raise ValueError(f"{field_name} is outside the query scope")
        return fixed if fixed is not None else requested

    def _offset(self, requested: int | None) -> int:
        if requested is None:
            return self.scope.offset
        if requested < self.scope.offset:
            raise ValueError("offset broadens the query scope")
        return requested

    def _limit(self, requested: int | None) -> int:
        if requested is None:
            return self.scope.limit
        if requested > self.scope.limit:
            raise ValueError("limit broadens the query scope")
        return requested

    def _families(
        self,
        requested: tuple[SourceFamily, ...],
    ) -> tuple[SourceFamily, ...]:
        fixed = set(self.scope.source_families)
        if fixed and any(family not in fixed for family in requested):
            raise ValueError("source families are outside the query scope")
        return tuple(sorted(requested or self.scope.source_families, key=str))

    def _allowed_source_versions(
        self,
        *,
        event_id: str | None = None,
        families: tuple[SourceFamily, ...] = (),
    ) -> tuple[SourceVersionRecord, ...]:
        effective_event_id = event_id or self.scope.event_id
        effective_families = self._families(families)
        if effective_event_id is not None:
            effective_event_id = self._event_id(effective_event_id)
            versions = self.store.get_event_sources(effective_event_id)
        else:
            versions = self.store.list_source_versions(
                current_only=True,
                families=effective_families,
            )
        return tuple(
            sorted(
                (
                    version
                    for version in versions
                    if (
                        not effective_families
                        or version.family in effective_families
                    )
                    and (
                        not self.scope.source_ids
                        or version.source_id in self.scope.source_ids
                    )
                ),
                key=lambda version: version.source_version_id,
            )
        )

    @staticmethod
    def _source_maps(
        sources: tuple[SourceVersionRecord, ...],
    ) -> tuple[dict[str, SourceVersionRecord], dict[str, str]]:
        by_version = {
            source.source_version_id: source for source in sources
        }
        logical_by_version = {
            source.source_version_id: source.source_id for source in sources
        }
        return by_version, logical_by_version

    def _owner_links(
        self,
        event_id: str,
        owner_kind: str,
        owner_id: str,
    ) -> tuple[EventEvidenceLink, ...]:
        return tuple(
            link
            for link in self.store.get_event_evidence(event_id)
            if link.owner_kind == owner_kind and link.owner_id == owner_id
        )

    def _allowed_event_sources(
        self,
        event_id: str,
    ) -> dict[str, SourceVersionRecord]:
        """Return exact event bindings after applying the immutable scope."""

        return {
            source.source_version_id: source
            for source in self.store.get_event_sources(event_id)
            if (
                not self.scope.source_ids
                or source.source_id in self.scope.source_ids
            )
            and (
                not self.scope.source_families
                or source.family in self.scope.source_families
            )
        }

    def _support_for_owner(
        self,
        *,
        event_id: str,
        owner_kind: Literal[
            "fact",
            "profile_gap",
            "weather_association",
            "public_observation",
        ],
        owner_id: str,
        support_kind: Literal[
            "source_fact",
            "non_causal_context",
            "public_observation",
        ],
        fact_ids: tuple[str, ...] = (),
        profile_gap_ids: tuple[str, ...] = (),
        context_association_ids: tuple[str, ...] = (),
        observation_ids: tuple[str, ...] = (),
        graph_path_ids: tuple[str, ...] = (),
    ) -> HybridQuerySupportRecord | None:
        links = self._owner_links(event_id, owner_kind, owner_id)
        sources = self._allowed_event_sources(event_id)
        selected = [
            link
            for link in links
            if link.source_version_id in sources
        ]
        if not selected:
            return None
        return HybridQuerySupportRecord(
            kind=support_kind,
            event_ids=(event_id,),
            fact_ids=fact_ids,
            profile_gap_ids=profile_gap_ids,
            context_association_ids=context_association_ids,
            observation_ids=observation_ids,
            graph_path_ids=graph_path_ids,
            source_ids=_unique(
                [
                    sources[link.source_version_id].source_id
                    for link in selected
                ]
            ),
            source_version_ids=_unique(
                [link.source_version_id for link in selected]
            ),
            source_anchor_ids=_unique(
                [
                    link.source_anchor_id
                    for link in selected
                    if link.source_anchor_id is not None
                ]
            ),
        )

    def _publication_support(
        self,
        event: TMIEventRecord,
    ) -> HybridQuerySupportRecord | None:
        source = self._allowed_event_sources(event.event_id).get(
            event.publication_source_version_id
        )
        if source is None:
            return None
        return HybridQuerySupportRecord(
            kind="source_fact",
            event_ids=(event.event_id,),
            source_ids=(source.source_id,),
            source_version_ids=(event.publication_source_version_id,),
        )

    def find_tmi_events(
        self,
        *,
        event_type_iri: str | None = None,
        facility_id: str | None = None,
        reason_status: ReasonStatus | None = None,
        reason_value: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> HybridQueryToolObservation:
        """Find active TMI events with exact filters and bounded paging."""

        if self.scope.event_id is not None:
            self._offset(offset)
            self._limit(limit)
            event = self.store.get_event(self.scope.event_id)
            events = (
                ()
                if event is None or not self._event_matches_scope(event)
                else (event,)
            )
            total_matches, page_offset, page_limit = len(events), 0, 1
        else:
            page = self.store.find_tmi_events(
                TMIEventQuery(
                    event_type_iri=self._filter(
                        "event_type_iri",
                        event_type_iri,
                    ),
                    facility_id=self._filter("facility_id", facility_id),
                    reason_status=self._filter(  # type: ignore[arg-type]
                        "reason_status",
                        reason_status,
                    ),
                    reason_value=self._filter(
                        "reason_value",
                        reason_value,
                    ),
                    offset=self._offset(offset),
                    limit=self._limit(limit),
                )
            )
            events = tuple(
                event
                for event in page.events
                if self._event_matches_scope(event)
            )
            total_matches = (
                page.total_matches
                if not self.scope.source_ids
                and not self.scope.source_families
                else len(events)
            )
            page_offset, page_limit = page.offset, page.limit
        publication_support = {
            event.event_id: record
            for event in events
            if (record := self._publication_support(event)) is not None
        }
        support = tuple(publication_support.values())
        return HybridQueryToolObservation(
            status="ok" if events else "insufficient",
            content=_json(
                {
                    "total_matches": total_matches,
                    "offset": page_offset,
                    "limit": page_limit,
                    "events": [
                        (
                            event.model_dump(mode="json")
                            if event.event_id in publication_support
                            else {
                                "event_id": event.event_id,
                                "publication_id": event.publication_id,
                            }
                        )
                        for event in events
                    ],
                }
            ),
            details=self._evidence_from_support(list(support)),
            support_records=support,
            limitation=(
                ""
                if events
                else "No TMI events match the bounded filters."
            ),
        )

    def read_tmi_event_facts(
        self,
        *,
        event_id: str,
    ) -> HybridQueryToolObservation:
        """Read formal facts and the declared-reason state for one event."""

        event_id = self._event_id(event_id)
        event = self.store.get_event(event_id)
        if event is None:
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json({"event_id": event_id, "facts": []}),
                limitation="The requested event is not present in the store.",
            )
        candidate_facts = tuple(
            fact
            for fact in self.store.get_event_facts(event_id)
            if fact.subject_iri == event_id
        )
        candidate_gaps = self.store.get_event_profile_gaps(event_id)
        publication_support = self._publication_support(event)
        support: list[HybridQuerySupportRecord] = (
            [] if publication_support is None else [publication_support]
        )
        facts = []
        for fact in candidate_facts:
            record = self._support_for_owner(
                event_id=event_id,
                owner_kind="fact",
                owner_id=fact.fact_id,
                support_kind="source_fact",
                fact_ids=(fact.fact_id,),
            )
            if record is not None:
                facts.append(fact)
                support.append(record)
        gaps = []
        for gap in candidate_gaps:
            record = self._support_for_owner(
                event_id=event_id,
                owner_kind="profile_gap",
                owner_id=gap.profile_gap_id,
                support_kind="source_fact",
                profile_gap_ids=(gap.profile_gap_id,),
            )
            if record is not None:
                gaps.append(gap)
                support.append(record)
                continue
            source = self._allowed_event_sources(event_id).get(
                gap.source_version_id
            )
            if source is not None:
                gaps.append(gap)
                support.append(
                    HybridQuerySupportRecord(
                        kind="source_fact",
                        event_ids=(event_id,),
                        profile_gap_ids=(gap.profile_gap_id,),
                        source_ids=(source.source_id,),
                        source_version_ids=(gap.source_version_id,),
                        source_anchor_ids=(gap.source_anchor_id,),
                    )
                )
        return HybridQueryToolObservation(
            status="ok" if support else "insufficient",
            content=_json(
                {
                    "event": (
                        event.model_dump(mode="json")
                        if publication_support is not None
                        else {"event_id": event_id}
                    ),
                    "facts": [
                        fact.model_dump(mode="json") for fact in facts
                    ],
                    "profile_gaps": [
                        gap.model_dump(mode="json") for gap in gaps
                    ],
                }
            ),
            details=self._evidence_from_support(support),
            support_records=tuple(support),
            limitation=(
                ""
                if support
                else "No event facts are available within the source scope."
            ),
        )

    def read_tmi_operational_context(
        self,
        *,
        event_id: str,
    ) -> HybridQueryToolObservation:
        """Read time-bounded Weather context without asserting causation."""

        event_id = self._event_id(event_id)
        event = self.store.get_event(event_id)
        if event is None:
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json({"event_id": event_id, "associations": []}),
                limitation="The requested event is not present in the store.",
            )
        association_support: list[
            tuple[EventWeatherAssociation, HybridQuerySupportRecord]
        ] = []
        for association in self.store.get_event_weather(event_id):
            record = self._support_for_owner(
                event_id=event_id,
                owner_kind="weather_association",
                owner_id=association.association_id,
                support_kind="non_causal_context",
                context_association_ids=(association.association_id,),
            )
            if record is not None:
                association_support.append((association, record))
        associations = tuple(
            association for association, _ in association_support
        )
        report_ids = {association.report_id for association in associations}
        report_tokens = {
            report_id.rsplit(":", 1)[-1] for report_id in report_ids
        }
        facts = tuple(
            fact
            for fact in self.store.get_event_facts(event_id)
            if fact.subject_iri in report_ids
            or fact.subject_iri.rsplit(":", 1)[-1] in report_tokens
        )
        support: list[HybridQuerySupportRecord] = []
        for association, association_record in association_support:
            report_fact_ids = tuple(
                fact.fact_id
                for fact in facts
                if fact.subject_iri == association.report_id
                or fact.subject_iri.rsplit(":", 1)[-1]
                == association.report_id.rsplit(":", 1)[-1]
            )
            record = self._support_for_owner(
                event_id=event_id,
                owner_kind="weather_association",
                owner_id=association.association_id,
                support_kind="non_causal_context",
                fact_ids=report_fact_ids,
                context_association_ids=(association.association_id,),
            )
            support.append(record or association_record)
        return HybridQueryToolObservation(
            status="ok" if associations else "insufficient",
            content=_json(
                {
                    "event_id": event_id,
                    "causal_claim": False,
                    "evidence_role": "non_causal_operational_context",
                    "associations": [
                        association.model_dump(mode="json")
                        for association in associations
                    ],
                    "report_facts": [
                        fact.model_dump(mode="json") for fact in facts
                    ],
                }
            ),
            details=self._evidence_from_support(support),
            support_records=tuple(support),
            limitation=(
                ""
                if associations
                else "No retained operational context is available."
            ),
        )

    def read_public_observations(
        self,
        *,
        event_id: str,
        phases: tuple[ObservationPhase, ...] = (
            "baseline",
            "active",
            "recovery",
        ),
    ) -> HybridQueryToolObservation:
        """Read source-qualified BTS public observations."""

        event_id = self._event_id(event_id)
        event = self.store.get_event(event_id)
        candidate_observations = (
            ()
            if event is None
            else self.store.get_event_observations(event_id, phases)
        )
        support: list[HybridQuerySupportRecord] = []
        observations = []
        for observation in candidate_observations:
            record = self._support_for_owner(
                event_id=event_id,
                owner_kind="public_observation",
                owner_id=observation.observation_id,
                support_kind="public_observation",
                fact_ids=observation.fact_ids,
                observation_ids=(observation.observation_id,),
            )
            if record is not None:
                observations.append(observation)
                support.append(record)
        selected_observations = tuple(observations)
        return HybridQueryToolObservation(
            status="ok" if selected_observations else "insufficient",
            content=_json(
                {
                    "event_id": event_id,
                    "evidence_role": "bts_reported_public_observation",
                    "causal_claim": False,
                    "not_interpreted_as": [
                        "FAA demand",
                        "FAA capacity",
                        "FAA AAR",
                        "FAA EDCT",
                        "decision cause",
                    ],
                    "observations": [
                        {
                            **observation.model_dump(mode="json"),
                            "value": (
                                str(observation.value)
                                if isinstance(observation.value, Decimal)
                                else observation.value
                            ),
                        }
                        for observation in selected_observations
                    ],
                }
            ),
            details=self._evidence_from_support(support),
            support_records=tuple(support),
            limitation=(
                ""
                if selected_observations
                else "No BTS public observations are available."
            ),
        )

    @staticmethod
    def _evidence_from_support(
        support: list[HybridQuerySupportRecord],
    ) -> HybridQueryEvidence:
        return HybridQueryEvidence(
            event_ids=_unique(
                [
                    value
                    for record in support
                    for value in record.event_ids
                ]
            ),
            fact_ids=_unique(
                [
                    value
                    for record in support
                    for value in record.fact_ids
                ]
            ),
            profile_gap_ids=_unique(
                [
                    value
                    for record in support
                    for value in record.profile_gap_ids
                ]
            ),
            context_association_ids=_unique(
                [
                    value
                    for record in support
                    for value in record.context_association_ids
                ]
            ),
            observation_ids=_unique(
                [
                    value
                    for record in support
                    for value in record.observation_ids
                ]
            ),
            graph_path_ids=_unique(
                [
                    value
                    for record in support
                    for value in record.graph_path_ids
                ]
            ),
            source_ids=_unique(
                [
                    value
                    for record in support
                    for value in record.source_ids
                ]
            ),
            source_version_ids=_unique(
                [
                    value
                    for record in support
                    for value in record.source_version_ids
                ]
            ),
            source_anchor_ids=_unique(
                [
                    value
                    for record in support
                    for value in record.source_anchor_ids
                ]
            ),
            chunk_ids=_unique(
                [
                    value
                    for record in support
                    for value in record.chunk_ids
                ]
            ),
        )

    def read_tmi_event_graph(
        self,
        *,
        event_id: str,
        view: GraphView = "edges",
        entity_iri: str | None = None,
        direction: Literal["out", "in"] = "out",
        predicate_iris: tuple[str, ...] = (),
        limit: int = 50,
    ) -> HybridQueryToolObservation:
        """Read bounded formal edges or reviewed non-causal paths."""

        event_id = self._event_id(event_id)
        event = self.store.get_event(event_id)
        if event is None:
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json({"event_id": event_id, "edges": []}),
                limitation="The requested event is not present in the store.",
            )
        if view == "evidence_paths":
            return self._read_tmi_event_evidence_paths(
                event_id=event_id,
                limit=limit,
            )
        candidate_edges = build_tmi_event_graph(self.store, event_id).edges(
            entity_iri=entity_iri,
            direction=direction,
            predicate_iris=predicate_iris,
        )
        support: list[HybridQuerySupportRecord] = []
        edges = []
        for edge in candidate_edges:
            record = self._support_for_owner(
                event_id=event_id,
                owner_kind="fact",
                owner_id=edge.fact_id,
                support_kind="source_fact",
                fact_ids=(edge.fact_id,),
            )
            if record is not None:
                edges.append(edge)
                support.append(record)
            if len(edges) >= limit:
                break
        selected_edges = tuple(edges)
        return HybridQueryToolObservation(
            status="ok" if selected_edges else "insufficient",
            content=_json(
                {
                    "event_id": event_id,
                    "view": "edges",
                    "edges": [
                        edge.model_dump(mode="json") for edge in selected_edges
                    ],
                }
            ),
            details=self._evidence_from_support(support),
            support_records=tuple(support),
            limitation=(
                ""
                if selected_edges
                else "No formal graph edges match the bounded filter."
            ),
        )

    def _read_tmi_event_evidence_paths(
        self,
        *,
        event_id: str,
        limit: int,
    ) -> HybridQueryToolObservation:
        graph = build_tmi_event_graph(self.store, event_id)
        edges = graph.edges()
        controlled_edges = tuple(
            edge
            for edge in edges
            if edge.subject_iri == event_id
            and edge.object_kind == "iri"
            and _local_name(edge.predicate_iri) == "controlledNASelement"
        )
        sources_by_version = {
            source.source_version_id: source
            for source in self.store.get_event_sources(event_id)
        }
        evidence_paths: list[EventEvidencePath] = []
        for association in self.store.get_event_weather(event_id):
            source = sources_by_version.get(association.source_version_id)
            if source is None:
                continue
            association_support = self._support_for_owner(
                event_id=event_id,
                owner_kind="weather_association",
                owner_id=association.association_id,
                support_kind="non_causal_context",
            )
            if association_support is None:
                continue
            for controlled_edge in controlled_edges:
                controlled_support = self._support_for_owner(
                    event_id=event_id,
                    owner_kind="fact",
                    owner_id=controlled_edge.fact_id,
                    support_kind="source_fact",
                    fact_ids=(controlled_edge.fact_id,),
                )
                if controlled_support is None:
                    continue
                if controlled_edge.object_value != association.facility_id:
                    continue
                for report_edge in edges:
                    if not (
                        report_edge.object_kind == "iri"
                        and _local_name(report_edge.predicate_iri)
                        == "forecastingAirport"
                        and report_edge.subject_iri
                        == _formal_report_iri(association.report_id)
                        and report_edge.object_value
                        == association.facility_id
                    ):
                        continue
                    report_support = self._support_for_owner(
                        event_id=event_id,
                        owner_kind="fact",
                        owner_id=report_edge.fact_id,
                        support_kind="source_fact",
                        fact_ids=(report_edge.fact_id,),
                    )
                    if report_support is None:
                        continue
                    allowed_source_ids = _unique(
                        [
                            *controlled_support.source_ids,
                            *report_support.source_ids,
                            *association_support.source_ids,
                        ]
                    )
                    path = _path(
                        event_id=event_id,
                        path_kind="weather_context_at_controlled_facility",
                        binding_id=association.association_id,
                        controlled_edge=controlled_edge,
                        related_edge=report_edge,
                        additional_source_id=source.source_id,
                    )
                    evidence_paths.append(
                        EventEvidencePath(
                            path=path,
                            support_kind="non_causal_context",
                            event_id=event_id,
                            fact_ids=(
                                controlled_edge.fact_id,
                                report_edge.fact_id,
                            ),
                            context_association_ids=(
                                association.association_id,
                            ),
                            source_ids=allowed_source_ids,
                            source_version_ids=_unique(
                                [
                                    *controlled_support.source_version_ids,
                                    *report_support.source_version_ids,
                                    *association_support.source_version_ids,
                                ]
                            ),
                            source_anchor_ids=_unique(
                                [
                                    *controlled_support.source_anchor_ids,
                                    *report_support.source_anchor_ids,
                                    *association_support.source_anchor_ids,
                                ]
                            ),
                        )
                    )
        edge_by_fact_id = {edge.fact_id: edge for edge in edges}
        for observation in self.store.get_event_observations(
            event_id,
            ("baseline", "active", "recovery"),
        ):
            source = sources_by_version.get(observation.source_version_id)
            if source is None:
                continue
            observation_support = self._support_for_owner(
                event_id=event_id,
                owner_kind="public_observation",
                owner_id=observation.observation_id,
                support_kind="public_observation",
            )
            if observation_support is None:
                continue
            observation_edges = tuple(
                edge_by_fact_id[fact_id]
                for fact_id in observation.fact_ids
                if fact_id in edge_by_fact_id
                and _local_name(edge_by_fact_id[fact_id].predicate_iri)
                == "hasFeatureOfInterest"
            )
            for controlled_edge in controlled_edges:
                controlled_support = self._support_for_owner(
                    event_id=event_id,
                    owner_kind="fact",
                    owner_id=controlled_edge.fact_id,
                    support_kind="source_fact",
                    fact_ids=(controlled_edge.fact_id,),
                )
                if controlled_support is None:
                    continue
                for observation_edge in observation_edges:
                    if (
                        observation_edge.object_kind != "iri"
                        or controlled_edge.object_value
                        != observation_edge.object_value
                    ):
                        continue
                    observation_edge_support = self._support_for_owner(
                        event_id=event_id,
                        owner_kind="fact",
                        owner_id=observation_edge.fact_id,
                        support_kind="public_observation",
                        fact_ids=(observation_edge.fact_id,),
                    )
                    if observation_edge_support is None:
                        continue
                    path = _path(
                        event_id=event_id,
                        path_kind=(
                            "public_observation_at_controlled_facility"
                        ),
                        binding_id=observation.observation_id,
                        controlled_edge=controlled_edge,
                        related_edge=observation_edge,
                        additional_source_id=source.source_id,
                    )
                    evidence_paths.append(
                        EventEvidencePath(
                            path=path,
                            support_kind="public_observation",
                            event_id=event_id,
                            fact_ids=(
                                controlled_edge.fact_id,
                                observation_edge.fact_id,
                            ),
                            observation_ids=(observation.observation_id,),
                            source_ids=_unique(
                                [
                                    *controlled_support.source_ids,
                                    *observation_edge_support.source_ids,
                                    *observation_support.source_ids,
                                ]
                            ),
                            source_version_ids=_unique(
                                [
                                    *controlled_support.source_version_ids,
                                    *observation_edge_support.source_version_ids,
                                    *observation_support.source_version_ids,
                                ]
                            ),
                            source_anchor_ids=_unique(
                                [
                                    *controlled_support.source_anchor_ids,
                                    *observation_edge_support.source_anchor_ids,
                                    *observation_support.source_anchor_ids,
                                ]
                            ),
                        )
                    )
        selected = tuple(
            sorted(
                {
                    item.path.path_id: item for item in evidence_paths
                }.values(),
                key=lambda item: item.path.path_id,
            )[:limit]
        )
        support = [item.support_record() for item in selected]
        paths = tuple(item.path for item in selected)
        details = self._evidence_from_support(support)
        return HybridQueryToolObservation(
            status="ok" if paths else "insufficient",
            content=_json(
                {
                    "event_id": event_id,
                    "view": "evidence_paths",
                    "causal_claim": False,
                    "graph_paths": {
                        path.path_id: path.model_dump(mode="json")
                        for path in paths
                    },
                }
            ),
            details=details,
            support_records=tuple(support),
            graph_paths=paths,
            limitation=(
                ""
                if paths
                else (
                    "No source-bound context or observation path shares "
                    "this event's controlled facility."
                )
            ),
        )

    def find_similar_tmi_events(
        self,
        *,
        reference_event_id: str,
        candidate_scope: Literal["archive", "prior"] | None = None,
        event_type_iri: str | None = None,
        facility_id: str | None = None,
        reason_status: ReasonStatus | None = None,
        reason_value: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> HybridQueryToolObservation:
        """Filter exact metadata before optional event-vector recall."""

        reference_event_id = self._event_id(reference_event_id)
        effective_scope = candidate_scope or self.scope.candidate_scope
        if effective_scope != self.scope.candidate_scope:
            raise ValueError("candidate_scope is outside the query scope")
        if self.runtime.event_index is None:
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json({"matches": []}),
                limitation="The TMI-event vector index is unavailable.",
            )
        query = TMIEventSimilarityQuery(
            reference_event_id=reference_event_id,
            candidate_scope=effective_scope,
            event_type_iri=self._filter("event_type_iri", event_type_iri),
            facility_id=self._filter("facility_id", facility_id),
            reason_status=self._filter(  # type: ignore[arg-type]
                "reason_status",
                reason_status,
            ),
            reason_value=self._filter("reason_value", reason_value),
            offset=self._offset(offset),
            limit=self._limit(limit),
        )
        result = search_ranked_tmi_events(
            self.store,
            self.runtime.event_index,
            query,
        )
        matches = tuple(
            match
            for match in result.matches
            if (
                not self.scope.source_ids
                or match.advisory_source_id in self.scope.source_ids
            )
            and (
                not self.scope.source_families
                or SourceFamily.ATCSCC_ADVISORY
                in self.scope.source_families
            )
        )
        support: list[HybridQuerySupportRecord] = []
        for match in matches:
            event = self.store.get_event(match.event_id)
            if event is not None:
                support.append(
                    HybridQuerySupportRecord(
                        kind="similarity",
                        event_ids=(match.event_id,),
                        source_ids=(match.advisory_source_id,),
                        source_version_ids=(
                            event.publication_source_version_id,
                        ),
                    )
                )
        return HybridQueryToolObservation(
            status=(
                result.status
                if matches or result.status == "blocked"
                else "insufficient"
            ),
            content=_json(
                {
                    "candidate_count": result.candidate_count,
                    "representation_version": result.representation_version,
                    "matches": [
                        match.model_dump(mode="json") for match in matches
                    ],
                    "limitation": result.limitation,
                }
            ),
            details=self._evidence_from_support(support),
            support_records=tuple(support),
            similarity_matches=matches,
            limitation=result.limitation,
        )

    @staticmethod
    def _candidate_payload(
        chunk: SourceChunkRecord,
        version: SourceVersionRecord,
        *,
        similarity: float | None = None,
    ) -> dict[str, object]:
        payload: dict[str, object] = {
            "chunk_id": chunk.chunk_id,
            "source_id": version.source_id,
            "source_version_id": version.source_version_id,
            "source_anchor_id": chunk.source_anchor_id,
            "family": version.family.value,
            "text": chunk.text,
        }
        if similarity is not None:
            payload["similarity"] = similarity
        return payload

    def search_source_text(
        self,
        *,
        query: str,
        families: tuple[SourceFamily, ...] = (),
        event_id: str | None = None,
        limit: int = 10,
    ) -> HybridQueryToolObservation:
        """Return lexical candidates; candidates are not statement support."""

        versions = self._allowed_source_versions(
            event_id=event_id,
            families=families,
        )
        version_by_id, _ = self._source_maps(versions)
        chunks = self.store.search_source_text(
            query,
            source_version_ids=tuple(version_by_id),
            families=self._families(families),
            # Event scope is enforced by the authoritative event_sources
            # whitelist above. A source chunk is a reusable representation of
            # one immutable source version and is not owned by one event.
            event_id=None,
            current_only=False,
            limit=limit,
        )
        payload = [
            self._candidate_payload(chunk, version_by_id[chunk.source_version_id])
            for chunk in chunks
            if chunk.source_version_id in version_by_id
        ]
        return self._candidate_observation(
            payload=payload,
            chunks=chunks,
            version_by_id=version_by_id,
            unavailable_message="No lexical source candidates match the scope.",
        )

    def semantic_search_sources(
        self,
        *,
        query: str,
        families: tuple[SourceFamily, ...] = (),
        event_id: str | None = None,
        limit: int = 10,
    ) -> HybridQueryToolObservation:
        """Return semantic candidates; candidates are not statement support."""

        if self.runtime.source_index is None:
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json({"candidates": []}),
                limitation="The source vector index is unavailable.",
            )
        versions = self._allowed_source_versions(
            event_id=event_id,
            families=families,
        )
        version_by_id, _ = self._source_maps(versions)
        hits = self.runtime.source_index.query_chunks(
            query_text=query,
            candidate_source_version_ids=tuple(version_by_id),
            n_results=limit,
        )
        selected: list[tuple[SourceChunkRecord, float]] = []
        for hit in hits:
            if hit.source_version_id not in version_by_id:
                raise ValueError("source vector hit is outside the query scope")
            chunk = self.store.get_source_chunk(hit.chunk_id)
            if (
                chunk is None
                or chunk.source_version_id != hit.source_version_id
                or chunk.source_anchor_id != hit.source_anchor_id
            ):
                raise ValueError("source vector hit does not match its chunk")
            selected.append((chunk, hit.similarity))
        chunks = tuple(chunk for chunk, _similarity in selected)
        payload = [
            self._candidate_payload(
                chunk,
                version_by_id[chunk.source_version_id],
                similarity=similarity,
            )
            for chunk, similarity in selected
        ]
        return self._candidate_observation(
            payload=payload,
            chunks=chunks,
            version_by_id=version_by_id,
            unavailable_message="No semantic source candidates match the scope.",
        )

    @staticmethod
    def _candidate_observation(
        *,
        payload: list[dict[str, object]],
        chunks: tuple[SourceChunkRecord, ...],
        version_by_id: dict[str, SourceVersionRecord],
        unavailable_message: str,
    ) -> HybridQueryToolObservation:
        selected_chunks = tuple(
            chunk
            for chunk in chunks
            if chunk.source_version_id in version_by_id
        )
        return HybridQueryToolObservation(
            status="ok" if payload else "insufficient",
            content=_json({"candidates": payload}),
            details=HybridQueryEvidence(
                event_ids=_unique(
                    [
                        chunk.event_id
                        for chunk in selected_chunks
                        if chunk.event_id is not None
                    ]
                ),
                source_ids=_unique(
                    [
                        version_by_id[chunk.source_version_id].source_id
                        for chunk in selected_chunks
                    ]
                ),
                source_version_ids=_unique(
                    [
                        chunk.source_version_id
                        for chunk in selected_chunks
                    ]
                ),
                source_anchor_ids=_unique(
                    [
                        chunk.source_anchor_id
                        for chunk in selected_chunks
                    ]
                ),
                chunk_ids=_unique(
                    [chunk.chunk_id for chunk in selected_chunks]
                ),
            ),
            support_records=(),
            limitation="" if payload else unavailable_message,
        )

    def read_source(
        self,
        *,
        source_version_id: str,
        source_anchor_id: str | None = None,
        offset: int = 0,
        max_chars: int = 6000,
    ) -> HybridQueryToolObservation:
        """Read one exact source version and anchor inside the user scope."""

        allowed = {
            version.source_version_id: version
            for version in self._allowed_source_versions()
        }
        if source_version_id not in allowed:
            raise ValueError("source version is outside the query scope")
        version = allowed[source_version_id]
        chunks = self.store.list_source_chunks(
            source_version_ids=(source_version_id,),
            chunk_kind="source_record",
        )
        if source_anchor_id is None:
            full_chunks = tuple(
                chunk
                for chunk in chunks
                if chunk.char_start == 0
                and chunk.char_end == len(version.content)
            )
            if not full_chunks:
                return HybridQueryToolObservation(
                    status="insufficient",
                    content=_json(
                        {
                            "source_version_id": source_version_id,
                            "bounded_text": "",
                        }
                    ),
                    limitation="The source version has no readable anchor.",
                )
            source_anchor_id = full_chunks[0].source_anchor_id
        anchor = self.store.get_source_anchor(source_anchor_id)
        if anchor is None:
            raise ValueError("source anchor does not exist")
        if anchor.source_version_id != source_version_id:
            raise ValueError("source anchor belongs to another source version")
        anchor_length = anchor.char_end - anchor.char_start
        if offset >= anchor_length:
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json(
                    {
                        "source_version_id": source_version_id,
                        "source_anchor_id": source_anchor_id,
                        "bounded_text": "",
                    }
                ),
                limitation="The source offset is outside the selected anchor.",
            )
        relative_end = min(anchor_length, offset + max_chars)
        absolute_start = anchor.char_start + offset
        absolute_end = anchor.char_start + relative_end
        matching_chunks = tuple(
            chunk
            for chunk in chunks
            if chunk.source_anchor_id == source_anchor_id
        )
        chunk_ids = tuple(chunk.chunk_id for chunk in matching_chunks)
        event_ids = (
            (self.scope.event_id,)
            if self.scope.event_id is not None
            else ()
        )
        support = HybridQuerySupportRecord(
            kind="source_record",
            event_ids=event_ids,
            source_ids=(version.source_id,),
            source_version_ids=(source_version_id,),
            source_anchor_ids=(source_anchor_id,),
            chunk_ids=chunk_ids,
        )
        return HybridQueryToolObservation(
            status="ok",
            content=_json(
                {
                    "source_id": version.source_id,
                    "source_version_id": source_version_id,
                    "source_anchor_id": source_anchor_id,
                    "family": version.family.value,
                    "content_sha256": version.content_sha256,
                    "bounded_text": version.content[
                        absolute_start:absolute_end
                    ],
                    "offset": offset,
                    "end": relative_end,
                    "source_url": version.source_url,
                }
            ),
            details=HybridQueryEvidence(
                event_ids=event_ids,
                source_ids=(version.source_id,),
                source_version_ids=(source_version_id,),
                source_anchor_ids=(source_anchor_id,),
                chunk_ids=chunk_ids,
            ),
            support_records=(support,),
        )


def build_hybrid_query_tools(
    gateway: HybridQueryGateway,
) -> list[BaseTool]:
    """Expose the fixed read-only HybridRAG registry to the model."""

    @tool("find_tmi_events", args_schema=FindTMIEventsInput)
    def find_tmi_events_tool(**kwargs: object) -> dict[str, object]:
        """Find TMI events using exact filters and bounded paging."""

        return gateway.find_tmi_events(**kwargs).model_dump(mode="json")  # type: ignore[arg-type]

    @tool("read_tmi_event_facts", args_schema=EventInput)
    def read_tmi_event_facts_tool(event_id: str) -> dict[str, object]:
        """Read formal TMI facts and the declared-reason state."""

        return gateway.read_tmi_event_facts(
            event_id=event_id
        ).model_dump(mode="json")

    @tool("read_tmi_operational_context", args_schema=EventInput)
    def read_tmi_operational_context_tool(
        event_id: str,
    ) -> dict[str, object]:
        """Read retained Weather context without treating it as rationale."""

        return gateway.read_tmi_operational_context(
            event_id=event_id
        ).model_dump(mode="json")

    @tool("read_public_observations", args_schema=PublicObservationsInput)
    def read_public_observations_tool(
        event_id: str,
        phases: tuple[ObservationPhase, ...],
    ) -> dict[str, object]:
        """Read BTS-reported public observations for selected phases."""

        return gateway.read_public_observations(
            event_id=event_id,
            phases=phases,
        ).model_dump(mode="json")

    @tool("read_tmi_event_graph", args_schema=TMIEventGraphInput)
    def read_tmi_event_graph_tool(
        event_id: str,
        view: GraphView = "edges",
        entity_iri: str | None = None,
        direction: Literal["out", "in"] = "out",
        predicate_iris: tuple[str, ...] = (),
        limit: int = 50,
    ) -> dict[str, object]:
        """Read bounded formal edges or reviewed non-causal paths."""

        return gateway.read_tmi_event_graph(
            event_id=event_id,
            view=view,
            entity_iri=entity_iri,
            direction=direction,
            predicate_iris=predicate_iris,
            limit=limit,
        ).model_dump(mode="json")

    @tool("find_similar_tmi_events", args_schema=SimilarTMIEventsInput)
    def find_similar_tmi_events_tool(
        **kwargs: object,
    ) -> dict[str, object]:
        """Find metadata-conditioned historical TMI event candidates."""

        return gateway.find_similar_tmi_events(**kwargs).model_dump(  # type: ignore[arg-type]
            mode="json"
        )

    @tool("search_source_text", args_schema=SearchSourceTextInput)
    def search_source_text_tool(**kwargs: object) -> dict[str, object]:
        """Find lexical source candidates; verify with read_source."""

        return gateway.search_source_text(**kwargs).model_dump(mode="json")  # type: ignore[arg-type]

    @tool(
        "semantic_search_sources",
        args_schema=SemanticSearchSourcesInput,
    )
    def semantic_search_sources_tool(
        **kwargs: object,
    ) -> dict[str, object]:
        """Find semantic source candidates; verify with read_source."""

        return gateway.semantic_search_sources(**kwargs).model_dump(  # type: ignore[arg-type]
            mode="json"
        )

    @tool("read_source", args_schema=ReadSourceInput)
    def read_source_tool(**kwargs: object) -> dict[str, object]:
        """Read exact bounded source text with immutable anchor support."""

        return gateway.read_source(**kwargs).model_dump(mode="json")  # type: ignore[arg-type]

    return [
        find_tmi_events_tool,
        read_tmi_event_facts_tool,
        read_tmi_operational_context_tool,
        read_public_observations_tool,
        read_tmi_event_graph_tool,
        find_similar_tmi_events_tool,
        search_source_text_tool,
        semantic_search_sources_tool,
        read_source_tool,
    ]


__all__ = ["HybridQueryGateway", "build_hybrid_query_tools"]
