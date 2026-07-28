"""Deterministic Query Agent reads over a normalized decision-case corpus."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Literal

from aviation_agentic_ai.agent_system.contracts import (
    QueryToolOutcome,
    QueryToolTrace,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.corpus_store import (
    CorpusCase,
    CorpusCaseQuery,
    CorpusQueryStore,
)
from aviation_agentic_ai.agent_system.query_tool_graph import (
    CONTROLLED_FACILITY_QUESTION,
    DECLARED_REASON_QUESTION,
    FORECAST_CONTEXT_QUESTION,
    MEASURE_QUESTION,
    OBSERVED_WEATHER_CONTEXT_QUESTION,
    OPERATIONAL_PERIOD_QUESTION,
    PUBLIC_OUTCOME_QUESTION,
    PROVENANCE_QUESTION,
    RECONSTRUCTED_CASE_QUESTION,
    REGISTERED_COMPETENCY_QUESTION,
)


CORPUS_CATALOG_QUESTION = "Which decision cases are recorded in this corpus?"

_RDF_TYPE_IRI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
_ReasonStatus = Literal["formal", "profile_gap", "missing"]


def _normalize_question(question: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", question.lower()))


_EVENT_QUESTIONS = {
    _normalize_question(question): question
    for question in (
        REGISTERED_COMPETENCY_QUESTION,
        MEASURE_QUESTION,
        CONTROLLED_FACILITY_QUESTION,
        OPERATIONAL_PERIOD_QUESTION,
        DECLARED_REASON_QUESTION,
        PROVENANCE_QUESTION,
        FORECAST_CONTEXT_QUESTION,
        OBSERVED_WEATHER_CONTEXT_QUESTION,
        PUBLIC_OUTCOME_QUESTION,
        RECONSTRUCTED_CASE_QUESTION,
    )
}


def _local_name(iri: str) -> str:
    return iri.rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def _facts_by_predicate(
    facts: tuple[ValidatedFact, ...],
) -> dict[str, list[ValidatedFact]]:
    rows: dict[str, list[ValidatedFact]] = {}
    for fact in facts:
        key = (
            "rdf:type"
            if fact.predicate_iri == _RDF_TYPE_IRI
            else _local_name(fact.predicate_iri)
        )
        rows.setdefault(key, []).append(fact)
    return rows


def _trace(
    *,
    tool: str,
    arguments: dict[str, object],
    case_ids: list[str],
    fact_ids: list[str],
    source_ids: list[str],
    status: Literal["ok", "insufficient", "blocked"],
) -> QueryToolTrace:
    return QueryToolTrace(
        tool_call_id=f"corpus:{tool}:1",
        tool=tool,
        arguments=arguments,
        result_refs=[*case_ids, *fact_ids],
        source_ids=source_ids,
        status=status,
    )


def _catalog_outcome(
    *,
    store: CorpusQueryStore,
    query: CorpusCaseQuery,
) -> QueryToolOutcome:
    page = store.find_cases(query)
    case_ids = [case.case_id for case in page.cases]
    source_ids = sorted(
        {
            source_id
            for case in page.cases
            for source_id in case.source_ids
        }
    )
    status = "ok" if page.total_matches else "insufficient"
    answer = (
        f"The corpus contains {page.total_matches} matching decision cases; "
        f"this page returns {len(page.cases)}."
        if page.total_matches
        else "No decision cases match the supplied corpus filters."
    )
    return QueryToolOutcome(
        status=status,
        answer=answer,
        match_count=page.total_matches,
        retrieved_case_ids=case_ids,
        source_ids=source_ids,
        tool_calls=[
            _trace(
                tool="find_corpus_cases",
                arguments=query.model_dump(mode="json"),
                case_ids=case_ids,
                fact_ids=[],
                source_ids=source_ids,
                status=status,
            )
        ],
    )


def _insufficient_case_outcome(
    *,
    case: CorpusCase,
    answer: str,
) -> QueryToolOutcome:
    source_ids = sorted(case.source_ids)
    return QueryToolOutcome(
        status="insufficient",
        answer=answer,
        match_count=1,
        retrieved_case_ids=[case.case_id],
        source_ids=source_ids,
        tool_calls=[
            _trace(
                tool="get_corpus_case_record",
                arguments={"event_id": case.event_id},
                case_ids=[case.case_id],
                fact_ids=[],
                source_ids=source_ids,
                status="insufficient",
            )
        ],
    )


def _event_outcome(
    *,
    store: CorpusQueryStore,
    question: str,
    event_id: str | None,
) -> QueryToolOutcome:
    if not event_id:
        return QueryToolOutcome(
            status="insufficient",
            answer="An event_id is required for a corpus record question.",
        )
    case = store.get_case(event_id)
    if case is None:
        return QueryToolOutcome(
            status="insufficient",
            answer="The requested event is not present in this corpus.",
        )
    normalized = _normalize_question(question)
    facts = store.get_event_facts(event_id)
    by_predicate = _facts_by_predicate(facts)

    if normalized == _normalize_question(DECLARED_REASON_QUESTION):
        if case.reason_status == "profile_gap":
            gap = next(
                (
                    row
                    for row in store.profile_gaps
                    if row.event_id == event_id
                    and row.field == "impacting_condition"
                ),
                None,
            )
            return _insufficient_case_outcome(
                case=case,
                answer=(
                    f"The corpus catalog retains {case.reason_value} as "
                    "profile-gap metadata. "
                    + (f"Source wording: {gap.evidence_text}" if gap else "")
                ),
            )
        if case.reason_status == "missing":
            return _insufficient_case_outcome(
                case=case,
                answer="No declared reason is recorded for this corpus case.",
            )
        selected = by_predicate.get("impactingCondition", [])
    elif normalized == _normalize_question(MEASURE_QUESTION):
        selected = by_predicate.get("rdf:type", [])
    elif normalized == _normalize_question(CONTROLLED_FACILITY_QUESTION):
        selected = by_predicate.get("controlledNASelement", [])
    elif normalized == _normalize_question(OPERATIONAL_PERIOD_QUESTION):
        selected = [
            *by_predicate.get("effectiveStartTime", []),
            *by_predicate.get("effectiveEndTime", []),
        ]
    elif normalized == _normalize_question(PROVENANCE_QUESTION):
        source_ids = sorted(case.source_ids)
        return QueryToolOutcome(
            status="ok",
            answer=(
                f"Source {case.advisory_source_id} supports this corpus case."
            ),
            match_count=1,
            retrieved_case_ids=[case.case_id],
            source_ids=source_ids,
            tool_calls=[
                _trace(
                    tool="get_corpus_case_record",
                    arguments={"event_id": event_id},
                    case_ids=[case.case_id],
                    fact_ids=[],
                    source_ids=source_ids,
                    status="ok",
                )
            ],
        )
    else:
        selected = [
            *by_predicate.get("rdf:type", []),
            *by_predicate.get("controlledNASelement", []),
            *by_predicate.get("effectiveStartTime", []),
            *by_predicate.get("effectiveEndTime", []),
        ]

    required_count = (
        4
        if normalized == _normalize_question(REGISTERED_COMPETENCY_QUESTION)
        else 2
        if normalized == _normalize_question(OPERATIONAL_PERIOD_QUESTION)
        else 1
    )
    if len(selected) != required_count:
        return _insufficient_case_outcome(
            case=case,
            answer="The corpus case does not contain the required formal facts.",
        )

    fact_ids = sorted(fact.fact_id for fact in selected)
    source_ids = sorted(
        {
            source_id
            for fact in selected
            for source_id in fact.source_ids
        }
    )
    if normalized == _normalize_question(DECLARED_REASON_QUESTION):
        fact = selected[0]
        evidence = (
            f" Source wording: {fact.evidence_texts[0]}."
            if fact.evidence_texts
            else ""
        )
        answer = (
            f"The advisory records {fact.object_value} as its impacting "
            f"condition.{evidence}"
        )
    elif normalized == _normalize_question(MEASURE_QUESTION):
        answer = (
            "The published traffic-management measure is "
            f"{_local_name(selected[0].object_value)}."
        )
    elif normalized == _normalize_question(CONTROLLED_FACILITY_QUESTION):
        answer = f"The controlled facility is {selected[0].object_value}."
    elif normalized == _normalize_question(OPERATIONAL_PERIOD_QUESTION):
        values = {
            _local_name(fact.predicate_iri): fact.object_value
            for fact in selected
        }
        answer = (
            "The TMI operational period is "
            f"{values['effectiveStartTime']} to {values['effectiveEndTime']}."
        )
    else:
        values = {
            (
                "rdf:type"
                if fact.predicate_iri == _RDF_TYPE_IRI
                else _local_name(fact.predicate_iri)
            ): fact.object_value
            for fact in selected
        }
        answer = (
            f"The corpus records {_local_name(values['rdf:type'])} controlling "
            f"{values['controlledNASelement']} from "
            f"{values['effectiveStartTime']} to {values['effectiveEndTime']}."
        )
    return QueryToolOutcome(
        status="ok",
        answer=answer,
        match_count=1,
        retrieved_case_ids=[case.case_id],
        retrieved_fact_ids=fact_ids,
        source_ids=source_ids,
        tool_calls=[
            _trace(
                tool="get_corpus_case_record",
                arguments={"event_id": event_id},
                case_ids=[case.case_id],
                fact_ids=fact_ids,
                source_ids=source_ids,
                status="ok",
            )
        ],
    )


def _context_outcome(
    *, store: CorpusQueryStore, question: str, event_id: str | None
) -> QueryToolOutcome:
    """Answer the three bounded context reads from corpus-owned artifacts."""

    if not event_id or store.get_case(event_id) is None:
        return QueryToolOutcome(
            status="insufficient",
            answer="The requested event is not present in this corpus.",
        )
    case = store.get_case(event_id)
    assert case is not None
    normalized = _normalize_question(question)
    associations = list(store.get_decision_context(event_id))
    facts = list(store.get_event_facts(event_id))
    if normalized == _normalize_question(FORECAST_CONTEXT_QUESTION):
        relations = {"latest_forecast_known_at_issue"}
    elif normalized == _normalize_question(OBSERVED_WEATHER_CONTEXT_QUESTION):
        relations = {
            "latest_observation_at_or_before_issue",
            "observation_during_operation",
        }
    else:
        relations = set()
    if relations:
        selected = [row for row in associations if row.relation_type in relations]
        report_ids = {row.report_id for row in selected}
        report_facts = [
            fact
            for fact in facts
            if fact.subject_iri in report_ids
            or fact.subject_iri.rsplit(":", 1)[-1]
            in {report_id.rsplit(":", 1)[-1] for report_id in report_ids}
        ]
        if not selected or not report_facts:
            return _insufficient_case_outcome(
                case=case,
                answer="The corpus case has no matching formal weather context.",
            )
        wording = "; ".join(
            sorted(
                {
                    evidence
                    for fact in report_facts
                    for evidence in fact.evidence_texts
                }
            )
        )
        return QueryToolOutcome(
            status="ok",
            answer=f"The corpus retains {wording} as non-causal context.",
            match_count=1,
            retrieved_case_ids=[case.case_id],
            retrieved_fact_ids=sorted(fact.fact_id for fact in report_facts),
            retrieved_context_association_ids=sorted(
                row.association_id for row in selected
            ),
            source_ids=sorted({row.source_id for row in selected}),
            tool_calls=[
                _trace(
                    tool="get_decision_context",
                    arguments={"event_id": event_id},
                    case_ids=[case.case_id],
                    fact_ids=sorted(fact.fact_id for fact in report_facts),
                    source_ids=sorted({row.source_id for row in selected}),
                    status="ok",
                )
            ],
        )
    observations = list(store.get_outcome_observations(event_id))
    active = {
        row.metric_key: row.value
        for row in observations
        if row.phase == "active"
        and row.metric_key
        in {
            "scheduled_arrival_count",
            "completed_arrival_count",
            "cancelled_count",
            "diverted_count",
        }
    }
    required = {
        "scheduled_arrival_count",
        "completed_arrival_count",
        "cancelled_count",
        "diverted_count",
    }
    if normalized == _normalize_question(PUBLIC_OUTCOME_QUESTION):
        if set(active) != required or any(not isinstance(active[key], int) for key in required):
            return _insufficient_case_outcome(
                case=case,
                answer="The corpus case has no complete BTS public observations.",
            )
        facility = case.facility_ids[0].rsplit(":", 1)[-1] if case.facility_ids else "the facility"
        return QueryToolOutcome(
            status="ok",
            answer=(
                "During the active interval, BTS reported "
                f"{active['scheduled_arrival_count']} scheduled arrivals, "
                f"{active['completed_arrival_count']} completed arrivals, "
                f"{active['cancelled_count']} cancellations, and "
                f"{active['diverted_count']} diversions for {facility} within the tracked BTS reporting scope."
            ),
            match_count=1,
            retrieved_case_ids=[case.case_id],
            retrieved_observation_ids=sorted(row.observation_id for row in observations),
            source_ids=sorted({row.source_id for row in observations}),
            tool_calls=[
                _trace(
                    tool="get_outcome_observations",
                    arguments={"event_id": event_id, "phases": ["baseline", "active", "recovery"]},
                    case_ids=[case.case_id], fact_ids=[],
                    source_ids=sorted({row.source_id for row in observations}), status="ok",
                )
            ],
        )
    core = [
        fact
        for fact in facts
        if _local_name(fact.predicate_iri)
        in {"controlledNASelement", "effectiveStartTime", "effectiveEndTime"}
        or fact.predicate_iri == _RDF_TYPE_IRI
    ]
    if len(core) < 4 or not associations or set(active) != required:
        return _insufficient_case_outcome(
            case=case,
            answer="The corpus case lacks the bounded context required for reconstruction.",
        )
    return QueryToolOutcome(
        status="ok",
        answer=(
            "The corpus reconstructs the formal decision record with retained "
            "non-causal weather context and BTS public observations."
        ),
        match_count=1,
        retrieved_case_ids=[case.case_id],
        retrieved_fact_ids=sorted(fact.fact_id for fact in core),
        retrieved_context_association_ids=sorted(row.association_id for row in associations),
        retrieved_observation_ids=sorted(row.observation_id for row in observations),
        source_ids=sorted(
            {row.source_id for row in associations}
            | {row.source_id for row in observations}
            | {source_id for fact in core for source_id in fact.source_ids}
        ),
        tool_calls=[
            _trace(
                tool="reconstruct_corpus_case",
                arguments={"event_id": event_id},
                case_ids=[case.case_id],
                fact_ids=sorted(fact.fact_id for fact in core),
                source_ids=sorted(
                    {row.source_id for row in associations}
                    | {row.source_id for row in observations}
                    | {source_id for fact in core for source_id in fact.source_ids}
                ),
                status="ok",
            )
        ],
    )


def answer_corpus_question(
    *,
    corpus_dir: str | Path,
    question: str,
    event_id: str | None = None,
    event_type_iri: str | None = None,
    facility_id: str | None = None,
    reason_status: _ReasonStatus | None = None,
    reason_value: str | None = None,
    offset: int = 0,
    limit: int = 20,
) -> QueryToolOutcome:
    """Answer one registered corpus question without constructing a model."""

    try:
        store = CorpusQueryStore(corpus_dir)
    except ValueError as exc:
        return QueryToolOutcome(
            status="blocked",
            answer="",
            failure_reason=str(exc),
        )
    normalized = _normalize_question(question)
    if normalized == _normalize_question(CORPUS_CATALOG_QUESTION):
        return _catalog_outcome(
            store=store,
            query=CorpusCaseQuery(
                event_type_iri=event_type_iri,
                facility_id=facility_id,
                reason_status=reason_status,
                reason_value=reason_value,
                offset=offset,
                limit=limit,
            ),
        )
    if normalized not in _EVENT_QUESTIONS:
        return QueryToolOutcome(
            status="insufficient",
            answer="Question is outside the registered corpus capability.",
        )
    if normalized in {
        _normalize_question(FORECAST_CONTEXT_QUESTION),
        _normalize_question(OBSERVED_WEATHER_CONTEXT_QUESTION),
        _normalize_question(PUBLIC_OUTCOME_QUESTION),
        _normalize_question(RECONSTRUCTED_CASE_QUESTION),
    }:
        return _context_outcome(store=store, question=question, event_id=event_id)
    return _event_outcome(
        store=store,
        question=question,
        event_id=event_id,
    )
