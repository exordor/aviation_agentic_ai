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
    MEASURE_QUESTION,
    OPERATIONAL_PERIOD_QUESTION,
    PROVENANCE_QUESTION,
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
    facts = store.get_case_facts(event_id)
    by_predicate = _facts_by_predicate(facts)

    if normalized == _normalize_question(DECLARED_REASON_QUESTION):
        if case.reason_status == "profile_gap":
            return _insufficient_case_outcome(
                case=case,
                answer=(
                    f"The corpus catalog retains {case.reason_value} as "
                    "profile-gap metadata. Exact profile-gap evidence remains "
                    "in the original run bundle."
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
    return _event_outcome(
        store=store,
        question=question,
        event_id=event_id,
    )
