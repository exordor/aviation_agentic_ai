# NASA ATMONTO S7 LLM Failure Review

Date: 2026-06-03

Status: failure review and resolution note for the bounded 60-case S7 LLM
answer-generation check. This is diagnostic evidence, not human certification
of answer quality.

## Current Reviewed Run

Reviewed artifact:
`reports/stages/nasa_atmonto_s7_llm_answer_generation.json`

The current reviewed run uses prompt version
`nasa_atmonto_s7_llm_answer_v3_route_partial`, with 30 selected cases per
routed mode and five selected cases per CQ template. The main prompt-contract
change from v2 is template-specific: for `QT-Q01-ROUTE-SEMANTICS`, the prompt
asks the model to return supported requested fields and list unsupported
requested fields separately instead of abstaining from the whole compound CQ.
The run also uses deterministic post-processing for ATCSCC time windows,
structured abstention flags, and `impactingCondition` literal normalization.

Aggregate result:

| Mode | Selected | Correctness | Citation precision | Citation recall | Evidence faithful | Unsupported claim rate | Abstention correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `routed_token_matched_live_tfidf_graphrag` | 30 | 0.9667 | 1.0 | 0.6084 | 0.9667 | 0.0167 | 1.0 |
| `routed_token_matched_dense_graphrag` | 30 | 0.9333 | 1.0 | 0.5945 | 0.9333 | 0.0333 | 1.0 |

Current failure count: 3 scored failures in the bounded 60-case run.

## Resolution Path

The previous v2 bounded LLM run had three failure types:

| Previous category | Previous cases | Current v3 status |
| --- | ---: | --- |
| Dense source miss on source-local temporal CQs | 2 | Addressed by `source_local_target_source_guard`. |
| Wrong-context abstention on source-local abstention CQs | 2 | Addressed by `source_local_target_source_guard`. |
| Compound CQ partial-answer ambiguity | 3 | Addressed by the targeted `QT-Q01-ROUTE-SEMANTICS` partial-answer contract. |
| Controlled-element type/metadata leakage | 2 observed in scaled inspection | Addressed by critic-gating `controlledNASelement` values such as `Airport` and JSON metadata artifacts. |

The remaining failures are not retrieval misses. They are concentrated in
`QT-Q01-CAUSE-CONDITION`:

| Current category | Current cases | Interpretation |
| --- | ---: | --- |
| Cause-condition over-answer | 3 | The LLM returns `impactingCondition` plus `impactingConditionMessage`, while the current label only accepts the literal message field. `reports/stages/nasa_atmonto_s7_candidate_adjudication.md` classifies these as profile/gold-boundary cases without changing the strict metric. |

The intermediate partial-answer ablation in
`reports/stages/nasa_atmonto_s7_partial_answer_ablation.md` tested the route
contract on the same two selected route-semantics cases per routed mode. Both
routed live lexical and guarded dense modes reached strict correctness 1.0,
partial contract satisfaction 1.0, value F1 1.0, abstain rate 0.0, unsupported
rate 0.0, and citation precision 1.0.

## Interpretation

The current bounded LLM result supports a narrower claim:

- source-local dense failures were retrieval-contract issues, not evidence that
  dense retrieval is generally unusable;
- route-semantics failures were compound-CQ answer-contract issues, not missing
  graph/source evidence for the scored `controlledNASelement` field;
- controlled-element metadata artifacts should be filtered before graph/hybrid
  answer contexts because type labels are not NAS elements;
- remaining cause-condition failures are useful evidence of over-answer risk,
  not a reason to loosen the scoring metric without human review;
- deterministic candidate adjudication records the likely profile/gold boundary,
  but it is not expert review and does not change the main S7 score.

The result does not prove broad GraphRAG superiority or operational readiness.
It is still a 60-case fixed-budget check over frozen S7 contexts.

## Next Engineering Step

Review rather than adding another prompt patch:

1. Use `reports/stages/nasa_atmonto_s7_human_review_candidates.md` and
   `reports/stages/nasa_atmonto_s7_candidate_adjudication.md` for a small
   human/expert review pass over failures plus coverage successes.
2. Decide whether `impactingCondition` should be treated as a valid canonical
   answer when `impactingConditionMessage` is the only current gold label.
3. Keep source-local dense guard rate, citation precision/recall, unsupported
   claim rate, and abstention correctness as separate thesis-facing metrics.
