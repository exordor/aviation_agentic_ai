# Master Project Scope Lock

This document freezes the project scope at master-project scale. It prevents
research support work from expanding into parallel subprojects.

## Locked Project Outcome

The project outcome is one bounded thesis-grade system study:

**Evidence-Grounded Schema-Constrained Agentic KG-RAG for FAA ATCSCC
Advisories.**

The thesis studies how a lightweight application schema constrains LLM
extraction from retrospective FAA ATCSCC advisories, how validator/refiner/critic
loops change extraction quality, and whether the resulting advisory event graph
improves source-grounded question answering and citation diagnostics.

The ontology/profile is an engineering constraint. It is not the research object.

## Single-Sentence Contribution

This project builds and evaluates a schema-constrained, evidence-linked
Agentic KG-RAG pipeline that extracts advisory-event facts from FAA ATCSCC
notices, validates and repairs candidate facts before graph insertion, and uses
the resulting event graph for source-bounded question answering.

## Minimum Deliverable Set

The final master project needs only the following deliverables.

| Deliverable | Purpose | Canonical evidence |
|---|---|---|
| Frozen ATCSCC data profile | Defines the retrospective source family and source format. | `reports/stages/atcscc_data_format_and_processing_flow.md` |
| Lightweight ATCSCC schema/profile | Defines allowed event fields, predicates, and profile gaps. | `reports/stages/atcscc_ontology_profile_overview.md` |
| Schema-constrained extraction experiment | Tests rule, LLM, schema, repair, and hybrid extraction variants. | `reports/stages/nasa_atmonto_formal_experiment_scoring.md` |
| Agentic validation/refinement loop | Tests whether validator/refiner/critic steps reduce schema and evidence failures. | `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md` |
| KG-RAG answer-generation comparison | Tests vector, graph, and hybrid/routed retrieval for source-grounded answers. | `reports/stages/nasa_atmonto_s7_retrieval.md`, `reports/stages/nasa_atmonto_s7_llm_answer_generation.md` |
| Failure and claim-safety audit | Defines what remains unresolved and where human review is required. | `reports/stages/nasa_atmonto_reviewer_defense_audit.md`, `reports/stages/nasa_atmonto_sota_goal_audit.md` |
| Thesis synthesis | Turns the evidence into the final research story. | `docs/research_mainline.md`, `docs/thesis_positioning.md`, `reports/stages/nasa_atmonto_experiment_chapter_draft.md` |

If a proposed task does not strengthen one of these deliverables, it should be
deferred.

## Non-Goals

The project must not expand into these tasks unless the thesis scope is
explicitly reopened.

- A full aviation ontology thesis.
- A complete NASA ATMONTO correctness or completeness evaluation.
- A live ATC or flight-decision support system.
- A universal GraphRAG benchmark.
- A general ontology-building platform.
- A large systematic literature review.
- A new database project beyond the existing bounded artifacts.
- A broad multi-domain transfer study.
- A production dashboard.
- A separate paper-gallery or PDF-mining product.
- A new data-source integration campaign.
- A large fine-tuning or model-training project.

These topics can appear in related work, limitations, or future work, but they
should not create new core implementation tracks.

## How External Papers Are Used

External papers have three allowed roles:

1. **Method justification**: explain why schema-guided extraction, validation,
   entity alignment, or KG-RAG comparison is reasonable.
2. **Figure and table inspiration**: improve the thesis method figure, schema
   figure, span-to-fact example, alignment figure, or result table.
3. **Evaluation design**: refine metrics such as schema validity, evidence
   support, citation quality, model/cost trade-off, and failure taxonomy.

External papers must not create a new experiment unless the experiment directly
tests one of the locked RQs in `docs/research_mainline.md`.

## Accepted Research Questions

The project keeps exactly four research questions.

1. Can schema-constrained LLM extraction produce valid and evidence-linked event
   records from ATCSCC advisories?
2. Does an agentic validation-refinement loop reduce schema violations and
   unsupported relations?
3. Does KG-RAG improve evidence grounding and citation quality compared with
   vector-only RAG?
4. What failure types remain, and where does human review remain necessary?

Any additional question should be folded into one of these four, or moved to
future work.

## Metric Boundary

The project reports layered metrics, not one overall score.

- Extraction layer: JSON validity, schema validity, structural acceptance,
  precision, recall, F1.
- Evidence layer: evidence-span coverage, unsupported relation rate,
  provenance completeness.
- Agentic loop layer: repair success, rejection reasons, violation reduction,
  post-loop quality.
- Retrieval/answer layer: answer-set F1, target-source hit rate, citation
  precision/recall, evidence faithfulness, unsupported answer rate.
- Boundary layer: profile gaps, abstention correctness, human-review status,
  remaining failure categories.

This metric boundary prevents the project from turning into an open-ended
benchmark.

## Figure Boundary

The thesis needs a small number of high-value figures only.

| Figure | Purpose |
|---|---|
| System overview | Show source, schema, agentic extraction, event graph, KG-RAG, and evaluation. |
| ATCSCC source-to-fact example | Show one advisory span mapped to event facts and evidence ids. |
| Schema/profile slice | Show the lightweight application schema, not full ATMONTO. |
| Agentic loop | Show extractor, validator, refiner, critic, and rejection/repair artifacts. |
| Results summary | Show layered metrics and failure categories. |

Paper figure galleries and PDF extraction assets are research support tools, not
final deliverables.

## New-Idea Intake Rule

When a new idea appears, classify it before doing work.

| Classification | Action |
|---|---|
| Strengthens an existing locked deliverable | Implement only the smallest required change. |
| Improves writing, figure clarity, or claim safety | Add to the relevant thesis/report document. |
| Requires new data, new benchmark, new platform, or new dashboard | Move to future work. |
| Changes the research question | Reject unless the scope lock is explicitly reopened. |
| Only useful for exploration | Keep as ignored local notes or a short literature note. |

Default decision: defer.

## Claim Boundary

Safe claims:

- The project implements a bounded schema-constrained Agentic KG-RAG prototype
  over retrospective FAA ATCSCC advisories.
- The schema/profile constrains accepted advisory-event facts.
- Accepted facts preserve source ids and evidence spans.
- The agentic loop provides auditable repair and rejection decisions.
- KG-RAG can improve selected grounding and citation diagnostics on the current
  source-bounded benchmark.
- Remaining failures and human-review requirements are explicitly categorized.

Unsafe claims:

- The project builds a complete aviation ontology.
- NASA ATMONTO is complete ground truth for ATCSCC.
- GraphRAG universally outperforms vector retrieval.
- Automated agents replace human review.
- The system is operationally safe for live ATC or flight decisions.
- The method is proven domain-general.

## Stop Rule

The project is ready to write up when these are true:

1. The frozen ATCSCC data, schema/profile, extraction results, agentic loop,
   KG-RAG results, and failure audit are all linked from
   `docs/documentation_map.md`.
2. `docs/research_mainline.md` and `docs/thesis_positioning.md` tell the same
   story.
3. Every major claim in the thesis draft maps to one tracked evidence artifact.
4. Remaining gaps are listed as limitations or future work rather than becoming
   new experiments.
5. Verification commands pass for the final code and documentation state.

## Immediate Operating Rule

From this point, do not add a new workstream by default. Convert new material
into one of:

- a sentence in related work;
- a limitation;
- a future-work bullet;
- a figure-design improvement;
- a metric clarification;
- a small patch to an existing experiment artifact.

If it cannot fit into one of those forms, it is outside the master project.
