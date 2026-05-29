# Graph Traversal Ablation

- Run ID: `graph-traversal-ablation-20260529T221747Z`
- Questions: 35
- Scenarios: 7
- Scoring: retrieval, KG evidence, and graph path metrics are kept separate.

| Scenario | Recall@5 | MRR@5 | Context Precision@5 | KG coverage | Path coverage | Avg path length | Avg returned paths | Key entity coverage | Relation coverage | Failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| vector-only | 0.6857 | 0.4714 | 0.1771 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 35 |
| lexical graph search | 0.5143 | 0.3929 | 0.1543 | 0.8286 | 0.0 | 0.0 | 0.0 | 0.6 | 0.625 | 17 |
| traversal graph search with 1 hop | 0.1714 | 0.1714 | 0.0638 | 0.7714 | 0.9429 | 1.0 | 9.6286 | 0.4833 | 0.75 | 29 |
| traversal graph search with 2 hops | 0.1714 | 0.1714 | 0.0419 | 0.7429 | 0.9429 | 1.417 | 16.5143 | 0.4929 | 0.75 | 29 |
| traversal graph search with 3 hops | 0.1714 | 0.15 | 0.0381 | 0.7429 | 0.9429 | 1.6115 | 18.8286 | 0.5024 | 0.75 | 29 |
| hybrid vector + lexical graph | 0.6286 | 0.4471 | 0.1543 | 0.8286 | 0.0 | 0.0 | 0.0 | 0.6 | 0.625 | 13 |
| hybrid vector + traversal graph | 0.6571 | 0.3557 | 0.16 | 0.7429 | 0.9429 | 1.417 | 16.5143 | 0.4929 | 0.75 | 14 |

## Notes

Lexical graph search remains the baseline. Traversal metrics describe whether bounded KG paths were returned and whether they cover named entities or relation intent; they do not imply better retrieval unless Recall@5/MRR@5 support that.

## Failure Cases

### vector_only

- `exp-001-atmosphere-envelope`: missing_kg_key_entity_evidence
- `exp-002-atmosphere-composition`: missing_kg_key_entity_evidence
- `exp-003-air-fluid`: missing_kg_key_entity_evidence
- `exp-004-viscosity-definition`: missing_kg_key_entity_evidence
- `exp-005-air-low-viscosity`: missing_kg_key_entity_evidence
- `exp-006-friction-wing-surface`: missing_kg_key_entity_evidence
- `exp-007-boundary-layer`: missing_kg_key_entity_evidence
- `exp-008-pressure-definition`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence
- `exp-009-atmospheric-pressure`: missing_kg_key_entity_evidence
- `exp-010-standard-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence

### lexical_graph_search

- `exp-008-pressure-definition`: missed_gold_evidence_at_5
- `exp-010-standard-pressure`: missed_gold_evidence_at_5
- `exp-011-pressure-altitude-trend`: missed_gold_evidence_at_5
- `exp-012-nonstandard-atmosphere`: missed_gold_evidence_at_5
- `exp-013-pressure-altitude`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence
- `exp-017-temperature-density`: missed_gold_evidence_at_5
- `exp-021-newton-second`: missed_gold_evidence_at_5
- `exp-022-newton-third`: missed_gold_evidence_at_5
- `exp-023-bernoulli`: missed_gold_evidence_at_5
- `exp-024-venturi`: missed_gold_evidence_at_5

### traversal_graph_1_hop

- `exp-001-atmosphere-envelope`: missed_gold_evidence_at_5
- `exp-002-atmosphere-composition`: missed_gold_evidence_at_5
- `exp-003-air-fluid`: missed_gold_evidence_at_5
- `exp-004-viscosity-definition`: missed_gold_evidence_at_5
- `exp-005-air-low-viscosity`: missed_gold_evidence_at_5
- `exp-008-pressure-definition`: missed_gold_evidence_at_5
- `exp-009-atmospheric-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence
- `exp-010-standard-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence
- `exp-011-pressure-altitude-trend`: missed_gold_evidence_at_5
- `exp-012-nonstandard-atmosphere`: missed_gold_evidence_at_5

### traversal_graph_2_hop

- `exp-001-atmosphere-envelope`: missed_gold_evidence_at_5
- `exp-002-atmosphere-composition`: missed_gold_evidence_at_5
- `exp-003-air-fluid`: missed_gold_evidence_at_5
- `exp-004-viscosity-definition`: missed_gold_evidence_at_5
- `exp-005-air-low-viscosity`: missed_gold_evidence_at_5
- `exp-008-pressure-definition`: missed_gold_evidence_at_5
- `exp-009-atmospheric-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence
- `exp-010-standard-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence
- `exp-011-pressure-altitude-trend`: missed_gold_evidence_at_5
- `exp-012-nonstandard-atmosphere`: missed_gold_evidence_at_5

### traversal_graph_3_hop

- `exp-001-atmosphere-envelope`: missed_gold_evidence_at_5
- `exp-002-atmosphere-composition`: missed_gold_evidence_at_5
- `exp-003-air-fluid`: missed_gold_evidence_at_5
- `exp-004-viscosity-definition`: missed_gold_evidence_at_5
- `exp-005-air-low-viscosity`: missed_gold_evidence_at_5
- `exp-008-pressure-definition`: missed_gold_evidence_at_5
- `exp-009-atmospheric-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence
- `exp-010-standard-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence
- `exp-011-pressure-altitude-trend`: missed_gold_evidence_at_5
- `exp-012-nonstandard-atmosphere`: missed_gold_evidence_at_5

### hybrid_vector_lexical_graph

- `exp-008-pressure-definition`: missed_gold_evidence_at_5
- `exp-010-standard-pressure`: missed_gold_evidence_at_5
- `exp-011-pressure-altitude-trend`: missed_gold_evidence_at_5
- `exp-012-nonstandard-atmosphere`: missed_gold_evidence_at_5
- `exp-013-pressure-altitude`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence
- `exp-022-newton-third`: missed_gold_evidence_at_5
- `exp-027-efficient-airfoil`: missed_gold_evidence_at_5
- `exp-030-pressure-distribution`: missed_gold_evidence_at_5
- `exp-031-no-answer-vspeeds`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence
- `exp-032-no-answer-live-weather`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence

### hybrid_vector_traversal_graph

- `exp-005-air-low-viscosity`: missed_gold_evidence_at_5
- `exp-008-pressure-definition`: missed_gold_evidence_at_5
- `exp-009-atmospheric-pressure`: missing_kg_key_entity_evidence
- `exp-010-standard-pressure`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence
- `exp-012-nonstandard-atmosphere`: missed_gold_evidence_at_5
- `exp-014-density-altitude`: missed_gold_evidence_at_5
- `exp-027-efficient-airfoil`: missed_gold_evidence_at_5
- `exp-028-low-pressure-above`: missing_kg_key_entity_evidence
- `exp-030-pressure-distribution`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence
- `exp-031-no-answer-vspeeds`: missed_gold_evidence_at_5, missing_kg_key_entity_evidence
