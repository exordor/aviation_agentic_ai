# Retrieval Ablation

- Run ID: `retrieval-ablation-20260529T235409Z`
- Questions: 35
- Supported labels: 30
- Insufficient-evidence labels: 5
- Scenarios: 12
- Scoring: layered retrieval and KG evidence metrics; no mixed overall score.

| Scenario | Mode | Recall@5 | Recall@10 | Precision@5 | MRR@5 | MRR@10 | NDCG@10 | Context Precision@5 | Context Recall | KG coverage | Avg triples |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vector_hops2_v5_h8 | vector | 0.6857 | 0.6857 | 0.1771 | 0.4714 | 0.4714 | 0.6261 | 0.1771 | 0.8286 | 0.0 | 0.0 |
| hybrid_graph_disabled_hops2_v5_h8 | hybrid_graph_disabled | 0.6857 | 0.6857 | 0.1771 | 0.4714 | 0.4714 | 0.6261 | 0.1771 | 0.8286 | 0.0 | 0.0 |
| graph_hops1_v5_h8 | graph | 0.5143 | 0.5143 | 0.1371 | 0.3929 | 0.3929 | 0.5026 | 0.1543 | 0.6571 | 0.8286 | 7.5429 |
| graph_hops2_v5_h8 | graph | 0.5143 | 0.5143 | 0.1371 | 0.3929 | 0.3929 | 0.5026 | 0.1543 | 0.6571 | 0.8286 | 7.5429 |
| graph_hops3_v5_h8 | graph | 0.5143 | 0.5143 | 0.1371 | 0.3929 | 0.3929 | 0.5026 | 0.1543 | 0.6571 | 0.8286 | 7.5429 |
| hybrid_hops1_v5_h8 | hybrid | 0.6286 | 0.6857 | 0.1543 | 0.4471 | 0.4567 | 0.6156 | 0.1543 | 0.8286 | 0.8286 | 7.5429 |
| hybrid_hops2_v5_h8 | hybrid | 0.6286 | 0.6857 | 0.1543 | 0.4471 | 0.4567 | 0.6156 | 0.1543 | 0.8286 | 0.8286 | 7.5429 |
| hybrid_hops3_v5_h8 | hybrid | 0.6286 | 0.6857 | 0.1543 | 0.4471 | 0.4567 | 0.6156 | 0.1543 | 0.8286 | 0.8286 | 7.5429 |
| hybrid_hops2_v3_h8 | hybrid | 0.6857 | 0.6857 | 0.16 | 0.4686 | 0.4686 | 0.6113 | 0.1629 | 0.8286 | 0.8286 | 7.5429 |
| hybrid_hops2_v8_h8 | hybrid | 0.5714 | 0.6857 | 0.1486 | 0.4295 | 0.4479 | 0.6161 | 0.1486 | 0.8286 | 0.8286 | 7.5429 |
| hybrid_hops2_v5_h5 | hybrid | 0.6571 | 0.6571 | 0.1543 | 0.44 | 0.44 | 0.5536 | 0.1543 | 0.8 | 0.8 | 4.7143 |
| hybrid_hops2_v5_h10 | hybrid | 0.6571 | 0.6857 | 0.16 | 0.4652 | 0.47 | 0.6443 | 0.16 | 0.8286 | 0.8286 | 9.2857 |

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
