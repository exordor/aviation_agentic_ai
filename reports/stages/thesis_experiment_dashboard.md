# Thesis Experiment Dashboard

- Source policy: aggregate existing reports; do not recompute experiments unnecessarily.
- Scoring policy: layered metrics; no mixed overall score.
- Advisory boundary: Aviation learning and decision support only; does not replace POH/AFM, approved checklists, ATC instructions, instructor guidance, regulations, or pilot judgment.

## Experiment Inventory

| Report | Present | Dataset | Questions | Layers | Manual review required |
| --- | ---: | --- | ---: | --- | ---: |
| `thesis_claims_review` | True | not_dataset_specific | n/a | claim_safety | False |
| `evaluation_protocol_review` | True | not_dataset_specific | n/a | evaluation_protocol | False |
| `benchmark_v2_summary` | True | benchmark_v2_120 | 120 | benchmark_validation | True |
| `retrieval_ablation_benchmark_v2` | True | benchmark_v2_120 | 120 | retrieval, kg_evidence | False |
| `graph_traversal_ablation_benchmark_v2` | True | benchmark_v2_120 | 120 | retrieval, graph_paths | True |
| `sufficiency_evaluation` | True | benchmark_v2_120 | 120 | safety_abstention | False |
| `kg_extraction_comparison` | True | 35_question_expanded | n/a | ontology_kg | False |
| `curated_ontology_evaluation` | True | not_dataset_specific | n/a | ontology_kg | False |
| `triple_semantic_review_sample` | True | triple_semantic_review_sample | n/a | ontology_kg, manual_review | True |
| `answer_evaluation` | True | 10_cq_answer_subset | n/a | answer_generation, safety_abstention | False |
| `robustness_evaluation` | True | robustness_10_cases | n/a | safety_abstention, robustness | False |
| `benchmark_review_pack` | True | not_dataset_specific | 120 | benchmark_manual_review | True |

## RQ-To-Evidence Matrix

| RQ | Evidence reports | Primary metrics | Claim strength | Remaining gaps |
| --- | --- | --- | --- | --- |
| RQ1 ontology constraint | curated_ontology_evaluation, kg_extraction_comparison, kg_validation | RDF/OWL parse validity, label/comment coverage, unsupported class/property count, provenance completeness | strong | Triple semantic correctness still requires manual review. |
| RQ2 evidence traceability | retrieval_ablation_benchmark_v2, graph_traversal_ablation_benchmark_v2, answer_evaluation | KG evidence coverage, citation completeness, citation precision, citation recall | moderate | Answer-level manual or LLM-judge evaluation is optional and not run. |
| RQ3 graph evidence vs vector sufficiency | retrieval_ablation_benchmark_v2, graph_traversal_ablation_benchmark_v2 | Recall@5, Recall@10, MRR@5, NDCG@10, Path Recall@5, Path Precision@5 | moderate | Path relevance metrics are heuristic until manually reviewed. |
| RQ4 safety-aware abstention | sufficiency_evaluation, robustness_evaluation | Abstention Accuracy, False Answer Rate, False Abstention Rate, Risk Category Accuracy | moderate | Sufficiency can create false abstentions on supported questions. |

## Dataset Usage Matrix

| Dataset | Purpose | Evidence role | Main claim support | Limitations |
| --- | --- | --- | --- | --- |
| 10-CQ pilot | demo and qualitative answer inspection | pilot | partial | too small for main thesis retrieval claims |
| 35-question expanded | pilot ablation and KG extraction comparison | pilot | partial | pilot-sized and not the main benchmark |
| benchmark v2 120 | main thesis retrieval and safety benchmark | main_thesis_benchmark | yes | machine-seeded and requires manual naturalness review |
| answer-eval subset | answer citation and faithfulness heuristics | pilot | partial | small subset; deterministic heuristic scores |
| triple semantic review sample | manual KG semantic correctness review template | manual_review_pending | partial | review fields pending; no correctness results claimed |

## Primary Results

| Metric group | Key numbers |
| --- | --- |
| vector-only benchmark v2 | Recall@5=0.475, Recall@10=0.475, MRR@5=0.3261, NDCG@10=0.3863 |
| lexical hybrid benchmark v2 | Recall@5=0.5083, Recall@10=0.5917, MRR@5=0.34, NDCG@10=0.4425, Context Recall=0.7375 |
| traversal hybrid | Recall@5=0.4583, Path Recall@5=0.6583, Path Precision@5=0.6522 (heuristic, requires manual review) |
| sufficiency | Abstention Accuracy=1.0, False Answer Rate=0.0, False Abstention Rate=0.29 |
| KG | Provenance Completeness=1.0, Evidence-in-source Rate=1.0, Valid Triples=448 |
| triple semantic review | Sample=100, reviewed=0, needs_review=100 |

## Failure-Mode Summary

- Graph failure categories: {'generic_seed_node': 75, 'graph_fusion_dilution': 100, 'kg_sparse_for_question': 374, 'low_value_predicate': 154, 'path_found_but_wrong_chunk': 322, 'seed_linking_error': 150}
- False abstention on supported questions: 29
- Machine-seeded benchmark wording findings: 90
- Missing manual triple review items: 100

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
- `manual_review_dependent_metrics_not_completed`: True
- `no_unsafe_claim_patterns`: True
- `all_passed`: True
