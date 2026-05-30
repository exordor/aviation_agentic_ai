# Retrieval Ablation

- Run ID: `retrieval-ablation-20260530T094831Z`
- Questions: 120
- Supported labels: 100
- Insufficient-evidence labels: 20
- Scenarios: 12
- Scoring: layered retrieval and KG evidence metrics; no mixed overall score.
- Confidence intervals: deterministic bootstrap 95% CIs over per-question metrics.

| Scenario | Mode | Recall@5 | Recall@10 | Precision@5 | MRR@5 | MRR@10 | NDCG@10 | Context Precision@5 | Context Recall | Supported Recall@5 | KG coverage | Avg triples |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vector_hops2_v5_h8 | vector | 0.475 | 0.475 | 0.11 | 0.3268 | 0.3268 | 0.3869 | 0.11 | 0.6208 | 0.57 | 0.0 | 0.0 |
| hybrid_graph_disabled_hops2_v5_h8 | hybrid_graph_disabled | 0.475 | 0.475 | 0.11 | 0.3268 | 0.3268 | 0.3869 | 0.11 | 0.6208 | 0.57 | 0.0 | 0.0 |
| graph_hops1_v5_h8 | graph | 0.4083 | 0.4167 | 0.09 | 0.3043 | 0.3055 | 0.3503 | 0.0942 | 0.5667 | 0.49 | 0.8 | 7.5833 |
| graph_hops2_v5_h8 | graph | 0.4083 | 0.4167 | 0.09 | 0.3043 | 0.3055 | 0.3503 | 0.0942 | 0.5667 | 0.49 | 0.8 | 7.5833 |
| graph_hops3_v5_h8 | graph | 0.4083 | 0.4167 | 0.09 | 0.3043 | 0.3055 | 0.3503 | 0.0942 | 0.5667 | 0.49 | 0.8 | 7.5833 |
| hybrid_hops1_v5_h8 | hybrid | 0.5167 | 0.5917 | 0.1183 | 0.3417 | 0.3534 | 0.443 | 0.1183 | 0.7375 | 0.62 | 0.8 | 7.5833 |
| hybrid_hops2_v5_h8 | hybrid | 0.5167 | 0.5917 | 0.1183 | 0.3417 | 0.3534 | 0.443 | 0.1183 | 0.7375 | 0.62 | 0.8 | 7.5833 |
| hybrid_hops3_v5_h8 | hybrid | 0.5167 | 0.5917 | 0.1183 | 0.3417 | 0.3534 | 0.443 | 0.1183 | 0.7375 | 0.62 | 0.8 | 7.5833 |
| hybrid_hops2_v3_h8 | hybrid | 0.5333 | 0.5833 | 0.1183 | 0.3444 | 0.3526 | 0.4359 | 0.1183 | 0.7292 | 0.64 | 0.8 | 7.5833 |
| hybrid_hops2_v8_h8 | hybrid | 0.5083 | 0.5833 | 0.115 | 0.3356 | 0.3477 | 0.4366 | 0.115 | 0.7292 | 0.61 | 0.8 | 7.5833 |
| hybrid_hops2_v5_h5 | hybrid | 0.525 | 0.525 | 0.12 | 0.3464 | 0.3464 | 0.4186 | 0.12 | 0.6708 | 0.63 | 0.7917 | 4.8 |
| hybrid_hops2_v5_h10 | hybrid | 0.5167 | 0.6 | 0.1183 | 0.3431 | 0.3556 | 0.4459 | 0.1183 | 0.7458 | 0.62 | 0.8083 | 9.4167 |

## Confidence Intervals

| Scenario | Metric | Mean | 95% CI | n |
| --- | --- | ---: | --- | ---: |
| vector_hops2_v5_h8 | recall_at_5 | 0.475 | 0.3917 - 0.5667 | 120 |
| vector_hops2_v5_h8 | recall_at_10 | 0.475 | 0.3917 - 0.5667 | 120 |
| vector_hops2_v5_h8 | mrr_at_5 | 0.3268 | 0.2557 - 0.4035 | 120 |
| vector_hops2_v5_h8 | mrr_at_10 | 0.3268 | 0.2557 - 0.4035 | 120 |
| vector_hops2_v5_h8 | ndcg_at_10 | 0.3869 | 0.303 - 0.4754 | 120 |
| vector_hops2_v5_h8 | context_precision_at_5 | 0.11 | 0.0867 - 0.1367 | 120 |
| vector_hops2_v5_h8 | context_recall | 0.6208 | 0.5375 - 0.7083 | 120 |
| hybrid_graph_disabled_hops2_v5_h8 | recall_at_5 | 0.475 | 0.3917 - 0.5667 | 120 |
| hybrid_graph_disabled_hops2_v5_h8 | recall_at_10 | 0.475 | 0.3917 - 0.5667 | 120 |
| hybrid_graph_disabled_hops2_v5_h8 | mrr_at_5 | 0.3268 | 0.2557 - 0.4035 | 120 |
| hybrid_graph_disabled_hops2_v5_h8 | mrr_at_10 | 0.3268 | 0.2557 - 0.4035 | 120 |
| hybrid_graph_disabled_hops2_v5_h8 | ndcg_at_10 | 0.3869 | 0.303 - 0.4754 | 120 |
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
| hybrid_hops1_v5_h8 | recall_at_5 | 0.5167 | 0.425 - 0.6083 | 120 |
| hybrid_hops1_v5_h8 | recall_at_10 | 0.5917 | 0.5 - 0.6833 | 120 |
| hybrid_hops1_v5_h8 | mrr_at_5 | 0.3417 | 0.2714 - 0.4194 | 120 |
| hybrid_hops1_v5_h8 | mrr_at_10 | 0.3534 | 0.2843 - 0.4276 | 120 |
| hybrid_hops1_v5_h8 | ndcg_at_10 | 0.443 | 0.3568 - 0.533 | 120 |
| hybrid_hops1_v5_h8 | context_precision_at_5 | 0.1183 | 0.0933 - 0.1417 | 120 |
| hybrid_hops1_v5_h8 | context_recall | 0.7375 | 0.6625 - 0.8125 | 120 |
| hybrid_hops2_v5_h8 | recall_at_5 | 0.5167 | 0.425 - 0.6083 | 120 |
| hybrid_hops2_v5_h8 | recall_at_10 | 0.5917 | 0.5 - 0.6833 | 120 |
| hybrid_hops2_v5_h8 | mrr_at_5 | 0.3417 | 0.2714 - 0.4194 | 120 |
| hybrid_hops2_v5_h8 | mrr_at_10 | 0.3534 | 0.2843 - 0.4276 | 120 |
| hybrid_hops2_v5_h8 | ndcg_at_10 | 0.443 | 0.3568 - 0.533 | 120 |
| hybrid_hops2_v5_h8 | context_precision_at_5 | 0.1183 | 0.0933 - 0.1417 | 120 |
| hybrid_hops2_v5_h8 | context_recall | 0.7375 | 0.6625 - 0.8125 | 120 |
| hybrid_hops3_v5_h8 | recall_at_5 | 0.5167 | 0.425 - 0.6083 | 120 |
| hybrid_hops3_v5_h8 | recall_at_10 | 0.5917 | 0.5 - 0.6833 | 120 |
| hybrid_hops3_v5_h8 | mrr_at_5 | 0.3417 | 0.2714 - 0.4194 | 120 |
| hybrid_hops3_v5_h8 | mrr_at_10 | 0.3534 | 0.2843 - 0.4276 | 120 |
| hybrid_hops3_v5_h8 | ndcg_at_10 | 0.443 | 0.3568 - 0.533 | 120 |
| hybrid_hops3_v5_h8 | context_precision_at_5 | 0.1183 | 0.0933 - 0.1417 | 120 |
| hybrid_hops3_v5_h8 | context_recall | 0.7375 | 0.6625 - 0.8125 | 120 |
| hybrid_hops2_v3_h8 | recall_at_5 | 0.5333 | 0.4417 - 0.625 | 120 |
| hybrid_hops2_v3_h8 | recall_at_10 | 0.5833 | 0.4917 - 0.675 | 120 |
| hybrid_hops2_v3_h8 | mrr_at_5 | 0.3444 | 0.2732 - 0.4203 | 120 |
| hybrid_hops2_v3_h8 | mrr_at_10 | 0.3526 | 0.282 - 0.4273 | 120 |
| hybrid_hops2_v3_h8 | ndcg_at_10 | 0.4359 | 0.3451 - 0.5235 | 120 |
| hybrid_hops2_v3_h8 | context_precision_at_5 | 0.1183 | 0.095 - 0.1417 | 120 |
| hybrid_hops2_v3_h8 | context_recall | 0.7292 | 0.65 - 0.8042 | 120 |
| hybrid_hops2_v8_h8 | recall_at_5 | 0.5083 | 0.4167 - 0.6 | 120 |
| hybrid_hops2_v8_h8 | recall_at_10 | 0.5833 | 0.4917 - 0.675 | 120 |
| hybrid_hops2_v8_h8 | mrr_at_5 | 0.3356 | 0.2653 - 0.411 | 120 |
| hybrid_hops2_v8_h8 | mrr_at_10 | 0.3477 | 0.2779 - 0.422 | 120 |
| hybrid_hops2_v8_h8 | ndcg_at_10 | 0.4366 | 0.3493 - 0.525 | 120 |
| hybrid_hops2_v8_h8 | context_precision_at_5 | 0.115 | 0.09 - 0.14 | 120 |
| hybrid_hops2_v8_h8 | context_recall | 0.7292 | 0.65 - 0.8042 | 120 |
| hybrid_hops2_v5_h5 | recall_at_5 | 0.525 | 0.4333 - 0.6167 | 120 |
| hybrid_hops2_v5_h5 | recall_at_10 | 0.525 | 0.4333 - 0.6167 | 120 |
| hybrid_hops2_v5_h5 | mrr_at_5 | 0.3464 | 0.2735 - 0.4243 | 120 |
| hybrid_hops2_v5_h5 | mrr_at_10 | 0.3464 | 0.2735 - 0.4243 | 120 |
| hybrid_hops2_v5_h5 | ndcg_at_10 | 0.4186 | 0.3278 - 0.5116 | 120 |
| hybrid_hops2_v5_h5 | context_precision_at_5 | 0.12 | 0.095 - 0.145 | 120 |
| hybrid_hops2_v5_h5 | context_recall | 0.6708 | 0.5833 - 0.7542 | 120 |
| hybrid_hops2_v5_h10 | recall_at_5 | 0.5167 | 0.425 - 0.6083 | 120 |
| hybrid_hops2_v5_h10 | recall_at_10 | 0.6 | 0.5083 - 0.6917 | 120 |
| hybrid_hops2_v5_h10 | mrr_at_5 | 0.3431 | 0.2719 - 0.4206 | 120 |
| hybrid_hops2_v5_h10 | mrr_at_10 | 0.3556 | 0.284 - 0.4313 | 120 |
| hybrid_hops2_v5_h10 | ndcg_at_10 | 0.4459 | 0.3602 - 0.5374 | 120 |
| hybrid_hops2_v5_h10 | context_precision_at_5 | 0.1183 | 0.0933 - 0.1417 | 120 |
| hybrid_hops2_v5_h10 | context_recall | 0.7458 | 0.6708 - 0.8167 | 120 |

## Supported Vs Insufficient-Evidence Breakdown

| Scenario | Group | Records | Recall@5 | MRR@5 | Context Recall |
| --- | --- | ---: | ---: | ---: | ---: |
| vector_hops2_v5_h8 | supported | 100 | 0.57 | 0.3922 | 0.545 |
| vector_hops2_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_graph_disabled_hops2_v5_h8 | supported | 100 | 0.57 | 0.3922 | 0.545 |
| hybrid_graph_disabled_hops2_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| graph_hops1_v5_h8 | supported | 100 | 0.49 | 0.3652 | 0.48 |
| graph_hops1_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| graph_hops2_v5_h8 | supported | 100 | 0.49 | 0.3652 | 0.48 |
| graph_hops2_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| graph_hops3_v5_h8 | supported | 100 | 0.49 | 0.3652 | 0.48 |
| graph_hops3_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_hops1_v5_h8 | supported | 100 | 0.62 | 0.41 | 0.685 |
| hybrid_hops1_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v5_h8 | supported | 100 | 0.62 | 0.41 | 0.685 |
| hybrid_hops2_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_hops3_v5_h8 | supported | 100 | 0.62 | 0.41 | 0.685 |
| hybrid_hops3_v5_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v3_h8 | supported | 100 | 0.64 | 0.4133 | 0.675 |
| hybrid_hops2_v3_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v8_h8 | supported | 100 | 0.61 | 0.4027 | 0.675 |
| hybrid_hops2_v8_h8 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v5_h5 | supported | 100 | 0.63 | 0.4157 | 0.605 |
| hybrid_hops2_v5_h5 | insufficient_evidence | 20 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v5_h10 | supported | 100 | 0.62 | 0.4117 | 0.695 |
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

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8) while not always improving page-level Recall@5 (0.5167).

### hybrid_hops2_v5_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8) while not always improving page-level Recall@5 (0.5167).

### hybrid_hops3_v5_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8) while not always improving page-level Recall@5 (0.5167).

### hybrid_hops2_v3_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8) while not always improving page-level Recall@5 (0.5333).

### hybrid_hops2_v8_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8) while not always improving page-level Recall@5 (0.5083).

### hybrid_hops2_v5_h5

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.7917) while not always improving page-level Recall@5 (0.525).

### hybrid_hops2_v5_h10

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8083) while not always improving page-level Recall@5 (0.5167).
