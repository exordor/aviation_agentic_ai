# Thesis Positioning

## Problem Statement

The project studies aviation training question answering over FAA PHAK Chapter 4.
The central problem is not only whether a retriever can return the right page. A
defensible aviation learning system must also show why evidence was selected,
which source text supports it, which KG relations were used, and when the source
material is insufficient for a safe answer.

The prototype therefore treats GraphRAG as an evidence-structuring method rather
than as a guaranteed Recall@k winner.

## Why The Old Recall Claim Is Too Strong

The earlier framing implied that GraphRAG or Hybrid RAG should generally improve
retrieval Recall@k over vector-only RAG. Current project evidence is more mixed:
on the expanded 35-question set, vector Recall@5 can be higher than the default
hybrid configuration. This negative result is useful. It shows that vector
retrieval can be sufficient for simple factual or page-local questions and that
GraphRAG should be evaluated for structured evidence support, provenance, and
abstention behavior rather than defended as a universal retrieval winner.

## Revised Thesis Claim

This thesis does not assume that GraphRAG universally improves retrieval Recall@k
over vector-only RAG. Instead, it investigates a narrower and more safety-relevant
claim: in aviation training question answering, an ontology-constrained GraphRAG
pipeline can improve evidence traceability, structured KG evidence coverage, and
insufficient-evidence abstention. The system is therefore evaluated with layered
metrics: retrieval quality, KG evidence quality, answer citation quality, and
safety-aware abstention are measured separately rather than collapsed into a
single overall score.

## Research Questions

- **RQ1**: How can a lightweight aviation ontology constrain KG extraction from
  aviation training text?
- **RQ2**: Does ontology-constrained KG extraction improve evidence traceability
  compared with vector-only RAG?
- **RQ3**: When does graph evidence help aviation QA, and when is vector
  retrieval sufficient?
- **RQ4**: Can evidence-aware GraphRAG better identify unsupported or unsafe
  aviation questions?

## Hypotheses

- **H1**: Ontology constraints reduce unsupported KG triples and preserve
  provenance.
- **H2**: GraphRAG improves evidence traceability compared with vector-only RAG.
- **H3**: GraphRAG does not always improve Recall@k but can improve structured
  evidence coverage.
- **H4**: Evidence sufficiency checking improves abstention on unsupported
  aviation questions.
- **H5**: KG evidence is most useful for relation-oriented, causal, and
  cross-page questions, and less useful for simple factual definition questions.

## Contributions

- A task ontology for PHAK Chapter 4 that constrains focused aviation KG
  extraction.
- Validator-gated KG/ABox artifacts with provenance back to source chunks.
- A CLI-first vector, graph, and hybrid GraphRAG pipeline that can be reproduced
  from local artifacts.
- A layered evaluation protocol that separates retrieval quality, KG evidence
  quality, answer quality, and safety-aware abstention.
- A claim-safety framing that keeps the aviation learning and decision-support
  boundary explicit.

## Evaluation Philosophy

The thesis should report negative and mixed Recall@k results directly. A lower
or equal hybrid Recall@k does not invalidate GraphRAG if the graph layer improves
evidence traceability, KG evidence coverage, or abstention on unsupported
questions. The evaluation should therefore keep these layers separate:

| Layer | Metrics | Purpose |
| --- | --- | --- |
| Retrieval quality | Recall@k, MRR@k, Context Precision@k | Measure whether the right chunks are returned near the top of the ranking. |
| KG evidence quality | key entity coverage, triple coverage, provenance completeness | Measure whether structured graph evidence covers the entities and relations needed by the question. |
| Answer quality | citation correctness, faithfulness, relevance | Measure whether generated answers are supported by cited evidence. |
| Safety-aware abstention | abstention correctness, false answer rate, boundary violations | Measure whether the system refuses unsupported or unsafe aviation questions. |

The thesis must not collapse these layers into a single mixed overall score.
The full metric protocol is documented in `docs/evaluation_protocol.md` and can
be audited with `uv run aviation-ai report evaluation-protocol`. It explicitly
maps mainstream RAGAS-style metrics, ARES-style component evaluation, standard
IR metrics, GraphRAG path/evidence metrics, ontology/KG construction metrics,
and aviation safety-abstention metrics onto the current project reports.
The full thesis experiment sequence is documented in
`docs/experiment_workflow.md` and summarized by
`uv run aviation-ai report thesis-experiment-dashboard`.

## Claim Safety Matrix

| Claim | Current evidence | Supported strength | Safe wording | Unsafe wording to avoid |
| --- | --- | --- | --- | --- |
| Ontology constrains KG extraction. | Extraction profile terms map to the curated ontology; KG validation rejects unsupported schema terms. | strong | The task ontology constrains which focused classes and relations can enter the KG. | The ontology fully models aviation knowledge. |
| KG triples preserve provenance. | KG validation reports zero missing-provenance errors in the current fixed-window and structure-aware artifacts. | strong | Current extracted triples carry source chunk provenance checked by deterministic validation. | Every KG triple is semantically correct. |
| GraphRAG improves Recall@5. | Expanded retrieval ablation shows vector Recall@5 can be higher than default hybrid Recall@5. | not supported | GraphRAG does not always improve Recall@5; report Recall separately from KG evidence coverage. | GraphRAG always improves Recall@5. |
| GraphRAG improves structured evidence support. | Graph and hybrid modes expose KG coverage, provenance, triples, and evidence-level answer support. | moderate | GraphRAG improves inspectable structured evidence support in the current benchmark. | GraphRAG is always more accurate than vector retrieval. |
| Hybrid RAG always beats vector-only RAG. | Fixed-window and expanded ablations include cases where vector retrieval is equal or better on Recall@5. | not supported | Hybrid RAG can add KG evidence coverage while vector retrieval can remain sufficient for simple factual questions. | Hybrid RAG always beats vector-only RAG. |
| The system can answer aviation operational questions. | The advisory boundary limits the system to learning and decision support; live operational data and official procedures are out of scope. | not supported | The system can answer aviation training questions when evidence is sufficient and should abstain otherwise. | The system can support operational flight decisions. |
| The system can support aviation learning questions. | The pipeline answers PHAK Chapter 4 training questions with citations and evidence panels. | moderate | The prototype supports aviation learning questions over its scoped source material. | The prototype is a certified aviation assistant. |
| The system can replace POH/checklists/ATC/instructor judgment. | The advisory boundary explicitly rejects replacement of official sources or human judgment. | not supported | The system does not replace POH, approved checklists, ATC, instructor guidance, or pilot judgment. | The system can replace POH, checklists, ATC, or instructor judgment. |
| The benchmark is externally aviation-expert certified. | Current labels are reviewed course-project / thesis-oriented gold, not external examiner certification. | not supported | The benchmark is course-project / thesis-oriented gold with documented limitations. | The benchmark is externally aviation-expert certified. |
| The benchmark is course-project / thesis-oriented gold. | Reports identify the 10-question and expanded 35-question labels as project/thesis evidence. | strong | The benchmark is course-project / thesis-oriented gold, useful for internal evaluation but not external certification. | The benchmark proves aviation-domain correctness. |

## What The Thesis Can Claim

- The project implements a reproducible aviation training GraphRAG prototype over
  scoped FAA handbook material.
- The task ontology constrains focused KG extraction and supports validation.
- Current KG triples preserve source provenance at the artifact level.
- GraphRAG adds structured KG evidence coverage and evidence traceability in the
  current experiments.
- Mixed Recall@k results show when vector retrieval is sufficient and motivate
  layered evaluation.
- The system can support aviation learning questions when scoped evidence is
  sufficient.

## What The Thesis Must Not Claim

- GraphRAG universally improves Recall@k over vector-only RAG.
- Hybrid RAG always outperforms vector-only RAG.
- The ontology is a complete aviation ontology.
- The benchmark is externally aviation-expert certified.
- The system is operationally safe for flight decisions.
- The system can replace the aircraft POH, approved checklists, ATC
  instructions, instructor guidance, or pilot judgment.

## Relationship Between Ontology, KG, GraphRAG, Provenance, And Abstention

The ontology is the schema boundary. It defines the focused classes and
relations that the extractor is allowed to emit. The KG is the structured
evidence layer built under that boundary; each accepted triple must preserve
source provenance so it can be traced back to handbook chunks. GraphRAG combines
this KG evidence with vector retrieval, allowing answers to cite both text and
relations where available. Provenance makes the result inspectable, while
evidence sufficiency checks determine whether the system should answer or
abstain.

This relationship is safety relevant because aviation questions often require a
clear boundary between training explanation and operational authority. When the
available source material does not support a question, the correct behavior is
to abstain and defer to official sources, the aircraft POH/AFM, approved
checklists, ATC instructions, instructor guidance, and pilot judgment.

## Evidence Gaps Before Thesis Submission

- Need larger benchmark beyond 35 questions.
- Need stronger no-answer / insufficient-evidence evaluation.
- Need triple-level semantic correctness review.
- Need graph traversal or path-based retrieval if claiming multi-hop graph
  reasoning.
- Need manual or expert review if claiming aviation-domain correctness.
- Need embedding/index comparison if claiming retrieval backend optimality.
