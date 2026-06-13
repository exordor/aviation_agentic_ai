# NASA ATMONTO GraphRAG Answer Generation

## Scope

- Status: `answer_generation_evaluated`
- Benchmark labels: 18
- Modes: `source_only`, `vector_rag`, `token_matched_vector_rag`, `graph_only`, `hybrid_graphrag`, `routed_graphrag`
- Boundary: Retrospective ATCSCC advisory GraphRAG answer evaluation only.
- Critic gate rejected facts: 25

## Aggregate Answer Quality

| Mode | Answers | Correctness | Citation P | Citation R | Evidence faithful | Unsupported claim rate | Abstention correct | Avg context tokens | Avg target tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `source_only` | 18 | 1.0 | 1.0 | 0.4167 | 1.0 | 0.0 | 1.0 | 5.94 | n/a |
| `vector_rag` | 18 | 1.0 | 1.0 | 0.4167 | 1.0 | 0.0 | 1.0 | 5.94 | n/a |
| `token_matched_vector_rag` | 18 | 1.0 | 1.0 | 0.4167 | 1.0 | 0.0 | 1.0 | 5.94 | 16.56 |
| `graph_only` | 18 | 0.8333 | 1.0 | 0.3148 | 0.9444 | 0.0278 | 1.0 | 49.28 | n/a |
| `hybrid_graphrag` | 18 | 0.9444 | 1.0 | 0.5861 | 0.9444 | 0.0185 | 1.0 | 16.56 | n/a |
| `routed_graphrag` | 18 | 0.9444 | 1.0 | 0.5445 | 0.9444 | 0.0185 | 1.0 | 14.89 | n/a |

## S7 Graph-Use Gate

- Status: `deterministic_proxy_gate`
- Policy: route each CQ template to vector or hybrid graph context before generation
- Decision counts: {'hybrid_graphrag': 12, 'vector_rag': 6}
- Boundary: The gate is evaluated in the deterministic answer scaffold. It is a proxy for query routing and does not claim live retriever performance.

## Critic Gate

- Policy: reject known parser artifacts before graph/hybrid answer generation
- Rejected values: ADDS, ADVZY, ARE, Airport, CAN, INTO, THAT, USERS, {"@type": "nas:Airport", "evidence_text": "CTL ELEMENT: SFO ELEMENT TYPE: APT"}, {"evidence_text": "CTL ELEMENT: IAD ELEMENT TYPE: APT ADL TIME: 1907Z GROUND STOP PERIOD: 20/1900Z - 20/2015Z", "type": "nas:Airport"}, {"evidence_text": "CTL ELEMENT: ORD ELEMENT TYPE: APT", "type": "nas:Airport"}

## Claim Boundary

The experiment is retrospective and source-bounded. NASA ATMONTO-derived terms are used as a lightweight application schema, not as a complete aviation ontology or ground truth. The thesis evaluates schema-constrained event extraction, agentic validation/refinement, KG-RAG grounding, and failure/human-review boundaries as separate layers; it does not make live operational ATC decision-support claims.
