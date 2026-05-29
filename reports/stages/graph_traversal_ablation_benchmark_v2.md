# Graph Traversal Ablation

- Run ID: `graph-traversal-ablation-20260529T235703Z`
- Questions: 120
- Scenarios: 8
- Scoring: retrieval, KG evidence, and graph path metrics are kept separate.

| Scenario | Recall@5 | Recall@10 | MRR@5 | NDCG@10 | Context Precision@5 | KG coverage | Path coverage | Path Recall@5 | Path Precision@5 | Supporting path rate | Irrelevant path rate | Key entity coverage | Relation coverage | Failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vector-only | 0.475 | 0.475 | 0.3261 | 0.3863 | 0.11 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 120 |
| lexical graph search | 0.4083 | 0.4167 | 0.3043 | 0.3503 | 0.0942 | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.6438 | 0.5652 | 74 |
| traversal graph search with 1 hop | 0.1333 | 0.1333 | 0.1111 | 0.1245 | 0.055 | 0.65 | 0.75 | 0.6583 | 0.6492 | 0.6309 | 0.1191 | 0.4389 | 0.2174 | 105 |
| traversal graph search with 2 hops | 0.1333 | 0.1333 | 0.1083 | 0.1273 | 0.0387 | 0.6583 | 0.75 | 0.6583 | 0.6522 | 0.6321 | 0.1179 | 0.45 | 0.2174 | 104 |
| traversal graph search with 3 hops | 0.1333 | 0.1333 | 0.1083 | 0.1273 | 0.0387 | 0.6583 | 0.75 | 0.6583 | 0.6529 | 0.6328 | 0.1172 | 0.45 | 0.2174 | 104 |
| hybrid vector + lexical graph | 0.5083 | 0.5917 | 0.34 | 0.4425 | 0.1167 | 0.8 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.6438 | 0.5652 | 63 |
| hybrid vector + traversal graph | 0.4417 | 0.475 | 0.2867 | 0.3672 | 0.105 | 0.6583 | 0.75 | 0.6583 | 0.6522 | 0.6321 | 0.1179 | 0.45 | 0.2174 | 88 |
| hybrid vector + traversal graph, vector-first guarded | 0.4583 | 0.475 | 0.3239 | 0.391 | 0.1083 | 0.6583 | 0.75 | 0.6583 | 0.6522 | 0.6321 | 0.1179 | 0.45 | 0.2174 | 87 |

## Notes

Lexical graph search remains the baseline. Traversal metrics describe whether bounded KG paths were returned and whether they cover named entities or relation intent; they do not imply better retrieval unless Recall@5/MRR@5 support that.

High path coverage with low standalone Recall@5 usually means traversal can find connected KG paths, but the chunks attached to those paths are not necessarily the gold evidence chunks. This can happen through seed linking errors, generic seed nodes, low-value predicates, sparse KG coverage for the question, or graph fusion dilution when graph chunks displace stronger vector hits.

Path Recall@5, Path Precision@5, Supporting Path Rate, and Irrelevant Path Rate are deterministic heuristics based on key-entity, relation-intent, source-page, and gold-chunk overlap. They require manual path relevance review before being treated as semantic path-correctness evidence.

## Failure Cases

### vector_only

- `bv2-sf-001`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; kg_sparse_for_question
- `bv2-sf-002`: missing_kg_key_entity_evidence; kg_sparse_for_question
- `bv2-sf-003`: missing_kg_key_entity_evidence; kg_sparse_for_question
- `bv2-sf-004`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; kg_sparse_for_question
- `bv2-sf-005`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; low_value_predicate, kg_sparse_for_question
- `bv2-sf-006`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; kg_sparse_for_question
- `bv2-sf-007`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; kg_sparse_for_question
- `bv2-sf-008`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; kg_sparse_for_question
- `bv2-sf-009`: missing_kg_key_entity_evidence; kg_sparse_for_question
- `bv2-sf-010`: missing_kg_key_entity_evidence; kg_sparse_for_question

### lexical_graph_search

- `bv2-sf-005`: missed_gold_evidence_at_5; low_value_predicate
- `bv2-sf-006`: missed_gold_evidence_at_5
- `bv2-sf-007`: missed_gold_evidence_at_5
- `bv2-sf-011`: missed_gold_evidence_at_5
- `bv2-sf-012`: low_value_predicate
- `bv2-sf-013`: missed_gold_evidence_at_5
- `bv2-sf-014`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; kg_sparse_for_question
- `bv2-sf-015`: missed_gold_evidence_at_5
- `bv2-sf-020`: missed_gold_evidence_at_5
- `bv2-sf-021`: missed_gold_evidence_at_5

### traversal_graph_1_hop

- `bv2-sf-001`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-002`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-004`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-005`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, low_value_predicate
- `bv2-sf-006`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-007`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-008`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-009`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-011`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, low_value_predicate
- `bv2-sf-012`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, low_value_predicate

### traversal_graph_2_hop

- `bv2-sf-001`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-002`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-004`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-005`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, low_value_predicate
- `bv2-sf-006`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-007`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-008`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-009`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-011`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, low_value_predicate
- `bv2-sf-012`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, low_value_predicate

### traversal_graph_3_hop

- `bv2-sf-001`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-002`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-004`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-005`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, low_value_predicate
- `bv2-sf-006`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-007`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-008`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-009`: missed_gold_evidence_at_5; path_found_but_wrong_chunk
- `bv2-sf-011`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, low_value_predicate
- `bv2-sf-012`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, low_value_predicate

### hybrid_vector_lexical_graph

- `bv2-sf-004`: missed_gold_evidence_at_5
- `bv2-sf-005`: missed_gold_evidence_at_5; low_value_predicate
- `bv2-sf-006`: missed_gold_evidence_at_5
- `bv2-sf-007`: missed_gold_evidence_at_5
- `bv2-sf-012`: low_value_predicate
- `bv2-sf-013`: missed_gold_evidence_at_5
- `bv2-sf-014`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence; kg_sparse_for_question
- `bv2-sf-015`: missed_gold_evidence_at_5
- `bv2-sf-019`: missed_gold_evidence_at_5
- `bv2-sf-020`: missed_gold_evidence_at_5

### hybrid_vector_traversal_graph

- `bv2-sf-001`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `bv2-sf-004`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `bv2-sf-005`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, low_value_predicate, graph_fusion_dilution
- `bv2-sf-006`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `bv2-sf-007`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `bv2-sf-008`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `bv2-sf-009`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `bv2-sf-011`: low_value_predicate
- `bv2-sf-012`: low_value_predicate
- `bv2-sf-013`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution

### hybrid_vector_traversal_guarded

- `bv2-sf-001`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `bv2-sf-004`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `bv2-sf-005`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, low_value_predicate, graph_fusion_dilution
- `bv2-sf-006`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `bv2-sf-007`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `bv2-sf-008`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `bv2-sf-009`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
- `bv2-sf-011`: low_value_predicate
- `bv2-sf-012`: low_value_predicate
- `bv2-sf-013`: missed_gold_evidence_at_5; path_found_but_wrong_chunk, graph_fusion_dilution
