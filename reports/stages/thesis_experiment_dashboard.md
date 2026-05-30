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
| `kg_extraction_comparison` | True | 35_question_expanded | n/a | ontology_kg | False | False |
| `curated_ontology_evaluation` | True | not_dataset_specific | n/a | ontology_kg | False | False |
| `triple_semantic_review_sample` | True | triple_semantic_review_sample | n/a | ontology_kg, llm_review_scaffold | False | False |
| `answer_evaluation` | True | 10_cq_answer_subset | n/a | answer_generation, safety_abstention | False | False |
| `robustness_evaluation` | True | robustness_10_cases | n/a | safety_abstention, robustness | False | False |
| `benchmark_review_pack` | True | not_dataset_specific | 120 | benchmark_llm_review_scaffold | False | False |

## RQ-To-Evidence Matrix

| RQ | Evidence reports | Primary metrics | Claim strength | Remaining gaps |
| --- | --- | --- | --- | --- |
| RQ1 ontology constraint | curated_ontology_evaluation, kg_extraction_comparison, kg_validation | RDF/OWL parse validity, label/comment coverage, unsupported class/property count, provenance completeness | strong | Triple semantic correctness is absent or LLM-estimated only. |
| RQ2 evidence traceability | retrieval_ablation_benchmark_v2, graph_traversal_ablation_benchmark_v2, answer_evaluation | KG evidence coverage, citation completeness, citation precision, citation recall | moderate | Answer-level LLM-judge evaluation must remain separate from deterministic metrics. |
| RQ3 graph evidence vs vector sufficiency | retrieval_ablation_benchmark_v2, graph_traversal_ablation_benchmark_v2, chunking_comparison_benchmark_v2, chunking_comparison_benchmark_v2_budget, chunking_topk_sensitivity_benchmark_v2, chunking_category_analysis_benchmark_v2 | Recall@5, Recall@10, MRR@5, NDCG@10, Path Recall@5, Path Precision@5, Fixed-budget chunking Recall@5 | moderate | Path relevance is heuristic or model-reviewed, not human-validated. |
| RQ4 safety-aware abstention | sufficiency_evaluation, robustness_evaluation | Abstention Accuracy, False Answer Rate, False Abstention Rate, Risk Category Accuracy | moderate | Sufficiency can create false abstentions on supported questions. |

## Dataset Usage Matrix

| Dataset | Purpose | Evidence role | Main claim support | Limitations |
| --- | --- | --- | --- | --- |
| 10-CQ pilot | demo and qualitative answer inspection | pilot | partial | too small for main thesis retrieval claims |
| 35-question expanded | pilot ablation and KG extraction comparison | pilot | partial | pilot-sized and not the main benchmark |
| benchmark v2 120 | main thesis retrieval and safety benchmark | main_thesis_benchmark | provisional_internal_pending_llm_review | machine-seeded and requires model-based naturalness review |
| benchmark v2 chunking experiment | chunking strategy comparison under top-k, fixed-budget, and category views | retrieval_design_diagnostic | partial_benchmark_specific | implementation-maturity labels required; top-k context volume differs by chunk size |
| benchmark reviewed subset 60 | model-based review scaffold for high-value labels | llm_review_scaffold | pending_llm_review | review scaffold only; no human review or external aviation expert certification |
| LLM review artifacts | model-based benchmark, triple, graph-path, answer, and consistency review | llm_judge | internal_llm_review_only | model-based internal review; no human or external expert certification |
| answer-eval subset | answer citation and faithfulness heuristics | pilot | partial | stratified subset; deterministic heuristic scores unless annotated |
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
| chunking benchmark v2 | Top-k best=structure_aware_large (Recall@5=0.85), Fixed-budget best=recursive_medium (Recall@5=0.79), Partial methods=['hierarchical_parent_child'] |
| KG | Provenance Completeness=1.0, Evidence-in-source Rate=1.0, Valid Triples=448 |
| triple semantic review | Sample=100, reviewed=0, needs_review=100 |
| LLM review status | Benchmark reviewed=6, triple evidence support=0.1667, graph path relevance=0.3333, answer judge correctness=None, human review=false |

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

- **Ontology constrains KG extraction.** Safe wording: The task ontology constrains which focused classes and relations can enter the KG. Limitations: Extraction profile terms map to the curated ontology; KG validation rejects unsupported schema terms. Avoid: The ontology fully models aviation knowledge.
- **KG triples preserve provenance.** Safe wording: Current extracted triples carry source chunk provenance checked by deterministic validation. Limitations: KG validation reports zero missing-provenance errors in the current fixed-window and structure-aware artifacts. Avoid: Every KG triple is semantically correct.
- **GraphRAG improves Recall@5.** Safe wording: GraphRAG does not always improve Recall@5; report Recall separately from KG evidence coverage. Limitations: Expanded retrieval ablation shows vector Recall@5 can be higher than default hybrid Recall@5. Avoid: GraphRAG always improves Recall@5.
- **GraphRAG improves structured evidence support.** Safe wording: GraphRAG improves inspectable structured evidence support in the current benchmark. Limitations: Graph and hybrid modes expose KG coverage, provenance, triples, and evidence-level answer support. Avoid: GraphRAG is always more accurate than vector retrieval.
- **Hybrid RAG always beats vector-only RAG.** Safe wording: Hybrid RAG can add KG evidence coverage while vector retrieval can remain sufficient for simple factual questions. Limitations: Fixed-window and expanded ablations include cases where vector retrieval is equal or better on Recall@5. Avoid: Hybrid RAG always beats vector-only RAG.
- **The system can answer aviation operational questions.** Safe wording: The system can answer aviation training questions when evidence is sufficient and should abstain otherwise. Limitations: The advisory boundary limits the system to learning and decision support; live operational data and official procedures are out of scope. Avoid: The system can support operational flight decisions.
- **The system can support aviation learning questions.** Safe wording: The prototype supports aviation learning questions over its scoped source material. Limitations: The pipeline answers PHAK Chapter 4 training questions with citations and evidence panels. Avoid: The prototype is a certified aviation assistant.
- **The system can replace POH/checklists/ATC/instructor judgment.** Safe wording: The system does not replace POH, approved checklists, ATC, instructor guidance, or pilot judgment. Limitations: The advisory boundary explicitly rejects replacement of official sources or human judgment. Avoid: The system can replace POH, checklists, ATC, or instructor judgment.
- **The benchmark is externally aviation-expert certified.** Safe wording: The benchmark is course-project / thesis-oriented gold with documented limitations. Limitations: Current labels are reviewed course-project / thesis-oriented gold, not external examiner certification. Avoid: The benchmark is externally aviation-expert certified.
- **The benchmark is course-project / thesis-oriented gold.** Safe wording: The benchmark is course-project / thesis-oriented gold, useful for internal evaluation but not external certification. Limitations: Reports identify the 10-question and expanded 35-question labels as project/thesis evidence. Avoid: The benchmark proves aviation-domain correctness.

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
- `reviewed_subset_llm_review_pending`: True
- `safety_reports_have_no_boundary_violations`: True
- `robustness_false_answer_rate_zero`: True
- `no_unsafe_claim_patterns`: True
- `automated_consistency_passed`: True
- `claim_readiness_passed`: True
- `all_passed`: True
