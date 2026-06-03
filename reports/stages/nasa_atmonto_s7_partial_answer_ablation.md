# NASA ATMONTO S7 Route-Semantics Partial-Answer Ablation

## Scope

- Status: `s7_partial_answer_ablation_evaluated`
- Reviewer model: `gpt-5.4-mini`
- Prompt version: `nasa_atmonto_s7_route_semantics_partial_answer_v1`
- Template: `QT-Q01-ROUTE-SEMANTICS`
- Requested predicates: `reRouteType`, `reRouteReason`, `controlledNASelement`
- Selected cases: 4
- Boundary: Controlled route-semantics partial-answer ablation over frozen S7 contexts. This tests answer-contract wording only; it is not a new gold label set or operational ATC evaluation.

## Aggregate Partial-Answer Metrics

| Mode | Selected | Answered | Strict correctness | Partial contract | Value P | Value R | Value F1 | Abstain rate | Unsupported rate | Citation P |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `routed_token_matched_live_tfidf_graphrag` | 2 | 2 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 1.0 |
| `routed_token_matched_dense_graphrag` | 2 | 2 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 1.0 |

## Case Records

| CQ | Mode | Strict correct | Partial contract | Missing requested predicates |
| --- | --- | ---: | ---: | --- |
| `QT-Q01-ROUTE-SEMANTICS::2026-05-19:079` | `routed_token_matched_live_tfidf_graphrag` | True | True | reRouteReason, reRouteType |
| `QT-Q01-ROUTE-SEMANTICS::2026-05-19:079` | `routed_token_matched_dense_graphrag` | True | True | reRouteReason, reRouteType |
| `QT-Q01-ROUTE-SEMANTICS::2026-05-19:074` | `routed_token_matched_live_tfidf_graphrag` | True | True | reRouteReason, reRouteType |
| `QT-Q01-ROUTE-SEMANTICS::2026-05-19:074` | `routed_token_matched_dense_graphrag` | True | True | reRouteReason, reRouteType |

## Notes

- Strict correctness is still the source-bounded S7 answer-set scorer.
- Partial contract measures whether the model returns supported route fields without unsupported claims instead of abstaining because other requested fields are absent.
- This ablation should not replace the main S7 LLM report.

## Claim Boundary

This report isolates the compound route-semantics answer-contract issue found in the S7 LLM failure review. It should be cited as a partial-answer policy diagnostic, not as a replacement for the main S7 LLM answer report.
