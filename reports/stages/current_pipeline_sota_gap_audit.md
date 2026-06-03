# Current Pipeline SOTA Gap Audit

Date: 2026-06-03

Status: gap audit against the SOTA comparison matrix. This is an internal
planning report, not a scored experiment.

## Direct Assessment

The current pipeline is **complete enough for a KG extraction case study** and
**SOTA-comparable as a layered, retrospective GraphRAG evaluation**, but it is
**not yet complete enough for a broad GraphRAG superiority claim**.

The strongest defensible story is:

> A NASA ATMONTO-derived application profile improves retrospective FAA ATCSCC
> advisory KG extraction when combined with deterministic event parsing,
> schema-slice constraints, validator gating, evidence review, and
> competency-question evaluation.

The current story should not be:

> GraphRAG is generally superior to vector RAG for aviation question answering.

That claim still needs broader human QA labels and evidence that graph routing
improves answers beyond this source-bounded setting. A small fixed-budget
LLM-backed S7 answer-generation check now exists, but it is intentionally
bounded and does not replace expert review.

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
| Natural-language answer generation | mostly satisfied for deterministic S7 plus bounded LLM check | `reports/stages/nasa_atmonto_answer_generation.md`, 18-label pilot; `reports/stages/nasa_atmonto_s7_answer_generation.md`, 317-label S7 rerun; `reports/stages/nasa_atmonto_s7_llm_answer_generation.md`, 24-case fixed-budget LLM check; `reports/stages/nasa_atmonto_s7_partial_answer_ablation.md`; `reports/stages/nasa_atmonto_s7_llm_failure_review.md` | larger human answer labels and broader LLM runs remain future work | keep deterministic S7 as reproducible thesis benchmark and LLM S7 as diagnostic supplement |
| Graph-use gate | mostly satisfied for deterministic S7 plus bounded LLM check | `reports/stages/atcscc_graph_use_plan.md`; `reports/stages/nasa_atmonto_answer_generation.md`; `reports/stages/nasa_atmonto_s7_retrieval.md`; `reports/stages/nasa_atmonto_s7_answer_generation.md`; `reports/stages/nasa_atmonto_s7_llm_answer_generation.md`; `reports/stages/nasa_atmonto_s7_partial_answer_ablation.md` | broad LLM/human answer evaluation remains future work | report routed lexical and source-local guarded dense results conservatively |
| Token-matched vector baseline | satisfied for deterministic S7 | `token_matched_vector_rag`; `token_matched_vector_proxy`; `token_matched_live_tfidf_vector`; `token_matched_dense_embedding_vector`; `routed_token_matched_live_tfidf_graphrag`; `routed_token_matched_dense_graphrag` | no current deterministic S7 gap | preserve token-matched comparisons in thesis tables |
| Graph health/path support | mostly satisfied for S7 diagnostics | `reports/stages/nasa_atmonto_s7_retrieval.md`; `reports/stages/nasa_atmonto_s7_graph_health.md` | graph health is diagnostic rather than semantic truth certification | preserve graph health by CQ group in thesis tables |
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

1. **GraphRAG fairness is bounded, not final.** The project now has
   graph/vector/hybrid, token-matched-vector, routed answer/retrieval modes,
   live lexical-vector retrieval, dense retrieval, source-local dense retrieval
   guards, materialized graph traversal, latency reporting, tokenizer-backed
   context budgets, deterministic answer generation over live retrieved
   contexts, a 24-case fixed-budget LLM answer-generation check, a 4-case
   route-semantics partial-answer ablation, and graph-health diagnostics by CQ
   group. It still lacks broad human-reviewed answer labels and larger LLM
   reruns.
2. **Answer-generation evidence is source-bounded.** The 317-label S7 rerun is
   useful for a reproducible thesis benchmark, but it is not a broad human QA
   benchmark or an operational ATC evaluation.
3. **Graph-path diagnostics are diagnostic, not semantic certification.** S7
   graph health now reports topology, graph-context availability, path support,
   and answer-set recovery by CQ group, but these metrics do not prove semantic
   truth or expert usefulness.
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
- graph answer generation is source-bounded and only partially LLM-tested, not
  an online operational LLM run;
- dense retrieval only becomes competitive after explicit source-local guards,
  so it should not be described as pure embedding superiority.

## Next Executable Experiment

The next experiment should scale and review the v3 S7 LLM check:

1. Rerun the S7 LLM check with more than two selected cases per CQ template
   while preserving the targeted `QT-Q01-ROUTE-SEMANTICS` partial-answer
   contract.
2. Keep the source-local dense guard and report its guard rate whenever dense
   results are compared against lexical or graph-routed modes.
3. Keep graph-health diagnostics by CQ group in the thesis tables, but describe
   them as diagnostic path/context evidence rather than semantic truth.
4. Add a small human/expert review pass for sampled generated answers before
   upgrading the claim from diagnostic LLM evidence to answer-quality evidence.
