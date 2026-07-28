"""Deterministic Query Agent reads over a normalized decision-case corpus."""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from aviation_agentic_ai.agent_system.case_analysis import (
    run_case_analysis_agent,
    write_case_analysis_artifacts,
)
from aviation_agentic_ai.agent_system.case_analysis_tools import BoundQueryGateway
from aviation_agentic_ai.agent_system.case_retrieval_contracts import (
    CaseSimilarityQuery,
)
from aviation_agentic_ai.agent_system.case_retrieval_index import (
    CASE_INDEX_MANIFEST,
    ChromaCaseRetrievalIndex,
)
from aviation_agentic_ai.agent_system.case_retrieval_search import (
    find_similar_cases,
)
from aviation_agentic_ai.agent_system.contracts import (
    QueryToolOutcome,
    QueryToolTrace,
    SourceFamily,
    SourceSnapshot,
    SourceSnapshotRegistry,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.corpus_graph import (
    get_reconstructed_case_evidence_paths,
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
    RECONSTRUCTION_EVIDENCE_PATH_QUESTION,
    RECONSTRUCTED_CASE_QUESTION,
    REGISTERED_COMPETENCY_QUESTION,
    classify_registered_question,
)
from aviation_agentic_ai.agent_system.query_plan import (
    AnalysisIntent,
    compile_query_plan,
)
from aviation_agentic_ai.agent_system.decision_case_contracts import (
    ContractExecutionBinding,
)
from aviation_agentic_ai.agent_system.prompts import (
    DEFAULT_PROMPT_CATALOG,
    get_prompt_catalog,
)


CORPUS_CATALOG_QUESTION = "Which decision cases are recorded in this corpus?"

_RDF_TYPE_IRI = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
_ReasonStatus = Literal["formal", "profile_gap", "missing"]
_ModelFactory = Callable[[list[Any]], Any]


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
        RECONSTRUCTION_EVIDENCE_PATH_QUESTION,
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


def _query_iri(iri: str) -> str:
    namespaces = {
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf:",
        "https://data.nasa.gov/ontologies/atmonto/ATM#": "atm:",
        "https://data.nasa.gov/ontologies/atmonto/NAS#": "nas:",
        "https://data.nasa.gov/ontologies/atmonto/data#": "data:",
    }
    for namespace, prefix in namespaces.items():
        if iri.startswith(namespace):
            return f"{prefix}{iri[len(namespace):]}"
    return iri


class CorpusAnalysisStoreAdapter:
    """In-memory QueryGraphStore view backed only by verified corpus artifacts."""

    def __init__(self, store: CorpusQueryStore, *, event_id: str) -> None:
        case = store.get_case(event_id)
        if case is None:
            raise ValueError("event is outside the current corpus")
        self.corpus_store = store
        self.run_dir = store.root
        self.manifest = {"run_id": store.manifest.corpus_id}
        self.event_ids = [event_id]
        self.rows = [
            {
                "fact_id": fact.fact_id,
                "subject": fact.subject_iri,
                "predicate": _query_iri(fact.predicate_iri),
                "object": fact.object_value,
                "source_ids": list(fact.source_ids),
            }
            for fact in store.get_event_facts(event_id)
        ]
        bindings_by_source: dict[str, Any] = {}
        for binding in sorted(
            (
                row
                for row in store.source_bindings
                if row.case_id == case.case_id
            ),
            key=lambda row: (row.source_id, row.object_key),
        ):
            if binding.source_id in bindings_by_source:
                raise ValueError(
                    "corpus case has multiple source artifact versions for "
                    f"logical source: {binding.source_id}"
                )
            bindings_by_source[binding.source_id] = binding
        snapshots = []
        for source_id, binding in sorted(bindings_by_source.items()):
            object_path = store.root / "source_objects" / f"{binding.object_key}.txt"
            snapshots.append(
                SourceSnapshot(
                    source_id=source_id,
                    family=SourceFamily(binding.source_family),
                    source_url=binding.source_url,
                    content=object_path.read_text(encoding="utf-8"),
                    content_sha256=binding.content_sha256,
                    snapshot_timestamp=min(binding.snapshot_timestamps),
                )
            )
        self.source_snapshots = SourceSnapshotRegistry(
            snapshots=tuple(snapshots)
        )


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


def _graph_path_outcome(
    *,
    store: CorpusQueryStore,
    event_id: str | None,
) -> QueryToolOutcome:
    """Answer the one closed multi-hop reconstruction question."""

    if not event_id:
        return QueryToolOutcome(
            status="insufficient",
            answer="An event_id is required for a corpus graph question.",
        )
    case = store.get_case(event_id)
    if case is None:
        return QueryToolOutcome(
            status="insufficient",
            answer="The requested event is not present in this corpus.",
        )
    paths = get_reconstructed_case_evidence_paths(
        store.graph_for_event(event_id),
        case.case_iri,
        case.reconstruction_iri,
    )
    weather_count = sum(
        path.path_kind == "weather_member" for path in paths
    )
    observation_count = sum(
        path.path_kind == "active_public_observation" for path in paths
    )
    fact_ids = sorted(
        {
            edge.fact_id
            for path in paths
            for edge in path.edges
        }
    )
    source_ids = sorted(
        {
            source_id
            for path in paths
            for source_id in path.source_ids
        }
    )
    status: Literal["ok", "insufficient"] = (
        "ok" if weather_count and observation_count else "insufficient"
    )
    facility = (
        case.facility_ids[0].rsplit(":", 1)[-1]
        if case.facility_ids
        else "the facility"
    )
    answer = (
        f"The validated reconstruction contains {weather_count} Weather "
        f"reports and {observation_count} active-window BTS public "
        f"observations for {facility}. These records are co-members of the "
        "same retrospective decision-case reconstruction; the graph does not "
        "assert that Weather caused the traffic-management decision."
    )
    return QueryToolOutcome(
        status=status,
        answer=answer,
        match_count=1,
        retrieved_case_ids=[case.case_id],
        retrieved_fact_ids=fact_ids,
        retrieved_graph_paths=list(paths),
        source_ids=source_ids,
        tool_calls=[
            _trace(
                tool="get_reconstructed_case_evidence_paths",
                arguments={"event_id": event_id},
                case_ids=[case.case_id],
                fact_ids=fact_ids,
                source_ids=source_ids,
                status=status,
            )
        ],
    )


def _analysis_outcome(
    *,
    store: CorpusQueryStore,
    question: str,
    event_id: str | None,
    intent: AnalysisIntent,
    allow_live_model: bool,
    model_factory: _ModelFactory | None,
) -> QueryToolOutcome:
    """Run retained analysis over a corpus-backed in-memory graph view."""

    if not allow_live_model:
        return QueryToolOutcome(
            status="blocked",
            failure_reason=(
                "registered Decision Case Analysis requires --allow-live-model"
            ),
        )
    if model_factory is None:
        return QueryToolOutcome(
            status="blocked",
            failure_reason="authorized analysis has no model factory",
        )
    selected_event_id = event_id
    if selected_event_id is None:
        if len(store.event_ids) != 1:
            return QueryToolOutcome(
                status="insufficient",
                answer="Insufficient graph evidence.",
                failure_reason=(
                    "non-similarity analysis requires an explicit event_id "
                    "for a multi-event corpus"
                ),
            )
        selected_event_id = store.event_ids[0]
    try:
        adapter = CorpusAnalysisStoreAdapter(
            store,
            event_id=selected_event_id,
        )
    except ValueError as exc:
        return QueryToolOutcome(
            status="insufficient",
            answer="Insufficient graph evidence.",
            failure_reason=str(exc),
        )
    try:
        plan = compile_query_plan(
            run_dir=adapter.run_dir,
            question=question,
            event_id=selected_event_id,
            store=adapter,  # type: ignore[arg-type]
        )
    except ValueError as exc:
        return QueryToolOutcome(
            status="insufficient",
            answer="Insufficient graph evidence.",
            failure_reason=str(exc),
        )
    role = get_prompt_catalog(DEFAULT_PROMPT_CATALOG).role(
        "decision_case_analysis"
    )
    binding = ContractExecutionBinding(
        run_id=str(adapter.manifest["run_id"]),
        created_at=datetime.now(UTC),
        prompt_version=role.prompt_version,
    )
    gateway = BoundQueryGateway(
        plan=plan,
        store=adapter,  # type: ignore[arg-type]
    )
    task, bundle, outcome = run_case_analysis_agent(
        plan=plan,
        gateway=gateway,
        model_factory=model_factory,
        binding=binding,
    )
    artifact_dir = write_case_analysis_artifacts(
        run_dir=adapter.run_dir,
        task=task,
        bundle=bundle,
        outcome=outcome,
        query_store=adapter,
    )
    return outcome.model_copy(
        update={"analysis_artifact_dir": str(artifact_dir)}
    )


def _similarity_outcome(
    *,
    store: CorpusQueryStore,
    event_id: str | None,
    candidate_scope: Literal["archive", "prior"],
    event_type_iri: str | None,
    facility_id: str | None,
    reason_status: _ReasonStatus | None,
    reason_value: str | None,
    offset: int,
    limit: int,
) -> QueryToolOutcome:
    arguments: dict[str, object] = {
        "reference_event_id": event_id or "",
        "candidate_scope": candidate_scope,
        "event_type_iri": event_type_iri,
        "facility_id": facility_id,
        "reason_status": reason_status,
        "reason_value": reason_value,
        "offset": offset,
        "limit": limit,
    }
    if not event_id:
        return QueryToolOutcome(
            status="insufficient",
            answer=(
                "An event_id is required for historical case retrieval."
            ),
            tool_calls=[
                _trace(
                    tool="find_similar_cases",
                    arguments=arguments,
                    case_ids=[],
                    fact_ids=[],
                    source_ids=[],
                    status="insufficient",
                )
            ],
        )
    if store.get_case(event_id) is None:
        return QueryToolOutcome(
            status="insufficient",
            answer="The reference event is not present in this corpus.",
            tool_calls=[
                _trace(
                    tool="find_similar_cases",
                    arguments=arguments,
                    case_ids=[],
                    fact_ids=[],
                    source_ids=[],
                    status="insufficient",
                )
            ],
        )

    query = CaseSimilarityQuery(
        reference_event_id=event_id,
        candidate_scope=candidate_scope,
        event_type_iri=event_type_iri,
        facility_id=facility_id,
        reason_status=reason_status,
        reason_value=reason_value,
        offset=offset,
        limit=limit,
    )
    index_dir = store.root / "case_index"
    if not (index_dir / CASE_INDEX_MANIFEST).is_file():
        return QueryToolOutcome(
            status="insufficient",
            answer=(
                "The corpus has no case index. Build it with index-cases."
            ),
            retrieved_case_ids=[],
            tool_calls=[
                _trace(
                    tool="find_similar_cases",
                    arguments=query.model_dump(mode="json"),
                    case_ids=[],
                    fact_ids=[],
                    source_ids=[],
                    status="insufficient",
                )
            ],
        )
    try:
        index = ChromaCaseRetrievalIndex(store, index_dir)
    except ValueError as exc:
        return QueryToolOutcome(
            status="blocked",
            failure_reason=str(exc),
            tool_calls=[
                _trace(
                    tool="find_similar_cases",
                    arguments=query.model_dump(mode="json"),
                    case_ids=[],
                    fact_ids=[],
                    source_ids=[],
                    status="blocked",
                )
            ],
        )
    result = find_similar_cases(store, index, query)
    matches = list(result.matches)
    case_ids = [match.case_id for match in matches]
    source_ids = [match.advisory_source_id for match in matches]
    if result.status == "ok":
        first = matches[0]
        answer = (
            "The closest published decision record in the "
            f"{query.candidate_scope} candidate set is "
            f"{first.advisory_source_id} with cosine similarity "
            f"{first.score:.6f}. Similarity describes record structure "
            "only; it is not a recommendation, causal explanation, or "
            "assessment that the historical decision was effective."
        )
    else:
        answer = result.limitation if result.status == "insufficient" else ""
    return QueryToolOutcome(
        status=result.status,
        answer=answer,
        match_count=result.candidate_count,
        retrieved_case_ids=case_ids,
        source_ids=source_ids,
        similarity_matches=matches,
        tool_calls=[
            _trace(
                tool="find_similar_cases",
                arguments=query.model_dump(mode="json"),
                case_ids=case_ids,
                fact_ids=[],
                source_ids=source_ids,
                status=result.status,
            )
        ],
        failure_reason=(
            result.limitation if result.status == "blocked" else ""
        ),
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
    candidate_scope: Literal["archive", "prior"] = "archive",
    offset: int = 0,
    limit: int = 20,
    allow_live_model: bool = False,
    model_factory: _ModelFactory | None = None,
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
    intent = classify_registered_question(question)
    if intent is AnalysisIntent.HISTORICAL_SIMILARITY:
        return _similarity_outcome(
            store=store,
            event_id=event_id,
            candidate_scope=candidate_scope,
            event_type_iri=event_type_iri,
            facility_id=facility_id,
            reason_status=reason_status,
            reason_value=reason_value,
            offset=offset,
            limit=limit,
        )
    if isinstance(intent, AnalysisIntent):
        return _analysis_outcome(
            store=store,
            question=question,
            event_id=event_id,
            intent=intent,
            allow_live_model=allow_live_model,
            model_factory=model_factory,
        )
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
    if normalized == _normalize_question(
        RECONSTRUCTION_EVIDENCE_PATH_QUESTION
    ):
        return _graph_path_outcome(store=store, event_id=event_id)
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
