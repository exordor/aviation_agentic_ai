# Evaluation Protocol

This project uses layered evaluation for schema-constrained Agentic KG-RAG over
retrospective FAA ATCSCC advisories. The goal is to show what each subsystem
contributes without hiding tradeoffs in a single custom score. Schema-guided
extraction, agentic validation/refinement, retrieval, graph evidence, answer
generation, and failure/human-review boundaries are measured separately.

## Why Layered Evaluation

Evidence-grounded ATCSCC advisory question answering has multiple failure modes.
A retriever can find the right advisory while the graph misses the relevant
event relation. A graph traversal can find connected facts while those facts
point to the wrong source advisory or unsupported span. An answer can look
fluent while citing weak evidence. An automated diagnostic can find consistency
issues without becoming human or expert review.

Layered evaluation keeps these cases visible:

- schema-constrained extraction asks whether advisory event records obey the
  application profile and keep provenance;
- agentic validation/refinement asks whether validator, refiner, and critic
  steps reduce unsupported or invalid facts;
- retrieval quality asks whether relevant advisories and contexts are ranked
  near the top;
- graph evidence quality asks whether KG facts and paths cover entities,
  relations, and source provenance;
- answer quality asks whether generated text is faithful, relevant, correct, and
  well cited;
- ontology/KG quality asks whether the schema and triples are parseable,
  constrained, annotated, and source-grounded;
- failure-boundary evaluation asks which failures remain and whether they need
  human review, profile changes, or stricter abstention.

## Why There Is No Overall Score

The project does not compute a mixed overall score. A single score would combine
metrics with different meanings, denominators, and risk profiles. For example,
Recall@5 is an information-retrieval metric, provenance completeness is an
extraction/KG-construction metric, and unsupported claim rate is an answer metric.
Averaging them would make a high retrieval score capable of hiding unsupported
answers, or a clean schema score capable of hiding poor retrieval.

The thesis should therefore report metric groups side by side. GraphRAG should
not be claimed to improve Recall@k unless the retrieval results support that
specific claim.

## Primary Thesis Metrics

### Schema-Constrained Extraction

Primary extraction metrics are:

- schema validity
- structural acceptance rate
- accepted fact count
- rejected fact count
- repaired fact count
- provenance completeness
- evidence-in-source rate
- precision, recall, and F1 against reviewed source-bounded facts

These metrics answer RQ1. Structural validity and semantic correctness must be
reported separately. A record can be schema-valid while still semantically
wrong, incomplete, or unsupported by the advisory text.

### Agentic Validation And Refinement

Primary agentic-loop metrics are:

- schema violation reduction
- unsupported relation reduction
- repair success count
- quarantine/rejection count
- critic rejection count
- post-loop precision, recall, and F1

These metrics answer RQ2. The agentic loop is evaluated as an auditable
extraction and validation workflow, not as autonomous ontology construction.

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
retrieved advisories, chunks, or spans match expected evidence.

Precision@5 and Context Precision@5 use intentionally different denominators.
Precision@5 is strict IR precision over a fixed cutoff and divides by 5 even
when fewer than five hits are returned. Context Precision@5 describes the
precision of the retrieved context actually returned in the top-five window and
therefore divides by the number of returned hits when fewer than five contexts
exist. These fields must not be treated as interchangeable.

Bootstrap confidence intervals are deterministic mean intervals over the
available per-label records. If a CI block has `n=0`, the statistic is undefined
for that subset; the placeholder numeric fields are compatibility values and
must not be interpreted as evidence that the metric is truly zero.

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

### Application Schema And KG Construction

Primary schema/KG metrics are:

- RDF/OWL parse validity
- label/comment coverage
- domain/range completeness
- unsupported class/property count
- provenance completeness
- evidence-in-source rate
- LLM-estimated triple semantic correctness from model-based review

Schema/KG evaluation covers structural, functional, and usability/annotation
quality. KG validation checks that extracted facts stay inside the ATCSCC
application profile and preserve source provenance. Triple semantic correctness
is not fabricated: reviewed source-bounded labels or explicit model-review
artifacts must be cited when semantic correctness is discussed.

### Failure And Human-Review Boundary

Primary failure-boundary metrics are:

- Abstention Accuracy
- False Answer Rate
- False Abstention Rate
- Advisory Boundary Violation Count
- Risk Category Accuracy
- failure candidate count
- profile/gold-boundary failure count
- human-review completion status
- expert-certification status

These metrics are safety-sensitive for aviation and thesis claims. They test
whether the system abstains when scoped advisory evidence is insufficient, and
whether remaining errors are clearly separated from human or expert review.

## Secondary Metrics

Secondary metrics include first relevant rank, retrieved chunk/page IDs, average
related triple count, average supporting triple count, graph path count, answer
presence, retrieval stability, citation stability, KG evidence stability, cost,
latency, index size, and report runtime. These metrics help diagnose failures but
are not the primary thesis claims.

## Mapping To This Project

| Layer | Project reports | Primary metrics |
| --- | --- | --- |
| Schema-constrained extraction | `nasa_atmonto_formal_experiment_scoring.json`, `nasa_atmonto_prediction_output_validation.json`, `nasa_atmonto_cq_evaluation.json` | schema validity, structural acceptance, accepted/rejected facts, precision, recall, F1, provenance completeness |
| Agentic validation/refinement | `nasa_atmonto_s5_s6_agentic_loop.json`, `nasa_atmonto_s5_s6_live_agentic_full_run*.json` | violation reduction, repair/quarantine outcomes, critic rejection, post-loop F1 |
| Retrieval and graph evidence | `nasa_atmonto_s7_retrieval.json`, `nasa_atmonto_s7_graph_health.json` | answer-set F1, target-source hit rate, graph-use rate, graph-context availability, path support |
| Answer generation | `nasa_atmonto_answer_generation.json`, `nasa_atmonto_s7_answer_generation.json`, `nasa_atmonto_s7_llm_answer_generation.json` | answer correctness, evidence faithfulness, citation precision, citation recall, unsupported claim rate, abstention correctness |
| Failure and review boundary | `nasa_atmonto_s7_*review*.json`, `nasa_atmonto_reviewer_defense_audit.json`, `nasa_atmonto_sota_goal_audit.json` | failure candidates, profile/gold-boundary cases, human-review completion, expert-certification status |

Sufficiency evaluation is reported in two modes. The primary benchmark mode is
gold-aided: it uses expected chunks and evidence spans to measure whether
retrieval found the answer-key evidence. The secondary evidence-only diagnostic
does not use gold labels and relies on retrieved context overlap plus boundary
risk terms. These modes must not be described as the same deployment behavior.

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
LLM-as-judge fields must be explicitly marked when used. Automated adversarial
review supports internal error discovery, but any strong aviation-domain
correctness, human-reviewed answer-quality, or certification claim remains
unsupported until a completed human or expert review artifact exists.
