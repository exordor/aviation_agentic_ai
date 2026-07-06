# Research Questions

> Migrated on 2026-07-05 from `docs/research_mainline.md`, `docs/thesis_positioning.md`, and `docs/master_project_scope_lock.md`. The source files (now archived under `docs/archive/governance_era/`) were migrated on 2026-07-05.

The project keeps exactly four research questions. Any additional question should be folded into one of these four, or moved to future work.

## RQ1: Schema-constrained extraction

### Description

Can schema-constrained LLM extraction produce valid and evidence-linked event records from ATCSCC advisories?

### Motivation

ATCSCC advisories are a narrow but useful case study for evidence-grounded extraction because many facts are visible in the source text and can be checked against evidence spans, so the question is whether a schema constraint can turn that visibility into valid, evidence-linked event records.

### Related Hypotheses

- H1 (schema guidance reduces structural drift after canonicalization)
- H5 (hybrid backbone + enrichment improves selected semantic predicates)

### Related Experiments

- Extraction layer: S0/S1/S1b/S2/S3/S4 over the frozen 100-record reviewed gold sample.
- Evidence: `reports/stages/nasa_atmonto_formal_experiment_scoring.md`, `reports/stages/nasa_atmonto_prediction_output_validation.md`, `reports/stages/nasa_atmonto_cq_evaluation.md`.

### Current Evidence

The schema-constrained or validator-gated system improves valid evidence-linked facts over weakly constrained LLM output, while deterministic fields remain protected.

### Status

active

## RQ2: Agentic validation-refinement

### Description

Does an agentic validation-refinement loop reduce schema violations and unsupported relations?

### Motivation

A validator/refiner/critic loop makes repair and rejection of candidate facts auditable before graph insertion, so the question is whether that loop actually reduces schema violations and unsupported relations rather than silently passing them through.

### Related Hypotheses

- H2 (validator/repair improves valid yield)

### Related Experiments

- Agentic loop: extractor / validator / refiner / critic over ATCSCC candidate facts; independent and live S5/S6 runs.
- Evidence: `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.md`, `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md`, `reports/stages/nasa_atmonto_agentic_loop.md`.

### Current Evidence

The loop produces auditable repair/rejection decisions and reduces specific schema or support failures without silently overwriting protected deterministic facts.

### Status

active

## RQ3: KG-RAG grounding

### Description

Does KG-RAG improve evidence grounding and citation quality compared with vector-only RAG?

### Motivation

Graph evidence is useful only when it improves source-bounded answer sets, evidence traceability, citation behavior, and failure diagnosis, so the question is whether KG-RAG beats vector-only RAG on those dimensions rather than on raw Recall@k.

### Related Hypotheses

- H3 (KG-RAG improves source-bounded grounding, answer-set quality, citation behavior on relation-oriented questions; vector-only can remain sufficient for simple source-local questions)

### Related Experiments

- Retrieval and answer generation: source-only, vector RAG, graph-only, token-matched GraphRAG, routed/hybrid KG-RAG.
- Evidence: `reports/stages/nasa_atmonto_s7_retrieval.md`, `reports/stages/nasa_atmonto_s7_graph_health.md`, `reports/stages/nasa_atmonto_s7_llm_answer_generation.md`.

### Current Evidence

KG/hybrid modes improve at least some relation-oriented grounding or citation diagnostics while vector-only remains a fair baseline for source-local questions.

### Status

active

## RQ4: Failure boundary

### Description

What failure types remain, and where does human review remain necessary?

### Motivation

The thesis must keep automated diagnostics separate from human or expert review and enumerate the failure types that remain unresolved, so the question is which failure categories survive the pipeline and which of them still require human adjudication.

### Related Hypotheses

- H4 (failure analysis separates extraction errors, profile/gold-boundary gaps, retrieval context errors, answer overreach, human-review cases)
- H6 (rejection triage produces actionable engineering decisions)

### Related Experiments

- Reviewer-defense, answer-review, profile-decision, claim-safety audits.
- Evidence: `reports/stages/nasa_atmonto_reviewer_defense_audit.md`, `reports/stages/nasa_atmonto_sota_goal_audit.md`, `reports/stages/nasa_atmonto_s7_profile_decision.md`.

### Current Evidence

The thesis explicitly separates automated diagnostics from human or expert review and lists remaining failure types with claim impact.

### Status

active
