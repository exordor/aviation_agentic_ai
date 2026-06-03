# NASA ATMONTO S7 Graph Health by CQ Group

## Scope

- Status: `s7_graph_health_evaluated`
- Retrieval cases: 317
- Modes: `graph_only`, `hybrid_graphrag`, `routed_graphrag`, `routed_token_matched_live_tfidf_graphrag`, `routed_token_matched_dense_graphrag`
- Boundary: Graph-health diagnostics over frozen S7 retrieval records. These metrics describe path and context availability by CQ group; they do not certify semantic truth or operational readiness.
- Materialized graph: 100 source nodes, 666 fact nodes, 1332 edges

## Aggregate Graph Health by Mode

| Mode | Cases | Graph-context rate | Avg graph contexts | Path support | Answer F1 | Abstention correct | Target hit | Avg context tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `graph_only` | 317 | 0.9968 | 1.8013 | 1.0 | 0.5205 | 0.01 | 0.9968 | 25.18 |
| `hybrid_graphrag` | 317 | 0.9968 | 1.4322 | 1.0 | 0.5205 | 0.01 | 1.0 | 38.96 |
| `routed_graphrag` | 317 | 0.3975 | 0.4543 | 1.0 | 0.9833 | 1.0 | 1.0 | 24.82 |
| `routed_token_matched_live_tfidf_graphrag` | 317 | 0.3975 | 0.4543 | 1.0 | 0.8534 | 1.0 | 1.0 | 38.96 |
| `routed_token_matched_dense_graphrag` | 317 | 0.3975 | 0.4543 | 1.0 | 0.1933 | 0.02 | 0.4069 | 38.96 |

## CQ Template Graph Health

| Template | Mode | Cases | Graph-context rate | Avg graph contexts | Path support | Answer F1 | Abstention correct |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `QT-A01-ABSTENTION-FIELDS` | `graph_only` | 100 | 0.99 | 2.36 | 1.0 | 0.0174 | 0.01 |
| `QT-A01-ABSTENTION-FIELDS` | `hybrid_graphrag` | 100 | 0.99 | 2.19 | 1.0 | 0.0174 | 0.01 |
| `QT-A01-ABSTENTION-FIELDS` | `routed_graphrag` | 100 | 0.0 | 0.0 | n/a | 1.0 | 1.0 |
| `QT-A01-ABSTENTION-FIELDS` | `routed_token_matched_live_tfidf_graphrag` | 100 | 0.0 | 0.0 | n/a | 1.0 | 1.0 |
| `QT-A01-ABSTENTION-FIELDS` | `routed_token_matched_dense_graphrag` | 100 | 0.0 | 0.0 | n/a | 0.0469 | 0.02 |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `graph_only` | 36 | 1.0 | 1.25 | 1.0 | 0.8889 | n/a |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `hybrid_graphrag` | 36 | 1.0 | 1.1944 | 1.0 | 0.8889 | n/a |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `routed_graphrag` | 36 | 1.0 | 1.1944 | 1.0 | 0.8889 | n/a |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `routed_token_matched_live_tfidf_graphrag` | 36 | 1.0 | 1.1944 | 1.0 | 0.8889 | n/a |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `routed_token_matched_dense_graphrag` | 36 | 1.0 | 1.1944 | 1.0 | 0.8889 | n/a |
| `QT-Q01-CAUSE-CONDITION` | `graph_only` | 24 | 1.0 | 1.2917 | 1.0 | 0.9667 | n/a |
| `QT-Q01-CAUSE-CONDITION` | `hybrid_graphrag` | 24 | 1.0 | 1.0833 | 1.0 | 0.9667 | n/a |
| `QT-Q01-CAUSE-CONDITION` | `routed_graphrag` | 24 | 1.0 | 1.0833 | 1.0 | 0.9667 | n/a |
| `QT-Q01-CAUSE-CONDITION` | `routed_token_matched_live_tfidf_graphrag` | 24 | 1.0 | 1.0833 | 1.0 | 0.9667 | n/a |
| `QT-Q01-CAUSE-CONDITION` | `routed_token_matched_dense_graphrag` | 24 | 1.0 | 1.0833 | 1.0 | 0.9667 | n/a |
| `QT-Q01-ROUTE-SEMANTICS` | `graph_only` | 36 | 1.0 | 1.25 | 1.0 | 0.8889 | n/a |
| `QT-Q01-ROUTE-SEMANTICS` | `hybrid_graphrag` | 36 | 1.0 | 1.1944 | 1.0 | 0.8889 | n/a |
| `QT-Q01-ROUTE-SEMANTICS` | `routed_graphrag` | 36 | 1.0 | 1.1944 | 1.0 | 0.8889 | n/a |
| `QT-Q01-ROUTE-SEMANTICS` | `routed_token_matched_live_tfidf_graphrag` | 36 | 1.0 | 1.1944 | 1.0 | 0.8889 | n/a |
| `QT-Q01-ROUTE-SEMANTICS` | `routed_token_matched_dense_graphrag` | 36 | 1.0 | 1.1944 | 1.0 | 0.8889 | n/a |
| `QT-Q01-STATUS-ACTION` | `graph_only` | 30 | 1.0 | 1.0667 | 1.0 | 0.9677 | n/a |
| `QT-Q01-STATUS-ACTION` | `hybrid_graphrag` | 30 | 1.0 | 1.0667 | 1.0 | 0.9677 | n/a |
| `QT-Q01-STATUS-ACTION` | `routed_graphrag` | 30 | 1.0 | 1.0667 | 1.0 | 0.9677 | n/a |
| `QT-Q01-STATUS-ACTION` | `routed_token_matched_live_tfidf_graphrag` | 30 | 1.0 | 1.0667 | 1.0 | 0.9677 | n/a |
| `QT-Q01-STATUS-ACTION` | `routed_token_matched_dense_graphrag` | 30 | 1.0 | 1.0667 | 1.0 | 0.9677 | n/a |
| `QT-Q01-TIME-WINDOW` | `graph_only` | 91 | 1.0 | 2.0 | 1.0 | 1.0 | n/a |
| `QT-Q01-TIME-WINDOW` | `hybrid_graphrag` | 91 | 1.0 | 1.0 | 1.0 | 1.0 | n/a |
| `QT-Q01-TIME-WINDOW` | `routed_graphrag` | 91 | 0.0 | 0.0 | n/a | 1.0 | n/a |
| `QT-Q01-TIME-WINDOW` | `routed_token_matched_live_tfidf_graphrag` | 91 | 0.0 | 0.0 | n/a | 0.6454 | n/a |
| `QT-Q01-TIME-WINDOW` | `routed_token_matched_dense_graphrag` | 91 | 0.0 | 0.0 | n/a | 0.0256 | n/a |

## Claim Boundary

Graph health is reported as topology, graph-context availability, path-support rate, answer-set recovery, and abstention behavior. It is a diagnostic layer, not a proof that graph context is always better than source or vector retrieval.
