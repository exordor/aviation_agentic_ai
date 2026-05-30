# Retrieval Ablation

- Run ID: `retrieval-ablation-20260530T100132Z`
- Questions: 35
- Supported labels: 30
- Insufficient-evidence labels: 5
- Scenarios: 12
- Scoring: layered retrieval and KG evidence metrics; no mixed overall score.
- Confidence intervals: deterministic bootstrap 95% CIs over per-question metrics.

| Scenario | Mode | Recall@5 | Recall@10 | Precision@5 | MRR@5 | MRR@10 | NDCG@10 | Context Precision@5 | Context Recall | Supported Recall@5 | KG coverage | Avg triples |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vector_hops2_v5_h8 | vector | 0.6857 | 0.6857 | 0.1771 | 0.4714 | 0.4714 | 0.6261 | 0.1771 | 0.8286 | 0.8 | 0.0 | 0.0 |
| hybrid_graph_disabled_hops2_v5_h8 | hybrid_graph_disabled | 0.6857 | 0.6857 | 0.1771 | 0.4714 | 0.4714 | 0.6261 | 0.1771 | 0.8286 | 0.8 | 0.0 | 0.0 |
| graph_hops1_v5_h8 | graph | 0.5143 | 0.5143 | 0.1371 | 0.3929 | 0.3929 | 0.5026 | 0.1543 | 0.6571 | 0.6 | 0.8286 | 7.5429 |
| graph_hops2_v5_h8 | graph | 0.5143 | 0.5143 | 0.1371 | 0.3929 | 0.3929 | 0.5026 | 0.1543 | 0.6571 | 0.6 | 0.8286 | 7.5429 |
| graph_hops3_v5_h8 | graph | 0.5143 | 0.5143 | 0.1371 | 0.3929 | 0.3929 | 0.5026 | 0.1543 | 0.6571 | 0.6 | 0.8286 | 7.5429 |
| hybrid_hops1_v5_h8 | hybrid | 0.6286 | 0.6857 | 0.1543 | 0.4471 | 0.4567 | 0.6156 | 0.1543 | 0.8286 | 0.7333 | 0.8286 | 7.5429 |
| hybrid_hops2_v5_h8 | hybrid | 0.6286 | 0.6857 | 0.1543 | 0.4471 | 0.4567 | 0.6156 | 0.1543 | 0.8286 | 0.7333 | 0.8286 | 7.5429 |
| hybrid_hops3_v5_h8 | hybrid | 0.6286 | 0.6857 | 0.1543 | 0.4471 | 0.4567 | 0.6156 | 0.1543 | 0.8286 | 0.7333 | 0.8286 | 7.5429 |
| hybrid_hops2_v3_h8 | hybrid | 0.6857 | 0.6857 | 0.16 | 0.4686 | 0.4686 | 0.6113 | 0.1629 | 0.8286 | 0.8 | 0.8286 | 7.5429 |
| hybrid_hops2_v8_h8 | hybrid | 0.5714 | 0.6857 | 0.1486 | 0.4295 | 0.4479 | 0.6161 | 0.1486 | 0.8286 | 0.6667 | 0.8286 | 7.5429 |
| hybrid_hops2_v5_h5 | hybrid | 0.6571 | 0.6571 | 0.1543 | 0.44 | 0.44 | 0.5536 | 0.1543 | 0.8 | 0.7667 | 0.8 | 4.7143 |
| hybrid_hops2_v5_h10 | hybrid | 0.6571 | 0.6857 | 0.16 | 0.4652 | 0.47 | 0.6443 | 0.16 | 0.8286 | 0.7667 | 0.8286 | 9.2857 |

## Confidence Intervals

| Scenario | Metric | Mean | 95% CI | n |
| --- | --- | ---: | --- | ---: |
| vector_hops2_v5_h8 | recall_at_5 | 0.6857 | 0.5429 - 0.8286 | 35 |
| vector_hops2_v5_h8 | recall_at_10 | 0.6857 | 0.5429 - 0.8286 | 35 |
| vector_hops2_v5_h8 | mrr_at_5 | 0.4714 | 0.3333 - 0.6071 | 35 |
| vector_hops2_v5_h8 | mrr_at_10 | 0.4714 | 0.3333 - 0.6071 | 35 |
| vector_hops2_v5_h8 | ndcg_at_10 | 0.6261 | 0.4482 - 0.8109 | 35 |
| vector_hops2_v5_h8 | context_precision_at_5 | 0.1771 | 0.1314 - 0.2286 | 35 |
| vector_hops2_v5_h8 | context_recall | 0.8286 | 0.7143 - 0.9429 | 35 |
| hybrid_graph_disabled_hops2_v5_h8 | recall_at_5 | 0.6857 | 0.5429 - 0.8286 | 35 |
| hybrid_graph_disabled_hops2_v5_h8 | recall_at_10 | 0.6857 | 0.5429 - 0.8286 | 35 |
| hybrid_graph_disabled_hops2_v5_h8 | mrr_at_5 | 0.4714 | 0.3333 - 0.6071 | 35 |
| hybrid_graph_disabled_hops2_v5_h8 | mrr_at_10 | 0.4714 | 0.3333 - 0.6071 | 35 |
| hybrid_graph_disabled_hops2_v5_h8 | ndcg_at_10 | 0.6261 | 0.4482 - 0.8109 | 35 |
| hybrid_graph_disabled_hops2_v5_h8 | context_precision_at_5 | 0.1771 | 0.1314 - 0.2286 | 35 |
| hybrid_graph_disabled_hops2_v5_h8 | context_recall | 0.8286 | 0.7143 - 0.9429 | 35 |
| graph_hops1_v5_h8 | recall_at_5 | 0.5143 | 0.3714 - 0.6857 | 35 |
| graph_hops1_v5_h8 | recall_at_10 | 0.5143 | 0.3714 - 0.6857 | 35 |
| graph_hops1_v5_h8 | mrr_at_5 | 0.3929 | 0.25 - 0.5429 | 35 |
| graph_hops1_v5_h8 | mrr_at_10 | 0.3929 | 0.25 - 0.5429 | 35 |
| graph_hops1_v5_h8 | ndcg_at_10 | 0.5026 | 0.3313 - 0.6811 | 35 |
| graph_hops1_v5_h8 | context_precision_at_5 | 0.1543 | 0.1033 - 0.2138 | 35 |
| graph_hops1_v5_h8 | context_recall | 0.6571 | 0.5143 - 0.8 | 35 |
| graph_hops2_v5_h8 | recall_at_5 | 0.5143 | 0.3714 - 0.6857 | 35 |
| graph_hops2_v5_h8 | recall_at_10 | 0.5143 | 0.3714 - 0.6857 | 35 |
| graph_hops2_v5_h8 | mrr_at_5 | 0.3929 | 0.25 - 0.5429 | 35 |
| graph_hops2_v5_h8 | mrr_at_10 | 0.3929 | 0.25 - 0.5429 | 35 |
| graph_hops2_v5_h8 | ndcg_at_10 | 0.5026 | 0.3313 - 0.6811 | 35 |
| graph_hops2_v5_h8 | context_precision_at_5 | 0.1543 | 0.1033 - 0.2138 | 35 |
| graph_hops2_v5_h8 | context_recall | 0.6571 | 0.5143 - 0.8 | 35 |
| graph_hops3_v5_h8 | recall_at_5 | 0.5143 | 0.3714 - 0.6857 | 35 |
| graph_hops3_v5_h8 | recall_at_10 | 0.5143 | 0.3714 - 0.6857 | 35 |
| graph_hops3_v5_h8 | mrr_at_5 | 0.3929 | 0.25 - 0.5429 | 35 |
| graph_hops3_v5_h8 | mrr_at_10 | 0.3929 | 0.25 - 0.5429 | 35 |
| graph_hops3_v5_h8 | ndcg_at_10 | 0.5026 | 0.3313 - 0.6811 | 35 |
| graph_hops3_v5_h8 | context_precision_at_5 | 0.1543 | 0.1033 - 0.2138 | 35 |
| graph_hops3_v5_h8 | context_recall | 0.6571 | 0.5143 - 0.8 | 35 |
| hybrid_hops1_v5_h8 | recall_at_5 | 0.6286 | 0.4857 - 0.7714 | 35 |
| hybrid_hops1_v5_h8 | recall_at_10 | 0.6857 | 0.5429 - 0.8286 | 35 |
| hybrid_hops1_v5_h8 | mrr_at_5 | 0.4471 | 0.3114 - 0.5914 | 35 |
| hybrid_hops1_v5_h8 | mrr_at_10 | 0.4567 | 0.319 - 0.6 | 35 |
| hybrid_hops1_v5_h8 | ndcg_at_10 | 0.6156 | 0.4288 - 0.8042 | 35 |
| hybrid_hops1_v5_h8 | context_precision_at_5 | 0.1543 | 0.1086 - 0.2 | 35 |
| hybrid_hops1_v5_h8 | context_recall | 0.8286 | 0.7143 - 0.9429 | 35 |
| hybrid_hops2_v5_h8 | recall_at_5 | 0.6286 | 0.4857 - 0.7714 | 35 |
| hybrid_hops2_v5_h8 | recall_at_10 | 0.6857 | 0.5429 - 0.8286 | 35 |
| hybrid_hops2_v5_h8 | mrr_at_5 | 0.4471 | 0.3114 - 0.5914 | 35 |
| hybrid_hops2_v5_h8 | mrr_at_10 | 0.4567 | 0.319 - 0.6 | 35 |
| hybrid_hops2_v5_h8 | ndcg_at_10 | 0.6156 | 0.4288 - 0.8042 | 35 |
| hybrid_hops2_v5_h8 | context_precision_at_5 | 0.1543 | 0.1086 - 0.2 | 35 |
| hybrid_hops2_v5_h8 | context_recall | 0.8286 | 0.7143 - 0.9429 | 35 |
| hybrid_hops3_v5_h8 | recall_at_5 | 0.6286 | 0.4857 - 0.7714 | 35 |
| hybrid_hops3_v5_h8 | recall_at_10 | 0.6857 | 0.5429 - 0.8286 | 35 |
| hybrid_hops3_v5_h8 | mrr_at_5 | 0.4471 | 0.3114 - 0.5914 | 35 |
| hybrid_hops3_v5_h8 | mrr_at_10 | 0.4567 | 0.319 - 0.6 | 35 |
| hybrid_hops3_v5_h8 | ndcg_at_10 | 0.6156 | 0.4288 - 0.8042 | 35 |
| hybrid_hops3_v5_h8 | context_precision_at_5 | 0.1543 | 0.1086 - 0.2 | 35 |
| hybrid_hops3_v5_h8 | context_recall | 0.8286 | 0.7143 - 0.9429 | 35 |
| hybrid_hops2_v3_h8 | recall_at_5 | 0.6857 | 0.5429 - 0.8286 | 35 |
| hybrid_hops2_v3_h8 | recall_at_10 | 0.6857 | 0.5429 - 0.8286 | 35 |
| hybrid_hops2_v3_h8 | mrr_at_5 | 0.4686 | 0.3343 - 0.6057 | 35 |
| hybrid_hops2_v3_h8 | mrr_at_10 | 0.4686 | 0.3343 - 0.6057 | 35 |
| hybrid_hops2_v3_h8 | ndcg_at_10 | 0.6113 | 0.431 - 0.8057 | 35 |
| hybrid_hops2_v3_h8 | context_precision_at_5 | 0.1629 | 0.12 - 0.2057 | 35 |
| hybrid_hops2_v3_h8 | context_recall | 0.8286 | 0.7143 - 0.9429 | 35 |
| hybrid_hops2_v8_h8 | recall_at_5 | 0.5714 | 0.4286 - 0.7143 | 35 |
| hybrid_hops2_v8_h8 | recall_at_10 | 0.6857 | 0.5429 - 0.8286 | 35 |
| hybrid_hops2_v8_h8 | mrr_at_5 | 0.4295 | 0.2914 - 0.581 | 35 |
| hybrid_hops2_v8_h8 | mrr_at_10 | 0.4479 | 0.3132 - 0.5905 | 35 |
| hybrid_hops2_v8_h8 | ndcg_at_10 | 0.6161 | 0.431 - 0.8145 | 35 |
| hybrid_hops2_v8_h8 | context_precision_at_5 | 0.1486 | 0.0971 - 0.2 | 35 |
| hybrid_hops2_v8_h8 | context_recall | 0.8286 | 0.7143 - 0.9429 | 35 |
| hybrid_hops2_v5_h5 | recall_at_5 | 0.6571 | 0.5143 - 0.8 | 35 |
| hybrid_hops2_v5_h5 | recall_at_10 | 0.6571 | 0.5143 - 0.8 | 35 |
| hybrid_hops2_v5_h5 | mrr_at_5 | 0.44 | 0.31 - 0.5771 | 35 |
| hybrid_hops2_v5_h5 | mrr_at_10 | 0.44 | 0.31 - 0.5771 | 35 |
| hybrid_hops2_v5_h5 | ndcg_at_10 | 0.5536 | 0.3876 - 0.7225 | 35 |
| hybrid_hops2_v5_h5 | context_precision_at_5 | 0.1543 | 0.1086 - 0.2 | 35 |
| hybrid_hops2_v5_h5 | context_recall | 0.8 | 0.6571 - 0.9143 | 35 |
| hybrid_hops2_v5_h10 | recall_at_5 | 0.6571 | 0.5143 - 0.8 | 35 |
| hybrid_hops2_v5_h10 | recall_at_10 | 0.6857 | 0.5429 - 0.8286 | 35 |
| hybrid_hops2_v5_h10 | mrr_at_5 | 0.4652 | 0.3352 - 0.6071 | 35 |
| hybrid_hops2_v5_h10 | mrr_at_10 | 0.47 | 0.3367 - 0.6114 | 35 |
| hybrid_hops2_v5_h10 | ndcg_at_10 | 0.6443 | 0.4542 - 0.8374 | 35 |
| hybrid_hops2_v5_h10 | context_precision_at_5 | 0.16 | 0.1143 - 0.2057 | 35 |
| hybrid_hops2_v5_h10 | context_recall | 0.8286 | 0.7143 - 0.9429 | 35 |

## Supported Vs Insufficient-Evidence Breakdown

| Scenario | Group | Records | Recall@5 | MRR@5 | Context Recall |
| --- | --- | ---: | ---: | ---: | ---: |
| vector_hops2_v5_h8 | supported | 30 | 0.8 | 0.55 | 0.8 |
| vector_hops2_v5_h8 | insufficient_evidence | 5 | 0.0 | 0.0 | 1.0 |
| hybrid_graph_disabled_hops2_v5_h8 | supported | 30 | 0.8 | 0.55 | 0.8 |
| hybrid_graph_disabled_hops2_v5_h8 | insufficient_evidence | 5 | 0.0 | 0.0 | 1.0 |
| graph_hops1_v5_h8 | supported | 30 | 0.6 | 0.4583 | 0.6 |
| graph_hops1_v5_h8 | insufficient_evidence | 5 | 0.0 | 0.0 | 1.0 |
| graph_hops2_v5_h8 | supported | 30 | 0.6 | 0.4583 | 0.6 |
| graph_hops2_v5_h8 | insufficient_evidence | 5 | 0.0 | 0.0 | 1.0 |
| graph_hops3_v5_h8 | supported | 30 | 0.6 | 0.4583 | 0.6 |
| graph_hops3_v5_h8 | insufficient_evidence | 5 | 0.0 | 0.0 | 1.0 |
| hybrid_hops1_v5_h8 | supported | 30 | 0.7333 | 0.5217 | 0.8 |
| hybrid_hops1_v5_h8 | insufficient_evidence | 5 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v5_h8 | supported | 30 | 0.7333 | 0.5217 | 0.8 |
| hybrid_hops2_v5_h8 | insufficient_evidence | 5 | 0.0 | 0.0 | 1.0 |
| hybrid_hops3_v5_h8 | supported | 30 | 0.7333 | 0.5217 | 0.8 |
| hybrid_hops3_v5_h8 | insufficient_evidence | 5 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v3_h8 | supported | 30 | 0.8 | 0.5467 | 0.8 |
| hybrid_hops2_v3_h8 | insufficient_evidence | 5 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v8_h8 | supported | 30 | 0.6667 | 0.5011 | 0.8 |
| hybrid_hops2_v8_h8 | insufficient_evidence | 5 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v5_h5 | supported | 30 | 0.7667 | 0.5133 | 0.7667 |
| hybrid_hops2_v5_h5 | insufficient_evidence | 5 | 0.0 | 0.0 | 1.0 |
| hybrid_hops2_v5_h10 | supported | 30 | 0.7667 | 0.5428 | 0.8 |
| hybrid_hops2_v5_h10 | insufficient_evidence | 5 | 0.0 | 0.0 | 1.0 |

## Interpretation

### vector_hops2_v5_h8

Vector retrieval measures whether semantic text search alone recovers the gold chunk/span/page evidence.

### hybrid_graph_disabled_hops2_v5_h8

This is the hybrid ablation with graph evidence disabled; it should match vector retrieval behavior while preserving the hybrid experiment label.

### graph_hops1_v5_h8

Graph retrieval is valuable when KG triples cover key entities, even if coarse Recall@5 is 0.5143 and evidence coverage is 0.8286.

### graph_hops2_v5_h8

Graph retrieval is valuable when KG triples cover key entities, even if coarse Recall@5 is 0.5143 and evidence coverage is 0.8286.

### graph_hops3_v5_h8

Graph retrieval is valuable when KG triples cover key entities, even if coarse Recall@5 is 0.5143 and evidence coverage is 0.8286.

### hybrid_hops1_v5_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8286) while not always improving page-level Recall@5 (0.6286).

### hybrid_hops2_v5_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8286) while not always improving page-level Recall@5 (0.6286).

### hybrid_hops3_v5_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8286) while not always improving page-level Recall@5 (0.6286).

### hybrid_hops2_v3_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8286) while not always improving page-level Recall@5 (0.6857).

### hybrid_hops2_v8_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8286) while not always improving page-level Recall@5 (0.5714).

### hybrid_hops2_v5_h5

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8) while not always improving page-level Recall@5 (0.6571).

### hybrid_hops2_v5_h10

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8286) while not always improving page-level Recall@5 (0.6571).
