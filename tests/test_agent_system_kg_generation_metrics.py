from __future__ import annotations

from test_agent_system_kg_generation_publication import _proposal, _task

from aviation_agentic_ai.agent_system.kg_generation import (
    CandidateFactGenerationResult,
)
from aviation_agentic_ai.agent_system.kg_generation_metrics import (
    evaluate_generation_results,
)
from aviation_agentic_ai.agent_system.kg_generation_validation import (
    validate_and_prepare_generated_publication,
)


def test_metrics_report_ontology_and_evidence_compliance() -> None:
    task, source_version, profiles, source_version_id = _task()
    proposal = _proposal()
    publication = validate_and_prepare_generated_publication(
        task=task,
        proposal=proposal,
        profile_registry=profiles,
        source_versions=(source_version,),
        primary_source_version_id=source_version_id,
    )

    metrics = evaluate_generation_results(
        tasks=(task,),
        generation_results=(
            CandidateFactGenerationResult(
                status="accepted",
                proposal=proposal,
                model_calls=(),
            ),
        ),
        publication_results=(publication,),
    )

    assert metrics.mode == "offline_software_test"
    assert metrics.proposal_count == 1
    assert metrics.candidate_fact_count == 1
    assert metrics.accepted_semantic_fact_count == 1
    assert metrics.ontology_term_compliance_rate == 1.0
    assert metrics.evidence_anchor_coverage_rate == 1.0
    assert metrics.blocked_result_count == 0


def test_metrics_preserve_abstention_and_detect_duplicate_semantics() -> None:
    task, _, _, _ = _task()
    proposal = _proposal().model_copy(
        update={
            "facts": (_proposal().facts[0], _proposal().facts[0]),
            "status": "accepted",
        }
    )

    metrics = evaluate_generation_results(
        tasks=(task, task),
        generation_results=(
            CandidateFactGenerationResult(
                status="accepted",
                proposal=proposal,
                model_calls=(),
            ),
            CandidateFactGenerationResult(
                status="abstained",
                proposal=None,
                model_calls=(),
            ),
        ),
    )

    assert metrics.abstained_proposal_count == 1
    assert metrics.duplicate_semantic_fact_count == 1
    assert metrics.candidate_fact_count == 2
    assert metrics.accepted_semantic_fact_count == 0


def test_blocked_publication_is_not_counted_as_accepted() -> None:
    task, source_version, profiles, source_version_id = _task(content="different")
    proposal = _proposal()
    publication = validate_and_prepare_generated_publication(
        task=task,
        proposal=proposal,
        profile_registry=profiles,
        source_versions=(source_version,),
        primary_source_version_id=source_version_id,
    )

    metrics = evaluate_generation_results(
        tasks=(task,),
        generation_results=(
            CandidateFactGenerationResult(
                status="accepted",
                proposal=proposal,
                model_calls=(),
            ),
        ),
        publication_results=(publication,),
    )

    assert publication.status == "blocked"
    assert metrics.blocked_result_count == 1
    assert metrics.accepted_semantic_fact_count == 0

