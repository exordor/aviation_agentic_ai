# NASA ATMONTO GraphRAG Answer Generation

## Scope

- Status: `answer_generation_evaluated`
- Benchmark labels: 18
- Modes: `source_only`, `vector_rag`, `graph_only`, `hybrid_graphrag`
- Boundary: Retrospective ATCSCC advisory GraphRAG answer evaluation only.
- Critic gate rejected facts: 20

## Aggregate Answer Quality

| Mode | Answers | Correctness | Citation P | Citation R | Evidence faithful | Unsupported claim rate | Abstention correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `source_only` | 18 | 1.0 | 1.0 | 0.4167 | 1.0 | 0.0 | 1.0 |
| `vector_rag` | 18 | 1.0 | 1.0 | 0.4167 | 1.0 | 0.0 | 1.0 |
| `graph_only` | 18 | 0.8333 | 1.0 | 0.3333 | 0.8333 | 0.0833 | 1.0 |
| `hybrid_graphrag` | 18 | 0.8333 | 1.0 | 0.5833 | 0.8333 | 0.0833 | 1.0 |

## Critic Gate

- Policy: reject known parser artifacts before graph/hybrid answer generation
- Rejected values: ADDS, ADVZY, ARE, CAN, INTO, THAT, USERS

## Claim Boundary

The experiment is retrospective and source-bounded. It evaluates extraction, CQ queryability, and generated-answer behavior as separate layers; it does not make live operational decision-support claims.
