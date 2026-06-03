# Current Pipeline SOTA Gap Audit

Date: 2026-06-03

Status: gap audit against the SOTA comparison matrix. This is an internal
planning report, not a scored experiment.

## Direct Assessment

The current pipeline is **complete enough for a KG extraction case study** and
**not yet complete enough for a full SOTA GraphRAG claim**.

The strongest defensible story is:

> A NASA ATMONTO-derived application profile improves retrospective FAA ATCSCC
> advisory KG extraction when combined with deterministic event parsing,
> schema-slice constraints, validator gating, evidence review, and
> competency-question evaluation.

The current story should not be:

> GraphRAG is generally superior to vector RAG for aviation question answering.

That claim still needs graph-use routing, token-matched controls, and a larger
answer-generation benchmark.

## Pipeline Audit

| Layer | Current status | Evidence | SOTA gap | Next action |
| --- | --- | --- | --- | --- |
| Source scope | satisfied | Frozen ATCSCC advisory snapshot and processed/aligned records | none for current case study | keep source-family boundaries explicit |
| Data format explanation | satisfied | `reports/stages/atcscc_data_format_and_processing_flow.md` | none | reuse in thesis data section |
| Ontology profile | satisfied | `reports/stages/atcscc_ontology_profile_overview.md`; `schema/atcscc_tmi_profile.yaml` | profile is task-relative, not full ATMONTO completeness | explain application-profile completeness/correctness |
| Event-centric framing | satisfied | `reports/stages/atcscc_event_centric_extraction_framing.md` | none for current case-study framing | reuse in thesis methodology and data-processing sections |
| Competency questions | satisfied | `reports/stages/nasa_atmonto_competency_questions.md` | only 12 primary CQs; deferred cross-source CQs are not scored | keep 12 as primary compact matrix; list deferred CQs separately |
| Reviewed gold | satisfied | `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl` | gold is retrospective and source-bounded | do not extrapolate to live operations |
| KG extraction systems | satisfied | S0/S1/S1b/S2/S3/S4 scoring in `reports/stages/nasa_atmonto_formal_experiment_scoring.md` | no new gap for S0-S4 extraction | preserve S4 as current strongest system |
| Profile-gap/rejection analysis | satisfied | 288 rejected facts adjudicated as extractor bugs or profile gaps | profile-gap explanations need thesis wording | summarize as application-profile boundary |
| CQ answer-set queryability | satisfied for pre-generation | `reports/stages/nasa_atmonto_cq_query_evaluation.md` | deterministic answer-set scoring is not natural-language answer quality | keep as graph/queryability layer |
| Natural-language answer generation | partial | `reports/stages/nasa_atmonto_answer_generation.md`, 18 labels | small label count; not yet rerun over live retrieved contexts | rerun answer generation over routed live retrieval outputs |
| Graph-use gate | mostly satisfied for retrieval-only S7 | `reports/stages/atcscc_graph_use_plan.md`; `reports/stages/nasa_atmonto_answer_generation.md`; `reports/stages/nasa_atmonto_s7_retrieval.md` | retrieval-only gate is complete enough for current SOTA comparison; answer-generation rerun remains | use routed retrieval outputs downstream |
| Token-matched vector baseline | satisfied for retrieval-only S7 | `token_matched_vector_rag`; `token_matched_vector_proxy`; `token_matched_live_tfidf_vector`; `token_matched_dense_embedding_vector`; `routed_token_matched_live_tfidf_graphrag`; `routed_token_matched_dense_graphrag` | none for retrieval-only S7 | carry token-matched modes into answer-generation rerun |
| Graph health/path support | partial | `reports/stages/nasa_atmonto_s7_retrieval.md` | route-level path support exists; full graph component/connectivity diagnostics remain limited | add graph health by CQ group |
| Multi-agent loop | partial | `reports/stages/atcscc_agentic_artifact_contract.md` | contract exists, but SRD/TIP/extraction/validation/evidence artifacts are incomplete | write artifacts before claiming agentic pipeline |
| Domain-agnostic methodology | partial | `reports/stages/domain_agnostic_ontology_kg_graphrag_methodology_roadmap.md` | only validated in ATM so far | keep second-domain transfer as future work |

## What Is Already Strong

The strongest parts of the project are:

1. **Scope discipline:** ATCSCC advisories are treated as one source family,
   while NASA/FAA PDFs are reference material unless explicitly added as a
   second source family.
2. **Application-profile logic:** the project uses a compact ATCSCC slice of
   ATMONTO because the source and CQs do not support the full ontology.
3. **Layer separation:** schema validity, semantic correctness, evidence
   support, CQ queryability, and answer generation are not collapsed into one
   metric.
4. **Negative-result handling:** the all-zero `S1_llm_only` run is correctly
   treated as an ontology-interface/canonicalization failure, not as proof that
   LLM extraction has zero semantic quality.
5. **Profile-gap accounting:** rejected facts are triaged instead of silently
   counted as generic failures.

## Main Weaknesses Against SOTA

1. **GraphRAG fairness is incomplete.** The project now has graph/vector/hybrid,
   token-matched-vector, routed answer/retrieval modes, live lexical-vector
   retrieval, dense retrieval, materialized graph traversal, latency reporting,
   and tokenizer-backed context budgets, but still needs answer generation over
   live retrieved contexts before making a strong GraphRAG comparison.
2. **Answer-generation evidence is small.** Eighteen labels are useful for a
   pilot, but not enough for a thesis-level answer-generation superiority
   claim.
3. **Graph-path diagnostics are partial.** Queryability metrics and S7 route
   path support exist, but graph health by CQ group is not complete.
4. **The multi-agent method is not yet executable.** The contract exists, but
   the actual SRD/TIP/validation/evidence-critique/repair artifacts need to be
   produced and wired into runs.
5. **Transferability is still a thesis direction.** The domain-agnostic
   methodology is credible, but it is not validated outside ATCSCC yet.

## Claim-Safe Story

For the current thesis/report, the story should be:

> The project studies event-centric semantic KG extraction from semi-structured
> FAA ATCSCC advisories. It uses NASA ATMONTO as a reference ontology, but
> constructs a task-specific ATCSCC application profile rather than using the
> full ontology. The experiment shows that a hybrid deterministic-plus-semantic
> extraction pipeline can improve source-bounded KG construction and CQ
> queryability under explicit evidence and schema constraints. GraphRAG is then
> evaluated as a downstream retrieval/answering layer, with current results
> showing useful but not yet final evidence for graph-aware retrieval.

## Unsafe Story

Avoid this storyline:

> We built a complete NASA ATMONTO KG and proved GraphRAG is better for ATM.

That version is not supported because:

- the ontology is a profile slice, not all ATMONTO;
- ATCSCC advisories expose a narrow event ABox, not the whole NAS;
- graph answer generation is currently a small pilot;
- answer generation has not been rerun over live retrieved contexts.

## Next Executable Experiment

The next experiment should be S7 answer-generation rerun:

1. Reuse the retrieval outputs from `routed_token_matched_live_tfidf_graphrag`
   and `routed_token_matched_dense_graphrag`.
2. Run natural-language answer generation over those routed contexts.
3. Compare answer correctness, citation recall, unsupported-claim rate, token
   budget, and latency by CQ group.
4. Keep the dense retrieval result framed as a negative result unless answer
   generation shows a defensible downstream benefit.
