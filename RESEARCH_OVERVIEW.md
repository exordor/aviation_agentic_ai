# Research Overview

> Migrated on 2026-07-05 from `docs/thesis_positioning.md`, `docs/research_mainline.md`, and `docs/master_project_scope_lock.md` as part of the research-governance refactor (spec `docs/superpowers/specs/2026-07-05-research-governance-refactor-design.md`). Sources preserved under `docs/archive/governance_era/`.

## Research Area

- Schema-constrained, evidence-grounded information extraction.
- Agentic validation/refinement loops for KG construction.
- Source-bounded KG-RAG question answering.
- Retrospective FAA ATCSCC advisory analysis.

## Problem Statement

The project studies evidence-grounded question answering over retrospective FAA
ATCSCC advisories. ATCSCC advisories are semi-structured operational notices:
they contain identifiers, affected NAS elements, route or airport constraints,
effective time windows, causes, and free-text operational context. The research
problem is not to build a complete aviation ontology. The research problem is to
extract advisory-event knowledge with explicit schema constraints and evidence
spans, then evaluate whether that structured graph improves grounded question
answering.

The prototype therefore treats the ontology/profile as an engineering
constraint. The main method is schema-constrained, evidence-grounded Agentic
KG-RAG.

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

## Revised Thesis Claim

This thesis investigates a retrospective and source-bounded claim: for FAA
ATCSCC advisories, a lightweight NASA ATMONTO-derived application schema can
constrain LLM extraction of advisory events, support agentic
validation/refinement, and provide an inspectable advisory event graph for
KG-RAG question answering. The system is evaluated with layered metrics:
schema-valid extraction, evidence-linked relation correctness on reviewed
subsets, repair/critic behavior, retrieval and answer quality, citation quality,
and failure/human-review boundaries are reported separately.

The thesis does not claim that the ATCSCC schema is a complete aviation
ontology, that GraphRAG universally improves retrieval, or that the system is
usable for live ATC decision support.

## Thesis Story

FAA ATCSCC advisories are public, semi-structured operational texts. They
describe traffic management initiatives, affected NAS elements, time windows,
causes, statuses, and route or airport constraints. They are a narrow but useful
case study for evidence-grounded information extraction because many facts are
visible in the source text and can be checked against evidence spans.

The project uses NASA ATMONTO-derived terms as a lightweight schema/profile.
That profile is a guardrail, not the research object. It defines what an
accepted advisory-event record may contain, and it makes validation, rejection,
repair, and evidence tracing explicit.

The research contribution is a bounded method:

```text
retrospective advisory text
  -> schema-constrained extraction
  -> agentic validation/refinement/critic loop
  -> advisory event graph with evidence spans
  -> vector / graph / routed KG-RAG
  -> source-grounded answers and failure analysis
```

## Research Scope

### In scope

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

### Not in scope (Non-Goals)

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

## Contributions

- A lightweight ATCSCC application schema/profile derived from NASA ATMONTO
  terms and restricted to the advisory-event extraction task.
- An advisory event graph with source IDs and evidence spans for extracted
  facts.
- An agentic extraction loop with extractor, validator, refiner, and critic
  roles that records repair and rejection outcomes.
- A reproducible vector, graph, and hybrid KG-RAG evaluation pipeline over
  retrospective ATCSCC advisories.
- A layered evaluation and claim-boundary protocol that separates schema
  validity, evidence support, answer quality, and human-review requirements.

## Evaluation Philosophy

The thesis should report mixed or negative retrieval results directly. KG-RAG
does not need to win every Recall@k comparison to be useful. The defensible
claim is narrower: graph evidence is useful when it improves source-bounded
answer sets, evidence traceability, citation behavior, and failure diagnosis.

| Layer | Metrics | Purpose |
| --- | --- | --- |
| Schema-constrained extraction | schema validity, structural acceptance rate, rejected fact count, repaired fact count | Measure whether generated event records obey the application schema before graph insertion. |
| Evidence support | evidence-span coverage, unsupported relation rate, provenance completeness, reviewed-subset precision/recall/F1 | Measure whether accepted facts can be traced to advisory text. |
| Agentic loop behavior | violation reduction, repair success, critic rejection count, post-loop extraction F1 | Measure whether validation/refinement improves extraction quality. |
| Retrieval and KG-RAG answer quality | answer-set F1, target-source hit rate, citation precision/recall, evidence faithfulness | Measure whether vector, graph, and hybrid modes support grounded answers. |
| Failure and human-review boundary | failure category counts, abstention correctness, profile/gold-boundary cases, human-review completion status | Measure what remains unresolved and which claims require review. |

The thesis must not collapse these layers into a single mixed overall score.
The full metric protocol is documented in `EXPERIMENTS.md` and can
be audited with `uv run aviation-ai report evaluation-protocol`. The full thesis
experiment sequence is documented in `EXPERIMENTS.md` and

## Claim Safety Matrix

| Claim | Current evidence | Supported strength | Safe wording | Unsafe wording to avoid |
| --- | --- | --- | --- | --- |
| Lightweight schema constrains advisory event extraction. | ATCSCC profile terms, schema validation, and prediction-output validation reports constrain accepted event fields. | strong | The application schema constrains which advisory event fields and relations can enter the graph. | The ontology fully models aviation knowledge. |
| Accepted facts preserve provenance. | KG and prediction validation reports check source IDs and evidence spans. | strong | Accepted facts carry source-bounded provenance checked by deterministic validation. | Every KG triple is semantically correct. |
| Agentic validation improves extraction quality. | S5/S6 reports record validator, refiner, critic, repair, and rejection behavior. | moderate | The agentic loop reduces specific schema and support failures in the current ATCSCC pipeline. | Autonomous agents construct a correct ontology. |
| KG-RAG improves grounded ATCSCC QA. | S7 retrieval, graph-health, and LLM answer-generation diagnostics report answer-set, citation, and target-source metrics. | moderate | KG-RAG improves some source-bounded grounding diagnostics on this benchmark. | GraphRAG is always more accurate than vector retrieval. |
| The system can answer operational ATC questions. | The advisory boundary limits the system to retrospective research diagnostics. | not supported | The system analyzes retrospective advisories and must not be used for live operational decisions. | The system can support operational flight or ATC decisions. |
| The benchmark is externally expert certified. | Current labels and diagnostics are project/thesis evidence with documented review gaps. | not supported | The benchmark is thesis-oriented and source-bounded, with explicit review limitations. | The benchmark is externally aviation-expert certified. |

## What The Thesis Can Claim

- The project implements a reproducible schema-constrained Agentic KG-RAG
  prototype over retrospective FAA ATCSCC advisories.
- The application schema constrains focused advisory-event extraction and
  supports deterministic validation.
- Accepted facts preserve source IDs and evidence spans at the artifact level.
- Agentic validation/refinement provides inspectable repair and rejection
  signals.
- KG-RAG adds structured evidence and citation diagnostics in the current
  source-bounded benchmark.
- Remaining failures and human-review requirements are explicitly categorized.

## What The Thesis Must Not Claim

- The ATCSCC application schema is a complete aviation ontology.
- NASA ATMONTO is treated as complete ground truth for ATCSCC advisories.
- GraphRAG universally improves Recall@k or answer accuracy.
- Automated diagnostics replace human or expert review.
- The benchmark is externally aviation-expert certified.
- The system is operationally safe for live ATC or flight decisions.

## Current Thesis-Usable Claims

- The ATCSCC application schema constrains which advisory event fields and
  relations can enter the graph.
- Accepted facts preserve source IDs and evidence spans at the artifact level.
- The agentic loop is useful as an auditable diagnostic and repair framework,
  even when deterministic extraction remains stronger for semi-structured
  advisories.
- KG-RAG adds structured evidence and citation diagnostics for source-bounded
  ATCSCC QA.
- Remaining failures can be categorized into extraction, retrieval, profile/gold
  boundary, answer-overreach, and human-review cases.

## Claims To Avoid

- The project builds a complete aviation ontology.
- NASA ATMONTO is complete ground truth for ATCSCC advisories.
- GraphRAG universally outperforms vector-only RAG.
- Automated review replaces human or expert review.
- The system is safe for live ATC or flight decisions.
- The method is proven domain-general.

## SOTA Positioning

The project should be positioned as a thesis-scale system study at the
intersection of four mature method areas rather than as a claim that ATCSCC
ontology research is itself a large SOTA field.

| SOTA area | What the thesis borrows | What the thesis contributes in this project |
| --- | --- | --- |
| Schema-guided / ontology-guided information extraction | Use a domain schema to constrain classes, predicates, values, and output contracts. | A source-native ATCSCC advisory-event profile with evidence-span requirements and profile-gap handling. |
| Knowledge-graph quality evaluation | Separate completeness, correctness, conformance, provenance, and error repair. | A layered metric protocol that reports schema validity, evidence support, extraction F1, retrieval quality, answer grounding, and review boundaries separately. |
| GraphRAG and citation-faithful QA | Compare vector, graph, hybrid, and routed retrieval instead of assuming graph retrieval is always better. | A source-bounded ATCSCC KG-RAG benchmark with answer-set, citation, unsupported-claim, and abstention diagnostics. |
| Multi-agent validation/refinement | Use role-separated extractor, validator, refiner, and critic loops. | An auditable agentic loop for extraction repair and rejection under hard schema and evidence gates. |

The safe novelty claim is therefore methodological integration under a bounded
source family: the thesis adapts schema-guided extraction, KG quality
evaluation, GraphRAG diagnostics, and multi-agent validation to retrospective
FAA ATCSCC advisories. It does not claim to invent a new general GraphRAG
algorithm, construct a complete aviation ontology, or prove domain-general
autonomy.

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

## Evidence Gaps Before Thesis Submission

- Need final reviewed subset for triple-level and answer-level correctness.
- Need explicit comparison against a naive/unconstrained extraction baseline.
- Need clearer reporting of repair success and rejection reasons across the
  agentic loop.
- Need final failure taxonomy with examples and claim impact.
- Need an optional second-domain pilot only as transfer evidence, not as proof
  of domain-general validity.
