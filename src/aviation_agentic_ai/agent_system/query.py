"""Query Agent graph-tools and answer composition (design §12).

The Query Agent answers from the MATERIALIZED knowledge graph only. It never
reads raw advisory documents and never falls back to model memory. Graph-tool
results (``graph_search`` / ``graph_neighbors`` / ``get_provenance``) are
deterministic reads over the run's ``kg.jsonl``; the Agent then composes a
natural-language answer and lists the supporting source IDs.

The Agent receives controlled ontology labels (design §12.2) for the classes
and properties referenced by the materialized facts, derived from the frozen
Schema Guide. This pins the natural-language rendering (e.g. Ground Stop vs
Ground Delay Program) to the ontology rather than to model memory.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.agents import (
    INSUFFICIENT_EVIDENCE_ANSWER,
    QueryGraphEvidence,
    run_query_agent,
)
from aviation_agentic_ai.agent_system.contracts import AgentTask, ModelCallRecord
from aviation_agentic_ai.agent_system.schema_guide import SchemaGuide, load_schema_guide

ModelInvoker = Callable[[str, dict[str, Any]], ModelCallRecord]


def load_materialized_triples(run_dir: str | Path) -> list[dict[str, Any]]:
    """Read the materialized ``kg.jsonl`` for a run (design §12.2 graph store)."""

    path = Path(run_dir) / "kg.jsonl"
    if not path.exists():
        return []
    triples: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        triples.append(json.loads(line))
    return triples


# Schema-predicate phrases the bounded deterministic intent layer recognizes
# (plan §13 T2). Each concept role maps to the schema predicates whose facts
# answer that role. The intent layer is bounded to the registered competency
# question's concepts; it is not a general retrieval system.
_INTENT_ROLES: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    # traffic-management measure -> rdf:type (the event type assertion).
    (("traffic management measure", "traffic-management measure"), ("rdf:type",)),
    # controlled airport -> atm:controlledNASelement.
    (("controlled airport", "controlled facility"),
     ("atm:controlledNASelement",)),
    # effective time -> atm:effectiveStartTime / atm:effectiveEndTime.
    (("effective time", "effective period"),
     ("atm:effectiveStartTime", "atm:effectiveEndTime", "atm:effectiveStart",
      "atm:effectiveEnd")),
)

# Generic words that occur inside ontology predicates or canonical identifiers
# but do not, by themselves, establish that a question is about the registered
# competency question. Keeping them out of keyword fallback prevents questions
# about runway properties, wall-clock time, or arbitrary airports from matching
# internal strings such as ``facility:airport`` or ``effectiveStartTime``.
_NON_DISTINCTIVE_KEYWORDS = {
    "airport",
    "facility",
    "measure",
    "period",
    "start",
    "end",
    "time",
}


def competency_intent(question: str) -> set[str] | None:
    """Bounded deterministic intent for the registered competency question.

    Plan §13 T2: map the supported concepts to the existing schema predicates.
    Returns the set of predicate substrings to retrieve, or ``None`` when the
    question carries no recognized concept role (the caller then falls back to
    keyword retrieval). This is one bounded intent layer for the registered
    question — not vector search, generic RAG, or a translation call.
    """

    lowered = question.lower()
    predicates: set[str] = set()
    matched_any_role = False
    for phrases, preds in _INTENT_ROLES:
        if any(phrase in lowered for phrase in phrases):
            matched_any_role = True
            predicates.update(preds)
    if not matched_any_role:
        return None
    return predicates


def graph_search(triples: list[dict[str, Any]], question: str) -> list[dict[str, Any]]:
    """``graph_search`` tool: select triples whose predicate/object/text matches.

    Deterministic keyword match over the materialized graph (no vector store).

    Plan §6.3: there is NO whole-graph fallback. When no triple matches the
    question's keywords, the result is empty — the caller then answers
    ``Insufficient graph evidence.`` with zero provider calls. An empty question
    yields no matches rather than the whole graph.
    """

    words = re.findall(r"[a-z0-9_-]+", question.lower())
    needles = [
        word
        for word in words
        if len(word) > 2 and word not in _NON_DISTINCTIVE_KEYWORDS
    ]
    if not needles:
        return []
    matches: list[dict[str, Any]] = []
    for t in triples:
        haystack = " ".join(
            str(t.get(k, "")) for k in ("subject", "predicate", "object", "source_document")
        ).lower()
        if any(n in haystack for n in needles):
            matches.append(t)
    return matches  # no fallback: no match -> empty


def graph_search_by_predicates(
    triples: list[dict[str, Any]], predicate_substrings: set[str]
) -> list[dict[str, Any]]:
    """Select triples whose predicate matches any of the given substrings.

    Used by the bounded competency intent layer (plan §13 T2) to route the
    registered question to the schema predicates that answer its concept roles.
    """

    if not predicate_substrings:
        return []
    matches: list[dict[str, Any]] = []
    for t in triples:
        pred = str(t.get("predicate", "")).lower()
        if any(sub.lower() in pred for sub in predicate_substrings):
            matches.append(t)
    return matches


def graph_neighbors(triples: list[dict[str, Any]], entity: str) -> list[dict[str, Any]]:
    """``graph_neighbors`` tool: one-hop neighbors of an entity."""

    return [t for t in triples if t.get("subject") == entity or t.get("object") == entity]


def get_provenance(triples: list[dict[str, Any]]) -> list[str]:
    """``get_provenance`` tool: distinct source ids cited by the triples."""

    sources: list[str] = []
    seen: set[str] = set()
    for t in triples:
        for sid in str(t.get("source_document", "")).split(";"):
            sid = sid.strip()
            if sid and sid not in seen:
                seen.add(sid)
                sources.append(sid)
    return sources


def ontology_labels_for(triples: list[dict[str, Any]], guide: SchemaGuide) -> dict[str, str]:
    """Controlled ontology labels for the classes/properties in the facts.

    Design §12.2: the Query Agent receives ontology labels and property
    descriptions. We surface the human-readable label of every class and
    property referenced by the materialized facts so the answer's rendering of
    an event type (e.g. Ground Stop vs Ground Delay Program) is pinned to the
    ontology, not model memory.
    """

    labels: dict[str, str] = {}
    for t in triples:
        subj_class = str(t.get("subject_class", ""))
        obj_class = str(t.get("object_class", ""))
        pred = str(t.get("predicate", ""))
        for cls in (subj_class, obj_class):
            if cls and cls in guide.classes:
                labels.setdefault(cls, guide.classes[cls].label or cls)
        if pred:
            if pred in guide.object_properties:
                labels.setdefault(pred, guide.object_properties[pred].label or pred)
            elif pred in guide.datatype_properties:
                labels.setdefault(pred, guide.datatype_properties[pred].label or pred)
    return labels


def build_evidence(triples: list[dict[str, Any]], question: str) -> QueryGraphEvidence:
    """Run the deterministic graph tools and assemble QueryGraphEvidence.

    Plan §13 T2: when the question carries a recognized competency concept
    role, route retrieval through the bounded schema-guided intent layer
    (selecting the predicates that answer that role). Otherwise fall back to
    keyword retrieval for simple matching questions.
    """

    intent = competency_intent(question)
    if intent is not None:
        focused = graph_search_by_predicates(triples, intent)
    else:
        focused = graph_search(triples, question)
    # De-duplicate while preserving order (an intent match may overlap a keyword
    # match for the same triple).
    seen: set[tuple[Any, ...]] = set()
    deduped: list[dict[str, Any]] = []
    for t in focused:
        key = (t.get("subject"), t.get("predicate"), t.get("object"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(t)
    facts = [
        {
            "subject": t.get("subject"),
            "predicate": t.get("predicate"),
            "object": t.get("object"),
            "source_document": t.get("source_document"),
        }
        for t in deduped
    ]
    sources = get_provenance(deduped)
    return QueryGraphEvidence(facts=facts, source_ids=sources)


def answer_question(
    *,
    run_dir: str | Path,
    question: str,
    model_invoker: ModelInvoker,
    guide: SchemaGuide | None = None,
    write_run_record: bool = True,
) -> tuple[str, str, list[str], ModelCallRecord, list[dict[str, Any]]]:
    """Answer a question from the materialized graph (design §12, plan §6.3/§13).

    Returns ``(status, answer, source_ids, model_call, graph_facts_seen)`` where
    ``status`` is ``ok``, ``insufficient``, or ``blocked``. Plan §6.3/§13 fixed
    behavior:

    - no matching graph fact -> status ``insufficient``, the shared English
      fallback ``Insufficient graph evidence.``, and zero provider calls;
    - missing provenance -> do not call the model;
    - a provider error or empty response -> status ``blocked`` (never reported
      as insufficient evidence);
    - answer source IDs are a subset of the retrieved fact source IDs;
    - internal ``ANSWER`` and ``SOURCES`` headers are parsed but not displayed.

    When ``write_run_record`` is True (default), writes ``query_run.json`` with
    ``status``, the question, retrieved facts, ontology labels, source IDs,
    final answer, failure reason (when blocked), and model-call metadata.
    """

    triples = load_materialized_triples(run_dir)
    evidence = build_evidence(triples, question)
    schema_guide = guide or load_schema_guide()
    labels = ontology_labels_for(triples, schema_guide)
    # No relevant graph evidence is a deterministic insufficient-evidence
    # result and makes zero provider calls.
    if not evidence.facts:
        rec = _no_call_record("query", "no matching graph evidence")
        if write_run_record:
            _write_query_run(
                run_dir=run_dir, status="insufficient", question=question, facts=[],
                labels=labels, source_ids=[], answer=INSUFFICIENT_EVIDENCE_ANSWER,
                model_call=rec, failure_reason="no matching graph evidence",
            )
        return ("insufficient", INSUFFICIENT_EVIDENCE_ANSWER, [], rec, [])
    # Provenance is a per-fact invariant. Aggregate source presence is not
    # enough: one sourced fact must never mask another unsourced fact.
    facts_missing_provenance = [
        fact
        for fact in evidence.facts
        if not str(fact.get("source_document") or "").strip()
    ]
    if facts_missing_provenance:
        reason = "retrieved graph fact missing provenance"
        rec = _no_call_record("query", reason)
        if write_run_record:
            _write_query_run(
                run_dir=run_dir, status="insufficient", question=question,
                facts=evidence.facts, labels=labels,
                source_ids=evidence.source_ids,
                answer=INSUFFICIENT_EVIDENCE_ANSWER, model_call=rec,
                failure_reason=reason,
            )
        return (
            "insufficient",
            INSUFFICIENT_EVIDENCE_ANSWER,
            [],
            rec,
            evidence.facts,
        )
    task = AgentTask(
        run_id=str(run_dir),
        source_id=str(run_dir),
        objective="answer from materialized graph",
        allowed_tools=["graph_search", "graph_neighbors", "get_provenance"],
    )
    result = run_query_agent(
        task=task,
        question=question,
        evidence=evidence,
        ontology_labels=labels,
        model_invoker=model_invoker,
        insufficient_answer=INSUFFICIENT_EVIDENCE_ANSWER,
    )
    if write_run_record:
        _write_query_run(
            run_dir=run_dir, status=result.status, question=question,
            facts=evidence.facts, labels=labels, source_ids=result.source_ids,
            answer=result.answer, model_call=result.model_call,
            failure_reason=result.failure_reason,
        )
    return (result.status, result.answer, result.source_ids, result.model_call, evidence.facts)


def _no_call_record(agent: str, reason: str) -> ModelCallRecord:
    """A zero-attempt record for the fail-closed path (no provider call)."""

    return ModelCallRecord(agent=agent, raw_response="", error=reason)


def _write_query_run(
    *,
    run_dir: str | Path,
    status: str,
    question: str,
    facts: list[dict[str, Any]],
    labels: dict[str, str],
    source_ids: list[str],
    answer: str,
    model_call: ModelCallRecord | None,
    failure_reason: str = "",
) -> None:
    """Write ``query_run.json`` (plan §6.3, §13 T3)."""

    record = {
        "status": status,
        "question": question,
        "retrieved_facts": facts,
        "ontology_labels": labels,
        "source_ids": source_ids,
        "answer": answer,
        "failure_reason": failure_reason,
        "model_call": model_call.model_dump(mode="json") if model_call else None,
    }
    path = Path(run_dir) / "query_run.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
