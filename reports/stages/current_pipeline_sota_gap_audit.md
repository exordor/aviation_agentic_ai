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
LLM-backed S7 answer-generation check now exists, with a 60-case broad reviewer
packet and a decision-status importer, but it is intentionally bounded and does
not replace completed expert review decisions.

## Pipeline Audit

| Layer | Current status | Evidence | SOTA gap | Next action |
| --- | --- | --- | --- | --- |
| Source scope | satisfied | Frozen ATCSCC advisory snapshot and processed/aligned records | none for current case study | keep source-family boundaries explicit |
| Data format explanation | satisfied | `reports/stages/atcscc_data_format_and_processing_flow.md` | none | reuse in thesis data section |
| Ontology profile | satisfied | `reports/stages/atcscc_ontology_profile_overview.md`; `data/ontology/curated/nasa_atmonto_atcscc_schema_slice.json` | profile is task-relative, not full ATMONTO completeness | explain application-profile completeness/correctness |
| Event-centric framing | satisfied | `reports/stages/atcscc_event_centric_extraction_framing.md` | none for current case-study framing | reuse in thesis methodology and data-processing sections |
| Competency questions | satisfied | `reports/stages/nasa_atmonto_competency_questions.md` | only 12 primary CQs; deferred cross-source CQs are not scored | keep 12 as primary compact matrix; list deferred CQs separately |
| Reviewed gold | satisfied | `data/evaluation/nasa_atmonto/atcscc_gold_v1.reviewed.jsonl` | gold is retrospective and source-bounded | do not extrapolate to live operations |
| KG extraction systems | satisfied | S0/S1/S1b/S2/S3/S4 scoring in `reports/stages/nasa_atmonto_formal_experiment_scoring.md` | no new gap for S0-S4 extraction | preserve S4 as current strongest system |
| Profile-gap/rejection analysis | satisfied | 288 rejected facts adjudicated as extractor bugs or profile gaps | profile-gap explanations need thesis wording | summarize as application-profile boundary |
| CQ answer-set queryability | satisfied for pre-generation | `reports/stages/nasa_atmonto_cq_query_evaluation.md` | deterministic answer-set scoring is not natural-language answer quality | keep as graph/queryability layer |
| Natural-language answer generation | mostly satisfied for deterministic S7 plus bounded LLM check | `reports/stages/nasa_atmonto_answer_generation.md`, 18-label pilot; `reports/stages/nasa_atmonto_s7_answer_generation.md`, 317-label S7 rerun; `reports/stages/nasa_atmonto_s7_llm_answer_generation.md`, 60-case fixed-budget LLM check; `reports/stages/nasa_atmonto_s7_broad_answer_review_packet.md`, 60-case reviewer packet/CSV; `reports/stages/nasa_atmonto_s7_answer_review_decisions.md`, review-decision validator/status report; `reports/stages/nasa_atmonto_s7_partial_answer_ablation.md`; `reports/stages/nasa_atmonto_s7_llm_failure_review.md`; `reports/stages/nasa_atmonto_s7_human_review_candidates.md`; `reports/stages/nasa_atmonto_s7_candidate_adjudication.md`; `reports/stages/nasa_atmonto_s7_profile_decision.md` | external human/expert review decisions remain future work | keep deterministic S7 as reproducible thesis benchmark and use the 60-case packet plus decision-status report as the review instrument |
| Graph-use gate | mostly satisfied for deterministic S7 plus bounded LLM check | `reports/stages/atcscc_graph_use_plan.md`; `reports/stages/nasa_atmonto_answer_generation.md`; `reports/stages/nasa_atmonto_s7_retrieval.md`; `reports/stages/nasa_atmonto_s7_answer_generation.md`; `reports/stages/nasa_atmonto_s7_llm_answer_generation.md`; `reports/stages/nasa_atmonto_s7_partial_answer_ablation.md` | broad LLM/human answer evaluation remains future work | report routed lexical and source-local guarded dense results conservatively |
| Token-matched vector baseline | satisfied for deterministic S7 | `token_matched_vector_rag`; `token_matched_vector_proxy`; `token_matched_live_tfidf_vector`; `token_matched_dense_embedding_vector`; `routed_token_matched_live_tfidf_graphrag`; `routed_token_matched_dense_graphrag` | no current deterministic S7 gap | preserve token-matched comparisons in thesis tables |
| Graph health/path support | mostly satisfied for S7 diagnostics | `reports/stages/nasa_atmonto_s7_retrieval.md`; `reports/stages/nasa_atmonto_s7_graph_health.md` | graph health is diagnostic rather than semantic truth certification | preserve graph health by CQ group in thesis tables |
| Multi-agent loop | full-set live LLM diagnostic plus deterministic controls | `reports/stages/atcscc_agentic_artifact_contract.md`; `reports/stages/nasa_atmonto_agentic_loop.md`; `reports/stages/atcscc_source_brief.md`; `reports/stages/atcscc_semantic_requirements.md`; `reports/stages/atcscc_technical_implementation_plan.md`; `reports/stages/atcscc_extraction_plan.md`; `reports/stages/atcscc_validation_findings.md`; `reports/stages/atcscc_evidence_support_findings.md`; `reports/stages/atcscc_repair_plan.md`; `reports/stages/atcscc_graph_use_plan.md`; `reports/stages/nasa_atmonto_s5_s6_agentic_loop.md`; `reports/stages/nasa_atmonto_s5_s6_independent_agentic_run.md`; `reports/stages/nasa_atmonto_s5_s6_live_agentic_pilot.md`; `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.md`; `reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md` | S5/S6 now has an S4-wrapper diagnostic, an independent source-derived deterministic run, a 3-sample live pilot, and a 100-record live LLM run; the live run is a negative diagnostic because S6 F1 0.4557 is far below deterministic S6 F1 0.7778 | frame live agents as executable/auditable but not superior to deterministic extraction on semi-structured ATCSCC data |
| Domain-agnostic methodology | mostly satisfied as bounded pilot | `reports/stages/domain_agnostic_ontology_kg_graphrag_methodology_roadmap.md`; `reports/stages/nasa_bga_domain_transfer_pilot.md` | BGA transfer is concept-centric, seed-labelled, and not a full S7-style answer-generation ablation | use it as second-source-family transfer evidence, not broad domain-general proof |

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
   contexts, a 60-case fixed-budget LLM answer-generation check, a 60-case
   broad reviewer packet/CSV, a decision-status importer for filled review
   decisions, a 4-case route-semantics partial-answer ablation, graph-health
   diagnostics by CQ group, a human-review candidate package, deterministic
   candidate adjudication, and a profile-decision what-if that leaves strict
   metrics unchanged. It still lacks externally reviewed answer labels and a
   full cross-domain answer-generation benchmark beyond the bounded BGA
   transfer pilot.
2. **Answer-generation evidence is source-bounded.** The 317-label S7 rerun is
   useful for a reproducible thesis benchmark, but it is not a broad human QA
   benchmark or an operational ATC evaluation.
3. **Graph-path diagnostics are diagnostic, not semantic certification.** S7
   graph health now reports topology, graph-context availability, path support,
   and answer-set recovery by CQ group, while candidate adjudication and the
   profile-decision what-if record profile/gold-boundary failures. These
   metrics do not prove semantic truth or expert usefulness.
4. **The multi-agent method now has full-set live-LLM evidence, but it is a negative diagnostic.**
   The SRD/TIP/extraction-plan/validation/evidence-critique/repair/graph-use
   artifact chain exists. S5/S6 now has both an S4-wrapper diagnostic and an
   independent deterministic extractor/validator/critic/refiner run over S0
   source-derived candidates. A 100-record live LLM run now exercises the
   extractor, validator, critic, and refiner roles under the same hard
   ontology/evidence gates. It completed without failed records, but S6 F1 is
   0.4557 versus 0.7778 for the deterministic independent S6 control, so it is
   evidence for auditable orchestration rather than autonomous-agent superiority.
5. **Transferability now has bounded pilot evidence.** The NASA BGA transfer
   pilot applies the artifact contract to a non-ATM NASA educational reference
   source family with source, CQ, chunking, KG, and validation artifacts. It is
   not a second event-centric operational domain and does not include full
   answer-generation ablations.

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

The deterministic S7 adjudication has now been converted into
`reports/stages/nasa_atmonto_s7_profile_decision.md`, a what-if profile-policy
analysis that corrects the three STAFFING boundary records under a predicate
whitelist while keeping strict main S7 metrics unchanged. The S5/S6 artifact
chain has also been converted into a bounded S4 wrapper
(`reports/stages/nasa_atmonto_s5_s6_agentic_loop.md`) and an independent
source-derived deterministic run
(`reports/stages/nasa_atmonto_s5_s6_independent_agentic_run.md`) plus a
3-sample live LLM pilot
(`reports/stages/nasa_atmonto_s5_s6_live_agentic_pilot.md`) and a full
100-record live LLM diagnostic run
(`reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run.md`;
`reports/stages/nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic.md`). The next
experiments should:

1. treat the live S5/S6 result as a negative control and analyze whether future
   gains should come from deterministic parsing, prompt specialization, or
   supervised extraction rather than unconstrained live LLM extraction;
2. complete the broad review CSV in
   `reports/stages/nasa_atmonto_s7_broad_answer_review_packet.csv`, using
   `reports/stages/nasa_atmonto_s7_human_review_candidates.md` and
   `reports/stages/nasa_atmonto_s7_candidate_adjudication.md` as the focused
   failure/candidate adjudication context.
3. decide whether STAFFING should become a reviewed `impactingCondition`
   profile extension, or whether cause-condition scoring should remain scoped
   to `impactingConditionMessage` for this profile.
4. decide whether the NASA BGA transfer pilot is enough for a methodology
   appendix, or whether the thesis needs a stronger truly non-aviation
   event-source transfer.

Keep the source-local dense guard, graph-health diagnostics, guard rate, and
CQ-group breakdowns as thesis-facing diagnostic tables, but describe them as
diagnostic path/context evidence rather than semantic truth.
