# NASA ATMONTO S7 Retrieval-Only Graph-Use Gate

## Scope

- Status: `s7_retrieval_proxy_evaluated`
- Retrieval cases: 317
- Modes: `source_oracle`, `vector_rag_proxy`, `token_matched_vector_proxy`, `graph_only`, `hybrid_graphrag`, `routed_graphrag`
- Boundary: Retrieval-only deterministic proxy over source-bounded ATCSCC labels. Vector modes use source-text proxy context, not a live vector index.

## Aggregate Retrieval Metrics

| Mode | Recall@5 | Context recall | Answer P | Answer R | Answer F1 | Abstention correct | Path support | Avg tokens | Target tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `source_oracle` | 0.6845 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | None | 7.65 | n/a |
| `vector_rag_proxy` | 0.6845 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | None | 7.65 | n/a |
| `token_matched_vector_proxy` | 0.6845 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | None | 7.65 | 14.88 |
| `graph_only` | 0.6845 | 1.0 | 0.5618 | 0.4923 | 0.5248 | 0.01 | 1.0 | 9.32 | n/a |
| `hybrid_graphrag` | 0.6845 | 1.0 | 0.5618 | 0.4923 | 0.5248 | 0.01 | 1.0 | 14.88 | n/a |
| `routed_graphrag` | 0.6845 | 1.0 | 0.9773 | 1.0 | 0.9885 | 1.0 | 1.0 | 9.9 | n/a |

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

This report evaluates retrieval-context availability, graph path support, answer-set recovery, and token-budget proxies. It does not prove live GraphRAG or vector-index performance.
