"""Two-stage ATMONTO-constrained KG construction for FAA Chapter 18."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import nullcontext
from dataclasses import dataclass
from typing import Literal

from aviation_agentic_ai.agent_system.evidence_store import AviationEvidenceStore
from aviation_agentic_ai.agent_system.faa_order_document import (
    FAAOrderSourcePackage,
)
from aviation_agentic_ai.agent_system.faa_order_ingestion import (
    register_faa_order_source,
)
from aviation_agentic_ai.agent_system.faa_order_ontology import (
    build_faa_order_entity_extraction_task,
    build_faa_order_relation_extraction_task,
    normalize_faa_order_entities,
)
from aviation_agentic_ai.agent_system.faa_order_publication import (
    publish_faa_order_subgraphs,
)
from aviation_agentic_ai.agent_system.kg_generation import (
    extract_entity_mentions,
    extract_relation_candidates,
    locate_relation_evidence,
    make_live_entity_extraction_model,
    make_live_relation_extraction_model,
)
from aviation_agentic_ai.agent_system.kg_generation_contracts import (
    CandidateKnowledgeSubgraph,
    RelationExtractionProposal,
)
from aviation_agentic_ai.agent_system.kg_live_experiment import (
    KGLiveExperimentRecorder,
)
from aviation_agentic_ai.agent_system.schema_guide import load_schema_guide
from aviation_agentic_ai.agent_system.tool_model import ToolCallingModel
from aviation_agentic_ai.agent_system.validation_profiles import (
    load_validation_profile_registry,
)


FAAOrderExtractionModelFactory = Callable[[str, object], ToolCallingModel]


@dataclass(frozen=True)
class FAAOrderKGSummary:
    """Compact construction, provider, and publication outcome."""

    status: Literal["ok", "insufficient", "blocked"]
    task_count: int
    attempted_count: int
    accepted_count: int
    abstained_count: int
    blocked_count: int
    provider_call_count: int
    ner_call_count: int = 0
    re_call_count: int = 0
    re_not_applicable_count: int = 0
    entity_candidate_count: int = 0
    resolved_entity_count: int = 0
    unmapped_mention_count: int = 0
    relation_candidate_count: int = 0
    validated_relation_count: int = 0
    published_fact_count: int = 0
    published_evidence_link_count: int = 0
    input_token_count: int = 0
    output_token_count: int = 0
    provider_latency_ms: float = 0.0
    publication_ids: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    experiment_manifest_path: str | None = None
    raw_response_artifact: str | None = None
    raw_response_sha256: str | None = None
    parsed_output_artifact: str | None = None
    parsed_output_sha256: str | None = None
    successful_real_calls: int = 0
    failed_real_calls: int = 0


def _record_usage(record: object) -> tuple[int, int, float]:
    return (
        int(getattr(record, "input_tokens", 0)),
        int(getattr(record, "output_tokens", 0)),
        float(getattr(record, "latency_ms", 0.0)),
    )


def run_faa_order_kg(
    package: FAAOrderSourcePackage,
    store: AviationEvidenceStore,
    *,
    allow_live_model: bool = False,
    model_factory: FAAOrderExtractionModelFactory | None = None,
    max_chunks: int | None = None,
    experiment_recorder: KGLiveExperimentRecorder | None = None,
) -> FAAOrderKGSummary:
    """Run NER -> normalization -> RE -> Formal Publication Kernel.

    ``model_factory`` is available only to offline software tests. Live mode
    always builds the pinned DeepSeek adapters and never substitutes scripted,
    replayed, cached, or deterministic model responses.
    """

    if model_factory is not None and allow_live_model:
        raise ValueError("test model_factory cannot be combined with live mode")
    if experiment_recorder is not None and not allow_live_model:
        raise ValueError("live experiment recorder requires live model mode")
    chunks = (
        package.extraction_chunks[:max_chunks]
        if max_chunks is not None
        else package.extraction_chunks
    )
    if not chunks:
        return FAAOrderKGSummary(
            status="insufficient",
            task_count=0,
            attempted_count=0,
            accepted_count=0,
            abstained_count=0,
            blocked_count=0,
            provider_call_count=0,
            reasons=("no FAA order extraction chunks were selected",),
        )
    if model_factory is None and not allow_live_model:
        return FAAOrderKGSummary(
            status="blocked",
            task_count=len(chunks),
            attempted_count=0,
            accepted_count=0,
            abstained_count=0,
            blocked_count=len(chunks),
            provider_call_count=0,
            reasons=("live model authorization is required for KG extraction",),
        )

    register_faa_order_source(store, package)
    profile_registry = load_validation_profile_registry(
        decision_guide=load_schema_guide(),
        include_faa_order=True,
    )
    subgraphs: list[CandidateKnowledgeSubgraph] = []
    reasons: list[str] = []
    attempted = abstained = blocked = provider_calls = 0
    ner_calls = re_calls = re_not_applicable = 0
    entity_candidates = resolved_entities = unmapped_mentions = 0
    relation_candidates = validated_relations = 0
    input_tokens = output_tokens = 0
    provider_latency_ms = 0.0
    eligible_re_chunk_ids: list[str] = []

    for chunk in chunks:
        entity_task = build_faa_order_entity_extraction_task(package, chunk)
        entity_model = (
            model_factory("ner", entity_task)
            if model_factory is not None
            else make_live_entity_extraction_model(task=entity_task)
        )
        ner_trial_id = f"{chunk.chunk_id}:ner"
        ner_call_ids: list[str] = []
        ner_context = (
            experiment_recorder.capture_trial(
                trial_id=ner_trial_id,
                chunk_id=chunk.chunk_id,
                stage="ner",
            )
            if experiment_recorder is not None
            else nullcontext(ner_call_ids)
        )
        with ner_context as captured_ner_call_ids:
            entity_result = extract_entity_mentions(entity_task, entity_model)
        ner_call_ids = list(captured_ner_call_ids)
        attempted += 1
        ner_calls += len(entity_result.model_calls)
        provider_calls += len(entity_result.model_calls)
        for record in entity_result.model_calls:
            input_count, output_count, latency = _record_usage(record)
            input_tokens += input_count
            output_tokens += output_count
            provider_latency_ms += latency
        if entity_result.status == "blocked" or entity_result.proposal is None:
            if experiment_recorder is not None:
                experiment_recorder.record_parsed_output(
                    trial_id=ner_trial_id,
                    chunk_id=chunk.chunk_id,
                    source_unit_id=chunk.paragraph_id,
                    stage="ner",
                    status=entity_result.status,
                    provider_call_ids=ner_call_ids,
                    payload={"failure_reason": entity_result.failure_reason},
                )
            blocked += 1
            reasons.append(
                entity_result.failure_reason
                or f"NER blocked for {chunk.paragraph_id}:{chunk.chunk_index}"
            )
            continue
        if entity_result.status == "abstained":
            abstained += 1
        entity_candidates += len(entity_result.proposal.mentions)
        resolution = normalize_faa_order_entities(
            package,
            chunk,
            entity_result.proposal,
            entity_task.ontology_schema,
        )
        resolved_entities += len(resolution.entities)
        unmapped_mentions += len(resolution.unmapped_mentions)
        if experiment_recorder is not None:
            experiment_recorder.record_parsed_output(
                trial_id=ner_trial_id,
                chunk_id=chunk.chunk_id,
                source_unit_id=chunk.paragraph_id,
                stage="ner",
                status=entity_result.status,
                provider_call_ids=ner_call_ids,
                payload={
                    "proposal": entity_result.proposal.model_dump(mode="json"),
                    "resolved_entities": [
                        row.model_dump(mode="json") for row in resolution.entities
                    ],
                    "unmapped_mentions": list(resolution.unmapped_mentions),
                },
            )
        relation_task = build_faa_order_relation_extraction_task(
            package,
            chunk,
            entity_task.ontology_schema,
            resolution.entities,
        )
        located_relations = RelationExtractionProposal(
            status="not_applicable",
            relations=(),
        )
        if relation_task is None:
            re_not_applicable += 1
        else:
            eligible_re_chunk_ids.append(chunk.chunk_id)
            relation_model = (
                model_factory("re", relation_task)
                if model_factory is not None
                else make_live_relation_extraction_model(task=relation_task)
            )
            re_trial_id = f"{chunk.chunk_id}:re"
            re_call_ids: list[str] = []
            re_context = (
                experiment_recorder.capture_trial(
                    trial_id=re_trial_id,
                    chunk_id=chunk.chunk_id,
                    stage="re",
                )
                if experiment_recorder is not None
                else nullcontext(re_call_ids)
            )
            with re_context as captured_re_call_ids:
                relation_result = extract_relation_candidates(
                    relation_task,
                    relation_model,
                )
            re_call_ids = list(captured_re_call_ids)
            attempted += 1
            re_calls += len(relation_result.model_calls)
            provider_calls += len(relation_result.model_calls)
            for record in relation_result.model_calls:
                input_count, output_count, latency = _record_usage(record)
                input_tokens += input_count
                output_tokens += output_count
                provider_latency_ms += latency
            if relation_result.status == "blocked" or relation_result.proposal is None:
                if experiment_recorder is not None:
                    experiment_recorder.record_parsed_output(
                        trial_id=re_trial_id,
                        chunk_id=chunk.chunk_id,
                        source_unit_id=chunk.paragraph_id,
                        stage="re",
                        status=relation_result.status,
                        provider_call_ids=re_call_ids,
                        payload={"failure_reason": relation_result.failure_reason},
                    )
                blocked += 1
                reasons.append(
                    relation_result.failure_reason
                    or f"RE blocked for {chunk.paragraph_id}:{chunk.chunk_index}"
                )
            else:
                if relation_result.status == "abstained":
                    abstained += 1
                relation_candidates += len(relation_result.proposal.relations)
                located_relations = locate_relation_evidence(
                    relation_result.proposal,
                    relation_task,
                    chunk,
                )
                validated_relations += len(located_relations.relations)
                if experiment_recorder is not None:
                    experiment_recorder.record_parsed_output(
                        trial_id=re_trial_id,
                        chunk_id=chunk.chunk_id,
                        source_unit_id=chunk.paragraph_id,
                        stage="re",
                        status=relation_result.status,
                        provider_call_ids=re_call_ids,
                        payload={
                            "proposal": relation_result.proposal.model_dump(mode="json"),
                            "located_relations": located_relations.model_dump(mode="json"),
                        },
                    )
        if chunk.source_anchor_id is None:
            blocked += 1
            reasons.append(f"source anchor missing for extraction chunk {chunk.chunk_id}")
            continue
        subgraphs.append(
            CandidateKnowledgeSubgraph(
                chunk_id=chunk.chunk_id,
                source_version_id=package.source_version_id,
                source_anchor_id=chunk.source_anchor_id,
                paragraph_id=chunk.paragraph_id,
                profile_id=entity_task.ontology_schema.profile_id,
                profile_checksum=entity_task.ontology_schema.profile_checksum,
                schema_checksum=entity_task.ontology_schema.schema_checksum,
                entities=resolution.entities,
                relations=located_relations.relations,
                unmapped_mentions=resolution.unmapped_mentions,
            )
        )

    publication = publish_faa_order_subgraphs(
        package,
        store,
        chunks=chunks,
        subgraphs=tuple(subgraphs),
        profile_registry=profile_registry,
    )
    blocked += publication.blocked_root_count
    reasons.extend(publication.reasons)
    if blocked:
        status: Literal["ok", "insufficient", "blocked"] = "blocked"
    elif publication.accepted_root_count:
        status = "ok"
    else:
        status = "insufficient"
    manifest = (
        experiment_recorder.finalize(
            eligible_re_chunk_ids=eligible_re_chunk_ids,
            knowledge_revision=store.get_knowledge_revision(),
            publication_count=len(publication.publication_ids),
            construction_status=status,
            entity_candidate_count=entity_candidates,
            resolved_entity_count=resolved_entities,
            unmapped_mention_count=unmapped_mentions,
            relation_candidate_count=relation_candidates,
            validated_relation_count=validated_relations,
            abstained_chunk_count=abstained,
            blocked_chunk_count=blocked,
            published_fact_count=publication.published_fact_count,
            published_evidence_link_count=(publication.published_evidence_link_count),
        )
        if experiment_recorder is not None
        else None
    )
    return FAAOrderKGSummary(
        status=status,
        task_count=attempted,
        attempted_count=attempted,
        accepted_count=publication.accepted_root_count,
        abstained_count=abstained,
        blocked_count=blocked,
        provider_call_count=provider_calls,
        ner_call_count=ner_calls,
        re_call_count=re_calls,
        re_not_applicable_count=re_not_applicable,
        entity_candidate_count=entity_candidates,
        resolved_entity_count=resolved_entities,
        unmapped_mention_count=unmapped_mentions,
        relation_candidate_count=relation_candidates,
        validated_relation_count=validated_relations,
        published_fact_count=publication.published_fact_count,
        published_evidence_link_count=(publication.published_evidence_link_count),
        input_token_count=input_tokens,
        output_token_count=output_tokens,
        provider_latency_ms=provider_latency_ms,
        publication_ids=publication.publication_ids,
        reasons=tuple(reasons),
        experiment_manifest_path=(
            str(experiment_recorder.output_dir / "experiment_manifest.json")
            if experiment_recorder is not None
            else None
        ),
        raw_response_artifact=(manifest.raw_response_artifact if manifest else None),
        raw_response_sha256=(manifest.raw_response_sha256 if manifest else None),
        parsed_output_artifact=(manifest.parsed_output_artifact if manifest else None),
        parsed_output_sha256=(manifest.parsed_output_sha256 if manifest else None),
        successful_real_calls=(manifest.successful_real_calls if manifest else 0),
        failed_real_calls=(manifest.failed_real_calls if manifest else 0),
    )


__all__ = ["FAAOrderKGSummary", "FAAOrderExtractionModelFactory", "run_faa_order_kg"]
