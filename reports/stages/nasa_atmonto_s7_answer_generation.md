# NASA ATMONTO S7 Live-Retrieval Answer Generation

## Scope

- Status: `s7_answer_generation_evaluated`
- Benchmark labels: 317
- Modes: `source_oracle`, `hybrid_graphrag`, `routed_graphrag`, `token_matched_live_tfidf_vector`, `routed_token_matched_live_tfidf_graphrag`, `token_matched_dense_embedding_vector`, `routed_token_matched_dense_graphrag`
- Boundary: Retrospective ATCSCC S7 answer-generation rerun over routed live retrieval contexts; no live operational decision-support claim.
- Live source documents: 100
- Dense retrieval model: `sentence-transformers/all-MiniLM-L6-v2` (local_files_only=True)

## Aggregate Answer Quality

| Mode | Answers | Correctness | Citation P | Citation R | Evidence faithful | Unsupported claim rate | Abstention correct | Avg tokens | Target tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `source_oracle` | 317 | 1.0 | 1.0 | 0.3423 | 1.0 | 0.0 | 1.0 | 19.78 | n/a |
| `hybrid_graphrag` | 317 | 0.9527 | 1.0 | 0.4603 | 0.9527 | 0.0237 | 1.0 | 38.37 | n/a |
| `routed_graphrag` | 317 | 0.9527 | 1.0 | 0.4125 | 0.9527 | 0.0237 | 1.0 | 24.29 | n/a |
| `token_matched_live_tfidf_vector` | 317 | 0.8297 | 1.0 | 0.4564 | 0.8297 | 0.0954 | 1.0 | 38.37 | 38.37 |
| `routed_token_matched_live_tfidf_graphrag` | 317 | 0.9527 | 1.0 | 0.4603 | 0.9527 | 0.0237 | 1.0 | 38.37 | 38.37 |
| `token_matched_dense_embedding_vector` | 317 | 0.3123 | 1.0 | 0.2166 | 0.3186 | 0.3722 | 0.4385 | 38.37 | 38.37 |
| `routed_token_matched_dense_graphrag` | 317 | 0.6435 | 1.0 | 0.413 | 0.6435 | 0.0237 | 0.6909 | 38.37 | 38.37 |

## CQ Template Breakdown

| Template | Mode | Correctness | Unsupported claim rate | Avg tokens |
| --- | --- | ---: | ---: | ---: |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `source_oracle` | 1.0 | 0.0 | 4.69 |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `hybrid_graphrag` | 0.8333 | 0.0833 | 11.75 |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `routed_graphrag` | 0.8333 | 0.0833 | 11.75 |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `token_matched_live_tfidf_vector` | 0.6944 | 0.1528 | 11.75 |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `routed_token_matched_live_tfidf_graphrag` | 0.8333 | 0.0833 | 11.75 |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `token_matched_dense_embedding_vector` | 0.0278 | 0.9722 | 11.75 |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `routed_token_matched_dense_graphrag` | 0.8333 | 0.0833 | 11.75 |
| `QT-Q01-TIME-WINDOW` | `source_oracle` | 1.0 | 0.0 | 21.0 |
| `QT-Q01-TIME-WINDOW` | `hybrid_graphrag` | 1.0 | 0.0 | 32.0 |
| `QT-Q01-TIME-WINDOW` | `routed_graphrag` | 1.0 | 0.0 | 21.0 |
| `QT-Q01-TIME-WINDOW` | `token_matched_live_tfidf_vector` | 1.0 | 0.0 | 32.0 |
| `QT-Q01-TIME-WINDOW` | `routed_token_matched_live_tfidf_graphrag` | 1.0 | 0.0 | 32.0 |
| `QT-Q01-TIME-WINDOW` | `token_matched_dense_embedding_vector` | 1.0 | 0.0 | 32.0 |
| `QT-Q01-TIME-WINDOW` | `routed_token_matched_dense_graphrag` | 1.0 | 0.0 | 32.0 |
| `QT-Q01-CAUSE-CONDITION` | `source_oracle` | 1.0 | 0.0 | 14.21 |
| `QT-Q01-CAUSE-CONDITION` | `hybrid_graphrag` | 0.9167 | 0.0417 | 28.5 |
| `QT-Q01-CAUSE-CONDITION` | `routed_graphrag` | 0.9167 | 0.0417 | 28.5 |
| `QT-Q01-CAUSE-CONDITION` | `token_matched_live_tfidf_vector` | 0.0833 | 0.5799 | 28.5 |
| `QT-Q01-CAUSE-CONDITION` | `routed_token_matched_live_tfidf_graphrag` | 0.9167 | 0.0417 | 28.5 |
| `QT-Q01-CAUSE-CONDITION` | `token_matched_dense_embedding_vector` | 0.1667 | 0.75 | 28.5 |
| `QT-Q01-CAUSE-CONDITION` | `routed_token_matched_dense_graphrag` | 0.9167 | 0.0417 | 28.5 |
| `QT-Q01-STATUS-ACTION` | `source_oracle` | 1.0 | 0.0 | 18.3 |
| `QT-Q01-STATUS-ACTION` | `hybrid_graphrag` | 0.9667 | 0.0167 | 37.57 |
| `QT-Q01-STATUS-ACTION` | `routed_graphrag` | 0.9667 | 0.0167 | 37.57 |
| `QT-Q01-STATUS-ACTION` | `token_matched_live_tfidf_vector` | 0.6667 | 0.1778 | 37.57 |
| `QT-Q01-STATUS-ACTION` | `routed_token_matched_live_tfidf_graphrag` | 0.9667 | 0.0167 | 37.57 |
| `QT-Q01-STATUS-ACTION` | `token_matched_dense_embedding_vector` | 0.0333 | 0.9667 | 37.57 |
| `QT-Q01-STATUS-ACTION` | `routed_token_matched_dense_graphrag` | 0.9667 | 0.0167 | 37.57 |
| `QT-Q01-ROUTE-SEMANTICS` | `source_oracle` | 1.0 | 0.0 | 4.69 |
| `QT-Q01-ROUTE-SEMANTICS` | `hybrid_graphrag` | 0.8333 | 0.0833 | 11.75 |
| `QT-Q01-ROUTE-SEMANTICS` | `routed_graphrag` | 0.8333 | 0.0833 | 11.75 |
| `QT-Q01-ROUTE-SEMANTICS` | `token_matched_live_tfidf_vector` | 0.6944 | 0.1528 | 11.75 |
| `QT-Q01-ROUTE-SEMANTICS` | `routed_token_matched_live_tfidf_graphrag` | 0.8333 | 0.0833 | 11.75 |
| `QT-Q01-ROUTE-SEMANTICS` | `token_matched_dense_embedding_vector` | 0.0 | 1.0 | 11.75 |
| `QT-Q01-ROUTE-SEMANTICS` | `routed_token_matched_dense_graphrag` | 0.8333 | 0.0833 | 11.75 |
| `QT-A01-ABSTENTION-FIELDS` | `source_oracle` | 1.0 | 0.0 | 31.32 |
| `QT-A01-ABSTENTION-FIELDS` | `hybrid_graphrag` | 1.0 | 0.0 | 65.93 |
| `QT-A01-ABSTENTION-FIELDS` | `routed_graphrag` | 1.0 | 0.0 | 31.32 |
| `QT-A01-ABSTENTION-FIELDS` | `token_matched_live_tfidf_vector` | 1.0 | 0.0 | 65.93 |
| `QT-A01-ABSTENTION-FIELDS` | `routed_token_matched_live_tfidf_graphrag` | 1.0 | 0.0 | 65.93 |
| `QT-A01-ABSTENTION-FIELDS` | `token_matched_dense_embedding_vector` | 0.02 | 0.0 | 65.93 |
| `QT-A01-ABSTENTION-FIELDS` | `routed_token_matched_dense_graphrag` | 0.02 | 0.0 | 65.93 |

## Cost and Latency

- Provider: none
- Model: deterministic_s7_answer_scaffold
- Elapsed seconds: 10.1836

## Critic Gate

- Policy: reject known parser artifacts before graph/hybrid answer generation
- Rejected facts: 20
- Rejected values: ADDS, ADVZY, ARE, CAN, INTO, THAT, USERS

## Claim Boundary

This report closes the retrieval-only S7 gap by generating deterministic answers from routed live lexical and dense retrieval contexts. It is still not an online LLM or operational ATC decision-support evaluation.
