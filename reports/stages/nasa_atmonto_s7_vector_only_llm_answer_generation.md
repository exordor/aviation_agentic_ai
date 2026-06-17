# NASA ATMONTO S7 Fixed-Budget LLM Answer Generation

## Scope

- Status: `s7_llm_answer_generation_evaluated`
- Reviewer model: `gpt-5.4-mini`
- Prompt version: `nasa_atmonto_s7_llm_answer_v3_route_partial`
- Run LLM requested: True
- LLM runtime available: True
- Selected cases: 60
- Modes: `token_matched_live_tfidf_vector`
- Boundary: Bounded LLM answer-generation pass over frozen S7 retrieved contexts. This is retrospective and source-bounded, not operational ATC support.

## Aggregate LLM Answer Quality

| Mode | Selected | Answered | Not run | Failed | Correctness | Citation P | Citation R | Evidence faithful | Unsupported claim rate | Abstention correct | Avg context tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `token_matched_live_tfidf_vector` | 60 | 60 | 0 | 0 | 0.5 | 1.0 | 0.3722 | 0.5 | 0.5 | 0.9667 | 31.23 |

## CQ Template Breakdown

| Template | Mode | Selected | Answered | Correctness | Citation R | Unsupported claim rate | Abstention correct |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `QT-A01-ABSTENTION-FIELDS` | `token_matched_live_tfidf_vector` | 10 | 10 | 1.0 | 0.6 | 0.0 | 1.0 |
| `QT-Q01-AFFECTED-NAS-ELEMENTS` | `token_matched_live_tfidf_vector` | 10 | 10 | 0.0 | 0.3333 | 1.0 | 1.0 |
| `QT-Q01-CAUSE-CONDITION` | `token_matched_live_tfidf_vector` | 10 | 10 | 0.0 | 0.3333 | 1.0 | 1.0 |
| `QT-Q01-ROUTE-SEMANTICS` | `token_matched_live_tfidf_vector` | 10 | 10 | 1.0 | 0.3333 | 0.0 | 1.0 |
| `QT-Q01-STATUS-ACTION` | `token_matched_live_tfidf_vector` | 10 | 10 | 0.0 | 0.3 | 1.0 | 0.8 |
| `QT-Q01-TIME-WINDOW` | `token_matched_live_tfidf_vector` | 10 | 10 | 1.0 | 0.3333 | 0.0 | 1.0 |

## Notes

- This is a fixed-budget model run over existing S7 contexts, not human review.
- Missing or failed LLM calls are counted separately from answered cases.
- Dense results should be framed as source-local guarded and source-bounded, not as pure dense embedding superiority.

## Claim Boundary

This report is a small fixed-budget LLM generation check over existing S7 contexts. It can support error discovery and cautious comparison, but it is not human review, expert certification, or operational readiness evidence.
