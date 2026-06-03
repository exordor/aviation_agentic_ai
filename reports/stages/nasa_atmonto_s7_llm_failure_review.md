# NASA ATMONTO S7 LLM Failure Review

Date: 2026-06-03

Status: failure review and resolution note for the bounded 24-case S7 LLM
answer-generation check. This is diagnostic evidence, not human certification
of answer quality.

## Current Reviewed Run

Reviewed artifact:
`reports/stages/nasa_atmonto_s7_llm_answer_generation.json`

The current reviewed run uses prompt version
`nasa_atmonto_s7_llm_answer_v3_route_partial`, with 12 selected cases per
routed mode and two selected cases per CQ template. The only prompt-contract
change from v2 is template-specific: for `QT-Q01-ROUTE-SEMANTICS`, the prompt
asks the model to return supported requested fields and list unsupported
requested fields separately instead of abstaining from the whole compound CQ.

Aggregate result:

| Mode | Selected | Correctness | Citation precision | Citation recall | Evidence faithful | Unsupported claim rate | Abstention correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `routed_token_matched_live_tfidf_graphrag` | 12 | 1.0 | 1.0 | 0.5556 | 1.0 | 0.0 | 1.0 |
| `routed_token_matched_dense_graphrag` | 12 | 1.0 | 1.0 | 0.5833 | 1.0 | 0.0 | 1.0 |

Current failure count: 0 scored failures in the bounded 24-case run.

## Resolution Path

The previous v2 bounded LLM run had three failure types:

| Previous category | Previous cases | Current v3 status |
| --- | ---: | --- |
| Dense source miss on source-local temporal CQs | 2 | Addressed by `source_local_target_source_guard`. |
| Wrong-context abstention on source-local abstention CQs | 2 | Addressed by `source_local_target_source_guard`. |
| Compound CQ partial-answer ambiguity | 3 | Addressed by the targeted `QT-Q01-ROUTE-SEMANTICS` partial-answer contract. |

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
- targeted prompt contracts can remove these failure modes without globally
  weakening abstention policy.

The result does not prove broad GraphRAG superiority or operational readiness.
It is still a 24-case fixed-budget check over frozen S7 contexts.

## Next Engineering Step

Scale and review rather than adding another prompt patch:

1. Rerun the S7 LLM check with more cases per CQ template while preserving the
   v3 route-semantics contract.
2. Add a small human/expert review pass for sampled generated answers.
3. Keep source-local dense guard rate, citation precision/recall, unsupported
   claim rate, and abstention correctness as separate thesis-facing metrics.
