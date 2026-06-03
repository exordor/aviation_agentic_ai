# NASA ATMONTO S7 Fixed-Budget LLM Answer Generation

## Scope

- Status: `s7_llm_answer_generation_evaluated`
- Reviewer model: `gpt-5.4-mini`
- Run LLM requested: True
- LLM runtime available: True
- Selected cases: 12
- Modes: `routed_token_matched_live_tfidf_graphrag`, `routed_token_matched_dense_graphrag`
- Boundary: Bounded LLM answer-generation pass over frozen S7 retrieved contexts. This is retrospective and source-bounded, not operational ATC support.

## Aggregate LLM Answer Quality

| Mode | Selected | Answered | Not run | Failed | Correctness | Citation P | Citation R | Evidence faithful | Unsupported claim rate | Abstention correct | Avg context tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `routed_token_matched_live_tfidf_graphrag` | 6 | 6 | 0 | 0 | 0.8333 | 1.0 | 0.6111 | 0.8333 | 0.3333 | 0.8333 | 23.0 |
| `routed_token_matched_dense_graphrag` | 6 | 6 | 0 | 0 | 0.5 | 1.0 | 0.6111 | 0.5 | 0.3333 | 0.5 | 23.0 |

## Notes

- This is a fixed-budget model run over existing S7 contexts, not human review.
- Missing or failed LLM calls are counted separately from answered cases.
- Dense retrieval should remain framed as negative/qualified unless answered cases show a defensible benefit.

## Claim Boundary

This report is a small fixed-budget LLM generation check over existing S7 contexts. It can support error discovery and cautious comparison, but it is not human review, expert certification, or operational readiness evidence.
