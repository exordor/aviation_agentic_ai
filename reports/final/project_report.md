# Aviation Agentic AI Project Report

## Research claim and scope

This thesis does not assume that GraphRAG universally improves retrieval Recall@k over vector-only RAG. Instead, it investigates a narrower and more safety-relevant claim: in aviation training question answering, an ontology-constrained GraphRAG pipeline can add inspectable KG/path evidence, expose structured evidence coverage, and support insufficient-evidence abstention checks. The system is therefore evaluated with layered metrics: retrieval quality, KG evidence quality, answer citation quality, and safety-aware abstention are measured separately rather than collapsed into a single overall score.

This deterministic report is organized by research questions and uses `reports/stages/thesis_experiment_dashboard.json` as the main evidence source. The dashboard aggregates existing reports without recomputing experiments. It keeps retrieval, graph evidence, answer quality, ontology/KG quality, and safety-abstention metrics separate; no mixed overall score is created.

Scope boundary: This system is for aviation learning and decision-support only. Do not claim to replace the aircraft POH, approved checklists, ATC instructions, instructor guidance, or pilot judgment.

## Dataset and benchmark

- **10-CQ pilot**: demo and qualitative answer inspection; evidence role=`pilot`; thesis main claim support=partial; limitations: too small for main thesis retrieval claims.
- **35-question expanded**: pilot ablation and KG extraction comparison; evidence role=`pilot`; thesis main claim support=partial; limitations: pilot-sized and not the main benchmark.
- **benchmark v2 120**: main thesis retrieval and safety benchmark; evidence role=`main_thesis_benchmark`; thesis main claim support=provisional_internal_pending_manual_review; limitations: machine-seeded and requires manual naturalness review.
- **benchmark reviewed subset 60**: project-author review scaffold for high-value labels; evidence role=`manual_review_scaffold`; thesis main claim support=pending_manual_review; limitations: review scaffold only; no external aviation expert certification.
- **answer-eval subset**: answer citation and faithfulness heuristics; evidence role=`pilot`; thesis main claim support=partial; limitations: stratified subset; deterministic heuristic scores unless annotated.
- **triple semantic review sample**: manual KG semantic correctness review template; evidence role=`manual_review_pending`; thesis main claim support=partial; limitations: review fields pending; no correctness results claimed.

Benchmark v2 is the main thesis retrieval and safety benchmark. The 10-CQ and 35-question sets remain pilot/demo evidence and must not be presented as the main thesis benchmark.

## Evaluation protocol

The evaluation protocol is defined in `docs/evaluation_protocol.md` and audited by `reports/stages/evaluation_protocol_review.json`. Primary metrics include Recall@5/@10, MRR@5/@10, NDCG@10, Precision@5, Context Precision@5, Context Recall, graph path metrics, citation metrics, KG validation metrics, and safety-abstention metrics.

## RQ1: ontology-constrained KG extraction

Current KG evidence: structure-aware valid triples=448, provenance completeness=1.0, evidence-in-source rate=1.0, unsupported triple count=0. Triple semantic review sample size=100, reviewed=0, needs_review=100; no semantic correctness claim is made until manual annotations are completed.

## RQ2: evidence traceability

Evidence traceability is supported by KG provenance, citation metrics, and the dashboard inventory. Answer-level scores are deterministic heuristics unless an LLM-judge or manual review score is explicitly recorded.

## RQ3: vector vs graph vs hybrid retrieval (Hybrid RAG protocol and layered metrics)

Benchmark v2 vector-only: Recall@5=0.475, Recall@10=0.475, MRR@5=0.3261, NDCG@10=0.3863. Lexical hybrid: Recall@5=0.5083, Recall@10=0.5917, MRR@5=0.34, NDCG@10=0.4425, Context Recall=0.7375, KG evidence coverage=0.8.

Traversal hybrid: Recall@5=0.4583, Path Recall@5=0.6583, Path Precision@5=0.6522. Path metrics are heuristic and require manual review. High path coverage is not treated as evidence of high retrieval quality unless Recall/MRR/NDCG also support that claim.

## RQ4: safety-aware abstention

Benchmark v2 safety metrics: Abstention Accuracy=1.0, False Answer Rate=0.0, False Abstention Rate=0.29, Risk Category Accuracy=1.0. Sufficiency diagnostics show strong abstention on benchmark v2 no-answer labels, while robustness must also remain visible: false answer rate=0.0, boundary violations=0.

## Review-dependent evidence status

Benchmark reviewed subset: labels=60, status=project_review_pending_external_review, external aviation expert review completed=False. Answer-evaluation benchmark subset: answers=0, status=pending_answer_generation, unmatched gold labels=35, hybrid faithfulness=0.0, score method=deterministic_heuristic. These are not manual review results.

## Failure analysis

Graph failure categories: {'generic_seed_node': 75, 'graph_fusion_dilution': 100, 'kg_sparse_for_question': 374, 'low_value_predicate': 154, 'path_found_but_wrong_chunk': 322, 'seed_linking_error': 150}.
False abstentions on supported questions: 29.
Machine-seeded benchmark wording findings: 90.
Missing manual triple review items: 100.

## Limitations

Benchmark v2 is thesis/course-project evidence, not external aviation expert certification. Path relevance and triple semantic correctness remain manual-review dependent. The system is not operational flight software and does not replace official sources or pilot judgment.

## Reproducibility appendix

- `make validate`
- `make reports-core`
- `make reports-main-experiments`
- `make reports-review`
- `make thesis-dashboard`
- `uv run aviation-ai report project --no-ai`
- `uv run aviation-ai report academic-paper --no-ai`

## Dashboard consistency checks

- `all_passed`: False
- `automated_consistency_passed`: True
- `benchmark_v2_used_in_main_retrieval`: True
- `benchmark_v2_used_in_safety`: True
- `claim_readiness_passed`: False
- `every_rq_has_evidence_report`: True
- `manual_review_dependent_metrics_not_completed`: True
- `no_unsafe_claim_patterns`: True
- `pilot_reports_not_marked_main`: True
- `primary_thesis_metric_gaps`: []
- `primary_thesis_metrics_have_report_evidence`: True
- `reviewed_subset_manual_review_pending`: True
- `robustness_false_answer_rate_zero`: True
- `safety_reports_have_no_boundary_violations`: True

## RQ evidence matrix

- **RQ1 ontology constraint**: reports=['curated_ontology_evaluation', 'kg_extraction_comparison', 'kg_validation']; metrics=['RDF/OWL parse validity', 'label/comment coverage', 'unsupported class/property count', 'provenance completeness']; claim strength=strong; gaps=Triple semantic correctness still requires manual review..
- **RQ2 evidence traceability**: reports=['retrieval_ablation_benchmark_v2', 'graph_traversal_ablation_benchmark_v2', 'answer_evaluation']; metrics=['KG evidence coverage', 'citation completeness', 'citation precision', 'citation recall']; claim strength=moderate; gaps=Answer-level manual or LLM-judge evaluation is optional and not run..
- **RQ3 graph evidence vs vector sufficiency**: reports=['retrieval_ablation_benchmark_v2', 'graph_traversal_ablation_benchmark_v2']; metrics=['Recall@5', 'Recall@10', 'MRR@5', 'NDCG@10', 'Path Recall@5', 'Path Precision@5']; claim strength=moderate; gaps=Path relevance metrics are heuristic until manually reviewed..
- **RQ4 safety-aware abstention**: reports=['sufficiency_evaluation', 'robustness_evaluation']; metrics=['Abstention Accuracy', 'False Answer Rate', 'False Abstention Rate', 'Risk Category Accuracy']; claim strength=moderate; gaps=Sufficiency can create false abstentions on supported questions..
