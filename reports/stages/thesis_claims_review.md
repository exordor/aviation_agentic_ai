# Thesis Claims Review

## Revised Thesis Claim

This thesis does not assume that GraphRAG universally improves retrieval Recall@k over vector-only RAG. Instead, it investigates a narrower and more safety-relevant claim: in aviation training question answering, an ontology-constrained GraphRAG pipeline can add inspectable KG/path evidence, expose structured evidence coverage, and support insufficient-evidence abstention checks. The system is therefore evaluated with layered metrics: retrieval quality, KG evidence quality, answer citation quality, and safety-aware abstention are measured separately rather than collapsed into a single overall score.

## Research Questions

- **RQ1**: How can a lightweight aviation ontology constrain KG extraction from aviation training text?
- **RQ2**: Does ontology-constrained KG extraction add inspectable evidence-traceability signals compared with vector-only RAG?
- **RQ3**: When does graph evidence help aviation QA, and when is vector retrieval sufficient?
- **RQ4**: Can evidence-aware GraphRAG better identify unsupported or unsafe aviation questions?

## Hypotheses

- **H1**: Ontology constraints reduce unsupported KG triples and preserve provenance.
- **H2**: GraphRAG adds inspectable evidence-traceability signals compared with vector-only RAG.
- **H3**: GraphRAG does not always improve Recall@k but can improve structured evidence coverage.
- **H4**: Evidence sufficiency checking improves abstention on unsupported aviation questions.
- **H5**: KG evidence is most useful for relation-oriented, causal, and cross-page questions, and less useful for simple factual definition questions.

## Evaluation Framing

Negative or mixed Recall@k results are not hidden. They motivate layered evaluation and identify when vector retrieval is sufficient.

| Layer | Metrics | Purpose |
| --- | --- | --- |
| Retrieval quality | Recall@k, MRR@k, Context Precision@k | Measure whether the retriever returns source chunks near the top of the ranking. |
| KG evidence quality | key entity coverage, triple coverage, provenance completeness | Measure whether graph evidence covers the entities and relations needed by the question. |
| Answer quality | citation correctness, faithfulness, relevance | Measure whether generated answers are supported by cited evidence. |
| Safety-aware abstention | abstention correctness, false answer rate, boundary violations | Measure whether the system refuses unsupported or unsafe aviation questions. |

The report must not create or recommend a single mixed overall score.

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

## Unsafe Claims Scan

No unsupported unsafe claims were found in the scanned files outside explicit limitation or advisory-boundary contexts.

## Evidence Gaps Before Thesis Submission

- Need larger benchmark beyond 35 questions
- Need stronger no-answer / insufficient-evidence evaluation
- Need triple-level semantic correctness review
- Need graph traversal or path-based retrieval if claiming multi-hop graph reasoning
- Need manual or expert review if claiming aviation-domain correctness
- Need embedding/index comparison if claiming retrieval backend optimality

## Evidence Files

- `GOALS.md`: present
- `README.md`: present
- `configs/extraction_profile.yaml`: present
- `data/cqs/06_phak_ch4_0.expanded.gold.json`: present
- `data/cqs/06_phak_ch4_0.gold.json`: present
- `data/kg/06_phak_ch4_0.kg.jsonl`: present
- `data/kg/06_phak_ch4_0.structure_aware.kg.jsonl`: present
- `docs/benchmark_design.md`: present
- `docs/document_expansion_protocol.md`: present
- `docs/ontology_design.md`: present
- `docs/thesis_positioning.md`: present
- `reports/stages/answer_evaluation.json`: present
- `reports/stages/evidence_cards.md`: present
- `reports/stages/evidence_level_evaluation.json`: present
- `reports/stages/final_evaluation_review.json`: present
- `reports/stages/graphrag_review.json`: present
- `reports/stages/hybrid_rag_experiment.json`: present
- `reports/stages/hybrid_rag_structure_aware.json`: present
- `reports/stages/kg_extraction_comparison.json`: present
- `reports/stages/kg_validation.json`: present
- `reports/stages/retrieval_ablation.json`: present
- `reports/stages/robustness_evaluation.json`: present
- `reports/stages/structure_aware_kg_validation.json`: present
- `reports/stages/web_demo_readiness.json`: present
- `src/aviation_agentic_ai/advisory.py`: present
