# LLM-Based Review Protocol

This project does not use human reviewers for the current thesis hardening
workflow. Review-dependent artifacts are therefore reported as model-based
review, LLM-assisted review, or configured-model review. They are not human
manual review, external aviation expert review, expert gold labels, or
operational certification.

## Purpose

The model-based review layer uses the configured LLM reviewer as a scalable way
to find likely benchmark, evidence, KG, graph-path, and answer-quality problems.
When `MODEL_NAME=Codex GPT-5.5`, reports identify the reviewer as Codex GPT-5.5.
Otherwise reports record the exact configured model identifier. This keeps the
workflow reproducible and avoids claiming a reviewer model that was not used.

LLM review can support:

- benchmark wording quality review;
- answerability review;
- evidence-support review;
- triple semantic review;
- graph path relevance review;
- answer faithfulness, correctness, citation, and abstention review.

LLM review cannot support:

- external expert certification;
- legal or operational aviation authority;
- proof of aviation-domain correctness;
- flight readiness;
- replacement of POH/AFM, approved checklists, ATC, instructor guidance,
  regulations, or pilot judgment.

## Required Metadata

Every LLM review item must include:

- `reviewer_type = "llm_judge"`
- `reviewer_model`
- `prompt_version`
- `input_hash`
- `review_run_id`
- `temperature`
- `human_review = false`
- `external_expert_certified = false`
- `aviation_expert_certified = false`
- `review_status`

The normal completed status is `llm_reviewed_not_human_certified`. If the LLM
cannot be called or the response is not schema-valid, the item is kept as
`llm_review_not_run`.

## Review Method

Review prompts use structured JSON output and explicit rubrics. Each item is
judged only from the supplied source fields, such as question text, reference
answer, evidence spans, retrieved chunks, KG triples, or graph paths.

Default review uses two role prompts when possible:

- `strict_evidence_reviewer`
- `skeptical_aviation_boundary_reviewer`

An optional third role, `retrieval_system_reviewer`, may be used for retrieval
diagnostics. The same model can be reused across roles, but the report must make
clear that this is role-based consistency checking, not independent human
review.

## Uncertainty And Disagreement

Uncertain decisions remain visible. Reports include uncertainty flags,
recommended actions, and consistency checks. When two role passes disagree, the
item is not safe for strong claims. When only one pass is available,
`consistency_not_measured = true` and the report must not claim high reliability.

Items may still be marked `requires_human_review = true` if a model judge
believes expert review would be needed. Because this project does not use human
reviewers, such items remain unsuitable for strong human-verified or
expert-certified claims.

## Bias And Reliability Limits

LLM judges can reward fluent wording, miss subtle source-evidence gaps, or
overstate confidence. They can also be sensitive to prompt wording, context
selection, and model version. For that reason, deterministic validation,
retrieval metrics, heuristic diagnostics, and LLM judge metrics stay separate.
No mixed overall score is created.
