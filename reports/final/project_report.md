# Aviation Agentic AI Project Report

## Research claim and scope

This thesis does not assume that GraphRAG universally improves retrieval Recall@k over vector-only RAG. Instead, it investigates a narrower and more safety-relevant claim: in aviation training question answering, an ontology-constrained GraphRAG pipeline can add inspectable KG/path evidence, expose structured evidence coverage, and support insufficient-evidence abstention checks. The system is therefore evaluated with layered metrics: retrieval quality, KG evidence quality, answer citation quality, and safety-aware abstention are measured separately rather than collapsed into a single overall score.

This deterministic report is organized by research questions and uses `reports/stages/thesis_experiment_dashboard.json` as the main evidence source. The dashboard aggregates existing reports without recomputing experiments. It keeps retrieval, graph evidence, answer quality, ontology/KG quality, and safety-abstention metrics separate; no mixed overall score is created.

Scope boundary: This system is for aviation learning and decision-support only. Do not claim to replace the aircraft POH, approved checklists, ATC instructions, instructor guidance, or pilot judgment.

## Dataset and benchmark

- **10-CQ pilot**: demo and qualitative answer inspection; evidence role=`pilot`; thesis main claim support=partial; limitations: too small for main thesis retrieval claims.
- **35-question expanded**: pilot ablation and KG extraction comparison; evidence role=`pilot`; thesis main claim support=partial; limitations: pilot-sized and not the main benchmark.
- **benchmark v2 120**: main thesis retrieval and safety benchmark; evidence role=`main_thesis_benchmark`; thesis main claim support=provisional_internal_pending_llm_review; limitations: machine-seeded and requires model-based naturalness review.
- **benchmark v2 chunking experiment**: chunking strategy comparison under top-k, fixed-budget, and category views; evidence role=`retrieval_design_diagnostic`; thesis main claim support=partial_benchmark_specific; limitations: implementation-maturity labels required; top-k context volume differs by chunk size.
- **benchmark reviewed subset 60**: model-based review scaffold for high-value labels; evidence role=`llm_review_scaffold`; thesis main claim support=pending_llm_review; limitations: review scaffold only; no human review or external aviation expert certification.
- **LLM review artifacts**: model-based benchmark, triple, graph-path, answer, and consistency review; evidence role=`llm_judge`; thesis main claim support=internal_llm_review_only; limitations: model-based internal review; no human or external expert certification.
- **answer-eval subset**: answer citation and faithfulness heuristics; evidence role=`pilot`; thesis main claim support=partial; limitations: stratified subset; deterministic heuristic scores unless annotated.
- **triple semantic review sample**: KG semantic correctness review template; evidence role=`llm_review_pending`; thesis main claim support=partial; limitations: review fields pending until model-based review is run; no expert correctness claimed.

Benchmark v2 is the main thesis retrieval and safety benchmark. The 10-CQ and 35-question sets remain pilot/demo evidence and must not be presented as the main thesis benchmark.

## Evaluation protocol

The evaluation protocol is defined in `docs/evaluation_protocol.md` and audited by `reports/stages/evaluation_protocol_review.json`. Primary metrics include Recall@5/@10, MRR@5/@10, NDCG@10, Precision@5, Context Precision@5, Context Recall, graph path metrics, citation metrics, KG validation metrics, and safety-abstention metrics.

## RQ1: ontology-constrained KG extraction

Current KG evidence: structure-aware valid triples=448, provenance completeness=1.0, evidence-in-source rate=1.0, unsupported triple count=0. Triple semantic review sample size=100, reviewed=0, needs_review=100; no semantic correctness claim is made unless a separate LLM-estimated review artifact is cited.

## RQ2: evidence traceability

Evidence traceability is supported by KG provenance, citation metrics, and the dashboard inventory. Answer-level scores are deterministic heuristics unless an LLM-judge score is explicitly recorded; human review is absent.

## RQ3: vector vs graph vs hybrid retrieval (Hybrid RAG protocol and layered metrics)

Benchmark v2 vector-only: Recall@5=0.475, Recall@10=0.475, MRR@5=0.3261, NDCG@10=0.3863. Lexical hybrid: Recall@5=0.5083, Recall@10=0.5917, MRR@5=0.34, NDCG@10=0.4425, Context Recall=0.7375, KG evidence coverage=0.8.

Traversal hybrid: Recall@5=0.4583, Path Recall@5=0.6583, Path Precision@5=0.6522. Path metrics are heuristic and may be model-reviewed, but they are not human-validated. High path coverage is not treated as evidence of high retrieval quality unless Recall/MRR/NDCG also support that claim.

Chunking-v2 evidence is interpreted as retrieval-design evidence, not as a universal best-chunker claim. Top-k best strategy=fixed_large with supported Recall@5=0.86; fixed-budget best strategy=recursive_medium with supported Recall@5=0.79. Partial methods=['hierarchical_parent_child']; semantic backend=['sentence_transformers']. Top-k chunking rankings expose unequal context budgets; fixed-budget and category diagnostics are stronger evidence but still benchmark-specific.

## RQ4: safety-aware abstention

Benchmark v2 safety metrics: Abstention Accuracy=1.0, False Answer Rate=0.0, False Abstention Rate=0.29, Risk Category Accuracy=1.0. Sufficiency diagnostics show strong abstention on benchmark v2 no-answer labels, while robustness must also remain visible: false answer rate=0.0, boundary violations=0.

## Review-dependent evidence status

Benchmark reviewed subset: labels=60, status=llm_review_pending_not_human_certified, external aviation expert certification completed=False. Answer-evaluation benchmark subset: answers=0, status=pending_answer_generation, unmatched gold labels=45, hybrid faithfulness=0.0, score method=deterministic_heuristic. These are not human review results.

## Model-Based Review Instead of Human Review

No human aviation expert review was conducted. Model-based review uses the configured LLM reviewer as an internal consistency and error-discovery layer. It does not provide external certification, expert gold labels, or operational aviation authority.
Benchmark LLM review: {'llm_reviewed': 6, 'records': 6, 'status': 'llm_reviewed_not_human_certified'}.
Triple semantic LLM review: {'evidence_support_rate': 0.1667, 'llm_reviewed': 6, 'records': 6}.
Graph path LLM review: {'llm_reviewed': 6, 'path_relevance_rate': 0.3333, 'records': 6}.
Answer generation and LLM judge: generation={'answers_total': 9, 'status': 'complete'}, judge={'correctness_rate': None, 'llm_reviewed': 5, 'records': 6}.
LLM review consistency: {'agreement_rate': 0.3636, 'consistency_not_measured': False}.
All review-dependent claims are phrased as LLM-assisted or LLM-estimated, not human-verified.

## Failure analysis

Graph failure categories: {'generic_seed_node': 75, 'graph_fusion_dilution': 100, 'kg_sparse_for_question': 374, 'low_value_predicate': 154, 'path_found_but_wrong_chunk': 322, 'seed_linking_error': 150}.
False abstentions on supported questions: 29.
Machine-seeded benchmark wording findings: 90.
Missing LLM triple review items: 100.

## Limitations

Benchmark v2 is thesis/course-project evidence, not external aviation expert certification. Path relevance and triple semantic correctness are heuristic or LLM-estimated unless a specific model-review artifact is cited. The system is not operational flight software and does not replace official sources or pilot judgment.

## Reproducibility appendix

- `make validate`
- `make reports-core`
- `make reports-main-experiments`
- `make reports-review`
- `make thesis-dashboard`
- `uv run aviation-ai report project --no-ai`
- `uv run aviation-ai report academic-paper --no-ai`

## Dashboard consistency checks

- `all_passed`: True
- `answer_llm_judge_available`: True
- `automated_consistency_passed`: True
- `aviation_expert_certified`: False
- `benchmark_llm_review_available`: True
- `benchmark_v2_used_in_main_retrieval`: True
- `benchmark_v2_used_in_safety`: True
- `claim_readiness_passed`: True
- `every_rq_has_evidence_report`: True
- `external_expert_certified`: False
- `human_review_absent`: True
- `no_unsafe_claim_patterns`: True
- `pilot_reports_not_marked_main`: True
- `primary_thesis_metric_gaps`: []
- `primary_thesis_metrics_have_report_evidence`: True
- `reviewed_subset_llm_review_pending`: True
- `robustness_false_answer_rate_zero`: True
- `safety_reports_have_no_boundary_violations`: True
- `triple_semantic_llm_review_available`: True

## RQ evidence matrix

- **RQ1 ontology constraint**: reports=['curated_ontology_evaluation', 'kg_extraction_comparison', 'kg_validation']; metrics=['RDF/OWL parse validity', 'label/comment coverage', 'unsupported class/property count', 'provenance completeness']; claim strength=strong; gaps=Triple semantic correctness is absent or LLM-estimated only..
- **RQ2 evidence traceability**: reports=['retrieval_ablation_benchmark_v2', 'graph_traversal_ablation_benchmark_v2', 'answer_evaluation']; metrics=['KG evidence coverage', 'citation completeness', 'citation precision', 'citation recall']; claim strength=moderate; gaps=Answer-level LLM-judge evaluation must remain separate from deterministic metrics..
- **RQ3 graph evidence vs vector sufficiency**: reports=['retrieval_ablation_benchmark_v2', 'graph_traversal_ablation_benchmark_v2', 'chunking_comparison_benchmark_v2', 'chunking_comparison_benchmark_v2_budget', 'chunking_topk_sensitivity_benchmark_v2', 'chunking_category_analysis_benchmark_v2']; metrics=['Recall@5', 'Recall@10', 'MRR@5', 'NDCG@10', 'Path Recall@5', 'Path Precision@5', 'Fixed-budget chunking Recall@5']; claim strength=moderate; gaps=Path relevance is heuristic or model-reviewed, not human-validated..
- **RQ4 safety-aware abstention**: reports=['sufficiency_evaluation', 'robustness_evaluation']; metrics=['Abstention Accuracy', 'False Answer Rate', 'False Abstention Rate', 'Risk Category Accuracy']; claim strength=moderate; gaps=Sufficiency can create false abstentions on supported questions..
