# NASA ATMONTO S7 Retrieval-Only Graph-Use Gate

## Scope

- Status: `s7_retrieval_gate_evaluated`
- Retrieval cases: 317
- Modes: `source_oracle`, `vector_rag_proxy`, `token_matched_vector_proxy`, `live_tfidf_vector`, `token_matched_live_tfidf_vector`, `graph_only`, `hybrid_graphrag`, `routed_graphrag`
- Boundary: Retrieval-only evaluation over source-bounded ATCSCC labels. Live vector modes use a deterministic lexical TF-IDF source index, not a dense embedding index.
- Live source documents: 100
- Materialized graph: 100 source nodes, 666 fact nodes, 1332 edges

## Aggregate Retrieval Metrics

| Mode | Recall@5 | Context recall | Target hit | Answer P | Answer R | Answer F1 | Abstention correct | Path support | Avg tokens | Target tokens | Avg latency ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `source_oracle` | 0.6845 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | None | 19.78 | n/a | 0.0014 |
| `vector_rag_proxy` | 0.6845 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | None | 19.78 | n/a | 0.0013 |
| `token_matched_vector_proxy` | 0.6845 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | None | 19.78 | 38.37 | 0.0012 |
| `live_tfidf_vector` | 0.6845 | 1.0 | 1.0 | 0.8935 | 1.0 | 0.9438 | 1.0 | None | 2001.44 | n/a | 0.1458 |
| `token_matched_live_tfidf_vector` | 0.6845 | 1.0 | 1.0 | 0.8935 | 1.0 | 0.9438 | 1.0 | None | 38.37 | 38.37 | 0.4376 |
| `graph_only` | 0.6845 | 1.0 | 0.9968 | 0.5618 | 0.4923 | 0.5248 | 0.01 | 1.0 | 24.49 | n/a | 0.0015 |
| `hybrid_graphrag` | 0.6845 | 1.0 | 1.0 | 0.5618 | 0.4923 | 0.5248 | 0.01 | 1.0 | 38.37 | n/a | 0.0037 |
| `routed_graphrag` | 0.6845 | 1.0 | 1.0 | 0.9773 | 1.0 | 0.9885 | 1.0 | 1.0 | 24.29 | n/a | 0.0022 |

Method note: Answer-set F1 treats a correct expected abstention as recovering the no-answer label. `Abstention correct` is computed only over expected abstention cases and should be read separately from non-abstention answer recovery.

## Graph-Use Route Summary

- Decision counts: {'hybrid_graphrag': 126, 'vector_rag': 191}

| Template | Underlying mode | Cases | Reason |
| --- | --- | ---: | --- |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `hybrid_graphrag` | 36 | graph context selected for semantic, entity-role, cause/status, or route query |
| `QT-Q01-TIME-WINDOW` | `vector_rag` | 91 | source/vector proxy selected for direct temporal or abstention query |
| `QT-Q01-CAUSE-CONDITION` | `hybrid_graphrag` | 24 | graph context selected for semantic, entity-role, cause/status, or route query |
| `QT-Q01-STATUS-ACTION` | `hybrid_graphrag` | 30 | graph context selected for semantic, entity-role, cause/status, or route query |
| `QT-Q01-ROUTE-SEMANTICS` | `hybrid_graphrag` | 36 | graph context selected for semantic, entity-role, cause/status, or route query |
| `QT-A01-ABSTENTION-FIELDS` | `vector_rag` | 100 | source/vector proxy selected for direct temporal or abstention query |

## Critic Gate

- Policy: reject known parser artifacts before graph/hybrid answer generation
- Rejected facts: 20
- Rejected values: ADDS, ADVZY, ARE, CAN, INTO, THAT, USERS

## Claim Boundary

This report evaluates retrieval-context availability, graph path support, answer-set recovery, live lexical-vector retrieval, and token-budget proxies. It does not prove dense-vector or operational GraphRAG performance.
