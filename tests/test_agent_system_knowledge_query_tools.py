"""Constructed knowledge-root retrieval through the online HybridRAG path."""

from __future__ import annotations

import hashlib
from typing import Any

from langchain_core.messages import AIMessage

from aviation_agentic_ai.agent_system.contracts import (
    HybridQueryScope,
    ModelCallRecord,
    SourceFamily,
    ValidationProfileRef,
)
from aviation_agentic_ai.agent_system.knowledge_query import answer_question
from aviation_agentic_ai.agent_system.knowledge_query_tools import (
    KnowledgeQueryGateway,
)
from aviation_agentic_ai.agent_system.knowledge_entity_retrieval_index import (
    KnowledgeEntityVectorHit,
    build_knowledge_entity_retrieval_documents,
)
from aviation_agentic_ai.agent_system.query_runtime import QueryRuntime
from aviation_agentic_ai.agent_system.storage_contracts import (
    ActiveFormalFactBinding,
    FormalFactEvidenceBinding,
    SemanticFactRecord,
    SourceVersionRecord,
)
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
from aviation_agentic_ai.utils.identifiers import stable_id


FAA_ORDER_SOURCE_ID = "source:faa:jo7210.3ee"
PARAGRAPH_ROOT = "urn:faa:7210.3ee:paragraph:18-10-1"
RULE_ROOT = "urn:faa:7210.3ee:rule:18-10-1"
RULE_PUBLICATION = "publication:faa:7210.3ee:rule:18-10-1"
RULE_FACT = "fact:faa:7210.3ee:rule:18-10-1:applies-to-gdp"
RULE_ANCHOR = "anchor:faa:7210.3ee:18-10-1"
GDP_IRI = "https://data.nasa.gov/ontologies/atmonto/ATM#GroundDelayProgramTMI"
APPLIES_TO_TMI_IRI = "urn:aviation-agentic-ai:faa7210.3ee#appliesToTMI"
FAA_ORDER_PROFILE = ValidationProfileRef(
    profile_id="faa-jo-7210.3ee-ontology-profile-v2",
    profile_checksum="a" * 64,
    layer="document_reference",
)


def _source() -> SourceVersionRecord:
    content = "18-10-1. GDP implementation is required for the affected flow."
    digest = hashlib.sha256(content.encode()).hexdigest()
    return SourceVersionRecord(
        source_version_id=stable_id("source-version", FAA_ORDER_SOURCE_ID, digest),
        source_id=FAA_ORDER_SOURCE_ID,
        family=SourceFamily.WEB_DOCUMENT,
        asset_id=None,
        content=content,
        content_sha256=digest,
        source_url="https://www.faa.gov/order/7210.3EE",
        logical_time="2025-02-20T00:00:00Z",
        metadata={"document": "JO 7210.3EE"},
    )


def _binding_store() -> tuple[object, SourceVersionRecord]:
    source = _source()
    paragraph_fact = SemanticFactRecord(
        fact_id="fact:faa:7210.3ee:paragraph:has-rule",
        subject_iri=PARAGRAPH_ROOT,
        subject_class_iri="urn:aviation-agentic-ai:faa7210.3ee#PolicyParagraph",
        predicate_iri="urn:faa:7210.3ee#hasRule",
        object_kind="iri",
        object_value=RULE_ROOT,
        object_class_iri="urn:aviation-agentic-ai:faa7210.3ee#PolicyRule",
        datatype_iri=None,
        validation_profile=FAA_ORDER_PROFILE,
        evidence_mode="source_text",
    )
    rule_fact = SemanticFactRecord(
        fact_id=RULE_FACT,
        subject_iri=RULE_ROOT,
        subject_class_iri="urn:aviation-agentic-ai:faa7210.3ee#PolicyRule",
        predicate_iri=APPLIES_TO_TMI_IRI,
        object_kind="iri",
        object_value=GDP_IRI,
        object_class_iri="https://data.nasa.gov/ontologies/atmonto/ATM#GroundDelayProgramTMI",
        datatype_iri=None,
        validation_profile=FAA_ORDER_PROFILE,
        evidence_mode="source_text",
    )

    def evidence(fact_id: str) -> FormalFactEvidenceBinding:
        return FormalFactEvidenceBinding(
            evidence_link_id=f"evidence:{fact_id}",
            publication_id=(
                RULE_PUBLICATION
                if fact_id == RULE_FACT
                else "publication:faa:7210.3ee:paragraph:18-10-1"
            ),
            fact_id=fact_id,
            source_version_id=source.source_version_id,
            source_anchor_id=RULE_ANCHOR,
            evidence_text=source.content,
            evidence_ref="page=411#18-10-1",
        )

    bindings = (
        ActiveFormalFactBinding(
            root_id=PARAGRAPH_ROOT,
            root_kind="ontology_paragraph",
            temporal_domain_id="faa-jo-7210.3ee-2025",
            publication_id="publication:faa:7210.3ee:paragraph:18-10-1",
            fact=paragraph_fact,
            evidence_links=(evidence(paragraph_fact.fact_id),),
        ),
        ActiveFormalFactBinding(
            root_id=RULE_ROOT,
            root_kind="ontology_entity",
            temporal_domain_id="faa-jo-7210.3ee-2025",
            publication_id=RULE_PUBLICATION,
            fact=rule_fact,
            evidence_links=(evidence(rule_fact.fact_id),),
        ),
    )

    class Store:
        _connection = object()

        def list_active_formal_fact_bindings(
            self,
            *,
            root_ids: tuple[str, ...] = (),
        ) -> tuple[ActiveFormalFactBinding, ...]:
            return tuple(
                binding
                for binding in bindings
                if not root_ids or binding.root_id in root_ids
            )

        def get_source_version(self, version_id: str) -> SourceVersionRecord | None:
            return source if version_id == source.source_version_id else None

    return Store(), source


def test_knowledge_graph_tools_find_and_read_source_bound_roots() -> None:
    store, source = _binding_store()
    runtime = QueryRuntime(store=store, source_index=None, event_index=None)  # type: ignore[arg-type]
    gateway = KnowledgeQueryGateway(runtime=runtime, scope=HybridQueryScope())

    found = gateway.find_knowledge_roots(
        query="What does JO 7210.3EE say about GDP implementation?"
    )
    assert found.status == "ok"
    assert RULE_ROOT in found.details.root_ids
    assert RULE_FACT in found.details.fact_ids

    graph = gateway.read_knowledge_graph(root_id=RULE_ROOT)
    assert graph.status == "ok"
    assert graph.graph_paths[0].edges[0].object_value == GDP_IRI
    assert set(graph.details.root_ids) == {RULE_ROOT, GDP_IRI}
    support = graph.support_records[0]
    assert set(support.root_ids) == {RULE_ROOT, GDP_IRI}
    assert support.publication_ids == (RULE_PUBLICATION,)
    assert support.fact_ids == (RULE_FACT,)
    assert support.source_ids == (source.source_id,)
    assert support.source_anchor_ids == (RULE_ANCHOR,)


def test_knowledge_root_discovery_can_filter_by_predicate_iri() -> None:
    store, _source = _binding_store()
    runtime = QueryRuntime(store=store, source_index=None, event_index=None)  # type: ignore[arg-type]
    gateway = KnowledgeQueryGateway(runtime=runtime, scope=HybridQueryScope())

    found = gateway.find_knowledge_roots(
        query="Which roots use this formal relationship?",
        predicate_iri=APPLIES_TO_TMI_IRI,
    )

    assert found.status == "ok"
    assert found.details.root_ids == (RULE_ROOT,)
    assert found.details.fact_ids == (RULE_FACT,)


def test_knowledge_entity_document_uses_published_graph_and_evidence() -> None:
    store, source = _binding_store()

    documents = build_knowledge_entity_retrieval_documents(store)  # type: ignore[arg-type]

    document = next(row for row in documents if row.root_id == RULE_ROOT)
    assert document.class_iri == "urn:aviation-agentic-ai:faa7210.3ee#PolicyRule"
    assert "PolicyRule" in document.text
    assert "appliesToTMI" in document.text
    assert "GroundDelayProgramTMI" in document.text
    assert source.source_version_id in document.source_version_ids
    assert RULE_ANCHOR in document.source_anchor_ids


class _KnowledgeEntityIndex:
    def __init__(self) -> None:
        self.queries: list[tuple[str, tuple[str, ...], int]] = []

    def query_entities(
        self,
        *,
        query_text: str,
        candidate_root_ids: tuple[str, ...],
        n_results: int,
    ) -> tuple[KnowledgeEntityVectorHit, ...]:
        self.queries.append((query_text, candidate_root_ids, n_results))
        return (
            KnowledgeEntityVectorHit(
                root_id=RULE_ROOT,
                publication_id=RULE_PUBLICATION,
                class_iri="urn:aviation-agentic-ai:faa7210.3ee#PolicyRule",
                label="GDP implementation rule",
                distance=0.1,
                similarity=0.9,
            ),
        )


def test_knowledge_entity_vector_discovery_returns_candidates_not_graph_facts() -> None:
    store, _source = _binding_store()
    knowledge_index = _KnowledgeEntityIndex()
    runtime = QueryRuntime(
        store=store,  # type: ignore[arg-type]
        source_index=None,
        event_index=None,
        knowledge_index=knowledge_index,  # type: ignore[arg-type]
    )
    gateway = KnowledgeQueryGateway(runtime=runtime, scope=HybridQueryScope())

    observation = gateway.search_knowledge_entities(
        query="Who coordinates GDP implementation?",
        limit=3,
    )

    assert observation.status == "ok"
    assert observation.details.root_ids == (RULE_ROOT,)
    assert observation.details.fact_ids == ()
    assert knowledge_index.queries == [
        (
            "Who coordinates GDP implementation?",
            (RULE_ROOT,),
            3,
        )
    ]
    assert "candidate" in observation.limitation.lower()


class _KnowledgeRouter:
    def invoke(self, _messages: list[Any], *, phase: str) -> ToolModelTurn:
        assert phase == "select_tool"
        return ToolModelTurn(
            message=AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": "route-knowledge",
                        "name": "select_query_tool_families",
                        "args": {"families": ["knowledge"]},
                    }
                ],
            ),
            record=ModelCallRecord(agent="query", raw_response=""),
        )


class _KnowledgeAnswer:
    def __init__(self, root_id: str, fact_id: str, source: SourceVersionRecord) -> None:
        self.root_id = root_id
        self.fact_id = fact_id
        self.source = source
        self.turn = 0

    def invoke(self, _messages: list[Any], *, phase: str) -> ToolModelTurn:
        assert phase == "query_step"
        self.turn += 1
        if self.turn == 1:
            call = {
                "id": "search-knowledge",
                "name": "search_knowledge_entities",
                "args": {"query": "GDP implementation"},
            }
            return ToolModelTurn(
                message=AIMessage(content="", tool_calls=[call]),
                record=ModelCallRecord(agent="query", raw_response=""),
            )
        if self.turn == 2:
            call = {
                "id": "read-knowledge",
                "name": "read_knowledge_graph",
                "args": {"root_id": self.root_id},
            }
            return ToolModelTurn(
                message=AIMessage(content="", tool_calls=[call]),
                record=ModelCallRecord(agent="query", raw_response=""),
            )
        payload = {
            "status": "ok",
            "statements": [
                {
                    "kind": "source_fact",
                    "text": "The policy rule applies to a Ground Delay Program.",
                    "support_root_ids": [self.root_id],
                    "support_publication_ids": [RULE_PUBLICATION],
                    "support_fact_ids": [self.fact_id],
                    "support_source_ids": [self.source.source_id],
                    "support_source_version_ids": [self.source.source_version_id],
                    "support_source_anchor_ids": [RULE_ANCHOR],
                }
            ],
            "limitations": [],
        }
        import json

        response = json.dumps(payload)
        return ToolModelTurn(
            message=AIMessage(content=response),
            record=ModelCallRecord(agent="query", raw_response=response),
        )


def test_public_query_routes_to_knowledge_graph_and_binds_answer_evidence() -> None:
    store, source = _binding_store()
    runtime = QueryRuntime(  # type: ignore[arg-type]
        store=store,
        source_index=None,
        event_index=None,
        knowledge_index=_KnowledgeEntityIndex(),
    )
    answer_model = _KnowledgeAnswer(RULE_ROOT, RULE_FACT, source)

    def factory(tools: list[Any]) -> object:
        if {tool.name for tool in tools} == {"select_query_tool_families"}:
            return _KnowledgeRouter()
        return answer_model

    outcome = answer_question(
        runtime=runtime,
        question="Which FAA rule applies to GDP implementation?",
        scope=HybridQueryScope(),
        model_factory=factory,  # type: ignore[arg-type]
    )

    assert outcome.status == "ok", outcome.failure_reason
    assert outcome.route_trace is not None
    assert outcome.route_trace.selected_families == ("knowledge",)
    assert "search_knowledge_entities" in outcome.route_trace.selected_tool_names
    assert "read_source" in outcome.route_trace.selected_tool_names
    assert set(outcome.retrieved_root_ids) == {RULE_ROOT, GDP_IRI}
    assert set(outcome.retrieved_fact_ids) == {RULE_FACT}
    assert outcome.retrieved_source_anchor_ids == [RULE_ANCHOR]
