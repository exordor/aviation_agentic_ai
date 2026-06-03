# NASA ATMONTO S7 LLM Failure Review

Date: 2026-06-03

Status: manual review of the bounded 24-case S7 LLM answer-generation check
after adding the source-local dense retrieval guard. This is a diagnostic
review, not human certification of answer quality.

## Scope

Reviewed artifact:
`reports/stages/nasa_atmonto_s7_llm_answer_generation.json`

The reviewed run uses prompt version `nasa_atmonto_s7_llm_answer_v2`, with
12 selected cases per routed mode and two selected cases per CQ template.
The dense retrieval path now applies `source_local_target_source_guard` to
source-local CQ templates when the dense hit list misses the target advisory.

Aggregate result:

| Mode | Selected | Correctness | Citation precision | Citation recall | Evidence faithful | Unsupported claim rate | Abstention correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `routed_token_matched_live_tfidf_graphrag` | 12 | 0.9167 | 1.0 | 0.6111 | 0.9167 | 0.0833 | 0.9167 |
| `routed_token_matched_dense_graphrag` | 12 | 0.8333 | 1.0 | 0.6111 | 0.8333 | 0.1667 | 0.8333 |

## Guard Effect

The previous bounded LLM run had three dense-route failure types:

| Previous category | Previous cases | Post-guard status |
| --- | ---: | --- |
| Dense source miss on source-local temporal CQs | 2 | Addressed in the selected 24-case rerun. |
| Wrong-context abstention on source-local abstention CQs | 2 | Addressed in the selected 24-case rerun. |
| Compound CQ partial-answer ambiguity | 2 | Still present. |

The deterministic S7 rerun shows the same direction at the full 317-case scale:
`routed_token_matched_dense_graphrag` answer correctness increased from 0.3344
to 0.6215, target-source hit rate increased from 0.4069 to 0.9685, and the
guard fired on 178 of 317 cases. This improvement should be described as a
source-bounded dense retrieval guard, not as evidence that pure dense retrieval
alone is sufficient for ATCSCC advisory CQs.

## Current Failure Taxonomy

| Category | Cases | Affected templates | Root cause | Claim impact | Recommended action |
| --- | ---: | --- | --- | --- | --- |
| Compound CQ partial-answer ambiguity | 3 | `QT-Q01-ROUTE-SEMANTICS` | The retrieved target source and graph triple support `controlledNASelement=BNA`, but the LLM abstains because reroute type/reason are unsupported. | This is a CQ/prompt granularity issue, not a source retrieval miss. | Split route-semantics CQs into separately scored fields, or add a controlled partial-answer policy and evaluate it as a separate ablation. |

## Reviewed Failure Cards

### F1. Route Semantics Partial Answer: Live Lexical, `2026-05-19:074`

- Template: `QT-Q01-ROUTE-SEMANTICS`
- Expected value: `controlledNASelement=BNA`
- Retrieved target context:
  `atcscc-2026-05-19-074-p1-c1`, text `CTL ELEMENT: BNA`
- Graph triple: `t1`, predicate `controlledNASelement`, object `BNA`
- LLM behavior: abstained because reroute type and reroute reason were not
  supported, even though the scored field was supported.

Assessment: this is a partial-answer policy mismatch for a compound CQ. The
retrieval context was sufficient for the scored field.

### F2. Route Semantics Partial Answer: Dense, `2026-05-19:079`

- Template: `QT-Q01-ROUTE-SEMANTICS`
- Expected value: `controlledNASelement=BNA`
- Retrieved target context:
  `atcscc-2026-05-19-079-p1-c1`, text `CTL ELEMENT: BNA`
- Graph triple: `t1`, predicate `controlledNASelement`, object `BNA`
- LLM behavior: abstained because reroute type and reroute reason were not
  supported.

Assessment: the dense retrieval guard removed the previous source-miss problem;
the remaining failure is the same compound-CQ partial-answer issue.

### F3. Route Semantics Partial Answer: Dense, `2026-05-19:074`

- Template: `QT-Q01-ROUTE-SEMANTICS`
- Expected value: `controlledNASelement=BNA`
- Retrieved target context:
  `atcscc-2026-05-19-074-p1-c1`, text `CTL ELEMENT: BNA`
- Graph triple: `t1`, predicate `controlledNASelement`, object `BNA`
- LLM behavior: abstained because reroute type and reroute reason were not
  supported.

Assessment: same compound-CQ partial-answer issue as F1/F2.

## Implications for SOTA Story

1. The dense retrieval guard converts an earlier negative dense result into a
   qualified, source-bounded improvement. It should be reported with its guard
   rate because the improvement depends on metadata/source constraints.
2. The remaining LLM failures are concentrated in `QT-Q01-ROUTE-SEMANTICS`.
   This is evidence that compound CQs need a clearer answer contract, not that
   graph context is unavailable.
3. The live lexical and guarded dense routed modes are now close on the bounded
   24-case LLM check, but the sample is still diagnostic and should not be used
   as a broad GraphRAG superiority claim.
4. Strict abstention scoring remains necessary: abstention is correct only when
   the target source context was actually retrieved or deliberately injected by
   an explicit source-local guard.

## Next Engineering Step

Follow-up ablation:
`reports/stages/nasa_atmonto_s7_partial_answer_ablation.md`

The controlled partial-answer prompt was run on the same two selected
route-semantics cases for each routed mode. Both
`routed_token_matched_live_tfidf_graphrag` and
`routed_token_matched_dense_graphrag` reached strict correctness 1.0, partial
contract satisfaction 1.0, value F1 1.0, abstain rate 0.0, unsupported rate
0.0, and citation precision 1.0. Each case returned
`controlledNASelement=BNA` and listed `reRouteType` and `reRouteReason` as
missing requested predicates.

This means the remaining failures in the main S7 LLM report are caused by the
answer contract around compound CQs, not by missing graph/source evidence for
the scored field.

Do not expand the LLM sample until the route-semantics contract is explicit:

1. Either promote the explicit partial-answer policy into the primary S7 LLM
   answer prompt, or split `QT-Q01-ROUTE-SEMANTICS` into separately scored
   field-level CQs.
2. Keep the source-local dense guard and report its guard rate in retrieval and
   answer-generation tables.
3. Rerun the 24-case and then larger S7 LLM checks after the CQ-contract change.
