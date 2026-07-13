# Research Overview

> Migrated on 2026-07-05 from `docs/thesis_positioning.md`, `docs/research_mainline.md`, and `docs/master_project_scope_lock.md` as part of the research-governance refactor (spec `docs/superpowers/specs/2026-07-05-research-governance-refactor-design.md`). The source files (now archived under `docs/archive/governance_era/`) were migrated on 2026-07-05.

## Research Area

- Schema-constrained, evidence-grounded information extraction.
- Agentic validation/refinement loops for KG construction.
- Authority-grounded cross-source KG-RAG question answering.
- Retrospective FAA ATCSCC advisory analysis.

## Problem Statement

The project studies evidence-grounded question answering over retrospective FAA
ATCSCC advisories linked to bounded authority and observation sources. ATCSCC
advisories are semi-structured operational notices:
they contain identifiers, affected NAS elements, route or airport constraints,
effective time windows, causes, and free-text operational context. The research
problem is not to build a complete aviation ontology. The research problem is to
extract advisory-event knowledge with explicit schema constraints and evidence
spans, align facility codes and operational abbreviations against versioned
registries, link a controlled 68-record cohort to NASR and weather evidence,
then evaluate whether the cross-source graph improves grounded question
answering without turning association into causal claims.

The prototype therefore treats the ontology/profile as an engineering
constraint. The main method is schema-constrained, evidence-grounded Agentic
KG-RAG.

## Locked Project Outcome

The project outcome is one bounded thesis-grade system study:

**Authority-Grounded Cross-Source Agentic KG-RAG for Retrospective FAA ATCSCC
Advisories.**

The thesis studies how a lightweight application schema constrains LLM
extraction from retrospective FAA ATCSCC advisories, how autonomous
validator/refiner/critic and context-alignment agents change extraction quality,
and whether a graph linking advisories, authority registries, NAS facilities,
and contemporaneous METAR/TAF evidence improves grounded question answering and
citation diagnostics.

The ontology/profile is an engineering constraint. It is not the research object.

## Single-Sentence Contribution

This project builds and evaluates a schema-constrained, evidence-linked
multi-agent KG-RAG pipeline that extracts FAA ATCSCC event facts, autonomously
aligns facility codes and operational abbreviations through versioned authority
snapshots, links a controlled cohort to contemporaneous weather evidence, and
answers with explicit source-declaration, observation/forecast, and
system-association evidence layers.

## Revised Thesis Claim

This thesis investigates a retrospective and source-bounded claim: for FAA
ATCSCC advisories, a lightweight NASA ATMONTO-derived application schema plus
versioned FAA-derived authority registries can constrain extraction and entity
alignment, support autonomous agentic validation/refinement, and provide an
inspectable cross-source event graph for KG-RAG question answering. The system
is evaluated with layered metrics:
schema-valid extraction, evidence-linked relation correctness on reviewed
subsets, repair/critic behavior, retrieval and answer quality, citation quality,
cross-source evidence-layer coverage, abstention/quarantine behavior, and the
independent scientific-review boundary are reported separately.

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
retrospective advisory text + versioned terminology/NASR/weather snapshots
  -> schema-constrained extraction
  -> facility/abbreviation alignment with autonomous confidence gates
  -> agentic validation/refinement/critic loop
  -> cross-source event graph with provenance and typed evidence links
  -> source-only / linked-text / KG-layered answer comparison
  -> evidence-layered answers, abstention, and failure analysis
```

## Research Scope

### In scope

The final master project needs only the following deliverables.

| Deliverable | Purpose | Canonical evidence |
|---|---|---|
| Frozen ATCSCC data profile | Defines the retrospective source family and source format. | `reports/stages/atcscc_data_format_and_processing_flow.md` |
| Lightweight ATCSCC schema/profile | Defines allowed event fields, predicates, and profile gaps. | `reports/stages/atcscc_ontology_profile_overview.md` |
| Versioned authority and source snapshots | Defines reproducible facility-code, operational-term, and weather inputs with source URL, effective date, and checksum. | `configs/cross_source_v1.yaml`, `data/sources/faa_atcscc_terms_v1.yaml` |
| Autonomous two-layer alignment | Aligns facility codes and operational abbreviations; ambiguous cases must be accepted by context evidence or quarantined. | `src/aviation_agentic_ai/cross_source/`, `data/evaluation/cross_source/` |
| Controlled cross-source cohort | Links the 68 connectable advisories to authority, NASR, and contemporaneous METAR/TAF evidence without causal overstatement. | `data/evaluation/cross_source/v1/automated_regression_v1.jsonl` |
| Schema-constrained extraction experiment | Tests rule, LLM, schema, repair, and hybrid extraction variants. | `reports/stages/nasa_atmonto_formal_experiment_scoring.md` |
| Agentic validation/refinement loop | Tests whether validator/refiner/critic steps reduce schema and evidence failures. | Agentic full-run diagnostic; see `ARTIFACT_INDEX.md`. |
| KG-RAG answer-generation comparison | Tests source-only, linked-text, and KG-layered cross-source answering alongside the existing vector/graph/routed evaluation. | Retrieval, answer-generation, and cross-source evaluation reports; see `ARTIFACT_INDEX.md`. |
| Failure and claim-safety audit | Defines autonomous rejection/quarantine behavior and separates runtime autonomy from independent research evaluation. | `reports/stages/nasa_atmonto_reviewer_defense_audit.md`, `reports/stages/nasa_atmonto_sota_goal_audit.md`, `reports/stages/cross_source_mainline_evaluation.md` |
| Thesis synthesis | Turns the evidence into the final research story. | `RESEARCH_OVERVIEW.md`, `reports/stages/nasa_atmonto_experiment_chapter_draft.md` |

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
- Unbounded source expansion beyond the versioned terminology, NASR/facility,
  and weather profiles admitted by the cross-source V2 protocol.
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
- A versioned two-layer canonicalization protocol for facility identifiers and
  operational abbreviations, with deterministic acceptance and contextual
  quarantine gates.
- A cross-source answer contract that separates source declarations,
  contemporaneous observations/forecasts, and system associations, and forbids
  converting correlation into deterministic causation.
- A layered evaluation and claim-boundary protocol that separates schema
  validity, evidence support, answer quality, autonomous runtime behavior, and
  independent scientific evaluation.

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
| Authority and ambiguity alignment | authoritative-map accuracy, contextual-target accuracy, quarantine accuracy, out-of-registry acceptance count | Measure whether canonical identifiers and ambiguous abbreviations are resolved safely. |
| Cross-source answer contract | required evidence-layer coverage, required citation-layer coverage, abstention correctness, causal-overstatement count | Measure whether linked answers remain attributable and epistemically bounded. |
| Autonomous failure boundary | failure category counts, abstention correctness, quarantine/rejection counts, independent-evaluation status | Measure whether runtime proceeds without human dependency while unresolved scientific claims remain explicit. |

The thesis must not collapse these layers into a single mixed overall score.
The full metric protocol is documented in `EXPERIMENTS.md` and can
be audited with `uv run aviation-ai report evaluation-protocol`. The full thesis
experiment sequence is documented in `EXPERIMENTS.md`, including systems under
test, baselines, metrics, and the experimental procedure.

## Claim Safety Matrix

| Claim | Current evidence | Supported strength | Safe wording | Unsafe wording to avoid |
| --- | --- | --- | --- | --- |
| Lightweight schema constrains advisory event extraction. | ATCSCC profile terms, schema validation, and prediction-output validation reports constrain accepted event fields. | strong | The application schema constrains which advisory event fields and relations can enter the graph. | The ontology fully models aviation knowledge. |
| Accepted facts preserve provenance. | KG and prediction validation reports check source IDs and evidence spans. | strong | Accepted facts carry source-bounded provenance checked by deterministic validation. | Every KG triple is semantically correct. |
| Agentic validation improves extraction quality. | Validator, refiner, critic, repair, and rejection reports. | moderate | The agentic loop reduces specific schema and support failures in the current ATCSCC pipeline. | Autonomous agents construct a correct ontology. |
| KG-RAG improves grounded ATCSCC QA. | Retrieval, graph-health, and LLM answer-generation diagnostics report answer-set, citation, and target-source metrics. | moderate | KG-RAG improves some source-bounded grounding diagnostics on this benchmark. | GraphRAG is always more accurate than vector retrieval. |
| Cross-source KG-RAG adds attributable context. | Versioned authority snapshots, 68-record linking cohort, typed answer layers, and matched component baselines. | strong on component/process metrics | Cross-source links add separately cited authority, observation/forecast, and system-association context on the controlled cohort. | Weather or graph links prove the cause of an advisory. |
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
- Remaining failures and independent-evaluation boundaries are explicitly categorized.

## What The Thesis Must Not Claim

- The ATCSCC application schema is a complete aviation ontology.
- NASA ATMONTO is treated as complete ground truth for ATCSCC advisories.
- GraphRAG universally improves Recall@k or answer accuracy.
- Runtime agents eliminate mandatory human intervention for acceptance,
  quarantine, and abstention; this does not eliminate independent scientific
  evaluation or external expert validation.
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
- Cross-source V2 adds versioned authority alignment, contemporaneous weather
  context, typed evidence layers, and autonomous quarantine/abstention.
- Remaining failures can be categorized into extraction, alignment, linking,
  retrieval, evidence-layer, and answer-overreach cases.

## Claims To Avoid

- The project builds a complete aviation ontology.
- NASA ATMONTO is complete ground truth for ATCSCC advisories.
- GraphRAG universally outperforms vector-only RAG.
- Runtime autonomy is externally certified or replaces independent scientific
  evaluation.
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
| GraphRAG and citation-faithful QA | Compare source-only, linked-text, graph, hybrid, and routed retrieval instead of assuming graph retrieval is always better. | A cross-source ATCSCC KG-RAG benchmark with evidence-layer, citation, unsupported-claim, and abstention diagnostics. |
| Multi-agent validation/refinement | Use role-separated source, extractor, alignment, linker, validator, answer, and critic roles. | An auditable autonomous loop for extraction repair, ambiguity quarantine, source linking, and rejection under hard schema and evidence gates. |

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
| Requires a source outside the admitted cross-source profiles, a new benchmark, platform, or dashboard | Move to future work. |
| Changes the research question | Reject unless the scope lock is explicitly reopened. |
| Only useful for exploration | Keep as ignored local notes or a short literature note. |

Default decision: defer.

## Stop Rule

The project is ready to write up when these are true:

1. The frozen ATCSCC and cross-source snapshots, schema/profile, extraction and
   alignment results, agentic loop, KG-RAG results, and failure audit are linked from
   `ARTIFACT_INDEX.md`.
2. The research-overview, research-questions, and claim-safety sections in
   `RESEARCH_OVERVIEW.md` tell the same story.
3. Every major claim in the thesis draft maps to one tracked evidence artifact.
4. Remaining gaps are listed as limitations or future work rather than becoming
   new experiments.
5. Verification commands pass for the final code and documentation state.

## Figure Boundary

The thesis needs a small number of high-value figures only.

| Figure | Purpose |
|---|---|
| System overview | Show versioned sources, schema, multi-agent gates, cross-source graph, KG-RAG, and evaluation. |
| ATCSCC source-to-fact example | Show one advisory span mapped to event facts and evidence ids. |
| Schema/profile slice | Show the lightweight application schema, not full ATMONTO. |
| Agentic loop | Show extractor, validator, refiner, critic, and rejection/repair artifacts. |
| Results summary | Show layered metrics and failure categories. |

Paper figure galleries and PDF extraction assets are research support tools, not final deliverables.

## Evidence Gaps Before Thesis Submission

- Replicate the hard ambiguity result across additional abbreviation families.
- Add an independent linker baseline; the current linked-text arm shares
  accepted links with the KG system.
- External aviation-expert certification remains optional future validation,
  not a runtime dependency or a prerequisite for the current bounded claims.
- Need explicit comparison against a naive/unconstrained extraction baseline.
- Need clearer reporting of repair success and rejection reasons across the
  agentic loop.
- Need final failure taxonomy with examples and claim impact.
- Need an optional second-domain pilot only as transfer evidence, not as proof
  of domain-general validity.
