# SOTA Comparison Matrix for the ATCSCC / NASA ATMONTO Experiment

Date: 2026-06-03

Status: SOTA-alignment audit. This report maps the current project artifacts
against literature-derived criteria. It is not a new experiment result.

## Purpose

The project should be compared against SOTA as a pipeline, not as a single
"GraphRAG beats RAG" claim. The appropriate comparison target is:

> Event-centric, ontology-guided, evidence-grounded KG extraction with layered
> GraphRAG evaluation over a retrospective domain corpus.

For this project, the domain corpus is FAA ATCSCC advisories, the reference
schema is a NASA ATMONTO-derived ATCSCC profile, and the evaluation contract is
defined by competency questions, reviewed gold facts, evidence spans, and
source-bounded answer tests.

## Literature-Derived Criteria

| SOTA criterion | Reference input | Required local evidence | Current local artifact | Status |
| --- | --- | --- | --- | --- |
| Event-centric semantic extraction | Event extraction and OBIE framing transferred to ATCSCC advisories | Explicit event type, event arguments, temporal fields, cause/status fields, and provenance links | `reports/stages/atcscc_data_format_and_processing_flow.md`; `reports/stages/atcscc_ontology_profile_overview.md`; `reports/stages/atcscc_event_centric_extraction_framing.md` | satisfied for the ATCSCC case-study framing |
| Ontology-grounded KG construction | Ontology-grounded KGC and LLM ontology-engineering papers | Reference ontology/profile, schema slice, predicate canonicalization, validator gate, profile-gap accounting | `data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json`; `reports/stages/nasa_atmonto_formal_experiment_scoring.md`; `reports/stages/atcscc_ontology_profile_overview.md` | satisfied for the ATCSCC profile |
| CQ-driven scope and evaluation | Ontology engineering and competency-question methodology | Compact primary CQs mapped to fields, predicates, validation, and query patterns | `reports/stages/nasa_atmonto_competency_questions.md`; `reports/stages/nasa_atmonto_cq_query_evaluation.md` | satisfied for 12 primary CQs |
| Evidence-grounded extraction | OBIE, claim KG, and GraphRAG evaluation practice | Every accepted fact has source ID and evidence span or explicit support record | `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl`; `reports/stages/nasa_atmonto_formal_experiment_scoring.md` | satisfied for scored extraction |
| Schema validity separated from semantic correctness | KG quality and ontology evaluation practice | Report schema violations, semantic P/R/F1, evidence support, and profile gaps separately | `reports/stages/nasa_atmonto_formal_experiment_scoring.md` | satisfied |
| Multi-agent artifact pipeline | Multi-agent ontology-generation paper | Source brief, SRD, TIP, extraction plan, validation findings, evidence critique, repair plan, graph-use plan | `reports/stages/atcscc_agentic_artifact_contract.md` | planned, contract exists but artifacts are incomplete |
| Layered GraphRAG evaluation | GraphRAG-Bench; RAG vs GraphRAG; When to use Graphs in RAG | Separate graph construction, retrieval, answer generation, rationale/citation, failure analysis, profile-decision sensitivity, and cost/token reporting | `reports/stages/nasa_atmonto_cq_query_evaluation.md`; `reports/stages/nasa_atmonto_answer_generation.md`; `reports/stages/nasa_atmonto_s7_retrieval.md`; `reports/stages/nasa_atmonto_s7_answer_generation.md`; `reports/stages/nasa_atmonto_s7_llm_answer_generation.md`; `reports/stages/nasa_atmonto_s7_partial_answer_ablation.md`; `reports/stages/nasa_atmonto_s7_candidate_adjudication.md`; `reports/stages/nasa_atmonto_s7_profile_decision.md` | mostly satisfied for deterministic S7 plus bounded LLM check; broad human/LLM answer evaluation remains future work |
| Fair RAG-vs-GraphRAG comparison | RAG vs GraphRAG; When to use Graphs in RAG | Vector-only, graph-only, hybrid, routed graph-use gate, token-matched vector control | Retrieval and answer-generation reports now include source/vector/token-matched-vector/live lexical-vector/dense-vector/source-local guarded dense/materialized graph/hybrid/routed modes, plus a 60-case fixed-budget LLM run over routed live/dense GraphRAG contexts | mostly satisfied for deterministic S7; bounded LLM evidence is diagnostic, not final |
| Queryability rather than ontological purity | KG quality for RAG-oriented systems | CQ answer-set precision/recall/F1 by predicate and question type | `reports/stages/nasa_atmonto_cq_query_evaluation.md` | satisfied for pre-generation answer sets |
| Graph health and path support | GraphRAG pipeline evaluation | Node/edge coverage, component/connectivity diagnostics, path support rate for graph-worthy CQs | `reports/stages/nasa_atmonto_s7_retrieval.md`; `reports/stages/nasa_atmonto_s7_graph_health.md` reports topology, graph-context availability, path support, answer recovery, and abstention behavior by CQ group | mostly satisfied as diagnostic graph-health evidence |
| Abstention and unsupported-claim control | Evidence-grounded QA and GraphRAG safety practice | Unsupported triple rate, abstention correctness, rejected/unsupported facts, candidate adjudication, profile-decision sensitivity, claim-safe answer policy | `reports/stages/nasa_atmonto_answer_generation.md`; `reports/stages/nasa_atmonto_s7_answer_generation.md`; `reports/stages/nasa_atmonto_s7_llm_answer_generation.md`; `reports/stages/nasa_atmonto_s7_llm_failure_review.md`; `reports/stages/nasa_atmonto_s7_candidate_adjudication.md`; `reports/stages/nasa_atmonto_s7_profile_decision.md`; `reports/stages/nasa_atmonto_formal_experiment_scoring.md` | mostly satisfied for deterministic S7 plus bounded LLM check; needs broader human/expert answer review |
| Cost and reproducibility reporting | Fair retrieval/GraphRAG benchmarking | Token budget, latency, deterministic source scope, frozen data version, rerunnable commands | frozen source/gold scope exists; S7 retrieval and answer-generation reports use tokenizer-backed token budgets and latency reporting | mostly satisfied for deterministic S7 |
| Transferability to another domain | Domain-agnostic ontology/KG/GraphRAG methodology | Same artifact contract applied to a non-ATM corpus with only domain artifacts changed | `reports/stages/domain_agnostic_ontology_kg_graphrag_methodology_roadmap.md` | planned |

## Current SOTA Position

The project is already SOTA-comparable at the **KG construction and
ontology-constrained extraction** layer:

- it has a frozen retrospective corpus;
- it uses a NASA ATMONTO-derived application profile rather than free-form
  labels;
- it has reviewed gold labels;
- it separates schema conformance, semantic correctness, evidence support, and
  profile gaps;
- it compares multiple extraction systems, including a deterministic backbone,
  canonicalized LLM baseline, schema-slice LLM, validator/repair condition, and
  hybrid backbone-enrichment system.

The project is only partially SOTA-comparable at the **GraphRAG** layer:

- deterministic CQ answer-set evaluation exists;
- a small source/vector/graph/hybrid answer-generation pilot exists;
- a retrieval-only S7 graph-use gate exists over 317 CQ-derived cases;
- live lexical-vector retrieval, dense-vector retrieval, and tokenizer-backed
  token matching exist;
- source-local dense retrieval guards now exist and are reported with guard
  rates;
- materialized graph traversal and latency reporting exist;
- graph health by CQ group now exists;
- deterministic answer generation over live retrieved contexts now exists;
- a 60-case fixed-budget LLM answer-generation check over routed live/dense
  GraphRAG contexts now exists;
- a 4-case controlled route-semantics partial-answer ablation now exists;
- the bounded LLM report now includes CQ-template breakdowns;
- a manual failure review now shows that source-local dense source misses and
  wrong-context abstentions were addressed in the selected post-guard rerun,
  while the partial-answer ablation isolates the compound-CQ answer-contract
  issue;
- a human-review candidate package now exists for the remaining failures and
  coverage-success examples;
- deterministic candidate adjudication classifies the three remaining
  cause-condition failures as profile/gold-boundary cases without changing the
  strict S7 metrics;
- a profile-decision what-if now shows that a predicate-whitelist policy would
  correct those three selected records while preserving strict main metrics as
  the reported benchmark;
- external human/expert answer review remains incomplete.

The project is currently a planned, not completed, example of the **multi-agent
artifact pipeline**:

- the role contract exists;
- the SRD/TIP/extraction-plan/validation/evidence-critique/repair/graph-use
  artifacts still need to be written and connected to executable runs.

## Claim-Safe SOTA Wording

Use this wording in thesis or defense material:

> This project implements a retrospective, event-centric case study of
> ontology-guided KG extraction for FAA ATCSCC advisories. It is SOTA-aligned in
> its use of competency questions, a NASA ATMONTO-derived application profile,
> reviewed gold facts, evidence-span grounding, schema validation, and layered
> KG/query/answer evaluation. It also includes a bounded LLM answer-generation
> check over frozen S7 retrieved contexts and graph-health diagnostics by CQ
> group. The 60-case fixed-budget LLM check shows strong live lexical routed
> behavior and a qualified source-local guarded dense result under the same
> frozen context policy, with remaining failures concentrated in
> cause-condition over-answer/profile-boundary cases that have been
> deterministically adjudicated; a profile-decision what-if records the
> predicate-whitelist sensitivity but does not replace strict metrics. It does
> not claim live
> operational readiness, pure dense embedding superiority, or universal GraphRAG
> superiority. The remaining SOTA gap is human/expert answer review and
> second-domain transfer while preserving citation, unsupported-claim, token,
> guard-rate, failure-adjudication, and latency reporting.

Avoid these claims:

- "GraphRAG is better than RAG" without route-specific and token-matched
  evidence.
- "The NASA ATMONTO ontology is complete" for ATCSCC operations.
- "All ATMONTO knowledge is extracted" from ATCSCC advisories.
- "The system is operationally ready" for air traffic decisions.

## Next SOTA Upgrade

The next executable upgrade should target the remaining GraphRAG gaps in this
order:

1. Run the human/expert review pass using
   `reports/stages/nasa_atmonto_s7_human_review_candidates.md` and
   `reports/stages/nasa_atmonto_s7_candidate_adjudication.md`.
2. Keep graph-health, guard-rate, and LLM CQ-group breakdowns as the thesis-facing
   diagnostic tables.
3. Use the profile-decision what-if as the evidence package for deciding whether
   STAFFING becomes a reviewed profile extension or remains message-only scoring.
