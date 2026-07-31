"""Domain-neutral contracts for atomic semantic knowledge publication."""

from __future__ import annotations

import json
from typing import Any, Literal

from pydantic import Field, model_validator

from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.agent_system.storage_contracts import (
    SemanticFactRecord,
    SourceAnchorRecord,
)
from aviation_agentic_ai.utils.identifiers import stable_id


def _canonical_json(value: object) -> str:
    """Serialize identity inputs without depending on insertion order."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def stable_knowledge_publication_id(
    root_id: str,
    primary_source_version_id: str,
    formal_publication_digest: str,
) -> str:
    """Return the stable publication ID for one semantic-root version."""

    return stable_id(
        "knowledge-publication",
        root_id,
        primary_source_version_id,
        formal_publication_digest,
    )


class KnowledgeRootRecord(StrictModel):
    """One domain semantic identity and its active immutable publication.

    ``root_id`` is the domain identity itself (for example, an ATMONTO Flight
    IRI or an existing TMI event ID), not a generic wrapper resource.
    """

    root_id: str = Field(min_length=1)
    root_kind: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    active_publication_id: str = Field(min_length=1)


class KnowledgePublicationRecord(StrictModel):
    """One immutable, source-qualified publication of a semantic root."""

    publication_id: str = Field(min_length=1)
    root_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    primary_source_version_id: str = Field(min_length=1)
    formal_publication_digest: str = Field(min_length=64, max_length=64)

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> KnowledgePublicationRecord:
        expected_id = stable_knowledge_publication_id(
            self.root_id,
            self.primary_source_version_id,
            self.formal_publication_digest,
        )
        if self.publication_id != expected_id:
            raise ValueError("knowledge publication identity does not match digest")
        return self


class PublicationSourceMembership(StrictModel):
    """Bind one immutable source version to one knowledge publication."""

    membership_id: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    source_version_id: str = Field(min_length=1)
    source_role: Literal["primary", "supporting"]

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> PublicationSourceMembership:
        expected_id = stable_id(
            "publication-source",
            self.publication_id,
            self.source_version_id,
            self.source_role,
        )
        if self.membership_id != expected_id:
            raise ValueError("publication source membership identity does not match")
        return self


class PublicationFactMembership(StrictModel):
    """Bind one provenance-independent semantic fact to one publication."""

    membership_id: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    fact_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> PublicationFactMembership:
        expected_id = stable_id(
            "publication-fact",
            self.publication_id,
            self.fact_id,
        )
        if self.membership_id != expected_id:
            raise ValueError("publication fact membership identity does not match")
        return self


class PublicationEvidenceLink(StrictModel):
    """Exact source evidence for a formal or non-formal publication member."""

    evidence_link_id: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    owner_kind: Literal["fact", "association", "derivation", "structured_record"]
    owner_id: str = Field(min_length=1)
    source_version_id: str = Field(min_length=1)
    source_anchor_id: str | None = Field(default=None, min_length=1)
    evidence_text: str | None = Field(default=None, min_length=1)
    evidence_ref: str = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> PublicationEvidenceLink:
        expected_id = stable_id(
            "publication-evidence",
            self.publication_id,
            self.owner_kind,
            self.owner_id,
            self.source_version_id,
            self.source_anchor_id or "",
            self.evidence_ref,
        )
        if self.evidence_link_id != expected_id:
            raise ValueError("publication evidence link identity does not match")
        return self


class DeterministicDerivationRecord(StrictModel):
    """Versioned deterministic procedure evidence owned by a publication."""

    derivation_id: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)
    procedure_id: str = Field(min_length=1)
    procedure_checksum: str = Field(min_length=64, max_length=64)
    normalized_parameters: dict[str, Any]
    input_publication_ids: tuple[str, ...]
    input_source_version_ids: tuple[str, ...]
    input_entity_ids: tuple[str, ...]
    result_checksum: str = Field(min_length=64, max_length=64)
    result_summary: str = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_stable_identity(self) -> DeterministicDerivationRecord:
        expected_id = stable_id(
            "derivation",
            self.publication_id,
            self.temporal_domain_id,
            self.procedure_id,
            self.procedure_checksum,
            _canonical_json(self.normalized_parameters),
            _canonical_json(list(self.input_publication_ids)),
            _canonical_json(list(self.input_source_version_ids)),
            _canonical_json(list(self.input_entity_ids)),
            self.result_checksum,
        )
        if self.derivation_id != expected_id:
            raise ValueError("derivation identity does not match inputs and result")
        if len(set(self.input_source_version_ids)) != len(
            self.input_source_version_ids
        ):
            raise ValueError("derivation source inputs must be unique")
        return self


class KnowledgePublicationPackage(StrictModel):
    """All general-spine rows accepted for one atomic root publication."""

    root: KnowledgeRootRecord
    publication: KnowledgePublicationRecord
    publication_sources: tuple[PublicationSourceMembership, ...]
    source_anchors: tuple[SourceAnchorRecord, ...]
    facts: tuple[SemanticFactRecord, ...]
    fact_memberships: tuple[PublicationFactMembership, ...]
    evidence_links: tuple[PublicationEvidenceLink, ...]
    derivations: tuple[DeterministicDerivationRecord, ...] = ()

    @model_validator(mode="after")
    def _validate_publication_scope(self) -> KnowledgePublicationPackage:
        publication = self.publication
        if self.root.root_id != publication.root_id:
            raise ValueError("knowledge root and publication identities differ")
        if self.root.active_publication_id != publication.publication_id:
            raise ValueError("knowledge root does not activate this publication")
        if self.root.temporal_domain_id != publication.temporal_domain_id:
            raise ValueError("knowledge root and publication temporal domain differ")

        source_ids: set[str] = set()
        primary_source_ids: list[str] = []
        membership_ids: set[str] = set()
        for membership in self.publication_sources:
            if membership.publication_id != publication.publication_id:
                raise ValueError("source membership is outside the publication")
            if membership.membership_id in membership_ids:
                raise ValueError("publication source memberships must be unique")
            membership_ids.add(membership.membership_id)
            if membership.source_version_id in source_ids:
                raise ValueError("source versions must be unique within a publication")
            source_ids.add(membership.source_version_id)
            if membership.source_role == "primary":
                primary_source_ids.append(membership.source_version_id)
        if primary_source_ids != [publication.primary_source_version_id]:
            raise ValueError("publication requires exactly its declared primary source")

        anchors_by_id: dict[str, SourceAnchorRecord] = {}
        for anchor in self.source_anchors:
            if anchor.source_anchor_id in anchors_by_id:
                raise ValueError("source anchors must be unique")
            if anchor.source_version_id not in source_ids:
                raise ValueError("source anchor is outside the publication")
            anchors_by_id[anchor.source_anchor_id] = anchor

        facts_by_id = {fact.fact_id: fact for fact in self.facts}
        if len(facts_by_id) != len(self.facts):
            raise ValueError("semantic facts must be unique within a publication")
        member_fact_ids: set[str] = set()
        fact_membership_ids: set[str] = set()
        for membership in self.fact_memberships:
            if membership.publication_id != publication.publication_id:
                raise ValueError("fact membership is outside the publication")
            if membership.membership_id in fact_membership_ids:
                raise ValueError("fact memberships must be unique")
            fact_membership_ids.add(membership.membership_id)
            if membership.fact_id not in facts_by_id:
                raise ValueError("fact membership references an unknown fact")
            member_fact_ids.add(membership.fact_id)
        if member_fact_ids != set(facts_by_id):
            raise ValueError("every publication fact requires one membership")

        derivations_by_id = {
            derivation.derivation_id: derivation for derivation in self.derivations
        }
        if len(derivations_by_id) != len(self.derivations):
            raise ValueError("derivations must be unique within a publication")
        for derivation in self.derivations:
            if derivation.publication_id != publication.publication_id:
                raise ValueError("derivation is outside the publication")
            if derivation.temporal_domain_id != publication.temporal_domain_id:
                raise ValueError("derivation temporal domain differs from publication")
            if not set(derivation.input_source_version_ids).issubset(source_ids):
                raise ValueError("derivation source input is outside the publication")

        evidence_ids: set[str] = set()
        evidenced_fact_ids: set[str] = set()
        anchored_fact_ids: set[str] = set()
        for link in self.evidence_links:
            if link.publication_id != publication.publication_id:
                raise ValueError("evidence link is outside the publication")
            if link.evidence_link_id in evidence_ids:
                raise ValueError("evidence links must be unique")
            evidence_ids.add(link.evidence_link_id)
            if link.source_version_id not in source_ids:
                raise ValueError("evidence source is outside the publication")
            if link.source_anchor_id is not None:
                anchor = anchors_by_id.get(link.source_anchor_id)
                if anchor is None:
                    raise ValueError("evidence link references an unknown source anchor")
                if anchor.source_version_id != link.source_version_id:
                    raise ValueError("evidence anchor and source version differ")
            if link.owner_kind == "fact":
                if link.owner_id not in facts_by_id:
                    raise ValueError("evidence link references an unknown fact")
                evidenced_fact_ids.add(link.owner_id)
                if link.source_anchor_id is not None:
                    anchored_fact_ids.add(link.owner_id)
            if (
                link.owner_kind == "derivation"
                and link.owner_id not in derivations_by_id
            ):
                raise ValueError("evidence link references an unknown derivation")
        if evidenced_fact_ids != set(facts_by_id):
            raise ValueError("every publication fact requires evidence")
        source_text_fact_ids = {
            fact.fact_id
            for fact in self.facts
            if fact.evidence_mode == "source_text"
        }
        if not source_text_fact_ids.issubset(anchored_fact_ids):
            raise ValueError(
                "source-text facts require exact anchored evidence"
            )
        return self


class KnowledgePublicationBatch(StrictModel):
    """A batch of independently publishable semantic-root partitions."""

    packages: tuple[KnowledgePublicationPackage, ...]

    @model_validator(mode="after")
    def _validate_unique_partitions(self) -> KnowledgePublicationBatch:
        root_ids = [package.root.root_id for package in self.packages]
        if len(root_ids) != len(set(root_ids)):
            raise ValueError("knowledge publication batch requires unique root IDs")
        publication_ids = [
            package.publication.publication_id for package in self.packages
        ]
        if len(publication_ids) != len(set(publication_ids)):
            raise ValueError("knowledge publication batch requires unique publications")
        return self
