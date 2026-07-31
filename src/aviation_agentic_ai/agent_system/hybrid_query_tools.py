"""Read-only Corpus, graph, and Chroma tools for the Hybrid Query Agent."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from typing import Literal

from langchain_core.tools import BaseTool, tool
from pydantic import Field

from aviation_agentic_ai.agent_system.tmi_event_retrieval_contracts import (
    TMIEventSimilarityQuery,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_index import (
    TMI_EVENT_INDEX_MANIFEST,
    ChromaTMIEventRetrievalIndex,
)
from aviation_agentic_ai.agent_system.tmi_event_retrieval_search import (
    find_similar_tmi_events as search_similar_tmi_events,
)
from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryEvidence,
    HybridQueryScope,
    HybridQuerySupportRecord,
    HybridQueryToolObservation,
    QueryGraphEdge,
    QueryGraphPath,
    StrictModel,
)
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusTMIEvent,
    CorpusEventQuery,
    CorpusQueryStore,
)
from aviation_agentic_ai.cross_source.identifiers import stable_id


ReasonStatus = Literal["formal", "profile_gap", "missing"]
ObservationPhase = Literal["baseline", "active", "recovery"]
GraphView = Literal["edges", "evidence_paths"]


class CorpusEventEvidencePath(StrictModel):
    """Corpus binding retained behind one model-visible graph path."""

    path: QueryGraphPath
    support_kind: Literal["non_causal_context", "public_observation"]
    event_id: str = Field(min_length=1)
    fact_ids: tuple[str, ...]
    context_association_ids: tuple[str, ...] = ()
    observation_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...]

    def support_record(self) -> HybridQuerySupportRecord:
        """Bind the path and every supporting corpus identifier together."""

        return HybridQuerySupportRecord(
            kind=self.support_kind,
            event_ids=(self.event_id,),
            fact_ids=self.fact_ids,
            context_association_ids=self.context_association_ids,
            observation_ids=self.observation_ids,
            graph_path_ids=(self.path.path_id,),
            source_ids=self.source_ids,
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
    if report_id.startswith("urn:"):
        return report_id
    return f"urn:aviation-agentic-ai:{report_id}"


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


class HybridQueryGateway:
    """Enforce one immutable CLI scope around all query tools."""

    def __init__(
        self,
        *,
        store: CorpusQueryStore,
        scope: HybridQueryScope,
    ) -> None:
        self.store = store
        self.scope = scope

    def _event_id(self, event_id: str) -> str:
        if self.scope.event_id is not None and event_id != self.scope.event_id:
            raise ValueError("event_id is outside the query scope")
        event = self.store.get_event(event_id)
        if event is not None and not self._event_matches_scope(event):
            raise ValueError("event_id is outside the query scope")
        return event_id

    def _event_matches_scope(self, event: CorpusTMIEvent) -> bool:
        return all(
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
        )

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
        """Find corpus TMI events with exact filters and bounded paging."""

        if self.scope.event_id is not None:
            event = self.store.get_event(self.scope.event_id)
            events = (
                ()
                if event is None or not self._event_matches_scope(event)
                else (event,)
            )
            total_matches = len(events)
            page_offset = 0
            page_limit = 1
        else:
            page = self.store.find_events(
                CorpusEventQuery(
                    event_type_iri=self._filter(
                        "event_type_iri",
                        event_type_iri,
                    ),
                    facility_id=self._filter("facility_id", facility_id),
                    reason_status=self._filter(  # type: ignore[arg-type]
                        "reason_status",
                        reason_status,
                    ),
                    reason_value=self._filter("reason_value", reason_value),
                    offset=self._offset(offset),
                    limit=self._limit(limit),
                )
            )
            events = page.events
            total_matches = page.total_matches
            page_offset = page.offset
            page_limit = page.limit
        event_rows = [
            {
                "event_id": event.event_id,
                "advisory_source_id": event.advisory_source_id,
                "event_type_iris": event.event_type_iris,
                "facility_ids": event.facility_ids,
                "effective_start": event.effective_start,
                "effective_end": event.effective_end,
                "reason_status": event.reason_status,
                "reason_value": event.reason_value,
            }
            for event in events
        ]
        status: Literal["ok", "insufficient"] = (
            "ok" if events else "insufficient"
        )
        source_ids = tuple(
            sorted(
                {
                    source_id
                    for event in events
                    for source_id in event.source_ids
                }
            )
        )
        return HybridQueryToolObservation(
            status=status,
            content=_json(
                {
                    "total_matches": total_matches,
                    "offset": page_offset,
                    "limit": page_limit,
                    "events": event_rows,
                }
            ),
            details=HybridQueryEvidence(
                event_ids=tuple(event.event_id for event in events),
                source_ids=source_ids,
            ),
            support_records=tuple(
                HybridQuerySupportRecord(
                    kind="source_fact",
                    event_ids=(event.event_id,),
                    source_ids=(event.advisory_source_id,),
                )
                for event in events
            ),
            limitation=(
                ""
                if events
                else "No corpus TMI events match the bounded filters."
            ),
        )

    def read_tmi_event_facts(self, *, event_id: str) -> HybridQueryToolObservation:
        """Read formal facts and declared-reason state for one event."""

        event_id = self._event_id(event_id)
        event = self.store.get_event(event_id)
        if event is None:
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json({"event_id": event_id, "facts": []}),
                limitation="The requested event is not present in this corpus.",
            )
        facts = tuple(
            fact
            for fact in self.store.get_event_facts(event_id)
            if fact.subject_iri == event_id
        )
        gaps = tuple(
            gap for gap in self.store.profile_gaps if gap.event_id == event_id
        )
        source_ids = tuple(
            sorted(
                {
                    *event.source_ids,
                    *(source_id for fact in facts for source_id in fact.source_ids),
                    *(gap.source_id for gap in gaps),
                }
            )
        )
        return HybridQueryToolObservation(
            status="ok",
            content=_json(
                {
                    "event": {
                        "event_id": event.event_id,
                        "advisory_source_id": event.advisory_source_id,
                        "event_type_iris": event.event_type_iris,
                        "facility_ids": event.facility_ids,
                        "effective_start": event.effective_start,
                        "effective_end": event.effective_end,
                        "reason_status": event.reason_status,
                        "reason_value": event.reason_value,
                    },
                    "facts": [
                        {
                            "fact_id": fact.fact_id,
                            "subject_iri": fact.subject_iri,
                            "predicate_iri": fact.predicate_iri,
                            "object_kind": fact.object_kind,
                            "object_value": fact.object_value,
                            "source_ids": fact.source_ids,
                            "evidence_texts": fact.evidence_texts,
                        }
                        for fact in facts
                    ],
                    "profile_gaps": [
                        {
                            "profile_gap_id": gap.profile_gap_id,
                            "field": gap.field,
                            "value": gap.value,
                            "evidence_text": gap.evidence_text,
                            "reason": gap.reason,
                            "source_id": gap.source_id,
                        }
                        for gap in gaps
                    ],
                }
            ),
            details=HybridQueryEvidence(
                event_ids=(event.event_id,),
                fact_ids=tuple(fact.fact_id for fact in facts),
                profile_gap_ids=tuple(gap.profile_gap_id for gap in gaps),
                source_ids=source_ids,
            ),
            support_records=(
                HybridQuerySupportRecord(
                    kind="source_fact",
                    event_ids=(event.event_id,),
                    source_ids=(event.advisory_source_id,),
                ),
                *(
                    HybridQuerySupportRecord(
                        kind="source_fact",
                        event_ids=(event.event_id,),
                        fact_ids=(fact.fact_id,),
                        source_ids=tuple(sorted(fact.source_ids)),
                    )
                    for fact in facts
                    if fact.source_ids
                ),
                *(
                    HybridQuerySupportRecord(
                        kind="source_fact",
                        event_ids=(event.event_id,),
                        profile_gap_ids=(gap.profile_gap_id,),
                        source_ids=(gap.source_id,),
                    )
                    for gap in gaps
                ),
            ),
        )

    def read_weather_context(
        self,
        *,
        event_id: str,
    ) -> HybridQueryToolObservation:
        """Read retained Weather context without making a causal claim."""

        event_id = self._event_id(event_id)
        event = self.store.get_event(event_id)
        if event is None:
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json({"event_id": event_id, "associations": []}),
                limitation="The requested event is not present in this corpus.",
            )
        associations = self.store.get_weather_context(event_id)
        report_ids = {row.report_id for row in associations}
        report_tokens = {report_id.rsplit(":", 1)[-1] for report_id in report_ids}
        facts = tuple(
            fact
            for fact in self.store.get_event_facts(event_id)
            if fact.subject_iri in report_ids
            or fact.subject_iri.rsplit(":", 1)[-1] in report_tokens
        )
        status: Literal["ok", "insufficient"] = (
            "ok" if associations and facts else "insufficient"
        )
        source_ids = tuple(
            sorted(
                {
                    *(row.source_id for row in associations),
                    *(source_id for fact in facts for source_id in fact.source_ids),
                }
            )
        )
        return HybridQueryToolObservation(
            status=status,
            content=_json(
                {
                    "event_id": event_id,
                    "causal_claim": False,
                    "evidence_role": "non_causal_weather_context",
                    "associations": [
                        association.model_dump(mode="json")
                        for association in associations
                    ],
                    "report_facts": [
                        {
                            "fact_id": fact.fact_id,
                            "subject_iri": fact.subject_iri,
                            "predicate_iri": fact.predicate_iri,
                            "object_value": fact.object_value,
                            "source_ids": fact.source_ids,
                            "evidence_texts": fact.evidence_texts,
                        }
                        for fact in facts
                    ],
                }
            ),
            details=HybridQueryEvidence(
                event_ids=(event.event_id,),
                fact_ids=tuple(fact.fact_id for fact in facts),
                context_association_ids=tuple(
                    row.association_id for row in associations
                ),
                source_ids=source_ids,
            ),
            support_records=tuple(
                HybridQuerySupportRecord(
                    kind="non_causal_context",
                    event_ids=(event.event_id,),
                    fact_ids=tuple(
                        fact.fact_id
                        for fact in facts
                        if fact.subject_iri == association.report_id
                        or fact.subject_iri.rsplit(":", 1)[-1]
                        == association.report_id.rsplit(":", 1)[-1]
                    ),
                    context_association_ids=(association.association_id,),
                    source_ids=tuple(
                        sorted(
                            {
                                association.source_id,
                                *(
                                    source_id
                                    for fact in facts
                                    if fact.subject_iri == association.report_id
                                    or fact.subject_iri.rsplit(":", 1)[-1]
                                    == association.report_id.rsplit(":", 1)[-1]
                                    for source_id in fact.source_ids
                                ),
                            }
                        )
                    ),
                )
                for association in associations
            ),
            limitation=(
                ""
                if status == "ok"
                else "No retained Weather context is available for this event."
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
        observations = (
            ()
            if event is None
            else self.store.get_public_observations(event_id, phases)
        )
        status: Literal["ok", "insufficient"] = (
            "ok" if observations else "insufficient"
        )
        source_ids = tuple(
            sorted({row.source_id for row in observations})
        )
        return HybridQueryToolObservation(
            status=status,
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
                            "observation_id": row.observation_id,
                            "phase": row.phase,
                            "metric_key": row.metric_key,
                            "value": (
                                str(row.value)
                                if isinstance(row.value, Decimal)
                                else row.value
                            ),
                            "unit_iri": row.unit_iri,
                            "source_id": row.source_id,
                        }
                        for row in observations
                    ],
                }
            ),
            details=HybridQueryEvidence(
                event_ids=(() if event is None else (event.event_id,)),
                fact_ids=tuple(
                    sorted(
                        {
                            fact_id
                            for row in observations
                            for fact_id in row.fact_ids
                        }
                    )
                ),
                observation_ids=tuple(
                    row.observation_id for row in observations
                ),
                source_ids=source_ids,
            ),
            support_records=tuple(
                HybridQuerySupportRecord(
                    kind="public_observation",
                    event_ids=(
                        () if event is None else (event.event_id,)
                    ),
                    observation_ids=(row.observation_id,),
                    source_ids=(row.source_id,),
                )
                for row in observations
            ),
            limitation=(
                ""
                if status == "ok"
                else "No BTS public observations are available for this event."
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
        """Read formal edges or reviewed cross-source paths for one event."""

        event_id = self._event_id(event_id)
        event = self.store.get_event(event_id)
        if event is None:
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json(
                    {
                        "event_id": event_id,
                        "view": view,
                        "edges": [],
                        "graph_paths": {},
                    }
                ),
                limitation="The requested event is not present in this corpus.",
            )
        if view == "evidence_paths":
            return self._read_tmi_event_evidence_paths(
                event_id=event.event_id,
                limit=limit,
            )
        edges = self.store.graph_for_event(event_id).edges(
            entity_iri=entity_iri,
            direction=direction,
            predicate_iris=predicate_iris,
        )[:limit]
        status: Literal["ok", "insufficient"] = (
            "ok" if edges else "insufficient"
        )
        source_ids = tuple(
            sorted(
                {
                    source_id
                    for edge in edges
                    for source_id in edge.source_ids
                }
            )
        )
        return HybridQueryToolObservation(
            status=status,
            content=_json(
                {
                    "event_id": event_id,
                    "view": "edges",
                    "edges": [
                        edge.model_dump(mode="json") for edge in edges
                    ],
                    "graph_paths": {},
                }
            ),
            details=HybridQueryEvidence(
                event_ids=(event.event_id,),
                fact_ids=tuple(edge.fact_id for edge in edges),
                source_ids=source_ids,
            ),
            support_records=tuple(
                HybridQuerySupportRecord(
                    kind="source_fact",
                    event_ids=(event.event_id,),
                    fact_ids=(edge.fact_id,),
                    source_ids=tuple(sorted(edge.source_ids)),
                )
                for edge in edges
                if edge.source_ids
            ),
            limitation=(
                ""
                if status == "ok"
                else "No formal graph edges match the bounded graph filter."
            ),
        )

    def _read_tmi_event_evidence_paths(
        self,
        *,
        event_id: str,
        limit: int,
    ) -> HybridQueryToolObservation:
        graph = self.store.graph_for_event(event_id)
        edges = graph.edges()
        controlled_edges = tuple(
            edge
            for edge in edges
            if edge.subject_iri == event_id
            and edge.object_kind == "iri"
            and _local_name(edge.predicate_iri) == "controlledNASelement"
        )
        evidence_paths: list[CorpusEventEvidencePath] = []

        for association in self.store.get_weather_context(event_id):
            for controlled_edge in controlled_edges:
                if controlled_edge.object_value != association.facility_id:
                    continue
                for report_edge in edges:
                    if (
                        report_edge.object_kind != "iri"
                        or _local_name(report_edge.predicate_iri)
                        != "forecastingAirport"
                        or report_edge.subject_iri
                        != _formal_report_iri(association.report_id)
                        or report_edge.object_value
                        != association.facility_id
                    ):
                        continue
                    path = _path(
                        event_id=event_id,
                        path_kind=(
                            "weather_context_at_controlled_facility"
                        ),
                        binding_id=association.association_id,
                        controlled_edge=controlled_edge,
                        related_edge=report_edge,
                        additional_source_id=association.source_id,
                    )
                    evidence_paths.append(
                        CorpusEventEvidencePath(
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
                            source_ids=path.source_ids,
                        )
                    )

        edge_by_fact_id = {edge.fact_id: edge for edge in edges}
        for observation in self.store.get_public_observations(event_id):
            observation_edges = tuple(
                edge_by_fact_id[fact_id]
                for fact_id in observation.fact_ids
                if fact_id in edge_by_fact_id
                and _local_name(edge_by_fact_id[fact_id].predicate_iri)
                == "hasFeatureOfInterest"
            )
            for controlled_edge in controlled_edges:
                for observation_edge in observation_edges:
                    if (
                        observation_edge.object_kind != "iri"
                        or controlled_edge.object_value
                        != observation_edge.object_value
                    ):
                        continue
                    path = _path(
                        event_id=event_id,
                        path_kind=(
                            "public_observation_at_controlled_facility"
                        ),
                        binding_id=observation.observation_id,
                        controlled_edge=controlled_edge,
                        related_edge=observation_edge,
                        additional_source_id=observation.source_id,
                    )
                    evidence_paths.append(
                        CorpusEventEvidencePath(
                            path=path,
                            support_kind="public_observation",
                            event_id=event_id,
                            fact_ids=(
                                controlled_edge.fact_id,
                                observation_edge.fact_id,
                            ),
                            observation_ids=(
                                observation.observation_id,
                            ),
                            source_ids=path.source_ids,
                        )
                    )

        selected = sorted(
            {
                evidence_path.path.path_id: evidence_path
                for evidence_path in evidence_paths
            }.values(),
            key=lambda item: item.path.path_id,
        )[:limit]
        paths = tuple(evidence_path.path for evidence_path in selected)
        support_records = tuple(
            evidence_path.support_record() for evidence_path in selected
        )
        fact_ids = tuple(
            sorted(
                {
                    fact_id
                    for support in support_records
                    for fact_id in support.fact_ids
                }
            )
        )
        association_ids = tuple(
            sorted(
                {
                    association_id
                    for support in support_records
                    for association_id in support.context_association_ids
                }
            )
        )
        observation_ids = tuple(
            sorted(
                {
                    observation_id
                    for support in support_records
                    for observation_id in support.observation_ids
                }
            )
        )
        source_ids = tuple(
            sorted(
                {
                    source_id
                    for path in paths
                    for source_id in path.source_ids
                }
            )
        )
        status: Literal["ok", "insufficient"] = (
            "ok" if paths else "insufficient"
        )
        return HybridQueryToolObservation(
            status=status,
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
            details=HybridQueryEvidence(
                event_ids=(event_id,),
                fact_ids=fact_ids,
                context_association_ids=association_ids,
                observation_ids=observation_ids,
                graph_path_ids=tuple(path.path_id for path in paths),
                source_ids=source_ids,
            ),
            support_records=support_records,
            graph_paths=paths,
            limitation=(
                ""
                if paths
                else (
                    "No source-bound Weather or public-observation path "
                    "shares this event's controlled facility."
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
        """Run exact filtering before corpus-bound Chroma recall."""

        reference_event_id = self._event_id(reference_event_id)
        effective_scope = candidate_scope or self.scope.candidate_scope
        if effective_scope != self.scope.candidate_scope:
            raise ValueError("candidate_scope is outside the query scope")
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
        index_dir = self.store.root / "tmi_event_index"
        if not (index_dir / TMI_EVENT_INDEX_MANIFEST).is_file():
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json({"matches": []}),
                limitation=(
                    "The corpus has no TMI-event index. "
                    "Build it with index-events."
                ),
            )
        try:
            index = ChromaTMIEventRetrievalIndex(self.store, index_dir)
        except ValueError as exc:
            return HybridQueryToolObservation(
                status="blocked",
                content=_json({"matches": []}),
                limitation=str(exc),
            )
        result = search_similar_tmi_events(self.store, index, query)
        matches = result.matches
        source_ids = tuple(
            sorted(match.advisory_source_id for match in matches)
        )
        return HybridQueryToolObservation(
            status=result.status,
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
            details=HybridQueryEvidence(
                event_ids=tuple(match.event_id for match in matches),
                source_ids=source_ids,
            ),
            support_records=tuple(
                HybridQuerySupportRecord(
                    kind="similarity",
                    event_ids=(match.event_id,),
                    source_ids=(match.advisory_source_id,),
                )
                for match in matches
            ),
            similarity_matches=matches,
            limitation=result.limitation,
        )


def build_hybrid_query_tools(
    gateway: HybridQueryGateway,
) -> list[BaseTool]:
    """Expose the fixed read-only HybridRAG registry to the model."""

    @tool("find_tmi_events", args_schema=FindTMIEventsInput)
    def find_tmi_events_tool(**kwargs: object) -> dict[str, object]:
        """Find TMI events using exact metadata filters and bounded paging."""

        return gateway.find_tmi_events(**kwargs).model_dump(mode="json")  # type: ignore[arg-type]

    @tool("read_tmi_event_facts", args_schema=EventInput)
    def read_tmi_event_facts_tool(event_id: str) -> dict[str, object]:
        """Read formal facts and declared-reason state for one event."""

        return gateway.read_tmi_event_facts(event_id=event_id).model_dump(mode="json")

    @tool("read_weather_context", args_schema=EventInput)
    def read_weather_context_tool(event_id: str) -> dict[str, object]:
        """Read retained TAF/METAR context without asserting causation."""

        return gateway.read_weather_context(event_id=event_id).model_dump(
            mode="json"
        )

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
        """Read bounded formal edges from one event-scoped graph."""

        return gateway.read_tmi_event_graph(
            event_id=event_id,
            view=view,
            entity_iri=entity_iri,
            direction=direction,
            predicate_iris=predicate_iris,
            limit=limit,
        ).model_dump(mode="json")

    @tool("find_similar_tmi_events", args_schema=SimilarTMIEventsInput)
    def find_similar_tmi_events_tool(**kwargs: object) -> dict[str, object]:
        """Find structurally similar TMI events through Chroma."""

        return gateway.find_similar_tmi_events(**kwargs).model_dump(mode="json")  # type: ignore[arg-type]

    return [
        find_tmi_events_tool,
        read_tmi_event_facts_tool,
        read_weather_context_tool,
        read_public_observations_tool,
        read_tmi_event_graph_tool,
        find_similar_tmi_events_tool,
    ]


__all__ = ["HybridQueryGateway", "build_hybrid_query_tools"]
