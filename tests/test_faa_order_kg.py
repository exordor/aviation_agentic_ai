from __future__ import annotations

import json
from pathlib import Path

from langchain_core.messages import AIMessage, BaseMessage

from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.faa_order_document import (
    build_faa_order_source_package,
)
from aviation_agentic_ai.agent_system.faa_order_kg import run_faa_order_kg
from aviation_agentic_ai.agent_system.faa_order_ontology import (
    ATMONTO_GDP_CLASS,
    FAA_ORDER_NAMESPACE,
    OPERATIONAL_ROLE_CLASS,
    POLICY_RULE_CLASS,
)
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
from aviation_agentic_ai.utils.pdf import PdfPage


class _PolicyExtractionModel:
    def __init__(self, stage: str, task: object) -> None:
        self.stage = stage
        self.task = task

    def invoke(
        self,
        _messages: list[BaseMessage],
        *,
        phase: str,
    ) -> ToolModelTurn:
        evidence_ref = self.task.evidence_ref
        if self.stage == "ner":
            assert phase == "extract_entities"
            rule_surface = self.task.evidence_text.split("\n", 1)[-1].rstrip(".")
            payload = {
                "status": "accepted",
                "mentions": [
                    {
                        "mention_id": "role",
                        "surface_text": "ATCSCC",
                        "class_iri": OPERATIONAL_ROLE_CLASS,
                        "evidence_ref": evidence_ref,
                        "concept_or_instance": "instance",
                        "confidence": 0.95,
                    },
                    {
                        "mention_id": "gdp",
                        "surface_text": "GDP",
                        "class_iri": ATMONTO_GDP_CLASS,
                        "evidence_ref": evidence_ref,
                        "concept_or_instance": "concept",
                        "confidence": 0.98,
                    },
                    {
                        "mention_id": "rule",
                        "surface_text": rule_surface,
                        "class_iri": POLICY_RULE_CLASS,
                        "evidence_ref": evidence_ref,
                        "concept_or_instance": "instance",
                        "confidence": 0.88,
                    },
                ],
                "unmapped_mentions": [],
                "abstentions": [],
            }
        else:
            assert self.stage == "re"
            assert phase == "extract_relations"
            rule = next(row for row in self.task.entities if row.class_iri == POLICY_RULE_CLASS)
            gdp = next(row for row in self.task.entities if row.class_iri == ATMONTO_GDP_CLASS)
            role = next(
                row for row in self.task.entities if row.class_iri == OPERATIONAL_ROLE_CLASS
            )
            payload = {
                "status": "accepted",
                "relations": [
                    {
                        "subject_id": rule.entity_id,
                        "predicate_iri": FAA_ORDER_NAMESPACE + "appliesToTMI",
                        "object_id": gdp.entity_id,
                        "evidence_ref": evidence_ref,
                        "evidence_quote": "GDP",
                        "confidence": 0.91,
                    },
                    {
                        "subject_id": rule.entity_id,
                        "predicate_iri": FAA_ORDER_NAMESPACE + "assignsResponsibilityTo",
                        "object_id": role.entity_id,
                        "evidence_ref": evidence_ref,
                        "evidence_quote": "ATCSCC",
                        "confidence": 0.89,
                    },
                ],
                "abstentions": [],
            }
        raw = json.dumps(payload)
        return ToolModelTurn(
            message=AIMessage(content=raw),
            record=ModelCallRecord(
                agent=f"kg_{self.stage}",
                raw_response=raw,
                prompt_set_id="offline-test",
                prompt_version="offline-test",
                provider="scripted",
                model="scripted",
                temperature=0.0,
                input_tokens=13,
                output_tokens=8,
                latency_ms=2.5,
            ),
        )


def _model_factory(stage: str, task: object) -> _PolicyExtractionModel:
    return _PolicyExtractionModel(stage, task)


def _package():
    return build_faa_order_source_package(
        (
            PdfPage(
                page_number=411,
                text=(
                    "18-10-1. POLICY\nATCSCC establishes the GDP.\n"
                    "18-10-2. COORDINATION\nATCSCC coordinates the GDP."
                ),
            ),
        ),
        pdf_sha256="d" * 64,
        pdf_byte_count=123,
    )


def test_faa_order_kg_requires_explicit_live_authorization_without_test_factory(
    tmp_path: Path,
) -> None:
    package = _package()
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="faa-order-kg-auth-test",
        create=True,
    )
    try:
        summary = run_faa_order_kg(package, store)
        assert summary.status == "blocked"
        assert summary.provider_call_count == 0
        assert summary.blocked_count == len(package.extraction_chunks)
    finally:
        store.close()


def test_two_stage_extraction_publishes_multihop_faa_order_graph(
    tmp_path: Path,
) -> None:
    package = _package()
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="faa-order-kg-two-stage-test",
        create=True,
    )
    try:
        summary = run_faa_order_kg(
            package,
            store,
            model_factory=_model_factory,
        )

        assert summary.status == "ok"
        assert summary.ner_call_count == 2
        assert summary.re_call_count == 2
        assert summary.provider_call_count == 4
        assert summary.entity_candidate_count == 6
        assert summary.relation_candidate_count == 4
        bindings = store.list_active_formal_fact_bindings()
        predicates = {row.fact.predicate_iri for row in bindings}
        assert {
            FAA_ORDER_NAMESPACE + "hasSection",
            FAA_ORDER_NAMESPACE + "hasParagraph",
            FAA_ORDER_NAMESPACE + "mentionsEntity",
            FAA_ORDER_NAMESPACE + "appliesToTMI",
            FAA_ORDER_NAMESPACE + "assignsResponsibilityTo",
        } <= predicates
        assert any(row.root_kind == "ontology_entity" for row in bindings)
    finally:
        store.close()


def test_same_entity_merges_cross_paragraph_evidence_and_replay_is_stable(
    tmp_path: Path,
) -> None:
    package = _package()
    store = AviationEvidenceStore.open(
        tmp_path / "store",
        dataset_id="faa-order-kg-idempotence-test",
        create=True,
    )
    try:
        first = run_faa_order_kg(package, store, model_factory=_model_factory)
        first_bindings = store.list_active_formal_fact_bindings()
        gdp_label = next(
            row
            for row in first_bindings
            if row.fact.subject_class_iri == ATMONTO_GDP_CLASS
            and row.fact.predicate_iri.endswith("label")
        )
        assert len(gdp_label.evidence_links) == 2

        second = run_faa_order_kg(package, store, model_factory=_model_factory)
        second_bindings = store.list_active_formal_fact_bindings()

        assert first.status == second.status == "ok"
        assert first.publication_ids == second.publication_ids
        assert first_bindings == second_bindings
    finally:
        store.close()
