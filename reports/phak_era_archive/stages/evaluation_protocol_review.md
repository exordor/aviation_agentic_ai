# Evaluation Protocol Review

- Protocol doc: `docs/evaluation_protocol.md`
- Scoring policy: layered metrics; no single mixed overall score.

## Primary Thesis Metrics

| Layer | Classification | Metrics | Reports |
| --- | --- | --- | --- |
| retrieval | mainstream | Recall@5, Recall@10, MRR@5, MRR@10, NDCG@10, Precision@5, Context Precision@5, Context Recall | `reports/stages/retrieval_ablation.json`, `reports/stages/retrieval_ablation_benchmark_v2.json`, `reports/stages/chunking_comparison.json` |
| graph_evidence | mainstream_plus_heuristic_path_review | Key Entity Coverage, Relation Coverage, Path Recall@5, Path Precision@5, Supporting Path Rate, Average Path Length, Irrelevant Path Rate | `reports/stages/graph_traversal_ablation.json`, `reports/stages/graph_traversal_ablation_benchmark_v2.json` |
| answer_generation | mainstream_heuristic_with_optional_llm_judge | Faithfulness, Answer Correctness, Answer Relevance, Citation Completeness, Citation Precision, Citation Recall | `reports/stages/answer_evaluation.json`, `reports/stages/answer_llm_judge.json` |
| ontology_kg | mainstream_plus_model_based_review | RDF/OWL parse validity, label/comment coverage, domain/range completeness, unsupported class/property count, provenance completeness, evidence-in-source rate, LLM-estimated triple semantic correctness | `reports/stages/curated_ontology_evaluation.json`, `reports/stages/kg_validation.json`, `reports/stages/kg_extraction_comparison.json`, `reports/stages/triple_semantic_review_sample.json`, `reports/stages/triple_semantic_llm_review.json` |
| safety_abstention | safety_sensitive_project_primary | Abstention Accuracy, False Answer Rate, False Abstention Rate, Advisory Boundary Violation Count, Risk Category Accuracy | `reports/stages/sufficiency_evaluation.json`, `reports/stages/robustness_evaluation.json`, `reports/stages/answer_evaluation.json` |

## Metric Implementation Status

| Metric | Status | Kind | Field | Reports |
| --- | --- | --- | --- | --- |
| Recall@5 | implemented | mainstream_ir | `recall_at_5` | retrieval_ablation, graph_traversal_ablation |
| Recall@10 | implemented | mainstream_ir | `recall_at_10` | retrieval_ablation, graph_traversal_ablation |
| Precision@5 | implemented | mainstream_ir | `precision_at_5` | retrieval_ablation, graph_traversal_ablation |
| MRR@5 | implemented | mainstream_ir | `mrr_at_5` | retrieval_ablation, graph_traversal_ablation |
| MRR@10 | implemented | mainstream_ir | `mrr_at_10` | retrieval_ablation, graph_traversal_ablation |
| NDCG@10 | implemented | mainstream_ir | `ndcg_at_10` | retrieval_ablation, graph_traversal_ablation |
| Context Precision@5 | implemented | ragas_style | `context_precision_at_5` | retrieval_ablation, graph_traversal_ablation |
| Context Recall | implemented | ragas_style | `context_recall` | retrieval_ablation, graph_traversal_ablation |
| Path Recall@5 | heuristic_available_llm_review_optional | graphrag_path | `path_recall_at_5` | graph_traversal_ablation |
| Path Precision@5 | heuristic_available_llm_review_optional | graphrag_path | `path_precision_at_5` | graph_traversal_ablation |
| Supporting Path Rate | heuristic_available_llm_review_optional | graphrag_path | `supporting_path_rate` | graph_traversal_ablation |
| Irrelevant Path Rate | heuristic_available_llm_review_optional | graphrag_path | `irrelevant_path_rate` | graph_traversal_ablation |
| Citation Precision | implemented | deterministic_answer_heuristic | `citation_precision` | answer_evaluation |
| Citation Recall | implemented | deterministic_answer_heuristic | `citation_recall` | answer_evaluation |
| Faithfulness | implemented_heuristic_llm_judge_optional_not_run | ragas_ares_style | `faithfulness` | answer_evaluation |
| Answer Correctness | implemented_heuristic_llm_judge_optional_not_run | ragas_style | `answer_correctness` | answer_evaluation |
| Answer Relevance | implemented_heuristic_llm_judge_optional_not_run | ragas_ares_style | `answer_relevance` | answer_evaluation |
| Triple Semantic Correctness | llm_review_template_available_results_optional | llm_kg_review | `summary.llm_evidence_support_rate` | triple_semantic_review, triple_semantic_llm_review |
| RDF/OWL Parse Validity | implemented | ontology_structural | `structural_metrics.rdf_valid` | curated_ontology_evaluation |
| Label/Comment Coverage | implemented | ontology_usability_annotation | `structural_metrics.*_coverage` | curated_ontology_evaluation |
| Domain/Range Completeness | implemented | ontology_functional | `structural_metrics.properties_with_domain/range` | curated_ontology_evaluation |
| Unsupported Class/Property Count | implemented | kg_validation | `errors_total and unsupported_triple_count` | kg_validation, kg_extraction_comparison |
| Provenance Completeness | implemented | kg_validation | `provenance_complete_rate` | kg_extraction_comparison, retrieval_ablation |
| Evidence-In-Source Rate | implemented | kg_validation | `evidence_in_chunk_rate` | kg_extraction_comparison |
| Abstention Accuracy | implemented | safety_sensitive | `abstention_accuracy` | sufficiency_evaluation, robustness_evaluation |
| False Answer Rate | implemented | safety_sensitive | `false_answer_rate` | sufficiency_evaluation, robustness_evaluation |
| False Abstention Rate | implemented | safety_sensitive | `false_abstention_rate` | sufficiency_evaluation, robustness_evaluation |
| Advisory Boundary Violation Count | implemented | safety_sensitive | `advisory_boundary_violation_count` | sufficiency_evaluation, robustness_evaluation, answer_evaluation |
| Risk Category Accuracy | implemented | safety_sensitive | `risk_category_accuracy` | sufficiency_evaluation, robustness_evaluation |

## Metric Interpretation Notes

- **precision_denominators**: Precision@5 divides by the fixed cutoff of 5, while Context Precision@5 divides by the number of returned top-five contexts when fewer than five contexts exist. They are related diagnostics, not interchangeable fields.
- **empty_bootstrap_ci**: Bootstrap CI blocks with n=0 are undefined for that subset. Numeric mean/lower/upper placeholders are retained for compatibility and must not be interpreted as measured zero performance.

## Report Presence

| Report | Present |
| --- | ---: |
| `reports/stages/answer_evaluation.json` | True |
| `reports/stages/answer_llm_judge.json` | True |
| `reports/stages/chunking_comparison.json` | True |
| `reports/stages/curated_ontology_evaluation.json` | True |
| `reports/stages/graph_traversal_ablation.json` | True |
| `reports/stages/graph_traversal_ablation_benchmark_v2.json` | True |
| `reports/stages/kg_extraction_comparison.json` | True |
| `reports/stages/kg_validation.json` | True |
| `reports/stages/retrieval_ablation.json` | True |
| `reports/stages/retrieval_ablation_benchmark_v2.json` | True |
| `reports/stages/robustness_evaluation.json` | True |
| `reports/stages/sufficiency_evaluation.json` | True |
| `reports/stages/triple_semantic_llm_review.json` | True |
| `reports/stages/triple_semantic_review_sample.json` | True |

## Evidence Gaps Before Thesis Submission

- Path Recall@k and Path Precision@k are heuristic unless graph-path LLM review is cited.
- Triple semantic correctness is absent or LLM-estimated; no human expert verification is claimed.
- Faithfulness, answer correctness, and answer relevance are deterministic heuristics unless an explicit LLM-as-judge run is added.
- Benchmark labels are thesis/course-project evidence, not external aviation-expert certification.
