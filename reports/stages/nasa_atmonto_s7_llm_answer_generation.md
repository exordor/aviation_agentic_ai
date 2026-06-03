# NASA ATMONTO S7 Fixed-Budget LLM Answer Generation

## Scope

- Status: `s7_llm_answer_generation_evaluated`
- Reviewer model: `gpt-5.4-mini`
- Prompt version: `nasa_atmonto_s7_llm_answer_v3_route_partial`
- Run LLM requested: True
- LLM runtime available: True
- Selected cases: 60
- Modes: `routed_token_matched_live_tfidf_graphrag`, `routed_token_matched_dense_graphrag`
- Boundary: Bounded LLM answer-generation pass over frozen S7 retrieved contexts. This is retrospective and source-bounded, not operational ATC support.

## Aggregate LLM Answer Quality

| Mode | Selected | Answered | Not run | Failed | Correctness | Citation P | Citation R | Evidence faithful | Unsupported claim rate | Abstention correct | Avg context tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `routed_token_matched_live_tfidf_graphrag` | 30 | 30 | 0 | 0 | 0.9667 | 1.0 | 0.6084 | 0.9667 | 0.0167 | 1.0 | 33.03 |
| `routed_token_matched_dense_graphrag` | 30 | 30 | 0 | 0 | 0.9333 | 1.0 | 0.5945 | 0.9333 | 0.0333 | 1.0 | 33.03 |

## CQ Template Breakdown

| Template | Mode | Selected | Answered | Correctness | Citation R | Unsupported claim rate | Abstention correct |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `QT-A01-ABSTENTION-FIELDS` | `routed_token_matched_live_tfidf_graphrag` | 5 | 5 | 1.0 | 0.6667 | 0.0 | 1.0 |
| `QT-A01-ABSTENTION-FIELDS` | `routed_token_matched_dense_graphrag` | 5 | 5 | 1.0 | 0.6 | 0.0 | 1.0 |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `routed_token_matched_live_tfidf_graphrag` | 5 | 5 | 1.0 | 0.6667 | 0.0 | 1.0 |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `routed_token_matched_dense_graphrag` | 5 | 5 | 1.0 | 0.6667 | 0.0 | 1.0 |
| `QT-Q01-CAUSE-CONDITION` | `routed_token_matched_live_tfidf_graphrag` | 5 | 5 | 0.8 | 0.65 | 0.1 | 1.0 |
| `QT-Q01-CAUSE-CONDITION` | `routed_token_matched_dense_graphrag` | 5 | 5 | 0.6 | 0.7 | 0.2 | 1.0 |
| `QT-Q01-ROUTE-SEMANTICS` | `routed_token_matched_live_tfidf_graphrag` | 5 | 5 | 1.0 | 0.6667 | 0.0 | 1.0 |
| `QT-Q01-ROUTE-SEMANTICS` | `routed_token_matched_dense_graphrag` | 5 | 5 | 1.0 | 0.6667 | 0.0 | 1.0 |
| `QT-Q01-STATUS-ACTION` | `routed_token_matched_live_tfidf_graphrag` | 5 | 5 | 1.0 | 0.6667 | 0.0 | 1.0 |
| `QT-Q01-STATUS-ACTION` | `routed_token_matched_dense_graphrag` | 5 | 5 | 1.0 | 0.6 | 0.0 | 1.0 |
| `QT-Q01-TIME-WINDOW` | `routed_token_matched_live_tfidf_graphrag` | 5 | 5 | 1.0 | 0.3333 | 0.0 | 1.0 |
| `QT-Q01-TIME-WINDOW` | `routed_token_matched_dense_graphrag` | 5 | 5 | 1.0 | 0.3333 | 0.0 | 1.0 |

## Notes

- This is a fixed-budget model run over existing S7 contexts, not human review.
- Missing or failed LLM calls are counted separately from answered cases.
- Dense results should be framed as source-local guarded and source-bounded, not as pure dense embedding superiority.

## Claim Boundary

This report is a small fixed-budget LLM generation check over existing S7 contexts. It can support error discovery and cautious comparison, but it is not human review, expert certification, or operational readiness evidence.
