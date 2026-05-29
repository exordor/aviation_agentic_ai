# Retrieval Ablation

- Run ID: `retrieval-ablation-20260529T232814Z`
- Questions: 120
- Supported labels: 100
- Insufficient-evidence labels: 20
- Scenarios: 12
- Scoring: layered retrieval and KG evidence metrics; no mixed overall score.

| Scenario | Mode | Recall@5 | MRR@5 | Context Precision@5 | KG coverage | Avg triples |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| vector_hops2_v5_h8 | vector | 0.475 | 0.3261 | 0.11 | 0.0 | 0.0 |
| hybrid_graph_disabled_hops2_v5_h8 | hybrid_graph_disabled | 0.475 | 0.3261 | 0.11 | 0.0 | 0.0 |
| graph_hops1_v5_h8 | graph | 0.4083 | 0.3043 | 0.0942 | 0.8 | 7.5833 |
| graph_hops2_v5_h8 | graph | 0.4083 | 0.3043 | 0.0942 | 0.8 | 7.5833 |
| graph_hops3_v5_h8 | graph | 0.4083 | 0.3043 | 0.0942 | 0.8 | 7.5833 |
| hybrid_hops1_v5_h8 | hybrid | 0.5083 | 0.34 | 0.1167 | 0.8 | 7.5833 |
| hybrid_hops2_v5_h8 | hybrid | 0.5083 | 0.34 | 0.1167 | 0.8 | 7.5833 |
| hybrid_hops3_v5_h8 | hybrid | 0.5083 | 0.34 | 0.1167 | 0.8 | 7.5833 |
| hybrid_hops2_v3_h8 | hybrid | 0.4583 | 0.3278 | 0.1694 | 0.8 | 7.5833 |
| hybrid_hops2_v8_h8 | hybrid | 0.5833 | 0.3472 | 0.0844 | 0.8 | 7.5833 |
| hybrid_hops2_v5_h5 | hybrid | 0.5167 | 0.3447 | 0.1183 | 0.7917 | 4.8 |
| hybrid_hops2_v5_h10 | hybrid | 0.5083 | 0.3414 | 0.1167 | 0.8083 | 9.4167 |

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

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8) while not always improving page-level Recall@5 (0.4583).

### hybrid_hops2_v8_h8

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8) while not always improving page-level Recall@5 (0.5833).

### hybrid_hops2_v5_h5

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.7917) while not always improving page-level Recall@5 (0.5167).

### hybrid_hops2_v5_h10

Hybrid RRF should be judged by retrieval and KG evidence separately; fusion can help evidence coverage (0.8083) while not always improving page-level Recall@5 (0.5083).
