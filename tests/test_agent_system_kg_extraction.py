from __future__ import annotations

import json

from langchain_core.messages import AIMessage, BaseMessage

from aviation_agentic_ai.agent_system.contracts import ModelCallRecord
from aviation_agentic_ai.agent_system.faa_order_document import (
    build_faa_order_source_package,
)
from aviation_agentic_ai.agent_system.faa_order_ontology import (
    ATMONTO_GDP_CLASS,
    FAA_ORDER_NAMESPACE,
    OPERATIONAL_ROLE_CLASS,
    build_faa_order_entity_extraction_task,
    build_faa_order_relation_extraction_task,
    normalize_faa_order_entities,
)
from aviation_agentic_ai.agent_system.kg_generation import (
    build_entity_extraction_messages,
    build_relation_extraction_messages,
    extract_entity_mentions,
    extract_relation_candidates,
    locate_relation_evidence,
)
from aviation_agentic_ai.agent_system.kg_generation_contracts import (
    EntityExtractionProposal,
    RelationExtractionProposal,
)
from aviation_agentic_ai.agent_system.tool_model import ToolModelTurn
from aviation_agentic_ai.utils.pdf import PdfPage


class _ScriptedExtractionModel:
    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload
        self.phases: list[str] = []

    def invoke(
        self,
        _messages: list[BaseMessage],
        *,
        phase: str,
    ) -> ToolModelTurn:
        self.phases.append(phase)
        raw = json.dumps(self.payload, ensure_ascii=False)
        return ToolModelTurn(
            message=AIMessage(content=raw),
            record=ModelCallRecord(
                agent="kg_extraction",
                raw_response=raw,
                prompt_set_id="test",
                prompt_version="test",
                provider="scripted",
                model="scripted",
                temperature=0.0,
                input_tokens=11,
                output_tokens=7,
            ),
        )


def _package():
    return build_faa_order_source_package(
        (
            PdfPage(
                page_number=411,
                text=(
                    "18-10-1. POLICY\n"
                    "The ATCSCC may implement a GDP and coordinate with affected ARTCCs."
                ),
            ),
        ),
        pdf_sha256="e" * 64,
        pdf_byte_count=456,
    )


def _entity_payload() -> dict[str, object]:
    return {
        "status": "accepted",
        "mentions": [
            {
                "mention_id": "m1",
                "surface_text": "ATCSCC",
                "class_iri": OPERATIONAL_ROLE_CLASS,
                "evidence_ref": _package().extraction_chunks[0].evidence_ref,
                "concept_or_instance": "instance",
                "confidence": 0.98,
            },
            {
                "mention_id": "m2",
                "surface_text": "GDP",
                "class_iri": ATMONTO_GDP_CLASS,
                "evidence_ref": _package().extraction_chunks[0].evidence_ref,
                "concept_or_instance": "concept",
                "confidence": 0.99,
            },
            {
                "mention_id": "m3",
                "surface_text": "implement a GDP and coordinate with affected ARTCCs",
                "class_iri": FAA_ORDER_NAMESPACE + "PolicyRule",
                "evidence_ref": _package().extraction_chunks[0].evidence_ref,
                "concept_or_instance": "instance",
                "confidence": 0.82,
            },
        ],
        "unmapped_mentions": ["affected ARTCCs"],
        "abstentions": [],
    }


def test_ner_prompt_contains_only_compact_schema_evidence_and_unseen_few_shots() -> None:
    package = _package()
    task = build_faa_order_entity_extraction_task(
        package,
        package.extraction_chunks[0],
    )

    prompt = str(build_entity_extraction_messages(task)[1].content)

    assert task.ontology_schema.prompt_schema in prompt
    assert package.extraction_chunks[0].evidence_text in prompt
    assert "FULL_ATMONTO_OWL" not in prompt
    assert prompt.count("FEW_SHOT_EXAMPLE") == 3


def test_generic_ner_prompt_does_not_inject_faa_examples() -> None:
    package = _package()
    task = build_faa_order_entity_extraction_task(
        package,
        package.extraction_chunks[0],
    ).model_copy(update={"few_shot_examples": ()})

    messages = build_entity_extraction_messages(task)
    prompt = str(messages[1].content)

    assert "FEW_SHOT_EXAMPLE" not in prompt
    assert "traffic management unit coordinates a ground stop" not in prompt
    assert "FAA evidence" not in str(messages[0].content)


def test_generic_relation_prompt_does_not_inject_faa_examples() -> None:
    package = _package()
    chunk = package.extraction_chunks[0]
    entity_task = build_faa_order_entity_extraction_task(package, chunk)
    resolution = normalize_faa_order_entities(
        package,
        chunk,
        EntityExtractionProposal.model_validate(_entity_payload()),
        entity_task.ontology_schema,
    )
    task = build_faa_order_relation_extraction_task(
        package,
        chunk,
        entity_task.ontology_schema,
        resolution.entities,
    )
    assert task is not None
    task = task.model_copy(update={"few_shot_examples": ()})

    messages = build_relation_extraction_messages(task)
    prompt = str(messages[1].content)

    assert "FEW_SHOT_EXAMPLE" not in prompt
    assert "requiresCoordinationWith" not in prompt.split("TASK_PAYLOAD", 1)[0]
    assert "FAA evidence" not in str(messages[0].content)


def test_entity_extraction_and_deterministic_normalization_resolve_aliases() -> None:
    package = _package()
    chunk = package.extraction_chunks[0]
    task = build_faa_order_entity_extraction_task(package, chunk)
    model = _ScriptedExtractionModel(_entity_payload())

    generated = extract_entity_mentions(task, model)
    assert generated.status == "accepted"
    assert generated.proposal is not None
    resolution = normalize_faa_order_entities(
        package,
        chunk,
        generated.proposal,
        task.ontology_schema,
    )

    assert model.phases == ["extract_entities"]
    assert {row.canonical_label for row in resolution.entities} >= {
        "Air Traffic Control System Command Center",
        "Ground Delay Program",
    }
    assert all(row.char_end > row.char_start for row in resolution.entities)
    assert resolution.unmapped_mentions == ("affected ARTCCs",)


def test_entity_contract_rejects_class_outside_active_schema() -> None:
    package = _package()
    task = build_faa_order_entity_extraction_task(
        package,
        package.extraction_chunks[0],
    )
    payload = _entity_payload()
    payload["mentions"][0]["class_iri"] = "https://example.test/Invented"  # type: ignore[index]
    proposal = EntityExtractionProposal.model_validate(payload)

    try:
        proposal.validate_against(task)
    except ValueError as exc:
        assert "outside" in str(exc)
    else:
        raise AssertionError("invented ontology class was accepted")


def test_ner_runtime_keeps_valid_mentions_and_demotes_invalid_terms_to_unmapped() -> None:
    package = _package()
    chunk = package.extraction_chunks[0]
    task = build_faa_order_entity_extraction_task(package, chunk)
    payload = _entity_payload()
    payload["mentions"].append(  # type: ignore[union-attr]
        {
            "mention_id": "invented",
            "surface_text": "affected ARTCCs",
            "class_iri": "https://example.test/Invented",
            "evidence_ref": chunk.evidence_ref,
            "concept_or_instance": "instance",
            "confidence": 0.7,
        }
    )
    payload["unmapped_mentions"] = [
        {"surface_text": "outside profile"},
    ]

    generated = extract_entity_mentions(task, _ScriptedExtractionModel(payload))

    assert generated.status == "accepted"
    assert generated.proposal is not None
    assert len(generated.proposal.mentions) == 3
    assert set(generated.proposal.unmapped_mentions) == {
        "affected ARTCCs",
        "outside profile",
    }


def test_re_uses_only_resolved_entities_and_locates_normalized_quote() -> None:
    package = _package()
    chunk = package.extraction_chunks[0]
    entity_task = build_faa_order_entity_extraction_task(package, chunk)
    proposal = EntityExtractionProposal.model_validate(_entity_payload())
    resolution = normalize_faa_order_entities(
        package,
        chunk,
        proposal,
        entity_task.ontology_schema,
    )
    relation_task = build_faa_order_relation_extraction_task(
        package,
        chunk,
        entity_task.ontology_schema,
        resolution.entities,
    )
    assert relation_task is not None
    rule = next(row for row in resolution.entities if row.class_iri.endswith("PolicyRule"))
    gdp = next(row for row in resolution.entities if row.class_iri == ATMONTO_GDP_CLASS)
    model = _ScriptedExtractionModel(
        {
            "status": "accepted",
            "relations": [
                {
                    "subject_id": rule.entity_id,
                    "predicate_iri": FAA_ORDER_NAMESPACE + "appliesToTMI",
                    "object_id": gdp.entity_id,
                    "evidence_ref": chunk.evidence_ref,
                    "evidence_quote": "implement a GDP",
                    "confidence": 0.91,
                }
            ],
            "abstentions": [],
        }
    )

    generated = extract_relation_candidates(relation_task, model)
    assert generated.status == "accepted"
    assert generated.proposal is not None
    located = locate_relation_evidence(
        generated.proposal,
        relation_task,
        chunk,
    )

    assert model.phases == ["extract_relations"]
    assert located.relations[0].quote_char_start is not None
    assert located.relations[0].quote_char_end is not None
    assert (
        package.source_version.content[
            located.relations[0].quote_char_start : located.relations[0].quote_char_end
        ]
        == "implement a GDP"
    )


def test_re_contract_rejects_unknown_entity_and_property() -> None:
    package = _package()
    chunk = package.extraction_chunks[0]
    entity_task = build_faa_order_entity_extraction_task(package, chunk)
    resolution = normalize_faa_order_entities(
        package,
        chunk,
        EntityExtractionProposal.model_validate(_entity_payload()),
        entity_task.ontology_schema,
    )
    relation_task = build_faa_order_relation_extraction_task(
        package,
        chunk,
        entity_task.ontology_schema,
        resolution.entities,
    )
    assert relation_task is not None
    proposal = RelationExtractionProposal.model_validate(
        {
            "status": "accepted",
            "relations": [
                {
                    "subject_id": "invented:subject",
                    "predicate_iri": "https://example.test/inventedPredicate",
                    "object_id": resolution.entities[0].entity_id,
                    "evidence_ref": chunk.evidence_ref,
                    "evidence_quote": "ATCSCC",
                    "confidence": 0.4,
                }
            ],
        }
    )

    try:
        proposal.validate_against(relation_task)
    except ValueError as exc:
        assert "outside" in str(exc)
    else:
        raise AssertionError("invented relation endpoint was accepted")


def test_re_runtime_normalizes_provider_envelope_and_filters_invalid_rows() -> None:
    package = _package()
    chunk = package.extraction_chunks[0]
    entity_task = build_faa_order_entity_extraction_task(package, chunk)
    resolution = normalize_faa_order_entities(
        package,
        chunk,
        EntityExtractionProposal.model_validate(_entity_payload()),
        entity_task.ontology_schema,
    )
    relation_task = build_faa_order_relation_extraction_task(
        package,
        chunk,
        entity_task.ontology_schema,
        resolution.entities,
    )
    assert relation_task is not None
    rule = next(row for row in resolution.entities if row.class_iri.endswith("PolicyRule"))
    gdp = next(row for row in resolution.entities if row.class_iri == ATMONTO_GDP_CLASS)
    model = _ScriptedExtractionModel(
        {
            "status": "completed",
            "relations": [
                {
                    "subject_id": rule.entity_id,
                    "predicate": "appliesToTMI",
                    "object_id": gdp.entity_id,
                    "evidence_quote": "implement a GDP",
                },
                {
                    "subject_id": "invented:subject",
                    "predicate": "inventedPredicate",
                    "object_id": gdp.entity_id,
                    "evidence_quote": "GDP",
                },
            ],
        }
    )

    generated = extract_relation_candidates(relation_task, model)

    assert generated.status == "accepted"
    assert generated.proposal is not None
    assert len(generated.proposal.relations) == 1
    relation = generated.proposal.relations[0]
    assert relation.predicate_iri == FAA_ORDER_NAMESPACE + "appliesToTMI"
    assert relation.evidence_ref == chunk.evidence_ref
    assert relation.confidence == 0.0
    assert generated.proposal.abstentions


def test_re_is_not_applicable_when_fewer_than_two_entities_resolve() -> None:
    package = _package()
    chunk = package.extraction_chunks[0]
    task = build_faa_order_entity_extraction_task(package, chunk)
    resolution = normalize_faa_order_entities(
        package,
        chunk,
        EntityExtractionProposal(
            status="accepted",
            mentions=(
                {
                    "mention_id": "single",
                    "surface_text": "GDP",
                    "class_iri": ATMONTO_GDP_CLASS,
                    "evidence_ref": chunk.evidence_ref,
                    "concept_or_instance": "concept",
                    "confidence": 1.0,
                },
            ),
        ),
        task.ontology_schema,
    )

    assert (
        build_faa_order_relation_extraction_task(
            package,
            chunk,
            task.ontology_schema,
            resolution.entities,
        )
        is None
    )
