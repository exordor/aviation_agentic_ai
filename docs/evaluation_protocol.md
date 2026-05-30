# Evaluation Protocol

This project uses layered evaluation for aviation ontology-grounded GraphRAG.
The goal is to show what each subsystem contributes without hiding tradeoffs in
a single custom score. Retrieval, graph evidence, ontology/KG construction,
answer generation, and safety-aware abstention are measured separately.

## Why Layered Evaluation

Aviation training question answering has multiple failure modes. A retriever can
find the right page while the KG misses the relation. A graph traversal can find
connected paths while those paths point to the wrong source chunks. An answer can
look fluent while citing weak evidence. A system can retrieve relevant training
text but still need to abstain because the question asks for live weather, ATC
clearance, POH procedures, aircraft-specific speeds, or a go/no-go decision.

Layered evaluation keeps these cases visible:

- retrieval quality asks whether relevant chunks are ranked near the top;
- graph evidence quality asks whether KG triples and paths cover entities,
  relations, and source provenance;
- answer quality asks whether generated text is faithful, relevant, correct, and
  well cited;
- ontology/KG quality asks whether the schema and triples are parseable,
  constrained, annotated, and source-grounded;
- safety evaluation asks whether the system abstains when scoped evidence is
  insufficient or the question crosses the advisory boundary.

## Why There Is No Overall Score

The project does not compute a mixed overall score. A single score would combine
metrics with different meanings, denominators, and risk profiles. For example,
Recall@5 is an information-retrieval metric, provenance completeness is a KG
construction metric, and false answer rate is a safety metric. Averaging them
would make a high retrieval score capable of hiding an unsafe answer policy, or a
clean ontology score capable of hiding poor retrieval.

The thesis should therefore report metric groups side by side. GraphRAG should
not be claimed to improve Recall@k unless the retrieval results support that
specific claim.

## Primary Thesis Metrics

### Retrieval

Primary retrieval metrics are:

- Recall@5
- Recall@10
- MRR@5
- MRR@10
- NDCG@10
- Precision@5
- Context Precision@5
- Context Recall

These follow mainstream IR and RAG practice. Recall@k, Precision@k, MRR@k, and
NDCG@k measure ranked retrieval quality. Context Precision@5 and Context Recall
map the RAGAS-style context layer to the project gold labels by checking whether
retrieved chunks, pages, or spans match expected evidence.

### Graph Evidence And Paths

Primary graph evidence metrics are:

- Key Entity Coverage
- Relation Coverage
- Path Recall@k
- Path Precision@k
- Supporting Path Rate
- Average Path Length
- Irrelevant Path Rate

Key Entity Coverage and Relation Coverage measure whether graph evidence covers
the entities and relation intent implied by a competency question. Path Recall@k,
Path Precision@k, Supporting Path Rate, and Irrelevant Path Rate are currently
heuristic where no model-based graph path review is cited. They use entity,
relation, source-page, and gold-chunk overlap and must be reported as heuristic
diagnostics.

### Answer Generation

Primary answer metrics are:

- Faithfulness
- Answer Correctness
- Answer Relevance
- Citation Completeness
- Citation Precision
- Citation Recall

Faithfulness, answer relevance, and answer correctness reflect RAGAS/ARES-style
answer evaluation. Current deterministic reports use source-citation and answer
key overlap heuristics. Optional LLM-as-judge fields may be added, but any such
scores must be marked as LLM-judge scores and not confused with human review.

### Ontology And KG Construction

Primary ontology/KG metrics are:

- RDF/OWL parse validity
- label/comment coverage
- domain/range completeness
- unsupported class/property count
- provenance completeness
- evidence-in-source rate
- LLM-estimated triple semantic correctness from model-based review

Ontology evaluation covers structural, functional, and usability/annotation
quality. KG validation checks that extracted triples stay inside the curated
ontology and preserve source provenance. Triple semantic correctness is not
fabricated: the triple semantic review report initializes annotation fields as
model-review pending, and `triple_semantic_llm_review` must be cited for
LLM-estimated semantic correctness.

### Safety And Abstention

Primary safety metrics are:

- Abstention Accuracy
- False Answer Rate
- False Abstention Rate
- Advisory Boundary Violation Count
- Risk Category Accuracy

These metrics are safety-sensitive for aviation. Benchmark v2 no-answer labels
and operational boundary risk categories test whether the system abstains when
the scoped PHAK Chapter 4 evidence is insufficient.

## Secondary Metrics

Secondary metrics include first relevant rank, retrieved chunk/page IDs, average
related triple count, average supporting triple count, graph path count, answer
presence, retrieval stability, citation stability, KG evidence stability, cost,
latency, index size, and report runtime. These metrics help diagnose failures but
are not the primary thesis claims.

## Mapping To This Project

| Layer | Project reports | Primary metrics |
| --- | --- | --- |
| Retrieval | `retrieval_ablation*.json`, `chunking_comparison.json`, `hybrid_rag*.json` | Recall@5, Recall@10, Precision@5, MRR@5, MRR@10, NDCG@10, Context Precision@5, Context Recall |
| Graph evidence/path retrieval | `graph_traversal_ablation*.json`, `retrieval_ablation*.json` | Key Entity Coverage, Relation Coverage, Path Recall@5, Path Precision@5, Supporting Path Rate, Average Path Length, Irrelevant Path Rate |
| Answer generation | `answer_evaluation.json`, `hybrid_rag*.json` | Faithfulness, Answer Correctness, Answer Relevance, Citation Completeness, Citation Precision, Citation Recall |
| Ontology/KG | `curated_ontology_evaluation.json`, `kg_validation.json`, `kg_extraction_comparison.json`, `triple_semantic_review_sample.json`, `triple_semantic_llm_review.json` | RDF/OWL validity, annotation coverage, domain/range completeness, unsupported schema counts, provenance completeness, evidence-in-source rate, LLM-estimated triple semantic review |
| Safety/abstention | `sufficiency_evaluation.json`, `robustness_evaluation.json`, `answer_evaluation.json` | Abstention Accuracy, False Answer Rate, False Abstention Rate, Boundary Violation Count, Risk Category Accuracy |

## LLM-As-Judge Limitations

LLM-as-judge evaluation can be useful for faithfulness, answer relevance, and
answer correctness, but it has limitations:

- judge prompts and model versions affect scores;
- judges can reward fluent but weakly grounded answers;
- judges can miss aviation boundary violations;
- repeated runs may not be stable unless model, prompt, and temperature are
  fixed;
- LLM judgment is not external aviation expert certification.

For this project, deterministic metrics and provenance checks are the default.
LLM-as-judge fields must be explicitly marked when used. Human review is absent
in this project. LLM-as-judge supports internal error discovery, but any strong
aviation-domain correctness or certification claim remains unsupported.
