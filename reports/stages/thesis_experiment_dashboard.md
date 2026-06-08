# Thesis Experiment Dashboard

- Source policy: aggregate existing reports; do not recompute experiments unnecessarily.
- Scoring policy: layered metrics; no mixed overall score.
- Advisory boundary: Aviation learning and decision support only; does not replace POH/AFM, approved checklists, ATC instructions, instructor guidance, regulations, or pilot judgment.

## Experiment Inventory

| Report | Present | Dataset | Questions | Layers | Human review present | LLM review available |
| --- | ---: | --- | ---: | --- | ---: | ---: |
| `thesis_claims_review` | True | not_dataset_specific | n/a | claim_safety | False | False |
| `evaluation_protocol_review` | True | not_dataset_specific | n/a | evaluation_protocol | False | False |
| `benchmark_v2_summary` | True | benchmark_v2_120 | 120 | benchmark_validation | False | False |
| `retrieval_ablation_benchmark_v2` | True | benchmark_v2_120 | 120 | retrieval, kg_evidence | False | False |
| `graph_traversal_ablation_benchmark_v2` | True | benchmark_v2_120 | 120 | retrieval, graph_paths | False | False |
| `sufficiency_evaluation` | True | benchmark_v2_120 | 120 | safety_abstention | False | False |
| `benchmark_reviewed_subset_summary` | True | benchmark_v2_reviewed_subset_60 | 60 | benchmark_llm_review_scaffold | False | False |
| `benchmark_llm_review` | True | benchmark_v2_reviewed_subset_or_v2 | n/a | benchmark_llm_review, llm_judge | False | True |
| `benchmark_llm_rewrite_proposals` | True | benchmark_v2_reviewed_subset_or_v2 | n/a | benchmark_llm_review | False | True |
| `answer_evaluation_benchmark_subset` | True | answer_eval_subset | n/a | answer_generation, safety_abstention | False | False |
| `answer_generation_benchmark_subset` | True | answer_eval_subset | 3 | answer_generation | False | False |
| `answer_llm_judge` | True | answer_eval_subset | n/a | answer_generation, llm_judge | False | True |
| `triple_semantic_llm_review` | True | triple_semantic_review_sample | n/a | ontology_kg, llm_judge | False | True |
| `graph_path_llm_review` | True | benchmark_v2_120 | n/a | graph_paths, llm_judge | False | True |
| `llm_review_consistency` | True | llm_review_artifacts | n/a | llm_judge, claim_safety | False | True |
| `chunking_implementation_audit` | True | benchmark_v2_120 | n/a | retrieval, evaluation_protocol | False | False |
| `chunking_comparison_benchmark_v2` | True | benchmark_v2_120 | n/a | retrieval | False | False |
| `chunking_comparison_benchmark_v2_budget` | True | benchmark_v2_120 | n/a | retrieval | False | False |
| `chunking_topk_sensitivity_benchmark_v2` | True | benchmark_v2_120 | n/a | retrieval | False | False |
| `chunking_category_analysis_benchmark_v2` | True | benchmark_v2_120 | n/a | retrieval | False | False |
| `chunking_failure_cards_benchmark_v2` | True | benchmark_v2_120 | n/a | retrieval, failure_analysis | False | False |
| `pdf_extraction_comparison` | True | phak_ch4_pdf_first_pages_heading_sample | n/a | pdf_extraction, claim_safety | False | False |
| `pdf_hybrid_repair_report` | True | phak_ch4_pdf_docling_items | n/a | pdf_extraction, text_fidelity | False | False |
| `pdf_backend_chunking_comparison` | True | benchmark_v2_120 | 120 | pdf_extraction, retrieval | False | False |
| `nasa_source_discovery` | True | nasa_bga_aerodynamics_full_landing_page_manifest | n/a | source_expansion, claim_safety | False | False |
| `nasa_source_ingestion` | True | nasa_bga_aerodynamics_full_corpus | n/a | source_expansion | False | False |
| `nasa_source_validation` | True | nasa_bga_aerodynamics_full_corpus | n/a | source_expansion, claim_safety | False | False |
| `nasa_chunking_summary` | True | nasa_bga_lessons_in_aerodynamics_subset | n/a | source_expansion, retrieval | False | False |
| `ontology_boundary_nasa` | True | nasa_bga_lessons_in_aerodynamics_subset | n/a | source_expansion, ontology_kg | False | False |
| `nasa_kg_validation` | True | nasa_bga_lessons_in_aerodynamics_subset | n/a | source_expansion, ontology_kg | False | False |
| `nasa_benchmark_summary` | True | nasa_bga_lessons_seed_50 | 50 | source_expansion, benchmark_validation | False | False |
| `cross_source_ontology_validation` | True | faa_phak_nasa_cross_source_seed_30 | 30 | source_expansion, ontology_kg | False | False |
| `multisource_retrieval_smoke` | True | faa_phak_nasa_smoke_35 | 25 | source_expansion, retrieval | False | False |
| `nasa_bga_domain_transfer_pilot` | True | nasa_bga_aerodynamics_reference_transfer | n/a | source_expansion, ontology_kg, evaluation_protocol, transfer_pilot, claim_safety | False | False |
| `deepseek_v4pro_implementation_remediation` | True | not_dataset_specific | n/a | implementation_review, claim_safety | False | False |
| `kg_extraction_comparison` | True | 35_question_expanded | n/a | ontology_kg | False | False |
| `curated_ontology_evaluation` | True | not_dataset_specific | n/a | ontology_kg | False | False |
| `triple_semantic_review_sample` | True | triple_semantic_review_sample | n/a | ontology_kg, llm_review_scaffold | False | False |
| `answer_evaluation` | True | 10_cq_answer_subset | n/a | answer_generation, safety_abstention | False | False |
| `robustness_evaluation` | True | robustness_10_cases | n/a | safety_abstention, robustness | False | False |
| `benchmark_review_pack` | True | not_dataset_specific | 120 | benchmark_llm_review_scaffold | False | False |
| `nasa_atmonto_formal_experiment_scoring` | True | atcscc_gold_100 | n/a | ontology_kg, evaluation_protocol | False | False |
| `nasa_atmonto_prediction_output_validation` | True | atcscc_prediction_outputs | n/a | ontology_kg, evaluation_protocol, claim_safety | False | False |
| `nasa_atmonto_cq_evaluation` | True | atcscc_cq_answer_sets | n/a | ontology_kg, answer_generation, evaluation_protocol | False | False |
| `nasa_atmonto_s5_s6_agentic_loop` | True | not_dataset_specific | n/a |  | False | False |
| `nasa_atmonto_s5_s6_independent_agentic_run` | True | not_dataset_specific | n/a |  | False | False |
| `nasa_atmonto_s5_s6_live_agentic_pilot` | True | atcscc_s5_s6_live_agentic_pilot_3 | n/a | ontology_kg, llm_agents, evaluation_protocol | False | False |
| `nasa_atmonto_s5_s6_live_agentic_full_run` | True | atcscc_s5_s6_live_agentic_full_run_100 | n/a | ontology_kg, llm_agents, evaluation_protocol | False | False |
| `nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic` | True | atcscc_s5_s6_live_agentic_full_run_100 | n/a | ontology_kg, llm_agents, failure_analysis, claim_safety | False | False |
| `nasa_atmonto_sota_goal_audit` | True | atcscc_thesis_claim_gate | n/a | claim_safety, evaluation_protocol, failure_analysis | False | False |
| `nasa_atmonto_reviewer_defense_audit` | True | atcscc_thesis_claim_gate | n/a | claim_safety, failure_analysis, evaluation_protocol | False | False |
| `nasa_atmonto_s7_retrieval` | True | atcscc_s7_source_bounded_317 | n/a | retrieval, graph_paths, evaluation_protocol | False | False |
| `nasa_atmonto_s7_graph_health` | True | atcscc_s7_source_bounded_317 | n/a | retrieval, graph_paths, claim_safety | False | False |
| `nasa_atmonto_s7_llm_answer_generation` | True | atcscc_s7_source_bounded_60 | n/a | answer_generation, graph_paths, safety_abstention | False | True |
| `nasa_atmonto_s7_human_review_candidates` | True | atcscc_s7_review_candidate_queue_9 | n/a | answer_generation, llm_review_scaffold, failure_analysis | False | False |
| `nasa_atmonto_s7_broad_answer_review_packet` | True | atcscc_s7_source_bounded_60 | n/a | answer_generation, llm_review_scaffold, failure_analysis | False | False |
| `nasa_atmonto_s7_answer_review_decisions` | True | atcscc_s7_source_bounded_60 | n/a | answer_generation, human_review_scaffold, claim_safety, failure_analysis | False | False |
| `nasa_atmonto_s7_answer_review_import` | True | atcscc_s7_source_bounded_60 | n/a | answer_generation, human_review_scaffold, claim_safety | False | False |
| `nasa_atmonto_s7_candidate_adjudication` | True | atcscc_s7_review_candidate_queue_9 | n/a | answer_generation, failure_analysis, claim_safety | False | False |
| `nasa_atmonto_s7_profile_decision` | True | atcscc_s7_profile_decision_what_if_3 | n/a | answer_generation, failure_analysis, claim_safety, evaluation_protocol | False | False |

## RQ-To-Evidence Matrix

| RQ | Evidence reports | Primary metrics | Claim strength | Remaining gaps |
| --- | --- | --- | --- | --- |
| RQ1 schema-constrained event extraction | nasa_atmonto_formal_experiment_scoring, nasa_atmonto_prediction_output_validation, nasa_atmonto_cq_evaluation, atcscc_ontology_profile_overview | schema validity, structural acceptance rate, triple precision/recall/F1, evidence-span containment, provenance completeness | strong | Semantic correctness remains reviewed-subset/profile-relative, not full ontology correctness. |
| RQ2 agentic validation-refinement | nasa_atmonto_s5_s6_agentic_loop, nasa_atmonto_s5_s6_independent_agentic_run, nasa_atmonto_s5_s6_live_agentic_pilot, nasa_atmonto_s5_s6_live_agentic_full_run, nasa_atmonto_s5_s6_live_agentic_full_run_diagnostic | schema violation rate, repair count, quarantine/rejection count, unsupported relation rate, post-loop extraction F1 | moderate | The agent loop is not autonomous ontology construction; it is a bounded diagnostic and repair loop for advisory-event extraction. |
| RQ3 KG-RAG grounding vs vector-only RAG | nasa_atmonto_s7_retrieval, nasa_atmonto_s7_graph_health, nasa_atmonto_s7_llm_answer_generation | answer-set F1, target-source hit rate, citation precision, citation recall, evidence faithfulness, unsupported claim rate | moderate | This is source-bounded ATCSCC evidence, not a universal claim that GraphRAG beats vector-only retrieval. |
| RQ4 failure modes and human-review boundary | nasa_atmonto_s7_llm_answer_generation, nasa_atmonto_s7_human_review_candidates, nasa_atmonto_s7_answer_review_import, nasa_atmonto_s7_answer_review_decisions, nasa_atmonto_s7_candidate_adjudication, nasa_atmonto_s7_profile_decision, nasa_atmonto_reviewer_defense_audit | failure candidate count, profile/gold-boundary failures, Unsupported Claim Rate, Abstention Correctness, human_review_completed, expert_certification_completed | moderate | Human/expert review remains separate from automated diagnostics; operational ATC use remains out of scope. |

## Dataset Usage Matrix

| Dataset | Purpose | Evidence role | Main claim support | Limitations |
| --- | --- | --- | --- | --- |
| 10-CQ pilot | demo and qualitative answer inspection | pilot | partial | too small for main thesis retrieval claims |
| 35-question expanded | pilot ablation and KG extraction comparison | pilot | partial | pilot-sized and not the main benchmark |
| benchmark v2 120 | main thesis retrieval and safety benchmark | main_thesis_benchmark | provisional_internal_pending_llm_review | machine-seeded and requires model-based naturalness review |
| benchmark v2 chunking experiment | chunking strategy comparison under top-k, fixed-budget, and category views | retrieval_design_diagnostic | partial_benchmark_specific | implementation-maturity labels required; top-k context volume differs by chunk size |
| PHAK PDF extraction backend comparison | compare PDF structure extraction and hybrid text repair | pdf_extraction_diagnostic | partial_backend_evidence | Docling structure is document-specific and text repairs are conservative |
| benchmark reviewed subset 60 | model-based review scaffold for high-value labels | llm_review_scaffold | pending_llm_review | review scaffold only; no human review or external aviation expert certification |
| LLM review artifacts | model-based benchmark, triple, graph-path, answer, and consistency review | llm_judge | internal_llm_review_only | model-based internal review; no human or external expert certification |
| NASA BGA full landing-page corpus | second authoritative educational source collection from NASA Glenn BGA | source_collection | source_collection_only | collected as educational web evidence; interactive pages may expose limited text |
| NASA Lessons in Aerodynamics subset | source-expansion experiment for ontology boundary, chunking, KG, and seed QA | domain_transfer_pilot | bounded_second_source_family_transfer | bounded concept-centric educational-source transfer pilot; no external aviation certification, no human review, no operational readiness, and no full S7-style answer-generation ablation |
| answer-eval subset | answer citation and faithfulness heuristics | pilot | partial | stratified subset; deterministic heuristic scores unless annotated |
| ATCSCC S7 source-bounded answer set | SOTA-comparable GraphRAG answer-generation diagnostic over frozen retrieved ATCSCC contexts | s7_graphrag_answer_generation | source_bounded_diagnostic | bounded retrospective LLM run; broad 60-case reviewer packet, reviewed-CSV import gate, and decision-status report exist but external review decisions remain incomplete; profile-decision what-if does not replace strict main metrics or completed human review |
| ATCSCC S5/S6 live agentic pilot 3 | bounded live extractor/validator/critic/refiner pilot over reviewed ATCSCC advisory samples | s5_s6_live_agentic_pilot | bounded_method_pilot | 3-sample live LLM pilot; useful for method evidence but not a full autonomous-agent benchmark |
| ATCSCC S5/S6 live agentic full run 100 | full reviewed-set live extractor/validator/critic/refiner run over ATCSCC advisory samples | s5_s6_live_agentic_full_run | full_extraction_layer_method_evidence | full extraction-layer run; still not human-reviewed answer quality, operational decision support, or cross-domain validation |
| triple semantic review sample | KG semantic correctness review template | llm_review_pending | partial | review fields pending until model-based review is run; no expert correctness claimed |

## Primary Results

| Metric group | Key numbers |
| --- | --- |
| vector-only benchmark v2 | Recall@5=0.475, Recall@10=0.475, MRR@5=0.3268, NDCG@10=0.3869 |
| lexical hybrid benchmark v2 | Recall@5=0.5167, Recall@10=0.5917, MRR@5=0.3417, NDCG@10=0.443, Context Recall=0.7375 |
| traversal hybrid | Recall@5=0.4583, Path Recall@5=0.6583, Path Precision@5=0.6522 (heuristic or model-reviewed; no human review) |
| sufficiency | Abstention Accuracy=1.0, False Answer Rate=0.0, False Abstention Rate=0.29 |
| robustness | Abstention Correctness=1.0, False Answer Rate=0.0, Boundary Violations=0 |
| benchmark reviewed subset | Labels=60, Review Status=llm_review_pending_not_human_certified, External Expert Certified=False |
| answer-eval benchmark subset | Answers=0, Status=pending_answer_generation, Unmatched Gold Labels=45, Hybrid Faithfulness=0.0, Score Method=deterministic_heuristic |
| ATCSCC S7 LLM answer generation | Selected=60, Best mode=routed_token_matched_live_tfidf_graphrag, Correctness=0.9667, Citation precision=1.0, Citation recall=0.6084, Unsupported claim rate=0.0167, Human-review candidates=9 (queue only; no human review), Adjudicated profile/gold-boundary failures=3, Strict metrics changed=False, Profile-decision what-if corrected records=3, Profile/gold changed=False, What-if replaces main=False |
| chunking benchmark v2 | Top-k best=structure_aware_large (Recall@5=0.85), Fixed-budget best=recursive_medium (Recall@5=0.79), Partial methods=['hierarchical_parent_child'] |
| PDF extraction backend | Recommended=hybrid_docling_pymupdf (candidate_default_not_final), legacy false headings=113, Docling heading recall=1.0, hybrid repairs=14, hybrid Recall@5=0.77 |
| KG | Provenance Completeness=1.0, Evidence-in-source Rate=1.0, Valid Triples=448 |
| NASA source expansion | Status=full_corpus_collected_aerodynamics_subset_experiment_ready, discovered URLs=90, covered URLs=90, corpus pages=90, valid pages=89, experiment valid pages=8/8, KG triples=134, FAA+NASA smoke Recall@5=0.64 |
| triple semantic review | Sample=100, reviewed=0, needs_review=100 |
| LLM review status | Benchmark reviewed=6, triple evidence support=0.1667, graph path relevance=0.3333, answer judge correctness=None, S7 selected=60, S7 review candidates=9, S7 adjudicated boundary failures=3, human review=false |
| implementation review remediation | Status=full_quality_gates_passed, implemented=6, verified already fixed=2, deferred=['I6', 'NF3'], metrics changed=False |

## Safety Confidence Intervals

| Metric | Mean | 95% CI | n |
| --- | ---: | --- | ---: |
| abstention_accuracy | 1.0 | 1.0 - 1.0 | 20 |
| false_abstention_rate | 0.29 | 0.21 - 0.38 | 100 |
| false_answer_rate | 0.0 | 0.0 - 0.0 | 20 |
| risk_category_accuracy | 1.0 | 1.0 - 1.0 | 120 |

## Failure-Mode Summary

- Graph failure categories: {'generic_seed_node': 75, 'graph_fusion_dilution': 100, 'kg_sparse_for_question': 374, 'low_value_predicate': 154, 'path_found_but_wrong_chunk': 322, 'seed_linking_error': 150}
- Chunking failure-card samples: {'chunk_too_large_low_precision': 3, 'chunk_too_small_lost_context': 8, 'cross_page_evidence_split': 14, 'missed_gold_evidence_at_5': 14, 'no_answer_retrieved_misleading_context': 14, 'parent_child_not_used': 1, 'proposition_context_loss': 1, 'section_boundary_split': 6, 'semantic_boundary_error': 2}
- False abstention on supported questions: 29
- Machine-seeded benchmark wording findings: 90
- Missing LLM triple review items: 100

## LLM Review Status

`deterministic`, `heuristic`, `llm_judge`, and `human_review` metrics are reported separately. Human review is absent and external expert certification is false.
- Benchmark LLM review: {'records': 6, 'llm_reviewed': 6, 'status': 'llm_reviewed_not_human_certified'}
- Triple semantic LLM review: {'records': 6, 'llm_reviewed': 6, 'evidence_support_rate': 0.1667}
- Graph path LLM review: {'records': 6, 'llm_reviewed': 6, 'path_relevance_rate': 0.3333}
- Answer generation subset: {'answers_total': 9, 'status': 'complete'}
- Answer LLM judge: {'records': 6, 'llm_reviewed': 5, 'correctness_rate': None}
- LLM review consistency: {'agreement_rate': 0.3636, 'consistency_not_measured': False}

## Thesis-Ready Claim Summary

- **Lightweight schema constrains advisory event extraction.** Safe wording: The application schema constrains which advisory event fields and relations can enter the graph. Limitations: ATCSCC profile terms, schema validation, and prediction-output validation reports constrain accepted event fields. Avoid: The ontology fully models aviation knowledge.
- **Accepted facts preserve provenance.** Safe wording: Accepted facts carry source-bounded provenance checked by deterministic validation. Limitations: KG and prediction validation reports check source IDs and evidence spans. Avoid: Every KG triple is semantically correct.
- **Agentic validation improves extraction quality.** Safe wording: The agentic loop reduces specific schema and support failures in the current ATCSCC pipeline. Limitations: S5/S6 reports record validator, refiner, critic, repair, and rejection behavior. Avoid: Autonomous agents construct a correct ontology.
- **KG-RAG improves grounded ATCSCC QA diagnostics.** Safe wording: KG-RAG improves some source-bounded grounding diagnostics on this benchmark. Limitations: S7 retrieval, graph-health, and LLM answer-generation diagnostics report answer-set, citation, and target-source metrics. Avoid: GraphRAG is always more accurate than vector retrieval.
- **GraphRAG universally improves retrieval.** Safe wording: KG-RAG should be reported as a source-bounded grounding and evidence diagnostic, not a universal Recall@k improvement. Limitations: S7 reports vector, graph, and routed modes separately; graph use is template-dependent. Avoid: GraphRAG always improves Recall@k.
- **The system can answer operational ATC questions.** Safe wording: The system analyzes retrospective advisories and must not be used for live operational decisions. Limitations: The advisory boundary limits the system to retrospective research diagnostics. Avoid: The system can support operational flight or ATC decisions.
- **Automated diagnostics replace human review.** Safe wording: Automated diagnostics are internal error-discovery tools and do not replace human or expert review. Limitations: Reviewer-defense and SOTA audits keep automated diagnostics separate from human review. Avoid: The benchmark is human reviewed or expert certified.
- **The benchmark is externally aviation-expert certified.** Safe wording: The benchmark is thesis-oriented and source-bounded, with explicit review limitations. Limitations: Current labels and diagnostics are project/thesis evidence with documented review gaps. Avoid: The benchmark is externally aviation-expert certified.
- **The method is domain-general.** Safe wording: The method is designed to be domain-adaptable, with only pilot-level transfer evidence so far. Limitations: A bounded second-source-family pilot exists, but it is not a full cross-domain benchmark. Avoid: The method is proven domain-general.

## Consistency Checks

- `every_rq_has_evidence_report`: True
- `primary_thesis_metrics_have_report_evidence`: True
- `primary_thesis_metric_gaps`: []
- `benchmark_v2_used_in_main_retrieval`: True
- `benchmark_v2_used_in_safety`: True
- `pilot_reports_not_marked_main`: True
- `human_review_absent`: True
- `external_expert_certified`: False
- `aviation_expert_certified`: False
- `benchmark_llm_review_available`: True
- `triple_semantic_llm_review_available`: True
- `answer_llm_judge_available`: True
- `s7_llm_answer_generation_available`: True
- `s7_human_review_candidates_available`: True
- `s7_candidate_adjudication_available`: True
- `s7_profile_decision_what_if_available`: True
- `reviewed_subset_llm_review_pending`: True
- `safety_reports_have_no_boundary_violations`: True
- `robustness_false_answer_rate_zero`: True
- `no_unsafe_claim_patterns`: True
- `automated_consistency_passed`: True
- `claim_readiness_passed`: True
- `all_passed`: True
