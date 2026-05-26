# Project Goals

Last updated: 2026-05-26

This file defines the durable project goals, scope boundaries, and success criteria. Execution work is tracked separately in `TASKS.md`.

## Goal vs Task

- A goal describes an outcome the project must achieve.
- A task describes a concrete action that can be completed and checked off.
- Goals change slowly. Tasks change whenever implementation or experiment evidence changes.
- Reports under `reports/` provide evidence that a goal has been met.

## G1 - Course Objective And Project Rationale

Build a research prototype that demonstrates how ontology, knowledge graphs, RAG, GraphRAG, hallucination reduction, and agentic workflow concepts can support an aviation advisory assistant.

Success criteria:

- The final report explains what problem the project solves and why this problem matters for private-pilot learning and decision support.
- The final report explains ontology, KG, RAG, GraphRAG, hallucination mitigation, and agentic AI in the context of the implemented system.
- The project can answer why GraphRAG is needed instead of only using plain LLM prompting or vector-only RAG.
- The project uses FAA aviation handbook material as the starting source corpus.
- The report clearly connects implementation choices to the course objective.

Current status: in progress.

## G2 - Ontology-Grounded KG Deliverable

Deliver a focused aviation KG/ABox artifact generated from PHAK Chapter 4, grounded by a validated ontology/TBox design.

Rationale:

- The KG is a project deliverable, not only an intermediate cache.
- KG generation depends on ontology design because class/property constraints define what can be extracted and validated.
- The ontology provides the schema boundary that prevents arbitrary LLM-generated triples from entering the KG.

Success criteria:

- A baseline or generated TBox ontology exists and can be validated.
- The extraction profile maps focused aviation classes/properties back to the ontology design.
- Focused ABox/KG triples are extracted only when supported by source chunks.
- KG validation rejects unsupported classes, unsupported properties, missing provenance, and evidence that is not present in the source chunk.
- The final report explains how ontology design affects KG extraction quality, provenance, and downstream GraphRAG retrieval.

Current status: active curated ontology is available; focused KG was extracted and validated against the curated schema.

## G3 - GraphRAG Core Pipeline

Implement GraphRAG as a core project goal: combine KG/graph retrieval with vector retrieval so answers can use both semantic text evidence and structured relationship evidence.

Target pipeline:

```text
PDF -> chunks -> ontology-constrained KG/ABox
    -> Chroma vector index
    -> graph retrieval + vector retrieval
    -> reciprocal-rank hybrid fusion
    -> grounded LLM answer with citations
```

Success criteria:

- Chunks, KG, index, retrieval results, and LLM answers are generated through CLI commands.
- Each run records configuration, model name, collection name, chunking strategy, paths, and rebuild flags.
- Experiments compare vector-only, graph-only, and hybrid/GraphRAG retrieval rather than reporting hybrid results alone.
- Reports explain when graph evidence helps, when vector retrieval is enough, and when the KG is too sparse to improve retrieval.
- Answers cite chunk/page/triple evidence or abstain when evidence is insufficient.

Current status: implementation exists for both fixed-window and structure-aware GraphRAG runs. Fixed-window shows GraphRAG's value mainly through KG evidence coverage; structure-aware Hybrid RAG matches vector-only Recall@5 while preserving KG evidence coverage.

## G4 - Evaluation And Experiment Protocol

Evaluate retrieval, KG evidence, and LLM answer quality as separate layers rather than a single mixed score.

Success criteria:

- Retrieval metrics include Recall@5, MRR@5, Context Precision@5, hit ranks, and hit source identifiers.
- KG evidence metrics include relevant triple counts, entity coverage, provenance completeness, and invalid/unsupported triple counts.
- LLM answer metrics include citation completeness, citation validity, and insufficient-evidence abstention behavior.
- Gold labels support page-level ground truth now and can later be refined to chunk/span-level evidence.
- Per-question evidence cards explain gold evidence, vector retrieval, graph retrieval, hybrid fusion behavior, citation status, and failure category for each evaluated CQ.

Current status: protocol modules and real experiment evidence exist for chunking comparison, fixed-window Hybrid RAG, structure-aware KG extraction, structure-aware Hybrid RAG, reviewed chunk/span gold labels, expanded 35-question course-project gold, evidence-level evaluation, retrieval ablation, KG extraction comparison, answer evaluation, robustness evaluation, final evaluation review, and per-question evidence cards. The gold labels are course-project gold and not external aviation examiner certification.

## G5 - Report Hygiene And Final Project Report

Maintain readable project evidence and generate a complete final report from deterministic sources plus optional AI polishing.

Success criteria:

- `reports/stages/` remains a compact dashboard.
- Historical stage artifacts are archived rather than deleted.
- `reports/final/project_report.md` is generated from evidence sources and does not invent missing results.
- Missing experiments are explicitly marked TBD / Not yet run until evidence exists.

Current status: report hygiene, deterministic final report, academic-style
report, project-defense notes, AI-enhanced visual assets with local SVG
fallbacks, and an editable academic defense PPTX are available under
`reports/final/`. Final evaluation and web smoke evidence are recorded under
`reports/stages/`.

## G6 - Future Advisory Assistant Boundary

Prepare for a future advisory assistant while keeping the current prototype within a safe learning and decision-support boundary.

Success criteria:

- The system is described as aviation learning and decision support only.
- It does not claim to replace the POH, approved checklists, ATC, flight instructor guidance, or pilot judgment.
- Future live aircraft/environment data and emergency/procedure manuals are treated as later-stage extensions.

Current status: boundary text exists; future live-context integration is out of scope for the current phase.

## G7 - Web Interface Demonstrator

Provide a user-facing web interface that demonstrates the implemented pipeline without claiming production cockpit readiness.

Success criteria:

- The interface lets a user ask aviation questions and choose or display retrieval mode: vector, graph, or hybrid/GraphRAG.
- The interface shows the final answer together with cited chunks, pages, and KG triples when available.
- The interface makes the advisory boundary visible: learning and decision support only, not a replacement for POH, approved checklists, ATC, instructor guidance, or pilot judgment.
- The interface can display experiment evidence or pipeline status so the project is understandable to a reviewer.

Current status: offline-first FastAPI demo implemented with a macOS-style
utility layout. It reads existing GraphRAG reports, gold labels, KG artifacts,
and evidence-level metrics by default; live query is opt-in. The interface now
includes a deterministic demo narrative, pipeline explanation, mode comparison,
Why This Result panel, and question-scoped KG relationship graph so reviewers
can see why evidence was selected, not only read the answer and evidence lists.
Offline FastAPI smoke evidence is available in
`reports/stages/web_demo_final_smoke.md`.

## G8 - Pipeline Explanation And Project Defense

Be ready to answer project-review questions about what was built, why it was built this way, and how the design choices affect quality.

Success criteria:

- The final report and/or presentation clearly explains the pipeline from PDF to chunks, ontology, KG, index, retrieval, GraphRAG answer, and citations.
- The project includes a comparison of chunking strategies and retrieval modes with an explanation of observed tradeoffs.
- The project can answer "what does each component do?", "why is it needed?", "why not use a simpler baseline?", and "where can the system fail?"
- Limitations are explicit: coarse gold labels, incomplete KG coverage, LLM dependency, source-scope limits, and non-production advisory boundary.

Current status: ontology design documentation, KG validation evidence, chunking
comparison, fixed-window Hybrid RAG, structure-aware Hybrid RAG, GraphRAG
review, evidence-level evaluation, web demo readiness, academic report,
final evaluation review, web demo readiness/smoke evidence, academic report,
defense notes, AI-enhanced defense PPT, and per-question evidence cards are
available. The current defense framing is:
structure-aware improves evidence support while costing more KG extraction work;
GraphRAG should be defended as structured evidence coverage rather than a simple
page-level Recall winner; and the web demo is offline-first by default for
reproducible review.

## G9 - Experimental Expansion And Robustness

Extend the current proof-of-pipeline experiments into a stronger evaluation suite that can support more defensible research claims about GraphRAG value.

Rationale:

- The current experiment proves that the system works end to end on 10 boundary CQs.
- Stronger claims require more gold labels, retrieval ablations, KG extraction comparisons, answer-level evaluation, and robustness checks.
- The project should keep retrieval quality, KG evidence quality, answer faithfulness, cost, and safety boundary behavior as separate experiment layers.

Success criteria:

- Gold labels expand from 10 boundary CQs to a larger set of 30-50 questions with chunk/span evidence, key entities, and no-answer or insufficient-evidence cases.
- Retrieval ablations compare vector-only, graph-only, hybrid RRF, hybrid with graph disabled, different graph hops, and different top-k settings.
- KG extraction experiments compare fixed-window and structure-aware chunks, model choice, max-token settings, prompt strictness, provenance completeness, and unsupported triple rejection.
- Answer-level evaluation records citation correctness, faithfulness, answer relevance, abstention correctness, and advisory-boundary violations without creating a single mixed score.
- Robustness tests include paraphrased CQs, terminology variation, cross-page questions, ambiguous questions, and insufficient-evidence questions.
- Cost and latency reports record chunk build time, KG extraction cost/time, index build time, query latency, token usage, and collection/index size.
- Dataset expansion beyond PHAK Chapter 4 only starts after document metadata and section schema are enforced for each new source.

Current status: in progress. The 10-CQ experiment remains the baseline, and a first expanded evaluation suite now exists with 35 gold-label questions, 5 insufficient-evidence cases, deterministic retrieval ablation, KG extraction comparison, answer evaluation, robustness evaluation, cost/latency metadata blocks, and a document expansion protocol. Embedding/index backend comparison remains future work.

## Current Non-Goals

- Do not build a production cockpit assistant in this phase.
- Do not present the web interface as certified, real-time, or operational flight software.
- Do not integrate live aircraft sensors or real-time environmental data in this phase.
- Do not expand to emergency/procedure manuals before the document metadata and section schema are stable.
- Do not collapse retrieval, KG evidence, and LLM answer quality into one overall score.
- Do not submit local secrets, Chroma indexes, model caches, or temporary generated files.

## Traceability

| Goal | Main evidence | Execution tasks |
| --- | --- | --- |
| G1 | `GOALS.md`, `README.md`, `reports/final/project_report.md`, optional local note `tmp/goal.md` | `TASKS.md` P2 |
| G2 | `data/ontology/`, `configs/extraction_profile.yaml`, KG reports | `TASKS.md` P0/P1 |
| G3 | chunk/index/query CLI outputs, Hybrid RAG report | `TASKS.md` P0 |
| G4 | `src/aviation_agentic_ai/evaluation/`, experiment reports, `reports/stages/final_evaluation_review.md`, `reports/stages/evidence_cards.md` | `TASKS.md` P0/P1 |
| G5 | `reports/stages/index.md`, `reports/final/project_report.md`, `reports/final/project_academic_report.md`, defense PPT | `TASKS.md` P2 |
| G6 | advisory boundary text, final report limitations | `TASKS.md` P1/P2 |
| G7 | web app code, `reports/stages/web_demo_readiness.md`, `reports/stages/web_demo_final_smoke.md`, demo instructions | `TASKS.md` P2 |
| G8 | final report, academic report, comparison reports, evidence cards, defense notes, defense PPT | `TASKS.md` P1/P2 |
| G9 | expanded gold labels, ablation reports, robustness reports, cost/latency reports | `TASKS.md` P3 |
