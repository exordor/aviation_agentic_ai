# Chunking Comparison Benchmark V2

- Run ID: `chunking-comparison-benchmark-v2-20260530T101838Z`
- Labels: 120
- Supported labels: 100
- Insufficient-evidence labels: 20
- Evaluation mode: `top_k`
- Context budget chars: None
- Scoring: layered metrics only; no single mixed overall score.
- Claim boundary: rankings are benchmark-specific and do not identify a universal best chunker.
- Supported-only retrieval metrics are primary; all-label metrics are diagnostic.
- Top-k rankings can privilege larger chunks by exposing more context; fixed-budget results are the fairer comparison when available.

## Supported-Only Ranking

| Rank | Strategy | Recall@5 | Recall@10 | Precision@5 | MRR@5 | MRR@10 | NDCG@10 | Context Precision@5 | Context Recall |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | structure_aware_large | 0.85 | 0.96 | 0.188 | 0.6262 | 0.6412 | 0.7355 | 0.188 | 0.945 |
| 2 | fixed_large | 0.85 | 0.95 | 0.188 | 0.5935 | 0.6081 | 0.707 | 0.188 | 0.935 |
| 3 | recursive_large | 0.84 | 0.96 | 0.19 | 0.6198 | 0.6372 | 0.7475 | 0.19 | 0.945 |
| 4 | recursive_medium | 0.83 | 0.91 | 0.176 | 0.5245 | 0.5353 | 0.6403 | 0.176 | 0.885 |
| 5 | fixed_medium | 0.79 | 0.88 | 0.162 | 0.5198 | 0.5324 | 0.618 | 0.162 | 0.855 |
| 6 | structure_aware_medium | 0.79 | 0.89 | 0.164 | 0.5113 | 0.5269 | 0.6178 | 0.164 | 0.86 |
| 7 | embedding_semantic | 0.73 | 0.85 | 0.146 | 0.5337 | 0.5517 | 0.6023 | 0.146 | 0.815 |
| 8 | hierarchical_parent_child | 0.71 | 0.81 | 0.15 | 0.4628 | 0.4782 | 0.5662 | 0.15 | 0.78 |
| 9 | recursive_small | 0.71 | 0.81 | 0.15 | 0.4628 | 0.4782 | 0.5662 | 0.15 | 0.78 |
| 10 | semantic_meta_like | 0.68 | 0.79 | 0.136 | 0.4502 | 0.4658 | 0.5277 | 0.136 | 0.755 |
| 11 | fixed_small | 0.64 | 0.77 | 0.128 | 0.4287 | 0.4463 | 0.5024 | 0.128 | 0.73 |
| 12 | structure_aware | 0.57 | 0.68 | 0.132 | 0.3913 | 0.4065 | 0.5099 | 0.132 | 0.655 |
| 13 | proposition_like | 0.56 | 0.63 | 0.112 | 0.3565 | 0.3654 | 0.4106 | 0.112 | 0.59 |
| 14 | contextual_prefix | 0.45 | 0.51 | 0.106 | 0.2693 | 0.2773 | 0.362 | 0.106 | 0.48 |

## Strategy Cost And Chunking Diagnostics

| Strategy | Chunks | Avg chars | P95 chars | Avg tokens | Boundary preservation | Overlap redundancy | Index build s | Mean query s | P95 query s | Index bytes | Cost notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| fixed_small | 106 | 377.68 | 399 | 63.14 | 0.1038 | 0.1913 | 2.5824 | 0.0871 | 0.0977 | 2384856 | Small chunks may improve localization while increasing index size and KG extraction units. |
| fixed_medium | 48 | 794.21 | 899 | 132.46 | 0.1042 | 0.1493 | 0.9131 | 0.0858 | 0.089 | 2081752 | Cost impact is interpreted from chunk count, chunk size, index size, and latency. |
| fixed_large | 27 | 1359.22 | 1598 | 226.15 | 0.1481 | 0.1158 | 0.5562 | 0.0863 | 0.0913 | 1844184 | Large chunks may preserve broad context while diluting top-k precision. |
| recursive_small | 107 | 358.78 | 399 | 60.58 | 0.3084 | 0.152 | 2.0605 | 0.0864 | 0.0897 | 2425816 | Small chunks may improve localization while increasing index size and KG extraction units. |
| recursive_medium | 48 | 782.17 | 898 | 132.4 | 0.25 | 0.1327 | 0.9363 | 0.0861 | 0.0909 | 1774552 | Cost impact is interpreted from chunk count, chunk size, index size, and latency. |
| recursive_large | 27 | 1355.26 | 1593 | 228 | 0.3704 | 0.1105 | 0.5794 | 0.0867 | 0.093 | 1819608 | Large chunks may preserve broad context while diluting top-k precision. |
| structure_aware | 267 | 233.36 | 1080 | 42.07 | 1.0 | 0.4789 | 4.9164 | 0.0855 | 0.0891 | 3249112 | Small chunks may improve localization while increasing index size and KG extraction units. |
| structure_aware_medium | 48 | 775.02 | 896 | 129.04 | 1.0 | 0.1273 | 0.9163 | 0.0859 | 0.0894 | 2748908 | Cost impact is interpreted from chunk count, chunk size, index size, and latency. |
| structure_aware_large | 27 | 1349.63 | 1591 | 224.26 | 1.0 | 0.1091 | 0.5624 | 0.0862 | 0.0957 | 2757100 | Large chunks may preserve broad context while diluting top-k precision. |
| semantic_meta_like | 56 | 580.55 | 712 | 98.09 | 1.0 | 0.0 | 1.0573 | 0.0864 | 0.0975 | 2110424 | Small chunks may improve localization while increasing index size and KG extraction units. |
| embedding_semantic | 53 | 613.47 | 890 | 103.64 | 1.0 | 0.0 | 1.0521 | 0.0862 | 0.0911 | 2147288 | Cost impact is interpreted from chunk count, chunk size, index size, and latency. |
| proposition_like | 84 | 387.9 | 809 | 65.69 | 0.9524 | 0.0028 | 1.553 | 0.0864 | 0.0927 | 2294744 | Heuristic proposition-like segmentation may increase chunk count and review cost. |
| hierarchical_parent_child | 107 | 358.78 | 399 | 60.58 | 1.0 | 0.152 | 1.9194 | 0.0858 | 0.0884 | 2483160 | Child chunks are indexed with parent metadata; full parent-return retrieval is not claimed in this report. |
| contextual_prefix | 279 | 303.71 | 944 | 48.94 | 1.0 | 0.49 | 5.0676 | 0.0855 | 0.0899 | 4359128 | Deterministic prefixes add metadata tokens to every indexed chunk. |

## Confidence Intervals

| Strategy | Metric | Mean | 95% CI | n |
| --- | --- | ---: | --- | ---: |
| fixed_small | recall_at_5 | 0.64 | 0.54 - 0.74 | 100 |
| fixed_small | recall_at_10 | 0.77 | 0.69 - 0.85 | 100 |
| fixed_small | mrr_at_5 | 0.4287 | 0.3462 - 0.514 | 100 |
| fixed_small | ndcg_at_10 | 0.5024 | 0.4322 - 0.5734 | 100 |
| fixed_small | context_recall | 0.73 | 0.65 - 0.815 | 100 |
| fixed_medium | recall_at_5 | 0.79 | 0.7 - 0.87 | 100 |
| fixed_medium | recall_at_10 | 0.88 | 0.82 - 0.94 | 100 |
| fixed_medium | mrr_at_5 | 0.5198 | 0.4408 - 0.6007 | 100 |
| fixed_medium | ndcg_at_10 | 0.618 | 0.5483 - 0.6874 | 100 |
| fixed_medium | context_recall | 0.855 | 0.785 - 0.915 | 100 |
| fixed_large | recall_at_5 | 0.85 | 0.78 - 0.91 | 100 |
| fixed_large | recall_at_10 | 0.95 | 0.91 - 0.99 | 100 |
| fixed_large | mrr_at_5 | 0.5935 | 0.5265 - 0.6668 | 100 |
| fixed_large | ndcg_at_10 | 0.707 | 0.6484 - 0.7709 | 100 |
| fixed_large | context_recall | 0.935 | 0.89 - 0.975 | 100 |
| recursive_small | recall_at_5 | 0.71 | 0.62 - 0.8 | 100 |
| recursive_small | recall_at_10 | 0.81 | 0.73 - 0.88 | 100 |
| recursive_small | mrr_at_5 | 0.4628 | 0.3862 - 0.547 | 100 |
| recursive_small | ndcg_at_10 | 0.5662 | 0.4872 - 0.6436 | 100 |
| recursive_small | context_recall | 0.78 | 0.705 - 0.855 | 100 |
| recursive_medium | recall_at_5 | 0.83 | 0.75 - 0.9 | 100 |
| recursive_medium | recall_at_10 | 0.91 | 0.85 - 0.96 | 100 |
| recursive_medium | mrr_at_5 | 0.5245 | 0.4507 - 0.5977 | 100 |
| recursive_medium | ndcg_at_10 | 0.6403 | 0.5716 - 0.7145 | 100 |
| recursive_medium | context_recall | 0.885 | 0.82 - 0.94 | 100 |
| recursive_large | recall_at_5 | 0.84 | 0.77 - 0.91 | 100 |
| recursive_large | recall_at_10 | 0.96 | 0.92 - 0.99 | 100 |
| recursive_large | mrr_at_5 | 0.6198 | 0.5455 - 0.6943 | 100 |
| recursive_large | ndcg_at_10 | 0.7475 | 0.6869 - 0.8154 | 100 |
| recursive_large | context_recall | 0.945 | 0.9 - 0.98 | 100 |
| structure_aware | recall_at_5 | 0.57 | 0.47 - 0.67 | 100 |
| structure_aware | recall_at_10 | 0.68 | 0.59 - 0.77 | 100 |
| structure_aware | mrr_at_5 | 0.3913 | 0.3083 - 0.4778 | 100 |
| structure_aware | ndcg_at_10 | 0.5099 | 0.4099 - 0.6153 | 100 |
| structure_aware | context_recall | 0.655 | 0.565 - 0.75 | 100 |
| structure_aware_medium | recall_at_5 | 0.79 | 0.7 - 0.87 | 100 |
| structure_aware_medium | recall_at_10 | 0.89 | 0.83 - 0.95 | 100 |
| structure_aware_medium | mrr_at_5 | 0.5113 | 0.4327 - 0.5935 | 100 |
| structure_aware_medium | ndcg_at_10 | 0.6178 | 0.5456 - 0.6935 | 100 |
| structure_aware_medium | context_recall | 0.86 | 0.795 - 0.92 | 100 |
| structure_aware_large | recall_at_5 | 0.85 | 0.79 - 0.91 | 100 |
| structure_aware_large | recall_at_10 | 0.96 | 0.92 - 0.99 | 100 |
| structure_aware_large | mrr_at_5 | 0.6262 | 0.5508 - 0.6955 | 100 |
| structure_aware_large | ndcg_at_10 | 0.7355 | 0.6753 - 0.7997 | 100 |
| structure_aware_large | context_recall | 0.945 | 0.9 - 0.98 | 100 |
| semantic_meta_like | recall_at_5 | 0.68 | 0.58 - 0.77 | 100 |
| semantic_meta_like | recall_at_10 | 0.79 | 0.71 - 0.86 | 100 |
| semantic_meta_like | mrr_at_5 | 0.4502 | 0.368 - 0.5257 | 100 |
| semantic_meta_like | ndcg_at_10 | 0.5277 | 0.4537 - 0.595 | 100 |
| semantic_meta_like | context_recall | 0.755 | 0.675 - 0.83 | 100 |
| embedding_semantic | recall_at_5 | 0.73 | 0.65 - 0.81 | 100 |
| embedding_semantic | recall_at_10 | 0.85 | 0.78 - 0.91 | 100 |
| embedding_semantic | mrr_at_5 | 0.5337 | 0.449 - 0.6097 | 100 |
| embedding_semantic | ndcg_at_10 | 0.6023 | 0.5323 - 0.6691 | 100 |
| embedding_semantic | context_recall | 0.815 | 0.745 - 0.88 | 100 |
| proposition_like | recall_at_5 | 0.56 | 0.46 - 0.66 | 100 |
| proposition_like | recall_at_10 | 0.63 | 0.53 - 0.73 | 100 |
| proposition_like | mrr_at_5 | 0.3565 | 0.275 - 0.44 | 100 |
| proposition_like | ndcg_at_10 | 0.4106 | 0.3338 - 0.4933 | 100 |
| proposition_like | context_recall | 0.59 | 0.495 - 0.69 | 100 |
| hierarchical_parent_child | recall_at_5 | 0.71 | 0.62 - 0.8 | 100 |
| hierarchical_parent_child | recall_at_10 | 0.81 | 0.73 - 0.88 | 100 |
| hierarchical_parent_child | mrr_at_5 | 0.4628 | 0.3862 - 0.547 | 100 |
| hierarchical_parent_child | ndcg_at_10 | 0.5662 | 0.4872 - 0.6436 | 100 |
| hierarchical_parent_child | context_recall | 0.78 | 0.705 - 0.855 | 100 |
| contextual_prefix | recall_at_5 | 0.45 | 0.35 - 0.55 | 100 |
| contextual_prefix | recall_at_10 | 0.51 | 0.42 - 0.6 | 100 |
| contextual_prefix | mrr_at_5 | 0.2693 | 0.1982 - 0.3477 | 100 |
| contextual_prefix | ndcg_at_10 | 0.362 | 0.2682 - 0.4681 | 100 |
| contextual_prefix | context_recall | 0.48 | 0.39 - 0.575 | 100 |

## Supported Vs No-Answer Diagnostics

| Strategy | Supported Recall@5 | All-label Recall@5 diagnostic | No-answer context rate@5 | No-answer key-entity overlap@5 |
| --- | ---: | ---: | ---: | ---: |
| fixed_small | 0.64 | 0.5333 | 1.0 | 0.05 |
| fixed_medium | 0.79 | 0.6583 | 1.0 | 0.05 |
| fixed_large | 0.85 | 0.7083 | 1.0 | 0.05 |
| recursive_small | 0.71 | 0.5917 | 1.0 | 0.05 |
| recursive_medium | 0.83 | 0.6917 | 1.0 | 0.05 |
| recursive_large | 0.84 | 0.7 | 1.0 | 0.05 |
| structure_aware | 0.57 | 0.475 | 1.0 | 0.05 |
| structure_aware_medium | 0.79 | 0.6583 | 1.0 | 0.05 |
| structure_aware_large | 0.85 | 0.7083 | 1.0 | 0.05 |
| semantic_meta_like | 0.68 | 0.5667 | 1.0 | 0.05 |
| embedding_semantic | 0.73 | 0.6083 | 1.0 | 0.05 |
| proposition_like | 0.56 | 0.4667 | 1.0 | 0.05 |
| hierarchical_parent_child | 0.71 | 0.5917 | 1.0 | 0.05 |
| contextual_prefix | 0.45 | 0.375 | 1.0 | 0.05 |

## Chunk Size Sensitivity

### fixed

Small chunks can improve entity/fact localization; large chunks can preserve broader context but may reduce precision. Definition, causal, and cross-page questions may prefer different chunk sizes.

| Strategy | Chunks | Avg chars | P95 chars | Recall@5 | MRR@5 | Context Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fixed_small | 106 | 377.68 | 399 | 0.64 | 0.4287 | 0.73 |
| fixed_medium | 48 | 794.21 | 899 | 0.79 | 0.5198 | 0.855 |
| fixed_large | 27 | 1359.22 | 1598 | 0.85 | 0.5935 | 0.935 |

### recursive

Small chunks can improve entity/fact localization; large chunks can preserve broader context but may reduce precision. Definition, causal, and cross-page questions may prefer different chunk sizes.

| Strategy | Chunks | Avg chars | P95 chars | Recall@5 | MRR@5 | Context Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| recursive_small | 107 | 358.78 | 399 | 0.71 | 0.4628 | 0.78 |
| recursive_medium | 48 | 782.17 | 898 | 0.83 | 0.5245 | 0.885 |
| recursive_large | 27 | 1355.26 | 1593 | 0.84 | 0.6198 | 0.945 |


## Category-Level Analysis

| Strategy | Question type | Labels | Recall@5 | Recall@10 | MRR@5 | Context Recall |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| fixed_small | supported_factual | 40 | 0.625 | 0.725 | 0.3642 | 0.725 |
| fixed_small | concept_definition | 15 | 0.6667 | 0.9333 | 0.5267 | 0.9333 |
| fixed_small | relation_causal | 15 | 0.9333 | 0.9333 | 0.6244 | 0.9333 |
| fixed_small | cross_page | 10 | 0.5 | 0.8 | 0.425 | 0.4 |
| fixed_small | paraphrase | 10 | 0.5 | 0.6 | 0.3833 | 0.6 |
| fixed_small | terminology_variation | 10 | 0.5 | 0.6 | 0.295 | 0.6 |
| fixed_small | insufficient_evidence | 20 | 0.0 | 0.0 | 0.0 | 1.0 |
| fixed_medium | supported_factual | 40 | 0.7 | 0.8 | 0.4558 | 0.8 |
| fixed_medium | concept_definition | 15 | 1.0 | 1.0 | 0.7333 | 1.0 |
| fixed_medium | relation_causal | 15 | 0.9333 | 1.0 | 0.7 | 1.0 |
| fixed_medium | cross_page | 10 | 0.9 | 1.0 | 0.44 | 0.75 |
| fixed_medium | paraphrase | 10 | 0.6 | 0.8 | 0.425 | 0.8 |
| fixed_medium | terminology_variation | 10 | 0.7 | 0.8 | 0.36 | 0.8 |
| fixed_medium | insufficient_evidence | 20 | 0.0 | 0.0 | 0.0 | 1.0 |
| fixed_large | supported_factual | 40 | 0.825 | 0.95 | 0.5987 | 0.95 |
| fixed_large | concept_definition | 15 | 1.0 | 1.0 | 0.8222 | 1.0 |
| fixed_large | relation_causal | 15 | 0.8 | 0.8667 | 0.5889 | 0.8667 |
| fixed_large | cross_page | 10 | 1.0 | 1.0 | 0.5666 | 0.85 |
| fixed_large | paraphrase | 10 | 0.7 | 0.9 | 0.4333 | 0.9 |
| fixed_large | terminology_variation | 10 | 0.8 | 1.0 | 0.4233 | 1.0 |
| fixed_large | insufficient_evidence | 20 | 0.0 | 0.0 | 0.0 | 1.0 |
| recursive_small | supported_factual | 40 | 0.75 | 0.8 | 0.4537 | 0.8 |
| recursive_small | concept_definition | 15 | 0.6667 | 0.9333 | 0.5189 | 0.9333 |
| recursive_small | relation_causal | 15 | 1.0 | 1.0 | 0.6911 | 1.0 |
| recursive_small | cross_page | 10 | 0.6 | 0.7 | 0.325 | 0.4 |
| recursive_small | paraphrase | 10 | 0.6 | 0.7 | 0.39 | 0.7 |
| recursive_small | terminology_variation | 10 | 0.4 | 0.6 | 0.2833 | 0.6 |
| recursive_small | insufficient_evidence | 20 | 0.0 | 0.0 | 0.0 | 1.0 |
| recursive_medium | supported_factual | 40 | 0.75 | 0.875 | 0.4425 | 0.875 |
| recursive_medium | concept_definition | 15 | 1.0 | 1.0 | 0.6967 | 1.0 |
| recursive_medium | relation_causal | 15 | 0.9333 | 1.0 | 0.75 | 1.0 |
| recursive_medium | cross_page | 10 | 0.9 | 1.0 | 0.4333 | 0.75 |
| recursive_medium | paraphrase | 10 | 0.6 | 0.7 | 0.3867 | 0.7 |
| recursive_medium | terminology_variation | 10 | 0.9 | 0.9 | 0.485 | 0.9 |
| recursive_medium | insufficient_evidence | 20 | 0.0 | 0.0 | 0.0 | 1.0 |
| recursive_large | supported_factual | 40 | 0.775 | 0.975 | 0.6008 | 0.975 |
| recursive_large | concept_definition | 15 | 1.0 | 1.0 | 0.8222 | 1.0 |
| recursive_large | relation_causal | 15 | 0.8667 | 0.8667 | 0.75 | 0.8667 |
| recursive_large | cross_page | 10 | 1.0 | 1.0 | 0.5833 | 0.85 |
| recursive_large | paraphrase | 10 | 0.7 | 0.9 | 0.4167 | 0.9 |
| recursive_large | terminology_variation | 10 | 0.8 | 1.0 | 0.4367 | 1.0 |
| recursive_large | insufficient_evidence | 20 | 0.0 | 0.0 | 0.0 | 1.0 |
| structure_aware | supported_factual | 40 | 0.425 | 0.525 | 0.2683 | 0.525 |
| structure_aware | concept_definition | 15 | 0.8667 | 0.9333 | 0.6167 | 0.9333 |
| structure_aware | relation_causal | 15 | 0.9333 | 0.9333 | 0.5967 | 0.9333 |
| structure_aware | cross_page | 10 | 0.5 | 0.6 | 0.4333 | 0.35 |
| structure_aware | paraphrase | 10 | 0.4 | 0.7 | 0.3333 | 0.7 |
| structure_aware | terminology_variation | 10 | 0.4 | 0.6 | 0.2533 | 0.6 |
| structure_aware | insufficient_evidence | 20 | 0.0 | 0.0 | 0.0 | 1.0 |
| structure_aware_medium | supported_factual | 40 | 0.75 | 0.825 | 0.4212 | 0.825 |
| structure_aware_medium | concept_definition | 15 | 1.0 | 1.0 | 0.7267 | 1.0 |
| structure_aware_medium | relation_causal | 15 | 0.9333 | 1.0 | 0.75 | 1.0 |
| structure_aware_medium | cross_page | 10 | 0.8 | 1.0 | 0.4533 | 0.7 |
| structure_aware_medium | paraphrase | 10 | 0.5 | 0.8 | 0.4333 | 0.8 |
| structure_aware_medium | terminology_variation | 10 | 0.7 | 0.8 | 0.3267 | 0.8 |
| structure_aware_medium | insufficient_evidence | 20 | 0.0 | 0.0 | 0.0 | 1.0 |
| structure_aware_large | supported_factual | 40 | 0.825 | 0.975 | 0.6442 | 0.975 |
| structure_aware_large | concept_definition | 15 | 1.0 | 1.0 | 0.8056 | 1.0 |
| structure_aware_large | relation_causal | 15 | 0.8 | 0.8667 | 0.6467 | 0.8667 |
| structure_aware_large | cross_page | 10 | 1.0 | 1.0 | 0.5833 | 0.85 |
| structure_aware_large | paraphrase | 10 | 0.7 | 0.9 | 0.4833 | 0.9 |
| structure_aware_large | terminology_variation | 10 | 0.8 | 1.0 | 0.44 | 1.0 |
| structure_aware_large | insufficient_evidence | 20 | 0.0 | 0.0 | 0.0 | 1.0 |
| semantic_meta_like | supported_factual | 40 | 0.625 | 0.775 | 0.4029 | 0.775 |
| semantic_meta_like | concept_definition | 15 | 0.8 | 0.8667 | 0.6 | 0.8667 |
| semantic_meta_like | relation_causal | 15 | 0.9333 | 0.9333 | 0.5944 | 0.9333 |
| semantic_meta_like | cross_page | 10 | 0.6 | 0.8 | 0.3367 | 0.45 |
| semantic_meta_like | paraphrase | 10 | 0.6 | 0.6 | 0.4033 | 0.6 |
| semantic_meta_like | terminology_variation | 10 | 0.5 | 0.7 | 0.3583 | 0.7 |
| semantic_meta_like | insufficient_evidence | 20 | 0.0 | 0.0 | 0.0 | 1.0 |
| embedding_semantic | supported_factual | 40 | 0.7 | 0.825 | 0.4279 | 0.825 |
| embedding_semantic | concept_definition | 15 | 0.9333 | 0.9333 | 0.7944 | 0.9333 |
| embedding_semantic | relation_causal | 15 | 0.7333 | 0.8667 | 0.6556 | 0.8667 |
| embedding_semantic | cross_page | 10 | 0.7 | 0.9 | 0.5333 | 0.55 |
| embedding_semantic | paraphrase | 10 | 0.7 | 0.7 | 0.5083 | 0.7 |
| embedding_semantic | terminology_variation | 10 | 0.6 | 0.9 | 0.4083 | 0.9 |
| embedding_semantic | insufficient_evidence | 20 | 0.0 | 0.0 | 0.0 | 1.0 |
| proposition_like | supported_factual | 40 | 0.575 | 0.6 | 0.3137 | 0.6 |
| proposition_like | concept_definition | 15 | 0.5333 | 0.6 | 0.3967 | 0.6 |
| proposition_like | relation_causal | 15 | 0.7333 | 0.7333 | 0.5611 | 0.7333 |
| proposition_like | cross_page | 10 | 0.6 | 0.8 | 0.345 | 0.4 |
| proposition_like | paraphrase | 10 | 0.7 | 0.8 | 0.4783 | 0.8 |
| proposition_like | terminology_variation | 10 | 0.1 | 0.3 | 0.05 | 0.3 |
| proposition_like | insufficient_evidence | 20 | 0.0 | 0.0 | 0.0 | 1.0 |
| hierarchical_parent_child | supported_factual | 40 | 0.75 | 0.8 | 0.4537 | 0.8 |
| hierarchical_parent_child | concept_definition | 15 | 0.6667 | 0.9333 | 0.5189 | 0.9333 |
| hierarchical_parent_child | relation_causal | 15 | 1.0 | 1.0 | 0.6911 | 1.0 |
| hierarchical_parent_child | cross_page | 10 | 0.6 | 0.7 | 0.325 | 0.4 |
| hierarchical_parent_child | paraphrase | 10 | 0.6 | 0.7 | 0.39 | 0.7 |
| hierarchical_parent_child | terminology_variation | 10 | 0.4 | 0.6 | 0.2833 | 0.6 |
| hierarchical_parent_child | insufficient_evidence | 20 | 0.0 | 0.0 | 0.0 | 1.0 |
| contextual_prefix | supported_factual | 40 | 0.3 | 0.4 | 0.1537 | 0.4 |
| contextual_prefix | concept_definition | 15 | 0.7333 | 0.8 | 0.4778 | 0.8 |
| contextual_prefix | relation_causal | 15 | 0.8 | 0.8 | 0.5 | 0.8 |
| contextual_prefix | cross_page | 10 | 0.6 | 0.6 | 0.3117 | 0.3 |
| contextual_prefix | paraphrase | 10 | 0.3 | 0.3 | 0.25 | 0.3 |
| contextual_prefix | terminology_variation | 10 | 0.1 | 0.2 | 0.05 | 0.2 |
| contextual_prefix | insufficient_evidence | 20 | 0.0 | 0.0 | 0.0 | 1.0 |

## Implementation Metadata

- `fixed_small`: `{"configured_max_chars": ["400"], "configured_overlap_chars": ["80"], "profile_family": ["fixed_window"], "token_count": ["1", "24", "25", "28", "34", "35", "53", "55", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "75", "76", "81", "87", "91"]}`
- `fixed_medium`: `{"configured_max_chars": ["900"], "configured_overlap_chars": ["150"], "profile_family": ["fixed_window"], "token_count": ["1", "110", "129", "135", "138", "139", "140", "141", "142", "143", "144", "145", "146", "147", "148", "149", "150", "151", "153", "154", "155", "156", "159", "160", "161", "163", "164", "165", "169", "174", "28", "45", "58", "61", "66", "69", "90"]}`
- `fixed_large`: `{"configured_max_chars": ["1600"], "configured_overlap_chars": ["250"], "profile_family": ["fixed_window"], "token_count": ["1", "112", "116", "158", "169", "174", "188", "206", "223", "240", "247", "249", "250", "251", "262", "263", "264", "266", "273", "275", "281", "282", "291"]}`
- `recursive_small`: `{"configured_max_chars": ["400"], "configured_overlap_chars": ["80"], "profile_family": ["sentence_recursive"], "token_count": ["1", "102", "16", "30", "31", "33", "37", "38", "39", "48", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "75", "76", "81", "82", "84", "99"]}`
- `recursive_medium`: `{"configured_max_chars": ["900"], "configured_overlap_chars": ["150"], "profile_family": ["sentence_recursive"], "token_count": ["1", "122", "130", "131", "134", "135", "136", "137", "138", "139", "140", "141", "142", "143", "144", "145", "146", "147", "148", "149", "150", "151", "152", "154", "155", "157", "161", "168", "171", "219", "40", "49", "62", "66", "78", "88", "90"]}`
- `recursive_large`: `{"configured_max_chars": ["1600"], "configured_overlap_chars": ["250"], "profile_family": ["sentence_recursive"], "token_count": ["1", "104", "117", "174", "177", "185", "188", "213", "230", "239", "241", "247", "250", "254", "259", "260", "262", "266", "267", "272", "274", "275", "280", "283", "344"]}`
- `structure_aware`: `{"configured_max_chars": ["1200"], "configured_overlap_chars": ["150"], "profile_family": ["structure_aware"], "token_count": ["1", "10", "105", "106", "107", "11", "116", "12", "124", "128", "13", "136", "139", "14", "142", "144", "145", "15", "158", "16", "17", "170", "172", "18", "182", "183", "184", "185", "19", "190", "193", "196", "197", "198", "2", "20", "200", "205", "21", "22", "23", "24", "25", "26", "27", "28", "29", "3", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "4", "40", "41", "42", "43", "44", "45", "47", "48", "49", "5", "50", "51", "56", "6", "61", "64", "7", "70", "76", "8", "87", "9", "90", "95"]}`
- `structure_aware_medium`: `{"configured_max_chars": ["900"], "configured_overlap_chars": ["150"], "profile_family": ["structure_aware"], "token_count": ["1", "110", "122", "130", "132", "134", "135", "136", "138", "139", "141", "142", "143", "144", "145", "146", "147", "149", "150", "151", "152", "154", "155", "156", "157", "160", "161", "167", "168", "33", "40", "62", "64", "78", "83", "90"]}`
- `structure_aware_large`: `{"configured_max_chars": ["1600"], "configured_overlap_chars": ["250"], "profile_family": ["structure_aware"], "token_count": ["1", "117", "123", "161", "177", "181", "188", "211", "230", "238", "239", "241", "246", "247", "252", "254", "260", "265", "267", "269", "275", "280", "281", "286"]}`
- `semantic_meta_like`: `{"configured_max_chars": ["1200"], "configured_overlap_chars": ["150"], "profile_family": ["semantic_boundary_lexical"], "semantic_backend": ["lexical_similarity"], "token_count": ["1", "100", "101", "102", "103", "104", "105", "106", "107", "108", "109", "110", "111", "112", "115", "118", "119", "121", "122", "126", "129", "136", "138", "143", "20", "39", "4", "56", "63", "67", "73", "82", "93", "94", "95", "97", "98", "99"]}`
- `embedding_semantic`: `{"configured_max_chars": ["900"], "configured_overlap_chars": ["150"], "profile_family": ["semantic_boundary_embedding"], "semantic_backend": ["sentence_transformers"], "semantic_embedding_model": ["sentence-transformers/all-MiniLM-L6-v2"], "token_count": ["1", "101", "102", "106", "107", "108", "111", "113", "115", "119", "120", "123", "125", "13", "132", "135", "137", "138", "140", "141", "142", "144", "145", "146", "147", "150", "151", "157", "158", "215", "25", "29", "40", "42", "69", "71", "75", "78", "79", "82", "85", "86", "87", "88", "89", "93", "94", "99"]}`
- `proposition_like`: `{"configured_max_chars": ["900"], "configured_overlap_chars": ["80"], "llm_proposition_extraction": ["False"], "profile_family": ["proposition_like_heuristic"], "proposition_extraction": ["heuristic_sentence_cue"], "token_count": ["1", "106", "107", "112", "113", "115", "117", "118", "126", "129", "135", "142", "15", "167", "183", "19", "21", "219", "22", "24", "25", "26", "28", "29", "30", "33", "34", "35", "36", "39", "40", "42", "43", "44", "46", "47", "49", "50", "51", "54", "56", "57", "61", "62", "64", "66", "67", "69", "71", "72", "73", "75", "78", "80", "82", "83", "84", "85", "93", "95", "99"]}`
- `hierarchical_parent_child`: `{"configured_max_chars": ["400"], "configured_overlap_chars": ["80"], "parent_context_available": ["True"], "profile_family": ["hierarchical_parent_child"], "retrieval_integration": ["partial_child_index_parent_metadata"], "token_count": ["1", "102", "16", "30", "31", "33", "37", "38", "39", "48", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "75", "76", "81", "82", "84", "99"]}`
- `contextual_prefix`: `{"configured_max_chars": ["900"], "configured_overlap_chars": ["150"], "contextualization": ["deterministic_prefix"], "llm_contextualization": ["False"], "profile_family": ["contextual_prefix"], "token_count": ["10", "101", "102", "103", "11", "112", "113", "114", "12", "127", "13", "130", "131", "138", "14", "140", "142", "144", "146", "148", "149", "15", "150", "152", "153", "154", "156", "158", "159", "16", "161", "166", "167", "168", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "54", "55", "56", "57", "60", "61", "63", "68", "69", "71", "72", "77", "8", "85", "9", "98"]}`
