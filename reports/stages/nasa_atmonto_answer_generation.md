# NASA ATMONTO GraphRAG Answer Generation

## Scope

- Status: `answer_generation_evaluated`
- Benchmark labels: 18
- Modes: `source_only`, `vector_rag`, `token_matched_vector_rag`, `graph_only`, `hybrid_graphrag`, `routed_graphrag`
- Boundary: Retrospective ATCSCC advisory GraphRAG answer evaluation only.
- Critic gate rejected facts: 20

## Aggregate Answer Quality

| Mode | Answers | Correctness | Citation P | Citation R | Evidence faithful | Unsupported claim rate | Abstention correct | Avg context tokens | Avg target tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `source_only` | 18 | 1.0 | 1.0 | 0.4167 | 1.0 | 0.0 | 1.0 | 5.11 | n/a |
| `vector_rag` | 18 | 1.0 | 1.0 | 0.4167 | 1.0 | 0.0 | 1.0 | 5.11 | n/a |
| `token_matched_vector_rag` | 18 | 1.0 | 1.0 | 0.4167 | 1.0 | 0.0 | 1.0 | 5.11 | 14.06 |
| `graph_only` | 18 | 0.8333 | 1.0 | 0.3333 | 0.8333 | 0.0833 | 1.0 | 48.78 | n/a |
| `hybrid_graphrag` | 18 | 0.8333 | 1.0 | 0.5833 | 0.8333 | 0.0833 | 1.0 | 14.06 | n/a |
| `routed_graphrag` | 18 | 0.8333 | 1.0 | 0.5417 | 0.8333 | 0.0833 | 1.0 | 12.39 | n/a |

## S7 Graph-Use Gate

- Status: `deterministic_proxy_gate`
- Policy: route each CQ template to vector or hybrid graph context before generation
- Decision counts: {'hybrid_graphrag': 12, 'vector_rag': 6}
- Boundary: The gate is evaluated in the deterministic answer scaffold. It is a proxy for query routing and does not claim live retriever performance.

## Critic Gate

- Policy: reject known parser artifacts before graph/hybrid answer generation
- Rejected values: ADDS, ADVZY, ARE, CAN, INTO, THAT, USERS

## Claim Boundary

The experiment is retrospective and source-bounded. It evaluates extraction, CQ queryability, and generated-answer behavior as separate layers; it does not make live operational decision-support claims.
