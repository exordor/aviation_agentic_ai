# Retrieval Ablation

- Run ID: `retrieval-ablation-20260530T001948Z`
- Questions: 120
- Supported labels: 100
- Insufficient-evidence labels: 20
- Scenarios: 12
- Scoring: layered retrieval and KG evidence metrics; no mixed overall score.
- Confidence intervals: deterministic bootstrap 95% CIs over per-question metrics.

| Scenario | Mode | Recall@5 | Recall@10 | Precision@5 | MRR@5 | MRR@10 | NDCG@10 | Context Precision@5 | Context Recall | KG coverage | Avg triples |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vector_hops2_v5_h8 | vector | 0.475 | 0.475 | 0.11 | 0.3261 | 0.3261 | 0.3863 | 0.11 | 0.6208 | 0.0 | 0.0 |
<!-- vector_hops2_v5_h8 Recall@5 95% CI: 0.3917 - 0.5667 -->
| hybrid_graph_disabled_hops2_v5_h8 | hybrid_graph_disabled | 0.475 | 0.475 | 0.11 | 0.3261 | 0.3261 | 0.3863 | 0.11 | 0.6208 | 0.0 | 0.0 |
<!-- hybrid_graph_disabled_hops2_v5_h8 Recall@5 95% CI: 0.3917 - 0.5667 -->
| graph_hops1_v5_h8 | graph | 0.4083 | 0.4167 | 0.09 | 0.3043 | 0.3055 | 0.3503 | 0.0942 | 0.5667 | 0.8 | 7.5833 |
<!-- graph_hops1_v5_h8 Recall@5 95% CI: 0.3167 - 0.5 -->
| graph_hops2_v5_h8 | graph | 0.4083 | 0.4167 | 0.09 | 0.3043 | 0.3055 | 0.3503 | 0.0942 | 0.5667 | 0.8 | 7.5833 |
<!-- graph_hops2_v5_h8 Recall@5 95% CI: 0.3167 - 0.5 -->
| graph_hops3_v5_h8 | graph | 0.4083 | 0.4167 | 0.09 | 0.3043 | 0.3055 | 0.3503 | 0.0942 | 0.5667 | 0.8 | 7.5833 |
<!-- graph_hops3_v5_h8 Recall@5 95% CI: 0.3167 - 0.5 -->
| hybrid_hops1_v5_h8 | hybrid | 0.5083 | 0.5917 | 0.1167 | 0.34 | 0.3529 | 0.4425 | 0.1167 | 0.7375 | 0.8 | 7.5833 |
<!-- hybrid_hops1_v5_h8 Recall@5 95% CI: 0.4167 - 0.6 -->
| hybrid_hops2_v5_h8 | hybrid | 0.5083 | 0.5917 | 0.1167 | 0.34 | 0.3529 | 0.4425 | 0.1167 | 0.7375 | 0.8 | 7.5833 |
<!-- hybrid_hops2_v5_h8 Recall@5 95% CI: 0.4167 - 0.6 -->
| hybrid_hops3_v5_h8 | hybrid | 0.5083 | 0.5917 | 0.1167 | 0.34 | 0.3529 | 0.4425 | 0.1167 | 0.7375 | 0.8 | 7.5833 |
<!-- hybrid_hops3_v5_h8 Recall@5 95% CI: 0.4167 - 0.6 -->
| hybrid_hops2_v3_h8 | hybrid | 0.525 | 0.575 | 0.1167 | 0.3428 | 0.3509 | 0.4326 | 0.1167 | 0.7208 | 0.8 | 7.5833 |
<!-- hybrid_hops2_v3_h8 Recall@5 95% CI: 0.4333 - 0.6167 -->
| hybrid_hops2_v8_h8 | hybrid | 0.5 | 0.5833 | 0.1133 | 0.3339 | 0.3472 | 0.4361 | 0.1133 | 0.7292 | 0.8 | 7.5833 |
<!-- hybrid_hops2_v8_h8 Recall@5 95% CI: 0.4167 - 0.5917 -->
| hybrid_hops2_v5_h5 | hybrid | 0.5167 | 0.5167 | 0.1183 | 0.3447 | 0.3447 | 0.4154 | 0.1183 | 0.6625 | 0.7917 | 4.8 |
<!-- hybrid_hops2_v5_h5 Recall@5 95% CI: 0.425 - 0.6083 -->
| hybrid_hops2_v5_h10 | hybrid | 0.5083 | 0.6 | 0.1167 | 0.3414 | 0.3552 | 0.4454 | 0.1167 | 0.7458 | 0.8083 | 9.4167 |
<!-- hybrid_hops2_v5_h10 Recall@5 95% CI: 0.4167 - 0.6 -->

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
