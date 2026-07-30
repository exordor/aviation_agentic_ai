"""Read-only Corpus, graph, and Chroma tools for the Hybrid Query Agent."""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Literal

from langchain_core.tools import BaseTool, tool
from pydantic import Field

from aviation_agentic_ai.agent_system.case_retrieval_contracts import (
    CaseSimilarityQuery,
)
from aviation_agentic_ai.agent_system.case_retrieval_index import (
    CASE_INDEX_MANIFEST,
    ChromaCaseRetrievalIndex,
)
from aviation_agentic_ai.agent_system.case_retrieval_search import (
    find_similar_cases as search_similar_cases,
)
from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryEvidence,
    HybridQueryScope,
    HybridQuerySupportRecord,
    HybridQueryToolObservation,
    StrictModel,
)
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusCase,
    CorpusCaseQuery,
    CorpusQueryStore,
)


ReasonStatus = Literal["formal", "profile_gap", "missing"]
ObservationPhase = Literal["baseline", "active", "recovery"]


class FindCasesInput(StrictModel):
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


class CaseGraphInput(EventInput):
    entity_iri: str | None = Field(default=None, min_length=1)
    direction: Literal["out", "in"] = "out"
    predicate_iris: tuple[str, ...] = ()
    limit: int = Field(default=50, ge=1, le=100)


class SimilarCasesInput(StrictModel):
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
        case = self.store.get_case(event_id)
        if case is not None and not self._case_matches_scope(case):
            raise ValueError("event_id is outside the query scope")
        return event_id

    def _case_matches_scope(self, case: CorpusCase) -> bool:
        return all(
            (
                self.scope.event_type_iri is None
                or self.scope.event_type_iri in case.event_type_iris,
                self.scope.facility_id is None
                or self.scope.facility_id in case.facility_ids,
                self.scope.reason_status is None
                or self.scope.reason_status == case.reason_status,
                self.scope.reason_value is None
                or self.scope.reason_value == case.reason_value,
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

    def find_cases(
        self,
        *,
        event_type_iri: str | None = None,
        facility_id: str | None = None,
        reason_status: ReasonStatus | None = None,
        reason_value: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> HybridQueryToolObservation:
        """Find corpus cases with exact filters and bounded paging."""

        if self.scope.event_id is not None:
            case = self.store.get_case(self.scope.event_id)
            cases = (
                ()
                if case is None or not self._case_matches_scope(case)
                else (case,)
            )
            total_matches = len(cases)
            page_offset = 0
            page_limit = 1
        else:
            page = self.store.find_cases(
                CorpusCaseQuery(
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
            cases = page.cases
            total_matches = page.total_matches
            page_offset = page.offset
            page_limit = page.limit
        case_rows = [
            {
                "case_id": case.case_id,
                "event_id": case.event_id,
                "advisory_source_id": case.advisory_source_id,
                "event_type_iris": case.event_type_iris,
                "facility_ids": case.facility_ids,
                "operational_start": case.operational_start,
                "operational_end": case.operational_end,
                "reason_status": case.reason_status,
                "reason_value": case.reason_value,
            }
            for case in cases
        ]
        status: Literal["ok", "insufficient"] = (
            "ok" if cases else "insufficient"
        )
        source_ids = tuple(
            sorted({source_id for case in cases for source_id in case.source_ids})
        )
        return HybridQueryToolObservation(
            status=status,
            content=_json(
                {
                    "total_matches": total_matches,
                    "offset": page_offset,
                    "limit": page_limit,
                    "cases": case_rows,
                }
            ),
            details=HybridQueryEvidence(
                case_ids=tuple(case.case_id for case in cases),
                source_ids=source_ids,
            ),
            support_records=tuple(
                HybridQuerySupportRecord(
                    kind="source_fact",
                    case_ids=(case.case_id,),
                    source_ids=(case.advisory_source_id,),
                )
                for case in cases
            ),
            limitation=(
                "" if cases else "No corpus cases match the bounded filters."
            ),
        )

    def read_case_facts(self, *, event_id: str) -> HybridQueryToolObservation:
        """Read formal facts and declared-reason state for one event."""

        event_id = self._event_id(event_id)
        case = self.store.get_case(event_id)
        if case is None:
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
                    *case.source_ids,
                    *(source_id for fact in facts for source_id in fact.source_ids),
                    *(gap.source_id for gap in gaps),
                }
            )
        )
        return HybridQueryToolObservation(
            status="ok",
            content=_json(
                {
                    "case": {
                        "case_id": case.case_id,
                        "event_id": case.event_id,
                        "advisory_source_id": case.advisory_source_id,
                        "event_type_iris": case.event_type_iris,
                        "facility_ids": case.facility_ids,
                        "operational_start": case.operational_start,
                        "operational_end": case.operational_end,
                        "reason_status": case.reason_status,
                        "reason_value": case.reason_value,
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
                case_ids=(case.case_id,),
                fact_ids=tuple(fact.fact_id for fact in facts),
                profile_gap_ids=tuple(gap.profile_gap_id for gap in gaps),
                source_ids=source_ids,
            ),
            support_records=(
                HybridQuerySupportRecord(
                    kind="source_fact",
                    case_ids=(case.case_id,),
                    source_ids=(case.advisory_source_id,),
                ),
                *(
                    HybridQuerySupportRecord(
                        kind="source_fact",
                        case_ids=(case.case_id,),
                        fact_ids=(fact.fact_id,),
                        source_ids=tuple(sorted(fact.source_ids)),
                    )
                    for fact in facts
                    if fact.source_ids
                ),
                *(
                    HybridQuerySupportRecord(
                        kind="source_fact",
                        case_ids=(case.case_id,),
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
        case = self.store.get_case(event_id)
        if case is None:
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json({"event_id": event_id, "associations": []}),
                limitation="The requested event is not present in this corpus.",
            )
        associations = self.store.get_decision_context(event_id)
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
                case_ids=(case.case_id,),
                fact_ids=tuple(fact.fact_id for fact in facts),
                context_association_ids=tuple(
                    row.association_id for row in associations
                ),
                source_ids=source_ids,
            ),
            support_records=tuple(
                HybridQuerySupportRecord(
                    kind="non_causal_context",
                    case_ids=(case.case_id,),
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
                else "No retained Weather context is available for this case."
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
        case = self.store.get_case(event_id)
        observations = (
            ()
            if case is None
            else self.store.get_outcome_observations(event_id, phases)
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
                case_ids=(() if case is None else (case.case_id,)),
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
                    case_ids=(() if case is None else (case.case_id,)),
                    observation_ids=(row.observation_id,),
                    source_ids=(row.source_id,),
                )
                for row in observations
            ),
            limitation=(
                ""
                if status == "ok"
                else "No BTS public observations are available for this case."
            ),
        )

    def read_case_graph(
        self,
        *,
        event_id: str,
        entity_iri: str | None = None,
        direction: Literal["out", "in"] = "out",
        predicate_iris: tuple[str, ...] = (),
        limit: int = 50,
    ) -> HybridQueryToolObservation:
        """Read formal graph edges from one case-scoped graph view."""

        event_id = self._event_id(event_id)
        case = self.store.get_case(event_id)
        if case is None:
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json({"event_id": event_id, "edges": []}),
                limitation="The requested event is not present in this corpus.",
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
                    "case_id": case.case_id,
                    "edges": [
                        edge.model_dump(mode="json") for edge in edges
                    ],
                }
            ),
            details=HybridQueryEvidence(
                case_ids=(case.case_id,),
                fact_ids=tuple(edge.fact_id for edge in edges),
                source_ids=source_ids,
            ),
            support_records=tuple(
                HybridQuerySupportRecord(
                    kind="source_fact",
                    case_ids=(case.case_id,),
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

    def find_similar_cases(
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
        query = CaseSimilarityQuery(
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
        index_dir = self.store.root / "case_index"
        if not (index_dir / CASE_INDEX_MANIFEST).is_file():
            return HybridQueryToolObservation(
                status="insufficient",
                content=_json({"matches": []}),
                limitation="The corpus has no case index. Build it with index-cases.",
            )
        try:
            index = ChromaCaseRetrievalIndex(self.store, index_dir)
        except ValueError as exc:
            return HybridQueryToolObservation(
                status="blocked",
                content=_json({"matches": []}),
                limitation=str(exc),
            )
        result = search_similar_cases(self.store, index, query)
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
                case_ids=tuple(match.case_id for match in matches),
                source_ids=source_ids,
            ),
            support_records=tuple(
                HybridQuerySupportRecord(
                    kind="similarity",
                    case_ids=(match.case_id,),
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

    @tool("find_cases", args_schema=FindCasesInput)
    def find_cases_tool(**kwargs: object) -> dict[str, object]:
        """Find decision cases using exact metadata filters and bounded paging."""

        return gateway.find_cases(**kwargs).model_dump(mode="json")  # type: ignore[arg-type]

    @tool("read_case_facts", args_schema=EventInput)
    def read_case_facts_tool(event_id: str) -> dict[str, object]:
        """Read formal facts and declared-reason state for one event."""

        return gateway.read_case_facts(event_id=event_id).model_dump(mode="json")

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

    @tool("read_case_graph", args_schema=CaseGraphInput)
    def read_case_graph_tool(
        event_id: str,
        entity_iri: str | None = None,
        direction: Literal["out", "in"] = "out",
        predicate_iris: tuple[str, ...] = (),
        limit: int = 50,
    ) -> dict[str, object]:
        """Read bounded formal edges from one case-scoped graph."""

        return gateway.read_case_graph(
            event_id=event_id,
            entity_iri=entity_iri,
            direction=direction,
            predicate_iris=predicate_iris,
            limit=limit,
        ).model_dump(mode="json")

    @tool("find_similar_cases", args_schema=SimilarCasesInput)
    def find_similar_cases_tool(**kwargs: object) -> dict[str, object]:
        """Find structurally similar decision records through Chroma."""

        return gateway.find_similar_cases(**kwargs).model_dump(mode="json")  # type: ignore[arg-type]

    return [
        find_cases_tool,
        read_case_facts_tool,
        read_weather_context_tool,
        read_public_observations_tool,
        read_case_graph_tool,
        find_similar_cases_tool,
    ]


__all__ = ["HybridQueryGateway", "build_hybrid_query_tools"]
