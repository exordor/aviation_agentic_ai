"""Deterministic validation and publication bridge for generated facts.

The LLM generator returns only a candidate proposal.  This module binds each
candidate to an immutable source version and anchor, converts it to the
existing ``ValidatedFact`` contract, and runs the shared Formal Publication
Kernel before producing a domain-neutral knowledge publication package.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Literal

from aviation_agentic_ai.agent_system.contracts import (
    FactTraceRow,
    SourceSnapshot,
    SourceSnapshotRegistry,
    ValidatedFact,
)
from aviation_agentic_ai.agent_system.kg_generation_contracts import (
    CandidateFactProposal,
    GenerationEvidenceRecord,
    OntologyGenerationTask,
)
from aviation_agentic_ai.agent_system.knowledge_publication import (
    KnowledgePublicationPackage,
    KnowledgePublicationRecord,
    KnowledgeRootRecord,
    PublicationEvidenceLink,
    PublicationFactMembership,
    PublicationSourceMembership,
    stable_knowledge_publication_id,
)
from aviation_agentic_ai.agent_system.materialize import (
    FormalPublication,
    FormalPublicationBlocked,
    run_formal_publication_kernel,
)
from aviation_agentic_ai.agent_system.storage_contracts import (
    SemanticFactRecord,
    SourceAnchorRecord,
    SourceVersionRecord,
)
from aviation_agentic_ai.agent_system.validation_profiles import (
    ValidationProfileRegistry,
)
from aviation_agentic_ai.utils.identifiers import stable_id


@dataclass(frozen=True)
class GeneratedFactPublication:
    """Result of validating one candidate proposal without writing storage."""

    status: Literal["ok", "abstained", "blocked"]
    formal_publication: FormalPublication | None
    package: KnowledgePublicationPackage | None
    accepted_facts: tuple[ValidatedFact, ...]
    profile_gaps: tuple[object, ...]
    reason: str | None = None


def merge_candidate_fact_proposals(
    proposals: tuple[CandidateFactProposal, ...] | list[CandidateFactProposal],
) -> CandidateFactProposal:
    """Fuse incremental model proposals without collapsing provenance.

    Semantic duplicates remain as separate candidate rows when their evidence
    references differ.  The publication bridge collapses their semantic fact
    identity and emits one-to-many evidence links.  Exact duplicate rows from
    a replay are removed here so a repeated incremental pass is byte-stable.
    """

    if not proposals:
        raise ValueError("at least one candidate proposal is required")
    facts = []
    seen_rows: set[tuple[str, str, str, str | None, str | None, str]] = set()
    abstentions = []
    profile_gaps = []
    for proposal in proposals:
        for fact in proposal.facts:
            key = (
                fact.predicate_iri,
                fact.object_kind,
                fact.object_value,
                fact.object_class_iri,
                fact.datatype_iri,
                fact.evidence_ref,
            )
            if key not in seen_rows:
                seen_rows.add(key)
                facts.append(fact)
        abstentions.extend(proposal.abstentions)
        profile_gaps.extend(proposal.profile_gaps)
    return CandidateFactProposal(
        status="accepted" if facts else "abstained",
        facts=tuple(facts),
        abstentions=tuple(abstentions),
        profile_gaps=tuple(profile_gaps),
    )


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _profile_ref(
    task: OntologyGenerationTask,
    profile_registry: ValidationProfileRegistry,
):
    profile_id = task.ontology_slice.profile_id
    if profile_id is None:
        raise ValueError("generated publication requires an active profile ID")
    candidates = [
        profile for profile in profile_registry.profiles
        if profile.ref.profile_id == profile_id
    ]
    if not candidates:
        raise ValueError(f"active profile is not loaded: {profile_id}")
    profile = candidates[0]
    expected_checksum = task.ontology_slice.profile_checksum
    if expected_checksum is not None and profile.ref.profile_checksum != expected_checksum:
        raise ValueError("task profile checksum does not match loaded profile")
    return profile.ref


def _binding_map(
    task: OntologyGenerationTask,
) -> dict[str, GenerationEvidenceRecord]:
    return {
        binding.evidence_ref: binding
        for binding in task.evidence_bindings
    }


def _source_versions_by_id(
    source_versions: tuple[SourceVersionRecord, ...],
) -> dict[str, SourceVersionRecord]:
    versions = {version.source_version_id: version for version in source_versions}
    if len(versions) != len(source_versions):
        raise ValueError("source versions must be unique")
    return versions


def _validate_binding(
    binding: GenerationEvidenceRecord,
    versions_by_id: dict[str, SourceVersionRecord],
) -> SourceVersionRecord:
    version = versions_by_id.get(binding.source_version_id)
    if version is None:
        raise ValueError(
            f"evidence binding references an unknown source version: "
            f"{binding.source_version_id}"
        )
    if version.source_id != binding.source_id:
        raise ValueError("evidence binding source and source version differ")
    if binding.char_end > len(version.content):
        raise ValueError("evidence anchor exceeds source version content")
    if version.content[binding.char_start:binding.char_end] != binding.evidence_text:
        raise ValueError("evidence text does not match its source anchor")
    expected_anchor_id = stable_id(
        "source-anchor",
        binding.source_version_id,
        binding.char_start,
        binding.char_end,
    )
    if binding.source_anchor_id != expected_anchor_id:
        raise ValueError("evidence anchor identity does not match its span")
    return version


def _source_snapshot_registry(
    versions: tuple[SourceVersionRecord, ...],
) -> SourceSnapshotRegistry:
    snapshots_by_source: dict[str, SourceSnapshot] = {}
    for version in versions:
        snapshots_by_source.setdefault(
            version.source_id,
            SourceSnapshot(
                source_id=version.source_id,
                family=version.family,
                source_url=version.source_url,
                content=version.content,
                content_sha256=version.content_sha256,
            ),
        )
    snapshots = tuple(
        snapshots_by_source[source_id]
        for source_id in sorted(snapshots_by_source)
    )
    return SourceSnapshotRegistry(snapshots=snapshots)


def _fact_id(task: OntologyGenerationTask, candidate) -> str:
    return stable_id(
        "semantic-fact",
        task.root_id,
        task.ontology_slice.subject_class_iri,
        candidate.predicate_iri,
        candidate.object_kind,
        candidate.object_value,
        candidate.object_class_iri or "",
        candidate.datatype_iri or "",
    )


def _to_validated_facts(
    *,
    task: OntologyGenerationTask,
    proposal: CandidateFactProposal,
    profile_ref,
    versions_by_id: dict[str, SourceVersionRecord],
    bindings: dict[str, GenerationEvidenceRecord],
) -> tuple[
    list[ValidatedFact],
    list[FactTraceRow],
    dict[str, tuple[GenerationEvidenceRecord, ...]],
]:
    facts: list[ValidatedFact] = []
    traces: list[FactTraceRow] = []
    fact_bindings: dict[str, list[GenerationEvidenceRecord]] = {}
    seen_ids: set[str] = set()
    for candidate in proposal.facts:
        binding = bindings.get(candidate.evidence_ref)
        if binding is None:
            raise ValueError("candidate fact evidence is not bound")
        version = _validate_binding(binding, versions_by_id)
        fact_id = _fact_id(task, candidate)
        if fact_id not in seen_ids:
            seen_ids.add(fact_id)
            facts.append(
                ValidatedFact(
                    fact_id=fact_id,
                    subject_iri=task.root_id,
                    subject_class_iri=task.ontology_slice.subject_class_iri,
                    predicate_iri=candidate.predicate_iri,
                    object_kind=candidate.object_kind,
                    object_value=candidate.object_value,
                    object_class_iri=candidate.object_class_iri,
                    datatype_iri=candidate.datatype_iri,
                    source_ids=[version.source_id],
                    evidence_texts=[binding.evidence_text],
                    validation_profile=profile_ref,
                    evidence_mode="source_text",
                    # The Formal Publication Kernel trace contract
                    # uses the fact ID as its internal source-text key.  The
                    # original task reference is retained on the generic
                    # package, which can carry one-to-many evidence links.
                    evidence_ref=fact_id,
                )
            )
            traces.append(
                FactTraceRow(
                    fact_id=fact_id,
                    graph_patch_line=(
                        f"{task.root_id} | {candidate.predicate_iri} | "
                        f"{candidate.object_value} | {version.source_id}"
                    ),
                    source_id=version.source_id,
                    evidence_text=binding.evidence_text,
                    evidence_agent_role="kg_generation",
                    source_snapshot_sha256=version.content_sha256,
                )
            )
        fact_bindings.setdefault(fact_id, []).append(binding)
    return facts, traces, {
        fact_id: tuple(bindings_for_fact)
        for fact_id, bindings_for_fact in fact_bindings.items()
    }


def _build_package(
    *,
    task: OntologyGenerationTask,
    facts: tuple[ValidatedFact, ...],
    fact_bindings: dict[str, tuple[GenerationEvidenceRecord, ...]],
    versions_by_id: dict[str, SourceVersionRecord],
    primary_source_version_id: str,
    root_kind: str,
) -> KnowledgePublicationPackage:
    used_binding_refs: list[str] = []
    used_version_ids: set[str] = {primary_source_version_id}
    anchors: dict[str, SourceAnchorRecord] = {}
    for fact in facts:
        for binding in fact_bindings[fact.fact_id]:
            used_binding_refs.append(binding.evidence_ref)
            used_version_ids.add(binding.source_version_id)
            anchors[binding.source_anchor_id] = SourceAnchorRecord(
                source_anchor_id=binding.source_anchor_id,
                source_version_id=binding.source_version_id,
                char_start=binding.char_start,
                char_end=binding.char_end,
                anchor_kind=(
                    "full_record"
                    if binding.char_start == 0
                    and binding.char_end == len(versions_by_id[binding.source_version_id].content)
                    else "text_span"
                ),
            )

    publication_payload = {
        "root_id": task.root_id,
        "root_kind": root_kind,
        "temporal_domain_id": task.temporal_domain_id,
        "facts": [fact.model_dump(mode="json") for fact in facts],
        "source_version_ids": sorted(used_version_ids),
        "evidence_refs": sorted(used_binding_refs),
    }
    digest = _digest(publication_payload)
    publication_id = stable_knowledge_publication_id(
        task.root_id,
        primary_source_version_id,
        digest,
    )
    source_versions = [versions_by_id[source_id] for source_id in sorted(used_version_ids)]
    primary = versions_by_id[primary_source_version_id]
    source_versions = [primary] + [
        version
        for version in source_versions
        if version.source_version_id != primary_source_version_id
    ]

    evidence_links = []
    for fact in facts:
        for binding in fact_bindings[fact.fact_id]:
            evidence_links.append(
                PublicationEvidenceLink(
                    evidence_link_id=stable_id(
                        "publication-evidence",
                        publication_id,
                        "fact",
                        fact.fact_id,
                        binding.source_version_id,
                        binding.source_anchor_id,
                        binding.evidence_ref,
                    ),
                    publication_id=publication_id,
                    owner_kind="fact",
                    owner_id=fact.fact_id,
                    source_version_id=binding.source_version_id,
                    source_anchor_id=binding.source_anchor_id,
                    evidence_text=binding.evidence_text,
                    evidence_ref=binding.evidence_ref,
                )
            )

    return KnowledgePublicationPackage(
        root=KnowledgeRootRecord(
            root_id=task.root_id,
            root_kind=root_kind,
            temporal_domain_id=task.temporal_domain_id,
            active_publication_id=publication_id,
        ),
        publication=KnowledgePublicationRecord(
            publication_id=publication_id,
            root_id=task.root_id,
            temporal_domain_id=task.temporal_domain_id,
            primary_source_version_id=primary_source_version_id,
            formal_publication_digest=digest,
        ),
        publication_sources=tuple(
            PublicationSourceMembership(
                membership_id=stable_id(
                    "publication-source",
                    publication_id,
                    version.source_version_id,
                    "primary" if index == 0 else "supporting",
                ),
                publication_id=publication_id,
                source_version_id=version.source_version_id,
                source_role="primary" if index == 0 else "supporting",
            )
            for index, version in enumerate(source_versions)
        ),
        source_anchors=tuple(anchors[key] for key in sorted(anchors)),
        facts=tuple(
            SemanticFactRecord(
                fact_id=fact.fact_id,
                subject_iri=fact.subject_iri,
                subject_class_iri=fact.subject_class_iri,
                predicate_iri=fact.predicate_iri,
                object_kind=fact.object_kind,
                object_value=fact.object_value,
                object_class_iri=fact.object_class_iri,
                datatype_iri=fact.datatype_iri,
                validation_profile=fact.validation_profile,
                evidence_mode=fact.evidence_mode,
            )
            for fact in facts
        ),
        fact_memberships=tuple(
            PublicationFactMembership(
                membership_id=stable_id("publication-fact", publication_id, fact.fact_id),
                publication_id=publication_id,
                fact_id=fact.fact_id,
            )
            for fact in facts
        ),
        evidence_links=tuple(evidence_links),
    )


def validate_and_prepare_generated_publication(
    *,
    task: OntologyGenerationTask,
    proposal: CandidateFactProposal,
    profile_registry: ValidationProfileRegistry,
    source_versions: tuple[SourceVersionRecord, ...],
    primary_source_version_id: str,
    root_kind: str = "ontology_generated",
) -> GeneratedFactPublication:
    """Validate and package a candidate proposal without writing any store."""

    if proposal.status == "abstained" and not proposal.facts:
        return GeneratedFactPublication(
            status="abstained",
            formal_publication=None,
            package=None,
            accepted_facts=(),
            profile_gaps=tuple(proposal.profile_gaps),
            reason=(proposal.abstentions[0].reason if proposal.abstentions else "model abstained"),
        )

    try:
        proposal.validate_against(task)
        profile_ref = _profile_ref(task, profile_registry)
        versions_by_id = _source_versions_by_id(source_versions)
        if primary_source_version_id not in versions_by_id:
            raise ValueError("primary source version is not registered")
        bindings = _binding_map(task)
        facts, traces, fact_bindings = _to_validated_facts(
            task=task,
            proposal=proposal,
            profile_ref=profile_ref,
            versions_by_id=versions_by_id,
            bindings=bindings,
        )
        snapshots = _source_snapshot_registry(source_versions)
        formal_publication = run_formal_publication_kernel(
            facts=facts,
            profile_registry=profile_registry,
            source_snapshot=snapshots,
            fact_traces=traces,
        )
        package = _build_package(
            task=task,
            facts=formal_publication.accepted,
            fact_bindings=fact_bindings,
            versions_by_id=versions_by_id,
            primary_source_version_id=primary_source_version_id,
            root_kind=root_kind,
        )
    except (ValueError, FormalPublicationBlocked) as exc:
        return GeneratedFactPublication(
            status="blocked",
            formal_publication=None,
            package=None,
            accepted_facts=(),
            profile_gaps=tuple(proposal.profile_gaps),
            reason=str(exc),
        )

    return GeneratedFactPublication(
        status="ok",
        formal_publication=formal_publication,
        package=package,
        accepted_facts=formal_publication.accepted,
        profile_gaps=tuple(proposal.profile_gaps),
    )


def apply_generated_publication(
    store,
    result: GeneratedFactPublication,
    source_versions: tuple[SourceVersionRecord, ...],
) -> str:
    """Register immutable inputs and apply one validated publication.

    The store is intentionally duck-typed here so the validation module stays
    independent of the concrete SQLite implementation.  Reapplying the same
    result is idempotent because the publication identity is content-derived.
    """

    if result.status != "ok" or result.package is None:
        raise ValueError("only an accepted generated publication can be applied")
    store.register_source_versions(source_versions)
    return store.apply_knowledge_publication(result.package)


__all__ = [
    "GeneratedFactPublication",
    "apply_generated_publication",
    "merge_candidate_fact_proposals",
    "validate_and_prepare_generated_publication",
]
