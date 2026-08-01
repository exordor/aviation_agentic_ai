"""Deterministic diagnostics for ontology-grounded fact generation.

These metrics describe contract and publication behaviour.  They are an
``offline_software_test`` diagnostic, not a claim about language-model
quality.  In particular, a proposal can be structurally compliant while a
real model may still be poor at choosing the proposal in the first place.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import Field

from aviation_agentic_ai.agent_system.contracts import StrictModel
from aviation_agentic_ai.agent_system.kg_generation import (
    CandidateFactGenerationResult,
)
from aviation_agentic_ai.agent_system.kg_generation_contracts import (
    CandidateFact,
    CandidateFactProposal,
    OntologyGenerationTask,
)
from aviation_agentic_ai.agent_system.kg_generation_validation import (
    GeneratedFactPublication,
)


class KGGenerationMetrics(StrictModel):
    """Small, serialisable report for one generation/publication evaluation."""

    mode: Literal["offline_software_test"] = "offline_software_test"
    task_count: int = Field(ge=0)
    proposal_count: int = Field(ge=0)
    accepted_proposal_count: int = Field(ge=0)
    abstained_proposal_count: int = Field(ge=0)
    blocked_result_count: int = Field(ge=0)
    candidate_fact_count: int = Field(ge=0)
    accepted_semantic_fact_count: int = Field(ge=0)
    ontology_term_compliance_rate: float = Field(ge=0.0, le=1.0)
    evidence_anchor_coverage_rate: float = Field(ge=0.0, le=1.0)
    duplicate_semantic_fact_count: int = Field(ge=0)
    profile_gap_count: int = Field(ge=0)
    idempotent_replay: bool | None = None


def _semantic_key(fact: CandidateFact) -> tuple[str, ...]:
    """Return identity without provenance, so evidence can merge one-to-many."""

    return (
        fact.predicate_iri,
        fact.object_kind,
        fact.object_value,
        fact.object_class_iri or "",
        fact.datatype_iri or "",
    )


def _candidate_compliance(
    task: OntologyGenerationTask,
    proposal: CandidateFactProposal,
) -> tuple[int, int]:
    """Count candidate rows that satisfy the sealed task ontology contract."""

    compliant = 0
    for fact in proposal.facts:
        one_fact = CandidateFactProposal(status="accepted", facts=(fact,))
        try:
            one_fact.validate_against(task)
        except ValueError:
            continue
        compliant += 1
    return compliant, len(proposal.facts)


def _publication_has_evidence(
    publication: GeneratedFactPublication,
    fact_id: str,
) -> bool:
    package = publication.package
    if package is None:
        return False
    return any(link.owner_id == fact_id for link in package.evidence_links)


def evaluate_generation_results(
    *,
    tasks: Sequence[OntologyGenerationTask],
    generation_results: Sequence[CandidateFactGenerationResult],
    publication_results: Sequence[GeneratedFactPublication] | None = None,
) -> KGGenerationMetrics:
    """Summarise generation and publication results without model calls.

    ``tasks`` and ``generation_results`` are positional by task.  A provided
    publication result must use the same ordering.  The function intentionally
    treats a blocked publication as blocked even when its preceding model
    response was syntactically accepted.
    """

    if len(tasks) != len(generation_results):
        raise ValueError("tasks and generation_results must have equal length")
    if publication_results is not None and len(publication_results) != len(tasks):
        raise ValueError("publication_results must match task count")

    proposal_count = 0
    accepted_proposal_count = 0
    abstained_proposal_count = 0
    blocked_result_count = 0
    candidate_fact_count = 0
    accepted_semantic_fact_count = 0
    compliant_fact_count = 0
    profile_gap_count = 0
    evidence_fact_count = 0
    candidate_semantic_keys: list[tuple[str, tuple[str, ...]]] = []

    for index, (task, generation) in enumerate(zip(tasks, generation_results)):
        proposal = generation.proposal
        if proposal is not None:
            proposal_count += 1
            if generation.status == "accepted" and proposal.status == "accepted":
                accepted_proposal_count += 1
            if generation.status == "abstained" or proposal.status == "abstained":
                abstained_proposal_count += 1
            candidate_fact_count += len(proposal.facts)
            compliant, total = _candidate_compliance(task, proposal)
            compliant_fact_count += compliant
            # Keep root identity in the duplicate key so separate roots do not
            # become false duplicates merely because they use the same term.
            candidate_semantic_keys.extend(
                (task.root_id, _semantic_key(fact)) for fact in proposal.facts
            )
            profile_gap_count += len(proposal.profile_gaps)
        elif generation.status == "abstained":
            abstained_proposal_count += 1

        publication = (
            publication_results[index] if publication_results is not None else None
        )
        if generation.status == "blocked" or (
            publication is not None and publication.status == "blocked"
        ):
            blocked_result_count += 1
        if publication is not None and publication.status == "ok":
            accepted_semantic_fact_count += len(publication.accepted_facts)
            for fact in publication.accepted_facts:
                if _publication_has_evidence(publication, fact.fact_id):
                    evidence_fact_count += 1

    unique_semantic_keys = set(candidate_semantic_keys)
    duplicate_count = len(candidate_semantic_keys) - len(unique_semantic_keys)
    ontology_rate = (
        compliant_fact_count / candidate_fact_count
        if candidate_fact_count
        else 0.0
    )
    evidence_rate = (
        evidence_fact_count / accepted_semantic_fact_count
        if accepted_semantic_fact_count
        else 0.0
    )
    return KGGenerationMetrics(
        task_count=len(tasks),
        proposal_count=proposal_count,
        accepted_proposal_count=accepted_proposal_count,
        abstained_proposal_count=abstained_proposal_count,
        blocked_result_count=blocked_result_count,
        candidate_fact_count=candidate_fact_count,
        accepted_semantic_fact_count=accepted_semantic_fact_count,
        ontology_term_compliance_rate=ontology_rate,
        evidence_anchor_coverage_rate=evidence_rate,
        duplicate_semantic_fact_count=duplicate_count,
        profile_gap_count=profile_gap_count,
    )


__all__ = ["KGGenerationMetrics", "evaluate_generation_results"]
