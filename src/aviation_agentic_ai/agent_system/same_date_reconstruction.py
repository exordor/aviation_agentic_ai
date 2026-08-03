"""Same-date reconstruction comparison for the public ATMONTO sample.

This module is an evaluation boundary, not a second knowledge store.  It
compares semantic fact identity produced by an ontology-constrained
reconstruction with the NASA public ABox reference for the same date and
geographic scope.  Provenance is deliberately excluded from fact identity;
provenance remains part of the publication and is evaluated separately.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from aviation_agentic_ai.agent_system.atmonto_sample_sources import (
    ATMONTO_PUBLIC_SAMPLE_DATE,
    ATMONTO_PUBLIC_SAMPLE_AIRPORT_CODES,
)
from aviation_agentic_ai.agent_system.contracts import StrictModel, ValidatedFact
from aviation_agentic_ai.agent_system.kg_generation_validation import (
    GeneratedFactPublication,
)


class SameDateReconstructionScope(StrictModel):
    """Frozen scope for reconstruction against the public NASA ABox."""

    experiment_id: str = Field(min_length=1)
    baseline_id: str = Field(min_length=1)
    sample_date: date
    airport_codes: tuple[str, ...] = Field(min_length=1)
    temporal_domain_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_public_baseline_scope(self) -> SameDateReconstructionScope:
        if self.sample_date != ATMONTO_PUBLIC_SAMPLE_DATE:
            raise ValueError(
                "same-date reconstruction must use the public baseline date "
                f"{ATMONTO_PUBLIC_SAMPLE_DATE.isoformat()}"
            )
        normalized = tuple(code.strip().upper() for code in self.airport_codes)
        if any(not code for code in normalized):
            raise ValueError("airport codes must not be empty")
        if len(set(normalized)) != len(normalized):
            raise ValueError("airport codes must be unique")
        if not set(normalized).issubset(ATMONTO_PUBLIC_SAMPLE_AIRPORT_CODES):
            raise ValueError(
                "same-date reconstruction airports must belong to the public "
                "baseline airport scope"
            )
        self.airport_codes = normalized
        return self


class SemanticFactSignature(StrictModel):
    """Provenance-independent identity used for baseline comparison."""

    subject_iri: str = Field(min_length=1)
    predicate_iri: str = Field(min_length=1)
    object_kind: Literal["iri", "literal"]
    object_value: str = Field(min_length=1)
    object_class_iri: str | None = None
    datatype_iri: str | None = None
    # Kept for report diagnostics only.  It is never part of ``semantic_key``.
    source_id: str | None = Field(default=None, min_length=1)

    def semantic_key(self) -> tuple[str, ...]:
        """Return fact identity without source or anchor provenance."""

        return (
            self.subject_iri,
            self.predicate_iri,
            self.object_kind,
            self.object_value,
            self.object_class_iri or "",
            self.datatype_iri or "",
        )

    @classmethod
    def from_validated_fact(cls, fact: ValidatedFact) -> SemanticFactSignature:
        """Adapt a formally published fact to the comparison signature."""

        return cls(
            subject_iri=fact.subject_iri,
            predicate_iri=fact.predicate_iri,
            object_kind=fact.object_kind,
            object_value=fact.object_value,
            object_class_iri=fact.object_class_iri,
            datatype_iri=fact.datatype_iri,
            source_id=fact.source_ids[0] if fact.source_ids else None,
        )


class SameDateReconstructionReport(StrictModel):
    """Comparison metrics for one same-date reconstruction run."""

    mode: Literal["same_date_reconstruction"] = "same_date_reconstruction"
    scope: SameDateReconstructionScope
    baseline_semantic_fact_count: int = Field(ge=0)
    reconstructed_semantic_fact_count: int = Field(ge=0)
    matched_fact_count: int = Field(ge=0)
    missing_fact_count: int = Field(ge=0)
    extra_fact_count: int = Field(ge=0)
    baseline_predicate_count: int = Field(ge=0)
    reconstructed_predicate_count: int = Field(ge=0)
    matched_predicate_count: int = Field(ge=0)
    precision: float = Field(ge=0.0, le=1.0)
    recall: float = Field(ge=0.0, le=1.0)
    f1: float = Field(ge=0.0, le=1.0)
    predicate_recall: float = Field(ge=0.0, le=1.0)
    publication_count: int = Field(default=0, ge=0)
    accepted_publication_count: int = Field(default=0, ge=0)
    abstained_publication_count: int = Field(default=0, ge=0)
    blocked_publication_count: int = Field(default=0, ge=0)
    baseline_is_reference_only: bool = True


def _unique_keys(facts: Sequence[SemanticFactSignature]) -> set[tuple[str, ...]]:
    return {fact.semantic_key() for fact in facts}


def compare_same_date_reconstruction(
    *,
    scope: SameDateReconstructionScope,
    baseline_facts: Sequence[SemanticFactSignature],
    reconstructed_facts: Sequence[SemanticFactSignature],
) -> SameDateReconstructionReport:
    """Compare reconstructed semantic facts with the same-date baseline.

    The comparison is intentionally set-based and provenance-independent.  A
    fact supported by a different source or anchor still matches the baseline
    semantic fact; provenance and evidence support remain separate metrics.
    """

    baseline_keys = _unique_keys(baseline_facts)
    reconstructed_keys = _unique_keys(reconstructed_facts)
    matched = baseline_keys & reconstructed_keys
    missing = baseline_keys - reconstructed_keys
    extra = reconstructed_keys - baseline_keys

    baseline_predicates = {key[1] for key in baseline_keys}
    reconstructed_predicates = {key[1] for key in reconstructed_keys}
    matched_predicates = baseline_predicates & reconstructed_predicates

    precision = (
        len(matched) / len(reconstructed_keys) if reconstructed_keys else 0.0
    )
    recall = len(matched) / len(baseline_keys) if baseline_keys else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    predicate_recall = (
        len(matched_predicates) / len(baseline_predicates)
        if baseline_predicates
        else 0.0
    )

    return SameDateReconstructionReport(
        scope=scope,
        baseline_semantic_fact_count=len(baseline_keys),
        reconstructed_semantic_fact_count=len(reconstructed_keys),
        matched_fact_count=len(matched),
        missing_fact_count=len(missing),
        extra_fact_count=len(extra),
        baseline_predicate_count=len(baseline_predicates),
        reconstructed_predicate_count=len(reconstructed_predicates),
        matched_predicate_count=len(matched_predicates),
        precision=precision,
        recall=recall,
        f1=f1,
        predicate_recall=predicate_recall,
    )


def compare_published_reconstruction(
    *,
    scope: SameDateReconstructionScope,
    baseline_facts: Sequence[SemanticFactSignature],
    publications: Sequence[GeneratedFactPublication],
) -> SameDateReconstructionReport:
    """Compare accepted facts from the existing publication bridge.

    This function deliberately consumes ``GeneratedFactPublication`` rather
    than writing a store.  The caller can therefore run the same comparison
    against a staged reconstruction while keeping the canonical store and the
    NASA reference baseline separate.
    """

    reconstructed_facts = tuple(
        fact
        for publication in publications
        if publication.status == "ok"
        for fact in publication.accepted_facts
    )
    report = compare_same_date_reconstruction(
        scope=scope,
        baseline_facts=baseline_facts,
        reconstructed_facts=signatures_from_validated_facts(reconstructed_facts),
    )
    accepted = sum(publication.status == "ok" for publication in publications)
    abstained = sum(
        publication.status == "abstained" for publication in publications
    )
    blocked = sum(publication.status == "blocked" for publication in publications)
    return report.model_copy(
        update={
            "publication_count": len(publications),
            "accepted_publication_count": accepted,
            "abstained_publication_count": abstained,
            "blocked_publication_count": blocked,
        }
    )


def signatures_from_validated_facts(
    facts: Sequence[ValidatedFact],
) -> tuple[SemanticFactSignature, ...]:
    """Convert published facts without changing their semantic identity."""

    return tuple(SemanticFactSignature.from_validated_fact(fact) for fact in facts)


__all__ = [
    "SameDateReconstructionReport",
    "SameDateReconstructionScope",
    "SemanticFactSignature",
    "compare_same_date_reconstruction",
    "compare_published_reconstruction",
    "signatures_from_validated_facts",
]
