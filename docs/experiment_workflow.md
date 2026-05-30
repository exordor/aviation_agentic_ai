# Thesis Experiment Workflow

This document defines the canonical thesis experiment pipeline. It connects the
research questions, source scope, datasets, baselines, metrics, reports,
failure analysis, and supported claims. The workflow uses layered metrics and
does not create a single mixed overall score.

## Step 0: Thesis Claim And Evaluation Protocol

Inputs:

- `docs/thesis_positioning.md`
- `docs/evaluation_protocol.md`

Outputs:

- fixed research questions;
- fixed evaluation layers;
- explicit rule that no mixed overall score is used.

Purpose: lock the thesis claim before running experiments. The project studies
whether an ontology-constrained GraphRAG pipeline improves evidence
traceability, structured KG evidence coverage, and safety-aware abstention over
scoped aviation training material. It does not assume that GraphRAG universally
improves Recall@k.

## Step 1: Source Corpus And Document Scope

Source:

- FAA PHAK Chapter 4 PDF.

Reports and documents:

- source scope reports;
- `docs/document_expansion_protocol.md`.

Purpose: define what the system can and cannot answer. The corpus supports
aviation learning questions over scoped handbook text. It does not support live
weather, current NOTAMs, ATC clearance, aircraft-specific POH/AFM procedures, or
operational go/no-go decisions.

## Step 2: Ontology Construction And Validation

Artifacts:

- curated ontology;
- baseline ontology;
- `docs/ontology_design.md`.

Metrics:

- RDF/OWL parse validity;
- class/property count;
- label/comment coverage;
- domain/range completeness;
- competency-question coverage.

Output: a task ontology for PHAK Chapter 4 evidence extraction, not a complete
aviation ontology.

## Step 3: Chunking And Indexing

Compared strategies:

- `fixed_window`;
- `sentence_recursive`;
- `structure_aware`;
- `semantic_meta_like`.

Metrics:

- Recall@5;
- MRR@5;
- Context Precision@5;
- chunk count;
- chunk size statistics;
- boundary preservation.

Output: selected default strategy and baseline strategy. Structure-aware
chunking is the default candidate when it improves retrieval quality and
evidence granularity; fixed-window remains a baseline where needed for
historical KG compatibility.

## Step 4: KG Extraction And Validation

Compared artifacts:

- fixed-window KG;
- structure-aware KG.

Metrics:

- valid triples;
- unsupported class/property count;
- provenance completeness;
- evidence-in-source rate;
- duplicate or near-duplicate count;
- key entity coverage;
- manual triple semantic review status.

Output: the KG is schema-valid and provenance-valid. Semantic correctness
remains manual-review dependent unless the triple semantic review sample is
completed. Do not fabricate semantic correctness results.

## Step 5: Benchmark Construction And Validation

Datasets:

- 10-CQ pilot set;
- 35-question expanded set;
- 120-label benchmark v2.

Dataset roles:

- 10-CQ set: demo and qualitative inspection;
- 35-question expanded set: pilot ablation;
- benchmark v2: main thesis retrieval and safety benchmark.

Metrics:

- evidence span validation;
- category distribution;
- supported vs no-answer labels;
- benchmark naturalness and manual-review status.

Warning: benchmark v2 is thesis/course-project evidence, not external aviation
expert certification.

## Step 6: Retrieval Ablation

Main benchmark:

- benchmark v2.

Baselines and variants:

- vector-only;
- graph-disabled hybrid;
- lexical graph;
- hybrid lexical;
- different graph hops;
- different top-k settings.

Metrics:

- Recall@5;
- Recall@10;
- Precision@5;
- MRR@5;
- MRR@10;
- NDCG@10;
- Context Precision@5;
- Context Recall;
- KG evidence coverage.

Output: retrieval tables explaining when vector retrieval is sufficient and
when graph evidence adds inspectable structure. Negative or mixed Recall results
must remain visible.

## Step 7: Graph Traversal And Graph Path Evaluation

Compared modes:

- vector-only;
- lexical graph search;
- traversal graph 1-hop;
- traversal graph 2-hop;
- traversal graph 3-hop;
- hybrid vector + lexical graph;
- hybrid vector + traversal graph;
- guarded hybrid traversal if implemented.

Metrics:

- graph path coverage;
- Path Recall@5;
- Path Precision@5;
- Supporting Path Rate;
- Irrelevant Path Rate;
- Key Entity Coverage;
- Relation Coverage;
- Average Path Length.

Interpretation: high path coverage does not imply high retrieval quality. Path
metrics are heuristic unless manually reviewed. Failure modes include
`seed_linking_error`, `generic_seed_node`, `path_found_but_wrong_chunk`,
`low_value_predicate`, `graph_fusion_dilution`, and `kg_sparse_for_question`.

## Step 8: Answer Generation Evaluation

Document or create a stratified answer-evaluation subset covering:

- supported factual;
- concept definition;
- relation causal;
- cross-page;
- paraphrase / terminology variation;
- insufficient-evidence.

Compared methods where available:

- direct LLM without retrieval;
- vector-only RAG;
- lexical HybridRAG;
- traversal HybridRAG;
- sufficiency-aware HybridRAG.

Metrics:

- Faithfulness;
- Answer Correctness;
- Answer Relevance;
- Citation Completeness;
- Citation Precision;
- Citation Recall;
- advisory boundary violation count.

Score labels:

- deterministic heuristic scores must be labelled as heuristic;
- LLM-as-judge scores must be labelled as LLM judge;
- manual scores must be labelled as manual review.

## Step 9: Safety And Abstention Evaluation

Main benchmark:

- benchmark v2 no-answer labels.

Metrics:

- Abstention Accuracy;
- False Answer Rate;
- False Abstention Rate;
- Advisory Boundary Violation Count;
- Risk Category Accuracy.

Risk categories:

- `live_weather`;
- `current_notam`;
- `atc_clearance`;
- `aircraft_specific_vspeeds`;
- `poh_or_checklist`;
- `emergency_procedure`;
- `weight_and_balance`;
- `go_no_go_decision`;
- `unknown_operational`;
- `training_question`.

Output: safety tables showing whether the system refuses unsupported or
operational questions.

## Step 10: Final Claim Synthesis

Map each research question to:

- evidence artifacts;
- primary metrics;
- result summary;
- supported claim;
- limitations.

Rules:

- do not hide negative results;
- explicitly state when graph traversal improves path evidence but not Recall;
- explicitly state when hybrid improves context recall but not MRR or precision;
- explicitly state when sufficiency improves safety but creates false
  abstentions;
- do not claim external aviation expert certification;
- preserve the advisory boundary: the system is for aviation learning and
  decision support only and does not replace POH/AFM, approved checklists, ATC
  instructions, instructor guidance, regulations, or pilot judgment.
