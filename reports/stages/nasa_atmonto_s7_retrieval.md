# NASA ATMONTO S7 Retrieval-Only Graph-Use Gate

## Scope

- Status: `s7_retrieval_gate_evaluated`
- Retrieval cases: 317
- Modes: `source_oracle`, `vector_rag_proxy`, `token_matched_vector_proxy`, `live_tfidf_vector`, `token_matched_live_tfidf_vector`, `dense_embedding_vector`, `token_matched_dense_embedding_vector`, `graph_only`, `hybrid_graphrag`, `routed_graphrag`, `routed_live_tfidf_graphrag`, `routed_token_matched_live_tfidf_graphrag`, `routed_dense_graphrag`, `routed_token_matched_dense_graphrag`
- Boundary: Retrieval-only evaluation over source-bounded ATCSCC labels. Live retrieval modes include deterministic lexical TF-IDF and dense embedding source indexes over frozen ATCSCC records.
- Live source documents: 100
- Dense retrieval model: `sentence-transformers/all-MiniLM-L6-v2` (local_files_only=True)
- Materialized graph: 100 source nodes, 666 fact nodes, 1332 edges

## Aggregate Retrieval Metrics

| Mode | Recall@5 | Context recall | Target hit | Answer P | Answer R | Answer F1 | Abstention correct | Path support | Avg context tokens | Target tokens | Guard rate | Avg latency ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `source_oracle` | 0.6845 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | None | 19.78 | n/a | 0.0 | 0.0027 |
| `vector_rag_proxy` | 0.6845 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | None | 19.78 | n/a | 0.0 | 0.0018 |
| `token_matched_vector_proxy` | 0.6845 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | None | 19.78 | 38.96 | 0.0 | 0.0017 |
| `live_tfidf_vector` | 0.6845 | 1.0 | 1.0 | 0.6999 | 1.0 | 0.8235 | 1.0 | None | 2001.44 | n/a | 0.0 | 0.2199 |
| `token_matched_live_tfidf_vector` | 0.6845 | 1.0 | 1.0 | 0.6999 | 1.0 | 0.8235 | 1.0 | None | 38.96 | 38.96 | 0.0 | 0.4382 |
| `dense_embedding_vector` | 0.3123 | 0.6278 | 0.6088 | 0.4011 | 0.8096 | 0.5364 | 1.0 | None | 1532.91 | n/a | 0.5615 | 10.5932 |
| `token_matched_dense_embedding_vector` | 0.2776 | 0.5931 | 0.571 | 0.3889 | 0.7693 | 0.5166 | 0.93 | None | 38.96 | 38.96 | 0.5615 | 10.1492 |
| `graph_only` | 0.6845 | 1.0 | 0.9968 | 0.5521 | 0.4923 | 0.5205 | 0.01 | 1.0 | 25.18 | n/a | 0.0 | 0.0026 |
| `hybrid_graphrag` | 0.6845 | 1.0 | 1.0 | 0.5521 | 0.4923 | 0.5205 | 0.01 | 1.0 | 38.96 | n/a | 0.0 | 0.0051 |
| `routed_graphrag` | 0.6845 | 1.0 | 1.0 | 0.9671 | 1.0 | 0.9833 | 1.0 | 1.0 | 24.82 | n/a | 0.0 | 0.0027 |
| `routed_live_tfidf_graphrag` | 0.6845 | 1.0 | 1.0 | 0.7442 | 1.0 | 0.8534 | 1.0 | 1.0 | 1326.48 | n/a | 0.0 | 0.1308 |
| `routed_token_matched_live_tfidf_graphrag` | 0.6845 | 1.0 | 1.0 | 0.7442 | 1.0 | 0.8534 | 1.0 | 1.0 | 38.96 | 38.96 | 0.0 | 0.2852 |
| `routed_dense_graphrag` | 0.6845 | 1.0 | 1.0 | 0.4578 | 1.0 | 0.6281 | 1.0 | 1.0 | 989.09 | n/a | 0.5615 | 6.0642 |
| `routed_token_matched_dense_graphrag` | 0.6751 | 0.9905 | 0.9685 | 0.4477 | 0.9598 | 0.6105 | 0.93 | 1.0 | 38.96 | 38.96 | 0.5615 | 6.1463 |

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

This report evaluates retrieval-context availability, graph path support, answer-set recovery, live lexical-vector retrieval, dense-vector retrieval, and token-budget controls. It does not prove operational GraphRAG performance.
