# Graph Traversal Ablation

- Run ID: `graph-traversal-ablation-20260529T235612Z`
- Questions: 35
- Scenarios: 8
- Scoring: retrieval, KG evidence, and graph path metrics are kept separate.

| Scenario | Recall@5 | Recall@10 | MRR@5 | NDCG@10 | Context Precision@5 | KG coverage | Path coverage | Path Recall@5 | Path Precision@5 | Supporting path rate | Irrelevant path rate | Key entity coverage | Relation coverage | Failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vector-only | 0.6857 | 0.6857 | 0.4714 | 0.6261 | 0.1771 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 35 |
| lexical graph search | 0.5143 | 0.5143 | 0.3929 | 0.5026 | 0.1543 | 0.8286 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.6 | 0.625 | 18 |
| traversal graph search with 1 hop | 0.1714 | 0.2 | 0.1714 | 0.181 | 0.0638 | 0.7714 | 0.9429 | 0.8571 | 0.7 | 0.7096 | 0.2333 | 0.4833 | 0.75 | 30 |
| traversal graph search with 2 hops | 0.1714 | 0.2 | 0.1714 | 0.1804 | 0.0419 | 0.7429 | 0.9429 | 0.8571 | 0.7543 | 0.722 | 0.2209 | 0.4929 | 0.75 | 30 |
| traversal graph search with 3 hops | 0.1714 | 0.2 | 0.15 | 0.1642 | 0.0381 | 0.7429 | 0.9429 | 0.8571 | 0.7657 | 0.7302 | 0.2127 | 0.5024 | 0.75 | 30 |
| hybrid vector + lexical graph | 0.6286 | 0.6857 | 0.4471 | 0.6156 | 0.1543 | 0.8286 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.6 | 0.625 | 14 |
| hybrid vector + traversal graph | 0.6571 | 0.7143 | 0.3557 | 0.5353 | 0.16 | 0.7429 | 0.9429 | 0.8571 | 0.7543 | 0.722 | 0.2209 | 0.4929 | 0.75 | 18 |
| hybrid vector + traversal graph, vector-first guarded | 0.6571 | 0.7143 | 0.4557 | 0.6204 | 0.16 | 0.7429 | 0.9429 | 0.8571 | 0.7543 | 0.722 | 0.2209 | 0.4929 | 0.75 | 18 |

## Notes

Lexical graph search remains the baseline. Traversal metrics describe whether bounded KG paths were returned and whether they cover named entities or relation intent; they do not imply better retrieval unless Recall@5/MRR@5 support that.

High path coverage with low standalone Recall@5 usually means traversal can find connected KG paths, but the chunks attached to those paths are not necessarily the gold evidence chunks. This can happen through seed linking errors, generic seed nodes, low-value predicates, sparse KG coverage for the question, or graph fusion dilution when graph chunks displace stronger vector hits.

Path Recall@5, Path Precision@5, Supporting Path Rate, and Irrelevant Path Rate are deterministic heuristics based on key-entity, relation-intent, source-page, and gold-chunk overlap. They require manual path relevance review before being treated as semantic path-correctness evidence.

## Failure Cases

### vector_only

- `exp-001-atmosphere-envelope`: missing_kg_key_entity_evidence; kg_sparse_for_question
- `exp-002-atmosphere-composition`: missing_kg_key_entity_evidence; kg_sparse_for_question
- `exp-003-air-fluid`: missing_kg_key_entity_evidence; kg_sparse_for_question
- `exp-004-viscosity-definition`: missing_kg_key_entity_evidence; kg_sparse_for_question
- `exp-005-air-low-viscosity`: missing_kg_key_entity_evidence; kg_sparse_for_question
- `exp-006-friction-wing-surface`: missing_kg_key_entity_evidence; low_value_predicate, kg_sparse_for_question
- `exp-007-boundary-layer`: missing_kg_key_entity_evidence; kg_sparse_for_question
- `exp-008-pressure-definition`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; kg_sparse_for_question
- `exp-009-atmospheric-pressure`: missing_kg_key_entity_evidence; kg_sparse_for_question
- `exp-010-standard-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; kg_sparse_for_question

### lexical_graph_search

- `exp-008-pressure-definition`: missed_gold_evidence_at_5
- `exp-010-standard-pressure`: missed_gold_evidence_at_5
- `exp-011-pressure-altitude-trend`: missed_gold_evidence_at_5
- `exp-012-nonstandard-atmosphere`: missed_gold_evidence_at_5
- `exp-013-pressure-altitude`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; kg_sparse_for_question
- `exp-017-temperature-density`: missed_gold_evidence_at_5
- `exp-019-lift-theories`: low_value_predicate
- `exp-021-newton-second`: missed_gold_evidence_at_5
- `exp-022-newton-third`: missed_gold_evidence_at_5
- `exp-023-bernoulli`: missed_gold_evidence_at_5

### traversal_graph_1_hop

- `exp-001-atmosphere-envelope`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-002-atmosphere-composition`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-003-air-fluid`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-004-viscosity-definition`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-005-air-low-viscosity`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-008-pressure-definition`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-009-atmospheric-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; path_found_but_wrong_chunk, kg_sparse_for_question
- `exp-010-standard-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; path_found_but_wrong_chunk, kg_sparse_for_question
- `exp-011-pressure-altitude-trend`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-012-nonstandard-atmosphere`: missed_gold_evidence_at_5; path_found_but_wrong_chunk

### traversal_graph_2_hop

- `exp-001-atmosphere-envelope`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-002-atmosphere-composition`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-003-air-fluid`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-004-viscosity-definition`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-005-air-low-viscosity`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-008-pressure-definition`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-009-atmospheric-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; path_found_but_wrong_chunk, kg_sparse_for_question
- `exp-010-standard-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; path_found_but_wrong_chunk, kg_sparse_for_question
- `exp-011-pressure-altitude-trend`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-012-nonstandard-atmosphere`: missed_gold_evidence_at_5; path_found_but_wrong_chunk

### traversal_graph_3_hop

- `exp-001-atmosphere-envelope`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-002-atmosphere-composition`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-003-air-fluid`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-004-viscosity-definition`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-005-air-low-viscosity`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-008-pressure-definition`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-009-atmospheric-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; path_found_but_wrong_chunk, kg_sparse_for_question
- `exp-010-standard-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; path_found_but_wrong_chunk, kg_sparse_for_question
- `exp-011-pressure-altitude-trend`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `exp-012-nonstandard-atmosphere`: missed_gold_evidence_at_5; path_found_but_wrong_chunk

### hybrid_vector_lexical_graph

- `exp-008-pressure-definition`: missed_gold_evidence_at_5
- `exp-010-standard-pressure`: missed_gold_evidence_at_5
- `exp-011-pressure-altitude-trend`: missed_gold_evidence_at_5
- `exp-012-nonstandard-atmosphere`: missed_gold_evidence_at_5
- `exp-013-pressure-altitude`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; kg_sparse_for_question
- `exp-019-lift-theories`: low_value_predicate
- `exp-022-newton-third`: missed_gold_evidence_at_5
- `exp-027-efficient-airfoil`: missed_gold_evidence_at_5
- `exp-030-pressure-distribution`: missed_gold_evidence_at_5
- `exp-031-no-answer-vspeeds`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; kg_sparse_for_question

### hybrid_vector_traversal_graph

- `exp-005-air-low-viscosity`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `exp-008-pressure-definition`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `exp-009-atmospheric-pressure`: missing_kg_key_entity_evidence; kg_sparse_for_question
- `exp-010-standard-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; path_found_but_wrong_chunk, graph_fusion_dilution, kg_sparse_for_question
- `exp-012-nonstandard-atmosphere`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `exp-014-density-altitude`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `exp-019-lift-theories`: generic_seed_node, low_value_predicate
- `exp-020-newton-first`: generic_seed_node
- `exp-021-newton-second`: generic_seed_node
- `exp-023-bernoulli`: low_value_predicate

### hybrid_vector_traversal_guarded

- `exp-005-air-low-viscosity`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `exp-008-pressure-definition`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `exp-009-atmospheric-pressure`: missing_kg_key_entity_evidence; kg_sparse_for_question
- `exp-010-standard-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; path_found_but_wrong_chunk, graph_fusion_dilution, kg_sparse_for_question
- `exp-012-nonstandard-atmosphere`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `exp-014-density-altitude`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `exp-019-lift-theories`: generic_seed_node, low_value_predicate
- `exp-020-newton-first`: generic_seed_node
- `exp-021-newton-second`: generic_seed_node
- `exp-023-bernoulli`: low_value_predicate
