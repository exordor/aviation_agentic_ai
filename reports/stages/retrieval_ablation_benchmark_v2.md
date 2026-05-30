# Retrieval Ablation

- Run ID: `retrieval-ablation-20260530T013605Z`
- Questions: 120
- Supported labels: 100
- Insufficient-evidence labels: 20
- Scenarios: 12
- Scoring: layered retrieval and KG evidence metrics; no mixed overall score.
- Confidence intervals: deterministic bootstrap 95% CIs over per-question metrics.

| Scenario | Mode | Recall@5 | Recall@10 | Precision@5 | MRR@5 | MRR@10 | NDCG@10 | Context Precision@5 | Context Recall | Supported Recall@5 | KG coverage | Avg triples |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vector_hops2_v5_h8 | vector | 0.475 | 0.475 | 0.11 | 0.3261 | 0.3261 | 0.3863 | 0.11 | 0.6208 | 0.57 | 0.0 | 0.0 |
| hybrid_graph_disabled_hops2_v5_h8 | hybrid_graph_disabled | 0.475 | 0.475 | 0.11 | 0.3261 | 0.3261 | 0.3863 | 0.11 | 0.6208 | 0.57 | 0.0 | 0.0 |
| graph_hops1_v5_h8 | graph | 0.4083 | 0.4167 | 0.09 | 0.3043 | 0.3055 | 0.3503 | 0.0942 | 0.5667 | 0.49 | 0.8 | 7.5833 |
| graph_hops2_v5_h8 | graph | 0.4083 | 0.4167 | 0.09 | 0.3043 | 0.3055 | 0.3503 | 0.0942 | 0.5667 | 0.49 | 0.8 | 7.5833 |
| graph_hops3_v5_h8 | graph | 0.4083 | 0.4167 | 0.09 | 0.3043 | 0.3055 | 0.3503 | 0.0942 | 0.5667 | 0.49 | 0.8 | 7.5833 |
| hybrid_hops1_v5_h8 | hybrid | 0.5083 | 0.5917 | 0.1167 | 0.34 | 0.3529 | 0.4425 | 0.1167 | 0.7375 | 0.61 | 0.8 | 7.5833 |
| hybrid_hops2_v5_h8 | hybrid | 0.5083 | 0.5917 | 0.1167 | 0.34 | 0.3529 | 0.4425 | 0.1167 | 0.7375 | 0.61 | 0.8 | 7.5833 |
| hybrid_hops3_v5_h8 | hybrid | 0.5083 | 0.5917 | 0.1167 | 0.34 | 0.3529 | 0.4425 | 0.1167 | 0.7375 | 0.61 | 0.8 | 7.5833 |
| hybrid_hops2_v3_h8 | hybrid | 0.525 | 0.575 | 0.1167 | 0.3428 | 0.3509 | 0.4326 | 0.1167 | 0.7208 | 0.63 | 0.8 | 7.5833 |
| hybrid_hops2_v8_h8 | hybrid | 0.5 | 0.5833 | 0.1133 | 0.3339 | 0.3472 | 0.4361 | 0.1133 | 0.7292 | 0.6 | 0.8 | 7.5833 |
| hybrid_hops2_v5_h5 | hybrid | 0.5167 | 0.5167 | 0.1183 | 0.3447 | 0.3447 | 0.4154 | 0.1183 | 0.6625 | 0.62 | 0.7917 | 4.8 |
| hybrid_hops2_v5_h10 | hybrid | 0.5083 | 0.6 | 0.1167 | 0.3414 | 0.3552 | 0.4454 | 0.1167 | 0.7458 | 0.61 | 0.8083 | 9.4167 |

## Confidence Intervals

| Scenario | Metric | Mean | 95% CI | n |
| --- | --- | ---: | --- | ---: |
| vector_hops2_v5_h8 | recall_at_5 | 0.475 | 0.3917 - 0.5667 | 120 |
| vector_hops2_v5_h8 | recall_at_10 | 0.475 | 0.3917 - 0.5667 | 120 |
| vector_hops2_v5_h8 | mrr_at_5 | 0.3261 | 0.2547 - 0.4017 | 120 |
| vector_hops2_v5_h8 | mrr_at_10 | 0.3261 | 0.2547 - 0.4017 | 120 |
| vector_hops2_v5_h8 | ndcg_at_10 | 0.3863 | 0.3023 - 0.4754 | 120 |
| vector_hops2_v5_h8 | context_precision_at_5 | 0.11 | 0.0867 - 0.1367 | 120 |
| vector_hops2_v5_h8 | context_recall | 0.6208 | 0.5375 - 0.7083 | 120 |
| hybrid_graph_disabled_hops2_v5_h8 | recall_at_5 | 0.475 | 0.3917 - 0.5667 | 120 |
| hybrid_graph_disabled_hops2_v5_h8 | recall_at_10 | 0.475 | 0.3917 - 0.5667 | 120 |
| hybrid_graph_disabled_hops2_v5_h8 | mrr_at_5 | 0.3261 | 0.2547 - 0.4017 | 120 |
| hybrid_graph_disabled_hops2_v5_h8 | mrr_at_10 | 0.3261 | 0.2547 - 0.4017 | 120 |
| hybrid_graph_disabled_hops2_v5_h8 | ndcg_at_10 | 0.3863 | 0.3023 - 0.4754 | 120 |
| hybrid_graph_disabled_hops2_v5_h8 | context_precision_at_5 | 0.11 | 0.0867 - 0.1367 | 120 |
| hybrid_graph_disabled_hops2_v5_h8 | context_recall | 0.6208 | 0.5375 - 0.7083 | 120 |
| graph_hops1_v5_h8 | recall_at_5 | 0.4083 | 0.3167 - 0.5 | 120 |
| graph_hops1_v5_h8 | recall_at_10 | 0.4167 | 0.325 - 0.5083 | 120 |
| graph_hops1_v5_h8 | mrr_at_5 | 0.3043 | 0.2281 - 0.3844 | 120 |
| graph_hops1_v5_h8 | mrr_at_10 | 0.3055 | 0.2313 - 0.3861 | 120 |
| graph_hops1_v5_h8 | ndcg_at_10 | 0.3503 | 0.2636 - 0.4407 | 120 |
| graph_hops1_v5_h8 | context_precision_at_5 | 0.0942 | 0.0715 - 0.1178 | 120 |
| graph_hops1_v5_h8 | context_recall | 0.5667 | 0.4792 - 0.6542 | 120 |
| graph_hops2_v5_h8 | recall_at_5 | 0.4083 | 0.3167 - 0.5 | 120 |
| graph_hops2_v5_h8 | recall_at_10 | 0.4167 | 0.325 - 0.5083 | 120 |
| graph_hops2_v5_h8 | mrr_at_5 | 0.3043 | 0.2281 - 0.3844 | 120 |
| graph_hops2_v5_h8 | mrr_at_10 | 0.3055 | 0.2313 - 0.3861 | 120 |
| graph_hops2_v5_h8 | ndcg_at_10 | 0.3503 | 0.2636 - 0.4407 | 120 |
| graph_hops2_v5_h8 | context_precision_at_5 | 0.0942 | 0.0715 - 0.1178 | 120 |
| graph_hops2_v5_h8 | context_recall | 0.5667 | 0.4792 - 0.6542 | 120 |
| graph_hops3_v5_h8 | recall_at_5 | 0.4083 | 0.3167 - 0.5 | 120 |
| graph_hops3_v5_h8 | recall_at_10 | 0.4167 | 0.325 - 0.5083 | 120 |
| graph_hops3_v5_h8 | mrr_at_5 | 0.3043 | 0.2281 - 0.3844 | 120 |
| graph_hops3_v5_h8 | mrr_at_10 | 0.3055 | 0.2313 - 0.3861 | 120 |
| graph_hops3_v5_h8 | ndcg_at_10 | 0.3503 | 0.2636 - 0.4407 | 120 |
| graph_hops3_v5_h8 | context_precision_at_5 | 0.0942 | 0.0715 - 0.1178 | 120 |
| graph_hops3_v5_h8 | context_recall | 0.5667 | 0.4792 - 0.6542 | 120 |
| hybrid_hops1_v5_h8 | recall_at_5 | 0.5083 | 0.4167 - 0.6 | 120 |
| hybrid_hops1_v5_h8 | recall_at_10 | 0.5917 | 0.5 - 0.6833 | 120 |
| hybrid_hops1_v5_h8 | mrr_at_5 | 0.34 | 0.2697 - 0.4174 | 120 |
| hybrid_hops1_v5_h8 | mrr_at_10 | 0.3529 | 0.2843 - 0.4276 | 120 |
| hybrid_hops1_v5_h8 | ndcg_at_10 | 0.4425 | 0.3559 - 0.5322 | 120 |
| hybrid_hops1_v5_h8 | context_precision_at_5 | 0.1167 | 0.0917 - 0.14 | 120 |
| hybrid_hops1_v5_h8 | context_recall | 0.7375 | 0.6625 - 0.8125 | 120 |
| hybrid_hops2_v5_h8 | recall_at_5 | 0.5083 | 0.4167 - 0.6 | 120 |
| hybrid_hops2_v5_h8 | recall_at_10 | 0.5917 | 0.5 - 0.6833 | 120 |
| hybrid_hops2_v5_h8 | mrr_at_5 | 0.34 | 0.2697 - 0.4174 | 120 |
| hybrid_hops2_v5_h8 | mrr_at_10 | 0.3529 | 0.2843 - 0.4276 | 120 |
| hybrid_hops2_v5_h8 | ndcg_at_10 | 0.4425 | 0.3559 - 0.5322 | 120 |
| hybrid_hops2_v5_h8 | context_precision_at_5 | 0.1167 | 0.0917 - 0.14 | 120 |
| hybrid_hops2_v5_h8 | context_recall | 0.7375 | 0.6625 - 0.8125 | 120 |
| hybrid_hops3_v5_h8 | recall_at_5 | 0.5083 | 0.4167 - 0.6 | 120 |
| hybrid_hops3_v5_h8 | recall_at_10 | 0.5917 | 0.5 - 0.6833 | 120 |
| hybrid_hops3_v5_h8 | mrr_at_5 | 0.34 | 0.2697 - 0.4174 | 120 |
| hybrid_hops3_v5_h8 | mrr_at_10 | 0.3529 | 0.2843 - 0.4276 | 120 |
| hybrid_hops3_v5_h8 | ndcg_at_10 | 0.4425 | 0.3559 - 0.5322 | 120 |
| hybrid_hops3_v5_h8 | context_precision_at_5 | 0.1167 | 0.0917 - 0.14 | 120 |
| hybrid_hops3_v5_h8 | context_recall | 0.7375 | 0.6625 - 0.8125 | 120 |
| hybrid_hops2_v3_h8 | recall_at_5 | 0.525 | 0.4333 - 0.6167 | 120 |
| hybrid_hops2_v3_h8 | recall_at_10 | 0.575 | 0.4833 - 0.6667 | 120 |
| hybrid_hops2_v3_h8 | mrr_at_5 | 0.3428 | 0.2726 - 0.4189 | 120 |
| hybrid_hops2_v3_h8 | mrr_at_10 | 0.3509 | 0.2804 - 0.4273 | 120 |
| hybrid_hops2_v3_h8 | ndcg_at_10 | 0.4326 | 0.3422 - 0.5202 | 120 |
| hybrid_hops2_v3_h8 | context_precision_at_5 | 0.1167 | 0.0933 - 0.1383 | 120 |
| hybrid_hops2_v3_h8 | context_recall | 0.7208 | 0.6375 - 0.7958 | 120 |
| hybrid_hops2_v8_h8 | recall_at_5 | 0.5 | 0.4167 - 0.5917 | 120 |
| hybrid_hops2_v8_h8 | recall_at_10 | 0.5833 | 0.4917 - 0.675 | 120 |
| hybrid_hops2_v8_h8 | mrr_at_5 | 0.3339 | 0.2635 - 0.4099 | 120 |
| hybrid_hops2_v8_h8 | mrr_at_10 | 0.3472 | 0.2775 - 0.4211 | 120 |
| hybrid_hops2_v8_h8 | ndcg_at_10 | 0.4361 | 0.3485 - 0.5241 | 120 |
| hybrid_hops2_v8_h8 | context_precision_at_5 | 0.1133 | 0.0883 - 0.1383 | 120 |
| hybrid_hops2_v8_h8 | context_recall | 0.7292 | 0.65 - 0.8042 | 120 |
| hybrid_hops2_v5_h5 | recall_at_5 | 0.5167 | 0.425 - 0.6083 | 120 |
| hybrid_hops2_v5_h5 | recall_at_10 | 0.5167 | 0.425 - 0.6083 | 120 |
| hybrid_hops2_v5_h5 | mrr_at_5 | 0.3447 | 0.2722 - 0.4222 | 120 |
| hybrid_hops2_v5_h5 | mrr_at_10 | 0.3447 | 0.2722 - 0.4222 | 120 |
| hybrid_hops2_v5_h5 | ndcg_at_10 | 0.4154 | 0.3216 - 0.5078 | 120 |
| hybrid_hops2_v5_h5 | context_precision_at_5 | 0.1183 | 0.0933 - 0.1417 | 120 |
| hybrid_hops2_v5_h5 | context_recall | 0.6625 | 0.575 - 0.7458 | 120 |
| hybrid_hops2_v5_h10 | recall_at_5 | 0.5083 | 0.4167 - 0.6 | 120 |
| hybrid_hops2_v5_h10 | recall_at_10 | 0.6 | 0.5083 - 0.6917 | 120 |
| hybrid_hops2_v5_h10 | mrr_at_5 | 0.3414 | 0.2693 - 0.4193 | 120 |
| hybrid_hops2_v5_h10 | mrr_at_10 | 0.3552 | 0.2832 - 0.4313 | 120 |
| hybrid_hops2_v5_h10 | ndcg_at_10 | 0.4454 | 0.3593 - 0.5365 | 120 |
| hybrid_hops2_v5_h10 | context_precision_at_5 | 0.1167 | 0.0917 - 0.14 | 120 |
| hybrid_hops2_v5_h10 | context_recall | 0.7458 | 0.6708 - 0.8167 | 120 |

## Supported Vs Insufficient-Evidence Breakdown

| Scenario | Group | Records | Recall@5 | MRR@5 | Context Recall |
| --- | --- | ---: | ---: | ---: | ---: |
| vector_hops2_v5_h8 | supported | 100 | 0.57 | 0.3913 | 0.545 |
| vector_hops2_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_graph_disabled_hops2_v5_h8 | supported | 100 | 0.57 | 0.3913 | 0.545 |
| hybrid_graph_disabled_hops2_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| graph_hops1_v5_h8 | supported | 100 | 0.49 | 0.3652 | 0.48 |
| graph_hops1_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| graph_hops2_v5_h8 | supported | 100 | 0.49 | 0.3652 | 0.48 |
| graph_hops2_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| graph_hops3_v5_h8 | supported | 100 | 0.49 | 0.3652 | 0.48 |
| graph_hops3_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_hops1_v5_h8 | supported | 100 | 0.61 | 0.408 | 0.685 |
| hybrid_hops1_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v5_h8 | supported | 100 | 0.61 | 0.408 | 0.685 |
| hybrid_hops2_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_hops3_v5_h8 | supported | 100 | 0.61 | 0.408 | 0.685 |
| hybrid_hops3_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v3_h8 | supported | 100 | 0.63 | 0.4113 | 0.665 |
| hybrid_hops2_v3_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v8_h8 | supported | 100 | 0.6 | 0.4007 | 0.675 |
| hybrid_hops2_v8_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v5_h5 | supported | 100 | 0.62 | 0.4137 | 0.595 |
| hybrid_hops2_v5_h5 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v5_h10 | supported | 100 | 0.61 | 0.4097 | 0.695 |
| hybrid_hops2_v5_h10 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |

## Interpretation

### vector_hops2_v5_h8

Vector retrieval measures whether semantic text search alone recovers the gold chunk/span/page evidence.

### hybrid_graph_disabled_hops2_v5_h8

This is the hybrid ablation with graph evidence disabled; it should match vector retrieval behavior while preserving the hybrid experiment label.

### graph_hops1_v5_h8

Graph retrieval is valuable when KG triples cover key entities, even if coarse Recall@5 is 0.4083 and evidence coverage is 0.8.

### graph_hops2_v5_h8

Graph retrieval is valuable when KG triples cover key entities, even if coarse Recall@5 is 0.4083 and evidence coverage is 0.8.

### graph_hops3_v5_h8

Graph retrieval is valuable when KG triples cover key entities, even if coarse Recall@5 is 0.4083 and evidence coverage is 0.8.

### hybrid_hops1_v5_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8) while not always improving page-level Recall@5 (0.5083).

### hybrid_hops2_v5_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8) while not always improving page-level Recall@5 (0.5083).

### hybrid_hops3_v5_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8) while not always improving page-level Recall@5 (0.5083).

### hybrid_hops2_v3_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8) while not always improving page-level Recall@5 (0.525).

### hybrid_hops2_v8_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8) while not always improving page-level Recall@5 (0.5).

### hybrid_hops2_v5_h5

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.7917) while not always improving page-level Recall@5 (0.5167).

### hybrid_hops2_v5_h10

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8083) while not always improving page-level Recall@5 (0.5083).
