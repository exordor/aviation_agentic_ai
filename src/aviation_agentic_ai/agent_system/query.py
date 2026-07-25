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
from collections.abc import Callable
from pathlib import Path
from typing import Any

from aviation_agentic_ai.agent_system.agents import (
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


def graph_search(triples: list[dict[str, Any]], question: str) -> list[dict[str, Any]]:
    """``graph_search`` tool: select triples whose predicate/object/text matches.

    Deterministic keyword match over the materialized graph (no vector store).
    """

    needles = [w.lower() for w in question.split() if len(w) > 2]
    if not needles:
        return list(triples)
    matches: list[dict[str, Any]] = []
    for t in triples:
        haystack = " ".join(
            str(t.get(k, "")) for k in ("subject", "predicate", "object", "source_document")
        ).lower()
        if any(n in haystack for n in needles):
            matches.append(t)
    return matches or list(triples)


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
    """Run the deterministic graph tools and assemble QueryGraphEvidence."""

    focused = graph_search(triples, question)
    facts = [
        {
            "subject": t.get("subject"),
            "predicate": t.get("predicate"),
            "object": t.get("object"),
            "source_document": t.get("source_document"),
        }
        for t in focused
    ]
    sources = get_provenance(focused)
    return QueryGraphEvidence(facts=facts, source_ids=sources)


def answer_question(
    *,
    run_dir: str | Path,
    question: str,
    model_invoker: ModelInvoker,
    guide: SchemaGuide | None = None,
) -> tuple[str, list[str], ModelCallRecord, list[dict[str, Any]]]:
    """Answer a question from the materialized graph (design §12).

    Returns ``(answer, source_ids, model_call, graph_facts_seen)``. The Query
    Agent sees only graph-tool results plus controlled ontology labels; if
    there is no graph evidence the answer is exactly ``图中证据不足`` and no
    model call is made.
    """

    triples = load_materialized_triples(run_dir)
    evidence = build_evidence(triples, question)
    task = AgentTask(
        run_id=str(run_dir),
        source_id=str(run_dir),
        objective="answer from materialized graph",
        allowed_tools=["graph_search", "graph_neighbors", "get_provenance"],
    )
    schema_guide = guide or load_schema_guide()
    labels = ontology_labels_for(triples, schema_guide)
    answer, sources, rec = run_query_agent(
        task=task,
        question=question,
        evidence=evidence,
        ontology_labels=labels,
        model_invoker=model_invoker,
    )
    return answer, sources, rec, evidence.facts
